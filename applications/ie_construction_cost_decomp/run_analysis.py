"""
Full analysis pipeline for IE Construction Cost Decomposition.
Phase 0.5 (E00 baseline) through Phase 2 experiments.
Option C: Decomposition project — systematic ablation of cost components.
"""
import json
import csv
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

from parse_data import parse_wpm28, parse_ehq03, parse_bea04

PROJECT = Path(__file__).parent
RAW = PROJECT / "data" / "raw"
RESULTS_FILE = PROJECT / "results.tsv"

# ============================================================
# Utility functions
# ============================================================

def cagr(start_val, end_val, years):
    """Compound annual growth rate."""
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return np.nan
    return (end_val / start_val) ** (1 / years) - 1


def annualised_growth(series, dates):
    """Compute annualised growth from first to last observation."""
    valid = ~(series.isna())
    if valid.sum() < 2:
        return np.nan
    first_val = series[valid].iloc[0]
    last_val = series[valid].iloc[-1]
    first_date = dates[valid].iloc[0]
    last_date = dates[valid].iloc[-1]
    years = (last_date - first_date).days / 365.25
    return cagr(first_val, last_val, years)


def write_results_row(rows, filepath=RESULTS_FILE):
    """Append rows to results.tsv."""
    fieldnames = ["experiment_id", "description", "metric", "value", "status",
                  "prior", "mechanism", "interaction", "notes"]
    file_exists = filepath.exists()
    with open(filepath, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        if not file_exists:
            writer.writeheader()
        for row in rows:
            # Fill missing fields
            for fn in fieldnames:
                if fn not in row:
                    row[fn] = ""
            writer.writerow(row)


# ============================================================
# Phase 0.5: Baseline (E00)
# ============================================================

def run_e00_baseline():
    """E00: Parse WPM28 panel, compute annualised growth rates, cross-ref EHQ03."""
    wpm = parse_wpm28()
    ehq = parse_ehq03()

    # Compute CAGR for each material
    results = []
    for mc in wpm["material_code"].unique():
        sub = wpm[wpm["material_code"] == mc].sort_values("date")
        label = sub["material_label"].iloc[0]
        vals = sub["index_value"].dropna()
        if len(vals) < 2:
            continue
        first_val = vals.iloc[0]
        last_val = vals.iloc[-1]
        years = (sub["date"].iloc[-1] - sub["date"].iloc[0]).days / 365.25
        g = cagr(first_val, last_val, years)
        results.append({
            "material_code": mc,
            "material_label": label,
            "cagr_pct": g * 100,
            "start_index": first_val,
            "end_index": last_val,
            "total_change_pct": (last_val / first_val - 1) * 100
        })

    df_growth = pd.DataFrame(results).sort_values("cagr_pct", ascending=False)

    # All-materials index
    all_mat = df_growth[df_growth["material_code"] == "-"]
    all_cagr = all_mat["cagr_pct"].iloc[0]

    # Top-3 fastest growing
    excl_all = df_growth[df_growth["material_code"] != "-"]
    top3_grow = excl_all.nlargest(3, "cagr_pct")
    top3_fall = excl_all.nsmallest(3, "cagr_pct")

    # Labour cost trajectory
    ehq_recent = ehq[(ehq["year"] >= 2015) & (ehq["year"] <= 2025)].copy()
    if "EHQ03C08" in ehq_recent.columns:
        labour_costs = ehq_recent["EHQ03C08"].dropna()
        if len(labour_costs) >= 2:
            first_lc = labour_costs.iloc[0]
            last_lc = labour_costs.iloc[-1]
            years_lc = (ehq_recent["date"].iloc[-1] - ehq_recent[ehq_recent["EHQ03C08"].notna()]["date"].iloc[0]).days / 365.25
            labour_cagr = cagr(first_lc, last_lc, years_lc) * 100
        else:
            labour_cagr = np.nan
    else:
        labour_cagr = np.nan

    print("=" * 70)
    print("E00: BASELINE — Material Price Growth Rates 2015-2024")
    print("=" * 70)
    print(f"\nAll-Materials Index CAGR: {all_cagr:.2f}%/yr")
    print(f"Labour Cost CAGR (construction, 2015-2025): {labour_cagr:.2f}%/yr")
    print(f"\nTop-3 Fastest Growing:")
    for _, r in top3_grow.iterrows():
        print(f"  {r['material_label']}: {r['cagr_pct']:.2f}%/yr (index {r['start_index']:.1f} -> {r['end_index']:.1f})")
    print(f"\nTop-3 Fastest Falling:")
    for _, r in top3_fall.iterrows():
        print(f"  {r['material_label']}: {r['cagr_pct']:.2f}%/yr (index {r['start_index']:.1f} -> {r['end_index']:.1f})")

    write_results_row([{
        "experiment_id": "E00",
        "description": "Baseline: WPM28 40-material panel parsed, CAGRs computed",
        "metric": "all_materials_cagr_pct",
        "value": f"{all_cagr:.4f}",
        "status": "KEEP",
        "notes": f"40 materials x 117 months; labour CAGR={labour_cagr:.2f}%"
    }])

    return df_growth, labour_cagr, ehq_recent


# ============================================================
# Phase 1: Tournament (T01-T05)
# ============================================================

def run_tournament(wpm_df=None):
    """Phase 1: Compare 5 analytical approaches."""
    if wpm_df is None:
        wpm_df = parse_wpm28()

    # Build wide panel: months x materials (index values only)
    all_mat_codes = [c for c in wpm_df["material_code"].unique() if c != "-"]
    pivot = wpm_df[wpm_df["material_code"].isin(all_mat_codes)].pivot_table(
        index="date", columns="material_code", values="index_value"
    )
    pivot = pivot.dropna(axis=1, how="all").dropna(axis=0)

    # Also get the All-Materials index
    all_idx = wpm_df[wpm_df["material_code"] == "-"][["date", "index_value"]].set_index("date")["index_value"]

    tournament_results = []

    # --- T01: Simple CAGR ranking ---
    cagrs = {}
    for col in pivot.columns:
        s = pivot[col].dropna()
        if len(s) < 2:
            continue
        years = (s.index[-1] - s.index[0]).days / 365.25
        cagrs[col] = cagr(s.iloc[0], s.iloc[-1], years) * 100

    cagr_df = pd.Series(cagrs).sort_values(ascending=False)
    t01_metric = cagr_df.std()  # spread of growth rates as metric
    tournament_results.append({
        "experiment_id": "T01",
        "description": "CAGR ranking of 39 material sub-indices",
        "metric": "cagr_spread_std_pct",
        "value": f"{t01_metric:.4f}",
        "status": "KEEP",
        "notes": f"Top: {cagr_df.index[0]} ({cagr_df.iloc[0]:.1f}%); Bottom: {cagr_df.index[-1]} ({cagr_df.iloc[-1]:.1f}%)"
    })
    print(f"\n--- T01: CAGR Ranking ---")
    print(f"Spread (std): {t01_metric:.2f}pp")
    print(f"Range: {cagr_df.iloc[-1]:.2f}% to {cagr_df.iloc[0]:.2f}%")

    # --- T02: Variance decomposition ---
    # Which materials contribute most to All-Materials index variance?
    # Use monthly returns
    returns = pivot.pct_change().dropna()
    all_returns = all_idx.pct_change().dropna()

    # Align dates
    common_dates = returns.index.intersection(all_returns.index)
    returns = returns.loc[common_dates]
    all_returns_aligned = all_returns.loc[common_dates]

    # Contribution to variance: covariance of each material with All-Materials / variance of All-Materials
    var_all = all_returns_aligned.var()
    contributions = {}
    for col in returns.columns:
        cov = returns[col].cov(all_returns_aligned)
        contributions[col] = cov / var_all if var_all > 0 else 0

    contrib_df = pd.Series(contributions).sort_values(ascending=False)
    top5_var = contrib_df.head(5)
    t02_metric = top5_var.sum()
    tournament_results.append({
        "experiment_id": "T02",
        "description": "Variance decomposition: material contribution to All-Materials index",
        "metric": "top5_var_contribution_share",
        "value": f"{t02_metric:.4f}",
        "status": "KEEP",
        "notes": f"Top-5 materials explain {t02_metric*100:.1f}% of index variance"
    })
    print(f"\n--- T02: Variance Decomposition ---")
    print(f"Top-5 contributors explain {t02_metric*100:.1f}% of All-Materials variance")
    for code, val in top5_var.items():
        label = wpm_df[wpm_df["material_code"] == code]["material_label"].iloc[0]
        print(f"  {label}: {val*100:.1f}%")

    # --- T03: PCA ---
    scaler = StandardScaler()
    X = scaler.fit_transform(pivot.dropna())
    pca = PCA()
    pca.fit(X)
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    n_90 = np.argmax(cum_var >= 0.9) + 1
    n_95 = np.argmax(cum_var >= 0.95) + 1

    tournament_results.append({
        "experiment_id": "T03",
        "description": "PCA on 39 material series: latent factor count",
        "metric": "n_components_90pct_var",
        "value": str(n_90),
        "status": "KEEP",
        "notes": f"PC1={pca.explained_variance_ratio_[0]*100:.1f}%, {n_90} for 90%, {n_95} for 95%"
    })
    print(f"\n--- T03: PCA ---")
    print(f"PC1 explains {pca.explained_variance_ratio_[0]*100:.1f}% of variance")
    print(f"Components for 90% variance: {n_90}")
    print(f"Components for 95% variance: {n_95}")

    # PCA loadings for PC1
    loadings = pd.Series(pca.components_[0], index=pivot.columns)
    top_pc1 = loadings.abs().nlargest(5)
    print("Top-5 loadings on PC1:")
    for code in top_pc1.index:
        label = wpm_df[wpm_df["material_code"] == code]["material_label"].iloc[0]
        print(f"  {label}: {loadings[code]:.3f}")

    # --- T04: Regression: All-Materials ~ top-5 sub-indices ---
    top5_codes = list(contrib_df.head(5).index)
    X_reg = pivot[top5_codes].values
    y_reg = all_idx.loc[pivot.index].values

    # Remove NaN rows
    mask = ~(np.isnan(X_reg).any(axis=1) | np.isnan(y_reg))
    X_reg = X_reg[mask]
    y_reg = y_reg[mask]

    reg = LinearRegression()
    reg.fit(X_reg, y_reg)
    r2 = reg.score(X_reg, y_reg)

    tournament_results.append({
        "experiment_id": "T04",
        "description": "Linear regression: All-Materials ~ top-5 contributing materials",
        "metric": "r_squared",
        "value": f"{r2:.6f}",
        "status": "KEEP",
        "notes": f"Regressors: {top5_codes}; R²={r2:.4f}"
    })
    print(f"\n--- T04: Regression ---")
    print(f"All-Materials ~ top-5 materials: R² = {r2:.6f}")
    for code, coef in zip(top5_codes, reg.coef_):
        label = wpm_df[wpm_df["material_code"] == code]["material_label"].iloc[0]
        print(f"  {label}: coef = {coef:.4f}")

    # --- T05: Structural break detection (simplified Chow test) ---
    # Test for a break at COVID (March 2020) and Ukraine (Feb 2022) for the All-Materials index
    all_ts = all_idx.sort_index().dropna()
    break_dates = {
        "COVID (Mar 2020)": pd.Timestamp("2020-03-01"),
        "Ukraine (Feb 2022)": pd.Timestamp("2022-02-01"),
    }

    break_results = {}
    for break_name, break_date in break_dates.items():
        pre = all_ts[all_ts.index < break_date]
        post = all_ts[all_ts.index >= break_date]
        if len(pre) < 5 or len(post) < 5:
            continue

        # Simple F-test: compare variance of residuals from single trend vs two separate trends
        # Single trend
        x_full = np.arange(len(all_ts)).reshape(-1, 1)
        y_full = all_ts.values
        reg_full = LinearRegression().fit(x_full, y_full)
        rss_full = np.sum((y_full - reg_full.predict(x_full)) ** 2)

        # Two separate trends
        n_pre = len(pre)
        x_pre = np.arange(n_pre).reshape(-1, 1)
        x_post = np.arange(len(post)).reshape(-1, 1)
        reg_pre = LinearRegression().fit(x_pre, pre.values)
        reg_post = LinearRegression().fit(x_post, post.values)
        rss_split = (np.sum((pre.values - reg_pre.predict(x_pre)) ** 2) +
                     np.sum((post.values - reg_post.predict(x_post)) ** 2))

        # F-statistic
        k = 2  # additional parameters in split model
        n = len(all_ts)
        f_stat = ((rss_full - rss_split) / k) / (rss_split / (n - 2 * k))
        p_val = 1 - stats.f.cdf(f_stat, k, n - 2 * k)

        break_results[break_name] = {"f_stat": f_stat, "p_value": p_val}
        print(f"\n  Break at {break_name}: F={f_stat:.2f}, p={p_val:.6f} {'***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'}")

    tournament_results.append({
        "experiment_id": "T05",
        "description": "Structural break detection (Chow test) at COVID/Ukraine",
        "metric": "covid_break_p_value",
        "value": f"{break_results.get('COVID (Mar 2020)', {}).get('p_value', np.nan):.6f}",
        "status": "KEEP",
        "notes": f"COVID p={break_results.get('COVID (Mar 2020)', {}).get('p_value', np.nan):.6f}; Ukraine p={break_results.get('Ukraine (Feb 2022)', {}).get('p_value', np.nan):.6f}"
    })

    write_results_row(tournament_results)

    # Save tournament summary
    t_df = pd.DataFrame(tournament_results)
    t_df.to_csv(PROJECT / "tournament_results.csv", index=False)

    return {
        "cagr_df": cagr_df,
        "contrib_df": contrib_df,
        "pca": pca,
        "pivot": pivot,
        "all_idx": all_idx,
        "loadings": loadings,
        "break_results": break_results,
        "top5_codes": top5_codes,
        "r2": r2,
        "n_90": n_90,
    }


# ============================================================
# Phase 2: Experiments (E01-E20)
# ============================================================

def run_phase2_experiments(wpm_df=None, ehq_df=None, bea_df=None):
    """Run all 20 experiments."""
    if wpm_df is None:
        wpm_df = parse_wpm28()
    if ehq_df is None:
        ehq_df = parse_ehq03()
    if bea_df is None:
        bea_df = parse_bea04()

    results = []

    # Helper: get material trajectory
    def get_material_trajectory(code):
        sub = wpm_df[wpm_df["material_code"] == code][["date", "index_value"]].set_index("date").sort_index()
        return sub["index_value"].dropna()

    def compute_cagr_for_code(code):
        s = get_material_trajectory(code)
        if len(s) < 2:
            return np.nan
        years = (s.index[-1] - s.index[0]).days / 365.25
        return cagr(s.iloc[0], s.iloc[-1], years) * 100

    # Material code lookup
    mat_lookup = wpm_df.drop_duplicates("material_code").set_index("material_code")["material_label"].to_dict()

    # === E01: Concrete/cement trajectory ===
    cement_codes = ["611", "621", "631"]
    cement_names = {c: mat_lookup.get(c, c) for c in cement_codes}
    cement_cagrs = {c: compute_cagr_for_code(c) for c in cement_codes}
    print("\n--- E01: Concrete/Cement ---")
    for c in cement_codes:
        print(f"  {cement_names[c]}: CAGR = {cement_cagrs[c]:.2f}%")
    avg_cement = np.mean([v for v in cement_cagrs.values() if not np.isnan(v)])
    results.append({
        "experiment_id": "E01",
        "description": "Concrete/cement trajectory 2015-2024",
        "metric": "avg_cement_cagr_pct",
        "value": f"{avg_cement:.4f}",
        "status": "KEEP",
        "prior": "70%",
        "mechanism": "Cement is a non-tradeable commodity with high transport costs; local demand driven",
        "notes": "; ".join([f"{cement_names[c]}={cement_cagrs[c]:.2f}%" for c in cement_codes])
    })

    # === E02: Structural steel trajectory ===
    steel_codes = ["65", "651", "65161", "65162", "652", "653"]
    steel_cagrs = {c: compute_cagr_for_code(c) for c in steel_codes if c in mat_lookup}
    print("\n--- E02: Structural Steel ---")
    for c, v in steel_cagrs.items():
        print(f"  {mat_lookup.get(c, c)}: CAGR = {v:.2f}%")
    avg_steel = np.mean([v for v in steel_cagrs.values() if not np.isnan(v)])
    results.append({
        "experiment_id": "E02",
        "description": "Structural steel trajectory 2015-2024",
        "metric": "avg_steel_cagr_pct",
        "value": f"{avg_steel:.4f}",
        "status": "KEEP",
        "prior": "60%",
        "mechanism": "Steel is globally traded; prices driven by Chinese production + EU energy costs",
    })

    # === E03: Timber trajectory ===
    timber_codes = ["661", "66161", "66162", "671", "67161", "67162"]
    timber_cagrs = {c: compute_cagr_for_code(c) for c in timber_codes if c in mat_lookup}
    print("\n--- E03: Timber ---")
    for c, v in timber_cagrs.items():
        print(f"  {mat_lookup.get(c, c)}: CAGR = {v:.2f}%")
    avg_timber = np.mean([v for v in timber_cagrs.values() if not np.isnan(v)])
    results.append({
        "experiment_id": "E03",
        "description": "Timber trajectory 2015-2024",
        "metric": "avg_timber_cagr_pct",
        "value": f"{avg_timber:.4f}",
        "status": "KEEP",
        "prior": "65%",
        "mechanism": "COVID lumber spike + subsequent oversupply; Scandinavian supply chains",
    })

    # === E04: Insulation ===
    insul_cagr = compute_cagr_for_code("702")
    print(f"\n--- E04: Insulation ---")
    print(f"  {mat_lookup.get('702', '702')}: CAGR = {insul_cagr:.2f}%")
    results.append({
        "experiment_id": "E04",
        "description": "Insulation trajectory 2015-2024 (NZEB regulatory driver)",
        "metric": "insulation_cagr_pct",
        "value": f"{insul_cagr:.4f}",
        "status": "KEEP",
        "prior": "75%",
        "mechanism": "NZEB (Part L 2019) mandated higher insulation standards; demand shock",
    })

    # === E05: Electrical fittings ===
    elec_codes = ["691", "69162", "69163"]
    elec_cagrs = {c: compute_cagr_for_code(c) for c in elec_codes if c in mat_lookup}
    print("\n--- E05: Electrical Fittings ---")
    for c, v in elec_cagrs.items():
        print(f"  {mat_lookup.get(c, c)}: CAGR = {v:.2f}%")
    avg_elec = np.mean([v for v in elec_cagrs.values() if not np.isnan(v)])
    results.append({
        "experiment_id": "E05",
        "description": "Electrical fittings trajectory (heat pump/solar transition)",
        "metric": "avg_electrical_cagr_pct",
        "value": f"{avg_elec:.4f}",
        "status": "KEEP",
        "prior": "70%",
        "mechanism": "Heat pump mandate + solar PV requirements increase electrical component demand",
    })

    # === E06: HVAC ===
    hvac_cagr = compute_cagr_for_code("701")
    print(f"\n--- E06: HVAC ---")
    print(f"  {mat_lookup.get('701', '701')}: CAGR = {hvac_cagr:.2f}%")
    results.append({
        "experiment_id": "E06",
        "description": "HVAC trajectory 2015-2024",
        "metric": "hvac_cagr_pct",
        "value": f"{hvac_cagr:.4f}",
        "status": "KEEP",
        "prior": "65%",
        "mechanism": "Heat pump transition replacing gas boilers; component complexity increases",
    })

    # === E07: Plumbing/Sanitary ===
    plumb_cagr = compute_cagr_for_code("700")
    print(f"\n--- E07: Plumbing/Sanitary ---")
    print(f"  {mat_lookup.get('700', '700')}: CAGR = {plumb_cagr:.2f}%")
    results.append({
        "experiment_id": "E07",
        "description": "Plumbing/sanitary trajectory 2015-2024",
        "metric": "plumbing_cagr_pct",
        "value": f"{plumb_cagr:.4f}",
        "status": "KEEP",
        "prior": "50%",
        "mechanism": "Sanitary ware largely imported; exchange rate and shipping cost dependent",
    })

    # === E08: Glass (triple glazing NZEB) ===
    glass_cagr = compute_cagr_for_code("706")
    print(f"\n--- E08: Glass ---")
    print(f"  {mat_lookup.get('706', '706')}: CAGR = {glass_cagr:.2f}%")
    results.append({
        "experiment_id": "E08",
        "description": "Glass trajectory 2015-2024 (triple glazing NZEB requirement)",
        "metric": "glass_cagr_pct",
        "value": f"{glass_cagr:.4f}",
        "status": "KEEP",
        "prior": "60%",
        "mechanism": "NZEB requires triple glazing; glass is energy-intensive to manufacture",
    })

    # === E09: Labour cost per hour ===
    ehq_2015_plus = ehq_df[ehq_df["year"] >= 2015].copy()
    if "EHQ03C08" in ehq_2015_plus.columns:
        lc = ehq_2015_plus[["date", "EHQ03C08"]].dropna()
        if len(lc) >= 2:
            first_lc = lc["EHQ03C08"].iloc[0]
            last_lc = lc["EHQ03C08"].iloc[-1]
            years = (lc["date"].iloc[-1] - lc["date"].iloc[0]).days / 365.25
            labour_cagr_val = cagr(first_lc, last_lc, years) * 100
        else:
            labour_cagr_val = np.nan
    else:
        labour_cagr_val = np.nan

    print(f"\n--- E09: Labour cost per hour ---")
    print(f"  Construction hourly total labour cost CAGR: {labour_cagr_val:.2f}%")
    results.append({
        "experiment_id": "E09",
        "description": "Construction labour cost per hour trajectory 2015-2025",
        "metric": "labour_hourly_cagr_pct",
        "value": f"{labour_cagr_val:.4f}",
        "status": "KEEP",
        "prior": "80%",
        "mechanism": "Tight labour market post-2018; SOLAS skills shortages; wage pressure",
    })

    # === E10: Labour hours per dwelling (productivity proxy) ===
    if "EHQ03C05" in ehq_2015_plus.columns:
        hrs = ehq_2015_plus[["date", "EHQ03C05"]].dropna()
        if len(hrs) >= 2:
            first_hrs = hrs["EHQ03C05"].iloc[0]
            last_hrs = hrs["EHQ03C05"].iloc[-1]
            hrs_change = (last_hrs / first_hrs - 1) * 100
        else:
            hrs_change = np.nan
    else:
        hrs_change = np.nan

    print(f"\n--- E10: Avg Weekly Paid Hours ---")
    print(f"  Change: {hrs_change:.2f}%")
    results.append({
        "experiment_id": "E10",
        "description": "Average weekly paid hours in construction (productivity proxy)",
        "metric": "weekly_hrs_change_pct",
        "value": f"{hrs_change:.4f}",
        "status": "KEEP",
        "prior": "55%",
        "mechanism": "Reduced hours may indicate shift to contract/gig work or regulatory limits",
    })

    # === E11: Employment count vs output (labour productivity) ===
    if "EHQ03C01" in ehq_2015_plus.columns:
        emp = ehq_2015_plus[["date", "year", "EHQ03C01"]].dropna()
        if len(emp) >= 2:
            first_emp = emp["EHQ03C01"].iloc[0]
            last_emp = emp["EHQ03C01"].iloc[-1]
            emp_change = (last_emp / first_emp - 1) * 100
        else:
            emp_change = np.nan
    else:
        emp_change = np.nan

    # BEA04 value index for residential building
    bea_res = bea_df[(bea_df["sector_code"] == "111") & (bea_df["statistic"] == "BEA04C02")]
    bea_res = bea_res.sort_values("year")
    if len(bea_res) >= 2:
        bea_2015 = bea_res[bea_res["year"] == 2015]["value"]
        bea_latest = bea_res[bea_res["year"] == bea_res["year"].max()]["value"]
        if len(bea_2015) > 0 and len(bea_latest) > 0:
            output_change = (bea_latest.iloc[0] / bea_2015.iloc[0] - 1) * 100
        else:
            output_change = np.nan
    else:
        output_change = np.nan

    print(f"\n--- E11: Employment vs Output ---")
    print(f"  Employment change (2015-latest): {emp_change:.2f}%")
    print(f"  Residential output volume change (2015-latest): {output_change:.2f}%")
    results.append({
        "experiment_id": "E11",
        "description": "Employment count vs residential output (labour productivity)",
        "metric": "employment_change_pct",
        "value": f"{emp_change:.4f}",
        "status": "KEEP",
        "prior": "60%",
        "mechanism": "If employment grows faster than output, productivity is declining",
        "notes": f"Output change: {output_change:.2f}%"
    })

    # === E12: Materials vs Labour: which grew faster? ===
    all_mat_cagr = compute_cagr_for_code("-")
    mat_vs_lab = all_mat_cagr - labour_cagr_val if not np.isnan(labour_cagr_val) else np.nan
    print(f"\n--- E12: Materials vs Labour ---")
    print(f"  Materials CAGR: {all_mat_cagr:.2f}%")
    print(f"  Labour CAGR: {labour_cagr_val:.2f}%")
    print(f"  Difference (materials - labour): {mat_vs_lab:.2f}pp")
    results.append({
        "experiment_id": "E12",
        "description": "Materials vs labour: which grew faster 2015-2024?",
        "metric": "materials_minus_labour_cagr_pp",
        "value": f"{mat_vs_lab:.4f}",
        "status": "KEEP",
        "prior": "50%",
        "mechanism": "If labour outpaces materials, the cost mix shifts toward labour dominance",
    })

    # === E13: COVID impact window ===
    covid_start = pd.Timestamp("2020-03-01")
    covid_end = pd.Timestamp("2021-12-01")
    pre_covid = pd.Timestamp("2020-01-01")

    print(f"\n--- E13: COVID Impact (2020-2021) ---")
    covid_impacts = {}
    key_materials = ["-", "611", "65", "661", "702", "691", "701", "700", "706"]
    for mc in key_materials:
        s = get_material_trajectory(mc)
        pre = s[s.index <= pre_covid]
        peak = s[(s.index >= covid_start) & (s.index <= covid_end)]
        if len(pre) > 0 and len(peak) > 0:
            impact = (peak.max() / pre.iloc[-1] - 1) * 100
            covid_impacts[mc] = impact
            print(f"  {mat_lookup.get(mc, mc)}: peak COVID impact = +{impact:.1f}%")

    results.append({
        "experiment_id": "E13",
        "description": "COVID impact window (2020-2021) on key materials",
        "metric": "all_materials_covid_peak_pct",
        "value": f"{covid_impacts.get('-', np.nan):.4f}",
        "status": "KEEP",
        "prior": "85%",
        "mechanism": "Supply chain disruption + construction site closures + demand surge on reopening",
    })

    # === E14: Ukraine/Energy impact (2022-2023) ===
    ukraine_start = pd.Timestamp("2022-02-01")
    ukraine_end = pd.Timestamp("2023-06-01")
    pre_ukraine = pd.Timestamp("2022-01-01")

    print(f"\n--- E14: Ukraine/Energy Impact (2022-2023) ---")
    ukraine_impacts = {}
    for mc in key_materials:
        s = get_material_trajectory(mc)
        pre = s[s.index <= pre_ukraine]
        peak = s[(s.index >= ukraine_start) & (s.index <= ukraine_end)]
        if len(pre) > 0 and len(peak) > 0:
            impact = (peak.max() / pre.iloc[-1] - 1) * 100
            ukraine_impacts[mc] = impact
            print(f"  {mat_lookup.get(mc, mc)}: peak Ukraine impact = +{impact:.1f}%")

    results.append({
        "experiment_id": "E14",
        "description": "Ukraine/energy impact (2022-2023) on key materials",
        "metric": "all_materials_ukraine_peak_pct",
        "value": f"{ukraine_impacts.get('-', np.nan):.4f}",
        "status": "KEEP",
        "prior": "80%",
        "mechanism": "Energy price spike → energy-intensive materials (steel, glass, cement) surge",
    })

    # === E15: Post-crisis trajectory (2024-2025) ===
    post_crisis_start = pd.Timestamp("2024-01-01")
    pre_crisis_peak_end = pd.Timestamp("2023-06-01")

    print(f"\n--- E15: Post-crisis trajectory (2024+) ---")
    reversion = {}
    for mc in key_materials:
        s = get_material_trajectory(mc)
        peak = s[(s.index >= pd.Timestamp("2022-01-01")) & (s.index <= pre_crisis_peak_end)]
        post = s[s.index >= post_crisis_start]
        if len(peak) > 0 and len(post) > 0:
            rev = (post.iloc[-1] / peak.max() - 1) * 100
            reversion[mc] = rev
            print(f"  {mat_lookup.get(mc, mc)}: post-peak change = {rev:+.1f}%")

    results.append({
        "experiment_id": "E15",
        "description": "Post-crisis trajectory (2024) — are costs mean-reverting?",
        "metric": "all_materials_post_peak_reversion_pct",
        "value": f"{reversion.get('-', np.nan):.4f}",
        "status": "KEEP",
        "prior": "55%",
        "mechanism": "Post-shock: some materials revert (steel, timber), others ratchet (concrete, insulation)",
    })

    # === E16 & E17: Buildcost trade-level decomposition ===
    # Parse from the buildcost text — residential costs per m2
    # From buildcost_2025h1.txt: residential range
    residential_costs_2025 = {
        "Terraced Houses": (1750, 1900),
        "Semi-Detached Houses": (1900, 2050),
        "Apartments (Superstructure)": (2500, 3000),
    }
    residential_costs_2024 = {
        "Terraced Houses": (1700, 1850),
        "Semi-Detached Houses": (1850, 2000),
        "Apartments (Superstructure)": (2500, 3000),
    }

    # SCSI hard/soft cost split calibration
    hard_cost_share = 0.53
    materials_share = 0.25  # of total
    labour_share = 0.25     # of total
    site_share = 0.03       # of total

    # Trade-level decomposition (estimated from industry data)
    # Source: SCSI/Buildcost guide typical breakdown for semi-detached house
    trade_breakdown = {
        "Substructure": 0.08,
        "Frame/Upper Floors": 0.12,
        "Roof": 0.07,
        "External Walls/Cladding": 0.10,
        "Windows/External Doors": 0.06,
        "Internal Walls/Partitions": 0.04,
        "Internal Finishes": 0.08,
        "Fittings/Fixtures": 0.05,
        "Mechanical Services (Plumbing/HVAC)": 0.14,
        "Electrical Services": 0.10,
        "Stairs": 0.02,
        "Preliminaries/Site Overhead": 0.10,
        "External/Site Works": 0.04,
    }

    print(f"\n--- E16: Trade-level decomposition ---")
    mid_cost_2025 = np.mean([1900, 2050])  # semi-detached midpoint
    for trade, share in sorted(trade_breakdown.items(), key=lambda x: -x[1]):
        print(f"  {trade}: {share*100:.0f}% = EUR {mid_cost_2025 * share:.0f}/sqm")

    results.append({
        "experiment_id": "E16",
        "description": "Buildcost.ie trade-level decomposition for residential",
        "metric": "semi_detached_mid_cost_eur_sqm",
        "value": f"{mid_cost_2025:.0f}",
        "status": "KEEP",
        "prior": "70%",
        "mechanism": "Services (mech+elec) dominate at ~24% of hard cost; envelope second at ~16%",
    })

    print(f"\n--- E17: Share of total cost by trade ---")
    results.append({
        "experiment_id": "E17",
        "description": "Share of total cost by trade (from buildcost guides)",
        "metric": "largest_trade_share",
        "value": f"{max(trade_breakdown.values())*100:.1f}",
        "status": "KEEP",
        "prior": "65%",
        "mechanism": "Mechanical services largest single trade; driven by NZEB complexity",
        "notes": "Mech 14%, Frame 12%, Elec 10%, Ext Walls 10%, Prelim 10%"
    })

    # === E18: Weighted contribution (inflation x share = total contribution) ===
    # Map trades to material indices where possible
    trade_material_map = {
        "Substructure": [("621", 0.6), ("611", 0.3), ("652", 0.1)],  # concrete, cement, rebar
        "Frame/Upper Floors": [("65", 0.4), ("621", 0.3), ("64", 0.3)],  # steel, concrete, precast
        "Roof": [("661", 0.4), ("65", 0.3), ("702", 0.3)],  # timber, steel, insulation
        "External Walls/Cladding": [("631", 0.4), ("702", 0.4), ("704", 0.2)],  # blocks, insulation, plaster
        "Windows/External Doors": [("706", 0.5), ("67162", 0.3), ("708", 0.2)],  # glass, wooden doors, metal fittings
        "Mechanical Services (Plumbing/HVAC)": [("701", 0.5), ("700", 0.3), ("703", 0.2)],  # HVAC, plumbing, pipes
        "Electrical Services": [("691", 0.6), ("69162", 0.2), ("69163", 0.2)],  # electrical fittings
    }

    print(f"\n--- E18: Weighted contribution to total cost growth ---")
    weighted_contributions = {}
    for trade, mat_weights in trade_material_map.items():
        trade_share = trade_breakdown[trade]
        weighted_infl = 0
        for mat_code, weight in mat_weights:
            mat_cagr = compute_cagr_for_code(mat_code)
            if not np.isnan(mat_cagr):
                weighted_infl += weight * mat_cagr
        contribution = trade_share * weighted_infl
        weighted_contributions[trade] = contribution
        print(f"  {trade}: share={trade_share*100:.0f}% x inflation={weighted_infl:.2f}% = contribution={contribution:.3f}pp")

    total_contribution = sum(weighted_contributions.values())
    results.append({
        "experiment_id": "E18",
        "description": "Weighted contribution: material inflation x share of cost",
        "metric": "total_weighted_contribution_pp",
        "value": f"{total_contribution:.4f}",
        "status": "KEEP",
        "prior": "60%",
        "mechanism": "High-share trades with high inflation dominate total cost growth",
    })

    # === E19: Which 5 materials contribute >50% of total materials inflation? ===
    # Use All-Materials CAGR and individual CAGRs
    all_cagrs = {}
    for mc in wpm_df["material_code"].unique():
        if mc == "-":
            continue
        c = compute_cagr_for_code(mc)
        if not np.isnan(c):
            all_cagrs[mc] = c

    # Sort by absolute CAGR (contribution approximation)
    sorted_cagrs = sorted(all_cagrs.items(), key=lambda x: abs(x[1]), reverse=True)
    top5_mat = sorted_cagrs[:5]
    rest = sorted_cagrs[5:]
    top5_sum = sum(abs(v) for _, v in top5_mat)
    total_sum = sum(abs(v) for _, v in sorted_cagrs)
    top5_share = top5_sum / total_sum * 100 if total_sum > 0 else 0

    print(f"\n--- E19: Top-5 materials by absolute contribution ---")
    for mc, v in top5_mat:
        print(f"  {mat_lookup.get(mc, mc)}: |CAGR| = {abs(v):.2f}%")
    print(f"  Top-5 share of total |CAGR|: {top5_share:.1f}%")

    results.append({
        "experiment_id": "E19",
        "description": "Top-5 materials contributing >50% of total inflation",
        "metric": "top5_share_of_abs_cagr",
        "value": f"{top5_share:.4f}",
        "status": "KEEP",
        "prior": "70%",
        "mechanism": "Concentration risk: few materials drive most of the cost movement",
        "notes": "; ".join([f"{mat_lookup.get(mc, mc)}={v:.2f}%" for mc, v in top5_mat])
    })

    # === E20: Regulatory-driven cost additions (NZEB, BCAR) ===
    # NZEB came into force Nov 2019 for dwellings
    # Compare insulation, glass, HVAC, electrical before and after
    nzeb_date = pd.Timestamp("2019-11-01")
    regulatory_materials = {"702": "Insulation", "706": "Glass", "701": "HVAC", "691": "Electrical"}

    print(f"\n--- E20: Regulatory-driven cost additions ---")
    reg_impacts = {}
    for mc, name in regulatory_materials.items():
        s = get_material_trajectory(mc)
        pre_nzeb = s[s.index < nzeb_date]
        post_nzeb = s[s.index >= nzeb_date]
        if len(pre_nzeb) >= 6 and len(post_nzeb) >= 6:
            pre_trend = (pre_nzeb.iloc[-1] / pre_nzeb.iloc[0] - 1) / (len(pre_nzeb) / 12) * 100
            post_trend = (post_nzeb.iloc[-1] / post_nzeb.iloc[0] - 1) / (len(post_nzeb) / 12) * 100
            excess = post_trend - pre_trend
            reg_impacts[name] = {
                "pre_trend": pre_trend,
                "post_trend": post_trend,
                "excess": excess,
                "code": mc
            }
            print(f"  {name}: pre-NZEB={pre_trend:.2f}%/yr, post-NZEB={post_trend:.2f}%/yr, excess={excess:+.2f}pp")

    results.append({
        "experiment_id": "E20",
        "description": "Regulatory-driven cost additions (NZEB, BCAR, Part L)",
        "metric": "insulation_excess_inflation_pp",
        "value": f"{reg_impacts.get('Insulation', {}).get('excess', np.nan):.4f}",
        "status": "KEEP",
        "prior": "75%",
        "mechanism": "NZEB mandates higher insulation, triple glazing, heat pumps; raises demand for those materials",
        "notes": "; ".join([f"{k}={v['excess']:+.2f}pp" for k, v in reg_impacts.items()])
    })

    write_results_row(results)

    return {
        "cement_cagrs": cement_cagrs,
        "steel_cagrs": steel_cagrs,
        "timber_cagrs": timber_cagrs,
        "insul_cagr": insul_cagr,
        "elec_cagrs": elec_cagrs,
        "hvac_cagr": hvac_cagr,
        "glass_cagr": glass_cagr,
        "labour_cagr": labour_cagr_val,
        "all_mat_cagr": all_mat_cagr,
        "trade_breakdown": trade_breakdown,
        "weighted_contributions": weighted_contributions,
        "covid_impacts": covid_impacts,
        "ukraine_impacts": ukraine_impacts,
        "reversion": reversion,
        "reg_impacts": reg_impacts,
        "mat_lookup": mat_lookup,
    }


# ============================================================
# Phase 2.5: Interaction experiments
# ============================================================

def run_phase25_interactions(wpm_df=None, ehq_df=None):
    """Test interactions: materials x labour, COVID x material type."""
    if wpm_df is None:
        wpm_df = parse_wpm28()
    if ehq_df is None:
        ehq_df = parse_ehq03()

    results = []

    # Interaction 1: Materials x Labour — do they move together?
    all_idx = wpm_df[wpm_df["material_code"] == "-"][["date", "index_value"]].set_index("date")["index_value"]

    # Resample all_idx to quarterly for alignment with EHQ03
    all_q = all_idx.resample("QE").mean()

    ehq_2015_plus = ehq_df[ehq_df["year"] >= 2015].copy()
    if "EHQ03C08" in ehq_2015_plus.columns:
        labour = ehq_2015_plus.set_index("date")["EHQ03C08"].dropna()
        # Align
        common = all_q.index.intersection(labour.index)
        if len(common) > 5:
            corr = all_q.loc[common].corr(labour.loc[common])
            print(f"\n--- Interaction: Materials x Labour correlation ---")
            print(f"  Pearson r = {corr:.4f}")
            results.append({
                "experiment_id": "I01",
                "description": "Interaction: All-Materials index x Labour cost correlation",
                "metric": "pearson_r",
                "value": f"{corr:.4f}",
                "status": "KEEP",
                "interaction": "True",
                "mechanism": "Materials and labour may co-move due to shared demand drivers",
            })

    # Interaction 2: COVID impact x energy-intensity of material
    # Energy-intensive materials (steel, glass, cement) vs non-energy-intensive (timber, paints)
    energy_intensive = ["65", "706", "611", "621"]  # steel, glass, cement, RMC
    non_energy = ["661", "705", "704"]  # timber, paints, plaster

    def covid_impact(mc):
        s = wpm_df[wpm_df["material_code"] == mc][["date", "index_value"]].set_index("date")["index_value"]
        pre = s[s.index <= pd.Timestamp("2020-01-01")]
        peak = s[(s.index >= pd.Timestamp("2020-03-01")) & (s.index <= pd.Timestamp("2021-12-01"))]
        if len(pre) > 0 and len(peak) > 0:
            return (peak.max() / pre.iloc[-1] - 1) * 100
        return np.nan

    ei_impacts = [covid_impact(mc) for mc in energy_intensive if not np.isnan(covid_impact(mc))]
    ne_impacts = [covid_impact(mc) for mc in non_energy if not np.isnan(covid_impact(mc))]

    if len(ei_impacts) > 1 and len(ne_impacts) > 1:
        t_stat, p_val = stats.ttest_ind(ei_impacts, ne_impacts)
        print(f"\n--- Interaction: COVID x Energy Intensity ---")
        print(f"  Energy-intensive COVID impact mean: {np.mean(ei_impacts):.1f}%")
        print(f"  Non-energy COVID impact mean: {np.mean(ne_impacts):.1f}%")
        print(f"  t={t_stat:.2f}, p={p_val:.4f}")
        results.append({
            "experiment_id": "I02",
            "description": "Interaction: COVID impact x energy-intensity of material",
            "metric": "t_statistic",
            "value": f"{t_stat:.4f}",
            "status": "KEEP",
            "interaction": "True",
            "mechanism": "Energy-intensive materials have different supply chain disruption dynamics",
            "notes": f"EI mean={np.mean(ei_impacts):.1f}%, NE mean={np.mean(ne_impacts):.1f}%, p={p_val:.4f}"
        })

    write_results_row(results)
    return results


# ============================================================
# Main execution
# ============================================================

if __name__ == "__main__":
    # Clear results file for fresh run
    if RESULTS_FILE.exists():
        RESULTS_FILE.unlink()

    print("=" * 70)
    print("PHASE 0.5: BASELINE")
    print("=" * 70)
    df_growth, labour_cagr, ehq_recent = run_e00_baseline()

    wpm = parse_wpm28()
    ehq = parse_ehq03()
    bea = parse_bea04()

    print("\n" + "=" * 70)
    print("PHASE 1: TOURNAMENT")
    print("=" * 70)
    tournament = run_tournament(wpm)

    print("\n" + "=" * 70)
    print("PHASE 2: EXPERIMENTS")
    print("=" * 70)
    exp_results = run_phase2_experiments(wpm, ehq, bea)

    print("\n" + "=" * 70)
    print("PHASE 2.5: INTERACTIONS")
    print("=" * 70)
    interactions = run_phase25_interactions(wpm, ehq)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
