# Asset correlation regimes: when do gold, bitcoin, and commodities decouple from equities?

**Project type**: exploratory (personal understanding; not a publication target)
**Date**: 2026-04-20
**Window analysed**: 2004-01-02 → 2026-04-20 (~22 years of daily data)
**Primary statistic**: 90-day rolling Pearson correlation of log returns
**Inference**: moving-block bootstrap (block length 90, 2,000 samples) for all confidence intervals (CIs) on regime means

## TL;DR

Over the last 22 years of daily data, gold (GLD) has been essentially uncorrelated with US equities (SPY); the long-run median of the 90-day rolling correlation is +0.049. In the second half of 2025 and early 2026, the rolling correlation has moved up into a narrow band around +0.17 — the same band the series visited during the 2022 inflation shock and the March–May 2025 tariff episode. Under honest (block-bootstrap) confidence intervals we **cannot** conclude that the current regime is higher than those prior episodes; on point estimate the spring-2025 tariff window is in fact numerically higher (+0.174) than the post-November-2025 window (+0.170). The surviving defensible claim is that SPY-GLD correlation has been sustained in an atypical-but-not-unprecedented positive band. Macro regime variables (Fed, inflation, dollar) cannot predict the rolling correlation out of sample (all R² strongly negative, even with a 90-day embargo between train and test), so the paper ends up descriptive, not inferential.

The BTC result is more robust: SPY-BTC rolling correlation in the current window is +0.51 (block CI [+0.46, +0.55]) against a long-run median of +0.16, and this elevation holds across 30d, 90d, and 250d rolling windows. This is consistent with the post-ETF-approval regime shift described by Baur, Hoang, and Hossain (2025).

WTI and DBC show the opposite: both are **less** correlated with SPY in the current window than their long-run norm.

## 1. Background

The question comes from casual observation through 2024–2026: gold has rallied alongside equities rather than moving opposite to risk, bitcoin has tracked tech, and commodities have looked less like a diversifier than usual. The literature is clear that cross-asset correlations are not constant — Longin and Solnik (2001) showed that equity correlations rise in joint lower tails; Forbes and Rigobon (2002) showed that apparent "contagion" spikes are partly a heteroskedasticity artefact; Engle (2002) parameterised this time-variation directly with Dynamic Conditional Correlation GARCH (DCC-GARCH), showing correlations mean-revert to a long-run level but only slowly.

For gold, Baur and Lucey (2010) defined the modern safe-haven distinction (hedge = uncorrelated on average; safe haven = uncorrelated or negatively correlated in stock-market tails) and found gold is both, but for about 15 trading days only. Akhtaruzzaman, Boubaker, and Sensoy (2021) documented that gold's safe-haven role weakened during COVID-19. For bitcoin, the decisive negative result is Conlon and McGee (2020): during the March 2020 crash BTC fell in lockstep with the S&P 500, and any portfolio allocation to BTC increased downside risk.

For commodities, Tang and Xiong (2012) and Cheng and Xiong (2014) document the "financialisation" structural break: pre-2004 commodity-equity correlation was in a [−0.2, +0.1] band; post-Lehman it jumped to +0.5 and has stayed elevated. So a 2024–2026 observation of positive commodity-equity correlation is not unprecedented — it has been the norm for 15 years.

Full review: `literature_review.md` (45 citations across three themes — correlation regimes, macro drivers, modern safe-haven-failure narratives).

## 2. Data

- **Prices** (Yahoo Finance via `yfinance`, adjusted close): SPY, QQQ, GLD, BTC-USD, WTI (CL=F), DBC (Invesco DB Commodity Index Tracking Fund, broad commodity ETF), DX-Y.NYB (dollar index DXY). Daily, 2004-01-02 → 2026-04-20 (5,609 SPY rows). BTC-USD starts 2014-09-17; DBC 2006-02-06. Everything else is continuous from 2004.
- **Macro** (FRED via `pandas_datareader`): FEDFUNDS (effective Federal Funds Rate), CPIAUCSL (US Consumer Price Index, All Urban Consumers), DTWEXBGS (Broad US Dollar Index), DGS10 (10-year Treasury constant-maturity yield). Ffilled to SPY's trading calendar before use.
- **Geopolitical Risk index** (Caldara and Iacoviello 2022, `gpr.csv`): planned but the public CSV mirror was unreachable on all three fetch attempts. GPR was therefore dropped as a conditioning variable — we note this in Limitations.

All data is real, freely-available, and fetched in `phase05_fetch_and_baseline.py`; no synthetic data is used.

## 3. Method

### 3.1 Primary statistic

For each pair (SPY, X) with X ∈ {GLD, BTC, WTI, DBC}:

ρₜ = Corr(rₜ₋₈₉…rₜ, rₜ₋₈₉ˣ…rₜˣ), r = Δlog P

— a 90-day rolling Pearson correlation of daily log returns. 90 days is the industry-standard window (Bredin, Conlon, and Potì 2015); we report 30d and 250d as robustness checks.

### 3.2 Regime partition

Five categorical regime variables (see `phase2_regime_decomposition.py`). All thresholds are post-hoc, declared in `knowledge_base.md`:

| Variable   | Levels                                        | Cutoff                                          |
|------------|-----------------------------------------------|-------------------------------------------------|
| R1 Fed     | cutting / neutral / hiking                    | ΔFEDFUNDS over 63 days ≷ ±25 bps                |
| R2 CPI     | low / moderate / high                         | CPI Year-over-Year (YoY) 2% / 3.5%              |
| R3 DXY     | weakening / neutral / strengthening           | ΔDXY over 126 days ≷ ±3%                        |
| R4 shock   | normal / growth_shock                         | SPY 90-day drawdown > 15%                       |
| R5 crisis  | normal / GFC / COVID / INFL2022 / TARIFF25 / CURRENT | named windows (post-hoc)                    |

### 3.3 Inference

For each (regime variable, level, target) cell we compute the mean of the rolling correlation series over that cell and a 95% moving-block bootstrap confidence interval (Künsch 1989) with block length 90 days and 2,000 resamples. Block bootstrap is required because each daily observation of a 90-day rolling correlation shares 89 of its 90 days with its neighbour — an IID bootstrap underestimates CI width by a factor of roughly 2–8× on these series (see `block_bootstrap_R5.csv` and §6).

No p-values or multiple-comparisons corrections are reported. We treat this as a descriptive partition, not a hypothesis test.

### 3.4 Predictive tournament (Phase 1)

As an orthogonal check on whether macroeconomic features can predict the rolling-correlation series, we ran a model-family tournament: Ordinary Least Squares (OLS) linear regression, Gradient Boosted Regression (GBR), and Random Forest (RF), each with 5-fold time-series cross-validation (CV) and a 90-day embargo between train and test folds (purged CV, following López de Prado 2018). Features: FEDFUNDS level, FEDFUNDS 3-month slope, CPI YoY, DXY level, DXY 6-month change, DGS10 level, SPY 30-day realised volatility, and seasonal (sin/cos of month). Targets: 90-day rolling SPY-X correlation for each of the four X.

## 4. Results

### 4.1 Unconditional rolling correlation (baseline)

| Pair     | Median | 5th percentile | 95th percentile | n     |
|----------|-------:|---------------:|----------------:|------:|
| SPY-GLD  | +0.049 | −0.406         | +0.486          | 6,625 |
| SPY-BTC  | +0.159 | −0.136         | +0.552          | 4,144 |
| SPY-WTI  | +0.204 | −0.163         | +0.618          | 6,849 |
| SPY-DBC  | +0.339 | −0.060         | +0.700          | 6,315 |
| SPY-QQQ  | +0.918 | +0.816         | +0.971          | 6,852 |

Gold is essentially uncorrelated with SPY on average over 22 years; BTC is weakly positive; WTI and DBC are moderately to strongly positive (consistent with the post-2004 financialisation regime).

### 4.2 R5 crisis-window table (SPY-GLD, block bootstrap)

| Window     | Dates                    | Mean   | 95% CI (block)     | n   |
|------------|--------------------------|-------:|--------------------|----:|
| GFC (Global Financial Crisis) | 2007-09-01 → 2009-03-31 | +0.017 | [−0.244, +0.155] | 397 |
| COVID      | 2020-02-01 → 2020-04-30  | −0.088 | [−0.302, +0.157]   |  90 |
| INFL2022   | 2022-01-01 → 2022-10-31  | +0.037 | [−0.251, +0.165]   | 304 |
| TARIFF25   | 2025-03-01 → 2025-05-31  | +0.174 | [+0.116, +0.256]   |  92 |
| CURRENT    | 2025-11-01 → 2026-04-20  | +0.170 | [+0.156, +0.185]   | 171 |

Three observations:

1. On point estimates TARIFF25 (+0.174) is marginally **higher** than CURRENT (+0.170). These are indistinguishable.
2. Under honest block-bootstrap inference, CURRENT's CI overlaps with TARIFF25, INFL2022 (upper tail), and COVID (upper tail). Only GFC is cleanly below the CURRENT band. "Highest in 22 years" is not a defensible claim.
3. The long-run full-window median (+0.049) **is** below CURRENT's CI — so the two-clauses-together claim "current gold-equity correlation is in a regime we've only visited a handful of times in 22 years, roughly tracking macro-stress episodes" is defensible.

### 4.3 Cross-target current-regime table

| Target | CURRENT mean | Block CI            | Long-run median | Interpretation                                             |
|--------|-------------:|---------------------|----------------:|------------------------------------------------------------|
| GLD    | +0.170       | [+0.156, +0.185]    | +0.049          | Elevated; comparable to other post-2022 stress windows     |
| BTC    | +0.511       | [+0.460, +0.549]    | +0.159          | Strongly elevated; consistent with post-Exchange-Traded Fund (ETF) regime shift |
| WTI    | −0.010       | [−0.114, +0.156]    | +0.204          | Weakly decoupled; block CI touches the long-run median at the upper edge |
| DBC    | +0.149       | [+0.054, +0.332]    | +0.339          | Point estimate about half the long-run commodity-equity correlation, but the block CI reaches up to +0.332 |

The headline narrative "everything moves together in 2025-26" is not supported by the panel: gold and BTC are more correlated with equities than usual, while WTI and DBC's current point estimates sit below their long-run medians with CIs that only weakly separate. The finding is asset-specific, not a pan-cross-asset phenomenon.

### 4.4 Window-length robustness (CURRENT window only)

| Target | 30d rolling | 90d rolling | 250d rolling |
|--------|------------:|------------:|-------------:|
| GLD    | +0.245      | +0.170      | +0.032       |
| BTC    | +0.505      | +0.511      | +0.438       |
| WTI    | −0.079      | −0.010      | −0.000       |
| DBC    | +0.070      | +0.149      | +0.126       |

The SPY-GLD elevation is **window-dependent**: at 250d the point estimate (+0.032) is indistinguishable from the long-run median (+0.049). The BTC elevation is robust across windows. This is an important qualifier to the gold result and is reported alongside the 90d finding rather than buried in an appendix.

### 4.5 CURRENT-start-date sensitivity (SPY-GLD, 90d)

| Start date  | Mean   | Block CI            | n   |
|-------------|-------:|---------------------|----:|
| 2025-09-01  | +0.098 | [+0.030, +0.175]    | 232 |
| 2025-10-01  | +0.142 | [+0.108, +0.179]    | 202 |
| 2025-11-01  | +0.170 | [+0.156, +0.185]    | 171 |
| 2025-12-01  | +0.184 | [+0.162, +0.193]    | 141 |

The elevation intensifies the later we start. This is consistent with the correlation climbing through H2 2025 rather than a discrete regime break. It also means our 2025-11-01 start is not arbitrary — it is near where the series enters the narrow +0.15 to +0.19 band — but earlier start dates give a lower mean, reinforcing that this is a descriptive observation of a trending series, not a step change.

### 4.6 Macro regime decomposition (SPY-GLD highlights, block CIs)

| Regime variable | Level          | Mean   | Block CI            | n     |
|-----------------|----------------|-------:|---------------------|------:|
| R1 Fed cycle    | cutting        | +0.015 | [−0.177, +0.141]    | 722   |
|                 | hiking         | +0.128 | [+0.031, +0.291]    | 888   |
|                 | neutral        | +0.037 | [−0.025, +0.093]    | 5,015 |
| R2 CPI regime   | low (<2%)      | −0.019 | [−0.088, +0.041]    | 3,782 |
|                 | moderate (2–3.5%) | +0.177 | [+0.097, +0.270] | 1,676 |
|                 | high (>3.5%)   | +0.077 | [−0.064, +0.182]    | 1,167 |
| R3 Dollar       | weakening      | +0.093 | [+0.002, +0.201]    | 1,701 |
|                 | neutral        | +0.022 | [−0.054, +0.085]    | 3,175 |
|                 | strengthening  | +0.049 | [−0.033, +0.125]    | 1,749 |

Noteworthy descriptive patterns: SPY-GLD correlation is highest when the Fed is **hiking** (not cutting), when CPI is **moderate** (not high), and when the dollar is **weakening**. The current macro state (cutting cycle expected, CPI moderate, DXY mixed) does not fall cleanly into any single bucket. Full 67-cell table: `regime_correlation_table.csv`.

### 4.7 Predictive tournament (Phase 1)

All three model families produce strongly negative out-of-sample R² on all four targets, even with a 90-day embargo:

| Target      | OLS R²  | GBR R²  | RF R²   | Winner (lowest Mean Absolute Error, MAE) |
|-------------|--------:|--------:|--------:|---------------------|
| SPY-GLD     | −2.85   | −1.32   | −1.33   | GBR                 |
| SPY-BTC     | −8.47   | −2.58   | −1.97   | RF                  |
| SPY-WTI     | −4.83   | −3.80   | −4.01   | GBR                 |
| SPY-DBC     | −0.79   | −0.56   | −1.26   | GBR                 |

A negative R² means the model does worse than predicting the training-set mean. The macro feature set — which includes Fed policy rate, CPI YoY, dollar index, 10-year yield, SPY realised volatility, and seasonal indicators — does not generalise at all. This was the same conclusion from the unembargoed CV; adding the embargo did not rescue it. We interpret this as: given only these slow-moving macro features and only 22 years of data, rolling correlation is not forecastable out of sample. This does **not** mean correlations are unforecastable in general — it means our feature set and panel are not sufficient for it.

## 5. Discussion

The casual-observation premise — that gold, BTC, and commodities have all been positively correlated with equities in 2024–2026 — turns out to be only partially true. Gold and BTC are elevated against their long-run norms; **WTI and DBC are decoupled downward**. A pan-commodity "everything moves together" narrative does not survive the data.

For **gold**, the 90d-window current correlation (+0.170) sits in a band visited before (GFC upper CI, INFL2022 upper CI, TARIFF25 mean +0.174) but not sustained outside crisis labels. The 250d-window current correlation (+0.032) is indistinguishable from the long-run median, meaning the "elevation" is concentrated in the last ~3 months and is not yet a long-horizon phenomenon. The most parsimonious description: gold is behaving like a real asset responding to the same macro factors as equities over short horizons, but reverting to its near-zero long-run equity correlation over longer ones. This is consistent with Iqbal (2017) and Beckmann and Czudaj (2013), whose point is that gold's macro response is regime-dependent and coefficient-unstable.

For **BTC**, the current SPY-BTC correlation (+0.51) is roughly three times the long-run median (+0.16) and the elevation is robust across 30d, 90d, and 250d windows. This is consistent with the post-January-2024 spot-ETF-approval regime shift documented in industry reports and in Baur, Hoang, and Hossain (2025): BTC is now held alongside equities by the same institutional flow and marks with them. The "digital gold" framing is empirically dead for post-2024 data.

For **commodities**, both WTI (−0.010) and DBC (+0.149) sit below their long-run medians in the current window. This is the **opposite** of the casual-observation premise and is worth flagging: during episodes of a strong dollar and actively hawkish trade policy, the commodity-equity link can weaken. This echoes fact 22 of the knowledge base (historical inverse commodity-USD correlation broke down 2021–2023).

On **prediction**, the macro feature set cannot forecast any of the four rolling correlation series out of sample, even with a 90d embargo. Whether this is a fundamental fact about rolling correlations or just a feature-set limitation is unresolved here — richer features (GPR index, realised-correlation momentum, flow-based variables, DCC-GARCH-implied correlation) or fancier targets (predict changes rather than levels, as §5 of López de Prado 2018 recommends) might improve things. The negative result is reported honestly but should be read as a "with this feature set" statement.

## 6. Why the naive IID bootstrap was wrong

The most important methodological finding of this project is that our first pass used an IID bootstrap on the rolling-correlation means, and it produced confidence intervals that were 2–8× too tight. The Phase 2.75 adversarial review caught it. The issue is that a 90-day rolling correlation computed daily has lag-1 autocorrelation ρ₁ in the range 0.87–0.997 across our five crisis windows, giving autoregressive-order-1 (AR(1)) effective sample sizes ranging from 1 to 8 (against raw n ranging from 90 to 397). The effective information content is a tiny fraction of the raw observation count.

Under the IID bootstrap the "CURRENT is highest in 22 years" headline appeared confidently supported. Under the moving-block bootstrap (Künsch 1989) with block length 90, the same claim collapses: three of four prior crises have CIs that overlap CURRENT. The corrected inference is what this paper reports. The first-pass IID-bootstrap claim is retracted and the episode is recorded in `paper_review.md`.

The same review also flagged a silent bug in the inflation-regime dummy: `pd.cut` on CPI YoY produces NaN for the first ~252 days of the sample, and the prior Phase 2 code stringified that NaN into a `"nan"` regime level that received a bootstrap mean. That row has been dropped from `regime_correlation_table.csv` (67 cells, not 68).

## 7. Limitations

- **All R5 crisis windows are post-hoc.** They were chosen after the rolling-correlation series was inspected. `knowledge_base.md` now declares this explicitly with CURRENT-start-date sensitivity in §4.5. Any "current is elevated vs normal" claim is partially circular and should be read as descriptive.
- **Regime thresholds (±25 bps Fed slope, 2%/3.5% CPI, ±3% DXY, 15% drawdown) are post-hoc** and not sensitivity-tested. A reader should not weight "hiking gives higher SPY-GLD correlation" as a robust finding.
- **68 descriptive cells, no multiple-comparisons correction.** We treat the whole Phase 2 partition as descriptive and do not claim any single cell is statistically significant against any null.
- **BTC data begins 2014-09-17.** GFC-era BTC rows are n=0 (handled correctly); COVID is the earliest BTC crisis in our panel.
- **GPR index was unreachable** at every fetch attempt; geopolitical risk is therefore not in the macro conditioning. This is a real gap given the 2022–present geopolitical backdrop.
- **DCC-GARCH** was planned as a robustness tool but is deferred. For an exploratory project the rolling-Pearson + block-bootstrap pipeline is sufficient; publication would require DCC-GARCH triangulation.
- **CURRENT window is 171 trading days** (5.5 months) — 8 effectively-independent observations under AR(1). A conclusion more decisive than "sits in a narrow band around +0.17 that the record has visited but not sustained" would be overreach.
- **No out-of-sample verification of the regime story.** The paper describes a panel and a period; it does not forecast what happens next.

## 8. What was learned

1. **Method matters**: moving to block bootstrap changed the main claim from "highest in 22 years" to "in a narrow band the record has visited before". For rolling-correlation work, IID resampling is not a safe default.
2. **The casual narrative is only partially true**: gold and BTC are elevated, but WTI and DBC are decoupled downward. "Everything moves together" is not the right summary of 2025–2026.
3. **BTC's post-ETF regime shift is the cleanest finding** in the project: correlation with SPY is 3× its long-run median and robust across rolling-window lengths.
4. **Rolling correlations are not forecastable** from our macro feature set with 5-fold embargoed CV. Whether richer features would fix this is an open question.
5. **A reviewer who re-derives the bootstrap from first principles is worth a lot.** The IID-vs-block-bootstrap miss would have survived a casual peer review; the adversarial Phase 2.75 reviewer caught it in a single pass.

## References

See `papers.csv` for the full 45-citation list. Core references cited in this note:

- Akhtaruzzaman, Boubaker, Sensoy (2021). "Is gold a hedge or a safe-haven asset in the COVID–19 crisis?" *Economic Modelling* 102. [P016]
- Baur, Lucey (2010). "Is gold a hedge or a safe haven?" *Financial Review* 45. [P004]
- Beckmann, Czudaj (2013). "Gold as an inflation hedge in a time-varying coefficient framework." *North American Journal of Economics and Finance* 24. [P031]
- Bredin, Conlon, Potì (2015). "Does gold glitter in the long-run?" *International Review of Financial Analysis* 41. [P007]
- Caldara, Iacoviello (2022). "Measuring geopolitical risk." *American Economic Review* 112. [P029]
- Campbell, Pflueger, Viceira (2020). "Macroeconomic drivers of bond and equity risks." *Journal of Political Economy* 128. [P026]
- Cheng, Xiong (2014). "Financialization of commodity markets." *Annual Review of Financial Economics* 6. [P023]
- Conlon, McGee (2020). "Safe haven or risky hazard? Bitcoin during the COVID-19 bear market." *Finance Research Letters* 35. [P015]
- Engle (2002). "Dynamic Conditional Correlation." *Journal of Business and Economic Statistics* 20. [P003]
- Forbes, Rigobon (2002). "No contagion, only interdependence." *Journal of Finance* 57. [P001]
- Gorton, Rouwenhorst (2006). "Facts and fantasies about commodity futures." *Financial Analysts Journal* 62. [P019]
- Iqbal (2017). "Does gold hedge stock market, inflation and exchange rate risks?" *International Review of Economics and Finance* 48. [P030]
- Künsch (1989). "The jackknife and the bootstrap for general stationary observations." *Annals of Statistics* 17.
- Longin, Solnik (2001). "Extreme correlation of international equity markets." *Journal of Finance* 56. [P002]
- López de Prado (2018). *Advances in Financial Machine Learning.* Wiley.
- Tang, Xiong (2012). "Index investment and the financialization of commodities." *Financial Analysts Journal* 68. [P022]
