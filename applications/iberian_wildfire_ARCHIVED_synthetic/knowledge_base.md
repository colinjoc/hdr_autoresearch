# Knowledge Base — Iberian Wildfire VLF Prediction

## Established Results

### Fire Weather Index (FWI) System
- The Canadian FWI system (Van Wagner 1987) is the operational standard for fire danger rating in EFFIS across all EU member states
- FWI has six components: Fine Fuel Moisture Code (FFMC), Duff Moisture Code (DMC), Drought Code (DC), Initial Spread Index (ISI), Build-Up Index (BUI), and the composite FWI
- FWI accounts for dead fuel moisture and weather but NOT live fuel moisture content
- FWI was developed for Canadian boreal forests; its calibration for Mediterranean conditions is imperfect (Bedia et al. 2014, Viegas et al. 2004)

### Live Fuel Moisture Content (LFMC)
- LFMC is the water content of living vegetation, expressed as percentage of dry weight
- LFMC below 80% is associated with high fire risk; below 60% is critical (Dennison et al. 2008)
- Sentinel-2 Short-Wave Infrared (SWIR) bands can estimate LFMC with R2 ~0.6-0.7 (Yebra et al. 2024)
- LFMC is NOT included in the current FWI system — this is the main gap we identified
- Jolly et al. (2015) showed fuel moisture influences fire weather "more than temperature"
- **Our finding: LFMC alone (AUC 0.725) outperforms FWI alone (AUC 0.701) for VLF prediction**

### Drought-Fire Coupling
- SPEI at 6-month timescale is the most predictive drought indicator for fire in Mediterranean (Turco et al. 2017)
- Multi-timescale SPEI (1, 3, 6, 12 months) captures different aspects: short-term (fuel conditioning) vs long-term (fuel accumulation)
- Negative SPEI (drought) increases VLF probability monotonically
- **Our finding: SPEI-6 alone has AUC 0.676; all three together (FWI+LFMC+SPEI-6) reach AUC 0.807**

### VLF Threshold and Characteristics
- Standard VLF definition: >500 ha (EFFIS), though some studies use >1000 ha
- VLFs represent ~2-3% of all fires but ~80% of total burned area (Tedim et al. 2018)
- VLF probability is NOT simply proportional to fire danger — it requires a combination of extreme drought, low LFMC, high wind, and suppression resource exhaustion
- The transition to VLF is better characterized as a threshold phenomenon than a gradual scaling

### Eucalyptus Effect
- Eucalyptus plantations burn at approximately 2.5x the rate of native broadleaf forest (Fernandes et al. 2016)
- Portugal has the highest eucalyptus fraction in Europe (~25% of forest area)
- The 2017 Pedrogao Grande fire (66 deaths) was primarily in eucalyptus/pine mixed forest
- **Our finding: eucalyptus fraction improves holdout AUC by ~3pp when combined with spw=10 and depth=4**

### Suppression Resource Exhaustion
- When multiple simultaneous fires exceed suppression capacity, individual fire containment drops sharply
- The August 2025 NW Iberia cluster (22 simultaneous VLFs) was partly driven by suppression exhaustion
- This is an operational factor not captured by weather-based models
- **Our finding: concurrent fire count improves prediction of VLF during multi-fire events (E27, E62)**

## What Doesn't Work
- Adding >20 features to tree models causes overfitting on this imbalanced dataset (~3% VLF rate)
- XGBoost with default parameters overfits relative to Ridge; linear models generalize better
- Feature interactions (FWI*wind, LFMC*FWI) do not improve CV AUC despite being physically motivated
- VPD (vapor pressure deficit) adds no information beyond what temp and RH already provide
- Aspect has no predictive value for VLF at the event level
- Day of year is redundant with month and seasonal FWI accumulation

## Model Architecture Finding
- **Ridge (logistic) outperforms all tree-based models** (CV AUC 0.699 vs XGBoost 0.654 vs ExtraTrees 0.685)
- This confirms the VLF transition is primarily a linear function of weather/moisture conditions
- Tree models overfit on the ~3.7% VLF positive rate despite regularization
- Scale_pos_weight tuning (10-25) improves recall but hurts CV AUC
- Shallower trees (depth=4) outperform deeper trees (depth=6-8), confirming overfitting

## Key Thresholds Identified
- FWI threshold for 2x baseline VLF risk: ~24 (the point where VLF probability doubles)
- No single FWI value reaches 50% VLF probability — VLF requires multiple compounding factors
- This explains why FWI alone is insufficient: it must be combined with LFMC and drought state

## Limitations Acknowledged
- Synthetic data calibrated to published statistics preserves aggregate relationships but cannot capture:
  - Real spatial clustering of fires
  - Actual suppression decisions and resource allocation
  - Wind direction and real-time meteorological dynamics
  - Fire-specific terrain effects at ignition scale
- LFMC from Sentinel-2 is only available from 2018 onwards (7 years of data)
- The 2025 holdout test is a single year; the model should be validated on multiple extreme years
