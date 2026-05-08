"""Funções auxiliares para visualizar árvores de decisão ID3."""

# takes 'unsafe' text and returns Graphviz-safe text
def escape_dot_text(text):
    text = str(text)

    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')

    return text


def tree_to_dot(tree):
    lines = []

    lines.append("digraph DecisionTree {")
    lines.append("    rankdir=TB;")
    lines.append('    node [fontname="Arial"];')
    lines.append('    edge [fontname="Arial"];')

    counter = [0]

    def add_node(node):
        node_id = f"node_{counter[0]}"
        counter[0] += 1

        if node.is_leaf:
            label = f"Predict: {node.prediction}"
            label = escape_dot_text(label)

            lines.append(
                f'    {node_id} [label="{label}", shape=box];'
            )

            return node_id

        label = f"Attribute: {node.attribute}"
        label = escape_dot_text(label)

        lines.append(
            f'    {node_id} [label="{label}", shape=ellipse];'
        )

        for attribute_value, child_node in node.children.items():
            child_id = add_node(child_node)

            edge_label = escape_dot_text(attribute_value)

            lines.append(
                f'    {node_id} -> {child_id} [label="{edge_label}"];'
            )

        return node_id

    add_node(tree)

    lines.append("}")

    dot_text = "\n".join(lines)

    return dot_text


def display_tree(tree):
    dot_text = tree_to_dot(tree)

    try:
        from graphviz import Source

        graph = Source(dot_text)

        return graph

    except ImportError:
        print("The graphviz Python package is not installed.")
        print("Here is the DOT text instead:")
        print(dot_text)

        return None


def save_dot(tree, filename):
    dot_text = tree_to_dot(tree)

    with open(filename, "w", encoding="utf-8") as file:
        file.write(dot_text)