# Project-scoped Knowledge Base — qec_rl_qldpc

Stylised facts compiled from the deep literature review (`literature_review.md`) and smoke test (`data_sources.md`). Each bullet has a citation by author+year (see `papers.csv`). Numbers are approximate unless stated otherwise — re-verify before Phase 1 training commits.

## RL-for-code-discovery: current scale limits

- **Olle 2024 qdx (arXiv:2311.04750)**: RL discovers [[n≤25, k=1, d≤5]] codes with Knill-Laflamme reward on a single GPU. Noise-aware meta-agent works. Roadmap targets n=100, d=10 but this is **NOT** delivered in the published paper. GitHub repo dormant since Dec 2024.
- **arXiv:2503.11638 RL-with-gadgets (2025)**: reaches [[n,1,d≤7]] and [[n,k,6]] for k≤7 on a single A100, with n reaching into the 30-60 range at d=6-7. Gadget (composite Clifford) action-space compression is the scaling lever.
- **arXiv:2502.14372 low-weight RL (2025)**: RL + weight-aware reward, n in tens-of-qubits range.
- **OpenReview 2025 symmetry-prior scaling**: [VERIFY scale] — symmetry priors let RL push beyond n=20.
- **Naive RL (no action-space compression)**: plateaus at n ≈ 12-15 due to exponential action-space.
- **Vectorised Clifford simulator (JAX)** is the scale floor: without it, RL at n=20 is infeasible on <20 GPUs.

## Reward cost per episode (our concern)

- **Knill-Laflamme reward** (Olle 2024 style): O(n² · enumerate-low-weight-errors) per call. Typical per-step cost ~milliseconds at n=20; scales to ~100 ms at n=50.
- **Automorphism-enumeration reward** (our addition, Zhu-Breuckmann style): O(|Aut(Tanner graph)| + logical-Clifford-classification). **Unprofiled at n=50.** nauty is fast on sparse graphs (seconds at n=30, minutes at n=50 worst-case) but the subsequent Pauli-correction and logical-Clifford classification adds cost. **PER-1 must profile this before any RL run.**
- **Reward fraction budget**: reward computation should be ≤ 20% of total RL step time; if > 50%, use proxy reward (see §Fallback proxies).

## Fallback proxy rewards (if full automorphism enumeration is too slow)

1. **Permutation-subgroup-size proxy**: count qubit-permutation subgroup preserving S; skip logical-Clifford classification.
2. **Tanner graph automorphism count** via nauty.
3. **Random automorphism sampling**: O(100) trials per episode; reward ∝ fraction of permutations preserving S.
4. **Precomputed family tables**: BB code automorphism is algebraic; precompute for BB-family codes.
5. **Graph-symmetry heuristic**: spectral-gap of the Tanner graph Laplacian; correlates with automorphism count but is O(n³).

## Code families and reference-set membership (for Pareto baseline)

- **Bivariate Bicycle (BB) codes**: [[l·m, 2k, d]] with k and d derived from polynomial parameters. `[[72,12,6]]`, `[[90,8,10]]`, `[[144,12,12]]` (gross code) are canonical small instances. [Bravyi 2024]
- **Self-dual BB codes**: subfamily with CSS duality; transversal Clifford directly from duality. [arXiv:2510.05211]
- **Covering-graph BB**: `[[64,14,8]]`, `[[144,14,14]]` h-covers. Non-trivially related to parent BB. [Symons et al. 2025]
- **Quantum Tanner codes**: left-right Cayley complex construction. Explicit small-n instances from [arXiv:2508.05095] — first source for finite-size Tanner codes to plug into our benchmarks.
- **Hypergraph product (HGP) codes**: from any pair of classical LDPC codes; distance √n. Small HGP from rate-1/2 random LDPC. [Tillich-Zémor 2014]
- **SHYPS**: subsystem HGP simplex codes; full Clifford transversal in O(m) rounds. [arXiv:2502.07150]
- **RASCqL**: hand-crafted automorphism-embedded qLDPC with 2-7× qubit reduction; 2026. [arXiv:2602.14273]
- **Asymmetric transversal-phase HGP**: transversal phase with k linear in n; O(1) phase-flip distance. [arXiv:2506.15905]
- **`[[16,6,4]]`**: Harvard/QuEra workhorse; low distance but exceptional rate. [Bluvstein 2024]
- **Reed-Muller `[[15,1,3]]`, Steane `[[7,1,3]]`, perfect `[[5,1,3]]`**: historical small-code baselines.

## Known transversal-gate capabilities (reference set)

- **Surface code**: transversal CNOT. No transversal H or S.
- **Steane [[7,1,3]]**: transversal Clifford (H, S, CNOT).
- **Reed-Muller [[15,1,3]]**: transversal T, NO transversal H.
- **Color code 2D**: transversal Clifford.
- **Self-dual BB**: transversal Clifford via self-duality.
- **SHYPS**: full Clifford in O(m) rounds (not transversal-depth-1 but transversal-depth-linear-in-m).
- **Fold-transversal BB** (Eberhardt-Steffan 2024): specific logical Clifford via Z_2 reflection.
- **Asymmetric HGP**: transversal phase gates with k linear in n.

## The equivalence relation (PER-2 commit)

**Pauli-equivalence under qubit permutation + local Clifford** — the canonical stabilizer-code equivalence.
- **Algorithm**: graph-state reduction → local-complementation orbit enumeration → nauty canonicalisation → compare canonical forms.
- **Cost**: seconds-to-minutes per pair at n ≤ 50.
- **Extensions**:
  - **Subsystem extension**: compare ungauged stabilizer representatives.
  - **Cover-code rule**: flag separately; n-changing relations NOT treated as equivalence but flagged.
- **Pre-registration**: commit the exact equivalence-checking Python module as a git hash BEFORE training.

## Noise model (final-eval)

Bluvstein 2024 NA supplement:
- CZ gate: depolarize2(0.007) + erasure2(0.003); fidelity ~99.3%.
- Atom loss per CZ: ~3×10⁻³ (detectable via fluorescence).
- Data-qubit decoherence: ~4% integrated over circuit (Ramsey).
- Transport error: ~10⁻³ per transport-cycle.
- Mid-circuit measurement: flip-probability ~10⁻² (VERIFY exact).
- SPAM: ~10⁻² per-qubit.
- Leakage: >80% converts to atom loss; residual <20% to hyperfine (non-Pauli).

**Stim realisation**: independent Pauli + erasure model; residual non-Pauli leakage treated as 10% LER error bar.

## Thresholds and overheads (as project context)

- Surface code circuit-level MWPM: ~0.7% threshold. Overhead at logical 10⁻⁹, p=10⁻³: distance 15-19, ~450-720 physical/logical.
- `[[144,12,12]]` BB: ~0.8% threshold, 24 physical/logical. [Bravyi 2024]
- Panteleev-Kalachev good qLDPC: threshold positive but finite-length numbers poor.
- Hyperbolic Floquet [[400,52,8]]: ~0.25% threshold.
- Bluvstein 2024 NA demonstrated below-threshold at d=4.

## What works (project-relevant)

- **PPO as primary RL algorithm** (Olle 2024 precedent, PureJaxRL integration).
- **Encoding-circuit-level action space** (vs stabilizer-generator-level).
- **Vectorised Clifford sim in JAX** (qdx lineage).
- **Knill-Laflamme reward** (generalises to any noise model).
- **Noise-aware meta-agent** (Olle 2024) — policy transfers across noise models.
- **Gadget action-space compression** (arXiv:2503.11638) — scales past n=20.
- **Symmetry priors** (OpenReview 2025) — scales past n=20.
- **Fold-transversal Clifford** as architecturally useful target (Eberhardt-Steffan 2024).
- **nauty / bliss for graph canonicalisation** at n ≤ 50.
- **BP+LSD / BP+OSD for qLDPC decoding** (Roffe `ldpc` package).
- **Stim + Sinter + CUDA-Q QEC** for final LER evaluation at ≥10⁶ shots/code.
- **Pareto archiving + NSGA-II** for multi-objective tracking.

## What does not work / pitfalls (project-relevant)

- **Naive RL past n≈15** without action-space compression — explodes.
- **Raw automorphism-count reward** — rewards trivially-symmetric codes with useless logical actions (reward hacking). Must use RANK of induced logical-Clifford subgroup.
- **Unbounded k in reward** — agent maximises distance by collapsing k→0. Must fix k ≥ 2 in reward or pre-register (n,k) grid.
- **Post-hoc (n,k)-cell selection** — reviewers detect this. Pre-register grid (PER-3).
- **Novelty-claim based on loose equivalence relation** — reviewers will break the claim. Commit option-3 relation (PER-2).
- **Decoder-shopping** across codes — commit BP+LSD for qLDPC, MWPM for topological, TN for baseline exactness.
- **Noise-model cherry-picking** — commit Bluvstein 2024 supplement.
- **Reward-cost profile ignored** — PER-1 is the day-0 gate.
- **Pauli-twirling non-Pauli errors** loses 10-50% LER accuracy. Treat as systematic error bar, not ground truth.
- **Training on n_fixed at once** — use curriculum starting from n≈14.
- **Forgetting to test the meta-agent across (n,k) combinations** — transfer claim must be verified empirically.

## Useful numbers

- qdx (Olle 2024): ~hundreds-of-thousands parallel Clifford rollouts per GPU-second.
- Stim speed (CPU): ~1 kHz shots for d=100 surface code.
- CUDA-Q QEC BP+OSD: 29-42× CPU speedup.
- PyMatching v2: ~10⁶ errors/core-second.
- nauty on sparse Tanner graphs: seconds at n≤30, minutes at n≤50.
- Pareto-front evaluation: 10⁶ shots × ~100 codes × 3 noise points ≈ 1 GPU-hour on one A100 (CUDA-Q QEC).
- Single PPO training step at n=30: ~seconds on one A100 (Olle 2024 extrapolation).
- Full training run to convergence at n=30: ~1-5 days on one A100 (budget).
- Bluvstein 2024 CZ fidelity: 99.3%.
- Bluvstein 2024 atom-loss per CZ: 3×10⁻³.

## Standard tooling stack (committed)

- **Simulation**: Stim + qdx fork (JAX) for RL; Stim + CUDA-Q QEC for final LER eval.
- **Decoder**: ldpc package (BP+LSD) for qLDPC; PyMatching v2 for topological reference codes.
- **MC driver**: Sinter.
- **Graph automorphism**: nauty + qLDPCOrg/qLDPC for logical-Clifford classification.
- **RL framework**: PureJaxRL (PPO).
- **GPU**: A100 (target), one GPU per training run per scale-curve point.

## Open problems at project scope

- **Best-known bound** on "useful-transversal-Clifford-gate count" as a function of (n, k, d) for small qLDPC: no tight lower bound. Open.
- **Lowest-n self-dual BB code**: known to exist at n=72 (Bravyi 2024) but smaller instances may exist. Open.
- **Does RL reward-shaping favour rediscovery or novel discovery?** Untested.
- **Transfer-learning across code families** via meta-agent: Olle 2024 demonstrates across noise models only; cross-family transfer is open.
- **Is there a qLDPC code at n≤50 with transversal non-Clifford gate?** Conjectured no (all known non-Clifford transversal constructions require higher dimension); our RL won't find one but failing to find it is informative.
- **Is the discovered Pareto front's structure robust to decoder variation?** Untested.

## Pre-registration commitments (from proposal_v2 and publishability_review)

- Reward weights pre-registered across 3 settings (5 suggested).
- (n,k) grid pre-registered per PER-3.
- Equivalence relation (PER-2): Pauli-equivalence under qubit permutation + local Clifford.
- Reference set: small BB, Tanner, HGP, ECC Zoo, [[16,6,4]], RASCqL, SHYPS, asymmetric HGP, self-dual BB, fold-transversal BB.
- Noise model: Bluvstein 2024 NA supplement.
- Scaling curve: n ∈ {20, 25, 30, 35, 40, 50}.
- Kill conditions: n_max < 35 (scale), Pareto-dominated, structural-novelty all-equivalent.

## Scoop-risk monitor

- 4-weekly arxiv scan for combinations of {RL, code discovery, automorphism, transversal, qLDPC, fold-transversal, BB} at n ≥ 30.
- Specific groups to watch: Photonic Inc. (SHYPS line), Zhu-Breuckmann line, Marquardt group (qdx origin), DeepMind (AlphaQubit-adjacent), IBM Quantinuum.
- Scoop-window estimate: 3-6 months from Phase 0 completion (2026-04-20).
