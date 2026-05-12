"""Tree node representation used by the ID3 decision tree."""


class TreeNode:
    """Represent either a decision node or a leaf node."""

    def __init__(
        self,
        is_leaf=False,
        prediction=None,
        attribute=None,
        majority_class=None,
    ):
        """Create a tree node.

        Args:
            is_leaf: Whether this node stores a final prediction.
            prediction: Class returned by a leaf node.
            attribute: Attribute tested by a decision node.
            majority_class: Fallback class for unseen branch values.
        """
        self.is_leaf = is_leaf
        self.prediction = prediction
        self.attribute = attribute
        self.children = {}
        self.majority_class = majority_class

    @classmethod
    def leaf(cls, prediction):
        """Create a leaf node that always predicts one class."""
        return cls(is_leaf=True, prediction=prediction, majority_class=prediction)

    @classmethod
    def decision(cls, attribute, majority_class):
        """Create a decision node that tests one attribute."""
        return cls(
            is_leaf=False,
            attribute=attribute,
            majority_class=majority_class,
        )

    def add_child(self, attribute_value, child_node):
        """Attach a child node for one attribute value."""
        self.children[attribute_value] = child_node

    def __repr__(self):
        if self.is_leaf:
            return f"Leaf(prediction={self.prediction})"

        children = list(self.children.keys())
        return f"DecisionNode(attribute={self.attribute}, children={children})"
