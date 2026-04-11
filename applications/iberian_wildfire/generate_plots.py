#!/usr/bin/env python
"""Generate publication-quality plots for the Iberian wildfire VLF prediction project.

Produces 7 PNGs in plots/. All use seaborn-v0_8-whitegrid, colourblind-safe
palettes, 300 DPI, labelled axes, and no annotation collisions.

Usage:
    python generate_plots.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from data_loaders import build_modelling_dataset
from model import (
    DROUGHT_PROXY_FEATURES,
    FWI_PROXY_FEATURES,
    LFMC_PROXY_FEATURES,
    get_baseline_features,
    make_ridge,
    make_xgboost,
)

PLOTS_DIR = HERE / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

RESULTS_PATH = HERE / "results.tsv"
DISCOVERIES_DIR = HERE / "discoveries"

# Colourblind-safe palette (Okabe-Ito inspired)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_GREY = "#999999"

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 14,
    "axes.titlesize": 16,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
})


# ============================================================
# Helpers
# ============================================================

def _load_data() -> pd.DataFrame:
    return build_modelling_dataset()


def _get_holdout_predictions(df: pd.DataFrame, model_factory, features,
                             holdout_year: int = 2025):
    """Train on pre-holdout, predict holdout, return (y_true, y_proba)."""
    avail = [c for c in features if c in df.columns]
    train = df[df["year"] < holdout_year]
    test = df[df["year"] == holdout_year]

    X_train = np.nan_to_num(train[avail].astype("float64").values)
    X_test = np.nan_to_num(test[avail].astype("float64").values)
    y_train = train["vlf"].values
    y_test = test["vlf"].values

    model = model_factory()
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    return y_test, proba, test


# ============================================================
# Plot 1: Headline Finding -- Recent fire activity beats seasonal climatology
# ============================================================

def plot_headline_finding() -> None:
    """Bar chart comparing predictor families by CV AUC (Ridge and XGBoost)."""
    comp_path = DISCOVERIES_DIR / "predictor_comparison.csv"
    comp = pd.read_csv(comp_path)

    # Reorder: show core 3 families + full baseline
    order = ["FWI_proxy", "Drought_proxy", "LFMC_proxy", "Baseline_full"]
    comp = comp.set_index("config").reindex(order).reset_index()

    labels = {
        "FWI_proxy": "Seasonal\nclimatology",
        "Drought_proxy": "Cumulative\nstress",
        "LFMC_proxy": "Recent fire\nactivity",
        "Baseline_full": "Full baseline\n(26 features)",
    }

    # Also load XGBoost comparison
    xgb_path = DISCOVERIES_DIR / "predictor_comparison_xgb.csv"
    xgb_comp = pd.read_csv(xgb_path)
    xgb_comp = xgb_comp.set_index("config").reindex(order).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    x = np.arange(len(comp))
    width = 0.35

    colors = [CB_BLUE, CB_GREEN, CB_ORANGE, CB_GREY]

    # Ridge panel
    bars1 = ax1.bar(x - width / 2, comp["cv_auc"], width, label="CV AUC",
                    color=colors, alpha=0.8, edgecolor="black", linewidth=0.5)
    bars2 = ax1.bar(x + width / 2, comp["holdout_auc"], width, label="2025 Holdout",
                    color=colors, alpha=0.4, edgecolor="black", linewidth=0.5,
                    hatch="//")
    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., h + 0.005,
                 f"{h:.3f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., h + 0.005,
                 f"{h:.3f}", ha="center", va="bottom", fontsize=9)

    ax1.set_xticks(x)
    ax1.set_xticklabels([labels.get(c, c) for c in comp["config"]], fontsize=10)
    ax1.set_ylabel("AUC")
    ax1.set_title("Ridge Logistic Regression")
    ax1.set_ylim(0.65, 1.08)
    ax1.legend(loc="lower left", fontsize=10)

    # XGBoost panel
    bars3 = ax2.bar(x - width / 2, xgb_comp["cv_auc"], width, label="CV AUC",
                    color=colors, alpha=0.8, edgecolor="black", linewidth=0.5)
    bars4 = ax2.bar(x + width / 2, xgb_comp["holdout_auc"], width, label="2025 Holdout",
                    color=colors, alpha=0.4, edgecolor="black", linewidth=0.5,
                    hatch="//")
    for bar in bars3:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., h + 0.005,
                 f"{h:.3f}", ha="center", va="bottom", fontsize=9)
    for bar in bars4:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., h + 0.005,
                 f"{h:.3f}", ha="center", va="bottom", fontsize=9)

    ax2.set_xticks(x)
    ax2.set_xticklabels([labels.get(c, c) for c in xgb_comp["config"]], fontsize=10)
    ax2.set_title("XGBoost (depth=4)")
    ax2.legend(loc="lower left", fontsize=10)

    fig.suptitle("Predictor Family Comparison for VLF Week Classification",
                 fontsize=16, y=1.02)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "headline_finding.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'headline_finding.png'}")


# ============================================================
# Plot 2: Tournament Comparison (Phase 1)
# ============================================================

def plot_tournament_comparison() -> None:
    """Grouped bar chart of tournament models."""
    results = pd.read_csv(RESULTS_PATH, sep="\t")
    tournament = results[results["exp_id"].str.startswith("T")].copy()
    tournament = tournament.sort_values("cv_auc", ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(tournament))
    width = 0.35

    ax.bar(x - width / 2, tournament["cv_auc"], width, label="Temporal CV AUC",
           color=CB_BLUE, alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.bar(x + width / 2, tournament["holdout_auc"], width, label="2025 Holdout AUC",
           color=CB_ORANGE, alpha=0.8, edgecolor="black", linewidth=0.5)

    # Value labels
    for i, (_, row) in enumerate(tournament.iterrows()):
        ax.text(i - width / 2, row["cv_auc"] + 0.002,
                f"{row['cv_auc']:.3f}", ha="center", va="bottom", fontsize=9)
        ax.text(i + width / 2, row["holdout_auc"] + 0.002,
                f"{row['holdout_auc']:.3f}", ha="center", va="bottom", fontsize=9)

    model_labels = {
        "ridge": "Ridge\n(Logistic L2)",
        "xgboost": "XGBoost\n(depth=4)",
        "xgboost_deep": "XGBoost\n(depth=6)",
        "extratrees": "ExtraTrees",
        "randomforest": "Random\nForest",
        "lightgbm": "LightGBM",
    }
    ax.set_xticks(x)
    ax.set_xticklabels(
        [model_labels.get(row["model"], row["model"])
         for _, row in tournament.iterrows()],
        fontsize=10,
    )
    ax.set_ylabel("AUC")
    ax.set_title("Model Tournament: VLF Week Classification (Full Baseline Features)")
    ax.set_ylim(0.9, 1.01)
    ax.legend(loc="lower left")

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "tournament_comparison.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'tournament_comparison.png'}")


# ============================================================
# Plot 3: Feature Importance (top 15)
# ============================================================

def plot_feature_importance() -> None:
    """Horizontal bar chart of top 15 features by standardized importance."""
    fi_path = DISCOVERIES_DIR / "feature_importance.csv"
    df = pd.read_csv(fi_path)
    df = df.sort_values("standardized_importance", ascending=False).head(15).copy()
    df = df.sort_values("standardized_importance", ascending=True)

    # Classify features
    activity_keywords = ["ratio", "lag1", "lag2", "_2wk"]
    seasonal_keywords = ["avg", "max", "log_", "season"]
    cumulative_keywords = ["cum_", "year_trend"]

    def classify(name):
        if any(kw in name for kw in activity_keywords):
            return "activity"
        if any(kw in name for kw in cumulative_keywords):
            return "cumulative"
        return "seasonal"

    categories = [classify(f) for f in df["feature"]]
    cat_colors = {"seasonal": CB_BLUE, "activity": CB_ORANGE, "cumulative": CB_GREEN}
    colors = [cat_colors[c] for c in categories]

    name_map = {
        "area_ha_avg": "Hist. avg burned area",
        "area_ratio": "Area vs historical average",
        "area_ha_max": "Hist. max burned area",
        "log_area_avg": "log(Hist. avg area)",
        "fires_avg": "Hist. avg fire count",
        "fire_season_week": "Week in fire season",
        "fires_ratio": "Fires vs historical average",
        "area_lag1": "Prev. week burned area",
        "area_2wk": "2-week burned area",
        "fires_max": "Hist. max fire count",
        "fires_4wk": "4-week fire count",
        "area_4wk": "4-week burned area",
        "area_lag2": "2-week-ago burned area",
        "cum_fires_ytd": "Year-to-date fire count",
        "fires_2wk": "2-week fire count",
    }
    labels = [name_map.get(f, f) for f in df["feature"]]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(df)), df["standardized_importance"].values, color=colors,
            edgecolor="black", linewidth=0.5)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("Standardized coefficient importance")
    ax.set_title("Top 15 Predictors of Very Large Fire Weeks (Ridge Logistic)")

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_BLUE, label="Seasonal climatology"),
        Patch(facecolor=CB_ORANGE, label="Recent fire activity"),
        Patch(facecolor=CB_GREEN, label="Cumulative season stress"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "feature_importance.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'feature_importance.png'}")


# ============================================================
# Plot 4: Seasonal VLF Risk Profile
# ============================================================

def plot_seasonal_risk(df: pd.DataFrame) -> None:
    """Line plot of VLF probability across the fire season by country."""
    risk = df.copy()

    # Train on 2012-2023, predict all
    features = get_baseline_features()
    avail = [c for c in features if c in df.columns]
    train = df[df["year"] <= 2023]
    X_train = np.nan_to_num(train[avail].astype("float64").values)
    y_train = train["vlf"].values

    model = make_ridge()
    model.fit(X_train, y_train)
    risk["vlf_prob"] = model.predict_proba(
        np.nan_to_num(df[avail].astype("float64").values)
    )[:, 1]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for ax, country, cname, color in [
        (axes[0], "PRT", "Portugal", CB_ORANGE),
        (axes[1], "ESP", "Spain", CB_BLUE),
    ]:
        c_data = risk[risk["country"] == country]
        seasonal = c_data.groupby("week").agg(
            mean_prob=("vlf_prob", "mean"),
            vlf_rate=("vlf", "mean"),
        ).reset_index()

        ax.fill_between(seasonal["week"], seasonal["mean_prob"],
                        alpha=0.3, color=color, label="Predicted VLF risk")
        ax.plot(seasonal["week"], seasonal["mean_prob"], color=color, linewidth=2)
        ax.scatter(seasonal["week"], seasonal["vlf_rate"], color=CB_RED,
                   s=30, zorder=5, label="Observed VLF rate")
        ax.set_xlabel("Week of year")
        ax.set_title(f"{cname}")
        ax.legend(loc="upper left", fontsize=10)
        ax.set_xlim(15, 48)

    axes[0].set_ylabel("VLF probability / rate")
    fig.suptitle("Seasonal Very Large Fire Risk Profile (2012-2025)",
                 fontsize=16, y=1.02)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "seasonal_risk.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'seasonal_risk.png'}")


# ============================================================
# Plot 5: ROC Curves for 2025 Holdout
# ============================================================

def plot_holdout_roc(df: pd.DataFrame) -> None:
    """ROC curves for multiple models on the 2025 holdout year."""
    features = get_baseline_features()

    configs = [
        ("Ridge (baseline)", make_ridge, features, CB_BLUE),
        ("XGBoost (depth=4)", make_xgboost, features, CB_ORANGE),
        ("Ridge (recent activity)", make_ridge, LFMC_PROXY_FEATURES, CB_GREEN),
        ("Ridge (seasonal clim.)", make_ridge, FWI_PROXY_FEATURES, CB_PURPLE),
    ]

    fig, ax = plt.subplots(figsize=(10, 8))

    for name, factory, feats, color in configs:
        y_true, y_proba, _ = _get_holdout_predictions(df, factory, feats)
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        auc_val = roc_auc_score(y_true, y_proba)
        ax.plot(fpr, tpr, color=color, linewidth=2,
                label=f"{name} (AUC={auc_val:.3f})")

    ax.plot([0, 1], [0, 1], "--", color="grey", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: 2025 Holdout Year\n(Trained on 2012-2024, N=68)")
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "holdout_roc.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'holdout_roc.png'}")


# ============================================================
# Plot 6: Threshold Sensitivity
# ============================================================

def plot_threshold_sensitivity() -> None:
    """Line plot showing AUC across different VLF thresholds."""
    thresh_path = DISCOVERIES_DIR / "threshold_sensitivity.csv"
    df = pd.read_csv(thresh_path)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df["threshold"], df["lfmc_auc"], "o-", color=CB_ORANGE,
            linewidth=2, markersize=8, label="Recent fire activity")
    ax.plot(df["threshold"], df["full_auc"], "s-", color=CB_GREY,
            linewidth=2, markersize=8, label="Full baseline")
    ax.plot(df["threshold"], df["fwi_auc"], "^-", color=CB_BLUE,
            linewidth=2, markersize=8, label="Seasonal climatology")

    # Persistence baseline reference
    ax.axhline(y=0.814, color=CB_RED, linestyle="--", linewidth=1.5,
               label="Persistence baseline (area_lag1)")

    ax.set_xlabel("VLF Threshold (hectares)")
    ax.set_ylabel("Ridge CV AUC")
    ax.set_title("Threshold Sensitivity: Predictor Family Comparison")
    ax.legend(loc="center left", fontsize=11)
    ax.set_xscale("log")
    ax.set_xticks(df["threshold"])
    ax.get_xaxis().set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{int(x):,}"))
    ax.set_ylim(0.65, 1.02)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "threshold_sensitivity.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'threshold_sensitivity.png'}")


# ============================================================
# Plot 7: Persistence Analysis
# ============================================================

def plot_persistence_analysis(df: pd.DataFrame) -> None:
    """Stacked bar showing onset vs persistence VLF weeks by year."""
    df2 = df.sort_values(["country", "year", "week"]).reset_index(drop=True)
    df2["vlf_prev"] = df2.groupby("country")["vlf"].shift(1).fillna(0)
    df2["vlf_onset"] = ((df2["vlf"] == 1) & (df2["vlf_prev"] == 0)).astype(int)
    df2["vlf_persist"] = ((df2["vlf"] == 1) & (df2["vlf_prev"] == 1)).astype(int)

    yearly = df2.groupby("year").agg(
        onset=("vlf_onset", "sum"),
        persist=("vlf_persist", "sum"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(yearly))
    width = 0.6

    ax.bar(x, yearly["onset"], width, label="VLF onset (new)",
           color=CB_ORANGE, edgecolor="black", linewidth=0.5)
    ax.bar(x, yearly["persist"], width, bottom=yearly["onset"],
           label="VLF persistence (continuing)", color=CB_BLUE, alpha=0.6,
           edgecolor="black", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(yearly["year"], rotation=45)
    ax.set_ylabel("Number of VLF country-weeks")
    ax.set_title("VLF Onset vs. Persistence by Year\n(47% of VLF weeks are persistence events)")
    ax.legend(loc="upper left")

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "persistence_analysis.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'persistence_analysis.png'}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", message=".*lbfgs.*")
    warnings.filterwarnings("ignore", message=".*penalty.*deprecated.*")
    warnings.filterwarnings("ignore", message=".*ConvergenceWarning.*")
    print("Generating plots for Iberian wildfire VLF prediction project...")

    print("\n[1/7] Loading data...")
    df = _load_data()
    print(f"  {len(df)} rows, VLF rate={df['vlf'].mean():.1%}")

    print("\n[2/7] Headline finding (predictor comparison)...")
    plot_headline_finding()

    print("\n[3/7] Tournament comparison...")
    plot_tournament_comparison()

    print("\n[4/7] Feature importance...")
    plot_feature_importance()

    print("\n[5/7] Seasonal risk profile...")
    plot_seasonal_risk(df)

    print("\n[6/7] Holdout ROC curves...")
    plot_holdout_roc(df)

    print("\n[7/7] Threshold sensitivity & persistence...")
    plot_threshold_sensitivity()
    plot_persistence_analysis(df)

    print(f"\nAll plots saved to {PLOTS_DIR}/")
    for p in sorted(PLOTS_DIR.glob("*.png")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
