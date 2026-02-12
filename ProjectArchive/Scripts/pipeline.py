import os
import librosa            # audio processing library
import soundfile as sf     # for writing audio files
import numpy as np         # numerical operations
import pandas as pd        # CSV/metadata handling
from sklearn.model_selection import train_test_split

# CONFIGURATION SECTION
RAW_FOLDER = "~/Users/cianan/Documents/GitHub/FYP/Data/prototype_raw"
PROCESSED_FOLDER = "~/Users/cianan/Documents/GitHub/FYP/Data/prototype_processed "
FEATURES_FOLDER = "~/Users/cianan/Documents/GitHub/FYP/Data/prototype_features"
METADATA_FOLDER = "~/Users/cianan/Documents/GitHub/FYP/Data/Prototype_Metadata"

# Audio preprocessing parameters
SAMPLE_RATE = 16000       # target sample rate for all clips
N_MFCC = 13               # number of MFCC features to extract

# Dataset split parameters
TEST_SIZE = 0             # fraction for test set
VAL_SIZE = 0.15           # fraction for validation set
RANDOM_STATE = 42         # ensures reproducibility of random splits

# Make sure the output folders exist (creates them if missing)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(FEATURES_FOLDER, exist_ok=True)

# Load the master CSV containing information about each clip
metadata_file = os.path.join(METADATA_FOLDER, "dataset.csv")
df = pd.read_csv(metadata_file)

print(f"Loaded metadata for {len(df)} clips.")

# ==============================
# AUDIO PREPROCESSING
# ==============================
# Preprocess all clips: resample, convert to mono, normalize volume
print("Starting audio preprocessing...")

for row in df.itertuples():
    infile = os.path.join(RAW_FOLDER, row.filename)   # original clip
    outfile = os.path.join(PROCESSED_FOLDER, row.filename)  # processed output

    # Skip if already processed (saves time when rerunning)
    if not os.path.exists(outfile):
        # librosa.load automatically converts to mono if mono=True
        y, sr = librosa.load(infile, sr=SAMPLE_RATE, mono=True)

        # Normalize audio amplitude to -1 to 1
        y = y / max(abs(y))

        # Write processed clip to output folder
        sf.write(outfile, y, SAMPLE_RATE)

print("Audio preprocessing complete!")

# ==============================
# FEATURE EXTRACTION (MFCCs)
# ==============================
# Extract MFCC features from each processed clip
print("Extracting MFCC features...")

for filename in os.listdir(PROCESSED_FOLDER):
    if filename.endswith(".wav"):
        filepath = os.path.join(PROCESSED_FOLDER, filename)

        # Load audio again (already mono + 16 kHz)
        y, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)

        # Compute MFCC features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)

        # Save MFCC as .npy file for fast loading later
        feature_file = os.path.join(FEATURES_FOLDER, filename.replace(".wav", ".npy"))
        np.save(feature_file, mfccs)

print(f"Extracted MFCCs for {len(os.listdir(FEATURES_FOLDER))} clips.")

print("Splitting dataset into train/validation/test...")

# Use 'province' as stratification if available to preserve distribution
stratify_col = df['province'] if 'province' in df.columns else None

# Split off test set
train_df, test_df = train_test_split(
    df, test_size=TEST_SIZE, stratify=stratify_col, random_state=RANDOM_STATE
)

# Split remaining train into train + validation
train_df, val_df = train_test_split(
    train_df, test_size=VAL_SIZE, stratify=train_df['province'] if 'province' in df.columns else None, random_state=RANDOM_STATE
)

# Save CSV files for each split
train_df.to_csv(os.path.join(METADATA_FOLDER, "train.csv"), index=False)
val_df.to_csv(os.path.join(METADATA_FOLDER, "val.csv"), index=False)
test_df.to_csv(os.path.join(METADATA_FOLDER, "test.csv"), index=False)

print("Dataset split complete!")
print(f"Training clips: {len(train_df)}")
print(f"Validation clips: {len(val_df)}")
print(f"Test clips: {len(test_df)}")

# ==============================
# SUMMARY
# ==============================
print("Pipeline complete!")
print(f"Processed audio clips saved in '{PROCESSED_FOLDER}'")
print(f"MFCC feature files saved in '{FEATURES_FOLDER}'")
print(f"Train/val/test CSVs saved in '{METADATA_FOLDER}'")
