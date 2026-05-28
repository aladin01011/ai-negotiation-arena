"""Matchmaking system — pairs agents for competition."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Set
import itertools
import random

from ..agents.base_agent import Agent


class MatchType(Enum):
    """Available matchmaking algorithms."""
    ROUND_ROBIN = "round_robin"       # Every agent plays every other agent
    RANDOM_PAIRS = "random_pairs"      # Random pairings each round
    SWISS = "swiss"                    # Similar scores play each other
    ELIMINATION = "elimination"        # Losers are eliminated


@dataclass
class Match:
    """A pairing of two agents for a game."""
    agent_a: Agent
    agent_b: Agent
    game_type: str = "prisoner_dilemma"

    def to_dict(self) -> dict:
        return {
            "agent_a_id": self.agent_a.agent_id,
            "agent_b_id": self.agent_b.agent_id,
            "agent_a_name": self.agent_a.name,
            "agent_b_name": self.agent_b.name,
            "game_type": self.game_type,
        }


class Matchmaker:
    """
    Responsible for pairing agents for each round of the simulation.
    
    Supports multiple matchmaking algorithms suitable for different
    experimental setups.
    """

    def __init__(self, match_type: MatchType = MatchType.ROUND_ROBIN):
        self.match_type = match_type
        self._round_number = 0

    def pair(self, agents: List[Agent]) -> List[Match]:
        """
        Generate matches for a round based on the configured match type.
        
        Args:
            agents: List of active agents to pair
            
        Returns:
            List of Match objects
        """
        self._round_number += 1
        
        if self.match_type == MatchType.ROUND_ROBIN:
            return self._round_robin(agents)
        elif self.match_type == MatchType.RANDOM_PAIRS:
            return self._random_pairs(agents)
        elif self.match_type == MatchType.SWISS:
            return self._swiss(agents)
        elif self.match_type == MatchType.ELIMINATION:
            return self._elimination(agents)
        else:
            raise ValueError(f"Unknown match type: {self.match_type}")

    def _round_robin(self, agents: List[Agent]) -> List[Match]:
        """
        Every agent plays every other agent exactly once per round.
        This is the gold standard for tournaments.
        """
        matches = []
        for a, b in itertools.combinations(agents, 2):
            matches.append(Match(agent_a=a, agent_b=b))
        return matches

    def _random_pairs(self, agents: List[Agent]) -> List[Match]:
        """
        Agents are randomly paired each round.
        If odd number, one agent sits out.
        """
        shuffled = agents.copy()
        random.shuffle(shuffled)
        
        matches = []
        for i in range(0, len(shuffled) - 1, 2):
            matches.append(Match(agent_a=shuffled[i], agent_b=shuffled[i + 1]))
        
        return matches

    def _swiss(self, agents: List[Agent]) -> List[Match]:
        """
        Swiss-system: agents with similar scores play each other.
        Used in real chess tournaments.
        """
        sorted_agents = sorted(agents, key=lambda a: a.total_score, reverse=True)
        
        matches = []
        for i in range(0, len(sorted_agents) - 1, 2):
            matches.append(Match(agent_a=sorted_agents[i], agent_b=sorted_agents[i + 1]))
        
        return matches

    def _elimination(self, agents: List[Agent]) -> List[Match]:
        """Simple elimination: randomly pair, losers are eliminated."""
        return self._random_pairs(agents)

    @property
    def round_number(self) -> int:
        return self._round_number