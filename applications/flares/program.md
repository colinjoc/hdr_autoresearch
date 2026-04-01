# Autoresearch: Solar Flare Prediction from Active Region Properties -- HDR

**Local**: `/home/col/generalized_hdr_autoresearch/applications/flares/`
**Venv**: `source /home/col/generalized_hdr_autoresearch/applications/flares/venv/bin/activate`

## Objective

Maximise **TSS** (True Skill Statistic) and **BSS** (Brier Skill Score) on 24-hour C+ flare prediction from NOAA active region properties, using Hypothesis-Driven Research (HDR).

**Primary metric: TSS** = TPR - FPR (True Skill Statistic, equivalent to Hanssen-Kuipers discriminant). Range [-1, 1], 1 = perfect, 0 = no skill. Standard in solar flare forecasting community.
**Secondary metric: BSS** (Brier Skill Score) = 1 - BS/BS_ref. Measures probabilistic forecast quality relative to climatology. Range (-inf, 1], 1 = perfect.
**Tertiary metric: AUC-ROC** — threshold-independent discrimination.
**Stretch target**: TSS > 0.65, AUC > 0.90

**Benchmark**: Hayes (2021) solar flare forecast project
- Dataset: `AR_flare_ml_23_24.csv` — 33,516 active region-day records (Aug 1996 – Dec 2018, solar cycles 23+24)
- 10 input features per sample (3 numerical, 3 categorical, 4 positional)
- Binary classification: did this AR produce a C-class or above flare in the next 24 hours?
- Current best published results:
  - McStat (Poisson): TSS 0.50, AUC 0.82
  - McEvol (Poisson): TSS 0.49, AUC 0.78
  - Gradient Boost: TSS 0.57, BSS 0.59, AUC 0.87

**Key reference**: Bloomfield et al. 2012, ApJ Letters 747, L41 — "Toward Reliable Benchmarking of Solar Flare Forecasting Methods"

---

## Dataset Description

**Source**: https://github.com/hayesla/flare_forecast_proj/tree/main/databases
**File**: `AR_flare_ml_23_24.csv`

Each row = one active region on one day. Features from NOAA Solar Region Summary (SRS) files.

### Features

| Feature | Type | Description |
|---------|------|-------------|
| `AR issue_date` | datetime | Date of observation (00:30 UTC daily) |
| `noaa_ar` | int | NOAA active region number |
| `Carrington_long` | int | Carrington longitude (0-360) |
| `AREA` | int | Active region area (millionths of solar hemisphere, MSH) |
| `McIntosh` | categorical | McIntosh 3-letter classification (63 classes) — encodes Zurich class + penumbral type + compactness |
| `Longitude_extent` | int | Longitudinal extent of sunspot group (heliographic degrees) |
| `Latitude` | int | Heliographic latitude |
| `Longitude` | int | Heliographic longitude |
| `No_sunspots` | float | Number of sunspots in the AR |
| `MAGTYPE` | categorical | Hale magnetic classification (7 classes: ALPHA, BETA, BETA-GAMMA, BETA-GAMMA-DELTA, BETA-DELTA, GAMMA, GAMMA-DELTA) |
| `LOCATION` | string | Heliographic location string (e.g., "S09E22") |

### Targets

| Column | Description |
|--------|-------------|
| `C` | Number of C-class flares that day |
| `M` | Number of M-class flares that day |
| `X` | Number of X-class flares that day |
| `C+` | Number of C-class-or-above flares (C + M + X) — **primary target** |
| `M+` | Number of M-class-or-above flares (M + X) |
| `X+` | Number of X-class flares |

**Binary target**: `y = (C+ > 0).astype(int)` — "did this AR produce at least one C+ flare today?"

### Class Distribution

- **No flare (C+ = 0)**: 27,229 (81.2%)
- **Flare (C+ > 0)**: 6,287 (18.8%)
- Imbalanced — 4.3:1 negative-to-positive ratio

### Train/Test Split

- **Train**: First 80% of data chronologically (Aug 1996 – ~mid 2014) — used for HDR loop
- **Test**: Last 20% chronologically (~mid 2014 – Dec 2018) — used for HDR loop evaluation
- **Holdout validation**: Any data after 2017-12-31 can be used for additional validation but is NOT used in the HDR loop scoring

The temporal split prevents data leakage — the model never sees future active regions during training.

---

## File Structure

```
strategy.py          # The ONLY file the agent modifies
prepare.py           # Evaluation engine (fixed, never modify)
program.md           # This file — instructions + domain context
observations.md      # Signal ideas and DATA GAPS observed during experiments
research_queue.md    # Prioritised questions (OPEN / RESOLVED / RETIRED)
knowledge_base.md    # Cumulative findings (what works, what doesn't, why)
results.tsv          # One row per cycle — all metrics
literature_review.md # Structured literature review
feature_candidates.md # Domain quantities mapped to computable features
papers.csv           # Paper tracking
data/                # Dataset files
literature/          # Downloaded PDFs
charts/              # Output plots
```

---

## Available Features for Engineering

**From McIntosh classification (3-letter code, e.g., "DSO"):**
- Letter 1: Modified Zurich class (A, B, C, D, E, F, H) — size/complexity
- Letter 2: Penumbral type (X, R, S, A, H, K) — penumbra of largest spot
- Letter 3: Compactness (X, O, I, C) — spot distribution

These sub-components can be extracted and used individually — each encodes different physics.

**From MAGTYPE:**
- Magnetic complexity is the single strongest predictor of flare productivity
- BETA-GAMMA-DELTA ARs produce the most M/X flares (Fig 9 in Hayes 2021)
- Can be ordinal-encoded by complexity: ALPHA < BETA < BETA-GAMMA < BETA-DELTA < BETA-GAMMA-DELTA

**Derived features (domain-informed):**
- `log(AREA)` — area spans 3 orders of magnitude; log-transform linearizes relationship with flare flux
- `log(No_sunspots + 1)` — same rationale
- McIntosh sub-components as separate features
- MAGTYPE complexity ordinal
- Interaction: `AREA * MAGTYPE_complexity` — large complex regions are most dangerous
- Absolute latitude (distance from equator)
- Longitude position relative to central meridian (limb effects)

---

## Metrics

### True Skill Statistic (TSS)
```
TSS = TPR - FPR = TP/(TP+FN) - FP/(FP+TN)
```
- Insensitive to class imbalance (unlike accuracy)
- Standard metric in solar flare forecasting (Bloomfield et al. 2012)
- Requires choosing a probability threshold — report max TSS over all thresholds

### Brier Skill Score (BSS)
```
BS = (1/N) * sum((p_i - o_i)^2)    # Brier Score
BSS = 1 - BS / BS_climatology      # Relative to always predicting base rate
```
- Measures probabilistic calibration
- Does not require a threshold choice

### AUC-ROC
- Area under the ROC curve
- Threshold-independent discrimination

---

## Constraints

- DO NOT modify prepare.py or any file except strategy.py
- DO NOT import anything beyond numpy, pandas, scipy, scikit-learn, xgboost
- Each evaluation must complete in < 60 seconds
- ONE change per experiment (isolation principle)
- ALWAYS commit before running evaluation
- ALWAYS record results in results.tsv
- NEVER stop — keep iterating until the human stops you

---

## Cost Model

No cost model — this is pure classification, not trading. The evaluation is the metrics themselves.

---

## Domain Context

Solar flares are sudden releases of magnetic energy in the solar atmosphere, classified by peak X-ray flux:
- **C-class**: 10^-6 to 10^-5 W/m^2 (minor)
- **M-class**: 10^-5 to 10^-4 W/m^2 (moderate, can cause radio blackouts)
- **X-class**: > 10^-4 W/m^2 (major, can damage satellites, disrupt communications)

Flare prediction is an operational priority for space weather forecasting. The key insight from the literature is that **magnetic complexity** of the active region is the strongest predictor — regions with complex magnetic topology (BETA-GAMMA-DELTA) are far more likely to produce large flares.

The prediction window is 24 hours: given the state of an AR today, will it produce a C+ flare in the next 24 hours?
