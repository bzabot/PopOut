import pandas as pd
from MCTS.pop_out_mcts import PopOutMCTS
from MCTS.mcts_service import MCTS


def generate_mcts_self_play(num_games=20, mcts_iterations=10000):
    dataset_rows = []
    mcts = MCTS(iterations=mcts_iterations)

    print(f"Starting... {num_games} games will be played")

    for i in range(num_games):
        game = PopOutMCTS()

        if (i + 1) % 2 == 0 or i == 0:
            print(f"Simulating game {i + 1} of {num_games}...")

        while not game.is_terminal():
            turn, flat_board = game.get_board_state()

            best_move = mcts.search(game)

            move_label = f"{best_move[0]}_{best_move[1]}"
            row_data = {"turn": turn}
            for idx, cell in enumerate(flat_board):
                row_data[f"cell_{idx}"] = cell
            row_data["best_move"] = move_label

            dataset_rows.append(row_data)
            game.apply_move(best_move)

    df = pd.DataFrame(dataset_rows)
    df = df.drop_duplicates()
    df.to_csv("MCTS_popout_dataset_MCTS_x_MCTS.csv", index=False)

    print(f"Success, {len(df)} unique examples generated")


if __name__ == "__main__":
    nome_ficheiro = "dataset_mcts_v_mcts_1.csv"

    generate_mcts_self_play(num_games=20, mcts_iterations=10000)