# Phase 0.25 Publishability Re-Review (v3): QEC Drift-Aware Online Noise-Model Inference

Fresh agent, PRX Quantum posture. Final permitted reframe cycle per program.md §Phase 0.25. Inputs: `proposal_v3.md`, `publishability_review.md` (v2 verdict), `proposal_v2.md`, `literature_review.md`, `knowledge_base.md`, program.md §Phase 0.25.

## 0. Revision-by-revision compliance check

**Revision 1 — §4.1.a pre-registered synthetic-fallback dominance test.** ADDRESSED.
v3 §4.1.a: *"if the smoke test fails and we fall back to synthetic-only, proceed as publication-target only if expected mean-LER gain over arXiv:2511.09491 sliding-window MLE is ≥3% relative averaged across the 24 phase-diagram cells at the pre-registered metric (2.1) measured on a pilot run before Phase 0.5 commit."* This matches the v2-reviewer's illustrative threshold (≥3% vs 2511.09491, averaged across cells) exactly and ties the gate to a pilot run before Phase 0.5 commit. The gate is closed. Mildly cynical note: the ≥3% number is plucked from the prior reviewer's own example sentence rather than independently anchored, but that was what was asked for.

**Revision 2 — §2.2 pre-registered phase-diagram success criterion.** ADDRESSED.
v3 §2.2: *"a contiguous region covering ≥10% of the scanned (timescale × amplitude) plane where the particle filter strictly dominates both baselines (sliding-window MLE and static Bayesian) at p < 0.05 under Bonferroni correction across cells, with 'strict dominance' defined as mean LER lower by ≥1% relative at the 95% CI lower bound."* All three pieces the prior reviewer demanded (contiguous-10%, Bonferroni, strict-dominance operationalisation) are present and the fallback to regime-characterisation-note is explicit. Not a fig leaf — see §2 below for the tightness audit.

**Revision 3 — §4.2.a pinned realistic refit cadence.** ADDRESSED.
v3 §4.2.a: *"The headline comparator is 1 refit/hr, per Willow 2024 reported operational cadence (Acharya et al., Nature 2024 supplement), with 1/min as a compute-upper-bound control only."* Cadence named, anchor cited, 1/min demoted to upper-bound control. Clean.

**Revision 4 — §2 LCD-class adaptive-decoder baseline commitment.** PARTIAL.
v3 §2.3 and §3 commit to a Riverlane-LCD-class baseline, with a stated fallback to "published-algorithm reimplementation with version-controlled protocol". The commitment exists, but the reimplementation-quality-gap risk (home LCD under-performing Riverlane production) is not acknowledged in-line. See judgement call (b) below.

**Revision 5 — §7 Quantum (journal) as tertiary venue.** ADDRESSED.
v3 §7 names Quantum (Verein), attaches the Gidney/Higgott-type reviewer profile demanded by the prior reviewer, and explicitly pre-empts both objections (1/hr-DEM baseline = Google-style cadence; smoke-test outcome public). Clean.

## 1. Novelty taxonomy

**Category: Synthesis.** The §2.0 contribution statement repositions the work as *regime characterisation at matched compute budget*: "under which (timescale × amplitude × refit-cadence) conditions does online SMC strictly beat sliding-window MLE and static Bayesian, and in what subset does it also beat LCD-class adaptive decoding?" The particle filter is explicitly demoted to one of three methods benchmarked.

The pivot is genuine, not cosmetic, *provided* the phase diagram is non-degenerate. Key tests: (i) pre-registered success criterion (§2.2) binds the filter-as-method claim to a measurable region; (ii) the §4.3 regime-kill clause converts negative results into a downgraded characterisation note rather than a silent scope change. Both are present.

Residual cynicism: the filter remains textbook SMC with Rao-Blackwellisation, the three ancestors (2511.09491, 2406.08981, 2504.14643) are reimplemented, and the LCD baseline is a reimplementation. The novelty lives *entirely* in the phase diagram being non-trivially carved. That is synthesis, not genuinely new. The proposal does not oversell.

## 2. Falsifiability

**Single measurable outcome that kills the headline:** the 24-cell (timescale × amplitude) phase diagram fails to exhibit a contiguous region covering ≥10% of the plane where the filter achieves mean LER ≥1% lower (relative, 95% CI lower bound) than *both* sliding-window MLE and static Bayesian baselines at p<0.05 Bonferroni-corrected across 24 cells. Per §4.3 this forces downgrade to a regime-characterisation note.

**Is the §2.2 criterion tight?** Mostly yes. Contiguous-10% of a 6×4 grid = ~2.4 cells touching — a lax-to-moderate bar; adjacency on a log-scaled kernel axis means two neighbouring cells at one amplitude would suffice. Bonferroni across 24 cells at α=0.05 is genuinely conservative (per-cell α=0.002). The ≥1% relative strict-dominance margin at 95% CI lower bound is modest. Combined, the bar is weak on area but strong on statistical test — a reviewer could plausibly argue the 10% area threshold is too low, but ≥10% × Bonferroni × ≥1%-at-lower-CI is defensible as a pre-registration. Not cherry-picked toothless.

**Remaining soft claims.** (a) The §4.2 operational-kill threshold ("within 5% of 1/hr periodic-DEM"): mirrors the §2.1 5% headline, consistent. (b) §4.1.a "measured on a pilot run before Phase 0.5 commit" — "pilot run" is not operationally defined (particle count, number of cells sampled, number of seeds). Minor; a reviewer will not fail v3 over this but it wants pinning before Phase 0.5 commits.

## 3. Load-bearing parameters

| Parameter | Committed | Lit uncertainty | Scaling | Stability |
|---|---|---|---|---|
| Raw public per-shot per-round syndrome stream | TBD after smoke test; synthetic-only gated by §4.1.a ≥3% | Willow supplement = calibration/summary, not raw; Heron/H2 unverified as of 2026-04 | Real-data headline dies without it | Gated. OK structurally. |
| Drift-kernel timescale | Sweep {10 ms, 1 s, 1 min, 10 min, 1 h, 6 h} | Minutes (thermal), hours (aging), days (bias tees). Sub-second undocumented. | ms cells likely empty; filter-wins band lies between refit-cadence (1/hr) and drift mode | Flag. Hardest cells are the 1/s–1/min band — plausible non-empty. |
| Headline refit cadence | 1/hr (pinned) | Anchored to Willow 2024 | Narrow-band filter advantage | Fixed; OK. |
| Particle count N | 10⁴ (d=5), 10⁵ (d=7); ablation at 10³, 10⁶ | Standard; degeneracy risk >10² state dim | Tractable on 24 GB GPU | OK. |
| Filter state dim | per-edge Pauli + 2 drift params, Rao-Blackwellised | Degeneracy at dim >100 without careful proposal | Directly threatens convergence | OK (pre-empt-reviewer item addressed in §3 via Rao-Blackwell + block-diag proposal). |
| LCD reimplementation fidelity | "closest open reimplementation; else published-algorithm reimplementation with version-controlled protocol" | Riverlane production code may not be public; FPGA-optimised LCD unavailable | Weak LCD baseline makes LCD-comparison strictly less meaningful | **Flag. See judgement (b).** |
| Statistical test | per-cell paired t-test, Bonferroni over 24 cells, α=0.05, ≥1% at 95% CI lower | Fixed | Success criterion | OK. |

## 4. Venue fit

**Primary: PRX Quantum.** Fit — applied-Bayesian-on-hardware, operational story, LCD head-to-head. Typical objection: *"quantify operational benefit over vendor periodic recalibration including filter compute latency, compare against adaptive decoders in production."* Pre-empt: §2.3 + §4.2.a ("filter latency matched to periodic-refit wall-clock"). Addressed.

**Secondary: Phys. Rev. Research.** Fit — empirical-methods, lower novelty bar; natural home if the phase diagram lands marginally. Typical objection: *"insufficient delta over 2511.09491 — name the regime."* Pre-empt: §2.2. Addressed.

**Tertiary: Quantum (Verein).** Fit — open-access, QEC-heavy, methods-plus-regime-characterisation tolerant. Objection (Gidney/Higgott-type): *"will demand a DEM-reweight baseline Google themselves would run; will notice if Willow raw syndromes are not actually public."* Pre-empt: §4.2.a 1/hr cadence = Google-style operational cadence, §4.1 smoke-test outcome made public. Addressed.

## 5. Top three killer objections

**A (major → addressed): LCD baseline is a reimplementation, not the production Riverlane FPGA decoder.** Risk: a home LCD under-performs, making the comparison unfair to LCD and artificially inflating the particle-filter win region. Pre-empt: version-controlled protocol is committed; the reimplementation-quality-gap is *not* explicitly acknowledged in v3. Mitigable by (i) publishing the LCD protocol-conformance tests against Riverlane's published benchmarks and (ii) phrasing the paper's claim as "vs published LCD protocol at matched reimplementation fidelity", not "vs Riverlane production". Scored major-not-fatal because the phase diagram against the two *other* baselines (sliding-window MLE, static Bayesian) is the primary contribution; LCD is a secondary stress test. Pre-empt-reviewer item.

**B (major → addressed): filter-wins band lies in the narrow slot between 1/hr refit and slow drift modes.** If kernel timescale ≪ 1 hr, periodic 1/hr refit lags drift (filter wins); if ≫ 1 hr, drift is essentially static (static Bayesian wins); if ≈ 1 hr, both tie. Narrow operating band is a *feature* of the regime-characterisation framing — as long as it is non-empty. §2.2 contiguous-10% criterion lands this. Pre-empt-reviewer item: justify 10% as publishable operational territory rather than a boutique sliver.

**C (minor → addressed): data-access gate leaves the headline language ambiguous until smoke test runs.** If synthetic-only, the paper is head-on against 2511.09491 on its home turf; the §4.1.a ≥3% gate is the mitigation. Scored minor because the gate is specific and pre-registered.

No new fatal objection has surfaced that v2 missed.

## Judgement calls

**(a) 5%-threshold defensibility (§2.1).** Defensible as a floor, not cherry-picked. Anchors: Fowler 2013 correlated matching ≈15% (upper ref), Riverlane LCD ≈2× leakage-dominant gain (upper ref), Gidney–Ekerå 2025 FTQC reaction-time axis (sensitivity ref). The argument "below 5% the improvement is absorbed by FTQC resource-estimation sensitivities" is plausible — FTQC resource estimates are famously elastic to decoder-margin assumptions at the 5–15% level. It is *also* true that 5% is a round number and the proposal does not quantify the Gidney–Ekerå sensitivity envelope numerically. A tougher reviewer would demand a sensitivity-envelope number; PRX Quantum will likely accept the anchoring as presented. Verdict: not a fig leaf, but on the soft end of "justified" — pre-empt-reviewer item.

**(b) LCD reimplementation-quality-gap acknowledgement (§2.3).** This is the weakest spot in v3. The commitment to "closest open reimplementation / published-algorithm reimplementation with version-controlled protocol" is concrete *enough* operationally (it names the procedure), but the proposal does *not* acknowledge the asymmetric risk — that a home LCD reimplementation may under-perform Riverlane production, causing the apparent filter-vs-LCD comparison to actually measure filter-vs-weakened-LCD. A PRX-Quantum reviewer with Riverlane ties will flag this. This should be upgraded in the paper by: (i) stating the reimplementation-quality risk explicitly, (ii) reporting LCD-reimplementation benchmarks against published Riverlane figures before reporting the filter-vs-LCD comparison, and (iii) phrasing the claim as "vs published LCD *protocol*" not "vs Riverlane deployment". PARTIAL, not NOT ADDRESSED — the commitment exists, the risk acknowledgement is missing. Mitigable at paper-draft stage; pre-empt-reviewer item.

Neither (a) nor (b) is a fig leaf in the strong sense — (a) is a softly-justified but defensible round number; (b) is an operational commitment that needs a stated risk acknowledgement. Both are fixable as pre-empt-reviewer items without reframe.

## VERDICT: PROCEED

All five prior-reviewer revisions are addressed (four fully, revision #4 partially in the specific sense above); no new fatal objection has emerged; three plausible venue fits remain pre-empted. The §2.0 regime-characterisation pivot is genuinely load-bearing and pre-registered, not cosmetic. Two judgement-call items ((a), (b)) and killer objection A remain, but each is mitigable at paper-draft stage and the commitment structure in v3 supports that mitigation.

**Pre-empt-reviewer items to append to `research_queue.md`:**

1. **LCD-reimplementation quality-gap benchmark.** Before running filter-vs-LCD on the phase diagram, run LCD reimplementation against published Riverlane benchmarks; report protocol-conformance gap; phrase the filter-vs-LCD claim as "vs published LCD protocol at matched reimplementation fidelity".
2. **5%-threshold FTQC-sensitivity envelope.** Quantify the Gidney–Ekerå 2025 reaction-time resource-estimation sensitivity numerically so "below 5% is absorbed by FTQC sensitivities" is backed by a computed envelope rather than an asserted one.
3. **Narrow-band operational territory.** In the paper, motivate the contiguous-10% criterion in terms of operational deployment value (time-to-recalibration window × fleet scale) so the filter-wins region is framed as publishable territory rather than a boutique sliver.

Word count: ~1330.
