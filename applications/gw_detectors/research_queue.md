# Research Queue — gw_detectors

**RECONSTRUCTED SKELETON.** The original `research_queue.md` (~12 KB, ~28 hypotheses) was lost on 2026-04-09. This file is a small skeleton derived from the headlines preserved in `paper.md`. The full hypothesis list needs to be re-built from a fresh literature review.

## Open hypotheses (priority order)

### H01 — Apply the decomposition protocol to other type families
- **Type**: Option C, decomposition
- **Question**: Does the noise-suppression-vs-signal-amplification taxonomy generalise to type1, type3, type5? Or do other type families have distinct mechanisms?
- **Approach**: Repeat exp06–exp15 on a representative member of each type family.
- **Expected effort**: 1 week per type.

### H02 — Test mass / cavity finesse scaling for lower-frequency bands
- **Type**: Option C → Option B (forward optimisation)
- **Question**: Can the noise-suppression mechanism (light test mass + critical cavity coupling) be transferred to inspiral-band targets (10–100 Hz) by scaling the test mass and finesse?
- **Approach**: Build a parameterised version of the minimal design with mass and finesse as free parameters, optimise against an inspiral-band figure of merit.
- **Expected effort**: 1 week.

### H03 — Engineering reoptimisation
- **Type**: Option C, multi-objective
- **Question**: After re-optimising for strain sensitivity, can we further re-optimise the broad-plateau parameters (BS reflectivity, homodyne angle) for engineering metrics (alignment tolerance, drift sensitivity, manufacturability)?
- **Approach**: Multi-objective Pareto sweep.
- **Expected effort**: 1 week.

### H04 — Cross-validation with Finesse / OSCAR
- **Type**: Option C, validation
- **Question**: Does an end-to-end simulator (Finesse or OSCAR) confirm the dominant noise-suppression mechanism, or does it reveal a Differometor-specific approximation?
- **Approach**: Reproduce exp14 (minimal design @ BS=0.70) in Finesse and compare strain sensitivity within 5%.
- **Expected effort**: 2 weeks (incl. installation and learning curve).

### H05 — Lossy mirror analysis
- **Type**: Option C, robustness
- **Question**: How does the simplified design degrade under realistic mirror losses (10⁻⁵ per surface)?
- **Approach**: Add a per-surface loss parameter to evaluate.py and re-run exp14.
- **Expected effort**: a few days.

## Closed (resolved or moved to results)

- exp01–exp15 — see `experiment_log.md`
