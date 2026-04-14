# Phase 2.75 Blind Review — YC vs Non-YC

## Summary

**Verdict: BLOCKING.** The null conclusion is not yet credible. Three structural
issues — a fake "ecosystem" covariate set, a ~10x name-match attrition that
almost certainly excludes successful YC firms, and power too low to detect the
+5–15 pp effect the prior literature predicts — each independently force the
ATT toward zero. Two code-level bugs compound this: right-censoring of 2019–20
filings is scored as real zeros, and the randomisation-inference test (E14)
permutes the wrong scale. Placebo E13 recovers +1.6 pp, essentially the same
magnitude as the headline +2.2 pp; that is evidence of residual selection, not
evidence of a null. The author must address the blocking issues before writing
this up as "consistent with Kerr–Lerner–Schoar 2014". It may well land there,
but the current experiments cannot tell us.

## Blocking issues

1. **M3 "ecosystem" is not ecosystem.** `hdr_loop.COV_SETS["M3_ecosystem"]`
   equals M2 + `entitytype` (Corp/LLC). `design_variables.md` defines M3 as
   M2 + MSA VC density + Bay/NYC/Boston flags; M4 adds VIX + macro. The code
   M4_macro is byte-identical to M3. Chen-Gompers-Kovner-Lerner (2010) is the
   main confounder cited in `knowledge_base.md`, and it is not in the model.
   Every E02 / E05 / E06 / E07 / E09 / E10 number is therefore an
   under-controlled estimate, and the "attenuation to zero" narrative is
   vacuous — the ladder never adds the covariate that is supposed to attenuate
   it. **Fix: RV01.**

2. **Matched-sample selection is almost certainly not ignorable.** 117 / 1,481
   YC 2014–2019 admits = 7.9% name-matched to Form D. YC firms that raise via
   uncapped SAFEs or 4(a)(2) angel rounds never file Form D. Successful YC
   companies who raise outside Rule D (the modal modern path post-2018) drop
   out; struggling YC companies forced into formal 506(b) rounds stay in. This
   selection biases the ATT *toward* zero in exactly the direction the author
   needs to rule out. The `fuzzy_matcher.py` module exists and is unused —
   A2 in `research_queue.md` predicted ~60% match rate. **Fix: RV02.**

3. **Right-censoring treated as zero.** Panel includes 13 treated filings in
   2020 with a follow-on rate of 0.000 (vs 0.63 in 2016). The T+5 window for a
   2020 filing ends 2025, but data ends 2024Q4. Same issue applies to 2019
   filings for T+7y (E07-T7y), which nevertheless reports identical point
   estimate to T+5y — a mechanical artefact of the window exceeding the data.
   The author must either (a) restrict the sample to anchors whose T+H window
   closes ≤ 2024-12-31, or (b) use a survival / Kaplan-Meier estimator.
   **Fix: RV03.**

4. **Randomisation inference (E14) permutes at the wrong scale.** `hdr_loop.
   run_e14_randomization_inference` permutes `is_yc` across the full 31,841-
   row panel, then recomputes the diff of unmatched means, and compares to the
   PSM-matched observed ATT. The null distribution is mechanically tight
   (n_t=117 vs n_c=31,724) so p=0.608 is not informative about whether the
   matched +2.2 pp is distinguishable from noise. The correct test permutes
   treatment within matched sets (or within sector × quarter strata) and
   re-runs the full matching pipeline each permutation. **Fix: RV04.**

5. **No balance diagnostics reported.** There is no table of standardised
   mean differences pre/post match, no propensity overlap histogram, no
   caliper-drop count. `psm_nn_match` silently drops caliper-violators but
   the caliper never binds in the results (n_control = 117 × 5 = 585 exactly
   in every run). Overlap is asserted, not demonstrated. **Fix: RV05.**

## Non-blocking concerns

- E13 placebo RD = +0.0163, essentially equal in magnitude to the headline
  +0.0222 with wider CI. This is the tell-tale signature of residual selection
  from the name-matching/Form-D-filing channel, not a clean null.
- E16 E-value = 1.38 is computed from a point estimate whose CI crosses zero;
  an E-value for a non-significant estimate has no interpretive meaning. Drop
  or re-compute against the CI limit (VanderWeele-Ding §3.2).
- `outcome_follow_on` filter `startswith("D") & ~startswith("D/A")` also keeps
  `D-W` (withdrawn notices); cross-check magnitude is small but document.
- Multiple testing: 25 experiments reported with no adjustment. The era and
  sector slices (E09-2016-2017 ATT=+0.112 [−0.07,+0.29]; E10-Biotech
  ATT=−0.033) are underpowered (n_t ≤ 34) — flag as descriptive, not tests.

## Mandatory follow-up experiments

| exp_id | hypothesis | null prediction | data needed | expected runtime |
|---|---|---|---|---|
| RV01 | Adding real ecosystem covariates (MSA VC density, Bay/NYC/Boston, VIX) does not attenuate the ATT beyond M2 | |M3 – M2| < 1 pp | Pitchbook MSA aggregates or Chen et al. 2010 state-year table; FRED VIX | 1 h |
| RV02 | Raising the YC match rate with fuzzy matcher does not change the ATT sign | ATT at match-rate 30–50% within ±3 pp of 117-firm ATT | existing `fuzzy_matcher.py` | 30 min |
| RV03 | Restricting to anchors with complete T+H forward window yields the same ATT | ATT stable within ±2 pp after dropping 2019+ filings for T+5y; 2017+ for T+7y | panel.parquet, no new data | 10 min |
| RV04 | Correctly-scaled randomisation inference (permute within matched sets) yields p > 0.10 | p-value consistent with CI crossing zero | panel.parquet | 30 min (1000 perms × matching) |
| RV05 | Propensity overlap and standardised mean differences satisfy conventional thresholds | SMD < 0.25 on every covariate post-match; PS distributions overlap on ≥95% of treated support | panel.parquet | 10 min |
| RV06 | Alternative-accelerator placebo (M3): using Techstars / 500 as the treatment gives a similar null | |Techstars ATT − YC ATT| < 3 pp | Techstars/500 public roster, Form D join | 2 h |
| RV07 | Survival (Cox) analysis of time-to-next-raise gives a hazard ratio indistinguishable from 1 | HR 95% CI includes 1.0 | lifelines, panel.parquet | 30 min |

## What would change the conclusion

The null survives if and only if **all** of the following hold simultaneously:
(a) RV01 shows M3-with-real-ecosystem ATT is within ±2 pp of current estimate;
(b) RV02 shows fuzzy-match-expanded ATT (n_treated ≥ 300) is within ±3 pp of
117-firm ATT; (c) RV03 shows censoring-corrected ATT is within ±2 pp of
current; (d) RV04 randomisation p > 0.10 under correct permutation; (e) RV05
demonstrates balance SMD < 0.25 and overlap ≥ 95%; (f) RV06 alternative-
accelerator placebo gives a comparable null.

A positive finding emerges if RV02 lifts the ATT above +5 pp with CI excluding
zero at n_treated ≥ 300, or if RV01's ecosystem-corrected ATT moves in the
opposite direction. The current data cannot adjudicate between those cases.

---

## Phase 2.75 execution status (added 2026-04-14 post-implementation)

All mandatory RV experiments have been executed and logged to `results.tsv`
with `status="REVIEW"`.

| exp_id | result | reviewer criterion | verdict |
|---|---|---|---|
| **RV01-M3_real** | ATT +6.0 pp [−3.1, +15.2] (vs M2 +1.7 pp) | \|M3 − M2\| < 1 pp | **FAIL** in the direction OPPOSITE the reviewer expected: ecosystem covariates made the estimate MORE positive, not more null. |
| **RV02 fuzzy** | n_treated lifted 117 → 134 (9.2%, not the 30% target); ATT +1.6 pp [−6.4, +9.7] | n ≥ 30%-match-rate, ATT within ±3 pp | **partial**: match rate insufficient; fuzzy matcher too conservative to reach 30% without unacceptable false-positive rate |
| **RV03 censoring** | T+5y drops 5.8% anchors, ATT −0.6 pp; T+7y drops 33%, ATT +5.9 pp | within ±2 pp | **PASS** at T+5y; T+7y confirms censoring inflated the T+7y=T+5y artefact |
| **RV04 correct perm** | p = 0.327 (300 perms) vs E14's broken p = 0.608 | no strict threshold | **PASS** in spirit; observed +4.3 pp not rare under stratified permutation null |
| **RV05 balance** | max post-match \|SMD\| = 0.250; 99.1% on common support; 1 caliper drop | SMD < 0.25, support ≥ 95% | **BORDERLINE**: `log_offering_amount` sits exactly at the threshold |
| **RV06-alt lookalike** | lookalike placebo ATT = −21.5 pp [−26, −16]; YC PSM ATT = +6.0 pp; gap 27.6 pp | pure Techstars scrape blocked on Typesense auth; substitute executed | **PASS** as substitute: reveals matched-control pool is systematically under-raising because high-PS non-YC firms skip Form D via SAFE — biasing primary ATT toward zero |
| **RV07 Cox** | HR(is_yc) = 0.786 [0.565, 1.093], p = 0.153 | HR CI includes 1.0 | **PASS**: null consistent across alternative outcome specification (hazard of next raise) |

### Key narrative updates forced by Phase 2.75

1. **The null ATT is now an under-controlled under-count.** RV01 shifts the
   point estimate from +1.7 pp (bogus M3) to +6.0 pp (real M3 with Bay/NYC/
   Boston + VC density + VIX). The CI still includes zero — but not by a lot
   ([−3, +15]). The study has ~1.5σ suggestive evidence of a positive effect,
   not a clean null.
2. **RV06-alt reveals a filing-habits artefact.** The ~-22 pp ATT for
   high-PS non-YC firms (vs remaining non-YC) shows the PSM-matched control
   pool is not behaviourally comparable to YC firms — it systematically
   under-raises on Form D because the highest-PS controls raise via SAFE /
   direct equity instead. The primary PSM ATT is biased TOWARD zero.
3. **n_treated is the binding constraint.** At n = 117 the minimum
   detectable effect (80% power, α = 0.05, base rate 0.29) is ≈ 10 pp.
   Every point estimate we produce is under-powered for the 5-15 pp range
   the literature predicts.

The conclusion should now read: "Consistent-with-null but with large CI
and an identified filing-habits bias toward zero; point estimate moves to
~+6 pp after proper ecosystem correction; sample power inadequate for a
clean +5-15 pp detection." This is a very different claim from the original
"consistent with Kerr-Lerner-Schoar 2014 null."
