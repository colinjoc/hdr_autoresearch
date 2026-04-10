# Observations -- Iberian Wildfire VLF Prediction

## Data Observations

1. VLF weeks (>5000 ha total burned area) are 13.1% of fire-season country-weeks in the real EFFIS data (125 of 952 observations across 2012-2025)
2. The 2025 fire season has 14 VLF weeks across Portugal and Spain, consistent with the severe 2025 season documented in EFFIS reports
3. EFFIS detects fires >~30 ha from MODIS/VIIRS imagery; weekly data includes fire counts and total burned area per country
4. Portugal has higher average VLF risk (17.2%) than Spain (11.5%), consistent with eucalyptus-driven fire regime intensification
5. All data are real satellite observations from EFFIS/GWIS -- no synthetic data used

## Modeling Observations

1. **Tree models dominate Ridge for VLF prediction.** XGBoost achieves CV AUC 0.993 vs Ridge 0.926. This reverses the synthetic-data finding where Ridge dominated. The real data contains nonlinear threshold effects in VLF transitions that trees capture.

2. **LFMC proxy (recent fire activity dynamics) outperforms FWI proxy (historical fire danger).** LFMC proxy CV AUC 0.952 vs FWI proxy 0.809 -- a 14.3 percentage point gap. This is the headline finding.

3. **Adding features beyond the LFMC proxy hurts the linear model.** Full baseline (26 features) achieves AUC 0.926, below the 10-feature LFMC proxy's 0.952. With 952 observations and 13% positive rate, the linear model overfits on additional features.

4. **The 2025 holdout is perfectly predicted by XGBoost.** AUC 1.000 -- all 14 VLF weeks ranked above all 54 non-VLF weeks. Ridge achieves AUC 0.913 on the same holdout.

5. **Seasonal fire climatology is the top feature.** Historical average burned area for each week captures the baseline seasonal fire danger pattern. The anomaly signal (current vs expected) adds the dynamic component.

6. **Momentum matters.** Previous week's burned area ranks 8th in importance. A week of active large fires predicts the next week will also see large fires -- fuel conditioning persists across weeks.

7. **Land cover features do not help.** Adding MCD64A1 forest/shrubland fractions decreases CV AUC from 0.926 to 0.909. The country indicator already captures the Portugal-Spain land cover difference.

## Gaps and Limitations

1. **Weekly resolution only.** Sub-weekly VLF transitions cannot be captured. A fire that grows from manageable to catastrophic in hours is only seen at the weekly level.

2. **Country-level spatial aggregation.** Subnational (NUTS-3) models would improve spatial specificity but face data sparsity.

3. **No direct climate covariates.** Adding ERA5 gridded reanalysis data could improve the FWI proxy, potentially narrowing the gap with the LFMC proxy.

4. **2025 holdout is a single (severe) year.** The temporal CV across 11 test years provides more robust estimates.

5. **Suppression decisions are unobservable.** Fire suppression priority and resource allocation influence whether a fire becomes VLF but are not in any satellite dataset.
