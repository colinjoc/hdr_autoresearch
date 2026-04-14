# Research Queue — Housing Crash Prediction

Each hypothesis: `[id] STATEMENT | design variable | expected outcome |
metric | baseline | prior`. Prior = subjective probability that the
result holds in a pre-registered test.

---

## Theme A — Crash definition (threshold, window, rolling vs peak-to-trough)

[A1] A 12-month trailing ZHVI return ≤ −10% gives the best balance of
early-warning utility and precision for a metro-month panel | y
definition | baseline prevalence 3-5% | Brier, AUC | 24m peak-to-trough
≥15% | 0.55

[A2] A stricter 24-month peak-to-trough ≥ 20% threshold is too sparse to
train a useful metro-level classifier | y definition | prevalence <1% |
AUC collapse | A1 | 0.75

[A3] A "rapid crash" definition (6-month trailing ZHVI ≤ −7%) matters
most for the 2022-24 cycle because of faster Fed-driven transmission | y
definition | 2022-24 recall | hit rate on Austin/Boise/Phoenix | A1 |
0.70

[A4] Using peak-to-trough as the label introduces look-ahead leakage if
the peak is identified ex post | methodology | zero-skill placebo |
chance-level AUC | peak-to-trough as y | 0.95

[A5] Rolling-window definitions produce label auto-correlation within
metros that inflates in-sample AUC | methodology | robust SE | AUC
deflation after clustering | naive AUC | 0.85

[A6] A two-level label (minor vs deep crash) improves calibration at
the expense of raw AUC | y definition | Brier | one-vs-rest logit | A1 |
0.45

[A7] Defining crash onset as first month of sustained month-on-month
decline (3 consecutive negative months) produces cleaner event times |
y definition | event-time alignment | kernel density of onset months |
A1 | 0.60

[A8] Absolute percentage decline matters less than position relative to
metro's own history (z-score vs own 20-year mean) | y definition | AUC |
Brier | A1 | 0.40

[A9] ZHVI smoother introduces 2-3 months of lookback in the label itself
| data | zero-shift test | correlation of y_t with price_t+2 | raw
y | 0.90

[A10] Using Case-Shiller (unsmoothed) as y and ZHVI features as X
resolves A9 with minimal data loss | methodology | AUC holds | vs A9 |
A1 | 0.65

## Theme B — Feature engineering

[B1] Price-to-income ratio above 5.0 is the single most predictive
univariate feature for 2006-09 crashes | feature PI | AUC | 0.65-0.70 |
momentum-only | 0.70

[B2] Price-to-rent ratio (ZHVI / Zillow ZRI) improves over price-to-
income because rent is more frictionless and updates faster | feature
PR | AUC | +0.03 vs B1 | B1 | 0.55

[B3] Inventory-turnover ratio (active listings / monthly sales) fires
3-9 months before crash | feature INV_TO | F1 | 0.50+ at 6-month lead |
PI only | 0.75

[B4] Median days-on-market change (YoY delta) is a faster leading
indicator than inventory build-up in 2022-24 cycle | feature DOM_YOY |
recall at 3m lead | 0.60+ | INV_TO | 0.50

[B5] Share of active listings with price reductions leads crashes by
2-4 months | feature PR_REDUCE | F1 | 0.45+ | DOM_YOY | 0.55

[B6] Price momentum (12-month return) is a two-edged feature: positive
momentum at extreme ratios flips from bullish to bearish | feature
MOMXPI interaction | sign of interaction | non-monotone | linear | 0.60

[B7] 30-year mortgage rate *delta* (12m change) matters more than level
| feature DMRT | AUC | +0.04 vs MRT level | MRT level | 0.70

[B8] Unemployment rate YoY change as crash confound: controls for
economy-wide shock | feature DUNEMP | drop in feature importance after
adding | SHAP | nothing | 0.40

[B9] Population-growth YoY is a crash *precursor* in migration-driven
metros | feature POP_YOY | AUC in Sun Belt subset | 0.65+ | nothing |
0.55

[B10] Permit-to-sales ratio proxies speculative overbuilding | feature
PERMIT_SALES | AUC | +0.03 | PI only | 0.45

[B11] Building-permits acceleration (MoM) as supply-shock proxy |
feature PERMIT_ACC | SHAP sign | negative | nothing | 0.35

[B12] Non-occupant-buyer share (Zillow investor data where available)
flags speculation | feature INVSHARE | AUC | +0.05 | nothing | 0.60

[B13] ZHVI volatility (12-month rolling std of monthly returns) as
regime flag | feature VOL | AUC | +0.02 | nothing | 0.50

[B14] Price-index dispersion across tiers (top vs bottom third) signals
segment-specific bubble | feature TIER_DISP | AUC in tier-specific
crashes | 0.60 | nothing | 0.40

[B15] Metro-level wealth-effect proxy via stock-market exposure | feature
STOCK_EXP | AUC in tech-heavy metros | modest | nothing | 0.25

[B16] Realtor.com new-listings delta is leading indicator before
inventory build-up | feature NEWLIST_YOY | 1m lead | +0.03 | INV_TO |
0.45

[B17] Price-per-square-foot vs construction-cost delta | feature
PPSF_CC | SHAP | bubble flag | nothing | 0.40

[B18] Migration in/out flows from IRS SOI data as demand proxy |
feature MIG_NET | AUC in 2022-24 subset | 0.60+ | nothing | 0.65

[B19] Short-term rental (Airbnb) saturation as hidden-demand proxy |
feature STR_SAT | AUC | +0.02 in tourist metros | nothing | 0.30

[B20] Mortgage-origination share by product (ARM vs fixed) was
predictive in 2006-09 but irrelevant in 2022-24 | feature ARMSHARE |
coefficient sign | era-dependent | pool | 0.75

[B21] Credit-growth acceleration at metro level (HMDA-based) | feature
HMDA_ACC | AUC 2006-09 | 0.70 | PI | 0.70

[B22] Combined Shiller-ratio deviation from own-metro long-run mean |
feature PI_DEV | AUC | +0.02 | raw PI | 0.50

[B23] Median household income growth (lagged 1y) | feature INC_YOY |
AUC | +0.01 | nothing | 0.30

[B24] Property-tax and insurance-cost growth (relevant post-2023 FL/CA)
| feature INSCOST_YOY | AUC in FL/CA | moderate | nothing | 0.55

[B25] Number of Realtor.com pending sales (contract-to-closing lag) |
feature PEND_DELTA | 2m lead | +0.02 | nothing | 0.40

## Theme C — Matching / causal — prediction vs identification

[C1] This project is a *prediction* problem not a causal-identification
problem per Kleinberg-Ludwig-Mullainathan-Obermeyer (200) | methodology
| honest framing | no causal claims in paper | nothing | 1.00

[C2] SHAP-based attribution can still surface hypothesis-worthy causal
conjectures even when the model itself is predictive | methodology |
sensible SHAP rankings | nothing | 0.70

[C3] Double ML (Chernozhukov et al. 197) could be used for one causal
subquestion (e.g., effect of credit on crash risk) but is out of scope
for primary deliverable | methodology | reserve for Phase 2 | nothing |
0.80

[C4] Negative controls (see Theme M) are more important than any
causal-identification strategy here | methodology | placebos fail as
expected | nothing | 0.90

## Theme D — Heterogeneity

[D1] Supply-inelastic metros (Saiz <1.5) crash deeper than elastic ones,
conditional on similar price-to-income | feature SUPPELAS interaction |
interaction coef | negative | pool | 0.55

[D2] The D1 relationship is attenuated in 2022-24 relative to 2006-09 —
Austin/Boise break the pattern | interaction | era-dependent interaction
| significant difference | pool | 0.75

[D3] Coastal metros have persistently higher baseline crash probability
but with longer lead times than inland | feature COAST | AUC | marginal
| nothing | 0.35

[D4] Migration-gaining metros (positive 2y net-migration) have *higher*
crash-risk conditional on high PI because demand is elastic with
remote-work sentiment | interaction MIG_NET × PI | positive coef | two-
sided | 0.65

[D5] Shrinking metros crash for different reasons (population loss vs
bubble) and should be modelled separately | subsample model | improves
overall AUC | pool | 0.60

[D6] Tech-heavy metros (SF, Seattle, Austin, Raleigh) co-move with
Nasdaq and carry additional wealth-effect risk | feature TECH | AUC in
subset | marginal | nothing | 0.40

[D7] Tourist/STR-heavy metros have unique mid-cycle demand channel |
feature STR_SHARE | AUC | marginal | nothing | 0.30

[D8] University towns have stable demand floors, less cyclical | feature
EDU_SHARE | lower volatility | yes | nothing | 0.55

[D9] Retirement-destination metros (FL, AZ) are sensitive to demographic
waves, 2020-22 pandemic relocation was a one-off shock | feature RETIRE
| era-specific shock | yes | nothing | 0.60

## Theme E — Confound sensitivity

[E1] Interest rates alone explain <25% of 2006-09 price variance per
Glaeser-Gottlieb-Gyourko (29); features must add > nothing | feature
ablation | AUC drop | moderate | nothing | 0.75

[E2] Adding macro controls (GDP growth, unemployment, CPI) reduces
feature importance of price-to-income modestly but not to zero | SHAP |
−10-20% | nothing | 0.70

[E3] Era dummy (pre/post 2015) absorbs much mechanism-level variance |
feature ERA | SHAP | yes | pool | 0.80

[E4] Removing the 2006-09 crash from training data tests whether the
mechanism is fundamentally different in 2022-24 | subsample | AUC drop
on 2022-24 | moderate | pool | 0.65

[E5] Removing tech-shock sensitive metros (SF, Seattle, Austin, SJ)
tests residual predictability | subsample | AUC hold | moderate | pool |
0.50

## Theme F — Temporal validity (2006-09 vs 2022-24 transfer)

[F1] A model trained on 2001-2011 predicts 2022-24 poorly: cross-era
AUC gap ≥ 0.10 | transfer | cross-era AUC | worse than in-era | pool |
0.70

[F2] Adding era dummy reduces but does not eliminate transfer gap |
transfer | AUC gap | residual | era-dummy model | 0.60

[F3] A model trained only on 2018-2021 (pre-crash of both eras) will
generalise worse than pooled | transfer | AUC | < pooled | pooled | 0.60

[F4] Features with sign-consistent coefficients across eras (PI ratio,
inventory) transfer best | feature stability | cross-era coef sign
agreement | yes | ARM-share | 0.75

[F5] Credit-supply features (subprime share, HMDA credit growth) do
*not* transfer: strong in 2006-09, null in 2022-24 | feature stability |
coef change | large | pool | 0.80

[F6] Remote-work / migration features transfer in the opposite direction:
null in 2006-09, strong in 2022-24 | feature stability | era-specific |
yes | pool | 0.70

[F7] A mixture-of-experts model with era-specific sub-models beats
pooled | methodology | AUC | +0.02 | pooled | 0.45

## Theme G — Leading-indicator timing

[G1] Inventory builds 3-9 months before price decline | timing | lag
regression peak | 6m | nothing | 0.70

[G2] Median DOM rises 2-6 months before price decline | timing | lag
| 4m | nothing | 0.70

[G3] Price reductions rise 1-3 months before decline | timing | lag | 2m
| nothing | 0.70

[G4] Mortgage-rate shocks transmit to prices in 6-12 months (2022-24
was faster, 3-6) | timing | impulse-response peak | era-dependent |
nothing | 0.65

[G5] Migration-flow signals (IRS SOI, USPS) available at 6-12 month lag
— too late for real-time prediction | data | lag | too slow | nothing |
0.80

[G6] Google Trends for "home buying", "mortgage rates", "recession" as
real-time proxy | feature GTRENDS | correlation with migration | yes |
nothing | 0.45

[G7] Listings new-to-active ratio rises *before* total active listings |
timing | sub-monthly lead | 1-2m | INV_TO | 0.55

[G8] Sale-to-list-price ratio declines before listing inventory visibly
builds | timing | lead | 2-3m | INV_TO | 0.60

[G9] Pending-sales-to-closings spread widens before price decline |
timing | lead | 1-2m | nothing | 0.50

## Theme H — Hyperparameters

[H1] LightGBM with max_depth=6, learning_rate=0.05, 500 trees is a
sensible starting point | hyperparameter | AUC | 0.72 | default | 0.60

[H2] Regularisation (L2 alpha 0.1-1.0) matters more than model capacity
for out-of-sample | hyperparameter | AUC gap to unreg | +0.02 | unreg |
0.75

[H3] Monotonicity constraints (PI ↑ → prob ↑, INV ↑ → prob ↑) improve
transfer | hyperparameter | cross-era AUC | better | unconstrained |
0.70

[H4] Class-imbalance handling via scale_pos_weight preferred to SMOTE |
hyperparameter | calibration | better | SMOTE | 0.80

[H5] Feature scaling (log price-to-income rather than raw) improves
linear-model transfer | preprocessing | AUC | +0.01 | raw | 0.65

## Theme I — Calibration

[I1] Raw XGBoost/LightGBM outputs are miscalibrated; Platt scaling
required | calibration | Brier | improves | raw | 0.90

[I2] Isotonic beats Platt on > 1000 validation points | calibration |
Brier | improves | Platt | 0.55

[I3] Calibration on time-blocked validation set maintains calibration
across eras | calibration | Brier on held-out era | good | pooled cal |
0.60

[I4] Calibration plot (reliability diagram) is part of reported
deliverable, not AUC alone | methodology | report presence | yes |
AUC-only | 1.00

## Theme J — Model family

[J1] Penalised logit provides the most interpretable baseline with
competitive AUC | model | AUC ≈ 0.70 | LightGBM +0.02 | nothing | 0.65

[J2] LightGBM with monotone constraints beats pure logit by 0.02-0.04
AUC | model | AUC | +0.02 | logit | 0.60

[J3] Random forest is slightly worse than LightGBM on tabular metro-
month data | model | AUC | −0.01 | LightGBM | 0.55

[J4] A Bayesian hierarchical model with metro-type random effects
improves calibration without AUC gain | model | Brier | improves |
pooled | 0.45

[J5] LSTM/TCN time-series models do not improve over tabular features
given the limited number of crash events | model | AUC | comparable |
LightGBM | 0.65

[J6] Stacking logit + LightGBM + hierarchical improves Brier modestly |
model | Brier | +0.005 | single | 0.40

[J7] Pre-trained time-series foundation models (e.g. Chronos) do not
improve because our outcome is a binary derived from prices, not price
forecasting itself | model | AUC | same | LightGBM | 0.70

## Theme K — Temporal CV (MANDATORY)

[K1] Blocked rolling-origin CV with 12-month folds is the *minimum*
methodology | CV scheme | AUC honest | yes | random-split | 1.00

[K2] 2006-09 held out entirely as test era | CV scheme | no leak | yes |
nothing | 1.00

[K3] 2022-24 held out entirely as test era | CV scheme | no leak | yes |
nothing | 1.00

[K4] Within-metro time-block CV to test metro-specific generalisation |
CV scheme | AUC per metro | plot distribution | nothing | 0.90

[K5] Nested CV for hyperparameter selection never peeks at either
holdout era | CV scheme | confirm | yes | flat CV | 1.00

[K6] Pre-registration of exact CV splits before running any model | CV
scheme | commit hash | yes | none | 1.00

[K7] Publish the exact list of (metro, month) in each CV fold with the
paper | CV scheme | reproducibility | yes | hidden | 0.95

## Theme L — Interactions

[L1] PI × supply-elasticity: high PI punishes inelastic metros more |
interaction | sign | negative elasticity coef | additive | 0.60

[L2] Mortgage-rate delta × leverage: rate shocks matter more for
leveraged metros | interaction | sign | positive | additive | 0.65

[L3] Momentum × distance-from-fundamentals: momentum is bullish until
PI > 5, then bearish | interaction | non-monotone | yes | linear | 0.55

[L4] Inventory × DOM: joint rise means crash risk more than either alone
| interaction | synergy SHAP | yes | additive | 0.60

[L5] Migration × WFH feasibility: for metros with remote-work sensitive
occupations, migration-in predicts larger subsequent crash | interaction
| era-specific | 2022-24 only | pool | 0.55

[L6] Price-reductions × DOM: both rising sharply = imminent decline |
interaction | synergy | yes | additive | 0.65

[L7] Credit-growth × LTV-distribution: 2006-09 only | interaction |
era-specific | yes | pool | 0.75

## Theme M — Negative controls (MANDATORY)

[M1] Fake-crash placebo: shuffle crash labels within year across metros;
model AUC should drop to ~0.50 | placebo | AUC | 0.50 ± 0.03 | real
labels | 0.95

[M2] Metro-permutation test: permute metro identity at test; model
should not rely on metro-ID alone | placebo | AUC | minimal drop | real
| 0.85

[M3] Pre-crash placebo: predict crash 24 months *before* actual onset;
should show zero skill | placebo | AUC | ~0.55 max | main | 0.85

[M4] Backshift placebo: shift all features backward 36 months; prediction
shouldn't work | placebo | AUC | 0.50-0.55 | main | 0.90

[M5] Non-crash metro placebo: restrict test set to Dallas, Indianapolis,
Kansas City — metros with negligible crashes; model should predict low
probabilities | placebo | mean predicted prob | <0.05 | main | 0.75

[M6] Randomised-timing placebo: use randomly-drawn "crash dates" within
each metro's timeline; model should fail | placebo | AUC | 0.50 | main |
0.90

[M7] Year-holdout placebo: hold out random year across all metros,
predict that year; compare to era-holdout | placebo | AUC gap | yes |
era-holdout | 0.75

## Summary counts

- Theme A: 10 hypotheses
- Theme B: 25 hypotheses
- Theme C: 4 hypotheses
- Theme D: 9 hypotheses
- Theme E: 5 hypotheses
- Theme F: 7 hypotheses
- Theme G: 9 hypotheses
- Theme H: 5 hypotheses
- Theme I: 4 hypotheses
- Theme J: 7 hypotheses
- Theme K: 7 hypotheses
- Theme L: 7 hypotheses
- Theme M: 7 hypotheses

**Total: 106 hypotheses** (exceeds 100 floor).

Pre-registered primary targets: A1 (crash definition), B1-B5 (core
features), K1-K3 (temporal CV scheme), M1-M3 (mandatory negative
controls). Everything else is secondary / robustness.
