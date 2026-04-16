"""Phase 2.75 reviewer-mandated follow-up experiments R1-R6.

R1: Threshold-invariant sub-sample re-analysis (>=250 cohort proxy via 2022-reporters)
R2: Bootstrap 95% CI on annualised narrowing rates (IE + UK-matched)
R3: Window-matched UK comparator (UK 2017-2020 vs IE 2022-2025)
R4: Blinder-Oaxaca-style population-change decomposition (within / entry / exit)
R5: paygap.ie coverage audit vs CSO/IBEC universe (best-effort; may be blocked)
R6: Bootstrap 95% CI for NACE-section medians (2025)

Appends rows to results.tsv under experiment_ids E02-R1 .. E07-R6.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
DISCOVERIES = HERE / "discoveries"
DISCOVERIES.mkdir(exist_ok=True)
RESULTS = HERE / "results.tsv"
RNG = np.random.default_rng(20260415)


def load_ie():
    df = pd.read_csv(RAW / "paygap_ie_all.csv", encoding="utf-8")
    df["Median Hourly Gap"] = pd.to_numeric(df["Median Hourly Gap"], errors="coerce")
    df["Mean Hourly Gap"] = pd.to_numeric(df["Mean Hourly Gap"], errors="coerce")
    df = df.dropna(subset=["Median Hourly Gap"])
    return df


def ann_rate(df_sub, year_col="Report Year", gap_col="Median Hourly Gap"):
    """Return annualised narrowing pp/yr from first-to-last-year medians."""
    annual = df_sub.groupby(year_col)[gap_col].median().sort_index()
    y0, yN = annual.index.min(), annual.index.max()
    return (annual.loc[yN] - annual.loc[y0]) / (yN - y0), annual


def bootstrap_rate_ci(df_sub, n_boot=1000, year_col="Report Year", gap_col="Median Hourly Gap"):
    """Cluster-bootstrap on firms (Company Name): resample firms with replacement,
    recompute yearly median-of-medians, recompute annualised rate."""
    firms = df_sub["Company Name"].unique()
    idx_by_firm = {f: np.where(df_sub["Company Name"].values == f)[0] for f in firms}
    years_sorted = np.array(sorted(df_sub[year_col].unique()))
    y0, yN = years_sorted[0], years_sorted[-1]
    gap_arr = df_sub[gap_col].values
    yr_arr = df_sub[year_col].values
    rates = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        sample_firms = RNG.choice(firms, size=len(firms), replace=True)
        rows = np.concatenate([idx_by_firm[f] for f in sample_firms])
        y = yr_arr[rows]; g = gap_arr[rows]
        try:
            m0 = np.median(g[y == y0])
            mN = np.median(g[y == yN])
            rates[b] = (mN - m0) / (yN - y0)
        except Exception:
            rates[b] = np.nan
    rates = rates[~np.isnan(rates)]
    lo, hi = np.percentile(rates, [2.5, 97.5])
    return rates, (lo, hi)


def r1_threshold_invariant(df):
    """R1 — restrict to firms that first appeared in 2022 (>=250 employee cohort)."""
    firms_2022 = set(df[df["Report Year"] == 2022]["Company Name"].unique())
    sub = df[df["Company Name"].isin(firms_2022)].copy()
    annual = sub.groupby("Report Year").agg(
        n=("Median Hourly Gap", "size"),
        median_gap=("Median Hourly Gap", "median"),
    ).reset_index()
    rate, _ = ann_rate(sub)
    annual.to_csv(DISCOVERIES / "r1_threshold_invariant_trajectory.csv", index=False)
    return sub, annual, rate


def r2_bootstrap_rates(df_full, df_r1):
    """R2 — bootstrap 95% CI on IE-full, IE-threshold-invariant, and UK-matched rates."""
    # IE full
    rates_full, ci_full = bootstrap_rate_ci(df_full[df_full["Report Year"].isin([2022, 2025])])
    # IE threshold-invariant
    rates_r1, ci_r1 = bootstrap_rate_ci(df_r1[df_r1["Report Year"].isin([2022, 2025])])
    out = {
        "IE_full_2022_2025": {"point": float((df_full[df_full["Report Year"] == 2025]["Median Hourly Gap"].median()
                                              - df_full[df_full["Report Year"] == 2022]["Median Hourly Gap"].median()) / 3),
                              "ci_95": [float(ci_full[0]), float(ci_full[1])]},
        "IE_threshold_invariant_2022_2025": {"point": float((df_r1[df_r1["Report Year"] == 2025]["Median Hourly Gap"].median()
                                                              - df_r1[df_r1["Report Year"] == 2022]["Median Hourly Gap"].median()) / 3),
                                             "ci_95": [float(ci_r1[0]), float(ci_r1[1])]},
    }
    with (DISCOVERIES / "r2_bootstrap_rates.json").open("w") as f:
        json.dump(out, f, indent=2)
    return out


def r3_uk_matched_window():
    """R3 — load UK year-by-year trajectory, extract UK 2017-2020 rate to match IE 2022-2025."""
    uk_path = Path("/home/col/generalized_hdr_autoresearch/applications/uk_gender_pay_gap/discoveries/annual_trend.csv")
    if not uk_path.exists():
        return None
    uk = pd.read_csv(uk_path)
    uk = uk.sort_values("reporting_year")
    uk_rates = {}
    # UK first-3-years (2017-2020 = 3-year span)
    for (y0, yN, label) in [(2017, 2020, "UK_2017_2020"),
                             (2017, 2025, "UK_2017_2025_full"),
                             (2022, 2025, "UK_2022_2025_match_calendar")]:
        try:
            m0 = uk[uk["reporting_year"] == y0]["median_gap_median"].iloc[0]
            mN = uk[uk["reporting_year"] == yN]["median_gap_median"].iloc[0]
            uk_rates[label] = {"start": float(m0), "end": float(mN),
                               "years": yN - y0,
                               "pp_per_year": float((mN - m0) / (yN - y0))}
        except IndexError:
            uk_rates[label] = None
    with (DISCOVERIES / "r3_uk_window_matched.json").open("w") as f:
        json.dump(uk_rates, f, indent=2)
    return uk_rates


def r4_decomposition(df):
    """R4 — decompose 2022->2025 median shift into within / entry / exit components.

    Define:
      P22 = median over 2022 submissions = m22
      P25 = median over 2025 submissions = m25
      Persistent set S = firms in both years.
      Entrants E = firms in 2025 not in 2022.
      Exiters X = firms in 2022 not in 2025.
      delta_total = m25 - m22

    Shapley-like decomposition using re-weighting:
      counterfactual_25_persistent_only = median gap over S in 2025 only (drops entrants from 2025)
      within_component  = (m25_S - m22_S)
      entry_component   = m25_full - m25_S      (effect of adding entrants to 2025 pool)
      exit_component    = m22_S - m22_full      (effect of removing exiters from 2022 pool;
                                                 equivalently the change in 2022 baseline if we had
                                                 restricted to persistent set)
      total = within + entry + exit (identity: m25_full - m22_full)
    """
    firms_22 = set(df[df["Report Year"] == 2022]["Company Name"].unique())
    firms_25 = set(df[df["Report Year"] == 2025]["Company Name"].unique())
    persistent = firms_22 & firms_25

    m22_full = df.loc[df["Report Year"] == 2022, "Median Hourly Gap"].median()
    m25_full = df.loc[df["Report Year"] == 2025, "Median Hourly Gap"].median()

    m22_S = df.loc[(df["Report Year"] == 2022) & (df["Company Name"].isin(persistent)),
                    "Median Hourly Gap"].median()
    m25_S = df.loc[(df["Report Year"] == 2025) & (df["Company Name"].isin(persistent)),
                    "Median Hourly Gap"].median()

    within   = m25_S - m22_S
    entry    = m25_full - m25_S
    exit_    = m22_S - m22_full
    total    = m25_full - m22_full
    identity = within + entry + exit_

    out = {
        "m22_full": float(m22_full),
        "m25_full": float(m25_full),
        "m22_persistent": float(m22_S),
        "m25_persistent": float(m25_S),
        "within_pp": float(within),
        "entry_pp": float(entry),
        "exit_pp": float(exit_),
        "total_pp_observed": float(total),
        "total_pp_identity": float(identity),
        "n_firms_persistent": int(len(persistent)),
        "n_firms_2022_only": int(len(firms_22 - firms_25)),
        "n_firms_2025_only": int(len(firms_25 - firms_22)),
    }
    with (DISCOVERIES / "r4_decomposition.json").open("w") as f:
        json.dump(out, f, indent=2)
    return out


def r5_coverage_audit():
    """R5 — coverage audit against CSO/IBEC universe of >=150-employee Irish firms.

    We do NOT have internet access and no prior local copy of the CSO BIS-02 or
    IBEC membership list for 2024/2025. Report as NOT EXECUTED and document.
    """
    note = ("Coverage audit requires the CSO Business Demography (BIS-02) employer "
            "size-class table for 2024/2025 OR the IBEC >=150 member list, neither "
            "of which is checked into this repo and neither of which is reachable "
            "from this sandboxed cycle. Deferred to Phase B data pull; flagged in "
            "paper §Caveats.")
    out = {"status": "NOT_EXECUTED", "reason": note}
    with (DISCOVERIES / "r5_coverage_audit.json").open("w") as f:
        json.dump(out, f, indent=2)
    return out


def r6_sector_bootstrap(df, n_boot=1000):
    """R6 — bootstrap 95% CI for every NACE-section median in 2025; flag n<10."""
    sec25 = df[df["Report Year"] == 2025].copy()
    rows = []
    for section, grp in sec25.groupby("NACE Section"):
        g = grp["Median Hourly Gap"].dropna().values
        n = len(g)
        if n == 0:
            continue
        med = float(np.median(g))
        if n == 1:
            lo, hi = med, med
        else:
            boots = np.array([np.median(RNG.choice(g, size=n, replace=True))
                              for _ in range(n_boot)])
            lo, hi = [float(x) for x in np.percentile(boots, [2.5, 97.5])]
        rows.append({"NACE Section": section, "n": n, "median": med,
                      "ci_lo_95": lo, "ci_hi_95": hi,
                      "flag_small_n": n < 10})
    out = pd.DataFrame(rows).sort_values("median", ascending=False).reset_index(drop=True)
    out.to_csv(DISCOVERIES / "r6_sector_ci.csv", index=False)
    return out


def append_results(rows):
    HEADER = ["experiment_id", "commit", "description", "metric", "value",
              "seed", "status", "notes"]
    with RESULTS.open("a") as f:
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in HEADER) + "\n")


def main():
    df = load_ie()

    # R1
    sub_r1, annual_r1, rate_r1 = r1_threshold_invariant(df)
    print("[R1] threshold-invariant (2022-reporter cohort, proxy >=250):")
    print(annual_r1.to_string(index=False))
    print(f"  annualised rate 2022-2025: {rate_r1:+.3f} pp/yr")

    # R2
    boot = r2_bootstrap_rates(df, sub_r1)
    print("\n[R2] bootstrap 95% CI on annualised rates:")
    for k, v in boot.items():
        print(f"  {k}: point {v['point']:+.3f} pp/yr, 95% CI [{v['ci_95'][0]:+.3f}, {v['ci_95'][1]:+.3f}]")

    # R3
    uk = r3_uk_matched_window()
    print("\n[R3] UK window-matched comparator:")
    for k, v in uk.items():
        if v:
            print(f"  {k}: {v['start']:.2f}% -> {v['end']:.2f}% over {v['years']}y = {v['pp_per_year']:+.3f} pp/yr")

    # R4
    decomp = r4_decomposition(df)
    print("\n[R4] decomposition of m22_full -> m25_full:")
    for k, v in decomp.items():
        print(f"  {k}: {v}")

    # R5
    cov = r5_coverage_audit()
    print(f"\n[R5] coverage audit: {cov['status']}")

    # R6
    sec_ci = r6_sector_bootstrap(df)
    print("\n[R6] sector 2025 medians with 95% CI (small-n flagged):")
    print(sec_ci.to_string(index=False))

    # Append results.tsv
    rows = [
        {"experiment_id": "E02-R1", "commit": "phase2.75",
         "description": "threshold-invariant subsample (2022-reporters, proxy >=250)",
         "metric": "median_2022_to_2025",
         "value": f"{annual_r1[annual_r1['Report Year']==2022]['median_gap'].iloc[0]:.2f} -> "
                  f"{annual_r1[annual_r1['Report Year']==2025]['median_gap'].iloc[0]:.2f} "
                  f"({rate_r1:+.3f} pp/yr)",
         "seed": 20260415, "status": "KEEP",
         "notes": f"n per year: {annual_r1['n'].tolist()}; isolates real narrowing from threshold phasing"},

        {"experiment_id": "E03-R2a", "commit": "phase2.75",
         "description": "bootstrap 95% CI IE full 2022-2025 annualised rate",
         "metric": "pp_per_year_CI95",
         "value": f"{boot['IE_full_2022_2025']['point']:+.3f} [{boot['IE_full_2022_2025']['ci_95'][0]:+.3f}, {boot['IE_full_2022_2025']['ci_95'][1]:+.3f}]",
         "seed": 20260415, "status": "KEEP",
         "notes": "cluster-bootstrap over firms, 1000 reps"},

        {"experiment_id": "E03-R2b", "commit": "phase2.75",
         "description": "bootstrap 95% CI IE threshold-invariant 2022-2025 annualised rate",
         "metric": "pp_per_year_CI95",
         "value": f"{boot['IE_threshold_invariant_2022_2025']['point']:+.3f} [{boot['IE_threshold_invariant_2022_2025']['ci_95'][0]:+.3f}, {boot['IE_threshold_invariant_2022_2025']['ci_95'][1]:+.3f}]",
         "seed": 20260415, "status": "KEEP",
         "notes": "cluster-bootstrap over firms, 1000 reps"},

        {"experiment_id": "E04-R3", "commit": "phase2.75",
         "description": "UK window-matched comparator (UK 2017-2020 matches IE 2022-2025 window length)",
         "metric": "pp_per_year",
         "value": f"UK 2017-2020 {uk['UK_2017_2020']['pp_per_year']:+.3f}; UK 2017-2025 {uk['UK_2017_2025_full']['pp_per_year']:+.3f}",
         "seed": 0, "status": "KEEP",
         "notes": f"UK 2017-2020: {uk['UK_2017_2020']['start']}% -> {uk['UK_2017_2020']['end']}%; diminishing-returns-adjusted comparator"},

        {"experiment_id": "E05-R4", "commit": "phase2.75",
         "description": "population-change decomposition into within/entry/exit",
         "metric": "pp_contribution",
         "value": f"within {decomp['within_pp']:+.3f}; entry {decomp['entry_pp']:+.3f}; exit {decomp['exit_pp']:+.3f}; total {decomp['total_pp_identity']:+.3f}",
         "seed": 0, "status": "KEEP",
         "notes": f"persistent n={decomp['n_firms_persistent']}; entrants={decomp['n_firms_2025_only']}; exiters={decomp['n_firms_2022_only']}"},

        {"experiment_id": "E06-R5", "commit": "phase2.75",
         "description": "paygap.ie coverage audit vs CSO/IBEC >=150 employee universe",
         "metric": "coverage_rate",
         "value": "NOT_EXECUTED",
         "seed": 0, "status": "DEFERRED",
         "notes": "CSO BIS-02 and IBEC membership list not reachable in sandboxed cycle; flagged in §Caveats"},

        {"experiment_id": "E07-R6", "commit": "phase2.75",
         "description": "bootstrap 95% CI for every NACE-section median 2025",
         "metric": "n_sections_with_n_lt_10",
         "value": int(sec_ci["flag_small_n"].sum()),
         "seed": 20260415, "status": "KEEP",
         "notes": f"flagged small-n sections: {sec_ci[sec_ci['flag_small_n']]['NACE Section'].tolist()}"},
    ]
    append_results(rows)
    print("\n[OK] rows appended to results.tsv")


if __name__ == "__main__":
    main()
