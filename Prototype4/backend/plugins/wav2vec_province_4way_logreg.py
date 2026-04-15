from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from plugins.base import ModelPlugin
from services.wav2vec_features import audio_bytes_to_embedding

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"


class Wav2VecProvince4WayLogReg(ModelPlugin):
    id = "wav2vec_province_4way_logreg"
    name = "Four Provinces — Wav2Vec + Logistic Regression"
    description = "Four-class accent classifier for Connacht, Leinster, Munster, and Ulster."

    def __init__(self) -> None:
        self.model = joblib.load(
            ARTIFACTS_DIR / "wav2vec_province_4way_logreg_model.joblib"
        )
        self.label_encoder = joblib.load(
            ARTIFACTS_DIR / "wav2vec_province_4way_logreg_label_encoder.joblib"
        )

    def predict(self, audio_bytes: bytes) -> dict:
        embedding = audio_bytes_to_embedding(audio_bytes)

        probs = self.model.predict_proba([embedding])[0]
        pred_idx = int(np.argmax(probs))
        label = self.label_encoder.inverse_transform([pred_idx])[0]

        probs_list = [
            {
                "label": str(self.label_encoder.inverse_transform([i])[0]),
                "p": float(p),
            }
            for i, p in enumerate(probs)
        ]
        probs_list.sort(key=lambda x: x["p"], reverse=True)

        return {
            "label": str(label),
            "confidence": float(probs[pred_idx]),
            "probs": probs_list,
        }