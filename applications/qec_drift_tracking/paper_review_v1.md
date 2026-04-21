# Phase 3.5 Paper Review — qec_drift_tracking / paper.md

## 1. One-paragraph assessment

The manuscript proposes an open-source particle-filter (PF) "infrastructure" for online QEC noise-model inference, together with lightweight reimplementations of two published baselines (arXiv:2511.09491 sliding-window MLE, arXiv:2406.08981 static Bayesian TN+MCMC) and a loader for the Google Willow Zenodo 13273331 dataset. The authors report a 24/24 strict-win synthetic phase diagram and a single d=5 Willow comparison in which the PF achieves the lowest MSE vs a published reference decoder error model (DEM). To their credit, the authors prominently disown these results, explicitly listing eight open-validation items (§4.3) that must close before the quantitative claims can be interpreted as real. Unfortunately, that very list describes concerns which — if taken seriously — imply the central measurements in §3 are presently uninterpretable: a Gaussian surrogate likelihood that the authors themselves judge "may not be doing real Bayesian work," baselines that are admittedly weakened vs the published algorithms they ostensibly benchmark, and a real-device comparison against a published prior DEM rather than device-measured ground truth. The framing as "honest infrastructure" is admirable but, as submitted, the paper lacks any quantitative claim that survives its own caveat section. My recommendation is **MAJOR REVISIONS**, with SciPost Physics Codebases as the more defensible venue.

## 2. Strengths

- **Exceptionally transparent limitations section.** The paper pre-empts almost every technical objection an SMC-literate reviewer would raise, explicitly naming the Gaussian-surrogate pathology, the prior-holding artefact risk, and the baseline-fidelity gap.
- **Real-device data is used, not just simulation.** Use of the Google Willow Zenodo 13273331 release on an actual d=5 surface-code experiment is non-trivial and lifts the paper above purely synthetic drift studies.
- **Well-scoped related-work section.** The three relevant 2024–2025 preprints (arXiv:2511.09491, 2406.08981, 2504.14643), Riverlane LCD (Nat. Commun. 2025), and Willow below-threshold (Acharya et al. 2024) are all identified and correctly positioned.
- **Pre-registration and fairness fixes are documented.** §2.4 explicitly lists the uniform-prior fix and the decoupling of the PF drift kernel from the synthetic generator, which is unusual and welcome rigour.
- **Useful open-validation checklist.** The eight items in §4.3 are individually actionable and constitute a serviceable roadmap for a follow-up paper.

## 3. Major concerns

**M1. The Gaussian surrogate likelihood very likely invalidates the PF as "Bayesian filtering."** §2.1 reports `log L(θ) ≈ -||Hθ - s||² / (2·0.5²)` with expected `Hθ ≈ 10⁻³` but observations `s ∈ {0,1}`. The authors correctly note this means the squared error is dominated by the ±0.999 residual rather than by θ. Consequently the reported PF "wins" cannot be attributed to Bayesian updating and may simply reflect a method that shrinks toward its prior.
*Fix:* Replace the surrogate with the stated exact Bernoulli likelihood (§4.3 item 2) BEFORE resubmission, rerun both synthetic and real-device experiments, and report whether the ordering is preserved. This is a one-function change and cannot justifiably be deferred.

**M2. The 24/24 strict-win may be a prior-holding artefact, not filtering.** §3.1 caveat explicitly concedes that the PF posterior mean ≈ 1e-3 ≈ generator base rate; §3.2 concedes that the real-device PF posterior mean (1.30×10⁻³) is closer to its own prior (1.00×10⁻³) than to the reference (3.53×10⁻³). This is exactly the signature of a filter that isn't filtering.
*Fix:* Run the §4.3 item 1 null-hypothesis test (PF with a mis-specified 1e-5 prior) and either demonstrate the PF recovers, or report the collapse and rewrite §3 to describe this as an infrastructure paper without any quantitative MSE claim.

**M3. Baselines are admittedly not faithful reimplementations of the cited papers.** §2.2 concedes the single-detector pseudo-inverse attribution is "a conservative lower bound" on arXiv:2511.09491 and arXiv:2406.08981. In peer review this is not acceptable: comparing a named competitor's algorithm against a deliberately weaker reimplementation and reporting "PF wins" is misleading regardless of caveats.
*Fix:* Either (a) implement the pair-correlation MLE and a minimally faithful TN+MCMC (§4.3 items 3–4) before resubmission, or (b) remove the method-name labels from Tables in §3 and call them "pseudo-inverse least-squares" and "Beta-conjugate per-edge," with explicit statement that these are NOT the published algorithms.

**M4. "MSE vs reference DEM" is not a validity metric.** §3.2 uses the published `correlated_matching_decoder_with_si1000_prior/error_model.dem` as the comparator. This DEM is a published prior, not device truth. A method whose posterior mean coincidentally lands near that prior scores low MSE without actually being more accurate.
*Fix:* Report logical error rate (LER) under decoding with each method's learned rates — this is the operationally relevant metric and requires only a PyMatching re-weighting pass, which the paper already says is within reach. Alternatively, use a per-detector empirical event frequency on a held-out shot subset as ground truth.

**M5. n=1 real-device experiment with no bootstrap and 10% of shots.** §3.2 analyses 5 000 of 50 000 shots from a single d=5, r=01, X-basis experiment at one physical location. No confidence intervals, no cross-experiment replication, no seed variation. The authors acknowledge this at §4.3 items 6–7 but still report point estimates with three significant figures in Table §3.2 as if they were measurements.
*Fix:* Run the full 50 000 shots, bootstrap-resample 1 000× over shot subsets, and report medians with 95% CIs. Extend to at least 3 `d5_at_qX_Y` positions so the ordering can be called replicable.

**M6. The LCD-as-1-particle-SMC conjecture is advertised in the abstract but unsupported.** The abstract lists the unification as one of four contributions (implicitly, by positioning against "production adaptive decoder"), §4.2 concedes none of the three required ingredients is in the paper, and §5.3 reiterates the conjecture.
*Fix:* Either produce a sketch proof with explicit LCD update rule and N=1 SMC step equivalence, or remove the conjecture from the abstract and §1 and demote it to a "future work" footnote. Advertising an unproven unification in the abstract is inappropriate.

**M7. Degenerate PeriodicDEMRefit baseline.** §2.2 admits the cadence is 3.6M shots on T=2000 synthetic runs, so this baseline never fires. Reporting it in comparison tables (implicitly through the sweep framing) inflates the apparent breadth of the benchmark.
*Fix:* Remove this baseline from the paper, or rerun the synthetic sweep with a sensible cadence (e.g., cadence = 100 shots) so it actually produces updates.

## 4. Minor concerns

- The abstract lists "arXiv:2504.14643 detector-error-model estimation" as a third online-estimation preprint and §1.1 mentions "per-edge DEM estimation," but this baseline is never actually implemented or compared. Clarify.
- §1.3 says "PF strict-wins 24/24" and §3.1 repeats it; this is three words from being overstated. Prefer "has lower MSE than both baselines in all 24 synthetic cells" — the word "wins" invites scrutiny.
- §2.3 says "1080 d=5 experiments available; this paper analyses one." This is jarring and undercuts the claim to be an infrastructure paper for the Willow dataset.
- §3.3 wall-clock (4.2 ms/shot) on RTX 3060 is reported without comparator baseline wall-clock. The paper would be stronger if all three methods' timings were tabulated.
- §4.4 mentions "proposal_v3" and PRX Quantum by name — venue pivots should not be litigated inside the paper.
- §5.4 cites "arXiv:2512.10814 (identified in Phase 0 scoop scan — direct baseline to beat in future submission rounds)" — internal project language should be scrubbed.
- The acknowledgements reveal the Phase 2.75 reviewer is a "blind-SMC-expert-simulation," i.e., an automated process. A human reader may find this disqualifying; consider rephrasing.
- Stim 1.16-dev is a development version; please pin to a released tag for reproducibility.
- Figure captions are not shown in the manuscript body; only filenames appear. Full captions required.
- §2.1: "Rao-Blackwellisation-ready" is claimed but no Rao-Blackwellised results are shown. Either demonstrate or describe as "Rao-Blackwellisable."

## 5. Is the "honest infrastructure with published open-validation list" framing defensible?

Partly. Transparency is a genuine strength, and there is modest precedent at SciPost Physics Codebases for infrastructure/software submissions that ship with test-coverage lists and known-limitation sections — the venue's scope explicitly welcomes "reusable scientific software." However, SciPost Codebases still requires that the software does what it claims and is validated on the target problem. A codebase paper that says "our main likelihood is a surrogate we believe is broken, our baselines are admittedly weaker than the published ones, and our benchmark metric (MSE vs a published prior) is not a ground-truth metric" is not yet a validated codebase — it is a scaffold. Phys. Rev. Research is even less accommodating: it requires a defensible quantitative finding, and the caveat section effectively withdraws every quantitative finding in §3.

There IS precedent for "infrastructure with open items" submissions — e.g., the DeepMind/Tweedledum/Stim-adjacent release papers — but in each case the core artefact has been demonstrated to work on at least one non-trivial task before publication. Here, §4.3 items 1 and 2 are small enough (one rerun and one likelihood swap) that withholding them is hard to defend. The framing becomes defensible only after items 1 and 2 are closed; items 3–8 could legitimately remain open.

## 6. Readiness for Phys. Rev. Research vs SciPost Codebases

**SciPost Physics Codebases is the better fit.** The artefact-centred framing, the public validation checklist, and the emphasis on reusable scaffolding match that venue's remit. However, even SciPost Codebases will likely require items 1–2 of §4.3 to be closed (null-hypothesis test and exact-Bernoulli likelihood) before the code can be said to "work." Expect MAJOR REVISIONS there too.

**Phys. Rev. Research is not yet viable.** PRR is a results venue, and the paper has no results that survive its own caveat list. It would be viable after items 1, 2, 4 (faithful static Bayesian), and 6 (bootstrap CIs on full 50 000 shots) close, plus LER-under-decoding as the headline metric.

Neither venue is likely to accept in the current state without substantial revision.

## 7. Self-flagged caveats audit

The caveat section is unusually thorough and pre-empts: Gaussian-surrogate pathology, prior-holding artefact, baseline fidelity, reference-DEM-is-not-truth, small-n real-device, Willow per-run timestamps, LCD unification unproven, PF wall-clock insufficient for FTQC.

**Concerns the caveats DO NOT pre-empt:**
1. **No LER measurement.** The paper never evaluates whether learned rates actually reduce decoding error, which is the whole operational point of online noise estimation. A reviewer will ask "does the PF produce a better decoder?" and the paper has no answer.
2. **Fixed random H matrix in §3.1.** The synthetic sweep uses "a fixed random 20×50 H matrix" — there is no sensitivity analysis over H, which could change the ordering.
3. **No cross-seed variance on synthetic sweep.** The 24/24 cells are each a single seed. Even without the null-hypothesis concern, variance bounds are missing.
4. **Shot subsampling methodology.** "5 000 of 50 000" — are these the first 5 000? Random? Consecutive? This matters for drift estimation and is unspecified.
5. **No check that the PF's OU kernel (τ=3600 s, σ=0.1) is consistent with the 1-round r01 Willow experiment's timescale.** For a single-round experiment, "drift" within the run is ill-defined.
6. **No null baseline.** The obvious null — constant prior, no filtering — is missing. This would resolve whether PF ≈ prior is trivially optimal on this data.

## 8. Figures and tables

Only two figures are referenced — `fig1_phase_diagram.png` (strict-win heatmap) and `fig2_mse_comparison.png` (log-log MSE scatter). Both filenames but no captions. Table in §3.1 is qualitative (check-marks only); please report actual per-cell MSE values so the magnitude of the "wins" can be assessed — at present the table has zero quantitative content. Table in §3.2 has three significant figures on a single-seed, sub-sample run — downgrade precision or add CIs.

## 9. Reproducibility

Data and code availability section names the files but there is no DOI, no Zenodo archival of the authors' code, no commit hash, no environment lockfile. Stim is pinned to "1.16-dev" (a dev build). NumPy 2.4 and SciPy 1.17 are listed but these versions do not yet exist as of my knowledge cutoff — please double-check. The Zenodo 13273331 dataset is correctly cited. Pre-registration `proposal_v3.md` and methodology review `methodology_review.md` are referenced but not archived — these should be in a supplementary Zenodo drop, not local filenames.

## 10. Verdict

**MAJOR REVISIONS.**

## 11. Three specific actions before resubmission

1. **Close §4.3 items 1 and 2 (null-hypothesis test with 1e-5 prior; replace Gaussian surrogate with exact Bernoulli likelihood) and rerun both §3.1 and §3.2.** Report whether the ordering survives. This is the single most important action; without it the paper has no defensible quantitative claim.
2. **Replace "MSE vs reference DEM" with "logical error rate under re-weighted decoding" as the primary metric** (PyMatching re-weighting on held-out shots). Supplement with bootstrap CIs from the full 50 000 Willow shots across at least three `d5_at_qX_Y` positions.
3. **Either implement the pair-correlation MLE and a minimally faithful TN-or-MCMC static Bayesian baseline, or rename your baselines to remove any implication that they reproduce arXiv:2511.09491 and arXiv:2406.08981.** Also: remove the LCD-as-1-particle-SMC unification from the abstract and demote it to future work, and drop the degenerate PeriodicDEMRefit baseline.
