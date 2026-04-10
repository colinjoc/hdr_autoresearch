"""
Generate all four paper figures for the paint formulation HDR project.

Usage:
    python generate_plots.py

Outputs:
    plots/pred_vs_actual.png      — predicted vs actual scatter for the best-R² target
    plots/feature_importance.png  — per-target feature importance (permutation-based)
    plots/headline_finding.png    — GP baseline vs PTPIE MAE grouped bar chart
    plots/per_target_winners.png  — which model family won each target (table-as-figure)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

# Local imports
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from model import (
    PaintFormulationModel,
    TARGET_COLS,
    WINNING_EXTRA_FEATURES_PER_TARGET,
    WINNING_MODEL_PARAMS,
)

PLOTS_DIR = PROJECT_ROOT / "plots"
PLOTS_DIR.mkdir(exist_ok=True)
DATA_PATH = PROJECT_ROOT / "data" / "paint.csv"

# Style setup
plt.style.use("seaborn-v0_8-whitegrid")
# Colourblind-safe palette (Tol bright)
CB_PALETTE = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"]
DPI = 300
SEED = 42


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


# -------------------------------------------------------------------------
# Plot 1: Predicted vs actual for the best-R² target
# -------------------------------------------------------------------------

def plot_pred_vs_actual(df: pd.DataFrame) -> None:
    """Scatter of predicted vs actual for the target with highest R²."""
    # Collect cross-validated predictions for all targets to find best R²
    best_r2 = -np.inf
    best_target = None
    best_y_true = None
    best_y_pred = None

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)

    for target in TARGET_COLS:
        y_true_all, y_pred_all = [], []
        for train_idx, test_idx in kf.split(df):
            model = PaintFormulationModel(target=target)
            X_tr, y_tr = model.featurize(df.iloc[train_idx])
            X_te, y_te = model.featurize(df.iloc[test_idx])
            model.train(X_tr, y_tr)
            preds = model.predict(X_te)
            y_true_all.extend(y_te.tolist())
            y_pred_all.extend(preds.tolist())
        y_true = np.array(y_true_all)
        y_pred = np.array(y_pred_all)
        from sklearn.metrics import r2_score
        r2 = r2_score(y_true, y_pred)
        if r2 > best_r2:
            best_r2 = r2
            best_target = target
            best_y_true = y_true
            best_y_pred = y_pred

    # Pretty target labels
    target_labels = {
        "scratch_hardness_N": "Scratch Hardness (N)",
        "gloss_60": "60\u00b0 Gloss (GU)",
        "hiding_power_pct": "Hiding Power (%)",
        "cupping_mm": "Cupping Depth (mm)",
    }

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.scatter(
        best_y_true, best_y_pred,
        c=CB_PALETTE[0], edgecolors="white", linewidths=0.5,
        s=60, alpha=0.85, zorder=3,
    )

    # 1:1 reference line
    lo = min(best_y_true.min(), best_y_pred.min())
    hi = max(best_y_true.max(), best_y_pred.max())
    margin = (hi - lo) * 0.05
    ax.plot([lo - margin, hi + margin], [lo - margin, hi + margin],
            ls="--", c="grey", lw=1.2, zorder=2, label="1:1 line")

    ax.set_xlim(lo - margin, hi + margin)
    ax.set_ylim(lo - margin, hi + margin)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"Actual {target_labels[best_target]}", fontsize=12)
    ax.set_ylabel(f"Predicted {target_labels[best_target]}", fontsize=12)
    ax.set_title(
        f"Predicted vs Actual \u2014 {target_labels[best_target]}\n"
        f"5-fold CV  R\u00b2 = {best_r2:.3f}",
        fontsize=13,
    )
    ax.legend(loc="upper left", fontsize=10)
    fig.tight_layout()
    out = PLOTS_DIR / "pred_vs_actual.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {out}  (target={best_target}, R2={best_r2:.3f})")


# -------------------------------------------------------------------------
# Plot 2: Feature importance per target
# -------------------------------------------------------------------------

def _manual_permutation_importance(
    model: PaintFormulationModel,
    X: np.ndarray,
    y: np.ndarray,
    n_repeats: int = 30,
    seed: int = 42,
) -> tuple:
    """Compute permutation importance without relying on sklearn's estimator API."""
    rng = np.random.RandomState(seed)
    baseline_pred = model.predict(X)
    baseline_mae = mean_absolute_error(y, baseline_pred)
    n_features = X.shape[1]
    importances = np.zeros((n_features, n_repeats))
    for f in range(n_features):
        for r in range(n_repeats):
            X_perm = X.copy()
            X_perm[:, f] = rng.permutation(X_perm[:, f])
            perm_pred = model.predict(X_perm)
            perm_mae = mean_absolute_error(y, perm_pred)
            # Importance = increase in MAE when feature is shuffled
            importances[f, r] = perm_mae - baseline_mae
    return importances.mean(axis=1), importances.std(axis=1)


def plot_feature_importance(df: pd.DataFrame) -> None:
    """Permutation importance for each target, as a horizontal grouped bar chart."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    target_labels = {
        "scratch_hardness_N": "Scratch Hardness (N)",
        "gloss_60": "60\u00b0 Gloss (GU)",
        "hiding_power_pct": "Hiding Power (%)",
        "cupping_mm": "Cupping Depth (mm)",
    }

    for idx, target in enumerate(TARGET_COLS):
        ax = axes[idx]
        # Train on full data for importance
        model = PaintFormulationModel(target=target)
        X, y = model.featurize(df)
        model.train(X, y)

        # Manual permutation importance (model-agnostic, no sklearn estimator API)
        importances, stds = _manual_permutation_importance(model, X, y, n_repeats=30, seed=SEED)
        feature_names = model.feature_names

        # Sort by importance
        sorted_idx = np.argsort(importances)
        sorted_names = [feature_names[i] for i in sorted_idx]
        sorted_imp = importances[sorted_idx]
        sorted_std = stds[sorted_idx]

        # Colour physics-informed features differently
        extra = set(WINNING_EXTRA_FEATURES_PER_TARGET.get(target, []))
        colors = [CB_PALETTE[1] if n in extra else CB_PALETTE[0] for n in sorted_names]

        ax.barh(range(len(sorted_names)), sorted_imp, xerr=sorted_std,
                color=colors, edgecolor="white", linewidth=0.5, capsize=3)
        ax.set_yticks(range(len(sorted_names)))
        ax.set_yticklabels(sorted_names, fontsize=9)
        ax.set_xlabel("Permutation Importance\n(increase in MAE when shuffled)", fontsize=9)
        ax.set_title(target_labels[target], fontsize=11, fontweight="bold")

    # Legend
    raw_patch = mpatches.Patch(color=CB_PALETTE[0], label="Raw feature")
    phys_patch = mpatches.Patch(color=CB_PALETTE[1], label="Physics-informed feature")
    fig.legend(handles=[raw_patch, phys_patch], loc="lower center",
               ncol=2, fontsize=11, frameon=True)
    fig.suptitle("Per-Target Permutation Feature Importance", fontsize=14, y=1.01)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out = PLOTS_DIR / "feature_importance.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {out}")


# -------------------------------------------------------------------------
# Plot 3: Headline finding — GP baseline vs PTPIE MAE
# -------------------------------------------------------------------------

def plot_headline_finding() -> None:
    """Grouped bar chart: GP baseline MAE vs PTPIE MAE for each target."""
    targets = ["scratch_hardness_N", "gloss_60", "hiding_power_pct", "cupping_mm"]
    target_short = ["Scratch\nHardness (N)", "60\u00b0 Gloss\n(GU)", "Hiding\nPower (%)", "Cupping\nDepth (mm)"]

    # From results.tsv GP_BASELINE rows and Section 5.5 of paper.md
    gp_mae = [1.844, 11.498, 2.841, 2.109]
    ptpie_mae = [1.800, 10.036, 2.187, 1.519]

    # Relative improvement
    rel_imp = [(g - p) / g * 100 for g, p in zip(gp_mae, ptpie_mae)]

    x = np.arange(len(targets))
    width = 0.32

    fig, ax = plt.subplots(figsize=(8, 5))
    bars_gp = ax.bar(x - width / 2, gp_mae, width, label="GP Baseline",
                      color=CB_PALETTE[6], edgecolor="white", linewidth=0.8)
    bars_ptpie = ax.bar(x + width / 2, ptpie_mae, width, label="PTPIE (this work)",
                         color=CB_PALETTE[0], edgecolor="white", linewidth=0.8)

    # Annotate with relative improvement
    for i, (gp, pt, ri) in enumerate(zip(gp_mae, ptpie_mae, rel_imp)):
        higher = max(gp, pt)
        if abs(ri) >= 5:
            label = f"\u2212{abs(ri):.0f}%"
            color = CB_PALETTE[2]  # green
        else:
            label = f"\u2212{abs(ri):.1f}%"
            color = "grey"
        ax.annotate(
            label,
            xy=(i + width / 2, pt),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=color,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(target_short, fontsize=10)
    ax.set_ylabel("5-fold CV Mean Absolute Error", fontsize=11)
    ax.set_title(
        "GP Baseline vs Per-Target Physics-Informed Ensemble (PTPIE)\n"
        "12\u201328% MAE reduction on 3 of 4 targets",
        fontsize=13,
    )
    ax.legend(fontsize=11, loc="upper right")
    ax.set_ylim(0, max(gp_mae) * 1.25)

    fig.tight_layout()
    out = PLOTS_DIR / "headline_finding.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {out}")


# -------------------------------------------------------------------------
# Plot 4: Per-target winners — model family dispatch table-as-figure
# -------------------------------------------------------------------------

def plot_per_target_winners() -> None:
    """Table-as-figure showing which model family won each target."""

    rows = [
        {
            "target": "Scratch Hardness",
            "units": "N",
            "model": "Ridge",
            "features": "binder_pigment_ratio",
            "mae": "1.800",
            "r2": "0.221",
        },
        {
            "target": "60\u00b0 Gloss",
            "units": "GU",
            "model": "XGBoost (d=7)",
            "features": "log_thickness,\nthickness \u00d7 matting",
            "mae": "10.036",
            "r2": "0.726",
        },
        {
            "target": "Hiding Power",
            "units": "%",
            "model": "ExtraTrees (mf=0.5)",
            "features": "thickness \u00d7 pigment",
            "mae": "2.187",
            "r2": "0.664",
        },
        {
            "target": "Cupping Depth",
            "units": "mm",
            "model": "ExtraTrees",
            "features": "cyc \u00d7 matting,\npvc_proxy",
            "mae": "1.519",
            "r2": "0.715",
        },
    ]

    col_labels = ["Target", "Units", "Winning Model", "Physics-Informed\nFeatures", "MAE", "R\u00b2"]
    cell_text = [
        [r["target"], r["units"], r["model"], r["features"], r["mae"], r["r2"]]
        for r in rows
    ]

    # Model-family colour coding
    model_colors = {
        "Ridge": CB_PALETTE[0],
        "XGBoost (d=7)": CB_PALETTE[1],
        "ExtraTrees (mf=0.5)": CB_PALETTE[2],
        "ExtraTrees": CB_PALETTE[2],
    }

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis("off")

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.0, 2.0)

    # Style header row
    for j in range(len(col_labels)):
        cell = table[0, j]
        cell.set_facecolor("#333333")
        cell.set_text_props(color="white", fontweight="bold", fontsize=11)

    # Colour-code the model column (column index 2)
    for i, row in enumerate(rows):
        model_cell = table[i + 1, 2]
        color = model_colors.get(row["model"], "#FFFFFF")
        # Use a light tint of the model colour
        import matplotlib.colors as mcolors
        rgba = mcolors.to_rgba(color, alpha=0.25)
        model_cell.set_facecolor(rgba)

    # Alternate row shading
    for i in range(len(rows)):
        for j in range(len(col_labels)):
            if j != 2:  # skip model column (already coloured)
                cell = table[i + 1, j]
                if i % 2 == 0:
                    cell.set_facecolor("#F5F5F5")
                else:
                    cell.set_facecolor("#FFFFFF")

    ax.set_title(
        "Per-Target Model Dispatch Pattern\n"
        "Ridge for linear targets, ExtraTrees for nonlinear small-N, XGBoost only with physics features",
        fontsize=12, pad=20,
    )

    # Legend for model families
    legend_patches = [
        mpatches.Patch(facecolor=mcolors.to_rgba(CB_PALETTE[0], 0.25),
                       edgecolor=CB_PALETTE[0], label="Ridge"),
        mpatches.Patch(facecolor=mcolors.to_rgba(CB_PALETTE[1], 0.25),
                       edgecolor=CB_PALETTE[1], label="XGBoost"),
        mpatches.Patch(facecolor=mcolors.to_rgba(CB_PALETTE[2], 0.25),
                       edgecolor=CB_PALETTE[2], label="ExtraTrees"),
    ]
    ax.legend(handles=legend_patches, loc="lower center", ncol=3,
              fontsize=10, frameon=True, bbox_to_anchor=(0.5, -0.08))

    fig.tight_layout()
    out = PLOTS_DIR / "per_target_winners.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {out}")


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

def main():
    print("Generating paint formulation plots...")
    df = load_data()
    print(f"  Loaded {len(df)} samples from {DATA_PATH}")

    print("\n[1/4] Predicted vs actual...")
    plot_pred_vs_actual(df)

    print("[2/4] Feature importance...")
    plot_feature_importance(df)

    print("[3/4] Headline finding (GP vs PTPIE)...")
    plot_headline_finding()

    print("[4/4] Per-target winners table...")
    plot_per_target_winners()

    print(f"\nAll plots saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
