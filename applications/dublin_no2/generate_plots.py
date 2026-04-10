#!/usr/bin/env python3
"""Generate all publication-quality plots for the Dublin NO2 source attribution paper.

Produces 5 figures in plots/:
  1. pred_vs_actual.png    — model-predicted vs actual NO2 (monthly, all stations)
  2. feature_importance.png — source contribution breakdown by component
  3. headline_finding.png   — annual mean NO2 by station with WHO/EU guideline lines
  4. covid_validation.png   — COVID lockdown station-by-station NO2 change
  5. source_attribution.png — stacked bar showing traffic/heating/background per station

All data is REAL from EEA/EPA Ireland + Met Eireann.
"""
import sys
import os
from pathlib import Path

# Ensure project root is on path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# Use colourblind-safe palette
# Wong (2011) Nature Methods colourblind palette
CB_BLUE = '#0072B2'
CB_ORANGE = '#E69F00'
CB_GREEN = '#009E73'
CB_RED = '#D55E00'
CB_PURPLE = '#CC79A7'
CB_CYAN = '#56B4E9'
CB_YELLOW = '#F0E442'
CB_BLACK = '#000000'

STYLE = 'seaborn-v0_8-whitegrid'
DPI = 300
PLOTS_DIR = PROJECT_DIR / 'plots'


def _setup():
    """Create output directory and set global style."""
    PLOTS_DIR.mkdir(exist_ok=True)
    plt.style.use(STYLE)
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.dpi': DPI,
        'savefig.dpi': DPI,
        'savefig.bbox': 'tight',
    })


def plot_pred_vs_actual():
    """Plot 1: Model-predicted vs actual monthly NO2 for all key stations.

    The 'predicted' value is background + heating + traffic from the source
    attribution model. For a well-specified additive model, these should
    fall on the 1:1 line.
    """
    from evaluate import attribute_sources_monthly
    from data_loaders import KEY_STATIONS

    fig, ax = plt.subplots(figsize=(10, 8))

    all_measured = []
    all_predicted = []
    station_types = []

    type_colors = {
        'traffic': CB_RED,
        'background': CB_BLUE,
        'rural-remote': CB_GREEN,
        'rural-regional': CB_GREEN,
    }
    type_markers = {
        'traffic': 'o',
        'background': 's',
        'rural-remote': '^',
        'rural-regional': '^',
    }

    for code in KEY_STATIONS:
        name, stype, city = KEY_STATIONS[code]
        try:
            monthly = attribute_sources_monthly(station=code)
        except Exception:
            continue
        if len(monthly) == 0:
            continue

        predicted = monthly['background'] + monthly['heating'] + monthly['traffic']
        measured = monthly['measured']

        all_measured.extend(measured.tolist())
        all_predicted.extend(predicted.tolist())
        station_types.extend([stype] * len(measured))

    # Plot by type for legend
    types_plotted = set()
    for stype in ['traffic', 'background', 'rural-remote', 'rural-regional']:
        mask = [st == stype for st in station_types]
        m = np.array(all_measured)[mask]
        p = np.array(all_predicted)[mask]
        if len(m) == 0:
            continue
        label = stype.replace('-', ' ').title()
        if stype.startswith('rural'):
            if 'rural' in types_plotted:
                label = None
            else:
                label = 'Rural'
                types_plotted.add('rural')
        ax.scatter(m, p, c=type_colors.get(stype, CB_BLACK),
                   marker=type_markers.get(stype, 'o'),
                   alpha=0.4, s=18, label=label, edgecolors='none')
        types_plotted.add(stype)

    # 1:1 line
    lims = [0, max(max(all_measured), max(all_predicted)) * 1.05]
    ax.plot(lims, lims, '--', color='grey', linewidth=1, label='1:1 line')

    # Compute R-squared
    m_arr = np.array(all_measured)
    p_arr = np.array(all_predicted)
    valid = np.isfinite(m_arr) & np.isfinite(p_arr)
    corr = np.corrcoef(m_arr[valid], p_arr[valid])[0, 1]
    r2 = corr ** 2
    mae = np.mean(np.abs(m_arr[valid] - p_arr[valid]))

    ax.text(0.05, 0.92, f'$R^2$ = {r2:.3f}\nMAE = {mae:.1f} $\\mu$g/m$^3$',
            transform=ax.transAxes, fontsize=13,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('Measured monthly NO$_2$ ($\\mu$g/m$^3$)', fontsize=14)
    ax.set_ylabel('Model-attributed NO$_2$ ($\\mu$g/m$^3$)', fontsize=14)
    ax.set_title('Source Attribution Model: Predicted vs Measured NO$_2$', fontsize=16)
    ax.legend(loc='lower right', fontsize=12)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect('equal')

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / 'pred_vs_actual.png', bbox_inches='tight')
    plt.close(fig)
    print("  [1/5] pred_vs_actual.png")


def plot_feature_importance():
    """Plot 2: Source contribution breakdown showing traffic/heating/background
    dominance, analogous to feature importance in ML models.

    Shows mean annual contribution of each source across station types,
    highlighting that traffic timing and station identity (type) are the
    dominant 'features' determining NO2.
    """
    from evaluate import attribute_sources
    from data_loaders import KEY_STATIONS

    rows = []
    for code in KEY_STATIONS:
        name, stype, city = KEY_STATIONS[code]
        try:
            annual = attribute_sources(station=code)
        except Exception:
            continue
        # Use 2019 (pre-COVID, full year)
        yr = annual[annual['year'] == 2019]
        if len(yr) == 0:
            # fallback to any available year
            yr = annual.iloc[:1]
        row = yr.iloc[0]
        rows.append({
            'station': name,
            'type': stype,
            'traffic': row['traffic'],
            'heating': row['heating'],
            'background': row['background'],
        })

    rdf = pd.DataFrame(rows).sort_values('traffic', ascending=True)

    n_bars = len(rdf)
    fig, ax = plt.subplots(figsize=(10, max(6, n_bars * 0.5)))

    y = np.arange(len(rdf))
    bar_height = 0.6

    # Stacked horizontal bars
    ax.barh(y, rdf['background'], bar_height, label='Regional background',
            color=CB_GREEN, edgecolor='white', linewidth=0.5)
    ax.barh(y, rdf['heating'], bar_height, left=rdf['background'],
            label='Residential heating', color=CB_ORANGE, edgecolor='white', linewidth=0.5)
    ax.barh(y, rdf['traffic'], bar_height,
            left=rdf['background'].values + rdf['heating'].values,
            label='Road traffic', color=CB_RED, edgecolor='white', linewidth=0.5)

    # Station type markers
    for i, (_, row) in enumerate(rdf.iterrows()):
        stype = row['type']
        type_label = stype.replace('-', ' ').title()
        total = row['traffic'] + row['heating'] + row['background']
        pct = row['traffic'] / total * 100 if total > 0 else 0
        ax.text(total + 0.5, i, f'{pct:.0f}%', va='center', fontsize=10, color=CB_RED)

    ax.set_yticks(y)
    ax.set_yticklabels(rdf['station'])
    ax.set_xlabel('Annual mean NO$_2$ ($\\mu$g/m$^3$)', fontsize=14)
    ax.set_title('Source Attribution: Traffic Dominates Urban NO$_2$ (2019)', fontsize=16)
    ax.legend(loc='lower right', fontsize=12)

    # WHO and EU lines
    ax.axvline(x=10, color=CB_PURPLE, linestyle='--', linewidth=1.5,
               label='WHO guideline (10)')
    ax.axvline(x=40, color=CB_BLACK, linestyle=':', linewidth=1.5,
               label='EU limit (40)')
    # Re-draw legend with guideline lines
    ax.legend(loc='lower right', fontsize=12)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / 'feature_importance.png', bbox_inches='tight')
    plt.close(fig)
    print("  [2/5] feature_importance.png")


def plot_headline_finding():
    """Plot 3: Annual mean NO2 by station with WHO 10 ug/m3 and EU 40 ug/m3 lines.

    The headline finding: every urban station above WHO, Winetavern at 3-4x WHO.
    """
    from evaluate import who_exceedance_summary
    from data_loaders import WHO_ANNUAL, EU_ANNUAL

    summary = who_exceedance_summary()

    # Use 2019 data (best pre-COVID year with full coverage)
    s2019 = summary[summary['year'] == 2019].copy()
    if len(s2019) < 5:
        # Fallback: use the year with most stations
        year_counts = summary.groupby('year')['station'].count()
        best_year = year_counts.idxmax()
        s2019 = summary[summary['year'] == best_year].copy()

    s2019 = s2019.sort_values('annual_mean', ascending=True)

    n_bars = len(s2019)
    fig, ax = plt.subplots(figsize=(12, max(6, n_bars * 0.5)))

    y = np.arange(len(s2019))
    bar_height = 0.6

    # Colour by station type
    colors = []
    for _, row in s2019.iterrows():
        stype = row['station_type']
        if stype == 'traffic':
            colors.append(CB_RED)
        elif stype == 'background':
            colors.append(CB_BLUE)
        else:
            colors.append(CB_GREEN)

    bars = ax.barh(y, s2019['annual_mean'], bar_height, color=colors,
                   edgecolor='white', linewidth=0.5)

    # WHO line
    ax.axvline(x=WHO_ANNUAL, color=CB_PURPLE, linestyle='--', linewidth=2,
               label=f'WHO guideline ({WHO_ANNUAL} $\\mu$g/m$^3$)')
    # EU line
    ax.axvline(x=EU_ANNUAL, color=CB_BLACK, linestyle=':', linewidth=2,
               label=f'EU limit ({EU_ANNUAL} $\\mu$g/m$^3$)')

    # Annotate WHO exceedance ratio
    for i, (_, row) in enumerate(s2019.iterrows()):
        ratio = row['annual_mean'] / WHO_ANNUAL
        if ratio > 1:
            ax.text(row['annual_mean'] + 0.5, i, f'{ratio:.1f}x WHO',
                    va='center', fontsize=11, fontweight='bold',
                    color=CB_RED if ratio > 2 else CB_BLACK)

    ax.set_yticks(y)
    ax.set_yticklabels(s2019['station_name'])
    ax.set_xlabel('Annual mean NO$_2$ ($\\mu$g/m$^3$)', fontsize=14)
    ax.set_title('Dublin/Cork Annual NO$_2$ vs WHO and EU Guidelines (2019)', fontsize=16)

    # Custom legend for station types + guidelines
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_RED, label='Traffic station'),
        Patch(facecolor=CB_BLUE, label='Background station'),
        Patch(facecolor=CB_GREEN, label='Rural station'),
        plt.Line2D([0], [0], color=CB_PURPLE, linestyle='--', linewidth=2,
                   label=f'WHO guideline ({WHO_ANNUAL} $\\mu$g/m$^3$)'),
        plt.Line2D([0], [0], color=CB_BLACK, linestyle=':', linewidth=2,
                   label=f'EU limit ({EU_ANNUAL} $\\mu$g/m$^3$)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=12)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / 'headline_finding.png', bbox_inches='tight')
    plt.close(fig)
    print("  [3/5] headline_finding.png")


def plot_covid_validation():
    """Plot 4: COVID lockdown natural experiment — station-by-station NO2 change.

    Shows 2020 vs 2019 (Mar-Jun) NO2 at each station, with traffic stations
    dropping most, validating the source attribution model.
    """
    from evaluate import covid_lockdown_analysis

    covid = covid_lockdown_analysis()
    if len(covid) == 0:
        print("  [4/5] SKIPPED — no COVID data")
        return

    covid = covid.sort_values('change_pct', ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={'width_ratios': [1.2, 1]})

    # Left panel: paired bar chart (2019 vs 2020)
    y = np.arange(len(covid))
    bar_height = 0.35

    ax1.barh(y - bar_height/2, covid['no2_2019'], bar_height,
             label='Mar-Jun 2019', color=CB_BLUE, edgecolor='white', linewidth=0.5)
    ax1.barh(y + bar_height/2, covid['no2_2020'], bar_height,
             label='Mar-Jun 2020 (lockdown)', color=CB_CYAN, edgecolor='white', linewidth=0.5)

    ax1.set_yticks(y)
    ax1.set_yticklabels(covid['station_name'])
    ax1.set_xlabel('Mean NO$_2$ ($\\mu$g/m$^3$)', fontsize=14)
    ax1.set_title('NO$_2$ Before and During COVID Lockdown', fontsize=16)
    ax1.legend(loc='lower right', fontsize=12)

    # Right panel: % change, coloured by station type
    colors = []
    for _, row in covid.iterrows():
        if row['station_type'] == 'traffic':
            colors.append(CB_RED)
        elif row['station_type'] == 'background':
            colors.append(CB_BLUE)
        else:
            colors.append(CB_GREEN)

    ax2.barh(y, covid['change_pct'], bar_height * 2, color=colors,
             edgecolor='white', linewidth=0.5)

    ax2.set_yticks(y)
    ax2.set_yticklabels(covid['station_name'])
    ax2.set_xlabel('NO$_2$ change (%)', fontsize=14)
    ax2.set_title('COVID Lockdown NO$_2$ Reduction by Station', fontsize=16)

    # Annotate percentages
    for i, (_, row) in enumerate(covid.iterrows()):
        pct = row['change_pct']
        ax2.text(pct - 2 if pct < -10 else pct + 1, i, f'{pct:.0f}%',
                 va='center', fontsize=10, fontweight='bold',
                 color='white' if pct < -30 else CB_BLACK)

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_RED, label='Traffic station'),
        Patch(facecolor=CB_BLUE, label='Background station'),
        Patch(facecolor=CB_GREEN, label='Rural station'),
    ]
    ax2.legend(handles=legend_elements, loc='lower left', fontsize=12)

    fig.suptitle('COVID-19 Lockdown as Natural Experiment for Traffic Attribution',
                 fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / 'covid_validation.png', bbox_inches='tight')
    plt.close(fig)
    print("  [4/5] covid_validation.png")


def plot_source_attribution():
    """Plot 5: Stacked bar showing traffic / heating / background fractions per station.

    Grouped by station type (traffic, background, rural) to show how the
    attribution changes with proximity to roads.
    """
    from evaluate import attribute_sources
    from data_loaders import KEY_STATIONS

    rows = []
    for code in KEY_STATIONS:
        name, stype, city = KEY_STATIONS[code]
        try:
            annual = attribute_sources(station=code)
        except Exception:
            continue
        # Use 2019 (pre-COVID)
        yr = annual[annual['year'] == 2019]
        if len(yr) == 0:
            yr = annual[annual['year'] == annual['year'].max()]
        if len(yr) == 0:
            continue
        row = yr.iloc[0]
        total = row['measured_annual']
        if total <= 0:
            continue
        rows.append({
            'station': name,
            'type': stype,
            'city': city,
            'total': total,
            'traffic_pct': row['traffic'] / total * 100,
            'heating_pct': row['heating'] / total * 100,
            'background_pct': row['background'] / total * 100,
            'traffic': row['traffic'],
            'heating': row['heating'],
            'background': row['background'],
        })

    rdf = pd.DataFrame(rows)

    # Sort: traffic stations first (descending by traffic %), then background, then rural
    type_order = {'traffic': 0, 'background': 1, 'rural-remote': 2, 'rural-regional': 2}
    rdf['type_rank'] = rdf['type'].map(type_order).fillna(3)
    rdf = rdf.sort_values(['type_rank', 'traffic_pct'], ascending=[True, False])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                    gridspec_kw={'width_ratios': [1, 1]})

    # Left panel: stacked bar (absolute values)
    x = np.arange(len(rdf))
    bar_width = 0.6

    ax1.bar(x, rdf['background'], bar_width, label='Regional background',
            color=CB_GREEN, edgecolor='white', linewidth=0.5)
    ax1.bar(x, rdf['heating'], bar_width, bottom=rdf['background'],
            label='Residential heating', color=CB_ORANGE, edgecolor='white', linewidth=0.5)
    ax1.bar(x, rdf['traffic'], bar_width,
            bottom=rdf['background'].values + rdf['heating'].values,
            label='Road traffic', color=CB_RED, edgecolor='white', linewidth=0.5)

    # WHO and EU lines
    ax1.axhline(y=10, color=CB_PURPLE, linestyle='--', linewidth=1.5, label='WHO (10)')
    ax1.axhline(y=40, color=CB_BLACK, linestyle=':', linewidth=1.5, label='EU (40)')

    ax1.set_xticks(x)
    ax1.set_xticklabels(rdf['station'], rotation=45, ha='right', fontsize=10)
    ax1.set_ylabel('Annual mean NO$_2$ ($\\mu$g/m$^3$)', fontsize=14)
    ax1.set_title('Source Attribution (Absolute)', fontsize=16)
    ax1.legend(loc='upper right', fontsize=11)

    # Add station type brackets/labels
    # Group boundaries
    prev_type = None
    group_starts = []
    for i, (_, row) in enumerate(rdf.iterrows()):
        if row['type'] != prev_type:
            group_starts.append((i, row['type']))
            prev_type = row['type']

    # Right panel: stacked bar (percentages)
    ax2.bar(x, rdf['background_pct'], bar_width, label='Regional background',
            color=CB_GREEN, edgecolor='white', linewidth=0.5)
    ax2.bar(x, rdf['heating_pct'], bar_width, bottom=rdf['background_pct'],
            label='Residential heating', color=CB_ORANGE, edgecolor='white', linewidth=0.5)
    ax2.bar(x, rdf['traffic_pct'], bar_width,
            bottom=rdf['background_pct'].values + rdf['heating_pct'].values,
            label='Road traffic', color=CB_RED, edgecolor='white', linewidth=0.5)

    ax2.set_xticks(x)
    ax2.set_xticklabels(rdf['station'], rotation=45, ha='right', fontsize=10)
    ax2.set_ylabel('Source contribution (%)', fontsize=14)
    ax2.set_title('Source Attribution (Percentage)', fontsize=16)
    ax2.legend(loc='lower right', fontsize=11)
    ax2.set_ylim(0, 105)

    fig.suptitle('NO$_2$ Source Attribution by Station Type (2019)',
                 fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / 'source_attribution.png', bbox_inches='tight')
    plt.close(fig)
    print("  [5/5] source_attribution.png")


def main():
    """Generate all plots."""
    print("Generating Dublin NO2 source attribution plots...")
    _setup()
    plot_pred_vs_actual()
    plot_feature_importance()
    plot_headline_finding()
    plot_covid_validation()
    plot_source_attribution()
    print(f"Done. All plots saved to {PLOTS_DIR}/")


if __name__ == '__main__':
    main()
