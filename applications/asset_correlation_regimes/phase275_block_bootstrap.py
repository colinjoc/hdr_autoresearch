"""Phase 2.75 — block bootstrap sanity check.

Phase 2 used an IID bootstrap on rolling-90d correlation series. But each
daily observation of a 90d rolling correlation shares 89 of its 90 days
with its neighbour, so consecutive observations are massively
autocorrelated. The IID bootstrap therefore treats ~90 redundant
observations as if they were independent and returns CIs that are far too
tight.

The correct fix is a moving-block bootstrap (Künsch 1989) with block
length on the order of the window size (90 days), or an effective-sample-
size adjustment using the lag-1 autocorrelation.

This script recomputes the R5 crisis-window CIs with a block bootstrap
(block length = 90 days) so we can quantify the widening and decide
whether the "CURRENT is highest" claim survives honest inference.

Outputs:
  - block_bootstrap_R5.csv         (comparison with IID bootstrap)
  - prints lag-1 autocorrelation and implied N_eff for each crisis
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA_RAW = HERE / "data" / "raw"


def build_panel():
    prices = pd.read_csv(DATA_RAW / "prices.csv", index_col=0, parse_dates=True)
    r_spy = np.log(prices["SPY"]).diff()
    df = pd.DataFrame(index=prices.index)
    for other in ["GLD", "BTC", "WTI", "DBC"]:
        r_o = np.log(prices[other]).diff()
        df[f"corr_SPY_{other}"] = r_spy.rolling(90).corr(r_o)
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
    return df, crises


def iid_bootstrap(x, n_boot=2000, seed=42):
    x = np.asarray(x); x = x[~np.isnan(x)]
    if len(x) < 10:
        return (float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, len(x), size=len(x))
        means[i] = x[idx].mean()
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def block_bootstrap(x, block_len=90, n_boot=2000, seed=42):
    """Moving-block bootstrap (Künsch 1989). Resamples overlapping blocks
    of length `block_len` with replacement from the original series."""
    x = np.asarray(x); x = x[~np.isnan(x)]
    if len(x) < block_len:
        # Degenerate: window too small for block length; fall back to
        # circular single block (entire window)
        block_len = max(5, len(x) // 3)
    n = len(x)
    if n < 10:
        return (float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_len))
    max_start = n - block_len
    if max_start <= 0:
        # Only one possible starting point — fall back to wild approach:
        # shuffle with replacement on blocks of size block_len//2
        block_len = max(5, n // 4)
        max_start = n - block_len
    means = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        sample = np.concatenate([x[s:s + block_len] for s in starts])[:n]
        means[i] = sample.mean()
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def lag1_autocorr(x):
    x = np.asarray(x); x = x[~np.isnan(x)]
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])


def main():
    df, crises = build_panel()
    targets = ["corr_SPY_GLD", "corr_SPY_BTC", "corr_SPY_WTI", "corr_SPY_DBC"]

    rows = []
    for crisis in crises:
        mask = df["R5_crisis"] == crisis
        for target in targets:
            vals = df.loc[mask, target].values
            n_raw = int(np.sum(~np.isnan(vals)))
            if n_raw < 10:
                continue
            rho1 = lag1_autocorr(vals)
            # Effective sample size under AR(1) approximation:
            # N_eff = N * (1 - rho) / (1 + rho)
            if np.isfinite(rho1) and rho1 < 1:
                n_eff = max(1.0, n_raw * (1 - rho1) / (1 + rho1))
            else:
                n_eff = float("nan")
            m, iid_lo, iid_hi = iid_bootstrap(vals)
            _, bb_lo, bb_hi = block_bootstrap(vals, block_len=min(90, max(5, n_raw // 3)))
            rows.append({
                "crisis": crisis, "target": target, "mean": m,
                "n_raw": n_raw, "lag1_autocorr": rho1, "n_eff_ar1": n_eff,
                "iid_ci_lo": iid_lo, "iid_ci_hi": iid_hi,
                "iid_width": iid_hi - iid_lo,
                "block_ci_lo": bb_lo, "block_ci_hi": bb_hi,
                "block_width": bb_hi - bb_lo,
                "width_ratio_block_over_iid": (bb_hi - bb_lo) / (iid_hi - iid_lo)
                                               if (iid_hi - iid_lo) > 0 else float("nan"),
            })

    out = pd.DataFrame(rows)
    out.to_csv(HERE / "block_bootstrap_R5.csv", index=False)

    # Print readable summary focused on the headline claim (CURRENT vs others, GLD)
    print("\n=== Block-bootstrap vs IID-bootstrap, 95% CI width comparison ===\n")
    print(f"{'crisis':<10}{'target':<14}{'n':>5}{'rho1':>8}{'Neff':>7}"
          f"{'mean':>9}{'IID CI':>22}{'Block CI':>22}{'ratio':>7}")
    for _, r in out.iterrows():
        print(f"{r['crisis']:<10}{r['target']:<14}{int(r['n_raw']):>5}"
              f"{r['lag1_autocorr']:>+8.3f}{r['n_eff_ar1']:>7.1f}"
              f"{r['mean']:>+9.3f}"
              f"   [{r['iid_ci_lo']:+.3f},{r['iid_ci_hi']:+.3f}]"
              f"   [{r['block_ci_lo']:+.3f},{r['block_ci_hi']:+.3f}]"
              f"{r['width_ratio_block_over_iid']:>7.2f}")

    # Headline check: does the CURRENT > all-other-crises claim survive?
    print("\n=== Headline check: SPY-GLD — CURRENT vs each prior crisis ===")
    gld = out[out["target"] == "corr_SPY_GLD"].set_index("crisis")
    if "CURRENT" in gld.index:
        cur = gld.loc["CURRENT"]
        cur_lo_block = cur["block_ci_lo"]
        print(f"CURRENT:  mean={cur['mean']:+.3f} IID=[{cur['iid_ci_lo']:+.3f},{cur['iid_ci_hi']:+.3f}]"
              f"  Block=[{cur['block_ci_lo']:+.3f},{cur['block_ci_hi']:+.3f}]  n={int(cur['n_raw'])}")
        for other in ["GFC", "COVID", "INFL2022", "TARIFF25"]:
            if other in gld.index:
                o = gld.loc[other]
                iid_sep = cur["iid_ci_lo"] > o["iid_ci_hi"]
                block_sep = cur["block_ci_lo"] > o["block_ci_hi"]
                overlap_block = "OVERLAP" if not block_sep else "separate"
                print(f"  vs {other:<8}  mean={o['mean']:+.3f} "
                      f"Block=[{o['block_ci_lo']:+.3f},{o['block_ci_hi']:+.3f}]  "
                      f"IID-separation={iid_sep}  Block-separation={block_sep} ({overlap_block})")

    print("\nblock_bootstrap_R5.csv written")


if __name__ == "__main__":
    main()
