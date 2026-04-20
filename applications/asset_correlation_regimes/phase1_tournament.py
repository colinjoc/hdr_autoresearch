"""Phase 1 tournament for asset_correlation_regimes (exploratory).

Tournament compares model families for predicting 90-day rolling correlation
from macroeconomic regime features.

Families:
  F1: OLS linear regression (linear-model sanity check — required)
  F2: sklearn GradientBoostingRegressor (tree-based; non-linear)
  F3: sklearn RandomForestRegressor (tree-based, bagging — exploratory bonus)

Targets: 90-day rolling corr(SPY, X) for X ∈ {GLD, BTC, WTI, DBC}.

Features:
  - fedfunds_level        (monthly, ffill to daily)
  - fedfunds_slope_3m     (3-month change)
  - cpi_yoy_pct           (year-over-year CPI)
  - dxy_level
  - dxy_6m_pct            (6-month dollar-index pct change)
  - dgs10_level           (10-year Treasury yield)
  - spy_vol_30d           (30-day realised SPY volatility — controls for
                           correlation's general elevation during volatile
                           periods)
  - month_of_year         (seasonal indicator)

Evaluation: 5-fold time-series cross-validation (no shuffling, training
only on past). Report held-out MAE and R² for each (family, target) pair.

Writes:
  - tournament_results.csv
  - appends T01-T12 rows to results.tsv
"""
from __future__ import annotations
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, r2_score

HERE = Path(__file__).parent
DATA_RAW = HERE / "data" / "raw"
RESULTS = HERE / "results.tsv"
TOURN = HERE / "tournament_results.csv"


def build_feature_panel():
    """Join prices + macro into a daily feature panel aligned to SPY calendar."""
    prices = pd.read_csv(DATA_RAW / "prices.csv", index_col=0, parse_dates=True)
    macro = pd.read_csv(DATA_RAW / "macro.csv", index_col=0, parse_dates=True)

    # Compute SPY 30-day realized volatility (annualized)
    spy_ret = np.log(prices["SPY"]).diff()
    spy_vol_30d = spy_ret.rolling(30).std() * math.sqrt(252)

    # Ffill WITHIN macro first (fills interspersed NaNs from the
    # daily+monthly series union), THEN reindex-ffill to SPY's calendar.
    macro_daily = macro.ffill().reindex(prices.index, method="ffill")

    # Feature columns
    df = pd.DataFrame(index=prices.index)
    df["fedfunds_level"] = macro_daily["FEDFUNDS"]
    df["fedfunds_slope_3m"] = macro_daily["FEDFUNDS"].diff(63)  # ~3 months
    df["cpi_yoy_pct"] = 100 * (macro_daily["CPIAUCSL"].pct_change(252))
    df["dxy_level"] = prices["DXY"]
    df["dxy_6m_pct"] = 100 * prices["DXY"].pct_change(126)
    df["dgs10_level"] = macro_daily["DGS10"]
    df["spy_vol_30d"] = spy_vol_30d
    df["month_sin"] = np.sin(2 * math.pi * df.index.month / 12)
    df["month_cos"] = np.cos(2 * math.pi * df.index.month / 12)

    # Targets
    for other in ["GLD", "BTC", "WTI", "DBC"]:
        if other not in prices.columns:
            continue
        r_spy = np.log(prices["SPY"]).diff()
        r_other = np.log(prices[other]).diff()
        df[f"corr_SPY_{other}"] = r_spy.rolling(90).corr(r_other)

    return df


def evaluate(model_ctor, X, y, name, target, splits=5):
    """5-fold time-series CV — MAE and R² on held-out folds."""
    tscv = TimeSeriesSplit(n_splits=splits)
    maes, r2s = [], []
    for tr_idx, te_idx in tscv.split(X):
        model = model_ctor()
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        pred = model.predict(X.iloc[te_idx])
        maes.append(mean_absolute_error(y.iloc[te_idx], pred))
        r2s.append(r2_score(y.iloc[te_idx], pred))
    return dict(family=name, target=target, mae=float(np.mean(maes)), mae_sd=float(np.std(maes)),
                r2=float(np.mean(r2s)), r2_sd=float(np.std(r2s)))


def main():
    df = build_feature_panel()

    feature_cols = ["fedfunds_level", "fedfunds_slope_3m", "cpi_yoy_pct",
                    "dxy_level", "dxy_6m_pct", "dgs10_level", "spy_vol_30d",
                    "month_sin", "month_cos"]
    target_cols = [c for c in df.columns if c.startswith("corr_SPY_")]
    print(f"Features: {feature_cols}")
    print(f"Targets:  {target_cols}\n")

    families = {
        "F1_OLS":  lambda: LinearRegression(),
        "F2_GBR":  lambda: GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=42),
        "F3_RF":   lambda: RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1),
    }

    rows = []
    for target in target_cols:
        sub = df[feature_cols + [target]].dropna()
        if len(sub) < 400:
            print(f"[SKIP] {target}: insufficient data ({len(sub)} obs)")
            continue
        X, y = sub[feature_cols], sub[target]
        print(f"\n=== target: {target}  (n={len(sub)} observations) ===")
        print(f"  Target stats: mean={y.mean():+.3f}  std={y.std():.3f}  min={y.min():+.3f}  max={y.max():+.3f}")
        for fname, ctor in families.items():
            res = evaluate(ctor, X, y, fname, target)
            print(f"  {fname:<7}  MAE={res['mae']:.3f}±{res['mae_sd']:.3f}  R²={res['r2']:+.3f}±{res['r2_sd']:.3f}")
            rows.append(res)

    # Save tournament_results.csv
    tourn_df = pd.DataFrame(rows)
    tourn_df.to_csv(TOURN, index=False)
    print(f"\ntournament_results.csv written ({len(rows)} rows)")

    # Append T-rows to results.tsv
    tsv_rows = []
    for i, r in enumerate(rows, 1):
        tsv_rows.append("\t".join([
            f"T{i:02d}_{r['family']}_{r['target']}", "1",
            f"Phase 1 tournament: predict {r['target']} from macro features",
            r["family"], "42",
            "r2_held_out",
            f"{r['r2']:.4f}",
            f"{r['r2'] - 1.96*r['r2_sd']:.4f}",
            f"{r['r2'] + 1.96*r['r2_sd']:.4f}",
            "KEEP",
            f"MAE={r['mae']:.4f}±{r['mae_sd']:.4f}, R²_sd={r['r2_sd']:.4f}",
        ]))
    with open(RESULTS, "a") as f:
        for line in tsv_rows:
            f.write(line + "\n")
    print(f"Appended {len(tsv_rows)} rows to results.tsv")

    # Headline: winning family per target
    print("\n=== Phase 1 winners (by MAE, lower = better) ===")
    winners = {}
    for target in target_cols:
        sub = [r for r in rows if r["target"] == target]
        if sub:
            w = min(sub, key=lambda r: r["mae"])
            winners[target] = w
            print(f"  {target}: winner={w['family']}  MAE={w['mae']:.3f}  R²={w['r2']:+.3f}")

    # Family-level ranking across targets
    print("\n=== Average rank per family (across targets) ===")
    for target in target_cols:
        sub = sorted([r for r in rows if r["target"] == target], key=lambda r: r["mae"])
        for rank, r in enumerate(sub, 1):
            r.setdefault("ranks", []).append(rank)
    for fname in families:
        avg_rank = np.mean([r["ranks"] for r in rows if r["family"] == fname], axis=0)
        print(f"  {fname}: {np.mean(avg_rank):.2f}")


if __name__ == "__main__":
    main()
