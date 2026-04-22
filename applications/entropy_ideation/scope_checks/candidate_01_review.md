# Phase −0.5 Scope-Check — Candidate 1

**Candidate.** Activation-avalanche exponents in pretrained GPT-2.
**Question.** Does pretrained GPT-2 small / medium show power-law-distributed activation avalanches with α ≈ 3/2 on natural-text inputs, with full crackling-noise / shape-collapse / branching-ratio discipline?
**Reviewer.** Phase −0.5 sub-agent, 2026-04-21.

---

## 1. Novelty vs papers.csv and the 2025–2026 arXiv surface

`lit_ml.md §Gap` is explicit: *"no published paper has computed avalanche-size distributions, branching ratios, or power-law cluster exponents on the activation time-series of trained transformer language models (GPT-2 or larger)."* The closest entries in `papers.csv` are:

- **3045 Torres, Morales, di Santo, Muñoz 2023 "The critical brain hypothesis in deep learning"** — RNN-type networks, not transformers; VERIFY flag on author/venue. Does not target GPT-2 activations.
- **3046 Morales, di Santo, Muñoz 2023 "Quasi-universal scaling in mouse-brain neuronal activity …"** — edge-of-instability framework applied to cortex, not to trained language models.
- **3042 Testolin, Piccolini, Suweis 2020 "Deep learning systems as complex networks"** — weight-graph small-world / scale-free topology of DBNs. Weight graph, not activation avalanches, and not on transformers.
- **3053 Pilarski et al. 2023 "Pathways to emergence …"** — Jacobian-spectrum Lyapunov proxy on wide feedforward nets. Sensitivity, not avalanche exponents, not transformers.
- **3002 Schoenholz 2017, 3005 Pennington 2017** — at-init edge-of-chaos theory. Init only; silent on trained dynamics.
- **3036 Li 2023 "Lazy neuron phenomenon"** — activation-sparsity fractions in transformers; no cluster-size analysis.

Novel-vs-published precedents on arXiv 2025–2026 (WebSearch 2026-04-21):

- **Zhang et al. 2025, arXiv 2503.13530, "Cognitive Activation and Chaotic Dynamics in LLMs: A Quasi-Lyapunov Analysis"** — Quasi-Lyapunov exponent across layers; the word "avalanche" is used metaphorically for error-propagation. No P(s), α, β, γ, σ measurements. Does not collide.
- **"Dimensional Criticality at Grokking Across MLPs and Transformers" (arXiv 2604.16431)** — an *offline gradient-cascade* cascade-dimension probe D(t) on toy Transformers trained on modular addition and MLPs on XOR. Not pretrained GPT-2; not P(s) / crackling-noise. Different observable, different model class. Does not collide but is close in spirit — worth citing as adjacent.
- **Hong & Hong 2025, arXiv 2511.12768, "Evidence of Phase Transitions in Small Transformer-Based Language Models"** — vocabulary-level linguistic order parameters during training of a character-level GPT. No avalanche / branching / crackling-noise. Does not collide.
- **arXiv 2501.04286, Mapping the Edge of Chaos (decoder-only transformer trainability)** — training-loss fractal boundaries in hyperparameter space. Trainability landscape, not activation dynamics. Does not collide.
- **ICLR 2025 "Intelligence at the Edge of Chaos"** — cellular-automaton-pretrained sequence models; edge-of-chaos of the *input data*, not the transformer activations. Does not collide.

**Verdict on novelty.** The specific question — α, β, γ with CSN bootstrap, σ via MR estimator, shape collapse, and crackling-noise relation on pretrained GPT-2 residual-stream activations — is unpublished as of 2026-04. Closest pre-existing work is on RNNs (Torres et al. 2023, VERIFY), MLPs / DBNs (Testolin 2020), or on toy-task transformers with different observables (2604.16431). Novelty claim stands.

## 2. Falsifiability and feasibility on one RTX 3060 12 GB in ≤4 weeks

**Kill condition** (from the candidate): *"If no basis-threshold combination yields ≥ 2 decades of power-law scaling with CSN p > 0.05 rejecting alternatives, report negative."* This is concrete, pre-registered, and binary. Further, the full evidence bar in §5 of `knowledge_base.md` gives an eight-item checklist; the candidate explicitly commits to seven of them (see §4 below), and a negative result at the kill line is itself publishable.

**Compute.**
- GPT-2 small (125 M) inference at batch 1, seq 1024, fp16 fits in ≈0.5 GB; GPT-2 medium (355 M) ≈1.5 GB. Both comfortable on 12 GB with room for activation caching.
- Cache residual-stream + post-MLP activations at ≈20 layers × ≈1024 tokens × hidden-dim 1024 (medium) × 10 k Pile samples → ≈200 GB if fp32 dense, but with top-K sparsification (5–10 % typical sparsity per §3036 Li) the storage is <50 GB. Feasible on a consumer SSD.
- Avalanche extraction + `powerlaw` + `mrestimator` is CPU-bound; per-run analysis <1 hour.
- Budget: ~1 week pipeline build, ~1 week sweep (basis × threshold × input-distribution × model-size), ~1 week analysis + crackling-noise cross-check, ~1 week writeup. Fits inside 4 weeks. Author's own estimate (2 weeks) is optimistic; 3–4 weeks is realistic with the full eight-item bar.

**Feasibility risks.**
- SAE basis: requires public SAE weights for GPT-2 (e.g. `gpt2-small-res-jb` from the SAELens zoo, or OpenAI's GPT-2 Small SAEs). If the exact hidden size / layer doesn't have a public SAE, the SAE basis becomes a synthetic-training cost that should not be incurred on a 3060. Reframe (§3 below) should say "use GPT-2 with existing public SAEs only; if none available, drop SAE basis to PCA + random-projection and report that decision".
- Threshold plateau: if sparsity is very extreme (<2 % active per token) the per-sample event counts collapse and 2 decades of scaling becomes impossible. Predictable mitigation: aggregate across batch and report batch-level statistics.

**Falsifiability verdict.** PASS. Kill condition is operationally concrete and matches the knowledge-base evidence bar.

## 3. Venue fit

**Journals.** `Entropy` (MDPI, editor board includes Plenz / Beggs collaborators — natural fit for criticality-on-LLM), `Neural Computation`, `PRX Life` (life / info-physics but open to ML crossover), `Physical Review Research`. Published precedents: Torres 2023 (Entropy), Morales 2023 (PRL / eLife). Entropy has a "Complex Systems and Information Theory in Neural Networks" special-issue cadence; submission reachable for an independent researcher.

**Workshops.** NeurIPS *Unifying Representations* workshop, NeurIPS *MechInterp*, NeurIPS *ATTRIB*, ICLR *Blogposts* (as a replication-style writeup), ICML *High-dim Learning Dynamics* workshop. Acceptance rates 30–50 % and explicitly independent-researcher friendly; no conference fee required for poster-only.

**Author demographic.** The criticality-in-biological-networks + ML papers (Morales, di Santo, Muñoz; Plenz collaborators; Priesemann group) are senior research groups with postdocs / PhD students. BUT: adjacent mechanistic-interp work (Nanda, Conerly, AI-safety individuals on the Anthropic adjacency) has a strong independent-researcher / blog-post / workshop-paper track record. A one-RTX-3060 independent submission is plausible at MechInterp workshops and at Entropy; realistic for NeurIPS main only if the paper is unusually clean (full 8-item bar + negative-result discipline).

**Venue-fit verdict.** PASS. Strongest-fit venue is `Entropy` (journal) or a NeurIPS MechInterp / ATTRIB workshop (conference-adjacent). Both accept consumer-hardware submissions; neither requires institutional affiliation.

## 4. Required controls vs the 8-item knowledge-base minimum bar

Mapping candidate text onto `knowledge_base.md §5`:

| # | Evidence-bar item | Handled? | Where in candidate |
|---|---|---|---|
| 1 | `P(s)` fit via `powerlaw` + KS + p-value + LLR | Yes | "CSN p > 0.05 rejecting alternatives" (kill) |
| 2 | α ≈ 3/2 with 95 % CI | Yes | Question statement |
| 3 | β, γ independently measured; scaling relation γ=(β−1)/(α−1) | Yes | "crackling-noise cross-check" in Required controls |
| 4 | Shape-collapse figure | Yes | Observable list: "shape-collapse" |
| 5 | σ ≈ 1 via MR estimator on ≥ 2 axes | **Partial** | MR estimator implied via `mrestimator` but not called out as multi-axis (token, layer, batch). Add: compute σ on ≥ 2 axes. |
| 6 | Threshold plateau across [θ × 0.5, θ × 2] | Yes | "Sweep activation thresholds θ ∈ {0, 0.1, 0.5, 95th percentile}" |
| 7 | At-init control (random-init same-architecture) | Yes | "compare to randomly-initialised same-architecture model" |
| 8 | Neutral-null rejection (scaling relation OR task-correlation) | **Partial** | Crackling-noise relation partially covers this; explicit Martinello / Griffiths null is the subject of Candidate 12 and is not re-done here. Candidate 1 should at minimum state "neutral-null rejection via scaling relation; explicit Martinello null is deferred to Candidate 12". |

**Gaps to close before promotion.**
- Add: "σ on ≥ 2 axes (token-time and layer), reported with MR-estimator confidence interval."
- Add: "explicit pointer that the full Martinello-null-rejection test is Candidate 12 and is run in parallel; Candidate 1 discharges neutral-null via scaling-relation only."
- Recommend: state that SAE basis is used *if public SAE weights are available for GPT-2 at the chosen layer*; otherwise substitute PCA + random-projection as the second basis.

Six-of-eight hard, two-of-eight partial. Not a killer, but REFRAME-level cleanup.

## 5. Dependence structure

- **Can stand alone.** Core claim — "pretrained GPT-2 shows / does not show avalanche criticality in residual-stream activations" — is self-contained.
- **Feeds into:** Candidate 2 (skip-connection-sweep tunes criticality) uses the same pipeline; Candidate 6 (layer-depth gradient) extends the same pipeline. Both are natural follow-ups.
- **Co-requires for a strong positive claim:** Candidate 12 (Griffiths / neutral-null rejection) should run in parallel, not after. If Candidate 1 reports a positive α ≈ 3/2 *and* Candidate 12 cannot reject the neutral null, the positive claim from Candidate 1 downgrades to "apparent criticality". The pair 1 + 12 is the minimum viable first paper.
- **Does not depend on:** 3 (trained-dynamics sweep), 4 (grokking), 5 (SAE basis alone), 7 (Pythia scaling), 9 (dynamic-range), 10 (semantic Lyapunov). Candidate 1 is the "anchor" candidate and all others build on or parallel it.

**Dependence verdict.** Stand-alone, with Candidate 12 as the recommended parallel null-check.

## 6. Final verdict and one-line justification

The candidate's scientific content is novel, falsifiable, feasible on an RTX 3060 in 3–4 weeks, and has a plausible venue path for an independent researcher. The only adjustments required are (a) explicit multi-axis σ reporting (token-time and layer), (b) an explicit pointer to Candidate 12 as the parallel neutral-null-rejection test, and (c) a fallback-plan note on SAE weights (use public ones or substitute PCA / random-projection). None of these are scope-altering; they are review-level specification tightening.

**Verdict — REFRAME.** Core idea is novel and feasible, but the deliverable must commit to multi-axis MR branching-ratio reporting, an SAE-availability fallback, and an explicit parallel-run with Candidate 12 before the paper can claim genuine (rather than apparent) criticality — no change to scope, only to the required-controls list.
