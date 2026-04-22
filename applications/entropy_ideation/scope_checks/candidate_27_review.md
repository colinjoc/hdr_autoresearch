# Phase -0.5 Scope-Check - Candidate 27

**Candidate.** In-context-learning emergence at sigma = 1. Test whether branching ratio sigma crosses 1 at the same training step as the Olsson-2022 induction-head / ICL phase transition, using Pythia's 154-checkpoint public release, a Nanda-style induction/ICL score, and the Candidate-1 sigma pipeline.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME - ABSORB into Paper 3 as a section, not a standalone workshop paper.** The underlying question is genuinely under-served - no 2024-2026 paper correlates sigma (or any basis-agnostic collective criticality observable) with the induction-head emergence step on Pythia - but the "ICL emerges because sigma crosses 1" headline is too narrow to carry a standalone paper, the pre-registered kill (>10 % step separation) is mis-specified, and the natural scientific value lives in a three-way head-to-head against Wang's D(t) within Paper 3's training-dynamics scope. Reframed as the "Pythia realisation" section of Paper 3, it is a ~3-week extension with clean novelty.

## 2. Feasibility of sigma on Pythia intermediate checkpoints (concern a)

**Feasible as a Paper-3 extension; tight as a standalone.** Pythia ships 154 checkpoints per scale: `step0`, ten log-spaced {1, 2, 4, ..., 512}, then 143 evenly-spaced from step1000 to step143000 [3082: Biderman 2023]. Induction emergence is narrow at ~step 1 000 across every Pythia scale (Tigges 2407.10827, 2024; 2502.14010, 2025) - Pythia's log-spaced early schedule is almost surgical for it.

Per-checkpoint cost on RTX 3060 12 GB (Candidate-7 empirical budget): MR-estimator + avalanche-size sigma on 10^5-token caches, three bases, block-bootstrapped, is ~15 min at Pythia-70M and ~90 min at Pythia-2.8B fp16. An emergence-window scan of ~50 checkpoints (20 log-spaced + 30 linear around the peak) across five in-budget scales (70M, 160M, 410M, 1B, 2.8B; 6.9B / 12B out) is ~90 GPU-hours plus ~200 GB caches (trimmable by streaming statistics). Fits a 2-3 week budget **only if** Paper 3's checkpointing infrastructure already exists; from-scratch build adds 2-3 weeks.

Per-checkpoint sigma has +/-0.02-0.05 shot-noise [1015; 1019]. That noise floor drives concern (c).

## 3. Prior art: criticality correlated with a real-LLM training-phase-transition? (concern b)

**No such paper exists on Pythia.** The 2024-2026 literature splits cleanly:

- **Criticality-through-training, toy systems.** Wang 2604.16431 / 2604.04655 (Apr 2026) tracks gradient-space cascade dimension D(t) through grokking on transformer-mod-add / MLP-XOR, crossing D=1 with 100-200 epoch lead. Prakash-Martin 2506.04434 tracks HTSR alpha through grokking. Clauw 2408.08944 tracks O-info through grokking. All three are mod-add / XOR; none touch Pythia; none target induction.
- **Criticality-on-pretrained-LLMs, no training axis.** Nakaishi 2406.05335 reports a *temperature*-parameter phase transition in GPT-2 with power-law correlations at critical temperature - inference-time. Zhang 2410.02536 (ICLR 2025) reports capability peaks at Wolfram-edge-of-chaos training-data complexity - data axis.
- **Induction-head-emergence-on-Pythia, no criticality observable.** Olsson 2022 [3024] (phase-change visible in loss, in-house Anthropic models). Edelman 2404.07129 (ICML 2024) four-phase toy-bigram mechanism. Tigges 2407.10827 replicates on Pythia 70M-12B at ~step 1 000. 2502.14010 (Feb 2025) contrasts induction-emergence (~step 1 000) vs function-vector emergence (~step 16 000) on Pythia. Sahin 2511.05743 (Nov 2025) dissociates copying from abstractive ICL. Musat 2511.01033 (Nov 2025) mechanistic theory. **None compute sigma, alpha, or any collective criticality observable alongside the induction-head score.**

**Gap is clean; scoop risk is moderate.** Wang has published twice in April 2026 and Pythia is the obvious next target - the 12-month window is not comfortable.

## 4. Is "sigma step and ICL-emergence step" well-defined? (concern c)

**The ">10 % of training" kill is mis-specified and must be replaced.** Three problems:

1. **Threshold too loose by an order of magnitude.** 10 % of Pythia training = ~14 300 steps = 14x the induction-emergence window (steps ~100-5 000). Tighten to |t_sigma - t_induction| / t_induction < 1.
2. **"Sigma crosses 1" is ill-defined at this noise floor.** With +/-0.02-0.05 per-checkpoint noise a literal zero-crossing is not well-posed. Operationalise as the first step at which a Bayesian changepoint detector on sigma(t) identifies a level-shift toward sigma=1 with posterior > 0.95, MR-estimator covariance as emission noise. **Bayesian changepoint is not optional - it is the only defensible operationalisation.** Use `bayesian_changepoint_detection` (Adams-MacKay 2007; Altamirano 2302.04759 robust-scalable variant) or BEAST. Pre-register the hazard prior (lambda ~= 1/500 steps).
3. **Same operationalisation must apply to the induction-score trajectory.** Both sigma(t) and induction(t) pass through identical detectors with matched priors; the test is 95 % credible-interval overlap of the two changepoint posteriors.

Replicate discipline is the harder problem: per `candidate_04_review.md §2`, Cohen's d=0.5 detection needs n >= 30 seeds; Pythia ships *one* seed per scale. The only axis is *across-scale* - treat 70M-2.8B as five samples and report a five-point correlation. That is weaker than a seed-wise test; standalone framing should not pretend otherwise. Bayesian changepoint itself is off-the-shelf; the real methodological effort (~1 week) is the joint bivariate model for (sigma, induction) with overlapping CIs.

## 5. Standalone vs Paper-3 section (concern d)

**Standalone is weak; Paper-3 section is strong.** Standalone: ~3-4 weeks realistic (proposed 2 is optimistic once Bayesian changepoint + five scales + bootstrap are enforced); workshop venue; novelty narrower than Wang's D(t); noise-limited to factor-of-2 coincidence claims.

Paper 3 (`promoted.md` row 11 / `candidate_03_review.md`) is already scoped as "How SGD deforms the criticality landscape" = C3 + reframed C4 with tri-init design and a (sigma, D, HTSR alpha, O-info) head-to-head on nanoGPT-on-TinyStories. Candidate 27 adds "same observables, on Pythia's pretrained checkpoints, aligned with induction-head emergence". This buys Paper 3 (a) cross-scale replication on a real LM suite, (b) a head-to-head aligned with a *real* phase transition rather than a synthetic one (grokking), (c) Candidate-8's induction-criticality question re-approached along the temporal axis. ~3 incremental weeks; pipeline reused. **Fold into Paper 3; drop workshop framing.**

## 6. Relation to Wang 2604.16431 / D(t) early-warning (concern e)

**Complementary, not redundant, but the headline must shift.** Wang's D(t) is cascade dimension in *gradient* space (TDU-OFC probe on gradient snapshots), a finite-size-scaling exponent crossing D=1 at grokking with 100-200-epoch lead on mod-add. Candidate 27's sigma(t) is one-step propagation in *activation* space via MR estimator - an autocorrelation-decay statistic, not an FSS exponent. Different axes (gradient flow vs activation flow), different mathematical objects.

Three distinct outcomes when both are computed on identical Pythia checkpoints around induction emergence:

- **Both cross unity concurrently with induction emergence.** Strong multi-observable critical claim - publishable as main-track.
- **One crosses, the other does not.** Informative disambiguation between gradient-SOC and activation-branching pictures - publishable.
- **Neither crosses at induction emergence.** The induction transition is not a criticality event in either sense - publishable negative result with high methodological content.

**All three are scientifically interesting; none requires a literal coincidence.** The original "ICL emergence is a direct consequence of criticality crossing" headline privileges outcome 1; the correct target is "what is the relationship between sigma(t), D(t) and induction-emergence(t) on Pythia?"

Hygiene items: (i) implement Wang's TDU-OFC on Pythia alongside sigma - like-for-like head-to-head; (ii) cite 2604.16431 / 2604.04655 as the gradient-space precedent; (iii) pre-register which outcome constitutes confirmation vs rejection, with Bayesian-changepoint thresholds.

## 7. Minimum-evidence-bar audit (`knowledge_base.md §5`)

Candidate 27 addresses item 5 (sigma via MR estimator) and partially item 7 (step-0 at-init control is free with intermediate checkpoints). Missing: items 1 (P(s) fit), 2 (alpha CI), 3 (beta, gamma, scaling relation), 4 (shape collapse), 6 (threshold plateau), 8 (neutral-null rejection). Not fatal - sigma is the primary observable - but the Paper-3 section must include items 1 + 3 (full crackling-noise discipline on ~3 focal checkpoints bracketing induction emergence) and item 8 (Griffiths-null rejection). Without item 8, a positive reading is compatible with Martinello-2017 non-critical branching nulls.

## 8. Pre-registered kill (rewritten)

Kill if **all of**: (a) Bayesian changepoint on sigma(t) identifies no changepoint within induction-emergence +/- 1 decade of training steps at posterior > 0.95, on any scale 70M-2.8B; (b) when changepoints are detected, 95 % credible intervals of t_sigma and t_induction do not overlap on >=3/5 scales; (c) Wang D(t) on the same checkpoints also fails to track induction-emergence within one decade. (a)+(b)+(c) kills the criticality-at-ICL-emergence claim; the section stays as a negative result / disambiguation in Paper 3.

## 9. Rubric and venue

D = 5 (Pythia + 2502.14010 induction-score code + MR estimator + Bayesian changepoint libraries all public). N = 3 standalone / 4 as Paper-3 section. F = 3 as rewritten (Bayesian changepoint + bivariate CI overlap + five-scale replicate axis). C = 3 standalone / 4 as Paper-3 section. P = 2 standalone workshop / 4 as section of a NeurIPS-main / *Neural Computation* Paper 3.

**Composite: PROCEED only as Paper 3 section, not as standalone workshop paper.**

## 10. Action items

1. Merge Candidate 27 into Paper 3 as "§Pythia realisation: criticality at induction-head emergence". Update `promoted.md` from "Paper 3 companion" to "Paper 3 §X".
2. Rewrite the kill in `candidate_ideas.md §Candidate 27` per §8: drop ">10 % of training"; replace with Bayesian-changepoint credible-interval overlap on >=3/5 scales.
3. Add the Wang head-to-head: compute TDU-OFC D(t) alongside sigma(t) on identical Pythia checkpoints; engage 2604.16431 / 2604.04655 as primary comparator.
4. Use the five Pythia scales (70M-2.8B) as the replicate axis; document that single-seed-per-scale precludes seed-wise testing; report a five-point correlation instead.
5. Pre-register before any run: Bayesian-changepoint prior (hazard ~= 1/500 steps), induction-head-score definition (adopt 2502.14010), sigma-estimator (MR + block bootstrap), three bases (raw, SAE via Gemma-Scope / FaithfulSAE-Pythia 2506.17673, PCA), threshold sweep theta in {0, p50, p95}.
6. Cite Tigges 2407.10827 and 2502.14010 as methodological primary; Olsson [3024] as phenomenon primary; Wang 2604.16431 / 04655 as criticality-at-training-transition primary; Nakaishi 2406.05335 as criticality-at-inference-parameter precedent.
