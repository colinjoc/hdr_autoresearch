# Phase 3.5 Paper Review (v3) — qec_drift_tracking / paper_v3.md

## 1. One-paragraph assessment

The manuscript reports a particle-filter (PF) / sequential-Monte-Carlo (SMC) approach to online noise-model inference for quantum error correction (QEC), and frames itself as a methodology contribution: a null-hypothesis test that distinguishes a genuinely filtering estimator from one that merely "prior-holds," a diagnosis of why a naive PF fails the test, and a calibrated variant that partially passes. The positive quantitative headline is modest: 14% of the prior-to-truth gap closed in 5000 shots under a 100× mis-specified prior, with baselines still achieving lower MSE. The writing is candid to a fault — it contains a prominent retraction table against a prior (unpublished-to-this-reviewer) v2 draft. As written, the paper reads as a lab notebook fragment more than a completed study: the "open items" list in §5.2 contains eight entries, two of which (faithful MLE and faithful TN+MCMC baselines) are the very comparisons needed to justify the central claim. I cannot recommend acceptance at Phys. Rev. Research in its current form. SciPost Physics Codebases is a more plausible fit if the codebase and null-testbench are the artefact being reviewed, but even there the paper needs substantial revision.

## 2. Strengths

- The **null-hypothesis test** (§1.2, §2.4) is a genuinely useful idea: initialise the PF 100× below the generator base rate and check whether the posterior moves. It is simple, cheap, and exposes a failure mode that matched-prior synthetic benchmarks hide.
- The **diagnosis table** in §3.2 is a clean pedagogical artefact: three named causes (likelihood flatness at p~10⁻³, narrow particle coverage, small effective batch) each mapped to a specific calibration knob.
- The **pair-correlation likelihood** (§2.1, Eq. in lines 34–38) is a principled alternative to per-shot independent Bernoulli in the low-rate regime where single-shot information is negligible.
- Transparency about the prior draft's error via the §6 retraction table is admirable scientific practice and removes ambiguity for a reviewer.
- Real Willow data (Zenodo 13273331) is used (§2.5, §3.3), not synthetic-only, though only one d=5 r01 experiment is analysed.

## 3. Major concerns

**M1. The central positive claim is not established against faithful baselines.** §2.3 states the baselines are "conservative reimplementations … not faithful — the published algorithms use correlated-pair MLE and TN+MCMC respectively." §5.2 item 1–2 lists those as open. The paper's positive claim ("the PF can filter when calibrated correctly") is decoupled from baselines, but §3.1 still reports "Strict MSE wins over baselines: still 0/8," and §3.3 withdraws the real-data MSE ordering. A reviewer cannot distinguish "calibrated PF is a useful addition" from "calibrated PF is strictly dominated by correctly-implemented baselines." **Fix:** implement faithful correlated-pair MLE (arXiv:2511.09491) and at minimum a correctly-tuned TN+MCMC or cite another group's reference implementation, and re-run the null test on all methods.

**M2. n=1 real-data experiment.** §2.5 and §3.3 report a single d=5 r01 experiment, 50 000 shots, and §3.3 gives a posterior range ("~1.2–1.5×10⁻³") without confidence intervals or bootstrap. §5.2 item 4 lists "Full-50 000-shot real-data run with bootstrap CIs" as open. The quantitative headline on real data is therefore an estimate from one experiment without error bars. **Fix:** bootstrap CIs and at least d=3, d=5, d=7 runs.

**M3. The 14% number has no uncertainty quantification.** §3.1 and Table (lines 66–68) report "14% of prior-to-truth gap closed across all 8 (τ, σ) cells" as a single number. Was this averaged, min-over-cells, or max? What is the spread across cells? Under Monte Carlo noise with 500 particles and 5000 shots, the variance of the posterior mean is not negligible. **Fix:** report per-cell values with Monte Carlo error bars, and include at least 5 independent PF seeds per cell.

**M4. Extrapolation in §3.4 is unsupported.** Line 86 extrapolates "~100 × 1000 shots to close the gap fully" linearly from the 14%/5000 shots datapoint, then concludes the filter is "viable." Linear extrapolation of a Bayesian filter's posterior mean toward truth across two decades is not justified; posterior update rates typically saturate or slow as the prior is partially corrected. **Fix:** run the PF for 50 000 shots and measure actual convergence, or remove the viability claim.

**M5. Figure 3 is not generated.** §3.2 says "Figure 3 (schematic, not generated for this draft)". Submitting a manuscript to PRR or SciPost with a labelled-but-missing figure is a procedural problem. **Fix:** generate the figure or cut the reference.

**M6. Pair-correlation likelihood derivation is under-specified.** The three lines 36–38 define C_emp, C_pred, and σ²_pair but do not justify the Gaussian approximation at low rates, do not say whether the diagonal is excluded, and use `p_i` (single-detector rate) in `σ²_pair[i,j] = p_i p_j / n_batch` without defining it — is it evaluated at the particle θ_p or at the batch-empirical rate? The shot-noise floor for an off-diagonal covariance element is more involved than `p_i p_j / n_batch` for non-independent detectors. **Fix:** full derivation in an appendix, with explicit assumptions.

**M7. Novelty vs. replication is muddled.** §5.3 notes the paper combines "positive filtering result + explicit diagnosis + null-test methodology." But naive SMC failing in regimes where the likelihood is flat is a textbook particle-degeneracy result, and the calibration fixes (batch accumulation, wider priors, higher-order statistics) are standard SMC practice. **Fix:** position the paper's novelty explicitly against the SMC literature (e.g., Chopin & Papaspiliopoulos 2020, Doucet & Johansen 2011) and against the three cited QEC preprints, not only against the authors' own retracted v2.

## 4. Minor concerns

- §1.1 lines 13: the three preprints (arXiv:2511.09491, 2406.08981, 2504.14643) are cited only as preprint numbers; authors, titles, and a one-line characterisation of each are needed on first use.
- §2.1 line 32: "this is critical" is colloquial; replace with a quantitative statement (e.g., "σ_log < X fails the null test by posterior-support argument Y").
- The retracted paper_v2 is referenced (lines 24, 62, 90) but a reader of v3 alone has no access to it. Either include v2's specific numeric claims in the retraction table or drop the cross-references.
- §3.4 line 86: "~1 μs/shot" and "1/hr" refit cadence are given as if known; cite the Willow paper for shot time.
- §5.2 line 107: "Formal LCD-as-1-particle-SMC equivalence proof" is dangled in the open-items list with no context — what is LCD? First use of the acronym is in §5.2 item 3.
- Line 7 abstract: "log-std = 2.0 spanning ~4 decades in rate space" — σ_log = 2 corresponds to roughly ±2σ ≈ ±4 decades, so ~4 decades is half the 95% support; clarify.
- §2.2 mixes naive-PF spec into Method as a side note; consider a unified table.
- The abstract promises the test "should become standard"; abstracts usually do not editorialise methodology-adoption.

## 5. The diagnosis-and-fix narrative

The narrative structure — naive-fails → null-test-catches-it → three-causes-identified → calibrated-fixes-one-dimension → partial-success — is defensible in principle but weak in this execution. Diagnosis-and-fix papers succeed at journals when (a) the diagnosis is non-obvious and generalises (e.g., Neal 2003 on slice sampling, Gelman et al. on R-hat degeneracy), and (b) the fix works convincingly. Here the three causes are plausible but the calibrated fix closes only 14% of the gap and is still beaten on MSE by baselines. A real-journal reviewer — especially at PRR, which expects a clear positive contribution — will ask "so what do I conclude, that PFs work or don't?" The paper's honest answer is "they work slowly and the baselines are better," which is a useful cautionary note but a thin contribution. SciPost Physics Codebases is more tolerant of "here is the honest state of the art" framings. The paper would be stronger if it committed to one of: (i) "the null test is the contribution, and here is one worked example" (short note), or (ii) "the calibrated PF beats baselines on criterion X" (requires M1 fixed).

## 6. The 14% partial result

Fourteen percent is a half-measure. A truly effective filter under 100× prior mis-specification should close the gap decisively — published particle-filter demonstrations in state-space models routinely achieve >90% convergence within a few effective sample sizes when the likelihood is informative. The 14% number is more consistent with a marginally-informative likelihood plus a slow exploration kernel than with a healthy filter. The extrapolation in §3.4 (linear to 100% at 100×5000=500 000 shots) is the optimistic reading; the pessimistic reading is that the filter will plateau below 50%. Without a longer run or a theoretical convergence-rate argument, I cannot tell which. This matters because the §5.3 framing — "viable for realistic device refit cadences" — rests on the linear extrapolation. For a positive result at PRR I would want convergence curves to 90%+ at some (perhaps generous) shot budget. As a cautionary result at SciPost Physics Codebases, 14% with CIs and a long-run convergence curve is defensible.

## 7. Retraction disclosure audit

The §6 retraction table is simultaneously the paper's most admirable and most problematic feature. As a reviewer I read it as a strength: the authors caught their own error via the null test, reported it, and revised. That is good science. However: (a) journal editors and other reviewers will read it as "this methodology is unstable — the same authors reported the opposite finding months ago"; (b) v1 and v2 are referenced but not reachable by a v3-only reviewer, so the retraction is a claim about invisible objects; (c) a PRR or SciPost editor may legitimately ask "why are we refereeing the third attempt?" My recommendation to the authors: if asked for a cleaner submission, (i) **delete the retraction table** as a standalone section, (ii) move the "prior-holding artefact" discussion into §1 as a motivation ("matched-prior benchmarks can mislead, as we initially found") without reference to paper_v2, and (iii) keep the null test as the positive methodological contribution. The intellectual honesty is preserved without signalling instability. Alternatively, if submitting to SciPost Physics Codebases where transparency is explicitly valued, keep the table.

## 8. Is the null-hypothesis test a standalone contribution?

Yes, plausibly — as a short comment or methods note (e.g., SciPost Physics Comments, or a letter to Quantum). The null test is a one-paragraph idea with broad applicability to any online-inference proposal in a sparse-event regime, not just QEC. The paper's own §5.1 says "any paper proposing online noise-model inference on QEC syndrome streams should report the prior-mis-specification null test"; that sentence is the seed of a standalone publication. For it to stand alone it needs: (i) application to at least two independent published methods (not only the authors' naive PF), (ii) a theoretical statement about what the test detects (particle-support coverage vs likelihood informativeness), and (iii) a false-positive/false-negative analysis (does a method that passes the null always filter? Does a method that fails always prior-hold?). Without these, the null test is a useful component of the current paper but not yet publishable on its own.

## 9. Figures and tables

The manuscript contains two tables (lines 66–68 and 74–78) and one schematic reference to a Figure 3 that is explicitly not generated. No convergence curves, no posterior-trajectory plots, no phase-diagram heatmaps, no real-data visualisations. For a paper whose central numeric claim is "14% convergence in 5000 shots," a convergence curve is table stakes. The tables themselves are sparse — line 66–68 collapses 8 phase-diagram cells into one row, hiding cell-level variation. A PRR paper typically has 4–8 figures; this manuscript has zero generated figures.

## 10. Reproducibility

§8 says "all scripts, results.tsv, figures, pre-registration, and review trail at the accompanying repository." This is the right intent. For a Codebases-track submission the code itself is the artefact and I would want to see the repository URL, a README with a one-command reproduction script, pinned dependencies, and a CI test on the null-hypothesis testbench. None of that is in the manuscript; the repository is referenced but not pointed to. Random seeds for the PF are not reported. The Willow subset filename path (line 56) is given but the exact selection of "one d=5 r01 experiment" is not uniquely determined. Reproducibility claim is incomplete.

## 11. Verdict

**MAJOR REVISIONS.**

For Phys. Rev. Research I lean toward REJECT without the faithful baselines and a stronger positive result. For SciPost Physics Codebases, MAJOR REVISIONS is appropriate — the codebase and null test have value, but the manuscript as written is an interim report, not a completed study.

## 12. Three specific actions before resubmission

1. **Implement at least one faithful baseline** (correlated-pair MLE per arXiv:2511.09491 is the cheapest) and re-run the null test head-to-head; report cell-level results with Monte Carlo error bars from ≥5 seeds. This addresses M1 and M3 together.
2. **Run the calibrated PF to 50 000 shots on the synthetic null test and on d=3/5/7 Willow experiments with bootstrap CIs**, and replace the linear extrapolation in §3.4 with the measured convergence curve. Produce the omitted Figure 3 and at least one convergence-curve figure. Addresses M2, M4, M5.
3. **Decide on one framing and commit**: either (a) SciPost Physics Codebases submission with the retraction table intact, the null test as the headline methodological contribution, and the calibrated PF as reference infrastructure; or (b) PRR submission with the retraction table removed, the diagnosis narrative compressed into §1 motivation, and a positive quantitative result that beats at least one faithful baseline on the null test. The current hybrid does neither well. Addresses §5, §7, and M7.
