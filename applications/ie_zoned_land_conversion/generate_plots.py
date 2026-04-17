"""
Generate all plots for IE Zoned Land Conversion paper.
Reads results.tsv and cached data; produces PNGs in plots/.
"""
import sys
sys.path.insert(0, "/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from load_data import (
    load_planning_register, get_planning_by_la_year,
    GOODBODY, LA_REGION, DUBLIN_LAS, LA_POPULATION_2022
)

PROJECT_DIR = Path("/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion")
PLOTS_DIR = PROJECT_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
COLORS = plt.cm.tab10.colors
DPI = 300

# ── Load data ──
print("Loading data for plots...")
pl = load_planning_register()
agg = get_planning_by_la_year(pl, year_range=(2015, 2025))

region_ha = {
    "East+Midlands": GOODBODY["east_midlands_ha"],
    "Southern": GOODBODY["southern_ha"],
    "Northern+Western": GOODBODY["north_western_ha"],
}

# ═══════════════════════════════════════════════════════════
# Plot 1: Headline Finding — Application intensity by region
# ═══════════════════════════════════════════════════════════
print("Plot 1: Regional application intensity (headline)...")
regional = agg[agg["ReceivedYear"].between(2018, 2024)].groupby("Region").agg(
    total_res_apps=("residential_permission_applications", "sum"),
).reset_index()
regional["zoned_ha"] = regional["Region"].map(region_ha)
regional["annual_apps"] = regional["total_res_apps"] / 7
regional["apps_per_ha"] = regional["annual_apps"] / regional["zoned_ha"]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(regional["Region"], regional["apps_per_ha"],
               color=[COLORS[0], COLORS[1], COLORS[2]], edgecolor="white", linewidth=0.5)

# Add national average line
national_rate = (regional["total_res_apps"].sum() / 7) / GOODBODY["total_zoned_ha"]
ax.axvline(national_rate, color="black", linestyle="--", linewidth=1.5, label=f"National avg: {national_rate:.2f}")

for bar, val in zip(bars, regional["apps_per_ha"]):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}", va="center", fontsize=11, fontweight="bold")

ax.set_xlabel("Residential applications per hectare of zoned land per year", fontsize=11)
ax.set_title("")
ax.legend(fontsize=10)
ax.set_xlim(0, max(regional["apps_per_ha"]) * 1.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "headline_finding.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 2: Time series of residential applications
# ═══════════════════════════════════════════════════════════
print("Plot 2: Time series...")
annual = agg.groupby("ReceivedYear")["residential_permission_applications"].sum()
annual = annual.loc[2015:2025]

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(annual.index, annual.values, color=COLORS[0], alpha=0.7, edgecolor="white")
ax.axhline(annual.loc[2018:2024].mean(), color="red", linestyle="--", linewidth=1.5,
           label=f"2018-2024 mean: {annual.loc[2018:2024].mean():,.0f}")
ax.axvline(2021.5, color="grey", linestyle=":", linewidth=1, label="RZLT announced (2022)")
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Residential permission applications", fontsize=11)
ax.legend(fontsize=10)
ax.set_xticks(range(2015, 2026))
plt.tight_layout()
plt.savefig(PLOTS_DIR / "time_series.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 3: LA ranking by application intensity
# ═══════════════════════════════════════════════════════════
print("Plot 3: LA ranking...")
# Build LA zoned ha
region_pop = {}
for la, reg in LA_REGION.items():
    pop = LA_POPULATION_2022.get(la, 0)
    region_pop.setdefault(reg, 0)
    region_pop[reg] += pop

la_zoned = {}
for la, reg in LA_REGION.items():
    pop = LA_POPULATION_2022.get(la, 0)
    rpop = region_pop.get(reg, 1)
    la_zoned[la] = region_ha.get(reg, 0) * pop / rpop
la_zoned["Fingal County Council"] = GOODBODY["fingal_ha"]

la_panel = agg[agg["ReceivedYear"].between(2018, 2024)].copy()
la_panel["zoned_ha"] = la_panel["Planning Authority"].map(la_zoned)
la_panel["apps_per_ha"] = la_panel["residential_permission_applications"] / la_panel["zoned_ha"].replace(0, np.nan)

la_ranked = la_panel.groupby("Planning Authority").agg(
    mean_intensity=("apps_per_ha", "mean"),
    region=("Region", "first"),
).dropna().sort_values("mean_intensity")

region_colors = {"East+Midlands": COLORS[0], "Southern": COLORS[1], "Northern+Western": COLORS[2]}
bar_colors = [region_colors.get(r, "grey") for r in la_ranked["region"]]

fig, ax = plt.subplots(figsize=(10, 10))
bars = ax.barh(range(len(la_ranked)), la_ranked["mean_intensity"],
               color=bar_colors, edgecolor="white", linewidth=0.3)
ax.set_yticks(range(len(la_ranked)))
ax.set_yticklabels([la.replace(" County Council", "").replace(" City Council", " City").replace(" City and County Council", " City+Co")
                     for la in la_ranked.index], fontsize=9)
ax.axvline(national_rate, color="black", linestyle="--", linewidth=1.5, alpha=0.7)
ax.set_xlabel("Residential applications per hectare of zoned land per year", fontsize=11)

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=COLORS[0], label="East+Midlands"),
                   Patch(facecolor=COLORS[1], label="Southern"),
                   Patch(facecolor=COLORS[2], label="Northern+Western")]
ax.legend(handles=legend_elements, loc="lower right", fontsize=10)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "la_ranking.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 4: Capacity utilization waterfall
# ═══════════════════════════════════════════════════════════
print("Plot 4: Capacity utilization...")
fig, ax = plt.subplots(figsize=(8, 5))

categories = ["Zoned capacity\n(417k units)", "Filed per year\n(~36k units)", "Gap\n(~381k units)"]
values = [GOODBODY["potential_units"], 35838, GOODBODY["potential_units"] - 35838]
colors_wf = [COLORS[0], COLORS[1], COLORS[3]]

ax.bar(categories, values, color=colors_wf, edgecolor="white", width=0.6)
for i, v in enumerate(values):
    ax.text(i, v + 5000, f"{v:,.0f}", ha="center", fontsize=11, fontweight="bold")

ax.set_ylabel("Residential units", fontsize=11)
ax.set_ylim(0, GOODBODY["potential_units"] * 1.15)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k"))
plt.tight_layout()
plt.savefig(PLOTS_DIR / "capacity_utilization.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 5: Predicted vs actual (OLS panel)
# ═══════════════════════════════════════════════════════════
print("Plot 5: Predicted vs actual...")
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

panel = agg[agg["ReceivedYear"].between(2018, 2024)].copy()
panel["zoned_ha"] = panel["Planning Authority"].map(la_zoned)
panel["population"] = panel["Planning Authority"].map(LA_POPULATION_2022)
panel = panel.dropna(subset=["zoned_ha", "population"])

X = panel[["zoned_ha", "population"]].values
y = panel["residential_permission_applications"].values

scaler = StandardScaler()
X_s = scaler.fit_transform(X)
ols = LinearRegression()
ols.fit(X_s, y)
y_pred = ols.predict(X_s)

fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(y, y_pred, alpha=0.4, s=20, color=COLORS[0])
lims = [0, max(y.max(), y_pred.max()) * 1.1]
ax.plot(lims, lims, "k--", linewidth=1, label="1:1 line")
ax.set_xlabel("Actual residential applications", fontsize=11)
ax.set_ylabel("Predicted (OLS: zoned_ha + population)", fontsize=11)
ax.set_xlim(lims)
ax.set_ylim(lims)
r2 = ols.score(X_s, y)
ax.text(0.05, 0.95, f"R² = {r2:.3f}", transform=ax.transAxes, fontsize=12,
        verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "pred_vs_actual.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 6: Feature importance (panel model coefficients)
# ═══════════════════════════════════════════════════════════
print("Plot 6: Feature importance...")
fig, ax = plt.subplots(figsize=(8, 4))

# Standardized coefficients as importance
feature_names = ["Zoned land (ha)", "Population"]
importance = np.abs(ols.coef_)

idx = np.argsort(importance)
ax.barh([feature_names[i] for i in idx], importance[idx], color=COLORS[0])
ax.set_xlabel("Absolute standardized coefficient", fontsize=11)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "feature_importance.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 7: Seasonal pattern
# ═══════════════════════════════════════════════════════════
print("Plot 7: Seasonal pattern...")
res_seasonal = pl[pl["is_residential"] & pl["ReceivedYear"].between(2018, 2024)].copy()
res_seasonal["month"] = res_seasonal["ReceivedDate"].dt.month
monthly = res_seasonal.groupby("month").size()
monthly_pct = monthly / monthly.sum() * 100

fig, ax = plt.subplots(figsize=(8, 4))
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ax.bar(months, [monthly_pct.get(i+1, 0) for i in range(12)], color=COLORS[0], edgecolor="white")
ax.axhline(100/12, color="red", linestyle="--", linewidth=1, label="Uniform (8.33%)")
ax.set_ylabel("Share of annual applications (%)", fontsize=11)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "seasonal_pattern.png", dpi=DPI, bbox_inches="tight")
plt.close()

# ═══════════════════════════════════════════════════════════
# Plot 8: One-off vs multi-unit vs apartment breakdown
# ═══════════════════════════════════════════════════════════
print("Plot 8: Application type breakdown...")
res_apps = pl[pl["is_residential"] & pl["ReceivedYear"].between(2018, 2024)]
oneoff = res_apps["is_one_off"].sum()
multi = res_apps["is_multi_unit"].sum()
other = len(res_apps) - oneoff - multi

fig, ax = plt.subplots(figsize=(7, 5))
sizes = [oneoff, multi, other]
labels = [f"One-off houses\n({oneoff/len(res_apps)*100:.1f}%)",
          f"Multi-unit\n({multi/len(res_apps)*100:.1f}%)",
          f"Other residential\n({other/len(res_apps)*100:.1f}%)"]
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct="",
                                    colors=[COLORS[0], COLORS[1], COLORS[2]],
                                    startangle=90, textprops={"fontsize": 11})
plt.tight_layout()
plt.savefig(PLOTS_DIR / "app_type_breakdown.png", dpi=DPI, bbox_inches="tight")
plt.close()

print(f"\nAll plots saved to {PLOTS_DIR}/")
print("Files:", [f.name for f in PLOTS_DIR.glob("*.png")])
