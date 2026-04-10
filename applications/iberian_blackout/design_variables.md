# Design Variables: Iberian Blackout Cascade Prediction

## Target Variable
- **frequency_excursion_binary**: 1 if max |f - 50.0| > 200 mHz in the hour, 0 otherwise
- **frequency_excursion_magnitude**: max |f - 50.0| in mHz (continuous target for regression)

## Primary Features (from ENTSO-E generation/load data)

### Generation Mix Features
| Variable | Unit | Source | Physics Justification |
|----------|------|--------|----------------------|
| gen_nuclear_mw | MW | ENTSO-E A75 | Synchronous, high inertia (H~6s), slow ramp |
| gen_coal_mw | MW | ENTSO-E A75 | Synchronous, moderate inertia (H~5s) |
| gen_gas_ccgt_mw | MW | ENTSO-E A75 | Synchronous, moderate inertia (H~4s), fast ramp |
| gen_gas_ocgt_mw | MW | ENTSO-E A75 | Synchronous, low inertia (H~3s), fast start |
| gen_hydro_mw | MW | ENTSO-E A75 | Synchronous, moderate inertia (H~3.5s), fast ramp |
| gen_wind_mw | MW | ENTSO-E A75 | Non-synchronous (grid-following), no inherent inertia |
| gen_solar_mw | MW | ENTSO-E A75 | Non-synchronous (grid-following), no inherent inertia |
| gen_other_re_mw | MW | ENTSO-E A75 | Biomass, geothermal — typically synchronous |
| gen_total_mw | MW | Computed | Sum of all generation |

### Load Features
| Variable | Unit | Source | Physics Justification |
|----------|------|--------|----------------------|
| load_total_mw | MW | ENTSO-E A65 | System demand determines operating point |
| load_fraction | ratio | Computed | load / installed_capacity — how stressed is the system? |

### Interconnector Features
| Variable | Unit | Source | Physics Justification |
|----------|------|--------|----------------------|
| flow_es_fr_mw | MW | ENTSO-E A11 | Spain-France flow (positive = export from Spain) |
| flow_es_pt_mw | MW | ENTSO-E A11 | Spain-Portugal flow (positive = export from Spain) |
| net_import_mw | MW | Computed | Net import to Iberian peninsula |

### Price Features
| Variable | Unit | Source | Physics Justification |
|----------|------|--------|----------------------|
| price_day_ahead_eur | EUR/MWh | ENTSO-E A44 | Low/negative prices indicate high RE, potential curtailment |

## Derived Features (computed from primary)

### Renewable Penetration
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| snsp | (wind + solar + import) / (total_gen + import) | System Non-Synchronous Penetration — primary risk indicator |
| re_fraction | (wind + solar) / total_gen | Simple renewable fraction |
| synchronous_fraction | (nuclear + coal + gas + hydro) / total_gen | Fraction providing inertia |

### Inertia Proxy
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| inertia_proxy_mws | nuclear*6 + coal*5 + gas*4 + hydro*3.5 | Estimated system inertia in MW*s |
| inertia_proxy_s | inertia_proxy_mws / total_gen | System-average H constant |
| kinetic_energy_gwh | inertia_proxy_mws / 3600 | Stored kinetic energy |

### Generation Diversity
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| gen_diversity_shannon | -sum(p_i * log(p_i)) over fuel types | Low diversity = vulnerability |
| gen_hhi | sum(p_i^2) over fuel types | Herfindahl-Hirschman concentration index |

### Ramp Rate Features
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| wind_ramp_1h_mw | wind(t) - wind(t-4) (15min steps) | Wind generation ramp over 1 hour |
| solar_ramp_1h_mw | solar(t) - solar(t-4) | Solar generation ramp over 1 hour |
| total_ramp_1h_mw | total_gen(t) - total_gen(t-4) | Total generation ramp |
| max_ramp_15min_mw | max absolute 15-min change in past hour | Steepest ramp in recent history |

### Temporal Features
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| hour_sin | sin(2*pi*hour/24) | Daily cycle (solar pattern) |
| hour_cos | cos(2*pi*hour/24) | Daily cycle (complement) |
| month_sin | sin(2*pi*month/12) | Seasonal cycle |
| month_cos | cos(2*pi*month/12) | Seasonal cycle (complement) |
| is_weekend | binary | Weekend demand patterns differ |
| day_of_week | 0-6 | Full weekly cycle |

### Lagged Features
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| snsp_lag_1h | snsp(t-4) | SNSP persistence |
| snsp_lag_6h | snsp(t-24) | SNSP trend |
| snsp_lag_24h | snsp(t-96) | Daily SNSP cycle |
| inertia_lag_1h | inertia_proxy(t-4) | Inertia persistence |
| load_lag_1h | load(t-4) | Load persistence |
| snsp_delta_1h | snsp(t) - snsp(t-4) | SNSP rate of change |
| snsp_delta_6h | snsp(t) - snsp(t-24) | SNSP trend direction |
| inertia_delta_1h | inertia(t) - inertia(t-4) | Inertia change rate |

### Flow Reversal Indicators
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| flow_es_fr_reversed_6h | sign change in ES-FR flow in past 6h | Flow reversal indicates dispatch instability |
| flow_magnitude_ratio | |flow_es_fr| / NTC | How close to transfer limit |

### Frequency Stress Proxy (if actual frequency data unavailable)
| Variable | Formula | Physics Justification |
|----------|---------|----------------------|
| gen_load_imbalance_mw | total_gen - load - net_export | Instantaneous power imbalance |
| imbalance_fraction | imbalance / load | Relative imbalance |
| ramp_to_inertia_ratio | max_ramp / inertia_proxy | Ramp stress relative to available inertia |

## Feature Groups for Ablation Studies

1. **BASE**: gen_mix + load + temporal = always included
2. **SNSP**: snsp, re_fraction, synchronous_fraction
3. **INERTIA**: inertia_proxy_mws, inertia_proxy_s, kinetic_energy_gwh
4. **FLOW**: flow_es_fr, flow_es_pt, net_import, flow_magnitude_ratio
5. **RAMP**: wind_ramp_1h, solar_ramp_1h, total_ramp_1h, max_ramp_15min
6. **LAG**: all lagged and delta features
7. **DIVERSITY**: gen_diversity_shannon, gen_hhi
8. **PRICE**: price_day_ahead_eur
9. **REVERSAL**: flow_es_fr_reversed_6h
10. **STRESS_PROXY**: gen_load_imbalance, imbalance_fraction, ramp_to_inertia_ratio
