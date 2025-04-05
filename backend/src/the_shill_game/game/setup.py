from the_shill_game.game.state import GameState
from the_shill_game.game.websocket import WebSocketManager
from the_shill_game.utils.dummy import create_agents, create_agent_with_traits
from the_shill_game.utils.logger import logger


async def setup_game(
    ws_manager: WebSocketManager,
    num_agents: int = 6,
    game_id: str = "default",
    client_traits: dict = None,
) -> GameState:
    """Set up a new game with the specified number of agents

    Args:
        ws_manager: WebSocket manager for the game
        num_agents: Total number of agents (including the client's character)
        game_id: Unique identifier for the game
        client_traits: Optional traits for client character. If provided, one character
                      will be created with these traits. The rest will have random traits.
    """
    logger.info("Setting up game...")

    if client_traits:
        # Create one agent with the provided traits and the rest with random traits
        client_agent = await create_agent_with_traits(
            name="Vitalik", traits_dict=client_traits
        )
        # Create the remaining agents randomly
        random_agents = await create_agents(num_agents - 1)
        # Combine the agents
        agents = [client_agent] + random_agents
    else:
        # Create all agents with random traits (original behavior)
        agents = await create_agents(num_agents)

    # Create and return the game state
    game_state = GameState(agents, ws_manager, game_id)
    return game_state


async def run_game(game_state: GameState):
    """Run the full game loop"""
    logger.info("Running game...")
    # Start with introductions
    await game_state.start()
