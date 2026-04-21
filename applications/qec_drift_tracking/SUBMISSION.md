# Submission Package — qec_drift_tracking

## Ready

- [x] `paper.md` — infrastructure-with-limitations draft acknowledging all Phase 2.75 methodology concerns inline
- [x] `references.bib` — 16 entries
- [x] `figures/fig1_phase_diagram.png` — synthetic-drift strict-win heatmap
- [x] `figures/fig2_mse_comparison.png` — PF vs baselines scatter
- [x] `results.tsv` — E01 synthetic sweep + E02 real Willow
- [x] `particle_filter.py` / `baselines.py` / `phase_diagram.py` / `willow_loader.py` / `e02_real_willow.py` / `make_figures.py`
- [x] `methodology_review.md` — Phase 2.75 MAJOR-REVISIONS verdict (internal; cited in paper)
- [x] `proposal_v3.md` — pre-registration
- [x] `data_sources.md` — Phase 0 Willow reachability record

## Pre-submission actions (user)

### Minimum to submit (Phys. Rev. Research or SciPost Codebases):

1. Address the two most damaging Phase 2.75 concerns before submission:
   - Replace PF Gaussian-surrogate likelihood with exact independent-Bernoulli (paper §4.3 item 2).
   - Run PF null-hypothesis test with 1e-5 prior on the synthetic sweep (§4.3 item 1).
2. Convert `paper.md` to LaTeX with pandoc + revtex/scipost template.
3. Zenodo archive of code + `results.tsv` + figures.

### Strong-submission (PRX Quantum realistic):

Close §4.3 items 1–5 (null-hypothesis test; exact-Bernoulli likelihood; faithful SW-MLE reimplementation per arXiv:2511.09491; faithful static-Bayesian TN+MCMC per arXiv:2406.08981; LCD reimplementation at Riverlane-protocol fidelity). Each ~1 week of focused work.

## HDR phase gates

| Phase | Status |
|-------|--------|
| −0.5 (scope) | PROCEED (via qec_ideation) |
| 0 (lit review, 268 citations, 103 hypotheses) | PASS |
| 0.25 (publishability, v3 reframe) | PROCEED |
| 0.5 (data + env + loader + particle filter + baselines + synthetic sweep + 1 real cell) | PASS (with caveats) |
| 1 (PF + baselines real run) | PASS (one cell, 5000/50000 shots, caveated) |
| 2.75 (methodology review) | MAJOR-REVISIONS → 2 fixes applied inline; 6 carried as open-validation items in paper §4.3 |
| 3 (paper draft) | written; honest-limitations framing |
| 3.5 (paper review) | pending |
| 4 (submission) | artifacts ready; §4.3 closure is the quality dial |

## Open-validation dial (from paper §4.3)

If the user closes each item, the paper moves up a venue tier:

| Items closed | Defensible venue |
|--------------|------------------|
| 0 (current draft) | arXiv + workshop track |
| 1, 2 | Phys. Rev. Research |
| 1, 2, 3, 4 | SciPost Physics (not Codebases) |
| 1, 2, 3, 4, 5 | PRX Quantum (plausible) |
| 1–8 | PRX Quantum (strong) |

## Reviewer transparency note

This project's Phase 2.75 methodology review (`methodology_review.md`, MAJOR-REVISIONS) was aggressive and identified real issues. Rather than silently fix or conceal, the paper draft publishes the reviewer's concerns as §4.3 open-validation items. This is unusual for a paper submission and may work for/against a real journal reviewer depending on venue culture — SciPost culture is more transparent-friendly; PRX Quantum less so.
