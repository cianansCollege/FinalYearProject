FYP Log Entry — Experiment 05: Recording Domain Classification (DAIL vs NI)

Objective

To test whether the model may be learning recording/domain characteristics (e.g., microphone, room acoustics, broadcast pipeline) rather than accent, by classifying the source dataset directly:

DAIL vs NI

This experiment helps identify potential domain confounding, especially given stronger performance on Ulster-related tasks.

⸻

Method
	•	Dataset: Cleaned 10s LUFS-normalised segments (N = 1674)
	•	Target label: dataset (two classes: DAIL, NI)
	•	Features:
	•	MFCC + delta statistics (mean, std, median, IQR)
	•	Model: Logistic Regression (class_weight="balanced")
	•	Evaluation: 5-fold StratifiedGroupKFold (speaker-safe, shuffle=True, random_state=42)

All other pipeline components were held constant to isolate whether recording-domain differences are learnable.

⸻

Results

Overall Performance
	•	Accuracy: 82%
	•	Weighted F1: 0.82
	•	Macro F1: 0.76

Per-Class Performance

Class	Precision	Recall	F1	Support
DAIL	0.89	0.86	0.88	1282
NI	0.60	0.67	0.63	392

Confusion Matrix

              Predicted
            DAIL     NI
Actual DAIL  1107    175
Actual NI     130    262


⸻

Interpretation

The model can distinguish DAIL vs NI recordings with 82% accuracy under speaker-safe splits, indicating a strong domain signal present in the data. This suggests that some portion of performance on province tasks—especially where province and dataset are correlated—may be influenced by recording conditions rather than accent alone.

However, domain and province are not perfectly aligned, meaning accent-related signal may still contribute. A province-by-dataset cross-tabulation showed:
	•	Leinster: entirely DAIL
	•	Munster: entirely DAIL
	•	Connacht: mostly DAIL with a small NI portion
	•	Ulster: split across both datasets (substantial NI and non-trivial DAIL)

This implies domain confounding is plausible and may inflate results for classes strongly associated with NI recordings, but it cannot fully explain province performance because Ulster includes a meaningful number of DAIL samples.

⸻

Conclusion

Experiment 05 demonstrates that recording domain (DAIL vs NI) is highly learnable from the audio features, confirming a substantial dataset/domain shift. This is an important validity finding for the project and should be discussed as:
	•	A potential confound in province classification
	•	A motivation for domain-robust evaluation (e.g., within-domain testing, domain adaptation, or controlling for dataset source)

This strengthens the experimental methodology and interpretation of subsequent province-based results.