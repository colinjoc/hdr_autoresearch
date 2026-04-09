# Experiment Log — gw_detectors

**Status**: Phase 0/0.5/1/2 in one session, 2026-04-09 (fresh restart).

This log records every measurement that contributed to `paper.md`. Every number in the paper is traceable to one of the experiments here. Every experiment is reproducible from the source files in this directory.

---

## Experimental setup

- **Working dir**: `/home/col/generalized_hdr_autoresearch/applications/gw_detectors/`
- **Venv**: `venv/` (Python 3.12, `pip install differometor pytest`)
- **Differometor**: cloned `--depth 1` from `github.com/artificial-scientist-lab/Differometor`
- **GWDetectorZoo**: cloned `--depth 1` from `github.com/artificial-scientist-lab/GWDetectorZoo`
- **Parser**: `kat_parser.py`, 286 lines, 15 pytest tests passing
- **Analysis driver**: `analysis.py` (cross-family) and `sol00_anatomy.py` (single-solution deep dive)

---

## E01 — kat parser TDD

**Goal**: Build a parser for the PyKat-format `.kat` files in the GWDetectorZoo. The canonical PyKat library is broken on Python ≥ 3.12 (uses removed `imp` and `distutils.spawn` modules). Differometor consumes a different JSON schema. There is no working modern loader for the Zoo files — we have to write one.

**Method**: Test-driven. Wrote `tests/test_kat_parser.py` first, with 15 tests asserting:
- 108 parameters parsed from sol00 (matches `const param0XXX` count in the file)
- 57 mirrors, 13 beamsplitters, 3 lasers, 0 squeezers, 1 directional bs (matches Zoo README)
- All `$paramXXXX` references resolve; `$fs` runtime variables are passed through
- The parser does not crash on any of the 25 type8 solutions

**Result**: 15 / 15 pass. The parser handles all 25 type8 solutions without errors.

**Lesson**: The `const param` count in the .kat file (108) does NOT match the Zoo README's stated count (120). The .kat file uses parameter IDs from 0000 to 0133 with 26 unused gaps. We trust the file, not the README, since the file is what gets simulated.

---

## E02 — Voyager baseline cross-check

**Goal**: Validate Differometor as an independent cross-check of the Zoo's `strain_baseline` column.

**Method**: Run Differometor's bundled `voyager()` setup in `df.run()`, sweep frequencies from 20 Hz to 5000 Hz, compute `noise / |signal|`, find the minimum.

**Result**:
- Differometor Voyager min strain noise: **3.764 × 10⁻²⁵ /√Hz** at **169.4 Hz**
- Published Voyager value [Adhikari 2020]: **3.76 × 10⁻²⁵ /√Hz** at **168 Hz**
- Agreement: within 0.1% in strain, within 1.4 Hz in frequency

**Lesson**: Differometor is a trustworthy independent simulator for Voyager. We can use it for sanity checks on other interferometer designs without running the canonical Finesse.

---

## E03 — Cross-family analysis (all 25 type8 solutions)

**Goal**: For every type8 solution, compute (a) structural inventory from the parsed `.kat` file, and (b) log-averaged improvement over Voyager in 800–3000 Hz from the Zoo's `strain.csv`.

**Method**: `analysis.py` driver. For each solution:
1. Parse the `.kat` file via `kat_parser.parse_kat()`
2. Count components by type, classify mirrors by reflectivity range
3. Read `strain.csv`, mask to 800–3000 Hz
4. Compute `exp(mean(log(strain_baseline / strain_best)))` over the band
5. Append a row to `results/per_solution.tsv`

**Result**: All 25 solutions analysed in ~1.5 seconds total (no Finesse needed). Improvement factors:

```
sol00: 4.05x  sol01: 3.36x  sol02: 2.68x  sol03: 2.22x  sol04: 1.78x
sol05: 1.30x  sol06: 1.28x  sol07: 1.14x  sol08: 1.14x  sol09: 1.12x
sol10: 1.12x  sol11: 1.11x  sol12: 1.11x  sol13: 1.10x  sol14: 1.06x
sol15: 1.06x  sol16: 1.04x  sol17: 1.03x  sol18: 1.01x  sol19: 1.01x
sol20: 1.01x  sol21: 1.01x  sol22: 1.00x  sol23: 1.00x  sol24: 1.00x

mean = 1.43x   median = 1.11x   max = 4.05x (sol00)   min = 1.00x (sol22-24)
```

**Lessons**:
- The type8 family is **highly skewed**: only sol00 and sol01 deliver substantial improvements; the bottom half is essentially break-even with Voyager.
- The lost reconstruction's claim "type8/sol00 = 3.12×" was wrong by ~25%. Sol00 is actually 4.05×.
- "All 50 solutions are superior to LIGO Voyager" is technically true but most by tiny margins.

---

## E04 — sol00 structural anatomy

**Goal**: Inventory every component in sol00 by reflectivity, mass, and connectivity. Find candidates for ablation.

**Method**: `sol00_anatomy.py`. Parse sol00.kat. For each mirror, resolve reflectivity / loss / tuning / mass against the parameter table. Bucket reflectivities into 9 ranges. List spaces > 100 m. Tabulate beamsplitter reflectivities.

**Result**: See `results/sol00_mirrors.tsv`, `results/sol00_spaces.tsv`, `results/sol00_param_histogram.tsv`. Highlights:

**Mirror reflectivity distribution (57 mirrors):**
- R < 0.001 (effectively transparent): **20** mirrors
- 0.001 ≤ R < 0.01: 4
- 0.01 ≤ R < 0.1: 7
- 0.1 ≤ R < 0.4: 2
- 0.4 ≤ R < 0.6 (BS-like): **6**
- 0.6 ≤ R < 0.9: 5
- 0.9 ≤ R < 0.99: 4
- 0.99 ≤ R < 0.999: **0** (gap)
- R ≥ 0.999 (perfect reflectors): **9**

**51% of mirrors are pinned to the two extremes** (29 of 57). These are candidates for removal.

**Beamsplitter inventory (13 declared):**
- B1_1, B1_2: R = 1.0000 (effectively perfect mirrors, not splitters)
- B2_3: R = 0.0000 (effectively transparent)
- B1_3: R = 0.8071 (real beamsplitter)
- B3_1: R = 0.3017 (real beamsplitter)
- B1_4, B2_1, B2_2, B3_2, B3_3, B3_4, B4_2, B4_3: R = 0.006 to 0.10 (highly asymmetric, near-transparent)

**Only 2 of 13 declared beamsplitters perform meaningful beam splitting.**

**Mass distribution (57 mirrors with explicit mass):**
- Range: 0.01 – 200.00 kg
- Median: **88.64 kg** (less than half of Voyager's 200 kg)
- At 200 kg exactly: 4 mirrors
- Below 50 kg (light test masses): **18**
- Below 1 kg: 9

**Cavity inventory (78 free spaces):**
- 6 spaces at 4-km-class lengths (3 at 3847 m, 3 at 3670 m): the 6 arm cavities
- 4 spaces at 276 m (medium-length connectors)
- 68 spaces at < 100 m (short connectors)

**Lesson**: Sol00 has **6 arm cavities, not 2** as the lost reconstruction claimed. The 4-km-class spaces form a more complex multi-arm geometry than a simple Michelson.

---

## E05 — Cross-family correlation analysis

**Goal**: Find structural features that predict improvement across the 25 type8 solutions.

**Method**: For each pair (feature_X, improvement_factor), compute Pearson r across the 25-row dataset.

**Result**:

| Feature | Pearson r |
|---|---|
| n_squeezers | **−0.497** |
| mirrors_R_near_zero | **+0.509** |
| n_directional_bs | −0.385 |
| n_mirrors | +0.316 |
| n_parameters | +0.236 |
| n_beamsplitters | +0.227 |
| mirrors_R_near_one | −0.185 |
| n_arm_spaces (>1km) | −0.093 |
| mirrors_R_interior | +0.079 |

**Lessons**:
1. **Squeezers correlate negatively (r = −0.50)**: more squeezer elements → worse improvement. The best solutions (sol00, sol01) have ZERO squeezers; the weakest carry 5–7. This contradicts conventional intuition about quantum-noise reduction.
2. **R-near-zero mirrors correlate positively (r = +0.51)**: more aggressively pruned mirrors → better improvement. The Urania optimisation rewards finding clean light paths over fitting more components into the topology.
3. The correlations together support the same picture: the type8 family's best solutions have the **simplest functional structure**, achieved by either removing squeezers entirely or pinning unused mirrors to transparent.

---

## What was NOT measured (and why)

- **Component-level ablation** (set a specific mirror to R=0 and recompute strain): would require either re-running Finesse (PyKat broken on 3.12) or building a Differometor `Setup` from the parsed kat (substantial engineering, signal-injection API not in the public Differometor examples). Deferred to future work.
- **Mechanism attribution** (what fraction of the 4.05× improvement comes from cavity coupling vs. test-mass mass vs. beamsplitter ratio): same blocker as above. Deferred.
- **Re-optimisation of broad-plateau parameters** (find parameters whose value can be perturbed by ±10% without measurable change, then sweep them for better local optima): same blocker. Deferred.
- **Cross-type analysis** (extend the structural decomposition to types 0, 1, 2, 3, 5, 6, 9, 10): straightforward extension of `analysis.py`, but scope-limited to type8 in this paper.
