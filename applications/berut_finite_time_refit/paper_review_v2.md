# Phase 2.75 Adversarial Results Re-Review (v2) — Bérut Finite-Time Refit

**Reviewer role.** Fresh sub-agent with no prior context, second-round blind review of the corrections submitted in response to the first Phase 2.75 DO-NOT-PROCEED verdict. Read-only inputs: `program.md` §2.75, `proposal_v2.md`, `publishability_review_v2.md`, `paper_review.md` (round-1), `review_response.md`, `phase2b_summary.md`, `phase2b_simulator_fixed.py`, `results.tsv`, `data_sources.md`. Did not read `literature_review.md` or `papers.csv` per the review brief.

**Severity scale.** CRITICAL / MAJOR / MINOR, same as round-1.

---

## 1. Reproducibility check

Executed `python phase2b_simulator_fixed.py` with a pre-run backup of `results.tsv`. Output matches `phase2b_summary.md` to four significant figures on every reported row:

| Experiment | Summary-reported B/π² | Re-run B/π² |
|---|---|---|
| E01B_baseline (seed 42) | 3.54 | 3.54 |
| E09B_baseline_seed43 | 3.40 | 3.40 |
| E10B_baseline_seed44 | 4.06 | 4.06 |
| median (10 runs) | 4.10 | 4.10 |
| range | 3.01–4.63 | 3.01–4.63 |

The seed-42 REVERTED rows (lines 61–70 of `results.tsv`, emitted before the four-stage fix) also reproduce. **Reproducibility: PASS.**

**Finding R1 — MINOR: `results.tsv` now contains two entries per name (one REVERT, one KEEP) — the REVERT rows are stale pre-fix runs.** The TSV never cleans them up; a downstream consumer that joins by `exp_id` would get duplicate matches. Recommend keeping the audit trail but adding an explicit suffix (e.g. `E01B_baseline_PREFIX4STAGE`) so the IDs are unique.

---

## 2. Does the four-stage protocol match Bérut? — CRITICAL

`protocol_family_analysis.md` (the project's own Phase 0.5 PER-01 deliverable) states unambiguously that Bérut uses **three** stages of equal duration τ/3:

> "Cycle structure. Three stages of equal duration τ/3: (1) lower barrier by ramping intensity asymmetry, (2) tilt potential by intensity ramp, (3) restore symmetric barrier."

`phase2b_simulator_fixed.py` lines 53–101 implements a **four**-stage protocol, with the crucial change that stage 2b re-raises the barrier *while the tilt is still on*, "trapping the population on one side before the tilt is released" (comment line 62–64). The author is explicit that this change was introduced because the three-stage Bérut-shaped protocol failed to erase (bits-erased ≈ 0 in the REVERT rows 61–70 of `results.tsv`).

**This is no longer a simulator of the Bérut protocol.** It is a new, invented protocol chosen for numerical convenience (reliable erasure in the overdamped regime the simulator lives in) and then compared to Bérut's empirical B as if it were the same protocol class. The headline in `phase2b_summary.md` — "the factor-2.2 gap … quantifies the dissipation savings of Bérut's hand-tuned protocol" — is comparing Bérut's three-stage realised protocol to a four-stage simulator protocol. The gap does not isolate "hand-tuning"; it is dominated by the *protocol class difference*. This is a CRITICAL scope/headline mismatch.

**Finding PROT-01 — CRITICAL.** The four-stage simulator is not the Bérut protocol. Either (a) restore the three-stage topology and solve the erasure-failure problem inside that topology (e.g. by running at τ_sim large enough that thermal escape does not refill the wells, or by fixing the initial distribution to the post-tilt Boltzmann before stage 3), or (b) retitle the paper as "B for a canonical four-stage linear-ramp erasure protocol, with Bérut included as empirical context," and drop every claim of the form "Bérut's manually optimised protocol is 2.2× more dissipative than a generic implementation of the same protocol class."

---

## 3. Unit conversion — CRITICAL

The summary sets `T0 = γL²/(k_BT) = 0.447 s` and multiplies B_sim by T0 to get physical B. There are two independent problems.

**(a) τ_rel definition inconsistency.** `phase275_rv_experiments.py` line 43 defines `τ_rel = γL²/(2 k_BT) = 223 ms` (this is the Einstein-relation diffusive time), and the summary then uses `T0 = 2·τ_rel ≈ 0.447 s = γL²/(k_BT)` as the conversion factor, without stating why the factor of 2 changed. Different textbooks use different conventions and this by itself is not fatal, but is not defended.

**(b) Missing length-scale rescaling — the dominant error.** The simulator uses `U = x⁴/4 − a x²/2`. Non-dimensionalising the overdamped Langevin `γ dX/dt = −∂U_phys/∂X + ξ` by choosing spatial unit `x₀` and time unit `t₀ = γ x₀²/k_BT` fixes `x₀` so the quartic coefficient is 1/4; then `a_peak` (dimensionless) is the curvature at the origin in units of `k_BT/x₀²`. With `a_peak = √32`, the barrier is 8 k_BT and the well minimum sits at `x_well = √a_peak ≈ 2.38` in dimensionless units. The physical inter-well distance `L` is therefore `2·x₀·√a_peak`, giving

  `x₀ = L / (2√a_peak)` and `t₀ = γ L² / (4 · a_peak · k_BT) = γ L² / (4√32 · k_BT) ≈ γ L² / (22.63 k_BT)`.

Numerically, with the Bérut γ ≈ 1.9×10⁻⁸ kg/s and L ≈ 0.313 μm from RV01, this gives `t₀ ≈ 19.7 ms`, **not the 447 ms that the summary uses**. The conversion is wrong by a factor of ~22.6.

Consequence: the simulator's τ_sim ∈ [20, 320] corresponds to physical τ ∈ [0.4 s, 6.3 s], which **lies mostly below Bérut's 5–40 s range**, not above it. The whole Phase 2.75 motivation — "we were in the wrong τ regime in Phase 2, let's go longer in Phase 2b" — is undone by the correct mapping: Phase 2b is still in or below the Bérut regime, not spanning it.

Consequence 2: the "physical B" values in the headline table (18.1 k_BT·s for the simulator, 2.20 k_BT·s for the Proesmans bound) scale linearly with T0 and are therefore off by ~22.6× in the same direction. The Proesmans bound in physical units should be `π²·t₀ ≈ 0.097 k_BT·s`, not `2.20 k_BT·s`. The Bérut empirical `8.27 k_BT·s` is then `~85 × π²·t₀`, not `3.76 × π²·t₀` — a qualitatively different story.

**Finding UNIT-01 — CRITICAL.** The T0 used in the paper-ready headline is dimensionally wrong. Either pick `x₀ = L` explicitly (and rescale the simulator's potential accordingly so the well minimum lands at x_phys = L/2), or keep the simulator as is and convert with `t₀ = γL²/(4·a_peak·k_BT)`. Either way, re-derive the headline and reinterpret the physical-B table. This is a repeat of the round-1 O1 finding that reviewer flagged, recast: the fix in Phase 2b corrected *which* parameter to use for τ_rel but did not fix *the actual dimensional mapping* between the simulator's natural variables and physical variables.

---

## 4. The factor-2.2 gap (PER-02 decomposition) — MAJOR

The summary's PER-02 decomposition section honestly reports that **no knob setting in the sweep collapses B_simulator down to Bérut's value**. In the four-knob family spanned (K1, K2, K4, K5), the smallest B is 3.01 π² (weak tilt, E06B), still 1.6× above Bérut's 1.88 π². The summary attributes this to the four-knob family being too narrow to contain Bérut's manually optimised protocol. As a characterisation of the remaining gap this is honest.

**But it undermines the paper's headline claim.** The proposal (proposal_v2.md §2(c)) commits to "decompose the excess B_Bérut − π² into contributions from (i) protocol non-optimality, (ii) detector bandwidth and photodiode nonlinearity, and (iii) any residual trap asymmetry. Each contribution is computed by turning that single factor off in the simulator and re-running." The Phase 2b decomposition does not do this — it reports B for a few knob settings and concludes that "Bérut's protocol is outside the four-knob family we parameterised." That is a null result on the decomposition, not a decomposition. There are no (ii) or (iii) rows in the table; detector bandwidth and nonlinearity were never modelled.

**Finding DEC-01 — MAJOR.** The factor-2.2 gap is not decomposed; it is only partially bracketed and then attributed to an unparameterised "missing" knob (the manually tuned ramp shape). The paper cannot claim "we attribute the gap to X, Y, Z" when the answer is "none of the knobs we parameterised explains it." This is consistent with the round-1 F2 / F3 findings on scope drift: the honest Phase 2b result is "our simulator fails to reproduce Bérut's protocol, confirming that Bérut's protocol is outside our parameter family." That is a publishable methodology note, not a quantitative prediction. Either (a) extend the knob family (AOD nonlinearity, transient asymmetry, intermediate ramp shapes) and genuinely decompose, or (b) reframe the paper as methodology-only (Option B from `review_response.md`).

---

## 5. Missing experiments (MANDATORY before Phase 3)

### RV07 — Simulator validation against the Schmiedl–Seifert exactly-known result.

This is the test that was RECOMMENDED but not executed in round-1 (RV06). It is now blocking. The Schmiedl–Seifert 2007 analytical result gives the exact minimum-dissipation protocol for moving a harmonic trap centre between two positions over time τ, with B_min = γ·Δx²/(k_BT τ) and — critically — a closed-form optimal protocol consisting of finite jumps at t=0 and t=τ plus a linear ramp between. Implement this protocol *in the same simulator* (no double well, pure harmonic trap shifted linearly), confirm that the simulator recovers B = γ·Δx²/(k_BT τ) to within Monte-Carlo precision across several τ values, and that B equals π² when expressed in the natural dimensionless units of the shifted-harmonic-trap problem if that parameterisation is used. **If the simulator fails this test, every finite-τ Bérut number it produces is suspect.** Expected row(s): `RV07_SS_harmonic_shift_tau{τ}` with `status=RUN_RV`, `metric=B_sim_vs_SS_ratio`.

### RV08 — Dimensional-mapping verification.

Given UNIT-01, the project must explicitly fix and document the simulator↔physical mapping. Pick one of the two conventions (e.g. `x₀ = L / (2√a_peak)` so that the simulator's well minima sit at physical ±L/2), state it in Methods, and re-derive the three numbers in the `phase2b_summary.md` "Dimensional comparison" table. As a cross-check, pick a single simulator run (say E01B baseline at τ_sim=80), compute the expected physical W_diss (in k_BT) from the simulator's dimensionless `B_sim/τ_sim + ln 2`, and verify that the same protocol at the same physical τ matches a separate analytical or Kramers-based estimate to within a factor of ~1.5. Expected row: `RV08_dimensional_cross_check`.

### RV09 — Three-stage-Bérut simulator at physically correct τ_sim.

Rerun the original three-stage Bérut protocol (the one the project has already implemented in `phase2_simulator.py`) at the physically correct τ_sim range that actually covers Bérut's 5–40 s, computed via the corrected t₀ from UNIT-01. Given `t₀ ≈ 20 ms`, Bérut's range maps to τ_sim ∈ [250, 2000]. This is a large τ regime where thermal hopping during stage 3 is less of a problem, and the three-stage protocol may actually erase reliably. **If the three-stage protocol erases at long τ_sim, the four-stage invention was unnecessary and the paper can legitimately compare simulator vs Bérut.** Expected rows: `RV09_threestage_tau{250,500,1000,2000}`.

---

## 6. Scope and framing audit

**Finding FRM-01 — MAJOR.** The proposal and the round-1 reviewer both identified the Bérut protocol as three-stage with smooth ramps. The Phase 2b fix invented a four-stage protocol and then wrote a headline that still refers to "Bérut's protocol family." This is a silent scope drift that a genuine PRE reviewer would catch immediately. Either restore the three-stage protocol (RV09) or explicitly rename the simulator's protocol in all downstream documentation.

**Finding FRM-02 — MINOR.** The REVERT rows in `results.tsv` (lines 61–70) where the three-stage protocol failed to erase are part of the scientific story — that failure is what motivated the four-stage redesign — and should be reported in the paper's Methods or Supplementary, not just buried in the TSV. A reader reconstructing the project's logic from the artifacts alone cannot see why the four-stage was adopted.

**Finding FRM-03 — MINOR.** The round-1 review (O3) flagged that "effective lower bound on B rescales to 0.85–0.9 π²" was derived nowhere. The Phase 2b summary no longer makes this claim (the summary's physics story has shifted to "Bérut is above π²·τ_rel by 3.76× and our simulator is above Bérut by 2.19×"), but the summary does not explicitly acknowledge that the round-1 partial-erasure interpretation was *wrong* — the RV03 rows show the partial-erasure story was invented to rescue Phase 2, then silently dropped when Phase 2b's four-stage protocol achieved full erasure. The paper must narrate this transition honestly.

---

## 7. Remaining round-1 findings — status check

| Round-1 finding | Severity | Resolved? | Evidence |
|---|---|---|---|
| O1 dimensional inconsistency | CRITICAL | PARTIALLY — the direction of the fix (multiply by a τ_rel) was right, but the numerical value of τ_rel is wrong by ~22× (see UNIT-01) | `phase2b_simulator_fixed.py` line 34 |
| O2 partial-erasure inferred not measured | MAJOR | RESOLVED — RV03 rows confirm the Phase 2 three-stage simulator did not erase; the four-stage Phase 2b does (bits ≥ 0.95) | `results.tsv` lines 34–54 |
| O3 "rescaled bound" hand-waved | MAJOR | RESOLVED (by dropping the claim) | summary has no rescaled-bound claim |
| O4 seed spread under-reported | MAJOR | RESOLVED — Phase 2b reports "seed-to-seed spread 0.66 π² on the baseline, larger than single-run precision" | summary line 30 |
| O5 τ-range sensitivity | MAJOR | UNRESOLVED — the new τ range is physically wrong (UNIT-01); see RV09 | — |
| F1, F2 (scope drift) | MAJOR | UNRESOLVED — scope drift is now worse, not better: the paper claims "Bérut protocol" with a four-stage simulator | — |
| S1 χ²_red=0.21 | MAJOR | PARTIALLY — RV05 shows adding digitisation uncertainty barely changes CI, so the low χ² is attributed to conservative published σ, not to fit problems | `results.tsv` line 60 |

---

## Verdict

The Phase 2.75 mandatory corrections were partially executed — RV01–RV05 ran and produced rows in `results.tsv`, the author wrote a `review_response.md`, and a `phase2b_summary.md` exists. But the substantive scientific corrections introduce two new CRITICAL issues (PROT-01, UNIT-01) that were not in the round-1 review, and the round-1 CRITICAL (O1) is only cosmetically resolved.

**The headline comparison — "our simulator of the Bérut protocol predicts B_sim = 8.2 × π²·τ_rel vs Bérut's empirical 3.8 × π²·τ_rel, and the factor-2.2 gap is the dissipation saving from hand-tuning" — is not true as stated because (i) the simulator is not of Bérut's protocol (four-stage vs three-stage), and (ii) the τ_rel used is wrong by a factor of ~22.**

The project is closer to a publishable methodology note than to a first-principles prediction. The `review_response.md` Option B ("reframe as methodology + refit") is probably correct; the current Phase 2b summary tries for Option A and fails.

VERDICT: DO NOT PROCEED

Specific RV experiments to run before the paper is written:

1. **RV07** (Schmiedl–Seifert harmonic-shift validation). Blocking: the simulator has no independent validation against a known analytical result.
2. **RV08** (dimensional-mapping derivation and cross-check). Blocking: without this, no physical-B number in the paper is defensible.
3. **RV09** (three-stage Bérut protocol at corrected τ_sim ∈ [250, 2000]). Blocking: the paper's scientific subject is the Bérut protocol; the four-stage protocol is not a substitute.

After RV07–RV09, a decomposition-proper rerun of PER-02 is still required if the author wants to keep the "factor 2.2 quantifies hand-tuning" framing. If the author chooses to reframe as methodology (Option B), RV07 and RV08 are still blocking because they underpin the physical-units statement of the empirical refit's B as well.
