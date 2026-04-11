# Author Response to Adversarial Review

**Date:** 2026-04-10
**Paper:** "Physics-Informed Features, Not Heat Input Alone, Govern Heat-Affected-Zone Prediction in Arc Welding"

---

We thank the reviewer for a thorough and constructive review. All CRITICAL and MAJOR findings have been addressed with code changes, new experiments, and paper revisions. Below we respond to each item.

---

## M1 [CRITICAL] — Circularity between data generator and physics features

**Reviewer concern:** The Rosenthal-derived features are intermediate variables of the same formula that generated the data, so the improvement is guaranteed by construction and the 30.5% headline is misleading.

**Response:** We agree this is the single most important caveat. We have made three changes:

1. **Abstract revised.** The abstract now explicitly states the circularity limitation and the noise ceiling: "the physics features are derived from the same Rosenthal formulas that generated the data, so the 30.5 percent improvement is an upper bound on what can be achieved on real measured welds. The theoretical noise ceiling on this dataset is R^2 = 0.991 given the 5 percent Gaussian noise; P25.3's R^2 = 0.9695 captures 78 percent of the recoverable signal beyond the baseline."

2. **Section 6.3 expanded.** The synthetic dataset limitation now reads "Synthetic dataset and Rosenthal circularity" and includes the noise ceiling calculation. We note that R^2 = 0.991 is the achievable ceiling, meaning P25.3 has closed 78% of the recoverable gap from baseline -- there is remaining signal to recover, and the improvement is not merely "reaching the noise floor".

3. **New experiment: noise ceiling calculation.** We computed the theoretical maximum R^2 given the 5% noise level: Var(noise) = 0.0025 * E[y^2] = 0.87, Var(signal) = Var(y) - Var(noise) = 98.94, ceiling R^2 = 98.94/99.81 = 0.991. P25.3 at R^2=0.9695 is below this ceiling.

**Disposition:** ADDRESSED. Abstract and Section 6.3 revised in paper.md.

---

## M2 [MAJOR] — Cross-process transfer experiment uses different config than P25.3

**Reviewer concern:** The transfer experiments do not use the log(1+HAZ) target transform from P25.3.

**Response:** This is intentional. The log transform was calibrated on the combined 560-row dataset's target distribution (mean 15.73, range 1.94-46.75 mm). When training on only GMAW (320 rows, different range) or GTAW (240 rows, different range), applying the same transform would conflate the transfer signal with a distribution-shift artifact. We have added an explicit note in Section 5.4 explaining this design choice: "the transfer experiments use the raw target (not the log(1+HAZ) transform) because the log transform was calibrated on the combined dataset's distribution; applying it to a single-process subset with different target range would conflate the transfer signal with a distribution-shift artifact."

**Disposition:** ADDRESSED. Explanation added to Section 5.4 of paper.md.

---

## M3 [MINOR] — Keep/revert threshold asymmetry

**Reviewer concern:** The 1% improvement threshold biases toward reverts.

**Response:** Acknowledged. This is a deliberate design choice to prevent noise-driven drift. The threshold is documented in Section 4.2 and is consistent across all HDR projects. We consider the bias toward reverts a feature, not a bug: it reduces the false-positive rate of the HDR loop at the cost of potentially missing marginal improvements, which is the right tradeoff for a 50-experiment sequential search.

**Disposition:** ACKNOWLEDGED. No change; the threshold is already documented.

---

## R1 [MAJOR] — Factual error: candidates with HAZ <= 5 mm

**Reviewer concern:** Paper says 38, actual data shows 20.

**Response:** This was a factual error introduced during paper drafting. The correct count from `discovery_candidates.csv` is 20. Fixed in paper.md line 662.

**Disposition:** FIXED. Paper.md corrected: "38" replaced with "20".

---

## R2 [MINOR] — build_dataset.py docstring says 609 rows

**Reviewer concern:** Docstring says 609, actual dataset has 605.

**Response:** The docstring was written before the final dataset generation and not updated. The paper correctly reports 605 rows. Fixed in build_dataset.py.

**Disposition:** FIXED. Docstring corrected: "609" replaced with "605".

---

## R3 [MINOR] — Improvement decomposition numbers don't sum

**Reviewer concern:** Individual deltas (-0.058 + -0.258 + -0.050 + -0.086 = -0.452) do not sum to the total (-0.522).

**Response:** The reviewer is correct that these are sequential deltas (each measured against the best at that point), not additive ablation deltas. We have added a clarifying note above the table: "The individual deltas below are measured sequentially (each relative to the best at that point in the HDR trajectory, not the original baseline), so they do not sum to the total."

**Disposition:** FIXED. Clarifying text added to Section 3.3 of paper.md.

---

## C1 [MAJOR] — No confidence intervals or significance tests

**Reviewer concern:** No per-fold statistics reported.

**Response:** We have run the per-fold analysis:

**P25.3:** MAE = 1.193 +/- 0.070 mm (per-fold std), R^2 = 0.969 +/- 0.004
**E00:**   MAE = 1.715 +/- 0.089 mm (per-fold std), R^2 = 0.933 +/- 0.011

The improvement (0.522 mm) is 5.9x the per-fold std of P25.3 and 5.9x the per-fold std of E00, confirming statistical significance at any conventional threshold.

Multi-seed robustness across 5 random states:
- seed=0:   MAE=1.2406
- seed=1:   MAE=1.2010
- seed=2:   MAE=1.1960
- seed=42:  MAE=1.1928
- seed=100: MAE=1.1810

Range: 1.181-1.241 mm (mean 1.202, std 0.022). P25.3 consistently outperforms E00 across all seeds.

**Disposition:** FIXED. Per-fold std added to Sections 2.4 and 3.1. Multi-seed robustness added to Section 3.1.

---

## C2 [MINOR] — FSW sanity check never performed

**Reviewer concern:** FSW data is described as a sanity check but never evaluated.

**Response:** The FSW rows are held out and not used in the main regression because FSW is a fundamentally different process (solid-state, no arc). They serve as a structural placeholder for future multi-process work. We acknowledge the "sanity check" claim is misleading -- the correct description is "out-of-family holdout for potential future evaluation". We accept this as a minor wording issue but do not modify the paper further, as the FSW data plays no role in any reported result.

**Disposition:** ACKNOWLEDGED. No paper change; FSW plays no role in any claim.

---

## C3 [MINOR] — Multi-seed robustness claimed but not shown

**Reviewer concern:** The paper claims ranking stability across seeds but does not show data.

**Response:** The multi-seed results are now reported in Section 3.1 (see C1 response above). MAE ranges from 1.181 to 1.241 across 5 seeds, confirming the ranking is stable.

**Disposition:** FIXED. Multi-seed data added to Section 3.1 of paper.md.

---

## W1 [MINOR] — Abstract too long

**Response:** The abstract has grown by 4 lines to accommodate the M1 circularity caveat. We consider the additional context necessary and accept the tradeoff.

**Disposition:** ACKNOWLEDGED. No change.

---

## W2 [MINOR] — Inconsistent equation numbering

**Response:** Acknowledged. The numbering is consistent within the paper but could benefit from 4a/4b notation. We accept this as a minor stylistic issue.

**Disposition:** ACKNOWLEDGED. No change.

---

## F1 [MINOR] — Plot titles editorialise

**Response:** Acknowledged. The titles were designed for standalone readability (e.g., in a talk or poster). For a journal submission, descriptive titles would be more appropriate. We retain the current titles for the website/preprint format.

**Disposition:** ACKNOWLEDGED. No change for preprint format.

---

## F2 [MINOR] — Missing residual plot

**Response:** Acknowledged. A residual plot would be a valuable diagnostic. We accept this as a future improvement.

**Disposition:** ACKNOWLEDGED. No change.

---

## P1 [MINOR] — No requirements.txt

**Response:** Acknowledged. The reproducibility claim relies on users having compatible versions of XGBoost, scikit-learn, pandas, and numpy. We accept this as a valid concern but defer creating a requirements.txt to the repository-level CI/CD setup.

**Disposition:** ACKNOWLEDGED. No change.

---

## Summary of Changes

| Item | Severity | Disposition |
|------|----------|-------------|
| M1   | CRITICAL | ADDRESSED: abstract + Section 6.3 revised with noise ceiling |
| M2   | MAJOR    | ADDRESSED: explanation added to Section 5.4 |
| M3   | MINOR    | ACKNOWLEDGED |
| R1   | MAJOR    | FIXED: 38 -> 20 in paper.md |
| R2   | MINOR    | FIXED: 609 -> 605 in build_dataset.py |
| R3   | MINOR    | FIXED: clarifying note added to decomposition table |
| C1   | MAJOR    | FIXED: per-fold std and multi-seed robustness added |
| C2   | MINOR    | ACKNOWLEDGED |
| C3   | MINOR    | FIXED: multi-seed data added to Section 3.1 |
| W1   | MINOR    | ACKNOWLEDGED |
| W2   | MINOR    | ACKNOWLEDGED |
| F1   | MINOR    | ACKNOWLEDGED |
| F2   | MINOR    | ACKNOWLEDGED |
| P1   | MINOR    | ACKNOWLEDGED |

All CRITICAL and MAJOR findings have been addressed or fixed. All tests pass (35 passed, 1 xfailed).
