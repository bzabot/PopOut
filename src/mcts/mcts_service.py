"""Generic Monte Carlo Tree Search implementation.

This module is game-agnostic: it does not know the rules of TicTacToe,
PopOut, or any other game. The game object passed to ``MCTS.search`` must
implement a small contract:

- ``clone()``
- ``available_moves()``
- ``apply_move(move)``
- ``is_terminal()``
- ``check_winner()``
Optional:
- ``get_board_state()`` for repetition detection during rollouts

See ``src/MCTS/README.md`` for the full contract and usage examples.
"""

import math
import random

DEFAULT_EXPLORATION_WEIGHT = math.sqrt(2)
DRAW_SCORE = 0.5
DEFAULT_ROLLOUT_LIMIT = 500
TACTICAL_ROLLOUT_DEPTH = 8
REPETITIONS_TO_DRAW = 3
DRAW_MOVE = "draw"
DEFAULT_HEURISTIC_WEIGHT = 0.25


class Node:
    """One state in the MCTS search tree."""

    def __init__(
        self,
        state,
        parent=None,
        move=None,
        player_that_moved=None,
        prior_scorer=None,
    ):
        """Create a tree node.

        Args:
            state: Game state represented by the external game object.
            parent: Parent ``Node`` in the tree, or ``None`` for the root.
            move: Move that produced this state from the parent.
            player_that_moved: Player who made ``move`` to reach this state.
        """
        self.state = state
        self.parent = parent
        self.move = move
        self.player_that_moved = player_that_moved
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.prior_score = 0.0
        self.prior_scorer = prior_scorer
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
        player_that_moved = next_state.apply_move(move)

        child = Node(
            next_state,
            parent=self,
            move=move,
            player_that_moved=player_that_moved,
            prior_scorer=self.prior_scorer,
        )
        child.prior_score = self._move_prior(move)
        self.children.append(child)
        return child

    def _move_prior(self, move):
        """Return a neutral prior by default.

        ``MCTS`` passes a scorer so every created child receives a heuristic
        prior derived from its parent's state.
        """
        if self.prior_scorer is None:
            return 0.0
        return self.prior_scorer(self.state, move)

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
            heuristic_bias = DEFAULT_HEURISTIC_WEIGHT * child.prior_score
            score = exploitation + exploration + heuristic_bias

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


class MCTS:
    """Monte Carlo Tree Search player.

    Args:
        iterations: Number of selection/expansion/simulation/backpropagation
            cycles to run per move. Higher values usually improve play quality
            but take more time.
    """

    def __init__(self, iterations=1000, rollout_limit=DEFAULT_ROLLOUT_LIMIT):
        self.iterations = iterations
        self.rollout_limit = rollout_limit
        self._winning_moves_cache = {}

    def search(self, game):
        """Return the best move found for the current player in ``game``.

        Args:
            game: Current game state implementing the MCTS game contract.

        Returns:
            A move object from ``game.available_moves()``, or ``None`` if the
            game is already terminal or has no legal moves.
        """
        self._winning_moves_cache = {}

        winning_moves = self._immediate_winning_moves(game)
        if winning_moves:
            return self._weighted_center_choice(game, winning_moves)

        root = Node(game.clone(), prior_scorer=self._score_move_prior)

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
        """Play moves from ``node`` until a win or draw."""
        rollout_state = node.state.clone()
        state_history = {}
        depth = 0

        while not rollout_state.is_terminal():
            if self._is_repeated_draw(state_history, rollout_state):
                return None
            if depth >= self.rollout_limit:
                return None

            move = self._choose_rollout_move(
                rollout_state,
                use_tactics=depth < TACTICAL_ROLLOUT_DEPTH,
            )
            rollout_state.apply_move(move)
            depth += 1

        return rollout_state.check_winner()

    def _score_move_prior(self, state, move):
        """Return a normalized heuristic prior used as a UCT bias."""
        # Central columns participate in more horizontal and diagonal four-in-a-row
        # lines, so they get a small positional prior before tactical checks.
        score = self._normalized_center_score(state, move) * 0.15

        if self._move_wins(state, move):
            # A forced win should dominate the prior, but the final score is still
            # clamped so it remains only a bias term inside UCT.
            score += 1.0
        if self._blocks_immediate_win(state, move):
            # Blocking an immediate loss is almost as urgent as winning now.
            score += 0.7
        if self._opponent_can_win_after(state, move):
            # Moves that allow a direct winning reply are tactically dangerous.
            score -= 1.0

        return max(-1.0, min(1.0, score))

    def _choose_rollout_move(self, state, use_tactics=True):
        """Choose a rollout move using cheap one-ply PopOut tactics."""
        moves = state.available_moves()
        if not use_tactics:
            return self._weighted_center_choice(state, moves)

        winning_moves = self._immediate_winning_moves(state)
        if winning_moves:
            return self._weighted_center_choice(state, winning_moves)

        opponent = self._opponent_of_current_player(state)
        if opponent is not None and self._player_has_immediate_win(state, opponent):
            blocking_moves = [
                move for move in moves if not self._opponent_can_win_after(state, move)
            ]
            if blocking_moves:
                return self._weighted_center_choice(state, blocking_moves)

        return self._weighted_center_choice(state, moves)

    def _move_wins(self, state, move):
        """Return whether ``move`` immediately wins for the player moving."""
        return move in self._immediate_winning_moves(state)

    def _blocks_immediate_win(self, state, move):
        """Return whether ``move`` removes all immediate opponent wins."""
        opponent = self._opponent_of_current_player(state)
        if opponent is None:
            return False

        if not self._player_has_immediate_win(state, opponent):
            return False

        next_state = state.clone()
        next_state.apply_move(move)
        if next_state.is_terminal():
            return False

        return not self._player_has_immediate_win(next_state, opponent)

    def _opponent_can_win_after(self, state, move):
        """Return whether the opponent has an immediate winning reply."""
        if move == DRAW_MOVE:
            return False

        next_state = state.clone()
        next_state.apply_move(move)
        if next_state.is_terminal():
            return False

        opponent = getattr(next_state, "turn", None)
        if opponent is None:
            return False

        return bool(self._immediate_winning_moves(next_state, opponent))

    def _player_has_immediate_win(self, state, player):
        """Return whether ``player`` has a one-move win in ``state``."""
        return bool(self._immediate_winning_moves(state, player))

    def _immediate_winning_moves(self, state, player=None):
        """Return moves that immediately win for ``player`` or state.turn."""
        test_state = state
        if player is not None:
            if not hasattr(state, "turn"):
                return ()
            test_state = state.clone()
            test_state.turn = player

        cache_key = self._state_cache_key(test_state)
        if cache_key is not None and cache_key in self._winning_moves_cache:
            return self._winning_moves_cache[cache_key]

        winning_moves = []
        for move in test_state.available_moves():
            if move == DRAW_MOVE:
                continue

            next_state = test_state.clone()
            player_that_moved = next_state.apply_move(move)
            if next_state.check_winner() == player_that_moved:
                winning_moves.append(move)

        winning_moves = tuple(winning_moves)
        if cache_key is not None:
            self._winning_moves_cache[cache_key] = winning_moves
        return winning_moves

    def _state_cache_key(self, state):
        """Return a hashable key for rollout tactical caches when available."""
        if not hasattr(state, "get_board_state"):
            return None
        return state.get_board_state()

    def _opponent_of_current_player(self, state):
        """Return the opponent of ``state.turn`` when the game exposes it."""
        player = getattr(state, "turn", None)
        if player is None:
            return None
        if hasattr(state, "next_player"):
            return state.next_player(player)
        try:
            return -player
        except TypeError:
            return None

    def _weighted_center_choice(self, state, moves):
        """Choose randomly, biased toward moves in central columns."""
        weighted_moves = []
        for move in moves:
            weight = max(1, self._center_score(state, move))
            weighted_moves.extend([move] * weight)
        return random.choice(weighted_moves)

    def _center_score(self, state, move):
        """Return a small preference for central board columns."""
        column = self._move_column(move)
        board = getattr(state, "board", None)
        if column is None or not board or not board[0]:
            return 1

        column_count = len(board[0])
        center = (column_count + 1) / 2
        distance = abs(column - center)
        return int((column_count + 1) - (2 * distance))

    def _normalized_center_score(self, state, move):
        """Return center preference normalized to the interval [0, 1]."""
        board = getattr(state, "board", None)
        if not board or not board[0]:
            return 0.0

        return self._center_score(state, move) / len(board[0])

    def _move_column(self, move):
        """Return a 1-based column from tuple/list PopOut-style moves."""
        if not isinstance(move, (list, tuple)) or not move:
            return None
        column = move[0]
        if isinstance(column, int):
            return column
        return None

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
