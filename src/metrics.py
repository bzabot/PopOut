"""Funções auxiliares para calcular métricas usadas pelo algoritmo ID3."""

import numpy as np
import pandas as pd


def entropy(labels):
    labels = pd.Series(labels)

    probabilities = labels.value_counts(normalize=True)

    total_entropy = 0.0

    for probability in probabilities:
        total_entropy += -probability * np.log2(probability)

    return float(total_entropy)


def conditional_entropy(attribute_column, labels):
    attribute_column = pd.Series(attribute_column).reset_index(drop=True)
    labels = pd.Series(labels).reset_index(drop=True)

    total_rows = len(labels)

    total_conditional_entropy = 0.0

    attribute_values = attribute_column.unique()

    for value in attribute_values:
        rows_with_this_value = attribute_column == value

        labels_for_this_value = labels[rows_with_this_value]

        weight = len(labels_for_this_value) / total_rows

        entropy_for_this_value = entropy(labels_for_this_value)

        total_conditional_entropy += weight * entropy_for_this_value

    return float(total_conditional_entropy)

def information_gain(attribute_column, labels):
    entropy_before_split = entropy(labels)

    entropy_after_split = conditional_entropy(attribute_column, labels)

    gain = entropy_before_split - entropy_after_split

    return float(gain)

def best_attribute(X, labels):
    gains = {}

    best_column = None
    best_gain = -1

    for column in X.columns:
        gain = information_gain(X[column], labels)

        gains[column] = gain

        if gain > best_gain:
            best_gain = gain
            best_column = column

    return best_column, best_gain, gains