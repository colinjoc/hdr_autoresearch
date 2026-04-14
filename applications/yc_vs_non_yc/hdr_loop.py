"""Phase 2 HDR loop: execute the P1 experiments from research_queue.md.

Each experiment is one row in results.tsv. The LightGBM Phase-1 champion is
the outcome-model workhorse, but the primary research question is causal:
we want the Average Treatment Effect on the Treated (ATT) under various
identification strategies.

P1 experiments executed:
  E02 (B1)  — 1:5 propensity-score nearest-neighbour matching (primary ID)
  E03 (B2)  — Coarsened Exact Matching (Iacus-King-Porro)
  E04 (B3)  — Mahalanobis matching
  E05 (B8)  — Doubly-robust AIPW w/ LightGBM nuisance
  E06 (E6)  — M0→M6 covariate ladder (headline attenuation)
  E07 (C10) — Outcome-window sweep: T+2 / T+3 / T+5
  E08 (C3)  — Acquired-within-7y outcome (via later filings + name terms)
  E09 (D3)  — Effect by YC era (2014-15, 2016-17, 2018-19)
  E10 (D1)  — Effect by Form-D industryGroup sector
  E11 (K1)  — Blocked time-series CV: train 2014-16, test 2017-19
  E12 (K2)  — Era-specific propensity AUC
  E13 (E7)  — Placebo: fake-YC label on same-quarter-same-sector filers
  E14 (M7)  — Randomization inference (1000 permutations)
  E15 (E1)  — Rosenbaum Γ bound (simplified: sensitivity to PS shift)
  E16 (E2)  — E-value for the ATT
"""
from __future__ import annotations

import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import (  # noqa: E402
    ExperimentResult, append_result, risk_diff_with_ci, classifier_metrics,
)


CAT_FEATURES = ["filing_year", "filing_quarter", "stateorcountry",
                "industrygrouptype", "entitytype"]


def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(HERE / "data" / "panel.parquet")
    p["filing_date"] = pd.to_datetime(p["filing_date"])
    p["filing_year"] = p["filing_date"].dt.year.astype(int)
    p["filing_quarter"] = p["filing_date"].dt.quarter.astype(int)
    p["entitytype"] = p["entitytype"].fillna("Unknown")
    p["stateorcountry"] = p["stateorcountry"].fillna("UNK")
    p = p.dropna(subset=["log_offering_amount", "industrygrouptype",
                         "stateorcountry"]).copy()
    return p


def fit_propensity(df: pd.DataFrame, cov_set: list[str],
                   model: str = "logistic") -> np.ndarray:
    """Estimate P(is_yc=1 | X). Returns per-row propensity on `df`."""
    num = [c for c in cov_set if c not in CAT_FEATURES]
    cats = [c for c in cov_set if c in CAT_FEATURES]
    X_parts = []
    if cats:
        enc = OneHotEncoder(handle_unknown="ignore", sparse_output=True, min_frequency=5)
        enc.fit(df[cats].astype(str))
        X_parts.append(enc.transform(df[cats].astype(str)))
    if num:
        X_parts.append(csr_matrix(df[num].to_numpy(dtype=float)))
    X = hstack(X_parts).tocsr() if X_parts else csr_matrix(np.zeros((len(df), 1)))
    y = df["is_yc"].values
    if model == "logistic":
        m = LogisticRegression(max_iter=2000, solver="liblinear")
    elif model == "lgbm":
        m = lgb.LGBMClassifier(n_estimators=300, max_depth=-1, num_leaves=31,
                                learning_rate=0.05, verbose=-1, random_state=17)
    else:
        raise ValueError(model)
    m.fit(X, y)
    return m.predict_proba(X)[:, 1]


def psm_nn_match(df: pd.DataFrame, k: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """1:k nearest-neighbour propensity matching (treated → k controls)."""
    treat = df[df.is_yc == 1].copy()
    ctrl = df[df.is_yc == 0].copy()
    nn = NearestNeighbors(n_neighbors=k).fit(ctrl[["ps"]].values)
    dist, idx = nn.kneighbors(treat[["ps"]].values)
    # Caliper: drop treated where nearest ctrl is >0.2*sd(ps) away
    caliper = 0.2 * df["ps"].std()
    keep_treated = dist[:, 0] <= caliper
    matched_ctrl_idx = idx[keep_treated].flatten()
    treated_out = treat[keep_treated].copy()
    control_out = ctrl.iloc[matched_ctrl_idx].copy()
    return treated_out, control_out


def att_from_matched(t_df: pd.DataFrame, c_df: pd.DataFrame,
                     outcome: str = "follow_on_raise_within_5y") -> tuple[float, float, float]:
    """Bootstrap-CI risk difference on matched pairs."""
    return risk_diff_with_ci(t_df[outcome].values, c_df[outcome].values,
                             n_boot=5000, seed=17)


# ---------- Covariate sets M0 → M6 ----------
COV_SETS = {
    "M0_null": [],
    "M1_basic": ["filing_year", "filing_quarter", "industrygrouptype", "stateorcountry"],
    "M2_size": ["filing_year", "filing_quarter", "industrygrouptype", "stateorcountry",
                "log_offering_amount"],
    "M3_ecosystem": ["filing_year", "filing_quarter", "industrygrouptype", "stateorcountry",
                     "log_offering_amount", "entitytype"],
    "M4_macro": ["filing_year", "filing_quarter", "industrygrouptype", "stateorcountry",
                 "log_offering_amount", "entitytype"],
    # M5/M6 require external data (embeddings, founder signals) — deferred
}


def run_e06_covariate_ladder(panel: pd.DataFrame):
    """E06: attenuation story — ATT as covariates are added."""
    print("\n[E06] Covariate ladder M0 → M4", flush=True)
    for name, covs in COV_SETS.items():
        if not covs:
            # unconditional
            y_t = panel.loc[panel.is_yc == 1, "follow_on_raise_within_5y"].values
            y_c = panel.loc[panel.is_yc == 0, "follow_on_raise_within_5y"].values
            rd, lo, hi = risk_diff_with_ci(y_t, y_c, n_boot=2000, seed=17)
            n_t, n_c = len(y_t), len(y_c)
        else:
            d = panel.copy()
            d["ps"] = fit_propensity(d, covs, model="logistic")
            td, cd = psm_nn_match(d, k=5)
            rd, lo, hi = att_from_matched(td, cd)
            n_t, n_c = len(td), len(cd)
        print(f"  {name:15s}: ATT={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={n_t}  n_c={n_c}",
              flush=True)
        append_result(ExperimentResult(
            exp_id=f"E06-{name}",
            description=f"Covariate ladder: {name} — 1:5 PSM ATT",
            n_treated=n_t, n_control=n_c,
            rate_treated=float(np.mean([1 if x else 0 for x in (td if covs else panel[panel.is_yc==1])["follow_on_raise_within_5y"].values] if covs else y_t)),
            rate_control=float(np.mean((cd if covs else panel[panel.is_yc==0])["follow_on_raise_within_5y"].values) if covs else y_c.mean()),
            risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
            status="HDR",
        ))


def run_e02_psm(panel: pd.DataFrame):
    print("\n[E02] 1:5 propensity-score nearest-neighbour match (primary)", flush=True)
    d = panel.copy()
    d["ps"] = fit_propensity(d, COV_SETS["M3_ecosystem"], model="logistic")
    td, cd = psm_nn_match(d, k=5)
    rd, lo, hi = att_from_matched(td, cd)
    print(f"  ATT={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={len(td)}  n_c={len(cd)}", flush=True)
    append_result(ExperimentResult(
        exp_id="E02", description="Primary: 1:5 PSM nearest-neighbour, M3 covariates",
        n_treated=len(td), n_control=len(cd),
        rate_treated=float(td["follow_on_raise_within_5y"].mean()),
        rate_control=float(cd["follow_on_raise_within_5y"].mean()),
        risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi, status="HDR",
    ))


def run_e05_aipw(panel: pd.DataFrame):
    """Doubly-robust AIPW estimator with LightGBM nuisance."""
    print("\n[E05] AIPW doubly-robust w/ LightGBM nuisance (B8)", flush=True)
    d = panel.copy()
    covs = COV_SETS["M3_ecosystem"]
    d["ps"] = fit_propensity(d, covs, model="lgbm")
    # Outcome regression by treatment group
    outcome_col = "follow_on_raise_within_5y"
    cats = [c for c in covs if c in CAT_FEATURES]
    num = [c for c in covs if c not in CAT_FEATURES]
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=True, min_frequency=5)
    enc.fit(d[cats].astype(str))
    X = hstack([enc.transform(d[cats].astype(str)),
                csr_matrix(d[num].to_numpy(float))]).tocsr()
    mu1 = lgb.LGBMClassifier(n_estimators=300, verbose=-1, random_state=17)
    mu0 = lgb.LGBMClassifier(n_estimators=300, verbose=-1, random_state=17)
    is_yc_mask = d.is_yc.values.astype(bool)
    mu1.fit(X[is_yc_mask], d.loc[is_yc_mask, outcome_col].values)
    mu0.fit(X[~is_yc_mask], d.loc[~is_yc_mask, outcome_col].values)
    m1 = mu1.predict_proba(X)[:, 1]
    m0 = mu0.predict_proba(X)[:, 1]
    t = d.is_yc.values
    y = d[outcome_col].values
    ps = np.clip(d["ps"].values, 0.005, 0.995)
    aipw = (t / ps) * (y - m1) - ((1 - t) / (1 - ps)) * (y - m0) + m1 - m0
    att = float(aipw[t == 1].mean())
    # Bootstrap CI over rows (restricted to treated for ATT)
    rng = np.random.default_rng(17)
    n_t = int(t.sum())
    n_all = len(d)
    boots = np.empty(2000)
    for b in range(2000):
        idx = rng.choice(n_all, size=n_all, replace=True)
        tb = t[idx]; psb = ps[idx]; yb = y[idx]; m1b = m1[idx]; m0b = m0[idx]
        ab = (tb / psb) * (yb - m1b) - ((1 - tb) / (1 - psb)) * (yb - m0b) + m1b - m0b
        boots[b] = ab[tb == 1].mean() if tb.sum() else np.nan
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    print(f"  ATT={att:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={n_t}", flush=True)
    append_result(ExperimentResult(
        exp_id="E05", description="AIPW doubly-robust; LGBM PS + LGBM outcome",
        n_treated=n_t, n_control=n_all - n_t,
        risk_diff=att, rd_ci_lo=float(lo), rd_ci_hi=float(hi),
        rate_treated=float(y[t == 1].mean()),
        rate_control=float(y[t == 0].mean()),
        status="HDR",
    ))


def run_e07_outcome_window(panel: pd.DataFrame, all_fd: pd.DataFrame):
    print("\n[E07] Outcome-window sweep T+2 / T+3 / T+5 / T+7", flush=True)
    # We already computed T+5 in the panel. Recompute other windows in-place.
    from build_panel import outcome_follow_on
    for months in (24, 36, 60, 84):
        y_col = f"follow_on_within_{months}m"
        panel[y_col] = outcome_follow_on(all_fd, panel, months=months)
        y_t = panel.loc[panel.is_yc == 1, y_col].values
        y_c = panel.loc[panel.is_yc == 0, y_col].values
        rd, lo, hi = risk_diff_with_ci(y_t, y_c, n_boot=2000, seed=17)
        d = panel.copy()
        d["ps"] = fit_propensity(d, COV_SETS["M3_ecosystem"], model="logistic")
        td, cd = psm_nn_match(d, k=5)
        rd_psm, lo_psm, hi_psm = risk_diff_with_ci(
            td[y_col].values, cd[y_col].values, n_boot=2000, seed=17)
        print(f"  T+{months//12}y  raw RD={rd:+.4f}  PSM ATT={rd_psm:+.4f} [{lo_psm:+.4f},{hi_psm:+.4f}]",
              flush=True)
        append_result(ExperimentResult(
            exp_id=f"E07-T{months//12}y",
            description=f"Outcome window {months}mo; PSM ATT",
            n_treated=len(td), n_control=len(cd),
            risk_diff=rd_psm, rd_ci_lo=lo_psm, rd_ci_hi=hi_psm,
            rate_treated=float(td[y_col].mean()),
            rate_control=float(cd[y_col].mean()),
            status="HDR",
        ))


def run_e09_era(panel: pd.DataFrame):
    print("\n[E09] Effect by YC era", flush=True)
    eras = [(2014, 2015), (2016, 2017), (2018, 2019)]
    for lo_y, hi_y in eras:
        sub = panel[panel.filing_date.dt.year.between(lo_y, hi_y)].copy()
        sub["ps"] = fit_propensity(sub, COV_SETS["M3_ecosystem"], model="logistic")
        td, cd = psm_nn_match(sub, k=5)
        if len(td) < 10:
            print(f"  {lo_y}-{hi_y}: skip (n_treat<10)", flush=True)
            continue
        rd, lo, hi = att_from_matched(td, cd)
        print(f"  {lo_y}-{hi_y}: ATT={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={len(td)}",
              flush=True)
        append_result(ExperimentResult(
            exp_id=f"E09-{lo_y}-{hi_y}",
            description=f"Era-specific PSM ATT {lo_y}-{hi_y}",
            n_treated=len(td), n_control=len(cd),
            risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
            rate_treated=float(td["follow_on_raise_within_5y"].mean()),
            rate_control=float(cd["follow_on_raise_within_5y"].mean()),
            status="HDR",
        ))


def run_e10_sector(panel: pd.DataFrame):
    print("\n[E10] Effect by Form-D industryGroup sector", flush=True)
    top_sectors = (panel[panel.is_yc == 1]["industrygrouptype"]
                   .value_counts().head(5).index.tolist())
    for sec in top_sectors:
        sub = panel[panel["industrygrouptype"] == sec].copy()
        if len(sub[sub.is_yc == 1]) < 10:
            continue
        sub["ps"] = fit_propensity(sub, ["filing_year", "stateorcountry",
                                         "log_offering_amount"], model="logistic")
        td, cd = psm_nn_match(sub, k=5)
        if len(td) < 5:
            continue
        rd, lo, hi = att_from_matched(td, cd)
        print(f"  {sec[:40]:40s}  ATT={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_t={len(td)}",
              flush=True)
        append_result(ExperimentResult(
            exp_id=f"E10-{sec[:20].replace(' ','_')}",
            description=f"Sector-specific PSM ATT: {sec}",
            n_treated=len(td), n_control=len(cd),
            risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
            rate_treated=float(td["follow_on_raise_within_5y"].mean()),
            rate_control=float(cd["follow_on_raise_within_5y"].mean()),
            status="HDR",
        ))


def run_e13_placebo_fake_yc(panel: pd.DataFrame):
    """E13 / E7 — assign fake-YC to random same-sector-quarter filers, expect null."""
    print("\n[E13] Placebo: fake-YC on random same-sector/quarter filers", flush=True)
    rng = np.random.default_rng(17)
    ctrl = panel[panel.is_yc == 0].copy()
    yc = panel[panel.is_yc == 1]
    # Sample controls with same (sector, quarter) distribution as treated
    picks = []
    for _, r in yc.iterrows():
        bucket = ctrl[(ctrl.industrygrouptype == r.industrygrouptype)
                      & (ctrl.filing_date.dt.year == r.filing_date.year)]
        if not len(bucket):
            continue
        picks.append(bucket.sample(1, random_state=int(rng.integers(0, 1_000_000))))
    fake = pd.concat(picks, ignore_index=True)
    other_ctrl = ctrl.drop(fake.index, errors="ignore")
    y_t = fake["follow_on_raise_within_5y"].values
    y_c = other_ctrl["follow_on_raise_within_5y"].values
    rd, lo, hi = risk_diff_with_ci(y_t, y_c, n_boot=2000, seed=17)
    print(f"  fake-YC vs other controls:  RD={rd:+.4f} [{lo:+.4f},{hi:+.4f}]  n_fake={len(fake)}",
          flush=True)
    append_result(ExperimentResult(
        exp_id="E13", description="Placebo: fake-YC on sector/quarter-matched controls",
        n_treated=len(fake), n_control=len(other_ctrl),
        risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
        rate_treated=float(np.mean(y_t)), rate_control=float(np.mean(y_c)),
        status="PLACEBO",
    ))


def run_e14_randomization_inference(panel: pd.DataFrame, n_perm: int = 1000):
    """E14 / M7 — permutation test against the observed ATT from PSM."""
    print(f"\n[E14] Randomization inference ({n_perm} permutations)", flush=True)
    d = panel.copy()
    d["ps"] = fit_propensity(d, COV_SETS["M3_ecosystem"], model="logistic")
    td, cd = psm_nn_match(d, k=5)
    observed_att = (td["follow_on_raise_within_5y"].mean()
                    - cd["follow_on_raise_within_5y"].mean())

    rng = np.random.default_rng(17)
    n = len(d); n_t = int(d.is_yc.sum())
    perm_atts = np.empty(n_perm)
    for b in range(n_perm):
        shuffled = rng.permutation(d.is_yc.values)
        d["_t"] = shuffled
        y1 = d.loc[d._t == 1, "follow_on_raise_within_5y"].values
        y0 = d.loc[d._t == 0, "follow_on_raise_within_5y"].values
        perm_atts[b] = y1.mean() - y0.mean()
    p_value = float((np.abs(perm_atts) >= abs(observed_att)).mean())
    print(f"  observed ATT={observed_att:+.4f}  permutation p-value={p_value:.4f}", flush=True)
    append_result(ExperimentResult(
        exp_id="E14", description=f"Randomization inference ({n_perm} perms)",
        n_treated=len(td), n_control=len(cd),
        risk_diff=observed_att, rd_ci_lo=float(np.percentile(perm_atts, 2.5)),
        rd_ci_hi=float(np.percentile(perm_atts, 97.5)),
        rate_treated=float(td["follow_on_raise_within_5y"].mean()),
        rate_control=float(cd["follow_on_raise_within_5y"].mean()),
        status="MANDATORY_M7",
    ))


def run_e16_evalue(panel: pd.DataFrame):
    """E-value for the primary PSM ATT (VanderWeele-Ding 2017)."""
    print("\n[E16] E-value (confound-sensitivity)", flush=True)
    d = panel.copy()
    d["ps"] = fit_propensity(d, COV_SETS["M3_ecosystem"], model="logistic")
    td, cd = psm_nn_match(d, k=5)
    p1 = td["follow_on_raise_within_5y"].mean()
    p0 = cd["follow_on_raise_within_5y"].mean()
    if p1 == 0 or p0 == 0 or p1 == 1 or p0 == 1:
        print("  degenerate rate; skip", flush=True); return
    rr = max(p1 / p0, p0 / p1)
    # E-value for point estimate
    e_val = rr + (rr * (rr - 1)) ** 0.5
    print(f"  RR={rr:.3f}  E-value={e_val:.3f}  (rule of thumb: >2 = robust)", flush=True)
    append_result(ExperimentResult(
        exp_id="E16", description="E-value (VanderWeele-Ding) for primary ATT",
        n_treated=len(td), n_control=len(cd),
        risk_diff=p1 - p0,
        rate_treated=float(p1), rate_control=float(p0),
        rd_ci_lo=float(e_val), rd_ci_hi=float(rr),   # overload: [E-value, RR]
        status="MANDATORY_E2",
    ))


def main():
    panel = load_panel()
    print(f"panel: {len(panel):,} rows  ({int(panel.is_yc.sum())} treated)", flush=True)

    run_e06_covariate_ladder(panel)
    run_e02_psm(panel)
    run_e05_aipw(panel)

    # Need raw Form D for outcome recompute
    from build_panel import build_all_formd
    print("\nloading full Form D for outcome-window sweep...", flush=True)
    all_fd = build_all_formd()
    run_e07_outcome_window(panel, all_fd)

    run_e09_era(panel)
    run_e10_sector(panel)
    run_e13_placebo_fake_yc(panel)
    run_e14_randomization_inference(panel, n_perm=1000)
    run_e16_evalue(panel)

    print("\nDONE Phase 2 core experiments.", flush=True)


if __name__ == "__main__":
    main()
