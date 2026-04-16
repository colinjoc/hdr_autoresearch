# The Judicial-Review Tax on Irish Housing Supply: Quantifying Decision-Time Costs in Housing-Unit-Months

## Abstract

Between 2018 and 2024, judicial review (JR) of planning decisions at An Bord Pleanala (ABP) imposed a measurable cost on Irish housing delivery, not in legal fees but in delayed housing units. This paper synthesises three predecessor studies -- the SHD JR outcome analysis (14/16 = 87.5% state-loss rate, 2018-2021), the LRD successor-regime comparison (honest null, n=2 decided), and the ABP decision-time analysis (mean weeks 18 to 42, SOP compliance 69% to 25%) -- to quantify the JR tax in housing-unit-months. The direct tax, computed from 22 Strategic Housing Development (SHD) JR cases affecting approximately 6,500 housing units, is 105,504 unit-months under the central imputation scenario, with a sensitivity range of [85,404, 150,204] reflecting the fact that 13 of the 22 cases have imputed (not stated) unit counts (R1, R7d). The indirect tax -- the additional delay imposed on all housing cases by JR-related institutional caution -- is bounded at [0, 9,305] unit-months under a [0%, 50%] channel-attribution framework; the 25% illustrative midpoint (4,652 unit-months) is an assumption, not an empirically identified estimate (R2). Under a counterfactual where ABP maintained 18-week statutory-objective-period (SOP) compliance throughout 2018-2024, an estimated 7,400-16,600 additional housing units would have been delivered to the market sooner, depending on whether a construction-capacity ceiling binds (R5); the uncapped 16,638 figure requires counterfactual completions of 38,700-40,500 units in 2023-2024, which may exceed construction-sector absorptive capacity. The holding cost of the direct delay is estimated at EUR 52.8 million (land-finance cost only at EUR 500/unit/month; sensitivity range EUR 52.8M-158.3M depending on cost base; R4). Five model families were evaluated; the counterfactual simulation (T05) was selected as champion for its policy relevance, with T01 accounting as the most robust (fewest assumptions).

## 1. Introduction

Ireland's housing crisis has been a defining policy challenge since 2015, with completions consistently falling short of estimated demand of 33,000-50,000 units per year [P010, P137]. The planning system has been identified as one of four binding constraints on supply [P004, P009], alongside zoning, infrastructure capacity, and construction labour.

The Strategic Housing Development (SHD) regime (2017-2021) was designed to accelerate large housing permissions by routing them directly to ABP, bypassing local authorities. Instead, the regime became a judicial-review magnet: 87.5% of SHD decisions that reached the High Court were quashed or conceded [PL-1]. ABP's legal costs doubled to EUR 8.2 million in a single year [P056, P057]. The regime was abolished at the end of 2021 and replaced by Large-scale Residential Development (LRD).

The direct cost of these judicial reviews -- the legal fees paid by ABP and developers -- is well-documented. What has not been quantified is the housing-unit cost: how many units were delayed, for how long, and what was the economic consequence of that delay? This paper provides that quantification by synthesising case-level JR data from the Office of the Planning Regulator (OPR) Appendix-2, aggregate ABP decision-time data from annual reports, and CSO housing completions data.

Three predecessor projects provide the evidentiary foundation:
- **PL-1** (ie_shd_judicial_review): established the 14/16 = 87.5% state-loss rate for SHD JRs 2018-2021, with a 27-test parser regression suite and hand-verified ground truth for all 22 SHD cases.
- **PL-2** (ie_lrd_vs_shd_jr): attempted the SHD-vs-LRD comparison and found an honest null -- only 2 substantive LRD JR outcomes by end-2024, below the detection floor for meaningful comparison.
- **PL-3** (ie_abp_decision_times): documented the ABP decision-time deterioration from 18 weeks (2017) to 42 weeks (2023-2024), with SOP compliance falling from 69% to 25%, and utilisation ratio rho peaking at 1.45 in 2022. Crucially, PL-3 caveat 11 states that the JR-feedback channel cannot be separated from the capacity-queueing channel at n=10 annual observations.

## 2. Detailed Baseline

The baseline is the set of 22 SHD JR cases from the OPR Appendix-2 (published October 2022), covering all SHD-related judicial reviews decided between 2018 and 2022. For the clean 2018-2021 window (fully closed years under the active SHD regime), there are 16 cases with 14 state losses (87.5%).

Each case is characterised by:
- **Unit count**: stated in the OPR body text for 9 of 22 cases (range: 197 to 741 units). For the remaining 13 cases, unit counts are imputed from the SHD regime minimum (100 units) or scheme-specific press reports. The 9 stated cases contribute 63,804 unit-months (60.5% of the central estimate); the 13 imputed cases contribute 41,700 (39.5%). This imputation is a material source of uncertainty (R1, R7e).
- **Delay**: measured as the interval from JR lodgement year (the Record-No year) to JR decision year (the neutral citation year), plus an estimated remittal/re-application period for quashed cases.
- **Outcome weight**: 1.0 for quashed or conceded (full delay realised), 0.5 for refused or dismissed (uncertainty delay), 0.25 for upheld on appeal (minimal delay).

The E00 baseline for the 2018-2021 window: 16 cases, 5,499 total units, 87.5% state-loss rate. The direct unit-month delay for the full 22-case set is 105,504 unit-months (central imputation).

The ABP decision-time baseline is the self-reported mean-weeks-to-dispose series from Annual Report Appendices 2018-2024 [PL-3 E00], with the pre-crisis 2017 value of 18 weeks as the counterfactual benchmark.

The CSO housing completions baseline is the NDQ07 series, showing completions rising from 18,072 (2018) to 34,177 (2024) with a plateau at approximately 20,500 in 2019-2021.

## 3. Detailed Solution

The JR tax on housing supply is decomposed into two channels:

**Channel 1 -- Direct delay.** For each SHD case that was judicially reviewed, the delay in housing-unit-months is:

    unit_months = units x delay_months x outcome_weight

where outcome_weight = 1.0 (quashed/conceded), 0.5 (refused/dismissed), or 0.25 (upheld). The total across 22 cases is 105,504 unit-months (central imputation; sensitivity range [85,404, 150,204] per R1/E11).

The five largest contributors are:
1. Dublin Cycling Campaign v ABP (case 104): 741 BTR apartments x 18 months = 13,338 unit-months
2. Highland Residents v ABP (case 107): 661 units x 18 months = 11,898 unit-months
3. Clonres v ABP No.2 (case 115): 657 dwellings x 18 months = 11,826 unit-months
4. Clonres CLG v ABP (case 63): 536 units x 12 months = 6,432 unit-months
5. Morris v ABP (case 101): 512 apartments x 12 months x 0.5 = 3,072 unit-months (refused -- ABP won)

All five have stated (not imputed) unit counts; the top five together account for 46,566 unit-months (44% of total).

**Channel 2 -- Indirect delay.** ABP decision times rose from 18 weeks to 42 weeks across all case types. The Oaxaca-Blinder decomposition [PL-3 R3] shows 100% of this is within-case-type productivity change, which is consistent with (but does not prove) JR-induced defensive behaviour rather than case-mix shift.

The indirect delay is:

    indirect_unit_months = sum_years(excess_weeks x (12/52) x housing_cases_per_year) x jr_share

where housing_cases_per_year is approximately 1,120 (40% of ABP's approximately 2,800 annual disposals), and jr_share is the attribution bound: 0% (lower) or 50% (upper).

The total ABP excess unit-months (before JR attribution) is 18,609. Under the channel framework:
- Lower (0% JR): 0 unit-months
- Illustrative midpoint (25% JR): 4,652 unit-months -- **this is an assumption, not an empirically estimated quantity** (R2)
- Upper (50% JR): 9,305 unit-months

The 25% midpoint has no regression, decomposition, or calibration to support it. PL-3 caveat 11 explicitly states that the JR-feedback and capacity-queueing channels cannot be separated at n=10 annual observations. The honest statement is that the indirect tax lies somewhere in [0, 9,305] unit-months with no basis for picking a point within that range.

**Counterfactual completions.** Under a scenario where ABP maintained 18-week SOP compliance throughout 2018-2024, the number of housing units that would have been delivered sooner is estimated as:

    shifted_units = completions_Y x (excess_weeks / 52) x housing_share

The uncapped cumulative gap is 16,638 units over 2018-2024. However, this estimate has three structural limitations (R3, R5):

1. **Construction-capacity ceiling**: The 2023-2024 counterfactual requires 38,731 and 40,486 completions respectively -- 15-20% above peak observed output. Under a 35,000-unit ceiling (roughly current peak capacity), the gap falls to 7,421 units. Under a moderate 38,000-unit ceiling, the gap is 13,421 units. The honest range is [7,421, 16,638] depending on capacity assumptions.

2. **Endogenous intake**: Faster ABP processing would likely induce more developer applications, partially offsetting the speed gain. Under a 10% intake-boost scenario the gap narrows to 15,806; under 20% boost it narrows to 14,973.

3. **Completions lag**: CSO completions are a 2-3 year lag from planning permissions. ABP processing time is one input among construction labour, materials, and finance availability.

## 4. Methods

### 4.1 Phase 0 literature review

205 verified citations in `papers.csv` covering: cost of delay in construction [P001-P020], judicial-review impact on administrative decision-making [P021-P040], Irish planning JR [P041-P060], ABP capacity [P061-P070], queueing theory [P091-P095], counterfactual estimation [P096-P110], and international comparisons [P111-P125].

### 4.2 Phase 1 tournament

Five model families evaluated on the same data:

| Family | Description | Metric | Value |
|--------|-------------|--------|-------|
| T01 Accounting | Direct unit-months (units x delay x weight) | unit-months | 105,504 |
| T02 RD proxy | SHD excess weeks over NPA (JR-exposure premium) | weeks | 83 |
| T03 Queueing | JR caseload as exogenous demand shock on rho | rho fraction | 0.165 |
| T04 DiD | Housing vs commercial ABP decision-time change | weeks | 19 |
| T05 Counterfactual | Completions gap under 18wk SOP scenario | units | 7,421-16,638 |

**Champion: T05 counterfactual simulation.** Selected for policy relevance: it incorporates both direct and indirect channels and produces the most actionable metric (housing units delivered sooner under a specific reform scenario). T01 is the most robust (fewest assumptions) but captures only the direct channel. T03 is mechanistically interesting but the JR case-multiplier (7x) is an assumption with no cited empirical source (R6).

### 4.3 Phase 2 experiments

40 experiments in `results.tsv`, plus 22 Phase 2.75 R-mandate rows (R1a-R7f), including: direct delay computation (E01-E02), indirect delay bounds (E03), counterfactual completions (E04, E15.*), geographic concentration (E05), outcome splits (E06-E07), cost estimation (E08-E09), scope and sensitivity (E10-E11), process analysis (E12-E13), annual decomposition (E14.*), size distribution (E16), headline bounds (E17), pairwise interactions (P01-P03), imputation sensitivity (R1a-c), indirect attribution basis (R2), endogenous intake (R3a-c), holding cost sensitivity (R4a-d), capacity ceiling (R5a-c), JR multiplier sensitivity (R6a-d), and reconciliation (R7a-f).

### 4.4 Phase 2.5 pairwise interactions

Three interaction experiments: Dublin x quashed (P01), large x quashed (P02), and year x large (P03). Dublin quashed cases dominate the direct delay; large quashed cases in 2020 account for the annual peak.

## 5. Results

### 5.1 Direct JR delay (E01, E02, R7c)

Total direct delay across all 22 SHD JR cases: **105,504 unit-months** (central imputation; sensitivity range [85,404, 150,204] per R1/E11). For the clean 2018-2021 window only: **88,422 unit-months** (16 cases; corrected from 93,708 per R7c). The 2022 partial-year cases add 17,082 unit-months.

### 5.2 Annual decomposition (E14.*, R7a, R7f)

| Year | Cases decided | Direct unit-months | Notes |
|------|--------------|-------------------|-------|
| 2018 | 1 | 6,432 | Clonres CLG (536 units, conceded) |
| 2019 | 2 | 5,346 | Heather Hill (197u), Southwood Park (100u) |
| 2020 | 10 | 58,818 | Peak year: Dublin Cycling (741u), Highland (661u), Morris (512u) |
| 2021 | 3 | 17,826 | Clonres No.2 (657u), Atlantic Diamond (300u), O'Riordan (100u) |
| 2022 | 6 | 17,082 | Partial year (OPR Appendix-2 published Oct 2022) |
| **Total** | **22** | **105,504** | Cross-checks with E01 (R7a) |

The 2020 spike (10 JRs decided, 58,818 unit-months, 56% of total) reflects the convergence of the 2018-2019 JR filings reaching hearing in 2020. This was the year the SHD regime's legal strategy became unsustainable.

### 5.3 Indirect delay bounds (E03, R2)

The indirect JR tax -- the additional delay imposed on all housing cases by JR-related institutional changes -- is bounded by a channel-attribution framework:

- **Lower (0% JR attribution)**: 0 unit-months. All ABP slowdown attributed to capacity crisis, IT transition, and board vacancies.
- **Illustrative midpoint (25% JR attribution)**: 4,652 unit-months. This is an assumption chosen to illustrate a plausible scenario, not an empirically derived estimate.
- **Upper (50% JR attribution)**: 9,305 unit-months. JR is the dominant driver of caution.

The total ABP excess (before attribution) is 18,609 housing-case unit-months over 2018-2024. The honest statement is that the indirect tax lies somewhere in [0, 9,305] unit-months. No data available to this project can identify where within that range the true value falls.

### 5.4 Total JR tax with bounds (E17)

| Bound | Direct | Indirect | Total unit-months |
|-------|--------|----------|-------------------|
| Lower (conservative) | 85,404 | 0 | 85,404 |
| Central (ad-hoc imputation, 0% indirect) | 105,504 | 0 | 105,504 |
| Upper (high imputation, 50% indirect) | 150,204 | 9,305 | 159,509 |

The range reflects both imputation uncertainty (R1) and indirect-channel uncertainty (R2). The tightest defensible claim is that the direct JR tax is between 85,000 and 150,000 unit-months.

### 5.5 Counterfactual completions gap (E04, E15.*, R3, R5)

Under an 18-week SOP counterfactual (no construction ceiling):

| Year | Observed | Counterfactual | Gap | Excess weeks |
|------|----------|----------------|-----|-------------|
| 2018 | 18,072 | 18,767 | 695 | 5 |
| 2019 | 21,241 | 21,894 | 653 | 4 |
| 2020 | 20,676 | 21,471 | 795 | 5 |
| 2021 | 20,433 | 20,747 | 314 | 2 |
| 2022 | 29,851 | 31,687 | 1,836 | 8 |
| 2023 | 32,695 | 38,731 | 6,036 | 24 |
| 2024 | 34,177 | 40,486 | 6,309 | 24 |
| **Total** | | | **16,638** | |

**Capacity-ceiling sensitivity (R5):**

| Ceiling | Gap |
|---------|-----|
| None (current) | 16,638 |
| 38,000 units/year | 13,421 |
| 35,000 units/year | 7,421 |

The gap accelerates sharply in 2023-2024 when ABP mean weeks hit 42 (24 weeks excess). The 2023-2024 gap alone (12,345 units uncapped) is the most ceiling-sensitive component. Under the 35,000-unit ceiling, the 2023-2024 gap shrinks from 12,345 to approximately 3,128 units because observed completions in those years (32,695 and 34,177) are already near the ceiling.

**Endogenous-intake sensitivity (R3):** Under a 10% intake boost, the gap narrows to 15,806 (-5%); under 20%, to 14,973 (-10%). The feedback effect is modest because the excess-week reduction from additional intake is partially offset by queue growth.

**The honest range for the counterfactual gap is [7,421, 16,638] units.** The 35K-ceiling scenario is the most materially different from the headline, reducing it by 55%. This counterfactual measures the total cost of ABP delay, not just the JR component; JR is one of several contributing channels.

### 5.6 Geographic concentration (E05, R7b)

Dublin accounts for 18 of 22 JR cases and 5,041 units (77% of total units directly affected). Meath (2 cases: Protect East Meath, Highland Residents) accounts for 1,111 units. Galway (2 cases: both Heather Hill) accounts for 394 units.

### 5.7 Holding cost (E08, R4)

At EUR 500/unit/month (land-finance cost only), the direct JR delay represents EUR 52.8 million in holding costs (R4a). The EUR 500 figure represents approximately the land-share (one-third) of the annual finance cost at 6% on a EUR 300,000 unit cost (6% of EUR 100,000 = EUR 6,000/year = EUR 500/month).

**Holding-cost sensitivity (R4):**

| Cost base | EUR per unit-month | Total holding cost |
|-----------|--------------------|--------------------|
| Land finance only | 500 | EUR 52.8M |
| Land + partial construction | 1,000 | EUR 105.5M |
| Full development finance | 1,500 | EUR 158.3M |

**Note on outcome weighting (R4d):** The holding cost above is computed on outcome-weighted unit-months (105,504). Developers pay finance costs during litigation regardless of JR outcome. The unweighted direct unit-months are 113,658, yielding EUR 56.8M at EUR 500/unit/month. The difference (EUR 4.1M) represents the cost borne by developers in cases where the JR was refused/dismissed or upheld.

### 5.8 Sensitivity to imputed unit counts (E11, R1, R7d, R7e)

Thirteen of 22 cases have imputed unit counts. The 9 stated cases contribute a fixed 63,804 unit-months (R7e); the 13 imputed cases contribute 41,700 under the current ad-hoc imputation.

**Three-scenario imputation (R1):**

| Scenario | Imputed value | Direct unit-months | Imputed share |
|----------|---------------|-------------------|---------------|
| Floor (R1a) | 100 (SHD minimum) | 85,404 | 25.3% |
| Current ad-hoc (R1c) | 100-400 (case-specific) | 105,504 | 39.5% |
| Median of stated (R1b) | 512 | 174,396 | 63.4% |

The floor and current scenarios span [-19%, 0%] relative to the central estimate. The median-of-stated scenario (+65%) is likely an overestimate because many imputed cases are smaller schemes (SHD minimum = 100 units). The defensible range is [85,404, 150,204] (floor to high=400), which spans -19% to +42% of the central estimate.

### 5.9 Queueing decomposition (E13, T03, R6)

JR defense work at ABP is estimated at 350 case-equivalents per year (50 JRs x 7x case multiplier), representing 16.5% of ABP's 2022 disposal capacity (2,115 cases). The 7x multiplier is an assumption -- no published source quantifies the ABP staff time per JR defense relative to a normal case disposal.

**JR-multiplier sensitivity (R6):**

| Multiplier | JR case-equiv | rho_jr component |
|------------|---------------|-----------------|
| 3x | 150 | 0.071 (7.1%) |
| 5x | 250 | 0.118 (11.8%) |
| 7x (current) | 350 | 0.165 (16.5%) |
| 10x | 500 | 0.236 (23.6%) |

The rho decomposition is an accounting exercise, not a causal identification. It is not inconsistent with a non-zero JR share of ABP slowdown, but it does not identify the JR channel specifically (PL-3 caveat 11). The rho decomposition must not be cited as evidence for any particular indirect-channel attribution percentage.

## 6. Discussion

### 6.1 The direct tax is large and concentrated

105,504 unit-months of direct JR delay (sensitivity [85,404, 150,204]) is equivalent to approximately 7,100-12,500 units delayed for one year. It is concentrated in a single year (2020: 58,818 unit-months, 56% of total) and a single city (Dublin: 18 of 22 cases, 77% of units). The five largest cases alone account for 46,566 unit-months (44% of total), and all five have stated (not imputed) unit counts, so the concentration is robust to imputation assumptions.

### 6.2 The indirect tax is real but not point-identified

The evidence supporting a non-zero indirect tax is:
- ABP decision times rose for all case types, not just housing, consistent with the radiating effect [P021].
- The Oaxaca-Blinder decomposition [PL-3 R3] attributes 100% of the rise to within-case-type productivity change, consistent with JR-induced defensive behaviour rather than case-mix shift.
- The post-Connelly/Balz reason-giving expansion [P043] is itself a JR-induced institutional change.
- NPA cases (0.3% JR rate) slowed from 19 to 48 weeks, suggesting the mechanism operates system-wide.

The evidence against a high JR attribution is:
- The board-member crisis (5 of 15 seats filled in 2022) is a sufficient explanation for the 2022-2023 surge [PL-3].
- The Plean-IT transition (2018) predates the JR peak.
- FTE shortages and case-complexity growth are confounding channels.

The honest statement is that the indirect tax lies somewhere in [0, 9,305] unit-months. No regression, decomposition, or natural experiment in the available data identifies the JR share of ABP decision-time growth. The 25% midpoint is illustrative only.

### 6.3 The counterfactual measures ABP delay cost, not JR cost

The 7,421-16,638 unit completions gap under the 18-week SOP counterfactual measures the total cost of ABP delay, not just the JR component. It is the answer to the question: "if Ireland had maintained a well-functioning planning-appellate body, how much more housing would have been delivered sooner?" The JR tax is a contributor to that gap but not the sole cause. The board-capacity crisis, IT transition, and case-complexity growth are concurrent factors. The JR contribution is bounded at 0-50% of the indirect channel, which is itself a small fraction of the total counterfactual gap.

The 35,000-unit capacity ceiling (R5b) is the single most important sensitivity: it reduces the headline from 16,638 to 7,421. Whether Ireland's construction sector could have absorbed an additional 6,000-12,000 units per year in 2023-2024 is an open question; labour-market data [P010, P011] suggests the sector was already near capacity.

### 6.4 Three levers for reducing the JR tax

1. **Reduce JR filing rates**: reform the one-way costs rule [P043] that makes JR filing near-free for environmental NGOs. This is the highest-leverage reform because it addresses both direct and indirect channels. The PDA 2024 attempts this through restricted grounds and Environmental Legal Costs Financial Assistance.

2. **Reduce the consequence of JR loss**: faster JR resolution (the Planning and Environment List, established November 2022, targets 12-18 months vs the previous 18-36 months), automatic remittal procedures, and a "defect notice" process that allows ABP to correct minor reasoning failures without full re-hearing.

3. **Increase ABP capacity**: the 2023-2024 FTE surge (202 to 290) is already reducing backlog, with 2025 Q1-Q3 compliance recovering to 37%-77% [PL-3 E21]. Maintaining this capacity prevents future rho > 1 episodes.

## 7. Caveats and Limitations

1. **Unit-count imputation**: 13 of 22 cases have imputed unit counts. The 9 stated cases contribute 63,804 unit-months (61% of central); the 13 imputed contribute 41,700 (39%). Sensitivity range: [85,404, 150,204] unit-months (R1, E11). The ad-hoc imputation has no systematic rule; floor-to-high range spans -19% to +42% of central.
2. **Delay measurement**: lodgement-to-decision year is a lower bound; actual scheme delay includes remittal time (12-24 additional months for quashed cases).
3. **Indirect channel not identified**: the 25% illustrative midpoint is an assumption, not an empirically estimated quantity. PL-3 caveat 11 states the JR-feedback and capacity-queueing channels cannot be separated at n=10 annual observations.
4. **Counterfactual assumes exogenous intake**: if ABP processing time affects developer filing behaviour, the 18-week counterfactual may overstate throughput. Under 10-20% endogenous intake, the gap narrows by 5-10% (R3).
5. **Construction-capacity ceiling**: the uncapped counterfactual requires 38,700-40,500 completions in 2023-2024, which may exceed sector capacity. Under a 35,000-unit ceiling the gap halves from 16,638 to 7,421 (R5).
6. **2022 partial year**: OPR Appendix-2 was published October 2022; 2022 data is incomplete.
7. **LRD-era excluded**: only 2 substantive LRD JR outcomes by end-2024; LRD JR tax is below detection floor [PL-2].
8. **Holding cost derivation**: EUR 500/unit/month is land-share (one-third) of 6% annual finance cost on EUR 300K; full development-cost finance would be EUR 1,500/unit/month, tripling the figure. Outcome weighting is applied to unit-months but developers pay finance cost regardless of JR outcome (R4d).
9. **No case-level data**: ABP does not publish per-case decision dates in its annual reports; all timing analysis uses year-level aggregates.
10. **Completions are not permissions**: the counterfactual measures completions shifted forward in time, not permissions. The permission-to-completion lag (2-3 years) adds further timing uncertainty.
11. **SHD carryover**: ABP continued deciding SHD cases (80 in 2022, 56 in 2023, 44 in 2024) after the regime ended. The JR tax from these carryover cases is only partially captured in the 22-case OPR list.
12. **7x JR case multiplier is an assumption**: no published source quantifies ABP staff time per JR defense relative to normal case disposal. Sensitivity at 3x-10x yields rho_jr of 0.071-0.236 (R6).
13. **Rho is an accounting identity, not a causal explanation**: the queueing decomposition (T03, section 5.9) describes how JR defense work relates to total throughput but does not identify JR as a causal driver of the slowdown (inherited from PL-3).

## 8. Conclusion

The judicial-review tax on Irish housing supply is quantifiable and large, but the precision of the estimate is lower than the headline numbers suggest. The direct tax -- 105,504 unit-months under the central imputation (range [85,404, 150,204]) from 22 SHD JR cases -- represents the equivalent of approximately 7,100-12,500 housing units delayed for a full year. This is the paper's most defensible finding because it rests on observed case data with imputation as the main source of uncertainty.

The indirect tax -- bounded at [0, 9,305] unit-months -- captures the radiating effect of JR-induced institutional caution on all planning decisions, but cannot be precisely estimated from available aggregate data. The 25% illustrative midpoint is an assumption. The distinction between "JR caused this delay" and "ABP was slow and JR was one of several concurrent factors" applies to every indirect-channel claim.

The counterfactual completions gap (7,421-16,638 units under a range of capacity-ceiling assumptions) measures the full cost of ABP delay, of which JR is one of several contributing channels. The uncapped headline of 16,638 requires counterfactual completions above Ireland's observed peak capacity and should be quoted with the caveat that construction-sector constraints bind independently of ABP processing time.

The holding cost of direct delay is EUR 52.8-158.3 million depending on cost base (R4). The policy implication is that JR reform must address both the direct channel (costs-rule reform, faster resolution, defect-notice procedures) and the capacity channel (sustained FTE investment, board-member stability). The largest single lever is the 2023-2024 completions gap, which is primarily driven by the board-capacity crisis rather than JR specifically.

## 9. Change Log

| R# | Mandate | Finding | Paper impact |
|----|---------|---------|-------------|
| R1 | Three-scenario imputation sensitivity | Floor=85,404, ad-hoc=105,504, median-of-stated=174,396 | Abstract quotes range [85,404, 150,204]; section 5.8 reports all three scenarios with imputed-share percentages |
| R2 | Indirect channel 25% labelled as assumption | No empirical basis for 25%; PL-3 caveat 11 confirmed | 25% rebranded "illustrative midpoint" throughout; abstract reports [0, 9,305] without central; section 5.3 rewritten |
| R3 | Endogenous-intake counterfactual | 10% boost: 15,806 (-5%); 20% boost: 14,973 (-10%) | Section 5.5 reports both; modest impact relative to capacity ceiling |
| R4 | Holding-cost sensitivity | EUR 500/1000/1500 per unit-month; unweighted 113,658 um = EUR 56.8M | Section 5.7 reports sensitivity table; derivation clarified; outcome-weighting caveat added |
| R5 | Construction-capacity ceiling | 35K ceiling: 7,421 (-55%); 38K ceiling: 13,421 (-19%) | **Headline revised**: counterfactual gap now reported as [7,421, 16,638]; abstract updated |
| R6 | JR multiplier sensitivity | 3x: 0.071; 5x: 0.118; 7x: 0.165; 10x: 0.236 | Section 5.9 reports range; 7x flagged as assumption; rho not used to support 25% attribution |
| R7 | Reconcile paper-vs-data inconsistencies | 2020 corrected 67,434 to 58,818; Dublin corrected 17 to 18; 2018-2021 corrected 93,708 to 88,422; E11 corrected; stated-um corrected 67,908 to 63,804 | All figures in paper now trace to results.tsv; cross-check R7a confirms E14.* sum = E01 |

## References

Selected citations from `papers.csv` (205 verified entries):

- P001 Geltner, D. (2014). *Commercial Real Estate Analysis and Investments*. MIT Press.
- P004 Glaeser, E. & Gyourko, J. (2018). The economic implications of housing supply. *JEP*.
- P009 Lyons, R. (2021). Can taxes on construction help address Ireland's housing shortage? *ESR*.
- P010 DHLGH (2021). *Housing for All*. Government of Ireland.
- P011 SCSI (2022). *The real cost of new apartment delivery*.
- P018 Saiz, A. (2010). The geographic determinants of housing supply. *QJE*.
- P021 Halliday, S. (2004). *Judicial Review and Compliance with Administrative Law*. Hart.
- P039 McGarity, T. (1992). Some thoughts on deossifying the rulemaking process. *Duke LJ*.
- P041 Hogan, G. & Morgan, D.G. (2010). *Administrative Law in Ireland*. Round Hall.
- P043 Simons, G. (2019). *Planning and Development Law* (3rd ed.). Round Hall.
- P046 OPR (2022). Appendix-2: Breakdown of Determined JRs involving ABP.
- P091 Kleinrock, L. (1975). *Queueing Systems Volume 1*. Wiley.
- P093 Kingman, J.F.C. (1961). The single server queue in heavy traffic. *Proc. Cambridge*.
- P096 Angrist, J. & Pischke, J.S. (2009). *Mostly Harmless Econometrics*. Princeton.
- P100 Abadie, A. et al. (2010). Synthetic control methods. *JASA*.
- P108 Oaxaca, R. (1973). Male-female wage differentials. *IER*.
- P137 CSO (2024). New Dwelling Completions StatBank NDQ07. CSO Ireland.
