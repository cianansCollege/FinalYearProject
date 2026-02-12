import numpy as np
import librosa
import pandas as pd
import os

meta = pd.read_csv("/Users/cianan/Documents/GitHub/FYP/Prototype1/data/metadata.csv")
audio_folder = "/Users/cianan/Documents/GitHub/FYP/Prototype1/data/audio/"
features = []

for i, row in meta.iterrows():
    path = os.path.join(audio_folder, row['filename'])
    y, sr = librosa.load(path, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)
    features.append(mfcc_mean)

mfcc_df = pd.DataFrame(features, columns=[f"mfcc_{i+1}" for i in range(13)])
df = pd.concat([meta, mfcc_df], axis=1)
df.to_csv("/Users/cianan/Documents/GitHub/FYP/Prototype1/features/mfcc_features.csv", index=False)
print(" MFCC feature file saved!")
