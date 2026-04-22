# Phase -0.5 Scope-Check - Candidate 30

**Candidate.** Hallucination rate vs σ. Hypothesis: hallucinations occur more when the model is locally super-critical. Test on TruthfulQA / HalluQA / FEVER-contradicting, on Gemma-2-2B and Pythia-1.4B; per-prompt regression of accuracy against |σ − 1|.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME leaning PROCEED, as a workshop-track arm of a consolidated applied-criticality paper, *not* a standalone main-conference submission.** The observable-type novelty (σ as hallucination predictor) is real, but activation-statistics hallucination probes are a crowded 2024-26 subfield, per-prompt MR-σ on ~100-token prompts is at or past the estimator's reliability floor, the supercritical-→-hallucination direction is ambiguous between two distinct mechanistic stories, and confound structure is unusually severe (knowledge-frequency, length, base-vs-instruct, judge error, overconfident-hallucination regime). Proceed after an MR-estimator short-sequence pilot, a Ji-2024 probing-baseline head-to-head, and bundling with C26 / C31 / C32 / C33 into a single Paper 8 (applied criticality).

## 2. Prior art on activation-based hallucination prediction (concern a)

Activation-statistics hallucination detection is saturated in 2024-26. Papers the candidate text does not cite:

- **arXiv:2407.03282 Ji et al. 2024** (BlackBoxNLP). Probing estimator on internal states predicts hallucination risk at 84 % accuracy across 15 NLG tasks / 700+ datasets. The obvious competitive baseline.
- **arXiv:2402.03744 INSIDE (ICLR 2024).** EigenScore on covariance matrix of internal embeddings + feature-clipping. Already a covariance-eigenvalue observable — same mathematical object feeding MR's autocorrelation-based σ.
- **arXiv:2411.04847 PRISM 2024** — prompt-guided internal-state probes.
- **arXiv:2512.01797 H-Neurons Dec 2025 (Tsinghua).** <0.1 % of neurons predict hallucination; trace to pre-training. Scoops "sparse activation signature predicts hallucination".
- **arXiv:2406.15927 Kossen 2024** — semantic entropy probes.
- **arXiv:2509.09715 Sept 2025** — Gemma-2-2B/9B/27B on HaluEval + TruthfulQA; **input-length dependence peaks at 10-30 tokens** — direct evidence the length confound is first-order.
- **arXiv:2508.14496 "Semantic Energy" 2025** — statistical-mechanics framing for hallucination beyond token entropy. Closest thematic precedent to "physics observable predicts hallucination".
- **arXiv:2601.20026 "QTN" 2026** — hallucination as local perturbation sensitivity (Lyapunov-like).
- **arXiv:2602.17691 "Tethered Reasoning" 2026** — decouples entropy from hallucination via manifold steering; articulates the sensitivity axis the supercritical story assumes.

**No 2024-26 paper uses MR σ, an avalanche exponent, or crackling-noise exponents for hallucination prediction.** The gap is narrow: "physics observable" is not a novelty claim when activation-statistics predictors already exist. Headline novelty survives only if σ adds information EigenScore and Ji's probe do not capture — this is the bar.

## 3. Per-prompt σ on short prompts (concern b)

**Probably not reliably estimable at T ≈ 100.** Spitzner et al. 2020 (arXiv:2007.03367, the MR-estimator reference) documents that correlation coefficients are biased for short trials; the `stationarymean` compensation requires many trials over which activity is stationary. Pooling prompts to fix one prompt's estimator breaks the per-prompt stationarity that is the target signal.

MR fits `C(k) = m^k + offset` over lag k; at T = 100 the fit has ≤ 100 lags per prompt. If τ ≳ T the fit is bias-dominated. Cortical data use T ≈ 10⁴-10⁵ bins — three to four orders of magnitude more than a 100-token prompt. The layer-axis alternative (L ≈ 12-32) is worse.

**Consequence.** The pre-registered kill threshold (|correlation| < 0.15) is likely *inside* the estimator-noise regime. A synthetic-branching-process pilot at T = 100, 500, 2000 with known σ is a mandatory pre-Phase-0 gate. Workable reframe if the pilot fails: 500-2000-token Pile/C4 prompts with a short factual question appended; label attaches to the completion, σ estimated on the context.

## 4. Confound structure (concern c)

- **Training-corpus frequency.** Ji 2024 shows seen-vs-unseen is the dominant hallucination covariate. To show σ adds information: `P(hallucinate | σ, corpus-freq) ≠ P(hallucinate | corpus-freq)`. Pile is public → computable per prompt for Pythia; not for Gemma.
- **Prompt difficulty.** TruthfulQA is adversarially designed; HalluQA is Chinese with different difficulty structure; FEVER-contradicting is NLI-style. Per-prompt difficulty covariate needed to avoid a σ-as-difficulty-proxy explanation.
- **Length.** arXiv:2509.09715: Gemma-2-2B hallucination peaks at 10-30 input tokens — the same regime where MR-σ is unreliable. Length and σ-reliability mechanically coupled.
- **Base vs instruction-tuned.** Pythia-1.4B has no official instruct variant (same problem as C21). Drop Pythia-instruct; use Gemma-2-2B-it + Gemma-2-2B-base for the base/instruct contrast.
- **Judge reliability.** TruthfulQA and HalluQA use GPT-4 judges; judge error correlates with difficulty → confounds any difficulty-tracking observable.
- **Overconfident hallucination.** INSIDE and Tethered Reasoning document a low-entropy high-confidence hallucination mode. If σ correlates with entropy it may miss this mode — inverting Story A's naive sign.

Corpus-frequency (Pythia-only), length, and difficulty must enter the regression as per-prompt covariates.

## 5. Is the supercritical direction theoretically motivated? (concern d)

**Partially, and the candidate conflates two stories.**

- **Story A (amplification).** σ > 1 amplifies small activation fluctuations; a weakly supported false continuation gets locked in. Predicts hallucination rate monotone in σ − 1 (signed), low for σ < 1 (subcritical = conservative).
- **Story B (divergent sensitivity at criticality).** At σ = 1, sensitivity diverges → output hypersensitive to prompt perturbation, model commits to whatever the initial tokens push. Predicts hallucination maximised at |σ − 1| ≈ 0, not monotone.
- **Story C (null).** σ carries no signal beyond what training-frequency, entropy, and INSIDE-style probes already capture.

The candidate text asserts Story A ("super-critical → hallucination") then regresses on |σ − 1|, which is Story B's test. This must be resolved before data collection. The closest published articulation of a sensitivity-based hallucination mechanism is arXiv:2601.20026 (QTN, local sensitivity) and Tethered Reasoning 2602.17691 (entropy-sensitivity tradeoff); neither directly supports Story A. The σ > 1 = "persistent off-topic activation fluctuation" argument is coherent but not established in any cited prior work. Pre-register both regressions (signed σ and |σ − 1|) and which is primary.

## 6. Venue fit (concern e)

**NeurIPS ATTRIB is the right workshop.** ATTRIB covers attribution of behaviour to model substrate; σ as a concept-free architectural attribute predicting behaviour fits. ATTRIB 2024 ran; 2025/2026 status needs verification. **ICML Mechanistic Interpretability Workshop 2026** is the other fit. Main-track (NeurIPS / ICLR) requires beating Ji 2024 (84 %) or INSIDE on a standard benchmark, which the candidate has not committed to. Downgrade to "ATTRIB / ICML MechInterp workshop; TMLR journal-length".

## 7. Pre-registered kill (stronger than the candidate's)

1. **Estimator-floor pilot.** Synthetic branching process at T = 100, 500, 2000; MR 95 % CI on σ must be < 0.1 at σ = 1 for T to be usable. Pilot failure → reformulate to longer-context prompts or kill.
2. **Ji-2024 head-to-head.** σ-predictor ≥ 80 % balanced hallucination-classification accuracy on a matched NLG battery (baseline 84 %). Failure → "new observable" claim hollow; downgrade to descriptive correlation.
3. **Story A / B / C discrimination.** Pre-register both signed-σ and |σ − 1| regressions with per-prompt controls (corpus-frequency on Pythia, length, difficulty). Positive claim requires one story at p < 0.01 after Bonferroni.
4. **Orthogonality.** σ must predict hallucination *residually* after regressing out EigenScore (INSIDE) and semantic entropy (Kossen 2024). If not, σ is a re-parameterisation of an existing signal; workshop note only.

## 8. Rubric

- **D = 4.** Benchmarks (TruthfulQA, HalluQA, FEVER), weights (Gemma-2-2B, Pythia-1.4B), Pile (Pythia corpus-frequency covariate) all public.
- **N = 2.** Observable novelty real; problem-space saturated; main-conference headline requires beating Ji / INSIDE / H-Neurons, which is non-trivial.
- **F = 3** after reframe (§7 kills); **F = 2** as written (0.15 threshold uncalibrated against estimator noise).
- **C = 3** on paper (~3 weeks); **realistic 4-5 weeks** with estimator pilot + Ji baseline + Pile-frequency pipeline.
- **P = 3** (workshop / TMLR) reframed; **P = 2** as written (main-track aspiration optimistic).

**Composite.** PROCEED only after estimator-floor pilot, and only as one arm of Paper 8 (applied criticality) bundling C30 + C31 + C32 + C33 (and possibly C26 for shared per-prompt σ infrastructure). Not a standalone main-conference submission.

## 9. Action items

1. Cite and position against Ji 2024 (2407.03282), INSIDE (2402.03744), PRISM (2411.04847), H-Neurons (2512.01797), semantic-entropy probes (2406.15927), Semantic Energy (2508.14496), QTN (2601.20026), Tethered Reasoning (2602.17691), Gemma-length hallucination (2509.09715). Add all to `papers.csv`.
2. Insert MR-estimator short-sequence pilot as a pre-Phase-0 gate.
3. Replace "super-critical → hallucination" with explicit Story A / B / C distinction; pre-register the primary regression.
4. Add per-prompt Pile n-gram probability as a covariate on the Pythia arm; drop Pythia if this cannot be implemented cleanly.
5. Drop Pythia-instruct framing (no instruct variant exists); use Gemma-2-2B-it + Gemma-2-2B-base for the base/instruct contrast.
6. Bundle with C31 + C32 + C33 (+ optionally C26) as **Paper 8 — Applied criticality observables for LLM deployment**; target ATTRIB / ICML MechInterp / TMLR.
7. Downgrade deliverable from "NeurIPS / ICLR main" to "ATTRIB or ICML MechInterp workshop; TMLR journal".

---

**Bottom line.** Defensible, not as a 3-week standalone. The measurement is hard (MR on ~100 tokens is the real risk), the competitive baseline is stiff (Ji 2024 at 84 %), and the mechanistic story must pick Story A or B before the regression is run. Proceed as a fourth arm of an applied-criticality Paper 8.
