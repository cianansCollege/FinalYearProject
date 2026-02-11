import csv
import os
from urllib.parse import urlparse, parse_qs

DATASET_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/ni_dataset.csv"
LOG_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_logs/trim_log.csv"
OUTPUT_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/ni_segments_index.csv"

# Your dataset headers
URL_COL = "youtube_url"
SPEAKER_COL = "speaker"
PARTY_COL = "party"
CONSTITUENCY_COL = "constituency"
CLIP_NAME_COL = "clip_name"
CLIP_TYPE_COL = "clip_type"
EXTRA_INFO_COL = "extra_info"
VALID_TIMES_COL = "valid_times"

def extract_video_id(url: str) -> str:
    url = (url or "").strip()
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "v" in qs and qs["v"]:
        return qs["v"][0]
    # shorts
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "shorts":
        return parts[1]
    # youtu.be
    if "youtu.be" in parsed.netloc:
        return parts[0] if parts else ""
    return ""

def read_dataset():
    # utf-8-sig removes BOM from the first header if present
    with open(DATASET_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        by_vid = {}
        for row in reader:
            vid = extract_video_id(row.get(URL_COL, ""))
            if not vid:
                continue
            by_vid[vid] = row
        return by_vid

def main():
    if not os.path.exists(LOG_PATH):
        raise SystemExit(f"Missing {LOG_PATH}")

    dataset = read_dataset()

    out_fields = [
        "segment_file",
        "video_id",
        "segment_index",
        "start_sec",
        "end_sec",
        "speaker",
        "party",
        "constituency",
        "clip_name",
        "clip_type",
        "extra_info",
        "valid_times",
    ]

    with open(LOG_PATH, newline="", encoding="utf-8") as f_in, \
         open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f_out:

        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=out_fields)
        writer.writeheader()

        for logrow in reader:
            if logrow.get("status") != "ok":
                continue

            vid = logrow.get("video_id", "").strip()
            seg = str(logrow.get("segment", "")).strip()
            start = str(logrow.get("start", "")).strip()
            end = str(logrow.get("end", "")).strip()
            seg_file = logrow.get("output", "").strip()

            meta = dataset.get(vid, {})

            writer.writerow({
                "segment_file": seg_file,
                "video_id": vid,
                "segment_index": seg,
                "start_sec": start,
                "end_sec": end,
                "speaker": meta.get(SPEAKER_COL, ""),
                "party": meta.get(PARTY_COL, ""),
                "constituency": meta.get(CONSTITUENCY_COL, ""),
                "clip_name": meta.get(CLIP_NAME_COL, ""),
                "clip_type": meta.get(CLIP_TYPE_COL, ""),
                "extra_info": meta.get(EXTRA_INFO_COL, ""),
                "valid_times": meta.get(VALID_TIMES_COL, ""),
            })

    print(f"Wrote {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
