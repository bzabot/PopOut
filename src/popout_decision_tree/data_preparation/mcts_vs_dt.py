"""Generate DAgger-style PopOut examples from MCTS against a decision tree."""

from src.mcts.mcts_service import MCTS
from src.popout_decision_tree.data_preparation.common import (
    MCTS_VS_DT_DATASET,
    build_dataset_row,
    choose_player,
    print_progress,
    save_unique_dataset,
)


def generate_dagger_dataset(
    num_games=50,
    mcts_iterations=10000,
    output_path=MCTS_VS_DT_DATASET,
):
    """Generate examples from games between MCTS and an existing DT model.

    This step must run after an initial decision tree has been trained, because
    ``PopOutDT`` loads the trained model and uses it to choose non-MCTS moves.
    """
    from src.popout_decision_tree.play_popout_dt import PopOutDT  # noqa: PLC0415

    dataset_rows = []
    mcts = MCTS(iterations=mcts_iterations)

    print(f"Starting (Dataset Aggregation)... {num_games} games will be played")

    for game_index in range(num_games):
        game = PopOutDT()
        mcts_player = choose_player()
        print_progress(game_index + 1, num_games, interval=5)

        while not game.is_terminal():
            turn, flat_board = game.get_board_state()

            if turn == mcts_player:
                best_move = mcts.search(game)

                if best_move is None:
                    break

                dataset_rows.append(build_dataset_row(turn, flat_board, best_move))
                game.apply_move(best_move)
            else:
                game.apply_move(game.get_dt_move())

    dataset, _duplicates = save_unique_dataset(dataset_rows, output_path)

    print(f"\nSuccess, {len(dataset)} examples generated")

    return dataset


if __name__ == "__main__":
    generate_dagger_dataset(num_games=50, mcts_iterations=10000)
