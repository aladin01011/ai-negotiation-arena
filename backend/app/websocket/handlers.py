"""WebSocket message handlers — maps incoming events to engine actions."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect

from ..core.simulation_engine import SimulationEngine, SimulationConfig
from ..core.event_bus import EventBus, EventType
from ..core.matchmaker import MatchType
from .manager import ConnectionManager

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """
    Handles the WebSocket lifecycle and message routing.
    
    Acts as the bridge between the network layer and the simulation engine.
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        event_bus: EventBus,
    ):
        self.connection_manager = connection_manager
        self.event_bus = event_bus
        self._engines: Dict[str, SimulationEngine] = {}

    async def handle_connection(
        self, websocket: WebSocket, simulation_id: Optional[str] = None
    ) -> None:
        """
        Handle a full WebSocket connection lifecycle.
        
        This is the main entry point for WebSocket connections.
        It manages the room assignment, message loop, and cleanup.
        """
        room_id = simulation_id or f"room-{uuid.uuid4().hex[:8]}"
        
        await self.connection_manager.connect(websocket, room_id)
        
        try:
            while True:
                # Receive and parse message
                raw = await websocket.receive_text()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    await self._send_error(websocket, "Invalid JSON")
                    continue

                # Route message to handler
                msg_type = data.get("type", "")
                handler = self._get_handler(msg_type)
                if handler:
                    await handler(websocket, room_id, data)
                else:
                    await self._send_error(
                        websocket, f"Unknown message type: {msg_type}"
                    )

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected from room {room_id}")
        except Exception as e:
            logger.error(f"WebSocket error in room {room_id}: {e}", exc_info=True)
        finally:
            self.connection_manager.disconnect(websocket)
            # Cleanup engine if this was the last connection
            if (
                room_id in self._engines
                and self.connection_manager.get_room_size(room_id) == 0
            ):
                engine = self._engines.pop(room_id)
                if engine.state.is_running:
                    await engine.stop()

    def _get_handler(self, msg_type: str):
        """Find the handler for a message type."""
        handlers = {
            "simulation.start": self._handle_start,
            "simulation.pause": self._handle_pause,
            "simulation.resume": self._handle_resume,
            "simulation.stop": self._handle_stop,
            "simulation.speed": self._handle_speed,
        }
        return handlers.get(msg_type)

    async def _handle_start(
        self, websocket: WebSocket, room_id: str, data: dict
    ) -> None:
        """Handle simulation start command."""
        payload = data.get("payload", {})

        config = SimulationConfig(
            total_rounds=payload.get("rounds", 100),
            match_type=MatchType(payload.get("match_type", "round_robin")),
        )

        # Create engine
        engine = SimulationEngine(
            simulation_id=room_id,
            config=config,
            event_bus=self.event_bus,
        )
        engine.spawn_agents()
        self._engines[room_id] = engine

        # Subscribe broadcaster to events
        broadcaster = SimulationBroadcaster(
            self.connection_manager, room_id
        )
        self.event_bus.subscribe(EventType.ROUND_COMPLETED, broadcaster.on_round)
        self.event_bus.subscribe(EventType.STANDINGS_UPDATED, broadcaster.on_standings)
        self.event_bus.subscribe(EventType.SIMULATION_ENDED, broadcaster.on_ended)
        self.event_bus.subscribe(EventType.SIMULATION_STARTED, broadcaster.on_started)
        self.event_bus.subscribe(EventType.SIMULATION_PAUSED, broadcaster.on_paused)
        self.event_bus.subscribe(EventType.SIMULATION_RESUMED, broadcaster.on_resumed)

        # Send initial agent list
        await self.connection_manager.broadcast_to_room(room_id, {
            "event": "agents.list",
            "agents": [a.to_dict() for a in engine.state.agents.values()],
        })

        # Start the engine
        await engine.start()

    async def _handle_pause(
        self, websocket: WebSocket, room_id: str, data: dict
    ) -> None:
        """Handle simulation pause command."""
        engine = self._engines.get(room_id)
        if engine:
            await engine.pause()

    async def _handle_resume(
        self, websocket: WebSocket, room_id: str, data: dict
    ) -> None:
        """Handle simulation resume command."""
        engine = self._engines.get(room_id)
        if engine:
            await engine.resume()

    async def _handle_stop(
        self, websocket: WebSocket, room_id: str, data: dict
    ) -> None:
        """Handle simulation stop command."""
        engine = self._engines.get(room_id)
        if engine:
            await engine.stop()

    async def _handle_speed(
        self, websocket: WebSocket, room_id: str, data: dict
    ) -> None:
        """Handle simulation speed change command."""
        engine = self._engines.get(room_id)
        multiplier = data.get("multiplier", 1.0)
        if engine and 0.1 <= multiplier <= 10.0:
            engine.set_speed(multiplier)
            await self.connection_manager.broadcast_to_room(room_id, {
                "event": "simulation.speed_changed",
                "multiplier": multiplier,
            })

    async def _send_error(self, websocket: WebSocket, message: str) -> None:
        """Send an error message to a specific client."""
        await self.connection_manager.send_personal_message(
            websocket, {"event": "error", "message": message}
        )


class SimulationBroadcaster:
    """
    Listens to simulation events and broadcasts them via WebSocket.
    
    Registered with the EventBus. Converts internal events to
    wire-format messages for frontend consumption.
    """

    def __init__(self, manager: ConnectionManager, room_id: str):
        self.manager = manager
        self.room_id = room_id

    async def on_started(self, event_type: EventType, **data) -> None:
        await self.manager.broadcast_to_room(self.room_id, {
            "event": "simulation.started",
            "simulation_id": data.get("simulation_id"),
            "agent_count": data.get("agent_count"),
            "total_rounds": data.get("total_rounds"),
        })

    async def on_round(self, event_type: EventType, **data) -> None:
        round_result = data.get("round_result")
        if round_result:
            await self.manager.broadcast_to_room(self.room_id, {
                "event": "round.result",
                "simulation_id": data.get("simulation_id"),
                "round_number": round_result.round_number,
                "matches": [m.to_dict() for m in round_result.matches],
            })

    async def on_standings(self, event_type: EventType, **data) -> None:
        await self.manager.broadcast_to_room(self.room_id, {
            "event": "standings.update",
            "simulation_id": data.get("simulation_id"),
            "standings": data.get("standings", []),
        })

    async def on_ended(self, event_type: EventType, **data) -> None:
        await self.manager.broadcast_to_room(self.room_id, {
            "event": "simulation.ended",
            "simulation_id": data.get("simulation_id"),
            "final_state": data.get("final_state"),
        })

    async def on_paused(self, event_type: EventType, **data) -> None:
        await self.manager.broadcast_to_room(self.room_id, {
            "event": "simulation.paused",
            "simulation_id": data.get("simulation_id"),
        })

    async def on_resumed(self, event_type: EventType, **data) -> None:
        await self.manager.broadcast_to_room(self.room_id, {
            "event": "simulation.resumed",
            "simulation_id": data.get("simulation_id"),
        })