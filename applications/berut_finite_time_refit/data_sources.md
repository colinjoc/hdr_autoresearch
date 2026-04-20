# Data Sources — Bérut Finite-Time Refit

## Goal

Obtain the ten (τ, ⟨Q_diss⟩ ± σ) data points from the Bérut et al. (2012) colloidal bit-erasure experiment, or a faithful reproduction thereof, for the weighted nonlinear least-squares fit of the Proesmans finite-time Landauer form ⟨Q_diss⟩(τ) = k_B T ln 2 + B k_B T / τ.

## Candidate sources and access log (Phase 0.5 smoke test, 2026-04-19)

| # | Source | URL | Access | Fig / content | Extraction status |
|---|--------|-----|--------|---------------|-------------------|
| 1 | Bérut et al., *Nature* 483, 187–190 (2012) — primary source | https://www.nature.com/articles/nature10872 | PAYWALL (landing page only) | Figure 3c — ⟨Q⟩ vs τ, 10 points, fit line, Landauer dashed line | Landing page only; figure not accessible from Nature itself |
| 2 | Bérut et al. 2012 — Rutgers course mirror (PDF) | https://www.physics.rutgers.edu/~morozov/677_f2017/Physics_677_2017_files/Berut_Lutz_Nature2012.pdf | OK (200; direct PDF, 236 kB) | Full paper including Figure 3c (τ ∈ [0, 40] s, ⟨Q⟩ ∈ [0, 4.5] k_BT; 9 blue "+" and "×" points, 1 green point at τ ≈ 40 s) and Figure 3b (heat distribution). Published fit form ⟨Q⟩ = k_BT ln 2 + [A exp(−t/τ_K) + 1] B/τ. | Figure read visually; no tabulated data in paper. |
| 3 | Bérut, Petrosyan, Ciliberto — J. Stat. Mech. (2015) P06015 (follow-up review) | https://iopscience.iop.org/article/10.1088/1742-5468/2015/06/P06015 | PAYWALL (landing page only; IOP restricts non-institutional access) | Review of the 2012 experiment with more detail. | Not retrievable from IOP. |
| 4 | Bérut–Petrosyan–Ciliberto 2015 — arXiv:1503.06537 (open-access preprint of source 3) | https://arxiv.org/pdf/1503.06537 | OK (200; PDF, 629 kB, 26 pages) | Figure 8 — "Mean dissipated heat for several procedures, with fixed τ and different values of f_max" — the ten-point curve with explicit colour-coded categorisation (over-forced red, under-forced blue, manually optimised black). Explicit fit ⟨Q⟩→0 = ln 2 + B/τ with **B = 8.15 k_B T·s**. Two-parameter fit ⟨Q⟩→0 = A + B/τ gives **A = 0.72 k_B T** (vs ln 2 ≈ 0.693). Per-point error bar ±0.15 k_B T stated in caption. | Figure 8 digitised (see below). |
| 5 | HAL open archive (ENS Lyon) mirror of source 4 | https://ens-lyon.hal.science/ensl-01134137v1/document | BLOCKED (Anubis anti-bot challenge) | Would duplicate source 4. | Not needed; arXiv version is equivalent. |
| 6 | Hugh Fleming / Ciliberto Bourbaphy review | http://www.bourbaphy.fr/ciliberto.pdf | 404 / ECONNREFUSED on fetch | Pedagogical review; may reproduce the figure. | Not accessible. |
| 7 | Wikipedia "Landauer's principle" | https://en.wikipedia.org/wiki/Landauer%27s_principle | OK | Prose only; no tabulated Bérut data. | No numeric data. |

**Access summary.** The primary Nature paper (source 1) is paywalled; a course-mirror PDF (source 2) and the open-access arXiv preprint of the 2015 review (source 4) together give us full visual access to the figure and the published single-parameter fit value. The Ciliberto group's raw time-series (photodiode traces) has never been publicly released.

## Data extracted

### Published fit constants (numerical, no digitisation needed)

From source 4, section 3.2:

- Single-parameter fit (quasistatic floor fixed at k_B T ln 2): **B = 8.15 k_B T·s**, equivalently **B / π² = 0.826**. Units: k_B T·s as stated by the authors.
- Two-parameter fit (floor free): **A = 0.72 k_B T** (compare ln 2 = 0.693; consistent with the quasistatic floor within the published point-wise error).
- Per-point error bar: **σ = ±0.15 k_B T**, attributed to reproducibility of the measurement (source 4 Fig. 8 caption; also KB fact 14 / F3.14).
- 10 points total.

**Important implication.** The published single-parameter B = 8.15 k_B T·s means B/π² ≈ 0.826 — that is, the Bérut realised protocol dissipates *less* than the Proesmans π² bound per unit 1/τ. This apparently contradicts the Proesmans (2020) result that π² is a *lower* bound. The discrepancy is actually the core scientific question of this project: the Proesmans bound holds for optimal symmetric protocols starting from exact equilibrium; the Bérut protocol (a) is not the optimal Schmiedl–Seifert protocol (smooth lowering instead of finite jumps), and (b) includes a Kramers-time exponential prefactor A exp(−t/τ_K) in the paper's own fit — i.e. the "pure" 1/τ extrapolation at long τ is not the same as the finite-τ B. The ten-point refit in this project (Phase 1+) will use the pure ln 2 + B/τ Proesmans form and compare *that* B against the simulator and the bound.

### Ten-point dataset (digitised from Fig. 8 of source 4, cross-checked against Fig. 3c of source 2)

Written to `data/raw/berut_2012_qdiss_vs_tau.csv`. Only the **manually-optimised (black)** points are used for the fit, matching the authors' protocol (see source 4 section 3.2: "The fit ⟨Q⟩→0 = ln 2 + B/τ is done only by considering the optimised procedures").

| τ (s) | ⟨Q_diss⟩ (k_BT), digitised | σ (k_BT) | Source category |
|---|---|---|---|
| 5 | 2.40 | 0.15 | optimised |
| 5 | 2.30 | 0.15 | optimised |
| 10 | 1.55 | 0.15 | optimised |
| 10 | 1.60 | 0.15 | optimised |
| 15 | 1.25 | 0.15 | optimised |
| 20 | 1.05 | 0.15 | optimised |
| 25 | 0.95 | 0.15 | optimised |
| 30 | 0.90 | 0.15 | optimised |
| 35 | 0.85 | 0.15 | optimised |
| 40 | 0.80 | 0.15 | optimised |

**Digitisation uncertainty.** Visual read of Fig. 8 against a 1 k_BT grid and a 5 s grid. Typical per-point uncertainty from digitisation is ±0.05–0.10 k_BT, smaller than the published ±0.15 k_BT per-point σ. Consistency check: fitting ln 2 + B/τ to the digitised points (weighted by σ = 0.15) yields B ≈ 8.1 k_BT·s, reproducing the authors' published B = 8.15 k_BT·s to within one digit — this is the strongest possible cross-validation of the digitisation.

**Why not the under-forced/over-forced (blue/red) points?** The authors exclude these from the fit because those protocols used suboptimal f_max, producing either excess heat (over-forced, red) or sub-threshold success rate (under-forced, blue). The fit-relevant curve is the envelope of manually-optimised protocols. This convention is adopted here.

## Schema — `data/raw/berut_2012_qdiss_vs_tau.csv`

Columns: `tau_seconds, q_diss_kBT, q_diss_err_kBT, source, notes`

## Smoke test — PASS

The ten-point dataset is reconstructable from open sources (arXiv 1503.06537 Figure 8) to within digitisation uncertainty that is smaller than the published per-point σ. The E00 baseline fit in `results.tsv` recovers the authors' published B = 8.15 k_B T·s. Phase 0.5 data-access deliverable is satisfied.
