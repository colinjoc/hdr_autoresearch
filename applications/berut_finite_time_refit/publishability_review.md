# Publishability Review — Bérut Finite-Time Landauer Refit

Phase 0.25 review. Fresh sub-agent, no prior context on this project.
Inputs read: `program.md` §Phase 0.25, `proposal.md`, `scope_check.md`,
`literature_review.md` (all four themes), `knowledge_base.md`,
`research_queue.md`. Papers.csv and theme-split files NOT read.

Headline context from the lit review that was not available at Phase −0.5:

- The published Bérut trap is explicitly tuned for near-symmetric wells
  ("asymmetry reduced to ~0.1 k_B T"), giving reconstructed
  *r* = 0.7–1.5 at 95 % CI in the high-barrier condition and 0.5–2 in
  the low-barrier condition (KB F3.25, §4.4 lit-review).
- The proposed asymmetric-barrier formula *B*(*r*) = π²(1+*r*)²/(4*r*)
  has **zero derivative at *r* = 1** — it is a minimum of the asymmetric
  factor. A ±50 % CI on *r* centred near 1 maps to only ~5 % uncertainty
  on *B*(*r*). (KB F3.26.)
- Consequence: the Bérut dataset cannot discriminate the asymmetric
  prediction from *B* = π² in any statistically meaningful way, by
  construction of the parametrisation and the apparatus tuning. The
  central discrimination test of the proposal is formally inconclusive
  before any experiment runs.

---

## 1. Novelty taxonomy

Category: **extension, partially prior-claimed**. The proposal promises
three deliverables; they fall in different places on the taxonomy.

**(a) Empirical refit of the full Bérut ten-point τ-curve against
Proesmans' B = π² / τ formula with bootstrap 95 % CI.**
*Extension* of Proesmans, Ehrich & Bechhoefer (2020 PRL 125; 2020 PRE 102)
to a dataset they cited without refitting. Closest prior work:
Proesmans et al. themselves, who compare only to Bérut's quasistatic
point; Dago, Pereda, Ciliberto & Bellon (2021 PRL; 2022 PRL) who refit
against their own cleaner underdamped data but do not touch Bérut's
curve; and Chiu, Lu & Jun (2022) who do a feedback-trap B(r) fit but
on a virtual potential with known *r*. This is a legitimate gap, but
thin: the contribution is one bootstrap CI on a ten-point curve, which
is, quite literally, a one-figure paper.

**(b) r-identifiability from the published Bérut supplementary.**
*Application* of existing methodology (Florin-Pralle-Stelzer-Hörber 1998
Boltzmann inversion; Gieseler et al. 2021 modern recipe;
Bakhtiari-Esposito-Lindenberg 2015 Kramers-rate asymmetry) to a specific
published dataset. Pre-registered to return a null result ("r worse
than factor-2") and the lit review essentially confirms that outcome
will obtain (KB F3.25).

**(c) Discrimination test between symmetric B = π² and asymmetric
B(r) = π²(1+r)²/(4r).**
*Claimed "genuinely new test"*, but the asymmetric formula itself is
inherited Kramers-prefactor algebra (Coffey-Kalmykov-Titov 2005,
Hänggi-Talkner-Borkovec 1990). The lit review (Theme 3 §3.1, KB F3.2,
F3.28) is explicit that the formula is heuristic — it has not been
rigorously derived from the Aurell-Proesmans Wasserstein machinery and
is not itself a new theoretical result. The novelty claim "first test
of B(r) against experimental data" is **already contradicted by the
lit review itself**: Chiu, Lu & Jun (2022) and Gavrilov-Bechhoefer (2016)
run feedback-trap experiments with explicitly asymmetric wells and
known *r*; Dago-Ciliberto-Bellon (2024, T3_058) give measured
erasure-cost curves vs asymmetry in a physical underdamped oscillator.
The project is not "the first asymmetric test" — it is at best a refit
of a dataset not designed to do the asymmetric test.

**Verdict on novelty:** extension (a) is the real contribution. (b) is
a methodological application with a pre-expected null. (c) is
weakly-novel synthesis of existing heuristic with existing data that
cannot resolve it. The "three-deliverable" framing oversells.

---

## 2. Falsifiability

The proposal pre-registers three kill-outcomes. The lit-review finding
on r-identifiability changes their falsifiability status as follows.

**Kill-outcome A — "a proper fit exists" vs "the ten-point curve does
not constrain B".** Still falsifiable. Ten points vs a 2-parameter fit
is enough to yield either a finite CI or not. Bootstrap on trajectory-
level data (if accessible; else on the published summary points) will
give a concrete answer. This leg is fine.

**Kill-outcome B — "empirical B CI contains B = π² (symmetric
prediction)".** Still falsifiable. This is a sharp numerical prediction
against a fitted coefficient with CI. Importantly, it is also the only
leg expected to be scientifically informative: if the CI excludes π²
from above (most-likely), the paper is about **why Bérut's protocol
does not saturate the Proesmans bound**, which is a real and
publishable result (KB F3.6, F3.10, F3.27 all predict B > π² for
Bérut's smooth protocol). If the CI excludes from below, Proesmans is
falsified — unlikely but genuinely testable.

**Kill-outcome C — "empirical B CI contains B(r) at the reconstructed
*r*".** **Now unfalsifiable in disguise.** With *r* ≈ 1 ± 0.5 (95 % CI)
and B(r) = π²(1+r)²/(4r) having zero derivative at *r* = 1, the
asymmetric prediction is numerically indistinguishable from π² across
the entire r-CI. This means:
- Outcome C cannot exclude the asymmetric prediction if it includes π²
  (because any r in the CI produces B(r) ≈ π²).
- Outcome C cannot exclude π² if it includes the asymmetric prediction
  (same reason).
- The "discriminate between symmetric and asymmetric" framing is
  tautological — the two predictions coincide at the achievable
  precision. This is the unfalsifiable-in-disguise pattern flagged in
  program.md ("is consistent with observation" dressed as a test).

Of the proposal's four pre-registered joint outcomes:
- (excludes symmetric, excludes asymmetric) — publishable, but
  requires B far from π² in both directions, an extreme outcome.
- (includes symmetric, excludes asymmetric) — **mathematically
  impossible** given r ≈ 1 ± 0.5 and vanishing derivative.
- (excludes symmetric, includes asymmetric) — **mathematically
  impossible** for the same reason.
- (includes both) — the default outcome, and the one the proposal
  describes as "the data is insufficient to discriminate". This is
  fine as a null result but does not require the asymmetric-test
  apparatus; it is simply "B ≈ π², within CI".

**Bottom line on §2:** only kill-outcomes A and B remain genuinely
falsifiable. The discrimination framing (C) is not a live test on the
Bérut data; it is a parameter-regime into which the prediction always
collapses to "B ≈ π²".

---

## 3. Load-bearing parameters

Headline depends on the following numerical inputs. Each row lists
value, literature uncertainty, and how the headline scales.

| Parameter | Value used | Uncertainty | Headline scaling |
|---|---|---|---|
| Bérut ⟨Q_diss⟩_i error bars (10 points) | ±0.15 k_B T | flagged optimistic by factor 1.5–2 (H2-009, H24, KB P1) via TUR-floor check | σ_B ∝ σ_Q at each point; 1.5× inflation → CI width up ~1.5× |
| Number of independent τ points | 10 | exact | B-CI half-width scales as 1/√(N − 2) = 1/√8; halving N doubles CI width |
| Autocorrelation time for N_eff | 3 ms in a 502 Hz stream | ±factor 2 in autocorr time → N_eff between 5 × 10⁴ and 4 × 10⁵ | only affects Boltzmann-inversion bias on r |
| Bath temperature T | 300 K + 1-3 °C laser heating (H22, KB pitfall P5) | ±1 % | B(k_B T) values scale linearly in T; 1 % T shift → 1 % shift in reported B |
| Drag coefficient γ (Faxen-corrected) | Stokes × (1 + a/h) ≈ 1.02 × 6πηa (H21, KB pitfall P2, §4.10 lit-review) | ±3 % residual after Faxen | B dimensional prefactor scales linearly in γ; 3 % drag error → 3 % B error |
| Trap stiffness κ (PSD calibration) | ~1 pN/μm | ±5 % (H2-034, Berg-Sørensen-Flyvbjerg 2004) | enters via inferred U(x) shape; couples to γ and T into B prefactor; ~5 % on B |
| Well-depth asymmetry *r* | ≈ 1 (tuned, qualitative) | 95 % CI 0.7–1.5 (high-barrier), 0.5–2 (low-barrier) (KB F3.25) | B(r) ∝ (1+r)²/(4r); **vanishing derivative at r = 1; 50 % r shift → < 5 % B(r) shift** |
| AOD diffraction asymmetry | ~5 % typical | unreported in Bérut 2012 (KB F3.18, Valentine 2008) | propagates into well-depth uncertainty of ±0.1 k_B T, roughly doubles the r-CI (§4.13 lit-review) |
| Barrier height V_b | 3–5 k_B T (low condition) or ~8 k_B T (high) | ±0.2 k_B T from digitisation (KB F3.20) | sets Kramers timescale; affects which points are "quasi-static" vs "finite-time"; also sets whether the Proesmans derivation's high-barrier asymptotic applies (H42 — 10–30 % shift in effective B) |

**Red flags:**
1. **The r parameter is load-bearing only in the formal sense.** Because
   (1+r)²/(4r) has vanishing derivative at r = 1, the headline
   *B*(*r*)-prediction is **insensitive to the 50 % r CI**. This
   simultaneously (a) weakens the r-identifiability story — tight r is
   not needed — and (b) kills the discrimination test. Honest statement:
   the refit paper can assume r = 1 without meaningful loss of accuracy
   on B(r), and should say so.
2. **The "finite-barrier correction" parameter is missing from the
   proposal.** Proesmans' B = π² derivation uses the high-barrier
   optimal-transport limit; Bérut's low-barrier condition is at
   V_b ≈ 2.2 k_B T, where the high-barrier assumption is violated
   (H42 prior 0.55). This correction could shift the realised B by
   10–30 %, which is **larger than the discrimination threshold between
   the two candidate predictions**. The proposal does not list this
   parameter or its uncertainty.
3. **Bérut published error bars are flagged as optimistic by factor
   1.5–2.** Inflating σ_B by 1.5× widens the B-CI by ~1.5× — this
   makes B = π² harder to exclude, which helps the "includes π²" null,
   but weakens any discrimination claim.

---

## 4. Venue fit

**Proposal's primary: Physical Review E.**
- *Fit*: PRE does publish empirical tests of stochastic-thermodynamics
  bounds at this scale. Dago 2021 (PRL), Gavrilov-Bechhoefer (2017 PRE,
  T3_052), and Proesmans-Bechhoefer 2019 (PRE, ESE protocols) are
  direct precedents. Bonanca-Deffner (PRE) type papers also land here.
- *Typical objection*: PRE expects either (i) a new theoretical bound
  rigorously derived, or (ii) new experimental data. The proposal
  supplies neither. A refit of a 2012 dataset with a bootstrap CI is
  at the lower end of PRE's novelty bar — scope-check already flagged
  this. Under the new lit-review finding that the asymmetric test is
  inconclusive by construction, the contribution narrows to
  "bootstrap CI on B from the ten Bérut points, concluding B is
  consistent with or above π²". That is a PRE Brief Report at best,
  and more likely a PRE rejection-with-suggestion-to-resubmit at
  J. Stat. Mech.

**Proposal's fallback: J. Stat. Mech.**
- *Fit*: J. Stat. Mech. explicitly publishes methodology-plus-test
  papers and empirical refits. Bérut-Petrosyan-Ciliberto's own 2015
  long-form review is in J. Stat. Mech. (T3_048). Dago-Ciliberto-Bellon
  2022 methodology paper is in J. Stat. Mech. The venue is the natural
  home for a paper that is "careful refit + honest null on the
  discrimination question + methodological contribution on r-identifiability".
- *Typical objection*: less picky on novelty, but demands full
  error-budget propagation and cross-checks against related data
  (Dago, Gavrilov-Bechhoefer, Chiu-Lu-Jun). Tractable.

**Under the reframed scope, J. Stat. Mech. is now the better primary
target.** The asymmetric discrimination test is no longer a credible
headline. What remains — empirical bootstrap-CI refit, honest
pre-registered null on B(r) discrimination, r-identifiability as a
methodology section — is squarely in J. Stat. Mech.'s band. PRE is
reachable only if the paper adds one of:
- a simulated Bérut-protocol refit (H33, H34, H2-051) quantifying the
  smooth-protocol excess over the Proesmans bound, and
- a cross-dataset refit including Dago 2021/2022 overdamped points
  (H35, H41, H2-053), tightening the joint B CI across apparatus
  families.

Either addition would bring the contribution closer to PRE's bar.
Without them, PRE will bounce and the revision cycle will end at J.
Stat. Mech. anyway. Cheaper to start there.

**Alternative venues worth naming** (none as strong):
- *New J. Phys.* publishes Brownian-particle stochastic-thermodynamics
  papers with methodology content; comparable to J. Stat. Mech. for
  this paper.
- *Entropy* (MDPI) accepts almost anything in the area. Weaker
  reputation; acceptable only as last resort.

---

## 5. Top three killer objections

**Objection 1 — Fatal. "The discrimination test is formally
inconclusive by construction — the asymmetric formula and the
symmetric formula are numerically indistinguishable at any r in the
reconstructed Bérut CI, because (1+r)²/(4r) has vanishing derivative
at r = 1. You have not pre-registered a genuine two-alternative test;
you have pre-registered a test that can only return 'consistent with
both'."**
A PRE referee will flag this in the first page. The proposal's own
lit review (KB F3.26) and research queue (H2-015, H2-018, H2-019,
H2-020 prior 0.25) both confirm this. The proposal currently treats
the inconclusive outcome as one of four equally informative
pre-registered results; in fact it is the **only possible result** for
the asymmetric leg given published r bounds.
*Mitigation*: **the asymmetric-discrimination framing must be removed
from the headline**. The proposal should be rewritten as a symmetric
refit paper with r-identifiability as a methodological section that
explicitly reports the insensitivity of B(r) to r near 1 as the
reason the asymmetric test cannot be done on this dataset. The proposal
should then explicitly flag which dataset *could* do the asymmetric
test (Gavrilov-Bechhoefer feedback trap; Chiu-Lu-Jun 2022;
Dago-Ciliberto-Bellon 2024 at strongly asymmetric protocols).
This mitigation requires `proposal_v2.md` — not fixable via pre-empt
research queue.

**Objection 2 — Major. "You claim this is the first refit of the full
Bérut τ-curve, but Proesmans-Ehrich-Bechhoefer 2020's long-form PRE
paper discusses Bérut explicitly, Dago 2021/2022 refit comparable
overdamped data, and Chiu-Lu-Jun 2022 already test B(r) in an
explicitly asymmetric feedback trap. Why is *your* refit the one
that deserves publication?"**
The novelty claim is narrow enough to survive if cleanly stated, but
vulnerable to the "the gap you're filling isn't a gap" line. The
lit review confirms that nobody has published a bootstrap-CI refit of
the full ten-point Bérut curve specifically — but the result of such
a refit is predictable from the lit review itself: B > π² because
Bérut's protocol is not the Schmiedl-Seifert optimal one (KB F3.6,
F3.10, F3.27). A refit that merely confirms "Bérut's smooth protocol
does not saturate Proesmans' lower bound" is a negative result against
an unasserted claim — nobody said Bérut's protocol should saturate it.
*Mitigation*: the paper must add **simulator-based protocol-specific
prediction**: run Brownian-dynamics with the Bérut trap parameters
and the actual protocol, predict the *B* that the Bérut apparatus
should have realised, and show that the empirical refit agrees with
the protocol-specific prediction within error. That turns the paper
from "we refit and confirm B > π²" (trivial) to "we predict and
verify the protocol-specific excess over the Proesmans bound" (real
content). This is directly a pre-empt-reviewer Phase 2 experiment
(H33, H34, H2-051, H2-052).

**Objection 3 — Major. "Bérut's published error bars are known to be
optimistic. Your CI inherits that optimism directly. Either show that
the bars pass a TUR-floor consistency check, or inflate them with a
justified systematic budget — including AOD diffraction asymmetry
(unreported), laser-power drift over the 50-minute acquisition, and
hydrodynamic wall-proximity drag corrections — and re-do the CI."**
The scope check already flagged this. Under the reframed scope it
becomes *more* important, not less, because the only remaining
non-trivial falsifiable claim is "B > π² by a specific margin", and
any margin claim requires defensible error bars.
*Mitigation*: Phase 2 must include (a) TUR-floor computation at each
τ-point (KB F3.24, F3.14, research-queue H24/H2-009), (b) explicit
systematic budget for AOD (H2-013), laser drift (H2-014), and Faxen
drag (H21), and (c) CI-inflation to the max(bootstrap, TUR-floor,
systematic-budget) floor. Tractable. Fits pre-empt-reviewer.

---

## Verdict

The contribution as described in proposal.md rests on three
deliverables. Deliverable (a) — empirical refit — is defensible but
needs a simulator-based protocol-specific comparator to clear PRE's
novelty bar (Objection 2). Deliverable (b) — r-identifiability — is
pre-expected-null and already demonstrated to be inconclusive in the
lit review. Deliverable (c) — asymmetric-vs-symmetric discrimination —
is **fatal** (Objection 1): the proposal has pre-registered an
unfalsifiable test because (1+r)²/(4r) has zero derivative at r = 1
and the Bérut r-CI straddles 1.

Per program.md §Phase 0.25 verdicts: "REFRAME: One or more fatal
problems — an unfalsifiable claim, poor venue fit, a load-bearing
unknown parameter, or weak novelty." The proposal has the first and
borderline the third.

A REFRAME is both achievable and specific. The defensible retreat is:

> **Proposal v2 scope**: an empirical refit of the full ten-point
> Bérut τ-curve against the symmetric Proesmans *B* = π² prediction,
> with bootstrap CI inflated to a TUR floor and propagated systematic
> budget. Paired with a **Brownian-dynamics simulation of the Bérut
> protocol** that predicts the protocol-specific *B* for smooth
> barrier-lowering, and a demonstration that the empirical *B* agrees
> with the protocol-specific prediction, quantifying the excess over
> the Proesmans bound. The asymmetric formula *B*(*r*) = π²(1+*r*)²/(4*r*)
> is reported in a *methodology* section with the explicit conclusion
> that, because of the vanishing derivative at *r* = 1 and the Bérut
> near-symmetric tuning, the Bérut dataset cannot discriminate
> asymmetric from symmetric. The correct dataset for that test is
> identified (Gavrilov-Bechhoefer 2016; Chiu-Lu-Jun 2022) and flagged
> as future work.

Specific proposal points to revise:
- **§1 Question**: drop the "with a proposed asymmetric generalisation"
  clause. The question is *B* vs π² and the protocol-specific
  prediction from simulation. State explicitly that the asymmetric
  test is not resolvable on this dataset.
- **§2 Proposed contribution**: collapse (a), (b), (c) into (a)
  empirical refit + protocol-specific simulator prediction, plus a
  short methodology paragraph on r-identifiability and the
  vanishing-derivative problem.
- **§4 Falsifiability**: reduce to two kill-outcomes (A and B), drop
  the four-outcome joint table — it contains two impossible cells.
- **§5 Named comparators**: add the protocol-specific simulator
  baseline as comparator, add Chiu-Lu-Jun 2022 and Gavrilov-Bechhoefer
  2016 as "correct-dataset-for-asymmetric-test" comparators.
- **§6 Target venue**: primary J. Stat. Mech., fallback PRE (invert
  the current order) unless simulator-based protocol-specific prediction
  is added, in which case keep PRE as primary.
- **§7 Relation to broader programme**: the predecessor paper's
  heuristic asymmetric-barrier claim is **not validated** by the Bérut
  refit; it is rendered "untestable on this dataset". This is a
  weaker outcome for the predecessor paper than the proposal claims.

Sharpest defensible retreat scope if even the above is too ambitious:
a pure symmetric refit with TUR-floor error bars and the Bérut-protocol
simulator — drop r-identifiability entirely, move it to a short
appendix. Target J. Stat. Mech. directly, do not attempt PRE. This
is a thin but honest paper and is publishable.

VERDICT: REFRAME
