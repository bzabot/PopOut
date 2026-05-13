"""Generate the initial PopOut decision-tree training dataset.

This entry point creates the two datasets that do not depend on an existing
decision tree model, then merges them into ``popout_training_initial.csv``.
"""

from src.popout_decision_tree.data_preparation.common import (
    INITIAL_TRAINING_DATASET,
    INITIAL_TRAINING_INPUTS,
    merge_datasets,
)
from src.popout_decision_tree.data_preparation.mcts_vs_mcts import (
    generate_mcts_self_play,
)
from src.popout_decision_tree.data_preparation.random_vs_mcts import generate_dataset


def main():
    """Generate random-vs-MCTS and MCTS-self-play data, then merge them."""
    generate_dataset(num_games=1000, mcts_iterations=5000)
    generate_mcts_self_play(num_games=20, mcts_iterations=5000)
    merge_datasets(
        input_paths=INITIAL_TRAINING_INPUTS,
        output_path=INITIAL_TRAINING_DATASET,
    )


if __name__ == "__main__":
    main()
