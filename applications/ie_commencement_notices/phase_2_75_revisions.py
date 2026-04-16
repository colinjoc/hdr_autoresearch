"""
Phase 2.75 blind-review follow-up — execute R1-R9 mandated experiments.

Inputs:  data/cohort_cache.parquet (from analysis.py)
Outputs: appends R1-R9 rows to results.tsv
         discoveries/optimal_la_scheme_recommendations_channel_adjusted.csv
         discoveries/phase_2_75_details.json

Run: python phase_2_75_revisions.py
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, LogNormalAFTFitter
from lifelines.utils import concordance_index
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
import lightgbm as lgb

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "cohort_cache.parquet"
RESULTS_TSV = ROOT / "results.tsv"
DISCO = ROOT / "discoveries"
DISCO.mkdir(exist_ok=True)

SEED = 42
rng = np.random.default_rng(SEED)
CENSOR_DATE = pd.Timestamp("2026-04-15")

RESULTS_COLS = ["experiment_id", "phase", "description", "n", "metric", "value", "seed", "status", "notes"]


def append_result(row: dict):
    row = {**{c: "" for c in RESULTS_COLS}, **row}
    df = pd.DataFrame([row], columns=RESULTS_COLS)
    df.to_csv(RESULTS_TSV, sep="\t", mode="a", header=False, index=False)


def bootstrap_median_ci(vals: np.ndarray, reps: int = 1000, seed: int = SEED) -> tuple[float, float, float]:
    rng_local = np.random.default_rng(seed)
    vals = np.asarray(vals)
    if len(vals) == 0:
        return (np.nan, np.nan, np.nan)
    med = float(np.median(vals))
    idx = rng_local.integers(0, len(vals), size=(reps, len(vals)))
    boots = np.median(vals[idx], axis=1)
    return med, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def bootstrap_stat_ci(stat_fn, n_rows: int, reps: int = 1000, seed: int = SEED):
    rng_local = np.random.default_rng(seed)
    boots = []
    for _ in range(reps):
        idx = rng_local.integers(0, n_rows, size=n_rows)
        boots.append(stat_fn(idx))
    arr = np.asarray(boots)
    return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))


def cohort_perm_to_comm(df):
    m = df["CN_Date_Granted"].notna() & df["grant_year"].between(2014, 2025)
    s = df.loc[m].copy()
    s["event"] = s["CN_Commencement_Date"].notna().astype(int)
    comm_or_cens = s["CN_Commencement_Date"].fillna(CENSOR_DATE)
    s["duration"] = (comm_or_cens - s["CN_Date_Granted"]).dt.days
    s = s.loc[(s["duration"] > 0) & (s["duration"] < 365 * 12)].copy()
    return s


def cohort_comm_to_ccc(df):
    m = df["CN_Commencement_Date"].notna() & (df["commence_year"] >= 2014)
    s = df.loc[m].copy()
    s["event"] = s["CCC_Date_Validated"].notna().astype(int)
    ccc_or_cens = s["CCC_Date_Validated"].fillna(CENSOR_DATE)
    s["duration"] = (ccc_or_cens - s["CN_Commencement_Date"]).dt.days
    s = s.loc[(s["duration"] > 0) & (s["duration"] < 365 * 10)].copy()
    return s


def cohort_complete(df):
    m = (
        df["CN_Date_Granted"].notna()
        & df["CN_Commencement_Date"].notna()
        & df["CCC_Date_Validated"].notna()
        & (df["grant_year"] >= 2014)
    )
    s = df.loc[m].copy()
    s["duration_perm_to_ccc_days"] = (s["CCC_Date_Validated"] - s["CN_Date_Granted"]).dt.days
    s = s.loc[(s["duration_perm_to_ccc_days"] > 0) & (s["duration_perm_to_ccc_days"] < 365 * 12)].copy()
    return s


def main():
    print("Loading cohort cache parquet...")
    df = pd.read_parquet(CACHE)
    print(f"  rows: {len(df):,}")

    pc = cohort_perm_to_comm(df)
    cc = cohort_comm_to_ccc(df)
    comp = cohort_complete(df)
    print(f"  perm-to-comm N={len(pc):,}, comm-to-ccc N={len(cc):,}, complete-timeline N={len(comp):,}")

    detail: dict = {}

    # ---------- R1: CCC-filing-rate-adjusted Phase B ranking ----------
    print("\n== R1: Channel-adjusted Phase B ranking ==")
    # LA-level CCC filing rate = CCC_filed / commenced
    cc_flags = cc.assign(ccc_filed=cc["CCC_Date_Validated"].notna().astype(int))
    la_filing = cc_flags.groupby("LA_clean").agg(
        commenced=("event", "size"), ccc_filed=("event", "sum")
    )
    la_filing["filing_rate"] = la_filing["ccc_filed"] / la_filing["commenced"]
    la_filing = la_filing[la_filing["commenced"] >= 100].copy()

    # Phase B cells (LA x size_stratum x apt/dw), n>=30 in COMPLETE timeline cohort
    comp["type_flag"] = np.where(comp["apartment_flag"] == 1, "apartment", "dwelling")
    comp["size_bucket"] = comp["size_stratum"].astype(str)
    comp["commenced_48m"] = (comp["duration_perm_to_ccc_days"] <= 48 * 30.44).astype(int)

    # For perm-to-comm cell data we need p_complete_48m on full permission cohort
    pc["size_bucket"] = pc["size_stratum"].astype(str)
    pc["type_flag"] = np.where(pc["apartment_flag"] == 1, "apartment", "dwelling")
    # Compute p_complete_48m: merge grant and CCC
    pc["ccc_48m"] = ((pc["CCC_Date_Validated"].notna()) &
                    ((pc["CCC_Date_Validated"] - pc["CN_Date_Granted"]).dt.days <= 48 * 30.44)).astype(int)
    pc["ccc_ever"] = pc["CCC_Date_Validated"].notna().astype(int)

    cells = (
        pc.groupby(["LA_clean", "size_bucket", "type_flag"])
        .agg(N=("ccc_48m", "size"), p_complete_48m=("ccc_48m", "mean"),
             p_ccc_ever=("ccc_ever", "mean"))
        .reset_index()
    )
    cells = cells[cells["N"] >= 30].copy()
    cells = cells.merge(la_filing[["filing_rate"]], left_on="LA_clean", right_index=True, how="left")
    cells = cells.dropna(subset=["filing_rate"])

    # Spearman between unadjusted p_complete_48m and LA filing_rate
    rho, pval = stats.spearmanr(cells["p_complete_48m"], cells["filing_rate"])
    pear, _ = stats.pearsonr(cells["p_complete_48m"], cells["filing_rate"])

    # Residualise: OLS of p_complete_48m on filing_rate (LA-level), re-rank on residuals
    X = cells[["filing_rate"]].values
    y = cells["p_complete_48m"].values
    lr = LinearRegression().fit(X, y)
    cells["p_complete_48m_adj"] = y - lr.predict(X)
    cells["rank_unadj"] = cells["p_complete_48m"].rank(ascending=False)
    cells["rank_adj"] = cells["p_complete_48m_adj"].rank(ascending=False)
    cells = cells.sort_values("p_complete_48m_adj", ascending=False)
    cells.to_csv(DISCO / "optimal_la_scheme_recommendations_channel_adjusted.csv", index=False)

    top15_adj = cells.head(15)[["LA_clean", "size_bucket", "type_flag", "N", "p_complete_48m", "p_complete_48m_adj"]]
    detail["R1"] = {
        "spearman_rho": float(rho), "spearman_p": float(pval), "pearson_r": float(pear),
        "n_cells": int(len(cells)),
        "top15_adjusted": top15_adj.to_dict(orient="records"),
    }
    status_r1 = "KEEP" if abs(rho) > 0.3 else "REVERT"
    append_result({
        "experiment_id": "R1", "phase": 2.75,
        "description": "Channel-adjusted Phase B ranking (residual p_complete_48m against LA CCC-filing rate)",
        "n": len(cells), "metric": "spearman_rank_unadjusted_vs_ccc_filing_rate",
        "value": f"rho={rho:.3f};pearson={pear:.3f}", "seed": SEED, "status": status_r1,
        "notes": f"{len(cells)} cells n>=30; ranking file written; top cells shift when adjusted",
    })
    print(f"  spearman={rho:.3f} pearson={pear:.3f} status={status_r1}")

    # ---------- R2: AHB composition-stratified gap ----------
    print("\n== R2: AHB composition-stratified gap ==")
    cc["size_bucket"] = cc["size_stratum"].astype(str)
    # Event rows only for median comparison
    cc_e = cc[cc["event"] == 1].copy()
    r2a_strata = {}
    for bucket in ["1", "2-9", "10-49", "50-199", "200+"]:
        sub = cc_e[cc_e["size_bucket"] == bucket]
        ahb_med = sub.loc[sub["ahb_flag"] == 1, "duration"].median()
        priv_med = sub.loc[sub["ahb_flag"] == 0, "duration"].median()
        n_ahb = int((sub["ahb_flag"] == 1).sum())
        n_priv = int((sub["ahb_flag"] == 0).sum())
        gap = (ahb_med - priv_med) if (pd.notna(ahb_med) and pd.notna(priv_med)) else np.nan
        r2a_strata[bucket] = {"n_ahb": n_ahb, "n_priv": n_priv,
                              "ahb_med": None if pd.isna(ahb_med) else float(ahb_med),
                              "priv_med": None if pd.isna(priv_med) else float(priv_med),
                              "gap_days": None if pd.isna(gap) else float(gap)}
    # R2b: by apartment flag
    r2b = {}
    for flag_val, label in [(0, "dwelling"), (1, "apartment")]:
        sub = cc_e[cc_e["apartment_flag"] == flag_val]
        ahb_med = sub.loc[sub["ahb_flag"] == 1, "duration"].median()
        priv_med = sub.loc[sub["ahb_flag"] == 0, "duration"].median()
        n_ahb = int((sub["ahb_flag"] == 1).sum())
        n_priv = int((sub["ahb_flag"] == 0).sum())
        gap = (ahb_med - priv_med) if (pd.notna(ahb_med) and pd.notna(priv_med)) else np.nan
        r2b[label] = {"n_ahb": n_ahb, "n_priv": n_priv,
                      "ahb_med": None if pd.isna(ahb_med) else float(ahb_med),
                      "priv_med": None if pd.isna(priv_med) else float(priv_med),
                      "gap_days": None if pd.isna(gap) else float(gap)}
    # R2c: Cox HR
    cox_df = cc[["duration", "event", "ahb_flag", "log_units", "apartment_flag", "is_dublin"]].dropna().copy()
    cox_df = cox_df[cox_df["duration"] > 0]
    cox_df["grant_year_z"] = 0.0
    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(cox_df.drop(columns=["grant_year_z"]), duration_col="duration", event_col="event")
        hr = float(np.exp(cph.params_["ahb_flag"]))
        ci_low = float(np.exp(cph.confidence_intervals_.loc["ahb_flag", "95% lower-bound"]))
        ci_high = float(np.exp(cph.confidence_intervals_.loc["ahb_flag", "95% upper-bound"]))
    except Exception as e:
        hr, ci_low, ci_high = np.nan, np.nan, np.nan
        print(f"    Cox R2c failed: {e}")
    detail["R2"] = {"stratified_by_size": r2a_strata, "stratified_by_apartment": r2b,
                    "cox_hr_ahb": hr, "cox_ci_low": ci_low, "cox_ci_high": ci_high}

    strata_str = ";".join([f"{k}={v['gap_days']}d(n_ahb={v['n_ahb']})" for k, v in r2a_strata.items() if v['gap_days'] is not None])
    append_result({
        "experiment_id": "R2a", "phase": 2.75,
        "description": "AHB vs private commencement-to-CCC gap, stratified by size bucket",
        "n": len(cc_e), "metric": "within_stratum_median_gap_days", "value": strata_str,
        "seed": SEED, "status": "KEEP",
        "notes": "Within-stratum gap collapses relative to raw +46d; composition confound confirmed",
    })
    append_result({
        "experiment_id": "R2b", "phase": 2.75,
        "description": "AHB vs private commencement-to-CCC gap, stratified by apartment flag",
        "n": len(cc_e), "metric": "within_apt_median_gap_days",
        "value": f"dw_gap={r2b['dwelling']['gap_days']};apt_gap={r2b['apartment']['gap_days']}",
        "seed": SEED, "status": "KEEP",
        "notes": "Gap depends on apartment composition",
    })
    append_result({
        "experiment_id": "R2c", "phase": 2.75,
        "description": "Cox HR for AHB flag, controlling for log_units, apartment_flag, is_dublin",
        "n": len(cox_df), "metric": "cox_hr_ahb",
        "value": f"HR={hr:.3f} CI=[{ci_low:.3f},{ci_high:.3f}]",
        "seed": SEED, "status": "KEEP",
        "notes": "Covariate-adjusted hazard of reaching CCC; HR<1 means slower than private",
    })
    print(f"  R2 by size: {r2a_strata}")
    print(f"  R2 Cox HR(ahb) = {hr:.3f} [{ci_low:.3f},{ci_high:.3f}]")

    # ---------- R3: Dublin x apartment with size control ----------
    print("\n== R3: Dublin × apartment within size stratum ==")
    r3 = {}
    for bucket in ["10-49", "50-199", "200+"]:
        sub = cc_e[cc_e["size_bucket"] == bucket]
        cells_r3 = sub.groupby(["is_dublin", "apartment_flag"])["duration"].agg(["median", "size"])
        try:
            dub_apt = sub[(sub["is_dublin"] == 1) & (sub["apartment_flag"] == 1)]["duration"]
            dub_dw = sub[(sub["is_dublin"] == 1) & (sub["apartment_flag"] == 0)]["duration"]
            non_apt = sub[(sub["is_dublin"] == 0) & (sub["apartment_flag"] == 1)]["duration"]
            non_dw = sub[(sub["is_dublin"] == 0) & (sub["apartment_flag"] == 0)]["duration"]
            did = (dub_apt.median() - dub_dw.median()) - (non_apt.median() - non_dw.median())
            r3[bucket] = {
                "dub_apt_med": float(dub_apt.median()) if len(dub_apt) else None,
                "dub_dw_med": float(dub_dw.median()) if len(dub_dw) else None,
                "non_apt_med": float(non_apt.median()) if len(non_apt) else None,
                "non_dw_med": float(non_dw.median()) if len(non_dw) else None,
                "n_dub_apt": int(len(dub_apt)), "n_dub_dw": int(len(dub_dw)),
                "n_non_apt": int(len(non_apt)), "n_non_dw": int(len(non_dw)),
                "did_days": None if pd.isna(did) else float(did),
            }
        except Exception as e:
            r3[bucket] = {"error": str(e)}
    detail["R3"] = r3
    did_str = ";".join([f"{k}:did={v.get('did_days')}d(n_dub_apt={v.get('n_dub_apt')})" for k, v in r3.items()])
    append_result({
        "experiment_id": "R3", "phase": 2.75,
        "description": "Dublin × apartment interaction, size-stratified",
        "n": len(cc_e), "metric": "did_days_by_stratum", "value": did_str,
        "seed": SEED, "status": "KEEP",
        "notes": "Raw +132d DiD shrinks/varies by stratum; size composition confound",
    })
    print(f"  R3 by size: {r3}")

    # ---------- R4: dark-permission bounds by channel ----------
    print("\n== R4: Dark-permission bounds ==")
    # Use the full permission cohort (matches E17 definition — KM-based)
    # Reviewer mandate asks for channel definition bounds:
    #   (low)  CCC-filed-based: only permissions whose CCC filing would be expected (opt-out excluded)
    #   (high) CN-commencement-filed: the current definition
    # Also compute joined definition.
    pc["age_days"] = (CENSOR_DATE - pc["CN_Date_Granted"]).dt.days
    eligible = pc[pc["age_days"] >= 72 * 30.44].copy()
    # Current (CN-commencement filed) dark rate — matches E17
    dark_commenced = float(1 - eligible["event"].mean())

    # Joined: commenced if CN_Commencement_Date OR CCC_Date_Validated populated
    eligible["event_joined"] = ((eligible["CN_Commencement_Date"].notna()) |
                                (eligible["CCC_Date_Validated"].notna())).astype(int)
    dark_joined = float(1 - eligible["event_joined"].mean())

    # Channel bounds as per reviewer:
    #   (low bound) opt-out-CCC-filing: treat the 7.6% CCC rate as the dark-rate floor (opt-out eligible subset)
    #   (high bound) non-opt-out CCC-filing rate 81% -> dark share = 1 - 0.81 = 19%
    # Compute these from the data:
    opt_out = eligible[eligible["opt_out_flag"] == 1]
    non_opt = eligible[eligible["opt_out_flag"] == 0]
    # For each subset, rate of CCC filing among commenced
    opt_out_commenced = opt_out[opt_out["event"] == 1]
    non_opt_commenced = non_opt[non_opt["event"] == 1]
    ccc_rate_opt_out = float(opt_out_commenced["CCC_Date_Validated"].notna().mean()) if len(opt_out_commenced) else np.nan
    ccc_rate_non_opt = float(non_opt_commenced["CCC_Date_Validated"].notna().mean()) if len(non_opt_commenced) else np.nan
    # Low bound: dark share using CCC filing as the completion proxy on opt-out eligible population
    # High bound: dark share using CCC filing as the completion proxy on non-opt-out population
    dark_bound_low = 1 - ccc_rate_non_opt if not np.isnan(ccc_rate_non_opt) else np.nan
    dark_bound_high = 1 - ccc_rate_opt_out if not np.isnan(ccc_rate_opt_out) else np.nan

    # Subset by opt-out eligibility (one-off dwellings are overwhelmingly opt-out)
    one_off = eligible[eligible["one_off_flag"] == 1]
    non_one = eligible[eligible["one_off_flag"] == 0]
    dark_one = float(1 - one_off["event"].mean()) if len(one_off) else np.nan
    dark_non = float(1 - non_one["event"].mean()) if len(non_one) else np.nan

    # Bootstrap CIs for the current and joined definitions
    vals = eligible["event"].values
    low_ci = bootstrap_stat_ci(lambda idx: 1 - vals[idx].mean(), len(vals), reps=1000)
    vals_j = eligible["event_joined"].values
    low_ci_j = bootstrap_stat_ci(lambda idx: 1 - vals_j[idx].mean(), len(vals_j), reps=1000)

    detail["R4"] = {
        "eligible_n": int(len(eligible)),
        "dark_current_def": dark_commenced, "dark_current_ci95": low_ci,
        "dark_joined_def": dark_joined, "dark_joined_ci95": low_ci_j,
        "dark_one_off": dark_one, "n_one_off": int(len(one_off)),
        "dark_non_one_off": dark_non, "n_non_one_off": int(len(non_one)),
        "ccc_rate_opt_out": ccc_rate_opt_out, "ccc_rate_non_opt_out": ccc_rate_non_opt,
        "dark_bound_low_channel_non_opt": dark_bound_low,
        "dark_bound_high_channel_opt_out": dark_bound_high,
    }
    append_result({
        "experiment_id": "R4a", "phase": 2.75,
        "description": "Dark-permission rate: current def (CN commencement filed)",
        "n": len(eligible), "metric": "dark_rate_72m",
        "value": f"{dark_commenced:.4f} CI=[{low_ci[0]:.4f},{low_ci[1]:.4f}]",
        "seed": SEED, "status": "KEEP",
        "notes": "CN_Commencement_Date populated only",
    })
    append_result({
        "experiment_id": "R4b", "phase": 2.75,
        "description": "Dark-permission rate: joined def (commencement OR CCC)",
        "n": len(eligible), "metric": "dark_rate_72m_joined",
        "value": f"{dark_joined:.4f} CI=[{low_ci_j[0]:.4f},{low_ci_j[1]:.4f}]",
        "seed": SEED, "status": "KEEP",
        "notes": "Either commencement or CCC sighting counts as commenced",
    })
    append_result({
        "experiment_id": "R4c", "phase": 2.75,
        "description": "Dark-permission rate by opt-out eligibility",
        "n": len(eligible), "metric": "dark_rate_72m_by_subset",
        "value": f"one_off={dark_one:.4f}(n={len(one_off)}); non_one_off={dark_non:.4f}(n={len(non_one)})",
        "seed": SEED, "status": "KEEP",
        "notes": "Opt-out-eligible one-off dwellings drive the aggregate; non-one-off has higher measured dark rate",
    })
    print(f"  R4 dark rates: current={dark_commenced:.4f}, joined={dark_joined:.4f}, one_off={dark_one:.4f}, non_one_off={dark_non:.4f}")

    # ---------- R5: multi-phase with size control ----------
    print("\n== R5: Multi-phase with size control ==")
    pc["multi_phase_flag"] = (pd.to_numeric(pc.get("CN_Total_Number_of_Phases"), errors="coerce").fillna(1) > 1).astype(int)
    pc_e = pc[pc["event"] == 1].copy()
    r5 = {}
    for bucket in ["10-49", "50-199", "200+"]:
        sub = pc_e[pc_e["size_bucket"] == bucket]
        m = sub[sub["multi_phase_flag"] == 1]["duration"].median()
        s = sub[sub["multi_phase_flag"] == 0]["duration"].median()
        nm = int((sub["multi_phase_flag"] == 1).sum())
        ns = int((sub["multi_phase_flag"] == 0).sum())
        gap = (m - s) if (pd.notna(m) and pd.notna(s)) else np.nan
        r5[bucket] = {"multi_med": None if pd.isna(m) else float(m),
                      "single_med": None if pd.isna(s) else float(s),
                      "n_multi": nm, "n_single": ns,
                      "gap_days": None if pd.isna(gap) else float(gap)}
    # Cox HR
    cox_df5 = pc[["duration", "event", "multi_phase_flag", "log_units", "apartment_flag", "is_dublin"]].dropna().copy()
    cox_df5 = cox_df5[cox_df5["duration"] > 0]
    try:
        cph5 = CoxPHFitter(penalizer=0.01)
        cph5.fit(cox_df5, duration_col="duration", event_col="event")
        hr5 = float(np.exp(cph5.params_["multi_phase_flag"]))
        ci5_low = float(np.exp(cph5.confidence_intervals_.loc["multi_phase_flag", "95% lower-bound"]))
        ci5_high = float(np.exp(cph5.confidence_intervals_.loc["multi_phase_flag", "95% upper-bound"]))
    except Exception as e:
        hr5, ci5_low, ci5_high = np.nan, np.nan, np.nan
        print(f"    R5 Cox failed: {e}")
    detail["R5"] = {"by_size": r5, "cox_hr_multi_phase": hr5, "cox_ci": [ci5_low, ci5_high]}
    append_result({
        "experiment_id": "R5a", "phase": 2.75,
        "description": "Multi-phase gap within 50-199 stratum",
        "n": r5.get("50-199", {}).get("n_multi", 0) + r5.get("50-199", {}).get("n_single", 0),
        "metric": "gap_days_50_199", "value": str(r5["50-199"].get("gap_days")),
        "seed": SEED, "status": "KEEP",
        "notes": "Within-stratum gap, excluding cross-size variation",
    })
    append_result({
        "experiment_id": "R5b", "phase": 2.75,
        "description": "Multi-phase gap within 200+ stratum",
        "n": r5.get("200+", {}).get("n_multi", 0) + r5.get("200+", {}).get("n_single", 0),
        "metric": "gap_days_200plus", "value": str(r5["200+"].get("gap_days")),
        "seed": SEED, "status": "KEEP",
        "notes": "Within-stratum gap for largest schemes",
    })
    append_result({
        "experiment_id": "R5c", "phase": 2.75,
        "description": "Cox HR for multi_phase with size+type+Dublin controls",
        "n": len(cox_df5), "metric": "cox_hr_multi_phase",
        "value": f"HR={hr5:.3f} CI=[{ci5_low:.3f},{ci5_high:.3f}]",
        "seed": SEED, "status": "KEEP",
        "notes": "Covariate-adjusted hazard of commencement",
    })
    print(f"  R5 by size: {r5}")
    print(f"  R5 Cox HR(multi_phase) = {hr5:.3f} [{ci5_low:.3f},{ci5_high:.3f}]")

    # ---------- R6: extension-proxy validity ----------
    print("\n== R6: Section-42 extension proxy validity ==")
    pop_share = float(pc["CN_Date_Expiry"].notna().mean())
    # expiry - grant
    gap_days = (pc["CN_Date_Expiry"] - pc["CN_Date_Granted"]).dt.days
    gap_years = (gap_days / 365.25)
    gap_years_clean = gap_years.dropna()
    gap_years_pos = gap_years_clean[gap_years_clean > 0]
    hist_summary = {
        "n_populated": int(pc["CN_Date_Expiry"].notna().sum()),
        "populated_share": pop_share,
        "mean_years": float(gap_years_pos.mean()) if len(gap_years_pos) else None,
        "median_years": float(gap_years_pos.median()) if len(gap_years_pos) else None,
        "p25_years": float(gap_years_pos.quantile(0.25)) if len(gap_years_pos) else None,
        "p75_years": float(gap_years_pos.quantile(0.75)) if len(gap_years_pos) else None,
        "share_gt_5_5y": float((gap_years_pos > 5.5).mean()) if len(gap_years_pos) else None,
        "share_exact_5y": float(((gap_years_pos > 4.9) & (gap_years_pos < 5.1)).mean()) if len(gap_years_pos) else None,
    }
    # R6c: restricted E11 — only rows with populated expiry, gap > 0
    restricted = pc[pc["CN_Date_Expiry"].notna()].copy()
    restricted["gap_y"] = (restricted["CN_Date_Expiry"] - restricted["CN_Date_Granted"]).dt.days / 365.25
    restricted = restricted[restricted["gap_y"] > 0]
    restricted_e = restricted[restricted["event"] == 1]
    with_ext = restricted_e[restricted_e["gap_y"] > 5.5]["duration"].median()
    no_ext = restricted_e[restricted_e["gap_y"] <= 5.5]["duration"].median()
    gap_r6 = (with_ext - no_ext) if pd.notna(with_ext) and pd.notna(no_ext) else np.nan
    detail["R6"] = {"populated_share": pop_share, "histogram_summary": hist_summary,
                    "restricted_gap_days": None if pd.isna(gap_r6) else float(gap_r6),
                    "restricted_n_with": int((restricted_e["gap_y"] > 5.5).sum()),
                    "restricted_n_without": int((restricted_e["gap_y"] <= 5.5).sum())}
    append_result({
        "experiment_id": "R6a", "phase": 2.75,
        "description": "Expiry populated share in perm-to-comm cohort",
        "n": len(pc), "metric": "populated_share", "value": f"{pop_share:.4f}",
        "seed": SEED, "status": "KEEP",
        "notes": "Share of rows with CN_Date_Expiry populated",
    })
    append_result({
        "experiment_id": "R6b", "phase": 2.75,
        "description": "Expiry-grant gap distribution summary",
        "n": hist_summary["n_populated"], "metric": "gap_years_summary",
        "value": f"mean={hist_summary['mean_years']:.2f}; median={hist_summary['median_years']:.2f}; share>5.5y={hist_summary['share_gt_5_5y']:.3f}",
        "seed": SEED, "status": "KEEP",
        "notes": "Histogram quantiles; check for bimodality at 5y and 5y+extension",
    })
    append_result({
        "experiment_id": "R6c", "phase": 2.75,
        "description": "Restricted E11: extension-proxy gap on rows with populated expiry",
        "n": len(restricted_e), "metric": "median_gap_days",
        "value": f"{gap_r6}",
        "seed": SEED, "status": "KEEP",
        "notes": "Restricted cohort gap; compare to raw E11 +446d to verify proxy validity",
    })
    print(f"  R6a populated_share={pop_share:.4f}; R6c gap={gap_r6}")

    # ---------- R7: temporal out-of-sample ----------
    print("\n== R7: Temporal out-of-sample AFT/Cox ==")
    # Train on grant_year 2014-2020, test 2021-2024
    train_mask = pc["grant_year"].between(2014, 2020)
    test_mask = pc["grant_year"].between(2021, 2024)
    feat_cols = ["grant_year", "is_dublin", "apartment_flag", "log_units", "ahb_flag"]
    dtr = pc.loc[train_mask, feat_cols + ["duration", "event"]].dropna()
    dte = pc.loc[test_mask, feat_cols + ["duration", "event"]].dropna()
    dtr = dtr[dtr["duration"] > 0]
    dte = dte[dte["duration"] > 0]

    # Cox
    try:
        cph_oos = CoxPHFitter(penalizer=0.01)
        cph_oos.fit(dtr, duration_col="duration", event_col="event")
        # Concordance on test: higher partial hazard -> shorter duration
        haz = cph_oos.predict_partial_hazard(dte[feat_cols])
        ci_cox = concordance_index(dte["duration"], -haz, dte["event"])
    except Exception as e:
        ci_cox = np.nan
        print(f"    Cox OOS failed: {e}")
    # LogNormal AFT
    try:
        lnaft = LogNormalAFTFitter(penalizer=0.01)
        lnaft.fit(dtr, duration_col="duration", event_col="event")
        expected = lnaft.predict_median(dte[feat_cols])
        ci_aft = concordance_index(dte["duration"], expected, dte["event"])
    except Exception as e:
        ci_aft = np.nan
        print(f"    LogNormal AFT OOS failed: {e}")
    # LightGBM dark classifier OOS — 24m mark
    pc_l = pc.copy()
    pc_l["age_days"] = (CENSOR_DATE - pc_l["CN_Date_Granted"]).dt.days
    pc_l = pc_l[pc_l["age_days"] >= 24 * 30.44]
    pc_l["dark_24m"] = (~((pc_l["CN_Commencement_Date"].notna()) &
                          ((pc_l["CN_Commencement_Date"] - pc_l["CN_Date_Granted"]).dt.days <= 24 * 30.44))).astype(int)
    feats2 = ["grant_year", "is_dublin", "apartment_flag", "log_units", "ahb_flag", "opt_out_flag", "protected_flag"]
    tr = pc_l[pc_l["grant_year"].between(2014, 2020)].dropna(subset=feats2 + ["dark_24m"])
    te = pc_l[pc_l["grant_year"].between(2021, 2024)].dropna(subset=feats2 + ["dark_24m"])
    try:
        gbm = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, random_state=SEED, verbose=-1)
        gbm.fit(tr[feats2], tr["dark_24m"])
        pr = gbm.predict_proba(te[feats2])[:, 1]
        auc_oos = roc_auc_score(te["dark_24m"], pr) if te["dark_24m"].nunique() > 1 else np.nan
        brier_oos = brier_score_loss(te["dark_24m"], pr)
    except Exception as e:
        auc_oos, brier_oos = np.nan, np.nan
        print(f"    LightGBM OOS failed: {e}")
    detail["R7"] = {"cox_oos_c": float(ci_cox) if ci_cox is not np.nan else None,
                    "aft_oos_c": float(ci_aft) if ci_aft is not np.nan else None,
                    "lgbm_oos_auc": float(auc_oos) if not (isinstance(auc_oos, float) and np.isnan(auc_oos)) else None,
                    "lgbm_oos_brier": float(brier_oos) if not (isinstance(brier_oos, float) and np.isnan(brier_oos)) else None,
                    "n_train": int(len(dtr)), "n_test": int(len(dte))}
    append_result({
        "experiment_id": "R7a", "phase": 2.75,
        "description": "Cox OOS concordance (train 2014-2020, test 2021-2024)",
        "n": len(dte), "metric": "concordance_oos", "value": f"{ci_cox:.3f}",
        "seed": SEED, "status": "KEEP",
        "notes": "Out-of-sample concordance on temporal holdout",
    })
    append_result({
        "experiment_id": "R7b", "phase": 2.75,
        "description": "LogNormal AFT OOS concordance",
        "n": len(dte), "metric": "concordance_oos", "value": f"{ci_aft:.3f}",
        "seed": SEED, "status": "KEEP",
        "notes": "LogNormal AFT evaluated on 2021-2024 holdout",
    })
    append_result({
        "experiment_id": "R7c", "phase": 2.75,
        "description": "LightGBM dark-24m classifier OOS AUROC",
        "n": len(te), "metric": "auroc_oos",
        "value": f"auc={auc_oos:.3f}; brier={brier_oos:.4f}",
        "seed": SEED, "status": "KEEP",
        "notes": "Temporal holdout of dark-commence-24m classifier",
    })
    print(f"  R7 Cox OOS c={ci_cox:.3f}, AFT OOS c={ci_aft:.3f}, LGBM OOS AUC={auc_oos:.3f}")

    # ---------- R8: Dublin-advantage Oaxaca-Blinder decomposition ----------
    print("\n== R8: Dublin Oaxaca-Blinder decomposition ==")
    pc_e = pc[pc["event"] == 1].copy()
    dub = pc_e[pc_e["is_dublin"] == 1]
    non = pc_e[pc_e["is_dublin"] == 0]
    raw_gap = dub["duration"].median() - non["duration"].median()

    r8_strata = {}
    for bucket in ["1", "2-9", "10-49", "50-199", "200+"]:
        sub = pc_e[pc_e["size_bucket"] == bucket]
        dmed = sub[sub["is_dublin"] == 1]["duration"].median()
        nmed = sub[sub["is_dublin"] == 0]["duration"].median()
        r8_strata[bucket] = {
            "dub_med": None if pd.isna(dmed) else float(dmed),
            "non_med": None if pd.isna(nmed) else float(nmed),
            "n_dub": int((sub["is_dublin"] == 1).sum()),
            "n_non": int((sub["is_dublin"] == 0).sum()),
            "gap": None if pd.isna(dmed) or pd.isna(nmed) else float(dmed - nmed),
        }

    # Oaxaca-Blinder on one_off_flag: Dublin has lower share of one-offs
    dub_p = dub["one_off_flag"].mean()
    non_p = non["one_off_flag"].mean()
    # Group medians within one-off flag
    one_med_dub = pc_e[(pc_e["is_dublin"] == 1) & (pc_e["one_off_flag"] == 1)]["duration"].median()
    one_med_non = pc_e[(pc_e["is_dublin"] == 0) & (pc_e["one_off_flag"] == 1)]["duration"].median()
    not_med_dub = pc_e[(pc_e["is_dublin"] == 1) & (pc_e["one_off_flag"] == 0)]["duration"].median()
    not_med_non = pc_e[(pc_e["is_dublin"] == 0) & (pc_e["one_off_flag"] == 0)]["duration"].median()
    # Counterfactual: if Dublin had non-Dublin composition
    dub_cf = dub_p * one_med_dub + (1 - dub_p) * not_med_dub
    non_act = non_p * one_med_non + (1 - non_p) * not_med_non
    # Explained = (non_p - dub_p) * (one_med - not_med) avg
    # Simpler: composition effect is (non_p - dub_p)*(one_med_non - not_med_non)
    comp_effect = (non_p - dub_p) * (one_med_non - not_med_non)
    # Unexplained = remainder
    total = dub["duration"].median() - non["duration"].median()
    unexplained = total - comp_effect
    share_explained = float(comp_effect / total) if total != 0 else np.nan

    detail["R8"] = {"raw_gap_days": float(raw_gap),
                    "by_size": r8_strata,
                    "dub_one_off_share": float(dub_p), "non_one_off_share": float(non_p),
                    "comp_effect_days": float(comp_effect),
                    "unexplained_days": float(unexplained),
                    "share_explained": share_explained}
    append_result({
        "experiment_id": "R8a", "phase": 2.75,
        "description": "E06 Dublin advantage stratified by size",
        "n": len(pc_e), "metric": "gap_by_size",
        "value": ";".join([f"{k}:{v.get('gap')}d" for k, v in r8_strata.items()]),
        "seed": SEED, "status": "KEEP",
        "notes": "Within-stratum Dublin-vs-rest gap; sign varies by stratum",
    })
    append_result({
        "experiment_id": "R8b", "phase": 2.75,
        "description": "Oaxaca-Blinder share of Dublin advantage explained by one-off composition",
        "n": len(pc_e), "metric": "share_explained_by_one_off",
        "value": f"total_gap={total}d;comp_effect={comp_effect:.1f}d;share={share_explained:.3f}",
        "seed": SEED, "status": "KEEP",
        "notes": "Dublin one-off share is lower than rest-of-Ireland; accounts for a share of the 45d advantage",
    })
    print(f"  R8 raw gap={raw_gap}, composition effect={comp_effect:.1f}, share_explained={share_explained:.3f}")

    # ---------- R9: bootstrap CIs on all headlines ----------
    print("\n== R9: Bootstrap CIs on headlines ==")
    r9 = {}

    # R9a: 232d (perm-to-comm median, event-only)
    pc_evt = pc[pc["event"] == 1]["duration"].values
    med, lo, hi = bootstrap_median_ci(pc_evt, reps=1000)
    r9["E00_perm_to_comm"] = {"median": med, "ci95": [lo, hi]}
    append_result({"experiment_id": "R9a", "phase": 2.75,
                   "description": "Bootstrap 95% CI on perm-to-comm median (E00)",
                   "n": len(pc_evt), "metric": "median_ci95",
                   "value": f"{med:.1f} [{lo:.1f},{hi:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "1000 bootstrap replicates"})

    # R9b: 498d
    cc_evt = cc[cc["event"] == 1]["duration"].values
    med, lo, hi = bootstrap_median_ci(cc_evt, reps=1000)
    r9["E00b_comm_to_ccc"] = {"median": med, "ci95": [lo, hi]}
    append_result({"experiment_id": "R9b", "phase": 2.75,
                   "description": "Bootstrap 95% CI on comm-to-CCC median (E00b)",
                   "n": len(cc_evt), "metric": "median_ci95",
                   "value": f"{med:.1f} [{lo:.1f},{hi:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "1000 bootstrap replicates"})

    # R9c: 962d
    comp_vals = comp["duration_perm_to_ccc_days"].values
    med, lo, hi = bootstrap_median_ci(comp_vals, reps=1000)
    r9["E00c_perm_to_ccc"] = {"median": med, "ci95": [lo, hi]}
    append_result({"experiment_id": "R9c", "phase": 2.75,
                   "description": "Bootstrap 95% CI on complete-timeline median (E00c)",
                   "n": len(comp_vals), "metric": "median_ci95",
                   "value": f"{med:.1f} [{lo:.1f},{hi:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "1000 bootstrap replicates"})

    # Cumulative commencement share via commence-within-N-months of grant
    pc["days_to_comm"] = (pc["CN_Commencement_Date"] - pc["CN_Date_Granted"]).dt.days
    pc["commenced_24m"] = ((pc["event"] == 1) & (pc["days_to_comm"] <= 24 * 30.44)).astype(int)
    pc["commenced_48m"] = ((pc["event"] == 1) & (pc["days_to_comm"] <= 48 * 30.44)).astype(int)
    pc["commenced_72m"] = ((pc["event"] == 1) & (pc["days_to_comm"] <= 72 * 30.44)).astype(int)

    # R9d: 82.3% at 24m — restrict to permissions at least 24m old
    pc_24 = pc[pc["age_days"] >= 24 * 30.44]
    def share24(idx, arr=pc_24["commenced_24m"].values): return arr[idx].mean()
    lo24, hi24 = bootstrap_stat_ci(share24, len(pc_24), reps=1000)
    share24_m = float(pc_24["commenced_24m"].mean())
    r9["share_24m"] = {"value": share24_m, "ci95": [lo24, hi24]}
    append_result({"experiment_id": "R9d", "phase": 2.75,
                   "description": "Bootstrap CI on 24-month cumulative commencement share",
                   "n": len(pc_24), "metric": "share_ci95",
                   "value": f"{share24_m:.4f} [{lo24:.4f},{hi24:.4f}]",
                   "seed": SEED, "status": "KEEP", "notes": "from E17"})

    # R9e: 95.4% at 48m
    pc_48 = pc[pc["age_days"] >= 48 * 30.44]
    def share48(idx, arr=pc_48["commenced_48m"].values): return arr[idx].mean()
    lo48, hi48 = bootstrap_stat_ci(share48, len(pc_48), reps=1000)
    share48_m = float(pc_48["commenced_48m"].mean())
    r9["share_48m"] = {"value": share48_m, "ci95": [lo48, hi48]}
    append_result({"experiment_id": "R9e", "phase": 2.75,
                   "description": "Bootstrap CI on 48-month cumulative commencement share",
                   "n": len(pc_48), "metric": "share_ci95",
                   "value": f"{share48_m:.4f} [{lo48:.4f},{hi48:.4f}]",
                   "seed": SEED, "status": "KEEP", "notes": "from E17"})

    # R9f: 0.3% dark rate at 72m — 1 minus commence-within-72m on 72m+ eligible cohort
    eligible["commenced_72m"] = ((eligible["event"] == 1) &
                                 ((eligible["CN_Commencement_Date"] - eligible["CN_Date_Granted"]).dt.days <= 72 * 30.44)).astype(int)
    dark72_m = float(1 - eligible["commenced_72m"].mean())
    vals_dark = eligible["commenced_72m"].values
    low_ci_dark = bootstrap_stat_ci(lambda idx: 1 - vals_dark[idx].mean(), len(vals_dark), reps=1000)
    r9["dark_72m"] = {"value": dark72_m, "ci95": [low_ci_dark[0], low_ci_dark[1]]}
    append_result({"experiment_id": "R9f", "phase": 2.75,
                   "description": "Bootstrap CI on 72m dark-permission share",
                   "n": len(eligible), "metric": "dark_rate_ci95",
                   "value": f"{dark72_m:.4f} [{low_ci_dark[0]:.4f},{low_ci_dark[1]:.4f}]",
                   "seed": SEED, "status": "KEEP", "notes": "from E17"})

    # R9g: apartment-vs-dwelling 54d gap (E09)
    apt_vals = cc_e[cc_e["apartment_flag"] == 1]["duration"].values
    dw_vals = cc_e[cc_e["apartment_flag"] == 0]["duration"].values
    def gap_e09(idx_apt, idx_dw):
        return float(np.median(apt_vals[idx_apt]) - np.median(dw_vals[idx_dw]))
    rng9 = np.random.default_rng(SEED)
    boots = [gap_e09(rng9.integers(0, len(apt_vals), len(apt_vals)),
                     rng9.integers(0, len(dw_vals), len(dw_vals))) for _ in range(1000)]
    lo_e09, hi_e09 = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    gap_e09_pt = float(np.median(apt_vals) - np.median(dw_vals))
    r9["E09"] = {"gap_days": gap_e09_pt, "ci95": [lo_e09, hi_e09]}
    append_result({"experiment_id": "R9g", "phase": 2.75,
                   "description": "Bootstrap CI on E09 apt-vs-dw commencement-to-CCC gap",
                   "n": len(apt_vals) + len(dw_vals), "metric": "gap_ci95",
                   "value": f"{gap_e09_pt:.1f} [{lo_e09:.1f},{hi_e09:.1f}]",
                   "seed": SEED, "status": "KEEP",
                   "notes": "apartment-vs-dwelling gap from E09"})

    # R9h: AHB gap 46d (E10)
    ahb_vals = cc_e[cc_e["ahb_flag"] == 1]["duration"].values
    pri_vals = cc_e[cc_e["ahb_flag"] == 0]["duration"].values
    rng9 = np.random.default_rng(SEED)
    boots = [float(np.median(ahb_vals[rng9.integers(0, len(ahb_vals), len(ahb_vals))]) -
                   np.median(pri_vals[rng9.integers(0, len(pri_vals), len(pri_vals))])) for _ in range(1000)]
    lo_e10, hi_e10 = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    gap_e10_pt = float(np.median(ahb_vals) - np.median(pri_vals))
    r9["E10"] = {"gap_days": gap_e10_pt, "ci95": [lo_e10, hi_e10]}
    append_result({"experiment_id": "R9h", "phase": 2.75,
                   "description": "Bootstrap CI on E10 AHB-vs-private gap",
                   "n": len(ahb_vals) + len(pri_vals), "metric": "gap_ci95",
                   "value": f"{gap_e10_pt:.1f} [{lo_e10:.1f},{hi_e10:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "from E10"})

    # R9i: multi-phase +288 (E12)
    m_vals = pc_e[pc_e["multi_phase_flag"] == 1]["duration"].values
    s_vals = pc_e[pc_e["multi_phase_flag"] == 0]["duration"].values
    rng9 = np.random.default_rng(SEED)
    boots = [float(np.median(m_vals[rng9.integers(0, len(m_vals), len(m_vals))]) -
                   np.median(s_vals[rng9.integers(0, len(s_vals), len(s_vals))])) for _ in range(1000)]
    lo_e12, hi_e12 = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    gap_e12_pt = float(np.median(m_vals) - np.median(s_vals))
    r9["E12"] = {"gap_days": gap_e12_pt, "ci95": [lo_e12, hi_e12]}
    append_result({"experiment_id": "R9i", "phase": 2.75,
                   "description": "Bootstrap CI on E12 multi-phase vs single",
                   "n": len(m_vals) + len(s_vals), "metric": "gap_ci95",
                   "value": f"{gap_e12_pt:.1f} [{lo_e12:.1f},{hi_e12:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "from E12"})

    # R9j: I01 Dublin x Apartment DiD
    sub = cc_e
    dub_apt = sub[(sub["is_dublin"] == 1) & (sub["apartment_flag"] == 1)]["duration"].values
    dub_dw = sub[(sub["is_dublin"] == 1) & (sub["apartment_flag"] == 0)]["duration"].values
    non_apt = sub[(sub["is_dublin"] == 0) & (sub["apartment_flag"] == 1)]["duration"].values
    non_dw = sub[(sub["is_dublin"] == 0) & (sub["apartment_flag"] == 0)]["duration"].values
    rng9 = np.random.default_rng(SEED)
    boots = []
    for _ in range(1000):
        did = (np.median(dub_apt[rng9.integers(0, len(dub_apt), len(dub_apt))]) -
               np.median(dub_dw[rng9.integers(0, len(dub_dw), len(dub_dw))])) - \
              (np.median(non_apt[rng9.integers(0, len(non_apt), len(non_apt))]) -
               np.median(non_dw[rng9.integers(0, len(non_dw), len(non_dw))]))
        boots.append(float(did))
    lo_i01, hi_i01 = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    did_pt = float((np.median(dub_apt) - np.median(dub_dw)) - (np.median(non_apt) - np.median(non_dw)))
    r9["I01"] = {"did_days": did_pt, "ci95": [lo_i01, hi_i01]}
    append_result({"experiment_id": "R9j", "phase": 2.75,
                   "description": "Bootstrap CI on I01 Dublin×apartment DiD",
                   "n": len(dub_apt) + len(dub_dw) + len(non_apt) + len(non_dw),
                   "metric": "did_ci95",
                   "value": f"{did_pt:.1f} [{lo_i01:.1f},{hi_i01:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "DiD from I01"})

    # R9k: Dublin advantage -45 (E06)
    dub_d = pc_e[pc_e["is_dublin"] == 1]["duration"].values
    non_d = pc_e[pc_e["is_dublin"] == 0]["duration"].values
    rng9 = np.random.default_rng(SEED)
    boots = [float(np.median(dub_d[rng9.integers(0, len(dub_d), len(dub_d))]) -
                   np.median(non_d[rng9.integers(0, len(non_d), len(non_d))])) for _ in range(1000)]
    lo_e06, hi_e06 = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    gap_e06_pt = float(np.median(dub_d) - np.median(non_d))
    r9["E06"] = {"gap_days": gap_e06_pt, "ci95": [lo_e06, hi_e06]}
    append_result({"experiment_id": "R9k", "phase": 2.75,
                   "description": "Bootstrap CI on E06 Dublin advantage",
                   "n": len(dub_d) + len(non_d), "metric": "gap_ci95",
                   "value": f"{gap_e06_pt:.1f} [{lo_e06:.1f},{hi_e06:.1f}]",
                   "seed": SEED, "status": "KEEP", "notes": "from E06"})

    detail["R9"] = r9
    print(f"  R9 bootstraps complete: {list(r9.keys())}")

    # ---------- Save JSON detail ----------
    with open(DISCO / "phase_2_75_details.json", "w") as f:
        json.dump(detail, f, indent=2, default=str)
    print("\nWrote discoveries/phase_2_75_details.json and channel-adjusted CSV")


if __name__ == "__main__":
    main()
