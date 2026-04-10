"""generate_plots.py -- Publication-quality figures for the FDM HDR paper.

Produces four plots in plots/:
  1. pred_vs_actual.png     -- predicted vs actual tensile strength scatter
  2. feature_importance.png -- XGBoost feature importance with physics features highlighted
  3. headline_finding.png   -- 1/50 keep rate dot plot and Cura-default comparison bars
  4. tree_to_linear.png     -- Phase 1 tournament bar chart showing tree-to-linear ratio

Style: seaborn-v0_8-whitegrid, colourblind-safe palette, 300 DPI.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import KFold

# ---------------------------------------------------------------------------
# Project paths and constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
PLOTS_DIR = PROJECT_ROOT / "plots"
DATA_PATH = PROJECT_ROOT / "data" / "3d_printing.csv"
RESULTS_TSV = PROJECT_ROOT / "results.tsv"

N_FOLDS = 5
RANDOM_SEED = 42

# Colourblind-safe palette (Wong 2011, Nature Methods)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_CYAN = "#56B4E9"
CB_GREY = "#999999"

# Physics-informed derived features
DERIVED_FEATURES = ["E_lin", "vol_flow", "interlayer_time", "infill_contact", "thermal_margin"]
RAW_FEATURES = [
    "layer_height", "wall_thickness", "infill_density", "infill_pattern",
    "nozzle_temperature", "bed_temperature", "print_speed", "material", "fan_speed",
]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES
LINE_WIDTH_MM = 0.48
TG_BY_MATERIAL = {0: 105.0, 1: 60.0}
REFERENCE_FOOTPRINT_MM2 = 50.0 * 50.0


# ---------------------------------------------------------------------------
# Data loading and featurisation (self-contained, no model.py import needed)
# ---------------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, sep=";")


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    layer_h = out["layer_height"].replace(0, np.nan)
    speed = out["print_speed"].replace(0, np.nan)
    out["E_lin"] = (out["nozzle_temperature"] * out["print_speed"] / layer_h).fillna(0.0)
    out["vol_flow"] = out["print_speed"] * out["layer_height"] * LINE_WIDTH_MM
    out["interlayer_time"] = (REFERENCE_FOOTPRINT_MM2 / (speed * LINE_WIDTH_MM)).fillna(0.0)
    out["infill_contact"] = out["infill_density"] / 100.0 * REFERENCE_FOOTPRINT_MM2
    tg = out["material"].map(TG_BY_MATERIAL).astype(float)
    out["thermal_margin"] = out["nozzle_temperature"].astype(float) - tg
    return out


def get_cv_predictions(df: pd.DataFrame):
    """Run 5-fold CV and return (y_true, y_pred) arrays."""
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["tension_strength"].values.astype(np.float32)

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    y_true_all, y_pred_all = [], []

    for train_idx, test_idx in kf.split(X):
        params = {
            "objective": "reg:squarederror",
            "max_depth": 6, "learning_rate": 0.05,
            "min_child_weight": 3, "subsample": 0.8,
            "colsample_bytree": 0.8, "verbosity": 0,
        }
        dtrain = xgb.DMatrix(X[train_idx], label=y[train_idx])
        dtest = xgb.DMatrix(X[test_idx])
        booster = xgb.train(params, dtrain, num_boost_round=300)
        preds = booster.predict(dtest)
        y_true_all.extend(y[test_idx].tolist())
        y_pred_all.extend(preds.tolist())

    return np.array(y_true_all), np.array(y_pred_all)


def get_feature_importance(df: pd.DataFrame) -> pd.Series:
    """Train on full dataset and return gain-based feature importance."""
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["tension_strength"].values.astype(np.float32)
    params = {
        "objective": "reg:squarederror",
        "max_depth": 6, "learning_rate": 0.05,
        "min_child_weight": 3, "subsample": 0.8,
        "colsample_bytree": 0.8, "verbosity": 0,
    }
    dtrain = xgb.DMatrix(X, label=y, feature_names=FEATURE_NAMES)
    booster = xgb.train(params, dtrain, num_boost_round=300)
    importance = booster.get_score(importance_type="gain")
    # Fill missing features with 0
    series = pd.Series({f: importance.get(f, 0.0) for f in FEATURE_NAMES})
    return series.sort_values(ascending=True)


def load_results() -> pd.DataFrame:
    return pd.read_csv(RESULTS_TSV, sep="\t")


# ---------------------------------------------------------------------------
# Plot 1: Predicted vs Actual scatter
# ---------------------------------------------------------------------------

def plot_pred_vs_actual(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))

    mae = np.mean(np.abs(y_true - y_pred))
    r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)

    ax.scatter(y_true, y_pred, c=CB_BLUE, edgecolor="white", linewidth=0.5,
               s=60, alpha=0.85, zorder=3)

    # Perfect prediction line
    lo = min(y_true.min(), y_pred.min()) - 2
    hi = max(y_true.max(), y_pred.max()) + 2
    ax.plot([lo, hi], [lo, hi], "--", color=CB_GREY, linewidth=1.2, zorder=1,
            label="Perfect prediction")

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel("Actual Tensile Strength (MPa)", fontsize=12)
    ax.set_ylabel("Predicted Tensile Strength (MPa)", fontsize=12)
    ax.set_title("Predicted vs Actual Tensile Strength\n(5-fold CV, E08 winning model)",
                 fontsize=13, fontweight="bold")

    # Annotation box
    textstr = f"MAE = {mae:.2f} MPa\n$R^2$ = {r2:.3f}\nN = {len(y_true)}"
    props = dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=CB_GREY, alpha=0.9)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment="top", bbox=props)

    ax.legend(loc="lower right", fontsize=10)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "pred_vs_actual.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 2: Feature importance (gain) with physics features highlighted
# ---------------------------------------------------------------------------

def plot_feature_importance(importance: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    colours = [CB_ORANGE if f in DERIVED_FEATURES else CB_BLUE
               for f in importance.index]

    bars = ax.barh(range(len(importance)), importance.values, color=colours,
                   edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(importance)))
    # Nicer display names
    display_names = {
        "E_lin": "E_lin (energy density)",
        "vol_flow": "vol_flow (flow rate)",
        "interlayer_time": "interlayer_time (bond time)",
        "infill_contact": "infill_contact (load area)",
        "thermal_margin": "thermal_margin (T - Tg)",
    }
    labels = [display_names.get(f, f) for f in importance.index]
    ax.set_yticklabels(labels, fontsize=10)

    ax.set_xlabel("Feature Importance (XGBoost gain)", fontsize=12)
    ax.set_title("Feature Importance: Raw vs Physics-Informed Features\n"
                 "(E08 winning model, trained on full dataset)",
                 fontsize=13, fontweight="bold")

    # Legend
    raw_patch = mpatches.Patch(color=CB_BLUE, label="Raw features (9)")
    phys_patch = mpatches.Patch(color=CB_ORANGE, label="Physics-informed features (5)")
    ax.legend(handles=[raw_patch, phys_patch], loc="lower right", fontsize=10)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 3: Headline finding -- two panels
#   Left:  1/50 keep rate dot plot (all experiments' MAE)
#   Right: Cura default vs Discovery recipe grouped bar comparison
# ---------------------------------------------------------------------------

def plot_headline_finding(results_df: pd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Left panel: dot plot of all Phase 2 experiments' MAE ---
    # Filter to Phase 2 experiments (E00-E50, excluding tournament T* and P25*)
    phase2 = results_df[results_df["exp_id"].str.startswith("E")].copy()
    phase2 = phase2.sort_values("mae", ascending=False).reset_index(drop=True)

    baseline_mae = float(results_df[results_df["exp_id"] == "E00"]["mae"].iloc[0])

    colours = []
    for _, row in phase2.iterrows():
        if row["exp_id"] == "E08":
            colours.append(CB_GREEN)
        elif row["exp_id"] == "E00":
            colours.append(CB_CYAN)
        else:
            colours.append(CB_RED if row["decision"] == "REVERT" else CB_GREEN)

    ax1.scatter(phase2["mae"], range(len(phase2)), c=colours,
                s=50, edgecolor="white", linewidth=0.4, zorder=3)

    # Baseline noise floor line
    ax1.axvline(x=baseline_mae, color=CB_GREY, linestyle="--", linewidth=1.2,
                label=f"Baseline MAE = {baseline_mae:.2f}", zorder=1)

    # Highlight E08
    e08_row = phase2[phase2["exp_id"] == "E08"]
    if not e08_row.empty:
        e08_idx = e08_row.index[0]
        e08_mae = float(e08_row["mae"].iloc[0])
        ax1.annotate(
            f"E08: {e08_mae:.2f} MPa\n(KEEP)",
            xy=(e08_mae, e08_idx),
            xytext=(e08_mae - 0.25, e08_idx + 3),
            fontsize=9, fontweight="bold", color=CB_GREEN,
            arrowprops=dict(arrowstyle="->", color=CB_GREEN, lw=1.5),
        )

    ax1.set_xlabel("5-fold CV MAE (MPa)", fontsize=12)
    ax1.set_ylabel("Experiment (sorted by MAE)", fontsize=12)
    ax1.set_title("Phase 2: 1 of 50 Experiments Kept\n"
                  "(49 at or above baseline noise floor)",
                  fontsize=12, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=9)

    # Hide y-ticks (experiment ordering is just visual)
    ax1.set_yticks([])

    # --- Right panel: Discovery recipe vs Cura default ---
    categories = ["Tensile Strength\n(MPa)", "Print Time\n(hours)", "Energy\n(kWh)"]
    cura_vals = [18.0, 0.52, 0.10]
    discovery_vals = [30.1, 0.24, 0.049]

    x_pos = np.arange(len(categories))
    width = 0.32

    bars_cura = ax2.bar(x_pos - width / 2, cura_vals, width, label="Cura PLA Default",
                        color=CB_GREY, edgecolor="white", linewidth=0.5)
    bars_disc = ax2.bar(x_pos + width / 2, discovery_vals, width, label="Discovery Recipe (E08 model)",
                        color=CB_GREEN, edgecolor="white", linewidth=0.5)

    # Add percentage improvement labels
    improvements = ["+59%", "-54%", "-51%"]
    for i, (bar, imp) in enumerate(zip(bars_disc, improvements)):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 imp, ha="center", va="bottom", fontsize=10, fontweight="bold",
                 color=CB_GREEN)

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(categories, fontsize=11)
    ax2.set_ylabel("Value", fontsize=12)
    ax2.set_title("Discovery Recipe vs Cura PLA Default\n"
                  "(PLA, 0.20 mm, 120 mm/s, 215 C, 70% infill, 3 walls)",
                  fontsize=12, fontweight="bold")
    ax2.legend(loc="upper right", fontsize=9)

    fig.tight_layout(w_pad=4)
    fig.savefig(PLOTS_DIR / "headline_finding.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 4: Tournament results -- tree-to-linear ratio
# ---------------------------------------------------------------------------

def plot_tree_to_linear(results_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))

    # Extract tournament entries (E00 + T01-T04)
    tournament_ids = ["E00", "T01", "T02", "T03", "T04"]
    tournament = results_df[results_df["exp_id"].isin(tournament_ids)].copy()
    tournament = tournament.set_index("exp_id").loc[tournament_ids].reset_index()

    families = ["XGBoost\n(baseline)", "LightGBM", "ExtraTrees", "RandomForest", "Ridge\n(linear)"]
    maes = tournament["mae"].values

    # Colour: XGBoost green (winner), Ridge orange (linear reference), others grey
    colours = [CB_GREEN] + [CB_GREY] * 3 + [CB_ORANGE]

    bars = ax.bar(range(len(families)), maes, color=colours, edgecolor="white",
                  linewidth=0.5, width=0.65)

    ax.set_xticks(range(len(families)))
    ax.set_xticklabels(families, fontsize=11)
    ax.set_ylabel("5-fold CV MAE (MPa)", fontsize=12)
    ax.set_title("Phase 1 Tournament: Tree-to-Linear MAE Ratio = 1.32\n"
                 "(below 2x threshold -- relationship is mostly linear at N=50)",
                 fontsize=13, fontweight="bold")

    # Add MAE labels on bars
    for bar, mae_val in zip(bars, maes):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{mae_val:.2f}", ha="center", va="bottom", fontsize=10,
                fontweight="bold")

    # Add the ratio annotation
    xgb_mae = maes[0]
    ridge_mae = maes[4]
    ratio = ridge_mae / xgb_mae

    # Draw a bracket between XGBoost and Ridge
    mid_y = max(maes) + 0.4
    ax.annotate("", xy=(0, mid_y), xytext=(4, mid_y),
                arrowprops=dict(arrowstyle="<->", color=CB_RED, lw=2))
    ax.text(2, mid_y + 0.15, f"Ratio = {ratio:.2f}x (threshold = 2.0x)",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color=CB_RED)

    # 2x threshold reference line
    threshold_2x = xgb_mae * 2
    ax.axhline(y=threshold_2x, color=CB_RED, linestyle=":", linewidth=1.2, alpha=0.6,
               label=f"2x threshold = {threshold_2x:.2f} MPa")
    ax.legend(loc="upper left", fontsize=9)

    # Set y-axis to start near 0 for honest comparison
    ax.set_ylim(0, max(maes) + 1.2)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "tree_to_linear.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    PLOTS_DIR.mkdir(exist_ok=True)

    # Apply style
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_context("paper", font_scale=1.1)

    print("Loading dataset...")
    df = load_dataset()
    results_df = load_results()

    print("Running 5-fold CV for predicted-vs-actual plot...")
    y_true, y_pred = get_cv_predictions(df)

    print("Computing feature importance...")
    importance = get_feature_importance(df)

    print("Generating plot 1: pred_vs_actual.png")
    plot_pred_vs_actual(y_true, y_pred)

    print("Generating plot 2: feature_importance.png")
    plot_feature_importance(importance)

    print("Generating plot 3: headline_finding.png")
    plot_headline_finding(results_df)

    print("Generating plot 4: tree_to_linear.png")
    plot_tree_to_linear(results_df)

    print(f"\nAll plots saved to {PLOTS_DIR}/")
    for f in sorted(PLOTS_DIR.glob("*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
