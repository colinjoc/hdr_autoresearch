# Phase 2.75 Adversarial Results Review — Bérut Finite-Time Refit

**Reviewer role.** Fresh sub-agent, no prior context. Blind review of the project artifacts on disk. Does not see the HDR agent's conversation history. Applies the six-point Phase 2.75 review protocol from `program.md` §Phase 2.75.

**Inputs read.** `program.md` §2.75 only, `proposal_v2.md`, `publishability_review_v2.md`, `results.tsv`, `data_sources.md`, `sanity_checks.md`, `protocol_family_analysis.md`, `phase2_summary.md`, `phase2_simulator.py`, `e00_baseline_fit.py`, `phase1_tournament.py`, `data/raw/berut_2012_qdiss_vs_tau.csv`. Scripts were re-run.

**Severity scale.** CRITICAL (result wrong or unreproducible) / MAJOR (overclaim, missing qualifier, gap) / MINOR (style, nice-to-have).

---

## 1. Reproducibility check

All three scripts were re-executed in-place (after backing up `results.tsv`). The full rerun produced a file **byte-identical to the committed copy** (`diff` returned empty). The declared `seed=42` in `e00_baseline_fit.py`, `phase1_tournament.py`, and `phase2_simulator.py` deterministically reproduces every number in `results.tsv`. Bootstrap at seeds 42/43/44 in the E00 fit reproduced medians 8.269 / 8.267 / 8.279 exactly. The Phase 1 tournament ranking (F1 < F2 < F3 < F4 by AICc) reproduced. All 21 Phase 2 simulator experiments reproduced to four significant figures.

**Finding R1 — MINOR: seed-column in `results.tsv` is hardcoded to "42" even for E19 (`seed=43`) and E20 (`seed=44`).** `phase2_simulator.py` line 239 writes the literal string `"42"` for every simulator row, so the TSV's seed column does not reflect the actual RNG seed used. The notes column and the experiment name disambiguate, but the canonical seed field is wrong. Minor — it is a logging bug, not a wrong result.

**Finding R2 — MINOR: Phase labeling bug.** `phase2_simulator.py` line 236 uses `"2" if r["name"] <= "E11" else "2.5" if r["name"] <= "E15" else "2"`. String comparison here is lexicographic; `"E11_K5_residual_50pct" <= "E11"` is False (longer string), so E11 is labeled phase 2.5. `"E15_K3K5_overlap+residual" <= "E15"` is False, so E15 gets labeled phase 2. Result: E11 (a pure single-knob K5 sweep) is in phase 2.5, while E15 (a genuine K3×K5 interaction sweep) is in phase 2. The phase label does not track what each experiment is actually doing. Minor — it affects bookkeeping of "what counts as the Phase 2.5 interaction sweep", not any numerical result.

**Verdict on reproducibility.** PASS. Scripts are deterministic at declared seeds and produce the reported numbers exactly.

---

## 2. Cherry-picking audit

Every row in `results.tsv` is produced by running `e00_baseline_fit.py` (1 row), `phase1_tournament.py` (9 rows: 1 KEEP + 8 TOURN), and `phase2_simulator.py` (21 rows, all KEEP). There are no dropped or un-logged simulator runs — the script itself is the record.

**Finding C1 — MINOR: every simulator row is `KEEP`.** For a simulator parameter sweep this is not inherently wrong (there is no "kept vs rejected" decision — the sweep is the data). But the project has no rows with `status` ∈ {REVERT, FAIL, DIAG}. This is unusual enough to note. The absence of a criterion in the notes field for what would have led to a REVERT is a minor documentation gap — a reader cannot tell whether any simulator setting was tried, failed (e.g., unstable integrator, divergent trajectories), and omitted from `results.tsv`. If none were omitted, say so explicitly; if some were omitted, they should appear with `status=REVERT`.

**Finding C2 — MINOR: the digitised CSV includes a note referencing an "under-forced" point at τ=40 s with ⟨Q⟩→0 = 0.59, "excluded from fit per authors".** This exclusion is legitimate (matches the Bérut-Petrosyan-Ciliberto 2015 convention) and is called out in `data_sources.md`. But it is worth flagging that the entire fit depends on accepting the authors' "optimised vs non-optimised" partition as-reported, without independent reclassification. A single-line sensitivity analysis in the paper ("including the under-forced point shifts B by …") would disarm reviewer objections. This isn't cherry-picking by the HDR agent, but the inherited classification propagates.

**Verdict on cherry-picking.** PASS. No evidence of selective reporting; the scripts are the record.

---

## 3. Overclaiming check

This is where the project starts to slip. The headline in `phase2_summary.md` §"What the paper should claim" is:

> "The Bérut 2012 / 2015 'optimised' protocol realises a finite-time Landauer coefficient B = 0.84 ± 0.05 π², apparently below the Schmiedl–Seifert symmetric lower bound of π². A first-principles Brownian-dynamics simulator of the full Bérut protocol family attributes this apparent violation to partial-erasure (residual-barrier) effects in which the effective information removed is less than one bit; under this interpretation, the effective lower bound on B rescales to ≈ 0.85–0.9 π², consistent with the data."

**Finding O1 — CRITICAL: dimensional inconsistency in the headline comparison.** The empirical B from E00 has units of k_BT·s (the authors' `B = 8.15 k_BT·s`). Dividing by π² gives `0.838` *k_BT·s / π²*, which is **not a pure dimensionless number** and **is not directly comparable to the simulator's dimensionless B/π² = 2.3**. The simulator operates in dimensionless time units (line 10 of `phase2_simulator.py`: "time in units of relaxation time γ/a_peak"). To make the comparison meaningful, the simulator's B must be multiplied by, or the empirical B divided by, the relaxation time τ_rel = γ L² / (a_peak k_BT). For plausible Bérut parameters (L≈1 μm, γ≈1.9×10⁻⁸ kg/s, a_peak=8 k_BT in dimensionless units), τ_rel is of order 0.6–5 seconds depending on length-scale choice — a factor that the project never fixes. As a consequence, the claim "empirical 0.84 π² vs simulator 2.3 π²" literally compares quantities in different units. The partial-erasure "rescue" of the factor-of-3 discrepancy is therefore consistent with *any* desired explanation simply by re-choosing τ_rel.

This finding alone blocks proceeding to Phase 3. The paper cannot advance a headline that equates `0.84 k_BT·s/π²` with `2.3 (dimensionless)/π²` without a pinned, defended choice of τ_rel.

**Finding O2 — MAJOR: "partial-erasure" interpretation is inferred, not measured.** The simulator records only the cycle-integrated work W (line 140 of `phase2_simulator.py`). It never counts how many trajectories end in the right well, never reports the Shannon entropy of the final distribution, and never computes "bits erased per cycle". The phase2_summary.md classification of E10/E11/E14/E17 as "incomplete-erasure" is *inferred from the knob setting* (K5 > 0) plus physical intuition, not from a simulator observable. The paper cannot claim "partial-erasure explains the discrepancy" when the simulator does not measure partial erasure. Fix: add final-well occupation and entropy-of-final-distribution outputs to the simulator; re-run E10/E11/E14/E17/E15; only then is the partial-erasure interpretation directly supported.

**Finding O3 — MAJOR: "effective lower bound on B rescales to 0.85–0.9 π²" is derived nowhere.** phase2_summary.md asserts that "at 5–10 % incompleteness, the effective bound would be ≈ 0.85–0.9 π²" but no calculation produces this number. Which Proesmans-bound derivation rescales linearly in residual population? The citation is not given and the scaling is not proven. The number is hand-waved. Fix: either derive the rescaled-bound formula explicitly, or drop the claim.

**Finding O4 — MAJOR: seed-stability claim understates the spread.** phase2_summary.md reports "seed-to-seed spread = 0.05 π²". E01 (seed 42) gives B/π² = 2.262, E19 (seed 43) gives 2.372, E20 (seed 44) gives 2.340. The actual peak-to-peak spread is 0.110 π² — **more than 2× the stated value** — and E01's 95 % CI [2.198, 2.325] does not overlap E19's CI [2.309, 2.434] except at the very edge. This is a direct misreport, not a rounding disagreement.

**Finding O5 — MAJOR: τ-range sensitivity of the fitted B is not acknowledged.** E01 uses τ ∈ {1,2,4,8,16} and yields B/π² = 2.262. E21 uses τ ∈ {0.5,1,2,4,8} (same knobs, same seed) and yields B/π² = 1.196. Changing the τ grid alone — no physics change — moves the inferred B by **a factor of 1.9**. This is a stronger sensitivity than any knob-variation in the protocol family. It means the "simulator B ≈ 2.3 π²" headline number is contingent on the specific τ range chosen, and the empirical B "fit over τ ∈ {5, …, 40} s" probes a τ regime that the simulator has not been calibrated to. Without a matched τ range (and the dimensional calibration in O1 above), comparing the two B values is meaningless. This is the most scientifically serious gap in the project.

**Verdict on overclaiming.** FAIL. Headline requires major fixes before paper-writing can proceed.

---

## 4. Statistical validity

**Finding S1 — MAJOR: reduced χ² for F1 is 0.21 (χ² = 1.87 with 9 d.o.f.).** This is very low and suggests the reported per-point error σ = 0.15 k_BT is larger than the residual scatter, i.e., the errors are over-estimated or the digitised curve has been smoothed by eye (digitisation follows the author-drawn fit line rather than scattered individual points). The E00 CI on B is consequently inflated: if the true scatter is σ ≈ 0.07 k_BT, the 95 % CI on B should be ~half as wide, and the empirical "B < π²" finding would be statistically stronger, not weaker. Conversely, if the errors are genuinely ±0.15 k_BT but the points have been smooth-digitised, the residuals are artificially suppressed and the CI understates the systematic uncertainty. This needs a bootstrap-from-resampled-scatter control.

**Finding S2 — MAJOR: is the 0.84 π² empirical vs 2.3 π² simulator gap informative given the bootstrap CI?** Given the dimensional-inconsistency finding O1, the gap is not currently in the same units and so "informativeness" is not defined. Setting that aside, even within the simulator's dimensionless units, the tau-range sensitivity (O5) and seed-to-seed spread (O4) together give a simulator systematic of ~0.5 π², which is 3–5× the quoted ±0.03 bootstrap stderr. The real error budget on the simulator side is dominated by systematics, not by Monte Carlo noise. The project has not yet presented the simulator result with its *systematic* uncertainty envelope; doing so may collapse or expand the apparent gap.

**Finding S3 — MINOR: Phase 1 F2 (Van Vu-Saito) parameter C has 95 % CI [−13.3, 19.1] — straddles zero.** The F2 model is not identifiable from the 10 Bérut points, which is consistent with the project's decision to use F1. But this should be noted explicitly when the 1/τ form is defended: "the higher-order 1/τ² term is not resolved by the data" is a cleaner defense than "AICc prefers F1".

**Finding S4 — MINOR: integrator convergence is not reported.** `simulate_cycle` uses Euler-Maruyama with `dt = tau / n_steps` where `n_steps = 800`. For τ = 16, dt = 0.02, which is moderately below the fastest timescale (a_peak = 8, so relaxation dt_max ≈ 0.125) but not by much. No convergence-in-dt study is reported. Euler-Maruyama has O(dt) bias in weak observables (like ⟨W⟩) so a 1–2 % bias at the largest τ is plausible. Fix: run a doubled-n_steps control on at least E01 and E21.

**Verdict on statistical validity.** Major issues in the statistical-uncertainty accounting. The empirical CI is potentially wrong due to digitisation smoothing (S1), and the simulator is dominated by systematics rather than the reported Monte Carlo stderr (S2, O4, O5).

---

## 5. Missing experiments (MANDATORY — HDR agent must execute all of these before Phase 3)

### RV01 — Unit calibration: pick and defend a single τ_rel and redo the comparison in matched units.

Define τ_rel = γ L² / (a_peak k_BT) using the Bérut-reported γ, L, a_peak values (with stated ±10 % uncertainties). Convert the simulator's dimensionless B to k_BT·s via B_sim^[sec] = B_sim × τ_rel. Re-present the headline in k_BT·s. Compare to empirical B_emp = 8.27 k_BT·s. Propagate τ_rel uncertainty into the simulator's CI. **Expected row(s) in `results.tsv`:** `RV01_calibrated_comparison` with `status=RUN_RV`, `metric=B_sim_kBT_s`, `value`, CI, and notes recording the chosen (γ, L, a_peak) triple. Without this experiment the project has no headline.

### RV02 — Matched τ range: run the simulator over τ values that correspond (in the chosen τ_rel calibration) to 5–40 s, matching the Bérut data.

Using the RV01 calibration, if τ_rel ≈ 1 s then run E01 at τ ∈ {5, 10, 15, 20, 25, 30, 35, 40} dimensionless; if τ_rel ≈ 0.6 s run at τ ∈ {8, 16, 25, 33, 42, 50, 58, 67}. Fit B from those simulator points. Report how the matched-range B compares to the previously reported "median B = 2.3 π²" that was computed over the arbitrary τ ∈ {1, …, 16}. **Expected rows:** `RV02_matched_tau_baseline`, `RV02_matched_tau_best_guess` (knobs from E16). Until this is done, the simulator has not been interrogated at the Bérut τ range.

### RV03 — Direct partial-erasure measurement: extend the simulator to record final-well occupation and Shannon entropy.

Add to `simulate_cycle`: (a) `p_right_final` (fraction of trajectories ending with x > 0 at t = τ), (b) `H_final = -p_R log p_R - p_L log p_L` in nats, (c) `bits_erased_per_cycle = 1 − H_final / log 2`. Re-run E01, E10, E11, E14, E15, E17 and report these quantities. The partial-erasure interpretation in phase2_summary.md is only supported if K5 > 0 configurations have `bits_erased_per_cycle < 1`. If all configurations successfully erase (p_right_final ≈ 1) regardless of K5, the interpretation collapses. **Expected rows:** `RV03_erasure_E01`, `RV03_erasure_E10`, `RV03_erasure_E11`, `RV03_erasure_E14`, `RV03_erasure_E15`, `RV03_erasure_E17`.

### RV04 — Integrator convergence control: double n_steps on E01 and E21 and report the shift in B.

Run `simulate_cycle` with n_steps ∈ {800, 1600, 3200} at the E01 and E21 knob settings. Report B as a function of n_steps. If the shift from 800→3200 exceeds 1 % of B, the project must re-run all simulator experiments at the converged n_steps. If the shift is <0.5 %, the existing runs are fine and this experiment documents that. **Expected rows:** `RV04_convergence_E01_n1600`, `RV04_convergence_E01_n3200`, `RV04_convergence_E21_n3200`.

### RV05 — Digitisation-bias control: bootstrap the empirical B under an error-model that treats σ as a free parameter, not σ = 0.15 fixed.

The reduced χ² = 0.21 for F1 suggests the stated σ = 0.15 is too large or the digitisation is smoothed. Fit `⟨Q⟩(τ) = ln 2 + B/τ` with `σ` (common for all points) as a free parameter by maximum likelihood. Report B and its profile-likelihood CI, and the fitted σ. Compare to the fixed-σ E00 result. **Expected row:** `RV05_freesigma_empirical_B` with `status=RUN_RV`. If the free-σ fit gives σ ≈ 0.05 k_BT, the original CI [0.75, 0.93] π² is too wide; if it agrees with 0.15, the original analysis is validated.

### RV06 (optional, encouraged) — Symmetric Schmiedl–Seifert verification.

The simulator does not currently recover B = π² for any protocol. phase2_summary.md admits the simulator's parameterisation "does not reach the SS optimum" and blames variational closure. For an independent cross-check, run the analytically-known two-step symmetric-optimal protocol (linear instantaneous jumps as described in Schmiedl–Seifert 2007) in the simulator and confirm B → π² in the quasistatic limit. If the simulator fails this test, the headline "B above π² by factor 2.3" is not a physical prediction but a simulator artifact. **Expected rows:** `RV06_SS_optimum_symmetric`. Not strictly mandatory for phase 3 if the other five above are addressed, but this would firm up confidence in the simulator by an order of magnitude.

---

## 6. Scope and framing audit

**Finding F1 — MAJOR: the proposed paper headline in phase2_summary.md strips the critical dimensional caveat.** It says "simulator B ≈ 2.3 π²" without saying "in the simulator's natural units, under the choice γ/a_peak as the time unit, which corresponds to τ_rel in Bérut of approximately …". Without that phrase the headline is wrong. Fix: once RV01 is done, the headline becomes "B_sim = X ± Y k_BT·s vs B_emp = 8.27 ± Z k_BT·s" — and the paper can then compare apples to apples.

**Finding F2 — MAJOR: the scope boundary has drifted.** proposal_v2.md §7 says the paper is "not a reinterpretation of Landauer" and "not a test of asymmetric-barrier extensions". But phase2_summary.md's headline "the effective lower bound on B rescales to 0.85–0.9 π²" *is* a reinterpretation of the Proesmans bound (it claims the bound does not apply as-stated to protocols with incomplete erasure — a modified bound, even if derived by invoking Shannon reduction rather than by new theory). Either (a) this reinterpretation is claimed as a genuine contribution — in which case it needs its own derivation (see RV03 and O3) and the proposal should be updated to reflect it; or (b) the framing drops this claim and reverts to the scope the proposal declared. Currently the paper would straddle the two, which is the worst of both.

**Finding F3 — MINOR: the "partial-erasure" re-interpretation, if formalised, is a publishable claim by itself.** If RV03 shows that Bérut's "optimised" protocol in fact leaves ≈10 % residual population in the wrong well and this completely explains the factor-3 dimensional discrepancy, that is a real and PRE-worthy finding. But it would be a different paper from the one the proposal pre-registered. The project should decide which paper it is writing before Phase 3 begins.

**Finding F4 — MINOR: the data source is arXiv:1503.06537 (2015 review) Fig 8, not Bérut 2012 Nature Fig 3c.** data_sources.md flags this; sanity_checks.md flags this; the scope check should flag it explicitly in the paper's §2.3 too. The 2015 "optimised" dataset is closer to the Schmiedl–Seifert optimum than the raw 2012 Fig 3c data, so any "Bérut protocol" claim must be clear that the comparison is to the 2015 optimised protocol, not to the original 2012 symmetric protocol.

---

## Verdict

**The project CANNOT proceed to Phase 3 in its current state.** Three findings are blocking:

- **O1 (CRITICAL)** — dimensional inconsistency between simulator and empirical B makes the headline literally meaningless without a pinned τ_rel. Must be fixed by RV01 + RV02.
- **O2 (MAJOR)** — the partial-erasure interpretation is inferred, not measured. Must be directly tested by RV03.
- **O5 (MAJOR)** — tau-range sensitivity of the simulator B is a factor of ~2, larger than all knob-variation effects. The simulator B is not a well-defined quantity without a specified τ range, which must be matched to Bérut (RV02).

The remaining MAJOR findings (O3, O4, S1, S2, F1, F2) can be resolved by revising `phase2_summary.md`, executing RV03–RV05, and tightening the abstract/scope. MINOR findings (R1, R2, C1, C2, S3, S4, F3, F4) should be addressed but are not blocking.

**Required actions before Phase 3:**

1. Execute RV01 through RV05 (RV06 recommended) and log all results to `results.tsv` with `status=RUN_RV`.
2. Write `review_response.md` addressing each finding with FIX / REBUT / ACKNOWLEDGE.
3. Rewrite `phase2_summary.md` with matched-unit comparisons and measured (not inferred) partial-erasure metrics.
4. Decide whether the paper is the originally-proposed simulator-vs-empirical comparison or the reinterpretation-of-Proesmans paper and update the proposal + scope check accordingly.

After those actions, a second reviewer pass is required before Phase 3 is unblocked.

**Phase 3 gate: DO NOT PROCEED. Execute the six (five mandatory + one encouraged) missing experiments and resolve the CRITICAL and MAJOR findings first.**
