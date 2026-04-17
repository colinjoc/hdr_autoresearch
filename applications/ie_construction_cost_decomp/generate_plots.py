"""
Generate all plots for the construction cost decomposition paper.
Reads from cached data (WPM28, EHQ03) and results.tsv.
Produces PNGs at 300 DPI to plots/ directory.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from parse_data import parse_wpm28, parse_ehq03

PROJECT = Path(__file__).parent
PLOTS = PROJECT / "plots"
PLOTS.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
COLORS = plt.cm.tab10.colors

def save(fig, name):
    fig.savefig(PLOTS / name, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}")


def plot_material_trajectories():
    """Plot 1: Key material price trajectories (headline finding)."""
    wpm = parse_wpm28()

    key_materials = {
        "-": "All Materials",
        "65162": "Structural Steel (Fabricated)",
        "611": "Cement",
        "66161": "Rough Timber (Softwood)",
        "702": "Insulation",
        "691": "Electrical Fittings",
        "701": "HVAC",
        "706": "Glass",
    }

    fig, ax = plt.subplots(figsize=(12, 7))
    for i, (code, label) in enumerate(key_materials.items()):
        sub = wpm[wpm["material_code"] == code].sort_values("date")
        style = "-" if code == "-" else "--"
        lw = 2.5 if code == "-" else 1.5
        ax.plot(sub["date"], sub["index_value"], style, label=label, linewidth=lw, color=COLORS[i])

    # Mark events
    ax.axvline(pd.Timestamp("2020-03-01"), color="gray", linestyle=":", alpha=0.7, label="COVID-19")
    ax.axvline(pd.Timestamp("2022-02-01"), color="red", linestyle=":", alpha=0.7, label="Ukraine Invasion")
    ax.axvline(pd.Timestamp("2019-11-01"), color="green", linestyle=":", alpha=0.5, label="NZEB (Part L)")

    ax.set_xlabel("Date")
    ax.set_ylabel("Price Index (2015 = 100)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.set_ylim(80, 220)
    save(fig, "headline_material_trajectories.png")


def plot_cagr_ranking():
    """Plot 2: Horizontal bar chart of CAGR by material (feature importance equivalent)."""
    wpm = parse_wpm28()

    cagrs = {}
    labels = {}
    for mc in wpm["material_code"].unique():
        if mc == "-":
            continue
        sub = wpm[wpm["material_code"] == mc].sort_values("date")
        vals = sub["index_value"].dropna()
        if len(vals) < 2:
            continue
        years = (sub["date"].iloc[-1] - sub["date"].iloc[0]).days / 365.25
        g = ((vals.iloc[-1] / vals.iloc[0]) ** (1 / years) - 1) * 100
        cagrs[mc] = g
        labels[mc] = sub["material_label"].iloc[0]

    # Sort and take top 15
    sorted_cagrs = sorted(cagrs.items(), key=lambda x: x[1], reverse=True)
    top15 = sorted_cagrs[:15]

    fig, ax = plt.subplots(figsize=(10, 8))
    y_pos = np.arange(len(top15))
    bars = ax.barh(y_pos, [v for _, v in top15], color=[COLORS[0] if v > 5 else COLORS[1] if v > 3 else COLORS[2] for _, v in top15])
    ax.set_yticks(y_pos)
    ax.set_yticklabels([labels[k][:35] for k, _ in top15], fontsize=9)
    ax.set_xlabel("CAGR 2015-2024 (%/yr)")
    ax.invert_yaxis()

    # Add value labels
    for bar, (_, v) in zip(bars, top15):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{v:.1f}%", va="center", fontsize=8)

    save(fig, "feature_importance_cagr_ranking.png")


def plot_materials_vs_labour():
    """Plot 3: Materials vs labour cost trajectory (pred vs actual equivalent)."""
    wpm = parse_wpm28()
    ehq = parse_ehq03()

    # All-materials monthly
    all_mat = wpm[wpm["material_code"] == "-"][["date", "index_value"]].sort_values("date")

    # Labour cost quarterly - normalize to 2015 Q1 = 100
    ehq_2015 = ehq[ehq["year"] >= 2015].copy()
    if "EHQ03C08" in ehq_2015.columns:
        labour = ehq_2015[["date", "EHQ03C08"]].dropna()
        if len(labour) > 0:
            base = labour["EHQ03C08"].iloc[0]
            labour["labour_index"] = labour["EHQ03C08"] / base * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(all_mat["date"], all_mat["index_value"], "-", label="Materials (WPM28 All-Materials)",
            color=COLORS[0], linewidth=2)
    ax.plot(labour["date"], labour["labour_index"], "s-", label="Labour (EHQ03 Hourly Total Cost, indexed)",
            color=COLORS[1], linewidth=2, markersize=4)

    # 1:1 reference concept: equal growth line
    ax.axvline(pd.Timestamp("2020-03-01"), color="gray", linestyle=":", alpha=0.5, label="COVID-19")
    ax.axvline(pd.Timestamp("2022-02-01"), color="red", linestyle=":", alpha=0.5, label="Ukraine")

    ax.set_xlabel("Date")
    ax.set_ylabel("Index (2015 = 100)")
    ax.legend()
    save(fig, "pred_vs_actual_materials_labour.png")


def plot_covid_ukraine_impact():
    """Plot 4: COVID and Ukraine impact by material (grouped bar)."""
    wpm = parse_wpm28()

    key_materials = {
        "-": "All Materials",
        "65": "Steel (all)",
        "611": "Cement",
        "661": "Timber (rough)",
        "702": "Insulation",
        "691": "Electrical",
        "701": "HVAC",
        "700": "Plumbing",
        "706": "Glass",
    }

    def get_impact(mc, start, end, pre):
        sub = wpm[wpm["material_code"] == mc][["date", "index_value"]].set_index("date")["index_value"]
        pre_val = sub[sub.index <= pre]
        peak = sub[(sub.index >= start) & (sub.index <= end)]
        if len(pre_val) > 0 and len(peak) > 0:
            return (peak.max() / pre_val.iloc[-1] - 1) * 100
        return 0

    covid_impacts = []
    ukraine_impacts = []
    mat_labels = []
    for mc, label in key_materials.items():
        ci = get_impact(mc, pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"), pd.Timestamp("2020-01-01"))
        ui = get_impact(mc, pd.Timestamp("2022-02-01"), pd.Timestamp("2023-06-01"), pd.Timestamp("2022-01-01"))
        covid_impacts.append(ci)
        ukraine_impacts.append(ui)
        mat_labels.append(label)

    x = np.arange(len(mat_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, covid_impacts, width, label="COVID (2020-2021)", color=COLORS[0])
    ax.bar(x + width/2, ukraine_impacts, width, label="Ukraine (2022-2023)", color=COLORS[3])
    ax.set_xticks(x)
    ax.set_xticklabels(mat_labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Peak Impact (%)")
    ax.legend()
    save(fig, "covid_ukraine_impact.png")


def plot_regulatory_excess():
    """Plot 5: Pre vs post NZEB inflation rates (regulatory cost burden)."""
    wpm = parse_wpm28()
    nzeb_date = pd.Timestamp("2019-11-01")

    reg_materials = {"702": "Insulation", "706": "Glass", "701": "HVAC", "691": "Electrical"}

    pre_rates = []
    post_rates = []
    mat_labels = []

    for mc, label in reg_materials.items():
        sub = wpm[wpm["material_code"] == mc][["date", "index_value"]].set_index("date")["index_value"].sort_index()
        pre = sub[sub.index < nzeb_date]
        post = sub[sub.index >= nzeb_date]
        if len(pre) >= 6 and len(post) >= 6:
            pre_trend = (pre.iloc[-1] / pre.iloc[0] - 1) / (len(pre) / 12) * 100
            post_trend = (post.iloc[-1] / post.iloc[0] - 1) / (len(post) / 12) * 100
            pre_rates.append(pre_trend)
            post_rates.append(post_trend)
            mat_labels.append(label)

    x = np.arange(len(mat_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, pre_rates, width, label="Pre-NZEB (2015-2019)", color=COLORS[2])
    ax.bar(x + width/2, post_rates, width, label="Post-NZEB (2019-2024)", color=COLORS[3])
    ax.set_xticks(x)
    ax.set_xticklabels(mat_labels)
    ax.set_ylabel("Annual Inflation Rate (%/yr)")
    ax.legend()
    ax.axhline(y=0, color="black", linewidth=0.5)
    save(fig, "regulatory_excess_inflation.png")


def plot_weighted_contribution():
    """Plot 6: Waterfall-style weighted contribution chart."""
    contributions = {
        "Frame/Floors\n(steel+concrete)": 0.565,
        "Mechanical\n(plumbing+HVAC)": 0.436,
        "Substructure\n(concrete+rebar)": 0.416,
        "Ext. Walls\n(blocks+insul.)": 0.404,
        "Roof\n(timber+insul.)": 0.299,
        "Electrical": 0.272,
        "Windows\n(glass+doors)": 0.096,
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    sorted_items = sorted(contributions.items(), key=lambda x: -x[1])
    y_pos = np.arange(len(sorted_items))
    values = [v for _, v in sorted_items]
    labels = [k for k, _ in sorted_items]

    colors = [COLORS[0] if v > 0.4 else COLORS[1] if v > 0.2 else COLORS[2] for v in values]
    bars = ax.barh(y_pos, values, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Weighted Contribution to Annual Cost Growth (pp)")
    ax.invert_yaxis()

    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f"{v:.2f}pp", va="center", fontsize=9)

    save(fig, "weighted_contribution.png")


def plot_pca_variance():
    """Plot 7: PCA cumulative variance explained."""
    wpm = parse_wpm28()
    all_mat_codes = [c for c in wpm["material_code"].unique() if c != "-"]
    pivot = wpm[wpm["material_code"].isin(all_mat_codes)].pivot_table(
        index="date", columns="material_code", values="index_value"
    ).dropna(axis=1, how="all").dropna(axis=0)

    scaler = StandardScaler()
    X = scaler.fit_transform(pivot)
    pca = PCA()
    pca.fit(X)

    fig, ax = plt.subplots(figsize=(8, 5))
    n = min(15, len(pca.explained_variance_ratio_))
    cum_var = np.cumsum(pca.explained_variance_ratio_[:n])
    ax.bar(range(1, n+1), pca.explained_variance_ratio_[:n] * 100, alpha=0.7, label="Individual", color=COLORS[0])
    ax.plot(range(1, n+1), cum_var * 100, "ro-", label="Cumulative", markersize=5)
    ax.axhline(y=90, color="gray", linestyle="--", alpha=0.5, label="90% threshold")
    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Variance Explained (%)")
    ax.legend()
    ax.set_xticks(range(1, n+1))
    save(fig, "pca_variance_explained.png")


if __name__ == "__main__":
    print("Generating plots...")
    plot_material_trajectories()
    plot_cagr_ranking()
    plot_materials_vs_labour()
    plot_covid_ukraine_impact()
    plot_regulatory_excess()
    plot_weighted_contribution()
    plot_pca_variance()
    print("Done.")
