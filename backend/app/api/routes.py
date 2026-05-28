"""REST API routes for the AI Negotiation Arena."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from ..agents.base_agent import list_strategies
from ..core.simulation_engine import SimulationEngine, SimulationConfig
from ..core.event_bus import EventBus
from ..core.matchmaker import MatchType
from .schemas import (
    CreateSimulationRequest,
    SimulationResponse,
    AgentResponse,
    StandingsResponse,
    StrategyInfo,
)

router = APIRouter(prefix="/api", tags=["api"])


def get_event_bus() -> EventBus:
    """Dependency injection for EventBus (singleton from app state)."""
    from ..main import app
    return app.state.event_bus


# In-memory storage for REST API (production would use DB)
_simulations: dict[str, SimulationEngine] = {}
_standings_cache: dict[str, list[dict]] = {}


@router.get("/strategies", response_model=list[StrategyInfo])
async def get_strategies():
    """
    List all available agent strategies with descriptions.
    
    This endpoint returns the full strategy catalog so the frontend
    can let users configure which agents to use.
    """
    return list_strategies()


@router.post("/simulations", response_model=SimulationResponse)
async def create_simulation(
    request: CreateSimulationRequest,
    event_bus: EventBus = Depends(get_event_bus),
):
    """
    Create and start a new simulation.
    
    This is the primary endpoint for launching simulations.
    It spawns agents, starts the game loop, and returns a simulation ID
    that can be used to connect via WebSocket for live updates.
    """
    simulation_id = uuid.uuid4().hex[:12]

    config = SimulationConfig(
        total_rounds=request.rounds,
        match_type=MatchType(request.match_type),
        speed_multiplier=request.speed_multiplier,
    )

    engine = SimulationEngine(
        simulation_id=simulation_id,
        config=config,
        event_bus=event_bus,
    )
    engine.spawn_agents()
    _simulations[simulation_id] = engine

    # Start in background
    await engine.start()

    return SimulationResponse(
        simulation_id=simulation_id,
        status=engine.state.status,
        rounds_completed=0,
        total_rounds=request.rounds,
        agent_count=len(engine.state.agents),
        elapsed_seconds=0.0,
    )


@router.get("/simulations", response_model=list[SimulationResponse])
async def list_simulations():
    """List all active and completed simulations."""
    results = []
    for sim_id, engine in _simulations.items():
        results.append(
            SimulationResponse(
                simulation_id=sim_id,
                status=engine.state.status,
                rounds_completed=engine.state.current_round,
                total_rounds=engine.config.total_rounds,
                agent_count=len(engine.state.agents),
                elapsed_seconds=engine.state.elapsed_seconds,
            )
        )
    return results


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: str):
    """Get the current state of a simulation."""
    engine = _simulations.get(simulation_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return SimulationResponse(
        simulation_id=simulation_id,
        status=engine.state.status,
        rounds_completed=engine.state.current_round,
        total_rounds=engine.config.total_rounds,
        agent_count=len(engine.state.agents),
        elapsed_seconds=engine.state.elapsed_seconds,
    )


@router.get(
    "/simulations/{simulation_id}/standings",
    response_model=StandingsResponse,
)
async def get_standings(simulation_id: str):
    """Get current tournament standings for a simulation."""
    engine = _simulations.get(simulation_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Simulation not found")

    standings = engine._get_standings()
    return StandingsResponse(standings=standings)


@router.get(
    "/simulations/{simulation_id}/agents",
    response_model=list[AgentResponse],
)
async def get_agents(simulation_id: str):
    """Get all agents in a simulation with their stats."""
    engine = _simulations.get(simulation_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Simulation not found")

    agents = []
    for agent in engine.state.agents.values():
        agents.append(
            AgentResponse(
                agent_id=agent.agent_id,
                name=agent.name,
                strategy=agent.strategy.name if agent.strategy else "unknown",
                personality_label=agent.personality.to_label(),
                total_score=agent.total_score,
                total_interactions=agent.memory.total_interactions(),
            )
        )
    return agents


@router.post(
    "/simulations/{simulation_id}/actions",
    response_model=SimulationResponse,
)
async def control_simulation(simulation_id: str, action: str):
    """
    Control a simulation: pause, resume, or stop.
    
    Usage: POST /simulations/{id}/actions with body {"action": "pause"}
    """
    engine = _simulations.get(simulation_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Simulation not found")

    action = action.lower().strip()
    if action == "pause":
        await engine.pause()
    elif action == "resume":
        await engine.resume()
    elif action == "stop":
        await engine.stop()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {action}. Use pause, resume, or stop.",
        )

    return SimulationResponse(
        simulation_id=simulation_id,
        status=engine.state.status,
        rounds_completed=engine.state.current_round,
        total_rounds=engine.config.total_rounds,
        agent_count=len(engine.state.agents),
        elapsed_seconds=engine.state.elapsed_seconds,
    )