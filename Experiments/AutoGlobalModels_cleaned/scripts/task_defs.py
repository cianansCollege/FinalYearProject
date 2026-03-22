"""
Defines cleaned global Common Voice experiment tasks.
"""

import pandas as pd


TASKS = {
    "roi_vs_ni": "task_roi_vs_ni",
    "roi_vs_uk": "task_roi_vs_uk",
    "ni_vs_uk": "task_ni_vs_uk",
    "roi_ni_uk_3way": "task_roi_ni_uk_3way",
    "five_way_global": "task_five_way_global",
}


def _basic_xy(df: pd.DataFrame, target_col: str = "label"):
    X_df = df[["filepath", "speaker"]].copy()
    y = df[target_col].copy()
    return X_df, y


def task_roi_vs_ni(df: pd.DataFrame):
    df = df[df["label"].isin(["Ireland", "Northern Ireland"])].copy()
    return _basic_xy(df)


def task_roi_vs_uk(df: pd.DataFrame):
    df = df[df["label"].isin(["Ireland", "UK"])].copy()
    return _basic_xy(df)


def task_ni_vs_uk(df: pd.DataFrame):
    df = df[df["label"].isin(["Northern Ireland", "UK"])].copy()
    return _basic_xy(df)


def task_roi_ni_uk_3way(df: pd.DataFrame):
    df = df[df["label"].isin(["Ireland", "Northern Ireland", "UK"])].copy()
    return _basic_xy(df)


def task_five_way_global(df: pd.DataFrame):
    keep = ["Ireland", "Northern Ireland", "UK", "NorthAmerican", "Oceania"]
    df = df[df["label"].isin(keep)].copy()
    return _basic_xy(df)


def get_task(task_name: str):
    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}")
    return globals()[TASKS[task_name]]