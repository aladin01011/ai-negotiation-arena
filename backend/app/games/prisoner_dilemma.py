"""Prisoner's Dilemma game logic — the core strategic interaction."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional
import uuid

from .payoff_matrix import PayoffMatrix, Action


@dataclass
class MatchResult:
    """The outcome of a single game between two agents."""
    match_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_a_id: str = ""
    agent_b_id: str = ""
    action_a: Optional[Action] = None
    action_b: Optional[Action] = None
    payoff_a: float = 0.0
    payoff_b: float = 0.0
    round_number: int = 0

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "agent_a_id": self.agent_a_id,
            "agent_b_id": self.agent_b_id,
            "action_a": self.action_a.value if self.action_a else None,
            "action_b": self.action_b.value if self.action_b else None,
            "payoff_a": self.payoff_a,
            "payoff_b": self.payoff_b,
            "round_number": self.round_number,
        }


@dataclass
class RoundResult:
    """Collection of all match results for a single simulation round."""
    round_number: int
    matches: list[MatchResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "round_number": self.round_number,
            "matches": [m.to_dict() for m in self.matches],
        }


class PrisonerDilemma:
    """
    The Prisoner's Dilemma game engine.
    
    Handles the rules, payoff computation, and result generation
    for pairwise prisoner's dilemma interactions.
    """

    def __init__(self, payoff_matrix: Optional[PayoffMatrix] = None):
        self.payoff_matrix = payoff_matrix or PayoffMatrix.prisoner_dilemma()

    def play(
        self,
        agent_a_id: str,
        agent_b_id: str,
        action_a: Action,
        action_b: Action,
        round_number: int = 0,
    ) -> MatchResult:
        """
        Resolve a single Prisoner's Dilemma interaction.
        
        Args:
            agent_a_id: Identifier for agent A
            agent_b_id: Identifier for agent B
            action_a: Agent A's chosen action
            action_b: Agent B's chosen action
            round_number: Current simulation round
            
        Returns:
            MatchResult with actions and payoffs
        """
        payoff_a, payoff_b = self.payoff_matrix.payoff(action_a, action_b)

        return MatchResult(
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            action_a=action_a,
            action_b=action_b,
            payoff_a=payoff_a,
            payoff_b=payoff_b,
            round_number=round_number,
        )

    def is_cooperative_outcome(self, result: MatchResult) -> bool:
        """Check if both agents cooperated."""
        return (
            result.action_a == Action.COOPERATE
            and result.action_b == Action.COOPERATE
        )

    def is_mutual_defection(self, result: MatchResult) -> bool:
        """Check if both agents defected."""
        return (
            result.action_a == Action.DEFECT
            and result.action_b == Action.DEFECT
        )

    def get_social_welfare(self, result: MatchResult) -> float:
        """Total payoff (social welfare) of the outcome."""
        return result.payoff_a + result.payoff_b

    @staticmethod
    def describe_outcome(action_a: Action, action_b: Action) -> str:
        """Human-readable description of the outcome."""
        if action_a == Action.COOPERATE and action_b == Action.COOPERATE:
            return "🤝 Mutual Cooperation! (Both win)"
        elif action_a == Action.DEFECT and action_b == Action.DEFECT:
            return "💥 Mutual Defection! (Both lose)"
        elif action_a == Action.COOPERATE and action_b == Action.DEFECT:
            return "🔪 A got betrayed! (B defects, A cooperates)"
        else:
            return "🔪 B got betrayed! (A defects, B cooperates)"