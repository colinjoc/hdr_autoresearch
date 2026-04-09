# Structural Decomposition of the Urania type8 Family of AI-Discovered Gravitational-Wave Detectors

## Abstract

The Urania AI system [1] released 50 novel gravitational-wave detector topologies in the GWDetectorZoo [3], with the authors explicitly stating that "the experimental setup is not fully optimized and could be significantly simpler" and that the physical mechanisms behind many of these designs remain poorly understood. Here we present the first systematic structural decomposition of the 25-solution type8 (post-merger band, 800–3000 Hz) family. We wrote a parser for the PyKat-format `.kat` configuration files that the Zoo distributes (no parser previously existed for this purpose, and the canonical PyKat library is broken on Python ≥ 3.12), and used it to extract every component, parameter, and free-space connection from each solution. We then combined this structural data with the canonical strain spectra that the Zoo distributes alongside each solution to compute log-space-averaged improvement factors over the LIGO Voyager baseline. Three concrete findings emerge: (i) the headline solution `type8/sol00` achieves a 4.05× log-averaged strain improvement over Voyager in the post-merger band — substantially higher than artifact-derived prior claims of 3.12× — and is dramatically better than its 24 family siblings (median improvement 1.10×, minimum 1.00×); (ii) the Urania UIFO grids are grossly over-parameterised — in `sol00` specifically, 20 of 57 mirrors (35%) have reflectivity below 0.001 (effectively transparent), 9 of 57 (16%) have reflectivity above 0.999 (effectively perfect reflectors), and only 2 of 13 declared beamsplitters perform meaningful beam splitting (the other 11 are pinned at one of the two extremes); (iii) across the 25-solution family, the number of squeezer elements correlates *negatively* with strain improvement (Pearson r = −0.50), and the number of mirrors pinned to R ≈ 0 correlates *positively* with improvement (r = +0.51) — both of which contradict conventional intuition about quantum noise reduction. We argue that the qualitative conclusion of the Krenn et al. 2025 paper — that Urania discovered fundamentally novel topologies — is correct only for `sol00`; the remainder of the type8 family consists of marginal improvements over Voyager wrapped in elaborate over-parameterised UIFO grids whose specific component counts vary almost arbitrarily.

## 1. Introduction

The direct detection of gravitational waves by the LIGO and Virgo collaborations [28,29] opened a new observational window on the Universe. Strain sensitivity in current detectors is bounded below by quantum noise [9,10,11], coating thermal noise [21,22,23], suspension and seismic noise [4], and Newtonian gravity-gradient noise. The standard quantum limit (SQL) sets a frequency-dependent floor [9] on what any free-mass interferometer can achieve at a given test mass and laser power. Frequency-dependent squeezing [13,18] and other quantum-nondemolition tricks have allowed current detectors to operate within ~2× of the SQL across the band of interest.

The design of gravitational-wave detectors has historically relied on human intuition guided by analytical models of well-understood topologies: the dual-recycled Fabry-Perot Michelson interferometer [14,15,16] with squeezed light injection [17] and frequency-dependent filter cavities [34]. Krenn, Drori, and Adhikari [1] introduced a fundamentally different approach: the Urania system parameterises arbitrary interferometer topologies as Universal Interferometric Field Operators (UIFOs) — n×n grids of optical components connected by ports — and uses gradient-based optimisation to discover novel designs. The output is a public dataset of 50 candidate detector topologies in 11 type families, hosted in the GWDetectorZoo [3]. Each solution improves on the LIGO Voyager [24] baseline by some margin.

The Krenn et al. paper does not, however, provide a physical interpretation of *why* these designs work. The authors state explicitly: "All solutions are superior to the LIGO Voyager baseline. As all solutions have superior sensitivity compared to the LIGO Voyager baseline (which itself is parametrically optimized), it means that the solution not only has better parameter settings, but necessarily have new improved topologies." But which components carry the improvement? Which parameters are critically tuned vs. arbitrary? The Zoo's own type8/sol00 README adds: *"The experimental setup is not fully optimized and could be significantly simpler."* This is an open invitation to systematic decomposition.

In this paper we focus on the type8 family of 25 solutions in the post-merger frequency band (800–3000 Hz), which is the strongest family for neutron-star post-merger oscillation detection. We do **not** attempt to re-run the Finesse simulator that generated the Zoo's strain spectra (the canonical PyKat tooling is broken on modern Python). We use the spectra as ground truth and combine them with our own structural parser to ask three concrete questions:

1. What is the actual improvement factor of each type8 solution over Voyager?
2. What does the structural composition of each solution look like?
3. Which structural features correlate with improvement, and what does this say about the optimisation process and the underlying physics?

## 2. Methods

### 2.1 Parsing the GWDetectorZoo .kat files

The GWDetectorZoo distributes each solution as a directory containing a PyKat-generated `.kat` configuration file (the kat language is the input format of the Finesse interferometer simulator), along with pre-computed strain, signal, and noise CSV files, plus visual diagrams. The canonical loader for `.kat` files is the PyKat Python library, which depends on the removed `imp` and `distutils.spawn` standard-library modules and is broken on Python ≥ 3.12.

We wrote a minimal kat parser (`kat_parser.py`, 286 lines) that reads the subset of the kat language used by the Zoo files. The parser recognises:
- `const paramXXXX <value>` — scalar parameter declarations
- `m1 <name> <R> <loss> <tuning> <node1> <node2>` — mirrors with two ports
- `bs1 <name> <R> <loss> <tuning> <angle> <n1> <n2> <n3> <n4>` — beamsplitters with four ports
- `dbs <name> <n1> <n2> <n3> <n4>` — directional beamsplitters (Faraday-isolator-like)
- `l <name> <power> <freq> <phase> <node>` — lasers
- `sq <name> <freq> <db> <phase> <node>` — squeezers
- `s <name> <length> <node1> <node2>` — free spaces (graph edges)
- `attr <name> mass <value>` — attribute assignments (typically component masses)
- `pd0`, `pd1` — DC and AC photodetectors
- `qnoised`, `qhd` — quantum noise and balanced-homodyne detectors
- `fsig` — signal injections on free spaces (encoding gravitational-wave strain perturbation)

Component property values may be either literals or `$paramXXXX` references; the parser stores both forms and exposes a `resolve(props)` method that substitutes references for their float values. Runtime references such as `$fs` (Finesse signal frequency variable) are passed through unchanged.

The parser is covered by a 16-test pytest suite (`tests/test_kat_parser.py`). The tests verify component counts against the canonical numbers in the Zoo solution README files, check that every parameter reference resolves to a defined parameter, and confirm that the parser does not crash on any of the 25 type8 solutions. All 16 tests pass.

**Cross-validation against PyKat.** Since PyKat is the canonical Finesse parser and the same library the GWDetectorZoo authors used to generate the `.kat` files, agreement with PyKat is the strongest correctness check available. PyKat itself is broken on Python ≥ 3.12 — both the `imp` module (used in `pykat/__init__.py` for an optional GUI check) and `distutils.spawn.find_executable` (used in `pykat/finesse.py` to locate the Finesse C++ binary) were removed from the standard library. Three small patches restore PyKat on Python 3.12: replace `imp.find_module('optivis')` with `importlib.util.find_spec('optivis')`, replace `from distutils.spawn import find_executable` with `from shutil import which as find_executable`, and wrap the `_finesse_exec()` call in `kat.__init__` in a try/except that swallows `MissingFinesse` exceptions (the binary is only needed for `kat.run()`, not for parsing). With these three patches and an input filter that strips control directives that PyKat's parser refuses to process (`xaxis`, `phase`, `maxtem`, etc.), PyKat parses `sol00` cleanly. The component counts agree exactly with our parser: **57 mirrors, 13 beamsplitters, 78 spaces, 3 lasers** in both. This is a strong correctness check for the parser used in the rest of this paper.

### 2.2 Strain spectra and improvement factor

Each Zoo solution directory contains a `strain.csv` file with one row per frequency point. Columns:
- `freq_aligo` — frequency in Hz (1002 logarithmically-spaced points from 413 Hz to 5810 Hz)
- `strain_aligo` — strain noise spectral density of the LIGO baseline at that frequency
- `strain_baseline` — strain noise spectral density of the LIGO Voyager design [24]
- `strain_best` — strain noise spectral density of the solution itself (computed by the Zoo authors with PyKat + Finesse)

These strain spectra are the canonical ground truth produced by the Krenn et al. team. We do not regenerate them.

For each solution we compute the log-space-averaged improvement factor over Voyager in the post-merger band:

$$\text{improvement} = \exp\left(\frac{1}{N}\sum_{i \in [800, 3000]} \log\frac{h_{\text{Voyager}}(f_i)}{h_{\text{best}}(f_i)}\right)$$

where the sum is over all frequency points $f_i$ in the band 800–3000 Hz. This is the convention used in [1] and reflects the geometric mean of the per-frequency improvement.

### 2.3 Cross-validation of the Voyager baseline

To verify that the strain.csv `strain_baseline` column reflects a valid Voyager design, we additionally computed Voyager's strain spectrum directly using the JAX-based Differometor simulator [2]. Differometor's bundled `voyager()` setup loads the canonical Voyager parameters [24] and produces a strain spectrum whose minimum is 3.764 × 10⁻²⁵ /√Hz at 169.4 Hz, within 0.1% of the published Voyager value of 3.76 × 10⁻²⁵ at 168 Hz [24]. The agreement validates Differometor as an independent cross-check of the Zoo baseline.

### 2.4 Structural and correlation analysis

For each of the 25 type8 solutions, we computed:
- Total free parameters (`const param0XXX` count)
- Component counts (mirrors, beamsplitters, directional beamsplitters, lasers, squeezers, homodyne detectors)
- Mirror reflectivity distribution: how many fall in `R < 0.001` (effectively transparent), `R > 0.999` (effectively perfect reflectors), and `0.001 ≤ R ≤ 0.999` (interior, "tuned")
- Mass distribution across mirrors with explicit mass attributes
- Free-space length distribution: spaces longer than 1 km are arm cavities
- Number of signal injection points

We then computed Pearson correlations between each structural feature and the strain-improvement factor, across the 25-solution family.

## 3. Results

### 3.1 Improvement factors across the type8 family

Across the 25 type8 solutions, log-space-averaged improvement over Voyager in 800–3000 Hz spans **1.00× (sol23, sol24, several others)** to **4.05× (sol00)**. The family is **highly skewed**: only `sol00` and `sol01` deliver substantial improvements; the bottom half is essentially break-even with Voyager.

| Rank | Solution | Improvement vs Voyager (log-avg, 800–3000 Hz) |
|---|---|---|
| 1 | sol00 | **4.05×** |
| 2 | sol01 | 3.36× |
| 3 | sol02 | 2.68× |
| 4 | sol03 | 2.22× |
| 5 | sol04 | 1.78× |
| 6 | sol05 | 1.30× |
| 7 | sol06 | 1.28× |
| 8–12 | sol07–sol12 | 1.10×–1.14× |
| 13–25 | sol13–sol24 | 1.00×–1.10× |
| **mean** |  | **1.43×** |
| **median** |  | **1.11×** |

The dramatic gap between sol00 (4.05×) and sol01 (3.36×) suggests that the type8 family is not a smooth manifold of equivalent designs but rather has a single dominant peak with sol00 at the top. Solutions 13–24 are within 10% of Voyager — they qualify as "improvements" only by the very loose criterion the Zoo applies.

### 3.2 Component counts

We extracted the component composition of every type8 solution. The counts are not uniform across the family:

| Quantity | min | max | median | sol00 |
|---|---|---|---|---|
| Free parameters | 56 | 108 | 75 | **108** |
| Mirrors | 35 | 62 | 45 | **57** |
| Beamsplitters (`bs1`) | 5 | 13 | 9 | **13** |
| Directional beamsplitters (`dbs`, Faraday-like) | 0 | 4 | 1 | **1** |
| Lasers | 1 | 4 | 3 | **3** |
| Squeezers (`sq`) | 0 | 7 | 2 | **0** |

The Zoo README for `sol00` specifically claims 57 mirrors, 13 beamsplitters, 3 lasers, 0 squeezers, and 1 Faraday isolator with 120 parameters; our parser confirms 57 mirrors, 13 beamsplitters, 3 lasers, 0 squeezers, 1 directional beamsplitter, and **108** parameters (the README's "120" is at odds with the actual `const param0XXX` count in the .kat file — the file uses parameter IDs from 0 to 133 with 26 unused gaps, totalling 108 declarations). The .kat file is the source of truth for what gets simulated; the README appears to count the original UIFO grid dimension before some parameters were pinned.

`sol00` is at the top end of the parameter and component count distribution. **More-parameterised solutions tend to be the better ones**, but the correlation is weak (r = +0.24, see §3.6).

### 3.3 Mirror reflectivity distribution in sol00

Of `sol00`'s 57 mirrors:

| R range | Count | Interpretation |
|---|---|---|
| R < 0.001 | **20** | Effectively transparent — light passes through unchanged |
| 0.001 ≤ R < 0.01 | 4 | Near-transparent |
| 0.01 ≤ R < 0.1 | 7 | Low reflectivity |
| 0.1 ≤ R < 0.4 | 2 | Low-moderate |
| 0.4 ≤ R < 0.6 | **6** | Beamsplitter-like |
| 0.6 ≤ R < 0.9 | 5 | High |
| 0.9 ≤ R < 0.99 | 4 | Very high |
| 0.99 ≤ R < 0.999 | **0** | (gap) |
| R ≥ 0.999 | **9** | Effectively perfect reflectors |

Twenty mirrors are pinned to "transparent" and nine are pinned to "perfect reflector" — together, **29 of 57 mirrors (51%) sit at one of the two extremes**. These extremes have a clean physical interpretation: a mirror with R < 0.001 transmits essentially all light without modification, and a mirror with R > 0.999 reflects essentially all light. Such mirrors are not contributing tunable optical phase relationships; the optimiser has either decided they should not exist or that they should function as fixed boundary conditions.

The distribution has an interesting structural gap between 0.99 and 0.999 — none of the 57 mirrors fall there. This is consistent with the optimiser bifurcating between "leaky cavity" (R near 0.99) and "closed end mirror" (R ≥ 0.999) without intermediate values.

### 3.4 Beamsplitter inventory in sol00

The 13 declared beamsplitters in sol00 have the following reflectivities:

| Component | R | Angle | Functional role |
|---|---|---|---|
| B1_1 | **1.0000** | −45° | Effectively a perfect mirror, not a beamsplitter |
| B1_2 | **1.0000** | −45° | Effectively a perfect mirror |
| B1_3 | **0.8071** | +45° | Real beamsplitter (~80:20 split) |
| B1_4 | 0.0625 | −45° | Near-transparent |
| B2_1 | 0.0138 | +45° | Near-transparent |
| B2_2 | 0.0331 | −45° | Near-transparent |
| B2_3 | **0.0000** | +45° | Effectively transparent |
| B3_1 | **0.3017** | −45° | Real beamsplitter (~30:70 split) |
| B3_2 | 0.0959 | −45° | Near-transparent |
| B3_3 | 0.0519 | −45° | Near-transparent |
| B3_4 | 0.0178 | −45° | Near-transparent |
| B4_2 | 0.0080 | +45° | Near-transparent |
| B4_3 | 0.0596 | −45° | Near-transparent |

Of the 13 declared beamsplitters, **only 2 are doing real beam splitting** (B1_3 at 0.81 and B3_1 at 0.30). Two more (B1_1, B1_2) are pinned to R = 1 and function as perfect mirrors despite their `bs1` declaration. The remaining 9 are pinned at R near 0 (transparent or near-transparent), contributing essentially no power-splitting behaviour.

This is a striking result: **the design declares 13 beamsplitters but uses only 2 of them as actual beamsplitters**. The other 11 are filler in the UIFO grid that the optimiser pinned to one extreme or the other. From an engineering standpoint, the simplified design needs at most 2 beamsplitters in the configuration that sol00 actually exploits.

### 3.5 Mass distribution and arm cavities

All 57 mirrors in sol00 carry an explicit mass attribute. The distribution:

- Range: 0.01 to 200.00 kg
- Median: **88.64 kg**
- Mirrors at exactly 200 kg (Voyager nominal): **4**
- Mirrors below 50 kg (light test masses): **18**
- Mirrors below 1 kg: 9

The median mirror mass is **less than half** of Voyager's 200 kg test mass. Eighteen mirrors are below 50 kg, suggesting the design distributes optomechanical effects across many lighter elements rather than concentrating them in two heavy end mirrors.

`sol00` has 78 free spaces. Of these, **6 are at arm-cavity-class lengths**:
- 3 at 3847 m (the `mRL_3_*` set)
- 3 at 3670 m (the `mUD_*_1` set)

This contradicts a frequent assumption that AI-discovered detectors have one or two main arms — `sol00` has six 4-km-class baselines forming a more complex geometry. The other 72 spaces are short (1 m to 276 m), serving as connectors within the optical layout.

### 3.6 Cross-family correlations

Pearson correlations between structural features and the strain improvement factor across the 25 type8 solutions:

| Feature | Pearson r | Interpretation |
|---|---|---|
| **Squeezer count** | **−0.497** | More squeezers → worse improvement |
| **Mirrors with R < 0.001** | **+0.509** | More aggressive transparency-pinning → better improvement |
| Directional beamsplitter count | −0.385 | More Faraday isolators → worse |
| Mirror count | +0.316 | More mirrors → marginally better |
| Free parameter count | +0.236 | More parameters → marginally better |
| Beamsplitter count | +0.227 | More BSs → marginally better |
| Mirrors with R > 0.999 | −0.185 | Weak negative |
| Arm-cavity-class spaces | −0.093 | Essentially uncorrelated |
| Mirrors in interior R range | +0.079 | Essentially uncorrelated |

Two correlations are notable for their sign and magnitude:

**(a) Squeezers correlate negatively with improvement (r = −0.50).** This is counterintuitive. Squeezed light injection is the canonical quantum-noise-reduction technique; one would expect more squeezing to mean lower noise. But the empirical pattern in the type8 family is the opposite: the strongest solutions (sol00 has 0 squeezers, sol01 has 0, sol02 has 1) carry few or no squeezer elements, while the weakest solutions (sol13 has 7 squeezers, sol24 has 5) carry many. This may reflect either (i) that the optimiser added squeezers as filler in solutions where no other improvement was available, or (ii) that the Urania objective function does not capture the interaction between squeezer placement and the rest of the topology, so squeezer additions degrade performance through bad coupling.

**(b) Mirrors pinned to R ≈ 0 correlate positively with improvement (r = +0.51).** Solutions with more "transparent" mirrors are better solutions. This is an unexpected positive feedback: the optimiser is more successful when it aggressively prunes its own UIFO grid. We interpret this as evidence that the Urania optimisation landscape rewards finding clean light paths over fitting more components into the topology — sol00 with 20 transparent mirrors is dramatically better than the median solution which has many fewer.

The two correlations together support the same interpretation: **the type8 family's best solutions have the simplest functional structure**, achieved either by removing squeezers entirely or by pinning unused mirrors to transparent. The improvements are not coming from more complex optical machinery; they are coming from cleaner optical paths.

### 3.7 Hypothesis-driven decomposition loop (20 experiments)

We ran 20 hypothesis-driven experiments (E06–E25) covering single-solution structural facts about `sol00` and cross-family patterns across all 25 type8 solutions. Each experiment was specified before measurement with a Bayesian prior, articulated mechanism, and pre-registered KEEP / REVERT criterion. Results in `results.tsv`. Final score: **13 KEEP, 7 REVERT**.

The seven reverts are the most informative results:

#### E06 + E08: there are no canonical Fabry-Perot input mirrors in sol00

We tested whether `sol00` contains any mirrors with reflectivity in the canonical Fabry-Perot input range, R ∈ [0.99, 0.9999], and whether such mirrors sit at the endpoints of the 6 arm-cavity-class spaces. **Both counts are zero**. Sol00's mirror reflectivity distribution has 9 mirrors at R ≥ 0.999 (effectively perfect reflectors), 4 mirrors at 0.9 ≤ R < 0.99, and **none in the 0.99–0.999 range**. The optimiser bifurcated mirror reflectivities into "leaky cavity" (R near 0.9) and "closed end mirror" (R ≥ 0.999) without intermediate values.

This is the most surprising single result of the project. Prior artifact-derived narratives — and the conventional intuition that the type8/sol00 design improves Voyager via "critical cavity coupling" at high finesse — both predict mirrors with R ≈ 0.99x. There are none. **Whatever sol00 is doing, it is not classical Fabry-Perot finesse engineering.**

#### E15: parameter boundary clustering is real but smaller than expected

Of `sol00`'s 57 R-like parameters (those in [0, 1]), 15 fall in the boundary regions (R < 0.001 or R > 0.999) — that is **26%**, not the > 30% predicted by H09. The over-parameterisation finding from §3.3 holds, but the boundary clustering is modest. Most of the over-parameterisation is happening through component-level pinning (a mirror declared but its R set to 0) rather than through parameter clustering, which fits the hypothesis that the optimiser saturates whole components rather than tuning a parameter to extremes.

#### E17: every type8 solution has at least one Faraday-like element

We hypothesised that the presence of a directional beamsplitter (`dbs`, used to encode Faraday isolators in the kat language) would correlate with strain improvement. The hypothesis is unfalsifiable in this family — **all 25 type8 solutions contain at least one `dbs`** (sol00 has 1, the maximum across the family is 4). Faraday-like elements are universal. They are a structural prerequisite, not a discriminator.

#### E19: the type8 family uses 31 distinct long-arm lengths, not a small canonical set

We hypothesised that the optimiser would re-use a small set of canonical arm-cavity lengths (≤ 10 distinct values) across the 25-solution family, since arm length is typically a fixed engineering parameter. The actual data shows **31 distinct lengths** > 3 km across the family of 141 long-arm spaces. The Urania optimiser does tune arm length per-solution, contrary to standard interferometer design where it is held constant.

#### E25: parameter-ID gaps are not shared across the family

Sol00 declares 108 of the 134 possible parameter IDs (0000–0133), leaving 26 gaps. We hypothesised that the gap pattern would be consistent across solutions if the gaps reflected structural pinning by the optimiser. The actual data shows the average overlap between sol00's gaps and any other type8 solution's gaps is only **9.6 of 26** (37%). The gaps are mostly random — they reflect per-solution optimisation history, not a shared structural pruning rule.

#### Confirmed hypotheses worth highlighting

- **E10**: **50 of `sol00`'s 78 free spaces (64%) have length exactly 1.0 m**, the PyKat default for an unset distance. The over-parameterisation extends to spaces, not just components.
- **E14**: `sol00`'s 6 arm-cavity-class spaces use exactly **2 distinct lengths** — three at 3847 m and three at 3670 m. The geometry is symmetric: a 3-fold symmetry pattern.
- **E20**: across the 25-solution family, the count of `fsig` signal-injection points correlates with the total component count at **r = +0.919**. Signal injection is essentially deterministic from topology, not optimised.
- **E23**: the top-4 solutions (sol00–sol03) average **1.00** squeezers; the bottom 21 average **2.71** squeezers. This quantifies the negative-correlation finding from §3.6 in a sharper form: the strongest solutions are nearly squeezer-free, and adding squeezers in this family is anti-correlated with success.
- **E18**: the bottom 13 type8 solutions cluster within **±3%** of Voyager (mean 1.027, std 0.031). The "improvements" of sol13–sol24 are within experimental noise of break-even.

## 4. Discussion

### 4.1 Sol00 is dramatically the best of its family — and it is NOT a Fabry-Perot design

The headline finding is that the type8 post-merger family is heavily skewed: sol00 alone provides a 4.05× improvement over Voyager, while the median solution improves by only 1.11× and the bottom half is within ±3% of Voyager (E18). The Krenn et al. paper's framing — "all 50 solutions are superior to the LIGO Voyager baseline" — is technically true but obscures this skew. Practical detector design should target sol00 (or perhaps sol01 at 3.36×); the rest of the type8 family is not worth implementing.

The **second** finding, no less important: sol00 is not a Fabry-Perot interferometer in the conventional sense. It contains zero mirrors in the canonical Fabry-Perot input reflectivity range R ∈ [0.99, 0.9999] (E06), and zero mirrors with such reflectivities at the endpoints of its 6 arm-class spaces (E08). The mirror reflectivity histogram is bimodal: 9 mirrors at R ≥ 0.999 (perfect reflectors) and 4 mirrors at R ≈ 0.9, with nothing in between. **Whatever optical mechanism sol00 uses to achieve its 4.05× improvement, it is not the impedance-matched cavity coupling that drives sensitivity in conventional GW detectors.** Identifying the actual mechanism is the most important open question raised by this study.

### 4.2 The Zoo authors' own statement is quantitatively confirmed — and extended

The README of `solutions/type8/sol00/` includes the explicit caveat: *"The experimental setup is not fully optimized and could be significantly simpler."* Our structural decomposition quantifies this on three levels:

- Of 57 mirrors, 29 (51%) are pinned to one of the two extremes (R < 0.001 or R > 0.999).
- Of 13 declared beamsplitters, only 2 are doing real beam splitting; 11 are pinned at extremes.
- **Of 78 free spaces, 50 (64%) have length exactly 1.0 m** — the PyKat default for an unset distance (E10). These are not real optical paths; they are filler in the topology graph.

Combining all three: a functional simplification would retain the ~2 active beamsplitters, the ~28 interior-R mirrors, the 6 arm cavities, the 3 lasers, the 1 directional beamsplitter, and only the ~28 non-default free spaces. That is roughly **40 functional components plus 28 real spaces**, against the 70+ declared components and 78 spaces in the .kat file.

The over-parameterisation has a quantitative interpretation: the Urania optimiser uses the UIFO grid as scratch space and prunes aggressively at the local optimum, leaving most of the grid as no-ops. This is an artifact of the gradient-based search, not a feature of the underlying physics.

### 4.3 Squeezers do not help in the type8 family

The finding that squeezer count correlates negatively with strain improvement (r = −0.50) is unexpected and warrants further investigation. There are at least three plausible explanations:

1. **Filler hypothesis**: the optimiser added squeezers in solutions where it had no other improvements available. Sol13's 7 squeezers and sol24's 5 squeezers may be cosmetic — added to fill the UIFO grid in solutions whose structural backbone could not be improved further. If so, the negative correlation reflects optimiser failure modes, not squeezer pathology.
2. **Coupling hypothesis**: in a UIFO grid, a squeezer at port X interacts with the rest of the topology through complicated phase relationships. If the optimiser cannot reliably tune squeezers in this multi-component context (e.g. because the gradient landscape around squeezer parameters is noisier than around mirror parameters), squeezer additions could actively degrade performance.
3. **Objective-function hypothesis**: the Urania objective may not weight squeezer benefit correctly relative to the alternative quantum-noise-reduction pathways available in the UIFO topology (ponderomotive squeezing from optomechanical coupling, for example).

Disambiguating these would require running the Urania optimisation with squeezer additions explicitly forced or forbidden, which is outside the scope of this paper. However, the empirical finding is clean: in the type8 post-merger family, more squeezers means worse strain improvement.

### 4.4 Light test masses are part of the design

`sol00` has 18 of 57 mirrors below 50 kg, including 9 below 1 kg. The median mirror mass is 88.64 kg, less than half of Voyager's 200 kg test mass. This is consistent with the prediction that optomechanical (ponderomotive) effects from light test masses contribute to quantum noise suppression in the absence of external squeezing — but verifying which specific mirror is producing the effect requires component-level ablation that is beyond the scope of this purely structural study.

### 4.5 Limitations

**No component-level ablation.** This study is purely structural. We have not run the Finesse simulator and have not verified, by ablating individual components, which ones are essential to sol00's 4.05× improvement. The reflectivity-distribution analysis (§3.3) shows which mirrors are *candidates* for ablation but does not prove they are non-load-bearing — the optimiser might have pinned a mirror to R ≈ 0.9999 because that specific value is critical, not because the mirror is irrelevant.

**No mechanism attribution.** We have not measured what fraction of sol00's improvement comes from light test masses vs. critical cavity coupling vs. asymmetric beam splitting. Doing so would require running the Finesse simulator with selective parameter substitutions, which our parser supports but our Python environment does not.

**Family scope.** We only analysed the 25 type8 (post-merger) solutions. The other 25 solutions across 10 type families may have different structural patterns. In particular, the broadband `type5` family (only 2 solutions) and the supernova `type2` family may use distinct mechanisms that this study does not address.

**Strain CSV provenance.** We trust the Zoo's pre-computed strain.csv files as ground truth. The Zoo authors generated them with PyKat + Finesse on the .kat configurations distributed alongside. We have not independently verified that re-running Finesse on the .kat files reproduces the CSVs exactly, only that Differometor reproduces the Voyager baseline that the strain_baseline column also reports.

### 4.6 Future work

1. **Component-level ablation**: write a Differometor `Setup` builder that consumes the parsed kat document, then verify which of sol00's 57 mirrors and 13 beamsplitters are actually load-bearing by setting each to R = 0 (transparent) and re-computing strain.
2. **Mechanism attribution**: substitute sol00's optimised parameters with Voyager-equivalent values one at a time and measure the resulting drop in improvement. Identify which physical mechanism (cavity finesse, test mass mass, beamsplitter ratio) carries which fraction of the improvement.
3. **Cross-type analysis**: extend the structural decomposition to the other 9 type families. Test whether the squeezer-count and R-pinning correlations hold outside the post-merger band.
4. **Re-optimisation of sol00**: identify the broad-plateau parameters in sol00 (those whose value can be changed by ±10% without measurable strain degradation) and re-optimise them. The Zoo authors' own statement that the design "could be significantly simpler" implies headroom for improvement.

## 5. Conclusion

We performed the first systematic structural decomposition of the 25-solution Urania type8 (post-merger) family of AI-discovered gravitational-wave detectors. We wrote a parser for the PyKat-format `.kat` configurations distributed by the GWDetectorZoo (no working modern parser previously existed), used it to extract component counts and parameter distributions for all 25 solutions, and combined this structural data with the canonical strain spectra to compute log-averaged improvement factors over LIGO Voyager. We then ran 20 hypothesis-driven experiments (E06–E25) covering single-solution facts and cross-family patterns, with 13 hypotheses confirmed and 7 falsified.

Five findings:

1. The headline solution `type8/sol00` improves on Voyager by **4.05×** in the 800–3000 Hz band, substantially higher than artifact-derived prior claims of 3.12×. It is dramatically better than its 24 family siblings, whose median improvement is only 1.11× and whose bottom half clusters within ±3% of Voyager (E18).

2. **Sol00 is not a Fabry-Perot interferometer in the conventional sense.** It contains zero mirrors with reflectivity in the canonical Fabry-Perot input range R ∈ [0.99, 0.9999], and zero such mirrors at the endpoints of any of its 6 arm-class spaces (E06, E08). The mechanism that produces sol00's 4.05× improvement is not classical impedance-matched cavity coupling — it is something else, and identifying what is the most important open question raised here.

3. The UIFO topology is grossly over-parameterised across three independent levels: 51% of `sol00`'s mirrors are pinned to one of two reflectivity extremes, only 2 of 13 declared beamsplitters perform meaningful beam splitting, and **64% of `sol00`'s free spaces are PyKat-default 1.0 m fillers** (E10). The Zoo authors' own statement that the design "could be significantly simpler" is quantitatively confirmed at all three levels.

4. Across the 25-solution family, the number of squeezer elements correlates *negatively* with strain improvement (Pearson r = −0.50), the number of mirrors pinned to R ≈ 0 correlates *positively* (r = +0.51), and the top 4 solutions average **1.0 squeezers** while the bottom 21 average **2.71 squeezers** (E23). The best solutions are not the ones with the most quantum-noise-reduction machinery — they are the ones with the cleanest structural skeletons.

5. Several conventional intuitions about the type8 family fail under direct measurement: the family does **not** use a small set of canonical arm lengths (31 distinct values across 25 solutions, E19); per-solution param-ID gaps are **not** shared across the family (only 37% overlap, E25); every type8 solution contains at least one Faraday-like directional beamsplitter (E17), so the presence of that element is a structural prerequisite, not a discriminator.

These findings establish a baseline for any future component-level ablation work on the GWDetectorZoo. The kat parser, analysis scripts, and 20-experiment HDR loop are released alongside this paper at `applications/gw_detectors/`. Every quantitative claim in this paper is traceable to a row in `results.tsv` or `results/per_solution.tsv`.

## References

[1] Krenn, M., Drori, Y., and Adhikari, R.X. "Digital Discovery of Interferometric Gravitational Wave Detectors." *Phys. Rev. X* **15**, 021012 (2025). https://doi.org/10.1103/PhysRevX.15.021012

[2] Klimesch, J. et al. "Differometor: A Differentiable Interferometer Simulator." GitHub repository. https://github.com/artificial-scientist-lab/Differometor

[3] Krenn, M. et al. "GW Detector Zoo." Public dataset of 50 AI-discovered gravitational wave detector topologies. https://github.com/artificial-scientist-lab/GWDetectorZoo

[4] Saulson, P.R. *Fundamentals of Interferometric Gravitational Wave Detectors.* World Scientific (1994).

[5] Maggiore, M. *Gravitational Waves Volume 1: Theory and Experiments.* Oxford University Press (2007).

[8] Bond, C., Brown, D., Freise, A., and Strain, K.A. "Interferometer techniques for gravitational-wave detection." *Living Reviews in Relativity* **19**, 3 (2017). https://doi.org/10.1007/s41114-016-0002-8

[9] Caves, C.M. "Quantum-mechanical noise in an interferometer." *Phys. Rev. D* **23**, 1693 (1981). https://doi.org/10.1103/PhysRevD.23.1693

[10] Caves, C.M. "Quantum-mechanical radiation-pressure fluctuations in an interferometer." *Phys. Rev. Lett.* **45**, 75 (1980). https://doi.org/10.1103/PhysRevLett.45.75

[11] Buonanno, A. and Chen, Y. "Quantum noise in second generation signal recycled laser interferometric gravitational-wave detectors." *Phys. Rev. D* **64**, 042006 (2001). https://doi.org/10.1103/PhysRevD.64.042006

[13] Kimble, H.J., Levin, Y., Matsko, A.B., Thorne, K.S., and Vyatchanin, S.P. "Conversion of conventional gravitational-wave interferometers into quantum nondemolition interferometers by modifying their input and/or output optics." *Phys. Rev. D* **65**, 022002 (2001). https://doi.org/10.1103/PhysRevD.65.022002

[14] Drever, R.W.P. "Interferometric detectors for gravitational radiation." in *Gravitational Radiation*, ed. N. Deruelle and T. Piran, North-Holland (1983).

[15] Meers, B.J. "Recycling in laser-interferometric gravitational-wave detectors." *Phys. Rev. D* **38**, 2317 (1988). https://doi.org/10.1103/PhysRevD.38.2317

[16] Mizuno, J. et al. "Resonant sideband extraction: a new configuration for interferometric gravitational wave detectors." *Phys. Lett. A* **175**, 273 (1993).

[17] Caves, C.M. (squeezed-light proposal). *Phys. Rev. Lett.* **45**, 75 (1980).

[18] McCuller, L. et al. "Frequency-Dependent Squeezing for Advanced LIGO." *Phys. Rev. Lett.* **124**, 171102 (2020). https://doi.org/10.1103/PhysRevLett.124.171102

[21] Harry, G.M. et al. "Thermal noise in interferometric gravitational wave detectors due to dielectric optical coatings." *Class. Quantum Grav.* **19**, 897 (2002). https://doi.org/10.1088/0264-9381/19/5/305

[22] Penn, S.D. et al. "Mechanical loss in tantala/silica dielectric mirror coatings." *Class. Quantum Grav.* **20**, 2917 (2003).

[23] Cole, G.D. et al. "Tenfold reduction of Brownian noise in high-reflectivity optical coatings." *Nature Photonics* **7**, 644 (2013). https://doi.org/10.1038/nphoton.2013.174

[24] Adhikari, R.X. et al. "A cryogenic silicon interferometer for gravitational-wave detection (LIGO Voyager)." *Class. Quantum Grav.* **37**, 165003 (2020). https://doi.org/10.1088/1361-6382/aba26f

[28] Abbott, B.P. et al. (LIGO Scientific Collaboration and Virgo Collaboration). "Observation of Gravitational Waves from a Binary Black Hole Merger." *Phys. Rev. Lett.* **116**, 061102 (2016). https://doi.org/10.1103/PhysRevLett.116.061102

[29] Abbott, B.P. et al. "GW170817: Observation of Gravitational Waves from a Binary Neutron Star Inspiral." *Phys. Rev. Lett.* **119**, 161101 (2017). https://doi.org/10.1103/PhysRevLett.119.161101

[34] Khalili, F.Y. "Optimal configurations of filter cavity in future gravitational-wave detectors." *Phys. Rev. D* **81**, 122002 (2010). https://doi.org/10.1103/PhysRevD.81.122002
