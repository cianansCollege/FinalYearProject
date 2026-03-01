import csv
import os
import glob
from typing import Dict, List

IN_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index.csv"
OUT_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index_with_resolved_paths.csv"

DAIL_DIR = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/DailData/roi_audio_processed"

RESOLVED_COL = "segment_file_resolved"


def find_audio_by_video_id(video_id: str, dail_dir: str) -> str:
    """
    Resolve a DÁIL audio file path using only the stable video_id.
    Searches dail_dir for any .wav containing the video_id substring.
    Deterministically returns the match with the shortest basename.
    """
    if not video_id:
        return ""

    pattern = os.path.join(dail_dir, f"*{video_id}*.wav")
    matches = glob.glob(pattern)

    if not matches:
        return ""

    matches.sort(key=lambda p: len(os.path.basename(p)))
    return matches[0]


def add_resolved_paths(
    in_path: str,
    out_path: str,
    dail_dir: str,
    resolved_col: str = RESOLVED_COL,
) -> Dict[str, int | str]:
    """
    Reads a merged segments index CSV, adds a resolved path column, and writes a new CSV.

    Rules:
      - Default: resolved_col = segment_file
      - For dataset == DAIL: resolve by video_id in dail_dir and write into resolved_col
      - No fallback directories
    """
    fixed = 0
    missing = 0
    total_dail = 0

    with open(in_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows: List[dict] = list(reader)

    if resolved_col not in fieldnames:
        fieldnames.append(resolved_col)

    for r in rows:
        r[resolved_col] = r.get("segment_file", "")

        if (r.get("dataset") or "").strip().upper() != "DAIL":
            continue

        total_dail += 1

        vid = (r.get("video_id") or "").strip()
        resolved = find_audio_by_video_id(vid, dail_dir)

        if resolved:
            r[resolved_col] = resolved
            fixed += 1
        else:
            missing += 1

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return {
        "out_path": out_path,
        "total_dail": total_dail,
        "fixed": fixed,
        "missing": missing,
    }


def main():
    stats = add_resolved_paths(
        in_path=IN_PATH,
        out_path=OUT_PATH,
        dail_dir=DAIL_DIR,
        resolved_col=RESOLVED_COL,
    )

    print(f"Wrote: {stats['out_path']}")
    print(f"DAIL rows: {stats['total_dail']}")
    print(f"Resolved paths found: {stats['fixed']}")
    print(f"Still missing: {stats['missing']}")


if __name__ == "__main__":
    main()
