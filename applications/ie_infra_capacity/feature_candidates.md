# Feature Candidates: U-3 Infrastructure Capacity Blocks

## WWTP-Level Features

| Feature | Source | Computation | Physics Justification |
|---------|--------|-------------|----------------------|
| capacity_status | WW register | Direct: GREEN/AMBER/RED | Primary classification of treatment capacity |
| is_red | WW register | Binary: capacity == RED | Hard constraint indicator |
| is_amber | WW register | Binary: capacity == AMBER | Partial constraint indicator |
| is_red_or_amber | WW register | Binary: RED or AMBER | Combined constraint indicator |
| project_planned | WW register | Binary: project exists | Indicates future capacity relief |
| reg_prefix | WW register | D (>2000 PE) vs A (<2000 PE) | Proxy for plant size and regulatory status |
| region | WW register | Categorical: NW/NE/S/E/W/MW | Regional infrastructure investment patterns |

## County-Level Features

| Feature | Source | Computation | Physics Justification |
|---------|--------|-------------|----------------------|
| pct_red | WW register | n_red / n_total per county | County constraint intensity |
| pct_amber | WW register | n_amber / n_total per county | County partial constraint |
| pct_red_or_amber | WW register | Combined share | Overall constraint rate |
| n_wwtp | WW register | Count per county | Infrastructure density |
| pct_with_project | WW register | n_project / n_constrained | Investment pipeline coverage |
| zoned_ha | Goodbody 2021 | Population-weighted allocation | Development potential |
| estimated_blocked_ha | Derived | zoned_ha × pct_red_or_amber | Land sterilised by infrastructure |

## Planning Application Features

| Feature | Source | Computation | Physics Justification |
|---------|--------|-------------|----------------------|
| n_residential_apps | Planning register | Count where NumResidentialUnits > 0 | Development demand indicator |
| refusal_rate | Planning register | n_refused / n_total | Planning system constraint |
| is_one_off | Planning register | One-Off House flag | Septic tank (WWTP-independent) |
| num_units | Planning register | NumResidentialUnits | Scale of proposed development |
| is_apartment | Planning register | NumResidentialUnits > 4 | Higher WWTP loading per hectare |
| year | Planning register | Application received year | Temporal trends |
| grant_rate | Planning register | Granted / total | Planning success indicator |

## Derived / Cross-Source Features

| Feature | Source | Computation | Physics Justification |
|---------|--------|-------------|----------------------|
| apps_per_ha | Planning + Goodbody | n_apps / zoned_ha | Development intensity |
| demand_constraint_ratio | Planning + WW | apps × pct_constrained | Demand weighted by constraint |
| double_stranded_ha | WW + U-2 | blocked_ha × 0.83 | Infrastructure + viability overlap |
| capacity_status_category | WW derived | Binned pct_red_or_amber | Low/medium/high constraint |
| investment_priority_score | Derived | blocked_ha × (1 - pct_with_project) | Unaddressed constraint weighted by impact |
