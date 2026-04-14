"""Data loaders for the housing-crash prediction project.

Three primary datasets:
- Zillow ZHVI metro (wide → long)
- Realtor.com inventory metro (already long)
- FRED weekly 30-year mortgage rate (resample to monthly)

All return DataFrames keyed on (cbsa_code, month) where possible.
Zillow uses its own RegionID which we crosswalk to CBSA via a name-match on
"City, ST" format.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"


# -------- Zillow ZHVI --------

def load_zhvi_long(path: Path | str = None) -> pd.DataFrame:
    """Return long-format ZHVI: columns [region_id, region_name, state, month, zhvi]."""
    path = Path(path) if path else DATA / "zillow_zhvi_metro.csv"
    df = pd.read_csv(path)
    # Drop the "United States" aggregate row (RegionType='country')
    df = df[df["RegionType"] == "msa"].copy()
    id_cols = ["RegionID", "SizeRank", "RegionName", "StateName"]
    month_cols = [c for c in df.columns if re.match(r"\d{4}-\d{2}-\d{2}", c)]
    long = df.melt(id_vars=id_cols, value_vars=month_cols,
                   var_name="month", value_name="zhvi")
    long["month"] = pd.to_datetime(long["month"]).dt.to_period("M").dt.to_timestamp()
    long = long.dropna(subset=["zhvi"])
    long = long.rename(columns={"RegionID": "zillow_region_id",
                                 "RegionName": "metro_name",
                                 "StateName": "state",
                                 "SizeRank": "size_rank"})
    return long[["zillow_region_id", "size_rank", "metro_name", "state", "month", "zhvi"]]


# -------- Realtor.com --------

def load_realtor(path: Path | str = None) -> pd.DataFrame:
    """Return Realtor.com metro-month panel, minus redundant MoM/YoY columns."""
    path = Path(path) if path else DATA / "realtor_inventory_metro.csv"
    df = pd.read_csv(path)
    # Parse YYYYMM → month-start timestamp
    df["month"] = pd.to_datetime(df["month_date_yyyymm"].astype(str), format="%Y%m")
    # Keep base measures (drop _mm, _yy, _share derivatives — we'll recompute cleanly)
    keep = ["month", "cbsa_code", "cbsa_title",
            "median_listing_price", "active_listing_count",
            "median_days_on_market", "new_listing_count",
            "price_increased_count", "price_reduced_count",
            "pending_listing_count", "median_square_feet", "total_listing_count"]
    keep = [c for c in keep if c in df.columns]
    out = df[keep].copy()
    out["cbsa_code"] = out["cbsa_code"].astype(str)
    return out


# -------- FRED 30-year mortgage rate --------

def load_mortgage_30yr_monthly(path: Path | str = None) -> pd.DataFrame:
    """Weekly FRED series → month-end average."""
    path = Path(path) if path else DATA / "fred_mortgage_30yr.csv"
    df = pd.read_csv(path)
    df.columns = ["date", "mortgage_30yr"]
    df["date"] = pd.to_datetime(df["date"])
    df["mortgage_30yr"] = pd.to_numeric(df["mortgage_30yr"], errors="coerce")
    df = df.set_index("date").sort_index()
    monthly = df.resample("MS")["mortgage_30yr"].mean().rename("mortgage_30yr").reset_index()
    monthly = monthly.rename(columns={"date": "month"})
    return monthly


# -------- CBSA crosswalk (Zillow name → CBSA code) --------

_STATE_SUFFIX_RE = re.compile(r",\s*([A-Z]{2}(?:-[A-Z]{2})*)$")


def normalize_metro_name(name: str) -> str:
    """Return the city portion of 'City, ST' or 'City-City2, ST1-ST2'."""
    if not isinstance(name, str):
        return ""
    s = _STATE_SUFFIX_RE.sub("", name).strip().lower()
    # Standardise common variants
    s = s.replace(" metropolitan area", "")
    s = s.replace("-", " ")
    return re.sub(r"\s+", " ", s).strip()


def crosswalk_zillow_to_cbsa(zhvi: pd.DataFrame, realtor: pd.DataFrame) -> pd.DataFrame:
    """Name-match Zillow metros to Realtor cbsa_code via normalised first-city.

    Precision-biased: only 1:1 unique matches are accepted. Reports match
    rate so we know how much coverage we actually have.
    """
    z = zhvi[["zillow_region_id", "metro_name"]].drop_duplicates("zillow_region_id").copy()
    z["_norm"] = z["metro_name"].apply(normalize_metro_name)

    r = realtor[["cbsa_code", "cbsa_title"]].drop_duplicates("cbsa_code").copy()
    r["_norm"] = r["cbsa_title"].apply(normalize_metro_name)

    # many-to-many on normalized name (rare, but some cities appear in multiple states)
    merged = z.merge(r, on="_norm", how="inner")
    # Keep only names that map 1:1 in BOTH directions
    name_to_cbsa_count = merged.groupby("_norm")["cbsa_code"].nunique()
    name_to_zillow_count = merged.groupby("_norm")["zillow_region_id"].nunique()
    unambiguous = name_to_cbsa_count[name_to_cbsa_count == 1].index.intersection(
        name_to_zillow_count[name_to_zillow_count == 1].index)
    merged = merged[merged["_norm"].isin(unambiguous)]
    return merged[["zillow_region_id", "cbsa_code", "metro_name", "cbsa_title"]]
