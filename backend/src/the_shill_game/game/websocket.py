from datetime import datetime, timezone
from typing import List, Dict, Literal, Optional
from fastapi import WebSocket
from pydantic import BaseModel, Field


class WsMessage(BaseModel):
    # Timestamp in milliseconds
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp() * 1000)
    )


class AgentMessage(WsMessage):
    type: Literal["agent"]
    sender: str
    response: str
    thought: str


class SystemMessage(WsMessage):
    type: Literal["system"]
    content: str
    event: Optional[str] = None


class WebSocketManager:
    def __init__(self):
        # ID -> List of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # ID -> List of Messages
        self.message_history: Dict[str, List[WsMessage]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        """Legacy method that accepts and adds a connection"""
        await websocket.accept()
        self.add_connection(websocket, game_id)

    def add_connection(self, websocket: WebSocket, game_id: str):
        """Add a connection that's already been accepted"""
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
            self.message_history[game_id] = []
        # Add the new connection to the list of active connections
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        """Remove a connection"""
        if (
            game_id in self.active_connections
            and websocket in self.active_connections[game_id]
        ):
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                del self.message_history[game_id]

    def is_connected(self, websocket: WebSocket, game_id: str) -> bool:
        """Check if a specific WebSocket connection is still active"""
        return (
            game_id in self.active_connections
            and websocket in self.active_connections[game_id]
        )

    def has_connections(self, game_id: str) -> bool:
        """Check if there are any active connections for a game"""
        return (
            game_id in self.active_connections
            and len(self.active_connections[game_id]) > 0
        )

    async def send_personal_message(self, websocket: WebSocket, content: str):
        """Send a message to a specific client"""
        try:
            message = SystemMessage(type="system", content=content)
            await websocket.send_json(message.model_dump())
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def send_character_message(self, game_id: str, content: str, sender: str):
        """Send a character message to all clients in a game"""
        message = AgentMessage(
            type="agent", sender=sender, response=content, thought=""
        )
        await self._broadcast(game_id, message)

    async def send_character_message_with_thought(
        self, game_id: str, content: str, thought: str, sender: str
    ):
        """Send a character message with thought to all clients in a game"""
        message = AgentMessage(
            type="agent", sender=sender, response=content, thought=thought
        )
        await self._broadcast(game_id, message)

    async def send_system_message(self, game_id: str, content: str):
        """Send a system message to all clients in a game"""
        message = SystemMessage(type="system", content=content)
        await self._broadcast(game_id, message)

    async def send_event(self, game_id: str, event: str):
        """Send an event to all clients in a game"""
        message = SystemMessage(type="system", content="", event=event)
        await self._broadcast(game_id, message)

    async def _broadcast(self, game_id: str, message: WsMessage):
        """Broadcast a message to all clients in a game"""
        if game_id in self.active_connections:
            self.message_history[game_id].append(message)
            failed_connections = []

            for connection in self.active_connections[game_id]:
                try:
                    # Convert the message to a dictionary and then to JSON
                    message_dict = message.model_dump()
                    await connection.send_json(message_dict)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")
                    # Mark the connection for removal
                    failed_connections.append(connection)

            # Remove failed connections
            for connection in failed_connections:
                self.disconnect(connection, game_id)
