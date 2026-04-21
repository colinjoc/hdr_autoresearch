# Phase 2.75 Methodology Review (v4) — qec_drift_tracking

Blind review by a fresh reviewer. Sources: paper_v4.md, methodology_review.md, particle_filter.py, baselines.py, phase_diagram.py, e03_null_hypothesis.py, e04_bootstrap_sweep.py, tests/ (5 files), results.tsv (127 rows).

## 1. Did v4 close the three v3 actions?

**Action 1 — faithful correlated-pair MLE (baselines.CorrelatedPairMLE).**
PARTIAL. `baselines.py:52–104` is *not* a faithful reimplementation of arXiv:2511.09491's MLE. It is a **pair-incidence linear least-squares** estimator: build M[pair(i,j), edge e] = H[i,e]·H[j,e] (line 77), compute empirical covariance c = ⟨s_i s_j⟩ − ⟨s_i⟩⟨s_j⟩ (line 93), solve `p_edge = lstsq(M, c)` (line 98) and clip to [1e-8, 0.499] (line 99). This differs from the paper's MLE in three substantive ways: (a) there is no likelihood function — it is a moment-matching regression on the *linearised-covariance-at-low-rate* approximation noted in the code comment `C_ij(θ) ≈ Σ_e H_{ie} H_{je} θ_e` (particle_filter.py:114–116), dropping all O(θ²) terms that the true MLE keeps; (b) it uses unweighted lstsq rather than inverse-variance-weighted or iteratively-reweighted least squares, so pairs with high shot-noise variance have equal influence as low-variance pairs; (c) there is no non-negativity constraint beyond post-hoc clipping (line 99 comment explicitly prefers `lstsq + clip` over NNLS "for speed"). The author acknowledges (a) in the docstring at baselines.py:56 ("higher-order corrections O(θ²)"). Calling this "faithful" in paper §2.3 is an overclaim; "linearised pair-covariance least-squares" would be accurate. It is however STRICTLY CLOSER to 2511.09491 than SlidingWindowMLE's per-detector pseudo-inverse, so action is *partially* addressed.

**Action 2 — 5-seed bootstrap convergence curves reduced to 3 seeds × 4 cells × T=5000 × 3 methods.**
REASONABLE COMPROMISE given the timebox, BUT a 3-seed bootstrap produces weak CIs: the bootstrap resamples 3 values with replacement, so the effective number of distinct means is C(3+3-1, 3) = 10 multiset outcomes, most of which are clumpy. The CIs reported in paper §3.3 (e.g. `[8.34, 9.25] × 10⁻⁷` at T=1000) are wide, but the ORDERING SW < PF < CP is confident because the inter-method gap (~1.5× MSE) is much larger than any credible intra-method CI. That said, the paper should flag n=3 seeds explicitly in §3.3 and the 3-seed limitation should appear in §1.2 "does not claim". Also, `e04_bootstrap_sweep.py:38` comment `"Naive PF dropped — its per-shot cost dominates"` drops the naive-PF comparison in the bootstrap; this is defensible if the null-test failure is already established (it is, §3.1) but the paper should explicitly say "naive PF not bootstrapped because it fails the null test at all seeds; MSE computation is moot".

**Action 3 — committed null-hypothesis-test framing.**
CONFIRMED. §1.1 and §1.2 commit cleanly; §6 retraction table is honest about v1–v3 retractions; paper does *not* hedge back into PF-advantage claims. The framing is followed through consistently. Remaining hedge: §3.2 reports a "1.65× informativeness ratio" as a contribution (see §6 below); §7 conclusion re-lists it as "concrete contribution". If the paper is truly a null-test methodology paper, that number is at most a supporting anecdote, not a contribution.

## 2. The σ² Laplace-smoothing fix

**Bug diagnosis: correct.** At particle_filter.py:137 `sigma2_pair = (p_i_smooth[:,None] * p_i_smooth[None,:]) / n_batch`. Without Laplace smoothing, p̃_i = 0 for zero-firing detectors → σ² = 0 → any non-zero (C_emp − C_pred) gets divided by a floor (previously 1e-10) → log L at wildly-wrong particles can dominate. Swapping to p̃_i = (k+1)/(n+2) gives a floor of 1/(n+2) ≈ 1e-3 for n=1000, which is physically reasonable as a "rarely-observed-fire" uncertainty.

**Fix sufficiency: partial.** The bug class is broader than Laplace smoothing covers. Specifically:
- **Regime A — high-rate (p ≈ 0.1+).** Laplace smoothing (k+1)/(n+2) under-estimates σ² when p is large because p(1-p) ≠ p². At p=0.5, true variance is 0.25 but the formula gives p²·p² = 0.0625 — a 4× underestimate. No test covers p > 0.01.
- **Regime B — finite-sample bias in covariance.** The empirical C_emp is biased by -p_i·p_j/n at finite N; the predicted C_pred does not account for this bias. At low rates the bias is O(p²/n), swamped by shot noise, but at higher rates or small n_batch (code uses batch_size=1000, which is ok; smaller would not be) this would matter.
- **Regime C — correlated higher-order terms.** The C_pred = H diag(θ) H^T formula drops O(θ²) cross-edge terms (paper §2.2 explicit; baselines.py:57 explicit). When any single edge rate exceeds ~10⁻¹ the dropped terms dominate. The current clip at θ ≤ 0.499 (particle_filter.py:70) permits this regime. Tests never probe it.
- **Regime D — numerical underflow in log_lik differences.** When n_batch · (C_emp − C_pred)²/σ² exceeds ~700, `np.exp(self.log_w)` in particle_filter.py:91 underflows even after lw_max subtraction on line 89. For N=500 particles and pathological spreads this could silently zero out most weights. No test covers this.

Tests `test_pair_correlation_likelihood_is_informative` (test_particle_filter.py:41–78) assert only the specific regression that triggered the v4 fix (1 nat at θ=1e-3 vs 1e-5). They do not cover A–D.

## 3. Test coverage

Audit of 21 tests across 5 files:

**Meaningful invariants (14 of 21):**
- `test_inject_drift_zero_amplitude_constant` — forces σ=0, asserts exact base rate. Non-trivial.
- `test_inject_drift_deterministic_same_seed` / `different_seeds_differ` — reproducibility checks, correct.
- `test_pair_correlation_likelihood_is_informative` — *the* TDD test; asserts log L at truth > log L at 100×-wrong by ≥ 1 nat. Would catch the σ² regression. Good.
- `test_pair_correlation_is_more_informative_than_independent_bernoulli` — ratio test with 1.2× margin; genuinely stresses the calibration decision.
- `test_pair_correlation_posterior_moves_toward_truth` — 5 % regression guard for the headline "14 % gap closed". Good.
- `test_correlated_pair_mle_incidence_matches_definition` with `tiny_css_H` — hand-computed expected matrix [[0,1,0]]; exact correctness check.
- `test_dem_to_pcm_hand_built` — 2-detector DEM with known structure; asserts H[i,j], O[i,j], rates entry-by-entry. Correct TDD style.

**Shape/tautological (5 of 21):**
- `test_drift_kernel_propagate_shape` — shape + dtype only.
- `test_pf_init_particle_shape` — shape + "positive" + "approximately prior mean" (rel=0.5, very loose).
- `test_sliding_window_mle_posterior_shape` — shape only.
- `test_correlated_pair_mle_incidence_matrix_shape` — shape + sparsity only.
- `test_dem_to_pcm_dtypes` — dtype only.
These pass if the code runs; they do not verify logic. Keep them as smoke tests but do not count them toward the 21-test contribution claim in paper §2.5.

**Weak invariants (2 of 21):**
- `test_sliding_window_mle_recovers_base_rate` — asserts only `post_mean < 1e-1`. Base rate is 1e-3; a 100× over-estimate would still pass. The test docstring acknowledges "overestimates by 3-10× in low-rate regime, documented in paper_v3 §3.3" — but then does not test that documented 3-10× band. Tighten to `post_mean in [1e-4, 1e-2]`.
- `test_correlated_pair_mle_recovers_base_rate` — same weakness: only `0 < post_mean < 1e-1`. Given this is the "faithful" baseline it should recover 1e-3 within 10×.

**Missing tests:**
- No test that `ParticleFilter.step` resampling branch (lines 95–100) actually fires when ESS drops. The `if ess < 0.5*N` branch may never execute in unit tests.
- No test that the `self._window = self._window[self.batch_size // 2:]` line 83 (50 % window overlap) behaves correctly across batches — a regression here would silently change the effective batch size.
- No test of drift-tracking on a non-stationary stream (all "recovery" tests use amplitude=0, i.e. stationary). The filter's *drift-tracking* capability is untested.
- No test of `CorrelatedPairMLE` recovering rate under drift (all fixtures use stationary streams).
- No end-to-end MSE-ordering test that encodes the paper's §3.3 finding "SW < PF < CP". A regression that flipped this ordering would not be caught.
- No test of `e04_bootstrap_sweep.run_cell_multiseed` determinism — the bootstrap is a numerical experiment and should be reproducible.

## 4. "Cell indistinguishability" (§3.4) — real or bug?

Tracing results.tsv rows 92–127 (E04, 3 seeds × 4 cells × 3 T-snapshots): yes, all four (τ, σ) cells are numerically near-identical at the same (seed, T). Example, seed=42, T=5000: pf_cal_mse = 9.2481e-07, 9.2487e-07, 9.2480e-07, 9.2480e-07 across cells. CAUSE: **the MSE is dominated by the PF-posterior-vs-truth gap, not by the drift.** pf_cal_mean ≈ 1.49e-4 (reported in note column line 92), truth ≈ 1e-3, so (posterior − truth)² ≈ (8.5e-4)² ≈ 7.2e-7 per edge — that is the entire MSE budget. Actual drift-induced gt variation contributes ~(σ·base_rate)² = (0.2·1e-3)² = 4e-8 at worst — two orders of magnitude below the prior-mis-specification floor.

There is also a plumbing contribution: `e04_bootstrap_sweep.py:41–44` uses the same `seed` for rng, H construction, AND `inject_drift`. The OU noise stream inside `inject_drift` (`phase_diagram.py:47` `rng.normal(0, drift_amplitude * np.sqrt(shot_dt_s / drift_timescale_s), size=E)`) draws the SAME underlying normals across cells and just scales them by different (σ, τ) prefactors. Across cells, `edge_fires` on line 53 is a Bernoulli draw whose threshold differs only slightly, so events often agree. Combined with the posterior-gap-dominates effect above, the cells collapse to 3-sig-fig identity.

**Verdict: (a) true finding — drift at T=5000 is too small to distinguish these cells against a mis-calibrated PF — but (b) also reflects a methodological problem.** The "phase diagram" never tests what it claims to test. The paper §3.4 is right to flag indistinguishability, but should be explicit that the MSE is dominated by prior-truth gap, not drift dynamics. A proper phase-diagram experiment would use a well-calibrated PF (prior = truth) and measure drift-tracking RMSE against moving gt — that would resolve to actually-different cells.

## 5. SW-MLE beating SMC and faithful CorrelatedPairMLE

From results.tsv E04 (rows 92–127, 3 seeds × 4 cells × T=5000): pf_cal_mse ≈ 9.1e-7, sw_mse ≈ 6.0e-7, cp_mse ≈ 1.7e-6. The SW-MLE (pseudo-inverse, baselines.py:39–46) wins despite being docstring-declared "conservative reimplementation" (baselines.py:23).

**Is this trustworthy? Qualified yes, with caveats:**

(a) **The "win" is partially an artefact of metric choice.** SW-MLE's pseudo-inverse estimates the per-edge marginal rate profile from window-averaged detector marginals; it produces an estimate `p_edge` that is a smoothed average (of base rate 1e-3). If the ground-truth drift has small amplitude (σ ≤ 0.2), the truth is also approximately-stationary at 1e-3, so SW-MLE's output is very close to the time-average of gt. The SMC is constrained by its wide prior (`prior_std_log=2.0`, particle_filter.py:43) centered at 1e-5, and its posterior at T=5000 has only reached 1.49e-4 — much further from truth than SW's 1e-3-ish average. MSE vs instantaneous gt is dominated by this stationary offset, not by drift tracking skill.

(b) **The SMC is handicapped by initial-condition mismatch that SW-MLE doesn't have.** SW-MLE starts at its first window and computes the empirical rate directly. The SMC starts 100× below truth (prior=1e-5) and has to migrate through particle resampling. The 14 %-gap-closed finding is consistent with "SMC moves but slowly"; SW-MLE gets the right order of magnitude immediately from the first window's data. A fair comparison would either (i) give SW-MLE the same mis-specified initial condition or (ii) give the SMC a correctly-specified prior centered on 1e-3 with std_log=0.5.

(c) **The CP-MLE underperformance is real and worth investigating.** CP-MLE's linearised covariance drops O(θ²) terms and uses unweighted lstsq — both identified in §1 Action 1 above. It may be that the unweighted lstsq amplifies noisy zero-count pairs (D·(D−1)/2 = 190 pair equations in a 50-edge system is over-determined, so noisy rows can bias the solution). Inverse-variance-weighted lstsq would likely close most of the CP-vs-SW gap.

(d) **The finding is still a publishable result of the METHODOLOGY paper**, because it demonstrates that simple baselines can outperform more elaborate methods in the null-test-passing-but-prior-mis-specified regime. This is informative for the field. But the paper should NOT over-claim: §4.1 "Sliding-window MLE with pseudo-inverse attribution is a surprisingly strong baseline" is fine; implying this is a fundamental ordering would be wrong.

## 6. The 1.65× per-shot informativeness ratio

Source: test_particle_filter.py:119 comment "Empirical ratio on this fixture: ~1.65× (pair=207 nats vs naive=125 nats at T=500)". Fixture: `small_H` = 10×30, seed=42, σ=0, T=500 (stationary).

**Single-fixture ratio is NOT a defensible quantitative claim.** The ratio depends on:
- H density (current 15 % — at 5 % or 30 % the pair-correlation informativeness would change materially because it's driven by the number of shared edges per detector pair).
- H shape (10×30 — larger H increases pair count quadratically, making pair-correlation more informative per shot).
- Stationary rate value (1e-3 — at 10⁻² the per-shot Bernoulli signal strengthens and the ratio likely compresses toward 1).
- Batch size (500 — pair-correlation benefits from batching, independent-Bernoulli does not).

The paper reports 1.65× as a single number in §3.2, §7, and in the abstract. This is at best a point on a function of (H, p, T, batch). A defensible claim would be: "On a 10×30 H at p≈1e-3 and T=500, pair-correlation is 1.65× more informative than independent-Bernoulli; the ratio depends on H-shape, density, rate, and batch size and is sensitive to all four". Or: run the ratio on 5–10 (H, seed) fixtures and report mean ± std. The test at test_particle_filter.py:123 already asserts ratio > 1.2, so a multi-fixture variant is a one-line change.

**Action required**: either de-emphasise the 1.65× number (move to a "details" appendix), or run multi-fixture and report with CI. As currently framed, a reviewer will call this a brittle anecdote.

## 7. Honest-framing audit

Paper §1.2 "does claim / does not claim" is unusually prominent — but is it defensive, or appropriate for SciPost Codebases?

SciPost Physics Codebases explicitly asks for: (i) code as primary artefact, (ii) reproducibility, (iii) concrete methodological contribution, (iv) honest limitations. The "does not claim" list in §1.2 is consistent with (iv) and directly addresses the v3 reviewer's action. For SciPost specifically this is *defensible and expected*, not defensive. Compare SciPost Codebases published examples (Stim, PyMatching): all include explicit "out-of-scope" sections.

However, there are two framing issues:

(a) **The retraction table (§6) and the retraction subsection (§1.3) are redundant with each other.** §6 is a cleaner summary. Remove §1.3's retraction table and keep only §6, or vice versa.

(b) **The abstract is too long.** ~250 words and dense. SciPost standard is 150–200 for methodology abstracts. Condense by removing the σ²-bug mention (leave for §3.5) and the 1.65× ratio (leave for §3.2).

(c) **Opening paragraph is meta ("This is a methodology paper..."). SciPost Codebases reviewers expect a one-sentence motivation, not a framing-commitment statement.** Rewrite the italic preamble into the first sentence of the abstract.

A reviewer at SciPost Codebases will expect: a one-line scope statement, concrete contribution (testbench + calibration recipe + null-test diagnostic), honest MSE ordering (v4 has this), reproducibility scaffolding (v4 has this via `tests/`). The "does not claim" framing is a plus, not a minus, *provided* it is moved to §1 proper rather than being introduced by a meta-paragraph about the paper's own history.

## 8. Top three revisions before Phase 3.5

**R1. Rename CorrelatedPairMLE in §2.3 from "faithful reimplementation of arXiv:2511.09491" to "linearised pair-covariance least-squares" and add a one-paragraph fidelity-gap discussion.** This closes the Action 1 partial. Separately: re-run CP-MLE with inverse-variance weighting or NNLS, or at minimum note in §3.3 that the CP-MLE underperformance may reflect the unweighted-lstsq choice rather than a fundamental property of pair-correlation MLE.

**R2. Either (a) move the 1.65× informativeness ratio to a supporting-detail appendix with a single-fixture caveat, or (b) run the ratio on 5+ (H, seed) fixtures and report with CI.** Current single-fixture claim in abstract and §3.2 is brittle.

**R3. Tighten baseline-recovery tests to assert ordering, not just `< 1e-1`.** Specifically: add `test_sw_mle_recovers_base_rate_order` asserting post_mean ∈ [1e-4, 1e-2] for true rate 1e-3; add `test_end_to_end_mse_ordering_sw_lt_pf_lt_cp` encoding the paper's §3.3 finding so a regression would be caught. Rewrite `test_pair_correlation_likelihood_is_informative` to cover the high-rate regime (θ=0.1, not just θ=1e-3) that §2's Laplace-smoothing analysis implies is untested.

## VERDICT: ACCEPT-WITH-REVISIONS

Three revisions are required but all are local: a one-paragraph fidelity caveat on CP-MLE, either multi-fixture 1.65× or appendix-relegation, and tightening two test assertions. None invalidate the core contributions. The framing commitment from v3 is honoured; the null-hypothesis test is clearly articulated and backed by a regression test; the σ² calibration bug is correctly diagnosed and correctly fixed within its operating range; the retraction discipline is exemplary. The MSE-ordering finding (SW-MLE beats SMC and CP-MLE on synthetic) is counter-intuitive but robustly reproducible across the 36 E04 rows and is the kind of honest negative result that methodology papers should report. The remaining weaknesses — CP-MLE fidelity overclaim, single-fixture informativeness ratio, weak baseline-recovery test bounds — are fixable in <1 day and do not affect the paper's main claims.

Word count: ~1950.
