from pathlib import Path
import csv
import unicodedata
import re

# Directory containing your .wav files
AUDIO_DIR = Path("/Users/cianan/Documents/GitHub/FYP/Prototype2/data/audio")

OUTPUT_CSV = "dail_speakers.csv"
FAILED_CSV = "dail_speakers_failed.csv"

# Match a dash/en-dash/em-dash separator after a speaker name, with optional spaces.
# Handles: " - ", "-", "--", " – ", "—", etc.
AFTER_NAME_DASH_RE = re.compile(r"\s*[-–—]{1,2}\s*")

# Heuristic: speaker names usually start with a title or an uppercase letter (incl. Irish fadas).
SPEAKER_LIKE_RE = re.compile(r"^(Deputy|Senator|Minister|Taoiseach|Tánaiste)?\s*[A-ZÁÉÍÓÚ]")

def to_nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def fix_mojibake(s: str) -> str:
    """
    Fix common UTF-8 text that was decoded as Latin-1 (e.g., Br√≠d -> Bríd).
    If it doesn't look like mojibake, this safely returns the original string.
    """
    try:
        repaired = s.encode("latin1").decode("utf-8")
        # Only accept the repair if it actually changes something and reduces mojibake markers.
        # This is conservative, but prevents unwanted transformations.
        if repaired != s and ("√" in s or "‚Ä" in s or "Â" in s):
            return repaired
        return s
    except Exception:
        return s

def strip_diacritics(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", s)

def normalise_key(name: str) -> str:
    """
    Normalise for matching:
      - Unicode NFC
      - fix mojibake if present
      - lowercase
      - strip diacritics (fadas)
      - unify apostrophes
      - collapse whitespace
      - remove leading titles like 'Deputy'/'Senator' (optional; enabled)
    """
    n = to_nfc(name).strip()
    n = fix_mojibake(n)

    # Unify apostrophes/quotes
    n = n.replace("’", "'").replace("‘", "'").replace("`", "'")

    # Optional: remove leading title(s) for matching consistency
    for prefix in ["deputy ", "senator ", "minister ", "táinaiste ", "taoiseach "]:
        if n.lower().startswith(prefix):
            n = n[len(prefix):].strip()
            break

    n = strip_diacritics(n).lower()
    n = re.sub(r"\s+", " ", n).strip()
    return n if n else "unknown"

def extract_speaker_raw(filename: str) -> str | None:
    """
    Robust extraction for filenames like:
      YTID_Speaker Name - Topic.wav
      YTID_Speaker Name- Topic.wav
      YTID1_YTID2_Speaker Name - Topic.wav
      _YTID_Speaker Name – Topic.wav

    Strategy:
      - Normalize to NFC
      - Fix mojibake in the whole filename
      - Split by '_' and scan right-to-left
      - For each segment, take text before the first dash separator
      - Accept the candidate if it looks like a speaker name
    """
    name = to_nfc(filename)
    name = fix_mojibake(name)

    stem = name.rsplit(".", 1)[0]  # remove extension
    parts = stem.split("_")

    for part in reversed(parts):
        m = AFTER_NAME_DASH_RE.search(part)
        if not m:
            continue

        candidate = part[:m.start()].strip()
        candidate = re.sub(r"\s+", " ", candidate).strip()

        if not candidate:
            continue

        if SPEAKER_LIKE_RE.match(candidate):
            return candidate

    return None

def main() -> None:
    if not AUDIO_DIR.exists():
        raise FileNotFoundError(f"Directory does not exist: {AUDIO_DIR}")
    if not AUDIO_DIR.is_dir():
        raise NotADirectoryError(f"Not a directory: {AUDIO_DIR}")

    rows: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []

    for p in AUDIO_DIR.iterdir():
        if not p.is_file() or p.suffix.lower() != ".wav":
            continue

        speaker_raw = extract_speaker_raw(p.name)

        if speaker_raw is None:
            failed.append({
                "filename": p.name,
                "reason": "Could not confidently extract speaker (underscore/dash pattern mismatch)"
            })
            rows.append({
                "filename": p.name,
                "speaker_raw": "UNKNOWN",
                "speaker_key": "unknown"
            })
            continue

        speaker_raw = to_nfc(fix_mojibake(speaker_raw))
        speaker_key = normalise_key(speaker_raw)

        rows.append({
            "filename": p.name,
            "speaker_raw": speaker_raw,
            "speaker_key": speaker_key
        })

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "speaker_raw", "speaker_key"])
        writer.writeheader()
        writer.writerows(rows)

    with open(FAILED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "reason"])
        writer.writeheader()
        writer.writerows(failed)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")
    print(f"Failed to parse {len(failed)} files; see {FAILED_CSV}")

if __name__ == "__main__":
    main()
