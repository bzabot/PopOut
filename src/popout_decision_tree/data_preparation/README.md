# PopOut Decision Tree Data Preparation

This package generates CSV datasets used to train the PopOut decision tree.
All outputs are written to `src/popout_decision_tree/datasets/`.

## Dataset Files

- `popout_random_vs_mcts.csv`: examples where MCTS labels positions from games against random moves.
- `popout_mcts_self_play.csv`: examples from MCTS playing both sides.
- `popout_mcts_vs_dt.csv`: DAgger-style examples from games between MCTS and a trained decision tree.
- `popout_training_initial.csv`: merge of the random-vs-MCTS and MCTS-self-play datasets.
- `popout_training_full.csv`: intended merge including the DAgger dataset after the first decision tree exists.

## Recommended Order

1. Generate the initial training data:

   ```bash
   uv run python -m src.popout_decision_tree.data_preparation.generate_dataset
   ```

2. Train the decision tree with `popout_training_initial.csv`.

3. Generate the MCTS-vs-DT dataset:

   ```bash
   uv run python -m src.popout_decision_tree.data_preparation.mcts_vs_dt
   ```

4. Merge all datasets into `popout_training_full.csv` if you want to retrain with
   DAgger examples.

## Module Map

- `common.py`: shared constants and CSV helpers.
- `random_vs_mcts.py`: generates MCTS labels from MCTS-vs-random games.
- `mcts_vs_mcts.py`: generates labels from MCTS self-play.
- `mcts_vs_dt.py`: generates DAgger labels using an already-trained decision tree.
- `generate_dataset.py`: main initial-data pipeline.
