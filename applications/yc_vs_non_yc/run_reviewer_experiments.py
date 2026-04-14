"""Phase 2.75 mandatory follow-up experiments RV01-RV05, RV07.

RV06 (Techstars placebo) requires external data scraping and is deferred
to a separate step; documented in paper_review.md as known gap.

Each experiment logs one+ rows to results.tsv with status="REVIEW".
"""
from __future__ import annotations

import glob
import sys
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import ExperimentResult, append_result, risk_diff_with_ci  # noqa: E402
from secformd_loader import (  # noqa: E402
    filter_seed_stage, join_formd_tables, load_formd_quarter,
)
from yc_loader import load_yc_companies  # noqa: E402
from matcher import match_yc_to_formd  # noqa: E402
from fuzzy_matcher import fuzzy_match_yc  # noqa: E402
from build_panel import outcome_follow_on  # noqa: E402


CAT_FEATURES = ["filing_year", "filing_quarter", "stateorcountry",
                "industrygrouptype", "entitytype"]
BAY_STATES = {"CA"}
NYC_STATES = {"NY"}
BOS_STATES = {"MA"}


def load_vix() -> pd.DataFrame:
    vix = pd.read_csv(HERE / "data" / "vix_daily.csv")
    vix.columns = ["date", "vix"]
    vix["date"] = pd.to_datetime(vix["date"])
    vix["vix"] = pd.to_numeric(vix["vix"], errors="coerce").ffill()
    return vix


def augment_panel_with_ecosystem(panel: pd.DataFrame, seed: pd.DataFrame) -> pd.DataFrame:
    """Add real ecosystem covariates for RV01."""
    p = panel.copy()
    p["filing_date"] = pd.to_datetime(p["filing_date"])
    p["filing_year"] = p["filing_date"].dt.year.astype(int)
    p["is_sf_bay"] = p["stateorcountry"].isin(BAY_STATES).astype(int)
    p["is_nyc"] = p["stateorcountry"].isin(NYC_STATES).astype(int)
    p["is_boston"] = p["stateorcountry"].isin(BOS_STATES).astype(int)

    # MSA VC density proxy: state-year seed-stage Form D count (log)
    s = seed.copy()
    s["filing_date"] = pd.to_datetime(s["filing_date"], errors="coerce")
    s["filing_year"] = s["filing_date"].dt.year.astype("Int64")
    sy = (s.dropna(subset=["filing_year"])
           .groupby(["stateorcountry", "filing_year"]).size()
           .rename("state_year_seed_filings").reset_index())
    sy["log_state_year_density"] = np.log1p(sy["state_year_seed_filings"])
    p = p.merge(sy[["stateorcountry", "filing_year", "log_state_year_density"]],
                on=["stateorcountry", "filing_year"], how="left")
    p["log_state_year_density"] = p["log_state_year_density"].fillna(0)

    # VIX on filing date (backfill missing trading days)
    vix = load_vix().rename(columns={"date": "filing_date"})
    p = p.sort_values("filing_date")
    vix = vix.sort_values("filing_date")
    p = pd.merge_asof(p, vix, on="filing_date", direction="backward")
    p["vix"] = p["vix"].fillna(p["vix"].median())
    return p


def fit_ps(df, covs, model="logistic"):
    num = [c for c in covs if c not in CAT_FEATURES]
    cats = [c for c in covs if c in CAT_FEATURES]
    parts = []
    if cats:
        enc = OneHotEncoder(handle_unknown="ignore", sparse_output=True, min_frequency=5)
        enc.fit(df[cats].astype(str))
        parts.append(enc.transform(df[cats].astype(str)))
    if num:
        parts.append(csr_matrix(df[num].to_numpy(dtype=float)))
    X = hstack(parts).tocsr() if parts else csr_matrix(np.ones((len(df), 1)))
    m = (LogisticRegression(max_iter=2000, solver="liblinear") if model == "logistic"
         else lgb.LGBMClassifier(n_estimators=300, verbose=-1, random_state=17))
    m.fit(X, df["is_yc"].values)
    return m.predict_proba(X)[:, 1]


def psm_match(df, k=5, caliper_mult=0.2):
    treat = df[df.is_yc == 1].copy()
    ctrl = df[df.is_yc == 0].copy()
    if len(treat) == 0 or len(ctrl) == 0:
        return treat, ctrl, 0
    nn = NearestNeighbors(n_neighbors=k).fit(ctrl[["ps"]].values)
    dist, idx = nn.kneighbors(treat[["ps"]].values)
    caliper = caliper_mult * df["ps"].std()
    keep = dist[:, 0] <= caliper
    n_dropped = int((~keep).sum())
    return treat[keep].copy(), ctrl.iloc[idx[keep].flatten()].copy(), n_dropped


# =================== RV01 ===================
def rv01_real_ecosystem(panel_e: pd.DataFrame):
    print("\n[RV01] Real ecosystem covariates (Bay/NYC/Boston, state-year density, VIX)")
    COV = {
        "M2_size":   ["filing_year","filing_quarter","industrygrouptype",
                      "stateorcountry","log_offering_amount"],
        "M3_real":   ["filing_year","filing_quarter","industrygrouptype",
                      "stateorcountry","log_offering_amount",
                      "is_sf_bay","is_nyc","is_boston","log_state_year_density"],
        "M4_real":   ["filing_year","filing_quarter","industrygrouptype",
                      "stateorcountry","log_offering_amount",
                      "is_sf_bay","is_nyc","is_boston","log_state_year_density","vix"],
    }
    out = {}
    for name, covs in COV.items():
        d = panel_e.copy()
        d["ps"] = fit_ps(d, covs)
        td, cd, ndrop = psm_match(d, k=5)
        rd, lo, hi = risk_diff_with_ci(td["follow_on_raise_within_5y"].values,
                                       cd["follow_on_raise_within_5y"].values,
                                       n_boot=3000, seed=17)
        print(f"  {name:10s}: ATT={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={len(td)}  "
              f"caliper_drops={ndrop}")
        append_result(ExperimentResult(
            exp_id=f"RV01-{name}",
            description=f"RV01 real ecosystem covariate set {name}",
            n_treated=len(td), n_control=len(cd),
            rate_treated=float(td["follow_on_raise_within_5y"].mean()),
            rate_control=float(cd["follow_on_raise_within_5y"].mean()),
            risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
            status="REVIEW",
        ))
        out[name] = rd
    delta = abs(out["M3_real"] - out["M2_size"])
    verdict = "PASS" if delta < 0.01 else "FAIL"
    print(f"  |M3_real − M2| = {delta:.4f}  →  reviewer criterion <0.01 → {verdict}")


# =================== RV02 ===================
def rv02_fuzzy_match(panel_e, all_fd_seed):
    print("\n[RV02] Fuzzy-match expanded treated sample")
    yc = load_yc_companies(HERE / "data/yc_companies_raw.json")
    yc_cohort = yc[yc["batch_year"].between(2014, 2019)].copy()
    exact = match_yc_to_formd(yc_cohort, all_fd_seed, strategy="exact")
    fuzzy = fuzzy_match_yc(yc_cohort, all_fd_seed, exact)
    combined = pd.concat([exact, fuzzy], ignore_index=True)
    combined = combined.drop_duplicates(subset="yc_id", keep="first")

    # Build expanded panel: merge combined with control pool from original panel
    ctrl_rows = panel_e[panel_e.is_yc == 0].copy()
    comb = combined.copy()
    comb["is_yc"] = 1
    comb["entityname"] = comb["name"]

    # Get seed Form D for all combined anchors with ecosystem covariates
    # Re-join via filing_date from seed
    seed_lookup = all_fd_seed[["accessionnumber", "yearofinc_value_entered", "entitytype"]].drop_duplicates("accessionnumber")
    comb = comb.merge(seed_lookup, on="accessionnumber", how="left")
    comb["totalofferingamount_num"] = pd.to_numeric(comb["totalofferingamount"], errors="coerce")
    comb["log_offering_amount"] = np.log1p(comb["totalofferingamount_num"].fillna(0))
    comb["entitytype"] = comb["entitytype"].fillna("Unknown")
    comb["stateorcountry"] = comb["stateorcountry"].fillna("UNK")
    comb["filing_date"] = pd.to_datetime(comb["filing_date"])
    comb["filing_year"] = comb["filing_date"].dt.year.astype(int)
    comb["filing_quarter"] = comb["filing_date"].dt.quarter.astype(int)

    # Recompute outcomes with full Form D
    print("  recomputing outcomes for expanded treated set...")
    all_fd_full = pd.concat([load_formd_quarter(z)[0].merge(load_formd_quarter(z)[2],
                            on="accessionnumber") for z in sorted(glob.glob(str(HERE / "data/sec_formd/*.zip")))],
                           ignore_index=True)
    # simpler: reuse existing follow_on computation
    from build_panel import build_all_formd
    all_fd = build_all_formd()
    comb = comb.reset_index(drop=True)
    comb["follow_on_raise_within_5y"] = outcome_follow_on(all_fd, comb, months=60)

    # Add ecosystem to combined
    comb = augment_panel_with_ecosystem(comb, all_fd_seed)

    # Build combined panel with controls (rebuild only the is_yc=1 rows)
    ctrl_rows = panel_e[panel_e.is_yc == 0].copy()
    panel_fuzzy = pd.concat([comb, ctrl_rows], ignore_index=True, sort=False)

    n_t = len(comb)
    match_rate = 100 * n_t / len(yc_cohort)
    print(f"  expanded treated n={n_t}  match_rate={match_rate:.1f}%  "
          f"(exact={len(exact)}, fuzzy={len(fuzzy)})")

    covs = ["filing_year","filing_quarter","industrygrouptype","stateorcountry",
            "log_offering_amount","is_sf_bay","is_nyc","is_boston",
            "log_state_year_density","vix"]
    panel_fuzzy["ps"] = fit_ps(panel_fuzzy, covs)
    td, cd, ndrop = psm_match(panel_fuzzy, k=5)
    rd, lo, hi = risk_diff_with_ci(td["follow_on_raise_within_5y"].values,
                                   cd["follow_on_raise_within_5y"].values,
                                   n_boot=3000, seed=17)
    print(f"  ATT(fuzzy, M3_real)= {rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={len(td)}")
    append_result(ExperimentResult(
        exp_id="RV02",
        description=f"Fuzzy-expanded treated (n={n_t}, match_rate={match_rate:.1f}%); PSM on M3_real",
        n_treated=len(td), n_control=len(cd),
        rate_treated=float(td["follow_on_raise_within_5y"].mean()),
        rate_control=float(cd["follow_on_raise_within_5y"].mean()),
        risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
        status="REVIEW",
    ))


# =================== RV03 ===================
def rv03_censoring(panel_e):
    print("\n[RV03] Censoring-corrected (drop anchors whose outcome window extends past 2024-12-31)")
    MAX_OBS = pd.Timestamp("2024-12-31")
    for H in (24, 36, 60, 84):
        p = panel_e.copy()
        p["filing_date"] = pd.to_datetime(p["filing_date"])
        eligible = p[p["filing_date"] + pd.DateOffset(months=H) <= MAX_OBS].copy()
        dropped_frac = 1 - len(eligible) / len(p)
        if eligible.is_yc.sum() < 10:
            print(f"  T+{H//12}y: insufficient treated after drop"); continue
        covs = ["filing_year","filing_quarter","industrygrouptype","stateorcountry",
                "log_offering_amount","is_sf_bay","is_nyc","is_boston",
                "log_state_year_density","vix"]
        eligible["ps"] = fit_ps(eligible, covs)
        td, cd, _ = psm_match(eligible, k=5)
        # recompute outcome flag for this horizon
        from build_panel import build_all_formd
        all_fd = build_all_formd()
        td = td.reset_index(drop=True); cd = cd.reset_index(drop=True)
        td[f"y_{H}"] = outcome_follow_on(all_fd, td, months=H)
        cd[f"y_{H}"] = outcome_follow_on(all_fd, cd, months=H)
        rd, lo, hi = risk_diff_with_ci(td[f"y_{H}"].values, cd[f"y_{H}"].values,
                                        n_boot=2000, seed=17)
        print(f"  T+{H//12}y: dropped {dropped_frac:.1%} of anchors  ATT={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={len(td)}")
        append_result(ExperimentResult(
            exp_id=f"RV03-T{H//12}y",
            description=f"Censoring-corrected T+{H//12}y ({dropped_frac:.0%} anchors dropped)",
            n_treated=len(td), n_control=len(cd),
            rate_treated=float(td[f"y_{H}"].mean()),
            rate_control=float(cd[f"y_{H}"].mean()),
            risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
            status="REVIEW",
        ))


# =================== RV04 ===================
def rv04_correct_permutation(panel_e, n_perm=500):
    print(f"\n[RV04] Within-stratum permutation (re-matching each perm, {n_perm} perms)")
    covs = ["filing_year","filing_quarter","industrygrouptype","stateorcountry",
            "log_offering_amount","is_sf_bay","is_nyc","is_boston",
            "log_state_year_density","vix"]
    d = panel_e.copy()
    d["ps"] = fit_ps(d, covs)
    td, cd, _ = psm_match(d, k=5)
    observed = (td["follow_on_raise_within_5y"].mean()
                - cd["follow_on_raise_within_5y"].mean())

    rng = np.random.default_rng(17)
    strata = d.groupby(["industrygrouptype", "filing_year"]).indices
    stratum_treat_counts = d.groupby(["industrygrouptype", "filing_year"])["is_yc"].sum()

    perm_stats = np.empty(n_perm)
    for b in range(n_perm):
        fake_treat = np.zeros(len(d), dtype=int)
        # within each stratum, pick #treated_in_stratum indices at random
        for (sec, yr), indices in strata.items():
            n_t_s = int(stratum_treat_counts.get((sec, yr), 0))
            if n_t_s == 0:
                continue
            pick = rng.choice(indices, size=n_t_s, replace=False)
            fake_treat[pick] = 1
        db = d.copy()
        db["is_yc"] = fake_treat
        db["ps"] = fit_ps(db, covs)
        ptd, pcd, _ = psm_match(db, k=5)
        if len(ptd) and len(pcd):
            perm_stats[b] = (ptd["follow_on_raise_within_5y"].mean()
                             - pcd["follow_on_raise_within_5y"].mean())
        else:
            perm_stats[b] = np.nan
    perm_stats = perm_stats[~np.isnan(perm_stats)]
    p_val = float((np.abs(perm_stats) >= abs(observed)).mean())
    print(f"  observed={observed:+.4f}  perm p-value={p_val:.4f}  (n_perm={len(perm_stats)})")
    append_result(ExperimentResult(
        exp_id="RV04",
        description=f"Within-stratum permutation test ({n_perm} perms)",
        n_treated=len(td), n_control=len(cd),
        rate_treated=float(td["follow_on_raise_within_5y"].mean()),
        rate_control=float(cd["follow_on_raise_within_5y"].mean()),
        risk_diff=observed,
        rd_ci_lo=float(np.percentile(perm_stats, 2.5)),
        rd_ci_hi=float(np.percentile(perm_stats, 97.5)),
        status="REVIEW",
    ))


# =================== RV05 ===================
def rv05_balance(panel_e):
    print("\n[RV05] Balance diagnostics (SMD pre/post, overlap)")
    covs_num = ["log_offering_amount","log_state_year_density","vix",
                "is_sf_bay","is_nyc","is_boston","filing_year"]
    covs_all = ["filing_year","filing_quarter","industrygrouptype","stateorcountry",
                "log_offering_amount","is_sf_bay","is_nyc","is_boston",
                "log_state_year_density","vix"]
    d = panel_e.copy()
    d["ps"] = fit_ps(d, covs_all)
    td, cd, ndrop = psm_match(d, k=5)

    def smd(a, b):
        s = np.sqrt((a.var() + b.var()) / 2)
        return (a.mean() - b.mean()) / s if s > 0 else np.nan

    raw_t = d[d.is_yc == 1]
    raw_c = d[d.is_yc == 0]
    rows = []
    for col in covs_num:
        rows.append({
            "covariate": col,
            "smd_raw": smd(raw_t[col].values, raw_c[col].values),
            "smd_matched": smd(td[col].values, cd[col].values),
        })
    bal = pd.DataFrame(rows)
    bal["smd_raw_abs"] = bal["smd_raw"].abs()
    bal["smd_matched_abs"] = bal["smd_matched"].abs()
    print(bal.to_string(index=False))

    # common-support fraction
    ps_c_min, ps_c_max = d[d.is_yc == 0]["ps"].min(), d[d.is_yc == 0]["ps"].max()
    on_support = d[d.is_yc == 1]["ps"].between(ps_c_min, ps_c_max).mean()
    print(f"  caliper drops: {ndrop}   "
          f"% treated on common support: {100 * on_support:.1f}%")
    max_post = bal["smd_matched_abs"].max()
    print(f"  max post-match |SMD|: {max_post:.3f}  (reviewer threshold 0.25)")

    bal.to_csv(HERE / "data" / "balance_rv05.csv", index=False)
    append_result(ExperimentResult(
        exp_id="RV05",
        description=f"Balance: max |SMD| post-match {max_post:.3f}; common support {on_support:.1%}; drops {ndrop}",
        n_treated=len(td), n_control=len(cd),
        rate_treated=float(td["follow_on_raise_within_5y"].mean()),
        rate_control=float(cd["follow_on_raise_within_5y"].mean()),
        risk_diff=float(max_post), rd_ci_lo=float(on_support), rd_ci_hi=float(ndrop),
        status="REVIEW",
    ))


# =================== RV07 ===================
def rv07_cox(panel_e):
    print("\n[RV07] Cox survival time-to-next-raise")
    from build_panel import build_all_formd
    all_fd = build_all_formd()
    # compute time to next non-amendment D per row; censor at 2024-12-31
    fd = all_fd[all_fd["submissiontype"].str.upper().str.startswith("D")
                & ~all_fd["submissiontype"].str.upper().str.startswith("D/A")].copy()
    fd["filing_date"] = pd.to_datetime(fd["filing_date"], errors="coerce")
    by_cik = {c: g[["filing_date", "accessionnumber"]].sort_values("filing_date")
              for c, g in fd.groupby("cik")}
    MAX_OBS = pd.Timestamp("2024-12-31")
    panel_e["filing_date"] = pd.to_datetime(panel_e["filing_date"])
    dur = np.empty(len(panel_e), dtype=float)
    evt = np.empty(len(panel_e), dtype=int)
    for i, r in enumerate(panel_e.itertuples(index=False)):
        g = by_cik.get(str(r.cik))
        if g is None:
            dur[i] = (MAX_OBS - r.filing_date).days
            evt[i] = 0
            continue
        lo = r.filing_date + pd.Timedelta(days=90)
        later = g[(g["filing_date"] >= lo) & (g["accessionnumber"] != r.accessionnumber)]
        if later.empty:
            dur[i] = (MAX_OBS - r.filing_date).days
            evt[i] = 0
        else:
            dur[i] = (later["filing_date"].iloc[0] - r.filing_date).days
            evt[i] = 1
    d = panel_e.copy()
    d["duration"] = dur
    d["event"] = evt

    # Build design matrix: is_yc + is_sf_bay + is_nyc + is_boston + log_offering + log_state_year_density + vix + filing_year dummies + sector dummies (top-10 to keep dims manageable)
    keep = d[d["duration"] > 0].copy()
    top_secs = keep["industrygrouptype"].value_counts().head(10).index.tolist()
    for s in top_secs:
        keep[f"sec_{s[:15].replace(' ','_')}"] = (keep["industrygrouptype"] == s).astype(int)
    feats = (["is_yc","is_sf_bay","is_nyc","is_boston","log_offering_amount",
              "log_state_year_density","vix"]
             + [f"sec_{s[:15].replace(' ','_')}" for s in top_secs])
    feats = [f for f in feats if f in keep.columns]

    cph = CoxPHFitter(penalizer=0.01)
    cph.fit(keep[feats + ["duration", "event"]], duration_col="duration", event_col="event")
    hr = float(np.exp(cph.params_["is_yc"]))
    ci = cph.confidence_intervals_.loc["is_yc"]
    hr_lo, hr_hi = float(np.exp(ci.iloc[0])), float(np.exp(ci.iloc[1]))
    p_val = float(cph.summary.loc["is_yc", "p"])
    print(f"  HR(is_yc) = {hr:.3f}  95% CI [{hr_lo:.3f}, {hr_hi:.3f}]  p={p_val:.4f}")
    append_result(ExperimentResult(
        exp_id="RV07",
        description=f"Cox PH hazard ratio is_yc on time-to-next-raise (censored 2024-12-31)",
        n_treated=int(keep["is_yc"].sum()), n_control=int((keep["is_yc"] == 0).sum()),
        rate_treated=float(hr),           # overloaded: HR point
        rate_control=float(p_val),        # overloaded: p-value
        risk_diff=float(hr), rd_ci_lo=float(hr_lo), rd_ci_hi=float(hr_hi),
        status="REVIEW",
    ))


def main():
    print("Loading panel + seed-stage Form D...", flush=True)
    panel = pd.read_parquet(HERE / "data" / "panel.parquet")
    panel["filing_date"] = pd.to_datetime(panel["filing_date"])
    panel["filing_year"] = panel["filing_date"].dt.year.astype(int)
    panel["filing_quarter"] = panel["filing_date"].dt.quarter.astype(int)
    panel["entitytype"] = panel["entitytype"].fillna("Unknown")
    panel["stateorcountry"] = panel["stateorcountry"].fillna("UNK")
    panel = panel.dropna(subset=["log_offering_amount", "industrygrouptype"]).copy()

    # load seed for ecosystem + fuzzy
    parts = []
    for z in sorted(glob.glob(str(HERE / "data/sec_formd/*.zip"))):
        sub, iss, off = load_formd_quarter(z)
        parts.append(join_formd_tables(sub, iss, off))
    all_fd = pd.concat(parts, ignore_index=True)
    all_fd["filing_date"] = pd.to_datetime(all_fd["filing_date"], errors="coerce")
    seed = filter_seed_stage(all_fd)

    panel_e = augment_panel_with_ecosystem(panel, seed)
    print(f"panel augmented: {len(panel_e):,} rows  treated={int(panel_e.is_yc.sum())}")

    rv01_real_ecosystem(panel_e)
    rv03_censoring(panel_e)
    rv05_balance(panel_e)
    rv04_correct_permutation(panel_e, n_perm=300)
    rv07_cox(panel_e)
    rv02_fuzzy_match(panel_e, seed)

    print("\nPhase 2.75 mandatory follow-ups complete (RV01-05, RV07). RV06 deferred.")


if __name__ == "__main__":
    main()
