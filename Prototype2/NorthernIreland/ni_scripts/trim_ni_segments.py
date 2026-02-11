import csv
import os
import re
import subprocess
from datetime import datetime
from urllib.parse import urlparse, parse_qs

INPUT_CSV = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_metadata/ni_dataset.csv"
URL_COL = "youtube_url"
TIMES_COL = "valid_times"

SPEAKER_COL = "speaker"
PARTY_COL = "party"
CONSTITUENCY_COL = "constituency"

AUDIO_DIR = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_audio_16k_mono"
OUT_DIR = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_segments"
LOG_FILE = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/NorthernIreland/ni_logs/trim_log.csv"

TARGET_SR = 16000
TARGET_CH = 1

MAX_SEG_SECONDS = 30
BOUNDARY_GAP_SECONDS = 0  # keep 0 for no gaps; set 1 for a 1-second gap

SKIP_IF_OUTPUT_EXISTS = True


def slug(text):
    if text is None:
        return "unknown"

    text = str(text)
    text = text.replace("\u00a0", " ").strip()

    if text == "":
        return "unknown"

    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^A-Za-z0-9_\-]", "", text)

    return text[:80] if text else "unknown"


def extract_video_id(url: str) -> str:
    if not url:
        raise ValueError("Empty URL")

    url = url.strip()
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        vid = parsed.path.strip("/").split("/")[0].strip()
        if vid:
            return vid

    qs = parse_qs(parsed.query)
    if "v" in qs and qs["v"]:
        return qs["v"][0].strip()

    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "shorts":
        return parts[1].strip()

    raise ValueError("Could not extract video ID")


def mmss_to_seconds(token: str) -> int:
    token = token.strip()
    if not re.fullmatch(r"\d+\.\d{2}", token):
        raise ValueError(f"Invalid mm.ss time: {token}")

    minutes, seconds = token.split(".")
    sec = int(seconds)

    if sec >= 60:
        raise ValueError(f"Seconds >= 60 in token: {token}")

    return int(minutes) * 60 + sec


def parse_valid_times(cell) -> list[tuple[int, int]]:
    if cell is None or str(cell).strip() == "":
        return []

    segments = []
    parts = [p.strip() for p in str(cell).split(",") if p.strip()]

    for p in parts:
        start_str, end_str = re.split(r"\s*-\s*", p)
        start = mmss_to_seconds(start_str)
        end = mmss_to_seconds(end_str)

        if end <= start:
            raise ValueError(f"End <= start in segment: {p}")

        segments.append((start, end))

    return segments


def split_interval(start_sec: int, end_sec: int, max_len: int = MAX_SEG_SECONDS, gap: int = BOUNDARY_GAP_SECONDS):
    chunks = []
    cur = start_sec

    while cur < end_sec:
        nxt = min(cur + max_len, end_sec)
        chunks.append((cur, nxt))
        cur = nxt + gap

    return [(s, e) for (s, e) in chunks if e > s]


def ffprobe_duration_seconds(wav_path: str) -> int:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path,
    ]
    out = subprocess.check_output(cmd).decode("utf-8").strip()
    return int(float(out))


def ffmpeg_trim(src: str, start_sec: int, end_sec: int, out: str):
    duration = end_sec - start_sec
    cmd = [
        "ffmpeg", "-y",
        "-hide_banner", "-loglevel", "error",
        "-ss", str(start_sec),
        "-i", src,
        "-t", str(duration),
        "-ar", str(TARGET_SR),
        "-ac", str(TARGET_CH),
        out
    ]
    subprocess.run(cmd, check=True)


def ensure_log(overwrite: bool = True):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if overwrite or not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "video_id", "segment", "start", "end", "output", "status", "error"])


def log(video_id, segment, start, end, output, status, error=""):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            datetime.now().isoformat(timespec="seconds"),
            video_id,
            segment,
            start,
            end,
            output,
            status,
            error
        ])


def main():
    ensure_log(overwrite=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    seen_video_ids = set()

    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            video_id = ""
            try:
                video_id = extract_video_id(row.get(URL_COL, ""))
                if video_id in seen_video_ids:
                    log(video_id, "", "", "", "", "skip", "Duplicate video_id in dataset; skipped row")
                    continue
                seen_video_ids.add(video_id)

                src = os.path.join(AUDIO_DIR, f"{video_id}.wav")
                if not os.path.exists(src):
                    raise FileNotFoundError(f"Audio file not found: {src}")

                base = "_".join([
                    slug(row.get(SPEAKER_COL)),
                    slug(row.get(PARTY_COL)),
                    slug(row.get(CONSTITUENCY_COL)),
                    video_id
                ])

                good_ranges = parse_valid_times(row.get(TIMES_COL, ""))

                if not good_ranges:
                    total_sec = ffprobe_duration_seconds(src)
                    good_ranges = [(0, total_sec)]

                chunk_index = 1
                for (start, end) in good_ranges:
                    chunks = split_interval(start, end)

                    for (s, e) in chunks:
                        out = os.path.join(OUT_DIR, f"{base}_{chunk_index:03d}.wav")

                        if SKIP_IF_OUTPUT_EXISTS and os.path.exists(out):
                            log(video_id, chunk_index, s, e, out, "skip", "Output already exists")
                            chunk_index += 1
                            continue

                        ffmpeg_trim(src, s, e, out)
                        log(video_id, chunk_index, s, e, out, "ok")
                        chunk_index += 1

            except Exception as e:
                log(video_id, "", "", "", "", "fail", str(e))


if __name__ == "__main__":
    main()
