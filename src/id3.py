import pandas as pd

from src.metrics import best_attribute


class TreeNode:
    def __init__(
        self,
        is_leaf=False,
        prediction=None,
        attribute=None, # the feature that the tree will be split on (questions asked to make descision at that node)
        majority_class=None
    ):
        self.is_leaf = is_leaf
        self.prediction = prediction
        self.attribute = attribute
        self.children = {} # dictionary with child nodes - answers/results of that split
        self.majority_class = majority_class

    def add_child(self, attribute_value, child_node):
        self.children[attribute_value] = child_node

    def __repr__(self):
        if self.is_leaf:
            return f"Leaf(prediction={self.prediction})"

        return f"DecisionNode(attribute={self.attribute}, children={list(self.children.keys())})"


def majority_class(labels):
    labels = pd.Series(labels)

    counts = labels.value_counts()

    most_common_label = counts.idxmax()

    return most_common_label


def build_tree(X, labels, attributes=None):
    X = X.reset_index(drop=True)
    labels = pd.Series(labels).reset_index(drop=True)

    if attributes is None:
        attributes = list(X.columns)

    node_majority_class = majority_class(labels) # Used as fallback. If this node gets stuck during prediction, predict this majoirty class

    if labels.nunique() == 1: # Stop case 1 : labels are pure
        prediction = labels.iloc[0]

        return TreeNode( # returns leaf node (predicts this class)
            is_leaf=True,
            prediction=prediction,
            majority_class=prediction
        )

    if len(attributes) == 0: # Stop case 2: no attributes left (no questions left to ask)
        return TreeNode( # returns a leaf node (predicting the majority class)
            is_leaf=True,
            prediction=node_majority_class,
            majority_class=node_majority_class
        )

    X_available_attributes = X[attributes]

    best_column, best_gain, _ = best_attribute( # find the best attribute
        X_available_attributes,
        labels
    )

    if best_gain == 0: # Stop case 3: best information gain = 0 means no attributre improves the split (splitting would be useless)
        return TreeNode( # returns a leaf node predicitng majority class
            is_leaf=True,
            prediction=node_majority_class,
            majority_class=node_majority_class
        )

    node = TreeNode(
        is_leaf=False,
        attribute=best_column,
        majority_class=node_majority_class
    )

    remaining_attributes = []

    for attribute in attributes:
        if attribute != best_column:
            remaining_attributes.append(attribute) # copies every attribute except the one just used

    attribute_values = X[best_column].unique() # get possible branch values

    for value in attribute_values:
        rows_with_this_value = X[best_column] == value #True/False mask

        child_X = X[rows_with_this_value].reset_index(drop=True) # creating subset for each value
        child_labels = labels[rows_with_this_value].reset_index(drop=True)

        child_node = build_tree( #recursive call
            child_X,
            child_labels,
            remaining_attributes
        )

        node.add_child(value, child_node)

    # Simplify this node into a leaf if all its child leaves make the same prediction
    child_predictions = []

    for child_node in node.children.values():
        if child_node.is_leaf:
            child_predictions.append(child_node.prediction)

    if len(child_predictions) == len(node.children):
        if len(set(child_predictions)) == 1:
            return TreeNode(
                is_leaf=True,
                prediction=child_predictions[0],
                majority_class=child_predictions[0]
            )
        
    return node

def print_tree(node, indent=""):
    if node.is_leaf:
        print(indent + f"Predict: {node.prediction}")
        return

    print(indent + f"Attribute: {node.attribute}")

    for attribute_value, child_node in node.children.items():
        print(indent + f"If {node.attribute} == {attribute_value}:")
        print_tree(child_node, indent + "    ")

def predict_one(tree, example):
    node = tree

    while not node.is_leaf:
        attribute = node.attribute

        attribute_value = example[attribute]

        if attribute_value in node.children:
            node = node.children[attribute_value]
        else:
            return node.majority_class

    return node.prediction


def predict(tree, X):
    predictions = []

    for index, row in X.iterrows():
        prediction = predict_one(tree, row)

        predictions.append(prediction)

    return predictions