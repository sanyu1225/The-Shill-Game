import asyncio
import random
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from the_shill_game.agent.character import Character
from the_shill_game.agent.traits import Traits
from the_shill_game.agent.memecoin_agent import create_agent
from the_shill_game.game.state import GameState


class Message(BaseModel):
    type: Literal["character", "system"]
    content: str
    sender: str | None = None
    timestamp: int


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.message_history: Dict[str, List[Message]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
            self.message_history[game_id] = []
        self.active_connections[game_id].append(websocket)

        # Send message history to the new connection
        if self.message_history[game_id]:
            await websocket.send_json(
                {
                    "type": "history",
                    "messages": [
                        msg.model_dump() for msg in self.message_history[game_id]
                    ],
                }
            )

    def disconnect(self, websocket: WebSocket, game_id: str):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                del self.message_history[game_id]

    async def broadcast(self, game_id: str, message: Message):
        if game_id in self.active_connections:
            # Add message to history
            self.message_history[game_id].append(message)

            # Broadcast to all connected clients
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message.model_dump())
                except WebSocketDisconnect:
                    self.disconnect(connection, game_id)

    async def send_character_message(self, game_id: str, content: str, sender: str):
        message = Message(
            type="character",
            content=content,
            sender=sender,
            timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
        )
        await self.broadcast(game_id, message)

    async def send_system_message(self, game_id: str, content: str):
        message = Message(
            type="system",
            content=content,
            timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
        )
        await self.broadcast(game_id, message)


async def _create_character_with_traits(name: str, memecoin_theme: str) -> Character:
    """Create a character with randomized traits"""
    # Create traits with random values for each trait category
    traits = Traits(
        sociability=random.choice(Traits.TRAIT_OPTIONS["sociability"]),
        thinking=random.choice(Traits.TRAIT_OPTIONS["thinking"]),
        cooperation=random.choice(Traits.TRAIT_OPTIONS["cooperation"]),
        risk_taking=random.choice(Traits.TRAIT_OPTIONS["risk_taking"]),
        exploration=random.choice(Traits.TRAIT_OPTIONS["exploration"]),
        trust=random.choice(Traits.TRAIT_OPTIONS["trust"]),
        morality=random.choice(Traits.TRAIT_OPTIONS["morality"]),
        adaptability=random.choice(Traits.TRAIT_OPTIONS["adaptability"]),
        initiative=random.choice(Traits.TRAIT_OPTIONS["initiative"]),
        emotional_control=random.choice(Traits.TRAIT_OPTIONS["emotional_control"]),
        foresight=random.choice(Traits.TRAIT_OPTIONS["foresight"]),
        action_style=random.choice(Traits.TRAIT_OPTIONS["action_style"]),
        knowledge_seeking=random.choice(Traits.TRAIT_OPTIONS["knowledge_seeking"]),
    )

    return await Character.create(
        name=name,
        traits=traits,
        memecoin_theme=memecoin_theme,
    )


async def setup_game(num_agents: int = 6) -> GameState:
    """Set up a new game with the specified number of agents"""
    # Character names
    names = [
        "Alex",
        "Jordan",
        "Taylor",
        "Morgan",
        "Casey",
        "Riley",
        "Quinn",
        "Avery",
        "Skyler",
        "Dakota",
        "Reese",
        "Jamie",
    ]
    random.shuffle(names)
    names = names[:num_agents]

    # Memecoin themes
    themes = [
        "Cats",
        "Space",
        "Gaming",
        "Memes",
        "Food",
        "Sports",
        "Music",
        "Art",
        "Technology",
        "Fashion",
        "Crypto",
        "NFTs",
    ]
    random.shuffle(themes)
    themes = themes[:num_agents]

    # Create characters and agents
    characters = []
    for i in range(num_agents):
        character = await _create_character_with_traits(names[i], themes[i])
        characters.append(character)

    # Create agents from characters
    agents = [create_agent(character) for character in characters]

    # Create and return the game state
    return GameState(agents)


async def run_game(game_state: GameState):
    """Run the full game loop"""
    # Start with introductions
    await game_state.start()

    # # Run rounds until we have a winner
    # while len(game_state.active_agents) > 2:
    #     print(f"\n=== ROUND {game_state.round + 1} ===")
    #     print(f"Remaining agents: {len(game_state.active_agents)}")

    #     await game_state.run_round()

    # # Game has concluded
    # winner = game_state.end_game()
    # return winner


# Setup FastAPI app
app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create WebSocket manager instance
manager = WebSocketManager()


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Create message object
            message = Message(
                type=message_data.get("type", "character"),
                content=message_data["content"],
                sender=message_data.get("sender"),
                timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
            )

            # Broadcast the message to all connected clients in the same game
            await manager.broadcast(game_id, message)
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(websocket, game_id)


async def main():
    """Main entry point for the game"""
    print("Setting up the game...")
    game_state = await setup_game(num_agents=6)

    print("Game starting...")
    winner = await run_game(game_state)

    if isinstance(winner, list) and len(winner) == 2:
        print(
            f"Game ended with finalists: {winner[0].character.name} and {winner[1].character.name}"
        )
    elif winner:
        print(
            f"Game winner: {winner.character.name} with memecoin {winner.character.memecoin.name}"
        )

    # Print the full game history
    print("\n=== GAME HISTORY ===")
    for message in game_state.messages:
        print(message)


if __name__ == "__main__":
    import uvicorn

    # To run both the game and the websocket server, we need to:
    # 1. Run the game in a background task
    # 2. Start the uvicorn server in the main thread

    # async def start_game():
    #     await main()

    # # Add game as a background task
    # @app.on_event("startup")
    # async def startup_event():
    #     asyncio.create_task(start_game())

    # Start the uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=8000)
