# Adversarial Review: Welding HDR Paper

**Reviewer:** Adversarial Review Agent
**Date:** 2026-04-10
**Paper:** "Physics-Informed Features, Not Heat Input Alone, Govern Heat-Affected-Zone Prediction in Arc Welding: A Hypothesis-Driven Study"

---

## Overall Assessment

The paper presents a well-structured hypothesis-driven investigation of physics-informed feature engineering for HAZ width prediction. The experimental log is thorough (50 experiments + 6 compositional retests + transfer tests + hypothesis tests), and the paper is transparent about the synthetic data limitation. The headline findings -- H1 refutation, cooling-time superiority over heat-input, and catastrophic transfer failure -- are genuine and well-supported. However, there are factual errors in the reported statistics, a circularity problem that the paper underplays, and missing robustness checks.

**Recommendation:** Revise and resubmit (minor-to-major revisions required).

---

## Category 1: Methodology

### M1 [CRITICAL] — Circularity between data generator and physics features

The data is generated from the Rosenthal closed-form solution. The winning physics features (heat input and cooling time t_{8/5}) are derived from the *same* Rosenthal formulas. The paper acknowledges this at lines 764-769 and 773-777 but underplays it. The 30.5% improvement is *guaranteed by construction*: the feature set contains the generator's own intermediate variables. Any residual is pure injected noise. The paper should:

1. State explicitly in the abstract that the improvement upper-bounds what is achievable on real data, not just in Section 6.3.
2. Quantify the theoretical ceiling: what R^2 is achievable given 5% Gaussian noise on the target? If the noise floor is ~0.97, then P25.3's R^2=0.9695 is at the noise ceiling, and the "improvement" is simply closing a gap that only exists because the baseline model was artificially handicapped by not using the generator's own variables.

**Severity:** CRITICAL. Without this, the headline "30.5% improvement" is misleading.

### M2 [MAJOR] — Cross-process transfer experiment does not use log-target transform

The transfer experiments in `hdr_phase25.py` (lines 163-165) train on raw y values, not log(1+y) as in the winning P25.3 configuration. The paper claims P25.3 is the "winning configuration" and then evaluates cross-process transfer with a *different* configuration (no log transform). This means the transfer gap of 455% is not attributable to P25.3 specifically -- it is a property of a non-winning variant. The paper should either re-run the transfer with the actual P25.3 setup, or clearly state that the transfer experiment uses a different configuration and explain why.

### M3 [MINOR] — Keep/revert threshold asymmetry not discussed

The threshold `MAE_new < best_so_far - max(0.005 mm, 0.01 * best_so_far)` requires improvement of at least 1% to KEEP. This is conservative and will bias toward reverts, potentially missing small genuine improvements. The paper should note this design choice and its consequences.

---

## Category 2: Results / Numerical Accuracy

### R1 [MAJOR] — Factual error: candidates with HAZ <= 5 mm

Line 656 of the paper states "Candidates with predicted HAZ <= 5 mm: 38". The actual data in `discoveries/discovery_summary.json` reports `n_haz_under_5mm: 20`. The `discovery_candidates.csv` file confirms 20 candidates below 5 mm. The paper number is wrong by 90%.

### R2 [MINOR] — build_dataset.py docstring says 609 rows, dataset has 605

The docstring at line 23 of `build_dataset.py` states "609 rows" but the actual CSV has 605 rows (606 lines including header). The paper correctly reports 605 at line 130. The docstring should be corrected.

### R3 [MINOR] — Inconsistent "improvement decomposition" numbers

The table at lines 398-404 claims the four changes sum to -0.522 mm. However, the individual deltas (-0.058 + -0.258 + -0.050 + -0.086 = -0.452 mm) do not sum to -0.522. The actual gap is E00 (1.7152) - P25.3 (1.1928) = 0.5224 mm. The individual deltas appear to be ablation-style numbers that do not decompose additively because the experiments were run sequentially against different running bests. The paper should either explain that these are non-additive or present the decomposition differently.

---

## Category 3: Completeness

### C1 [MAJOR] — No confidence intervals or statistical significance tests

All results are reported as point estimates. For a 560-row dataset with 5-fold CV, fold-to-fold variance is non-trivial. The paper mentions that "MAE standard deviation drops from ~0.07 mm to ~0.05 mm" at line 386 but never reports actual per-fold standard deviations for the key comparisons. At minimum, the paper should report:
- Mean +/- std of MAE across the 5 folds for E00 and P25.3.
- A paired test or bootstrap interval to confirm the 30.5% improvement is statistically significant.

### C2 [MINOR] — FSW data used only as "sanity check" but never actually checked

The paper includes 45 FSW rows from Matitopanum et al. (2024) and describes them as an "out-of-family sanity check" (line 140), but no sanity check is ever performed or reported. Either remove the claim or report what happens when the model is evaluated on FSW data.

### C3 [MINOR] — Missing multi-seed robustness on the full pipeline

The paper states at line 779-781 that the ranking of the top-5 experiments is stable across 5 random seeds but does not provide the data. Given the synthetic nature of the dataset, this is worth reporting in a table.

---

## Category 4: Writing / Presentation

### W1 [MINOR] — Abstract is too long

The abstract is 44 lines (lines 12-46). Journals typically want 150-300 words. This abstract is approximately 400 words and includes implementation details (file names, command lines) that belong in the methods section.

### W2 [MINOR] — Inconsistent equation numbering

Equation 1 is inline at line 65, equation 2-3 are at lines 166-167, and equation 4 is at lines 265-270. But the paper refers to "equation 4" at line 378 for the t_{8/5} formula. The thin-plate and thick-plate expressions are given as a single "equation 4" but are actually two separate equations. This should be equation 4a/4b or similar.

---

## Category 5: Figures / Plots

### F1 [MINOR] — Feature importance plot title editorialises

The title "Permutation Importance: Cooling Time t_{8/5} Outranks Heat Input" is a finding, not a description. Plot titles should be descriptive; the finding belongs in the caption text. Same issue with "H1 Refuted" and "H20 Refuted" in the other plot titles.

### F2 [MINOR] — Pred vs actual scatter could benefit from a residual subplot

The pred_vs_actual scatter shows the model tracks well overall, but the heteroscedasticity (variance increases with predicted value) is hard to assess. A residual plot or a plot of residual/actual vs actual would strengthen the diagnostic.

---

## Category 6: Reproducibility

### P1 [MINOR] — No requirements.txt or environment specification

The paper claims reproducibility via running Python scripts but does not specify the Python version, XGBoost version, scikit-learn version, or any other dependency versions. Given that XGBoost's tree building can produce numerically different results across versions, a `requirements.txt` or conda environment file is needed.

---

## Summary Table

| ID  | Category       | Severity | Summary |
|-----|----------------|----------|---------|
| M1  | Methodology    | CRITICAL | Circularity: features derived from same formula as data generator |
| M2  | Methodology    | MAJOR    | Transfer experiment uses different config than P25.3 winner |
| M3  | Methodology    | MINOR    | Keep/revert threshold bias not discussed |
| R1  | Results        | MAJOR    | Wrong count: paper says 38 candidates HAZ<=5mm, actual is 20 |
| R2  | Results        | MINOR    | build_dataset.py docstring says 609 rows, actual is 605 |
| R3  | Results        | MINOR    | Improvement decomposition numbers don't sum correctly |
| C1  | Completeness   | MAJOR    | No confidence intervals or significance tests |
| C2  | Completeness   | MINOR    | FSW "sanity check" claimed but never performed |
| C3  | Completeness   | MINOR    | Multi-seed robustness claimed but not shown |
| W1  | Writing        | MINOR    | Abstract too long |
| W2  | Writing        | MINOR    | Inconsistent equation numbering |
| F1  | Figures        | MINOR    | Plot titles editorialise findings |
| F2  | Figures        | MINOR    | Missing residual plot for heteroscedasticity check |
| P1  | Reproducibility| MINOR    | No requirements.txt or environment spec |

**CRITICAL: 1 | MAJOR: 3 | MINOR: 10**
