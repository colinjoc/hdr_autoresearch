# Design Variables

## Primary Design Variables (10 levers)

| # | Variable | Type | Settings | Mechanism | Source |
|---|----------|------|----------|-----------|--------|
| 1 | Duration reduction | Continuous (discretised) | 0%, -25%, -33%, -50% | Reduces finance carry costs | PL-1 |
| 2 | Modular construction savings | Continuous (discretised) | 0%, -10%, -20%, -30% off hard costs | Direct hard cost reduction | C-1, SCSI |
| 3 | VAT rate | Discrete | 13.5%, 9%, 0% | Reduces total cost by removing tax | Revenue |
| 4 | Part V rate | Discrete | 20%, 10%, 0% | Reduces cross-subsidy obligation | DHLGH |
| 5 | Development contributions | Discrete | 100%, 50%, 0% | Reduces infrastructure levies | DECLG |
| 6 | BCAR compliance | Discrete | 100%, 50%, 0% | Reduces regulatory compliance cost | DHLGH |
| 7 | Land cost (CPO) | Continuous (discretised) | 100%, 50%, 10% of market | Land acquisition cost reduction | Evans |
| 8 | Finance rate | Continuous (discretised) | 7%, 5%, 3% | Reduces cost of capital | C-2 |
| 9 | Developer margin | Continuous (discretised) | 15%, 10%, 6% | Reduces required return | C-2 |
| 10 | Workforce/capacity multiplier | Continuous (discretised) | +0%, +20%, +50% | Lifts construction capacity ceiling | S-3, IGEES |

## Derived Variables (computed within the model)

| Variable | Formula | Units |
|----------|---------|-------|
| Cost reduction (fractional) | Sum of lever-specific savings / total_dev_cost | fraction |
| New viability margin | baseline_viability + cost_reduction | fraction |
| Application multiplier | 1 + 0.91 * (cost_reduction / 0.10) | dimensionless |
| Effective applications | baseline_apps_effective * app_multiplier | units/yr |
| Permissions | applications * 0.68 | units/yr |
| Gross completions | permissions * 0.596 | units/yr |
| Capacity ceiling | 35,000 * workforce_multiplier | units/yr |
| Final completions | min(gross_completions, capacity_ceiling) | units/yr |

## Interaction Terms

| Interaction | Mechanism | Expected sign |
|-------------|-----------|---------------|
| Duration × Finance rate | Both reduce finance costs; sub-additive on same cost component | Negative (redundancy) |
| Modular × Workforce | Modular both reduces cost AND expands effective capacity | Positive (synergy) |
| Any cost lever × Workforce | Cost levers increase demand; workforce lifts supply cap | Positive (synergy) |
| VAT × Margin | Both reduce cost; additive on different components | Near-zero |
| Land CPO × Duration | Independent cost components | Near-zero |
| Multiple cost levers × Viability threshold | Levers that jointly flip viability from negative to positive | Strongly positive (threshold) |
