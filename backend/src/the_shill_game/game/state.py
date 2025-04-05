from typing import Dict, List, Optional
import random
import re

from the_shill_game.agent.memecoin_agent import MemecoinAgent
from the_shill_game.game.host import get_host_message


class GameState:
    def __init__(self, agents: List[MemecoinAgent]):
        # Game state
        self.round = 0
        self.messages = []  # Full conversation history
        # Maps agent ID to the ID of the agent they voted for
        self.votes = {}
        # Whether a tie-breaker has been attempted this round
        self.tie_breaker_attempted = False

        # Agents
        self.agents = agents
        self.active_agents = agents.copy()
        self.eliminated_agents = []

        self.round_phase = None  # Current phase within the round
        self.speaking_order = []  # Order of agents in the current round
        self.defending_agent = None  # Agent that is currently defending
        self.tied_agents = []  # Agents tied for most votes in final voting

    async def start(self):
        """Start the game with the introduction round"""
        self.round = 1

        self._add_to_messages(get_host_message("opening"))

        # Determine random speaking order for introductions
        self.speaking_order = self.active_agents.copy()
        random.shuffle(self.speaking_order)

        # Introduction round
        for i, agent in enumerate(self.speaking_order):
            self._add_to_messages(
                get_host_message("intro", agent.character.name, i == 0)
            )
            response = await agent.respond(self.messages)
            agent_message = f"[{agent.character.name}] {response.response}"
            self._add_to_messages(agent_message)

        # Start first voting round
        self._add_to_messages(get_host_message("init_voting"))
        # await self.initial_voting_phase()

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

        # Report on alliances if any strong ones exist
        strong_alliances = self.alliance_tracker.get_strongest_alliances(threshold=0.6)
        if strong_alliances and self.round > 1:
            alliance_text = (
                "[Host] I've noticed some interesting dynamics forming in the group. "
            )
            if len(strong_alliances) == 1:
                alliance_pair = strong_alliances[0]
                agent1_id, agent2_id, _ = alliance_pair
                agent1_name = self._get_agent_name_by_id(agent1_id)
                agent2_name = self._get_agent_name_by_id(agent2_id)
                alliance_text += (
                    f"It seems {agent1_name} and {agent2_name} may be working together."
                )
            else:
                alliance_text += (
                    "Several alliances appear to be forming between players."
                )
            self.messages.append(alliance_text)

        round_intro = f"[Host] Round {self.round} begins! It's time for the persuasion phase. Each player will have a chance to speak."
        self.messages.append(round_intro)

        for agent in self.speaking_order:
            prompt = f"[Host] {agent.character.name}, it's your turn to speak."
            self.messages.append(prompt)

            response = await agent.respond(self.messages)
            agent_message = f"[{agent.character.name}] {response.response}"
            self.messages.append(agent_message)

            # Detect alliances from agent's speech
            self.alliance_tracker.update_alliances(
                agent, response.response, self.messages
            )

    async def initial_voting_phase(self):
        """Run the initial voting phase"""
        self.round_phase = "initial_voting"
        self.votes = {}

        self.messages.append(
            "[Host] It's time to vote. Please vote for the player with the least convincing memecoin."
        )

        for agent in self.active_agents:
            vote_prompt = f"[Host] {agent.character.name}, please cast your vote."
            self.messages.append(vote_prompt)

            response = await agent.respond(self.messages)

            # Extract voted agent from response
            voted_agent = self._extract_vote(agent, response.response)
            self.votes[agent.character.id] = voted_agent

            vote_message = (
                f"[{agent.character.name}] I vote for {voted_agent.character.name}."
            )
            self.messages.append(vote_message)

        # Update alliances based on voting patterns
        self.alliance_tracker.detect_alliance_from_votes(self.votes)

        # Count votes and determine who goes to defense
        vote_results = self._count_votes_detailed()
        if vote_results["tied"] and len(vote_results["most_voted_agents"]) > 1:
            # If there's a tie for most votes, randomly select one to defend
            self.defending_agent = random.choice(vote_results["most_voted_agents"])
            tie_message = f"[Host] There's a tie between {', '.join([a.character.name for a in vote_results['most_voted_agents']])}. {self.defending_agent.character.name} has been randomly selected to enter the defense phase."
            self.messages.append(tie_message)
        else:
            self.defending_agent = vote_results["most_voted_agents"][0]
            defense_announcement = f"[Host] {self.defending_agent.character.name} has received the most votes and will now enter the defense phase."
            self.messages.append(defense_announcement)

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
        self.messages.append(defense_prompt)

        response = await self.defending_agent.respond(self.messages)
        defense_message = f"[{self.defending_agent.character.name}] {response.response}"
        self.messages.append(defense_message)

        # Update alliances based on the defense speech
        self.alliance_tracker.update_alliances(
            self.defending_agent, response.response, self.messages
        )

    async def final_voting_phase(self):
        """Run the final voting phase"""
        self.round_phase = "final_voting"
        self.votes = {}

        self.messages.append(
            "[Host] After hearing the defense, it's time for the final vote. Please vote for the player to eliminate."
        )

        for agent in self.active_agents:
            if agent == self.defending_agent:
                continue  # Defending agent doesn't vote in this implementation

            vote_prompt = f"[Host] {agent.character.name}, please cast your final vote."
            self.messages.append(vote_prompt)

            response = await agent.respond(self.messages)

            voted_agent = self._extract_vote(agent, response.response)
            self.votes[agent.character.id] = voted_agent

            vote_message = (
                f"[{agent.character.name}] I vote for {voted_agent.character.name}."
            )
            self.messages.append(vote_message)

        # Update alliances based on voting patterns
        self.alliance_tracker.detect_alliance_from_votes(self.votes)

    async def process_round_results(self):
        """Process the results of the current round"""
        vote_results = self._count_votes_detailed()

        # Check if there's a tie
        if vote_results["tied"] and len(vote_results["most_voted_agents"]) > 1:
            self.tied_agents = vote_results["most_voted_agents"]
            tie_message = f"[Host] We have a tie between {', '.join([a.character.name for a in self.tied_agents])}."
            self.messages.append(tie_message)
            return False

        # If there's a clear elimination
        eliminated_agent = vote_results["most_voted_agents"][0]
        self.active_agents.remove(eliminated_agent)
        self.eliminated_agents.append(eliminated_agent)

        elimination_message = f"[Host] {eliminated_agent.character.name} has been eliminated from the game!"
        self.messages.append(elimination_message)

        # Let the eliminated agent say farewell
        farewell_prompt = (
            f"[Host] {eliminated_agent.character.name}, do you have any final words?"
        )
        self.messages.append(farewell_prompt)

        response = await eliminated_agent.respond(self.messages)
        farewell_message = f"[{eliminated_agent.character.name}] {response.response}"
        self.messages.append(farewell_message)

        return True

    async def run_tie_breaker(self):
        """Run a tie-breaker when there's a tie in voting"""
        if self.tie_breaker_attempted:
            # If we've already attempted a tie-breaker this round, randomly eliminate someone
            eliminated_agent = random.choice(self.tied_agents)
            self.active_agents.remove(eliminated_agent)
            self.eliminated_agents.append(eliminated_agent)

            tie_break_message = f"[Host] Since we've had a persistent tie, {eliminated_agent.character.name} has been randomly eliminated."
            self.messages.append(tie_break_message)

            # Let the eliminated agent say farewell
            farewell_prompt = f"[Host] {eliminated_agent.character.name}, do you have any final words?"
            self.messages.append(farewell_prompt)

            response = await eliminated_agent.respond(self.messages)
            farewell_message = (
                f"[{eliminated_agent.character.name}] {response.response}"
            )
            self.messages.append(farewell_message)

            return True

        # First tie-breaker attempt
        self.tie_breaker_attempted = True
        self.round_phase = "tie_breaker"
        self.votes = {}

        tie_breaker_msg = f"[Host] We have a tie between {', '.join([a.character.name for a in self.tied_agents])}. Let's have a tie-breaker."
        self.messages.append(tie_breaker_msg)

        # Let tied agents speak again
        for agent in self.tied_agents:
            speak_prompt = f"[Host] {agent.character.name}, please make your final case to stay in the game."
            self.messages.append(speak_prompt)

            response = await agent.respond(self.messages)
            speak_message = f"[{agent.character.name}] {response.response}"
            self.messages.append(speak_message)

        # Non-tied agents vote between the tied agents
        voting_agents = [a for a in self.active_agents if a not in self.tied_agents]

        if not voting_agents:
            # If everyone is tied, randomly eliminate someone
            eliminated_agent = random.choice(self.tied_agents)
            self.active_agents.remove(eliminated_agent)
            self.eliminated_agents.append(eliminated_agent)

            random_elim_msg = f"[Host] Since all remaining players are tied, {eliminated_agent.character.name} has been randomly eliminated."
            self.messages.append(random_elim_msg)
            return True

        tie_vote_msg = f"[Host] Non-tied players, please vote to eliminate one of the tied players: {', '.join([a.character.name for a in self.tied_agents])}."
        self.messages.append(tie_vote_msg)

        for agent in voting_agents:
            vote_prompt = f"[Host] {agent.character.name}, please vote to eliminate one of the tied players."
            self.messages.append(vote_prompt)

            response = await agent.respond(self.messages)

            # Only allow voting for tied agents
            voted_agent = self._extract_vote_from_list(
                agent, response.response, self.tied_agents
            )
            self.votes[agent.character.id] = voted_agent

            vote_message = f"[{agent.character.name}] I vote to eliminate {voted_agent.character.name}."
            self.messages.append(vote_message)

        # Count tie-breaker votes
        vote_results = self._count_votes_detailed()

        if vote_results["tied"] and len(vote_results["most_voted_agents"]) > 1:
            # Still tied after tie-breaker
            tie_message = f"[Host] We still have a tie after the tie-breaker."
            self.messages.append(tie_message)
            return False

        # Eliminate the agent with most votes in tie-breaker
        eliminated_agent = vote_results["most_voted_agents"][0]
        self.active_agents.remove(eliminated_agent)
        self.eliminated_agents.append(eliminated_agent)

        elimination_message = f"[Host] After the tie-breaker, {eliminated_agent.character.name} has been eliminated from the game!"
        self.messages.append(elimination_message)

        # Let the eliminated agent say farewell
        farewell_prompt = (
            f"[Host] {eliminated_agent.character.name}, do you have any final words?"
        )
        self.messages.append(farewell_prompt)

        response = await eliminated_agent.respond(self.messages)
        farewell_message = f"[{eliminated_agent.character.name}] {response.response}"
        self.messages.append(farewell_message)

        return True

    def end_game(self):
        """End the game and announce the winner"""
        if len(self.active_agents) == 1:
            winner = self.active_agents[0]
            winning_message = f"[Host] Congratulations {winner.character.name}! You are the winner of The Shill Game!"
            self.messages.append(winning_message)
            return winner
        elif len(self.active_agents) == 2:
            # Final two agents
            finalists_message = f"[Host] We have our final two contestants: {self.active_agents[0].character.name} and {self.active_agents[1].character.name}!"
            self.messages.append(finalists_message)
            return self.active_agents
        return None

    def _extract_vote(
        self, voting_agent: MemecoinAgent, response: str
    ) -> MemecoinAgent:
        """Extract the voted agent from a response"""
        # Try to identify who they're voting for from the response
        for agent in self.active_agents:
            if (
                agent != voting_agent
                and agent.character.name.lower() in response.lower()
            ):
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

        # If we couldn't extract the vote, randomly select an agent that's not the voting agent
        valid_targets = [a for a in self.active_agents if a != voting_agent]
        if not valid_targets:
            return None
        return random.choice(valid_targets)

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

    def _add_to_messages(self, message: str):
        self.messages.append(message.strip().replace("\n", " "))

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
