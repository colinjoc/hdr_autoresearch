# Feature Candidates — Iberian Wildfire VLF Prediction

## Domain quantities mapped to computable features

### Fire Weather (from ERA5 reanalysis)
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| FWI | Composite fire danger index | Van Wagner equations from T, RH, wind, precip | **KEPT** (base) |
| FFMC | Dead fine fuel surface moisture | Van Wagner equation, 16-hour lag | **KEPT** (base) |
| DMC | Duff layer moisture | Van Wagner equation, multi-day lag | **KEPT** (base) |
| DC | Deep organic layer drought | Van Wagner equation, seasonal lag | **KEPT** (base) |
| ISI | Fire spread rate potential | FFMC * wind function | **KEPT** (base) |
| BUI | Fuel available for combustion | DMC + DC function | **KEPT** (base) |
| Temperature | Direct fuel drying, convective heating | ERA5 2m temperature at noon | **KEPT** (base) |
| Relative humidity | Fuel moisture equilibrium | ERA5 at noon | **KEPT** (base) |
| Wind speed | Fire spread rate, oxygen supply | ERA5 10m wind at noon | **KEPT** (base) |
| Precipitation | Fuel wetting | ERA5 24h accumulated | **KEPT** (base) |

### Vegetation Moisture (from Sentinel-2)
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| LFMC | Live fuel moisture content | Sentinel-2 SWIR band ratio | **KEPT** (extra) |
| NDVI | Pre-fire greenness/biomass | Sentinel-2 NIR/Red | **KEPT** (base) |

### Drought (from SPEIbase)
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| SPEI-1 | 1-month drought severity | Precipitation-evapotranspiration | **KEPT** (extra) |
| SPEI-3 | 3-month drought severity | Captures seasonal drought | **KEPT** (extra) |
| SPEI-6 | 6-month drought severity | Captures fire-season preparation | **KEPT** (base) |
| SPEI-12 | 12-month drought severity | Captures annual water balance | **KEPT** (extra) |

### Terrain (from EU-DEM)
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| Elevation | Temperature lapse, moisture | EU-DEM at fire location | **KEPT** (base) |
| Slope | Fire uphill spread acceleration | EU-DEM derived | **KEPT** (base) |
| Aspect | Solar exposure, fuel drying | EU-DEM derived | REVERTED (no signal E13) |

### Land Cover (from CORINE)
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| Land cover type | Fuel type, fire spread rate | CORINE classification | Available but not in final model |
| Eucalyptus fraction | Fast-burning fuel proportion | CORINE + national data | Tested (E05), helps with tuned model |

### Temporal / Operational
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| Month | Seasonal fire risk pattern | Calendar month | **KEPT** (base) |
| Latitude | Geographic fire regime gradient | From fire coordinates | **KEPT** (base) |
| Detection hour | Afternoon fires spread faster | Hour of first detection | REVERTED (no CV gain E07) |
| Day of year | Sub-monthly seasonal pattern | Day number 1-365 | REVERTED (redundant E15) |
| Concurrent fires | Suppression capacity exhaustion | Count of active fires in region | Tested (E06, E62), helps with tuned model |

### Engineered Features (tested in HDR loop)
| Feature | Physics | Proxy | Status |
|---------|---------|-------|--------|
| FWI * wind | Wind amplification of fire danger | Product interaction | REVERTED (no CV gain E17) |
| LFMC * FWI | Fuel moisture modulation of danger | Product interaction | REVERTED (E18) |
| temp * wind | Hot wind fire risk | Product interaction | Marginal (E19) |
| VPD | Vapor pressure deficit | T-based saturation pressure | REVERTED (redundant with T+RH, E69) |
| log(FWI) | Nonlinear fire danger response | Log transform | REVERTED (E20) |
| wind^2 | Nonlinear wind effect | Quadratic | REVERTED (E21) |
| SPEI6 * LFMC | Drought-moisture interaction | Product | REVERTED (E22) |
| High wind binary | Wind threshold effect | wind > 30 km/h | REVERTED (E23) |
| Low LFMC binary | Critical dryness threshold | LFMC < 80% | Marginal (E24) |
| Severe drought | Drought threshold | SPEI-6 < -1 | REVERTED (E25) |
| LFMC anomaly | Deviation from seasonal mean | Monthly residual | REVERTED (E66) |
| Temp anomaly | Deviation from monthly mean | Monthly residual | REVERTED (E67) |
| FWI percentile | Within-month ranking | Monthly rank | REVERTED (E68) |
| KB proxy | Keetch-Byram drought approximation | DC * temp function | REVERTED (E70) |
| Heatwave days | Consecutive hot days | Days > 35C count | REVERTED (E08) |
| Night temperature | Overnight drying | Previous night minimum | REVERTED (E09) |
| Prev year precip | Fuel load accumulation | Annual precipitation | REVERTED (E10) |
| WUI distance | Urban proximity fire escalation | Distance to nearest urban | REVERTED (E11) |
| Soil moisture | Root zone moisture availability | ERA5-Land soil moisture | REVERTED (E12) |
| Country indicator | Country-specific fire regime | Binary Portugal/Spain | REVERTED (E14) |
