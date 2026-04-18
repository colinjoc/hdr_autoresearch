#!/usr/bin/env python3
"""Generate all plots for the NUFORC UFO sighting pattern analysis paper."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

sys.path.insert(0, PROJECT_DIR)
from data_loader import load_nuforc_str, load_nuforc_kaggle

STATE_POP_2020 = {
    'AL': 5024, 'AK': 733, 'AZ': 7151, 'AR': 3012, 'CA': 39538,
    'CO': 5773, 'CT': 3606, 'DE': 990, 'FL': 21538, 'GA': 10712,
    'HI': 1456, 'ID': 1901, 'IL': 12812, 'IN': 6786, 'IA': 3190,
    'KS': 2937, 'KY': 4506, 'LA': 4657, 'ME': 1362, 'MD': 6177,
    'MA': 7030, 'MI': 10077, 'MN': 5707, 'MS': 2961, 'MO': 6155,
    'MT': 1085, 'NE': 1962, 'NV': 3105, 'NH': 1378, 'NJ': 9289,
    'NM': 2118, 'NY': 20202, 'NC': 10440, 'ND': 779, 'OH': 11800,
    'OK': 3960, 'OR': 4238, 'PA': 13002, 'RI': 1098, 'SC': 5119,
    'SD': 887, 'TN': 6910, 'TX': 29146, 'UT': 3272, 'VT': 643,
    'VA': 8631, 'WA': 7615, 'WV': 1794, 'WI': 5894, 'WY': 577,
    'DC': 689
}


def plot_annual_trend(df):
    """Plot 1: Annual sighting count 1990-2024 (headline finding)."""
    valid = df[(df['year'] >= 1990) & (df['year'] <= 2024)]
    yearly = valid.groupby('year').size()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(yearly.index, yearly.values, alpha=0.3, color='steelblue')
    ax.plot(yearly.index, yearly.values, 'o-', color='steelblue', markersize=4)
    ax.axvline(x=2014, color='red', linestyle='--', alpha=0.7, label='Peak: 2014')
    ax.axvline(x=2019.4, color='orange', linestyle='--', alpha=0.7, label='Starlink launch (May 2019)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Sighting Reports')
    ax.legend(fontsize=9)
    ax.set_xlim(1990, 2024)
    fig.savefig(os.path.join(PLOTS_DIR, "headline_finding.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved headline_finding.png")


def plot_shape_evolution(df):
    """Plot 2: Shape category evolution over decades."""
    valid = df[(df['year'] >= 1990) & (df['year'] <= 2024) & df['Shape'].notna()].copy()
    valid['decade'] = (valid['year'] // 5) * 5  # 5-year bins for smoother view

    top_shapes = ['Light', 'Circle', 'Triangle', 'Fireball', 'Disk', 'Orb', 'Formation']
    shape_data = valid[valid['Shape'].isin(top_shapes)]
    shape_pct = shape_data.groupby(['decade', 'Shape']).size().unstack(fill_value=0)
    shape_pct = shape_pct.div(shape_pct.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Set2(np.linspace(0, 1, len(top_shapes)))
    for i, shape in enumerate(top_shapes):
        if shape in shape_pct.columns:
            ax.plot(shape_pct.index, shape_pct[shape], 'o-', label=shape,
                    color=colors[i], markersize=5, linewidth=2)
    ax.set_xlabel('5-Year Period')
    ax.set_ylabel('Percentage of Reports (%)')
    ax.legend(ncol=2, fontsize=9)
    ax.set_xlim(1990, 2024)
    fig.savefig(os.path.join(PLOTS_DIR, "shape_evolution.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved shape_evolution.png")


def plot_hour_of_day(df):
    """Plot 3: Hour-of-day distribution."""
    valid = df[df['hour'].notna()].copy()
    hour_counts = valid.groupby('hour').size()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(hour_counts.index, hour_counts.values, color='steelblue', alpha=0.8)
    # Highlight peak hour
    peak_idx = hour_counts.idxmax()
    bars[int(peak_idx)].set_color('darkred')

    ax.set_xlabel('Hour of Day (local time)')
    ax.set_ylabel('Number of Reports')
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], rotation=45)

    # Add dusk annotation
    ax.axvspan(17, 22, alpha=0.1, color='orange', label='Dusk window')
    ax.legend(fontsize=9)
    fig.savefig(os.path.join(PLOTS_DIR, "hour_of_day.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved hour_of_day.png")


def plot_feature_importance():
    """Plot 4: Feature importance from classifier."""
    # From the Random Forest run
    features = ['year', 'text_length', 'summary_length', 'month',
                'duration_seconds', 'hour', 'shape_enc', 'day_of_week']
    importances = [0.7173, 0.0679, 0.0571, 0.0544, 0.0321, 0.0284, 0.0264, 0.0164]

    labels = ['Year', 'Text Length', 'Summary Length', 'Month',
              'Duration', 'Hour', 'Shape Category', 'Day of Week']

    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = range(len(labels))
    ax.barh(y_pos, importances, color='steelblue', alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Permutation Importance')
    ax.invert_yaxis()
    fig.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved feature_importance.png")


def plot_starlink_impact(df):
    """Plot 5: Starlink impact on formation sightings."""
    valid = df[df['year'].notna() & df['Shape'].notna()].copy()
    valid = valid[valid['year'] >= 2015]

    monthly = valid.groupby([valid['year'].astype(int), valid['month'].astype(int)]).agg(
        total=('Shape', 'size'),
        formation=('Shape', lambda x: (x == 'Formation').sum()),
        light=('Shape', lambda x: (x == 'Light').sum()),
        disk=('Shape', lambda x: (x == 'Disk').sum()),
    ).reset_index()
    monthly.columns = ['year', 'month', 'total', 'formation', 'light', 'disk']

    monthly['date'] = pd.to_datetime(monthly['year'].astype(str) + '-' + monthly['month'].astype(str) + '-01')
    monthly['formation_pct'] = monthly['formation'] / monthly['total'] * 100
    monthly['disk_pct'] = monthly['disk'] / monthly['total'] * 100

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly['date'], monthly['formation_pct'], '-', label='Formation', color='tab:red', linewidth=1.5)
    ax.plot(monthly['date'], monthly['disk_pct'], '-', label='Disk (control)', color='tab:blue', linewidth=1.5, alpha=0.7)
    ax.axvline(x=pd.Timestamp('2019-05-01'), color='orange', linestyle='--', alpha=0.7,
               label='First Starlink launch')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage of Monthly Reports (%)')
    ax.legend(fontsize=9)
    fig.savefig(os.path.join(PLOTS_DIR, "starlink_impact.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved starlink_impact.png")


def plot_state_percapita(df):
    """Plot 6: State per-capita sighting rate (top 20)."""
    us_df = df[df['country_str'].isin(['USA', 'US', 'United States'])].copy()
    us_df['state_clean'] = us_df['state'].str.strip().str.upper()
    state_counts = us_df.groupby('state_clean').size().reset_index(name='count')
    state_counts = state_counts[state_counts['state_clean'].isin(STATE_POP_2020.keys())]
    state_counts['pop_thousands'] = state_counts['state_clean'].map(STATE_POP_2020)
    state_counts['per_100k'] = state_counts['count'] / state_counts['pop_thousands'] * 100
    state_counts = state_counts.sort_values('per_100k', ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(state_counts)), state_counts['per_100k'].values,
                   color='steelblue', alpha=0.8)
    ax.set_yticks(range(len(state_counts)))
    ax.set_yticklabels(state_counts['state_clean'].values)
    ax.set_xlabel('Sighting Reports per 100,000 Population')
    ax.invert_yaxis()
    fig.savefig(os.path.join(PLOTS_DIR, "state_percapita.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved state_percapita.png")


def plot_explanation_types(df):
    """Plot 7: Explanation type breakdown."""
    explained = df[df['has_explanation'] == 1]
    type_counts = explained['explanation_type'].value_counts().head(10)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(range(len(type_counts)), type_counts.values, color='steelblue', alpha=0.8)
    ax.set_yticks(range(len(type_counts)))
    ax.set_yticklabels(type_counts.index)
    ax.set_xlabel('Number of Reports')
    ax.invert_yaxis()
    fig.savefig(os.path.join(PLOTS_DIR, "explanation_types.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved explanation_types.png")


def plot_holiday_spikes(df):
    """Plot 8: Holiday spike ratios."""
    holidays = ['New Year\'s Eve', 'July 4th', 'Halloween']
    ratios = [2.83, 1.67, 1.36]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(holidays, ratios, color=['steelblue', 'darkred', 'darkorange'], alpha=0.8)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Baseline (1.0)')
    ax.set_ylabel('Daily Sighting Rate Ratio vs Rest of Month')
    ax.legend(fontsize=9)
    fig.savefig(os.path.join(PLOTS_DIR, "holiday_spikes.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved holiday_spikes.png")


def plot_spatial_heatmap(df_kaggle):
    """Plot 9: Spatial density of US sightings."""
    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    valid['latitude'] = pd.to_numeric(valid['latitude'], errors='coerce')
    valid['longitude'] = pd.to_numeric(valid['longitude'], errors='coerce')
    us = valid[(valid['latitude'].between(24, 50)) & (valid['longitude'].between(-125, -66))]

    fig, ax = plt.subplots(figsize=(12, 7))
    h = ax.hist2d(us['longitude'].values, us['latitude'].values,
                   bins=[100, 60], cmap='YlOrRd', cmin=1)
    plt.colorbar(h[3], ax=ax, label='Number of Sightings')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    fig.savefig(os.path.join(PLOTS_DIR, "spatial_heatmap.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved spatial_heatmap.png")


def plot_clock_hour_rounding(df):
    """Plot 10: Clock-hour rounding rate by decade."""
    valid = df[df['occurred_dt'].notna()].copy()
    valid['minute'] = valid['occurred_dt'].dt.minute
    valid['decade'] = (valid['year'] // 10) * 10

    rounding = valid[valid['decade'] >= 1990].groupby('decade').apply(
        lambda x: (x['minute'] == 0).mean() * 100
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([str(int(d))+'s' for d in rounding.index], rounding.values,
           color='steelblue', alpha=0.8)
    ax.axhline(y=100/60, color='red', linestyle='--', alpha=0.5, label='Expected (1.7%)')
    ax.set_ylabel('Reports on Exact Hour (%)')
    ax.set_xlabel('Decade')
    ax.legend(fontsize=9)
    fig.savefig(os.path.join(PLOTS_DIR, "clock_rounding.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved clock_rounding.png")


def main():
    print("Loading data...")
    df = load_nuforc_str()
    df_kaggle = load_nuforc_kaggle()
    print(f"Generating plots...")

    plot_annual_trend(df)
    plot_shape_evolution(df)
    plot_hour_of_day(df)
    plot_feature_importance()
    plot_starlink_impact(df)
    plot_state_percapita(df)
    plot_explanation_types(df)
    plot_holiday_spikes(df)
    plot_spatial_heatmap(df_kaggle)
    plot_clock_hour_rounding(df)

    print(f"\nAll plots saved to {PLOTS_DIR}/")


if __name__ == '__main__':
    main()
