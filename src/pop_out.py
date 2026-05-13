import sys
from random import choice

COLOURS = {
    "reset": "\033[m",
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "black_bold": "\033[1;30m",
    "red_bold": "\033[1;31m",
    "green_bold": "\033[1;32m",
    "yellow_bold": "\033[1;33m",
    "blue_bold": "\033[1;34m",
    "magenta_bold": "\033[1;35m",
    "cyan_bold": "\033[1;36m",
    "white_bold": "\033[1;37m",
}

GAME_TITLE = """
██████╗  ██████╗ ██████╗      ██████╗ ██╗   ██╗████████╗██╗
██╔══██╗██╔═══██╗██╔══██╗    ██╔═══██╗██║   ██║╚══██╔══╝██║
██████╔╝██║   ██║██████╔╝    ██║   ██║██║   ██║   ██║   ██║
██╔═══╝ ██║   ██║██╔═══╝     ██║   ██║██║   ██║   ██║   ╚═╝
██║     ╚██████╔╝██║         ╚██████╔╝╚██████╔╝   ██║   ██╗
╚═╝      ╚═════╝ ╚═╝          ╚═════╝  ╚═════╝    ╚═╝   ╚═╝
                                                           """
ROWS = 6
COLS = 7
EMPTY_DOT = f"{COLOURS['white']}●{COLOURS['reset']}"
RED_DOT = f"{COLOURS['red']}●{COLOURS['reset']}"
BLUE_DOT = f"{COLOURS['blue']}●{COLOURS['reset']}"
EMPTY = 0
RED_PLAYER = 1
BLUE_PLAYER = -1
SYMBOLS = {EMPTY: EMPTY_DOT, RED_PLAYER: RED_DOT, BLUE_PLAYER: BLUE_DOT}
WIN_LENGTH = 4


class PopOut:
    """Terminal-playable PopOut game state and rule engine."""

    def __init__(self):
        """Create an empty board and randomly choose the starting player."""
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = choice([-1, 1])
        self.last_player = None

    def print_turn(self):
        """
        Print a colored message showing which player has the current turn.

        The current player is determined by self.turn:
        - RED_PLAYER prints "RED's turn!" in red
        - BLUE_PLAYER prints "BLUE's turn!" in blue
        """

        if self.turn == RED_PLAYER:
            print(f"{COLOURS['red']}RED's turn!{COLOURS['reset']}")
        else:
            print(f"{COLOURS['blue']}BLUE's turn!{COLOURS['reset']}")

    def print_board(self, show_arrow=True):
        """
        Print the current PopOut board to the terminal.

        When show_arrow is True, green arrows are printed as move hints:
        - above columns whose top cell is empty, indicating that a piece can be dropped
        - below columns whose bottom cell belongs to the current player, indicating
            that the player can pop a piece out from that column

        Args:
            show_arrow (bool): Whether to display green arrows for available moves.
        """

        green_arrow = f" {COLOURS['green']}↓{COLOURS['reset']}"

        if show_arrow:
            print(
                "".join(
                    (green_arrow if cell == EMPTY else "  ") for cell in self.board[0]
                )
            )
        for row in self.board:
            print(f"|{'|'.join(SYMBOLS[cell] for cell in row)}|")
        if show_arrow:
            print(
                "".join(
                    (green_arrow if cell == self.turn else "  ")
                    for cell in self.board[-1]
                )
            )

    def get_board_state(self):
        """
        Return the current board as a flat, immutable tuple.

        The board is flattened row by row, from top to bottom and left to right.
        This creates a hashable representation of the board, which is useful for
        storing or looking up game states in dictionaries, sets, or MCTS tables.

        Returns:
            tuple: The current turn and a flattened representation of self.board.
        """
        return (self.turn, tuple(cell for row in self.board for cell in row))

    def clone(self):
        """Return an independent copy of the current game state."""
        new_game = self.__class__.__new__(self.__class__)
        new_game.__dict__ = self.__dict__.copy()
        new_game.board = [row[:] for row in self.board]
        return new_game

    def available_moves(self):
        """Return all legal drop and pop moves for the current player."""
        moves = []
        for column_index in range(COLS):
            move_column = column_index + 1
            if self.board[0][column_index] == EMPTY:
                moves.append((move_column, "d"))
            if self.board[ROWS - 1][column_index] == self.turn:
                moves.append((move_column, "p"))
        return moves

    def apply_move(self, move):
        """Apply a move and advance the turn.

        Returns:
            int: The player who made the move.
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
        """Return whether the game is won or has no legal moves."""
        return self.check_winner() is not None or not self.available_moves()

    def get_ans(self):
        """
        Ask for a yes/no answer and return its first character.

        Returns:
            str: "y" for yes or "n" for no.
        """
        answer = ""
        while answer not in ["y", "n"]:
            answer = str(input("yes[y] or no[n]: ")).lower()
            if answer:
                answer = answer[0]
        return answer

    def is_full_board(self):
        """
        Return whether every board cell is occupied.

        Returns:
            bool: True when no empty cells remain, otherwise False.
        """
        return all(cell != EMPTY for row in self.board for cell in row)

    def print_invalid_move(self, is_board_full: bool):
        """
        Print the invalid-move message appropriate for the board state.

        Args:
            is_board_full (bool): Whether to include the draw option in the message.
        """
        if is_board_full:
            print(
                "Invalid. Type the column index (starts in 1), space, "
                f"drop(d) or pop(p). Or type {COLOURS['green']}draw"
                f"{COLOURS['reset']} to end the game"
            )
        else:
            print(
                "Invalid. Type the column index (starts in 1), space, drop(d) or pop(p)"
            )

    def get_player_input(self, is_board_full: bool):
        """
        Read and validate a move from the current player.

        Accepted move input is a column number followed by "drop" or "pop",
        using only the first letter of the action. When the board is full,
        the player may type "draw" to end the game.

        Args:
            is_board_full (bool): Whether draw input is currently allowed.

        Returns:
            list | str: A valid move as [column, action], or "draw".
        """

        if is_board_full:
            print(
                f"{COLOURS['green']}The board is full. You can end the game "
                f"as a draw.{COLOURS['reset']}"
            )
            print(
                f"Type your move or type {COLOURS['green']}draw"
                f"{COLOURS['reset']} to end the game"
            )
        else:
            print("Type your move: [column] [drop/pop]")
        while True:
            try:
                player_in = str(input())
            except (EOFError, KeyboardInterrupt):
                print(f"\n{COLOURS['red']}Game interrupted by user.{COLOURS['reset']}")
                sys.exit(0)

            if is_board_full and player_in[0:4].lower() == "draw":
                return "draw"
            player_in = player_in.split()

            if len(player_in) < 2:
                self.print_invalid_move(is_board_full)
                continue
            if len(player_in) > 2:
                player_in = [player_in[0], player_in[1]]
            try:
                player_in = [int(player_in[0]), player_in[1][0].lower()]
            except (ValueError, IndexError):
                self.print_invalid_move(is_board_full)
                continue
            if (
                player_in[0] > COLS
                or player_in[0] <= 0
                or player_in[1] not in ["d", "p"]
            ):
                self.print_invalid_move(is_board_full)
                continue
            if self.is_valid(player_in):
                return player_in
            print("Invalid move. Try again.")

    def is_valid(self, move):
        """
        Return whether a parsed move is legal for the current board and player.

        A drop is valid when the chosen column has an empty top cell. A pop is
        valid when the bottom cell in the chosen column belongs to self.turn.

        Args:
            move (list): [column, action], where column is 1-based and action
                is "d" or "p".

        Returns:
            bool: True when the move can be played, otherwise False.
        """
        if move[1] == "d" and self.board[0][move[0] - 1] != EMPTY:
            return False
        if move[1] == "p" and self.board[-1][move[0] - 1] != self.turn:
            return False
        return True

    def make_move(self, move):
        """
        Apply a valid drop or pop move for the current player.

        Drop places self.turn in the lowest empty cell of the chosen column.
        Pop removes the bottom cell of the chosen column and shifts the column
        down, leaving the top cell empty.

        Args:
            move (list): [column, action], where column is 1-based and action
                is "d" or "p".
        """
        column = move[0] - 1
        if move[1] == "d":
            for i in range(ROWS - 1, -1, -1):
                if self.board[i][column] == EMPTY:
                    self.board[i][column] = self.turn
                    return
        for i in range(ROWS - 1, 0, -1):
            self.board[i][column] = self.board[i - 1][column]
        self.board[0][column] = EMPTY

    def is_winning_line(self, row, col, row_step, col_step):
        """
        Return whether four matching pieces start at a cell in one direction.

        Args:
            row (int): Starting row.
            col (int): Starting column.
            row_step (int): Row movement for each next cell.
            col_step (int): Column movement for each next cell.

        Returns:
            bool: True when the four checked cells are non-empty and equal.
        """
        first_cell = self.board[row][col]
        if first_cell == EMPTY:
            return False

        for offset in range(1, WIN_LENGTH):
            next_row = row + offset * row_step
            next_col = col + offset * col_step
            if self.board[next_row][next_col] != first_cell:
                return False
        return True

    def check_horizontal_wins(self):
        """Check for 4-in-a-row horizontally."""
        wins = set()
        for row in range(ROWS):
            for col in range(COLS - 3):
                if self.is_winning_line(row, col, 0, 1):
                    wins.add(self.board[row][col])
        return wins

    def check_vertical_wins(self):
        """Check for 4-in-a-row vertically."""
        wins = set()
        for row in range(ROWS - 3):
            for col in range(COLS):
                if self.is_winning_line(row, col, 1, 0):
                    wins.add(self.board[row][col])
        return wins

    def check_diagonal_wins_backslash(self):
        """Check for 4-in-a-row diagonally (\\)."""
        wins = set()
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                if self.is_winning_line(row, col, 1, 1):
                    wins.add(self.board[row][col])
        return wins

    def check_diagonal_wins_slash(self):
        """Check for 4-in-a-row diagonally (/)."""
        wins = set()
        for row in range(ROWS - 3):
            for col in range(3, COLS):
                if self.is_winning_line(row, col, 1, -1):
                    wins.add(self.board[row][col])
        return wins

    def check_winner(self):
        """Return the winner, or ``None`` when there is no winner.

        If one move creates winning lines for both players, PopOut awards the
        win to the player who just moved.
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

    def print_winner(self, player):
        """
        Print the winning player message.

        Args:
            player (int): RED_PLAYER or BLUE_PLAYER.
        """
        if player == BLUE_PLAYER:
            print(f"{COLOURS['blue']}BLUE WINS!{COLOURS['reset']}")
        else:
            print(f"{COLOURS['red']}RED WINS!{COLOURS['reset']}")

    def run(self):
        """
        Run the interactive PopOut game loop until win, draw, or interruption.

        The loop prints the board, tracks repeated states for draw offers,
        reads player moves, applies valid moves, checks for winners, and
        alternates turns.
        """
        state_history = {}
        while True:
            self.print_turn()
            self.print_board()

            current_state = self.get_board_state()
            state_history[current_state] = state_history.get(current_state, 0) + 1
            if state_history[current_state] == 3:
                print(
                    f"{COLOURS['green']}This board has been repeated 3 times. "
                    "Does any player wish to end the game as a draw?"
                    f"{COLOURS['reset']}"
                )
                ans = self.get_ans()
                if ans == "y":
                    self.print_board(show_arrow=False)
                    print(f"{COLOURS['green']}Game ended as a draw.{COLOURS['reset']}")
                    break
                self.print_turn()

            player_input = self.get_player_input(self.is_full_board())
            if player_input == "draw":
                self.print_board(show_arrow=False)
                print(f"{COLOURS['green']}Game ended as a draw.{COLOURS['reset']}")
                break

            self.apply_move(player_input)
            winner = self.check_winner()
            if winner is not None:
                self.print_board(show_arrow=False)
                self.print_winner(winner)
                break


if __name__ == "__main__":
    game = PopOut()
    game.run()
