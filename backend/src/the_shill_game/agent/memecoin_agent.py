from typing import Type
from agents import Agent, Runner
from the_shill_game.agent.character import (
    Character,
    CharacterResponse,
    CharacterVoteResponse,
)
from the_shill_game.agent.traits import Traits


class MemecoinAgent:
    _respond_prompt = (
        "Begin with a line only *your* character would say. "
        "Channel their temperament, pride, or flaws — no generic or diplomatic responses. "
        "React meaningfully to what *other players* say, NOT the *host*. "
        "Focus on their tone, logic, or attitude. Always be concise."
    )

    _vote_prompt = (
        "You are in a voting round. "
        "You must vote for a character to eliminate. "
        "You CANNOT vote for yourself. "
        "Remember, you need to survive no matter what. "
    )

    def __init__(self, character: Character, model: str):
        self.character = character
        self.agent = Agent(
            name=character.name,
            instructions=character.get_instructions(),
            model=model,
            tools=[],
            output_type=CharacterResponse,
        )

    async def _run_response(self, messages: list[str], output_type: Type) -> any:
        """
        Internal helper to run a character response/vote with the shared logic.
        """
        self.agent.output_type = output_type
        message_history = "\n".join(messages)
        base_prompt = (
            self._respond_prompt
            if output_type == CharacterResponse
            else self._vote_prompt
        )

        user_prompt = f"{base_prompt}\n\n# Current Conversation\n{message_history}"
        response = await Runner.run(self.agent, user_prompt)
        return response.final_output

    async def respond(self, messages: list[str]) -> CharacterResponse:
        """Generates a response to the current conversation based on message history."""
        return await self._run_response(messages, CharacterResponse)

    async def vote(self, messages: list[str]) -> CharacterVoteResponse:
        """Generates a vote to the current conversation based on message history."""
        return await self._run_response(messages, CharacterVoteResponse)


def create_agent(character: Character, model: str = "gpt-4o-mini") -> MemecoinAgent:
    return MemecoinAgent(character, model)


if __name__ == "__main__":
    import asyncio

    character1 = asyncio.run(
        Character.create(
            name="John",
            traits=Traits(thinking="Emotional"),
            memecoin_theme="Vitalik",
        )
    )

    character2 = asyncio.run(
        Character.create(
            name="Emma",
            traits=Traits(thinking="Logical"),
            memecoin_theme="Hackathon",
        )
    )
    agent1 = create_agent(character1)
    agent2 = create_agent(character2)

    initial_message = "[Host] Good morning! First round introduce your memecoin"
    messages = [initial_message]

    result = asyncio.run(agent1.respond(messages=messages))
    print(result)
    messages.append(f"[{agent1.character.name}] {result.response}")

    result = asyncio.run(agent2.respond(messages=messages))
    print(result)
    messages.append(f"[{agent2.character.name}] {result.response}")
