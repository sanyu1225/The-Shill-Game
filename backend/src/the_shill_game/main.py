import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional

from the_shill_game.game.setup import run_game, setup_game
from the_shill_game.game.websocket import WebSocketManager
from the_shill_game.utils.logger import logger


# Setup FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Create WebSocket manager instance
ws_manager = WebSocketManager()
# Current active game state
game_state = None
# Flag to track if game is being set up
is_initializing = False
# Lock for game initialization
initialization_lock = asyncio.Lock()

# Default game ID
GAME_ID = "default"


@app.get("/game/state")
async def get_game_state():
    """Get the current game state"""
    try:
        if not game_state:
            return {
                "status": "not_initialized",
                "message": "Game not initialized yet. Connect via WebSocket to initialize.",
            }

        # Collect basic game data
        response = {
            "status": "success",
            "round": game_state.round,
            "round_phase": game_state.round_phase,
            "active_players": [
                {
                    "name": agent.character.name,
                    "traits": agent.character.traits.to_dict(),
                    "memecoin": agent.character.memecoin,
                }
                for agent in game_state.active_agents
            ],
            "eliminated_players": [
                {
                    "name": agent.character.name,
                    "traits": agent.character.traits,
                    "memecoin": agent.character.memecoin,
                }
                for agent in game_state.eliminated_agents
            ],
        }
        return response
    except Exception as e:
        logger.error(f"Error retrieving game state: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving game state: {str(e)}"
        )


@app.post("/game/setup")
async def setup_game_api(traits: Dict[str, str] = Body(...)):
    """Set up a new game with custom character traits"""
    global game_state, is_initializing

    try:
        async with initialization_lock:
            if is_initializing:
                return {
                    "status": "error",
                    "message": "Game is already being initialized. Please wait.",
                }

            if game_state:
                return {
                    "status": "error",
                    "message": "Game already exists. Cannot initialize a new one.",
                }

            is_initializing = True
            try:
                # Setup the game with client traits
                game_state = await setup_game(
                    ws_manager=ws_manager, game_id=GAME_ID, client_traits=traits
                )

                # Get player names to return
                players = game_state.get_player_names()

                return {
                    "status": "success",
                    "message": "Game initialized successfully with client character",
                    "players": players,
                }
            finally:
                is_initializing = False

    except Exception as e:
        logger.error(f"Error setting up game: {e}")
        raise HTTPException(status_code=500, detail=f"Error setting up game: {str(e)}")


@app.post("/game/start")
async def start_game():
    """Start the game"""
    global game_state

    try:
        if not game_state:
            return {
                "status": "error",
                "message": "Game not initialized yet. Connect via WebSocket to initialize.",
            }

        # Start the game
        asyncio.create_task(run_game(game_state))

        return {"status": "success", "message": "Game started"}

    except Exception as e:
        logger.error(f"Error starting game: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting game: {str(e)}")


@app.post("/game/next-round")
async def next_round():
    """Trigger the next round via HTTP POST"""
    global game_state

    try:
        if not game_state:
            return {
                "status": "error",
                "message": "Game not initialized yet. Connect via WebSocket to initialize.",
            }

        if game_state.round_phase == "game_over":
            return {
                "status": "error",
                "message": "Game is over. Cannot trigger next round.",
            }

        # Trigger the next round
        asyncio.create_task(game_state.run_round())

        return {"status": "success", "message": "Next round triggered successfully"}

    except Exception as e:
        logger.error(f"Error triggering next round: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error triggering next round: {str(e)}"
        )


@app.get("/game/winner")
async def get_winner():
    """Get the winner's takeaway when the game is over"""
    try:
        if not game_state:
            return {
                "status": "not_initialized",
                "message": "Game not initialized yet. Connect via WebSocket to initialize.",
            }

        if game_state.round_phase != "game_over":
            return {
                "status": "game_not_over",
                "message": "Game is not over yet. The winner will be announced when the game concludes.",
            }

        # Get the winner(s)
        takeaway = game_state.generate_winner_takeaway()
        if len(game_state.active_agents) == 1:
            winner = game_state.active_agents[0]
            return {
                "status": "success",
                "winner": {
                    "name": winner.character.name,
                    "memecoin": winner.character.memecoin,
                    "takeaway": takeaway,
                },
            }
        elif len(game_state.active_agents) == 2:
            # In case of a tie between two finalists
            winners = game_state.active_agents
            return {
                "status": "success",
                "winners": [
                    {
                        "name": winner.character.name,
                        "memecoin": winner.character.memecoin,
                        "takeaway": takeaway,
                    }
                    for winner in winners
                ],
            }
        else:
            return {
                "status": "error",
                "message": "Invalid game state: unexpected number of active agents.",
            }

    except Exception as e:
        logger.error(f"Error retrieving winner: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving winner: {str(e)}"
        )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle a new WebSocket connection for an existing game"""
    global game_state

    logger.info("New WebSocket connection")
    # Accept the WebSocket connection
    await websocket.accept()

    try:
        # Add the connection to the manager for the default game ID
        ws_manager.add_connection(websocket, GAME_ID)

        # Check if game exists
        if game_state:
            logger.info("Client joined existing game.")
            await ws_manager.send_personal_message(websocket, "Joined game.")

            # Inform client of current game state
            players = game_state.get_player_names()
            await ws_manager.send_personal_message(
                websocket, f"Current players: {players}"
            )
        else:
            # Game doesn't exist, inform client to set up game via API
            logger.info("Game not initialized. Informing client to use API.")
            await ws_manager.send_personal_message(
                websocket,
                "Game not initialized. Please set up the game using the /game/setup API endpoint first.",
            )

        # Main message loop - just keep the connection alive
        while True:
            try:
                # Check if the connection is still active
                if websocket.client_state.name != "CONNECTED":
                    logger.info(f"Client state is {websocket.client_state.name}")
                    break
                # Keep the connection alive
                await websocket.receive_text()

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket connection: {e}")
                break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during setup")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up the connection
        ws_manager.disconnect(websocket, GAME_ID)


if __name__ == "__main__":
    import uvicorn

    # Start the uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=8000)
