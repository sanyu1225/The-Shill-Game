from typing import Dict, List, Optional
from collections import Counter
import random

from the_shill_game.agent.memecoin_agent import MemecoinAgent
from the_shill_game.game.host import (
    eliminate_agent,
    get_background,
    get_host_defense_message,
    get_host_final_vote_message,
    get_host_intro_message,
    get_host_voting_message,
)
from the_shill_game.game.websocket import WebSocketManager
from the_shill_game.utils.logger import logger
from the_shill_game.utils.model import invoke_chat_response


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
        self.votes: Dict[str, MemecoinAgent] = {}
        self.most_voted_agents: List[MemecoinAgent] = []

        # Agents
        self.agents = agents
        self.active_agents = agents.copy()
        self.eliminated_agents = []

        self.speaking_order = []  # Order of agents in the current round
        self.tied_agents = []  # Agents tied for most votes in final voting

        self.ws_manager = ws_manager
        self.game_id = game_id

    def get_player_names(self) -> List[str]:
        """Get the names of the players in the game"""
        return [agent.character.name for agent in self.active_agents]

    async def start(self):
        """Start the game with the introduction round"""
        logger.info("Running intro phase")
        self.round_phase = "intro"

        await self._add_to_messages(get_background())

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
        await self._add_to_messages(get_host_intro_message("transition"))
        await self.initial_voting_phase()
        await self.defense_phase()
        await self.final_voting_phase()
        elimination_result = await self.process_round_results()
        if not elimination_result:
            # There was a tie, run tie-breaker
            await self.run_tie_breaker()

    async def run_round(self):
        """Run a full game round"""
        self.round += 1

        # Reset round state
        self.votes = {}
        self.speaking_order = self.active_agents.copy()
        random.shuffle(self.speaking_order)

        self.tied_agents = []

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
        if not elimination_result:
            await self.run_tie_breaker()

        if len(self.active_agents) <= 2:
            # Game is over, we have a winner
            return await self.end_game()

    async def persuasion_phase(self):
        """Run the persuasion and strategy phase"""
        self.round_phase = "persuasion"

        round_intro = "[Host] Alright! It's time for the persuasion phase. Each player will have a chance to speak."
        await self._add_to_messages(round_intro)

        for agent in self.speaking_order:
            prompt = f"[Host] {agent.character.name}, it's your turn to speak."
            await self._add_to_messages(prompt)

            response = await agent.respond(self.messages)
            agent_message = f"[{agent.character.name}] {response.response}"
            await self._add_to_messages(agent_message, response.thought)

    async def initial_voting_phase(self):
        """Run the initial voting phase"""
        logger.info("Running initial voting phase")
        self.round_phase = "initial_voting"
        self.votes = {}

        await self._add_to_messages(get_host_voting_message("intro"))

        for agent in self.active_agents:
            await self._add_to_messages(
                get_host_voting_message("cue", agent.character.name)
            )

            response = await agent.vote(self.messages)
            # Get voted agent from response
            voted_agent = self._resolve_vote_target(agent, response.vote_target)
            # Store vote result
            self.votes[agent.character.id] = voted_agent

            vote_message = (
                f"[{agent.character.name}] I vote for {voted_agent.character.name}."
            )
            await self._add_to_messages(vote_message, response.thought)

        # Count votes and determine who goes to defense
        self._count_votes()

        announce_result_message = get_host_voting_message(
            "announce_result",
            most_voted_agents=[
                agent.character.name for agent in self.most_voted_agents
            ],
        )
        await self._add_to_messages(announce_result_message)

    async def defense_phase(self):
        """Run the defense phase"""
        logger.info("Running defense phase")
        self.round_phase = "defense"

        for agent in self.most_voted_agents:
            defense_prompt = get_host_defense_message(agent.character.name)
            await self._add_to_messages(defense_prompt)
            response = await agent.respond(self.messages)
            defense_message = f"[{agent.character.name}] {response.response}"
            await self._add_to_messages(defense_message, response.thought)

    async def final_voting_phase(self):
        """Run the final voting phase"""
        logger.info("Running final voting phase")
        self.round_phase = "final_voting"
        self.votes = {}

        await self._add_to_messages(get_host_voting_message("final_vote"))

        for agent in self.active_agents:
            await self._add_to_messages(
                get_host_voting_message("cue", agent.character.name)
            )

            response = await agent.vote(self.messages)
            # Get voted agent from response
            voted_agent = self._resolve_vote_target(agent, response.vote_target)
            # Store vote result
            self.votes[agent.character.id] = voted_agent

            vote_message = (
                f"[{agent.character.name}] I vote for {voted_agent.character.name}."
            )
            await self._add_to_messages(vote_message, response.thought)

    async def process_round_results(self) -> bool:
        """Process the results of the current round"""
        logger.info("Processing round results")
        vote_results = self._count_votes()

        most_voted_agents = vote_results["most_voted_agents"]
        # Check if there's a tie
        if len(most_voted_agents) > 1:
            self.tied_agents = most_voted_agents
            tie_message = get_host_final_vote_message(
                phase="tie",
                most_voted_agents=[a.character.name for a in most_voted_agents],
            )
            await self._add_to_messages(tie_message)
            return False

        # If there's a clear elimination
        eliminated_agent = most_voted_agents[0]
        self.active_agents.remove(eliminated_agent)
        print(f"Active agents: {len(self.active_agents)} left")
        self.eliminated_agents.append(eliminated_agent)
        print(f"Eliminated agent: {eliminated_agent.character.name}")

        await self._add_to_messages(
            get_host_final_vote_message(
                phase="elimination",
                eliminated_agent=eliminated_agent.character.name,
            )
        )

        # Let the eliminated agent say farewell
        await self._add_to_messages(
            get_host_final_vote_message(
                phase="farewell",
                eliminated_agent=eliminated_agent.character.name,
            )
        )
        response = await eliminated_agent.respond(self.messages)
        farewell_message = f"[{eliminated_agent.character.name}] {response.response}"
        await self._add_to_messages(farewell_message, response.thought)
        return True

    async def run_tie_breaker(self):
        """Run a tie-breaker when there's a tie in voting"""
        # TODO: For demo purposes, we let the host decide who to eliminate
        response = eliminate_agent(self.tied_agents)
        eliminated_agent_name = response.vote_target.strip().lower()
        # Resolve the agent from the response
        eliminated_agent = None
        for agent in self.tied_agents:
            active_agent_name = agent.character.name.strip().lower()
            if active_agent_name == eliminated_agent_name:
                eliminated_agent = agent
        if not eliminated_agent:
            logger.warning(f"Unable to find agent {eliminated_agent_name}")
            eliminated_agent = random.choice(self.tied_agents)

        self.active_agents.remove(eliminated_agent)
        self.eliminated_agents.append(eliminated_agent)

        await self._add_to_messages(
            f"[Host] No more delays—I'm making the call. {response.vote_target}, you're out!"
        )
        # Let the eliminated agent say farewell
        await self._add_to_messages(
            get_host_final_vote_message(
                phase="farewell",
                eliminated_agent=eliminated_agent.character.name,
            )
        )
        response = await eliminated_agent.respond(self.messages)
        farewell_message = f"[{eliminated_agent.character.name}] {response.response}"
        await self._add_to_messages(farewell_message, response.thought)

    async def end_game(self):
        """End the game and announce the winner"""
        logger.info("Running end game")
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
        else:
            raise ValueError("Game is not over")

    def generate_winner_takeaway(self) -> str:
        """Generate a takeaway message for the winner"""
        # if len(self.active_agents) > 2 or self.round_phase != "game_over":
        #     raise ValueError("Game is not over")

        winners = self.active_agents
        response = invoke_chat_response(
            input=(
                f"The following is a transcript of The Shill Game, a social survival show where players must outwit, outtalk, "
                f"and outmaneuver each other to become the last memecoin founder standing.\n\n"
                f"Conversation history:\n{self.messages}\n\n"
                f"The winner(s): {', '.join(agent.character.name for agent in winners)}"
            ),
            instruction=(
                "You're the host of The Shill Game. "
                "Summarize how the winner(s) outplayed the others — highlight their most brilliant moves, "
                "alliances made or broken, emotional or psychological tactics, and what set them apart.\n"
                "End with a punchy one-liner or mic-drop statement that captures why they won."
            ),
        )
        return response

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

    def _count_votes(self) -> Dict:
        """Count votes and return detailed information about voting results"""
        self.most_voted_agents = []
        vote_count = Counter(
            voted_agent.character.id for voted_agent in self.votes.values()
        )

        # Get the agent(s) with the most votes
        max_votes = max(vote_count.values())
        most_voted_agents = [
            self._get_agent_by_id(agent_id)
            for agent_id, count in vote_count.items()
            if count == max_votes
        ]
        self.most_voted_agents = most_voted_agents
        return {
            "vote_count": dict(vote_count),
            "max_votes": max_votes,
            "most_voted_agents": most_voted_agents,
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
