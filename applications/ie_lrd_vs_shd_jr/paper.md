# LRD vs SHD judicial review intensity — did the 2021 reform reduce exposure?

**Project**: Ireland, 2017-2024
**Status**: Phase 3 FINAL (post Phase 2.75 blind review)
**One-sentence finding**: The per-permission LRD judicial-review (JR) rate cannot yet be cleanly estimated from public data; the substantive-LRD-outcome sample to end-2024 is n=2 cases, the available signal is consistent with no meaningful reduction, and a clean test requires ≥2027 and Department of Housing (DHLGH) local-authority-level LRD decision counts that are not yet published.

## Abstract

The Strategic Housing Development (SHD) regime (2017-2021) was succeeded by the Large-scale Residential Development (LRD) regime in December 2021. The question of whether LRD reduced judicial-review (JR) exposure against large housing schemes is central to the policy debate. This paper attempts the comparison using An Bord Pleanála (ABP) annual reports 2020-2024 and the Office of the Planning Regulator (OPR) Appendix-2 decided-JR schedule.

The answer is that the comparison **cannot yet be defensibly made**. The SHD-era decided-JR count is 16 in 2018-2021 against an aligned denominator of 392 SHD decisions (4.08%, Wilson 95% CI 2.53-6.53%). The LRD-era decided-JR count to end-2024 is **2 cases** (both conceded by the Board, ABP 2024 Table 3). The per-permission LRD denominator is unobtainable from ABP data alone — it requires DHLGH local-authority first-instance LRD decisions which are not in any publicly available PDF in our data layer. The per-appeal-concluded LRD JR rate (10/116 = 8.62%, Wilson 95% CI 4.75-15.14%) is on a **categorically different denominator** to the per-decision SHD rate; stitching them together flatters neither regime defensibly.

Concurrent with LRD's 2022 onset, three further interventions landed: the Heather Hill Supreme Court judgment (Aarhus costs, July 2022), the High Court Planning and Environment List (November 2022), and the 2024 concession spike (53 concessions vs 15 losses in ABP 2024, system-wide, not regime-specific). System-wide JR intake grew 58% from 2023 to 2024 (93→147); Commercial-type JR intake grew 150% (14→35); Infrastructure grew 850% (2→19). The LRD growth (3→7, 133%) is indistinguishable from this system-wide pattern and cannot, at annual resolution, be isolated as a regime effect.

The defensible finding is that the reform's LRD-specific JR effect is below the detection floor of currently-available data. A clean test requires approximately 2027, when the LRD permission cohort 2022-2024 will have fully passed the JR-lodgement and JR-decision windows, plus DHLGH LA-level LRD permission counts for the per-permission denominator.

## 1. Introduction

The SHD regime (Planning and Development (Housing) and Residential Tenancies Act 2016, as amended in 2018) required that applications for ≥100 housing units, ≥200 student bed-spaces, or ≥200 shared-accommodation bed-spaces be made directly to ABP, bypassing local-authority first-instance determination. It became widely characterised as a "JR magnet": the OPR Appendix-2 schedule records 16 SHD JRs as substantively decided over 2018-2021 with 14 state losses (14/16 Clopper-Pearson 95% CI 61.7-98.5%). Press tracking by end-2021 indicated approximately 35 SHD permissions had been judicially reviewed.

The LRD regime (Planning and Development (Large-scale Residential Development) Act 2021) replaced SHD in December 2021 with a two-stage process: local-authority first-instance decision, then ABP appeal under section 127 of the Planning and Development Act 2000.

This paper asks whether LRD actually reduced JR intensity on large housing schemes. It does not attempt the broader question of whether total planning-law friction fell.

## 2. Data

Two primary real-data sources.

**OPR Appendix-2 (October 2022)**: a case-level schedule of 144 decided planning JRs 2012-2022. Parsed by `parser_v2.py` and validated by a 12-test suite in `tests/test_jr_parser.py`. The SHD subset is 22 cases; 16 decided in the clean 2018-2021 window.

**An Bord Pleanála Annual Reports 2020-2024**: fetched from pleanala.ie as PDFs, converted to text with pdftotext, and harvested for numeric facts cited to line-numbers in `phase_2_75_revisions.py:JR_TOTAL_OUTCOMES` / `SHD_DECISIONS` / `LRD_CONCLUDED` / `JR_BY_TYPE_2023` / `JR_BY_TYPE_2024` / `COMPLETED_2023` / `COMPLETED_2024`.

**OPR Learning-from-Litigation Bulletins 10 (Dec 2025) and 11 (Mar 2026)**: structured-extracted in `discoveries/opr_bulletin_cases.csv` (R11). Together they cover 8 High Court cases with permission-regime labels. Zero of the 8 are LRD-era permissions.

No synthetic data is used. Where a quantity is unobtainable from the PDFs, the relevant `results.tsv` row is marked `UNANSWERABLE` or `REVERT`.

## 3. Methodology

### 3.1 Phase 0 literature review

210 verified citations in `papers.csv` (Hogan & Morgan, de Blacam, Simons, Galligan, Friends of the Irish Environment line of cases, Heather Hill, Eco Advocacy, UK NSIP evaluation, Dutch Crisis-en-Herstelwet comparative work, and small-n statistics texts on Firth penalisation, weak-informative Bayesian priors for rare-event logistic, and Goodman-Bacon DID diagnostics). The review explicitly identifies Firth-penalised logistic and weak-informative Bayesian logistic as the appropriate tools for rare-event small-N JR-rate estimation; R7 operationalises both.

### 3.2 Phase 1 model tournament

Five model families on the combined SHD+LRD decided-case panel (N=24 cases: 22 SHD + 2 LRD from ABP 2024 Table 3). T01 climatology proportion (AIC=26.56) narrowly beat T03 ITS (27.47) and T02 logistic-regime (27.58). **This is a precision diagnostic, not a regime-effect finding**: at N=24 case-level observations (with 2 of those 24 being LRD) no tournament can adjudicate a between-regime effect. The vanilla logistic (T02) produced `b1=-16.166` — numerically divergent — which is exactly the pathology Firth penalisation is designed to fix (R7).

### 3.3 Phase 2 experiments (26 rows)

E00, E00b, E01-E23, P01-P08 in `results.tsv`. Phase 2.5 adds P01-P08 pairwise-interaction descriptors.

### 3.4 Phase 2.75 blind-review revisions (R1-R12, 28 new rows)

The Phase 2.75 blind reviewer ruled major revisions on the Phase 3 draft. R1-R12 in `phase_2_75_revisions.py` execute the mandated repairs. Rows with status `UNANSWERABLE` flag claims withdrawn because data is unavailable; rows with status `wide_CI` flag percentages that are qualitative only.

## 4. Results

### 4.1 Headline — what we can say

There are **three** honest ways to phrase the SHD-vs-LRD comparison, and none of them is the draft's "6.4% vs 8.6%, p=0.51":

**Per-permission, SHD only (aligned, R1a)**. SHD decisions 2018-2021 = 60 + 82 + 137 + 113 = 392 (the 2018 figure has low confidence, from the ABP 2020 narrative). SHD decided JRs 2018-2021 = 16. **Rate = 4.08% [Wilson 95% CI 2.53-6.53%]**. This supersedes the draft's 16/250 = 6.4% which used only the 2020-2021 window (numerator-denominator window mismatch).

**Per-permission, LRD (R1b)**. **UNANSWERABLE.** The ABP-appeal denominator (116 LRD appeals concluded 2022-2024) is not the universe of LRD permissions; it is the subset of LA LRD decisions that were appealed to the Board. The per-permission denominator requires DHLGH LA-level LRD decision counts, which are not published in any PDF available to us. The per-decision LRD JR rate is therefore not comparable to the SHD per-decision rate on matching definitions.

**Decided-JR count, LRD (R8b)**. ABP 2024 Table 3 shows 2 LRD substantive outcomes (both conceded); ABP 2023 Table 3 has no LRD row. **The honest LRD numerator at end-2024 is 2**, not 10. The "10" is LRD-tagged JRs *received* but not decided. The 10 cannot be mapped to permission-year cohorts from within this project's data — OPR Bulletins 10 and 11 cover 8 High Court cases and zero of them is LRD-era (R11).

**What survived from the draft headline**: nothing as a comparative claim. The draft's "SHD 6.4% vs LRD 8.6%, Fisher p=0.51" is **withdrawn**.

### 4.2 State-loss rate

- **SHD 2018-2021**: 14/16 = 87.5% (Clopper-Pearson 95% CI [61.7%, 98.5%]). Matches predecessor project `ie_shd_judicial_review/E01-R1`.
- **LRD 2024 substantive**: 2/2 conceded. The "100% LRD state-loss rate" figure is **withdrawn** (R10c). Under a concession-sensitivity treatment (exclude concessions → 0/0 undefined; re-weight to pre-2022 baseline concession share of 33.3% → undefined). In 2024 the Board adopted a cautious defensive posture (ABP 2024 §Legal, line 1781): 53 concessions vs 15 losses system-wide is a structural shift, not a regime-specific signal.

### 4.3 Firth-penalised and Bayesian logistic (R7)

The vanilla logistic T02 diverged (`b1=-16.166`). Firth-adjusted 2×2 (add 0.5 per cell): SHD rate 15/18 = 83.3%, LRD rate 3/4 = 75.0%; odds-ratio CI spans 1 widely. Bayesian weak-prior posterior difference: E[SHD-LRD state-loss rate difference] = 0.083, 95% credible interval straddles zero. **Result**: with N=2 LRD observations, even penalisation/shrinkage methods cannot detect a regime difference in state-loss rate.

### 4.4 Interrupted time-series with concurrent-trend knots (R3)

Annual total-system JR lodged 2017-2024: 60, 41, 35, 83, 95, 95, 93, 147. Three-knot ITS (knots at 2022=LRD onset, 2023=Heather Hill + List commencement taking effect, 2024=concession spike) is point-identified but standard errors are not meaningfully reportable at N=8 annual observations with 5 parameters. The **single-knot (2022) coefficient cannot be separated from the Heather Hill / List coefficient** at annual resolution (C3 upheld).

**Commercial placebo (R3c, R9)**: Commercial JR intake 2023→2024 grew 150% (14→35). Commercial is unaffected by SHD→LRD but affected by list commencement, Heather Hill, and PDA 2024 signalling. Infrastructure grew 850% (2→19). **Total-system JR intake grew 58%**. LRD's 133% growth (3→7) sits comfortably inside the system-wide envelope.

### 4.5 Lodged-basis comparison (R2)

On a lodged-JR-per-permission basis: SHD 35/392 = 8.93% [Wilson 95% CI 6.5-12.1%] vs LRD 10/116 = 8.62% [4.8-15.1%]. Fisher exact p=1.00. This is **not** evidence that the two regimes are equal — it is the result of the LRD denominator being the appealed-subset of LRD permissions rather than the population.

### 4.6 Phase B projection — recast as monitoring framework (R6)

The Wilson CI on LRD_RATE_2024 = 7/79 is [4.36%, 17.18%]. A 50%-reduction target under baseline uncertainty spans [2.18%, 8.59%] — a 6.4pp band. Under this propagation, the central and pessimistic projection scenarios overlap throughout 2025-2030. The Phase B projection **does not support point-estimate claims like "2028 hit year"**. It is therefore re-cast as a monitoring framework: the 2025, 2026, and 2027 ABP annual reports will successively narrow the LRD baseline CI to an informative width, at which point (and only at which point) a target-year statement is defensible.

### 4.7 KEEP / REVERT / UNANSWERABLE summary

- **KEEP** (21 experiments from Phase 2 + 20 of 28 Phase 2.75 R-rows): E01-E04, E06, E08-E11, E13, E14, E16-E18, E20-E23, P01-P08; R1a, R2a-c, R3a-d, R4b, R5b, R6a-b, R7a-b, R8b, R9a-c, R10a-b, R11a, R12.
- **REVERT** (5 Phase-2 + 2 Phase-2.75): E05, E07, E12, E15, E19; R6c (Phase B projection not informative), R10c (2/2=100% withdrawn).
- **UNANSWERABLE** (3 new): R1b (LRD per-permission requires DHLGH data), R5a (per-unit JR rate requires DHLGH data), R8a (10 LRD-tagged JRs not mappable to permission year).
- **wide_CI** (1 new): R4a lists nine percentages whose 95% CI spans >30pp; these appear in the paper only qualitatively.

## 5. Phase B — LRD monitoring framework (not projection)

Per R6, point-estimate forecasting from the LRD 7/79 baseline is not defensible: the baseline CI is [4.36%, 17.18%] and propagating that through any scenario yields overlapping trajectories for "pessimistic" and "central" PDA 2024 treatments. The Phase B deliverable is therefore re-scoped to a **three-trigger monitoring framework**:

1. **Trigger A (2025 ABP report)**: if LRD JRs initiated 2025 ≥ 15 against an LRD-appeals-concluded base ≥ 100, the LRD rate CI narrows to approximately ±6pp. Only then does a within-LRD trend statement become possible.
2. **Trigger B (DHLGH data release)**: publication of LA-level LRD permission counts 2022-2024 enables per-permission denominator alignment (R1b currently UNANSWERABLE becomes KEEP).
3. **Trigger C (2027 ABP report)**: LRD permission cohort 2022-2024 has passed the typical JR-lodgement-to-decision lag (~2 years per ABP 2023 Table 4). Substantive-outcome count should exceed 20, enabling Firth/Bayesian logistic with meaningful posterior intervals.

`discoveries/lrd_successor_regime_projection.csv` (24 rows + 3 summary rows) remains as a sketch; its "year 2028" column is flagged NON-INFORMATIVE by R6c and must not be quoted as a forecast.

## 6. Discussion

The draft's headline — "LRD rate is not lower than SHD rate" — was in a specific sense correct (the two point estimates do not differ at p<0.05 under a Fisher exact test on the stitched 2×2) but the stitching is invalid. The SHD numerator is decided-JRs-against-direct-applications; the LRD numerator is lodged-JRs-against-appealed-applications. These are not comparable populations. The honest statement is the weaker one: **on the one denominator where both regimes are measured on matching definitions (lodged-JR per permission-reaching-ABP), the rates are within ~1pp of each other, but that denominator understates LRD because it excludes LA-first-instance LRD permissions that were never appealed to the Board**.

Three concurrent interventions confound any regime-specific reading:

- **Heather Hill [2022] IESC 43** (July 2022) extended Aarhus Convention cost-protection to a broader class of environmental judicial review, mechanically lowering the cost barrier to lodgement.
- The **Planning and Environment List** (High Court, commencement November 2022) sped up hearings, which in the medium term increased the rate at which latent cases resolved to substantive outcomes in any given year.
- The 2024 **concession spike** (53 concessions vs 15 losses, ABP 2024 Table 3) reflects a Board-internal shift to cautious defence in the face of recent adverse judgments and costs exposure, not a change in underlying case strength.

Each of these has the same sign as the hypothesised LRD effect (lower loss rate, shorter lag, more concessions on weaker cases). At annual resolution and with 2 substantive LRD outcomes, **none of them can be separated from a putative regime effect**.

The composition dimension — whether LRD's two-stage process re-routes JR exposure from ABP to local authorities — is a plausible substantive effect but is outside the measurement frame of ABP annual reports. DHLGH LA-level data would address it.

## 7. Caveats

Every risk the blind reviewer raised (C1-C11) is named here explicitly.

- **C1 (denominator mismatch)**: The draft's "6.4% vs 8.6%" stitched incompatible populations. Withdrawn; replaced with the R1a aligned SHD figure (4.08%) and R1b UNANSWERABLE for LRD.
- **C2 (tournament)**: T01 climatology winning is a precision diagnostic (N=24, 2 LRD), not a null-effect finding. This paper says so in §3.2.
- **C3 (concurrent trends)**: Heather Hill, List commencement, and the 2024 concession spike each pull in the same direction as the LRD hypothesis. R3 ITS cannot separate them at N=8 annual observations.
- **C4 (per-permission denominator)**: The substantively correct denominator requires DHLGH LA-level data. Per-permission and per-unit comparisons are explicitly WITHDRAWN pending that data release (R1b, R5a).
- **C5 (Phase B circular)**: The baseline rate CI is ±14pp; scenarios overlap. Phase B is recast as a monitoring framework, not a forecast (R6).
- **C6 (SHD-carryover)**: Not implementable as a per-permission cohort split for LRD until DHLGH data is available. SHD side is restricted to 2018-2021 permissions in R1a.
- **C7 (appeals concluded vs permissions granted)**: Made explicit in every rate quoted; readers are directed to R1b UNANSWERABLE for the LRD population-mismatch issue.
- **C8 (concession spike)**: R10c removes "2/2 = 100% LRD state-loss" from every headline. 2024 is tagged as a year of Board defensive-posture change.
- **C9 (bootstrap CI)**: R4a and R4b attach Wilson / Clopper-Pearson CIs to every percentage. Nine percentages are flagged wide-CI (qualitative only).
- **C10 (Firth / Bayesian)**: R7 operationalises both. Neither produces a significant LRD-vs-SHD loss-rate difference at N=2 LRD.
- **C11 (E14 typo)**: Retained for transparency in `results.tsv`; the homogeneous-definition carryover figure (2022 shd_decisions=80 + 2023=56 + 2024=44 = 180 post-LRD SHD decisions) is used in §4.2 discussion.

Further limitations:
- The 2018 SHD decisions figure (60) is harvested from ABP 2020 narrative ("up from 82 in 2019") and is a low-confidence proxy; rate estimates are mildly sensitive to it (swapping 60 for 80 moves the R1a rate from 4.08% to 3.88%).
- OPR Appendix-2 ends October 2022; subsequent decided cases rely on OPR Bulletins 10 and 11, which are narrative (not tabular) and do not cover LRD permissions as of March 2026.
- The Planning and Development Act 2024 is signed but not fully commenced; any claim about PDA 2024 effect is extrapolation.

## 8. Reproduction

```
cd /home/col/generalized_hdr_autoresearch/applications/ie_lrd_vs_shd_jr
python -m pytest tests/test_jr_parser.py -v       # 12 tests
python analysis.py                                  # Phase 0.5 + Phase 1 + Phase 2 rows
python phase_2_75_revisions.py                      # R1-R12 appended to results.tsv
python phase_b_discovery.py                         # Phase B monitoring-framework CSV
```

Outputs: `results.tsv` (54 rows: E00-E23 + T01-T05 + TC + P01-P08 + R1-R12), `tournament_results.csv` (5 rows), `discoveries/lrd_successor_regime_projection.csv` (27 rows), `discoveries/opr_bulletin_cases.csv` (8 rows).

## 9. Change log — how each R mandate was discharged

| R     | Mandate                                           | Paper impact                                                                 |
|-------|---------------------------------------------------|------------------------------------------------------------------------------|
| R1    | Permission-year cohort alignment                  | SHD rate revised 6.4%→4.08%; LRD per-permission WITHDRAWN (UNANSWERABLE).    |
| R2    | Lodged-JR denominator alternative                 | Lodged-basis comparison reported alongside (§4.5); no preferred answer.      |
| R3    | ITS with three knots + Commercial placebo         | ITS single-knot and three-knot fitted; placebos show system-wide trend.     |
| R4    | Bootstrap / Clopper-Pearson CI on every %         | Wilson/CP CIs attached; nine percentages flagged wide-CI qualitative-only.  |
| R5    | Per-permission-with-housing-size denominator      | UNANSWERABLE; withdrawn (requires DHLGH LA data).                           |
| R6    | Phase B baseline-CI propagation honesty check     | Phase B recast as monitoring framework; no "2028 hit" claim.                |
| R7    | Firth-penalised + Bayesian logistic               | Both fitted; neither distinguishes LRD from SHD state-loss rate at N=2.     |
| R8    | Disaggregate the 10 LRD-tagged JRs                | Unmappable from Bulletins 10/11; "10" remains mixed population.              |
| R9    | Commercial / Infrastructure placebo               | §4.4; system-wide JR growth dominates any regime-specific signal.           |
| R10   | 2024 concession-artefact sensitivity              | 2/2=100% LRD state-loss figure WITHDRAWN.                                    |
| R11   | OPR Bulletin 10 & 11 structured extraction        | `discoveries/opr_bulletin_cases.csv`; zero LRD-era cases in bulletins.      |
| R12   | Abstract/§4.1/§5 rewrite                          | Done; 6.4%-vs-8.6% claim withdrawn.                                         |

## 10. Conclusion

The per-permission LRD JR rate cannot yet be cleanly estimated. The available signal is consistent with no meaningful reduction relative to SHD, but is underpowered: substantive LRD outcomes to end-2024 total 2 cases (both conceded), concurrent interventions (Heather Hill, Planning and Environment List, 2024 concession spike) match the sign of any hypothesised LRD effect, and the per-permission denominator needed for a clean test is not in ABP data. A defensible comparative claim requires ≥2027 and DHLGH local-authority-level LRD permission data.
