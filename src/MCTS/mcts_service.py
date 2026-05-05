"""Generic Monte Carlo Tree Search implementation.

This module is game-agnostic: it does not know the rules of TicTacToe,
PopOut, or any other game. The game object passed to ``MCTS.search`` must
implement a small contract:

- ``clone()``
- ``available_moves()``
- ``play_move(player, move)``
- ``next_player(player)``
- ``is_terminal()``
- ``check_winner()``

See ``src/MCTS/README.md`` for the full contract and usage examples.
"""

import math
import random


DEFAULT_EXPLORATION_WEIGHT = math.sqrt(2)
DRAW_SCORE = 0.5


class Node:
    """One state in the MCTS search tree."""

    def __init__(self, state, player_to_move, parent=None, move=None):
        """Create a tree node.

        Args:
            state: Game state represented by the external game object.
            player_to_move: Player who must play from this state.
            parent: Parent ``Node`` in the tree, or ``None`` for the root.
            move: Move that produced this state from the parent.
        """
        self.state = state
        self.player_to_move = player_to_move
        self.parent = parent
        self.move = move
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
        """Create one child by applying one untried move."""
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)

        next_state = self.state.clone()
        next_state.play_move(self.player_to_move, move)
        next_player = next_state.next_player(self.player_to_move)

        child = Node(next_state, next_player, parent=self, move=move)
        self.children.append(child)
        return child

    def best_child(self, exploration_weight=DEFAULT_EXPLORATION_WEIGHT):
        """Select the child with the highest UCT score.

        ``child.wins`` is stored from the perspective of the player who made
        the move into that child. This is important because selection must
        behave adversarially: opponent nodes should favor opponent wins.
        """
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
        """Return the root child that should be used as the final move.

        MCTS usually selects the final move by highest visit count, because it
        is more stable than selecting by win rate after noisy random rollouts.
        """
        return max(self.children, key=lambda child: child.visits)

    def player_that_moved_here(self):
        """Return the player who made ``self.move`` to reach this node."""
        if self.parent is None:
            return None
        return self.parent.player_to_move


class MCTS:
    """Monte Carlo Tree Search player.

    Args:
        iterations: Number of selection/expansion/simulation/backpropagation
            cycles to run per move. Higher values usually improve play quality
            but take more time.
    """

    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, game, player):
        """Return the best move found for ``player`` in ``game``.

        Args:
            game: Current game state implementing the MCTS game contract.
            player: Player who must play now.

        Returns:
            A move object from ``game.available_moves()``, or ``None`` if the
            game is already terminal or has no legal moves.
        """
        root = Node(game.clone(), player)

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
        """Play random moves from ``node`` until the game ends."""
        rollout_state = node.state.clone()
        current_player = node.player_to_move

        while not rollout_state.is_terminal():
            move = random.choice(rollout_state.available_moves())
            rollout_state.play_move(current_player, move)
            current_player = rollout_state.next_player(current_player)

        return rollout_state.check_winner()

    def _backpropagate(self, node, winner):
        """Update visit and win statistics from ``node`` back to the root."""
        current = node

        while current is not None:
            current.visits += 1
            player_that_moved = current.player_that_moved_here()

            if winner == player_that_moved:
                current.wins += 1
            elif winner is None:
                current.wins += DRAW_SCORE

            current = current.parent
