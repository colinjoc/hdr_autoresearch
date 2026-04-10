# Feature Candidates — Dublin/Cork NO2 Source Attribution

## Domain Quantities -> Computable Proxies

| Domain Quantity | Computable Proxy | Data Source | Status |
|----------------|------------------|-------------|--------|
| Traffic volume | Weekday/weekend differential | EEA station data | USED |
| Traffic volume | COVID lockdown period flag | Calendar | USED |
| Heating demand | Temperature (inverse) | Met Eireann | USED |
| Heating demand | Month (seasonal proxy) | Calendar | USED |
| Heating demand | Heating degree days (HDD) | Derivable from temp | TESTED |
| Atmospheric dispersion | Wind speed | Met Eireann | AVAILABLE |
| Source direction | Wind direction sectors | Met Eireann | TESTED |
| Mixing height | Temperature inversion proxy (Tmin-Tmax) | Met Eireann | AVAILABLE |
| Traffic type (diesel fraction) | PM2.5/NO2 ratio | EEA station data | OPEN |
| Solid fuel heating | SO2 co-measurement | EEA station data | AVAILABLE |
| Port emissions | Wind from port direction | Met Eireann | TESTED |
| Rush hour traffic | Morning/evening hourly peaks | EEA hourly (4GB) | OPEN |
| Fleet composition | Vehicle registration year | SIMI data | EXTERNAL |
| Smoky coal ban effect | Station in ban area flag | EPA policy | AVAILABLE |
| School term | School calendar proxy | Calendar | AVAILABLE |
| Rainfall washout | Precipitation sum | Met Eireann | AVAILABLE |
| Fog/inversion | Visibility | Met Eireann | AVAILABLE |
