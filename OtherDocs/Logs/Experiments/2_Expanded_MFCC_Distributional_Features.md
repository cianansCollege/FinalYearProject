# FYP Log Entry — Experiment 02: Expanded MFCC Distributional Features

## Objective

To test whether richer statistical summaries of MFCC coefficients improve province-level classification performance.

The hypothesis was that capturing distribution shape (rather than only mean and variance) might better represent accent variation.

---

## Method

Starting from Experiment 01, the feature representation was expanded.

Features included:

* 13 MFCC coefficients
* First-order deltas
* Summary statistics per coefficient:

  * Mean
  * Standard deviation
  * Median
  * Interquartile range (IQR)

Total feature dimension increased from:

* 52 → 104 features

Model and evaluation protocol remained identical:

* Logistic Regression (class_weight="balanced")
* StratifiedGroupKFold (speaker-safe)

No other variables were changed.

---

## Results

### Overall Performance

* **Accuracy:** ~40%
* **Macro F1:** ~0.37
* No statistically meaningful improvement over baseline.

### Observed Pattern

* Confusion structure remained nearly identical to Experiment 01.
* Ulster still separable.
* Southern provinces continued to exhibit heavy mutual confusion.

---

## Interpretation

Adding distributional statistics (median and IQR) did not materially improve classification performance.

This suggests:

* The limiting factor is unlikely to be simple statistical summarisation of MFCCs.
* Either:

  * Province-level granularity exceeds separability under MFCC representation,
  * Or additional acoustic/prosodic information is required.

This negative result is methodologically valuable, as it isolates feature representation as a likely constraint rather than data quality or evaluation leakage.

---

# Combined Experimental Narrative (What This Now Shows)

1. **Experiment 01:** 4-class baseline ≈ 41%
2. **Experiment 02:** Richer MFCC stats → no improvement
3. **Experiment 03:** Binary Ulster vs Rest → 77%

This progression demonstrates:

* The dataset contains strong accent signal.
* Ulster speech is acoustically distinguishable.
* Fine-grained southern province separation is the core challenge.

This is now a coherent, defensible experimental trajectory.