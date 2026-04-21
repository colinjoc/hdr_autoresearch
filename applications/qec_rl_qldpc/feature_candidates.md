# Feature Candidates — qec_rl_qldpc

Alias for `design_variables.md` — same content, organised here as *features* the RL agent or evaluator sees and varies. For the authoritative list and justifications, refer to `design_variables.md`.

## Structural features of candidate codes (observed by the RL policy network)

- **F-1: Stabilizer tableau** (binary matrix of stabilizers × qubits, X-part and Z-part). Size 2k×n. Primary observation in Olle 2024.
- **F-2: Tanner graph** (bipartite: qubits, stabilizers). Graph-structured input — natural for GNN policy (DV-10).
- **F-3: Running distance estimate** via Knill-Laflamme low-weight enumeration (partial-code distance).
- **F-4: Running automorphism-subgroup size** (or proxy per DV-4).
- **F-5: Running CSS-duality preservation indicator** (boolean: does S have equal X-type and Z-type generator counts related by duality?).
- **F-6: Running code-dimension k** (derived from stabilizer rank).
- **F-7: Current step index / episode progress** — positional encoding for the policy.
- **F-8: Noise-model summary statistics** — for noise-aware meta-agent conditioning (DV-15).
- **F-9: Target (n, k, d)** — for meta-agent (n,k)-conditioning (DV-15).

## Reward features

- **R-1: Knill-Laflamme distance reward** (α_d · d_current / d_target).
- **R-2: Transversal-gate-count reward** (α_g · g_useful_count).
- **R-3: Qubit-count penalty** (α_n · n / n_target).
- **R-4: Novelty / exploration bonus** (optional; DV-11).
- **R-5: Dense reward shaping** — partial-distance increments per step.
- **R-6: Terminal code-validity reward** — binary: is the final code a valid QEC code (rank conditions, commutativity) × reward bonus.

## Action features (what the policy outputs)

- **A-1: Gate type** (CNOT / H / S / CZ / SWAP / measurement).
- **A-2: Target qubits** (1 or 2 indices).
- **A-3: Gadget-type** (if gadgets enabled per DV-5).
- **A-4: Gadget position** (which qubits in the code the gadget acts on).
- **A-5: Action mask** — which actions are forbidden by DV-6 (symmetry / automorphism preservation).

## Evaluation features (for the Pareto front)

- **E-1: LER at p=10⁻³ under Bluvstein 2024 noise** (axis 1).
- **E-2: Transversal-Clifford-gate count** (axis 2).
- **E-3: Physical-qubit count n** (axis 3).
- **E-4: Secondary: syndrome-extraction circuit depth** (reported but not Pareto).
- **E-5: Secondary: BP+LSD decoding wall-clock** (reported but not Pareto).
- **E-6: Secondary: equivalence-class membership vs reference set** (for novelty check).

## Rationale summary

All features above are either (a) directly lifted from published RL-for-codes pipelines (Olle 2024 structural features; reward features lifted from Knill-Laflamme; action features from encoding-circuit action spaces), (b) our novel additions (transversal-gate-count reward, automorphism-aware action mask, novelty bonus), or (c) evaluation features for the Pareto front. See `design_variables.md` for per-feature references and hypothesis linkages.
