# gw_detectors — HDR

**Local**: `/home/col/generalized_hdr_autoresearch/applications/gw_detectors/`
**Venv**: `source venv/bin/activate` (after `python3 -m venv venv && pip install differometor`)
**Methodology**: see `../../program.md` (this file is the project-local instantiation).

---

## Scientific question

Can we systematically decompose the AI-discovered gravitational-wave detector topologies in the GWDetectorZoo to identify (a) which optical components carry the sensitivity gain, (b) what physical mechanisms are responsible, and (c) whether the simplified designs can be improved by post-hoc re-optimisation of the parameters that the original gradient-based search left in broad-plateau regions?

The Krenn-Drori-Adhikari Urania paper (Phys. Rev. X 2025) released 50 novel detector designs that improve on LIGO Voyager by up to 5.3× in strain sensitivity, but explicitly stated that the physical mechanisms behind many of them are not understood. This project aims to provide that understanding using systematic ablation, parameter sensitivity analysis, and minimal-design re-optimisation.

## Objective (Option C: Decomposition-Based)

Reverse-engineer the GWDetectorZoo's `type8/sol00` post-merger design (the strongest published candidate in the 800–3000 Hz band). Identify essential components, mechanism contributions, parameter sensitivity regimes, and produce a minimal-component design whose performance matches or exceeds the original after re-optimisation of broad-plateau parameters. Then survey the rest of the type8 family to test whether the decomposition generalises or whether multiple physical mechanism families coexist.

## Tools

- **Differometor** — JAX-based differentiable interferometer simulator. Standard published tool. Install: `pip install differometor`. Source: `https://github.com/artificial-scientist-lab/Differometor`.
- **GWDetectorZoo** — public dataset of 50 AI-discovered topologies. Source: `https://github.com/artificial-scientist-lab/GWDetectorZoo`. Format: PyKat `.kat` config files. A loader from `.kat` to Differometor's JSON schema is part of the Phase 0.5 baseline audit.
- **PyKat** — historical Python wrapper for the Finesse simulator. Used by the Zoo's original authors. Status: unmaintained, broken on Python ≥ 3.12. Not a hard dependency for this project, but useful for cross-validation if installable.

## Phase 0 status

Phase 0 begins on 2026-04-09 from a clean slate. A previous reconstruction attempt (built from artifacts after a 2026-04-09 source loss) is preserved at `~/archive/gw_detectors_reconstruction_2026-04-09.tar.gz`. None of its findings are taken as given — every claim must be verified directly via Phase 0 lit review and Phase 1 onward.

See `literature_review.md` for the running review, `papers.csv` for the citation database, `research_queue.md` for the current hypothesis list, `knowledge_base.md` for established results, and `design_variables.md` for the UIFO parameter space catalogue.

## Out of scope (for now)

- Per-experiment commit history of the lost reconstruction (preserved in archive only).
- The lost reconstruction's specific numerical claims (mechanism contributions, narrow/broad classifications, family taxonomy). These are starting hypotheses for Phase 0/1, not given facts.
- Other GWDetectorZoo type families (type0, type1, type3 etc.). Type8 is the post-merger headline family; once it is decomposed cleanly, the protocol can be extended.
