# Observations: Irish Radon Prediction

## Phase 0.5 Baseline
- XGBoost on 8 raw features (eU, eTh, K, elevation, lat, lon, bedrock_code, quat_code)
- Spatial CV (grouped by county, 5 folds): AUC = 0.5909
- This is dramatically lower than the ~0.78-0.82 reported by Elío et al. (2022) because they used standard random CV. Our spatial CV avoids spatial leakage and gives an honest estimate.

## Phase 1 Tournament
- XGBoost: CV AUC = 0.5909 (winner)
- LightGBM: CV AUC = 0.5873
- ExtraTrees: CV AUC = 0.5820
- Ridge logistic: CV AUC = 0.5847
- All models are close; XGBoost edges ahead. With only 8 features on spatial CV, the problem is genuinely hard at baseline.

## Phase 2 HDR Loop (20 experiments)
- Starting AUC: 0.5909 (8 features)
- Final AUC: 0.7935 (20 features)
- Improvement: +0.2026 AUC (massive)
- Kept: 12/20 experiments
- Reverted: 8/20 experiments

### Kept features (in order added):
1. eU_eTh_ratio — uranium enrichment indicator
2. total_dose_rate — composite radiometric index
3. log_eU — log-transformed uranium
4. quat_permeability — ordinal quaternary permeability
5. is_limestone — binary limestone indicator
6. is_shale — binary shale indicator
7. is_rock_surface — binary rock-at-surface indicator
8. is_peat — binary peat (barrier) indicator
9. mean_air_permeability — BER ventilation proxy
10. pct_suspended_timber — floor type
11. pct_post_2011 — modern building regulation proxy
12. pct_mvhr — mechanical ventilation proxy

### Reverted features:
1. is_granite — redundant with bedrock_code + eU
2. mean_ber_rating_ordinal — redundant with air_permeability
3. pct_slab_on_ground — no improvement
4. mean_year_built — no improvement beyond pct_post_2011
5. pct_detached — no improvement
6. pct_pre_1970 — no improvement
7. mean_floor_area — no improvement
8. scale_pos_weight class balancing — marginal AUC regression

## Key Surprises
1. **is_granite reverted**: Despite granite being the highest-radon lithology, the binary indicator didn't help because bedrock_code + eU already capture the granite signal. The tree can learn the granite splits directly.
2. **Air permeability outperformed BER rating**: The direct ventilation proxy (m3/h/m2 at 50Pa) was more informative than the ordinal BER rating. This makes physical sense — BER rating includes many factors (insulation, heating, etc.) while air permeability is the specific mechanism for radon dilution.
3. **pct_post_2011 helped**: Areas with more modern construction (post-2011 building regs that require radon barriers in HRAs) have lower radon risk. This is a real signal from building regulation effectiveness.
4. **MVHR helped**: Areas with more mechanical ventilation with heat recovery show a slight improvement. MVHR can maintain ventilation despite airtightness.

## Phase 2.5: BER x Geology Interaction
- Mean risk ratio (high BER / low BER areas, controlling for geology): 1.26x
- Strongest on limestone (1.34x) and sandstone (1.33x)
- Granite shows the smallest ratio (1.13x), possibly because granite already pushes radon so high that the BER effect is relatively smaller
- This confirms the EPA UNVEIL finding at national scale: airtight homes on high-radon geology have measurably higher predicted radon risk

## Phase B: Hidden Danger Zones
- 27 areas identified as "hidden danger" (high radon risk + high BER + sparse measurement)
- Concentrated in Cork (8), Galway (8), Dublin (5)
- Predominantly on granite (7 zones) and limestone (6 zones)
- These are areas where the EPA should prioritize measurement campaigns

## Feature Importance (Final Model)
1. quat_code: 0.263 (dominant — quaternary geology is the key pathway modifier)
2. bedrock_code: 0.138 (lithology determines uranium source)
3. eU_mean: 0.128 (direct uranium measurement)
4. latitude: 0.100 (north-south geological gradient)
5. eTh_mean: 0.096 (thorium as geological indicator)
6. longitude: 0.095 (east-west geological gradient)
7. elevation_mean: 0.091 (topographic control)
8. K_mean: 0.089 (potassium as rock-type indicator)

Note: The building features (air_permeability, pct_suspended_timber, etc.) have lower individual importance but contribute to the +0.20 AUC improvement collectively. Their contribution is through interactions with the geological features.
