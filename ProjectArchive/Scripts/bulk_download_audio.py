import os
import subprocess
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
URLS_FILE = "/Users/cianan/Documents/GitHub/FYP/Prototype/data/yt-data/playlistsurls2.txt"
OUTPUT_DIR = Path("/Users/cianan/Documents/GitHub/FYP/Prototype/data/yt-data/playlists2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ffmpeg normalization options
TARGET_SR = 16000   # sampling rate
TARGET_CHANNELS = 1 # mono

def download_audio(url: str):
    """Download YouTube audio and convert to mono 16 kHz WAV."""
    try:
        print(f"\n🎧 Downloading: {url}")

        # yt-dlp command
        command = [
            "yt-dlp",
            "-f", "best",
            "--extract-audio",
            "--audio-format", "wav",
            "--audio-quality", "0",
            "--cookies-from-browser", "firefox", 
            "--download-sections", "*00:30-01:00",
            "-o", str(OUTPUT_DIR / "%(id)s_%(title).50s.%(ext)s"),
            url,
        ]

        subprocess.run(command, check=True)

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download {url}: {e}")
        return None

def normalize_audio():
    """Convert all WAV files to mono, 16 kHz using ffmpeg."""
    processed_dir = OUTPUT_DIR / "processed"
    processed_dir.mkdir(exist_ok=True)

    for wav_file in OUTPUT_DIR.glob("*.wav"):
        out_path = processed_dir / wav_file.name
        cmd = [
            "ffmpeg", "-y",
            "-i", str(wav_file),
            "-ac", str(TARGET_CHANNELS),
            "-ar", str(TARGET_SR),
            str(out_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Normalized {wav_file.name}")

def main():
    with open(URLS_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"📋 Found {len(urls)} URLs in {URLS_FILE}")

    for url in urls:
        download_audio(url)

    print("\n🔄 Normalizing all audio...")
    normalize_audio()
    print("\n🎉 All done! Files saved in Prototype/data/yt-data")

if __name__ == "__main__":
    main()
