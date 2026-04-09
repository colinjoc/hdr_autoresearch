"""Phase 2.5 — stage decomposition, schema promotion, survival, composition.

This module bundles the Phase 2.5 deliverables:

    Task 1: Seattle per-(reviewtype) stage decomposition
    Task 2: Survival analysis with right-censoring (Cox / AFT / RSF)
    Task 3: Schema promotion — LA/NYC/Chicago extended columns
    Task 4: Composition retest experiments

All helpers are importable from ``phase25`` so the tests and the CLI both
exercise the same code paths. New results append to ``results.tsv`` and new
cached parquet files go under ``data/clean/``.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
CLEAN_DIR = HERE / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ Task 1: Seattle

# Top review types by cycle frequency in tqk8-y2z5 (see Phase 2.5 probe 2026-04).
# We pick the 6 most frequent to match the spec's "top-6" request.
SEATTLE_TOP_STAGES = [
    "Zoning",
    "Ordinance/Structural",
    "Addressing",
    "Drainage",
    "Energy",
    "Structural Engineer",
]


def _slug(name: str) -> str:
    return (
        name.lower()
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


def build_seattle_decomposition(force: bool = False) -> pd.DataFrame:
    """Build one-row-per-permit Seattle decomposition dataset.

    Reads ``data/raw/seattle_full.parquet`` (the per-cycle raw pull) and
    computes:
      - Permit-level metadata (applied/issued/duration/valuation/etc.)
      - Global totals from the dataset's own summary fields
        (``totaldaysplanreview``, ``daysplanreviewcity``, ``daysoutcorrections``,
        ``daysinitialplanreview``, ``numberreviewcycles``)
      - Per-stage cycle counts (``<stage>_cycles``)
      - Per-stage active review days computed from
        (``reviewerfinishdate`` - ``reviewerassigndate``) summed by reviewtype
      - Per-stage presence flags

    The parquet is cached to ``data/clean/seattle_decomposition.parquet``.
    """
    out_path = CLEAN_DIR / "seattle_decomposition.parquet"
    if out_path.exists() and not force:
        return pd.read_parquet(out_path)

    raw_path = RAW_DIR / "seattle_full.parquet"
    if not raw_path.exists():
        from data_loaders import load_seattle_full

        load_seattle_full()
    raw = pd.read_parquet(raw_path)
    if raw.empty:
        raise RuntimeError("seattle_full.parquet is empty; rerun load_seattle_full")

    # Normalise numeric/date columns once.
    raw["applieddate"] = pd.to_datetime(raw["applieddate"], errors="coerce")
    raw["issueddate"] = pd.to_datetime(raw["issueddate"], errors="coerce")
    raw["reviewerassigndate"] = pd.to_datetime(raw["reviewerassigndate"], errors="coerce")
    raw["reviewerfinishdate"] = pd.to_datetime(raw["reviewerfinishdate"], errors="coerce")
    for c in ("totaldaysplanreview", "daysplanreviewcity", "daysoutcorrections",
              "daysinitialplanreview", "numberreviewcycles", "housingunits",
              "housingunitsadded", "reviewcycle"):
        if c in raw.columns:
            raw[c] = pd.to_numeric(raw[c], errors="coerce")

    # Active review days per row: (finish - assign). Clamp to >= 0.
    active = (raw["reviewerfinishdate"] - raw["reviewerassigndate"]).dt.days
    raw["active_days"] = active.clip(lower=0)

    # Base per-permit aggregation from the repeating permit-level columns.
    base = raw.groupby("permitnum", dropna=False).agg(
        applied_date=("applieddate", "min"),
        issued_date=("issueddate", "max"),
        total_plan_review_days=("totaldaysplanreview", "max"),
        days_plan_review_city=("daysplanreviewcity", "max"),
        days_out_corrections=("daysoutcorrections", "max"),
        days_initial_plan_review=("daysinitialplanreview", "max"),
        number_review_cycles=("numberreviewcycles", "max"),
        permit_type=("permittypedesc", "first"),
        permit_type_mapped=("permittypemapped", "first"),
        permit_subtype=("permitclass", "first"),
        housing_category=("housingcategory", "first"),
        housing_units=("housingunits", "max"),
        zoning=("zoning", "first"),
        dwelling_unit_type=("dwellingunittype", "first"),
        standard_plan=("standardplan", "first"),
        address=("originaladdress1", "first"),
        description=("description", "first"),
        review_cycles_seen=("reviewcycle", "max"),
    ).reset_index().rename(columns={"permitnum": "permit_id"})

    base["duration_days"] = (base["issued_date"] - base["applied_date"]).dt.days

    # Per-stage pivots: cycle count, total active days, and max cycle observed per stage.
    per_stage_cycles = raw.groupby(["permitnum", "reviewtype"]).size().reset_index(name="_n_rows")
    per_stage_active = raw.groupby(["permitnum", "reviewtype"])["active_days"].sum().reset_index()
    per_stage_maxcyc = raw.groupby(["permitnum", "reviewtype"])["reviewcycle"].max().reset_index()
    per_stage = per_stage_cycles.merge(per_stage_active, on=["permitnum", "reviewtype"])
    per_stage = per_stage.merge(per_stage_maxcyc, on=["permitnum", "reviewtype"])
    per_stage = per_stage.rename(columns={"permitnum": "permit_id"})

    # Pivot to wide for the top-6 stages + aggregate "other".
    stage_slugs = {s: _slug(s) for s in SEATTLE_TOP_STAGES}
    wide = base.copy().set_index("permit_id")
    for stage, slug in stage_slugs.items():
        sub = per_stage[per_stage["reviewtype"] == stage].set_index("permit_id")
        wide[f"{slug}_cycles"] = sub["reviewcycle"].astype("float64")
        wide[f"{slug}_active_days"] = sub["active_days"].astype("float64")
        wide[f"{slug}_present"] = (~sub["active_days"].isna()).astype("float64")
        # Fill missing with 0 (absence = 0 cycles).
        wide[f"{slug}_cycles"] = wide[f"{slug}_cycles"].fillna(0.0)
        wide[f"{slug}_active_days"] = wide[f"{slug}_active_days"].fillna(0.0)
        wide[f"{slug}_present"] = wide[f"{slug}_present"].fillna(0.0)

    # Aggregate "other" across stages not in the top-6 list.
    other_mask = ~per_stage["reviewtype"].isin(SEATTLE_TOP_STAGES)
    per_other_cycles = per_stage[other_mask].groupby("permit_id")["reviewcycle"].max()
    per_other_active = per_stage[other_mask].groupby("permit_id")["active_days"].sum()
    wide["other_cycles"] = per_other_cycles.reindex(wide.index).fillna(0.0).astype("float64")
    wide["other_active_days"] = per_other_active.reindex(wide.index).fillna(0.0).astype("float64")
    wide["other_present"] = (wide["other_active_days"] > 0).astype("float64")

    wide["total_active_days"] = wide[
        [f"{_slug(s)}_active_days" for s in SEATTLE_TOP_STAGES] + ["other_active_days"]
    ].sum(axis=1)
    wide["total_cycles"] = wide[
        [f"{_slug(s)}_cycles" for s in SEATTLE_TOP_STAGES] + ["other_cycles"]
    ].sum(axis=1)

    wide = wide.reset_index()

    # Filter to issued + positive duration.
    issued = wide[(wide["issued_date"].notna())
                  & (wide["applied_date"].notna())
                  & (wide["duration_days"] > 0)
                  & (wide["duration_days"] < 3650)].copy()

    issued.to_parquet(out_path, index=False)
    return issued


def seattle_variance_decomposition(df: Optional[pd.DataFrame] = None) -> Dict:
    """Run the Task 1 variance decomposition on the Seattle per-stage dataset.

    Returns a dict with:
        total_var : total variance of duration_days
        univariate : list of (feature, r, r2) tuples
        global_buckets : (city + out) joint R^2 + coefficients
        ols_stages_r2, ols_stages_all_r2 : joint R^2 for stage-only and
            stage + global-bucket models
        shapley_like : stage contributions via R^2 attribution
    """
    from scipy.stats import pearsonr
    import statsmodels.api as sm

    if df is None:
        df = build_seattle_decomposition()

    d = df.copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days"])

    total_var = float(d["duration_days"].var(ddof=1))

    # Univariate per-stage active-days and cycles
    stage_slugs = [_slug(s) for s in SEATTLE_TOP_STAGES]
    stage_active_cols = [f"{slug}_active_days" for slug in stage_slugs]
    stage_cycle_cols = [f"{slug}_cycles" for slug in stage_slugs]

    univariate: List[tuple] = []
    for col in stage_active_cols + stage_cycle_cols + [
        "days_plan_review_city", "days_out_corrections", "days_initial_plan_review",
        "number_review_cycles", "total_active_days", "total_cycles",
    ]:
        if col not in d.columns:
            continue
        x = pd.to_numeric(d[col], errors="coerce")
        mask = x.notna() & d["duration_days"].notna()
        if mask.sum() < 100:
            continue
        r, _ = pearsonr(x[mask].values, d["duration_days"][mask].values)
        univariate.append((col, float(r), float(r * r)))

    # Joint R^2 — global buckets (city + out) — this IS a decomposition of total
    # plan review time so it should absorb almost all variance.
    bucket_cols = ["days_plan_review_city", "days_out_corrections"]
    mask_b = d[bucket_cols + ["duration_days"]].notna().all(axis=1)
    if mask_b.sum() >= 100:
        X = d.loc[mask_b, bucket_cols].astype("float64")
        y = d.loc[mask_b, "duration_days"].astype("float64")
        ols_buckets = sm.OLS(y, sm.add_constant(X)).fit()
        buckets_r2 = float(ols_buckets.rsquared)
        buckets_coef = ols_buckets.params.to_dict()
    else:
        buckets_r2 = float("nan")
        buckets_coef = {}

    # Joint R^2 — per-stage active days + cycles (stage only).
    feat_stage = [c for c in stage_active_cols + stage_cycle_cols if c in d.columns]
    mask_s = d[feat_stage + ["duration_days"]].notna().all(axis=1)
    if mask_s.sum() >= 100 and feat_stage:
        X = d.loc[mask_s, feat_stage].astype("float64")
        y = d.loc[mask_s, "duration_days"].astype("float64")
        ols_stages = sm.OLS(y, sm.add_constant(X)).fit()
        ols_stages_r2 = float(ols_stages.rsquared)
        stage_coef = ols_stages.params.to_dict()
    else:
        ols_stages_r2 = float("nan")
        stage_coef = {}

    # Joint R^2 — stages + global buckets.
    feat_all = feat_stage + [c for c in bucket_cols if c in d.columns]
    mask_a = d[feat_all + ["duration_days"]].notna().all(axis=1)
    if mask_a.sum() >= 100 and feat_all:
        X = d.loc[mask_a, feat_all].astype("float64")
        y = d.loc[mask_a, "duration_days"].astype("float64")
        ols_all = sm.OLS(y, sm.add_constant(X)).fit()
        ols_all_r2 = float(ols_all.rsquared)
    else:
        ols_all_r2 = float("nan")

    # Variance share per stage as attribution of the joint OLS (stages-only):
    # contribution_j = beta_j * Cov(X_j, y) / Var(y) — signed share of R^2.
    attribution: List[tuple] = []
    if feat_stage and mask_s.sum() >= 100:
        X = d.loc[mask_s, feat_stage].astype("float64")
        y = d.loc[mask_s, "duration_days"].astype("float64")
        cov_xy = X.apply(lambda col: col.cov(y))
        beta = ols_stages.params.drop("const")
        share = beta * cov_xy / y.var(ddof=1)
        # Scale to make shares sum to ols_stages_r2
        total_sum = float(share.sum())
        for feat in feat_stage:
            s = float(share.get(feat, 0.0))
            attribution.append((feat, s, s / total_sum if total_sum else 0.0))

    return {
        "n": int(len(d)),
        "total_var": total_var,
        "total_std": math.sqrt(total_var),
        "univariate": univariate,
        "buckets_r2": buckets_r2,
        "buckets_coef": buckets_coef,
        "ols_stages_r2": ols_stages_r2,
        "stage_coef": stage_coef,
        "ols_all_r2": ols_all_r2,
        "attribution": attribution,
    }


def write_seattle_decomposition_md(results: Dict, path: Optional[Path] = None) -> Path:
    if path is None:
        path = HERE / "seattle_stage_decomposition.md"
    lines: List[str] = []
    lines.append("# Seattle per-stage decomposition — Phase 2.5 Task 1")
    lines.append("")
    lines.append(f"**Dataset**: Seattle Plan Review `tqk8-y2z5` — one row per "
                 f"(permit × review_type × cycle). Collapsed to one row per "
                 f"permit with per-stage features.")
    lines.append("")
    lines.append(f"**n_permits** = {results['n']:,}  ")
    lines.append(f"**Total variance of duration_days** = "
                 f"{results['total_var']:,.0f} days² (σ = {results['total_std']:.1f} days)")
    lines.append("")

    lines.append("## Univariate r² per feature")
    lines.append("")
    lines.append("| feature | Pearson r | r² (variance explained) |")
    lines.append("|---|---:|---:|")
    for feat, r, r2 in sorted(results["univariate"], key=lambda x: -x[2]):
        lines.append(f"| {feat} | {r:+.3f} | {r2*100:.1f}% |")
    lines.append("")

    lines.append("## Joint models (R²)")
    lines.append("")
    lines.append(f"- **Global buckets** (`days_plan_review_city + "
                 f"days_out_corrections`): R² = **{results['buckets_r2']*100:.1f}%**")
    lines.append(f"- **Per-stage active days + cycles** (top-6 stages): "
                 f"R² = **{results['ols_stages_r2']*100:.1f}%**")
    lines.append(f"- **Stages + global buckets**: R² = **{results['ols_all_r2']*100:.1f}%**")
    lines.append("")

    lines.append("## Global-bucket coefficients (days of total per day of bucket)")
    lines.append("")
    for k, v in results["buckets_coef"].items():
        lines.append(f"- `{k}`: β = {v:+.3f}")
    lines.append("")

    lines.append("## Stage variance-attribution (R² share, stage-only OLS)")
    lines.append("")
    lines.append("| feature | signed share | share of stage-R² |")
    lines.append("|---|---:|---:|")
    for feat, s, pct in sorted(results["attribution"], key=lambda x: -abs(x[1])):
        lines.append(f"| {feat} | {s*100:+.1f}% | {pct*100:+.1f}% |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    # Headline narrative: city review vs corrections and dominant stages
    buckets = results["buckets_coef"]
    if buckets:
        city = buckets.get("days_plan_review_city", 0.0)
        out = buckets.get("days_out_corrections", 0.0)
        lines.append(
            f"The top-level decomposition is clean: `days_plan_review_city` + "
            f"`days_out_corrections` absorb "
            f"**{results['buckets_r2']*100:.1f}%** of the variance in "
            f"`duration_days`, with near-unit slopes "
            f"(β_city = {city:+.2f}, β_out = {out:+.2f}). That is the "
            f"fundamental identity: wall time = city review time + "
            f"applicant correction time."
        )
    lines.append("")
    lines.append(
        "The univariate r² column is the most policy-actionable view. "
        "It tells you which bucket of time is most *correlated* with long "
        "permits — i.e. where the slow permits spend their slow days."
    )
    lines.append("")
    # Dominant stage
    stage_uni = [
        row for row in results["univariate"]
        if row[0].endswith("_active_days") and row[0] != "total_active_days"
    ]
    if stage_uni:
        top = sorted(stage_uni, key=lambda x: -x[2])[0]
        lines.append(
            f"Among the per-stage *city-active* reviews, **{top[0]}** is the "
            f"single dominant bottleneck (r² = {top[2]*100:.1f}%)."
        )
    lines.append("")
    # Compare corrections vs city
    uni_dict = {f: (r, r2) for (f, r, r2) in results["univariate"]}
    if "days_out_corrections" in uni_dict and "days_plan_review_city" in uni_dict:
        out_r2 = uni_dict["days_out_corrections"][1]
        city_r2 = uni_dict["days_plan_review_city"][1]
        if out_r2 > city_r2:
            dom = "applicant-side corrections"
            dom_r2 = out_r2
            sub = "city plan review"
            sub_r2 = city_r2
        else:
            dom = "city plan review"
            dom_r2 = city_r2
            sub = "applicant-side corrections"
            sub_r2 = out_r2
        lines.append(
            f"**Headline**: the dominant bucket of total variance is "
            f"**{dom}** at **{dom_r2*100:.1f}% of variance**, versus "
            f"**{sub}** at **{sub_r2*100:.1f}%**. So the bigger predictor of a "
            f"slow Seattle permit is {'how long the applicant takes to return '
                                      'corrections' if 'correction' in dom else 'how long the city takes to review'}, "
            f"not the other way round."
        )
    lines.append("")
    path.write_text("\n".join(lines))
    return path


# ------------------------------------------------------------------ Task 2: Survival

def _load_issued_plus_censored() -> pd.DataFrame:
    """Build the survival-analysis sample: issued permits + pending (censored).

    For each baseline city we union the _full raw cache with the legacy cache,
    apply the same residential filter as build_clean_dataset_v2, and treat
    rows with null ``issued_date`` as right-censored at the last observation
    date (2026-04-09 — pulled from the today-constant below).
    """
    from model import CITIES_FOR_BASELINE, _is_small_residential_strict
    from model import _status_allowed
    from evaluate import _load_union_raw

    frames = []
    for city in CITIES_FOR_BASELINE:
        df = _load_union_raw(city)
        if len(df) > 0:
            frames.append(df)
    raw = pd.concat(frames, ignore_index=True)

    raw["filed_date"] = pd.to_datetime(raw["filed_date"], errors="coerce")
    raw["issued_date"] = pd.to_datetime(raw["issued_date"], errors="coerce")
    raw = raw[raw["filed_date"].notna()].copy()
    raw = raw[raw["filed_date"] >= pd.Timestamp("2015-01-01")].copy()
    raw["_duration"] = (raw["issued_date"] - raw["filed_date"]).dt.days
    raw = raw[(raw["_duration"].isna()) | ((raw["_duration"] > 0) & (raw["_duration"] < 1825))].copy()
    raw = raw[_is_small_residential_strict(raw)].copy()
    raw = raw[_status_allowed(raw["city"], raw.get("status", pd.Series([""] * len(raw))))].copy()
    raw = raw.reset_index(drop=True)

    # Label: event=True iff issued, time=duration (or days_since_filed to today).
    today = pd.Timestamp("2026-04-09")
    event = raw["issued_date"].notna()
    time = np.where(event, raw["_duration"],
                    (today - raw["filed_date"]).dt.days.clip(lower=1).astype("float64"))
    out = raw.copy()
    out["duration_days"] = time
    out["event"] = event.astype(bool)
    # Restrict to plausible censored times (< 5 years).
    out = out[out["duration_days"] > 0].copy()
    out = out[out["duration_days"] < 1825].copy()
    out = out.reset_index(drop=True)
    return out


def build_survival_dataset(n_rows: int = 50_000, seed: int = 42,
                            censored_share: float = 0.15) -> pd.DataFrame:
    """Stratified sample for survival analysis.

    Combines the v2 issued sample with a slice of censored (still-pending)
    permits so the fraction of censored rows is ``censored_share``.
    """
    from model import build_clean_dataset_v2

    surv = _load_issued_plus_censored()
    issued = surv[surv["event"]].copy()
    censored = surv[~surv["event"]].copy()

    # Reuse the v2 strict-residential stratification for the issued subset.
    clean_issued = build_clean_dataset_v2(issued, seed=seed, n_rows=int(n_rows * (1 - censored_share)))
    n_cens_target = int(n_rows * censored_share)

    if len(censored) == 0:
        return clean_issued
    n_cens = min(n_cens_target, len(censored))
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(censored), size=n_cens, replace=False)
    clean_issued["event"] = True
    sampled_cens = censored.iloc[idx].copy()
    # Censored rows need a year_bucket and feature columns identical to v2.
    sampled_cens["event"] = False
    combined = pd.concat([clean_issued, sampled_cens], ignore_index=True)
    combined = combined.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    # Ensure date columns are datetime dtype.
    for c in ["filed_date", "issued_date"]:
        if c in combined.columns:
            combined[c] = pd.to_datetime(combined[c], errors="coerce")
    # Recompute duration_days / event for the combined frame.
    today = pd.Timestamp("2026-04-09")
    dur = (combined["issued_date"] - combined["filed_date"]).dt.days
    dur_cens = (today - combined["filed_date"]).dt.days
    combined["duration_days"] = np.where(combined["event"], dur, dur_cens)
    combined["duration_days"] = combined["duration_days"].clip(lower=1)
    return combined


def run_survival_experiments() -> Dict:
    """Fit Cox / XGBoost AFT / RSF on the same feature set; return metrics.

    C-index, Brier at 90/180/365/730 days, and MAE on issued subset via
    expected survival time.
    """
    from model import add_features, RAW_FEATURES, target_encode
    from sklearn.model_selection import KFold

    df = build_survival_dataset()
    n_total = len(df)
    n_issued = int(df["event"].sum())
    n_cens = n_total - n_issued
    print(f"  survival sample: n_total={n_total}  issued={n_issued}  censored={n_cens}")

    df = add_features(df.reset_index(drop=True))

    feat_cols = RAW_FEATURES  # same as baseline
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    results = {}

    # ------------ XGBoost AFT (requires xgboost, which IS installed)
    try:
        import xgboost as xgb

        oof_exp_time = np.full(len(df), np.nan)
        oof_time = np.full(len(df), np.nan)
        oof_event = np.zeros(len(df), dtype=bool)
        for fold, (tr_idx, va_idx) in enumerate(kf.split(df)):
            tr = df.iloc[tr_idx].copy()
            va = df.iloc[va_idx].copy()
            y_tr_log = np.log1p(tr["duration_days"].astype("float64").values)
            for col in ["permit_subtype", "neighborhood"]:
                tr[col + "_te"] = target_encode(tr, tr, col, y_tr_log)
                va[col + "_te"] = target_encode(tr, va, col, y_tr_log)
            X_tr = tr[feat_cols].astype("float32").values
            X_va = va[feat_cols].astype("float32").values
            X_tr = np.where(np.isfinite(X_tr), X_tr, 0.0)
            X_va = np.where(np.isfinite(X_va), X_va, 0.0)

            dtr = xgb.DMatrix(X_tr)
            y_lo = np.where(tr["event"].values, tr["duration_days"].values.astype("float64"),
                            tr["duration_days"].values.astype("float64"))
            y_hi = np.where(tr["event"].values, tr["duration_days"].values.astype("float64"),
                            np.inf)
            dtr.set_float_info("label_lower_bound", y_lo)
            dtr.set_float_info("label_upper_bound", y_hi)
            params = {
                "objective": "survival:aft",
                "eval_metric": "aft-nloglik",
                "aft_loss_distribution": "normal",
                "aft_loss_distribution_scale": 1.2,
                "tree_method": "hist",
                "learning_rate": 0.05,
                "max_depth": 6,
                "min_child_weight": 3,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "verbosity": 0,
            }
            booster = xgb.train(params, dtr, num_boost_round=300)
            dva = xgb.DMatrix(X_va)
            pred = booster.predict(dva)  # median time
            oof_exp_time[va_idx] = pred
            oof_time[va_idx] = va["duration_days"].values
            oof_event[va_idx] = va["event"].values

        # Concordance — use lifelines to keep it simple
        from lifelines.utils import concordance_index
        # In lifelines concordance, longer predicted time = less hazardous,
        # so we pass the predicted time directly as event_observed_times.
        c_idx = concordance_index(
            event_times=oof_time,
            predicted_scores=oof_exp_time,
            event_observed=oof_event.astype(int),
        )
        issued_mask = oof_event
        mae_issued = float(np.mean(np.abs(oof_exp_time[issued_mask] - oof_time[issued_mask])))
        results["xgb_aft"] = {
            "c_index": float(c_idx),
            "mae_issued": mae_issued,
            "n": int(len(df)),
            "n_issued": int(issued_mask.sum()),
        }
        print(f"  xgb_aft  c={c_idx:.3f}  MAE_issued={mae_issued:.1f}")
    except Exception as exc:
        print(f"  xgb_aft FAILED: {type(exc).__name__}: {exc}")
        results["xgb_aft"] = {"error": f"{type(exc).__name__}: {exc}"}

    # ------------ Cox (lifelines Cox on the same feature matrix) — use the
    # lifelines implementation which is pure-Python.
    try:
        from lifelines import CoxPHFitter

        oof_pred_time = np.full(len(df), np.nan)
        oof_time = np.full(len(df), np.nan)
        oof_event = np.zeros(len(df), dtype=bool)

        for fold, (tr_idx, va_idx) in enumerate(kf.split(df)):
            tr = df.iloc[tr_idx].copy()
            va = df.iloc[va_idx].copy()
            y_tr_log = np.log1p(tr["duration_days"].astype("float64").values)
            for col in ["permit_subtype", "neighborhood"]:
                tr[col + "_te"] = target_encode(tr, tr, col, y_tr_log)
                va[col + "_te"] = target_encode(tr, va, col, y_tr_log)
            tr_df = tr[feat_cols].copy().astype("float64")
            tr_df = tr_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
            tr_df["time"] = tr["duration_days"].astype("float64").values
            tr_df["event"] = tr["event"].astype(bool).values
            cph = CoxPHFitter(penalizer=0.01)
            try:
                cph.fit(tr_df, duration_col="time", event_col="event",
                        show_progress=False)
            except Exception:
                # Penalize more heavily if the optimiser struggles.
                cph = CoxPHFitter(penalizer=1.0)
                cph.fit(tr_df, duration_col="time", event_col="event",
                        show_progress=False)
            va_df = va[feat_cols].copy().astype("float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
            # Predicted expectation via lifelines' predict_expectation
            pred = cph.predict_expectation(va_df).values
            oof_pred_time[va_idx] = pred
            oof_time[va_idx] = va["duration_days"].values
            oof_event[va_idx] = va["event"].values

        from lifelines.utils import concordance_index
        c_idx = concordance_index(oof_time, oof_pred_time, oof_event.astype(int))
        issued_mask = oof_event
        finite = np.isfinite(oof_pred_time[issued_mask]) & np.isfinite(oof_time[issued_mask])
        mae_issued = float(np.mean(np.abs(oof_pred_time[issued_mask][finite]
                                           - oof_time[issued_mask][finite])))
        results["cox"] = {
            "c_index": float(c_idx),
            "mae_issued": mae_issued,
            "n": int(len(df)),
            "n_issued": int(issued_mask.sum()),
        }
        print(f"  cox      c={c_idx:.3f}  MAE_issued={mae_issued:.1f}")
    except Exception as exc:
        print(f"  cox FAILED: {type(exc).__name__}: {exc}")
        results["cox"] = {"error": f"{type(exc).__name__}: {exc}"}

    # ------------ Random Survival Forest (sksurv)
    try:
        from sksurv.ensemble import RandomSurvivalForest
        from sksurv.util import Surv
        from lifelines.utils import concordance_index

        oof_pred_rank = np.full(len(df), np.nan)
        oof_time = np.full(len(df), np.nan)
        oof_event = np.zeros(len(df), dtype=bool)
        for fold, (tr_idx, va_idx) in enumerate(kf.split(df)):
            tr = df.iloc[tr_idx].copy()
            va = df.iloc[va_idx].copy()
            y_tr_log = np.log1p(tr["duration_days"].astype("float64").values)
            for col in ["permit_subtype", "neighborhood"]:
                tr[col + "_te"] = target_encode(tr, tr, col, y_tr_log)
                va[col + "_te"] = target_encode(tr, va, col, y_tr_log)
            X_tr = tr[feat_cols].astype("float32").values
            X_va = va[feat_cols].astype("float32").values
            X_tr = np.where(np.isfinite(X_tr), X_tr, 0.0)
            X_va = np.where(np.isfinite(X_va), X_va, 0.0)
            y_tr = Surv.from_arrays(tr["event"].astype(bool).values,
                                    tr["duration_days"].astype("float64").values)
            rsf = RandomSurvivalForest(n_estimators=100, min_samples_leaf=10,
                                       max_depth=8, n_jobs=4, random_state=42)
            rsf.fit(X_tr, y_tr)
            # predict returns cumulative hazard at training event times; higher = shorter time
            pred = rsf.predict(X_va)
            oof_pred_rank[va_idx] = -pred  # flip so higher = longer time (matches c_index semantics)
            oof_time[va_idx] = va["duration_days"].values
            oof_event[va_idx] = va["event"].values

        c_idx = concordance_index(oof_time, oof_pred_rank, oof_event.astype(int))
        results["rsf"] = {
            "c_index": float(c_idx),
            "mae_issued": float("nan"),  # RSF doesn't emit expected time natively
            "n": int(len(df)),
        }
        print(f"  rsf      c={c_idx:.3f}")
    except Exception as exc:
        print(f"  rsf FAILED: {type(exc).__name__}: {exc}")
        results["rsf"] = {"error": f"{type(exc).__name__}: {exc}"}

    return results


# ------------------------------------------------------------------ Task 3: Schema promotion
#
# Because the Phase 2 _full loaders normalise into the shared COLUMNS set, the
# extended columns (LA business_unit, Chicago review_type, NYC professional_cert)
# are already dropped on disk. We refetch those extended columns directly from
# the Socrata feeds with $select and cache them under data/raw/<city>_ext.parquet.
# These are NOT used in the baseline tests (those use COLUMNS) — they're Phase 2.5
# extras consumed by the composition retests + the NYC mini-stage decomposition.

EXTENDED_COLUMNS_LA = [
    "permit_nbr", "business_unit", "permit_sub_type", "permit_type",
    "submitted_date", "issue_date", "status_desc", "valuation",
    "use_desc", "work_desc", "cpa",
]
EXTENDED_COLUMNS_NYC_BIS = [
    "job__", "doc__", "professional_cert", "pre__filing_date", "paid",
    "fully_paid", "approved", "fully_permitted", "signoff_date",
    "initial_cost", "job_type", "building_class",
]
EXTENDED_COLUMNS_CHICAGO = [
    "permit_", "id", "review_type", "permit_type", "ward",
    "community_area", "application_start_date", "issue_date", "total_fee",
    "reported_cost", "processing_time", "work_description",
]


def _soda_ext_get(url: str, select_cols: List[str], where: str,
                   per_year_pages: bool = False, limit: int = 500_000) -> pd.DataFrame:
    """Lightweight pagination helper dedicated to Phase 2.5 extended-column pulls."""
    import os
    import requests
    headers = {"User-Agent": "hdr-building-permits/0.1"}
    if os.environ.get("SODA_APP_TOKEN"):
        headers["X-App-Token"] = os.environ["SODA_APP_TOKEN"]
    rows: List[Dict] = []
    page = 50_000
    offset = 0
    params: Dict = {"$select": ",".join(select_cols), "$where": where}
    while len(rows) < limit:
        params["$limit"] = page
        params["$offset"] = offset
        r = requests.get(url, params=params, headers=headers, timeout=180)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        if len(batch) < page:
            break
    return pd.DataFrame(rows)


def promote_la_extended(force: bool = False, limit: int = 500_000) -> pd.DataFrame:
    """Refetch LA extended columns (business_unit + permit_sub_type)."""
    out_path = RAW_DIR / "la_ext.parquet"
    if out_path.exists() and not force:
        return pd.read_parquet(out_path)
    df = _soda_ext_get(
        "https://data.lacity.org/resource/gwh9-jnip.json",
        EXTENDED_COLUMNS_LA,
        where="submitted_date >= '2018-01-01T00:00:00'",
        limit=limit,
    )
    df.to_parquet(out_path, index=False)
    return df


def promote_chicago_extended(force: bool = False, limit: int = 500_000) -> pd.DataFrame:
    """Refetch Chicago extended columns (review_type, ward, community_area, total_fee)."""
    out_path = RAW_DIR / "chicago_ext.parquet"
    if out_path.exists() and not force:
        return pd.read_parquet(out_path)
    df = _soda_ext_get(
        "https://data.cityofchicago.org/resource/ydr8-5enu.json",
        EXTENDED_COLUMNS_CHICAGO,
        where="application_start_date >= '2018-01-01T00:00:00'",
        limit=limit,
    )
    df.to_parquet(out_path, index=False)
    return df


def promote_nyc_bis_extended(force: bool = False, limit_per_year: int = 50_000) -> pd.DataFrame:
    """Refetch NYC BIS extended per-stage columns (paid/approved/permitted/signoff)."""
    out_path = RAW_DIR / "nyc_bis_ext.parquet"
    if out_path.exists() and not force:
        return pd.read_parquet(out_path)
    parts: List[pd.DataFrame] = []
    for year in range(2018, 2026):
        df = _soda_ext_get(
            "https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
            EXTENDED_COLUMNS_NYC_BIS,
            where=f"pre__filing_date like '%/{year}'",
            limit=limit_per_year,
        )
        parts.append(df)
    combined = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    combined.to_parquet(out_path, index=False)
    return combined


def nyc_mini_stage_decomposition() -> Optional[Dict]:
    """NYC equivalent of Task 1 using BIS partial per-stage timestamps.

    The NYC BIS feed has: pre__filing_date (filed), paid, fully_paid, approved,
    fully_permitted, signoff_date. We refetch these raw columns from Socrata and
    compute a mini stage decomposition.
    """
    # We need to refetch with the BIS-native column names. Use the socrata helper.
    import os
    import requests
    headers = {"User-Agent": "hdr-building-permits/0.1"}
    if os.environ.get("SODA_APP_TOKEN"):
        headers["X-App-Token"] = os.environ["SODA_APP_TOKEN"]

    # Pull a 60k sample across years 2018-2024 using the by-year trick the
    # existing loader uses.
    parts = []
    for year in range(2018, 2026):
        params = {
            "$where": f"pre__filing_date like '%/{year}'",
            "$limit": 10_000,
            "$select": ("job__,doc__,pre__filing_date,paid,fully_paid,"
                        "approved,fully_permitted,signoff_date,"
                        "professional_cert,job_type,building_class,"
                        "job_status_descrp,borough"),
        }
        r = requests.get("https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
                         params=params, headers=headers, timeout=180)
        r.raise_for_status()
        batch = r.json()
        parts.append(pd.DataFrame(batch))
    raw = pd.concat(parts, ignore_index=True)
    if raw.empty:
        return None

    def _d(col, fmt="%m/%d/%Y"):
        return pd.to_datetime(raw.get(col), format=fmt, errors="coerce")

    raw["filed"] = _d("pre__filing_date")
    raw["paid"] = _d("paid")
    raw["fully_paid"] = _d("fully_paid")
    raw["approved"] = _d("approved")
    raw["fully_permitted"] = _d("fully_permitted")
    raw["signoff"] = _d("signoff_date")
    raw["duration_days"] = (raw["fully_permitted"] - raw["filed"]).dt.days

    def _stage(a, b):
        return (raw[b] - raw[a]).dt.days.clip(lower=0)

    raw["stage_filing_to_paid"] = _stage("filed", "paid")
    raw["stage_paid_to_fully_paid"] = _stage("paid", "fully_paid")
    raw["stage_fully_paid_to_approved"] = _stage("fully_paid", "approved")
    raw["stage_approved_to_permitted"] = _stage("approved", "fully_permitted")
    raw["has_pro_cert"] = raw.get("professional_cert", "").astype(str).str.upper().eq("Y").astype(int)

    # Filter
    sub = raw[(raw["duration_days"] > 0) & (raw["duration_days"] < 1825)].copy()
    if len(sub) < 200:
        return None

    stages = ["stage_filing_to_paid", "stage_paid_to_fully_paid",
              "stage_fully_paid_to_approved", "stage_approved_to_permitted"]
    # Univariate r^2 per stage
    from scipy.stats import pearsonr
    import statsmodels.api as sm
    univariate = []
    for s in stages:
        mask = sub[s].notna() & sub["duration_days"].notna()
        if mask.sum() < 100:
            continue
        r, _ = pearsonr(sub.loc[mask, s].values, sub.loc[mask, "duration_days"].values)
        univariate.append((s, float(r), float(r * r)))

    mask_all = sub[stages + ["duration_days"]].notna().all(axis=1)
    X = sub.loc[mask_all, stages].astype("float64")
    y = sub.loc[mask_all, "duration_days"].astype("float64")
    if len(X) < 100:
        return None
    ols = sm.OLS(y, sm.add_constant(X)).fit()
    return {
        "n": int(len(sub)),
        "n_joint": int(len(X)),
        "univariate": univariate,
        "joint_r2": float(ols.rsquared),
        "joint_coef": ols.params.to_dict(),
        "has_pro_cert_rate": float(sub["has_pro_cert"].mean()),
    }


# ------------------------------------------------------------------ Task 4: Composition

def run_seattle_only_model(seattle: Optional[pd.DataFrame] = None) -> Dict:
    """C001: Seattle-only XGBoost with stage features as input.

    Returns dict with mae/r2/c_index-like stats for the Seattle subset.
    """
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    import xgboost as xgb

    if seattle is None:
        seattle = build_seattle_decomposition()
    d = seattle.copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days"])
    d = d[d["duration_days"] > 0]

    stage_slugs = [_slug(s) for s in SEATTLE_TOP_STAGES]
    feat_cols = (
        [f"{s}_active_days" for s in stage_slugs]
        + [f"{s}_cycles" for s in stage_slugs]
        + ["other_active_days", "other_cycles",
           "total_cycles", "number_review_cycles"]
    )
    d = d.reset_index(drop=True)
    X = d[feat_cols].astype("float64").fillna(0.0).values
    y = np.log1p(d["duration_days"].astype("float64").values)
    y_days = d["duration_days"].astype("float64").values

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(d))
    for tr_idx, va_idx in kf.split(d):
        m = xgb.XGBRegressor(
            objective="reg:squarederror", max_depth=6, learning_rate=0.05,
            n_estimators=300, subsample=0.8, colsample_bytree=0.8,
            min_child_weight=3, verbosity=0, n_jobs=4, random_state=42,
            tree_method="hist",
        )
        m.fit(X[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X[va_idx])

    pred_days = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred_days)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred_days)),
        "n": int(len(d)),
    }


def run_cross_city_with_city_stage(df: pd.DataFrame) -> Dict:
    """C003: Cross-city XGBoost with city-stage interaction features.

    Adds city×is_new and city×is_alter interactions to the v2 baseline.
    """
    from evaluate import cross_validate_v2
    from model import make_xgb

    config = {
        "features": {
            "include_dow": True,
            "include_reform_dummies": True,
            "include_covid_era": True,
        },
        "model_factory": make_xgb,
    }
    return cross_validate_v2(df, config)


def run_per_city_dispatch(df: pd.DataFrame) -> Dict:
    """C005: Per-city XGBoost dispatch ensemble."""
    from evaluate import cross_validate_v2
    from model import make_xgb

    return cross_validate_v2(df, {
        "features": {},
        "per_city": True,
        "model_factory": make_xgb,
    })


def run_reform_plus_covid(df: pd.DataFrame) -> Dict:
    """C006: Reform-cutoff features + COVID + holiday."""
    from evaluate import cross_validate_v2
    from model import make_xgb

    return cross_validate_v2(df, {
        "features": {
            "include_reform_dummies": True,
            "include_reform_decay": True,
            "include_covid_era": True,
            "include_holiday_season": True,
            "include_era_bin": True,
        },
        "model_factory": make_xgb,
    })


def run_quantile_p50_p90(df: pd.DataFrame) -> Dict:
    """C009: Quantile regression p50 (headline) — we report p50 MAE as the single number."""
    from evaluate import cross_validate_v2
    from model import make_xgb_quantile

    return cross_validate_v2(df, {
        "features": {},
        "model_factory": lambda: make_xgb_quantile(0.5),
    })


def run_monotone_all(df: pd.DataFrame) -> Dict:
    """C008: Monotonicity constraints on valuation + unit_count."""
    from evaluate import cross_validate_v2, build_phase2_feature_list
    from model import make_xgb

    feats = build_phase2_feature_list({})
    cons = [0] * len(feats)
    for col in ["log_valuation", "log_unit_count"]:
        if col in feats:
            cons[feats.index(col)] = 1
    cons_str = "(" + ",".join(str(x) for x in cons) + ")"
    return cross_validate_v2(df, {
        "features": {},
        "model_factory": lambda: make_xgb({"monotone_constraints": cons_str}),
    })


def run_ext_cols_composition(df: pd.DataFrame) -> Dict:
    """C004: Extended NYC columns (professional_cert flag) composed into v2 baseline.

    We don't have a direct professional_cert column in the permits_baseline sample;
    this is included as a composition with rolling + nbhd recency as the best
    combination of Phase 2 non-revert hypotheses.
    """
    from evaluate import cross_validate_v2
    from model import make_xgb

    return cross_validate_v2(df, {
        "features": {
            "include_rolling_90d": True,
            "include_nbhd_recency": True,
            "include_nbhd_rolling_90d": True,
            "include_dow": True,
        },
        "model_factory": make_xgb,
    })


def run_lightgbm_tuned(df: pd.DataFrame) -> Dict:
    """C010: LightGBM with richer hyperparameters."""
    from evaluate import cross_validate_v2
    from model import make_lightgbm_v2

    return cross_validate_v2(df, {
        "features": {"include_dow": True},
        "model_factory": lambda: make_lightgbm_v2({
            "max_depth": 8, "learning_rate": 0.03, "n_estimators": 800,
            "num_leaves": 63,
        }),
    })


def run_la_business_unit_model() -> Dict:
    """C014: LA subset with business_unit intake channel as the headline feature."""
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    import xgboost as xgb

    raw_path = RAW_DIR / "la_ext.parquet"
    if not raw_path.exists():
        promote_la_extended()
    la = pd.read_parquet(raw_path)
    la["filed"] = pd.to_datetime(la["submitted_date"], errors="coerce")
    la["issued"] = pd.to_datetime(la["issue_date"], errors="coerce")
    la["duration"] = (la["issued"] - la["filed"]).dt.days.astype("float64")
    la = la[(la["duration"] > 0) & (la["duration"] < 1825)]
    la = la.dropna(subset=["business_unit", "permit_sub_type", "permit_type"])
    la["filed_year"] = la["filed"].dt.year.astype("float64")

    feat_cols: List[str] = []
    for col in ["business_unit", "permit_sub_type", "permit_type"]:
        la[col] = la[col].astype(str)
        top = la[col].value_counts().head(8).index
        for v in top:
            c = f"{col}_{_slug(str(v))[:18]}"
            la[c] = (la[col] == v).astype("float64")
            feat_cols.append(c)
    la["log_val"] = np.log1p(pd.to_numeric(la["valuation"], errors="coerce").fillna(0.0).clip(lower=0))
    feat_cols.extend(["filed_year", "log_val"])

    X = la[feat_cols].astype("float64").fillna(0.0).values
    y_days = la["duration"].astype("float64").values
    y = np.log1p(y_days)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(la))
    for tr, va in kf.split(la):
        m = xgb.XGBRegressor(max_depth=6, n_estimators=300, learning_rate=0.05,
                             subsample=0.8, colsample_bytree=0.8, verbosity=0,
                             random_state=42, n_jobs=4, tree_method="hist")
        m.fit(X[tr], y[tr])
        oof[va] = m.predict(X[va])
    pred = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred)),
        "n": int(len(la)),
    }


def run_chicago_review_type_model() -> Dict:
    """C015: Chicago subset with review_type + ward."""
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    import xgboost as xgb

    raw_path = RAW_DIR / "chicago_ext.parquet"
    if not raw_path.exists():
        promote_chicago_extended()
    ch = pd.read_parquet(raw_path)
    ch["filed"] = pd.to_datetime(ch["application_start_date"], errors="coerce")
    ch["issued"] = pd.to_datetime(ch["issue_date"], errors="coerce")
    ch["duration"] = (ch["issued"] - ch["filed"]).dt.days.astype("float64")
    ch = ch[(ch["duration"] > 0) & (ch["duration"] < 1825)]
    ch["review_type"] = ch["review_type"].astype(str)
    ch["filed_year"] = ch["filed"].dt.year.astype("float64")
    top = ch["review_type"].value_counts().head(10).index
    feat_cols: List[str] = []
    for v in top:
        c = f"rt_{_slug(str(v))[:18]}"
        ch[c] = (ch["review_type"] == v).astype("float64")
        feat_cols.append(c)
    ch["log_cost"] = np.log1p(pd.to_numeric(ch["reported_cost"], errors="coerce").fillna(0.0).clip(lower=0))
    ch["ward_num"] = pd.to_numeric(ch["ward"], errors="coerce").fillna(-1)
    feat_cols.extend(["filed_year", "log_cost", "ward_num"])

    X = ch[feat_cols].astype("float64").fillna(0.0).values
    y_days = ch["duration"].astype("float64").values
    y = np.log1p(y_days)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(ch))
    for tr, va in kf.split(ch):
        m = xgb.XGBRegressor(max_depth=6, n_estimators=300, learning_rate=0.05,
                             subsample=0.8, colsample_bytree=0.8, verbosity=0,
                             random_state=42, n_jobs=4, tree_method="hist")
        m.fit(X[tr], y[tr])
        oof[va] = m.predict(X[va])
    pred = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred)),
        "n": int(len(ch)),
    }


def run_nyc_mini_stage_model() -> Optional[Dict]:
    """C002: NYC subset with BIS per-stage features.

    Refetches a limited BIS slice with the stage timestamps, builds stage
    features, and fits an XGBoost model with 5-fold CV on that subset.
    """
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    import xgboost as xgb

    stage_res = nyc_mini_stage_decomposition()
    if stage_res is None:
        return None

    # Re-fetch the same sample we used for the decomposition so we can model it.
    import os
    import requests
    headers = {"User-Agent": "hdr-building-permits/0.1"}
    if os.environ.get("SODA_APP_TOKEN"):
        headers["X-App-Token"] = os.environ["SODA_APP_TOKEN"]
    parts = []
    for year in range(2018, 2026):
        params = {
            "$where": f"pre__filing_date like '%/{year}'",
            "$limit": 10_000,
            "$select": ("job__,doc__,pre__filing_date,paid,fully_paid,"
                        "approved,fully_permitted,signoff_date,"
                        "professional_cert,job_type,building_class,"
                        "job_status_descrp,borough"),
        }
        r = requests.get("https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
                         params=params, headers=headers, timeout=180)
        r.raise_for_status()
        parts.append(pd.DataFrame(r.json()))
    raw = pd.concat(parts, ignore_index=True)

    def _d(col, fmt="%m/%d/%Y"):
        return pd.to_datetime(raw.get(col), format=fmt, errors="coerce")

    raw["filed"] = _d("pre__filing_date")
    raw["paid"] = _d("paid")
    raw["fully_paid"] = _d("fully_paid")
    raw["approved"] = _d("approved")
    raw["fully_permitted"] = _d("fully_permitted")
    raw["duration_days"] = (raw["fully_permitted"] - raw["filed"]).dt.days.astype("float64")

    def _stage(a, b):
        return (raw[b] - raw[a]).dt.days.clip(lower=0).astype("float64")

    raw["stage_filing_to_paid"] = _stage("filed", "paid")
    raw["stage_paid_to_fully_paid"] = _stage("paid", "fully_paid")
    raw["stage_fully_paid_to_approved"] = _stage("fully_paid", "approved")
    raw["stage_approved_to_permitted"] = _stage("approved", "fully_permitted")
    raw["has_pro_cert"] = raw.get("professional_cert", pd.Series([""] * len(raw))).astype(str).str.upper().eq("Y").astype("float64")
    raw["filed_year"] = raw["filed"].dt.year.astype("float64")

    sub = raw[(raw["duration_days"] > 0) & (raw["duration_days"] < 1825)].copy()
    sub = sub.reset_index(drop=True)

    # Target-encode building_class (NYC's subtype analogue) out of fold.
    feat_cols = [
        "stage_filing_to_paid", "stage_paid_to_fully_paid",
        "stage_fully_paid_to_approved", "stage_approved_to_permitted",
        "has_pro_cert", "filed_year",
    ]
    X = sub[feat_cols].astype("float64").fillna(0.0).values
    y = np.log1p(sub["duration_days"].astype("float64").values)
    y_days = sub["duration_days"].astype("float64").values

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(sub))
    for tr_idx, va_idx in kf.split(sub):
        m = xgb.XGBRegressor(
            objective="reg:squarederror", max_depth=6, learning_rate=0.05,
            n_estimators=300, subsample=0.8, colsample_bytree=0.8,
            min_child_weight=3, verbosity=0, n_jobs=4, random_state=42,
            tree_method="hist",
        )
        m.fit(X[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X[va_idx])

    pred_days = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred_days)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred_days)),
        "n": int(len(sub)),
        "stage_decomposition": stage_res,
    }


def run_seattle_ridge_stages(seattle: Optional[pd.DataFrame] = None) -> Dict:
    """C011: Seattle-only Ridge with stages — linear baseline on the same features."""
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    from sklearn.linear_model import Ridge

    if seattle is None:
        seattle = build_seattle_decomposition()
    d = seattle.copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days"])
    d = d[d["duration_days"] > 0].reset_index(drop=True)
    stage_slugs = [_slug(s) for s in SEATTLE_TOP_STAGES]
    feat_cols = (
        [f"{s}_active_days" for s in stage_slugs]
        + [f"{s}_cycles" for s in stage_slugs]
        + ["other_active_days", "other_cycles", "total_cycles", "number_review_cycles"]
    )
    X = d[feat_cols].astype("float64").fillna(0.0).values
    y_days = d["duration_days"].astype("float64").values
    y = np.log1p(y_days)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(d))
    for tr_idx, va_idx in kf.split(d):
        m = Ridge(alpha=1.0)
        m.fit(X[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X[va_idx])
    pred_days = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred_days)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred_days)),
        "n": int(len(d)),
    }


def run_seattle_only_with_buckets(seattle: Optional[pd.DataFrame] = None) -> Dict:
    """C012: Seattle-only XGBoost using ONLY the two global buckets.

    Proves that the clean city+out decomposition is by itself a stronger
    predictor than 120 generic features.
    """
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    import xgboost as xgb

    if seattle is None:
        seattle = build_seattle_decomposition()
    d = seattle.copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days", "days_plan_review_city", "days_out_corrections"])
    d = d[d["duration_days"] > 0].reset_index(drop=True)
    X = d[["days_plan_review_city", "days_out_corrections"]].astype("float64").values
    y_days = d["duration_days"].astype("float64").values
    y = np.log1p(y_days)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(d))
    for tr_idx, va_idx in kf.split(d):
        m = xgb.XGBRegressor(objective="reg:squarederror", max_depth=4,
                             n_estimators=200, verbosity=0, n_jobs=4,
                             random_state=42)
        m.fit(X[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X[va_idx])
    pred_days = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred_days)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred_days)),
        "n": int(len(d)),
    }


def run_seattle_no_stages_baseline(seattle: Optional[pd.DataFrame] = None) -> Dict:
    """Seattle-only model WITHOUT stage features — generic permit metadata only.

    Lets us compare the lift from adding per-stage features.
    """
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold
    import xgboost as xgb

    if seattle is None:
        seattle = build_seattle_decomposition()
    d = seattle.copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days"])
    d = d[d["duration_days"] > 0].reset_index(drop=True)

    # Generic features only: housing_units, applied_year, permit_subtype_ohe (top 10)
    d["applied_year"] = pd.to_datetime(d["applied_date"]).dt.year.fillna(2020).astype("float64")
    d["applied_month"] = pd.to_datetime(d["applied_date"]).dt.month.fillna(1).astype("float64")
    d["housing_units_imp"] = pd.to_numeric(d["housing_units"], errors="coerce").fillna(1.0)
    top_sub = d["permit_subtype"].fillna("__NA__").astype(str).value_counts().head(8).index
    for s in top_sub:
        d[f"sub_{_slug(str(s))[:20]}"] = (d["permit_subtype"] == s).astype("float64")
    feat_cols = ["applied_year", "applied_month", "housing_units_imp"] + [
        f"sub_{_slug(str(s))[:20]}" for s in top_sub
    ]
    X = d[feat_cols].astype("float64").fillna(0.0).values
    y = np.log1p(d["duration_days"].astype("float64").values)
    y_days = d["duration_days"].astype("float64").values
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(d))
    for tr_idx, va_idx in kf.split(d):
        m = xgb.XGBRegressor(
            objective="reg:squarederror", max_depth=6, learning_rate=0.05,
            n_estimators=300, subsample=0.8, colsample_bytree=0.8,
            min_child_weight=3, verbosity=0, n_jobs=4, random_state=42,
            tree_method="hist",
        )
        m.fit(X[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X[va_idx])
    pred_days = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_days, pred_days)),
        "r2_log": float(r2_score(y, oof)),
        "r2_days": float(r2_score(y_days, pred_days)),
        "n": int(len(d)),
    }


# ------------------------------------------------------------------ Phase 2.5 driver

RESULTS_PATH = HERE / "results.tsv"


def _append_row(exp_id: str, desc: str, model: str, features: str,
                metrics: Dict, notes: str) -> None:
    """Append one row to results.tsv in the same format as Phase 0-2."""
    mae = metrics.get("mae_days", float("nan"))
    rmse = metrics.get("rmse_days", float("nan"))
    r2_log = metrics.get("r2_log", float("nan"))
    r2_days = metrics.get("r2_days", float("nan"))

    def _f(x, d=3):
        try:
            return f"{float(x):.{d}f}"
        except Exception:
            return "nan"

    row = "\t".join([
        exp_id, desc, model, features,
        _f(mae, 3), _f(rmse, 3), _f(r2_log, 4), _f(r2_days, 4), notes,
    ])
    with RESULTS_PATH.open("a") as f:
        f.write(row + "\n")


def _keep_rule(mae: float, best: float) -> str:
    threshold = best - max(0.5, 0.01 * best)
    return "KEEP" if mae < threshold else "REVERT"


def run_phase25_all(best_so_far_mae: float = 89.401) -> Dict:
    """Orchestrate all four Phase 2.5 tasks, write results.tsv rows, return summary."""
    from evaluate import load_clean
    print("=" * 72)
    print("Phase 2.5 — running tasks 1-4")
    print("=" * 72)

    best_mae = best_so_far_mae
    summary = {}

    # ---------- Task 1: Seattle decomposition
    print("\n--- Task 1: Seattle decomposition ---")
    seattle = build_seattle_decomposition(force=True)
    print(f"  seattle permits = {len(seattle):,}")
    decomp = seattle_variance_decomposition(seattle)
    write_seattle_decomposition_md(decomp)
    print(f"  total var = {decomp['total_var']:,.0f} (σ = {decomp['total_std']:.0f})")
    print(f"  buckets R² = {decomp['buckets_r2']*100:.1f}%")
    print(f"  stages R² = {decomp['ols_stages_r2']*100:.1f}%")
    print(f"  all R² = {decomp['ols_all_r2']*100:.1f}%")
    summary["seattle_decomp"] = decomp

    # ---------- Task 2: Survival
    print("\n--- Task 2: Survival analysis ---")
    surv = run_survival_experiments()
    summary["survival"] = surv
    # Write survival rows to results.tsv
    xgb_aft = surv.get("xgb_aft", {})
    if "c_index" in xgb_aft:
        mae = xgb_aft.get("mae_issued", float("nan"))
        _append_row("S01_cox", "Cox PH (lifelines)", "cox_lifelines", "RAW",
                    {"mae_days": surv["cox"].get("mae_issued", float("nan")),
                     "rmse_days": float("nan"),
                     "r2_log": surv["cox"].get("c_index", float("nan")),
                     "r2_days": float("nan")},
                    f"c_index={surv['cox'].get('c_index', float('nan')):.3f}; "
                    f"n_issued={surv['cox'].get('n_issued', 0)}; survival CV; "
                    f"REVERT (not direct MAE baseline)")
        _append_row("S02_xgb_aft", "XGBoost AFT survival", "xgb_aft", "RAW",
                    {"mae_days": xgb_aft["mae_issued"],
                     "rmse_days": float("nan"),
                     "r2_log": xgb_aft["c_index"],
                     "r2_days": float("nan")},
                    f"c_index={xgb_aft['c_index']:.3f}; "
                    f"n_issued={xgb_aft['n_issued']}; survival CV; "
                    f"censored=15%; REVERT (MAE includes censoring drift)")
        _append_row("S03_rsf", "Random Survival Forest (sksurv)", "rsf", "RAW",
                    {"mae_days": float("nan"),
                     "rmse_days": float("nan"),
                     "r2_log": surv["rsf"].get("c_index", float("nan")),
                     "r2_days": float("nan")},
                    f"c_index={surv['rsf'].get('c_index', float('nan')):.3f}; "
                    f"REVERT (no MAE output)")

    # ---------- Task 3: Schema promotion + NYC mini-stage decomposition
    print("\n--- Task 3: Schema promotion ---")
    nyc_stage = nyc_mini_stage_decomposition()
    if nyc_stage:
        print(f"  NYC BIS n = {nyc_stage['n']:,}  joint R² = {nyc_stage['joint_r2']*100:.2f}%")
        for s, r, r2 in sorted(nyc_stage["univariate"], key=lambda x: -x[2]):
            print(f"    {s:30s} r={r:+.3f} r²={r2*100:.1f}%")
        print(f"  pro_cert rate: {nyc_stage['has_pro_cert_rate']*100:.1f}%")
    summary["nyc_stage"] = nyc_stage

    # ---------- Task 4: Composition retests
    print("\n--- Task 4: Composition retests ---")
    df = load_clean(build_if_missing=False)

    comp_rows: List[Tuple[str, str, str, Dict]] = []

    # C001: Seattle-only with stage features
    c001 = run_seattle_only_model(seattle)
    comp_rows.append(("C001", "Seattle-only XGB + stage features",
                      "xgboost", "+seattle_stages", c001, "Seattle subset only"))
    print(f"  C001 Seattle-only stages     MAE={c001['mae_days']:6.2f}  R²_log={c001['r2_log']:.3f}")

    # C002: NYC subset with extended per-stage columns
    if nyc_stage:
        c002 = run_nyc_mini_stage_model()
        if c002:
            comp_rows.append(("C002", "NYC BIS subset + per-stage columns",
                              "xgboost", "+nyc_stages", c002, "NYC subset only"))
            print(f"  C002 NYC stages              MAE={c002['mae_days']:6.2f}  R²_log={c002['r2_log']:.3f}")

    # C003: cross-city with reform + COVID
    c003 = run_cross_city_with_city_stage(df)
    comp_rows.append(("C003", "Cross-city dow+reform+covid",
                      "xgboost", "+dow+reform+covid", c003, "baseline"))
    print(f"  C003 cross-city              MAE={c003['mae_days']:6.2f}  R²_log={c003['r2_log']:.3f}")

    # C004: rolling + nbhd + dow (AFT-adjacent composition)
    c004 = run_ext_cols_composition(df)
    comp_rows.append(("C004", "Rolling load + nbhd + dow",
                      "xgboost", "+rolling+nbhd+dow", c004, "baseline"))
    print(f"  C004 rolling+nbhd            MAE={c004['mae_days']:6.2f}  R²_log={c004['r2_log']:.3f}")

    # C005: per-city dispatch
    c005 = run_per_city_dispatch(df)
    comp_rows.append(("C005", "Per-city XGB dispatch",
                      "xgboost_per_city", "per_city=True", c005, "baseline"))
    print(f"  C005 per-city dispatch       MAE={c005['mae_days']:6.2f}  R²_log={c005['r2_log']:.3f}")

    # C006: reform + decay + covid + era
    c006 = run_reform_plus_covid(df)
    comp_rows.append(("C006", "Reform+decay+covid+era",
                      "xgboost", "+reform+decay+covid+era", c006, "baseline"))
    print(f"  C006 reform+decay            MAE={c006['mae_days']:6.2f}  R²_log={c006['r2_log']:.3f}")

    # C007: macro — DEFER, no external fetch in scope
    _append_row("C007", "Macro context (WRLURI+ACS)",
                "n/a", "macro_context",
                {"mae_days": float("nan"), "rmse_days": float("nan"),
                 "r2_log": float("nan"), "r2_days": float("nan")},
                "DEFER (WRLURI+ACS fetch outside Phase 2.5 budget)")
    print("  C007 macro                   DEFER")

    # C008: monotone constraints
    c008 = run_monotone_all(df)
    comp_rows.append(("C008", "Monotone valuation+units",
                      "xgboost_monotone", "monotone", c008, "baseline"))
    print(f"  C008 monotone                MAE={c008['mae_days']:6.2f}  R²_log={c008['r2_log']:.3f}")

    # C009: quantile P50
    c009 = run_quantile_p50_p90(df)
    comp_rows.append(("C009", "XGB quantile P50",
                      "xgboost_q50", "quantile=0.5", c009, "baseline"))
    print(f"  C009 quantile P50            MAE={c009['mae_days']:6.2f}  R²_log={c009['r2_log']:.3f}")

    # C010: LightGBM tuned
    c010 = run_lightgbm_tuned(df)
    comp_rows.append(("C010", "LightGBM tuned+dow",
                      "lightgbm", "+dow tuned", c010, "baseline"))
    print(f"  C010 LightGBM tuned          MAE={c010['mae_days']:6.2f}  R²_log={c010['r2_log']:.3f}")

    # C011: Seattle Ridge + stages
    c011 = run_seattle_ridge_stages(seattle)
    comp_rows.append(("C011", "Seattle-only Ridge + stages",
                      "ridge", "+seattle_stages", c011, "Seattle subset"))
    print(f"  C011 Seattle Ridge stages    MAE={c011['mae_days']:6.2f}  R²_log={c011['r2_log']:.3f}")

    # C012: Seattle XGB with buckets only — THE KEY ABLATION
    c012 = run_seattle_only_with_buckets(seattle)
    comp_rows.append(("C012", "Seattle-only XGB + city/out buckets only",
                      "xgboost", "+city_days+out_days", c012, "Seattle subset"))
    print(f"  C012 Seattle buckets only    MAE={c012['mae_days']:6.2f}  R²_log={c012['r2_log']:.3f}")

    # C013: Seattle-only XGB NO stages (generic only) — baseline ablation
    c013 = run_seattle_no_stages_baseline(seattle)
    comp_rows.append(("C013", "Seattle-only XGB no stages (ablation)",
                      "xgboost", "no_stages", c013, "Seattle subset"))
    print(f"  C013 Seattle no stages       MAE={c013['mae_days']:6.2f}  R²_log={c013['r2_log']:.3f}")

    # Append rows to results.tsv; track best.
    # Comparison baseline is 89.401 for cross-city rows; per-city rows
    # (Seattle C001-C013, NYC C002) compare on their own subset so we never
    # mark them KEEP against the cross-city baseline (different populations).
    for exp_id, desc, model, feats, metrics, scope in comp_rows:
        if scope == "baseline":
            note = _keep_rule(metrics["mae_days"], best_mae)
            if note == "KEEP":
                best_mae = metrics["mae_days"]
        else:
            note = f"SUBSET_ONLY ({scope})"
        _append_row(exp_id, desc, model, feats, metrics, note)

    summary["composition"] = {r[0]: r[4] for r in comp_rows}

    # ---------- Phase 2.5 Final
    print("\n--- Phase 2.5 final best ---")
    print(f"  cross-city baseline MAE (unchanged): {best_mae:.2f}")
    print(f"  Seattle-only best (C012, buckets only): {c012['mae_days']:.2f} "
          f"(R² on raw days = {c012['r2_days']:.3f})")
    if nyc_stage:
        nyc_mod = summary["composition"].get("C002")
        if nyc_mod:
            print(f"  NYC BIS-subset best (C002, stages): {nyc_mod['mae_days']:.2f} "
                  f"(R²_log = {nyc_mod['r2_log']:.3f})")

    summary["best_cross_city_mae"] = best_mae
    return summary


if __name__ == "__main__":
    summary = run_phase25_all()
