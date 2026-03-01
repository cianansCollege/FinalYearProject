import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# -------- CONFIG --------
INPUT_CSV = "/Users/cianan/Documents/College/GitHub/FYP/Prototype2/all_segments_index_with_resolved_paths.csv"
OUTPUT_CSV = "speaker_master_with_coords.csv"
USER_AGENT = "fyp_accent_mapping_project"
# ------------------------

# Load CSV
df = pd.read_csv(INPUT_CSV)

# Combine city + county
df["location_query"] = (
    df["native_city"].fillna("").str.strip() + ", " +
    df["native_county"].fillna("").str.strip() +
    ", Ireland"
)

# Remove extra commas if city missing
df["location_query"] = df["location_query"].str.replace(r"^,\s*", "", regex=True)
df["location_query"] = df["location_query"].str.replace(r",\s*,", ",", regex=True)

# Setup geocoder
geolocator = Nominatim(user_agent=USER_AGENT)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Dictionary cache to avoid duplicate lookups
cache = {}

latitudes = []
longitudes = []

for location in df["location_query"]:
    if location in cache:
        lat, lon = cache[location]
    else:
        try:
            result = geocode(location)
            if result:
                lat, lon = result.latitude, result.longitude
            else:
                lat, lon = None, None
            cache[location] = (lat, lon)
        except Exception as e:
            print(f"Error geocoding {location}: {e}")
            lat, lon = None, None

    latitudes.append(lat)
    longitudes.append(lon)
    print(f"{location} → {lat}, {lon}")

df["latitude"] = latitudes
df["longitude"] = longitudes

df.drop(columns=["location_query"], inplace=True)

df.to_csv(OUTPUT_CSV, index=False)

print("Done.")
