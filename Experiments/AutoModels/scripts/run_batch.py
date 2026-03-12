"""
Runs the full Irish accent experiment batch.

Usage:
    python3 run_batch.py

This script:
- loads metadata
- loops through all tasks
- loops through all models
- extracts MFCC features
- runs speaker-safe CV
- saves per-fold and summary results
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from model_defs import MODELS, get_model
from pipeline_utils import (
    build_feature_matrix,
    load_metadata,
    run_cv_experiment,
    summarize_results,
)
from task_defs import TASKS, get_task


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path("/Users/cianan/Documents/College/GitHub/FYP/Experiments/Auto32Models")
CSV_PATH = Path("/Users/cianan/Documents/College/GitHub/FYP/Data/Dail_NI_Metadata/training_minimal_clean.csv")

RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def run_single_experiment(
    metadata_df: pd.DataFrame,
    task_name: str,
    model_name: str,
) -> dict:
    print(f"\n=== Running task={task_name} | model={model_name} ===")

    task_fn = get_task(task_name)
    model = get_model(model_name)

    X_df, y = task_fn(metadata_df)

    if len(X_df) == 0:
        raise ValueError(f"No rows returned for task '{task_name}'")

    speakers = X_df["speaker"].to_numpy()

    class_counts = pd.Series(y).value_counts().to_dict()
    n_classes = len(pd.Series(y).unique())
    n_samples = len(X_df)
    n_speakers = X_df["speaker"].nunique()

    print(f"Samples: {n_samples}")
    print(f"Speakers: {n_speakers}")
    print(f"Classes: {n_classes}")
    print(f"Class counts: {class_counts}")

    X = build_feature_matrix(X_df)

    fold_results, label_encoder = run_cv_experiment(
        X=X,
        y=y,
        speakers=speakers,
        model=model,
        n_splits=5,
    )

    summary = summarize_results(fold_results)

    result = {
        "task_name": task_name,
        "model_name": model_name,
        "n_samples": n_samples,
        "n_speakers": n_speakers,
        "n_classes": n_classes,
        "class_counts": class_counts,
        "label_classes": label_encoder.classes_.tolist(),
        **summary,
    }

    experiment_dir = RESULTS_DIR / task_name / model_name
    experiment_dir.mkdir(parents=True, exist_ok=True)

    fold_df = pd.DataFrame(fold_results)
    fold_df.to_csv(experiment_dir / "fold_results.csv", index=False)

    save_json(experiment_dir / "summary.json", result)

    print(
        "Done:",
        f"acc={result['accuracy_mean']:.4f}",
        f"bal_acc={result['balanced_accuracy_mean']:.4f}",
        f"macro_f1={result['macro_f1_mean']:.4f}",
    )

    return result


# --------------------------------------------------
# Main
# --------------------------------------------------

def main() -> None:
    print("Loading metadata...")
    metadata_df = load_metadata(str(CSV_PATH))
    print(f"Loaded {len(metadata_df)} rows from {CSV_PATH}")

    all_results: list[dict] = []
    failures: list[dict] = []

    for task_name in TASKS.keys():
        for model_name in MODELS.keys():
            try:
                result = run_single_experiment(
                    metadata_df=metadata_df,
                    task_name=task_name,
                    model_name=model_name,
                )
                all_results.append(result)

            except Exception as exc:
                failure = {
                    "task_name": task_name,
                    "model_name": model_name,
                    "error": str(exc),
                }
                failures.append(failure)
                print(f"FAILED: task={task_name} model={model_name} error={exc}")

    if all_results:
        summary_df = pd.DataFrame(all_results)

        summary_df = summary_df.sort_values(
            by=["task_name", "balanced_accuracy_mean", "macro_f1_mean"],
            ascending=[True, False, False],
        )

        summary_df.to_csv(RESULTS_DIR / "irish_model_summary.csv", index=False)
        print(f"\nSaved summary CSV to {RESULTS_DIR / 'irish_model_summary.csv'}")

    if failures:
        failure_df = pd.DataFrame(failures)
        failure_df.to_csv(LOGS_DIR / "failures.csv", index=False)
        print(f"Saved failures log to {LOGS_DIR / 'failures.csv'}")

    print("\nBatch complete.")
    print(f"Successful experiments: {len(all_results)}")
    print(f"Failed experiments: {len(failures)}")


if __name__ == "__main__":
    main()