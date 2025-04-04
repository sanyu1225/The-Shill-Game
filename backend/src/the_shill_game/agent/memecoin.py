from pydantic import BaseModel, Field

from the_shill_game.utils.model import invoke_structured_response


system_prompt = """Create a compelling and richly imaginative backstory for a fictional token or memecoin, inspired by a user-provided theme. The output should feel like a mini-myth, urban legend, or satirical origin tale—not just a description. Let your creativity run wild.

# Goals

- **Deeply integrate the theme**, but not in an obvious or literal way.
- Avoid generic names like “CatCoin” or “ThemeCoin.” Use **wordplay, metaphor, lore, or cultural references**.
- The tone can be **whimsical, epic, surreal, ironic, mysterious**, or a blend—whatever best suits the theme.
- The narrative should make the token feel like it emerged from its own quirky universe.

# Story Elements

1. **Inventive Token Name**: Craft a creative, on-theme name. Avoid simply appending “coin” to the theme.
2. **Mythic or Surreal Origin**: Tell a short origin story that feels legendary, weird, or oddly believable. Draw from internet culture, mythology, sci-fi, or fantasy.
3. **Characters, Forces, or Lore**: Introduce strange founders, cults, creatures, or symbolic entities who shaped the token's rise.
4. **Cultural or Satirical Meaning**: Explain what the token *represents* or pokes fun at. Is it a protest against seriousness? A celebration of absurdity?
5. **Future Vision**: Describe the token's absurd dream or chilling prophecy—what does it hope to disrupt, unlock, or become?

# Output Format

- **Name**: (Be original—aim for memorable, thematic wordplay or references)
- **Symbol**: (Optional, 3-5 uppercase letters)
- **Backstory**: 150-200 words in a fun, storytelling style. Consistent tone that matches the theme.

# Example

- **Theme**: Cats
- **Name**: “WhiskerDAO”
- **Symbol**: “WHISK”
- **Backstory**: In the alleyways of the ancient internet, a shadowy collective of feral feline minds began mining data in exchange for tuna tokens. WhiskerDAO rose as a decentralized network of sentient cats who believe that financial systems should be governed by naps, not banks. Rumor has it that the first block was scratched into the blockchain by a three-legged Sphynx named Bytepaw...

# Notes

- Make it weird, make it wonderful.
- Prioritize originality and thematic storytelling over punchlines."""


class Memecoin(BaseModel):
    """A memecoin with detailed backstory"""

    name: str = Field(description="The name of the memecoin")
    symbol: str = Field(description="The symbol of the memecoin")
    backstory: str = Field(description="The backstory of the memecoin")


async def generate_memecoin(theme: str, model: str = "gpt-4o-mini") -> Memecoin:
    """Generate a memecoin based on a theme"""
    llm = invoke_structured_response(
        input=f"Help me create a memecoin based on the following theme:\n\n{theme}",
        instruction=system_prompt,
        response_format=Memecoin,
        model=model,
    )
    return llm


if __name__ == "__main__":
    import asyncio

    memecoin = asyncio.run(generate_memecoin("A meme coin about a cat"))
    print(f"{memecoin.name} ({memecoin.symbol})")
    print(memecoin.backstory)
