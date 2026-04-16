# Phase 2.75 Blind Review — ABP Decision Times Paper

**Reviewer:** Independent (fresh read, no prior context)
**Project:** `/home/col/generalized_hdr_autoresearch/applications/ie_abp_decision_times/`
**Paper version reviewed:** `paper_draft.md` (as of 2026-04-16), `results.tsv` (47 rows), `tournament_results.csv` (5 rows)
**Research question:** Has ABP decision-time deteriorated 2018-2025 with rising case volumes and JR pressure, under a queueing-theoretic frame?

---

## Decision: **MAJOR REVISION REQUIRED**

The project has a solid empirical core — the headline 2018–2024 compliance collapse is real, hand-verified against the Annual Report Appendices, and reproducibly parsed. The TDD discipline in `tests/test_parser.py` (11 tests passing) is exemplary.

But several load-bearing claims in the paper are under-identified, over-fit, or rest on chart-reads and single-point calibrations that are not honestly disclosed. Specifically:

1. **T02 is textbook over-fit.** 5 parameters on 10 observations with break-points chosen ex post from the narrative. MAE = 0.57 weeks is an in-sample fit statistic of limited interpretive value. No cross-validation exists.
2. **The queueing-theoretic "solution" is correlational.** ρ = intake / throughput is arithmetically equivalent to "did the queue grow?". Invoking Kingman (ρ → 1) to explain a 3-year window when ρ was only ever observed to cross 1 once (in 2022) and the paper simultaneously admits ρ = 0.74 in 2024 did NOT immediately restore compliance is internally inconsistent — the mechanism is claimed to be dominant yet demonstrably doesn't predict the 2024 persistence.
3. **Pre-2018 data is chart-read-off.** The 2015/2016/2017 all-cases mean-weeks figures (17, 17, 18) are NOT in any table I could locate in `ar_2018.txt`; the 2018 AR only provides Normal-Planning-Appeals figures (15, 16, 17 weeks for 2015–2017) and all-cases 18 weeks for 2017 in a single text sentence. The 2015/2016 all-cases means are unsourced. This is material because those three points are used to claim a "stable 17-18 week" pre-crisis regime.
4. **SHD 124 weeks vs LRD 13 weeks is a mean-vs-mean comparison.** The 124-week SHD 2024 figure is a small-n residual-tail mean — the 2024 SHD disposals are literally the dregs of a 2017-2021 regime that ended. A median or full distribution is required before using this as a causal contrast.
5. **Phase B scenarios have zero parameter uncertainty.** `throughput_per_fte = 12.8 cases/FTE/year` is a single-point 2024 calibration. The three scenarios differ by a handful of point assumptions; the ±15% bands in the CSV are not derived from anything.
6. **Case-mix is never decomposed from productivity.** The paper asserts Kingman-ρ drives the trajectory but never does the obvious mix-vs-productivity accounting decomposition: how much of the 2022→2024 rise in mean weeks is (case-mix shift × fixed within-type cycle time) vs (within-type cycle time change)?
7. **The "58% YTD 2025 with bootstrap CI 49–68%" (E24) treats the nine 2025 monthly figures as iid.** They are transparently trending (37 → 77) — a Q1–Q3 growth curve. The CI is meaningless; the resampling violates iid by construction.

None of these issues invalidate the broad thesis (ABP was in a queueing crisis and is recovering). But they are sufficient to force a major revision of Sections 3, 4, 5.2, 5.8 and 6.

---

## Mandated experiments

### R1. Leave-one-year-out cross-validation of T02

**Motivation.** With 5 parameters fit to 10 observations, T02's MAE = 0.57 weeks is in-sample. T01 (linear year) has MAE = 3.99 on the same 10 points — a 7× ratio, but T02 adds 3 degrees of freedom chosen from the narrative (2018, 2022, 2023 are the exact years of the three largest jumps). LOO-CV will reveal whether the gap closes.

**Spec.**
- For each year y ∈ {2015, ..., 2024}: refit T01, T02, and T03 on the other 9 years, predict y, record absolute error.
- Report LOO-CV MAE for each family and the ratio LOO_MAE / in_sample_MAE (an over-fitting index).
- Additional variants of T02: (a) drop the 2023 knot (nested model T02a); (b) replace hand-picked knots with a LASSO dummy-selection over all possible break years 2016–2024 (T02b); (c) Bayesian piecewise-linear with exponential prior on number of knots.
- **Accept criterion.** T02 is champion ⇔ T02 LOO-CV MAE is still <2× the next-best family. If not, the paper cannot claim T02 as "the model".
- **Output.** `discoveries/loocv_tournament.csv` with columns `(model, left_out_year, pred, obs, abs_err)`.

### R2. Bootstrap CIs on every headline week / percentage figure

**Motivation.** The paper quotes 42 weeks (2023, 2024), 124 weeks (SHD 2024), 13 weeks (LRD), 58% (2025 YTD) without CIs. For aggregate-year data without case-level counts these have to be approximated, but they MUST be approximated. Taking a point estimate from the Appendix and treating it as exact is the single most correctable defect.

**Spec.**
- For quantities reported from a case count N per year/type (SHD 2024: 40 cases disposed; LRD: 69 cases Jan-24 to Mar-25; etc.), construct a Poisson-normal approximation CI on the mean: CI = mean ± 1.96 × σ̂ / √N, where σ̂ is approximated as (mean × cv), cv = 1.0 for SHD (right-skewed), cv = 0.4 for LRD (narrower).
- For SOP% report Wilson binomial CI with N = annual-disposed-count from `INTAKE[y]["disposed"]`.
- For the 2025 Q1-Q3 "YTD 58%" replace the iid monthly bootstrap (E24) with a proper trend-plus-noise model: fit SOP_month = α + β·month + ε, and report (a) the Jan-Sep mean with its corresponding standard error from the regression, (b) the end-of-Sep level (77%) with its own CI, (c) a separate forecast CI for the Q4 YTD figure.
- **Accept criterion.** Every headline number in the abstract, §2 table, and §5 results tables must appear in the revised paper with a 95% CI. Point estimates without CIs are reviewer-rejected.
- **Output.** `discoveries/headline_cis.csv`.

### R3. Pure case-mix decomposition (Oaxaca-Blinder-style)

**Motivation.** If 2022→2024 disposed-case-mix shifted toward slow case types (SHD long-tail clearing), the mean weeks could rise even if every case type's within-type cycle time was flat. The paper asserts the trajectory is ρ-driven but never separates the two channels.

**Spec.**
- Let W̄ᵧ = Σₜ sₜᵧ × Wₜᵧ where sₜᵧ is the share of disposals in year y that are type t, Wₜᵧ is the mean weeks for type t in year y.
- Decompose (W̄₂₀₂₄ - W̄₂₀₁₈) = Σₜ sₜ,₂₀₁₈ × (Wₜ,₂₀₂₄ - Wₜ,₂₀₁₈)  [**productivity effect**, holding mix constant]
                              + Σₜ Wₜ,₂₀₁₈ × (sₜ,₂₀₂₄ - sₜ,₂₀₁₈)  [**mix effect**, holding productivity constant]
                              + interaction.
- Report the same decomposition for 2017→2022, 2022→2023, 2023→2024.
- Requires reconstructing disposed-count shares by type from Appendix Table 1 "Disposed of Formally" subtotals (available in `abp_2024.txt`, `appendix_2023.txt`, `appendix_2022.txt`).
- **Accept criterion.** If the mix-effect term exceeds ~30% of the 2022→2024 rise, the paper must retitle Section 5.3 and reframe the queueing mechanism as **one** of two drivers, not "the" driver.
- **Output.** `discoveries/mix_productivity_decomposition.csv` with columns `(period, type, share_effect, productivity_effect, interaction)`.

### R4. Phase B sensitivity / Monte Carlo on scenario parameters

**Motivation.** `throughput_per_fte = 12.8 cases/FTE/year` is the 2024 point estimate. 2023 would give 3284/250 = 13.1, 2022 would give 2115/202 = 10.5 — a 25% range even with identical FTE definition. `base = 14.0`, `sr = 6.0`, `mix_shd_share = 0.05` in `phase_b_discovery.py` are all hand-calibrated single numbers. The scenario outputs `38%`, `60%`, `53%` pretend these are precise.

**Spec.**
- Treat each Phase B parameter as a uniform prior over a plausible range:
  - `throughput_per_fte` ~ U[10.0, 13.5] (from 2022, 2023, 2024 observed values)
  - `base` ~ U[12, 17] (LRD-like steady-state cycle times)
  - `sr` ~ U[3, 10] (service-rate inverse — very loosely constrained)
  - `mix_shd_share` ~ U[0.01, 0.10]  (SHD tail clearing; the 0.8**t decay assumption is also a free parameter — test U[0.6, 0.95])
  - Intake volatility: intake ~ Normal(2727, 250) (based on 2019-2024 s.d.)
- Run 5000 Monte Carlo draws per scenario and report: median, 5th, 95th percentiles of 2028 W and SOP% per scenario.
- Also report: fraction of draws in which S1 (status quo) beats S3 (PDA-2024). If this fraction is non-trivial (>15%), the scenario ranking is not robust.
- **Accept criterion.** Paper §5.8 table must be replaced with median ± 90% CI per scenario. Any scenario whose 90% CI for SOP% spans more than 30pp should be described as "directionally indicative, not quantitatively precise."
- **Output.** `discoveries/phase_b_mc.csv`.

### R5. Median (or full distribution) for SHD vs LRD and for the SOP

**Motivation.** SHD 2024 mean = 124 weeks is computed over a specific cohort: 2024 formally-disposed SHD cases. The 2024 Appendix says 40 SHD cases were disposed (Granted 6, Refused 20, Split 2, Discharged 4, Withdrawn 8; ref abp_2024.txt lines 177-208). Of these, 8 withdrawals and 4 discharges-pending-decision may have very different cycle times than the contested 20 refusals. And the paper's LRD 13-week figure is computed over a 15-month window (Jan-2024 to Mar-2025), not a 12-month year. These are not directly comparable.

**Spec.**
- Extract from the appendices the case-level disposal-week distributions for SHD and LRD where available (2023 SHD appendix §8; 2024 SHD appendix §8; 2024 LRD §8 in abp_2024.txt). These appendices list each case with its decision date and its receipt date; weeks-to-dispose can be computed per case.
- For each case type and year, report: n, mean, median, 25th, 75th, 90th, 99th percentiles.
- Specifically reconstruct the SHD 2024 mean from per-case durations to confirm 124 weeks, and report what the median is. If the median is <60 weeks, the paper's "SHD is a long-tail" claim is supported but the 124-week mean must be annotated as extreme-skew.
- For LRD, restrict to 2024 calendar year only (not Jan-24 to Mar-25).
- **Accept criterion.** §5.4 and abstract must use median(or, if case-level data is unavailable, a clearly labelled subset-of-disposals) instead of or alongside mean. The headline SHD-vs-LRD contrast must survive on medians or be retracted.
- **Output.** `discoveries/shd_lrd_distributions.csv`.

### R6. Provenance audit on 2015–2017 all-cases mean weeks

**Motivation.** The ANNUAL dict sets `2015: (15, 27, None, 30, 17, 75)`, `2016: (16, 50, None, 26, 17, 63)`, `2017: (17, 22, None, 30, 18, 64)`. The 2018 AR clearly supplies Normal-Planning-Appeals means (15, 16, 17) and a single all-cases figure (18 weeks for 2017 in narrative prose). But the 2015 and 2016 all-cases means of "17" are not documented in any table I could locate. The SOP percentages 75/63/64 come from the Figure 3 bar chart — a read-off.

**Spec.**
- Locate the primary source for 2015, 2016 all-cases mean-weeks figures. Candidates: ABP Annual Report 2015; ABP Annual Report 2016; ABP Annual Report 2017. If these PDFs are obtainable from pleanala.ie or web.archive.org, download them.
- Add explicit unit tests: `test_2015_mean_weeks_all_cases_in_source(...)` etc.
- If the real source is an ABP chart without a tabular companion, mark those rows PROVENANCE=CHART_READOFF in `results.tsv` and remove them from the T02 fit (refitting on 2017-2024, n=8).
- Report whether removing 2015/2016 changes T02's break-point coefficients or the ordering of the tournament.
- **Accept criterion.** Every E00 row must have an auditable source. If not, it's removed.

### R7. T04 M/M/1 re-specification with time-varying μ (not capped at 260)

**Motivation.** The paper's tournament shows T04 M/M/1 with MAE = 135 weeks — a catastrophic failure — because `disposed/52` is used as μ in crisis years when disposed < intake (ρ > 1 ⇒ W formally ∞, capped at 260). This "losing" model is then strategically avoided in Phase B, where a mutated M/M/1-ish functional form (base + sr·ρ/(1-ρ) + mix·share) is used instead.

**Spec.**
- Refit T04 with μ = `capacity_per_fte × FTE[y]` instead of `disposed[y]/52`. This decouples service-rate from realized disposal and is the correct queueing-theoretic specification (μ = service capacity, not realized service).
- Report the new T04 MAE.
- Compare the refit T04 to the Phase B `predicted_W` formula — they should be the same functional form. If T04 MAE is much worse than T02 after this fix, the paper must disclose that the Phase B projection model does not validate against the observed series.
- **Accept criterion.** The Phase B model must reproduce in-sample the 2019-2024 observed W with MAE < 5 weeks (the Kingman regime is a rough approximation; this is generous). If it cannot, the §5.8 projection is unmoored.

### R8. Out-of-sample validation against 2025 Q1-Q3 monthly data

**Motivation.** The 2025 monthly series (9 points, 37% → 77%) is quietly held out of every model fit but is then used rhetorically as "the recovery is already visible." This is the natural out-of-sample test and the paper doesn't do it.

**Spec.**
- Use each Phase B model (S1 status-quo parametrisation) to predict 2025 Q1, Q2, Q3 SOP% (or W).
- The inputs for 2025 Q1-Q3 are: intake = 595 (Q1) and 2153 YTD Q3, disposed = 800 (Q1) and 2296 YTD Q3, FTE ~ 290. The observed SOP% is 41% (Q1 YTD), 61% (Q2 approx), 73% (Q3 approx).
- Report model-predicted vs observed for each quarter, MAE, and whether the model's CI (from R4) covers the observation.
- If the model over/under-predicts 2025 systematically, disclose the direction and magnitude in §6.
- **Accept criterion.** The paper must report one 2025-out-of-sample MAE number in §5.8 or §6, alongside its in-sample MAE.

### R9. Honest framing on causation vs correlation (no new experiment, a writing change)

**Motivation.** The abstract says "ρ = 1.45 → 1.00 → 0.74 ... is sufficient without invoking direct judicial-review feedback." Phrased this way, the paper is claiming a negative causal result (JR feedback is not needed). But ρ = intake/disposed is an accounting identity: of course a queue that absorbed more than it dispatched grew. Nothing about this proves *why* disposed was low in 2022. The paper needs:

**Spec.** Rewrite §3, §5.3, §5.5, §6 to:
- Replace every statement of the form "ρ explains X" with "ρ is consistent with X", "ρ is arithmetically equivalent to backlog dynamics", etc.
- Acknowledge that ρ is an outcome variable — both intake AND disposed are endogenous to capacity, board-member count, JR pressure, etc.
- Explicitly state that the aggregate-year data cannot separate (a) "disposed fell because board was short" from (b) "disposed fell because JR made inspector-reports longer" from (c) "disposed fell because intake was a difficult composition".
- Downgrade §7's "board-member and judicial-review pressure are secondary drivers at the aggregate level" — this is a claim about effect sizes that the data cannot support with n=10 years.

### R10. Drop or restructure the June-2025 ACP claim

**Motivation.** The abstract notes "the June 2025 transition to An Coimisiún Pleanála (ACP) is too recent for hard evidence," but §6.3 proceeds to claim "the new statutory timelines under PDA-2024 ... are structurally lax ... the statutory-compliance headline figure will mechanically rise as case mix shifts toward cases with longer SOPs." This is a forecast, not an observation. The data pipeline ends before ACP commenced (18 June 2025), and the Q3 2025 figures are still under ABP governance in practice.

**Spec.**
- Remove the "mechanical rise" claim from the abstract.
- Keep it in §6 as a caveat: "If ACP case mix shifts ... the headline SOP% will rise partly for mechanical definitional reasons." Move it from §6.3 to §8 (Limitations) if §8 exists, or to a new caveats sub-section.

---

## Items that DO work well

- The tests/test_parser.py discipline and the ANNUAL dict hash fingerprint (E00.fingerprint) are best practice for a data-dependent analysis paper. Keep.
- The 2018, 2019, 2020, 2021, 2022, 2023, 2024 Appendix Table 2 figures in ANNUAL match the raw text exactly (I verified 2023 and 2024 against source).
- The intake/disposed figures for 2019-2024 in INTAKE match abp_2024.txt Figure 1.
- The tournament framing (T01-T05) is methodologically standard; reporting all five MAEs with their n is honest.
- The ρ = 1.45 → 1.00 → 0.74 trajectory is a real and striking finding. The criticism is about how much of the variance it explains, not whether it exists.
- The LRD 13-week / 100% compliance rebuttal to the "housing cases are slow" press narrative (E15) is original and supported.
- The Indecon and Farrell report citations, and the board-member timeline, are solid qualitative evidence.

---

## Nice-to-have (not mandated)

- **E17 (same-inspector continuity):** marked PARTIAL. If case-level appendix tables (13A, 13B) can be parsed, an inspector-level fixed-effect is highly informative. Not blocking the paper, but worth the try.
- **INT03 phase diagram:** the narrative "FTE+48 gave compliance −3pp in 2023; gains only in 2025" is evocative but the scatter of 3 points proves nothing. Either drop the phase-diagram language or add a formal lagged-FTE regression on quarterly data.
- **External comparator:** UK PINS (26 weeks) and NL Raad van State (40 weeks) are cited once in the lit review but never used as benchmarks in §5. A single row "ABP 2024 mean = 42 weeks vs international 26-40 weeks" would anchor the claim that this is a crisis, not a baseline.

---

## Summary scoring

| Dimension | Current | After R1-R10 |
|---|---|---|
| Data quality | B+ (verified Appendix extractions, but 2015-2017 shaky) | A (after R6) |
| Identification strategy | C (correlation framed as causation) | B (after R3, R9) |
| Uncertainty quantification | D (no CIs on headline numbers) | B+ (after R2, R4) |
| Out-of-sample validation | F (no LOO-CV, 2025 held out rhetorically) | B (after R1, R8) |
| Reproducibility | A− (tests pass, hash-fingerprinted) | A |
| Narrative discipline | C (over-claims on ρ mechanism) | B+ (after R9, R10) |

Recommend **major revision**. Not a reject — the empirical foundation is sound and the question is important. But the current draft asks the reader to trust more than the n=10 annual data can bear.

---

*Reviewer note: I was unable to obtain separate 2015 or 2016 Annual Report PDFs in the workspace, so R6 may require a web fetch. I also did not re-run `python phase2_experiments.py` as part of this review; all critique is based on code reading and raw-text spot-checks.*
