# HDR Active Queue

**Last updated**: 2026-04-09
**Companion**: `pipeline.md` (full 140-candidate pool)
**Order**: strict series — one project at a time, dependencies enforced via task tracker

## Top 15 (in execution order)

| # | Status | ID | Project | Score | Cluster | Task ID |
|---|---|---|---|---|---|---|
| 1 | **complete** | O-4 | Building permit pipeline (Austin 48d vs SF 605+d) | 30/30 | O | 18 |
| 2 | **in_progress** | W-5 | Heat-wave excess deaths predictor (night-time wet-bulb?) | 30/30 | W | 19 |
| 3 | queued | T-1 | Phantom highway traffic jams (smart-car suppression) | 30/30 | T | 20 |
| 4 | queued | EU-1 | Iberian blackout cascade prediction | 29/30 | EU | 21 |
| 5 | queued | IE-1 | Irish BER vs real home energy gap | 29/30 | IE | 22 |
| **REFRESH-1** | — | — | re-search candidate pool, update files | — | — | 23 |
| 6 | queued | IE-2 | Predict dangerous Irish radon homes | 29/30 | IE | 24 |
| 7 | queued | EU-3 | Xylella prediction in Spanish/Italian olive groves | 29/30 | EU | 25 |
| 8 | queued | IE-3 | DART punctuality cascade prediction | 29/30 | IE | 26 |
| 9 | queued | EU-6 | Iberian wildfire "very large fire" transition | 29/30 | EU | 27 |
| 10 | queued | T-3 | Flight delay propagation through network | 29/30 | T | 28 |
| **REFRESH-2** | — | — | re-search candidate pool, update files | — | — | 29 |
| 11 | queued | IE-7 | Dublin/Cork NO2 source attribution | 29/30 | IE | 30 |
| 12 | queued | T-9 | NYC congestion charge effect decomposition | 29/30 | T | 31 |
| 13 | queued | O-10 | Aircraft turnaround time mechanism (32 vs 71 min) | 29/30 | O | 32 |
| 14 | queued | E-4 | TOU non-shifters mechanism (75% don't shift) | 29/30 | E | 33 |
| 15 | queued | EU-2 | Po Valley fog persistence + aerosol coupling | 29/30 | EU | 34 |
| **REFRESH-3** | — | — | re-search candidate pool, update files | — | — | 35 |

## Per-project HDR phases (every project runs these)

1. **Phase 0** — Deep literature review (≥200 citations + textbook coverage), build `papers.csv`, `literature_review.md`, `knowledge_base.md`, `research_queue.md`, `design_variables.md`
2. **Phase 0.5** — Baseline audit: define the baseline algorithm + dataset + evaluation harness; record `E00` row in `results.tsv`
3. **Phase 1** — Model-family tournament (4+ families + linear sanity check); pick winner for Phase 2 starting point
4. **Phase 2** — 100-300+ pre-registered single-change experiments with Bayesian priors and KEEP/REVERT decisions
5. **Phase 2.5** — Compositional retest of kept changes
6. **Phase 3** — `paper.md` with Detailed Baseline + Detailed Solution sections (per writing rules in feedback memory)
7. **Phase B** — Discovery sweep / inverse design / Pareto-front exploration over the trained surrogate
8. **Website summary** — `~/website/site/content/hdr/results/<slug>.md`, commit, push

Each project lives in `applications/<slug>/` with `paper.md`, `model.py`, `evaluate.py`, `hdr_loop.py`, `phase_b_discovery.py`, `papers.csv`, `results.tsv`, `tests/`.

## Refresh actions

After every 5 completed projects, run:

1. Spawn parallel cluster sub-agents (transport, energy, environment, weather, agriculture, operations, physical-sciences, Ireland, Europe-wide) with the same rubric and exclusions used in the original pool
2. Merge results into `pipeline.md` with new IDs
3. Update `active_queue.md`: keep remaining queue but reconsider order if new candidates score higher
4. Note in `pipeline.md` what changed and why

## Status legend

- `in_progress` — currently active, work happening now
- `queued` — waiting for predecessor to finish
- `complete` — paper.md written, website summary published, commit pushed
- `paused` — waiting on external dependency
- `parked` — abandoned (with reason)
