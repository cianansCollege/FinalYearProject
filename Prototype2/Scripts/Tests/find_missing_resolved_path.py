import csv, os

path = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index_with_resolved_paths.csv"
dail_dir = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/DailData/roi_audio_processed"

with open(path, newline="", encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    for row in r:
        if (row.get("dataset") or "").strip().upper() != "DAIL":
            continue

        vid = (row.get("video_id") or "").strip()
        resolved = (row.get("segment_file_resolved") or "").strip()

        # unresolved means it stayed as original segment_file and doesn't exist
        if not resolved or not os.path.exists(resolved):
            print("Missing row:")
            print("video_id:", vid)
            print("segment_file (original):", row.get("segment_file"))
            print("segment_file_resolved:", resolved)
            break

    print("No missing file found")