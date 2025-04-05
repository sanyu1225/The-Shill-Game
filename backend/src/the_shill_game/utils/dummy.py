import asyncio
import random
from typing import List

from the_shill_game.agent.character import Character
from the_shill_game.agent.memecoin_agent import MemecoinAgent, create_agent
from the_shill_game.agent.traits import Traits


def _get_character_names(num: int) -> List[str]:
    """Get a list of random character names"""
    names = [
        "Alex",
        "Avery",
        "Blake",
        "Cameron",
        "Casey",
        "Charlie",
        "Clement",
        "Dakota",
        "Elliot",
        "Finley",
        "Harper",
        "Jamie",
        "Jimmy",
        "Johnathan",
        "Jordan",
        "Logan",
        "Micah",
        "Morgan",
        "Parker",
        "Quinn",
        "Reese",
        "Riley",
        "Robin",
        "Rowan",
        "Sam",
        "Shawn",
        "Spencer",
        "Sydney",
        "Taylor",
        "Terry",
        "Victoria",
    ]
    random.shuffle(names)
    return names[:num]


def _get_character_traits(num: int) -> List[Traits]:
    """Get a random trait set up"""
    trait_keys = Traits.TRAIT_OPTIONS.keys()

    return [
        Traits(**{key: random.choice(Traits.TRAIT_OPTIONS[key]) for key in trait_keys})
        for _ in range(num)
    ]


def _get_memecoin_themes(num: int) -> List[str]:
    """Get a list of random memecoin themes"""

    themes = [
        "Cats",
        "Dogs",
        "Aliens",
        "Space",
        "Time Travel",
        "Gaming",
        "Retro Tech",
        "Dank Memes",
        "Food (Pizza, Tacos, Burgers)",
        "Sports",
        "Music Genres (Lo-fi, Metal, Synthwave)",
        "Street Art",
        "Tech Bros",
        "Fashion (Y2K, Vaporwave)",
        "Crypto Culture",
        "NFT Parody",
        "AI Takeover",
        "Taiwan Culture",
        "Conspiracy Theories",
        "Internet Legends",
        "Meme History (Doge, Pepe, etc.)",
        "Cartoons",
        "Movie Parodies",
        "Quantum Physics (but dumbed down)",
        "Weird Holidays (Talk Like a Pirate Day, etc.)",
        "Fast Food Mascots",
        "Mythical Creatures",
        "Apocalypse Vibes",
        "Corporate Satire",
        "Internet Nostalgia (early 2000s)",
    ]
    random.shuffle(themes)
    return themes[:num]


async def create_agents(num: int, model: str = "gpt-4o-mini") -> List[MemecoinAgent]:
    """Create characters with random trait sets and return agents"""
    traits = _get_character_traits(num)
    names = _get_character_names(num)
    themes = _get_memecoin_themes(num)
    characters = await asyncio.gather(
        *[
            Character.create(
                name=names[i],
                traits=traits[i],
                memecoin_theme=themes[i],
            )
            for i in range(num)
        ]
    )
    # Create agents from characters
    return [create_agent(character, model) for character in characters]


if __name__ == "__main__":
    agents = asyncio.run(create_agents(6))
    for agent in agents:
        print("Name:", f"{agent.character.name} - {agent.character.id}")
        print("Memecoin:", agent.character.memecoin.name)
        print("Model:", agent.agent.model)
        print("-" * 100)
