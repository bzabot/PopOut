"""ID3 decision tree classifier for categorical tabular data."""

import pandas as pd

from .metrics import best_attribute
from .tree_node import TreeNode


class ID3DecisionTree:
    """Train and use an ID3 decision tree classifier."""

    def __init__(self):
        """Create an unfitted decision tree."""
        self.root = None
        self.attributes = None

    def majority_class(self, labels):
        """Return the most frequent label from a label collection."""
        labels = pd.Series(labels)
        counts = labels.value_counts()

        most_common_label = counts.idxmax()

        return most_common_label

    def fit(self, X, labels):
        """Train the decision tree from a feature table and target labels.

        Args:
            X: pandas DataFrame containing the training attributes.
            labels: Class labels aligned by row with ``X``.

        Returns:
            The fitted ``ID3DecisionTree`` instance.
        """
        self.attributes = list(X.columns)
        self.root = self._build_tree(X, labels, self.attributes)
        return self

    def _build_tree(self, X, labels, attributes):
        """Recursively build a tree node using the remaining attributes."""
        X = X.reset_index(drop=True)
        labels = pd.Series(labels).reset_index(drop=True)

        node_majority_class = self.majority_class(labels)  # fallback

        if labels.nunique() == 1:
            return TreeNode.leaf(labels.iloc[0])

        if len(attributes) == 0:
            return TreeNode.leaf(node_majority_class)

        X_available_attributes = X[attributes]

        best_column, best_gain, _ = best_attribute(  # find the best attribute
            X_available_attributes, labels
        )

        if best_gain == 0:
            return TreeNode.leaf(node_majority_class)

        node = TreeNode.decision(best_column, node_majority_class)

        remaining_attributes = [
            attribute for attribute in attributes if attribute != best_column
        ]

        attribute_values = X[best_column].unique()  # get possible branch values

        for value in attribute_values:
            rows_with_this_value = X[best_column] == value  # True/False mask

            child_X = X[rows_with_this_value].reset_index(
                drop=True
            )  # creating subset for each value
            child_labels = labels[rows_with_this_value].reset_index(drop=True)

            child_node = self._build_tree(  # recursive call
                child_X, child_labels, remaining_attributes
            )

            node.add_child(value, child_node)

        return self._collapse_if_redundant(node)

    def _collapse_if_redundant(self, node):
        """Replace a decision node with a leaf when all children agree."""
        child_predictions = []

        for child_node in node.children.values():
            if child_node.is_leaf:
                child_predictions.append(child_node.prediction)

        if len(child_predictions) != len(node.children):
            return node

        if len(set(child_predictions)) == 1:
            return TreeNode.leaf(child_predictions[0])

        return node

    def print_tree(self, node=None, indent=""):
        """Print a readable representation of the trained tree."""
        if node is None:
            if self.root is None:
                raise ValueError("The tree has not been trained yet.")
            node = self.root

        if node.is_leaf:
            print(indent + f"Predict: {node.prediction}")
            return

        print(indent + f"Attribute: {node.attribute}")

        for attribute_value, child_node in node.children.items():
            print(indent + f"If {node.attribute} == {attribute_value}:")
            self.print_tree(child_node, indent + "    ")

    def predict_one(self, example, tree=None):
        """Predict the class for one example.

        Args:
            example: Row-like object indexed by attribute name.
            tree: Optional tree root. Defaults to the fitted model root.

        Returns:
            The predicted class label.
        """
        if isinstance(example, TreeNode):
            example, tree = tree, example

        node = self.root if tree is None else tree
        if node is None:
            raise ValueError("The tree has not been trained yet.")

        while not node.is_leaf:
            attribute = node.attribute

            attribute_value = example[attribute]

            if attribute_value in node.children:
                node = node.children[attribute_value]
            else:
                return node.majority_class

        return node.prediction

    def predict(self, X, tree=None):
        """Predict the class for every row in a feature table.

        Args:
            X: pandas DataFrame containing examples to classify.
            tree: Optional tree root. Defaults to the fitted model root.

        Returns:
            A list of predicted class labels.
        """
        if isinstance(X, TreeNode):
            X, tree = tree, X

        if X is None:
            raise ValueError("X is required for prediction.")

        predictions = []

        for _, row in X.iterrows():
            prediction = self.predict_one(row, tree)

            predictions.append(prediction)

        return predictions
