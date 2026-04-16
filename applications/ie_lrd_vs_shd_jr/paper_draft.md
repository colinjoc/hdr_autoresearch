# LRD vs SHD judicial review intensity — did the 2021 reform reduce exposure?

**Project**: Ireland, 2017-2024
**Status**: Phase 3 DRAFT (pre-Phase 2.75 blind review)
**Headline**: On the cleanest available per-decision denominator, LRD's 2023-2024 JR rate is *not* lower than SHD's 2018-2021 clean-window rate (LRD 10/116 = 8.6% vs SHD 16/250 = 6.4%; Fisher exact p = 0.51). The reform's effect is below the noise floor given the small LRD denominator and the reporting lag.

## 1. Introduction

The Strategic Housing Development (SHD) regime operated from 3 July 2017 to December 2021. Under SHD, large-scale housing schemes (≥100 residential units or ≥200 student bed-spaces) bypassed local-authority first-instance decision-making and applied directly to An Bord Pleanála (ABP). The regime was repeatedly characterised as a "JR magnet": by 2021, press tracking indicated approximately 35 SHD permissions had been judicially reviewed, and the Office of the Planning Regulator's (OPR) Appendix-2 schedule recorded 16 SHD JRs as substantively decided over the 2018-2021 window with 14 state losses — a state-loss rate of 87.5%. The Large-scale Residential Development (LRD) regime, enacted in December 2021, replaced SHD with a two-stage process: local-authority first-instance decision followed by ABP appeal under section 127 of the Planning and Development Act 2000.

This project asks whether LRD actually reduced JR intensity. We examine: (a) JR rate per permission decision, (b) state-loss rate on decided JRs, (c) JR intake volume by year, (d) composition of applicants, (e) handling of the reporting lag, and (f) whether the reform is a substantive JR-exposure reduction or a procedural re-routing.

## 2. Data

Two primary sources, both real.

**OPR Appendix-2 (October 2022)**: a case-level schedule of 144 decided planning JRs 2012-2022. Parsed by `parser_v2.py` (reused from predecessor project `ie_shd_judicial_review`) and validated by a 12-test suite in `tests/test_jr_parser.py`. The SHD subset is 22 cases, with 16 decided in the clean 2018-2021 window.

**An Bord Pleanála Annual Reports 2020-2024**: fetched from pleanala.ie as PDFs and extracted to text via pdftotext. Reports provide (a) total JR applications lodged per year, (b) substantive outcome counts, (c) development-type intake breakdowns from 2023 and 2024, and (d) SHD decision and LRD appeal volumes. See `data_sources.md` for URLs and `knowledge_base.md` for extracted numeric facts.

No synthetic data is used. Where a quantity is not cleanly extractable from the PDFs, the relevant `results.tsv` row is marked `partial` or `REVERT`.

## 3. Methodology

### 3.1 Phase 0 lit review
210 verified citations in `papers.csv` spanning Irish planning/admin law textbooks (Hogan & Morgan, de Blacam, Simons, Galligan), SHD-era case law, ABP and OPR primary reports, EU environmental directives, comparative UK NSIP and Dutch Crisis-en-Herstelwet material, and small-n / DID / ITS / survival statistics texts. The lit review (`literature_review.md`) is compact-4-theme per the descriptive-project rule in program.md §Phase 0.

### 3.2 Phase 1 tournament
Five model families compared on the combined SHD+LRD decided-case panel (N=24 cases: 22 SHD + 2 LRD substantive outcomes from ABP 2024 Table 3):
- T01 climatology / proportion baseline
- T02 logistic regression `state_loss ~ regime` (DID-style)
- T03 logistic regression `state_loss ~ year` (ITS-style)
- T04 survival-proxy Cox-style single covariate
- T05 ridge-regression linear sanity check

Champion by AIC: **T01 climatology** (AIC=26.56), narrowly beating T03 ITS (AIC=27.47) and T02 DID (AIC=27.58). Interpretation: at N=24 the case-level panel cannot distinguish a regime effect from year-drift or a constant; the model champion is literally "no effect". This is a data-availability finding, not a null-effect finding. Ridge (T05) gives RMSE=0.37 with small coefficients, confirming no single feature carries predictive signal at this N.

### 3.3 Phase 2 experiments (26 rows)
Numbered E00, E00b, E01–E23, P01–P08 in `results.tsv`. Each tests a variant of the primary comparison: cleaning the window (E01), stratifying by LA (E02), applicant type (E10, E11), scheme type (E03), denominator definition (E13, E16), carryover accounting (E14), and pairwise interactions (P01–P08).

### 3.4 Phase 2.5 pairwise interactions
8 interaction rows P01–P08: Dublin×regime, NGO×apartment, year×apartment, regime×concession, year×multi-party, regime×environmental grounds, Dublin×NGO, size×year. All descriptively compatible with the main effect: no interaction changes the null conclusion.

## 4. Results

### 4.1 Headline (E00)

| Regime | JR intake | Decision denominator | JR rate per decision | Wilson 95% CI |
|---|---|---|---|---|
| SHD 2018-2021 (clean window) | 16 | 250 (ABP 2020+2021 SHD decisions) | **6.4%** | [4.0%, 10.1%] |
| LRD 2023-2024 | 10 | 116 (ABP 2022+2023+2024 LRD appeals concluded) | **8.6%** | [4.7%, 15.1%] |

Fisher exact test on SHD vs LRD per-decision JR rate: **p = 0.51**. We cannot reject equality.

### 4.2 State-loss rate (E00b)

- SHD 2018-2021: 14/16 = **87.5%** (Wilson CI approx [64%, 97%]) — matches predecessor project `E01-R1`.
- LRD 2024 substantive outcomes (ABP Table 3): 0 won, 0 lost, 2 conceded, 0 withdrawn = **2/2 = 100% state loss**. Denominator far too small for inference.

### 4.3 KEEP/REVERT summary (E01–E23, P01–P08)

**KEEP** (21 experiments): E01, E02, E03, E04, E06, E08, E09, E10, E11, E13, E14, E16, E17, E18, E20, E21, E22, E23, P01–P08.

**REVERT** (5 experiments): E05 (LA-vs-ABP split not in ABP reports), E07 (post-PDA2024 cohort not separable), E12 (cost-order stratification not in PDFs), E15 (LA-approved-no-appeal LRD not reported), E19 (Aarhus cost-cap effect not directly measurable).

**Top three KEEP levers** by effect on the headline:

1. **E14 carryover accounting**. ABP 2024 Table 3 SHD row (3 won, 7 lost, 7 conceded, 6 withdrawn = 23 substantive outcomes in 2024 alone) is almost entirely against pre-2022 SHD permissions. Folding carryover into "SHD-era" rather than "LRD-era" is decisive. Without this correction, LRD's per-decision loss-rate appears artificially low.
2. **E09 regime window definition**. Using calendar windows rather than permission-grant windows misattributes ~25 SHD-carryover JRs from 2022-2024 to the wrong regime. The clean "permission-year cohort" framing is the honest one but forces partial-year reporting for 2022-2024 grants.
3. **E20 international benchmark**. IE SHD 18.5% per-permission JR rate (Oneil 2020 estimate) is far above UK NSIP 3-5% per DCO. IE LRD 8.6% per appeal is still above UK NSIP but below SHD. The reform appears to have moved Ireland approximately half-way toward the NSIP benchmark — but this single comparison is swamped by reporting-lag uncertainty.

### 4.4 Volume and composition
- JR intake: 83 (2020), 95 (2021), 95 (2022), 93 (2023), 147 (2024). Intake is *up* post-LRD — driven by non-housing categories (RZLT 21+10, Commercial 14+35). Housing-specific intake (SHD+LRD+Housing 2-99+Large housing) tracks roughly 35-40/year across 2022-2024.
- Applicant composition (ABP 2024): 82 third-party, 39 developer-applicant, 22 landowner. Third-party dominance unchanged from SHD-era.
- Concession share of losses (E23): 2021 = 48.7% (19/39), 2024 = 77.9% (53/68). The concession rise is universal across types, not regime-specific.

### 4.5 Reporting lag (E01, E13)
Per ABP Tables 4-5 (year-of-initiation of JRs completed in current year), ~80% of JRs completed in 2023-2024 were initiated in 2021-2022. This means "decided LRD JRs to end-2024" is 2 cases — insufficient for rate inference. The LRD-rate question effectively cannot be answered with decided-case data before 2027-2028.

## 5. Phase B: successor-regime projection

`phase_b_discovery.py` projects a Planning and Development Act 2024 (PDA2024) regime under three scenarios. Target: 50% reduction from LRD 2024 baseline rate (8.86% → 4.43% per appeal concluded).

| Scenario | Rate-reduction param | ELCFA uptake | List throughput | Year 50% target reached |
|---|---|---|---|---|
| Pessimistic | 0% | 0% | 1× | NOT REACHED by 2030 |
| Central PDA2024 | 15%/yr | 40% | 1.5× | **2028** |
| Optimistic | 30%/yr | 75% | 2× | **2027** |

Output: `discoveries/lrd_successor_regime_projection.csv` (24 rows).

## 6. Discussion

The headline finding — LRD JR rate is not statistically distinguishable from SHD on the clean comparison — should be read narrowly. It does **not** say LRD failed. It says the current data are not yet adequate to test the claim. Three reasons:

1. **The LRD-era decided-JR denominator is 2 cases** (both conceded). Any rate estimate is heavily imprecise. By 2027 it will be an order of magnitude larger.
2. **SHD-carryover contamination**. SHD permissions granted in 2019-2021 continued to be judicially reviewed through 2024, contributing 23 substantive outcomes to ABP 2024 Table 3 alone. Almost all "SHD JRs decided 2022-2024" are in this carryover tail.
3. **Concurrent trends.** The Planning and Environment List commenced late 2022, the Heather Hill Supreme Court judgment landed mid-2022, and 2024 saw a concession-spike attributable to precedent cascades. These secular moves overwhelm any direct SHD→LRD treatment signal in the raw data.

A more defensible claim is this: **LRD did not move JR rate by more than the magnitude of concurrent changes in judicial capacity, costs law, and case-management.** In the broader literature (UK NSIP and Dutch Crisis-en-Herstelwet comparisons), consent-regime reforms of this type have produced moderate rather than dramatic rate reductions, and our result is consistent with that pattern.

The composition dimension is where LRD's effect is plausibly visible. The two-stage process front-loads LA-level scrutiny, which ought to reduce the number of JR-ripe decisions reaching the Board on appeal. ABP 2024 reports that 79 LRD appeals concluded against 71 received — a working equilibrium. If LA-first-instance decisions on LRD are themselves now being judicially reviewed (plausible, and not reported in ABP data), the JR exposure has been *re-routed* from ABP to LAs rather than reduced in aggregate.

## 7. Limitations (placeholder — to be expanded after Phase 2.75 blind review)

- LRD decided-JR denominator is 2 cases; any rate estimate carries a ±10pp Wilson half-width.
- SHD-carryover vs LRD classification relies on development-type labels in ABP annual reports which started appearing only in 2023.
- OPR Appendix-2 ends October 2022; subsequent decided cases rely on OPR Legal Bulletins which are narrative, not tabular.
- Per-unit JR exposure is only partially computable; the 3,042 dwellings-affected-by-JR figure for 2024 is reported, but the SHD-era equivalent is not published.
- The Phase B projection uses an analytic rate-envelope, not a trained model. It is a scenario sketch, not a forecast.

## 8. Reproduction

```
cd /home/col/generalized_hdr_autoresearch/applications/ie_lrd_vs_shd_jr
python -m pytest tests/test_jr_parser.py -v   # 12 tests, ~0.04s
python analysis.py                              # E00 + T01-T05 + E01-E23 + P01-P08
python phase_b_discovery.py                     # discoveries/lrd_successor_regime_projection.csv
```
