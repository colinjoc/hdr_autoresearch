# Research Queue — Development Viability Frontier

## Format: ID | Prior | Impact | Status | Hypothesis | Design Variable | Metric | Baseline

### Core Viability
H001 | 0.90 | 9 | OPEN | Development is unviable in the majority of Irish counties at median land and construction costs | All defaults | fraction_unviable | E00
H002 | 0.80 | 8 | OPEN | Dublin is the least unviable county due to highest sale prices | Sale price by county | margin_pct | E00
H003 | 0.70 | 8 | OPEN | Construction cost is a larger drag on viability than land cost in most counties | Construction cost vs land cost share | cost_share_pct | E00
H004 | 0.60 | 7 | OPEN | Dublin vs non-Dublin viability gap exceeds 20 percentage points | Regional split | margin_gap_pp | E00
H005 | 0.75 | 8 | OPEN | Apartment viability differs structurally from house viability (higher density offsets higher per-sqm cost) | House type/density | margin_pct | E00

### Sensitivity Analysis
H006 | 0.85 | 7 | OPEN | ±25% land cost change flips viability in 3+ counties | land_cost_per_ha ±25% | counties_flipped | E00
H007 | 0.80 | 8 | OPEN | ±15% construction cost change has larger impact than ±25% land cost change | construction_cost ±15% | margin_delta | E00
H008 | 0.65 | 7 | OPEN | Finance rate sensitivity: 5% vs 12% rate changes margin by >10pp | finance_rate | margin_pct | E00
H009 | 0.70 | 7 | OPEN | Build duration sensitivity: 1.5yr vs 4yr changes margin by >8pp | build_duration | margin_pct | E00
H010 | 0.60 | 6 | OPEN | Developer margin squeeze from 20% to 15% flips 2+ counties to viable | profit_margin | counties_viable | E00

### Part V and Development Contributions
H011 | 0.75 | 8 | OPEN | Part V at 20% reduces viability margin by 5-10pp vs 0% obligation | part_v_pct | margin_pct | E00
H012 | 0.70 | 7 | OPEN | Development contribution variation across LAs creates >5pp viability spread | dev_contributions | margin_spread | E00
H013 | 0.50 | 6 | OPEN | Removing Part V + halving dev contributions is insufficient to make most counties viable | combined | counties_viable | E00
H014 | 0.60 | 7 | OPEN | Part V impact is regressive — hurts less viable counties disproportionately | part_v interaction with county | margin_delta_by_county | E00

### Temporal Analysis
H015 | 0.80 | 8 | OPEN | Viability has deteriorated since 2015 (costs rising faster than prices) | year (2015-2025) | margin_pct_trajectory | E00
H016 | 0.70 | 7 | OPEN | 2020-2022 was the peak viability period (prices rising, costs lagging) | year | margin_pct | E00
H017 | 0.60 | 7 | OPEN | Some counties flipped from viable to unviable between 2015 and 2025 | year × county | flip_count | E00
H018 | 0.55 | 6 | OPEN | Construction cost inflation trajectory is steeper than price appreciation in 2023-2025 | BEA04 vs HPM09 | cost_price_ratio_change | E00
H019 | 0.65 | 7 | OPEN | Developer margin has been squeezed by >10pp between 2018 and 2025 | year | margin_pct | E00

### Spatial Analysis
H020 | 0.85 | 9 | OPEN | Counties within commuting distance of Dublin (Kildare, Meath, Wicklow, Louth) are more viable than remote counties | distance_to_dublin | margin_pct | E00
H021 | 0.70 | 8 | OPEN | A spatial viability frontier exists — clear geographic boundary between viable and unviable areas | county classification | viability_map | E00
H022 | 0.50 | 7 | OPEN | The viability frontier has shifted inward (toward Dublin) over time | frontier_boundary × year | frontier_shift | E00
H023 | 0.60 | 6 | OPEN | NUTS3 regions explain >60% of viability variance | region dummies | R2 | E00

### Stranded Land
H024 | 0.80 | 9 | OPEN | More than 3,000 hectares of zoned residential land sit in unviable areas | zoned_ha × viability | stranded_ha | E00
H025 | 0.75 | 8 | OPEN | More than 100,000 potential units are stranded on unviable land | units × viability | stranded_units | E00
H026 | 0.70 | 7 | OPEN | RZLT will impose costs on landowners whose land is unviable to develop | RZLT × viability | rzlt_unviable_ha | E00
H027 | 0.60 | 7 | OPEN | The counties with the most stranded hectares are not the most populated | zoned_ha × pop | correlation | E00

### Housing for All Price Caps
H028 | 0.65 | 7 | OPEN | Viability at Housing for All price caps (€250k-€325k) is negative in all counties | price_cap | margin_pct | E00
H029 | 0.55 | 6 | OPEN | Price caps require state subsidy of >€80k/unit to achieve viability in GDA | subsidy_needed | eur_per_unit | E00
H030 | 0.50 | 6 | OPEN | Cost-rental viability (lower rent capitalisation) requires >30% subsidy | cost_rental | subsidy_pct | E00

### Scale Effects
H031 | 0.55 | 6 | OPEN | Larger sites (>5ha) achieve better viability through economies of scale | site_size | margin_pct | E00
H032 | 0.50 | 5 | OPEN | Higher density (>60 units/ha) improves viability by spreading land cost | density | margin_pct | E00
H033 | 0.45 | 5 | OPEN | Apartment schemes at 100 units/ha are viable in Dublin but not elsewhere | density × county | viable | E00

### House Type Analysis
H034 | 0.60 | 6 | OPEN | Starter homes (75sqm 2-bed) are more viable than family homes (115sqm 4-bed) | avg_sqm | margin_pct | E00
H035 | 0.55 | 6 | OPEN | Detached bungalows are the least viable type despite lower per-sqm cost (larger footprint) | house_type | margin_pct | E00
H036 | 0.50 | 5 | OPEN | 3-bed semi is the most viable type nationally (optimal size-cost-price balance) | house_type | margin_pct | E00

### Rural/One-Off Analysis
H037 | 0.40 | 5 | OPEN | One-off rural houses have different viability structure (no density, lower land cost, self-build) | one_off parameters | margin_pct | E00
H038 | 0.35 | 5 | OPEN | Self-build is viable where developer-led is not (no profit margin, lower spec) | self_build_params | margin_pct | E00

### Correlation with Activity
H039 | 0.65 | 8 | OPEN | Viability margin correlates positively with planning application rate (from U-1) | margin × app_rate | correlation_r | E00
H040 | 0.55 | 7 | OPEN | Counties that flipped from viable to unviable show declining application rates | flip × app_trend | correlation | E00
H041 | 0.50 | 6 | OPEN | ESB connections (NDQ04) correlate with viability better than with zoned land area | NDQ04 × viability | correlation_r | E00

### Monte Carlo / Uncertainty
H042 | 0.80 | 7 | OPEN | Monte Carlo simulation shows viability margin 95% CI spans >30pp for any given county | MC simulation | ci_width | E00
H043 | 0.70 | 7 | OPEN | Construction cost is the highest-sensitivity parameter in Monte Carlo | MC sensitivity | tornado_rank | E00
H044 | 0.60 | 6 | OPEN | Sale price × construction cost interaction dominates the uncertainty | MC interaction | joint_sensitivity | E00
H045 | 0.55 | 6 | OPEN | At 90th percentile optimistic assumptions, Dublin becomes viable | MC percentile | viable_at_p90 | E00

### Policy Scenarios
H046 | 0.50 | 7 | OPEN | Waiving development contributions makes 3+ counties viable | dev_contrib=0 | counties_viable | E00
H047 | 0.45 | 7 | OPEN | State construction cost reduction of 20% (modular/industrialised) makes 5+ counties viable | construction_cost×0.8 | counties_viable | E00
H048 | 0.40 | 6 | OPEN | Combining Part V waiver + dev contrib waiver + 15% construction cost reduction makes majority viable | combined policy | counties_viable | E00
H049 | 0.55 | 7 | OPEN | RZLT at 3% adds meaningful pressure only when land is held >3 years | RZLT×holding_period | marginal_cost | E00
H050 | 0.50 | 6 | OPEN | Increasing density to 60 u/ha (from 40) has larger impact than reducing construction cost by 10% | density vs cost | margin_delta | E00

### Panel Regression
H051 | 0.70 | 7 | OPEN | Panel regression: region fixed effects explain >40% of viability variance | region FE | R2 | E00
H052 | 0.60 | 6 | OPEN | Year fixed effects capture cost-inflation trajectory in panel model | year FE | coeff_significance | E00
H053 | 0.55 | 6 | OPEN | House type interaction with region is significant (apartments viable in cities, not rural) | type×region | interaction_p | E00
H054 | 0.50 | 5 | OPEN | Random effects model preferred over fixed effects (Hausman test) | RE vs FE | hausman_p | E00

### Threshold Models
H055 | 0.65 | 7 | OPEN | A clear sale-price threshold exists below which no county is viable | threshold model | threshold_eur | E00
H056 | 0.60 | 7 | OPEN | The break-even sale price varies by >€200k across counties | break_even | spread | E00
H057 | 0.55 | 6 | OPEN | Construction cost threshold: above €2,800/sqm, viability requires sale price >€400k | cost threshold | price_required | E00
H058 | 0.50 | 6 | OPEN | Land cost threshold: above €800k/ha at 40u/ha, viability requires premium location | land threshold | premium_needed | E00

### Break-Even Analysis
H059 | 0.75 | 8 | OPEN | Break-even sale price exceeds current median price in every county | break_even vs median | excess_count | E00
H060 | 0.65 | 7 | OPEN | Dublin's break-even is ~€550-600k, implying only top-30% of market supports new development | dublin_breakeven | percentile | E00
H061 | 0.55 | 6 | OPEN | Break-even analysis reveals that new build requires prices 20-50% above current medians | all counties | premium_pct | E00

### International Comparison
H062 | 0.50 | 5 | OPEN | Ireland's cost-to-price ratio is higher than UK average | international | ratio_comparison | literature
H063 | 0.45 | 5 | OPEN | Ireland's viability crisis is more acute than England's | international | margin_comparison | literature

### RZLT Interaction
H064 | 0.60 | 7 | OPEN | RZLT will increase holding cost enough to force some land sales at below-reservation price | RZLT effect | price_reduction | E00
H065 | 0.55 | 6 | OPEN | If RZLT reduces land prices by 10%, viability improves but remains negative for most counties | RZLT×land_price | margin_pct | E00
H066 | 0.50 | 6 | OPEN | RZLT burden falls disproportionately on counties where land is already unviable | RZLT×viability | rzlt_cost_by_class | E00

### Predecessor Integration
H067 | 0.70 | 8 | OPEN | U-1 application rate per hectare correlates with viability margin (r > 0.5) | app_rate × margin | correlation | E00
H068 | 0.60 | 7 | OPEN | S-1 build-yield of 59.6% further reduces effective viability (not all permissions complete) | pipeline_yield | effective_margin | E00
H069 | 0.55 | 6 | OPEN | Fingal's low app rate (0.08/ha/yr from U-1) is explained by its viability position | fingal analysis | margin vs rate | E00

### Robustness Checks
H070 | 0.80 | 6 | OPEN | Results robust to using mean instead of median land prices | mean vs median | margin_change | E00
H071 | 0.75 | 6 | OPEN | Results robust to ±10% variation in assumed unit size | avg_sqm ±10% | margin_change | E00
H072 | 0.80 | 6 | OPEN | Results robust to using HPA06 annual RPPI instead of HPM09 monthly | data source | margin_change | E00
H073 | 0.70 | 5 | OPEN | Bootstrap 95% CI on national margin excludes zero | bootstrap | ci_includes_zero | E00
H074 | 0.60 | 5 | OPEN | Removing counties with <5 RZLPA02 transactions does not change main findings | sample restriction | margin_change | E00

### Long-Shot Hypotheses (prior ≤ 0.3)
H075 | 0.20 | 5 | OPEN | There exists a county where development is currently viable at median costs | all parameters | any_viable | E00
H076 | 0.25 | 6 | OPEN | Modular construction (30% cost reduction) makes all counties viable | modular_cost | all_viable | E00
H077 | 0.15 | 5 | OPEN | Zero-land-cost (state-provided land) makes all counties viable | land=0 | all_viable | E00
H078 | 0.30 | 5 | OPEN | Developer margin of 10% (below industry minimum) makes 50%+ counties viable | margin=0.10 | pct_viable | E00
H079 | 0.20 | 6 | OPEN | Combined maximum optimistic scenario makes <50% of counties viable | all optimistic | pct_viable | E00
H080 | 0.25 | 5 | OPEN | Apartment viability in Dublin at 100 u/ha and €450k sale price is positive | apartment params | viable | E00
H081 | 0.10 | 4 | OPEN | Construction costs will decrease in real terms by 2027 | forecast | cost_trajectory | literature
H082 | 0.20 | 5 | OPEN | Viability improved between 2023 and 2025 (prices rose faster than costs) | temporal | margin_change | E00
H083 | 0.15 | 4 | OPEN | Remote working has improved viability outside Dublin by raising rural sale prices | WFH effect | rural_margin | E00
H084 | 0.25 | 5 | OPEN | The viability crisis is primarily a land-cost problem not a construction-cost problem | decomposition | cost_share | E00
H085 | 0.30 | 5 | OPEN | Reducing avg unit size to 80sqm makes Dublin viable | size=80 | dublin_viable | E00

### Additional Experiments
H086 | 0.60 | 6 | OPEN | Break-even density (units/ha needed for viability) varies from 30 to 150+ across counties | density_breakeven | density_needed | E00
H087 | 0.55 | 6 | OPEN | The "viability gap" (subsidy needed per unit) ranges from €0 to >€200k by county | subsidy_needed | gap_range | E00
H088 | 0.50 | 5 | OPEN | Including VAT at 13.5% on construction makes viability worse by 5-8pp | VAT | margin_change | E00
H089 | 0.45 | 5 | OPEN | Professional fees (12% of construction) have minimal marginal impact vs construction cost itself | fees | margin_sensitivity | E00
H090 | 0.65 | 7 | OPEN | The national viability-weighted stranded hectares figure exceeds 5,000 ha | stranded analysis | ha_total | E00
H091 | 0.60 | 6 | OPEN | Stranded potential units exceed 200,000 | stranded analysis | units_total | E00
H092 | 0.55 | 6 | OPEN | If viability improved to make all land developable, pipeline capacity would exceed Housing for All target | counterfactual | potential_units_yr | E00
H093 | 0.50 | 5 | OPEN | Counties with highest RZLT burden relative to viability are those most likely to see rezoning | RZLT/viability | rezoning_prediction | E00
H094 | 0.45 | 5 | OPEN | The median sale price needed nationally for viability at current costs is ~€470k | break_even_national | price_needed | E00
H095 | 0.70 | 7 | OPEN | Construction cost per sqm correlates with building production index trajectory | BEA04 × buildcost | calibration_r | E00
H096 | 0.40 | 5 | OPEN | Inflation at 5%/yr on costs for 3 years of build-out worsens margin by >5pp | inflation | margin_delta | E00
H097 | 0.60 | 6 | OPEN | Using mean land prices (instead of median) worsens viability uniformly | mean vs median | direction | E00
H098 | 0.55 | 6 | OPEN | The top 5 counties by viability margin are all in the GDA or major cities | ranking | top5_list | E00
H099 | 0.50 | 5 | OPEN | Cost-rental viability at €1,200/month rent capitalised requires >40% state subsidy | cost_rental | subsidy_pct | E00
H100 | 0.65 | 7 | OPEN | The viability map shows a clear east-west gradient matching Ireland's economic geography | spatial | gradient_test | E00
H101 | 0.45 | 5 | OPEN | Reducing profit margin to 12% (construction-company model vs developer model) flips 3+ counties | margin=0.12 | counties_flipped | E00
H102 | 0.30 | 5 | OPEN | Site remediation costs (brownfield premium of €20-50k/unit) make urban infill less viable than greenfield | remediation | margin_delta | E00
H103 | 0.55 | 6 | OPEN | Energy efficiency requirements (NZEB) add €15-25k per unit to construction costs | nzeb_cost | margin_impact | literature
H104 | 0.40 | 5 | OPEN | Social housing direct build by local authorities avoids profit margin requirement | social build | cost_comparison | E00
H105 | 0.50 | 6 | OPEN | The viability frontier has policy implications: RZLT should be conditional on viability | policy | recommendation | analysis
