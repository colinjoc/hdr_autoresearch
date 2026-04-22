# Phase -0.5 Scope-Check - Candidate 24

**Candidate.** 1/f power spectrum of residual-stream activations. Test S(f) proportional to 1/f^beta with beta near 1 on GPT-2 / Pythia / Gemma activations. Reference: [2001: Bak-Tang-Wiesenfeld 1987] canonical SOC signature.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME.** The question - does the activation PSD of a trained transformer exhibit 1/f^beta scaling - is untouched on the 2024-2026 arXiv surface for *transformer* LLMs in the form proposed (per-neuron residual-stream PSD, multiple model families, statistically rigorous exponent fitting). But the candidate as written has three solvable methodological hazards and one novelty pressure from one prior paper: **arXiv:2301.08530 (Nguyen, Hu, Yen 2023) "Self-Organization Towards 1/f Noise in Deep Neural Networks"** already reports 1/f neuron-activation noise *in LSTMs on IMDb* via DFA, with 1/f claimed as a signature of optimal-capacity learning. Candidate 24 must (a) cite 2301.08530 as the primary precedent rather than invent novelty against it; (b) reframe as "extension from LSTM DFA to transformer direct PSD, across multiple families, with aperiodic-component decomposition"; (c) resolve the non-stationarity of autoregressive generation head-on; (d) bundle with Candidate 23 (DFA) as a single two-observable paper, since the observables are the Fourier pair of the same underlying long-range-correlation claim.

With those four fixes this is a ~2-week inference-only study suitable for *Entropy* or as a section of Paper 1 anchor.

## 2. 2024-2026 arXiv landscape: what exists, what does not

**Direct precedent, missed by the candidate.** arXiv:2301.08530 (Nguyen-Hu-Yen, Jan 2023) trains LSTMs on IMDb, runs DFA on internal / external neuron activation time series, reports 1/f noise in the trained network degrading to white noise when over-capacity. Methodology is DFA, not PSD - which is why Candidates 23 and 24 must be planned jointly. For C23, 2301.08530 is *the* LSTM precedent and the transformer case is open. For C24, 2301.08530 measures 1/f via DFA; direct Welch / multitaper PSD on transformer residual streams, with rigorous exponent fitting, has not been published as far as this review's search extends.

**Transformer-activation work adjacent but non-overlapping.** arXiv:2502.12131 (Transformer Dynamics, Feb 2025) analyses Llama-3.1-8B residual streams via correlation, cosine similarity, velocity, mutual information, phase-space portraits - *no* PSD, no 1/f, no Fourier analysis. It explicitly frames activations as non-stationary across layers, a direct headwind for Welch-style spectral estimation on the layer axis (but not on the token axis; see Section 4). arXiv:2409.17113 (Characterizing stable regions) covers GPT, Pythia, Phi, Llama and flags **Gemma as behaving differently** - a methodology warning: do not average across families blind. arXiv:2512.18209 (When Does Learning Renormalize?) gives a power-law spectral-dynamics framework for *loss / gradient* spectra, not activations.

**Neuroscience reference work missing from `papers.csv`.** Linkenkaer-Hansen 2001 [1023] and Meisel 2017 [1032] are present; Bak-Tang-Wiesenfeld 1987 is in as 1024/2001. Missing: **FOOOF** (Donoghue et al. 2020, Nat Neurosci) which decomposes a neural PSD into aperiodic 1/f^beta and periodic peaks and is field-canonical for robust 1/f-exponent estimation. Add the FOOOF citation and use the tool.

**Verdict on novelty.** Narrow but real. Not a first measurement of 1/f in a trained neural-network activation time series (Nguyen-Hu-Yen 2023 did LSTMs). It *is* the first direct-PSD, multi-family, multi-basis study on residual streams of modern pretrained transformers.

## 3. Relation to Candidate 23 (DFA): complementary, not redundant - but not independent

The candidate claims "complementary to both avalanche size and DFA". Only half right.

**Mathematical fact.** For a stationary Gaussian process, DFA exponent alpha_DFA and PSD slope beta are rigidly related: **beta = 2 alpha_DFA - 1** (Kantelhardt et al. 2001; Heneghan-McDarby 2000). Under stationarity, DFA alpha = 1 *is equivalent to* PSD beta = 1. They are not independent observables.

**Where they diverge.** The rigid relation breaks under (a) non-stationarity, (b) heavy-tailed increments, (c) oscillatory contamination. DFA is more robust to non-stationary trends (hence "detrended"); PSD is more interpretable for peaks. The useful complementarity is *exactly* non-stationarity diagnosis: if alpha_DFA and beta disagree beyond bootstrap CI, that disagreement is the interesting signal on LLM activations.

**Recommendation.** Merge C23 and C24 into one two-observable paper. Pre-register (i) both estimators on the same cached activations, (ii) the consistency check beta = 2 alpha_DFA - 1, (iii) disagreement flagged as non-stationarity evidence. This is the load-bearing novelty beyond 2301.08530.

## 4. Does PSD require stationary ergodic time series? Yes - and LLM inference violates it

**Statistical fact.** Welch's method assumes wide-sense-stationary (WSS); multitaper (Thomson 1982) formally requires the same. Non-stationary processes have time-varying spectra; a single averaged periodogram is a biased estimator of the true spectrum averaged over time, and the 1/f^beta slope recovered is not a property of the underlying process unless it is stationary.

**Does autoregressive LLM generation violate WSS?** Axis- and conditioning-dependent.

- **Token axis within a single free-form generation:** non-stationary - the distribution of residual activations at token t depends on context to t-1 and drifts as the generation develops a topic.
- **Token axis conditioned on a fixed corpus, ensemble-averaged across prompts:** approximately WSS if prompts are i.i.d. from a stationary text distribution (Pile, FineWeb) and each per-prompt series is one realisation. *This is the correct estimator.*
- **Layer axis:** explicitly non-stationary (2502.12131 documents this). Do not run PSD on the layer axis.
- **Neuron / feature axis:** not a time series; not what C24 is about.

**Resolvable via design.** Pre-register: token axis within prompt, ensemble-averaged over >=1000 prompts drawn i.i.d. from a reference corpus, context >=1024 tokens for >=2 decades of frequency resolution. Stationarity empirically checked via (i) split-half reverse-arrangement, (ii) first-half vs second-half PSD, (iii) per-prompt variance vs ensemble bias. Fallback if these fail: time-frequency methods (Wavelet, Hilbert-Huang) that do not require WSS, with the result framed as "time-averaged 1/f slope on non-stationary autoregressive activations" with the caveat in the abstract.

**Ergodicity.** Separate from stationarity. LLM generation is *not* ergodic under temperature-1.0 sampling: repeated generations from the same prompt diverge. Ensemble over independent prompts (the design above) is the fix.

## 5. Is Welch / multitaper enough?

**Welch.** Standard, fast, biased at low frequencies by window length, smears peaks. Adequate for a gross slope estimate; inadequate for peak-vs-aperiodic separation.

**Multitaper (Thomson 1982).** Lower variance, better frequency resolution, weighted-eigenspectra combination. Preferred for the main result.

**FOOOF (Donoghue 2020).** Field-canonical for decomposing a PSD into aperiodic 1/f^beta and periodic Gaussian peaks. *Required* for a clean 1/f-exponent robust to any attention-induced oscillatory structure. Add FOOOF alongside multitaper.

**Power-law goodness-of-fit.** The candidate proposes "CSN-style goodness-of-fit for power-law spectra". Non-trivial: Clauset-Shalizi-Newman 2009 is for discrete-event counts, not PSD slopes. The right tool for PSD is weighted log-log regression with chi-square heteroscedasticity, plus model comparison against broken-power-law, bent-power-law, and Lorentzian (knee + 1/f^2 tail) alternatives via AIC / BIC. **Do not apply the `powerlaw` package naively to PSD values**; use `fooof` / `specparam` for the aperiodic fit and its CI.

**Minimum pipeline.** Welch (reader's sanity check) + multitaper (main result) + FOOOF (periodic-aperiodic decomposition) + broken-power-law vs single-power-law model comparison + block-bootstrap across prompts for CIs + at-init baseline + shuffled-token surrogate (destroys temporal correlations, should yield white PSD; if not, methodology bug).

## 6. Rubric and action items

**Rubric.** D = 5 (public weights, public corpora, inference-only). N = 2 standalone, 2301.08530 is unavoidable / N = 3 as C23+C24 bundle with the beta = 2 alpha_DFA - 1 consistency check as the new contribution. F = 4 (pre-registered null: beta outside [0.8, 1.2]; >=2 decades; threshold / basis plateau). C = 5 (~1-2 weeks, ~100 GPU-hours). P = 3 (*Entropy* methodology paper, or section of Paper 1 anchor).

**Composite:** PROCEED as **merged C23 + C24 bundle** - one paper, two observables, with the beta = 2 alpha_DFA - 1 consistency check as the load-bearing contribution beyond 2301.08530.

**Action items.**
1. In `candidate_ideas.md` Candidate 24, add arXiv:2301.08530 as acknowledged precedent; strike "no ML paper has measured it on trained transformer activations". Correct claim: "no ML paper has measured 1/f directly via PSD on residual-stream activations of modern pretrained transformers with rigorous goodness-of-fit".
2. Add FOOOF / `specparam` (Donoghue 2020) to `papers.csv` and `knowledge_base.md` Section 6 tooling as the canonical aperiodic-exponent estimator.
3. Merge Candidates 23 and 24 in `promoted.md` into one two-observable sub-paper; pre-register beta = 2 alpha_DFA - 1 consistency as the flagship test.
4. Pin the axis: token axis within prompt, ensemble over >=1000 prompts, context >=1024. Do not run PSD on the layer axis.
5. Pre-register stationarity diagnostics (split-half reverse-arrangement; first-half vs second-half PSD; per-prompt variance vs ensemble bias) and the time-frequency fallback.
6. Report Gemma in its own subsection per arXiv:2409.17113 (Gemma differs from GPT / Pythia / Phi / Llama in residual structure); do not average across families blind.
7. Replace "CSN-style goodness-of-fit" with "multitaper PSD + FOOOF aperiodic fit + AIC / BIC vs broken-power-law, bent-power-law, Lorentzian + block-bootstrap CI". `powerlaw` is wrong for PSD values.
8. Cite Bak-Tang-Wiesenfeld 1987 for SOC framing but acknowledge the knowledge-base caveat: 1/f alone is compatible with Griffiths phases, neutral nulls, and slow-latent-variable artefacts [1039: Morrell-Sederberg-Nemenman 2023]. A 1/f positive is necessary-not-sufficient and must be paired with avalanche-exponent or branching-ratio evidence from Paper 1.
