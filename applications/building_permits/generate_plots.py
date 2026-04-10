"""Generate all paper plots for the building-permits HDR project.

Reads cached data (permits_baseline.parquet, seattle_decomposition.parquet,
results.tsv, and discoveries/*.csv) and produces PNG plots in plots/.

Usage:
    python generate_plots.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold

HERE = Path(__file__).resolve().parent
PLOTS_DIR = HERE / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

CLEAN_PATH = HERE / "data" / "clean" / "permits_baseline.parquet"
SEATTLE_PATH = HERE / "data" / "clean" / "seattle_decomposition.parquet"
RESULTS_PATH = HERE / "results.tsv"
SEATTLE_SWEEP = HERE / "discoveries" / "seattle_intervention_sweep.csv"
NYC_SWEEP = HERE / "discoveries" / "nyc_intervention_sweep.csv"

# Colourblind-safe palette (Wong 2011 / IBM Design)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_CYAN = "#56B4E9"
CB_YELLOW = "#F0E442"
CB_GREY = "#999999"

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 16,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "figure.dpi": 150,
})


# ---------------------------------------------------------------------------
# Helper: run the E00 baseline 5-fold CV and return out-of-fold predictions
# ---------------------------------------------------------------------------

def _get_baseline_oof() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run 5-fold CV on the baseline XGBoost, return (y_true_days, pred_days, cities)."""
    from model import RAW_FEATURES, add_features, make_baseline_xgb, target_encode

    df = pd.read_parquet(CLEAN_PATH).reset_index(drop=True)
    df = add_features(df)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(df), dtype="float64")

    for tr_idx, va_idx in kf.split(df):
        tr = df.iloc[tr_idx].copy()
        va = df.iloc[va_idx].copy()
        y_tr_log = np.log1p(tr["duration_days"].astype("float64").values)

        for col in ["permit_subtype", "neighborhood"]:
            tr[col + "_te"] = target_encode(tr, tr, col, y_tr_log)
            va[col + "_te"] = target_encode(tr, va, col, y_tr_log)

        X_tr = tr[RAW_FEATURES].astype("float32").values
        X_va = va[RAW_FEATURES].astype("float32").values

        m = make_baseline_xgb()
        m.fit(X_tr, y_tr_log)
        oof[va_idx] = m.predict(X_va)

    y_days = df["duration_days"].astype("float64").values
    pred_days = np.expm1(oof)
    cities = df["city"].values
    return y_days, pred_days, cities


def _get_feature_importance() -> tuple[list[str], np.ndarray]:
    """Train one full-sample XGBoost and return feature names + gain importances."""
    from model import RAW_FEATURES, add_features, make_baseline_xgb, target_encode

    df = pd.read_parquet(CLEAN_PATH).reset_index(drop=True)
    df = add_features(df)
    y_log = np.log1p(df["duration_days"].astype("float64").values)

    for col in ["permit_subtype", "neighborhood"]:
        df[col + "_te"] = target_encode(df, df, col, y_log)

    X = df[RAW_FEATURES].astype("float32").values
    m = make_baseline_xgb()
    m.fit(X, y_log)

    importances = m.feature_importances_
    return list(RAW_FEATURES), importances


def _get_seattle_oof() -> tuple[np.ndarray, np.ndarray]:
    """Run 5-fold CV on the Seattle 2-bucket model, return (y_true_days, pred_days)."""
    d = pd.read_parquet(SEATTLE_PATH).copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days", "days_plan_review_city", "days_out_corrections"])
    d = d[d["duration_days"] > 0].reset_index(drop=True)

    X = d[["days_plan_review_city", "days_out_corrections"]].astype("float64").values
    y_days = d["duration_days"].astype("float64").values
    y = np.log1p(y_days)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(d))
    for tr_idx, va_idx in kf.split(d):
        model = xgb.XGBRegressor(
            objective="reg:squarederror", max_depth=4, n_estimators=200,
            verbosity=0, n_jobs=4, random_state=42,
        )
        model.fit(X[tr_idx], y[tr_idx])
        oof[va_idx] = model.predict(X[va_idx])

    pred_days = np.expm1(oof)
    return y_days, pred_days


# ---------------------------------------------------------------------------
# Plot 1: Predicted vs Actual (cross-city baseline)
# ---------------------------------------------------------------------------

def plot_pred_vs_actual():
    print("  [1/6] Predicted vs Actual scatter ...")
    y_true, y_pred, cities = _get_baseline_oof()

    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(10, 8))

    city_colors = {
        "sf": CB_RED, "nyc": CB_BLUE, "la": CB_ORANGE,
        "chicago": CB_GREEN, "austin": CB_PURPLE,
    }
    city_labels = {
        "sf": "San Francisco", "nyc": "New York City", "la": "Los Angeles",
        "chicago": "Chicago", "austin": "Austin",
    }

    # Sub-sample for readability (50k points is too dense) and file size
    rng = np.random.default_rng(42)
    n_plot = min(5000, len(y_true))
    idx = rng.choice(len(y_true), size=n_plot, replace=False)

    for city_key in ["sf", "nyc", "la", "chicago", "austin"]:
        mask = np.array([cities[i] == city_key for i in idx])
        ax.scatter(
            y_true[idx[mask]], y_pred[idx[mask]],
            c=city_colors[city_key], label=city_labels[city_key],
            s=4, alpha=0.30, edgecolors="none", rasterized=True,
        )

    # 1:1 line
    lim_max = max(y_true.max(), y_pred.max()) * 1.02
    ax.plot([0, lim_max], [0, lim_max], "k--", lw=1.0, alpha=0.6, label="1:1 line")
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_xlabel("Actual duration (days)", fontsize=14)
    ax.set_ylabel("Predicted duration (days)", fontsize=14)
    ax.set_title(f"Cross-City Baseline: Predicted vs Actual\n"
                 f"MAE = {mae:.1f} days, R\u00b2 = {r2:.3f}")
    ax.legend(loc="upper left", fontsize=12, markerscale=3)
    ax.set_aspect("equal")

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "pred_vs_actual.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> plots/pred_vs_actual.png  (MAE={mae:.1f}, R2={r2:.3f})")


# ---------------------------------------------------------------------------
# Plot 2: Feature importance (top 15)
# ---------------------------------------------------------------------------

def plot_feature_importance():
    print("  [2/6] Feature importance bar chart ...")
    names, importances = _get_feature_importance()

    # Sort descending
    order = np.argsort(importances)[::-1]
    top_n = min(15, len(names))
    top_idx = order[:top_n]

    # Pretty names
    pretty = {
        "city_sf": "City: SF", "city_nyc": "City: NYC", "city_la": "City: LA",
        "city_chicago": "City: Chicago", "city_austin": "City: Austin",
        "filed_year": "Filed year", "filed_month_sin": "Filed month (sin)",
        "filed_month_cos": "Filed month (cos)",
        "log_valuation": "log(valuation USD)", "log_square_feet": "log(square feet)",
        "log_unit_count": "log(unit count)",
        "permit_subtype_te": "Permit subtype (TE)", "neighborhood_te": "Neighborhood (TE)",
    }

    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.4)))
    y_pos = np.arange(top_n)
    bars = ax.barh(
        y_pos,
        importances[top_idx],
        color=CB_BLUE, edgecolor="white", linewidth=0.5,
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels([pretty.get(names[i], names[i]) for i in top_idx], fontsize=12)
    ax.invert_yaxis()
    ax.set_xlabel("Feature importance (gain)", fontsize=14)
    ax.set_title("Cross-City Baseline XGBoost: Top Feature Importances", fontsize=16)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> plots/feature_importance.png")


# ---------------------------------------------------------------------------
# Plot 3: Headline finding -- Cross-city MAE comparison (with/without stages)
# ---------------------------------------------------------------------------

def plot_headline_finding():
    print("  [3/6] Headline finding: cross-city MAE comparison ...")

    # Data from results.tsv rows
    categories = [
        "Cross-city\nbaseline\n(5 cities, 13 feat.)",
        "Seattle\nno stages\n(metadata only)",
        "Seattle\n+ stages\n(14 feat.)",
        "Seattle\n2 buckets\n(2 feat.)",
        "NYC BIS\n4 stages\n(6 feat.)",
    ]
    mae_vals = [89.40, 99.86, 70.80, 24.68, 4.04]
    colors = [CB_GREY, CB_GREY, CB_CYAN, CB_BLUE, CB_ORANGE]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(categories))
    bars = ax.bar(x, mae_vals, color=colors, edgecolor="white", linewidth=0.8, width=0.65)

    # Annotate values on bars
    for bar, val in zip(bars, mae_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{val:.1f}",
            ha="center", va="bottom", fontsize=13, fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel("5-Fold CV MAE (days)", fontsize=14)
    ax.set_title("Stage-Level Data Collapses the Prediction Problem\n"
                 "Generic ML saturates at 89 days; 2 stage features reach 25 days",
                 fontsize=16)
    ax.set_ylim(0, 115)

    # Annotate the key improvement arrows
    ax.annotate(
        "4.0\u00d7", xy=(3, 24.68), xytext=(2.2, 55),
        fontsize=14, fontweight="bold", color=CB_RED,
        arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
        ha="center",
    )
    ax.annotate(
        "22\u00d7", xy=(4, 4.04), xytext=(4.3, 40),
        fontsize=14, fontweight="bold", color=CB_RED,
        arrowprops=dict(arrowstyle="->", color=CB_RED, lw=1.5),
        ha="center",
    )

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "headline_finding.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> plots/headline_finding.png")


# ---------------------------------------------------------------------------
# Plot 4: Duration by city (box plot)
# ---------------------------------------------------------------------------

def plot_duration_by_city():
    print("  [4/6] Duration by city box plot ...")
    df = pd.read_parquet(CLEAN_PATH)

    city_order = ["sf", "la", "chicago", "nyc", "austin"]
    city_labels = {
        "sf": "San Francisco", "la": "Los Angeles",
        "chicago": "Chicago", "nyc": "New York City", "austin": "Austin",
    }
    city_colors = {
        "sf": CB_RED, "nyc": CB_BLUE, "la": CB_ORANGE,
        "chicago": CB_GREEN, "austin": CB_PURPLE,
    }

    data_by_city = [df[df["city"] == c]["duration_days"].values for c in city_order]
    medians = [np.median(d) for d in data_by_city]

    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(
        data_by_city,
        positions=range(len(city_order)),
        widths=0.55,
        patch_artist=True,
        showfliers=False,  # hide outliers for readability
        medianprops=dict(color="black", linewidth=1.5),
    )
    for patch, city_key in zip(bp["boxes"], city_order):
        patch.set_facecolor(city_colors[city_key])
        patch.set_alpha(0.7)

    # Annotate medians
    for i, med in enumerate(medians):
        ax.text(i, med + 10, f"{med:.0f}d", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_xticks(range(len(city_order)))
    ax.set_xticklabels([city_labels[c] for c in city_order], fontsize=12)
    ax.set_ylabel("Permit duration (days)", fontsize=14)
    ax.set_title("Small-Residential Permit Duration by City\n"
                 "Outliers hidden; box = IQR, whiskers = 1.5\u00d7IQR")
    ax.set_ylim(0, 700)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "duration_by_city.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> plots/duration_by_city.png")


# ---------------------------------------------------------------------------
# Plot 5: Seattle per-stage variance decomposition
# ---------------------------------------------------------------------------

def plot_seattle_stage_decomposition():
    print("  [5/6] Seattle per-stage variance decomposition ...")

    # Univariate r-squared values from the decomposition analysis
    features = [
        "City plan review",
        "Total review cycles",
        "Number review cycles",
        "Total active days",
        "Drainage cycles",
        "Zoning cycles",
        "Drainage active days",
        "Applicant corrections",
        "Zoning active days",
        "Initial plan review",
    ]
    r2_vals = [39.2, 36.1, 35.5, 30.9, 24.4, 20.0, 18.6, 18.5, 16.0, 15.2]

    # Color: city-side vs applicant-side
    colors = [CB_BLUE if f != "Applicant corrections" else CB_ORANGE for f in features]

    n_bars = len(features)
    fig, ax = plt.subplots(figsize=(10, max(6, n_bars * 0.4)))
    y_pos = np.arange(len(features))
    bars = ax.barh(y_pos, r2_vals, color=colors, edgecolor="white", linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=12)
    ax.invert_yaxis()
    ax.set_xlabel("Univariate R\u00b2 (% of variance explained)", fontsize=14)
    ax.set_title("Seattle Per-Stage Variance Decomposition (n = 20,173)\n"
                 "Blue = city-side; orange = applicant-side")

    # Annotate values
    for bar, val in zip(bars, r2_vals):
        ax.text(
            bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center", fontsize=11,
        )

    ax.set_xlim(0, 48)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "seattle_stage_decomposition.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> plots/seattle_stage_decomposition.png")


# ---------------------------------------------------------------------------
# Plot 6: Phase 2 experiment waterfall (all 34 REVERT experiments)
# ---------------------------------------------------------------------------

def plot_phase2_waterfall():
    print("  [6/6] Phase 2 experiment delta waterfall ...")
    results = pd.read_csv(RESULTS_PATH, sep="\t")

    # Get all experiments that have numeric MAE and are REVERT
    mask = results["notes"].str.contains("REVERT", na=False)
    reverts = results[mask].copy()
    reverts["cv_mae_days"] = pd.to_numeric(reverts["cv_mae_days"], errors="coerce")
    reverts = reverts.dropna(subset=["cv_mae_days"])
    reverts = reverts[reverts["exp_id"].str.startswith(("H", "T"))].copy()

    # Compute delta from baseline
    baseline_mae = 89.401
    reverts["delta"] = reverts["cv_mae_days"] - baseline_mae
    reverts = reverts.sort_values("delta")

    # Pick the 25 most interesting (closest to threshold and farthest)
    n_show = min(25, len(reverts))
    show = reverts.head(n_show)

    fig, ax = plt.subplots(figsize=(12, max(6, n_show * 0.35)))
    y_pos = np.arange(n_show)
    colors = [CB_GREEN if d < 0 else CB_RED for d in show["delta"].values]

    ax.barh(y_pos, show["delta"].values, color=colors, edgecolor="white", linewidth=0.5)

    # Labels
    labels = []
    for _, row in show.iterrows():
        desc = row["description"]
        if len(desc) > 35:
            desc = desc[:32] + "..."
        labels.append(f"{row['exp_id']}: {desc}")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()

    # Keep threshold line
    keep_thr = -0.89
    ax.axvline(keep_thr, color=CB_RED, linestyle="--", lw=1.5, alpha=0.7, label=f"KEEP threshold ({keep_thr:.2f}d)")
    ax.axvline(0, color="black", lw=0.8, alpha=0.5)

    ax.set_xlabel("\u0394 MAE vs baseline (days); negative = improvement")
    ax.set_title("Phase 2: All Reverted Experiments by MAE Change\n"
                 "None cleared the KEEP threshold (dashed red)")
    ax.legend(loc="lower right", fontsize=12)

    fig.tight_layout(pad=2.0)
    fig.savefig(PLOTS_DIR / "phase2_waterfall.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> plots/phase2_waterfall.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating plots for building-permits paper ...")
    plot_pred_vs_actual()
    plot_feature_importance()
    plot_headline_finding()
    plot_duration_by_city()
    plot_seattle_stage_decomposition()
    plot_phase2_waterfall()

    # Report file sizes
    print("\nPlot file sizes:")
    for p in sorted(PLOTS_DIR.glob("*.png")):
        size_kb = p.stat().st_size / 1024
        flag = " [!>500KB]" if size_kb > 500 else ""
        print(f"  {p.name:40s} {size_kb:6.1f} KB{flag}")
    print("\nDone.")


if __name__ == "__main__":
    main()
