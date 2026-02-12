import csv
import os
from pathlib import Path

import pytest

# Import from your script
from add_resolved_paths import find_audio_by_video_id, add_resolved_paths, RESOLVED_COL


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return (r.fieldnames or []), list(r)


def touch_wav(path: Path):
    """
    Create a small dummy .wav file. Content doesn't matter for path resolution tests.
    """
    path.write_bytes(b"RIFF----WAVEfmt ")


def test_find_audio_by_video_id_picks_shortest_match(tmp_path: Path):
    dail_dir = tmp_path / "roi_audio_processed"
    dail_dir.mkdir()

    vid = "ABC123"

    # Two matches: ensure the deterministic rule (shortest basename) is used
    long_name = dail_dir / f"_{vid}_Deputy Eamon O Cuiv - Government Business - 25 Sep.wav"
    short_name = dail_dir / f"_{vid}.wav"

    touch_wav(long_name)
    touch_wav(short_name)

    resolved = find_audio_by_video_id(vid, str(dail_dir))
    assert resolved == str(short_name)


def test_find_audio_by_video_id_returns_empty_when_missing(tmp_path: Path):
    dail_dir = tmp_path / "roi_audio_processed"
    dail_dir.mkdir()

    resolved = find_audio_by_video_id("DOES_NOT_EXIST", str(dail_dir))
    assert resolved == ""


def test_add_resolved_paths_adds_column_and_resolves_dail_only(tmp_path: Path):
    dail_dir = tmp_path / "roi_audio_processed"
    dail_dir.mkdir()

    # Create processed audio for 2 DÁIL rows
    touch_wav(dail_dir / "_VID1_Deputy Someone.wav")
    touch_wav(dail_dir / "_VID2_Senator Someone.wav")

    in_csv = tmp_path / "all_segments_index.csv"
    out_csv = tmp_path / "all_segments_index_with_resolved_paths.csv"

    fields = [
        "segment_file", "video_id", "segment_index", "start_sec", "end_sec",
        "speaker", "party", "constituency", "native_city", "native_county",
        "native_province", "clip_name", "clip_type", "extra_info",
        "valid_times", "dataset",
    ]

    rows = [
        # DÁIL row with mojibake path that won't exist; should resolve by video_id
        {
            "segment_file": "/bad/path/_VID1_Deputy √âamon √ì Cu√≠v.wav",
            "video_id": "VID1",
            "segment_index": "1",
            "start_sec": "0",
            "end_sec": "30",
            "speaker": "eamon o cuiv",
            "party": "Fianna Fáil",
            "constituency": "Galway West",
            "native_city": "Galway",
            "native_county": "Galway",
            "native_province": "Connacht",
            "clip_name": "x",
            "clip_type": "parliament",
            "extra_info": "",
            "valid_times": "",
            "dataset": "DAIL",
        },
        # Another DÁIL row
        {
            "segment_file": "/bad/path/_VID2_Senator ???.wav",
            "video_id": "VID2",
            "segment_index": "1",
            "start_sec": "30",
            "end_sec": "60",
            "speaker": "someone",
            "party": "Independent",
            "constituency": "Seanad",
            "native_city": "",
            "native_county": "",
            "native_province": "",
            "clip_name": "y",
            "clip_type": "parliament",
            "extra_info": "",
            "valid_times": "",
            "dataset": "DAIL",
        },
        # NI row should NOT be changed by DÁIL resolver logic
        {
            "segment_file": str(tmp_path / "segments" / "NI_FILE.wav"),
            "video_id": "NIVID",
            "segment_index": "1",
            "start_sec": "0",
            "end_sec": "30",
            "speaker": "gavin robinson",
            "party": "DUP",
            "constituency": "Belfast East",
            "native_city": "Belfast",
            "native_county": "Antrim",
            "native_province": "Ulster",
            "clip_name": "z",
            "clip_type": "party conference",
            "extra_info": "",
            "valid_times": "",
            "dataset": "NI",
        }
    ]

    # Create the NI file so it exists
    (tmp_path / "segments").mkdir()
    touch_wav(tmp_path / "segments" / "NI_FILE.wav")

    write_csv(in_csv, fields, rows)

    stats = add_resolved_paths(
        in_path=str(in_csv),
        out_path=str(out_csv),
        dail_dir=str(dail_dir),
    )

    assert stats["total_dail"] == 2
    assert stats["fixed"] == 2
    assert stats["missing"] == 0
    assert os.path.exists(out_csv)

    out_fields, out_rows = read_csv(out_csv)
    assert RESOLVED_COL in out_fields
    assert len(out_rows) == 3

    # DÁIL resolved paths should exist and be inside processed dir
    r1 = out_rows[0]
    assert r1["dataset"] == "DAIL"
    assert os.path.exists(r1[RESOLVED_COL])
    assert Path(r1[RESOLVED_COL]).parent == dail_dir

    r2 = out_rows[1]
    assert r2["dataset"] == "DAIL"
    assert os.path.exists(r2[RESOLVED_COL])
    assert Path(r2[RESOLVED_COL]).parent == dail_dir

    # NI row should keep its original segment path (resolved col equals segment_file)
    r3 = out_rows[2]
    assert r3["dataset"] == "NI"
    assert r3[RESOLVED_COL] == r3["segment_file"]
    assert os.path.exists(r3[RESOLVED_COL])
