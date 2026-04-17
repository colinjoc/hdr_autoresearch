"""
Generate all plots for the viability frontier paper.

Reads results.tsv and cached data to produce PNG plots at 300 DPI.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from viability import (
    assess_county_viability, calculate_viability, load_rzlpa02,
    COUNTY_SALE_PRICES_2025, DEV_CONTRIBUTIONS, ZONED_HECTARES,
    get_construction_cost_per_sqm, national_viability_margin,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
COLORS = plt.cm.tab10.colors


def plot_viability_by_county():
    """Plot 1 (headline): Viability margin by county — horizontal bar chart."""
    df = assess_county_viability()
    df = df.sort_values("margin_pct", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#d32f2f" if m < -0.05 else "#ff9800" if m < 0.05 else "#388e3c"
              for m in df["margin_pct"]]
    bars = ax.barh(df["county"].str.replace("Co. ", ""), df["margin_pct"] * 100, color=colors)
    ax.axvline(0, color="black", linewidth=1.5, linestyle="-")
    ax.axvline(-5, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_xlabel("Viability Margin (% of sale price)")
    ax.set_title("")
    # Add value labels
    for bar, val in zip(bars, df["margin_pct"]):
        ax.text(bar.get_width() - 2, bar.get_y() + bar.get_height() / 2,
                f"{val:.0%}", va="center", ha="right", fontsize=8, color="white", fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "headline_finding.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  headline_finding.png")


def plot_cost_breakdown():
    """Plot 2 (feature importance analog): Cost breakdown stacked bar for selected counties."""
    counties = ["Co. Dublin", "Co. Cork", "Co. Galway", "Co. Limerick",
                "Co. Waterford", "Co. Tipperary", "Co. Donegal", "Co. Leitrim"]
    df = assess_county_viability()
    df = df[df["county"].isin(counties)].sort_values("sale_price", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(df))
    labels = df["county"].str.replace("Co. ", "")

    # Stacked bars
    land = df["land_cost_per_unit"].values
    construction = df["construction_cost"].values
    dev = df["dev_contributions"].values
    finance = df["finance_cost"].values
    profit = df["required_profit"].values

    ax.bar(x, land, label="Land", color="#4CAF50")
    ax.bar(x, construction, bottom=land, label="Construction", color="#2196F3")
    ax.bar(x, dev, bottom=land + construction, label="Dev. Contributions", color="#FF9800")
    ax.bar(x, finance, bottom=land + construction + dev, label="Finance", color="#9C27B0")
    ax.bar(x, profit, bottom=land + construction + dev + finance, label="Profit (17.5%)", color="#F44336")

    # Sale price line
    ax.scatter(x, df["sale_price"].values, color="black", zorder=5, s=80, marker="D", label="Sale Price")
    ax.plot(x, df["sale_price"].values, color="black", linewidth=2, linestyle="--", zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("EUR per unit")
    ax.legend(loc="upper right", fontsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"€{x:,.0f}"))

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  feature_importance.png (cost breakdown)")


def plot_pred_vs_actual():
    """Plot 3: Predicted break-even vs actual sale price (scatter)."""
    df = assess_county_viability()

    # Compute break-even price for each county
    breakevens = []
    for _, row in df.iterrows():
        county = row["county"]
        lo, hi = 100000, 1200000
        for _ in range(50):
            mid = (lo + hi) / 2
            r = calculate_viability(
                sale_price=mid,
                land_cost_per_hectare=row["land_cost_per_hectare"],
                construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                avg_sqm=110,
                dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
            )
            if r["margin"] > 0:
                hi = mid
            else:
                lo = mid
        breakevens.append(mid)

    df["break_even"] = breakevens

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(df["sale_price"] / 1000, df["break_even"] / 1000, s=80, c="#2196F3", edgecolors="black", alpha=0.8)

    # Add county labels
    for _, row in df.iterrows():
        ax.annotate(row["county"].replace("Co. ", ""),
                    (row["sale_price"] / 1000, row["break_even"] / 1000),
                    fontsize=7, ha="left", va="bottom",
                    xytext=(3, 3), textcoords="offset points")

    # 1:1 line
    mn = min(df["sale_price"].min(), df["break_even"].min()) / 1000
    mx = max(df["sale_price"].max(), df["break_even"].max()) / 1000
    ax.plot([mn, mx], [mn, mx], "k--", linewidth=1.5, label="1:1 (viability threshold)")
    ax.fill_between([mn, mx], [mn, mx], [mx, mx], alpha=0.1, color="red", label="Unviable zone")

    ax.set_xlabel("Current Median Sale Price (€k)")
    ax.set_ylabel("Break-Even Sale Price (€k)")
    ax.legend()
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "pred_vs_actual.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  pred_vs_actual.png")


def plot_sensitivity_tornado():
    """Plot 4: Tornado chart of parameter sensitivities."""
    base = national_viability_margin()

    # Run sensitivity for each parameter
    sensitivities = {}

    # Construction cost ±15%
    for mult, label in [(0.85, "-15%"), (1.15, "+15%")]:
        land_df = load_rzlpa02()
        rows = []
        for _, row in land_df.iterrows():
            county = row["county"]
            if county in COUNTY_SALE_PRICES_2025:
                ml = row.get("median_price_per_hectare")
                if pd.isna(ml): continue
                r = calculate_viability(COUNTY_SALE_PRICES_2025[county], ml,
                                        construction_cost_per_sqm=get_construction_cost_per_sqm(county) * mult,
                                        avg_sqm=110, dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000))
                r["county"] = county; r["zoned_hectares"] = ZONED_HECTARES.get(county, 0)
                rows.append(r)
        df_tmp = pd.DataFrame(rows)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        sensitivities.setdefault("Construction cost ±15%", {})[label] = wm

    # Finance rate 5% vs 15%
    for rate, label in [(0.05, "-50%"), (0.15, "+50%")]:
        df_tmp = assess_county_viability(finance_rate=rate)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        sensitivities.setdefault("Finance rate (5-15%)", {})[label] = wm

    # Profit margin 12% vs 22%
    for pm, label in [(0.12, "-30%"), (0.22, "+30%")]:
        df_tmp = assess_county_viability(profit_margin=pm)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        sensitivities.setdefault("Profit margin (12-22%)", {})[label] = wm

    # Unit size 85 vs 135 sqm
    for sqm, label in [(85, "-23%"), (135, "+23%")]:
        df_tmp = assess_county_viability(avg_sqm=sqm)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        sensitivities.setdefault("Unit size (85-135 sqm)", {})[label] = wm

    # Density 25 vs 60 u/ha
    for d, label in [(25, "-38%"), (60, "+50%")]:
        df_tmp = assess_county_viability(density=d)
        wm = (df_tmp["margin_pct"] * df_tmp["zoned_hectares"]).sum() / df_tmp["zoned_hectares"].sum()
        sensitivities.setdefault("Density (25-60 u/ha)", {})[label] = wm

    fig, ax = plt.subplots(figsize=(10, 5))
    params = list(sensitivities.keys())
    lows = []
    highs = []
    for p in params:
        vals = list(sensitivities[p].values())
        lows.append(min(vals))
        highs.append(max(vals))

    # Sort by spread
    spreads = [h - l for l, h in zip(lows, highs)]
    order = np.argsort(spreads)
    params = [params[i] for i in order]
    lows = [lows[i] for i in order]
    highs = [highs[i] for i in order]

    y = range(len(params))
    ax.barh(y, [(h - base) * 100 for h in highs], left=[base * 100] * len(params),
            color="#4CAF50", alpha=0.7, label="Favorable")
    ax.barh(y, [(l - base) * 100 for l in lows], left=[base * 100] * len(params),
            color="#F44336", alpha=0.7, label="Adverse")
    ax.axvline(base * 100, color="black", linewidth=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels(params)
    ax.set_xlabel("Viability Margin (%)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "sensitivity_tornado.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  sensitivity_tornado.png")


def plot_stranded_hectares():
    """Plot 5: Stranded hectares by county."""
    df = assess_county_viability()
    df = df.sort_values("stranded_hectares", ascending=True)
    df = df[df["stranded_hectares"] > 0]

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#d32f2f" if m < -0.5 else "#ff9800" for m in df["margin_pct"]]
    ax.barh(df["county"].str.replace("Co. ", ""), df["stranded_hectares"], color=colors)
    ax.set_xlabel("Stranded Hectares (zoned, unviable)")

    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row["stranded_hectares"] + 10, i,
                f"{row['stranded_hectares']:.0f} ha ({row['margin_pct']:.0%})",
                va="center", fontsize=7)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "stranded_hectares.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  stranded_hectares.png")


def plot_monte_carlo():
    """Plot 6: Monte Carlo margin distribution."""
    np.random.seed(42)
    n_sims = 10000
    margins = []
    for _ in range(n_sims):
        sp = np.random.normal(387000, 387000 * 0.15)
        lc = np.random.lognormal(np.log(571235), 0.3)
        cc = np.random.normal(2690, 2690 * 0.10)
        dc = np.random.uniform(8000, 28000)
        fr = np.random.uniform(0.06, 0.14)
        bd = np.random.uniform(1.5, 3.5)
        pm = np.random.uniform(0.12, 0.22)
        r = calculate_viability(sp, lc, 40, cc, 110, dc, fr, bd, pm)
        margins.append(r["margin_pct"] * 100)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(margins, bins=80, color="#2196F3", alpha=0.7, edgecolor="white")
    ax.axvline(0, color="red", linewidth=2, linestyle="-", label="Viability threshold")
    ax.axvline(np.mean(margins), color="black", linewidth=1.5, linestyle="--", label=f"Mean: {np.mean(margins):.1f}%")
    pct_viable = np.mean(np.array(margins) > 0) * 100
    ax.set_xlabel("Viability Margin (%)")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.text(0.95, 0.95, f"{pct_viable:.1f}% viable\n(margin > 0)",
            transform=ax.transAxes, ha="right", va="top", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "monte_carlo.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("  monte_carlo.png")


if __name__ == "__main__":
    print("Generating plots...")
    plot_viability_by_county()
    plot_cost_breakdown()
    plot_pred_vs_actual()
    plot_sensitivity_tornado()
    plot_stranded_hectares()
    plot_monte_carlo()
    print("All plots generated in plots/")
