# Phase 0.25 Publishability Review: QEC Drift-Aware Online Noise-Model Inference

Fresh agent, PRX Quantum posture. Inputs: `proposal_v2.md`, `scope_checks/candidate_02_review.md`, `literature_review.md`, `knowledge_base.md`, `program.md` §Phase 0.25.

## 1. Novelty taxonomy

**Category: Synthesis.** Ancestors named in proposal_v2 §1–2:
- **arXiv:2511.09491 (2025)** — sliding-window MLE drift estimator, simulation.
- **arXiv:2406.08981 (2024)** — static Bayesian (TN+MCMC) noise-parameter inference.
- **arXiv:2504.14643 (2025)** — per-edge DEM estimation, no drift.
- **arXiv:2502.21044 (2025)** — noise-model-informed decoding.
- **Riverlane LCD (2025 Nat. Commun.)** — adaptive real-time decoder with online noise-model adaptation, deployed on hardware.

The reframe's novelty claim is the **phase diagram**: identify (kernel timescale × amplitude) regions where the particle filter strictly beats both sliding-window MLE and static MCMC. Genuinely more defensible than a method-swap, but still synthesis. The filter is textbook SMC; contribution is the operating envelope.

**Cynical read:** the phase-diagram framing is the minimal reframe converting "Method C not A/B" into a synthesis claim. It works *only* if the diagram exhibits a non-trivial carved-out regime (§5-B). If every cell favours sliding-window or static, the filter collapses to method-swap with no home.

**No KILL-grounds prior art:** lit review confirms no Google/IBM/Riverlane published head-to-head SMC-vs-sliding-window-vs-static drift-inference comparison. Window narrow but not closed.

## 2. Falsifiability

**Primary headline:** "particle filter reduces mean LER vs periodic-DEM-refit by ≥5% under a pre-registered drift regime." Falsifiable: if Δmean-LER < 5%, dead. Good — variance demotion is clean.

**Secondary:** phase diagram exhibits ≥1 cell where filter strictly beats both baselines. Falsifiable via pre-registered grid.

**Remaining soft claims:**
- Synthetic fallback (§4.1): no pre-registered threshold for "dominated by arXiv:2511.09491." Reviewer will demand a specific metric.
- "Realistic refit cadences" (§4.2) unquantified. Per knowledge_base.md: minutes (thermal), hours (aging), days (bias tees). Pre-register the cadence before running.
- "Strictly beats" (§4.3) needs a fixed statistical test with multi-comparison correction across cells. Not specified.

Headline reasonably falsifiable, but three thresholds need pinning before Phase 0.5.

## 3. Load-bearing parameters

| Parameter | Committed | Lit uncertainty | Headline scaling |
|---|---|---|---|
| Raw public per-shot per-round syndrome stream | TBD after smoke test | **Unverified as of 2026-04**; Willow supplement is calibration + summary stats, not raw per-round detectors; Heron/H2 also unverified. | Real-data headline dies without it → synthetic-only, head-on vs 2511.09491. Gated in §4.1. **OK structurally.** |
| Drift-kernel timescale | Sweep {10 ms, 1 s, 1 min, 1 h} | minutes (thermal), hours (aging), days (bias tees) per knowledge_base.md. Sub-second drift not documented. | ms-scale cells likely empty — fast end of sweep risks being a dead zone. Headline needs ≥1 non-empty filter-wins cell. **Flag.** |
| Periodic-refit cadence | {never, 1/hr, 1/min} | 1/hr plausible; 1/min unrealistic on compute. | If 1/hr refit captures hours-scale drift, operational gain collapses. Filter only wins in the narrow band between refit cadence and drift mode. **Flag — this is where paper lives or dies.** |
| Particle count N | 10⁴ (d=5), 10⁵ (d=7) | 10³–10⁶ standard; degeneracy risk at dim >100 | Tractable on 24 GB GPU. Ablation at 10³, 10⁶ pre-registered. **OK.** |
| Filter state dim | per-edge Pauli + 2 drift params → O(100–200) | Degeneracy begins here without careful proposal | Rao-Blackwellisation / block structure may be needed; not discussed. **Minor flag — pre-empt-reviewer.** |

Two load-bearing: (1) raw data (gated correctly); (2) drift timescale vs refit cadence — quietly kills the paper if vendor operational refit cadence ≤ slowest drift mode.

## 4. Venue fit

**Primary: PRX Quantum.** Fit: applied-Bayesian-on-hardware with operational story. Typical objection: "quantify operational benefit over vendor periodic recalibration end-to-end, including filter compute latency; compare against Riverlane LCD-class adaptive decoders already in production." Pre-empt in v2: partial — refit comparator pre-registered (§4.2); **no LCD-class baseline mentioned**. Gap.

**Secondary: Phys. Rev. Research.** Fit: lower novelty bar, empirical-methods-friendly. Typical objection: "insufficient delta over 2511.09491 and 2504.14643 — name the regime where filter strictly beats both." Pre-empt: yes, phase diagram. OK.

**Tertiary (not named, worth adding): Quantum (journal).** Gidney/Higgott-type reviewers will demand DEM-reweight baseline Google would run and will notice if Willow raw syndromes are not actually public.

## 5. Top three killer objections

**A (fatal → partially mitigated): raw public per-shot per-round syndrome stream.** Without a public raw stream from Willow/Heron/H2, the real-data headline collapses; synthetic fallback competes head-on with 2511.09491 on its home turf. Plan: §4.1 pre-registers smoke test with KILL path — structurally correct per `feedback_verify_data_access_before_phase_0`, but the fallback-to-synthetic gate is soft: no pre-registered dominance test. Required: (i) run the smoke test before Phase 0.5; (ii) pre-register a dominance metric, e.g. "if synthetic-only mean-LER improvement over sliding-window MLE is <3% averaged across phase-diagram cells, abandon." Until (ii) is in the proposal, the fatal gate is not closed.

**B (major → partially addressed): filter-vs-method-swap.** §1 still says "particle-filter-based estimator"; §2 leans on the phase diagram. Reviewer will ask which is the paper. If the diagram yields a large filter-wins region, the filter is the contribution; if mostly ties, the paper has characterised a regime and happens to use a filter; if nearly empty, the reframe is exposed as cosmetic. Plan: phase diagram pre-registered. Gap: no pre-registered minimum-win-area criterion. Required: pre-register a threshold before running — e.g. "≥1 contiguous region covering ≥10% of the (timescale × amplitude) plane where filter strictly dominates both baselines at p<0.05 Bonferroni-corrected." Without this, REFRAME risk returns at Phase 2.75.

**C (major → addressed): variance-reduction headline was operationally hollow.** Variance is cosmetic; mean LER at matched latency is the operational metric. Plan: §2 demotes variance to secondary, promotes mean-LER-vs-refit to headline with pre-registered ≥5% threshold. §4.2 is a clean operational kill. Addressed. Residual: the 5% threshold is not anchored — Fowler 2013 correlated matching gives ~15%, Riverlane LCD ~2× in leakage-dominant regimes. Pre-empt-reviewer item: justify 5% against operational FTQC-margin numbers.

## VERDICT: REFRAME

Objection A has a gate but the gate is soft (no pre-registered synthetic-dominance test). Objection B has a phase diagram but no pre-registered minimum-win-area criterion — the exact place where "cosmetic reframe" hides. Both are fixable in a ≤1-page revision; not a KILL. The reframes in v2 on (A) gating, (C) variance demotion are real; on (B) the phase diagram is genuine but under-specified — currently a *near*-fig-leaf.

**Specific revisions required for proposal_v3:**

1. §4.1.a: pre-registered synthetic-fallback dominance test. E.g. "if smoke test fails and we fall back to synthetic-only, proceed only if expected mean-LER gain over arXiv:2511.09491 across phase-diagram cells ≥3% averaged; else KILL."
2. §2.a: pre-registered phase-diagram success criterion. E.g. "diagram must exhibit a contiguous region covering ≥10% of the (timescale × amplitude) plane where filter strictly dominates both baselines at p<0.05, Bonferroni-corrected across cells."
3. §4.2.a: pin the realistic refit cadence. E.g. "headline baseline cadence is 1 refit/hr per Willow 2024 operational cadence; 1/min is a compute-upper-bound control only."
4. §2: add explicit comparison commitment against a Riverlane-LCD-class adaptive decoder baseline on synthetic drift. Cannot pretend LCD does not exist.
5. §7: name Quantum (journal) as tertiary with the Gidney/Higgott reviewer objection.

Once v3 incorporates these five, the gate should clear on re-review. This is the **first** reframe cycle on this proposal; one further REFRAME is permitted before automatic KILL per program.md §Phase 0.25.

Pre-empt-reviewer items not appended to research_queue.md — that happens on PROCEED only.
