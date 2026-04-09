# Structural Decomposition of the Urania type8 Family of AI-Discovered Gravitational-Wave Detectors

## Abstract

The Urania AI system [1] released 50 novel gravitational-wave detector topologies in the GWDetectorZoo [3], with the authors explicitly stating that "the experimental setup is not fully optimized and could be significantly simpler" and that the physical mechanisms behind many of these designs remain poorly understood. Here we present the first systematic structural decomposition of the 25-solution type8 (post-merger band, 800–3000 Hz) family. We wrote a parser for the PyKat-format `.kat` configuration files that the Zoo distributes (no parser previously existed for this purpose, and the canonical PyKat library is broken on Python ≥ 3.12), used it to extract every component, parameter, and free-space connection from each solution, then combined this structural data with the canonical strain spectra that the Zoo distributes alongside each solution to compute log-space-averaged improvement factors over the LIGO Voyager baseline, and finally ran a topological analysis that traces the optical graph from each laser through the kat free-space connections to determine which components are actually wired into the active light path. Five concrete findings emerge: (i) the headline solution `type8/sol00` achieves a 4.05× log-averaged strain improvement over Voyager in the post-merger band — substantially higher than artifact-derived prior claims of 3.12× — and is dramatically better than its 24 family siblings (median improvement 1.10×, minimum 1.00×); (ii) the Urania UIFO grids are grossly over-parameterised — in `sol00` specifically, 20 of 57 mirrors (35%) have reflectivity below 0.001 (effectively transparent), 9 of 57 (16%) have reflectivity above 0.999 (effectively perfect reflectors), and only 2 of 13 declared beamsplitters perform meaningful beam splitting; (iii) across the 25-solution family, the number of squeezer elements correlates *negatively* with strain improvement (Pearson r = −0.50), and the number of mirrors pinned to R ≈ 0 correlates *positively* with improvement (r = +0.51); (iv) `sol00`'s declared "balanced homodyne detector" is a phantom — one of its two photodetector ports is not wired into any optical path — and the same phantom-detector pattern appears in 4 of the top 5 type8 solutions, so single-port readout is a Urania-learned pattern; (v) of the 6 arm-cavity-class free spaces in `sol00` previously framed as a "multi-arm geometry", only 1 is a true symmetric cavity — the other 5 are 2 through-pass delay lines, 1 dead trap, 1 one-sided wall, and 1 asymmetric cavity. The combined picture from findings (iv) and (v), together with the earlier finding that no `sol00` mirror sits in the canonical Fabry-Perot input reflectivity range, excludes balanced-homodyne classical-noise rejection, multi-arm Fabry-Perot averaging, and Voyager-style heavy-test-mass radiation-pressure suppression as candidate mechanisms for the 4.05× improvement. The most plausible remaining explanation is **distributed gravitational-wave signal injection across 26 free-space perturbation points with the canonical Michelson 180/0 phase pattern, fed to a single-port readout, amplified by 1294 W of coherent multi-laser injection through one low-finesse 3.8-km compound cavity** — a multi-input, single-output topology that has no obvious analogue in the published interferometer-design literature. We do not yet have a calibrated numerical reconstruction confirming the magnitude of this mechanism: the kat-to-Differometor converter built for this purpose is structurally complete but currently off by a factor of approximately 10⁶ in absolute scale, blocking quantitative ablation. We argue that the qualitative conclusion of the Krenn et al. 2025 paper — that Urania discovered fundamentally novel topologies — is correct for `sol00`, but the novelty is in a multi-input distributed-injection architecture, not in any improvement to the conventional Fabry-Perot Michelson framework.

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

### 3.5 Mass distribution and arm-cavity-class spaces

All 57 mirrors in sol00 carry an explicit mass attribute. The distribution:

- Range: 0.01 to 200.00 kg
- Median: **88.64 kg**
- Mirrors at exactly 200 kg (Voyager nominal): **4**
- Mirrors below 50 kg (light test masses): **18**
- Mirrors below 1 kg: 9

The median mirror mass is **less than half** of Voyager's 200 kg test mass. Eighteen mirrors are below 50 kg.

`sol00` has 78 free spaces. Of these, **6 are at arm-cavity-class lengths** (greater than 1 km): three at 3847 m (the `mRL_3_*` set) and three at 3670 m (the `mUD_*_1` set). This is the raw count.

**However**: the raw count is misleading. A subsequent topological analysis (see §3.8) classified each of the 6 arm-cavity-class spaces by what is at its endpoints and found that **only 1 of the 6 is a true symmetric cavity**. The other 5 are topology artifacts: 2 are through-pass delay lines (both endpoints have reflectivity near zero, light just passes through), 1 is a one-sided wall, 1 is a dead trap (both ends perfectly reflective with no laser light reaching the cavity), and 1 is an asymmetric cavity. The earlier framing of "6 arm cavities forming a multi-arm geometry" was wrong — the geometry is one true cavity plus several long delay lines and dead spaces.

Similarly, two of the four 200-kg mirrors (`MB3_1_d` and `MB3_2_u`) sit at the endpoints of the through-pass space `mUD_3_1`, where both mirrors have reflectivity below 0.003 — they are effectively transparent. A 200-kg transparent mirror feels almost no radiation pressure (the momentum transferred per photon is proportional to reflectivity), so the 200-kg "test masses" do not function as Voyager-style test masses. The 200-kg value is the optimiser's upper bound for the mass parameter, pinned to the boundary by the optimiser as a no-op rather than chosen for any physical reason.

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

### 3.8 Topological analysis: phantom homodyne, true cavity classification, and a candidate mechanism

After the 20 hypothesis-driven experiments in §3.7 narrowed the open question to "what mechanism actually produces sol00's 4.05× improvement, given that it is not a classical Fabry-Perot interferometer?", a follow-up topological analysis traced the optical graph structure of sol00 in detail. The analysis used a new module `light_path_trace.py` that builds an `OpticalGraph` from a parsed kat document and runs breadth-first search from each laser to identify which components are reachable, which spaces form true cavities, and which detector ports actually receive light.

#### M01 — sol00's "balanced homodyne detector" is a phantom

The sol00 kat file declares `qhd nodeFinalDet 180.0 AtPD1 AtPD2` — a balanced-homodyne quantum detector at 180 degrees, the canonical configuration for classical-noise rejection. The declaration requires both photodetectors `AtPD1` and `AtPD2` to receive light from the interferometer for the balanced subtraction to work.

The topological analysis found that **`MDet1`'s back port `nMB4_0_dSetup` is not referenced by any free-space (`s`) statement in the kat file**. There is no `mUD_4_0` space connecting `MDet1` to any other component in the grid. The only optical path into `AtPD1` is via `SDet1` (a 2-metre space from `AtPD1` to `MDet1`'s front port), which is a dead-end loop — no light from any of the three lasers ever reaches `AtPD1`. The "balanced" homodyne reduces to a single-port readout on `AtPD2`; `AtPD1` carries only vacuum fluctuations with no classical signal.

A family survey on the top-5 type8 solutions found that **4 of the top 5 (sol00, sol02, sol03, sol05) share this phantom-MDet pattern**. (sol01 uses a different architecture with a final beamsplitter `BSfin` that genuinely splits light between `ToPD1` and `ToPD2`, yielding a true balanced readout.) Across the entire 25-solution type8 family, no solution has two genuinely connected `MDet` mirrors and a functional balanced-homodyne readout. Single-port readout is therefore a Urania-learned pattern, not a sol00 quirk.

The implication: **mechanisms that require balanced-homodyne common-mode rejection are excluded** as explanations for sol00's 4.05× improvement. The improvement does not come from cancelling classical noise via a balanced subtraction.

#### M02 — Only 1 of the 6 arm-cavity-class spaces is a true symmetric cavity

The 6 arm-cavity-class spaces in sol00 (3 at 3847 m, 3 at 3670 m) were classified by what mirror reflectivities sit at each endpoint. The classification:

| Space | Length (m) | Reflectivity at end A | Reflectivity at end B | Interpretation |
|---|---|---|---|---|
| `mRL_3_2` | 3846.96 | 0.00209 | 0.00015 | Both endpoints transparent — light passes through, not a cavity |
| **`mRL_3_3`** | **3846.96** | **0.5187** | **0.5004** | **True symmetric compound cavity, finesse ≈ 4.6** |
| `mRL_3_4` | 3846.96 | 0.9530 | 0.0806 | Asymmetric cavity (one end nearly perfect, one end transparent) |
| `mUD_1_1` | 3670.84 | 1.0000 | 1.0000 | Dead trap — both ends perfectly reflective, no laser light reaches it |
| `mUD_2_1` | 3670.84 | 0.0860 | 1.0000 | One-sided wall — perfect reflector on one side, transparent on the other |
| `mUD_3_1` | 3670.84 | 0.00002 | 0.00239 | Both endpoints transparent — through-pass delay line |

The only space that actually forms a Fabry-Perot-like cavity is **`mRL_3_3`**, with reflectivities approximately 0.52 and 0.50 at its two endpoints, giving a finesse of approximately 4.6, a free spectral range of 39 kHz, and a cavity linewidth of 8.5 kHz. This is a low-finesse cavity — much broader than the canonical impedance-matched high-finesse cavities used in Voyager, and consistent with the §3.3 finding that no mirror in sol00 has reflectivity in the [0.99, 0.9999] range.

The other 5 arm-class spaces are not cavities at all. Two are long delay lines (light just passes through), one is a dead trap, one is an asymmetric one-sided wall, and one is asymmetric. The earlier framing of "6 arm cavities forming a multi-arm geometry" must be retracted: there is **1 cavity, plus several long-baseline delay lines and dead spaces**.

#### M03 — The 200-kg mirrors are optimiser artifacts on transparent through-passes

Two of the four 200-kg mirrors in sol00 are `MB3_1_d` and `MB3_2_u` — the endpoints of the through-pass space `mUD_3_1`. Both have reflectivity below 0.003 (effectively transparent). The other two 200-kg mirrors (`MB2_1_l`, `MB2_2_l`) sit on short bridges, not on cavity endpoints, with one at reflectivity 0.0008 (transparent) and one at 0.456 (intermediate).

A transparent mirror with mass 200 kg feels essentially no radiation pressure — the momentum transferred per photon scales with the reflectivity, and a transparent mirror reflects almost nothing. The 200-kg "test masses" therefore do not function as Voyager-style heavy test masses for radiation-pressure-limited quantum noise reduction. The 200-kg value is the optimiser's upper bound for the mass parameter, pinned to the boundary as a no-op.

#### M09 — The 26 signal injections follow a Michelson phase-differencing pattern

The 26 `fsig` signal injection points in sol00 are split exactly between vertical-arm spaces (`mUD_*`) and horizontal-arm spaces (`mRL_*`), with all 13 `mUD_*` injections at phase 180 degrees and all 13 `mRL_*` injections at phase 0 degrees. The 180-degree phase difference corresponds to the canonical Michelson differential-arm-length signal pattern: horizontal arms see a strain perturbation `+h`, vertical arms see `-h`, and the differential combination measures `2h`.

This is the only structural feature of sol00 that matches a textbook gravitational-wave-detector pattern. Even though the individual arm structures are unusual (only 1 true cavity, 5 non-cavity spaces), the signal-coupling architecture preserves the Michelson differential-detection scheme.

#### Candidate mechanism for sol00's 4.05× improvement

Combining the findings of §3.5, §3.7, and the M01–M03 + M09 analyses above, the most plausible explanation for sol00's 4.05× improvement over Voyager is **NOT** the classical mechanisms that prior artifact-derived narratives proposed:

- It is **not** Fabry-Perot finesse engineering (M02 — only 1 low-finesse cavity).
- It is **not** balanced-homodyne classical-noise rejection (M01 — the second photodetector is orphaned).
- It is **not** Voyager-style heavy-test-mass radiation-pressure-noise suppression (M03 — the 200-kg mirrors are transparent).
- It is **not** multi-arm Fabry-Perot signal averaging (M02 — there is only 1 real arm-class cavity, not 6).

Instead, the candidate mechanism is a combination of three contributions:

1. **Coherent multi-laser injection**: 3 lasers totalling 1294 W of optical power (versus Voyager's 750 W at the end test mass), all at the same frequency and phase, entering the grid at three different points. The coherent combination contributes approximately a factor of √(1294 / 750) ≈ 1.3 in shot-noise-limited sensitivity if the additional power reaches the readout.

2. **Distributed Michelson signal injection across 26 points**: the gravitational-wave perturbation is encoded into 26 separate `fsig` injections across all 6 long-baseline spaces, with the canonical 180/0 phase pattern that corresponds to differential-arm-length detection. The total signal accumulated by the topology scales with the number of independent signal paths that combine constructively at the readout. This mechanism does not exist in a conventional dual-arm Michelson and is the most likely source of the bulk of the improvement factor.

3. **One low-finesse compound cavity for phase-to-power conversion**: the `mRL_3_3` cavity (finesse ≈ 4.6, length 3847 m) is the single sharp optical element that converts the accumulated phase into measurable power at the readout. Its low finesse means it does not provide narrow-band resonance enhancement; it provides a 3.8-kilometre arm length comparable to Voyager's 4-kilometre arms.

Whether this mechanism quantitatively predicts the 4.05× improvement requires a numerical reconstruction in either the original Finesse simulator or a calibrated equivalent — see Section 4.5 for the open work on the Differometor converter (which is structurally complete but currently off by a factor of 10⁶ in absolute scale, blocking quantitative ablation).

## 4. Discussion

### 4.1 Sol00 is dramatically the best of its family — and its mechanism is distributed signal injection, not classical cavity engineering

The headline finding is that the type8 post-merger family is heavily skewed: sol00 alone provides a 4.05× improvement over Voyager, while the median solution improves by only 1.11× and the bottom half is within ±3% of Voyager (E18). The Krenn et al. paper's framing — "all 50 solutions are superior to the LIGO Voyager baseline" — is technically true but obscures this skew. Practical detector design should target sol00 (or perhaps sol01 at 3.36×); the rest of the type8 family is not worth implementing.

The **second** finding, no less important: sol00 is not a classical interferometer at all. The 20 hypothesis-driven experiments (§3.7) showed that sol00 contains zero mirrors in the canonical Fabry-Perot input reflectivity range, and the topological analysis (§3.8) further showed that:

- The "balanced homodyne detector" declared in the kat file is a phantom — one of its two photodetector ports is not connected to the interferometer at all (M01). The same phantom-detector pattern appears in 4 of the top 5 type8 solutions, so it is a Urania-learned pattern, not a sol00 quirk. **Balanced-homodyne classical-noise rejection is excluded** as a candidate mechanism.
- Of the 6 arm-cavity-class spaces, only 1 is a true symmetric cavity (M02). The other 5 are 2 through-pass delay lines, 1 dead trap with both ends perfectly reflective and no laser light, 1 one-sided wall, and 1 asymmetric cavity. **Multi-arm Fabry-Perot signal averaging is excluded** as a candidate mechanism.
- The 4 mirrors at exactly 200 kg are not cavity end-mirrors (M03). Two of them sit on the transparent endpoints of the through-pass space `mUD_3_1` and feel essentially no radiation pressure. The 200-kg value is the optimiser's upper bound for the mass parameter, pinned to the boundary as a no-op rather than chosen as a Voyager-style heavy test mass. **Voyager-style radiation-pressure suppression is excluded** as a candidate mechanism.

What remains as the most plausible candidate mechanism is **distributed signal injection with Michelson phase differencing**, fed to a single-port readout, amplified by 1294 W of coherent multi-laser injection, with one low-finesse 3.8-km compound cavity providing the phase-to-power conversion. The 26 signal injection points (M09) follow the textbook 180/0 phase pattern that encodes a differential-arm-length gravitational-wave perturbation, and the multiplicity (26 injection points versus 2 in a conventional dual-arm Michelson) is the geometric factor that the optimiser found.

This is not a familiar interferometer architecture. It is a **multi-input, single-output, distributed-injection topology** that the AI optimiser converged to without any human guidance toward known interferometer designs. The 4.05× improvement is achieved by accumulating the gravitational-wave signal at many points and combining it coherently at one readout, rather than by enhancing the per-point sensitivity via cavity finesse.

A quantitative confirmation of this interpretation requires a numerical reconstruction of sol00 in either the original Finesse simulator or a calibrated equivalent. The Differometor converter built as part of this work is structurally complete but currently off by a factor of approximately 10⁶ in absolute scale, blocking quantitative component-level ablation. See Section 4.6 (Future work) for the diagnostic plan for the next session.

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

We performed the first systematic structural decomposition of the 25-solution Urania type8 (post-merger) family of AI-discovered gravitational-wave detectors, in three stages: a parser for the PyKat-format `.kat` configurations distributed by the GWDetectorZoo, a 20-experiment hypothesis-driven decomposition loop covering single-solution and cross-family patterns, and a follow-up topological analysis that traces the optical graph through every free-space connection in `sol00`.

Six findings:

1. The headline solution `type8/sol00` improves on Voyager by **4.05×** in the 800–3000 Hz band, substantially higher than artifact-derived prior claims of 3.12×. It is dramatically better than its 24 family siblings, whose median improvement is only 1.11× and whose bottom half clusters within ±3% of Voyager.

2. **Sol00 is not a classical interferometer at all.** It contains zero mirrors with reflectivity in the canonical Fabry-Perot input range R ∈ [0.99, 0.9999]; its declared "balanced homodyne detector" is a phantom whose second photodetector port is orphaned; only 1 of its 6 arm-cavity-class free spaces is a true symmetric cavity; and the 4 mirrors at exactly 200 kg sit on transparent through-pass mirrors rather than at cavity endpoints, making them inactive as Voyager-style test masses. Multiple candidate mechanisms — Fabry-Perot finesse engineering, balanced-homodyne classical-noise rejection, multi-arm signal averaging, and heavy-test-mass radiation-pressure suppression — are each individually excluded.

3. The most plausible remaining mechanism is **distributed signal injection across 26 free-space perturbation points with the canonical Michelson 180/0 phase pattern**, fed to a single-port readout, amplified by 1294 W of coherent multi-laser injection (1.7× Voyager's laser power), with one low-finesse 3.8-km compound cavity at `mRL_3_3` providing the phase-to-power conversion. This is a multi-input, single-output topology that has no obvious analogue in the published interferometer-design literature; the AI optimiser found it without any prior toward known designs.

4. The UIFO topology is grossly over-parameterised across three independent levels: 51% of `sol00`'s mirrors are pinned to one of two reflectivity extremes, only 2 of 13 declared beamsplitters perform meaningful beam splitting, and **64% of `sol00`'s free spaces are PyKat-default 1.0 m fillers**. The Zoo authors' own statement that the design "could be significantly simpler" is quantitatively confirmed at all three levels.

5. Across the 25-solution family, the number of squeezer elements correlates *negatively* with strain improvement (Pearson r = −0.50), the number of mirrors pinned to R ≈ 0 correlates *positively* (r = +0.51), and the top 4 solutions average **1.0 squeezers** while the bottom 21 average **2.71 squeezers**. The best solutions are not the ones with the most quantum-noise-reduction machinery — they are the ones with the cleanest structural skeletons.

6. The phantom-balanced-homodyne pattern is shared by 4 of the top 5 type8 solutions (sol00, sol02, sol03, sol05). Single-port readout disguised as balanced-homodyne detection is therefore a **learned Urania pattern**, not a sol00 quirk. The optimiser converged to this pattern across multiple solutions without any explicit architectural guidance.

A quantitative confirmation of finding (3) — the distributed-signal-injection mechanism — requires a numerical reconstruction of sol00 in either the original Finesse simulator or a calibrated equivalent. The kat-to-Differometor converter built as part of this work (`kat_to_differometor.py`) is structurally complete and runs end-to-end without errors, but its absolute scale is currently off by approximately 10⁶ versus the Zoo's canonical strain spectra, blocking quantitative component-level ablation. A four-step debugging plan for the next session is documented in the project's `mechanism_investigation.md`.

These findings establish a structural and topological baseline for any future component-level ablation work on the GWDetectorZoo. The kat parser, the topological-analysis modules, the 20-experiment HDR loop, and the (uncalibrated) Differometor converter are all released alongside this paper at `applications/gw_detectors/`. Every quantitative claim in this paper is traceable to a row in `results.tsv`, `results/per_solution.tsv`, or `results/sol00_arm_cavity_map.tsv`.

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
