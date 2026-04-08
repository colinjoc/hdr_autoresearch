# HDR Project Candidates — Ranked by Novelty Potential

Updated 2026-04-08. Reassessed through the lens of: can HDR find genuinely novel solutions that advance the state of the art? Reproducing known results is engineering, not research.

---

## Tier 1 — Transformative Impact, High Novelty, GPU Feasible

### 1. Room Temperature Superconductor Discovery Pipeline
- **Domain**: Condensed matter physics / Materials science
- **Simulation**: Crystal structure → GNN (BEE-NET) → electron-phonon spectral function → Eliashberg equations → Tc prediction. Alternatively: crystal structure → SuperConNet → Tc directly (3DSC dataset, 33K superconductors)
- **SOTA**: 151K at ambient pressure (UH, March 2026). Room temp target: 300K. **Gap: 149K**
- **Tools**: BEE-NET/BETE-NET (PyTorch), GradDFT/D4FT (JAX), CrystalFlow (generative), MACE+PFT (phonons, fine-tunable in minutes on 1 GPU), 3DSC dataset
- **Novelty**: HIGH — Complete AI-accelerated pipeline just published (2026). Nobody has done HDR-style systematic hypothesis iteration over the design space. Most groups do one-shot screening.
- **HDR fit**: Iterate on crystal symmetry groups, elemental substitutions, hydrogen content, layer count, coordination environments, pressure-quench-stabilisable phases. 30K+ starting points in 3DSC + Materials Project
- **GPU**: YES — ML pipeline fits 12GB. Full DFT needs approximation but surrogates work
- **Why this matters**: Room temperature superconductors would revolutionise energy transmission, computing, transportation, and medical imaging. The ambient-pressure record was broken weeks ago.

### 2. Tokamak Plasma Transport Optimization (TORAX)
- **Domain**: Nuclear fusion / Plasma physics
- **Simulation**: TORAX (Google DeepMind, JAX) solves coupled transport PDEs for tokamak plasmas. Fully differentiable. Optimise heating profiles, current drive, density targets for max fusion power while avoiding disruptions.
- **SOTA**: ITER targets Q=10. Current best sustained: Q=0.33 (JET). **Gap: 30x in energy gain**
- **Tools**: TORAX (JAX, open source, faster-than-realtime, verified against RAPTOR). DeepMind partnering with CFS for SPARC pulse design.
- **Novelty**: HIGH — TORAX is new (2024). The design space for plasma operating scenarios is enormous and barely explored systematically. HDR maps perfectly.
- **HDR fit**: Heating power ramps, current drive timing, density targets, impurity seeding, edge safety factor profiles, bootstrap current fraction. Seconds per evaluation. Thousands of scenarios per hour.
- **GPU**: YES — 1D radial transport code. Lightweight. Runs faster-than-realtime on GPU.
- **Why this matters**: Fusion energy would solve climate change and energy scarcity permanently. TORAX is THE tool for designing SPARC/ITER operating scenarios.

### 3. Quantum Error Correction Code Discovery
- **Domain**: Quantum computing
- **Simulation**: RL agent proposes stabiliser codes → Clifford simulator evaluates code distance and logical error rates under noise → reward drives toward better codes. Or: optimise decoders for existing codes via differentiable belief propagation.
- **SOTA**: Surface codes need ~1000 physical qubits per logical qubit. qLDPC codes promise 10-100x reduction. **Gap: from ~1M physical qubits needed to <100K target**
- **Tools**: NVIDIA CUDA-Q QEC (GPU decoders), Stim (Clifford simulator), RL frameworks. 25-qubit code discovery demonstrated on single GPU.
- **Novelty**: HIGH — 120 QEC papers in 2025 alone. RL code discovery is early-stage. New code families (Majorana-XYZ, March 2026) still being found. Huge design space barely explored.
- **HDR fit**: Stabiliser weight constraints, connectivity patterns (matching hardware topology), code symmetry classes, decoder-aware design, noise-model-specific optimisation.
- **GPU**: YES — Clifford simulation is polynomial. RL training for 25-50 qubit codes runs in seconds.
- **Why this matters**: QEC is THE bottleneck for useful quantum computing. Better codes = fewer qubits needed = quantum advantage sooner.

### 4. Gravitational Wave Detector Topology Discovery
- **Domain**: Fundamental physics / Astrophysics
- **Simulation**: Parameterise interferometric detector topologies (mirrors, beam splitters, squeezing, filter cavities) → compute strain sensitivity via transfer matrices → optimise for broadband or narrowband sensitivity.
- **SOTA**: LIGO Voyager baseline. Urania AI (April 2025, Phys. Rev. X) discovered designs with **50x larger observable volume**. "Scientists don't yet fully understand" many discovered designs.
- **Tools**: Urania (open source, GitHub/GWDetectorZoo), neural surrogates for fast evaluation. BFGS with 1000 parallel runs.
- **Novelty**: HIGH — Urania just published. 50 novel designs in a "Detector Zoo" that nobody understands yet. Systematic HDR exploration of WHY certain topologies work = genuine scientific discovery.
- **HDR fit**: Number of recycling cavities, filter cavity configs, squeezing injection points, mirror mass ratios, arm cavity finesse, frequency-dependent squeezing angles.
- **GPU**: YES — Transfer matrix algebra is lightweight. Thousands of evaluations per second.
- **Why this matters**: Better detectors = detecting more gravitational wave sources = understanding black holes, neutron stars, and the early universe.

---

## Tier 2 — High Impact, Good Novelty

### 5. RNA Sequence Design
- **Domain**: Computational biology
- **Simulation**: JAX-RNAfold (differentiable) predicts MFE structure → match to target. Optimise nucleotide sequence for structural accuracy + thermodynamic stability.
- **SOTA**: Eterna100 pseudoknot-free: 91/100. Pseudoknotted: 50% wet-lab success (gRNAde). **Gap: large, especially pseudoknots and 3D**
- **Tools**: JAX-RNAfold (1250 nt on A100, ~200-300 nt on RTX 3060)
- **Novelty**: HIGH — Enormous design space (4^n), clear benchmarks (RNAInvBench, Eterna), massive gap from theoretical limit. Cross-domain potential from protein design.
- **GPU**: YES for moderate-length sequences
- **Why this matters**: mRNA vaccines, CRISPR guide RNAs, RNA therapeutics.

### 6. Photonic Nanostructure Inverse Design
- **Domain**: Photonics / Optics
- **Simulation**: FDTDX (JAX) solves Maxwell's equations → optimise device geometry for transmission/coupling.
- **SOTA**: Metasurface efficiencies ~70-75%. **Gap: large vs theoretical bounds**
- **Tools**: FDTDX (JAX, 10x faster than Meep, 98% memory reduction via time-reversible AD)
- **Novelty**: HIGH for 3D designs and quantum photonic devices. Tool is brand new (2025).
- **GPU**: YES for 2D, MAYBE for small 3D (288M grid cells fits on single GPU)

### 7. Crystal Plasticity Inverse Design (JAX-CPFEM) — NEW
- **Domain**: Materials science / Metallurgy
- **Simulation**: JAX-CPFEM (Feb 2025, 39x faster than MOOSE) — inverse design of crystallographic texture for target mechanical properties. Differentiable end-to-end.
- **SOTA**: Inverse texture design essentially unexplored. **Gap: entire field is new**
- **Tools**: JAX-CPFEM (JAX, differentiable, 52K DOF fits RTX 3060)
- **Novelty**: HIGH — Brand new capability. Nobody has systematically explored what microstructure designs are possible.
- **Why this matters**: Strength-ductility tradeoff optimisation for structural materials (aerospace, automotive, biomedical).

### 8. Phonon Thermal Transport Inverse Design (JAX-BTE) — NEW
- **Domain**: Condensed matter physics / Energy
- **Simulation**: JAX-BTE (first differentiable phonon BTE solver) — inverse design of nanostructures for targeted phonon transport spectra. Optimise for thermoelectric ZT.
- **SOTA**: Best ZT ~1.1-1.4. Theoretical projections: ZT >3-4 possible with optimal phonon engineering. **Gap: 2-3x in ZT**
- **Tools**: JAX-BTE (JAX, GPU, differentiable, npj Comp. Mat. 2025)
- **Novelty**: HIGH — First differentiable phonon BTE solver. Inverse design capability is unique.
- **GPU**: YES for 2D problems

### 9. Stellarator Divertor + Plasma Boundary Co-optimization
- **Domain**: Nuclear fusion
- **Simulation**: DESC (JAX, differentiable) for MHD equilibria + SIMSOPT for coils. ConStellaration dataset (158K boundary shapes, NeurIPS 2025 benchmarks).
- **SOTA**: Helios (Thea Energy) has best integrated design with X-point divertor. **Gap: no stellarator has reactor-relevant confinement + heat exhaust simultaneously**
- **Novelty**: MEDIUM-HIGH — ConStellaration benchmarks are brand new. Extends user's existing stellarator work.
- **GPU**: MAYBE — DESC fits for moderate resolution.

### 10. Warp Drive Metric Engineering
- **Domain**: General relativity / Theoretical physics
- **Simulation**: warpax (JAX, Feb 2026) — parameterise warp bubble spacetime metrics → compute stress-energy tensor → optimise to minimise energy condition violations. Positive-energy subluminal warp solutions discovered 2024.
- **SOTA**: First positive-energy solution exists. Energy requirements: ~Jupiter mass. **Gap: orders of magnitude in energy reduction needed**
- **Tools**: warpax (JAX, GPU, open source), Warp Factory (MATLAB)
- **Novelty**: MEDIUM — Tiny field, new tools. Even modest HDR campaign could be the most thorough investigation ever done.
- **GPU**: YES — Einstein field equations on a grid. Seconds per evaluation.
- **Why this matters**: Speculative but humanity's long-term future depends on interstellar capability.

---

## Tier 3 — Moderate Novelty or Feasibility Constraints

### 11. Structural Topology Optimization (JAX-FEM)
- **Novelty**: MEDIUM — 2D compliance is mature. Multi-physics 3D has room.

### 12. Battery Electrolyte Optimization (DiffMix)
- **Novelty**: MEDIUM — Framework exists and is validated. Multi-objective optimisation less explored.

### 13. Optical Lens System Design (DeepLens)
- **Novelty**: MEDIUM — Co-design of optics + computation is novel but memory-limited on RTX 3060.

### 14. Particle Accelerator Beam Optics (Cheetah)
- **Novelty**: MEDIUM — Differentiable accelerator sim is active but narrow.

### 15. Quantum Repeater Network Optimization
- **Novelty**: MEDIUM — Stochastic autodiff approach is new (2025) but niche.

---

## Dropped — Low Novelty or Infeasible

- **Robot Locomotion (MuJoCo/Brax)**: Classic benchmarks saturated. RL ≠ HDR. LOW.
- **Catalyst Surface Design (MACE/OC)**: ML benchmarking, not design exploration. MLIP accuracy too poor for reliable screening. LOW.
- **Seismic FWI (Devito)**: CPU-focused, 64GB+ RAM needed. INFEASIBLE.
- **Climate Model Emulation (ACE2)**: Needs 8 H100s for training. INFEASIBLE.
- **Spacecraft Trajectory (DiffOG)**: DiffOG is misidentified (robotics, not spacecraft). LOW dimensional. LOW.
- **Differentiable Fluid Control (PhiFlow)**: Overlaps with CFD. MEDIUM-LOW.

---

## The Big Picture

The strongest HDR candidates share these traits:
1. **A differentiable GPU simulator exists** (JAX-based preferred)
2. **SOTA is far from the physical limit** (large gap = room for HDR to find improvements)
3. **The design space is combinatorially rich** (many knobs to turn, non-obvious interactions)
4. **Published benchmarks exist** (can demonstrate novelty vs prior work)
5. **The problem matters to humanity** (energy, health, fundamental science)

The top 4 (superconductors, fusion, QEC, gravitational waves) score 5/5 on these criteria.
