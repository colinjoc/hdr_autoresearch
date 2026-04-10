# Design Variables: Irish BER vs Real Home Energy Gap

## Target Variable

**BER Energy Value (kWh/m2/yr)**: The DEAP-calculated primary energy consumption per square meter per year. This is the number that determines the BER letter grade. It is a MODEL OUTPUT, not a measured quantity.

## Core Building Characteristics (Raw Features)

| # | Variable | Type | Source | Physics Justification |
|---|----------|------|--------|----------------------|
| 1 | `year_built` | Ordinal | BER certificate | Construction era determines wall type, insulation standards, building regulations |
| 2 | `floor_area_m2` | Continuous | BER certificate | Scales absolute demand; energy value normalised by area creates nonlinear effects |
| 3 | `wall_type` | Categorical | BER certificate | Primary fabric heat loss path: solid stone, solid brick, cavity block, timber frame |
| 4 | `wall_insulation_type` | Categorical | BER certificate | None, partial fill, full fill, external, internal |
| 5 | `wall_insulation_thickness_mm` | Continuous | BER certificate | Determines wall U-value |
| 6 | `roof_insulation_mm` | Continuous | BER certificate | Attic insulation thickness |
| 7 | `floor_insulation` | Binary | BER certificate | Present/absent ground floor insulation |
| 8 | `window_type` | Categorical | BER certificate | Single, double, triple glazed; frame type |
| 9 | `window_u_value` | Continuous | BER certificate (some) | Window thermal transmittance |
| 10 | `heating_system_type` | Categorical | BER certificate | Oil boiler, gas boiler, heat pump, solid fuel, electric |
| 11 | `heating_system_efficiency` | Continuous | BER certificate | Boiler seasonal efficiency or heat pump COP |
| 12 | `secondary_heating_type` | Categorical | BER certificate | Open fire, stove, electric heater |
| 13 | `hot_water_system` | Categorical | BER certificate | Immersion, combi boiler, solar-assisted |
| 14 | `ventilation_type` | Categorical | BER certificate | Natural, extract fans, balanced MVHR |
| 15 | `air_permeability` | Continuous | BER certificate (newer) | m3/h/m2 at 50 Pa from blower door test |
| 16 | `county` | Categorical (26) | BER certificate | Geographic location affecting climate |
| 17 | `dwelling_type` | Categorical | BER certificate | Detached, semi-detached, terraced, apartment |
| 18 | `number_of_storeys` | Ordinal | BER certificate | Affects form factor (surface area to volume) |

## Derived Physics Features (Engineered)

| # | Variable | Computation | Physics Justification |
|---|----------|-------------|----------------------|
| 19 | `wall_u_value_est` | f(wall_type, insulation_type, insulation_thickness) | Estimated wall U-value from lookup tables + physics formulas |
| 20 | `fabric_heat_loss_coeff` | Sum(U_i * A_i) for all fabric elements | Total fabric heat loss coefficient (W/K) |
| 21 | `form_factor` | Envelope area / Floor area | Higher form factor = more surface heat loss per m2 |
| 22 | `hdd_county` | Met Eireann data by county | Heating degree days capturing regional climate severity |
| 23 | `heating_demand_proxy` | fabric_loss_coeff * HDD * 24 / 1000 / floor_area | Physics-based proxy for space heating demand |
| 24 | `ventilation_heat_loss_est` | 0.33 * ACH * Volume | Estimated ventilation heat loss (W/K) |
| 25 | `total_heat_loss_coeff` | fabric_loss + ventilation_loss | Total building heat loss |
| 26 | `solar_gain_proxy` | window_area * g_value * irradiance_county | Estimated useful solar heat gains |
| 27 | `net_heat_demand_proxy` | heating_demand - solar_gains | Net space heating demand |
| 28 | `system_efficiency_ratio` | actual_efficiency / 1.0 | Heating system efficiency normalised to direct electric |
| 29 | `delivered_energy_proxy` | net_heat_demand / system_efficiency | Estimated delivered energy for space heating |
| 30 | `primary_energy_factor` | fuel-type dependent multiplier | Primary energy conversion factor for BER calculation |

## Interaction Features (Hypothesis-Driven)

| # | Variable | Computation | Hypothesis |
|---|----------|-------------|-----------|
| 31 | `wall_x_heating` | wall_u_value * (1/system_efficiency) | Poor walls + inefficient heating compounds the problem |
| 32 | `vintage_x_insulation` | year_built * wall_insulation_thickness | Newer homes with less insulation are unusual — may indicate data quality issues |
| 33 | `area_per_bedroom` | floor_area / n_bedrooms | Proxy for occupancy density — smaller per-person area = more internal gains |
| 34 | `heat_pump_x_fabric` | is_heat_pump * wall_u_value | Heat pumps need good fabric to achieve high COP |
| 35 | `county_x_wall_type` | county * wall_type interaction | Regional construction practices affect performance |
| 36 | `airtight_x_radon_risk` | air_permeability * county_radon_risk | UNVEIL tension: tight + high-radon is the dangerous combination |
| 37 | `vintage_decade` | year_built // 10 * 10 | Construction decade as categorical — captures building regulation thresholds |
| 38 | `regulation_era` | mapped from year_built | Pre-1972, 1972-1991, 1992-2005, 2006-2010, 2011-2019, 2019+ (nZEB) |
| 39 | `assessor_volume` | count of certificates per assessor_id | High-volume assessors may use more defaults |
| 40 | `assessment_year` | date of BER assessment | Later assessments may have different calibration |

## Retrofit-Specific Features (for Before-After Analysis)

| # | Variable | Computation | Purpose |
|---|----------|-------------|---------|
| 41 | `delta_ber_value` | after_value - before_value | BER improvement from retrofit |
| 42 | `retrofit_type` | categorical from grant data | Which measure was installed |
| 43 | `pre_retrofit_rating` | BER rating before | Starting point affects potential improvement |
| 44 | `expected_improvement` | engineering calculation | How much improvement DEAP predicts for this measure |
| 45 | `actual_vs_expected_ratio` | delta_ber / expected_improvement | Ratio of achieved to predicted improvement |
