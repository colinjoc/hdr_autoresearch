# Cross-city counterfactual: if every city published per-stage timestamps

**This is a projection, not a measurement.** It relies on the assumption that the Seattle within-subset lift from adding per-stage features is representative of the lift other cities would show if they promoted their schemas.

## Inputs

| Quantity | Value (days) | Source |
|---|---:|---|
| Cross-city Mean Absolute Error (MAE), 5 cities, Phase 2 baseline E00 | 89.40 | `results.tsv` row `E00` |
| Seattle-only MAE, generic features, no stage data (C013 ablation) | 99.86 | `results.tsv` row `C013` |
| Seattle-only MAE, two-bucket stage features (C012 winner) | 24.68 | `results.tsv` row `C012` |

## Calculation

```
ratio           = 24.68 / 99.86  = 0.2471
projected_mae   = 89.40 × 0.2471                = 22.09 days
lift_over_base  = 89.40 − 22.09 = 67.31 days
```

## Result

If all 5 cities published per-stage plan-review timestamps of the same quality as Seattle's `tqk8-y2z5` feed, the cross-city MAE would drop from **89.40 days** to approximately **22.09 days** — a **67.31-day absolute reduction**, **75.3%** relative.

## Caveats

1. The ratio is Seattle-specific. SF / LA / Chicago / Austin pipelines may have different splits between stage time and other sources of variance.
2. The non-stage variance floor in Seattle (MAE 99.9 days) is slightly higher than the cross-city baseline (89.4 days), which implies Seattle's generic-feature problem is *harder* than the cross-city average. Applying the Seattle ratio to the cross-city baseline may therefore *over*state the achievable lift.
3. The lift assumes the per-city Phase 2.5 result (NYC BIS: MAE 4.0 at R² log 0.999) is also achievable on small-residential subsets of every city. NYC BIS stage data covers the whole filing → paid → approved → permitted pipeline; other cities' schemas may be thinner.
4. The projection is a *ceiling*, not a forecast. Actually achieving it would require each city to expose per-stage timestamps and each modeller to build per-city stage features.

**Bottom line**: publishing stage timestamps is the single highest-leverage data-quality intervention for this problem. Model improvements cannot substitute for it.
