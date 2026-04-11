# Data Sources — NYC Congestion Charge Effect Decomposition

## Primary Sources (all publicly downloadable, no authentication required)

### 1. NYC DOT Automated Traffic Volume Counts
- **Portal**: NYC Open Data
- **Dataset ID**: 7ym2-wayt
- **URL**: https://data.cityofnewyork.us/Transportation/Automated-Traffic-Volume-Counts/7ym2-wayt
- **API**: Socrata SODA — `https://data.cityofnewyork.us/resource/7ym2-wayt.json`
- **Fields**: RequestID, Boro, Yr, M, D, HH, MM, Vol, SegmentID, WktGeom, street, fromSt, toSt, Direction
- **Date range**: 2000--2026
- **Records downloaded**: 56,866 (Manhattan) + 45,320 (Bronx) + 50,000 (Brooklyn) + 50,000 (Queens) + 7,684 (Staten Island)
- **Downloaded**: 2026-04-10
- **Limitations**: Intermittent sampling — not every location is counted every week. Coverage varies by year and borough. Brooklyn has no post-charge data in our extract.

### 2. MTA Daily Ridership (Next-Day Estimates)
- **Portal**: New York State Open Data (data.ny.gov)
- **Dataset ID**: sayj-mze2
- **URL**: https://data.ny.gov/Transportation/MTA-Daily-Ridership-Data-2020-2025/vxuj-8kew
- **API**: Socrata SODA — `https://data.ny.gov/resource/sayj-mze2.json`
- **Modes**: Subway, Bus, LIRR, MNR, AAR, BT (Bridges & Tunnels), SIR, CRZ Entries, CBD Entries
- **CRZ Entries**: Daily vehicle count entering the Congestion Relief Zone, available from 2025-01-05
- **Date range**: 2024-01-01 to 2026-04-09
- **Records downloaded**: 6,722 mode-day records
- **Downloaded**: 2026-04-10

### 3. MTA Daily Ridership (Legacy, with pre-pandemic %)
- **Portal**: New York State Open Data (data.ny.gov)
- **Dataset ID**: vxuj-8kew
- **URL**: https://data.ny.gov/Transportation/MTA-Daily-Ridership-Data-2020-2025/vxuj-8kew
- **Date range**: 2021-01-01 to 2025-01-09
- **Records**: 1,776 days
- **Downloaded**: 2026-04-10

### 4. NYC TLC Trip Record Data
- **Portal**: NYC Taxi & Limousine Commission
- **URL**: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **CDN**: https://d37ci6vzurychx.cloudfront.net/trip-data/
- **Format**: Apache Parquet
- **Files downloaded**:
  - yellow_tripdata_2024-11.parquet (58 MB, 3,646,369 trips)
  - yellow_tripdata_2025-02.parquet (58 MB, 3,577,543 trips)
  - green_tripdata_2024-11.parquet (1.3 MB)
  - green_tripdata_2025-02.parquet (1.1 MB)
  - fhvhv_tripdata_2024-11.parquet (458 MB, ~20M trips)
  - fhvhv_tripdata_2025-02.parquet (441 MB, ~19M trips)
- **Key fields**: PULocationID, DOLocationID, tpep_pickup_datetime, cbd_congestion_fee (2025 only)
- **Downloaded**: 2026-04-10

### 5. TLC Taxi Zone Lookup
- **URL**: https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
- **Records**: 265 zones (5 boroughs + EWR + Unknown)
- **Downloaded**: 2026-04-10

## Key References

1. Cook et al. (2025). NBER WP 33584. "The Short-Run Effects of Congestion Pricing in New York City."
2. Fraser et al. (2025). npj Clean Air. "A first look into congestion pricing in the United States."
3. Streetsblog NYC (2025-03-12). "Data: Congestion Pricing is Not Rerouting Traffic to Other Boroughs."
