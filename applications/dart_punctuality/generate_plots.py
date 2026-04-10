"""
Generate publication-quality plots for the DART punctuality HDR project.

Produces five figures in plots/:
  1. pred_vs_actual.png     — predicted vs actual bad-day probability scatter
  2. feature_importance.png — top feature importances from XGBoost
  3. headline_finding.png   — monthly punctuality time series with timetable-change line
  4. cascade_risk_calendar.png — risk heatmap by day-of-week and month
  5. timetable_vs_weather.png  — feature importance comparison: timetable dwarfs weather

Style: seaborn-v0_8-whitegrid, colourblind-safe palette, 300 DPI.

Usage:
    python generate_plots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

APP_DIR = Path(__file__).resolve().parent
PLOTS_DIR = APP_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, MONTHLY_PUNCTUALITY, TIMETABLE_CHANGE_DATE
from model import prepare_features, get_feature_columns, build_model, get_model_config
from evaluate import _get_proba, get_train_test_split

# ---------------------------------------------------------------------------
# Style setup
# ---------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid")
# Colourblind-safe palette (IBM Design / Wong)
CB_PALETTE = ["#0072B2", "#D55E00", "#009E73", "#E69F00",
              "#56B4E9", "#CC79A7", "#F0E442", "#000000"]
sns.set_palette(CB_PALETTE)
DPI = 300


def _load_and_prepare() -> tuple[pd.DataFrame, object, list[str]]:
    """Load data, prepare features, train the full model."""
    df = load_dataset()
    df = prepare_features(df)
    config = get_model_config()
    feature_cols = get_feature_columns()
    X = df[feature_cols].values.astype(np.float32)
    y = df["bad_day"].values
    model = build_model(config)
    model.fit(X, y)
    return df, model, feature_cols


# =========================================================================
# Plot 1: Predicted vs Actual bad-day probability
# =========================================================================
def plot_pred_vs_actual(df: pd.DataFrame, model, feature_cols: list[str]) -> None:
    """Scatter of predicted bad-day probability vs actual daily punctuality."""
    X = df[feature_cols].values.astype(np.float32)
    proba = _get_proba(model, X, "xgboost")

    fig, ax = plt.subplots(figsize=(7, 6))

    # Colour by actual bad_day status
    colours = np.where(df["bad_day"].values == 1, CB_PALETTE[1], CB_PALETTE[0])
    ax.scatter(
        df["daily_punctuality"].values, proba,
        c=colours, alpha=0.45, s=18, edgecolors="none", rasterized=True,
    )

    # Reference lines
    ax.axhline(0.5, color="grey", ls="--", lw=0.8, label="Decision threshold (P=0.5)")
    ax.axvline(0.85, color="grey", ls=":", lw=0.8, label="Bad-day threshold (85%)")

    # Legend proxy artists
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=CB_PALETTE[1],
               markersize=7, label="Bad day (punct < 85%)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=CB_PALETTE[0],
               markersize=7, label="Normal day"),
        Line2D([0], [0], color="grey", ls="--", lw=0.8, label="Decision threshold"),
        Line2D([0], [0], color="grey", ls=":", lw=0.8, label="Bad-day boundary (85%)"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8, framealpha=0.9)

    ax.set_xlabel("Actual Daily Punctuality", fontsize=11)
    ax.set_ylabel("Predicted Bad-Day Probability", fontsize=11)
    ax.set_title("Predicted vs Actual: Bad-Day Classification", fontsize=13, fontweight="bold")
    ax.set_xlim(0.28, 1.02)
    ax.set_ylim(-0.05, 1.05)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "pred_vs_actual.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/pred_vs_actual.png")


# =========================================================================
# Plot 2: Feature importance (top features)
# =========================================================================
def plot_feature_importance(model, feature_cols: list[str]) -> None:
    """Horizontal bar chart of XGBoost feature importances."""
    importances = model.feature_importances_
    pairs = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)

    # Take top 15
    top_n = 15
    names = [p[0] for p in pairs[:top_n]][::-1]
    values = [p[1] for p in pairs[:top_n]][::-1]

    # Colour-code: timetable=orange, weather=blue, cascade=green, other=grey
    timetable_feats = {"post_timetable_change", "post_change_x_wind"}
    weather_feats = {"wind_speed_kmh", "rainfall_mm", "temperature_c",
                     "wind_above_50", "rain_above_10", "wind_dir_coastal_exposure",
                     "is_stormy", "is_frost"}
    cascade_feats = {"morning_punct", "morning_afternoon_gap", "prev_day_punct",
                     "prev_day_bad", "rolling_7d_punct", "rolling_7d_bad_count",
                     "rolling_7d_bad_rate", "rolling_3d_punct", "prev_day_bad_x_monday"}

    bar_colours = []
    for n in names:
        if n in timetable_feats:
            bar_colours.append(CB_PALETTE[1])  # orange
        elif n in weather_feats:
            bar_colours.append(CB_PALETTE[0])  # blue
        elif n in cascade_feats:
            bar_colours.append(CB_PALETTE[2])  # green
        else:
            bar_colours.append(CB_PALETTE[4])  # light blue

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(range(len(names)), values, color=bar_colours, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Feature Importance (gain)", fontsize=11)
    ax.set_title("Top Feature Importances: XGBoost Model", fontsize=13, fontweight="bold")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CB_PALETTE[1], label="Timetable regime"),
        Patch(facecolor=CB_PALETTE[0], label="Weather"),
        Patch(facecolor=CB_PALETTE[2], label="Cascade / system state"),
        Patch(facecolor=CB_PALETTE[4], label="Temporal / other"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8, framealpha=0.9)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/feature_importance.png")


# =========================================================================
# Plot 3: Headline finding — monthly punctuality with timetable-change line
# =========================================================================
def plot_headline_finding(df: pd.DataFrame) -> None:
    """Monthly DART punctuality time series with Sep 2024 timetable change marked."""
    monthly = df.groupby([df.index.year, df.index.month])["daily_punctuality"].mean()
    dates = [pd.Timestamp(year=y, month=m, day=15) for (y, m) in monthly.index]
    values = monthly.values * 100  # percent

    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot line with markers
    ax.plot(dates, values, color=CB_PALETTE[0], linewidth=2.2, marker="o",
            markersize=5, markerfacecolor=CB_PALETTE[0], markeredgecolor="white",
            markeredgewidth=0.8, zorder=3, label="DART monthly punctuality")

    # Timetable change vertical line
    change_dt = pd.Timestamp(TIMETABLE_CHANGE_DATE)
    ax.axvline(change_dt, color=CB_PALETTE[1], ls="--", lw=2.0, zorder=2,
               label="September 2024 timetable change")

    # Shade pre and post regions
    ax.axvspan(dates[0], change_dt, alpha=0.06, color=CB_PALETTE[2], zorder=0)
    ax.axvspan(change_dt, dates[-1], alpha=0.06, color=CB_PALETTE[1], zorder=0)

    # 90% target line
    ax.axhline(90, color=CB_PALETTE[2], ls=":", lw=1.2, alpha=0.7,
               label="NTA 90% target")

    # Annotations
    # Pre-change high point
    pre_peak_idx = np.argmax([v if d < change_dt else 0 for d, v in zip(dates, values)])
    ax.annotate(
        f"{values[pre_peak_idx]:.1f}%",
        xy=(dates[pre_peak_idx], values[pre_peak_idx]),
        xytext=(0, 14), textcoords="offset points",
        fontsize=9, fontweight="bold", color=CB_PALETTE[2],
        ha="center",
        arrowprops=dict(arrowstyle="-", color=CB_PALETTE[2], lw=0.8),
    )

    # Post-change low point
    post_low_idx = np.argmin([v if d >= change_dt else 100 for d, v in zip(dates, values)])
    ax.annotate(
        f"{values[post_low_idx]:.1f}%",
        xy=(dates[post_low_idx], values[post_low_idx]),
        xytext=(0, -18), textcoords="offset points",
        fontsize=9, fontweight="bold", color=CB_PALETTE[1],
        ha="center",
        arrowprops=dict(arrowstyle="-", color=CB_PALETTE[1], lw=0.8),
    )

    # Text labels for pre/post
    ax.text(
        pd.Timestamp("2023-10-01"), 97,
        "Pre-change\n~93% punctuality",
        fontsize=9, color=CB_PALETTE[2], ha="center", fontstyle="italic",
    )
    ax.text(
        pd.Timestamp("2025-04-01"), 58,
        "Post-change\n~65-80% punctuality",
        fontsize=9, color=CB_PALETTE[1], ha="center", fontstyle="italic",
    )

    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Monthly Punctuality (%)", fontsize=11)
    ax.set_title(
        "DART Punctuality Collapse: September 2024 Timetable Change",
        fontsize=13, fontweight="bold",
    )
    ax.set_ylim(55, 100)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=35, ha="right")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.9)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "headline_finding.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/headline_finding.png")


# =========================================================================
# Plot 4: Cascade risk calendar — heatmap by DOW x month
# =========================================================================
def plot_cascade_risk_calendar(df: pd.DataFrame, model, feature_cols: list[str]) -> None:
    """Heatmap of predicted cascade risk by day-of-week and month."""
    X = df[feature_cols].values.astype(np.float32)
    risk = _get_proba(model, X, "xgboost")

    df_plot = df.copy()
    df_plot["risk"] = risk
    df_plot["dow"] = df_plot.index.dayofweek
    df_plot["month"] = df_plot.index.month

    pivot = df_plot.pivot_table(values="risk", index="dow", columns="month", aggfunc="mean")

    dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto", vmin=0.15, vmax=0.90)

    ax.set_xticks(range(12))
    ax.set_xticklabels(month_labels, fontsize=9)
    ax.set_yticks(range(7))
    ax.set_yticklabels(dow_labels, fontsize=9)

    # Annotate cells
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            if not np.isnan(val):
                text_colour = "white" if val > 0.55 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=8, color=text_colour, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Mean Predicted Bad-Day Probability", fontsize=10)

    ax.set_title("Cascade Risk Calendar: Day-of-Week x Month", fontsize=13, fontweight="bold")

    # Mark the timetable-change month
    # September = column index 8 (0-indexed)
    from matplotlib.patches import Rectangle
    rect = Rectangle((7.5, -0.5), 4, 7, linewidth=2.5, edgecolor=CB_PALETTE[1],
                      facecolor="none", linestyle="--", zorder=5)
    ax.add_patch(rect)
    ax.text(9.5, -0.85, "Post-change months", fontsize=8, color=CB_PALETTE[1],
            ha="center", fontweight="bold")

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "cascade_risk_calendar.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/cascade_risk_calendar.png")


# =========================================================================
# Plot 5: Timetable vs weather — grouped feature importance comparison
# =========================================================================
def plot_timetable_vs_weather(model, feature_cols: list[str]) -> None:
    """Compare grouped feature importance: timetable regime vs weather vs cascade."""
    importances = dict(zip(feature_cols, model.feature_importances_))

    # Group features
    groups = {
        "Timetable\nregime": ["post_timetable_change", "post_change_x_wind"],
        "Cascade /\nsystem state": [
            "morning_punct", "morning_afternoon_gap", "prev_day_punct",
            "prev_day_bad", "rolling_7d_punct", "rolling_7d_bad_count",
            "rolling_7d_bad_rate", "rolling_3d_punct", "prev_day_bad_x_monday",
        ],
        "Weather": [
            "wind_speed_kmh", "rainfall_mm", "temperature_c",
            "wind_above_50", "rain_above_10", "wind_dir_coastal_exposure",
        ],
        "Temporal /\ndemand": [
            "dow_sin", "dow_cos", "month_sin", "month_cos",
            "is_weekend", "is_monday", "is_friday", "year",
            "is_school_term",
        ],
    }

    group_sums = {}
    for grp, feats in groups.items():
        total = sum(importances.get(f, 0.0) for f in feats)
        group_sums[grp] = total

    grp_names = list(group_sums.keys())
    grp_vals = [group_sums[g] for g in grp_names]
    grp_colours = [CB_PALETTE[1], CB_PALETTE[2], CB_PALETTE[0], CB_PALETTE[4]]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.3, 1]})

    # Left: bar chart
    ax = axes[0]
    bars = ax.bar(range(len(grp_names)), grp_vals, color=grp_colours,
                  edgecolor="white", linewidth=1.2, width=0.65)
    ax.set_xticks(range(len(grp_names)))
    ax.set_xticklabels(grp_names, fontsize=10)
    ax.set_ylabel("Aggregate Feature Importance (gain)", fontsize=11)
    ax.set_title("Feature Group Importance", fontsize=13, fontweight="bold")

    # Annotate bars with values and percentages
    total_imp = sum(grp_vals)
    for bar, val in zip(bars, grp_vals):
        pct = val / total_imp * 100
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f"{val:.3f}\n({pct:.1f}%)", ha="center", va="bottom",
                fontsize=9, fontweight="bold")

    ax.set_ylim(0, max(grp_vals) * 1.25)

    # Right: individual feature breakdown within timetable and weather groups
    ax2 = axes[1]

    # Show individual features for timetable and weather side by side
    tt_feats = groups["Timetable\nregime"]
    wx_feats = groups["Weather"]

    all_feats = tt_feats + wx_feats
    all_vals = [importances.get(f, 0.0) for f in all_feats]
    all_colours = [CB_PALETTE[1]] * len(tt_feats) + [CB_PALETTE[0]] * len(wx_feats)

    # Sort by importance
    sorted_pairs = sorted(zip(all_feats, all_vals, all_colours),
                          key=lambda x: x[1], reverse=True)
    s_names = [p[0] for p in sorted_pairs][::-1]
    s_vals = [p[1] for p in sorted_pairs][::-1]
    s_colours = [p[2] for p in sorted_pairs][::-1]

    ax2.barh(range(len(s_names)), s_vals, color=s_colours,
             edgecolor="white", linewidth=0.5)
    ax2.set_yticks(range(len(s_names)))
    ax2.set_yticklabels(s_names, fontsize=9)
    ax2.set_xlabel("Feature Importance (gain)", fontsize=11)
    ax2.set_title("Timetable vs Weather: Individual Features", fontsize=13, fontweight="bold")

    from matplotlib.patches import Patch
    ax2.legend(
        handles=[
            Patch(facecolor=CB_PALETTE[1], label="Timetable regime"),
            Patch(facecolor=CB_PALETTE[0], label="Weather"),
        ],
        loc="lower right", fontsize=9, framealpha=0.9,
    )

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "timetable_vs_weather.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  Saved plots/timetable_vs_weather.png")


# =========================================================================
# Main
# =========================================================================
def main():
    print("=" * 60)
    print("  DART Punctuality — Generating Plots")
    print("=" * 60)

    df, model, feature_cols = _load_and_prepare()

    print("\n  Generating plots...")
    plot_pred_vs_actual(df, model, feature_cols)
    plot_feature_importance(model, feature_cols)
    plot_headline_finding(df)
    plot_cascade_risk_calendar(df, model, feature_cols)
    plot_timetable_vs_weather(model, feature_cols)

    print("\n  All plots saved to plots/")
    print("=" * 60)


if __name__ == "__main__":
    main()
