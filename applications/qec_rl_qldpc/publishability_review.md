# Phase 0.25 Publishability Review: RL Code Discovery for Small qLDPC with Transversal-Gate-Aware Rewards

Reviewer: fresh agent, no prior conversation. Inputs: `proposal_v2.md`, `scope_checks/candidate_05_review.md`, shared `literature_review.md`, `knowledge_base.md`, Phase 0.25 of `program.md`. `papers.csv` and code not consulted (no code exists).

## 1. Novelty taxonomy

Category: **Synthesis**, now better argued than in v1 but still Synthesis.

Specific prior work being synthesised:
- Olle, Zen, Puviani & Marquardt 2024 (arXiv:2311.04750) — `qdx` + Knill–Laflamme RL, n≈20, d=5.
- arXiv:2502.14372 (2025) — RL low-weight code discovery, reward-shaping lineage.
- arXiv:2503.11638 (2025) — RL + gadget action space, scales past n=20.
- OpenReview 2025 — symmetry-prior RL, n>20.
- Zhu, Breuckmann et al. 2023 — automorphism-based transversal Clifford on BB codes (fixed codes, not RL).
- Nautrup et al. 2023 (arXiv:2305.06378) — earlier RL-for-codes baseline.

Is the reframe genuine or cosmetic? **Partly genuine.** The reframe shifts the headline from "scale RL past n=20" (crowded) to "Pareto-front study with transversal-gate-count reward and a pre-registered structural-novelty criterion". That is a real reframe — no single prior paper jointly optimises distance, rate, and transversal-gate availability, and the lit review theme 5 does not list a 2026 preprint that already fuses automorphism-gate rewards with RL at n≥30 (§214: `deepqec` not yet public; no such preprint in theme-5 inventory). So this is not a KILL on "already done".

But two cracks remain. (i) The gate-count bonus is still implemented "via Zhu–Breuckmann automorphism check" (§3), which is a polynomial-time check on a discovered code and hence nearly interchangeable with a reward add-on in the arXiv:2502.14372 or arXiv:2503.11638 pipelines. A rival lab running the same reward on `qdx` reaches the same destination; scoop risk remains high (scope check §Scoop-risk still applies). (ii) The claim "none targets the joint optimisation" (proposal §1) is narrower than the author implies — arXiv:2502.14372 already does joint (distance, stabilizer-weight) optimisation, which is the same trade-off class. So novelty is real but thin; this is Synthesis not Extension-dressed.

Verdict for §1: passes the "not a fig leaf" bar; fails the "clearly orthogonal to all five prior works" bar. Acceptable at npj QI only if the Pareto-dominance and structural-novelty criteria hold.

## 2. Falsifiability

Specific kill-outcome: **the Phase 0 feasibility gate returns n_max < 35 on one A100 in one week** (proposal §4 Kill #1), OR **every Pareto-optimal discovered code is automorphism-equivalent to a reference code** (Kill #2), OR **the discovered Pareto front is strictly dominated by the reference set at every point** (Kill #3).

Is the Pareto-dominance criterion genuinely pre-registered and tight? **Mostly yes, but with one soft edge.** The reference set is now named (small BB instances, Tanner, hypergraph-product, Error Correction Zoo entries, `[[16,6,4]]`), the three metrics are named (logical-error-rate under Bluvstein 2024 neutral-atom noise at matched k, transversal-Clifford gate count, physical-qubit count), and the noise model is fixed. Kill #3 uses "strictly dominating" but it is the *discovered front that must not be strictly dominated* — that is a clean bar.

**Soft edges that must be pinned before Phase 1:**
- "Matched (n,k)" is unambiguous for (k) but ambiguous for (n) — if the discovered code has (n',k) with n' slightly larger than a reference code's n, is it matched? The Pareto framing should nominally handle this (physical-qubit count is an axis), but the relation needs to be an explicit dominance rule: "code A dominates code B iff A is ≤ B on all three metrics and < on at least one, at the same k". Write this as one line in `proposal_v3` or Phase 0.5.
- "Transversal-Clifford gate count" is not a standard metric in the Zhu–Breuckmann paper; it is operationally "|{logical Clifford gates realisable by code automorphisms}|" — this needs a fixed enumeration procedure (e.g. automorphism-group order divided by stabilizer-subgroup action, or explicit generator count). Otherwise reviewers will say it was chosen post-hoc.
- "Graph-automorphism-equivalent" as the structural-novelty test (§2) — graph of the Tanner graph, or of the stabilizer generator matrix? Specify.

These are pin-downs, not fatal — §2 passes if they are written into `proposal_v3` or Phase 0.5's `data_sources.md` before any RL run. The headline is falsifiable.

## 3. Load-bearing parameters

| Parameter | Committed value | Consensus uncertainty / range | Headline scaling | Stable? |
|---|---|---|---|---|
| RL qubit scale n_max | Target 50; floor 35 (Kill #1) | Olle 2024 reached 20; arXiv:2503.11638 gadgets reportedly ~30–40 on single A100; extrapolation to 50 is not demonstrated in any published work I can see in the lit review | Headline requires n ≥ 35; below that project demotes | **Now stable on the downside** because of the explicit Kill #1 gate; upside still speculative |
| Reward weights (KL + transversal-gate bonus + qubit penalty) | "Pre-registered before training"; three ablation settings | No consensus — reward-weight sensitivity is high in RL-for-codes (scope check §3) | Pareto front composition depends strongly on weights; ablation across 3 settings partially hedges | Borderline. Three settings is the minimum; five would be safer |
| Transversal-gate identification cost | "automorphism check"; cost unspecified | Zhu–Breuckmann automorphism enumeration is polynomial per code but non-trivial; per-episode cost could dominate wall-clock | If per-episode reward > 10× the Clifford-sim cost, A100 budget breaks | **Unstable.** Proposal does not profile this. Must be profiled in Phase 0.5. |
| Action-space compression (symmetry priors + automorphism-aware masking) | "Ablation on/off" | Olle-style symmetry priors demonstrated at n=20; automorphism-aware masking is novel | Convergence at n ≥ 35 likely requires masking; if masking costs too much the feasibility gate fails | Coupled to parameter above; unstable |
| Final-eval noise model | Bluvstein 2024 supplement | Published | Fixed; affects only final eval not RL loop | Stable |
| Reference Pareto set | 5 code families at matched (n,k) | Well-defined for Error Correction Zoo and `[[16,6,4]]`; "small BB instances" needs enumerated list | Headline scales with how many reference codes are included — a larger reference front is harder to dominate | Needs enumeration but otherwise stable |
| Structural-novelty test | Graph-automorphism equivalence | Well-defined mathematically; implementation non-trivial | Gates Kill #2 | Specify graph type (see §2), otherwise stable |

**Flag: two of seven parameters (per-episode reward cost, action-space compression efficacy) are unstable and tightly coupled to each other and to the scale target.** These are the same two the scope check flagged as unstable — v2 has mitigated them only partly by pushing them into the feasibility gate. Since the gate genuinely demotes the project at n<35, this is acceptable; but the reviewer should understand that the feasibility gate is itself an experiment, not a commitment.

## 4. Venue fit

**Primary — npj Quantum Information.**
- *Fit:* publishes ML-for-QEC code-discovery papers (Olle 2024 npj QI is the precedent; lit review theme 5 §196); Pareto-front framing with a specific FT-architecture axis (transversal gates) is on-brand.
- *Typical objection:* "what is new beyond Olle + reward modification + automorphism check?" Reviewers at npj QI consistently demand an ablation isolating the new reward's effect AND a structural-novelty argument.
- *Pre-empt plan:* proposal §3 commits to the with/without-gate-count ablation; §2 commits to the structural-novelty criterion that explicitly excludes Zhu–Breuckmann rediscovery. This addresses the objection head-on. Acceptable.

**Secondary — NeurIPS ML-for-Science track.**
- *Fit:* RL methodology with a QEC reward; action-space compression + automorphism-aware masking is an ML-methodology contribution.
- *Typical objection:* NeurIPS reviewers want RL baselines (PPO vs SAC vs MuZero) and a non-trivial ML contribution beyond reward-shaping; they also complain when the application is simulation-only with no wall-clock or scaling-law analysis.
- *Pre-empt plan:* proposal does NOT commit to multi-RL-algorithm baselines; the n=20→50 scaling curve covers the scaling-law concern but not the algorithm-comparison concern. This is a partial pre-empt. If npj QI rejects, repurposing for NeurIPS will need a second ablation table. Acceptable as fallback but not first-choice.

**Not mentioned but should be considered: Quantum (journal).** The scope check named it; proposal v2 dropped it. Quantum is a natural fallback for code-discovery preprints and will demand exactly the BB/Tanner/hypergraph-product comparison that v2 now commits to. Leaving it off is mild and not blocking.

Verdict for §4: at least one plausible fit (npj QI), realistic fallback (NeurIPS ML-for-Science). Passes.

## 5. Top three killer objections

**(a) Scale feasibility is still an experiment, not a result. [MAJOR]**
- Specifically: n=50 on one A100 in one week with a Zhu–Breuckmann-style automorphism check per episode is not demonstrated in any published work in the lit review. arXiv:2503.11638 reaches the n>20 regime with gadgets but does not add a per-episode automorphism reward. The combination is unprofiled.
- Mitigation in v2: Kill #1 downgrades the project at n<35. This is a real mitigation — the project commits to not claiming something it cannot do — but it means the headline depends on an unverified compute claim.
- Required before Phase 1: a **day-0 profile** of per-episode Zhu–Breuckmann automorphism check wall-clock on representative stabilizer matrices at n=20, 30, 50 to confirm the reward cost is not the dominant term. This is cheap (no RL run needed) and must go in Phase 0.5's `data_sources.md`.

**(b) Structural-novelty test can still rubber-stamp Zhu–Breuckmann rediscoveries if "graph-automorphism-equivalent" is defined loosely. [MAJOR]**
- Specifically: the reference set is enumerated (§2), but if two codes have isomorphic Tanner graphs yet different stabilizer generators, does that count as automorphism-equivalent? The answer determines whether "rediscovered BB-like rotation" is excluded or accepted. Given that the scope check called objection (c) borderline fatal and this is the direct residue, ambiguity here would re-open the fatal channel.
- Mitigation in v2: §2 names the criterion but not the exact equivalence relation (stabilizer-group isomorphism? Tanner-graph isomorphism? GF(2) row-equivalence of parity checks with permutation + local Clifford?). These give different yes/no answers.
- Required before Phase 1: **pin the equivalence relation exactly in `proposal_v3` or equivalently in Phase 0.5's protocol doc.** Default recommendation: "Pauli-equivalent under qubit permutation + local Clifford" (standard stabilizer-code equivalence); anything weaker must be justified.

**(c) Pareto front at matched (n,k) can still be gamed by choosing favourable (n,k) points. [MINOR, borderline major]**
- Specifically: the proposal discovers codes and then reports the Pareto front. If the RL-discovered (n,k) pairs systematically avoid points where BB or hypergraph-product codes are strong, "Pareto-dominance at matched (n,k)" is tautological — the agent just picks easy (n,k).
- Mitigation in v2: none explicitly. The Pareto axes include physical-qubit count, which partially protects against this — a code at very different n won't match — but does not fully.
- Required before Phase 1: **pre-register the (n,k) grid** on which the Pareto comparison is carried out (e.g. n ∈ {20, 25, 30, 35, 40, 50}, k ∈ {2, 4, 6, 8, 12}), with the comparison restricted to (n,k) points where at least one reference code and at least one discovered code exist.

None of the three is fatal given the mitigations above. (a) and (b) are each "major with clear and cheap fixes"; (c) is "minor with a one-line fix". All three are tractable before Phase 1.

## VERDICT: PROCEED

All five items clear the bar. No fatal objection is unaddressed. npj QI is a plausible primary venue with a realistic pre-empt plan. The reframe from v1 to v2 is substantive, not cosmetic: Kill #1 is a real feasibility gate with a demotion path, the baseline is redefined as a multi-code Pareto reference set, and a structural-novelty criterion is introduced that explicitly excludes Zhu–Breuckmann rediscoveries. No 2026 preprint in the lit review already combines automorphism-gate rewards with RL at n≥30 (theme 5, §196–214), so the grounds for automatic KILL are absent.

**Pre-empt-reviewer items to append to `research_queue.md`:**

1. Day-0 profiling of Zhu–Breuckmann automorphism-check wall-clock at n ∈ {20, 30, 50} on representative stabilizer matrices (killer objection (a)). Cheap; no RL run needed. Must pass before the n=20→50 scaling curve starts.
2. Pin the exact code-equivalence relation used by the structural-novelty test (killer objection (b)). Default: Pauli-equivalence under qubit permutation + local Clifford. Write into `proposal_v3` or Phase 0.5 protocol doc with justification.
3. Pre-register the (n,k) grid for Pareto comparison with the rule that each grid point must contain at least one reference and one discovered code (killer objection (c)).

Additional reviewer remarks, non-blocking:
- Consider adding a fourth reward-weight ablation setting (proposal commits to three; scope-check concern about reward-weight sensitivity deserves a wider sweep).
- Reconsider Quantum (journal) as tertiary venue — it was in the scope check and dropped without explanation in v2.
- Scoop risk remains high; 4–5 months to arXiv is the correct cadence. Do not slip.
