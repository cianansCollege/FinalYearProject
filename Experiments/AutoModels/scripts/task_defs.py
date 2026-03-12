"""
Defines all experiment tasks.

Each task takes the full metadata dataframe and returns:
    X_df  -> filtered dataframe containing filepath + speaker
    y     -> target labels
"""

import pandas as pd


# -----------------------------------------------------
# Task registry
# -----------------------------------------------------

TASKS = {
    "province_4way": "task_province_4way",
    "dail_only_province": "task_dail_only_province",
    "dail_vs_ni": "task_dail_vs_ni",
    "ulster_leinster_rest": "task_ulster_leinster_rest",
    "ulster_vs_rest": "task_ulster_vs_rest",
    "leinster_vs_rest": "task_leinster_vs_rest",
}


# -----------------------------------------------------
# Task implementations
# -----------------------------------------------------

def task_province_4way(df: pd.DataFrame):
    """
    4-way province classification
    Drops 'Other'
    """

    df = df[df["label"] != "Other"].copy()

    X_df = df[["filepath", "speaker"]]
    y = df["label"]

    return X_df, y


def task_dail_only_province(df: pd.DataFrame):
    """
    Province classification using only Dáil data
    """

    df = df[(df["dataset"] == "DAIL") & (df["label"] != "Other")].copy()

    X_df = df[["filepath", "speaker"]]
    y = df["label"]

    return X_df, y


def task_dail_vs_ni(df: pd.DataFrame):
    """
    Binary dataset classification
    """

    X_df = df[["filepath", "speaker"]]
    y = df["dataset"]

    return X_df, y


def task_ulster_leinster_rest(df: pd.DataFrame):
    """
    3-class regional classification
    """

    df = df[df["label"] != "Other"].copy()

    def map_label(label):
        if label == "Ulster":
            return "Ulster"
        elif label == "Leinster":
            return "Leinster"
        else:
            return "Rest"

    df["target"] = df["label"].apply(map_label)

    X_df = df[["filepath", "speaker"]]
    y = df["target"]

    return X_df, y


def task_ulster_vs_rest(df: pd.DataFrame):
    """
    Binary classification: Ulster vs Rest
    """

    df = df[df["label"] != "Other"].copy()

    df["target"] = df["label"].apply(
        lambda x: "Ulster" if x == "Ulster" else "Rest"
    )

    X_df = df[["filepath", "speaker"]]
    y = df["target"]

    return X_df, y


def task_leinster_vs_rest(df: pd.DataFrame):
    """
    Binary classification: Leinster vs Rest
    """

    df = df[df["label"] != "Other"].copy()

    df["target"] = df["label"].apply(
        lambda x: "Leinster" if x == "Leinster" else "Rest"
    )

    X_df = df[["filepath", "speaker"]]
    y = df["target"]

    return X_df, y


# -----------------------------------------------------
# Helper
# -----------------------------------------------------

def get_task(task_name: str):
    """
    Returns task function by name
    """

    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}")

    return globals()[TASKS[task_name]]