**Target type**: publication-target

# entropy_avalanches — Activation Avalanches in Trained Transformer Language Models

## Target paper

Multi-predicate statistical-physics characterisation of activation avalanches in pretrained transformer language models (GPT-2, Pythia, Gemma) on natural text: Clauset-Shalizi-Newman power-law fit + Sethna crackling-noise γ = (β−1)/(α−1) cross-check + shape-collapse (parabolic χ=2 per Capek 2023) + MR-estimator branching ratio + threshold plateau + Griffiths-phase neutral-null rejection + basis-invariance battery including **random-init-SAE control (Heap et al. 2025)** + **Fontenele-subspace σ on the top-K-PC projection (not just ambient)**. The headline is the *conjunction*, not any single observable — Wang 2604.16431, Zhang 2410.02536, Nakaishi 2406.05335 and Fontenele 2024 each address single pieces of the battery on adjacent substrates.

**Primary observable discipline post-Phase-0.25 reframe: foreground the causal-cascade observable (path-patching per-head avalanches) over correlational P(s).** The correlational-vs-causal distinction was the strongest hostile-reviewer line of attack; foregrounding causal lifts the paper out of "ornate replication of Wang" framing.

## Bundled candidates (post-Phase-0.25 reframe)

From `applications/entropy_ideation/candidate_ideas.md` and `promoted.md`, four reframes applied per `publishability_review.md`:

**Primary §-level arms (main claims):**
- **C1 (§2–§4) — Anchor.** Avalanche exponents on GPT-2 / Pythia / Gemma with CSN + Sethna γ = (β−1)/(α−1) + parabolic χ=2 shape collapse + MR-σ + threshold plateau + Griffiths-null.
- **C8 reframed + C28 (§5) — Causal-cascade criticality, foregrounded.** Per-head path-patching causal σ distribution across all 144 / 288 GPT-2 heads; induction-head vs entropy-matched null within that distribution. Foregrounded over correlational P(s) to counter the "correlational-not-causal" hostile-reviewer attack.
- **C29 imported (§6) — Fontenele subspace σ.** Top-K-PC subspace σ and reconstructed-scalar avalanche analysis (Fontenele 2024 method replication). Previously sibling-project-only; now a Paper-1 first-class arm. The ambient-basis negative is uninformative without this arm.
- **C12 (§7) — Neutral-null rejection.** Martinello / di Santo / Lombardi / Tkacik Griffiths-phase + coherent-bursting + adaptive-Ising null battery. Mandatory methodology, not a separate paper.

**Secondary arms:**
- **C6 §8** — layer-depth gradient of causal σ_ℓ (path-patching, not residual-stream confound). γ scaling-relation per-layer is *secondary* (under-powered per Phase-0.25; report with wide CIs, not flagship).
- **C11 §9** — ViT-Tiny / CIFAR-10 cross-architecture universality arm. Commit to shape-collapse + threshold-plateau explicitly (Phase-0.25 gap).

**Appendix only:**
- **C25 appendix** — d_β temporal-RG probe. **Not a main-claim arm per Phase-0.25 reframe.** Ship as a consistency check on the same activation cache, don't headline it.

**Reframe on random-init-SAE basis (per Phase-0.25):** widen from 3-layer to **all 12 layers on GPT-2-small** (so it's a basis-invariance test, not a 3-point check). Drop the random-init-SAE arm from Pythia-2.8B and Gemma-2-2B to fund the compute. GPT-2-small carries the full basis-invariance claim; larger models carry only raw / PCA / random-projection / trained-SAE.

## Scope and constraints

- **Single RTX 3060 12 GB.** Inference-only on pretrained weights. No new training (except for small at-init control).
- **Cap at Pythia-2.8B fp16.** Larger models via int8 only as secondary / appendix.
- **All 8 evidence-bar items** from `../entropy_ideation/knowledge_base.md §5` must be addressed.

## Prior-art engagement (mandatory citations)

- Wang et al. 2026 (arXiv:2604.16431, 2604.04655) — dimensional criticality at grokking; differentiate by: pretrained LLMs on natural text + full CSN discipline + MR σ + crackling-noise cross-check + basis-invariance + Griffiths-null rejection.
- Zhang et al. 2024 (arXiv:2410.02536) — intelligence at edge of chaos; differentiate by: activation-space σ, not training-data Wolfram-class axis.
- Heap, Lawson, Farnik & Aitchison 2025 (arXiv:2501.17727) — SAEs on random-init networks; mandates random-init-SAE control.
- Nakaishi 2406.05335 — Pythia temperature-axis criticality; differentiate by: scale and training-trajectory axes on natural text.
- Capek et al. 2023 (Nat. Commun., papers.csv 4001) — parabolic χ = 2 shape-collapse expectation for cortical avalanches.
- Fontenele 2024 Sci. Adv. (papers.csv 4005) — low-dim subspace for criticality; ambient-basis negative is not informative unless subspace is also negative (motivates companion Paper 11).

## Phase sequence (per program.md)

- **Phase 0 — deep lit review** (in progress, agent-driven; target 200+ citations scoped to activation criticality in deep networks + cortex avalanche methodology).
- **Phase 0.25 — publishability review.**
- **Phase 0.5 — baseline audit and data-access verification** (HuggingFace weights for GPT-2 / Pythia / Gemma / ViT-Tiny; Gemma Scope SAE weights; CIFAR-10 already cached; CRCNS ssc-3 for the Griffiths-null control cortex reference).
- **Phase 1 — pipeline build**: activation caching, CSN / crackling / shape-collapse / MR-σ implementations with unit tests (TDD per `CLAUDE.md`).
- **Phase 2 — experiments**.
- **Phase 2.75 — methodology review.**
- **Phase 3 — paper draft.**
- **Phase 3.5 — adversarial paper review.**
- **Phase 4 — submission.**

## Venue target

Per Phase-0.25 publishability audit: **parallel submission strategy, not sequential fallback.** Honest success probabilities conditional on clean execution of the reframed bundle: NeurIPS / ICLR main 25–35%, ICML MechInterp workshop ~70%, *Entropy* journal ~85%, TMLR ~60%. Recommendation: submit the extended version to NeurIPS main and a compressed "observable-battery" version to workshop simultaneously. If NeurIPS rejects with reviews worth addressing, escalate; if rejection is dismissive ("replication of Wang"), pivot to TMLR.

## Phase 0.25 reframes applied (2026-04-21)

Full review at `publishability_review.md`. Four load-bearing reframes:
1. **C29 (Fontenele subspace σ) imported as §6 first-class arm.** Previously sibling-project-only; ambient-basis negative is uninformative without it.
2. **Causal-cascade observable (C8 reframe + C28) foregrounded over correlational P(s).** Counters "correlational-not-causal" hostile-reviewer attack.
3. **Random-init-SAE basis widened** from 3 layers to all 12 on GPT-2-small; dropped from Pythia-2.8B / Gemma-2-2B to fund compute.
4. **C25 (TRG d_β) confirmed appendix-only**, not a main-claim arm.

## Parent ideation

See `../entropy_ideation/` for the full 35-candidate portfolio, 239-paper `papers.csv`, and the landscape `literature_review.md`. This project is the "Anchor" of a 12-paper programme.
