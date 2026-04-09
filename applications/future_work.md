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

## Lost Projects (Need to Be Rebuilt From Scratch)

These four projects had substantial work — code, experiments, results, knowledge bases — but their entire on-disk state was destroyed on 2026-04-09 by an unverified destructive bash loop during a repo migration. Their per-experiment git histories are unrecoverable. The lessons each one taught the methodology have been promoted to `program.md` (Sanity Checks, Tournament Anti-Patterns, Phase A → Phase B Bridge, Bayesian Prior Calibration, Anti-Patterns, Plateau Detection). The projects themselves need to be re-built from scratch by re-running Phase 0 lit review and onward — there is no recovery path. Listed in priority order for revisit.

### CYPHER (turbulent diffusivity / hydrogen flame challenge)
- **Original goal**: predict turbulent diffusivity in hydrogen-air premixed flames; submission to a published challenge
- **What was lost**: 109 commits across 50 experiments; final score ~12.0 on the challenge metric; model.py / model_v37_best.py / model_mlp_best.py
- **What survived**: lessons promoted to program.md (data curation > feature engineering once alignment is correct; training-trick priors are systematically overconfident; inference optimization compounds reliably; ensemble pivots are catastrophic without validation rigor; tighten revert thresholds late-loop)
- **To revisit**: re-clone the upstream challenge repo, re-do Phase 0 lit review on combustion-DNS featurization, re-build the predictor from scratch. Phase 0 is the longest part — the methodology lessons should make Phase 1 onward faster than the original.

### matbench (materials property prediction benchmark)
- **Original goal**: HDR loop on the MatBench v0.1 benchmark; per-task model selection across 4 tasks (expt_gap, mp_gap, steels, glass)
- **What was lost**: 86 commits, strategy.py, tournament_results.md, the per-task decision table, ~110-entry papers.csv, the matminer feature cache (442 MB)
- **What survived**: lessons promoted to program.md (per-task model selection is mandatory; bagging > boosting for N < 400; hard thresholds beat soft blends for bimodal targets; cache custom featurization on first run; featurizer speed audit at 500 samples)
- **To revisit**: matbench dataset is public and stable. Re-clone, re-do Phase 0 (the lit review for materials informatics is large), and rebuild the per-task tournament. The methodology shortcuts in program.md will save substantial effort the second time.

### superconductor (Tc prediction + candidate screening)
- **Original goal**: train a Tc predictor on the SuperCon database, then use it to screen novel compositions for high-Tc candidates; post-filter with MACE-MP for stability
- **What was lost**: 28 commits; model.py, evaluate.py, stability.py; results.tsv with the Phase A predictor history; discoveries/candidates.csv and pareto_front.csv with the top screened compositions; the recently-added MACE-MP integration that kept 33/50 candidates as stable
- **What survived**: lessons promoted to program.md (feature availability check — features in the predictor must be computable on novel candidates; combinatorial template diversity beats predictor improvement in Phase B; stability / feasibility post-filter with universal ML potentials)
- **To revisit**: SuperCon is publicly available. Re-do Phase 0 lit review on superconductor ML, rebuild the predictor avoiding the structure-feature trap (the lesson the project taught us), and re-run the discovery loop with combinatorial templates from the start.

### quantum_gates (pulse-shape optimization for high-fidelity gates)
- **Original goal**: optimize control pulse shapes for high-fidelity single-qubit transmon gates; reach 99.94% fidelity at 10 ns; identify the next research directions
- **What was lost**: 12 commits; pulse.py, simulate.py; results.tsv with the 7 experiments; next_steps.md with the 5 prioritised future directions (neural ODE pulses, two-qubit CZ gates, Lindblad-aware optimization, transfer learning across frequencies, novel parameterisations)
- **What survived**: lessons promoted to program.md (random initialisation is malpractice for parameterised search — always warm-start from a known-good baseline; physical floors mean pivot, not push; reproduce published SOTA on the same system as a Phase 0.5 calibration; small pilot before expensive optimisation)
- **To revisit**: QuTiP (or similar pulse-level simulator) is publicly available. Re-do Phase 0 lit review on optimal quantum control, rebuild the pulse parameterisation with explicit DRAG warm-start from the start (the lesson the project taught us), and re-derive the next_steps prioritisation.

**Recovery effort estimate per project**: 1–2 weeks each, dominated by the Phase 0 lit review. The methodology shortcuts in `program.md` should make the actual HDR loop substantially faster than the original runs.
