"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Schema for configuring an agent in a simulation."""
    name: str = "Agent"
    strategy: str = Field(default="tit_for_tat", description="Strategy identifier")
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    greed: float = Field(default=0.5, ge=0.0, le=1.0)
    forgiveness: float = Field(default=0.5, ge=0.0, le=1.0)
    reciprocity: float = Field(default=0.7, ge=0.0, le=1.0)
    spite: float = Field(default=0.3, ge=0.0, le=1.0)
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)


class CreateSimulationRequest(BaseModel):
    """Schema for creating a new simulation."""
    agent_configs: Optional[List[AgentConfig]] = None
    rounds: int = Field(default=100, ge=10, le=10000)
    match_type: str = Field(default="round_robin", pattern="^(round_robin|random_pairs|swiss|elimination)$")
    speed_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)

    class Config:
        json_schema_extra = {
            "example": {
                "rounds": 100,
                "match_type": "round_robin",
                "speed_multiplier": 1.0,
            }
        }


class SimulationResponse(BaseModel):
    """Schema for simulation data in responses."""
    simulation_id: str
    status: str
    rounds_completed: int
    total_rounds: int
    agent_count: int
    elapsed_seconds: float

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    """Schema for agent data in responses."""
    agent_id: str
    name: str
    strategy: str
    personality_label: str
    total_score: float
    total_interactions: int

    class Config:
        from_attributes = True


class StandingsResponse(BaseModel):
    """Schema for tournament standings."""
    standings: List[AgentResponse]


class StrategyInfo(BaseModel):
    """Schema describing an available strategy."""
    id: str
    name: str
    description: str