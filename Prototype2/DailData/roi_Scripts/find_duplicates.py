import pandas as pd

speakers = pd.read_csv("speaker_master.csv")
speakers["speaker_key"] = speakers["speaker_key"].astype("string").str.strip().str.lower()

dupes = speakers[speakers["speaker_key"].duplicated(keep=False)].sort_values("speaker_key")

print("Total rows in speaker_master:", len(speakers))
print("Unique speaker_key:", speakers["speaker_key"].nunique(dropna=True))
print("Duplicate rows:", len(dupes))
print("\nDuplicate speaker_keys (counts):")
print(dupes["speaker_key"].value_counts())

# Save a review file so you can open it easily
dupes.to_csv("speaker_master_DUPLICATES.csv", index=False)
print("\nWrote: speaker_master_DUPLICATES.csv")