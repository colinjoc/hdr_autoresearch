"""Phase 2.75 — sensitivity of the CURRENT result to window choices.

The Phase 2.75 review flagged that the CURRENT crisis window
(2025-11-01 → today) was chosen after seeing the data. This script
sweeps:

  (a) CURRENT start date ∈ {2025-09-01, 2025-10-01, 2025-11-01, 2025-12-01}
  (b) Rolling-correlation window length ∈ {30, 90, 250} days

and reports the SPY-GLD point estimate and moving-block bootstrap 95%
CI in each cell. If the "sustained elevated correlation" observation
is robust, it should survive ±2 months of start-date wiggle and 30/250
window alternatives.

Also produces a cross-crisis comparison table that is robust under the
corrected inference.
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA_RAW = HERE / "data" / "raw"


def build_corr(prices, other, window):
    r_spy = np.log(prices["SPY"]).diff()
    r_o = np.log(prices[other]).diff()
    return r_spy.rolling(window).corr(r_o)


def block_bootstrap(x, block_len=90, n_boot=2000, seed=42):
    x = np.asarray(x); x = x[~np.isnan(x)]
    if len(x) < 10:
        return float("nan"), float("nan"), float("nan"), len(x)
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
    prices = pd.read_csv(DATA_RAW / "prices.csv", index_col=0, parse_dates=True)
    end_date = str(prices.index.max().date())
    targets = ["GLD", "BTC", "WTI", "DBC"]

    # (a) CURRENT start date sensitivity, window fixed at 90d
    print("\n=== CURRENT start-date sensitivity (90d rolling, SPY-GLD) ===")
    print(f"{'start':<12}{'end':<12}{'mean':>9}{'block 95% CI':>26}{'n':>6}")
    rows_a = []
    for start in ["2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01"]:
        c = build_corr(prices, "GLD", 90)
        vals = c.loc[start:end_date].values
        m, lo, hi, n = block_bootstrap(vals, block_len=min(90, max(5, len(vals[~np.isnan(vals)]) // 3)))
        print(f"{start:<12}{end_date:<12}{m:+9.3f}   [{lo:+.3f}, {hi:+.3f}]{n:>6}")
        rows_a.append(dict(start=start, end=end_date, mean=m, lo=lo, hi=hi, n=n))
    pd.DataFrame(rows_a).to_csv(HERE / "sensitivity_current_start.csv", index=False)

    # (b) Rolling-window-length robustness, CURRENT fixed at 2025-11-01
    print("\n=== Window-length robustness (CURRENT=2025-11-01 → today) ===")
    print(f"{'window':>7}{'target':<8}{'mean':>9}{'block 95% CI':>26}{'n':>6}")
    rows_b = []
    for window in [30, 90, 250]:
        for tgt in targets:
            c = build_corr(prices, tgt, window)
            vals = c.loc["2025-11-01":end_date].values
            m, lo, hi, n = block_bootstrap(vals, block_len=min(window, max(5, max(1, len([v for v in vals if not np.isnan(v)])) // 3)))
            print(f"{window:>7}  {tgt:<6}{m:+9.3f}   [{lo:+.3f}, {hi:+.3f}]{n:>6}")
            rows_b.append(dict(window=window, target=tgt, mean=m, lo=lo, hi=hi, n=n))
    pd.DataFrame(rows_b).to_csv(HERE / "sensitivity_window.csv", index=False)

    # (c) Cross-crisis comparison under block bootstrap
    print("\n=== Crisis-window block-bootstrap table (SPY-GLD) ===")
    print(f"{'crisis':<10}{'window':<24}{'mean':>9}{'block 95% CI':>26}{'n':>6}")
    crises = {
        "GFC":      ("2007-09-01", "2009-03-31"),
        "COVID":    ("2020-02-01", "2020-04-30"),
        "INFL2022": ("2022-01-01", "2022-10-31"),
        "TARIFF25": ("2025-03-01", "2025-05-31"),
        "CURRENT":  ("2025-11-01", end_date),
    }
    rows_c = []
    for name, (s, e) in crises.items():
        c = build_corr(prices, "GLD", 90)
        vals = c.loc[s:e].values
        m, lo, hi, n = block_bootstrap(vals)
        print(f"{name:<10}{s} → {e}  {m:+9.3f}   [{lo:+.3f}, {hi:+.3f}]{n:>6}")
        rows_c.append(dict(crisis=name, start=s, end=e, mean=m, lo=lo, hi=hi, n=n))
    pd.DataFrame(rows_c).to_csv(HERE / "crisis_block_bootstrap.csv", index=False)

    # Append E-rows for the sensitivity checks
    results_tsv = HERE / "results.tsv"
    exp_id = 0
    with open(results_tsv, "a") as f:
        for r in rows_a:
            if np.isnan(r["mean"]):
                continue
            exp_id += 1
            f.write("\t".join([
                f"S{exp_id:02d}_current_start_{r['start']}_GLD",
                "2.75",
                f"Sensitivity: SPY-GLD mean with CURRENT start = {r['start']}",
                "block_bootstrap", "42",
                "correlation_mean",
                f"{r['mean']:.4f}", f"{r['lo']:.4f}", f"{r['hi']:.4f}",
                "KEEP",
                f"n={r['n']}; moving-block bootstrap",
            ]) + "\n")
        for r in rows_b:
            if np.isnan(r["mean"]):
                continue
            exp_id += 1
            f.write("\t".join([
                f"S{exp_id:02d}_window_{r['window']}d_SPY_{r['target']}",
                "2.75",
                f"Sensitivity: {r['window']}d rolling corr SPY-{r['target']} over CURRENT",
                "block_bootstrap", "42",
                "correlation_mean",
                f"{r['mean']:.4f}", f"{r['lo']:.4f}", f"{r['hi']:.4f}",
                "KEEP",
                f"n={r['n']}; moving-block bootstrap",
            ]) + "\n")
    print(f"\nAppended {exp_id} S-rows to results.tsv")


if __name__ == "__main__":
    main()
