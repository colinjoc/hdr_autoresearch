# Feature Candidates: Irish International Construction Cost Comparison

## Primary Variables (from Eurostat STS_COPI_Q)

| Feature | Source | Coverage | Notes |
|---------|--------|----------|-------|
| PRC_PRR (producer price, residential) | Eurostat | All 11 countries | Output price index, base 2015=100 or 2021=100 |
| COST (construction cost index) | Eurostat | 7 of 11 countries | Input cost index; IE, UK, BE, FR lack this |
| PCH_PRE (quarter-on-quarter change) | Eurostat | All countries | Percentage change on previous quarter |
| PCH_SM (same quarter previous year) | Eurostat | All countries | Annual growth rate |

## Derived Features

| Feature | Computation | Justification |
|---------|-------------|---------------|
| Cumulative growth from 2015 | (latest / 2015-Q1 - 1) * 100 | Total cost inflation since base year |
| Subperiod growth | Growth within pre-COVID, COVID, Ukraine, Recovery windows | Isolates shock effects |
| Country rank at each quarter | Rank by index level at each time point | Shows trajectory of relative position |
| EU-average deviation | Country index minus mean of other countries | Excess or deficit vs comparator group |
| Quarterly slope (panel regression) | Country-specific time coefficient | Rate of cost increase per quarter |
| Trajectory cluster membership | Ward hierarchical clustering on normalised trajectories | Groups countries by pattern |
| Structural break locations | PELT changepoint detection | Identifies regime changes |

## Anchoring Variables (external)

| Feature | Source | Value | Notes |
|---------|--------|-------|-------|
| Absolute EUR/sqm | Industry sources | IE: 1,975; UK: 2,800; DE: 2,500; etc. | Base construction costs, approximate |
| Labour cost per hour | CSO EHQ03, Eurostat | IE: EUR 34.22; EU avg: ~EUR 28 | Construction-specific hourly rate |
| Labour share of cost | Industry literature | ~40% | Proportion of total build cost |
| Material share of cost | Industry literature | ~45% | Proportion of total build cost |
| Prefab adoption rate | Industry reports | SE: 45%; NL: growing; IE: low | Share of offsite construction |
| Price level index | Eurostat | IE: 127% of EU avg | For PPP adjustment |
| Median household income | Eurostat | IE: ~EUR 50k; DE: ~EUR 45k | For affordability ratios |
| VAT rate on new residential | National legislation | IE: 13.5%; UK: 0%; DE: 19% | Affects consumer cost |

## Interaction Features

| Feature | Computation | Justification |
|---------|-------------|---------------|
| Growth * absolute level | Growth rate * EUR/sqm level | High-cost countries may show lower % growth (base effect) |
| Labour cost * labour share | Hourly rate * share of total | Total labour cost contribution |
| Island premium * material share | Import premium * material proportion | Total logistics cost contribution |
| Regulatory stringency * cost growth | Regulation index * cost trajectory | Regulatory burden impact |
