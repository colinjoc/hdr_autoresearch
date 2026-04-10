# Feature Candidates: BER Energy Gap

## Core Building Fabric Features

| Feature | Physics Justification | Expected Direction | Available |
|---------|----------------------|-------------------|-----------|
| UValueWall | Conductive heat loss through walls (largest area) | Higher U → more energy | YES |
| UValueRoof | Conductive heat loss through roof | Higher U → more energy | YES |
| UValueFloor | Conductive heat loss through floor | Higher U → more energy | YES |
| UValueWindow | Conductive heat loss through windows (high U, low area) | Higher U → more energy | YES |
| UValueDoor | Conductive heat loss through doors | Higher U → more energy | YES |
| WallArea, RoofArea, FloorArea | Total heat loss area | More area → more energy | YES |
| WindowArea | Glazing area (high U + solar gains) | Complex: heat loss vs solar gain | YES |
| ThermalBridgingFactor | Junction heat loss (y-value W/m²K) | Higher → more energy | YES |

## Derived Envelope Features

| Feature | Derivation | Physics Justification |
|---------|-----------|----------------------|
| envelope_u_avg | Area-weighted mean of all U-values | Overall fabric quality |
| hlp_proxy | Total UA / floor area | Heat Loss Parameter — the physics-correct summary metric |
| window_wall_ratio | WindowArea / WallArea | Glazing fraction (higher = more loss) |

## Heating System Features

| Feature | Physics Justification | Expected Direction |
|---------|----------------------|-------------------|
| hs_efficiency | SEAI heating system efficiency (%) | Higher → less energy |
| is_heat_pump | Efficiency > 100% (COP > 1) | Heat pump → much less energy |
| fuel_group | Gas/oil/electricity/solid/wood | Different primary energy factors |
| MainSpaceHeatingFuel | Specific fuel type | Primary energy conversion |

## Ventilation Features

| Feature | Physics Justification | Expected Direction |
|---------|----------------------|-------------------|
| is_mechanical_vent | MVHR vs natural ventilation | MVHR recovers ~70% of ventilation heat |
| no_chimneys | Open chimneys = uncontrolled ventilation | More chimneys → more energy |
| no_open_flues | Similar to chimneys | More → more energy |
| draft_lobby | Reduces infiltration | Reduces energy |
| pct_draught_stripped | Reduces infiltration | Higher % → less energy |
| permeability_result | Air test result (m³/hr/m² @50Pa) | Lower → less energy |

## Building Form Features

| Feature | Physics Justification | Expected Direction |
|---------|----------------------|-------------------|
| ground_floor_area | Dwelling size | Larger → more total, less per m² |
| no_storeys | Vertical extent | More floors → more wall area |
| dwelling_type | Detached/semi-d/terrace/apartment | Exposed surface area varies |
| year_built | Proxy for building regulations era | Newer → less energy |
| age_category | Binned construction era | Regulatory era effects |

## Lighting Features

| Feature | Physics Justification | Expected Direction |
|---------|----------------------|-------------------|
| low_energy_lighting_pct | % LED/CFL lighting | Higher → less electricity |

## Candidate Engineered Features (for HDR Loop)

1. **Wall insulation era interaction**: year_built × UValueWall — captures whether old buildings have been retrofitted
2. **Heating-fabric interaction**: hs_efficiency × envelope_u_avg — efficient heating matters more in leaky buildings
3. **County climate proxy**: county → degree-day adjustment (northern counties are colder)
4. **Compactness ratio**: total_envelope_area / floor_area — detached vs apartment effect
5. **Primary energy factor**: fuel-specific conversion from delivered to primary energy
6. **Roof insulation quality relative to era**: UValueRoof relative to regulatory requirement for year_built
7. **Ventilation heat loss estimate**: chimney/flue count + permeability → infiltration rate
8. **Solar gain potential**: window_area × orientation proxy (not available, but window-wall ratio is)
