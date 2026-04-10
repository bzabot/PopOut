from MCTS import MCTS


class TicTacToe:
    def __init__(self, board=None):
        if board is None:
            self.board = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
        else:
            self.board = [row[:] for row in board]

    def clone(self):
        return TicTacToe(self.board)

    def move(self, player, line, col):
        self.board[line - 1][col - 1] = player

    def play_move(self, player, move):
        line, col = move
        self.board[line][col] = player

    def print_board(self):
        for row in self.board:
            print(" ".join(row))

    def current_state(self):
        return [row[:] for row in self.board]

    def are_equal(self, pos1, pos2, pos3):
        return pos1 == pos2 == pos3 and pos1 != "."

    def check_winner(self):
        # Lines
        if self.are_equal(self.board[0][0], self.board[0][1], self.board[0][2]):
            return self.board[0][0]
        if self.are_equal(self.board[1][0], self.board[1][1], self.board[1][2]):
            return self.board[1][0]
        if self.are_equal(self.board[2][0], self.board[2][1], self.board[2][2]):
            return self.board[2][0]

        # Columns
        if self.are_equal(self.board[0][0], self.board[1][0], self.board[2][0]):
            return self.board[0][0]
        if self.are_equal(self.board[0][1], self.board[1][1], self.board[2][1]):
            return self.board[0][1]
        if self.are_equal(self.board[0][2], self.board[1][2], self.board[2][2]):
            return self.board[0][2]

        # Diagonals
        if self.are_equal(self.board[0][0], self.board[1][1], self.board[2][2]):
            return self.board[0][0]
        if self.are_equal(self.board[0][2], self.board[1][1], self.board[2][0]):
            return self.board[0][2]

        return None

    def is_draw(self):
        return self.check_winner() is None and not self.available_moves()

    def is_terminal(self):
        return self.check_winner() is not None or self.is_draw()

    def available_moves(self):
        moves = []
        for line in range(3):
            for col in range(3):
                if self.board[line][col] == ".":
                    moves.append((line, col))
        return moves

    def next_player(self, player):
        if player == "X":
            return "O"
        return "X"

    def check_valid_move(self, line, col):
        if line < 1 or line > 3 or col < 1 or col > 3:
            return False
        return self.board[line - 1][col - 1] == "."

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
        current_player = "X"
        mcts = MCTS(iterations=mcts_iterations)

        while not self.is_terminal():
            self.print_board()
            print()

            if current_player == human_player:
                print(f"{human_player} to play")
                line, col = self.get_human_move()
                self.move(human_player, line, col)
            else:
                print(f"{ai_player} (MCTS) is thinking...")
                best_move = mcts.search(self, ai_player)

                if best_move is None:
                    break

                self.play_move(ai_player, best_move)
                print(f"{ai_player} played: {best_move[0] + 1} {best_move[1] + 1}")

            current_player = self.next_player(current_player)

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
