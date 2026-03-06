import csv, os
import sys
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / "project_paths.py").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break
else:
    raise RuntimeError("Could not locate project_paths.py")

from project_paths import data_path, metadata_path

path = metadata_path("all_segments_index_with_resolved_paths.csv")
dail_dir = data_path("DailData", "roi_audio_processed")

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
