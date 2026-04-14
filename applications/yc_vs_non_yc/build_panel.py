"""Build the Phase 0.5 matched-pair panel.

Steps:
1. Concat all Form D quarterly ZIPs → one joined DataFrame (all filings).
2. Filter to seed/early-stage tech raises → `seed_panel`.
3. Join YC companies (2014-2019 batches) by normalized name → `yc_matched`.
4. For each filing (YC match AND non-YC control), look up outcome:
   follow_on_raise_within_5y = any later Form D by same CIK within 60 months.
5. Write `data/panel.parquet` with treated (`is_yc=1`) and control (`is_yc=0`)
   rows, plus pre-treatment covariates (SAFE only) and the outcome.
"""
from __future__ import annotations

import glob
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from secformd_loader import (  # noqa: E402
    filter_seed_stage,
    join_formd_tables,
    load_formd_quarter,
    normalize_issuer_name,
)
from yc_loader import load_yc_companies  # noqa: E402
from matcher import match_yc_to_formd  # noqa: E402


YC_MIN_YEAR = 2014
YC_MAX_YEAR = 2019  # need 5 y of forward outcome window; we have data through 2024
OUTCOME_MONTHS = 60


def build_all_formd() -> pd.DataFrame:
    zips = sorted(glob.glob(str(HERE / "data" / "sec_formd" / "*.zip")))
    parts = []
    for z in zips:
        sub, iss, off = load_formd_quarter(z)
        parts.append(join_formd_tables(sub, iss, off))
    df = pd.concat(parts, ignore_index=True)
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["totalofferingamount_num"] = pd.to_numeric(df["totalofferingamount"], errors="coerce")
    return df


def outcome_follow_on(all_formd: pd.DataFrame, anchor: pd.DataFrame,
                      months: int = OUTCOME_MONTHS) -> pd.Series:
    """For each anchor row, return 1 if any later Form D by same CIK within
    `months` of the anchor's filing_date.

    A Form D amendment (SUBMISSIONTYPE='D/A') does NOT count as a raise.
    """
    out = np.zeros(len(anchor), dtype=int)
    fd = all_formd[all_formd["submissiontype"].str.upper().str.startswith("D")
                   & ~all_formd["submissiontype"].str.upper().str.startswith("D/A")]
    by_cik = {c: g[["filing_date", "accessionnumber"]]
              .sort_values("filing_date")
              for c, g in fd.groupby("cik")}
    for i, row in enumerate(anchor.itertuples(index=False)):
        g = by_cik.get(str(row.cik))
        if g is None:
            continue
        lo = row.filing_date + pd.Timedelta(days=90)   # exclude same raise + immediate amendments
        hi = row.filing_date + pd.DateOffset(months=months)
        later = g[(g["filing_date"] >= lo) & (g["filing_date"] <= hi)
                  & (g["accessionnumber"] != row.accessionnumber)]
        if not later.empty:
            out[i] = 1
    return pd.Series(out, index=anchor.index, name="follow_on_raise_within_5y")


def main():
    t0 = time.time()
    print("[1/5] load & join all Form D quarters...", flush=True)
    all_fd = build_all_formd()
    print(f"      {len(all_fd):,} rows, {time.time()-t0:.1f}s", flush=True)

    print("[2/5] filter seed-stage...", flush=True)
    seed = filter_seed_stage(all_fd)
    seed = seed[seed["filing_date"].notna()]
    print(f"      {len(seed):,} seed-stage rows", flush=True)

    print("[3/5] load YC + match...", flush=True)
    yc = load_yc_companies(HERE / "data" / "yc_companies_raw.json")
    yc_cohort = yc[yc["batch_year"].between(YC_MIN_YEAR, YC_MAX_YEAR)].copy()
    yc_matched = match_yc_to_formd(yc_cohort, seed, strategy="exact")
    yc_matched["is_yc"] = 1
    print(f"      YC cohort size: {len(yc_cohort):,}; matched: {len(yc_matched):,}",
          flush=True)

    print("[4/5] build control pool + outcome labels...", flush=True)
    matched_accn = set(yc_matched["accessionnumber"])
    seed["_norm"] = seed["entityname"].apply(normalize_issuer_name)
    yc_names = set(yc_matched["name"].apply(normalize_issuer_name))
    # Control pool: seed filings in same year range, not YC-matched, not bearing
    # a normalized name that matches ANY YC company in the full cohort
    all_yc_names = set(yc["name"].apply(normalize_issuer_name)) - {""}
    control = seed[
        (seed["filing_date"].dt.year.between(YC_MIN_YEAR, YC_MAX_YEAR + 1))
        & ~seed["accessionnumber"].isin(matched_accn)
        & ~seed["_norm"].isin(all_yc_names)
    ].copy()
    # Keep one filing per CIK (earliest in window), so each control firm appears once
    control = control.sort_values("filing_date").drop_duplicates("cik", keep="first")
    print(f"      control-pool size: {len(control):,}", flush=True)

    # Panel columns
    common_cols = ["cik", "accessionnumber", "filing_date", "totalofferingamount",
                   "industrygrouptype", "stateorcountry"]
    treated = yc_matched.copy()
    treated["batch_year"] = treated["batch_year"].astype(int)
    treated["batch_quarter"] = treated["batch_quarter"].astype(int)
    treated["entityname"] = treated["name"]

    ctrl = control[common_cols + ["entityname", "yearofinc_value_entered", "entitytype"]].copy()
    ctrl["is_yc"] = 0
    ctrl["batch_year"] = ctrl["filing_date"].dt.year
    ctrl["batch_quarter"] = ctrl["filing_date"].dt.quarter
    ctrl["slug"] = np.nan
    ctrl["batch"] = np.nan
    ctrl["yc_id"] = np.nan

    trt = treated[common_cols + ["entityname", "slug", "batch", "batch_year",
                                  "batch_quarter", "is_yc", "yc_id"]].copy()
    # Attach yearofinc + entitytype to treated rows from Form D join
    seed_lookup = seed[["accessionnumber", "yearofinc_value_entered", "entitytype"]].drop_duplicates("accessionnumber")
    trt = trt.merge(seed_lookup, on="accessionnumber", how="left")

    panel = pd.concat([trt, ctrl], ignore_index=True, sort=False)
    panel["filing_date"] = pd.to_datetime(panel["filing_date"])
    panel["totalofferingamount_num"] = pd.to_numeric(panel["totalofferingamount"], errors="coerce")
    panel["log_offering_amount"] = np.log1p(panel["totalofferingamount_num"].fillna(0))

    print("[5/5] compute outcomes (follow-on raise within 60 months)...", flush=True)
    panel = panel.reset_index(drop=True)
    panel["follow_on_raise_within_5y"] = outcome_follow_on(all_fd, panel)
    print(f"      treated outcome rate: {panel.loc[panel.is_yc==1, 'follow_on_raise_within_5y'].mean():.3f}")
    print(f"      control outcome rate: {panel.loc[panel.is_yc==0, 'follow_on_raise_within_5y'].mean():.3f}")

    out = HERE / "data" / "panel.parquet"
    panel.to_parquet(out, index=False)
    print(f"wrote {out}  ({len(panel):,} rows)  total {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
