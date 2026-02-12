import csv
import os

path = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index_with_resolved_paths.csv"

missing = []
with open(path, newline="", encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    for i, row in enumerate(r, start=2):  # header is line 1
        sf = (row.get("segment_file_resolved") or "").strip()
        if sf and not os.path.exists(sf):
            missing.append((i, sf, row.get("dataset"), row.get("video_id")))

print("missing segment_file count:", len(missing))
for item in missing[:20]:
    print(item)
if len(missing) > 20:
    print("... (showing first 20)")
