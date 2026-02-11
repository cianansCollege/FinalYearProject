import os
import csv
import librosa
import numpy as np
import pandas as pd

INDEX_CSV = "ni_segments_index.csv"
SEGMENTS_DIR = "segments"
OUTPUT_CSV = "ni_mfcc_features.csv"

N_MFCC = 13
TARGET_SR = 16000


def extract_mfcc_stats(wav_path):
    y, sr = librosa.load(wav_path, sr=TARGET_SR, mono=True)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=N_MFCC
    )

    # mfcc shape: (n_mfcc, time_frames)
    features = {}

    for i in range(N_MFCC):
        features[f"mfcc_{i+1}_mean"] = float(np.mean(mfcc[i]))
        features[f"mfcc_{i+1}_std"] = float(np.std(mfcc[i]))

    return features


def main():
    df = pd.read_csv(INDEX_CSV)

    rows = []

    for _, row in df.iterrows():
        segment_file = row["segment_file"]

        if not isinstance(segment_file, str):
            continue

        wav_path = segment_file
        if not os.path.exists(wav_path):
            print(f"Missing audio: {wav_path}")
            continue

        mfcc_feats = extract_mfcc_stats(wav_path)

        out_row = {
            "segment_file": segment_file,
            "video_id": row["video_id"],
            "segment_index": row["segment_index"],
            "speaker": row["speaker"],
            "party": row["party"],
            "constituency": row["constituency"],
            "clip_type": row["clip_type"],
        }

        out_row.update(mfcc_feats)
        rows.append(out_row)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print(f"Wrote {OUTPUT_CSV} with {len(out_df)} rows")


if __name__ == "__main__":
    main()

