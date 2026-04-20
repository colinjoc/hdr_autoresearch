# Design Variables: Asset Correlation Regimes

The variables we will compute, with source, sampling choices, and rationale grounded in the Phase 0 literature.

## Primary asset returns (daily log returns)

| Symbol | Description | Source | Coverage | Notes |
|--------|-------------|--------|----------|-------|
| SPY | S&P 500 ETF | Yahoo Finance | 2004-01-01 → today | Primary US equity benchmark |
| QQQ | Nasdaq-100 ETF | Yahoo Finance | 2004-01-01 → today | Tech-weighted equity, for BTC comparison |
| GLD | SPDR Gold Trust ETF | Yahoo Finance | 2004-11-18 → today | Gold proxy; spot gold series also available from FRED (GOLDPMGBD228NLBM) |
| BTC-USD | Bitcoin / USD spot | Yahoo Finance | 2014-09-17 → today | Primary crypto; pre-2014 BTC is thinly traded and unreliable |
| CL=F | WTI crude futures | Yahoo Finance | 2004-01-01 → today | Continuous front-month |
| DBC | Invesco DB Commodity Index Tracking Fund | Yahoo Finance | 2006-02-03 → today | Broad commodity ETF proxy; BCOM directly is not a traded series |
| UUP | Invesco US Dollar Bullish ETF | Yahoo Finance | 2007-02-20 → today | DXY proxy, traded form |

For all series: use adjusted close; compute log returns as log(P_t / P_{t-1}); drop the first observation.

## Macro regime variables (monthly or weekly, forward-filled to daily)

| Variable | Description | Source (FRED ID) | Frequency | Regime buckets |
|----------|-------------|-----------------|-----------|----------------|
| FEDFUNDS | Effective Fed funds rate | FRED `FEDFUNDS` | monthly | Slope = rate - rate_6mo_ago; buckets {cutting: slope < −0.25, steady: |slope| ≤ 0.25, hiking: slope > 0.25} |
| CPI_YOY | Headline CPI YoY | FRED `CPIAUCSL` (12-month % change) | monthly | Buckets {low: < 2%, target: [2, 3], elevated: [3, 5], high: > 5%} |
| DXY | Trade-weighted US dollar index | FRED `DTWEXBGS` | daily | 6-month Δ buckets {weakening: < −3%, stable: [−3, +3], strengthening: > +3%} |
| GPR | Geopolitical Risk Index | Caldara-Iacoviello (https://www.matteoiacoviello.com/gpr.htm) | monthly | Quartile buckets of 20-year rolling distribution |
| DEFICIT | Federal deficit / GDP | FRED `FYFSGDA188S` | annual | Buckets {low: <3%, moderate: [3, 5], elevated: [5, 7], high: >7%} |
| VIX | CBOE volatility index | FRED `VIXCLS` | daily | Used as secondary stress indicator |
| EPU | Economic Policy Uncertainty | Baker-Bloom-Davis (policyuncertainty.com) | monthly | Top-quartile indicator |

## Rolling correlation definitions (primary statistics)

Compute three window lengths, all on log returns, all reported. This matches literature practice (P007 wavelet multi-horizon, P026 long-horizon).

| Variable | Formula | Window |
|----------|---------|--------|
| `corr_30` | Pearson(log-return pair, 30-day rolling) | 30 trading days |
| `corr_90` | Pearson(log-return pair, 90-day rolling) | 90 trading days (primary) |
| `corr_250` | Pearson(log-return pair, 250-day rolling) | 250 trading days (~1 year) |
| `corr_spearman_90` | Spearman rank correlation, 90-day | 90 trading days |
| `corr_kendall_90` | Kendall τ, 90-day | 90 trading days |

Pairs to compute for ALL correlations: SPY-GLD, SPY-BTC, SPY-WTI, SPY-DBC, SPY-UUP, GLD-BTC, GLD-UUP, GLD-WTI, BTC-QQQ.

## Model families for the tournament (Phase 1)

Per `program.md` exploratory requirement of ≥ 2 families including a linear sanity check:

1. **Linear baseline (sanity check)**: OLS of rolling correlation ~ macro regime dummies + trend.
2. **DCC-GARCH(1,1)** per pair, with (α, β) parameters estimated via quasi-ML (Engle 2002, P003).
3. **Markov-switching** 2-state model on rolling-correlation time series (Hamilton 1989, P009; Ang-Bekaert 2002, P008).
4. **Random forest / gradient boosting** predicting current correlation from macro regime features (non-parametric sanity check).

## Regime-conditioning strategy

For each pair × rolling-correlation window, compute:

- Unconditional mean, median, quartiles over full sample.
- Regime-conditional mean of correlation for each bucket of each macro variable (single-variable conditioning).
- Regression: `corr ~ CPI_bucket + DXY_bucket + FedSlope_bucket + GPR_quartile + post_2024_dummy`.
- Interaction regression to test whether post-2024 coefficient remains significant after controls (direct test of H11).

## Data-source fallbacks

| Variable | Primary | Fallback |
|----------|---------|----------|
| BTC-USD | Yahoo Finance | CoinGecko public API; Coinbase/Kraken historical CSV |
| DXY | FRED DTWEXBGS | Yahoo UUP ETF as traded proxy; St. Louis Fed daily dollar index |
| BCOM | DBC ETF | GSG ETF; spot commodity index from Bloomberg terminal if accessible |
| GPR | Iacoviello personal site | Mirror at Federal Reserve Board |
| CPI | FRED CPIAUCSL | BLS direct CSV download |

## Identified data-access risks (flags for Phase 0.5)

- **BTC pre-2014 data**: Yahoo's series starts 2014-09-17. For genuine coverage back to ~2010 we'd need CoinGecko or Bitstamp historical data. For this project 2014+ is sufficient since ETF narrative is post-2020.
- **GPR index licensing**: free for non-commercial use; download format is CSV from Iacoviello's site. Not expected to be a blocker.
- **Yahoo Finance BTC-USD gaps**: sometimes has missing weekend data or late-evening adjustment issues. Need a forward-fill + sanity check.
- **DBC inception 2006**: for 2004–2006 broad commodity, either use GSCI futures data (only through Bloomberg) or drop those two years from the BCOM-SPY analysis. Not fatal — SPY-WTI alone covers the commodity story from 2004.
- **All data sources are free and public**. No registered APIs required.
