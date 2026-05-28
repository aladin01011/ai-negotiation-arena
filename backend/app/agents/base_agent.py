"""Base agent and strategy implementations."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import uuid

from ..games.payoff_matrix import Action, PayoffMatrix
from .memory import AgentMemory
from .personality import Personality


class Strategy(ABC):
    """Abstract base class for all agent strategies."""

    @abstractmethod
    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        """
        Decide whether to cooperate or defect.

        Args:
            agent_id: This agent's identifier
            opponent_id: Opponent agent's identifier
            memory: Agent's memory of past interactions
            personality: Agent's personality traits
            payoff_matrix: The payoff matrix for current game

        Returns:
            Action.COOPERATE or Action.DEFECT
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the strategy's logic."""
        ...


@dataclass
class Agent:
    """
    An autonomous agent in the simulation.
    
    Each agent has a strategy, personality, memory, and identity.
    The agent's decision-making is the composition of these parts.
    """

    agent_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = "Agent"
    strategy: Strategy = None
    personality: Personality = field(default_factory=Personality.strategic)
    memory: AgentMemory = None
    total_score: float = 0.0
    is_alive: bool = True

    def __post_init__(self):
        if self.memory is None:
            self.memory = AgentMemory(self.agent_id)
        if self.name == "Agent":
            self.name = f"{self.strategy.name}-{self.agent_id[:4]}"

    def decide(
        self,
        opponent_id: str,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        """Make a decision using the agent's strategy, personality, and memory."""
        return self.strategy.decide(
            agent_id=self.agent_id,
            opponent_id=opponent_id,
            memory=self.memory,
            personality=self.personality,
            payoff_matrix=payoff_matrix,
        )

    def update_score(self, payoff: float) -> None:
        """Add payoff to total score."""
        self.total_score += payoff

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "strategy": self.strategy.name if self.strategy else "unknown",
            "strategy_description": self.strategy.description if self.strategy else "",
            "personality": self.personality.to_dict(),
            "personality_label": self.personality.to_label(),
            "total_score": self.total_score,
            "is_alive": self.is_alive,
            "memory": self.memory.to_dict(),
        }


# =============================================================================
# Strategy Implementations
# =============================================================================


class AlwaysCooperate(Strategy):
    """Always cooperates regardless of opponent behavior."""

    @property
    def name(self) -> str:
        return "Always Cooperate"

    @property
    def description(self) -> str:
        return "Always chooses to cooperate, regardless of opponent."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        return Action.COOPERATE


class AlwaysDefect(Strategy):
    """Always defects regardless of opponent behavior."""

    @property
    def name(self) -> str:
        return "Always Defect"

    @property
    def description(self) -> str:
        return "Always chooses to defect, regardless of opponent."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        return Action.DEFECT


class TitForTat(Strategy):
    """The classic strategy: cooperate first, then mirror opponent's last move."""

    @property
    def name(self) -> str:
        return "Tit-for-Tat"

    @property
    def description(self) -> str:
        return "Cooperate on first move, then mirror opponent's previous action."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        last_action = memory.opponent_last_action(opponent_id)
        if last_action is None:
            # First interaction: cooperate
            return Action.COOPERATE
        # Mirror opponent's last action
        return last_action


class GrimTrigger(Strategy):
    """
    Cooperate until opponent defects once, then defect forever.
    The unforgiving strategy.
    """

    @property
    def name(self) -> str:
        return "Grim Trigger"

    @property
    def description(self) -> str:
        return "Cooperate until opponent defects, then defect forever after."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        history = memory.get_history(opponent_id)
        # Check if opponent has EVER defected
        for record in history:
            if record.opponent_action == Action.DEFECT:
                return Action.DEFECT
        return Action.COOPERATE


class Pavlov(Strategy):
    """
    Win-stay, lose-shift.
    If previous round was mutual cooperation or mutual defection (win), repeat.
    If previous round was one-sided (lose), switch.
    """

    @property
    def name(self) -> str:
        return "Pavlov"

    @property
    def description(self) -> str:
        return "Win-stay lose-shift: repeat action if last round was good, switch if bad."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        last = memory.last_interaction(opponent_id)
        if last is None:
            return Action.COOPERATE

        # "Win" = opponent cooperated (got good outcome)
        if last.opponent_action == Action.COOPERATE:
            return last.own_action  # Stay
        else:
            # "Lose" = opponent defected, switch
            return Action.DEFECT if last.own_action == Action.COOPERATE else Action.COOPERATE


class RandomStrategy(Strategy):
    """Randomly chooses cooperate or defect with equal probability."""

    def __init__(self, seed: Optional[int] = None):
        import random
        self._rng = random.Random(seed)

    @property
    def name(self) -> str:
        return "Random"

    @property
    def description(self) -> str:
        return "Randomly chooses cooperate or defect with 50% probability."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        return Action.COOPERATE if self._rng.random() < 0.5 else Action.DEFECT


class GenerousTitForTat(Strategy):
    """
    Like Tit-for-Tat but occasionally forgives defections.
    Cooperates after opponent defect with probability p.
    """

    def __init__(self, forgiveness_prob: float = 0.33):
        import random
        self._rng = random.Random()
        self.forgiveness_prob = forgiveness_prob

    @property
    def name(self) -> str:
        return "Generous TFT"

    @property
    def description(self) -> str:
        return f"Tit-for-Tat but forgives {self.forgiveness_prob*100:.0f}% of defections."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        last_action = memory.opponent_last_action(opponent_id)
        if last_action is None:
            return Action.COOPERATE
        if last_action == Action.COOPERATE:
            return Action.COOPERATE
        # Opponent defected — maybe forgive
        return Action.COOPERATE if self._rng.random() < self.forgiveness_prob else Action.DEFECT


class AdaptiveStrategy(Strategy):
    """
    Uses personality traits to modulate decision-making.
    The personality-aware strategy that serves as a bridge to RL agents.
    """

    @property
    def name(self) -> str:
        return "Adaptive"

    @property
    def description(self) -> str:
        return "Uses personality traits (trust, greed, forgiveness) to make decisions."

    def decide(
        self,
        agent_id: str,
        opponent_id: str,
        memory: AgentMemory,
        personality: Personality,
        payoff_matrix: PayoffMatrix,
    ) -> Action:
        last_action = memory.opponent_last_action(opponent_id)

        # First move: use trust level
        if last_action is None:
            return Action.COOPERATE if personality.trust > 0.5 else Action.DEFECT

        # Opponent's cooperation rate
        coop_rate = memory.opponent_cooperation_rate(opponent_id)

        # Probability of cooperating = f(reciprocity, forgiveness, coop_rate)
        # Start with base tendency to mirror
        prob_cooperate = coop_rate * personality.reciprocity

        # Add forgiveness (willingness to cooperate after defection)
        if last_action == Action.DEFECT:
            prob_cooperate += personality.forgiveness * 0.3

        # Subtract greed (temptation to defect)
        prob_cooperate -= personality.greed * 0.2

        # Clamp
        prob_cooperate = max(0.0, min(1.0, prob_cooperate))

        import random
        return Action.COOPERATE if random.random() < prob_cooperate else Action.DEFECT


# Registry of all available strategies
STRATEGY_REGISTRY: dict[str, type[Strategy]] = {
    "always_cooperate": AlwaysCooperate,
    "always_defect": AlwaysDefect,
    "tit_for_tat": TitForTat,
    "grim_trigger": GrimTrigger,
    "pavlov": Pavlov,
    "random": RandomStrategy,
    "generous_tft": GenerousTitForTat,
    "adaptive": AdaptiveStrategy,
}


def create_strategy(name: str) -> Strategy:
    """Factory function to create a strategy by name."""
    strategy_class = STRATEGY_REGISTRY.get(name)
    if not strategy_class:
        raise ValueError(
            f"Unknown strategy: {name}. "
            f"Available: {list(STRATEGY_REGISTRY.keys())}"
        )
    return strategy_class()


def list_strategies() -> list[dict]:
    """List all available strategies with descriptions."""
    return [
        {
            "id": name,
            "name": strategy_class().name,
            "description": strategy_class().description,
        }
        for name, strategy_class in STRATEGY_REGISTRY.items()
    ]