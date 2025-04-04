from typing import List
from agents import Agent, Runner
from the_shill_game.agent.character import Character, CharacterResponse
from the_shill_game.agent.traits import Traits


class MemecoinAgent:
    def __init__(self, character: Character, model: str):
        self.character = character
        self.agent = Agent(
            name=character.name,
            instructions=character.get_instructions(),
            model=model,
            tools=[],
            output_type=CharacterResponse,
        )

    async def respond(self, messages: List[str]) -> CharacterResponse:
        """
        Generates a response to the current conversation based on message history.
        """
        prompt = (
            "You are given a list of messages of the current conversation. "
            "Respond as your character. NEVER repeat another character's phrasing or tone."
            "Make sure the response is as concise as possible."
        )
        message_history = "\n".join(messages)
        response = await Runner.run(
            self.agent, f"{prompt}\n\n# Current Conversation\n{message_history}"
        )
        return response.final_output


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
