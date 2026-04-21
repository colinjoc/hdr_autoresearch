# Design Variables — qec_rl_qldpc

The RL agent's search is parametrised by the variables below. Each variable is (i) what it is, (ii) the candidate range, (iii) the justification with reference to `literature_review.md`, and (iv) the hypothesis in `research_queue.md` that varies it. Target ≥15 variables; we enumerate 20.

---

## Core reward-function variables

### DV-1: Reward weight on Knill-Laflamme distance term
- **What**: coefficient α_d in reward = α_d · (distance score) + ...
- **Range**: {0.5, 1.0, 2.0} (pre-registered for ablation; `publishability_review.md` suggests 5)
- **Justification**: Olle 2024 uses an implicit weight of 1.0 on KL reward. Our ablation swings this to see if distance prioritisation reshapes the Pareto front. [Refs: entries 8, 102 in papers.csv]
- **Hypothesis**: H-RL-2 (reward-weight sweep).

### DV-2: Reward weight on transversal-gate-count term
- **What**: coefficient α_g
- **Range**: {0.0 (ablation off), 0.3, 1.0, 3.0}
- **Justification**: This is the project's distinguishing axis. Weight must be calibrated so neither distance nor gate-count dominates trivially; we pre-register three non-zero settings for comparability. [Refs: 33, 34, 35]
- **Hypothesis**: H-RL-2, H-TG-3.

### DV-3: Reward weight on qubit-count penalty
- **What**: coefficient α_n (negative)
- **Range**: {-0.1, -0.3, -1.0}
- **Justification**: n-penalty keeps the search away from the trivial "use more qubits" solution. Needed in fixed-(n,k)-grid mode as a soft pressure. [Ref: proposal_v2 §3]
- **Hypothesis**: H-RL-2.

### DV-4: Transversal-gate-count measurement choice
- **What**: how "transversal-gate count" is computed
- **Range**: {rank of induced logical Clifford group, raw automorphism count, fold-transversal count only, permutation-subgroup size (proxy)}
- **Justification**: raw automorphism count admits reward hacking (§3.3 of lit review); rank of induced logical Clifford is the correct operational quantity but expensive. Proxies trade accuracy for speed. PER-1 profiles the options. [Refs: 33, 35]
- **Hypothesis**: H-TG-1, H-TG-4.

---

## Action-space variables

### DV-5: Action-space factorisation
- **What**: gate sequence vs stabilizer-generator vs gadget vs mixed
- **Range**: {encoding-circuit gates (Olle style), encoding-circuit + gadgets (arXiv:2503.11638), stabilizer-generator edits, hierarchical (template + fill)}
- **Justification**: encoding-circuit is Olle's choice; gadgets scale past n=20. Hierarchical is an untested option for Phase 2. [Refs: 8, 10]
- **Hypothesis**: H-ASC-1.

### DV-6: Symmetry prior on action space
- **What**: whether actions are restricted to symmetry-preserving transformations
- **Range**: {none, qubit-permutation invariance, CSS-duality preservation, automorphism-aware masking}
- **Justification**: symmetry priors were necessary to push past n=20 in OpenReview 2025. Automorphism-aware masking is our novel addition — actions that would break a target symmetry are masked out. [Refs: 12, OpenReview paper]
- **Hypothesis**: H-ASC-2.

### DV-7: Gate set
- **What**: which Clifford gates are available as primitive actions
- **Range**: {CNOT, H, S, CZ + H + S (Olle), extended with mid-circuit measurements, extended with SWAP}
- **Justification**: different gate sets produce different accessible manifolds. Olle 2024 uses a minimal CNOT+H+S set. For NA-relevant codes, CZ is the native gate. [Refs: 8, 63]
- **Hypothesis**: H-ASC-3.

### DV-8: Qubit-connectivity constraint
- **What**: connectivity graph on which gates can be applied
- **Range**: {all-to-all, 2D grid, 3D grid, long-range (NA-style), custom (device-matched)}
- **Justification**: all-to-all matches BB/Tanner-code reality on NA; 2D grid matches superconducting. Affects both the action mask and the discovered codes' hardware-relevance. [Refs: 50, 61]
- **Hypothesis**: H-HW-1.

---

## RL algorithm variables

### DV-9: RL algorithm
- **What**: policy-gradient family choice
- **Range**: {PPO (primary), SAC-discrete, MuZero, MCTS+AlphaZero-style value net}
- **Justification**: PPO is the proven Olle precedent; MCTS/AlphaZero works for combinatorial search (AlphaTensor, AlphaDev). [Refs: 115, 118, 119, 120, 137, 138]
- **Hypothesis**: H-RL-6.

### DV-10: Policy network architecture
- **What**: neural-network backbone
- **Range**: {MLP (Olle default), GNN on Tanner graph, transformer on stabilizer tableau, CNN on stabilizer-matrix image}
- **Justification**: GNN policies are natural for graph-structured problems; transformer might handle larger-n better. [Refs: 132, 133, 164, 165]
- **Hypothesis**: H-NET-1.

### DV-11: Exploration bonus
- **What**: intrinsic-motivation / entropy addition to reward
- **Range**: {none (off), entropy-bonus (standard PPO), RND, novelty-bonus (graph-canonical-form distance from visited codes)}
- **Justification**: code-discovery is sparse-reward; exploration crucial. Novelty-bonus is natural but risks reward-hacking via spurious "novelty". [Refs: 141, 142, 143, 144]
- **Hypothesis**: H-EXP-1.

### DV-12: Learning rate / PPO hyperparameters
- **What**: learning rate, clip range, entropy coefficient, GAE λ, batch size
- **Range**: standard PPO defaults with per-factor sweeps where needed
- **Justification**: ICLR Blog Track paper enumerates 37 implementation details; sensitivity is high. [Ref: 255]
- **Hypothesis**: H-RL-12 (hyperparameter sensitivity).

---

## Curriculum and meta-training variables

### DV-13: Curriculum schedule for n
- **What**: how the target n evolves during training
- **Range**: {fixed n, linear ramp 14 → target, exponential doubling, adaptive (increment when reward > threshold)}
- **Justification**: small-n is easier; starting small and scaling up reduces wasted compute. [Refs: 130, 131, 123]
- **Hypothesis**: H-CUR-1.

### DV-14: Curriculum schedule for distance target
- **What**: distance target vs training step
- **Range**: {fixed d, ramp from d=3 to d=target, noise-level ramp instead of distance}
- **Justification**: Olle 2024 increases noise rate as curriculum; equivalent to ramping distance requirement. [Ref: 8]
- **Hypothesis**: H-CUR-2.

### DV-15: Meta-agent conditioning
- **What**: what inputs condition the policy (noise model, target (n,k), target distance)
- **Range**: {noise-only (Olle), noise + (n,k), noise + (n,k) + target-family-prior}
- **Justification**: Olle 2024 shows noise-conditioning enables transfer across noise models. Extending to (n,k) conditioning is natural for our Pareto grid. [Ref: 8]
- **Hypothesis**: H-META-1.

---

## Final-evaluation variables (held fixed post-pre-registration, but listed for completeness)

### DV-16: Final-eval decoder
- **What**: which decoder for LER evaluation
- **Range**: pre-registered: {BP+LSD via `ldpc` for qLDPC; PyMatching v2 for topological; TN via Chubb for 2D exactness}
- **Justification**: decoder choice matters; pre-commit to prevent decoder-shopping. [Refs: 23, 20, 99]
- **Hypothesis**: H-PARETO-3 (decoder-sensitivity ablation — fixed for main result, varied for sensitivity).

### DV-17: Final-eval noise model
- **What**: noise model for LER evaluation
- **Range**: pre-registered: Bluvstein 2024 NA supplement.
- **Justification**: locks the primary comparison; sensitivity axis explored in H-NOISE-4.
- **Hypothesis**: H-NOISE-4.

### DV-18: (n,k) grid for Pareto comparison (PER-3)
- **What**: which (n,k) cells are evaluated
- **Range**: pre-registered grid (draft): (20,2), (25,2), (30,4), (30,6), (35,4), (40,6), (50,8), (50,12)
- **Justification**: PER-3 requires explicit pre-registration to prevent cell-cherry-picking.
- **Hypothesis**: n/a (locked by PER-3).

---

## Structural-novelty variables

### DV-19: Equivalence-relation choice (PER-2)
- **What**: equivalence relation for the novelty check
- **Range**: pre-registered: option 3 (Pauli-equivalence under qubit permutation + local Clifford). Sensitivity check: compare to options 2, 4 as stated in §5.7 of lit review.
- **Justification**: locks the novelty claim.
- **Hypothesis**: H-EQ-5.

### DV-20: Reference-set composition
- **What**: which codes go into the reference Pareto baseline
- **Range**: pre-registered: {small BB instances (Bravyi 2024 + Symons 2025 + self-dual 2510.05211), Tanner instances (2508.05095), HGP (Tillich-Zémor recipe), ECC Zoo qLDPC entries at n≤50, [[16,6,4]], RASCqL (2602.14273), SHYPS (2502.07150), asymmetric-HGP (2506.15905), fold-transversal BB (2407.03973)}
- **Justification**: reference set must be comprehensive enough to make dominance non-trivial AND reflect 2025-2026 SOTA automorphism-gate constructions.
- **Hypothesis**: n/a (locked); scoop-monitor can adds 2026 arrivals.

---

## Summary table (for Phase 0.5 protocol doc)

| # | Variable | Range | Lock-in stage | Reference |
|---|---|---|---|---|
| DV-1 | α_d reward weight | {0.5, 1.0, 2.0} | Phase 0.5 | PER-2 / proposal_v2 |
| DV-2 | α_g reward weight | {0.0, 0.3, 1.0, 3.0} | Phase 0.5 | proposal_v2 |
| DV-3 | α_n reward weight | {-0.1, -0.3, -1.0} | Phase 0.5 | proposal_v2 |
| DV-4 | Transversal-gate measure | {rank of induced Clifford (primary), proxies} | Phase 0.5 per PER-1 profile | §3.3 |
| DV-5 | Action-space factorisation | {encoding, +gadgets, stabilizer-edits, hierarchical} | Phase 0.5 | §6.2 |
| DV-6 | Symmetry prior | {none, permutation, CSS-duality, auto-masking} | Phase 1 ablation | OpenReview 2025 |
| DV-7 | Gate set | {minimal, CZ+H+S, extended} | Phase 0.5 | NA context |
| DV-8 | Connectivity | {all-to-all, 2D, long-range, device} | Phase 0.5 | NA / SC ablation |
| DV-9 | RL algorithm | {PPO, SAC-d, MCTS, MuZero} | Phase 1 ablation | §6.1 |
| DV-10 | Policy net | {MLP, GNN, transformer, CNN} | Phase 1 ablation | §6.1 |
| DV-11 | Exploration bonus | {none, entropy, RND, novelty} | Phase 1 | §6.5 |
| DV-12 | PPO hyperparameters | standard sweeps | Phase 1 | 37 details paper |
| DV-13 | Curriculum n | {fixed, linear, exp, adaptive} | Phase 1 | §6.4 |
| DV-14 | Curriculum d | {fixed, ramped, noise-ramp} | Phase 1 | Olle 2024 |
| DV-15 | Meta-agent conditioning | {noise, +({n,k}), +(family)} | Phase 2 | H-META-1 |
| DV-16 | Final decoder | BP+LSD/MWPM/TN committed | Phase 0.5 lock | Refs 23, 20, 99 |
| DV-17 | Final noise model | Bluvstein 2024 committed | Phase 0.5 lock | Ref 63 |
| DV-18 | (n,k) grid | pre-registered | Phase 0.5 lock | PER-3 |
| DV-19 | Equivalence relation | option 3 committed | Phase 0.5 lock | PER-2 |
| DV-20 | Reference set | pre-registered | Phase 0.5 lock | §4.4 |

---

Each variable's justification refers to a specific citation in `papers.csv` (where a specific number is not given, see `literature_review.md` for section-level context). The reference-level justification is load-bearing: any Phase 1 change to a locked variable must be explicitly revisited against the citation.
