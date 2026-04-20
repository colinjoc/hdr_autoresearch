# Data sources — Phase 0.5 smoke test

Run date: 2026-04-20T13:58:43.938876+00:00

## Yahoo Finance (yfinance)

Tickers fetched: SPY, QQQ, GLD, BTC-USD, CL=F (WTI), DBC, DX-Y.NYB (DXY).
Start date: 2004-01-01. Adjusted close (auto_adjust=True).

Coverage per asset:

- `SPY`: 6942 obs, 2004-01-02 → 2026-04-20
- `QQQ`: 6942 obs, 2004-01-02 → 2026-04-20
- `GLD`: 6715 obs, 2004-11-18 → 2026-04-20
- `BTC`: 4234 obs, 2014-09-17 → 2026-04-20
- `WTI`: 6941 obs, 2004-01-05 → 2026-04-20
- `DBC`: 6405 obs, 2006-02-06 → 2026-04-20
- `DXY`: 6942 obs, 2004-01-02 → 2026-04-20


## FRED (pandas_datareader)

Series: FEDFUNDS, CPIAUCSL, DTWEXBGS, DGS10.

- `FEDFUNDS`: 267 obs, 2004-01-01 → 2026-03-01
- `CPIAUCSL`: 266 obs, 2004-01-01 → 2026-03-01
- `DTWEXBGS`: 5082 obs, 2006-01-02 → 2026-04-10
- `DGS10`: 5576 obs, 2004-01-02 → 2026-04-16


## Geopolitical Risk Index (Caldara–Iacoviello)

Not reachable at smoke test; acceptable for E00. Will retry at Phase 1 or drop from macro conditioning if still unavailable.

## Data coverage notes

- BTC-USD begins 2014-09-17 on Yahoo; pre-2014 coverage not available from this source.
- DBC (broad commodity ETF) inception 2006-02-03.
- For 2004-01-01 → 2006-02 period, WTI is the only continuous commodity series.

Phase 0.5 verdict on data: **CLEAR** — all critical series (SPY, GLD, BTC, WTI) are reachable with multi-year coverage.
