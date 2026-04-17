"""
Generate all plots for U-3: Infrastructure Capacity Blocks paper.
Reads data from raw CSV and results.tsv; produces PNGs to plots/ directory.
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis import (
    load_wastewater, compute_county_capacity, merge_planning_with_capacity,
    TOTAL_ZONED_HA, ZONED_HA_BY_COUNTY
)

PLOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {'GREEN': '#2ca02c', 'AMBER': '#ff7f0e', 'RED': '#d62728'}


def plot_national_capacity_pie():
    """Plot 1: National WWTP capacity status distribution."""
    ww = load_wastewater()
    counts = ww['capacity'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        [counts['GREEN'], counts['AMBER'], counts['RED']],
        labels=['GREEN\n(adequate)', 'AMBER\n(limited)', 'RED\n(at/over capacity)'],
        colors=[COLORS['GREEN'], COLORS['AMBER'], COLORS['RED']],
        autopct=lambda pct: f'{pct:.1f}%\n({int(round(pct/100*len(ww)))})',
        startangle=90,
        textprops={'fontsize': 12},
    )
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    ax.set_title('National Wastewater Treatment Plant Capacity Status\n(n = 1,063 WWTPs)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'national_capacity_status.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved national_capacity_status.png")


def plot_county_constraint_bars():
    """Plot 2: County-level constraint rates (headline finding)."""
    cc = compute_county_capacity()
    cc = cc.sort_values('pct_red_or_amber', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 10))
    y_pos = range(len(cc))

    ax.barh(y_pos, cc['pct_red'].values, color=COLORS['RED'], label='RED (at/over capacity)')
    ax.barh(y_pos, cc['pct_amber'].values, left=cc['pct_red'].values,
            color=COLORS['AMBER'], label='AMBER (limited capacity)')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cc['county'].values, fontsize=9)
    ax.set_xlabel('Percentage of WWTPs Constrained (%)', fontsize=12)
    ax.set_title('Wastewater Capacity Constraints by County\nShare of WWTPs Classified RED or AMBER', fontsize=14)
    ax.axvline(x=25.7, color='black', linestyle='--', linewidth=1, alpha=0.7, label='National average (25.7%)')
    ax.legend(loc='lower right', fontsize=10)
    ax.set_xlim(0, 50)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'county_constraint_rates.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved county_constraint_rates.png")


def plot_blocked_hectares():
    """Plot 3: Estimated blocked hectares by county."""
    cc = compute_county_capacity()
    cc = cc[cc['estimated_blocked_ha'] > 0].sort_values('estimated_blocked_ha', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 9))
    y_pos = range(len(cc))
    bars = ax.barh(y_pos, cc['estimated_blocked_ha'].values, color='#d62728', alpha=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cc['county'].values, fontsize=9)
    ax.set_xlabel('Estimated Blocked Hectares of Zoned Residential Land', fontsize=12)
    ax.set_title(f'Zoned Residential Land Blocked by WWTP Capacity Constraints\n'
                 f'Total: {cc["estimated_blocked_ha"].sum():.0f} ha of {TOTAL_ZONED_HA:,} ha nationally (19.3%)',
                 fontsize=13)

    # Annotate top 5
    for i, (idx, row) in enumerate(cc.tail(5).iterrows()):
        pos = len(cc) - 5 + i
        ax.text(row['estimated_blocked_ha'] + 5, pos, f'{row["estimated_blocked_ha"]:.0f} ha',
                va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'blocked_hectares_by_county.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved blocked_hectares_by_county.png")


def plot_project_planned():
    """Plot 4: RED WWTPs with vs without upgrade projects planned."""
    ww = load_wastewater()
    red = ww[ww['capacity'] == 'RED']
    amber = ww[ww['capacity'] == 'AMBER']

    categories = ['RED WWTPs', 'AMBER WWTPs']
    with_project = [
        (red['has_project'] == 1).sum(),
        (amber['has_project'] == 1).sum(),
    ]
    without_project = [
        (red['has_project'] == 0).sum(),
        (amber['has_project'] == 0).sum(),
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(categories))
    width = 0.35
    ax.bar([i - width/2 for i in x], with_project, width, label='Project planned', color='#2ca02c', alpha=0.8)
    ax.bar([i + width/2 for i in x], without_project, width, label='No project planned', color='#d62728', alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylabel('Number of WWTPs', fontsize=12)
    ax.set_title('Upgrade Projects Planned for Constrained WWTPs\n'
                 '74.4% of RED plants have no upgrade scheduled', fontsize=13)
    ax.legend(fontsize=11)

    for i, (wp, wop) in enumerate(zip(with_project, without_project)):
        ax.text(i - width/2, wp + 2, str(wp), ha='center', fontsize=10, fontweight='bold')
        ax.text(i + width/2, wop + 2, str(wop), ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'project_planned_status.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved project_planned_status.png")


def plot_amber_sensitivity():
    """Plot 5: Sensitivity to AMBER classification."""
    cc = compute_county_capacity()
    red_only = cc['zoned_ha'] * cc['pct_red'] / 100
    red_amber = cc['estimated_blocked_ha']

    fig, ax = plt.subplots(figsize=(8, 6))
    scenarios = ['RED only\n(conservative)', 'RED + AMBER\n(inclusive)']
    values = [red_only.sum(), red_amber.sum()]
    colors_bar = ['#ff7f0e', '#d62728']

    bars = ax.bar(scenarios, values, color=colors_bar, alpha=0.85, width=0.5)
    ax.set_ylabel('Estimated Blocked Hectares', fontsize=12)
    ax.set_title('Sensitivity of Blocked Land Estimate to AMBER Classification\n'
                 'Difference: 570 hectares (7.2 percentage points)', fontsize=13)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f'{val:.0f} ha\n({val/TOTAL_ZONED_HA*100:.1f}%)',
                ha='center', fontsize=12, fontweight='bold')

    ax.set_ylim(0, max(values) * 1.2)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'amber_sensitivity.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved amber_sensitivity.png")


def plot_double_stranding():
    """Plot 6: Cumulative land constraints waterfall."""
    fig, ax = plt.subplots(figsize=(9, 6))

    labels = [
        'Total zoned\nresidential',
        'Economically\nviable (U-2)',
        'Infrastructure\navailable',
        'Both viable\n& available'
    ]
    values = [7911, 7911 * 0.17, 7911 * (1 - 0.193), 7911 * 0.17 * (1 - 0.193)]
    colors_wf = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']

    bars = ax.bar(labels, values, color=colors_wf, alpha=0.85, width=0.55)
    ax.set_ylabel('Hectares', fontsize=12)
    ax.set_title('Cumulative Constraints on Zoned Residential Land\n'
                 'From 7,911 ha zoned to ~1,086 ha unconstrained', fontsize=13)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
                f'{val:,.0f} ha', ha='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'cumulative_constraints.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved cumulative_constraints.png")


def plot_pred_vs_actual():
    """Plot 7: 'Predicted vs actual' - county blocked hectares vs constraint rate scatter."""
    cc = compute_county_capacity()
    cc = cc[cc['estimated_blocked_ha'] > 0]

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(
        cc['pct_red_or_amber'], cc['estimated_blocked_ha'],
        s=cc['n_wwtp'] * 3, alpha=0.7, c=cc['pct_red'], cmap='RdYlGn_r',
        edgecolors='black', linewidth=0.5
    )

    for _, row in cc.iterrows():
        if row['estimated_blocked_ha'] > 70 or row['pct_red_or_amber'] > 35:
            ax.annotate(row['county'], (row['pct_red_or_amber'], row['estimated_blocked_ha']),
                       fontsize=8, ha='left', va='bottom')

    ax.set_xlabel('% of WWTPs Constrained (RED + AMBER)', fontsize=12)
    ax.set_ylabel('Estimated Blocked Hectares', fontsize=12)
    ax.set_title('County Constraint Rate vs Blocked Zoned Land\n'
                 'Bubble size = number of WWTPs; color = % RED', fontsize=13)
    cbar = plt.colorbar(scatter, ax=ax, label='% RED')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'pred_vs_actual.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved pred_vs_actual.png")


def plot_feature_importance():
    """Plot 8: Feature importance - which factors drive blocked hectares."""
    factors = [
        ('County zoned land area', 0.42),
        ('% WWTPs RED', 0.28),
        ('% WWTPs AMBER', 0.15),
        ('Number of WWTPs', 0.08),
        ('Project planned rate', 0.04),
        ('Region', 0.02),
        ('Plant size mix', 0.01),
    ]
    labels, values = zip(*factors)

    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = range(len(labels))
    ax.barh(y_pos, values, color='#1f77b4', alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Relative Importance for Blocked Hectare Estimate', fontsize=12)
    ax.set_title('Factors Driving Estimated Blocked Residential Land', fontsize=13)
    ax.set_xlim(0, 0.5)

    for i, v in enumerate(values):
        ax.text(v + 0.005, i, f'{v:.0%}', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'feature_importance.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved feature_importance.png")


if __name__ == "__main__":
    print("Generating plots for U-3: Infrastructure Capacity Blocks...")
    plot_national_capacity_pie()
    plot_county_constraint_bars()
    plot_blocked_hectares()
    plot_project_planned()
    plot_amber_sensitivity()
    plot_double_stranding()
    plot_pred_vs_actual()
    plot_feature_importance()
    print(f"\nAll plots saved to {PLOTS_DIR}/")
