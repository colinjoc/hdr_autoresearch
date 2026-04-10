# Observations — Xylella Olive Decline Prediction

## Phase 0.5 Baseline
- Baseline XGBoost on 8 raw features achieves CV AUC 0.767 under spatial CV grouped by province. This is an honest estimate; random CV would likely inflate to ~0.85-0.90.
- High variance across folds (std 0.14): the model struggles with Valencia (AUC 0.51) but excels on Brindisi (AUC 0.92).
- The Valencia fold is hard because it has no nearby affected Italian provinces in training; the Spanish context is different.

## Phase 1 Tournament
- XGBoost (0.767), LightGBM (0.769), ExtraTrees (0.752), Ridge (0.714).
- LightGBM slightly edges XGBoost in mean AUC but with higher fold variance (F1 std 0.33 vs 0.24).
- ExtraTrees has extreme F1 variance (0 on some folds) — overfitting.
- Ridge (linear) is competitive (0.714) suggesting the relationship is substantially linear in the baseline feature space.
- XGBoost selected for HDR loop due to stability.

## Phase 2 HDR Loop Key Findings
1. **ndvi_trend is the single most impactful feature** (E10: +0.053 AUC, from 0.785 to 0.838). This confirms the literature: temporal NDVI derivative provides the strongest early-warning signal.
2. **Diffusion features (E01, E04) provide modest but consistent gains** (+0.013 AUC for dist_nearest_declining_km; +0.004 for already_affected).
3. **Individual frost threshold features do not help** (E05 frost_days_below_minus6 reverted; E06 frost_days_below_minus12 reverted) but the **composite frost_severity_index does** (E09: +0.001 AUC). This suggests nonlinear frost effects matter but the signal is weak.
4. **Most climate features are redundant** with jan_tmin_mean already in the baseline: winter_tmin_abs, coldest_month_anomaly all reverted.
5. **NDVI variability features all keep** (ndvi_anomaly +0.001, ndvi_std +0.006) — canopy heterogeneity carries information.
6. **EVI does not add value** beyond NDVI (E13 reverted) — consistent with literature that NDVI is more sensitive to early-stage decline.
7. **summer_precip_mm keeps** (E15: +0.003) — drought stress matters for tree susceptibility.
8. **ndvi_x_jan_tmin interaction keeps** (E17: +0.002) — vegetation-frost coupling captures something the main effects miss.

## Phase 2.5 Mechanism Comparison
- **Frost-kill model (climate only): CV AUC 0.458** — below random. Climate features alone cannot predict the decline front under spatial CV. The climate gradients in the study area are confounded with latitude, and the spatial CV removes this.
- **Diffusion model (spatial only): CV AUC 0.571** — marginally above random but much better than climate-only. Distance to affected areas carries real signal even under spatial CV.
- **Combined (climate + spatial): CV AUC 0.488** — paradoxically worse than diffusion-only, suggesting overfitting with too many climate features on small spatial folds.
- **Conclusion: the decline front is primarily diffusion-driven**, not climate-limited, at the current stage of the epidemic. This supports hypothesis (c). The frost-limitation hypotheses (a, b) may become relevant when the front reaches colder northern regions.

## Phase B Discovery
- **Feature importance**: ndvi_trend dominates (24.8% of gain), followed by latitude (10.8%), already_affected (8.6%), dist_nearest_declining (8.1%), ndvi_mean (7.8%).
- **5-year predictions**: Foggia province shows highest risk (0.94 mean risk in 2025), consistent with it being the current frontier.
- **Currently unaffected high-risk areas**: Castellon and Valencia provinces in Spain show elevated risk (0.27-0.30 mean), with several individual municipalities above 0.5 risk.
- **Caveat**: predictions for Spanish provinces rely on transfer from Italian training data. The model may not transfer well across countries.

## Limitations
1. Ground truth is from administrative detection timeline, not individual tree measurements — 1-3 year lag.
2. Synthetic data calibrated to published statistics; not validated on real Sentinel-2 + E-OBS data.
3. The spatial CV with only 9 provinces produces high variance (5 folds over 9 provinces).
4. Spanish provinces are underrepresented and may have different dynamics.
5. No soil type or land management features included.
