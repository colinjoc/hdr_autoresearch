# Knowledge Base — gw_detectors

**Status**: Phase 0 in progress. This file accumulates established results, validated baselines, and known facts. Anything here is **either** taken from a peer-reviewed reference (with `papers.csv` id) **or** verified directly via simulation in this project (with the verifying script's name and a date). Anything that is neither cited nor verified is a hypothesis and belongs in `research_queue.md`, not here.

---

## 1. Established baselines

### 1.1 LIGO Voyager (the comparison target)
- Paper: Adhikari et al. 2020, *Class. Quantum Grav.* **37**, 165003 (papers.csv id 24)
- Test mass: 200 kg crystalline silicon, 123 K
- Laser: 2 µm wavelength
- Frequency-dependent squeezing: 10 dB
- Configuration: power-recycled, signal-recycled Fabry-Perot Michelson
- Published strain noise minimum: ~3.76e-25 /√Hz near 168 Hz
- **Verification status**: TO BE VERIFIED via Differometor's bundled `voyager()` setup in Phase 0.5. (A previous session verified this; that result is preserved as a starting point but should be re-confirmed.)

### 1.2 LIGO / Virgo / KAGRA current generation
- aLIGO design strain ~1e-23 /√Hz at ~100 Hz; first detection 2015 (Abbott et al. 2016, papers.csv id 28)
- Quantum-enhanced operation since 2019 (Tse et al. 2019; Acernese et al. 2019; ids 19, 20)
- Frequency-dependent squeezing operational since 2020 (McCuller et al. 2020, id 18)

### 1.3 Standard quantum limit (SQL)
- Formula (free-mass interferometer): $h_{\rm SQL}(f) = \sqrt{\frac{8\hbar}{M (2\pi f)^2 L^2}}$
- For $L=4$ km, $M=40$ kg, at $f=100$ Hz: $h_{\rm SQL} \approx 1.7 \times 10^{-24}$ /√Hz
- Reference: Caves 1981, *Phys. Rev. D* **23**, 1693 (papers.csv id 9)
- Practical detectors approach but do not exceed the SQL except by squeezing or quantum-nondemolition tricks (Kimble et al. 2001, papers.csv id 13)

---

## 2. The Universal Interferometric Field Operator (UIFO) framework

- Introduced by Krenn, Drori, Adhikari 2025 (papers.csv id 1)
- An $n \times n$ grid of optical components connected by ports
- Components: mirrors, beamsplitters (regular and directional), lasers, squeezers, photodetectors, free masses, signal sinks, frequency nodes
- Up to 463 continuous parameters per design (paper id 1, abstract)
- Optimisation method: gradient-based BFGS with 1000 random restarts
- Output: 50 designs in 11 type families (type0..type10), grouped by target frequency band and topology family

### Type8/sol00 — canonical authoritative numbers (from the Zoo README)

Read directly from `GWDetectorZoo/solutions/type8/sol00/README.md` on 2026-04-09:

| Property | Value |
|---|---|
| Frequency range | 800–3000 Hz (post-merger / neutron star) |
| Loss (Urania objective value) | −85.46 |
| **Lasers** | **3** |
| **Squeezers** | **0** |
| **Mirrors** | **57** |
| **Beam splitters** | **13** |
| **Faraday isolators** | **1** |
| **Number of free parameters** | **120** |

The Zoo authors explicitly note: *"The experimental setup is not fully optimized and could be significantly simpler."* This sentence — written by Krenn, Drori, Adhikari themselves — directly validates the decomposition project's premise.

**Important corrections to anticipated values**: prior artifact-derived claims about "48 mirrors and 4 squeezers" were wrong. Sol00 has **57 mirrors and zero squeezers**. Any "ponderomotive squeezing" or "external squeezed-light" reasoning that follows from a non-zero squeezer count is moot. The 1 Faraday isolator (a non-reciprocal element used for light isolation) is also a feature missed by all artifact descriptions.

---

## 3. The GW Detector Zoo

- Public dataset, 50 designs, available at `https://github.com/artificial-scientist-lab/GWDetectorZoo` (papers.csv id 3)
- Format: each solution is a directory under `solutions/typeN/solMM/` containing a PyKat `.kat` config file, pre-computed strain/signal/noise CSVs, and PNG visualisations
- Config file format: PyKat / Finesse `.kat` text language
- The Zoo's own `software/sensitivity/` directory has Python scripts (using PyKat + Finesse) that can re-compute strain from each `.kat`. **PyKat is unmaintained and broken on Python 3.12.** Reproducing the Zoo's own evaluation requires either Python 3.10/3.11 or a different loader.
- Differometor (papers.csv id 2) is the recommended modern simulator and is JSON-based, not `.kat`-based. A `.kat → Differometor JSON` converter does not exist as of 2026-04-09 and would need to be written in Phase 0.5 if direct loading of Zoo solutions into Differometor is required.

---

## 4. Differometor

- JAX-based differentiable interferometer simulator (papers.csv id 2)
- Bundled with predefined Voyager and aLIGO setups
- Bundled example UIFO designs in `examples/data/`: `uifo_20_5000.json` (broadband) and `uifo_800_3000.json` (post-merger). These are pre-trained UIFOs from the Differometor authors and **may or may not** correspond to specific solutions in the GWDetectorZoo — to be verified in Phase 0.5.
- API surface (read from Differometor source examples):
  - `from differometor.setups import voyager, Setup`
  - `S, _ = voyager()` → predefined Setup
  - `S = Setup.from_data(json_dict)` → load arbitrary UIFO from JSON
  - `df.run(S, [(component, prop)], values)` → main solver
  - `df.signal_detector(carrier, signal)` → signal at detector ports
  - `df.power_detector(carrier)` → power at detector ports
- Strain sensitivity: $S_h(f) = \text{noise} / |\text{signal at detector}|$, where the detector signal is the difference between the two homodyne photodetectors

---

## 5. Frequency bands of interest

| Band | Frequency range | Astrophysical sources |
|---|---|---|
| Inspiral | 10–100 Hz | BBH, BNS, NSBH inspirals (long-duration) |
| Merger | 100–800 Hz | Final coalescence; peak frequency $\sim$ kHz for stellar-mass BBH |
| Post-merger / ringdown | 800–3000 Hz | NS post-merger oscillations; BH ringdown |
| Free spectral range | 4 km arms → ~37 kHz | (technical) |

The GWDetectorZoo type8 family targets the post-merger band 800–3000 Hz.

---

## 6. Empirical / verified results from this project

All numbers below are from real measurements run on 2026-04-09 against the canonical GWDetectorZoo files and Differometor. Each is traceable to a specific script and the source data.

### 6.1 Differometor reproduces Voyager (`analysis.py` cross-check)
- Voyager min strain noise: **3.764 × 10⁻²⁵ /√Hz at 169.4 Hz**
- Published value [Adhikari 2020]: 3.76 × 10⁻²⁵ at 168 Hz
- Agreement: 0.1% in strain, 1.4 Hz in frequency

### 6.2 Type8 family improvement factors (`analysis.py`)
Log-averaged over the post-merger band (800–3000 Hz), measured directly from each solution's `strain.csv`:
- **sol00: 4.05×** (winner)
- sol01: 3.36×
- sol02: 2.68×
- sol03: 2.22×
- sol04: 1.78×
- sol05–sol12: 1.10×–1.30×
- sol13–sol24: 1.00×–1.10× (essentially break-even with Voyager)
- mean 1.43×, median 1.11×, max 4.05× (sol00), min 1.00×

### 6.3 Sol00 structural inventory (`sol00_anatomy.py`)
- 108 parameters (Zoo README claims 120; the .kat file has 108 const param lines)
- 57 mirrors, 13 beamsplitters, 3 lasers, 0 squeezers, 1 directional beamsplitter (matches Zoo README)
- 78 free spaces; 6 at 4-km-class arm-cavity length (3 at 3847 m, 3 at 3670 m)

### 6.4 Sol00 mirror reflectivity distribution
- R < 0.001 (effectively transparent): **20** mirrors (35%)
- R > 0.999 (effectively perfect reflectors): **9** mirrors (16%)
- Total at extremes: **29 of 57 (51%)**
- Interior R values: 28 of 57

### 6.5 Sol00 beamsplitter inventory
- 2 of 13 are doing real beam splitting (B1_3 at R=0.81, B3_1 at R=0.30)
- 2 are pinned to R=1.0 (functioning as perfect mirrors)
- 1 is pinned to R=0.0 (effectively transparent)
- 8 are at R=0.006–0.10 (highly asymmetric, near-transparent)
- **Only 2 of 13 declared beamsplitters perform meaningful beam splitting**

### 6.6 Sol00 mass distribution
- All 57 mirrors carry explicit mass attributes
- Range 0.01–200.00 kg, **median 88.64 kg** (less than half Voyager's 200 kg)
- 18 mirrors below 50 kg (light test masses)
- 4 mirrors at exactly 200 kg (Voyager nominal)

### 6.7 Cross-family correlations (`analysis.py` Pearson r vs improvement)
- **n_squeezers vs improvement: r = −0.497** (more squeezers → worse, counterintuitive)
- **mirrors_R_near_zero vs improvement: r = +0.509** (more aggressive pruning → better)
- n_directional_bs: r = −0.385
- n_mirrors: r = +0.316
- n_parameters: r = +0.236

### 6.8 Falsified prior claims
The lost reconstruction made these claims (now archived). They are wrong:

| Reconstruction claim | Verified ground truth |
|---|---|
| sol00 has 48 mirrors | sol00 has **57 mirrors** |
| sol00 has 4 squeezers | sol00 has **0 squeezers** |
| sol00 improvement is 3.12× | sol00 improvement is **4.05×** |
| 2 essential arm cavities | sol00 has **6 arm cavities** at 4-km-class length |
| "All 4 squeezers carry <0.5 dB" | There are no squeezers to carry anything |
| Type8 family uses noise-suppression vs signal-amplification mechanisms | Type8 family is dominated by sol00; family pattern is "fewer squeezers → better" |
