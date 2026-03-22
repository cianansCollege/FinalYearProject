"""
Reusable wav2vec experiment pipeline utilities.

- metadata loading
- wav2vec embedding extraction
- speaker-safe CV
- metric calculation
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import librosa
import torch

from transformers import Wav2Vec2Model, Wav2Vec2Processor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME = "facebook/wav2vec2-base"

_processor = None
_wav2vec_model = None


def get_wav2vec_components():
    global _processor, _wav2vec_model

    if _processor is None:
        _processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)

    if _wav2vec_model is None:
        _wav2vec_model = Wav2Vec2Model.from_pretrained(MODEL_NAME)
        _wav2vec_model.to(DEVICE)
        _wav2vec_model.eval()

    return _processor, _wav2vec_model


def load_metadata(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = {"filepath", "speaker", "label"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def extract_wav2vec_embedding(filepath: str) -> np.ndarray:
    processor, model = get_wav2vec_components()

    waveform, sr = librosa.load(filepath, sr=16000, mono=True)

    inputs = processor(
        waveform,
        sampling_rate=16000,
        return_tensors="pt",
        padding=False,
    )

    input_values = inputs.input_values.to(DEVICE)

    with torch.no_grad():
        outputs = model(input_values)
        hidden = outputs.last_hidden_state  # [1, time, hidden_dim]
        pooled = hidden.mean(dim=1).squeeze(0)  # [hidden_dim]

    return pooled.cpu().numpy().astype(np.float32)


def build_feature_matrix(X_df: pd.DataFrame) -> np.ndarray:
    features = []
    total = len(X_df)

    for i, path in enumerate(X_df["filepath"], start=1):
        if i == 1 or i % 25 == 0 or i == total:
            print(f"Embedding {i}/{total}: {path}")
        emb = extract_wav2vec_embedding(path)
        features.append(emb)

    return np.vstack(features)


def run_cv_experiment(X, y, speakers, model, n_splits=5):
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    min_class_count = int(pd.Series(y_encoded).value_counts().min())
    n_unique_speakers = int(pd.Series(speakers).nunique())
    actual_splits = min(n_splits, min_class_count, n_unique_speakers)

    if actual_splits < 2:
        raise ValueError(
            "Not enough data for StratifiedGroupKFold. "
            f"min_class_count={min_class_count}, unique_speakers={n_unique_speakers}"
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

        fold_results.append({
            "fold": fold,
            "accuracy": accuracy_score(y_test, preds),
            "balanced_accuracy": balanced_accuracy_score(y_test, preds),
            "macro_f1": f1_score(y_test, preds, average="macro"),
        })

    return fold_results, le


def summarize_results(fold_results):
    df = pd.DataFrame(fold_results)

    return {
        "accuracy_mean": float(df["accuracy"].mean()),
        "accuracy_std": float(df["accuracy"].std()),
        "balanced_accuracy_mean": float(df["balanced_accuracy"].mean()),
        "macro_f1_mean": float(df["macro_f1"].mean()),
    }