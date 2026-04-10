# Research Queue — Heat-Mortality HDR Phase 2/2.5/B hypotheses

Pre-registered list of single-change hypotheses for the HDR discovery loop.
Paper IDs in `[n]` point to `papers.csv` (240 entries, Phase 0).

Ordering: prior-probability descending within each theme block. The flagship
theme (Theme 1 — night-time wet-bulb features) has the most entries per the
project brief.

**Baseline reference** (per `data_acquisition_notes.md` §"Phase 0.5 baseline
recipe"): LightGBM with group-shuffle split by city, target `p_score`, features
`{tmax_c_mean, tmin_c_mean, tavg_c, week_of_year_sin/cos, country, lat, lon}`.

"Previous best" below means "the single best model identified by the HDR
loop so far". Phase 2 hypotheses are single-adds on top of the current best;
Phase 2.5 hypotheses compose two or more confirmed Phase 2 adds; Phase B
hypotheses are optimisation sweeps over a confirmed composition.

Hypothesis IDs are stable. Format: `H001–H116`.

Effect units: MAE in deaths/week, R² on `p_score`, AUC/AUROC on binary
`p_score ≥ 0.10` ("lethal heatwave") target, Brier score on the same.

---

## Theme 1 — Night-time wet-bulb features (flagship, 22 hypotheses)

### H001: add `tw_night_c_max` to baseline
- **Prior**: 0.70
- **Mechanism**: night-time wet-bulb directly quantifies the overnight
  evaporative-cooling sink. A week with `tw_night_c_max ≥ 26` is close to
  the PSU HEAT empirical critical limit for humid conditions [19, 20, 207,
  208] and far below the Sherwood-Huber 35 C ceiling [18]. Elevated night
  wet-bulb prevents overnight core-temperature reset and is mechanistically
  upstream of the compound day-night mortality effect shown in London
  [28], southern Europe [35], China [31], and the 178-city multi-country
  analysis [34]. Lee et al. [32] and Yin et al. [33] show it has super-
  linear effect on mortality in European projection. This is the single
  highest-prior feature of the project.
- **Single change**: add column `tw_night_c_max` to feature matrix.
- **Expected effect**: +0.04–0.07 AUROC on lethal-binary; −3–6% RMSE on
  p_score.
- **Phase**: Phase 2 single-add

### H002: add `tw_night_c_mean` to baseline
- **Prior**: 0.68
- **Mechanism**: weekly-mean night-time wet-bulb averages across the
  week, smoothing the signal compared to H001 max. The mean form is more
  robust when station coverage within the 00–06 local window is sparse
  (some European synoptic stations only report every 3 hours — see
  `data_acquisition_notes.md`). Matches the physiological recovery
  framing [18, 21, 25, 26] and the Royé et al. southern Europe hot-night
  result [35, 169].
- **Single change**: add column `tw_night_c_mean`.
- **Expected effect**: +0.03–0.05 AUROC.
- **Phase**: Phase 2 single-add

### H003: add both `tw_night_c_max` and `tw_night_c_mean`
- **Prior**: 0.66
- **Mechanism**: the weekly max captures the single worst night (tail
  event signal) while the mean captures sustained exposure. Gasparrini-
  Armstrong [3, 4] DLNM theory supports using both peak and mean. The
  compound super-linearity in Lee-Yin [32, 33] depends on both a high
  peak and a sustained elevation, so both levers carry information.
- **Single change**: add both columns simultaneously (two-feature add,
  treated as one atomic change).
- **Expected effect**: +0.05–0.08 AUROC; the two-feature add strictly
  dominates either alone.
- **Phase**: Phase 2 single-add

### H004: add consecutive-night-above-threshold count
- **Prior**: 0.63
- **Mechanism**: Mukherjee-Mishra [29] defined concurrent hot-day +
  hot-night events with 1-, 3-, and 5-day variants; Tang et al. [31]
  quantified the super-linear mortality of multi-day compound events;
  Lee et al. [32] projects a 103.7–135.1 deaths/million/°C warming
  slope under compound assumptions. A count of consecutive nights with
  `tw_night_c_max ≥ 24` within the week captures physiological
  hyperthermia accumulation more directly than a single-day metric.
- **Single change**: add column `consecutive_nights_tw_above_24_count`.
- **Expected effect**: +0.03–0.06 AUROC, particularly on multi-week
  heat waves.
- **Phase**: Phase 2 single-add

### H005: add `tw_day_night_spread_c`
- **Prior**: 0.62
- **Mechanism**: a small day–night wet-bulb spread (low diurnal range)
  is the meteorological fingerprint of a heat dome, where a strong
  mid-tropospheric ridge prevents overnight radiative cooling [15, 42,
  219, 220, 221]. Physiologically it is the direct marker that the body
  cannot recover overnight [18, 21, 25, 28, 34]. Operationally absent
  from NWS HeatRisk [106] and most EuroHEAT-style systems [95].
- **Single change**: add column
  `tw_day_night_spread_c = tw_c_max − tw_night_c_mean`.
- **Expected effect**: +0.02–0.04 AUROC; negative sign (small spread
  → more dangerous).
- **Phase**: Phase 2 single-add

### H006: add tropical-night count (`tmin ≥ 20`)
- **Prior**: 0.60
- **Mechanism**: classical WMO tropical-night definition. Well
  established for European heat-health [93, 101, 169]. The direct
  dry-bulb comparator against which the wet-bulb variant (H007) must
  beat.
- **Single change**: add column `tropical_night_count_week`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H007: add wet-bulb tropical-night count (`tw_night ≥ 22`)
- **Prior**: 0.60
- **Mechanism**: wet-bulb analogue of H006. A Tw ≥ 22 night is a
  meaningful physiological threshold (~65% of the PSU HEAT critical
  limit for older adults [209]). Not in any current operational HHWS
  [101, 106]. The head-to-head between H006 and H007 is a direct test
  of the HDR wet-bulb-vs-dry-bulb hypothesis.
- **Single change**: add column `tropical_night_count_tw22_week`.
- **Expected effect**: +0.03 AUROC, and +0.01 over H006.
- **Phase**: Phase 2 single-add

### H008: add 95th-percentile-anomaly version of `tw_night_c_max`
- **Prior**: 0.58
- **Mechanism**: the raw wet-bulb threshold is climate-dependent (25 C
  is extreme in Dublin but routine in Miami). Sera et al. 2019 [193]
  meta-regression and Gasparrini 2015 [6] MCC analysis show city-
  specific percentile thresholds pool better than absolute thresholds.
  The 95th percentile is the conventional MCC heat-threshold choice
  [6, 116, 117]. Tang et al. [31] and Lee et al. [32] use 15-day
  calendar-day moving windows for percentile extraction.
- **Single change**: add column
  `tw_night_c_max_p95_anomaly = tw_night_c_max − city_p95(tw_night_c_max)`.
- **Expected effect**: +0.04 AUROC over raw `tw_night_c_max`.
- **Phase**: Phase 2 single-add

### H009: add 90th-percentile-anomaly version of `tw_night_c_mean`
- **Prior**: 0.56
- **Mechanism**: 90th-percentile is EuroHEAT's operational choice [95].
  Milder anomaly than H008 but more inclusive — catches longer-tail
  events.
- **Single change**: add column `tw_night_c_mean_p90_anomaly`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H010: add `tw_night_c_max` with a city-specific z-score
- **Prior**: 0.54
- **Mechanism**: z-score normalisation relative to city-climatology
  week-of-year standard deviation is an alternative to percentile
  (robust but less tail-sensitive). This is the Anderson-Bell [10]
  framing for heat-wave definitions.
- **Single change**: add column `tw_night_c_max_zscore_city`.
- **Expected effect**: +0.02 AUROC; tests pooling robustness.
- **Phase**: Phase 2 single-add

### H011: widen night window to 22:00–06:00 local
- **Prior**: 0.52
- **Mechanism**: the default 00:00–06:00 window (per
  `data_acquisition_notes.md`) matches Bouchama-Knochel / Gasparrini-
  Armstrong evidence that the signal is early-morning. Widening to
  22:00–06:00 (8 h) aligns with clinical sleep-period definitions and
  could capture pre-midnight compound exposure that the 6 h window
  excludes [28, 35, 121].
- **Single change**: set night-window filter to `local_hour >= 22 | local_hour < 6`
  in `aggregate_hourly_to_weekly`.
- **Expected effect**: +0.00–0.02 AUROC. This is a loader-level
  sensitivity test and may be noise.
- **Phase**: Phase 2 single-add

### H012: narrow night window to 02:00–06:00 local
- **Prior**: 0.44
- **Mechanism**: the tightest clinical definition of night-time
  minimum is the pre-dawn hour, and Bouchama-Knochel clinical data
  suggest 03:00–06:00 is the optimal window. Narrower window has less
  averaging but higher signal purity.
- **Single change**: set night-window filter to `local_hour >= 2 & local_hour < 6`.
- **Expected effect**: −0.01 to +0.02 AUROC — two-sided; plausible it
  hurts by reducing sample count.
- **Phase**: Phase 2 single-add

### H013: add `tw_night_c_min` (the coolest night-time Tw in the week)
- **Prior**: 0.42
- **Mechanism**: if the week contains even one genuinely cool night,
  the population gets partial recovery and the lethal signal fades
  [4, 10, 28]. The minimum over the week is a "worst-recovery-opportunity"
  indicator. This is the mirror of `tw_night_c_max`.
- **Single change**: add column `tw_night_c_min` (weekly min of hourly
  tw within 00:00–06:00 local).
- **Expected effect**: +0.01–0.03 AUROC (negative sign, cooler → lower
  mortality).
- **Phase**: Phase 2 single-add

### H014: swap Stull wet-bulb for Davies-Jones wet-bulb (night features)
- **Prior**: 0.38
- **Mechanism**: Davies-Jones 2008 [43] is the canonical physical
  wet-bulb calculation with MAE < 0.03 C vs measurements; Stull 2011
  [44] has MAE < 0.3 C but max error up to −1.0 C near the Stull-domain
  edges (RH 95–99%, T > 45 C). The Buzan-Huber review [216] notes the
  discrepancy is largest for the tail conditions we care about most.
  Davies-Jones needs pressure, which requires ERA5 or ISD SLP parsing.
- **Single change**: replace `compute_wet_bulb` with `metpy.calc.wet_bulb_temperature`
  (Davies-Jones internally), recompute `tw_night_c_*`.
- **Expected effect**: −0.01 to +0.02 AUROC; the change is likely small
  because cities with the largest divergence (desert heat waves at
  altitude) are a minority of the panel. Tests whether wet-bulb
  algorithm choice matters for mortality prediction.
- **Phase**: Phase 2 single-add (gated on ERA5 access)

### H015: add night-time UTCI instead of night-time Tw
- **Prior**: 0.54
- **Mechanism**: UTCI is the canonical European bioclimatology metric
  [51, 133, 134], derived from a multi-node Fiala thermoregulation model.
  ERA5-HEAT [55] provides it globally. Pappenberger 2015 [134]
  demonstrated forecast skill. Night-time UTCI has never been tested
  as a mortality predictor at the city-week level — this is new ground.
- **Single change**: add `utci_night_c_max` computed from ERA5-HEAT nights.
- **Expected effect**: +0.03–0.06 AUROC. Comparable to H001 but via a
  different physical model.
- **Phase**: Phase 2 single-add (gated on ERA5-HEAT pull)

### H016: add `tw_night_c_max` *interacted with* `pct_age_65p`
- **Prior**: 0.50
- **Mechanism**: Wolf 2023 [20] and Vecellio 2024 [209] showed that
  critical Tw falls with age. Modelling the night-wet-bulb effect as
  heterogeneous in elderly fraction captures the PSU HEAT "older
  adults have lower critical limits" result. Sera 2019 [193] MCC
  meta-regression shows elderly share as a first-order moderator.
- **Single change**: add `tw_night_c_max_x_age_65p` = product of the
  two columns.
- **Expected effect**: +0.02–0.04 AUROC (captures tail heterogeneity).
- **Phase**: Phase 2 single-add (requires Phase 1 population loader)

### H017: add `tw_night_c_max` interacted with `ac_penetration_pct`
- **Prior**: 0.48
- **Mechanism**: Barreca et al. [76] and Sera et al. [75] show AC as
  the dominant protective factor against hot-day mortality; the
  protective effect must be strongest precisely when night-time Tw is
  high and unventilated indoor recovery is impossible. This is the
  classical "interaction hiding the main effect" case.
- **Single change**: add `tw_night_c_max_x_ac_penetration` = product.
  Sign: negative (high AC + high Tw_night → lower excess).
- **Expected effect**: +0.02–0.04 AUROC, mostly concentrated in the
  US 15-city panel where AC data is available.
- **Phase**: Phase 2 single-add

### H018: 3-day rolling `tw_night_c_max` peak
- **Prior**: 0.46
- **Mechanism**: a 3-day consecutive-hot-night window is where Tang-Lee-
  Yin [31, 32, 33] compound effect becomes super-linear. Pre-extracting
  the 3-day rolling peak of `tw_night_c_max` (within the week) is an
  interpretable alternative to the consecutive-count H004.
- **Single change**: add column `tw_night_c_max_roll3d`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H019: add the Mukherjee-Mishra concurrent hot-day hot-night flag but
  using wet-bulb
- **Prior**: 0.52
- **Mechanism**: Mukherjee-Mishra 2018 [29] defines concurrent events
  with dry-bulb T at 90th percentile. A wet-bulb analogue — day Tw
  ≥ city-p90(day Tw) AND night Tw ≥ city-p90(night Tw) on ≥ 2
  consecutive days — operationalises the HDR hypothesis in the form
  most directly comparable to the Indian [29] and Chinese [31]
  literature.
- **Single change**: add `tw_compound_flag`.
- **Expected effect**: +0.03–0.05 AUROC.
- **Phase**: Phase 2 single-add

### H020: add weekly integral `sum(tw_hourly) over tw_hourly > 26`
  ("degree-hours above threshold")
- **Prior**: 0.48
- **Mechanism**: degree-hour integrals are standard in building-energy
  and climate-change-attribution literature [22, 25, 26, 170]. Cumulative
  exposure above a physiological threshold (PSU HEAT 30.55 C for young
  active [19], ~26 for older sedentary extrapolation [20, 209]) captures
  both duration and intensity in one scalar. Matthews et al. 2023 [25]
  used a related cumulative form globally.
- **Single change**: add column `tw_degree_hours_above_26`.
- **Expected effect**: +0.02–0.04 AUROC.
- **Phase**: Phase 2 single-add

### H021: replace absolute 26 C threshold with the PSU HEAT
  older-sedentary critical value (~24 C)
- **Prior**: 0.42
- **Mechanism**: Wolf 2023 [20] and Vecellio 2024 [209] extrapolated
  critical limits to older sedentary adults — around 24 C Tw for low-
  activity conditions in humid environments. Using this as the
  degree-hour threshold directly embeds the physiology literature in
  the feature.
- **Single change**: recompute H020 with threshold 24.
- **Expected effect**: +0.00–0.02 AUROC (signal shift, not magnitude).
- **Phase**: Phase 2 single-add

### H022: pool 4-week rolling `tw_night_c_max` (heat-priming memory)
- **Prior**: 0.40
- **Mechanism**: the literature on heat-wave clustering [4, 10, 88,
  122, 127] suggests recent prior hot weeks change the pool of
  vulnerable survivors and short-run acclimatisation state. A 4-week
  rolling peak of night-time Tw captures both harvesting depletion and
  short-term heat acclimatisation [127].
- **Single change**: add `tw_night_c_max_roll4w` (rolling peak over
  previous 4 weeks, lagged 1 week to avoid leakage).
- **Expected effect**: +0.01–0.03 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 2 — Wet-bulb computation choice (4 hypotheses)

### H023: swap entire Tw pipeline to Davies-Jones
- **Prior**: 0.40
- **Mechanism**: Davies-Jones [43] is the reference wet-bulb
  calculation; Stull [44] is the sea-level fast approximation we ship.
  Buzan-Huber [216] review and IPCC AR6 chapter 11 [168] note Stull is
  acceptable at low altitude but may drift in extreme humid or hot-dry
  conditions. A whole-pipeline swap tests whether the wet-bulb
  algorithm choice matters for any feature, not just night features.
- **Single change**: replace `compute_wet_bulb` with `metpy.calc.wet_bulb_temperature`
  for all downstream Tw features.
- **Expected effect**: ±0.01 AUROC; this is a scientific-soundness
  check more than an expected improvement.
- **Phase**: Phase 2 single-add (gated on pressure availability)

### H024: elevation-stratified Stull vs Davies-Jones comparison
- **Prior**: 0.36
- **Mechanism**: Stull's MAE against Davies-Jones grows with altitude
  because Stull is pressure-independent by construction. Denver (1600 m)
  and Madrid (650 m) are the altitude-sensitive cities in the panel.
  Running both methods and comparing on Denver + Madrid isolates the
  altitude bias.
- **Single change**: add elevation as a covariate AND swap
  wet-bulb method on elevation > 500 m cities only.
- **Expected effect**: +0.01 AUROC on altitude cities, ±0 elsewhere.
- **Phase**: Phase 2 single-add

### H025: use sWBGT instead of Tw as the humid-heat aggregate
- **Prior**: 0.34
- **Mechanism**: sWBGT = 0.567·T + 0.393·e + 3.94 is the humidity-
  modified-T variant of WBGT used when wind and solar are unknown
  [45, 50]. Kong-Huber [50] criticise it but it remains operationally
  ubiquitous.
- **Single change**: add `swbgt_c_max` weekly.
- **Expected effect**: +0.01 AUROC; sWBGT is a near-linear transform
  of T+RH so it's unlikely to beat Tw directly.
- **Phase**: Phase 2 single-add

### H026: use full Liljegren WBGT instead of Tw
- **Prior**: 0.50
- **Mechanism**: Liljegren 2008 [49] is the ISO 7243 standard WBGT
  calculation (needs wind and solar), RMSE < 1 C vs field measurements.
  Brimicombe 2022 [136] pre-computed it on a global ERA5 grid. Kong-
  Huber [50] showed it is materially more accurate than sWBGT for
  extreme heat. Occupational heat-illness literature [130, 131, 132]
  uses WBGT not Tw. If outdoor-work mortality is a meaningful fraction
  of the signal, WBGT may outperform Tw.
- **Single change**: add `wbgt_full_c_max` and `wbgt_night_c_max` from
  ERA5 or Brimicombe product [136].
- **Expected effect**: +0.02–0.05 AUROC; most gain on hot humid cities
  with outdoor workforce (Houston, Miami, Athens).
- **Phase**: Phase 2 single-add (gated on ERA5 pull)

---

## Theme 3 — Compound day-night exposure (6 hypotheses)

### H027: add `tmax_x_tmin` interaction
- **Prior**: 0.48
- **Mechanism**: classical compound-heat-wave framing from Mukherjee-
  Mishra [29] and Tang [31]. Simple product captures the "both day
  and night hot" state. A tree model finds this automatically but
  making it explicit helps Ridge and interpretability.
- **Single change**: add column `tmax_x_tmin = tmax_c_mean · tmin_c_mean`.
- **Expected effect**: +0.01 AUROC on linear models, ~0 on trees.
- **Phase**: Phase 2 single-add

### H028: 2-day compound flag (Tang et al. threshold)
- **Prior**: 0.56
- **Mechanism**: Tang et al. [31] defines compound events at 2 or more
  consecutive days with Tmax ≥ p90 and Tmin ≥ p90. Direct
  implementation.
- **Single change**: add `tang_compound_2d_flag`.
- **Expected effect**: +0.02–0.04 AUROC.
- **Phase**: Phase 2 single-add

### H029: 3-day compound flag
- **Prior**: 0.52
- **Mechanism**: Yin et al. [33] shows 3-day compound events drive a
  super-linear response.
- **Single change**: add `compound_3d_flag`.
- **Expected effect**: +0.02–0.03 AUROC.
- **Phase**: Phase 2 single-add

### H030: compound *duration* (count of compound days in week)
- **Prior**: 0.54
- **Mechanism**: duration matters beyond the binary trigger [32, 33, 36].
  Wang et al. 2023 [36] shows duration is the quantitative driver of
  excess.
- **Single change**: add `compound_day_count_week`.
- **Expected effect**: +0.03 AUROC.
- **Phase**: Phase 2 single-add

### H031: compound-event ordinal label (none / day-only / night-only /
  compound)
- **Prior**: 0.50
- **Mechanism**: Yin et al. [33] explicitly decomposes heatwaves into
  daytime-only, nighttime-only, and compound, and shows compound has
  the steepest exposure-response curve. Encoding this as a 4-level
  ordinal feature preserves the clinically meaningful typology.
- **Single change**: add `heatwave_type_ordinal` (0,1,2,3).
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H032: compound-event count of compound days *in previous 4 weeks*
- **Prior**: 0.44
- **Mechanism**: compound events are not independent; a prior compound
  event in recent weeks changes the susceptible population [4, 10].
  4-week lookback captures the harvesting interaction.
- **Single change**: add `compound_days_4w_lag`.
- **Expected effect**: +0.01–0.02 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 4 — Heat-wave definition variants (8 hypotheses)

### H033: fixed-threshold heat-wave flag (Tmax ≥ 35 C, 3 days)
- **Prior**: 0.46
- **Mechanism**: simple fixed threshold is the original 1990s NWS rule
  and matches Anderson-Bell [10] US definition. Direct comparator
  against percentile-based definitions.
- **Single change**: add `hw_fixed_35_3d_flag`.
- **Expected effect**: +0.01 AUROC; likely to lose to percentile forms
  on heterogeneous cities.
- **Phase**: Phase 2 single-add

### H034: 95th-percentile heat-wave flag (Tmax ≥ city-p95, 3 days)
- **Prior**: 0.52
- **Mechanism**: Gasparrini 2015 [6] MCC uses city-percentile heat
  thresholds; Anderson-Bell [10] quantified 43-US-city mortality at
  p95. This is the MCC default.
- **Single change**: add `hw_p95_3d_flag`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H035: EuroHEAT flag (Tmax ≥ city-p90 AND Tmin ≥ city-p90, 2 days)
- **Prior**: 0.54
- **Mechanism**: EuroHEAT operational definition [95], validated across
  9 European cities; 7.6–33.6% mortality increase during EuroHEAT
  events. This is the European operational baseline.
- **Single change**: add `euroheat_flag`.
- **Expected effect**: +0.02–0.04 AUROC.
- **Phase**: Phase 2 single-add

### H036: Hobday marine-heatwave-style climatology flag
- **Prior**: 0.36
- **Mechanism**: Hobday et al. definition uses calendar-day climatology
  + percentile + minimum duration. It was developed for marine heat
  waves but is commonly adapted to atmospheric data. Smith-Fox-Frölicher
  adaptations exist in recent literature.
- **Single change**: add `hobday_atm_flag`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H037: NWS HeatRisk level (US-only) as a feature
- **Prior**: 0.58
- **Mechanism**: NWS HeatRisk [106, 107] is the direct operational
  benchmark for US cities. Including it as a feature converts the
  HDR task into "does adding night-time Tw improve on HeatRisk".
  Expected to improve raw MAE but the HDR win is on the *residual*.
- **Single change**: add `nws_heatrisk_level` (US-only).
- **Expected effect**: +0.04–0.08 AUROC on US subset; ~0 on EU subset.
- **Phase**: Phase 2 single-add

### H038: UK HHAS level (UK-only) as a feature
- **Prior**: 0.48
- **Mechanism**: Thompson 2022 [103] showed UK HHAS mortality patterns;
  this is the UK operational comparator.
- **Single change**: add `uk_hhas_level` (UK-only).
- **Expected effect**: +0.03 AUROC on London subset.
- **Phase**: Phase 2 single-add

### H039: ensemble of 3 heat-wave definitions as a vote
- **Prior**: 0.42
- **Mechanism**: operational HHWS practice sometimes combines multiple
  definitions to reduce miss rate [101, 161]. Voting across
  p95-3d + EuroHEAT + HeatRisk captures the union signal.
- **Single change**: add column `hw_majority_vote = (sum ≥ 2)`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H040: Russo 2014 HWMI (Heat Wave Magnitude Index)
- **Prior**: 0.38
- **Mechanism**: HWMI integrates heat-wave duration with daily magnitude
  above the p90 threshold. Used in Russian 2010 [111, 112] and European
  attribution literature [119, 166]. More informative than a binary
  flag.
- **Single change**: add `hwmi_daily` integrated over the week.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 5 — Acclimatisation features (5 hypotheses)

### H041: city-specific MMT (minimum mortality temperature) as a feature
- **Prior**: 0.46
- **Mechanism**: MMT is the T at which the U-shaped mortality curve is
  lowest [6, 124]. It encodes city climate adaptation. Phase 1 can
  estimate it from the baseline training data via a GAM fit, then
  use `T − MMT_city` as a centred exposure.
- **Single change**: add column `tw_c_mean_minus_city_mmt`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H042: MMT percentile (rank of MMT within city climatology)
- **Prior**: 0.38
- **Mechanism**: MMT typically lies at the 75–85th percentile of local
  climatology [6, 124]. Using the percentile rather than the absolute
  value lets the model compare across climates.
- **Single change**: add column `mmt_percentile_city`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H043: climate normal era choice — 1961-1990 for anomaly baseline
- **Prior**: 0.30
- **Mechanism**: CRU / IPCC default. Too cold — pre-adaptation state.
  Included as a lower-bound sensitivity test.
- **Single change**: set `climatology` arg to 1961-1990 reference table.
- **Expected effect**: −0.01 AUROC; tests that the choice of baseline
  era doesn't secretly drive the signal.
- **Phase**: Phase 2 single-add

### H044: climate normal era choice — 1991-2020 for anomaly baseline
- **Prior**: 0.38
- **Mechanism**: NOAA climate normals since 2021. Matches most recent
  human acclimatisation state. Shifts anomalies downward and may
  weaken the signal by construction.
- **Single change**: set `climatology` arg to 1991-2020 reference table.
- **Expected effect**: −0.01 AUROC vs the 1980-2010 default.
- **Phase**: Phase 2 single-add

### H045: adaptation trend — linear `year_index` interaction with Tw
- **Prior**: 0.44
- **Mechanism**: Bobb et al. [11], Gasparrini 2015 EHP [7], Folkerts
  [125] and Yin [126] all document adaptation over time — heat-
  mortality slope declines by ~63% 1987-2005 in the US. Including a
  year-interaction term lets the model learn this trend.
- **Single change**: add `tw_c_mean_x_year_index`.
- **Expected effect**: +0.01–0.03 AUROC; mostly improves out-of-time
  generalisation.
- **Phase**: Phase 2 single-add

---

## Theme 6 — Lag structure (7 hypotheses)

### H046: add same-day + lag-1-day `tmax` rolling max
- **Prior**: 0.60
- **Mechanism**: heat effects on mortality are strongest at lag 0 and
  lag 1 for cardiovascular and respiratory deaths [3, 6, 68, 120, 166].
  Weekly aggregation already implicitly averages this but an explicit
  rolling-max-over-2-days-within-the-week captures the tail day.
- **Single change**: add `tmax_max2d_week`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H047: distributed-lag 0-14 day Tw rolling mean
- **Prior**: 0.54
- **Mechanism**: standard DLNM lag window for heat is 0-14 days or
  0-21 days [3, 4, 6]. Rolling mean captures cumulative exposure.
- **Single change**: add `tw_rolling_14d_mean`.
- **Expected effect**: +0.02–0.03 AUROC.
- **Phase**: Phase 2 single-add

### H048: distributed-lag 0-21 day Tw rolling mean
- **Prior**: 0.50
- **Mechanism**: 0-21 days is the MCC Network convention for heat-cold
  analyses [6, 117]. Longer window catches the harvesting tail.
- **Single change**: add `tw_rolling_21d_mean`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H049: distributed-lag 0-28 day Tw rolling mean
- **Prior**: 0.40
- **Mechanism**: 4-week window is longer than standard DLNM heat and
  probably includes cold-effect contamination. Included as
  sensitivity.
- **Single change**: add `tw_rolling_28d_mean`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H050: DLNM cross-basis features (3 df exposure × 4 df lag) pre-extracted
- **Prior**: 0.58
- **Mechanism**: Gasparrini DLNM [1, 2, 3, 4, 5] is the gold-standard
  framework. Pre-extracting 12 cross-basis columns from daily Tw over
  lag 0-14 days with 3 df exposure × 4 df lag lets a tree model
  approximate the DLNM answer. Boudreault et al. [140, 141, 142]
  recommended exactly this approach.
- **Single change**: add 12 columns `dlnm_cb_tw_k0..k11`.
- **Expected effect**: +0.04–0.07 AUROC.
- **Phase**: Phase 2 single-add

### H051: DLNM cross-basis features over *night-time* Tw
- **Prior**: 0.52
- **Mechanism**: apply H050's cross-basis construction to
  `tw_night_c_max_daily` instead of daily-mean Tw. Combines the
  night-time flagship with DLNM structure.
- **Single change**: add 12 columns `dlnm_cb_twnight_k0..k11`.
- **Expected effect**: +0.03–0.06 AUROC.
- **Phase**: Phase 2 single-add (composable after H050)

### H052: separate heat and cold lag basis for cold-season control
- **Prior**: 0.32
- **Mechanism**: cold has a longer lag than heat [3, 6]. Separating
  the cold basis from the heat basis may avoid contamination in
  winter weeks.
- **Single change**: add separate cold lag cross-basis columns.
- **Expected effect**: +0.00–0.02 AUROC; probably small because the
  HDR focus is summer.
- **Phase**: Phase 2 single-add

---

## Theme 7 — Vulnerability moderators (8 hypotheses)

### H053: add `pct_age_65p` as a feature
- **Prior**: 0.50
- **Mechanism**: age 65+ is the strongest individual risk factor [9,
  37, 90, 163, 209]. Sera 2019 [193] meta-regression confirms it as
  first-order moderator.
- **Single change**: add `pct_age_65p`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H054: add `ac_penetration_pct` as a feature
- **Prior**: 0.54
- **Mechanism**: AC is the dominant protective factor [71, 73, 75, 76,
  210, 212, 213]. Barreca et al. [76] estimated 80% reduction in hot-day
  mortality since 1960 due to AC diffusion.
- **Single change**: add `ac_penetration_pct`.
- **Expected effect**: +0.02–0.04 AUROC on US subset.
- **Phase**: Phase 2 single-add

### H055: add UHI intensity as a city-level feature
- **Prior**: 0.50
- **Mechanism**: Iungman et al. [85, 86] attributed 4–5% of summer
  mortality to UHI across European cities; 38% of 2022 London heat-
  wave deaths [84]. UHI is strongest at night so it directly
  correlates with the compound-night hypothesis.
- **Single change**: add `uhi_intensity_c`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H056: add deprivation index / social vulnerability index
- **Prior**: 0.44
- **Mechanism**: low SES is a heat-mortality risk factor via AC access,
  housing quality, isolation [74, 78, 122, 195, 210]. Sera 2019 [193]
  meta-regression confirms.
- **Single change**: add `deprivation_index`.
- **Expected effect**: +0.01–0.02 AUROC.
- **Phase**: Phase 2 single-add

### H057: add prior-week p-score (autocorrelation)
- **Prior**: 0.62
- **Mechanism**: weekly all-cause mortality has strong week-on-week
  autocorrelation both from ongoing wave dynamics and from harvesting
  [4, 10, 122]. Jones-Fleck [138] and Boudreault [140, 141] showed
  prior-week mortality is a dominant feature for wave detection.
- **Single change**: add `prior_week_pscore` lagged 1 week (with strict
  train/test split to avoid leakage).
- **Expected effect**: +0.04–0.08 AUROC.
- **Phase**: Phase 2 single-add (care with leakage)

### H058: add prior-4-week mean p-score
- **Prior**: 0.50
- **Mechanism**: longer-horizon autocorrelation for wave dynamics.
- **Single change**: add `p_score_4w_rolling_mean` lagged 1 week.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H059: add elderly-share × tw_night_c_max interaction (second-order)
- **Prior**: 0.46
- **Mechanism**: Vecellio 2024 [209] shows the critical Tw for older
  adults is lower. This is Wolf 2023 [20] formalised as a feature.
- **Single change**: add interaction term.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H060: add the difference between country-p90 and city-p90 Tw
  ("climate mismatch")
- **Prior**: 0.34
- **Mechanism**: a city that is colder than its country average will
  be less adapted to the country-scale heat wave. Novel feature —
  tests whether regional mismatch matters.
- **Single change**: add `tw_p90_city_minus_country`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 8 — Air pollution co-stressors (5 hypotheses)

### H061: add weekly PM2.5
- **Prior**: 0.48
- **Mechanism**: PM2.5 amplifies heat mortality via cardiovascular
  stress [110, 113, 114, 237]. Russia 2010 wildfire-heat co-exposure
  [110, 111] is the paradigm.
- **Single change**: add `pm25_ug_m3_weekly_mean`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add (gated on air-quality loader)

### H062: add weekly O3
- **Prior**: 0.40
- **Mechanism**: ozone co-varies with heat via photochemistry; adds
  independent respiratory mortality [113, 237].
- **Single change**: add `o3_ppb_weekly_mean`.
- **Expected effect**: +0.01–0.02 AUROC.
- **Phase**: Phase 2 single-add

### H063: add wildfire smoke flag
- **Prior**: 0.36
- **Mechanism**: wildfire smoke spikes during heat-dome events [110,
  112]; Russian 2010 and Canadian 2023 paradigms. Binary flag captures
  the exceptional events.
- **Single change**: add `wildfire_smoke_flag` from HMS archive.
- **Expected effect**: +0.01 AUROC, concentrated on a handful of
  high-leverage weeks.
- **Phase**: Phase 2 single-add

### H064: add PM2.5 × Tw_night interaction
- **Prior**: 0.38
- **Mechanism**: additive heat-pollution interaction is well documented
  [110, 113, 237]. Interaction term captures multiplicative dose
  response.
- **Single change**: add `pm25_x_tw_night`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add (depends on H061)

### H065: add ozone 8-hour daily max
- **Prior**: 0.32
- **Mechanism**: EPA standard is 8-h daily max ozone. More relevant
  than daily mean for health [113].
- **Single change**: replace `o3_ppb_weekly_mean` with
  `o3_ppb_max8h_weekly`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 9 — Regional dummies vs per-city models (4 hypotheses)

### H066: add country fixed effects
- **Prior**: 0.56
- **Mechanism**: country-level health systems, coding practices, and
  baseline mortality differ substantially [6, 7, 13, 63, 154]. Fixed
  effects absorb the nuisance variation.
- **Single change**: one-hot encode `country` or add it as a category
  to LightGBM.
- **Expected effect**: +0.03–0.05 AUROC (especially in the pooled
  15-EU subset).
- **Phase**: Phase 2 single-add

### H067: add city fixed effects
- **Prior**: 0.62
- **Mechanism**: city is the finer unit and absorbs within-country
  heterogeneity (Phoenix vs Miami are both "US" but behave differently).
- **Single change**: add `city` as a LightGBM categorical.
- **Expected effect**: +0.04–0.07 AUROC. Caveat: with group-shuffle
  split by city, fixed effects do nothing at test time — evaluate on
  temporal split for this one.
- **Phase**: Phase 2 single-add

### H068: train one model per city, ensemble predictions
- **Prior**: 0.42
- **Mechanism**: Boudreault 2023 [141] tested multi-region vs per-region
  models for heat-health. Per-city has advantages on tail events if
  cities are heterogeneous enough.
- **Single change**: fit 30 LightGBM models (one per city), average
  probabilities.
- **Expected effect**: +0.01 AUROC on tail events, −0.02 on average
  (fewer samples per model).
- **Phase**: Phase 2 single-add

### H069: cluster cities by climate zone, one model per cluster
- **Prior**: 0.44
- **Mechanism**: Köppen-Geiger clusters capture climate archetype
  (hot-humid / hot-dry / temperate / continental). One model per
  cluster is a halfway point between pooled and per-city [53, 124].
- **Single change**: cluster 30 cities into 4-5 Köppen groups, fit
  per-cluster.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 10 — Target transforms (5 hypotheses)

### H070: train on log-rate instead of p-score
- **Prior**: 0.44
- **Mechanism**: log-rate is the canonical GLM link for Poisson time-
  series [3, 6, 68]. Less influenced by small-expected-baseline
  outliers than p-score.
- **Single change**: set `y = log((deaths + 0.5) / population)`.
- **Expected effect**: +0.01 AUROC on small cities, ~0 on large.
- **Phase**: Phase 2 single-add (needs population column)

### H071: train on raw excess_deaths instead of p-score
- **Prior**: 0.36
- **Mechanism**: excess deaths is the operationally reported metric;
  trains the model directly on what the HHWS reports to the public
  [60, 154].
- **Single change**: set `y = excess_deaths`.
- **Expected effect**: −0.02 AUROC because cities have wildly different
  sizes; probably worse unless pooled with fixed effects.
- **Phase**: Phase 2 single-add

### H072: train binary classifier on `p_score ≥ 0.10`
- **Prior**: 0.62
- **Mechanism**: binary lethal classification is the HDR evaluation
  target per `data_acquisition_notes.md`. Direct optimisation of a
  binary target usually produces better-calibrated classification
  scores than regression-then-threshold [138, 140, 142, 198].
- **Single change**: train LightGBMClassifier instead of Regressor;
  `y = (p_score ≥ 0.10).astype(int)`.
- **Expected effect**: +0.02 AUROC vs regression-then-threshold.
- **Phase**: Phase 2 single-add

### H073: train binary classifier on `p_score ≥ 0.20`
- **Prior**: 0.50
- **Mechanism**: higher threshold isolates only the most lethal heat
  events, which is the operational alert level. Lower positive count;
  noisier but more decision-relevant.
- **Single change**: `y = (p_score ≥ 0.20).astype(int)`.
- **Expected effect**: +0.01 AUROC on tail weeks, noisier.
- **Phase**: Phase 2 single-add

### H074: train on age-standardised mortality rate
- **Prior**: 0.38
- **Mechanism**: ASMR [63, 66] removes population ageing confound.
  Preferred Lancet Countdown frame [37, 38]. Requires age-stratified
  data (EU only).
- **Single change**: `y = asmr_weekly`.
- **Expected effect**: +0.01 AUROC in EU subset.
- **Phase**: Phase 2 single-add (gated on age-stratified load)

---

## Theme 11 — Survival / time-to-event of mortality wave (3 hypotheses)

### H075: predict lag between heat peak and mortality peak
- **Prior**: 0.36
- **Mechanism**: heat wave mortality is not instantaneous; the lag
  between Tw peak and mortality peak is a physiological and
  demographic signature [3, 6, 120]. Modelling the lag as a target
  directly tests DLNM assumptions.
- **Single change**: create new target `lag_days_tw_peak_to_mortality_peak`
  for each wave event, regress it.
- **Expected effect**: new target, no baseline comparison. Proof-of-
  concept rather than skill improvement.
- **Phase**: Phase 2 single-add (new target family)

### H076: survival analysis of weeks-until-p_score-drops-below-0
- **Prior**: 0.28
- **Mechanism**: wave duration as a time-to-event outcome [120]. Cox or
  Kaplan-Meier style analysis. Less operationally useful but a new
  framing that may reveal dynamics.
- **Single change**: new target `weeks_until_pscore_neg`.
- **Expected effect**: exploratory.
- **Phase**: Phase 2 single-add

### H077: quantile regression at τ=0.95 on p-score (upper tail)
- **Prior**: 0.54
- **Mechanism**: the HDR concern is the tail of the distribution; Koenker
  quantile regression or Quantile LightGBM directly optimises the
  upper tail [140, 142, 198].
- **Single change**: fit LightGBM with `objective='quantile', alpha=0.95`.
- **Expected effect**: +0.03 AUROC on lethal-binary if derived from the
  95%-quantile prediction.
- **Phase**: Phase 2 single-add

---

## Theme 12 — DLNM-style pre-extracted features (2 hypotheses)

### H078: ns(T, 3 df) × ns(lag, 4 df) cross-basis for dry-bulb T
- **Prior**: 0.52
- **Mechanism**: Gasparrini 2010 [1, 3] standard exposure × lag cross-
  basis. Standard MCC Network feature. 3 exposure df captures
  U-shape; 4 lag df captures heat-immediate + cold-prolonged.
- **Single change**: add 12 cross-basis columns from dry-bulb daily T.
- **Expected effect**: +0.03 AUROC.
- **Phase**: Phase 2 single-add

### H079: penalised DLNM basis (Gasparrini 2017 [5])
- **Prior**: 0.44
- **Mechanism**: Gasparrini 2017 [5] introduced penalised-spline DLNM
  that avoids knot-position sensitivity. More robust at small sample
  sizes.
- **Single change**: replace unpenalised ns() with P-splines in the
  cross-basis.
- **Expected effect**: +0.01 AUROC, better stability.
- **Phase**: Phase 2 single-add (depends on H050 / H078)

---

## Theme 13 — Hyperparameter sweeps (6 hypotheses)

### H080: LightGBM max_depth = 8
- **Prior**: 0.42
- **Mechanism**: default depth=6 may under-fit interaction-heavy
  compound-heat signals. Deeper trees can capture higher-order
  interactions.
- **Single change**: `max_depth=8`.
- **Expected effect**: +0.01 AUROC, risk of overfitting on small
  cities.
- **Phase**: Phase B optimisation

### H081: LightGBM learning_rate = 0.02, n_estimators = 2000
- **Prior**: 0.46
- **Mechanism**: smaller steps with more rounds typically improves
  generalisation; standard LightGBM practice.
- **Single change**: `learning_rate=0.02, n_estimators=2000, early_stopping_rounds=50`.
- **Expected effect**: +0.01–0.02 AUROC.
- **Phase**: Phase B optimisation

### H082: LightGBM min_child_samples = 20
- **Prior**: 0.38
- **Mechanism**: default 20 is probably fine but small-city weeks
  may warrant higher to regularise.
- **Single change**: `min_child_samples=20`.
- **Expected effect**: +0.00–0.01 AUROC.
- **Phase**: Phase B optimisation

### H083: LightGBM subsample = 0.8, colsample_bytree = 0.8
- **Prior**: 0.40
- **Mechanism**: stochastic boosting regularisation.
- **Single change**: `bagging_fraction=0.8, feature_fraction=0.8`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase B optimisation

### H084: LightGBM num_leaves = 63
- **Prior**: 0.36
- **Mechanism**: increase tree complexity.
- **Single change**: `num_leaves=63` (default 31).
- **Expected effect**: +0.00–0.01 AUROC; overfits small cities.
- **Phase**: Phase B optimisation

### H085: add monotone constraints on Tw features (monotone-positive)
- **Prior**: 0.40
- **Mechanism**: mortality should be monotonically non-decreasing in
  Tw above the MMT. Monotone constraints in LightGBM enforce this,
  improving tail-event reliability.
- **Single change**: `monotone_constraints=[1, 1, ...]` on Tw columns.
- **Expected effect**: +0.00–0.02 AUROC, better calibration on tail.
- **Phase**: Phase B optimisation

---

## Theme 14 — Model-family pivots (8 hypotheses)

### H086: XGBoost instead of LightGBM
- **Prior**: 0.40
- **Mechanism**: XGBoost is the classical gradient-boosting implementation;
  Boudreault 2023 [140, 141, 142] compared several. Similar to LightGBM
  with slightly different histogram handling.
- **Single change**: swap model class.
- **Expected effect**: ±0.01 AUROC. Tests model-family robustness.
- **Phase**: Phase 2 single-add

### H087: ExtraTrees instead of LightGBM
- **Prior**: 0.28
- **Mechanism**: non-gradient ensemble; high variance, low bias. Useful
  as a calibration anchor.
- **Single change**: swap model class.
- **Expected effect**: −0.02 AUROC typically.
- **Phase**: Phase 2 single-add

### H088: RandomForest instead of LightGBM
- **Prior**: 0.30
- **Mechanism**: canonical ensemble; Boudreault [140] found RF was
  competitive on average but worse on extreme days — exactly the
  HDR concern.
- **Single change**: swap model class.
- **Expected effect**: ±0.02 AUROC on average, −0.05 on tail.
- **Phase**: Phase 2 single-add

### H089: Ridge regression sanity check
- **Prior**: 0.22
- **Mechanism**: linear-model lower bound. Useful to verify the
  non-linear signal is real.
- **Single change**: swap to RidgeCV.
- **Expected effect**: −0.08 AUROC vs LightGBM; if not, something is
  wrong.
- **Phase**: Phase 2 single-add

### H090: Quantile LightGBM at τ=0.9 (upper-tail regression)
- **Prior**: 0.54
- **Mechanism**: quantile loss optimises the tail of the distribution,
  which is the HDR operational concern [198, 140, 142].
- **Single change**: `objective='quantile', alpha=0.9`.
- **Expected effect**: +0.02–0.04 AUROC on lethal-binary derived
  from quantile predictions.
- **Phase**: Phase 2 single-add

### H091: Poisson-objective LightGBM on raw deaths count
- **Prior**: 0.46
- **Mechanism**: Poisson GLM / GBM is the literature-standard for
  count mortality [3, 6, 68]. LightGBM supports Poisson objective
  natively.
- **Single change**: `objective='poisson'` on `deaths_all_cause`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H092: Tweedie LightGBM on excess_deaths
- **Prior**: 0.32
- **Mechanism**: Tweedie distribution handles zero-inflated non-
  negative counts (common in small cities with no-excess weeks).
- **Single change**: `objective='tweedie'`.
- **Expected effect**: +0.01 AUROC in sparse-excess regimes.
- **Phase**: Phase 2 single-add

### H093: stacked ensemble of LightGBM + DLNM residual
- **Prior**: 0.44
- **Mechanism**: DLNM captures structure; GBM captures non-linear
  residuals [140, 142]. Stacking (DLNM prediction as feature for GBM)
  is a classical ensemble that has worked in heat-mortality
  literature [140].
- **Single change**: fit DLNM, add its prediction as a feature to GBM.
- **Expected effect**: +0.02–0.04 AUROC.
- **Phase**: Phase 2.5 composition

---

## Theme 15 — Reanalysis vs station (3 hypotheses)

### H094: ERA5-Land instead of ISD at city centroid
- **Prior**: 0.42
- **Mechanism**: ERA5-Land [56] is 9 km resolution vs ERA5 single-levels
  31 km. Better at urban-rural gradients, though still misses UHI.
  ISD is a single point (often an airport, rural).
- **Single change**: load ERA5-Land T and Td; recompute Tw.
- **Expected effect**: +0.01 AUROC. Tests the airport-vs-grid assumption.
- **Phase**: Phase 2 single-add (gated on CDS account)

### H095: ISD + ERA5-based UHI correction
- **Prior**: 0.46
- **Mechanism**: [84, 85, 86] attribute meaningful mortality share to
  UHI. Correcting ISD airport T with an ERA5 urban-rural offset
  combines station measurements with gridded context.
- **Single change**: `t_corrected = t_isd + (era5_urban - era5_rural)`.
- **Expected effect**: +0.02 AUROC on European dense-city subset.
- **Phase**: Phase 2 single-add

### H096: HadISDH monthly Tw climatology as anomaly reference
- **Prior**: 0.36
- **Mechanism**: HadISDH [57, 58, 59] is the reference humidity
  observational product. Using its Tw climatology as the anomaly
  denominator is methodologically cleaner than raw ISD self-reference.
- **Single change**: set `climatology` to HadISDH 1980-2010 means.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 16 — Drought / dryness moderators (3 hypotheses)

### H097: add SPI-3 (3-month Standardised Precipitation Index)
- **Prior**: 0.38
- **Mechanism**: dry antecedent soil moisture amplifies heat wave
  intensity and persistence [30, 219]. Zscheischler-Seneviratne compound
  literature [30] shows drought-heat combination has super-linear
  human impacts.
- **Single change**: add `spi3`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H098: add antecedent 30-day precipitation anomaly
- **Prior**: 0.36
- **Mechanism**: same mechanism, simpler proxy.
- **Single change**: add `precip_30d_anomaly`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H099: add soil-moisture percentile from ERA5-Land
- **Prior**: 0.34
- **Mechanism**: direct soil moisture rather than proxy. ERA5-Land
  [56] provides it.
- **Single change**: add `soil_moisture_pct`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add (gated on ERA5-Land)

---

## Theme 17 — Holiday and weekday confounders (4 hypotheses)

### H100: add week-of-year cyclic sine/cosine
- **Prior**: 0.56
- **Mechanism**: seasonality dominates weekly mortality [3, 6, 68].
  Cyclic encoding is essential for pooled models.
- **Single change**: add `week_of_year_sin`, `week_of_year_cos`.
- **Expected effect**: +0.04–0.08 R² on p-score; +0.02 AUROC.
- **Phase**: Phase 2 single-add (high prior — almost baseline)

### H101: add holiday flag
- **Prior**: 0.30
- **Mechanism**: public holidays shift reporting and movement patterns
  [3, 6, 68]. Gasparrini always includes a holiday dummy.
- **Single change**: add `holiday_flag`.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

### H102: interact week-of-year with Tw_night (seasonal modifier)
- **Prior**: 0.44
- **Mechanism**: early-season heat (June) kills disproportionately because
  the population is un-acclimatised [127]. Gasparrini 2016 [127] showed
  a time-varying heat-mortality slope within the warm season.
- **Single change**: add `tw_night_x_sin_week`.
- **Expected effect**: +0.02 AUROC.
- **Phase**: Phase 2 single-add

### H103: add week-of-summer (days since June 1)
- **Prior**: 0.38
- **Mechanism**: early-summer vs late-summer acclimatisation [127].
  Linear encoding is simpler than sine/cosine for this subset.
- **Single change**: add `days_since_jun1` masked to 0 outside summer.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 18 — Pandemic indicator (2 hypotheses)

### H104: add pandemic dummy, keep COVID weeks in training
- **Prior**: 0.34
- **Mechanism**: rather than excluding 2020-W11 to 2022-W26 (the Phase
  0.5 default), keep those weeks with a pandemic dummy that the model
  can absorb. More data at the cost of confounding risk [60, 61, 156,
  158].
- **Single change**: set `exclude_pandemic=False` in
  `compute_expected_baseline`; add `pandemic_indicator` feature.
- **Expected effect**: −0.01 AUROC (confounding > data gain).
- **Phase**: Phase 2 single-add

### H105: Farrington-style baseline instead of same-week mean
- **Prior**: 0.48
- **Mechanism**: Farrington 1996 is the UK HPA outlier-robust baseline;
  Nielsen-Vestergaard [154, 155] EuroMOMO uses it. Better handling of
  pandemic weeks via outlier down-weighting [61, 157].
- **Single change**: replace `compute_expected_baseline` with a
  Farrington-style baseline.
- **Expected effect**: +0.01–0.03 AUROC via improved p-score quality.
- **Phase**: Phase 2 single-add

---

## Theme 19 — External-shock features (3 hypotheses)

### H106: add Storm Events "Excessive Heat" flag from NOAA
- **Prior**: 0.32
- **Mechanism**: NOAA Storm Events database records heat-related
  fatalities; the "Excessive Heat" event label is a weak ground-
  truth signal for "bad heat" events. Complements mortality with a
  different source.
- **Single change**: add `storm_events_heat_flag` (US only).
- **Expected effect**: +0.01 AUROC on US subset.
- **Phase**: Phase 2 single-add

### H107: add power-outage flag
- **Prior**: 0.28
- **Mechanism**: power outages during heat waves (especially AC loss)
  are a known mortality amplifier; Houston 2021 post-winter-storm
  and repeated summer brownout events in Phoenix. Data coverage is
  patchy.
- **Single change**: add `power_outage_flag`.
- **Expected effect**: +0.01 AUROC on affected weeks.
- **Phase**: Phase 2 single-add (data availability gate)

### H108: add wildfire acres burned (in-state)
- **Prior**: 0.26
- **Mechanism**: continuous analogue of the wildfire smoke flag, via
  NIFC data. Smoke is non-binary.
- **Single change**: add `wildfire_acres_burned_state`.
- **Expected effect**: +0.00–0.01 AUROC.
- **Phase**: Phase 2 single-add

---

## Theme 20 — Calibration improvements (4 hypotheses)

### H109: isotonic regression post-calibration
- **Prior**: 0.42
- **Mechanism**: LightGBM classification probabilities are often
  miscalibrated at tails; isotonic regression on a held-out fold
  fixes this without changing ranking [140, 142, 198].
- **Single change**: add `CalibratedClassifierCV(method='isotonic')`.
- **Expected effect**: Brier score −0.005; AUROC unchanged.
- **Phase**: Phase B optimisation

### H110: Platt scaling post-calibration
- **Prior**: 0.36
- **Mechanism**: simpler alternative to isotonic; assumes sigmoid
  miscalibration.
- **Single change**: `CalibratedClassifierCV(method='sigmoid')`.
- **Expected effect**: Brier −0.003.
- **Phase**: Phase B optimisation

### H111: conformal prediction intervals on p-score
- **Prior**: 0.40
- **Mechanism**: conformal inference gives distribution-free coverage
  guarantees on the excess-mortality prediction interval. Useful for
  HHWS decision-making where false-alarm rate must be bounded.
- **Single change**: wrap final model in Mapie `MapieRegressor`.
- **Expected effect**: no AUROC change; adds calibrated intervals.
- **Phase**: Phase B optimisation

### H112: Brier score targeting via focal loss
- **Prior**: 0.34
- **Mechanism**: focal loss (Lin et al.) down-weights easy negatives
  and up-weights hard positives, improving tail-class performance.
  The HDR concern is tail events.
- **Single change**: implement LightGBM focal-loss objective.
- **Expected effect**: +0.01 AUROC.
- **Phase**: Phase B optimisation

---

## Theme 21 — Forecasting horizon ablations (4 hypotheses)

### H113: predict deaths same-week (nowcast, horizon 0)
- **Prior**: 0.60
- **Mechanism**: same-week prediction is the upper bound — most
  information is available. The Phase 0.5 default.
- **Single change**: baseline (no lag on features).
- **Expected effect**: this is the benchmark against which the
  lagged-horizon hypotheses compete.
- **Phase**: Phase 2 single-add (baseline reference)

### H114: predict deaths 1-week ahead
- **Prior**: 0.48
- **Mechanism**: HHWS operational horizon is typically 5–7 days [95,
  96, 101, 106]. 1-week lead matches this.
- **Single change**: lag all features by 1 week from the target.
- **Expected effect**: −0.05 AUROC vs nowcast; still useful.
- **Phase**: Phase 2 single-add

### H115: predict deaths 2-weeks ahead
- **Prior**: 0.30
- **Mechanism**: public-health response (cooling-centre staffing,
  outreach to isolated elderly) needs 10+ day lead times [95, 97].
  Much harder — tests upper limit of forecastability.
- **Single change**: lag all features by 2 weeks.
- **Expected effect**: −0.15 AUROC vs nowcast.
- **Phase**: Phase 2 single-add

### H116: predict deaths 3-weeks ahead
- **Prior**: 0.18
- **Mechanism**: planning horizon; almost certainly outperformed by
  climatology alone.
- **Single change**: lag all features by 3 weeks.
- **Expected effect**: −0.20 AUROC vs nowcast.
- **Phase**: Phase 2 single-add

---

## Prior-ranked top-25 summary

| rank | H-id | title | prior | phase |
|---:|:---|:---|---:|:---|
| 1 | H001 | add `tw_night_c_max` | 0.70 | 2 |
| 2 | H002 | add `tw_night_c_mean` | 0.68 | 2 |
| 3 | H003 | add both tw_night max and mean | 0.66 | 2 |
| 4 | H004 | consecutive-night-above-threshold count | 0.63 | 2 |
| 5 | H067 | city fixed effects (temporal split) | 0.62 | 2 |
| 6 | H005 | day-night Tw spread | 0.62 | 2 |
| 7 | H057 | prior-week p-score | 0.62 | 2 |
| 8 | H072 | binary classifier on p_score ≥ 0.10 | 0.62 | 2 |
| 9 | H113 | nowcast baseline reference | 0.60 | 2 |
| 10 | H006 | tropical-night count (dry-bulb) | 0.60 | 2 |
| 11 | H007 | wet-bulb tropical-night count | 0.60 | 2 |
| 12 | H046 | lag-0/1 tmax rolling max | 0.60 | 2 |
| 13 | H008 | p95 anomaly of tw_night_c_max | 0.58 | 2 |
| 14 | H037 | NWS HeatRisk as feature | 0.58 | 2 |
| 15 | H050 | DLNM cross-basis 3×4 (dry-bulb) | 0.58 | 2 |
| 16 | H009 | p90 anomaly of tw_night_c_mean | 0.56 | 2 |
| 17 | H066 | country fixed effects | 0.56 | 2 |
| 18 | H100 | week-of-year cyclic | 0.56 | 2 |
| 19 | H028 | Tang 2-day compound flag | 0.56 | 2 |
| 20 | H054 | AC penetration | 0.54 | 2 |
| 21 | H035 | EuroHEAT flag | 0.54 | 2 |
| 22 | H015 | night-time UTCI | 0.54 | 2 |
| 23 | H077 | quantile regression at τ=0.95 | 0.54 | 2 |
| 24 | H090 | Quantile LightGBM τ=0.9 | 0.54 | 2 |
| 25 | H047 | 0-14 day Tw rolling mean | 0.54 | 2 |

---

## Phase 2.5 composition candidates (top-5, expected after Phase 2)

These are "add two confirmed Phase 2 levers simultaneously" candidates that
become testable once the Phase 2 stage produces ≥ 2 confirmed wins.

### C001: `tw_night_c_max + tw_night_c_mean + DLNM cross-basis on night-Tw`
- **Prior**: 0.48
- **Mechanism**: combines H001 + H002 + H051. Full flagship stack.
- **Phase**: Phase 2.5 composition

### C002: `tw_night_c_max + pct_age_65p + ac_penetration_pct`
- **Prior**: 0.44
- **Mechanism**: flagship feature + vulnerability moderators (H001 +
  H053 + H054). Matches Sera 2019 [193] meta-regression structure.
- **Phase**: Phase 2.5 composition

### C003: `tw_compound_flag + prior_week_pscore + week_of_year_sin/cos`
- **Prior**: 0.42
- **Mechanism**: compound + autocorrelation + seasonality (H019 + H057 +
  H100). Captures the three orthogonal signal sources.
- **Phase**: Phase 2.5 composition

### C004: `H050 DLNM cross-basis + H051 DLNM night-Tw cross-basis + Gasparrini P-spline`
- **Prior**: 0.40
- **Mechanism**: full DLNM replication both on day and night basis
  with penalised splines [5]. Direct MCC-style baseline [6, 117].
- **Phase**: Phase 2.5 composition

### C005: `H015 night-UTCI + H026 WBGT + H014 Davies-Jones Tw`
- **Prior**: 0.36
- **Mechanism**: "every humid-heat metric simultaneously" composition.
  Tests whether ensembling physiological metrics beats any single one,
  which is the Lo et al. 2023 [53] concern.
- **Phase**: Phase 2.5 composition

---

## Notes on dependencies and gates

- **ERA5 CDS account gates**: H014, H015, H023, H026, H094, H095, H099.
- **Air-quality loader gates** (Phase 1): H061, H062, H063, H064, H065.
- **Population loader gates** (Phase 1 Eurostat `demo_r_pjanaggr3`): H053,
  H070, H074, C002.
- **AC-prevalence loader gates** (Phase 1 Gross 2025 [212] / ORNL [213]):
  H017, H054, C002.
- **NWS HeatRisk archive gate**: H037.
- **Storm Events gate**: H106.
- **Age-stratified EU loader gate**: H074.
- **Wildfire smoke gate** (HMS): H063, H108.
- **Independent of any gates** (runnable today with Phase 0.5 loaders):
  H001, H002, H003, H004, H005, H006, H007, H008, H009, H010, H011,
  H012, H013, H018, H019, H020, H021, H022, H025, H027, H028, H029,
  H030, H031, H032, H033, H034, H035, H046, H047, H048, H049, H050,
  H051, H052, H057, H058, H066, H067, H068, H069, H070, H071, H072,
  H073, H077, H078, H079, H080, H081, H082, H083, H084, H085, H086,
  H087, H088, H089, H090, H091, H092, H093, H100, H101, H102, H103,
  H104, H105, H109, H110, H111, H112, H113, H114, H115, H116.

The Phase 0.5 ready subset is 75 hypotheses of the 116. The flagship theme
(H001–H022, 22 hypotheses) is fully Phase 0.5 runnable.
