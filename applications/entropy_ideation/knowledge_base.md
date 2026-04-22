# Knowledge Base — Criticality in Trained Neural Networks

Cross-domain synthesis of what works, what fails, and what constitutes acceptable evidence. This is the working reference for candidate-idea design and for Phase −0.5 scope-checks.

## 1. The criticality hypothesis in one paragraph

A dynamical system is *critical* when activity propagates via a marginal-branching process: each active unit at one time step (or depth) activates, on average, one child at the next. At criticality, three signatures co-occur: (a) avalanche-size distribution follows `P(s) ∝ s^{-α}` with `α ≈ 3/2` for mean-field / directed-percolation dynamics; (b) branching ratio `σ ≈ 1`; (c) the crackling-noise scaling relation `γ = (β − 1)/(α − 1)` holds, where β is the avalanche-duration exponent and γ is the mean-size-given-duration exponent. Subcritical systems damp; supercritical systems saturate; critical systems maximise dynamic range, memory capacity, and mutual-information transfer.

The *critical brain hypothesis* claims biological cortex self-organises to this regime. The *edge-of-chaos hypothesis* for neural networks claims artificial networks either need to be initialised there for trainability (well-established) or benefit from remaining near this boundary during training (open).

## 2. The canonical observables and how to compute them

### 2.1 Avalanche-size distribution `P(s)`
- **Define an event.** For continuous activations, threshold at `θ`; an event is activation > θ. For transformers, threshold choice is non-trivial: `θ = 0` captures anything post-nonlinearity; `θ = percentile-based` controls for baseline sparsity.
- **Define an avalanche.** Contiguous time / layer regions of non-zero events separated by quiescent (all-below-threshold) intervals. In time: the avalanche ends when no unit fires in a given bin. In depth: the avalanche starts at layer ℓ with k seed activations and ends at the layer where the cascade has fully died.
- **Fit the power law.** Use `powerlaw` Python package [3: Alstott-Bullmore-Plenz 2014]. Report `x_min` (the lower cutoff), `α`, KS statistic, bootstrap p-value for power-law goodness-of-fit, and log-likelihood ratios vs lognormal / truncated power-law / exponential alternatives.
- **Minimum acceptable scaling range**: 2 decades. Three is better. One decade cannot distinguish power law from lognormal [2038: Clauset 2009].

### 2.2 Branching ratio `σ`
- **Naive estimator**: σ = ⟨events at t+1 | events at t⟩ / events at t. Systematically under-estimates σ under subsampling [1014].
- **MR estimator** [1015: Wilting-Priesemann 2018]: fits the exponential decay of the autocorrelation function of activity, recovers unbiased σ even from severely subsampled data. Python implementation: `mrestimator`.
- **For deep networks**: use layer-resolved σ_ℓ = ⟨activations at ℓ+1 triggered by activations at ℓ⟩. This is a causal probe (which downstream activations are caused by each upstream one) — done via single-unit ablation or activation patching.

### 2.3 Crackling-noise cross-check
- Measure `α` (size), `β` (duration), `γ` (mean-size-given-duration) independently.
- Test `γ = (β − 1)/(α − 1)` within bootstrap confidence intervals.
- Any criticality claim without this cross-check is incomplete [2031: Sethna 2001].

### 2.4 Shape collapse
- For each duration T, compute mean avalanche profile `s(t, T)`.
- If critical, `s(t, T) = T^{γ−1} F(t/T)` for a universal scaling function F.
- Plot collapsed curves; visual pass/fail is informative [2032: Papanikolaou 2011].

### 2.5 Lyapunov / sensitivity
- **Jacobian spectral radius**: at each layer, compute the spectral radius of the Jacobian of post-activation w.r.t. pre-activation. Mean-field prediction: ρ = 1 at criticality [3039: Pilarski 2023 VERIFY].
- **Perturbation-based**: perturb an input or intermediate activation by ε; measure ‖Δoutput‖ at subsequent layers. Log-slope = Lyapunov-like exponent.
- **Semantically-conditioned**: perturb along a known mechanistically-important direction (residual-stream write of a specific circuit feature from [3025: Wang 2023]) rather than random.

### 2.6 Dynamic range
- Sweep input magnitude / prompt difficulty; measure ratio of max output response to threshold response.
- Kinouchi-Copelli prediction [1022]: dynamic range maximised at criticality.
- In LLMs: perplexity vs input-perturbation magnitude, or capability-metric vs intermediate-activation-perturbation magnitude.

## 3. Transformer-specific methodological notes

### 3.1 Basis choice
Raw-neuron activations, random-projection, PCA, and SAE-feature representations of the same residual stream or MLP output can give different avalanche statistics. **Mandatory to report results in at least two bases** — typically raw-neuron + SAE-feature. Basis-sensitivity is itself a publishable observation.

### 3.2 Temporal structure
- **Token axis**: each token's activation is one observation. Autocorrelated across tokens (attention produces correlations over the context).
- **Layer axis**: each layer's activation is another observation. Highly correlated across layers via residual stream.
- **Batch axis**: across batches / prompts is the "i.i.d." axis if prompts are independent.

Decide which axis defines the avalanche. Neuroscience convention: time. ML convention for transformers: layer or batch. Report multiple choices.

### 3.3 Causal vs correlational connectivity
Two neurons co-firing on the same inputs is a *correlational* co-activation. The true branching-ratio computation requires **causal**: if unit A is activated by ablation / patching, does unit B subsequently activate? Activation patching [3027: Meng 2022 ROME] is the gold-standard tool.

## 4. Known pitfalls, by provenance

### From neuroscience
- Subsampling under-estimates σ. Use MR estimator.
- Log-log eyeballing finds power laws in everything. Use CSN bootstrap.
- α ≈ 3/2 alone is compatible with Griffiths phases and neutral null models. Use scaling relation + shape collapse.

### From complex systems
- Power-law vs lognormal requires ≥2 decades and CSN likelihood-ratio test.
- Sethna scaling relation is the multi-exponent universality check.
- Griffiths phases produce broad apparent-criticality regimes without a tuning parameter.
- Block-bootstrap on autocorrelated time series.

### From ML theory
- At-init edge of chaos is well-characterised for vanilla MLPs and CNNs; trained networks drift.
- Residual networks bypass the init-criticality constraint; analysis needs re-derivation per architecture.
- Extreme activation sparsity in LLMs changes the effective branching denominator.
- NTK vs feature-learning distinction matters: linearised analysis on feature-learning nets gives wrong verdicts.
- Small-model results do not automatically transfer to LLM scale — but full LLM training is infeasible on one GPU, so pretrained large nets + small-model ablations is the only feasible path.

### Cross-cutting
- Threshold sensitivity of avalanche statistics: exponents must plateau across reasonable threshold range or the claim fails.
- At-init control is mandatory for any trained-network criticality claim.
- Neutral null rejection is mandatory.

## 5. Minimum evidence bar for a positive criticality claim

Before claiming a trained network is at criticality, a paper must show:

1. `P(s) ∝ s^{-α}` fit via `powerlaw` package. Report `x_min`, KS statistic, bootstrap p-value ≥ 0.05 for power-law, and explicit log-likelihood ratios rejecting lognormal / truncated power-law / exponential.
2. `α ≈ 3/2` within 95 % confidence interval (for mean-field / DP expected class).
3. `β`, `γ` independently measured, and `γ = (β − 1)/(α − 1)` within bootstrap error.
4. Shape collapse figure passes eyeball test.
5. σ = 1 ± 0.02 via the MR estimator on at least two axes (time / layer / batch).
6. Threshold plateau: exponents stable within reported CI across at least [θ × 0.5, θ × 2].
7. At-init control showing different (off-critical) exponents — demonstrates the criticality is a consequence of training, not initialisation.
8. Neutral-null rejection: either via the Sethna scaling relation, or by showing criticality observables correlate with task-relevant metrics (loss, accuracy, capability probes) that a neutral null could not predict.

If seven of eight are positive the paper is publishable as "evidence consistent with critical dynamics". If the scaling relation fails it is "critical-like but not critical"; if σ ≠ 1 it is off-critical; if no power law is found at any threshold it is a negative result — itself publishable.

## 6. Tooling available today

- **`powerlaw` (Python)**: CSN fitting + bootstrap + alternatives [3: Alstott-Bullmore-Plenz 2014]
- **`mrestimator`**: MR branching-ratio estimator [1015]
- **`TransformerLens` / `nnsight`**: activation caching + patching on pretrained LLMs
- **`SAE Lens`, `Gemma-Scope` public weights**: SAE feature extraction for basis-invariance study
- **`einops` + PyTorch hooks**: custom activation logging at any layer
- **`PyMC` / `emcee`**: Bayesian fits for avalanche exponents with proper uncertainty
- **existing `~/entropy/nanoGPT/ActivationAnalyzer`**: per-layer activation fraction at threshold — extends naturally to avalanche detection

## 7. What would kill each candidate thesis

- *"Trained transformers are at criticality"* — killed if (i) no power law across bases and thresholds; or (ii) `α` consistent with at-init value, so training does not tune it; or (iii) scaling relation fails.
- *"Skip-connection count tunes distance-from-criticality"* — killed if (i) `σ(n_skip)` is flat across the sweep; or (ii) task performance does not track `|σ − 1|`.
- *"Criticality predicts LLM capability"* — killed if capability-metric residual after controlling for model size is independent of criticality observables.
- *"Induction-head emergence is a phase transition"* — killed if progress-measure trajectory is smooth in all criticality observables through the emergence kink.
- *"SAE features show different criticality than raw neurons"* — killed if basis-invariance holds within CI.

## 8. How this feeds candidate ideas

The candidate-ideas document should propose concrete experiments where the observable bar and kill condition are both explicit. Every candidate must declare: (a) which criticality observable it measures, (b) on which model(s) and in which basis, (c) what the pre-registered kill threshold is, (d) which of the above pitfalls it explicitly controls for.
