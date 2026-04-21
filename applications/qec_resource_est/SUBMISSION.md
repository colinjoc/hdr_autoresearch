# Submission Package — qec_resource_est

Checklist for arXiv + PRX Quantum submission after Phase 4.

## Ready now

- [x] `paper_v3.md` — final manuscript with 30+ citations, 4 figures referenced, scope acknowledged
- [x] `references.bib` — 30+ entries, BibTeX-ready
- [x] `figures/fig1_codecap_crossover.png`
- [x] `figures/fig2_bb_vs_surface.png`
- [x] `figures/fig3_iter_ablation.png`
- [x] `figures/fig4_regime_map.png`
- [x] `results.tsv` — raw experimental data (21 rows across E00–E05)
- [x] `methodology_review.md` — Phase 2.75 MAJOR-REVISIONS verdict (internal record)
- [x] `paper_review.md` — Phase 3.5 MAJOR REVISIONS verdict (internal record)
- [x] `proposal_v3.md` — pre-registration document
- [x] `data_sources.md` — Phase 0 smoke-test record with tooling versions
- [x] Experiment scripts reproducible (`e00_benchmark.py`, `e00_azure.py`, `e01_bb_codecap.py`, `e02_bb_circuit.py`, `e03_surface_matched.py`, `e04_energy.py`, `e05_revisions.py`, `make_figures.py`)

## Pre-submission actions (user)

1. **Submit NVIDIA Academic Grant application** (deadline 2026-04-27). Template in `nvidia_grant_abstract.md`.
2. **Run A100 headline cell** once grant or cloud rental lands (proposal_v3 §9, one GPU-hour on any cloud A100 suffices).
3. **Convert `paper_v3.md` to LaTeX** using `pandoc -s paper_v3.md -o paper.tex --bibliography=references.bib` and PRX Quantum's revtex class.
4. **Create Zenodo archive** with `results.tsv`, scripts, `figures/`, `references.bib`. Record DOI in `paper.tex` Data Availability.
5. **Host code** at a public GitHub repo; update the "URL pending" in paper_v3 §Data and Code Availability.
6. **Run one more methodology reviewer pass** on paper_v3 (optional, Phase 3.5 round 2); likely ACCEPT given all major revisions addressed.

## Optional strengthening (would lift MINOR → near-ACCEPT at PRX Quantum)

- Rack-level CPU power meter to narrow the 60×–190× energy bracket to a point estimate.
- Stim sampler seed plumbing + 10-seed variance quantification.
- One GPU-surface spot-check via a workaround (e.g., custom pymatching fork with CUDA).
- LER-matched-compute-budget sweep (vary p for both decoders, report LER curves).

## Venue mapping

- **Primary:** PRX Quantum. §6 citations cover resource-estimation, qLDPC, decoders. §5.4 open issues list confirms scope.
- **Secondary:** Quantum (Verein). Open-access, QEC-heavy. Shorter turnaround.
- **Fallback:** arXiv + Phys. Rev. Research if PRX Quantum desk-rejects over scope.

## HDR phase gates cleared

| Phase | Artifact | Verdict |
|-------|----------|---------|
| −0.5 | `scope_check.md` (via qec_ideation) | PROCEED |
| 0 | `literature_review.md`, `papers.csv` (260 citations), `knowledge_base.md`, `design_variables.md`, `feature_candidates.md`, `research_queue.md` | PASS |
| 0.25 | `publishability_review.md` | PROCEED (tight) |
| 0.5 | `PHASE_0_5_PLAN.md`, `phase_0_5_findings.md`, `e00_benchmark.py`, `e00_azure.py`, `data_sources.md` | PASS (E00 + E00_azure) |
| 1 | `phase_1_findings.md`, `e01_bb_codecap.py`, `e02_bb_circuit.py`, `e03_surface_matched.py`, `e04_energy.py`, `observations.md` | PASS (5 experiments) |
| 2.75 | `methodology_review.md` | MAJOR-REVISIONS → addressed in E05/v2 |
| 3 | `paper.md` (v1) → `paper_v2.md` → `paper_v3.md` | Final draft ready |
| 3.5 | `paper_review.md` | MAJOR REVISIONS → addressed in paper_v3 |
| 4 | This `SUBMISSION.md`, `references.bib`, `figures/` | Ready for LaTeX conversion + submission |
