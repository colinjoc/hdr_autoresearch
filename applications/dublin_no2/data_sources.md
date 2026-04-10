# Data Sources — Dublin/Cork NO2 Source Attribution

## 1. EEA Air Quality In-Situ Measurement Station Data

- **Name**: EEA Air Quality hourly/daily/monthly/annual measurements (NO2, O3, SO2, PM10, PM2.5)
- **URL**: https://zenodo.org/records/14513586
- **Size**: Daily ~195 MB (parquet), Monthly ~13 MB, Annual ~1.4 MB; Hourly ~4 GB (zip)
- **License**: Creative Commons Attribution 4.0 International
- **Local paths**:
  - `data/daily_eu.parquet` — all EU daily data 2015-2023
  - `data/daily_ireland.parquet` — Ireland-only extract
  - `data/monthly_eu.parquet` — all EU monthly data 2015-2023
  - `data/annual_eu.parquet` — all EU annual data 2015-2023
- **Download commands**:
  ```
  wget "https://zenodo.org/records/14513586/files/airquality.no2.o3.so2.pm10.pm2p5_2.daily_pnt_20150101_20231231_eu_epsg.3035_v20240718.parquet" -O data/daily_eu.parquet
  wget "https://zenodo.org/records/14513586/files/airquality.no2.o3.so2.pm10.pm2p5_3.monthly_pnt_20150101_20231231_eu_epsg.3035_v20240718.parquet" -O data/monthly_eu.parquet
  wget "https://zenodo.org/records/14513586/files/airquality.no2.o3.so2.pm10.pm2p5_4.annual_pnt_20150101_20231231_eu_epsg.3035_v20240718.parquet" -O data/annual_eu.parquet
  ```

### Irish Stations Used

| EEA Code | EPA Name | Type | Location | Lat | Lon |
|----------|----------|------|----------|-----|-----|
| IE005AP | Winetavern Street | traffic/urban | Dublin city centre | 53.3458 | -6.2948 |
| IE0098A | Rathmines | background/urban | Dublin south | 53.3417 | -6.2889 |
| IE004AP | Pearse Street | traffic/urban | Dublin city centre | 53.3419 | -6.2141 |
| IE006AP | St John's Road West | traffic/urban | Dublin west | 53.3450 | -6.2543 |
| IE0131A | Blanchardstown (M50/N3) | traffic/suburban | Dublin NW | 53.3856 | -6.3699 |
| IE0132A | Dun Laoghaire | background/suburban | Dublin SE coast | 53.2858 | -6.1319 |
| IE0036A | Ballyfermot | background/suburban | Dublin SW | 53.3405 | -6.3523 |
| IE0028A | Clonskeagh | background/urban | Dublin south | 53.3539 | -6.2781 |
| IE0140A | Tallaght | background/suburban | Dublin SW | 53.2748 | -6.2224 |
| IE001BP | Cork Old Station Road | background/suburban | Cork city | 51.9111 | -8.4750 |
| IE013CK | Cork South Link Road | traffic/urban | Cork city | 51.9017 | -8.4621 |
| IE0090A | Lough Navar | background/rural-remote | Fermanagh | 54.0661 | -6.8831 |
| IE0111A | Moate | background/rural-regional | Westmeath | 53.1069 | -7.1964 |

## 2. Met Eireann Dublin Airport Hourly Weather

- **Name**: Dublin Airport synoptic station hourly observations
- **URL**: https://data.gov.ie/dataset/dublin-airport-hourly-data
- **Download URL**: https://clidata.met.ie/cli/climate_data/webdata/hly532.csv
- **Size**: ~50 MB CSV (80 years of hourly data)
- **License**: Creative Commons Attribution 4.0
- **Local path**: `data/dublin_airport_hourly.csv`, `data/dublin_airport_weather.parquet` (2015-2023 extract)
- **Variables**: Temperature, wind speed (kt), wind direction (deg), rain (mm), relative humidity (%), pressure (hPa), visibility (m), sunshine hours
- **Download command**:
  ```
  wget "https://clidata.met.ie/cli/climate_data/webdata/hly532.csv" -O data/dublin_airport_hourly.csv
  ```
