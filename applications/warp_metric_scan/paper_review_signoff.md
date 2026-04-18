# Phase 3.5 Signoff: Warp Metric Scan

## Review Concerns -- Resolution Status

| # | Concern | Resolution | Status |
|---|---------|------------|--------|
| a | Fell-Heisenberg proxy not labelled as proxy in paper | Added explicit disclosure in Section 2.2 validation list: "pipeline validation only -- does not reproduce the self-consistent shell construction" | RESOLVED |
| b | F4 EC torsion model is ad-hoc, not standard EC derivation | Added disclosure in Section 2.1 (framework description) and new Section 4.3 (Modelling Limitations) explaining ad-hoc Gaussian profile vs. self-consistent Cartan derivation | RESOLVED |
| c | F5 Weyl projection treated as free parameter | Added disclosure in Section 2.1: "best-case analysis" framing. Reiterated in Section 4.3 | RESOLVED |
| d | Grid resolution sensitivity | Ran convergence test at 50/100/200 points: critical s0 = 4.195 at all three, relative change <0.1%. Added to Section 2.2 | RESOLVED |
| e | "Tantalizingly close" over-claiming | Not present in paper. Abstract, Section 4.1, and conclusions all say "formal loophole, not physical." No action needed | N/A |
| f | Missing tests for F4/F5 scan results | Added 3 tests: F4 critical s0 bounds, F5 C_W=-100 still violates, F4 grid convergence. All pass (13/13) | RESOLVED |

## Test Suite

- 13 tests, 13 passing
- Coverage: F1 baseline (3), F2 KK (1), F3 f(R) (1 via F1 Olum), F4 EC (4), F5 braneworld (2), grid convergence (1), flat spacetime (2)

## Paper Edits Made

1. Section 2.1 F4 description: ad-hoc torsion profile disclosed, Hehl et al. cited
2. Section 2.1 F5 description: best-case analysis framing added
3. Section 2.2 validation list: Fell-Heisenberg proxy labelled; 3 new test results added
4. Section 2.2: grid convergence paragraph added
5. New Section 4.3 (Modelling Limitations of F4 and F5): consolidates all caveats
6. Former Section 4.3 renumbered to 4.4

## Signoff

All mandated experiments executed. All review concerns resolved or confirmed not applicable. 13/13 tests green. The paper honestly labels F4 and F5 results as formal loopholes with ad-hoc modelling, not physical predictions. No over-claiming found.

**APPROVED for submission.**
