import pandas as pd
from id3 import build_tree
from visualizer import save_dot
import pickle


def train_popout_decision_tree():
    """
    Reads the generated dataset, separates features and targets and trains the DT
    In the end, saves the DT in a "pkl" binary file and exports the tree to "dot" format for visualisation.
    """
    df = pd.read_csv("MCTS_popout_dataset.csv")
    target = df["best_move"]
    X = df.drop(columns=["best_move"])
    print(f"Dataset loaded with {len(df)} examples")
    print("Starting training for DT...")
    print("This can take a while")
    tree = build_tree(X, target)
    print("Process finished successfully, saving tree")
    with open("popout_DT_model.pkl", "wb") as f:
        pickle.dump(tree, f)
    save_dot(tree, "popout_tree.dot")
    return tree


if __name__ == "__main__":
    train_popout_decision_tree()