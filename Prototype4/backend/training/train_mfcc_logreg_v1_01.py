"""Trains the MFCC-based classifier used by the live backend plugin.

This script belongs to the offline training pipeline rather than the running
application. It reads the prepared metadata CSV, extracts MFCC features from
each clip, evaluates the model with grouped cross-validation, and saves the
artefacts loaded by `backend/plugins/mfcc_logreg_v1_01.py`.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import librosa
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler


BACKEND_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = BACKEND_DIR / "training" / "training_minimal_clean_01.csv"


def extract_mfcc_summary_features(file_path: str, n_mfcc: int = 13) -> np.ndarray:
    # Mirror the runtime MFCC feature shape so training and inference stay aligned.
    waveform, sr = librosa.load(file_path, sr=16000, mono=True)

    mfcc = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=n_mfcc)
    mfcc_means = np.mean(mfcc, axis=1)
    mfcc_stds = np.std(mfcc, axis=1)

    return np.concatenate([mfcc_means, mfcc_stds]).astype(np.float32)


def main() -> None:
    # Read the reduced training metadata generated for this experiment.
    df = pd.read_csv(CSV_PATH)

    # Expected columns:
    # filepath,speaker,label
    required_cols = {"filepath", "speaker", "label"}
    missing_cols = sorted(c for c in required_cols if c not in df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {missing_cols}")

    # Accumulate features, labels, and speaker groups for grouped validation.
    X = []
    y = []
    groups = []

    for _, row in df.iterrows():
        try:
            features = extract_mfcc_summary_features(row["filepath"])
            X.append(features)
            y.append(row["label"])
            groups.append(str(row["speaker"]))
        except Exception as exc:
            print(f"Skipping {row['filepath']}: {exc}")

    if not X:
        raise ValueError("No valid training rows were loaded.")

    X = np.array(X)
    y = np.array(y)
    groups = np.array(groups, dtype=object)

    # Encode province labels into integer classes for scikit-learn.
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y).astype(np.int64)

    min_class_count = int(pd.Series(y).value_counts().min())
    n_unique_speakers = int(pd.Series(groups).nunique())
    n_splits = min(5, min_class_count, n_unique_speakers)

    if n_splits < 2:
        raise ValueError(
            "Not enough data for StratifiedGroupKFold. "
            f"min_class_count={min_class_count}, unique_speakers={n_unique_speakers}"
        )

    # Keep speakers separated across folds to reduce speaker leakage.
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_scores: list[float] = []

    for fold, (train_idx, val_idx) in enumerate(cv.split(X, y, groups=groups), start=1):
        fold_model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=5000)),
        ])

        fold_model.fit(X[train_idx], y_encoded[train_idx])
        fold_acc = float(fold_model.score(X[val_idx], y_encoded[val_idx]))
        fold_scores.append(fold_acc)

        print(
            f"Fold {fold}/{n_splits}: "
            f"train={len(train_idx)} val={len(val_idx)} "
            f"acc={fold_acc:.4f}"
        )

    # Refit on the full dataset before exporting the deployable artefacts.
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=5000)),
    ])

    model.fit(X, y_encoded)

    joblib.dump(model, ARTIFACTS_DIR / "mfcc_logreg_v1_model_01.joblib")
    joblib.dump(label_encoder, ARTIFACTS_DIR / "mfcc_logreg_v1_label_encoder_01.joblib")

    print(f"Training CSV: {CSV_PATH}")
    print(f"Rows used: {len(X)}")
    print(f"Unique speakers used: {n_unique_speakers}")
    print(f"StratifiedGroupKFold splits: {n_splits}")
    print(f"CV mean acc: {np.mean(fold_scores):.4f}")
    print(f"CV std acc: {np.std(fold_scores):.4f}")
    print(f"Saved model to: {ARTIFACTS_DIR / 'mfcc_logreg_v1_model_01.joblib'}")
    print(f"Saved label encoder to: {ARTIFACTS_DIR / 'mfcc_logreg_v1_label_encoder_01.joblib'}")


if __name__ == "__main__":
    main()
