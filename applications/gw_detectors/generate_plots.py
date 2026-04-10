"""
generate_plots.py — Create publication-quality figures for the GW Detectors HDR paper.

Data is hardcoded from the paper's tables and results/per_solution.tsv to avoid
dependence on the large .kat files and strain CSVs at plot-generation time.

Produces four plots in plots/:
  1. headline_finding.png      — improvement factor vs Voyager for all 25 type8 solutions
  2. component_analysis.png    — sol00 over-parameterisation (mirrors + beamsplitters)
  3. squeezer_anticorrelation.png — squeezers vs improvement, r = -0.50
  4. arm_cavity_classification.png — 6 arm-cavity-class spaces classified
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent
PLOTS_DIR = PROJECT_ROOT / "plots"

# ---------------------------------------------------------------------------
# Data from paper Table (Section 3.1) and results/per_solution.tsv
# ---------------------------------------------------------------------------

# Improvement factors from per_solution.tsv (rounded to match paper presentation)
IMPROVEMENT_DATA = [
    {"sol_id": "sol00", "improvement": 4.05},
    {"sol_id": "sol01", "improvement": 3.36},
    {"sol_id": "sol02", "improvement": 2.68},
    {"sol_id": "sol03", "improvement": 2.22},
    {"sol_id": "sol04", "improvement": 1.78},
    {"sol_id": "sol05", "improvement": 1.30},
    {"sol_id": "sol06", "improvement": 1.28},
    {"sol_id": "sol07", "improvement": 1.14},
    {"sol_id": "sol08", "improvement": 1.14},
    {"sol_id": "sol09", "improvement": 1.12},
    {"sol_id": "sol10", "improvement": 1.12},
    {"sol_id": "sol11", "improvement": 1.11},
    {"sol_id": "sol12", "improvement": 1.11},
    {"sol_id": "sol13", "improvement": 1.10},
    {"sol_id": "sol14", "improvement": 1.06},
    {"sol_id": "sol15", "improvement": 1.06},
    {"sol_id": "sol16", "improvement": 1.04},
    {"sol_id": "sol17", "improvement": 1.03},
    {"sol_id": "sol18", "improvement": 1.01},
    {"sol_id": "sol19", "improvement": 1.01},
    {"sol_id": "sol20", "improvement": 1.01},
    {"sol_id": "sol21", "improvement": 1.01},
    {"sol_id": "sol22", "improvement": 1.00},
    {"sol_id": "sol23", "improvement": 1.00},
    {"sol_id": "sol24", "improvement": 1.00},
]

# ---------------------------------------------------------------------------
# Component data from paper Section 3.3 and 3.4
# ---------------------------------------------------------------------------

SOL00_COMPONENT_DATA = {
    "mirrors": {
        "total": 57,
        "at_extremes": 29,     # 20 R<0.001 + 9 R>0.999 = 29 (51%)
        "doing_work": 28,      # interior R range
        "near_zero": 20,       # R < 0.001
        "near_one": 9,         # R > 0.999
    },
    "beamsplitters": {
        "total": 13,
        "at_extremes": 11,     # 2 at R=1.0 (perfect mirrors) + 9 near-transparent
        "doing_work": 2,       # B1_3 (R=0.81) and B3_1 (R=0.30)
        "perfect_mirror": 2,   # R = 1.0
        "near_transparent": 9, # R < 0.1
    },
}

# ---------------------------------------------------------------------------
# Squeezer vs improvement data from per_solution.tsv
# ---------------------------------------------------------------------------

SQUEEZER_DATA = [
    {"sol_id": "sol00", "n_squeezers": 0,  "improvement": 4.05},
    {"sol_id": "sol01", "n_squeezers": 0,  "improvement": 3.36},
    {"sol_id": "sol02", "n_squeezers": 1,  "improvement": 2.68},
    {"sol_id": "sol03", "n_squeezers": 3,  "improvement": 2.22},
    {"sol_id": "sol04", "n_squeezers": 2,  "improvement": 1.78},
    {"sol_id": "sol05", "n_squeezers": 0,  "improvement": 1.30},
    {"sol_id": "sol06", "n_squeezers": 3,  "improvement": 1.28},
    {"sol_id": "sol07", "n_squeezers": 3,  "improvement": 1.14},
    {"sol_id": "sol08", "n_squeezers": 3,  "improvement": 1.14},
    {"sol_id": "sol09", "n_squeezers": 2,  "improvement": 1.12},
    {"sol_id": "sol10", "n_squeezers": 1,  "improvement": 1.12},
    {"sol_id": "sol11", "n_squeezers": 1,  "improvement": 1.11},
    {"sol_id": "sol12", "n_squeezers": 2,  "improvement": 1.11},
    {"sol_id": "sol13", "n_squeezers": 7,  "improvement": 1.10},
    {"sol_id": "sol14", "n_squeezers": 4,  "improvement": 1.06},
    {"sol_id": "sol15", "n_squeezers": 2,  "improvement": 1.06},
    {"sol_id": "sol16", "n_squeezers": 1,  "improvement": 1.04},
    {"sol_id": "sol17", "n_squeezers": 2,  "improvement": 1.03},
    {"sol_id": "sol18", "n_squeezers": 3,  "improvement": 1.01},
    {"sol_id": "sol19", "n_squeezers": 4,  "improvement": 1.01},
    {"sol_id": "sol20", "n_squeezers": 3,  "improvement": 1.01},
    {"sol_id": "sol21", "n_squeezers": 3,  "improvement": 1.01},
    {"sol_id": "sol22", "n_squeezers": 4,  "improvement": 1.00},
    {"sol_id": "sol23", "n_squeezers": 2,  "improvement": 1.00},
    {"sol_id": "sol24", "n_squeezers": 5,  "improvement": 1.00},
]

# ---------------------------------------------------------------------------
# Arm cavity classification from paper Section 3.8 / M02
# ---------------------------------------------------------------------------

ARM_CAVITY_DATA = [
    {
        "space": "mRL_3_2",
        "length_m": 3847.0,
        "R_a": 0.00209,
        "R_b": 0.00015,
        "classification": "Through-pass delay line",
        "detail": "Both endpoints transparent",
    },
    {
        "space": "mRL_3_3",
        "length_m": 3847.0,
        "R_a": 0.5187,
        "R_b": 0.5004,
        "classification": "True symmetric cavity",
        "detail": "Finesse ~4.6, the only real cavity",
    },
    {
        "space": "mRL_3_4",
        "length_m": 3847.0,
        "R_a": 0.9530,
        "R_b": 0.0806,
        "classification": "Asymmetric cavity",
        "detail": "One end nearly perfect, one transparent",
    },
    {
        "space": "mUD_1_1",
        "length_m": 3671.0,
        "R_a": 1.0000,
        "R_b": 1.0000,
        "classification": "Dead trap",
        "detail": "Both ends perfectly reflective, no laser light",
    },
    {
        "space": "mUD_2_1",
        "length_m": 3671.0,
        "R_a": 0.0860,
        "R_b": 1.0000,
        "classification": "One-sided wall",
        "detail": "Perfect reflector on one side",
    },
    {
        "space": "mUD_3_1",
        "length_m": 3671.0,
        "R_a": 0.00002,
        "R_b": 0.00239,
        "classification": "Through-pass delay line",
        "detail": "Both endpoints transparent",
    },
]


# ---------------------------------------------------------------------------
# Colour palette: colourblind-safe (IBM Design / Wong)
# ---------------------------------------------------------------------------

CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_CYAN = "#56B4E9"
CB_YELLOW = "#F0E442"
CB_GREY = "#999999"


def _setup_style():
    """Set seaborn whitegrid style for all plots."""
    sns.set_style("whitegrid")
    plt.rcParams.update({
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "font.size": 14,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })


# ---------------------------------------------------------------------------
# Plot 1: Headline finding — family skew
# ---------------------------------------------------------------------------

def plot_headline_finding(out_path: Path) -> None:
    """Ranked lollipop plot of improvement factor for all 25 type8 solutions."""
    _setup_style()

    data = sorted(IMPROVEMENT_DATA, key=lambda d: d["improvement"], reverse=True)
    labels = [d["sol_id"] for d in data]
    values = [d["improvement"] for d in data]
    median_val = float(np.median(values))

    fig, ax = plt.subplots(figsize=(14, 7))

    # Colour: sol00 highlighted, rest graded
    colours = []
    for i, d in enumerate(data):
        if d["sol_id"] == "sol00":
            colours.append(CB_RED)
        elif d["improvement"] > 2.0:
            colours.append(CB_ORANGE)
        elif d["improvement"] > 1.1:
            colours.append(CB_BLUE)
        else:
            colours.append(CB_GREY)

    # Lollipop stems
    for i, (val, col) in enumerate(zip(values, colours)):
        ax.plot([i, i], [1.0, val], color=col, linewidth=2, zorder=2)

    # Lollipop heads
    ax.scatter(range(len(values)), values, c=colours, s=80, zorder=3, edgecolors="white", linewidths=0.5)

    # Median line
    ax.axhline(y=median_val, color=CB_CYAN, linestyle="--", linewidth=1.5, alpha=0.8, zorder=1)
    ax.text(len(values) - 1, median_val + 0.05, f"median = {median_val:.2f}x",
            ha="right", va="bottom", color=CB_CYAN, fontsize=10, fontweight="bold")

    # Voyager baseline
    ax.axhline(y=1.0, color=CB_GREY, linestyle="-", linewidth=1, alpha=0.5, zorder=0)

    # Annotate sol00
    ax.annotate(
        f"sol00: {values[0]:.2f}x",
        xy=(0, values[0]),
        xytext=(2.5, values[0] + 0.15),
        fontsize=11, fontweight="bold", color=CB_RED,
        arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
    )

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=11)
    ax.set_ylabel("Improvement factor vs LIGO Voyager\n(log-averaged, 800-3000 Hz)", fontsize=14)
    ax.set_xlabel("Type8 solutions (ranked)", fontsize=14)
    ax.set_title("Family Skew: sol00 at 4.05x far above the rest of the type8 family", fontsize=16)
    ax.set_ylim(0.8, 4.5)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=CB_RED, label="sol00 (dominant outlier)"),
        mpatches.Patch(facecolor=CB_ORANGE, label="Substantial improvement (>2x)"),
        mpatches.Patch(facecolor=CB_BLUE, label="Moderate improvement (1.1-2x)"),
        mpatches.Patch(facecolor=CB_GREY, label="Near break-even with Voyager"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=12, framealpha=0.9)

    fig.tight_layout(pad=2.0)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 2: Component analysis — over-parameterisation
# ---------------------------------------------------------------------------

def plot_component_analysis(out_path: Path) -> None:
    """Stacked bar chart of sol00 mirrors and beamsplitters: filler vs working."""
    _setup_style()

    md = SOL00_COMPONENT_DATA["mirrors"]
    bd = SOL00_COMPONENT_DATA["beamsplitters"]

    fig, ax = plt.subplots(figsize=(10, 7))

    categories = ["Mirrors (57 total)", "Beamsplitters (13 total)"]
    doing_work = [md["doing_work"], bd["doing_work"]]
    at_extremes = [md["at_extremes"], bd["at_extremes"]]
    totals = [md["total"], bd["total"]]

    x = np.arange(len(categories))
    bar_width = 0.5

    bars_work = ax.bar(x, doing_work, bar_width, label="Doing work (interior R values)",
                       color=CB_BLUE, edgecolor="white", linewidth=0.5, zorder=3)
    bars_filler = ax.bar(x, at_extremes, bar_width, bottom=doing_work,
                         label="At extreme values (filler/no-ops)",
                         color=CB_ORANGE, edgecolor="white", linewidth=0.5, zorder=3)

    # Percentage annotations
    for i, (work, filler, total) in enumerate(zip(doing_work, at_extremes, totals)):
        pct_filler = 100 * filler / total
        # Annotate the filler portion
        ax.text(i, work + filler / 2, f"{filler} ({pct_filler:.0f}%)\nfiller",
                ha="center", va="center", fontsize=11, fontweight="bold", color="white")
        # Annotate the working portion
        pct_work = 100 * work / total
        ax.text(i, work / 2, f"{work} ({pct_work:.0f}%)\nworking",
                ha="center", va="center", fontsize=11, fontweight="bold", color="white")

    # Mirror detail sub-annotation
    ax.annotate(
        f"20 transparent (R < 0.001)\n9 perfect reflectors (R > 0.999)",
        xy=(0.15, md["doing_work"] + md["at_extremes"]),
        xytext=(0.55, md["total"] + 5),
        fontsize=8.5, color=CB_ORANGE,
        arrowprops=dict(arrowstyle="->", color=CB_ORANGE, lw=1.2),
        ha="left",
    )

    # BS detail sub-annotation
    ax.annotate(
        f"2 at R = 1.0 (act as mirrors)\n9 near-transparent (R < 0.1)",
        xy=(1.1, bd["doing_work"] + bd["at_extremes"]),
        xytext=(1.25, bd["total"] + 18),
        fontsize=8.5, color=CB_ORANGE,
        arrowprops=dict(arrowstyle="->", color=CB_ORANGE, lw=1.2),
        ha="left",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=13)
    ax.set_ylabel("Number of components", fontsize=14)
    ax.set_title("sol00 Over-parameterisation: most components are filler", fontsize=16)
    ax.legend(loc="upper right", fontsize=12, framealpha=0.9)
    ax.set_ylim(0, 70)

    fig.tight_layout(pad=2.0)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 3: Squeezer anti-correlation
# ---------------------------------------------------------------------------

def plot_squeezer_anticorrelation(out_path: Path) -> None:
    """Scatter of squeezer count vs improvement factor, r = -0.50."""
    _setup_style()

    n_sq = np.array([d["n_squeezers"] for d in SQUEEZER_DATA])
    imp = np.array([d["improvement"] for d in SQUEEZER_DATA])
    sol_ids = [d["sol_id"] for d in SQUEEZER_DATA]

    # Compute Pearson r
    r = float(np.corrcoef(n_sq, imp)[0, 1])

    fig, ax = plt.subplots(figsize=(10, 7))

    # Scatter with jitter for overlapping points
    jitter = np.random.RandomState(42).uniform(-0.15, 0.15, size=len(n_sq))
    ax.scatter(n_sq + jitter, imp, c=CB_BLUE, s=70, alpha=0.8, edgecolors="white",
               linewidths=0.5, zorder=3)

    # Highlight sol00 and sol13
    for i, sid in enumerate(sol_ids):
        if sid == "sol00":
            ax.annotate(
                f"sol00\n(0 squeezers, 4.05x)",
                xy=(n_sq[i] + jitter[i], imp[i]),
                xytext=(1.2, 3.8),
                fontsize=9, fontweight="bold", color=CB_RED,
                arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
            )
        elif sid == "sol13":
            ax.annotate(
                f"sol13\n(7 squeezers, 1.10x)",
                xy=(n_sq[i] + jitter[i], imp[i]),
                xytext=(5.5, 1.6),
                fontsize=9, fontweight="bold", color=CB_ORANGE,
                arrowprops=dict(arrowstyle="->", color=CB_ORANGE, lw=1.5),
            )

    # Regression line
    z = np.polyfit(n_sq, imp, 1)
    x_line = np.linspace(-0.5, 7.5, 100)
    y_line = np.polyval(z, x_line)
    ax.plot(x_line, y_line, color=CB_RED, linestyle="--", linewidth=1.5, alpha=0.7,
            label=f"Linear fit (Pearson r = {r:.2f})")

    # Top-4 vs bottom-21 annotation
    ax.axhspan(2.0, 4.5, alpha=0.06, color=CB_GREEN, zorder=0)
    ax.text(6.8, 3.0, "Top 4 solutions:\nmean 1.0 squeezers",
            fontsize=9, color=CB_GREEN, ha="right", style="italic")
    ax.text(6.8, 1.25, "Bottom 21:\nmean 2.7 squeezers",
            fontsize=9, color=CB_GREY, ha="right", style="italic")

    ax.set_xlabel("Number of squeezer elements", fontsize=14)
    ax.set_ylabel("Improvement factor vs Voyager", fontsize=14)
    ax.set_title(f"Squeezer Anti-correlation: more squeezers = worse improvement (r = {r:.2f})", fontsize=16)
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(0.7, 4.5)
    ax.legend(loc="upper right", fontsize=12, framealpha=0.9)

    fig.tight_layout(pad=2.0)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 4: Arm cavity classification
# ---------------------------------------------------------------------------

def plot_arm_cavity_classification(out_path: Path) -> None:
    """Classified bar chart of the 6 arm-cavity-class spaces in sol00."""
    _setup_style()

    fig, ax = plt.subplots(figsize=(13, 7))

    # Colour map by classification
    class_colours = {
        "True symmetric cavity": CB_GREEN,
        "Through-pass delay line": CB_CYAN,
        "Dead trap": CB_RED,
        "One-sided wall": CB_ORANGE,
        "Asymmetric cavity": CB_PURPLE,
    }

    data = ARM_CAVITY_DATA
    labels = [d["space"] for d in data]
    lengths = [d["length_m"] for d in data]
    classifications = [d["classification"] for d in data]
    colours = [class_colours[d["classification"]] for d in data]

    x = np.arange(len(data))
    bars = ax.bar(x, lengths, color=colours, edgecolor="white", linewidth=0.5, width=0.6, zorder=3)

    # Add reflectivity annotations on each bar
    for i, d in enumerate(data):
        # Classification label above bar
        ax.text(i, lengths[i] + 50, d["classification"],
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                color=colours[i])
        # Reflectivity values inside bar
        r_text = f"R_A = {d['R_a']:.4f}\nR_B = {d['R_b']:.4f}"
        ax.text(i, lengths[i] / 2, r_text,
                ha="center", va="center", fontsize=8, color="white",
                fontweight="bold")
        # Detail below x-axis
        ax.text(i, -250, d["detail"], ha="center", va="top", fontsize=7,
                color=CB_GREY, style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, rotation=30, ha="right")
    ax.set_ylabel("Length (metres)", fontsize=14)
    ax.set_title("Arm-Cavity Classification: only 1 of 6 long spaces is a true cavity", fontsize=16)
    ax.set_ylim(-500, 4400)

    # Add a "true cavity" highlight
    ax.axhline(y=0, color="black", linewidth=0.5)

    # Legend
    legend_elements = [mpatches.Patch(facecolor=c, label=l) for l, c in class_colours.items()]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=12, framealpha=0.9,
              title="Space classification", title_fontsize=12)

    fig.tight_layout(pad=2.0)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Generate all four plots."""
    PLOTS_DIR.mkdir(exist_ok=True)

    plot_headline_finding(PLOTS_DIR / "headline_finding.png")
    print(f"  Wrote {PLOTS_DIR / 'headline_finding.png'}")

    plot_component_analysis(PLOTS_DIR / "component_analysis.png")
    print(f"  Wrote {PLOTS_DIR / 'component_analysis.png'}")

    plot_squeezer_anticorrelation(PLOTS_DIR / "squeezer_anticorrelation.png")
    print(f"  Wrote {PLOTS_DIR / 'squeezer_anticorrelation.png'}")

    plot_arm_cavity_classification(PLOTS_DIR / "arm_cavity_classification.png")
    print(f"  Wrote {PLOTS_DIR / 'arm_cavity_classification.png'}")

    print(f"\nAll 4 plots generated in {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
