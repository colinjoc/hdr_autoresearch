# Phase -0.5 Scope-Check - Candidate 34

**Title.** Emergent capability = σ phase transition (Wei vs Schaeffer resolution).
**Proposed observables.** σ(scale) across Pythia 70M-2.8B vs capability scores; test whether capability-discontinuities align with σ-crossings.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME - PROCEED as a Paper 5 companion, not a standalone.** The Wei-Schaeffer debate is a genuine open question with no scale-axis physics-observable resolution as of 2026-04. But the candidate as written has four structural weaknesses: (a) a 7-scale single-checkpoint design is statistically under-powered; (b) Nakaishi 2406.05335 (June 2024) already computes a *temperature-axis* critical phase transition on Pythia-70M and must be cited and differentiated; (c) Du 2403.15796 (NeurIPS 2024) partially resolved the debate on the pre-training-loss axis, so the remaining genuinely-open question is whether a criticality observable (σ/α/shape-collapse) adds explanatory content *above loss*; (d) Schaeffer-side 2502.17356 (Feb 2025) shifts the null to *bimodal-across-seed* distributions, mandating a multi-seed control absent from the current proposal. Reframe: reuse reframed Candidate 7's Pythia (N, t) atlas (five scales × ~20 checkpoints); overlay continuous + discontinuous capability metrics; pre-register a 2D Bayesian-changepoint test and an `L_pretrain`-regression null; make the Paper 5 companion framing explicit.

## 2. Has a 2024-2026 paper addressed Wei-Schaeffer via a physics observable?

**Partially yes - three near-misses, none closes the gap.**

- **Nakaishi, Nishikawa, Hukushima, arXiv:2406.05335 (2024)** - "Critical Phase Transition in a Large Language Model". Pythia-70M + Japanese GPT-2; genuine critical phase transition as a function of *sampling temperature*, power-law correlation decay at T_c. Closest prior art. Axis is temperature, not scale, so does *not* resolve Wei-Schaeffer (which is a scale-axis claim). Candidate's "first empirical test with a physics observable" wording must weaken to "first scale-axis physics-observable test". Mandatory cite; methodological borrow (power-law correlation length as auxiliary observable).
- **Du, Zeng, Dong, Tang, arXiv:2403.15796 (NeurIPS 2024)** - "Understanding Emergent Abilities from the Loss Perspective". Capability crossovers predictable from *pre-training loss* thresholds, independent of metric continuity. Partly concedes Wei (continuous-loss threshold is real), partly concedes Schaeffer (accuracy discontinuity is metric-induced). Strongest partial-resolution prior. Remaining open question: does σ carry information *beyond* `L_pretrain`? This is the publishable reframing.
- **Schaeffer et al., arXiv:2502.17356 (Feb 2025)** - "Random Scaling of Emergent Capabilities". Breakthroughs attributed to bimodal across-seed distributions, not metric choice alone. Mandates multi-seed control.
- **Krakauer, Krakauer, Mitchell, arXiv:2506.11135 (2025)** - Conceptual complex-systems paper, no observable computed; framing cite.
- **Hong & Hong, `papers.csv` 3086 (2025)** - KL / vocabulary / word-length discontinuities during training of small transformers. Training-step axis, not scale-axis; cite.

**Defensible framing:** "First **scale-axis** criticality-observable test of Wei vs Schaeffer with explicit additive-explanatory-power null against Du 2024's loss baseline and multi-seed variance control against Schaeffer 2025's bimodality null."

## 3. Capability benchmarks - discontinuous vs smooth

Three tiers required:

**Tier A - genuinely discontinuous below 2.8B (per Wei 2022).** The BIG-Bench-Hard subset Wei documented as emergent below 2.8B params: periodic-elements, modular arithmetic, IPA transliteration, word-unscramble. Exact-match scored.

**Tier B - smooth under continuous proxies (per Schaeffer 2023, Du 2024).** Same prompts, Brier score / CorrectChoiceProb / token-edit-distance / per-token log-likelihood. Standard 2024-2026 practice is to compute both A and B on matched prompts.

**Tier C - negative controls.** Perplexity, LAMBADA cloze, standard NLI - tasks where no discontinuity is claimed. σ must not cross here if the claim is to be scale-emergence-specific.

**MMLU is a trap.** MMLU's documented ~10B jump is above Pythia-2.8B. Including it in Tier A guarantees an uninformative negative. Drop MMLU from Tier A; restrict Tier A to tasks Wei explicitly documented as emergent below 2.8B.

## 4. Sample size: is 7 points enough?

**No, single-checkpoint 7-scale is under-powered.** Per-scale σ shot noise is ~0.02-0.04 (block-bootstrap, MR estimator, Priesemann-Wilting subsampling correction). A Nakaishi-sized critical signature Δσ ≈ 0.05-0.15 on 7 points with 0.03 per-point error yields a Bayesian changepoint Bayes factor of ~3-10 under the true-change hypothesis - suggestive, not decisive, well below 20:1.

**Pythia's 154 intermediate checkpoints per scale are the essential fix.** 20 log-spaced ckpts × 5 scales = 100 (N, t) cells lets two cleaner questions be asked: (i) does σ(N, t) cross 1 at a training step aligned with capability emergence (Olsson 2022 / Candidate 27 framing)? (ii) is there a scale threshold above which σ crosses 1 earlier in training (Wei framing)? With 100 cells, changepoint detection on each marginal axis has ~4× the effective power. Natural stats framework becomes 2D Bayesian changepoint (Adams-MacKay online BCP or 2D GP-step-kernel), not 1D. This is exactly the design reframed Candidate 7 already commits to - hence the Paper 5 companion reframe.

## 5. Strongest nulls

Three nulls, ordered:

**H0a (Schaeffer-2023).** σ(N) and continuous-metric capability(N) are both smooth; accuracy discontinuity is metric-induced. Reject by: σ-crossing aligns with continuous-metric inflection, not with accuracy jump.

**H0b (Du-loss-threshold, 2024).** Capability thresholds fully explained by `L_pretrain`; σ carries no extra predictive info. Reject by: regress capability(N, t) on both `L_pretrain(N, t)` and σ(N, t); σ's partial R² must be significant after controlling for loss. **This is the scientifically critical null** - the only clean separator from Du 2024.

**H0c (Schaeffer-2025-bimodal).** Apparent breakthroughs reflect bimodal across-seed distributions. Reject by: ≥ 3 seeds at any scale with a claimed σ-crossing. EleutherAI released additional-seed Pythia runs only for 160M and 1.4B - multi-seed arm feasible only at those two scales.

H0b rejection → NeurIPS / ICLR main. H0b acceptance (σ tracks loss) → modest-novelty Du-confirmation. Either is publishable; only the former is a flagship result.

## 6. Bayesian-changepoint feasibility

Standard + tractable:

- **1D along t (per scale):** Adams-MacKay 2007 online BCP with Student-t observation model; `bayesian_changepoint_detection` package.
- **1D along N (at fixed t):** PELT / BinSeg or stickbreaking-DP segmentation (pymc). Small-N axis limits evidence strength but is the axis Wei-Schaeffer argues about.
- **2D (N, t):** GP with step-function kernel (pymc `gp.Marginal` + custom mean) or BART-changepoint. This is the methodological novelty; ~2-3 days stats engineering.
- **Continuous-proxy comparison:** matched-metric changepoint on accuracy(N, t) and Brier(N, t) simultaneously - mandatory for Schaeffer-null rejection.

Total stats-engineering: ~5 working days. All feasible on the existing laptop stack.

## 7. Relation to Paper 5 - standalone or companion?

**Companion.** C34 cannot run without Paper 5's (N, t) atlas; the atlas cannot be interpreted without C34-style capability annotations. Tight mutual dependency, not a loose bundle.

- **Paper 5 core**: σ(N, t) atlas, criticality-at-scale mapping, minimum-evidence-bar-compliant on the criticality side.
- **Paper 5 companion (C34)**: capability(N, t) overlay + changepoint alignment + H0b rejection.

Fits cleanly in one 8-10 page paper with §5 dedicated to the Wei-Schaeffer test. Splitting fragments both. `promoted.md` line 42 already flags C34 as "Paper 5 companion / Wei-Schaeffer resolution" - ratify and move out of "pending" into "Paper 5 arm".

**Budget.** 4 weeks as a companion is realistic *if* Paper 5's (N, t) atlas is already computed (shared cache, inference pipeline, changepoint code). 4 weeks as standalone is not: rebuilding the atlas is ~3 weeks on its own.

## 8. Pre-registered kill (rewritten)

Kill the σ-explains-emergence claim if *all three*: (a) σ(N, t) and continuous capability(N, t) both pass 2D Bayesian changepoint with Bayes factor < 3 for any jump; (b) after conditioning on `L_pretrain(N, t)`, σ's partial R² on capability is < 5% (H0b accepted); (c) on the 160M and 1.4B multi-seed arms, σ-crossings are within-seed-consistent but fail to correlate with capability-crossings across seeds. Any two of three rejected → PROCEED to writeup.

## 9. Rubric

- D = 5: Pythia weights, checkpoints, BIG-Bench, TriviaQA, multi-seed Pythia runs for 160M + 1.4B all public.
- N = 3 standalone / N = 4 as Paper 5 arm (narrow gap after Nakaishi + Du; H0b rejection would be genuinely new).
- F = 3: explicit changepoint + continuous/discontinuous metric pair + multi-seed at 2 scales + `L_pretrain` regression control.
- C = 4 as Paper 5 companion / C = 2 standalone.
- P = 4 as Paper 5 arm (NeurIPS / ICLR main for H0b-rejection outcome).

**Composite: REFRAME - PROCEED** strictly as Paper 5's Wei-Schaeffer arm. Not a standalone.

## 10. Action items

1. Update `candidate_ideas.md §C34`: replace "First empirical test with a physics observable" with "First scale-axis criticality-observable test"; cite Nakaishi 2406.05335 as temperature-axis prior art.
2. Add Du 2024 (arXiv:2403.15796), Schaeffer 2025 (arXiv:2502.17356), Nakaishi 2024 (arXiv:2406.05335), Krakauer-Mitchell 2025 (arXiv:2506.11135) to `papers.csv`.
3. Drop MMLU from Tier A; restrict Tier A to Wei-2022 BIG-Bench tasks emergent below 2.8B.
4. Move C34 from `promoted.md` "pending" (line 42) to Paper 5's arm list alongside reframed C7 and C9-capstone.
5. Commit to 2D Bayesian changepoint (Adams-MacKay + GP-step-kernel) as stats spine; pre-register in Phase 0 doc.
6. Commit to H0b (`L_pretrain` regression) as primary falsifier - this is the separator from Du 2024.
7. Verify EleutherAI multi-seed Pythia-160M and 1.4B downloads in Phase 0 (per verify-data-access-before-Phase-0 memory rule).
