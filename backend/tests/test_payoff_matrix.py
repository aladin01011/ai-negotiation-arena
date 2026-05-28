"""Tests for the payoff matrix module."""

import pytest
import numpy as np
from app.games.payoff_matrix import PayoffMatrix, Action, R, S, T, P


class TestPayoffMatrix:
    """Test suite for the PayoffMatrix class."""

    def test_prisoner_dilemma_creation(self):
        """PD payoff matrix should have correct structure."""
        matrix = PayoffMatrix.prisoner_dilemma()
        assert matrix.matrix.shape == (2, 2, 2)
        
        # Verify standard PD inequalities
        cc_payoff = matrix.matrix[0, 0]  # (R, R)
        cd_payoff = matrix.matrix[0, 1]  # (S, T)
        dc_payoff = matrix.matrix[1, 0]  # (T, S)
        dd_payoff = matrix.matrix[1, 1]  # (P, P)
        
        assert cc_payoff[0] == R  # Both cooperate
        assert cd_payoff[0] == S  # Sucker
        assert cd_payoff[1] == T  # Temptation
        assert dc_payoff[0] == T  # Temptation
        assert dc_payoff[1] == S  # Sucker
        assert dd_payoff[0] == P  # Both defect

    def test_payoff_method(self):
        """payoff() should return correct values for each action pair."""
        matrix = PayoffMatrix.prisoner_dilemma()
        
        # (C, C) -> (R, R)
        assert matrix.payoff(Action.COOPERATE, Action.COOPERATE) == (R, R)
        
        # (C, D) -> (S, T)
        assert matrix.payoff(Action.COOPERATE, Action.DEFECT) == (S, T)
        
        # (D, C) -> (T, S)
        assert matrix.payoff(Action.DEFECT, Action.COOPERATE) == (T, S)
        
        # (D, D) -> (P, P)
        assert matrix.payoff(Action.DEFECT, Action.DEFECT) == (P, P)

    def test_nash_equilibrium_pd(self):
        """In PD, (D, D) should be the unique Nash equilibrium."""
        matrix = PayoffMatrix.prisoner_dilemma()
        
        assert not matrix.is_nash_equilibrium(Action.COOPERATE, Action.COOPERATE)
        assert not matrix.is_nash_equilibrium(Action.COOPERATE, Action.DEFECT)
        assert not matrix.is_nash_equilibrium(Action.DEFECT, Action.COOPERATE)
        assert matrix.is_nash_equilibrium(Action.DEFECT, Action.DEFECT)
        
        equilibria = matrix.find_pure_nash()
        assert len(equilibria) == 1
        assert equilibria[0] == (Action.DEFECT, Action.DEFECT)

    def test_custom_matrix_validation(self):
        """Custom matrices should enforce T > R > P > S."""
        # Valid custom matrix
        matrix = PayoffMatrix.custom(r=4, s=1, t=6, p=2)
        assert matrix.payoff(Action.COOPERATE, Action.COOPERATE) == (4, 4)
        
        # Invalid: T < R
        with pytest.raises(AssertionError):
            PayoffMatrix.custom(r=5, s=1, t=3, p=2)
        
        # Invalid: 2R <= T + S
        with pytest.raises(AssertionError):
            PayoffMatrix.custom(r=4, s=3, t=5, p=2)

    def test_chicken_game(self):
        """Chicken game should have two Nash equilibria."""
        matrix = PayoffMatrix.chicken()
        equilibria = matrix.find_pure_nash()
        # Chicken has two pure NE: (Swerve, Stay) and (Stay, Swerve)
        assert len(equilibria) == 2

    def test_stag_hunt(self):
        """Stag hunt should have two Nash equilibria."""
        matrix = PayoffMatrix.stag_hunt()
        equilibria = matrix.find_pure_nash()
        # Stag hunt has two pure NE: (Stag, Stag) and (Hare, Hare)
        assert len(equilibria) == 2