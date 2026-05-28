"""
AI Negotiation Arena — Backend Server

FastAPI application with WebSocket support for real-time
multi-agent simulation.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .core.event_bus import EventBus
from .websocket.manager import ConnectionManager
from .websocket.handlers import WebSocketHandler
from .api.routes import router as api_router

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Application Lifecycle ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize global services
    app.state.event_bus = EventBus()
    app.state.connection_manager = ConnectionManager()
    app.state.ws_handler = WebSocketHandler(
        connection_manager=app.state.connection_manager,
        event_bus=app.state.event_bus,
    )
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    # Cleanup would go here


# ── FastAPI Application ────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time multi-agent simulation platform "
                "for game theory and strategic AI.",
    lifespan=lifespan,
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST Routes ────────────────────────────────────────────────────

app.include_router(api_router)


# ── Health Check ───────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ── WebSocket Endpoint ────────────────────────────────────────────

@app.websocket("/ws/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    """
    WebSocket endpoint for live simulation streaming.
    
    Connect to /ws/{simulation_id} to receive real-time updates
    for a specific simulation.
    
    Client can send commands:
    - {"type": "simulation.start", "payload": {...}}
    - {"type": "simulation.pause"}
    - {"type": "simulation.resume"}
    - {"type": "simulation.stop"}
    - {"type": "simulation.speed", "multiplier": 2.0}
    
    Server sends events:
    - {"event": "simulation.started", ...}
    - {"event": "round.result", ...}
    - {"event": "standings.update", ...}
    - {"event": "simulation.ended", ...}
    """
    ws_handler: WebSocketHandler = app.state.ws_handler
    await ws_handler.handle_connection(websocket, simulation_id)


@app.websocket("/ws")
async def websocket_endpoint_no_id(websocket: WebSocket):
    """
    WebSocket endpoint that creates a new simulation room.
    """
    ws_handler: WebSocketHandler = app.state.ws_handler
    await ws_handler.handle_connection(websocket)


# ── Entry Point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )