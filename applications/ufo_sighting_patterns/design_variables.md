# Design Variables

This project is a decomposition/analysis study (Option C). The "design variables" are the analytical choices that define the decomposition and can be varied to test robustness.

## Primary Design Variables

| Variable | Range | Default | Justification |
|----------|-------|---------|---------------|
| temporal_resolution | daily/weekly/monthly/yearly | monthly | Trade-off: noise vs trend visibility |
| year_range | 1990-2024, 1950-2024, 2000-2024 | 1990-2024 | Modern era with reliable data |
| spatial_unit | point/county/state/country | state | MAUP sensitivity |
| population_denominator | 2000/2010/2020 Census | 2020 | Per-capita normalization |
| shape_grouping | raw (15+) / collapsed (5) / binary (light vs craft) | raw | Category granularity |
| starlink_cutoff | May 2019 / Jan 2020 | May 2019 | First Starlink launch |
| dbscan_eps | 0.1-2.0 degrees | 0.5 | Spatial cluster radius |
| dbscan_min_samples | 5-50 | 20 | Minimum cluster size |
| kde_bandwidth | 0.1-2.0 degrees | 0.5 | Smoothing parameter |
| classifier_family | logistic/RF/XGB/LightGBM | logistic | Explained-vs-unexplained prediction |
| topic_model_n_topics | 5-30 | 10 | LDA topic count |
| duration_outlier_cap | 99th/99.5th/99.9th percentile | 99th | Cap extreme durations |
| text_min_length | 0/10/50/100 characters | 0 | Quality filter |
| bootstrap_n | 100/1000/5000 | 1000 | CI precision |

## Robustness Dimensions
- Pre/post internet era (pre-2000 vs post-2000)
- US-only vs all countries
- With vs without July 4th ± 3 days
- With vs without clock-hour-rounded entries
- Kaggle subset vs full structured dataset (overlap period)
- Shape taxonomy: raw vs collapsed
- Duration: including vs excluding missing
