#!/usr/bin/env python3
"""Generate publication-quality plots for the phantom traffic jam paper.

Produces 5 PNG files in plots/:
  1. trajectory_baseline.png   — space-time diagram, all-IDM baseline
  2. trajectory_suppressed.png — space-time diagram, ACC 4/22
  3. headline_finding.png      — wave amplitude vs number of ACC vehicles
  4. controller_comparison.png — wave amplitude by controller at 18.2%
  5. pareto_front.png          — wave amplitude vs throughput (ACC sweep)

Usage:
    python generate_plots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import seaborn as sns

# Ensure project root is importable
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from sim_ring_road import RingRoadConfig, simulate
from controllers import ACCController

PLOTS_DIR = APP_DIR / "plots"
DPI = 300


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

def _apply_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    })


# ---------------------------------------------------------------------------
# Colourblind-safe palette (Wong 2011)
# ---------------------------------------------------------------------------

CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_CYAN = "#56B4E9"
CB_YELLOW = "#F0E442"
CB_BLACK = "#000000"


# ---------------------------------------------------------------------------
# 1 & 2. Space-time trajectory diagrams
# ---------------------------------------------------------------------------

def _run_trajectory(n_acc: int, seed: int = 42) -> pd.DataFrame:
    """Run the 22-vehicle ring and return trajectory DataFrame."""
    cfg = RingRoadConfig(seed=seed, t_max=600.0)
    if n_acc == 0:
        return simulate(cfg)
    else:
        spacing = 22 / n_acc
        indices = [int(round(i * spacing)) % 22 for i in range(n_acc)]
        indices = sorted(set(indices))
        return simulate(cfg, smart_indices=indices,
                        smart_controller_factory=lambda: ACCController())


def _plot_spacetime(df: pd.DataFrame, title: str, outpath: Path):
    """Create a space-time (position vs time) scatter coloured by velocity.

    Each dot is a vehicle at a given time. Colour encodes velocity:
    dark (near 0 m/s) = stopped/jammed, bright = moving freely.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    # Subsample for speed: every 5th timestep (0.5 s resolution)
    times = sorted(df["time"].unique())
    keep_times = times[::5]
    sub = df[df["time"].isin(keep_times)]

    # Use a diverging-style colourmap that is colourblind-friendly
    # viridis: dark purple = low velocity, yellow = high velocity
    sc = ax.scatter(
        sub["time"], sub["position"],
        c=sub["velocity"], cmap="viridis",
        s=0.3, edgecolors="none", rasterized=True,
        vmin=0.0, vmax=max(df["velocity"].quantile(0.99), 8.0),
    )
    cbar = fig.colorbar(sc, ax=ax, label="Velocity (m/s)", pad=0.02)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position on ring (m)")
    ax.set_title(title)
    ax.set_xlim(0, df["time"].max())
    ax.set_ylim(0, 230)

    fig.tight_layout()
    fig.savefig(outpath, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {outpath.name}")


def plot_trajectory_baseline():
    print("Generating trajectory_baseline.png ...")
    df = _run_trajectory(n_acc=0)
    _plot_spacetime(
        df,
        "All-IDM Baseline: Stop-and-Go Wave on Sugiyama Ring",
        PLOTS_DIR / "trajectory_baseline.png",
    )


def plot_trajectory_suppressed():
    print("Generating trajectory_suppressed.png ...")
    df = _run_trajectory(n_acc=4)
    _plot_spacetime(
        df,
        "4 ACC Vehicles (18.2%): Wave Suppressed",
        PLOTS_DIR / "trajectory_suppressed.png",
    )


# ---------------------------------------------------------------------------
# 3. Headline finding: wave amplitude vs number of ACC vehicles
# ---------------------------------------------------------------------------

def plot_headline_finding():
    """Wave amplitude vs n_smart for ACC, showing the sharp drop at 4/22."""
    print("Generating headline_finding.png ...")

    sweep_file = APP_DIR / "discoveries" / "penetration_sweep.csv"
    sweep = pd.read_csv(sweep_file)
    acc = sweep[sweep["sweep_controller"] == "ACC"].copy()
    acc = acc.sort_values("n_smart")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(acc["n_smart"], acc["wave_amp_ms"],
            marker="o", color=CB_BLUE, linewidth=2, markersize=7,
            zorder=3, label="ACC")

    # Highlight the critical transition at 4/22
    row4 = acc[acc["n_smart"] == 4].iloc[0]
    ax.annotate(
        f'4/22 vehicles\n{row4["wave_amp_ms"]:.2f} m/s\n(93.3% reduction)',
        xy=(4, row4["wave_amp_ms"]),
        xytext=(8, 4.5),
        fontsize=10,
        arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
        color=CB_RED, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor=CB_RED, alpha=0.9),
    )

    # Baseline reference line
    ax.axhline(y=8.17, color=CB_ORANGE, linestyle="--", linewidth=1.5,
               alpha=0.7, label="Baseline (all-IDM): 8.17 m/s")

    # Mark the 1 m/s threshold
    ax.axhline(y=1.0, color="gray", linestyle=":", linewidth=1,
               alpha=0.6, label="1 m/s threshold")

    ax.set_xlabel("Number of ACC vehicles (out of 22)")
    ax.set_ylabel("Wave amplitude (m/s)")
    ax.set_title("Sharp Penetration Threshold for Wave Suppression")
    ax.set_xticks(range(0, 23, 2))
    ax.set_ylim(-0.3, 9.5)
    ax.legend(loc="upper right", framealpha=0.9)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "headline_finding.png", dpi=DPI,
                bbox_inches="tight")
    plt.close(fig)
    print("  Saved headline_finding.png")


# ---------------------------------------------------------------------------
# 4. Controller comparison bar chart at 18.2% penetration
# ---------------------------------------------------------------------------

def plot_controller_comparison():
    """Bar chart of wave amplitude by controller family at 18.2%."""
    print("Generating controller_comparison.png ...")

    results = pd.read_csv(APP_DIR / "results.tsv", sep="\t")

    # Pull tournament rows at 18.2% penetration (T02, T04, T06, T08, T10)
    # plus baseline E00
    rows = []
    # E00 baseline
    e00 = results[results["exp_id"] == "E00"].iloc[0]
    rows.append({"Controller": "Baseline\n(All-IDM)", "wave_amp_ms": e00["wave_amp_ms"],
                 "throughput_vph": e00["throughput_vph"]})
    # T04 FS 18.2%
    t04 = results[results["exp_id"] == "T04"].iloc[0]
    rows.append({"Controller": "Follower\nStopper", "wave_amp_ms": t04["wave_amp_ms"],
                 "throughput_vph": t04["throughput_vph"]})
    # T06 PI 18.2%
    t06 = results[results["exp_id"] == "T06"].iloc[0]
    rows.append({"Controller": "PI with\nSaturation", "wave_amp_ms": t06["wave_amp_ms"],
                 "throughput_vph": t06["throughput_vph"]})
    # T08 ACC 18.2%
    t08 = results[results["exp_id"] == "T08"].iloc[0]
    rows.append({"Controller": "ACC", "wave_amp_ms": t08["wave_amp_ms"],
                 "throughput_vph": t08["throughput_vph"]})
    # T10 ConstantVelocity 18.2%
    t10 = results[results["exp_id"] == "T10"].iloc[0]
    rows.append({"Controller": "Constant\nVelocity*", "wave_amp_ms": t10["wave_amp_ms"],
                 "throughput_vph": t10["throughput_vph"]})

    df_bar = pd.DataFrame(rows)

    colours = [CB_BLACK, CB_ORANGE, CB_RED, CB_BLUE, CB_PURPLE]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(df_bar["Controller"], df_bar["wave_amp_ms"],
                  color=colours, edgecolor="white", linewidth=0.8, width=0.65)

    # Add value labels on top of each bar
    for bar, row in zip(bars, rows):
        height = bar.get_height()
        label_y = height + 0.4
        # For PI which is very tall, put label inside
        if height > 15:
            ax.text(bar.get_x() + bar.get_width() / 2, height - 2,
                    f'{height:.1f}',
                    ha='center', va='top', fontweight='bold', color='white',
                    fontsize=11)
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, label_y,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=10)

    ax.set_ylabel("Wave amplitude (m/s)")
    ax.set_title("Controller Comparison at 18.2% Penetration (4/22 vehicles)")
    ax.set_ylim(0, 35)

    # Add footnote for ConstantVelocity
    ax.annotate("* Constant Velocity ignores leader — unsafe, shown for reference only",
                xy=(0.5, -0.12), xycoords="axes fraction",
                ha="center", fontsize=8, fontstyle="italic", color="gray")

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "controller_comparison.png", dpi=DPI,
                bbox_inches="tight")
    plt.close(fig)
    print("  Saved controller_comparison.png")


# ---------------------------------------------------------------------------
# 5. Pareto front: wave amplitude vs throughput
# ---------------------------------------------------------------------------

def plot_pareto_front():
    """Wave amplitude vs throughput for ACC at different penetration rates."""
    print("Generating pareto_front.png ...")

    sweep_file = APP_DIR / "discoveries" / "penetration_sweep.csv"
    sweep = pd.read_csv(sweep_file)
    acc = sweep[sweep["sweep_controller"] == "ACC"].copy()
    acc = acc.sort_values("n_smart")

    fig, ax = plt.subplots(figsize=(8, 5.5))

    # Plot all ACC points
    sc = ax.scatter(
        acc["throughput_vph"], acc["wave_amp_ms"],
        c=acc["n_smart"], cmap="viridis_r",
        s=80, edgecolors="white", linewidth=0.8, zorder=3,
    )
    # Connect with a line
    ax.plot(acc["throughput_vph"], acc["wave_amp_ms"],
            color="gray", linewidth=1, alpha=0.5, zorder=2)

    cbar = fig.colorbar(sc, ax=ax, label="Number of ACC vehicles")
    cbar.set_ticks([0, 4, 8, 11, 16, 22])

    # Annotate key points
    baseline = acc[acc["n_smart"] == 0].iloc[0]
    ax.annotate("Baseline\n(0 ACC)", xy=(baseline["throughput_vph"], baseline["wave_amp_ms"]),
                xytext=(baseline["throughput_vph"] - 120, baseline["wave_amp_ms"] - 1.5),
                fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="->", color="gray"))

    knee = acc[acc["n_smart"] == 4].iloc[0]
    ax.annotate("4 ACC (18.2%)\nKnee point",
                xy=(knee["throughput_vph"], knee["wave_amp_ms"]),
                xytext=(knee["throughput_vph"] + 80, knee["wave_amp_ms"] + 2.0),
                fontsize=9, ha="center", color=CB_RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=CB_RED, alpha=0.9))

    full = acc[acc["n_smart"] == 22].iloc[0]
    ax.annotate("All ACC\n(100%)", xy=(full["throughput_vph"], full["wave_amp_ms"]),
                xytext=(full["throughput_vph"] + 60, full["wave_amp_ms"] + 1.5),
                fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="->", color="gray"))

    ax.set_xlabel("Throughput (veh/hr)")
    ax.set_ylabel("Wave amplitude (m/s)")
    ax.set_title("Pareto Front: Wave Suppression vs Throughput (ACC Sweep)")

    # Shade the Pareto-efficient region
    ax.axhline(y=1.0, color="gray", linestyle=":", linewidth=1, alpha=0.5)
    ax.text(400, 1.2, "1 m/s threshold", fontsize=8, color="gray",
            fontstyle="italic")

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "pareto_front.png", dpi=DPI,
                bbox_inches="tight")
    plt.close(fig)
    print("  Saved pareto_front.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    _apply_style()
    PLOTS_DIR.mkdir(exist_ok=True)

    plot_trajectory_baseline()
    plot_trajectory_suppressed()
    plot_headline_finding()
    plot_controller_comparison()
    plot_pareto_front()

    print(f"\nAll plots saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
