"""
generate_plots.py — Create publication-quality figures for the concrete HDR paper.

Outputs (all at 300 DPI, seaborn-v0_8-whitegrid, colourblind-safe palette):
  plots/pred_vs_actual.png    — Predicted vs actual compressive strength scatter
  plots/feature_importance.png — Top feature importances from the winning model
  plots/headline_finding.png  — CO2 vs strength Pareto front with C40 baseline
  plots/co2_comparison.png    — CO2 component breakdown: conventional vs discovered

Usage:
    python generate_plots.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import KFold

# ── Project paths ──
PROJECT_ROOT = Path(__file__).resolve().parent
PLOTS_DIR = PROJECT_ROOT / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

# ── Style setup ──
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
})
# Colourblind-safe palette (Okabe-Ito inspired)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_CYAN = "#56B4E9"
CB_YELLOW = "#F0E442"
CB_BLACK = "#000000"

DPI = 300

# ── CO2 and cost factors (same as evaluate.py) ──
CO2_PER_KG = {
    "cement": 0.90, "slag": 0.07, "fly_ash": 0.01,
    "water": 0.001, "superplasticizer": 1.50,
    "coarse_agg": 0.005, "fine_agg": 0.005,
}

# Column name mapping (same as evaluate.py)
COL_MAP = {
    "Cement (component 1)(kg in a m^3 mixture)": "cement",
    "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": "slag",
    "Fly Ash (component 3)(kg in a m^3 mixture)": "fly_ash",
    "Water  (component 4)(kg in a m^3 mixture)": "water",
    "Superplasticizer (component 5)(kg in a m^3 mixture)": "superplasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": "coarse_agg",
    "Fine Aggregate (component 7)(kg in a m^3 mixture)": "fine_agg",
    "Age (day)": "age",
    "Concrete compressive strength(MPa. megapascals)": "strength",
}

RAW_FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer",
                "coarse_agg", "fine_agg", "age"]
DERIVED_FEATURES = ["wb_ratio", "scm_pct"]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES


def load_dataset() -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "data" / "concrete.csv").rename(columns=COL_MAP)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    binder = out["cement"] + out["slag"] + out["fly_ash"]
    out["wb_ratio"] = (out["water"] / binder.replace(0, np.nan)).fillna(0)
    scm = out["slag"] + out["fly_ash"]
    out["scm_pct"] = (scm / binder.replace(0, np.nan)).fillna(0)
    return out


def get_xgb_params() -> dict:
    """Return the winning model's XGBoost parameters."""
    monotone = [0] * len(FEATURE_NAMES)
    monotone[FEATURE_NAMES.index("cement")] = 1
    return {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "monotone_constraints": "(" + ",".join(str(v) for v in monotone) + ")",
        "verbosity": 0,
    }


def train_full_model(df: pd.DataFrame):
    """Train the winning P25.5 model on the full dataset. Returns (booster, X, y)."""
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["strength"].values.astype(np.float32)
    params = get_xgb_params()
    dtrain = xgb.DMatrix(X, label=y, feature_names=FEATURE_NAMES)
    booster = xgb.train(params, dtrain, num_boost_round=600)
    return booster, X, y


def cross_val_predictions(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """5-fold cross-validation returning (y_true, y_pred) arrays."""
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["strength"].values.astype(np.float32)
    params = get_xgb_params()

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    all_true, all_pred = [], []
    for train_idx, test_idx in kf.split(X):
        dtrain = xgb.DMatrix(X[train_idx], label=y[train_idx])
        dtest = xgb.DMatrix(X[test_idx])
        booster = xgb.train(params, dtrain, num_boost_round=600)
        preds = booster.predict(dtest)
        all_true.extend(y[test_idx].tolist())
        all_pred.extend(preds.tolist())
    return np.array(all_true), np.array(all_pred)


# ── Plot 1: Predicted vs Actual ──

def plot_pred_vs_actual(y_true: np.ndarray, y_pred: np.ndarray):
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(y_true, y_pred, alpha=0.35, s=18, color=CB_BLUE, edgecolors="none",
               label="Test-fold predictions")

    # Perfect-prediction line
    lo = min(y_true.min(), y_pred.min()) - 2
    hi = max(y_true.max(), y_pred.max()) + 2
    ax.plot([lo, hi], [lo, hi], "--", color=CB_RED, linewidth=1.5, label="Perfect prediction")

    # Compute metrics
    from sklearn.metrics import mean_absolute_error, r2_score
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

    ax.text(0.05, 0.92, f"MAE = {mae:.2f} MPa\nRMSE = {rmse:.2f} MPa\nR$^2$ = {r2:.3f}",
            transform=ax.transAxes, fontsize=13,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="gray", alpha=0.9))

    ax.set_xlabel("Actual Compressive Strength (MPa)", fontsize=14)
    ax.set_ylabel("Predicted Compressive Strength (MPa)", fontsize=14)
    ax.set_title("Predicted vs Actual Compressive Strength\n(5-fold Cross-Validation)", fontsize=16)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.legend(loc="lower right", fontsize=12)
    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "pred_vs_actual.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/pred_vs_actual.png")


# ── Plot 2: Feature Importance ──

def plot_feature_importance(booster):
    # Use gain-based importance
    importance = booster.get_score(importance_type="gain")

    # Pretty names for display
    pretty_names = {
        "cement": "Cement",
        "slag": "Blast-Furnace Slag",
        "fly_ash": "Fly Ash",
        "water": "Water",
        "superplasticizer": "Superplasticizer",
        "coarse_agg": "Coarse Aggregate",
        "fine_agg": "Fine Aggregate",
        "age": "Curing Age",
        "wb_ratio": "Water-to-Binder Ratio",
        "scm_pct": "SCM Percentage",
    }

    features = sorted(importance.keys(), key=lambda k: importance[k], reverse=True)
    values = [importance[f] for f in features]
    labels = [pretty_names.get(f, f) for f in features]

    n_bars = len(features)
    fig, ax = plt.subplots(figsize=(10, max(6, n_bars * 0.4)))
    bars = ax.barh(range(len(features)), values, color=CB_BLUE, edgecolor="white", linewidth=0.5)

    # Highlight key features mentioned in the paper
    highlight = {"cement", "wb_ratio", "scm_pct"}
    for i, f in enumerate(features):
        if f in highlight:
            bars[i].set_color(CB_ORANGE)

    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(labels, fontsize=12)
    ax.invert_yaxis()
    ax.set_xlabel("Feature Importance (Gain)", fontsize=14)
    ax.set_title("XGBoost Feature Importance (Gain-Based)\nPhase 2.5 Winning Model", fontsize=16)

    # Add legend for highlight colour
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_ORANGE, label="Key engineered / constrained features"),
        Patch(facecolor=CB_BLUE, label="Other features"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=12)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/feature_importance.png")


# ── Plot 3: Headline Finding — CO2 vs Strength Pareto Front ──

def plot_headline_finding():
    # Load all candidates and Pareto front
    cand_df = pd.read_csv(PROJECT_ROOT / "discoveries" / "discovery_candidates.csv")
    pareto_df = pd.read_csv(PROJECT_ROOT / "discoveries" / "discovery_pareto.csv")

    fig, ax = plt.subplots(figsize=(12, 7))

    # All candidates as faint background
    ax.scatter(cand_df["co2_kg_per_m3"], cand_df["predicted_strength"],
               alpha=0.08, s=8, color=CB_BLUE, edgecolors="none",
               label="All candidates (n=3,685)")

    # Pareto front as connected line + markers
    pareto_sorted = pareto_df.sort_values("co2_kg_per_m3")
    ax.plot(pareto_sorted["co2_kg_per_m3"], pareto_sorted["predicted_strength"],
            "-o", color=CB_GREEN, markersize=5, linewidth=1.5, markeredgecolor="white",
            markeredgewidth=0.5, label="Pareto front (n=31)", zorder=5)

    # Mark the conventional C40 baseline
    c40_co2 = 335.4
    c40_strength = 50.0
    ax.scatter([c40_co2], [c40_strength], marker="D", s=120, color=CB_RED,
               edgecolors=CB_BLACK, linewidth=1.2, zorder=10,
               label=f"Conventional C40 ({c40_strength:.0f} MPa, {c40_co2:.0f} kg CO$_2$/m$^3$)")

    # Mark the discovered low-carbon mix (in-distribution winner from paper)
    disc_co2 = 156.9
    disc_strength = 58.8
    ax.scatter([disc_co2], [disc_strength], marker="*", s=250, color=CB_ORANGE,
               edgecolors=CB_BLACK, linewidth=1.0, zorder=10,
               label=f"Low-carbon discovery ({disc_strength:.0f} MPa, {disc_co2:.0f} kg CO$_2$/m$^3$)")

    # Arrow connecting C40 to discovery
    ax.annotate("",
                xy=(disc_co2, disc_strength),
                xytext=(c40_co2, c40_strength),
                arrowprops=dict(arrowstyle="->", color=CB_BLACK, lw=1.2,
                                linestyle="--", connectionstyle="arc3,rad=-0.2"))
    # Label the arrow
    mid_x = (c40_co2 + disc_co2) / 2 + 15
    mid_y = (c40_strength + disc_strength) / 2 + 2
    ax.text(mid_x, mid_y, "53% CO$_2$ reduction\n+18% strength",
            fontsize=12, ha="center", va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=CB_YELLOW, alpha=0.8, edgecolor="gray"))

    # 50 MPa structural target line
    ax.axhline(50, color="gray", linestyle=":", linewidth=1, alpha=0.7)
    ax.text(ax.get_xlim()[0] + 5 if ax.get_xlim()[0] > 0 else 75, 50.8,
            "50 MPa structural target", fontsize=8, color="gray", alpha=0.8)

    ax.set_xlabel("Embodied CO$_2$ (kg CO$_2$e / m$^3$)", fontsize=14)
    ax.set_ylabel("Predicted Compressive Strength (MPa)", fontsize=14)
    ax.set_title("CO$_2$ vs Compressive Strength: Pareto Front\nPhase B Discovery Sweep (3,685 candidates)", fontsize=16)
    ax.legend(loc="lower right", fontsize=11, framealpha=0.9)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "headline_finding.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/headline_finding.png")


# ── Plot 4: CO2 Component Breakdown Comparison ──

def plot_co2_comparison():
    # Conventional C40 mix
    c40 = {"cement": 350, "slag": 0, "fly_ash": 0, "water": 160,
            "superplasticizer": 8, "coarse_agg": 950, "fine_agg": 700}

    # Discovered low-carbon mix — the in-distribution Pareto winner from the
    # Phase B discovery sweep (cement >= 102 kg/m3).  The Pareto CSV row with
    # CO2 = 156.91 and strength = 58.77 MPa is: 120/300/150/160/12/950/700/90d.
    disc = {"cement": 120, "slag": 300, "fly_ash": 150, "water": 160,
            "superplasticizer": 12, "coarse_agg": 950, "fine_agg": 700}

    # Component labels and colours (colourblind-safe)
    components = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_agg", "fine_agg"]
    component_labels = ["Cement", "Slag", "Fly Ash", "Water", "Superplasticizer",
                        "Coarse Agg.", "Fine Agg."]
    # Use distinct colourblind-safe colours for each component
    component_colours = [CB_RED, CB_BLUE, CB_GREEN, CB_CYAN, CB_PURPLE, CB_ORANGE, CB_YELLOW]

    c40_co2 = [c40[c] * CO2_PER_KG[c] for c in components]
    disc_co2 = [disc[c] * CO2_PER_KG[c] for c in components]

    fig, ax = plt.subplots(figsize=(10, 7))

    x = np.array([0, 1])
    width = 0.55

    # Stacked bars
    c40_bottom = np.zeros(1)
    disc_bottom = np.zeros(1)

    for i, (label, colour) in enumerate(zip(component_labels, component_colours)):
        c40_val = c40_co2[i]
        disc_val = disc_co2[i]

        bar1 = ax.bar(0, c40_val, width, bottom=c40_bottom[0], color=colour,
                       edgecolor="white", linewidth=0.5, label=label if i == i else None)
        bar2 = ax.bar(1, disc_val, width, bottom=disc_bottom[0], color=colour,
                       edgecolor="white", linewidth=0.5)
        c40_bottom[0] += c40_val
        disc_bottom[0] += disc_val

    # Add total labels on top of each bar
    c40_total = sum(c40_co2)
    disc_total = sum(disc_co2)
    ax.text(0, c40_total + 5, f"{c40_total:.1f} kg\nCO$_2$/m$^3$",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.text(1, disc_total + 5, f"{disc_total:.1f} kg\nCO$_2$/m$^3$",
            ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Add percentage reduction annotation
    pct_reduction = (1 - disc_total / c40_total) * 100
    ax.annotate(f"{pct_reduction:.0f}% reduction",
                xy=(1, disc_total + 2), xytext=(0.5, (c40_total + disc_total) / 2 + 30),
                fontsize=11, ha="center", fontweight="bold", color=CB_GREEN,
                arrowprops=dict(arrowstyle="->", color=CB_GREEN, lw=1.5))

    # Add component value labels inside bars (only for visible segments)
    for i, (c40_val, disc_val) in enumerate(zip(c40_co2, disc_co2)):
        # C40 bar
        c40_mid = sum(c40_co2[:i]) + c40_val / 2
        if c40_val > 8:
            ax.text(0, c40_mid, f"{c40_val:.1f}",
                    ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        # Discovery bar
        disc_mid = sum(disc_co2[:i]) + disc_val / 2
        if disc_val > 8:
            ax.text(1, disc_mid, f"{disc_val:.1f}",
                    ha="center", va="center", fontsize=8, color="white", fontweight="bold")

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Conventional C40\n(350 kg cement, 28-day)",
                         "Low-Carbon Discovery\n(120 kg cement, 90-day)"],
                        fontsize=12)
    ax.set_ylabel("Embodied CO$_2$ (kg CO$_2$e / m$^3$)", fontsize=14)
    ax.set_title("CO$_2$ Emissions by Component:\nConventional vs Low-Carbon Mix", fontsize=16)
    ax.set_ylim(0, c40_total + 50)

    # Legend — build from component labels
    from matplotlib.patches import Patch
    legend_handles = [Patch(facecolor=c, label=l) for c, l in zip(component_colours, component_labels)]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=11, framealpha=0.9)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "co2_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/co2_comparison.png")


# ── Plot 5: Emission Factor Sensitivity ──

def plot_emission_sensitivity():
    """Bar chart showing how the headline CO2 reduction varies with the
    slag emission-factor allocation method."""
    # Discovery mix: 120/300/150 + 160 water + 12 SP + 950 coarse + 700 fine
    disc_base = {
        "cement": 120, "slag": 300, "fly_ash": 150, "water": 160,
        "superplasticizer": 12, "coarse_agg": 950, "fine_agg": 700,
    }
    c40_co2 = 335.4

    scenarios = [
        (0.02, "System\nexpansion"),
        (0.07, "Economic\n(default)"),
        (0.10, "Mid-range"),
        (0.20, "Mass\nallocation"),
        (0.30, "Conservative"),
    ]

    slag_efs = [s[0] for s in scenarios]
    labels = [s[1] for s in scenarios]
    disc_co2s = []
    reductions = []
    for ef, _ in scenarios:
        factors = dict(CO2_PER_KG)
        factors["slag"] = ef
        co2 = sum(disc_base.get(k, 0) * factors.get(k, 0) for k in factors)
        disc_co2s.append(co2)
        reductions.append((1 - co2 / c40_co2) * 100)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    x = np.arange(len(scenarios))
    bars = ax1.bar(x, reductions, width=0.55, color=CB_BLUE, edgecolor="white", linewidth=0.5)

    # Highlight the default
    bars[1].set_color(CB_ORANGE)

    for i, (red, co2) in enumerate(zip(reductions, disc_co2s)):
        ax1.text(i, red + 1.2, f"{red:.0f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax1.text(i, red / 2, f"{co2:.0f}\nkg CO$_2$", ha="center", va="center",
                 fontsize=9, color="white", fontweight="bold")

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=11)
    ax1.set_xlabel("Slag Emission-Factor Allocation Method", fontsize=13)
    ax1.set_ylabel("CO$_2$ Reduction vs C40 Baseline (%)", fontsize=13)
    ax1.set_title("Sensitivity of Headline CO$_2$ Reduction\nto Slag Emission-Factor Allocation", fontsize=15)
    ax1.set_ylim(0, max(reductions) + 10)

    # Add horizontal reference line at C40
    ax1.axhline(0, color="gray", linewidth=0.5)

    # Add note
    ax1.text(0.98, 0.02, f"C40 baseline: {c40_co2:.0f} kg CO$_2$/m$^3$\nDiscovery: 120/300/150 cement/slag/fly ash",
             transform=ax1.transAxes, fontsize=9, ha="right", va="bottom",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "emission_sensitivity.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/emission_sensitivity.png")


# ── Main ──

def main():
    print("Loading dataset and training model...")
    df = load_dataset()

    print("Running 5-fold cross-validation for pred vs actual plot...")
    y_true, y_pred = cross_val_predictions(df)

    print("Training full model for feature importance...")
    booster, X, y = train_full_model(df)

    print("Generating plots:")
    plot_pred_vs_actual(y_true, y_pred)
    plot_feature_importance(booster)
    plot_headline_finding()
    plot_co2_comparison()
    plot_emission_sensitivity()

    print("\nAll plots saved to plots/")


if __name__ == "__main__":
    main()
