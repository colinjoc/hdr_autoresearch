# Future HDR Projects

Candidates assessed 2026-04-08, ready for Phase 0 when capacity allows.

## Ready to Start (lit review needed)

### Tokamak Plasma Transport (TORAX)
- DeepMind's JAX differentiable tokamak simulator, faster-than-realtime
- Optimise SPARC/ITER operating scenarios (heating, current, density)
- Q=0.33 → Q=10 gap. Thousands of scenarios per hour on 1 GPU
- Complements existing stellarator work
- Ref: github.com/google-deepmind/torax

### Quantum Error Correction Code Discovery
- RL discovers new stabiliser codes, Clifford simulator evaluates
- 120 QEC papers in 2025, field exploding. New codes still being found
- ~1M qubits needed → <100K target. 10-100x overhead reduction possible
- Ref: NVIDIA CUDA-Q QEC, Stim, npj QI 2024

### Gravitational Wave Detector Topology
- Urania AI found 50x improvement over LIGO Voyager (Phys. Rev. X, April 2025)
- 50 novel designs nobody understands. HDR could explain WHY they work
- Open source: github.com/artificial-scientist-lab/GWDetectorZoo
- Transfer matrix algebra — lightweight, thousands of evals/sec

### Warp Drive Metric Engineering
- warpax (JAX, Feb 2026) — optimise warp bubble metrics for energy conditions
- Positive-energy subluminal solution discovered 2024 (UAH)
- Tiny field — even modest HDR campaign would be most thorough investigation ever
- Ref: github.com/anindex/warpax

## Phase 0 Complete (ready for Phase 0.5)

### Robot Locomotion Policy Optimization
- Lit review done at ~/generalized_hdr_autoresearch/applications/robot_locomotion/
- 110 citations, design variables, 25 hypotheses, knowledge base
- MuJoCo Playground / MJX / Brax
- Lower novelty potential (classic benchmarks saturated) but good for learning HDR on simulation

### Quantum Gate Pulse Optimization
- Phase 0.5 done, 7 experiments completed
- Best: 99.94% fidelity at 10ns, robust ±2MHz, hardware-feasible
- Next steps documented in ~/quantum_gates/next_steps.md
- Neural ODE pulses (novel) and two-qubit CZ gates (high impact) identified

## Assessed but Lower Priority

- Crystal Plasticity Inverse Design (JAX-CPFEM) — brand new, unexplored
- Phonon Thermal Transport (JAX-BTE) — first differentiable phonon BTE, thermoelectrics
- Photonic Nanostructure Inverse Design (FDTDX) — large gap, 3D underexplored
- RNA Sequence Design (JAX-RNAfold) — 50% solve rate on pseudoknots, large gap
- Stellarator Divertor Co-optimization (DESC + ConStellaration) — extends existing project
- Structural Topology Optimization (JAX-FEM) — mature for 2D, multi-physics has room
- Battery Electrolyte Optimization (DiffMix) — validated framework, multi-objective less explored
