# Reconstruction Notes — gw_detectors

## What happened

On 2026-04-09 the original `gw_detectors/` directory was destroyed by a bash loop that combined `mv` → `git subtree add` → `rm -rf` without per-iteration error checking. After the first failed iteration the loop continued and the `rm -rf` deleted the source repo from `/tmp` before the failure was visible. The git fetch step in `git subtree` had not yet run, so no objects from the source repo had been imported into the parent's `.git/objects` — there was no recovery path.

Lost from disk:
- 19 commits of git history
- 15 numbered experiment scripts (`exp01_voyager_baseline.py` … `exp15_cross_solution_survey.py`)
- `paper_draft.md` (the original draft)
- `experiment_log.md`, `knowledge_base.md`, `papers.csv`, `research_queue.md`, `design_variables.md`, `literature_review.md`
- The `Differometor/` and `GWDetectorZoo/` git submodule clones (these are external upstream repos and can be re-cloned)

## What was preserved

- The website summary at `~/website/site/content/hdr/results/gw-detectors.md` — full numerical results, mechanism breakdown, surprises, references
- The first ~50 lines of `paper_draft.md` (abstract, introduction, methods 2.1–2.3, results 3.1) preserved in agent context earlier in the session
- An Explore-agent report from earlier in the session that listed all 15 experiments by purpose, the 5 main lessons, several specific commit IDs, and the headline numbers

## What was reconstructed in this directory

| File | Status | Source of reconstruction |
|---|---|---|
| `paper.md` | **Reconstructed** | Verbatim abstract / intro / methods 2.1–2.3 from the preserved draft fragment; results, discussion, conclusion, and references rebuilt from the website summary and agent report |
| `tests/test_paper_invariants.py` | **Reconstructed** | Encodes every quantitative claim in the paper as an assertion. Run with `pytest -x` against a future re-implementation to verify. |
| `tests/test_evaluate.py` | **Reconstructed** | Skeleton for harness tests |
| `evaluate.py` | **Reconstructed** | Helper module that wraps Differometor (skeleton — actual Differometor API calls need verification against the live library) |
| `utils.py` | **Reconstructed** | Helpers for loading designs, saving results, formatting log entries |
| `exp01_voyager_baseline.py` … `exp15_cross_solution_survey.py` | **Reconstructed** | Each script implements the experimental protocol described in `paper.md` Methods §2.3 and Results §3.1–3.6. Differometor API calls are placeholder-faithful and need verification. |
| `experiment_log.md` | **Reconstructed** | Narrative reassembled from agent-report fragments and `paper.md` |
| `knowledge_base.md` | **Reconstructed** | 5 lessons + key facts from agent report and `paper.md` |
| `data_sources.md` | **Reconstructed** | Upstream URLs for Differometor and GWDetectorZoo |
| `papers.csv` | **Reconstructed (partial)** | The 22 references cited in `paper.md`. Original `papers.csv` had ~110 entries; the rest must be re-collected. |
| `research_queue.md`, `design_variables.md`, `literature_review.md` | **Skeleton** | Need to be re-built from scratch |

## What's missing and needs to be re-collected

- Full `literature_review.md` (original was ~40 KB across 7 themes)
- Full `papers.csv` (original was ~28 KB, ~110 references; reconstructed copy has the 22 cited in paper.md)
- Full `research_queue.md` (original ~12 KB with ~28 hypotheses)
- Full `design_variables.md` (original ~10 KB cataloguing UIFO parameter space)
- Full per-commit experiment narrative in `experiment_log.md` (original ~32 KB)

## Verification path before trusting any of the reconstructed scripts

1. Install Differometor: `pip install -e git+https://github.com/artificial-scientist-lab/Differometor.git`
2. Clone GWDetectorZoo: `git clone https://github.com/artificial-scientist-lab/GWDetectorZoo.git`
3. Run `pytest tests/test_paper_invariants.py -x` — every test should pass against the real Differometor + Zoo data
4. If tests fail, the reconstructed scripts have API drift; fix the API calls to match Differometor's actual interface
5. Re-run `exp01_voyager_baseline.py` and confirm strain noise minimum of 3.76 × 10⁻²⁵ /√Hz at 168 Hz (within 0.1%)

## Lessons promoted to `program.md` from this project

The decomposition-mode methodology (Phase 2 Variant: Decomposition Loop) and its 5 rules in `program.md` were synthesized from this project before the source was lost. Those rules are preserved at the parent repo level and apply to any future Option C HDR project.
