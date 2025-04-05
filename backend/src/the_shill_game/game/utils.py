from typing import List
from the_shill_game.agent.memecoin_agent import MemecoinAgent


def get_player_names(agents: List[MemecoinAgent]) -> str:
    return ", ".join([agent.character.name for agent in agents])
