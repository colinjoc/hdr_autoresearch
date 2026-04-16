# Phase 2.75 Blind Review — `ie_commencement_notices`

**Reviewer role:** independent, blind. No participation in Phase 0–2.5.
**Artifacts inspected:** `paper_draft.md`, `results.tsv`, `tournament_results.csv`, `analysis.py`, `phase_b_discovery.py`, `tests/test_cohort_durations.py`, `literature_review.md`, `data/raw/bcms_notices.csv` (spot-checks via `data/cohort_cache.parquet`), `discoveries/optimal_la_scheme_recommendations.csv`.
**Reviewer-side computation:** spot-checks on the cached cohort parquet (Pearson/Spearman of LA CCC-filing rate vs Phase B ranking, opt-out share breakdown by dwelling type, composition check on AHB vs private cohorts, concordance noise floor).

---

## 1. Decision

**Major revisions.**

The cohort framing, headline durations (232 / 498 / 962 d), tournament mechanics, and the placebo construction (E25) are defensible and the lit review (lit_review.md) is genuinely substantive and shapes the stratification choices. However, **two structural issues prevent acceptance as drafted:**

1. The Phase B "high-delivery LA" ranking (§5.8) is materially confounded with CCC-filing-rate heterogeneity (§5.4 / E26). Reviewer-side check on the cached cohort found Pearson r = 0.53 and Spearman ρ = 0.57 between LA-level CCC-filing rate and the Phase B weighted p_complete_48m for dwelling schemes (>1 unit). The paper flags the channel problem qualitatively but continues to name-rank counties ("Fingal, South Dublin, Dublin City, Wicklow … are the delivery workhorses") in §5.8 and the conclusion — language that is not defensible until a channel-adjusted ranking is published.
2. Several headline deltas (AHB +46 d, Dublin apartment intra-gap +154 d, multi-phase +288 d) are reported as stand-alone effects without composition controls. Reviewer-side check shows AHB schemes have a 28-unit median vs 1-unit private median and materially different type mix — a site-complexity / scheme-size confound the paper itself anticipates but never adjusts for.

The champion-selection footnote (§6.4) is already honest about the Weibull-vs-LogNormal concordance gap being within the noise floor; that issue is acknowledged and not a blocker.

Minor-revision-only issues are listed at the end (§5 of this review). The mandated experiments below (R1–R9) are required before this paper is acceptable.

---

## 2. Reproducibility spot-checks (what I verified)

- `cohort_for_perm_to_comm` median on `event==1, duration>0, duration<365*12` reproduces E00 = 232 d.
- `cohort_for_comm_to_ccc` produces N for I01 cells that sum to the claimed 4,481 apartment events (2,810 non-Dublin + 1,671 Dublin). This is fine.
- E25 placebo (LA-label-shuffled CV = 0.020 vs observed 0.272) is a clean and legitimate test of sampling-noise-vs-signal; worth highlighting more in the paper.
- E26 CCC-filing-rate CV = 0.47 reproduces. Excluding opt-out commencements, the CV is still 0.29 (reviewer computation), so the channel variance is not purely a one-off-self-build artefact — it survives the obvious filter.
- One-off dwellings (n=88,413 commenced) are 67% opt-out and have a 7.6% CCC rate; multi-unit dwellings are 0.3% opt-out with an 81% CCC rate. This composition is not mentioned in the results section and is the single largest driver of the "bottom 15 cells are one-off dwellings in slow-filing counties" finding.

---

## 3. Strengths

- The five-question framing (a)–(e) is well-posed.
- The cohort construction (three cohorts: perm→comm, comm→CCC, complete-timeline) is a genuine methodological upgrade over the predecessor aggregate cross-correlation baseline, and the §2.1 description of the baseline is mathematically rigorous.
- Lit review spans four themes and is clearly shaping the experiment choices (real-options → E11, E23; Bromilow/Flyvbjerg → E04; regime-shift literature → E07, E08). Not decorative.
- E24 bootstrap + E25 label-shuffle placebo + E26 channel placebo together form a sensible triangulation of the LA signal. The instinct is right, the execution is incomplete.
- TDD tests (`test_cohort_durations.py`) correctly enforce the cohort invariants (perm ≤ comm ≤ CCC).
- §6.4 is honest about the concordance tie between Weibull and LogNormal and backs off the "champion" claim to AIC.

---

## 4. Mandated experiments (must run before accept)

Each experiment must be added to `results.tsv` with a new `experiment_id`, run using the same seed (42), and referenced in the paper revision.

### R1 — CCC-filing-rate-adjusted Phase B ranking (HIGH PRIORITY)

**What to compute.** For every (LA × size_stratum × type) cell with n ≥ 30, compute p_complete_48m both (a) as currently (unconditional) and (b) conditional on CCC filing: p_complete_48m_given_filed = P(CCC_date_validated ≤ grant + 48 m | CCC filed eventually). Publish a parallel ranking table. Also compute the Spearman rank correlation between the ranking on (a) and the LA-level CCC-filing rate from E26.

**Why.** My spot check produced Pearson r = 0.53 between LA CCC-filing rate and the Phase B weighted p_complete_48m for dwelling schemes >1 unit. The observed ranking is contaminated by filing-channel heterogeneity — the paper acknowledges this in §5.4 qualitatively but continues to name LAs as "delivery workhorses" in §5.8 and §7.

**Record as.** `R1` — metric `spearman_rank_unadjusted_vs_ccc_filing_rate`; plus a new recommendations file `discoveries/optimal_la_scheme_recommendations_channel_adjusted.csv`.

**What should change in the paper.**
- If ρ > 0.3: §5.8, §6.1 and §7 must be rewritten to lead with the channel-adjusted ranking; the conclusion sentence naming counties must cite only the adjusted ranking. The language "delivery workhorses" must be explicitly attributed to the adjusted measure and an explicit note added that the unadjusted ranking is not interpretable as a delivery ranking.
- If ρ ≤ 0.3: the current ranking stands and the paper should note the channel check confirmed robustness.

### R2 — AHB composition-adjusted duration comparison (HIGH PRIORITY)

**What to compute.** Run the E10 AHB-vs-private commencement-to-CCC comparison
(i) stratified by size_stratum (1 / 2-9 / 10-49 / 50-199 / 200+) with N per stratum reported, and
(ii) stratified by apartment_flag,
(iii) also run as a Cox regression with ahb_flag + log_units + apartment_flag + grant_year + is_dublin as covariates; report the HR for ahb_flag and its 95% CI.

**Why.** Reviewer check: AHB schemes have median 28 units vs private median 1 unit, and AHB apartment-share is 0.3% vs private 4.4% — they are composition-wise very different cohorts. The "+46 day" gap is ambiguous between (a) genuine AHB slowness and (b) AHB-selects-larger-projects slowness. The paper's §5.3 interpretation ("site-complexity and regulatory-compliance diligence") is a hypothesis, not a finding.

**Record as.** `R2a` (stratified-by-size gap), `R2b` (stratified-by-apartment gap), `R2c` (Cox HR).

**What should change.** Remove the causal language "This likely reflects ..." in §5.3. Replace with: AHB cohorts differ structurally from private on size and type; within-stratum gap is X days / HR Y. State which way the size-conditioned gap points; it may reverse sign.

### R3 — Dublin-apartment interaction (I01) with size control

**What to compute.** Re-run I01 (Dublin × apartment on comm-to-CCC) stratified by size_stratum for apartments. Dublin apartments are ~100% in schemes of 10+ units, non-Dublin apartments likely include smaller schemes. Report the DiD within the 50–199 and 200+ strata separately, with N and observed events.

**Why.** The headline "Dublin apartments take 607 days vs Dublin dwellings 453" is a comparison across unit mixes. Without a size control this interaction is not isolating an apartment-in-Dublin effect.

**Record as.** `R3` with breakdown by stratum.

**What should change.** §5.6 I01 paragraph must cite the size-conditioned DiD as the headline number, with the raw number demoted to a robustness appendix.

### R4 — CCC-filing-rate-adjusted dark-permission estimate (HIGH PRIORITY)

**What to compute.** Re-estimate the 72-month cumulative commencement share (E17) and the dark-permission classifier (E20) using:
(a) the current definition (CN_Commencement_Date filed), and
(b) a "joined" definition: commenced if either CN_Commencement_Date filed OR CCC_Date_Validated filed (catches projects whose commencement notice was lost but CCC was submitted); AND
(c) a bound analysis: for the opt-out-eligible single-site subset (one_off_flag==1), report the dark share separately; for the non-opt-out subset, report the dark share separately.

**Why.** The 0.3% figure is the first number a policy reader will quote. The paper disclaims it in §5.2 and §6.3, but the 0.3% number is repeated in the abstract without a bound. The composition breakdown (one-off vs multi-unit vs apartment) is not reported.

**Record as.** `R4a, R4b, R4c`.

**What should change.** The abstract should report the dark-permission rate as a range or as "0.3%–X% depending on channel definition", and §5.2 should give the breakdown by the three subsets. Section 6.3's caveat is fine but needs the quantitative bounds to be operational.

### R5 — Multi-phase (E12) site-complexity control

**What to compute.** Re-run E12 (multi-phase vs single-phase permission-to-commencement) stratified by size_stratum. Multi-phase projects are structurally larger. Report the within-stratum gap for 50–199 and 200+ only. Also fit Cox with multi_phase + log_units + apartment_flag + is_dublin and report the multi_phase HR.

**Why.** +288 days is called out as the largest Phase 2 effect besides the extension-proxy. But "multi-phase" is near-perfectly correlated with scheme size, so this may just be the size-effect re-indexed.

**Record as.** `R5a` (within 50–199), `R5b` (within 200+), `R5c` (Cox HR).

### R6 — Section-42 extension-proxy validity check

**What to compute.** The E11 extension proxy (grant-to-expiry > 5.5 years) assumes the expiry date reflects any Section-42 extension. Verify: (i) what share of rows have `CN_Date_Expiry` populated at all (pc cohort); (ii) plot the distribution of `CN_Date_Expiry - CN_Date_Granted` in days — is it bimodal around 5y and 5y+extension?; (iii) repeat E11 using only rows where the expiry-grant gap is exactly known and > 0.

**Why.** The single largest stratification effect in the paper (+446 d) rides on a proxy whose construct validity is asserted but not checked. If expiry-date populating is non-random (e.g. only appears on permissions the LA has administratively re-examined), E11 may conflate extension status with LA administrative activity.

**Record as.** `R6a` (populated share), `R6b` (expiry-grant histogram summary), `R6c` (restricted E11).

### R7 — Temporal-split external validation

**What to compute.** The paper proposes this in §6.5 as future work, but it is cheap and should be in scope. Fit LogNormal AFT and Cox PH on grant_year ∈ [2014, 2021]; score on grant_year ∈ [2022, 2025]. Report out-of-sample concordance and calibration (Brier at the 24-month mark for the dark-permission task).

**Why.** A blind reviewer would not accept the tournament-champion claim without an out-of-sample check — in-sample concordance differences at the third decimal place are not credible evidence of model superiority.

**Record as.** `R7a` (Cox OOS concordance), `R7b` (LogNormal AFT OOS concordance), `R7c` (LightGBM OOS AUROC).

**What should change.** If OOS concordance gap reverses or vanishes, §5.5 and §6.4 must re-state the champion selection as "we cannot discriminate among Cox / Weibull / LogNormal on a temporal-split holdout."

### R8 — Dublin-advantage (E06) decomposition

**What to compute.** Current E06 says Dublin is 45 d faster than non-Dublin; §5.3 says this is "dominated by Dublin's lower share of slow-to-start one-off dwellings". Make that claim quantitative: compute E06 stratified by size_stratum, and report the sign and magnitude within each stratum. Compute what fraction of the 45-d gap is explained by one_off_flag composition (Oaxaca-Blinder-style decomposition on the medians).

**Why.** The narrative in §5.3 asserts a mechanism that would need to be checked before publication.

**Record as.** `R8a` (stratified E06), `R8b` (share explained by one-off composition).

### R9 — Bootstrap CI on ALL headline claims

**What to compute.** Add 500-replicate bootstrap 95% CIs (same protocol as E24) to:
- 498 d commencement-to-CCC median (E00b)
- 962 d complete-timeline median (E00c)
- each of the seven KEEP stratification gaps in §5.3 (E06, E07, E08, E09, E10, E11, E12)
- each of the five interaction effects I01–I05
- the 0.3% dark-permission rate (via bootstrap over the 90,835-row 72-m-eligible cohort)

**Why.** Only E24 currently has a bootstrap CI. The abstract quotes 232 / 498 / 962 as point estimates; the paper needs to report uncertainty on the numbers it leads with. Several "+54 day" / "+46 day" effects may be within noise on an N that varies by two orders of magnitude across rows.

**Record as.** `R9a` through `R9k`, one per claim.

**What should change.** The §5 results table and the abstract must carry ±CI for every headline. Any effect whose bootstrap CI crosses zero must be explicitly flagged as "not distinguishable from zero at 95%" and the KEEP/REVERT decision revisited.

---

## 5. Minor revisions (no additional experiment required, but must be addressed in text)

1. **§1 Abstract.** Replace "the first project-level cohort dataset of Irish residential building-control filings" with something like "the first publicly reproducible …" — "first project-level cohort dataset" is a strong originality claim that is hard to verify in a blind review.
2. **§2.2.** The aggregate baseline k*≈8 quarters is asserted as output of running BHQ15+HSM13 cross-correlation — but no k* sweep curve or β estimate is reported. Add a plot or a one-line standard error.
3. **§3.2.** The tie-handling choice (Efron) is cited but not tested against Breslow or exact-partial. Not critical, one-line robustness note.
4. **§4.3.** The KEEP threshold is 10 d (≈1.4% of baseline) but several "KEEP" rows have deltas well under 10 d (E08: +18 d, E16: −11 d). Check the status assignments are consistent with the stated threshold and add the threshold to the §4.3 rule-statement.
5. **§5.3 E06.** "45-day *advantage* for Dublin, opposite to the prior expectation" — the prior expectation is not stated earlier; say what the prior was and cite it.
6. **§5.3 AHB paragraph.** The phrase "AHB cohort is small, N = 1,682" is correct but the comparison to private N=74,883 means the 46-day gap has a much larger SE on the AHB side than on the private side — report the individual-cohort CIs.
7. **§5.5 tournament table.** Add OOS concordance (from R7) as a column; drop the "champion" designation from the table header (already demoted in §6.4 but the table still says "champion").
8. **§5.7.** "The dominant features, by empirical inspection, are scheme size (log_units) and grant_year." Report permutation importance or SHAP values rather than "empirical inspection" — LightGBM's SHAP integration is one line.
9. **§5.8.** Strike the sentence "The policy-relevant conclusion is that the delivery cells … are concentrated in Dublin commuter counties …" until R1 is complete. Rephrase in conditional tense.
10. **§6.4 Limitations.** Add: "The Phase B LA ranking is co-informed by CCC-filing-rate heterogeneity (r ≈ 0.53 in the unadjusted ranking); the channel-adjusted ranking (R1) should be preferred."
11. **§6.4 Limitations.** Add: "The E11 extension-proxy depends on the assumption that populated `CN_Date_Expiry` reflects post-grant administrative action; this has not been tested against the Section 42 register directly."
12. **§7 Conclusion.** The final paragraph is appropriately hedged on the dark-permission estimate but still names counties — revise once R1 is complete.
13. **Reference list.** Several textbook-level cites are named inline (Kalbfleisch & Prentice, Klein & Moeschberger, Therneau & Grambsch) but not leveraged. Either cite the specific chapter/section being used or drop.
14. **Tests.** `test_cohort_durations.py` has 7 tests — reasonable coverage of invariants but does not test any of the KEEP/REVERT thresholds or any of the I01–I05 interaction signs. At least one regression test per headline finding would strengthen the TDD posture the project claims.

---

## 6. What an accepted version would look like

1. `results.tsv` contains R1–R9 (with R9 producing sub-rows R9a–R9k).
2. `discoveries/optimal_la_scheme_recommendations_channel_adjusted.csv` exists and is the primary ranking cited in §5.8.
3. The abstract carries CIs on all three headline durations and on the 0.3% dark rate.
4. §5.3 AHB, multi-phase, and Dublin paragraphs cite within-stratum effects, not raw gaps.
5. §5.5 cites OOS concordance and drops "champion" language in favour of "indistinguishable on temporal holdout" OR preserves the champion designation supported by OOS evidence.
6. §5.8 names counties only after R1 has been run and only via the channel-adjusted ranking.
7. §6.4 has explicit quantitative channel-correction language.

---

## 7. Summary table for the author

| Mandate | Priority | Blocking for §abstract | Blocking for §5.8 ranking |
|---|---|---|---|
| R1 Channel-adjusted Phase B ranking | HIGH | no | YES |
| R2 AHB size/type stratification | HIGH | no | no |
| R3 Dublin×apartment size-controlled | MED | no | no |
| R4 Dark-rate composition bounds | HIGH | YES | no |
| R5 Multi-phase size control | MED | no | no |
| R6 Extension-proxy validity | MED | no | no |
| R7 Temporal-split OOS | HIGH | no (§5.5 change) | no |
| R8 Dublin advantage decomposition | LOW | no | no |
| R9 Bootstrap CI on all headlines | HIGH | YES | no |

Without R1, R4, R7, and R9, the paper is not publishable. R2, R3, R5 are required to avoid over-claiming. R6, R8 are robustness polish.

---

*End of blind review.*
