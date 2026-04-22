# Phase 0.25 Publishability Review — entropy_brain_homology

**Reviewer.** Phase 0.25 sub-agent, 2026-04-21. Fresh — not the Phase 0 literature agent, not the Phase −0.5 scope-check agent, not the Phase 0.5 data-access author.
**Mandate.** Answer the six review-contract questions on the LLM-vs-cortex exponent-equality bundle (C18 + C20 + C22). Be harsh — this is the most cross-disciplinary of the three promoted papers, with the highest definitional risk.
**Artefacts read.** `README.md`, `literature_review.md` (~12 k words, 384 citations), `papers.csv`, `phase_0_5_data_access.py` (DANDI smoke test, 4/4 pass), `tests/test_phase_0_5_data_access.py`, `../entropy_ideation/knowledge_base.md` §5, `../entropy_ideation/candidate_ideas.md` §§18, 20, 22, and the three Phase −0.5 scope-checks. Template inherited from `../entropy_avalanches/publishability_review.md`.

---

## 1. Is the novelty claim defensible after the Phase 0 synthesis?

**Yes, but narrowly, and the hostile one-liner is painfully close to working.** Phase 0 correctly identifies the threats:

- **Morales-di Santo-Muñoz 2023 PNAS** (`papers.csv 4014`) fits edge-of-instability to the *same* Allen Neuropixels data the README now names as primary and assigns it to *edge-of-synchronisation*, not classical MF-DP. The cortex half of the bundle's framing is therefore already occupied — the Allen exponents are not "DP with α = 3/2" in the current PNAS reading, they are a di-Santo-2018 Landau-Ginzburg edge-of-synchronisation phase.
- **Doimo et al. 2024** (`papers.csv 5049`, per-token Lyapunov on LLMs) — partial scoop on the C20 Lyapunov arm.
- **Yoneda-Nishimori-Hukushima 2025 PRR** (`papers.csv 4021`) assigns MLPs = MF and CNNs = DP; does not touch transformers, Mamba, cortex, or SpikeGPT — but sets the template that the next 2026 preprint may close.
- **Ghavasieh 2512.00168** (theory-only, activation-function-tuned DP sub-class), **Arola-Fernández 2508.06477** (Maximum-Caliber toy maze), **Halloran 2406.00209** (Mamba Lyapunov theorem) remain the three clean adjacent works. None runs a joint cortex–LLM empirical exponent-equality test.
- **Scoop-risk entry 5120** ("avalanche dynamics in spiking LLMs") is VERIFY-flagged in `literature_review.md §6` and is the single entry a Phase 0.25 agent must re-verify immediately.

**What survives as novel** is the *conjunction*: joint block-bootstrap equality test on (α, β, γ) with a CSN + MR + crackling + shape-collapse pipeline applied to (i) Allen Neuropixels in-vivo mouse spikes, (ii) pretrained-LLM residual streams (GPT-2 / Pythia / Gemma), (iii) Mamba-1/2 with Halloran-stability engagement, (iv) SpikeGPT-216M inference-only rasters — anchored by a synthetic branching-process validator that recovers seeded α on both discrete-spike and continuous-activation pipelines. No 2024–2026 paper clears the conjunction.

**Hostile one-sentence kill.** "Morales-di Santo-Muñoz 2023 already placed Allen cortex in edge-of-synchronisation and Doimo 2024 already measured per-token LLM Lyapunov, so the contribution reduces to bolting one pipeline onto two separately-measured observables — the joint bootstrap is plumbing, not a result, and if equality is rejected the reader learns nothing because 2024–2025 theory (Ghavasieh, Yoneda) already predicts architecture- and activation-function-dependent sub-class splits."

**Counter.** (a) Morales 2023 does not report matched-basis SSM or LLM measurements or a cross-substrate bootstrap equality test; the joint statistical test itself is the novelty, not any single exponent. (b) Doimo's per-token Lyapunov is one observable; the full (α, β, γ, γ-relation residual, MR-σ, shape-collapse) battery is a higher-dimensional fingerprint permitting class-splits Lyapunov alone cannot see. (c) The synthetic matched-protocol validator is itself a methodological contribution that no adjacent paper ships. But (a)–(c) push the result into "careful methodology paper + one or two new numerical facts", i.e. *Neural Computation* / TMLR, not guaranteed-ICLR-main. See §4.

**Verdict.** Novelty defensible; the margin is thin; Morales 2023 is the blade at the throat. The README's downgrade from "universality class" to "exponent equality under field-canonical protocols" is correct and non-negotiable.

---

## 2. Evidence bar vs bundled candidates (C18, C20, C22)

Crosswalk of `knowledge_base.md §5` against the three candidates, using README + `literature_review.md §Minimum evidence bar` + the scope-checks:

| Bar item | C18 (cross-substrate) | C20 (dense vs SSM) | C22 (SpikeGPT inference) |
|---|:-:|:-:|:-:|
| 1. `P(s)` via powerlaw + KS + LLR | ✓ | ✓ (both axes) | ✓ |
| 2. α ≈ 3/2 with 95 % CI | ✓ (target [1.47, 1.55]) | partial — SSM predicted off 3/2 by Halloran | ✓ |
| 3. γ = (β−1)/(α−1) | ✓ | ✓ | ✓ |
| 4. Shape collapse | ✓ | ✓ | ✓ |
| 5. σ = 1 ± 0.02 via MR ≥ 2 axes | ✓ | ✓ (layer + token; Mamba Lyapunov primary on token axis) | ✓ |
| 6. Threshold plateau | partial — MR correction replaces on cortex | partial — SiLU-vs-GELU confound per C20 §8 | ✓ |
| 7. At-init control | ✓ | ✓ (HiPPO init for Mamba) | **GAP** — no random-weight SpikeGPT baseline committed |
| 8. Neutral-null rejection | partial — Griffiths finite-size-scaling not committed | partial | partial — Touboul-Destexhe null named, not run |

**Items NOT covered by any candidate.**

- **Item 7 on C22 is effectively absent.** SpikeGPT is inference-only per C22 scope-check §3; a "random-weight SpikeGPT-216M" at-init control is ~0.5 GPU-day to run but currently not committed. Without it, C22 collapses from "trained SNN is critical" to "this SNN architecture is critical" — a much weaker claim. **Fix: commit the random-weight SpikeGPT control in Phase 0.5.**
- **Griffiths-phase rejection (`literature_review.md` bar item 9) is named but not operationalised.** Finite-size scaling on the cortex side cannot be done (no control over system size). On the LLM side, Pythia 70M/160M/410M/1.0B/1.4B gives different *populations*, not different-size samples of the same population — FSS there is a research programme, not a control. **Realistic commitment: scope Griffiths rejection *out* explicitly in §Limitations rather than silently leaving it unresolved; do not let the abstract imply universality-class identification.**

**Synthetic cross-substrate validator is the strongest single piece of the bundle.** `literature_review.md §10` commits to Zierenberg-Wilting-Priesemann-Levina 2020 (`papers.csv 5082`) with configurable σ and subsampling. Pass criterion: both pipelines recover seeded α to within 0.05 at bootstrap p > 0.1 under subsampling fractions matched to real data (p = 0.01 ssc-3; p = 0.025 Allen). This is the foundation of Figure 1 — see §3.

**CRCNS ssc-3 as "fire-and-forget secondary" is inadequate.** The README line 19 framing hides three problems:

1. Allen alone cannot distinguish DP from edge-of-synchronisation — Morales 2023 already placed it in edge-of-synchronisation. If CRCNS ssc-3 slice data does not arrive (Ito 2014 reports α ≈ 1.5 closer to pure DP), the slice-vs-in-vivo two-class framing the README implies is unsupported.
2. The `feedback_verify_data_access_before_phase_0` memory was satisfied only for Allen (4/4 DANDI pytest pass), not for CRCNS. CRCNS was not smoke-tested.
3. "Fire-and-forget" implies no tracking. The bundle needs a Phase 0.5 deliverable: (i) `phase_0_5_crcns_access.py` status-poll, (ii) pre-registered pivot — if CRCNS credentials are not granted by Phase 1 day-T, drop the slice-vs-in-vivo two-class framing and target in-vivo-only Allen + optional Senzai-Buzsaki hippocampus (`papers.csv 5175`). Convert hidden risk into tracked contingency.

**Consistency verdict.** Bar is covered in aggregate once (a) at-init SpikeGPT is committed, (b) Griffiths rejection is explicitly out-of-scope, and (c) CRCNS is elevated from optional to contingent-on-pivot. Three one-paragraph Phase 0.5 fixes; no extra compute.

---

## 3. Operational well-definedness of the matched event-definition protocol

This is the hardest question in the review. The claim's survival depends on whether cortical-spike avalanches (discrete events in time × neuron) and transformer-activation avalanches (continuous signals in token × layer × feature) are commensurable enough for a joint bootstrap on their α's to be *meaningful*.

**Correct epistemic posture.** Per the C18 scope-check §3, "matched protocol = field-canonical-within-each-substrate, not literally identical". The claim is *exponent equality*, not protocol equality. The two pipelines are matched on *methodology* (CSN + Wilting-Priesemann MR + Sethna relation) not on *observable instantiation* (spike vs activation); the synthetic validator calibrates substrate-specific bias.

**What the synthetic validator specifically tests.** Seed a known σ on the Zierenberg 2020 spiking-branching simulator (analytical ground-truth α per Lübeck 2000, `papers.csv 5038`). Render the *same* seeded process two ways: (a) as a discrete-spike raster through the cortex-side pipeline, (b) as a continuous local-activity signal through the LLM-side pipeline. Pass: both recover seeded α to within 0.05 at bootstrap p > 0.1 at matched subsampling fractions.

**Three concerns the bundle has not yet answered.**

1. **Rendering a spiking branching process as a "continuous activation" is not canonical.** Zierenberg is discrete-spiking; there is no standard spike-to-continuous map. Gaussian-kernel convolution, binarise-and-sum-in-window, and treat-as-rate-for-Poisson all produce different α-bias on the continuous-side pipeline. This is a methodology commitment the bundle owes before Phase 1, *not* a scope-check deliverable. **Fix: pre-register the rendering (e.g. "per-step local activity count rebinned to the token axis with identical threshold convention θ as LLM activations"), document it as a *methodological bridge* (not universally-accepted), cite di Santo 2018 (`papers.csv 2036`) Landau-Ginzburg equivalence as theoretical backing, and report sensitivity across at least two alternative renderings.**

2. **Subsampling analogy is thin.** Cortex subsampling = 0.6 %–2.5 % of neurons observed. LLM subsampling ≠ 1.0: all residual-stream units are recorded, but *basis choice* (raw / PCA / SAE) is a superposition analogue. The validator must seed synthetic data *and render under each basis*, not just each subsampling fraction. **The basis-axis of the validator is currently missing from `literature_review.md §10`; add it.**

3. **Autocorrelation structures differ.** Cortex avalanche bins are physical time — stationarity is clean. LLM token-axis activations are context-segmented; autocorrelation length varies with position within context. The block-bootstrap block length must be matched between sides and pre-registered. Currently the bundle cites Lahiri 1999 / Resnick 2007 without pre-registering a block length on either side.

**Can both pipelines recover a known α within CI?** At seeded σ = 1, N = 10⁵ events, p = 1: **yes, high confidence**, based on CSN performance on comparable synthetic data. At p = 0.01 and N = 10³ (ssc-3 worst case), CSN SE(α̂) ≈ 0.016 per C18 scope-check §6 and Wilting-Priesemann MR introduces additional bias — recovery within CI is **marginal**. The validator *may fail its own pass criterion* at real-data subsampling fractions. If so, the bundle must honestly report the miscalibration and widen the equality CI rather than suppress.

**Headline risk.** If the validator passes only at p ≥ 0.1 (effectively full sampling), the joint-bootstrap equality test on real data (at p = 0.01–0.025 on cortex) is *not calibrated*. The honest outcome is a methodology paper explaining the calibration gap, flagged as such — publishable in *Entropy* but not in NeurIPS/ICLR main.

**Operational verdict.** *Less* well-defined than the entropy_avalanches within-LLM observables. Defensible as "exponent equality under field-canonical protocols calibrated by a spiking-branching-process validator" — provided the validator clears its pass criterion at the subsampling fractions the real data will be analysed at. This is not currently guaranteed. **The validator must be the first Phase 1 deliverable, before any real-data number is produced.**

---

## 4. Venue target realism

**Morales-di Santo-Muñoz 2023 is already in PNAS.** Any paper re-using Allen and claiming a cortex-LLM bridge will be compared against Morales 2023. PNAS is adjacent territory, not an open field. The realistic PNAS path requires either (i) a clearly different cortex class assignment — which we cannot produce because we use the same data — or (ii) a strong positive cross-class equality (cortex *and* LLM both in edge-of-synchronisation with matched exponents to a precision Morales did not reach). (ii) is the realistic pitch and it is thin: we *confirm* Morales on the cortex side and *extend* to LLMs on the LLM side.

**Honest venue ranking.**

- **Nature Machine Intelligence (~15 %).** NatMI has published physics-of-DL-with-biology-bridge work (Cowsik-Nebabu-Qi-Ganguli 2024). A strongly-positive exponent equality with clean Halloran-theorem engagement on SSMs would fit. Editor pre-screen on "insufficient biological impact" is the main risk; cortex side is recycled rather than novel. Conditional on a *surprising* result (Mamba violates Halloran prediction; SpikeGPT differs from cortex despite mimicry) the probability rises to ~25 %.
- **PNAS (~8 %).** Morales-occupied; needs a Schwab/Bialek-level framing to clear the editor.
- **Neural Computation (~60 %).** Natural fit, Plenz-Beggs-adjacent reviewers, criticality-in-LLM squarely in remit. **Realistic primary target.**
- **PRX Life (~40 %).** Methodological-rigour-over-headline; reasonable backup.
- **ICLR / NeurIPS main (~15 %).** ML reviewers do not reward cortex-side measurements. The ML-only split (C20 + C22, drop cortex) is ICLR-main compatible; the full bundle is not. Splitting into two papers is a realistic optimisation the README does not propose.
- **NeurIPS UniReps / Brain & AI / ATTRIB workshop (~75 %).** Natural home for the bridge framing.
- ***Entropy* (~85 %).** Reliable fallback.

**Bridge-paper viability.** Yes — *if* the paper chooses Neural Computation or PRX Life as primary. The "not-quite-ML, not-quite-neuro no-man's-land" risk is real for NatMI/PNAS (which want field-redefining ML or clinically-actionable neuro) but negligible for bridge-friendly venues. Stop aspiring to PNAS given Morales occupancy; commit to Neural Computation as primary, NatMI as stretch only if a surprising result materialises in Phase 2.

**Parallel-submission recommendation.** Neural Computation (primary) + NeurIPS UniReps workshop (concurrent) + *Entropy* (fallback). Do not sequentially submit to NatMI first — Doimo 2024 / Yoneda 2025 / scoop-entry-5120 clock is too expensive.

---

## 5. Hostile-reviewer audit (≤ 400 words)

**Reviewer #2, statistical-physics-of-cortex PC member — the most dangerous reader this paper has.**

> This paper runs a CSN + MR + crackling + shape-collapse pipeline on Allen cortex and on GPT-2 / Pythia / Mamba / SpikeGPT activations, then runs a joint bootstrap for exponent equality. Three fatal concerns.
>
> **First, the cortex side is not novel and the paper misrepresents its status.** Morales-di Santo-Muñoz PNAS 2023 already placed Allen Neuropixels in edge-of-synchronisation; Hengen-Shew Neuron 2025 pooled 140 datasets at α = 1.50 ± 0.08. The authors recompute these and use them as a "reference", but the paper reads as though they discovered the cortex exponents. The methodological cost of being matched-pipeline does not repay the novelty cost.
>
> **Second, the matched protocol is not well-defined and the synthetic validator does not rescue it.** A spiking branching process rendered as "continuous activation" is a design choice with no canonical status. The validator passes on the rendering *the authors chose*; it says nothing about whether the LLM-side pipeline applied to *actual* LLM activations is commensurable with the cortex-side pipeline applied to actual spikes. The basis-axis (raw / PCA / SAE) is separately unvalidated.
>
> **Third, Griffiths-phase cannot be rejected.** Authors acknowledge this in §Limitations then frame the result as universality-class evidence in §Abstract. Finite-size scaling to distinguish MF-DP from Griffiths-quasi-critical is absent on both sides. Exponent coincidence at α ≈ 3/2 is compatible with Griffiths, and di Santo 2018's edge-of-synchronisation is closer to Griffiths than to point-critical. The Methods retreat does not propagate to the Abstract.
>
> **Recommendation:** reject from main. Major revisions: drop the cross-substrate headline; reframe as a methodology paper with secondary empirical results; cut SpikeGPT arm (tangential); add finite-size-scaling on Pythia scales.

**Are the counters convincing?**

- **Concern 1 (cortex-replication-masquerading-as-discovery):** convincing as currently framed. **Fix: rewrite the abstract to place cortex-side numbers explicitly as "validation of our matched pipeline against the Hengen-Shew 2025 pooled interval", with LLM-side numbers as the sole novel empirical result.** One-paragraph re-framing; addresses the attack.
- **Concern 2 (matched-protocol not well-defined):** partially convincing. The validator *does* test cross-pipeline commensurability on seeded synthetic data; the rendering is a design choice. Defence: foreground as a methodological innovation — "we propose a bridge rendering and test its calibration" — rather than hide it. **Fix: dedicate a Methods subsection to rendering-choice sensitivity with ≥ 2 alternative renderings.** ~2 GPU-days.
- **Concern 3 (Griffiths):** convincing on abstract wording, not on substance. Pythia-scale FSS is doable (70M/160M/410M/1.0B/1.4B on Pile, matched tokeniser/corpus) — it is work, not impossible. **Fix: commit Pythia-scale FSS as a primary result; cortex side keeps acknowledge-limitation posture.** ~3 GPU-days.

Two of three addressable with bounded extra compute; concern 1 is a framing fix; concern 3 is doable. The bundle survives this reviewer if it restructures the abstract and adds the two empirical deliverables.

---

## 6. Decision gate

**Verdict: REFRAME.** Not KILL — the cross-substrate question is real, Phase 0 is thorough, the Allen DANDI gate passes, and the bundle has a coherent story. Not PROCEED-unchanged — four load-bearing weaknesses a hostile reviewer can reach without effort.

**Required reframes before Phase 1:**

1. **Synthetic validator: pre-register basis + block-bootstrap commitments now.** §10 of `literature_review.md` names the simulator but does not commit to (a) spike-to-continuous rendering, (b) basis-axis of the validator, (c) block length on each side. Pre-register all three as a Phase 0.5 memo *before* any real-data number is produced. Validator must clear its pass criterion at subsampling fractions matching the real data (p = 0.01–0.025), not just p = 1.0. **If it fails, retreat headline to "qualitative consistency under calibrated field-canonical protocols" and target *Entropy* rather than *Neural Computation*.**

2. **Commit at-init SpikeGPT-216M control (random-weight inference).** Bar item 7 currently absent on C22. ~0.5 GPU-day. Without it, C22's "training tunes criticality" collapses.

3. **Promote CRCNS ssc-3 from "fire-and-forget optional" to "contingent-on-pivot tracked secondary".** Add: (i) status-poll script for CRCNS account, (ii) pre-registered pivot — if credentials not granted by Phase 1 day-T, drop slice-vs-in-vivo two-class framing and target in-vivo-only Allen + optional Senzai-Buzsaki hippocampus (`papers.csv 5175`).

4. **Restructure the abstract: cortex-side numbers as *validation*, not *discovery*.** Hostile Reviewer #2's Concern 1 is the single biggest framing risk. The LLM side is the sole novel empirical contribution; cortex side is a validated pipeline anchor to Hengen-Shew 2025 / Morales 2023. Write it that way from day one.

5. **Venue realignment.** Drop NatMI/PNAS from primary. Target Neural Computation (primary) + NeurIPS UniReps workshop (concurrent) + *Entropy* (fallback). NatMI/PNAS return as stretch only if Phase 2 produces a surprising result.

6. **Explicit finite-size-scaling on Pythia scales.** Currently the Griffiths acknowledgement lives only in Methods-limitations. Commit Pythia-70M/160M/410M/1.0B/1.4B scan as an explicit section. ~3 GPU-days. Cortex FSS remains out of scope (acknowledged).

**Bundle composition after reframe.**
- **KEEP:** C18 (cross-substrate anchor; cortex explicitly framed as validation, LLM as discovery), C20 (architecture-class dense-vs-SSM; Halloran-Mamba-Lyapunov primary on token axis), C22 (SpikeGPT-216M inference-only + random-weight at-init control added).
- **ADD:** at-init SpikeGPT control (§2), Pythia-FSS commitment (§6), CRCNS pivot deliverable (§3). All within-bundle; no new candidates.
- **No candidates dropped.**

**Scoop-tracking discipline.** Re-verify `papers.csv` entries 5049 (Doimo), 5120 (spiking-LLM avalanche preprint), 5122 (GPT-2 temperature-tuned σ), 4021 (Yoneda), 5113 (Halloran-Roysdon follow-up) against live arXiv before Phase 1. Any becoming a direct scoop during Phase 1 collapses the novelty margin.

---

**One-line justification.** The bundle is cross-disciplinarily coherent and Phase 0 is thorough, but Morales-di Santo-Muñoz 2023 PNAS on the cortex side plus Doimo 2024 / Yoneda 2025 on the ML side have cut the novelty margin to the precision of the matched-protocol calibration — REFRAME to make the synthetic validator the first Phase 1 deliverable, explicitly downgrade the cortex side to pipeline-validation, rewrite the abstract accordingly, realign the venue target away from NatMI/PNAS, and add two small empirical commitments (at-init SpikeGPT + Pythia-FSS) before starting Phase 1. **PROCEED-with-REFRAME.**

*Word count: ~2470.*
