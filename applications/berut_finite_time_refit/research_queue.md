# Research Queue — Bérut Finite-Time Refit

115 hypotheses drawn from themes 1-4. Each entry gives a Bayesian prior, proposed mechanism, and expected outcome. Top-priority hypotheses (prior > 0.7) are tagged for Phase 2 execution.

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

---

# Hypotheses — Part 2 (Themes 3 and 4)

Format for each: **id** — hypothesis, prior, mechanism, design variable / metric, baseline.

---

## Group A — Empirical refit of the ten-point Bérut curve (symmetric B test)

**H2-001**. Bootstrap refit of the ten Bérut (tau, ⟨Q_diss⟩) points against k_B T ln 2 + B k_B T / tau yields a finite B with a 95 percent CI of order ±0.5 π².  
*Prior*: 0.7. *Mechanism*: 10 points × ±0.15 k_B T noise are enough to constrain B at ± factor 2 but not better. *Design variable*: bootstrap sample size. *Metric*: width of B CI. *Baseline*: 2-parameter fit to Arrhenius + 1/tau.

**H2-002**. The point-estimate fitted B is greater than π² at > 3σ.  
*Prior*: 0.5. *Mechanism*: Bérut's smooth-protocol excess over optimal protocol is expected to increase dissipation by a factor of order 1-10. *Metric*: z-score of B relative to π². *Baseline*: Proesmans 2020 lower bound.

**H2-003**. The Bérut tau = 40 s point alone is inconsistent with B = π² at > 2σ.  
*Prior*: 0.3. *Mechanism*: at tau = 40 s the 1/tau correction is only ~ 0.25 k_B T, comparable to the error bar, so discrimination is marginal.

**H2-004**. The Bérut tau = 5 s point is consistent with B = π² within 1σ.  
*Prior*: 0.5. *Mechanism*: at shorter tau the 1/tau correction is larger relative to noise, so if the data obey Proesmans the shortest-tau points should fit best.

**H2-005**. The 95 percent CI on B excludes B = π²(1+r)²/(4r) for the worst-case r from the Bérut SI.  
*Prior*: 0.2. *Mechanism*: as demonstrated in knowledge base F3.26, the asymmetric factor (1+r)²/(4r) is insensitive to r near r = 1, so discrimination is unlikely.

**H2-006**. A two-parameter fit (B, T_eff) to the Bérut curve yields T_eff within 5 percent of measured bath temperature.  
*Prior*: 0.8. *Mechanism*: standard colloidal systems are well-thermalised at kHz-and-slower timescales.

**H2-007**. Fitting k_B T ln 2 + A + B/tau to the curve (adding a constant offset) yields A consistent with 0 at 95 percent CI.  
*Prior*: 0.7. *Mechanism*: Landauer bound has no adjustable offset for symmetric erasure.

**H2-008**. Fitting an exponential-decay model ⟨Q_diss⟩(tau) = Q_0 + A exp(-tau/tau_rel) instead of 1/tau gives higher reduced chi².  
*Prior*: 0.6. *Mechanism*: the 1/tau scaling is the Proesmans prediction; alternative shapes should fit worse.

**H2-009**. The Bérut published ±0.15 k_B T error bars are optimistic; a propagated systematic uncertainty (AOD, laser drift, Boltzmann-inversion bias) inflates them by at least factor 1.5.  
*Prior*: 0.7. *Mechanism*: scope-check reviewer's objection (ii).

**H2-010**. Removing the tau = 40 s point (quasistatic limit, high leverage) from the fit changes the B estimate by less than 1σ.  
*Prior*: 0.5. *Mechanism*: if the Proesmans model is correct, the long-tau point provides the offset ln 2 and the short-tau points provide B; removal of the offset anchor should not shift B much.

---

## Group B — Asymmetry identifiability and B(r) discrimination

**H2-011**. The well-depth asymmetry r reconstructed from the digitised Bérut U(x) has 95 percent CI of 0.7–1.5 in the high-barrier condition.  
*Prior*: 0.6. *Mechanism*: digitisation-error analysis in knowledge base F3.25.

**H2-012**. The well-depth asymmetry r in the low-barrier condition has 95 percent CI of 0.5–2.  
*Prior*: 0.6. *Mechanism*: shallower wells have less statistical leverage in the histogram.

**H2-013**. The AOD diffraction asymmetry in the Bérut apparatus contributes > 10 percent of the systematic uncertainty budget on r.  
*Prior*: 0.5. *Mechanism*: Valentine 2008 (T4_033).

**H2-014**. The laser-power drift over 50 minutes of Bérut acquisition contributes > 3 percent to the well-depth asymmetry uncertainty.  
*Prior*: 0.5. *Mechanism*: typical 1064 nm diode-pumped laser stability.

**H2-015**. B(r) = π²(1+r)²/(4r) evaluated at r = 1 ± 30 percent gives B within 3 percent of π².  
*Prior*: 0.9. *Mechanism*: (1+r)²/(4r) has vanishing derivative at r = 1.

**H2-016**. Tkachenko drift-field inference from raw photodiode traces (if available) would tighten r precision by factor > 3 compared to histogram inversion.  
*Prior*: 0.6. *Mechanism*: drift-field uses more information than equilibrium histogram. Source: Frishman-Ronceray 2020 (T4_101).

**H2-017**. The Bérut polynomial U(x) coefficients, if tabulated, would reduce r uncertainty to ±10 percent.  
*Prior*: 0.7. *Mechanism*: polynomial coefficients encode the full shape, not just visible features.

**H2-018**. Given the irreducible uncertainty on r, the discrimination test between B = π² and B(r) = π²(1+r)²/(4r) is formally inconclusive.  
*Prior*: 0.8. *Mechanism*: KB F3.26.

**H2-019**. A reframe of the project to a pure symmetric-Proesmans-refit paper has the same publishability as the original proposal.  
*Prior*: 0.6. *Mechanism*: discrimination result is bonus, refit is primary.

**H2-020**. Chiu-Lu-Jun 2022 (T3_089) present feedback-trap asymmetric-well finite-time Landauer data that already tests B(r); our Bérut refit is not the first asymmetric test.  
*Prior*: 0.8. *Mechanism*: direct read of T3_089 — they probe B(r) in explicit asymmetric wells.

---

## Group C — Alternative protocols and bound saturation

**H2-021**. The empirical B from Bérut should differ from π² by more than factor 2 because Bérut used a non-optimal protocol.  
*Prior*: 0.6. *Mechanism*: smooth barrier-lowering is suboptimal relative to Schmiedl-Seifert jumps.

**H2-022**. Using the Schmiedl-Seifert optimal protocol with the Bérut trap geometry, the extracted B would be closer to π² at 10 percent.  
*Prior*: 0.7. *Mechanism*: design of optimal protocol.

**H2-023**. The Hellinger-distance bound (Zulkowski-DeWeese 2014) predicts a tighter B at tau > 30 s than Proesmans.  
*Prior*: 0.5. *Mechanism*: Hellinger is tighter quasi-statically, looser finite-time.

**H2-024**. Zhen-Egloff-Modi-Dahlsten 2021 (T3_060) bound applied to Bérut gives same B in the zero-error limit.  
*Prior*: 0.9. *Mechanism*: both reduce to π²/tau in zero-error, equal-initial-probability regime.

**H2-025**. The Barato-Seifert TUR (T3_107) applied to Bérut gives a weaker B lower bound than Proesmans in this regime.  
*Prior*: 0.6. *Mechanism*: TUR is a general bound, often loose for specific protocols.

---

## Group D — Optical-trap potential reconstruction precision

**H2-026**. A 6th-degree polynomial is sufficient to capture the Bérut U(x) shape within 0.05 k_B T at all tested points.  
*Prior*: 0.8. *Mechanism*: standard Bérut methodology.

**H2-027**. A 4th-degree polynomial fit would introduce systematic bias in the well-depth asymmetry of ~ 0.2 k_B T.  
*Prior*: 0.5. *Mechanism*: lower-order truncation is insufficient for non-symmetric shapes.

**H2-028**. Boltzmann inversion finite-sample bias on U(x) is negligible compared to the error bar on Q_diss for the Bérut sample size.  
*Prior*: 0.8. *Mechanism*: KB F3.9 computation.

**H2-029**. Photodiode nonlinearity contributes < 0.01 k_B T systematic bias to U(x).  
*Prior*: 0.6. *Mechanism*: typical quadrant-photodiode nonlinearity 0.1-1 percent.

**H2-030**. The Bérut position tracking is limited by the 108 nm/pixel raw resolution; the post-processed > 5 nm claim is consistent with Bérut 2015 but not audited.  
*Prior*: 0.5. *Mechanism*: T3_048.

**H2-031**. Cramer-Rao lower bound on the polynomial coefficients at N = 10⁵ effective samples gives ± 3 percent on each polynomial coefficient.  
*Prior*: 0.6. *Mechanism*: T4_189.

**H2-032**. Alternative inference (drift-field Kramers-Moyal) would require dt << min(gamma/omega²) and hence sample rates of > 5 kHz; Bérut's 502 Hz is inadequate.  
*Prior*: 0.7. *Mechanism*: Ragwitz-Kantz 2001 (T4_064).

**H2-033**. Bayesian inference of the Bérut U(x) with informative priors on the inter-well separation yields r with tighter CI than the frequentist polynomial fit.  
*Prior*: 0.6. *Mechanism*: Bayesian advantage under informative priors.

**H2-034**. The PSD calibration of the Bérut trap has ≤ 5 percent uncertainty on the stiffness.  
*Prior*: 0.8. *Mechanism*: Berg-Sørensen-Flyvbjerg 2004.

**H2-035**. Absolute calibration of the trap force (Viana et al. 2007, T4_028) has not been done for Bérut and contributes 10-20 percent to absolute stiffness uncertainty.  
*Prior*: 0.7. *Mechanism*: PSD gives relative calibration, not absolute.

---

## Group E — Underdamped/quasi-Markovian alternatives

**H2-036**. In the overdamped limit appropriate for 2 μm silica in water, inertia corrections to the Proesmans B are < 1 percent.  
*Prior*: 0.9. *Mechanism*: Reynolds number << 1.

**H2-037**. Memory-friction (viscoelastic fluid) effects add < 5 percent to the dissipation at tau > 1 s.  
*Prior*: 0.7. *Mechanism*: water at 1 μm scale has no measurable viscoelasticity.

**H2-038**. Dago-Ciliberto-Bellon 2022 underdamped data are incompatible with the overdamped Proesmans prediction and not directly comparable.  
*Prior*: 0.8. *Mechanism*: different regime.

**H2-039**. Non-Gaussian noise effects in the Bérut apparatus (Lisowski et al. 2015, T3_161) are negligible at the achievable statistical power.  
*Prior*: 0.9. *Mechanism*: water at room T is Gaussian-noise standard.

---

## Group F — Systematic uncertainty investigations

**H2-040**. AOD diffraction-asymmetry measurement directly (by blocking one focus) would constrain the Bérut trap asymmetry to ± 2 percent.  
*Prior*: 0.7. *Mechanism*: direct measurement bypasses inference.

**H2-041**. Reproducing Bérut's apparatus with modern AOD intensity feedback would reduce well-depth-asymmetry uncertainty below 1 percent.  
*Prior*: 0.8. *Mechanism*: Serrao et al. 2024 (T4_146).

**H2-042**. Propagating the 5 percent AOD-diffraction systematic through the 6th-degree polynomial gives ± 0.1 k_B T on the well minima.  
*Prior*: 0.6. *Mechanism*: error propagation.

**H2-043**. The Bérut published correlation time ~ 3 ms is consistent with gamma/k = 3 ms for 1 μm silica in water at k ~ 1 pN/μm.  
*Prior*: 0.9. *Mechanism*: Stokes-Einstein check.

**H2-044**. Laser-power drift compensation (if implemented) would reduce asymmetry uncertainty by factor 2.  
*Prior*: 0.6. *Mechanism*: real-time monitoring.

---

## Group G — Theoretical extensions to investigate

**H2-045**. A direct derivation of B(r) from the Aurell-Wasserstein framework (generalising Proesmans 2020 T3_015 Eq. 10-12) yields (1+r)²/(4r) exactly.  
*Prior*: 0.3. *Mechanism*: uncertain whether the inherited asymmetric Kramers factor is exactly reproduced.

**H2-046**. The derivation instead yields a closely-related form like pi²(1 + r²)/(2r) or pi² cosh(log r).  
*Prior*: 0.4. *Mechanism*: various asymmetry factors arise in Kramers extensions.

**H2-047**. A direct Fokker-Planck eigenvalue calculation for the asymmetric double-well (using Risken method) gives B(r) that deviates from (1+r)²/(4r) at O(r²) for large asymmetry.  
*Prior*: 0.5. *Mechanism*: T3_003, T3_031 asymmetric-well Kramers.

**H2-048**. Shortcut-to-adiabaticity asymmetric protocols (Boyd-Patra-Jarzynski-Crutchfield 2022, T3_090) achieve B(r) below the naive formula at additional dissipation cost.  
*Prior*: 0.7. *Mechanism*: shortcut dissipation is protocol-dependent.

**H2-049**. The Zulkowski-DeWeese Hellinger bound for asymmetric wells has a different r-dependence than (1+r)²/(4r).  
*Prior*: 0.5. *Mechanism*: Hellinger captures different geometric content.

**H2-050**. The Zhen-Egloff-Modi-Dahlsten 2021 universal bound (T3_060) at finite error tolerance gives a B(r, epsilon) formula that depends on asymmetry through the initial bias of the Boltzmann distribution.  
*Prior*: 0.6. *Mechanism*: initial distribution enters the bound structurally.

---

## Group H — Validation and cross-check strategies

**H2-051**. Replicating the Bérut ten points with Langevin simulation (known U(x), known protocol) returns B = pi² + delta_protocol where delta_protocol ≈ 2-5 pi² for smooth barrier-lowering.  
*Prior*: 0.7. *Mechanism*: numerical refit of simulated data.

**H2-052**. A simulated ideal-protocol refit recovers B = pi² within 10 percent.  
*Prior*: 0.9. *Mechanism*: Schmiedl-Seifert validation.

**H2-053**. The Dago-Pereda-Ciliberto-Bellon 2021 underdamped data refit against the underdamped-Proesmans formula gives B_underdamped consistent with theory at 5 percent.  
*Prior*: 0.7. *Mechanism*: literature comparison.

**H2-054**. Gavrilov-Bechhoefer 2017 asymmetric-erasure data (T3_053) refit against B(r) gives a tighter discrimination than Bérut.  
*Prior*: 0.8. *Mechanism*: virtual-potential trap has known r.

**H2-055**. The Chiu-Lu-Jun 2022 (T3_089) reported B(r) data is consistent with (1+r)²/(4r) or with an alternative r-dependence — unknown until we read that paper carefully.  
*Prior*: 0.5. *Mechanism*: direct check of T3_089.

---

# Pre-Empt-Reviewer Hypotheses (from Phase 0.25 v2 PROCEED verdict)

These three hypotheses are added with flag `pre-empt-reviewer`. Phase 2 experiments MUST address each before the paper is written.

## PER-01 — Protocol under-specification sensitivity
**Prior:** 0.6
**Mechanism:** The Bérut supplementary does not tabulate U(x, t); digitising Fig. 1c yields a family of compatible modulations, each with its own simulated B.
**Experiment:** Phase 0.5 deliverable. Run the Brownian-dynamics simulator across N ≥ 20 modulations within the band compatible with the Bérut figures; report the spread of simulated B. If the spread exceeds the empirical CI width, contact Ciliberto group for the control waveform before continuing.
**Flag:** pre-empt-reviewer, Phase 0.5 blocker.

## PER-02 — Decomposition table of B_Bérut − π²
**Prior:** 0.85
**Mechanism:** The paper's physics content lives in attributing the excess B − π² to specific protocol / apparatus features. Without this decomposition, the paper reads as re-analysis with no new physics.
**Experiment:** Phase 2 deliverable. Produce a quantitative ablation: (i) Schmiedl-Seifert optimal (B = π²), (ii) Bérut smooth-protocol delta, (iii) AOD diffraction asymmetry delta, (iv) photodiode bandwidth delta, (v) residual systematic. Each delta numerical with bootstrap error bars. Sum must reproduce full-simulator B to within simulation precision.
**Flag:** pre-empt-reviewer, Phase 2 mandatory.

## PER-03 — Replace tautological falsifier in §4(iii)
**Prior:** 0.95
**Mechanism:** "Simulated B ≥ π²" is tautological for any correct overdamped Langevin simulation of a non-pathological protocol. Reviewer will flag.
**Experiment:** Writing-only fix at Phase 3 draft stage. Replace the tautological falsifier with: "decomposition's Σ deltas reproduces full-simulator B_Bérut to within simulation precision, or it does not." Harden (iii) from consistency check to informative test.
**Flag:** pre-empt-reviewer, Phase 3 draft.
