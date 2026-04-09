"""data_loaders.py — fetch + normalise building-permit open data.

`load_<city>(limit=None)` returns a DataFrame with the shared schema COLUMNS.
Raw pulls are cached to `data/raw/<city>.parquet`. APIs verified live on
2026-04-09 — see `data_sources.md` for per-dataset details and gotchas.
Sources: sf i98e-djp9, nyc ic3t-wcy2, la gwh9-jnip, chicago ydr8-5enu,
austin 3syk-w9eu, seattle tqk8-y2z5, portland BDS_Permit/FeatureServer/22.
Env var `SODA_APP_TOKEN` is sent as X-App-Token on Socrata calls.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd
import requests

np.seterr(over="ignore", invalid="ignore")  # pandas ms cast trips overflow

COLUMNS = [
    "city", "permit_id", "address", "parcel_id", "permit_type",
    "permit_subtype", "use_code", "status", "filed_date", "first_action_date",
    "plan_check_start_date", "plan_check_end_date", "approval_date",
    "issued_date", "finaled_date", "valuation_usd", "square_feet",
    "unit_count", "neighborhood",
]

RAW_DIR = Path(__file__).parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "hdr-building-permits/0.1"
if os.environ.get("SODA_APP_TOKEN"):
    SESSION.headers["X-App-Token"] = os.environ["SODA_APP_TOKEN"]


# --------------------------------- fetch helpers

def _soda_get(base: str, where: Optional[str] = None, limit: Optional[int] = None,
              order: Optional[str] = None, progress_label: Optional[str] = None) -> pd.DataFrame:
    rows: List[Dict] = []
    page = 50_000
    offset = 0
    params: Dict[str, object] = {}
    if where:
        params["$where"] = where
    if order:
        params["$order"] = order
    next_progress = 100_000
    while True:
        want = page if limit is None else min(page, limit - len(rows))
        if want <= 0:
            break
        params["$limit"] = want
        params["$offset"] = offset
        r = SESSION.get(base, params=params, timeout=180)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        if progress_label and len(rows) >= next_progress:
            print(f"    [{progress_label}] pulled {len(rows):,} rows")
            next_progress += 100_000
        if len(batch) < want:
            break
    return pd.DataFrame(rows)


def _arcgis_get(base: str, where: str, limit: Optional[int] = None) -> pd.DataFrame:
    rows: List[Dict] = []
    page = 1000
    offset = 0
    while True:
        want = page if limit is None else min(page, limit - len(rows))
        if want <= 0:
            break
        params = {
            "where": where, "outFields": "*", "f": "json",
            "resultOffset": offset, "resultRecordCount": want,
            "returnGeometry": "false",
        }
        r = SESSION.get(f"{base}/query", params=params, timeout=120)
        r.raise_for_status()
        feats = r.json().get("features", [])
        if not feats:
            break
        rows.extend(f["attributes"] for f in feats)
        offset += len(feats)
        if len(feats) < want:
            break
    return pd.DataFrame(rows)


# --------------------------------- coercion helpers

def _col(df: pd.DataFrame, name: str) -> pd.Series:
    """Return a string column or an empty-string Series if missing."""
    if name in df.columns:
        return df[name].fillna("").astype(str)
    return pd.Series([""] * len(df), index=df.index)


def _dt(df: pd.DataFrame, name: str, fmt: Optional[str] = None) -> pd.Series:
    if name not in df.columns:
        return pd.Series([pd.NaT] * len(df), index=df.index).dt.date
    return pd.to_datetime(df[name], format=fmt, errors="coerce", utc=False).dt.tz_localize(None).dt.date


def _ms_dt(df: pd.DataFrame, name: str) -> pd.Series:
    # ArcGIS returns epoch-ms; pandas float→ms cast has a numpy overflow bug.
    if name not in df.columns:
        return pd.Series([pd.NaT] * len(df), index=df.index).dt.date
    ms = pd.to_numeric(df[name], errors="coerce").where(
        lambda s: (s > -6.2e13) & (s < 4.1e12))
    with np.errstate(all="ignore"):
        return pd.to_datetime(ms.astype("Int64"), unit="ms", errors="coerce").dt.date


def _money(df: pd.DataFrame, name: str) -> pd.Series:
    if name not in df.columns:
        return pd.Series([None] * len(df), index=df.index, dtype="float64")
    s = df[name].astype(str).str.replace(r"[\$,]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")


def _num(df: pd.DataFrame, name: str) -> pd.Series:
    if name not in df.columns:
        return pd.Series([None] * len(df), index=df.index, dtype="float64")
    return pd.to_numeric(df[name], errors="coerce")


def _pick(df: pd.DataFrame, name: str):
    return df[name] if name in df.columns else None


def _frame(city: str, mapping: Dict[str, object]) -> pd.DataFrame:
    out = pd.DataFrame(mapping)
    out["city"] = city
    for c in COLUMNS:
        if c not in out.columns:
            out[c] = None
    return out[COLUMNS]


def _cached(city: str, fetcher: Callable[[], pd.DataFrame], limit: Optional[int]) -> pd.DataFrame:
    cache = RAW_DIR / f"{city}.parquet"
    if cache.exists() and limit is None:
        return pd.read_parquet(cache)
    df = fetcher()
    if limit is None:
        df.to_parquet(cache, index=False)
    return df


# --------------------------------- per-city loaders

def load_sf(limit: Optional[int] = None) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.sfgov.org/resource/i98e-djp9.json",
                        where="filed_date IS NOT NULL", limit=limit)
        if raw.empty:
            return _frame("sf", {})
        addr = (_col(raw, "street_number") + " " + _col(raw, "street_name") +
                " " + _col(raw, "street_suffix")).str.strip()
        return _frame("sf", {
            "permit_id": _pick(raw, "permit_number"),
            "address": addr,
            "parcel_id": _col(raw, "block") + "/" + _col(raw, "lot"),
            "permit_type": _pick(raw, "permit_type_definition"),
            "permit_subtype": _pick(raw, "proposed_use"),
            "use_code": _pick(raw, "proposed_occupancy"),
            "status": _pick(raw, "status"),
            "filed_date": _dt(raw, "filed_date"),
            "first_action_date": _dt(raw, "permit_creation_date"),
            "plan_check_start_date": _dt(raw, "filed_date"),
            "plan_check_end_date": _dt(raw, "approved_date"),
            "approval_date": _dt(raw, "approved_date"),
            "issued_date": _dt(raw, "issued_date"),
            "finaled_date": _dt(raw, "last_permit_activity_date"),
            "valuation_usd": _money(raw, "revised_cost").fillna(_money(raw, "estimated_cost")),
            "unit_count": _num(raw, "proposed_units"),
            "neighborhood": _pick(raw, "neighborhoods_analysis_boundaries"),
        })
    return _cached("sf", fetch, limit)


def load_nyc(limit: Optional[int] = None) -> pd.DataFrame:
    """NYC legacy BIS — per-stage (pre_filing / paid / fully_paid / approved /
    fully_permitted / signoff). Dates are MM/DD/YYYY strings."""
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
                        where="pre__filing_date IS NOT NULL", limit=limit)
        if raw.empty:
            return _frame("nyc", {})
        fmt = "%m/%d/%Y"
        addr = (_col(raw, "house__").str.strip() + " " +
                _col(raw, "street_name").str.strip() + ", " + _col(raw, "borough"))
        return _frame("nyc", {
            "permit_id": _col(raw, "job__") + "-" + _col(raw, "doc__"),
            "address": addr,
            "parcel_id": _pick(raw, "bin__"),
            "permit_type": _pick(raw, "job_type"),
            "permit_subtype": _pick(raw, "building_class"),
            "use_code": _col(raw, "proposed_occupancy").where(
                _col(raw, "proposed_occupancy") != "", _col(raw, "existing_occupancy")),
            "status": _pick(raw, "job_status_descrp"),
            "filed_date": _dt(raw, "pre__filing_date", fmt=fmt),
            "first_action_date": _dt(raw, "paid", fmt=fmt),
            "plan_check_start_date": _dt(raw, "fully_paid", fmt=fmt),
            "plan_check_end_date": _dt(raw, "approved", fmt=fmt),
            "approval_date": _dt(raw, "approved", fmt=fmt),
            "issued_date": _dt(raw, "fully_permitted", fmt=fmt),
            "finaled_date": _dt(raw, "signoff_date", fmt=fmt),
            "valuation_usd": _money(raw, "initial_cost"),
            "square_feet": _num(raw, "total_construction_floor_area"),
            "unit_count": _num(raw, "proposed_dwelling_units"),
            "neighborhood": _pick(raw, "gis_nta_name"),
        })
    return _cached("nyc", fetch, limit)


def load_la(limit: Optional[int] = None) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.lacity.org/resource/gwh9-jnip.json", limit=limit)
        if raw.empty:
            return _frame("la", {})
        return _frame("la", {
            "permit_id": _pick(raw, "permit_nbr"),
            "address": _pick(raw, "primary_address"),
            "parcel_id": _pick(raw, "apn"),
            "permit_type": _pick(raw, "permit_type"),
            "permit_subtype": _pick(raw, "permit_sub_type"),
            "use_code": _pick(raw, "use_desc"),
            "status": _pick(raw, "status_desc"),
            "filed_date": _dt(raw, "submitted_date"),
            "first_action_date": _dt(raw, "submitted_date"),
            "plan_check_start_date": _dt(raw, "submitted_date"),
            "plan_check_end_date": _dt(raw, "issue_date"),
            "approval_date": _dt(raw, "issue_date"),
            "issued_date": _dt(raw, "issue_date"),
            "finaled_date": _dt(raw, "cofo_date"),
            "valuation_usd": _num(raw, "valuation"),
            "square_feet": _num(raw, "square_footage"),
            "unit_count": _num(raw, "du_changed"),
            "neighborhood": _pick(raw, "cpa"),
        })
    return _cached("la", fetch, limit)


def load_chicago(limit: Optional[int] = None) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.cityofchicago.org/resource/ydr8-5enu.json",
                        where="application_start_date IS NOT NULL", limit=limit)
        if raw.empty:
            return _frame("chicago", {})
        addr = (_col(raw, "street_number") + " " + _col(raw, "street_direction") +
                " " + _col(raw, "street_name")).str.strip()
        permit_id = _col(raw, "permit_").where(_col(raw, "permit_") != "", _col(raw, "id"))
        return _frame("chicago", {
            "permit_id": permit_id,
            "address": addr,
            "permit_type": _pick(raw, "permit_type"),
            "permit_subtype": _pick(raw, "review_type"),
            "filed_date": _dt(raw, "application_start_date"),
            "first_action_date": _dt(raw, "application_start_date"),
            "plan_check_start_date": _dt(raw, "application_start_date"),
            "plan_check_end_date": _dt(raw, "issue_date"),
            "approval_date": _dt(raw, "issue_date"),
            "issued_date": _dt(raw, "issue_date"),
            "valuation_usd": _num(raw, "reported_cost"),
            "neighborhood": _pick(raw, "community_area"),
        })
    return _cached("chicago", fetch, limit)


def load_austin(limit: Optional[int] = None) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.austintexas.gov/resource/3syk-w9eu.json",
                        where="applieddate IS NOT NULL", limit=limit)
        if raw.empty:
            return _frame("austin", {})
        return _frame("austin", {
            "permit_id": _pick(raw, "permit_number"),
            "address": _pick(raw, "original_address1"),
            "parcel_id": _pick(raw, "tcad_id"),
            "permit_type": _pick(raw, "permit_type_desc"),
            "permit_subtype": _pick(raw, "permit_class"),
            "use_code": _pick(raw, "work_class"),
            "status": _pick(raw, "status_current"),
            "filed_date": _dt(raw, "applieddate"),
            "first_action_date": _dt(raw, "applieddate"),
            "plan_check_start_date": _dt(raw, "applieddate"),
            "plan_check_end_date": _dt(raw, "issue_date"),
            "approval_date": _dt(raw, "issue_date"),
            "issued_date": _dt(raw, "issue_date"),
            "finaled_date": _dt(raw, "statusdate"),
            "neighborhood": _pick(raw, "council_district"),
        })
    return _cached("austin", fetch, limit)


def load_seattle(limit: Optional[int] = None) -> pd.DataFrame:
    """Seattle Plan Review has one row per (permit x reviewtype x cycle);
    collapse to one per permit for the shared schema. The per-cycle detail is
    still reachable directly via tqk8-y2z5 when needed."""
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.seattle.gov/resource/tqk8-y2z5.json", limit=limit)
        if raw.empty:
            return _frame("seattle", {})
        agg = raw.groupby("permitnum", dropna=False).agg(
            applieddate=("applieddate", "min"),
            planreviewcompletedate=("planreviewcompletedate", "max"),
            readyissuedate=("readyissuedate", "max"),
            issueddate=("issueddate", "max"),
            permitclass=("permitclass", "last"),
            permittypedesc=("permittypedesc", "last"),
            permittypemapped=("permittypemapped", "last"),
            housingunits=("housingunits", "last"),
            housingcategory=("housingcategory", "last"),
            zoning=("zoning", "last"),
            originaladdress1=("originaladdress1", "last"),
        ).reset_index()
        return _frame("seattle", {
            "permit_id": agg["permitnum"],
            "address": agg["originaladdress1"],
            "permit_type": agg["permittypemapped"],
            "permit_subtype": agg["permitclass"],
            "use_code": agg["permittypedesc"],
            "status": agg["housingcategory"],
            "filed_date": _dt(agg, "applieddate"),
            "first_action_date": _dt(agg, "applieddate"),
            "plan_check_start_date": _dt(agg, "applieddate"),
            "plan_check_end_date": _dt(agg, "planreviewcompletedate"),
            "approval_date": _dt(agg, "readyissuedate"),
            "issued_date": _dt(agg, "issueddate"),
            "unit_count": _num(agg, "housingunits"),
            "neighborhood": agg["zoning"],
        })
    return _cached("seattle", fetch, limit)


def load_portland(limit: Optional[int] = None) -> pd.DataFrame:
    base = ("https://www.portlandmaps.com/arcgis/rest/services/Public/"
            "BDS_Permit/FeatureServer/22")

    def fetch() -> pd.DataFrame:
        raw = _arcgis_get(base, where="1=1", limit=limit)
        if raw.empty:
            return _frame("portland", {})
        addr = (_col(raw, "HOUSE").str.strip() + " " + _col(raw, "DIRECTION") +
                " " + _col(raw, "PROPSTREET") + " " + _col(raw, "STREETTYPE")).str.strip()
        val = _num(raw, "SUBMITTEDVALUATION").fillna(_num(raw, "FINALVALUATION"))
        return _frame("portland", {
            "permit_id": _pick(raw, "APPLICATION"),
            "address": addr,
            "parcel_id": _pick(raw, "STATEIDKEY"),
            "permit_type": _pick(raw, "PERMIT"),
            "permit_subtype": _pick(raw, "TYPE"),
            "use_code": _pick(raw, "OCCUPANCYGROUP"),
            "status": _pick(raw, "STATUS"),
            "filed_date": _ms_dt(raw, "CREATEDATE"),
            "first_action_date": _ms_dt(raw, "CREATEDATE"),
            "plan_check_start_date": _ms_dt(raw, "INTAKECOMPLETEDATE"),
            "plan_check_end_date": _ms_dt(raw, "ISSUED"),
            "approval_date": _ms_dt(raw, "ISSUED"),
            "issued_date": _ms_dt(raw, "ISSUED"),
            "finaled_date": _ms_dt(raw, "FINALED"),
            "valuation_usd": val,
            "square_feet": _num(raw, "TOTALSQFT"),
            "unit_count": _num(raw, "NUMNEWUNITS"),
            "neighborhood": _pick(raw, "NEIGHBORHOOD"),
        })
    return _cached("portland", fetch, limit)


# --------------------------------- full historical re-pulls (Phase 2 sampling fix)
#
# The default loaders above rely on Socrata's implicit ordering and a 150k cap
# per city, which under the hood pulls newest-first and starves the historical
# tail (SF's 2018–2023 slow era is the worst offender).
#
# The *_full loaders below paginate explicitly with $order=<date_field> ASC and a
# year-range $where filter (target 2015-01-01 → today), with per-pull row
# budgets large enough that the slow eras survive. They cache to
# data/raw/<city>_full.parquet and are called via build_clean_dataset_v2 /
# build_clean_cache_v2 in model.py + evaluate.py.

def _full_cached(city: str, fetcher: Callable[[], pd.DataFrame],
                 force: bool = False) -> pd.DataFrame:
    cache = RAW_DIR / f"{city}_full.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)
    df = fetcher()
    df.to_parquet(cache, index=False)
    return df


def load_sf_full(force: bool = False, row_budget: int = 1_500_000) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get("https://data.sfgov.org/resource/i98e-djp9.json",
                        where="filed_date >= '2015-01-01T00:00:00'",
                        order="filed_date ASC",
                        limit=row_budget,
                        progress_label="sf_full")
        if raw.empty:
            return _frame("sf", {})
        addr = (_col(raw, "street_number") + " " + _col(raw, "street_name") +
                " " + _col(raw, "street_suffix")).str.strip()
        return _frame("sf", {
            "permit_id": _pick(raw, "permit_number"),
            "address": addr,
            "parcel_id": _col(raw, "block") + "/" + _col(raw, "lot"),
            "permit_type": _pick(raw, "permit_type_definition"),
            "permit_subtype": _pick(raw, "proposed_use"),
            "use_code": _pick(raw, "proposed_occupancy"),
            "status": _pick(raw, "status"),
            "filed_date": _dt(raw, "filed_date"),
            "first_action_date": _dt(raw, "permit_creation_date"),
            "plan_check_start_date": _dt(raw, "filed_date"),
            "plan_check_end_date": _dt(raw, "approved_date"),
            "approval_date": _dt(raw, "approved_date"),
            "issued_date": _dt(raw, "issued_date"),
            "finaled_date": _dt(raw, "last_permit_activity_date"),
            "valuation_usd": _money(raw, "revised_cost").fillna(_money(raw, "estimated_cost")),
            "unit_count": _num(raw, "proposed_units"),
            "neighborhood": _pick(raw, "neighborhoods_analysis_boundaries"),
        })
    return _full_cached("sf", fetch, force=force)


def load_nyc_full(force: bool = False, row_budget_each: int = 1_000_000) -> pd.DataFrame:
    """Union of legacy BIS (ic3t-wcy2, 2015+) and DOB NOW (w9ak-ipjd, 2020+).

    Legacy BIS is the SLOW era historically; DOB NOW carries post-2020.
    """
    def fetch() -> pd.DataFrame:
        fmt = "%m/%d/%Y"
        print("    [nyc_full] legacy BIS (ic3t-wcy2)")
        # BIS stores pre__filing_date as a TEXT column (MM/DD/YYYY), so neither
        # range filtering nor date ordering is supported. Pull year-by-year
        # using `$where=pre__filing_date like '%/YYYY'`.
        bis_parts: List[pd.DataFrame] = []
        per_year_cap = max(1, row_budget_each // 12)
        for year in range(2015, 2027):
            yr_df = _soda_get(
                "https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
                where=f"pre__filing_date like '%/{year}'",
                limit=per_year_cap,
                progress_label=f"nyc_bis_{year}",
            )
            bis_parts.append(yr_df)
        bis_raw = pd.concat(bis_parts, ignore_index=True) if bis_parts else pd.DataFrame()
        if not bis_raw.empty:
            bis_addr = (_col(bis_raw, "house__").str.strip() + " " +
                        _col(bis_raw, "street_name").str.strip() + ", " + _col(bis_raw, "borough"))
            bis_df = _frame("nyc", {
                "permit_id": _col(bis_raw, "job__") + "-" + _col(bis_raw, "doc__"),
                "address": bis_addr,
                "parcel_id": _pick(bis_raw, "bin__"),
                "permit_type": _pick(bis_raw, "job_type"),
                "permit_subtype": _pick(bis_raw, "building_class"),
                "use_code": _col(bis_raw, "proposed_occupancy").where(
                    _col(bis_raw, "proposed_occupancy") != "", _col(bis_raw, "existing_occupancy")),
                "status": _pick(bis_raw, "job_status_descrp"),
                "filed_date": _dt(bis_raw, "pre__filing_date", fmt=fmt),
                "first_action_date": _dt(bis_raw, "paid", fmt=fmt),
                "plan_check_start_date": _dt(bis_raw, "fully_paid", fmt=fmt),
                "plan_check_end_date": _dt(bis_raw, "approved", fmt=fmt),
                "approval_date": _dt(bis_raw, "approved", fmt=fmt),
                "issued_date": _dt(bis_raw, "fully_permitted", fmt=fmt),
                "finaled_date": _dt(bis_raw, "signoff_date", fmt=fmt),
                "valuation_usd": _money(bis_raw, "initial_cost"),
                "square_feet": _num(bis_raw, "total_construction_floor_area"),
                "unit_count": _num(bis_raw, "proposed_dwelling_units"),
                "neighborhood": _pick(bis_raw, "gis_nta_name"),
            })
        else:
            bis_df = _frame("nyc", {})
        print(f"    [nyc_full] BIS rows={len(bis_df):,}")

        print("    [nyc_full] DOB NOW (w9ak-ipjd)")
        try:
            dn_raw = _soda_get(
                "https://data.cityofnewyork.us/resource/w9ak-ipjd.json",
                where="filing_date >= '2020-01-01T00:00:00'",
                order="filing_date ASC",
                limit=row_budget_each,
                progress_label="nyc_dob_now",
            )
        except requests.HTTPError:
            dn_raw = pd.DataFrame()
        if not dn_raw.empty:
            # DOB NOW schema. Column names vary but these are documented in data_sources.md.
            dn_df = _frame("nyc", {
                "permit_id": _pick(dn_raw, "job_filing_number"),
                "address": _col(dn_raw, "house_no") + " " + _col(dn_raw, "street_name"),
                "permit_type": _pick(dn_raw, "job_type"),
                "permit_subtype": _pick(dn_raw, "work_on_floor"),
                "use_code": _pick(dn_raw, "occupancy_classification"),
                "status": _pick(dn_raw, "filing_status"),
                "filed_date": _dt(dn_raw, "filing_date"),
                "first_action_date": _dt(dn_raw, "filing_date"),
                "plan_check_start_date": _dt(dn_raw, "filing_date"),
                "plan_check_end_date": _dt(dn_raw, "approved_date"),
                "approval_date": _dt(dn_raw, "approved_date"),
                "issued_date": _dt(dn_raw, "first_permit_date"),
                "finaled_date": _dt(dn_raw, "signoff_date"),
                "valuation_usd": _num(dn_raw, "initial_cost"),
                "unit_count": _num(dn_raw, "proposed_no_of_stories"),
                "neighborhood": _pick(dn_raw, "borough"),
            })
        else:
            dn_df = _frame("nyc", {})
        print(f"    [nyc_full] DOB NOW rows={len(dn_df):,}")
        return pd.concat([bis_df, dn_df], ignore_index=True) if not (bis_df.empty and dn_df.empty) else _frame("nyc", {})
    return _full_cached("nyc", fetch, force=force)


def load_la_full(force: bool = False, row_budget: int = 1_500_000) -> pd.DataFrame:
    """Union of current gwh9-jnip (2020+) and historical dyxf-7hc4 (2010-2019)."""
    def fetch() -> pd.DataFrame:
        print("    [la_full] LADBS current (gwh9-jnip)")
        cur_raw = _soda_get(
            "https://data.lacity.org/resource/gwh9-jnip.json",
            where="submitted_date >= '2015-01-01T00:00:00'",
            order="submitted_date ASC",
            limit=row_budget,
            progress_label="la_current",
        )
        print("    [la_full] LADBS historical (dyxf-7hc4)")
        try:
            hist_raw = _soda_get(
                "https://data.lacity.org/resource/dyxf-7hc4.json",
                where="submitted_date >= '2015-01-01T00:00:00'",
                order="submitted_date ASC",
                limit=row_budget,
                progress_label="la_hist",
            )
        except requests.HTTPError:
            hist_raw = pd.DataFrame()
        raw = pd.concat([cur_raw, hist_raw], ignore_index=True) if not hist_raw.empty else cur_raw
        if raw.empty:
            return _frame("la", {})
        return _frame("la", {
            "permit_id": _pick(raw, "permit_nbr"),
            "address": _pick(raw, "primary_address"),
            "parcel_id": _pick(raw, "apn"),
            "permit_type": _pick(raw, "permit_type"),
            "permit_subtype": _pick(raw, "permit_sub_type"),
            "use_code": _pick(raw, "use_desc"),
            "status": _pick(raw, "status_desc"),
            "filed_date": _dt(raw, "submitted_date"),
            "first_action_date": _dt(raw, "submitted_date"),
            "plan_check_start_date": _dt(raw, "submitted_date"),
            "plan_check_end_date": _dt(raw, "issue_date"),
            "approval_date": _dt(raw, "issue_date"),
            "issued_date": _dt(raw, "issue_date"),
            "finaled_date": _dt(raw, "cofo_date"),
            "valuation_usd": _num(raw, "valuation"),
            "square_feet": _num(raw, "square_footage"),
            "unit_count": _num(raw, "du_changed"),
            "neighborhood": _pick(raw, "cpa"),
        })
    return _full_cached("la", fetch, force=force)


def load_chicago_full(force: bool = False, row_budget: int = 1_500_000) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get(
            "https://data.cityofchicago.org/resource/ydr8-5enu.json",
            where="application_start_date >= '2015-01-01T00:00:00'",
            order="application_start_date ASC",
            limit=row_budget,
            progress_label="chicago_full",
        )
        if raw.empty:
            return _frame("chicago", {})
        addr = (_col(raw, "street_number") + " " + _col(raw, "street_direction") +
                " " + _col(raw, "street_name")).str.strip()
        permit_id = _col(raw, "permit_").where(_col(raw, "permit_") != "", _col(raw, "id"))
        return _frame("chicago", {
            "permit_id": permit_id,
            "address": addr,
            "permit_type": _pick(raw, "permit_type"),
            "permit_subtype": _pick(raw, "review_type"),
            "use_code": _pick(raw, "work_description"),
            "filed_date": _dt(raw, "application_start_date"),
            "first_action_date": _dt(raw, "application_start_date"),
            "plan_check_start_date": _dt(raw, "application_start_date"),
            "plan_check_end_date": _dt(raw, "issue_date"),
            "approval_date": _dt(raw, "issue_date"),
            "issued_date": _dt(raw, "issue_date"),
            "valuation_usd": _num(raw, "reported_cost"),
            "neighborhood": _pick(raw, "community_area"),
        })
    return _full_cached("chicago", fetch, force=force)


def load_austin_full(force: bool = False, row_budget: int = 1_500_000) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        raw = _soda_get(
            "https://data.austintexas.gov/resource/3syk-w9eu.json",
            where="applieddate >= '2015-01-01T00:00:00'",
            order="applieddate ASC",
            limit=row_budget,
            progress_label="austin_full",
        )
        if raw.empty:
            return _frame("austin", {})
        return _frame("austin", {
            "permit_id": _pick(raw, "permit_number"),
            "address": _pick(raw, "original_address1"),
            "parcel_id": _pick(raw, "tcad_id"),
            "permit_type": _pick(raw, "permit_type_desc"),
            "permit_subtype": _pick(raw, "permit_class"),
            "use_code": _pick(raw, "work_class"),
            "status": _pick(raw, "status_current"),
            "filed_date": _dt(raw, "applieddate"),
            "first_action_date": _dt(raw, "applieddate"),
            "plan_check_start_date": _dt(raw, "applieddate"),
            "plan_check_end_date": _dt(raw, "issue_date"),
            "approval_date": _dt(raw, "issue_date"),
            "issued_date": _dt(raw, "issue_date"),
            "finaled_date": _dt(raw, "statusdate"),
            "square_feet": _num(raw, "total_new_sqft"),
            "unit_count": _num(raw, "total_new_units"),
            "neighborhood": _pick(raw, "council_district"),
        })
    return _full_cached("austin", fetch, force=force)


def load_seattle_full(force: bool = False, row_budget: int = 1_500_000) -> pd.DataFrame:
    """Seattle Plan Review (tqk8-y2z5) — one row per (permit x reviewtype x cycle).

    Unlike the other *_full loaders, this one does NOT collapse down to one row
    per permit. It preserves the per-cycle granularity needed for the Phase 2.5
    stage-level decomposition. The data_loaders.load_seattle loader already
    performs the per-permit aggregation for the shared schema; this loader is
    for the Seattle-only decomposition task.
    """
    def fetch() -> pd.DataFrame:
        raw = _soda_get(
            "https://data.seattle.gov/resource/tqk8-y2z5.json",
            where="applieddate IS NOT NULL",
            order="applieddate ASC",
            limit=row_budget,
            progress_label="seattle_full",
        )
        return raw  # return raw — DO NOT collapse; that's the whole point
    cache = RAW_DIR / "seattle_full.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)
    df = fetch()
    df.to_parquet(cache, index=False)
    return df


FULL_LOADERS: Dict[str, Callable[..., pd.DataFrame]] = {
    "sf": load_sf_full,
    "nyc": load_nyc_full,
    "la": load_la_full,
    "chicago": load_chicago_full,
    "austin": load_austin_full,
    "seattle": load_seattle_full,
}


# --------------------------------- smoke test

LOADERS: Dict[str, Callable[..., pd.DataFrame]] = {
    "sf": load_sf, "nyc": load_nyc, "la": load_la, "chicago": load_chicago,
    "austin": load_austin, "seattle": load_seattle, "portland": load_portland,
}

CRITICAL = ["filed_date", "issued_date", "plan_check_end_date", "permit_subtype"]


def smoke(limit: int = 1000) -> None:
    for name, fn in LOADERS.items():
        try:
            df = fn(limit=limit)
        except Exception as exc:  # noqa: BLE001
            print(f"{name:9s}  ERROR: {type(exc).__name__}: {exc}")
            continue
        print(f"{name:9s}  rows={len(df):6d}  cols={len(df.columns)}  "
              f"city={df['city'].iloc[0] if len(df) else '-'}")
        for col in CRITICAL:
            frac = df[col].isna().mean() if len(df) else 1.0
            print(f"            null[{col:22s}] = {frac:5.1%}")


if __name__ == "__main__":
    smoke(limit=1000)
