"""Data loaders for the Iberian wildfire VLF prediction project.

Loads real data from:
1. EFFIS/GWIS weekly fire statistics (fires + burned area per country-week)
2. GlobFire regional fire counts (subnational monthly)
3. MCD64A1 regional burned area by land cover (subnational monthly)

All data are REAL, downloaded from the GWIS country profile API
(api2.effis.emergency.copernicus.eu) and the GWIS S3 data archive.

Usage:
    from data_loaders import load_effis_weekly, build_modelling_dataset
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
RAW_DIR = DATA_DIR / "raw"


# ---------------------------------------------------------------- EFFIS weekly
def load_effis_weekly(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Load the EFFIS weekly fire statistics for Portugal and Spain.

    Each row is one (country, year, week) observation with:
        - fires: number of fire events detected that week
        - area_ha: total burned area (hectares) that week
        - fires_avg / fires_max / area_ha_avg / area_ha_max: historical stats
    """
    if data_dir is None:
        data_dir = DATA_DIR
    path = data_dir / "effis_weekly.parquet"
    if path.exists():
        return pd.read_parquet(path)
    # Build from raw JSON files
    return _build_effis_weekly_from_raw(data_dir)


def _build_effis_weekly_from_raw(data_dir: Path) -> pd.DataFrame:
    """Parse weekly JSON files into a single DataFrame."""
    raw_dir = data_dir / "raw"
    rows = []
    for country in ["PRT", "ESP"]:
        for year in range(2006, 2027):
            fpath = raw_dir / f"weekly_{country}_{year}.json"
            if not fpath.exists():
                continue
            with open(fpath) as f:
                data = json.load(f)
            for entry in data["banfweekly"]:
                rows.append({
                    "country": country,
                    "year": year,
                    "week": entry["week"],
                    "fires": entry["events"],
                    "area_ha": entry["area_ha"],
                    "fires_avg": entry["events_avg"],
                    "fires_max": entry["events_max"],
                    "area_ha_avg": entry["area_ha_avg"],
                    "area_ha_max": entry["area_ha_max"],
                })
    df = pd.DataFrame(rows)
    out_path = data_dir / "effis_weekly.parquet"
    df.to_parquet(out_path, index=False)
    return df


# ---------------------------------------------------------------- GlobFire regional
def load_globfire_iberia(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Load GlobFire subnational monthly fire counts for Iberia."""
    if data_dir is None:
        data_dir = DATA_DIR
    path = data_dir / "globfire_iberia.parquet"
    if path.exists():
        return pd.read_parquet(path)
    # Fall back to CSV
    csv_path = data_dir / "raw" / "GLOBFIRE_burned_area_full_dataset_2002_2024.csv"
    df = pd.read_csv(csv_path, sep=";")
    iberia = df[df["gid_0"].isin(["PRT", "ESP"])].copy()
    iberia.to_parquet(path, index=False)
    return iberia


# ---------------------------------------------------------------- MCD64A1 regional
def load_mcd64a1_iberia(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Load MCD64A1 MODIS burned area by land cover for Iberia."""
    if data_dir is None:
        data_dir = DATA_DIR
    path = data_dir / "mcd64a1_iberia.parquet"
    if path.exists():
        return pd.read_parquet(path)
    csv_path = data_dir / "raw" / "MCD64A1_burned_area_full_dataset_2002_2024.csv"
    df = pd.read_csv(csv_path, sep=";")
    iberia = df[df["gid_0"].isin(["PRT", "ESP"])].copy()
    iberia["total_ba"] = iberia[
        ["forest", "savannas", "shrublands_grasslands", "croplands", "other"]
    ].sum(axis=1)
    iberia.to_parquet(path, index=False)
    return iberia


# ---------------------------------------------------------------- VLF labelling

# VLF definition: a country-week where total burned area > 5000 ha.
# EFFIS data only includes fires detectable by MODIS (~30 ha minimum),
# so the "fires" field counts only substantial fires. A total weekly
# burned area of 5000 ha indicates at least one very large fire (VLF),
# consistent with EFFIS VLF definition (individual fire > 500 ha).
# This gives a VLF rate of ~13% of fire-season country-weeks.
VLF_AREA_THRESHOLD = 5000  # ha total
VLF_MIN_FIRES = 1


def label_vlf_week(df: pd.DataFrame) -> np.ndarray:
    """Binary label: 1 if this country-week contains VLF activity.

    A week is labelled VLF if total burned area exceeds 5000 ha
    with at least 1 detected fire event.
    """
    fires = df["fires"].values.astype(float)
    area = df["area_ha"].values.astype(float)
    vlf = (area > VLF_AREA_THRESHOLD) & (fires >= VLF_MIN_FIRES)
    return vlf.astype(np.int64)


# ---------------------------------------------------------------- feature engineering

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute modelling features from the EFFIS weekly data.

    Features built from the data itself (no external climate data needed
    for baseline -- climate features added in Phase 2):
        - month, month_sin, month_cos: seasonal cycle
        - fires_ratio: fires this week / historical average
        - area_ratio: area this week / historical average
        - fires_prev: fires in previous week (same country)
        - area_prev: area in previous week
        - fires_2wk: fires in previous 2 weeks
        - area_2wk: area in previous 2 weeks
        - fires_4wk: fires in previous 4 weeks
        - area_4wk: area in previous 4 weeks
        - country_pt: binary indicator (Portugal = 1, Spain = 0)
        - log_area_avg: log(1 + historical average area)
        - log_fires_avg: log(1 + historical average fires)
        - year_trend: linear year trend (centered)
        - cum_area_ytd: cumulative area year-to-date
        - cum_fires_ytd: cumulative fires year-to-date
        - is_fire_season: 1 if week 22-42 (Jun-Oct)
        - fire_season_week: week number within fire season (0 outside)
    """
    out = df.copy()
    out = out.sort_values(["country", "year", "week"]).reset_index(drop=True)

    # Month from week number (approximate)
    out["month"] = np.clip((out["week"] * 7 - 3) // 30 + 1, 1, 12).astype(float)
    out["month_sin"] = np.sin(2 * np.pi * out["month"] / 12.0)
    out["month_cos"] = np.cos(2 * np.pi * out["month"] / 12.0)

    # Ratios vs historical average
    out["fires_ratio"] = out["fires"] / out["fires_avg"].clip(lower=0.1)
    out["area_ratio"] = out["area_ha"] / out["area_ha_avg"].clip(lower=0.1)

    # Lagged features (within same country)
    for lag in [1, 2, 4]:
        out[f"fires_lag{lag}"] = out.groupby("country")["fires"].shift(lag).fillna(0)
        out[f"area_lag{lag}"] = out.groupby("country")["area_ha"].shift(lag).fillna(0)

    # Rolling sums
    for window in [2, 4]:
        out[f"fires_{window}wk"] = (
            out.groupby("country")["fires"]
            .rolling(window, min_periods=1)
            .sum()
            .reset_index(level=0, drop=True)
            .shift(1)
            .fillna(0)
        )
        out[f"area_{window}wk"] = (
            out.groupby("country")["area_ha"]
            .rolling(window, min_periods=1)
            .sum()
            .reset_index(level=0, drop=True)
            .shift(1)
            .fillna(0)
        )

    # Country indicator
    out["country_pt"] = (out["country"] == "PRT").astype(float)

    # Log-transformed historical averages
    out["log_area_avg"] = np.log1p(out["area_ha_avg"].clip(lower=0))
    out["log_fires_avg"] = np.log1p(out["fires_avg"].clip(lower=0))

    # Year trend (centered on 2018)
    out["year_trend"] = (out["year"] - 2018).astype(float)

    # Cumulative year-to-date
    out["cum_area_ytd"] = out.groupby(["country", "year"])["area_ha"].cumsum()
    out["cum_fires_ytd"] = out.groupby(["country", "year"])["fires"].cumsum()

    # Fire season indicator
    out["is_fire_season"] = ((out["week"] >= 22) & (out["week"] <= 42)).astype(float)
    out["fire_season_week"] = np.where(
        out["is_fire_season"] == 1, out["week"] - 22, 0
    ).astype(float)

    # Week number (cyclical)
    out["week_sin"] = np.sin(2 * np.pi * out["week"] / 52.0)
    out["week_cos"] = np.cos(2 * np.pi * out["week"] / 52.0)

    # Fill any remaining NaN
    for col in out.select_dtypes(include=["float64", "float32", "int64"]).columns:
        if out[col].isna().any():
            out[col] = out[col].fillna(0.0)

    return out


# ---------------------------------------------------------------- feature lists

BASELINE_FEATURES = [
    "month_sin", "month_cos",
    "week_sin", "week_cos",
    "fires_avg", "area_ha_avg",
    "fires_max", "area_ha_max",
    "log_area_avg", "log_fires_avg",
    "fires_ratio", "area_ratio",
    "fires_lag1", "area_lag1",
    "fires_lag2", "area_lag2",
    "fires_2wk", "area_2wk",
    "fires_4wk", "area_4wk",
    "country_pt",
    "year_trend",
    "cum_area_ytd", "cum_fires_ytd",
    "is_fire_season", "fire_season_week",
]


# Phase 2 adds these (from MCD64A1 land cover analysis)
PHASE2_EXTRA_FEATURES = [
    "forest_frac",       # fraction of burned area that is forest
    "shrub_frac",        # fraction that is shrubland/grassland
    "fires_lag4",        # longer lag
    "area_lag4",         # longer lag
]


def build_modelling_dataset(
    data_dir: Optional[Path] = None,
    min_year: int = 2012,
    max_year: int = 2025,
) -> pd.DataFrame:
    """Load EFFIS weekly data, add features, and label VLF weeks.

    Returns a DataFrame with features + target ready for modelling.
    Only includes weeks from fire-active months (April-November).
    """
    df = load_effis_weekly(data_dir)
    df = df[(df["year"] >= min_year) & (df["year"] <= max_year)].copy()

    # Add features
    df = add_features(df)

    # Label VLF
    df["vlf"] = label_vlf_week(df)

    # Filter to fire-relevant weeks (15-48, roughly Apr-Nov)
    df = df[(df["week"] >= 15) & (df["week"] <= 48)].copy()

    return df.reset_index(drop=True)


def add_land_cover_features(df: pd.DataFrame,
                            data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Merge MCD64A1 land-cover fractions onto the weekly panel.

    Computes per (country, year, month) the fraction of total burned area
    that was forest vs shrubland/grassland, then merges onto the weekly data.
    """
    if data_dir is None:
        data_dir = DATA_DIR

    mcd = load_mcd64a1_iberia(data_dir)
    # Map gid_0 to country code
    mcd["country"] = mcd["gid_0"]

    # Aggregate by country-year-month
    agg = mcd.groupby(["country", "year", "month"]).agg(
        forest=("forest", "sum"),
        shrub=("shrublands_grasslands", "sum"),
        total=("total_ba", "sum"),
    ).reset_index()
    agg["forest_frac"] = agg["forest"] / agg["total"].clip(lower=0.1)
    agg["shrub_frac"] = agg["shrub"] / agg["total"].clip(lower=0.1)

    # Merge onto weekly data using approximate month
    out = df.copy()
    if "month" not in out.columns:
        out["month"] = np.clip((out["week"] * 7 - 3) // 30 + 1, 1, 12).astype(float)
    out["_merge_month"] = out["month"].astype(int)
    out["_merge_year"] = out["year"].astype(int)

    merged = out.merge(
        agg[["country", "year", "month", "forest_frac", "shrub_frac"]].rename(
            columns={"year": "_merge_year", "month": "_merge_month"}
        ),
        on=["country", "_merge_year", "_merge_month"],
        how="left",
    )
    merged["forest_frac"] = merged["forest_frac"].fillna(0.0)
    merged["shrub_frac"] = merged["shrub_frac"].fillna(0.0)
    merged = merged.drop(columns=["_merge_month", "_merge_year"])
    return merged
