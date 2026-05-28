"""SQLAlchemy database models for persistent storage."""

from __future__ import annotations

import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class AgentModel(Base):
    """Persistent agent record."""
    __tablename__ = "agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    personality = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    scores = relationship("AgentScoreModel", back_populates="agent")

    def to_dict(self) -> dict:
        return {
            "agent_id": str(self.agent_id),
            "name": self.name,
            "strategy_type": self.strategy_type,
            "personality": self.personality,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SimulationModel(Base):
    """Persistent simulation record."""
    __tablename__ = "simulations"

    simulation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config = Column(JSON, nullable=False, default=dict)
    status = Column(String(20), default="idle")  # idle, running, paused, completed, error
    rounds_completed = Column(Integer, default=0)
    total_rounds = Column(Integer, default=100)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    summary = Column(JSON, nullable=True)

    # Relationships
    rounds = relationship("RoundModel", back_populates="simulation")
    scores = relationship("AgentScoreModel", back_populates="simulation")

    def to_dict(self) -> dict:
        return {
            "simulation_id": str(self.simulation_id),
            "config": self.config,
            "status": self.status,
            "rounds_completed": self.rounds_completed,
            "total_rounds": self.total_rounds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "summary": self.summary,
        }


class RoundModel(Base):
    """Persistent round record within a simulation."""
    __tablename__ = "rounds"

    round_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("simulations.simulation_id"),
        nullable=False,
    )
    round_number = Column(Integer, nullable=False)
    results = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    simulation = relationship("SimulationModel", back_populates="rounds")


class AgentScoreModel(Base):
    """Per-simulation agent scores and statistics."""
    __tablename__ = "agent_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("simulations.simulation_id"),
        nullable=False,
    )
    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.agent_id"),
        nullable=False,
    )
    total_score = Column(Float, default=0.0)
    cooperation_count = Column(Integer, default=0)
    defection_count = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)

    # Relationships
    simulation = relationship("SimulationModel", back_populates="scores")
    agent = relationship("AgentModel", back_populates="scores")

    def to_dict(self) -> dict:
        return {
            "agent_id": str(self.agent_id),
            "total_score": self.total_score,
            "cooperation_count": self.cooperation_count,
            "defection_count": self.defection_count,
            "rank": self.rank,
        }