# Research Queue — qec_rl_qldpc

Status: **Phase 0 deep-literature-review complete (2026-04-20)**. This file now contains:
- 3 Phase 0.25 `pre-empt-reviewer` items (PER-1..PER-3) — **preserved verbatim from the prior file**.
- 100+ Phase 0 hypotheses populated from the deep scoped literature review and smoke test, grouped by theme.

Each hypothesis has: Bayesian prior (probability it outperforms current best); Mechanism (why it might work); Design variable(s) touched (see `design_variables.md`); Metric of success; Baseline; Estimated cost (GPU-hours).

---

## Pre-empt-reviewer items (from Phase 0.25 publishability review)

These are the top three killer objections raised by the Phase 0.25 reviewer at npj Quantum Information. Every one must be addressed in the Phase 2 experiment plan, pro-actively, so that the paper reviewer cannot land the same point when the manuscript is submitted.

### PER-1 [pre-empt-reviewer] Zhu–Breuckmann automorphism-check wall-clock at scale
- **Objection:** Per-episode reward cost (automorphism-gate identification via Zhu–Breuckmann) may dominate RL wall-clock and make n=50 infeasible on one A100, silently collapsing the scale claim.
- **Required action (day 0, before scaling curve):** Profile the Zhu–Breuckmann automorphism check on representative stabilizer matrices at n ∈ {20, 30, 50}. Report median + p95 wall-clock per call. Must pass before the n=20→50 scaling curve starts.
- **Design variable:** automorphism-search implementation + cache strategy.
- **Metric:** reward-computation wall-clock as fraction of total RL step.
- **Baseline:** Olle 2024 `qdx` step time at n=20.
- **Prior:** 60% the reward-cost is tractable with caching; 40% it will force a coarser gate-count proxy.

### PER-2 [pre-empt-reviewer] Equivalence-relation specification for structural-novelty
- **Objection:** The structural-novelty criterion (proposal_v2 §2) uses "graph-automorphism-equivalent" but this is under-specified. If two codes have isomorphic Tanner graphs yet different stabilizer generators, does that count as equivalent? The answer determines whether rediscovered BB-like rotations are excluded (paper OK) or accepted (paper collapses to "RL rediscovers known families").
- **Required action:** Lock the equivalence relation in `proposal_v3` or a Phase 0.5 protocol doc, with justification. Default: **Pauli-equivalence under qubit permutation + local Clifford**. Commit this as a pre-registered hash before any RL run.
- **Design variable:** equivalence-relation definition.
- **Metric:** fraction of Pareto-optimal discovered codes flagged equivalent to any reference code.
- **Baseline:** reference-set enumeration under the chosen relation.
- **Prior:** this is the single most brittle novelty claim; 50% the locked relation gives acceptable non-equivalents at n≥35, 50% it does not.

### PER-3 [pre-empt-reviewer] Pre-registered (n,k) grid for Pareto comparison
- **Objection:** "Matched (n,k)" can be gamed — if the reference set is weak at specific (n,k) cells, the Pareto claim becomes cosmetic. Reviewers at npj QI will demand a pre-registered grid that includes both reference and candidate codes at every cell.
- **Required action:** Pre-register the (n,k) grid. Rule: each cell must contain at least one reference code (from {small BB, Tanner, hypergraph-product, ECC Zoo, [[16,6,4]]}) AND at least one discovered candidate code. Cells that do not satisfy this post-hoc are reported as "unexplored" — NOT included in dominance claims.
- **Design variable:** grid spec and reference-population strategy.
- **Metric:** Pareto-dominance fraction at pre-registered cells only.
- **Baseline:** best-reference Pareto front per cell.
- **Prior:** 70% a defensible grid exists at n ≤ 35; 30% the grid is sparse enough that the headline must be narrowed.

---

## Phase 0 hypotheses — populated from deep literature review

Grouped by the 7 lit-review themes.

---

### Theme 1: RL for quantum code discovery — H-RL-*

#### H-RL-1: PPO baseline reproduces Olle 2024 at n=20, d=5
- **Mechanism:** Re-run of published result to verify our fork/reimplementation is faithful.
- **DV:** DV-9 (PPO), DV-5 (encoding-circuit).
- **Metric:** reach d=5 at n=20 in ≤ 12 GPU-hours; match Olle reported reward curve.
- **Baseline:** Olle 2024 published curve.
- **Prior:** 85% it reproduces cleanly; 10% minor divergence from JAX version changes; 5% qdx fork is broken.
- **Cost:** 12 GPU-hours.

#### H-RL-2: Reward-weight sweep across (α_d, α_g, α_n) ∈ 3×3×3 settings changes the Pareto front composition by ≥30% at n=30
- **Mechanism:** Reward weights drive policy convergence; Pareto composition is sensitive.
- **DV:** DV-1, DV-2, DV-3.
- **Metric:** fraction of Pareto-optimal codes differing between any two reward-weight settings.
- **Baseline:** single setting α_d=α_g=1.0, α_n=-0.3.
- **Prior:** 90% the front shifts measurably; 5% flat landscape; 5% all settings fail.
- **Cost:** 9 settings × 1 GPU-day = 216 GPU-hours.

#### H-RL-3: Gadgets (arXiv:2503.11638 action space) compose with our transversal-gate reward to reach n=40 in 1 week
- **Mechanism:** Gadgets compress action space; our reward is gadget-agnostic.
- **DV:** DV-5.
- **Metric:** PPO converges to valid code at n=40 within 168 GPU-hours.
- **Baseline:** encoding-circuit-only RL timing out at n≈30.
- **Prior:** 70%.
- **Cost:** 168 GPU-hours.

#### H-RL-4: Symmetry-aware action-masking (automorphism-preserving) reduces wall-clock to convergence by ≥3× at n=30
- **Mechanism:** Masking actions that break CSS duality or target symmetry cuts the effective branching factor.
- **DV:** DV-6.
- **Metric:** median training step count to reach d=5 at n=30.
- **Baseline:** unmasked PPO.
- **Prior:** 60%.
- **Cost:** 48 GPU-hours (two runs).

#### H-RL-5: MCTS+AlphaZero-style value network beats PPO on codes at n≥30 with transversal-gate reward
- **Mechanism:** Combinatorial search benefits from tree lookahead; AlphaTensor precedent.
- **DV:** DV-9.
- **Metric:** final reward at equal GPU-hour budget.
- **Baseline:** PPO at the same budget.
- **Prior:** 40% it wins; 30% ties; 30% loses (PPO is more sample-efficient on sparse reward).
- **Cost:** 120 GPU-hours.

#### H-RL-6: Noise-aware meta-agent transfers across (n,k) pairs at fixed noise model
- **Mechanism:** Policy parameters condition on (n,k); generalises beyond Olle's noise-conditioning.
- **DV:** DV-15.
- **Metric:** zero-shot reward on unseen (n,k) ≥ 50% of fine-tuned reward.
- **Baseline:** per-(n,k) from-scratch training.
- **Prior:** 50%.
- **Cost:** 96 GPU-hours.

#### H-RL-7: Knill-Laflamme reward is sufficient on CSS qLDPC at n≤50 without stabilizer-weight regularisation
- **Mechanism:** KL reward identifies distance; separate weight reward (arXiv:2502.14372) is complementary but not needed for our primary objective.
- **DV:** (none, negative-control ablation).
- **Metric:** discovered codes at n=30 have minimum-weight stabilizer ≤ threshold without weight reward.
- **Baseline:** arXiv:2502.14372 with weight reward.
- **Prior:** 70% KL alone is fine at small n; 30% weights go unbounded.
- **Cost:** 24 GPU-hours.

#### H-RL-8: Policy network as GNN on Tanner graph outperforms MLP at n≥35
- **Mechanism:** GNN respects graph structure; parameter-efficient.
- **DV:** DV-10.
- **Metric:** final reward at equal budget.
- **Baseline:** MLP policy (Olle default).
- **Prior:** 55%.
- **Cost:** 48 GPU-hours.

#### H-RL-9: Transformer policy on stabilizer tableau outperforms GNN at n≥40
- **Mechanism:** Transformers handle variable-length sequences; can attend to long-range stabilizer correlations.
- **DV:** DV-10.
- **Metric:** final reward at equal budget.
- **Baseline:** GNN.
- **Prior:** 45%.
- **Cost:** 72 GPU-hours.

#### H-RL-10: Episodic-replay of near-reference codes as curriculum accelerates discovery
- **Mechanism:** Starting episodes at known reference codes and asking the policy to propose modifications accelerates convergence by providing strong priors.
- **DV:** DV-13.
- **Metric:** training steps to reach target reward.
- **Baseline:** random-init policy.
- **Prior:** 55%.
- **Cost:** 24 GPU-hours.

#### H-RL-11: Olle 2024 meta-agent transfer across reward-weight settings
- **Mechanism:** Policy conditioned on α_g discovers different codes at different settings from one training run.
- **DV:** DV-15.
- **Metric:** transfer loss to each weight-setting ≤ 20% of full per-setting training.
- **Baseline:** per-setting training.
- **Prior:** 45%.
- **Cost:** 48 GPU-hours.

#### H-RL-12: PPO hyperparameter sweep (37 details paper) accelerates convergence by ≥2× at n=30
- **Mechanism:** Hyperparameter defaults not tuned for code-discovery MDP.
- **DV:** DV-12.
- **Metric:** median training wall-clock.
- **Baseline:** Olle 2024 defaults.
- **Prior:** 60%.
- **Cost:** 96 GPU-hours (sweep).

#### H-RL-13: RND-style intrinsic motivation improves Pareto-front diversity
- **Mechanism:** Intrinsic novelty reward pushes exploration into under-visited code-families.
- **DV:** DV-11.
- **Metric:** number of distinct code-family members on the Pareto front.
- **Baseline:** no exploration bonus.
- **Prior:** 40%.
- **Cost:** 48 GPU-hours.

#### H-RL-14: Distributed actor-learner (RLlib/ACME) parallelism scales to 8 A100s
- **Mechanism:** More parallel environments = faster sample accumulation.
- **DV:** n/a (infrastructure).
- **Metric:** training wall-clock at fixed sample budget.
- **Baseline:** single-A100 PPO.
- **Prior:** 70% linear speedup up to 4 GPUs; 50% up to 8 GPUs; synchronisation overhead dominates beyond.
- **Cost:** 32 GPU-hours.

#### H-RL-15: Training at mixed (n,k) simultaneously (shared policy) beats fixed-(n,k) training at the same budget
- **Mechanism:** Sample sharing across related tasks is the meta-agent promise.
- **DV:** DV-15.
- **Metric:** average reward across (n,k) grid.
- **Baseline:** per-(n,k) separate training.
- **Prior:** 50%.
- **Cost:** 96 GPU-hours.

#### H-RL-16: SAC-discrete as alternative to PPO at n=30
- **Mechanism:** Max-entropy RL handles sparse reward better; implicit exploration.
- **DV:** DV-9.
- **Metric:** final reward at equal budget.
- **Baseline:** PPO.
- **Prior:** 30% it wins; 40% ties; 30% loses.
- **Cost:** 48 GPU-hours.

#### H-RL-17: Rediscovery-detection shaping term accelerates novelty-discovery
- **Mechanism:** Penalise codes close to reference set during training to steer exploration toward novel regions.
- **DV:** DV-11 adjacent.
- **Metric:** fraction of non-equivalent Pareto codes.
- **Baseline:** no rediscovery penalty.
- **Prior:** 40% positive effect; 30% reward-hacking ruins it.
- **Cost:** 48 GPU-hours.

#### H-RL-18: Code-switching-pipeline RL (target: code A + code B pair for universality) is feasible at n_A+n_B ≤ 50
- **Mechanism:** Joint RL over a pair of codes with the constraint that code-switching between them gives universality.
- **DV:** new (compound action space).
- **Metric:** discovers any (A, B) pair with certified code-switch.
- **Baseline:** none — untested.
- **Prior:** 25% (exploratory).
- **Cost:** 120 GPU-hours.

#### H-RL-19: Self-supervised stabilizer-tableau pretraining accelerates downstream RL
- **Mechanism:** Pretrain policy network on random-stabilizer reconstruction task; fine-tune for code-discovery.
- **DV:** DV-10 adjacent.
- **Metric:** fine-tuning convergence speed.
- **Baseline:** random-init policy.
- **Prior:** 35%.
- **Cost:** 72 GPU-hours.

#### H-RL-20: Mixture-of-experts policy for per-family code discovery
- **Mechanism:** MoE routing to specialised sub-policies per code family (BB / HGP / Tanner).
- **DV:** DV-10.
- **Metric:** final reward on mixed tasks.
- **Baseline:** monolithic policy.
- **Prior:** 35%.
- **Cost:** 96 GPU-hours.

---

### Theme 2: Small qLDPC code families — H-QLDPC-*

#### H-QLDPC-1: RL discovers a [[n≤35, k≥4, d≥5]] BB-like code not in the Bravyi-2024 enumeration
- **Mechanism:** The BB parameter space is large; RL can sample points missed by systematic algebraic search.
- **DV:** DV-1, DV-2.
- **Metric:** discovered code is a BB by structure but not in Bravyi 2024 Table or Eberhardt-Steffan 2024 enumeration.
- **Baseline:** Bravyi 2024 and Eberhardt-Steffan 2024 enumerations.
- **Prior:** 35%.
- **Cost:** 48 GPU-hours.

#### H-QLDPC-2: RL discovers a non-BB qLDPC code at (n=30, k=6, d=5) dominating the hypergraph-product reference on the transversal-gate axis
- **Mechanism:** Transversal-gate reward pushes exploration away from generic HGP toward BB/self-dual-like symmetry.
- **DV:** DV-2.
- **Metric:** transversal-Clifford-gate count > best HGP at same (n,k,d).
- **Baseline:** best HGP.
- **Prior:** 40%.
- **Cost:** 72 GPU-hours.

#### H-QLDPC-3: Fold-transversal BB codes form a dense subset of the Pareto front
- **Mechanism:** Eberhardt-Steffan 2024 fold-transversal analysis suggests the BB family is naturally Pareto-optimal on transversal-gates.
- **DV:** n/a (structural analysis).
- **Metric:** fraction of Pareto-optimal discovered codes that are fold-transversal.
- **Baseline:** Pareto front without restriction.
- **Prior:** 45%.
- **Cost:** 12 GPU-hours (analysis).

#### H-QLDPC-4: Covering-graph BB codes (Symons et al. 2025) dominate non-cover BB at matched (n,k) on LER
- **Mechanism:** Covers introduce auxiliary redundancy; may improve decoder performance.
- **DV:** n/a (reference analysis).
- **Metric:** LER at p=10⁻³ Bluvstein noise.
- **Baseline:** non-cover BB.
- **Prior:** 50%.
- **Cost:** 8 GPU-hours.

#### H-QLDPC-5: Self-dual BB codes (arXiv:2510.05211) Pareto-dominate the reference set within their (n,k) footprint
- **Mechanism:** Self-duality gives free transversal H; distance and LER are competitive.
- **DV:** n/a (reference analysis).
- **Metric:** Pareto-optimal flag.
- **Baseline:** full reference set.
- **Prior:** 70% yes they do; 30% they tie with SHYPS.
- **Cost:** 8 GPU-hours.

#### H-QLDPC-6: Small Tanner codes (arXiv:2508.05095) are dominated by HGP at matched (n,k) below n=40
- **Mechanism:** Tanner asymptotic advantage kicks in only at large n; small-n instances carry construction overhead.
- **DV:** n/a (analysis).
- **Metric:** Pareto dominance.
- **Baseline:** HGP.
- **Prior:** 60%.
- **Cost:** 8 GPU-hours.

#### H-QLDPC-7: There exists at least one (n,k) cell where no reference code is Pareto-optimal vs a discovered RL code
- **Mechanism:** The project's headline — strict Pareto dominance at at-least-one cell.
- **DV:** (all project DVs).
- **Metric:** boolean.
- **Baseline:** reference Pareto front.
- **Prior:** 55%.
- **Cost:** included in main experimental plan.

#### H-QLDPC-8: Discovered codes at n≤30 include new self-dual BB-like structures not in the 2025 enumeration
- **Mechanism:** RL explores polynomial space beyond human-curated choices.
- **DV:** DV-6, DV-2.
- **Metric:** discovery of distinct self-dual BB instances.
- **Baseline:** arXiv:2510.05211 enumeration.
- **Prior:** 30%.
- **Cost:** 48 GPU-hours.

#### H-QLDPC-9: RASCqL-equivalent codes are rediscovered in ≥20% of RL runs at n=35
- **Mechanism:** RASCqL's automorphism-embedded structure is a strong attractor under our reward.
- **DV:** n/a (analysis).
- **Metric:** fraction of discovered Pareto-optimal codes equivalent to RASCqL.
- **Baseline:** 0% rediscovery (if reward doesn't match).
- **Prior:** 50% (expected; must be flagged as non-contribution per §2 proposal_v2).
- **Cost:** free (from main runs).

#### H-QLDPC-10: SHYPS-equivalent codes are rediscovered
- **Mechanism:** SHYPS is explicitly built for transversal Clifford; our reward pushes toward this corner.
- **DV:** n/a.
- **Metric:** equivalence-check fraction.
- **Baseline:** 0%.
- **Prior:** 40% (must be flagged).
- **Cost:** free (from main runs).

#### H-QLDPC-11: Non-CSS qLDPC codes emerge at reduced action-space priors
- **Mechanism:** CSS is a prior; without it the agent may discover non-CSS constructions with unknown properties.
- **DV:** DV-6 (off CSS preservation).
- **Metric:** discovery of valid non-CSS codes.
- **Baseline:** CSS-only enumeration.
- **Prior:** 30% non-CSS found; 70% still converges to CSS.
- **Cost:** 48 GPU-hours.

#### H-QLDPC-12: Discovered small-n qLDPC codes transfer to n=100 via known cover-code constructions
- **Mechanism:** If the discovered code has a known lifting structure, cover-code construction extends it.
- **DV:** n/a (post-hoc).
- **Metric:** cover-code extension exists and preserves distance scaling.
- **Baseline:** n=100 literature construction.
- **Prior:** 25% (exploratory).
- **Cost:** 4 GPU-hours (analysis).

#### H-QLDPC-13: Asymmetric-distance codes (like arXiv:2506.15905) appear on the Pareto front at k≥8
- **Mechanism:** Asymmetric distance trades off phase-flip for transversal phase; at high k this may Pareto-dominate.
- **DV:** n/a (analysis).
- **Metric:** Pareto optimality.
- **Baseline:** symmetric-distance codes.
- **Prior:** 35%.
- **Cost:** free.

#### H-QLDPC-14: BiBiEQ-like erasure-aware BB variants are competitive under full Bluvstein NA noise
- **Mechanism:** BB + erasure conversion tailored to NA; should Pareto-dominate generic BB under our noise model.
- **DV:** n/a (reference analysis).
- **Metric:** Pareto optimality.
- **Baseline:** generic BB.
- **Prior:** 55%.
- **Cost:** 4 GPU-hours.

#### H-QLDPC-15: Discovered codes include an unexplored [[n, 2, 4]] family at n≤30
- **Mechanism:** Low-k, low-distance regime is not well-populated in the reference enumeration.
- **DV:** DV-18.
- **Metric:** new family discovery.
- **Baseline:** reference set.
- **Prior:** 35%.
- **Cost:** 48 GPU-hours.

---

### Theme 3: Transversal/automorphism gates — H-TG-*

#### H-TG-1: Rank-of-logical-Clifford reward outperforms raw-automorphism-count reward (no reward-hacking)
- **Mechanism:** Raw count rewards trivially-symmetric codes; rank-based reward identifies useful operations.
- **DV:** DV-4.
- **Metric:** Pareto-optimal codes have higher induced-Clifford rank when rank-reward is used.
- **Baseline:** raw-count reward.
- **Prior:** 85%.
- **Cost:** 48 GPU-hours.

#### H-TG-2: At n≤50 no qLDPC code exists with transversal non-Clifford gate
- **Mechanism:** Theorem-adjacent: transversal non-Clifford requires higher dimension (Bravyi-König 2013 generalised). Expected negative result, informative for the field.
- **DV:** (exploration over CSS-T-like codes).
- **Metric:** no RL run produces a code with transversal T / CCZ / S^1/2.
- **Baseline:** CSS-T codes (Vuillot 2019) require d→∞ for asymptotic advantage.
- **Prior:** 85% no code found.
- **Cost:** included in main runs.

#### H-TG-3: Transversal-gate reward shifts discovered codes toward symmetric-graph structures
- **Mechanism:** Symmetry produces automorphisms; reward aligns with symmetry.
- **DV:** DV-2.
- **Metric:** Tanner graph symmetry index of discovered codes > reference.
- **Baseline:** reward without DV-2 term.
- **Prior:** 80%.
- **Cost:** 24 GPU-hours.

#### H-TG-4: Fold-transversal-count proxy reward achieves 80% of full-rank-reward Pareto front at 1/10 compute
- **Mechanism:** Fold-transversal is a cheap subset of full logical-Clifford classification.
- **DV:** DV-4.
- **Metric:** Pareto-front overlap between full and proxy rewards.
- **Baseline:** full reward.
- **Prior:** 50%.
- **Cost:** 48 GPU-hours.

#### H-TG-5: Non-CSS qLDPC codes admit richer transversal gate sets than CSS
- **Mechanism:** Non-CSS constructions can have non-separable stabilizer structure — potentially more symmetry.
- **DV:** DV-6 (off CSS preservation).
- **Metric:** transversal-gate count on discovered non-CSS codes.
- **Baseline:** CSS-only codes.
- **Prior:** 30%.
- **Cost:** 48 GPU-hours.

#### H-TG-6: Automorphism-aware action masking is computable online per step at reasonable cost
- **Mechanism:** Masking requires automorphism enumeration at the partial-code state — may be too slow.
- **DV:** DV-6.
- **Metric:** masking overhead ≤ 50% of base step time.
- **Baseline:** no masking.
- **Prior:** 40%.
- **Cost:** 24 GPU-hours (profiling).

#### H-TG-7: Discovered codes at n=30 have ≥|Z2| fold-transversal symmetry
- **Mechanism:** Fold-transversal is natural under our reward; at n=30 we should find at least Z_2 fold-transversal.
- **DV:** n/a.
- **Metric:** fold-symmetry count in discovered codes.
- **Baseline:** reference BB (has Z_2).
- **Prior:** 65%.
- **Cost:** free.

#### H-TG-8: Larger reference set (adding 2026 arxiv preprints) shrinks discovered-code novelty claim by 20-40%
- **Mechanism:** More references = more equivalence-check matches.
- **DV:** DV-20.
- **Metric:** novelty fraction.
- **Baseline:** 2024-2025 reference set only.
- **Prior:** 80% this is true.
- **Cost:** 8 GPU-hours.

#### H-TG-9: Transversal-gate identifiability at Pareto-optimal discovered codes is ≥80%
- **Mechanism:** The qLDPCOrg/qLDPC tool can classify most automorphism-induced gates; residual 20% may require manual analysis.
- **DV:** n/a (eval).
- **Metric:** classification success rate.
- **Baseline:** manual.
- **Prior:** 70%.
- **Cost:** 8 GPU-hours.

#### H-TG-10: Training with mixed-reward (alternating weight settings across episodes) yields wider Pareto front than fixed-setting training
- **Mechanism:** Implicit curriculum over reward landscape.
- **DV:** DV-1, DV-2, DV-3.
- **Metric:** Pareto-front coverage.
- **Baseline:** fixed weights.
- **Prior:** 40%.
- **Cost:** 48 GPU-hours.

#### H-TG-11: At n=50, RL finds at least one code with transversal-Clifford-gate count > reference SHYPS at matched k
- **Mechanism:** The scale regime SHYPS targets is n≥100 (they claim O(m) gates); at n=50 SHYPS may be sub-optimal.
- **DV:** n/a (primary outcome).
- **Metric:** gate count.
- **Baseline:** SHYPS at matched k.
- **Prior:** 35%.
- **Cost:** free.

#### H-TG-12: Code-discovery with a "CSS-duality preservation" action mask finds more self-dual codes
- **Mechanism:** Mask reinforces the symmetry we want.
- **DV:** DV-6.
- **Metric:** fraction of discovered self-dual.
- **Baseline:** unmasked.
- **Prior:** 70%.
- **Cost:** 24 GPU-hours.

#### H-TG-13: Discovered codes with large logical-Clifford-rank have lower LER (correlation)
- **Mechanism:** Symmetric codes have regular Tanner graphs, which help BP decoding.
- **DV:** n/a.
- **Metric:** Pearson correlation between rank and LER.
- **Baseline:** no correlation.
- **Prior:** 60%.
- **Cost:** free.

#### H-TG-14: Transversal-CNOT across copies is not a useful axis at fixed-copy evaluation
- **Mechanism:** Every CSS code has transversal bit-wise CNOT across copies; not a differentiator.
- **DV:** DV-4.
- **Metric:** uniform free transversal CNOT across all discovered codes.
- **Baseline:** universal.
- **Prior:** 99%.
- **Cost:** free.

#### H-TG-15: Automorphism group of discovered codes often includes non-Z2 subgroups (e.g., cyclic Z_n/2)
- **Mechanism:** BB-family codes have cyclic automorphisms from the torus structure.
- **DV:** n/a (analysis).
- **Metric:** largest cyclic subgroup of Aut.
- **Baseline:** Z_2 fold.
- **Prior:** 55%.
- **Cost:** free.

---

### Theme 4: Pareto-dominance benchmarking — H-PARETO-*

#### H-PARETO-1: Pareto-dominance claim is robust to reward-weight variation within pre-registered range
- **Mechanism:** The 3-setting ablation should give overlapping Pareto fronts; robustness = each discovered Pareto-optimal code is Pareto-optimal under at least 2 of 3 settings.
- **DV:** DV-1, DV-2, DV-3.
- **Metric:** overlap fraction.
- **Baseline:** single setting.
- **Prior:** 60%.
- **Cost:** 72 GPU-hours.

#### H-PARETO-2: Reference Pareto front at our (n,k) grid has ≥2 codes per cell
- **Mechanism:** Validates PER-3 pre-registration — required for dominance comparison at each cell.
- **DV:** DV-18.
- **Metric:** min-over-cells reference count.
- **Baseline:** pre-registration.
- **Prior:** 70%.
- **Cost:** 16 GPU-hours (enumeration + eval).

#### H-PARETO-3: Discovered Pareto-optimal codes dominate reference at ≥60% of pre-registered cells
- **Mechanism:** The headline claim; partial dominance counts for the paper if structural-novelty holds.
- **DV:** (all).
- **Metric:** dominance-cell fraction.
- **Baseline:** reference.
- **Prior:** 40%.
- **Cost:** included.

#### H-PARETO-4: Pareto front shape changes qualitatively when decoder is swapped (BP+LSD → BP+OSD → TN)
- **Mechanism:** Decoder sensitivity.
- **DV:** DV-16.
- **Metric:** Pareto-front shift.
- **Baseline:** committed decoder.
- **Prior:** 55%.
- **Cost:** 32 GPU-hours.

#### H-PARETO-5: Pareto front robust to p variation in [10⁻⁴, 10⁻²]
- **Mechanism:** Dominance relations should be stable across the realistic p range.
- **DV:** DV-17 sensitivity.
- **Metric:** front overlap.
- **Baseline:** p = 10⁻³.
- **Prior:** 60%.
- **Cost:** 24 GPU-hours.

#### H-PARETO-6: Pareto front robust to noise-model swap (Bluvstein → SI1000)
- **Mechanism:** Codes that win under NA noise should also win under SC noise — implies hardware-independence.
- **DV:** DV-17.
- **Metric:** front overlap.
- **Baseline:** Bluvstein committed.
- **Prior:** 45%.
- **Cost:** 24 GPU-hours.

#### H-PARETO-7: Syndrome-extraction depth (secondary metric) correlates negatively with transversal-gate count
- **Mechanism:** Codes with more transversal structure often have lower-weight stabilizers → shallower syndrome extraction.
- **DV:** n/a (analysis).
- **Metric:** Pearson correlation.
- **Baseline:** no correlation.
- **Prior:** 60%.
- **Cost:** free.

#### H-PARETO-8: BP+LSD wall-clock (secondary metric) is not on the Pareto front's dominance rule but should be reported
- **Mechanism:** Discovered codes with fewer low-weight stabilizers may need longer BP convergence — operationally relevant but not in our three axes.
- **DV:** (eval).
- **Metric:** reported in paper.
- **Baseline:** BP+LSD default.
- **Prior:** informational.
- **Cost:** free.

#### H-PARETO-9: Composite objective (weighted sum of axes) ranking agrees with Pareto dominance at ≥80% of points
- **Mechanism:** Pareto is conservative; a single-composite-objective ranking usually agrees but is less defensible.
- **DV:** n/a.
- **Metric:** agreement fraction.
- **Baseline:** composite ranking.
- **Prior:** 70%.
- **Cost:** free.

#### H-PARETO-10: Discovered Pareto-optimal codes Pareto-dominate reference Pareto-optimal codes in bootstrapped confidence
- **Mechanism:** Statistical rigour on the claim — 10⁶-shot bootstrap intervals do not overlap.
- **DV:** n/a.
- **Metric:** CI non-overlap fraction.
- **Baseline:** point estimates.
- **Prior:** 60%.
- **Cost:** 48 GPU-hours (bootstrap).

---

### Theme 5: Equivalence relations and novelty — H-EQ-*

#### H-EQ-1: Pauli-equivalence check at n=50 runs in ≤ 60 seconds per pair
- **Mechanism:** Graph-state reduction + LC-orbit + nauty tractable at small n.
- **DV:** n/a.
- **Metric:** wall-clock.
- **Baseline:** worst case (minutes).
- **Prior:** 70%.
- **Cost:** 4 GPU-hours (profile).

#### H-EQ-2: Subsystem-to-stabilizer reduction for SHYPS-like codes preserves our equivalence
- **Mechanism:** Ungauging SHYPS to a stabilizer code; the resulting code is or is not equivalent to a discovered stabilizer code.
- **DV:** n/a.
- **Metric:** boolean test.
- **Baseline:** SHYPS references.
- **Prior:** 50% — untested.
- **Cost:** 8 GPU-hours.

#### H-EQ-3: Cover-code detection algorithm has no false negatives at n≤50
- **Mechanism:** h-cover detection is a structural test; for small h it is enumerable.
- **DV:** n/a.
- **Metric:** false-negative rate.
- **Baseline:** manual check.
- **Prior:** 70%.
- **Cost:** 4 GPU-hours.

#### H-EQ-4: Stabilizer-generator normalisation does not change the equivalence class
- **Mechanism:** Choosing a canonical generator set should not matter; verify.
- **DV:** n/a.
- **Metric:** class invariance.
- **Baseline:** expected invariance.
- **Prior:** 95% invariant; 5% subtle bug.
- **Cost:** 4 GPU-hours.

#### H-EQ-5: Novelty verdict is robust across equivalence options (2, 3, 4)
- **Mechanism:** The claim should hold under stricter equivalences (option 4) too.
- **DV:** DV-19.
- **Metric:** novelty fraction at each option.
- **Baseline:** option 3 (committed).
- **Prior:** 50% robust; 50% novelty shrinks at option 4.
- **Cost:** 8 GPU-hours.

#### H-EQ-6: The equivalence-checking Python module's git hash is committed BEFORE any RL training run
- **Mechanism:** Pre-registration integrity.
- **DV:** DV-19.
- **Metric:** git-log timestamp.
- **Baseline:** commitment.
- **Prior:** 100% (procedural).
- **Cost:** 0.

#### H-EQ-7: Published reference codes (Bravyi 2024, Eberhardt-Steffan 2024, SHYPS 2502.07150, RASCqL 2602.14273) are not equivalent to each other
- **Mechanism:** Reference set members should be structurally distinct; verify.
- **DV:** n/a.
- **Metric:** pairwise equivalence matrix.
- **Baseline:** expected distinct.
- **Prior:** 95%.
- **Cost:** 4 GPU-hours.

#### H-EQ-8: Fold-transversal BB codes form distinct equivalence classes from BB automorphism gates
- **Mechanism:** Subtleties in equivalence might collapse them together.
- **DV:** n/a.
- **Metric:** classification.
- **Baseline:** literature.
- **Prior:** 85%.
- **Cost:** 4 GPU-hours.

#### H-EQ-9: Discovered codes fail CSS-preservation when DV-6 is off
- **Mechanism:** Without CSS prior, RL discovers non-CSS codes — equivalence check still applies but novelty class changes.
- **DV:** DV-6.
- **Metric:** CSS fraction.
- **Baseline:** CSS-only.
- **Prior:** 60% still CSS (strong prior even without mask).
- **Cost:** 24 GPU-hours.

#### H-EQ-10: Equivalence-check scaling is O(n^5) empirically
- **Mechanism:** LC-orbit enumeration is the bottleneck; expected poly scaling.
- **DV:** n/a.
- **Metric:** runtime vs n.
- **Baseline:** expected polynomial.
- **Prior:** 75%.
- **Cost:** 8 GPU-hours.

---

### Theme 6: Reward shaping and learning theory — H-RL/6-*, H-CUR-*, H-EXP-*, H-META-*

#### H-CUR-1: Linear n-curriculum outperforms fixed-n training at n=50 target within same budget
- **Mechanism:** Easy-to-hard curriculum reduces wasted early exploration.
- **DV:** DV-13.
- **Metric:** final reward at n=50.
- **Baseline:** fixed-n from start.
- **Prior:** 65%.
- **Cost:** 96 GPU-hours.

#### H-CUR-2: Noise-ramp curriculum outperforms distance-ramp at n=30
- **Mechanism:** Olle 2024 uses noise-level ramp; may be more informative than distance-ramp.
- **DV:** DV-14.
- **Metric:** final reward at fixed compute.
- **Baseline:** distance-ramp.
- **Prior:** 55%.
- **Cost:** 48 GPU-hours.

#### H-CUR-3: Adaptive curriculum (increment n when reward > threshold) beats linear at n=50
- **Mechanism:** Self-pacing adapts to task difficulty.
- **DV:** DV-13.
- **Metric:** compute-to-convergence.
- **Baseline:** linear.
- **Prior:** 50%.
- **Cost:** 72 GPU-hours.

#### H-CUR-4: Curriculum-induced policy transfers to fine-tune at new (n,k) with 50% less compute
- **Mechanism:** Meta-learning effect.
- **DV:** DV-13, DV-15.
- **Metric:** fine-tune compute.
- **Baseline:** from-scratch per-(n,k).
- **Prior:** 50%.
- **Cost:** 48 GPU-hours.

#### H-CUR-5: Curriculum across reward-weight settings beats fixed-weight training
- **Mechanism:** Alternating emphases prevents reward-surface local optima.
- **DV:** DV-1, DV-2, DV-3, DV-13.
- **Metric:** Pareto coverage.
- **Baseline:** fixed weights.
- **Prior:** 45%.
- **Cost:** 72 GPU-hours.

#### H-EXP-1: RND intrinsic bonus improves Pareto diversity by ≥30%
- **Mechanism:** Novelty bonus pushes exploration off main attractor.
- **DV:** DV-11.
- **Metric:** distinct-code-family count on Pareto.
- **Baseline:** entropy-only exploration.
- **Prior:** 40%.
- **Cost:** 48 GPU-hours.

#### H-EXP-2: Novelty-bonus in graph-canonical-form space accelerates discovery of non-BB codes
- **Mechanism:** Explicit novelty steers exploration.
- **DV:** DV-11.
- **Metric:** non-BB-family rate of discovered Pareto-optimal codes.
- **Baseline:** no novelty bonus.
- **Prior:** 35%.
- **Cost:** 48 GPU-hours.

#### H-EXP-3: Diversity-is-All-You-Need-style skill discovery produces distinct policies per code family
- **Mechanism:** Unsupervised skill learning may specialise.
- **DV:** DV-11.
- **Metric:** distinct policy clusters.
- **Baseline:** single policy.
- **Prior:** 30%.
- **Cost:** 72 GPU-hours.

#### H-EXP-4: Never-Give-Up episodic memory improves exploration at n=40
- **Mechanism:** Episodic memory avoids re-visiting visited states.
- **DV:** DV-11.
- **Metric:** training progress at n=40.
- **Baseline:** no memory.
- **Prior:** 30%.
- **Cost:** 48 GPU-hours.

#### H-EXP-5: Entropy bonus schedule (decaying) outperforms constant entropy bonus
- **Mechanism:** Early exploration, late exploitation.
- **DV:** DV-11 / DV-12.
- **Metric:** final reward.
- **Baseline:** constant entropy.
- **Prior:** 50%.
- **Cost:** 16 GPU-hours.

#### H-META-1: Meta-agent conditioning on (n,k) generalises zero-shot to unseen (n,k) within 2×{min, max} range
- **Mechanism:** Continuous embedding of (n,k) allows interpolation.
- **DV:** DV-15.
- **Metric:** zero-shot reward.
- **Baseline:** fine-tuned per-(n,k).
- **Prior:** 40%.
- **Cost:** 48 GPU-hours.

#### H-META-2: Meta-agent conditioning on reward-weights generalises across settings
- **Mechanism:** Continuous embedding of (α_d, α_g, α_n).
- **DV:** DV-15.
- **Metric:** transfer loss.
- **Baseline:** per-setting training.
- **Prior:** 40%.
- **Cost:** 48 GPU-hours.

#### H-META-3: Meta-agent conditioning on code-family (BB / HGP / Tanner) enables family-specific discovery
- **Mechanism:** Family prior accelerates convergence within family.
- **DV:** DV-15.
- **Metric:** family-specific Pareto coverage.
- **Baseline:** unconditioned.
- **Prior:** 45%.
- **Cost:** 72 GPU-hours.

#### H-META-4: Meta-agent pretrained on noise-family 1 transfers to noise-family 2
- **Mechanism:** Olle 2024 showed noise-transfer; we expect this to persist across our meta-agent extensions.
- **DV:** DV-15.
- **Metric:** cross-noise transfer.
- **Baseline:** Olle precedent.
- **Prior:** 70%.
- **Cost:** 24 GPU-hours.

#### H-META-5: Meta-agent with (n, k, p, α_g) as conditioning input reduces training budget by 3× vs per-setting
- **Mechanism:** Cumulative transfer benefit.
- **DV:** DV-15.
- **Metric:** total GPU-hours for full Pareto.
- **Baseline:** per-setting.
- **Prior:** 40%.
- **Cost:** evaluated across H-RL-*.

#### H-RL-6 through H-RL-20 (already above)

(These are listed under Theme 1 — PPO vs others, curriculum, etc.)

---

### Theme 7: Noise model and evaluation — H-NOISE-*

#### H-NOISE-1: Non-Pauli-approximation LER error bar at our discovered codes is ≤ 10%
- **Mechanism:** Residual non-atom-loss leakage is small in Bluvstein; treating as Pauli is approximately correct.
- **DV:** n/a.
- **Metric:** LER-change when switching to TN leakage simulation.
- **Baseline:** Pauli-only Stim.
- **Prior:** 70%.
- **Cost:** 16 GPU-hours (TN comparison at representative codes).

#### H-NOISE-2: Pareto front reshapes qualitatively at gate-fidelity 99.9% (vs 99.3%)
- **Mechanism:** 10× improvement may favour different codes.
- **DV:** DV-17 sensitivity.
- **Metric:** front overlap.
- **Baseline:** 99.3% committed.
- **Prior:** 50%.
- **Cost:** 16 GPU-hours.

#### H-NOISE-3: Correlated-error decoder (arXiv:2403.03272-style) improves LER of discovered transversal-gate-rich codes
- **Mechanism:** Transversal gates propagate correlations; decoder exploit.
- **DV:** DV-16.
- **Metric:** LER improvement.
- **Baseline:** uncorrelated decoder.
- **Prior:** 50%.
- **Cost:** 24 GPU-hours.

#### H-NOISE-4: Pareto front holds under IBM heavy-hex noise (not NA)
- **Mechanism:** Hardware-independence check.
- **DV:** DV-17.
- **Metric:** front overlap.
- **Baseline:** Bluvstein.
- **Prior:** 40%.
- **Cost:** 16 GPU-hours.

#### H-NOISE-5: Bluvstein 2024 raw parameters reproduce the published Stim noise model exactly
- **Mechanism:** Calibration re-verification; no subtle misalignment.
- **DV:** n/a.
- **Metric:** parameter match.
- **Baseline:** Bluvstein supplement.
- **Prior:** 90%.
- **Cost:** 4 GPU-hours.

#### H-NOISE-6: Atom-loss rate variation ±50% changes Pareto front negligibly
- **Mechanism:** Codes robust to atom loss are expected to dominate.
- **DV:** DV-17.
- **Metric:** front overlap under rate variation.
- **Baseline:** committed rate.
- **Prior:** 55%.
- **Cost:** 16 GPU-hours.

#### H-NOISE-7: BP+LSD (Roffe's preferred) outperforms BP+OSD on discovered codes at matched compute
- **Mechanism:** BP+LSD is recommended by Roffe for recent work.
- **DV:** DV-16.
- **Metric:** LER.
- **Baseline:** BP+OSD.
- **Prior:** 65%.
- **Cost:** 24 GPU-hours.

#### H-NOISE-8: Erasure decoding (post-atom-loss) improves LER ≥2× on discovered codes
- **Mechanism:** Erasure information is a significant decoder gain.
- **DV:** DV-16.
- **Metric:** LER improvement.
- **Baseline:** no-erasure-detection decoder.
- **Prior:** 75%.
- **Cost:** 16 GPU-hours.

#### H-NOISE-9: Mid-circuit measurement error dominates LER at our n=30 codes
- **Mechanism:** Measurement error ~10⁻² is higher than CZ error ~7×10⁻³.
- **DV:** n/a (analysis).
- **Metric:** LER sensitivity to measurement-error variation.
- **Baseline:** committed rate.
- **Prior:** 55%.
- **Cost:** 16 GPU-hours.

#### H-NOISE-10: Transport errors (NA-specific) dominate at large-n reconfiguration
- **Mechanism:** Transport cycles scale with circuit depth × reconfigurations.
- **DV:** n/a.
- **Metric:** LER sensitivity.
- **Baseline:** committed.
- **Prior:** 40%.
- **Cost:** 16 GPU-hours.

---

### Additional cross-cutting hypotheses — H-X-*

#### H-X-1: Scoop-risk monitor 4-weekly arxiv scan catches competing preprints with ≥80% sensitivity
- **Mechanism:** arxiv alerts + manual scan.
- **DV:** n/a.
- **Metric:** sensitivity at subsequent full scan.
- **Baseline:** manual inspection.
- **Prior:** 80%.
- **Cost:** 1 person-hour/month.

#### H-X-2: PER-1 profile completes within 2 GPU-days on representative stabilizer matrices
- **Mechanism:** Small-n profiling is cheap.
- **DV:** n/a.
- **Metric:** completion time.
- **Baseline:** PER-1 protocol.
- **Prior:** 90%.
- **Cost:** 2 GPU-days.

#### H-X-3: `qdx` fork compiles and runs Olle 2024 examples out-of-the-box
- **Mechanism:** Repo is dormant but may still work.
- **DV:** n/a.
- **Metric:** successful execution.
- **Baseline:** published example.
- **Prior:** 70%.
- **Cost:** 4 GPU-hours.

#### H-X-4: qLDPCOrg/qLDPC tool integrates with our training loop at acceptable overhead
- **Mechanism:** Tool is Python; interop with JAX training loop is standard.
- **DV:** n/a.
- **Metric:** per-call overhead.
- **Baseline:** standalone execution.
- **Prior:** 75%.
- **Cost:** 4 GPU-hours.

#### H-X-5: Final paper includes ablation across ≥3 reward-weight settings (minimum commit)
- **Mechanism:** Process commit from publishability_review.md.
- **DV:** DV-1, DV-2, DV-3.
- **Metric:** paper content.
- **Baseline:** commit.
- **Prior:** 100%.
- **Cost:** included in ablation.

#### H-X-6: Submit to npj Quantum Information within 5 months of Phase 0 completion
- **Mechanism:** Timeline commit from proposal_v2 §8.
- **DV:** n/a.
- **Metric:** arxiv submission date.
- **Baseline:** 2026-09-20.
- **Prior:** 50% on-time; 30% +1 month; 20% +2 months.
- **Cost:** n/a.

#### H-X-7: Heavy-hex-targeted code variant (targeting IBM BB roadmap) can be discovered as a bonus result
- **Mechanism:** Action-space mask to heavy-hex connectivity produces IBM-compatible codes.
- **DV:** DV-8.
- **Metric:** valid heavy-hex-compatible code discovered.
- **Baseline:** IBM reference.
- **Prior:** 35%.
- **Cost:** 24 GPU-hours.

#### H-X-8: Fork of qdx publishable as separate method note alongside main paper
- **Mechanism:** Contribution to open-source tooling.
- **DV:** n/a.
- **Metric:** public release.
- **Baseline:** qdx upstream.
- **Prior:** 70%.
- **Cost:** 20 person-hours.

#### H-X-9: Reward-ablation with α_g=0 (transversal-gate term off) reproduces arXiv:2502.14372-like results
- **Mechanism:** Null-ablation sanity check.
- **DV:** DV-2.
- **Metric:** codes match arXiv:2502.14372 regime.
- **Baseline:** arXiv:2502.14372.
- **Prior:** 70%.
- **Cost:** 24 GPU-hours.

#### H-X-10: Training reproducibility: same random seed produces same Pareto front ± 5% axis values
- **Mechanism:** Determinism check.
- **DV:** n/a.
- **Metric:** inter-run variance.
- **Baseline:** seed isolation.
- **Prior:** 80%.
- **Cost:** 48 GPU-hours.

#### H-X-11: Meta-learning produces a learnt reward-weight schedule that outperforms hand-tuned
- **Mechanism:** The meta-agent discovers good reward-weight schedule via sample-efficient adaptation.
- **DV:** DV-15.
- **Metric:** final reward.
- **Baseline:** hand-tuned weight ramps.
- **Prior:** 35%.
- **Cost:** 96 GPU-hours.

#### H-X-12: Discovered codes generalise to larger n via cover-code lifting
- **Mechanism:** If discovered code has structure, it lifts.
- **DV:** n/a.
- **Metric:** lifted-code validity.
- **Baseline:** discovered code at small n.
- **Prior:** 35%.
- **Cost:** 8 GPU-hours.

#### H-X-13: Discovered codes are compatible with BP+LSD at streaming speeds (< 10 ms/shot)
- **Mechanism:** Roffe's package performance.
- **DV:** n/a.
- **Metric:** wall-clock.
- **Baseline:** BP+LSD default.
- **Prior:** 60%.
- **Cost:** 4 GPU-hours.

#### H-X-14: Our Pareto front is robust under 10% perturbation in reference-set parameters (e.g., slightly different small-BB instances)
- **Mechanism:** Stability check.
- **DV:** n/a.
- **Metric:** front stability.
- **Baseline:** committed reference set.
- **Prior:** 75%.
- **Cost:** 16 GPU-hours.

#### H-X-15: Publishing the equivalence-check module as a standalone Python package adds citable artefact
- **Mechanism:** Field contribution.
- **DV:** n/a.
- **Metric:** package DOI / pip installability.
- **Baseline:** module in-repo.
- **Prior:** 80%.
- **Cost:** 40 person-hours.

#### H-X-16: Reward-weight sweep over 5 settings (publishability_review.md suggestion) adds 67% to training budget but improves robustness
- **Mechanism:** Wider ablation; reviewer-pre-empt value.
- **DV:** DV-1, DV-2, DV-3.
- **Metric:** robustness CI.
- **Baseline:** 3 settings.
- **Prior:** 65% worth the extra compute.
- **Cost:** 144 GPU-hours (vs 216 for 9 settings in H-RL-2; here 5 chosen settings).

#### H-X-17: Pareto-front evaluation under alternative distance metric (e.g., confusion distance) preserves ranking
- **Mechanism:** Distance-metric robustness.
- **DV:** n/a.
- **Metric:** ranking stability.
- **Baseline:** min-weight distance.
- **Prior:** 70%.
- **Cost:** 8 GPU-hours.

#### H-X-18: Cross-validation on held-out (n,k) cells (leave-one-out) preserves Pareto claim
- **Mechanism:** Statistical rigour.
- **DV:** DV-18.
- **Metric:** stability.
- **Baseline:** full-grid claim.
- **Prior:** 55%.
- **Cost:** 32 GPU-hours.

---

## Summary

Total hypotheses in this queue: **3 PER (top) + 100+ Phase 0 = 103+**. Total GPU-hour estimate if ALL are run: ~3200 GPU-hours, clearly unaffordable in Phase 1; Phase 1 will select ~15-20 hypotheses from this queue based on the scope-and-priority analysis in the Phase 0.5 protocol doc.

**Phase 1 priority set (proposed)**:
- H-RL-1 (baseline reproduce) → must pass first.
- H-RL-2 (reward-weight sweep) → main result.
- H-RL-3 (gadgets for scale) → scale-kill mitigation.
- H-TG-1 (rank reward vs raw count) → reward-correctness foundation.
- H-EQ-1 (equivalence at scale) → PER-2 operational.
- H-PARETO-2 (reference cell count) → PER-3 operational.
- H-PARETO-3 (dominance fraction) → main result.
- H-QLDPC-7 (at-least-one-cell dominance) → headline.
- H-NOISE-5 (Bluvstein parameter re-verify) → noise-model sanity.
- PER-1 (automorphism profile) → pre-gate.

Approx Phase 1 budget: ~800 GPU-hours, 4-5 months, aligns with proposal_v2 §8.
