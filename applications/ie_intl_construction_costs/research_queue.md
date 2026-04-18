# Research Queue: Irish International Construction Cost Comparison

## Format
Each hypothesis: ID | Prior (0-1) | Impact (3-9) | Status | Hypothesis | Design Variable | Expected Outcome | Metric | Baseline

## Hypotheses

### Growth Rate Analysis
H01 | 0.3 | 9 | TESTED-KEEP | Ireland has the highest construction cost growth in Europe 2015-2025 | country | IE ranked #1 | rank | T01 result: IE is #6/10
H02 | 0.5 | 8 | TESTED-KEEP | Ireland's growth rate is above EU-10 average | growth_diff | positive | pct_diff | E04 result: IE is -4.9pp BELOW average
H03 | 0.6 | 7 | TESTED-KEEP | Germany and Netherlands are fastest-growing | country | DE+NL top 2 | rank | Confirmed: DE #1 (+74.7%), NL #2 (+71.2%)
H04 | 0.7 | 6 | TESTED-KEEP | Pre-COVID Ireland was already diverging from EU | subperiod | IE above avg pre-2020 | growth_diff | E05: IE BELOW avg pre-COVID (+9.7% vs +11.4%)
H05 | 0.5 | 7 | TESTED-KEEP | COVID impact hit Ireland harder than comparators | shock_period | IE above avg 2020-21 | growth_diff | E06: IE at average during COVID (+9.6% vs +9.9%)
H06 | 0.5 | 7 | TESTED-KEEP | Ukraine/energy crisis hit Ireland harder | shock_period | IE above avg 2022-23 | growth_diff | E07: IE BELOW avg during Ukraine (+9.9% vs +12.5%)
H07 | 0.4 | 6 | TESTED-KEEP | Recovery period shows Ireland catching up | recovery | IE below avg 2024-25 | growth_diff | E08: IE slightly above avg (+3.9% vs +2.0%)
H08 | 0.4 | 7 | TESTED-KEEP | Ireland's rank position deteriorated over time | rank_trajectory | worsening rank | rank_change | E13: rank moved from #8 to #6 (worsened)

### Absolute Level Analysis
H09 | 0.4 | 9 | TESTED-KEEP | Ireland has highest absolute EUR/sqm | country | IE ranked #1 | rank | E14: IE ranked #8/11 (below average)
H10 | 0.6 | 8 | TESTED-KEEP | UK is more expensive than Ireland | bilateral | UK>IE | eur_sqm_diff | Confirmed: UK EUR 2,800 vs IE EUR 1,975
H11 | 0.5 | 7 | TESTED-KEEP | PPP adjustment makes Ireland look cheaper | ppp | IE lower after PPP | ppp_eur_sqm | E15: PPP-adjusted IE ~EUR 1,555/sqm
H12 | 0.5 | 7 | TESTED-KEEP | Ireland cost-to-income ratio is worst in EU | affordability | IE highest ratio | ratio | E16: IE 4.0x vs DE 5.6x (IE better)

### Structural Analysis
H13 | 0.5 | 8 | TESTED-KEEP | Ireland's cost trajectory is structurally distinct from DE/NL | cluster | IE in different cluster | cluster_id | T04: IE clusters with BE/SE, not DE/NL/AT
H14 | 0.6 | 7 | TESTED-KEEP | Panel regression shows significant country-time interaction for Ireland | regression | significant int_IE | p_value | T02: IE significantly below AT slope (p<0.0001)
H15 | 0.5 | 7 | TESTED-KEEP | Structural breaks align with COVID and Ukraine for all countries | breaks | common break dates | break_dates | T03: 2021-Q1 and 2022-Q2 common across most countries
H16 | 0.5 | 6 | TESTED-KEEP | Ireland shows convergence toward EU average | convergence | IE slope approaches avg | slope_diff | T02: IE slope below average; NOT converging up but below median

### Bilateral Comparisons
H17 | 0.5 | 6 | TESTED-KEEP | IE grew faster than UK (2015-2020) | bilateral_uk | IE>UK growth | growth_diff | E01: IE +10.0% vs UK +15.5% to 2020-Q3 (UK faster)
H18 | 0.3 | 7 | TESTED-KEEP | IE grew faster than NL | bilateral_nl | IE>NL growth | growth_diff | E02: IE 41.3% vs NL 71.2% (NL much faster)
H19 | 0.5 | 6 | TESTED-KEEP | IE grew faster than DK (small open economy) | bilateral_dk | IE>DK | growth_diff | E03: IE +8.2pp above DK
H20 | 0.4 | 7 | TESTED-KEEP | Countries with housing crises (IE, NL) have higher growth | demand_pressure | crisis countries faster | group_avg | Mixed: NL fastest, IE mid-pack

### Modular/Regulatory
H21 | 0.6 | 7 | TESTED-KEEP | Modular construction leaders have slower cost growth | prefab_rate | negative correlation | correlation | E11: Contradicted --- SE and NL high prefab but high growth
H22 | 0.5 | 6 | TESTED-KEEP | Lower-regulation countries have slower growth | regulatory | negative correlation | group_avg | E12: Partial --- ES/FI slower but also lower baseline
H23 | 0.4 | 6 | TESTED-KEEP | Flattest cost curves correlate with weaker demand | demand | demand negatively correlated | correlation | E19: FI/FR flattest, both have weak construction demand

### Decomposition
H24 | 0.6 | 8 | TESTED-KEEP | Labour premium is largest component of Irish excess | component | labour > materials | eur_amount | E20: Labour EUR 175 largest, then regulatory EUR 138
H25 | 0.5 | 7 | TESTED-KEEP | Materials island premium is significant | component | materials premium >5% | pct | E20: Materials ~EUR 53 (small)
H26 | 0.5 | 7 | TESTED-KEEP | Regulatory compliance adds >5% to costs | component | regulatory >5% | pct | E20: Regulatory ~EUR 138 (~7%)
H27 | 0.4 | 6 | TESTED-KEEP | Ireland's excess is mostly explained by measurable components | decomposition | residual small | eur_amount | E20: Residual negative (IE below EU avg overall)

### Counterfactual
H28 | 0.4 | 7 | TESTED-KEEP | If Ireland tracked EU average, costs would be higher | counterfactual | CF > actual | eur_sqm | E17: CF EUR 2,044 vs actual EUR 1,975 (actual is lower)
H29 | 0.5 | 6 | TESTED-KEEP | Ireland's excess above EU average is >10% | excess | >10% | pct | E18: IE is -2.1% BELOW EU-10 average

### Additional hypotheses (untested, for completeness)
H30 | 0.5 | 5 | OPEN | Seasonal patterns differ across countries | seasonality | different seasonal amplitudes | seasonal_component | -
H31 | 0.4 | 5 | OPEN | Eastern EU countries converging toward Western levels | convergence_east | faster growth in East | growth_rate | -
H32 | 0.3 | 5 | OPEN | Interest rate changes correlate with construction cost breaks | monetary_policy | break points align with ECB rate changes | break_alignment | -
H33 | 0.5 | 5 | OPEN | Currency movements explain UK divergence | fx | GBP/EUR correlation with cost diff | correlation | -
H34 | 0.4 | 4 | OPEN | Construction output volume negatively correlates with cost growth | supply_demand | inverse relationship | correlation | -
H35 | 0.5 | 5 | OPEN | Apartment vs house mix explains some country differences | compositional | mix-adjusted growth differs | growth_diff | -
H36 | 0.3 | 4 | OPEN | Energy intensity of national industries correlates with Ukraine shock | energy_dep | positive correlation | correlation | -
H37 | 0.4 | 5 | OPEN | Immigration policy correlates with construction labour supply | immigration | more open = lower wage growth | correlation | -
H38 | 0.5 | 5 | OPEN | Land cost component varies more than construction cost | land_vs_build | land variance > build variance | variance_ratio | -
H39 | 0.4 | 4 | OPEN | Public sector construction share affects cost trajectories | public_share | higher share = different trajectory | trajectory_shape | -
H40 | 0.5 | 5 | OPEN | Inflation expectations feed into construction cost expectations | expectations | survey data correlates | correlation | -
H41 | 0.3 | 4 | OPEN | Timber-frame adoption correlates with lower costs | timber | negative correlation | correlation | -
H42 | 0.4 | 5 | OPEN | Transport infrastructure costs correlate with material costs | transport | island premium quantifiable | premium_pct | -
H43 | 0.5 | 5 | OPEN | Green building mandates increase costs more in late adopters | green_regs | late adopters see larger jumps | growth_spike | -
H44 | 0.4 | 4 | OPEN | Apprenticeship system quality correlates with productivity | training | better systems = higher productivity | correlation | -
H45 | 0.3 | 4 | OPEN | Construction firm concentration affects pricing power | market_structure | more concentrated = higher margins | correlation | -
H46 | 0.5 | 5 | OPEN | Concrete vs steel-frame preference affects cost sensitivity to global prices | material_mix | steel-heavy more volatile | volatility | -
H47 | 0.4 | 4 | OPEN | Self-build share affects measured costs differently | self_build | higher share = underestimated costs | measurement_bias | -
H48 | 0.3 | 4 | OPEN | BIM adoption rate correlates with productivity gains | bim | positive correlation | productivity_change | -
H49 | 0.4 | 5 | OPEN | Social housing share affects average cost trajectories | social_housing | higher share = different trajectory | trajectory | -
H50 | 0.5 | 5 | OPEN | Renovation vs new-build ratio affects national statistics | renovation | higher ratio = different index behavior | index_bias | -
H51 | 0.4 | 4 | OPEN | Developer profit margins vary across countries | margins | IE margins above average | pct | -
H52 | 0.3 | 5 | OPEN | Tax treatment (VAT reduced rates) explains consumer cost differences | vat | VAT adjustment changes ranking | adjusted_rank | -
H53 | 0.5 | 5 | OPEN | Urbanisation rate correlates with cost levels | urban | positive correlation | correlation | -
H54 | 0.4 | 4 | OPEN | Population density correlates with land premium but not build cost | density | build cost independent of density | correlation | -
H55 | 0.3 | 4 | OPEN | Export share of construction materials affects domestic prices | trade | net importers pay more | correlation | -
H56 | 0.5 | 5 | OPEN | Labour mobility within EU affects wage convergence | mobility | mobile workers equalize wages | convergence | -
H57 | 0.4 | 4 | OPEN | Subcontracting practices affect cost measurement | subcontracting | more subcontracting = higher measured costs | measurement | -
H58 | 0.3 | 5 | OPEN | Climate requirements (insulation etc) differ by country | climate | colder = higher build cost | correlation | -
H59 | 0.4 | 4 | OPEN | Warranty and defects liability periods vary and affect costs | warranty | longer warranty = higher upfront cost | correlation | -
H60 | 0.3 | 4 | OPEN | Professional fees (architects/engineers) as share of project cost vary | fees | IE higher professional fees | fee_share | -
H61 | 0.5 | 5 | OPEN | Infrastructure charges (development levies) affect delivered cost | levies | IE levies above average | levy_amount | -
H62 | 0.4 | 4 | OPEN | Site preparation costs differ (rocky ground, water table) | site_prep | geographic factors significant | cost_share | -
H63 | 0.3 | 5 | OPEN | Dispute resolution mechanisms affect project costs | disputes | more litigious = higher cost | correlation | -
H64 | 0.5 | 5 | OPEN | Planning permission duration correlates with cost | planning_time | longer = higher cost | correlation | -
H65 | 0.4 | 4 | OPEN | Procurement methods (design-build vs traditional) affect costs | procurement | design-build cheaper | cost_diff | -
H66 | 0.3 | 4 | OPEN | Union density correlates with labour costs | unions | positive correlation | correlation | -
H67 | 0.5 | 5 | OPEN | Building height restrictions affect apartment costs | height | stricter = higher unit cost | correlation | -
H68 | 0.4 | 4 | OPEN | Foundation requirements differ by geology | foundation | variable cost impact | cost_share | -
H69 | 0.3 | 5 | OPEN | Fire safety requirements post-Grenfell affected costs | fire_safety | countries with reforms saw jumps | growth_spike | -
H70 | 0.5 | 5 | OPEN | Accessibility requirements vary and affect costs | accessibility | stricter = higher cost | cost_pct | -
H71 | 0.4 | 4 | OPEN | Acoustic insulation requirements vary | acoustic | stricter = higher cost | cost_pct | -
H72 | 0.3 | 4 | OPEN | Car parking requirements affect residential costs | parking | minimum parking = higher cost | cost_per_unit | -
H73 | 0.5 | 5 | OPEN | Renewable energy mandates add to construction costs | renewables | mandate = higher cost | cost_pct | -
H74 | 0.4 | 4 | OPEN | Local authority efficiency affects planning delays | la_efficiency | faster = lower cost | correlation | -
H75 | 0.3 | 5 | OPEN | Judicial review frequency correlates with project delays | jr | more JRs = higher cost | correlation | -
H76 | 0.5 | 5 | OPEN | Public infrastructure (roads, water) availability affects site cost | infrastructure | better infra = lower site prep | cost_diff | -
H77 | 0.4 | 4 | OPEN | Student population correlates with rental construction demand | students | more students = more demand | correlation | -
H78 | 0.3 | 4 | OPEN | Tourist accommodation demand competes with residential | tourism | tourism demand raises costs | correlation | -
H79 | 0.5 | 5 | OPEN | Data centre construction competes for trades and materials | data_centres | IE data centre boom raises costs | timing_correlation | -
H80 | 0.4 | 4 | OPEN | Pharmaceutical/tech construction crowd-out effects | pharma | high-value construction crowds out housing | wage_premium | -
H81 | 0.3 | 5 | OPEN | Insurance costs for builders vary across countries | insurance | IE higher insurance | cost_pct | -
H82 | 0.5 | 5 | OPEN | Working time regulations affect effective labour supply | hours | fewer hours = higher per-unit cost | hourly_productivity | -
H83 | 0.4 | 4 | OPEN | Health and safety compliance costs vary | h_and_s | stricter = higher cost | compliance_cost | -
H84 | 0.3 | 4 | OPEN | Material testing and certification requirements differ | testing | more testing = higher cost | cost_pct | -
H85 | 0.5 | 5 | OPEN | Currency union membership affects material import costs | euro | eurozone = lower import cost volatility | volatility | -
H86 | 0.4 | 4 | OPEN | Government capital spending cycles correlate with cost | capex | more govt spending = higher private costs | correlation | -
H87 | 0.3 | 5 | OPEN | Housing finance availability affects demand-side pressure | credit | easier credit = higher costs | correlation | -
H88 | 0.5 | 5 | OPEN | Population growth correlates with construction cost growth | pop_growth | positive correlation | correlation | -
H89 | 0.4 | 4 | OPEN | Migration patterns to construction sector | migration | net construction immigration matters | worker_supply | -
H90 | 0.3 | 4 | OPEN | Skills certification reciprocity affects labour mobility | skills_cert | mutual recognition = more supply | worker_supply | -
H91 | 0.5 | 5 | OPEN | Distance from major material producers affects cost | distance | further = higher transport cost | cost_premium | -
H92 | 0.4 | 4 | OPEN | Cement industry structure (local vs imported) | cement | local monopoly = higher cost | price_diff | -
H93 | 0.3 | 5 | OPEN | Aggregate (sand/gravel) availability varies | aggregates | scarcity = higher cost | cost_component | -
H94 | 0.5 | 5 | OPEN | Window/glazing specifications differ (U-values) | glazing | stricter U-value = higher cost | cost_pct | -
H95 | 0.4 | 4 | OPEN | Roof specifications vary by country | roofing | different standards = different costs | cost_component | -
H96 | 0.3 | 4 | OPEN | Plumbing/mechanical specifications differ | plumbing | stricter = higher cost | cost_pct | -
H97 | 0.5 | 5 | OPEN | Electrical specifications and smart home mandates | electrical | more mandates = higher cost | cost_pct | -
H98 | 0.4 | 4 | OPEN | Waste management regulations affect demolition/construction cost | waste | stricter = higher cost | cost_pct | -
H99 | 0.3 | 5 | OPEN | Brownfield vs greenfield development costs | brownfield | brownfield premium varies by country | cost_premium | -
H100 | 0.5 | 5 | OPEN | Construction technology adoption rate (drones, robotics) | tech | higher tech = lower unit cost | correlation | -
H101 | 0.4 | 4 | OPEN | Weather disruption days vary by country | weather | more disruption = higher cost | lost_days | -
H102 | 0.3 | 4 | OPEN | Ground contamination remediation requirements | contamination | stricter = higher brownfield cost | cost_premium | -
H103 | 0.5 | 5 | OPEN | Stormwater management requirements | stormwater | SuDS mandates = higher site cost | cost_component | -
