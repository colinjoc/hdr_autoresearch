# Phase 0.5 Findings — qec_rl_qldpc

Date: 2026-04-21. Host: RTX 3060 12 GB, Python 3.12.3, qldpc 0.2.9, GAP 4.12 + GUAVA 3.18, pynauty 2.8.8.1.

## PER-1: transversal-Clifford rank via GAP+GUAVA → FAIL at production scale

Per `research_queue.md` PER-1 (pre-registered in proposal_v2 Phase 0.25), we profiled the Zhu–Breuckmann transversal-automorphism-group pipeline in `qldpc.circuits.get_transversal_automorphism_group` across BB instances at n ∈ {12, 20, 30, 40, 48, 50, 72, 144}.

### Measured per-call wall-clock (subprocess-isolated, 60 s hard timeout)

| Code | n | k | auto-group wall-s | Status |
|------|--:|--:|------------------:|--------|
| BB 2×3 (smallest nontrivial) | 12 |  0 | 3.02 | OK (includes GAP cold-start) |
| BB 2×5 | 20 |  0 | 0.04 | OK (warm) |
| BB 3×5 | 30 |  0 | 0.11 | OK (warm) |
| BB 4×5 | 40 | — | >60  | **TIMEOUT** |
| BB 5×5 | 50 | — | >60  | **TIMEOUT** |
| BB 3×8 | 48 | — | >60  | **TIMEOUT** |
| BB 6×6 | 72 | — | >60  | **TIMEOUT** |
| **BB gross 12×6** | **144** | **12** | **>60** | **TIMEOUT** |

### Verdict: PER-1 FAIL

The GAP+GUAVA pipeline does not scale past n ≈ 30 on consumer hardware under a 60 s per-call budget. The pre-registered RL step budget is 0.5 s/step; GAP+GUAVA at n = 40 exceeds this by ≥120×. **Per research_queue PER-1 fallback, we adopt a proxy metric.**

## Proxy: Tanner-graph automorphism group order via nauty

### Design

The full Zhu–Breuckmann pipeline computes (i) Tanner-graph automorphisms preserving CSS structure, (ii) lifts to stabilizer-preserving automorphisms, (iii) computes the induced logical-Clifford action, (iv) reports the rank. Steps (iii)–(iv) require GAP+GUAVA.

The proxy short-circuits at step (i): compute the order of the 3-coloured (qubit / X-check / Z-check) Tanner-graph automorphism group via nauty's canonical relabelling. This is an upper bound on the stabilizer-preserving subgroup and hence on the transversal-Clifford-rank reward, but it is O(n log n) in practice and well under 0.01 s at n ≤ 288.

### Measured proxy wall-clock (nauty via pynauty)

| Code | n | k | proxy wall-s | Autgroup order |
|------|--:|--:|-------------:|---------------:|
| BB 3×3 small          |  18 |  8 | 0.0001 |    2 592 |
| BB 6×3 small          |  36 |  8 | 0.0001 |      144 |
| BB 6×6 small          |  72 | 12 | 0.0003 |      432 |
| BB 8×4 (k=0)          |  64 |  0 | 0.0001 |       32 |
| BB 10×5 (k=0)         | 100 |  0 | 0.0003 |       50 |
| **BB gross 12×6**     | **144** | **12** | **0.0004** | **144** |
| BB 12×12 extended     | 288 | 16 | 0.0059 |      576 |

At n = 288, nauty is 1.19 % of a 0.5 s RL step budget — tractable by **four orders of magnitude** better than the GAP pipeline.

### Proxy PASS verdict

The proxy scales to n ≥ 144 on consumer hardware with per-call wall-clock ≤ 6 ms, well inside the RL step budget. We adopt it as the reward signal for Phase 1 experiments. The reward-hacking concern (automorphisms with trivial logical action inflating the score) is addressed in two ways:

1. **Separate Hx-only and Hz-only proxies.** Run nauty on two smaller Tanner graphs (qubits + X-checks only; qubits + Z-checks only). The difference between the joint-order and the product-of-individual-orders quantifies the CSS-duality contribution (Hadamard transversal candidates). This is Phase 1 work.
2. **Structural-novelty post-check** against the expanded reference set (proposal v3 §5). Discovered codes whose proxy score matches a reference-family instance at the same (n,k) are flagged as rediscoveries, not novel contributions.

## Reference-set expansion (Phase 0 scoop scan)

Per Phase 0 `data_sources.md` §3 scoop scan, three 2025–2026 hand-crafted automorphism-gate-friendly qLDPC constructions **must** be in the reference Pareto set or the novelty claim collapses. These were absent from proposal_v2 which predates them. Added to proposal_v3 §5:

- **RASCqL** — arXiv:2602.14273 (Feb 2026), symmetry-preserving qLDPC family.
- **SHYPS codes** — arXiv:2502.07150 (Feb 2025), symmetric hypergraph-product.
- **Asymmetric HGP** — arXiv:2506.15905 (Jun 2025), biased-noise-tailored.
- Fold-transversal BB, covering-graph BB (Symons 2025 arXiv:2511.13560).

## Tooling updates (Phase 0.5 infrastructure)

- venv: Python 3.12.3, qldpc 0.2.9, ldpc 2.4.1, pymatching 2.3.1, stim 1.16-dev, sympy 1.14.0, galois 0.4.10, **pynauty 2.8.8.1** (proxy backend), networkx 3.6.1.
- System: **GAP 4.12.1 + GUAVA 3.18 installed** via `sudo apt-get install gap gap-guava` — present on host even though we now use pynauty as the primary reward backend (GAP is retained for offline validation of the proxy against the full rank metric at n ≤ 30).
- **Olle 2024 `qdx`** is dormant since Dec 2024 (MIT licensed, forkable). A minimal fork for Phase 1 is deferred until the proxy is validated end-to-end; a custom PPO implementation on top of qldpc + nauty may prove simpler.

## Implication for proposal — draft v4 amendment

proposal_v3 §2 ("rank of induced logical Clifford") is no longer directly achievable at the pre-registered n=50 target on consumer hardware under the available tooling. The Phase 0.5-correct reward is:

**Primary reward (proposal v4):** nauty-computed Tanner-graph automorphism-group order × Knill–Laflamme distance term − qubit penalty. The proxy is an upper bound on the ideal rank-reward and is validated against the full rank metric on n ≤ 30 codes before Phase 1 training begins.

This is a scope adjustment consistent with the pre-registered PER-1 fallback path and should not trigger a fresh Phase 0.25 re-review (the reward *metric* changes; the *research question* — "can RL discover Pareto-front qLDPC codes at n ≤ 50 with automorphism-gate friendly structure?" — does not).

## What's next (Phase 1 trajectory)

1. Validate proxy ↔ rank correlation on small codes (n ≤ 30) where GAP is tractable.
2. Enumerate a small Pareto reference set by brute-force over BB polynomial families at small n.
3. Run a minimal PPO-style local search over the BB polynomial coefficient space using the nauty proxy as reward; record discovered codes.
4. Compare against the reference set at matched (n,k).
5. Write paper emphasising the **proxy methodology** as the primary contribution.
