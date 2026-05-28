"""Agent memory system — stores interaction history and builds opponent models."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from ..games.payoff_matrix import Action


@dataclass
class InteractionRecord:
    """Record of a single interaction with another agent."""
    opponent_id: str
    own_action: Action
    opponent_action: Action
    payoff: float
    round_number: int

    def to_dict(self) -> dict:
        return {
            "opponent_id": self.opponent_id,
            "own_action": self.own_action.value,
            "opponent_action": self.opponent_action.value,
            "payoff": self.payoff,
            "round_number": self.round_number,
        }


class AgentMemory:
    """
    Stores and analyzes an agent's interaction history.
    
    Provides query methods for strategy decision-making:
    - How often has this opponent cooperated?
    - What did they do last time?
    - What's my average payoff against them?
    """

    def __init__(self, agent_id: str, max_history: int = 1000):
        self.agent_id = agent_id
        self.max_history = max_history

        # history[opponent_id] = list of InteractionRecord
        self._history: Dict[str, List[InteractionRecord]] = defaultdict(list)
        self._all_interactions: List[InteractionRecord] = []

    def remember(self, record: InteractionRecord) -> None:
        """Store an interaction in memory."""
        self._history[record.opponent_id].append(record)
        self._all_interactions.append(record)

        # Trim if exceeds max
        if len(self._all_interactions) > self.max_history:
            oldest = self._all_interactions.pop(0)
            opp_history = self._history.get(oldest.opponent_id, [])
            if opp_history and opp_history[0] is oldest:
                opp_history.pop(0)

    def get_history(self, opponent_id: str) -> List[InteractionRecord]:
        """Get all interactions with a specific opponent."""
        return self._history.get(opponent_id, [])

    def last_interaction(self, opponent_id: str) -> Optional[InteractionRecord]:
        """Get the most recent interaction with an opponent."""
        history = self._history.get(opponent_id, [])
        return history[-1] if history else None

    def opponent_cooperation_rate(self, opponent_id: str) -> float:
        """How often has this opponent cooperated against me?"""
        history = self._history.get(opponent_id, [])
        if not history:
            return 0.5  # Neutral prior
        cooperations = sum(
            1 for r in history if r.opponent_action == Action.COOPERATE
        )
        return cooperations / len(history)

    def opponent_last_action(self, opponent_id: str) -> Optional[Action]:
        """What did opponent do in our most recent interaction?"""
        last = self.last_interaction(opponent_id)
        return last.opponent_action if last else None

    def average_payoff(self, opponent_id: Optional[str] = None) -> float:
        """Average payoff against a specific opponent (or all opponents)."""
        if opponent_id:
            history = self._history.get(opponent_id, [])
        else:
            history = self._all_interactions

        if not history:
            return 0.0
        return sum(r.payoff for r in history) / len(history)

    def total_interactions(self) -> int:
        """Total number of interactions in memory."""
        return len(self._all_interactions)

    def get_opponents(self) -> List[str]:
        """Get list of all opponents we've interacted with."""
        return list(self._history.keys())

    def clear(self) -> None:
        """Reset all memory."""
        self._history.clear()
        self._all_interactions.clear()

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "total_interactions": self.total_interactions(),
            "opponents_count": len(self.get_opponents()),
            "recent_history": [
                r.to_dict() for r in self._all_interactions[-10:]
            ],
        }