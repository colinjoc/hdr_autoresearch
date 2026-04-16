#!/usr/bin/env python3
"""
Generate plots for IE Housing Pipeline E2E paper.

Reads results.tsv and cached analysis data to produce publication-quality PNGs.
"""

import os, pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid")

PROJECT = pathlib.Path(__file__).resolve().parent
PLOTS = PROJECT / "plots"
PLOTS.mkdir(exist_ok=True)

PRED_CN = pathlib.Path("/home/col/generalized_hdr_autoresearch/applications/ie_commencement_notices/data/raw")

# Load BCMS data
print("Loading BCMS data...")
bcms = pd.read_csv(PRED_CN / "bcms_notices.csv", low_memory=False)
res_keywords = ["1_residential_dwellings", "2_residential_institutional", "3_residential_other"]
bcms["is_res"] = bcms["CN_Proposed_use_of_building"].astype(str).apply(
    lambda x: any(k in x for k in res_keywords)
)
br = bcms[bcms["is_res"]].copy()
for col in ["CN_Date_Granted", "CN_Commencement_Date", "CCC_Date_Validated"]:
    br[col] = pd.to_datetime(br[col], format="mixed", errors="coerce")
br["grant_year"] = br["CN_Date_Granted"].dt.year
br = br[br["grant_year"].between(2014, 2019)].copy()
br["has_ccc"] = br["CCC_Date_Validated"].notna()
br["days_perm_to_ccc"] = (br["CCC_Date_Validated"] - br["CN_Date_Granted"]).dt.days
br["units"] = pd.to_numeric(br["CN_Total_Number_of_Dwelling_Units"], errors="coerce").fillna(1).astype(int)

def size_stratum(u):
    if u <= 1: return "1"
    elif u <= 9: return "2-9"
    elif u <= 49: return "10-49"
    elif u <= 199: return "50-199"
    else: return "200+"
br["size_stratum"] = br["units"].apply(size_stratum)
br["opt_out"] = br["CN_Project_type"].astype(str).str.contains("Opt_Out", case=False, na=False)
br["la_clean"] = br["LocalAuthority"].astype(str).str.strip()

results = pd.read_csv(PROJECT / "results.tsv", sep="\t")

# ── Plot 1: Funnel / stage-by-stage attrition (headline finding) ────────
print("Plot 1: Pipeline funnel...")
fig, ax = plt.subplots(figsize=(8, 5))

stages = ["Permissions\ngranted", "Commenced\n(CN filed)", "CCC\nfiled", "Occupied\n(est.)"]
# Using best-estimate rates
rates = [1.00, 0.9051, 0.9051 * 0.4086, 0.9051 * 0.4086 * 0.95]
colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]

bars = ax.bar(stages, [r * 100 for r in rates], color=colors, width=0.6, edgecolor="white", linewidth=1.5)
for bar, rate in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f"{rate:.1%}", ha="center", va="bottom", fontsize=12, fontweight="bold")

# Add attrition labels between bars
for i in range(len(rates)-1):
    loss = rates[i] - rates[i+1]
    mid_x = i + 0.5
    ax.annotate(f"-{loss:.1%}",
                xy=(mid_x, (rates[i] + rates[i+1]) / 2 * 100),
                fontsize=9, color="red", ha="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

ax.set_ylabel("Share of original permissions (%)", fontsize=12)
ax.set_title("Irish Housing Pipeline Funnel (2014-2019 Permission Cohort)", fontsize=13, fontweight="bold")
ax.set_ylim(0, 115)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "headline_finding.png", dpi=300, bbox_inches="tight")
plt.close()

# ── Plot 2: CCC rate by size stratum (feature importance proxy) ─────────
print("Plot 2: CCC rate by size stratum...")
fig, ax = plt.subplots(figsize=(8, 5))

size_data = br.groupby("size_stratum").agg(
    n=("has_ccc", "count"), ccc=("has_ccc", "sum")
).reset_index()
size_data["rate"] = size_data["ccc"] / size_data["n"]

# Order the strata
order = ["1", "2-9", "10-49", "50-199", "200+"]
size_data["order"] = size_data["size_stratum"].map({s: i for i, s in enumerate(order)})
size_data = size_data.sort_values("order")

colors_size = ["#E53935", "#FF9800", "#4CAF50", "#2196F3", "#1565C0"]
bars = ax.barh(size_data["size_stratum"], size_data["rate"] * 100,
               color=colors_size, edgecolor="white", linewidth=1.5, height=0.6)

for bar, (_, row) in zip(bars, size_data.iterrows()):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            f"{row['rate']:.1%} (n={int(row['n']):,})",
            va="center", fontsize=10)

ax.set_xlabel("CCC Filing Rate (%)", fontsize=12)
ax.set_ylabel("Scheme Size (units)", fontsize=12)
ax.set_title("CCC Filing Rate by Scheme Size (2014-2019 Commenced Projects)", fontsize=13, fontweight="bold")
ax.set_xlim(0, 105)
ax.invert_yaxis()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "feature_importance.png", dpi=300, bbox_inches="tight")
plt.close()

# ── Plot 3: Predicted vs actual (CCC rate by year: model vs observed) ───
print("Plot 3: Model vs observed yield by year...")
fig, ax = plt.subplots(figsize=(7, 6))

yr_data = br.groupby("grant_year").agg(
    n=("has_ccc", "count"), ccc=("has_ccc", "sum")
).reset_index()
yr_data["observed_rate"] = yr_data["ccc"] / yr_data["n"]

# Model prediction: using overall stage rates
# The "model" prediction is the same stage1_to_2 × ccc_rate × stage3_to_4
# applied uniformly (the binomial model)
lapse = 0.0949
s34 = 0.95
model_yield = (1 - lapse) * yr_data["observed_rate"] * s34  # CCC rate varies by year

ax.scatter(yr_data["observed_rate"] * 100, model_yield * 100,
           s=120, c="#2196F3", zorder=5, edgecolors="white", linewidth=1.5)

for _, row in yr_data.iterrows():
    ax.annotate(int(row["grant_year"]),
                (row["observed_rate"] * 100, (1 - lapse) * row["observed_rate"] * s34 * 100),
                textcoords="offset points", xytext=(8, 5), fontsize=10)

# 1:1 line (if model perfectly predicted observed CCC rate to yield)
lims = [0, 50]
ax.plot(lims, [(1-lapse)*x/100*s34*100 for x in lims], "k--", alpha=0.5, linewidth=1, label="Model: yield = 0.86 × CCC_rate")
ax.plot(lims, lims, "r:", alpha=0.3, linewidth=1, label="1:1 line")

ax.set_xlabel("Observed CCC Rate (%)", fontsize=12)
ax.set_ylabel("Modelled Pipeline Yield (%)", fontsize=12)
ax.set_title("Modelled Yield vs Observed CCC Rate by Grant Year", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.set_xlim(33, 50)
ax.set_ylim(28, 42)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "pred_vs_actual.png", dpi=300, bbox_inches="tight")
plt.close()

# ── Plot 4: Pipeline duration distribution ───────────────────────────────
print("Plot 4: Pipeline duration distribution...")
fig, ax = plt.subplots(figsize=(8, 5))

complete = br[(br["days_perm_to_ccc"].notna()) & (br["days_perm_to_ccc"] > 0) & (br["days_perm_to_ccc"] < 4000)]
ax.hist(complete["days_perm_to_ccc"], bins=80, color="#2196F3", alpha=0.7, edgecolor="white", linewidth=0.5)

# Mark median and IQR
med = complete["days_perm_to_ccc"].median()
q25 = np.percentile(complete["days_perm_to_ccc"], 25)
q75 = np.percentile(complete["days_perm_to_ccc"], 75)

ax.axvline(med, color="red", linewidth=2, label=f"Median: {med:.0f}d ({med/365:.1f}yr)")
ax.axvline(q25, color="orange", linewidth=1.5, linestyle="--", label=f"Q25: {q25:.0f}d")
ax.axvline(q75, color="orange", linewidth=1.5, linestyle="--", label=f"Q75: {q75:.0f}d")

ax.set_xlabel("Days from Permission Grant to CCC", fontsize=12)
ax.set_ylabel("Number of Projects", fontsize=12)
ax.set_title("Pipeline Duration Distribution: Permission to Completion Certificate", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "duration_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

# ── Plot 5: CCC rate by grant year ──────────────────────────────────────
print("Plot 5: CCC rate by grant year...")
fig, ax = plt.subplots(figsize=(8, 5))

ax.bar(yr_data["grant_year"], yr_data["observed_rate"] * 100,
       color="#4CAF50", edgecolor="white", linewidth=1.5, width=0.7)

for _, row in yr_data.iterrows():
    ax.text(row["grant_year"], row["observed_rate"] * 100 + 1,
            f"{row['observed_rate']:.1%}", ha="center", fontsize=10, fontweight="bold")

ax.set_xlabel("Permission Grant Year", fontsize=12)
ax.set_ylabel("CCC Filing Rate (%)", fontsize=12)
ax.set_title("CCC Filing Rate by Grant Year (2014-2019)", fontsize=13, fontweight="bold")
ax.set_ylim(0, 55)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "ccc_rate_by_year.png", dpi=300, bbox_inches="tight")
plt.close()

# ── Plot 6: LA-level CCC rate choropleth (ranked bar chart) ────────────
print("Plot 6: LA-level CCC rates...")
fig, ax = plt.subplots(figsize=(10, 8))

la_data = br.groupby("la_clean").agg(
    n=("has_ccc", "count"), ccc=("has_ccc", "sum")
).reset_index()
la_data["rate"] = la_data["ccc"] / la_data["n"]
la_data = la_data[la_data["n"] >= 50].sort_values("rate", ascending=True)

colors_la = plt.cm.RdYlGn(la_data["rate"] / la_data["rate"].max())
ax.barh(range(len(la_data)), la_data["rate"] * 100,
        color=colors_la, edgecolor="white", linewidth=0.5)
ax.set_yticks(range(len(la_data)))
ax.set_yticklabels(la_data["la_clean"], fontsize=8)
ax.set_xlabel("CCC Filing Rate (%)", fontsize=12)
ax.set_title("CCC Filing Rate by Local Authority (2014-2019, n>=50)", fontsize=13, fontweight="bold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "la_ccc_rates.png", dpi=300, bbox_inches="tight")
plt.close()

# ── Plot 7: Sensitivity / permissions needed ────────────────────────────
print("Plot 7: Permissions needed scenarios...")
fig, ax = plt.subplots(figsize=(8, 5))

scenarios = ["Current yield\n(35.1%)", "Non-opt-out\nyield (51.4%)", "If lapse\nhalved (36.8%)",
             "If CCC +10pp\n(43.7%)", "Upper lapse\n(28.2%)"]
perms = [143734, 98249, 137195, 115548, 179149]
colors_sc = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336"]

bars = ax.bar(scenarios, [p/1000 for p in perms], color=colors_sc, width=0.6, edgecolor="white", linewidth=1.5)
ax.axhline(y=38, color="red", linewidth=2, linestyle="--", label="Current ~38k perms/yr")
ax.axhline(y=50.5, color="green", linewidth=2, linestyle=":", label="HFA target: 50.5k comps/yr")

for bar, p in zip(bars, perms):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f"{p/1000:.0f}k", ha="center", fontsize=10, fontweight="bold")

ax.set_ylabel("Permissions Needed per Year (thousands)", fontsize=12)
ax.set_title("Permissions Needed for 50,500 Completions/Year", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.set_ylim(0, 200)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(PLOTS / "permissions_needed.png", dpi=300, bbox_inches="tight")
plt.close()

print(f"\nAll plots saved to {PLOTS}/")
print("Done.")
