import librosa
import pandas as pd
import os

meta = pd.read_csv("/Users/cianan/Documents/GitHub/FYP/Prototype1/data/metadata.csv")
audio_folder = "/Users/cianan/Documents/GitHub/FYP/Prototype1/data/audio/"

for i, row in meta.iterrows():
    path = os.path.join(audio_folder, row['filename'])
    y, sr = librosa.load(path, sr=None, mono=True)
    print(f"{row['filename']}: {sr} Hz, length {len(y)/sr:.2f}s")
