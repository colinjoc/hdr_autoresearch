"""RV06-alt: propensity-lookalike placebo (substitute for Techstars scrape).

Reviewer RV06 asked for an alternative-accelerator placebo (Techstars) to
distinguish YC-specific treatment from generic "elite early-stage filer"
selection. Techstars data is behind Typesense auth and couldn't be pulled
in budget. Substitute: use the highest-propensity-score non-YC firms as a
"YC-lookalike" placebo cohort. Interpretation:

  - If ATT(YC, PSM) ≈ ATT(lookalike vs remaining non-YC), YC-specific
    treatment is indistinguishable from selection on observables.
  - If ATT(YC) >> ATT(lookalike), something YC-specific remains.

Outputs one row to results.tsv as RV06-alt.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import ExperimentResult, append_result, risk_diff_with_ci  # noqa: E402
from run_reviewer_experiments import (  # noqa: E402
    augment_panel_with_ecosystem, fit_ps, psm_match,
)
from secformd_loader import filter_seed_stage, join_formd_tables, load_formd_quarter  # noqa: E402


def main():
    panel = pd.read_parquet(HERE / "data" / "panel.parquet")
    panel["filing_date"] = pd.to_datetime(panel["filing_date"])
    panel["filing_year"] = panel["filing_date"].dt.year.astype(int)
    panel["filing_quarter"] = panel["filing_date"].dt.quarter.astype(int)
    panel["entitytype"] = panel["entitytype"].fillna("Unknown")
    panel["stateorcountry"] = panel["stateorcountry"].fillna("UNK")
    panel = panel.dropna(subset=["log_offering_amount", "industrygrouptype"]).copy()

    parts = []
    for z in sorted(glob.glob(str(HERE / "data/sec_formd/*.zip"))):
        sub, iss, off = load_formd_quarter(z)
        parts.append(join_formd_tables(sub, iss, off))
    all_fd = pd.concat(parts, ignore_index=True)
    all_fd["filing_date"] = pd.to_datetime(all_fd["filing_date"], errors="coerce")
    seed = filter_seed_stage(all_fd)
    panel_e = augment_panel_with_ecosystem(panel, seed)

    covs = ["filing_year","filing_quarter","industrygrouptype","stateorcountry",
            "log_offering_amount","is_sf_bay","is_nyc","is_boston",
            "log_state_year_density","vix"]
    panel_e["ps"] = fit_ps(panel_e, covs)

    # Identify YC-lookalikes = top-117 non-YC by propensity score
    non_yc = panel_e[panel_e.is_yc == 0].sort_values("ps", ascending=False)
    n_yc = int(panel_e.is_yc.sum())
    lookalike = non_yc.head(n_yc).copy()
    remaining = non_yc.iloc[n_yc:].copy()

    # Compare lookalike vs remaining — same outcome
    rd, lo, hi = risk_diff_with_ci(
        lookalike["follow_on_raise_within_5y"].values,
        remaining["follow_on_raise_within_5y"].values,
        n_boot=3000, seed=17)
    print(f"RV06-alt: YC-lookalike (top-{n_yc} non-YC by PS) vs remaining non-YC")
    print(f"  lookalike rate = {lookalike['follow_on_raise_within_5y'].mean():.3f}")
    print(f"  remaining rate = {remaining['follow_on_raise_within_5y'].mean():.3f}")
    print(f"  ATT (lookalike − remaining) = {rd:+.4f} [{lo:+.4f},{hi:+.4f}]")

    # Compare against RV01-M3_real ATT (YC = +0.0603)
    print(f"  Compare to YC PSM ATT = +0.0603 [−0.031, +0.152]")
    print(f"  Interpretation: |YC_ATT − lookalike_ATT| = {abs(0.0603 - rd):.4f}")

    append_result(ExperimentResult(
        exp_id="RV06-alt",
        description=("RV06-alt lookalike placebo: top-n non-YC by PS vs remaining "
                     "(Techstars scrape blocked on auth)"),
        n_treated=len(lookalike), n_control=len(remaining),
        rate_treated=float(lookalike["follow_on_raise_within_5y"].mean()),
        rate_control=float(remaining["follow_on_raise_within_5y"].mean()),
        risk_diff=rd, rd_ci_lo=lo, rd_ci_hi=hi,
        status="REVIEW",
    ))


if __name__ == "__main__":
    main()
