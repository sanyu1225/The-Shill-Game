from the_shill_game.game.state import GameState
from the_shill_game.game.websocket import WebSocketManager
from the_shill_game.utils.dummy import create_agents
from the_shill_game.utils.logger import logger


async def setup_game(
    ws_manager: WebSocketManager,
    num_agents: int = 6,
    game_id: str = "default",
) -> GameState:
    """Set up a new game with the specified number of agents"""
    logger.info("Setting up game...")
    # Create agents from characters
    agents = await create_agents(num_agents)
    # Create and return the game state
    game_state = GameState(agents, ws_manager, game_id)
    return game_state


async def run_game(game_state: GameState):
    """Run the full game loop"""
    logger.info("Running game...")
    # Start with introductions
    await game_state.start()

    # Run rounds until we have a winner
    # while len(game_state.active_agents) > 2:
    #     # Run a round
    #     await game_state.run_round()
    #     # Add a short delay between rounds to give clients time to process
    #     await asyncio.sleep(2)

    # # Game has concluded
    # winner = await game_state.end_game()
    # return winner
