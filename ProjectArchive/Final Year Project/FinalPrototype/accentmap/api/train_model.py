import os
import librosa
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# ==== CONFIG: CHANGE THESE PATHS ====

# Folder where your .wav files live
AUDIO_DIR = "/Users/cianan/Documents/GitHub/FYP/Prototype1/data/audio/"

# Path to your metadata CSV (the one you showed me)
METADATA_CSV = "/Users/cianan/Documents/GitHub/FYP/Prototype1/data/metadata.csv"   

# Where to save the trained model (inside the Django app)
OUTPUT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "rf_model.pkl")

# ====================================

print("Loading metadata from:", METADATA_CSV)

# Your sample shows TAB-separated columns, so we use sep="\t"
df = pd.read_csv(METADATA_CSV)

# Sanity check
print("Metadata rows:", len(df))
print("Columns:", df.columns.tolist())

X = []
y = []

for idx, row in df.iterrows():
    filename = row["filename"]
    # Use PROVINCE as the label for now
    label = row["province"]      # <- change to "constituency" later if you want

    audio_path = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(audio_path):
        print("WARNING: audio file not found:", audio_path)
        continue

    try:
        # Load audio
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        # Extract MFCC
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        feat_vec = np.mean(mfcc.T, axis=0)

        X.append(feat_vec)
        y.append(label)
    except Exception as e:
        print("ERROR processing", audio_path, ":", e)

X = np.array(X)
y = np.array(y)

print("\nFinished feature extraction.")
print("X shape:", X.shape)
print("y shape:", y.shape)
print("Unique labels:", np.unique(y))

if X.shape[0] == 0:
    raise RuntimeError("No training samples were loaded. Check paths/metadata.")

print("\nTraining Random Forest model...")
clf = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
)
clf.fit(X, y)

print("Saving model to:", OUTPUT_MODEL_PATH)
joblib.dump(clf, OUTPUT_MODEL_PATH)

print("\nTraining complete. Model saved successfully.")
