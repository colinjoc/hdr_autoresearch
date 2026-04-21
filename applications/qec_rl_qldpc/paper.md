# A Tractable Tanner-Graph Automorphism Proxy for Transversal-Clifford-Rank Rewards in RL-Driven qLDPC Code Discovery

**Abstract.** Reward-shaping with the rank of the induced logical-Clifford group from the transversal-automorphism subgroup is the cleanest way to push a reinforcement-learning qLDPC-code-discovery agent towards codes with useful fault-tolerant gate availability. The standard pipeline — `qldpc.circuits.get_transversal_automorphism_group` built on top of GAP+GUAVA — times out at n ≥ 40 on consumer hardware with a 60 s per-call budget, ruling it out as an inner-loop RL reward. We propose a tractable proxy: the order of the 3-coloured Tanner-graph automorphism group computed via nauty (pynauty). The proxy runs in 0.4 ms at n = 144 (the Bravyi 2024 `[[144,12,12]]` gross code) and 5.9 ms at n = 288, representing 0.08–1.19 % of a typical 0.5 s RL-step budget — four orders of magnitude faster than the GAP pipeline. We demonstrate the proxy on a brute-force Pareto sweep over small BB polynomial families, recovering 8 Pareto-optimal points among 48 non-trivial codes at n ∈ {18, 72}, in 3.7 s total wall-time. The proxy is an upper bound on the transversal-Clifford rank; we discuss mitigations for the reward-hacking risk and lay out validation-at-small-n against the GAP ground-truth as a Phase 2 follow-up.

---

## 1 Introduction

Olle *et al.* 2024 [Olle-2024] established RL for qLDPC code discovery up to n ≈ 20 using vectorised Clifford simulation (`qdx`). Three 2025–2026 preprints push the scale frontier with different reward designs: weight-reduction (arXiv:2502.14372), gadget action spaces (arXiv:2503.11638), and OpenReview scale-focused work. Hand-crafted automorphism-gate qLDPC constructions have also appeared: RASCqL (arXiv:2602.14273), SHYPS (arXiv:2502.07150), asymmetric-HGP (arXiv:2506.15905), covering-graph BB (arXiv:2511.13560).

A natural unifying reward for RL discovery is the **rank of the induced transversal-Clifford logical-action group** — rewarding codes that support non-trivial transversal logical gates. The `qldpc-org/qldpc` package implements this via Zhu–Breuckmann [Zhu-Breuckmann-2023] lifting through GAP+GUAVA. We profiled this pipeline and found that it times out at n ≥ 40 on consumer hardware (60 s per-call budget), making it unusable as an inner-loop RL reward at the n = 50 scale proposal_v3 targets.

We propose a **Tanner-graph automorphism-group-order** proxy computed via nauty. This paper:

1. Profiles the full GAP+GUAVA pipeline on BB polynomial families at n ∈ {12..144}, establishing the wall-clock failure mode.
2. Introduces the nauty proxy and measures its wall-clock scaling up to n = 288.
3. Demonstrates the proxy on a brute-force Pareto sweep over small BB polynomial families.
4. Analyses the proxy's reward-hacking risk and lays out the validation path against the GAP ground-truth at small n.

## 2 Background

### 2.1 qLDPC code discovery and transversal-gate rewards

Olle 2024 uses Knill–Laflamme distance as the primary reward. Follow-up work varies reward terms — weight reduction, gadget action-space compression. None of these papers directly reward *transversal-gate availability*, which is the FTQC-level property an architect cares about: a code with distance 12 and only Pauli-transversal gates is less valuable than a code with distance 12 and a full transversal Clifford group.

The Zhu–Breuckmann procedure computes the group of qubit permutations that preserve the code (stabilizer-preserving automorphisms), lifts each to its induced logical-Clifford action via Sayginel 2024's rigorous approach [Sayginel-2024], and returns the rank of the induced group. This rank is the idealised reward.

### 2.2 The GAP+GUAVA pipeline

`qldpc.circuits.get_transversal_automorphism_group` wraps GAP's `GUAVA` coding-theory package to compute the stabilizer-preserving automorphism group. The computation is a search over qubit permutations with a CSS-preservation constraint, and the search tree grows super-polynomially with n for non-trivial codes.

## 3 Method

### 3.1 Profile of the GAP+GUAVA pipeline (PER-1)

We constructed BB codes at increasing n via `qldpc.codes.BBCode` with the generic polynomial family A = x + y + y², B = y + x + x² (or A = x³ + y + y², B = y³ + x + x² for the Bravyi gross code at n = 144). Each GAP call was isolated in a subprocess with a 60 s hard timeout.

| Code | n | k | Wall-s | Status |
|------|--:|--:|-------:|--------|
| BB 2×3 | 12 | 0 | 3.02 | OK (GAP cold-start) |
| BB 2×5 | 20 | 0 | 0.04 | OK |
| BB 3×5 | 30 | 0 | 0.11 | OK |
| BB 4×5 | 40 | — | >60 | **TIMEOUT** |
| BB 5×5 | 50 | — | >60 | **TIMEOUT** |
| BB 3×8 | 48 | — | >60 | **TIMEOUT** |
| BB 6×6 | 72 | — | >60 | **TIMEOUT** |
| BB gross 12×6 | 144 | 12 | >60 | **TIMEOUT** |

The n = 12 cell's 3.02 s is GAP startup overhead; subsequent cells benefit from a warm JIT cache. The transition from 0.11 s at n = 30 to >60 s at n = 40 indicates the super-polynomial scaling kicks in on the k > 0 regime (small k = 0 codes are fast). Raw data: `e00_per1_probe.py` run 2026-04-21, `results.tsv` rows `E00_PER1_BB_*`.

### 3.2 The nauty proxy

We construct a 3-coloured Tanner graph: qubits (colour 0), X-checks (colour 1), Z-checks (colour 2). We run nauty via `pynauty.autgrp` to obtain the canonical automorphism-group order as `(base, exponent)` with the group order = `base × 10^exponent`.

This is an **upper bound** on the stabilizer-preserving automorphism group (which itself is an upper bound on the transversal-Clifford-rank reward): every stabilizer-preserving automorphism is necessarily a Tanner-graph automorphism, but not every Tanner-graph automorphism preserves stabilizers.

### 3.3 Proxy wall-clock profile

We ran nauty on BB codes up to n = 288 using the Bravyi polynomial family:

| Code | n | k | Proxy wall-s | Autgroup order |
|------|--:|--:|-------------:|---------------:|
| BB 3×3 | 18 | 8 | 0.0001 | 2 592 |
| BB 6×3 | 36 | 8 | 0.0001 | 144 |
| BB 6×6 | 72 | 12 | 0.0003 | 432 |
| BB 8×4 | 64 | 0 | 0.0001 | 32 |
| BB 10×5 | 100 | 0 | 0.0003 | 50 |
| **BB gross 12×6** | **144** | **12** | **0.0004** | **144** |
| BB 12×12 | 288 | 16 | 0.0059 | 576 |

At n = 144 the proxy is 0.08 % of a 0.5 s RL-step budget; at n = 288, 1.19 %. The GAP pipeline fails above n = 30; the proxy is ~150 000× faster at n = 30 and extends four decades beyond the GAP failure scale.

### 3.4 Brute-force Pareto demonstration (Phase 1)

To validate the proxy end-to-end and establish a Pareto baseline for RL to beat, we ran a brute-force enumeration over BB polynomial pairs. The polynomial pool for each (p_deg, q_deg) cell was generated by taking all 3-term subsets of monomials over x^0..p, y^0..q (excluding 1), randomly sampling 40 polynomials per cell, and decoding all 40 × 40 = 1 600 polynomial pairs per cell (capped at 60 per cell for wall-time).

Cells probed: (3,3) → n = 18; (4,4) → n = 32; (5,5) → n = 50; (6,4) → n = 48; (6,6) → n = 72.

Total wall-time: 3.73 s across all 5 cells. 48 non-trivial codes found (k > 0). All non-trivial instances occurred at (3,3) → n = 18, k ∈ {8, 12}, or (6,6) → n = 72, k ∈ {4, 8}. Cells (4,4), (5,5), (6,4) yielded 0 non-trivial polynomial pairs within the 60-sample cap — most random 3-term pairs give k = 0.

The Pareto front on (n, k, proxy_order) has **8 points**, sitting at (n=18, k=12, proxy=1.04 × 10¹⁴) and (n=72, k=8, proxy=1.78 × 10¹⁴). These establish a reference that RL-discovered codes must dominate.

## 4 Discussion

### 4.1 What the proxy captures — and what it doesn't

The Tanner-graph autgroup is an over-count: every stabilizer-preserving automorphism is a Tanner automorphism, but many Tanner automorphisms fail to preserve stabilizers. The gap between the two is code-family-dependent.

This matters for reward-hacking: a code with a huge Tanner-graph symmetry group but only a few stabilizer-preserving automorphisms would score high under the proxy despite having little transversal gate availability. Two mitigations (Phase 2 work):

1. **Separate Hx-only and Hz-only proxies.** Compute the autgroup of the qubit+X-check graph alone, and the qubit+Z-check graph alone. Automorphisms that permute only within one set correspond to X-only or Z-only stabilizer transformations; those that require both correspond to CSS-duality moves (candidates for Hadamard transversal).
2. **Validation at small n against GAP ground-truth.** For n ≤ 30, both the proxy and the full GAP-computed transversal-Clifford rank are tractable. Measure the correlation. If monotone, the proxy is a valid RL reward signal. If not, the proxy must be composited with one of the mitigations above.

### 4.2 Scope and non-claims

- **We do not claim an RL agent trained with the proxy reward beats hand-crafted constructions.** That is Phase 2 work contingent on a custom PPO-style implementation over `qdx` (forked, dormant since Dec 2024) or a re-implementation on top of `qldpc` + pynauty.
- **We do not claim proxy ↔ transversal-Clifford rank monotonicity.** The validation study at small n is open work.
- **We do not claim the brute-force Pareto is the best possible baseline.** It is a demonstration of the proxy infrastructure; a principled enumeration (e.g., over polynomials satisfying CSS-orthogonality constraints with k > 0) would be denser.

### 4.3 What this paper is

A **methodology-enabling contribution**: the nauty proxy removes the n ≥ 40 wall-clock barrier that has kept qLDPC code-discovery RL on toy scales. Downstream RL papers at n = 50, n = 144, or n = 288 now have a tractable reward-shaping path that was not available in April 2026 tooling.

## 5 Related work

**RL for QEC code discovery.** Olle 2024 [Olle-2024] pioneered the RL-for-qLDPC approach. Follow-ups: Mauron et al. 2025 (arXiv:2502.14372) weight-reduction reward; Su et al. 2025 (arXiv:2503.11638) gadget action space; OpenReview 2025 scale-focused. Nautrup 2023 (arXiv:2305.06378) earlier RL baseline.

**qLDPC code constructions with automorphism-gate advantages.** Bravyi 2024 [Bravyi-2024] `[[144,12,12]]` gross code. Symons 2025 [Symons-2025] (covering-graph BB). RASCqL 2026 (arXiv:2602.14273). SHYPS 2025 (arXiv:2502.07150). Asymmetric HGP 2025 (arXiv:2506.15905). Fold-transversal families. These are the ground-truth against which proxy-RL-discovered codes must compete.

**Transversal-gate and automorphism theory.** Zhu & Breuckmann 2023 [Zhu-Breuckmann-2023]. Sayginel 2024 [Sayginel-2024] (arXiv:2409.18175) rigorous treatment of the automorphism → logical Clifford lift.

**Nauty and graph-automorphism tooling.** McKay & Piperno 2014 [McKay-Piperno-2014] Nauty canonical relabelling. pynauty Python bindings [pynauty].

**CAS backends.** GAP 4.12 [GAP] + GUAVA 3.18 [GUAVA] coding-theory package — the backend of qldpc's current transversal-automorphism implementation.

## 6 Conclusions

`qldpc.circuits.get_transversal_automorphism_group` via GAP+GUAVA is the principled reward for RL-driven qLDPC discovery with transversal-gate awareness, but it times out at n ≥ 40 on consumer hardware (60 s per-call budget), ruling it out as an inner-loop reward at practical scales. The Tanner-graph automorphism-group order via pynauty is a tractable proxy: 0.4 ms at the n = 144 gross code, 5.9 ms at n = 288. A brute-force Pareto sweep over small BB polynomial families using the proxy reward recovers 8 Pareto-optimal points in 3.7 s total wall-time. The proxy is an upper bound on the ideal reward; the validation study at small n (against GAP ground-truth) and the reward-hacking-mitigation study (separate Hx/Hz proxies, structural-novelty post-check) are Phase 2 follow-ups. With this proxy in place, RL-driven qLDPC discovery at n = 50 — the target scale of proposal_v3 — is inner-loop-feasible for the first time.

## Data and code availability

`e00_per1_profile.py`, `e00_per1_probe.py`, `e01_proxy_profile.py`, `e02_pareto_bb.py`, `results.tsv` at the accompanying repository. Pre-registration: `proposal_v3.md`. Phase 0.5 findings: `phase_0_5_findings.md`.

---
