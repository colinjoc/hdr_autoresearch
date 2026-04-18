"""
Generate all plots for the Irish international construction cost comparison paper.
Reads from data/raw/ and results.tsv, outputs to plots/.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
from analyze import (
    load_data, build_panel, compute_cumulative_growth,
    compute_subperiod_growth, ABS_EUR_SQM_2025, COUNTRY_NAMES,
    cluster_countries, compute_eu_avg_and_irish_excess,
    compute_ireland_rank_over_time, decompose_irish_excess,
)

PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Style
plt.style.use("seaborn-v0_8-whitegrid")
COLORS = {
    "IE": "#1f77b4",  # blue for Ireland
    "DE": "#ff7f0e",  # orange
    "NL": "#2ca02c",  # green
    "UK": "#d62728",  # red
    "DK": "#9467bd",  # purple
    "SE": "#8c564b",  # brown
    "AT": "#e377c2",  # pink
    "FR": "#7f7f7f",  # grey
    "FI": "#bcbd22",  # olive
    "BE": "#17becf",  # cyan
    "ES": "#aec7e8",  # light blue
    "EU_AVG": "#000000",  # black
}


def plot_1_trajectory_comparison():
    """Time series of all countries' rebased indices with Ireland highlighted."""
    df = load_data()
    panel = build_panel(df)

    fig, ax = plt.subplots(figsize=(12, 7))

    for geo in panel.columns:
        if geo == "IE":
            continue
        ax.plot(range(len(panel)), panel[geo], color=COLORS.get(geo, "#cccccc"),
                alpha=0.5, linewidth=1, label=COUNTRY_NAMES.get(geo, geo))

    # EU average
    non_ie = [c for c in panel.columns if c != "IE"]
    eu_avg = panel[non_ie].mean(axis=1)
    ax.plot(range(len(panel)), eu_avg, color="black", linewidth=2,
            linestyle="--", label="EU-9 Average")

    # Ireland highlighted
    ax.plot(range(len(panel)), panel["IE"], color=COLORS["IE"],
            linewidth=3, label="Ireland", zorder=5)

    # Shade subperiods
    quarters = list(panel.index)
    covid_start = quarters.index("2020-Q1") if "2020-Q1" in quarters else None
    covid_end = quarters.index("2021-Q4") if "2021-Q4" in quarters else None
    ukraine_start = quarters.index("2022-Q1") if "2022-Q1" in quarters else None
    ukraine_end = quarters.index("2023-Q4") if "2023-Q4" in quarters else None

    if covid_start and covid_end:
        ax.axvspan(covid_start, covid_end, alpha=0.1, color="red", label="COVID")
    if ukraine_start and ukraine_end:
        ax.axvspan(ukraine_start, ukraine_end, alpha=0.1, color="orange", label="Ukraine/Energy")

    # X-axis labels
    tick_positions = [i for i, q in enumerate(quarters) if q.endswith("-Q1")]
    tick_labels = [q[:4] for q in quarters if q.endswith("-Q1")]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)

    ax.set_ylabel("Construction Cost Index (2015-Q1 = 100)")
    ax.set_xlabel("")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.set_ylim(95, 185)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "headline_finding.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved headline_finding.png")


def plot_2_cumulative_growth_ranking():
    """Horizontal bar chart of cumulative growth ranked."""
    df = load_data()
    panel = build_panel(df)
    growth = compute_cumulative_growth(panel)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COLORS["IE"] if geo == "IE" else "#aaaaaa" for geo in growth.index]
    bars = ax.barh(range(len(growth)), growth.values, color=colors)

    ax.set_yticks(range(len(growth)))
    ax.set_yticklabels([f"{COUNTRY_NAMES.get(g, g)}" for g in growth.index])
    ax.set_xlabel("Cumulative Growth 2015-Q1 to 2025-Q4 (%)")
    ax.invert_yaxis()

    # Add value labels
    for i, (geo, val) in enumerate(growth.items()):
        ax.text(val + 0.5, i, f"+{val:.1f}%", va="center", fontsize=9)

    # Mark EU average
    eu_avg = growth.mean()
    ax.axvline(eu_avg, color="black", linestyle="--", linewidth=1, label=f"EU-10 avg: +{eu_avg:.1f}%")
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "cumulative_growth_ranking.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved cumulative_growth_ranking.png")


def plot_3_subperiod_growth():
    """Grouped bar chart of subperiod growth rates."""
    df = load_data()
    panel = build_panel(df)
    subperiod = compute_subperiod_growth(panel)

    countries_order = ["DE", "NL", "AT", "BE", "SE", "IE", "ES", "DK", "FR", "FI"]
    periods = ["Pre-COVID", "COVID", "Ukraine/Energy", "Recovery"]
    period_colors = ["#4e79a7", "#e15759", "#f28e2b", "#76b7b2"]

    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.arange(len(countries_order))
    width = 0.2

    for i, period in enumerate(periods):
        if period in subperiod.columns:
            vals = [subperiod.loc[c, period] if c in subperiod.index else 0 for c in countries_order]
            offset = (i - 1.5) * width
            bars = ax.bar(x + offset, vals, width, label=period, color=period_colors[i])

    ax.set_xticks(x)
    ax.set_xticklabels([COUNTRY_NAMES.get(c, c) for c in countries_order], rotation=45, ha="right")
    ax.set_ylabel("Growth (%)")
    ax.legend()
    ax.axhline(0, color="black", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "subperiod_growth.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved subperiod_growth.png")


def plot_4_absolute_eur_sqm():
    """Bar chart of absolute EUR/sqm levels."""
    abs_sorted = sorted(ABS_EUR_SQM_2025.items(), key=lambda x: -x[1])

    fig, ax = plt.subplots(figsize=(10, 6))

    geos = [g for g, _ in abs_sorted]
    vals = [v for _, v in abs_sorted]
    colors = [COLORS["IE"] if g == "IE" else "#aaaaaa" for g in geos]

    bars = ax.barh(range(len(geos)), vals, color=colors)
    ax.set_yticks(range(len(geos)))
    ax.set_yticklabels([COUNTRY_NAMES.get(g, g) for g in geos])
    ax.set_xlabel("Approximate Construction Cost (EUR/sqm, 2025)")
    ax.invert_yaxis()

    # Value labels
    for i, (geo, val) in enumerate(abs_sorted):
        ax.text(val + 20, i, f"EUR {val:,}", va="center", fontsize=9)

    # EU average line
    eu_avg = np.mean(vals)
    ax.axvline(eu_avg, color="black", linestyle="--", linewidth=1, label=f"Average: EUR {eu_avg:,.0f}")
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "absolute_eur_sqm.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved absolute_eur_sqm.png")


def plot_5_ireland_rank_over_time():
    """Line chart of Ireland's rank position over time."""
    df = load_data()
    panel = build_panel(df)
    ie_rank = compute_ireland_rank_over_time(panel)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(range(len(ie_rank)), ie_rank["ie_rank"], color=COLORS["IE"],
            linewidth=2, marker="o", markersize=3)
    ax.set_ylabel("Ireland's Rank (1=highest growth, 10=lowest)")
    ax.invert_yaxis()
    ax.set_ylim(10.5, 0.5)
    ax.set_yticks(range(1, 11))

    # X-axis
    quarters = list(ie_rank["quarter"])
    tick_positions = [i for i, q in enumerate(quarters) if q.endswith("-Q1")]
    tick_labels = [q[:4] for q in quarters if q.endswith("-Q1")]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)

    # Annotations
    ax.annotate(f"#{ie_rank.iloc[0]['ie_rank']:.0f}", xy=(0, ie_rank.iloc[0]["ie_rank"]),
                fontsize=10, fontweight="bold", color=COLORS["IE"])
    ax.annotate(f"#{ie_rank.iloc[-1]['ie_rank']:.0f}", xy=(len(ie_rank)-1, ie_rank.iloc[-1]["ie_rank"]),
                fontsize=10, fontweight="bold", color=COLORS["IE"])

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "ireland_rank_over_time.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved ireland_rank_over_time.png")


def plot_6_ireland_vs_eu_avg():
    """Ireland vs EU average over time."""
    df = load_data()
    panel = build_panel(df)
    eu_avg, ie_excess = compute_eu_avg_and_irish_excess(panel)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])

    quarters = list(panel.index)
    x = range(len(quarters))

    # Top: levels
    ax1.plot(x, panel["IE"], color=COLORS["IE"], linewidth=2, label="Ireland")
    ax1.plot(x, eu_avg, color="black", linewidth=2, linestyle="--", label="EU-9 Average")
    ax1.fill_between(x, panel["IE"], eu_avg, alpha=0.2, color=COLORS["IE"])
    ax1.set_ylabel("Index (2015-Q1 = 100)")
    ax1.legend()

    tick_positions = [i for i, q in enumerate(quarters) if q.endswith("-Q1")]
    tick_labels = [q[:4] for q in quarters if q.endswith("-Q1")]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45)

    # Bottom: excess
    ax2.bar(x, ie_excess, color=[COLORS["IE"] if v < 0 else "#d62728" for v in ie_excess],
            alpha=0.7)
    ax2.axhline(0, color="black", linewidth=0.5)
    ax2.set_ylabel("IE - EU Avg (index points)")
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels, rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "ireland_vs_eu_avg.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved ireland_vs_eu_avg.png")


def plot_7_pred_vs_actual():
    """Panel regression predicted vs actual (the mandatory pred-vs-actual plot)."""
    df = load_data()
    panel = build_panel(df)

    import statsmodels.api as sm
    from analyze import run_panel_regression

    model, slopes = run_panel_regression(panel)

    fig, ax = plt.subplots(figsize=(8, 8))

    actual = model.model.endog
    predicted = model.predict()

    ax.scatter(actual, predicted, alpha=0.3, s=10, color="#1f77b4")
    lims = [min(actual.min(), predicted.min()) - 2, max(actual.max(), predicted.max()) + 2]
    ax.plot(lims, lims, "r--", linewidth=1, label="1:1 line")
    ax.set_xlabel("Actual Index Value")
    ax.set_ylabel("Predicted Index Value")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.legend()
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "pred_vs_actual.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved pred_vs_actual.png")


def plot_8_feature_importance():
    """Country-time interaction coefficients as feature importance proxy."""
    df = load_data()
    panel = build_panel(df)

    from analyze import run_panel_regression
    model, slopes = run_panel_regression(panel)

    slopes_sorted = sorted(slopes.items(), key=lambda x: -x[1])

    fig, ax = plt.subplots(figsize=(10, 6))

    geos = [g for g, _ in slopes_sorted]
    vals = [v for _, v in slopes_sorted]
    colors = [COLORS["IE"] if g == "IE" else "#aaaaaa" for g in geos]

    ax.barh(range(len(geos)), vals, color=colors)
    ax.set_yticks(range(len(geos)))
    ax.set_yticklabels([COUNTRY_NAMES.get(g, g) for g in geos])
    ax.set_xlabel("Quarterly Slope (index points per quarter)")
    ax.invert_yaxis()

    for i, (geo, val) in enumerate(slopes_sorted):
        ax.text(val + 0.02, i, f"{val:.3f}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  Saved feature_importance.png")


if __name__ == "__main__":
    print("Generating plots...")
    plot_1_trajectory_comparison()
    plot_2_cumulative_growth_ranking()
    plot_3_subperiod_growth()
    plot_4_absolute_eur_sqm()
    plot_5_ireland_rank_over_time()
    plot_6_ireland_vs_eu_avg()
    plot_7_pred_vs_actual()
    plot_8_feature_importance()
    print("Done. All plots saved to plots/")
