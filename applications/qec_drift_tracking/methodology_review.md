# Phase 2.75 Methodology Review — qec_drift_tracking

Blind review by a fresh reviewer, no access to prior conversation. Sources: README, proposal_v3, publishability_review_v3, PHASE_0_5_PLAN, results.tsv (26 rows), particle_filter.py, baselines.py, phase_diagram.py, willow_loader.py, e02_real_willow.py, data_sources.md, research_queue.md. `phase_0_5_findings.md` does not exist on disk.

## 1. Synthetic phase-diagram sweep: what's the honest reading?

The 91.7% strict-win figure (22/24 cells, `results.tsv` rows 2–25) is almost entirely a self-consistency artefact. Three concrete pieces of evidence:

(a) **The PF's drift model IS the generator.** `phase_diagram.py:67–69` constructs `DriftKernel(kernel_timescale_s, kernel_amplitude, shot_dt_s)` using the exact `(τ, σ)` values then `inject_drift` in `phase_diagram.py:33–55` samples OU noise with the *same* `drift_timescale_s` and `drift_amplitude` (lines 46–47: `rng.normal(0, drift_amplitude * np.sqrt(shot_dt_s / drift_timescale_s), size=E)`). The PF is therefore told the answer. This is not a regime characterisation; it is a tautology check that a correctly-specified filter beats mis-specified baselines.

(b) **The baselines are constant across cells.** `mse_sw ≈ 4.78e-7` and `mse_bay ≈ 8.49e-8` are near-identical for rows 6–25 (timescale ≥ 1 s). Neither baseline responds to the drift regime it is being scored on. Re-examine `baselines.py:36–50` and `baselines.py:67–77`: both use `np.linalg.lstsq(H, p_det)` which produces a single rate estimate from the window-averaged detector rate. Drift amplitude information is destroyed by averaging over the buffer. So the "baselines lose" is really "baselines emit an unchanging point estimate while PF tracks the truth it was given".

(c) **`mse_per` is often 10⁻²⁰ to 10⁻²⁸** (rows 9–25) — the periodic-DEM baseline is beating every method by 13+ orders of magnitude, which should have been a red flag. Looking at `baselines.py:82–105`: at `refit_cadence_s=3600` and `dt_per_shot_s=1e-3`, `shots_per_refit = 3.6e6`, which never triggers over T=2000 shots. Its posterior_mean never updates from `current_rates = np.full(n_errors, 1e-3)` — the constant prior. Meanwhile `phase_diagram.py:42` sets the ground-truth base rate to `1e-3`. The "periodic refit" is winning by doing nothing, because doing nothing equals the unperturbed base-rate mean. The 10⁻²⁰ numbers are float-precision residuals, not physics.

**Flag: SEVERE.** The 91.7% number is meaningless as a regime-characterisation result and cannot appear in the paper. The phase diagram must be re-run with: (i) PF's drift kernel *not* told the generator's timescale and amplitude (that is literally what the phase diagram is supposed to discover), (ii) baselines that actually estimate drifting rates (e.g. sliding window on a transformed statistic, or exponential-forgetting MLE), and (iii) a periodic baseline whose cadence fires at least once during the run.

## 2. Real-data MSE: what does it actually measure?

`e02_real_willow.py:52–55` computes MSE of each method's posterior-mean-rate vector against `ref_rates`, where `ref_rates` is extracted from `correlated_matching_decoder_with_si1000_prior/error_model.dem` (see `willow_loader.py:81–82`). Three problems:

(a) The SI1000 DEM is Google's SI1000 Pauli-noise model — an *a priori* published pseudo-device noise model, not a per-experiment fit. `willow_loader.py:61` literally loads `circuit_noisy_si1000.stim`, i.e. a circuit instrumented with the SI1000 prior. The reference is the decoder's prior, not a device-measured truth.

(b) Calling this "MSE vs ground truth" is a category error. Every method's MSE to SI1000 is actually measuring *how close does this method get to the decoder's prior*, which is a prior-recovery test and rewards conservatism.

(c) The PF is initialised with `prior_mean=ref_rates` (`e02_real_willow.py:36`) while SW-MLE and Static-Bayes are not. The PF starts at the reference; the two baselines start from `np.full(n_errors, 1e-3)` and `Beta(2, 2000)` (mean ≈ 1e-3). Of *course* the PF's final posterior MSE against the reference is lower — it started there and its drift propagator has a small step. The real-Willow ordering (PF 1.42e-5 < SW 2.35e-5 < Bay 3.79e-5) is dominated by initialisation, not filtering.

**Flag: SEVERE.** No real-data claim of "PF beats baselines on Willow" is defensible from this experiment. To fix: (i) use the same prior for every method; (ii) use the log-likelihood of held-out shots under each method's posterior, or the reweighted-PyMatching LER as the proposal specified, not MSE-to-prior; (iii) seek an actual device-specific ground truth (e.g. per-experiment calibration DEMs from metadata.json, or arXiv:2512.10814's published per-window DEMs) before any claim about "tracking Willow".

## 3. Likelihood function in the particle filter

`particle_filter.py:79–84`: `log_liks[p] = -0.5 * (diff ** 2).sum() / 0.5`. The likelihood is `L(θ) ∝ exp(-‖Hθ - s‖²)` where `Hθ` is the per-detector *expected event rate* treated as a prediction of the *observed binary event vector s*. This is wrong in two ways:

(a) **Mean ≠ sample.** `Hθ` is approximately the expected per-detector marginal (and even that is only first-order correct since DEM detector events arise from XOR of edges, not addition, per `phase_diagram.py:54` `(H @ edge_fires) % 2`). Comparing an expected rate (~0.001) against a binary (0/1) event vector makes the residual always order-unity regardless of θ; the likelihood is effectively flat.

(b) **Independent-Bernoulli is the proper likelihood.** For a single shot on a decomposable DEM, `P(s | θ) = Σ_{e consistent with s} Π_j θ_j^{e_j} (1-θ_j)^{1-e_j}`. This is the posterior-syndrome distribution Stim models. The Gaussian surrogate throws away all the structure.

The in-code comment (lines 73–77) acknowledges this as "a smoke implementation". That is honest; what isn't honest is running this code through a publication-scale phase diagram and a paper claim. Switching to the correct likelihood would most likely *shrink* the PF's apparent advantage, because the baselines' pseudo-inverse attribution (which IS approximately a first-order MLE under the same independent-Bernoulli model) becomes a much more reasonable comparator.

**Flag: MAJOR.** At minimum, reporting any advantage figure should be gated on replacing the Gaussian surrogate with the Bernoulli likelihood (or its Poisson approximation) and re-running.

## 4. Baseline implementation quality

`baselines.py:36–50` (`SlidingWindowMLE._refit`): the buffer is a list of per-shot detector-event vectors; `p_det = stream.mean(axis=0)`; `p_edge = np.linalg.lstsq(H, p_det, rcond=None)`. That is a linear *regression* of per-detector marginal event probabilities on the parity-check matrix, clipped to [1e-8, 0.499].

Is that a faithful reimplementation of arXiv:2511.09491's sliding-window MLE? Almost certainly **not**. 2511.09491 derives an optimal window width *as a function of an assumed drift spectrum* and uses maximum-likelihood on the *joint detector-pair* statistics (the standard pair-correlation trick from Chen et al., because edges with overlapping detector support produce correlated firing). `baselines.py` uses only single-detector marginals and a pseudo-inverse — i.e. the *worst* case of the MLE family, equivalent to a first-order Taylor expansion of the real MLE. The same critique applies to `StaticBayesianRates` (lines 67–77), which is a Beta-conjugate proxy not a TN+MCMC implementation as `proposal_v3` §3 committed to (file-comment lines 6–9 acknowledge this). The `.md` files flag this as "Phase 2 refinement" but the paper claim's denominator depends on baselines representing the published state of the art.

**Flag: MAJOR.** Calling this a head-to-head against arXiv:2511.09491 and arXiv:2406.08981 is an apples-to-oranges comparison that will be caught immediately by any reviewer familiar with either paper. A real reimplementation (or at least author-code if available) is required before any "PF beats SW-MLE / static Bayes" claim is made.

## 5. The LCD-as-1-particle-SMC unification

Search results: the "LCD is formally a 1-particle SMC" claim appears in exactly two places — `research_queue.md` H25 and H46 (as a *hypothesis to formalise*) and `make_figures.py:6` (as a *planned schematic*). No proof, derivation, definition of the mapping, or Riverlane LCD specification document appears anywhere in the repository. `data_sources.md:31` explicitly notes "Riverlane FPGA-LCD production raw syndrome release: NO", and no LCD reimplementation is on disk.

The Phase 0.25 reviewer (publishability_review_v3.md §5 objection A) already flagged that the LCD baseline is the weakest spot and demanded a protocol-conformance gap report *before* any filter-vs-LCD claim. That gate is not met; in fact the prerequisite reimplementation does not exist.

**Flag: SEVERE.** Promoting H25 to a paper-level claim ("Riverlane's production LCD is formally a 1-particle SMC") is not something the repository currently supports. It is at best a conjecture. At worst it is wrong — production LCD (Barnes et al. 2025 Nat. Commun.) is a graph-clustering decoder, not a state-space inference procedure, and the mapping between its cluster-update step and a single Dirac-delta particle update is not obviously true. Either this claim is removed from the paper or a formal proof is added.

## 6. Shots and statistical power

E02 used 5000 shots on one d=5 r=1 experiment (`results.tsv` row 26: `5000`). Zenodo 13273331 ships ~50 000 shots per experiment per the dataset description in `data_sources.md:10`, so we use 10% of available data. Two statistical issues:

(a) A single experiment, single seed, single rate vector: no confidence interval on the reported 1.42e-5 / 2.35e-5 / 3.79e-5. A bootstrap over shots would expose whether the ordering is inside or outside sampling noise.

(b) The reference-DEM MSE denominator is ~(1e-3)² = 1e-6, so the reported MSEs are of the same order as the rate variance itself. With no CI, the 1.66× ratio between PF and SW may be entirely within per-seed, per-experiment noise.

(c) Code bug in the e02 recording schema: `results.tsv` row 26 writes the experiment path into the `timescale_s` column, `24` (num_detectors) into `amplitude`, `77` (num_errors) into `T`, `willow_real` into `elapsed_s`, etc. — see `e02_real_willow.py:106–112`. The on-disk headline numbers (PF=1.42e-5, SW=2.35e-5, Bay=3.79e-5) are in columns `mse_pf`/`mse_sw`/`mse_bay` so they are still readable, but anything automated over this TSV will misalign. Furthermore the code intends to run r01, r11, r25 but `results.tsv` contains only one row (r01). Either r11 and r25 failed silently (the try/except in e02_real_willow.py:97–101 would absorb any exception) or only r01 was run. Neither is acknowledged anywhere.

**Flag: MAJOR.** Bootstrap shots within the r01 experiment (10⁴ draws, per research_queue H40) and run multiple experiments (the proposal §2.2 pre-registers 24 cells; it's odd to present a single real-data experiment as headline evidence). The three-way ordering PF < SW < Bay must survive a Bonferroni-corrected paired test, as the proposal itself committed to.

## 7. Missing: LCD baseline entirely

`proposal_v3.md` §2.3, §3, §6 (row "LCD-class baseline"), and §7 all commit to a Riverlane-LCD-class head-to-head. `publishability_review_v3.md` §0 revision-4 flags this as PARTIAL and demands a conformance-gap report. `PHASE_0_5_PLAN.md` Step 7 commits to scaffolding the reimplementation in Phase 0.5. **Nothing on disk implements or benchmarks LCD.**

The central claim's framing "PF outperforms SW-MLE and static Bayes" silently drops the LCD comparator. Per the proposal's own §4.3 regime-kill logic and the publishability reviewer's objection A, dropping LCD means the LCD-class adaptive baseline cannot be ruled out as the method that actually dominates the filter in production-relevant regimes, which is exactly the caveat PRX Quantum reviewers will insist on.

**Flag: SEVERE — show-stopper for the proposal's stated venue.** Either (a) the paper has to be scoped down and explicitly declare "LCD out of scope for this submission, deferred to follow-up", accepting that it cannot be the "regime characterisation including LCD head-to-head" proposed, or (b) the LCD reimplementation has to actually happen before paper draft.

## 8. Sub-hour-drift claim

`data_sources.md` residual risk #2 and `research_queue.md` H63 both note that Willow Zenodo timestamps are per-run, not per-shot. `proposal_v3.md` §4.1 sweep covers {10ms, 1s, 1min, 10min, 1hr, 6hr}. Any cell with timescale ≤ minutes-scale is therefore unreachable on real data — all evidence for sub-hour cells must come from synthetic drift injected atop Willow statistics, exactly as H31 predicts.

The central claim's real-data MSE result (§2 above) is from a single r01 experiment, unrelated to any timescale cell. The 22/24 synthetic strict-wins are unreal for the reasons in §1. So no real-data sub-hour-drift claim is supported, and even the synthetic sub-hour-drift claim is invalid until §1–§3 are fixed.

**Flag: MAJOR.** The paper's headline — if there is one that survives §1–§7 — must be restricted to ≥1-hour-scale drift, and the sub-hour-cell results must be explicitly labelled "synthetic-only, injected drift atop real base statistics" per the proposal's own §4.1.a framing.

## 9. Scope: what can the current data actually support?

Given flags 1–8, the defensible headline shrinks dramatically. What the current repo can actually support:

- **A replication study** of the arXiv:2512.10814 DEM-on-Willow baseline (once actually run; `PHASE_0_5_PLAN.md` Step 4 is not yet executed — no E00 row in results.tsv).
- **A methodology demonstration** that a textbook Rao-Blackwellised bootstrap SMC, given oracle access to the drift generator, tracks injected OU drift better than a single-rate pseudo-inverse MLE baseline that doesn't try to track drift.
- **A data-access contribution**: public, tested loaders for Zenodo 13273331 and (future) Zenodo 13961130.

That is a Phys. Rev. Research methods note, not a PRX Quantum regime-characterisation paper.

**What is achievable in one week of further work:**

1. Re-run the phase diagram with the PF drift kernel *not* matched to the generator (draw τ, σ from a prior wider than the sweep range); expect strict-win fraction to drop from 91.7% to something genuinely informative (and possibly <10%).
2. Re-implement sliding-window MLE per 2511.09491 using pair-correlation statistics, not single-detector pseudo-inverse.
3. Swap the PF likelihood from Gaussian surrogate to independent-Bernoulli on decomposable DEM edges.
4. Bootstrap the E02 numbers over shots; report CIs.
5. Fix the results.tsv schema for E02 rows.
6. Add ≥5 more Willow experiments (r11, r25, and 2-3 random q-pairs) to E02.

One week gets a defensible Phys. Rev. Research methods note. LCD + full phase diagram + sub-hour real-data claim remain out of reach in one week.

## 10. Top three revisions before paper draft

**(R1) Kill the PF-knows-the-generator self-consistency.** Sample the PF's `DriftKernel(τ, σ)` from a prior strictly wider than the sweep range (e.g., log-uniform τ ∈ [1e-3 s, 1e5 s], σ ∈ [0.01, 1.0]) and marginalise the hyperparameters via a Rao-Blackwellised-in-hyperparameters scheme. Without this, no phase-diagram number is publishable. This is the single biggest issue.

**(R2) Replace the Gaussian-surrogate likelihood with an independent-Bernoulli likelihood on the decomposable DEM, and reimplement SW-MLE per 2511.09491's pair-correlation MLE.** If PF still beats SW-MLE after this, the claim is much more defensible; if it doesn't, the paper needs a different angle.

**(R3) Either implement the LCD baseline with a protocol-conformance benchmark against Barnes et al. 2025 Nat. Commun., or rescope the paper to drop the LCD head-to-head and the "unification of LCD as 1-particle SMC" claim.** Both options are acceptable; the current half-committed state is not.

## VERDICT: MAJOR-REVISIONS

The three central claims in the submitted headline all fail sanity checks on the code as written. The synthetic 22/24 win is a tautology, not a regime result; the real-data MSE ordering is dominated by initialisation choices and baselines fitted to a decoder's prior, not a device truth; the LCD-as-SMC unification exists only as a speculative hypothesis in the research queue. None of these defects are fatal to the project — each has a clear fix path — but every one of them is fatal to the paper as currently claimed, and (R1) alone invalidates the phase-diagram centrepiece. The project has strong scaffolding (loaders, proposal registration, lit review, data access cleared) but has not yet done the real experimental work the paper pretends to report.

Word count: ~1900.
