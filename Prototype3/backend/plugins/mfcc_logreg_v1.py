"""Placeholder for an MFCC + Logistic Regression model plugin implementation."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from plugins.base import ModelPlugin
from services.audio import load_audio_from_bytes
from services.features import extract_mfcc_summary_features


class MFCCLogRegV1(ModelPlugin):
    id = "mfcc_logreg_v1"
    name = "MFCC + Logistic Regression (v1)"
    description = "MFCC summary features with a Logistic Regression classifier."

    def __init__(self) -> None:
        model_dir = Path(__file__).resolve().parent.parent / "artifacts"

        self.model = joblib.load(model_dir / "mfcc_logreg_model.joblib")
        self.label_encoder = joblib.load(model_dir / "label_encoder.joblib")

    def predict(self, audio_bytes: bytes) -> dict:
        waveform, sr = load_audio_from_bytes(audio_bytes)
        features = extract_mfcc_summary_features(waveform, sr)

        X = features.reshape(1, -1)

        probs = self.model.predict_proba(X)[0]
        pred_index = int(np.argmax(probs))
        pred_label = str(self.label_encoder.inverse_transform([pred_index])[0])
        confidence = float(probs[pred_index])

        labels = self.label_encoder.classes_
        prob_list = [
            {"label": str(label), "p": float(prob)}
            for label, prob in zip(labels, probs)
        ]
        prob_list.sort(key=lambda item: item["p"], reverse=True)

        return {
            "label": pred_label,
            "confidence": confidence,
            "probs": prob_list,
        }


plugin = MFCCLogRegV1()