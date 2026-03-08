from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import librosa
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder


ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def extract_mfcc_summary_features(file_path: str, n_mfcc: int = 13) -> np.ndarray:
    waveform, sr = librosa.load(file_path, sr=16000, mono=True)

    mfcc = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=n_mfcc)
    mfcc_means = np.mean(mfcc, axis=1)
    mfcc_stds = np.std(mfcc, axis=1)

    return np.concatenate([mfcc_means, mfcc_stds]).astype(np.float32)


def main() -> None:
    csv_path = Path("training_data.csv")
    df = pd.read_csv(csv_path)

    # Expected columns:
    # filepath,label
    X = []
    y = []

    for _, row in df.iterrows():
        try:
            features = extract_mfcc_summary_features(row["filepath"])
            X.append(features)
            y.append(row["label"])
        except Exception as exc:
            print(f"Skipping {row['filepath']}: {exc}")

    X = np.array(X)
    y = np.array(y)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    model = LogisticRegression(max_iter=2000)
    model.fit(X, y_encoded)

    joblib.dump(model, ARTIFACTS_DIR / "mfcc_logreg_model.joblib")
    joblib.dump(label_encoder, ARTIFACTS_DIR / "label_encoder.joblib")

    print("Saved model artifacts to backend/artifacts/")


if __name__ == "__main__":
    main()