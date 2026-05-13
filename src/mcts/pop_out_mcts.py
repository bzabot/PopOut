"""PopOut terminal loop for playing against Monte Carlo Tree Search."""

from ..pop_out import RED_PLAYER, PopOut
from .mcts_service import MCTS


class PopOutMCTS(PopOut):
    """PopOut game with a human-vs-MCTS terminal loop."""

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
