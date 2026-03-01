# FYP Log Entry — Experiment 01: 4-Class Province Baseline

## Objective

To establish a speaker-safe baseline performance for province-level accent classification using standard MFCC-based acoustic features.

Target classes:

* Connacht
* Leinster
* Munster
* Ulster

This experiment establishes the initial performance ceiling before feature modifications.

---

## Method

* Dataset: Cleaned 10s LUFS-normalised speech segments (N = 1618)
* Features:

  * 13 MFCC coefficients
  * First-order deltas
  * Summary statistics: mean and standard deviation
* Total feature dimension: 52
* Model: Logistic Regression (class_weight="balanced")
* Evaluation: StratifiedGroupKFold (5-fold, speaker-safe)

Speaker-safe cross-validation ensured no speaker appeared in both train and test folds.

---

## Results

### Overall Performance

* **Accuracy:** ~41%
* **Macro F1:** ~0.37
* **Weighted F1:** ~0.42

### Class Behaviour

| Province | F1 Score (approx.) |
| -------- | ------------------ |
| Ulster   | ~0.62              |
| Leinster | ~0.43              |
| Connacht | ~0.23              |
| Munster  | ~0.21              |

### Observed Pattern

* Ulster shows consistent separability.
* Strong confusion between Connacht, Leinster, and Munster.
* Southern provinces form an overlapping cluster.

---

## Interpretation

The baseline confirms:

* Accent signal exists (Ulster distinguishable).
* Southern province-level classification is substantially more difficult.
* MFCC mean/std summaries may not capture sufficient discriminative structure for fine-grained regional separation.

This establishes a robust, reproducible baseline for further experimentation.

---