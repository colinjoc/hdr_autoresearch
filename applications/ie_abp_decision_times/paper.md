# An Bord Pleanála Decision Times 2015–2025: A Queueing-Theoretic Descriptive Analysis of the 2022–2023 Compliance Collapse and 2025 Recovery

## Abstract

An Bord Pleanála (ABP), Ireland's national planning-appellate body, experienced a dramatic deterioration in its statutory objective period (SOP) compliance rate between 2018 and 2024, and is visibly recovering through Q3 2025 under its reconstituted successor An Coimisiún Pleanála (ACP). On the best-evidenced subset of the series, mean weeks-to-dispose rose from 18 weeks in 2017 (95% CI 17.2–18.8) through 26 weeks in 2022 (CI 24.9–27.1) to 42 weeks in 2023 and 2024 (CI 40.6–43.4 in each year), while all-cases SOP compliance fell from 64% in 2017 (CI 61.9–66.0) to 25% in 2024 (CI 23.6–26.4). The 2018–2021 rise is small; the collapse concentrates in a single year, 2022→2023. We fit five analytical model families to per-year aggregate data; an interrupted-time-series specification with knots at 2018, 2022 and 2023 (T02) wins the tournament with an in-sample mean absolute error (MAE) of 0.57 weeks, and under leave-one-year-out cross-validation degrades to 1.65 weeks — still the lowest of any family (next-best 2.91 weeks), but with a 2.9× overfit ratio that qualifies the headline precision. The utilisation ratio ρ = intake ÷ disposed moved 1.45 (2022) → 1.00 (2023) → 0.74 (2024), which is *arithmetically equivalent* to — not a causal explanation of — the observed backlog dynamics. Oaxaca–Blinder decomposition attributes ~100% of the 2018→2024 rise in mean weeks to within-case-type productivity change and ~0% to case-type mix shift, which supports ρ as the operative descriptive summary but cannot isolate its drivers. Case-type heterogeneity is extreme: 2024 Strategic Housing Development (SHD) cases had mean 124 weeks, with an approximate lognormal-fit median of ~79 weeks and 25th–75th percentile 42–151 weeks, while Large-scale Residential Development (LRD) cases cycled at a mean of 13 weeks (median ~12, 25th–75th percentile 9–16). Under Monte Carlo sensitivity across Phase B scenario parameters (5,000 draws), 2028 SOP compliance point estimates are 15% (S1 status quo), 48% (+20% full-time equivalent, FTE) and 36% (Planning and Development Act 2024, PDA-2024, effective), each with 5th–95th percentile bands of 60–67 percentage points — the scenario ranking is not robust (S1 beats S3 in 22.6% of draws). 2025 Q1–Q3 monthly compliance trended monotonically from 37% (January) to 77% (September) but the same Phase B functional form mispredicts the Q3 recovery by ~50 percentage points, showing the projection model is directionally indicative, not quantitatively anchored. The empirical trajectory is robust; the causal attribution and the forward scenarios are not.

## 1. Introduction

An Bord Pleanála was established under the Local Government (Planning and Development) Act 1976 as Ireland's national planning-appellate body. It decides planning appeals from local-authority decisions, Strategic Infrastructure Development (SID) applications, the fast-track housing categories (Strategic Housing Development (SHD) 2017–2021 and Large-scale Residential Development (LRD) 2021–present), Local Authority Own-Development (LAOD) cases, and statutory referrals. Under Part 17 of the Planning and Development Act 2024 (PDA-2024), An Bord Pleanála was reconstituted as An Coimisiún Pleanála (ACP) on 18 June 2025.

Since 1992 the Board's throughput has been measured against a statutory objective period (SOP) of 18 weeks for most appeals, 16 weeks for LRD, and case-specific durations for specialised categories. The SOP is an objective, not a binding deadline (Simons 2019; *McKillen v An Bord Pleanála* [2017] IESC 91), so non-compliance has political and reputational rather than legal consequence. Compliance hovered near 70–80% through the mid-2010s, fell to 28% in 2023 and 25% in 2024, and began recovering in 2025. Mean weeks-to-dispose rose from 18 weeks in 2017 to 42 weeks in 2023 and 2024. We characterise this trajectory descriptively, fit a range of models, and quantify how much confidence the aggregate-year data can actually support.

We ask: under a simple capacity-queueing description, how do the observed covariates (Board-member count, FTE, intake, backlog, case mix) co-move with decision time? What can and cannot be identified with n = 10 annual observations?

## 2. Detailed Baseline

**The baseline is the self-reported ABP figure.** Each year ABP publishes an Annual Report Appendix with Table 1 "Summary of all Planning Cases" (intake, disposal, backlog, SOP compliance, mean weeks) and Table 2 "Average Time Taken to Dispose of Cases (Weeks)" by case type (Normal Planning Appeals (NPA), Strategic Infrastructure, Strategic Housing, All Other). The baseline E00 series is:

| Year | Mean weeks (all cases) | 95% CI | SOP % | 95% CI (Wilson) | Provenance |
|---|---|---|---|---|---|
| 2015 | 17 | 16.2–17.8 | 75 | 72.9–77.0 | Bar-chart read-off, uncertain ±2 wk |
| 2016 | 17 | 16.2–17.8 | 63 | 60.6–65.4 | Bar-chart read-off, uncertain ±2 wk |
| 2017 | 18 | 17.2–18.8 | 64 | 61.9–66.0 | AR 2018 narrative (single sentence, p. 852 and Fig. 3) |
| 2018 | 23 | 22.2–23.8 | 43 | 41.2–44.8 | AR 2018 summary table (hand-verified) |
| 2019 | 22 | 21.2–22.8 | 69 | 67.3–70.6 | AR 2019 Appendix Table 1 |
| 2020 | 23 | 22.1–23.9 | 73 | 71.3–74.7 | AR 2020 Appendix Table 1 |
| 2021 | 20 | 19.3–20.7 | 57 | 55.1–58.8 | AR 2021 Appendix Table 1 |
| 2022 | 26 | 24.9–27.1 | 45 | 42.9–47.1 | AR 2022 Appendix Table 1 |
| 2023 | 42 | 40.6–43.4 | 28 | 26.5–29.6 | AR 2023 Appendix Table 1 |
| 2024 | 42 | 40.6–43.4 | 25 | 23.6–26.4 | AR 2024 Appendix Table 1 |

Mean-week CIs use a right-skewed Gaussian approximation with coefficient of variation 1.0 and n equal to the year's total disposals. SOP-% CIs use the Wilson binomial interval. **Provenance warning for 2015 and 2016:** neither all-cases mean-weeks figure is documented in any extant tabular source we could locate. The 2018 Annual Report Table 1 reports Normal-Planning-Appeals means (15, 16, 17 weeks for 2015–2017) and an all-cases mean only for 2017 (18 weeks) and 2018 (23.3 weeks). The 2015 and 2016 all-cases-mean values of 17 weeks are therefore chart read-offs or extrapolations; we flag them `CHART_READOFF` in `results.tsv` (R6). Re-fitting the champion model T02 on 2017–2024 only (n = 8) gives an in-sample MAE of 0.43 weeks and break-point coefficients stable within 0.5 weeks, so the headline trajectory is not sensitive to the two flagged points.

## 3. Detailed Trajectory (Descriptive, Not Causal)

The champion model is an interrupted time series with three structural break dummies:

```
W_year ≈ β0 + β1·(year − 2020) + β2·1[year ≥ 2018] + β3·1[year ≥ 2022] + β4·1[year ≥ 2023]
```

OLS on 2015–2024 (n = 10) gives in-sample MAE = 0.57 weeks. Leave-one-year-out (LOO) cross-validation (R1) gives MAE = 1.65 weeks — a 2.9× overfit ratio and still the lowest across all five families tested (T01 linear LOO = 5.10 weeks; T02a drop-2023-knot LOO = 5.15; T02b exhaustive-LASSO knots LOO = 2.91; T03 Little's-law LOO = 3.05). The three break years (2018, 2022, 2023) were chosen ex post from the narrative (Plean-IT IT-transition, Board-member crisis, backlog crystallisation respectively); the overfit ratio is exactly the price of that ex-post specification and is honestly the largest single methodological critique of the paper. The interrupted-time-series is best read as a *trajectory description*, not a structural model.

Approximate fitted coefficients:
- β0 ≈ 19 weeks (2020 intercept, after the first shock but before the second)
- β1 ≈ +0.2 weeks/year (slow secular drift)
- β2 ≈ +5 weeks (2018 Plean-IT IT-transition step-up)
- β3 ≈ +4 weeks (2022 Board-capacity step-up)
- β4 ≈ +15 weeks (2023 backlog-crystallisation step-up)

**Capacity-queueing summary (not a causal claim).** Using ABP Table 1 intake and disposal counts:
- 2022: intake 3,058 ÷ disposed 2,115 → ρ = 1.45 (95% CI 1.37–1.53)
- 2023: intake 3,272 ÷ disposed 3,284 → ρ = 1.00 (95% CI 0.95–1.05)
- 2024: intake 2,727 ÷ disposed 3,705 → ρ = 0.74 (95% CI 0.70–0.77)

ρ = intake ÷ disposed is an accounting identity for net-backlog change; Kingman-regime utilisation (Kingman 1961) predicts wait-time scales as ρ/(1−ρ) for a single-server queue in heavy traffic, but the data do not identify ρ as a causal *input* to decision time — intake, disposed and FTE are jointly endogenous to Board capacity, JR-lodgement pressure and case-mix composition. The 2024 ρ = 0.74 is consistent with, not a causal driver of, the 2025 recovery.

## 4. Methods

**Data.** ABP Annual Report Appendices 2018, 2020, 2021, 2022, 2023, and 2024 (the 2024 appendix is reused from the companion Judicial-Review project `ie_lrd_vs_shd_jr`). The 2018 full Annual Report provides the 2011–2017 narrative context and Figure 3 bar chart. The 2024 Q1–Q3 and 2025 Q1–Q3 Quarterly Planning Casework Statistics provide monthly compliance figures YTD. Every numerical cell in the derived `ANNUAL` dictionary in `analysis.py` is hand-verified against the raw text in the six appendix PDFs (`tests/test_parser.py`, 11 pytest tests, all passing; `E00.fingerprint` hash `9c839ce14726`). Case-level disposal-week data was *not* found in any of the public source text, which is why the SHD/LRD distributional analysis (R5) relies on aggregate mean plus a calibrated lognormal assumption.

**Tournament (Phase 1).** Five model families were fit to the year-level all-cases mean-weeks series:
- T01 — linear OLS on year
- T02 — interrupted time series with three dummies (the champion)
- T03 — Little's-law proxy W ≈ β0 + β1·(on-hand-start / intake)·52
- T04 — M/M/1 closed form W = 1/(μ − λ) with μ from realised disposals
- T05 — case-type × year fixed-effects panel

**Experiments (Phase 2 and 2.5).** 25 robustness experiments and 5 interaction experiments vary window, case-type filter, outlier handling and covariate inclusion. Every row is logged in `results.tsv`.

**Phase 2.75 revisions (this paper).** Ten reviewer-mandated follow-ups (R1–R10) executed in `phase_2_75_revisions.py`:
- R1 LOO-CV on T02 and four alternatives.
- R2 Bootstrap / analytic CIs on every headline figure.
- R3 Oaxaca–Blinder decomposition of 2018→2024, 2022→2023 and 2023→2024 changes into mix and productivity effects.
- R4 Monte Carlo sensitivity (5,000 draws) on Phase B scenario parameters.
- R5 Approximate case-cohort distributions (mean, median, interquartile range, 90th/99th percentiles) for SHD vs LRD.
- R6 Provenance audit on the pre-2018 rows.
- R7 M/M/1 re-specification with capacity-based μ = throughput-per-FTE × FTE.
- R8 Out-of-sample validation against 2025 Q1–Q3.
- R9 Re-phrase ρ-narrative from causal to arithmetic-consistent (writing-only).
- R10 Move "ACP mechanical compliance rise" claim to §Caveats as a forecast (writing-only).

**Phase B (forward scenarios).** A simplified closed-form analogue of M/M/1 with throughput = throughput-per-FTE × FTE, calibrated to 2024 (12.8 cases/FTE/year), base wait 14 weeks, service-rate inverse 6 weeks, and a SHD-share mix penalty. *This functional form is wholly unable to reproduce 2022 and 2023 in-sample W* (the Phase-B-form MAE against observed 2022–2024 is 100 weeks because the 2022 and 2023 ρ values push the prediction to the 180-week backstop); R7 confirms the projection is unmoored from the in-sample fit, which is why the §5.8 point estimates must be read with the R4 Monte Carlo bands.

## 5. Results

### 5.1 Headline trajectory (E00, R2)

Mean weeks and SOP compliance follow the baseline table of Section 2 with 95% CIs. The most striking features survive: a first step-up 2017→2018 from 18 to 23 weeks (CIs non-overlapping); a sharp second step-up 2022→2023 from 26 to 42 weeks; a flat crisis-level 2024. The 2018–2021 within-period variance (20–23 weeks) is small and CIs largely overlap, so the "first-break" story is better described as a one-time level shift than as a rising trend.

### 5.2 Tournament (T02, R1)

Interrupted time series with three knots wins with in-sample MAE = 0.57 weeks, LOO-CV MAE = 1.65 weeks (R1). The next-best LOO-CV family is the exhaustive-LASSO-knot variant T02b at MAE = 2.91 weeks. T02's LOO < 2.0× next-best — it is still champion, but by a narrower margin under cross-validation (1.65 vs 2.91, a 1.76× ratio) than the 7× in-sample gap initially suggested.

### 5.3 Capacity, backlog and utilisation (E10, E11, E12, E23, R3)

- ρ trajectory (R2 CIs): 1.45 (1.37–1.53) → 1.00 (0.95–1.05) → 0.74 (0.70–0.77). These CIs are narrow (n is >5,000 cases underlying each year's counts), so the three-value trajectory is statistically robust.
- Backlog-at-start-of-year co-moves most strongly with mean weeks: OLS slope +13.7 weeks per 1,000 cases of standing backlog (E12).
- FTE slope is weakly positive (+0.18 weeks per FTE, E10) because FTE growth *lagged* the crisis; this is an endogenous-response artefact, not evidence that hiring lengthens wait.
- **Oaxaca–Blinder decomposition (R3).** For 2018→2024, the decomposition attributes +17.1 weeks (~100%) to within-case-type productivity change and −0.55 weeks (~−3%) to case-type mix shift, with a +0.56-week interaction residual. The same decomposition for 2022→2023 attributes +18.6 weeks to productivity and ~0 to mix. **Mix is not the story; within-case-type cycle-time is.** This validates using ρ as an operative descriptive summary, but does not identify *which* within-type mechanism is doing the work.

### 5.4 Case-type heterogeneity (E02, E03, E14, E15, R5)

Mean weeks by type, 2024 Appendix Table 2:
- NPA: 41 weeks
- SID: 53 weeks
- SHD: 124 weeks (95% CI 85.6–162.4 with n = 40)
- OTHER: 39 weeks

R5 reconstructs approximate distributions under a lognormal assumption with mean matched to each cohort:

| Cohort | n | Mean | Median (est.) | IQR (est.) | p90 (est.) |
|---|---|---|---|---|---|
| SHD 2024 | 40 | 124 | ~79 | 42–151 | ~267 |
| SHD 2023 | ~60 | 59 | ~42 | 24–73 | ~122 |
| LRD (15-mo) | 69 | 13 | ~12 | 9–16 | ~20 |
| NPA 2024 | 2,277 | 41 | ~34 | 22–51 | ~75 |
| OTHER 2024 | ~600 | 39 | ~30 | 19–49 | ~75 |

**Caveat on R5.** Per-case decision-date data is not present in the source appendices; distributions are inferred from the aggregate mean plus an assumed coefficient of variation (cv = 1.2 for SHD, 0.4 for LRD, calibrated from narrative descriptions of tail severity). The headline SHD-vs-LRD mean contrast (124 vs 13) survives as a median-vs-median contrast (~79 vs ~12) but the precision on SHD is highly uncertain; the 2024 SHD cohort is small (n = 40) and, per the reviewer, consists largely of the residual-tail of a 2017–2021 legislative regime that ended in 2021, so the "124 weeks" headline is best described as *a 2024-disposal-cohort-of-long-tail-SHD-cases* mean, not a generic "how long does SHD take now" number. The LRD 13-week figure is computed over a 15-month window (Jan-24 to Mar-25), *not* a 12-month year; R5 reports an estimated 2024-calendar-year-only LRD cohort at mean ~13 and median ~12 weeks.

### 5.5 Judicial review as a covariate (E20, R9)

JR-lodgement rates differ by three orders of magnitude across case types: SHD 33%, LRD 36%, NPA 0.3%. The composite JR-lodgement rate moved roughly in lockstep with ABP decision time 2018–2024. **With n = 10 annual observations we cannot separate the JR-feedback channel from the capacity-queueing channel.** The aggregate-year data is uninformative about whether high-JR-risk case types are slow because drafting must anticipate challenge (JR-feedback channel) or because complex cases are both slow *and* attract JR (correlated-confounder). R9 accordingly reworded §3, §5.3 and §5.5 from "ρ explains X" to "ρ is consistent with X" throughout.

### 5.6 Planning and Environment List null (E09)

The P&E List was established November 2022 to reduce JR-disposal time at the Courts Service. Its effect on ABP mean weeks is null at the 2024 horizon: mean weeks are 42 in both 2023 and 2024, two weeks *worse* than the 2022 figure of 26. The P&E List reduced JR-remittal delay but not the underlying reason-giving or Board-capacity channels that drove ABP decision time.

### 5.7 Interaction effects (INT01–INT05)

- INT02: SHD mean rose +54 weeks post-crisis (2022–2024 avg) vs NPA +19 weeks — SHD cases were the most crisis-sensitive (confounded with the SHD-cohort tail-clearing effect in 5.4).
- INT03: FTE growth in 2023 produced no 2023 SOP-compliance improvement; the compliance gain appears only in 2025 Q1–Q3 once the backlog started contracting.
- INT04: the three-point ρ trajectory (1.45 → 1.00 → 0.74) tracks SOP recovery (45 → 28 → 25 → 58 YTD) monotonically, consistent with a queueing-regime description.

### 5.8 Phase B forward scenarios — Monte Carlo sensitivity (R4)

The point-estimate scenarios are:

| Scenario | 2028 W (wk, median) | 90% CI W | 2028 SOP (%, median) | 90% CI SOP |
|---|---|---|---|---|
| S1 status quo (290 FTE, 2,727 intake) | 42 | 25–180 | 15 | 0–60 |
| S2 +20% FTE (348 FTE) | 29 | 20–48 | 48 | 8–71 |
| S3 PDA-2024 effective (+10% intake) | 33 | 22–72 | 36 | 0–67 |

Monte Carlo parameter priors (5,000 draws): throughput-per-FTE ~ U[10, 13.5], base wait ~ U[12, 17], inverse-service-rate ~ U[3, 10], SHD-share initial ~ U[0.01, 0.10], SHD decay ~ U[0.6, 0.95] (S1, S2) or U[0.5, 0.85] (S3), intake ~ Normal(μ, 250).

**All three scenarios have 60+ percentage-point SOP CIs, so the point estimates are directionally indicative, not quantitatively precise.** In 22.6% of draws S1 (status quo) beats S3 (PDA-2024 effective) — the scenario ranking is *not* robust. The only finding that survives is qualitative: the status-quo parametrisation keeps SOP well below the pre-2018 regime across the MC distribution.

### 5.9 Phase B form does not validate in-sample (R7)

The Phase B functional form was evaluated against 2022–2024 observed W. Because 2022 and 2023 ρ are ≥ 1 under the capacity parametrisation (intake 3,058 / (12.8 × 202) = 1.19, intake 3,272 / (12.8 × 250) = 1.02), the formula diverges to its 180-week backstop for those years. In-sample MAE = 100 weeks. **The projection model is not anchored to the observed series; the §5.8 numbers should be read as scenario bookkeeping, not forecasts.**

### 5.10 2025 out-of-sample validation (R8)

Using the Phase B status-quo parametrisation with 2025 actual intake (annualised from Q1 = 2,380 per year; Q3 YTD annualised = 2,871 per year) and FTE = 290:
- Q1-end SOP predicted 52.6%, observed 47% (error ~6pp)
- Q3-end SOP predicted 25.6%, observed 77% (error ~51pp)

OOS MAE = 28.5pp. The Phase B form systematically **under**-predicts 2025 Q3 recovery, because actual disposals per FTE accelerated substantially above the 12.8 calibration as the Board-member cohort stabilised. The 2025 Q3 observation is consistent with throughput-per-FTE ~ 18 cases/FTE/year, outside the U[10, 13.5] prior used in R4. **The model's CI does not cover the 2025 Q3 observation.** This is a failure mode that the paper must disclose plainly rather than paper over.

## 6. Discussion

The 2022–2023 ABP decision-time deterioration admits a simple capacity-queueing *description*: intake outpaced disposal in 2022 (ρ = 1.45), a 2,580-case backlog carried into 2023, and mean weeks spiked. The 2024 ρ fell to 0.74 and the 2025 Q1–Q3 monthly compliance series rose monotonically from 37% to 77%, consistent with a queue draining once service capacity exceeded arrival. The ρ arithmetic is an accounting identity, not a mechanism — we cannot with n = 10 annual observations separate (a) disposals fell because Board-member seats were empty, from (b) disposals fell because *Connelly/Balz* reason-giving expanded inspector-report length, from (c) disposals fell because 2020–2021 intake was a difficult composition (SID/SHD-heavy). The Oaxaca–Blinder decomposition (R3) rules out (c) as the dominant channel — mix shift contributed ~0 to the 2018→2024 rise — but (a) and (b) remain jointly confounded at the aggregate level.

Four caveats bound the analysis. They are itemised in §8.

## 7. Conclusion

ABP decision-times deteriorated sharply in 2022–2023, in a pattern consistent with a capacity-squeeze queueing description. The observed recovery signal in 2025 Q1–Q3 monthly compliance (37% → 77%) is real; the forward projection of that recovery to 2028 is highly sensitive to assumptions (60–67pp SOP CIs under R4) and the scenario ranking (S1 < S3 < S2) is not robust to parameter uncertainty. ρ = intake/disposed is an arithmetically compact summary of the trajectory but not a causal identifier. The return to a pre-2018 70–80% compliance regime by 2028 is supported by none of the three scenarios' median point estimates.

## 8. Caveats and Limitations

1. **Aggregate-year data.** All substantive results rest on n = 10 annual observations. A case-level panel would identify the JR-feedback, Board-capacity and complexity channels separately.
2. **SOP is not binding.** SOP-compliance measures a political target, not a legal deadline; incentive structures differ from binding-deadline agencies.
3. **ACP transition uncertainty.** The June 2025 transition to An Coimisiún Pleanála is too recent for any substantive effect attribution. Under the new PDA-2024 statutory timelines (48 weeks for SIDs, 26 weeks for Local-Authority projects, 48 weeks for Section 37B applications) the headline SOP compliance figure will **mechanically** rise as the denominator case-mix shifts toward categories with longer SOPs, partly independent of any change in agency throughput. This is a forecast, not an observation; the pre-ACP baseline cannot measure it (moved from Abstract and §6 per R10).
4. **T02 is an ex-post-specified descriptive fit, not a structural model.** Break years (2018, 2022, 2023) were chosen from the narrative; LOO-CV overfit ratio 2.9× is the honest price of that choice.
5. **Phase B projections are unmoored from in-sample fit (R7).** The functional form cannot reproduce 2022 or 2023 observed W (diverges to backstop) and mispredicts 2025 Q3 by ~51 percentage points (R8). 2028 scenarios are reported as directional sensitivity bands, not forecasts.
6. **Scenario ranking is not robust (R4).** In 22.6% of Monte Carlo draws the status-quo S1 outperforms the PDA-2024-effective S3.
7. **2015 and 2016 baseline figures are chart read-offs (R6).** All-cases mean-weeks values of 17 for those two years are not documented in any tabular source; flagged `CHART_READOFF` in `results.tsv`.
8. **SHD 124-week 2024 figure is a small-n (n = 40) residual-tail cohort.** The headline mean overstates generic "SHD-like duration" because the cohort consists of 2017–2021-legislative-regime residuals; median is ~79 weeks under the lognormal approximation. No case-level data is available in the source text.
9. **LRD 13-week figure is over a 15-month window, not 12 months.** The 2024-only restriction (R5) gives a very similar mean and median (~13 and ~12 weeks respectively).
10. **ρ is an outcome, not an input.** ρ = intake/disposed; both numerator and denominator are endogenous to Board capacity, JR pressure, and mix. "ρ is consistent with the observed trajectory" is the strongest statement the aggregate data supports (R9).
11. **JR-channel vs capacity-channel not identifiable.** JR-lodgement rate is correlated with mean weeks at the year level, but confounded with case complexity and backlog at n = 10.

## 9. Change Log (R1–R10)

| Mandate | Finding | Paper edit |
|---|---|---|
| **R1** LOO-CV on T02 | in-sample MAE 0.57 → LOO 1.65 wk; T02 still champion (1.76× next-best, LASSO-knot T02b 2.91) but overfit ratio 2.9× disclosed | §3 disclosed overfit ratio; Abstract quotes LOO alongside in-sample; Caveat 4 |
| **R2** Bootstrap CIs | 29 quantities with 95% CIs in `discoveries/headline_cis.csv`; mean-weeks Gaussian, SOP% Wilson, ρ delta-method, 2025 trend-plus-noise for YTD | §2 table adds CI columns; Abstract quotes CIs for every headline number; §5.3 ρ with CIs |
| **R3** Oaxaca–Blinder | mix-effect ≈ −3% of 2018→2024 rise; productivity within-type dominates | §5.3 new decomposition paragraph; ρ framed as within-type-productivity summary |
| **R4** Phase B Monte Carlo | 90% SOP CIs span 60–67pp per scenario; S1 beats S3 in 22.6% of draws | §5.8 replaced point estimates with median ± 90% CI; explicit "directionally indicative, not quantitatively precise"; Caveat 6 |
| **R5** SHD vs LRD distributions | SHD 2024 median ~79 wk (mean 124); LRD median ~12 (mean 13); case-level data unavailable, lognormal approximation used | §5.4 reports median + IQR + p90; contrast re-stated on medians |
| **R6** Pre-2018 provenance | 2015, 2016 all-cases mean-weeks are chart read-offs; T02 refit on 2017-2024 MAE = 0.43, coefficients stable | §2 provenance column; rows flagged; Caveat 7 |
| **R7** Capacity-based μ M/M/1 | Phase B form MAE = 100 wk in-sample (diverges to backstop for 2022 and 2023 due to ρ ≥ 1) | §5.9 new subsection; Caveat 5 |
| **R8** 2025 OOS validation | Q1 pred 52.6 vs obs 47 (6pp error); Q3 pred 25.6 vs obs 77 (51pp error); Phase B underpredicts recovery | §5.10 new subsection; explicit OOS disclosure; Caveat 5 |
| **R9** Causation→correlation | ρ reframed as accounting identity; "ρ explains" → "ρ is consistent with"; endogeneity of intake and disposed stated | §3 and §5.3 reworded throughout; §6 added explicit identification caveat; Caveats 10–11 |
| **R10** ACP mechanical rise | moved from Abstract and §6.3 to §8 Caveat 3; labelled "forecast, not observation" | Abstract silent on mechanical-rise claim; Caveat 3 |

## References

Selected citations from `papers.csv` (full bibliography of 210 entries is in the project directory):

- P001 Kleinrock, L. (1975). *Queueing Systems, Volume 1: Theory*. Wiley.
- P002 Little, J. D. C. (1961). A proof for the queueing formula L = λW. *Operations Research* 9(3).
- P003 Parkinson, C. N. (1957). *Parkinson's Law*. John Murray.
- P011 Simons, G. (2019). *Planning and Development Law* (3rd ed.). Round Hall.
- P015–P021 An Bord Pleanála Annual Reports 2018–2024.
- P022–P027 ABP / ACP Quarterly Planning Casework Statistics 2024–2025.
- P028 Planning and Development Act 2024 (No. 34 of 2024).
- P034 *Heather Hill Management Company v An Bord Pleanála* [2022] IESC 43.
- P039 *Balz v An Bord Pleanála* [2019] IESC 91.
- P040 *Connelly v An Bord Pleanála* [2018] IESC 31.
- P041 Courts Service Practice Direction HC101 (Planning and Environment List, November 2022).
- P048 Oaxaca, R. (1973). Male-female wage differentials in urban labor markets. *International Economic Review* 14(3).
- P049 Blinder, A. S. (1973). Wage discrimination: reduced form and structural estimates. *Journal of Human Resources* 8(4).
- P052 Indecon (2022). *Organisational Capacity Review of An Bord Pleanála*.
- P053 O'Broin, K. (2023). Why is An Bord Pleanála taking so long? *Irish Times*, 12 October 2023.
- P057 Farrell, R. (2022). *Preliminary Report on Governance at An Bord Pleanála*.
- P065 Kingman, J. F. C. (1961). The single server queue in heavy traffic. *Proceedings of the Cambridge Philosophical Society* 57(4).
- P072 Wilson, J. Q. (1989). *Bureaucracy: What Government Agencies Do and Why They Do It*. Basic Books.
- P093 Halliday, S. (2004). *Judicial Review and Compliance with Administrative Law*. Hart Publishing.
