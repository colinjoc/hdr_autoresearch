#!/usr/bin/env python3
"""Generate plots for warp drive physics paper.

Produces:
  plots/energy_condition_matrix.png  - The "predicted vs actual" equivalent: EC evaluation matrix
  plots/exotic_matter_comparison.png - Feature importance equivalent: exotic matter by metric
  plots/headline_finding.png         - The subluminal boundary: what Fell-Heisenberg achieved
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")

# ============================================================
# Plot 1: Energy Condition Matrix (the "predicted vs actual" equivalent)
# ============================================================
metrics = [
    "Alcubierre\n(1994)",
    "Van Den Broeck\n(1999)",
    "Natario\n(2002)",
    "Krasnikov tube\n(1998)",
    "Morris-Thorne\n(1988)",
    "Lentz\n(2021)",
    "Bobrick-Martire\n(2021, super.)",
    "Fell-Heisenberg\n(2024, sub.)",
]

conditions = ["NEC", "WEC", "SEC", "DEC"]

# 1 = satisfied, 0 = violated
# Rows: metrics, Cols: conditions
matrix = np.array([
    [0, 0, 0, 0],  # Alcubierre
    [0, 0, 0, 0],  # Van Den Broeck
    [0, 0, 0, 0],  # Natario
    [0, 0, 0, 0],  # Krasnikov
    [0, 0, 0, 0],  # Morris-Thorne
    [0, 0, 0, 0],  # Lentz (refuted)
    [0, 0, 0, 0],  # Bobrick-Martire superluminal
    [1, 1, 1, 1],  # Fell-Heisenberg subluminal
])

fig, ax = plt.subplots(figsize=(8, 6))
cmap = plt.cm.RdYlGn
im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1)

ax.set_xticks(range(len(conditions)))
ax.set_xticklabels(conditions, fontsize=12, fontweight="bold")
ax.set_yticks(range(len(metrics)))
ax.set_yticklabels(metrics, fontsize=10)

for i in range(len(metrics)):
    for j in range(len(conditions)):
        label = "PASS" if matrix[i, j] == 1 else "FAIL"
        color = "white" if matrix[i, j] == 0 else "black"
        ax.text(j, i, label, ha="center", va="center", fontsize=10,
                fontweight="bold", color=color)

ax.set_title("Energy Condition Evaluation for Proposed Warp/FTL Metrics",
             fontsize=13, fontweight="bold", pad=15)
ax.set_xlabel("Energy Condition", fontsize=12)

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "energy_condition_matrix.png"),
            dpi=300, bbox_inches="tight")
plt.close()
print("Saved energy_condition_matrix.png")

# ============================================================
# Plot 2: Exotic Matter Comparison (feature importance equivalent)
# ============================================================
metric_names = [
    "Krasnikov\ntube (1 ly)",
    "Alcubierre\n(v=c, R=100m)",
    "Natario\n(v=c, R=100m)",
    "Van Den\nBroeck",
    "Morris-Thorne\n(r_0=1m)",
    "Alcubierre\n(v=0.1c)",
    "Fell-Heisenberg\n(positive E)",
    "Casimir\n(1 um)",
]

# log10 of exotic matter mass in kg (negative = exotic, positive = regular)
log_masses = [
    46,    # Krasnikov: ~10^46 kg
    30,    # Alcubierre v=c: ~10^30 kg
    30,    # Natario: ~10^30 kg
    28,    # Van Den Broeck: ~10^28 kg
    27,    # Morris-Thorne: ~10^27 kg
    28,    # Alcubierre v=0.1c: ~10^28 kg
    27.65, # Fell-Heisenberg: 4.49e27 kg (POSITIVE)
    -60,   # Casimir: ~10^{-60} relative
]

is_positive = [False, False, False, False, False, False, True, False]

colors = ["#d32f2f" if not p else "#388e3c" for p in is_positive]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(metric_names)), log_masses, color=colors, edgecolor="black", linewidth=0.5)

ax.set_yticks(range(len(metric_names)))
ax.set_yticklabels(metric_names, fontsize=10)
ax.set_xlabel("log$_{10}$(Mass / kg)", fontsize=12)
ax.set_title("Mass Requirements for Proposed Warp/FTL Metrics\n(Red = exotic/negative energy; Green = positive energy only)",
             fontsize=12, fontweight="bold")

# Reference lines
ax.axvline(x=np.log10(1.989e30), color="orange", linestyle="--", linewidth=1.5, label="Solar mass")
ax.axvline(x=np.log10(1.898e27), color="blue", linestyle="--", linewidth=1.5, label="Jupiter mass")
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "exotic_matter_comparison.png"),
            dpi=300, bbox_inches="tight")
plt.close()
print("Saved exotic_matter_comparison.png")

# ============================================================
# Plot 3: Headline Finding - The Subluminal Boundary
# ============================================================
v_over_c = np.linspace(0.001, 0.2, 200)

# Conceptual: momentum flux / energy density ratio
# For the Fell-Heisenberg geometry, this ratio scales roughly as (v/v_max)^2
# EC satisfied when ratio < 1
v_max_est = 0.10  # estimated EC boundary

ratio = (v_over_c / v_max_est) ** 2

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(v_over_c, ratio, "b-", linewidth=2.5, label="Momentum flux / Energy density")
ax.axhline(y=1.0, color="red", linestyle="--", linewidth=2, label="Energy condition threshold")
ax.fill_between(v_over_c, 0, ratio, where=(ratio <= 1),
                alpha=0.15, color="green", label="Energy conditions satisfied")
ax.fill_between(v_over_c, ratio, np.maximum(ratio, 1), where=(ratio > 1),
                alpha=0.15, color="red", label="Energy conditions violated")

# Mark the demonstrated solution
ax.plot(0.04, (0.04/v_max_est)**2, "go", markersize=12, zorder=5,
        label=f"Fell-Heisenberg 2024\n(v = 0.04c, all EC satisfied)")

# Mark the light speed boundary
ax.axvline(x=1.0, color="gray", linestyle=":", linewidth=1)

ax.set_xlabel("Warp velocity (v / c)", fontsize=13)
ax.set_ylabel("Momentum flux / Energy density ratio", fontsize=13)
ax.set_title("The Subluminal Boundary: Why Positive-Energy Warp\nCannot Reach the Speed of Light",
             fontsize=13, fontweight="bold")
ax.set_xlim(0, 0.2)
ax.set_ylim(0, 5)
ax.legend(fontsize=10, loc="upper left")

# Annotation
ax.annotate("Physical\nregime",
            xy=(0.03, 0.3), fontsize=14, fontweight="bold", color="green",
            ha="center")
ax.annotate("Unphysical\n(exotic matter\nrequired)",
            xy=(0.16, 3.0), fontsize=12, fontweight="bold", color="red",
            ha="center")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "headline_finding.png"),
            dpi=300, bbox_inches="tight")
plt.close()
print("Saved headline_finding.png")

print("\nAll plots generated successfully.")
