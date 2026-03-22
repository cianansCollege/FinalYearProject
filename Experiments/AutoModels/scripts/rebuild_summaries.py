from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


RESULTS_DIR = Path("/Users/cianan/Documents/College/GitHub/FYP/Experiments/AutoModels/results")

IRISH_TASKS = {
    "province_4way",
    "dail_only_province",
    "dail_vs_ni",
    "ulster_leinster_rest",
    "ulster_vs_rest",
    "leinster_vs_rest",
}

GLOBAL_TASKS = {
    "global_4way",
    "ireland_vs_rest",
    "uk_vs_ireland",
}


def classify_experiment_scope(task_name: str) -> str:
    if task_name in IRISH_TASKS:
        return "irish"
    if task_name in GLOBAL_TASKS:
        return "global"
    return "unknown"


def load_all_summaries(results_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []

    for summary_file in results_dir.rglob("summary.json"):
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["summary_path"] = str(summary_file)
            data["scope"] = classify_experiment_scope(data.get("task_name", ""))
            rows.append(data)

        except Exception as exc:
            print(f"Failed to read {summary_file}: {exc}")

    if not rows:
        raise RuntimeError("No summary.json files found.")

    df = pd.DataFrame(rows)
    return df


def sort_summary(df: pd.DataFrame) -> pd.DataFrame:
    sort_cols = [c for c in ["task_name", "balanced_accuracy_mean", "macro_f1_mean"] if c in df.columns]
    if not sort_cols:
        return df

    ascending = []
    for col in sort_cols:
        if col == "task_name":
            ascending.append(True)
        else:
            ascending.append(False)

    return df.sort_values(sort_cols, ascending=ascending)


def save_outputs(df: pd.DataFrame, results_dir: Path) -> None:
    all_path = results_dir / "all_model_summary.csv"
    irish_path = results_dir / "irish_model_summary.csv"
    global_path = results_dir / "global_model_summary.csv"
    unknown_path = results_dir / "unknown_model_summary.csv"

    sort_summary(df).to_csv(all_path, index=False)

    df_irish = df[df["scope"] == "irish"].copy()
    df_global = df[df["scope"] == "global"].copy()
    df_unknown = df[df["scope"] == "unknown"].copy()

    sort_summary(df_irish).to_csv(irish_path, index=False)
    sort_summary(df_global).to_csv(global_path, index=False)

    if len(df_unknown) > 0:
        sort_summary(df_unknown).to_csv(unknown_path, index=False)

    print(f"Saved: {all_path}")
    print(f"Saved: {irish_path}")
    print(f"Saved: {global_path}")
    if len(df_unknown) > 0:
        print(f"Saved: {unknown_path}")

    print("\nCounts by scope:")
    print(df["scope"].value_counts(dropna=False).to_string())

    print("\nTasks found:")
    if "task_name" in df.columns:
        for task in sorted(df["task_name"].dropna().unique().tolist()):
            print(f"- {task}")


def main() -> None:
    print(f"Scanning: {RESULTS_DIR}")
    df = load_all_summaries(RESULTS_DIR)

    print(f"Loaded {len(df)} experiment summaries.")
    save_outputs(df, RESULTS_DIR)


if __name__ == "__main__":
    main()