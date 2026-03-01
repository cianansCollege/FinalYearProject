import csv
import os

NI_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/ni_segments_index_with_native.csv"
DAIL_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/DailData/roi_MetaData/dail_segments_index.csv"
OUT_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index.csv"

MASTER_FIELDS = [
    "segment_file",
    "video_id",
    "segment_index",
    "start_sec",
    "end_sec",
    "speaker",
    "party",
    "constituency",
    "native_city",
    "native_county",
    "native_province",
    "clip_name",
    "clip_type",
    "extra_info",
    "valid_times",
    "dataset",
]


def read_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def ensure_fields(rows: list[dict]) -> list[dict]:
    for r in rows:
        for f in MASTER_FIELDS:
            if f not in r:
                r[f] = ""
        # normalise dataset string
        r["dataset"] = (r.get("dataset") or "").strip()
    return rows


def dedupe(rows: list[dict]) -> tuple[list[dict], int]:
    """
    Remove exact duplicates using a stable key:
      (dataset, video_id, start_sec, end_sec)

    This is robust even if segment_index differs across pipelines.
    """
    seen = set()
    out = []
    removed = 0

    for r in rows:
        key = (
            (r.get("dataset") or "").strip(),
            (r.get("video_id") or "").strip(),
            str(r.get("start_sec") or "").strip(),
            str(r.get("end_sec") or "").strip(),
        )
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        out.append(r)

    return out, removed


def write_rows(path: str, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    for p in (NI_PATH, DAIL_PATH):
        if not os.path.exists(p):
            raise SystemExit(f"Missing input file: {p}")

    ni_rows = ensure_fields(read_rows(NI_PATH))
    dail_rows = ensure_fields(read_rows(DAIL_PATH))

    combined = ni_rows + dail_rows
    combined, removed = dedupe(combined)

    write_rows(OUT_PATH, combined)

    print(f"Wrote merged index: {OUT_PATH}")
    print(f"NI rows: {len(ni_rows)}")
    print(f"DAIL rows: {len(dail_rows)}")
    print(f"Total rows written: {len(combined)}")
    print(f"Duplicates removed: {removed}")


if __name__ == "__main__":
    main()
