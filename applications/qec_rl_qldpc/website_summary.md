---
title: "A fast proxy for transversal-gate rewards on quantum LDPC codes"
date: 2026-04-20
domain: "Quantum Computing"
blurb: "The natural reward for machine-learning-driven quantum code discovery — the size of a code's transversal-Clifford group — is hundreds of times too slow to use as a training signal. We built a graph-symmetry proxy that is formally bounded above, runs in under a millisecond at code sizes where the reference implementation times out, and ships with an explicit limitation that the correlation to the true reward is still unmeasured."
weight: 38
tags: ["quantum-error-correction", "qldpc", "reinforcement-learning", "infrastructure", "graph-automorphism"]
---

*A plain-language summary. The [full technical paper](https://github.com/colinjoc/hdr_autoresearch/blob/master/applications/qec_rl_qldpc/paper_submission.md) has the complete methods and results. See [About HDR](/hdr/) for how this work was produced.*

**Bottom line.** Reinforcement-learning agents that try to discover new quantum error-correction codes need a reward signal that tells them which codes are useful — not just which ones detect errors, but which ones allow fault-tolerant quantum gates to run transversally. The natural reward is the size of a code's transversal-Clifford automorphism group, computed via the computer-algebra system GAP. On consumer hardware, that computation times out within the training loop's per-step budget at code sizes larger than about 40 qubits. We introduce a graph-symmetry proxy that runs in under half a millisecond at the 144-qubit Bravyi gross-code scale, prove it is a formal upper bound on the true reward, and measure a 1,100× speedup at the one scale where both pipelines run to completion. We also publish — as the central limitation — that the correlation between the proxy and the true reward is still unmeasured, because our own attempt to measure it did not complete.

## The question

Quantum error-correction codes protect logical qubits by imposing an algebraic structure on many physical qubits. The Bravyi 2024 "gross code" [[144,12,12]] encodes 12 logical qubits in 144 physical data qubits — an order-of-magnitude improvement over the surface code. A natural research direction is to search for more codes in this style, using reinforcement learning (RL) over the space of parity-check polynomial families.

RL needs a fast, dense reward. Error-detection distance is easy to compute. But what really matters for fault-tolerant computing is whether the code supports transversal Clifford gates — logical gates implemented by parallel, non-interacting physical operations. Formally, this is the rank of the induced logical-Clifford group of the code's transversal-automorphism subgroup. The reference implementation is a GAP + GUAVA computer-algebra call that exhausts an exhaustive search over CSS-preserving qubit permutations.

On consumer hardware, this reference implementation hits a wall. At n = 30 it returns in 0.11 seconds. At n = 40 it times out at 60 seconds. At n = 144 (the gross code's size) it does not complete. The downstream rank computation — the part that turns the automorphism group into a number — does not complete within 600 seconds even at n = 30 where the preliminary group computation does complete. You cannot train an RL agent with a reward that takes longer than the training step itself.

## What we found

![Figure 1. Log-log wall-time versus code size n for the canonical GAP+GUAVA pipeline and the nauty proxy. A 60-second timeout plateau and a 0.5-second per-RL-step budget reference line make the scale gap visible; the proxy stays under one millisecond across the full range.](plots/fig1_gap_vs_nauty.png)

**The proxy is four to six orders of magnitude faster.** We build the 3-coloured Tanner graph of a CSS code — vertices are qubits, X-check rows, and Z-check rows; edges encode the parity-check matrices — and compute its automorphism group with nauty, the canonical graph-symmetry tool. On the gross code at n = 144 the proxy runs in 0.4 milliseconds. At the n = 30 cell where both pipelines complete, the measured speedup is ≥ 1,100×. At n ≥ 40, where the canonical pipeline times out, the speedup is bounded below by 150,000× but the canonical-side is a timeout rather than a completion, so we do not headline that number.

**The proxy is a formal upper bound, not a guess.** Section 3 of the paper proves that every element of the transversal-Clifford automorphism group induces a colour-preserving automorphism of the 3-coloured Tanner graph. A smaller proxy therefore directly constrains the true rank; a larger proxy is consistent with any true rank. This lets downstream RL users adopt the proxy with a clear formal guarantee: the proxy will never under-estimate the true rank, so it cannot prune codes that the true reward would have kept.

![Figure 2. Scatter of non-trivial codes in (n, k) from a brute-force Pareto smoke test over small BB polynomial families, with marker size and colour encoding the log-proxy-order. Eight Pareto-optimal points among 48 non-trivial codes, computed in 3.73 seconds total.](plots/fig2_pareto_scatter.png)

**The proxy operates end-to-end.** A 3.7-second brute-force Pareto smoke-test over BB polynomial families at (p, q) degree combinations ∈ {(3,3), (4,4), (5,5), (6,4), (6,6)} enumerates 48 non-trivial codes and identifies 8 Pareto-optimal points on (n, k, proxy). The n=18, k=12, proxy ≈ 10¹⁴ and n=72, k=8, proxy ≈ 1.8 × 10¹⁴ families both appear. This is the infrastructure smoke test; it is not a discovery claim.

**The central limitation is honest.** The proxy is a formal upper bound but there is no measurement of how tight that bound is. To measure the tightness we need proxy ↔ true-rank correlation at small n, and we need the true rank to compute for that we need the canonical downstream rank call to complete — which, as documented, does not complete within 600 seconds at the sizes where comparison is theoretically possible. We state this limitation prominently: any downstream user of this proxy should know that it is a bounded-above-only reward signal until the correlation study is run. Remedies we did not pursue include an offline multi-day GAP budget, a commercial MAGMA backend, or a Python/JAX reimplementation of the Zhu–Breuckmann lift. The cleanest of the three is the offline GAP run as a follow-up paper.

## Why that matters

Quantum-error-correction code discovery is a hot research area. Every new RL result published without a transversal-gate-aware reward is training on a proxy that over-values error-detection distance and under-values fault-tolerant logical-gate availability — which is the entire reason to build qLDPC codes in the first place. A tractable transversal-gate reward, even one known only to be an upper bound, is a strict improvement on the status quo, provided the limitation is published with the tool.

The 3-coloured Tanner-graph automorphism approach is also transferable beyond code discovery. Any setting where a combinatorial object has a natural symmetry group that lifts to a Clifford-type action — surface-code patch families, quantum Tanner constructions, concatenated codes — can use the same bound. What the proxy exchanges for its speedup is the guarantee that it reports the correct rank for the underlying code; what it preserves is the direction of the inequality.

## What it means in practice

**For RL practitioners working on qLDPC code discovery.** Adopt the proxy as a reward that rewards codes with rich Tanner-graph symmetry. Know that it is an upper bound; design your agent to not reward-hack on symmetry that does not lift to logical Cliffords (split H^X-only and H^Z-only proxies, compare joint vs individual autgroup ratios). Published downstream work using the proxy should also run a small validation study of correlation to the true rank.

**For anyone building a fast graph-symmetry reward for code search.** Use nauty with explicit colour classes for qubits, X-checks, and Z-checks. Account for CSS duality by running nauty twice (joint and CSS-dual) and taking the max. pynauty gives a clean Python interface.

**For downstream tooling authors.** The reference implementation bottleneck here is in GAP's exhaustive search, not in nauty. Any automorphism reward that requires the full GAP + GUAVA pipeline should not be used as an inner-loop reward; use the proxy for the loop and GAP only for offline validation.

## How we did it

We profiled the canonical GAP + GUAVA pipeline by wrapping each call in a 60-second subprocess timeout on a single consumer host (x86-64, 8-core class, Ubuntu 24.04, Python 3.12.3). BB codes were built with Bravyi gross-family polynomials and passed through the `qldpc` library's `get_transversal_automorphism_group` and `get_transversal_ops` interfaces. We then implemented the proxy directly: NetworkX to build the 3-coloured Tanner graph, pynauty to compute its automorphism group. The brute-force Pareto smoke-test sweeps polynomial coefficient combinations, filters by CSS orthogonality, and logs (n, k, proxy) tuples.

The reference implementation, profile tables, figure-generation artefacts, and the Pareto smoke-test are in the [project repository](https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/qec_rl_qldpc). The paper is prepared for Quantum or SciPost Physics Codebases submission.

## What's next

Three immediate follow-ups. First, the offline GAP run at 48-hour budgets on 5–10 small codes (n ≤ 16) to compute proxy ↔ true-rank correlation and either validate or invalidate the proxy as a reward signal. Second, an end-to-end RL experiment using the proxy as a reward on BB polynomial search, benchmarked against the gross code and the RASCqL, SHYPS, and asymmetric-HGP hand-crafted baselines. Third, extension of the 3-coloured Tanner construction to non-CSS codes via the symplectic product on stabilizer-tableau rows.
