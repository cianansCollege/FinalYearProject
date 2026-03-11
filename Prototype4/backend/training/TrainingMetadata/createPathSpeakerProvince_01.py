import pandas as pd

input_csv = "/Users/cianan/Documents/College/GitHub/FYP/Data/speaker_master_clean_10s_lufs.csv"
output_csv = "training_minimal_clean_01.csv"

df = pd.read_csv(input_csv)

df_small = df[["segment_file_clean", "speaker", "native_province", "dataset"]].copy()

df_small = df_small.rename(columns={
    "segment_file_clean": "filepath",
    "native_province": "label"
})

df_small.to_csv(output_csv, index=False)

print(f"Saved cleaned CSV to {output_csv}")
print(df_small.head())