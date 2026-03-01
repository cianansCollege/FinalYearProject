import pandas as pd

INPUT = "speaker_master_with_coords.csv"
OUT_BAD = "coords_outside_ireland_bbox.csv"
OUT_MISSING = "coords_missing.csv"

# Generous bounding box covering island of Ireland
MIN_LAT, MAX_LAT = 51.0, 55.6
MIN_LON, MAX_LON = -11.2, -5.3

df = pd.read_csv(INPUT)

# Basic numeric coercion (in case strings slipped in)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

missing = df[df["latitude"].isna() | df["longitude"].isna()].copy()

outside = df[
    df["latitude"].notna()
    & df["longitude"].notna()
    & (
        (df["latitude"] < MIN_LAT)
        | (df["latitude"] > MAX_LAT)
        | (df["longitude"] < MIN_LON)
        | (df["longitude"] > MAX_LON)
    )
].copy()

print("Total rows:", len(df))
print("Missing coords:", len(missing))
print("Outside bbox:", len(outside))

if len(missing) > 0:
    missing.to_csv(OUT_MISSING, index=False)
    print("Wrote:", OUT_MISSING)

if len(outside) > 0:
    outside.to_csv(OUT_BAD, index=False)
    print("Wrote:", OUT_BAD)

# Optional: quick summary by county for outside rows (helps spot systematic errors)
if len(outside) > 0 and "native_county" in outside.columns:
    print("\nOutside bbox by native_county:")
    print(outside["native_county"].value_counts(dropna=False).head(30))
