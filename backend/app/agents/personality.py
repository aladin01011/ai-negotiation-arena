"""Agent personality traits that modulate decision-making."""

from __future__ import annotations
from dataclasses import dataclass, field
import random


@dataclass
class Personality:
    """
    Personality traits that influence agent behavior.
    
    Each trait is a float in [0.0, 1.0] range.
    """
    # Trust: willingness to cooperate initially (0=paranoid, 1=trusting)
    trust: float = 0.5

    # Greed: how much the agent values immediate gain (0=selfless, 1=greedy)
    greed: float = 0.5

    # Risk tolerance: willingness to risk defection for higher reward
    # (0=risk-averse, 1=risk-seeking)
    risk_tolerance: float = 0.5

    # Forgiveness: how quickly an agent forgives defection
    # (0=grudges forever, 1=forgives immediately)
    forgiveness: float = 0.5

    # Reciprocity: tendency to mirror opponent behavior
    # (0=independent, 1=strongly mirrors)
    reciprocity: float = 0.7

    # Spite: willingness to sacrifice own payoff to punish defectors
    # (0=never spiteful, 1=highly spiteful)
    spite: float = 0.3

    def __post_init__(self):
        """Clamp all values to [0, 1]."""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            setattr(self, field_name, max(0.0, min(1.0, value)))

    @classmethod
    def random(cls, seed: Optional[int] = None) -> Personality:
        """Generate a random personality."""
        rng = random.Random(seed)
        return cls(
            trust=rng.random(),
            greed=rng.random(),
            risk_tolerance=rng.random(),
            forgiveness=rng.random(),
            reciprocity=rng.random(),
            spite=rng.random(),
        )

    @classmethod
    def cooperative(cls) -> Personality:
        """A naturally cooperative personality."""
        return cls(trust=0.8, greed=0.2, risk_tolerance=0.3,
                   forgiveness=0.7, reciprocity=0.8, spite=0.1)

    @classmethod
    def competitive(cls) -> Personality:
        """A naturally competitive/defecting personality."""
        return cls(trust=0.2, greed=0.8, risk_tolerance=0.7,
                   forgiveness=0.2, reciprocity=0.3, spite=0.7)

    @classmethod
    def strategic(cls) -> Personality:
        """A balanced, adaptive personality."""
        return cls(trust=0.5, greed=0.5, risk_tolerance=0.4,
                   forgiveness=0.5, reciprocity=0.7, spite=0.3)

    def to_dict(self) -> dict:
        return {
            "trust": round(self.trust, 2),
            "greed": round(self.greed, 2),
            "risk_tolerance": round(self.risk_tolerance, 2),
            "forgiveness": round(self.forgiveness, 2),
            "reciprocity": round(self.reciprocity, 2),
            "spite": round(self.spite, 2),
        }

    def to_label(self) -> str:
        """Return a human-readable personality label."""
        if self.trust > 0.7 and self.greed < 0.3:
            return "Cooperative"
        elif self.trust < 0.3 and self.greed > 0.7:
            return "Competitive"
        elif self.forgiveness < 0.3:
            return "Grudger"
        elif self.reciprocity > 0.8:
            return "Mirror"
        else:
            return "Balanced"