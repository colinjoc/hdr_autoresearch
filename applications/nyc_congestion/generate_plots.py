#!/usr/bin/env python3
"""Generate publication-quality plots for the NYC congestion charge project.

Produces 4 PNGs in plots/:
  1. before_after_volume.png — Traffic volume pre/post by borough
  2. mta_ridership_trend.png — Subway + bus ridership with charge date marked
  3. tlc_cbd_shift.png — TLC trip CBD vs outer share pre/post
  4. decomposition.png — Waterfall chart of effect decomposition

Usage:
    python generate_plots.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from data_loaders import (
    build_master_dataset,
    load_mta_ridership,
    aggregate_mta_weekly,
    load_tlc_summary,
    CHARGE_START,
)
from model import decompose_volume_change

PLOTS_DIR = HERE / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

# Style
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.figsize": (10, 6),
})
# Colourblind-safe palette
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9"]


def plot_mta_ridership_trend():
    """Plot 2: MTA subway + bus ridership weekly trend with charge date."""
    mta = load_mta_ridership()
    mta_weekly = aggregate_mta_weekly(mta)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Filter to 2024+ for clarity
    mta_recent = mta_weekly[mta_weekly["week_start"] >= "2024-01-01"].copy()

    if "subway_ridership" in mta_recent.columns:
        ax.plot(mta_recent["week_start"], mta_recent["subway_ridership"] / 1e6,
                color=COLORS[0], linewidth=2, label="Subway", marker="", markersize=3)
    if "bus_ridership" in mta_recent.columns:
        ax.plot(mta_recent["week_start"], mta_recent["bus_ridership"] / 1e6,
                color=COLORS[1], linewidth=2, label="Bus", marker="", markersize=3)
    if "bridge_tunnel_traffic" in mta_recent.columns:
        ax.plot(mta_recent["week_start"], mta_recent["bridge_tunnel_traffic"] / 1e6,
                color=COLORS[2], linewidth=2, label="Bridges & Tunnels", marker="", markersize=3)

    # Mark congestion charge start
    ax.axvline(CHARGE_START, color="red", linestyle="--", linewidth=2,
               label="Congestion charge starts", alpha=0.8)

    ax.set_xlabel("Week")
    ax.set_ylabel("Weekly ridership / traffic (millions)")
    ax.set_title("MTA Weekly Ridership and Bridge Traffic Around Congestion Charge Launch")
    ax.legend(loc="lower right", framealpha=0.9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    fig.autofmt_xdate(rotation=30)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "mta_ridership_trend.png")
    plt.close(fig)
    print("  Saved mta_ridership_trend.png")


def plot_tlc_cbd_shift():
    """Plot 3: TLC CBD vs outer borough trip share pre/post."""
    tlc = load_tlc_summary()

    # Aggregate by period
    summary = []
    for period in ["pre", "post"]:
        subset = tlc[tlc["period"] == period]
        total = subset["total_trips"].sum()
        cbd_pu = subset["cbd_pickups"].sum()
        cbd_do = subset["cbd_dropoffs"].sum()
        outer_pu = subset["outer_pickups"].sum()
        outer_do = subset["outer_dropoffs"].sum()
        summary.append({
            "period": period.upper(),
            "CBD Pickups": cbd_pu / total * 100 if total > 0 else 0,
            "CBD Dropoffs": cbd_do / total * 100 if total > 0 else 0,
            "Outer Pickups": outer_pu / total * 100 if total > 0 else 0,
            "Outer Dropoffs": outer_do / total * 100 if total > 0 else 0,
            "total_trips": total,
        })

    df_summary = pd.DataFrame(summary)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: CBD shares
    x = np.arange(2)
    width = 0.35
    ax = axes[0]
    ax.bar(x - width/2, df_summary["CBD Pickups"], width, label="CBD Pickups",
           color=COLORS[0])
    ax.bar(x + width/2, df_summary["CBD Dropoffs"], width, label="CBD Dropoffs",
           color=COLORS[1])
    ax.set_xticks(x)
    ax.set_xticklabels(df_summary["period"])
    ax.set_ylabel("Share of total trips (%)")
    ax.set_title("CBD Trip Share Before and After Congestion Charge")
    ax.legend()
    ax.set_ylim(0, 55)
    for i, row in df_summary.iterrows():
        ax.text(i - width/2, row["CBD Pickups"] + 0.5, f'{row["CBD Pickups"]:.1f}%',
                ha="center", va="bottom", fontsize=9)
        ax.text(i + width/2, row["CBD Dropoffs"] + 0.5, f'{row["CBD Dropoffs"]:.1f}%',
                ha="center", va="bottom", fontsize=9)

    # Right: total trips
    ax2 = axes[1]
    bars = ax2.bar(x, [s["total_trips"] / 1e6 for s in summary],
                    color=[COLORS[0], COLORS[1]])
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_summary["period"])
    ax2.set_ylabel("Total trips (millions)")
    ax2.set_title("Total TLC Trips (Yellow + Green + FHVHV)")
    for bar, s in zip(bars, summary):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 f'{s["total_trips"]/1e6:.1f}M', ha="center", va="bottom", fontsize=10)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "tlc_cbd_shift.png")
    plt.close(fig)
    print("  Saved tlc_cbd_shift.png")


def plot_decomposition():
    """Plot 4: Waterfall chart of effect decomposition."""
    df = build_master_dataset()
    result = decompose_volume_change(df)

    components = [
        ("Total Change", result["total_change"]),
        ("Mode Shift\n(to transit)", result["mode_shift"]),
        ("Route\nDisplacement", result["route_displacement"]),
        ("Time-of-Day\nShift", result["time_shift"]),
        ("Trip\nElimination", result["trip_elimination"]),
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    labels = [c[0] for c in components]
    values = [c[1] for c in components]
    colors_bar = []
    for v in values:
        if abs(v) < 1:
            colors_bar.append("#999999")
        elif v > 0:
            colors_bar.append(COLORS[1])
        else:
            colors_bar.append(COLORS[0])

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors_bar, edgecolor="black", linewidth=0.5)

    # Add value labels
    for bar, val in zip(bars, values):
        ypos = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, ypos + (0.5 if ypos >= 0 else -1.5),
                f'{val:+.1f}%', ha="center", va="bottom" if ypos >= 0 else "top",
                fontsize=11, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Change (%)")
    ax.set_title("Decomposition of Manhattan Traffic Volume Change\nAfter Congestion Charge (Jan 2025)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "decomposition.png")
    plt.close(fig)
    print("  Saved decomposition.png")


def plot_borough_volume_trend():
    """Plot 1: Weekly traffic volume by borough with charge date."""
    master = build_master_dataset()

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, boro in enumerate(sorted(master["boro"].unique())):
        subset = master[master["boro"] == boro].sort_values("week_start")
        ax.plot(subset["week_start"], subset["daily_vol_mean"] / 1000,
                color=COLORS[i % len(COLORS)], linewidth=1.5, label=boro, alpha=0.8)

    ax.axvline(CHARGE_START, color="red", linestyle="--", linewidth=2,
               label="Congestion charge starts", alpha=0.8)

    ax.set_xlabel("Week")
    ax.set_ylabel("Average daily volume (thousands)")
    ax.set_title("NYC DOT Automated Traffic Counts by Borough (Weekly Average)")
    ax.legend(loc="upper left", framealpha=0.9, fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    fig.autofmt_xdate(rotation=30)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "borough_volume_trend.png")
    plt.close(fig)
    print("  Saved borough_volume_trend.png")


def main():
    print("Generating plots...")
    plot_borough_volume_trend()
    plot_mta_ridership_trend()
    plot_tlc_cbd_shift()
    plot_decomposition()
    print("Done.")


if __name__ == "__main__":
    main()
