# Research Queue: Irish BER vs Real Home Energy Gap

## Status Legend
- OPEN: not yet tested
- KEEP: tested, improved score, kept
- REVERT: tested, did not improve, reverted
- SKIP: infeasible or superseded

## Feature Engineering Hypotheses

### Building Fabric Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H001 | Estimated wall U-value from wall_type + insulation_type + thickness improves over raw categoricals | 70% | OPEN | Physics-based continuous feature captures U-value variation within categories |
| H002 | Form factor (envelope area / floor area) improves prediction for apartments vs houses | 55% | OPEN | Apartments have shared walls with lower heat loss; form factor captures this |
| H003 | Estimated fabric heat loss coefficient (sum of U*A) improves over individual U-values | 65% | OPEN | Single aggregated physics feature may be more predictive than separate fabric elements |
| H004 | County-level heating degree days (HDD) improve over raw county | 60% | OPEN | HDD captures the physical quantity (heating demand) that county proxies for |
| H005 | Ventilation heat loss estimate from air permeability * volume | 50% | OPEN | Ventilation is 30-50% of heat loss in older homes; explicit calculation may help |
| H006 | Net heat demand proxy (fabric loss * HDD - solar gains) | 45% | OPEN | Approximates the DEAP calculation directly — may be collinear with target |
| H007 | Thermal bridging factor based on construction era | 40% | OPEN | Pre-2006 homes have worse thermal bridges; DEAP applies a Y-factor |
| H008 | Window-to-wall ratio (window area / wall area) if data available | 35% | OPEN | Affects both heat loss (U-value) and solar gain (g-value) |
| H009 | Roof-to-floor area ratio for attic heat loss | 35% | OPEN | Bungalows have higher roof exposure than two-storey houses |
| H010 | Ground floor U-value from floor construction type | 40% | OPEN | Ground floor contributes 10-15% of fabric loss; currently captured poorly |

### Heating System Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H011 | Heating system efficiency as continuous feature (not categorical) | 65% | OPEN | Efficiency varies within categories (old gas vs new condensing gas); continuous is more informative |
| H012 | Primary energy factor by fuel type | 55% | OPEN | BER uses primary energy; electricity factor (2.08) heavily penalises electric heating |
| H013 | Heat pump COP x fabric quality interaction | 50% | OPEN | Heat pumps in poorly insulated homes run at lower COP; interaction captures this |
| H014 | Boiler age proxy from assessment date and heating system type | 35% | OPEN | Older boilers less efficient; assessment date gives upper bound on boiler age |
| H015 | Secondary heating contribution flag | 40% | OPEN | Homes with secondary heating (open fires) have different energy profile |
| H016 | Hot water fraction: is hot water electric (immersion) vs boiler-fed | 45% | OPEN | Separate hot water system affects delivered energy calculation path |
| H017 | Distribution loss factor from piping insulation | 30% | OPEN | DEAP penalises uninsulated distribution pipes; may add signal for older homes |
| H018 | Renewable contribution (solar thermal + heat pump) combined flag | 50% | OPEN | Homes with any renewable technology have fundamentally different BER profile |

### Regional and Climate Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H019 | Replace county with Met Eireann climate zone (14 zones) | 45% | OPEN | Climate zone is the physical quantity; county adds noise from non-climate variation |
| H020 | Solar irradiance by county (south vs northwest) | 40% | OPEN | Solar gains vary significantly across Ireland — 900 kWh/m2/yr in Dublin vs 800 in Donegal |
| H021 | Wind exposure factor by county/location | 30% | OPEN | Wind exposure increases infiltration heat loss; coastal vs inland matters |
| H022 | Urban/rural indicator (from dwelling type + county) | 50% | OPEN | Urban homes have different heating patterns, sheltering, gas availability |
| H023 | Gas network availability proxy (county x dwelling_type) | 45% | OPEN | Rural homes cannot get gas — forced to oil/solid fuel with different BER profile |
| H024 | HDD x wall_u_value interaction | 55% | OPEN | Cold climate + poor walls compounds the heating demand |
| H025 | HDD x airtightness interaction | 40% | OPEN | Cold + leaky is worse than cold + tight or mild + leaky |

### Building Vintage and Regulation Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H026 | Regulation era (6 categories) instead of raw year_built | 55% | OPEN | Building regs changed at specific years; era captures step-changes in standards |
| H027 | Year built as decade categorical | 50% | OPEN | Construction practices changed by decade; categorical may outperform linear |
| H028 | Celtic Tiger flag (2000-2008) | 35% | OPEN | Celtic Tiger homes had rapid construction with potentially lower quality |
| H029 | Pre-1900 flag (historic buildings) | 40% | OPEN | Very old buildings have distinct construction: thick mass walls, no DPC |
| H030 | Building regulation threshold indicators (1972, 1992, 2006, 2011, 2019) | 60% | OPEN | Step functions at regulation change years — should show discontinuities in BER |
| H031 | Age of building at time of BER assessment | 35% | OPEN | Degradation: older buildings at assessment time may have deteriorated insulation |

### Occupancy Proxy Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H032 | Floor area per bedroom as occupancy density proxy | 45% | OPEN | DEAP assumes standard occupancy from floor area; actual occupancy varies hugely |
| H033 | Number of habitable rooms | 40% | OPEN | More rooms = more heating zones = potentially less whole-house heating |
| H034 | Living room fraction of floor area | 30% | OPEN | DEAP distinguishes living area (20C) from rest (18C); proportion matters |
| H035 | Log(floor_area) instead of linear | 50% | OPEN | Energy per m2 likely decreases with area (economies of scale in heating) |

### Assessor Effect Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H036 | Assessor ID encoded as target mean (leave-one-out) | 55% | OPEN | Some assessors may rate systematically higher/lower; known issue (SEAI audit, P157) |
| H037 | Assessor volume (certificates per assessor) | 45% | OPEN | High-volume assessors may use more defaults (faster but less accurate) |
| H038 | Assessment year (temporal trend in assessment practice) | 40% | OPEN | DEAP methodology updated over time; earlier assessments may be less accurate |
| H039 | Assessor x county interaction (local assessor knowledge) | 30% | OPEN | Local assessors may know typical construction better |

### Radon-Energy Interaction Features

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H040 | County radon risk level (EPA data) | 25% | OPEN | Radon risk may correlate with geology which affects thermal mass and construction |
| H041 | Airtightness x radon risk interaction | 30% | OPEN | UNVEIL finding: tight homes in high-radon areas need MVHR — different energy profile |
| H042 | Geology type proxy from county (granite vs limestone vs sandstone) | 25% | OPEN | Bedrock type affects both radon emanation and local building material traditions |

## Model Architecture Hypotheses

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H043 | Log-transform target (energy value) | 50% | OPEN | Energy value distribution is right-skewed; log may improve regression |
| H044 | Quantile regression instead of mean regression | 35% | OPEN | Predicting median may be more robust to outliers |
| H045 | Two-stage model: classifier (above/below median) + regressor | 30% | OPEN | May capture bimodal distribution if present |
| H046 | Separate models by dwelling type | 40% | OPEN | Apartments vs houses may have fundamentally different feature-target relationships |
| H047 | Separate models by heating fuel type | 35% | OPEN | Gas vs oil vs electric homes have different BER calculation paths |
| H048 | Target-encode wall_type instead of one-hot | 55% | OPEN | 30+ wall types; target encoding reduces dimensionality |
| H049 | Target-encode heating_system_type | 50% | OPEN | Many heating system categories; target encoding may help |
| H050 | Ordinal encode window_type (single < double < triple) | 60% | OPEN | Natural ordering should be captured ordinally |

## Training Improvement Hypotheses

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H051 | Scale positive weight for rare high-energy outliers | 25% | OPEN | Extreme values (>400 kWh/m2/yr) may be underweighted |
| H052 | Increase n_estimators from 300 to 500 | 30% | OPEN | More trees may improve with many features |
| H053 | Reduce learning_rate from 0.05 to 0.01 with more trees | 35% | OPEN | Slower learning with more rounds may improve generalisation |
| H054 | Increase max_depth from 6 to 8 | 25% | OPEN | Deeper trees may capture more interactions |
| H055 | Decrease max_depth from 6 to 4 | 35% | OPEN | Shallower trees may reduce overfitting with many categorical features |
| H056 | Add L1/L2 regularisation (reg_alpha, reg_lambda) | 30% | OPEN | Regularisation may help with correlated features |
| H057 | Use Huber loss instead of squared error | 40% | OPEN | Huber is more robust to outliers in regression |
| H058 | Monotone constraints on physics features (more insulation = lower energy) | 45% | OPEN | Physics-informed constraints may improve generalisation |

## Data Utilisation Hypotheses

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H059 | Remove records with suspiciously low energy values (<10 kWh/m2/yr) | 50% | OPEN | Data quality: some records may be data entry errors |
| H060 | Remove records where energy value exactly equals common defaults | 40% | OPEN | Assessors using only default values produce less informative records |
| H061 | Weight recent assessments higher (post-2015) | 30% | OPEN | Newer assessments use more accurate DEAP version |
| H062 | Stratified sampling to ensure representation of rare building types | 25% | OPEN | Random split may underrepresent rare types (historic, nZEB) |
| H063 | Remove re-assessments (keep only first BER per dwelling) | 35% | OPEN | Multiple BER per dwelling creates quasi-duplication |
| H064 | Add synthetic feature noise for regularisation | 20% | OPEN | May prevent overfitting to exact category boundaries |

## Retrofit-Specific Hypotheses (if before-after data available)

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H065 | Retrofit type (wall/roof/heating/windows) as categorical | 70% | OPEN | Different retrofits have different BER impacts — strongest signal |
| H066 | Pre-retrofit BER rating as baseline feature | 65% | OPEN | Starting point determines potential improvement |
| H067 | Retrofit depth (number of simultaneous measures) | 55% | OPEN | Deep retrofits may have synergistic effects |
| H068 | Interaction: wall_insulation_type x heating_system_change | 50% | OPEN | Insulating walls + upgrading boiler may have interaction effects |
| H069 | Cost-effectiveness ratio (BER improvement per euro spent) | 40% | OPEN | May identify optimal retrofit strategies |
| H070 | Time between original build and retrofit | 35% | OPEN | Very old homes may respond differently to retrofit |

## Discovery and Interpretation Hypotheses

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H071 | SHAP analysis reveals assessor effects are a top-5 feature | 50% | OPEN | Would indicate BER system has significant rater noise |
| H072 | County effects are explained by HDD + gas availability (no residual county signal) | 40% | OPEN | Would indicate geography effect is purely physical |
| H073 | Building vintage effects are explained by regulation era (not gradual trend) | 55% | OPEN | Would indicate step-changes from regulations matter more than gradual improvement |
| H074 | Interaction between wall_type and heating_type accounts for >15% of explained variance | 45% | OPEN | Would indicate fabric-system interaction is a key driver |
| H075 | The DEAP model is almost perfectly linear in its inputs | 60% | OPEN | If tree model offers <5% improvement over Ridge, the DEAP calculation is approximately linear |

## Performance Gap Inference Hypotheses

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H076 | Residuals (actual - predicted BER) correlate with known prebound indicators | 50% | OPEN | Large positive residuals in G-rated homes = the model overpredicts where prebound is strongest |
| H077 | Homes built pre-1940 have systematically different residual patterns | 45% | OPEN | Historic construction has thermal mass benefits not captured by DEAP steady-state method |
| H078 | Heat pump homes have smaller residuals than oil boiler homes | 40% | OPEN | Heat pump COP in DEAP may be more accurate than boiler efficiency in DEAP |
| H079 | Rural detached homes have larger residuals than urban terraced | 45% | OPEN | Rural homes have more wind exposure and different heating patterns |
| H080 | Post-2019 nZEB homes have smallest residuals | 55% | OPEN | nZEB calculation methodology is most refined; less room for error |

## Additional Hypotheses (extending to 100+)

| # | Hypothesis | Prior | Status | Mechanism |
|---|-----------|-------|--------|-----------|
| H081 | Polynomial features (year_built^2, floor_area^2) | 30% | OPEN | Nonlinear relationships may exist |
| H082 | Binned floor area (small/medium/large/very large) | 35% | OPEN | Categorical bins may capture size class effects |
| H083 | Heating fuel cost proxy (oil price vs gas price vs electricity price) | 25% | OPEN | Fuel cost may correlate with actual heating behaviour via prebound |
| H084 | Building orientation if available (south-facing = more solar) | 30% | OPEN | Orientation affects solar gains significantly |
| H085 | Number of external walls (end-terrace vs mid-terrace) | 50% | OPEN | Exposed wall count directly affects fabric heat loss |
| H086 | Storey height (affects volume for ventilation loss) | 30% | OPEN | Older homes have higher ceilings |
| H087 | Dual-aspect vs single-aspect for apartments | 25% | OPEN | Cross-ventilation and solar gains differ |
| H088 | Presence of conservatory/sunroom | 20% | OPEN | Unheated conservatory acts as thermal buffer |
| H089 | Is_corner_unit for apartments | 25% | OPEN | Corner units have more exposed surface area |
| H090 | Fuel type ordinal encoding (solid fuel < oil < gas < heat pump) | 50% | OPEN | Natural ordering by efficiency |
| H091 | Wall construction detail: 9-inch solid vs 13.5-inch vs cavity | 55% | OPEN | Finer wall classification may capture U-value variation |
| H092 | Insulation brand/specification if encoded | 20% | OPEN | Different insulation materials have different lambda values |
| H093 | MVHR flag (mechanical ventilation with heat recovery) | 50% | OPEN | MVHR substantially reduces ventilation heat loss in tight buildings |
| H094 | Renewable energy contribution percentage | 45% | OPEN | BER accounts for on-site renewable contribution |
| H095 | CO2 emissions as secondary target for multi-task learning | 25% | OPEN | CO2 and energy are correlated but not identical targets |
| H096 | BER assessor company (not just individual) | 30% | OPEN | Company-level calibration effects |
| H097 | Month of assessment (seasonal bias in surveying) | 20% | OPEN | Summer surveys may miss heating system issues |
| H098 | Distance to nearest Met Eireann station | 20% | OPEN | Climate data accuracy depends on proximity to weather station |
| H099 | County population density as urban/rural proxy | 40% | OPEN | More readily available than direct urban/rural flag |
| H100 | Dwelling age at assessment x insulation interaction | 35% | OPEN | Old homes assessed recently may have been retrofitted |
| H101 | Multi-target: predict both energy value and CO2 | 25% | OPEN | Joint prediction may improve feature learning |
| H102 | Feature selection by SHAP importance (top 15 features only) | 40% | OPEN | Removing noise features may improve generalisation |
| H103 | Ensemble of XGBoost + ExtraTrees (if both competitive in tournament) | 30% | OPEN | Ensemble may improve over single model |
| H104 | Drop floor area feature to test if model still works | 35% | OPEN | Floor area may be redundant since target is per-m2 |
| H105 | Add noise label smoothing for borderline BER ratings | 15% | OPEN | Homes near rating boundaries have less certain values |
