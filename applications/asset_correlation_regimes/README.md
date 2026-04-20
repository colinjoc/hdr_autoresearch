**Target type**: exploratory

# Asset correlation regimes: when do gold, bitcoin, and commodities decouple from equities?

## One-paragraph framing

Casual observation through 2024–2026 is that gold, bitcoin, and broad commodities have been positively correlated with equity indices, contradicting the standard "safe-haven" intuition that these assets should be anti-correlated under heightened risk. This exploratory project builds a reproducible rolling-correlation panel for SPY, GLD, BTC-USD, WTI crude, and the Bloomberg Commodity Index over 20+ years, identifies the historical correlation regimes, and tests whether the 2024–2026 regime is unusual when compared against prior regimes conditioned on macroeconomic context (Fed cycle phase, inflation regime, dollar direction, geopolitical-risk indicators). The aim is personal understanding, not publication — but the project still goes through the full HDR methodology-gate sequence (Phase 0.5 baseline, Phase 1 tournament, Phase 2 loop, Phase 2.75 adversarial results review, Phase 3 paper, Phase 3.5 blind signoff, website publish) as required for exploratory projects by program.md.

## Core questions

1. What has actually been the rolling 90-day correlation between SPY and each of {GLD, BTC-USD, WTI, Bloomberg Commodity Index} over the last 20 years, and specifically over the last 24 months?
2. Is the current regime (2024–2026) statistically unusual against 2004–2024?
3. Conditional on macroeconomic regime (Fed cycle, inflation level, dollar direction), is the current correlation behaviour surprising?
4. If it's not surprising conditional on regime, what are the signatures that the "risk-off" intuition requires — and do they hold now?

## Scope

- Real daily price data from public sources (Yahoo Finance, FRED) only.
- 2004-01-01 to today (gives ~22 years including 2008 GFC, 2020 COVID, 2022 inflation shock).
- Assets: SPY, QQQ, GLD, BTC-USD, WTI (CL=F), Bloomberg Commodity Index (BCOM via a proxy ETF if BCOM not directly tradeable), DXY (dollar index).
- Macro regime variables: effective fed funds rate, CPI YoY, dollar index trend, Geopolitical Risk Index (Caldara-Iacoviello).
- Primary statistic: 90-day rolling Pearson correlation. Robustness: Spearman, Kendall, DCC-GARCH.

## What this project will NOT do

- Make trading recommendations.
- Propose a new correlation model or time-series theorem.
- Backtest a portfolio strategy.
- Attempt publication anywhere.

Promotion to publication-target is explicitly *not* planned.
