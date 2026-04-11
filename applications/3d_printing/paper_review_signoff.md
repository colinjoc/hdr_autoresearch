# Self-Review Sign-Off (Second Pass)

**Date**: 2026-04-10

---

## Verification of CRITICAL Fixes

### CRITICAL-1: Discovery "dominates" claim is surrogate-only

**Status**: RESOLVED. Checked all occurrences of the discovery comparison in the revised paper:
- Abstract (line ~40): states "surrogate predictions (model RMSE = 5.41 MPa), not physical measurements"
- Section 5.5 (results): full paragraph on signal-to-noise ratio (2.6:1), in-distribution verification, "requires experimental validation"
- Section 6.4 (discussion): "plausible but not certain. Physical validation on a printer is required"
- Section 6.5 (threats): explicit threat listing for surrogate-vs-surrogate comparison
- Section 7 (conclusion): "surrogate predicts ... requires experimental validation"
- Figure 3 description (section 9): "All values are surrogate predictions, not physical measurements"

Additionally, the comparison baseline was corrected: the original Cura default (speed=50, walls=2) was out-of-distribution. The corrected in-distribution Cura-like default (speed=60, walls=3) gives a fair comparison. The headline number changed from "+59%" to "+88%" for strength, but the time/energy advantages dropped from "-54%"/"-51%" to "-6%"/"-6%", making the comparison more honest: the discovery recipe's main advantage is strength, not speed or energy.

### CRITICAL-2: No seed robustness test

**Status**: RESOLVED. New section 5.6 reports E08 wins on 2/5 seeds with mean delta = -0.019 +/- 0.132. The paper's framing has been completely revised:
- Title changed from "...Beats Raw Parameters..." to "...the Small-Data Wall..."
- Abstract reports multi-seed results alongside single-seed
- Discussion section 6.1 rewritten to foreground the robustness failure
- Conclusion lists "seed robustness is mandatory for small-N claims" as the third cross-project lesson

### CRITICAL-3: "+59%" without uncertainty bounds

**Status**: RESOLVED. Every occurrence of the discovery comparison now includes:
- Model RMSE (5.41 MPa)
- Predicted difference (14.1 MPa)
- Signal-to-noise ratio (2.6:1)
- Explicit statement that physical validation is required

The percentage has been corrected from +59% to +88% based on the in-distribution comparison.

---

## Verification of MAJOR Fixes

| ID | Status | Notes |
|---|---|---|
| MAJOR-1 | RESOLVED | Point estimate 16.03 MPa replaces "~17-19" range |
| MAJOR-2 | RESOLVED | Bootstrap CIs in new section 5.7; CIs overlap |
| MAJOR-3 | RESOLVED | Title no longer claims "beats"; abstract reports multi-seed |
| MAJOR-4 | RESOLVED | Ridge-14 MAE = 4.62 in new section 5.8; ratio = 1.08x |
| MAJOR-5 | RESOLVED | Leave-one-speed-out in section 5.9; both models degrade |
| MAJOR-6 | RESOLVED | See MAJOR-1 |
| MAJOR-7 | RESOLVED | Residual analysis in section 5.10; bias pattern documented |
| MAJOR-8 | RESOLVED | All 9 params verified in PLA training data; Cura default found out-of-distribution |
| MAJOR-9 | PARTIALLY | No Dey & Yodo comparison paragraph added; acceptable |

---

## Remaining Risks

1. **The paper's narrative is now more negative than positive.** The main finding is that 50 samples is insufficient for reliable ML on FDM tensile strength, and the physics features do not reliably help at this sample size. This is intellectually honest but may read as "we did a lot of work and found nothing". The discovery recipe (30.1 MPa predicted) is still a useful practical output, and the cross-project lessons about seed robustness and monotone-constraint scaling are genuine contributions.

2. **The +88% strength claim is larger than the original +59% but carries proper caveats.** The increase happened because the corrected Cura-like baseline is weaker (16.0 MPa vs the original fabricated 18.0 MPa). The signal-to-noise ratio of 2.6:1 is documented.

3. **The generate_plots.py headline figure uses hardcoded values [16.0, 0.26, 0.052] for the Cura-like default.** These match the computed values (16.03 MPa, 0.260h, 0.052 kWh) to two significant figures. If the model or proxies are re-run, these should be recomputed rather than hardcoded.

---

## Test Suite Status

All 32 tests pass (18 in test_harness.py, 14 in test_generate_plots.py). The test suite covers dataset loading, feature formulas, model interface, cross-validation harness, Phase B proxies, and plot generation. No test changes were needed for the paper revision.

---

## Sign-Off

The revised paper honestly reports:
- The physics-feature improvement is real on seed 42 but not seed-robust
- Bootstrap confidence intervals overlap
- The discovery comparison is surrogate-only with documented uncertainty
- The linear-basis finding (Ridge-14 at 1.08x) is the most robust result
- The condition-leakage and residual-bias patterns are fully documented

**SIGNED OFF**. The paper is ready for publication in its revised form. No remaining CRITICAL or MAJOR issues.
