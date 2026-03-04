# FYP Log Entry — Experiment 03: Ulster vs Rest Ceiling Test

## Objective

To determine whether the dataset contains sufficient accent signal for reliable classification, or whether the previously observed ~40% accuracy (4-class province classification) reflects a fundamental data limitation.

This experiment tests a simplified binary classification task:

> **Ulster vs Other (Connacht + Leinster + Munster)**

The goal was to estimate an upper-bound performance ceiling under current feature representation.

---

## Method

* Dataset: Cleaned 10s LUFS-normalised speech segments (N = 1618)
* Features: MFCC + delta statistics (mean, std, median, IQR)
* Model: Logistic Regression (class_weight="balanced")
* Evaluation: StratifiedGroupKFold (5-fold, speaker-safe)

Binary label mapping:

* Ulster → "Ulster"
* All other provinces → "Other"

Speaker-safe splits ensured no speaker appeared in both training and testing sets.

---

## Results

### Overall Performance

* **Accuracy:** 77%
* **Macro F1:** 0.74
* **Weighted F1:** 0.77

### Per-Class Performance

| Class  | Precision | Recall | F1   | Support |
| ------ | --------- | ------ | ---- | ------- |
| Other  | 0.82      | 0.83   | 0.83 | 1077    |
| Ulster | 0.66      | 0.64   | 0.65 | 541     |

### Confusion Matrix

```
              Predicted
            Other  Ulster
Actual Other   898     179
Actual Ulster  194     347
```

---

## Interpretation

The model demonstrates strong separability between Ulster and non-Ulster speech, achieving 77% accuracy under speaker-safe evaluation.

This indicates:

* The dataset contains genuine accent signal.
* The previously observed 4-class performance (~40%) is not due to dataset collapse.
* The primary difficulty lies in separating the southern provinces (Connacht, Leinster, Munster), not in detecting accent structure overall.

---

## Conclusion

The binary ceiling test confirms that accent-related acoustic features are present and learnable within the dataset.

Therefore, limitations in 4-class classification are more likely due to:

* Province-level granularity,
* Acoustic similarity between southern regions,
* Or limitations of MFCC-based feature representation.

This experiment provides strong methodological validation of the dataset and evaluation pipeline.