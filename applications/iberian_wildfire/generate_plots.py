#!/usr/bin/env python
"""Generate publication-quality plots for the Iberian wildfire VLF prediction project.

Produces 5 PNGs in plots/. All use seaborn-v0_8-whitegrid, colourblind-safe
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
# Plot 1: Headline Finding -- LFMC proxy beats FWI proxy
# ============================================================

def plot_headline_finding() -> None:
    """Bar chart comparing predictor families by CV AUC.

    Shows that recent fire activity dynamics (LFMC proxy) outperforms
    historical fire danger patterns (FWI proxy) for VLF prediction.
    """
    comp_path = DISCOVERIES_DIR / "predictor_comparison.csv"
    comp = pd.read_csv(comp_path)

    # Reorder for presentation
    order = ["FWI_proxy", "Drought_proxy", "LFMC_proxy",
             "FWI+LFMC", "FWI+Drought", "LFMC+Drought",
             "All_three", "Baseline_full"]
    comp = comp.set_index("config").reindex(order).reset_index()

    labels = {
        "FWI_proxy": "Fire weather\n(historical patterns)",
        "Drought_proxy": "Drought\n(cumulative stress)",
        "LFMC_proxy": "Fuel moisture proxy\n(recent fire dynamics)",
        "FWI+LFMC": "Weather +\nFuel moisture",
        "FWI+Drought": "Weather +\nDrought",
        "LFMC+Drought": "Fuel moisture +\nDrought",
        "All_three": "All three\ncombined",
        "Baseline_full": "Full baseline\n(26 features)",
    }

    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.arange(len(comp))
    width = 0.35

    # Color: LFMC-family = orange, FWI-family = blue, combos = green
    colors_cv = []
    colors_ho = []
    for c in comp["config"]:
        if "LFMC" in c and "FWI" not in c and "Drought" not in c:
            colors_cv.append(CB_ORANGE)
            colors_ho.append(CB_ORANGE)
        elif "FWI" in c and "LFMC" not in c and "Drought" not in c:
            colors_cv.append(CB_BLUE)
            colors_ho.append(CB_BLUE)
        else:
            colors_cv.append(CB_GREEN)
            colors_ho.append(CB_GREEN)

    bars1 = ax.bar(x - width / 2, comp["cv_auc"], width, label="Temporal CV AUC",
                   color=colors_cv, alpha=0.8, edgecolor="black", linewidth=0.5)
    bars2 = ax.bar(x + width / 2, comp["holdout_auc"], width, label="2025 Holdout AUC",
                   color=colors_ho, alpha=0.4, edgecolor="black", linewidth=0.5,
                   hatch="//")

    # Value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.005,
                f"{height:.3f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.005,
                f"{height:.3f}", ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("")
    ax.set_ylabel("AUC")
    ax.set_title("Which Predictor Family Best Identifies\nVery Large Fire Weeks on the Iberian Peninsula?")
    ax.set_xticks(x)
    ax.set_xticklabels([labels.get(c, c) for c in comp["config"]], fontsize=10)
    ax.set_ylim(0.65, 1.05)
    ax.legend(loc="lower left", fontsize=12)

    # Annotation -- positioned below the bars to avoid overlaps
    ax.text(
        0.02, 0.03,
        "Fuel moisture proxy alone (AUC 0.952)\noutperforms fire weather (AUC 0.809)",
        transform=ax.transAxes, fontsize=11, va="bottom", ha="left",
        color=CB_ORANGE, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor=CB_ORANGE, alpha=0.9),
    )

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
    ax.set_title("Phase 1 Tournament: Model Comparison for VLF Prediction")
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
    lfmc_keywords = ["ratio", "lag1", "lag2", "_2wk"]
    fwi_keywords = ["avg", "max", "log_", "season"]
    drought_keywords = ["cum_", "year_trend"]

    def classify(name):
        if any(kw in name for kw in lfmc_keywords):
            return "lfmc"
        if any(kw in name for kw in drought_keywords):
            return "drought"
        return "fwi"

    categories = [classify(f) for f in df["feature"]]
    cat_colors = {"fwi": CB_BLUE, "lfmc": CB_ORANGE, "drought": CB_GREEN}
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
        Patch(facecolor=CB_BLUE, label="Fire weather (historical patterns)"),
        Patch(facecolor=CB_ORANGE, label="Fuel moisture proxy (recent activity)"),
        Patch(facecolor=CB_GREEN, label="Drought (cumulative stress)"),
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
        ("Ridge (LFMC proxy only)", make_ridge, LFMC_PROXY_FEATURES, CB_GREEN),
        ("Ridge (FWI proxy only)", make_ridge, FWI_PROXY_FEATURES, CB_PURPLE),
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
    ax.set_title("ROC Curves: 2025 Holdout Year\n(Trained on 2012-2024)")
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "holdout_roc.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'holdout_roc.png'}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", message=".*lbfgs.*")
    warnings.filterwarnings("ignore", message=".*penalty.*deprecated.*")
    print("Generating plots for Iberian wildfire VLF prediction project...")

    print("\n[1/5] Loading data...")
    df = _load_data()
    print(f"  {len(df)} rows, VLF rate={df['vlf'].mean():.1%}")

    print("\n[2/5] Headline finding (predictor comparison)...")
    plot_headline_finding()

    print("\n[3/5] Tournament comparison...")
    plot_tournament_comparison()

    print("\n[4/5] Feature importance...")
    plot_feature_importance()

    print("\n[5/5] Seasonal risk profile...")
    plot_seasonal_risk(df)

    print("\n[6/5] Holdout ROC curves...")
    plot_holdout_roc(df)

    print(f"\nAll plots saved to {PLOTS_DIR}/")
    for p in sorted(PLOTS_DIR.glob("*.png")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
