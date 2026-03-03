FYP Log Entry — Experiment 04: Ulster / Leinster / Rest (3-Class Restructuring)

Objective

To evaluate whether restructuring province labels into broader regional groupings improves classification performance compared to the original 4-class task.

The 4-class baseline (~41% accuracy) showed strong confusion among southern provinces (Connacht, Leinster, Munster), while Ulster remained relatively separable.

This experiment tests a 3-class regional mapping:
	•	Ulster
	•	Leinster
	•	Rest (Connacht + Munster)

The goal was to determine whether reducing label granularity improves separability.

⸻

Method
	•	Dataset: Cleaned 10s LUFS-normalised speech segments (N = 1618)
	•	Feature representation:
	•	13 MFCC coefficients
	•	First-order deltas
	•	Mean, standard deviation, median, and IQR per coefficient
	•	Model: Logistic Regression (class_weight=“balanced”)
	•	Evaluation: StratifiedGroupKFold (5-fold, speaker-safe)

Label mapping:

Ulster   → Ulster
Leinster → Leinster
Connacht → Rest
Munster  → Rest

All other aspects of the pipeline were kept constant to isolate the effect of label restructuring.

⸻

Results

Overall Performance
	•	Accuracy: 47%
	•	Macro F1: 0.48
	•	Weighted F1: 0.48

This represents a modest improvement over the 4-class baseline (~41%).

⸻

Per-Class Performance

Class	Precision	Recall	F1	Support
Rest	0.40	0.35	0.38	596
Leinster	0.37	0.50	0.43	481
Ulster	0.69	0.58	0.63	541

Ulster remains the strongest-performing class.

⸻

Confusion Matrix

              Predicted
            Rest  Leinster  Ulster
Actual Rest     210     295       91
Actual Leinster 193     240       48
Actual Ulster   119     106      316


⸻

Interpretation

1. Ulster remains clearly separable

Ulster maintains strong performance, consistent with previous experiments.

2. Leinster vs Rest remains highly confusable

The dominant pattern in the confusion matrix is mutual misclassification between:
	•	Rest → Leinster (295)
	•	Leinster → Rest (193)

This indicates that even after merging Connacht and Munster, the southern regions remain acoustically overlapping under the current feature representation.

3. Label restructuring yields only modest gains

Accuracy improved from ~41% (4-class) to ~47% (3-class), suggesting:
	•	Reducing granularity helps,
	•	But does not fundamentally resolve southern class overlap.

⸻

Conclusion

The 3-class regional restructuring confirms:
	•	Accent signal is strongest in distinguishing Ulster from other regions.
	•	Southern province-level distinctions remain difficult under MFCC-based features.
	•	Performance gains from label merging are incremental rather than transformative.

This supports the broader experimental narrative:
	•	The dataset contains macro-regional accent structure,
	•	But fine-grained province-level separation is weak under classical acoustic feature modelling.