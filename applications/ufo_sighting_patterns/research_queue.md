# Research Queue

## Format: ID | Hypothesis | Prior | Impact | Mechanism | Design Variable | Metric | Baseline | Status

### Temporal Patterns (H001-H025)
| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|----|-----------|-------|--------|-----------|-----|--------|----------|--------|
| H001 | Annual sighting count peaked 2012-2014 | 0.80 | 3,2,3=8 | Internet saturation; NUFORC web form adoption leveled off | year_range | peak_year | None | OPEN |
| H002 | Sightings show strong summer seasonality (Jul-Aug peak) | 0.85 | 2,1,3=6 | Dark sky + outdoor leisure; longer evenings | month | summer_ratio | uniform | OPEN |
| H003 | Dusk peak at 8-10 PM dominates time-of-day distribution | 0.85 | 2,1,3=6 | Transition lighting; observers still outdoors | hour | peak_hour | uniform | OPEN |
| H004 | Weekend sightings are elevated relative to weekdays | 0.70 | 2,1,2=5 | Leisure time; outdoor activities; socializing outdoors | day_of_week | weekend_rate_ratio | 2/7 | OPEN |
| H005 | July 4th ± 3 days shows anomalous spike from fireworks | 0.80 | 2,1,3=6 | Fireworks misidentified as UFOs | is_july4_window | jul4_spike_ratio | weekly_mean | OPEN |
| H006 | New Year's Eve shows spike from fireworks/lanterns | 0.60 | 2,1,2=5 | Fireworks + Chinese lanterns | is_holiday | nye_spike_ratio | weekly_mean | OPEN |
| H007 | Halloween shows no significant spike | 0.70 | 1,1,2=4 | No aerial stimuli specific to Halloween | is_holiday | halloween_ratio | weekly_mean | OPEN |
| H008 | Monthly sighting counts are overdispersed (NB > Poisson) | 0.85 | 2,1,2=5 | Media-driven clustering; social contagion | temporal_resolution | overdispersion_test | Poisson | OPEN |
| H009 | Sighting trend is non-monotonic: growth then plateau/decline | 0.75 | 2,2,2=6 | Internet adoption curve saturation | year_range | trend_shape | linear | OPEN |
| H010 | STL residuals correlate with major media events | 0.55 | 3,2,2=7 | Availability heuristic; media priming | temporal_resolution | residual_media_corr | zero | OPEN |
| H011 | Post-2020 sightings declined (pandemic indoor shift) | 0.50 | 2,2,2=6 | COVID lockdowns; fewer outdoor observers | year_range | 2020_vs_2019 | pre-2020 trend | OPEN |
| H012 | Dawn (4-6 AM) reports are rarer than midnight reports | 0.75 | 1,1,2=4 | Fewer observers awake at dawn | hour | dawn_vs_midnight | equal | OPEN |
| H013 | Clock-hour rounding rate decreased over time | 0.40 | 2,2,2=6 | Digital devices reduce rounding | year_range | rounding_rate_trend | 41% | OPEN |
| H014 | Reporting lag decreased over time (faster web submission) | 0.70 | 2,2,2=6 | Smartphone + internet access | year_range | median_lag_trend | early_2000s | OPEN |
| H015 | Reports submitted same day have shorter text | 0.55 | 1,2,1=4 | Quick reports less detailed | reporting_lag_days | text_length_corr | no_correlation | OPEN |
| H016 | Spring equinox/fall equinox show no special pattern | 0.75 | 1,1,1=3 | No mechanism; null hypothesis | day_of_year | equinox_ratio | weekly_mean | OPEN |
| H017 | Friday evenings show highest sighting rate | 0.50 | 1,1,2=4 | Start of weekend leisure; socializing | day_of_week | friday_rate | mean_daily | OPEN |
| H018 | December shows reduced sighting rate (cold, cloudy, indoor) | 0.60 | 1,1,2=4 | Weather drives outdoor exposure | month | december_ratio | mean_monthly | OPEN |
| H019 | Sighting rate tracks sunset time across months | 0.65 | 2,2,3=7 | Dusk availability; more dark leisure hours in summer | month | sunset_correlation | no_correlation | OPEN |
| H020 | Post-2017 UAP media coverage (NYT article) increased reports | 0.55 | 2,2,2=6 | Dec 2017 NYT AATIP article; media priming | year_range | post_2017_change | pre-2017 trend | OPEN |
| H021 | 2021 UAP report (ODNI) spiked NUFORC submissions | 0.45 | 2,2,2=6 | June 2021 ODNI report; media attention | year_range | 2021_spike | monthly_mean | OPEN |
| H022 | Multi-observer reports (n>1) have different temporal patterns | 0.40 | 2,2,2=6 | Group sightings require multiple people outdoors together | n_observers | multi_vs_single_temporal | single_observer | OPEN |
| H023 | Sighting duration is bimodal (brief flashes vs extended observations) | 0.60 | 2,2,2=6 | Two different phenomena types | duration_seconds | bimodality_test | unimodal | OPEN |
| H024 | Very short durations (<5 sec) are more common post-2015 | 0.45 | 2,2,2=6 | Camera use captures brief events | duration_seconds | short_rate_trend | pre-2015 | OPEN |
| H025 | Median sighting duration decreased over decades | 0.45 | 2,2,2=6 | Attention span; quick video; brief satellite transits | year_range | median_duration_trend | 1990s_median | OPEN |

### Shape Evolution (H026-H040)
| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|----|-----------|-------|--------|-----------|-----|--------|----------|--------|
| H026 | "Disk" reports declined as fraction of total since 1990 | 0.80 | 2,1,3=6 | Cultural shift away from "flying saucer" archetype | shape_grouping | disk_fraction_trend | 1990s_fraction | OPEN |
| H027 | "Light" became the dominant shape category by 2010 | 0.75 | 2,1,3=6 | Generic description for satellite/aircraft/ISS | shape_grouping | light_dominance_year | none | OPEN |
| H028 | "Triangle" reports peaked in the 1990s-2000s | 0.55 | 2,2,2=6 | Belgian wave (1989-90); stealth aircraft programs | shape_grouping | triangle_peak_decade | uniform | OPEN |
| H029 | "Formation" reports spiked post-May 2019 (Starlink) | 0.75 | 3,2,3=8 | Starlink satellite train misidentification | is_starlink_era | formation_spike_ratio | pre-2019 | OPEN |
| H030 | "Orb" is a 2010s+ neologism; rare before 2005 | 0.65 | 2,2,2=6 | Cultural/linguistic shift in reporting | shape_grouping | orb_emergence_year | none | OPEN |
| H031 | Shape category correlates with time-of-day (lights at night, disks by day) | 0.75 | 2,1,3=6 | Perceptual conditions determine shape description | shape_x_hour | interaction_chi2 | independence | OPEN |
| H032 | "Fireball" peaks correlate with meteor shower dates | 0.50 | 3,3,3=9 | Meteor misidentification during Perseids/Geminids | shape_grouping | fireball_meteor_corr | no_correlation | OPEN |
| H033 | "Cigar" shape declined similarly to "disk" | 0.65 | 1,1,2=4 | Same cultural archetype; 1950s imagery | shape_grouping | cigar_fraction_trend | 1990s_fraction | OPEN |
| H034 | "Chevron/V-shape" reports have distinctive time-of-day profile | 0.45 | 2,2,2=6 | Possible aircraft formation or geese | shape_grouping | chevron_hour_profile | overall_hour_profile | OPEN |
| H035 | "Changing" shape reports are longer duration | 0.55 | 1,2,2=5 | Longer observation allows noting shape changes | duration_seconds | changing_vs_other_duration | median_duration | OPEN |
| H036 | Shape diversity (n unique shapes/year) increased over time | 0.65 | 1,2,2=5 | More descriptive options; more diverse stimuli | shape_grouping | shape_entropy_trend | early_entropy | OPEN |
| H037 | "Sphere" and "Circle" have nearly identical characteristics | 0.70 | 1,1,2=4 | Redundant categories | shape_grouping | sphere_circle_similarity | random | OPEN |
| H038 | "Flash" reports are very short duration (median <10 sec) | 0.75 | 1,1,2=4 | Flash implies momentary | duration_seconds | flash_median_duration | overall_median | OPEN |
| H039 | "Rectangle" reports increased with drone popularity (post-2015) | 0.40 | 2,2,2=6 | Quadcopter drone silhouettes | shape_grouping | rectangle_trend | pre-2015 | OPEN |
| H040 | Shape-year chi-square test shows significant association | 0.90 | 2,1,2=5 | Shape distribution evolved; confirmed by literature | shape_x_era | chi2_pvalue | independence | OPEN |

### Spatial Patterns (H041-H060)
| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|----|-----------|-------|--------|-----------|-----|--------|----------|--------|
| H041 | California, Washington, and Arizona have highest per-capita rates | 0.60 | 2,1,2=5 | Western states; dark skies; outdoor culture | state_population | top_states | uniform | OPEN |
| H042 | Per-capita sighting rate is higher in western US | 0.75 | 2,1,3=6 | Open terrain; dark skies; Medina et al. confirmed | spatial_unit | west_vs_east_ratio | 1.0 | OPEN |
| H043 | DBSCAN finds ≥10 significant spatial clusters | 0.70 | 2,2,2=6 | Population centers + specific hotspot locations | dbscan_eps | n_clusters | 0 | OPEN |
| H044 | Largest spatial cluster is centered on a major metro area | 0.80 | 1,1,2=4 | Population artifact | dbscan_eps | largest_cluster_location | random | OPEN |
| H045 | After population normalization, urban clusters weaken | 0.70 | 2,2,3=7 | Removing population confound | population_denominator | normalized_cluster_significance | raw | OPEN |
| H046 | Sightings per capita correlate negatively with population density | 0.50 | 2,2,3=7 | Dark sky access; light pollution reduces visibility | spatial_unit | density_correlation | zero | OPEN |
| H047 | Military base proximity (<50 km) elevates sighting rate | 0.60 | 3,2,3=8 | Aircraft misidentification; heightened attention | spatial_unit | base_proximity_rate_ratio | >50km | OPEN |
| H048 | Major airport proximity (<30 km) elevates sighting rate | 0.55 | 2,2,2=6 | Aircraft approach/departure misidentification | spatial_unit | airport_proximity_rate_ratio | >30km | OPEN |
| H049 | Launch site proximity (<100 km) shows distinct patterns | 0.50 | 2,3,2=7 | Rocket launch misidentification | spatial_unit | launch_site_rate | >100km | OPEN |
| H050 | US sighting rate is 3-5x higher per capita than Canada | 0.50 | 2,2,2=6 | Reporting culture; NUFORC accessibility | country | us_vs_canada_ratio | 1.0 | OPEN |
| H051 | UK sighting rate is lower per capita than US | 0.65 | 1,1,2=4 | Different reporting channels (MoD desk vs NUFORC) | country | us_vs_uk_ratio | 1.0 | OPEN |
| H052 | Sighting clusters are stable across decades (same locations) | 0.55 | 2,3,2=7 | Persistent population centers; persistent stimuli | dbscan_eps | cluster_temporal_stability | random | OPEN |
| H053 | State-level sighting rate rank is stable across 5-year periods | 0.65 | 2,2,2=6 | Persistent population/geography | spatial_unit | rank_correlation_5yr | random | OPEN |
| H054 | Pacific coast has higher rate than Atlantic coast | 0.60 | 2,1,2=5 | West-is-best finding; open Pacific horizons | spatial_unit | pacific_vs_atlantic | 1.0 | OPEN |
| H055 | Nevada has anomalously high per-capita rate (Area 51 culture) | 0.50 | 2,2,2=6 | Cultural priming; tourism; military testing | state_population | nevada_rate_zscore | mean_rate | OPEN |
| H056 | Florida has elevated rate (launch site + military + population) | 0.50 | 2,1,2=5 | Cape Canaveral; many military bases; retirees outdoors | state_population | florida_rate_zscore | mean_rate | OPEN |
| H057 | Spatial autocorrelation exists at state level (Moran's I > 0) | 0.65 | 2,1,2=5 | Neighboring states share geography/culture | spatial_unit | morans_i | 0 | OPEN |
| H058 | Top-50 population-normalized hotspots are NOT all metro areas | 0.55 | 3,2,3=8 | Some genuine non-population hotspots | dbscan_eps | non_metro_hotspot_fraction | 0 | OPEN |
| H059 | Rural counties have higher per-capita sighting rates than urban | 0.45 | 2,2,3=7 | Dark skies; fewer distractions; more sky visibility | spatial_unit | rural_vs_urban_rate | 1.0 | OPEN |
| H060 | Hawaiian islands have distinct shape distribution (military Pacific) | 0.35 | 1,2,2=5 | Pacific fleet; unique aerial traffic | state_population | hawaii_shape_chi2 | national | OPEN |

### Starlink and Satellite Effects (H061-H075)
| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|----|-----------|-------|--------|-----------|-----|--------|----------|--------|
| H061 | Post-May-2019 "formation" reports increased >2x | 0.70 | 3,2,3=8 | Starlink train visibility | is_starlink_era | formation_rate_change | pre-2019 | OPEN |
| H062 | Post-May-2019 "light" reports increased | 0.50 | 2,2,2=6 | Individual Starlink satellites visible | is_starlink_era | light_rate_change | pre-2019 | OPEN |
| H063 | Post-May-2019 "disk" reports did NOT increase (control) | 0.80 | 2,1,2=5 | Disk is not Starlink-related; natural control | is_starlink_era | disk_rate_change | pre-2019 | OPEN |
| H064 | NUFORC "Starlink" explanations cluster in first week after launches | 0.55 | 2,3,2=7 | Trains most visible when newly deployed (close together) | is_starlink_era | post_launch_spike | uniform | OPEN |
| H065 | Starlink-era reports mention "line", "row", "train" more frequently | 0.70 | 2,2,2=6 | Descriptive language matches Starlink appearance | is_starlink_era | keyword_frequency_change | pre-2019 | OPEN |
| H066 | ISS pass times correlate with nearby sighting reports | 0.30 | 3,3,3=9 | ISS misidentification; ISS is very bright | temporal_resolution | iss_sighting_correlation | no_correlation | OPEN |
| H067 | Satellite re-entry events produce localized sighting spikes | 0.40 | 2,3,2=7 | Dramatic re-entries visible over wide areas | temporal_resolution | reentry_spike_detection | no_spike | OPEN |
| H068 | "Formation" duration is shorter than "disk" duration | 0.65 | 1,1,2=4 | Satellite trains pass quickly (~30-120 sec) | duration_seconds | formation_vs_disk_duration | equal | OPEN |
| H069 | Starlink-explained reports are 2019-2021 concentrated (novelty) | 0.55 | 2,2,2=6 | Public learned to recognize Starlink over time | is_starlink_era | starlink_explanation_trend | uniform | OPEN |
| H070 | "Flash" reports correlate with Iridium flare predictions | 0.25 | 2,3,2=7 | Iridium satellite flares (before deorbit) | temporal_resolution | flash_iridium_corr | no_correlation | OPEN |
| H071 | The fraction of reports receiving ANY explanation increased post-2019 | 0.55 | 2,2,2=6 | Starlink made some reports easy to explain | is_starlink_era | explanation_rate_trend | pre-2019 | OPEN |
| H072 | Pre-Starlink "formation" reports have different text characteristics | 0.50 | 2,2,2=6 | Pre-2019 formations = aircraft; post-2019 = Starlink | is_starlink_era | text_similarity | same | OPEN |
| H073 | Post-Starlink reports more frequently mention technology keywords | 0.45 | 1,2,1=4 | Awareness of satellite constellations | is_starlink_era | tech_keyword_rate | pre-2019 | OPEN |
| H074 | Starlink effect is stronger at high latitudes (better visibility) | 0.40 | 2,3,2=7 | Starlink trains more visible at higher latitudes | spatial_unit | latitude_starlink_interaction | no_interaction | OPEN |
| H075 | Post-Starlink reports have shorter duration (satellite transits are brief) | 0.55 | 2,2,2=6 | Satellite pass takes 30-120 sec | duration_seconds | post_starlink_duration | pre-2019_duration | OPEN |

### Explanation/Classification (H076-H090)
| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|----|-----------|-------|--------|-----------|-----|--------|----------|--------|
| H076 | Logistic regression can predict explained vs unexplained with AUC>0.75 | 0.55 | 2,2,2=6 | Structured features contain signal | classifier_family | AUC | 0.50 | OPEN |
| H077 | Shape is the strongest predictor of having an explanation | 0.65 | 2,1,2=5 | "Formation" → Starlink; "Fireball" → meteor | classifier_family | feature_importance_rank | none | OPEN |
| H078 | Text length negatively correlates with having explanation | 0.45 | 2,2,2=6 | Longer reports = more unusual events harder to explain | text_min_length | text_length_correlation | no_correlation | OPEN |
| H079 | Multi-observer reports are less likely to have explanations | 0.40 | 2,2,2=6 | Multiple witnesses = less likely trivial explanation | n_observers | multi_obs_explanation_rate | single_obs | OPEN |
| H080 | Post-2019 reports are more likely to have explanations | 0.60 | 2,1,2=5 | Starlink annotations added | is_starlink_era | explanation_rate_post2019 | pre-2019 | OPEN |
| H081 | "Starlink" is the most common explanation type | 0.55 | 2,1,2=5 | 196 Starlink annotations in the data | classifier_family | top_explanation_type | uniform | OPEN |
| H082 | XGBoost outperforms logistic regression for classification | 0.55 | 2,1,2=5 | Non-linear interactions; small positive class | classifier_family | AUC_xgb_vs_lr | LR_AUC | OPEN |
| H083 | Adding text features (TF-IDF) improves classification | 0.50 | 2,2,2=6 | Keywords reveal stimulus type | classifier_family | AUC_with_text | AUC_without_text | OPEN |
| H084 | LDA topic model finds a "satellite/Starlink" topic | 0.65 | 2,2,2=6 | Coherent language pattern for satellite reports | topic_model_n_topics | satellite_topic_coherence | random | OPEN |
| H085 | LDA topic model finds a "fireball/meteor" topic | 0.60 | 2,2,2=6 | Coherent language for meteor descriptions | topic_model_n_topics | meteor_topic_coherence | random | OPEN |
| H086 | Explained reports cluster in few LDA topics | 0.55 | 2,2,2=6 | Explained reports are more stereotyped | topic_model_n_topics | topic_concentration | uniform | OPEN |
| H087 | Random forest feature importance: shape > hour > duration | 0.50 | 2,1,2=5 | Shape is most discriminating | classifier_family | importance_ranking | random | OPEN |
| H088 | Duration <60 sec predicts "satellite" explanation | 0.55 | 2,1,2=5 | Satellite transits are brief | duration_seconds | short_duration_satellite_rate | overall | OPEN |
| H089 | Nighttime reports are harder to explain than daytime | 0.55 | 2,1,2=5 | Fewer reference cues; harder to identify | hour | night_explanation_rate | day_rate | OPEN |
| H090 | Reporting lag >30 days correlates with fewer explanations | 0.40 | 2,2,2=6 | Old reports harder to match to events | reporting_lag_days | lag_explanation_corr | no_correlation | OPEN |

### Reporting Dynamics and Text (H091-H105)
| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|----|-----------|-------|--------|-----------|-----|--------|----------|--------|
| H091 | Median reporting lag is <7 days for post-2010 reports | 0.65 | 1,1,2=4 | Web form accessibility | reporting_lag_days | median_lag | 30_days | OPEN |
| H092 | 1-observer reports are the vast majority (>80%) | 0.70 | 1,1,2=4 | Most sightings are individual | n_observers | single_obs_fraction | 0.50 | OPEN |
| H093 | Reports with >3 observers have different shape distribution | 0.45 | 2,2,2=6 | Group events may be more conspicuous/public | n_observers | multi_obs_shape_chi2 | overall | OPEN |
| H094 | Text length distribution is log-normal | 0.65 | 1,1,1=3 | Natural language text lengths | text_min_length | lognormal_test | other | OPEN |
| H095 | Average text length increased over time | 0.40 | 1,2,1=4 | More thoughtful reports; or longer web forms | year_range | text_length_trend | early_mean | OPEN |
| H096 | Reports mentioning "military" have different shape distribution | 0.50 | 2,2,2=6 | Military-related sightings may be aircraft | text_min_length | military_shape_chi2 | overall | OPEN |
| H097 | Reports mentioning "drone" increased dramatically post-2015 | 0.80 | 2,1,3=6 | Consumer drone proliferation | year_range | drone_mention_trend | pre-2015 | OPEN |
| H098 | Reports from pilots/aviation have distinctive features | 0.40 | 2,3,2=7 | Trained observers; different perceptual frame | text_min_length | pilot_report_features | overall | OPEN |
| H099 | Negative sentiment in text correlates with longer duration | 0.30 | 1,2,1=4 | Extended unexplained events cause more distress | text_min_length | sentiment_duration_corr | no_correlation | OPEN |
| H100 | "Characteristics" field (structured observations) predicts explanation | 0.45 | 2,2,2=6 | Structured observations aid identification | classifier_family | chars_explanation_corr | no_correlation | OPEN |
| H101 | Post-2020 reports show language shifts (UAP vs UFO terminology) | 0.45 | 1,2,1=4 | NASA/DoD terminology change; media adoption | year_range | uap_mention_rate | pre-2020 | OPEN |
| H102 | Country-level text analysis reveals cultural differences | 0.35 | 2,3,2=7 | Different cultural frames for similar stimuli | country | text_similarity_by_country | same | OPEN |
| H103 | Bootstrap CI on annual peak year spans 2-3 years | 0.60 | 2,1,2=5 | Statistical uncertainty on the peak | bootstrap_n | peak_year_ci_width | point_estimate | OPEN |
| H104 | Permutation test confirms day-of-week effect is significant | 0.75 | 1,1,2=4 | Not a random fluctuation | day_of_week | permutation_pvalue | 0.05 | OPEN |
| H105 | Poisson regression: year + month + military explains >50% of deviance | 0.40 | 2,2,2=6 | Structured covariates capture main patterns | classifier_family | deviance_explained | null | OPEN |
