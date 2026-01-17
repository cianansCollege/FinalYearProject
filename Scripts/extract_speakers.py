import os
import csv
import re

# CHANGE THIS to your audio directory
AUDIO_DIR = "/Users/cianan/Documents/GitHub/FYP/Prototype2/data/audio"

OUTPUT_CSV = "dail_speakers.csv"

pattern = re.compile(r"_(.*?)\s-")

rows = []

for filename in os.listdir(AUDIO_DIR):
    if not filename.lower().endswith(".wav"):
        continue

    match = pattern.search(filename)

    if match:
        speaker = match.group(1).strip()
    else:
        speaker = "UNKNOWN"

    rows.append({
        "filename": filename,
        "speaker": speaker
    })

# Write to CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["filename", "speaker"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Extracted {len(rows)} entries to {OUTPUT_CSV}")
