from pathlib import Path

import joblib
import numpy as np

from plugins.base import ModelPlugin
from services.wav2vec_features import audio_bytes_to_embedding

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BASE_DIR / "artifacts"


class Wav2VecUlsterVsRestRF(ModelPlugin):
    id = "wav2vec_ulster_vs_rest_rf"
    name = "Ulster Detection (Wav2Vec)"
    description = "Detects whether the speaker is from Ulster."

    def __init__(self):
        self.model = joblib.load(
            ARTIFACTS_DIR / "wav2vec_ulster_vs_rest_rf_model.joblib"
        )
        self.label_encoder = joblib.load(
            ARTIFACTS_DIR / "wav2vec_ulster_vs_rest_rf_label_encoder.joblib"
        )

    def predict(self, audio_bytes: bytes):
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
        probs_list.sort(key=lambda item: item["p"], reverse=True)

        return {
            "label": str(label),
            "confidence": float(probs[pred_idx]),
            "probs": probs_list,
        }
