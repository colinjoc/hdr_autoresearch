# Research Queue: Irish Radon Prediction

## Status legend
- OPEN: Not yet tested
- KEEP: Tested, improved, kept
- REVERT: Tested, did not improve, reverted
- BLOCKED: Waiting on dependency

## Geological Feature Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H01 | Adding eU/eTh ratio improves AUC by >1% (uranium enrichment indicator) | 65% | OPEN | Strong literature support (Appleton et al. 2008) |
| H02 | Adding eU_p90 (90th percentile) captures localised hotspots better than mean | 55% | OPEN | High-U pockets within mixed geology |
| H03 | Adding eU_std captures within-area geological variability | 40% | OPEN | Could indicate mixed lithology |
| H04 | Total dose rate (composite 0.0417K+0.604eU+0.310eTh) outperforms eU alone | 30% | OPEN | eU alone may be sufficient |
| H05 | Adding eTh_mean independently improves beyond eU alone | 35% | OPEN | Th correlated with U but captures different mineralogy |
| H06 | Log-transforming eU before input improves model (radon is log-normal) | 50% | OPEN | Literature uses log-transformed radon; may help features too |
| H07 | Adding eU_min captures the "worst-case safe" areas | 25% | OPEN | Minimum uranium defines lower bound |
| H08 | K/eTh ratio indicates granitic vs sedimentary lithology | 40% | OPEN | Ternary radiometric classification |
| H09 | eU^2 (quadratic) captures non-linear dose-response | 35% | OPEN | Radon entry may be nonlinear with uranium |
| H10 | Bedrock age (Carboniferous vs Devonian vs Ordovician) as separate feature | 45% | OPEN | Different ages have different U distributions |

## Quaternary Geology Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H11 | Ordinal quaternary permeability (rock>gravel>sand>thin_till>thick_till>peat) beats raw code | 55% | OPEN | Physical ordering captures permeability gradient |
| H12 | Binary is_rock_surface feature captures maximum radon transport | 50% | OPEN | Rock at surface = no barrier |
| H13 | Binary is_peat feature captures radon barrier effect | 50% | OPEN | Peat is known low-permeability barrier |
| H14 | Interaction: eU × quat_permeability captures supply × pathway | 70% | OPEN | Strong physics: need both source AND pathway |
| H15 | Interaction: is_granite × is_rock_surface = extreme radon risk | 60% | OPEN | Granite source + no barrier |
| H16 | Interaction: is_limestone × quat_permeability captures karst variability | 50% | OPEN | Karst creates preferential pathways |
| H17 | Till thickness proxy (thick vs thin, binary) adds to quaternary code | 40% | OPEN | Thick till attenuates more |
| H18 | Alluvium flag captures river valley radon accumulation | 30% | OPEN | Alluvium can concentrate radon from upstream |

## Lithology Indicator Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H19 | Binary is_granite indicator improves over raw bedrock code | 45% | OPEN | Simplifies the granite signal; may help tree splits |
| H20 | Binary is_limestone indicator captures karst radon source | 45% | OPEN | Carboniferous limestone specific signal |
| H21 | Binary is_black_shale captures organic-rich U-bearing shales | 40% | OPEN | Clare/Kerry shales |
| H22 | Binary is_volcanic captures volcanic rock radon | 25% | OPEN | Minor component in Ireland |
| H23 | Granite × eU interaction captures within-granite U variability | 55% | OPEN | Not all granite is equally uranium-rich |
| H24 | Limestone × eU interaction captures within-limestone radon | 50% | OPEN | Karst variability within limestone |

## Building Feature Hypotheses (BER Data)

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H25 | Area-mean BER rating (ordinal A1=15, G=1) improves AUC | 50% | OPEN | Airtightness proxy at area level |
| H26 | Area-mean air permeability from BER improves AUC | 55% | OPEN | Direct ventilation rate proxy |
| H27 | Fraction of homes with suspended timber floors improves AUC | 45% | OPEN | Timber floors allow more radon entry |
| H28 | Fraction of homes with slab-on-ground floor improves AUC | 40% | OPEN | Slab is better barrier |
| H29 | Fraction of homes with MVHR ventilation adds predictive value | 30% | OPEN | MVHR effect is ambiguous |
| H30 | Fraction with natural ventilation (leaky) adds predictive value | 35% | OPEN | More ventilation = lower radon |
| H31 | Mean year built captures construction era regulation effects | 45% | OPEN | Post-1998 regs include radon barriers |
| H32 | Fraction of homes built post-2011 (modern regs) reduces radon risk | 40% | OPEN | Building regs require radon barriers in HRAs |
| H33 | Fraction of homes built pre-1970 captures old leaky construction | 35% | OPEN | Old homes: mixed effect |
| H34 | Fraction of detached homes (more ground contact) increases radon | 40% | OPEN | Larger foundation = more entry |
| H35 | Mean floor area increases radon risk (more ground contact) | 30% | OPEN | Larger footprint = more entry area |

## Interaction Hypotheses (The Headline Findings)

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H36 | eU × BER_rating_ordinal: high U + high BER = highest risk | 75% | OPEN | THE headline hypothesis; UNVEIL finding at scale |
| H37 | eU × air_permeability: high U + low permeability = highest risk | 70% | OPEN | Direct physics: source × inverse ventilation |
| H38 | is_granite × pct_a_rated: granite + A-rated = danger zone | 65% | OPEN | Specific testable prediction |
| H39 | is_limestone × pct_a_rated: limestone + A-rated = danger zone | 55% | OPEN | Karst + airtight |
| H40 | eU × pct_suspended_timber: high U + timber floor = max entry | 60% | OPEN | Source × entry pathway |
| H41 | eU × pct_post_2011: high U + modern construction (with radon barrier) = reduced risk | 50% | OPEN | Modern regs should help on high-radon geology |
| H42 | BER_rating × quat_permeability: airtight + permeable subsoil = high risk | 55% | OPEN | Building meets geological pathway |
| H43 | BER_rating × is_rock_surface: airtight + rock at surface = extreme risk | 60% | OPEN | No geological barrier + no ventilation barrier |

## Climate Feature Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H44 | Mean wind speed reduces indoor radon (wind-driven ventilation) | 45% | OPEN | Literature support; western coastal effect |
| H45 | Mean annual rainfall has nonlinear effect (moderate rain flushes, heavy rain caps) | 30% | OPEN | Complex soil moisture dynamics |
| H46 | Heating degree days correlate with radon (longer heating = more stack effect) | 35% | OPEN | Winter heating drives radon entry |
| H47 | Mean temperature has weak effect (absorbed by HDD) | 20% | OPEN | Likely redundant with HDD |
| H48 | Wind speed × eU interaction: high wind reduces radon even on high-U geology | 40% | OPEN | Ventilation mitigates source |
| H49 | Rainfall × quat_permeability interaction: rain on permeable soil flushes radon | 30% | OPEN | Complex interaction |

## Spatial Feature Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H50 | Elevation improves AUC (uplands = different geology) | 40% | OPEN | Already in baseline but testing explicitly |
| H51 | Slope reduces radon (drainage reduces accumulation) | 35% | OPEN | Steep slopes drain better |
| H52 | Distance to nearest known HRA captures spatial autocorrelation | 55% | OPEN | Radon is spatially autocorrelated |
| H53 | County as random effect captures unmeasured regional variation | 40% | OPEN | Already used for spatial CV grouping |
| H54 | Latitude captures north-south geological gradient | 25% | OPEN | Already in baseline |
| H55 | Longitude captures east-west geological gradient | 25% | OPEN | Already in baseline |
| H56 | Kriging residual from eU surface as feature | 45% | OPEN | Captures local anomalies vs regional trend |
| H57 | Local Moran's I for eU captures spatial clustering | 35% | OPEN | Hot/cold spot detection |

## Model Configuration Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H58 | Increasing max_depth from 6 to 8 improves on expanded feature set | 40% | OPEN | More features may need deeper trees |
| H59 | Reducing learning_rate from 0.05 to 0.02 with more estimators | 35% | OPEN | Standard regularization tradeoff |
| H60 | Increasing n_estimators from 300 to 500 | 30% | OPEN | May help with more features |
| H61 | Adding L1 regularization (reg_alpha) for feature selection | 35% | OPEN | Many candidate features |
| H62 | Class weight balancing (scale_pos_weight = ~3.5 for 28% positive) | 50% | OPEN | Imbalanced classes |
| H63 | SMOTE oversampling of positive class | 30% | OPEN | Tree methods usually don't benefit |
| H64 | Threshold tuning: optimize F1 threshold instead of 0.5 | 55% | OPEN | Class imbalance suggests non-default threshold |
| H65 | Focal loss instead of binary cross-entropy | 30% | OPEN | For hard-to-classify boundary cases |

## Feature Engineering Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H66 | Log(eU+1) transformation normalizes skewed distribution | 45% | OPEN | eU is right-skewed |
| H67 | Rank transformation of all continuous features | 30% | OPEN | Tree methods are rank-invariant; won't help directly but may help interactions |
| H68 | PCA of radiometric trio (eU, eTh, K) as composite feature | 35% | OPEN | May capture correlated geological signal |
| H69 | Ratio features: eU/K, eTh/K, (eU+eTh)/K | 40% | OPEN | Ternary radiometric ratios |
| H70 | Binning eU into radon potential categories (low/medium/high per Neznal) | 35% | OPEN | Categorical may capture thresholds |
| H71 | Polynomial features: eU^2, eU×eTh, eU×K | 35% | OPEN | Capture nonlinear relationships |
| H72 | Target encoding of bedrock_code (encode by target prevalence) | 45% | OPEN | Many codes; target encoding compresses |
| H73 | Target encoding of quat_code | 40% | OPEN | Fewer codes but still useful |
| H74 | Frequency encoding of bedrock_code (encode by frequency in dataset) | 25% | OPEN | Captures rare lithology effect |

## Validation and Robustness Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H75 | Spatial block CV (by county) is more conservative than random CV by >5% AUC | 80% | OPEN | Strong literature support (Roberts et al. 2017) |
| H76 | Leave-one-county-out CV gives different ranking than 5-fold blocked CV | 40% | OPEN | County-level effects may differ |
| H77 | Training on eastern counties (more data) generalizes to western (less data) | 45% | OPEN | West has different geology and fewer measurements |
| H78 | Performance degrades in areas with <10 measurements per ED | 60% | OPEN | Sparse data = unreliable labels |
| H79 | Calibrated probabilities (Platt scaling) improve F1 at 200 Bq/m3 threshold | 40% | OPEN | Tree models often poorly calibrated |

## Phase 2.5: Retrofit-Radon Tension Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H80 | A-rated homes on granite have HIGHER predicted radon than G-rated on granite | 70% | OPEN | Direct UNVEIL finding test |
| H81 | The BER-radon effect is larger on granite than on sandstone | 65% | OPEN | Effect should scale with geology |
| H82 | Post-2011 homes on high-radon geology have LOWER radon than pre-1970 homes (regs help) | 55% | OPEN | Building regulations include radon barriers |
| H83 | The BER improvement from D→B increases radon risk more than from F→D | 50% | OPEN | Nonlinear airtightness effect |
| H84 | Areas with high retrofit rate AND high eU are under-measured for radon | 60% | OPEN | Hidden danger identification |

## Phase B: Discovery Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H85 | Top 100 "hidden danger" SAs are concentrated in Wicklow/Carlow/Kilkenny (Leinster Granite) | 60% | OPEN | Granite + Dublin commuter belt = high BER + high U |
| H86 | Clare/Kerry (black shales) has underappreciated radon risk in new builds | 45% | OPEN | Tourism-driven new construction on high-U shale |
| H87 | Dublin southern suburbs on Leinster Granite edge have hidden risk | 55% | OPEN | Urban A-rated homes on granite margin |
| H88 | Galway city expansion into granite areas creates new risk | 40% | OPEN | Similar to Dublin but smaller scale |
| H89 | Midlands limestone karst areas with new housing estates are at risk | 45% | OPEN | Housing estate construction on karst |
| H90 | Small Areas with 0 measurements but high predicted risk exist in every county | 70% | OPEN | Measurement coverage is only 3% |

## Ensemble and Stacking Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H91 | Stacking XGBoost + LightGBM improves over best single model by >1% AUC | 35% | OPEN | Typical ensemble marginal gain |
| H92 | Adding Ridge logistic as meta-learner for stacking | 30% | OPEN | Linear stacking of tree models |
| H93 | CatBoost handles categorical geology codes better than label-encoded XGBoost | 40% | OPEN | CatBoost native categorical handling |

## Advanced Spatial Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H94 | Graph neural network on county adjacency graph captures spatial structure | 20% | OPEN | Likely overkill for this problem size |
| H95 | Gaussian process regression residuals from eU surface as feature | 35% | OPEN | GP captures smooth spatial trends |
| H96 | Nearest-5-ED average radon rate as feature (spatial smoothing) | 50% | OPEN | Simple spatial autocorrelation capture |
| H97 | Inverse distance weighted average of neighbouring ED radon rates | 45% | OPEN | More sophisticated spatial feature |

## Data Quality Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H98 | Excluding EDs with <5 measurements improves model reliability | 55% | OPEN | Noisy labels hurt training |
| H99 | Measurement count as feature (more measurements = more reliable label) | 40% | OPEN | Meta-feature about data quality |
| H100 | Downweighting EDs with uncertain labels improves calibration | 35% | OPEN | Uncertainty-aware training |

## Post-Hoc Analysis Hypotheses

| # | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H101 | SHAP analysis shows eU as top feature across all models | 85% | OPEN | Expected from literature |
| H102 | SHAP analysis shows BER×eU interaction in top 5 | 60% | OPEN | Headline interaction |
| H103 | Partial dependence plots show nonlinear eU effect with threshold around 3 ppm | 50% | OPEN | Threshold behavior in radon potential |
| H104 | Feature importance differs significantly between granite-dominated and limestone-dominated counties | 55% | OPEN | Different mechanisms in different geologies |
| H105 | Model disagrees with EPA HRA designation in >5% of areas | 50% | OPEN | Model may flag missed areas |
