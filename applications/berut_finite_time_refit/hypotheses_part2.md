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
