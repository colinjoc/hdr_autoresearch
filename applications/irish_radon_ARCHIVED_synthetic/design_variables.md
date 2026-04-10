# Design Variables: Irish Radon Prediction

## Target Variable

**Binary classification**: Does the area (Electoral Division or Small Area) have >10% of homes exceeding 200 Bq/m3?
- Equivalent to: Is this area a "High Radon Area" (HRA)?
- Derived from: EPA radon map grid designations aggregated to ED/SA level
- Class balance: ~28% positive (HRA), ~72% negative (non-HRA)

## Geological Features (from Tellus Radiometric + GSI Maps)

| Variable | Source | Physics Justification | Expected Effect |
|---|---|---|---|
| eU_mean | Tellus radiometric | Uranium is the source of radon; direct parent-daughter chain | Strong positive |
| eU_median | Tellus radiometric | Robust central tendency of uranium | Strong positive |
| eU_p90 | Tellus radiometric | Tail captures localised high-U zones | Strong positive |
| eU_std | Tellus radiometric | Variability indicates mixed lithology | Uncertain |
| eTh_mean | Tellus radiometric | Thorium correlates with uranium in most rocks | Moderate positive |
| eU_eTh_ratio | Tellus radiometric | Uranium enrichment relative to thorium; indicates specific mineralisation | Strong positive for >1.0 |
| K_mean | Tellus radiometric | Potassium indicates acidic/alkaline rock type | Weak positive |
| total_dose_rate | Tellus radiometric | 0.0417K + 0.604eU + 0.310eTh; composite radiation index | Strong positive |
| bedrock_code | GSI bedrock map | Lithology determines U content and rock permeability | Categorical, strong |
| bedrock_class | GSI bedrock map | igneous/sedimentary/metamorphic grouping | Categorical |
| bedrock_age | GSI bedrock map | Geological age affects U distribution | Categorical |
| is_granite | GSI bedrock map | Granite = high U, high radon | Strong positive |
| is_limestone | GSI bedrock map | Karstified limestone = high permeability | Moderate positive |
| is_shale | GSI bedrock map | Black shale = high U | Moderate positive |
| quat_code | GSI quaternary map | Subsoil type determines permeability | Categorical, strong |
| quat_permeability | GSI quaternary map | Ordinal: rock>gravel>sand>thin_till>thick_till>peat | Strong positive |
| is_rock_surface | GSI quaternary map | Rock at surface = max radon transport | Strong positive |
| is_peat | GSI quaternary map | Peat acts as radon barrier | Strong negative |
| till_thickness_proxy | GSI quaternary map | Thin vs thick till distinction | Negative with thickness |

## Building Features (from BER Database)

| Variable | Source | Physics Justification | Expected Effect |
|---|---|---|---|
| ber_rating_ordinal | SEAI BER | Airtightness proxy; high BER = low ventilation | Positive (high BER → more radon) |
| air_permeability_mean | SEAI BER | Direct ventilation rate proxy | Negative (high permeability → more dilution) |
| pct_slab_on_ground | SEAI BER | Slab-on-ground vs suspended timber floor | Negative (slabs better barrier) |
| pct_suspended_timber | SEAI BER | Suspended timber floors allow more radon entry | Positive |
| pct_mvhr | SEAI BER | MVHR can reduce or increase radon depending on balance | Uncertain |
| pct_natural_vent | SEAI BER | Natural ventilation = more air exchange | Negative |
| mean_year_built | SEAI BER | Proxy for construction standards and sealing | Nonlinear |
| pct_post_2011 | SEAI BER | Modern building regs include radon barriers | Negative |
| pct_pre_1970 | SEAI BER | Old homes: leaky but also poor foundation sealing | Uncertain |
| pct_detached | SEAI BER | Detached homes have more ground contact | Positive |
| mean_floor_area | SEAI BER | Larger floor = more ground contact area | Positive |
| pct_a_rated | SEAI BER | A-rated = very airtight = radon trap risk | Positive on high-radon geology |
| pct_fg_rated | SEAI BER | F/G-rated = very leaky = well-ventilated | Negative |

## Interaction Features

| Variable | Source | Physics Justification | Expected Effect |
|---|---|---|---|
| eU_x_ber_ordinal | Tellus × BER | High U + high airtightness = highest radon risk | Strong positive |
| eU_x_pct_slab | Tellus × BER | Slab-on-ground reduces entry even on high-U geology | Interaction |
| granite_x_a_rated | GSI × BER | Granite geology + A-rated = danger zone | Strong positive |
| limestone_x_thin_till | GSI × GSI | Karst limestone with thin cover = max radon transport | Strong positive |
| eU_x_quat_perm | Tellus × GSI | U source × permeability pathway | Strong positive |

## Climate Features

| Variable | Source | Physics Justification | Expected Effect |
|---|---|---|---|
| mean_wind_speed | Met Éireann | Wind drives ventilation; high wind = lower indoor radon | Negative |
| mean_rainfall | Met Éireann | Rainfall saturates soil, can cap radon or flush it | Nonlinear |
| mean_temperature | Met Éireann | Temperature drives stack effect (winter heating) | Positive with cold |
| hdd | Met Éireann / SEAI | Heating degree days; proxy for heating season length | Positive |

## Spatial Features

| Variable | Source | Physics Justification | Expected Effect |
|---|---|---|---|
| elevation_mean | OSi DEM | Uplands often on different geology; drainage affects radon | Nonlinear |
| slope_mean | OSi DEM | Slope affects soil drainage and radon accumulation | Negative |
| dist_to_hra | EPA radon map | Spatial autocorrelation of radon | Negative |
| county | Admin boundaries | Regional grouping for spatial CV | Categorical |
| latitude | Coordinates | North-south geological gradient | Weak |
| longitude | Coordinates | East-west geological gradient | Weak |

## Feature Engineering Roadmap

### Baseline (Phase 0.5): 8 features
eU_mean, eTh_mean, K_mean, bedrock_code, quat_code, elevation_mean, latitude, longitude

### Phase 1 Tournament: Same 8 features, 4 model families

### Phase 2 HDR Loop: Add features one at a time
1. eU_eTh_ratio, eU_p90, eU_std → radiometric detail
2. total_dose_rate → composite index
3. is_granite, is_limestone, is_shale → lithology indicators
4. quat_permeability, is_rock_surface, is_peat → quaternary detail
5. ber_rating_ordinal, air_permeability_mean → building airtightness
6. pct_slab_on_ground, pct_suspended_timber → floor type
7. pct_mvhr, pct_natural_vent → ventilation type
8. mean_year_built, pct_post_2011, pct_pre_1970 → building age
9. eU_x_ber_ordinal → headline interaction
10. granite_x_a_rated, eU_x_quat_perm → geology × building/soil interactions
11. mean_wind_speed, mean_rainfall → climate
12. slope_mean → topographic
13. dist_to_hra → spatial autocorrelation
