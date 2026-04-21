# Phase 3.5 Paper Review (v5) — qec_drift_tracking / paper_v5.md

## 1. One-paragraph assessment

This manuscript proposes a null-hypothesis test for sequential-Monte-Carlo (SMC) noise-model inference on quantum-error-correction (QEC) syndrome streams: initialise the particle filter (PF) with a prior mean 100x below the generator's base rate and ask whether the posterior migrates. A naive independent-Bernoulli SMC fails the test; a calibrated SMC with a pair-correlation likelihood and Laplace-smoothed shot-noise variance passes (about 14% of the prior-to-truth gap closed in 5000 shots). The authors candidly report that the calibrated SMC does NOT beat a sliding-window pseudo-inverse MLE on rate-estimation mean-squared error (MSE) across a 3-seed bootstrap. The paper self-identifies as a SciPost Physics Codebases submission and is unusually transparent: it includes a retraction table of three prior drafts, a test suite that caught a latent sigma^2-floor bug, and an explicit list of what it does and does not claim. As a methodology/infrastructure paper this is a credible and distinctive contribution; as a quantitative claim about SMC superiority it deliberately makes none. My recommendation is MINOR REVISIONS: the scientific content is sound and the honesty is valuable, but several technical items (single-fixture informativeness ratio, cell-indistinguishability scope, missing figures, 3-seed statistics) need tightening before acceptance.

## 2. Strengths (up to 5)

1. **A genuinely useful diagnostic.** The null-hypothesis prior-migration test is simple, cheap, transferable across SMC-for-QEC papers, and addresses a concrete failure mode (prior-holding artefacts) that the authors themselves fell into in v1. This alone is publishable.
2. **The sigma^2-floor bug write-up and its Laplace-smoothing fix.** Section 2.2 and Section 3.5 document a subtle, real pitfall in pair-correlation likelihoods at sparse-fire detectors, with a regression-guarded test. This is exactly the kind of codebase-level contribution SciPost Codebases exists for.
3. **Honest negative result with context.** Section 3.3 reports that sliding-window MLE wins on MSE and then discusses three plausible reasons (initial-condition asymmetry, unweighted lstsq in the pair variant, metric choice) without hiding or overselling any of them.
4. **Test-driven development is not rhetorical.** Twenty-one (or "24-test" in the abstract — see minor concerns) pytest invariants are enumerated with scope, and the sigma^2 bug was actually caught by the suite rather than by a reviewer.
5. **Explicit retraction table.** Section 6 lists each withdrawn claim from v1-v3 with its v4 status; this is unusually good scientific hygiene for a preprint line.

## 3. Major concerns

**M1. The informativeness ratio (1.65x) is a single-fixture, single-particle-pair measurement.** Section 3.2 already concedes this and flags a 1.3-2.5x likely CI as open work, but the 1.65x number appears in the abstract, Section 1.2, and Section 7 without the single-fixture caveat attached. Either (a) run the multi-fixture sweep before submission and report the CI, or (b) strip the bare "1.65x" from the abstract / conclusion and replace with "measurably (~1.3-2.5x estimated) more informative per shot." As currently written, the abstract oversells what Section 3.2 honestly walks back.

**M2. Three seeds is thin for a bootstrap CI claim.** Section 3.3 reports 1000 bootstrap resamples over 3 seeds. A bootstrap over N=3 is resampling the same three points; the CIs in the MSE table for the calibrated SMC row have width ~4% of the mean, which seems implausibly tight given the seed count. Please either (i) increase to >=10 seeds, or (ii) report the raw per-seed MSEs and explicitly flag that the interval is a bootstrap over N=3 (which is a known weak estimator). The abstract says "3-seed bootstrap Monte Carlo" which is acceptable only if honestly framed — currently it is not distinguished from a 100-seed study.

**M3. Cell indistinguishability is a methodology-scope issue, not just a footnote.** Section 3.4 reports that all four phase-diagram cells collapse to identical 3-sig-fig numbers, and attributes this to drift magnitude being below prior-migration cost. This means the "phase diagram" framing from earlier drafts is entirely unsupported by this data. The paper should state more prominently — probably in Section 1.2 under "does not claim" — that no regime-dependence claim is made at all on this benchmark. The current phrasing in Section 3.4 ("not supported by this data at T<=5000 and sigma_log>=2.0 prior") is correct but buried.

**M4. The "strict-filtering threshold" of >=5% gap-closed is asserted without justification.** Section 2.1 declares 5% as "defensible as noise-dominated below 5%" but does not derive or cite this. For a null-hypothesis test proposed as a community diagnostic, the threshold choice needs either a short derivation (what is the expected posterior-mean random-walk spread under the null?) or a calibration experiment (null simulations with prior-at-truth to measure the noise floor). Without it, 14% could be 2.8 sigma or 0.8 sigma and the reader cannot tell.

**M5. No figures.** For a SciPost Codebases paper centred on a diagnostic test, the absence of figures is a real weakness. See Section 8 below.

## 4. Minor concerns

- **Abstract/Methods mismatch on test count.** Abstract: "24-test pytest regression suite." Section 2.5: "21 passing tests." Reconcile.
- **Abstract says "Phase 3 draft v4"** (line 7 editorial comment) but the filename and §6 refer to this as v4/v5. Strip internal-phase bookkeeping from the published manuscript.
- **Section 1.1 footnote "125 nats on a 10-detector H"** — please state T (shots) used for this number; it is not the same fixture as Section 3.2.
- **Section 2.4 `20x50 H matrix with 15% density`** — is this also the Section 3.2 fixture (which says "10-detector x 30-error-mechanism")? If not, state both explicitly; currently the reader must guess.
- **Section 2.3 "lstsq variant is a conservative lower bound on what a proper likelihood MLE could achieve"** — this is a conjecture, not a theorem. Soften to "expected to be a conservative proxy" or demonstrate.
- **Section 3.3 baseline MSE values** are reported as point estimates with no CIs, unlike the SMC row. Match the treatment.
- **Section 4.3 venue listing ("SciPost Physics Codebases is the cleanest fit")** is editorial meta-commentary; remove from the published version.
- **Section 5 "Per v3 §5. Unchanged."** Not acceptable in a standalone paper. Inline the related work.
- **Data availability** references `paper_review_v1.md`, `paper_review_v3.md` — these are internal review artefacts; either expose them as supplementary material or drop.
- **Willow data at Zenodo 13273331** — but Section 1.2 explicitly states no Willow claims are made. Why is this cited?
- **Line 7 and Section 6 heading number** — "v4" appears in the editorial note but the filename is `paper_v5.md` and the review is v5. Freeze the version number.

## 5. The null-hypothesis test as a standalone contribution

Yes, this is publishable at SciPost Physics Codebases on its own, without beating baselines on MSE. SciPost Codebases' mandate explicitly includes methodology and reproducibility artefacts; a diagnostic test that (a) caught a prior-holding artefact the authors themselves shipped, (b) is trivially portable to other SMC-for-QEC papers, and (c) comes with a regression-guarded test suite, fits squarely. The contribution is in the same spirit as "posterior predictive checks" in the Bayesian-stats literature: a cheap, universal sanity check. The paper does need to lift the null-test threshold justification (M4) to make the test self-contained.

The pair-correlation + Laplace-smoothing calibration recipe is a second, complementary codebase-level contribution. Together they justify the submission independently of MSE ordering.

## 6. Retraction transparency

The retraction table STRENGTHENS the submission at SciPost. SciPost's editorial culture rewards candour — the journal runs open peer review and publishes referee reports. A preprint line that openly withdraws three prior claims (v1's 24/24 cells, v2's "clean negative result," v3's implied MSE win) and maps each to its current status demonstrates exactly the kind of self-correcting discipline SciPost editors like to see. Far from flagging the paper as unstable, it signals that the authors have done three independent audit passes and know where every claim came from. I would keep the table prominently placed (as it is, §6) and cross-reference it from the abstract, which currently only says "a candid retraction table of three prior draft claims" — consider adding one sentence in Section 1.1 pointing the reader directly at it.

One caveat: SciPost editors may ask whether the prior drafts were posted to arXiv or only internal. If only internal, the word "retracted" is slightly overloaded — "withdrawn prior-internal-draft claims" is more accurate. Clarify.

## 7. Negative-result framing

The negative-result framing is acceptable and does NOT cross into "why submit at all" territory, but only because the paper does not rest its case on the negative result. The contribution is not "SMC loses to MLE" (which alone would be a thin paper); it is "here is a diagnostic that every SMC-for-QEC paper should run, here is the calibration recipe that makes an SMC pass it, and here is the surprising fact that passing the null test does not translate into MSE wins over a trivial baseline on this benchmark." That is three contributions stacked, two positive and one honest-negative.

If the paper were re-framed around the negative result alone ("SMC doesn't work for QEC drift") it would indeed be thin and arguably misleading, because Section 3.3 flags several reasons the MSE ordering could reverse (matched prior, proper weighted MLE, LER metric). The current framing — "null test passes, MSE doesn't, and here is why neither fact is the final word" — is scientifically appropriate. Keep it.

One small suggestion: the abstract says "an honest negative result of immediate diagnostic value" which is slightly awkward. The diagnostic value is the null test, not the MSE loss. Consider rephrasing: "the calibrated SMC does not beat sliding-window MLE on MSE in this regime — a bounded negative result that sharpens the operating envelope rather than closing the question."

## 8. Figures (none referenced)

The manuscript references no figures. For a SciPost Codebases paper this is a real gap. At minimum I would ask for:

1. **Prior-to-truth migration trajectory.** Posterior mean vs shot-index for (naive SMC, calibrated SMC, prior-at-truth control), with the 5% and 14% gap-closed horizontal lines. This is the single figure that makes the null test concrete.
2. **MSE vs T for the three methods** in Section 3.3, with the 3-seed spread shown as a shaded band.
3. **Log-likelihood gap (truth vs 100x-wrong) as a function of batch size**, to justify the 1000-shot window choice and make the 1.65x ratio visible.

A schematic of the pair-incidence matrix M and the Laplace-smoothing pathway would help readers reproduce Section 2.2.

## 9. Reproducibility

The reproducibility story is strong on process and thin on artefact binding:

- **Process:** TDD suite with 21 (or 24) tests, Laplace-smoothing regression test, explicit DEM/H fixture tests — excellent.
- **Artefact binding:** "Data and code availability" points to "the accompanying repository" without a URL, DOI, or commit hash. For SciPost Codebases, a Zenodo snapshot or a frozen GitHub tag with a DOI is expected. The Willow Zenodo 13273331 reference is the only concrete external identifier and it is not actually used for any reported result.
- **Environment:** No Python version, no dependency pin, no OS, no runtime budget stated. `pytest tests/` "runs green on every commit" — which commit? On what environment?
- **Seeds:** 3 seeds for the bootstrap (M2). The seeds themselves should be listed (e.g., `seeds = [0, 1, 2]`).

Before acceptance, add: repository URL + commit hash + DOI, Python version, seed list, hardware (CPU/GPU) note, and runtime per cell.

## 10. Verdict

**MINOR REVISIONS.**

Rationale: the scientific content is sound, the contributions are well-identified and independently justifiable (null-test diagnostic, Laplace-smoothing recipe, TDD suite, honest negative result), and the retraction discipline is exemplary for SciPost's editorial culture. The remaining issues are largely presentation, scoping of claims, and reproducibility metadata — none are structural. M1 (single-fixture ratio), M2 (3-seed bootstrap framing), M3 (cell-indistinguishability scope), M4 (null-test threshold justification), and M5 (figures) are the blocking items; all are tractable within a minor-revision cycle without new experimental work (M1 and M4 may require short additional runs but nothing the existing codebase cannot do overnight).

## 11. Signoff

Once the minor revisions M1-M5 are addressed (tighten the 1.65x informativeness framing, honestly frame the 3-seed bootstrap or extend to >=10 seeds, lift the cell-indistinguishability scope statement into Section 1.2, justify the 5% null-test threshold, and add the three core figures), the paper is acceptable for SciPost Physics Codebases. No new experiments or structural rewrites are required. The scientific content, retraction discipline, and codebase-level contributions clear the bar for this venue.

NO FURTHER BLOCKING ISSUES
