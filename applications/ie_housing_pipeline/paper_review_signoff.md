# Phase 3.5 signoff review — Irish housing permission-vs-completion paper

**Reviewer**: independent Phase 3.5 signoff agent
**Date**: 2026-04-16
**Inputs checked**: paper.md (revised), paper_review.md, analysis.py, results.tsv, discoveries/pipeline_annual.csv, discoveries/lag_sensitivity.csv, website at /home/col/website/site/content/hdr/results/irish-housing-pipeline/index.md
**Build**: Hugo build passes (exit 0).

## Check against Phase 2.75 sign-off criteria

### R1. Cohort-mismatch disclaimer on 2-year conversion — ADDRESSED
Table 1 column header relabelled to "2-year aggregate ratio (completions T+2 ÷ permissions T)", and an explicit footnote follows the table: *"this is a population-level aggregate … not a cohort-tracked rate. Permissions granted in 2019 may complete in 2025 or 2026; completions in 2021 partly reflect permissions granted before 2019, which are not captured in BHQ15. A rising ratio can reflect a changing mix as much as genuinely higher follow-through."* Repeated in §Caveats bullet 1. Recorded as `E01-R1` in results.tsv. PASS.

### R2. Pre-2019 comparison — ADDRESSED, and strengthened
The paper did not merely acknowledge the problem; it pulled BHQ16 (1975-2025) to produce a pre-2019 comparison table showing 2-yr ratios of 86% (2016), 77% (2017), 54% (2018), 41% (2019). This reframes the 41%→65% headline as a recovery from a COVID trough toward — still below — the pre-COVID regime. Surfaced in §"What we found" as its own paragraph, in §Caveats, and in the blurb. Recorded as `E02-R2` in results.tsv. This is a real strengthening of the paper, not a cosmetic mention. PASS.

### R3. SHD vs Non-SHD not apples-to-apples — ADDRESSED via option (b)
§"The SHD window: descriptive only" retitled and softened. Explicit sentence: *"We are deliberately **not** inferring relative productivity here: SHD permissions are apartment-dominant large schemes, non-SHD permissions are a mix of one-off houses, small scheme houses, and small apartment developments, and BHQ15 does not give us scheme counts broken down by SHD status — so a per-scheme productivity comparison is not computable from the available data."* Caveat repeated in §Caveats bullet 4. Recorded as `E03-R3` in results.tsv. The paper also documents *why* option (a) normalisation was not done — BHQ15 lacks scheme counts by SHD status, which is correct (verified against the BHQ15 dimension structure). PASS.

### R4. Commencement-notice middle stage — ADDRESSED via option (b)
The paper now opens with an explicit framing note: *"we do **not** observe the whole construction pipeline … never see the middle stage (commencement notices, which are held by the Department of Housing, not CSO PxStat). So what follows is a permission-vs-completion comparison with a lag, not a cohort-traced pipeline."* §"How we did it" ends with *"No cohort tracking — the data does not support it."* §"Permissions vs completions, year by year" replaces the former "The pipeline, year by year". Caveat repeated in §Caveats bullet 3. Recorded as `E04-R4` in results.tsv. Verified that the NHC01 commencement table is NOT reachable on CSO PxStat (404 — it's a Department of Housing series), so the documented unavailability is factual. PASS.

### Recommended (non-blocking)
- Lag sensitivity table: **delivered** in paper §"Lag sensitivity" and in discoveries/lag_sensitivity.csv. Ranking-across-lags robustness is demonstrated (2022 top at all lags, 2019-20 trough at all lags). Recorded as `E05-LAG`.
- Bootstrap CI: not delivered. Acknowledged in §Caveats as "No uncertainty quantification. The 41% → 65% jump is a point estimate with no confidence interval." Acceptable disclosure; CI would be an improvement but was marked non-blocking by Phase 2.75.
- 5-yr lapse for 2019 cohort: not computed (5-yr cohort ratio not implemented; 2019 permissions would lapse in 2024). This was marked non-blocking; we accept the omission given the paper now explicitly lacks cohort tracking and states "No cancellation/lapse accounting" as a caveat. Not blocking.

## Independent checks performed
- **Arithmetic reproducibility**: re-ran analysis.py; pipeline_annual.csv matches paper Table 1 exactly. 2019 perms 38,461; 2025 completions 25,237; 2-yr conv_2019 = 0.406; conv_2022 = 0.648.
- **Pre-2019 numbers**: recomputed from BHQ16 "Units for which Permission Granted" × "Ireland" × (All houses + Apartments). 2016=15,950; 2017=20,776; 2018=28,939. Match paper.
- **No double-counting**: BHQ15 sums use only "Apartment units" + "All house units" (the "Multi-development house units" subset is excluded, as the 2.75 reviewer noted and we verified: 13,941 ≤ 19,563 for 2019).
- **Title claim**: the word "pipeline" is preserved in the repo path and in the one sentence saying "we do not observe the whole construction pipeline", but the body of the paper is now explicit that this is a two-end comparison, not a three-stage pipeline. Acceptable — the honesty is up front.
- **Website matches paper**: side-by-side structural check. Website has the same blurb, same Table 1 with footnote, same pre-2019 context table, same Caveats section, same "retroactively revised on 2026-04-15" note, same softened SHD section. Hugo build passes.
- **results.tsv**: new rows E01-R1 through E05-LAG appended with explicit commit=phase2.75. Header schema preserved.

## Things a nastier reviewer might still raise (not blocking)
- The pre-2019 conversion ratios are computed against NDA12 completions which themselves begin 2012. If urban-area coverage of NDA12 grew over time, pre-2019 completion totals would be systematically underestimated, which would *inflate* the pre-2019 ratios. The paper does not check NDA12 area coverage over time. However, this would only strengthen the caveat (pre-COVID may have been even higher), not weaken it.
- "Permission volume is the binding constraint" is stated as the policy conclusion in both the paper and the website. It is a defensible conclusion under either reading of the conversion trajectory, as the paper now explicitly argues. Not a blocker but worth noting that this claim rests on the observation that completions cap at ~25,000 even during the best conversion years, which is empirically supported by Table 1.
- Hugo build succeeds; no broken ref shortcodes.

## Verdict

**NO FURTHER BLOCKING ISSUES**

R1 through R4 are actioned in paper.md with matching updates to results.tsv and the website summary. The surfaced caveats are in a dedicated §Caveats section of the paper (not only in code comments or script docstrings, which was the specific Phase 2.75 concern). One recommended improvement (bootstrap CI) is still outstanding but was marked non-blocking and is now disclosed as a known limitation. The core findings reproduce from the data, the methodological caveats are honestly stated, and the policy claim survives the caveats.
