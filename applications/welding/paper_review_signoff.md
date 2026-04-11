# Review Sign-off: Welding HDR Paper

**Reviewer:** Adversarial Review Agent
**Date:** 2026-04-10
**Paper:** "Physics-Informed Features, Not Heat Input Alone, Govern Heat-Affected-Zone Prediction in Arc Welding"

---

## Verdict: ACCEPT

All CRITICAL and MAJOR findings have been satisfactorily addressed.

### M1 [CRITICAL] — Circularity: RESOLVED

The abstract and Section 6.3 now explicitly acknowledge the Rosenthal circularity and quantify the noise ceiling (R^2 = 0.991). The paper correctly frames the 30.5% improvement as an upper bound and notes that P25.3 captures 78% of the recoverable signal. The claim is no longer misleading.

### M2 [MAJOR] — Transfer config mismatch: RESOLVED

Section 5.4 now explains why the transfer experiments omit the log-target transform (distribution-shift artifact avoidance). The reasoning is sound.

### R1 [MAJOR] — Factual error: FIXED

Corrected from 38 to 20 candidates with HAZ <= 5 mm. Verified against discovery_candidates.csv.

### C1 [MAJOR] — Confidence intervals: FIXED

Per-fold standard deviations (MAE std = 0.070 mm for P25.3, 0.089 mm for E00) and multi-seed robustness (MAE range 1.181-1.241 across 5 seeds) are now reported. The improvement of 0.522 mm is approximately 6x the fold-to-fold standard deviation.

### Minor items: ACCEPTABLE

The remaining 10 minor findings are either acknowledged or fixed. None affect the paper's core claims.

### Tests

All 35 tests pass (1 xfailed) after all changes. No regressions introduced.

---

**Final assessment:** The paper is honest about its limitations, the numerical claims are now verified, and the methodology is sound within the stated scope. The synthetic data caveat is prominently stated. The paper is ready for website publication.
