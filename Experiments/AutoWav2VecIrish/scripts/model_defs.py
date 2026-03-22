"""
Defines simple downstream classifiers for wav2vec embeddings.
"""

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODELS = {
    "logreg": "make_logreg",
    "logreg_weighted": "make_logreg_weighted",
}


def make_logreg():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=10000,
            random_state=42,
        )),
    ])


def make_logreg_weighted():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=10000,
            class_weight="balanced",
            random_state=42,
        )),
    ])


def get_model(model_name: str):
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}")
    return globals()[MODELS[model_name]]()