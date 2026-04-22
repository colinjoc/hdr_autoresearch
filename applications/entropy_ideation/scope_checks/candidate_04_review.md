# Scope check — Candidate 4: Grokking phase transition and criticality observables

**Date:** 2026-04-21
**Reviewer:** Phase −0.5 scope-check agent
**Target:** Candidate 4 (`candidate_ideas.md §Candidate 4`). Test whether avalanche exponents / branching ratios shift at the grokking step, and whether they predict it before val-loss signal appears, on the canonical modular-arithmetic task.

**Verdict: REFRAME (leaning KILL of the headline claim).** The "criticality observables as early indicator of grokking" thesis is *already occupied* by Wang 2026 (arXiv:2604.16431 / 2604.04655, April 2026), which uses gradient-avalanche probes, reports a cascade-dimension crossing D=1 at the generalization transition, and explicitly claims grokked/ungrokked trajectories diverge 100–200 epochs before the behavioural transition on Transformers-on-mod-add and MLPs-on-XOR. A version of Candidate 4 can still be salvaged, but not the headline.

---

## 1. Novelty

### 1.1 The primary claim collapses

The headline claim — "criticality observables are early indicators of the grokking transition on modular arithmetic" — is already published, twice, in April 2026 by Ping Wang (IHEP, CAS):

- **arXiv:2604.16431** (Wang 2026a). Introduces TDU–OFC — an offline avalanche probe on gradient snapshots. Observable: time-resolved effective cascade dimension `D(t)`, which crosses the Gaussian-diffusion baseline `D = 1` *at the generalization transition* on Transformers trained on modular addition (p = 47, 59) and MLPs on XOR. Avalanche-size CCDFs exhibit heavy tails with cutoffs scaling as `s_max ∼ N^D`.
- **arXiv:2604.04655** (Wang 2026b). Companion: eight-scale finite-size-scaling, six seeds per scale, 51 gradient snapshots. `D_pre = 0.90 ± 0.02`, `D_post = 1.20 ± 0.02`, Gini-of-weights transient +25%, topology-invariant across five graph substrates. Framing: grokking is a self-organized-criticality event in gradient space.

These two papers scoop the method (avalanche analysis across grokking), the task (modular addition, canonical prime), the architectures (transformer + MLP), and the critical-exponent language. Wang 2026a explicitly claims early-warning separation of grokked vs ungrokked runs in `D(t)` "100–200 epochs before the behavioural transition" — exactly the pre-registered claim in the candidate.

### 1.2 Adjacent prior art also crowds the field

- **Clauw, Stramaglia & Marinazzo 2024** (arXiv:2408.08944, ICML 2024 MI workshop). Higher-order mutual-information / synergy / redundancy; claims to identify phases *preceding* grokking, enabling anticipation.
- **Prakash & Martin 2025** (arXiv:2506.04434). Heavy-tailed self-regularization (HTSR) exponent α on weight singular values as early-warning progress measure; also anticipates "anti-grokking" collapse. The physics-style-exponent-as-progress-measure slot is filled.
- **Cullen et al. 2026** (arXiv:2603.01192). Singular-learning-theory local-learning-coefficient framing of the same transition.
- **ICLR 2024 — "Grokking as a First-Order Phase Transition"** and **JMLR 2024 — "Grokking phase transitions in learning local rules"**. Phase-transition framing of grokking is no longer a contribution; it is the default.

### 1.3 Relation to Nanda 2023

Nanda's progress measures (restricted loss, excluded loss, Gini-of-Fourier-components, sum-of-squared-weights) are **circuit-specific**: defined in the Fourier basis that the mod-add embedding converges to. They are conceptually *distinct* from σ, α, or gradient-cascade dimension — those are **basis-agnostic collective observables**. So the concern that "Nanda measure = criticality observable" is not the operative failure mode; the classes are genuinely different. The actual failure mode is that Wang 2026 already carved out the criticality-observable slot (gradient-avalanche dimension) and Prakash–Martin 2025 carved out the heavy-tail-spectral slot. The conceptual novelty that Candidate 4 was premised on in late-2025 has evaporated in the ≤6 months since.

### 1.4 Residual novelty surface

Remaining crevices:

1. **Activation avalanches (not gradient avalanches).** Wang's probe is on gradient snapshots. Layer-resolved *activation* avalanches through training on mod-add are not in Wang 2026.
2. **Branching-ratio σ via MR estimator.** No search hit shows Wilting–Priesemann MR-estimator across a grokking transition. Cascade dimension `D(t)` ≠ branching ratio σ (FSS exponent vs one-step propagation).
3. **Scaling-relation / shape-collapse discipline.** Wang reports D and γ; no paper runs a full crackling-noise scaling-relation test (γ = (β−1)/(α−1)) with shape collapse, and none run neutral-null rejection (Candidate 12 discipline).
4. **Head-to-head across observables.** Wang's D, Prakash–Martin's HTSR α, Clauw's O-info all claim anticipation. No paper puts them on one axis across seeds and asks which has the lowest variance, longest lead time, or whether they are redundant.

Any reframe should live in 2–4.

## 2. Falsifiability

The original pre-registered kill ("if criticality observables lag val-loss or are uncorrelated with the phase transition, the claim dies") is well-posed. The operationalisation gap raised in the concerns is the deeper problem.

**"N steps before val-loss drops" is NOT well-defined as stated.** Required pinning:

- **Which val-loss milestone?** First derivative of val loss changes sign? Val-loss below threshold τ (τ = 10%, 1%?)? Val-accuracy crosses 50% / 99%? Use the midpoint of the logistic fit to val-loss trajectory, following Liu et al. 2022.
- **Which criticality milestone?** First step where |σ − 1| < ε? First inflection of σ(t)? Detection must be causal (no look-ahead smoothing). Use an online changepoint detector (Bayesian CUSUM, or the same logistic-midpoint on the observable trajectory) applied left-to-right.
- **Early-indicator metric.** Define `Δ = t_criticality − t_val` as a random variable over seeds. The claim is `E[Δ] < 0` with a specified magnitude. Report full distribution, not just the mean.

**Seed-variance budget.** Grokking-step variance on mod-add (p = 59 or 113, weight decay = 1, 40% train-fraction) is large: σ_t ≈ 20–40 % of the grokking step itself (Power 2022; Liu 2022; Nanda 2023 supp.). To distinguish `E[Δ] = -100` from `E[Δ] = 0` at Cohen's d = 0.5, α = 0.05, β = 0.2, the *minimum replicate count is n ≥ 30 seeds per condition*. Common 5-seed setups are *insufficient*. Budget: n = 32 × 2 conditions = 64 runs. Each run < 10 min on RTX 3060, so ≤ 1 GPU-day. Wang 2026a's 100–200-epoch claim needs re-verification with this replicate discipline; if anyone does that work, it should be this project, as partial-replication value.

## 3. Venue fit

- Original plan (ICML MechInterp / NeurIPS ATTRIB workshop) now needs positioning as replication-of-Wang or multi-observable head-to-head. Standalone "avalanches predict grokking" will be desk-rejected citing Wang 2026 and Prakash–Martin 2025.
- A reframe ("which of {cascade-D, HTSR α, O-info, activation-σ} is the earliest, most seed-stable predictor, and are they redundant?") is workshop-publishable.
- Alternative: *Entropy* special issue on criticality in learning systems; natural fit for a full crackling-noise treatment with neutral-null rejection.

## 4. Required controls

- **At-init control:** criticality observables on untrained same-architecture network.
- **Non-grokking control:** training regime with no weight decay (no grokking) — observable should not exhibit the pre-critical divergence.
- **Memorisation-only control:** small-p / high-train-fraction regime where memorisation is sufficient.
- **Replicate seeds:** n ≥ 32 per condition (see §2).
- **Neutral-null rejection** (Candidate 12 discipline): on the same activation traces, fit Martinello-style Griffiths-phase / neutral-branching null; reject only if scaling-relation residual is incompatible.
- **Observable-head-to-head:** Wang's `D(t)`, Prakash–Martin's HTSR α, Clauw's O-info, and activation-σ on one plot, common time axis, same seeds.
- **Operationalisation pre-registration:** exact definitions of `t_criticality` and `t_val`, locked before runs.

## 5. Dependence on other candidates

- **Candidate 12 (neutral-null rejection)** is a hard dependency. Without it the "critical" label is indefensible, and Wang 2026 does not run it either — so incorporating it is a genuine differentiator.
- Candidate 3 (SGD-deforms-criticality-landscape) shares the per-checkpoint observables pipeline; code is shared; a single infrastructure build services both.
- No dependency on Candidates 5, 7, 10, 11; independent of the transformer-LM pretrained-weights track.

## 6. Recommended reframe

**Kill:** "avalanche exponents as early indicator of grokking on mod-add" — scooped by Wang 2026.

**Salvage and reframe as:** *"Head-to-head evaluation of four physics-inspired early-indicator observables for grokking, with pre-registered operationalisation, n = 32 seeds, and neutral-null rejection."*

- Observables: (i) activation-space branching ratio σ via MR estimator; (ii) Wang-style gradient cascade dimension D(t); (iii) HTSR α on singular-value distribution; (iv) O-info synergy. All on same modular-addition runs.
- Primary outcome: earliest-detection lead time `E[Δ] = t_obs − t_val` distribution per observable; pairwise correlation across seeds (are the four observables redundant?).
- Secondary: neutral-null likelihood ratio per observable.
- Deliverable: workshop paper, conditioned on pre-registration of thresholds and seed counts. Cost ≤ 2 weeks: runs are cheap; bulk of effort is the four-observable analysis pipeline.
- Contingent kill: if all four observables are strongly correlated across seeds (|r| > 0.85), the reframe collapses to a single-observable scoop-verification and should be reported as a short replication note only.

Priority among candidates: **demote below Candidates 1, 2, 11, 12**; keep above Candidate 8.

---

**Sources consulted:**

- [Dimensional Criticality at Grokking Across MLPs and Transformers (Wang 2026a)](https://arxiv.org/abs/2604.16431)
- [Grokking as Dimensional Phase Transition in Neural Networks (Wang 2026b)](https://arxiv.org/html/2604.04655)
- [Information-Theoretic Progress Measures reveal Grokking is an Emergent Phase Transition (Clauw et al. 2024)](https://arxiv.org/abs/2408.08944)
- [Grokking and Generalization Collapse: Insights from HTSR theory (Prakash & Martin 2025)](https://arxiv.org/abs/2506.04434)
- [Grokking as a Phase Transition between Competing Basins (Cullen et al. 2026)](https://arxiv.org/abs/2603.01192)
- [Progress measures for grokking via mechanistic interpretability (Nanda et al. 2023)](https://arxiv.org/abs/2301.05217)
- [Grokking as a First Order Phase Transition (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/file/682f87a8c306098ec8be29019bd76aa4-Paper-Conference.pdf)
- [Grokking phase transitions in learning local rules (JMLR 2024)](https://jmlr.org/papers/volume25/22-1228/22-1228.pdf)
- Internal: `lit_ml.md §3` (training-dynamics phase transitions); `knowledge_base.md §2` (observable definitions); `papers.csv` rows 97–98 (Power 2022, Nanda 2023).
