# Research Queue — gw_detectors

**Status**: Phase 2 in progress. Hypotheses are sorted by priority. Each is tested via a discrete experiment (E06+) that records its result in `results.tsv` and feeds back into `knowledge_base.md`.

Format per entry: hypothesis, evidence trail, prior (P that hypothesis holds before test), proposed experiment.

---

## Tested in this session (see experiment_log.md / results.tsv)

H08, H09 — see "Methodology / cross-validation" section below — TESTED in E02 (Voyager baseline reproduces).

---

## Decomposition hypotheses (Option C / type8/sol00 specific)

### H01 — Most components in type8/sol00 carry no useful optical work
**Hypothesis**: A majority of the 70+ declared components in `sol00` (mirrors + beamsplitters) sit at parameter extremes (R ≈ 0 or R ≈ 1) and contribute essentially no light-modulating behaviour.
**Prior**: 70%
**Experiment**: E04 (mirror reflectivity histogram) + E07 (beamsplitter R inventory).
**Status**: TESTED in E04, KEPT.

### H02 — Sol00 has arm cavities with sharply tuned mirror reflectivities
**Hypothesis**: At least one mirror in `sol00` has a reflectivity in the range that produces critical impedance matching for a 4-km Fabry-Perot cavity (R ≈ 0.99–0.9999), corresponding to the cavity-finesse claim in the original Krenn paper.
**Prior**: 75%
**Experiment**: E08 — find mirrors with R in (0.99, 0.9999) and check whether they sit at endpoints of the 6 long-arm spaces.
**Status**: pending.

### H03 — The beamsplitter angle distribution matches a standard Michelson backbone
**Hypothesis**: The 13 beamsplitters in `sol00` use either +45° or −45° angles (the canonical Michelson reflection orientation). Any other angle would indicate a non-Michelson geometry.
**Prior**: 90%
**Experiment**: E09 — angle histogram for beamsplitters.
**Status**: pending.

### H04 — Free spaces of length exactly 1.0 m are dummy connectors (not real distances)
**Hypothesis**: A large fraction of `sol00`'s 78 free spaces have a length of exactly 1.0 m, corresponding to PyKat's default value used when the optimiser had no reason to set a length.
**Prior**: 60%
**Experiment**: E10 — count spaces with length exactly 1.0 m vs other lengths.
**Status**: pending.

### H05 — Signal injections (`fsig`) are exclusively on free spaces, not on components
**Hypothesis**: All 26 `fsig` signal injection points in `sol00` target free-space connectors (the standard way to encode a strain perturbation in the kat language), not optical components.
**Prior**: 95%
**Experiment**: E11 — for each fsig, look up the target name and confirm it appears in the spaces list.
**Status**: pending.

### H06 — The 4 mirrors at exactly 200 kg form a structural subgroup (the "fixed Voyager-equivalent" boundary)
**Hypothesis**: The 4 mirrors with mass = 200.0 kg are connected to each other or to the input/output of the design, acting as fixed boundary conditions that the optimiser refused to perturb.
**Prior**: 50%
**Experiment**: E12 — list these mirrors and inspect their port connectivity.
**Status**: pending.

### H07 — Mirror mass and reflectivity are uncorrelated in sol00
**Hypothesis**: Mass and reflectivity are independent design parameters in the Urania UIFO, so a per-mirror correlation across `sol00` should be near zero.
**Prior**: 80%
**Experiment**: E13 — Pearson r between mass and reflectivity for the 57 mirrors.
**Status**: pending.

### H08 — The 6 arm cavities in sol00 are structurally identical
**Hypothesis**: The 6 arm-length spaces (3 at 3847 m + 3 at 3670 m) come in matched groups whose connecting mirrors have similar parameters, indicating a symmetric multi-arm geometry.
**Prior**: 65%
**Experiment**: E14 — for each arm space, find the bounding mirrors and compare their R values.
**Status**: pending.

### H09 — Sol00's parameter values are non-uniformly distributed (cluster at 0/1 for R-like, at 200 for mass-like)
**Hypothesis**: The 108 parameters in `sol00` show clustering at boundary values, not a uniform distribution. Specifically, > 30% of the R-like parameters should fall in the bins (0, 0.001) ∪ (0.999, 1).
**Prior**: 80%
**Experiment**: E15 — parameter histogram with explicit bin counts.
**Status**: pending.

---

## Cross-family hypotheses (across the 25 type8 solutions)

### H10 — Sol00 is dramatically the best of the type8 family (>2× the median improvement)
**Hypothesis**: The headline solution `sol00` improves Voyager by at least 2× more than the median type8 solution.
**Prior**: 60%
**Experiment**: E03 (cross-family analysis) + comparison.
**Status**: TESTED in E03, KEPT (sol00 = 4.05× vs median 1.11× → 3.6× ratio).

### H11 — Squeezer count anti-correlates with improvement across the family
**Hypothesis**: More squeezers in a Urania UIFO solution → worse strain improvement, contradicting the conventional "more squeezing is better" intuition.
**Prior**: 25% (counterintuitive, low prior)
**Experiment**: E05 (correlation analysis).
**Status**: TESTED in E05, KEPT (r = −0.497, strong support).

### H12 — Aggressive mirror-pruning correlates with improvement
**Hypothesis**: Solutions where the optimiser pinned more mirrors to R ≈ 0 (transparency) are stronger solutions.
**Prior**: 35%
**Experiment**: E05 correlation analysis.
**Status**: TESTED in E05, KEPT (r = +0.509, strong support).

### H13 — More parameters → more improvement
**Hypothesis**: Solutions with more `const param0XXX` declarations are better, because the optimiser had more degrees of freedom to exploit.
**Prior**: 65%
**Experiment**: E05 correlation.
**Status**: TESTED in E05, REVERTED (r = +0.236, weak — the finding is "marginally yes" not the strong predicted relationship).

### H14 — Number of arm cavities → improvement
**Hypothesis**: Solutions with more 4-km-class spaces (more arm cavities) have higher improvement.
**Prior**: 60%
**Experiment**: E05 correlation.
**Status**: TESTED in E05, REVERTED (r = −0.093, essentially no relationship).

### H15 — Type8 family solutions vary in laser count from 1 to 4
**Hypothesis**: Not every type8 solution uses the same number of lasers; the optimiser picked anything from 1 to 4 across the family.
**Prior**: 60%
**Experiment**: E16 — list per-solution laser count.
**Status**: pending.

### H16 — Beamsplitter count is roughly constant across the type8 family
**Hypothesis**: The number of declared beamsplitters in each type8 solution is consistently 9–13 (the natural UIFO grid count).
**Prior**: 50%
**Experiment**: E16 — per-solution BS count from analysis.py output.
**Status**: pending.

### H17 — Solutions with at least one directional beamsplitter (Faraday isolator) are systematically different from those without
**Hypothesis**: The presence of a `dbs` element in a solution correlates with a different operating regime than solutions without one.
**Prior**: 50%
**Experiment**: E17 — group by dbs presence/absence and compare improvement distributions.
**Status**: pending.

### H18 — The bottom-half solutions (sol13–sol24) all have improvement within 5% of each other
**Hypothesis**: The bottom half of the type8 family is essentially Voyager-equivalent, with improvement factors clustering near 1.0× ± 5%.
**Prior**: 70%
**Experiment**: E18 — std-dev of bottom-half improvement factors.
**Status**: pending.

### H19 — Among the 25 solutions, longer top-class spaces (>3500m) appear in identical lengths across solutions
**Hypothesis**: The 4-km-class space lengths are not optimised per-solution; they all use a small set of canonical values.
**Prior**: 75%
**Experiment**: E19 — collect all spaces > 3000 m across the 25 solutions, see how many distinct length values appear.
**Status**: pending.

### H20 — The number of signal injection points (`fsig`) varies with solution complexity
**Hypothesis**: Solutions with more components also have more `fsig` signal injection points.
**Prior**: 60%
**Experiment**: E20 — Pearson r between fsig count and total component count.
**Status**: pending.

### H21 — Sol00 vs sol01 differ in at least one categorical structural feature (not just parameter values)
**Hypothesis**: The two strongest type8 solutions are not parameter perturbations of each other — they have categorically different topologies (different component counts, different cavity arrangements).
**Prior**: 70%
**Experiment**: E21 — diff sol00 and sol01 component inventories.
**Status**: pending.

### H22 — Sol00 vs sol24 (best vs worst) differ by more than just the number of squeezers
**Hypothesis**: The best and worst solutions in the family differ structurally in multiple ways, not just squeezer count.
**Prior**: 80%
**Experiment**: E22 — full structural diff sol00 vs sol24.
**Status**: pending.

### H23 — Solutions with improvement > 2× share a common structural signature absent from the rest
**Hypothesis**: The top 4 solutions (sol00–sol03) all have at least one feature not present in the bottom 21.
**Prior**: 50%
**Experiment**: E23 — set-difference structural feature analysis.
**Status**: pending.

### H24 — Across all 25 solutions, every long arm space is exactly 4-km class
**Hypothesis**: There are no "almost-arm-length" spaces in the family; every long-baseline cavity is firmly in the 3500–4000 m range.
**Prior**: 65%
**Experiment**: E24 — collect all long spaces, plot distribution.
**Status**: pending.

### H25 — The unused parameter IDs (gaps in 0000–0133) are consistent across the family
**Hypothesis**: The 26 unused parameter IDs in sol00 are not random — they reflect structural choices the Urania optimiser pinned out across all type8 solutions.
**Prior**: 30%
**Experiment**: E25 — collect param IDs used in each of the 25 solutions, compare gaps.
**Status**: pending.

---

## Methodology / cross-validation hypotheses

### H_M1 — Differometor reproduces Voyager strain to within 0.1%
**Status**: TESTED in E02, KEPT (3.764e-25 at 169.4 Hz vs published 3.76e-25 at 168 Hz).

### H_M2 — The Zoo's `strain.csv` files are reliable ground truth
**Hypothesis**: The pre-computed strain spectra in each Zoo solution dir match what Finesse would compute from the corresponding `.kat` file (i.e. they were not corrupted in the publication process).
**Prior**: 85%
**Experiment**: difficult to verify without re-running PyKat+Finesse, which is broken on Python 3.12. Deferred.
**Status**: pending (assumed true for the rest of this work).
