# Research Queue: U-3 Infrastructure Capacity Blocks

## Format: ID | Hypothesis | Prior | Mechanism | Design Variable | Metric | Baseline | Status

### Core Hypotheses (High Impact)

1. H01 | >25% of WWTP catchments are RED or AMBER | 0.7 | Capacity register shows direct classification | capacity_status | pct_constrained | 0% | RUN → KEEP (25.7%)
2. H02 | Dublin is less constrained than national average | 0.6 | Ringsend upgrade completed | county_filter=Dublin | pct_constrained | 25.7% | RUN → KEEP (12.5%)
3. H03 | Kerry has highest constraint rate | 0.5 | Rural county with many small plants | county_ranking | pct_red | national avg | RUN → KEEP (37.5% RED)
4. H04 | No county exceeds 50% RED | 0.4 | Even worst counties have some green | threshold=50% | n_counties | 0 | RUN → KEEP (0 counties >50%)
5. H05 | >1000 hectares of zoned land in RED/AMBER catchments | 0.6 | 25.7% of 7911 ha | county_weighted | blocked_ha | 0 | RUN → KEEP (1524 ha)
6. H06 | Majority of RED plants lack upgrade projects | 0.7 | Investment pipeline limited | project_planned | pct_without_project | 0% | RUN → KEEP (74.4%)
7. H07 | Commuter belt counties are meaningfully constrained | 0.5 | Growth pressure meets limited infrastructure | county_filter | pct_constrained | 25.7% | RUN → KEEP (17.6%)
8. H08 | AMBER classification materially changes blocked estimate | 0.6 | AMBER adds uncertainty | amber_treatment | difference_ha | 0 | RUN → KEEP (570 ha difference)
9. H09 | Large plants more constrained than small | 0.4 | Urban plants face more demand pressure | reg_prefix | pct_constrained | 25.7% | RUN → KEEP (30.8% vs 20.3%)
10. H10 | Correlation between demand and constraints is positive | 0.5 | Growing areas strain capacity | correlation | r_value | 0 | RUN → KEEP (r=0.189)

### Viability Overlap Hypotheses

11. H11 | >15% of zoned land is double-stranded | 0.5 | Independence assumption for two constraints | overlap_calc | pct_double | 0% | RUN → KEEP (16.0%)
12. H12 | Double-stranding is concentrated in specific counties | 0.6 | Both constraints cluster spatially | county_breakdown | concentration | uniform | RUN → KEEP
13. H13 | Cork has the most blocked hectares in absolute terms | 0.5 | Large county with high constraint rate | county_ranking | blocked_ha | 0 | RUN → KEEP (305 ha)
14. H14 | Settlement-level and county-level aggregation agree | 0.7 | Methodology check | aggregation_level | difference_pp | 0 | RUN → KEEP (0.0 pp difference)

### Investment Priority Hypotheses

15. H15 | Top 5 counties account for >50% of blocked hectares | 0.6 | Constraint concentration | county_ranking | cumulative_pct | uniform | RUN → KEEP
16. H16 | Upgrading all RED-with-project plants would unlock significant land | 0.5 | Projects already planned | project_filter | unlocked_ha | 0 | RUN → KEEP
17. H17 | Cost per hectare unlocked varies >10x across counties | 0.4 | Investment efficiency varies | cost_per_ha | ratio | 1 | OPEN
18. H18 | Prioritising by housing output differs from prioritising by constraint | 0.7 | Different objectives, different rankings | ranking_method | rank_correlation | 1 | OPEN

### Refusal Rate and Planning Hypotheses

19. H19 | Constrained areas have higher refusal rates | 0.5 | Infrastructure cited as refusal reason | constraint_level | refusal_rate | baseline | RUN → REVERT (opposite found)
20. H20 | The refusal rate finding is driven by composition (rural vs urban) | 0.8 | Rural areas have simpler applications | county_type | refusal_rate | pooled | RUN → KEEP
21. H21 | Residential applications are declining in RED areas | 0.4 | Developers avoid constrained areas | time_trend | slope | 0 | RUN → KEEP
22. H22 | One-off houses are concentrated in constrained counties | 0.5 | Alternative to WWTP-connected development | one_off_share | correlation | 0 | OPEN
23. H23 | Apartment schemes are rarer in constrained areas | 0.4 | Apartments have higher WWTP load per unit | apartment_share | correlation | 0 | OPEN

### International Comparison Hypotheses

24. H24 | Ireland's 25.7% is less severe than UK nutrient neutrality | 0.5 | UK affects 74 LPAs | comparison | relative_severity | 1:1 | RUN → KEEP
25. H25 | Ireland's constraint is more targeted than Netherlands nitrogen | 0.7 | NL affects all construction | scope_comparison | breadth | equal | RUN → KEEP
26. H26 | NZ three waters reform cost suggests Ireland's EUR 10.3bn is adequate | 0.4 | Scale comparison | investment_ratio | per_capita | NZ benchmark | OPEN
27. H27 | UK Levelling Up Act override approach could apply to Ireland | 0.3 | Political feasibility | policy_comparison | applicability | baseline | OPEN

### UWWTD Compliance Hypotheses

28. H28 | Large plants have lower RED rate than small plants under UWWTD | 0.4 | More investment in regulated plants | uwwtd_filter | pct_red | overall | RUN → KEEP (12.1% vs 15.4%)
29. H29 | Recast UWWTD will increase number of constrained plants | 0.6 | New requirements raise the bar | scenario_analysis | delta_constrained | 0 | OPEN
30. H30 | Compliance and capacity correlate | 0.5 | Plants failing on quality also failing on capacity | correlation | r_value | 0 | OPEN

### Temporal and Dynamic Hypotheses

31. H31 | Applications are shifting from RED to GREEN counties over time | 0.4 | Market response to constraints | time_trend | migration_rate | 0 | OPEN
32. H32 | Post-2020 application trends differ by constraint status | 0.5 | COVID and construction boom effects | period_comparison | trend_difference | 0 | RUN → KEEP
33. H33 | Counties with projects planned show faster application growth | 0.3 | Anticipation effects | project_status | growth_rate | baseline | OPEN
34. H34 | ESB connection rates are lower in constrained counties | 0.5 | Completions track capacity | connections | correlation | 0 | OPEN

### Sensitivity and Robustness Hypotheses

35. H35 | Results robust to excluding Dublin entirely | 0.8 | Dublin has few constraints | dublin_excl | pct_constrained | 25.7% | OPEN
36. H36 | Results robust to excluding one-off houses | 0.7 | One-offs use septic tanks | one_off_excl | pct_constrained | 25.7% | OPEN
37. H37 | Results robust to treating AMBER as GREEN | 0.6 | Conservative scenario | amber_as_green | blocked_ha | 1524 | RUN → KEEP (954 ha)
38. H38 | Results robust to 20% variation in zoned land estimates | 0.8 | Goodbody figures are approximate | zoned_land_range | blocked_ha_range | 1524 | OPEN
39. H39 | Weighted by settlement population gives different results | 0.5 | Large settlements dominate | weighting | pct_constrained | 25.7% | OPEN
40. H40 | Bootstrap CI on national headline is narrow | 0.7 | 1063 observations, clear classification | bootstrap | ci_width | 0 | OPEN

### Supply Chain Hypotheses

41. H41 | WWTP upgrade costs have inflated >50% since 2019 | 0.6 | Construction cost inflation | cost_index | pct_change | 0% | OPEN
42. H42 | Labour shortage is a binding constraint on WWTP delivery | 0.5 | Skilled trades shortage | capacity_analysis | constraint_type | financial | OPEN
43. H43 | Modular treatment solutions could address small RED plants | 0.4 | Technology alternative | plant_size_filter | applicable_pct | 0% | OPEN
44. H44 | Private developer-funded WWTPs are underused in Ireland | 0.5 | New policy announced Nov 2025 | policy_analysis | utilisation | 0 | OPEN

### Cross-Study Integration Hypotheses

45. H45 | Infrastructure constraint adds to viability constraint, not substitutes | 0.7 | Different mechanisms | overlap_type | interaction | additive | RUN → KEEP
46. H46 | Planning permission rate (U-1) is lower in constrained areas | 0.5 | Additional constraint reduces grants | cross_study | grant_rate | baseline | RUN → REVERT (opposite)
47. H47 | S-3 bottleneck ranking changes when infrastructure is included | 0.4 | New constraint dimension | ranking_update | rank_change | 0 | OPEN
48. H48 | Total effective zoned land after all constraints <2000 ha | 0.3 | Cumulative deductions | cascade | residual_ha | 7911 | OPEN

### Geographic Pattern Hypotheses

49. H49 | Coastal counties more constrained than inland | 0.4 | Discharge sensitivity in coastal waters | coastal_filter | pct_constrained | 25.7% | OPEN
50. H50 | Border counties (Donegal, Cavan, Monaghan) are highly constrained | 0.6 | Historical underinvestment | border_filter | pct_constrained | 25.7% | RUN → KEEP (>30%)
51. H51 | Shannon basin counties share common constraint patterns | 0.3 | River basin effects | basin_filter | commonality | independent | OPEN
52. H52 | EMRA region is less constrained than NWRA | 0.6 | More investment in east | regional_comparison | pct_constrained | equal | OPEN
53. H53 | University towns have lower constraint rates | 0.4 | Growth areas received investment | university_filter | pct_constrained | 25.7% | OPEN

### Population and Demand Hypotheses

54. H54 | Fastest-growing settlements are disproportionately constrained | 0.5 | Growth outstrips capacity | growth_rate | correlation | 0 | OPEN
55. H55 | Settlements <2000 population are more likely RED | 0.4 | Small plants less investment priority | pop_filter | pct_red | 15.4% | OPEN
56. H56 | Social housing sites are in constrained catchments | 0.3 | Public land in secondary locations | tenure_filter | pct_constrained | 25.7% | OPEN
57. H57 | Student accommodation not affected (within existing urban networks) | 0.6 | Urban infill uses existing capacity | use_class | affected_pct | 25.7% | OPEN

### Policy Response Hypotheses

58. H58 | EUR 10.3bn is sufficient to address all RED plants by 2029 | 0.3 | Optimistic timeline given delays | investment_analysis | coverage_pct | 0% | OPEN
59. H59 | Accelerated Growth Programme targets highest-blocked counties | 0.4 | Political vs technical prioritisation | programme_analysis | alignment | 0 | OPEN
60. H60 | Connection charges do not reflect true capacity costs | 0.7 | Cross-subsidy from existing users | charge_analysis | cost_recovery | 100% | OPEN

### Methodological Hypotheses

61. H61 | Fuzzy matching of settlement names achieves >80% match rate | 0.4 | Name inconsistencies | fuzzy_matching | match_rate | 0% | OPEN
62. H62 | County-level results are insensitive to matching method | 0.7 | Aggregation smooths errors | method_sensitivity | difference_pp | 0 | RUN → KEEP
63. H63 | Results replicate if we use different county zoned-land allocations | 0.7 | Proportional vs equal allocation | allocation_method | difference_ha | 0 | OPEN
64. H64 | Excluding HTML-parsed data errors doesn't change headlines | 0.8 | Data quality check | error_exclusion | pct_change | 0% | OPEN

### Long-Shot Hypotheses (Prior ≤ 0.3)

65. H65 | WWTP status predicts house prices controlling for county | 0.2 | Capitalisation of constraint | hedonic_model | coefficient | 0 | OPEN
66. H66 | RED status causes developer land banking | 0.2 | Strategic behaviour | banking_analysis | correlation | 0 | OPEN
67. H67 | Climate change adaptation will worsen capacity constraints | 0.3 | Increased rainfall → infiltration | climate_scenario | delta_capacity | 0 | OPEN
68. H68 | Circular economy approaches could reduce WWTP loading | 0.2 | Grey water recycling, composting toilets | tech_analysis | load_reduction | 0% | OPEN
69. H69 | WWTP constraint correlates with broadband deficit | 0.2 | Common infrastructure underinvestment | cross_infra | correlation | 0 | OPEN
70. H70 | Agricultural runoff contributes to WWTP overloading | 0.3 | Non-point source loading | agriculture_analysis | contribution_pct | 0% | OPEN
71. H71 | Tourism-heavy areas have seasonal capacity issues | 0.3 | Summer population surge | tourism_filter | seasonal_variation | 0 | OPEN
72. H72 | Blockchain/smart metering could improve capacity management | 0.1 | Technology speculation | tech_assessment | feasibility | 0 | OPEN
73. H73 | Decentralised treatment could bypass RED WWTPs | 0.3 | Package treatment plants | decentral_analysis | applicable_pct | 0% | OPEN
74. H74 | WWTP emissions contribute to local air quality issues | 0.2 | Secondary environmental effect | emission_analysis | impact | 0 | OPEN
75. H75 | Insurance costs higher in RED catchment areas | 0.2 | Risk pricing | insurance_analysis | premium_diff | 0 | OPEN

### Interaction Hypotheses

76. H76 | RED status × high demand = development displacement | 0.5 | Combined effect exceeds sum | interaction | displacement_rate | additive | OPEN
77. H77 | AMBER × project planned = effectively GREEN | 0.4 | Anticipation of upgrade | interaction | grant_rate | amber_alone | OPEN
78. H78 | Viability constraint × infrastructure constraint = permanent sterilisation | 0.3 | No mechanism to resolve both | interaction | development_rate | single_constraint | OPEN
79. H79 | Rural × RED = one-off house substitution | 0.5 | Alternative available | interaction | one_off_rate | urban_red | OPEN
80. H80 | Urban × RED = price inflation in adjacent GREEN areas | 0.3 | Demand spillover | interaction | price_change | no_red | OPEN

### Data Quality and Validation Hypotheses

81. H81 | HTML scraping captured all 1063 plants correctly | 0.8 | Cross-check with published totals | validation | error_rate | 0% | RUN → KEEP
82. H82 | County boundaries match between WW register and planning register | 0.9 | Standard administrative boundaries | validation | mismatch_rate | 0% | RUN → KEEP
83. H83 | GREEN/AMBER/RED classification is consistent across source pages | 0.7 | CSS color parsing | validation | inconsistency_rate | 0% | OPEN
84. H84 | Project planned flag is reliable | 0.5 | May be outdated | validation | accuracy | 100% | OPEN
85. H85 | Some plants classified RED may have been recently upgraded | 0.3 | Snapshot timing | validation | false_positive_rate | 0% | OPEN

### Extension Hypotheses

86. H86 | Drinking water capacity is also a binding constraint | 0.5 | Same utility, different asset class | cross_asset | correlation | 0 | OPEN
87. H87 | Stormwater/surface water drainage is separately constraining | 0.4 | SuDS requirements | drainage_analysis | constraint_rate | 0% | OPEN
88. H88 | Road infrastructure constraints compound water constraints | 0.3 | Multiple infrastructure deficits | compound_analysis | interaction | additive | OPEN
89. H89 | Electricity grid capacity is also binding in some areas | 0.4 | EirGrid capacity | grid_analysis | constraint_rate | 0% | OPEN
90. H90 | Schools and healthcare capacity interact with housing constraints | 0.3 | Social infrastructure | social_infra | correlation | 0 | OPEN

### Quantification Refinement Hypotheses

91. H91 | Population-weighted constraint rate differs from plant-count-weighted | 0.5 | Large settlements underweighted by plant count | weighting_method | difference_pp | 0 | OPEN
92. H92 | Design PE data would improve hectare estimates | 0.6 | Capacity proportional to PE | data_enhancement | precision_gain | 0 | OPEN
93. H93 | Spatial join with zoning shapefiles would replace county proportions | 0.5 | Direct overlap measurement | spatial_analysis | accuracy_gain | 0 | OPEN
94. H94 | Goodbody zoned land figures are overstated | 0.4 | Some zoned land has other constraints | validation | overstatement_pct | 0% | OPEN
95. H95 | Effective development capacity is <50% of zoned land after all constraints | 0.6 | Cumulative deductions | cascade_analysis | residual_pct | 100% | OPEN
96. H96 | Per-settlement capacity data (PE) would change county rankings | 0.4 | Size distribution matters | data_enhancement | rank_change | 0 | OPEN
97. H97 | Regional Spatial Strategy growth targets align with GREEN catchments | 0.4 | Policy coherence check | policy_analysis | alignment_pct | 100% | OPEN
98. H98 | Zoned land in RED catchments has lower site values | 0.3 | Market discounts constraint | valuation_analysis | discount_pct | 0% | OPEN
99. H99 | Multi-authority catchments create coordination failures | 0.3 | Governance complexity | governance_analysis | affected_pct | 0% | OPEN
100. H100 | Total housing units blocked by infrastructure >50,000 | 0.4 | 1524 ha × ~33 units/ha | unit_calculation | total_units | 0 | OPEN
101. H101 | Investment priority ranking is robust to alternative weighting schemes | 0.6 | Sensitivity check | ranking_robustness | rank_correlation | 1 | OPEN
102. H102 | Seasonal WWTP loading data would refine capacity classification | 0.5 | Summer vs winter loads differ | temporal_refinement | reclassification_pct | 0% | OPEN
103. H103 | Cross-referencing EPA Priority Action List with RED plants yields >80% overlap | 0.5 | Regulatory and operational alignment | cross_reference | overlap_pct | 0% | OPEN
