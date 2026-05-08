try:
    from .mcts_service import MCTS
except ImportError:
    from mcts_service import MCTS


BOARD_SIZE = 3
EMPTY = "."
WIN_LINES = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


class TicTacToe:
    def __init__(self, board=None, turn="X"):
        self.turn = turn
        if board is None:
            self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        else:
            self.board = [row[:] for row in board]

    def clone(self):
        return TicTacToe(self.board, self.turn)

    def move(self, player, line, col):
        self.board[line - 1][col - 1] = player

    def play_move(self, player, move):
        line, col = move
        self.board[line][col] = player

    def apply_move(self, move):
        player_that_moved = self.turn
        self.play_move(player_that_moved, move)
        self.turn = self.next_player(player_that_moved)
        return player_that_moved

    def print_board(self):
        for row in self.board:
            print(" ".join(row))

    def current_state(self):
        return [row[:] for row in self.board]

    def are_equal(self, pos1, pos2, pos3):
        return pos1 == pos2 == pos3 and pos1 != EMPTY

    def check_winner(self):
        for line in WIN_LINES:
            values = [self.board[row][col] for row, col in line]
            if self.are_equal(*values):
                row, col = line[0]
                return self.board[row][col]

        return None

    def is_draw(self):
        return self.check_winner() is None and not self.available_moves()

    def is_terminal(self):
        return self.check_winner() is not None or self.is_draw()

    def available_moves(self):
        moves = []
        for line in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[line][col] == EMPTY:
                    moves.append((line, col))
        return moves

    def next_player(self, player):
        if player == "X":
            return "O"
        return "X"

    def check_valid_move(self, line, col):
        if line < 1 or line > BOARD_SIZE or col < 1 or col > BOARD_SIZE:
            return False
        return self.board[line - 1][col - 1] == EMPTY

    def get_human_move(self):
        while True:
            print("Choose line and column (1-3):")
            try:
                line, col = map(int, input().split())
            except ValueError:
                continue

            if self.check_valid_move(line, col):
                return line, col

    def game_loop(self, human_player="X", mcts_iterations=1000):
        ai_player = self.next_player(human_player)
        self.turn = "X"
        mcts = MCTS(iterations=mcts_iterations)

        while not self.is_terminal():
            self.print_board()
            print()

            if self.turn == human_player:
                print(f"{human_player} to play")
                line, col = self.get_human_move()
                self.apply_move((line - 1, col - 1))
            else:
                print(f"{ai_player} (MCTS) is thinking...")
                best_move = mcts.search(self)

                if best_move is None:
                    break

                self.apply_move(best_move)
                print(f"{ai_player} played: {best_move[0] + 1} {best_move[1] + 1}")

        print()
        self.print_board()
        winner = self.check_winner()

        if winner is None:
            print("draw")
        else:
            print("winner:", winner)


if __name__ == "__main__":
    game = TicTacToe()
    game.game_loop()
