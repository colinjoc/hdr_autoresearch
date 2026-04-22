# Landscape Literature Review: Criticality and Edge-of-Chaos in Trained Neural Networks

Scope: 2026-04 landscape scan supporting ideation for simulation-feasible, single-GPU research projects probing whether trained neural networks operate near self-organized criticality / edge of chaos, and how network topology (skip connections, sparsity, effective depth) tunes distance-from-criticality. **140 verified citations** in `papers.csv` — 40 neuroscience (IDs 1001–1040), 45 complex systems (IDs 2001–2045), 55 AI/ML (IDs 3001–3055). Individual domain reviews live in `lit_neuro.md`, `lit_complex.md`, `lit_ml.md`; this file is the index, the synthesis, and the gap statement the candidate ideas will target.

---

## Domain index

| File | Word count | Citations | Themes |
|---|---:|---:|---|
| `lit_neuro.md` | ~4 300 | 40 (1001–1040) | Cortical avalanches • branching-ratio + subsampling • dynamic range • contested-criticality critiques • pharmacological / developmental / clinical signatures • methodology |
| `lit_complex.md` | ~11 800 | 45 (2001–2045) | SOC (sandpile, Oslo, Bak-Sneppen) • absorbing-state / directed-percolation • branching processes • crackling noise • Langton edge of chaos • Sompolinsky random-RNN chaos • reservoir computing • power-law fitting methodology • Griffiths phases and quasi-criticality |
| `lit_ml.md` | ~10 300 | 55 (3001–3055) | Signal-propagation mean-field init EOC • NTK / infinite-width • grokking / edge-of-stability / scaling laws • mechanistic interpretability (SAE, circuits, induction heads) • superposition and feature geometry • activation sparsity • network-topology analyses of trained nets • criticality in deep/recurrent nets • Lyapunov / Jacobian proxies • LLM activation-analysis methodology |

The three reviews deliberately overlap on methodology: all three identify Clauset-Shalizi-Newman goodness-of-fit as the minimum bar for any power-law claim, Priesemann MR estimator as the minimum bar for any branching-ratio claim, and the crackling-noise scaling relation as the minimum bar for any universality-class claim.

---

## Synthesis — what the three fields agree on

Three conditions characterise a system at critical dynamics, and all three fields converge on them:

**1. Avalanche-size distribution follows a power law `P(s) ∝ s^{-α}`** with a specific mean-field exponent α ≈ 3/2 for generic absorbing-state / directed-percolation / branching-process dynamics. This is measured in cortical slices [1001: Beggs & Plenz 2003], in sandpile models [2001: Bak 1987], in random-recurrent-network mean-field theory [2021: Sompolinsky 1988], and has never been measured on trained transformer activations [lit_ml §9 gap].

**2. Branching ratio σ ≈ 1.** For each activated unit at time t (or layer ℓ), the mean number of activated children at t+1 (or ℓ+1) equals one. σ < 1 is subcritical (activity dies out); σ > 1 is supercritical (activity explodes); σ = 1 sits on the phase boundary. In the brain literature this is the most diagnostically reliable single observable under subsampling correction [1015: Wilting & Priesemann 2018]. In deep-network theory, σ = 1 is the same condition as the Jacobian spectral radius = 1 that characterises the Sompolinsky edge-of-chaos for random recurrent networks and the Schoenholz edge-of-chaos for deep feedforward networks.

**3. Crackling-noise scaling relation.** The three exponents from avalanche size `α`, avalanche duration `β`, and mean-size-given-duration `γ` satisfy `γ = (β − 1)/(α − 1)` in a critical system [2031: Sethna, Dahmen & Myers 2001]. This three-way cross-check rules out many power-law-mimicking non-critical mechanisms (lognormal truncation, Griffiths phases in broad parameter regimes, neutral null models) that can look like α ≈ 3/2 individually.

**Computational capacity peaks at criticality.** This is the Langton / Bertschinger-Natschläger / Boedecker result [2041–2043] and is the motivating link from physics observables to learning-relevant properties. Random reservoir networks have maximum memory capacity and maximum mutual-information transfer at the spectral-radius-one boundary. Edge-of-chaos init enables trainable deep networks without skip connections [3001: Poole 2016, 3002: Schoenholz 2017]. Whether trained (not just at-init) deep networks remain near this boundary is open.

## Synthesis — the open gap the ideation targets

The ML review [lit_ml §Gap] identifies the specific empirical niche that is untouched:

> **No published paper computes avalanche-size distributions, branching ratios, or power-law cluster exponents on the activation time-series of trained transformer language models (GPT-2 or larger), nor cross-references such observables with mechanistic-interpretability primitives (residual-stream components, SAE features) or with topology knobs (skip-connection count, effective depth).**

Adjacent work exists — RNN criticality [3042–3044], weight-graph topology of DBNs and MLPs [3032–3034], Jacobian-spectrum Lyapunov proxies for feedforward nets [3039], activation-sparsity characterisations [3020–3023] — but none combines the rigorous statistical-physics exponent discipline (Clauset-Shalizi-Newman fit + crackling-noise cross-check + shape collapse + threshold plateau + MR branching-ratio estimator) with transformer-specific activation analysis and mechanistic-interpretability primitives.

The existing `~/entropy/` infrastructure already covers the experimental axis: a nanoGPT variant with a continuously tunable `n_skip_connections` knob, an ActivationAnalyzer recording per-layer activation fractions, a sweep across 0–1000 skip connections at two thresholds, and parallel pretrained-GPT-2 and CNN analysers. What's missing is the criticality-statistics pipeline and the mechanistic-interpretability integration.

## Synthesis — pitfalls that any project must handle

From the three reviews, the following pitfalls are not optional:

1. **Power-law fitting without Clauset-Shalizi-Newman bootstrap and alternative-distribution rejection.** Log-log eyeballing produces publishable-looking power laws from lognormal, truncated exponential, and Griffiths-phase data. The `powerlaw` Python package [1031: Alstott-Bullmore-Plenz 2014] implements the full CSN pipeline and is the minimum bar.

2. **Single-exponent claims without crackling-noise cross-check.** α ≈ 3/2 alone does not establish criticality — it is compatible with Griffiths phases, neutral null models, and several non-critical universality classes [2033: Muñoz 2018; 2040: Martinello 2017]. The `γ = (β − 1)/(α − 1)` scaling relation plus avalanche-shape collapse [2032: Papanikolaou 2011] is the multi-line test.

3. **Naive branching-ratio estimation.** Partial observation systematically under-estimates σ. The MR estimator [1014: Priesemann 2013, 1015: Wilting & Priesemann 2018] is required for any σ claim on subsampled (i.e. any realistic) activation data.

4. **Ignoring autocorrelation in bootstrap.** LLM activations are autoregressive; naive i.i.d. bootstrap over-narrows confidence intervals. Block-bootstrap over token or batch dimensions is required.

5. **Basis choice confounding.** Raw-neuron, random-projection, PCA, and SAE-feature representations of the same activation can give different exponents. Report all bases or explicitly justify one; the basis-sensitivity study is itself publishable.

6. **Threshold sensitivity.** The activation-threshold choice (0, 0.1, percentile-based) flips avalanche distributions between power-law and exponential in many published neuroscience datasets [1029: Deluca & Corral 2013]. Mandatory: a threshold plateau test showing exponents stable across a reasonable range.

7. **Init-vs-trained confusion.** Mean-field EOC at initialisation is well-understood [3001: Poole, 3002: Schoenholz, 3003: Xiao]; trained networks drift, and the direction of drift (toward, away from, or past the init boundary) is not known. Any project reporting criticality observables on trained networks MUST report the at-init control, and ideally a sweep through training steps.

8. **Neutral-model null.** A published-by-neutral-model Griffiths-phase distribution can produce the same α ≈ 3/2 without any phase transition [2040: Martinello 2017]. Explicit rejection of the neutral null (via the scaling relation or via task-performance correlation) is mandatory.

---

## Consolidated stylised facts across the three fields

**Robustly known:**
- Cortical avalanches reproducibly show α ≈ 3/2, β ≈ 2 across slice, culture, and awake in vivo [1001–1005].
- The crackling-noise relation γ = (β−1)/(α−1) is empirically satisfied in cortical data [1006: Friedman 2012], giving multi-exponent support.
- Branching ratio σ ≈ 1 (±correction) is a robust neural signature of criticality [1015: Wilting-Priesemann 2018].
- Random recurrent networks with Gaussian weights have a chaotic transition at g = 1 computable from dynamical mean-field theory [2021: Sompolinsky 1988].
- Random reservoirs peak in computational / memory capacity near spectral radius 1 [2041: Bertschinger 2004, 2042: Boedecker 2012].
- Deep feedforward nets at σ_w², σ_b² tuned to χ_1 = 1 can be trained at depth 10⁴; off-critical init cannot [3002: Schoenholz 2017, 3003: Xiao 2018].
- Trained LLMs show extreme activation sparsity: 75–90 % of MLP neurons inactive per token [3020: Li 2023]; contextual sparsity is predictable [3021: Liu 2023].
- Training exhibits real phase transitions: grokking [3010: Power 2022], induction-head emergence [3018: Olsson 2022], superposition phase boundaries [3029: Elhage 2022].
- Test loss scales as a smooth power law over >5 orders of magnitude in data/parameters/compute [3013: Kaplan 2020, 3014: Hoffmann 2022].
- Trained networks use sparse functional circuits: IOI uses 26 of 144 GPT-2 heads [3025: Wang 2023]; knowledge neurons and universal neurons are a small fraction.
- Weight-graph topology of some trained architectures is approximately scale-free [3033: Testolin 2020, 3034: Scabini 2023].

**Contested:**
- Whether cortex is *at* criticality or *slightly subcritical* ("reverberating regime", σ ≈ 0.98) [1004: Ma 2019].
- Whether the apparent neural universality is genuine mean-field DP or a Griffiths phase [2040: Martinello 2017, 2039: di Santo 2018].
- Whether trained deep networks drift toward, away from, or past the init edge of chaos. Mean-field theory is silent on trained dynamics.
- Whether capability emergence reflects a phase transition in internal structure or a metric-discontinuity artefact [3016: Schaeffer 2023 vs 3015: Wei 2022].
- Whether NTK / linearisation or feature-learning better describes finite-width trained LLMs.

**Methodologically fragile:**
- Exponent estimates from <2–3 decades of scaling cannot distinguish power-law from lognormal [2038: Clauset 2009].
- Activation threshold (0 vs 0.1 vs percentile) can flip a trained-network avalanche distribution from power-law to exponential.
- Subsampling bias in branching-ratio estimation [1015].
- i.i.d. bootstrap on autocorrelated LLM activations; block-bootstrap is required.
- Confusing correlation-based co-firing with causal functional connectivity (activation patching is gold-standard for the latter).
- NTK vs feature-learning regime misdiagnosis on trained LLMs.

---

## Pointer to candidate ideas

Ten to fifteen concrete research proposals flowing from this gap are in `candidate_ideas.md`. Each will go through a Phase −0.5 scope-check by a fresh sub-agent against this review before promotion to its own `applications/entropy_<slug>/` project.
