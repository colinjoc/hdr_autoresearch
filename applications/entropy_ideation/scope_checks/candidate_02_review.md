# Phase −0.5 Scope Check — Candidate 2

**Candidate.** Skip-connection topology sweep tunes distance-from-criticality. As `n_skip_connections` varies across the nanoGPT sweep (0 → 1000), do the branching ratio σ and avalanche exponent α vary monotonically or non-monotonically? Is there a topology setting that places the network closest to σ = 1?

**Verdict.** **REFRAME (PROCEED conditional on rebrand + inference rerun).** The experimental slot is publishable — *continuous topology interpolation on a trained transformer with criticality readouts* is a genuine gap — but the existing sweep is a **skip-density knob**, not a small-world or scale-free topology knob, and the saved pickles do **not** contain the per-token per-neuron binary masks required for CSN avalanche fits or MR branching-ratio estimation. The scope must be rewritten and an inference rerun executed on the saved `ckpt.pt` files before any criticality claim can be made.

---

## 1. Novelty

**Partial.** The *combination* (topology knob × trained transformer × Clauset-Shalizi-Newman / MR discipline) is genuinely untouched on arXiv through 2026-04. Adjacent hits:

- *Dimensional Criticality at Grokking Across MLPs and Transformers* (arXiv 2604.16431) uses TDU-OFC avalanche statistics on gradients at the grokking transition — avalanche methodology on transformers, but a different observable (gradient cascades, not activations) and no topology sweep.
- *Self-organized criticality on small-world networks* (Lahtinen et al.) studies branching on Watts-Strogatz rewirings — but on sandpile abstractions, not trained nets.
- *Statistical complexity is maximized in a small-world brain* (PLOS ONE) — brain, not ANN.
- Testolin 2020 / Scabini 2023 [3042, 3043] — weight-graph topology of trained DBNs / MLPs, no criticality observables, no continuous topology sweep, no transformers.

The closest prior art in the brain / ESN literature is Bertschinger-Natschläger 2004 [2041] (capacity peak at spectral radius = 1 on random reservoirs). That result *predicts* a capacity-peak-at-criticality curve for the candidate; the candidate's contribution is the first trained-transformer realisation of it.

**Concern (from the brief).** *Are random neuron-to-neuron skip connections a meaningful topology knob or a regularisation-strength knob?* This is the critical weakness. nanoGPT's `n_skip_connections` adds *extra* random forward edges on top of the full dense residual stream; it does not *rewire* (Watts-Strogatz) or *preferentially attach* (Barabási-Albert). The existing residual stream already provides a skip between every pair of blocks; adding 1 000 more random neuron-neuron edges to a 12 288-neuron graph (384 × 4 × 6 MLP neurons + 384 × 2 × 6 attention neurons ≈ 13 k) changes edge density by ~0.6 % relative to dense attention / MLP. Interpretation: this sweep varies **density of random bypass paths** through an already fully-residual network — closer to a sparse-augmentation / regularisation axis than a small-world / scale-free axis.

**Implication.** The candidate cannot be framed as "small-world topology tunes criticality" (the lit-review framing under [3033, 3034]). It must be framed as "*auxiliary random-bypass density* tunes effective-depth distribution and the resulting avalanche statistics." This is still novel — no one has done it — but the topology-vs-regularisation ambiguity must be acknowledged up front and disambiguated in controls (see §4).

**Novelty verdict.** Moderate. Publishable as workshop paper or short venue contribution; not a NeurIPS headliner unless paired with Candidate 1 (which supplies the baseline criticality measurement for the zero-skip anchor).

## 2. Falsifiability

The candidate's declared kill conditions are:

- σ(n_skip) flat (range < 0.1 across sweep), OR
- val-loss independent of |σ − 1| (|corr| < 0.3).

These are reasonable but the thresholds should be pre-registered *with uncertainty intervals*. Concretely:

- σ-range < 0.1 is meaningful only if the per-point σ CI is itself < 0.05 — otherwise "flat" is indistinguishable from "noisy". This requires the MR-estimator variance analysis in §5.
- Correlation < 0.3 on 11 sweep points has wide CI; a bootstrap or permutation test on the correlation is required.

**Additional falsifiers to pre-register:**

- CSN bootstrap p-value ≥ 0.05 at ≥ 2 sweep points (else no power law exists anywhere in the sweep and α(n_skip) is not definable).
- Threshold-plateau check at θ ∈ {0, 0.1} (both thresholds are already on disk, exploit them): if α shifts by > 0.5 between θ = 0 and θ = 0.1 at matched n_skip, the threshold-sensitivity pitfall fires and the claim is "α is threshold-conditional and cannot be reported without joint (n_skip, θ) reporting".
- Neutral-null rejection per Martinello 2017 [2040] / knowledge_base §5: Sethna scaling relation γ = (β − 1)/(α − 1) must hold at the best-fit-critical n_skip point. If it fails, the critical claim downgrades to "apparent criticality, Griffiths-like".

**Falsifiability verdict.** Adequate after the additions above. The candidate is intrinsically falsifiable because a flat sweep is a valid negative result.

## 3. Venue Fit

- **ICML ML4PS / NeurIPS ATTRIB / ICLR Blogposts-Track / MechInterp workshop** (positive): first continuous-topology-vs-criticality sweep on a trained transformer.
- **Entropy / Neural Computation** (positive): cross-disciplinary audience, tolerant of nanoGPT-scale models.
- **Complexity / Physical Review Research** (positive but only if paired with Candidate 1 baseline and full crackling-noise suite).
- **NeurIPS / ICML main conference**: unlikely alone. Pair with Candidates 1 + 12 as a combined paper "Criticality in trained transformers: a natural-experiment topology sweep with neutral-null rejection" — that package is main-track viable.

## 4. Required Controls

Mandatory, from knowledge_base §4–§5 and the topology-vs-regularisation ambiguity in §1:

1. **At-init baseline** for every n_skip. Required to separate training-induced drift from architectural effect.
2. **Threshold plateau.** The two saved thresholds (θ = 0, θ = 0.1) give the plateau minimum; add θ = 95th-percentile at rerun.
3. **MR estimator** (not naive branching ratio) for σ, with block-bootstrap over token blocks of length ≥ 10 to respect attention-induced autocorrelation.
4. **CSN power-law fit** via `powerlaw`, with explicit LLR rejection vs lognormal, truncated-power-law, exponential. Report KS, x_min, and bootstrap p-value.
5. **Crackling-noise scaling relation.** Measure α, β (duration), γ independently and test γ = (β − 1)/(α − 1) at each sweep point.
6. **Shape collapse** across avalanche durations at the best-fit-critical n_skip.
7. **Basis control.** Raw-neuron only is the minimum; add random-projection as a cheap second basis. SAE is out of scope for nanoGPT-sized models (no trained SAE available).
8. **Regularisation disambiguation (topology-vs-regularisation).** Pair every n_skip point with a matched random-weight-dropout point calibrated to the same parameter count / effective-depth. If (σ, α) track skip-density but not dropout-density, the "topology" framing survives. If they track dropout-density equally well, the knob is regularisation, not topology, and the paper must be re-titled accordingly. **This control is load-bearing** given the concern raised in the brief.
9. **Effective-depth distribution measurement.** Per Veit 2016, the prediction is that n_skip broadens the effective-depth distribution. Compute it directly (via gradient-norm-by-path-length, or via path-patching) and correlate with σ. This is what makes the topology framing coherent even if the dropout control complicates it.
10. **Seed replication.** Minimum 3 training seeds per n_skip for error bars on (σ, α, val-loss). The existing sweep is single-seed — this is the biggest gap.
11. **Val-loss correlation with |σ − 1|** must be reported with permutation-test p-value, not just Pearson r.

Controls 8 and 10 together are non-negotiable. Without them the novelty claim does not survive peer review.

## 5. Data Sufficiency — the load-bearing gap

The brief asks: *is the existing saved data sufficient, or does this need a substantial inference rerun?*

**The saved data is insufficient.** Inspection of `sweep_output_threshold_0/n_skip_connections_500/activation_analysis_.../activation_data_iter_000100.pkl` shows:

```
keys: ['iteration', 'activated_counts', 'activation_percentages', 'total_neurons',
       'train_loss', 'val_loss', 'layer_names', 'threshold', 'skip_connections',
       'skip_source_activations', 'skip_dest_activations', ...]
activated_counts: (1000,)       # aggregate counts, no per-token structure
activation_percentages: (1000,) # aggregate %, no per-token structure
total_neurons: 11520
```

These are **batch-aggregate per-layer activation percentages**. CSN avalanche-size fitting requires the per-sample, per-neuron binary activation tensor of shape `[n_tokens, n_layers, n_neurons_per_layer]` (plus skip-edge information) to extract cluster sizes and durations. The pickles do not contain this.

**What is saved that helps:** `ckpt.pt` is present for every sweep point. Model weights + skip-connection graph are fully reproducible. An inference rerun on a held-out evaluation corpus is straightforward.

**Minimum inference rerun specification:**

- **Token budget per sweep point.** Per knowledge_base §2.1, 2 decades of power-law scaling is the minimum bar. Cluster sizes span 1 to ~11 520 neurons → 4 decades of range, but the *tail* is what matters. For α ≈ 3/2, the tail density at s decays as s^{-1.5}; to get O(100) avalanches in the last decade requires O(100 × 10^1.5) ≈ 3 000 avalanches overall, and since mean avalanche rate per token is unknown a priori, a safe target is **10^5 tokens per sweep point** × 11 n_skip values × 2 thresholds × 3 seeds = 6.6 × 10^6 token forward passes. At batch 64, block 256 on an RTX 3060 this is ≈ 6.6 × 10^6 / (64 × 256) = 400 batches × ~1 s/batch = ~7 minutes per sweep point → ~4 hours per threshold × per seed → ~24 hours total for the full 3-seed × 2-threshold × 11-n_skip grid. Tractable.
- **Storage.** Per-token per-neuron binary masks at int8: 10^5 × 12 × 11 520 × 1 B = 13.8 GB per sweep point → ~150 GB per threshold per seed → ~900 GB total. This exceeds typical local disk. Mitigation: store per-token *event lists* (list of active (layer, neuron) pairs per token) at ~5 % sparsity → ~45 GB total, feasible.
- **MR estimator sample size.** Wilting-Priesemann 2018 [1015] recommend ≥ 10^4 events for unbiased σ with the MR estimator under subsampling. At ~5 % activation density × 11 520 neurons × 10^5 tokens = 5.8 × 10^7 activations — three orders of magnitude over the MR minimum. Sufficient.
- **CSN bootstrap.** 1 000 bootstrap resamples on 10^5-token data is ~minutes on CPU.

**Additional reruns for control 10 (seed replication).** Three seeds × 11 n_skip × 2 thresholds × ~20 min training per run (nanoGPT at max_iters=2000 on RTX 3060) = ~22 hours. The existing 22 runs already on disk are one seed's worth; two more seeds needed.

**Total inference + retrain time:** ~48 GPU-hours on RTX 3060. Fits in the declared 2-week budget.

## 6. Dependence Structure

- **Upstream dependency on Candidate 1.** Candidate 2 cannot stand alone: the zero-skip anchor point IS Candidate 1 on the nanoGPT architecture. If Candidate 1 reports no power law at n_skip = 0 (negative result), Candidate 2 has no reference point for "distance-from-criticality" — the entire sweep becomes a null-to-null comparison. **Run Candidate 1 first and use its pipeline for Candidate 2.** This is explicitly the intended bundle per candidate_ideas.md §Natural bundle.
- **Parallel dependency on Candidate 12.** Neutral-null rejection (Candidate 12) must be run at the best-fit-critical n_skip point of this sweep before any criticality claim. These are not optional.
- **Downstream.** Feeds Candidate 9 (dynamic-range test needs a tuned-criticality axis, which is exactly this sweep's output).
- **Independence from Candidates 3, 5, 7, 10.** Could in principle run alone, but the paper is weaker without the bundle.

## 7. Specific concerns from the brief

**Q1. Random neuron-to-neuron skip connections — meaningful topology knob or just sparse extra residual paths?** Latter. The existing residual stream already guarantees block-to-block skips; `n_skip_connections` adds *extra random forward neuron-to-neuron* edges on top. This is additive to an already dense graph, not a rewiring. It is closest to a *sparse auxiliary bypass density* axis, which is a genuine architectural variable but does not sit on the small-world / scale-free axis emphasised by [3033, 3034]. The framing in the candidate must be downgraded from "topology sweep" to "auxiliary-bypass density sweep" or equivalently "effective-depth distribution sweep (à la Veit 2016)". The experiment remains scientifically interesting but the lit-review cross-reference to small-world network theory is *not* a tight match.

**Q2. Has anyone on arXiv 2024–2026 published a topology-tunes-criticality experiment on a trained transformer?** No. The closest is arXiv 2604.16431 (Dimensional Criticality at Grokking Across MLPs and Transformers, 2026) which touches transformers + avalanches but not a topology sweep. The gap is real. Publication window is open.

**Q3. Minimum sample size / token count for stable σ and α estimates.** Per §5: 10^5 tokens per sweep point for α (CSN 2-decade fit); 10^4 events for σ (MR estimator). Existing aggregate data is insufficient; full inference rerun from saved `ckpt.pt` is required. Storage and compute budgets in §5 show this is feasible in ~48 GPU-hours.

## 8. Recommended reframing

**Title.** "Auxiliary-bypass density tunes effective depth and avalanche statistics in a trained transformer: a natural-experiment sweep on nanoGPT."

**Claim (post-reframe).** Not "topology tunes criticality". Rather: "Varying the density of random auxiliary skip edges shifts the effective-depth distribution and thereby the branching ratio of residual-stream activations; the shift is monotonic (or non-monotonic — preregistered both-ways) in skip density; val-loss correlates with |σ − 1|; and the dropout-density matched control distinguishes topology effect from regularisation effect."

**Deliverable.** Workshop paper as lead author; main-conference if bundled with Candidates 1 and 12.

## 9. Verdict

**REFRAME → PROCEED.** The experimental slot is real and publishable. The candidate as currently written over-claims on the "topology" framing and under-specifies the data-regeneration requirement. Required changes before promotion:

1. Rewrite as auxiliary-bypass density / effective-depth sweep, not small-world topology sweep.
2. Add dropout-density matched control (control 8).
3. Add 3-seed replication (control 10).
4. Budget the ~48-hour inference + retrain rerun; do not rely on saved aggregate pickles.
5. Bundle with Candidate 1 (baseline) and Candidate 12 (neutral null) as one coherent paper.

One-line justification: *Experimental niche is genuine and feasible in budget, but the lit-review framing is mismatched (extra random edges ≠ small-world rewiring) and the saved data is aggregate-only so CSN/MR analyses require a full inference rerun from saved checkpoints.*

---

### Source URLs (arXiv/web, accessed 2026-04-21)

- Dimensional Criticality at Grokking Across MLPs and Transformers (arXiv 2604.16431)
- Hidden Dynamics of Massive Activations in Transformer Training (arXiv 2508.03616)
- Avalanches and edge-of-chaos learning in neuromorphic nanowire networks (Nat. Commun. 2021)
- Statistical complexity is maximized in a small-world brain (PLOS ONE)
- Self-organized criticality on small-world networks (Lahtinen et al.)
