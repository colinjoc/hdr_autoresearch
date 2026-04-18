"""
Generate all plots for the housing-lever interaction paper.
Reads results.tsv and model outputs. Produces PNGs at 300 DPI.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
import os

plt.style.use('seaborn-v0_8-whitegrid')
PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

from feedback_model import (
    run_feedback_loop, BASELINE, LEVER_SETTINGS, LEVER_NAMES, describe_levers,
    compute_cost_reduction, run_monte_carlo
)


def soft_ceiling_model(gross, base_ceiling=35000, wf_mult=1.0, congestion=0.02):
    effective_ceiling = base_ceiling * wf_mult
    if gross <= effective_ceiling:
        return gross
    excess = gross - effective_ceiling
    delivered_excess = excess / (1 + congestion * excess / effective_ceiling * 10)
    return effective_ceiling + delivered_excess


# ====== Plot 1: Individual lever effects (horizontal bar chart) ======
print("Plot 1: Individual lever effects...")
max_levers = {
    "duration_reduction": ("Duration -50%", {"duration_reduction": 0.50}),
    "modular_reduction": ("Modular -30%", {"modular_reduction": 0.30}),
    "vat_rate": ("VAT 0%", {"vat_rate": 0.0}),
    "part_v_rate": ("Part V abolished", {"part_v_rate": 0.0}),
    "dev_contribs_fraction": ("Dev contribs zeroed", {"dev_contribs_fraction": 0.0}),
    "bcar_fraction": ("BCAR abolished", {"bcar_fraction": 0.0}),
    "land_cost_multiplier": ("Land CPO agric.", {"land_cost_multiplier": 0.1}),
    "finance_rate_new": ("Finance 3%", {"finance_rate_new": 0.03}),
    "developer_margin_new": ("Margin 6%", {"developer_margin_new": 0.06}),
    "workforce_multiplier": ("Workforce +50%", {"workforce_multiplier": 1.5}),
}

names = []
cost_reds = []
gross_deltas = []
for key, (label, levers) in max_levers.items():
    r = run_feedback_loop(levers)
    names.append(label)
    cost_reds.append(r["cost_reduction"] * 100)
    gross_deltas.append(r["gross_completions_uncapped"] - 35000)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Cost reduction
y_pos = np.arange(len(names))
colors = ['#e74c3c' if cr > 10 else '#3498db' if cr > 3 else '#95a5a6' for cr in cost_reds]
ax1.barh(y_pos, cost_reds, color=colors, edgecolor='white')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(names)
ax1.set_xlabel('Cost reduction (%)')
ax1.set_title('Cost Reduction per Lever (max setting)')
ax1.invert_yaxis()
for i, v in enumerate(cost_reds):
    ax1.text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=9)

# Gross completions delta
colors2 = ['#e74c3c' if gd > 30000 else '#3498db' if gd > 10000 else '#95a5a6' for gd in gross_deltas]
ax2.barh(y_pos, [gd/1000 for gd in gross_deltas], color=colors2, edgecolor='white')
ax2.set_yticks(y_pos)
ax2.set_yticklabels(names)
ax2.set_xlabel('Additional gross completions (thousands)')
ax2.set_title('Gross Completions Increase per Lever')
ax2.invert_yaxis()
ax2.axvline(x=15.5, color='red', linestyle='--', alpha=0.5, label='Target gap (15.5k)')
ax2.legend(fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'feature_importance.png'), dpi=300, bbox_inches='tight')
plt.close()


# ====== Plot 2: Ceiling dynamics — the headline finding ======
print("Plot 2: Headline finding - ceiling dynamics...")
fig, ax = plt.subplots(figsize=(10, 7))

cost_red_range = np.linspace(0, 0.70, 100)
gross = [35000 * (1 + 9.1 * cr) for cr in cost_red_range]

# Plot gross completions
ax.plot(cost_red_range * 100, [g/1000 for g in gross], 'b-', linewidth=2, label='Gross completions (uncapped)')

# Plot various ceilings
for wf, color, style in [(1.0, 'red', '-'), (1.2, 'orange', '--'), (1.5, 'green', '-.')]:
    ceiling = 35000 * wf
    ax.axhline(y=ceiling/1000, color=color, linestyle=style, linewidth=1.5,
               label=f'Capacity ceiling (×{wf}): {ceiling:,.0f}')

# Soft ceiling curves
for wf, color in [(1.0, 'red'), (1.5, 'green')]:
    soft_vals = [soft_ceiling_model(g, wf_mult=wf)/1000 for g in gross]
    ax.plot(cost_red_range * 100, soft_vals, color=color, linewidth=2, alpha=0.5,
            linestyle=':', label=f'Soft ceiling (×{wf})')

# HFA target
ax.axhline(y=50.5, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='HFA target: 50,500')

# Mark key levers on x-axis
key_levers = [
    (2.8, "Duration\n-25%"),
    (5.3, "Modular\n-10%"),
    (11.9, "VAT 0%"),
    (15.9, "Modular\n-30%"),
    (16.2, "Land\nCPO"),
]
for cr, label in key_levers:
    ax.annotate(label, xy=(cr, 0), fontsize=7, ha='center', va='top',
                rotation=0, color='gray')

ax.set_xlabel('Total cost reduction (%)', fontsize=12)
ax.set_ylabel('Completions (thousands/yr)', fontsize=12)
ax.set_title('The Capacity Ceiling Dominates Housing Output:\nCost Reduction Generates Demand, Workforce Enables Supply', fontsize=13)
ax.legend(loc='upper left', fontsize=8)
ax.set_xlim(0, 72)
ax.set_ylim(0, 280)

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'headline_finding.png'), dpi=300, bbox_inches='tight')
plt.close()


# ====== Plot 3: Pairwise interaction matrix heatmap ======
print("Plot 3: Interaction matrix heatmap...")

lever_names_ordered = list(LEVER_SETTINGS.keys())
max_settings = {
    "duration_reduction": 0.50, "modular_reduction": 0.30, "vat_rate": 0.0,
    "part_v_rate": 0.0, "dev_contribs_fraction": 0.0, "bcar_fraction": 0.0,
    "land_cost_multiplier": 0.1, "finance_rate_new": 0.03, "developer_margin_new": 0.06,
    "workforce_multiplier": 1.5,
}

n = len(lever_names_ordered)
matrix = np.zeros((n, n))
base_soft = soft_ceiling_model(35000)

for i, la in enumerate(lever_names_ordered):
    for j, lb in enumerate(lever_names_ordered):
        if i == j:
            matrix[i, j] = 0
            continue
        if j < i:
            matrix[i, j] = matrix[j, i]
            continue
        la_d = {la: max_settings[la]}
        lb_d = {lb: max_settings[lb]}
        lab_d = {la: max_settings[la], lb: max_settings[lb]}

        r_a = run_feedback_loop(la_d)
        r_b = run_feedback_loop(lb_d)
        r_ab = run_feedback_loop(lab_d)

        wf_a = la_d.get("workforce_multiplier", 1.0)
        wf_b = lb_d.get("workforce_multiplier", 1.0)
        wf_ab = lab_d.get("workforce_multiplier", 1.0)

        s_a = soft_ceiling_model(r_a["gross_completions_uncapped"], wf_mult=wf_a)
        s_b = soft_ceiling_model(r_b["gross_completions_uncapped"], wf_mult=wf_b)
        s_ab = soft_ceiling_model(r_ab["gross_completions_uncapped"], wf_mult=wf_ab)

        matrix[i, j] = (s_ab - (s_a + s_b - base_soft)) / 1000  # thousands
        matrix[j, i] = matrix[i, j]

short_names = ["Duration", "Modular", "VAT", "Part V", "Dev\nContribs", "BCAR",
               "Land\nCPO", "Finance", "Dev\nMargin", "Work-\nforce"]

fig, ax = plt.subplots(figsize=(10, 8))
vmax = max(abs(matrix.max()), abs(matrix.min()))
im = ax.imshow(matrix, cmap='RdBu', vmin=-vmax, vmax=vmax, aspect='auto')
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(short_names, fontsize=8, rotation=45, ha='right')
ax.set_yticklabels(short_names, fontsize=8)
ax.set_title('Pairwise Interaction Matrix (thousands of completions)\nBlue = Synergy, Red = Redundancy', fontsize=12)

# Add text annotations
for i in range(n):
    for j in range(n):
        if i != j:
            text = f'{matrix[i,j]:+.1f}k'
            color = 'white' if abs(matrix[i,j]) > vmax * 0.6 else 'black'
            ax.text(j, i, text, ha='center', va='center', fontsize=7, color=color)

plt.colorbar(im, ax=ax, label='Interaction (thousands)', shrink=0.8)
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'interaction_matrix.png'), dpi=300, bbox_inches='tight')
plt.close()


# ====== Plot 4: Package comparison ======
print("Plot 4: Package comparison...")
packages = [
    ("Baseline", {}, "gray"),
    ("Feasible", {"duration_reduction":0.25, "modular_reduction":0.10, "vat_rate":0.09,
                  "part_v_rate":0.10, "dev_contribs_fraction":0.5}, "#3498db"),
    ("Feasible\n+WF 1.2", {"duration_reduction":0.25, "modular_reduction":0.10, "vat_rate":0.09,
                            "part_v_rate":0.10, "dev_contribs_fraction":0.5, "workforce_multiplier":1.2}, "#2980b9"),
    ("Radical\n+WF 1.5", {"duration_reduction":0.33, "modular_reduction":0.20, "vat_rate":0.0,
                           "part_v_rate":0.0, "dev_contribs_fraction":0.0, "land_cost_multiplier":0.1,
                           "workforce_multiplier":1.5}, "#e67e22"),
    ("Everything", {"duration_reduction":0.50, "modular_reduction":0.30, "vat_rate":0.0,
                     "part_v_rate":0.0, "dev_contribs_fraction":0.0, "bcar_fraction":0.0,
                     "land_cost_multiplier":0.1, "finance_rate_new":0.03, "developer_margin_new":0.06,
                     "workforce_multiplier":1.5}, "#e74c3c"),
]

fig, ax = plt.subplots(figsize=(10, 6))
x_pos = np.arange(len(packages))
bar_width = 0.3

gross_vals = []
soft_vals = []
hard_vals = []
colors = []
names_pkg = []

for name, levers, color in packages:
    r = run_feedback_loop(levers)
    wf = levers.get("workforce_multiplier", 1.0)
    soft = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)
    gross_vals.append(r["gross_completions_uncapped"] / 1000)
    soft_vals.append(soft / 1000)
    hard_vals.append(r["completions"] / 1000)
    colors.append(color)
    names_pkg.append(name)

ax.bar(x_pos - bar_width, gross_vals, bar_width, label='Gross (uncapped)', color=colors, alpha=0.3, edgecolor='gray')
ax.bar(x_pos, soft_vals, bar_width, label='Soft ceiling', color=colors, alpha=0.7, edgecolor='gray')
ax.bar(x_pos + bar_width, hard_vals, bar_width, label='Hard ceiling', color=colors, edgecolor='gray')

ax.axhline(y=50.5, color='purple', linestyle='--', linewidth=1.5, alpha=0.7, label='HFA target: 50.5k')
ax.axhline(y=35.0, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='Current: 35k')

ax.set_xticks(x_pos)
ax.set_xticklabels(names_pkg, fontsize=9)
ax.set_ylabel('Completions (thousands/yr)', fontsize=11)
ax.set_title('Policy Package Comparison: Gross vs Constrained Completions', fontsize=12)
ax.legend(fontsize=8, loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'package_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()


# ====== Plot 5: Monte Carlo distribution ======
print("Plot 5: Monte Carlo distributions...")

def mc_soft_dist(levers, n=10000, seed=42):
    rng = np.random.RandomState(seed)
    results = []
    for _ in range(n):
        by = np.clip(rng.normal(0.596, 0.023), 0.40, 0.80)
        ar = np.clip(rng.normal(0.68, 0.03), 0.50, 0.90)
        ve = np.clip(rng.normal(0.91, 0.05), 0.50, 1.0)
        r = run_feedback_loop(levers, viability_elasticity=ve, build_yield=by, approval_rate=ar)
        wf = levers.get("workforce_multiplier", 1.0)
        s = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)
        results.append(s / 1000)
    return results

fig, ax = plt.subplots(figsize=(10, 6))

for name, levers, color in [
    ("Feasible+WF1.2", {"duration_reduction":0.25, "modular_reduction":0.10, "vat_rate":0.09,
                         "part_v_rate":0.10, "dev_contribs_fraction":0.5, "workforce_multiplier":1.2}, "#3498db"),
    ("Radical+WF1.5", {"duration_reduction":0.33, "modular_reduction":0.20, "vat_rate":0.0,
                        "part_v_rate":0.0, "dev_contribs_fraction":0.0, "land_cost_multiplier":0.1,
                        "workforce_multiplier":1.5}, "#e67e22"),
    ("Everything", {"duration_reduction":0.50, "modular_reduction":0.30, "vat_rate":0.0,
                     "part_v_rate":0.0, "dev_contribs_fraction":0.0, "bcar_fraction":0.0,
                     "land_cost_multiplier":0.1, "finance_rate_new":0.03, "developer_margin_new":0.06,
                     "workforce_multiplier":1.5}, "#e74c3c"),
]:
    mc = mc_soft_dist(levers)
    ax.hist(mc, bins=50, alpha=0.5, color=color, label=f'{name} (mean={np.mean(mc):.1f}k)')

ax.axvline(x=50.5, color='purple', linestyle='--', linewidth=2, label='HFA target: 50.5k')
ax.axvline(x=35.0, color='gray', linestyle=':', linewidth=1.5, label='Current: 35k')
ax.set_xlabel('Completions (thousands/yr)', fontsize=11)
ax.set_ylabel('Frequency (10,000 MC draws)', fontsize=11)
ax.set_title('Monte Carlo Uncertainty: Completion Distributions Under Policy Packages', fontsize=12)
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'monte_carlo.png'), dpi=300, bbox_inches='tight')
plt.close()


# ====== Plot 6: Pareto frontier ======
print("Plot 6: Pareto frontier...")
from itertools import combinations

lever_list = list(LEVER_SETTINGS.keys())
lever_costs_max = {
    "duration_reduction": 0, "modular_reduction": 300e6, "vat_rate": 1400e6,
    "part_v_rate": 400e6, "dev_contribs_fraction": 300e6, "bcar_fraction": 40e6,
    "land_cost_multiplier": 1500e6, "finance_rate_new": 500e6,
    "developer_margin_new": 0, "workforce_multiplier": 600e6,
}
max_settings_all = {
    "duration_reduction": 0.50, "modular_reduction": 0.30, "vat_rate": 0.0,
    "part_v_rate": 0.0, "dev_contribs_fraction": 0.0, "bcar_fraction": 0.0,
    "land_cost_multiplier": 0.1, "finance_rate_new": 0.03, "developer_margin_new": 0.06,
    "workforce_multiplier": 1.5,
}

pareto_all = []
for combo_keys in combinations(lever_list, 3):
    levers = {k: max_settings_all[k] for k in combo_keys}
    cost = sum(lever_costs_max[k] for k in combo_keys)
    r = run_feedback_loop(levers)
    wf = levers.get("workforce_multiplier", 1.0)
    soft = soft_ceiling_model(r["gross_completions_uncapped"], wf_mult=wf)
    pareto_all.append((combo_keys, soft/1000, cost/1e6))

fig, ax = plt.subplots(figsize=(10, 7))

# All points
x_all = [p[2] for p in pareto_all]
y_all = [p[1] for p in pareto_all]
ax.scatter(x_all, y_all, alpha=0.3, s=30, color='gray', label='All 3-lever combos')

# Pareto frontier
pareto_sorted = sorted(pareto_all, key=lambda x: x[1], reverse=True)
frontier = []
min_cost = float('inf')
for p in pareto_sorted:
    if p[2] < min_cost:
        frontier.append(p)
        min_cost = p[2]

x_f = [p[2] for p in frontier]
y_f = [p[1] for p in frontier]
ax.scatter(x_f, y_f, color='red', s=100, zorder=5, label='Pareto frontier')
ax.plot(x_f, y_f, 'r-', alpha=0.5)

# Label frontier points
for keys, comp, cost in frontier:
    short = "+".join([k[:3].upper() for k in keys])
    ax.annotate(short, (cost, comp), fontsize=7, ha='left', va='bottom',
                xytext=(5, 5), textcoords='offset points')

ax.axhline(y=50.5, color='purple', linestyle='--', alpha=0.5, label='HFA target')
ax.set_xlabel('Fiscal cost (EUR millions/yr)', fontsize=11)
ax.set_ylabel('Completions (thousands/yr, soft ceiling)', fontsize=11)
ax.set_title('Pareto Frontier: 3-Lever Combinations\n(Completions vs Fiscal Cost)', fontsize=12)
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'pareto_frontier.png'), dpi=300, bbox_inches='tight')
plt.close()

print("\nAll plots saved to plots/")
print("Files:", os.listdir(PLOT_DIR))
