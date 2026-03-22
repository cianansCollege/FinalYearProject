"""
Defines Irish wav2vec experiment tasks.
"""

import pandas as pd


TASKS = {
    "province_4way": "task_province_4way",
    "ulster_vs_rest": "task_ulster_vs_rest",
    "leinster_vs_rest": "task_leinster_vs_rest",
    "ulster_leinster_rest": "task_ulster_leinster_rest",
    "dail_vs_ni": "task_dail_vs_ni",
}


def _basic_xy(df: pd.DataFrame, target_col: str = "label"):
    X_df = df[["filepath", "speaker"]].copy()
    y = df[target_col].copy()
    return X_df, y


def task_province_4way(df: pd.DataFrame):
    keep = ["Connacht", "Leinster", "Munster", "Ulster"]
    df = df[df["label"].isin(keep)].copy()
    return _basic_xy(df)


def task_ulster_vs_rest(df: pd.DataFrame):
    keep = ["Connacht", "Leinster", "Munster", "Ulster"]
    df = df[df["label"].isin(keep)].copy()
    df["target"] = df["label"].apply(
        lambda x: "Ulster" if x == "Ulster" else "Rest"
    )
    return _basic_xy(df, "target")


def task_leinster_vs_rest(df: pd.DataFrame):
    keep = ["Connacht", "Leinster", "Munster", "Ulster"]
    df = df[df["label"].isin(keep)].copy()
    df["target"] = df["label"].apply(
        lambda x: "Leinster" if x == "Leinster" else "Rest"
    )
    return _basic_xy(df, "target")


def task_ulster_leinster_rest(df: pd.DataFrame):
    keep = ["Connacht", "Leinster", "Munster", "Ulster"]
    df = df[df["label"].isin(keep)].copy()
    df["target"] = df["label"].apply(
        lambda x: x if x in ["Ulster", "Leinster"] else "Rest"
    )
    return _basic_xy(df, "target")


def task_dail_vs_ni(df: pd.DataFrame):
    df = df[df["label"].isin(["DAIL", "NI"])].copy()
    return _basic_xy(df)


def get_task(task_name: str):
    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}")
    return globals()[TASKS[task_name]]