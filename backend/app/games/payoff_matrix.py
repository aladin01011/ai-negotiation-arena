"""Game theory payoff matrix definitions and computations."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Tuple
import numpy as np


class Action(Enum):
    """Available actions for agents in the Prisoner's Dilemma."""
    COOPERATE = "cooperate"
    DEFECT = "defect"

    def __str__(self) -> str:
        return self.value

    @property
    def is_cooperate(self) -> bool:
        return self == Action.COOPERATE

    @property
    def is_defect(self) -> bool:
        return self == Action.DEFECT


# Standard payoff matrix values (classic PD)
# Mutual cooperation: both get R (Reward)
# Mutual defection: both get P (Punishment)
# Cooperate vs Defect: cooperator gets S (Sucker), defector gets T (Temptation)
# Must satisfy: T > R > P > S and 2R > T + S
R = 3  # Reward for mutual cooperation
S = 0  # Sucker's payoff
T = 5  # Temptation to defect
P = 1  # Punishment for mutual defection


@dataclass(frozen=True)
class PayoffMatrix:
    """
    Immutable payoff matrix for a 2-player, 2-action game.
    
    Format: payoff_matrix[action_a][action_b] -> (payoff_a, payoff_b)
    Index 0 = Cooperate, Index 1 = Defect
    """
    matrix: np.ndarray  # Shape (2, 2, 2)

    @classmethod
    def prisoner_dilemma(cls) -> PayoffMatrix:
        """Classic Prisoner's Dilemma payoff matrix."""
        matrix = np.array([
            [[R, R], [S, T]],  # A cooperates
            [[T, S], [P, P]],  # A defects
        ])
        return cls(matrix=matrix)

    @classmethod
    def chicken(cls) -> PayoffMatrix:
        """Chicken game (Snowdrift). Swerve vs Stay."""
        # Both swerve: (0, 0)
        # One swerves, one stays: (-1, 1) or (1, -1)
        # Both stay: (-10, -10)
        matrix = np.array([
            [[0, 0], [-1, 1]],   # A swerves
            [[1, -1], [-10, -10]],  # A stays
        ])
        return cls(matrix=matrix)

    @classmethod
    def stag_hunt(cls) -> PayoffMatrix:
        """Stag Hunt game. Cooperate for big reward vs safe small reward."""
        matrix = np.array([
            [[4, 4], [0, 3]],   # A hunts stag
            [[3, 0], [2, 2]],   # A hunts hare
        ])
        return cls(matrix=matrix)

    @classmethod
    def custom(cls, r: float, s: float, t: float, p: float) -> PayoffMatrix:
        """Custom PD with given parameters. Must satisfy T > R > P > S."""
        assert t > r > p > s, f"Invalid PD parameters: T={t} > R={r} > P={p} > S={s} violated"
        assert 2 * r > t + s, "2R > T+S violated (iterated game stability condition)"
        matrix = np.array([
            [[r, r], [s, t]],
            [[t, s], [p, p]],
        ])
        return cls(matrix=matrix)

    def payoff(self, action_a: Action, action_b: Action) -> Tuple[float, float]:
        """Get payoff for both agents given their actions."""
        a_idx = 0 if action_a == Action.COOPERATE else 1
        b_idx = 0 if action_b == Action.COOPERATE else 1
        return tuple(self.matrix[a_idx, b_idx].tolist())

    def is_nash_equilibrium(self, action_a: Action, action_b: Action) -> bool:
        """
        Check if the action pair is a pure-strategy Nash equilibrium.
        Neither player can improve by unilaterally changing.
        """
        a_idx = 0 if action_a == Action.COOPERATE else 1
        b_idx = 0 if action_b == Action.COOPERATE else 1

        current_a_payoff = self.matrix[a_idx, b_idx, 0]
        current_b_payoff = self.matrix[a_idx, b_idx, 1]

        # Check if player A can improve by switching
        other_a_idx = 1 - a_idx
        if self.matrix[other_a_idx, b_idx, 0] > current_a_payoff:
            return False

        # Check if player B can improve by switching
        other_b_idx = 1 - b_idx
        if self.matrix[a_idx, other_b_idx, 1] > current_b_payoff:
            return False

        return True

    def find_pure_nash(self) -> list[Tuple[Action, Action]]:
        """Find all pure-strategy Nash equilibria."""
        equilibria = []
        actions = [Action.COOPERATE, Action.DEFECT]
        for a in actions:
            for b in actions:
                if self.is_nash_equilibrium(a, b):
                    equilibria.append((a, b))
        return equilibria

    def __repr__(self) -> str:
        actions = ["C", "D"]
        lines = ["Payoff Matrix (A, B):"]
        lines.append(f"      {actions[0]:>6}  {actions[1]:>6}")
        for i, a_name in enumerate(actions):
            vals = []
            for j in range(2):
                vals.append(f"({self.matrix[i,j,0]}, {self.matrix[i,j,1]})")
            lines.append(f"  {a_name}:  {vals[0]:>10}  {vals[1]:>10}")
        return "\n".join(lines)