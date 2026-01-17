import soundfile as sf
import os

def display_clips_info(folder):
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        try:
            info = sf.info(filepath)
            print(f"{filename}: {info}\n\n")
        except RuntimeError:
            print(f"Could not read {filename}")

folder = "/Users/cianan/Documents/GitHub/FYP/Data/Prototype_Raw"
display_clips_info(folder)
