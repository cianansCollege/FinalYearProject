# Audio decoding, normalization, and resampling helpers for inference input.

from __future__ import annotations

import io
import subprocess
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


TARGET_SR = 16000


def _guess_audio_suffix(audio_bytes: bytes) -> str:
    if audio_bytes.startswith(b"RIFF") and audio_bytes[8:12] == b"WAVE":
        return ".wav"
    if audio_bytes.startswith(b"fLaC"):
        return ".flac"
    if audio_bytes.startswith(b"OggS"):
        return ".ogg"
    if audio_bytes.startswith(b"ID3"):
        return ".mp3"
    if audio_bytes.startswith(b"\x1A\x45\xDF\xA3"):
        return ".webm"
    if len(audio_bytes) > 12 and audio_bytes[4:8] == b"ftyp":
        return ".m4a"
    return ".bin"


def _load_with_ffmpeg(audio_bytes: bytes, target_sr: int) -> tuple[np.ndarray, int]:
    input_path: Path | None = None
    output_path: Path | None = None

    try:
        suffix = _guess_audio_suffix(audio_bytes)

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
            tmp_in.write(audio_bytes)
            input_path = Path(tmp_in.name)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
            output_path = Path(tmp_out.name)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-ac",
            "1",
            "-ar",
            str(target_sr),
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise ValueError(f"ffmpeg conversion failed: {result.stderr.strip()}")

        waveform, sr = sf.read(output_path)
        waveform = np.asarray(waveform, dtype=np.float32)

        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)

        return waveform, sr

    finally:
        if input_path and input_path.exists():
            input_path.unlink()
        if output_path and output_path.exists():
            output_path.unlink()


def load_audio_from_bytes(
    audio_bytes: bytes, target_sr: int = TARGET_SR
) -> tuple[np.ndarray, int]:
    """
    Load uploaded audio bytes and convert to mono float waveform at target_sr.
    """
    if not audio_bytes:
        raise ValueError("Empty audio payload")

    # 1. Fast path: direct decode with soundfile
    try:
        with io.BytesIO(audio_bytes) as buffer:
            waveform, sr = sf.read(buffer)
    except Exception:
        # 2. Fallback: librosa from a temp file
        tmp_path: Path | None = None
        try:
            suffix = _guess_audio_suffix(audio_bytes)
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = Path(tmp.name)

            waveform, sr = librosa.load(tmp_path, sr=None, mono=True)

        except Exception:
            # 3. Robust fallback: ffmpeg conversion
            try:
                waveform, sr = _load_with_ffmpeg(audio_bytes, target_sr=target_sr)
            except Exception as exc:
                raise ValueError("Unsupported or unreadable audio format.") from exc

        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()

    waveform = np.asarray(waveform, dtype=np.float32)

    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)

    if sr != target_sr:
        waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    return waveform, sr