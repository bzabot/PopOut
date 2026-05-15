"""Baseline Monte Carlo Tree Search implementation for benchmarks.

This module intentionally removes the improvements present in
``mcts_service.py``:

- no heuristic prior in UCT selection
- no tactical rollout for immediate wins or blocks
- no center-column rollout bias

It keeps the same public interface as the improved implementation, so benchmark
code can compare both versions by changing only the import:

```
from src.mcts.mcts_service import MCTS        # improved MCTS
from src.mcts.mcts_service_mock import MCTS   # baseline MCTS
```
"""

import math
import random

DEFAULT_EXPLORATION_WEIGHT = math.sqrt(2)
DRAW_SCORE = 0.5
DEFAULT_ROLLOUT_LIMIT = 500
REPETITIONS_TO_DRAW = 3


class Node:
    """One state in the baseline MCTS search tree."""

    def __init__(self, state, parent=None, move=None, player_that_moved=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.player_that_moved = player_that_moved
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = state.available_moves()

    def is_terminal(self):
        """Return whether this node represents a finished game state."""
        return self.state.is_terminal()

    def is_fully_expanded(self):
        """Return whether every legal move from this state has a child node."""
        return not self.untried_moves

    def expand(self):
        """Create one child by applying one random untried move."""
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)

        next_state = self.state.clone()
        player_that_moved = next_state.apply_move(move)

        child = Node(
            next_state,
            parent=self,
            move=move,
            player_that_moved=player_that_moved,
        )
        self.children.append(child)
        return child

    def best_child(self, exploration_weight=DEFAULT_EXPLORATION_WEIGHT):
        """Select the child with the highest plain UCT score."""
        best_score = float("-inf")
        best_node = None

        for child in self.children:
            exploitation = child.wins / child.visits
            exploration = exploration_weight * math.sqrt(
                math.log(self.visits) / child.visits
            )
            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_node = child

        return best_node

    def best_move_child(self):
        """Return the root child selected as the final move."""
        return max(self.children, key=lambda child: child.visits)


class MCTS:
    """Plain MCTS player used as a baseline for quality/time comparisons.

    Args:
        iterations: Number of MCTS iterations to run per move.
        rollout_limit: Maximum simulated moves before treating the rollout as a
            draw. This protects benchmarks from very long games.
    """

    def __init__(self, iterations=1000, rollout_limit=DEFAULT_ROLLOUT_LIMIT):
        self.iterations = iterations
        self.rollout_limit = rollout_limit

    def search(self, game):
        """Return the best move found for the current player in ``game``."""
        root = Node(game.clone())

        for _ in range(self.iterations):
            node = self._select(root)
            result = self._simulate(node)
            self._backpropagate(node, result)

        if not root.children:
            return None

        return root.best_move_child().move

    def _select(self, node):
        """Walk down the tree until reaching a node to simulate from."""
        current = node

        while not current.is_terminal():
            if not current.is_fully_expanded():
                return current.expand()
            current = current.best_child()

        return current

    def _simulate(self, node):
        """Play uniformly random moves from ``node`` until a win or draw."""
        rollout_state = node.state.clone()
        state_history = {}
        depth = 0

        while not rollout_state.is_terminal():
            if self._is_repeated_draw(state_history, rollout_state):
                return None
            if depth >= self.rollout_limit:
                return None

            moves = rollout_state.available_moves()
            if not moves:
                return None

            rollout_state.apply_move(random.choice(moves))
            depth += 1

        return rollout_state.check_winner()

    def _is_repeated_draw(self, state_history, game):
        """Return whether ``game`` reached a threefold repeated state."""
        if not hasattr(game, "get_board_state"):
            return False

        state = game.get_board_state()
        state_history[state] = state_history.get(state, 0) + 1
        return state_history[state] >= REPETITIONS_TO_DRAW

    def _backpropagate(self, node, winner):
        """Update visit and win statistics from ``node`` back to the root."""
        current = node

        while current is not None:
            current.visits += 1
            player_that_moved = current.player_that_moved

            if winner == player_that_moved:
                current.wins += 1
            elif winner is None:
                current.wins += DRAW_SCORE

            current = current.parent
