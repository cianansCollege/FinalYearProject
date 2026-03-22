"""
Defines Irish wav2vec experiment tasks.
"""

import pandas as pd


TASKS = {
    "ulster_vs_rest": "task_ulster_vs_rest",
    "province_4way": "task_province_4way",
}


def _basic_xy(df: pd.DataFrame, target_col: str = "label"):
    X_df = df[["filepath", "speaker"]].copy()
    y = df[target_col].copy()
    return X_df, y


def task_ulster_vs_rest(df: pd.DataFrame):
    df = df[df["label"].isin(["Ulster", "Leinster", "Munster", "Connacht"])].copy()

    df["target"] = df["label"].apply(
        lambda x: "Ulster" if x == "Ulster" else "Rest"
    )

    return _basic_xy(df, target_col="target")


def task_province_4way(df: pd.DataFrame):
    keep = ["Connacht", "Leinster", "Munster", "Ulster"]
    df = df[df["label"].isin(keep)].copy()
    return _basic_xy(df)


def get_task(task_name: str):
    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}")
    return globals()[TASKS[task_name]]