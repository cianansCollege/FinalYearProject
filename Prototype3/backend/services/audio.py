# Audio decoding, normalization, and resampling helpers for inference input.

from __future__ import annotations

import io

import librosa
import numpy as np
import soundfile as sf


TARGET_SR = 16000


def load_audio_from_bytes(audio_bytes: bytes, target_sr: int = TARGET_SR) -> tuple[np.ndarray, int]:
    """
    Load uploaded audio bytes and convert to mono float waveform at target_sr.
    """
    with io.BytesIO(audio_bytes) as buffer:
        waveform, sr = sf.read(buffer)

    waveform = np.asarray(waveform, dtype=np.float32)

    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)

    if sr != target_sr:
        waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    return waveform, sr