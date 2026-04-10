# Data Sources — Flight Delay Propagation Through US Airline Networks

## Primary Sources

### 1. BTS On-Time Performance (Reporting Carrier On-Time Performance)
- **Name**: Bureau of Transportation Statistics Airline On-Time Performance Data
- **URL**: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoession_VQ=FGJ&QO_fu146_anzr=b0-gvzr
- **Alternative URL**: https://www.transtats.bts.gov/ONTIME/
- **Format**: Monthly CSV files (~60-80 MB each compressed, ~500 MB uncompressed)
- **Contents**: Every US domestic flight with: scheduled/actual departure and arrival times, carrier (marketing and operating), origin/destination airports, aircraft tail number, delay cause codes (carrier, weather, NAS, security, late aircraft), elapsed time, distance, cancellation/diversion flags
- **Size**: ~7 million flights/year; 2023-2024 = ~14M flights; sampled to 500k for baseline
- **License**: Public domain (US government data)
- **Local path**: `data/bts_ontime_YYYYMM.csv` (monthly files)
- **Download method**: Manual download from transtats.bts.gov (select fields, date range, download). Alternatively, bulk download via BTS download page. No API key required.
- **Key fields used**:
  - `FL_DATE` — flight date
  - `OP_UNIQUE_CARRIER` — operating carrier code
  - `TAIL_NUM` — aircraft tail number (for rotation chain reconstruction)
  - `ORIGIN`, `DEST` — airport codes
  - `CRS_DEP_TIME`, `DEP_TIME` — scheduled and actual departure times
  - `CRS_ARR_TIME`, `ARR_TIME` — scheduled and actual arrival times
  - `DEP_DELAY`, `ARR_DELAY` — departure and arrival delay in minutes
  - `CARRIER_DELAY`, `WEATHER_DELAY`, `NAS_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY` — delay cause decomposition (only populated when delay >= 15 min)
  - `CRS_ELAPSED_TIME`, `ACTUAL_ELAPSED_TIME` — scheduled and actual flight time
  - `DISTANCE` — route distance in miles
  - `CANCELLED`, `DIVERTED` — binary flags
- **Known limitations**: Delay cause codes are self-reported by airlines and known to be noisy. Airlines may systematically misattribute delay causes to minimize blame (e.g., reporting "NAS" when the cause is operational). Tail numbers are sometimes masked for regional carriers.

### 2. NOAA Integrated Surface Database (ISD)
- **Name**: NOAA ISD / METAR observations
- **URL**: https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database
- **Format**: CSV/fixed-width
- **Contents**: Hourly surface weather observations at airport weather stations
- **Variables**: Wind speed/direction, visibility, ceiling height, temperature, precipitation, present weather codes
- **Size**: ~1 GB/year for all US airport stations
- **License**: Public domain (US government data)
- **Local path**: `data/noaa_isd/` (not used in baseline; potential Phase 2 enhancement)
- **Note**: Not used in the synthetic baseline. BTS delay cause codes provide a weather proxy. Full METAR integration is a Phase 2 hypothesis.

## Secondary Sources

### 3. FAA ASPM (Aviation System Performance Metrics)
- **URL**: https://aspm.faa.gov/
- **Format**: Web portal, downloadable reports
- **Contents**: Airport-level delay metrics, taxi times, throughput rates
- **Access**: Requires FAA account; data is aggregated
- **Used for**: Knowledge base construction; not in model

### 4. BTS T-100 Domestic Market Data
- **URL**: https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFI&QO_anzr=Nv4%20Pn44vr4%20Fgngvfgvpf%20%28Sbez%2041%20Genssvp%29-%20%20N77%20Pn44vr4f&QO_fu146_anzr=N
- **Format**: CSV
- **Contents**: Carrier-level traffic statistics (passengers, freight, mail) by route
- **Used for**: Hub identification, carrier-specific scheduling analysis

### 5. OpenSky Network
- **URL**: https://opensky-network.org/
- **Format**: API / bulk download (academic access)
- **Contents**: Global ADS-B flight tracking data
- **Used for**: Reference; not used in model (BTS data is more complete for US domestic)

## Synthetic Data

Because the full BTS dataset is ~14 million flights for 2023-2024 and requires manual download from the BTS website, this project generates a **synthetic flight dataset** calibrated to published BTS statistics. The synthetic data generator is in `data_loaders.py` and produces:

- **500,000 flights** sampled from a realistic US domestic network
- **Tail number rotation chains** reconstructed to simulate aircraft moving through the network
- **Delay distributions** calibrated to published BTS delay statistics (mean arrival delay ~7-8 min, ~20% of flights delayed >15 min)
- **Delay cause code decomposition** matching published BTS proportions (carrier ~30%, late aircraft ~35%, NAS ~25%, weather ~5%, security ~5%)
- **Airport congestion patterns** reflecting real hub/spoke structure
- **Temporal patterns** (time of day, day of week, seasonal) matching published statistics

The synthetic approach enables reproducible research without requiring a BTS account or multi-gigabyte downloads. All quantitative claims are conditional on the synthetic data faithfully representing the real BTS data dynamics.
