# Scope Check v3 (Phase -0.5, Round 3 of 3)

Reviewer: fresh sub-agent, grouchy stochastic-thermodynamics. Read: program.md Phase -0.5 + proposal_v3.md only.

## 1. Is the three-tier cascade actually protective?

Partially. Tier A (Skinner-Dunkel flagellar) and Tier B (Pekola single-electron box) share the stuff that matters for this paper: stationary cycle-counting trajectories with integer jump counts N over long windows, from which Var(N)/<N> (Fano) and the Skinner-Dunkel sigma estimator are well-defined. Good fallback. Tier C (Bustamante DNA-unzipping), on the other hand, is a *non-stationary* pulling experiment — the observable is extension vs force ramp, not a counted current on a stationary cycle. The KUR and TUR in the Barato-Seifert / Van Vu-Hasegawa form assume NESS with a defined integer current; Crooks/Jarzynski-style DNA data does not give you that without major reformulation. Tier C is therefore closer to cosmetic than substantive — if both A and B fail, the paper changes shape, not just its label. That's tolerable as a genuine last-resort fallback, but the proposal should not present C as a drop-in for A or B. MAJOR-leaning-MINOR.

## 2. Is O2 genuinely non-tautological now?

Yes, the framing is fixed — this is now a ratio measurement, not a theorem test, which is correct. But "operational enough to pre-register" is weaker than it reads. The three diagnostic checks (stationarity, Markov-order increase, observable-validity) are named but not specified: which stationarity test, which threshold; up to what Markov order and by which estimator; what "valid current under KUR assumptions" means operationally (is it a linear combination of edge fluxes? an antisymmetric observable?). Pre-registration needs numbers and tests named, not just concepts. Patchable at Phase 0.25 but currently under-specified.

## 3. Coherence across tiers

Weak but defensible. The unifying story is "KUR/TUR tightness ratio vs a model-free memory indicator (Fano) across substrates." If A + B both run, that's a genuinely nice cross-substrate comparison. If only one tier runs, it becomes a single re-analysis — honest, but smaller. Title/abstract must be written tier-conditional.

## 4. Venue

PRE primary still correct. *J. Stat. Mech.* fallback remains right. Entropy not needed.

## 5. Top three killer objections

- **(major) Tier C mismatch.** DNA-unzipping data is non-stationary and lacks a clean counted current. Mitigation: restrict Tier C to stationary hopping regimes only, or drop C and name a second stationary source (e.g. Ritort-group colloidal, Ciliberto-group) instead.
- **(major) Diagnostic protocol under-specified.** Name the stationarity test (ADF / KPSS), the Markov-order sweep range (k = 1..4) and selection criterion (BIC), and the current-validity check (antisymmetry under time reversal) before Phase 0 closes.
- **(minor) Pekola data resolution.** Pekola single-electron datasets can have short run lengths relative to what Fano-vs-ratio regression needs. Mitigation: power-analyze required trajectory length in Phase 0.5 before committing.

None fatal. v3 patched both M1 and M2 enough to continue.

VERDICT: PROCEED
