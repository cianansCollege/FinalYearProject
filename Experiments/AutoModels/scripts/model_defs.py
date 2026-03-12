"""
Defines all experiment model configurations.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


MODELS = {
    "logreg": "make_logreg",
    "logreg_weighted": "make_logreg_weighted",
    "rf": "make_rf",
    "knn_k1": "make_knn_k1",
    "knn_k3": "make_knn_k3",
    "knn_k5": "make_knn_k5",
    "knn_k7": "make_knn_k7",
    "knn_k11": "make_knn_k11",
    "svm_linear": "make_svm_linear",
    "svm_rbf": "make_svm_rbf",
    "nb": "make_nb",
}


def make_logreg():
    return LogisticRegression(
        max_iter=5000,
        random_state=42,
    )


def make_logreg_weighted():
    return LogisticRegression(
        max_iter=5000,
        class_weight="balanced",
        random_state=42,
    )


def make_rf():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
    )


def make_knn_k1():
    return KNeighborsClassifier(n_neighbors=1)


def make_knn_k3():
    return KNeighborsClassifier(n_neighbors=3)


def make_knn_k5():
    return KNeighborsClassifier(n_neighbors=5)


def make_knn_k7():
    return KNeighborsClassifier(n_neighbors=7)


def make_knn_k11():
    return KNeighborsClassifier(n_neighbors=11)


def make_svm_linear():
    return SVC(
        kernel="linear",
        probability=True,
        random_state=42,
    )


def make_svm_rbf():
    return SVC(
        kernel="rbf",
        probability=True,
        random_state=42,
    )


def make_nb():
    return GaussianNB()


def get_model(model_name: str):
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    return globals()[MODELS[model_name]]()