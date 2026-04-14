from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

BACKEND_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = Path("/Users/cianan/Documents/College/GitHub/FYP/Data/Dail_NI_Metadata/training_minimal_clean.csv")

EXPERIMENTS_SCRIPTS_DIR = Path("/Users/cianan/Documents/College/GitHub/FYP/Experiments/AutoWav2VecIrish/scripts")
if str(EXPERIMENTS_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_SCRIPTS_DIR))

from model_defs import get_model
from task_defs import get_task
from pipeline_utils_wav2vec import build_feature_matrix


DEPLOY_CONFIGS = [
    ("ulster_vs_rest", "rf"),
    ("leinster_vs_rest", "logreg"),
    ("ulster_leinster_rest", "logreg"),
    ("province_4way", "logreg"),
]


def train_one(df: pd.DataFrame, task_name: str, model_name: str):
    task_fn = get_task(task_name)
    X_df, y = task_fn(df)

    if len(X_df) == 0:
        raise ValueError(f"No rows returned for task '{task_name}'")

    print(f"\n=== Training {task_name} | {model_name} ===")

    X = build_feature_matrix(X_df)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(np.array(y)).astype(np.int64)

    model = get_model(model_name)
    model.fit(X, y_encoded)

    artifact_prefix = f"wav2vec_{task_name}_{model_name}"

    model_path = ARTIFACTS_DIR / f"{artifact_prefix}_model.joblib"
    le_path = ARTIFACTS_DIR / f"{artifact_prefix}_label_encoder.joblib"
    meta_path = ARTIFACTS_DIR / f"{artifact_prefix}_meta.json"

    joblib.dump(model, model_path)
    joblib.dump(label_encoder, le_path)

    metadata = {
        "task_name": task_name,
        "model_name": model_name,
        "label_classes": label_encoder.classes_.tolist(),
        "feature_type": "wav2vec2-base_mean_pool",
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved: {artifact_prefix}")


def main():
    df = pd.read_csv(CSV_PATH)

    for task_name, model_name in DEPLOY_CONFIGS:
        try:
            train_one(df, task_name, model_name)
        except Exception as e:
            print(f"FAILED: {task_name} | {model_name} -> {e}")


if __name__ == "__main__":
    main()