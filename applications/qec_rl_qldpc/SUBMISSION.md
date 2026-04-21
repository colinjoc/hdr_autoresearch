# Submission Package — qec_rl_qldpc

## Artifacts ready

- [x] `paper.md` (v1) + Phase 3.5 revisions pending
- [x] `references.bib` — 16 entries
- [x] `figures/fig1_gap_vs_nauty.png` — reward-compute scaling GAP vs nauty
- [x] `figures/fig2_pareto_scatter.png` — brute-force BB Pareto
- [x] `results.tsv` — E00–E03 raw data
- [x] `e00_per1_probe.py`, `e01_proxy_profile.py`, `e02_pareto_bb.py`, `e03_per1_rerun_and_correlation.py`, `make_figures.py` — reproducible scripts
- [x] `phase_0_5_findings.md` — PER-1 outcome + proxy adoption rationale
- [x] `methodology_review.md` — Phase 2.75 MAJOR-REVISIONS verdict
- [x] `proposal_v3.md` — pre-registered scope
- [x] `data_sources.md` — Phase 0 smoke test + tooling inventory

## Pre-submission actions (user)

1. Run `e03_per1_rerun_and_correlation.py` to completion; integrate PER-1 rerun data (warm-GAP measurements at gross-family polynomials) + proxy↔rank correlation coefficient into paper_v2.
2. Decide target venue: originally npj QI (Pareto-front framing). The Phase 2.75 reviewer recommends demoting to Quantum / SciPost (infrastructure paper framing) — the methodology contribution is stronger than the Pareto scope.
3. Fork Olle 2024 `qdx` or build a custom PPO wrapper using `qldpc` + pynauty — Phase 2 work, out of scope for this submission.
4. Convert paper.md → LaTeX via pandoc + revtex.
5. Zenodo archive of scripts + results.tsv + figures.

## HDR phase gates

| Phase | Status |
|-------|--------|
| −0.5 (scope) | PROCEED (via qec_ideation) |
| 0 (lit review 260+ citations) | PASS |
| 0.25 (publishability) | PROCEED |
| 0.5 (baseline + PER-1) | PASS with scope shift (proxy adopted) |
| 1 (experiments) | PASS (PER-1 profile + nauty profile + brute-force Pareto) |
| 2.75 (methodology) | MAJOR REVISIONS → E03 rerun in progress |
| 3 (paper draft) | v1 written; v2 pending E03 data |
| 3.5 (paper review) | pending v2 |
| 4 (submission) | artifacts ready; user to submit |

## Open items (Phase 2 future work)

- Proxy↔rank correlation validation (E03.2 output — being generated).
- Hx-only vs Hz-only proxy split for reward-hacking mitigation.
- Custom PPO/MCTS loop on top of `qldpc` + pynauty.
- Comparison against RASCqL, SHYPS, asymmetric-HGP at matched (n,k).
