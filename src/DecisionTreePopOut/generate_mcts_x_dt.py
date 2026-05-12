import pandas as pd
import random
from MCTS.mcts_service import MCTS
from pop_out_DT import PopOutDT


def generate_dagger_dataset(num_games=50, mcts_iterations=10000):
    dataset_rows = []
    mcts = MCTS(iterations=mcts_iterations)

    print(f"Starting (Dataset Aggregation)... {num_games} games will be played")

    for i in range(num_games):
        game = PopOutDT()

        mcts_player = random.choice([-1, 1])

        if (i + 1) % 5 == 0 or i == 0:
            print(f"Simulating game {i + 1} of {num_games}...")

        while not game.is_terminal():
            turn, flat_board = game.get_board_state()

            if turn == mcts_player:
                best_move = mcts.search(game)

                if best_move is None:
                    break

                move_label = f"{best_move[0]}_{best_move[1]}"
                row_data = {"turn": turn}
                for idx, cell in enumerate(flat_board):
                    row_data[f"cell_{idx}"] = cell
                row_data["best_move"] = move_label

                dataset_rows.append(row_data)
                game.apply_move(best_move)
            else:
                dt_move = game.get_dt_move()
                game.apply_move(dt_move)

    df = pd.DataFrame(dataset_rows)
    df = df.drop_duplicates()
    df.to_csv("MCTS_popout_dataset_MCTS_x_DT_2", index=False)

    print(f"\nSuccess, {len(df)} examples generated")


if __name__ == "__main__":
    generate_dagger_dataset(num_games=50, mcts_iterations=10000)