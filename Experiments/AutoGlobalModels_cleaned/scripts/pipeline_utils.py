import numpy as np
import pandas as pd
import librosa

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score


def load_metadata(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = {"filepath", "speaker", "label", "dataset"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def extract_features(filepath: str, n_mfcc: int = 13):
    y, sr = librosa.load(filepath, sr=16000, mono=True)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)

    zcr = librosa.feature.zero_crossing_rate(y)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

    features = np.concatenate([
        np.mean(mfcc, axis=1), np.std(mfcc, axis=1),
        np.mean(delta, axis=1), np.std(delta, axis=1),
        np.mean(delta2, axis=1), np.std(delta2, axis=1),
        np.mean(zcr, axis=1), np.std(zcr, axis=1),
        np.mean(centroid, axis=1), np.std(centroid, axis=1),
        np.mean(rolloff, axis=1), np.std(rolloff, axis=1),
    ])

    return features


def build_feature_matrix(df):
    return np.vstack([extract_features(p) for p in df["filepath"]])


def run_cv_experiment(X, y, speakers, model, n_splits=5):
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    min_class = pd.Series(y_encoded).value_counts().min()
    n_speakers = pd.Series(speakers).nunique()

    n_splits = min(n_splits, min_class, n_speakers)

    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)

    results = []

    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y_encoded, speakers), 1):
        model.fit(X[train_idx], y_encoded[train_idx])
        preds = model.predict(X[test_idx])

        results.append({
            "fold": fold,
            "accuracy": accuracy_score(y_encoded[test_idx], preds),
            "balanced_accuracy": balanced_accuracy_score(y_encoded[test_idx], preds),
            "macro_f1": f1_score(y_encoded[test_idx], preds, average="macro"),
        })

    return results, le


def summarize_results(results):
    df = pd.DataFrame(results)

    return {
        "accuracy_mean": df["accuracy"].mean(),
        "accuracy_std": df["accuracy"].std(),
        "balanced_accuracy_mean": df["balanced_accuracy"].mean(),
        "macro_f1_mean": df["macro_f1"].mean(),
    }