# Proposal v2 — Pareto-Front RL Discovery of Small qLDPC Codes with Transversal-Gate-Aware Rewards

Responds to scope check in `../qec_ideation/scope_checks/candidate_05_review.md` (verdict: REFRAME).

## 1. Problem

RL-driven QEC code discovery has been demonstrated up to n≈20, distance 5 (Olle et al. 2024, arXiv:2311.04750). Three 2025 preprints (arXiv:2502.14372, arXiv:2503.11638, OpenReview 2025) are pushing the scale frontier, but none targets the *joint* optimisation of distance, encoding rate, and transversal-Clifford gate availability — three axes that must be traded for any fault-tolerant architecture.

## 2. Claim (falsifiable)

**Headline (reframed):** We will produce a **Pareto-front study** of small qLDPC codes at n ≤ N_max (N_max to be set by the Phase 0 feasibility gate; target 50) under a transversal-gate-count-weighted RL search. The discovered Pareto front will strictly dominate the reference set {small BB-family instances at matched (n,k); Tanner, hypergraph-product, and Error Correction Zoo codes at matched (n,k); `[[16,6,4]]`} on the composite (logical-error-rate under Harvard/QuEra circuit noise at matched k, transversal-Clifford gate count, physical-qubit count).

**Structural-novelty criterion (pre-registered):** At least one Pareto-optimal discovered code must fail to be a graph-automorphism-equivalent of any code in the reference list. Re-discovery of Zhu–Breuckmann automorphism-gate-friendly codes does NOT count as a contribution — it must be flagged and excluded from the novelty claim.

**Primary axis selected (per scope-check objection):** transversal-gate-count reward shaping. Scale-past-n=20 is a secondary / ablation axis, not the headline.

## 3. Method sketch

- `qdx` (JAX) for vectorised Clifford sim + gradient-free RL; MCTS or PPO with symmetry-aware action spaces.
- Per-episode reward: weighted sum of (Knill–Laflamme distance term, transversal-Clifford gate-count bonus via Zhu–Breuckmann automorphism check, qubit penalty).
- Ablation: reward with and without the gate-count term; both under the same compute budget; structural-novelty post-check against the reference set.
- Final evaluation on Stim under the Bluvstein 2024 neutral-atom noise supplement.

## 4. Kill-conditions (pre-registered)

1. **Scaling kill:** the Phase 0 feasibility gate requires n ≥ 35 to be reachable on one A100 within 1 week of training. If n_max < 35, the project downgrades to a method note and does not proceed to Phase 0.25 as publication-target.
2. **Structural-novelty kill:** if every Pareto-optimal discovered code is automorphism-equivalent to a reference code, the paper reduces to "RL rediscovers known families" — demote or abandon.
3. **Dominance kill:** if the discovered Pareto front is dominated (not strictly dominating) by the reference set at every point, KILL.

## 5. Reframe responses to scope-check objections

- **Objection (a) scale not robust:** Phase 0 feasibility gate (§4) runs the n=20→50 scaling curve BEFORE committing to the full paper. The scaling curve is itself publishable even if n=50 is out of reach.
- **Objection (b) baseline too weak:** baseline redefined as the Pareto front of {small BB instances, Tanner, hypergraph-product, Error Correction Zoo, `[[16,6,4]]`} at matched (n,k). Single-code baselines removed.
- **Objection (c) synthesis dressed as new [borderline fatal]:** addressed via (i) pre-registered structural-novelty criterion (§2), (ii) ablation isolating the gate-count reward's effect, (iii) commitment that "RL rediscovers Zhu–Breuckmann" is explicitly a non-contribution.

## 6. Load-bearing parameters

| Parameter | Committed value | Sensitivity plan |
|---|---|---|
| RL scale n | Target 50; committed to n ≥ 35 per feasibility gate | Scaling curve at n ∈ {20, 25, 30, 35, 40, 50} |
| Reward weights | Pre-registered before training | Fixed; ablation at three settings |
| Action-space compression | Symmetry priors (Olle-style) + automorphism-aware masking | Ablation on/off |
| Final-eval noise model | Bluvstein 2024 NA supplement | Fixed |
| Reference baselines | Pareto front of 5 code families at matched (n,k) | Fixed |
| Structural-novelty check | Graph automorphism equivalence against reference list | Fixed |

## 7. Target venue

**Primary: npj Quantum Information.** Fit — code-discovery paper lineage (Olle 2024). Anticipated objection (novelty beyond Olle + reward modification) pre-empted by Pareto-front framing and structural-novelty criterion.

**Secondary: NeurIPS ML-for-Science track.** Fit — if the RL methodology contribution (action-space compression for automorphism-aware masking) is strong enough to stand alone.

## 8. Timing

Aim: arXiv within 4–5 months. Scoop-risk mitigation — Pareto-front framing with structural-novelty criterion differentiates from the three 2025 preprints, all of which currently target single-point objectives (distance OR rate OR scale).
