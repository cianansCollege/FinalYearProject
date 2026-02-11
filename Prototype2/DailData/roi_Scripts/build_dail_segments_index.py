import os
import pandas as pd

DAIL_META = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/DailData/DailSpeakers_CSV/final_dataset_all_copy.csv"
DAIL_AUDIO_DIR = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/DailData/audio"   # CHANGE if needed
OUT = "dail_segments_index.csv"

def extract_video_id_from_filename(name: str) -> str:
    if not isinstance(name, str):
        return ""
    return name[:11]  # YouTube IDs are always 11 chars

def find_real_file(video_id: str) -> str:
    if not video_id:
        return ""

    for f in os.listdir(DAIL_AUDIO_DIR):
        if f.startswith(video_id):
            return os.path.join(DAIL_AUDIO_DIR, f)

    return ""  # not found

def main():
    df = pd.read_csv(DAIL_META)

    if "filename" not in df.columns:
        raise SystemExit("Missing 'filename' column")

    df["video_id"] = df["filename"].apply(extract_video_id_from_filename)
    df["segment_file"] = df["video_id"].apply(find_real_file)

    missing = (df["segment_file"] == "").sum()
    print("Missing audio files:", int(missing))

    out = pd.DataFrame({
        "segment_file": df["segment_file"],
        "video_id": df["video_id"],
        "segment_index": "001",
        "start_sec": 30,
        "end_sec": 60,

        "speaker": df.get("speaker_key", df.get("speaker_raw", "")),
        "party": df.get("party", ""),
        "constituency": df.get("constituency", ""),

        "native_city": df.get("native_city", ""),
        "native_county": df.get("native_county", ""),
        "native_province": df.get("native_province", df.get("province", "")),

        "clip_name": df.get("filename_raw", ""),
        "clip_type": "",
        "extra_info": df.get("extra_information", ""),
        "valid_times": "0.30-1.00",

        "source": "DAIL",
        "province": df.get("province", df.get("native_province", "")),
        "province_source": "native_province"
    })

    out = out[out["segment_file"] != ""]  # drop unresolved rows
    out.to_csv(OUT, index=False)

    print("Wrote", OUT, "rows:", len(out))

if __name__ == "__main__":
    main()
