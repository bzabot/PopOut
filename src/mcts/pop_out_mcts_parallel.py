"""PopOut terminal loop for playing against parallel Monte Carlo Tree Search."""

try:
    from ..pop_out import DRAW_MOVE, RED_PLAYER, PopOut
    from .mcts_service_parallel import ParallelMCTS
except ImportError:
    from src.mcts.mcts_service_parallel import ParallelMCTS
    from src.pop_out import DRAW_MOVE, RED_PLAYER, PopOut


class PopOutMCTSParallel(PopOut):
    """PopOut game with a human-vs-parallel-MCTS terminal loop."""

    def game_loop(self, human_player=RED_PLAYER, mcts_iterations=1500):
        """Run an interactive human-vs-parallel-MCTS PopOut game in the terminal.

        Args:
            human_player (int): The player controlled through terminal input.
            mcts_iterations (int): Total search iterations used for each MCTS move.
        """
        mcts = ParallelMCTS(iterations=mcts_iterations)

        while not self.is_terminal():
            self.print_board()

            if self.turn == human_player:
                move = self.get_player_input(self.is_full_board())
                if move == DRAW_MOVE:
                    self.apply_move(move)
                    self.print_board(show_arrow=False)
                    print("Draw")
                    break
                self.apply_move(move)
            else:
                print("Parallel MCTS is thinking...")
                move = mcts.search(self)

                if move is None:
                    break

                self.apply_move(move)
                print(f"Parallel MCTS played: {move}")
                if move == DRAW_MOVE:
                    self.print_board(show_arrow=False)
                    print("Draw")
                    break
            self.print_board(show_arrow=False)

            if self.is_terminal():
                winner = self.check_winner()
                if winner is None:
                    print("Draw")
                else:
                    self.print_winner(winner)


if __name__ == "__main__":
    game = PopOutMCTSParallel()
    game.game_loop()
