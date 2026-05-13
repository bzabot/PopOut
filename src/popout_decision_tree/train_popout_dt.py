"""Train and export an ID3 decision tree for the PopOut dataset."""

import pickle
import sys
import types
from itertools import count
from pathlib import Path
from time import perf_counter

import pandas as pd

from src.decision_tree.id3_decision_tree import ID3DecisionTree
from src.decision_tree.tree_node import TreeNode
from src.popout_decision_tree.data_preparation.common import FULL_TRAINING_DATASET

DATASET_PATH = FULL_TRAINING_DATASET
MODEL_PATH = Path(__file__).resolve().parent / "datasets" / "popout_DT_model.pkl"
LEGACY_MODEL_PATH = (
    Path(__file__).resolve().parent / "datasets" / "legacy" / "popout_DT_model.pkl"
)
DOT_PATH = Path(__file__).resolve().parent / "datasets" / "popout_tree.dot"
TARGET_COLUMN = "best_move"


def train_popout_decision_tree(
    dataset_path=DATASET_PATH,
    model_path=MODEL_PATH,
    dot_path=DOT_PATH,
):
    """Train the PopOut decision tree and save the model plus DOT export."""
    model_path = Path(model_path)
    df = pd.read_csv(dataset_path)
    target = df[TARGET_COLUMN]
    features = df.drop(columns=[TARGET_COLUMN])

    print(f"Dataset loaded with {len(df)} examples")
    print("Starting training for DT...")
    print("This can take a while")

    start_time = perf_counter()
    tree = ID3DecisionTree().fit(features, target)
    elapsed_time = perf_counter() - start_time

    print(f"Training finished in {elapsed_time:.2f} seconds, saving tree")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as file:
        pickle.dump(tree, file)

    save_dot(tree.root, dot_path)
    return tree


def load_decision_tree(model_path=MODEL_PATH):
    """Load a decision tree model and normalize legacy raw nodes."""
    register_legacy_pickle_modules()
    model_path = Path(model_path)
    if not model_path.exists() and model_path == MODEL_PATH:
        model_path = LEGACY_MODEL_PATH

    with open(model_path, "rb") as file:
        tree = pickle.load(file)

    if isinstance(tree, ID3DecisionTree):
        return tree

    if isinstance(tree, TreeNode):
        decision_tree = ID3DecisionTree()
        decision_tree.root = tree
        return decision_tree

    raise TypeError(f"Unsupported decision tree model type: {type(tree).__name__}")


def register_legacy_pickle_modules():
    """Register old module names needed by previously saved pickle models."""
    legacy_id3 = types.ModuleType("id3")
    legacy_id3.TreeNode = TreeNode
    sys.modules.setdefault("id3", legacy_id3)


def escape_dot_text(text):
    """Return text escaped for use inside a Graphviz DOT label."""
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def tree_to_dot(tree):
    """Convert a trained decision tree into Graphviz DOT text."""
    lines = [
        "digraph DecisionTree {",
        "    rankdir=TB;",
        '    node [fontname="Arial"];',
        '    edge [fontname="Arial"];',
    ]
    node_ids = count()

    def add_node(node):
        node_id = f"node_{next(node_ids)}"

        if node.is_leaf:
            label = escape_dot_text(f"Predict: {node.prediction}")
            lines.append(f'    {node_id} [label="{label}", shape=box];')
            return node_id

        label = escape_dot_text(f"Attribute: {node.attribute}")
        lines.append(f'    {node_id} [label="{label}", shape=ellipse];')

        for attribute_value, child_node in node.children.items():
            child_id = add_node(child_node)
            edge_label = escape_dot_text(attribute_value)
            lines.append(f'    {node_id} -> {child_id} [label="{edge_label}"];')

        return node_id

    add_node(tree)

    lines.append("}")
    return "\n".join(lines)


def save_dot(tree, filename):
    """Save a trained decision tree as a Graphviz DOT file."""
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(tree_to_dot(tree))


if __name__ == "__main__":
    train_popout_decision_tree()
