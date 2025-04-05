from pydantic import BaseModel, Field

from the_shill_game.agent.traits import Traits
from the_shill_game.utils.id_generator import generate_id
from the_shill_game.agent.memecoin import generate_memecoin, Memecoin


class CharacterResponse(BaseModel):
    """A response from a character."""

    response: str = Field(description="The response from the character.")
    thought: str = Field(description="The brief reasoning behind the response.")


class CharacterVoteResponse(BaseModel):
    """A response from a character indicating their vote in an elimination round."""

    vote_target: str = Field(
        description="The name of the player this character is voting to eliminate."
    )
    thought: str = Field(description="The brief reasoning behind the vote.")


def _compose_base_instructions(character: "Character") -> str:
    """Generate the base role instructions for the character."""
    return f"""You are {character.name}, a {character.role} in *The Shill Game* — a high-stakes memecoin strategy showdown.
You are NOT an AI. Use your own personality, memories, and worldview to respond to the conversation. Remember, always stay in character. 


## Objective

Outlast your rivals by:
1. Shilling your memecoin with confidence and flair  
2. Forming — and breaking — alliances with purpose  
3. Voting tactically to eliminate threats  
4. Surviving to the final round and emerging victorious

## Output Format

### CharacterResponse
Use this during regular conversation rounds.
- "response": "<your in-character message, in first person>",
- "thought": "<your private reasoning, also in first person>"

### CharacterVoteResponse
Use only during elimination rounds.
- "response": "<your in-character message about the vote>",
- "thought": "<your private reasoning behind the vote>",
- "vote_target": "<name of the character you are voting to eliminate>"


You'll receive ongoing conversation history between you {character.name} and other characters.
React naturally — emotionally, strategically, and personally — as if your reputation and project are truly at stake."""


def _compose_personality_section(traits: Traits) -> str:
    """Insert the character's psychological profile and speaking style."""
    communication_style = traits.get_communication_style().strip()
    return f"""## Personality & Communication Style

{communication_style}

Use this voice to persuade, form bonds, plant seeds of doubt, or steer conversations toward your desired outcomes."""


def _compose_game_mechanics(memecoin: Memecoin) -> str:
    """Detail the gameplay rules and the character's memecoin."""
    return f"""## Game Mechanics

This is a social survival game. Each round:
1. Interact with other players to promote your memecoin  
2. Vote to eliminate one participant  
3. The most-voted player is eliminated  
4. Last player standing wins

## Your Memecoin: {memecoin.name} ({memecoin.symbol})

{memecoin.backstory.strip()}

You're the founder and soul of {memecoin.name} ({memecoin.symbol}). Your mission is to make it iconic by highlighting:
- Name, symbol, and branding  
- Cultural resonance and viral potential  
- Why people should ape in emotionally or tactically  
- Why {memecoin.name} survives when others fade

## Winning Tips

- Forge bonds — and break them when it matters  
- Pick your targets with surgical precision  
- Read the room. Every silence, joke, or shift matters  
- Let your traits do the work — charm, logic, restraint, whatever fits  
- Don't just survive — **shape the narrative**"""


def _get_character_instructions(character: "Character", memecoin: Memecoin) -> str:
    """Generate the full character system prompt."""
    return "\n\n".join(
        [
            _compose_base_instructions(character),
            _compose_personality_section(character.traits),
            _compose_game_mechanics(memecoin),
        ]
    )


class Character:
    def __init__(
        self,
        id: str,
        name: str,
        traits: Traits,
        memecoin_theme: str,
        memecoin: Memecoin,
        role: str = "memecoin manager",
    ):
        self.id = id
        self.name = name
        self.traits = traits
        self.memecoin_theme = memecoin_theme
        self.memecoin = memecoin
        self.role = role

    @classmethod
    async def create(
        cls,
        name: str,
        traits: Traits,
        memecoin_theme: str,
        role: str = "memecoin manager",
    ) -> "Character":
        id = generate_id(name)
        memecoin = await generate_memecoin(memecoin_theme)
        return cls(
            id=id,
            name=name,
            traits=traits,
            memecoin=memecoin,
            memecoin_theme=memecoin_theme,
            role=role,
        )

    def get_instructions(self) -> str:
        if self.memecoin is None:
            raise ValueError("Memecoin not initialized")
        return _get_character_instructions(self, self.memecoin)

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.id}) - {self.memecoin.name} ({self.memecoin.symbol})"
        )


if __name__ == "__main__":
    import asyncio

    character = asyncio.run(
        Character.create(
            name="John",
            traits=Traits(thinking="Emotional"),
            memecoin_theme="A meme coin about Vitalik",
        )
    )
    print(character)
