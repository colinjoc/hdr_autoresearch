# Paper Review Signoff

**Project:** ie_lever_interactions
**Date:** 2026-04-16
**Reviewer:** Blind adversarial reviewer (Phase 3.5)

## Status of all findings

| ID | Severity | Finding | Resolution | Status |
|----|----------|---------|------------|--------|
| F1 | CRITICAL | 50% workforce expansion infeasible at projected rates | RV01 run. Paper SS5.5 includes 3-scenario trajectory. Title/abstract revised. | RESOLVED |
| F2 | MAJOR | Diminishing returns to workforce not modeled | RV02 run. Effective capacity 49,289 vs 52,500 reported in SS4.8, SS6.4. | RESOLVED |
| F3 | MAJOR | r=0.91 extrapolated linearly beyond observed range | RV03 run. Tanh sensitivity in SS5.4, SS5.6. Linear figures now labeled "upper bounds." | RESOLVED |
| F4 | MAJOR | GE price effects not modeled | RV04 run. Demonstrated PE assumption breaks down. SS5.9 added with honest assessment. | RESOLVED |
| F5 | MAJOR | Modular x CPO redundancy may be ceiling artifact | RV05 run. Confirmed: gross interaction = 0. SS5.2 and SS6.3 revised. | RESOLVED |
| F6 | MAJOR | No CIs on interaction terms or Pareto ranking | RV06 run. CIs on 5 pairs in SS5.8. All signs robust. | RESOLVED |
| F7 | MINOR | Title implies empirical discovery | Title changed to "Deterministic Parameter-Propagation Analysis." | RESOLVED |
| F8 | MINOR | Pareto fiscal costs unsourced | Caveat added to SS4.5 and SS5.7. | RESOLVED |
| F9 | MINOR | Soft-ceiling congestion parameter unsourced | Caveat added to SS4.2. | RESOLVED |
| F10 | MAJOR | "Optimal" language without optimization | Changed to "maximum policy package" throughout. | RESOLVED |

## Assessment

All CRITICAL and MAJOR findings have been addressed. The revised paper:

1. Honestly reports that the 50% workforce expansion takes 8-16 years at plausible recruitment rates (RV01).
2. Shows that diminishing workforce productivity may push effective capacity below the HFA target (RV02).
3. Presents the linear soft-ceiling numbers as upper bounds, with tanh sensitivity reducing the maximum package from 167,810 to 50,925-91,702 depending on saturation (RV03).
4. Acknowledges that the partial-equilibrium assumption breaks down for large supply changes (RV04).
5. Correctly identifies the modular x CPO "redundancy" as a ceiling artifact with zero gross interaction (RV05).
6. Reports Monte Carlo CIs on key interaction terms; all signs robust (RV06).

The paper's qualitative conclusion -- that cost reduction without capacity expansion cannot close the housing gap -- survives all robustness checks. The quantitative estimates are now properly bounded and caveated.

NO FURTHER BLOCKING ISSUES
