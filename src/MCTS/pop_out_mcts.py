"""PopOut integration for the generic Monte Carlo Tree Search service.

The base :class:`src.pop_out.PopOut` class owns the board rules and terminal UI.
``PopOutMCTS`` adds the small state-management contract required by
``mcts_service.MCTS``: clone the state, list legal moves for the current player,
apply a move while advancing the turn, and report terminal winners as ``None``
for draws.
"""

from ..pop_out import COLS, EMPTY, RED_PLAYER, ROWS, PopOut
from .mcts_service import MCTS


class PopOutMCTS(PopOut):
    """PopOut game adapter for the MCTS service contract."""

    def __init__(self):
        """Create an empty PopOut game state for MCTS play."""
        super().__init__()
        self.last_player = None

    def clone(self):
        """Return an independent copy of the current game state.

        MCTS mutates cloned states during expansion and rollout, so the board
        rows must be copied rather than shared with the live game.
        """
        new_game = PopOutMCTS()
        new_game.board = [row[:] for row in self.board]
        new_game.turn = self.turn
        new_game.last_player = self.last_player
        return new_game

    def available_moves(self):
        """Return all legal drop and pop moves for ``self.turn``.

        Moves use the same format accepted by ``PopOut.make_move``:
        ``(column, action)``, where ``column`` is 1-based and ``action`` is
        ``"d"`` for drop or ``"p"`` for pop.
        """
        moves = []
        for column_index in range(COLS):
            move_column = column_index + 1
            if self.board[0][column_index] == EMPTY:
                moves.append((move_column, "d"))
            if self.board[ROWS - 1][column_index] == self.turn:
                moves.append((move_column, "p"))
        return moves

    def apply_move(self, move):
        """Apply ``move`` for the current player and advance the turn.

        Returns:
            int: The player who made the move, used by MCTS backpropagation.
        """
        player_that_moved = self.turn
        self.make_move(move)
        self.last_player = player_that_moved
        self.turn = self.next_player(player_that_moved)
        return player_that_moved

    def next_player(self, player):
        """Return the opponent of ``player``."""
        return -player

    def is_terminal(self):
        """Return whether the state is won or has no legal continuation."""
        return self.check_winner() is not None or not self.available_moves()

    def check_winner(self):
        """Return the PopOut winner, or ``None`` when there is no winner.

        If a move creates winning lines for both players, PopOut awards the win
        to the player who just moved.
        """
        wins = set()
        wins.update(self.check_horizontal_wins())
        wins.update(self.check_vertical_wins())
        wins.update(self.check_diagonal_wins_backslash())
        wins.update(self.check_diagonal_wins_slash())

        if len(wins) == 0:
            return None
        if len(wins) == 2:
            return self.last_player
        return wins.pop()

    def game_loop(self, human_player=RED_PLAYER, mcts_iterations=1500):
        """Run an interactive human-vs-MCTS PopOut game in the terminal.

        Args:
            human_player (int): The player controlled through terminal input.
            mcts_iterations (int): Search iterations used for each MCTS move.
        """
        mcts = MCTS(iterations=mcts_iterations)

        while not self.is_terminal():
            self.print_board()

            if self.turn == human_player:
                move = self.get_player_input(self.is_full_board())
                self.apply_move(move)
            else:
                print("MCTS is thinking...")
                move = mcts.search(self)

                if move is None:
                    break

                self.apply_move(move)
                print(f"MCTS played: {move}")
            self.print_board(show_arrow=False)

            if self.is_terminal():
                winner = self.check_winner()
                if winner is None:
                    print("Draw")
                else:
                    self.print_winner(winner)


if __name__ == "__main__":
    game = PopOutMCTS()
    game.game_loop()
