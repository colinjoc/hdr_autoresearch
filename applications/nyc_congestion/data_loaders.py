"""NYC congestion charge data loaders — real data from NYC Open Data, MTA, TLC.

Data sources:
  - NYC DOT Automated Traffic Volume Counts (Socrata API, dataset 7ym2-wayt)
  - MTA Daily Ridership Data (data.ny.gov, dataset vxuj-8kew, through Jan 2025)
  - MTA Next-Day Ridership (data.ny.gov, dataset sayj-mze2, through Apr 2026)
    Includes CRZ Entries (Congestion Relief Zone) and CBD Entries columns
  - NYC TLC Trip Record Data (parquet via CloudFront CDN)
  - Taxi Zone Lookup (TLC reference file)

All data is downloaded and cached locally. No synthetic data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Set

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

# Congestion pricing launch date
CHARGE_START = pd.Timestamp("2025-01-05")

# CBD = Manhattan below 60th Street. These taxi zone IDs correspond to that area.
# Derived from taxi_zone_lookup.csv — all Manhattan zones south of ~60th St.
_CBD_ZONE_IDS: Set[int] = {
    4, 12, 13, 24, 33, 34, 37, 41, 42, 43, 45, 48, 50, 52, 65, 68, 79, 87,
    88, 90, 100, 107, 113, 114, 125, 128, 137, 140, 141, 142, 143, 144, 148,
    151, 152, 153, 158, 161, 162, 163, 164, 170, 186, 194, 202, 209, 211, 224,
    229, 230, 231, 232, 233, 234, 236, 237, 239, 243, 244, 246, 249, 261, 262, 263,
}


def load_taxi_zones() -> pd.DataFrame:
    """Load taxi zone lookup CSV."""
    path = DATA_DIR / "taxi_zone_lookup.csv"
    df = pd.read_csv(path)
    return df


def get_cbd_zone_ids() -> Set[int]:
    """Return set of taxi zone IDs in the CBD (Manhattan below 60th St)."""
    return _CBD_ZONE_IDS.copy()


def load_traffic_counts() -> pd.DataFrame:
    """Load NYC DOT automated traffic volume counts from cached JSON files.

    Returns DataFrame with columns: boro, date, hour, vol, street, direction, segmentid.
    """
    frames = []
    # Load all traffic JSON files
    for path in sorted(DATA_DIR.glob("traffic_*.json")):
        if "p2" in path.name:
            continue  # skip pagination fragment (merged into _all)
        if "_all" in path.name or "2023_2026" in path.name:
            with open(path) as f:
                records = json.load(f)
            frames.append(pd.DataFrame(records))

    # Prefer merged _all file for Manhattan
    all_path = DATA_DIR / "traffic_manhattan_all.json"
    base_path = DATA_DIR / "traffic_manhattan_2023_2026.json"
    if all_path.exists():
        # Remove base if _all exists to avoid double counting
        frames = [fr for fr in frames
                  if not (fr["boro"].iloc[0] == "Manhattan" and len(fr) == 50000)]

    df = pd.concat(frames, ignore_index=True)

    # Type conversions
    df["yr"] = df["yr"].astype(int)
    df["m"] = df["m"].astype(int)
    df["d"] = df["d"].astype(int)
    df["hh"] = df["hh"].astype(int)
    df["vol"] = pd.to_numeric(df["vol"], errors="coerce").fillna(0).astype(int)
    df["date"] = pd.to_datetime(
        df[["yr", "m", "d"]].rename(columns={"yr": "year", "m": "month", "d": "day"}),
        errors="coerce",
    )
    df = df.dropna(subset=["date"])
    df = df.rename(columns={"hh": "hour", "segmentid": "segmentid"})

    keep_cols = ["boro", "date", "hour", "vol", "street", "direction", "segmentid"]
    return df[[c for c in keep_cols if c in df.columns]].copy()


def aggregate_daily_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly traffic counts to daily totals by borough."""
    daily = (
        df.groupby(["boro", "date"])["vol"]
        .sum()
        .reset_index()
    )
    return daily


def load_mta_ridership() -> pd.DataFrame:
    """Load MTA ridership from next-day dataset (sayj-mze2) which goes through 2026.

    Falls back to legacy CSV if JSON not available.
    Returns DataFrame with date, subway_ridership, bus_ridership, bridge_tunnel_traffic,
    crz_entries, cbd_entries columns (daily).
    """
    nextday_path = DATA_DIR / "mta_nextday_ridership.json"
    if nextday_path.exists():
        records = json.load(open(nextday_path))
        raw = pd.DataFrame(records)
        raw["date"] = pd.to_datetime(raw["date"])
        raw["count"] = pd.to_numeric(raw["count"], errors="coerce")

        # Pivot from long to wide: one row per date, modes as columns
        pivot = raw.pivot_table(index="date", columns="mode", values="count",
                                aggfunc="sum").reset_index()
        rename_map = {
            "Subway": "subway_ridership",
            "Bus": "bus_ridership",
            "BT": "bridge_tunnel_traffic",
            "CRZ Entries": "crz_entries",
            "CBD Entries": "cbd_entries",
            "LIRR": "lirr_ridership",
            "MNR": "metronorth_ridership",
            "SIR": "sir_ridership",
            "AAR": "aar_trips",
        }
        pivot = pivot.rename(columns=rename_map)
        pivot.columns.name = None
        return pivot

    # Fallback: legacy CSV
    path = DATA_DIR / "mta_daily_ridership.csv"
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    rename = {
        "Date": "date",
        "Subways: Total Estimated Ridership": "subway_ridership",
        "Buses: Total Estimated Ridership": "bus_ridership",
        "Bridges and Tunnels: Total Traffic": "bridge_tunnel_traffic",
        "LIRR: Total Estimated Ridership": "lirr_ridership",
        "Metro-North: Total Estimated Ridership": "metronorth_ridership",
    }
    df = df.rename(columns=rename)
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    for col in ["subway_ridership", "bus_ridership", "bridge_tunnel_traffic",
                "lirr_ridership", "metronorth_ridership"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def aggregate_mta_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate MTA daily ridership to weekly totals."""
    df = df.copy()
    df["week_start"] = df["date"].dt.to_period("W-SUN").apply(lambda x: x.start_time)
    numeric_cols = ["subway_ridership", "bus_ridership", "bridge_tunnel_traffic",
                    "lirr_ridership", "metronorth_ridership"]
    numeric_cols = [c for c in numeric_cols if c in df.columns]
    weekly = df.groupby("week_start")[numeric_cols].sum().reset_index()
    return weekly


def _summarize_tlc_file(path: Path, period: str) -> pd.DataFrame:
    """Summarize a single TLC parquet file into CBD vs outer pickup/dropoff counts."""
    df = pd.read_parquet(path, columns=["PULocationID", "DOLocationID"])
    cbd = _CBD_ZONE_IDS

    cbd_pickups = int(df["PULocationID"].isin(cbd).sum())
    cbd_dropoffs = int(df["DOLocationID"].isin(cbd).sum())
    outer_pickups = int((~df["PULocationID"].isin(cbd)).sum())
    outer_dropoffs = int((~df["DOLocationID"].isin(cbd)).sum())
    total = len(df)

    return pd.DataFrame([{
        "period": period,
        "total_trips": total,
        "cbd_pickups": cbd_pickups,
        "cbd_dropoffs": cbd_dropoffs,
        "outer_pickups": outer_pickups,
        "outer_dropoffs": outer_dropoffs,
        "cbd_pickup_share": cbd_pickups / total if total > 0 else 0,
        "cbd_dropoff_share": cbd_dropoffs / total if total > 0 else 0,
        "file": path.name,
    }])


def load_tlc_summary() -> pd.DataFrame:
    """Summarize TLC trip records into pre/post CBD vs outer borough counts."""
    frames = []
    for path in sorted(DATA_DIR.glob("yellow_*.parquet")):
        # Parse year-month from filename
        parts = path.stem.split("_")
        year_month = f"{parts[-2]}-{parts[-1]}"
        period = "pre" if year_month < "2025-01" else "post"
        frames.append(_summarize_tlc_file(path, period))

    for path in sorted(DATA_DIR.glob("green_*.parquet")):
        parts = path.stem.split("_")
        year_month = f"{parts[-2]}-{parts[-1]}"
        period = "pre" if year_month < "2025-01" else "post"
        frames.append(_summarize_tlc_file(path, period))

    for path in sorted(DATA_DIR.glob("fhvhv_*.parquet")):
        parts = path.stem.split("_")
        year_month = f"{parts[-2]}-{parts[-1]}"
        period = "pre" if year_month < "2025-01" else "post"
        frames.append(_summarize_tlc_file(path, period))

    if not frames:
        return pd.DataFrame(columns=["period", "cbd_pickups", "cbd_dropoffs",
                                      "outer_pickups", "outer_dropoffs"])
    return pd.concat(frames, ignore_index=True)


def build_master_dataset() -> pd.DataFrame:
    """Build the weekly master dataset combining traffic counts, MTA, and TLC.

    Returns one row per (week_start, boro) with traffic volume, transit ridership,
    and the post_charge binary indicator.
    """
    # --- Traffic volumes: aggregate to weekly by borough ---
    traffic = load_traffic_counts()
    daily = aggregate_daily_volume(traffic)
    daily["week_start"] = daily["date"].dt.to_period("W-SUN").apply(
        lambda x: x.start_time
    )
    weekly_traffic = (
        daily.groupby(["boro", "week_start"])
        .agg(daily_vol_mean=("vol", "mean"), daily_vol_sum=("vol", "sum"),
             n_days=("vol", "count"))
        .reset_index()
    )

    # --- MTA ridership (city-wide, not per-borough) ---
    mta = load_mta_ridership()
    mta_weekly = aggregate_mta_weekly(mta)

    # --- Merge ---
    master = weekly_traffic.merge(mta_weekly, on="week_start", how="left")

    # --- Post-charge indicator ---
    master["post_charge"] = (master["week_start"] >= CHARGE_START).astype(int)

    # --- Time features ---
    master["week_num"] = master["week_start"].dt.isocalendar().week.astype(int)
    master["year"] = master["week_start"].dt.year
    master["month"] = master["week_start"].dt.month
    master["dow_start"] = master["week_start"].dt.dayofweek

    # --- Sort ---
    master = master.sort_values(["boro", "week_start"]).reset_index(drop=True)

    return master
