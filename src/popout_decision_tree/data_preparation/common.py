"""Shared paths and helpers for PopOut dataset generation."""

import glob
import random
from pathlib import Path

import pandas as pd

DATASETS_DIR = Path(__file__).resolve().parents[1] / "datasets"

RANDOM_VS_MCTS_DATASET = DATASETS_DIR / "popout_random_vs_mcts.csv"
MCTS_SELF_PLAY_DATASET = DATASETS_DIR / "popout_mcts_self_play.csv"
MCTS_VS_DT_DATASET = DATASETS_DIR / "popout_mcts_vs_dt.csv"
INITIAL_TRAINING_DATASET = DATASETS_DIR / "popout_training_initial.csv"
FULL_TRAINING_DATASET = DATASETS_DIR / "popout_training_full.csv"

INITIAL_TRAINING_INPUTS = (
    RANDOM_VS_MCTS_DATASET,
    MCTS_SELF_PLAY_DATASET,
)
FULL_TRAINING_INPUTS = (
    RANDOM_VS_MCTS_DATASET,
    MCTS_SELF_PLAY_DATASET,
    MCTS_VS_DT_DATASET,
)


def build_dataset_row(turn, flat_board, best_move):
    """Build one decision-tree training row from a board state and MCTS move."""
    row = {"turn": turn}

    for idx, cell in enumerate(flat_board):
        row[f"cell_{idx}"] = cell

    row["best_move"] = format_move_label(best_move)
    return row


def format_move_label(move):
    """Convert a PopOut move tuple into the CSV target label format."""
    return f"{move[0]}_{move[1]}"


def choose_player():
    """Return the player selected to be controlled by MCTS in one game."""
    return random.choice([-1, 1])


def choose_move(moves):
    """Return one random legal move from the available move list."""
    return random.choice(moves)


def print_progress(game_number, total_games, interval):
    """Print progress for the first game and then every ``interval`` games."""
    if game_number == 1 or game_number % interval == 0:
        print(f"Simulating game {game_number} of {total_games}...")


def save_unique_dataset(dataset_rows, output_path):
    """Drop duplicate rows, save the dataset as CSV, and return duplicate count."""
    output_path = Path(output_path)
    dataset = pd.DataFrame(dataset_rows)
    original_size = len(dataset)
    dataset = dataset.drop_duplicates()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    return dataset, original_size - len(dataset)


def merge_datasets(
    input_paths=INITIAL_TRAINING_INPUTS,
    output_path=INITIAL_TRAINING_DATASET,
):
    """Merge the given dataset CSV files, drop duplicates, and save the result."""
    csv_files = [Path(csv_file) for csv_file in input_paths]
    output_path = Path(output_path)

    print(len(csv_files))

    datasets = []

    for csv_file in csv_files:
        datasets.append(pd.read_csv(csv_file))

    merged_dataset = pd.concat(datasets, ignore_index=True)
    original_size = len(merged_dataset)
    merged_dataset = merged_dataset.drop_duplicates()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_dataset.to_csv(output_path, index=False)

    print(f"Total lines read: {original_size}")
    print(f"Duplicates: {original_size - len(merged_dataset)}")
    print(f"Unique lines to train the DT: {len(merged_dataset)}")

    return merged_dataset


def merge_datasets_by_pattern(input_pattern, output_path):
    """Merge dataset CSV files matched by a glob pattern."""
    return merge_datasets(glob.glob(input_pattern), output_path)
