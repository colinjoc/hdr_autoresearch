"""
Generate all plots for the AARO Case Resolution Analysis paper.

Reads data from extract_data.py and produces PNGs in plots/ directory.
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from extract_data import (
    compute_resolution_rates,
    compute_backlog_growth,
    compute_base_rate_comparison,
    compute_bayesian_posterior,
    extract_fy2024_figures,
)

PLOTS_DIR = os.path.join(PROJECT_ROOT, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9", "#E69F00"]


def plot_resolution_rates():
    """Plot 1: Resolution rates across programs/periods (headline finding)."""
    rates = compute_resolution_rates()
    labels = []
    values = []
    colors = []
    for r in rates:
        if r["resolution_rate"] is not None:
            labels.append(r["period"].split("(")[0].strip())
            values.append(r["resolution_rate"] * 100)
            if "Blue Book" in r["period"]:
                colors.append(COLORS[0])
            elif "Preliminary" in r["period"]:
                colors.append(COLORS[1])
            elif "2022" in r["period"]:
                colors.append(COLORS[2])
            else:
                colors.append(COLORS[3])

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor="black", linewidth=0.5)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Resolution Rate (%)", fontsize=12)
    ax.set_title("UAP Case Resolution Rates Across Programs and Periods", fontsize=13)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=10, fontweight="bold")

    ax.set_xlim(0, 110)
    ax.invert_yaxis()

    # Add annotation about data insufficiency
    ax.annotate(
        "AARO's low rate driven by\ndata insufficiency (58.7%\nof cases lack data),\nnot anomalous content",
        xy=(17.7, 3), xytext=(55, 2.5),
        fontsize=9, ha="center",
        arrowprops=dict(arrowstyle="->", color="gray"),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"),
    )

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "resolution_rates.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: resolution_rates.png")


def plot_case_disposition():
    """Plot 2: FY2024 case disposition breakdown (feature importance equivalent)."""
    fy24 = extract_fy2024_figures()

    categories = [
        "Resolved\n(118 formal)",
        "Pending Closure\n(174)",
        "Recommended\nClosure (243)",
        "Active Archive\n(444 - data insufficient)",
        "Merit IC/S&T\nAnalysis (21)",
    ]
    # Note: These sum to 757+243 but the 243 is from a different count.
    # The 757 new breaks down as: 49 resolved + 243 recommended + 21 IC + 444 archive = 757
    # Plus 118-49=69 resolved from prior periods, and 174 pending from prior
    # For the FY2024 intake of 757:
    values = [49, 243, 21, 444]
    labels = [
        f"Resolved During Period\n(49, {49/757*100:.1f}%)",
        f"Recommended Closure\n(243, {243/757*100:.1f}%)",
        f"Merit IC/S&T Analysis\n(21, {21/757*100:.1f}%)",
        f"Active Archive\n(444, {444/757*100:.1f}%)",
    ]
    colors_pie = [COLORS[2], COLORS[5], COLORS[1], COLORS[6]]

    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors_pie,
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=90, textprops={"fontsize": 10},
        pctdistance=0.75,
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontweight("bold")

    ax.set_title(
        "AARO FY2024 Case Disposition (757 new reports)\n"
        "All resolved/recommended-closure cases are prosaic",
        fontsize=12,
    )

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "case_disposition.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: case_disposition.png")


def plot_cumulative_trend():
    """Plot 3: Cumulative UAP reports over time."""
    # Timeline data points
    dates = ["Jun 2021\n(ODNI\nPrelim)", "Aug 2022\n(ODNI\n2022)", "Apr 2023\n(AARO\nFY2023)", "Oct 2024\n(AARO\nFY2024)"]
    cumulative = [144, 510, 801, 1652]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(len(dates)), cumulative, "o-", color=COLORS[0], linewidth=2.5, markersize=10)

    for i, (d, c) in enumerate(zip(dates, cumulative)):
        ax.annotate(f"{c:,}", (i, c), textcoords="offset points",
                    xytext=(0, 15), ha="center", fontsize=12, fontweight="bold")

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, fontsize=9)
    ax.set_ylabel("Cumulative UAP Reports", fontsize=12)
    ax.set_title("Cumulative UAP Reports to AARO/UAPTF Over Time", fontsize=13)
    ax.set_ylim(0, 2000)

    # Add resolution overlay
    resolved_dates = [0, 1, 3]  # indices where we have resolution data
    resolved_counts = [1, 195, 292]
    ax.bar([d - 0.15 for d in resolved_dates], resolved_counts, width=0.3,
           color=COLORS[2], alpha=0.7, label="Resolved/Characterized")

    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "cumulative_trend.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: cumulative_trend.png")


def plot_bayesian_sensitivity():
    """Plot 4: Bayesian posterior sensitivity to prior."""
    priors = np.linspace(0.01, 0.25, 50)
    p_unresolved_prosaic = 444 / 757

    posteriors = []
    for p in priors:
        p_unresolved = 1.0 * p + p_unresolved_prosaic * (1 - p)
        post = (1.0 * p) / p_unresolved
        posteriors.append(post)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(priors * 100, np.array(posteriors) * 100, "-", color=COLORS[0], linewidth=2.5)
    ax.plot([0, 25], [0, 25], "--", color="gray", linewidth=1, label="No-update line (posterior = prior)")

    # Mark key priors
    key_priors = [(0.05, "Blue Book\n5%"), (0.114, "Hendry\n11.4%"), (0.035, "GEIPAN\n3.5%")]
    for kp, label in key_priors:
        p_unr = 1.0 * kp + p_unresolved_prosaic * (1 - kp)
        post = (1.0 * kp) / p_unr
        ax.plot(kp * 100, post * 100, "o", color=COLORS[1], markersize=8, zorder=5)
        ax.annotate(label, (kp * 100, post * 100),
                    textcoords="offset points", xytext=(15, -5), fontsize=9)

    ax.set_xlabel("Prior P(anomalous) (%)", fontsize=12)
    ax.set_ylabel("Posterior P(anomalous | unresolved) (%)", fontsize=12)
    ax.set_title("Bayesian Posterior: How Prior Belief Affects Anomaly Assessment\n"
                 "For an unresolved AARO case", fontsize=12)
    ax.legend(fontsize=10)
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 40)

    ax.annotate(
        "Update is modest because\n58.7% of prosaic cases\nalso go unresolved\n(data insufficiency)",
        xy=(15, 25), fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"),
    )

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "bayesian_sensitivity.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: bayesian_sensitivity.png")


def plot_base_rate_comparison():
    """Plot 5: Base-rate comparison across programs."""
    programs = [
        "Blue Book\n(1947-69)",
        "Hendry\n(1979)",
        "GEIPAN\n(ongoing)",
        "AARO FY2024\n(exc. archive)",
        "AARO FY2024\n(overall)",
    ]
    identified = [94.4, 88.6, 96.5, 24.2, 17.7]
    unidentified = [5.6, 11.4, 3.5, 75.8, 82.3]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(programs))
    width = 0.6

    ax.bar(x, identified, width, color=COLORS[2], label="Identified / Resolved", edgecolor="black", linewidth=0.5)
    ax.bar(x, unidentified, width, bottom=identified, color=COLORS[1], label="Unidentified / Unresolved", edgecolor="black", linewidth=0.5)

    for i, (id_val, uid_val) in enumerate(zip(identified, unidentified)):
        ax.text(i, id_val / 2, f"{id_val:.1f}%", ha="center", va="center", fontsize=10, fontweight="bold", color="white")

    ax.set_xticks(x)
    ax.set_xticklabels(programs, fontsize=10)
    ax.set_ylabel("Percentage of Cases (%)", fontsize=12)
    ax.set_title("Case Resolution Rates Across UAP Investigation Programs", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 105)

    ax.annotate(
        "AARO's low resolution rate\nreflects data insufficiency,\nnot higher anomaly rate.\n"
        "100% of resolved cases\nare prosaic.",
        xy=(3.5, 50), fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"),
    )

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "base_rate_comparison.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: base_rate_comparison.png")


def plot_backlog_growth():
    """Plot 6: Backlog growth projection."""
    months = np.arange(0, 37)  # 3 years projection
    intake_rate = 58.2
    resolution_rate = 22.5
    initial_backlog = 1360

    backlog = initial_backlog + (intake_rate - resolution_rate) * months

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(months, backlog, alpha=0.3, color=COLORS[1])
    ax.plot(months, backlog, "-", color=COLORS[1], linewidth=2.5, label="Projected backlog")
    ax.axhline(y=initial_backlog, color="gray", linestyle="--", linewidth=1, label=f"Current backlog ({initial_backlog:,})")

    ax.set_xlabel("Months from Oct 2024", fontsize=12)
    ax.set_ylabel("Open Cases", fontsize=12)
    ax.set_title("AARO Case Backlog Projection\n"
                 f"Intake: {intake_rate}/month | Resolution: {resolution_rate}/month | Net accumulation: {intake_rate-resolution_rate:.1f}/month",
                 fontsize=12)
    ax.legend(fontsize=10)

    # Mark key points
    for m in [12, 24, 36]:
        val = initial_backlog + (intake_rate - resolution_rate) * m
        ax.plot(m, val, "o", color=COLORS[0], markersize=6)
        ax.annotate(f"{val:,.0f}", (m, val), textcoords="offset points",
                    xytext=(10, 5), fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "backlog_growth.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: backlog_growth.png")


if __name__ == "__main__":
    print("Generating plots for AARO Case Resolution Analysis...\n")
    plot_resolution_rates()
    plot_case_disposition()
    plot_cumulative_trend()
    plot_bayesian_sensitivity()
    plot_base_rate_comparison()
    plot_backlog_growth()
    print(f"\nAll plots saved to {PLOTS_DIR}/")
