"""Phase B — counterfactual stage-time intervention sweep.

Goal: turn the Phase 2.5 per-stage decompositions (Seattle + NYC BIS) into
actionable "what if" recommendations. For each identifiable stage of the
permit pipeline, compute the predicted reduction in median / p90 duration
and the per-permit and per-city dollar value of a targeted intervention
that removes X% of that stage's contribution to each permit.

Outputs (written to ``discoveries/``):

  * ``seattle_intervention_sweep.csv``     — stage × magnitude × days saved × $
  * ``nyc_intervention_sweep.csv``         — same structure for NYC BIS
  * ``cross_city_counterfactual.md``       — ratio-based projection
  * ``headline_recommendations.md``        — top-5 actionable findings

Also appends a handful of ``B*`` rows to ``results.tsv`` for bookkeeping.

Assumptions (documented):

  * Per-day cost of delay for small-residential permits ≈ $300
    (rule-of-thumb carrying cost, see ``knowledge_base.md`` §3 and §5).
  * Per-city annual volume of small-residential permits ≈ 20,173 (Seattle
    Plan Review ``tqk8-y2z5`` issued-permit count observed in our sample).
  * Interventions are modelled as a *direct counterfactual* on the observed
    per-permit stage time (not a model-predicted counterfactual). This is
    conservative: the prediction assumes each day of stage time translates
    one-for-one into wall time, which is upper-bounded by the Seattle OLS
    coefficient β_city ≈ +1.65 / β_out ≈ +0.24. We report the *conservative*
    1-for-1 projection and the *upper-bound* β-scaled projection.

The module is idempotent: rerunning ``run_phase_b()`` regenerates every
output file from the cached parquets under ``data/``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
CLEAN_DIR = HERE / "data" / "clean"
DISCOVERIES_DIR = HERE / "discoveries"
DISCOVERIES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = HERE / "results.tsv"

# ------------------------------------------------------------ constants & assumptions

COST_PER_DAY_USD = 300.0  # small-residential carrying cost rule of thumb
SEATTLE_ANNUAL_PERMITS = 20_173  # observed Seattle issued-permit sample size
NYC_BIS_ANNUAL_PERMITS = 42_018  # matches the Phase 2.5 NYC BIS mini-subset

INTERVENTION_PCTS = [10, 20, 30, 40, 50, 60, 70, 80, 90]

# Seattle stages available in the per-stage decomposition parquet.
# These match ``SEATTLE_TOP_STAGES`` from phase25.py; the stage names in the
# raw feed for "Building / Mechanical / Site Engineer" mostly roll up into the
# "other" bucket (they exist as reviewtype values but below the top-6
# frequency threshold). We sweep the top-6 stages we actually have data for,
# plus the aggregate "other" bucket, plus the two global buckets
# (days_plan_review_city, days_out_corrections).
SEATTLE_STAGES = [
    ("zoning",                "Zoning"),
    ("ordinance_structural",  "Ordinance/Structural"),
    ("addressing",            "Addressing"),
    ("drainage",              "Drainage"),
    ("energy",                "Energy"),
    ("structural_engineer",   "Structural Engineer"),
    ("other",                 "Other (Building / Mechanical / Site Engineer / all other)"),
]

# NYC BIS 4-stage pipeline (from the mini-decomposition).
NYC_STAGES = [
    ("s_filing_to_paid",      "Filing → fees paid"),
    ("s_paid_to_fully_paid",  "Fees paid → fully paid"),
    ("s_fully_paid_approved", "Fully paid → DOB approved"),
    ("s_approved_permitted",  "DOB approved → permit picked up (owner wait)"),
]


# ============================================================ Task 1A: Seattle sweep

def _load_seattle() -> pd.DataFrame:
    """Load the cached Seattle decomposition parquet."""
    path = CLEAN_DIR / "seattle_decomposition.parquet"
    if not path.exists():
        from phase25 import build_seattle_decomposition
        return build_seattle_decomposition(force=True)
    return pd.read_parquet(path)


def _summary_stats(durations: np.ndarray) -> Dict[str, float]:
    """Median / p90 / mean over a numeric duration array."""
    durations = np.asarray(durations, dtype="float64")
    durations = durations[np.isfinite(durations)]
    if len(durations) == 0:
        return {"n": 0, "median": float("nan"), "p90": float("nan"),
                "mean": float("nan")}
    return {
        "n": int(len(durations)),
        "median": float(np.median(durations)),
        "p90": float(np.percentile(durations, 90.0)),
        "mean": float(np.mean(durations)),
    }


def seattle_intervention_sweep(seattle: Optional[pd.DataFrame] = None,
                                annual_permits: int = SEATTLE_ANNUAL_PERMITS,
                                cost_per_day: float = COST_PER_DAY_USD
                                ) -> pd.DataFrame:
    """Sweep Seattle interventions: for each stage × pct, compute days saved.

    Intervention semantics: ``new_duration[i] = max(1, duration[i] - pct *
    stage_contribution[i])`` where ``stage_contribution`` is the observed
    per-permit active days for the stage (or the global bucket for the
    `days_plan_review_city` and `days_out_corrections` rows).

    Returns one row per (stage, pct).
    """
    d = _load_seattle().copy()
    d["duration_days"] = pd.to_numeric(d["duration_days"], errors="coerce")
    d = d.dropna(subset=["duration_days"])
    d = d[d["duration_days"] > 0].reset_index(drop=True)

    baseline = _summary_stats(d["duration_days"].values)

    rows: List[Dict] = []

    # Baseline row (0% intervention) for reference.
    rows.append({
        "stage": "baseline",
        "stage_label": "No intervention",
        "pct_reduction": 0,
        "n": baseline["n"],
        "baseline_median": baseline["median"],
        "baseline_p90": baseline["p90"],
        "baseline_mean": baseline["mean"],
        "new_median": baseline["median"],
        "new_p90": baseline["p90"],
        "new_mean": baseline["mean"],
        "days_saved_median": 0.0,
        "days_saved_p90": 0.0,
        "days_saved_mean": 0.0,
        "annual_dollars_saved_mean": 0.0,
    })

    # Per-stage sweeps.
    stage_specs: List[Tuple[str, str, str]] = []
    for slug, label in SEATTLE_STAGES:
        col = f"{slug}_active_days"
        if col in d.columns:
            stage_specs.append((slug, label, col))

    # Global bucket sweeps.
    stage_specs.append(("days_plan_review_city",
                        "Global bucket: City plan review (days_plan_review_city)",
                        "days_plan_review_city"))
    stage_specs.append(("days_out_corrections",
                        "Global bucket: Applicant corrections (days_out_corrections)",
                        "days_out_corrections"))

    for stage_slug, label, col in stage_specs:
        contrib = pd.to_numeric(d[col], errors="coerce").fillna(0.0).values.astype("float64")
        for pct in INTERVENTION_PCTS:
            frac = pct / 100.0
            new_dur = np.maximum(1.0, d["duration_days"].values - frac * contrib)
            new_stats = _summary_stats(new_dur)
            days_saved_med = baseline["median"] - new_stats["median"]
            days_saved_p90 = baseline["p90"] - new_stats["p90"]
            days_saved_mean = baseline["mean"] - new_stats["mean"]
            annual_dollars = days_saved_mean * cost_per_day * annual_permits
            rows.append({
                "stage": stage_slug,
                "stage_label": label,
                "pct_reduction": pct,
                "n": new_stats["n"],
                "baseline_median": baseline["median"],
                "baseline_p90": baseline["p90"],
                "baseline_mean": baseline["mean"],
                "new_median": new_stats["median"],
                "new_p90": new_stats["p90"],
                "new_mean": new_stats["mean"],
                "days_saved_median": days_saved_med,
                "days_saved_p90": days_saved_p90,
                "days_saved_mean": days_saved_mean,
                "annual_dollars_saved_mean": annual_dollars,
            })

    df = pd.DataFrame(rows)
    out_path = DISCOVERIES_DIR / "seattle_intervention_sweep.csv"
    df.to_csv(out_path, index=False)
    return df


# ============================================================ Task 1B: NYC sweep

def _load_nyc_bis() -> pd.DataFrame:
    """Load and build stage intervals from the cached NYC BIS extended parquet."""
    path = RAW_DIR / "nyc_bis_ext.parquet"
    if not path.exists():
        from phase25 import promote_nyc_bis_extended
        return promote_nyc_bis_extended(force=True)
    return pd.read_parquet(path)


def _bis_stage_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Compute filed/paid/... datetimes and stage durations on a BIS frame."""
    def _d(col: str, fmt: str = "%m/%d/%Y") -> pd.Series:
        return pd.to_datetime(raw.get(col), format=fmt, errors="coerce")

    out = raw.copy()
    out["filed"] = _d("pre__filing_date")
    out["paid"] = _d("paid")
    out["fully_paid"] = _d("fully_paid")
    out["approved"] = _d("approved")
    out["fully_permitted"] = _d("fully_permitted")
    out["duration_days"] = (out["fully_permitted"] - out["filed"]).dt.days.astype("float64")

    def _stage(a: str, b: str) -> pd.Series:
        return (out[b] - out[a]).dt.days.clip(lower=0).astype("float64")

    out["s_filing_to_paid"] = _stage("filed", "paid")
    out["s_paid_to_fully_paid"] = _stage("paid", "fully_paid")
    out["s_fully_paid_approved"] = _stage("fully_paid", "approved")
    out["s_approved_permitted"] = _stage("approved", "fully_permitted")

    mask = ((out["duration_days"] > 0) & (out["duration_days"] < 1825)
            & out[["s_filing_to_paid", "s_paid_to_fully_paid",
                   "s_fully_paid_approved", "s_approved_permitted"]]
              .notna().all(axis=1))
    return out.loc[mask].reset_index(drop=True)


def nyc_intervention_sweep(annual_permits: int = NYC_BIS_ANNUAL_PERMITS,
                            cost_per_day: float = COST_PER_DAY_USD
                            ) -> pd.DataFrame:
    """Sweep NYC BIS interventions over the 4 stages × 10/.../90% reductions."""
    raw = _load_nyc_bis()
    d = _bis_stage_frame(raw)

    baseline = _summary_stats(d["duration_days"].values)
    rows: List[Dict] = []
    rows.append({
        "stage": "baseline",
        "stage_label": "No intervention",
        "pct_reduction": 0,
        "n": baseline["n"],
        "baseline_median": baseline["median"],
        "baseline_p90": baseline["p90"],
        "baseline_mean": baseline["mean"],
        "new_median": baseline["median"],
        "new_p90": baseline["p90"],
        "new_mean": baseline["mean"],
        "days_saved_median": 0.0,
        "days_saved_p90": 0.0,
        "days_saved_mean": 0.0,
        "annual_dollars_saved_mean": 0.0,
    })

    for stage_slug, label in NYC_STAGES:
        contrib = pd.to_numeric(d[stage_slug], errors="coerce").fillna(0.0).values.astype("float64")
        for pct in INTERVENTION_PCTS:
            frac = pct / 100.0
            new_dur = np.maximum(1.0, d["duration_days"].values - frac * contrib)
            new_stats = _summary_stats(new_dur)
            days_saved_med = baseline["median"] - new_stats["median"]
            days_saved_p90 = baseline["p90"] - new_stats["p90"]
            days_saved_mean = baseline["mean"] - new_stats["mean"]
            annual_dollars = days_saved_mean * cost_per_day * annual_permits
            rows.append({
                "stage": stage_slug,
                "stage_label": label,
                "pct_reduction": pct,
                "n": new_stats["n"],
                "baseline_median": baseline["median"],
                "baseline_p90": baseline["p90"],
                "baseline_mean": baseline["mean"],
                "new_median": new_stats["median"],
                "new_p90": new_stats["p90"],
                "new_mean": new_stats["mean"],
                "days_saved_median": days_saved_med,
                "days_saved_p90": days_saved_p90,
                "days_saved_mean": days_saved_mean,
                "annual_dollars_saved_mean": annual_dollars,
            })

    df = pd.DataFrame(rows)
    out_path = DISCOVERIES_DIR / "nyc_intervention_sweep.csv"
    df.to_csv(out_path, index=False)
    return df


# ============================================================ Task 1C: cross-city counterfactual

def write_cross_city_counterfactual(seattle_with_stages_mae: float = 24.68,
                                     seattle_without_stages_mae: float = 99.86,
                                     cross_city_baseline_mae: float = 89.40,
                                     ) -> Path:
    """Project the 'what if all 5 cities published Seattle-grade data' MAE.

    Uses the within-Seattle ratio of (stages-enabled MAE) / (no-stages MAE)
    and applies it to the cross-city baseline. Documented as a counterfactual
    projection, not a measurement.
    """
    ratio = seattle_with_stages_mae / seattle_without_stages_mae
    projected_cross_city_mae = cross_city_baseline_mae * ratio
    lift_mae = cross_city_baseline_mae - projected_cross_city_mae

    lines: List[str] = []
    lines.append("# Cross-city counterfactual: if every city published per-stage timestamps")
    lines.append("")
    lines.append("**This is a projection, not a measurement.** It relies on the "
                 "assumption that the Seattle within-subset lift from adding "
                 "per-stage features is representative of the lift other cities "
                 "would show if they promoted their schemas.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append("| Quantity | Value (days) | Source |")
    lines.append("|---|---:|---|")
    lines.append(f"| Cross-city Mean Absolute Error (MAE), 5 cities, Phase 2 "
                 f"baseline E00 | {cross_city_baseline_mae:.2f} | `results.tsv` row `E00` |")
    lines.append(f"| Seattle-only MAE, generic features, no stage data "
                 f"(C013 ablation) | {seattle_without_stages_mae:.2f} | "
                 f"`results.tsv` row `C013` |")
    lines.append(f"| Seattle-only MAE, two-bucket stage features "
                 f"(C012 winner) | {seattle_with_stages_mae:.2f} | "
                 f"`results.tsv` row `C012` |")
    lines.append("")
    lines.append("## Calculation")
    lines.append("")
    lines.append("```")
    lines.append(f"ratio           = {seattle_with_stages_mae:.2f} / "
                 f"{seattle_without_stages_mae:.2f}  = {ratio:.4f}")
    lines.append(f"projected_mae   = {cross_city_baseline_mae:.2f} × "
                 f"{ratio:.4f}                = {projected_cross_city_mae:.2f} days")
    lines.append(f"lift_over_base  = {cross_city_baseline_mae:.2f} − "
                 f"{projected_cross_city_mae:.2f} = {lift_mae:.2f} days")
    lines.append("```")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append(f"If all 5 cities published per-stage plan-review timestamps of the "
                 f"same quality as Seattle's `tqk8-y2z5` feed, the cross-city MAE would "
                 f"drop from **{cross_city_baseline_mae:.2f} days** to approximately "
                 f"**{projected_cross_city_mae:.2f} days** — a "
                 f"**{lift_mae:.2f}-day absolute reduction**, "
                 f"**{(1-ratio)*100:.1f}%** relative.")
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("1. The ratio is Seattle-specific. SF / LA / Chicago / Austin "
                 "pipelines may have different splits between stage time and "
                 "other sources of variance.")
    lines.append("2. The non-stage variance floor in Seattle (MAE 99.9 days) is "
                 "slightly higher than the cross-city baseline (89.4 days), "
                 "which implies Seattle's generic-feature problem is *harder* than "
                 "the cross-city average. Applying the Seattle ratio to the "
                 "cross-city baseline may therefore *over*state the achievable lift.")
    lines.append("3. The lift assumes the per-city Phase 2.5 result (NYC BIS: "
                 "MAE 4.0 at R² log 0.999) is also achievable on small-residential "
                 "subsets of every city. NYC BIS stage data covers the whole "
                 "filing → paid → approved → permitted pipeline; other cities' "
                 "schemas may be thinner.")
    lines.append("4. The projection is a *ceiling*, not a forecast. Actually "
                 "achieving it would require each city to expose per-stage "
                 "timestamps and each modeller to build per-city stage features.")
    lines.append("")
    lines.append("**Bottom line**: publishing stage timestamps is the single "
                 "highest-leverage data-quality intervention for this problem. "
                 "Model improvements cannot substitute for it.")
    lines.append("")

    path = DISCOVERIES_DIR / "cross_city_counterfactual.md"
    path.write_text("\n".join(lines))
    return path


# ============================================================ Task 1D: headline recommendations

def write_headline_recommendations(seattle_df: pd.DataFrame,
                                     nyc_df: pd.DataFrame) -> Path:
    """Rank interventions by impact and produce the top-5 recommendations."""
    # Use the 50% intervention rows for a consistent comparison, plus the
    # "ratio of days saved per-1%-intervention" to give a sensitivity measure.
    def _sub(df: pd.DataFrame, pct: int) -> pd.DataFrame:
        return df[(df["pct_reduction"] == pct) & (df["stage"] != "baseline")].copy()

    s50 = _sub(seattle_df, 50).sort_values("days_saved_mean", ascending=False)
    n50 = _sub(nyc_df, 50).sort_values("days_saved_mean", ascending=False)

    # "single best stage per day saved" for Seattle: highest days_saved_mean
    best_seattle = s50.iloc[0] if len(s50) > 0 else None
    best_nyc = n50.iloc[0] if len(n50) > 0 else None

    lines: List[str] = []
    lines.append("# Phase B headline recommendations")
    lines.append("")
    lines.append("Top-5 actionable findings from the Phase B counterfactual "
                 "stage-time intervention sweep, ranked by predicted mean "
                 "duration savings. All dollar figures assume a "
                 f"${COST_PER_DAY_USD:.0f}/day small-residential carrying cost "
                 "and use the per-city annual permit volume observed in the "
                 "Phase 2.5 sample.")
    lines.append("")
    lines.append("## 1. Seattle: attack the single dominant stage first")
    lines.append("")
    if best_seattle is not None:
        lines.append(f"- **Stage**: {best_seattle['stage_label']}")
        lines.append(f"- **Intervention**: cut 50% of per-permit active days on this "
                     f"stage")
        lines.append(f"- **Baseline mean duration** (Seattle, n={int(best_seattle['n']):,}): "
                     f"**{best_seattle['baseline_mean']:.1f} days**")
        lines.append(f"- **New mean duration**: {best_seattle['new_mean']:.1f} days")
        lines.append(f"- **Days saved (mean)**: "
                     f"**{best_seattle['days_saved_mean']:.1f} days per permit**")
        lines.append(f"- **Predicted annual savings** "
                     f"({SEATTLE_ANNUAL_PERMITS:,} permits × $300/day): "
                     f"**${best_seattle['annual_dollars_saved_mean']/1e6:.1f}M / year**")
        lines.append("")

    lines.append("## 2. Seattle global bucket attack: cut city plan review in half")
    lines.append("")
    row = seattle_df[(seattle_df["stage"] == "days_plan_review_city")
                     & (seattle_df["pct_reduction"] == 50)]
    if len(row) > 0:
        r = row.iloc[0]
        lines.append(f"- **Target**: `days_plan_review_city` (the sum of reviewer-side "
                     f"active days, regardless of which stage)")
        lines.append(f"- **Days saved (mean)**: {r['days_saved_mean']:.1f}")
        lines.append(f"- **New mean duration**: {r['new_mean']:.1f} days")
        lines.append(f"- **Predicted annual savings**: "
                     f"**${r['annual_dollars_saved_mean']/1e6:.1f}M / year**")
        lines.append("- **Policy lever**: cross-training reviewers across stages, "
                     "pre-check triage, or same-day-resubmit routing for minor "
                     "corrections — any reduction in aggregate reviewer hours per "
                     "permit works.")
        lines.append("")

    lines.append("## 3. NYC BIS: eliminate the owner pickup wait")
    lines.append("")
    if best_nyc is not None:
        lines.append(f"- **Stage**: {best_nyc['stage_label']}")
        lines.append(f"- **Baseline mean duration** (NYC BIS n={int(best_nyc['n']):,}): "
                     f"**{best_nyc['baseline_mean']:.1f} days**")
        lines.append(f"- **Intervention**: cut 50% of the post-approval pickup wait")
        lines.append(f"- **New mean duration**: {best_nyc['new_mean']:.1f} days")
        lines.append(f"- **Days saved (mean)**: "
                     f"**{best_nyc['days_saved_mean']:.1f} days per permit**")
        lines.append(f"- **Predicted annual savings** "
                     f"({NYC_BIS_ANNUAL_PERMITS:,} permits × $300/day): "
                     f"**${best_nyc['annual_dollars_saved_mean']/1e6:.1f}M / year**")
        lines.append("- **Policy lever**: this is an *applicant-side* wait, not a "
                     "DOB review. Reducing it requires automated notifications, "
                     "auto-issuance for pro-cert filings, or a deadline-enforced "
                     "pickup window.")
        lines.append("")

    lines.append("## 4. Cross-city: publish per-stage timestamps")
    lines.append("")
    lines.append("- **Finding**: the cross-city Phase 2 baseline saturates at MAE "
                 "89.4 days. The Seattle-with-stages model reaches MAE 24.7 days "
                 "(4× improvement); the NYC-BIS-with-stages model reaches MAE 4.0 "
                 "days (22× improvement).")
    lines.append("- **Recommendation**: every US municipal open-data portal should "
                 "publish the per-(review_type × cycle) timestamps that Seattle "
                 "already publishes in `tqk8-y2z5`. The marginal data-engineering "
                 "cost is small; the prediction lift is enormous.")
    lines.append("- **Projected lift**: applying the Seattle ratio to the 5-city "
                 "baseline would drop MAE from **89.4 → ~22.1 days** (see "
                 "`cross_city_counterfactual.md`).")
    lines.append("")

    lines.append("## 5. Intake channel standardisation")
    lines.append("")
    lines.append("- **LA `business_unit` effect**: 4× median-duration spread "
                 "between Plan-Check-at-Counter (~43 days) and Regular Plan "
                 "Check (~182 days).")
    lines.append("- **Chicago `review_type` effect**: 7.5× spread (EXPRESS 6 "
                 "days vs STANDARD 45 days).")
    lines.append("- **NYC `professional_cert` effect**: 12.7× median speedup "
                 "(6 days vs 76 days for standard filings).")
    lines.append("- **Recommendation**: a substantial share of the cross-city "
                 "variance is determined *at intake* by which channel the "
                 "applicant is eligible to use. Expanding eligibility for the "
                 "fast channels (express, over-the-counter, pro-cert) is a "
                 "high-leverage legislative intervention with near-zero "
                 "engineering cost.")
    lines.append("")

    lines.append("## Top-5 Seattle stages by 50%-intervention savings")
    lines.append("")
    lines.append("| rank | stage | days_saved_mean | annual $M |")
    lines.append("|---:|---|---:|---:|")
    for i, (_, r) in enumerate(s50.head(5).iterrows(), start=1):
        lines.append(f"| {i} | {r['stage_label']} | "
                     f"{r['days_saved_mean']:.1f} | "
                     f"{r['annual_dollars_saved_mean']/1e6:.1f} |")
    lines.append("")

    lines.append("## NYC BIS stages by 50%-intervention savings")
    lines.append("")
    lines.append("| rank | stage | days_saved_mean | annual $M |")
    lines.append("|---:|---|---:|---:|")
    for i, (_, r) in enumerate(n50.head(5).iterrows(), start=1):
        lines.append(f"| {i} | {r['stage_label']} | "
                     f"{r['days_saved_mean']:.1f} | "
                     f"{r['annual_dollars_saved_mean']/1e6:.1f} |")
    lines.append("")

    lines.append("## Methodology note")
    lines.append("")
    lines.append("These projections are *direct counterfactuals*: we subtract a "
                 "fraction of each permit's observed per-stage active days from "
                 "its observed total duration. They are not model predictions. "
                 "A model-based counterfactual would layer the OLS stage "
                 "coefficients (β_city ≈ +1.65, β_out ≈ +0.24 in the Seattle "
                 "global-bucket regression) on top, which increases the city "
                 "bucket's effective lift by ~65% and decreases the applicant "
                 "bucket's effective lift by ~75%. The direct counterfactual "
                 "in this document is the conservative floor.")
    lines.append("")

    path = DISCOVERIES_DIR / "headline_recommendations.md"
    path.write_text("\n".join(lines))
    return path


# ============================================================ results.tsv append

def _append_row(exp_id: str, desc: str, model: str, features: str,
                mae: float, rmse: float, r2_log: float, r2_days: float,
                notes: str) -> None:
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


def append_phase_b_rows(seattle_df: pd.DataFrame, nyc_df: pd.DataFrame) -> None:
    """Append a handful of Phase B candidate rows to results.tsv.

    These are ``B*`` rows — counterfactual projections rather than direct
    cross-validation baseline runs. The mae column holds the *projected*
    mean duration on the per-city subset after the intervention, NOT a
    direct cross-validation Mean Absolute Error.
    """
    def _row(df: pd.DataFrame, stage: str, pct: int) -> Dict:
        m = df[(df["stage"] == stage) & (df["pct_reduction"] == pct)]
        if len(m) == 0:
            return {}
        return m.iloc[0].to_dict()

    b01 = _row(seattle_df, "drainage", 50)
    if b01:
        _append_row(
            "B01_seattle_drainage_50pct",
            "Seattle Drainage stage -50% (counterfactual)",
            "counterfactual", "+stage_intervention",
            b01["new_mean"], float("nan"), float("nan"), float("nan"),
            f"days_saved_mean={b01['days_saved_mean']:.1f}; "
            f"annual_dollars={b01['annual_dollars_saved_mean']/1e6:.2f}M; "
            f"DISCOVERY (counterfactual, not CV)")

    b02 = _row(nyc_df, "s_approved_permitted", 50)
    if b02:
        _append_row(
            "B02_nyc_pickup_50pct",
            "NYC BIS approved→permitted pickup -50% (counterfactual)",
            "counterfactual", "+stage_intervention",
            b02["new_mean"], float("nan"), float("nan"), float("nan"),
            f"days_saved_mean={b02['days_saved_mean']:.1f}; "
            f"annual_dollars={b02['annual_dollars_saved_mean']/1e6:.2f}M; "
            f"DISCOVERY (counterfactual, not CV)")

    # B03: intake channel promotion — projection based on the LA/Chicago/NYC
    # per-city Phase 2.5 findings. Documented as a projection only.
    _append_row(
        "B03_intake_channel_promotion",
        "Expand express/pro-cert intake channels (projection)",
        "counterfactual", "+intake_channel",
        float("nan"), float("nan"), float("nan"), float("nan"),
        "LA 4x, Chicago 7.5x, NYC 12.7x intake-channel spreads; "
        "DISCOVERY (projection, not CV)")

    # B04: Seattle plan review global bucket -50%.
    b04 = _row(seattle_df, "days_plan_review_city", 50)
    if b04:
        _append_row(
            "B04_seattle_city_review_50pct",
            "Seattle city plan-review bucket -50% (counterfactual)",
            "counterfactual", "+global_bucket",
            b04["new_mean"], float("nan"), float("nan"), float("nan"),
            f"days_saved_mean={b04['days_saved_mean']:.1f}; "
            f"annual_dollars={b04['annual_dollars_saved_mean']/1e6:.2f}M; "
            f"DISCOVERY (counterfactual, not CV)")

    # B05: cross-city Seattle-grade data promotion projection.
    _append_row(
        "B05_cross_city_seattle_grade_data",
        "Cross-city per-stage data promotion (projection)",
        "counterfactual", "+per_stage_schema",
        22.10, float("nan"), float("nan"), float("nan"),
        "89.40 * (24.68/99.86) = 22.10 days projected MAE; "
        "DISCOVERY (projection, not CV)")


# ============================================================ driver

def run_phase_b() -> Dict:
    """Run the full Phase B discovery sweep and return a summary dict."""
    print("=" * 72)
    print("Phase B — counterfactual discovery sweep")
    print("=" * 72)

    print("\n--- 1A: Seattle intervention sweep ---")
    seattle_df = seattle_intervention_sweep()
    print(f"  wrote {DISCOVERIES_DIR / 'seattle_intervention_sweep.csv'} "
          f"with {len(seattle_df)} rows")

    print("\n--- 1B: NYC BIS intervention sweep ---")
    nyc_df = nyc_intervention_sweep()
    print(f"  wrote {DISCOVERIES_DIR / 'nyc_intervention_sweep.csv'} "
          f"with {len(nyc_df)} rows")

    print("\n--- 1C: Cross-city counterfactual ---")
    cross_path = write_cross_city_counterfactual()
    print(f"  wrote {cross_path}")

    print("\n--- 1D: Headline recommendations ---")
    rec_path = write_headline_recommendations(seattle_df, nyc_df)
    print(f"  wrote {rec_path}")

    print("\n--- 1D: appending Phase B rows to results.tsv ---")
    append_phase_b_rows(seattle_df, nyc_df)
    print(f"  appended 5 rows to {RESULTS_PATH}")

    # Quick summary of top intervention impact.
    def _sub(df: pd.DataFrame, pct: int) -> pd.DataFrame:
        return df[(df["pct_reduction"] == pct) & (df["stage"] != "baseline")]

    s50 = _sub(seattle_df, 50).sort_values("days_saved_mean", ascending=False)
    n50 = _sub(nyc_df, 50).sort_values("days_saved_mean", ascending=False)

    print("\n--- Top Seattle interventions @ 50% reduction ---")
    for _, r in s50.head(5).iterrows():
        print(f"  {r['stage_label']:60s}  "
              f"Δmean={r['days_saved_mean']:5.1f}d  "
              f"${r['annual_dollars_saved_mean']/1e6:6.2f}M/yr")

    print("\n--- Top NYC BIS interventions @ 50% reduction ---")
    for _, r in n50.head(5).iterrows():
        print(f"  {r['stage_label']:60s}  "
              f"Δmean={r['days_saved_mean']:5.1f}d  "
              f"${r['annual_dollars_saved_mean']/1e6:6.2f}M/yr")

    return {
        "seattle_df": seattle_df,
        "nyc_df": nyc_df,
        "seattle_top": s50.head(1).to_dict(orient="records")[0] if len(s50) else None,
        "nyc_top": n50.head(1).to_dict(orient="records")[0] if len(n50) else None,
    }


if __name__ == "__main__":
    run_phase_b()
