# Data Sources — DART Punctuality Cascade Prediction

## Primary Sources

### 1. NTA GTFS-Realtime Feeds
- **Name**: National Transport Authority GTFS-Realtime
- **URL**: https://developer.nationaltransport.ie/
- **Format**: Protocol Buffer (GTFS-RT spec)
- **Contents**: Vehicle positions, trip updates, service alerts for DART, Irish Rail, Dublin Bus, Luas, Bus Eireann, Go-Ahead Ireland
- **License**: Open Government Licence (Ireland)
- **Limitation**: **Real-time only — no historical archive.** The feed provides current positions and predictions but does not store historical data. A multi-month collection campaign would be required to build a historical dataset. This project uses synthetic data instead.
- **Rate limits**: Polling recommended every 30 seconds; API key required

### 2. NTA GTFS Static
- **Name**: National Transport Authority GTFS Static
- **URL**: https://developer.nationaltransport.ie/
- **Format**: GTFS (CSV zipped)
- **Contents**: Scheduled timetables, stop locations, route definitions, calendar
- **License**: Open Government Licence (Ireland)
- **Local path**: Not used (synthetic data calibrated to published reports)

### 3. Irish Rail Punctuality Reports
- **Name**: Irish Rail Train Punctuality & Reliability Performance
- **URL**: https://www.irishrail.ie/en-ie/about-us/train-punctuality-reliability-performance
- **Format**: Monthly PDF reports
- **Contents**: Monthly aggregate punctuality by route (DART commuter, InterCity, Commuter)
- **Key data points used**:
  - June 2024: 92.8% on-time (DART)
  - October 2024: 64.5% on-time (DART)
  - Monthly figures 2023-2025 (see data_loaders.py MONTHLY_PUNCTUALITY dict)
- **License**: Public information
- **Note**: These monthly aggregates calibrate our synthetic daily dataset

### 4. Met Eireann Weather Observations
- **Name**: Met Eireann Historical Weather Data
- **URL**: https://www.met.ie/climate/available-data/historical-data
- **Format**: CSV
- **Contents**: Hourly observations from Dublin Airport, Casement Aerodrome, Phoenix Park
- **Variables**: Wind speed, wind direction, rainfall, temperature, relative humidity
- **License**: Creative Commons Attribution 4.0
- **Local path**: Not directly used (synthetic weather calibrated to Dublin Airport climatology)
- **Download**: `wget https://cli.fusio.net/cli/climate_data/webdata/dly3904.csv` (Dublin Airport daily)

### 5. Met Eireann Open Data
- **Name**: Met Eireann on data.gov.ie
- **URL**: https://data.gov.ie/organization/met-eireann
- **Format**: CSV/JSON
- **License**: Creative Commons Attribution 4.0

## Secondary Sources

### 6. Irish Rail Network Map
- **URL**: https://www.irishrail.ie/en-ie/travel-information/station-and-route-maps
- **Contents**: Route topology, junction points, station locations
- **Used for**: Knowledge base construction (Connolly junction analysis, single-track sections)

### 7. TII Traffic Data
- **Name**: Transport Infrastructure Ireland Traffic Data
- **URL**: https://trafficdata.tii.ie/
- **Format**: CSV
- **Contents**: Road traffic counts at level crossings
- **License**: Open
- **Used for**: Not used in model; potential secondary indicator

## Synthetic Data

Because the NTA GTFS-RT feed is real-time only (no historical archive), this project generates a **synthetic daily-punctuality dataset** calibrated to published Irish Rail monthly reports. The synthetic data generator is in `data_loaders.py` and produces:

- **1089 days** (2023-01-08 to 2025-12-31, after 7-day lag warm-up)
- **Daily punctuality** calibrated to match published monthly means
- **Weather features** calibrated to Met Eireann Dublin Airport climatology
- **Temporal features**, timetable regime, school term, holidays
- **Lag and rolling features** for autocorrelation capture

The synthetic approach is documented honestly in the paper. All quantitative claims are conditional on the synthetic data faithfully representing the real system dynamics.
