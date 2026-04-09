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

**Note**: detailed component-by-component breakdown of type8/sol00 is **not** in this knowledge base because it has not been verified by reading the actual `.kat` config file in Phase 0.5. The previous session's reconstruction claimed specific counts but those came from artifacts.

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

*This section grows as Phase 0.5 / Phase 1 / Phase 2 produces verified numbers. Anything that survives a `verify_*.py` script lives here, with the script name and run date.*

(Empty as of Phase 0 start, 2026-04-09. The previous session's reconstruction had some verified Voyager numbers; those are not carried over without re-running.)
