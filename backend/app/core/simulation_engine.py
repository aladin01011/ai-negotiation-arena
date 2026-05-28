"""The core simulation engine — runs the tournament loop."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Awaitable

from ..agents.base_agent import (
    Agent,
    create_strategy,
    STRATEGY_REGISTRY,
)
from ..agents.personality import Personality
from ..games.prisoner_dilemma import PrisonerDilemma, RoundResult, MatchResult
from ..games.payoff_matrix import Action
from .matchmaker import Matchmaker, MatchType, Match
from .event_bus import EventBus, EventType

logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    agent_configs: list[dict] = field(default_factory=list)
    total_rounds: int = 100
    match_type: MatchType = MatchType.ROUND_ROBIN
    game_type: str = "prisoner_dilemma"
    tick_interval_ms: int = 500
    speed_multiplier: float = 1.0
    track_all_history: bool = True


@dataclass
class SimulationState:
    """The full state of a running simulation."""
    simulation_id: str
    config: SimulationConfig
    agents: dict[str, Agent] = field(default_factory=dict)
    current_round: int = 0
    status: str = "idle"  # idle, running, paused, completed, error
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    round_history: list[RoundResult] = field(default_factory=list)

    @property
    def is_running(self) -> bool:
        return self.status == "running"

    @property
    def elapsed_seconds(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time


class SimulationEngine:
    """
    The central simulation loop.
    
    Manages agent lifecycle, round execution, and state broadcasting.
    Designed as an async context manager for clean lifecycle.
    """

    def __init__(
        self,
        simulation_id: str,
        config: SimulationConfig,
        event_bus: EventBus,
        on_state_change: Optional[Callable[[SimulationState], Awaitable[None]]] = None,
    ):
        self.simulation_id = simulation_id
        self.config = config
        self.event_bus = event_bus
        self.on_state_change = on_state_change

        self.state = SimulationState(
            simulation_id=simulation_id,
            config=config,
        )
        self.game = PrisonerDilemma()
        self.matchmaker = Matchmaker(config.match_type)
        self._running_task: Optional[asyncio.Task] = None
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially
        self._stop_requested = False

    def spawn_agents(self) -> None:
        """Create agents from configuration."""
        if self.config.agent_configs:
            # Custom agent configs provided
            for cfg in self.config.agent_configs:
                strategy = create_strategy(cfg.get("strategy", "tit_for_tat"))
                personality = Personality(
                    trust=cfg.get("trust", 0.5),
                    greed=cfg.get("greed", 0.5),
                    forgiveness=cfg.get("forgiveness", 0.5),
                    reciprocity=cfg.get("reciprocity", 0.7),
                    spite=cfg.get("spite", 0.3),
                    risk_tolerance=cfg.get("risk_tolerance", 0.5),
                )
                agent = Agent(
                    name=cfg.get("name", f"Agent-{len(self.state.agents)}"),
                    strategy=strategy,
                    personality=personality,
                )
                self.state.agents[agent.agent_id] = agent
        else:
            # Default: create a balanced mix of strategies
            strategy_names = list(STRATEGY_REGISTRY.keys())
            num_agents = self.config.agent_configs or 20
            
            import random
            rng = random.Random(42)
            
            for i in range(
                max(4, self.config.agent_configs if isinstance(self.config.agent_configs, int) else 20)
            ):
                # Actually, let's handle the case where agent_configs might be an int
                pass
            
            # Default: create 20 agents with varied strategies
            default_distribution = {
                "always_cooperate": 2,
                "always_defect": 2,
                "tit_for_tat": 4,
                "grim_trigger": 2,
                "pavlov": 2,
                "random": 2,
                "generous_tft": 3,
                "adaptive": 3,
            }
            
            for strategy_name, count in default_distribution.items():
                for j in range(count):
                    strategy = create_strategy(strategy_name)
                    personality = Personality.random(seed=hash(strategy_name) + j)
                    agent = Agent(
                        name=f"{strategy.name}-{j+1}",
                        strategy=strategy,
                        personality=personality,
                    )
                    self.state.agents[agent.agent_id] = agent

        logger.info(
            f"Spawned {len(self.state.agents)} agents "
            f"for simulation {self.simulation_id}"
        )

    async def start(self) -> None:
        """Start the simulation loop in a background task."""
        if self.state.status not in ("idle", "completed", "error"):
            raise RuntimeError(f"Cannot start simulation in state: {self.state.status}")

        self.state.status = "running"
        self.state.start_time = time.time()
        self._stop_requested = False

        # Publish start event
        await self.event_bus.publish(
            EventType.SIMULATION_STARTED,
            simulation_id=self.simulation_id,
            agent_count=len(self.state.agents),
            total_rounds=self.config.total_rounds,
        )

        # Start the run loop in background
        self._running_task = asyncio.create_task(self._run_loop())
        logger.info(f"Simulation {self.simulation_id} started")

    async def pause(self) -> None:
        """Pause the simulation."""
        if self.state.status == "running":
            self.state.status = "paused"
            self._pause_event.clear()
            await self.event_bus.publish(
                EventType.SIMULATION_PAUSED,
                simulation_id=self.simulation_id,
            )
            logger.info(f"Simulation {self.simulation_id} paused")

    async def resume(self) -> None:
        """Resume a paused simulation."""
        if self.state.status == "paused":
            self.state.status = "running"
            self._pause_event.set()
            await self.event_bus.publish(
                EventType.SIMULATION_RESUMED,
                simulation_id=self.simulation_id,
            )
            logger.info(f"Simulation {self.simulation_id} resumed")

    async def stop(self) -> None:
        """Stop the simulation entirely."""
        self._stop_requested = True
        self._pause_event.set()  # Unpause so loop can exit
        if self._running_task:
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                pass
        self.state.status = "completed"
        self.state.end_time = time.time()
        await self.event_bus.publish(
            EventType.SIMULATION_ENDED,
            simulation_id=self.simulation_id,
            final_state=self._get_summary(),
        )
        logger.info(f"Simulation {self.simulation_id} stopped")

    async def _run_loop(self) -> None:
        """Main simulation loop."""
        try:
            for round_num in range(1, self.config.total_rounds + 1):
                # Check for stop request
                if self._stop_requested:
                    break

                # Wait if paused
                await self._pause_event.wait()

                self.state.current_round = round_num

                # Publish round start
                await self.event_bus.publish(
                    EventType.ROUND_STARTED,
                    simulation_id=self.simulation_id,
                    round_number=round_num,
                )

                # Get active agents
                active_agents = [
                    a for a in self.state.agents.values() if a.is_alive
                ]
                if len(active_agents) < 2:
                    logger.info("Less than 2 agents alive, ending simulation")
                    break

                # Pair agents
                matches = self.matchmaker.pair(active_agents)

                # Run all matches concurrently
                match_results = await asyncio.gather(*[
                    self._run_match(match, round_num) for match in matches
                ])

                # Create round result
                round_result = RoundResult(
                    round_number=round_num,
                    matches=[r for r in match_results if r is not None],
                )

                # Store in history
                if self.config.track_all_history:
                    self.state.round_history.append(round_result)

                # Publish round completed
                await self.event_bus.publish(
                    EventType.ROUND_COMPLETED,
                    simulation_id=self.simulation_id,
                    round_result=round_result,
                )

                # Publish standings
                await self.event_bus.publish(
                    EventType.STANDINGS_UPDATED,
                    simulation_id=self.simulation_id,
                    standings=self._get_standings(),
                )

                # Tick interval (respect speed multiplier)
                tick_ms = self.config.tick_interval_ms / self.config.speed_multiplier
                await asyncio.sleep(tick_ms / 1000.0)

                # Notify state change
                if self.on_state_change:
                    await self.on_state_change(self.state)

            # Loop completed normally
            self.state.status = "completed"
            self.state.end_time = time.time()
            await self.event_bus.publish(
                EventType.SIMULATION_ENDED,
                simulation_id=self.simulation_id,
                final_state=self._get_summary(),
            )

        except asyncio.CancelledError:
            logger.info(f"Simulation {self.simulation_id} task cancelled")
            raise
        except Exception as e:
            logger.error(
                f"Simulation {self.simulation_id} error: {e}", exc_info=True
            )
            self.state.status = "error"
            await self.event_bus.publish(
                EventType.ERROR,
                simulation_id=self.simulation_id,
                error=str(e),
            )

    async def _run_match(
        self, match: Match, round_number: int
    ) -> Optional[MatchResult]:
        """Run a single match between two agents."""
        agent_a = match.agent_a
        agent_b = match.agent_b

        # Both agents decide
        action_a = agent_a.decide(
            opponent_id=agent_b.agent_id,
            payoff_matrix=self.game.payoff_matrix,
        )
        action_b = agent_b.decide(
            opponent_id=agent_a.agent_id,
            payoff_matrix=self.game.payoff_matrix,
        )

        # Resolve the game
        result = self.game.play(
            agent_a_id=agent_a.agent_id,
            agent_b_id=agent_b.agent_id,
            action_a=action_a,
            action_b=action_b,
            round_number=round_number,
        )

        # Update scores
        agent_a.update_score(result.payoff_a)
        agent_b.update_score(result.payoff_b)

        # Update memories
        from ..agents.memory import InteractionRecord

        agent_a.memory.remember(
            InteractionRecord(
                opponent_id=agent_b.agent_id,
                own_action=action_a,
                opponent_action=action_b,
                payoff=result.payoff_a,
                round_number=round_number,
            )
        )
        agent_b.memory.remember(
            InteractionRecord(
                opponent_id=agent_a.agent_id,
                own_action=action_b,
                opponent_action=action_a,
                payoff=result.payoff_b,
                round_number=round_number,
            )
        )

        # Publish match completed
        await self.event_bus.publish(
            EventType.MATCH_COMPLETED,
            simulation_id=self.simulation_id,
            match_result=result,
        )

        return result

    def _get_standings(self) -> list[dict]:
        """Get current standings sorted by score."""
        standings = []
        for agent in sorted(
            self.state.agents.values(),
            key=lambda a: a.total_score,
            reverse=True,
        ):
            standings.append({
                "rank": len(standings) + 1,
                "agent_id": agent.agent_id,
                "name": agent.name,
                "strategy": agent.strategy.name if agent.strategy else "unknown",
                "personality_label": agent.personality.to_label(),
                "total_score": agent.total_score,
                "total_interactions": agent.memory.total_interactions(),
            })
        return standings

    def _get_summary(self) -> dict:
        """Get a summary of the simulation results."""
        standings = self._get_standings()
        return {
            "simulation_id": self.simulation_id,
            "total_rounds": self.state.current_round,
            "total_agents": len(self.state.agents),
            "elapsed_seconds": self.state.elapsed_seconds,
            "status": self.state.status,
            "standings": standings,
            "top_agent": standings[0] if standings else None,
        }

    def set_speed(self, multiplier: float) -> None:
        """Change simulation speed."""
        self.config.speed_multiplier = max(
            0.1, min(self.config.MAX_SPEED_MULTIPLIER, multiplier)
        )
        logger.info(
            f"Simulation {self.simulation_id} speed set to {multiplier}x"
        )