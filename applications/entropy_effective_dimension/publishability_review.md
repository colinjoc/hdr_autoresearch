# Phase 0.25 Publishability Review — entropy_effective_dimension

**Reviewer.** Phase 0.25 sub-agent, 2026-04-21. Fresh — not the Phase 0 literature-review agent, not the Phase −0.5 scope-check agent, not the Phase 0.5 data-access author. Third of the three promoted Phase 0.25 sibling reviews.
**Mandate.** Answer the six review-contract questions on the single-candidate Fontenele-subspace-σ-in-Pythia bundle (C29 only). Be harsh — single-candidate papers carry the highest failure-mode concentration risk in the programme.
**Artefacts read.** `README.md`, `literature_review.md` (~5 k words with 311 citations), `papers.csv` (311 entries), `../entropy_ideation/knowledge_base.md` §5 (8-item evidence bar), `../entropy_ideation/candidate_ideas.md §Candidate 29` (18-line proposal), `../entropy_ideation/scope_checks/candidate_29_review.md` (Phase −0.5 scope-check, REFRAME → PROCEED). Template structure inherited from `../entropy_avalanches/publishability_review.md` and `../entropy_brain_homology/publishability_review.md`; content is fresh.

---

## 1. Is the novelty claim defensible after the Phase 0 synthesis?

**Yes, but the defensible claim is now one sentence long, not a programme.** The surviving claim the README and `literature_review.md §14` commit to is:

> On Pythia residual-stream activations, the branching ratio σ measured via the MR estimator on the reconstructed scalar Σ_K(t) of the Fontenele-operationally-selected top-K principal-component subspace crosses 1 at training checkpoints where the ambient-basis σ is off-critical (|σ_ambient − 1| > 0.05), and the complementary (d_model − K)-dimensional subspace has σ_complement < 0.95 at those same checkpoints.

Phase 0 verified Fontenele 2024 against PMC11051676 directly — operational K-selection by 1.5-decade power-law-range collapse, reconstructed-scalar population-sum, avalanche-statistics-via-crackling-noise (not MR estimator), Δ_T ≳ 10⟨ISI⟩ time-bin dependence. That verification alone corrects three material errors in the original Candidate 29 proposal (K = D_eff, per-PC σ, no time-bin analogue) and is the right scope-check posture. But the adjacent work has simultaneously narrowed what remains:

- **Liu-Paquette-Sous NeurIPS-OPT-2025 workshop paper 43** (`papers.csv 5042`) already fits the covariance spectrum λᵢ ∝ i^{−α} across Pythia 100 M – 70 B through fine-tuning. The *spectrum-evolution-through-training* axis is published. What is *not* published: σ on the reconstructed scalar of the top-K subspace, ambient-vs-subspace asymmetry, and Fontenele's operational K-selection applied to LLMs.
- **Razzhigaev et al. 2024 EACL** (arXiv:2311.05928 "Shape of Learning") publishes intrinsic-dimension trajectories across transformer pre-training — TwoNN/MLE on embeddings, expansion-then-compression bell shape. Trajectory axis is published; *subspace-σ-in-trajectory* is not.
- **Xu 2026 arXiv:2602.10496** publishes low-dimensional execution manifolds (3–4 dim on d=128 modular-arithmetic transformer) with a clean two-subspace split (execution ⊥ staging). Subspace-decomposition axis is published on a toy task; *criticality-observable on the subspace* and *pretrained-LLM substrate* are not.
- **Wang 2026 arXiv:2604.16431 / 2604.04655** publishes dimensional criticality at grokking — on gradients, with a toy modular-arithmetic target. Gradient-axis and grokking-toy differentiation is clean; *activation-axis on pretrained Pythia* is the orthogonal niche.

Three adjacent papers have eaten three axes. The surviving niche is a *four-predicate conjunction*: (i) activations, not gradients; (ii) pretrained Pythia at scale, not modular-arithmetic toys; (iii) σ observable, not α-spectrum or intrinsic-dimension; (iv) Fontenele operational K, not participation-ratio-chosen K. No 2024–2026 paper clears all four.

**Hostile one-sentence kill.** "Liu-Paquette-Sous 2025 already tracked the covariance-spectrum exponent α through Pythia training, Razzhigaev 2024 already tracked intrinsic-dimension trajectories, and Xu 2026 already demonstrated the two-subspace split; the remaining delta of 'compute σ on the top-K-subspace reconstructed scalar' is a one-observable extension whose positive result is predicted by the three adjacent papers and whose negative result tells the reader only that the MR estimator does not transfer cleanly to PCA-projected LLM activations — either outcome is a workshop short, not a main-track paper."

**Counter.** (a) None of the three adjacent papers computes any criticality observable on any LLM activation; "σ on reconstructed scalar" is load-bearing because it is the *univocal Fontenele claim* being tested, not a colour on a spectrum already measured. (b) The ambient-vs-subspace *asymmetry* is the key predicate — the Fontenele pattern requires σ_topK ≈ 1 *while* σ_complement < 0.95 *while* σ_ambient is intermediate-and-off-critical. Liu-Paquette-Sous cannot even state this pattern, let alone test it. (c) Fontenele's operational K-selection (power-law range ≥ 1.5 decades) applied to LLM substrate has *never been run*; whether it terminates cleanly on residual-stream activations, and whether the resulting K tracks D_PR or diverges from it, is a publishable datum in its own right — per the literature review's open-gap G3.

**Verdict.** Novelty defensible as a four-predicate conjunction; the margin is *one preprint* (from Liu's group, from Wang's group, or from a 2026 Sci. Adv. author's lab porting Fontenele to a net). The kill-one-liner is painfully close to working because three of the four predicates are independently covered. Execution-discipline + submission-speed matter more than additional experimental arms — which is itself the single-candidate paper's structural trap, see §6.

---

## 2. Evidence bar vs the single candidate (C29)

A single-candidate paper cannot spread bar-coverage risk across arms. All 8 items must be cleared on C29 alone; any silent gap becomes a direct hole in the paper.

Crosswalk of `knowledge_base.md §5` against C29 as stated in README + `literature_review.md §14` + `scope_checks/candidate_29_review.md §6`:

| Bar item | C29 coverage | Load-bearing weakness |
|---|---|---|
| 1. `P(s)` via powerlaw + KS + LLR | ✓ committed (scope-check §6 non-negotiable 3) | Must also be done on the reconstructed scalar Σ_K, a non-standard input for the package |
| 2. α ≈ 3/2 with 95% CI | ✓ committed (ML expected, DP class) | α-on-LLM-subspace target value is theoretically unconstrained — Fontenele cortex α varies across sessions |
| 3. γ = (β−1)/(α−1) | ✓ **explicit** (scope-check §6 non-negotiable 4) | See §3 below — γ cross-check on Σ_K-derived avalanches has never been done in ML |
| 4. Shape collapse | Not explicitly committed in README | **GAP** — must be added |
| 5. σ = 1 ± 0.02 via MR ≥ 2 axes | Partial | MR on ambient + subspace = 2 axes of *basis*; temporal axis is one (token). Layer-axis MR not committed — Fontenele didn't have a layer axis, but our substrate does. Weak 2-axis argument |
| 6. Threshold plateau | ✓ committed (θ ∈ {0, 0.1, p95}, scope-check §6 non-negotiable 3) | Thresholds on Σ_K (a reconstructed scalar) need a different plateau argument than raw activations |
| 7. At-init control | Implicit (Pythia checkpoint 0) | **Weakness** — "checkpoint 0" in Pythia is step 0, which is post-initialisation-distribution sampling but pre-optimisation. Is this *the* at-init control or does it need a fresh-weight-matched random baseline? Unresolved |
| 8. Neutral-null rejection | Partial | Random-subspace null (matched-variance K-PC) is committed (scope-check §6 non-negotiable 2). Griffiths-phase null is **scoped out** — same choice as `entropy_brain_homology`, and for the same reason: Pythia-scale FSS is a research programme, not a check |

**Silent gaps.**

1. **Shape collapse (item 4) is not in the README.** The scope-check §6 non-negotiable list covers items 1, 2, 3, 5, 6 explicitly but does not name shape collapse. The literature review §11 mentions Papanikolaou 2011 and Capek 2023 χ = 2 parabolic profile in passing as "additional adjacent literature" but without a project commitment. **Fix: add shape-collapse as an explicit Phase 0.5 deliverable; it is a few lines of code on top of avalanche detection and the Capek χ = 2 cortical profile test gives a named quantitative target.** ~0.5 GPU-day.
2. **At-init Pythia baseline (item 7).** Pythia `step0` is the pre-optimisation checkpoint. Whether this is the correct at-init baseline for a *Fontenele-replication* claim depends on whether a random-weight matched-initialisation-distribution baseline gives different σ_topK / σ_complement. Two defensible at-init nulls: (a) Pythia step0, (b) freshly sampled weights from the Pythia-matched initialisation distribution. **The paper must run both and report the difference as a robustness check.** ~0.5 GPU-day per scale.
3. **Crackling-noise γ cross-check on the *reconstructed scalar* (item 3) has never been done in the ML literature.** Fontenele ran it on cortex; we need to run it on an LLM subspace. Whether γ = (β−1)/(α−1) is satisfied on Σ_K(t) for any LLM is an *open question* with three possible outcomes: (i) γ-relation holds → strong DP-universality evidence; (ii) fails but with Capek χ = 2 parabolic shape → edge-of-synchronisation; (iii) fails both → Griffiths-phase or non-critical. The scope-check committed this as non-negotiable 4 — it must remain a paper-level named result, not an appendix line.
4. **Griffiths-phase null is scoped out** — same choice as `entropy_brain_homology`. This is *defensible* (Pythia scales are different populations, not different samples of one system; FSS on scale axis is research-programme-level) but the abstract cannot imply universality-class assignment. The `entropy_brain_homology` review's Hostile Reviewer #2 Concern 3 applies verbatim here: acknowledge in Limitations, do not propagate to Abstract. **Fix: pre-register abstract wording as "exponent-matching evidence consistent with DP universality in the low-dimensional subspace of trained transformers, with Griffiths-phase distinguishability scoped out".**

**Aggregate-bar coverage verdict.** 5 of 8 solid, 2 of 8 weak (item 4 shape-collapse, item 7 at-init-matching-distribution), 1 of 8 explicitly scoped-out with honest limitation framing (item 8 Griffiths). Three Phase 0.5 fixes close the gaps without new candidates. A single-candidate paper with *three silent gaps in the evidence bar* is not currently publishable at main track — see §6 decision gate.

---

## 3. Is the Fontenele operational K-selection well-defined on Pythia?

This is the question on which the project's publishability hinges. The Phase 0 literature review §1 verifies the Fontenele protocol verbatim, and §13 gap G3 explicitly flags "Fontenele's operational K-selection in an ML substrate" as an open gap — *no published paper has applied the 1.5-decade-collapse K-selection to trained-network activations*. The README and scope-check claim the port is feasible. On inspection, three structural obstacles the project has not yet solved:

**Obstacle 1: The cortex-Neuropixels substrate is sparse-spike, d ≈ 200, single session. The Pythia-1.4B substrate is dense-continuous, d = 2048, across 20 checkpoints × 5 scales.**

- Cortex `activity`: binned spike counts at Δ_T ≈ 10 ms; per-bin vector is an integer-valued sparse N-vector; thresholding "median of Σ_K" produces a sparse event stream.
- LLM `activity`: continuous residual-stream vector at dimension d_model ∈ {512 (70M), 768 (160M), 1024 (410M), 2048 (1.4B), 2560 (2.8B)}; per-token vector is a dense real-valued N-vector.

The 1.5-decade criterion requires a *power-law range*. On cortex, this spans ~3 decades of avalanche size (1 to ~10³). On LLM reconstructed-scalar avalanches, the expected dynamic range is *not known a priori* — the project has not estimated it. If LLM avalanches span only 1.5–2 decades at *any* K, the criterion cannot distinguish K values and the operational rule is degenerate. **This must be pre-tested in Phase 0.5 on one checkpoint of Pythia-410M before committing pipeline time** — ~2 GPU-hours.

**Obstacle 2: Time-bin analogue for LLMs is not the ISI-based criterion.**

Fontenele's Δ_T ≳ 10⟨ISI⟩ requirement is *substrate-native*: ISI is defined because spikes are discrete events. LLMs have no ISI — activations are emitted every token, deterministically. The natural analogues (per-token, per-sequence, per-batch aggregation) are proposed in the scope-check §6 recommendation 7 but are *different objects* from a time-bin sweep. On cortex, a sub-10⟨ISI⟩ bin breaks the power law and Δ_T sweeping *finds the critical regime*; on LLMs, all three aggregation levels are a priori reasonable and none is "critical" or "subcritical" by a Fontenele-analogous criterion.

**Implication.** The time-bin-dependent part of the Fontenele protocol *does not port*. The project must either (a) drop it and commit to a single aggregation level with pre-registration of why, or (b) report the aggregation sweep as a side-observable with its own dependence on σ but *not as the critical-regime selector*. README committed to (b) via the scope-check §6 recommendation 7; this must be stated clearly in Methods as "a Fontenele-inspired but not Fontenele-canonical sweep".

**Obstacle 3: Layer index is an extra dimension the Fontenele protocol does not handle.**

Pythia-1.4B has 24 layers. The Fontenele protocol assumes a single N-vector time series. Options:

- (a) Pick one layer per checkpoint (which? last? middle? where prior work — e.g. Neural Collapse, induction-head emergence, tuned-lens — sees phase-transition behaviour?).
- (b) Concatenate all-layers into a single (N_layers × d_model)-vector per token — creates artificial cross-layer correlations via the residual stream and *tautologically* inflates K.
- (c) Repeat the full Fontenele pipeline at every layer (~24 × the wall-clock).

The README and scope-check are *silent* on which choice is canonical. **This is the single most important unspecified methodological choice in the project.** A hostile reviewer will ask for the layer-choice and the answer must be pre-registered — likely (a) with the layer-chosen justified (e.g., "final residual-stream position of layer N−1 for each scale", following the tuned-lens / logit-lens convention; or "layer N/2" following Ansuini's hunchback-ID peak).

**Recommendation.** Commit in Phase 0.5 to: (a) explicit K-selection protocol with the 1.5-decade criterion tested on a pilot checkpoint; (b) explicit layer-choice pre-registration (single layer per scale, justified); (c) aggregation-sweep-as-side-observable not as critical-regime-selector, with single canonical aggregation chosen.

**Also: pilot-test on synthetic continuous-activation branching process with known K and σ.** The Wilting-Priesemann proof that MR is unbiased on linear observables covers the σ-correctness. The *K-selection* correctness on a continuous-valued substrate is *not* proven anywhere. Seed a branching process in d_synth = 100, embed K_true = 3 critical components in a basis with N_samples ≈ 10⁵ tokens, noise the remaining 97 dimensions with σ = 0.5 OU process, run the full Fontenele-ported pipeline and verify K_recovered ≈ 3 at σ_seed = 1. **This validator must be Phase 1 Day 1 deliverable, before any real-Pythia number is produced.** ~1 GPU-day.

**Operational-well-definedness verdict.** *Not yet well-defined*. Three specific structural issues (power-law dynamic range, no ISI analogue, layer choice) plus a missing synthetic validator. These are *solvable* but have not been solved. This is the largest risk in the project and the primary driver of the §6 decision below.

---

## 4. Venue target realism

The README targets NeurIPS / ICLR main with TMLR fallback and a stretch bridge at *Neural Computation* / *PNAS* if a cortex arm is added.

**Case for main-track.**

- Single-sentence pitch: "first direct empirical test of a 2024 *Science Advances* cortex-criticality finding on trained transformers". This is the exact format NeurIPS / ICLR *sometimes* reward — single-paper cross-disciplinary replication.
- Fontenele 2024 is a high-profile result at a high-impact venue (*Sci. Adv.* IF ~14); a clean positive replication in ML is main-track-worthy.
- The ambient-vs-subspace asymmetry is a clean, visualisable, single-figure result that competes well in 10-minute review sessions.

**Case against main-track.**

- **Liu-Paquette-Sous is workshop-level (NeurIPS OPT 2025 workshop paper 43), not main-track.** If the three-axis adjacent precedent is workshop-level, the four-predicate extension is one-predicate-beyond-workshop. That is TMLR territory, not main-track.
- **Single-observable papers rarely clear main-track even with clean execution.** NeurIPS / ICLR reward either (i) a new *method* that others will use (SAEs, path-patching), or (ii) a result that overturns a prior belief. "σ is non-trivial on low-D LLM subspace" is neither — it confirms Fontenele in a new substrate, and the ML community has no prior strong belief about subspace-σ-in-LLMs to overturn.
- **The C29 scope-check §8 explicitly positions the positive outcome as "ICML / NeurIPS main — first direct ML replication of a Sci. Adv. 2024 neuroscience result" — but that was written before the Liu-Paquette-Sous positioning work of Phase 0. The Phase 0 literature review correctly downgrades this by acknowledging three adjacent axes are published. The README has not propagated that downgrade back to the venue target.**
- **Main-track reviewers want a *method*, not a *test*.** A paper that says "we applied Fontenele's method to LLM" will be read as applied-replication work unless there is a methodological innovation — which there is (MR on reconstructed scalar, Fontenele K-selection on continuous-dense-substrate, two-subspace-asymmetry protocol). These methodological pieces need to be *foregrounded* as contributions for main-track viability.

**Honest venue ranking.**

- **NeurIPS / ICLR main (~15 %).** Realistic only if (a) all 8 bar items clear cleanly, (b) the ambient-vs-subspace asymmetry is *large* (σ_topK ≈ 1, σ_complement ≈ 0.8, σ_ambient ≈ 0.7 — the dramatic case), (c) the methodological contributions (Fontenele K on LLMs, MR on reconstructed scalar, random-subspace null) are foregrounded. Conditional on a *surprising* result (e.g., σ_topK < 1 at all scales and checkpoints → "LLMs are systematically subcritical in their critical subspace") the probability rises to ~25 %.
- ***Neural Computation* (~60 %).** Plenz-Beggs-Priesemann-adjacent reviewers would see this as a natural follow-up to Fontenele 2024; the bridge-framing is the venue's sweet spot. **Realistic primary target.**
- **TMLR (~65 %).** Technically solid + incremental-but-clean; works as a primary target if Neural Computation editor pre-rejects.
- ***Entropy* journal (~85 %).** Criticality-in-LLM is squarely in remit; reliable fallback.
- **NeurIPS UniReps / ATTRIB / MechInterp workshop (~75 %).** Natural workshop home for the bridge framing.
- ***PNAS*** — **not viable**. Morales-di Santo-Muñoz 2023 occupies the cortex-criticality PNAS territory; even with a cortex arm added, the scoop-risk from their group is real.

**Recommendation.** *Drop NeurIPS/ICLR main as the declared primary.* Target *Neural Computation* (primary) + TMLR (concurrent-if-policy-allows) + NeurIPS UniReps workshop. Keep NeurIPS/ICLR main as stretch only if Phase 2 produces the σ-dramatic-asymmetry result. The README's current "NeurIPS / ICLR main track — TMLR fallback" wording signals both over-confidence and reviewer-handing a "reject to workshop" opening. Neural Computation is the honest primary.

---

## 5. Hostile-reviewer audit (≤ 400 words)

**Reviewer #2, senior ML-theory PC member sympathetic to statistical physics — the most likely real reviewer.**

> This paper applies the Fontenele 2024 cortex-criticality protocol to Pythia residual-stream activations and reports ambient-vs-subspace σ asymmetry. Three concerns.
>
> **First: the core contribution is a one-observable extension to Liu-Paquette-Sous 2025 (NeurIPS-OPT workshop).** The covariance-spectrum trajectory through Pythia training is published. Adding σ on the top-K reconstructed scalar is a natural follow-up — so natural that I expect Liu's group has it in draft. The four-predicate-conjunction framing ("activations not gradients, Pythia not toys, σ not α, Fontenele-K not D_PR") reads as the authors' attempt to carve a niche; any one of Liu's group, Wang's group, or the Razzhigaev group closes it with a single follow-up preprint. If this paper's review cycle exceeds six months, the novelty is likely gone.
>
> **Second: the operational K-selection protocol is not well-defined on LLMs and the paper's commitments are inadequate.** Fontenele's 1.5-decade-collapse criterion depends on power-law range ≥ 3 decades in the full-K spectrum. The authors have not demonstrated this range exists on *any* Pythia checkpoint. The ISI-based time-bin criterion (Δ_T ≳ 10⟨ISI⟩) does not transfer — LLMs have no ISI. The layer-index choice is unspecified. The synthetic-validator on a continuous-activation branching process with known K is referenced but not yet run. Any of these four under-specifications could invalidate the reported K-values.
>
> **Third: single-candidate papers have no fallback.** If the protocol runs and σ_topK ≈ σ_ambient ≈ σ_complement across all 100 grid cells — the flat null — there is no paper. "Fontenele does not transfer to LLMs" is a negative result whose interest is bounded: it tells us the cortex-LLM correspondence is not as tight as a few recent reviews suggest, but it does not advance our understanding of what *does* govern σ in LLMs. The project bet everything on one candidate where a portfolio of 3–5 would have given narrative flexibility. This is a structural fragility the bundle has not addressed.
>
> **Recommendation:** reject from main track. Major revisions: (i) run the synthetic-validator and report K-recovery before submitting; (ii) pre-register layer choice and show it is not cherry-picked; (iii) add a fallback observable (e.g., the Halloran-Roysdon Lyapunov probe on the same checkpoints) so a flat-σ null is still publishable.

**Are the counters convincing?**

- **Concern 1 (scoop clock):** *not convincing as a defence, only a scheduling argument*. Ship before Q3 2026 or accept scoop risk. Nothing the paper can say makes the clock less real.
- **Concern 2 (operational well-definedness):** *addressable with Phase 0.5 work* (see §3 above). Four named fixes: synthetic validator, pilot dynamic-range check, layer pre-registration, aggregation-as-side-observable framing. **Convincing if those four are executed.**
- **Concern 3 (single-candidate fragility):** *structurally correct*. The honest counter is (a) run the synthetic-validator first so the flat-σ outcome is attributable to substrate, not pipeline; (b) consider adding one small companion observable (the Halloran-Roysdon Lyapunov probe named in the entropy_brain_homology bundle is ~3 GPU-days on these checkpoints) so a flat-σ paper still has an alternative dynamical-observable story. **Partially convincing; concern has merit that deserves portfolio reform.**

Two of three addressable; concern 3 is the structural risk this paper carries that its siblings do not.

---

## 6. Decision gate

**Verdict: REFRAME.** Not PROCEED-unchanged — the scope-check's "REFRAME → PROCEED" status has not been fully reflected in the README's venue declaration, three bar-items are silently weak, and the operational K-selection has three unsolved structural issues. Not KILL — the core scientific question (does σ-on-top-K-subspace cross 1 at training checkpoints where ambient-σ is off-critical?) is genuinely novel, testable on the declared budget, and answers either "yes" (NatComp/TMLR-quality positive) or "no" (publishable-negative-with-Fontenele-nontransfer framing).

**Required reframes before Phase 1:**

1. **Run the synthetic continuous-activation K-validator as Phase 1 Day 1.** Seed a branching process with K_true = 3 in d_synth = 100; verify Fontenele-ported pipeline recovers K within ±1 at σ = 1, with MR on the reconstructed scalar recovering σ within ±0.02. If the validator fails, *stop and redesign* before real-Pythia compute. ~1 GPU-day. **This is the single most important Phase 1 deliverable; do not skip it.**

2. **Pilot-test dynamic range on one Pythia-410M checkpoint before full grid.** Run avalanche detection at K = 1, 3, 10, 30 and check whether any K gives ≥ 2.5 decades of power-law range on Σ_K. If none does, Fontenele's 1.5-decade-collapse criterion is degenerate on this substrate and the whole operational-K approach must be replaced with a direct participation-ratio K sweep. ~2 GPU-hours. **Second Phase 1 Day 1 deliverable.**

3. **Pre-register layer choice.** Commit in Phase 0.5 to a single layer per scale (e.g., N−1 / final residual-stream), cite the convention used (tuned-lens, Ansuini hunchback, NC last-layer, or induction-head-emerging-layer), and stick with it. No silent "best layer" cherry-picking. Report the other-layer sensitivity as an appendix sweep on one scale.

4. **Add shape collapse + matched-initialisation-distribution at-init + crackling-γ on Σ_K to the bar-checklist explicitly in README.** Three items across three missing-bar-rows identified in §2. Cost: ~1.5 GPU-days total.

5. **Restructure the abstract to scope-out Griffiths-phase explicitly rather than imply universality-class.** Phrase: "exponent-matching evidence consistent with directed-percolation mean-field universality in the low-dimensional subspace, with Griffiths-phase distinguishability scoped out per Methods §X". This pre-empts Hostile Reviewer #2 Concern 3 from `entropy_brain_homology`.

6. **Drop NeurIPS/ICLR main from declared primary; target *Neural Computation* primary + TMLR concurrent + NeurIPS UniReps workshop.** §4 venue reframe. Keep main as stretch conditional on surprising Phase 2 result. Update README line 49 accordingly.

7. **Add one companion dynamical observable on the same checkpoint grid as narrative insurance against the flat-σ null.** Cheapest option: Halloran-Roysdon (arXiv:2406.00209) Lyapunov probe — gradient-of-output w.r.t. intermediate-activation, ~3 GPU-days on the 100-cell grid using existing activation hooks. If σ_topK is flat across the grid, Lyapunov-spectrum asymmetry becomes the narrative anchor. This is the single structural fix to the single-candidate fragility §5 Concern 3. **Strongly recommended; not optional if the project aims for anything above *Entropy*.**

**Bundle composition after reframe.**
- **KEEP:** C29 anchor (Fontenele operational K + MR-σ on reconstructed scalar + ambient/top-K/complement three-way comparison + random-subspace null + aggregation-sweep as side-observable).
- **ADD:** synthetic continuous-K validator (Phase 1 Day 1), dynamic-range pilot (Phase 1 Day 1), matched-init-distribution at-init control (bar item 7), shape collapse (bar item 4), crackling-γ on Σ_K (bar item 3), Halloran-Roysdon Lyapunov companion observable (narrative insurance).
- **No candidates dropped** (there is only one).

**Scoop-tracking discipline.** Re-verify `papers.csv 5042` (Liu-Paquette-Sous), `5044` (Xu), `5064/5065` (Wang dyad), and the Razzhigaev 2311.05928 entry against live arXiv weekly from Phase 1 Day 1. Any 2026 preprint from the Liu, Paquette, or Razzhigaev groups that extends to σ-on-subspace collapses the novelty margin. Ship the synthetic validator within two weeks, the full grid within six weeks, and the paper draft within ten weeks. Scoop clock is real.

**Single-candidate fragility — is it a red flag?** Yes. This paper carries concentration risk its two siblings do not — entropy_avalanches spreads across 7 candidates, entropy_brain_homology spreads across 3 candidates. One candidate means one protocol, one observable, one possible-failure-mode. Phase 0 handled this honestly by pre-verifying Fontenele against primary source, but the fragility propagates forward: if the synthetic-validator fails, if the K-selection is degenerate, if σ is flat — there is no alternative arm. Reframe #7 (Halloran-Roysdon companion observable) is the minimal structural fix. Do not skip it.

---

**One-line justification.** The narrow Fontenele-on-Pythia subspace-σ claim survives the adjacent-work landscape (Liu-Paquette-Sous, Razzhigaev, Xu, Wang), but three silent bar-gaps + three unresolved operational-K issues + single-candidate fragility mean REFRAME the bundle to add a synthetic-validator-Day-1, a Lyapunov-companion observable for narrative insurance, the three missing bar-items, and a downgrade of the declared primary venue from NeurIPS/ICLR main to *Neural Computation* before Phase 1 — the scientific question is real, the execution path is real, but the main-track framing and the single-candidate concentration both currently exceed what the evidence will support. **PROCEED-with-REFRAME.**

*Word count: ~2485.*
