# Scope Check — Bérut finite-time Landauer refit

## 1. Novelty of the proposed contribution

Narrow-and-plausible, but the claim "first refit of the full Bérut curve under Proesmans" is the kind of thing reviewers like to puncture. The three closest comparators a PRE reviewer will reach for:

- **Proesmans, Ehrich & Bechhoefer, PRL 125, 100602 (2020)** and its PRE long-form companion (PRE 102, 032105, 2020). They derive B = π² and discuss Bérut explicitly. A reviewer will want to know whether the long-form PRE paper already shows the ten-point curve in a figure with a π²/τ line overlaid — if it does, even without CI analysis, the "never refit" novelty claim collapses to "first bootstrap CI on B." That is a much thinner paper.
- **Dago, Ciliberto, Bellon et al. (PRL 2021; PRX 2022)** — finite-time Landauer under modulated double-wells. They already do time-resolved dissipation fits in a Bérut-adjacent apparatus; a reviewer will ask why the refit is not done against their cleaner data.
- **Zulkowski & DeWeese, PRE 89, 052140 (2014)** and related optimal-protocol literature — they gave protocol-dependent finite-time coefficients years before Proesmans. The "π² is the prediction for Bérut" framing has to survive this.

Novelty is defensible but brittle. The asymmetric B(r) = π²(1+r)²/(4r) extension is the only genuinely new piece, and it is self-cited from an earlier in-house preprint that a reviewer has no reason to credit.

## 2. Falsifiability and the r-identifiability leg

The three binary outcomes are genuinely pre-registered and genuinely falsifiable — good. The r-identifiability leg is the weak joint. "Reconstruct U(x) from the Bérut supplementary and extract r = V_left/V_right" sounds crisp in a proposal; in practice Bérut 2012 reports trap stiffnesses and inter-well separations, not a calibrated asymmetric potential. If r must be back-inferred from photodiode traces that are not in the public SI, leg (b) is an uncontrolled hidden-variable step and the asymmetric test becomes "we picked r to see what happens," which is exactly the parameter-tuning freedom the proposal denies. The honest pre-commitment — "if r is worse than factor-2 we report that null" — is defensible but almost certainly the outcome, at which point the paper is a one-result refit of a single symmetric prediction.

## 3. Venue fit

PRE is acceptable but not obvious. An empirical refit of one 2012 dataset with ten points and bootstrap error bars is on the lower end of PRE's novelty bar. J. Stat. Mech. or New J. Phys. is the more natural home — both publish exactly this grain of methodology-plus-test paper without demanding a framework-level contribution. Lead with PRE, but the fallback is load-bearing.

## 4. Most likely killer objections

(i) Ten data points cannot distinguish π² from π²(1+r)²/(4r) at realistic r unless r is far from 1 and σ_B is small — a power analysis is missing. (ii) Bérut's published error bars are known to be optimistic; propagating them as-is will be challenged.

VERDICT: PROCEED
