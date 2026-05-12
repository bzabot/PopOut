import pandas as pd
import random

from MCTS.pop_out_mcts import PopOutMCTS
from MCTS.mcts_service import MCTS


def generate_dataset(num_games=200, mcts_iterations=3000):
    """
    Puts the MCTS to play against random plays to store his best moves which will be used to train the DT
    """
    dataset_rows = []
    mcts = MCTS(iterations=mcts_iterations)

    print(f"Starting... {num_games} games will be played")

    for i in range(num_games):
        game = PopOutMCTS()

        # decides randomly who is the MCTS in this game, this ensures the DT knows how to be first or second to play
        mcts_player = random.choice([-1, 1])

        if (i + 1) % 5 == 0 or i == 0:
            print(f"Simulating game {i + 1} of {num_games}...")

        while not game.is_terminal():
            turn, flat_board = game.get_board_state()  #1 get game state

            if turn == mcts_player:
                best_move = mcts.search(game)  #2 get best move according to MCTS
                move_label = f"{best_move[0]}_{best_move[1]}"  #3 format label: ex: (3, 'd') -> "3_d"
                row_data = {"turn": turn}  #4 start dict for a single row

                # 5 add the 42 board positions as individual features (cell_0 to cell_41)
                for idx, cell in enumerate(flat_board):
                    row_data[f"cell_{idx}"] = cell

                row_data["best_move"] = move_label  #6 add target
                dataset_rows.append(row_data)  #7 add row to the list
                game.apply_move(best_move)  #8 apply move to progress the game

            else:
                game.apply_move(random.choice(game.available_moves()))

    df = pd.DataFrame(dataset_rows)
    tamanho_original = len(df)
    df = df.drop_duplicates()
    tamanho_novo = len(df)
    df.to_csv("MCTS_popout_dataset_6.csv", index=False)


    print(f"\nProcess successfully finished")
    print(f"Duplicate lines removed: {tamanho_original - tamanho_novo}")
    print(f"Total MCTS examples stored: {tamanho_novo}")

    return df


if __name__ == "__main__":
    generate_dataset(num_games=1000, mcts_iterations=10000)
