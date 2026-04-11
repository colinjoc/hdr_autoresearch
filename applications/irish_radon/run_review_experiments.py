#!/usr/bin/env python3
"""Run all experiments requested by the paper review.

Experiments:
1. SHAP analysis (TreeSHAP for XGBoost)
2. Precision/recall decomposition for HRA classification
3. Threshold sensitivity analysis (optimize for recall >= 0.9)
4. Random CV comparison (to compare with Elio et al.)
5. Calibration analysis (reliability diagram)
6. Bootstrap confidence intervals on MAE, F1, feature importance
7. Granite-till interaction ablation (explicit count + MAE with/without)
8. Residual spatial analysis (per-county residual patterns)

Outputs saved to plots/ and printed to stdout as structured results.
"""
import sys
import os
import warnings

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

from sklearn.model_selection import GroupKFold, KFold
from sklearn.metrics import (
    mean_absolute_error, f1_score, precision_score, recall_score,
    accuracy_score, roc_auc_score, precision_recall_curve
)

from data_loaders import build_dataset
from model import build_best_model, FULL_FEATURES, INTERACTION_FEATURES, ENHANCED_FEATURES

# Colourblind-safe palette
CB_BLUE = '#0072B2'
CB_ORANGE = '#E69F00'
CB_GREEN = '#009E73'
CB_RED = '#D55E00'
CB_PURPLE = '#CC79A7'
CB_CYAN = '#56B4E9'
CB_BLACK = '#000000'

PLOTS_DIR = Path(PROJECT_DIR) / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

HRA_THRESHOLD = 10.0

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


def _get_oof_predictions(X, y, groups, model_fn, features, use_spatial=True, n_splits=10):
    """Get out-of-fold predictions from spatial or random CV."""
    if use_spatial:
        n_groups = groups.nunique()
        gkf = GroupKFold(n_splits=min(n_groups, n_splits))
        splits = list(gkf.split(X, y, groups))
    else:
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        splits = list(kf.split(X, y))

    all_preds = np.full(len(y), np.nan)
    fold_maes = []

    for train_idx, test_idx in splits:
        model, _ = model_fn()
        available = [f for f in features if f in X.columns]
        X_tr = X.iloc[train_idx][available].fillna(0)
        X_te = X.iloc[test_idx][available].fillna(0)
        model.fit(X_tr, y.iloc[train_idx])
        preds = np.clip(model.predict(X_te), 0, 100)
        all_preds[test_idx] = preds
        fold_maes.append(mean_absolute_error(y.iloc[test_idx], preds))

    return all_preds, fold_maes


def experiment_shap(X, y, groups):
    """Experiment 1: SHAP analysis using TreeSHAP."""
    print("\n" + "="*70)
    print("EXPERIMENT 1: SHAP Analysis (TreeSHAP)")
    print("="*70)

    import shap

    model, features = build_best_model()
    available = [f for f in features if f in X.columns]
    X_full = X[available].fillna(0)
    model.fit(X_full, y)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_full)

    # Mean absolute SHAP values
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    shap_importance = dict(zip(available, mean_abs_shap))
    shap_sorted = sorted(shap_importance.items(), key=lambda x: x[1], reverse=True)

    print("\nTop 15 features by mean |SHAP value|:")
    for fname, val in shap_sorted[:15]:
        print(f"  {fname}: {val:.4f}")

    # Compare with gain importance
    gain_importance = dict(zip(available, model.feature_importances_))
    gain_sorted = sorted(gain_importance.items(), key=lambda x: x[1], reverse=True)

    print("\nTop 15 features by XGBoost gain (for comparison):")
    for fname, val in gain_sorted[:15]:
        print(f"  {fname}: {val:.4f}")

    # SHAP summary plot
    fig, ax = plt.subplots(figsize=(12, 10))
    # Manual SHAP bar plot for top 15
    top_n = 15
    top_features = [f for f, _ in shap_sorted[:top_n]]
    top_values = [v for _, v in shap_sorted[:top_n]]

    name_map = {
        'eU_mean': 'Uranium (eU)',
        'eTh_mean': 'Thorium (eTh)',
        'K_mean': 'Potassium (K)',
        'eU_std': 'Uranium variability',
        'eU_p90': 'Uranium 90th pctile',
        'eU_eTh_ratio': 'U/Th ratio',
        'total_dose_rate': 'Total dose rate',
        'log_eU': 'Log uranium',
        'centroid_x': 'Longitude',
        'centroid_y': 'Latitude',
        'bedrock_is_granite': 'Granite bedrock',
        'bedrock_is_limestone': 'Limestone bedrock',
        'bedrock_is_shale': 'Shale bedrock',
        'bedrock_is_sandstone': 'Sandstone bedrock',
        'bedrock_is_carboniferous': 'Carboniferous age',
        'bedrock_is_devonian': 'Devonian age',
        'bedrock_is_ordovician_silurian': 'Ordovician/Silurian',
        'subsoil_is_till': 'Till subsoil',
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
        return CB_CYAN

    labels = [name_map.get(f, f.replace('bedrock_unit_', '').replace('bedrock_age_', '')[:30]) for f in reversed(top_features)]
    vals = list(reversed(top_values))
    colors = [_get_color(f) for f in reversed(top_features)]

    ax.barh(range(len(labels)), vals, color=colors, edgecolor='white', height=0.7)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xlabel('Mean |SHAP value| (percentage points)')
    ax.set_title('Feature Importance by SHAP Values\n(TreeSHAP, full training set)')

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

    fig.savefig(PLOTS_DIR / 'shap_importance.png')
    plt.close(fig)
    print("  -> shap_importance.png")

    # SHAP beeswarm for top 10
    fig2 = plt.figure(figsize=(12, 8))
    top10_idx = [available.index(f) for f in top_features[:10]]
    shap_top10 = shap_values[:, top10_idx]
    X_top10 = X_full.iloc[:, top10_idx]
    # Rename columns for display
    X_top10_display = X_top10.copy()
    X_top10_display.columns = [name_map.get(f, f[:30]) for f in top_features[:10]]

    shap.summary_plot(shap_top10, X_top10_display, show=False, max_display=10)
    plt.title('SHAP Beeswarm: Top 10 Features')
    plt.tight_layout()
    fig2.savefig(PLOTS_DIR / 'shap_beeswarm.png')
    plt.close(fig2)
    print("  -> shap_beeswarm.png")

    # SHAP interaction for granite_x_till
    if 'granite_x_till' in available:
        gt_idx = available.index('granite_x_till')
        gt_shap = shap_values[:, gt_idx]
        gt_feat = X_full['granite_x_till'].values
        print(f"\n  granite_x_till SHAP: mean |SHAP| = {np.abs(gt_shap).mean():.4f}")
        print(f"  granite_x_till == 1: n = {(gt_feat == 1).sum()}, mean SHAP = {gt_shap[gt_feat == 1].mean():.3f}")
        print(f"  granite_x_till == 0: n = {(gt_feat == 0).sum()}, mean SHAP = {gt_shap[gt_feat == 0].mean():.3f}")

    return shap_importance, shap_values, available


def experiment_precision_recall(X, y, groups):
    """Experiment 2: Precision/recall decomposition and threshold sensitivity."""
    print("\n" + "="*70)
    print("EXPERIMENT 2: Precision/Recall Decomposition & Threshold Sensitivity")
    print("="*70)

    all_preds, fold_maes = _get_oof_predictions(X, y, groups, build_best_model, FULL_FEATURES)

    valid = ~np.isnan(all_preds)
    y_val = y[valid].values
    p_val = all_preds[valid]

    y_hra = (y_val >= HRA_THRESHOLD).astype(int)

    # At default threshold (10%)
    pred_hra_10 = (p_val >= HRA_THRESHOLD).astype(int)
    prec_10 = precision_score(y_hra, pred_hra_10, zero_division=0)
    rec_10 = recall_score(y_hra, pred_hra_10, zero_division=0)
    f1_10 = f1_score(y_hra, pred_hra_10, zero_division=0)

    print(f"\nAt HRA threshold = {HRA_THRESHOLD}%:")
    print(f"  Precision: {prec_10:.3f}")
    print(f"  Recall:    {rec_10:.3f}")
    print(f"  F1:        {f1_10:.3f}")
    print(f"  # actual HRA: {y_hra.sum()}")
    print(f"  # predicted HRA: {pred_hra_10.sum()}")
    print(f"  True positives: {((pred_hra_10 == 1) & (y_hra == 1)).sum()}")
    print(f"  False negatives: {((pred_hra_10 == 0) & (y_hra == 1)).sum()}")
    print(f"  False positives: {((pred_hra_10 == 1) & (y_hra == 0)).sum()}")

    # False negatives: dangerous areas the model misses
    fn_mask = (pred_hra_10 == 0) & (y_hra == 1)
    fn_actual = y_val[fn_mask]
    if len(fn_actual) > 0:
        print(f"\n  False negatives (missed dangerous areas):")
        print(f"    Count: {len(fn_actual)}")
        print(f"    Actual radon %: mean={fn_actual.mean():.1f}, max={fn_actual.max():.1f}")
        print(f"    These areas have >10% homes above reference but model says safe")

    # Threshold sensitivity
    thresholds = np.arange(2, 20, 0.5)
    results = []
    for t in thresholds:
        pred_t = (p_val >= t).astype(int)
        prec = precision_score(y_hra, pred_t, zero_division=0)
        rec = recall_score(y_hra, pred_t, zero_division=0)
        f1 = f1_score(y_hra, pred_t, zero_division=0)
        results.append({'threshold': t, 'precision': prec, 'recall': rec, 'f1': f1})

    results_df = pd.DataFrame(results)

    # Find threshold for recall >= 0.9
    high_recall = results_df[results_df['recall'] >= 0.9]
    if len(high_recall) > 0:
        best_hr = high_recall.loc[high_recall['f1'].idxmax()]
        print(f"\n  Best threshold for recall >= 0.9:")
        print(f"    Threshold: {best_hr['threshold']:.1f}%")
        print(f"    Precision: {best_hr['precision']:.3f}")
        print(f"    Recall:    {best_hr['recall']:.3f}")
        print(f"    F1:        {best_hr['f1']:.3f}")
    else:
        print(f"\n  Cannot achieve recall >= 0.9 at any threshold")
        best_rec = results_df.loc[results_df['recall'].idxmax()]
        print(f"  Best recall: {best_rec['recall']:.3f} at threshold {best_rec['threshold']:.1f}%")

    # Find threshold that maximizes F1
    best_f1_row = results_df.loc[results_df['f1'].idxmax()]
    print(f"\n  F1-optimal threshold: {best_f1_row['threshold']:.1f}%")
    print(f"    Precision: {best_f1_row['precision']:.3f}")
    print(f"    Recall:    {best_f1_row['recall']:.3f}")
    print(f"    F1:        {best_f1_row['f1']:.3f}")

    # Plot threshold sensitivity
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(results_df['threshold'], results_df['precision'], '-', color=CB_BLUE,
            linewidth=2, label='Precision')
    ax.plot(results_df['threshold'], results_df['recall'], '-', color=CB_RED,
            linewidth=2, label='Recall')
    ax.plot(results_df['threshold'], results_df['f1'], '--', color=CB_GREEN,
            linewidth=2, label='F1')
    ax.axvline(HRA_THRESHOLD, color=CB_ORANGE, linestyle=':', linewidth=1.5,
               alpha=0.7, label=f'EPA threshold ({HRA_THRESHOLD}%)')
    if len(high_recall) > 0:
        ax.axvline(best_hr['threshold'], color=CB_PURPLE, linestyle='--',
                   linewidth=1.5, alpha=0.7, label=f'Recall>=0.9 ({best_hr["threshold"]:.1f}%)')

    ax.set_xlabel('Classification threshold (% homes above reference level)')
    ax.set_ylabel('Score')
    ax.set_title('Threshold Sensitivity for HRA Classification\n(Spatial CV predictions)')
    ax.legend(loc='center left', framealpha=0.9)
    ax.set_ylim(-0.02, 1.02)

    fig.savefig(PLOTS_DIR / 'threshold_sensitivity.png')
    plt.close(fig)
    print("  -> threshold_sensitivity.png")

    return results_df


def experiment_random_cv(X, y, groups):
    """Experiment 3: Random CV comparison (to compare with Elio et al.)."""
    print("\n" + "="*70)
    print("EXPERIMENT 3: Random CV vs Spatial CV Comparison")
    print("="*70)

    # Spatial CV
    spatial_preds, spatial_maes = _get_oof_predictions(
        X, y, groups, build_best_model, FULL_FEATURES, use_spatial=True)

    # Random CV
    random_preds, random_maes = _get_oof_predictions(
        X, y, groups, build_best_model, FULL_FEATURES, use_spatial=False)

    valid_s = ~np.isnan(spatial_preds)
    valid_r = ~np.isnan(random_preds)

    # Spatial CV metrics
    y_hra_s = (y[valid_s].values >= HRA_THRESHOLD).astype(int)
    pred_hra_s = (spatial_preds[valid_s] >= HRA_THRESHOLD).astype(int)
    mae_s = np.mean(np.abs(y[valid_s].values - spatial_preds[valid_s]))
    f1_s = f1_score(y_hra_s, pred_hra_s, zero_division=0)
    corr_s = np.corrcoef(y[valid_s].values, spatial_preds[valid_s])[0, 1]

    # Random CV metrics
    y_hra_r = (y[valid_r].values >= HRA_THRESHOLD).astype(int)
    pred_hra_r = (random_preds[valid_r] >= HRA_THRESHOLD).astype(int)
    mae_r = np.mean(np.abs(y[valid_r].values - random_preds[valid_r]))
    f1_r = f1_score(y_hra_r, pred_hra_r, zero_division=0)
    corr_r = np.corrcoef(y[valid_r].values, random_preds[valid_r])[0, 1]

    # AUC
    auc_s = roc_auc_score(y_hra_s, spatial_preds[valid_s])
    auc_r = roc_auc_score(y_hra_r, random_preds[valid_r])

    print(f"\n{'Metric':<20} {'Spatial CV':>12} {'Random CV':>12} {'Inflation':>12}")
    print("-" * 56)
    print(f"{'MAE':<20} {mae_s:>12.2f} {mae_r:>12.2f} {(mae_s-mae_r)/mae_r*100:>11.1f}%")
    print(f"{'HRA F1':<20} {f1_s:>12.3f} {f1_r:>12.3f} {(f1_r-f1_s)/f1_s*100:>11.1f}%")
    print(f"{'Correlation':<20} {corr_s:>12.3f} {corr_r:>12.3f} {(corr_r-corr_s)/corr_s*100:>11.1f}%")
    print(f"{'AUC':<20} {auc_s:>12.3f} {auc_r:>12.3f} {(auc_r-auc_s)/auc_s*100:>11.1f}%")
    print(f"\nElio et al. reported AUC: 0.78-0.82 (random CV)")
    print(f"Our random CV AUC:        {auc_r:.3f}")
    print(f"Our spatial CV AUC:       {auc_s:.3f}")
    print(f"Spatial CV deflation:     {(auc_s - auc_r) / auc_r * 100:.1f}%")

    return {
        'spatial': {'mae': mae_s, 'f1': f1_s, 'corr': corr_s, 'auc': auc_s},
        'random': {'mae': mae_r, 'f1': f1_r, 'corr': corr_r, 'auc': auc_r},
    }


def experiment_calibration(X, y, groups):
    """Experiment 4: Calibration plot (reliability diagram)."""
    print("\n" + "="*70)
    print("EXPERIMENT 4: Calibration Analysis")
    print("="*70)

    all_preds, _ = _get_oof_predictions(X, y, groups, build_best_model, FULL_FEATURES)

    valid = ~np.isnan(all_preds)
    y_val = y[valid].values
    p_val = all_preds[valid]

    # Bin predictions and compute actual fraction of HRA in each bin
    bins = [0, 3, 5, 7, 10, 13, 16, 20, 30, 55]
    bin_labels = []
    bin_pred_mean = []
    bin_actual_mean = []
    bin_actual_hra_frac = []
    bin_counts = []

    for i in range(len(bins) - 1):
        mask = (p_val >= bins[i]) & (p_val < bins[i+1])
        if mask.sum() > 0:
            bin_labels.append(f'{bins[i]}-{bins[i+1]}%')
            bin_pred_mean.append(p_val[mask].mean())
            bin_actual_mean.append(y_val[mask].mean())
            bin_actual_hra_frac.append((y_val[mask] >= HRA_THRESHOLD).mean())
            bin_counts.append(mask.sum())

    print("\nCalibration by prediction bin:")
    print(f"{'Predicted range':<15} {'n':>5} {'Mean pred':>10} {'Mean actual':>12} {'Frac HRA':>10}")
    print("-" * 52)
    for i in range(len(bin_labels)):
        print(f"{bin_labels[i]:<15} {bin_counts[i]:>5} {bin_pred_mean[i]:>10.1f} {bin_actual_mean[i]:>12.1f} {bin_actual_hra_frac[i]:>10.2f}")

    # Calibration plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Panel A: Predicted vs actual continuous calibration
    ax1.scatter(bin_pred_mean, bin_actual_mean, s=[n*2 for n in bin_counts],
                color=CB_BLUE, alpha=0.7, edgecolor='white', linewidth=1, zorder=3)
    lim = max(max(bin_pred_mean), max(bin_actual_mean)) * 1.1
    ax1.plot([0, lim], [0, lim], '--', color=CB_BLACK, linewidth=1.5, alpha=0.5,
             label='Perfect calibration')
    for i in range(len(bin_labels)):
        ax1.annotate(f'n={bin_counts[i]}', (bin_pred_mean[i], bin_actual_mean[i]),
                     textcoords='offset points', xytext=(5, 5), fontsize=9, color='gray')
    ax1.set_xlabel('Mean predicted %')
    ax1.set_ylabel('Mean actual %')
    ax1.set_title('(a) Continuous calibration')
    ax1.legend(loc='upper left')

    # Panel B: HRA classification calibration
    ax2.bar(range(len(bin_labels)), bin_actual_hra_frac, color=CB_RED, alpha=0.7,
            edgecolor='white', label='Actual HRA fraction')
    # Expected HRA fraction if perfectly calibrated
    expected_hra = [(p >= HRA_THRESHOLD) * 1.0 for p in bin_pred_mean]
    ax2.step(range(len(bin_labels)), expected_hra, where='mid',
             color=CB_BLACK, linewidth=2, linestyle='--', label='Expected if calibrated')
    ax2.set_xticks(range(len(bin_labels)))
    ax2.set_xticklabels(bin_labels, rotation=45, ha='right')
    ax2.set_ylabel('Fraction that are actual HRA')
    ax2.set_title('(b) HRA classification calibration')
    ax2.legend(loc='upper left')

    fig.suptitle('Model Calibration: Predicted vs Actual Radon Risk', fontsize=16, y=1.02)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / 'calibration.png')
    plt.close(fig)
    print("  -> calibration.png")

    # Systematic bias analysis
    # For high-radon areas (actual > 20%), what does the model predict?
    high_radon = y_val >= 20
    if high_radon.sum() > 0:
        print(f"\n  Systematic underprediction analysis:")
        print(f"    Grid squares with actual >= 20%: n = {high_radon.sum()}")
        print(f"    Their mean actual:    {y_val[high_radon].mean():.1f}%")
        print(f"    Their mean predicted: {p_val[high_radon].mean():.1f}%")
        print(f"    Mean underprediction: {(y_val[high_radon] - p_val[high_radon]).mean():.1f} pp")

    very_high = y_val >= 30
    if very_high.sum() > 0:
        print(f"\n    Grid squares with actual >= 30%: n = {very_high.sum()}")
        print(f"    Their mean actual:    {y_val[very_high].mean():.1f}%")
        print(f"    Their mean predicted: {p_val[very_high].mean():.1f}%")
        print(f"    Mean underprediction: {(y_val[very_high] - p_val[very_high]).mean():.1f} pp")

    return bin_pred_mean, bin_actual_mean, bin_counts


def experiment_bootstrap(X, y, groups, n_boot=50):
    """Experiment 5: Bootstrap confidence intervals."""
    print("\n" + "="*70)
    print(f"EXPERIMENT 5: Bootstrap Confidence Intervals ({n_boot} iterations)")
    print("="*70)

    rng = np.random.RandomState(42)
    boot_maes = []
    boot_f1s = []
    boot_precisions = []
    boot_recalls = []
    granite_till_importances = []

    for i in range(n_boot):
        # Resample at the group (county) level
        unique_counties = groups.unique()
        boot_counties = rng.choice(unique_counties, size=len(unique_counties), replace=True)

        # Build bootstrap sample
        boot_idx = []
        for county in boot_counties:
            county_idx = np.where(groups.values == county)[0]
            boot_idx.extend(county_idx)
        boot_idx = np.array(boot_idx)

        X_boot = X.iloc[boot_idx].reset_index(drop=True)
        y_boot = y.iloc[boot_idx].reset_index(drop=True)
        g_boot = groups.iloc[boot_idx].reset_index(drop=True)

        try:
            preds, fold_maes = _get_oof_predictions(
                X_boot, y_boot, g_boot, build_best_model, FULL_FEATURES,
                use_spatial=True, n_splits=5)

            valid = ~np.isnan(preds)
            if valid.sum() < 50:
                continue

            y_v = y_boot[valid].values
            p_v = preds[valid]

            boot_maes.append(np.mean(np.abs(y_v - p_v)))

            y_hra = (y_v >= HRA_THRESHOLD).astype(int)
            pred_hra = (p_v >= HRA_THRESHOLD).astype(int)
            boot_f1s.append(f1_score(y_hra, pred_hra, zero_division=0))
            boot_precisions.append(precision_score(y_hra, pred_hra, zero_division=0))
            boot_recalls.append(recall_score(y_hra, pred_hra, zero_division=0))

            # Feature importance from a fit on the full bootstrap sample
            model, features = build_best_model()
            available = [f for f in features if f in X_boot.columns]
            model.fit(X_boot[available].fillna(0), y_boot)
            imp = dict(zip(available, model.feature_importances_))
            granite_till_importances.append(imp.get('granite_x_till', 0))

        except Exception as e:
            print(f"  Boot {i} failed: {e}")
            continue

        if (i + 1) % 10 == 0:
            print(f"  Completed {i+1}/{n_boot} bootstrap iterations")

    boot_maes = np.array(boot_maes)
    boot_f1s = np.array(boot_f1s)
    boot_precisions = np.array(boot_precisions)
    boot_recalls = np.array(boot_recalls)
    granite_till_importances = np.array(granite_till_importances)

    print(f"\n  Bootstrap results ({len(boot_maes)} successful iterations):")
    print(f"  MAE:       {boot_maes.mean():.2f} (95% CI: [{np.percentile(boot_maes, 2.5):.2f}, {np.percentile(boot_maes, 97.5):.2f}])")
    print(f"  F1:        {boot_f1s.mean():.3f} (95% CI: [{np.percentile(boot_f1s, 2.5):.3f}, {np.percentile(boot_f1s, 97.5):.3f}])")
    print(f"  Precision: {boot_precisions.mean():.3f} (95% CI: [{np.percentile(boot_precisions, 2.5):.3f}, {np.percentile(boot_precisions, 97.5):.3f}])")
    print(f"  Recall:    {boot_recalls.mean():.3f} (95% CI: [{np.percentile(boot_recalls, 2.5):.3f}, {np.percentile(boot_recalls, 97.5):.3f}])")
    if len(granite_till_importances) > 0:
        print(f"  Granite-till importance: {granite_till_importances.mean():.4f} (95% CI: [{np.percentile(granite_till_importances, 2.5):.4f}, {np.percentile(granite_till_importances, 97.5):.4f}])")

    return {
        'mae': (boot_maes.mean(), np.percentile(boot_maes, 2.5), np.percentile(boot_maes, 97.5)),
        'f1': (boot_f1s.mean(), np.percentile(boot_f1s, 2.5), np.percentile(boot_f1s, 97.5)),
        'precision': (boot_precisions.mean(), np.percentile(boot_precisions, 2.5), np.percentile(boot_precisions, 97.5)),
        'recall': (boot_recalls.mean(), np.percentile(boot_recalls, 2.5), np.percentile(boot_recalls, 97.5)),
        'granite_till': (granite_till_importances.mean(), np.percentile(granite_till_importances, 2.5), np.percentile(granite_till_importances, 97.5)),
    }


def experiment_ablation(X, y, groups):
    """Experiment 6: Granite-till interaction ablation and feature subset analysis."""
    print("\n" + "="*70)
    print("EXPERIMENT 6: Feature Ablation (Granite-Till and Radiometric Features)")
    print("="*70)

    # Count granite-till observations
    if 'granite_x_till' in X.columns:
        n_gt = (X['granite_x_till'] == 1).sum()
        print(f"\n  Grid squares with granite AND till: {n_gt} / {len(X)} ({n_gt/len(X)*100:.1f}%)")
        gt_mask = X['granite_x_till'] == 1
        print(f"  Their mean radon %: {y[gt_mask].mean():.1f}% vs overall mean {y.mean():.1f}%")
        print(f"  Their median radon %: {y[gt_mask].median():.1f}% vs overall median {y.median():.1f}%")

    # Ablation: full vs without granite-till interaction
    configs = {
        'Full model': FULL_FEATURES,
        'Without granite_x_till': [f for f in FULL_FEATURES if f != 'granite_x_till'],
        'Without all interactions': ENHANCED_FEATURES + [f for f in FULL_FEATURES if f not in INTERACTION_FEATURES and f not in ENHANCED_FEATURES],
        'Without radiometric features': [f for f in FULL_FEATURES if not f.startswith('eU') and not f.startswith('eTh') and not f.startswith('K_') and not f.startswith('log_eU') and not f.startswith('total_dose') and 'x_granite' not in f and 'x_limestone' not in f and 'x_shale' not in f and 'x_peat' not in f and 'x_gravel' not in f and 'x_till' not in f],
        'Only radiometric features': [f for f in FULL_FEATURES if f.startswith('eU') or f.startswith('eTh') or f.startswith('K_') or f.startswith('log_eU') or f.startswith('total_dose')],
    }

    print(f"\n  {'Configuration':<35} {'n_feat':>7} {'MAE':>8} {'F1':>8}")
    print("  " + "-" * 58)

    for name, features in configs.items():
        preds, fold_maes = _get_oof_predictions(X, y, groups, build_best_model, features)
        valid = ~np.isnan(preds)
        y_v = y[valid].values
        p_v = preds[valid]
        mae = np.mean(np.abs(y_v - p_v))
        y_hra = (y_v >= HRA_THRESHOLD).astype(int)
        pred_hra = (p_v >= HRA_THRESHOLD).astype(int)
        f1 = f1_score(y_hra, pred_hra, zero_division=0)
        n_used = len([f for f in features if f in X.columns])
        print(f"  {name:<35} {n_used:>7} {mae:>8.2f} {f1:>8.3f}")


def experiment_county_calibration(X, y, groups):
    """Experiment 7: County-level calibration plots."""
    print("\n" + "="*70)
    print("EXPERIMENT 7: County-Level Calibration")
    print("="*70)

    all_preds, _ = _get_oof_predictions(X, y, groups, build_best_model, FULL_FEATURES)

    valid = ~np.isnan(all_preds)
    y_val = y[valid].values
    p_val = all_preds[valid]
    g_val = groups[valid].values

    counties = sorted(set(g_val))
    county_stats = []
    for county in counties:
        mask = g_val == county
        if mask.sum() < 3:
            continue
        actual = y_val[mask]
        predicted = p_val[mask]
        mae = np.mean(np.abs(actual - predicted))
        bias = np.mean(predicted - actual)  # positive = overprediction
        n_hra_actual = (actual >= HRA_THRESHOLD).sum()
        n_hra_pred = (predicted >= HRA_THRESHOLD).sum()
        county_stats.append({
            'county': county,
            'n': mask.sum(),
            'mean_actual': actual.mean(),
            'mean_pred': predicted.mean(),
            'mae': mae,
            'bias': bias,
            'n_hra_actual': n_hra_actual,
            'n_hra_pred': n_hra_pred,
        })

    cdf = pd.DataFrame(county_stats).sort_values('mae', ascending=False)
    print(f"\n{'County':<15} {'n':>4} {'Actual':>8} {'Pred':>8} {'MAE':>8} {'Bias':>8} {'HRA act':>8} {'HRA pred':>9}")
    print("-" * 78)
    for _, row in cdf.iterrows():
        print(f"{row['county']:<15} {row['n']:>4} {row['mean_actual']:>8.1f} {row['mean_pred']:>8.1f} {row['mae']:>8.1f} {row['bias']:>8.1f} {row['n_hra_actual']:>8} {row['n_hra_pred']:>9}")

    # County calibration plot
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(cdf['mean_actual'], cdf['mean_pred'],
               s=cdf['n'] * 5, alpha=0.7, color=CB_BLUE, edgecolor='white',
               linewidth=1, zorder=3)
    for _, row in cdf.iterrows():
        ax.annotate(row['county'], (row['mean_actual'], row['mean_pred']),
                    textcoords='offset points', xytext=(5, 5), fontsize=8, color='gray')

    lim = max(cdf['mean_actual'].max(), cdf['mean_pred'].max()) * 1.1
    ax.plot([0, lim], [0, lim], '--', color=CB_BLACK, linewidth=1.5, alpha=0.5,
            label='Perfect calibration')
    ax.set_xlabel('Mean actual % homes above 200 Bq/m\u00b3')
    ax.set_ylabel('Mean predicted % homes above 200 Bq/m\u00b3')
    ax.set_title('County-Level Calibration\n(Each point = one county, size = # grid squares)')
    ax.legend(loc='upper left')

    fig.savefig(PLOTS_DIR / 'county_calibration.png')
    plt.close(fig)
    print("  -> county_calibration.png")

    return cdf


def experiment_high_radon_underprediction(X, y, groups):
    """Experiment 8: Detailed analysis of systematic underprediction of high-radon areas."""
    print("\n" + "="*70)
    print("EXPERIMENT 8: Systematic Underprediction of High-Radon Areas")
    print("="*70)

    all_preds, _ = _get_oof_predictions(X, y, groups, build_best_model, FULL_FEATURES)

    valid = ~np.isnan(all_preds)
    y_val = y[valid].values
    p_val = all_preds[valid]

    # Analyze by actual radon level bins
    level_bins = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 55)]
    print(f"\n{'Actual range':<15} {'n':>5} {'Mean actual':>12} {'Mean pred':>10} {'Mean bias':>10} {'Miss rate':>10}")
    print("-" * 62)
    for lo, hi in level_bins:
        mask = (y_val >= lo) & (y_val < hi)
        if mask.sum() > 0:
            actual = y_val[mask]
            predicted = p_val[mask]
            bias = (predicted - actual).mean()
            # For HRA: how many predicted below threshold
            if lo >= HRA_THRESHOLD:
                miss_rate = (predicted < HRA_THRESHOLD).mean()
            else:
                miss_rate = float('nan')
            print(f"{lo}-{hi}%{'':<10} {mask.sum():>5} {actual.mean():>12.1f} {predicted.mean():>10.1f} {bias:>10.1f} {miss_rate:>10.2f}" if not np.isnan(miss_rate) else
                  f"{lo}-{hi}%{'':<10} {mask.sum():>5} {actual.mean():>12.1f} {predicted.mean():>10.1f} {bias:>10.1f} {'N/A':>10}")

    # Updated pred_vs_actual plot with bias lines
    fig, ax = plt.subplots(figsize=(10, 9))

    is_hra = y_val >= HRA_THRESHOLD
    ax.scatter(y_val[~is_hra], p_val[~is_hra], alpha=0.35, s=30,
               color=CB_BLUE, label='Non-HRA (<10%)', zorder=2)
    ax.scatter(y_val[is_hra], p_val[is_hra], alpha=0.55, s=40,
               color=CB_RED, label='High Radon Area (>=10%)', zorder=3)

    lim = max(y_val.max(), p_val.max()) * 1.05
    ax.plot([0, lim], [0, lim], '--', color=CB_BLACK, linewidth=1.5,
            alpha=0.6, label='Perfect prediction', zorder=1)

    # HRA threshold lines
    ax.axhline(10, color=CB_ORANGE, linestyle=':', linewidth=1.2, alpha=0.7)
    ax.axvline(10, color=CB_ORANGE, linestyle=':', linewidth=1.2, alpha=0.7,
               label='HRA threshold (10%)')

    # Shade the false-negative quadrant
    ax.fill_between([10, lim], [0, 0], [10, 10],
                    color=CB_RED, alpha=0.08, label='Missed dangerous areas')

    # Stats
    mae = np.mean(np.abs(y_val - p_val))
    corr = np.corrcoef(y_val, p_val)[0, 1]
    y_hra_bin = (y_val >= HRA_THRESHOLD).astype(int)
    pred_hra_bin = (p_val >= HRA_THRESHOLD).astype(int)
    f1 = f1_score(y_hra_bin, pred_hra_bin)
    prec = precision_score(y_hra_bin, pred_hra_bin)
    rec = recall_score(y_hra_bin, pred_hra_bin)

    stats_text = (f'MAE = {mae:.1f}%\n'
                  f'r = {corr:.2f}\n'
                  f'HRA F1 = {f1:.2f}\n'
                  f'Precision = {prec:.2f}\n'
                  f'Recall = {rec:.2f}\n'
                  f'n = {len(y_val)} grid squares')
    ax.text(0.03, 0.97, stats_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor='gray', alpha=0.9))

    ax.set_xlabel('Actual % homes above 200 Bq/m\u00b3')
    ax.set_ylabel('Predicted % homes above 200 Bq/m\u00b3')
    ax.set_title('Predicted vs Actual Radon Risk\n(Spatial CV, county-grouped)')
    ax.legend(loc='lower right', framealpha=0.9, fontsize=11)
    ax.set_xlim(-1, lim)
    ax.set_ylim(-1, lim)

    fig.savefig(PLOTS_DIR / 'pred_vs_actual.png')
    plt.close(fig)
    print("  -> pred_vs_actual.png (updated with precision/recall)")


def main():
    print("Loading dataset...")
    X, y, groups = build_dataset()
    print(f"  {len(X)} samples, {X.shape[1]} features, {groups.nunique()} counties")

    # 1. SHAP
    shap_imp, shap_vals, shap_features = experiment_shap(X, y, groups)

    # 2. Precision/recall
    threshold_df = experiment_precision_recall(X, y, groups)

    # 3. Random CV comparison
    cv_results = experiment_random_cv(X, y, groups)

    # 4. Calibration
    cal_results = experiment_calibration(X, y, groups)

    # 5. Bootstrap (reduced iterations for speed)
    boot_results = experiment_bootstrap(X, y, groups, n_boot=50)

    # 6. Ablation
    experiment_ablation(X, y, groups)

    # 7. County calibration
    county_results = experiment_county_calibration(X, y, groups)

    # 8. Updated pred_vs_actual with underprediction analysis
    experiment_high_radon_underprediction(X, y, groups)

    print("\n" + "="*70)
    print("ALL EXPERIMENTS COMPLETE")
    print("="*70)
    print(f"\nNew plots in {PLOTS_DIR}/:")
    for p in sorted(PLOTS_DIR.glob('*.png')):
        print(f"  {p.name}")


if __name__ == '__main__':
    main()
