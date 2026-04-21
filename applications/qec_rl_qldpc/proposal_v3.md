# Proposal v3 — Pareto-Front RL Discovery of Small qLDPC Codes with Transversal-Gate-Aware Rewards

*Supersedes proposal_v2.md with Phase 0 amendments from the deep literature review + smoke test.*

## 1. Problem

RL-driven QEC code discovery has been demonstrated up to n≈20 at distance 5 (Olle et al. 2024, arXiv:2311.04750). Multiple 2025 preprints (arXiv:2502.14372 weight-reduction reward; arXiv:2503.11638 action-space gadgets; OpenReview 2025 scale-focused work) are pushing the scale frontier, and **three 2025–2026 hand-crafted** automorphism-gate-friendly qLDPC constructions have appeared — **RASCqL (arXiv:2602.14273), SHYPS (arXiv:2502.07150), asymmetric-HGP (arXiv:2506.15905)** — along with fold-transversal BB and covering-graph BB families. None of these lines targets the *joint* optimisation of distance, encoding rate, **and transversal-Clifford gate availability** via RL, and no published work combines automorphism-gate rewards with an RL pipeline at n≥30. 3-6 month scoop window per Phase 0 scoop scan.

## 2. Claim (falsifiable)

**Headline:** A **Pareto-front study** of small qLDPC codes at n ≤ N_max (N_max to be set by the Phase 0.5 feasibility gate; target 50) under a transversal-gate-rank-weighted RL search. The discovered Pareto front will strictly dominate the expanded reference set at matched (n,k) cells on a composite objective (logical-error-rate under Harvard/QuEra circuit noise, **rank of induced transversal logical Clifford group**, physical-qubit count).

**Key design correction from Phase 0 (H-TG-1):** the reward must count **RANK of induced logical Clifford group**, not raw automorphism count — otherwise RL reward-hacks into symmetric-but-useless codes (e.g., high permutation symmetry but only trivial logical action). This is a correctness-critical choice established in Phase 0 theme 3 deep read.

**Structural-novelty criterion (pre-registered per PER-2):** equivalence relation = **Pauli-equivalence under qubit permutation + local Clifford** (per qldpc's Sayginel 2024 [arXiv:2409.18175] treatment). At least one Pareto-optimal discovered code must NOT be equivalent to any code in the expanded reference set. Rediscovery of Zhu–Breuckmann, RASCqL, SHYPS, asymmetric-HGP, fold-transversal BB, or covering-graph BB instances is explicitly a non-contribution.

**Primary axis:** transversal-gate-rank reward shaping. Scale-past-n=20 is a secondary / ablation axis.

## 3. Method sketch

- **RL engine:** `qdx` (JAX, Olle 2024, MIT-licensed, dormant since Dec 2024 — forked and pinned). Vectorised Clifford simulation; PPO baseline with symmetry-aware action masking.
- **Reward back-end:** `qldpc-org/qldpc` (v0.2.9) for the `get_transversal_automorphism_group` + `get_transversal_ops` Zhu–Breuckmann pipeline (Sayginel 2024 arXiv:2409.18175 rigorous treatment). **Requires GAP 4 + GUAVA** as an external CAS dependency for the transversal-automorphism-group call.
- **Per-episode reward:** weighted sum of (Knill–Laflamme distance score, logical-Clifford rank bonus via Zhu–Breuckmann, qubit penalty).
- **Ablation grid:** with/without rank-reward term; with/without gadget action-space compression (arXiv:2503.11638 adopted as orthogonal lever per Phase 0 insight 3).
- **Final evaluation:** Stim under the Bluvstein 2024 neutral-atom noise supplement.

## 4. Kill-conditions (pre-registered)

1. **PER-1 reward-compute kill.** If `get_transversal_automorphism_group` + `get_transversal_ops` wall-clock on one A100 exceeds 50% of a typical 0.5 s RL step budget at any tested n ∈ {20, 30, 50}, swap the reward to a cheaper proxy (fold-transversal-count OR permutation-subgroup-size OR precomputed family tables). **Evaluated in Phase 0.5 E00/PER-1** — see `results.tsv`.
2. **Scaling kill.** The Phase 0.5 feasibility gate requires n ≥ 35 to be reachable on one A100 within 1 week of training. If n_max < 35, the project downgrades to a method note and does not proceed to Phase 1 as publication-target.
3. **Structural-novelty kill.** If every Pareto-optimal discovered code is Pauli-equivalent-under-permutation-plus-local-Clifford to a reference code, the paper reduces to "RL rediscovers known families" — demote or abandon.
4. **Dominance kill.** If the discovered Pareto front is dominated (not strictly dominating) by the reference set at every pre-registered (n,k) cell, KILL.

## 5. Expanded reference set (Phase 0 amendment)

Per Phase 0 scoop scan (see `data_sources.md`), the reference set must include 2025–2026 hand-crafted automorphism-gate-friendly qLDPC constructions that appeared during or after proposal_v2:

| Reference family | Citation | (n,k,d) coverage |
|---|---|---|
| Bivariate bicycle small instances | Bravyi 2024 [Nature] + Symons 2025 [arXiv:2511.13560 covering-graph] | small instances at various (n,k) |
| Tanner codes | Panteleev-Kalachev 2022 [arXiv:2111.03654] | asymptotic-good quantum Tanner |
| Hypergraph-product codes | Tillich-Zémor 2014 | classical-code × classical-code |
| Asymmetric HGP | arXiv:2506.15905 (2025) | tailored for biased-noise |
| **RASCqL (symmetry-preserving qLDPC)** | arXiv:2602.14273 (2026) | hand-crafted automorphism family |
| **SHYPS codes** | arXiv:2502.07150 (2025) | symmetric hypergraph-product |
| Fold-transversal BB | various 2025 | BB with fold-transversal logical gates |
| Error Correction Zoo entries | Albert et al. (reference catalogue) | small qLDPC instances across families |
| `[[16,6,4]]` teleportation code | Bluvstein 2024 supplement | single-cell baseline |

Pre-registered (n,k) grid for dominance claims (per PER-3): each grid cell must contain ≥1 reference code and ≥1 discovered code; cells without both populate as "unexplored" and are excluded from dominance claims.

## 6. Reframe responses absorbed

### v2 → v3 changes:

| Change | Source | Effect |
|---|---|---|
| Reward switches from "automorphism count" to "rank of logical Clifford" | Phase 0 insight H-TG-1 | Prevents reward-hacking on symmetric-but-logically-trivial codes |
| Expanded reference set with RASCqL/SHYPS/asym-HGP | Phase 0 scoop scan (`data_sources.md`) | Closes scoop window — these are the scoop-adjacent 2025–2026 constructions |
| PER-1 gate kill-condition made explicit | research_queue.md | GAP+GUAVA dependency cost measured Phase 0.5 |
| Equivalence relation pinned to Pauli-under-permutation+local-Clifford | research_queue PER-2 | Concrete structural-novelty criterion |
| Pre-registered (n,k) grid | research_queue PER-3 | Rules out post-hoc grid gerrymandering |
| `qdx` dormant-fork commitment | Phase 0 tooling audit | Maintenance cost budgeted; licensed fork pinned |

## 7. Load-bearing parameters

| Parameter | Committed value | Sensitivity plan |
|---|---|---|
| RL scale n | Target 50; committed to n ≥ 35 per feasibility gate | Scaling curve at n ∈ {20, 25, 30, 35, 40, 50} |
| Reward term | Rank of induced logical Clifford (NOT raw automorphism count) | Ablation: rank vs count vs fold-transversal-count proxy |
| Action-space compression | Symmetry priors (Olle-style) + optional gadgets (arXiv:2503.11638) | Ablation on/off |
| Final-eval noise model | Bluvstein 2024 NA supplement | Fixed |
| Reference baselines | Expanded 9-family set at pre-registered (n,k) grid | Fixed |
| Structural-novelty check | Pauli-equivalence under qubit permutation + local Clifford | Fixed |
| Reward back-end | `qldpc-org/qldpc` v0.2.9 + GAP 4.12 + GUAVA 3.18 | PER-1 profile gates the grid |

## 8. Target venues

**Primary: npj Quantum Information.** Anticipated objection (novelty beyond Olle + reward modification) pre-empted by Pareto-front framing + structural-novelty criterion.

**Secondary: NeurIPS ML-for-Science track.** Fit if RL methodology contribution stands alone.

## 9. Timing

Aim: arXiv within 4–5 months. Scoop risk: 3-6 months per Phase 0 scoop scan. **PER-3 monthly monitoring** armed.
