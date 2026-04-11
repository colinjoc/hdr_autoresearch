"""
Generate publication-quality plots for flight delay propagation paper.

All plots use real BTS On-Time Performance data (Jan-Jun 2024).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from model import (
    prepare_enhanced_data, find_super_spreader_routes,
    carrier_propagation_analysis, hourly_delay_accumulation,
    airport_propagation_scores,
)
from evaluate import decompose_delay_variance, measure_propagation_depth

# Consistent styling
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
})

# Cache loaded data to avoid repeated I/O
_CACHED_DF = None
_CACHED_MONTHS = None


def _get_data(months=None):
    """Load data with caching."""
    global _CACHED_DF, _CACHED_MONTHS
    if months is None:
        months = [1, 2, 3, 4, 5, 6]
    if _CACHED_DF is not None and _CACHED_MONTHS == months:
        return _CACHED_DF
    _CACHED_DF = prepare_enhanced_data(2024, months)
    _CACHED_MONTHS = months
    return _CACHED_DF


def plot_hourly_delay_accumulation():
    """
    Plot 1: How delays accumulate through the day.

    Shows mean arrival delay and late-aircraft delay by hour of day,
    demonstrating the cascade accumulation pattern.
    """
    df = _get_data()
    hourly = hourly_delay_accumulation(df)
    # Filter to reasonable hours (5am - 23pm)
    hourly = hourly[(hourly['hour_of_day'] >= 5) & (hourly['hour_of_day'] <= 23)]

    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    color1 = '#2166ac'
    color2 = '#b2182b'

    ax1.bar(hourly['hour_of_day'], hourly['mean_arr_delay'],
            color=color1, alpha=0.7, label='Mean arrival delay', width=0.8)

    ax2 = ax1.twinx()
    ax2.plot(hourly['hour_of_day'], hourly['mean_late_aircraft'],
             color=color2, linewidth=2.5, marker='o', markersize=5,
             label='Mean late-aircraft delay')

    ax1.set_xlabel('Hour of day (scheduled departure)')
    ax1.set_ylabel('Mean arrival delay (minutes)', color=color1)
    ax2.set_ylabel('Mean late-aircraft delay (minutes)', color=color2)

    ax1.set_xticks(range(5, 24))
    ax1.set_xticklabels([f'{h:02d}:00' for h in range(5, 24)], rotation=45, ha='right')

    ax1.tick_params(axis='y', labelcolor=color1)
    ax2.tick_params(axis='y', labelcolor=color2)

    # Add annotation for key insight
    ax1.annotate('Morning flights start\nfrom clean overnight reset',
                 xy=(6, hourly[hourly['hour_of_day'] == 6]['mean_arr_delay'].values[0]),
                 xytext=(8, -5),
                 fontsize=9, ha='center',
                 arrowprops=dict(arrowstyle='->', color='gray', lw=1))

    ax1.annotate('Peak cascade\naccumulation',
                 xy=(19, hourly[hourly['hour_of_day'] == 19]['mean_arr_delay'].values[0]),
                 xytext=(21.5, 20),
                 fontsize=9, ha='center',
                 arrowprops=dict(arrowstyle='->', color='gray', lw=1))

    ax1.set_title('Delay cascade accumulation through the day\n'
                   'US domestic flights, Jan-Jun 2024 (3.4M flights)')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    ax1.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
    fig.tight_layout()

    return fig, ax1


def plot_carrier_propagation():
    """
    Plot 2: Carrier buffer strategy vs delay propagation.

    Shows that carriers with tighter schedules propagate more delay,
    while carriers with more buffer absorb delays.
    """
    df = _get_data()
    carriers = carrier_propagation_analysis(df)
    # Filter to carriers with at least 20k flights for reliability
    carriers = carriers[carriers['n_flights'] >= 20000].copy()

    fig, ax = plt.subplots(figsize=(12, 8))

    # Scatter: x = mean turnaround, y = mean late aircraft delay
    sizes = carriers['n_flights'] / 5000
    scatter = ax.scatter(
        carriers['mean_turnaround'],
        carriers['mean_late_aircraft'],
        s=sizes,
        c=carriers['delay_rate'],
        cmap='RdYlGn_r',
        edgecolors='black',
        linewidth=0.8,
        alpha=0.85,
        zorder=5,
    )

    # Add colorbar, labels, title BEFORE label placement so tight_layout is stable
    cbar = fig.colorbar(scatter, ax=ax, label='Delay rate (fraction >= 15 min)')
    ax.set_xlabel('Mean turnaround time (minutes)')
    ax.set_ylabel('Mean late-aircraft delay (minutes)')
    ax.set_title('Carrier buffer strategy determines delay propagation\n'
                 'Tighter turnarounds = more delay cascading through rotations')
    fig.tight_layout()

    # Now place labels with collision avoidance (layout is frozen)
    carriers_list = carriers.sort_values('mean_turnaround').reset_index(drop=True)
    label_offsets = {}

    for _, row in carriers_list.iterrows():
        code = row['Reporting_Airline']
        x = row['mean_turnaround']
        y = row['mean_late_aircraft']
        label_offsets[code] = (x + 5, y + 1.5)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    for iteration in range(500):
        temp_texts = {}
        for _, row in carriers_list.iterrows():
            code = row['Reporting_Airline']
            ox, oy = label_offsets[code]
            t = ax.annotate(
                code, (row['mean_turnaround'], row['mean_late_aircraft']),
                xytext=(ox, oy), textcoords='data',
                fontsize=9, fontweight='bold',
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.5),
            )
            temp_texts[code] = t

        fig.canvas.draw()
        codes = list(temp_texts.keys())
        bboxes = {c: temp_texts[c].get_window_extent(renderer=renderer) for c in codes}

        for t in temp_texts.values():
            t.remove()

        moved = False
        pad = 3
        for i_idx in range(len(codes)):
            for j_idx in range(i_idx + 1, len(codes)):
                ci, cj = codes[i_idx], codes[j_idx]
                bi, bj = bboxes[ci], bboxes[cj]
                ox_hit = (bi.x0 - pad) < bj.x1 and (bj.x0 - pad) < bi.x1
                oy_hit = (bi.y0 - pad) < bj.y1 and (bj.y0 - pad) < bi.y1
                if ox_hit and oy_hit:
                    xi, yi = label_offsets[ci]
                    xj, yj = label_offsets[cj]
                    step_y = 1.2
                    step_x = 4.0
                    if yi <= yj:
                        label_offsets[ci] = (xi, yi - step_y)
                        label_offsets[cj] = (xj, yj + step_y)
                    else:
                        label_offsets[ci] = (xi, yi + step_y)
                        label_offsets[cj] = (xj, yj - step_y)
                    if abs(xi - xj) < 10:
                        if xi <= xj:
                            label_offsets[ci] = (label_offsets[ci][0] - step_x, label_offsets[ci][1])
                            label_offsets[cj] = (label_offsets[cj][0] + step_x, label_offsets[cj][1])
                        else:
                            label_offsets[ci] = (label_offsets[ci][0] + step_x, label_offsets[ci][1])
                            label_offsets[cj] = (label_offsets[cj][0] - step_x, label_offsets[cj][1])
                    moved = True
        if not moved:
            break

    for _, row in carriers_list.iterrows():
        code = row['Reporting_Airline']
        ox, oy = label_offsets[code]
        ax.annotate(
            code, (row['mean_turnaround'], row['mean_late_aircraft']),
            xytext=(ox, oy), textcoords='data',
            fontsize=9, fontweight='bold',
            arrowprops=dict(arrowstyle='-', color='gray', lw=0.5),
        )

    return fig, ax


def plot_propagation_depth():
    """
    Plot 3: Distribution of delay propagation depth through rotation chains.

    Shows how far an initial delay ripples through subsequent flights.
    """
    # Use Jan 2024 for depth analysis (it's per-chain, so computationally expensive)
    prop = measure_propagation_depth(months=[1])

    fig, ax = plt.subplots(figsize=(9, 5.5))

    depths = prop['depth_distribution']
    x = sorted(depths.keys())
    y = [depths[d] for d in x]
    total = sum(y)
    pcts = [100 * v / total for v in y]

    bars = ax.bar(x, pcts, color='#2166ac', edgecolor='white', linewidth=0.5)

    # Add count labels on bars
    for bar, count, pct in zip(bars, y, pcts):
        if pct > 2:  # Only label visible bars
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                    f'{count:,}\n({pct:.1f}%)',
                    ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Propagation depth (number of flights affected)')
    ax.set_ylabel('Percentage of delay chains (%)')
    ax.set_title(f'How far does a delay ripple through the aircraft rotation?\n'
                 f'{total:,} delay chains analyzed (Jan 2024)')
    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in x])

    # Add key stats as text box
    stats_text = (f"Mean depth: {prop['mean_depth']:.1f} flights\n"
                  f"Containment rate: {prop['containment_rate']:.0%}\n"
                  f"Max observed: {prop['max_depth']} flights")
    ax.text(0.72, 0.85, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

    fig.tight_layout()
    return fig, ax


def plot_feature_importance():
    """
    Plot 4: Feature importance from XGBoost model.

    Shows which features matter most for predicting delay propagation.
    """
    from xgboost import XGBClassifier
    from prepare import make_target

    df = _get_data(months=[1, 2, 3])
    from model import get_enhanced_feature_columns
    feature_cols = get_enhanced_feature_columns()
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols].fillna(-999)
    y = make_target(df)

    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='logloss', verbosity=0, n_jobs=-1,
        tree_method='hist', random_state=42,
    )
    try:
        model.set_params(device='cuda')
        model.fit(X, y)
    except Exception:
        model.set_params(device='cpu')
        model.fit(X, y)

    imps = dict(zip(feature_cols, model.feature_importances_))

    # Human-readable labels
    label_map = {
        'prev_delay_x_buffer': 'Previous delay x buffer',
        'log_prev_delay': 'Log previous delay',
        'prior_flight_arr_delay': 'Prior flight arrival delay',
        'prior_flight_late_aircraft': 'Prior flight late-aircraft code',
        'dest_arr_delay_mean_1h': 'Dest. arrival delay (hourly)',
        'TaxiOut': 'Taxi-out time',
        'turnaround_time': 'Turnaround time',
        'origin_dep_delay_mean_1h': 'Origin dep. delay (hourly)',
        'buffer_over_min': 'Buffer over minimum',
        'is_regional': 'Regional carrier',
        'origin_dep_delay_std_1h': 'Origin delay variability',
        'dest_flights_1h': 'Dest. traffic volume',
        'carrier_buffer_factor': 'Carrier buffer factor',
        'rotation_position': 'Rotation position (leg #)',
        'origin_flights_1h': 'Origin traffic volume',
        'prior_flight_dep_delay': 'Prior flight dep. delay',
        'cumulative_delay': 'Cumulative delay',
        'origin_is_hub': 'Origin is hub',
        'dest_is_hub': 'Dest. is hub',
        'is_hub_to_hub': 'Hub-to-hub route',
        'morning_flight': 'Morning flight (6-9am)',
        'is_evening': 'Evening flight',
        'Distance': 'Route distance',
        'dep_hour_sin': 'Hour (sin)',
        'dep_hour_cos': 'Hour (cos)',
        'dow_sin': 'Day of week (sin)',
        'dow_cos': 'Day of week (cos)',
        'month_sin': 'Month (sin)',
        'month_cos': 'Month (cos)',
    }

    # Sort and take top 15
    sorted_imps = sorted(imps.items(), key=lambda x: -x[1])[:15]
    features = [label_map.get(f, f) for f, _ in sorted_imps]
    values = [v for _, v in sorted_imps]

    fig, ax = plt.subplots(figsize=(9, 6))

    # Color by category
    rotation_features = {'Previous delay x buffer', 'Log previous delay',
                         'Prior flight arrival delay', 'Prior flight late-aircraft code',
                         'Turnaround time', 'Buffer over minimum', 'Carrier buffer factor',
                         'Rotation position (leg #)', 'Prior flight dep. delay',
                         'Cumulative delay', 'Regional carrier'}
    colors = ['#b2182b' if f in rotation_features else '#2166ac' for f in features]

    bars = ax.barh(range(len(features)), values, color=colors, edgecolor='white')
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features)
    ax.invert_yaxis()
    ax.set_xlabel('Feature importance (XGBoost gain)')
    ax.set_title('What predicts whether a delay propagates?\n'
                 'Red = rotation chain features, Blue = airport/temporal features')

    # Add percentage labels
    total_imp = sum(values)
    for i, (bar, val) in enumerate(zip(bars, values)):
        pct = 100 * val / total_imp
        if pct > 2:
            ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
                    f'{pct:.1f}%', va='center', fontsize=8)

    fig.tight_layout()
    return fig, ax


def plot_delay_cause_decomposition():
    """
    Plot 5: Pie chart of delay causes from BTS data.

    Shows the breakdown of delay minutes by BTS cause code.
    """
    decomp = decompose_delay_variance(months=[1, 2, 3, 4, 5, 6])

    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ['Late aircraft\n(rotation)', 'Carrier\n(ops/crew)',
              'NAS\n(ATC/congestion)', 'Weather', 'Security']
    sizes = [decomp['rotation'], decomp['carrier'], decomp['nas'],
             decomp['weather'], decomp['security']]
    colors = ['#b2182b', '#ef8a62', '#fddbc7', '#67a9cf', '#d1e5f0']
    explode = [0.05, 0, 0, 0, 0]  # Emphasize rotation

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=90, pctdistance=0.75,
        textprops={'fontsize': 10},
    )

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax.set_title('What causes flight delays?\n'
                 'BTS delay cause decomposition, Jan-Jun 2024 (749K delayed flights)')

    fig.tight_layout()
    return fig, ax


def plot_shap_importance():
    """
    Plot 6: SHAP-based feature importance.

    Uses TreeExplainer for unbiased feature attribution, addressing
    the known gain-importance bias toward high-cardinality features.
    """
    from review_experiments import plot_shap_summary
    return plot_shap_summary(months=[1, 2, 3], sample_size=20000)


def save_all_plots(output_dir=None):
    """Save all plots to the specified directory."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'plots')
    os.makedirs(output_dir, exist_ok=True)

    plot_funcs = {
        'hourly_delay_accumulation': plot_hourly_delay_accumulation,
        'carrier_propagation': plot_carrier_propagation,
        'propagation_depth': plot_propagation_depth,
        'feature_importance': plot_feature_importance,
        'delay_cause_decomposition': plot_delay_cause_decomposition,
        'shap_importance': plot_shap_importance,
    }

    for name, func in plot_funcs.items():
        print(f'Generating {name}...')
        fig, ax = func()
        path = os.path.join(output_dir, f'{name}.png')
        fig.savefig(path)
        plt.close(fig)
        print(f'  Saved: {path}')


if __name__ == '__main__':
    save_all_plots()
    print('All plots generated.')
