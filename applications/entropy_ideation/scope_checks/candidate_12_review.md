# Phase -0.5 Scope-Check - Candidate 12

**Candidate.** Griffiths phase or true criticality? The neutral-model rejection test.
**Question.** On the activation data from Candidate 1, distinguish "genuinely critical" from "Griffiths-phase-like" or "neutral-null-compatible" via scaling-relation residual, shape-collapse quality, and parametric sensitivity of exponents to training-run seed variation.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, then MERGE as Section 5 of Candidate 1's paper.** The neutral-null rejection test is `knowledge_base.md` §5 item 8 (mandatory) and §4 "cross-cutting" pitfall; it is not a standalone contribution under 2026 publishing norms.

## 2. Novelty vs papers.csv and 2025-2026 arXiv surface

The methodology is load-bearing but not new. `papers.csv` 2037 (Martinello 2017, *PRX*) is the template neutral-null test; 2036 (di Santo 2018, *PNAS*) and 2035 (Moretti-Munoz 2013) give Griffiths-phase rejection signatures (continuous exponent drift, non-universal finite-size scaling, short-time shape deviation, cutoff location). `lit_complex.md` §10 already lays out exactly the toolkit Candidate 12 proposes.

ID reconciliation: `candidate_ideas.md` cites Martinello as [2040] and di Santo as [2039], but `papers.csv` lists 2040 = Watkins SOC review and 2039 = Beggs-Timme 2012. Correct IDs are 2037 and 2036. Fix before Phase 0.

Arxiv 2025-2026 adjacency (WebSearch 2026-04-21):

- **Qu, Wardak, Gong 2022, arXiv 2203.12967 + PRL 129:048103 "Extended Anderson Criticality in Heavy-Tailed Neural Networks"** - heavy-tailed DNN couplings generate a Griffiths-phase-like extended critical regime, not a knife-edge. Direct ML-side precedent for the Griffiths interpretation. Uses random (untrained) matrices and mean-field theory, not avalanche exponents on trained transformer activations, and does not run a Martinello-style neutral-null likelihood comparison.
- **APS March 2022 M09.12 "Evidence for Griffiths Phase Criticality in Residual Neural Networks"** (Qu-Gong group, abstract only). ResNet at init, not trained LLM; topological signatures, not avalanche rejection.
- **Ghavasieh 2026, arXiv 2512.00168, "Tuning Universality in Deep Neural Networks"** - four-parameter stochastic theory collapsing DNN avalanche dynamics onto Directed Percolation, with activation-function Taylor coefficients tuning the universality class. Theory-side; does not empirically run Martinello 2017 / di Santo 2018 rejection on a trained network.
- **Morales-di Santo-Munoz 2023 (paper 3046)** - quasi-universal scaling on mouse-brain data. Not applied to trained transformers.
- **"Grokking as Dimensional Phase Transition" (arXiv 2604.04655)** and **"Allometric scaling..." (arXiv 2512.10834)** - different observables / models.

**Gap.** No 2024-2026 paper applies the Martinello 2017 / di Santo 2018 neutral-null + Griffiths rejection toolkit to a *trained* deep transformer on its residual-stream activation avalanches. Gap is real; what Candidate 12 lacks is a positive finding to hang it on.

## 3. Standalone methodology paper? Publishability

A "how to distinguish genuine criticality from Griffiths / neutral in deep networks" paper with no positive finding is a tough sell in 2026:

- **For**: Martinello 2017 itself is essentially a methodology paper; it was published in *PRX* because it ran against a pre-existing positive claim (Beggs 2003) and was framed as a null model with surprising fit. The parallel ML paper would need either a pre-existing LLM criticality claim to attack (there isn't one yet - the Candidate 1 paper *is* that claim) or a synthetic benchmark on a controllable network where the ground truth is known (train at different skip-connection / heavy-tail regimes a la Qu 2022, show the test distinguishes).
- **Against**: the three observables are already in `knowledge_base.md` §5 as mandatory. A paper whose contribution is "we ran the mandatory check" without a positive or strongly negative empirical finding is methodology-as-checklist - *Entropy* / *Neural Computation* will accept it; NeurIPS / ICLR / ICML will not.

Upshot: Candidate 12 is publishable standalone only if (a) it reveals that Candidate 1's apparent criticality is Griffiths-phase or neutral-compatible (a strong negative with interpretive value; but then it *is* Candidate 1's result), or (b) it is reframed as a synthetic-benchmark methodology paper validating the rejection toolkit on controllable deep networks before applying it to GPT-2 (different compute budget; different novelty claim).

## 4. Merge-vs-separate recommendation

Merge as §5 of Candidate 1's paper. The knowledge-base checklist has eight items; Candidate 1 commits to seven; item 8 (neutral-null rejection) *is* Candidate 12. Omitting it would drop Candidate 1 from "seven of eight" to "six of eight" and weaken the publication. Including it is the guard-rail that Beggs 2012, Martinello 2017, Moretti 2013, di Santo 2018, Munoz 2018 unanimously require for any positive criticality claim on a high-dimensional heterogeneous network.

Concretely, Candidate 1 §5 "Neutral-null and Griffiths-phase rejection":

- (5.1) Sethna scaling-relation residual gamma - (beta - 1) / (alpha - 1) with block-bootstrap CI. Already in Candidate 1.
- (5.2) Shape-collapse quality (chi-squared on F(t/T)) vs mean-field branching shape *and* Martinello neutral-model shape. Both closed-form or simulable.
- (5.3) Seed-variance panel: N >= 5 independent pretraining seeds. Griffiths predicts continuous drift; true criticality predicts clustering within CI.
- (5.4) Griffiths cutoff-location test: short-time slope of avalanche shape at fixed T (di Santo 2018 eqs).
- (5.5) Neutral-null likelihood ratio: fit empirical P(s), P(T), joint (s, T), shape to (i) DP / branching-process mean-field, (ii) Martinello neutral random-walk-plus-absorbing, (iii) Qu 2022 heavy-tailed / Anderson. Report log-likelihood ratios with KS / bootstrap p.

If any of (5.1-5.5) fail, the paper is still publishable and more interesting - headline becomes "Griffiths-phase interpretation of apparent criticality in trained LLMs", defensible given Qu 2022 and Munoz 2018 priors.

## 5. Feasibility and compute delta on top of Candidate 1

- (5.1): already inside Candidate 1. Zero compute.
- (5.2): Candidate 1 already requires shape collapse. ~1-2 days extra coding for Martinello-shape comparison.
- (5.3) seed-variance: the dominant cost. Candidate 12 says "10+ training runs". Training 10 GPT-2-smalls from scratch is ~10-15 GPU-days on one RTX 3060 - violates the 4-week budget. Fix: use public multi-seed checkpoints. **Pythia** has deduped sizes with intermediate checkpoints but not multi-seed at fixed size; **OLMo** has limited multi-seed; HuggingFace hosts 5-10 Karpathy-style GPT-2-small replications. Realistic panel: 5 independent HF seeds + original OpenAI GPT-2-small. Six runs, inference-only, ~2 extra GPU-days for caching. Feasible.
- (5.4): trivial post-processing. Hours.
- (5.5): Martinello neutral simulation is fast (CPU); branching-process mean-field is closed form. 2-3 days coding.

**Total delta on Candidate 1**: ~1 week (not 2), dominated by (5.3) and (5.5). This is a week Candidate 1 already needs to satisfy `knowledge_base.md` §5.

## 6. Pre-registered kill condition for the merged §5

Reuse Candidate 1's kill line plus:

- If (5.1) scaling-relation residual exceeds 2 bootstrap sigma and (5.2) shape-collapse chi-squared favours neutral over critical, headline becomes "apparent criticality is neutral-null compatible" (negative-result paper, still publishable).
- If (5.1) holds but (5.3) exponents drift continuously across seeds with variance > 0.1 or (5.5) log-likelihood favours heavy-tailed / Anderson over DP, headline becomes "Griffiths-phase interpretation of trained-transformer avalanches" (positive, reframes the claim).
- If (5.1) holds, (5.3) clusters, (5.4) shape short-time slope matches critical, and (5.5) favours DP mean-field, the headline is "evidence consistent with true critical dynamics" (the strong positive).

All three outcomes are publishable; only the narrative shifts.

## 7. Risks and mitigations

- Multi-seed GPT-2-small replicates may not be training-step-matched, inflating seed-variance. *Mitigation*: use HF replications with matching hyperparameters; fall back to Pythia-160M as cross-scale proxy.
- Qu 2022 heavy-tailed alternative (5.5 item iii) requires weight-matrix tail-index estimation, extra to Candidate 1. *Mitigation*: cite but defer; DP mean-field vs Martinello neutral suffice for the rejection test.
- Seed panel may show alpha clustering within CI, making (5.3) look uninformative. *Mitigation*: clustering *is* the positive result - it supports universality over Griffiths.
- "Methodology section" framing can bury the contribution. *Mitigation*: state in Candidate 1's abstract "first application of Martinello-di Santo neutral-null and Griffiths-phase rejection tests to a trained transformer".

## 8. Summary

**Verdict.** REFRAME as Candidate 1 §5. Not a separate paper. ~1 week extra on top of Candidate 1 using public multi-seed checkpoints.
**Rubric.** D = 5 (uses Candidate 1's real activations; multi-seed data public); N = 3 as standalone, N = 4 as merged §5 (first application of Martinello 2017 / di Santo 2018 rejection toolkit to a trained transformer); F = 5 (three pre-registered quantitative tests, three distinct narrative outcomes); C = 5 (~1 week delta, no new training); P = 5 merged / P = 2 standalone. Composite strongly favours merge.
**Action items.** (i) Fix citation IDs in candidate_ideas.md: Martinello = 2037, di Santo = 2036. (ii) Add §5 block to Candidate 1's paper outline; update Candidate 1's compute estimate from "~2 weeks" to "~3 weeks" to absorb the merged §5 work. (iii) Remove Candidate 12 from `promoted.md` as an independent project; note in `promoted.md` that its content is promoted-as-§5-of-Candidate-1.
