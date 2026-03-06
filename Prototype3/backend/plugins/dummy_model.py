from __future__ import annotations

from plugins.base import ModelPlugin


class DummyModel(ModelPlugin):
    id = "dummy_v1"
    name = "Dummy Model (v1)"
    description = "Test model for frontend-backend integration."

    def predict(self, wav_bytes: bytes) -> dict:
        return {
            "label": "Leinster",
            "confidence": 0.75,
            "probs": [
                {"label": "Leinster", "p": 0.75},
                {"label": "Munster", "p": 0.15},
                {"label": "Connacht", "p": 0.07},
                {"label": "Ulster", "p": 0.03},
            ],
        }


plugin = DummyModel()