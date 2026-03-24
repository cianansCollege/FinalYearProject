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

CSV_PATH = Path("/Users/cianan/Documents/College/GitHub/FYP/Prototype3/backend/training/training_minimal_clean_01.csv")

EXPERIMENTS_SCRIPTS_DIR = Path("/Users/cianan/Documents/College/GitHub/FYP/Experiments/AutoWav2VecIrish/scripts")
if str(EXPERIMENTS_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_SCRIPTS_DIR))

from model_defs import get_model
from task_defs import get_task
from pipeline_utils_wav2vec import build_feature_matrix

TASK_NAME = "ulster_vs_rest"
MODEL_NAME = "rf"


def main() -> None:
    df = pd.read_csv(CSV_PATH)

    required_cols = {"filepath", "speaker", "label"}
    missing_cols = sorted(c for c in required_cols if c not in df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {missing_cols}")

    task_fn = get_task(TASK_NAME)
    X_df, y = task_fn(df)

    if len(X_df) == 0:
        raise ValueError(f"No rows returned for task '{TASK_NAME}'")

    speakers = X_df["speaker"].astype(str).to_numpy()

    n_samples = len(X_df)
    n_speakers = int(pd.Series(speakers).nunique())
    n_classes = int(pd.Series(y).nunique())
    class_counts = pd.Series(y).value_counts().to_dict()

    print(f"Training task: {TASK_NAME}")
    print(f"Model: {MODEL_NAME}")
    print(f"Training CSV: {CSV_PATH}")
    print(f"Rows used: {n_samples}")
    print(f"Unique speakers used: {n_speakers}")
    print(f"Classes: {n_classes}")
    print(f"Class counts: {class_counts}")

    print("Building wav2vec embeddings...")
    X = build_feature_matrix(X_df)

    if len(X) == 0:
        raise ValueError("No valid feature rows were created.")

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(np.array(y)).astype(np.int64)

    model = get_model(MODEL_NAME)
    model.fit(X, y_encoded)

    artifact_prefix = f"wav2vec_{TASK_NAME}_{MODEL_NAME}"

    model_path = ARTIFACTS_DIR / f"{artifact_prefix}_model.joblib"
    le_path = ARTIFACTS_DIR / f"{artifact_prefix}_label_encoder.joblib"
    meta_path = ARTIFACTS_DIR / f"{artifact_prefix}_meta.json"

    joblib.dump(model, model_path)
    joblib.dump(label_encoder, le_path)

    metadata = {
        "task_name": TASK_NAME,
        "model_name": MODEL_NAME,
        "source_csv": str(CSV_PATH),
        "n_samples": n_samples,
        "n_speakers": n_speakers,
        "n_classes": n_classes,
        "class_counts": class_counts,
        "label_classes": label_encoder.classes_.tolist(),
        "feature_type": "wav2vec2-base_mean_pool",
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved model to: {model_path}")
    print(f"Saved label encoder to: {le_path}")
    print(f"Saved metadata to: {meta_path}")


if __name__ == "__main__":
    main()