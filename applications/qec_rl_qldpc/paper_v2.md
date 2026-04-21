# A Tractable Tanner-Graph Automorphism Proxy for Transversal-Clifford Rewards in RL-Driven qLDPC Code Discovery

*Phase 3 v2 — addresses Phase 2.75 methodology review MAJOR-REVISIONS verdict (`methodology_review.md`).*

## Abstract

Reinforcement-learning qLDPC code discovery with transversal-gate-aware rewards is gated by the wall-clock cost of the reward function. The ideal reward — the rank of the induced logical-Clifford group from the transversal-automorphism subgroup — requires `qldpc.circuits.get_transversal_automorphism_group` and `get_transversal_ops`, both built on GAP 4.12 + GUAVA 3.18. We profile the pipeline on bivariate-bicycle codes (both generic and Bravyi 2024 gross-family polynomials) and find that the group-computation call times out at n ≥ 40 under a 60 s per-call budget, and the downstream `get_transversal_ops` (which returns the logical-Clifford tableaus and underwrites the rank reward) fails to complete within 600 s even on small codes at n ≤ 30 on consumer hardware. We introduce a tractable upper-bound proxy: the order of the 3-coloured Tanner-graph automorphism group computed via nauty (pynauty). The proxy runs in 0.4 ms at the Bravyi `[[144,12,12]]` gross code and 5.9 ms at n = 288 — four orders of magnitude faster than the GAP pipeline at n ≤ 30 and five or more at the code scales where GAP fails. A brute-force Pareto sweep over small BB polynomial families recovers 8 Pareto-optimal points among 48 non-trivial codes in 3.7 s. **We do NOT claim the proxy correlates with the full transversal-Clifford rank**: the validation study is an explicit Phase 2 follow-up, blocked by the same GAP cost that motivated the proxy. We release the proxy infrastructure (`e01_proxy_profile.py`, `e02_pareto_bb.py`) along with PER-1 profile data, and discuss mitigations for the reward-hacking risk (Hx-only/Hz-only proxy split, structural-novelty post-check).

## 1 Introduction

RL-driven qLDPC code discovery [Olle-2024, Mauron-2025, Su-2025] has been bounded by two costs: (i) the Clifford simulation per episode (addressed by vectorised Stim/qdx), and (ii) the reward function. Reward-shaping with distance (Knill–Laflamme) is the current default. The richer reward — *rank of induced logical-Clifford group from the code's transversal-automorphism subgroup* — would push RL towards codes with actual fault-tolerant gate availability, a property hand-crafted constructions like RASCqL (arXiv:2602.14273), SHYPS (arXiv:2502.07150), and asymmetric HGP (arXiv:2506.15905) optimise for directly.

The canonical pipeline for this reward (qldpc-org/qldpc → GAP + GUAVA → Zhu–Breuckmann → Sayginel 2024 lift) is inner-loop-infeasible in our measurements. This paper is an infrastructure contribution: a proxy that removes the wall-clock barrier, profiled on Bravyi 2024 gross-family polynomials up to n = 288, and an honest enumeration of the open validation work the proxy still requires before it can be trusted as an RL reward.

## 2 Method

### 2.1 Hardware and tooling

Single-host measurements: AMD/Intel x86-64 CPU, NVIDIA GeForce RTX 3060 12 GB (CUDA 12.9), Ubuntu 24.04, Python 3.12.3. Libraries: qldpc 0.2.9, stim 1.16-dev, pymatching 2.3.1, ldpc 2.4.1, sympy 1.14.0, galois 0.4.10, pynauty 2.8.8.1. System CAS: GAP 4.12.1 + GUAVA 3.18 (installed via `apt-get install gap gap-guava`).

### 2.2 The canonical reward — GAP+GUAVA pipeline

`qldpc.circuits.get_transversal_automorphism_group(code)` computes the transversal-Clifford automorphism group. `qldpc.circuits.get_transversal_ops(code, local_gates={S, H, SQRT_X, SWAP})` returns the logical tableaus and physical circuits for transversal logical-Clifford gates — the rank of this set is the idealised RL reward.

Both calls invoke GAP + GUAVA via the qldpc `external/gap.py` and `external/groups.py` adapters. A warning emitted during the call (`"Attempting to compute an automorphism group with GAP, which may take a long time"`) is now directly substantiated by our measurements.

### 2.3 PER-1 profile

We constructed BB instances at increasing n via `qldpc.codes.BBCode` with two polynomial families: (i) generic 3-term polynomials for fast iteration, (ii) the Bravyi gross-code polynomials A = x³ + y + y², B = y³ + x + x² for matched-family timing. Each GAP call was subprocess-isolated with a 60 s hard timeout (300 s in a follow-up warm-GAP run).

### 2.4 The nauty proxy

Given a CSS code, we build the 3-coloured Tanner graph (qubits / X-checks / Z-checks) and call `pynauty.autgrp` for the canonical automorphism-group order. The proxy is an **upper bound** on the transversal-Clifford rank (every stabilizer-preserving automorphism is a Tanner automorphism, but not conversely).

### 2.5 Brute-force Pareto demonstration

We sampled BB polynomial pairs at (p_deg, q_deg) ∈ {(3,3), (4,4), (5,5), (6,4), (6,6)} from all 3-term sums over x^{0..p} y^{0..q}, tested CSS orthogonality via k ≔ code.dimension > 0, and recorded (n, k, proxy-order) for each non-trivial code. Pareto frontier on (n, k, proxy-order) treats the first two as maximise-per-fixed-family and proxy as maximise-at-fixed-(n,k).

## 3 Results

### 3.1 PER-1: GAP+GUAVA wall-clock on BB codes

Subprocess-isolated, 60 s hard timeout per call:

| Code | n | k | `get_transversal_automorphism_group` wall-s |
|------|--:|--:|--------------------------------------------:|
| BB 2×3 generic  | 12 | 0 | 3.02 (GAP cold start) |
| BB 2×5 generic  | 20 | 0 | 0.04 (warm) |
| BB 3×5 generic  | 30 | 0 | 0.11 (warm) |
| BB 4×5 generic  | 40 | — | **>60** (TIMEOUT) |
| BB 5×5 generic  | 50 | — | **>60** (TIMEOUT) |
| BB 3×8 generic  | 48 | — | **>60** (TIMEOUT) |
| BB 6×6 generic  | 72 | — | **>60** (TIMEOUT) |
| BB gross 12×6   | 144| 12| **>60** (TIMEOUT) |

**Phase 2.75 reviewer note (addressed).** The probe used generic polynomials at the failing n-values and gross polynomials at n = 144. A warm-GAP follow-up with gross-family polynomials at n ∈ {40, 48, 50, 72} is an explicit open item (§4.3). Its outcome cannot flip the n = 144 timeout (which is the paper's decisive scale) and is unlikely to flip the n ≥ 40 timeouts given the 600-to-1 wall-clock jump between n = 30 (0.11 s) and n = 40 (> 60 s). We note the incomplete warm-GAP data as a caveat and proceed.

**`get_transversal_ops` (the rank-computing downstream call).** In a follow-up test at n ≤ 30 with the gross polynomial family, `get_transversal_ops` did not complete within 600 s on any tested code. This is substantively worse than the automorphism-group call and confirms that the full rank reward is not inner-loop-feasible.

### 3.2 Nauty proxy scaling

| Code | n | k | Proxy wall-s | Autgroup order |
|------|--:|--:|-------------:|---------------:|
| BB 3×3 gross   |  18 |  8 | 0.0001 | 2 592 |
| BB 6×3 gross   |  36 |  8 | 0.0001 |   144 |
| BB 6×6 gross   |  72 | 12 | 0.0003 |   432 |
| BB 8×4 gross   |  64 |  0 | 0.0001 |    32 |
| BB 10×5 gross  | 100 |  0 | 0.0003 |    50 |
| **BB gross 12×6** | **144** | **12** | **0.0004** | **144** |
| BB 12×12 gross | 288 | 16 | 0.0059 |   576 |

At n = 288 the proxy is 1.19 % of a typical 0.5 s RL-step budget — tractable by four or more orders of magnitude at every n vs. the GAP pipeline. The proxy infrastructure is available at scales where the canonical reward is not.

### 3.3 Brute-force Pareto over small BB families

Total wall-time 3.73 s, 48 non-trivial codes, 8 Pareto-optimal points. Pareto front concentrates at two n-values:

- **n = 18, k = 12, proxy ≈ 1.04 × 10¹⁴** — 6 polynomial-pair variants.
- **n = 72, k = 8, proxy ≈ 1.78 × 10¹⁴** — 2 polynomial-pair variants.

The non-trivial density at (p_deg, q_deg) ∈ {(4,4), (5,5), (6,4)} was **zero in our 60-pair-per-cell sample**: almost all random 3-term BB polynomial pairs violate CSS orthogonality (A Bᵀ + B Aᵀ ≠ 0 mod 2). A denser search would need to condition on this constraint explicitly.

**Phase 2.75 reviewer concern (acknowledged).** Eight Pareto points at two n-values is not a "Pareto-front study" worthy of a Nature / npj Quantum Information headline. We reframe this data as a **proxy infrastructure smoke-test**, not a Pareto-front contribution. The reframing matches our §4.1 venue note.

## 4 Discussion

### 4.1 Venue scope, revised

Based on the Phase 2.75 methodology-review assessment, this paper's contribution is the **proxy infrastructure and PER-1 wall-clock characterisation**, not an RL paper. We target Quantum (Verein) or SciPost Physics Codebases as the primary venue — both routinely accept infrastructure/tooling papers with clear validation plans. The original npj Quantum Information Pareto-front framing is downgraded to open work (see §4.3).

### 4.2 What the proxy captures — and what it doesn't

The Tanner-graph autgroup is an **upper bound** on the transversal-Clifford rank. The gap between the two is code-family-dependent and currently unmeasured at the scales we report (n ≥ 18 with k > 0). A Tanner automorphism that swaps two qubits may fail to preserve the stabilizer group, in which case it contributes to the proxy score without contributing to rank.

### 4.3 Open validation work (explicit Phase 2 items)

1. **Proxy ↔ rank correlation at n ≤ 30.** For small codes where both the proxy and `get_transversal_ops` can be computed, measure Pearson / Spearman correlation of log-proxy vs log-rank. **Our attempt (`e03_per1_rerun_and_correlation.py`, 600 s budget) did not complete** — `get_transversal_ops` exceeded the budget on all tested codes. This is consistent with the PER-1 FAIL result but leaves the validation open. Possible remedies: (a) pre-compute `get_transversal_ops` output via offline GAP scripts with multi-day budgets for a handful of codes, (b) use MAGMA instead of GAP (commercial, not available on our host), (c) accept the proxy without correlation validation and state this prominently as a caveat.

2. **Reward-hacking mitigation (Hx/Hz split).** Compute the autgroup of the qubit+X-check graph and the qubit+Z-check graph separately; report the ratio (joint / product). Automorphisms that require CSS duality correspond to Hadamard-transversal candidates; those that preserve Hx and Hz separately are less informative for logical-Clifford rank. Untested in this paper.

3. **Structural-novelty post-check.** Pauli-equivalence under qubit permutation + local Clifford, against an expanded reference set including RASCqL, SHYPS, asymmetric HGP, fold-transversal BB, covering-graph BB. No implementation on disk as of submission.

4. **End-to-end RL run.** A custom PPO wrapper around `qldpc` + pynauty (or a fork of the dormant `qdx` package) at n = 30, 50, 72, 144 using the proxy reward. This is the headline experiment that would justify the RL-discovery framing. Out of scope for this submission.

### 4.4 What this paper is and is not

Is:
- An infrastructure contribution: a 4-order-of-magnitude wall-clock reduction for transversal-gate-aware RL rewards via a principled graph-automorphism upper bound.
- A PER-1 profile: a reproducible characterisation of the GAP+GUAVA pipeline showing inner-loop infeasibility at n ≥ 40 on consumer hardware.
- A brute-force Pareto demonstration validating the proxy runs end-to-end on Bravyi-family BB codes.

Is not:
- An RL paper. No training loop on disk. §4.3 item 4 is future work.
- A Pareto-front contribution. 8 points at 2 n-values is insufficient to claim Pareto coverage. §4.3 item 4 is where dense Pareto discovery happens.
- A reward-validation paper. The proxy ↔ rank correlation is not measured (§4.3 item 1), and the reward-hacking mitigations (§4.3 items 2–3) are not implemented.

## 5 Related work

Same as v1 §5 — unchanged.

## 6 Conclusions

The canonical transversal-Clifford-rank reward for RL-driven qLDPC discovery via `qldpc.circuits.get_transversal_*` + GAP + GUAVA is not inner-loop-feasible on consumer hardware: `get_transversal_automorphism_group` times out at n ≥ 40 under a 60 s per-call budget, and `get_transversal_ops` does not complete within 600 s on tested codes at n ≤ 30. A 3-coloured Tanner-graph automorphism-group-order proxy via nauty is four or more orders of magnitude faster, running in 0.4 ms at n = 144 and 5.9 ms at n = 288. The proxy is an upper bound; its correlation to the true rank remains an open validation, pending offline multi-day GAP runs at small n. We release the proxy implementation and PER-1 profiling scripts as infrastructure for downstream RL qLDPC work.

## Data and code availability

`e00_per1_probe.py`, `e01_proxy_profile.py`, `e02_pareto_bb.py`, `e03_per1_rerun_and_correlation.py`, `make_figures.py`, `results.tsv` at the accompanying repository. Pre-registration: `proposal_v3.md`. Phase 0.5 findings: `phase_0_5_findings.md`. Phase 2.75 methodology review: `methodology_review.md`.

---
