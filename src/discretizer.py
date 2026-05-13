"""Funções auxiliares para discretizar características
numéricas em categorias discretas."""

import numpy as np
import pandas as pd


def learn_bins(X_train, columns, n_bins, method="equal_width"):
    valid_methods = ["equal_width", "equal_frequency"]

    if method not in valid_methods:
        raise ValueError(
            f"Invalid method: {method}. Choose 'equal_width' or 'equal_frequency'."
        )

    if n_bins < 2:
        raise ValueError("n_bins must be at least 2.")

    bin_rules = {}

    for column in columns:
        values = X_train[column]

        if method == "equal_width":
            min_value = values.min()
            max_value = values.max()

            bin_width = (max_value - min_value) / n_bins

            edges = []
            for i in range(1, n_bins):
                edge = min_value + i * bin_width
                edges.append(edge)

        elif method == "equal_frequency":
            sorted_values = values.sort_values().reset_index(drop=True)

            edges = []
            for i in range(1, n_bins):
                number_of_values = len(sorted_values)
                fraction_of_data = i / n_bins
                exact_position = number_of_values * fraction_of_data
                position = int(exact_position)

                edge = sorted_values.iloc[position]
                edges.append(edge)

        edges = sorted(set(edges))

        labels = []
        for i in range(len(edges) + 1):
            labels.append(f"bin_{i}")

        bin_rules[column] = {
            "edges": edges,
            "labels": labels,
            "method": method,
            "requested_n_bins": n_bins,
            "actual_n_bins": len(labels),
        }

    return bin_rules


def apply_bins(X, bin_rules):
    X_discrete = X.copy()

    for column, rules in bin_rules.items():
        edges = rules["edges"]
        labels = rules["labels"]

        bins = [-np.inf] + edges + [np.inf]

        X_discrete[column] = pd.cut(
            X_discrete[column],
            bins=bins,
            labels=labels,
            include_lowest=True,
        )

    return X_discrete
