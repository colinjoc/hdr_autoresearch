**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics: Theory and Experiment

# Is the kinetic uncertainty relation tighter than the TUR on Skinner-Dunkel's single-molecule datasets?

## 1. Question

Skinner & Dunkel (PNAS 2021) inferred entropy-production lower bounds on flagellar-motor and beating-flagellum single-molecule time-series using the Barato–Seifert thermodynamic uncertainty relation (TUR). The kinetic uncertainty relation (KUR) of Van Vu & Hasegawa (2022) postdates their work and is strictly tighter for non-Markovian systems with high dynamical activity. **On the exact datasets Skinner & Dunkel analysed, does the KUR yield a tighter entropy-production estimate than the TUR, and — if so — is the relative tightening monotone in a model-free memory indicator like the Fano factor of the cycle-count distribution?**

The v1 scope check (three-round Phase −0.5 budget; this is round 2) correctly flagged that: (a) a broad "TUR-violation hunt" competes directly with Skinner-Dunkel 2021, Manikandan 2020 and Van der Meer 2022, all uncited; (b) "TUR violation on a Markovian system" is a *tautological* kill-outcome — it's a theorem, not a measurement, so listing it as a finding reveals confusion; (c) "data availability" is a feasibility gate, not falsifiability; (d) σ-from-ATP-stoichiometry is >2× uncertain; (e) PRL/PRX is the wrong target for confirmatory work. v2 addresses each.

## 2. Proposed contribution

**(a) Narrow the scope from broad hunt to direct bound-tightening measurement.** Instead of a broad search for TUR-violating biomolecules (redundant with Skinner-Dunkel 2021), we compute BOTH the TUR bound and the KUR bound on the *identical* time-series Skinner-Dunkel used, and report the ratio KUR / TUR as a function of the dataset's empirical dynamical activity. The theoretical prediction (Van Vu-Hasegawa 2022) is that KUR ≤ TUR strictly, with tightness growing with dynamical activity; our contribution is the first empirical check of this prediction on biological single-molecule data.

**(b) Phase 0.5 data-access gate (must pass before any further work).** The v1 reviewer correctly flagged that single-molecule dwell-time traces are rarely publicly deposited. Before Phase 0 begins, we will:
  - Check the Skinner-Dunkel 2021 PNAS supplementary for any deposited time-series (Dryad, Zenodo, GitHub links).
  - Check the Harvard/MIT motor-data repositories that host Berry lab and Chemla lab flagellar datasets.
  - If the data is behind email-only access, we will attempt one author email with a 2-week response window; the project is Phase 0.5 BLOCKED if no response.
  
  The proposal commits to **not entering Phase 0 until at least one dataset has been verified accessible with per-trajectory resolution**. If only histogram-level data is available, the Var(N)/⟨N⟩² computation cannot be done honestly and the project pauses. This is a hard gate.

**(c) Use Skinner-Dunkel's σ-inference method, not ATP stoichiometry.** The v1 ATP-stoichiometry approach to σ has >2× systematic uncertainty (futile cycles, branching pathways). Adopt the Skinner-Dunkel 2021 trajectory-based σ estimator instead — this is their core methodological contribution, and our paper uses it unchanged. The TUR bound is computed from the same estimator. Consistency is enforced at the method level.

**(d) Model-free memory indicator.** Replace v1's Erlang-k parametric fit with the Fano factor F = Var(N) / ⟨N⟩ of the cycle-count distribution over matched observation windows — a model-free measure of deviation from Poisson (Markovian) statistics. F = 1 for a Poisson process (perfectly Markovian); F > 1 for clustering/bursty (non-Markovian) dynamics; F < 1 for anti-bunched. The relative KUR tightening is a function of F; we pre-register that |KUR/TUR − 1| scales monotonically with F across datasets.

**(e) Drop the tautological kill-outcome entirely.** The v1 "TUR violation on a Markovian system" kill-outcome is removed from v2. In its place, (O3) below tests whether KUR gives *zero* tightening (TUR = KUR to within CI) on approximately-Markovian systems (F ≈ 1), which would confirm the theoretical prediction without mistaking it for a falsifiable finding.

## 3. Why now

- **Skinner & Dunkel 2021 (PNAS)** established a reliable σ-inference protocol from single-molecule time-series and applied the TUR. Their framework is the starting point.
- **Van Vu & Hasegawa 2022 (*J. Phys. A*)** derived the KUR, strictly tighter than TUR. They applied it to abstract Markov chains — no experimental data.
- **Di Terlizzi & Baiesi 2019 / Otsubo et al. 2020** developed kinetic-style entropy-production estimators compatible with the KUR machinery.

The literal gap: KUR has not been evaluated on any published single-molecule dataset. Closing this is a narrow but concrete contribution.

## 4. Pre-registered binary kill-outcomes

- **(O1, gate) Data accessibility.** At least one single-molecule dataset (flagellar, motor, or ribosomal) with per-trajectory time-resolution is verified accessible — via public deposition or responsive author email — before Phase 0 opens. Otherwise project is paused at Phase 0.5 BLOCKED.
- **(O2) KUR ≤ TUR empirically.** On every accessible dataset, KUR ≤ TUR within the bootstrap 95% CI, or this theoretical prediction is violated empirically — either outcome is publishable (the second would be a major result requiring careful scrutiny of the σ estimator).
- **(O3) Tightness scales with F.** The ratio (TUR − KUR)/TUR either correlates with F via a bootstrapped regression with ΔAIC ≥ 2 vs constant-ratio null, or it does not. Monotone scaling is expected but not assumed.
- **(O4) At least two datasets.** The above tests are performed on at least two independent datasets (e.g., flagellar motor AND ribosome) to avoid a single-system artefact. If only one dataset is accessible, the scope of the paper is reduced and the title reflects the single system.

## 5. Named comparators and differentiation

| Comparator | What they did | What we do differently |
|---|---|---|
| Skinner & Dunkel 2021 (*PNAS*) | σ-inference on flagellar-motor + beating-flagellum time-series; TUR bound evaluated | We use their datasets and σ estimator; add the KUR comparison and the F-memory regression — no competing new method |
| Manikandan, Gupta & Krishnamurthy 2020 (*PRL*) | TUR as thermodynamic inference on molecular motor data | Complementary but orthogonal observable; cited; no overlap in observables |
| Van der Meer, Ertel & Seifert 2022 (*PRX*) | Entropy-production estimation from trajectories | Cited; our measurement uses a narrower TUR/KUR ratio, not a full estimation |
| Di Terlizzi & Baiesi 2019 (*PRE*) | Kinetic-uncertainty estimators | Cited; our KUR instance follows Van Vu-Hasegawa 2022 formulation directly |
| Otsubo et al. 2020 (*PRE*) | Stochastic thermodynamics from experimental dwell-time | Cited; complementary dwell-time machinery |
| Van Vu & Hasegawa 2022 (*J. Phys. A*) | KUR derivation, abstract Markov chains | First empirical application |
| Barato & Seifert 2015 (*PRL*) | Original TUR | Baseline bound |

A focused Phase 0 literature search will scan 2023–2026 *PRE*, *JSTAT*, *PRX*, *PNAS*, *Biophys. J.* for any paper whose title combines KUR, single-molecule, and empirical — pre-empting the round-1 risk of missing a published precursor.

## 6. Target venue — PRE primary

**Physical Review E** — publishes empirical evaluations of stochastic-thermodynamics bounds on experimental data. The v1 reviewer's explicit recommendation; v2 adopts it.

**Fallback: *J. Stat. Mech.*** — tolerant of narrow-scope empirical work if the result is a confirmation / null. Open to data-constrained studies with explicit scope restriction.

**NOT attempted:** PRL (not a crisp theorem result), PRX (not a broad methodological advance), *Biophys. J.* (the observable is thermodynamic, not biological).

## 7. Scope boundaries — what this paper is NOT

- NOT a search for TUR-violating biomolecular systems (the v1 framing). That is Skinner-Dunkel's question.
- NOT a new bound or theorem.
- NOT a cross-substrate comparison with ML.
- NOT a claim that will be published if data access fails at the Phase 0.5 gate.

## 8. Real-data rule (CLAUDE.md)

This project uses only published experimental single-molecule data. The data-access gate (O1) ensures no synthetic substitute is introduced if real data is unavailable — the project pauses instead.
