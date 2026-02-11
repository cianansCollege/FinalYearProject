import csv
import os
import glob

IN_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index.csv"
OUT_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index_with_resolved_paths.csv"

DAIL_DIR_PRIMARY = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/DailData/roi_audio_processed"

RESOLVED_COL = "segment_file_resolved"


def find_audio_by_video_id(video_id: str) -> str:
    if not video_id:
        return ""

    # try processed first
    pattern = os.path.join(DAIL_DIR_PRIMARY, f"*{video_id}*.wav")
    matches = glob.glob(pattern)
    if matches:
        matches.sort(key=lambda p: len(os.path.basename(p)))
        return matches[0]

    # fallback to raw
    pattern = os.path.join(DAIL_DIR_FALLBACK, f"*{video_id}*.wav")
    matches = glob.glob(pattern)
    if matches:
        matches.sort(key=lambda p: len(os.path.basename(p)))
        return matches[0]

    return ""


def main():
    fixed = 0
    missing = 0
    total_dail = 0

    with open(IN_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if RESOLVED_COL not in fieldnames:
        fieldnames.append(RESOLVED_COL)

    for r in rows:
        # default: keep original path
        r[RESOLVED_COL] = r.get("segment_file", "")

        if (r.get("dataset") or "").strip().upper() != "DAIL":
            continue

        total_dail += 1

        vid = (r.get("video_id") or "").strip()
        resolved = find_audio_by_video_id(vid)

        if resolved:
            r[RESOLVED_COL] = resolved
            fixed += 1
        else:
            missing += 1

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote: {OUT_PATH}")
    print(f"DAIL rows: {total_dail}")
    print(f"Resolved paths found: {fixed}")
    print(f"Still missing: {missing}")


if __name__ == "__main__":
    main()
