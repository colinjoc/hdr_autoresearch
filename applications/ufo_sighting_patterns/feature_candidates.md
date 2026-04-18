# Feature Candidates

## Temporal Features
| Feature | Source | Computation | Justification |
|---------|--------|-------------|---------------|
| year | Occurred field | Extract year | Long-term trend; internet adoption effect |
| month | Occurred field | Extract month (1-12) | Seasonal pattern; summer peak |
| hour | Occurred field | Extract hour (0-23) | Time-of-day; dusk peak |
| day_of_week | Occurred field | 0=Mon..6=Sun | Weekend vs weekday leisure |
| day_of_year | Occurred field | 1-366 | Fine seasonal resolution |
| is_weekend | day_of_week | Sat/Sun flag | Leisure vs work observing |
| is_summer | month | Jun-Aug flag | Dark-sky + outdoor activity |
| is_july4_window | date | July 1-7 flag | Fireworks contamination |
| is_holiday | date | Major holidays | New Year, July 4, Halloween |
| is_starlink_era | year/month | >=May 2019 | Post-Starlink period |
| reporting_lag_days | Occurred-Reported | Timedelta in days | Report freshness; retrospective indicator |
| clock_hour_rounding | minute | minute==0 flag | Digit preference bias indicator |

## Shape/Categorical Features
| Feature | Source | Computation | Justification |
|---------|--------|-------------|---------------|
| shape | Shape field | Categorical (15+ levels) | Object taxonomy |
| shape_is_light | Shape | Light/Orb/Flash/Fireball | Astronomical misidentification proxy |
| shape_is_craft | Shape | Disk/Triangle/Rectangle/Cigar | "Structured craft" reports |
| shape_is_formation | Shape | Formation flag | Starlink/satellite train proxy |
| duration_seconds | Duration | Parse to seconds | Observation quality; satellite transit ~30s |
| log_duration | duration_seconds | log10(duration) | Skewed distribution normalization |
| n_observers | No of observers | Numeric | Corroboration; 1 vs multiple |

## Text Features
| Feature | Source | Computation | Justification |
|---------|--------|-------------|---------------|
| text_length | Text field | Character count | Report detail/quality proxy |
| summary_length | Summary | Character count | Brief description quality |
| has_characteristics | Characteristics | Non-null flag | Structured observation metadata |
| n_characteristics | Characteristics | Count of listed items | Observation detail richness |
| mention_satellite | Text | Keyword search | Self-identified satellite |
| mention_starlink | Text | Keyword search | Self-identified Starlink |
| mention_aircraft | Text | Keyword search | Self-identified aircraft |
| mention_military | Text | Keyword search | Military-related report |

## Spatial Features (Kaggle geocoded subset)
| Feature | Source | Computation | Justification |
|---------|--------|-------------|---------------|
| latitude | lat field | Numeric | North-south position |
| longitude | lon field | Numeric | East-west position |
| state | state field | US state code | State-level aggregation |
| country | country field | Country code | National comparison |
| state_population | Census join | 2020 Census population | Denominator for per-capita |
| sightings_per_capita | count/pop | Normalized rate | Population-adjusted intensity |

## Derived/Interaction Features
| Feature | Computation | Justification |
|---------|-------------|---------------|
| shape_x_hour | shape * hour_bin | Lights at night, disks by day |
| shape_x_era | shape * year_bin | Shape evolution over time |
| duration_x_shape | duration * shape | Short formations = satellite |
| weekend_x_hour | weekend * hour | Weekend evening peak |
| text_length_x_explanation | text_length * has_explanation | Detail predicts explainability |
