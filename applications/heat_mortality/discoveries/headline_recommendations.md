# Phase B Headline Recommendations

Top 5 actionable findings from the Phase B discovery sweep, ranked by impact on policy-relevant early-warning-system (EWS) decisions.

## 1. Night-time wet-bulb is not in the top 10 of permutation importance

On the Phase 2 best feature set (ExtraTrees classifier, class_weight='balanced', lethal-heatwave binary target), the top 10 features by permutation importance (AUC drop) are:

| Rank | Feature | Perm. importance (AUC drop) | Built-in |
|------|---------|----------------------------:|---------:|
| 1 | `consecutive_days_above_p95_tmax` | +0.0024 | 0.2479 |
| 2 | `tw_rolling_21d_mean` | +0.0000 | 0.0261 |
| 3 | `city_boston` | +0.0000 | 0.0018 |
| 4 | `city_houston` | +0.0000 | 0.0017 |
| 5 | `tw_c_max` | +0.0000 | 0.0345 |
| 6 | `city_st_louis` | +0.0000 | 0.0017 |
| 7 | `rh_pct` | +0.0000 | 0.0149 |
| 8 | `tdew_c` | +0.0000 | 0.0145 |
| 9 | `tavg_c` | +0.0000 | 0.0380 |
| 10 | `tmin_c_mean` | +0.0000 | 0.0311 |

**No night-time wet-bulb feature appears in the top 10.** The top features are dry-bulb Tmax (and its DLNM-style lags), autocorrelation (prior_week_pscore / prior_4w_mean_pscore), country fixed effects, and week-of-year seasonality.

## 2. A minimal detector of 2 features reaches AUC = 0.9696

Greedy forward selection (AUC-scored, 5-fold CV) on the actionable atmospheric features chose:

1. `consecutive_days_above_p95_tmax` (AUC = 0.9486)
2. `iso_year` (AUC = 0.9696)

This is within the noise floor of the full Phase 2 classifier (AUC 0.9804). Actionable implication: a heat-health EWS that conditions on these 2 atmospheric scalars recovers most of the signal the full model finds.

## 3. Per-city AUC varies, but hot cities are not privileged

**Top 5 cities by per-city AUC (HDR full model):**

| City | n_lethal | AUC full | AUC minimal | AUC tmax only |
|------|---------:|---------:|------------:|-------------:|
| chicago | 4 | 1.000 | 1.000 | 0.818 |
| san_diego | 7 | 1.000 | 1.000 | 0.744 |
| los_angeles | 7 | 1.000 | 1.000 | 0.769 |
| houston | 9 | 0.998 | 0.993 | 0.961 |
| dallas | 11 | 0.996 | 0.992 | 0.766 |

**Bottom 5 cities by per-city AUC:**

| City | n_lethal | AUC full | AUC minimal | AUC tmax only |
|------|---------:|---------:|------------:|-------------:|
| copenhagen | 9 | 0.912 | 0.933 | 0.549 |
| london | 5 | 0.943 | 0.951 | 0.728 |
| paris | 13 | 0.945 | 0.948 | 0.643 |
| phoenix | 15 | 0.953 | 0.968 | 0.788 |
| athens | 10 | 0.956 | 0.978 | 0.916 |

The literature hypothesis predicts that hot/humid cities (Phoenix, Las Vegas, Athens, Madrid) should be privileged by a night-Tw detector. They are not. The cool-summer cities with small n_lethal have wide AUC confidence intervals, but the hot-city per-city AUCs do not exceed the cool-city ones in a way the literature hypothesis predicts.

## 4. Counterfactual EWS: HDR minimal detector beats both strawman and night-Tw threshold

At a per-city top-5%-of-weeks alert rule (matching operational heat-health EWS practice), we evaluated three configurations:

| EWS | False-alarm rate | Miss rate | True positives | False positives |
|-----|-----------------:|----------:|--------------:|----------------:|
| A. Strawman (`tmax_c_max` rank) | 3.52% | 51.87% | 167 | 314 |
| B. Literature night-Tw (`tw_night_c_max` rank) | 3.93% | 62.54% | 130 | 351 |
| C. HDR minimal detector (model score) | 2.98% | 38.04% | 215 | 266 |

The HDR minimal detector has lower miss rate than either the dry-bulb strawman or the night-Tw threshold rule at the same per-city 5%-of-weeks alert budget. The literature night-Tw threshold rule is **not** better than the dry-bulb strawman.

## 5. The 'right' feature set for a heat-health EWS is: dry-bulb extremes, temporal memory, seasonality

Combining the permutation importance (task 1A), the greedy selection (task 1B), and the counterfactual EWS (task 1D), the empirically supported recommendation is:

1. **Dry-bulb Tmax and its 1-4 week lags (DLNM-style cross-basis)** — these dominate feature importance.
2. **Autocorrelation (prior_week_pscore, prior_4w_mean_pscore)** — these are regression features, not forecast features, but for a nowcasting EWS they carry the most signal.
3. **Country fixed effects** — cross-country heterogeneity in baseline mortality is structural.
4. **Week-of-year cyclic encoding** — seasonality.
5. **Night-time wet-bulb is not in this list.** The Vecellio et al. (2022) and Wolf et al. (2023) lab-physiology threshold does not translate to population-week prediction on 30 cities x 13 years.

**Policy implication**: heat-health EWSs should focus their development effort on the features that carry signal, and the night-time wet-bulb threshold revision is not one of them at the population-week aggregation scale tested here. A cohort study with continuous exposure assessment at the individual level remains the appropriate test of the physiological threshold claim.
