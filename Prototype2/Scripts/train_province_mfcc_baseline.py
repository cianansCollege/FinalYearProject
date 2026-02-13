import os
import re
import random
from typing import List, Tuple

import numpy as np
import pandas as pd

from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

import librosa


DATA_CSV = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index_with_resolved_paths.csv"

# Prefer resolved paths (DÁIL), fall back to original (NI)
AUDIO_COL_PRIMARY = "segment_file_resolved"
AUDIO_COL_FALLBACK = "segment_file"

# Province classification target
LABEL_COL = "native_province"

DATASET_COL = "dataset"
SPEAKER_COL = "speaker"

# If speaker_key exists in CSV we use it, otherwise we generate one deterministically
SPEAKER_KEY_COL = "speaker_key"

# Reduce dominance of speakers with many segments
MAX_SEGMENTS_PER_SPEAKER = 20
RANDOM_SEED = 42

# MFCC settings (match your processed audio)
TARGET_SR = 16000
N_MFCC = 13
N_FFT = 512
HOP_LENGTH = 160   # 10ms at 16kHz
WIN_LENGTH = 400   # 25ms at 16kHz


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]+", "", text)
    return text or "unknown"


def pick_audio_path(row: pd.Series) -> str:
    """
    Use segment_file_resolved if it exists on disk, else fall back to segment_file.
    """
    p = str(row.get(AUDIO_COL_PRIMARY, "") or "").strip()
    if p and os.path.exists(p):
        return p

    p2 = str(row.get(AUDIO_COL_FALLBACK, "") or "").strip()
    return p2


def ensure_speaker_key(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure a stable speaker key exists for grouping splits (prevents speaker leakage).
    If speaker_key is present and non-empty, use it.
    Otherwise generate: dataset + "_" + slug(speaker).
    """
    if SPEAKER_KEY_COL in df.columns and df[SPEAKER_KEY_COL].astype(str).str.strip().ne("").any():
        df[SPEAKER_KEY_COL] = df[SPEAKER_KEY_COL].astype(str).str.strip()
        return df

    ds = df.get(DATASET_COL, pd.Series([""] * len(df))).astype(str).map(slugify)
    sp = df.get(SPEAKER_COL, pd.Series([""] * len(df))).astype(str).map(slugify)
    df[SPEAKER_KEY_COL] = (ds + "_" + sp).astype(str)
    return df


def cap_segments_per_speaker(df: pd.DataFrame, cap: int, seed: int) -> pd.DataFrame:
    """
    Limit number of segments per speaker to reduce dominance.
    Deterministic via seed.
    """
    rng = random.Random(seed)
    kept_rows: List[int] = []

    for _, group in df.groupby(SPEAKER_KEY_COL):
        idxs = list(group.index)
        if len(idxs) <= cap:
            kept_rows.extend(idxs)
        else:
            rng.shuffle(idxs)
            kept_rows.extend(idxs[:cap])

    return df.loc[sorted(kept_rows)].copy()


def mfcc_features(path: str) -> np.ndarray:
    """
    Extract MFCC-based features from one audio file.

    Feature vector:
      - MFCC mean (13)
      - MFCC std  (13)
      - Delta mean (13)
      - Delta std  (13)
    Total length: 52
    """
    y, sr = librosa.load(path, sr=TARGET_SR, mono=True)

    # Guard: very short clips can cause FFT issues
    if y.size < WIN_LENGTH:
        y = np.pad(y, (0, WIN_LENGTH - y.size), mode="constant")

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        win_length=WIN_LENGTH,
    )

    delta = librosa.feature.delta(mfcc)

    feats = np.concatenate(
        [
            mfcc.mean(axis=1),
            mfcc.std(axis=1),
            delta.mean(axis=1),
            delta.std(axis=1),
        ],
        axis=0,
    )

    return feats.astype(np.float32)


def build_feature_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
    """
    Build X, y, groups arrays from the dataframe.
    Skips rows with missing labels or missing audio paths.
    Returns:
      X: (n_samples, 52)
      y: (n_samples,)
      groups: (n_samples,) speaker_key
      bad: list of "row_index:reason" for skipped rows
    """
    X_list: List[np.ndarray] = []
    y_list: List[str] = []
    g_list: List[str] = []
    bad: List[str] = []

    for i, row in df.iterrows():
        label = str(row.get(LABEL_COL, "") or "").strip()
        if not label:
            bad.append(f"{i}:missing_label")
            continue

        audio_path = pick_audio_path(row)
        if not audio_path or not os.path.exists(audio_path):
            bad.append(f"{i}:missing_audio:{audio_path}")
            continue

        try:
            x = mfcc_features(audio_path)
        except Exception as e:
            bad.append(f"{i}:mfcc_error:{e}")
            continue

        X_list.append(x)
        y_list.append(label)
        g_list.append(str(row[SPEAKER_KEY_COL]))

    X = np.vstack(X_list) if X_list else np.zeros((0, 4 * N_MFCC), dtype=np.float32)
    y = np.array(y_list, dtype=object)
    groups = np.array(g_list, dtype=object)

    return X, y, groups, bad


def main():
    df = pd.read_csv(DATA_CSV, encoding="utf-8-sig")

    # Ensure speaker key for grouped splits (prevents speaker leakage)
    df = ensure_speaker_key(df)

    # Clean label text
    df[LABEL_COL] = df[LABEL_COL].astype(str).str.strip()

    # Keep only the 4 main provinces (drop "Other")
    VALID_PROVINCES = ["Ulster", "Leinster", "Munster", "Connacht"]
    df = df[df[LABEL_COL].isin(VALID_PROVINCES)].copy()

    # Cap segments per speaker to reduce dominance
    df = cap_segments_per_speaker(df, cap=MAX_SEGMENTS_PER_SPEAKER, seed=RANDOM_SEED)

    # Build features
    X, y, groups, bad = build_feature_matrix(df)

    print("Rows after province filter + cap:", len(df))
    print("Feature matrix shape:", X.shape)
    print("Bad rows skipped:", len(bad))
    if bad:
        print("First 10 bad rows:", bad[:10])

    unique_groups = np.unique(groups)
    if unique_groups.size < 5:
        raise SystemExit(f"Not enough unique speakers for GroupKFold: {unique_groups.size}")

    # Speaker-grouped cross-validation
    n_splits = min(5, unique_groups.size)
    gkf = GroupKFold(n_splits=n_splits)

    y_true_all: List[str] = []
    y_pred_all: List[str] = []

    clf = RandomForestClassifier(
        n_estimators=400,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )

    for fold, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups), start=1):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        y_true_all.extend(list(y_test))
        y_pred_all.extend(list(y_pred))

        print(f"\nFold {fold}/{n_splits}")
        print("Test samples:", len(test_idx))
        print(classification_report(y_test, y_pred, zero_division=0))

    print("\n=== Overall (all folds combined) ===")
    print(classification_report(y_true_all, y_pred_all, zero_division=0))

    labels = sorted(set(y_true_all))
    print("Confusion matrix (labels in sorted order):")
    print(labels)
    print(confusion_matrix(y_true_all, y_pred_all, labels=labels))


if __name__ == "__main__":
    main()
