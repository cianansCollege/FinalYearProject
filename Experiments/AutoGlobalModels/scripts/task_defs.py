"""
Defines global Common Voice experiment tasks.
"""

import pandas as pd


TASKS = {
    "ireland_vs_rest": "task_ireland_vs_rest",
    "uk_vs_ireland": "task_uk_vs_ireland",
    "ireland_vs_northamerican": "task_ireland_vs_northamerican",
    "ireland_vs_oceania": "task_ireland_vs_oceania",
    "uk_vs_rest_non_ireland": "task_uk_vs_rest_non_ireland",
    "northamerican_vs_oceania": "task_northamerican_vs_oceania",
    "four_way_global": "task_four_way_global",
    "ireland_uk_vs_rest": "task_ireland_uk_vs_rest",
}


def _basic_xy(df: pd.DataFrame, target_col: str = "label"):
    X_df = df[["filepath", "speaker"]].copy()
    y = df[target_col].copy()
    return X_df, y


def task_ireland_vs_rest(df: pd.DataFrame):
    keep = ["Ireland", "UK", "NorthAmerican", "Oceania"]
    df = df[df["label"].isin(keep)].copy()
    df["target"] = df["label"].apply(lambda x: "Ireland" if x == "Ireland" else "Rest")
    return _basic_xy(df, "target")


def task_uk_vs_ireland(df: pd.DataFrame):
    df = df[df["label"].isin(["UK", "Ireland"])].copy()
    return _basic_xy(df)


def task_ireland_vs_northamerican(df: pd.DataFrame):
    df = df[df["label"].isin(["Ireland", "NorthAmerican"])].copy()
    return _basic_xy(df)


def task_ireland_vs_oceania(df: pd.DataFrame):
    df = df[df["label"].isin(["Ireland", "Oceania"])].copy()
    return _basic_xy(df)


def task_uk_vs_rest_non_ireland(df: pd.DataFrame):
    keep = ["UK", "NorthAmerican", "Oceania"]
    df = df[df["label"].isin(keep)].copy()
    df["target"] = df["label"].apply(lambda x: "UK" if x == "UK" else "Rest")
    return _basic_xy(df, "target")


def task_northamerican_vs_oceania(df: pd.DataFrame):
    df = df[df["label"].isin(["NorthAmerican", "Oceania"])].copy()
    return _basic_xy(df)


def task_four_way_global(df: pd.DataFrame):
    keep = ["Ireland", "UK", "NorthAmerican", "Oceania"]
    df = df[df["label"].isin(keep)].copy()
    return _basic_xy(df)


def task_ireland_uk_vs_rest(df: pd.DataFrame):
    keep = ["Ireland", "UK", "NorthAmerican", "Oceania"]
    df = df[df["label"].isin(keep)].copy()
    df["target"] = df["label"].apply(
        lambda x: "Ireland_UK" if x in ["Ireland", "UK"] else "Rest"
    )
    return _basic_xy(df, "target")


def get_task(task_name: str):
    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}")
    return globals()[TASKS[task_name]]