"""
Clean and standardize audio segments:
- Drop clips shorter than MIN_SEC
- Trim to middle TARGET_SEC
- Loudness normalize using ffmpeg loudnorm
- Write cleaned WAVs and an updated CSV index

Input CSV must contain:
- segment_file_resolved (full path to wav)
- native_province
- speaker
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pandas as pd

for parent in Path(__file__).resolve().parents:
    if (parent / "project_paths.py").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break
else:
    raise RuntimeError("Could not locate project_paths.py")

from project_paths import data_path


# =============================================================================
# EDIT THIS SECTION
# =============================================================================

# Your input segments CSV (the one you train from currently)
IN_CSV = data_path("speaker_master_main.csv")

# Where to write cleaned WAVs
OUT_DIR = data_path("segments_clean_lufs10s")

# Where to write the updated CSV
OUT_CSV = data_path("segments_clean_index.csv")

# Column names in your CSV
PATH_COL = "segment_file_resolved"
LABEL_COL = "native_province"
SPEAKER_COL = "speaker"

# Cleaning rules
MIN_SEC = 10.0          # drop anything shorter than this
TARGET_SEC = 10.0       # trim everything to this duration (middle window)
SKIP_EXISTING = True    # if cleaned wav already exists, reuse it

# Audio output format
OUT_SR = 16000
OUT_CH = 1

# Loudness normalization targets (ffmpeg loudnorm)
LUFS_I = -23.0
LUFS_LRA = 7.0
LUFS_TP = -2.0

# =============================================================================
# END EDIT SECTION
# =============================================================================


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + "\n\nSTDOUT:\n"
            + p.stdout
            + "\n\nSTDERR:\n"
            + p.stderr
        )


def ffprobe_duration_seconds(wav_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nk=1:nw=1",
        str(wav_path),
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {wav_path}\n{p.stderr}")
    return float(p.stdout.strip())


def stable_output_name(src_path: Path) -> str:
    h = hashlib.sha1(str(src_path).encode("utf-8")).hexdigest()[:10]
    stem = src_path.stem
    safe_stem = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in stem)
    return f"{safe_stem}__{h}.wav"


def process_one(src_wav: Path, dst_wav: Path) -> None:
    dur = ffprobe_duration_seconds(src_wav)
    start = max(0.0, (dur - TARGET_SEC) / 2.0)

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{TARGET_SEC:.3f}",
        "-i",
        str(src_wav),
        "-ac",
        str(OUT_CH),
        "-ar",
        str(OUT_SR),
        "-af",
        f"loudnorm=I={LUFS_I}:LRA={LUFS_LRA}:TP={LUFS_TP}",
        str(dst_wav),
    ]
    run(cmd)


def main() -> None:
    if not IN_CSV.exists():
        raise FileNotFoundError(f"IN_CSV not found: {IN_CSV}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(IN_CSV)

    required = {PATH_COL, LABEL_COL, SPEAKER_COL}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    kept_rows = []
    dropped_missing = 0
    dropped_short = 0
    processed = 0
    reused = 0
    failed = 0

    for _, row in df.iterrows():
        src = row[PATH_COL]
        if not isinstance(src, str) or not src.strip():
            dropped_missing += 1
            continue

        src_path = Path(src).expanduser()
        if not src_path.exists():
            dropped_missing += 1
            continue

        try:
            dur = ffprobe_duration_seconds(src_path)
        except Exception:
            failed += 1
            continue

        if dur < MIN_SEC:
            dropped_short += 1
            continue

        dst_path = OUT_DIR / stable_output_name(src_path)

        if SKIP_EXISTING and dst_path.exists():
            reused += 1
        else:
            try:
                process_one(src_path, dst_path)
                processed += 1
            except Exception:
                failed += 1
                continue

        new_row = row.copy()
        new_row["segment_file_clean"] = str(dst_path)
        new_row["duration_sec_original"] = dur
        new_row["clean_target_sec"] = TARGET_SEC
        new_row["clean_lufs_i"] = LUFS_I
        kept_rows.append(new_row)

    out_df = pd.DataFrame(kept_rows)
    out_df.to_csv(OUT_CSV, index=False)

    total = len(df)
    kept = len(out_df)

    print("Done.")
    print(f"Input rows: {total}")
    print(f"Kept rows: {kept}")
    print(f"Dropped (missing/unreadable path): {dropped_missing}")
    print(f"Dropped (too short): {dropped_short}")
    print(f"Processed (new files): {processed}")
    print(f"Reused (already existed): {reused}")
    print(f"Failed (ffmpeg/ffprobe errors): {failed}")
    print(f"Output CSV: {OUT_CSV}")
    print(f"Output WAV dir: {OUT_DIR}")


if __name__ == "__main__":
    main()
