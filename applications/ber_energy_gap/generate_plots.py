"""Generate publication-quality plots for BER Energy Gap paper.

Produces five plots in plots/:
  1. pred_vs_actual.png    — predicted vs actual BER energy scatter with 1:1 line
  2. feature_importance.png — top 15 features by SHAP mean |SHAP|
  3. headline_finding.png  — actual energy distribution by BER rating band
  4. era_comparison.png    — energy value by construction era
  5. retrofit_cost_effectiveness.png — horizontal bar of retrofit savings per EUR
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Style: seaborn-v0_8-whitegrid, colourblind-safe palette
plt.style.use("seaborn-v0_8-whitegrid")

# Colourblind-safe palette (Wong 2011)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_CYAN = "#56B4E9"
CB_YELLOW = "#F0E442"
CB_BLACK = "#000000"

CB_PALETTE = [CB_BLUE, CB_ORANGE, CB_GREEN, CB_RED, CB_PURPLE, CB_CYAN, CB_YELLOW, CB_BLACK]

warnings.filterwarnings("ignore", category=UserWarning)

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(PROJ_DIR, "plots")
DISCOVERIES_DIR = os.path.join(PROJ_DIR, "discoveries")
DPI = 300

sys.path.insert(0, PROJ_DIR)


def load_model_data():
    """Load prepared modelling data and generate cross-validated predictions."""
    from prepare import load_raw, clean_and_feature_engineer, prepare_modelling_data
    from run_experiments import add_engineered_features
    from evaluate import cross_validate

    print("Loading data...")
    raw = load_raw()
    clean = clean_and_feature_engineer(raw)
    X, y, df_model = prepare_modelling_data(clean)
    print(f"  Records: {len(X):,}")

    # Add kept HDR features
    X_composed = add_engineered_features(X, df_model)

    # Keep only the features used in composition (base + 4 kept HDR features)
    kept_hdr = ["compactness_ratio", "vent_loss_proxy", "primary_energy_factor", "sh_fraction"]
    extra_cols = [c for c in kept_hdr if c in X_composed.columns and c not in X.columns]
    X_final = X.copy()
    for col in extra_cols:
        X_final[col] = X_composed[col]

    return X_final, y, df_model, clean


def get_predictions(X, y):
    """Get cross-validated predictions using the final LightGBM model."""
    from evaluate import cross_validate
    from lightgbm import LGBMRegressor

    def model_fn():
        return LGBMRegressor(
            n_estimators=600, max_depth=10, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
            device="cpu", random_state=42, n_jobs=-1, verbose=-1,
        )

    # Use subsample for speed — 200k is enough for a good scatter
    n = min(200_000, len(X))
    rng = np.random.RandomState(42)
    idx = rng.choice(len(X), n, replace=False)
    X_sub = X.iloc[idx].reset_index(drop=True)
    y_sub = y[idx]

    print(f"  Running 5-fold CV on {n:,} records for predictions...")
    metrics = cross_validate(model_fn, X_sub, y_sub, n_splits=5)
    print(f"  MAE={metrics['mae']:.2f}, R2={metrics['r2']:.4f}")
    return y_sub, metrics["predictions"], metrics


# ── Plot 1: Predicted vs Actual ─────────────────────────────────────────────

def plot_pred_vs_actual(y_true, y_pred):
    """Scatter plot of predicted vs actual BER energy values."""
    print("Generating pred_vs_actual.png...")

    fig, ax = plt.subplots(figsize=(7, 7))

    # Hex-bin for density (millions of points would overplot)
    hb = ax.hexbin(
        y_true, y_pred, gridsize=80, cmap="Blues", mincnt=1,
        linewidths=0.2, edgecolors="face",
    )
    cb = fig.colorbar(hb, ax=ax, label="Count")

    # 1:1 line
    lims = [0, max(y_true.max(), y_pred.max()) * 1.05]
    ax.plot(lims, lims, "--", color=CB_RED, linewidth=1.5, label="1:1 line", zorder=5)

    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Actual BER energy (kWh/m$^2$/yr)", fontsize=12)
    ax.set_ylabel("Predicted BER energy (kWh/m$^2$/yr)", fontsize=12)
    ax.set_title("Predicted vs Actual BER Energy Rating", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=11)

    # Annotate with metrics
    from sklearn.metrics import mean_absolute_error, r2_score
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    ax.text(
        0.97, 0.03,
        f"MAE = {mae:.1f} kWh/m$^2$/yr\nR$^2$ = {r2:.3f}",
        transform=ax.transAxes, fontsize=11,
        verticalalignment="bottom", horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85, edgecolor="gray"),
    )

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "pred_vs_actual.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Plot 2: Feature Importance ──────────────────────────────────────────────

def plot_feature_importance():
    """Top 15 features by SHAP mean absolute value."""
    print("Generating feature_importance.png...")

    shap_df = pd.read_csv(os.path.join(DISCOVERIES_DIR, "shap_importance.csv"))
    top15 = shap_df.head(15).iloc[::-1]  # reverse for horizontal bar

    # Clean feature names for display
    name_map = {
        "hlp_proxy": "Heat Loss Parameter (HLP)",
        "hs_efficiency": "Heating system efficiency",
        "primary_energy_factor": "Primary energy factor",
        "window_area": "Window area",
        "uvaluewindow": "Window U-value",
        "no_chimneys": "Number of chimneys",
        "sh_fraction": "Space heating fraction",
        "year_built": "Year of construction",
        "low_energy_lighting_pct": "Low-energy lighting (%)",
        "ground_floor_area": "Ground floor area",
        "compactness_ratio": "Compactness ratio",
        "uvaluewall": "Wall U-value",
        "uvalueroof": "Roof U-value",
        "window_wall_ratio": "Window-to-wall ratio",
        "envelope_u_avg": "Envelope avg U-value",
    }
    labels = [name_map.get(f, f) for f in top15["feature"]]

    fig, ax = plt.subplots(figsize=(9, 6.5))

    colours = []
    for feat in top15["feature"]:
        if feat in ("hlp_proxy", "uvaluewall", "uvalueroof", "uvaluewindow",
                     "window_area", "envelope_u_avg", "window_wall_ratio", "compactness_ratio"):
            colours.append(CB_BLUE)      # Fabric / envelope
        elif feat in ("hs_efficiency", "primary_energy_factor"):
            colours.append(CB_ORANGE)    # Heating system
        elif feat in ("no_chimneys", "vent_loss_proxy"):
            colours.append(CB_GREEN)     # Ventilation
        else:
            colours.append(CB_PURPLE)    # Other

    bars = ax.barh(labels, top15["mean_abs_shap"], color=colours, edgecolor="white", linewidth=0.5)

    ax.set_xlabel("Mean |SHAP value| (kWh/m$^2$/yr)", fontsize=12)
    ax.set_title("Top 15 Feature Importances (SHAP)", fontsize=14, fontweight="bold")

    # Value labels
    for bar, val in zip(bars, top15["mean_abs_shap"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", fontsize=9)

    # Legend for colour categories
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_BLUE, label="Building fabric"),
        Patch(facecolor=CB_ORANGE, label="Heating system"),
        Patch(facecolor=CB_GREEN, label="Ventilation"),
        Patch(facecolor=CB_PURPLE, label="Other"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

    ax.set_xlim(0, top15["mean_abs_shap"].max() * 1.15)
    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "feature_importance.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Plot 3: Headline Finding — BER rating distribution ──────────────────────

def plot_headline_finding(df_model):
    """Box/violin plot of actual energy by BER rating band — shows the overlap."""
    print("Generating headline_finding.png...")

    bands_ordered = ["A1", "A2", "A3", "B1", "B2", "B3",
                     "C1", "C2", "C3", "D1", "D2", "E1", "E2", "F", "G"]

    # Filter to bands with data
    df = df_model[["energy_rating", "ber_kwh_m2"]].copy()
    df = df[df["energy_rating"].isin(bands_ordered)]
    df["energy_rating"] = pd.Categorical(df["energy_rating"], categories=bands_ordered, ordered=True)

    # Subsample for speed (box plots on 1.3M rows are slow)
    if len(df) > 300_000:
        df = df.sample(300_000, random_state=42)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Use box plot with colour gradient from green (A) to red (G)
    from matplotlib.colors import LinearSegmentedColormap
    n_bands = len(bands_ordered)
    # Green -> Yellow -> Orange -> Red gradient
    cmap = LinearSegmentedColormap.from_list("ber",
        [CB_GREEN, CB_YELLOW, CB_ORANGE, CB_RED], N=n_bands)
    band_colours = [cmap(i / (n_bands - 1)) for i in range(n_bands)]

    # Gather data per band
    data_per_band = []
    positions = []
    colours_used = []
    band_labels = []
    for i, band in enumerate(bands_ordered):
        subset = df.loc[df["energy_rating"] == band, "ber_kwh_m2"]
        if len(subset) > 10:
            data_per_band.append(subset.values)
            positions.append(i)
            colours_used.append(band_colours[i])
            band_labels.append(band)

    bp = ax.boxplot(
        data_per_band, positions=positions, widths=0.6,
        patch_artist=True, showfliers=False,
        medianprops=dict(color=CB_BLACK, linewidth=1.5),
        whiskerprops=dict(color="gray"),
        capprops=dict(color="gray"),
    )

    for patch, colour in zip(bp["boxes"], colours_used):
        patch.set_facecolor(colour)
        patch.set_alpha(0.75)
        patch.set_edgecolor("gray")

    # Add BER band boundary lines (official thresholds)
    band_boundaries = {
        "A1": 25, "A2": 50, "A3": 75, "B1": 100, "B2": 125, "B3": 150,
        "C1": 175, "C2": 200, "C3": 225, "D1": 260, "D2": 300,
        "E1": 340, "E2": 380, "F": 450,
    }

    ax.set_xticks(positions)
    ax.set_xticklabels(band_labels, fontsize=10)
    ax.set_ylabel("DEAP-calculated energy (kWh/m$^2$/yr)", fontsize=12)
    ax.set_xlabel("BER Rating Band", fontsize=12)
    ax.set_title(
        "Energy Consumption Distribution by BER Rating Band\n"
        "(boxes show IQR; whiskers show 1.5 IQR — note the substantial overlap between adjacent bands)",
        fontsize=13, fontweight="bold",
    )

    # Overlay the nominal band boundaries as a step function
    band_midpoints = []
    band_upper = []
    for i, band in enumerate(band_labels):
        band_midpoints.append(i)
        if band in band_boundaries:
            band_upper.append(band_boundaries[band])
        else:
            band_upper.append(600)  # G band

    ax.plot(band_midpoints, band_upper, "s--", color=CB_BLACK, markersize=4,
            linewidth=1, alpha=0.5, label="Band upper boundary")
    ax.legend(loc="upper left", fontsize=10)

    ax.set_ylim(0, 700)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "headline_finding.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Plot 4: Era Comparison ──────────────────────────────────────────────────

def plot_era_comparison(df_model):
    """Box plot of energy by construction era."""
    print("Generating era_comparison.png...")

    era_order = ["pre-1930", "1930-1977", "1978-2005", "2006-2011", "2012-2020", "2021+"]

    # Use the actual era names from the data
    # prepare.py uses bins [0, 1930, 1978, 2006, 2012, 2021, 2200] with labels
    # ["pre-1930", "1930-1977", "1978-2005", "2006-2011", "2012-2020", "2021+"]

    df = df_model[["age_category", "ber_kwh_m2"]].copy()
    df = df.dropna(subset=["age_category"])
    df["age_category"] = df["age_category"].astype(str)

    # Map any slight naming differences
    name_remap = {
        "pre-1930": "pre-1930",
        "1930-1977": "1930-1977",
        "1978-2005": "1978-2005",
        "2006-2011": "2006-2011",
        "2012-2020": "2012-2020",
        "2021+": "2021+",
    }
    df["era"] = df["age_category"].map(name_remap)
    df = df[df["era"].isin(era_order)]

    # Subsample
    if len(df) > 300_000:
        df = df.sample(300_000, random_state=42)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Era colours: old=warm, new=cool
    era_colours = [CB_RED, CB_ORANGE, CB_YELLOW, CB_CYAN, CB_BLUE, CB_GREEN]

    data_per_era = []
    era_labels_used = []
    colours_used = []
    for i, era in enumerate(era_order):
        subset = df.loc[df["era"] == era, "ber_kwh_m2"]
        if len(subset) > 10:
            data_per_era.append(subset.values)
            era_labels_used.append(era)
            colours_used.append(era_colours[i])

    bp = ax.boxplot(
        data_per_era, widths=0.6,
        patch_artist=True, showfliers=False,
        medianprops=dict(color=CB_BLACK, linewidth=2),
        whiskerprops=dict(color="gray"),
        capprops=dict(color="gray"),
    )

    for patch, colour in zip(bp["boxes"], colours_used):
        patch.set_facecolor(colour)
        patch.set_alpha(0.75)
        patch.set_edgecolor("gray")

    # Overlay mean markers
    era_stats = pd.read_csv(os.path.join(DISCOVERIES_DIR, "era_analysis.csv"))
    means = []
    for era in era_labels_used:
        row = era_stats[era_stats["age_category"] == era]
        if len(row) > 0:
            means.append(row["mean_ber"].values[0])
        else:
            means.append(np.nan)

    positions = list(range(1, len(era_labels_used) + 1))
    ax.plot(positions, means, "D", color=CB_BLACK, markersize=7, zorder=5, label="Mean")

    # Annotate means
    for pos, m in zip(positions, means):
        if not np.isnan(m):
            ax.annotate(
                f"{m:.0f}",
                (pos, m), textcoords="offset points", xytext=(12, 5),
                fontsize=10, fontweight="bold",
            )

    ax.set_xticklabels(era_labels_used, fontsize=11)
    ax.set_ylabel("DEAP-calculated energy (kWh/m$^2$/yr)", fontsize=12)
    ax.set_xlabel("Construction era", fontsize=12)
    ax.set_title(
        "BER Energy by Construction Era\n"
        "(8.5:1 ratio between pre-1930 and 2021+ reflects cumulative building regulation improvements)",
        fontsize=13, fontweight="bold",
    )
    ax.legend(loc="upper right", fontsize=11)
    ax.set_ylim(0, 650)

    # Add regulation milestone annotations
    ax.axhline(y=339, color=CB_RED, linestyle=":", alpha=0.3, linewidth=1)
    ax.axhline(y=40, color=CB_GREEN, linestyle=":", alpha=0.3, linewidth=1)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "era_comparison.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Plot 5: Retrofit Cost-Effectiveness ─────────────────────────────────────

def plot_retrofit_cost_effectiveness():
    """Horizontal bar chart of retrofit savings and cost-effectiveness."""
    print("Generating retrofit_cost_effectiveness.png...")

    retrofit_df = pd.read_csv(os.path.join(DISCOVERIES_DIR, "retrofit_effectiveness.csv"))

    # Only show positive-saving interventions
    retrofit_df = retrofit_df[retrofit_df["saving_kwh_m2_yr"] > 0].copy()
    retrofit_df = retrofit_df.sort_values("saving_kwh_m2_yr", ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    labels = retrofit_df["intervention"].values
    savings = retrofit_df["saving_kwh_m2_yr"].values
    costs_per = retrofit_df["cost_per_kwh_m2_saved"].values

    # Colour by cost-effectiveness tier
    colours = []
    for c in costs_per:
        if c < 100:
            colours.append(CB_GREEN)    # excellent
        elif c < 600:
            colours.append(CB_CYAN)     # good
        elif c < 1000:
            colours.append(CB_ORANGE)   # moderate
        else:
            colours.append(CB_RED)      # expensive

    # Left panel: absolute saving
    bars1 = ax1.barh(labels, savings, color=colours, edgecolor="white", linewidth=0.5)
    ax1.set_xlabel("Predicted saving (kWh/m$^2$/yr)", fontsize=12)
    ax1.set_title("Absolute DEAP Improvement", fontsize=13, fontweight="bold")

    for bar, val in zip(bars1, savings):
        ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", fontsize=10, fontweight="bold")

    ax1.set_xlim(0, max(savings) * 1.25)

    # Right panel: cost per kWh/m2/yr saved
    bars2 = ax2.barh(labels, costs_per, color=colours, edgecolor="white", linewidth=0.5)
    ax2.set_xlabel("Cost per kWh/m$^2$/yr saved (EUR)", fontsize=12)
    ax2.set_title("Cost-Effectiveness", fontsize=13, fontweight="bold")

    for bar, val in zip(bars2, costs_per):
        ax2.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}", va="center", fontsize=10)

    ax2.set_xlim(0, max(costs_per) * 1.2)

    # Legend for colour tiers
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_GREEN, label="< 100 EUR (excellent)"),
        Patch(facecolor=CB_CYAN, label="100-600 EUR (good)"),
        Patch(facecolor=CB_ORANGE, label="600-1000 EUR (moderate)"),
        Patch(facecolor=CB_RED, label="> 1000 EUR (expensive)"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=4, fontsize=10,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(
        "Single-Measure Retrofit Cost-Effectiveness (Average Irish Dwelling, BER 171 kWh/m$^2$/yr)",
        fontsize=13, fontweight="bold", y=1.02,
    )

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "retrofit_cost_effectiveness.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # Load data for plots that need raw records
    X, y, df_model, clean = load_model_data()

    # Plot 1: Predicted vs actual (needs CV predictions)
    y_sub, preds_sub, metrics = get_predictions(X, y)
    plot_pred_vs_actual(y_sub, preds_sub)

    # Plot 2: Feature importance (from cached SHAP CSV)
    plot_feature_importance()

    # Plot 3: Headline finding — BER band distribution
    plot_headline_finding(df_model)

    # Plot 4: Era comparison
    plot_era_comparison(df_model)

    # Plot 5: Retrofit cost-effectiveness (from cached CSV)
    plot_retrofit_cost_effectiveness()

    print("\nAll plots generated successfully.")
