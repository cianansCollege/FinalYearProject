import joblib
import numpy as np

from plugins.base import ModelPlugin
from services.wav2vec_features import audio_bytes_to_embedding


class Wav2VecUlsterVsRestRF(ModelPlugin):
    id = "wav2vec_ulster_vs_rest_rf"
    name = "Ulster Detection (Wav2Vec + Random Forest)"
    description = "Predicts whether a speaker is from Ulster."

    def __init__(self):
        self.model = joblib.load("backend/artifacts/wav2vec_ulster_vs_rest_rf_model.joblib")
        self.label_encoder = joblib.load("backend/artifacts/wav2vec_ulster_vs_rest_rf_label_encoder.joblib")

    def predict(self, audio_bytes: bytes):
        embedding = audio_bytes_to_embedding(audio_bytes)

        probs = self.model.predict_proba([embedding])[0]
        pred_idx = np.argmax(probs)

        label = self.label_encoder.inverse_transform([pred_idx])[0]

        return {
            "label": label,
            "confidence": float(probs[pred_idx]),
            "probabilities": {
                self.label_encoder.inverse_transform([i])[0]: float(p)
                for i, p in enumerate(probs)
            }
        }