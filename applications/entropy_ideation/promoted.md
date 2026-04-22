# Promotion Status — Consolidated Verdicts

Phase −0.5 scope-check outcomes. 12 fresh sub-agents, one per candidate. Detailed reviews in `scope_checks/candidate_NN_review.md`.

## Verdict table

| # | Title | Verdict | Natural home |
|---|-------|---------|--------------|
| 1 | Activation-avalanche exponents in pretrained GPT-2 | **REFRAME** → PROCEED | **Anchor paper** |
| 2 | Skip-connection topology sweep tunes criticality | **REFRAME** → PROCEED | Paper 2 (topology) |
| 3 | Training pushes toward / away from edge-of-chaos init | **REFRAME** → PROCEED | Paper 3 (dynamics), bundle with C4 |
| 4 | Grokking phase transition and criticality observables | **REFRAME leaning KILL** — scooped | Paper 3, reframed as head-to-head |
| 5 | SAE features vs raw neurons | **REFRAME** → PROCEED | Paper 4 (MI bridge), bundle with C10 |
| 6 | Layer-depth gradient of branching ratio | **REFRAME** — absorb | §4 of Paper 1 (Anchor) |
| 7 | Criticality observables across Pythia scale | **REFRAME** → PROCEED | Paper 5 (scale atlas); cap at Pythia-2.8B |
| 8 | Induction heads as circuit-specific criticality | **REFRAME** — observable under-specified | §X of Paper 1, or kill |
| 9 | Dynamic-range peak (Kinouchi-Copelli on LLMs) | **REFRAME (defer)** — scooped | Capstone of Paper 1; never standalone |
| 10 | Semantically-conditioned Lyapunov | **REFRAME (conditional)** — tautology risk | Paper 4, sequenced after C5 |
| 11 | CNN criticality on Fashion-MNIST | **REFRAME** — swap CNN→ViT; absorb | §5 of Paper 1 (Anchor), universality arm |
| 12 | Griffiths-phase vs true criticality rejection | **REFRAME** — absorb | §6 of Paper 1 (Anchor), mandatory null rejection |
| 13 | Branching-ratio regulariser | **REFRAME** — scooped by Falanti 2506.12810, Lewandowski 2406.06811 | Paper 6 (reframed, bundle with 17) |
| 14 | Criticality-aware init beyond Schoenholz | **REFRAME leaning KILL** — scooped by LSUV + Geometric Dynamics 2403.02579 + Fixup/ReZero/DeepNet/u-µP | Paper 1 tooling or cross-init benchmark |
| 15 | Criticality early-stopping signal | **REFRAME → PROCEED** as Paper 3 section | Paper 3 (dynamics), merged — drop Paper 8 |
| 16 | Criticality curriculum (anneal λ) | **KILL standalone** — biology inverted, saturated pattern, Achille-Soatto owns developmental framing | Fold as ~1wk ablation in Paper 6 (13) |
| 17 | Controllable grokking via σ-steering | **REFRAME leaning KILL** — 8 grokking interventions 2024-26, GrokAlign direct scoop | Workshop benchmark vs GrokAlign/Grokfast/Muon/⊥SGD/WD |
| 18 | Cross-universality-class: LLM vs cortex | **REFRAME** — dataset crisis; substitute CRCNS ssc-3 + Allen Neuropixels | Paper 7 (brain-homology) primary |
| 19 | Training-mode vs inference-mode criticality | **KILL standalone** — category error, absorb into Paper 3 | Paper 3 (if anything) |
| 20 | Architecture-class criticality (dense / SSM / MoE) | **REFRAME** — drop MoE; dense-vs-SSM only; Halloran SSM Lyapunov theorem | Paper 7 (brain-homology) arm |
| 21 | Pretrained vs instruction-tuned σ-shift | **REFRAME → MERGE** — Pythia-1.4B-instruct doesn't exist; Prakash-Martin finds HIGHER ρ | Paper 5 §post-training (Gemma-2-2B pair primary) |
| 22 | Spiking-transformer biological comparison | **REFRAME** — from-scratch infeasible; inference-only on public SpikeGPT weights | Paper 7 arm (inference only) |
| 23 | DFA of LLM activations | **REFRAME** → bundle with C24 | *Entropy* short / Paper 1 appendix |
| 24 | 1/f power spectrum | **REFRAME** → bundle with C23 | *Entropy* short / Paper 1 appendix; Le & Feng 2301.08530 covers LSTMs, transformers still open |
| 25 | Temporal RG on token sequences | **REFRAME lean KILL-standalone** → 5–7 day d_β appendix | Paper 1 or 7 appendix; partial scoop by 2601.19942 depth-RG |
| 26 | Prompt-type modulates σ at inference | **REFRAME → PROCEED standalone** | New paper — input-driven criticality; Magnasco arXiv:2405.15036 (RNN precedent, single-author preprint) |
| 27 | ICL emergence at σ=1 coincidence | **REFRAME → ABSORB** into Paper 3 | Paper 3 "Pythia realisation" section; complementary to Wang D(t) |
| 28 | Per-attention-head σ distribution | **REFRAME → ABSORB** into Paper 1 | Paper 1 head-resolved section, co-scoped with reframed C8 |
| 29 | Effective dimension tracks σ | **REFRAME → PROCEED** | New paper or Paper 5 arm; Fontenele method correction; stronger than C5 |
| 30 | Hallucination rate and σ | **REFRAME lean PROCEED** | Paper 8 workshop arm; saturated by Ji 2024 et al. but σ-observable novel |
| 31 | Adversarial robustness as sub-criticality | **REFRAME → PROCEED** | Paper 8 deployment-criticality arm; Singh 2023 ViT-B-ConvStem; drop LLM arm |
| 32 | Quantization damage via σ-shift | **REFRAME** → Paper 5 §N | Paper 5 int-precision-robustness section; distribution-reshaping confound is fatal as written |
| 33 | Distillation preservation of σ | **REFRAME → MERGE** into Paper 3 | Paper 3 post-training arm with C21; TinyLLaMA strike, Gemma teacher not public |
| 34 | Emergent capability = σ phase transition | **REFRAME → companion** to Paper 5 | Paper 5 companion; Nakaishi/Du/Schaeffer-2025 narrow but leave σ-adds-over-L_pretrain open |
| 35 | ViT vs LLM σ (cross-modality) | **REFRAME** — pivot axis | C11 absorbs cross-modal; novel scope = training-objective axis (sup vs DINO vs CLIP within ViT), vision-analogue of C21 |

**Round-3 synthesis findings.** Zero standalone promotions as written. The 13 collapse into: 4 bundle into Paper 1 (C25 appendix, C28 head-section); 3 into Paper 3 (C27 Pythia section, C33 post-training arm, with earlier C15 diagnostic section); 2 into Paper 5 (C32 §int-precision, C34 companion); 1 new Entropy-short bundle (C23+C24); 1 new input-driven-criticality paper (C26); 1 new Paper 8 deployment-criticality (C30+C31 bundled); C29 is the only clean standalone new paper; C35 pivots to ViT-internal training-objective axis. **~30 more arXiv IDs** surfaced to add to papers.csv beyond round-2's 38.

## Final programme (post-synthesis)

- **Paper 1 — Anchor** (C1 + C6 §4 + C11 §5 + C12 §6 + C8 + C25 d_β appendix + C28 head-section). Unchanged core; richer observable battery.
- **Paper 2 — Topology** (C2). Unchanged.
- **Paper 3 — Training dynamics** (C3 + C4 + C15 § + C27 Pythia-ICL § + C33 distillation arm + C21 base-vs-instruct arm).
- **Paper 4 — MI bridge** (C5 + C10). Unchanged.
- **Paper 5 — Scale atlas** (C7 + C21 post-training + C32 §int-precision + C34 companion + optional C9 capstone).
- **Paper 6 — Criticality-regularised training, workshop** (C13 + C17 + C16 ablation). Unchanged.
- **Paper 7 — Brain-LLM homology** (C18 + C20 + C22). Unchanged.
- **Paper 8 — Deployment criticality** (C30 hallucination + C31 adversarial robustness). **NEW — synthesis round**.
- **Paper 9 — Entropy-short: orthogonal observables** (C23 DFA + C24 1/f PSD). **NEW — synthesis round**.
- **Paper 10 — Input-driven criticality** (C26). **NEW — synthesis round standalone**.
- **Paper 11 — Effective-dimension criticality** (C29). **NEW — synthesis round standalone** — probably the strongest novel direction.
- **Paper 12 — Training-objective axis on ViT** (C35 reframed). Vision-analogue of Paper 3 post-training.

**Recommendation.** Promote Paper 1 + Paper 7 + Paper 11 (C29 Effective Dimension) as the first three project directories. All three are inference-only on pretrained weights, so they run in parallel on a single RTX 3060 without GPU contention. C29 is particularly strong because it directly tests a 2024 Sci. Adv. result in new substrate; it's the highest novelty-per-cost item in the entire 35-candidate portfolio.

**Round-1 zero candidates pass as-written.** All twelve need reframes — mostly in controls, null specification, or bundling — but the core research programme is intact.

**Round-2 findings are tougher.** 2 kills (16, 19), 2 lean-kills (14, 17), 6 reframes. Training-interventions space is crowded: Falanti, Lewandowski, GrokAlign, Grokfast, NeuralGrok, Muon, ⊥SGD, GrokTransfer, Geometric Inductive Bias, Low-Dim Curvature. Brain-comparison space also has adjacent work (Ghavasieh 2512.00168, Arola-Fernández 2508.06477) but less saturated.

## Revised five-paper programme (after extension round)

- **Paper 1 — Anchor** (C1 + C6 §4 + C11 §5 + C12 §6 + optional C8 §X). Unchanged.
- **Paper 2 — Topology tuning** (C2 reframed). Unchanged.
- **Paper 3 — Training dynamics** (C3 + reframed C4 + C15 § + C19 §only-if-salvage). Gains C15 diagnostic-comparison section.
- **Paper 4 — MI bridge** (C5 → C10). Unchanged.
- **Paper 5 — Scale atlas** (C7 + C21 §post-training-axis + C9 capstone). Gains C21 Gemma-2-2B pair arm.
- **Paper 6 — Criticality-regulated training** (C13 reframed as activation-σ + C17 reframed as head-to-head benchmark + C16 as ~1wk ablation). **Downgraded from "method paper" to "workshop benchmark"** — the field is too crowded for a main-track novelty claim.
- **Paper 7 — Brain-LLM homology** (C18 with CRCNS substitute + C20 dense-vs-SSM + C22 inference-only SpikeGPT). Strongest extension-round paper.
- Paper 8 dropped (C15 folded into Paper 3, C16 killed).

**Dropped candidates:** C16, C19. **Fully merged:** C15 → Paper 3; C21 → Paper 5. **Absorbed:** C22 → Paper 7.

## Remaining action items (now with all 22 candidates scope-checked)

1. **Append ~25 missing arXiv IDs to `papers.csv`** (round-1: 16 IDs; round-2 adds Falanti 2506.12810, Lewandowski 2406.06811, LSUV 1511.06422, Fixup 1901.09321, Geometric Dynamics 2403.02579, Shaped Transformer Noci NeurIPS 2023, u-µP Blake 2024, GrokAlign, Grokfast, NeuralGrok, Muon, ⊥SGD/StableMax, GrokTransfer, Geometric Inductive Bias, Low-Dim Curvature, Halloran 2406.00209, Gu-Dao 2405.21060, Ghavasieh 2512.00168, Arola-Fernández 2508.06477, Prakash-Martin 2506.04434, Dong 2502.07547, Lin 2312.01552, SpikeGPT 2302.13939, Spikformer 2209.15425, CRCNS ssc-3 10.6080/K07D2S2F).

2. **Fix 7 citation-ID bugs** in `candidate_ideas.md` and `knowledge_base.md` (Biderman ≠ 3017, Olsson ≠ 3018, Martinello ≠ 2040, di Santo ≠ 2039, Kinouchi-Copelli ≠ 1008, µP ≠ 3008, Meisel ≠ 1034/1035).

3. **Revise `lit_ml.md §Gap`** acknowledging Wang 2604.16431/2604.04655 (dimensional criticality at grokking), Zhang 2410.02536 (intelligence at EOC), GrokAlign, Falanti 2506.12810, Geometric Dynamics 2403.02579, Halloran 2406.00209.

4. **Decide which paper(s) to promote first.** Recommendation: **Paper 1 (Anchor) and Paper 7 (Brain-LLM homology) together**. Paper 7 is inference-only (CRCNS data + public SpikeGPT + pretrained Mamba/Pythia), so it can run in parallel with Paper 1 without sharing GPU time. All other papers (2, 3, 4, 5, 6) are downstream of Paper 1's pipeline and should follow.

---

## Addendum — 2026-04-21 post-merge (209-citation papers.csv)

After merging `papers_round2.csv` (Agent A, 38 entries, IDs 1041-1042 / 2046-2047 / 3056-3089) and `papers_nonarxiv.csv` (Agent B, 31 entries, IDs 4001-4031), total citation count is 209. Six attribution fixes were applied to candidate_ideas.md and lit_ml.md. The non-arXiv venue sweep surfaced seven citations that materially sharpen existing candidates:

**Impact on candidate novelty claims:**

- **4001 Capek et al. 2023 (Nat. Commun.)** — the *parabolic χ = 2* shape-collapse is the expected universality signature for cortical avalanches. Paper 1 / Candidate 12 must test against χ = 2 specifically, not just α ≈ 3/2.
- **4005 Fontenele et al. 2024 (Sci. Adv.)** and **4027 (bioRxiv 2025)** — criticality lives in a low-dim subspace of raw neural activations. Candidate 5's basis-invariance null is reframed: ambient-basis negative is *not* informative unless the SAE / low-dim-projected basis is also negative.
- **4006 Hengen & Shew 2025 Neuron review** and **4007 Sooter et al. 2025 bioRxiv (temporal renormalization group)** — mandatory framing citations for the entire programme; must be in every paper's introduction.
- **4014 Morales, di Santo & Muñoz 2023 (PNAS)** — *edge-of-instability* alternative to pure directed-percolation for cortex. Candidate 12 must add this as an additional non-DP null to reject beyond Griffiths phases and neutral theory.
- **4015-4016 Lombardi / Tkacik** — adaptive-Ising and coherent-bursting non-critical null models. Candidate 12's neutral-null rejection must exclude these too.
- **4017 Mastrovito et al. 2024 bioRxiv** — **direct RNN precedent for "SGD pushes toward edge of chaos"**. Candidate 3's novelty narrows to "transformers specifically, not RNNs". Must cite and position against.
- **4020 Haber et al. 2024** and **4021 Yoneda et al. 2025 (PRR)** — **CNN universality class already assigned to directed percolation**; MLP to mean-field. Candidate 11's CNN control has a published anchor; Candidate 20's architecture-class test must target the *transformer and SSM* assignment as the novel contribution.
- **4003 Xu, Hengen et al. 2024 (Nat. Neurosci.)** — sleep restores criticality — gives Candidate 19 a biological anchor (though Candidate 19 already killed standalone).

**Revised final programme narrowing:**

- **Paper 1 Anchor** now targets three specific shape-collapse exponents (α, τ, χ=2) rather than α alone, aligned with Capek 2023.
- **Paper 3 Training dynamics** narrows to *transformer-specific* criticality drift, with Mastrovito 2024 bioRxiv as the RNN-side precedent.
- **Paper 7 Brain-homology** must cite Hengen-Shew 2025 as framing; must test against Morales edge-of-instability as well as Griffiths; must engage Fontenele's low-dim-subspace finding explicitly.
- **Paper 5 Scale atlas** incorporates Yoneda 2025 CNN-DP baseline as the non-transformer universality-class reference.

**No candidate is newly killed by these finds.** All effects are novelty-tightening: the reframed claims are sharper but smaller. Promotion recommendation stands: Paper 1 + Paper 7 as the first two projects, with the cited additions incorporated into each project's Phase 0 deep lit review.

## Critical findings across all 12 reviews

### Papers the lit review missed (must add to `papers.csv`)

Sixteen arXiv IDs surfaced across the scope-checks that are directly adjacent to the programme and were not in the original lit review. These tighten the novelty claims and in two cases force reframes:

**Directly scooping / partially scooping:**
- **arXiv:2604.16431** (Wang 2026a) "Dimensional Criticality at Grokking Across MLPs and Transformers" — introduces TDU-OFC avalanche probe on transformer activations, measures cascade dimension D(t) crossing D=1 at generalisation transition. Hits Candidates 1, 4, 8.
- **arXiv:2604.04655** (Wang 2026b) "Grokking as Dimensional Phase Transition" — full finite-size scaling, 8 scales × 6 seeds × 51 snapshots. Directly scoops Candidate 4's headline.
- **arXiv:2410.02536** (Zhang 2024) "Intelligence at the Edge of Chaos" — publishes LLM-capability-peaks-at-EOC using Wolfram-class training-data complexity. Partially scoops Candidate 9.
- **arXiv:2501.17727** (Heap, Lawson, Farnik & Aitchison 2025) "SAEs Can Interpret Randomly Initialized Transformers" — mandates random-init-SAE basis in Candidate 5.

**Adjacent prior art (novelty-tightening, not killing):**
- arXiv:2501.04286 — edge of chaos in hyperparameter space, decoder transformers
- arXiv:2510.05554 — critical attention scaling in long-context transformers
- arXiv:2503.13530 — Quasi-Lyapunov across LLM layers (random perturbations)
- arXiv:2603.20991 — Lyapunov stability of transformer compression
- arXiv:2406.00209 — Mamba Lyapunov analysis
- arXiv:2506.04434 — HTSR theory for grokking (Prakash-Martin 2025)
- arXiv:2506.17673 — FaithfulSAE across Pythia sizes
- arXiv:2512.10834 — allometric avalanche scaling in brain data
- arXiv:2512.00168 — DP-universality theory in DNNs / "Tuning universality"
- arXiv:2408.08944 — O-info information-theoretic progress measures for grokking
- arXiv:2603.01192 — SLT basin-transition view of grokking
- arXiv:2508.06477 — Maximum-Caliber maze / Arola-Fernández 2025
- arXiv:2304.01373 — Biderman Pythia original release

### Citation bugs in candidate_ideas.md (must fix before promotion)

- `[3017: Biderman 2023]` in Candidate 7 — ID 3017 is Frankle-Carbin lottery-ticket. Biderman Pythia is missing from papers.csv; needs new ID.
- `[3018: Olsson 2022]` in Candidate 8 — ID 3018 is Kaplan. Olsson is 3024.
- `[2040: Martinello 2017]` in Candidate 12 — ID 2040 is Watkins 2016 SOC review. Martinello is 2037.
- `[2039: di Santo 2018]` in Candidate 12 — ID 2039 is Beggs-Timme 2012. di Santo is 2036.
- `[1008: Kinouchi-Copelli]` in Candidate 9 — ID 1008 is Shew-Plenz 2013 review. Kinouchi-Copelli is 1022.

### Methodological findings common to multiple candidates

1. **Residual-stream confound in layer-resolved observables.** Naive σ_ℓ = ⟨ℓ+1 activations | ℓ activations⟩ ≈ 1 trivially because `h_{ℓ+1} = h_ℓ + F_ℓ(h_ℓ)`. Three cleaner definitions: (a) branching of the *contribution* F_ℓ(h_ℓ); (b) causal σ_ℓ via path patching; (c) layer-wise MR estimator (ill-fitting). Affects Candidates 2, 6, 8.
2. **σ, α, ρ collapse in mean field** — reporting all three as independent evidence is a Schaeffer-style multiple-comparisons trap. Pick ρ (Jacobian spectral radius) as primary; σ, α as cross-checks.
3. **Seed variance demands n ≥ 30 for grokking detection** (given σ_t ≈ 20–40 % of grokking step), not the typical 5. Affects Candidate 4.
4. **Existing nanoGPT sweep data is batch-aggregate only** — full avalanche pipeline needs a ~48 GPU-hour inference rerun to regenerate per-token per-neuron masks. Affects Candidate 2.
5. **RTX 3060 hard cap: Pythia-2.8B fp16**. Larger models need int8 (quantisation confounds exponents) or CPU offload (>30h/pass). Affects Candidate 7.
6. **ROME-directional Lyapunov is tautological as stated** — ROME edits are defined as max-mediation; larger-than-random response restates the definition. Needs matched-subspace null. Affects Candidate 10.
7. **Neutral-null rejection is mandatory** (item 8 of the evidence bar), not a separate paper. Folds Candidate 12 into Candidate 1.
8. **Basis-divergence is the expected null**, not basis-invariance. Candidate 5's null was mis-specified.

## Recommended five-paper programme

The 12 candidates naturally collapse into **5 papers**. Order is topological: later papers depend on earlier ones for pipeline validation and observable baselines.

### Paper 1 — Anchor. "Activation avalanches in trained transformer language models."
**Bundles:** C1 + C6 (§4 layer-depth gradient) + C11 (§5 ViT cross-architecture) + C12 (§6 Griffiths-null rejection) + C8 (§X circuit-specific, if causal-cascade reframe holds).
**Claim:** First measurement of avalanche-size distributions + crackling-noise exponents + MR branching ratio on pretrained GPT-2 and ViT, with Griffiths-phase null rejection and basis-sensitivity across raw-neuron / SAE / PCA / random-projection / random-init-SAE.
**Cost:** ~4–5 weeks. Cheapest path to a publishable positive-or-negative result. Anchors the rest.
**Venue:** NeurIPS main / ICLR main; *Entropy* journal version.

### Paper 2 — Topology tuning. "Skip-connection density tunes distance-from-criticality in a trained transformer."
**Bundles:** C2 (reframed as auxiliary-bypass density + matched-dropout control).
**Prerequisite:** Paper 1 pipeline validated.
**Cost:** ~2 weeks post-processing + ~1 week inference rerun.
**Venue:** ICML main / ICLR main.

### Paper 3 — Training dynamics. "How SGD deforms the criticality landscape."
**Bundles:** C3 + C4 (reframed as head-to-head comparison of σ, dimensional criticality D, HTSR α, O-info on common seeds).
**Claim:** First map of criticality-observable trajectories through training, with tri-init design and Wang/Prakash engagement.
**Cost:** ~3–4 weeks.
**Venue:** NeurIPS main / *Neural Computation*.

### Paper 4 — MI bridge. "Interpretability-basis criticality."
**Bundles:** C5 (SAE-vs-raw basis study with random-init-SAE control) → C10 (SAE-feature-directional Lyapunov with matched-subspace control, sequenced after C5).
**Claim:** First joint treatment of criticality statistics and MI feature primitives.
**Cost:** ~5 weeks.
**Venue:** ICML MechInterp / NeurIPS ATTRIB; *TMLR*.

### Paper 5 — Scale atlas. "The criticality atlas of the Pythia model suite."
**Bundles:** C7 (reframed, Pythia-2.8B cap, 20×5 checkpoint-scale grid) + C9 (capability peak as capstone if time permits).
**Claim:** First scaling-law-style study of criticality observables across model size × training step.
**Cost:** ~4 weeks primary + capstone optional.
**Venue:** ICML main / *JMLR*.

**Parallelisation.** Paper 1 must come first. Once Paper 1's pipeline is validated, Papers 2, 3, 4, 5 can proceed in parallel, sharing activation caches and infrastructure.

## Action items before any promotion

1. **Append the 16 missing arXiv IDs to `papers.csv`** (neuro 1041+, complex 2046+, ML 3056+).
2. **Fix the 5 citation ID bugs** in `candidate_ideas.md`.
3. **Revise `lit_ml.md §Gap`** — the bare "no avalanche exponents on transformers" is partially obsolete after Wang 2604.16431. Reframe to: "no crackling-noise-exponent-discipline + MR-branching-ratio + basis-invariance-rigour study on pretrained transformer LMs, with Griffiths-null rejection".
4. **Decide which paper(s) to promote first.** Recommendation: Paper 1 only, now. Paper 1 is the anchor; all downstream work depends on its pipeline. Promote to `applications/entropy_avalanches/` (or similar slug). Re-open the promotion queue once Paper 1 is past Phase 0 and the infrastructure is validated.

Once action items 1–3 are done and the user chooses the promotion slug, a per-project deep Phase 0 lit review (target 200+ citations, deeper on avalanche-detection algorithms + Gemma / Pythia activation-analysis toolchain) kicks off for the promoted project.
