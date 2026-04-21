# Data Sources & Phase 0 Smoke Test — qec_rl_qldpc

Smoke test executed 2026-04-20 as the mandatory gate BEFORE the deep literature review. All checks pass.

## 1. Tooling reachability

| Tool | URL | Status | License | Latest release | Active? |
|---|---|---|---|---|---|
| `qdx` (Olle RL QEC code-discovery, JAX) | https://github.com/jolle-ag/qdx | Reachable | MIT | 21 commits total, 2023-2024, published npj QI Dec 2024 | Reachable but visibly dormant since publication. This is a concern — a dormant upstream means we must be prepared to fork, not merely import. Scale demonstrated in paper: up to 25 physical qubits, distance 5 (paper roadmap aims at 100 qubits, d=10 — not delivered yet). |
| Stim (Gidney, stabilizer sim) | https://github.com/quantumlib/Stim | Reachable | Apache-2.0 | v1.15.0 (May 2025) | Very active; 720+ commits on main, 19 releases. Standard final-eval simulator. |
| `ldpc` (Roffe BP+OSD / BP+LSD) | https://github.com/quantumgizmos/ldpc | Reachable | MIT | Active (909 commits, 2025 activity) | Active. C++ rewrite with Python bindings. BP+LSD now recommended over BP+OSD for general use. NO CUDA/GPU support natively — we must use CUDA-Q QEC for GPU BP+OSD if needed. |
| PyMatching v2 (Higgott MWPM) | https://github.com/oscarhiggott/PyMatching | Reachable | Apache-2.0 | v2.3.1 (Sept 2025) | Very active. Correlated matching available since v2.3. CPU-only, ~10⁶ shots/core-second. |
| Bluvstein 2024 neutral-atom noise supplement | arXiv:2312.03982 / Nature doi.org/10.1038/s41586-023-06927-3 | Reachable | Nature | Published Dec 2023 / Nature (Jan 2024) | Nature paywall on HTML — but arXiv PDF + ancillaries are openly accessible. The supplement contains atom-loss, CZ-fidelity, transport-error numbers. Direct Nature HTML returned 303 redirect; arXiv variant is the canonical open path. |
| Error Correction Zoo | https://errorcorrectionzoo.org/c/qldpc | Reachable | CC-BY-SA | Continuously updated | Reference qLDPC entries exist; small-instance parity check matrices are NOT uniformly inline — we will need to pull specific matrices from cited references (code tables, QEC-Pages repo, QUITS simulator). |

**Tooling verdict: PASS.** Every load-bearing tool is reachable. The `qdx` dormancy risk means Phase 1 must include a "fork or rewrite" decision early — do not let a silent upstream be a single point of failure.

## 2. Scoop scan (2025-2026 preprints)

We searched for (a) RL + code discovery + qLDPC + transversal gates at n≥30, (b) RL + automorphism-gate rewards, (c) 2026 preprints fusing these elements.

### What exists and is close:

- **arXiv:2502.14372 (Feb 2025, "Discovering highly efficient low-weight QEC codes with RL")**. Extends Olle's approach to low-weight / qLDPC. Reward is stabilizer-weight-aware. Does NOT include transversal-gate count / automorphism-gate rewards. Scale regime is not the n≥30 target here; this is a weight-reduction reward pipeline. **Not a scoop** — complementary axis (weight) rather than transversal-gate availability. Their methodology and ours share the vectorised Clifford sim backbone; we will cite them as precedent and ablate against their reward.

- **arXiv:2503.11638 (March 2025, "Scaling Automated Discovery of Quantum Circuits via RL with Gadgets")**. Uses "gadget" composite-Clifford action compression to scale RL code discovery to "multiple dozens of qubits". Demonstrated [[n,1,d≤7]] and [[n,k,6]] for k≤7 — so n is somewhere in the 30-60 range at d=6-7 but the abstract doesn't commit to a specific maximum. Does NOT target transversal-gate-count-weighted reward. Closest published competitor on scale. **Not a scoop** — orthogonal reward axis. Their gadgets technique is potentially directly composable with our reward — flag for Phase 1 as a potential action-space enhancement.

- **OpenReview 2025 "Scaling Automated QEC Discovery with RL"**. Symmetry-prior-based scaling approach. OpenReview page returned 403 on direct fetch; we will attempt to pull the PDF in Phase 0.5 profile. Based on the abstract in the ideation papers.csv (entry 58): targets larger distances with symmetry priors. **Not a scoop** on transversal-gate rewards.

- **arXiv:2305.06378 (Nautrup et al. 2023)**. Earlier RL-for-codes baseline at small distance (≤4). Not a scoop.

- **arXiv:2511.12482 (Nov 2025, "Discovering autonomous QEC via deep RL")**. Targets continuous-variable autonomous QEC — a different problem space (bosonic/cat, not stabilizer qLDPC). Not a scoop.

- **arXiv:2601.19279 (2026, "RL for Enhanced Advanced QEC Architecture Decoding")**. This is RL for **decoding**, not for code **discovery**. Not a scoop.

### Non-RL automorphism/transversal-gate work on qLDPC (2025-2026):

- **arXiv:2602.14273 (March 2026, "RASCqL: Spacetime-Efficient and Hardware-Compatible Complex Quantum Logic Units in qLDPC Codes")**. Hand-designed approach that embeds automorphism-based complex Clifford operations in qLDPC codes; claims 2×-7× qubit-footprint reduction vs surface-code transversal architectures. **Is NOT RL**. It is an application-tailored construction. **Therefore not a scoop on the "RL + automorphism-gate rewards" thesis**. However — and this is important — RASCqL does exactly the kind of post-hoc curated analysis that our RL method is trying to automate. If our RL discovers codes that RASCqL already hand-curated, that is rediscovery, which the `proposal_v2` §2 structural-novelty criterion is designed to flag and EXCLUDE from the novelty claim. We must pre-register RASCqL's code set as part of the reference-set BEFORE any RL run. **Action: add RASCqL codes to the pre-registered reference set.**

- **arXiv:2506.15905 (June 2025, "Transversal Gates for Highly Asymmetric qLDPC Codes")**. Construction-based (not RL). Demonstrates transversal phase gates with k growing linearly in n, at the cost of O(1) phase-flip distance. Not a scoop. Adds to the reference set of "known transversal-gate-friendly constructions" for the structural-novelty check.

- **arXiv:2502.07150 (SHYPS codes, Photonic Inc., Feb 2025)**. Hand-designed symmetric subsystem hypergraph product codes supporting large transversal Clifford groups in O(m) syndrome extraction rounds. Not RL. Add to reference set.

- **arXiv:2510.08552 (Oct 2025, "Single-Shot Universality in qLDPC via Code-Switching")**. Code-switching between HGP codes for transversal CCZ. Not RL. Not a scoop.

- **arXiv:2510.07269 (Oct 2025, "Transversal Dimension Jump for Product qLDPC Codes")**. Construction-based. Not RL. Not a scoop.

- **qLDPCOrg/qLDPC GitHub tool** (github.com/qLDPCOrg/qLDPC). Non-RL tool that computes logical tableaus and physical circuits for SWAP-transversal logical Clifford gates via the code-automorphism method of arXiv:2409.18175. **This is an important auxiliary tool — we can use it to evaluate the automorphism-gate count of any discovered code, removing a Phase 1 implementation burden. Action: plan to use qLDPCOrg/qLDPC as the reward-evaluation back-end in PER-1's profiling.**

### Scoop verdict: CLEAR. No 2026 preprint fuses RL with automorphism-gate-count rewards at n≥30.

The three closest lines — RL-gadgets (2503.11638), RL-weight-reduction (2502.14372), hand-crafted automorphism-gate qLDPC (2602.14273 RASCqL, 2506.15905, SHYPS) — all leave the specific combination "RL with automorphism-gate-count-weighted reward on small qLDPC at n∈[20,50]" open. Our Pareto-front framing with a pre-registered structural-novelty criterion remains differentiated. Proceed.

### But — important scoop-risk flags:

1. **RASCqL (2602.14273) is less than 2 months old as of today (2026-04-20)**. Their explicit claim is that "code automorphisms, though rare and hard to lift to fault tolerance, can be exploited in targeted ways." This implies their community is actively hunting for automorphism-gate-friendly codes. An RL fusion from that group is plausible within our 4-5-month arXiv-time window. **Mitigation: keep scoop-risk review as a 4-weekly action during Phase 1. The `publishability_review.md` commitment "Do not slip" on the 4-5-month timeline is operationally binding.**
2. **qLDPCOrg/qLDPC tool**. The existence of this open-source automorphism-circuit-synthesis tool means the technical barrier-to-entry for an RL-based approach is very low for anyone who notices. A lab with a working RL-for-codes pipeline (IBM, Photonic, Quantinuum internal, any of the 5 known academic groups) could close the gap in weeks.

## 3. Reference-code availability

For the pre-registered Pareto-front reference set:

| Family | Availability | Notes |
|---|---|---|
| Small BB codes (`[[n,k,d]]` instances, n≤144) | Bravyi et al. 2024 Nature supplement; arXiv:2308.07915; Error Correction Zoo entry | Gross code and smaller BB instances have published parity check matrices in the ancillaries. Symons et al. 2025 (arXiv:2511.13560) adds `[[64,14,8]]` and `[[144,14,14]]` covering-graph variants. Automorphism group published separately in arXiv preprints (entries 146, 179 in ideation papers.csv). |
| Quantum Tanner codes | Panteleev-Kalachev arXiv:2111.03654 (asymptotic); Leverrier-Zémor arXiv:2202.13641 (simplified) | Asymptotic constructions; small instances require manual instantiation via the Cayley-complex recipe. Requires mild reconstruction effort — this should be checked early. |
| Hypergraph product codes | Tillich-Zémor 2014 IEEE TIT; SHYPS 2025 (2502.07150); panqec software | Standard; generators and small-n instances readily constructable from any pair of small classical LDPC codes. `ldpc` Python package has tooling. |
| Error Correction Zoo qLDPC entries | errorcorrectionzoo.org/c/qldpc | Links to code tables; small-instance parity-check matrices NOT inline on the zoo page but referenced via the QEC-Pages repo. |
| `[[16,6,4]]` code | Bluvstein 2024 supplement (Harvard/QuEra) | Published. |
| RASCqL codes (automorphism-embedded complex Clifford units) | arXiv:2602.14273 | ADD TO REFERENCE SET. Must be pre-registered before Phase 1. |
| Transversal-phase-gate HGP (2506.15905) | arXiv:2506.15905 | ADD TO REFERENCE SET (asymmetric distance constructions — may fall outside Pareto for our composite metric but should be evaluated). |
| SHYPS codes | arXiv:2502.07150 | ADD TO REFERENCE SET. Subsystem hypergraph product; highly symmetric. |
| Zhu-Breuckmann automorphism-gate-friendly BB codes | Original 2023 paper; arXiv:2409.18175 | Already planned for inclusion as "rediscovery-excluded" set per proposal_v2 §2. |

**Reference-code verdict: PASS with scope update.** The reference set enumerated in `proposal_v2.md` §2 must be updated in `proposal_v3` or a Phase 0.5 protocol doc to include the RASCqL, asymmetric-HGP (2506.15905), and SHYPS constructions that emerged in 2025-2026. The `publishability_review.md` objection (c) about gaming the (n,k) grid becomes slightly harder to pre-empt with these additions, but they are all hand-crafted — our structural-novelty rule will correctly flag any RL-discovered equivalent as rediscovery.

## 4. Day-0 profile plan (for PER-1 in research_queue.md)

PER-1 requires profiling the Zhu-Breuckmann automorphism check at n ∈ {20, 30, 50}. Design of the profile:

- Use qLDPCOrg/qLDPC as the reference automorphism-enumeration implementation — avoid rolling our own.
- Representative stabilizer matrices: 10 random small BB instances at each n, 10 random HGP instances at each n.
- Profile targets: median, p95 wall-clock per automorphism-enumeration call; memory footprint.
- Pass gate: per-episode reward cost ≤ 2× Olle 2024 `qdx` step time at n=20 (so that reward cost is not dominant; target ≤10% of total step with caching, but pass at ≤2× vanilla step time).
- Deliverable: `phase_0_5/per1_profile.md` with plots and pass/fail decision before any training run.

## 5. Final smoke-test verdict

**PASS.** Proceed to deep scoped Phase 0 literature review. No KILL condition triggered. The three scoop-risk mitigations (update reference set to include 2025-2026 hand-crafted automorphism-gate qLDPC; use qLDPCOrg/qLDPC as the reward back-end; 4-weekly scoop-risk re-check during Phase 1) are now first-class Phase 0.5 actions.

Date of smoke test: 2026-04-20.
Smoke-test duration: within 15-minute budget.
