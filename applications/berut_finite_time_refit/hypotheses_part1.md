# Hypotheses / candidate experiments — Part 1 (Themes 1 & 2)

50+ hypotheses for the Bérut 2012 finite-time Landauer refit. Each entry
has: ID, statement, Bayesian prior (0–1), mechanism (one line), expected
outcome. Priors are the author's best estimate before Phase 0.5 analysis.

---

## Hypotheses on the empirical B fit

**H1.** The Bérut ten-point curve admits a stable fit to kT ln 2 + B·kT/τ.
Prior: 0.85. Mechanism: the 1/τ scaling is theoretically robust and the
data visually shows it. Expected outcome: fit converges to a B ∈ [3, 50]
with finite CI.

**H2.** The 95% bootstrap CI on fitted B *contains* π² ≈ 9.87.
Prior: 0.55. Mechanism: Bérut's quasistatic verification suggests the
protocol is 'close to optimal' at its cleanest regime. Expected: either
in or out with roughly equal prior weight.

**H3.** The 95% CI on B *contains* B(r) = π²(1+r)²/(4r) at some
plausible r ∈ [1.1, 3]. Prior: 0.35. Mechanism: the asymmetric formula
can accommodate a larger B; if the realised r > 1, the prediction
shifts up. Expected: if r > 1 is extractable, CI may prefer asymmetric.

**H4.** Adding a 1/τ² correction significantly improves fit quality (F-
test p < 0.05). Prior: 0.40. Mechanism: Miller et al. 2019 show slow-
process corrections scale 1/τ². Expected: F-test favours 3-param model
at short τ.

**H5.** The short-τ points (τ < Kramers time) show dissipation in excess
of the pure 1/τ law. Prior: 0.70. Mechanism: under-thermalised
trajectories contribute additional dissipation. Expected: residuals at
short τ are positive.

**H6.** The long-τ points (τ > 5 × Kramers time) lie within 1σ of
kT ln 2. Prior: 0.85. Mechanism: quasistatic limit reached. Expected:
confirmed.

**H7.** The fit is *degenerate*: the 95% CI on B is unbounded above.
Prior: 0.10. Mechanism: ten points + three parameters may produce a
poorly constrained fit. Expected: refit produces a flat χ² surface.

**H8.** Using parametric bootstrap (resampling from fitted Gaussian)
gives tighter CI than nonparametric bootstrap (resampling trajectories).
Prior: 0.65. Mechanism: parametric exploits fitted variance;
nonparametric respects empirical tails. Expected: 10–30% tighter
parametric CI.

**H9.** Heteroskedastic weighting (weights ∝ 1/σ²_i) materially shifts
the fitted B compared to unweighted. Prior: 0.70. Mechanism: σ_i varies
across τ in Bérut. Expected: B shifts by ≥ 20%.

**H10.** The fit is robust to dropping any single data point (leave-
one-out CI contains the full-dataset point estimate). Prior: 0.80.
Mechanism: ten-point fit should not be dominated by one point. Expected:
confirmed modulo the shortest-τ outlier.

---

## Hypotheses on r-identifiability (the weak joint)

**H11.** r is extractable from the Bérut stiffnesses alone to factor-2
precision. Prior: 0.25. Mechanism: stiffnesses constrain curvature but
not depth. Expected: r has a wide CI, potentially including r = 1.

**H12.** r is extractable to 10% precision from the Bérut supplementary
histograms. Prior: 0.20. Mechanism: histograms would need long
bistable-regime sampling; unclear whether SI includes it. Expected:
supplement lacks the needed histograms.

**H13.** r is extractable to 30% precision using Kramers-rate asymmetry
from Bérut trajectories. Prior: 0.35. Mechanism: barrier-crossing rate
ratio gives an independent handle on depth asymmetry. Expected:
feasible if trajectories are available.

**H14.** r extracted from stiffness and r from histogram agree within
their joint error bars. Prior: 0.50. Mechanism: both should reflect the
same potential; any disagreement indicates model misspecification.

**H15.** Non-conservative optical forces (Pesce et al. 2009) inflate the
histogram-derived r by ≥ 10%. Prior: 0.40. Mechanism: scattering-force
component biases equilibrium distribution. Expected: correction
detectable but small.

**H16.** r ≠ 1 at significance > 2σ in the Bérut apparatus. Prior: 0.45.
Mechanism: two-foci traps are rarely perfectly balanced. Expected:
small but non-zero asymmetry.

**H17.** r > 1.2 (asymmetric test distinguishable from symmetric).
Prior: 0.25. Mechanism: large asymmetry unlikely in a carefully
balanced setup. Expected: borderline.

**H18.** The bulkiest source of r uncertainty is bead polydispersity.
Prior: 0.30. Mechanism: 1 μm beads have ~5% size variation; κ scales
with a², so depth scales with κ·a² ∝ a⁴. Expected: ~20% r uncertainty
from this alone.

**H19.** A Bayesian joint fit of r and B gives a tighter B CI than
assuming r = 1. Prior: 0.55. Mechanism: marginalizing r over prior
incorporates uncertainty rigorously. Expected: CI width marginally
tighter.

**H20.** The r = 1 slice of the 2D likelihood excludes the data (p <
0.05 for r-fixed-at-1 null). Prior: 0.25. Mechanism: if r ≠ 1 at all,
the symmetric assumption biases the fit. Expected: fit-quality
degradation when r is fixed.

---

## Hypotheses on systematic/calibration issues

**H21.** Re-calibrating γ using modern Faxen corrections (Berg-Sørensen
and Flyvbjerg 2004) shifts fitted B by ≥ 5%. Prior: 0.50. Mechanism:
wall-proximity corrections were cruder in 2012. Expected: B shifts up.

**H22.** Effective temperature (laser heating) raises the true bath T
by 1–3 °C, which lowers B in units of the true T. Prior: 0.70.
Mechanism: Rings, Selmke, Cichos and Kroy 2011. Expected: 1–3% shift.

**H23.** Photodiode non-linearity at large displacements (~500 nm) adds
a systematic that cannot be bootstrap-captured. Prior: 0.35. Mechanism:
position detection saturates for large x. Expected: small but
detectable bias at short τ.

**H24.** The Bérut bootstrap error bars are optimistic by a factor of
1.5–2 relative to the TUR floor at each τ. Prior: 0.55. Mechanism:
bootstrap ignores some systematic error sources. Expected: the CI must
be inflated for a refit.

**H25.** Hydrodynamic memory (non-Markovian drag) biases ⟨Q⟩ by < 1%
for Bérut's τ range. Prior: 0.80. Mechanism: bead inertial time ~μs,
far below τ. Expected: negligible.

**H26.** The trap stiffness in the bistable regime is not constant —
it depends on bead position between the two foci. Prior: 0.85.
Mechanism: two-beam interference produces position-dependent
intensity. Expected: must be modeled carefully in reconstruction.

**H27.** The 'no-erasure' Bérut control points show zero excess heat at
all τ within error. Prior: 0.75. Mechanism: no protocol work → no
excess dissipation. Expected: confirmed; if not, signals systematic.

**H28.** Using the Gieseler et al. (2021) modern tutorial recipe for r
extraction produces a 20–30% tighter r CI than Bérut's implicit method.
Prior: 0.60. Mechanism: Bayesian + modern corrections. Expected: yes.

---

## Hypotheses on competing predictions

**H29.** Van Vu and Saito's (2022) tight finite-time bound gives B ≈ π²
in Bérut's regime. Prior: 0.70. Mechanism: their bound reduces to
Proesmans for overdamped symmetric cases. Expected: confirmed;
predictions coincide.

**H30.** Zhen et al. (2021) bound is excluded by the Bérut fit at short
τ. Prior: 0.40. Mechanism: their bound is tighter. Expected: if fit
gives B > π², Zhen is ruled out.

**H31.** Zulkowski and DeWeese (2014) Hellinger-distance coefficient
is contained in the fit CI. Prior: 0.60. Mechanism: it is similar to
π² for symmetric case. Expected: both included.

**H32.** Schmiedl and Seifert's (2007) coefficient for the
specific Bérut control parameter differs from π² by an order-unity
factor. Prior: 0.55. Mechanism: S-S coefficient is
control-parameter-dependent. Expected: discrepancy detectable.

**H33.** A protocol-specific simulation of the Bérut cycle in a
Brownian-dynamics code reproduces the ten ⟨Q_diss⟩ points within Bérut
error bars. Prior: 0.75. Mechanism: we know the trap parameters;
simulation is direct. Expected: yes; provides ground-truth B.

**H34.** The simulated Bérut cycle has B strictly greater than π² — i.e.,
Bérut's protocol does not saturate Proesmans. Prior: 0.70. Mechanism:
Bérut's protocol is smooth and has no jumps, unlike the optimal one.
Expected: simulated B ∈ [1.2, 2] × π².

**H35.** Dago (2021) overdamped data give a B consistent with Bérut's.
Prior: 0.65. Mechanism: same overdamped regime, similar protocol family.
Expected: consistent.

**H36.** Jun, Gavrilov and Bechhoefer (2014) feedback-trap data, if
fit to the same form, give a B consistent with Bérut. Prior: 0.55.
Mechanism: different apparatus; should agree if Proesmans is universal.
Expected: useful cross-check.

**H37.** Roldán, Martínez, Parrondo and Petrov (2014) symmetry-
breaking energetics data fit the same B·kT/τ scaling. Prior: 0.45.
Mechanism: different protocol, but same underlying physics. Expected:
useful comparator; B may differ.

---

## Hypotheses on higher-order structure

**H38.** A sub-leading 1/τ² term is detectable in the Bérut curve with
coefficient ~2π² (Bonanca-Deffner 2014 prediction). Prior: 0.30.
Mechanism: specific Gaussian-work tail correction. Expected:
marginal signal.

**H39.** The fit residuals show systematic curvature inconsistent with
pure 1/τ. Prior: 0.35. Mechanism: mis-specified functional form.
Expected: if present, signals need for higher-order model.

**H40.** Machta et al.'s (2013) parameter-space compression analysis
shows B and r are statistically indistinguishable from ten points.
Prior: 0.45. Mechanism: limited sample size. Expected: identifies a
sloppy direction in parameter space.

**H41.** Including Dago (2021) overdamped data as a second dataset
tightens the joint B CI by ~30%. Prior: 0.60. Mechanism: more data →
tighter CI. Expected: yes.

**H42.** The leading 1/τ coefficient depends on barrier height; Bérut's
B is in the ~3 kT barrier regime, which is *not* the high-barrier
asymptotic limit that Proesmans analyse. Prior: 0.55. Mechanism:
finite-barrier correction. Expected: 10–30% shift in B.

**H43.** Adding a barrier-height-dependent correction B(V) = π²·f(V/kT)
to the fit improves χ² when cross-comparing Bérut (V~3kT), Dago
(V~10kT), and Jun (V~5kT). Prior: 0.50. Mechanism: different barrier
heights. Expected: coefficient shifts systematically with V.

---

## Hypotheses on experimental falsification of the formula

**H44.** The fitted B lies strictly above π²(1+r_max)²/(4·r_min) for
all r ∈ [1, r_max] where r_max is the r CI upper limit — i.e., the
asymmetric formula is falsified at any plausible r. Prior: 0.20.
Mechanism: would require the data to strongly exclude all asymmetric
variants. Expected: rare but would be the strongest result.

**H45.** The fitted B lies strictly below π² — Proesmans is falsified
in its conservative form. Prior: 0.15. Mechanism: Bérut's measurement
is below the 'optimal' bound, which would be surprising but possible
if error bars are genuinely off. Expected: rare.

**H46.** The fitted B is bounded above by a protocol-specific value that
can be derived from Bérut's trap parameters and the Schmiedl-Seifert
formalism. Prior: 0.55. Mechanism: protocol dictates B. Expected:
reasonable agreement.

**H47.** A Bayesian model-comparison of {Proesmans π², Zhen et al.,
Van Vu-Saito, Zulkowski-DeWeese, B(r)} against the Bérut data
identifies a clear winner with log-evidence > 2. Prior: 0.30.
Mechanism: ten-point data may discriminate. Expected: borderline.

**H48.** The fit is *equally consistent* with symmetric Proesmans and
asymmetric B(r) for r extracted from the apparatus — i.e., the data is
insufficient to discriminate. Prior: 0.45. Mechanism: scope check (i)
concern. Expected: likely outcome.

---

## Hypotheses on methodology and reproducibility

**H49.** Re-implementing the Bérut bootstrap using modern code (scipy +
emcee) produces CIs consistent with the 2012 published bars within
20%. Prior: 0.75. Mechanism: standard method. Expected: yes.

**H50.** Publishing the refit code on GitHub enables at least one
independent reproduction within six months. Prior: 0.55. Mechanism:
open science. Expected: yes if paper gets traction.

**H51.** The Dago (2022) heat-partition analysis (overdamped vs
underdamped) can be cross-checked against the Bérut data, yielding an
independent estimate of γ. Prior: 0.40. Mechanism: different
apparatus; common physics. Expected: useful methodology check.

**H52.** A simulator calibrated to Bérut's parameters reproduces the
ten-point curve within error bars. Prior: 0.75. Mechanism: direct
BD simulation. Expected: essential TDD step.

**H53.** A simulator with the same parameters but r set arbitrarily
(e.g. 1.5, 2.0) produces a fitted B that obeys B_sim ≈ B(r_sim) to
within 5%. Prior: 0.60. Mechanism: the asymmetric formula is the
correct prediction. Expected: validates or falsifies the prediction
by simulation before it meets Bérut data.

**H54.** Under-specified Bérut metadata (e.g., exact protocol shape)
can be reverse-engineered from the ten ⟨Q_diss⟩ points + simulator.
Prior: 0.40. Mechanism: fit protocol parameters to match data. Expected:
partial; some degeneracy.

**H55.** A minimum-variance unbiased estimator (MVUE) for B under
Gaussian error bars gives a materially different point estimate than
weighted least-squares. Prior: 0.30. Mechanism: MVUE accounts for
heteroskedasticity correctly. Expected: small shift.

---

## Additional reviewer-pre-emption hypotheses

**H56.** The scope-check concern (i) (ten points cannot distinguish π²
from B(r) at realistic r) is confirmed by a formal power analysis.
Prior: 0.70. Mechanism: low statistical power. Expected: honest
pre-commitment required.

**H57.** The scope-check concern (ii) (Bérut error bars optimistic) is
confirmed by TUR floor analysis. Prior: 0.55. Mechanism: see H24.
Expected: inflate CI for publication.

**H58.** Re-running the Bérut experiment (Ciliberto group at ENS Lyon,
or Bechhoefer group at SFU) would produce a ~100-point curve with
5–10× tighter error bars. Prior: 0.85. Mechanism: 12 years of
apparatus improvement. Expected: yes if institutional access
available. (Not in scope for this project; mentioned as fallback.)

**H59.** The asymmetric formula B(r) = π²(1+r)²/(4r) can be derived
from optimal-transport (Aurell et al. 2011) for asymmetric double
wells. Prior: 0.55. Mechanism: generalise the symmetric OT proof.
Expected: plausible; worth checking.

**H60.** The asymmetric formula can be derived from thermodynamic-
length arguments with an asymmetric metric. Prior: 0.50. Mechanism:
Sivak-Crooks 2012. Expected: plausible.
