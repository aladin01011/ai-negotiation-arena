"""Tests for agent strategy implementations."""

import pytest
from app.games.payoff_matrix import Action, PayoffMatrix
from app.agents.base_agent import (
    Agent,
    AlwaysCooperate,
    AlwaysDefect,
    TitForTat,
    GrimTrigger,
    Pavlov,
    RandomStrategy,
    GenerousTitForTat,
    AdaptiveStrategy,
    create_strategy,
    list_strategies,
)
from app.agents.memory import AgentMemory, InteractionRecord
from app.agents.personality import Personality


class TestStrategies:
    """Test suite for all strategy implementations."""

    @pytest.fixture
    def payoff_matrix(self):
        return PayoffMatrix.prisoner_dilemma()

    @pytest.fixture
    def memory(self):
        return AgentMemory("test_agent")

    def test_always_cooperate(self, payoff_matrix, memory):
        strategy = AlwaysCooperate()
        personality = Personality.random()
        
        # Always returns COOPERATE
        for _ in range(10):
            action = strategy.decide(
                "a", "b", memory, personality, payoff_matrix
            )
            assert action == Action.COOPERATE

    def test_always_defect(self, payoff_matrix, memory):
        strategy = AlwaysDefect()
        personality = Personality.random()
        
        # Always returns DEFECT
        for _ in range(10):
            action = strategy.decide(
                "a", "b", memory, personality, payoff_matrix
            )
            assert action == Action.DEFECT

    def test_tit_for_tat_first_move(self, payoff_matrix, memory):
        """Tit-for-Tat should cooperate on first move."""
        strategy = TitForTat()
        personality = Personality.random()
        
        action = strategy.decide("a", "b", memory, personality, payoff_matrix)
        assert action == Action.COOPERATE

    def test_tit_for_tat_mirrors(self, payoff_matrix):
        """Tit-for-Tat should mirror opponent's last action."""
        strategy = TitForTat()
        memory = AgentMemory("a")
        personality = Personality.random()

        # Add a record where opponent defected
        memory.remember(InteractionRecord(
            opponent_id="b",
            own_action=Action.COOPERATE,
            opponent_action=Action.DEFECT,
            payoff=0,
            round_number=1,
        ))

        action = strategy.decide("a", "b", memory, personality, payoff_matrix)
        assert action == Action.DEFECT  # Mirror defect

        # Add a record where opponent cooperated
        memory.remember(InteractionRecord(
            opponent_id="b",
            own_action=Action.COOPERATE,
            opponent_action=Action.COOPERATE,
            payoff=3,
            round_number=2,
        ))

        action = strategy.decide("a", "b", memory, personality, payoff_matrix)
        assert action == Action.COOPERATE  # Mirror cooperate

    def test_grim_trigger_first_move(self, payoff_matrix, memory):
        """Grim Trigger should cooperate on first move."""
        strategy = GrimTrigger()
        personality = Personality.random()
        
        action = strategy.decide("a", "b", memory, personality, payoff_matrix)
        assert action == Action.COOPERATE

    def test_grim_trigger_after_defection(self, payoff_matrix):
        """Grim Trigger should defect forever after opponent defects."""
        strategy = GrimTrigger()
        memory = AgentMemory("a")
        personality = Personality.random()

        # Add a record where opponent defected
        memory.remember(InteractionRecord(
            opponent_id="b",
            own_action=Action.COOPERATE,
            opponent_action=Action.DEFECT,
            payoff=0,
            round_number=1,
        ))

        # Should defect forever now
        for _ in range(10):
            action = strategy.decide("a", "b", memory, personality, payoff_matrix)
            assert action == Action.DEFECT

    def test_pavlov_win_stay(self, payoff_matrix):
        """Pavlov should repeat action after a 'win' (opponent cooperated)."""
        strategy = Pavlov()
        memory = AgentMemory("a")
        personality = Personality.random()

        memory.remember(InteractionRecord(
            opponent_id="b",
            own_action=Action.COOPERATE,
            opponent_action=Action.COOPERATE,  # Win
            payoff=3,
            round_number=1,
        ))

        action = strategy.decide("a", "b", memory, personality, payoff_matrix)
        assert action == Action.COOPERATE  # Stay

    def test_pavlov_lose_shift(self, payoff_matrix):
        """Pavlov should switch action after a 'loss' (opponent defected)."""
        strategy = Pavlov()
        memory = AgentMemory("a")
        personality = Personality.random()

        memory.remember(InteractionRecord(
            opponent_id="b",
            own_action=Action.COOPERATE,
            opponent_action=Action.DEFECT,  # Loss
            payoff=0,
            round_number=1,
        ))

        action = strategy.decide("a", "b", memory, personality, payoff_matrix)
        assert action == Action.DEFECT  # Shift

    def test_create_strategy(self):
        """Strategy factory should create correct types."""
        strategy = create_strategy("tit_for_tat")
        assert isinstance(strategy, TitForTat)

        strategy = create_strategy("always_defect")
        assert isinstance(strategy, AlwaysDefect)

        with pytest.raises(ValueError):
            create_strategy("nonexistent_strategy")

    def test_list_strategies(self):
        """list_strategies should return all available strategies."""
        strategies = list_strategies()
        assert len(strategies) >= 8
        strategy_ids = [s["id"] for s in strategies]
        assert "tit_for_tat" in strategy_ids
        assert "always_defect" in strategy_ids
        assert "grim_trigger" in strategy_ids

    def test_agent_integration(self, payoff_matrix):
        """Full agent integration test."""
        agent = Agent(
            name="TestAgent",
            strategy=TitForTat(),
            personality=Personality.cooperative(),
        )
        
        # First decision
        action = agent.decide("opponent_1", payoff_matrix)
        assert action == Action.COOPERATE
        
        # Update score
        agent.update_score(5.0)
        assert agent.total_score == 5.0
        
        # Agent dict should include all fields
        d = agent.to_dict()
        assert d["agent_id"] == agent.agent_id
        assert d["name"] == "TestAgent"
        assert d["strategy"] == "Tit-for-Tat"
        assert d["total_score"] == 5.0