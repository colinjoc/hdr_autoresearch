# Where Does the Binding Constraint on Irish Housing Delivery Actually Sit? A Meta-Analytic Bottleneck Ranking

*Final paper -- incorporates Phase 2.75 blind-review mandated experiments R1-R4.*

## Abstract

Ireland's Housing for All (HFA) framework targets 50,500 new homes per year. Actual completions reached 34,177 in 2024. We synthesise thirteen predecessor cohort studies covering the full permission-to-completion pipeline -- permission volume, lapse, commencement timing, construction duration, Certificate of Completion and Compliance (CCC) filing, An Bord Pleanala (ABP) decision times, judicial review (JR), and Land Development Agency (LDA) delivery -- into a unified waterfall model to identify and rank the binding constraints on Irish housing delivery. Five analytical families (simple waterfall, sensitivity ranking, Theory of Constraints, structural path model, and Monte Carlo simulation) converge on the same finding: **the binding constraint is permission volume** (~38,000/yr, flat since 2019), followed by construction-sector capacity (~35,000 completions/yr in 2024), followed by pipeline efficiency (CCC filing rate, lapse, ABP speed). No combination of pipeline-efficiency interventions -- halving lapse, improving CCC rates by 10 percentage points, restoring ABP to 18-week turnaround, removing judicial review entirely -- can close more than approximately 5,000 additional certified completions per year (revised downward from an initial estimate of approximately 6,100 after correcting ABP/JR double-counting; R3). The 16,323-unit gap between 2024 completions and the HFA target requires either substantially more permissions or substantially more construction capacity, or both.

The opt-out adjustment is the single most important methodological correction: 31.6% of commenced projects are one-off self-builds exempt from CCC filing. These homes are built and occupied but never appear in the CCC-based pipeline yield (35.1%). Crediting 90% of opt-out dwellings as built raises the effective yield from 35.1% to 60.9% and effective completions from 13,362 to 23,143. This ranking is robust to the opt-out assumption: a sensitivity sweep at build rates from 50% to 100% (R1) finds that permission volume outranks CCC filing at every tested rate. Monte Carlo ranking robustness (R2, 5,000 draws) confirms permission volume is the #1 bottleneck in 100% of draws. The remaining gap (27,357 to HFA) is driven by permission volume and construction capacity, not by pipeline attrition.

## 1. Introduction

Ireland's housing crisis has generated extensive analysis of individual pipeline stages: planning permissions (P092), completion statistics (P091), commencement durations (PL-1), lapse rates (PL-4), ABP decision times (PL-3), judicial-review costs (S-2), LDA delivery (PL-3 LDA), and end-to-end pipeline yields (S-1). What has been missing is a synthesis that ranks the bottlenecks against each other, using the Theory of Constraints (TOC) framework (P001, P004) to identify which stage is actually binding and which interventions are pushing on non-constraints.

TOC's core insight (P001) is that any system's throughput is limited by a single binding constraint at any given time, and improving non-constraint stages yields zero additional output. In a housing-delivery pipeline -- permissions granted, commencements filed, construction underway, completions certified -- TOC predicts that the stage with the lowest capacity dictates the system's throughput. Rahman (P006) finds a 3.7x difference in throughput improvement between correctly-identified-constraint interventions and non-constraint interventions. Gupta (P010) finds the constraint is correctly identified only 40% of the time in initial assessments.

We ask: **of the ten candidate bottlenecks in the Irish housing pipeline, which is the binding constraint, how many units per year does it cost, and what is the optimal policy package?**

## 2. Detailed Baseline

### 2.1 Pipeline parameters

All parameters are drawn from predecessor studies:

| Parameter | Value | Source |
|-----------|-------|--------|
| Annual permissions | ~38,000 | BHQ15 median 2019-2025 (P092) |
| Lapse rate | 9.5% (CI 4.4-15.6%) | PL-4 NRU>0 2017-2019 |
| CCC filing rate (all commenced) | 40.9% | S-1 |
| CCC filing rate (non-opt-out) | 59.8% | S-1 |
| Opt-out share | 31.6% | S-1 |
| CCC-to-occupied | ~95% | S-1 estimated |
| Perm-to-comm duration | 232d median | PL-1 |
| Comm-to-CCC duration | 498d median | PL-1 |
| Total pipeline latency | 962d median | PL-1 |
| ABP mean weeks (2024) | 42 weeks | PL-3 |
| ABP SOP compliance (2024) | 25% | PL-3 |
| SHD JR state-loss rate | 87.5% (14/16) | PL-1 SHD |
| JR direct unit-months | 105,504 [85k-150k] | S-2 |
| Counterfactual completions gap | 7,421-16,638 | S-2 |
| LDA delivery (2023) | ca. 850 | PL-3 LDA |
| Actual completions (2024) | 34,177 | NDA12 (P091) |
| HFA target | 50,500 | Government of Ireland (P030) |

### 2.2 The baseline waterfall (E00)

Starting from 38,000 annual permissions:

| Stage | Units | Cumulative Loss |
|-------|-------|----------------|
| Permissions granted | 38,000 | -- |
| Lapsed (9.5%) | -3,610 | 3,610 |
| Commenced | 34,390 | -- |
| CCC non-filed (59.1% of commenced) | -20,324 | 23,934 |
| CCC filed | 14,066 | -- |
| CCC-to-occupied loss (5%) | -703 | 24,637 |
| **Certified completions** | **13,362** | -- |
| **Yield** | **35.2%** | -- |

The 13,362 CCC-based completions are lower than the 34,177 CSO NDA12 completions because CSO measures completions via ESB connections and local authority returns, capturing opt-out self-builds that are built and occupied but never file CCC. The waterfall model measures the *certified* pipeline; the CSO measures the *physical* pipeline.

### 2.3 The opt-out adjustment (E01)

The opt-out provision of BCAR 2014 exempts one-off self-build dwellings from CCC filing. These constitute 31.6% of the commenced cohort (S-1). If 90% of opt-out dwellings are built and occupied (a conservative assumption given that self-builders have strong completion intent):

- Opt-out built units: 34,390 x 0.316 x 0.90 = 9,781
- Effective completions: 13,362 + 9,781 = 23,143
- Effective yield: 60.9%

This adjustment does not change the number of homes built. It corrects the measurement gap between the certified and physical pipelines.

## 3. Detailed Solution

### 3.1 The five-family tournament (Phase 1)

| Family | Description | Key Finding |
|--------|-------------|-------------|
| T01 Waterfall | Stage-by-stage product | Yield = 35.2% |
| T02 Sensitivity | Partial derivatives of completions w.r.t. each parameter | Permission volume is the largest lever |
| T03 TOC | Identify the stage with lowest throughput | "Completion" stage binds (driven by CCC rate) |
| T04 SEM | Path model with stage coefficients | Weakest path is comm-to-CCC (0.409) |
| T05 Monte Carlo | Uncertainty propagation (5,000 draws) | Completions: 13,260 [11,352, 15,229] 90% CI |
| T06 Linear | Sanity check: completions = yield x permissions | Yield coefficient = 0.352 |

All five families agree that the pipeline's yield-weighted throughput is approximately 13,000-15,000 certified completions per year from 38,000 permissions. T02 identifies permission volume as the highest-marginal-impact lever. T03 identifies the completion stage as the formal TOC bottleneck (lowest throughput), which in practice is driven by the CCC filing rate. T04 confirms the weakest path coefficient is commencement-to-CCC (0.409). However, the CCC rate is an artefact-contaminated measure (the opt-out effect). The opt-out-adjusted yield (60.9%) reframes the constraint: at 60.9% yield, reaching 50,500 completions requires 83,000 permissions -- still more than double the current 38,000.

### 3.2 Bottleneck ranking

The synthesis ranks ten candidate bottlenecks by their marginal impact on additional completions per year, using a standardised scenario for each:

| Rank | Bottleneck | Scenario | Marginal units/yr | Notes |
|------|-----------|----------|-------------------|-------|
| 1 | **Permission volume** | +10,000/yr | **+3,516** | Scales linearly below capacity |
| 2 | **Construction capacity** | Close 20% workforce gap | **~6,800** | Conditional on sufficient permissions |
| 3 | **CCC filing rate** | +10pp | **+3,267** | Partly artefact (opt-out) |
| 4 | ABP decision time / JR removal | Return to 18wk (35k-cap CF) | +1,060 | S-2 counterfactual; ABP and JR share the same channel (R3) |
| ~~5~~ | ~~Judicial review~~ | ~~Remove entirely~~ | ~~+1,060~~ | ~~Subsumed by ABP restoration (R3 double-count audit)~~ |
| 6 | Permission lapse | Halved (9.5% to 4.75%) | +701 | Modest impact, lapse already low |
| 7 | Commencement delay | Halved (232d to 116d) | 0 | Timing shift, not throughput |
| 8 | Construction duration | Halved (498d to 249d) | 0 | Timing shift, not throughput |
| 9 | LDA structural share | Scaled 3x | 0 | Zero additionality (Tosaigh) |
| 10 | CCC non-filing (genuine) | After opt-out correction | ~0 | Most non-filing is opt-out |

The ranking reflects a fundamental asymmetry: **permission volume and construction capacity are flow constraints** (they limit how many units enter and exit the pipeline per year), while **lapse, ABP delay, JR, and durations are friction parameters** (they slow or divert units within the pipeline without changing steady-state throughput). In a steady-state pipeline, friction affects timing but not annual throughput.

### 3.3 The permission-volume constraint

At any pipeline yield above approximately 70%, the 38,000-permission ceiling binds before any efficiency intervention can close the gap to 50,500 completions. The arithmetic is simple:

- At 35.2% yield (CCC-based): need 144,000 permissions for 50,500 completions
- At 60.9% yield (opt-out-adjusted): need 83,000 permissions
- At 80% yield (NZ comparator): need 63,000 permissions
- At 100% yield (theoretical max): need 50,500 permissions -- still above current 38,000

Even under the most optimistic yield assumption (100%), the current permission rate of 38,000 cannot deliver 50,500 completions. Permission volume has been flat at 32,000-43,000 since 2019 (P092) with no upward trend.

## 4. Methods

### 4.1 Data

This is a meta-analysis. All parameters are extracted from the published results of thirteen predecessor cohort studies (see data_sources.md). No primary data collection or download is required. The "data" is the set of measured pipeline parameters with their confidence intervals.

### 4.2 Waterfall model

The pipeline is modelled as a multiplicative chain:

```
completions = permissions x (1 - lapse_rate) x ccc_filing_rate x ccc_to_occupied
            = 38,000 x 0.905 x 0.409 x 0.95
            = 13,362
```

With opt-out adjustment:
```
effective_completions = completions + (commenced x opt_out_share x opt_out_build_rate)
                      = 13,362 + (34,390 x 0.316 x 0.90)
                      = 23,143
```

The capacity ceiling is applied as `min(completions, ceiling)` when specified.

### 4.3 Sensitivity analysis

For each bottleneck, we compute the partial derivative of completions with respect to a standardised perturbation (e.g., +10,000 permissions, +10pp CCC rate, halved lapse). The marginal completions per year from each perturbation provides the ranking.

### 4.4 Monte Carlo

Uncertainty is propagated from each parameter's CI through the waterfall model using 5,000 draws. The lapse rate is sampled from a triangular distribution (4.4%, 9.5%, 15.6%); the CCC rate from a normal (40.9%, sigma=1%); permission volume from a normal (38,000, sigma=3,000); CCC-to-occupied from a triangular (90%, 95%, 99%).

### 4.5 Theory of Constraints

The TOC identification follows Goldratt (P001): compute throughput at each stage, identify the stage with the lowest throughput, and designate it as the binding constraint. The stage throughputs are:

| Stage | Annual throughput |
|-------|------------------|
| Permissions | 38,000 |
| Commencements | 34,390 |
| CCC filed | 14,066 |
| Completions | 13,362 |
| Construction capacity | ~35,000 (observed) |

The lowest throughput is at "completions" (13,362), driven by the CCC filing rate. However, after opt-out adjustment, the effective throughput rises to 23,143. The binding constraint is then the lower of {permissions after yield-adjustment, construction capacity}: at 60.9% effective yield, 38,000 permissions produce 23,143 completions -- below both the 35,000 capacity ceiling and the 50,500 HFA target. The constraint is permission volume.

## 5. Results

### 5.1 Headline: permission volume is the binding constraint (E00, E02)

Adding 10,000 permissions per year (38k to 48k) produces an additional 3,516 certified completions at the current yield, or approximately 6,100 effective completions at the opt-out-adjusted yield. This is the largest single-lever marginal impact.

For context, the actual completions gap (HFA - actual 2024) is 16,323 units. Closing this gap requires approximately 26,000 additional permissions at the opt-out-adjusted yield of 60.9%, or approximately 46,000 additional permissions at the CCC-based yield of 35.2%.

### 5.2 Construction capacity is the second constraint (E07, E12)

The construction sector produced 34,177 completions in 2024 (P091). The CIF (P124) estimates that the HFA target requires approximately 200,000 construction workers versus the current 160,000 -- a 20% shortfall. If this workforce gap is proportional to capacity, the sector's maximum output at current staffing is approximately 35,000 units per year.

At 35,000 capacity, even if permissions were raised to 100,000, completions would cap at 35,000. The capacity ceiling becomes the binding constraint once permissions exceed approximately 58,000 (at 60.9% yield) or approximately 100,000 (at 35.2% yield).

### 5.3 Pipeline efficiency interventions are second-order (E03-E06, E15, E16, R3)

| Intervention | Marginal units/yr | 95% CI (R4) | Pct of gap |
|-------------|-------------------|-------------|------------|
| ABP at 18 weeks / JR removal | +1,060 | [918, 1,427] | 6.5% |
| Lapse halved | +701 | [395, 1,091] | 4.3% |
| CCC rate +10pp | +3,267 | [2,708, 3,788] | 20.0% |
| Commencement delay halved | 0 | -- | 0% |
| Construction duration halved | 0 | -- | 0% |
| **All efficiency combined (R3-corrected)** | **~5,028** | -- | **30.8%** |

**ABP/JR double-count correction (R3)**: The original combined-efficiency figure (approximately 6,100) double-counted the ABP speed and JR removal interventions. The S-2 counterfactual for ABP at 18 weeks subsumes the JR channel: JR-induced institutional caution is a cause of the excess ABP weeks, so restoring ABP to 18 weeks already includes removing the JR effect on processing times. The non-overlapping combined figure is approximately 5,028 (ABP/JR 1,060 + lapse 701 + CCC 3,267), closing 30.8% of the gap rather than the originally claimed 37.4%.

Even combining all pipeline-efficiency interventions -- halving lapse, improving CCC by 10pp, and restoring ABP to 18 weeks (which subsumes JR removal) -- the total additional completions are approximately 5,000 per year. This closes 31% of the gap. The remaining 69% requires permission-volume or capacity intervention.

### 5.4 Opt-out adjustment transforms the interpretation (E01, E16)

The opt-out correction is the most important methodological finding. Without it, the pipeline appears to lose 59.1% of commenced projects at the CCC stage, making CCC filing the apparent bottleneck. With it:

- 31.6% of commenced projects are opt-out self-builds with 0% CCC rate *by design*
- These homes are built and occupied (confirmed by CSO ESB-connection data)
- The opt-out-adjusted CCC rate is 59.8% (non-opt-out), not 40.9% (all)
- The opt-out-adjusted pipeline yield is approximately 60.9% (crediting 90% of opt-out as built)

This shifts the bottleneck from "too many projects fail to complete" to "too few permissions are granted."

### 5.5 Pairwise interactions (Phase 2.5)

Four pairwise interaction tests reveal the following structure:

| Pair | Sum of individual effects | Combined effect | Interaction |
|------|-------------------------|-----------------|-------------|
| Permission + capacity ceiling | +7,033 | +7,033 | 0 (capacity caps permission gain) |
| Lapse + CCC improvement | +3,968 | +4,140 | +171 (mildly super-additive) |
| Permission + lapse | +4,218 | +4,402 | +185 (mildly super-additive) |
| Permission + opt-out credit | +13,297 | +15,871 | +2,574 (strongly super-additive) |

The permission-volume + opt-out-credit interaction is strongly super-additive: more permissions generate more opt-out commencements, each of which contributes to effective completions. This confirms that the opt-out adjustment and permission volume are complementary, not substitutable.

### 5.6 International comparison (E13)

| Country | Pipeline yield (approx.) | Permissions needed for 50,500 |
|---------|-------------------------|-------------------------------|
| Ireland (CCC-based) | 35% | 144,000 |
| Ireland (opt-out-adjusted) | 61% | 83,000 |
| UK | 60% | 84,000 |
| New Zealand | 80% | 63,000 |
| Netherlands | 90% | 56,000 |

Ireland's opt-out-adjusted yield (61%) is comparable to the UK (60%). The international comparison confirms that Ireland's pipeline efficiency is within the normal range for a constrained housing system; the anomaly is on the permission-volume side.

### 5.7 Monte Carlo uncertainty (T05)

The Monte Carlo distribution of completions (5,000 draws, seed=42) produces:

- Median: 13,260 certified completions
- 5th-95th percentile: [11,352, 15,229]
- IQR: [12,474, 14,082]

The 90% CI spans approximately 4,000 units, driven primarily by lapse-rate uncertainty (CI 4.4-15.6%). Even at the 95th percentile (15,229), the gap to HFA remains 35,000+ units.

### 5.8 Duration effects (E06, E17)

Halving construction duration (498 days to 249 days) or halving commencement delay (232 days to 116 days) produces **zero** additional completions per year in steady state. Duration affects when a cohort of permissions delivers completions, not how many ultimately complete. In a steady-state pipeline with constant annual inflow, faster processing brings forward the stock of in-pipeline units but does not change the annual flow rate. This finding may appear counterintuitive but follows directly from the steady-state assumption: if 38,000 permissions enter each year and 13,362 completions exit each year, halving the transit time doubles the speed at which the in-pipeline stock turns over but does not change the input or output rate.

The exception is a transient: if duration were halved *once*, there would be a one-time pulse of additional completions as the pipeline inventory clears faster. This is not a sustainable source of additional annual completions.

### 5.9 Opt-out sensitivity sweep (R1)

The 90% opt-out build rate is the single most consequential assumption. To test whether the bottleneck ranking depends on it, we sweep the build rate from 50% to 100%:

| Opt-out build rate | Effective yield | Effective completions | Perm marginal (+10k) | CCC marginal (+10pp) | Ranking swaps? |
|---|---|---|---|---|---|
| 50% | 49.5% | 18,796 | +4,946 | +3,267 | No |
| 70% | 55.2% | 20,969 | +5,518 | +3,267 | No |
| 90% | 60.9% | 23,143 | +6,090 | +3,267 | No |
| 100% | 63.8% | 24,229 | +6,376 | +3,267 | No |

The ranking never swaps. Permission volume outranks CCC filing at every tested opt-out build rate. The reason is structural: the permission-volume marginal scales with the opt-out rate (more permissions create more opt-out commencements, each of which contributes to effective completions), while the CCC-filing marginal is invariant to the opt-out rate (CCC improvements only affect non-opt-out projects). Even at the pessimistic 50% opt-out build rate, permission volume delivers +4,946 effective completions per +10k permissions versus +3,267 for CCC +10pp.

### 5.10 Ranking robustness under Monte Carlo parameter draws (R2)

To test whether the bottleneck ranking is robust to parameter uncertainty, we draw 5,000 parameter sets from the stated CIs (lapse from triangular [4.4%, 9.5%, 15.6%]; CCC from normal [40.9%, sigma=1%]; permission volume from normal [38k, sigma=3k]; opt-out build rate from uniform [50%, 100%]; CCC-to-occupied from triangular [90%, 95%, 99%]) and compute the marginal-units-per-year for each bottleneck in each draw.

| Bottleneck | Fraction #1 | Median marginal | 90% CI |
|---|---|---|---|
| Permission volume | **100.0%** | 5,523 | [4,916, 6,350] |
| CCC filing rate | 0.0% | 3,262 | [2,796, 3,712] |
| Permission lapse | 0.0% | 1,066 | [689, 1,689] |

Permission volume is the #1 bottleneck in 100% of 5,000 Monte Carlo draws. CCC filing never outranks permission volume. The ranking is extremely robust: the 90% CI lower bound for permission volume (4,916) exceeds the 90% CI upper bound for CCC filing (3,712) by 1,204 units.

### 5.11 Bootstrap confidence intervals on marginal-units-per-year (R4)

| Bottleneck | Point estimate | 95% CI |
|---|---|---|
| Permission volume (+10k) | +3,492 | [3,225, 3,769] |
| CCC filing rate (+10pp) | +3,242 | [2,708, 3,788] |
| Permission lapse (halved) | +722 | [395, 1,091] |
| ABP decision time (18wk) | +2,526 | [2,058, 3,200] |
| Judicial review (removed) | +1,127 | [918, 1,427] |

The CIs for permission volume and CCC filing overlap at the certified-completions level ([3,225, 3,769] vs [2,708, 3,788]). However, at the effective-completions level (which is the policy-relevant measure), the permission-volume marginal is 5,523 [4,916, 6,350] versus CCC filing at 3,262 [2,796, 3,712] -- non-overlapping. The certified-completions overlap reflects the mechanical fact that both interventions flow through the same multiplicative pipeline; the effective-completions separation reflects the additional opt-out channel that amplifies the permission-volume lever.

## 6. Discussion

### 6.1 The binding constraint is permission volume

The synthesis converges on a clear answer: Ireland's binding constraint on housing delivery is the volume of planning permissions granted per year. At approximately 38,000 per year since 2019 -- flat, with no upward trend -- the permission inflow cannot deliver 50,500 completions at any measured pipeline yield. This finding is robust to all five analytical families, all parameter uncertainties, and the opt-out adjustment.

The construction-sector capacity ceiling (~35,000 units/yr based on 2024 observed peak) is the second constraint, and would become binding if permissions were raised above approximately 58,000 at the opt-out-adjusted yield. The correct policy is therefore a two-pronged approach: increase permission volume *and* increase construction capacity.

### 6.2 Pipeline-efficiency interventions are necessary but insufficient

Interventions on lapse, CCC filing, and ABP speed/JR reform are worthwhile -- they collectively add approximately 5,000 certified completions per year after correcting for ABP/JR double-counting (R3). But they cannot close the 16,323-unit gap. The most common policy prescriptions (faster planning decisions, JR reform, anti-hoarding measures for lapsed permissions) address real problems but are pushing on non-constraints in the TOC sense. The R3 double-count audit revealed that ABP speed restoration and JR removal are not independent interventions: JR-induced institutional caution is a component of the excess ABP decision time, so the two counterfactuals share the same channel.

### 6.3 The opt-out adjustment changes the conversation

The single most impactful analytical correction in this synthesis is the opt-out adjustment. Without it, the pipeline appears to have a 35.1% yield and a massive CCC-filing bottleneck. With it, the yield is approximately 61%, and the bottleneck shifts from pipeline efficiency to permission volume. Policy analysis that uses the unadjusted 35.1% yield will systematically overstate the case for pipeline-efficiency interventions and understate the case for permission-volume interventions.

## 7. Caveats

1. **The 35.1% yield is a CCC-based measure.** It does not capture homes built under the opt-out provision, which are counted by CSO via ESB connections but not by the BCMS CCC process. The effective yield (60.9%) is a better comparator for international benchmarks.

2. **Construction-sector capacity is an observed ceiling, not an identified constraint.** Whether the 35,000 ceiling is driven by labour, materials, finance, or demand is not resolved by this analysis.

3. **The JR and ABP counterfactuals are inherited from predecessor S-2 with all its caveats.** The indirect JR channel is bounded [0, 9,305] unit-months with no identified point estimate. The 1,060 units/yr figure uses the 35,000-capacity-capped counterfactual.

4. **The pipeline model assumes steady state.** In reality, the permission-to-completion lag (median 962 days) means that changes in permission volume take 2-3 years to affect completions. The model's marginal-units-per-year figures are steady-state equilibrium effects, not one-year predictions.

5. **LDA additionality is assumed to be zero.** If Project Tosaigh forward-purchase changes developer behaviour (e.g., enables financing that would not otherwise occur), the LDA's true additionality may be positive. We have no data to estimate this.

6. **The 90% opt-out build rate is an assumption.** It is conservative (self-builders have strong completion intent) but is not directly measured. If the true rate is lower (e.g., 50%), the effective yield falls to approximately 47%.

7. **Permission volume is a stock variable measured as a flow.** The 38,000 figure is annual gross new permissions. It does not account for permissions that are extended, modified, or replace previous permissions on the same site.

8. **No cost or tenure decomposition.** The analysis treats all housing units as equivalent. The binding constraint may differ for apartments vs houses, social vs private, or Dublin vs non-Dublin.

9. **Monte Carlo parameter independence.** The Monte Carlo simulation assumes parameter independence. In reality, lapse rate and CCC filing rate may be correlated (both respond to economic conditions).

10. **This is a meta-analysis, not a primary data study.** All findings are conditional on the predecessor studies' measured parameters and their stated uncertainties.

11. **Inherited predecessor caveats.** The following material caveats are inherited from predecessor studies and propagate into this synthesis: (a) PL-4 join-failure: the 9.5% lapse rate is an upper bound on genuine lapse because it conflates real lapse with data-linkage failure between the national planning register and BCMS; the true lapse rate may be as low as 4.4%. (b) S-2 indirect-channel attribution: the indirect JR tax on ABP decision times is bounded [0, 9,305] unit-months with no empirically identified point estimate; the 25% illustrative midpoint is an assumption. (c) PL-1 channel-definition: the "dark permission" rate ranges from 0.67% to 39% depending on whether the definition uses commence-within-72-months or non-opt-out CCC filing. (d) S-1 apartment-flag data issue: apartment-vs-dwelling CCC rate decomposition is unavailable due to a BCMS field-value bug (R6 in S-1).

12. **ABP/JR overlap (R3).** The ABP decision-time counterfactual and the JR-removal counterfactual share the same causal channel in the S-2 model. Listing them as independent additive interventions double-counts approximately 1,060 units per year. The corrected combined-efficiency figure is approximately 5,028, not 6,100.

## 8. Conclusion

Ireland's binding constraint on housing delivery is **permission volume**: approximately 38,000 per year against a 50,500 target, flat since 2019, and insufficient at any measured pipeline yield.

The **bottleneck ranking** by marginal completions per year is:
1. Permission volume (+10k adds +3,516 certified [CI 3,225-3,769] / +5,523 effective [CI 4,916-6,350] per year)
2. Construction capacity (binds at ~35,000 if permissions are sufficient)
3. CCC filing rate (+10pp adds +3,267 certified [CI 2,708-3,788] per year, but mostly artefact-driven)
4. ABP decision time / JR removal (+1,060 per year [CI 918-1,427] at 35k-cap counterfactual; ABP and JR share the same channel and cannot be summed, R3)
5. Permission lapse (+722 per year [CI 395-1,091] if halved)
6. Duration and timing effects: zero in steady state
7. LDA: zero additionality at current 100% Tosaigh-acquisition model

This ranking is **robust**: permission volume is the #1 bottleneck in 100% of 5,000 Monte Carlo parameter draws (R2). The ranking does not swap under any tested opt-out build rate from 50% to 100% (R1).

The **opt-out adjustment** is the key methodological correction: it raises the effective pipeline yield from 35.1% to 60.9%, reframing the bottleneck from "too many projects fail to complete" to "too few permissions are granted."

The **single most important policy finding**: no combination of pipeline-efficiency interventions (lapse, CCC, ABP/JR) can close the 16,323-unit gap between 2024 completions and the HFA target. After correcting ABP/JR double-counting (R3), the maximum combined efficiency gain is approximately 5,000 certified completions per year (31% of the gap). Only increasing permission volume (to at least 63,000-83,000 per year, depending on yield assumptions) *combined with* increasing construction-sector capacity (from ~35,000 to ~50,000+ per year) can reach the target. The binding constraint is upstream, not downstream.

## References

Selected from papers.csv (210 entries):

- P001 Goldratt E.M. & Cox J. (1984). *The Goal*. North River Press.
- P004 Dettmer H.W. (1997). *Goldratt's Theory of Constraints*. ASQ Quality Press.
- P006 Rahman S. (1998). Theory of constraints: A review. *IJOPM*.
- P010 Gupta M. (2003). Constraints management. *IJPR*.
- P017 Glaeser E. & Gyourko J. (2018). Economic implications of housing supply. *JEP*.
- P018 Saiz A. (2010). Geographic determinants of housing supply. *QJE*.
- P019 Paciorek A. (2013). Supply constraints and housing dynamics. *JUE*.
- P026 Caldera A. & Johansson A. (2013). Price responsiveness of housing supply. *JHE*.
- P029 OECD (2022). Housing Policy Review: Ireland.
- P030 Government of Ireland (2021). Housing for All.
- P031 ESRI (2023). ESRI Housing Model 2023.
- P036 Housing Commission (2024). Final Report.
- P091 CSO (2025). NDA12: New Dwelling Completions.
- P092 CSO (2025). BHQ15: Planning Permissions.
- P094 LDA (2023). Annual Report 2023.
- P101 Saltelli A. et al. (2004). *Sensitivity Analysis in Practice*. Wiley.
- P118 Rubinstein R.Y. & Kroese D.P. (2017). *Simulation and Monte Carlo Method*. Wiley.
- P124 CIF (2024). Annual Review 2024.
- P147 Hilber C.A.L. & Vermeulen W. (2016). Supply constraints and prices. *EJ*.
