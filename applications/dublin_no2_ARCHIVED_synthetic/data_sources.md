# Data Sources — Dublin/Cork NO2 Source Attribution

## Primary Dataset

| Name | EPA AirQuality.ie Monitoring Data |
|------|-----------------------------------|
| URL | https://airquality.ie/ |
| API | https://airquality.ie/api/ |
| Size | ~50MB (hourly NO2 for 7 stations, 2019-2025) |
| License | Open Government Licence (Ireland) |
| Local path | `data/dublin_no2_hourly.parquet` |
| Download | Manual download from https://airquality.ie/tab/current-stations or via API |
| Notes | Currently using synthetic data calibrated to published EPA statistics. Real data requires station-by-station CSV download or API queries. |

## Weather Data

| Name | Met Eireann Observations |
|------|--------------------------|
| URL | https://www.met.ie/climate/available-data/historical-data |
| Size | ~20MB (hourly Dublin Airport, 2019-2025) |
| License | Open data |
| Local path | `data/met_eireann_dublin_airport.csv` |
| Download | `wget https://cli.fusio.net/cli/climate_data/webdata/dly3723.csv` |

## Traffic Data

| Name | Dublin City Council Traffic Counts |
|------|-----------------------------------|
| URL | https://www.dublincity.ie/residential/transportation/traffic-management |
| Size | ~10MB |
| License | Open data |
| Local path | `data/dcc_traffic_counts.csv` |

| Name | TII Traffic Data |
|------|-----------------|
| URL | https://trafficdata.tii.ie/ |
| Size | ~5MB |
| License | Open data |
| Local path | `data/tii_traffic.csv` |

## Shipping Data

| Name | Dublin Port AIS Data |
|------|---------------------|
| URL | https://www.marinetraffic.com/ (commercial) or Dublin Port Company |
| Size | ~5MB |
| License | Commercial / request |
| Local path | `data/dublin_port_ais.csv` |

## Fleet Data

| Name | CSO Transport Statistics |
|------|--------------------------|
| URL | https://data.cso.ie/ |
| Size | ~1MB |
| License | Open data |
| Local path | `data/cso_vehicle_fleet.csv` |

## Satellite Data

| Name | Sentinel-5P TROPOMI NO2 |
|------|------------------------|
| URL | https://s5phub.copernicus.eu/ |
| Size | ~500MB per orbit |
| License | Copernicus Open Access |
| Notes | Column density, not surface concentration. Requires AMF correction. |

## Emissions Inventory

| Name | EPA Ireland Emissions Inventory |
|------|-------------------------------|
| URL | https://www.epa.ie/our-services/monitoring--assessment/assessment/irelands-environment/air/ |
| License | Open data |
