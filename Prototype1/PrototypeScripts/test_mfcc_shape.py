import librosa
import numpy as np

def test_mfcc_shape(path):
    y, sr = librosa.load(path, sr=16000, mono=True)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    print("MFCC shape:", mfcc.shape)
    print("Data type:", type(mfcc))
    print("Contains NaN:", np.isnan(mfcc).any())
    print("Contains Inf:", np.isinf(mfcc).any())

    # Expected: 13 coefficient rows
    if mfcc.shape[0] != 13:
        raise ValueError("MFCC extraction error: Expected 13 coefficients.")

    # Expected: at least one frame
    if mfcc.shape[1] < 1:
        raise ValueError("MFCC extraction error: No frames extracted.")

    return "MFCC test passed!"

print(test_mfcc_shape("/Users/cianan/Documents/GitHub/FYP/Prototype1/data/audio/en.carlow-kilkenny.kathleen-funchion.1.wav"))
