# Data Sources

## BTS On-Time Reporting Carrier Performance

- **Name**: Airline On-Time Performance Data (BTS/DOT)
- **URL**: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ
- **Bulk download**: https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{YEAR}_{MONTH}.zip
- **Size**: ~27-30 MB compressed per month (~250 MB CSV), ~550k flights/month
- **License**: US Government public domain
- **Local path**: `data/raw/On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_{YEAR}_{MONTH}.csv`
- **Download command**:
  ```bash
  for m in 1 2 3 4 5 6; do
    wget --no-check-certificate -q \
      "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_${m}.zip" \
      -O "data/raw/2024_${m}.zip"
  done
  # Extract with: python3 -c "import zipfile; [zipfile.ZipFile(f'data/raw/2024_{m}.zip').extractall('data/raw') for m in range(1,7)]"
  ```
- **Months downloaded**: 2024-01 through 2024-06
- **Key fields**: FlightDate, Reporting_Airline, Tail_Number, Origin, Dest, CRSDepTime, DepTime, DepDelay, CRSArrTime, ArrTime, ArrDelay, CarrierDelay, WeatherDelay, NASDelay, SecurityDelay, LateAircraftDelay, Cancelled, Diverted
