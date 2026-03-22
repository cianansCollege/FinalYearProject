"""
Reusable experiment pipeline utilities.

Handles:
- metadata loading
- MFCC feature extraction
- speaker-safe cross validation
- model training
- metric calculation
"""

import numpy as np
import pandas as pd
import librosa

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
)


# --------------------------------------------------
# Metadata loading
# --------------------------------------------------

def load_metadata(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = {"filepath", "speaker", "label", "dataset"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


# --------------------------------------------------
# Feature extraction
# --------------------------------------------------

def extract_mfcc_features(filepath: str, n_mfcc: int = 13):
    """
    Extract enriched MFCC-based summary statistics from audio file.
    """

    y, sr = librosa.load(filepath, sr=16000, mono=True)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=n_mfcc,
    )

    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)

    zcr = librosa.feature.zero_crossing_rate(y)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

    features = np.concatenate([
        np.mean(mfcc, axis=1),
        np.std(mfcc, axis=1),
        np.mean(delta, axis=1),
        np.std(delta, axis=1),
        np.mean(delta2, axis=1),
        np.std(delta2, axis=1),
        np.mean(zcr, axis=1),
        np.std(zcr, axis=1),
        np.mean(centroid, axis=1),
        np.std(centroid, axis=1),
        np.mean(rolloff, axis=1),
        np.std(rolloff, axis=1),
    ])

    return features.astype(np.float32)


def build_feature_matrix(X_df: pd.DataFrame):
    """
    Convert dataframe of filepaths to feature matrix.
    """

    features = []

    for path in X_df["filepath"]:
        feat = extract_mfcc_features(path)
        features.append(feat)

    X = np.vstack(features)

    return X


# --------------------------------------------------
# Cross validation
# --------------------------------------------------

def run_cv_experiment(X, y, speakers, model, n_splits=5):
    """
    Run StratifiedGroupKFold cross-validation with a safe number of splits.
    """

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    class_counts = pd.Series(y_encoded).value_counts()
    min_class_count = int(class_counts.min())
    n_unique_speakers = int(pd.Series(speakers).nunique())

    actual_splits = min(n_splits, min_class_count, n_unique_speakers)

    if actual_splits < 2:
        raise ValueError(
            "Not enough data for StratifiedGroupKFold: "
            f"min_class_count={min_class_count}, "
            f"unique_speakers={n_unique_speakers}"
        )

    cv = StratifiedGroupKFold(
        n_splits=actual_splits,
        shuffle=True,
        random_state=42,
    )

    fold_results = []

    for fold, (train_idx, test_idx) in enumerate(
        cv.split(X, y_encoded, groups=speakers),
        start=1,
    ):
        X_train = X[train_idx]
        X_test = X[test_idx]

        y_train = y_encoded[train_idx]
        y_test = y_encoded[test_idx]

        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        bal_acc = balanced_accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="macro")

        fold_results.append({
            "fold": fold,
            "accuracy": acc,
            "balanced_accuracy": bal_acc,
            "macro_f1": f1,
        })

    return fold_results, le


# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

def summarize_results(fold_results):
    df = pd.DataFrame(fold_results)

    summary = {
        "accuracy_mean": df["accuracy"].mean(),
        "accuracy_std": df["accuracy"].std(),
        "balanced_accuracy_mean": df["balanced_accuracy"].mean(),
        "macro_f1_mean": df["macro_f1"].mean(),
    }

    return summary