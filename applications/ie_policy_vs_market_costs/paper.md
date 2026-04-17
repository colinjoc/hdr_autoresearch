# Policy-Set vs Market-Driven Costs in Irish Residential Development: A Full Cost Stack Decomposition

## Abstract

We decompose the total cost of new residential development in Ireland into policy-set components (those government can directly change: VAT, Part V, development contributions, BCAR compliance, planning fees) and market-driven components (materials, labour, land, finance, developer margin). Using real data from the CSO (WPM28, EHQ03, BEA04, RZLPA02), Buildcost.ie (H1 2025), and published local authority development contribution schemes, we construct a full cost stack for four dwelling types across four location categories and all 26 Republic of Ireland counties. Policy-set costs account for 13-17% of total development cost (median 15.5%), while market-driven costs account for 83-87%. The single most impactful policy lever is VAT: zeroing the 13.5% rate on new residential construction makes three counties viable under static pricing assumptions (Dublin, Wicklow, Kildare), but under a 50% pass-through assumption (where half of the saving flows to buyers as lower prices), zero counties become viable. Even eliminating all policy costs entirely makes only 4 of 26 counties commercially viable under static pricing, dropping to 3 under 50% pass-through. The median viability gap is EUR 144,289 per unit -- computed from scheme-level costs using a 0.85 factor applied to one-off rebuild rates -- far exceeding the total policy cost per unit of EUR 70-100k. The housing viability crisis is fundamentally a market cost problem -- materials, labour, land, and finance -- not a policy cost problem. A national viability gap fund at 33,000 units per year would cost EUR 4.4 billion annually.

## 1. Introduction

Irish housing policy debate frequently focuses on policy-set costs as barriers to development viability: VAT on construction, Part V affordable housing obligations, development contributions, building regulation compliance costs (BCAR), and planning fees. The implicit assumption is that reducing these policy-imposed costs would unlock significantly more housing supply by bringing more locations across the viability frontier.

This paper tests that assumption quantitatively. We construct a full cost stack for representative dwelling types across all 26 Republic of Ireland counties, classify each component as POLICY-set (government can directly change the rate or remove the obligation) or MARKET-driven (government cannot directly set the price), and run a systematic scenario analysis asking: if each policy cost were halved or zeroed, how many additional counties would cross from unviable to viable for speculative residential development?

The predecessor projects provide essential context. C-1 established that Irish construction costs grow at approximately 4% per annum for both materials and labour, and that the NZEB (Nearly Zero Energy Buildings) regulation was not a significant independent driver of cost growth. U-2 established the viability frontier: only Dublin-area counties are close to commercial viability for apartment development, and even Dublin requires sustained annual price growth of approximately 5.1% for apartment schemes to be viable.

## 2. Data and Methods

### 2.1 Data Sources

All data are from published sources; no synthetic data are used.

**Construction costs**: Buildcost.ie H1 2025 Construction Cost Guide provides tender prices (EUR per square metre) by dwelling type and region, based on SCSI (Society of Chartered Surveyors Ireland) methodology. These are one-off rebuilding guide rates. We apply a 0.85 scheme factor to convert from one-off rebuilding costs to multi-unit development scheme costs, reflecting economies of scale in multi-unit schemes. This scheme-cost basis is used throughout all viability and gap calculations.

**Land prices**: CSO dataset RZLPA02 provides median zoned residential land prices per hectare by county (2024 data). We convert to per-unit land cost using typical density assumptions: 35 units/ha for semi-detached, 100 for apartments, 20 for detached, 45 for terraced.

**Policy cost parameters**: VAT rate (13.5%) from Revenue Commissioners; Part V obligation (20% at cost price) from Planning and Development Act 2000 s.96; development contributions from published LA schemes (range EUR 6,000-25,000 per unit); BCAR compliance costs (EUR 4,500-8,000 per unit) from RIAI/SCSI surveys; planning fees from SI 600/2001.

**Sale prices**: New-build sale prices from Property Price Register (2024) data, by county.

**Calibration**: The SCSI benchmark for a EUR 400,000 dwelling is hard costs at 53% and soft costs at 47%. Our model produces hard cost shares of 50-53% across locations, within the calibration range.

### 2.2 Cost Stack Model

For each dwelling type (3-bed semi-detached 110 sqm, 2-bed apartment 75 sqm, 4-bed detached 119 sqm, 3-bed terraced 98 sqm) and each location (Dublin, commuter belt, regional city, rural), we compute:

- **Materials** = 45% of hard construction cost
- **Labour** = 40% of hard construction cost
- **Site works** = 15% of hard construction cost
- **Land** = land price per hectare / units per hectare
- **Development contributions** = LA-published rate per unit
- **Part V** = estimated effective cost per unit (varies by location; see Section 2.3)
- **VAT** = 13.5% of (hard cost + professional fees). VAT is applied to the construction output value because builders reclaim VAT on their inputs (materials, plant hire); the net VAT liability is on the value added in construction, which equals the output (hard cost + fees) minus reclaimable input tax. We apply VAT to the full output as an upper bound, noting that partial input reclaim would reduce the effective rate.
- **BCAR** = fixed per dwelling type
- **Planning fees** = EUR 1,500 (including fire cert, disability cert)
- **Professional fees** = 12% of hard cost
- **Finance** = 8% of subtotal
- **Developer margin** = 15% of (subtotal + finance)

### 2.3 Part V Cost Estimation

Part V requires 20% of units in a development to be transferred to the local authority at "cost price" -- NOT given away. The cost to the developer is the forgone profit margin on those 20% of units: `0.20 * max(0, sale_price - cost_price)`, spread across all units. In the cost stack, we use fixed estimates per region (EUR 5,000-20,000) based on SCSI viability reports. These are upper-bound estimates: the cross-subsidy analysis in Section 3.7 computes the actual forgone-margin cost as EUR 13,820 per market unit in Dublin, EUR 3,418 in the commuter belt, and near-zero in regional and rural areas where cost price exceeds sale price. The fixed cost stack estimates are conservative (higher than computed) to avoid understating the policy burden.

### 2.4 Classification

Each component is classified as POLICY (government sets the rate) or MARKET (price determined by market forces):

| POLICY | MARKET |
|:---|:---|
| VAT (13.5%) | Materials |
| Part V (20%) | Labour |
| Development contributions | Site works |
| BCAR compliance | Land |
| Planning fees | Professional fees |
| | Finance |
| | Developer margin |

Note on developer margin: the 15% developer margin is classified as MARKET because it reflects the return required by private capital. However, this classification is debatable. State-led delivery through the Land Development Agency (LDA), Approved Housing Bodies (AHBs), and local authority direct-build routinely operates at 6-8% margin or cost-neutral. Part V units themselves are delivered at 0% margin. If developer margin were reclassified as partially policy-amenable (reflecting the state's ability to deliver at lower margins through alternative delivery models), the policy-amenable share would rise to approximately 25-28% of total cost. The margin compression experiment (E13, Section 3.9) quantifies this effect: compressing margin from 15% to 10% brings Wicklow to within 0.2% of viability.

### 2.5 Viability Metric

A county is **viable** for speculative development when the achievable new-build sale price exceeds the total development cost (including all components above). The viability margin is (sale price - total cost) / sale price. Positive margin = viable; negative = unviable.

## 3. Results

### 3.1 Cost Stack Decomposition (E00)

For a Dublin 3-bed semi-detached (110 sqm):

| Component | EUR | Share | Class |
|:---|---:|---:|:---|
| Materials | 134,228 | 22.7% | MARKET |
| Labour | 119,314 | 20.2% | MARKET |
| Developer margin | 74,911 | 12.7% | MARKET |
| VAT | 45,098 | 7.6% | POLICY |
| Site works | 44,743 | 7.6% | MARKET |
| Land | 45,369 | 7.7% | MARKET |
| Finance | 36,993 | 6.3% | MARKET |
| Professional fees | 35,791 | 6.0% | MARKET |
| Dev contributions | 25,000 | 4.2% | POLICY |
| Part V | 20,000 | 3.4% | POLICY |
| BCAR | 5,500 | 0.9% | POLICY |
| Planning fees | 1,500 | 0.3% | POLICY |
| **TOTAL** | **591,929** | **100%** | |
| **POLICY total** | **97,098** | **16.4%** | |
| **MARKET total** | **494,831** | **83.6%** | |

Policy share varies from 13.0% (Longford) to 18.8% (Dublin apartment), with a narrow range reflecting the relatively uniform policy cost structure across Ireland.

### 3.2 Baseline Viability (E00, E10-E13)

Zero of 26 counties are viable at baseline for speculative 3-bed semi development. The closest counties to viability are:

| County | Sale Price | Total Cost | Margin | Gap |
|:---|---:|---:|---:|---:|
| Wicklow | EUR 480,000 | EUR 502,839 | -4.8% | EUR 22,839 |
| Dublin | EUR 550,000 | EUR 591,929 | -7.6% | EUR 41,929 |
| Kildare | EUR 460,000 | EUR 498,514 | -8.4% | EUR 38,514 |
| Meath | EUR 420,000 | EUR 477,631 | -13.7% | EUR 57,631 |
| Cork | EUR 400,000 | EUR 478,035 | -19.5% | EUR 78,035 |

### 3.3 Single Policy Lever Impact (E01-E06, E09)

| Lever | Counties Viable | Per-Unit Saving |
|:---|---:|---:|
| VAT zeroed (13.5% -> 0%) | **3**/26 | EUR 45,098 |
| VAT to 9% | 0/26 | EUR 15,035 |
| Part V zeroed | 0/26 | EUR 20,000 |
| Part V halved | 0/26 | EUR 10,000 |
| Dev contribs zeroed | 0/26 | EUR 25,000 |
| Dev contribs halved | 0/26 | EUR 12,500 |
| BCAR zeroed | 0/26 | EUR 5,500 |
| BCAR halved | 0/26 | EUR 2,750 |
| Planning fees zeroed | 0/26 | EUR 1,500 |

**VAT is the only single policy lever that moves any county across the viability frontier.** Zeroing VAT makes Wicklow, Dublin, and Kildare viable by saving approximately EUR 45,000 per unit. However, this result assumes that sale prices remain unchanged (see Section 3.8 for pass-through sensitivity).

### 3.4 Combined Policy Scenarios (E07-E08)

| Scenario | Counties Viable | Counties |
|:---|---:|:---|
| All policy halved | 3/26 | Wicklow, Dublin, Kildare |
| All policy zeroed | 4/26 | Wicklow, Dublin, Kildare, Meath |

Halving all policy costs achieves the same result as zeroing VAT alone (3 counties). This demonstrates that VAT dominates the policy cost stack. Zeroing all policy costs adds only one additional county (Meath).

### 3.5 Market-Side Reforms (E15-E17)

| Reform | Counties Viable |
|:---|---:|
| Land at CPO agricultural price (EUR 15k/ha) | 2/26 |
| Modular construction (-20% hard costs) | 3/26 |
| Modular + VAT halved + Part V halved | 4/26 |
| Radical: modular + CPO + all policy zeroed | 9/26 |

Even the most radical combined reform -- modular construction, compulsory purchase of land at agricultural prices, and complete elimination of all policy costs -- makes only 9 of 26 counties viable.

### 3.6 Viability Gap Fund (E18, E29-E30)

The per-unit subsidy required to make each county viable ranges from EUR 22,839 (Wicklow) to EUR 225,873 (Longford), with a median of EUR 144,289 and mean of EUR 132,145. These gaps are computed from the same scheme-cost model (0.85 factor) used throughout; they represent the shortfall between achievable sale prices and full development cost at scheme scale.

At the Housing for All target of 33,000 completions per year, a national viability gap fund would cost approximately EUR 4.4 billion annually.

Subsidy escalation:

| Per-Unit Subsidy | Counties Viable |
|:---|---:|
| EUR 25,000 | 1/26 |
| EUR 50,000 | 3/26 |
| EUR 75,000 | 4/26 |
| EUR 100,000 | 5/26 |
| EUR 125,000 | 8/26 |
| EUR 150,000 | 15/26 |
| EUR 175,000 | 22/26 |
| EUR 200,000 | 24/26 |

### 3.7 Part V Cross-Subsidy (E19-E20)

Part V's cross-subsidy effect is modest: the computed per-unit cost to remaining market units is EUR 13,820 in Dublin, EUR 3,418 in the commuter belt, and near-zero in regional and rural areas (where the sale-price-to-cost gap is negative or very small, meaning Part V units are transferred at close to market value). The cost stack uses conservative fixed estimates (EUR 20,000 for Dublin) that exceed the computed cross-subsidy (EUR 13,820), representing an upper-bound assumption. Part V delivers an estimated 2,100 social housing units per year (6,066 theoretical x 35% effective rate).

### 3.8 Pass-Through Sensitivity (E31)

The static-price scenarios (Sections 3.3-3.4) assume that policy cost savings accrue entirely to the developer, with sale prices unchanged. In practice, the tax incidence literature (Crossley et al., 2012; Glaeser and Gyourko, 2018) predicts that some portion of policy savings would flow through to buyers as lower prices, particularly in supply-constrained markets where regulatory barriers bind.

We test a 50% pass-through assumption: if a policy saving reduces development cost by EUR X, the sale price also decreases by EUR X/2 (i.e., half the saving is captured by buyers, half by developers).

| Scenario | Static Counties Viable | 50% Pass-Through Counties Viable |
|:---|---:|---:|
| VAT zeroed | 3/26 | **0/26** |
| All policy zeroed | 4/26 | **3/26** |

Under 50% pass-through, zeroing VAT alone makes NO counties viable -- the sale price reduction fully offsets the cost saving for the three borderline counties. Even zeroing ALL policy costs makes only 3 counties viable (one fewer than the static case). This result is important: it means that the viability benefit of policy cost reform is substantially overstated by static models. The true benefit depends on the degree to which savings are shared between developers and buyers, which is empirically uncertain.

### 3.9 Margin Compression and Interaction Effects (E13, E26-E28)

Compressing developer margin from 15% to 10% brings the closest counties substantially closer to viability: Wicklow reaches -0.2% margin, Dublin -2.9%, Kildare -3.7%. However, none cross the threshold at 10% margin alone.

VAT zeroed alone achieves the same county count (3) as VAT zeroed + Part V zeroed combined (3), suggesting the effects are NOT additive at the county-level threshold. The marginal impact of Part V removal is subsumed within the VAT removal.

## 4. Discussion

### 4.1 The Fundamental Finding

Policy costs account for only 13-17% of total development cost. Even if every policy cost were abolished entirely, 22 of 26 counties would remain unviable for speculative development. Under a realistic 50% pass-through assumption, the viability improvement is even smaller: zero counties become viable from VAT reform alone. The housing viability crisis is driven by market costs: materials (23% of total), labour (20%), developer margin (13%), land (7-8%), and finance (6%).

This finding challenges the common framing that "government-imposed costs" are the primary barrier to housing supply. While policy costs are real and their reduction would help at the margin (particularly in the four counties closest to viability), they are not the binding constraint for the vast majority of the country.

### 4.2 VAT Dominance Among Policy Levers

VAT on new construction is the single largest and most impactful policy cost. At EUR 45,098 per Dublin unit, it exceeds development contributions (EUR 25,000), Part V (EUR 20,000), and BCAR (EUR 5,500) combined in some locations. Zeroing VAT achieves the same viability improvement as halving ALL other policy costs combined. This suggests that if policy reform is to target a single lever, VAT reduction or zero-rating (as in the UK) would be the most effective intervention.

However, the pass-through analysis (Section 3.8) cautions that the viability benefit of VAT reform may be substantially reduced if savings are shared with buyers rather than retained as developer margin. Under 50% pass-through, VAT reform moves zero counties across the viability frontier, fundamentally changing the policy implication.

### 4.3 The Viability Gap is a Market Problem

The median viability gap of EUR 144,289 per unit far exceeds the total policy cost per unit of approximately EUR 70-100k. Even eliminating all policy costs would not close the gap for most counties. The gap must be closed through market-side changes: lower construction costs (modular, productivity), lower land costs (CPO, RZLT), lower finance costs (state lending), compressed margins (direct delivery), or higher sale prices (population growth, demand).

### 4.4 Developer Margin as a Policy-Market Boundary

The classification of developer margin as MARKET is the standard assumption in viability analysis (RICS, 2019; SCSI, 2021). However, the state can and does influence the effective margin through alternative delivery models. AHBs and the LDA operate at margins well below the 15% commercial benchmark. If margin were reclassified as partially policy-amenable, the policy-amenable share of total cost would rise to approximately 25-28%. The margin compression experiment (E13) shows that reducing margin from 15% to 10% brings Wicklow to within 0.2% of viability and saves EUR 22,000-25,000 per unit -- comparable to zeroing development contributions. This suggests that the state's choice of delivery model (speculative private vs direct public/AHB) is itself a significant "policy lever" that the POLICY/MARKET binary does not fully capture.

### 4.5 Limitations

1. **Static model**: does not capture dynamic effects of cost changes on supply/demand equilibrium. The 50% pass-through sensitivity (Section 3.8) partially addresses this but is itself a simplification -- actual pass-through rates are heterogeneous across locations and time periods.
2. **Tax capitalisation**: VAT reduction may be capitalised into land prices rather than reducing house prices (Crossley et al., 2012). The RZLT may partially offset this by penalising land hoarding.
3. **Part V cost estimation**: the fixed Part V estimates in the cost stack (EUR 5k-20k by region) are conservative upper bounds that exceed the computed cross-subsidy cost (Section 3.7). The true Part V cost per unit depends on the sale-price-to-cost-price gap, which varies by scheme.
4. **Land price data**: RZLPA02 county medians based on small transaction volumes; high variance
5. **Sale price assumptions**: new-build prices estimated from PPR data; actual scheme prices vary
6. **Density assumptions**: scheme density affects land cost per unit significantly
7. **No general equilibrium**: does not model second-round effects (e.g., more building reduces labour shortage)

## 5. Conclusion

Of total Irish residential development cost, policy-set costs (VAT, Part V, development contributions, BCAR, planning fees) account for 13-17%, with the remainder being market-driven. VAT is the single most impactful policy lever: zeroing it makes three counties viable under static pricing, but zero counties under a 50% pass-through assumption. If all policy costs were halved, three counties (Dublin, Wicklow, Kildare) would cross the viability frontier. If all policy costs were zeroed, four counties would be viable (static) or three (with pass-through). The viability gap fund needed to make all counties viable has a median of EUR 144,289 per unit -- computed from scheme-level costs -- implying a national cost of EUR 4.4 billion per year at the 33,000-unit target.

The central finding is that the Irish housing viability crisis cannot be solved through policy cost reduction alone. Market-driven costs -- materials, labour, land, finance, and developer margin -- constitute over 83% of total development cost and are the binding constraint on viability in 22 of 26 counties. Developer margin itself sits on the policy-market boundary: the state's choice of delivery model can compress it significantly, but this represents a structural reform rather than a parametric adjustment.

## References

See papers.csv for full citation list (210 entries). Key references:

- Buildcost.ie (2025). Construction Cost Guide H1 2025.
- CSO (2024). RZLPA02: Residentially Zoned Land Prices.
- CSO (2024). WPM28: Wholesale Price Index for Building Materials.
- CSO (2024). EHQ03: Earnings in Construction.
- Crossley, T., Phillips, D., Sherwood, M. (2012). The Effect of VAT on House Prices. JPublicEcon.
- Glaeser, E. & Gyourko, J. (2018). Tax Policy and Housing Supply. JUrbanEcon.
- SCSI (2021). Viability Study: Apartment Development in Dublin.
- SCSI (2020). BCAR Compliance Costs Survey.
- SCSI (2019). Development Contributions in Practice.
- Calavita, N. & Mallach, A. (2010). Inclusionary Housing. Lincoln Institute.
- Norris, M. & Shiels, P. (2007). Part V: An Assessment. JISS.
- RICS (2019). Financial Viability in Planning.
- McAllister, P. (2017). The Calculus of Consent in Viability Testing. JPP.
