"""Game factory — creates game instances by type."""

from __future__ import annotations
from typing import Optional

from .payoff_matrix import PayoffMatrix
from .prisoner_dilemma import PrisonerDilemma


class GameFactory:
    """Creates game instances based on game type configuration."""

    GAME_TYPES = {
        "prisoner_dilemma": PrisonerDilemma,
    }

    @classmethod
    def create(cls, game_type: str, **kwargs) -> PrisonerDilemma:
        """Create a game instance by type name."""
        game_class = cls.GAME_TYPES.get(game_type)
        if not game_class:
            raise ValueError(
                f"Unknown game type: {game_type}. "
                f"Available: {list(cls.GAME_TYPES.keys())}"
            )
        return game_class(**kwargs)