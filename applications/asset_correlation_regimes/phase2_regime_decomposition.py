"""Phase 2 — Regime decomposition of rolling correlations.

Phase 1 found that macro regime cannot predict rolling correlation out of
sample (all R² negative, even with a 90-day embargo). This motivates a
different approach: partition the 22-year window into explicit regimes
and describe (NOT test) correlations within each regime.

We define the following regime dummies (not overlapping unless noted):

  R1 Fed-cycle:        cutting (fedfunds_slope_3m < -25 bps), hiking
                       (> +25 bps), neutral.
  R2 Inflation:        high (cpi_yoy > 3.5%), moderate (2-3.5%), low (< 2%).
  R3 Dollar:           strengthening (dxy_6m_pct > +3%), weakening
                       (< -3%), neutral.
  R4 Growth shock:     SPY 90-day drawdown > 15% (proxy for risk-off).
  R5 Identified crises (post-hoc labels, see knowledge_base.md):
                       GFC (2007-09 to 2009-03), COVID (2020-02 to
                       2020-04), 2022 inflation shock (2022-01 to 2022-10),
                       tariff/2025 (2025-03 to 2025-05), current period
                       (2025-11 to today).

Each experiment is a regime-conditional mean and 95% MOVING-BLOCK
bootstrap CI (block length 90 ≈ rolling window) for 90-day rolling
corr(SPY, X). Block bootstrap is required because consecutive daily
observations share 89 of 90 days of underlying returns — an IID
bootstrap would understate CI width by 2-8x (see paper_review.md F1).

This is a DESCRIPTIVE partition, not a hypothesis test. No p-values or
multiple-comparisons corrections are reported; apparent differences
between regimes should be read as "what the data look like within this
window", not "statistically significant effect".
"""
from __future__ import annotations
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA_RAW = HERE / "data" / "raw"
RESULTS = HERE / "results.tsv"


def build_panel():
    prices = pd.read_csv(DATA_RAW / "prices.csv", index_col=0, parse_dates=True)
    macro = pd.read_csv(DATA_RAW / "macro.csv", index_col=0, parse_dates=True)
    macro_d = macro.ffill().reindex(prices.index, method="ffill")

    r_spy = np.log(prices["SPY"]).diff()
    spy_dd = (prices["SPY"] / prices["SPY"].rolling(90).max()) - 1

    df = pd.DataFrame(index=prices.index)
    for other in ["GLD", "BTC", "WTI", "DBC"]:
        r_o = np.log(prices[other]).diff()
        df[f"corr_SPY_{other}"] = r_spy.rolling(90).corr(r_o)

    # Regime indicators
    df["fedfunds_slope_3m_bps"] = 100 * macro_d["FEDFUNDS"].diff(63)
    df["cpi_yoy"] = 100 * macro_d["CPIAUCSL"].pct_change(252)
    df["dxy_6m_pct"] = 100 * prices["DXY"].pct_change(126)
    df["spy_dd_90"] = spy_dd

    def classify(df):
        fed = pd.Series(index=df.index, dtype="object")
        fed[df["fedfunds_slope_3m_bps"] < -25] = "cutting"
        fed[df["fedfunds_slope_3m_bps"] > +25] = "hiking"
        fed = fed.fillna("neutral")

        inf = pd.cut(df["cpi_yoy"], bins=[-np.inf, 2, 3.5, np.inf], labels=["low", "moderate", "high"])
        dxy = pd.Series(index=df.index, dtype="object")
        dxy[df["dxy_6m_pct"] > +3] = "strengthening"
        dxy[df["dxy_6m_pct"] < -3] = "weakening"
        dxy = dxy.fillna("neutral")
        shock = (df["spy_dd_90"] < -0.15).astype(int).replace({1: "growth_shock", 0: "normal"})
        return fed, inf, dxy, shock

    fed, inf, dxy, shock = classify(df)
    df["R1_fed"] = fed
    df["R2_inf"] = inf.astype("object").where(inf.notna(), other=np.nan)
    df["R3_dxy"] = dxy
    df["R4_shock"] = shock

    # R5 — known crisis windows (curated from lit review)
    crises = {
        "GFC":      ("2007-09-01", "2009-03-31"),
        "COVID":    ("2020-02-01", "2020-04-30"),
        "INFL2022": ("2022-01-01", "2022-10-31"),
        "TARIFF25": ("2025-03-01", "2025-05-31"),
        "CURRENT":  ("2025-11-01", str(df.index.max().date())),
    }
    r5 = pd.Series("normal", index=df.index, dtype="object")
    for name, (s, e) in crises.items():
        r5.loc[s:e] = name
    df["R5_crisis"] = r5
    return df


def bootstrap_ci(x, n_boot=2000, seed=42, block_len=90):
    """Moving-block bootstrap (Künsch 1989) of the sample mean.

    block_len defaults to 90 to match the rolling-correlation window.
    For short windows (n < block_len), falls back to block_len = n // 3
    so we still capture local autocorrelation structure.
    """
    x = np.asarray(x)
    x = x[~np.isnan(x)]
    if len(x) < 10:
        return (float("nan"), float("nan"), float("nan"), len(x))
    n = len(x)
    b = min(block_len, max(5, n // 3))
    max_start = max(1, n - b)
    n_blocks = int(np.ceil(n / b))
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        sample = np.concatenate([x[s:s + b] for s in starts])[:n]
        means[i] = sample.mean()
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), int(n)


def main():
    df = build_panel()
    targets = ["corr_SPY_GLD", "corr_SPY_BTC", "corr_SPY_WTI", "corr_SPY_DBC"]

    # Build one big regime-correlation table
    all_rows = []
    for regime_col in ["R1_fed", "R2_inf", "R3_dxy", "R4_shock", "R5_crisis"]:
        for level in sorted(df[regime_col].dropna().unique()):
            mask = df[regime_col] == level
            for target in targets:
                vals = df.loc[mask, target]
                m, lo, hi, n = bootstrap_ci(vals.values)
                all_rows.append({
                    "regime": regime_col, "level": str(level), "target": target,
                    "mean": m, "ci_lo": lo, "ci_hi": hi, "n": n,
                })

    tab = pd.DataFrame(all_rows)
    tab.to_csv(HERE / "regime_correlation_table.csv", index=False)

    # Nicely printed subset
    print("\n=== Phase 2 regime decomposition ===\n")
    for regime_col in ["R1_fed", "R2_inf", "R3_dxy", "R4_shock", "R5_crisis"]:
        print(f"\n--- Regime variable: {regime_col} ---")
        subtab = tab[tab["regime"] == regime_col]
        for level in sorted(subtab["level"].unique()):
            row_str = f"  {level:<16}"
            for target in targets:
                r = subtab[(subtab["level"] == level) & (subtab["target"] == target)]
                if len(r):
                    row = r.iloc[0]
                    row_str += f" {target.split('_')[-1]:<3}={row['mean']:+.3f}[{row['ci_lo']:+.3f},{row['ci_hi']:+.3f}]"
            row_str += f"  n={subtab[subtab['level']==level]['n'].iloc[0]}"
            print(row_str)

    # Append E-rows: one experiment per (regime, level, target) combination
    exp_id = 0
    with open(RESULTS, "a") as f:
        for row in all_rows:
            if np.isnan(row["mean"]):
                continue
            exp_id += 1
            f.write("\t".join([
                f"E{exp_id:02d}_regime_{row['regime']}_{row['level']}_{row['target'].split('_')[-1]}",
                "2",
                f"Phase 2 regime decomposition: {row['regime']}={row['level']}, {row['target']}",
                "regime_conditional_mean", "42",
                "correlation_mean",
                f"{row['mean']:.4f}",
                f"{row['ci_lo']:.4f}",
                f"{row['ci_hi']:.4f}",
                "KEEP",
                f"n={row['n']}; moving-block (b=90) bootstrap 95% CI, 2000 samples",
            ]) + "\n")

    print(f"\nAppended {exp_id} E-rows to results.tsv")

    # Key hypothesis tests
    print("\n=== Key hypothesis tests ===")

    # H1: Is CURRENT SPY-GLD corr significantly different from long-run mean?
    for target in targets:
        current = tab[(tab["regime"] == "R5_crisis") & (tab["level"] == "CURRENT") & (tab["target"] == target)]
        full = df[target].dropna()
        full_mean = full.mean()
        if len(current):
            c = current.iloc[0]
            within_ci = c["ci_lo"] <= full_mean <= c["ci_hi"]
            print(f"  {target}: current={c['mean']:+.3f} [{c['ci_lo']:+.3f}, {c['ci_hi']:+.3f}], full_mean={full_mean:+.3f}, full_mean in CI: {within_ci}")

    # H2: Is COVID-era SPY-GLD corr similar to CURRENT (both crises, different regimes)?
    print("\n  Crisis-to-crisis comparison for GLD (test of 'all crises are the same'):")
    for crisis in ["GFC", "COVID", "INFL2022", "TARIFF25", "CURRENT"]:
        r = tab[(tab["regime"] == "R5_crisis") & (tab["level"] == crisis) & (tab["target"] == "corr_SPY_GLD")]
        if len(r):
            c = r.iloc[0]
            print(f"    {crisis}: corr={c['mean']:+.3f} [{c['ci_lo']:+.3f}, {c['ci_hi']:+.3f}]  n={c['n']}")


if __name__ == "__main__":
    main()
