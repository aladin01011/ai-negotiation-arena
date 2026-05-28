"""WebSocket event type definitions matching the frontend protocol."""

from typing import TypedDict, Optional


# =============================================================================
# Server → Client Events
# =============================================================================

class SimulationStartedEvent(TypedDict):
    event: str  # "simulation.started"
    simulation_id: str
    agent_count: int
    total_rounds: int
    agents: list[dict]


class SimulationEndedEvent(TypedDict):
    event: str  # "simulation.ended"
    simulation_id: str
    final_state: dict


class SimulationPausedEvent(TypedDict):
    event: str  # "simulation.paused"
    simulation_id: str


class SimulationResumedEvent(TypedDict):
    event: str  # "simulation.resumed"
    simulation_id: str


class RoundResultEvent(TypedDict):
    event: str  # "round.result"
    simulation_id: str
    round_number: int
    matches: list[dict]


class StandingsUpdateEvent(TypedDict):
    event: str  # "standings.update"
    simulation_id: str
    standings: list[dict]


class ErrorEvent(TypedDict):
    event: str  # "error"
    message: str


# =============================================================================
# Client → Server Events
# =============================================================================

class StartSimulationCommand(TypedDict):
    type: str  # "simulation.start"
    payload: Optional[dict]


class PauseSimulationCommand(TypedDict):
    type: str  # "simulation.pause"


class ResumeSimulationCommand(TypedDict):
    type: str  # "simulation.resume"


class StopSimulationCommand(TypedDict):
    type: str  # "simulation.stop"


class SpeedChangeCommand(TypedDict):
    type: str  # "simulation.speed"
    multiplier: float