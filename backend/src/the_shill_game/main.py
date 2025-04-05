import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle a new WebSocket connection and automatically set up the game if needed"""
    global game_state, is_initializing

    logger.info("New WebSocket connection")
    # Accept the WebSocket connection
    await websocket.accept()

    try:
        # Add the connection to the manager for the default game ID
        ws_manager.add_connection(websocket, GAME_ID)

        # Initialize the game if it doesn't exist
        if game_state:
            logger.info("Client joined existing game.")
            await ws_manager.send_personal_message(websocket, "Joined game.")
        else:
            async with initialization_lock:
                if not game_state and not is_initializing:
                    is_initializing = True

                    try:
                        # Inform client that game is being initialized
                        await ws_manager.send_personal_message(
                            websocket, "Initializing game. Please wait..."
                        )

                        # Setup the game
                        game_state = await setup_game(
                            ws_manager=ws_manager, game_id=GAME_ID
                        )
                        # Inform all clients that the game is ready
                        players = game_state.get_player_names()
                        await ws_manager.send_system_message(
                            GAME_ID, f"Game initialized with players: {players}"
                        )

                        logger.info("Game initialized successfully")
                    finally:
                        is_initializing = False

                elif is_initializing:
                    await ws_manager.send_personal_message(
                        websocket, "Game is being initialized. Please wait..."
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
