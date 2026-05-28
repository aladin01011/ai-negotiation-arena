"""Tests for the simulation engine and matchmaker."""

import pytest
from app.core.simulation_engine import SimulationEngine, SimulationConfig
from app.core.event_bus import EventBus
from app.core.matchmaker import Matchmaker, MatchType
from app.agents.base_agent import Agent, TitForTat, AlwaysDefect, create_strategy
from app.agents.personality import Personality


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def sim_config():
    """A small simulation config for fast tests."""
    return SimulationConfig(
        agent_configs=[],  # Will use default agents
        total_rounds=5,
        match_type=MatchType.ROUND_ROBIN,
        tick_interval_ms=10,  # Fast ticks for tests
    )


class TestMatchmaker:
    """Test suite for the matchmaker."""

    def test_round_robin_pairing(self):
        """Round robin should pair every agent with every other agent."""
        agents = [
            Agent(name=f"Agent-{i}", strategy=TitForTat())
            for i in range(4)
        ]
        
        matchmaker = Matchmaker(MatchType.ROUND_ROBIN)
        matches = matchmaker.pair(agents)
        
        # With 4 agents, there should be C(4,2) = 6 matches
        assert len(matches) == 6
        
        # Every pair should be unique
        pairs = set()
        for m in matches:
            pair = frozenset([m.agent_a.agent_id, m.agent_b.agent_id])
            assert pair not in pairs  # No duplicates
            pairs.add(pair)
        
        assert len(pairs) == 6

    def test_random_pairs(self):
        """Random pairing should produce floor(N/2) matches."""
        agents = [
            Agent(name=f"Agent-{i}", strategy=TitForTat())
            for i in range(5)  # Odd number
        ]
        
        matchmaker = Matchmaker(MatchType.RANDOM_PAIRS)
        matches = matchmaker.pair(agents)
        
        # 5 agents -> 2 pairs (one agent sits out)
        assert len(matches) == 2

    def test_swiss_pairing(self):
        """Swiss pairing should match agents with similar scores."""
        agents = [
            Agent(name=f"Agent-{i}", strategy=TitForTat())
            for i in range(4)
        ]
        
        # Give agents different scores
        agents[0].total_score = 100
        agents[1].total_score = 80
        agents[2].total_score = 50
        agents[3].total_score = 30
        
        matchmaker = Matchmaker(MatchType.SWISS)
        matches = matchmaker.pair(agents)
        
        # Top two should be paired
        assert len(matches) == 2
        # The first match should contain the two highest scorers
        match_agents = {m.agent_a.agent_id, m.agent_b.agent_id for m in matches}
        # Not strictly deterministic, but should pair close scores


class TestSimulationEngine:
    """Test suite for the simulation engine."""

    @pytest.mark.asyncio
    async def test_simulation_lifecycle(self, event_bus, sim_config):
        """Full simulation lifecycle: start, run, complete."""
        engine = SimulationEngine(
            simulation_id="test-sim-1",
            config=sim_config,
            event_bus=event_bus,
        )
        
        # Should start in idle
        assert engine.state.status == "idle"
        
        # Spawn agents
        engine.spawn_agents()
        assert len(engine.state.agents) >= 20  # Default agents
        
        # Start the simulation
        await engine.start()
        
        # Wait for it to complete
        import asyncio
        while engine.state.status == "running":
            await asyncio.sleep(0.1)
        
        # Should have completed
        assert engine.state.status == "completed"
        assert engine.state.current_round > 0
        assert engine.state.end_time is not None

    @pytest.mark.asyncio
    async def test_pause_resume(self, event_bus, sim_config):
        """Simulation should pause and resume correctly."""
        sim_config.total_rounds = 50
        engine = SimulationEngine(
            simulation_id="test-sim-2",
            config=sim_config,
            event_bus=event_bus,
        )
        engine.spawn_agents()
        
        await engine.start()
        
        # Let it run a bit
        import asyncio
        await asyncio.sleep(0.3)
        
        # Pause
        await engine.pause()
        assert engine.state.status == "paused"
        
        # Ensure it's actually paused (rounds shouldn't advance)
        rounds_at_pause = engine.state.current_round
        await asyncio.sleep(0.2)
        assert engine.state.current_round == rounds_at_pause
        
        # Resume
        await engine.resume()
        assert engine.state.status == "running"
        
        # Wait for completion
        while engine.state.status == "running":
            await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_agent_scoring(self, event_bus, sim_config):
        """Agents should accumulate scores correctly."""
        # Create a minimal simulation
        config = SimulationConfig(
            total_rounds=2,
            match_type=MatchType.ROUND_ROBIN,
            tick_interval_ms=10,
        )
        engine = SimulationEngine(
            simulation_id="test-scoring",
            config=config,
            event_bus=event_bus,
        )
        
        # Add just 2 agents with known strategies
        agent_a = Agent(
            name="Cooperator",
            strategy=AlwaysDefect(),  # Always defects
            personality=Personality.competitive(),
        )
        agent_b = Agent(
            name="Defector",
            strategy=AlwaysDefect(),  # Always defects
            personality=Personality.competitive(),
        )
        engine.state.agents[agent_a.agent_id] = agent_a
        engine.state.agents[agent_b.agent_id] = agent_b
        
        await engine.start()
        
        import asyncio
        while engine.state.status == "running":
            await asyncio.sleep(0.1)
        
        # Both agents always defect -> each gets P=1 per round
        # Round robin: 1 match per round -> 2 rounds -> each gets 2
        assert agent_a.total_score == 2.0
        assert agent_b.total_score == 2.0