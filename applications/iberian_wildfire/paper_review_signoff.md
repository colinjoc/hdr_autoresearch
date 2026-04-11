# Review Signoff: Iberian Wildfire VLF Prediction

## Verdict: ACCEPT after Major Revision (revisions complete)

## Changes Made

1. **Title changed**: "Recent Fire Activity Dynamics Outpredict Fire Weather Indices" -> "Lagged Fire Activity Outperforms Seasonal Climatology for VLF Week Classification on the Iberian Peninsula"

2. **Feature family names corrected**: FWI proxy -> Seasonal Climatology, LFMC proxy -> Recent Fire Activity, SPEI proxy -> Cumulative Season Stress. No more borrowed terminology from fire weather/fuel moisture literature.

3. **Six new experiments run**:
   - Fire persistence analysis (47% of VLF weeks are persistence events)
   - Persistence baseline (trivial area_lag1: AUC 0.814)
   - Onset-only evaluation (signal survives: 0.921 vs 0.799)
   - XGBoost predictor comparison (confirms Ridge finding: 0.972 vs 0.751)
   - Threshold sensitivity (robust across 1K-20K ha)
   - Per-year AUC (XGBoost > 0.977 every year)
   - Bootstrap 95% CIs (non-overlapping: [0.934-0.968] vs [0.768-0.848])

4. **Overclaiming eliminated**:
   - "Perfect identification" -> "a single favorable test case"
   - "Outpredicts fire weather" -> "outperforms seasonal climatology"
   - "Implications for fire management: anomaly-based alert triggers" -> "modest suggestion with appropriate caveats"
   - "Significantly outperforming" -> replaced with specific CI values

5. **New sections added**:
   - Section 4.1: Fire Persistence Analysis
   - Section 4.4: Per-Year AUC Analysis
   - Section 4.5: Onset-Only Evaluation
   - Section 4.6: Threshold Sensitivity
   - Section 5.2: What This Study Does Not Show

6. **Literature expanded**: Added Bedia et al. (2018), Turco et al. (2013, 2018), Ruffault et al. (2018), Vitolo et al. (2020), Preisler et al. (2004), Taylor et al. (2013).

7. **Plots regenerated**: 7 figures with honest labels. New plots: threshold sensitivity, persistence analysis. Updated headline plot shows both Ridge and XGBoost.

## Remaining Limitations (Acknowledged)

- No actual fire weather data (FWI not available via simple API; ERA5 requires spatial processing)
- Country-level weekly resolution is too coarse for operational use
- Fire persistence inflates the headline metric by ~3 percentage points
- VLF threshold not based on established operational definition

## Honest Assessment

The core finding is real and defensible: recent fire activity features contain more VLF-predictive information than seasonal fire climatology, even after controlling for fire persistence. But the finding is more modest than originally claimed. It is a study of autoregressive prediction, not a demonstration that fire activity beats fire weather. The paper is now honest about this.

## Quality Checklist

- [x] All CRITICAL issues addressed
- [x] All MAJOR issues addressed
- [x] All MINOR issues addressed or flagged as future work
- [x] No unsupported claims remain
- [x] Confidence intervals provided
- [x] Persistence analysis complete
- [x] Multiple model comparison (Ridge + XGBoost)
- [x] Threshold sensitivity tested
- [x] Per-year breakdown provided
- [x] Tests pass (38/38)
- [x] Plots regenerated with honest labels
- [x] Website summary updated
