# Feature Candidates: Asset Correlation Regimes

Features we'll compute in the Phase 0.5 baseline panel and Phase 1 tournament. Each row lists the feature, its formula, the paper(s) that motivate it, and the primary research-queue hypothesis it addresses.

## A. Correlation features (dependent variables and correlated-series features)

| Feature | Formula | Motivating paper(s) | Targets |
|---------|---------|---------------------|---------|
| `corr_90_SPY_GLD` | 90-day rolling Pearson(SPY log returns, GLD log returns) | P004, P005, P007 | H1, H10, H22 |
| `corr_90_SPY_BTC` | 90-day rolling Pearson(SPY, BTC-USD) | P012, P013, P015 | H2, H11, H23 |
| `corr_90_QQQ_BTC` | 90-day rolling Pearson(QQQ, BTC-USD) | P011, P044 | H3 |
| `corr_90_SPY_WTI` | 90-day rolling Pearson(SPY, CL=F) | P021, P022 | H8 |
| `corr_90_SPY_DBC` | 90-day rolling Pearson(SPY, DBC) | P022, P023 | H9 |
| `corr_90_GLD_BTC` | 90-day rolling Pearson(GLD, BTC-USD) | P045 | H17 |
| `corr_90_GLD_UUP` | 90-day rolling Pearson(GLD, UUP) | P006 | H20 |
| `corr_30_*`, `corr_250_*` | Same pairs, 30- and 250-day windows | P007 (wavelets) | H16, H18 |
| `corr_spearman_90_*`, `corr_kendall_90_*` | Rank-correlation analogues | P002 (extreme-tail) | H13 |
| `dcc_corr_*` | DCC-GARCH(1,1) conditional correlation | P003 | H12 |
| `dcc_alpha`, `dcc_beta` | DCC parameters per pair | P003 | H12 |
| `corr_FR_adj_90_*` | Forbes-Rigobon heteroskedasticity-corrected 90-day correlation | P001 | H14 |
| `avg_pairwise_corr` | Mean of all six pairwise correlations in the asset basket | P008, P024 | H24 |

## B. Macroeconomic regime features (conditioning variables)

| Feature | Formula | Motivating paper(s) | Targets |
|---------|---------|---------------------|---------|
| `fed_funds_6m_slope` | FEDFUNDS_t − FEDFUNDS_{t−6mo} | P024 | H4 |
| `fed_regime` | {cutting, steady, hiking} from slope buckets | P024 | H4 |
| `cpi_yoy` | 12-month log change in CPIAUCSL | P026, P027, P030 | H6, H22 |
| `cpi_regime` | {low, target, elevated, high} from CPI buckets | P026, P030 | H6, H10 |
| `dxy_6m_change` | Log change of trade-weighted US dollar over 6 months | P041, P042, P043 | H7, H10, H20 |
| `dxy_regime` | {weakening, stable, strengthening} from 6m change | P041, P042 | H7 |
| `gpr_level` | Caldara-Iacoviello GPR index, monthly | P029, P040 | H5, H21 |
| `gpr_quartile` | Quartile of GPR against 20-year rolling distribution | P029 | H5, H21 |
| `deficit_gdp` | Federal deficit as fraction of GDP | P034, P035 | H25 |
| `vix_level` | Daily VIX close | P032 | H19, H24 |
| `epu_level` | BBD EPU index | P028 | (secondary control) |
| `dollar_cycle_phase` | Global dollar cycle phase indicator (Obstfeld-Zhou) | P043 | H7 |

## C. Structural-break / time features

| Feature | Formula | Motivating paper(s) | Targets |
|---------|---------|---------------------|---------|
| `post_2008_dummy` | 1 if date ≥ 2008-09-15 (Lehman) | P022, P023 | H8, H9 |
| `post_2020_dummy` | 1 if date ≥ 2020-03-01 (COVID crash) | P015, P016 | H15, H24 |
| `post_ETF_dummy` | 1 if date ≥ 2024-01-11 (BTC spot ETF approval) | P044, P045 | H2, H11 |
| `regime_state_MSM` | 2-state Markov-switching state inference | P008, P009 | H15 |
| `year_decade` | Decade bucket (2000s / 2010s / 2020s) | — | H24 |

## D. Asset-state features

| Feature | Formula | Motivating paper(s) | Targets |
|---------|---------|---------------------|---------|
| `spy_200d_trend` | sign of SPY log return over 200 days | P002 (asymmetric tails) | H23 |
| `spy_drawdown` | (SPY_t / max(SPY_{t−250}...SPY_t)) − 1 | P002, P008 | H22, H24 |
| `spy_vol_realised_30d` | realised 30-day SPY volatility | P003, P001 | H14 |
| `btc_etf_aum` | sum of AUM across BTC spot ETFs (post-Jan-2024) | P044, P045 | H2, H11 |
| `gold_real_rate` | gold return net of 10Y TIPS real yield | P031, P030 | H6 |

## E. Interaction features (second-order)

- `cpi_regime × dxy_regime` → identifies "debasement" regime (high CPI × weakening DXY)
- `fed_regime × gpr_quartile` → distinguishes geopolitical panic under tight vs loose Fed
- `post_ETF_dummy × vix_level` → tests whether post-ETF BTC-equity co-movement is vol-dependent (H23)
- `post_2008_dummy × commodity_index_membership` → tests Tang-Xiong financialisation channel (P022)

## Feature-engineering priority

Tier 1 (must-have for Phase 0.5 baseline):
- All 90-day rolling Pearson correlations for SPY pairs.
- `fed_regime`, `cpi_regime`, `dxy_regime`, `gpr_quartile`.
- `post_2020_dummy`, `post_ETF_dummy`.

Tier 2 (for Phase 1 tournament):
- DCC-GARCH outputs for at least SPY-GLD and SPY-BTC.
- Markov-switching state time series.
- Forbes-Rigobon-adjusted correlation.

Tier 3 (for Phase 2 iteration):
- Interaction features.
- Alternative-window correlations (30d, 250d).
- Rank-correlation versions.
- BTC-ETF AUM feature.
