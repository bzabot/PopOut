# Decision Tree

This folder contains a small ID3 decision tree implementation for supervised
classification.

The code in this folder is intentionally generic. It should only know about
tabular training data:

- `X`: a pandas `DataFrame` with the input attributes.
- `labels`: a pandas `Series` or list with the target class for each row.

It should not depend on PopOut, MCTS, board states, move generation, or model
training scripts. Those concerns should live outside this folder.

## Files

- `id3_decision_tree.py`
  - Defines `ID3DecisionTree`.
  - Owns the trained tree root after calling `fit`.
  - Provides prediction methods.

- `tree_node.py`
  - Defines `TreeNode`.
  - Represents either a decision node or a leaf node.

- `metrics.py`
  - Defines entropy, conditional entropy, information gain, and best-attribute
    selection.
  - These functions are used by the ID3 training algorithm.

## Basic Usage

Run this from a context where `src/decision_tree` is on the Python path.

```python
import pandas as pd

from id3_decision_tree import ID3DecisionTree

X = pd.DataFrame(
    {
        "outlook": ["sunny", "sunny", "overcast", "rain"],
        "wind": ["weak", "strong", "weak", "weak"],
    }
)

labels = pd.Series(["no", "no", "yes", "yes"])

model = ID3DecisionTree()
model.fit(X, labels)

predictions = model.predict(X)
print(predictions)
```

## Training Flow

Use `fit` when training a model:

```python
model = ID3DecisionTree()
model.fit(X_train, y_train)
```

After training:

- `model.root` contains the root `TreeNode`.
- `model.attributes` contains the training attributes used by the tree.
- `model.predict(X)` predicts one label for each row in `X`.
- `model.predict_one(row)` predicts a label for a single example.

## Saving A Trained Model

Training scripts can save the fitted model with `pickle`.

```python
import pickle

model = ID3DecisionTree()
model.fit(X_train, y_train)

with open("models/popout_id3.pkl", "wb") as file:
    pickle.dump(model, file)
```

Loading it later:

```python
import pickle

with open("models/popout_id3.pkl", "rb") as file:
    model = pickle.load(file)

predictions = model.predict(X)
```

## Architectural Boundary

Keep this folder focused on the ID3 algorithm.

PopOut-specific code should handle:

- converting board states into feature rows;
- creating training datasets;
- choosing where trained models are saved;
- loading a trained model during gameplay;
- translating predicted labels back into PopOut moves.

That means a PopOut training pipeline should look like this:

```text
PopOut game data
    -> feature extraction
    -> X and labels
    -> ID3DecisionTree.fit(X, labels)
    -> saved trained model
```

Later gameplay can load the saved model and use the same feature extraction
logic before calling `predict_one`.

## Prediction Fallback

Each decision node stores the majority class seen at that node during training.
If prediction reaches a value that was not seen during training, the model
returns that node's majority class instead of failing.

