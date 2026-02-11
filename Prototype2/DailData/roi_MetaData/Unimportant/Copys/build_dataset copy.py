from __future__ import annotations

from pathlib import Path
import pandas as pd


DATA_DIR = Path(".")
FILES_CSV = DATA_DIR / "dail_speaker_files.csv"
SPEAKERS_CSV = DATA_DIR / "speaker_master.csv"
COORDS_CSV = DATA_DIR / "constituency_coordinates.csv"

OUT_ALL = DATA_DIR / "final_dataset_all.csv"
OUT_MODEL = DATA_DIR / "final_dataset_model.csv"


def clean_text(s: pd.Series) -> pd.Series:
    """
    Normalise join keys:
    - convert to pandas string dtype
    - strip leading/trailing whitespace
    - collapse internal whitespace
    """
    s = s.astype("string")
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    return s


def province_from_constituency_2022(constituency: str) -> str | None:
    """
    2022 constituency -> province mapping.
    ASCII, hyphen '-' style (matches your master sheet choices).
    """
    if constituency is None:
        return None
    c = str(constituency).strip()
    if not c:
        return None

    leinster = {
        "Carlow-Kilkenny",
        "Dublin Bay North",
        "Dublin Bay South",
        "Dublin Central",
        "Dublin Fingal",
        "Dublin Mid-West",
        "Dublin North-West",
        "Dublin Rathdown",
        "Dublin South-Central",
        "Dublin South-West",
        "Dublin West",
        "Dun Laoghaire",
        "Kildare North",
        "Kildare South",
        "Laois",
        "Longford-Westmeath",
        "Louth",
        "Meath East",
        "Meath West",
        "Offaly",
        "Wexford",
        "Wicklow",
    }

    munster = {
        "Clare",
        "Cork East",
        "Cork North-Central",
        "Cork North-West",
        "Cork South-Central",
        "Cork South-West",
        "Kerry",
        "Limerick City",
        "Limerick County",
        "Tipperary",
        "Waterford",
    }

    connacht = {
        "Galway East",
        "Galway West",
        "Mayo",
        "Roscommon-Galway",
        "Sligo-Leitrim",
    }

    ulster = {
        "Donegal",
        "Cavan-Monaghan",
    }

    if c in leinster:
        return "Leinster"
    if c in munster:
        return "Munster"
    if c in connacht:
        return "Connacht"
    if c in ulster:
        return "Ulster"
    return None


def main() -> None:
    # -----------------------
    # Load CSVs
    # -----------------------
    files = pd.read_csv(FILES_CSV)
    speakers = pd.read_csv(SPEAKERS_CSV)
    coords = pd.read_csv(COORDS_CSV)

    # -----------------------
    # Validate required columns
    # -----------------------
    req_files = {"filename", "speaker_raw", "speaker_key"}
    req_speakers = {"speaker_key", "constituency", "non_td_role", "gender"}
    req_coords = {"constituencies", "x_coordinates", "y_coordinates"}

    missing_files = req_files - set(files.columns)
    missing_speakers = req_speakers - set(speakers.columns)
    missing_coords = req_coords - set(coords.columns)

    if missing_files:
        raise KeyError(f"{FILES_CSV} missing columns: {sorted(missing_files)}")
    if missing_speakers:
        raise KeyError(f"{SPEAKERS_CSV} missing columns: {sorted(missing_speakers)}")
    if missing_coords:
        raise KeyError(f"{COORDS_CSV} missing columns: {sorted(missing_coords)}")

    # -----------------------
    # Standardise column names for joining
    # -----------------------
    coords = coords.rename(
        columns={
            "constituencies": "constituency",
            "x_coordinates": "lon",
            "y_coordinates": "lat",
        }
    )

    # -----------------------
    # Clean join keys
    # -----------------------
    # speaker_key should be consistent lowercase, trimmed
    files["speaker_key"] = clean_text(files["speaker_key"]).str.lower()
    speakers["speaker_key"] = clean_text(speakers["speaker_key"]).str.lower()

    # constituency: trimmed; keep original case formatting as in your master
    speakers["constituency"] = clean_text(speakers["constituency"])
    coords["constituency"] = clean_text(coords["constituency"])

    # Also trim filename/speaker_raw for cleanliness
    files["filename_raw"] = files["filename"]
    files["filename"] = clean_text(files["filename"])
    files["speaker_raw"] = clean_text(files["speaker_raw"])

    # Convert lon/lat to numeric (coerce errors to NaN)
    coords["lon"] = pd.to_numeric(coords["lon"], errors="coerce")
    coords["lat"] = pd.to_numeric(coords["lat"], errors="coerce")

    # -----------------------
    # Join 1: files -> speakers (many files to one speaker)
    # -----------------------
    merged = files.merge(
        speakers,
        on="speaker_key",
        how="left",
        validate="many_to_one",
        suffixes=("", "_speaker"),
    )

    # -----------------------
    # Join 2: add coordinates (many speakers/files to one constituency row)
    # -----------------------
    merged = merged.merge(
        coords,
        on="constituency",
        how="left",
        validate="many_to_one",
        suffixes=("", "_coords"),
    )

    # -----------------------
    # Add province (2022)
    # -----------------------
    merged["province"] = merged["constituency"].apply(
        lambda x: province_from_constituency_2022(x) if pd.notna(x) else None
    )

    # -----------------------
    # Diagnostics
    # -----------------------
    print("\n=== JOIN DIAGNOSTICS ===")
    print("Rows (audio files):", len(merged))
    print("Unique speakers in files:", merged["speaker_key"].nunique(dropna=True))

    missing_speaker_meta = merged["native_place"].isna().sum()
    print("Rows missing speaker_master match (native_place is NaN):", missing_speaker_meta)

    missing_const = merged["constituency"].isna().sum()
    print("Rows missing constituency:", missing_const)

    missing_prov = merged["province"].isna().sum()
    print("Rows missing province:", missing_prov)

    missing_coords = merged["lat"].isna().sum() + merged["lon"].isna().sum()
    print("Rows missing lat/lon (either missing):", missing_coords)

    # Identify constituencies that did not match the coordinate table
    unmatched_const = merged.loc[
        merged["constituency"].notna() & (merged["lat"].isna() | merged["lon"].isna()),
        "constituency",
    ].dropna().unique()

    if len(unmatched_const) > 0:
        print("\nConstituencies present in speaker_master but missing in constituency_coordinates:")
        for c in sorted(unmatched_const):
            print(" -", c)

    # -----------------------
    # Save ALL rows
    # -----------------------
    merged.to_csv(OUT_ALL, index=False)
    print("\nWrote:", OUT_ALL)

    # -----------------------
    # Build MODEL dataset:
    # - exclude non-TDs
    # - require constituency + province
    # -----------------------
    model = merged.copy()

    # Mark TD rows: treat non_td_role blank/NaN as "is TD"
    model["non_td_role"] = clean_text(model["non_td_role"])
    is_td = model["non_td_role"].isna() | (model["non_td_role"] == "")

    model = model[is_td]
    model = model.dropna(subset=["constituency", "province"])

    model.to_csv(OUT_MODEL, index=False)
    print("Wrote:", OUT_MODEL)

    print("\n=== MODEL DATASET SUMMARY ===")
    print("Rows (TD clips):", len(model))
    print("Unique TD speakers:", model["speaker_key"].nunique(dropna=True))
    print("\nClips per province:")
    print(model["province"].value_counts())

    print("\nTop 15 constituencies by clip count:")
    print(model["constituency"].value_counts().head(15))


if __name__ == "__main__":
    main()
