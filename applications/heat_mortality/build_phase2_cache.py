"""Build a Phase 2 extended weekly feature cache from the hourly ISD parquets.

Reads the existing Phase 0.5 master (``data/clean/heat_mortality_master.parquet``)
and each per-city hourly ISD parquet (``data/raw/isd/{city}_*.parquet``).
For every (city, iso_week) computes all Phase 2 atmospheric features that
need hourly-level inputs:

- ``tw_night_c_p95``              weekly 95th percentile of night-hour Tw
- ``tw_night_c_min``              weekly min of per-day night-max Tw
- ``tropical_night_count_week``   count of days with Tmin >= 20 C
- ``tropical_night_count_tw22``   count of nights with night-max Tw >= 22
- ``consecutive_nights_tw_above_24_count``  streak of consecutive nights
- ``tw_night_max_roll3d``         weekly max of rolling-3-day night-Tw-max
- ``tw_degree_hours_above_26``    sum over hours of max(0, tw - 26)
- ``tw_degree_hours_above_24``    same for 24 C threshold
- ``tw_night_c_max_nw22``         night-window 22->06 variant (H011 wider)
- ``tw_night_c_max_nw02``         narrow 02->06 variant (H012)
- ``tmin_c_min``                  weekly min of daily Tmin (for tropical-night)
- ``tmax_c_p95_daily``            weekly 95th pct of daily Tmax
- ``compound_days_count``         days with Tmax >= p90 AND Tmin >= p90
- ``compound_tw_days_count``      days with day-tw >= p90(day-tw) AND night-tw >= p90(night-tw)
- ``hwmi_daily_sum``              weekly sum of HWMI daily magnitudes
- ``hw_p95_3d_flag``              weekly flag: 3 consecutive days >= city p95 Tmax
- ``euroheat_flag``               weekly flag: 2 consecutive days Tmax >= p90 and Tmin >= p90
- ``hw_fixed_35_3d_flag``         weekly flag: 3 consecutive days Tmax >= 35 C
- ``hobday_atm_flag``             weekly flag: 5 consecutive days Tmax >= calendar-day p90

Writes ``data/clean/heat_mortality_phase2.parquet`` which is the Phase 0.5
master JOIN extras.

Run once before phase2_runner.py. Deterministic. Re-runnable.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from data_loaders import CITIES, _iso_week_start, _utc_offset, compute_wet_bulb  # noqa: E402

RAW_ISD = HERE / "data" / "raw" / "isd"
CLEAN_DIR = HERE / "data" / "clean"
MASTER_PATH = CLEAN_DIR / "heat_mortality_master.parquet"
EXT_PATH = CLEAN_DIR / "heat_mortality_phase2.parquet"


def _run_lengths(mask: np.ndarray) -> np.ndarray:
    """Return, for each index i, the length of the current true-streak ending at i."""
    out = np.zeros(len(mask), dtype=np.int64)
    cur = 0
    for i, v in enumerate(mask):
        cur = cur + 1 if v else 0
        out[i] = cur
    return out


def _has_consec(mask: np.ndarray, n: int) -> np.ndarray:
    """Per-index boolean: some window ending within this period has >= n consecutive trues."""
    streak = _run_lengths(mask)
    return streak >= n


def build_city_features(city: str, df_hourly: pd.DataFrame) -> pd.DataFrame:
    """Produce a weekly frame with every Phase 2 hourly-derived feature."""
    if df_hourly.empty:
        return pd.DataFrame()
    c = CITIES[city]
    off = _utc_offset(c)
    h = df_hourly.copy()
    h["local_time"] = h["datetime_utc"] + pd.to_timedelta(off, unit="h")
    h["local_date"] = h["local_time"].dt.normalize()
    h["local_hour"] = h["local_time"].dt.hour

    # night masks
    h["is_night_06"] = h["local_hour"] < 6              # default 00->06
    h["is_night_22_06"] = (h["local_hour"] >= 22) | (h["local_hour"] < 6)  # wide
    h["is_night_02_06"] = (h["local_hour"] >= 2) & (h["local_hour"] < 6)   # narrow

    # Daily aggregates
    daily = h.groupby("local_date").agg(
        tmax_c=("t2m_c", "max"),
        tmin_c=("t2m_c", "min"),
        tavg_c=("t2m_c", "mean"),
        tdew_c=("td2m_c", "mean"),
        tw_c_daily_max=("tw_c", "max"),
        tw_c_daily_mean=("tw_c", "mean"),
    ).reset_index()
    # Night-window daily aggregates (00-06)
    night = h[h["is_night_06"]].groupby("local_date").agg(
        tw_night_max_06=("tw_c", "max"),
        tw_night_mean_06=("tw_c", "mean"),
    ).reset_index()
    night22 = h[h["is_night_22_06"]].groupby("local_date").agg(
        tw_night_max_2206=("tw_c", "max"),
        tw_night_mean_2206=("tw_c", "mean"),
    ).reset_index()
    night02 = h[h["is_night_02_06"]].groupby("local_date").agg(
        tw_night_max_0206=("tw_c", "max"),
        tw_night_mean_0206=("tw_c", "mean"),
    ).reset_index()

    daily = daily.merge(night, on="local_date", how="left")
    daily = daily.merge(night22, on="local_date", how="left")
    daily = daily.merge(night02, on="local_date", how="left")
    daily["iso_week_start"] = _iso_week_start(daily["local_date"])
    daily = daily.sort_values("local_date").reset_index(drop=True)

    # calendar-day percentile for Hobday — per day-of-year, full-panel
    daily["doy"] = daily["local_date"].dt.dayofyear
    doy_p90 = daily.groupby("doy")["tmax_c"].transform(lambda s: s.quantile(0.90))
    daily["_above_doy_p90"] = (daily["tmax_c"] >= doy_p90).to_numpy()

    # Per-city absolute thresholds (for Tang / EuroHEAT)
    city_tmax_p90 = daily["tmax_c"].quantile(0.90)
    city_tmax_p95 = daily["tmax_c"].quantile(0.95)
    city_tmin_p90 = daily["tmin_c"].quantile(0.90)
    city_twd_p90 = daily["tw_c_daily_max"].quantile(0.90)
    city_twnight_p90 = daily["tw_night_max_06"].quantile(0.90)

    daily["_tmax_above_p90"] = (daily["tmax_c"] >= city_tmax_p90).to_numpy()
    daily["_tmax_above_p95"] = (daily["tmax_c"] >= city_tmax_p95).to_numpy()
    daily["_tmin_above_p90"] = (daily["tmin_c"] >= city_tmin_p90).to_numpy()
    daily["_compound_day"] = (daily["_tmax_above_p90"] & daily["_tmin_above_p90"]).to_numpy()
    daily["_compound_tw_day"] = (
        (daily["tw_c_daily_max"] >= city_twd_p90)
        & (daily["tw_night_max_06"].fillna(-99) >= city_twnight_p90)
    ).to_numpy()
    daily["_tmax_above_35"] = (daily["tmax_c"] >= 35.0).to_numpy()
    daily["_night_above_24"] = (daily["tw_night_max_06"].fillna(-99) >= 24.0).to_numpy()
    daily["_tropical_night"] = (daily["tmin_c"] >= 20.0).to_numpy()
    daily["_tropical_night_tw22"] = (daily["tw_night_max_06"].fillna(-99) >= 22.0).to_numpy()

    # Streaks on the sorted daily frame
    daily["_compound_streak"] = _run_lengths(daily["_compound_day"].to_numpy())
    daily["_tmax_p95_streak"] = _run_lengths(daily["_tmax_above_p95"].to_numpy())
    daily["_tmax_p90_and_tmin_p90_streak"] = _run_lengths(daily["_compound_day"].to_numpy())
    daily["_tmax_fixed35_streak"] = _run_lengths(daily["_tmax_above_35"].to_numpy())
    daily["_hobday_streak"] = _run_lengths(daily["_above_doy_p90"].to_numpy())
    daily["_night_above_24_streak"] = _run_lengths(daily["_night_above_24"].to_numpy())

    # HWMI daily magnitude (Russo 2014 simplified): daily value above city p25
    # of summer Tmax, normalised by (p75 - p25) over summer days.
    summer = daily[daily["local_date"].dt.month.isin([6, 7, 8])]
    if len(summer) > 10:
        p25, p75 = summer["tmax_c"].quantile([0.25, 0.75])
        denom = max(p75 - p25, 1e-3)
        daily["_hwmi"] = np.clip((daily["tmax_c"] - p25) / denom, 0, None).to_numpy()
    else:
        daily["_hwmi"] = 0.0

    # tw degree-hours per day
    dh_above = h.groupby("local_date").agg(
        tw_dh_26=("tw_c", lambda s: float(np.clip(s - 26.0, 0, None).sum())),
        tw_dh_24=("tw_c", lambda s: float(np.clip(s - 24.0, 0, None).sum())),
        tw_night_p95=("tw_c", lambda s: float(np.nanpercentile(s.dropna(), 95)) if s.notna().any() else np.nan),
    ).reset_index()
    daily = daily.merge(dh_above, on="local_date", how="left")

    # Rolling 3-day night-Tw-max peak (using night 00-06)
    daily["tw_night_max_roll3d"] = (
        daily["tw_night_max_06"].rolling(3, min_periods=1).max()
    )

    # Week-level aggregation
    wk = daily.groupby("iso_week_start").agg(
        tw_night_c_p95=("tw_night_p95", "mean"),
        tw_night_c_min=("tw_night_max_06", "min"),
        tmin_c_min=("tmin_c", "min"),
        tmax_c_p95_daily=("tmax_c", "max"),
        tropical_night_count_week=("_tropical_night", "sum"),
        tropical_night_count_tw22=("_tropical_night_tw22", "sum"),
        consecutive_nights_tw_above_24_count=("_night_above_24_streak", "max"),
        tw_degree_hours_above_26=("tw_dh_26", "sum"),
        tw_degree_hours_above_24=("tw_dh_24", "sum"),
        tw_night_max_roll3d=("tw_night_max_roll3d", "max"),
        compound_days_count=("_compound_day", "sum"),
        compound_tw_days_count=("_compound_tw_day", "sum"),
        hwmi_daily_sum=("_hwmi", "sum"),
        tw_night_c_max_nw22=("tw_night_max_2206", "max"),
        tw_night_c_mean_nw22=("tw_night_mean_2206", "mean"),
        tw_night_c_max_nw02=("tw_night_max_0206", "max"),
        tw_night_c_mean_nw02=("tw_night_mean_0206", "mean"),
        tang_compound_2d_flag=("_compound_day", lambda s: int(_has_consec(s.to_numpy(), 2).any())),
        compound_3d_flag=("_compound_day", lambda s: int(_has_consec(s.to_numpy(), 3).any())),
        hw_p95_3d_flag=("_tmax_p95_streak", lambda s: int((s >= 3).any())),
        euroheat_flag=("_compound_streak", lambda s: int((s >= 2).any())),
        hw_fixed_35_3d_flag=("_tmax_fixed35_streak", lambda s: int((s >= 3).any())),
        hobday_atm_flag=("_hobday_streak", lambda s: int((s >= 5).any())),
    ).reset_index()
    wk["city"] = city
    return wk


def main() -> None:
    if not MASTER_PATH.exists():
        raise FileNotFoundError(f"{MASTER_PATH} missing — run evaluate.py --build-cache first")
    master = pd.read_parquet(MASTER_PATH)
    master["iso_week_start"] = pd.to_datetime(master["iso_week_start"])

    extras: Dict[str, pd.DataFrame] = {}
    t_all = time.time()
    for city in sorted(master["city"].unique()):
        t0 = time.time()
        # pick the widest ISD cache for that city
        candidates = sorted(RAW_ISD.glob(f"{city}_*_2013_2024.parquet"))
        if not candidates:
            candidates = sorted(RAW_ISD.glob(f"{city}_*.parquet"))
        if not candidates:
            print(f"  {city}: no ISD cache — skipping")
            continue
        df_h = pd.read_parquet(candidates[-1])
        wk = build_city_features(city, df_h)
        extras[city] = wk
        print(f"  {city:<14} rows_h={len(df_h):>6} rows_w={len(wk):>4} "
              f"dt={time.time()-t0:4.1f}s")

    if not extras:
        raise RuntimeError("no extras built")
    ext = pd.concat(extras.values(), ignore_index=True)
    ext["iso_week_start"] = pd.to_datetime(ext["iso_week_start"])
    print(f"extras total rows: {len(ext)} "
          f"wall={time.time()-t_all:.1f}s")

    joined = master.merge(ext, on=["city", "iso_week_start"], how="left")
    print(f"joined rows: {len(joined)}  master={len(master)}  extras={len(ext)}")

    # Lag-1/2/3 weekly features for DLNM-ish surrogates
    joined = joined.sort_values(["city", "iso_week_start"]).reset_index(drop=True)
    for col in [
        "tw_c_mean", "tw_c_max",
        "tw_night_c_max", "tw_night_c_mean",
        "tmax_c_mean", "tmin_c_mean",
    ]:
        if col in joined.columns:
            for lag in (1, 2, 3, 4):
                joined[f"{col}_lag{lag}"] = joined.groupby("city")[col].shift(lag)
    # Rolling 4-week peak (lagged 1 week to avoid leakage)
    joined["tw_night_c_max_roll4w"] = (
        joined.groupby("city")["tw_night_c_max"]
        .shift(1)
        .rolling(4, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
    )

    # Prior-week pscore (H057)
    joined["prior_week_pscore"] = joined.groupby("city")["p_score"].shift(1)
    joined["prior_4w_mean_pscore"] = (
        joined.groupby("city")["p_score"]
        .shift(1)
        .rolling(4, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    joined.to_parquet(EXT_PATH, index=False)
    print(f"wrote {EXT_PATH}  cols={joined.shape[1]}")


if __name__ == "__main__":
    main()
