# Phase -0.5 Scope-Check - Candidate 18

**Candidate.** Cross-universality-class comparison: pretrained-LLM avalanche exponents (alpha, beta, gamma) vs Beggs-Plenz / Shriki / Ma cortical-avalanche datasets; joint bootstrap test for exponent-equality.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME.** The question is genuinely novel on the 2024-2026 arXiv surface, but the candidate as written collapses on three fronts: (a) two of the three named datasets (Shriki, Ma) are not archivally public; (b) a rigorous "same event-definition protocol" across discrete-spike cortex and continuous-activation transformer is a non-trivial methodological contribution requiring synthetic-ground-truth validation; (c) "universality class" is a category overreach - exponent coincidence does not identify a class, only consistency with one. With (i) substituted public datasets, (ii) a synthetic matched-protocol validation, and (iii) a headline downgraded from "universality class" to "exponent-equality under field-canonical protocols", this is publishable.

## 2. Data availability - the strongest pressure

`lit_neuro.md` Theme 7 names CRCNS, Allen Brain Observatory, and DANDI as viable public archives. The candidate's three datasets do not map cleanly to these:

| Cited dataset | Actually public? |
|---|---|
| **Beggs-Plenz 2003** (organotypic rat LFP, 60-ch MEA) | Original 2003 LFP data not deposited. The closest public asset is **CRCNS ssc-3** (Ito, Yeh, Timme, Hottowy, Litke, Beggs 2016): mouse slice spikes, 512-channel array, 25 recordings, 98-594 neurons each, ~184 MB .mat, registration-gated free download, DOI 10.6080/K07D2S2F. Different modality, different species, same lab. |
| **Shriki et al. 2013** (human resting MEG, 124 subjects) | Paper states data "available from O.S. on reasonable request" - no public archive. |
| **Ma et al. 2019** (awake rat V1/FrCx spikes, Hengen lab) | No DANDI / CRCNS / Zenodo deposition surfaced. Contact-the-PI policy. |

Two of three are gated behind cold-email requests, which is outside the "3 weeks, data-loading-is-the-wall-cost" envelope and violates the `~/.claude/CLAUDE.md` "verify data access before Phase 0" invariant.

**Replacement set that is actually downloadable:**
- **CRCNS ssc-3** (mouse slice spikes).
- **Allen Brain Observatory Neuropixels Visual Coding** (multi-area mouse spikes, NWB, fully public).
- **Senzai et al. 2021 / Fontenele-adjacent NWB rat cortex datasets** (Sci. Data 2021 anaesthetised-rat 128-channel silicon-probe deposit).

Per "Real data first", swap the cortex panel to this triple. Scientific claim *strengthens* (three preparations spanning slice / anaesthetised / awake, not one).

## 3. The "same event-definition protocol" methodology gap

User's concern is correct. Cortex is neuron x time (discrete spikes). Transformer is layer x position x feature (continuous real-valued). Options for the transformer's space-time analogue include: feature x position, layer x position (Candidate 1's choice, Petermann-2009 layer-as-time analogy), head x position, SAE-feature x position. Cortex has no layer analogue at spike resolution.

**"Matched protocol" must therefore be described as field-canonical-within-each-substrate, not literally identical.** The joint bootstrap operates on two exponent triples each extracted via each field's canonical pipeline: Friedman-2012 / Clauset-Shalizi-Newman for cortex, Candidate-1 layer-time binning for LLM.

Reviewers will push on any matched-protocol claim. **Mandatory mitigation:** run both pipelines on a shared synthetic ground truth - a mean-field branching-process simulation viewed two ways (discrete spikes; continuous local potential). Both pipelines must recover known exponents within CI. Without this validation, the cross-substrate claim is indefensible. ~1 week extra.

## 4. Universality class vs exponent match

Exponent coincidence does not identify a universality class. Mean-field directed percolation, mean-field branching process, and Griffiths-phase regimes all give (alpha, beta) = (3/2, 2). `lit_neuro.md` Theme 4 flags this explicitly (Villegas 2019: cortex may be non-MF-DP). Ghavasieh 2026 (arXiv:2512.00168) now shows random DNNs can sit in at least two distinct DP-family sub-classes selected by activation function.

**Publishable claim:** "LLM and cortical avalanche exponents are jointly consistent with a common class within bootstrap CI under field-canonical protocols." **Not publishable:** "LLMs are in the cortical MF-DP universality class." True class identification would require finite-size-scaling collapse on both sides (Pythia suite LLM-side is OK; cortex side needs multi-subset N-scaling), response-function / susceptibility scaling, and shape-collapse parametrised by (nu_parallel, nu_perp) - none fit in 4 weeks.

Drop "universality class" from the headline; keep it as §Discussion framing.

## 5. Novelty vs 2024-2026 arXiv surface

Searches run 2026-04-21:

- **Ghavasieh 2026, arXiv:2512.00168 "Tuning Universality in Deep Neural Networks"** - theory only; four-parameter stochastic framework, activation-function-tuned DP sub-classes. No cortex-LLM empirical exponent comparison. Complements, does not collide.
- **Arola-Fernandez 2025, arXiv:2508.06477 "Intuition emerges in Maximum Caliber models at criticality"** - maximum-caliber toy maze models. Not cross-substrate exponent comparison.
- **arXiv:2509.22649 "Toward a Physics of Deep Learning and Brains"** - synthesis / position; not empirical.
- **arXiv:2307.02284 "Universal Scaling Laws of Absorbing Phase Transitions in Artificial DNNs"** - feed-forward random nets; no cortex comparison.
- **bioRxiv 2024.12.26.629294 "Universality of representation in biological and artificial neural networks"** - representational similarity (CKA family), not avalanche exponents.
- **NeurIPS 2025 poster "Scaling and context steer LLMs along the same computational path as the human brain"** - fMRI encoding-model alignment, not avalanche exponents.

**Gap verdict:** no 2024-2026 paper runs a joint bootstrap equality test on avalanche exponents between pretrained-LLM activations and public cortical-avalanche data. Ghavasieh 2026 is the closest (theoretical only). Empirical gap is real.

## 6. Minimum sample sizes for distinguishing overlapping vs non-overlapping CIs

For CSN-MLE exponent estimates, `sigma(alpha_hat) ~ (alpha-1)/sqrt(N_events)`. For alpha ~ 1.5, `N_events = 10^3` gives sigma ~ 0.016; `N_events = 10^4` gives sigma ~ 0.005.

- **Cortex side, ssc-3 pooled:** ~10^4-10^5 avalanches across 25 recordings after x_min truncation. sigma(alpha_cortex) ~ 0.003-0.01.
- **Cortex side, Allen Neuropixels pooled:** comparable order.
- **LLM side, GPT-2-small residual stream on 10^4 Pile samples, seq=1024:** ~10^5-10^6 avalanches. sigma(alpha_LLM) < 0.01.

**Joint test:** `z = (alpha_LLM - alpha_cortex) / sqrt(sigma_LLM^2 + sigma_cortex^2)`. With both sigmas at 0.01, a true 0.05 gap is 3.5 sigma (clearly detectable); a 0.02 gap is 1.4 sigma (marginal). Published cortex-side preparation-to-preparation spread is ~0.05 in alpha, so the available N is sufficient to resolve at the scale of that natural variance. **Test is well-powered**, conditional on both sides passing CSN p > 0.05 over >= 2 decades. If either side fails the power-law existence test, Candidate 18 is auto-killed regardless of N.

## 7. Feasibility on one RTX 3060 in 4 weeks

- Week 1: LLM activation extraction (shared with Candidate 1).
- Week 2: CRCNS ssc-3 + Allen Neuropixels subset download; avalanche extraction via NCC / in-house Friedman-2012 protocol.
- Week 3: Pooled CSN fits, shape collapse, Sethna-relation residuals both sides; joint bootstrap on (delta alpha, delta beta, delta gamma); synthetic-ground-truth matched-protocol validation.
- Week 4: Null controls (shuffled cortex, shuffled LLM); writeup.

**Realistic: 4-5 weeks**, not 3. Strictly downstream of Candidate 1.

## 8. Controls specific to Candidate 18

- (C18.1) Joint bootstrap on (delta alpha, delta beta, delta gamma) with block resampling.
- (C18.2) Preparation-stratified CIs (ssc-3 vs Allen vs anaesthetised rat vs LLM), not pooled cortex-as-one.
- (C18.3) Shuffle nulls: neuron-label-shuffled cortex and position-shuffled LLM; both must move exponents away from 3/2.
- (C18.4) Synthetic matched-protocol validation (MF-branching-process ground truth, two view modalities, both pipelines recover known exponents).

## 9. Pre-registered kill conditions

- **K1 (inherited):** Candidate 1 fails CSN p > 0.05 over >= 2 decades -> nothing to compare.
- **K2 (data-access):** 1-week cap on cortex-side public dataset sufficiency; no synthetic cortex substitute.
- **K3 (methodology):** synthetic matched-protocol pipelines disagree by > 0.05 -> cross-substrate claim downgraded.
- **K4 (main):** |delta alpha| or |delta beta| or |delta gamma| > 2 * sqrt(sigma_LLM^2 + sigma_cortex^2) -> "LLMs and cortex are in distinct exponent regimes", still publishable as negative result.

All four binary and pre-declared.

## 10. Dependence, venue, rubric

- **Strictly downstream** of Candidate 1; **natural co-run** with Candidate 12 (Griffiths-null strengthens positive).
- **Realistic venues:** *Neural Computation*, *Entropy*, *PRX Life*, *PRE*; workshop hedge at NeurIPS *Unifying Representations* / *Brain & AI*. *Nature MI* / *PNAS* only with added finite-size-scaling on both sides (out of scope at current compute budget).
- **Rubric:** D = 3 (4 post-substitution), N = 4, F = 4, C = 3, P = 3-4.

## 11. Action items before promotion

1. Replace §18 datasets in `candidate_ideas.md`: drop Shriki / Ma as primary; use CRCNS ssc-3 + Allen Neuropixels + Senzai-Fontenele-adjacent NWB. Keep Ma as aspirational contact-the-PI item with explicit fallback.
2. Add C18.4 synthetic matched-protocol validation to Required controls.
3. Replace "universality-class comparison" headline with "exponent-equality test under field-canonical protocols"; keep universality-class in Discussion only.
4. State explicit dependence on Candidate 1.
5. Bump compute estimate 3 -> 5 weeks.
6. Cite Ghavasieh 2026 (arXiv:2512.00168) as theoretical companion; cite Villegas 2019 and `lit_neuro.md` Theme 4 on exponent-coincidence vs class-identification.
