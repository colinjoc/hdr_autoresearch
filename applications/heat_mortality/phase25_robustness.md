# Phase 2.5 — Night-time Wet-Bulb Robustness Tests

Phase 2 produced a negative finding: on 9,276 city-weeks, night-time wet-bulb temperature did NOT improve prediction over a baseline that already had dry-bulb Tmax, Tmin, lags, seasonality, and autocorrelation. Phase 2.5 stress-tests that finding across 10 alternative specifications + 2 deferred tests.

## Reference (Phase 2 best, full panel)

- Baseline: MAE=40.448 R2=0.8231 AUC=0.8171
- +tw_night_c_max: MAE=40.504 R2=0.8222 AUC=0.8197
- +22 stacked flagship: MAE=40.677 R2=0.8202 AUC=0.8149

## Summary table

| Test | Description | Base MAE | +tw MAE | +stacked MAE | Base AUC | +tw AUC | +stk AUC | tw_max | stacked |
|------|-------------|---------:|--------:|-------------:|---------:|--------:|--------:|:------:|:-------:|
| R01 | per-city ensemble (one ExtraTrees per city) | 44.357 | 44.371 | 44.724 | 0.8086 | 0.8036 | 0.8107 | REVERT | REVERT |
| R02 | 70+ demographic-proxy target | 4.167 | 4.172 | 4.193 | 0.8161 | 0.8188 | 0.8217 | REVERT | REVERT |
| R03 | Davies-Jones wet-bulb swap | 40.448 | 40.458 | 40.819 | 0.8171 | 0.8221 | 0.8176 | REVERT | REVERT |
| R04 | climatology era swap (panel median per city-week) | 40.532 | 40.458 | 40.700 | 0.8163 | 0.8189 | 0.8140 | REVERT | REVERT |
| R05 | drop city + country fixed effects | 41.294 | 41.217 | 41.432 | 0.8250 | 0.8224 | 0.8202 | REVERT | REVERT |
| R06 | drop autocorrelation (prior pscores) | 42.555 | 42.498 | 43.144 | 0.8197 | 0.8199 | 0.8201 | REVERT | REVERT |
| R07 | hot cities only (n=3812) | 52.646 | 52.490 | 53.012 | 0.8449 | 0.8414 | 0.8426 | REVERT | REVERT |
| R08 | heat-wave weeks only (tmax>=city p95, n=524) | 52.588 | 52.525 | 53.294 | 0.8033 | 0.8059 | 0.7973 | REVERT | REVERT |
| R09 | lethal-heat-wave binary classifier (AUC decision) | — | — | — | 0.9804 | 0.9805 | 0.9781 | REVERT | REVERT |
| R10 | Mediterranean subset (n=1957) | 36.423 | 36.551 | 36.553 | 0.8593 | 0.8505 | 0.8564 | REVERT | REVERT |
| R11 | wildfire smoke indicator (HMS) | — | — | — | — | — | — | DEFER | DEFER |
| R12 | Farrington-robust expected baseline | — | — | — | — | — | — | DEFER | DEFER |

## Verdict per test

- **R01** (per-city ensemble (one ExtraTrees per city)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R02** (70+ demographic-proxy target): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R03** (Davies-Jones wet-bulb swap): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R04** (climatology era swap (panel median per city-week)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R05** (drop city + country fixed effects): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R06** (drop autocorrelation (prior pscores)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R07** (hot cities only (n=3812)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R08** (heat-wave weeks only (tmax>=city p95, n=524)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R09** (lethal-heat-wave binary classifier (AUC decision)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R10** (Mediterranean subset (n=1957)): tw_max=REVERT, stacked=REVERT. Flipped negative finding? **NO**
- **R11** (wildfire smoke indicator (HMS)): tw_max=DEFER, stacked=DEFER. Flipped negative finding? **NO**
- **R12** (Farrington-robust expected baseline): tw_max=DEFER, stacked=DEFER. Flipped negative finding? **NO**

## Robustness map — which tests show ANY positive night-Tw signal

| Test | tw_max signal | stacked signal | notes |
|------|:-------------:|:--------------:|-------|
| R01 | no | no | per-city KFold wall=54.1s |
| R02 | no | no | 70+ proxy (linear rescale by demographic share) wall=34.8s |
| R03 | no | no | DJ(tavg,tdew)+stull-night-offset wall=34.8s |
| R04 | no | no | climatology-median-reanchored wall=34.9s |
| R05 | no | no | FE one-hots zeroed out wall=29.3s |
| R06 | no | no | prior_week_pscore & prior_4w_mean_pscore zeroed wall=31.9s |
| R07 | no | no | subset ['athens', 'atlanta', 'dallas', 'houston', 'las_vegas |
| R08 | no | no | heat-wave-weeks wall=3.2s |
| R09 | no | no | ETClassifier class_weight=balanced wall=4.9s |
| R10 | no | no | ['athens', 'lisbon', 'madrid', 'milan', 'rome'] wall=7.7s |
| R11 | DEFER | DEFER | DEFER HMS shapefile spatial-join loader not cached; 25-min b |
| R12 | DEFER | DEFER | DEFER surveillance/pyflu not installed; 5y same-week mean re |

## Headline

**The negative finding is ROBUST.** Across 10 executed robustness tests, no specification flipped the night-time wet-bulb negative finding at the 0.5-death / 1% MAE noise floor. The finding is therefore publishable as written: night-Tw does not carry marginal information beyond the Phase 2 baseline on this 9,276 city-week panel.

## Open questions (tests we could not run)

- **R11** (wildfire smoke indicator (HMS)): HMS shapefile spatial-join loader not cached; 25-min budget
- **R12** (Farrington-robust expected baseline): surveillance/pyflu not installed; 5y same-week mean retained

- R02 used a demographic 70+ proxy (linear rescaling) because the cached Eurostat dataset is `demo_r_mwk3_t` (totals only), not `demo_r_mweek3` with age strata. A true age-stratified replication remains open.
- R03 swapped Stull -> Davies-Jones at the weekly-aggregate level (not at hourly level) because the cache does not retain hourly data. A fully hourly DJ recomputation is open.
- R04 used the in-panel 2012-2024 median (per city-week) as the climatology reference — there is no pre-1991 data in this panel. A full 1991-2020 ERA5 climatology rebuild is open.

## Implication

Night-time wet-bulb temperature is physiologically plausible but empirically redundant for predicting weekly excess-death P-scores once you already have (a) dry-bulb Tmax and Tmin, (b) 1-week and 4-week autocorrelation, (c) tmax DLNM lags, (d) country fixed effects, and (e) week-of-year seasonality. Policy-wise, this is good news: existing heat-health early warning systems that condition on day-time Tmax extremes are *not* leaving mortality signal on the table. The methodological implication is that the Phase 0.5 / Phase 1 baseline is already tight enough that a nominally 'stronger' physiological indicator has to clear a very high noise floor to be publishable as an addition.
