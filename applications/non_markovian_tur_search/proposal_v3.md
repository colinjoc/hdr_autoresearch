**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics: Theory and Experiment

# The kinetic uncertainty relation on published single-molecule and single-electron datasets: an empirical tightness comparison against TUR with explicit diagnostic protocol

## 1. Question

Is the kinetic uncertainty relation (KUR, Van Vu–Hasegawa 2022) empirically tighter than the Barato–Seifert 2015 thermodynamic uncertainty relation (TUR) when both are evaluated on publicly available single-molecule or single-electron entropy-production-inference datasets, and does the ratio (TUR − KUR)/TUR scale with a model-free memory indicator?

v1 REFRAMEd over five objections (uncited Skinner-Dunkel / Manikandan / Van der Meer; tautological TUR-violation outcome; feasibility gate vs falsifiability confusion; σ-from-ATP-stoichiometry uncertainty; PRL venue too ambitious). v2 addressed most of these (pivoted to KUR-vs-TUR on Skinner-Dunkel data, used their σ estimator, dropped ATP stoichiometry, swapped to PRE) but was REFRAMEd again over two residual MAJORs: (M1) the data-access "gate" was a polite way to die — one author email with no fallback, and (M2) the O2 kill-outcome ("KUR ≤ TUR empirically, or the theorem is violated") is partially tautological: a measured violation overwhelmingly indicates a σ-estimator mis-specification or coarse-graining class mismatch, not a real theorem violation. v3 patches both.

## 2. Proposed contribution (v3: two targeted changes from v2)

### What v3 keeps from v2 (unchanged)

- Narrow scope: KUR-vs-TUR tightness comparison, not a broad TUR-violation hunt.
- Skinner-Dunkel 2021 σ-inference estimator, not ATP stoichiometry.
- Fano factor F = Var(N)/⟨N⟩ as the model-free memory indicator; pre-register that (TUR − KUR)/TUR scales monotonically with F.
- PRE primary target, *J. Stat. Mech.* fallback.

### v3 change 1 — named fallback datasets (addresses M1)

v2 depended on a single dataset source (Skinner-Dunkel 2021 flagellar-motor / beating-flagellum data) with "email the PI if inaccessible" as the only fallback. The round-2 reviewer correctly flagged that non-response would pause the project indefinitely. v3 commits to a **three-tier dataset cascade** with public sources first and the project proceeding on whichever tier is accessible:

- **Tier A (preferred): Skinner-Dunkel 2021 flagellar-motor traces.** Smoke test — check PNAS supplementary + Dryad/Zenodo/GitHub links before Phase 0. Two weeks maximum on an author-email attempt if not publicly deposited.
- **Tier B (public electronic-analog fallback): Pekola-group single-electron-box datasets.** The Pekola-group (Aalto) has published open-deposited single-electron-box trajectories with cycle-counting statistics (Koski et al. 2015, Hofmann et al. 2016, and follow-ups). These are single-electron, not single-molecule, but they share the stochastic-thermodynamics observable structure. The KUR-vs-TUR tightness prediction applies identically.
- **Tier C (public DNA-unzipping fallback): Bustamante-group DNA-unzipping optical-trap datasets.** Liphardt et al. 2002, Collin et al. 2005, and follow-ups publish trajectory-level data. These are non-stationary but have been used in prior fluctuation-theorem benchmark work.

The project proceeds on whichever tier passes the Phase 0.5 smoke test first; the paper's scope is labelled accordingly (flagellar / electronic / DNA). Failing all three tiers is a genuine external blocker and the project is paused — but the probability of all three failing is very small, and naming them up front means a single non-response does not kill the project.

### v3 change 2 — reword O2 as ratio measurement with diagnostic protocol (addresses M2)

v2's O2 framed the KUR-vs-TUR check as "KUR ≤ TUR, or the theorem is violated." The reviewer correctly noted that a measured "KUR > TUR" almost certainly means σ is mis-estimated, the chosen observable is not a valid current for the KUR derivation, or the state-space coarse-graining is wrong — not a theorem violation.

v3 replaces O2 with a three-part binary outcome:

- **(O2a) The measured KUR/TUR ratio is reported with bootstrap 95% CI.** This is a measurement, not a theorem test.
- **(O2b) If the CI lies entirely in (0, 1], the theoretical prediction is confirmed at that dataset.** If the CI lies entirely in (1, ∞), the project activates the **diagnostic protocol**: (i) check for time-series stationarity violations; (ii) check for hidden-state coarse-graining by increasing the Markov-order of the inferred transition matrix; (iii) check whether the chosen observable is a valid current under KUR assumptions. The outcome of the diagnostic is reported. The paper does not claim a theorem violation unless all three diagnostics return negative — and even then the paper frames it as "anomalous" and invites independent re-measurement, not "KUR refuted."
- **(O2c) If the CI straddles 1.0, the measurement is inconclusive at the dataset's precision.** This is the most likely outcome on short Tier-A time-series and is publishable as a null with specified precision requirements for future follow-up.

The "Markov system violating TUR" language is removed from v3 entirely.

## 3. Why now

Same as v2. Skinner-Dunkel 2021 established the σ-inference protocol; Van Vu-Hasegawa 2022 derived the KUR; no empirical KUR evaluation has been published on any biological single-molecule dataset or Pekola-group electronic dataset. The Phase 0 lit review will actively search 2023–2026 for Ohga-Ito-Kolchinsky 2023 PRL, Van der Meer 2023 follow-up, and Pekola-group-associated KUR tests before any Phase 0.25 claim.

## 4. Pre-registered binary kill-outcomes (updated)

- **(O1) Data accessibility.** At least one of the three tiers is verified accessible with per-trajectory resolution before Phase 0 opens. Otherwise Phase 0.5 BLOCKED.
- **(O2a, O2b, O2c)** As defined in §2 above. Each outcome is publishable in its appropriate frame.
- **(O3) Tightness scales with F.** The ratio (TUR − KUR)/TUR correlates with the Fano factor F via bootstrapped regression with ΔAIC ≥ 2 vs constant-ratio null, or it does not. Either outcome is publishable.
- **(O4) At least one full independent cross-check.** The result in (O3) reproduces on a second dataset within the chosen tier (or across tiers, e.g. electronic + DNA) to within a factor of 2 in the slope, or it does not.

## 5. Named comparators and differentiation (v3 adds Ohga 2023 and Pekola-group sources)

| Comparator | What they did | What we do differently |
|---|---|---|
| Skinner & Dunkel 2021 (*PNAS*) | TUR σ-inference on flagellar traces | Use same data + σ estimator; compute KUR too |
| Manikandan, Gupta & Krishnamurthy 2020 (*PRL*) | TUR as thermodynamic inference on motor data | Cited; orthogonal observable |
| Van der Meer, Ertel & Seifert 2022 (*PRX*) | Entropy-production estimation from trajectories | Cited; complementary machinery |
| Van der Meer 2023 follow-up | Extended trajectory-based inference | Cited; check for KUR overlap |
| Ohga, Ito & Kolchinsky 2023 (*PRL*) | Unified TUR / entropy-production framework | Cited; check overlap with KUR on single-molecule data |
| Di Terlizzi & Baiesi 2019 (*PRE*) | Kinetic-uncertainty estimators | Cited; our KUR follows Van Vu-Hasegawa 2022 unchanged |
| Otsubo et al. 2020 (*PRE*) | Stochastic thermodynamics from dwell times | Cited; complementary dwell-time work |
| Van Vu & Hasegawa 2022 (*J. Phys. A*) | KUR derivation, abstract Markov chains | First empirical application on real single-molecule / single-electron data |
| Barato & Seifert 2015 (*PRL*) | Original TUR | Baseline bound |
| Koski et al. 2015 / Hofmann et al. 2016 (Pekola-group) | Single-electron-box trajectory data | Tier-B dataset source |
| Liphardt et al. 2002 / Collin et al. 2005 (Bustamante-group) | DNA-unzipping optical-trap data | Tier-C dataset source |

## 6. Target venue — PRE primary

Unchanged from v2. **PRE** primary, *J. Stat. Mech.* fallback. Not PRL; not PRX. The 2023 Ohga paper appeared in PRL — we do not attempt PRL because our scope is narrower (ratio measurement on existing data, not a new framework).

## 7. Scope boundaries — what this paper is NOT

- NOT a TUR-violation hunt.
- NOT a new bound.
- NOT a test that will be published if Tier A, B, and C all fail at Phase 0.5.
- NOT a claim of KUR-theorem violation without the diagnostic protocol having been executed and returning negative on all three checks.

## 8. Real-data rule (CLAUDE.md)

Three named public data sources enumerated in §2. No synthetic data at any stage. The tier-cascade is the real-data-first strategy specifically constructed to avoid the "single point of failure" that v2 exposed.
