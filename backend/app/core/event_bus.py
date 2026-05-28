"""Event bus for decoupled communication between simulation components."""

from __future__ import annotations
from typing import Callable, Dict, List, Any, Awaitable
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """All event types in the system."""
    SIMULATION_STARTED = "simulation.started"
    SIMULATION_PAUSED = "simulation.paused"
    SIMULATION_RESUMED = "simulation.resumed"
    SIMULATION_ENDED = "simulation.ended"
    ROUND_STARTED = "round.started"
    ROUND_COMPLETED = "round.completed"
    MATCH_COMPLETED = "match.completed"
    AGENT_UPDATED = "agent.updated"
    STANDINGS_UPDATED = "standings.updated"
    ERROR = "error"


EventHandler = Callable[..., Awaitable[None]]


class EventBus:
    """
    Simple in-process event bus for loosely coupled communication.
    
    Components publish events, and subscribers react to them.
    This follows the Observer pattern and enables clean separation
    between the simulation engine, WebSocket broadcaster, and database writer.
    """

    def __init__(self):
        self._subscribers: Dict[EventType, List[EventHandler]] = {}

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register an event handler for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Remove a previously registered handler."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]

    async def publish(self, event_type: EventType, **data: Any) -> None:
        """
        Publish an event to all subscribers.
        
        All handlers are awaited concurrently for performance.
        If a handler fails, other handlers still run.
        """
        handlers = self._subscribers.get(event_type, [])
        if not handlers:
            return

        logger.debug(f"Publishing {event_type.value} to {len(handlers)} handlers")

        tasks = []
        for handler in handlers:
            tasks.append(self._safe_call(handler, event_type, data))

        await asyncio.gather(*tasks)

    async def _safe_call(
        self, handler: EventHandler, event_type: EventType, data: dict
    ) -> None:
        """Call a handler safely, logging errors without crashing."""
        try:
            await handler(event_type=event_type, **data)
        except Exception as e:
            logger.error(
                f"Handler {handler.__name__} failed for {event_type.value}: {e}",
                exc_info=True,
            )