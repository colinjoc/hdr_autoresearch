# Phase 2.75 Methodology Review — entropy_avalanches

**Reviewer.** Phase 2.75 sub-agent, fresh context. Not the Phase 0 / 0.25 / 0.5 / 1 / 2 agent.
**Date.** 2026-04-21.
**Mandate.** Audit the five methodology dimensions below and deliver ACCEPT-WITH-REVISIONS / MAJOR-REVISIONS / REFRAME before the paper draft. Reviewer is explicitly invited to be harsh.
**Artefacts read.** `README.md`, `publishability_review.md`, `phase_0_5_audit.md`, all six `pipeline/*.py` modules, `experiments/e01_anchor_gpt2_small.py`, `experiments/make_figures.py`, `results/e01_anchor_gpt2.tsv` (96 rows), the three PNG figures, `../entropy_ideation/knowledge_base.md`, and all three test files (`tests/test_pipeline_*.py`).

**Verdict up front: MAJOR-REVISIONS.** Five load-bearing bugs or gaps in the E01 run make the present TSV unsafe to write a paper on. None is fatal to the pipeline *architecture* — all are fixable in days, not weeks — but shipping a draft on the current cache would embed errors a hostile reviewer can one-line. Details below, in decreasing order of severity.

---

## S-tier methodology defects (paper-killing if un-fixed)

### D1. Random-init control is pathologically degenerate — it is not a control, it is a bug.

The TSV (`results/e01_anchor_gpt2.tsv`) rows 50–97 show that at every layer 0–11 and every threshold θ ∈ {1.5, 2.0, 2.5, 3.0} the random-init run produces **literally identical numbers** (same PR = 34.16, same σ_ambient = 0.99958, same σ_subspace = 0.97820, and at θ=3 the same α = 2.8428, n_avalanches = 3040). Two independent diagnoses:

1. The `activation_cache.cache_activations` random-init branch re-initialises weights with `xavier_normal_(p, gain=0.02)` and zeros all bias-shaped vectors (including LayerNorm γ, which is *not* a weight-matrix). Zeroing LayerNorm γ forces every block's output to zero on the residual-path contribution, leaving only the identity skip. The residual stream is then essentially the token embedding at *every* layer — which is exactly why every layer reports the same PR, the same σ, and the same exponent fit. This is confirmed by `sigma_ambient == 0.99958` being identical across 12 layers on ostensibly different activations.
2. Alternatively (or additionally) `gain=0.02` on 768-wide weight matrices produces effective per-layer spectral radius far below any training-induced nonlinearity regime; combined with the LN-γ issue the random-init activations are a near-degenerate linear map from embedding to residual stream.

**Impact.** The fig-1 headline claim ("training pulls σ toward the reverberating regime") compares a real trained model against a control that is approximately the token-embedding itself. The control is nearly critical (σ ≈ 1) not because random-init transformers are critical, but because the random-init transformer, as currently initialised, is a no-op. A reviewer who re-runs with a Kaiming or standard-transformer init will get a different σ profile and the paper's primary figure evaporates. This is a D=1 methodology-integrity problem.

**Required fix.** Drop the custom `xavier_normal_(gain=0.02) + zero-bias` re-init. Either (a) reload `GPT2Config.from_pretrained("gpt2")` and call `model.init_weights()` or `AutoModel.from_config(cfg)` (HF's own pre-training init), or (b) explicitly replicate the GPT-2 reference init (normal(μ=0, σ=0.02) for linears + bias=0 + LN γ=1 + LN β=0). The test `test_random_init_gives_different_activations` at `tests/test_pipeline_core.py:102` only checks that trained-σ ≠ init-σ, which does not catch the degenerate-control case (both σ and degenerate linear map can differ from trained). Add a regression test: random-init σ_ambient at layer 0 must differ from random-init σ_ambient at layer 11 by > 0.02. Currently it is 0.0.

### D2. Shuffle-null is imported but never invoked — the "null-rejection" column does not exist.

`experiments/e01_anchor_gpt2_small.py:34` imports `shuffle_null`; it is never called anywhere in the script. The TSV has no null-rejection column. The README claims `shuffle_null` is part of the "Phase 1 complete" pipeline; the publishability review's evidence-bar item 8 ("neutral-null rejection") is marked "partially present" in the task prompt. **It is not present in E01 results.** Any α ≈ 3/2 claim absolutely requires a neutral-null rejection per Touboul-Destexhe 2010/2017 and Martinello 2017, and the anchor experiment ships none.

Secondary bug: `pipeline/nulls.py:51–52` calls `binarise_activations(activations, threshold)` without `zscore=True`, whereas the experiment uses `zscore=True`. This is a silent units mismatch: if the experiment z-scores before thresholding at θ=2 (σ units), but the null thresholds at raw magnitude 2 (fp16 residual-stream magnitude, typically 20–100), the two are incomparable. The shuffle-null bug is latent because nothing calls it; but when it *is* wired in, this will produce garbage.

**Required fix.** Plumb `shuffle_null(..., zscore=True)` through the signature; call it per (layer, θ) and record `shuffled_alpha`, `shuffled_p_vs_exponential`, `distinguishable` in the TSV.

### D3. Pad tokens are included in the activation cache and in every downstream statistic.

`pipeline/activation_cache.py:104` sets `padding=True` on the tokeniser and the forward-hook (lines 85–89) flattens `(batch, seq, d_model)` → `(batch*seq, d_model)` without masking pad tokens. With `max_length=64` and a 24-sentence corpus whose sentences range ~15–30 tokens, **roughly half of the cached "tokens" in E01 are PAD**. Consequences:

1. **MR-σ is contaminated** by a large block of identical (pad-token) residual-stream activations. Pad tokens create a highly autocorrelated stretch in the activity time series, inflating the exponential-autocorrelation fit that drives `fit.mre`. This biases σ upward — and likely explains why the supposed-critical σ ≈ 0.97 numbers in middle layers are so clean.
2. **Avalanche detection** per-neuron z-scores over (tokens × neurons) where ~50 % of rows are near-identical pad activations. The per-neuron σ is inflated, z-thresholds are systematically too lenient, and the "event" definition is contaminated.
3. **The total real-token count is ~15 K as claimed, but the total cached "tokens" in the TSV is probably ~30 K**, of which half are noise.

**Required fix.** Use the tokeniser's attention mask to drop pad-token rows from the per-layer cache before any statistics. This is 2 lines of code and is the standard pretrained-LM activation-analysis protocol (it is what TransformerLens does by default).

### D4. The corpus fails the real-data-first rule and is too small regardless.

24 hand-written sentences × 20 repetitions = 480 samples, max_length=64, → ~15 K real tokens. Three problems:

1. **Repetition breaks i.i.d. sampling.** The same 24 sentences repeated 20× puts 20 identical token-sequences into the cache, so the effective independent-sample count is ~24 sentences worth of tokens ≈ 750 tokens, not 15 K. MR-σ fitting requires T ≥ 1000 *independent* samples; the effective T is below that floor.
2. **24 hand-written sentences is synthetic data.** Per `~/.claude/CLAUDE.md`, if The Pile / C4 / WikiText-103 is available via HuggingFace `datasets` (it is), synthetic hand-written text is not acceptable unless a stated reason for unavailability is given. There is no such reason. This is a D=1 rubric penalty by the user's own rule.
3. **15 K tokens is under-powered for α.** The Clauset-Shalizi-Newman minimum for ≥ 2 decades of scaling range is typically 10³–10⁴ avalanches; E01 reports 200–380 per (layer, θ) at θ=2. That is < 1 decade.

**Required fix.** Load a 1 M-token stream from `EleutherAI/pile` or `allenai/c4` or `wikitext-103` via `datasets.load_dataset(..., streaming=True)`, tokenise, and cache at max_length ≥ 256. On an RTX 3060 with GPT-2-small fp16 this is an afternoon of inference time. Phase 0.5 already verified the HF weights path. No new data-access work needed.

### D5. Threshold plateau fails — and this is itself a finding, but the pipeline handles it silently.

The emerging finding "α drifts 2.0→3.0 as θ varies 2.0→3.0 at the middle layer" is confirmed by the TSV rows 26–29 (layer 6): α = 2.32 at θ=2, 1.99 at θ=2.5, 2.74 at θ=3. Evidence-bar item 6 (threshold plateau) is not just partially met — it is actively violated. Per `knowledge_base.md §5` this makes the observation "critical-like but not critical" at best, and a neutral-null-compatible result at worst.

This is not a pipeline bug — it is the *correct* output of a correct plateau test. The methodology problem is that the paper framing in README.md and publishability_review.md still headlines α-fitting as a primary observable; if the plateau fails, the α value is not a universality-class pointer and the Sethna γ cross-check (which requires a stable α, β) is also unsafe. The paper must pivot to "we see scale-free activity without a plateau, consistent with Griffiths-phase / lognormal-mimic / correlated-noise; we reject a DP-criticality claim."

**Required fix.** Not a code fix — a framing fix. The paper should not be "anchor exponents match mean-field DP". It should be "anchor exponents do NOT match mean-field DP; threshold plateau fails; MR-σ shows layer-depth gradient inconsistent with global criticality; we therefore report a negative result on the strong-DP-criticality hypothesis for pretrained transformers on natural text."

---

## A-tier methodology concerns (fixable, non-blocking but reviewer-facing)

### C1. Per-neuron z-score is defensible but not universal.

The review-contract question is whether per-neuron z-score (each column gets its own μ, σ) is the right adaptation of Beggs-Plenz 2003 to continuous transformer activations. Answer: yes, with a caveat.

- Beggs-Plenz 2003 thresholded extracellular voltage against a *per-electrode* noise floor. Per-neuron z-score is the LLM analogue and is used by Yoneda 2025 and Nakaishi 2406.05335. **Defensible.**
- Caveat: per-neuron normalisation destroys any magnitude-structure in the residual stream. If the signal is carried by a small number of high-magnitude "outlier" features (Dettmers 2022), z-scoring rescales them to the same σ-units as low-magnitude features and may wash out genuine avalanches. A per-*layer* global z-score (one μ, σ per layer) is an alternative worth reporting as a robustness check.
- Cartesian recommendation: report both per-neuron and per-layer global z-score in an appendix. If the two agree on α within CI, fine. If not, the paper must say which defines the "event."

### C2. `bin_size = 1` (token-level) is correct for MR but arguably too fine for avalanche detection.

Beggs-Plenz and Priesemann bin at ≈ mean inter-spike interval. Token-level binning is the transformer analogue if one treats tokens as time. Retaining bin_size=1 is correct for the MR-σ estimator (which wants the finest possible resolution of the autocorrelation function). It may over-segment avalanches at low θ, since a single quiescent token ends an avalanche. The evidence-bar item 6 plateau test should also sweep bin_size ∈ {1, 2, 4} to separate threshold-dependence from bin-dependence. Currently only θ is swept.

### C3. CSN implementation — `distribution_compare` defaults and xmin auto-fit.

- `fit_power_law` at `exponents.py:44–47` uses `powerlaw.Fit(samples, discrete=True)` with auto `xmin`. Standard CSN protocol (Clauset-Shalizi-Newman 2009, Alstott 2014). **Correct.**
- Drop of `samples[samples >= 2]` singleton removal (line 41) is a standard choice in cortical-avalanche papers — singletons dominate the low-size region and do not inform the power-law tail. **Standard.**
- The three Vuong LLR tests against lognormal, exponential, truncated-power-law are the right protocol. **Correct in the limit.**
- **Gap:** the function returns a Vuong p, but the *sign* of R matters too. `fit.distribution_compare` returns `(R, p)`; the PowerLawFit dataclass stores only `p`. If R < 0, lognormal wins; if R > 0, power-law wins; a small p with R < 0 means lognormal is *preferred*, not rejected. Currently the TSV has `p_vs_lognormal ≈ 1e-9` on many rows which is easy to misread as "power-law wins strongly" when it in fact means "the two hypotheses are strongly distinguishable" — the *direction* is in R, which is discarded. This is a silent bug. Fix: store R as well and report (R, p) jointly.
- **Gap:** no bootstrap goodness-of-fit p-value for the power-law itself (the Clauset 2009 §C bootstrap). Only alternative-distribution LLRs are reported. Add `fit.plfit.bootstrap(n_resamples=2500).p_value`.

### C4. MR-estimator — kmax inconsistency and method choice.

- `exponents.py:129` defaults `kmax=500` and `method='ts'`. The test `test_branching_ratio_mr_recovers_sigma` uses `kmax=500`. The experiment `e01_anchor_gpt2_small.py:86` uses `kmax=200`. **Inconsistent with tests.** Minor — `kmax` sets the upper lag used in the exponential-autocorrelation fit. At kmax=200 with T=~20–30 K tokens the fit window is fine; but the test coverage does not actually exercise the experimental code path. Fix: align to one kmax (200 is fine) and update the test.
- `method='ts'` is trial-separated. With a single long time series across 480 concatenated sentences, this is not quite right — `method='sm'` (stationary-mean) is better, or the MR should be applied per-sentence with `method='ts'` across sentences. Currently the pipeline reshapes `activity.reshape(1, -1)` → one giant "trial." Sentence boundaries introduce discontinuities that the MR exponential-autocorrelation model does not handle — similar to the Phase 0.5 driven-BP re-seed issue, noted in `phase_0_5_audit.md`, but for natural text. Fix: reshape per-sentence to `(n_sentences, per_sentence_length)` and use `method='ts'`, or call with `method='sm'` and a block-bootstrap CI.
- **Wilting-Priesemann subsampling correction is inherent to `fit.mre`.** The pipeline uses `fit.mre` not `fit.m_naive`. **Correct.**

### C5. Sethna γ cross-check — log-bucket width is not catastrophic but is arbitrary.

- `exponents.py:92` uses 0.2-decade log-bucket width. Sethna-Dahmen-Myers 2001 and the cortical-avalanche canon (Friedman 2012, Capek 2023) vary between 0.1 and 0.25 decades. 0.2 is within range. **Acceptable.**
- The `mask.sum() > 10` per-bucket minimum (line 95) is a weak filter. Shaw-Friedman's fit-to-convergence protocol requires ≥ 50 per bucket for a stable mean. With 200–380 avalanches total (E01) and ~5 buckets spanning 2-decade duration range, per-bucket counts are ~40–80; borderline. This is the underpinned-ness that `publishability_review.md §2` already flagged for the per-layer γ.
- **Gap:** the pipeline does not bootstrap γ_measured or γ_predicted. The TSV reports point estimates only. A reviewer will not accept a scaling-relation closure/failure claim without ≥ 95 % CIs on both. Add bootstrap: 500 resamples of the (s, T) pair set, recompute (α, β, γ_pred, γ_meas) per resample, report 2.5 / 97.5 percentiles.
- The implementation is otherwise faithful to Sethna 2001.

### C6. Fontenele subspace K-selection does not match Fontenele's rule.

The review-contract question: is `K = round(PR)` the Fontenele operational rule? Answer: **no.**

Fontenele 2024 Sci. Adv. defines K as the largest K such that the complement-subspace avalanche distribution passes the power-law test over ≥ 1.5 decades, or equivalently the smallest K such that the top-K-PC reconstruction captures the "critical" scaling component. `pipeline/subspace.py:73` documents this in the docstring as `method='fontenele_operational'` but the implementation (`K = max(2, int(round(pr)))`) uses participation-ratio as a proxy and never exercises the collapse-criterion branch. The pipeline file honestly says this is a Phase 1 stub.

Impact on E01: PR collapses from ~34 (random-init) to ~1 (trained) — so `K = max(2, round(PR)) = 2` on every trained layer except layer 0 (PR=7.4, K=7) and layer 11 (PR=9.3, K=9). **Setting K=2 for 9 of 12 layers is almost certainly wrong** — it hard-codes a 2-D subspace for Fontenele-replication regardless of the true effective dimension of the critical component. Fontenele's own paper reports K ≈ 10–30 on cortical data. K=2 is implausibly low for transformer residual streams and is driven entirely by the PR-rounding rule, not by a collapse criterion.

**Required fix.** Either (a) implement the collapse-criterion K-sweep: for K ∈ {2, 5, 10, 20, 50, 100}, compute σ_K on the reconstructed scalar and the CSN power-law fit on the complement-subspace; pick the largest K for which both the σ_K is near 1 and the complement fit still closes. Or (b) explicitly state "we use PR as a K proxy, not Fontenele's collapse-criterion — a full replication is deferred to Paper 11" and move the subspace arm to an appendix. Option (b) is faster but concedes the headline Fontenele claim. Option (a) is ~3 GPU-days as budgeted in Phase 0.5.

### C7. Basis-invariance battery is not present in E01.

Per publishability_review.md §6, the Phase-0.25 reframe committed to a basis-invariance battery on all 12 GPT-2-small layers: raw / PCA / random-projection / trained SAE / random-init SAE. E01 runs **only** ambient (mean-magnitude) and top-K-PC subspace σ. Missing from E01: random projection, trained SAE (OpenAI / Anthropic / SAE Lens), random-init SAE.

The knowledge-base `§3.1` explicitly labels basis-sensitivity as *"itself a publishable observation"* — but the paper cannot make basis-sensitivity claims when only 2 of 5 bases are measured. The Heap 2501.17727 random-init-SAE is the single most important control in the whole publishability_review.md argument (it is item 2 of the multi-predicate novelty claim). It is missing.

**Required fix.** Add random-projection and at least one trained-SAE basis to E01 before the paper draft. Random-init SAE can be deferred only if the README's "reduced scope" is re-scoped with honesty ("random-init-SAE reported on one layer as a proof-of-concept, full 12-layer sweep in the workshop-length version"). The ambient-subspace-only result is, as the publishability review predicted, "uninformative" without these other bases.

### C8. Griffiths-null battery is not implemented.

Evidence-bar item 8 (Martinello 2017 Griffiths phase + Lombardi coherent bursting + Touboul-Destexhe neutral null + Qu 2022 heavy-tailed Anderson) is covered in the pipeline by `shuffle_null` only. Shuffle-in-time destroys temporal correlations but preserves per-neuron marginal event rates — this rejects only the *simplest* Poisson-coincidence null. It does **not** reject Griffiths-phase (which produces scale-free-looking distributions in quenched-disordered systems without fine-tuning) or coherent-bursting (which produces power-law-like distributions via magnitude-driven bursts).

The publishability review (§6 reframe #2) did not list Griffiths rejection as a pre-Phase-1 blocker, but the methodology-review contract explicitly asks. Honest answer: **the Griffiths rejection is not done.** `shuffle_null` is a shuffled-Poisson null, not a Griffiths null. The Sethna γ cross-check is the *theoretical* Griffiths-rejection signal (γ closure fails in Griffiths phases), which is exactly what E01 already shows — γ does not close. That is compatible with "we are in a Griffiths-like regime, not genuine DP criticality." Which is fine, but must be stated.

**Required fix.** Either (a) add a quenched-disorder Ising or 2-D contact-process Griffiths simulation as a reference null (Martinello 2017 §3), fit it through the same pipeline, and show the real transformer data is distinguishable. Or (b) state explicitly that the γ-closure failure in E01 is *consistent* with a Griffiths-phase interpretation and reframe the paper as "evidence for Griffiths-phase-like dynamics in trained transformers, not directed-percolation criticality." The latter is a substantive reframe and should be blessed by Phase 2.75.

---

## B-tier concerns (nice-to-have, not paper-blocking)

- **`xmin` auto-fit on tiny samples.** With 200 avalanches per layer-θ, `powerlaw.Fit` auto-`xmin` is unstable (it minimises the KS statistic which has a bimodal landscape at small N). Report `xmin` per row alongside α so reviewers can see whether xmin jumps around.
- **Shape-collapse is a stub.** `exponents.shape_collapse` returns `chi = 2.0` as a hardcoded constant (line 191). Evidence-bar item 4 (shape-collapse figure passes eyeball test) is therefore not implemented. Phase 2 was meant to fill this in; it has not.
- **`test_pipeline_core.py:test_detect_avalanches_binning`** passes but its arithmetic in the docstring is wrong — it says "bin_size=2 -> [1,1,1,0]" but `[1,0,1,0,1,0,0,0]` binned at 2 gives `[1,1,1,0]` only if partial bins are dropped; the code does `trunc = (T//bin_size)*bin_size` then sums, correctly producing `[1, 1, 1, 0]`. Test is correct; comment is confusing. Cosmetic.
- **Hooks capture residual-stream *output* of each block, not the sub-layer contribution.** Per publishability_review.md §3(a), naive layer-to-layer σ on residual-stream has a tautological σ ≈ 1 from identity skip; the publishability review committed to using `F_ℓ(h_ℓ)` or path-patching. E01 ignores this and uses residual-stream output directly. The layer-depth σ gradient reported (supercritical early / reverberating middle / subcritical last) is therefore residual-stream-confounded in exactly the way §3(a) flagged. **This is a reviewer-facing vulnerability; see also D1.**

---

## Direct answers to the contract questions

**Avalanche event-definition.** Z-score-then-threshold is valid. Per-neuron normalisation is defensible but needs a per-layer-global check. bin_size=1 is correct. Pad-token contamination (D3) is the bug.

**CSN implementation.** Broadly correct. Store R as well as p (C3 gap). Add `powerlaw.Fit.plfit.bootstrap` goodness-of-fit p. Plateau failure (D5) forces a framing pivot.

**MR-estimator.** Wilting-Priesemann subsampling correction is correctly applied via `fit.mre`. `method='ts'` with a single concatenated trial is wrong — use `method='sm'` or reshape per-sentence (C4). kmax inconsistency test↔experiment is cosmetic.

**Sethna γ.** Faithful to the formula. Add bootstrap CIs. 0.2-decade bucket width is fine.

**Controls + honesty.** Random-init control is broken (D1), threshold plateau fails and this *is* a finding (D5, requires framing pivot), basis-invariance absent from E01 (C7), Griffiths-null absent (C8), at-init control = random-init = broken (D1).

**Corpus size.** 24 hand-written sentences × 20 repeats is insufficient and violates the real-data-first rule (D4).

**max_length=64.** Too short given the pad contamination (D3); 15 K tokens is 10× below what CSN and MR need. Fix by (a) removing padding and (b) loading a real stream.

**Fontenele K.** Not Fontenele's rule (C6). Either implement collapse-criterion K-sweep or downgrade the arm.

**Shuffle-null alone.** Not strong enough. Needs Griffiths-phase and coherent-bursting nulls per Martinello 2017 / Lombardi 2012 (C8). And currently not even invoked in E01 (D2).

---

## Verdict

**MAJOR-REVISIONS.** Five S-tier defects (D1–D5) are paper-killing if un-addressed: a broken random-init control, an un-invoked shuffle-null, pad-token contamination of every statistic, a 15 K-token synthetic corpus, and a silent framing mismatch with the threshold-plateau failure. All five are fixable in ~1 week of engineering + re-run time on the RTX 3060. Eight A-tier issues (C1–C8) are reviewer-facing and should be closed before the paper draft. The pipeline architecture is sound and the tests pass their synthetic-truth checks; the bugs are at the integration boundary and in the experiment script, not in the core fitters.

**Do not enter Phase 3 (paper draft) on the current `e01_anchor_gpt2.tsv`.** Re-run E01 after D1–D5 are fixed, then re-evaluate.

*Word count: ~2480.*
