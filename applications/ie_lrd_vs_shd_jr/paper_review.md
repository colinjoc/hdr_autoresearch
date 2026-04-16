# Phase 2.75 Blind Review — LRD vs SHD judicial-review intensity

**Reviewer**: independent (did not participate in Phases 0-2.5)
**Date**: 2026-04-16
**Artifacts read**: `paper_draft.md`, `results.tsv`, `tournament_results.csv`,
`analysis.py`, `phase_b_discovery.py`, `data_sources.md`, `knowledge_base.md`,
`literature_review.md`, ABP 2023 and 2024 raw text, predecessor project
`ie_shd_judicial_review/paper.md`.

## Decision: **MAJOR REVISIONS**

The draft is intellectually honest in §6 but the Executive/Abstract and §4.1
over-claim well beyond what the data can support. Specifically the headline
"SHD 6.4% vs LRD 8.6%, p=0.51" is computed from two incompatible populations
stitched together with a denominator mismatch, and the Phase B projection
operates on a baseline rate (`LRD_RATE_2024 = 7/79 = 8.86%`) that the paper's
own §4.5 admits is based on effectively 2 decided cases. The findings
directionally belong; the *precision with which they are stated* does not.

The paper must either (a) be substantially re-framed as a
"data-cannot-yet-answer" methodology and monitoring report, or (b) shore up
its numerator/denominator alignment, its concurrent-trend controls, and its
projection baseline before any comparative claim can survive. I recommend
path (a) with the experiments below to support it.

## Major Concerns

### C1. Headline denominator mismatch is not just "partial" — it is invalid

The E00 / E22 headline comparison is:

| | numerator | denominator |
|---|---|---|
| SHD 6.4% | **16 JRs decided in 2018-2021** | **250 SHD ABP decisions in 2020-2021** |
| LRD 8.6% | 10 LRD JRs *received* in 2023-2024 | 116 LRD appeals *concluded* 2022-2024 |

Three flaws compound:

1. **Numerator–denominator window mismatch on SHD.** The SHD numerator
   spans four years (2018-2021) but the denominator spans two (2020-2021)
   because `analysis.py` uses only the ABP facts it has. That inflates the
   SHD rate toward the LRD rate and makes the Fisher p=0.51 meaningless.
   Predecessor project data for 2018-2019 SHD decisions exists at ABP annual
   report level and must be pulled.

2. **"Received" vs "decided" across sides.** The SHD numerator is *decided
   JRs from the OPR list*. The LRD numerator is *JRs received by ABP by
   development type* (Table 2 of the 2023 and 2024 annual reports). Those
   are categorically different populations: received-but-not-decided JRs can
   be withdrawn, conceded, or still pending. Stated another way, SHD 2018-21
   "received" was in the low-30s (press tracking ~35); SHD "decided
   2018-21" was 16. The equivalent move on the LRD side (received→decided)
   yields 2, not 10. So the honest like-for-like comparisons are either
   (received vs received, ~35/~X vs 10/116) or (decided vs decided, 16/~X
   vs 2/116). Mixing received for LRD with decided for SHD flatters LRD.

3. **The "truly LRD-era" denominator is even smaller.** The 116
   LRD-appeals-concluded denominator contains appeals whose underlying *LA
   first-instance decisions* stretch back to late 2022. But per §4.5, only
   2 of the 10 LRD-tagged JRs are substantive outcomes. Whether the other
   8 are against LA-first-instance LRD decisions or against LA-first-instance
   cases that never reached ABP is unclear from the annual reports. The
   draft should either identify how many of those 10 JRs target LA
   decisions vs Board decisions, or treat the "decided LRD-era JRs on
   LRD-era permissions" count as 2.

**This must be fixed before any "6.4% vs 8.6%" number appears anywhere in
the paper.**

### C2. T01 climatology winning is a precision diagnostic, not a finding

The draft handles this well in §3.2 ("a data-availability finding, not a
null-effect finding") but the Executive line — "On the cleanest available
per-decision denominator, LRD's 2023-2024 JR rate is *not* lower than SHD's"
— leaks the climatology victory into a comparative claim. At N=24 case-level
observations (with 2 of those 24 being LRD) no tournament can adjudicate
effect size. The paper should explicitly state that **the tournament is
informative about model-fit at this N, not about regime effect**, and move
that caveat to the Abstract. Remove "not lower than" from the headline and
replace with "not yet estimable".

### C3. T03 ITS does not control for concurrent trends

§6 correctly identifies three concurrent interventions during the LRD
window:

- **Planning and Environment List** commencement (Nov 2022)
- **Heather Hill Supreme Court judgment** (Jul 2022) on Aarhus costs
- **2024 concession spike** (53 concessions vs 15 losses) attributable to
  Board's new defensive posture and precedent cascades

None of these enter T03 as covariates. The regression is literally
`state_loss ~ year`; it cannot disentangle the LRD effect from any
secular trend sharing the same sign. This is a *structural* limitation of
the current experiment, not a data limitation. A meaningful ITS requires
either a segmented knot at each intervention or a control series (e.g.,
Commercial-type JR rate as a placebo, since Commercial is unaffected by
SHD→LRD but affected by list commencement and Heather Hill).

### C4. Per-permission denominator is the substantively correct one, and it is absent

The regime difference matters for per-permission JR exposure *per housing
unit consented*. Under SHD, every ≥100-unit scheme was in the numerator
universe because every ≥100-unit scheme went to ABP directly. Under LRD,
ABP-appeal-concluded schemes exclude all LA-first-instance LRD approvals
that were *not appealed* to the Board. So the 116-denominator systematically
*under-counts LRD permissions*, which inflates the per-decision LRD JR rate.
The honest denominators are:

- **SHD per-permission**: total SHD permissions granted 2018-2021.
- **LRD per-permission**: total LRD permissions granted (LA decision +
  Board appeal outcome) 2022-2024. This requires DHLGH LA-level data that
  the project flags in E15 as "not in ABP annual reports" but does not
  pursue.

The paper must either (a) source DHLGH LA-level LRD decisions data, or (b)
acknowledge the per-permission question is *unanswerable from ABP data
alone* and demote the E20 "LRD 8.6% vs NSIP 3-5%" comparison because the
8.6% is on a definitionally different denominator than the NSIP figure.

### C5. Phase B projection is circular

`phase_b_discovery.py` uses `LRD_RATE_2024 = 7/79 = 8.86%` as its baseline
and projects a 50% reduction under PDA 2024. But:

1. The 7 is *JRs received against LRD in 2024*. The 79 is *LRD appeals
   concluded in 2024*. The 7 JRs do not necessarily target the 79
   concluded appeals — they target whichever Board LRD decisions were
   made in or near 2024, and most of those 7 were lodged but likely not
   yet decided at the time of the 2024 ABP report.
2. With a numerator of 7 and a denominator of 79, the Wilson 95% CI on the
   per-appeal JR rate is approximately **[3.9%, 17.6%]**. A 50% reduction
   from a point estimate inside a 14-pt CI is not a meaningful target; the
   CI on 50%-reduced rate overlaps massively with the CI on the baseline
   itself.
3. The "central" scenario mixes three separately-parameterised effects
   (annual rate reduction 15%, ELCFA 40%, list-throughput 1.5×) with no
   empirical anchor for any of them. The paper labels it a "scenario
   sketch", which is honest, but the summary table "hits 50% target in
   2028" reads like a forecast. A reader will remember "2028", not the
   sketch caveat. The projection must either be deleted or re-framed as
   "conditional on assumptions that this paper does not estimate".

### C6. SHD-carryover vs LRD-era-permission separation is acknowledged but not enforced

§4.3 correctly identifies E14 as the decisive lever and §6 bullet 2
correctly names the ~23 SHD-substantive outcomes in 2024 as carryover.
But the top-line comparison at §4.1 does not actually implement a
permission-year cohort split. The paper's own Discussion defeats its own
Abstract. The fix is mechanical: add a row to `results.tsv` that restricts
the SHD numerator to permissions granted strictly in 2018-2021 and
restricts the LRD numerator to permissions granted strictly in 2022-2024,
and quote *those* rates as the headline.

### C7. The paper confuses "appeals concluded" with "permissions granted" in multiple places

Examples:

- Abstract/§4.1: "LRD 10/116 = 8.6% (ABP 2022+2023+2024 LRD appeals
  concluded)". `analysis.py` computes the same value. But the numerator
  (10) is a count of LRD-tagged *JR applications received* across two
  years (2023-2024), while the denominator (116) is a count of *ABP-stage
  appeals concluded* across three years (2022-2024). A JR received in
  2023 might target an LA decision that was not even appealed to ABP, or
  might target a 2024 ABP concluded appeal. The paper needs to state
  which population each number describes and then pick a single,
  coherent denominator.
- §4.5 reports a "per-appeal JR rate 2023=8.3%, 2024=8.9%" without noting
  that the appeal-concluded series includes appeals that cannot have been
  JR'd yet because the JR window hasn't closed.

### C8. 2024 concession spike is treated inconsistently

§4.4 notes "the concession rise is universal across types, not
regime-specific." §6 bullet 3 correctly flags it as a concurrent trend.
But §4.2 reports "LRD 2/2 = 100% state loss" with only a generic
"denominator far too small" caveat. Given that *both* LRD substantive
outcomes in 2024 are concessions (not losses), and that concessions are
up 30pp system-wide in 2024, the LRD state-loss rate is mechanically
determined by the concession-spike secular trend — it tells us nothing
about the LRD regime. The paper should say so.

### C9. Every stated percentage lacks a bootstrap CI

Wilson CI is computed (correctly) for 6.4% and 8.6%, but *none* of
E02/E03/E06/E08/E10/E11/E17/E18/E21/E23 have any uncertainty
quantification. Several of those percentages are computed on
denominators of 2–5 events where even a normal-approximation CI would
span the entire [0, 1] interval. These look like findings when presented
as bare percentages — they are not.

### C10. Literature review acknowledges but does not operationalise Firth / Bayesian shrinkage

Theme 3 (§Statistical methodology) in `literature_review.md` explicitly
cites Firth-penalised logistic [P126, P127] and weak-informative-prior
Bayesian approaches [P109, P110, P136] as the *appropriate* tools for
rare-event small-N JR-rate estimation. None of T01-T05 implement these.
T02 (vanilla logistic) with an N=2 LRD group yields `b1=-16.166` —
effectively divergent — which is exactly the symptom Firth penalisation
is designed to fix. This is a visible "lit review → methodology" gap
that Phase 2.75 explicitly guards against.

### C11. Minor: `shd_valid_apps` used in place of `shd_decisions` in E14

`analysis.py` line for E14 reads
`ABP_FACTS[2022]['shd_valid_apps']` (127) + `ABP_FACTS[2023]['shd_decisions']`
(56) + `ABP_FACTS[2024]['shd_decisions']` (44). The 2022 term uses
*applications received* where the other two terms use *decisions*. This is
presumably a typo but the sum (227) is quoted in §4.3 as "carryover SHD
cases". Fix to homogeneous definition.

## Mandated Experiments

These must all appear as new rows in `results.tsv` and be referenced from
the revised paper. Each is a *concrete* spec with inputs, outputs, and
acceptance criteria.

### R1 — Permission-year cohort alignment (fixes C1, C6)

- **Inputs**: SHD permissions granted Jan-2018 to Dec-2021 (from ABP
  annual reports 2018, 2019, 2020, 2021 for the numerator-side consent
  count; 2018 and 2019 ABP PDFs must be added to `data/raw/`). LRD
  permissions granted Jan-2022 to Dec-2024 (LA-level DHLGH data +
  ABP-appeal outcomes).
- **Output**: a four-row table
  (regime × {numerator=decided JRs, denominator=permissions-granted})
  with Wilson 95% CI and Fisher exact p on the matched per-permission
  rate. If DHLGH LA-level data cannot be obtained, output a single
  "UNANSWERABLE" row with the justification and DELETE every per-decision
  comparative claim from §4.1 and the Abstract.
- **Acceptance**: the headline comparison has matched window lengths
  (4-year SHD cohort vs 3-year LRD cohort) and matched denominator
  definitions. If R1 shows the comparison is unanswerable, the paper
  must state "not yet testable" rather than "not statistically
  distinguishable".

### R2 — Lodged-JR denominator alternative (fixes C1(2), C7)

- **Inputs**: press-tracking + FOI SHD JR-lodged count (Irish Times and
  Business Post 2021 coverage gives ~35 lodged by end-2021; validate
  figure against OPR Bulletin 10 if reported there). ABP 2023 Table 2
  LRD JRs received = 3. ABP 2024 Table 2 LRD JRs received = 7. Also
  include any 2022 LRD JRs (likely 0, confirm).
- **Output**: a second headline line "lodged-JR per permission": SHD
  ~35/[permission count] vs LRD ~10/[permission count]. Wilson CI and
  Fisher exact on this lodged-basis comparison.
- **Acceptance**: the paper reports both decided-basis and lodged-basis
  comparisons side by side, and takes no position on which is "the"
  answer. Discrepancies between them are discussed in §6.

### R3 — ITS with concurrent-trend controls (fixes C3)

- **Inputs**: monthly JR-rate series 2017-01 to 2024-12. Three knots:
  (a) SHD→LRD (Dec-2021), (b) Heather Hill (Jul-2022), (c) Planning and
  Environment List commencement (Nov-2022). Control series: Commercial-type
  JR rate (placebo — SHD→LRD does not affect Commercial).
- **Output**: segmented regression with three level and three slope
  terms; placebo series run in parallel. Report coefficient on
  LRD-step controlling for the other two steps and for secular trend.
  Include pre-specified bandwidth robustness (±3 months, ±6 months on
  each knot).
- **Acceptance**: ITS coefficient on LRD step must be reported with its
  CI; if the CI overlaps zero or overlaps the Heather Hill/List
  coefficient CIs, the paper must say "the LRD effect cannot be
  separated from concurrent interventions at this sample size".

### R4 — Bootstrap CI on every quoted percentage (fixes C9)

- **Inputs**: every row in `results.tsv` with a percentage metric
  (E02, E03, E06, E08, E09, E10, E11, E13, E14, E17, E18, E21, E22, E23,
  P01-P08). Use 10,000-iteration nonparametric bootstrap for each
  percentage where case-level data exists; for aggregate table-derived
  percentages where only counts are available, use Clopper-Pearson
  exact CI.
- **Output**: each row's `value` field gets an appended
  " [CI_lo%, CI_hi%]" suffix. Rows where the CI spans more than 30pp
  get a new status `"wide_CI"` and are reported as qualitative not
  quantitative in the paper.
- **Acceptance**: no percentage appears anywhere in the paper without a
  CI or an explicit "denominator too small, qualitative only" flag.

### R5 — Per-permission-with-housing-size denominator (fixes C4)

- **Inputs**: ABP 2024 note "3,042 dwellings were subject to JR initiated
  in 2024". Historical SHD unit counts: from ABP annual reports
  2018-2021 (SHD permissions × units-per-permission, reported in
  annual reports as "total units sanctioned under SHD"). LRD 2022-2024
  unit counts from LA-level DHLGH data.
- **Output**: dwellings-under-JR / dwellings-permitted ratios per regime
  per year, with Wilson CI. Compare SHD per-unit JR exposure to LRD
  per-unit JR exposure. If DHLGH data unavailable, mark
  `"REVERT: per-unit comparison requires LA-level data not obtained"`.
- **Acceptance**: either a real per-unit comparison appears, or the
  per-unit question is explicitly withdrawn from the paper scope.

### R6 — Phase B honesty check (fixes C5)

- **Inputs**: `phase_b_discovery.py`, `LRD_RATE_2024 = 7/79`.
- **Output**: propagate the Wilson CI on `LRD_RATE_2024` through every
  scenario projection. Report each scenario's target-year *range* under
  (baseline rate lower bound) and (baseline rate upper bound). If the
  "central" scenario's target-year range under baseline-CI overlaps the
  "pessimistic" scenario's range, the projection is *not informative*
  and must be relabelled as such.
- **Acceptance**: no "year 2028" type point-estimate appears in the
  paper. The projection section must either show year-range bands under
  baseline uncertainty, or be deleted.

### R7 — Firth-penalised logistic rerun of T02 (fixes C10)

- **Inputs**: same 24-case panel used in T01-T05.
- **Output**: Firth-penalised logistic `state_loss ~ regime` + Firth
  `state_loss ~ year` + weak-informative-prior Bayesian logistic with
  Beta(16, 3) prior on SHD state-loss rate and Beta(1, 1) uniform on LRD
  state-loss rate (uninformative prior for LRD because it is the
  quantity of scientific interest). Report posterior mean and 95%
  credible interval for LRD vs SHD difference.
- **Acceptance**: the tournament section reports both AIC-ranked
  frequentist families *and* the Firth/Bayesian results; any claim about
  regime effect must be sourced from the Firth/Bayesian result because
  vanilla logistic is known to diverge at this N.

### R8 — LRD-era-permission vs SHD-carryover disaggregation of the "10" (fixes C1(3), C7)

- **Inputs**: OPR Bulletin 10 and 11 (already in `data/raw/`). ABP 2023
  Table 2 LRD=3 and ABP 2024 Table 2 LRD=7.
- **Output**: for each of the 10 LRD-tagged JRs, attempt to identify
  from OPR Bulletin narrative (a) the underlying permission date,
  (b) whether the challenged decision was the LA first-instance or the
  ABP appeal. Report a split table: "LRD-era permissions JR'd" vs
  "other (LA-first-instance or ambiguous)".
- **Acceptance**: the paper's LRD numerator for the headline either
  shrinks to the identified LRD-era-permission subset, or the paper
  explicitly flags that the 10 is a mixed population and cannot be used
  for per-permission rate estimation.

### R9 — Placebo: Commercial and Infrastructure JR rate trajectories (supplements C3, C8)

- **Inputs**: ABP annual reports 2020-2024. Commercial and Infrastructure
  JR counts per year, and ABP Commercial/Infrastructure decisions per
  year.
- **Output**: per-year JR rate for Commercial and Infrastructure from
  2020 to 2024. These development types are unaffected by SHD→LRD but
  affected by list commencement, Heather Hill, and PDA2024 signalling.
  If the Commercial/Infrastructure JR rate rose in 2022-2024 by a
  similar magnitude to the SHD rate or the aggregate rate, the paper
  must state that "system-wide JR growth is the dominant trend; the
  SHD→LRD contribution is indistinguishable."
- **Acceptance**: Commercial/Infrastructure rates appear in §4.4 as
  control series; §6 draws the explicit "system-wide vs regime-specific"
  contrast.

### R10 — 2024 concession-artefact sensitivity (fixes C8)

- **Inputs**: 2024 ABP Table 3 by development type. Historical 2020-2023
  concession shares from ABP annual reports.
- **Output**: recompute every state-loss-rate metric in §4.2, §4.3
  (E06, E17, E23) with 2024 concessions (a) included, (b) excluded
  entirely, (c) weighted by pre-2022 concession rate. Report the
  SHD-vs-LRD loss-rate comparison under each treatment.
- **Acceptance**: the paper discusses 2024 as "a year the Board changed
  its defensive posture, and any loss-rate comparison including 2024
  carries a structural-bias warning." The 2/2 = 100% LRD state-loss
  figure is removed from any headline quotation.

### R11 — OPR Bulletin 10 & 11 structured extraction (supplements R8)

- **Inputs**: `data/raw/opr_bulletin_10.pdf`, `opr_bulletin_11.pdf`
  (already available).
- **Output**: a case-level CSV of every LRD-era JR discussed in these
  bulletins, with columns {case_name, neutral_citation, decision_year,
  permission_date_known, permission_regime (SHD/LRD/unclear), LA or ABP
  challenge target, outcome}. Validate by a new test in `tests/` with
  hand-verified labels for at least 10 cases.
- **Acceptance**: the LRD-era-decided-JR count is no longer "~2" drawn
  from ABP Table 3; it is a transparently audited list from the two
  bulletin sources, which the paper treats as the canonical LRD-side
  analogue of the OPR Appendix-2 SHD list.

### R12 — Abstract / §4.1 / §5 rewrite for claims-to-evidence match

- **Output**: rewrite the headline line, §4.1, and the entire §5 Phase B
  to state:
  - "The per-decision JR-rate comparison cannot be honestly made from
    current data because denominators differ by regime and by window
    length." (headline)
  - Or, if R1 succeeds in aligning denominators, the resulting aligned
    comparison with matched CI.
  - Phase B projection re-cast as a "monitoring framework" rather than a
    "forecast", with explicit year-range bands from R6.
- **Acceptance**: the paper never says "LRD rate is not lower than SHD
  rate" without the qualifier "on our aligned but still small-N
  denominator". The Abstract's first sentence does not contain a
  statistical claim that the paper's own §6 partially refutes.

## Summary of what is good

- The limitations in §6 are frank and correctly identify the SHD-carryover
  and concurrent-trend issues. They are just not propagated up into §4 or
  the Abstract.
- The KEEP/REVERT discipline in `results.tsv` is used seriously;
  REVERT labels on E05/E07/E12/E15/E19 correctly flag where PDFs do not
  support the intended experiment.
- The literature review names the right statistical tools (Firth, Bayesian
  shrinkage, Poisson-with-offset, Goodman-Bacon DID decomposition) even if
  it doesn't implement them.
- The predecessor-project linkage (SHD 14/16 = 87.5% from ie_shd_judicial_review
  E01-R1) is correctly reproduced.
- No synthetic data is used; every numeric claim traces to ABP PDFs or the
  OPR Appendix-2.

## Decision summary

**Major revisions.** R1-R12 all required. The paper must not be posted to
the website summary until at minimum R1, R3, R4, R6, R8, and R12 are
complete. R2, R5, R7, R9, R10, R11 are required but can proceed in a
second revision if R1+R3+R4+R6+R8+R12 are closed first.

Until those are done, the honest one-sentence finding is:

> "The current ABP and OPR data cannot support a per-permission JR-rate
> comparison between SHD and LRD: SHD-era decided JRs have a well-defined
> denominator in ABP 2018-2021 decisions, but LRD-era decided JRs against
> LRD-era permissions number 2 by end-2024, which is below any
> defensible inference threshold. A comparative claim is premature until
> ≥2027."

That is the finding the data supports. The draft's "SHD 6.4% vs LRD 8.6%"
headline is not.
