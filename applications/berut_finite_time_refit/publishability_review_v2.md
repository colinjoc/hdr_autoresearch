# Publishability Review v2 — Bérut Finite-Time Refit

**Reviewer role.** Grouchy Phase 0.25 reviewer, second round. Fresh sub-agent, no access to v1. Reading only `proposal_v2.md`, `literature_review.md`, `knowledge_base.md`, `research_queue.md`, and the Phase 0.25 section of `program.md`.

**Target venue.** Physical Review E (fallback: J. Stat. Mech.).

**Context of the revision.** v1 received a REFRAME because the asymmetric-barrier formula *B*(*r*) = π²(1+*r*)²/(4*r*) has vanishing derivative at *r* = 1, so the near-symmetric Bérut trap could not discriminate it from *B* = π² (±50 % on *r* → only ~5 % on *B*(*r*)). v2 (a) explicitly defers the asymmetric test to Gavrilov–Bechhoefer 2016 / Chiu–Lu–Jun 2022 as follow-up, and (b) adds a Brownian-dynamics simulator of Bérut's actual (non-optimal) protocol as the new substantive contribution.

---

## 1. Novelty taxonomy

**Category: *application* + *genuinely new numerical prediction*, hybrid.**

The paper has three sub-claims and they sit in different taxonomy boxes:

- *(a) Empirical ten-point refit of the Bérut curve under the Proesmans formula.* This is an **application** — the Proesmans 2020 bound is the pre-existing framework; nobody has done the weighted nonlinear least-squares on the ten published points with propagated CIs. The lit review (Theme 1 §1.10 item 1; KB fact 9) explicitly documents the gap: "Proesmans et al. (2020) cites Bérut as motivation but does not re-fit the full ten-point curve." Low-novelty but a genuine gap.
- *(b) First-principles Brownian-dynamics prediction of B_Bérut for the actual (non-optimal) Bérut protocol.* This is the substantive contribution. It is **genuinely new as a specific numerical prediction**, even though the methodology (overdamped Langevin integration per Volpe & Volpe 2013 / Ermak–McCammon 1978) is textbook. The novelty is the target, not the method.
- *(c) Decomposition of B_Bérut − π² into protocol non-optimality, detector bandwidth, trap asymmetry.* An **application / decomposition** using established tools (ablation-style).

**Closest existing comparators for (b) — the load-bearing novelty claim:**

1. **Proesmans & Bechhoefer 2019 (PRE)** — derives *optimal* ESE protocols that saturate B = π². They explicitly construct the optimal protocol; they do *not* simulate the *realised non-optimal* Bérut protocol. Differentiation: our simulator runs the Bérut protocol as-reported, not the optimal protocol.
2. **Dago–Pereda–Ciliberto–Bellon (2021, 2022, 2024)** — simulate and measure finite-time erasure in an underdamped micromechanical cantilever with a virtual double well. Different dynamical regime (underdamped), different apparatus (virtual feedback vs physical two-foci AOD trap), different protocol family. Not a substitute.
3. **Volpe & Volpe 2013 (Am. J. Phys.)** — the canonical Brownian-dynamics simulation recipe for optical-trap particles. This is the *toolkit*, not a prior simulation of Bérut's protocol. The lit review §2.9 flags this paper as the methodological template but notes no one has applied it to Bérut's specific time-dependent modulation.
4. **Bérut–Petrosyan–Ciliberto 2015 J. Stat. Mech. review** — a long-form account of the 2012 experiment. No first-principles simulation of the protocol; only data analysis.
5. **Goerlich–Rosales-Cabara–Ciliberto 2022 (Phys. Rev. Res.)** — tests Landauer with non-equilibrium initial conditions, includes Brownian-dynamics checks, but not a reconstruction of the Bérut time-dependent potential.

The lit review searched 701 citations across four themes; **no paper simulates Bérut's specific experimental modulation U(x, t) from first principles and reports a predicted B**. The gap is real.

**Caveat the reviewer flags.** The novelty of (b) is contingent on fidelity. If the Bérut SI does not specify U(x, t) in enough detail, the simulator's "first-principles prediction" is actually "prediction under a specific reconstruction of U(x, t)" — which downgrades it toward (a). The proposal acknowledges this in §6 ("the Bérut supplementary's incomplete specification of the modulation shape…may require us to report bounds on the simulated B rather than a single number; we pre-commit to doing so"). Bounds are acceptable but must be tight enough to be publishable; see §3 below.

---

## 2. Falsifiability

Three kill-outcomes in v2:

- **(i) Empirical-fit validity.** Binary: CI on *B* is either finite or degenerate. Power analysis pre-reported. **Genuinely falsifiable** — the ten points may or may not constrain *B* to finite width. Not tautological.
- **(ii) Simulation–experiment consistency.** Simulated *B*_Bérut is within 2σ of empirical CI or it is not. **Genuinely falsifiable and the scientifically load-bearing test.** If consistent, the Proesmans framework + Bérut protocol reconstruction together predict the data — a non-trivial cross-validation. If not, the decomposition in (c) localises the discrepancy. There is a subtle asymmetry in the test — a "pass" could hide errors that happen to cancel (detector bandwidth compensating protocol non-optimality), but the decomposition addresses this by turning factors off individually.
- **(iii) Proesmans-bound violation.** Simulated *B*_Bérut ≥ π². **Formally falsifiable but a near-tautology** — if the simulator correctly implements the overdamped Langevin equation under any non-pathological protocol, the Proesmans lower bound *must* hold by construction. A violation would indicate a bug in the simulator, not new physics. The reviewer would not give points for this as a test of the theory; it is a sanity check. *The proposal acknowledges this phrasing ("which falsifies either the Proesmans derivation or our simulation") but should downgrade (iii) to a consistency check rather than a kill-outcome in the paper.* This is a minor issue, not REFRAME-fatal.

Net: falsifiability is real for the two load-bearing claims (i) and (ii). Kill-outcome (iii) is weak but not disqualifying.

---

## 3. Load-bearing parameters

The headline of v2 is "simulated *B*_Bérut matches empirical *B*_fit from Bérut 2012". Parameters the headline depends on, from the lit review and knowledge base:

| Parameter | Value used in headline | Literature uncertainty | Headline scaling |
|---|---|---|---|
| Stokes-Einstein drag γ (with Faxén wall correction) | ~6πη·a, +2 % Faxén | ±5–10 % (PSD calibration residual, lit §2.2; wall-proximity Faxén ±3 %) | *B* scales linearly in γ·L²/(k_BT τ) if one varies γ at fixed dissipation-data; an error in γ maps ~1:1 into inferred *B* |
| Well separation L | ~0.8–1 μm | no published uncertainty (lit §4.4: "~1 μm") | *B* scales as L² (Wasserstein distance); 10 % error in L → 20 % error in predicted *B* |
| Barrier height ΔU | ~3–5 k_BT (high-barrier ~8, low-barrier ~2.2) | qualitative only, no uncertainty (lit §4.4 / KB F3.20) | Moderate — controls Kramers time; for τ < t_Kramers the predicted *B* inflates substantially |
| Effective laser-heating temperature | +1–2 °C above ambient | Rings et al. 2011 | Small, <5 % |
| Barrier-lowering protocol shape U(x, t) | "linear tilt ramp + barrier lowering, read off Fig. 1c and SI" | Unspecified functional form; proposal admits modulation shape "incompletely specified" | **Potentially large and not quantified** |
| AOD diffraction asymmetry | 5–10 % (lit §4.5, KB F3.18) | Valentine 2008 range | Enters via residual trap asymmetry; for the symmetric headline, contributes to systematic spread in simulated *B* of a few percent |
| Photodiode bandwidth / nonlinearity | ~kHz (KB 28), 0.1–1 % nonlinearity | Gittes & Schmidt 1998; Williams 2014 | Enters only via (c) decomposition; tested by turning off in simulator |

**The single biggest risk: the protocol shape U(x, t) is under-specified in the published Bérut papers.** The lit review explicitly catalogues this (§4.4): Bérut 2012 and the 2015 review publish U(x) shapes at high- and low-barrier conditions but do *not* publish the time-dependent modulation between them as a tabulated schedule. The proposal commits to "reading off Fig. 1c and SI" and to "report bounds on the simulated B rather than a single number". This is honest, but the reviewer must ask: is the bound tight enough to make (ii) informative? If digitisation uncertainty alone produces simulated *B* ∈ [π², 5π²], then "empirical *B*_fit ≈ 3π²" and "simulated *B*_Bérut ∈ [π², 5π²]" is a tautological consistency. This is the single biggest risk and it does not have a clean mitigation that is internal to the current Phase 0.5–Phase 3 plan — it is a *data-availability* problem. Mitigation options: (1) contact the Ciliberto group for the control waveform (lit §4.7 flags this); (2) perform sensitivity analysis across a family of plausible protocol parameterisations and report *B* as a band, with the paper's headline being the band's position relative to π² and relative to the empirical CI; (3) select a subfamily of protocols consistent with Bérut's Fig. 1c and show the simulated *B* band is sufficiently narrow to discriminate from the Schmiedl–Seifert optimum. Option (2) is the minimum viable plan and is what §6 already commits to.

This is a *major* objection, not fatal, because the proposal pre-empts it. But the Phase 2 plan must include an explicit test that the protocol-digitisation uncertainty band does not swallow the result, and that test must be done at Phase 0.5 before committing to the full HDR loop. If it does swallow the result, the project should contact the Ciliberto group (they are cited co-authors of Bérut 2012 and highly active in this subfield).

**Other load-bearing parameters** — γ, L, ΔU — have ~10 % uncertainties individually. Combined in quadrature they produce a ~20 % uncertainty band on predicted *B*. This is acceptable if the empirical fit produces a tight enough CI for the comparison to mean something. The power analysis committed in §4(i) addresses this.

---

## 4. Venue fit

Two candidate venues from the proposal plus one the reviewer suggests:

**Physical Review E (primary).** Fit: PRE publishes first-principles numerical simulations of specific published experiments against stochastic-thermodynamic bounds. The "simulator + empirical fit" structure is standard PRE material (cf. several Proesmans, Dago, Miller papers). Typical objection: PRE reviewers demand rigorous error budgets; under-specified protocol shapes or under-propagated calibration uncertainties routinely trigger major-revision returns. Our §3 analysis already identifies where this objection lands. Mitigable.

**Journal of Statistical Mechanics: Theory and Experiment (fallback).** Fit: J. Stat. Mech. is the traditional home of protocol-optimality and exactly-solvable-stochastic-thermodynamics papers. Bérut 2015 itself was published there. If the simulator becomes the main contribution — i.e. if the empirical refit's CI is weak and (a) degrades to a secondary result — J. Stat. Mech. is the cleaner fit. Typical objection: J. Stat. Mech. expects either an exact analytical result or a clean numerical benchmark; heuristic digitisations of a figure are a hard sell. The fallback framing proposed in v2 handles this correctly.

**Verdict on venue.** PRE is the right primary target *provided* the simulator prediction ends up tighter than the empirical CI and the comparison is informative. J. Stat. Mech. is a fine fallback if the empirical fit is the weaker leg, which it probably is. The proposal correctly names both.

A secondary note: the v2 contribution reads, on paper, as methodology-plus-measurement (simulator + fit of published data). Neither venue has an allergy to this, but *Nature Communications* or *Communications Physics* are **not** appropriate targets for this scope and the proposal correctly does not claim them.

---

## 5. Top three killer objections

**Objection A (major, not fatal): Protocol under-specification means the "first-principles" prediction is actually a prediction under a specific and possibly one-of-many reconstructions of U(x, t).**
The Bérut supplementary does not tabulate the time-dependent control. Digitising Fig. 1c plus textual description yields a family of compatible protocols, each producing a different simulated *B*. If the band of simulated *B* is wide enough to always agree with the empirical CI, the comparison in §4(ii) is uninformative. *Mitigation:* (1) §6 already commits to reporting bounds rather than a single number; (2) Phase 0.5 must produce a protocol-family sensitivity analysis showing the band width *before* committing to the full loop; (3) parallel track — attempt to contact the Ciliberto group for the control waveform. The current project plan addresses (1). (2) needs to be elevated to a Phase 0.5 blocker in `research_queue.md`. (3) should be attempted even if (2) passes — an answer from the authors is a huge derisking.

**Objection B (major, not fatal): If the simulated *B*_Bérut ends up consistent with the empirical fit (both saying, e.g., "B ≈ 2–3× π²"), the paper's takeaway is "the Bérut protocol realises *B* that is not π² because the protocol is not the Schmiedl–Seifert optimum, and our simulator of the Bérut protocol agrees with the data to within uncertainties." That is a positive null result that closes an 11-year gap.** But a reviewer may ask: "is this a publication, or is it an applied-physics exercise that confirms what everyone assumed?" The answer depends on the decomposition in (c). If the decomposition attributes the excess *B* − π² cleanly to identifiable protocol features, the paper has real content (a specific prediction: Bérut-protocol *B* = π² + X; X explained by Y). If the decomposition is ambiguous or dominated by calibration systematics, the paper reads as "re-analysis with no new physics". *Mitigation:* the decomposition in §2(c) must be concrete. Phase 2 should commit to producing a decomposition table: (i) B_optimal = π² (Schmiedl–Seifert), (ii) B_Bérut-smooth-vs-jump = ?, (iii) B_add-AOD-asymmetry = ?, (iv) B_add-bandwidth-limits = ?, with each delta quantified by ablation. This table *is* the paper's physics content; if it is not produced, the paper is not publishable in PRE.

**Objection C (minor): Kill-outcome (iii) in §4 ("Simulated *B*_Bérut ≥ π² or violates the Proesmans bound") is tautological for any correct overdamped-Langevin simulation under any non-pathological protocol.** A reviewer will note this and ask why it appears as a falsifiable prediction. *Mitigation:* downgrade (iii) to a consistency check in the paper text and call it a simulator verification step, not a theoretical test. Replace with a sharper falsifier: e.g. "the decomposition resolves the *B*_Bérut − π² excess into ≥2 named contributions whose sum matches the full-simulator result to within simulation precision, or it does not." This is a genuinely informative falsifier. Already implied in (c); just needs to be moved into §4. Not REFRAME-fatal.

---

## Summary of the three killer objections for `research_queue.md`

If PROCEED, these are added with flag `pre-empt-reviewer`:

1. **Protocol under-specification risk** — produce a Phase 0.5 sensitivity analysis over the family of Bérut-compatible U(x, t) modulations, showing simulated *B* band width is narrower than the empirical CI. If not, contact Ciliberto group for control waveform before continuing.
2. **Decomposition concreteness** — Phase 2 must produce a quantitative decomposition table of *B*_Bérut − π² into (i) protocol non-optimality (smooth vs jump), (ii) AOD diffraction asymmetry, (iii) photodiode bandwidth, (iv) residual systematic, each delta numerical with error bars. This is the paper's physics content.
3. **Falsifier (iii) hardening** — replace the tautological "simulated *B* ≥ π²" kill-outcome with a sharper test: the decomposition's sum reproduces the full-simulator *B*_Bérut to within simulation precision, or it does not.

---

## Verdict

v2 addresses the v1 REFRAME cleanly. The asymmetric-formula trap is defused by explicit deferral to Gavrilov–Bechhoefer / Chiu–Lu–Jun. The new substantive contribution — first-principles Brownian-dynamics simulation of Bérut's actual protocol — fills a genuine 11-year gap identified by the lit review across 701 citations. Falsifiability is real for the two load-bearing kill-outcomes; one is tautological and should be hardened but is not disqualifying. Venue fit (PRE primary, J. Stat. Mech. fallback) is appropriate. Load-bearing-parameter analysis identifies one major-but-mitigable risk (protocol under-specification) and several minor ones, all pre-empted in the proposal.

No fatal objection is unaddressed. The major objections all have clear mitigation paths that the Phase 0.5 → Phase 2 plan already gestures at; the three `pre-empt-reviewer` items above elevate them to explicit experiments.

VERDICT: PROCEED
