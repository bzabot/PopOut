"""Parallel Monte Carlo Tree Search implementation.

This version keeps the same search behavior as ``mcts_service.MCTS`` but runs
several independent root searches in separate processes. Each worker builds its
own tree from the same starting position, then the parent process aggregates the
root-child visit counts and chooses the most visited move.
"""

import os
import random
from concurrent.futures import ProcessPoolExecutor

from .mcts_service import DEFAULT_ROLLOUT_LIMIT, MCTS, Node


def _run_root_search(game, iterations, rollout_limit, seed):
    """Run one independent MCTS search and return root-child statistics."""
    random.seed(seed)
    mcts = MCTS(iterations=iterations, rollout_limit=rollout_limit)
    root = Node(game.clone(), prior_scorer=mcts._score_move_prior)

    for _ in range(iterations):
        node = mcts._select(root)
        result = mcts._simulate(node)
        mcts._backpropagate(node, result)

    return [(child.move, child.visits, child.wins) for child in root.children]


class ParallelMCTS:
    """MCTS player that parallelizes independent searches at the root.

    Args:
        iterations: Total MCTS iterations across all workers.
        rollout_limit: Maximum rollout depth per simulation.
        workers: Number of worker processes. Defaults to the available CPUs.
    """

    def __init__(
        self,
        iterations=1000,
        rollout_limit=DEFAULT_ROLLOUT_LIMIT,
        workers=None,
    ):
        self.iterations = iterations
        self.rollout_limit = rollout_limit
        self.workers = workers or os.cpu_count() or 1

    def search(self, game):
        """Return the best move found for the current player in ``game``."""
        if game.is_terminal() or not game.available_moves():
            return None

        worker_count = min(self.workers, self.iterations)
        if worker_count <= 1:
            return MCTS(self.iterations, self.rollout_limit).search(game)

        chunks = self._iteration_chunks(worker_count)
        seeds = [random.randrange(2**32) for _ in chunks]

        move_stats = {}
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            futures = [
                executor.submit(
                    _run_root_search,
                    game,
                    iterations,
                    self.rollout_limit,
                    seed,
                )
                for iterations, seed in zip(chunks, seeds)
            ]

            for future in futures:
                for move, visits, wins in future.result():
                    total_visits, total_wins = move_stats.get(move, (0, 0.0))
                    move_stats[move] = (total_visits + visits, total_wins + wins)

        if not move_stats:
            return None

        return max(move_stats.items(), key=lambda item: item[1][0])[0]

    def _iteration_chunks(self, worker_count):
        """Split total iterations as evenly as possible across workers."""
        base_iterations = self.iterations // worker_count
        extra_iterations = self.iterations % worker_count

        return [
            base_iterations + (1 if worker_index < extra_iterations else 0)
            for worker_index in range(worker_count)
        ]
