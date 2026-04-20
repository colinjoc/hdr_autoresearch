"""Generate plots for the website summary."""
from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = Path(__file__).parent
DATA_RAW = HERE / "data" / "raw"
PLOTS = HERE / "plots"
PLOTS.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "figure.dpi": 110,
    "savefig.dpi": 140,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

CRISES = {
    "GFC":      ("2007-09-01", "2009-03-31"),
    "COVID":    ("2020-02-01", "2020-04-30"),
    "INFL2022": ("2022-01-01", "2022-10-31"),
    "TARIFF25": ("2025-03-01", "2025-05-31"),
    "CURRENT":  ("2025-11-01", "2026-04-20"),
}


def fig_timeseries():
    """SPY-GLD 90d rolling correlation, 2004-2026, crisis windows shaded."""
    prices = pd.read_csv(DATA_RAW / "prices.csv", index_col=0, parse_dates=True)
    r_spy = np.log(prices["SPY"]).diff()
    r_gld = np.log(prices["GLD"]).diff()
    corr = r_spy.rolling(90).corr(r_gld)
    full_median = corr.median()

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(corr.index, corr.values, lw=0.8, color="#1f2a44")
    ax.axhline(full_median, ls="--", lw=1, color="#aa4444",
               label=f"22-year median = {full_median:+.3f}")
    ax.axhline(0, lw=0.5, color="#999")

    colors = ["#f0c674", "#b5bd68", "#8abeb7", "#cc6666", "#de935f"]
    for (name, (s, e)), c in zip(CRISES.items(), colors):
        ax.axvspan(pd.Timestamp(s), pd.Timestamp(e), color=c, alpha=0.35, label=name)

    ax.set_ylabel("90-day rolling Pearson correlation")
    ax.set_xlabel("")
    ax.set_ylim(-0.7, 0.7)
    ax.set_title("SPY ↔ GLD: 22 years of rolling correlation")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", ncol=3, fontsize=8, frameon=False)
    ax.grid(True, axis="y", lw=0.4, color="#ccc")

    fig.tight_layout()
    fig.savefig(PLOTS / "fig1_spy_gld_timeseries.png")
    plt.close(fig)


def fig_crisis_compare():
    """Crisis-window means with block-bootstrap 95% CIs for SPY-GLD."""
    cb = pd.read_csv(HERE / "crisis_block_bootstrap.csv")
    cb = cb.set_index("crisis")
    order = ["GFC", "COVID", "INFL2022", "TARIFF25", "CURRENT"]
    cb = cb.loc[order]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    y = np.arange(len(cb))
    means = cb["mean"].values
    lo = means - cb["lo"].values
    hi = cb["hi"].values - means

    ax.errorbar(means, y, xerr=[lo, hi], fmt="o", color="#1f2a44",
                ecolor="#1f2a44", capsize=4, markersize=7, lw=1.6)

    full_median = 0.049
    ax.axvline(full_median, ls="--", lw=1, color="#aa4444",
               label=f"22-year median = {full_median:+.3f}")
    ax.axvline(0, lw=0.5, color="#999")

    # Highlight CURRENT
    cur_idx = order.index("CURRENT")
    ax.plot(means[cur_idx], cur_idx, "o", color="#cc6666", markersize=11, zorder=5)
    tar_idx = order.index("TARIFF25")
    ax.plot(means[tar_idx], tar_idx, "o", color="#de935f", markersize=11, zorder=5)

    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    ax.set_xlabel("Mean 90-day rolling SPY-GLD correlation (block-bootstrap 95% CI)")
    ax.set_title("Gold-equity correlation across five crisis windows")
    ax.set_xlim(-0.35, 0.35)
    ax.legend(loc="lower right", fontsize=9, frameon=False)
    ax.grid(True, axis="x", lw=0.4, color="#ccc")

    fig.tight_layout()
    fig.savefig(PLOTS / "fig2_crisis_compare.png")
    plt.close(fig)


def fig_cross_asset():
    """CURRENT vs long-run means for all four targets."""
    data = {
        "GLD":  ("Gold",       +0.170, +0.156, +0.185, +0.049),
        "BTC":  ("Bitcoin",    +0.511, +0.460, +0.549, +0.159),
        "WTI":  ("WTI crude",  -0.010, -0.114, +0.156, +0.204),
        "DBC":  ("Commodities (DBC)", +0.149, +0.054, +0.332, +0.339),
    }
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = []
    current = []
    longrun = []
    lo_list = []
    hi_list = []
    for k, (lab, m, lo, hi, lr) in data.items():
        labels.append(lab)
        current.append(m)
        lo_list.append(m - lo)
        hi_list.append(hi - m)
        longrun.append(lr)

    y = np.arange(len(labels))
    ax.errorbar(current, y - 0.15, xerr=[lo_list, hi_list], fmt="o",
                color="#cc6666", ecolor="#cc6666", capsize=4, markersize=8,
                label="CURRENT (Nov-2025 → Apr-2026)")
    ax.plot(longrun, y + 0.15, "s", color="#1f2a44", markersize=8,
            label="22-year median")

    ax.axvline(0, lw=0.5, color="#999")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(-0.25, 0.65)
    ax.set_xlabel("SPY rolling 90d correlation")
    ax.set_title("Current cross-asset correlation with equities vs long-run normal")
    ax.legend(loc="lower right", fontsize=9, frameon=False)
    ax.grid(True, axis="x", lw=0.4, color="#ccc")

    fig.tight_layout()
    fig.savefig(PLOTS / "fig3_cross_asset.png")
    plt.close(fig)


def main():
    fig_timeseries()
    fig_crisis_compare()
    fig_cross_asset()
    print(f"Wrote plots to {PLOTS}")


if __name__ == "__main__":
    main()
