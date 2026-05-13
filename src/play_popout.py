"""Play PopOut with humans and selectable computer agents.

Run from the project root:

    python -m src.play_popout

The script supports:
- Human vs Human
- Human vs Computer
- Computer vs Computer
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from time import sleep
from typing import Protocol

from src.mcts.mcts_service import MCTS
from src.pop_out import BLUE_PLAYER, COLOURS, RED_PLAYER, PopOut
from src.popout_decision_tree.play_popout_dt import build_example
from src.popout_decision_tree.train_popout_dt import MODEL_PATH, load_decision_tree

HUMAN = "human"
RANDOM = "random"
MCTS_MODEL = "mcts"
DT_MODEL = "dt"
COMPUTER_MODELS = (RANDOM, MCTS_MODEL, DT_MODEL)
PLAYER_NAMES = {
    RED_PLAYER: f"{COLOURS['red']}RED{COLOURS['reset']}",
    BLUE_PLAYER: f"{COLOURS['blue']}BLUE{COLOURS['reset']}",
}


class Player(Protocol):
    """Player interface used by the PopOut match runner."""

    name: str

    def choose_move(self, game: PopOut):
        """Return a legal move for the current PopOut state."""


@dataclass
class HumanPlayer:
    """Human player that reads moves from terminal input."""

    name: str

    def choose_move(self, game: PopOut):
        """Ask the user for a move."""
        return game.get_player_input(game.is_full_board())


@dataclass
class RandomPlayer:
    """Computer player that chooses uniformly from legal moves."""

    name: str = "Random"

    def choose_move(self, game: PopOut):
        """Return a random legal move."""
        return random.choice(game.available_moves())


@dataclass
class MCTSPlayer:
    """Computer player backed by Monte Carlo Tree Search."""

    iterations: int
    name: str = "MCTS"

    def choose_move(self, game: PopOut):
        """Run MCTS and return the selected move."""
        return MCTS(iterations=self.iterations).search(game)


@dataclass
class DecisionTreePlayer:
    """Computer player backed by the trained PopOut decision tree."""

    model_path: str = str(MODEL_PATH)
    name: str = "Decision Tree"

    def __post_init__(self):
        """Load the decision tree once for the whole match."""
        self.tree = load_decision_tree(self.model_path)

    def choose_move(self, game: PopOut):
        """Predict a move and fall back to random if the prediction is illegal."""
        turn, flat_board = game.get_board_state()
        move_label = self.tree.predict_one(build_example(turn, flat_board))
        col_str, action = move_label.split("_")
        move = (int(col_str), action)

        if game.is_valid(move):
            return move

        legal_moves = game.available_moves()
        print(
            f"{COLOURS['yellow']}Decision Tree predicted invalid move {move}; "
            f"using a random legal move instead.{COLOURS['reset']}"
        )
        return random.choice(legal_moves)


class PopOutMatch:
    """Visible terminal match runner for any two PopOut players."""

    def __init__(self, red_player: Player, blue_player: Player, delay: float):
        self.game = PopOut()
        self.game.turn = RED_PLAYER
        self.red_player = red_player
        self.blue_player = blue_player
        self.delay = delay
        self.state_history = {}

    def run(self):
        """Run the match until a win, draw, or interrupted human input."""
        self.print_match_header()
        self.game.print_board(show_arrow=False)

        while True:
            if self.handle_repeated_state_draw():
                break

            current_player = self.get_current_player()
            print()
            self.game.print_turn()
            self.game.print_board(show_arrow=True)
            print(f"{current_player.name} is choosing a move...")

            move = current_player.choose_move(self.game)
            if move == "draw":
                self.print_draw("Game ended as a draw.")
                break
            if move is None:
                self.print_draw("No legal move available. Game ended as a draw.")
                break

            moved_player = self.game.apply_move(move)
            print(f"{self.describe_player(moved_player)} played: {format_move(move)}")
            self.game.print_board(show_arrow=False)

            winner = self.game.check_winner()
            if winner is not None:
                self.game.print_winner(winner)
                break
            if not self.game.available_moves():
                self.print_draw("No legal moves remain. Game ended as a draw.")
                break

            if self.delay > 0 and not isinstance(current_player, HumanPlayer):
                sleep(self.delay)

    def print_match_header(self):
        """Print the selected players before the first turn."""
        print()
        print("=== POP OUT MATCH ===")
        print(f"{PLAYER_NAMES[RED_PLAYER]}: {self.red_player.name}")
        print(f"{PLAYER_NAMES[BLUE_PLAYER]}: {self.blue_player.name}")
        print("=====================")
        print()

    def handle_repeated_state_draw(self):
        """Offer or automatically claim a draw after three repeated states."""
        current_state = self.game.get_board_state()
        self.state_history[current_state] = self.state_history.get(current_state, 0) + 1

        if self.state_history[current_state] < 3:
            return False

        has_human = isinstance(self.red_player, HumanPlayer) or isinstance(
            self.blue_player, HumanPlayer
        )
        if has_human:
            print(
                f"{COLOURS['green']}This board has been repeated 3 times. "
                f"End the game as a draw?{COLOURS['reset']}"
            )
            if self.game.get_ans() == "y":
                self.print_draw("Game ended as a draw.")
                return True
            return False

        self.print_draw("Board repeated 3 times. Game ended as a draw.")
        return True

    def get_current_player(self):
        """Return the Player object for the current turn."""
        if self.game.turn == RED_PLAYER:
            return self.red_player
        return self.blue_player

    def describe_player(self, player):
        """Return a colored player and agent description."""
        agent = self.red_player if player == RED_PLAYER else self.blue_player
        return f"{PLAYER_NAMES[player]} ({agent.name})"

    def print_draw(self, message):
        """Print a draw message with the final board."""
        self.game.print_board(show_arrow=False)
        print(f"{COLOURS['green']}{message}{COLOURS['reset']}")


def format_move(move):
    """Return a readable move description."""
    column, action = move
    action_name = "drop" if action == "d" else "pop"
    return f"column {column}, {action_name}"


def build_player(kind, label, mcts_iterations, dt_model_path):
    """Create a Player from a CLI/menu model name."""
    if kind == HUMAN:
        return HumanPlayer(label)
    if kind == RANDOM:
        return RandomPlayer(f"{label} Random")
    if kind == MCTS_MODEL:
        return MCTSPlayer(mcts_iterations, f"{label} MCTS ({mcts_iterations} it)")
    if kind == DT_MODEL:
        return DecisionTreePlayer(dt_model_path, f"{label} Decision Tree")
    raise ValueError(f"Unknown player kind: {kind}")


def choose_mode():
    """Ask for the desired match mode."""
    print("Choose game mode:")
    print("1. Human vs Human")
    print("2. Human vs Computer")
    print("3. Computer vs Computer")
    return ask_choice("Mode", {"1", "2", "3"})


def choose_computer_model(prompt):
    """Ask for one computer model."""
    print(f"Choose {prompt} model:")
    print("1. Random")
    print("2. MCTS")
    print("3. Decision Tree")
    selected = ask_choice(prompt, {"1", "2", "3"})
    return {"1": RANDOM, "2": MCTS_MODEL, "3": DT_MODEL}[selected]


def ask_choice(prompt, allowed):
    """Read a menu choice until it is valid."""
    while True:
        answer = input(f"{prompt}: ").strip()
        if answer in allowed:
            return answer
        print(f"Invalid choice. Choose one of: {', '.join(sorted(allowed))}")


def players_from_menu(args):
    """Build red and blue players from interactive menu answers."""
    mode = choose_mode()

    if mode == "1":
        return (
            build_player(HUMAN, "Red Human", args.mcts_iterations, args.dt_model_path),
            build_player(HUMAN, "Blue Human", args.mcts_iterations, args.dt_model_path),
        )

    if mode == "2":
        computer_model = choose_computer_model("computer")
        human_color = ask_human_color()
        human = build_player(HUMAN, "Human", args.mcts_iterations, args.dt_model_path)
        computer = build_player(
            computer_model,
            "Computer",
            args.mcts_iterations,
            args.dt_model_path,
        )
        if human_color == RED_PLAYER:
            return human, computer
        return computer, human

    red_model = choose_computer_model("RED computer")
    blue_model = choose_computer_model("BLUE computer")
    return (
        build_player(red_model, "Red", args.mcts_iterations, args.dt_model_path),
        build_player(blue_model, "Blue", args.mcts_iterations, args.dt_model_path),
    )


def ask_human_color():
    """Ask whether the human should play red or blue."""
    print("Choose human color:")
    print("1. Red (first)")
    print("2. Blue (second)")
    selected = ask_choice("Color", {"1", "2"})
    return RED_PLAYER if selected == "1" else BLUE_PLAYER


def players_from_args(args):
    """Build players directly from CLI arguments when provided."""
    if args.red is None and args.blue is None:
        return players_from_menu(args)
    if args.red is None or args.blue is None:
        raise ValueError("Use both --red and --blue, or neither for the menu.")
    return (
        build_player(args.red, "Red", args.mcts_iterations, args.dt_model_path),
        build_player(args.blue, "Blue", args.mcts_iterations, args.dt_model_path),
    )


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Play PopOut in the terminal.")
    parser.add_argument(
        "--red",
        choices=(HUMAN, *COMPUTER_MODELS),
        help="RED player type. If omitted, an interactive menu is shown.",
    )
    parser.add_argument(
        "--blue",
        choices=(HUMAN, *COMPUTER_MODELS),
        help="BLUE player type. If omitted, an interactive menu is shown.",
    )
    parser.add_argument(
        "--mcts-iterations",
        type=int,
        default=5000,
        help="MCTS iterations per move.",
    )
    parser.add_argument(
        "--dt-model-path",
        default=str(MODEL_PATH),
        help="Path to the trained Decision Tree pickle model.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Seconds to wait after computer moves.",
    )
    return parser.parse_args()


def main():
    """CLI entrypoint."""
    args = parse_args()
    red_player, blue_player = players_from_args(args)
    PopOutMatch(red_player, blue_player, args.delay).run()


if __name__ == "__main__":
    main()
