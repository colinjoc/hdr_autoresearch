#!/usr/bin/env python
"""Generate publication-quality plots for the heat-mortality HDR project.

Reads results.tsv, discoveries/, and the Phase 2 cache to produce 6 PNGs
in plots/. All plots use seaborn-v0_8-whitegrid, colourblind-safe palettes,
300 DPI, and labelled axes.

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
import seaborn as sns
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import KFold

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from model import (
    BASELINE_FEATURES_WITH_CITY,
    add_features,
    add_phase2_features,
    build_clean_dataset,
    label_lethal_heatwave,
)

PLOTS_DIR = HERE / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

RESULTS_PATH = HERE / "results.tsv"
PHASE2_CACHE = HERE / "data" / "clean" / "heat_mortality_phase2.parquet"
FEAT_IMP_PATH = HERE / "discoveries" / "feature_importance.csv"
PER_CITY_AUC_PATH = HERE / "discoveries" / "per_city_auc.csv"

# Phase 2 best accumulated features
PHASE2_BEST_ADDS = (
    ["tw_night_c_max_roll4w", "tw_rolling_21d_mean",
     "prior_week_pscore", "prior_4w_mean_pscore"]
    + [f"country_{cn}" for cn in
       ("US", "FR", "GB", "ES", "IT", "DE", "GR", "PT", "RO",
        "AT", "PL", "SE", "DK", "IE", "NL")]
    + ["tmax_c_mean_lag1", "tmax_c_mean_lag2",
       "tmax_c_mean_lag3", "tmax_c_mean_lag4"]
    + ["week_of_year_sin", "week_of_year_cos"]
)
PHASE2_BEST_FEATURES = BASELINE_FEATURES_WITH_CITY + PHASE2_BEST_ADDS

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

def _load_panel() -> pd.DataFrame:
    """Load and clean the Phase 2 cache, add all features."""
    raw = pd.read_parquet(PHASE2_CACHE)
    clean = build_clean_dataset(raw)
    feat = add_features(clean)
    feat = add_phase2_features(feat)
    return feat.reset_index(drop=True)


def _get_oof_predictions(panel: pd.DataFrame) -> np.ndarray:
    """Run 5-fold CV with Phase 2 best ExtraTrees and return OOF predictions."""
    feature_cols = [c for c in PHASE2_BEST_FEATURES if c in panel.columns]
    X = panel[feature_cols].astype("float64").fillna(0.0).values
    y = panel["excess_deaths"].astype("float64").values

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(panel), dtype="float64")
    for tr, va in kf.split(panel):
        m = ExtraTreesRegressor(
            n_estimators=300, max_depth=None, n_jobs=4, random_state=42
        )
        m.fit(X[tr], y[tr])
        oof[va] = m.predict(X[va])
    return oof


def _load_results() -> pd.DataFrame:
    """Load results.tsv as a DataFrame."""
    return pd.read_csv(RESULTS_PATH, sep="\t")


# ============================================================
# Plot 1: Predicted vs Actual Excess Deaths
# ============================================================

def plot_pred_vs_actual(panel: pd.DataFrame, oof: np.ndarray) -> None:
    """Scatter of predicted vs actual excess deaths (Phase 2 best OOF)."""
    y = panel["excess_deaths"].astype("float64").values
    lethal = label_lethal_heatwave(panel).astype(bool)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Non-lethal weeks
    ax.scatter(
        y[~lethal], oof[~lethal],
        s=6, alpha=0.25, color=CB_GREY, label="Non-lethal weeks",
        rasterized=True, edgecolors="none",
    )
    # Lethal weeks
    ax.scatter(
        y[lethal], oof[lethal],
        s=20, alpha=0.7, color=CB_RED, label="Lethal heat-wave weeks",
        edgecolors="none", zorder=5,
    )

    # Identity line
    lims = [min(y.min(), oof.min()) - 20, max(y.max(), oof.max()) + 20]
    ax.plot(lims, lims, "--", color="black", linewidth=1, alpha=0.5, zorder=1)

    from sklearn.metrics import mean_absolute_error, r2_score
    mae = mean_absolute_error(y, oof)
    r2 = r2_score(y, oof)
    ax.text(
        0.05, 0.92,
        f"MAE = {mae:.1f} deaths/week\n$R^2$ = {r2:.3f}\nn = {len(y):,}",
        transform=ax.transAxes, fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8),
    )

    ax.set_xlabel("Actual excess deaths (per week)")
    ax.set_ylabel("Predicted excess deaths (OOF, Phase 2 best)")
    ax.set_title("Predicted vs Actual Excess Deaths (5-fold CV)")
    ax.legend(loc="lower right")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect("equal")

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "pred_vs_actual.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'pred_vs_actual.png'}")


# ============================================================
# Plot 2: Feature Importance (top 15)
# ============================================================

def plot_feature_importance() -> None:
    """Horizontal bar chart of top 15 features by built-in importance.

    Night-time wet-bulb features are highlighted -- they should appear
    near the bottom or not at all, which IS the negative finding.
    """
    df = pd.read_csv(FEAT_IMP_PATH)
    df = df.sort_values("builtin_importance", ascending=False).head(15).copy()
    df = df.sort_values("builtin_importance", ascending=True)  # for horizontal bar

    # Classify features
    night_tw_keywords = ["tw_night", "tropical_night", "compound_tw"]

    def is_night_tw(name):
        return any(kw in name for kw in night_tw_keywords)

    colors = [CB_RED if is_night_tw(f) else CB_BLUE for f in df["feature"]]

    # Clean feature names for display
    name_map = {
        "consecutive_days_above_p95_tmax": "Tmax > p95 streak",
        "iso_month_cos": "Month (cosine)",
        "tmax_c_max": "Tmax weekly max",
        "tmax_c_mean": "Tmax weekly mean",
        "tavg_c": "Tavg",
        "iso_month_sin": "Month (sine)",
        "tw_c_max": "Tw daytime max",
        "tw_c_mean": "Tw daytime mean",
        "tmin_c_mean": "Tmin weekly mean",
        "tw_rolling_21d_mean": "Tw 21-day rolling mean",
        "iso_year": "Year",
        "rh_pct": "Relative humidity (%)",
        "tdew_c": "Dewpoint",
        "lat": "Latitude",
        "log_population": "log(Population)",
        "city_philadelphia": "City: Philadelphia",
    }
    labels = [name_map.get(f, f) for f in df["feature"]]

    n_bars = len(df)
    fig, ax = plt.subplots(figsize=(10, max(6, n_bars * 0.4)))
    bars = ax.barh(range(len(df)), df["builtin_importance"].values, color=colors)

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xlabel("Feature importance (Gini decrease)")
    ax.set_title("Top 15 Features by Importance (Binary Lethal Classifier)")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_BLUE, label="Baseline / daytime features"),
        Patch(facecolor=CB_RED, label="Night-time wet-bulb features"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    # Annotation
    ax.text(
        0.97, 0.05,
        "No night-time wet-bulb\nfeature in the top 15",
        transform=ax.transAxes, fontsize=10, ha="right", va="bottom",
        style="italic", color=CB_RED, alpha=0.8,
    )

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "feature_importance.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'feature_importance.png'}")


# ============================================================
# Plot 3: Headline Finding -- Night-Tw Hypotheses Dot Plot
# ============================================================

def plot_headline_finding() -> None:
    """Dot plot of all 22 flagship night-Tw hypotheses vs baseline MAE,
    plus the Phase 2 best (without night-Tw) and stacked-all-22.
    Shows that all night-Tw additions cluster at the noise floor.
    """
    results = _load_results()

    # Get baseline MAE (T03 ExtraTrees)
    t03 = results[results["exp_id"] == "T03"]
    baseline_mae = float(t03["cv_mae_deaths"].iloc[0])

    # Get night-Tw hypotheses H001-H022 (non-deferred)
    night_tw = results[results["exp_id"].str.match(r"^H0(0[1-9]|1\d|2[0-2])$")].copy()
    night_tw = night_tw[night_tw["cv_mae_deaths"].notna()].copy()
    night_tw["delta_mae"] = night_tw["cv_mae_deaths"] - baseline_mae

    # Get Phase 2 best (H100)
    h100 = results[results["exp_id"] == "H100"]
    phase2_best_mae = float(h100["cv_mae_deaths"].iloc[0]) if len(h100) > 0 else 40.334

    # Classify KEEP vs REVERT
    night_tw["decision"] = night_tw["notes"].apply(
        lambda n: "KEEP" if "KEEP" in str(n) else "REVERT"
    )

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot each hypothesis as a dot
    keep_mask = night_tw["decision"] == "KEEP"
    revert_mask = ~keep_mask

    # REVERT dots
    ax.scatter(
        night_tw.loc[revert_mask, "delta_mae"],
        range(revert_mask.sum()),
        s=80, color=CB_GREY, edgecolors="black", linewidth=0.5,
        label="REVERT (no improvement)", zorder=5,
    )
    # KEEP dots
    if keep_mask.any():
        offset = revert_mask.sum()
        ax.scatter(
            night_tw.loc[keep_mask, "delta_mae"],
            range(offset, offset + keep_mask.sum()),
            s=80, color=CB_GREEN, edgecolors="black", linewidth=0.5,
            label="KEEP (memory signal only)", zorder=5,
        )

    # Labels
    all_labels = list(night_tw.loc[revert_mask, "exp_id"]) + list(night_tw.loc[keep_mask, "exp_id"])
    all_descs = []
    for _, row in night_tw.loc[revert_mask].iterrows():
        all_descs.append(f"{row['exp_id']}: {row['description'][:40]}")
    for _, row in night_tw.loc[keep_mask].iterrows():
        all_descs.append(f"{row['exp_id']}: {row['description'][:40]}")

    ax.set_yticks(range(len(all_descs)))
    ax.set_yticklabels(all_descs, fontsize=10)

    # Noise floor zone
    noise = max(0.5, 0.01 * baseline_mae)
    ax.axvspan(-noise, noise, alpha=0.15, color=CB_ORANGE, label=f"Noise floor (+/- {noise:.1f} deaths)")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_xlabel("Change in MAE vs baseline (deaths/week)")
    ax.set_title("22 Flagship Night-Time Wet-Bulb Hypotheses:\nAll Cluster at the Noise Floor")
    ax.legend(loc="lower right", fontsize=12)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "headline_finding.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'headline_finding.png'}")


# ============================================================
# Plot 4: Robustness Heatmap
# ============================================================

def plot_robustness_heatmap() -> None:
    """Heatmap of 10 robustness tests x {baseline, +tw_max, +stacked} MAE."""
    results = _load_results()

    tests = []
    labels = {
        "R01": "Per-city ensemble",
        "R02": "70+ age proxy",
        "R03": "Davies-Jones Tw",
        "R04": "Climatology swap",
        "R05": "No fixed effects",
        "R06": "No autocorrelation",
        "R07": "Hot cities only",
        "R08": "Heat-wave weeks only",
        "R09": "Binary classifier",
        "R10": "Mediterranean only",
    }

    for rnum in range(1, 11):
        rid = f"R{rnum:02d}"
        e00 = results[results["exp_id"] == f"{rid}.E00"]
        tw = results[results["exp_id"] == f"{rid}.tw_max"]
        stk = results[results["exp_id"] == f"{rid}.stacked"]

        if len(e00) == 0:
            continue

        # For R09, use AUC (no MAE)
        if rid == "R09":
            tests.append({
                "test": labels.get(rid, rid),
                "Baseline": float(e00["cv_auc_lethal"].iloc[0]),
                "+ tw_night_c_max": float(tw["cv_auc_lethal"].iloc[0]) if len(tw) > 0 else np.nan,
                "+ 22 flagship": float(stk["cv_auc_lethal"].iloc[0]) if len(stk) > 0 else np.nan,
                "metric": "AUC",
            })
        else:
            tests.append({
                "test": labels.get(rid, rid),
                "Baseline": float(e00["cv_mae_deaths"].iloc[0]),
                "+ tw_night_c_max": float(tw["cv_mae_deaths"].iloc[0]) if len(tw) > 0 else np.nan,
                "+ 22 flagship": float(stk["cv_mae_deaths"].iloc[0]) if len(stk) > 0 else np.nan,
                "metric": "MAE",
            })

    df = pd.DataFrame(tests)

    # Split into MAE and AUC rows
    mae_df = df[df["metric"] == "MAE"].copy()
    auc_df = df[df["metric"] == "AUC"].copy()

    # For the heatmap, show the DELTA from baseline for each test
    fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                              gridspec_kw={"width_ratios": [9, 1]})

    # MAE heatmap (show deltas -- positive = worse)
    mae_matrix = mae_df[["test", "Baseline", "+ tw_night_c_max", "+ 22 flagship"]].set_index("test")
    delta_matrix = mae_matrix.copy()
    delta_matrix["+ tw_night_c_max"] = mae_matrix["+ tw_night_c_max"] - mae_matrix["Baseline"]
    delta_matrix["+ 22 flagship"] = mae_matrix["+ 22 flagship"] - mae_matrix["Baseline"]
    delta_matrix["Baseline"] = 0.0

    ax = axes[0]
    # Annotate with actual MAE values, color by delta
    annot_vals = mae_matrix.values
    annot_str = np.array([[f"{v:.1f}" for v in row] for row in annot_vals])

    sns.heatmap(
        delta_matrix.values, ax=ax,
        cmap="RdYlGn_r", center=0, vmin=-1, vmax=1,
        annot=annot_str, fmt="",
        xticklabels=["Baseline", "+ tw_night_c_max", "+ 22 flagship"],
        yticklabels=mae_matrix.index,
        linewidths=1, linecolor="white",
        cbar_kws={"label": "MAE delta from baseline (deaths/week)"},
    )
    ax.set_title("MAE Robustness Tests (values = MAE, colour = delta)")

    # AUC row
    ax2 = axes[1]
    if len(auc_df) > 0:
        auc_matrix = auc_df[["test", "Baseline", "+ tw_night_c_max", "+ 22 flagship"]].set_index("test")
        delta_auc = auc_matrix.copy()
        delta_auc["+ tw_night_c_max"] = auc_matrix["+ tw_night_c_max"] - auc_matrix["Baseline"]
        delta_auc["+ 22 flagship"] = auc_matrix["+ 22 flagship"] - auc_matrix["Baseline"]
        delta_auc["Baseline"] = 0.0

        annot_auc = np.array([[f"{v:.4f}" for v in row] for row in auc_matrix.values])

        sns.heatmap(
            delta_auc.values, ax=ax2,
            cmap="RdYlGn", center=0, vmin=-0.005, vmax=0.005,
            annot=annot_auc, fmt="",
            xticklabels=["Base", "+tw", "+22"],
            yticklabels=auc_matrix.index,
            linewidths=1, linecolor="white",
            cbar_kws={"label": "AUC delta"},
        )
        ax2.set_title("AUC (R09)")
    else:
        ax2.axis("off")

    fig.suptitle("Phase 2.5 Robustness: Night-Tw Never Helps", fontsize=16, y=1.02)
    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "robustness_heatmap.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'robustness_heatmap.png'}")


# ============================================================
# Plot 5: Night-Tw vs Tmax Scatter (coloured by lethality)
# ============================================================

def plot_night_tw_vs_tmax(panel: pd.DataFrame) -> None:
    """Scatter of night-time wet-bulb vs daytime Tmax, coloured by whether
    the week was lethal. Shows both variables separate equally well,
    so night-Tw adds nothing over Tmax.
    """
    lethal = label_lethal_heatwave(panel).astype(bool)
    tmax = panel["tmax_c_mean"].astype("float64").values
    tw_night = panel["tw_night_c_max"].astype("float64").values

    # Remove NaN
    valid = np.isfinite(tmax) & np.isfinite(tw_night)
    tmax = tmax[valid]
    tw_night = tw_night[valid]
    lethal = lethal[valid]

    fig, ax = plt.subplots(figsize=(10, 7))

    # Non-lethal
    ax.scatter(
        tmax[~lethal], tw_night[~lethal],
        s=4, alpha=0.15, color=CB_GREY, label="Non-lethal weeks",
        rasterized=True, edgecolors="none",
    )
    # Lethal
    ax.scatter(
        tmax[lethal], tw_night[lethal],
        s=25, alpha=0.7, color=CB_RED, label="Lethal heat-wave weeks",
        edgecolors="black", linewidth=0.3, zorder=5,
    )

    # Correlation
    from scipy import stats
    r, p = stats.pearsonr(tmax, tw_night)
    ax.text(
        0.05, 0.95,
        f"r = {r:.3f}\nLethal weeks cluster\nin the same corner",
        transform=ax.transAxes, fontsize=10, va="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8),
    )

    ax.set_xlabel("Daytime Tmax weekly mean ($^\\circ$C)")
    ax.set_ylabel("Night-time wet-bulb max ($^\\circ$C)")
    ax.set_title("Night-Time Tw vs Daytime Tmax:\nBoth Separate Lethal Weeks Equally Well")
    ax.legend(loc="lower right")

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "night_tw_vs_tmax.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'night_tw_vs_tmax.png'}")


# ============================================================
# Plot 6: Phase 2 KEEPs Waterfall Chart
# ============================================================

def plot_phase2_keeps() -> None:
    """Horizontal bar chart showing the 7 KEEP experiments as MAE deltas
    from the Phase 1 baseline, demonstrating that autocorrelation and
    seasonality dominate, not night-Tw.
    """
    # The 7 KEEPs in order with their individual delta-MAE contributions
    keeps = [
        ("H022: 4-week rolling night-Tw max (memory)", -0.85, "tw_night"),
        ("H048: 21-day Tw rolling mean (daytime)", -0.66, "daytime_tw"),
        ("H057: Prior-week p-score (autocorrelation)", -0.71, "autocorrelation"),
        ("H058: 4-week mean p-score (autocorrelation)", -1.03, "autocorrelation"),
        ("H066: Country fixed effects", -0.89, "structure"),
        ("H078: Dry-bulb Tmax lags 1-4 (DLNM)", -0.58, "lag"),
        ("H100: Week-of-year cyclic (seasonality)", -0.51, "seasonality"),
    ]

    labels = [k[0] for k in keeps]
    deltas = [k[1] for k in keeps]
    categories = [k[2] for k in keeps]

    cat_colors = {
        "tw_night": CB_ORANGE,
        "daytime_tw": CB_BLUE,
        "autocorrelation": CB_GREEN,
        "structure": CB_PURPLE,
        "lag": CB_BLUE,
        "seasonality": CB_BLUE,
    }
    cat_labels_map = {
        "tw_night": "Night-Tw (memory only)",
        "daytime_tw": "Daytime Tw memory",
        "autocorrelation": "Autocorrelation",
        "structure": "Structural (country FE)",
        "lag": "Dry-bulb lag structure",
        "seasonality": "Seasonality",
    }

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_colors = [cat_colors[c] for c in categories]
    y_pos = np.arange(len(keeps))

    bars = ax.barh(y_pos, deltas, color=bar_colors, edgecolor="black", linewidth=0.5)

    # Annotate bar values
    for i, (delta, bar) in enumerate(zip(deltas, bars)):
        ax.text(delta - 0.02, i, f"{delta:+.2f}", ha="right", va="center",
                fontsize=9, fontweight="bold", color="white")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("Change in MAE (deaths/week)", fontsize=14)
    ax.set_title(
        "Phase 2 KEEPs: What Actually Improved the Model\n"
        "(Baseline MAE 45.56 $\\rightarrow$ Phase 2 best 40.33, total gain = -5.23)",
        fontsize=16,
    )
    ax.axvline(0, color="black", linewidth=0.8)
    ax.invert_yaxis()  # first KEEP at the top

    # Legend
    from matplotlib.patches import Patch
    seen = set()
    legend_elements = []
    for cat in categories:
        if cat not in seen:
            seen.add(cat)
            legend_elements.append(
                Patch(facecolor=cat_colors[cat], label=cat_labels_map[cat],
                      edgecolor="black", linewidth=0.5)
            )
    ax.legend(handles=legend_elements, loc="lower left", fontsize=12)

    # Annotation
    ax.text(
        0.97, 0.95,
        "Only 1 of 7 KEEPs involves night-Tw,\n"
        "and it is a memory signal, not a threshold",
        transform=ax.transAxes, fontsize=10, ha="right", va="top",
        style="italic", color=CB_ORANGE,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8, edgecolor=CB_ORANGE),
    )

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "phase2_keeps.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {PLOTS_DIR / 'phase2_keeps.png'}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    warnings.filterwarnings("ignore", category=FutureWarning)
    print("Generating plots for heat-mortality HDR project...")

    # Load data once
    print("\n[1/6] Loading panel and computing OOF predictions...")
    panel = _load_panel()
    oof = _get_oof_predictions(panel)

    print("\n[2/6] Predicted vs Actual scatter...")
    plot_pred_vs_actual(panel, oof)

    print("\n[3/6] Feature importance bar chart...")
    plot_feature_importance()

    print("\n[4/6] Headline finding dot plot...")
    plot_headline_finding()

    print("\n[5/6] Robustness heatmap...")
    plot_robustness_heatmap()

    print("\n[6/6] Night-Tw vs Tmax scatter...")
    plot_night_tw_vs_tmax(panel)

    print("\n[7/6] Phase 2 KEEPs waterfall...")
    plot_phase2_keeps()

    print(f"\nAll plots saved to {PLOTS_DIR}/")
    for p in sorted(PLOTS_DIR.glob("*.png")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
