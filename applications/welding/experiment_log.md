# Experiment Log — Welding Parameter-Quality HDR Project

**Dates:** 2026-04-02 (Phase 0 lit review complete) → 2026-04-09 (Phases 0.5–3 complete)
**Project:** `/home/col/generalized_hdr_autoresearch/applications/welding/`
**Objective:** Predict Heat-Affected Zone (HAZ) half-width from welding
process parameters, then run Phase B inverse-design discovery to find
low-cost, low-heat-input parameter windows that keep the HAZ narrow.

This file is administrative only. Quantitative results live in
`results.tsv`; the scientific narrative is in `paper.md`.

---

## Phase 0 — Literature Review

**Status:** Complete before 2026-04-02 (see `literature_review.md`,
`papers.csv` (111 entries), `knowledge_base.md`, `research_queue.md`
(22 hypotheses)). Phase 0 deliverables were not modified during the
HDR loop.

---

## Phase 0.5 — Baseline Audit

**Started:** 2026-04-09
**Dataset choice:** No single open tabular welding parameter-quality
regression dataset could be located in this session. The aggregated
dataset noted in `knowledge_base.md` §6.5 could not be fetched. Attempts
to download Kaggle or Mendeley CSVs failed (Kaggle returned an HTML
auth page; Mendeley links were 12.7 GB HDF5 bundles). We therefore
constructed a synthetic dataset (`build_dataset.py`) from the Rosenthal
closed-form heat-flow solution (Rosenthal 1946; Easterling 1992 §3)
with 5–8% Gaussian measurement noise, seeded with 45 rows of real FSW
Ultimate Tensile Strength (UTS) measurements from Matitopanum et al.
(2024) PMC11012866. The synthetic nature of the dataset is flagged
explicitly as a limitation in `paper.md`.

**Data stats after `build_dataset.py`:**
- 605 rows total: 320 GMAW + 240 GTAW + 45 FSW (aluminium, held-out)
- HAZ half-width range 1.94 – 46.75 mm (steel subset, 560 rows)
- Columns: process, voltage_v, current_a, travel_mm_s, efficiency,
  thickness_mm, preheat_c, carbon_equiv, base_material, haz_width_mm,
  hardness_hv, cooling_t85_s, uts_mpa

**E00 baseline (XGBoost on six raw process features):**
- Features: voltage_v, current_a, travel_mm_s, thickness_mm,
  preheat_c, carbon_equiv (no physics derivation)
- 5-fold cross-validation MAE = **1.7152 mm**, R² = **0.9344**

---

## Phase 1 — Four-Way Tournament

| Exp | Family        | MAE   | R²     | Decision |
|-----|---------------|-------|--------|----------|
| E00 | XGBoost       | 1.7152| 0.9344 | baseline |
| T01 | LightGBM      | 1.6278| 0.9385 | **KEEP** |
| T02 | ExtraTrees    | 1.9721| 0.8960 | revert   |
| T03 | Ridge (linear)| 3.4656| 0.7715 | revert   |

Winner: **LightGBM (T01)**. The linear baseline sits at more than 2× the
boosted-tree MAE, which means the HAZ-width signal is not purely
log-linear in the raw parameters — tree methods are doing genuine
nonlinear work (the thin-/thick-plate regime switch alone is a
discontinuity that a linear model cannot capture).

---

## Phase 2 — HDR Loop (50 single-change experiments)

**Keep/revert rule:** `Δ < -max(0.005 mm, 0.01 × best_MAE)` required.

**Summary:** 4 KEEP, 46 REVERT.

Keeps:
- **E01** — add heat input (HI): LightGBM + HI, MAE 1.5730 (-8.6%)
- **E06** — add Rosenthal cooling time t_{8/5}: LightGBM + HI + t_{8/5}, MAE 1.3162 (-16.3%)
- **E20** — add HI/thickness: LightGBM + HI/thickness, MAE 1.2972 (-1.4%)
- **E34** — monotone(HI, t_{8/5}): XGBoost + HI + t_{8/5} + monotonicity, MAE 1.2788 (-1.4%)

Notable reverts:
- **E02–E05, E14, E23, E42–E43** — log / sqrt / cube-root / ×k_steel
  transforms of heat input gave zero improvement because LightGBM
  already learns those monotone nonlinearities from the raw feature.
- **E11, E12** — V/I and I/V ratios hurt: the transfer-mode signal
  (H4) was not strong in the synthetic data because the generator
  does not model arc transfer modes.
- **E41–E43** — Ridge regression on physics-informed features still
  produces MAE ≈ 3.2 mm, only modestly better than raw-features
  Ridge (3.47 mm). Tree methods are doing more than feature engineering.
- **E36** — aggressive monotonicity (I↑, v↓, thk↓) broke the model
  (MAE 1.6490) because it forced the thin-/thick-plate regime switch
  to disappear — the same HI value is compatible with narrow (thick-
  plate) and wide (thin-plate) HAZ zones.

---

## Phase 2.5 — Composition Retest and Cross-Process Transfer

**Six composition retests** stacking the strongest single-change wins:

| Exp   | Description                         | MAE    | Decision |
|-------|-------------------------------------|--------|----------|
| P25.1 | HI + t_{8/5} + monotone + n=600     | 1.2756 | revert   |
| P25.2 | HI + t_{8/5} + hi/thk + monotone    | 1.2760 | revert   |
| **P25.3** | **HI + t_{8/5} + log-target + monotone** | **1.1928** | **KEEP** |
| P25.4 | HI + t_{8/5} + depth=4 + monotone   | 1.2570 | revert   |
| P25.5 | HI + t_{8/5} + depth=4 + n=600      | 1.2321 | revert   |
| P25.6 | HI + t_{8/5} + lr=0.03 + n=800      | 1.2441 | revert   |

**P25.3** is the final winning configuration. Composing the log-target
transform (which reverted alone in E29) with the two physics features
and monotonicity produced a compound win of 30% relative to E00 — a
clear example of the "composition beats single-change" pattern the
methodology warns about.

**Cross-process transfer (H20 from `research_queue.md`):**

| Test                              | MAE     | R²      |
|-----------------------------------|---------|---------|
| P25.T1 — train GMAW, test GTAW    | 3.9475  | 0.3853  |
| P25.T2 — train GTAW, test GMAW    | 9.7611  | −0.7515 |
| P25.T3 — GTAW 5-fold CV baseline  | 0.7116  | 0.9694  |

The GMAW→GTAW gap is +3.2 mm absolute (+455 % relative). **H20 REFUTED
on this dataset.** Even with the universal heat-input feature, a model
trained on GMAW fails to generalise to GTAW because the two processes
sit in different thickness / preheat windows (thin plate is more
common in GTAW) and the thin-/thick-plate regime switch is
process-specific in practice.

**H1 explicit test:**

Linear regression on heat input alone → MAE 5.92 mm, R² 0.485.
**H1 REFUTED** on this dataset. Heat input by itself explains less than
half the variance in HAZ width — the thickness regime and preheat
modulate the scaling in ways a single scalar cannot capture.

---

## Phase B — Discovery

**Candidate generator:** 1760 tuples across 5 strategies (dense GMAW
grid, preheat sweep, thin-plate, low-heat-input, 800 Latin-hypercube
samples).

**Results:**
- 1760 candidates scored
- Pareto front (HAZ vs 1/travel) = 6 designs
- Minimum predicted HAZ = 3.71 mm
- Minimum heat input among candidates = 0.11 kJ/mm
- Zero candidates with HAZ < 3 mm (the training data minimum is
  1.94 mm, so this is a faithful model-ranging limit)
- Top 5 low-HI + HAZ ≤ 5 mm candidates all share the pattern:
  18–24 V, 100 A, 10–15 mm/s travel, 4–6 mm plate, ambient preheat.
  The model has independently recovered the textbook prescription
  for thin-plate low-heat-input GMAW.

---

## Phase 3 — Paper

**`paper.md`** drafted 2026-04-09. Sections:
Abstract → Introduction → Detailed Baseline → Detailed Solution → Methods
→ Results → Discussion → Conclusion → References.

---

## Test Suite

22 `pytest` tests covering the dataset, the `WeldingModel` class, the
HDR loop, and the Phase B discovery pipeline all pass in 1.5 seconds:

```
tests/test_dataset.py       9 passed
tests/test_hdr_loop.py      7 passed
tests/test_model.py         6 passed
total                      22 passed
```
