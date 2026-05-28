"""CRUD operations for database access."""

from __future__ import annotations

import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    AgentModel,
    SimulationModel,
    RoundModel,
    AgentScoreModel,
)


class DatabaseService:
    """Service layer for database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==========================================================================
    # Agents
    # ==========================================================================

    async def create_agent(
        self,
        agent_id: str,
        name: str,
        strategy_type: str,
        personality: dict,
    ) -> AgentModel:
        agent = AgentModel(
            agent_id=uuid.UUID(agent_id) if isinstance(agent_id, str) else agent_id,
            name=name,
            strategy_type=strategy_type,
            personality=personality,
        )
        self.session.add(agent)
        await self.session.commit()
        return agent

    async def get_agent(self, agent_id: str) -> Optional[AgentModel]:
        result = await self.session.execute(
            select(AgentModel).where(AgentModel.agent_id == uuid.UUID(agent_id))
        )
        return result.scalar_one_or_none()

    async def list_agents(self) -> List[AgentModel]:
        result = await self.session.execute(select(AgentModel))
        return result.scalars().all()

    # ==========================================================================
    # Simulations
    # ==========================================================================

    async def create_simulation(
        self,
        simulation_id: str,
        config: dict,
        total_rounds: int,
    ) -> SimulationModel:
        sim = SimulationModel(
            simulation_id=uuid.UUID(simulation_id) if isinstance(simulation_id, str) else simulation_id,
            config=config,
            total_rounds=total_rounds,
        )
        self.session.add(sim)
        await self.session.commit()
        return sim

    async def get_simulation(self, simulation_id: str) -> Optional[SimulationModel]:
        result = await self.session.execute(
            select(SimulationModel).where(
                SimulationModel.simulation_id == uuid.UUID(simulation_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_simulations(
        self, limit: int = 20, offset: int = 0
    ) -> List[SimulationModel]:
        result = await self.session.execute(
            select(SimulationModel)
            .order_by(SimulationModel.started_at.desc().nullslast())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def update_simulation_status(
        self, simulation_id: str, status: str
    ) -> Optional[SimulationModel]:
        sim = await self.get_simulation(simulation_id)
        if sim:
            sim.status = status
            await self.session.commit()
        return sim

    # ==========================================================================
    # Rounds
    # ==========================================================================

    async def save_round(
        self, simulation_id: str, round_number: int, results: list
    ) -> RoundModel:
        round_record = RoundModel(
            simulation_id=uuid.UUID(simulation_id) if isinstance(simulation_id, str) else simulation_id,
            round_number=round_number,
            results=results,
        )
        self.session.add(round_record)
        await self.session.commit()
        return round_record

    # ==========================================================================
    # Agent Scores
    # ==========================================================================

    async def save_agent_scores(
        self, simulation_id: str, scores: list[dict]
    ) -> None:
        """Save final agent scores for a simulation."""
        for score_data in scores:
            score = AgentScoreModel(
                simulation_id=uuid.UUID(simulation_id) if isinstance(simulation_id, str) else simulation_id,
                agent_id=uuid.UUID(score_data["agent_id"]),
                total_score=score_data.get("total_score", 0),
                cooperation_count=score_data.get("cooperation_count", 0),
                defection_count=score_data.get("defection_count", 0),
                rank=score_data.get("rank"),
            )
            self.session.add(score)
        await self.session.commit()