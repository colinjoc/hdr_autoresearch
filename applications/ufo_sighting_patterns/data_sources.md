# Data sources — UFO-1 NUFORC sighting pattern analysis

## Primary

1. **NUFORC Structured Reports (HuggingFace kcimc/NUFORC)**
   - Path: `data/raw/nuforc_str.csv` (168 MB, 147,890 rows)
   - Fields: Sighting ID, Occurred (datetime), Location (city/state/country), Shape, Duration, No of observers, Reported, Posted, Characteristics, Summary, Text, Location details, Explanation
   - Coverage: 1400-2024 (practically 1950s-2024)
   - Shapes: 15+ categories (Light 27k, Circle 14k, Triangle 13k, Fireball 10k, Disk 9k, Sphere 8k, etc.)

2. **NUFORC Geocoded Reports (Kaggle/planetsig)**
   - Path: `data/raw/nuforc_kaggle.csv` (14 MB, 80,332 rows)
   - Fields: datetime, city, state, country, shape, duration_sec, duration_text, description, date_posted, latitude, longitude
   - Coverage: 1910-2013
   - 100% geocoded (lat/lon for every row)
   - Countries: US (65k), Canada (3k), UK (2k), Australia (500+)

## Analysis strategy

- Use `nuforc_str.csv` (147k rows) as main dataset for temporal/shape/duration analysis
- Use `nuforc_kaggle.csv` (80k rows with lat/lon) for spatial analysis
- Parse location strings from nuforc_str for approximate geocoding of the 2014-2024 additions

## Cross-reference datasets needed

- US military base locations (publicly available from DoD)
- Major airport locations (FAA/IATA)
- Starlink launch dates (SpaceX public schedule, 2019-2024)
- ISS visible passes (Heavens-Above archive)
- Population by county (US Census)
- Satellite re-entry events (Aerospace Corporation public list)

## Smoke-test (2026-04-18)

- nuforc_str.csv: 147,890 rows confirmed loadable
- nuforc_kaggle.csv: 80,332 rows with lat/lon confirmed
- Both freely available, no credentials required
