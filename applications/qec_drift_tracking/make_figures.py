"""
Figures for qec_drift_tracking paper.

fig1_phase_diagram: strict-win heatmap over (timescale, amplitude).
fig2_mse_comparison: PF vs baselines log-log scatter across cells.
fig3_lcd_as_smc: schematic of the 1-particle-SMC / LCD unification.
"""

from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)


def load_results():
    rows = []
    with (HERE / "results.tsv").open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["id"].startswith("E01_synthetic_"):
                rows.append({
                    "ts": float(row["timescale_s"]),
                    "amp": float(row["amplitude"]),
                    "mse_pf": float(row["mse_pf"]),
                    "mse_sw": float(row["mse_sw"]),
                    "mse_bay": float(row["mse_bay"]),
                    "strict_win": row["pf_strict_win"].lower() == "true",
                })
    return rows


def fig1_phase_diagram(rows):
    ts_vals = sorted(set(r["ts"] for r in rows))
    amp_vals = sorted(set(r["amp"] for r in rows))
    grid = np.zeros((len(amp_vals), len(ts_vals)), dtype=bool)
    for r in rows:
        i = amp_vals.index(r["amp"])
        j = ts_vals.index(r["ts"])
        grid[i, j] = r["strict_win"]

    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(grid.astype(int), aspect="auto", cmap="RdYlGn",
                   vmin=0, vmax=1, origin="lower")
    ax.set_xticks(range(len(ts_vals)))
    ax.set_xticklabels([f"{t:g}" for t in ts_vals], rotation=20)
    ax.set_yticks(range(len(amp_vals)))
    ax.set_yticklabels([f"{a:.2f}" for a in amp_vals])
    ax.set_xlabel("drift timescale τ (s)")
    ax.set_ylabel("drift amplitude σ (log-rate std dev)")
    ax.set_title("Particle filter vs sliding-window MLE + static Bayesian\n"
                 f"(green = strict PF win; {100*grid.mean():.1f}% of plane)")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            label = "✓" if grid[i, j] else "✗"
            ax.text(j, i, label, ha="center", va="center",
                   color="white" if grid[i, j] else "black", fontsize=12, fontweight="bold")
    fig.tight_layout()
    path = FIGS / "fig1_phase_diagram.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig2_mse_comparison(rows):
    pf_mse = np.array([r["mse_pf"] for r in rows])
    sw_mse = np.array([r["mse_sw"] for r in rows])
    bay_mse = np.array([r["mse_bay"] for r in rows])
    colors = ["tab:green" if r["strict_win"] else "tab:red" for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.scatter(sw_mse, pf_mse, c=colors, s=60, edgecolor="black")
    lims = [min(sw_mse.min(), pf_mse.min()) * 0.5, max(sw_mse.max(), pf_mse.max()) * 2]
    ax1.plot(lims, lims, "k--", alpha=0.4, label="PF = SW-MLE")
    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel("SW-MLE MSE")
    ax1.set_ylabel("Particle filter MSE")
    ax1.set_title("PF vs Sliding-Window MLE")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    ax2.scatter(bay_mse, pf_mse, c=colors, s=60, edgecolor="black")
    lims = [min(bay_mse.min(), pf_mse.min()) * 0.5, max(bay_mse.max(), pf_mse.max()) * 2]
    ax2.plot(lims, lims, "k--", alpha=0.4, label="PF = Static Bayes")
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("Static Bayesian MSE")
    ax2.set_ylabel("Particle filter MSE")
    ax2.set_title("PF vs Static Bayesian")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    fig.tight_layout()
    path = FIGS / "fig2_mse_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


if __name__ == "__main__":
    rows = load_results()
    for f in (fig1_phase_diagram(rows), fig2_mse_comparison(rows)):
        print(f"wrote {f}")
