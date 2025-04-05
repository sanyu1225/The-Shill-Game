from typing import Dict, List, Optional
import random
import re

from the_shill_game.agent.memecoin_agent import MemecoinAgent
from the_shill_game.game.host import get_host_intro_message
from the_shill_game.game.websocket import WebSocketManager


class GameState:
    def __init__(
        self,
        agents: List[MemecoinAgent],
        ws_manager: WebSocketManager,
        game_id: str = "default",
    ):
        # Game state
        self.round = 0
        self.round_phase = None  # Current phase within the round
        self.messages = []  # Full conversation history
        # Maps agent ID to the ID of the agent they voted for
        self.votes = {}
        # Whether a tie-breaker has been attempted this round
        self.tie_breaker_attempted = False

        # Agents
        self.agents = agents
        self.active_agents = agents.copy()
        self.eliminated_agents = []

        self.speaking_order = []  # Order of agents in the current round
        self.defending_agent = None  # Agent that is currently defending
        self.tied_agents = []  # Agents tied for most votes in final voting

        self.ws_manager = ws_manager
        self.game_id = game_id

    def get_player_names(self) -> List[str]:
        """Get the names of the players in the game"""
        return [agent.character.name for agent in self.active_agents]

    async def start(self):
        """Start the game with the introduction round"""
        self.round = 1
        self.round_phase = "intro"

        await self._add_to_messages(get_host_intro_message("opening"))

        # Determine random speaking order for introductions
        self.speaking_order = self.active_agents.copy()
        random.shuffle(self.speaking_order)

        # Introduction round
        for i, agent in enumerate(self.speaking_order):
            await self._add_to_messages(
                get_host_intro_message("intro", agent.character.name, i == 0)
            )
            response = await agent.respond(self.messages)
            agent_message = f"[{agent.character.name}] {response.response}"
            await self._add_to_messages(agent_message, response.thought)

        # Start first voting round
        await self._add_to_messages(get_host_intro_message("init_voting"))
        await self.initial_voting_phase()

    async def run_round(self):
        """Run a full game round"""
        self.round += 1

        if len(self.active_agents) <= 2:
            # Game is over, we have a winner
            return self.end_game()

        # Reset round state
        self.votes = {}
        self.speaking_order = self.active_agents.copy()
        random.shuffle(self.speaking_order)

        self.tied_agents = []
        self.tie_breaker_attempted = False

        # Start persuasion phase
        await self.persuasion_phase()
        # Run initial voting
        await self.initial_voting_phase()
        # Run defense phase
        await self.defense_phase()
        # Run final voting
        await self.final_voting_phase()
        # Process results
        elimination_result = await self.process_round_results()

        # If there was a tie, run tie-breaker
        if not elimination_result and len(self.tied_agents) > 1:
            await self.run_tie_breaker()

        return True

    async def persuasion_phase(self):
        """Run the persuasion and strategy phase"""
        self.round_phase = "persuasion"

        round_intro = f"[Host] Round {self.round} begins! It's time for the persuasion phase. Each player will have a chance to speak."
        await self._add_to_messages(round_intro)

        for agent in self.speaking_order:
            prompt = f"[Host] {agent.character.name}, it's your turn to speak."
            await self._add_to_messages(prompt)

            response = await agent.respond(self.messages)
            agent_message = f"[{agent.character.name}] {response.response}"
            await self._add_to_messages(agent_message, response.thought)

    async def initial_voting_phase(self):
        """Run the initial voting phase"""
        self.round_phase = "initial_voting"
        self.votes = {}

        await self._add_to_messages(
            "[Host] It's time to vote. Please vote for the player with the least convincing memecoin."
        )

        for agent in self.active_agents:
            vote_prompt = f"[Host] {agent.character.name}, please cast your vote."
            await self._add_to_messages(vote_prompt)

            response = await agent.vote(self.messages)

            # Extract voted agent from response
            voted_agent = self._resolve_vote_target(agent, response.vote_target)
            self.votes[agent.character.id] = voted_agent

            vote_message = (
                f"[{agent.character.name}] I vote for {voted_agent.character.name}."
            )
            await self._add_to_messages(vote_message, response.thought)

        # Count votes and determine who goes to defense
        vote_results = self._count_votes_detailed()
        if vote_results["tied"] and len(vote_results["most_voted_agents"]) > 1:
            # If there's a tie for most votes, randomly select one to defend
            self.defending_agent = random.choice(vote_results["most_voted_agents"])
            tie_message = f"[Host] There's a tie between {', '.join([a.character.name for a in vote_results['most_voted_agents']])}. {self.defending_agent.character.name} has been randomly selected to enter the defense phase."
            await self._add_to_messages(tie_message)
        else:
            self.defending_agent = vote_results["most_voted_agents"][0]
            defense_announcement = f"[Host] {self.defending_agent.character.name} has received the most votes and will now enter the defense phase."
            await self._add_to_messages(defense_announcement)

    async def defense_phase(self):
        """Run the defense phase"""
        self.round_phase = "defense"

        # For the defense, provide information about who voted for them
        voters = []
        for voter_id, voted_agent in self.votes.items():
            if (
                voted_agent
                and voted_agent.character.id == self.defending_agent.character.id
            ):
                voter_name = self._get_agent_name_by_id(voter_id)
                voters.append(voter_name)

        defense_prompt = f"[Host] {self.defending_agent.character.name}, you received votes from {', '.join(voters)}. You now have a chance to defend your memecoin."
        await self._add_to_messages(defense_prompt)

        response = await self.defending_agent.respond(self.messages)
        defense_message = f"[{self.defending_agent.character.name}] {response.response}"
        await self._add_to_messages(defense_message, response.thought)

    async def final_voting_phase(self):
        """Run the final voting phase"""
        self.round_phase = "final_voting"
        self.votes = {}

        await self._add_to_messages(
            "[Host] After hearing the defense, it's time for the final vote. Please vote for the player to eliminate."
        )

        for agent in self.active_agents:
            if agent == self.defending_agent:
                continue  # Defending agent doesn't vote in this implementation

            vote_prompt = f"[Host] {agent.character.name}, please cast your final vote."
            await self._add_to_messages(vote_prompt)

            response = await agent.vote(self.messages)

            voted_agent = self._resolve_vote_target(agent, response.vote_target)
            self.votes[agent.character.id] = voted_agent

            vote_message = (
                f"[{agent.character.name}] I vote for {voted_agent.character.name}."
            )
            await self._add_to_messages(vote_message, response.thought)

    async def process_round_results(self):
        """Process the results of the current round"""
        vote_results = self._count_votes_detailed()

        # Check if there's a tie
        if vote_results["tied"] and len(vote_results["most_voted_agents"]) > 1:
            self.tied_agents = vote_results["most_voted_agents"]
            tie_message = f"[Host] We have a tie between {', '.join([a.character.name for a in self.tied_agents])}."
            await self._add_to_messages(tie_message)
            return False

        # If there's a clear elimination
        eliminated_agent = vote_results["most_voted_agents"][0]
        self.active_agents.remove(eliminated_agent)
        self.eliminated_agents.append(eliminated_agent)

        elimination_message = f"[Host] {eliminated_agent.character.name} has been eliminated from the game!"
        await self._add_to_messages(elimination_message)

        # Let the eliminated agent say farewell
        farewell_prompt = (
            f"[Host] {eliminated_agent.character.name}, do you have any final words?"
        )
        await self._add_to_messages(farewell_prompt)

        response = await eliminated_agent.respond(self.messages)
        farewell_message = f"[{eliminated_agent.character.name}] {response.response}"
        await self._add_to_messages(farewell_message, response.thought)

        return True

    async def run_tie_breaker(self):
        """Run a tie-breaker when there's a tie in voting"""
        if self.tie_breaker_attempted:
            # If we've already attempted a tie-breaker this round, randomly eliminate someone
            eliminated_agent = random.choice(self.tied_agents)
            self.active_agents.remove(eliminated_agent)
            self.eliminated_agents.append(eliminated_agent)

            tie_break_message = f"[Host] Since we've had a persistent tie, {eliminated_agent.character.name} has been randomly eliminated."
            await self._add_to_messages(tie_break_message)

            # Let the eliminated agent say farewell
            farewell_prompt = f"[Host] {eliminated_agent.character.name}, do you have any final words?"
            await self._add_to_messages(farewell_prompt)

            response = await eliminated_agent.respond(self.messages)
            farewell_message = (
                f"[{eliminated_agent.character.name}] {response.response}"
            )
            await self._add_to_messages(farewell_message, response.thought)

            return True

        # First tie-breaker attempt
        self.tie_breaker_attempted = True
        self.round_phase = "tie_breaker"
        self.votes = {}

        tie_breaker_msg = f"[Host] We have a tie between {', '.join([a.character.name for a in self.tied_agents])}. Let's have a tie-breaker."
        await self._add_to_messages(tie_breaker_msg)

        # Let tied agents speak again
        for agent in self.tied_agents:
            speak_prompt = f"[Host] {agent.character.name}, please make your final case to stay in the game."
            await self._add_to_messages(speak_prompt)

            response = await agent.respond(self.messages)
            speak_message = f"[{agent.character.name}] {response.response}"
            await self._add_to_messages(speak_message, response.thought)

        # Non-tied agents vote between the tied agents
        voting_agents = [a for a in self.active_agents if a not in self.tied_agents]

        if not voting_agents:
            # If everyone is tied, randomly eliminate someone
            eliminated_agent = random.choice(self.tied_agents)
            self.active_agents.remove(eliminated_agent)
            self.eliminated_agents.append(eliminated_agent)

            random_elim_msg = f"[Host] Since all remaining players are tied, {eliminated_agent.character.name} has been randomly eliminated."
            await self._add_to_messages(random_elim_msg)
            return True

        tie_vote_msg = f"[Host] Non-tied players, please vote to eliminate one of the tied players: {', '.join([a.character.name for a in self.tied_agents])}."
        await self._add_to_messages(tie_vote_msg)

        for agent in voting_agents:
            vote_prompt = f"[Host] {agent.character.name}, please vote to eliminate one of the tied players."
            await self._add_to_messages(vote_prompt)

            response = await agent.respond(self.messages)

            # Only allow voting for tied agents
            voted_agent = self._extract_vote_from_list(
                agent, response.response, self.tied_agents
            )
            self.votes[agent.character.id] = voted_agent

            vote_message = f"[{agent.character.name}] I vote to eliminate {voted_agent.character.name}."
            await self._add_to_messages(vote_message, response.thought)

        # Count tie-breaker votes
        vote_results = self._count_votes_detailed()

        if vote_results["tied"] and len(vote_results["most_voted_agents"]) > 1:
            # Still tied after tie-breaker
            tie_message = "[Host] We still have a tie after the tie-breaker."
            await self._add_to_messages(tie_message)
            return False

        # Eliminate the agent with most votes in tie-breaker
        eliminated_agent = vote_results["most_voted_agents"][0]
        self.active_agents.remove(eliminated_agent)
        self.eliminated_agents.append(eliminated_agent)

        elimination_message = f"[Host] After the tie-breaker, {eliminated_agent.character.name} has been eliminated from the game!"
        await self._add_to_messages(elimination_message)

        # Let the eliminated agent say farewell
        farewell_prompt = (
            f"[Host] {eliminated_agent.character.name}, do you have any final words?"
        )
        await self._add_to_messages(farewell_prompt)

        response = await eliminated_agent.respond(self.messages)
        farewell_message = f"[{eliminated_agent.character.name}] {response.response}"
        await self._add_to_messages(farewell_message, response.thought)

        return True

    async def end_game(self):
        """End the game and announce the winner"""
        self.round_phase = "game_over"

        if len(self.active_agents) == 1:
            # We have a winner
            winner = self.active_agents[0]
            winning_message = f"[Host] Congratulations {winner.character.name}! You are the winner of The Shill Game!"
            await self._add_to_messages(winning_message)
            return winner
        elif len(self.active_agents) == 2:
            # Final two agents
            finalists_message = f"[Host] We have our final two contestants: {self.active_agents[0].character.name} and {self.active_agents[1].character.name}!"
            await self._add_to_messages(finalists_message)
            return self.active_agents
        return None

    def _resolve_vote_target(
        self, voting_agent: MemecoinAgent, voted_target: str
    ) -> MemecoinAgent:
        """Resolve the voted agent from the input string."""
        normalized_target = voted_target.strip().lower()
        voting_agent_name = voting_agent.character.name.strip().lower()

        for agent in self.active_agents:
            active_agent_name = agent.character.name.strip().lower()
            if active_agent_name == voting_agent_name:
                continue  # Can't vote for yourself
            if active_agent_name == normalized_target:
                return agent

        raise ValueError(
            f"Unable to resolve vote target '{voted_target}'. "
            f"Active targets: {[agent.character.name for agent in self.active_agents]}"
        )

    def _extract_vote_from_list(
        self,
        voting_agent: MemecoinAgent,
        response: str,
        agent_list: List[MemecoinAgent],
    ) -> MemecoinAgent:
        """Extract the voted agent from a response, only considering agents in the provided list"""
        # Try to identify who they're voting for from the response
        for agent in agent_list:
            if agent.character.name.lower() in response.lower():
                # Look for patterns like "I vote for X" or "voting for X"
                vote_patterns = [
                    rf"vote (?:for|to eliminate) .*?{agent.character.name}",
                    rf"voting (?:for|to eliminate) .*?{agent.character.name}",
                    rf"my vote is .*?{agent.character.name}",
                    rf"I choose .*?{agent.character.name}",
                    rf"eliminating .*?{agent.character.name}",
                ]

                for pattern in vote_patterns:
                    if re.search(pattern, response, re.IGNORECASE):
                        return agent

        # If we couldn't extract the vote, randomly select an agent from the list
        if not agent_list:
            return None
        return random.choice(agent_list)

    def _count_votes_detailed(self) -> Dict:
        """Count votes and return detailed information about voting results"""
        vote_count = {}

        for voted_agent in self.votes.values():
            if voted_agent:
                agent_id = voted_agent.character.id
                vote_count[agent_id] = vote_count.get(agent_id, 0) + 1

        # Find agent(s) with most votes
        max_votes = 0
        most_voted_agents = []

        for agent_id, count in vote_count.items():
            if count > max_votes:
                max_votes = count
                most_voted_agents = [self._get_agent_by_id(agent_id)]
            elif count == max_votes:
                most_voted_agents.append(self._get_agent_by_id(agent_id))

        return {
            "vote_count": vote_count,
            "max_votes": max_votes,
            "most_voted_agents": most_voted_agents,
            "tied": len(most_voted_agents) > 1,
        }

    async def _add_to_messages(self, message: str, thought: str = None):
        """Add a message to the conversation history and send via WebSocket if available"""
        # Store message in local history
        self.messages.append(message.strip().replace("\n", " "))

        # If WebSocket manager is available, send the message
        if self.ws_manager and self.game_id:
            # Extract sender and content from message format
            if message.startswith("[") and "]" in message:
                parts = message.split("]", 1)
                sender = parts[0][1:].strip()  # Remove brackets
                content = parts[1].strip()

                if thought:
                    await self.ws_manager.send_character_message_with_thought(
                        self.game_id, content, thought, sender
                    )
                else:
                    await self.ws_manager.send_character_message(
                        self.game_id, content, sender
                    )
            else:
                # Default to system message if format doesn't match
                await self.ws_manager.send_system_message(self.game_id, message)

    def _get_agent_name_by_id(self, agent_id: str) -> str:
        """Helper method to get an agent's name by their ID"""
        for agent in self.agents:
            if agent.character.id == agent_id:
                return agent.character.name
        return "Unknown"

    def _get_agent_by_id(self, agent_id: str) -> Optional[MemecoinAgent]:
        """Helper method to get an agent object by ID"""
        for agent in self.active_agents:
            if agent.character.id == agent_id:
                return agent
        return None
