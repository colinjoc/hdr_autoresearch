# HDR Active Queue

**Last updated**: 2026-04-13 (REFRESH-3 done; 45 new candidates across 9 clusters added to pipeline.md)
**Companion**: `pipeline.md` (216-candidate pool as of REFRESH-3)
**Order**: strict series — one project at a time, dependencies enforced via task tracker

## Top 15 (in execution order)

| # | Status | ID | Project | Score | Cluster | Task ID |
|---|---|---|---|---|---|---|
| 1 | **complete** | O-4 | Building permit pipeline (Austin 48d vs SF 605+d) | 30/30 | O | 18 |
| 2 | **complete** | W-5 | Heat-wave excess deaths predictor (night-time wet-bulb?) | 30/30 | W | 19 |
| 3 | **complete** | T-1 | Phantom highway traffic jams (smart-car suppression) | 30/30 | T | 20 |
| 4 | **complete** | EU-1 | Iberian blackout cascade prediction | 29/30 | EU | 21 |
| 5 | **complete** | IE-1 | Irish BER vs real home energy gap | 29/30 | IE | 22 |
| **REFRESH-1** | — | — | re-search candidate pool, update files | — | — | 23 |
| 6 | **complete** | IE-2 | Predict dangerous Irish radon homes | 29/30 | IE | 24 |
| 7 | queued | OSS-1 | What predicts open source project abandonment? (GH Archive/commits/stars/issues) | 30/30 | O | — |
| 8 | queued | ECON-1 | Do YC companies actually outperform non-YC at same stage? (Crunchbase) | 30/30 | O | — |
| 9 | queued | ECON-2 | What predicts which housing markets crash first? (permits/price-to-income/inventory) | 30/30 | O | — |
| 10 | queued | EU-3 | Xylella prediction in Spanish/Italian olive groves | 29/30 | EU | 25 |
| 11 | **complete** | IE-3 | DART punctuality cascade prediction | 29/30 | IE | 26 |
| 12 | **complete** | EU-6 | Iberian wildfire "very large fire" transition | 29/30 | EU | 27 |
| 13 | **complete** | T-3 | Flight delay propagation through network | 29/30 | T | 28 |
| **REFRESH-2** | — | — | re-search candidate pool, update files | — | — | 29 |
| 14 | **complete** | IE-7 | Dublin/Cork NO2 source attribution (REAL DATA, re-run from scratch) | 29/30 | IE | 30 |
| 15 | **complete** | T-9 | NYC congestion charge effect decomposition | 29/30 | T | 31 |
| 16 | **complete** | O-10 | Aircraft turnaround time mechanism (32 vs 71 min) | 29/30 | O | 32 |
| 17 | **complete** | E-4 | TOU non-shifters mechanism (75% don't shift) | 29/30 | E | 33 |
| 18 | **complete** | EU-2 | Po Valley fog persistence + aerosol coupling | 29/30 | EU | 34 |
| **REFRESH-3** | **complete** | — | 45 new candidates across 9 clusters; queue re-ranked | — | — | 35 |
| 19 | **paused** | OSS-1 | Paused after Phase 2.75 — E28 temporal-holdout ROC 0.54 + E25 E17-vs-E11 n.s.; needs denser 180d prior / 365d forward data before resume | 30/30 | O | — |
| 20 | queued | EU-29 | Predict where European aircraft lose GNSS — Baltic/Black Sea corridor | 30/30 | EU | — |
| 21 | queued | ECON-1 | Do YC companies actually outperform non-YC at same stage? (Crunchbase) | 30/30 | O | — |
| 22 | queued | ECON-2 | What predicts which housing markets crash first? | 30/30 | O | — |
| 23 | queued | W-20 | SWIO rapid-intensification cyclones (Gezani/Fytia) | 29/30 | W | — |
| 24 | queued | EU-30 | Which European imports face biggest CBAM cost shock | 29/30 | EU | — |
| 25 | queued | EU-31 | H5N1 bovine spillover — which EU dairy region next | 29/30 | EU | — |
| 26 | queued | Q-20 | EU AQD 2030 PM2.5 breaches — traffic vs wood vs transboundary | 29/30 | Q | — |
| 27 | queued | P-13 | Why did this SSW crash polar vortex and the next barely nudge | 29/30 | P | — |
| **REFRESH-4** | — | — | re-search candidate pool after 5 more completed projects | — | — | — |

## Per-project HDR phases (every project runs these)

1. **Phase 0** — Deep literature review (≥200 citations + textbook coverage), build `papers.csv`, `literature_review.md`, `knowledge_base.md`, `research_queue.md`, `design_variables.md`
2. **Phase 0.5** — Baseline audit: define the baseline algorithm + dataset + evaluation harness; record `E00` row in `results.tsv`
3. **Phase 1** — Model-family tournament (4+ families + linear sanity check); pick winner for Phase 2 starting point
4. **Phase 2** — 100-300+ pre-registered single-change experiments with Bayesian priors and KEEP/REVERT decisions
5. **Phase 2.5** — Interaction sweep: pairwise test of near-miss rejected changes
6. **Phase 2.75** — Adversarial results review by independent agent (reproducibility, cherry-picking, overclaiming, missing experiments). **Suggested experiments are mandatory — run them.**
7. **Phase 3** — `paper.md` with Detailed Baseline + Detailed Solution sections (per writing rules in feedback memory)
8. **Phase 3.5** — Adversarial paper review by independent agent (blind review of paper.md only). **Suggested experiments are mandatory — run them and update the paper.**
9. **Phase B** — Discovery sweep / inverse design / Pareto-front exploration over the trained surrogate
10. **Website summary** — `~/website/site/content/hdr/results/<slug>.md`, commit, push (only after `paper_review_signoff.md` exists)

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
