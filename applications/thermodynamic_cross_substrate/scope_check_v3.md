# Scope Check v3 — Finite-time Landauer bounds, Bérut to GPU

Reviewer: fresh sub-agent, no access to prior rounds.

## 1. Novelty of the contribution

The claim splits cleanly into two atoms. Atom (a) — "refit Bérut et al. 2012 under the Schmiedl–Seifert (2007) / Proesmans–Ehrich–Bechhoefer (2020) finite-time law, and test an asymmetric generalisation *B*(*r*) = π²(1+*r*)²/(4*r*)" — is, as far as I can tell, genuinely novel as a *targeted* empirical exercise, but the novelty is thin. The asymmetric-barrier correction is a textbook exercise in overdamped control theory; anyone who has read Aurell–Mejía-Monasterio–Muratore-Ginanneschi (2011) on optimal protocols in asymmetric wells has written something essentially equivalent. Close comparators: (i) Proesmans, Ehrich & Bechhoefer 2020 — derives π² in a symmetric well, tests against synthetic data; (ii) Dago et al. 2021–2022 (Bechhoefer group) — already refit Bérut-like bit-erasure cycles in the Proesmans finite-time framework at multiple τ using nanomechanical cantilevers, with several protocol variants; (iii) Zhen et al. 2021 (Nature Physics) — "Universal bound on the finite-time dissipation" explicitly tests finite-time Landauer against colloidal data. The gap the proposal exploits (nobody refit *the original Bérut curve* under *the asymmetric* variant) is real but narrow; a PRE referee will ask why the cantilever refits don't already settle it.

## 2. Falsifiability

Mixed. The three "binary kill-outcomes" are not equally sharp.

- Outcome 1 (Bérut *B* fit within ±20% of *B*(*r*)) is genuinely falsifiable *if* the optical-trap asymmetry *r* in Bérut 2012 is actually recoverable from the supplementary to useful precision. If *r* is only loosely bounded, the ±20% window becomes a tunable knob and the test is not pre-specified — it is a post-hoc fit with a free parameter rebranded as a prior.
- Outcome 2 ("the CI includes both π² and *B*(*r*), null result") is a null-escape hatch, not a falsification — it is the outcome you report when you cannot discriminate, which is not the same as being refuted. Perfectly fine to pre-commit to, but don't call it a kill.
- Outcome 3 (CMOS prediction within one order of magnitude) is the weakest. "Within 10× of Patterson 2021" is an enormous window for a thermodynamic bound; any non-crazy prefactor will satisfy it. This is unfalsifiable-in-disguise — tautological given how loose the tolerance is.

## 3. Cross-substrate extrapolation

Apples-to-oranges. Colloidal overdamped Langevin dynamics in an optical trap share almost no relevant dissipation physics with CMOS switching — the latter is dominated by CV² charge/discharge of interconnect capacitance, sub-threshold leakage, and clock-tree power, none of which are governed by a finite-time Landauer coefficient. The proposal concedes as much in §2(b) by listing leakage and data-movement as candidate dominant corrections. A PRE referee will read that and ask: if those terms dominate, in what sense is the finite-time coefficient being tested at all? The one-order-of-magnitude tolerance is not a test of the bound — it is a test of whether you chose reasonable engineering numbers.

## 4. Likely killer objections

- "Dago 2021/2022 already did this refit on a related platform" — novelty looks incremental.
- "The asymmetric *B*(*r*) is an elementary rescaling; you have not shown the Bérut data can resolve *r* at all" — identifiability objection.
- "The CMOS leg is a dimensional-analysis exercise disguised as a thermodynamic test" — substrate-mismatch objection.

## Verdict

The Bérut-only leg (a) is probably publishable as a short PRE paper if the asymmetry *r* is genuinely extractable and the discrimination is genuinely sharp — but the current proposal does not demonstrate either. The CMOS leg (b) is not a thermodynamic test in any meaningful sense and will sink the paper. Drop (b), tighten (a) with an explicit identifiability argument for *r*, and re-submit.

VERDICT: REFRAME
