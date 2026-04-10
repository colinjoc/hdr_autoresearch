#!/usr/bin/env python3
"""Generate all publication-quality plots for the Irish radon prediction paper.

Produces 3 figures in plots/:
  1. pred_vs_actual.png     -- predicted vs actual % homes > 200 Bq/m3 per grid square
  2. feature_importance.png -- top features ranked by XGBoost importance
  3. headline_finding.png   -- radon risk by geology type: the granite-till story

All data is REAL from EPA Ireland, GSI Tellus airborne survey, and GSI geology maps.
"""
import sys
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# Colourblind-safe palette (Wong 2011, Nature Methods)
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
    """Plot 1: Predicted vs actual % homes above 200 Bq/m3 per 10km grid square.

    Uses spatial CV (county-grouped) out-of-fold predictions to show honest
    performance without data leakage.
    """
    from data_loaders import build_dataset
    from model import build_best_model, FULL_FEATURES
    from sklearn.model_selection import GroupKFold

    X, y, groups = build_dataset()
    gkf = GroupKFold(n_splits=min(groups.nunique(), 10))

    all_preds = np.full(len(y), np.nan)
    all_counties = groups.values.copy()

    for train_idx, test_idx in gkf.split(X, y, groups):
        model, features = build_best_model()
        available = [f for f in features if f in X.columns]
        X_tr = X.iloc[train_idx][available].fillna(0)
        X_te = X.iloc[test_idx][available].fillna(0)
        model.fit(X_tr, y.iloc[train_idx])
        preds = model.predict(X_te)
        all_preds[test_idx] = np.clip(preds, 0, 100)

    valid = ~np.isnan(all_preds)
    y_val = y[valid].values
    p_val = all_preds[valid]

    fig, ax = plt.subplots(figsize=(10, 9))

    # Color by whether it's a High Radon Area
    is_hra = y_val >= 10.0
    ax.scatter(y_val[~is_hra], p_val[~is_hra], alpha=0.35, s=30,
               color=CB_BLUE, label='Non-HRA (<10%)', zorder=2)
    ax.scatter(y_val[is_hra], p_val[is_hra], alpha=0.55, s=40,
               color=CB_RED, label='High Radon Area (>=10%)', zorder=3)

    # 1:1 line
    lim = max(y_val.max(), p_val.max()) * 1.05
    ax.plot([0, lim], [0, lim], '--', color=CB_BLACK, linewidth=1.5,
            alpha=0.6, label='Perfect prediction', zorder=1)

    # HRA threshold lines
    ax.axhline(10, color=CB_ORANGE, linestyle=':', linewidth=1.2,
               alpha=0.7, label='HRA threshold (10%)')
    ax.axvline(10, color=CB_ORANGE, linestyle=':', linewidth=1.2, alpha=0.7)

    # Stats annotation
    mae = np.mean(np.abs(y_val - p_val))
    corr = np.corrcoef(y_val, p_val)[0, 1]
    from sklearn.metrics import f1_score
    pred_hra = (p_val >= 10.0).astype(int)
    actual_hra = (y_val >= 10.0).astype(int)
    f1 = f1_score(actual_hra, pred_hra)

    stats_text = (f'MAE = {mae:.1f}%\n'
                  f'r = {corr:.2f}\n'
                  f'HRA F1 = {f1:.2f}\n'
                  f'n = {len(y_val)} grid squares')
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes,
            fontsize=13, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor='gray', alpha=0.9))

    ax.set_xlabel('Actual % homes above 200 Bq/m\u00b3')
    ax.set_ylabel('Predicted % homes above 200 Bq/m\u00b3')
    ax.set_title('Predicted vs Actual Radon Risk\n(Spatial CV, county-grouped)')
    ax.legend(loc='lower right', framealpha=0.9)
    ax.set_xlim(-1, lim)
    ax.set_ylim(-1, lim)

    fig.savefig(PLOTS_DIR / 'pred_vs_actual.png')
    plt.close(fig)
    print('  -> pred_vs_actual.png')


def plot_feature_importance():
    """Plot 2: Feature importance from the best XGBoost model.

    Shows the top 15 features by gain-based importance, with human-readable
    names and grouped by category (geology, radiometric, subsoil, geographic).
    """
    from data_loaders import build_dataset
    from model import build_best_model

    X, y, groups = build_dataset()
    model, features = build_best_model()
    available = [f for f in features if f in X.columns]
    model.fit(X[available].fillna(0), y)

    imp = dict(zip(available, model.feature_importances_))
    top = sorted(imp.items(), key=lambda x: x[1], reverse=True)[:15]

    # Human-readable labels
    name_map = {
        'eU_mean': 'Uranium (eU)',
        'eTh_mean': 'Thorium (eTh)',
        'K_mean': 'Potassium (K)',
        'eU_std': 'Uranium variability',
        'eU_p90': 'Uranium 90th percentile',
        'eU_eTh_ratio': 'Uranium/Thorium ratio',
        'total_dose_rate': 'Total dose rate',
        'log_eU': 'Log uranium',
        'centroid_x': 'Longitude (easting)',
        'centroid_y': 'Latitude (northing)',
        'bedrock_is_granite': 'Granite bedrock',
        'bedrock_is_limestone': 'Limestone bedrock',
        'bedrock_is_shale': 'Shale bedrock',
        'bedrock_is_sandstone': 'Sandstone bedrock',
        'bedrock_is_carboniferous': 'Carboniferous age',
        'bedrock_is_devonian': 'Devonian age',
        'bedrock_is_ordovician_silurian': 'Ordovician/Silurian age',
        'subsoil_is_till': 'Till (glacial) subsoil',
        'subsoil_is_peat': 'Peat subsoil',
        'subsoil_is_alluvium': 'Alluvial subsoil',
        'subsoil_is_gravel': 'Sand/gravel subsoil',
        'till_is_granite': 'Granite-derived till',
        'till_is_limestone': 'Limestone-derived till',
        'till_is_shale': 'Shale-derived till',
        'till_is_sandstone': 'Sandstone-derived till',
        'till_is_metamorphic': 'Metamorphic-derived till',
        'eU_x_granite': 'Uranium x Granite',
        'eU_x_limestone': 'Uranium x Limestone',
        'eU_x_shale': 'Uranium x Shale',
        'eU_x_peat': 'Uranium x Peat',
        'eU_x_gravel': 'Uranium x Gravel',
        'eU_x_till': 'Uranium x Till',
        'granite_x_till': 'Granite x Till',
        'limestone_x_gravel': 'Limestone x Gravel',
    }

    # Category colors
    def _get_color(fname):
        if 'bedrock_unit' in fname or 'bedrock_age' in fname:
            return CB_PURPLE
        if fname.startswith('eU') or fname.startswith('eTh') or fname.startswith('K') or fname.startswith('log_eU') or fname.startswith('total_dose'):
            return CB_RED
        if fname.startswith('bedrock') or fname.startswith('granite') or fname.startswith('limestone'):
            return CB_BLUE
        if fname.startswith('subsoil') or fname.startswith('till'):
            return CB_GREEN
        if 'x_' in fname:
            return CB_ORANGE
        return CB_CYAN  # geographic

    names = []
    values = []
    colors = []
    for fname, val in reversed(top):
        short = name_map.get(fname, fname.replace('bedrock_unit_', '').replace('bedrock_age_', '')[:30])
        names.append(short)
        values.append(val)
        colors.append(_get_color(fname))

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(range(len(names)), values, color=colors, edgecolor='white',
                   linewidth=0.5, height=0.7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=12)
    ax.set_xlabel('Feature importance (XGBoost gain)')
    ax.set_title('Top 15 Features for Radon Risk Prediction')

    # Legend for categories
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_RED, label='Radiometric'),
        Patch(facecolor=CB_BLUE, label='Bedrock geology'),
        Patch(facecolor=CB_GREEN, label='Subsoil'),
        Patch(facecolor=CB_PURPLE, label='Bedrock unit/age'),
        Patch(facecolor=CB_ORANGE, label='Interaction'),
        Patch(facecolor=CB_CYAN, label='Geographic'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9)

    fig.savefig(PLOTS_DIR / 'feature_importance.png')
    plt.close(fig)
    print('  -> feature_importance.png')


def plot_headline_finding():
    """Plot 3: Radon risk by geology type -- the granite-subsoil story.

    Shows that granite bedrock with granitic till produces the highest
    radon risk, and that the uranium signal from Tellus survey strongly
    differentiates risk within each bedrock type.
    """
    from data_loaders import build_dataset

    X, y, groups = build_dataset()
    df = X.copy()
    df['pct_above_rl'] = y.values

    # Panel A: Radon risk by dominant bedrock type
    bedrock_types = {
        'Granite': 'bedrock_is_granite',
        'Limestone': 'bedrock_is_limestone',
        'Shale': 'bedrock_is_shale',
        'Sandstone': 'bedrock_is_sandstone',
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Panel A: Box plot by bedrock type
    ax = axes[0]
    data_by_type = {}
    for btype, col in bedrock_types.items():
        if col in df.columns:
            mask = df[col] == 1
            if mask.sum() > 5:
                data_by_type[btype] = df.loc[mask, 'pct_above_rl'].values

    # Add "Other" for non-matching
    other_mask = pd.Series(True, index=df.index)
    for col in bedrock_types.values():
        if col in df.columns:
            other_mask &= (df[col] == 0)
    if other_mask.sum() > 5:
        data_by_type['Other'] = df.loc[other_mask, 'pct_above_rl'].values

    type_colors = {
        'Granite': CB_RED,
        'Limestone': CB_BLUE,
        'Shale': CB_PURPLE,
        'Sandstone': CB_ORANGE,
        'Other': CB_CYAN,
    }

    positions = list(range(len(data_by_type)))
    bp = ax.boxplot(
        [data_by_type[k] for k in data_by_type.keys()],
        positions=positions,
        widths=0.6,
        patch_artist=True,
        showfliers=True,
        flierprops=dict(marker='o', markersize=3, alpha=0.3),
    )
    for patch, key in zip(bp['boxes'], data_by_type.keys()):
        patch.set_facecolor(type_colors.get(key, CB_CYAN))
        patch.set_alpha(0.7)
    for median in bp['medians']:
        median.set_color(CB_BLACK)
        median.set_linewidth(2)

    ax.set_xticks(positions)
    ax.set_xticklabels(list(data_by_type.keys()), fontsize=13)
    ax.axhline(10, color=CB_ORANGE, linestyle='--', linewidth=1.2,
               alpha=0.7, label='HRA threshold (10%)')
    ax.set_ylabel('% homes above 200 Bq/m\u00b3')
    ax.set_title('(a) Radon risk by bedrock type')
    ax.legend(loc='upper right', fontsize=11)

    # Add n= annotations
    for i, key in enumerate(data_by_type.keys()):
        n = len(data_by_type[key])
        median = np.median(data_by_type[key])
        ax.text(i, -3.5, f'n={n}', ha='center', fontsize=10, color='gray')

    # Panel B: eU signal split by above/below median within granite areas
    ax2 = axes[1]
    if 'eU_mean' in df.columns:
        # Show the relationship between eU and radon for each major bedrock type
        for btype, col in [('Granite', 'bedrock_is_granite'),
                           ('Limestone', 'bedrock_is_limestone'),
                           ('Shale', 'bedrock_is_shale')]:
            if col in df.columns:
                mask = (df[col] == 1) & df['eU_mean'].notna()
                if mask.sum() > 10:
                    ax2.scatter(
                        df.loc[mask, 'eU_mean'],
                        df.loc[mask, 'pct_above_rl'],
                        alpha=0.4, s=25,
                        color=type_colors[btype],
                        label=btype,
                    )

        # Other
        if other_mask.sum() > 10:
            omask = other_mask & df['eU_mean'].notna()
            ax2.scatter(
                df.loc[omask, 'eU_mean'],
                df.loc[omask, 'pct_above_rl'],
                alpha=0.15, s=15,
                color=type_colors['Other'],
                label='Other',
            )

        ax2.axhline(10, color=CB_ORANGE, linestyle='--', linewidth=1.2,
                     alpha=0.7)
        ax2.set_xlabel('Tellus uranium signal (eU, normalized)')
        ax2.set_ylabel('% homes above 200 Bq/m\u00b3')
        ax2.set_title('(b) Uranium signal vs radon by bedrock')
        ax2.legend(loc='upper left', fontsize=11, framealpha=0.9)

    fig.suptitle('Geology Controls Irish Radon: The Granite-Uranium Story',
                 fontsize=17, y=1.02)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / 'headline_finding.png')
    plt.close(fig)
    print('  -> headline_finding.png')


def main():
    _setup()
    print('Generating plots...')
    plot_pred_vs_actual()
    plot_feature_importance()
    plot_headline_finding()
    print(f'All plots saved to {PLOTS_DIR}/')


if __name__ == '__main__':
    main()
