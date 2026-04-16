"""Phase 2.75 mandated experiments M1-M5.

Runs the four experiments mandated by the blind reviewer (plus M5 stretch goal)
and writes results rows to results.tsv.

M1 — Bootstrap CIs on every headline number
M2 — Size-stratified late-filer analysis
M3 — COVID regime handling on the trend
M4 — Firm-identity robustness + SIC 1-digit sectoral cut
M5 — Wilcoxon signed-rank test on within-firm deltas
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
DISCOVERIES = HERE / "discoveries"
RESULTS = HERE / "results.tsv"

RNG_SEED = 20260415


def load_all() -> pd.DataFrame:
    frames = []
    for f in sorted(RAW.glob("gpg_*.csv")):
        year = int(f.stem.split("_")[1])
        df = pd.read_csv(f, low_memory=False)
        df["reporting_year"] = year
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True, sort=False)
    gap_col = "DiffMedianHourlyPercent"
    combined[gap_col] = pd.to_numeric(combined[gap_col], errors="coerce")
    combined["DiffMeanHourlyPercent"] = pd.to_numeric(
        combined["DiffMeanHourlyPercent"], errors="coerce"
    )
    return combined


# ---------------------------------------------------------------------------
# M1 — Bootstrap CIs
# ---------------------------------------------------------------------------
def bootstrap_median_ci(values: np.ndarray, n_boot: int = 1000, rng=None) -> tuple[float, float, float]:
    rng = rng or np.random.default_rng(RNG_SEED)
    values = values[~np.isnan(values)]
    n = len(values)
    if n == 0:
        return (np.nan, np.nan, np.nan)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        sample = rng.choice(values, size=n, replace=True)
        boots[b] = np.median(sample)
    point = float(np.median(values))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return point, float(lo), float(hi)


def bootstrap_paired_delta_ci(delta: np.ndarray, n_boot: int = 1000, rng=None) -> tuple[float, float, float, float, float, float]:
    rng = rng or np.random.default_rng(RNG_SEED)
    delta = delta[~np.isnan(delta)]
    n = len(delta)
    boots_med = np.empty(n_boot)
    boots_share = np.empty(n_boot)
    for b in range(n_boot):
        sample = rng.choice(delta, size=n, replace=True)
        boots_med[b] = np.median(sample)
        boots_share[b] = (sample < 0).mean() * 100
    med_point = float(np.median(delta))
    share_point = float((delta < 0).mean() * 100)
    med_lo, med_hi = np.percentile(boots_med, [2.5, 97.5])
    sh_lo, sh_hi = np.percentile(boots_share, [2.5, 97.5])
    return med_point, float(med_lo), float(med_hi), share_point, float(sh_lo), float(sh_hi)


def run_m1(df: pd.DataFrame) -> list[dict]:
    gap = "DiffMedianHourlyPercent"
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    # 2017 and 2025 annual median with CI
    for yr in (2017, 2025):
        vals = df[df["reporting_year"] == yr][gap].dropna().to_numpy()
        pt, lo, hi = bootstrap_median_ci(vals, n_boot=1000, rng=rng)
        rows.append({
            "experiment_id": f"E02-M1-{yr}",
            "commit": "phase2.75",
            "description": f"Bootstrap 95% CI on {yr} population median gap",
            "metric": f"median_gap_{yr}",
            "value": f"{pt:.2f} [{lo:.2f}, {hi:.2f}]",
            "seed": RNG_SEED,
            "status": "RUN_RV",
            "notes": f"n={len(vals)}; 1000 bootstrap draws",
        })

    # Delta 2025 - 2017 via paired bootstrap of difference-of-medians
    v17 = df[df["reporting_year"] == 2017][gap].dropna().to_numpy()
    v25 = df[df["reporting_year"] == 2025][gap].dropna().to_numpy()
    boots = np.empty(1000)
    for b in range(1000):
        s17 = rng.choice(v17, size=len(v17), replace=True)
        s25 = rng.choice(v25, size=len(v25), replace=True)
        boots[b] = np.median(s25) - np.median(s17)
    pt_delta = np.median(v25) - np.median(v17)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    rows.append({
        "experiment_id": "E02-M1-delta",
        "commit": "phase2.75",
        "description": "Bootstrap 95% CI on 2025-minus-2017 population median delta",
        "metric": "delta_2025_minus_2017_pp",
        "value": f"{pt_delta:.2f} [{lo:.2f}, {hi:.2f}]",
        "seed": RNG_SEED,
        "status": "RUN_RV",
        "notes": "crosses-zero" if lo < 0 < hi else "excludes-zero",
    })

    # Within-firm panel
    pairs = df[df["reporting_year"].isin([2017, 2025])][
        ["EmployerName", "reporting_year", gap]
    ].dropna()
    pairs = pairs.pivot_table(
        index="EmployerName", columns="reporting_year", values=gap, aggfunc="first"
    ).dropna()
    delta = (pairs[2025] - pairs[2017]).to_numpy()
    med, med_lo, med_hi, share, sh_lo, sh_hi = bootstrap_paired_delta_ci(
        delta, n_boot=1000, rng=rng
    )
    rows.append({
        "experiment_id": "E02-M1-within",
        "commit": "phase2.75",
        "description": "Within-firm median delta (5259 firms 2017 & 2025) with CI",
        "metric": "within_firm_median_delta_pp",
        "value": f"{med:.2f} [{med_lo:.2f}, {med_hi:.2f}]",
        "seed": RNG_SEED,
        "status": "RUN_RV",
        "notes": f"n_pairs={len(delta)}; excludes-zero" if med_hi < 0 or med_lo > 0 else f"n_pairs={len(delta)}; crosses-zero",
    })
    rows.append({
        "experiment_id": "E02-M1-share",
        "commit": "phase2.75",
        "description": "Share of firms narrowing their gap (within-firm panel) with CI",
        "metric": "share_narrowed_pct",
        "value": f"{share:.1f} [{sh_lo:.1f}, {sh_hi:.1f}]",
        "seed": RNG_SEED,
        "status": "RUN_RV",
        "notes": f"n_pairs={len(delta)}; >50 => significant majority" if sh_lo > 50 else "crosses 50%",
    })

    # Late vs on-time difference (bootstrap difference of medians)
    ont = df[df["SubmittedAfterTheDeadline"] == False][gap].dropna().to_numpy()
    late = df[df["SubmittedAfterTheDeadline"] == True][gap].dropna().to_numpy()
    boots = np.empty(1000)
    for b in range(1000):
        s_ont = rng.choice(ont, size=len(ont), replace=True)
        s_late = rng.choice(late, size=len(late), replace=True)
        boots[b] = np.median(s_late) - np.median(s_ont)
    pt = np.median(late) - np.median(ont)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    rows.append({
        "experiment_id": "E02-M1-late",
        "commit": "phase2.75",
        "description": "Late-vs-on-time median gap difference with CI",
        "metric": "late_minus_ontime_pp",
        "value": f"{pt:.2f} [{lo:.2f}, {hi:.2f}]",
        "seed": RNG_SEED,
        "status": "RUN_RV",
        "notes": f"n_late={len(late)}; n_ontime={len(ont)}; "
                 + ("excludes-zero" if hi < 0 or lo > 0 else "crosses-zero"),
    })
    return rows


# ---------------------------------------------------------------------------
# M2 — Size-stratified late-filer analysis
# ---------------------------------------------------------------------------
def run_m2(df: pd.DataFrame) -> list[dict]:
    gap = "DiffMedianHourlyPercent"
    rows = []
    sub = df[[gap, "SubmittedAfterTheDeadline", "EmployerSize", "reporting_year"]].dropna(
        subset=[gap, "SubmittedAfterTheDeadline", "EmployerSize"]
    ).copy()
    # stratified medians
    strat = (
        sub.groupby(["EmployerSize", "SubmittedAfterTheDeadline"])[gap]
        .agg(["median", "size"])
        .reset_index()
    )
    strat.to_csv(DISCOVERIES / "late_vs_ontime_by_size.csv", index=False)
    # size-weighted overall late-minus-ontime after conditioning
    sizes = sub["EmployerSize"].unique()
    diffs = []
    weights = []
    for sz in sizes:
        s = sub[sub["EmployerSize"] == sz]
        med_late = s.loc[s["SubmittedAfterTheDeadline"] == True, gap].median()
        med_ont = s.loc[s["SubmittedAfterTheDeadline"] == False, gap].median()
        n = len(s)
        if pd.notna(med_late) and pd.notna(med_ont):
            diffs.append(med_late - med_ont)
            weights.append(n)
    size_weighted = float(np.average(diffs, weights=weights))
    rows.append({
        "experiment_id": "E02-M2-strat",
        "commit": "phase2.75",
        "description": "Size-weighted late-minus-ontime median gap difference (stratified)",
        "metric": "late_minus_ontime_size_weighted_pp",
        "value": f"{size_weighted:.2f}",
        "seed": RNG_SEED,
        "status": "CONTROL",
        "notes": f"strata_used={len(diffs)}; naive raw was -2.40pp; see discoveries/late_vs_ontime_by_size.csv",
    })
    # Per-stratum differences (one row per size band)
    for _, r in strat.pivot(index="EmployerSize", columns="SubmittedAfterTheDeadline", values="median").reset_index().iterrows():
        sz = r["EmployerSize"]
        med_late = r.get(True, np.nan)
        med_ont = r.get(False, np.nan)
        if pd.notna(med_late) and pd.notna(med_ont):
            diff = med_late - med_ont
            rows.append({
                "experiment_id": f"E02-M2-stratum-{str(sz).replace(' ', '_').replace(',', '')[:20]}",
                "commit": "phase2.75",
                "description": f"Late-minus-ontime median gap within size band '{sz}'",
                "metric": "diff_pp",
                "value": f"{diff:.2f}",
                "seed": RNG_SEED,
                "status": "CONTROL",
                "notes": f"median_late={med_late:.2f}; median_ontime={med_ont:.2f}",
            })

    # OLS with size + year FE
    model_df = sub.copy()
    model_df["late"] = model_df["SubmittedAfterTheDeadline"].astype(int)
    model_df["EmployerSize_cat"] = model_df["EmployerSize"].astype("category")
    model_df["year_cat"] = model_df["reporting_year"].astype("category")
    try:
        res = smf.ols(
            f"{gap} ~ late + C(EmployerSize_cat) + C(year_cat)", data=model_df
        ).fit()
        coef = res.params["late"]
        ci_lo, ci_hi = res.conf_int().loc["late"]
        pval = res.pvalues["late"]
        rows.append({
            "experiment_id": "E02-M2-ols",
            "commit": "phase2.75",
            "description": "OLS coef on SubmittedAfterDeadline with Size + Year FE",
            "metric": "ols_coef_late_pp",
            "value": f"{coef:.2f} [{ci_lo:.2f}, {ci_hi:.2f}]",
            "seed": RNG_SEED,
            "status": "CONTROL",
            "notes": f"p={pval:.3g}; n={int(res.nobs)}; outcome=DiffMedianHourlyPercent",
        })
    except Exception as e:  # pragma: no cover
        rows.append({
            "experiment_id": "E02-M2-ols",
            "commit": "phase2.75",
            "description": "OLS with Size + Year FE",
            "metric": "ols_coef_late_pp",
            "value": "FAIL",
            "seed": RNG_SEED,
            "status": "CONTROL",
            "notes": f"error: {e}",
        })
    return rows


# ---------------------------------------------------------------------------
# M3 — COVID regime handling
# ---------------------------------------------------------------------------
def run_m3(df: pd.DataFrame) -> list[dict]:
    gap = "DiffMedianHourlyPercent"
    annual = (
        df.groupby("reporting_year")[gap]
        .median()
        .reset_index()
        .rename(columns={gap: "median_gap"})
    )
    rows = []
    # (a) OLS no dummy
    x = sm.add_constant(annual["reporting_year"])
    res_a = sm.OLS(annual["median_gap"], x).fit()
    slope_a = res_a.params["reporting_year"]
    ci_lo_a, ci_hi_a = res_a.conf_int().loc["reporting_year"]
    rows.append({
        "experiment_id": "E02-M3-a",
        "commit": "phase2.75",
        "description": "OLS trend 2017-2025 no COVID dummy (slope pp/year)",
        "metric": "slope_pp_per_year",
        "value": f"{slope_a:.3f} [{ci_lo_a:.3f}, {ci_hi_a:.3f}]",
        "seed": RNG_SEED,
        "status": "TEMPORAL",
        "notes": f"p={res_a.pvalues['reporting_year']:.3g}; n={len(annual)}",
    })
    # (b) Excluding 2019-2021
    sub = annual[~annual["reporting_year"].isin([2019, 2020, 2021])]
    x = sm.add_constant(sub["reporting_year"])
    res_b = sm.OLS(sub["median_gap"], x).fit()
    slope_b = res_b.params["reporting_year"]
    ci_lo_b, ci_hi_b = res_b.conf_int().loc["reporting_year"]
    rows.append({
        "experiment_id": "E02-M3-b",
        "commit": "phase2.75",
        "description": "OLS trend excluding COVID years 2019-2021",
        "metric": "slope_pp_per_year",
        "value": f"{slope_b:.3f} [{ci_lo_b:.3f}, {ci_hi_b:.3f}]",
        "seed": RNG_SEED,
        "status": "TEMPORAL",
        "notes": f"p={res_b.pvalues['reporting_year']:.3g}; n={len(sub)}",
    })
    # (c) COVID dummy
    annual["covid"] = annual["reporting_year"].isin([2019, 2020, 2021]).astype(int)
    x = sm.add_constant(annual[["reporting_year", "covid"]])
    res_c = sm.OLS(annual["median_gap"], x).fit()
    slope_c = res_c.params["reporting_year"]
    ci_lo_c, ci_hi_c = res_c.conf_int().loc["reporting_year"]
    rows.append({
        "experiment_id": "E02-M3-c",
        "commit": "phase2.75",
        "description": "OLS trend with COVID dummy (2019-2021)",
        "metric": "slope_pp_per_year",
        "value": f"{slope_c:.3f} [{ci_lo_c:.3f}, {ci_hi_c:.3f}]",
        "seed": RNG_SEED,
        "status": "TEMPORAL",
        "notes": f"p_slope={res_c.pvalues['reporting_year']:.3g}; covid_coef={res_c.params['covid']:.2f}",
    })
    annual.to_csv(DISCOVERIES / "annual_trend_with_covid.csv", index=False)
    return rows


# ---------------------------------------------------------------------------
# M4 — Firm identity robustness + SIC 1-digit sectoral cut
# ---------------------------------------------------------------------------
SIC_DIVISION_MAP = {
    "01": "A", "02": "A", "03": "A",
    "05": "B", "06": "B", "07": "B", "08": "B", "09": "B",
    "10": "C", "11": "C", "12": "C", "13": "C", "14": "C", "15": "C",
    "16": "C", "17": "C", "18": "C", "19": "C", "20": "C", "21": "C",
    "22": "C", "23": "C", "24": "C", "25": "C", "26": "C", "27": "C",
    "28": "C", "29": "C", "30": "C", "31": "C", "32": "C", "33": "C",
    "35": "D",
    "36": "E", "37": "E", "38": "E", "39": "E",
    "41": "F", "42": "F", "43": "F",
    "45": "G", "46": "G", "47": "G",
    "49": "H", "50": "H", "51": "H", "52": "H", "53": "H",
    "55": "I", "56": "I",
    "58": "J", "59": "J", "60": "J", "61": "J", "62": "J", "63": "J",
    "64": "K", "65": "K", "66": "K",
    "68": "L",
    "69": "M", "70": "M", "71": "M", "72": "M", "73": "M", "74": "M", "75": "M",
    "77": "N", "78": "N", "79": "N", "80": "N", "81": "N", "82": "N",
    "84": "O",
    "85": "P",
    "86": "Q", "87": "Q", "88": "Q",
    "90": "R", "91": "R", "92": "R", "93": "R",
    "94": "S", "95": "S", "96": "S",
    "97": "T", "98": "T",
    "99": "U",
}

SIC_DIVISION_NAMES = {
    "A": "Agriculture",
    "B": "Mining/Quarrying",
    "C": "Manufacturing",
    "D": "Energy/Utilities",
    "E": "Water/Waste",
    "F": "Construction",
    "G": "Wholesale/Retail",
    "H": "Transport/Storage",
    "I": "Accommodation/Food",
    "J": "Info/Communication",
    "K": "Finance/Insurance",
    "L": "Real Estate",
    "M": "Professional/Scientific",
    "N": "Admin/Support",
    "O": "Public Administration",
    "P": "Education",
    "Q": "Health/Social Work",
    "R": "Arts/Entertainment",
    "S": "Other Services",
    "T": "Household employers",
    "U": "Extraterritorial",
}


def first_sic_division(sic_str) -> str | None:
    if pd.isna(sic_str):
        return None
    s = str(sic_str).strip().strip(",")
    if not s:
        return None
    # Take first comma-separated code
    first = s.split(",")[0].strip()
    # Normalise to at least 2 digits
    first = first.replace(" ", "")
    # Pad or take first 2 digits
    if len(first) < 2:
        return None
    two = first[:2]
    return SIC_DIVISION_MAP.get(two)


def run_m4(df: pd.DataFrame) -> list[dict]:
    gap = "DiffMedianHourlyPercent"
    rows = []
    # (a) identifier robustness
    for key in ["EmployerName", "CompanyNumber", "EmployerId"]:
        if key not in df.columns:
            rows.append({
                "experiment_id": f"E02-M4a-{key}",
                "commit": "phase2.75",
                "description": f"Within-firm panel keyed on {key}",
                "metric": "n_matched",
                "value": "MISSING",
                "seed": RNG_SEED,
                "status": "DIAG",
                "notes": f"{key} not in schema",
            })
            continue
        sub = df[df["reporting_year"].isin([2017, 2025])][[key, "reporting_year", gap]].dropna()
        # Drop blank keys
        sub = sub[sub[key].astype(str).str.strip() != ""]
        pivot = sub.pivot_table(
            index=key, columns="reporting_year", values=gap, aggfunc="first"
        ).dropna()
        if 2017 in pivot.columns and 2025 in pivot.columns:
            delta = pivot[2025] - pivot[2017]
            rows.append({
                "experiment_id": f"E02-M4a-{key}",
                "commit": "phase2.75",
                "description": f"Within-firm panel keyed on {key}",
                "metric": "n_and_median_delta",
                "value": f"n={len(delta)}; med_delta={delta.median():.2f}",
                "seed": RNG_SEED,
                "status": "DIAG",
                "notes": f"share_narrowed={(delta<0).mean()*100:.1f}%",
            })
    # (b) SIC 1-digit sectoral cut
    sub = df[df["reporting_year"].isin([2017, 2025])][
        ["SicCodes", "reporting_year", gap]
    ].copy()
    sub["division"] = sub["SicCodes"].apply(first_sic_division)
    sub = sub.dropna(subset=["division", gap])
    sector_tbl = (
        sub.groupby(["division", "reporting_year"])[gap]
        .agg(["median", "size"])
        .reset_index()
    )
    pivot = sector_tbl.pivot(index="division", columns="reporting_year", values="median")
    pivot["delta"] = pivot.get(2025, np.nan) - pivot.get(2017, np.nan)
    pivot["name"] = pivot.index.map(SIC_DIVISION_NAMES)
    pivot.to_csv(DISCOVERIES / "sector_trend_2017_vs_2025.csv")
    # Top 3 best-improving (most negative delta) and worst-improving
    if "delta" in pivot.columns:
        clean = pivot.dropna(subset=["delta"]).sort_values("delta")
        best3 = clean.head(3)
        worst3 = clean.tail(3)
        for div, r in best3.iterrows():
            rows.append({
                "experiment_id": f"E02-M4b-best-{div}",
                "commit": "phase2.75",
                "description": f"SIC {div} ({r['name']}) 2017→2025 median gap delta",
                "metric": "delta_pp",
                "value": f"{r['delta']:.2f}",
                "seed": RNG_SEED,
                "status": "DIAG",
                "notes": f"2017={r.get(2017, float('nan')):.2f}; 2025={r.get(2025, float('nan')):.2f}; BEST-IMPROVING",
            })
        for div, r in worst3.iterrows():
            rows.append({
                "experiment_id": f"E02-M4b-worst-{div}",
                "commit": "phase2.75",
                "description": f"SIC {div} ({r['name']}) 2017→2025 median gap delta",
                "metric": "delta_pp",
                "value": f"{r['delta']:.2f}",
                "seed": RNG_SEED,
                "status": "DIAG",
                "notes": f"2017={r.get(2017, float('nan')):.2f}; 2025={r.get(2025, float('nan')):.2f}; WORST-IMPROVING",
            })
    return rows


# ---------------------------------------------------------------------------
# M5 — Wilcoxon signed-rank on within-firm deltas
# ---------------------------------------------------------------------------
def run_m5(df: pd.DataFrame) -> list[dict]:
    gap = "DiffMedianHourlyPercent"
    pairs = df[df["reporting_year"].isin([2017, 2025])][
        ["EmployerName", "reporting_year", gap]
    ].dropna()
    pivot = pairs.pivot_table(
        index="EmployerName", columns="reporting_year", values=gap, aggfunc="first"
    ).dropna()
    delta = (pivot[2025] - pivot[2017]).to_numpy()
    # Wilcoxon signed-rank (H0: median = 0)
    # Alternative: two-sided
    w_stat, p_val = stats.wilcoxon(delta, alternative="two-sided")
    # One-sided: median < 0 => gap narrowed
    w_stat_less, p_val_less = stats.wilcoxon(delta, alternative="less")
    return [
        {
            "experiment_id": "E02-M5",
            "commit": "phase2.75",
            "description": "Wilcoxon signed-rank on within-firm delta (5259 pairs)",
            "metric": "wilcoxon_p_twosided",
            "value": f"{p_val:.3g}",
            "seed": RNG_SEED,
            "status": "RUN_RV",
            "notes": f"W={w_stat:.0f}; n={len(delta)}; one-sided p(delta<0)={p_val_less:.3g}",
        }
    ]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    df = load_all()
    print(f"[load] {len(df)} rows, {df['reporting_year'].min()}-{df['reporting_year'].max()}")

    all_rows = []
    print("\n=== M1 bootstrap CIs ===")
    m1 = run_m1(df)
    all_rows.extend(m1)
    for r in m1:
        print(f"  {r['experiment_id']}: {r['value']}  ({r['notes']})")

    print("\n=== M2 size-stratified late filer ===")
    m2 = run_m2(df)
    all_rows.extend(m2)
    for r in m2:
        print(f"  {r['experiment_id']}: {r['value']}  ({r['notes']})")

    print("\n=== M3 COVID regime ===")
    m3 = run_m3(df)
    all_rows.extend(m3)
    for r in m3:
        print(f"  {r['experiment_id']}: {r['value']}  ({r['notes']})")

    print("\n=== M4 firm identity + SIC ===")
    m4 = run_m4(df)
    all_rows.extend(m4)
    for r in m4:
        print(f"  {r['experiment_id']}: {r['value']}  ({r['notes']})")

    print("\n=== M5 Wilcoxon signed-rank ===")
    m5 = run_m5(df)
    all_rows.extend(m5)
    for r in m5:
        print(f"  {r['experiment_id']}: {r['value']}  ({r['notes']})")

    # Append to results.tsv (preserve existing rows)
    header = ["experiment_id", "commit", "description", "metric", "value",
              "seed", "status", "notes"]
    existing = RESULTS.read_text().rstrip("\n")
    with RESULTS.open("w") as f:
        f.write(existing + "\n")
        for r in all_rows:
            f.write("\t".join(str(r[c]) for c in header) + "\n")
    print(f"\nAppended {len(all_rows)} rows to {RESULTS}")


if __name__ == "__main__":
    main()
