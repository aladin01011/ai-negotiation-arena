"""WebSocket connection manager for real-time communication."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections grouped by simulation rooms.
    
    Supports:
    - Broadcasting to all clients in a room
    - Broadcasting to all clients globally
    - Client disconnect handling
    - Room lifecycle management
    """

    def __init__(self):
        # room_id -> set of WebSocket connections
        self._rooms: Dict[str, Set[WebSocket]] = {}
        # WebSocket -> room_id mapping (for cleanup)
        self._connection_rooms: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        """
        Accept a WebSocket connection and add it to a room.
        
        Args:
            websocket: The WebSocket connection
            room_id: Simulation room identifier
        """
        await websocket.accept()
        
        if room_id not in self._rooms:
            self._rooms[room_id] = set()
        
        self._rooms[room_id].add(websocket)
        self._connection_rooms[websocket] = room_id
        
        logger.info(
            f"Client connected to room {room_id}. "
            f"Room size: {len(self._rooms[room_id])}"
        )

    def disconnect(self, websocket: WebSocket) -> Optional[str]:
        """
        Remove a WebSocket from its room.
        
        Returns:
            The room_id if the connection was found, None otherwise
        """
        room_id = self._connection_rooms.pop(websocket, None)
        if room_id and room_id in self._rooms:
            self._rooms[room_id].discard(websocket)
            # Cleanup empty rooms
            if not self._rooms[room_id]:
                del self._rooms[room_id]
            logger.info(
                f"Client disconnected from room {room_id}. "
                f"Room size: {len(self._rooms.get(room_id, set()))}"
            )
        return room_id

    async def broadcast_to_room(
        self, room_id: str, message: dict
    ) -> None:
        """
        Send a message to all clients in a specific room.
        
        Handles disconnection gracefully — if a client disconnects
        mid-broadcast, we remove them from the room and continue.
        """
        if room_id not in self._rooms:
            return

        message_str = json.dumps(message, default=str)
        disconnected: list[WebSocket] = []

        for websocket in self._rooms[room_id]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.warning(
                    f"Failed to send to client in room {room_id}: {e}"
                )
                disconnected.append(websocket)

        # Cleanup disconnected clients
        for ws in disconnected:
            self._rooms[room_id].discard(ws)
            self._connection_rooms.pop(ws, None)

    async def broadcast_global(self, message: dict) -> None:
        """Send a message to ALL connected clients across all rooms."""
        message_str = json.dumps(message, default=str)
        
        for room_id in list(self._rooms.keys()):
            await self.broadcast_to_room(room_id, message)

    def get_room_size(self, room_id: str) -> int:
        """Get number of connected clients in a room."""
        return len(self._rooms.get(room_id, set()))

    def get_rooms(self) -> list[str]:
        """Get list of all active room IDs."""
        return list(self._rooms.keys())

    async def send_personal_message(
        self, websocket: WebSocket, message: dict
    ) -> None:
        """Send a message to a single client."""
        await websocket.send_json(message)