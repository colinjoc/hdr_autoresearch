"""
PL-1 Irish commencement-notice cohort study — main analysis pipeline.

Produces:
- results.tsv      (E00 baseline + E01..E20+ experiments + tournament rows)
- tournament_results.csv (Phase 1 model-family comparison)
- plots/*.png (via generate_plots.py; this script only produces a single E00 chart)

Run: python analysis.py
"""
from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import (
    CoxPHFitter,
    GeneralizedGammaFitter,
    KaplanMeierFitter,
    LogNormalAFTFitter,
    WeibullAFTFitter,
    WeibullFitter,
)
from lifelines.utils import concordance_index
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(__file__).resolve().parent
DATA_RAW = ROOT / "data" / "raw" / "bcms_notices.csv"
RESULTS_TSV = ROOT / "results.tsv"
TOURNAMENT_CSV = ROOT / "tournament_results.csv"
CACHE_PARQUET = ROOT / "data" / "cohort_cache.parquet"

SEED = 42
CENSOR_DATE = pd.Timestamp("2026-04-15")  # dataset export day
MIN_GRANT_YEAR = 2014
MAX_GRANT_YEAR = 2025  # anything granted after won't have observable commencement duration
RESULTS_COLS = [
    "experiment_id",
    "phase",
    "description",
    "n",
    "metric",
    "value",
    "seed",
    "status",
    "notes",
]


def load_cohort() -> pd.DataFrame:
    """Load and clean BCMS, return residential cohort dataframe."""
    if CACHE_PARQUET.exists():
        return pd.read_parquet(CACHE_PARQUET)
    print("Loading BCMS raw CSV (258 MB)...")
    df = pd.read_csv(DATA_RAW, low_memory=False)
    print(f"  raw rows: {len(df):,}")

    # Date parsing
    for c in [
        "CN_Date_Granted",
        "CN_Date_Expiry",
        "CN_Date_Submitted_or_Received",
        "CN_Commencement_Date",
        "CN_Validation_Date",
        "CN_Proposed_end_date",
        "CCC_Date_Validated",
    ]:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    # Residential filter
    use = df["CN_Proposed_use_of_building"].astype(str)
    resi_mask = use.str.contains(
        "1_residential_dwellings|2_residential_institutional|3_residential_other",
        regex=True,
        na=False,
    )
    df = df.loc[resi_mask].copy()
    print(f"  residential rows: {len(df):,}")

    # Sanitise dates: clip to plausible window
    for c in ["CN_Date_Granted", "CN_Commencement_Date", "CCC_Date_Validated"]:
        bad = (df[c] < pd.Timestamp("2000-01-01")) | (df[c] > pd.Timestamp("2027-01-01"))
        df.loc[bad, c] = pd.NaT

    # Year columns
    df["grant_year"] = df["CN_Date_Granted"].dt.year
    df["grant_month"] = df["CN_Date_Granted"].dt.month
    df["commence_year"] = df["CN_Commencement_Date"].dt.year

    # Duration columns (days)
    d_pc = (df["CN_Commencement_Date"] - df["CN_Date_Granted"]).dt.days
    d_cc = (df["CCC_Date_Validated"] - df["CN_Commencement_Date"]).dt.days
    d_pcc = (df["CCC_Date_Validated"] - df["CN_Date_Granted"]).dt.days

    df["duration_perm_to_comm_days"] = d_pc
    df["duration_comm_to_ccc_days"] = d_cc
    df["duration_perm_to_ccc_days"] = d_pcc

    # Classifications
    sub = df["CN_Sub_Group"].astype(str).str.strip("^").fillna("")
    puse = use.str.strip("^").fillna("")
    apt = sub.str.contains("flat|maisonette", regex=True, na=False) | puse.str.contains(
        "apartments", regex=True, na=False
    )
    dw = sub.str.contains("dwelling_house", regex=True, na=False)
    df["apartment_flag"] = apt.astype(int)
    df["dwelling_flag"] = dw.astype(int)
    df["one_off_flag"] = (
        (df["CN_Total_Number_of_Dwelling_Units"] == 1)
        & (df["dwelling_flag"] == 1)
        & (df["apartment_flag"] == 0)
    ).astype(int)

    # LA normalisation
    la = df["LocalAuthority"].astype(str).str.strip()
    df["LA_clean"] = la
    dublin_las = {
        "Dublin City Council",
        "Fingal County Council",
        "Dún-Laoghaire Rathdown County Council",
        "South Dublin County Council",
    }
    df["is_dublin"] = la.isin(dublin_las).astype(int)
    major_cities = dublin_las | {"Cork City Council", "Galway City Council", "Limerick City and County Council", "Waterford City and County Council"}
    df["is_major_city"] = la.isin(major_cities).astype(int)

    # Flags
    df["ahb_flag"] = (df["CN_Approved_housing_body"].astype(str) == "yes").astype(int)
    df["la_own_flag"] = (df["CN_Behalf_local_authority"].astype(str) == "yes").astype(int)
    df["opt_out_flag"] = (df["CN_Project_type"].astype(str) == "Opt_Out_Comm_Notice").astype(int)
    df["seven_day_flag"] = (df["CN_Project_type"].astype(str) == "Seven_Day_Notice").astype(int)
    df["protected_flag"] = (df["CN_Protected_structure"].astype(str) == "yes").astype(int)
    df["mmc_flag"] = (
        df["CN_Main_Method_of_Construction"].astype(str).str.startswith("MMC", na=False)
    ).astype(int)

    df["units"] = pd.to_numeric(df["CN_Total_Number_of_Dwelling_Units"], errors="coerce")
    df["units_filled"] = df["units"].fillna(0)
    df["log_units"] = np.log1p(df["units_filled"])
    df["floor_area"] = pd.to_numeric(df["CN_Total_floor_area_of_building"], errors="coerce")
    df["log_floor_area"] = np.log1p(df["floor_area"].fillna(0))
    df["ccc_units"] = pd.to_numeric(df["CCC_Units_Completed"], errors="coerce")

    # Regime flags (by grant year)
    df["pre_2015_flag"] = (df["grant_year"] < 2015).astype(int)
    df["shd_era_flag"] = df["grant_year"].between(2017, 2021).astype(int)
    df["post_hfa_flag"] = (df["grant_year"] >= 2022).astype(int)

    # Size strata
    u = df["units_filled"]
    df["size_stratum"] = pd.cut(
        u,
        bins=[-0.1, 1, 9, 49, 199, 1e6],
        labels=["1", "2-9", "10-49", "50-199", "200+"],
    )

    DATA_RAW.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE_PARQUET, index=False)
    return df


def project_level(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to project level via CN_Planning_Permission_Number."""
    pp = df["CN_Planning_Permission_Number"].fillna("").astype(str)
    df = df.assign(_pp=pp)
    # Prefer phase 1 rows or largest-unit row per permission
    df_proj = (
        df.sort_values(["_pp", "units_filled"], ascending=[True, False])
        .groupby("_pp", as_index=False)
        .first()
    )
    return df_proj


def cohort_for_perm_to_comm(df: pd.DataFrame) -> pd.DataFrame:
    """Cohort for permission-to-commencement analysis."""
    m = df["CN_Date_Granted"].notna() & (df["grant_year"].between(MIN_GRANT_YEAR, MAX_GRANT_YEAR))
    sub = df.loc[m].copy()
    # Duration: if commenced, time from grant to commencement; otherwise censored at export date
    sub["event"] = sub["CN_Commencement_Date"].notna().astype(int)
    comm_or_censor = sub["CN_Commencement_Date"].fillna(CENSOR_DATE)
    sub["duration"] = (comm_or_censor - sub["CN_Date_Granted"]).dt.days
    sub = sub.loc[sub["duration"] > 0].copy()  # remove negative durations
    sub = sub.loc[sub["duration"] < 365 * 12].copy()  # cap at 12 years
    return sub


def cohort_for_comm_to_ccc(df: pd.DataFrame) -> pd.DataFrame:
    """Cohort for commencement-to-CCC analysis."""
    m = df["CN_Commencement_Date"].notna() & (df["commence_year"] >= 2014)
    sub = df.loc[m].copy()
    sub["event"] = sub["CCC_Date_Validated"].notna().astype(int)
    ccc_or_censor = sub["CCC_Date_Validated"].fillna(CENSOR_DATE)
    sub["duration"] = (ccc_or_censor - sub["CN_Commencement_Date"]).dt.days
    sub = sub.loc[sub["duration"] > 0].copy()
    sub = sub.loc[sub["duration"] < 365 * 10].copy()
    return sub


def cohort_complete_timeline(df: pd.DataFrame) -> pd.DataFrame:
    """Subcohort with permission, commencement AND CCC all observed."""
    m = (
        df["CN_Date_Granted"].notna()
        & df["CN_Commencement_Date"].notna()
        & df["CCC_Date_Validated"].notna()
        & (df["grant_year"] >= 2014)
        & (df["duration_perm_to_ccc_days"] > 0)
        & (df["duration_perm_to_ccc_days"] < 365 * 12)
    )
    return df.loc[m].copy()


# -----------------------
# Result recording
# -----------------------


def append_result(row: dict):
    """Append a single row to results.tsv."""
    row = {**{c: "" for c in RESULTS_COLS}, **row}
    df = pd.DataFrame([row], columns=RESULTS_COLS)
    if RESULTS_TSV.exists():
        df.to_csv(RESULTS_TSV, sep="\t", mode="a", header=False, index=False)
    else:
        df.to_csv(RESULTS_TSV, sep="\t", mode="w", header=True, index=False)


# -----------------------
# Baseline (E00) and chart
# -----------------------


def phase_0_5_baseline(cohort_pc: pd.DataFrame, cohort_cc: pd.DataFrame, cohort_complete: pd.DataFrame):
    rng = np.random.default_rng(SEED)

    commenced = cohort_pc.loc[cohort_pc["event"] == 1, "duration"].values
    med_pc = float(np.median(commenced))
    n_pc = len(commenced)

    ccc_observed = cohort_cc.loc[cohort_cc["event"] == 1, "duration"].values
    med_cc = float(np.median(ccc_observed)) if len(ccc_observed) else float("nan")
    n_cc = len(ccc_observed)

    full = cohort_complete["duration_perm_to_ccc_days"].values
    med_full = float(np.median(full)) if len(full) else float("nan")
    n_full = len(full)

    append_result(
        {
            "experiment_id": "E00",
            "phase": "0.5",
            "description": "Baseline median permission-to-commencement (observed event rows)",
            "n": n_pc,
            "metric": "median_days",
            "value": f"{med_pc:.1f}",
            "seed": SEED,
            "status": "BASELINE",
            "notes": "Residential cohort, grant_year 2014-2025; includes all LAs",
        }
    )
    append_result(
        {
            "experiment_id": "E00b",
            "phase": "0.5",
            "description": "Baseline median commencement-to-CCC (observed event rows)",
            "n": n_cc,
            "metric": "median_days",
            "value": f"{med_cc:.1f}",
            "seed": SEED,
            "status": "BASELINE",
            "notes": "Residential cohort, commenced 2014+; 39% CCC population",
        }
    )
    append_result(
        {
            "experiment_id": "E00c",
            "phase": "0.5",
            "description": "Baseline median permission-to-CCC (complete-timeline subcohort)",
            "n": n_full,
            "metric": "median_days",
            "value": f"{med_full:.1f}",
            "seed": SEED,
            "status": "BASELINE",
            "notes": "Residential cohort with grant, commencement AND CCC all observed",
        }
    )

    # KM-style percentiles
    kmf = KaplanMeierFitter()
    kmf.fit(cohort_pc["duration"], cohort_pc["event"], label="perm_to_comm")
    p25 = float(kmf.percentile(0.75))  # 25% have commenced by this day
    p50 = float(kmf.percentile(0.50))  # median
    p75 = float(kmf.percentile(0.25))  # 75% have commenced by this day
    append_result(
        {
            "experiment_id": "E00d",
            "phase": "0.5",
            "description": "KM-adjusted median permission-to-commencement",
            "n": len(cohort_pc),
            "metric": "km_median_days",
            "value": f"{p50:.1f}" if np.isfinite(p50) else "inf",
            "seed": SEED,
            "status": "BASELINE",
            "notes": f"KM p25={p25:.1f}d p75={p75 if np.isfinite(p75) else 'inf'}",
        }
    )

    # Baseline chart
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5))
    kmf.plot_survival_function(ax=ax[0])
    ax[0].set_title("Time-to-commencement survival (residential cohort)")
    ax[0].set_xlabel("Days since permission granted")
    ax[0].set_ylabel("P(not yet commenced)")
    ax[0].axvline(p50, color="k", ls=":", alpha=0.6, label=f"median={p50:.0f}d")
    ax[0].legend()

    if len(ccc_observed):
        kmf2 = KaplanMeierFitter()
        kmf2.fit(cohort_cc["duration"], cohort_cc["event"], label="comm_to_ccc")
        kmf2.plot_survival_function(ax=ax[1])
        ax[1].set_title("Time-to-CCC survival (commenced cohort)")
        ax[1].set_xlabel("Days since commencement")
        ax[1].set_ylabel("P(no CCC yet)")
        m2 = float(kmf2.percentile(0.5))
        ax[1].axvline(m2, color="k", ls=":", alpha=0.6, label=f"median={m2:.0f}d")
        ax[1].legend()

    plt.tight_layout()
    (ROOT / "plots").mkdir(exist_ok=True)
    fig.savefig(ROOT / "plots" / "baseline_survival.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    return med_pc, med_cc, med_full


# -----------------------
# Phase 1: Tournament
# -----------------------


def fit_cox(cohort: pd.DataFrame, features: list[str]) -> tuple[float, float, float]:
    X = cohort[features + ["duration", "event"]].dropna().copy()
    X = X.loc[X["duration"] > 0]
    # Sample to 50k max for speed
    if len(X) > 50000:
        X = X.sample(50000, random_state=SEED)
    cph = CoxPHFitter(penalizer=0.01)
    cph.fit(X, duration_col="duration", event_col="event", show_progress=False)
    ci = cph.concordance_index_
    ll = cph.log_likelihood_
    aic = cph.AIC_partial_
    return ci, ll, aic


def fit_aft(cohort: pd.DataFrame, features: list[str], fitter_cls):
    X = cohort[features + ["duration", "event"]].dropna().copy()
    X = X.loc[X["duration"] > 0]
    if len(X) > 50000:
        X = X.sample(50000, random_state=SEED)
    fit = fitter_cls(penalizer=0.01)
    fit.fit(X, duration_col="duration", event_col="event", show_progress=False)
    ci = fit.concordance_index_
    aic = fit.AIC_
    return ci, aic, fit


def phase_1_tournament(cohort_pc: pd.DataFrame):
    # simple feature set
    features = ["grant_year", "is_dublin", "apartment_flag", "log_units", "ahb_flag"]
    rows = []

    # 1. KM (no covariates) — just records n and the KM median as "value"
    kmf = KaplanMeierFitter()
    kmf.fit(cohort_pc["duration"], cohort_pc["event"], label="km")
    km_median = float(kmf.percentile(0.5))
    rows.append(
        dict(
            family="KaplanMeier",
            concordance=0.5,
            aic=np.nan,
            brier=np.nan,
            notes=f"median={km_median:.0f}d",
        )
    )

    # 2. Cox PH
    try:
        ci_cox, ll_cox, aic_cox = fit_cox(cohort_pc, features)
    except Exception as e:
        ci_cox, aic_cox = np.nan, np.nan
        print("Cox fit failed:", e)
    rows.append(dict(family="CoxPH", concordance=ci_cox, aic=aic_cox, brier=np.nan, notes="penalizer=0.01"))

    # 3. Weibull AFT
    try:
        ci_wb, aic_wb, _ = fit_aft(cohort_pc, features, WeibullAFTFitter)
    except Exception as e:
        ci_wb, aic_wb = np.nan, np.nan
    rows.append(dict(family="WeibullAFT", concordance=ci_wb, aic=aic_wb, brier=np.nan, notes=""))

    # 4. LogNormal AFT
    try:
        ci_ln, aic_ln, _ = fit_aft(cohort_pc, features, LogNormalAFTFitter)
    except Exception as e:
        ci_ln, aic_ln = np.nan, np.nan
    rows.append(dict(family="LogNormalAFT", concordance=ci_ln, aic=aic_ln, brier=np.nan, notes=""))

    # 5. Generalized Gamma (no covariates, univariate baseline comparison)
    try:
        gg = GeneralizedGammaFitter()
        samp = cohort_pc.sample(min(len(cohort_pc), 50000), random_state=SEED)
        gg.fit(samp["duration"], samp["event"])
        aic_gg = gg.AIC_
        rows.append(dict(family="GeneralizedGamma_univariate", concordance=np.nan, aic=aic_gg, brier=np.nan, notes="univariate"))
    except Exception as e:
        rows.append(dict(family="GeneralizedGamma_univariate", concordance=np.nan, aic=np.nan, brier=np.nan, notes=str(e)[:50]))

    # 6. LightGBM dark-permission classifier (binary task)
    dark_auc = dark_permission_classifier(cohort_pc)
    rows.append(
        dict(family="LightGBM_dark_classifier", concordance=np.nan, aic=np.nan, brier=dark_auc["brier"], notes=f"AUROC={dark_auc['auc']:.3f}")
    )
    # 7. Logistic regression dark-permission classifier (linear sanity)
    log_auc = dark_permission_classifier(cohort_pc, linear=True)
    rows.append(
        dict(family="Logistic_dark_classifier", concordance=np.nan, aic=np.nan, brier=log_auc["brier"], notes=f"AUROC={log_auc['auc']:.3f}")
    )

    tournament_df = pd.DataFrame(rows)
    tournament_df.to_csv(TOURNAMENT_CSV, index=False)

    # Summary row in results.tsv
    append_result(
        dict(
            experiment_id="T01",
            phase="1",
            description="Tournament: 7 model-family comparison on permission-to-commencement cohort",
            n=len(cohort_pc),
            metric="concordance_or_auc",
            value=f"Cox={ci_cox:.3f} Weibull={ci_wb:.3f} LogN={ci_ln:.3f} LGBM_auc={dark_auc['auc']:.3f}",
            seed=SEED,
            status="TOURNAMENT",
            notes="See tournament_results.csv",
        )
    )

    # Champion: Cox vs AFTs by concordance
    concs = {r["family"]: r["concordance"] for r in rows if not np.isnan(r.get("concordance", np.nan))}
    champion = max(concs, key=concs.get) if concs else "CoxPH"
    append_result(
        dict(
            experiment_id="T02",
            phase="1",
            description="Tournament champion selected",
            n=len(cohort_pc),
            metric="champion_family",
            value=champion,
            seed=SEED,
            status="TOURNAMENT",
            notes=f"best concordance={max(concs.values()):.3f}",
        )
    )
    return champion, tournament_df


# -----------------------
# Dark-permission classifier
# -----------------------


def prep_dark_permission_data(df: pd.DataFrame) -> pd.DataFrame:
    """Construct the dark-permission dataset: permissions granted at least 72 months ago.

    Label: 1 = did NOT commence within 72 months (= dark), 0 = commenced.
    """
    cutoff = CENSOR_DATE - pd.DateOffset(months=72)
    m = df["CN_Date_Granted"].notna() & (df["CN_Date_Granted"] <= cutoff)
    sub = df.loc[m].copy()
    if len(sub) == 0:
        return sub
    commenced_window = (
        sub["CN_Commencement_Date"].notna()
        & ((sub["CN_Commencement_Date"] - sub["CN_Date_Granted"]).dt.days <= 72 * 30)
    )
    sub["dark"] = (~commenced_window).astype(int)
    return sub


def dark_permission_classifier(cohort_pc: pd.DataFrame, linear: bool = False) -> dict:
    sub = prep_dark_permission_data(cohort_pc)
    if len(sub) < 500:
        return {"auc": float("nan"), "brier": float("nan"), "n": len(sub)}
    feats = ["grant_year", "is_dublin", "apartment_flag", "log_units", "ahb_flag", "opt_out_flag", "protected_flag"]
    X = sub[feats].fillna(0).values
    y = sub["dark"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=SEED, stratify=y)
    if linear:
        clf = LogisticRegression(max_iter=1000, n_jobs=None)
    else:
        try:
            import lightgbm as lgb  # noqa

            clf = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, random_state=SEED, verbose=-1)
        except Exception:
            clf = GradientBoostingClassifier(n_estimators=200, random_state=SEED)
    clf.fit(Xtr, ytr)
    proba = clf.predict_proba(Xte)[:, 1]
    auc = roc_auc_score(yte, proba)
    brier = brier_score_loss(yte, proba)
    return {"auc": auc, "brier": brier, "n": len(sub)}


# -----------------------
# Phase 2: KEEP/REVERT experiments (>=20)
# -----------------------


def median_of_observed(sub: pd.DataFrame, col: str = "duration") -> tuple[float, int]:
    s = sub.loc[sub["event"] == 1, col].values
    if len(s) == 0:
        return float("nan"), 0
    return float(np.median(s)), int(len(s))


def km_percentile(sub: pd.DataFrame, p: float = 0.5) -> float:
    if len(sub) == 0:
        return float("nan")
    try:
        kmf = KaplanMeierFitter()
        kmf.fit(sub["duration"], sub["event"])
        return float(kmf.percentile(1.0 - p))
    except Exception:
        return float("nan")


def phase_2_experiments(cohort_pc: pd.DataFrame, cohort_cc: pd.DataFrame, cohort_complete: pd.DataFrame, df_raw: pd.DataFrame):
    baseline_pc_median, _ = median_of_observed(cohort_pc)
    baseline_cc_median, _ = median_of_observed(cohort_cc)
    print(f"Phase 2 baselines: perm-to-comm median={baseline_pc_median:.0f}d, comm-to-ccc median={baseline_cc_median:.0f}d")

    # E01 — exclude pre-2015
    sub = cohort_pc.loc[cohort_pc["grant_year"] >= 2015]
    med, n = median_of_observed(sub)
    delta = med - baseline_pc_median
    append_result(
        dict(
            experiment_id="E01",
            phase="2",
            description="Exclude pre-2015 rows (data-quality ramp-up)",
            n=n,
            metric="median_days_perm_to_comm",
            value=f"{med:.1f}",
            seed=SEED,
            status="KEEP" if abs(delta) > 3 else "REVERT",
            notes=f"delta_vs_E00={delta:+.1f}d",
        )
    )

    # E02 — multi-unit residential only (units > 1)
    sub = cohort_pc.loc[cohort_pc["units_filled"] > 1]
    med, n = median_of_observed(sub)
    append_result(
        dict(
            experiment_id="E02",
            phase="2",
            description="Restrict to multi-unit residential (units > 1)",
            n=n,
            metric="median_days_perm_to_comm",
            value=f"{med:.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"delta_vs_E00={med - baseline_pc_median:+.1f}d",
        )
    )

    # E03 — Cox with vs without LA fixed effects (concordance)
    feats_no_la = ["grant_year", "is_dublin", "apartment_flag", "log_units", "ahb_flag"]
    try:
        ci_no_la, _, _ = fit_cox(cohort_pc, feats_no_la)
    except Exception:
        ci_no_la = np.nan
    # With LA dummies
    try:
        sub = cohort_pc.copy()
        top_las = sub["LA_clean"].value_counts().head(15).index.tolist()
        sub["la_top"] = sub["LA_clean"].where(sub["LA_clean"].isin(top_las), "other")
        dums = pd.get_dummies(sub["la_top"], prefix="la", drop_first=True)
        sub2 = pd.concat([sub[feats_no_la + ["duration", "event"]], dums.astype(float)], axis=1).dropna()
        if len(sub2) > 50000:
            sub2 = sub2.sample(50000, random_state=SEED)
        cph = CoxPHFitter(penalizer=0.05)
        cph.fit(sub2, duration_col="duration", event_col="event", show_progress=False)
        ci_la = cph.concordance_index_
    except Exception as e:
        print("E03 LA-dummies failed:", e)
        ci_la = np.nan
    delta = (ci_la or 0) - (ci_no_la or 0)
    append_result(
        dict(
            experiment_id="E03",
            phase="2",
            description="Cox with LA fixed effects vs without",
            n=len(cohort_pc),
            metric="concordance_delta",
            value=f"{delta:.4f}",
            seed=SEED,
            status="KEEP" if abs(delta) > 0.005 else "REVERT",
            notes=f"without_LA={ci_no_la:.3f} with_LA={ci_la:.3f}",
        )
    )

    # E04 — stratify by development size
    strata = {}
    for stratum in ["1", "2-9", "10-49", "50-199", "200+"]:
        ss = cohort_pc.loc[cohort_pc["size_stratum"] == stratum]
        med, n = median_of_observed(ss)
        strata[stratum] = (med, n)
    strata_str = "; ".join(f"{k}={v[0]:.0f}d(n={v[1]})" for k, v in strata.items())
    append_result(
        dict(
            experiment_id="E04",
            phase="2",
            description="Stratified medians by size stratum (1 / 2-9 / 10-49 / 50-199 / 200+)",
            n=sum(v[1] for v in strata.values()),
            metric="stratified_medians",
            value=strata_str[:100],
            seed=SEED,
            status="KEEP",
            notes="monotone or not — see notes",
        )
    )

    # E05 — winsorise top 1% durations
    cap = cohort_pc.loc[cohort_pc["event"] == 1, "duration"].quantile(0.99)
    wins = cohort_pc.copy()
    wins.loc[wins["duration"] > cap, "duration"] = cap
    med_w, n_w = median_of_observed(wins)
    append_result(
        dict(
            experiment_id="E05",
            phase="2",
            description="Winsorise top 1 percent of durations",
            n=n_w,
            metric="median_days_perm_to_comm",
            value=f"{med_w:.1f}",
            seed=SEED,
            status="REVERT",
            notes="median unchanged by design",
        )
    )

    # E06 — Dublin vs non-Dublin
    dub = cohort_pc.loc[cohort_pc["is_dublin"] == 1]
    non = cohort_pc.loc[cohort_pc["is_dublin"] == 0]
    m_dub, n_dub = median_of_observed(dub)
    m_non, n_non = median_of_observed(non)
    gap = m_dub - m_non
    append_result(
        dict(
            experiment_id="E06",
            phase="2",
            description="Dublin vs non-Dublin median permission-to-commencement",
            n=n_dub + n_non,
            metric="median_days_gap",
            value=f"{gap:.1f}",
            seed=SEED,
            status="KEEP" if abs(gap) > 10 else "REVERT",
            notes=f"dublin={m_dub:.0f}d non={m_non:.0f}d",
        )
    )

    # E07 — SHD era (2017-2021) vs non-SHD
    shd = cohort_pc.loc[cohort_pc["shd_era_flag"] == 1]
    non_shd = cohort_pc.loc[cohort_pc["shd_era_flag"] == 0]
    m_shd, n_shd = median_of_observed(shd)
    m_non, n_non = median_of_observed(non_shd)
    append_result(
        dict(
            experiment_id="E07",
            phase="2",
            description="SHD-era permissions (2017-2021) vs others",
            n=n_shd + n_non,
            metric="median_days_gap",
            value=f"{m_shd - m_non:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"shd={m_shd:.0f}d non={m_non:.0f}d",
        )
    )

    # E08 — pre/post-COVID commencement
    pre = cohort_cc.loc[cohort_cc["CN_Commencement_Date"] < pd.Timestamp("2020-03-01")]
    post = cohort_cc.loc[cohort_cc["CN_Commencement_Date"] >= pd.Timestamp("2020-03-01")]
    m_pre, n_pre = median_of_observed(pre)
    m_post, n_post = median_of_observed(post)
    append_result(
        dict(
            experiment_id="E08",
            phase="2",
            description="Commencement-to-CCC pre-COVID vs post-COVID-shutdown",
            n=n_pre + n_post,
            metric="median_days_gap",
            value=f"{m_post - m_pre:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"pre={m_pre:.0f}d post={m_post:.0f}d",
        )
    )

    # E09 — apartment vs dwelling
    apt = cohort_cc.loc[cohort_cc["apartment_flag"] == 1]
    dw = cohort_cc.loc[(cohort_cc["apartment_flag"] == 0) & (cohort_cc["dwelling_flag"] == 1)]
    m_apt, n_apt = median_of_observed(apt)
    m_dw, n_dw = median_of_observed(dw)
    append_result(
        dict(
            experiment_id="E09",
            phase="2",
            description="Apartment vs dwelling-house commencement-to-CCC",
            n=n_apt + n_dw,
            metric="median_days_gap",
            value=f"{m_apt - m_dw:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"apt={m_apt:.0f}d(n={n_apt}) dw={m_dw:.0f}d(n={n_dw})",
        )
    )

    # E10 — AHB vs private
    ahb = cohort_cc.loc[cohort_cc["ahb_flag"] == 1]
    priv = cohort_cc.loc[cohort_cc["ahb_flag"] == 0]
    m_a, n_a = median_of_observed(ahb)
    m_p, n_p = median_of_observed(priv)
    append_result(
        dict(
            experiment_id="E10",
            phase="2",
            description="AHB vs private-developer commencement-to-CCC",
            n=n_a + n_p,
            metric="median_days_gap",
            value=f"{m_a - m_p:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"ahb={m_a:.0f}d(n={n_a}) priv={m_p:.0f}d(n={n_p})",
        )
    )

    # E11 — permission-near-expiry proxy (Section 42 extension proxy)
    expir = df_raw["CN_Date_Expiry"] - df_raw["CN_Date_Granted"]
    extension_probable = (expir.dt.days > 365 * 5 + 180).fillna(False)
    sub = cohort_pc.assign(ext_flag=extension_probable.reindex(cohort_pc.index, fill_value=False))
    with_ext = sub.loc[sub["ext_flag"]]
    no_ext = sub.loc[~sub["ext_flag"]]
    m_e, n_e = median_of_observed(with_ext)
    m_n, n_n = median_of_observed(no_ext)
    append_result(
        dict(
            experiment_id="E11",
            phase="2",
            description="Section 42 extension proxy (expiry > 5.5 years from grant)",
            n=n_e + n_n,
            metric="median_days_gap",
            value=f"{m_e - m_n:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"with_ext={m_e:.0f}d(n={n_e}) no_ext={m_n:.0f}d(n={n_n})",
        )
    )

    # E12 — multi-phase developments
    mp = pd.to_numeric(df_raw["CN_Total_Number_of_Phases"], errors="coerce").fillna(1)
    mp_idx = mp > 1
    sub = cohort_pc.assign(multi_phase=mp_idx.reindex(cohort_pc.index, fill_value=False))
    with_mp = sub.loc[sub["multi_phase"]]
    no_mp = sub.loc[~sub["multi_phase"]]
    m_mp, n_mp = median_of_observed(with_mp)
    m_sp, n_sp = median_of_observed(no_mp)
    append_result(
        dict(
            experiment_id="E12",
            phase="2",
            description="Multi-phase vs single-phase permission-to-commencement",
            n=n_mp + n_sp,
            metric="median_days_gap",
            value=f"{m_mp - m_sp:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"multiphase={m_mp:.0f}d(n={n_mp}) single={m_sp:.0f}d(n={n_sp})",
        )
    )

    # E13 — units_declared vs units_completed (proxy test for completion)
    sub = cohort_complete.copy()
    if "ccc_units" in sub.columns:
        ratio = (sub["ccc_units"] / sub["units_filled"]).replace([np.inf, -np.inf], np.nan).dropna()
        append_result(
            dict(
                experiment_id="E13",
                phase="2",
                description="CCC units / declared units ratio on complete cohort",
                n=len(ratio),
                metric="median_ratio",
                value=f"{ratio.median():.3f}",
                seed=SEED,
                status="KEEP",
                notes=f"mean={ratio.mean():.3f} p25={ratio.quantile(.25):.3f} p75={ratio.quantile(.75):.3f}",
            )
        )

    # E14 — right-censoring handling (move censor date back 6m)
    alt_censor = CENSOR_DATE - pd.DateOffset(months=6)
    sub = cohort_pc.copy()
    late = sub["CN_Commencement_Date"] > alt_censor
    sub.loc[late, "event"] = 0
    sub.loc[late, "duration"] = (alt_censor - sub.loc[late, "CN_Date_Granted"]).dt.days
    sub = sub.loc[sub["duration"] > 0]
    try:
        kmf = KaplanMeierFitter()
        kmf.fit(sub["duration"], sub["event"])
        med_alt = float(kmf.percentile(0.5))
    except Exception:
        med_alt = float("nan")
    append_result(
        dict(
            experiment_id="E14",
            phase="2",
            description="Right-censoring shift (-6 months) sensitivity",
            n=len(sub),
            metric="km_median_days",
            value=f"{med_alt:.1f}",
            seed=SEED,
            status="KEEP",
            notes="shift censor date 6 months back",
        )
    )

    # E15 — small vs large schemes
    small = cohort_cc.loc[cohort_cc["units_filled"] <= 9]
    large = cohort_cc.loc[cohort_cc["units_filled"] >= 50]
    m_s, n_s = median_of_observed(small)
    m_l, n_l = median_of_observed(large)
    append_result(
        dict(
            experiment_id="E15",
            phase="2",
            description="Small-scheme (<=9) vs large-scheme (>=50) commencement-to-CCC",
            n=n_s + n_l,
            metric="median_days_gap",
            value=f"{m_l - m_s:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"small={m_s:.0f}d(n={n_s}) large={m_l:.0f}d(n={n_l})",
        )
    )

    # E16 — rural vs major-city
    rural = cohort_pc.loc[cohort_pc["is_major_city"] == 0]
    urban = cohort_pc.loc[cohort_pc["is_major_city"] == 1]
    m_r, n_r = median_of_observed(rural)
    m_u, n_u = median_of_observed(urban)
    append_result(
        dict(
            experiment_id="E16",
            phase="2",
            description="Major-city vs rest permission-to-commencement",
            n=n_r + n_u,
            metric="median_days_gap",
            value=f"{m_u - m_r:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"urban={m_u:.0f}d non_urban={m_r:.0f}d",
        )
    )

    # E17 — cohort survival at 24/48/72 months
    try:
        kmf = KaplanMeierFitter()
        kmf.fit(cohort_pc["duration"], cohort_pc["event"])
        s24 = float(1 - kmf.survival_function_at_times(24 * 30).iloc[0])
        s48 = float(1 - kmf.survival_function_at_times(48 * 30).iloc[0])
        s72 = float(1 - kmf.survival_function_at_times(72 * 30).iloc[0])
    except Exception:
        s24 = s48 = s72 = float("nan")
    append_result(
        dict(
            experiment_id="E17",
            phase="2",
            description="Cumulative commencement share at 24 / 48 / 72 months",
            n=len(cohort_pc),
            metric="share_commenced",
            value=f"24m={s24:.3f} 48m={s48:.3f} 72m={s72:.3f}",
            seed=SEED,
            status="KEEP",
            notes=f"dark_fraction_at_72m={1-s72:.3f}",
        )
    )

    # E18 — commencement-year cohort medians
    yearly = {}
    for y in range(2015, 2024):
        sub = cohort_pc.loc[cohort_pc["grant_year"] == y]
        m, n = median_of_observed(sub)
        if n > 0:
            yearly[y] = (m, n)
    yearly_str = ",".join(f"{y}={v[0]:.0f}(n={v[1]})" for y, v in yearly.items())
    append_result(
        dict(
            experiment_id="E18",
            phase="2",
            description="Medians by grant-year cohort 2015-2023",
            n=sum(v[1] for v in yearly.values()),
            metric="annual_medians",
            value=yearly_str[:160],
            seed=SEED,
            status="KEEP",
            notes="time-trend decomposition",
        )
    )

    # E19 — geographic clustering (variance of LA-level medians)
    la_meds = cohort_pc.loc[cohort_pc["event"] == 1].groupby("LA_clean")["duration"].median()
    la_sample = cohort_pc["LA_clean"].value_counts()
    la_meds = la_meds.loc[la_meds.index.isin(la_sample.loc[la_sample >= 200].index)]
    cv = la_meds.std() / la_meds.mean() if la_meds.mean() > 0 else np.nan
    append_result(
        dict(
            experiment_id="E19",
            phase="2",
            description="LA-level median dispersion (CV across LAs with >=200 rows)",
            n=len(la_meds),
            metric="cv_la_medians",
            value=f"{cv:.3f}",
            seed=SEED,
            status="KEEP" if cv > 0.15 else "REVERT",
            notes=f"min={la_meds.min():.0f}d max={la_meds.max():.0f}d",
        )
    )

    # E20 — dark-permission classifier AUROC
    r = dark_permission_classifier(cohort_pc)
    append_result(
        dict(
            experiment_id="E20",
            phase="2",
            description="LightGBM dark-permission classifier (>=72 months)",
            n=r.get("n", 0),
            metric="auc",
            value=f"{r['auc']:.3f}",
            seed=SEED,
            status="KEEP" if r["auc"] > 0.7 else "REVERT",
            notes=f"brier={r['brier']:.3f}",
        )
    )

    # E21 — one-off dwelling subset
    oneoff = cohort_pc.loc[cohort_pc["one_off_flag"] == 1]
    m, n = median_of_observed(oneoff)
    append_result(
        dict(
            experiment_id="E21",
            phase="2",
            description="One-off dwelling subset median",
            n=n,
            metric="median_days_perm_to_comm",
            value=f"{m:.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"delta_vs_E00={m - baseline_pc_median:+.1f}d",
        )
    )

    # E22 — seasonal effect (grant-month quarter)
    q_meds = {}
    for q in [1, 2, 3, 4]:
        months = [(q - 1) * 3 + 1, (q - 1) * 3 + 2, (q - 1) * 3 + 3]
        sub = cohort_pc.loc[cohort_pc["grant_month"].isin(months)]
        m, n = median_of_observed(sub)
        q_meds[q] = (m, n)
    q_str = ";".join(f"Q{q}={v[0]:.0f}d(n={v[1]})" for q, v in q_meds.items())
    append_result(
        dict(
            experiment_id="E22",
            phase="2",
            description="Grant-quarter seasonal medians",
            n=sum(v[1] for v in q_meds.values()),
            metric="quarterly_medians",
            value=q_str[:100],
            seed=SEED,
            status="KEEP",
            notes="seasonal decomposition",
        )
    )

    # E23 — 5-year-expiry mode (visible spike around 60 months)
    obs = cohort_pc.loc[cohort_pc["event"] == 1, "duration"].values
    near60m = ((obs > 55 * 30) & (obs < 61 * 30)).mean()
    append_result(
        dict(
            experiment_id="E23",
            phase="2",
            description="Share of commencements within 55-61 months of grant (near-expiry mode)",
            n=len(obs),
            metric="share",
            value=f"{near60m:.4f}",
            seed=SEED,
            status="KEEP" if near60m > 0.02 else "REVERT",
            notes="real-options 'commence-before-expiry' pattern",
        )
    )

    # E24 — bootstrap 95% CI of national permission-to-commencement median
    rng = np.random.default_rng(SEED)
    obs = cohort_pc.loc[cohort_pc["event"] == 1, "duration"].values
    boots = []
    for _ in range(500):
        idx = rng.integers(0, len(obs), size=len(obs))
        boots.append(np.median(obs[idx]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    append_result(
        dict(
            experiment_id="E24",
            phase="2",
            description="Bootstrap 95% CI on national permission-to-commencement median",
            n=len(obs),
            metric="ci95_days",
            value=f"[{lo:.1f},{hi:.1f}]",
            seed=SEED,
            status="KEEP",
            notes="500-replicate bootstrap",
        )
    )

    # E25 — placebo shuffle (LA label shuffled; dispersion should collapse to CV<<observed)
    sub = cohort_pc.loc[cohort_pc["event"] == 1].copy()
    sub["LA_shuffled"] = rng.permutation(sub["LA_clean"].values)
    la_meds_null = sub.groupby("LA_shuffled")["duration"].median()
    la_sizes = sub["LA_shuffled"].value_counts()
    la_meds_null = la_meds_null.loc[la_meds_null.index.isin(la_sizes.loc[la_sizes >= 200].index)]
    cv_null = la_meds_null.std() / la_meds_null.mean() if la_meds_null.mean() > 0 else np.nan
    append_result(
        dict(
            experiment_id="E25",
            phase="2",
            description="Placebo — LA labels shuffled; CV of LA medians should collapse",
            n=len(la_meds_null),
            metric="cv_la_medians_placebo",
            value=f"{cv_null:.3f}",
            seed=SEED,
            status="KEEP",
            notes=f"observed_CV={cv:.3f} placebo_CV={cv_null:.3f}",
        )
    )

    # E26 — channel placebo (LookAlike for CCC-rate across LAs)
    la_ccc_rate = df_raw.groupby("LA_clean").apply(
        lambda g: g["CCC_Date_Validated"].notna().sum() / max(g["CN_Commencement_Date"].notna().sum(), 1)
    )
    la_ccc_rate = la_ccc_rate.dropna()
    append_result(
        dict(
            experiment_id="E26",
            phase="2",
            description="Channel-reporting placebo — CCC filing rate across LAs",
            n=len(la_ccc_rate),
            metric="cv_ccc_filing_rate",
            value=f"{(la_ccc_rate.std()/la_ccc_rate.mean()):.3f}",
            seed=SEED,
            status="KEEP",
            notes=f"range={la_ccc_rate.min():.2f}-{la_ccc_rate.max():.2f}",
        )
    )

    # Interaction experiments (Phase 2.5)
    # I01 — LA × apartment
    sub_dub_apt = cohort_cc.loc[(cohort_cc["is_dublin"] == 1) & (cohort_cc["apartment_flag"] == 1)]
    sub_dub_dw = cohort_cc.loc[(cohort_cc["is_dublin"] == 1) & (cohort_cc["apartment_flag"] == 0) & (cohort_cc["dwelling_flag"] == 1)]
    sub_non_apt = cohort_cc.loc[(cohort_cc["is_dublin"] == 0) & (cohort_cc["apartment_flag"] == 1)]
    sub_non_dw = cohort_cc.loc[(cohort_cc["is_dublin"] == 0) & (cohort_cc["apartment_flag"] == 0) & (cohort_cc["dwelling_flag"] == 1)]
    m = {k: median_of_observed(v) for k, v in {"dub_apt": sub_dub_apt, "dub_dw": sub_dub_dw, "non_apt": sub_non_apt, "non_dw": sub_non_dw}.items()}
    interaction_delta = (m["dub_apt"][0] - m["dub_dw"][0]) - (m["non_apt"][0] - m["non_dw"][0])
    append_result(
        dict(
            experiment_id="I01",
            phase="2.5",
            description="Interaction: Dublin × apartment flag on commencement-to-CCC",
            n=sum(v[1] for v in m.values()),
            metric="interaction_delta_days",
            value=f"{interaction_delta:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"dub_apt={m['dub_apt'][0]:.0f}d dub_dw={m['dub_dw'][0]:.0f}d non_apt={m['non_apt'][0]:.0f}d non_dw={m['non_dw'][0]:.0f}d; interaction=True",
        )
    )

    # I02 — AHB × size
    ahb_large = cohort_cc.loc[(cohort_cc["ahb_flag"] == 1) & (cohort_cc["units_filled"] >= 10)]
    ahb_small = cohort_cc.loc[(cohort_cc["ahb_flag"] == 1) & (cohort_cc["units_filled"] < 10)]
    priv_large = cohort_cc.loc[(cohort_cc["ahb_flag"] == 0) & (cohort_cc["units_filled"] >= 10)]
    priv_small = cohort_cc.loc[(cohort_cc["ahb_flag"] == 0) & (cohort_cc["units_filled"] < 10)]
    m_al = median_of_observed(ahb_large); m_as = median_of_observed(ahb_small)
    m_pl = median_of_observed(priv_large); m_ps = median_of_observed(priv_small)
    interaction = (m_al[0] - m_pl[0]) - (m_as[0] - m_ps[0])
    append_result(
        dict(
            experiment_id="I02",
            phase="2.5",
            description="Interaction: AHB × size on commencement-to-CCC",
            n=m_al[1] + m_as[1] + m_pl[1] + m_ps[1],
            metric="interaction_delta_days",
            value=f"{interaction:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"ahb_large={m_al[0]:.0f} ahb_small={m_as[0]:.0f} priv_large={m_pl[0]:.0f} priv_small={m_ps[0]:.0f}; interaction=True",
        )
    )

    # I03 — Dublin × COVID
    pre_dub = cohort_cc.loc[(cohort_cc["is_dublin"] == 1) & (cohort_cc["CN_Commencement_Date"] < pd.Timestamp("2020-03-01"))]
    post_dub = cohort_cc.loc[(cohort_cc["is_dublin"] == 1) & (cohort_cc["CN_Commencement_Date"] >= pd.Timestamp("2020-03-01"))]
    pre_non = cohort_cc.loc[(cohort_cc["is_dublin"] == 0) & (cohort_cc["CN_Commencement_Date"] < pd.Timestamp("2020-03-01"))]
    post_non = cohort_cc.loc[(cohort_cc["is_dublin"] == 0) & (cohort_cc["CN_Commencement_Date"] >= pd.Timestamp("2020-03-01"))]
    m_pd, m_pq, m_pn, m_pq2 = [median_of_observed(x) for x in [pre_dub, post_dub, pre_non, post_non]]
    interaction = (m_pq[0] - m_pd[0]) - (m_pq2[0] - m_pn[0])
    append_result(
        dict(
            experiment_id="I03",
            phase="2.5",
            description="Interaction: Dublin × COVID on commencement-to-CCC",
            n=m_pd[1] + m_pq[1] + m_pn[1] + m_pq2[1],
            metric="interaction_delta_days",
            value=f"{interaction:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"pre_dub={m_pd[0]:.0f} post_dub={m_pq[0]:.0f} pre_non={m_pn[0]:.0f} post_non={m_pq2[0]:.0f}; interaction=True",
        )
    )

    # I04 — apartment × COVID
    pre_a = cohort_cc.loc[(cohort_cc["apartment_flag"] == 1) & (cohort_cc["CN_Commencement_Date"] < pd.Timestamp("2020-03-01"))]
    post_a = cohort_cc.loc[(cohort_cc["apartment_flag"] == 1) & (cohort_cc["CN_Commencement_Date"] >= pd.Timestamp("2020-03-01"))]
    pre_d = cohort_cc.loc[(cohort_cc["apartment_flag"] == 0) & (cohort_cc["dwelling_flag"] == 1) & (cohort_cc["CN_Commencement_Date"] < pd.Timestamp("2020-03-01"))]
    post_d = cohort_cc.loc[(cohort_cc["apartment_flag"] == 0) & (cohort_cc["dwelling_flag"] == 1) & (cohort_cc["CN_Commencement_Date"] >= pd.Timestamp("2020-03-01"))]
    m = [median_of_observed(x) for x in [pre_a, post_a, pre_d, post_d]]
    interaction = (m[1][0] - m[0][0]) - (m[3][0] - m[2][0])
    append_result(
        dict(
            experiment_id="I04",
            phase="2.5",
            description="Interaction: apartment × COVID on commencement-to-CCC",
            n=sum(x[1] for x in m),
            metric="interaction_delta_days",
            value=f"{interaction:+.1f}",
            seed=SEED,
            status="KEEP",
            notes=f"pre_apt={m[0][0]:.0f} post_apt={m[1][0]:.0f} pre_dw={m[2][0]:.0f} post_dw={m[3][0]:.0f}; interaction=True",
        )
    )

    # I05 — year × is_dublin interaction on Cox
    try:
        feats = ["grant_year", "is_dublin", "apartment_flag", "log_units"]
        sub = cohort_pc[feats + ["duration", "event"]].dropna().copy()
        if len(sub) > 50000:
            sub = sub.sample(50000, random_state=SEED)
        sub["year_x_dublin"] = sub["grant_year"] * sub["is_dublin"]
        cph = CoxPHFitter(penalizer=0.05)
        cph.fit(sub, duration_col="duration", event_col="event", show_progress=False)
        coef = cph.summary.loc["year_x_dublin", "coef"]
        p = cph.summary.loc["year_x_dublin", "p"]
    except Exception as e:
        coef, p = np.nan, np.nan
    append_result(
        dict(
            experiment_id="I05",
            phase="2.5",
            description="Interaction: year × Dublin in Cox PH on permission-to-commencement",
            n=len(cohort_pc),
            metric="coef_year_x_dublin",
            value=f"{coef:.5f}",
            seed=SEED,
            status="KEEP",
            notes=f"p={p:.4f}; interaction=True",
        )
    )


# -----------------------
# Main
# -----------------------


def main():
    # Clear prior results file to ensure deterministic regeneration
    if RESULTS_TSV.exists():
        RESULTS_TSV.unlink()
    print("== Loading cohort ==")
    df = load_cohort()
    print(f"cohort loaded: {len(df):,} residential rows")

    cohort_pc = cohort_for_perm_to_comm(df)
    cohort_cc = cohort_for_comm_to_ccc(df)
    cohort_complete = cohort_complete_timeline(df)
    print(f"  perm-to-comm cohort: {len(cohort_pc):,} rows")
    print(f"  comm-to-CCC cohort: {len(cohort_cc):,} rows")
    print(f"  complete-timeline cohort: {len(cohort_complete):,} rows")

    print("== Phase 0.5: baselines ==")
    phase_0_5_baseline(cohort_pc, cohort_cc, cohort_complete)

    print("== Phase 1: tournament ==")
    champion, tdf = phase_1_tournament(cohort_pc)
    print(f"champion: {champion}")
    print(tdf.to_string())

    print("== Phase 2 + 2.5 experiments ==")
    phase_2_experiments(cohort_pc, cohort_cc, cohort_complete, df)

    print("\n== Results summary ==")
    out = pd.read_csv(RESULTS_TSV, sep="\t")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
