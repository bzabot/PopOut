import pickle
import pandas as pd
from MCTS.pop_out_mcts import PopOutMCTS
from MCTS.mcts_service import MCTS
from id3 import predict_one
from pop_out import RED_PLAYER, BLUE_PLAYER, COLOURS


class PopOutDT(PopOutMCTS):
    """
    Class integrates the trained Decision Tree model into the PopOut game.
    It inherits from PopOutMCTS to utilize game logic and state representation.
    """

    def __init__(self, model_path="popout_DT_model.pkl"):
        """
        Initializes the game and loads the pre-trained Decision Tree model.

        Args:
            model_path (str): The file path to the trained pickle model.
        """
        super().__init__()
        with open(model_path, "rb") as f:
            self.tree = pickle.load(f)

    def get_dt_move(self):
        """
        Converts the current game state into the feature format expected by the Decision Tree and returns the move.

        Returns:
            tuple: A move in the format (column_index, action), ex: (3, 'd').
        """
        turn, flat_board = self.get_board_state()

        # create a dict representing the features
        example = {"turn": turn}
        for idx, cell in enumerate(flat_board):
            example[f"cell_{idx}"] = cell

        example_series = pd.Series(example)  # convert to a Pandas Series as expected by the id3 predict_one function
        move_label = predict_one(self.tree, example_series)  # get the predicted label (ex: "3_d")
        col_str, action = move_label.split('_')  # split the string back
        return (int(col_str), action)

    def run_mcts_x_dt(self, mcts_iterations=1000):
        """
        Runs an automatic game between the Monte Carlo Tree Search (MCTS) agent
        and the Decision Tree (DT) agent.

        Args:
            mcts_iterations (int): The number of iterations the MCTS will use per move.
        """
        mcts = MCTS(iterations=mcts_iterations)

        # assign players
        dt_player = BLUE_PLAYER
        mcts_player = RED_PLAYER

        print(f"\nSTARTING: {COLOURS['red']}MONTE CARLO TREE SEARCH ({mcts_iterations} it){COLOURS['reset']} vs {COLOURS['blue']}DECISION TREE{COLOURS['reset']}")
        while not self.is_terminal():
            self.print_board()

            # check turn and play
            if self.turn == mcts_player:
                print(f"{COLOURS['red']}Monte Carlo Tree Search{COLOURS['reset']} is thinking...")
                move = mcts.search(self)
                self.apply_move(move)
                print(f"{COLOURS['red']}Monte Carlo Tree Search{COLOURS['reset']} played: {move}")
            else:
                move = self.get_dt_move()
                self.apply_move(move)
                print(f"{COLOURS['blue']}Decision Tree{COLOURS['reset']} played: {move}")

        self.print_board(show_arrow=False)

        winner = self.check_winner()
        if winner == 0:
            print(f"{COLOURS['green']}DRAW!{COLOURS['reset']}")
        elif winner == mcts_player:
            print(f"{COLOURS['red']}Monte Carlo Tree Search WINS!{COLOURS['reset']}")
        elif winner == dt_player:
            print(f"{COLOURS['blue']}Decision Tree WINS!{COLOURS['reset']}")


if __name__ == "__main__":
    PopOutDT().run_mcts_x_dt(mcts_iterations=500)