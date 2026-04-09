# Experiment Log — Paint Formulation HDR

This file records the administrative trivia that is deliberately excluded
from the published paper's methodology section: literature counts,
hypothesis counts, timing, and a narrative summary of each phase.

## Phase 0: Literature review

- `literature_review.md`: 372 lines, 7 themes
- `papers.csv`: 115 entries (textbooks, reviews, method papers, cross-disciplinary)
- `research_queue.md`: 26 hypotheses seeded
- `knowledge_base.md`: 260 lines of established results
- `design_variables.md`: 238 lines mapping 30+ formulation variables
- Saturation criteria (marginal information gain, citation-graph closure,
  textbook coverage) not yet fully satisfied — flagged as a Phase 0 limitation
  to be addressed on future iterations.

## Phase 0.5: Baseline audit

- **Dataset**: Borgert et al., "High-Throughput and Explainable Machine
  Learning for Lacquer Formulations", Zenodo DOI 10.5281/zenodo.13742098.
  Fetched 2026-04-09 with `curl` against the Zenodo API.
- **Sheet used**: `Evaluation/PURformance-Dataset.xlsx` (consolidated
  across the six experimental campaigns cs / i1 / i2 / i3 / i4 / rdm).
- **Rows after dropping NaN targets**: 65 of 65 raw rows.
- **Columns**: 4 composition (crosslink, cyc_nco_frac, matting_agent,
  pigment_paste), 1 process variable (thickness_um), 4 targets
  (scratch_hardness_N, gloss_60, hiding_power_pct, cupping_mm).
- **Baseline model**: XGBoost with default 5-feature raw inputs, 300 rounds.
- **Baseline 5-fold CV MAE** (experiment E00 in `results.tsv`):
  - scratch_hardness_N: 2.14 N
  - gloss_60: 10.87 gloss units (GU)
  - hiding_power_pct: 3.13 %
  - cupping_mm: 1.76 mm

## Phase 1: Tournament

- 4 families × 4 targets = 16 tournament runs.
- Winners (see `results.tsv` rows T01..T04 per target):
  - scratch_hardness_N → **Ridge** (MAE 1.83)
  - gloss_60 → **ExtraTrees** (MAE 10.29) [switched to XGBoost in Phase 2
    because a depth-7 XGBoost in experiment E109 was the final winner]
  - hiding_power_pct → **ExtraTrees** (MAE 2.45)
  - cupping_mm → **ExtraTrees** (MAE 1.66)

- Ridge winning scratch_hardness_N and ExtraTrees winning 3/4 targets
  validates both published HDR anti-patterns:
  - "Bagging beats boosting for small N (<100 samples)" — confirmed
  - "Linear baseline first — if Ridge wins, publish it" — confirmed for
    scratch hardness

## Phase 2: HDR loop

- **141 Phase 2 experiments** + **63 Phase 2.5 experiments** = **204 HDR
  experiments** total (see `results.tsv`).
- Decisions (Phase 2 + 2.5 combined):
  - KEEP: 11
  - REVERT: 191
  - ERROR: 2 (log-ratio features on Ridge with unclipped negative input —
    fixed by clipping in `model.py` `add_features`)
- Overall keep ratio: 5.4% (expected ~5–10% for mature HDR loops)
- Wall time per experiment: 0.3–3.0 seconds
- Wall time total: approximately 3 minutes for the full loop

### Per-target experiment counts and winners

| Target | KEEP | REVERT | Final family | Final features |
|---|---|---|---|---|
| scratch_hardness_N | 2 | 46 | Ridge (α=1) | `binder_pigment_ratio` |
| gloss_60 | 2 | 54 | XGBoost (depth=7, 300 rounds) | `log_thickness`, `thickness_x_matting` |
| hiding_power_pct | 3 | 46 | ExtraTrees (max_features=0.5) | `thickness_x_pigment` |
| cupping_mm | 4 | 45 | ExtraTrees | `cyc_x_matting`, `pvc_proxy` |

## Phase 2.5: extended loop

- Motivated by the per-target experiment count being only ~30–50 each
  after Phase 2 — below the "50 minimum" recommended in `program.md`.
- 63 additional single-change experiments covering multi-feature combos,
  cross-family retries, XGBoost depth refinement, ExtraTrees
  max_features, Ridge alpha sweep, and a kitchen-sink 7-feature set.
- Outcomes: 2 KEEP (hiding_power_pct max_features=0.5, cupping_mm
  cyc_x_matting + pvc_proxy), 61 REVERT.
- This confirms the Phase 2 exit state is near a local optimum for all
  four targets.

## Phase B: discovery

- 7785 candidates across 5 generation strategies (dense grid, high-gloss
  corner, low-VOC corner, high-hardness corner, Latin hypercube random).
- 4 predictions per candidate × batched inference → sub-second total
  screening time.
- Pareto fronts:
  - gloss × VOC: 24 non-dominated points
  - hardness × VOC: 9 non-dominated points
  - gloss × hardness: 33 non-dominated points
- Headline discovery: predicted ≥80 GU gloss at 73 g/L estimated VOC,
  which is inside the low-VOC waterborne regime reported in
  `knowledge_base.md` Section 5.2.

## Phase 3: paper

- `paper.md` drafted with the required section order: Abstract →
  Introduction → Detailed Baseline → Detailed Solution → Methods →
  Results → Discussion → Conclusion → References.
- All quantitative claims traceable to `results.tsv`,
  `winning_config.json`, and `discoveries/discovery_summary.json`.

## Tests

- Final test count: 23 tests across `tests/test_model.py`,
  `tests/test_evaluate.py`, `tests/test_hdr_loop.py`,
  `tests/test_phase_b.py`.
- All passing: `pytest tests/` → 23 passed in ~6 seconds.
