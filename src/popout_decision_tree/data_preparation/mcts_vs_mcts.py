"""Generate PopOut examples from MCTS self-play."""

from src.mcts.mcts_service import MCTS
from src.mcts.pop_out_mcts import PopOutMCTS
from src.popout_decision_tree.data_preparation.common import (
    MCTS_SELF_PLAY_DATASET,
    build_dataset_row,
    print_progress,
    save_unique_dataset,
)


def generate_mcts_self_play(
    num_games=20,
    mcts_iterations=10000,
    output_path=MCTS_SELF_PLAY_DATASET,
):
    """Generate MCTS-labeled positions while MCTS controls both players."""
    dataset_rows = []
    mcts = MCTS(iterations=mcts_iterations)

    print(f"Starting... {num_games} games will be played")

    for game_index in range(num_games):
        game = PopOutMCTS()
        print_progress(game_index + 1, num_games, interval=2)

        while not game.is_terminal():
            turn, flat_board = game.get_board_state()
            best_move = mcts.search(game)

            dataset_rows.append(build_dataset_row(turn, flat_board, best_move))
            game.apply_move(best_move)

    dataset, _duplicates = save_unique_dataset(dataset_rows, output_path)

    print(f"Success, {len(dataset)} unique examples generated")

    return dataset


if __name__ == "__main__":
    generate_mcts_self_play(num_games=20, mcts_iterations=10000)
