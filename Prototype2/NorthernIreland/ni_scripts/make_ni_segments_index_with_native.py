import csv
from urllib.parse import urlparse, parse_qs

NI_INDEX_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/ni_segments_index.csv"
NI_META_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/Unimportant/Copies/ni_dataset copy.csv"
OUT_PATH = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/ni_segments_index_with_native.csv"


def extract_video_id(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    if "v" in qs and qs["v"]:
        return qs["v"][0].strip()

    parts = parsed.path.strip("/").split("/")

    if len(parts) >= 2 and parts[0] == "shorts":
        return parts[1].strip()

    if "youtu.be" in parsed.netloc:
        return parts[0].strip() if parts else ""

    return ""


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return (reader.fieldnames or []), list(reader)


def write_csv(path: str, fieldnames: list[str], rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def build_meta_by_video_id(meta_rows: list[dict]) -> dict[str, dict]:
    """
    meta_rows are from ni_dataset copy.csv:
      constituency, native_city, native_county, native_province, speaker, party,
      youtube_url, clip_name, valid_times, clip_type, extra_info
    """
    lookup: dict[str, dict] = {}

    for r in meta_rows:
        vid = extract_video_id(r.get("youtube_url", ""))
        if not vid:
            continue

        lookup[vid] = {
            "native_city": (r.get("native_city") or "").strip(),
            "native_county": (r.get("native_county") or "").strip(),
            "native_province": (r.get("native_province") or "").strip(),
        }

    return lookup


def main():
    _, ni_rows = read_csv(NI_INDEX_PATH)
    _, meta_rows = read_csv(NI_META_PATH)

    meta_by_vid = build_meta_by_video_id(meta_rows)

    out_fields = [
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

    missing = 0
    for r in ni_rows:
        vid = (r.get("video_id") or "").strip()
        meta = meta_by_vid.get(vid)

        if meta:
            r["native_city"] = meta.get("native_city", "")
            r["native_county"] = meta.get("native_county", "")
            r["native_province"] = meta.get("native_province", "")
        else:
            r["native_city"] = r.get("native_city", "") or ""
            r["native_county"] = r.get("native_county", "") or ""
            r["native_province"] = r.get("native_province", "") or ""
            missing += 1

        if (r.get("dataset") or "").strip() == "":
            r["dataset"] = "NI"

    write_csv(OUT_PATH, out_fields, ni_rows)

    print(f"Wrote: {OUT_PATH}")
    print(f"Rows: {len(ni_rows)}")
    print(f"Rows missing native fields (no metadata match by video_id): {missing}")


if __name__ == "__main__":
    main()
