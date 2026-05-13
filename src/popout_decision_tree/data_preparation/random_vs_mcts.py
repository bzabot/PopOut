"""Generate PopOut examples from MCTS playing against random moves."""

from src.mcts.mcts_service import MCTS
from src.mcts.pop_out_mcts import PopOutMCTS
from src.popout_decision_tree.data_preparation.common import (
    RANDOM_VS_MCTS_DATASET,
    build_dataset_row,
    choose_move,
    choose_player,
    print_progress,
    save_unique_dataset,
)


def generate_dataset(
    num_games=200,
    mcts_iterations=3000,
    output_path=RANDOM_VS_MCTS_DATASET,
):
    """Generate MCTS-labeled positions from games against random moves.

    In each game, one randomly chosen player is controlled by MCTS and the
    other player uses random legal moves. Only MCTS turns are stored because
    they provide the target labels used by the decision tree.
    """
    dataset_rows = []
    mcts = MCTS(iterations=mcts_iterations)

    print(f"Starting... {num_games} games will be played")

    for game_index in range(num_games):
        game = PopOutMCTS()
        mcts_player = choose_player()
        print_progress(game_index + 1, num_games, interval=5)

        while not game.is_terminal():
            turn, flat_board = game.get_board_state()

            if turn == mcts_player:
                best_move = mcts.search(game)
                dataset_rows.append(build_dataset_row(turn, flat_board, best_move))
                game.apply_move(best_move)
            else:
                game.apply_move(choose_move(game.available_moves()))

    dataset, duplicates = save_unique_dataset(dataset_rows, output_path)

    print("\nProcess successfully finished")
    print(f"Duplicate lines removed: {duplicates}")
    print(f"Total MCTS examples stored: {len(dataset)}")

    return dataset


if __name__ == "__main__":
    generate_dataset(num_games=1000, mcts_iterations=10000)
