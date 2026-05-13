import pandas as pd

from src.mcts.mcts_service import MCTS
from src.pop_out import BLUE_PLAYER, COLOURS, RED_PLAYER, PopOut
from src.popout_decision_tree.train_popout_dt import MODEL_PATH, load_decision_tree

DEFAULT_MODEL_PATH = MODEL_PATH
DT_PLAYER = BLUE_PLAYER
MCTS_PLAYER = RED_PLAYER


class PopOutDT(PopOut):
    """PopOut game that chooses moves with a trained decision tree."""

    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        super().__init__()
        self.tree = load_decision_tree(model_path)

    def get_dt_move(self):
        """Return the decision tree move for the current board state."""
        turn, flat_board = self.get_board_state()
        move_label = self.tree.predict_one(build_example(turn, flat_board))
        col_str, action = move_label.split("_")
        return (int(col_str), action)

    def run_mcts_x_dt(self, mcts_iterations=1000):
        """
        Runs an automatic game between the Monte Carlo Tree Search (MCTS) agent
        and the Decision Tree (DT) agent.

        Args:
            mcts_iterations (int): The number of iterations the MCTS will use per move.
        """
        mcts = MCTS(iterations=mcts_iterations)

        print(
            f"\nSTARTING: {COLOURS['red']}MONTE CARLO TREE SEARCH "
            f"({mcts_iterations} it){COLOURS['reset']} vs "
            f"{COLOURS['blue']}DECISION TREE{COLOURS['reset']}"
        )
        while not self.is_terminal():
            self.print_board()

            if self.turn == MCTS_PLAYER:
                move = self.play_mcts_turn(mcts)
            else:
                move = self.play_dt_turn()

            if move is None:
                break

        self.print_board(show_arrow=False)
        self.print_result()

    def play_mcts_turn(self, mcts):
        """Search, apply, and print one MCTS move."""
        print(
            f"{COLOURS['red']}Monte Carlo Tree Search{COLOURS['reset']} is thinking..."
        )
        move = mcts.search(self)

        if move is None:
            return None

        self.apply_move(move)
        print(
            f"{COLOURS['red']}Monte Carlo Tree Search{COLOURS['reset']} played: {move}"
        )
        return move

    def play_dt_turn(self):
        """Predict, apply, and print one decision tree move."""
        move = self.get_dt_move()
        self.apply_move(move)
        print(f"{COLOURS['blue']}Decision Tree{COLOURS['reset']} played: {move}")
        return move

    def print_result(self):
        """Print the final game result."""
        winner = self.check_winner()
        if winner is None:
            print(f"{COLOURS['green']}DRAW!{COLOURS['reset']}")
        elif winner == MCTS_PLAYER:
            print(f"{COLOURS['red']}Monte Carlo Tree Search WINS!{COLOURS['reset']}")
        elif winner == DT_PLAYER:
            print(f"{COLOURS['blue']}Decision Tree WINS!{COLOURS['reset']}")


def build_example(turn, flat_board):
    """Build the feature row expected by the ID3 prediction function."""
    example = {"turn": turn}

    for idx, cell in enumerate(flat_board):
        example[f"cell_{idx}"] = cell

    return pd.Series(example)


if __name__ == "__main__":
    PopOutDT().run_mcts_x_dt(mcts_iterations=500)
