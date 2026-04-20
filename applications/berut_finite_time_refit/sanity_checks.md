# Sanity Checks — Phase 0.5

Computed by `e00_baseline_fit.py` on the digitised Bérut-Petrosyan-Ciliberto 2015 Fig 8 optimised-protocol data (10 points, see `data_sources.md` for caveats).

## 1. Quasistatic-limit residual

The largest-τ point is at τ = 40.0 s with ⟨Q_diss⟩ = 0.800 k_B T ± 0.150.
The Landauer floor is k_B T ln 2 ≈ 0.6931 k_B T.
Residual = ⟨Q_diss⟩ − k_B T ln 2 = +0.107 k_B T (+0.71 σ).

**Pass** if the residual is within ~2 σ and is still positive (Landauer is a lower bound).
Observed: +0.107 k_B T = +0.71 σ. PASS.

## 2. Power-law vs 1/τ (free α)

Fit:  ⟨Q_diss⟩(τ) = a + b / τ^α  with α as a free parameter.

Result:
- a = +0.3463 (Landauer floor predicted = 0.6931)
- b = +6.4493 (predicted B in 1/τ model = 8.2667)
- α = 0.7253 ± 0.3206  (95 % CI 0.097 – 1.354)

**Pass** if α = 1 is inside the 95 % CI (consistent with Proesmans 1/τ scaling).
Observed: α = 1 IS inside the CI → PASS.

## 3. Seed stability

Bootstrap of the B fit at three seeds:

| Seed | B (median) | 95 % CI | CI width |
|------|-----------|---------|----------|
| 42 | 8.269 | [7.376, 9.182] | 1.806 |
| 43 | 8.267 | [7.426, 9.123] | 1.697 |
| 44 | 8.279 | [7.369, 9.173] | 1.805 |

Across seeds the median moves by 0.013 (Monte-Carlo noise estimate at n_boot=2000 is ~0.040).

**Pass** if the cross-seed median spread is smaller than the within-seed CI width.
Observed: cross-seed spread = 0.013, within-seed CI = 1.806. PASS.


## Summary

Fitted B (canonical 1/τ, seed 42) = **8.269**  with 95 % CI [7.376, 9.182]
 = **0.838 π²** with 95 % CI [0.747 π², 0.930 π²].

Interpretation: the Schmiedl-Seifert symmetric-optimal prediction is B = π². The optimised-protocol data of the 2015 review should recover this (optimised ≈ Schmiedl-Seifert optimum). Our fitted value is 0.838 π², which is INCONSISTENT with π² — either the optimised protocol is not quite the Schmiedl-Seifert optimum, or the digitisation has a systematic bias.

**Critical data caveat:** these ten points are from the *optimised* protocol (black curve in arXiv:1503.06537 Fig 8), NOT the original Bérut 2012 Nature Fig 2 symmetric-protocol ten-point curve. For the project's central comparison — "simulated B_Bérut of the actual 2012 protocol vs empirical B" — we need Bérut 2012 Fig 2's non-optimised protocol data. Phase 0.5 verdict therefore depends on whether that data is reachable; see data_sources.md.
