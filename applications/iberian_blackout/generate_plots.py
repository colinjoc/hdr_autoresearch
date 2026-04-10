"""
Generate publication-quality plots for the Iberian Blackout HDR project.

Produces five figures in plots/:
  1. pred_vs_actual.png   — ROC curves (ensemble, LR, GBM) from LOO-CV
  2. feature_importance.png — top features by importance (LR + GBM)
  3. headline_finding.png — timeline of ensemble risk score around the blackout
  4. tournament_comparison.png — model family comparison from results.tsv
  5. ablation.png         — ablation study: which feature groups matter
"""
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc, roc_auc_score

# ── project imports ──────────────────────────────────────────────────
from data_loader import build_daily_feature_matrix, compute_grid_stress_indicators
from evaluate import label_blackout_risk
from model import CascadeRiskModel

# ── style ────────────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
# Colourblind-safe palette (Tol bright)
CB_PALETTE = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"]
DPI = 300

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")
RESULTS_TSV = os.path.join(PROJECT_DIR, "results.tsv")


def _ensure_plots_dir():
    os.makedirs(PLOTS_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────
# Helper: get LOO-CV predictions for all three models
# ─────────────────────────────────────────────────────────────────────
def _loo_cv_predictions():
    """Return (y_true, y_prob_lr, y_prob_gbm, y_prob_ensemble, feature_names, X_scaled, y)."""
    features = build_daily_feature_matrix(DATA_DIR)
    labels = label_blackout_risk(features)

    m = CascadeRiskModel("logistic")
    X = m._build_features(features)
    common_idx = X.index.intersection(labels.index)
    X = X.loc[common_idx]
    y = labels.loc[common_idx]
    valid = X.notna().all(axis=1) & y.notna()
    X = X[valid]
    y = y[valid]
    X_numeric = X.select_dtypes(include=[np.number])
    feature_names = list(X_numeric.columns)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_numeric)

    loo = LeaveOneOut()
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42, C=1.0)
    gbm = GradientBoostingClassifier(n_estimators=50, max_depth=2, learning_rate=0.1, random_state=42)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y_prob_lr = cross_val_predict(lr, X_scaled, y, cv=loo, method="predict_proba")[:, 1]
        y_prob_gbm = cross_val_predict(gbm, X_scaled, y, cv=loo, method="predict_proba")[:, 1]

    y_prob_ensemble = (y_prob_lr + y_prob_gbm) / 2.0

    return y.values, y_prob_lr, y_prob_gbm, y_prob_ensemble, feature_names, X_scaled, y.index


# ─────────────────────────────────────────────────────────────────────
# Plot 1: ROC curves
# ─────────────────────────────────────────────────────────────────────
def plot_roc_curves(y_true, y_prob_lr, y_prob_gbm, y_prob_ensemble):
    """ROC curve for ensemble, LR, and GBM with AUC annotations."""
    fig, ax = plt.subplots(figsize=(6, 6))

    for probs, label, color, ls in [
        (y_prob_ensemble, "Ensemble (LR+GBM)", CB_PALETTE[0], "-"),
        (y_prob_lr, "Logistic Regression", CB_PALETTE[1], "--"),
        (y_prob_gbm, "GBM", CB_PALETTE[2], "-."),
    ]:
        fpr, tpr, _ = roc_curve(y_true, probs)
        auc_val = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, linestyle=ls, linewidth=2,
                label=f"{label} (AUC = {auc_val:.3f})")

    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, alpha=0.5, label="Random classifier")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curves — LOO-CV on 94 Days (8 Positive)", fontsize=13)
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "pred_vs_actual.png"), dpi=DPI,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────
# Plot 2: Feature importance
# ─────────────────────────────────────────────────────────────────────
def plot_feature_importance():
    """Horizontal bar chart of feature importances from both LR and GBM."""
    features = build_daily_feature_matrix(DATA_DIR)
    labels = label_blackout_risk(features)

    model_lr = CascadeRiskModel("logistic")
    model_lr.fit(features, labels)
    imp_lr = model_lr.feature_importance()

    model_gbm = CascadeRiskModel("gbm")
    model_gbm.fit(features, labels)
    imp_gbm = model_gbm.feature_importance()

    # Normalize each to [0, 1] for comparison
    imp_lr_norm = imp_lr / imp_lr.max() if imp_lr.max() > 0 else imp_lr
    imp_gbm_norm = imp_gbm / imp_gbm.max() if imp_gbm.max() > 0 else imp_gbm

    # Combine into a DataFrame for side-by-side bars
    all_features = imp_lr_norm.index.union(imp_gbm_norm.index)
    df = pd.DataFrame({
        "Logistic Regression": imp_lr_norm.reindex(all_features).fillna(0),
        "Gradient Boosting": imp_gbm_norm.reindex(all_features).fillna(0),
    })
    df["avg"] = df.mean(axis=1)
    df = df.sort_values("avg", ascending=True)

    # Take top 12
    df = df.tail(12)

    # Prettify feature names
    rename_map = {
        "voltage_stress": "Voltage Stress *",
        "inertia_proxy": "Inertia Proxy",
        "reactive_gap": "Reactive Power Gap *",
        "solar_x_low_sync": "Solar x Low Sync *",
        "reactive_x_export": "Reactive x Export *",
        "composite_risk_score": "Composite Risk Score",
        "renewable_fraction": "Renewable Fraction",
        "solar_fraction": "Solar Fraction *",
        "sync_fraction": "Synchronous Fraction",
        "excess_gen_ratio": "Excess Generation Ratio *",
        "export_fraction": "Export Fraction *",
        "has_negative_price": "Negative Price Flag *",
        "price_floor_EUR": "Price Floor",
        "price_mean_EUR": "Mean Price",
        "demand_cv": "Demand Variability",
        "total_net_export_MWh": "Net Export Volume",
        "day_of_week": "Day of Week",
        "is_weekend": "Weekend",
    }
    df.index = [rename_map.get(f, f) for f in df.index]

    fig, ax = plt.subplots(figsize=(9, 6))
    y_pos = np.arange(len(df))
    bar_height = 0.35

    ax.barh(y_pos + bar_height / 2, df["Logistic Regression"], bar_height,
            label="Logistic Regression (|coef|)", color=CB_PALETTE[1], alpha=0.85)
    ax.barh(y_pos - bar_height / 2, df["Gradient Boosting"], bar_height,
            label="Gradient Boosting (impurity)", color=CB_PALETTE[2], alpha=0.85)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df.index, fontsize=10)
    ax.set_xlabel("Normalized Importance", fontsize=12)
    ax.set_title("Feature Importance — Top 12 Features\n(* = voltage stress indicator)", fontsize=13)
    ax.legend(loc="lower right", fontsize=10)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=DPI,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────
# Plot 3: Headline finding — timeline around April 28
# ─────────────────────────────────────────────────────────────────────
def plot_headline_finding():
    """Timeline of ensemble risk score with the blackout event marked."""
    features = build_daily_feature_matrix(DATA_DIR)
    labels = label_blackout_risk(features)

    # Fit both models on all data
    model_lr = CascadeRiskModel("logistic")
    model_lr.fit(features, labels)
    preds_lr = model_lr.predict(features)

    model_gbm = CascadeRiskModel("gbm")
    model_gbm.fit(features, labels)
    preds_gbm = model_gbm.predict(features)

    # Ensemble
    ensemble_risk = (preds_lr["risk_score"] + preds_gbm["risk_score"]) / 2.0

    # Focus on March-May 2025 for visibility
    start = pd.Timestamp("2025-03-01", tz="UTC")
    end = pd.Timestamp("2025-05-04", tz="UTC")
    mask = (ensemble_risk.index >= start) & (ensemble_risk.index <= end)
    risk_window = ensemble_risk[mask]
    labels_window = labels.reindex(risk_window.index).fillna(0)

    # Dates for x-axis
    dates = risk_window.index

    fig, ax = plt.subplots(figsize=(12, 5))

    # Risk score line
    ax.plot(dates, risk_window.values, color=CB_PALETTE[0], linewidth=2,
            label="Ensemble risk score", zorder=3)

    # Fill high-risk zone
    ax.fill_between(dates, 0, risk_window.values,
                    where=risk_window.values > 0.45,
                    color=CB_PALETTE[1], alpha=0.25, label="Risk > 0.45 (threshold)")

    # Mark labeled high-risk days
    high_risk_dates = dates[labels_window == 1]
    high_risk_scores = risk_window[labels_window == 1]
    ax.scatter(high_risk_dates, high_risk_scores.values,
               color=CB_PALETTE[1], s=80, zorder=5, edgecolors="black",
               linewidths=0.8, label="Labeled high-risk days")

    # Mark April 28 specifically
    blackout_date = pd.Timestamp("2025-04-28", tz="UTC")
    if blackout_date in risk_window.index:
        score_28 = risk_window.loc[blackout_date]
        ax.annotate(
            f"28 April 2025\nBlackout\n(risk = {score_28:.2f})",
            xy=(blackout_date, score_28),
            xytext=(blackout_date - pd.Timedelta(days=12), score_28 - 0.15),
            fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.9),
            zorder=6,
        )

    ax.axhline(0.45, color=CB_PALETTE[3], linestyle="--", linewidth=1, alpha=0.7,
               label="Decision threshold (0.45)")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Ensemble Risk Score", fontsize=12)
    ax.set_title("Cascade Risk Timeline — March to May 2025\nEnsemble (LR + GBM) Predicted Risk",
                 fontsize=13)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

    # Format x-axis dates
    fig.autofmt_xdate(rotation=30)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "headline_finding.png"), dpi=DPI,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────
# Plot 4: Tournament comparison
# ─────────────────────────────────────────────────────────────────────
def plot_tournament_comparison():
    """Grouped bar chart comparing model families from results.tsv."""
    df = pd.read_csv(RESULTS_TSV, sep="\t")

    # Select tournament and key HDR rows
    keep_experiments = [
        "baseline_logistic_stress",
        "tournament_gbm",
        "tournament_et",
        "tournament_svm",
        "tournament_lr_c1",
        "hdr_lr_enhanced",
        "hdr_ensemble_lr_gbm",
    ]
    df = df[df["experiment"].isin(keep_experiments)].copy()
    df = df.set_index("experiment").reindex(keep_experiments)

    # Short labels
    short_labels = {
        "baseline_logistic_stress": "Baseline LR\n(C=0.1)",
        "tournament_gbm": "GBM\n(50, d2)",
        "tournament_et": "ExtraTrees\n(100, d3)",
        "tournament_svm": "SVM\n(RBF)",
        "tournament_lr_c1": "LR\n(C=1.0)",
        "hdr_lr_enhanced": "LR Enhanced\n(18 feat.)",
        "hdr_ensemble_lr_gbm": "Ensemble\n(LR+GBM)",
    }
    df.index = [short_labels.get(e, e) for e in df.index]

    metrics = ["f1", "auc_roc", "precision", "recall"]
    metric_labels = ["F1 Score", "AUC-ROC", "Precision", "Recall"]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df))
    width = 0.18

    for i, (metric, mlabel) in enumerate(zip(metrics, metric_labels)):
        vals = df[metric].values.astype(float)
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, vals, width, label=mlabel,
                      color=CB_PALETTE[i], alpha=0.85, edgecolor="white", linewidth=0.5)
        # Value labels on top
        for bar, val in zip(bars, vals):
            if not np.isnan(val):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{val:.2f}", ha="center", va="bottom", fontsize=7.5, rotation=0)

    ax.set_xticks(x)
    ax.set_xticklabels(df.index, fontsize=9)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Model Tournament — LOO-CV Performance Comparison", fontsize=13)
    ax.legend(loc="lower left", fontsize=10, ncol=2)
    ax.set_ylim(0, 1.15)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "tournament_comparison.png"), dpi=DPI,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────
# Plot 5: Ablation study
# ─────────────────────────────────────────────────────────────────────
def plot_ablation():
    """Horizontal bar chart showing ablation study results."""
    df = pd.read_csv(RESULTS_TSV, sep="\t")

    # Select ablation experiments + the baseline GBM for reference
    ablation_experiments = [
        "tournament_gbm",
        "hdr_rolling_ren7d",
        "hdr_solar_neg_price",
        "hdr_triple_interact",
        "hdr_drop_inertia",
        "hdr_voltage_focus",
        "hdr_rf_enhanced",
        "hdr_et_enhanced",
    ]
    df = df[df["experiment"].isin(ablation_experiments)].copy()
    df = df.set_index("experiment").reindex(ablation_experiments)

    short_labels = {
        "tournament_gbm": "GBM baseline (physics proxies)",
        "hdr_rolling_ren7d": "+Rolling renewable 7d avg",
        "hdr_solar_neg_price": "+Solar x negative price",
        "hdr_triple_interact": "+Triple interaction",
        "hdr_drop_inertia": "-Inertia proxy (removed)",
        "hdr_voltage_focus": "Voltage-focused features only",
        "hdr_rf_enhanced": "RF (enhanced features)",
        "hdr_et_enhanced": "ExtraTrees (enhanced features)",
    }
    df.index = [short_labels.get(e, e) for e in df.index]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

    # F1 scores
    colors_f1 = []
    for exp in ablation_experiments:
        status = pd.read_csv(RESULTS_TSV, sep="\t")
        status = status[status["experiment"] == exp]["status"].values
        s = status[0] if len(status) > 0 else "KEEP"
        if s == "REVERT":
            colors_f1.append(CB_PALETTE[1])  # red
        elif exp == "tournament_gbm":
            colors_f1.append(CB_PALETTE[0])  # blue = reference
        else:
            colors_f1.append(CB_PALETTE[3])  # yellow = tie

    y_pos = np.arange(len(df))

    axes[0].barh(y_pos, df["f1"].values.astype(float), color=colors_f1, alpha=0.85,
                 edgecolor="white", linewidth=0.5)
    axes[0].set_xlabel("F1 Score", fontsize=12)
    axes[0].set_title("Ablation Study — F1 Score", fontsize=12)
    axes[0].set_xlim(0, 1.0)
    for i, val in enumerate(df["f1"].values.astype(float)):
        axes[0].text(val + 0.01, i, f"{val:.3f}", va="center", fontsize=9)

    # AUC-ROC
    colors_auc = colors_f1.copy()
    axes[1].barh(y_pos, df["auc_roc"].values.astype(float), color=colors_auc, alpha=0.85,
                 edgecolor="white", linewidth=0.5)
    axes[1].set_xlabel("AUC-ROC", fontsize=12)
    axes[1].set_title("Ablation Study — AUC-ROC", fontsize=12)
    axes[1].set_xlim(0, 1.0)
    for i, val in enumerate(df["auc_roc"].values.astype(float)):
        axes[1].text(val + 0.01, i, f"{val:.3f}", va="center", fontsize=9)

    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(df.index, fontsize=9)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_PALETTE[0], alpha=0.85, label="Reference (GBM baseline)"),
        Patch(facecolor=CB_PALETTE[3], alpha=0.85, label="TIE (no change)"),
        Patch(facecolor=CB_PALETTE[1], alpha=0.85, label="REVERT (degraded)"),
    ]
    axes[1].legend(handles=legend_elements, loc="lower right", fontsize=9)

    fig.suptitle("Ablation: Feature Group Contributions\n"
                 "Voltage stress features alone match full model; inertia is redundant",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "ablation.png"), dpi=DPI,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────
def main():
    _ensure_plots_dir()
    print("Loading data and computing LOO-CV predictions ...")
    y_true, y_prob_lr, y_prob_gbm, y_prob_ensemble, feat_names, X_scaled, dates = _loo_cv_predictions()

    print("Generating plot 1/5: ROC curves ...")
    plot_roc_curves(y_true, y_prob_lr, y_prob_gbm, y_prob_ensemble)

    print("Generating plot 2/5: Feature importance ...")
    plot_feature_importance()

    print("Generating plot 3/5: Headline finding (timeline) ...")
    plot_headline_finding()

    print("Generating plot 4/5: Tournament comparison ...")
    plot_tournament_comparison()

    print("Generating plot 5/5: Ablation study ...")
    plot_ablation()

    print(f"All plots saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
