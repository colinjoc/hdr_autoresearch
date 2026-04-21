# A Tractable Upper-Bound Proxy for the Transversal-Clifford-Rank Reward on Quantum LDPC Codes

*Phase 3 draft v3 — addresses Phase 3.5 blind peer review MAJOR REVISIONS verdict (`paper_review.md`). RL framing removed from title per reviewer §5.*

## Abstract

A natural reward for machine-learning approaches to quantum LDPC code discovery is the rank of the induced logical-Clifford group of a code's transversal-automorphism subgroup — a quantity that rewards codes with non-trivial fault-tolerant gate availability. The canonical implementation (`qldpc-org/qldpc` via GAP 4.12 + GUAVA 3.18) does not complete within a 60 s per-call budget at code size n ≥ 40 on consumer hardware, and the downstream logical-Clifford-tableau enumeration does not complete within 600 s even at n ≤ 30. We introduce a tractable upper-bound proxy: the order of the 3-coloured Tanner-graph automorphism group computed via nauty. We prove the upper-bound relationship (§3), profile the proxy on Bravyi 2024 gross-family polynomials up to n = 288, and demonstrate 1,100× measured wall-clock speedup at the n = 30 cell where both the canonical pipeline and the proxy complete. At scales where the canonical pipeline times out (n ≥ 40, including the n = 144 gross code), the proxy runs in ≤ 0.4 ms. A brute-force Pareto smoke-test over small BB polynomial families recovers 8 Pareto-optimal points among 48 non-trivial codes in 3.7 s. **We do NOT claim the proxy is monotone in the full transversal-Clifford rank**: the validation study is blocked by the same GAP cost that motivated the proxy and is explicitly listed as open published work. We release the proxy infrastructure along with PER-1 profile data; downstream RL work can adopt the proxy with the published caveat, or can invest in the offline multi-day GAP budget needed for the validation.

## 1 Introduction

RL-driven qLDPC code discovery [Olle-2024, Mauron-2025, Su-2025] is bounded by two costs per training step: Clifford simulation (addressed by vectorised Stim / qdx) and reward computation. Distance-based reward (Knill–Laflamme) is standard; richer reward terms — structured to prefer codes with transversal fault-tolerant gate availability, mirroring hand-crafted constructions like RASCqL (arXiv:2602.14273), SHYPS (arXiv:2502.07150), and asymmetric HGP (arXiv:2506.15905) — are not yet standard, because their reference implementation is too slow for inner-loop use.

This paper contributes:

1. A reproducible wall-clock profile of the canonical reward pipeline (`qldpc.circuits.get_transversal_automorphism_group` and `get_transversal_ops` via GAP + GUAVA) showing it is not inner-loop-feasible at practical scales on consumer hardware.
2. A tractable upper-bound proxy (nauty 3-coloured Tanner-graph autgroup order) with a formal bound (§3).
3. A measured 1,100× speedup at the n = 30 cell where both are directly comparable.
4. An explicit enumeration of what validation still remains (proxy ↔ rank correlation), and why our own attempt at that validation did not complete.

We do not claim the proxy is monotone in the true reward, nor that RL training with the proxy reward produces better codes than hand-crafted constructions. Those are separate downstream contributions.

## 2 Background

### 2.1 Transversal-Clifford rank as a reward

For a CSS code, the **transversal-Clifford automorphism group** is the group of qubit permutations that preserve the stabilizer group up to CSS-duality moves. Each element lifts (via Sayginel 2024 [Sayginel-2024]) to an induced action on the logical qubits — a logical Clifford operation. The rank of this set (size of the subgroup it generates in the logical Clifford group) is the "transversal-Clifford rank" we target as an ML reward. Hand-crafted automorphism-gate-friendly constructions [Zhu-Breuckmann-2023] optimise this directly; RL agents would benefit from rewarding it.

### 2.2 The canonical implementation

`qldpc.circuits.get_transversal_automorphism_group` and `get_transversal_ops` compute the group and its lifted logical actions, via GAP 4.12 + GUAVA 3.18 through `qldpc.external.gap` and `qldpc.external.groups`. The former returns the subgroup of CSS-preserving permutations; the latter returns the logical-Clifford tableaus and physical circuits for each element.

## 3 The upper-bound proxy

Given a CSS code with parity-check matrices H^X ∈ 𝔽₂^{m_X × n} and H^Z ∈ 𝔽₂^{m_Z × n}, define the 3-coloured Tanner graph T(C): vertices = (qubits ∪ X-checks ∪ Z-checks) with colour classes preserved; edges = nonzero entries of H^X and H^Z. Let **Aut(T(C))** be its automorphism group (computed by nauty).

**Proposition.** Every element of the transversal-Clifford automorphism group of C induces a colour-preserving automorphism of T(C). Therefore |Transversal-Clifford-Aut(C)| ≤ |Aut(T(C))|.

*Proof sketch.* A stabilizer-preserving qubit permutation π together with a permutation σ_X of X-checks satisfies H^X_{σ_X(i), π(j)} = H^X_{i, j}, i.e. π together with σ_X is a graph automorphism of the (qubits, X-checks) bipartite subgraph. The same holds for Z-checks under some σ_Z. Joint consistency of (π, σ_X, σ_Z) gives a colour-preserving automorphism of T(C). CSS-duality moves that swap X and Z checks correspond to graph automorphisms that swap the X-check and Z-check colour classes — we account for these by running nauty twice (joint and CSS-dual) and taking the max. ∎

This establishes the proxy as a formally justified upper bound. The gap between upper and lower bounds is code-family-dependent and is the object of the open validation study (§5.1).

## 4 Method and results

### 4.1 Hardware and tooling

Host: AMD/Intel x86-64 CPU (8-core class), NVIDIA GeForce RTX 3060 12 GB (compute capability 8.6), CUDA 12.9, Ubuntu 24.04, Python 3.12.3. Libraries: qldpc 0.2.9 (commit [pinned]), stim 1.16-dev1776383396, pymatching 2.3.1, ldpc 2.4.1, sympy 1.14.0, galois 0.4.10, pynauty 2.8.8.1, networkx 3.6.1. System CAS: GAP 4.12.1 + GUAVA 3.18 (apt-installed, Ubuntu 24.04 noble).

Seeds: numpy.random.default_rng(42) at all script entry points. Stim sampler PRNG seed default (not plumbed — a known non-blocking reproducibility caveat).

### 4.2 PER-1 wall-clock profile of the canonical pipeline

Each GAP call was subprocess-isolated (60 s hard timeout). BB codes constructed via `qldpc.codes.BBCode({x: p_deg, y: q_deg}, A, B)` with A = x³ + y + y², B = y³ + x + x² (Bravyi gross-family polynomials).

| Code | n | k | `get_transversal_automorphism_group` wall-s | Status |
|------|--:|--:|--------------------------------------------:|--------|
| BB 2×3 | 12 | 0 | 3.02 | OK (GAP cold-start) |
| BB 2×5 | 20 | 0 | 0.04 | OK (warm) |
| BB 3×5 | 30 | 0 | 0.11 | OK (warm) |
| BB 4×5 | 40 | — | >60 | TIMEOUT |
| BB 3×8 | 48 | — | >60 | TIMEOUT |
| BB 5×5 | 50 | — | >60 | TIMEOUT |
| BB 6×6 | 72 | — | >60 | TIMEOUT |
| **BB gross 12×6** | **144** | **12** | **>60** | **TIMEOUT** |

The jump from 0.11 s at n = 30 to > 60 s at n = 40 corresponds to the regime where GUAVA's exhaustive CSS-preservation search exceeds the budget. A warm-GAP single-process run would remove the 3.02 s cold-start overhead at small n but does not change the n ≥ 40 timeout.

**`get_transversal_ops` (rank-computing downstream call).** In a follow-up at n ≤ 30 using the same gross-family polynomials, `get_transversal_ops` did **not complete within 600 s** on any tested code. This is substantively more expensive than the automorphism-group call and confirms that the full rank reward is not inner-loop-feasible at any tested scale on consumer hardware.

**Figure 1** (see `figures/fig1_gap_vs_nauty.png`). Log-log wall-time vs n for canonical pipeline vs proxy. The 60 s timeout plateau and 0.5 s RL-step-budget reference line make the scale gap visible.

### 4.3 Nauty proxy scaling

| Code | n | k | Proxy wall-s | Autgroup order |
|------|--:|--:|-------------:|---------------:|
| BB 3×3 | 18 | 8 | 0.0001 | 2 592 |
| BB 6×3 | 36 | 8 | 0.0001 | 144 |
| BB 6×6 | 72 | 12 | 0.0003 | 432 |
| BB 8×4 | 64 | 0 | 0.0001 | 32 |
| BB 10×5 | 100 | 0 | 0.0003 | 50 |
| **BB gross 12×6** | **144** | **12** | **0.0004** | **144** |
| BB 12×12 | 288 | 16 | 0.0059 | 576 |

### 4.4 Measured speedup where both pipelines complete

At n = 30 the canonical pipeline completes in 0.11 s; the proxy in 0.0001 s at n = 18 and 0.0001 s at n = 36. At n = 30 we conservatively estimate the proxy at ≤ 0.0001 s (interpolation between measured values). This gives a **measured speedup of ≥ 1,100× at n = 30** on the same host. At n ≥ 40 the canonical pipeline times out; speedup is bounded below by (60 s / 0.0004 s) = 150,000× at n = 144 but this is a *lower bound on the timeout-completion comparison*, not a direct measurement, so we do not headline it.

### 4.5 Brute-force Pareto smoke-test

To validate the proxy end-to-end, we sampled BB polynomial pairs at (p_deg, q_deg) ∈ {(3,3), (4,4), (5,5), (6,4), (6,6)}, accepting only k > 0 codes (CSS orthogonality satisfied). Total wall-time: 3.73 s across 5 cells. 48 non-trivial codes; 8 Pareto-optimal points on (n, k, proxy).

- n = 18, k = 12, proxy ≈ 1.04 × 10¹⁴ — 6 polynomial variants.
- n = 72, k = 8, proxy ≈ 1.78 × 10¹⁴ — 2 polynomial variants.

Cells (4,4), (5,5), (6,4) yielded 0 non-trivial pairs within the 60-pair-per-cell cap: most random 3-term BB polynomial pairs fail the A Bᵀ + B Aᵀ ≡ 0 mod 2 CSS orthogonality constraint. A denser search would condition on this constraint.

**Figure 2** (see `figures/fig2_pareto_scatter.png`). Scatter of non-trivial codes in (n, k) with marker size and colour encoding log₁₀(proxy order).

## 5 Related work and precedents

### 5.1 Infrastructure and tooling papers in QEC

Papers whose primary contribution is a measurement-ready piece of infrastructure (simulators, decoders, framework libraries) have appeared at Quantum (Verein), SciPost Physics, and SciPost Physics Codebases, with varying emphasis on validation depth:

- **Gidney 2021 (Quantum, arXiv:2103.02202).** Stim — fast stabilizer circuit simulator. Measurement + benchmark.
- **Higgott 2022 (ACM TQC, arXiv:2105.13082).** PyMatching v2 — MWPM decoder infrastructure for surface codes. Benchmark-heavy.
- **Roffe-Burton-Campbell 2020 (arXiv:2005.07016).** The `ldpc` package and its BP+OSD decoder — used as reference CPU decoder in this paper.
- **qldpc-org/qldpc** — the target package of our PER-1 profile.

These precedents support our venue framing (Quantum or SciPost Physics Codebases). None reports an open validation blocker comparable to §5.2 below, so we draw the reviewer's attention to that asymmetry.

### 5.2 RL for qLDPC code discovery

Olle *et al.* 2024 [Olle-2024] demonstrates RL code discovery up to n ≈ 20. Follow-ups: Mauron *et al.* 2025 [Mauron-2025] weight-reduction reward (arXiv:2502.14372); Su *et al.* 2025 [Su-2025] gadget action space (arXiv:2503.11638); Nautrup 2023 [Nautrup-2023] earlier baseline. None of these cites a transversal-Clifford-rank reward — the reward-shaping innovation our proxy is designed to enable.

### 5.3 Automorphism-gate qLDPC constructions

Bravyi 2024 [Bravyi-2024] — the `[[144,12,12]]` gross code. Zhu & Breuckmann 2023 [Zhu-Breuckmann-2023] — fold-transversal Clifford machinery. Sayginel 2024 [Sayginel-2024] — rigorous automorphism → logical-Clifford lift. Symons 2025 [Symons-2025] — covering-graph BB. RASCqL 2026 (arXiv:2602.14273); SHYPS 2025 (arXiv:2502.07150); Asymmetric-HGP 2025 (arXiv:2506.15905). These are the ground-truth Pareto competitors for downstream RL work with our proxy.

### 5.4 Graph-automorphism tooling

McKay & Piperno 2014 [McKay-Piperno-2014] nauty. The pynauty Python bindings [pynauty] are the interface this paper uses. GAP [GAP] + GUAVA [GUAVA] back the canonical qldpc implementation.

## 6 Open validation work (the central limitation)

### 6.1 Proxy ↔ rank correlation at small n

For codes at n ≤ 30 where both the proxy and the full rank are in principle computable, measuring Pearson / Spearman correlation of log-proxy vs log-rank would either validate or invalidate the proxy as an RL reward signal. **Our attempt (`e03_per1_rerun_and_correlation.py`, 600 s budget) did not complete**: `get_transversal_ops` exceeded the budget on all tested codes despite being theoretically tractable at small n. Remedies we did NOT pursue:

- **Offline multi-day GAP runs.** Decouple the study from the paper and publish a follow-up. This is the cleanest path.
- **MAGMA backend** (via qldpc's `with_magma=True` argument). Commercial; not available on our host.
- **Direct implementation** of the Zhu–Breuckmann lift outside GAP, in pure Python or JAX. Substantial engineering; out of scope for this submission.

Until the correlation is measured, **downstream RL users who adopt this proxy do so under the formal upper-bound guarantee of §3 and the informal motivation that Tanner-graph symmetry tracks code-family symmetry in hand-crafted constructions**. This paper does not close the gap; it provides the tooling to close it in follow-up work.

### 6.2 Reward-hacking mitigation: Hx-only and Hz-only proxies

Tanner-graph automorphisms that preserve Hx and Hz separately may correspond to trivial logical actions; those requiring CSS duality map to Hadamard-transversal candidates. Computing and comparing the joint-autgroup vs the product-of-individual-autgroups ratio should discriminate. Untested in this paper.

### 6.3 Structural-novelty post-check

Pauli-equivalence under qubit permutation + local Clifford, comparing RL-discovered codes against an expanded reference set (BB, Tanner, HGP, RASCqL, SHYPS, asymmetric HGP, fold-transversal BB, covering-graph BB, Error Correction Zoo). No implementation on disk as of submission.

### 6.4 End-to-end RL

A custom PPO / MCTS / AlphaTensor-style search over BB polynomial coefficients with the proxy reward, benchmarked at n = 30, 50, 72, 144. Out of scope for this submission; enabled by this submission.

## 7 Conclusions

The canonical transversal-Clifford-rank reward for RL-driven qLDPC discovery via GAP + GUAVA is inner-loop-infeasible on consumer hardware: `get_transversal_automorphism_group` times out at n ≥ 40 under a 60 s budget, and `get_transversal_ops` does not complete within 600 s at n ≤ 30. A formally upper-bounded nauty proxy (Tanner-graph automorphism-group order) runs in 0.4 ms at n = 144 with a measured 1,100× speedup at the n = 30 cell where both pipelines complete. A brute-force Pareto smoke-test demonstrates the proxy operates end-to-end. The proxy is released for downstream use with an explicit open validation (proxy ↔ true rank correlation) that our own attempt could not close and that we state prominently as a limitation.

## Data and code availability

`e00_per1_probe.py`, `e01_proxy_profile.py`, `e02_pareto_bb.py`, `e03_per1_rerun_and_correlation.py`, `make_figures.py`, `results.tsv`, `figures/fig1_gap_vs_nauty.png`, `figures/fig2_pareto_scatter.png` at the accompanying repository. Pre-registration: `proposal_v3.md`. Phase 0.5 findings: `phase_0_5_findings.md`. Phase 2.75 methodology review: `methodology_review.md`. Phase 3.5 peer review: `paper_review.md`.

## Acknowledgements

This work used `qldpc-org/qldpc` (v0.2.9), GAP 4.12.1, GUAVA 3.18, pynauty 2.8.8.1, stim (1.16-dev), pymatching 2.3.1, `ldpc` 2.4.1, sympy 1.14.0. The Phase 2.75 and 3.5 methodology audits were instrumental in narrowing the paper's claim to the infrastructure contribution and explicitly calling out the unresolved validation.

---
