"""
Defines trimmed global experiment model configurations.
Scaled pipelines are used for models that benefit from feature scaling.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


MODELS = {
    "logreg": "make_logreg",
    "logreg_weighted": "make_logreg_weighted",
    "rf": "make_rf",
    "knn_k5": "make_knn_k5",
    "svm_rbf": "make_svm_rbf",
    "svm_linear": "make_svm_linear",
    "nb": "make_nb",
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


def make_rf():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
    )


def make_knn_k5():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", KNeighborsClassifier(n_neighbors=5)),
    ])


def make_svm_rbf():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(
            kernel="rbf",
            probability=True,
            random_state=42,
        )),
    ])


def make_nb():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GaussianNB()),
    ])

def make_svm_linear():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(
            kernel="linear",
            probability=True,
            random_state=42,
        )),
    ])

def get_model(model_name: str):
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    return globals()[MODELS[model_name]]()