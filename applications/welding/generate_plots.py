"""
generate_plots.py — Publication-quality figures for the welding HDR project.

Produces four plots in plots/:
  1. pred_vs_actual.png       — predicted vs actual HAZ half-width scatter
  2. feature_importance.png   — top feature importances from the winning model
  3. headline_finding.png     — H1 refutation: HI-only R²=0.485 vs full model R²=0.97
  4. cross_process_transfer.png — H20 refutation: GMAW→GTAW transfer gap

Style: seaborn-v0_8-whitegrid, colourblind-safe palette, 300 DPI.

Usage:
    python generate_plots.py
"""
from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xgboost as xgb
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "welding.csv"
PLOTS_DIR = PROJECT_ROOT / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

# Colourblind-safe palette (Okabe-Ito)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_GREY = "#999999"

STYLE = "seaborn-v0_8-whitegrid"
DPI = 300
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
})
RANDOM_SEED = 42
N_FOLDS = 5

# Rosenthal constants
K_STEEL = 45.0
RHO_STEEL = 7850.0
CP_STEEL = 490.0
T_AMB = 25.0

STEEL_PROCESSES = ("GMAW", "GTAW")

RAW_FEATURES = [
    "voltage_v", "current_a", "travel_mm_s",
    "thickness_mm", "preheat_c", "carbon_equiv",
]
DERIVED_FEATURES = ["heat_input_kj_mm", "cooling_t85_s_est"]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES


# ---------------------------------------------------------------------------
# Helper: feature engineering (mirrors model.py _add_features)
# ---------------------------------------------------------------------------

def add_physics_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add heat_input_kj_mm and cooling_t85_s_est columns."""
    out = df.copy()
    eta = out["efficiency"].astype(float)
    v = out["voltage_v"].astype(float)
    i = out["current_a"].astype(float)
    s = out["travel_mm_s"].astype(float)
    thk = out["thickness_mm"].astype(float)
    pre = out["preheat_c"].astype(float)
    q_per_mm = eta * v * i / s
    out["heat_input_kj_mm"] = q_per_mm / 1000.0
    q_per_m = q_per_mm * 1000.0
    t0 = pre + T_AMB
    a1 = 1.0 / np.maximum(500.0 - t0, 10.0)
    a2 = 1.0 / np.maximum(800.0 - t0, 10.0)
    thk_m = thk / 1000.0
    t85_thick = (q_per_m / (2.0 * math.pi * K_STEEL)) * (a1 - a2)
    safe_thk2 = np.maximum(thk_m ** 2, 1e-10)
    t85_thin = (q_per_m ** 2) / (
        4.0 * math.pi * K_STEEL * RHO_STEEL * CP_STEEL * safe_thk2
    ) * (a1 ** 2 - a2 ** 2)
    out["cooling_t85_s_est"] = np.where(thk >= 8.0, t85_thick, t85_thin)
    return out


def load_steel_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df[df["process"].isin(STEEL_PROCESSES)].reset_index(drop=True)


def build_xgb_params(monotone: bool = True) -> dict:
    """Return the winning P25.3 XGBoost parameter dict."""
    monotone_vec = [0] * len(FEATURE_NAMES)
    if monotone:
        monotone_vec[FEATURE_NAMES.index("heat_input_kj_mm")] = 1
        monotone_vec[FEATURE_NAMES.index("cooling_t85_s_est")] = 1
    return {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "monotone_constraints": "(" + ",".join(str(v) for v in monotone_vec) + ")",
        "verbosity": 0,
        "nthread": 1,
    }


# ---------------------------------------------------------------------------
# 1. Predicted vs Actual scatter
# ---------------------------------------------------------------------------

def plot_pred_vs_actual():
    """5-fold OOF predictions from the winning P25.3 model."""
    print("  [1/4] pred_vs_actual.png ...")
    df = load_steel_dataset()
    df = add_physics_features(df)
    X = df[FEATURE_NAMES].values.astype(np.float32)
    y = df["haz_width_mm"].values.astype(np.float32)

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    y_true_all, y_pred_all = [], []
    for train_idx, test_idx in kf.split(X):
        params = build_xgb_params(monotone=True)
        dtrain = xgb.DMatrix(X[train_idx], label=np.log1p(y[train_idx]))
        booster = xgb.train(params, dtrain, num_boost_round=300)
        preds = np.expm1(booster.predict(xgb.DMatrix(X[test_idx])))
        y_true_all.extend(y[test_idx].tolist())
        y_pred_all.extend(preds.tolist())

    y_true_arr = np.array(y_true_all)
    y_pred_arr = np.array(y_pred_all)
    r2 = r2_score(y_true_arr, y_pred_arr)
    mae = mean_absolute_error(y_true_arr, y_pred_arr)

    with plt.style.context(STYLE):
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(y_true_arr, y_pred_arr, s=18, alpha=0.55, color=CB_BLUE,
                   edgecolors="none", label="Out-of-fold predictions")
        lo = min(y_true_arr.min(), y_pred_arr.min()) - 1
        hi = max(y_true_arr.max(), y_pred_arr.max()) + 1
        ax.plot([lo, hi], [lo, hi], "--", color=CB_GREY, linewidth=1.2,
                label="Perfect prediction")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_xlabel("Actual HAZ half-width (mm)", fontsize=12)
        ax.set_ylabel("Predicted HAZ half-width (mm)", fontsize=12)
        ax.set_title("Predicted vs Actual HAZ Width (P25.3, 5-fold CV)",
                      fontsize=13, fontweight="bold")
        ax.text(0.05, 0.92,
                f"R$^2$ = {r2:.4f}\nMAE = {mae:.2f} mm\nn = {len(y_true_arr)}",
                transform=ax.transAxes, fontsize=11,
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                          edgecolor=CB_GREY, alpha=0.9))
        ax.legend(loc="lower right", fontsize=12)
        ax.set_aspect("equal", adjustable="box")
        fig.tight_layout(pad=2.0)
        fig.savefig(PLOTS_DIR / "pred_vs_actual.png", dpi=DPI,
                    bbox_inches="tight")
        plt.close(fig)
    print(f"    R2={r2:.4f}, MAE={mae:.2f} mm")


# ---------------------------------------------------------------------------
# 2. Feature importance
# ---------------------------------------------------------------------------

def plot_feature_importance():
    """Permutation importance: shuffle each feature, measure MAE increase.

    Permutation importance is used instead of tree-internal gain because
    it better reflects the actual predictive contribution of each feature
    (consistent with the ablation story: E06 t_{8/5} gives 5x more MAE
    improvement than E01 heat input alone).
    """
    print("  [2/4] feature_importance.png (permutation, 10 repeats) ...")
    df = load_steel_dataset()
    df = add_physics_features(df)
    X = df[FEATURE_NAMES].values.astype(np.float32)
    y = df["haz_width_mm"].values.astype(np.float32)

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    rng = np.random.RandomState(RANDOM_SEED)

    # Baseline OOF predictions
    y_pred_base = np.zeros_like(y)
    boosters = []
    fold_indices = list(kf.split(X))
    for train_idx, test_idx in fold_indices:
        params = build_xgb_params(monotone=True)
        dtrain = xgb.DMatrix(X[train_idx], label=np.log1p(y[train_idx]))
        booster = xgb.train(params, dtrain, num_boost_round=300)
        boosters.append(booster)
        y_pred_base[test_idx] = np.expm1(
            booster.predict(xgb.DMatrix(X[test_idx])))
    base_mae = mean_absolute_error(y, y_pred_base)

    # Permutation importance: for each feature, shuffle and re-predict
    n_repeats = 10
    imp_means = {}
    for fi, fname in enumerate(FEATURE_NAMES):
        deltas = []
        for _ in range(n_repeats):
            X_perm = X.copy()
            X_perm[:, fi] = rng.permutation(X_perm[:, fi])
            y_pred_perm = np.zeros_like(y)
            for (train_idx, test_idx), bst in zip(fold_indices, boosters):
                y_pred_perm[test_idx] = np.expm1(
                    bst.predict(xgb.DMatrix(X_perm[test_idx])))
            perm_mae = mean_absolute_error(y, y_pred_perm)
            deltas.append(perm_mae - base_mae)
        imp_means[fname] = np.mean(deltas)

    # Sort descending
    sorted_feats = sorted(imp_means.items(), key=lambda x: x[1], reverse=True)
    names = [f[0] for f in sorted_feats]
    values = [f[1] for f in sorted_feats]

    # Pretty labels
    label_map = {
        "voltage_v": "Voltage (V)",
        "current_a": "Current (A)",
        "travel_mm_s": "Travel speed (mm/s)",
        "thickness_mm": "Plate thickness (mm)",
        "preheat_c": "Preheat temp. (\u00b0C)",
        "carbon_equiv": "Carbon equivalent",
        "heat_input_kj_mm": "Heat input HI (kJ/mm)",
        "cooling_t85_s_est": "Cooling time t$_{8/5}$ (s)",
    }
    pretty_names = [label_map.get(n, n) for n in names]

    # Colour: physics-derived features in orange, raw in blue
    colours = [CB_ORANGE if n in DERIVED_FEATURES else CB_BLUE for n in names]

    with plt.style.context(STYLE):
        n_bars = len(names)
        fig, ax = plt.subplots(figsize=(10, max(6, n_bars * 0.5)))
        bars = ax.barh(range(len(names)), values, color=colours, edgecolor="white",
                       linewidth=0.5)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(pretty_names, fontsize=12)
        ax.invert_yaxis()
        ax.set_xlabel("MAE increase when feature is shuffled (mm)", fontsize=14)
        ax.set_title(
            "Permutation Importance: Cooling Time t$_{8/5}$ Outranks Heat Input",
            fontsize=13, fontweight="bold")

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                    f"+{val:.2f} mm", va="center", fontsize=10)

        # Legend for colours
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=CB_ORANGE, label="Physics-derived feature"),
            Patch(facecolor=CB_BLUE, label="Raw process parameter"),
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=12)

        fig.tight_layout(pad=2.0)
        fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=DPI,
                    bbox_inches="tight")
        plt.close(fig)
    print(f"    Top feature: {names[0]} (+{values[0]:.2f} mm)")


# ---------------------------------------------------------------------------
# 3. Headline finding: H1 refutation dual scatter
# ---------------------------------------------------------------------------

def plot_headline_finding():
    """Dual scatter: HI-only linear model vs full P25.3 model predictions.

    Visualises the H1 refutation: heat input alone gets R²=0.485, the
    full physics-informed model achieves R²=0.97.
    """
    print("  [3/4] headline_finding.png ...")
    df = load_steel_dataset()
    df = add_physics_features(df)
    X_full = df[FEATURE_NAMES].values.astype(np.float32)
    y = df["haz_width_mm"].values.astype(np.float32)
    hi = df["heat_input_kj_mm"].values.reshape(-1, 1)

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)

    # Collect OOF predictions for both models
    y_true_all = []
    y_pred_hi_all = []
    y_pred_full_all = []

    for train_idx, test_idx in kf.split(X_full):
        # HI-only linear model
        lr = LinearRegression().fit(hi[train_idx], y[train_idx])
        y_pred_hi_all.extend(lr.predict(hi[test_idx]).tolist())

        # Full P25.3 model
        params = build_xgb_params(monotone=True)
        dtrain = xgb.DMatrix(X_full[train_idx], label=np.log1p(y[train_idx]))
        booster = xgb.train(params, dtrain, num_boost_round=300)
        preds = np.expm1(booster.predict(xgb.DMatrix(X_full[test_idx])))
        y_pred_full_all.extend(preds.tolist())
        y_true_all.extend(y[test_idx].tolist())

    y_true_arr = np.array(y_true_all)
    y_pred_hi_arr = np.array(y_pred_hi_all)
    y_pred_full_arr = np.array(y_pred_full_all)

    r2_hi = r2_score(y_true_arr, y_pred_hi_arr)
    r2_full = r2_score(y_true_arr, y_pred_full_arr)
    mae_hi = mean_absolute_error(y_true_arr, y_pred_hi_arr)
    mae_full = mean_absolute_error(y_true_arr, y_pred_full_arr)

    with plt.style.context(STYLE):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

        lo = min(y_true_arr.min(), y_pred_hi_arr.min(), y_pred_full_arr.min()) - 1
        hi_lim = max(y_true_arr.max(), y_pred_hi_arr.max(), y_pred_full_arr.max()) + 1

        # Left panel: HI-only
        ax1.scatter(y_true_arr, y_pred_hi_arr, s=16, alpha=0.45,
                    color=CB_RED, edgecolors="none")
        ax1.plot([lo, hi_lim], [lo, hi_lim], "--", color=CB_GREY, linewidth=1.2)
        ax1.set_xlim(lo, hi_lim)
        ax1.set_ylim(lo, hi_lim)
        ax1.set_xlabel("Actual HAZ half-width (mm)", fontsize=14)
        ax1.set_ylabel("Predicted HAZ half-width (mm)", fontsize=14)
        ax1.set_title("Heat Input Only (Linear)", fontsize=16, fontweight="bold")
        ax1.text(0.05, 0.92,
                 f"R$^2$ = {r2_hi:.3f}\nMAE = {mae_hi:.2f} mm",
                 transform=ax1.transAxes, fontsize=11,
                 verticalalignment="top",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                           edgecolor=CB_RED, alpha=0.9))
        ax1.set_aspect("equal", adjustable="box")

        # Right panel: full model
        ax2.scatter(y_true_arr, y_pred_full_arr, s=16, alpha=0.45,
                    color=CB_BLUE, edgecolors="none")
        ax2.plot([lo, hi_lim], [lo, hi_lim], "--", color=CB_GREY, linewidth=1.2)
        ax2.set_xlim(lo, hi_lim)
        ax2.set_ylim(lo, hi_lim)
        ax2.set_xlabel("Actual HAZ half-width (mm)", fontsize=14)
        ax2.set_title("Full Physics-Informed Model (P25.3)", fontsize=16,
                       fontweight="bold")
        ax2.text(0.05, 0.92,
                 f"R$^2$ = {r2_full:.4f}\nMAE = {mae_full:.2f} mm",
                 transform=ax2.transAxes, fontsize=11,
                 verticalalignment="top",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                           edgecolor=CB_BLUE, alpha=0.9))
        ax2.set_aspect("equal", adjustable="box")

        fig.suptitle(
            "H1 Refuted: Heat Input Alone Explains <50% of HAZ Variance",
            fontsize=16, fontweight="bold", y=1.02)
        fig.tight_layout(pad=2.0)
        fig.savefig(PLOTS_DIR / "headline_finding.png", dpi=200,
                    bbox_inches="tight")
        plt.close(fig)
    print(f"    HI-only R2={r2_hi:.3f}, Full model R2={r2_full:.4f}")


# ---------------------------------------------------------------------------
# 4. Cross-process transfer: GMAW -> GTAW catastrophic failure
# ---------------------------------------------------------------------------

def plot_cross_process_transfer():
    """Bar chart comparing MAE across three conditions:
    GTAW within-family, GMAW->GTAW transfer, GTAW->GMAW transfer.
    """
    print("  [4/4] cross_process_transfer.png ...")
    df_all = pd.read_csv(DATA_PATH)
    df_all = df_all[df_all["process"].isin(STEEL_PROCESSES)].reset_index(drop=True)
    df_all = add_physics_features(df_all)
    gmaw = df_all[df_all["process"] == "GMAW"].reset_index(drop=True)
    gtaw = df_all[df_all["process"] == "GTAW"].reset_index(drop=True)

    # NOTE: the transfer experiments in hdr_phase25.py train without the
    # log-target transform (they pass label=y_tr directly to DMatrix).
    # We match that behaviour here so the numbers agree with results.tsv.
    def train_and_predict(train_df, test_df):
        X_tr = train_df[FEATURE_NAMES].values.astype(np.float32)
        y_tr = train_df["haz_width_mm"].values.astype(np.float32)
        X_te = test_df[FEATURE_NAMES].values.astype(np.float32)
        y_te = test_df["haz_width_mm"].values.astype(np.float32)
        params = build_xgb_params(monotone=True)
        dtrain = xgb.DMatrix(X_tr, label=y_tr)
        booster = xgb.train(params, dtrain, num_boost_round=300)
        y_pred = booster.predict(xgb.DMatrix(X_te))
        return y_te, y_pred

    # GMAW -> GTAW
    y_te_g2t, y_pred_g2t = train_and_predict(gmaw, gtaw)
    mae_g2t = mean_absolute_error(y_te_g2t, y_pred_g2t)
    r2_g2t = r2_score(y_te_g2t, y_pred_g2t)

    # GTAW -> GMAW
    y_te_t2g, y_pred_t2g = train_and_predict(gtaw, gmaw)
    mae_t2g = mean_absolute_error(y_te_t2g, y_pred_t2g)
    r2_t2g = r2_score(y_te_t2g, y_pred_t2g)

    # GTAW within-family 5-fold CV (also no log-target, matching hdr_phase25.py)
    X_g = gtaw[FEATURE_NAMES].values.astype(np.float32)
    y_g = gtaw["haz_width_mm"].values.astype(np.float32)
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    all_t, all_p = [], []
    for tr, te in kf.split(X_g):
        params = build_xgb_params(monotone=True)
        dtrain = xgb.DMatrix(X_g[tr], label=y_g[tr])
        booster = xgb.train(params, dtrain, num_boost_round=300)
        preds = booster.predict(xgb.DMatrix(X_g[te]))
        all_t.extend(y_g[te].tolist())
        all_p.extend(preds.tolist())
    mae_within = mean_absolute_error(all_t, all_p)
    r2_within = r2_score(all_t, all_p)

    # Build bar chart
    conditions = [
        "GTAW within-family\n(5-fold CV)",
        "GMAW \u2192 GTAW\ntransfer",
        "GTAW \u2192 GMAW\ntransfer",
    ]
    maes = [mae_within, mae_g2t, mae_t2g]
    r2s = [r2_within, r2_g2t, r2_t2g]
    bar_colours = [CB_GREEN, CB_ORANGE, CB_RED]

    with plt.style.context(STYLE):
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(conditions, maes, color=bar_colours, edgecolor="white",
                      width=0.55, linewidth=0.8)

        # Add value labels on bars
        for bar, mae_val, r2_val in zip(bars, maes, r2s):
            ypos = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, ypos + 0.25,
                    f"MAE = {mae_val:.2f} mm\nR$^2$ = {r2_val:.3f}",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

        # Annotate the transfer gap
        gap_pct = (mae_g2t - mae_within) / mae_within * 100
        ax.annotate(
            f"+{gap_pct:.0f}% MAE gap",
            xy=(1, mae_g2t), xytext=(1.45, mae_g2t * 0.75),
            fontsize=11, fontweight="bold", color=CB_RED,
            arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
            ha="center")

        ax.set_ylabel("Mean Absolute Error (mm)", fontsize=14)
        ax.set_title(
            "H20 Refuted: Cross-Process Transfer Fails Catastrophically",
            fontsize=16, fontweight="bold")
        ax.set_ylim(0, max(maes) * 1.35)

        # Add a horizontal dashed line at the within-family baseline
        ax.axhline(y=mae_within, color=CB_GREEN, linestyle=":", linewidth=1.2,
                   alpha=0.6)

        fig.tight_layout(pad=2.0)
        fig.savefig(PLOTS_DIR / "cross_process_transfer.png", dpi=DPI,
                    bbox_inches="tight")
        plt.close(fig)

    print(f"    Within-family MAE={mae_within:.2f}, "
          f"GMAW->GTAW MAE={mae_g2t:.2f} (+{gap_pct:.0f}%)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating welding HDR plots ...")
    plot_pred_vs_actual()
    plot_feature_importance()
    plot_headline_finding()
    plot_cross_process_transfer()
    print(f"\nAll plots saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
