**Target type**: exploratory

# Asset correlation regimes: when do gold, bitcoin, and commodities decouple from equities?

## One-paragraph framing

Casual observation through 2024–2026 is that gold, bitcoin, and broad commodities have been positively correlated with equity indices, contradicting the standard "safe-haven" intuition that these assets should be anti-correlated under heightened risk. This exploratory project builds a reproducible rolling-correlation panel for SPY, GLD, BTC-USD, WTI crude, and the Bloomberg Commodity Index over 20+ years, identifies the historical correlation regimes, and *describes* how the 2024–2026 regime compares to prior macroeconomic regimes (Fed cycle phase, inflation regime, dollar direction). The paper is descriptive, not inferential: it partitions the record into regimes and reports moving-block bootstrap CIs on the regime means, without testing any null hypothesis or claiming statistical significance across a family of 68 regime-conditional cells. The aim is personal understanding, not publication — but the project still goes through the full HDR methodology-gate sequence (Phase 0.5 baseline, Phase 1 tournament, Phase 2 loop, Phase 2.75 adversarial results review, Phase 3 paper, Phase 3.5 blind signoff, website publish) as required for exploratory projects by program.md.

## Core questions

1. What has actually been the rolling 90-day correlation between SPY and each of {GLD, BTC-USD, WTI, Bloomberg Commodity Index} over the last 20 years, and specifically over the last 24 months?
2. Descriptively, how does the current window (2025–H1 2026) sit relative to prior identified crisis windows and relative to long-run medians?
3. Conditional on macroeconomic regime (Fed cycle, inflation level, dollar direction), where does the current correlation behaviour fall within the historical distribution?
4. If it sits in a region the historical record has visited before, which signatures of the "risk-off" intuition hold now, and which don't?

Note: question 2 is deliberately *descriptive*, not an inferential test. An honest version of "is the current regime statistically unusual" is well beyond what a single 5-month window permits.

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
