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
    Extract MFCC summary statistics from audio file.
    """

    y, sr = librosa.load(filepath, sr=16000)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=n_mfcc,
    )

    # summarize MFCC across time
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    features = np.concatenate([mfcc_mean, mfcc_std])

    return features


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
    Run StratifiedGroupKFold cross-validation.
    """

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    cv = StratifiedGroupKFold(
        n_splits=n_splits,
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