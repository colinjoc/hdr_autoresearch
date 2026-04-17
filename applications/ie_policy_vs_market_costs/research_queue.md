# Research Queue

## Notation
- Prior: Bayesian prior probability of KEEP (0-1)
- Impact: Expected_Delta + Novelty + Mechanistic_clarity (3-9)
- Status: OPEN / RUN / KEEP / REVERT

| ID | Hypothesis | Prior | Impact | DV | Metric | Baseline | Status |
|:---|:---|:---|:---|:---|:---|:---|:---|
| H01 | VAT halved (to ~6.75%) makes Dublin viable | 0.6 | 7 | vat_rate | counties_viable | 0 | RUN |
| H02 | VAT zeroed makes Dublin+commuter viable | 0.7 | 8 | vat_rate | counties_viable | 0 | RUN |
| H03 | Part V halved makes no county flip | 0.7 | 6 | part_v_rate | counties_viable | 0 | RUN |
| H04 | Part V zeroed makes Dublin viable | 0.5 | 6 | part_v_rate | counties_viable | 0 | RUN |
| H05 | Dev contribs halved insufficient alone | 0.8 | 5 | dev_contributions_rate | counties_viable | 0 | RUN |
| H06 | BCAR halved negligible impact | 0.9 | 4 | bcar_rate | counties_viable | 0 | RUN |
| H07 | Planning fees zeroed negligible | 0.95 | 3 | planning_fees_rate | counties_viable | 0 | RUN |
| H08 | All policy halved makes 3+ counties viable | 0.6 | 8 | all_policy | counties_viable | 0 | RUN |
| H09 | All policy zeroed makes <6 counties viable | 0.5 | 9 | all_policy | counties_viable | 0 | RUN |
| H10 | VAT is the single most impactful policy lever | 0.7 | 8 | vat_rate | counties_delta | 0 | RUN |
| H11 | Dublin apt viability improves most from VAT removal | 0.6 | 7 | vat_rate | margin_change | baseline | RUN |
| H12 | Commuter belt most sensitive to dev contribs | 0.5 | 6 | dev_contributions_rate | margin_change | baseline | RUN |
| H13 | Regional cities most sensitive to Part V | 0.4 | 6 | part_v_rate | margin_change | baseline | RUN |
| H14 | Developer margin at 10% makes Dublin viable | 0.7 | 7 | margin_rate | counties_viable | 0 | RUN |
| H15 | Finance at 5% insufficient alone | 0.6 | 6 | finance_rate | counties_viable | 0 | RUN |
| H16 | Land at CPO price makes most counties viable | 0.8 | 9 | land_price | counties_viable | 0 | RUN |
| H17 | Modular -20% makes Dublin+commuter viable | 0.6 | 8 | build_cost | counties_viable | 0 | RUN |
| H18 | Modular + VAT reduction combined > sum of parts | 0.4 | 7 | combined | counties_viable | 0 | RUN |
| H19 | Viability gap fund median < EUR 100k | 0.3 | 6 | none | gap_median | none | RUN |
| H20 | Part V cross-subsidy makes remaining 80% unviable | 0.4 | 7 | part_v_mechanism | viability | baseline | RUN |
| H21 | Policy share varies <5pp across locations | 0.6 | 5 | none | policy_share_range | none | RUN |
| H22 | Dublin has highest policy share | 0.7 | 5 | none | policy_share | by_county | RUN |
| H23 | Land cost variation dominates county viability spread | 0.5 | 7 | none | regression_coeff | none | RUN |
| H24 | Sale price variation dominates county viability spread | 0.6 | 7 | none | regression_coeff | none | RUN |
| H25 | Combined policy+market reform makes 15+ counties viable | 0.4 | 8 | combined_reform | counties_viable | 0 | RUN |
| H26 | Bootstrap CI on policy share is tight (<2pp) | 0.7 | 4 | none | ci_width | none | OPEN |
| H27 | Sensitivity to build cost/sqm > sensitivity to any policy lever | 0.8 | 7 | build_cost | elasticity | none | RUN |
| H28 | International comparison: Ireland's policy burden is middling | 0.6 | 6 | none | ranking | none | OPEN |
| H29 | Equalising dev contribs to lowest LA rate makes 1 county flip | 0.3 | 5 | dev_contributions_rate | counties_delta | 0 | RUN |
| H30 | The viability gap increases monotonically with distance from Dublin | 0.6 | 5 | none | correlation | none | RUN |
| H31 | Apartment viability worse than house viability in every location | 0.7 | 5 | none | margin_comparison | none | RUN |
| H32 | 4-bed detached best viability profile | 0.6 | 4 | none | margin_comparison | none | RUN |
| H33 | EUR 50k subsidy makes Dublin viable | 0.8 | 6 | subsidy | viability | not_viable | RUN |
| H34 | EUR 150k subsidy makes 10 counties viable | 0.5 | 7 | subsidy | counties_viable | 0 | RUN |
| H35 | EUR 200k subsidy makes 20 counties viable | 0.4 | 7 | subsidy | counties_viable | 0 | RUN |
| H36 | The total national cost of viability gap fund > EUR 3bn/yr | 0.5 | 7 | none | total_cost | none | RUN |
| H37 | Part V delivery is <500 units/yr nationally | 0.5 | 5 | none | part_v_units | none | OPEN |
| H38 | VAT revenue from new housing > EUR 1bn/yr | 0.4 | 5 | none | vat_revenue | none | OPEN |
| H39 | VAT reduction self-financing via increased activity | 0.2 | 6 | dynamic_scoring | net_fiscal | none | OPEN |
| H40 | Pre/post-2014 BCAR cost differential < EUR 5k | 0.6 | 4 | bcar_regime | cost_delta | none | OPEN |
| H41 | Density (units/ha) is more important than per-unit land cost | 0.5 | 6 | density | viability | baseline | RUN |
| H42 | Apartment density advantage offset by higher build cost/sqm | 0.7 | 6 | dwelling_type | viability | none | RUN |
| H43 | Regional city viability requires EUR 100k+ subsidy | 0.7 | 6 | subsidy | viability | not_viable | RUN |
| H44 | Rural viability requires EUR 150k+ subsidy | 0.8 | 5 | subsidy | viability | not_viable | RUN |
| H45 | 10% build cost reduction > VAT zeroed for viability | 0.5 | 7 | build_cost | counties_delta | none | RUN |
| H46 | 20% build cost reduction > all policy zeroed for viability | 0.5 | 8 | build_cost | counties_delta | none | RUN |
| H47 | Land + build cost reform together makes 20+ counties viable | 0.4 | 8 | combined | counties_viable | 0 | RUN |
| H48 | Policy costs as % of sale price higher in Dublin than rural | 0.6 | 5 | none | policy_share_sale | by_location | RUN |
| H49 | Marginal tax rate on construction (all taxes) > 20% | 0.5 | 5 | none | effective_tax_rate | none | OPEN |
| H50 | Developer margin is the single largest soft cost component | 0.7 | 5 | none | component_ranking | none | RUN |
| H51 | Finance + margin together > all policy costs | 0.8 | 6 | none | cost_comparison | none | RUN |
| H52 | Hard cost share varies <10pp across locations | 0.6 | 4 | none | hard_share_range | none | RUN |
| H53 | Dublin land cost per unit < commuter due to higher density | 0.5 | 5 | none | land_per_unit | by_location | RUN |
| H54 | Leitrim's high land price is an outlier (few transactions) | 0.8 | 3 | none | data_quality | none | OPEN |
| H55 | Longford is the most unviable county | 0.6 | 4 | none | ranking | by_county | RUN |
| H56 | VAT reduction + Part V reduction is superadditive | 0.3 | 6 | interaction | counties_delta | sum_of_parts | RUN |
| H57 | Dev contrib + BCAR reduction is merely additive | 0.7 | 4 | interaction | counties_delta | sum_of_parts | RUN |
| H58 | Halving all policy costs saves EUR 40-60k per Dublin unit | 0.6 | 5 | all_policy | cost_saving | per_unit | RUN |
| H59 | Zeroing all policy costs saves EUR 80-120k per Dublin unit | 0.6 | 5 | all_policy | cost_saving | per_unit | RUN |
| H60 | Policy share is higher for apartments than houses | 0.7 | 5 | none | policy_share | by_type | RUN |
| H61 | VAT as % of total cost is stable across locations (within 1pp) | 0.5 | 4 | none | vat_share_range | none | RUN |
| H62 | Part V impact varies >3x between Dublin and rural | 0.7 | 5 | none | part_v_impact | by_location | RUN |
| H63 | Build cost/sqm is the dominant predictor of county viability | 0.4 | 6 | none | regression | viability | RUN |
| H64 | Sale price is the dominant predictor of county viability | 0.7 | 7 | none | regression | viability | RUN |
| H65 | Margin compression from 15% to 10% equivalent to VAT zeroed | 0.5 | 6 | margin | counties_delta | none | RUN |
| H66 | State finance at 3% + VAT zeroed makes Dublin + 3 counties viable | 0.5 | 7 | combined | counties_viable | 0 | RUN |
| H67 | The marginal county (closest to viability) is Wicklow | 0.6 | 5 | none | ranking | by_margin | RUN |
| H68 | Reducing build cost 10% is equivalent to ~EUR 30k per unit savings | 0.7 | 5 | build_cost | saving_per_unit | none | RUN |
| H69 | A EUR 25k per unit reduction in costs makes Wicklow viable | 0.8 | 5 | cost_reduction | viability | not_viable | RUN |
| H70 | Policy cost share increases with dwelling price level | 0.5 | 5 | none | correlation | none | RUN |
| H71 | Land cost as share of total is highest in Dublin | 0.5 | 5 | none | land_share | by_county | RUN |
| H72 | Land cost as share of total is lowest in Cavan (cheapest land) | 0.7 | 4 | none | land_share | by_county | RUN |
| H73 | Professional fees > BCAR + planning fees in every case | 0.9 | 3 | none | cost_comparison | none | RUN |
| H74 | Modular + CPO land + VAT zeroed makes >20 counties viable | 0.5 | 9 | combined_radical | counties_viable | 0 | RUN |
| H75 | Even with all reforms, Longford/Leitrim remain unviable | 0.4 | 5 | combined_radical | viability | none | RUN |
| H76 | Total policy cost in EUR is higher for Dublin than rural | 0.9 | 3 | none | policy_total | by_location | RUN |
| H77 | Total policy cost as % is higher for Dublin than rural | 0.7 | 4 | none | policy_share | by_location | RUN |
| H78 | The EUR per-unit cost saving from VAT zeroed > Part V zeroed everywhere | 0.7 | 5 | none | saving_comparison | by_location | RUN |
| H79 | Development contributions vary >3x across counties | 0.9 | 3 | none | dc_range | none | OPEN |
| H80 | The cost stack structure is similar across dwelling types | 0.6 | 4 | none | structure_similarity | none | RUN |
| H81 | Apartment viability worsens faster than house viability as we move from Dublin | 0.5 | 5 | none | margin_gradient | by_type | OPEN |
| H82 | A 2-bed apartment has higher policy share than a 3-bed semi | 0.7 | 4 | none | policy_share | by_type | RUN |
| H83 | The viability gap for apartments in Dublin < EUR 20k | 0.5 | 5 | none | gap | apt_dublin | RUN |
| H84 | Terraced houses have best viability profile (cheapest to build) | 0.4 | 4 | none | viability_ranking | by_type | RUN |
| H85 | Per-unit land cost for apartments < houses due to density | 0.8 | 4 | none | land_per_unit | by_type | RUN |
| H86 | The total viability gap fund for 30,000 units/yr > EUR 4bn | 0.6 | 7 | none | fund_total | national | RUN |
| H87 | Policy costs as % are fairly stable across dwelling types (<3pp range) | 0.5 | 4 | none | policy_share_range | by_type | RUN |
| H88 | Reducing finance costs from 8% to 3% equivalent to VAT halved | 0.5 | 5 | finance | counties_delta | vat_halved | RUN |
| H89 | VAT generates more revenue per unit than dev contribs in Dublin | 0.7 | 4 | none | revenue_comparison | none | RUN |
| H90 | Part V effective cost is higher in Dublin than regional (bigger cost-market gap) | 0.8 | 5 | none | part_v_cost | by_location | RUN |
| H91 | Hard costs > 50% of total in every location | 0.7 | 4 | none | hard_share | by_location | RUN |
| H92 | The model is robust to +/-10% variation in build cost/sqm | 0.6 | 5 | sensitivity | viable_count_range | none | OPEN |
| H93 | The model is robust to +/-10% variation in sale prices | 0.5 | 5 | sensitivity | viable_count_range | none | OPEN |
| H94 | International policy burden ranking: Ireland mid-table | 0.6 | 5 | none | ranking | international | OPEN |
| H95 | Labour cost inflation > material cost inflation in recent years | 0.7 | 4 | none | inflation_comparison | CSO data | OPEN |
| H96 | The break-even price for Dublin 3-bed semi = total dev cost = EUR ~590k | 0.8 | 5 | none | break_even | dublin | RUN |
| H97 | The break-even price for rural 3-bed semi > EUR 400k | 0.7 | 5 | none | break_even | rural | RUN |
| H98 | Tax wedge (all govt costs / sale price) > 15% in Dublin | 0.7 | 5 | none | tax_wedge | dublin | RUN |
| H99 | Abolishing ALL policy costs = EUR ~50k saving in Dublin | 0.3 | 5 | all_policy | saving_per_unit | dublin | RUN |
| H100 | Combined modular+CPO+all_policy_zeroed makes ALL counties viable | 0.3 | 9 | combined_radical | counties_viable | 0 | RUN |
| H101 | The marginal cost of Part V units exceeds their social value | 0.4 | 6 | none | cost_benefit | part_v | OPEN |
| H102 | Dev contribs are regressive (higher % of cost in cheaper locations) | 0.3 | 5 | none | regressivity | by_location | RUN |
| H103 | BCAR is the least impactful policy lever measured by viability delta | 0.5 | 4 | bcar | viability_delta | none | RUN |
| H104 | Planning fees + fire cert + disability cert total < EUR 2k per unit | 0.8 | 3 | none | fee_total | per_unit | RUN |
| H105 | Halving all costs equally (market+policy) is more effective than zeroing policy alone | 0.7 | 7 | combined | counties_viable | none | RUN |
