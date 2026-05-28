"""Evolutionary algorithm for strategy optimization.

This module enables strategies to evolve over generations using
genetic algorithms. Placeholder for Phase 2 expansion."""

from __future__ import annotations

from typing import List, Tuple
import random


class GeneticOptimizer:
    """
    Evolves agent strategy parameters across generations.
    
    Used after the initial tournament to find optimal strategies
    through selection, crossover, and mutation.
    """

    def __init__(self, population_size: int = 50, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate

    def select(
        self, population: List[dict], fitness_scores: List[float], top_k: int = 10
    ) -> List[dict]:
        """Tournament selection — pick the best agents to reproduce."""
        sorted_pop = [
            p for _, p in sorted(
                zip(fitness_scores, population), key=lambda x: -x[0]
            )
        ]
        return sorted_pop[:top_k]

    def crossover(self, parent_a: dict, parent_b: dict) -> dict:
        """Combine two parent strategies to create offspring."""
        child = {}
        for key in parent_a:
            if isinstance(parent_a[key], (int, float)):
                # Blend crossover for numeric traits
                alpha = random.random()
                child[key] = alpha * parent_a[key] + (1 - alpha) * parent_b[key]
            else:
                # Random choice for categorical traits
                child[key] = random.choice([parent_a[key], parent_b[key]])
        return child

    def mutate(self, individual: dict) -> dict:
        """Randomly mutate traits with configured probability."""
        mutated = individual.copy()
        for key, value in mutated.items():
            if isinstance(value, (int, float)) and random.random() < self.mutation_rate:
                mutated[key] = value + random.uniform(-0.2, 0.2)
                if isinstance(value, float):
                    mutated[key] = max(0.0, min(1.0, mutated[key]))
        return mutated