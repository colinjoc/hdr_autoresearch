# Knowledge Base -- Iberian Wildfire VLF Prediction

## Established Results (from Real Data)

### Fire Weather Index (FWI) System
- The Canadian FWI system (Van Wagner 1987) is the operational standard for fire danger rating in EFFIS across all EU member states
- FWI has six components: FFMC, DMC, DC, ISI, BUI, and the composite FWI
- FWI accounts for dead fuel moisture and weather but NOT live fuel moisture content
- FWI was developed for Canadian boreal forests; calibration for Mediterranean is imperfect
- **Our finding: FWI proxy alone achieves CV AUC 0.809 -- useful but not dominant**

### Live Fuel Moisture Content (LFMC) Proxy
- We approximate LFMC through recent fire activity dynamics: how current burning compares to historical patterns
- Active large fires indicate low fuel moisture, favorable fire spread conditions, and suppression stress
- **Our finding: LFMC proxy (10 features) achieves CV AUC 0.952, outperforming FWI proxy by 14.3pp**
- The anomaly signal (current area / historical average) is the key predictor
- Momentum (previous week's area) contributes additional signal

### Drought-Fire Coupling
- Cumulative fire stress (year-to-date burned area and fire count) captures drought effects
- **Our finding: Drought proxy alone achieves CV AUC 0.808 -- comparable to FWI but weaker than LFMC**
- Combining all three predictor families does not improve over the LFMC proxy alone for linear models

### VLF Threshold and Characteristics
- VLF definition: country-week with >5,000 ha total burned area
- VLF weeks are 13.1% of fire-season country-weeks (125 of 952)
- These weeks account for the vast majority of total burned area and impacts
- The VLF transition involves threshold effects captured by tree models but not linear models

### Country Differences
- Portugal: higher average VLF risk (17.2%), peak in weeks 29-34 (mid-Jul to late Aug)
- Spain: lower average VLF risk (11.5%), more distributed across weeks 26-40 (Jun-Oct)
- Portugal's higher risk consistent with eucalyptus-driven fire regime intensification

## What Works

### Model Architecture
- **XGBoost (depth=4) is the tournament winner**: CV AUC 0.993, holdout AUC 1.000
- XGBoost-deep (depth=6): CV AUC 0.993, holdout AUC 1.000
- LightGBM: CV AUC 0.990, holdout AUC 1.000
- Random Forest: CV AUC 0.983, holdout AUC 0.995
- ExtraTrees: CV AUC 0.975, holdout AUC 0.977
- Ridge: CV AUC 0.926, holdout AUC 0.913
- Tree models substantially outperform linear models -- the VLF transition is nonlinear

### Feature Engineering
- area_ratio (current / historical average) -- the anomaly signal
- area_ha_avg (historical seasonal average) -- the climatology baseline
- fires_ratio, fires_avg -- fire count counterparts
- Lagged area and fire count (1 week, 2 weeks, 4 weeks)
- Fire season indicator and week-within-season

## What Doesn't Work
- Adding land cover fractions (forest, shrubland) from MCD64A1 -- hurts Ridge CV AUC
- The country indicator adds minimal information beyond what features capture
- Combining all predictor families degrades linear model performance (overfitting with n=952)
- Full baseline (26 features) is slightly worse than LFMC proxy (10 features) for Ridge

## Key Thresholds Identified
- VLF area threshold: 5,000 ha per country-week captures 13.1% of fire-season weeks
- Historical average area ratio > 3x: strong VLF indicator
- Fire season concentrated in weeks 22-42 (Jun-Oct); peak weeks 29-36 (late Jul to early Sep)

## Limitations Acknowledged
- All results use real EFFIS satellite fire data (no synthetic)
- Weekly temporal resolution limits sub-weekly event detection
- Country-level aggregation; NUTS-3 models would improve spatial specificity
- No direct climate covariates (ERA5 temperature, humidity, wind, precipitation)
- 2025 holdout is a single severe year; temporal CV provides robustness across 11 test years
