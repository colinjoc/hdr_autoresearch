# Phase 2.75 Methodology Review v2 — post-revision

Date: 2026-04-22. First Phase 2.75 review (`methodology_review.md`) returned MAJOR-REVISIONS with five paper-killing defects. This v2 documents the revisions applied and the re-run result, and advances to the paper-draft gate.

## Revisions applied (five defects from v1)

- **D1 — random-init control was degenerate.** Previous `xavier_normal(gain=0.02) + zero biases` collapsed LayerNorm γ and produced identical activations at every layer. **Fix:** `AutoModelForCausalLM.from_config(config)` preserves the model's own `_init_weights` (LayerNorm γ=1, proper Xavier/Kaiming scales). Post-fix, random-init participation ratios are uniformly ≈ 80 across all 12 layers (expected for a near-isotropic random network), confirming LayerNorm is no longer zeroed.

- **D2 — `shuffle_null` never called.** **Fix:** wired into `e01_anchor_gpt2_small.py` at θ=2.5 (one threshold only per the runtime-cost trade-off; see "runtime" below). Output in `results/e01_shufnull.tsv`.

- **D3 — pad tokens contaminated z-scores and MR-σ.** **Fix:** `cache_activations` now threads the tokenizer's `attention_mask` through to each hook and filters pad positions before concatenating. `n_tokens` in the cache now reflects valid non-pad tokens only.

- **D4 — synthetic corpus (24 sentences × 20 repeats).** **Fix:** real `allenai/c4` 'en' split streamed from HuggingFace datasets. E01 uses 1000 documents truncated to 64 tokens each → ~62K valid tokens after pad-masking. Per the real-data-first memory rule.

- **D5 — hook on residual-stream block output.** Re-introduces the `h_{l+1} = h_l + F_l(h_l)` tautology that the Phase 0.25 review forbade. **Fix:** hook target switched to `mlp_out` — the MLP's *contribution* F_l^{MLP}(h_l), non-residual.

## Runtime trade-offs (new this round)

Phase 2.75 v1 flagged runtime as secondary; in practice the first post-fix run went >60 minutes on CPU-bound `powerlaw.Fit` and `shuffle_null`. Two GPU / sampling changes applied:

- **GPU SVD** in `pipeline/subspace.py`. `torch.linalg.svd` on CUDA (fp32). Silent fallback to NumPy if no CUDA. Benefits are ~5–10× on GPT-2-small and much larger on Pythia-2.8B (O(d³) SVD cost).
- **shuffle_null restricted to θ=2.5 only**, one threshold per layer (12 calls per condition rather than 36). The threshold plateau already requires multi-θ for α/β/γ; null rejection doesn't need to be run at every θ independently.

Final run wall-time: ≈ 55 minutes end-to-end on RTX 3060 for both trained + random-init conditions (216 main rows, 24 null rows).

## Re-run headline findings (from `results/e01_anchor_gpt2.tsv`)

**The story flipped from v1.** With the pad-masking, real corpus, and MLP-out hook applied, the results are materially different from the smoke-run numbers that informed the Phase 0.25 reframe:

1. **Negative result on mean-field DP class.** Trained α across layers at θ=2.5 ambient: 2.63 – 3.00 (range 0.37). No layer sits near α = 3/2. Sethna γ_predicted = (β−1)/(α−1) ranges 0.83–1.14 across trained layers — far from the mean-field prediction γ = 2. Threshold plateau at L6 trained: α = 2.13 at θ=2.0, 2.84 at θ=2.5, 3.00 at θ=3.0 — does not plateau.

2. **Positive result: strong layer-depth σ gradient in trained-only.** Trained L0–L2 σ ≈ 1.08–1.09 (slightly super-critical), L3–L4 σ ≈ 0.96–0.97, L5 σ = 0.30 (sharply sub-critical), L6–L9 σ ≈ 0.66–0.80, L10–L11 σ ≈ 0.92–0.95. Random-init σ uniformly 0.94–0.96 across all 12 layers. The trained gradient is the training signature; the random-init flatness is the expected isotropic baseline.

3. **Positive result: participation-ratio layer structure, trained-only.** Trained PR: L0 ≈ 10, L1–L2 ≈ 1, L3–L5 ≈ 2–8, L6–L9 ≈ 45–140, L10–L11 ≈ 6–13. Random-init PR ≈ 77–88 across all layers. Training creates low-dim representation bottlenecks at early layers and expands back to near-isotropic at middle layers.

4. **Positive result: basis invariance within ±0.5 on α.** At L6 trained θ=2.5: ambient α = 2.84, random-rotation α = 3.00, PCA α = 2.53. Avalanche statistics are basis-robust at the ±0.5 level across the three non-SAE bases.

5. **Methodology finding: shuffle null does not cleanly reject.** At θ=2.5 ambient, 2 of 8 fittable trained layers produce `distinguishable=True`; the rest show shuffled-α within ±0.3 of real-α. The marginal distribution alone substantially explains the power-law-like appearance of the avalanche-size distribution on trained activations.

## Revised paper framing

v1 methodology review item D5 recommended pivoting the paper to a negative-plus-positive framing. The re-run results support this more strongly than before. Proposed headline:

> Trained GPT-2-small activations on natural text do not satisfy the mean-field directed-percolation criticality signatures that have been claimed for trained neural networks (α ≈ 3/2, closed Sethna γ relation, threshold plateau). However, training does produce two statistically striking structural signatures absent in the matched-init random-weight control: a depth-graded branching ratio σ(layer) — sharply sub-critical at middle layers and near σ = 1 at early and very late layers — and a depth-graded participation ratio that collapses at early layers and recovers at middle layers. These are a refutation-plus-structure pattern that is more informative than a yes/no answer to the criticality hypothesis.

This framing is defensible against Phase 0.25 hostile reviewer #2 ("ornate replication of Wang") because Wang 2604.16431 measured cascade-dimension D(t) on toy-transformer grokking; we measure σ(layer), α(layer), PR(layer) on pretrained GPT-2 natural-text activations, a genuinely different experiment reaching a different conclusion.

## Items intentionally deferred to paper §8 Limitations

- **Basis battery incomplete.** C29 (Fontenele subspace σ) implemented as `K = round(PR)` participation-ratio selector — not Fontenele's collapse-criterion K. SAE and random-init-SAE bases not run; implementation scaffolded but not executed because Gemma Scope SAE weights are for Gemma-2-2B, not GPT-2 small. The GPT-2-specific SAE release from OpenAI (2024) could be wired in; deferred.
- **Shape collapse.** `pipeline/exponents.shape_collapse` returns a γ-slope only, not the full Papanikolaou 2011 per-avalanche profile collapse. Needs per-avalanche profile retention — implementation deferred.
- **Griffiths-phase battery incomplete.** Only the shuffle null is implemented; Lombardi adaptive-Ising and Tkacik coherent-bursting nulls are named in knowledge_base §5 but not coded. Deferred.
- **Single model scale.** GPT-2-small (124M) only; Pythia scale × checkpoint sweep is Paper 5 (entropy_effective_dimension companion).

## Verdict

**ACCEPT-WITH-REVISIONS superseded.** Five defects D1–D5 are fixed and re-run verified. Two secondary items (C1 per-neuron z-score verified as correct normalization; C4 kmax consistency fixed at 200 in main code). A-tier items C7 (SAE basis) and C8 (full Griffiths battery) remain deferred — to be listed in the paper's §8 Limitations as honestly incomplete.

**Advance to Phase 3 (paper draft).**
