import soundfile as sf

filename = "/Users/cianan/Documents/GitHub/FYP/Data/Prototype_Raw/en.carlow-kilkenny.kathleen-funchion.1.wav"
info = sf.info(filename)
print(info)