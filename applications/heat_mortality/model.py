"""Baseline + tournament model definitions for heat-wave excess mortality.

Phase 0.5 (baseline) and Phase 1 (5-family tournament) live here. The target
is weekly ``excess_deaths = deaths_all_cause - expected_baseline`` predicted
from a **strictly atmospheric** feature set that mimics what current heat-
health early-warning systems use. Notably ``tw_night_*`` (night-time wet-bulb)
is deliberately excluded — that is the Phase 2 hypothesis variable.

Follows the same patterns as ``applications/building_permits/model.py``:
- ``add_features(df)`` produces every column in ``BASELINE_FEATURES``
- ``build_clean_dataset(df)`` applies the Phase 0.5 filters (drop pandemic
  weeks, drop rows with missing target or key exposure)
- ``make_*`` factories for each tournament family
- ``BINARY_THRESHOLD`` + ``label_lethal_heatwave`` define the AUC/Brier target
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge

try:
    import lightgbm as lgb
    _HAS_LGB = True
except Exception:  # noqa: BLE001
    _HAS_LGB = False


# ---------------------------------------------------------------- city list
# Matches the verified 30-city inventory in data_loaders.CITIES — see
# data_acquisition_notes.md § "Cities to include — Phase 0.5 starter set".
CITIES_FOR_BASELINE: List[str] = [
    # US (CDC state-weekly target)
    "new_york", "los_angeles", "chicago", "houston", "phoenix",
    "las_vegas", "atlanta", "miami", "seattle", "boston",
    "san_diego", "dallas", "philadelphia", "denver", "st_louis",
    # EU (Eurostat NUTS-3 weekly target)
    "paris", "london", "madrid", "rome", "berlin",
    "milan", "athens", "lisbon", "bucharest", "vienna",
    "warsaw", "stockholm", "copenhagen", "dublin", "amsterdam",
]


# ---------------------------------------------------------------- feature set
# Atmospheric-only baseline. Explicitly excludes tw_night_c_mean / tw_night_c_max
# because those encode the headline Phase 2 hypothesis.
BASELINE_FEATURES: List[str] = [
    # daily aggregates of weekly window
    "tmax_c_mean",
    "tmax_c_max",
    "tmin_c_mean",
    "tavg_c",
    "tdew_c",
    "rh_pct",
    "tw_c_mean",            # DAY-averaged — no night/day split
    "tw_c_max",
    # heat-wave indicators
    "consecutive_days_above_p95_tmax",
    "tmax_anomaly_c",
    # calendar / cyclic
    "iso_year",
    "iso_month_sin", "iso_month_cos",
    # vulnerability proxies (city-level static)
    "log_population",
    "lat",
]

# One-hot city columns (populated in add_features).
CITY_ONEHOT = [f"city_{c}" for c in CITIES_FOR_BASELINE]

# Final matrix for modelling (baseline feature set + city one-hot).
BASELINE_FEATURES_WITH_CITY: List[str] = BASELINE_FEATURES + CITY_ONEHOT


# Rough (2023) city populations in millions for the log_population proxy. These
# are municipal / metro-proxy figures — good enough as a static vulnerability
# feature. See data_acquisition_notes.md for the rationale.
_CITY_POP_MILLIONS: dict = {
    "new_york": 8.3, "los_angeles": 3.9, "chicago": 2.7, "houston": 2.3,
    "phoenix": 1.6, "las_vegas": 0.65, "atlanta": 0.5, "miami": 0.45,
    "seattle": 0.75, "boston": 0.65, "san_diego": 1.4, "dallas": 1.3,
    "philadelphia": 1.6, "denver": 0.72, "st_louis": 0.30,
    "paris": 2.1, "london": 9.0, "madrid": 3.3, "rome": 2.8, "berlin": 3.7,
    "milan": 1.4, "athens": 0.66, "lisbon": 0.55, "bucharest": 1.8,
    "vienna": 2.0, "warsaw": 1.9, "stockholm": 1.0, "copenhagen": 0.66,
    "dublin": 0.60, "amsterdam": 0.92,
}


# ---------------------------------------------------------------- target defs

# A week is a "lethal heat-wave week" if (a) excess mortality is ≥10% above
# baseline AND (b) a heat-wave meteorological indicator fires. The second
# condition keeps the positive class meteorologically plausible and strips
# out the ~1-in-20 weeks where p_score > 0.1 purely from random noise
# (mid-winter respiratory wobbles, reporting lags, etc.).
#
# ``BINARY_HEAT_STREAK_WEEKS`` is the rolling-2-week sum of "this week's
# tmax ≥ city p90" computed inside ``add_features``; a value of 1 means
# at least one of the last two weeks was in the hot tail.
BINARY_P_SCORE_THRESHOLD: float = 0.10
BINARY_HEAT_STREAK_WEEKS: float = 1.0


def label_lethal_heatwave(df: pd.DataFrame) -> np.ndarray:
    """Binary label for the AUC/Brier target.

    A week is lethal if p_score ≥ 0.10 AND the heat-wave indicator
    (``consecutive_days_above_p95_tmax`` in the Phase 0.5 feature set) is
    ≥ 1, i.e. the current week's Tmax is in the city's hot tail. NaN
    p_scores become 0 (the baseline couldn't be computed, so we can't
    call it lethal).
    """
    p = df["p_score"].to_numpy(dtype="float64")
    streak = df.get("consecutive_days_above_p95_tmax",
                    pd.Series(np.zeros(len(df)))).to_numpy(dtype="float64")
    p_ok = np.where(np.isnan(p), 0.0, p) >= BINARY_P_SCORE_THRESHOLD
    streak_ok = streak >= BINARY_HEAT_STREAK_WEEKS
    return (p_ok & streak_ok).astype("int64")


# ---------------------------------------------------------------- clean filter

PANDEMIC_START = pd.Timestamp("2020-03-09")   # 2020-W11 Monday
PANDEMIC_END = pd.Timestamp("2022-06-27")     # 2022-W26 Monday

# Baseline feature columns must be non-null in the cleaned panel. We require
# tmax_c_mean, tw_c_mean, and the target (excess_deaths / expected_baseline).
REQUIRED_NON_NULL = [
    "excess_deaths",
    "expected_baseline",
    "tmax_c_mean",
    "tmin_c_mean",
    "tavg_c",
    "tw_c_mean",
]


def build_clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Phase 0.5 cleaning for the master (city × week) panel.

    Filters:
        1. Drop pandemic weeks (2020-W11..2022-W26) — kept available for Phase 2
        2. Drop rows with null excess_deaths / expected_baseline
        3. Drop rows with null core exposure columns (tmax_c_mean, tw_c_mean)
        4. Drop non-physical expected_baseline values (≤ 0)
        5. Clip extreme p_scores (|p| > 2.0) — these are data-entry artefacts
    """
    out = df.copy()
    out["iso_week_start"] = pd.to_datetime(out["iso_week_start"], errors="coerce")
    out = out[out["iso_week_start"].notna()].copy()

    # 1. Pandemic window.
    pandemic = (out["iso_week_start"] >= PANDEMIC_START) & \
               (out["iso_week_start"] <= PANDEMIC_END)
    out = out[~pandemic].copy()

    # 2-3. Required-non-null columns.
    for col in REQUIRED_NON_NULL:
        if col in out.columns:
            out = out[out[col].notna()].copy()

    # 4. Non-physical baselines.
    out = out[out["expected_baseline"] > 0].copy()

    # 5. Extreme P-scores.
    out = out[out["p_score"].abs() <= 2.0].copy()

    return out.reset_index(drop=True)


# ---------------------------------------------------------------- feature engine

def _compute_rh_from_t_td(t_c: pd.Series, td_c: pd.Series) -> pd.Series:
    """Relative humidity (%) from air temp + dewpoint via Magnus-Tetens."""
    a, b = 17.625, 243.04
    t = t_c.astype("float64")
    td = td_c.astype("float64")
    num = np.exp(a * td / (b + td))
    den = np.exp(a * t / (b + t))
    rh = 100.0 * num / den
    return rh.clip(lower=1.0, upper=100.0)


def _weekly_climatology_anomaly(df: pd.DataFrame, col: str,
                                 start_year: int = 1980,
                                 end_year: int = 2010) -> pd.Series:
    """Per-(city, iso_week) climatological anomaly.

    ``start_year`` / ``end_year`` bound the climatology window. If the panel
    has no data before ``end_year`` (e.g. our Phase 0.5 panel starts 2013),
    fall back to the **full-panel same-(city, iso_week) mean**. The Phase 0.5
    note is that the 1980-2010 reference will replace this once the ERA5 pull
    is wired up; until then the anomaly is a within-panel de-meaning.
    """
    t = df[[col]].copy()
    t["city"] = df["city"].values
    t["iso_year"] = pd.to_datetime(df["iso_week_start"]).dt.isocalendar().year
    t["iso_week"] = pd.to_datetime(df["iso_week_start"]).dt.isocalendar().week

    ref = t[(t["iso_year"] >= start_year) & (t["iso_year"] <= end_year)]
    if len(ref) == 0:
        ref = t  # fall back to whole panel

    clim = ref.groupby(["city", "iso_week"])[col].mean().rename("clim")
    merged = t.merge(clim.reset_index(), on=["city", "iso_week"], how="left")
    return (t[col].values - merged["clim"].values)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Produce every column in ``BASELINE_FEATURES`` on the cleaned panel.

    Input columns expected (produced by ``data_loaders.build_master_dataset``):
        - city, iso_week_start
        - tmax_c_mean, tmin_c_mean, tavg_c, tdew_c
        - tw_c_mean, tw_c_max
        - consecutive_days_above_p95 (renamed to *_tmax)
        - lat
        - deaths_all_cause, expected_baseline, excess_deaths, p_score
    """
    out = df.copy()

    # tmax_c_max: we only have tmax_c_mean in the current aggregator; the
    # loader stores the *weekly mean of daily Tmax* as tmax_c_mean. Approximate
    # tmax_c_max as tmax_c_mean + 0.5 * (tmax_c_mean - tmin_c_mean) when
    # unavailable (rough headroom), and overwrite with the true value if
    # the aggregator begins to emit it. This keeps the feature list stable
    # across iterations.
    if "tmax_c_max" not in out.columns:
        diurnal = out["tmax_c_mean"].astype("float64") - out["tmin_c_mean"].astype("float64")
        out["tmax_c_max"] = out["tmax_c_mean"].astype("float64") + 0.5 * diurnal.clip(lower=0)

    # Relative humidity from T + Td.
    if "rh_pct" not in out.columns:
        out["rh_pct"] = _compute_rh_from_t_td(out["tavg_c"], out["tdew_c"])

    # Heat-wave indicator derived from the loader's ``consecutive_days_above_p95``
    # when populated. That column is only computed if ``aggregate_hourly_to_weekly``
    # was given a ``p95_threshold`` (rare in Phase 0.5), so we fall back to a
    # **per-city weekly-Tmax p90** indicator: the number of recent weeks whose
    # ``tmax_c_mean`` exceeds the city-specific 90th percentile.
    if "consecutive_days_above_p95_tmax" not in out.columns:
        src = pd.to_numeric(
            out.get("consecutive_days_above_p95", pd.Series(np.zeros(len(out)))),
            errors="coerce",
        ).fillna(0)
        if src.max() > 0:
            out["consecutive_days_above_p95_tmax"] = src
        else:
            # Per-city Tmax p90 -> binary indicator per week. Then rolling
            # sum over 2 weeks to get a "weeks above p90 in the last 14 days"
            # proxy. This matches the spirit of "consecutive hot weeks".
            tmax = out["tmax_c_mean"].astype("float64")
            out["_city_p90"] = tmax.groupby(out["city"]).transform(
                lambda s: s.quantile(0.90)
            )
            above = (tmax >= out["_city_p90"]).astype("float64")
            # 2-week rolling sum per city.
            out = out.sort_values(["city", "iso_week_start"]).reset_index(drop=True)
            out["consecutive_days_above_p95_tmax"] = (
                above.groupby(out["city"]).transform(
                    lambda s: s.rolling(2, min_periods=1).sum()
                )
            )
            out = out.drop(columns=["_city_p90"])

    # Tmax anomaly vs 1980-2010 climatology — falls back to within-panel
    # per-(city, iso_week) de-meaning until ERA5 is wired up.
    if "tmax_anomaly_c" not in out.columns:
        out["tmax_anomaly_c"] = _weekly_climatology_anomaly(out, "tmax_c_mean")

    # Calendar features.
    wk = pd.to_datetime(out["iso_week_start"])
    iso = wk.dt.isocalendar()
    out["iso_year"] = iso.year.astype("float64")
    month = wk.dt.month.astype("float64")
    out["iso_month_sin"] = np.sin(2 * np.pi * month / 12.0)
    out["iso_month_cos"] = np.cos(2 * np.pi * month / 12.0)

    # Population proxy (log millions).
    pop = out["city"].map(_CITY_POP_MILLIONS).astype("float64")
    out["log_population"] = np.log1p(pop.fillna(pop.median() if pop.notna().any() else 1.0))

    # Lat — ensure present.
    if "lat" not in out.columns or out["lat"].isna().all():
        raise ValueError("missing lat column in input dataset")
    out["lat"] = pd.to_numeric(out["lat"], errors="coerce")

    # City one-hot.
    for c in CITIES_FOR_BASELINE:
        out[f"city_{c}"] = (out["city"].astype(str) == c).astype("float64")

    # Fill remaining NaNs in feature columns with column medians (trees are
    # fine but Ridge can't consume NaN). Only impute the feature matrix cells.
    for col in BASELINE_FEATURES:
        if col not in out.columns:
            out[col] = np.nan
        if out[col].dtype.kind in "fi":
            med = out[col].median()
            out[col] = out[col].fillna(med if not np.isnan(med) else 0.0)

    return out


# ---------------------------------------------------------------- Phase 2 features

def add_phase2_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute every Phase 2 atmospheric feature on the cleaned panel.

    Most columns come straight from ``data/clean/heat_mortality_phase2.parquet``
    (see ``build_phase2_cache.py``); a handful are derived in pandas here so
    they only exist on the modelling side and don't bloat the cache.

    All features are deterministic and depend only on columns already present
    in the input ``df``.
    """
    out = df.copy()

    # ----- Theme 1 — night-time wet-bulb derived ---------------------------
    # H005: day-night Tw spread
    if {"tw_c_max", "tw_night_c_mean"}.issubset(out.columns):
        out["tw_day_night_spread_c"] = (
            pd.to_numeric(out["tw_c_max"], errors="coerce")
            - pd.to_numeric(out["tw_night_c_mean"], errors="coerce")
        )

    # H008: city p95 anomaly of tw_night_c_max
    if "tw_night_c_max" in out.columns:
        p95 = out.groupby("city")["tw_night_c_max"].transform(lambda s: s.quantile(0.95))
        out["tw_night_c_max_p95_anomaly"] = out["tw_night_c_max"] - p95
    # H009: city p90 anomaly of tw_night_c_mean
    if "tw_night_c_mean" in out.columns:
        p90 = out.groupby("city")["tw_night_c_mean"].transform(lambda s: s.quantile(0.90))
        out["tw_night_c_mean_p90_anomaly"] = out["tw_night_c_mean"] - p90
    # H010: city z-score of tw_night_c_max
    if "tw_night_c_max" in out.columns:
        mu = out.groupby("city")["tw_night_c_max"].transform("mean")
        sd = out.groupby("city")["tw_night_c_max"].transform("std").replace(0, np.nan)
        out["tw_night_c_max_zscore_city"] = (out["tw_night_c_max"] - mu) / sd
        out["tw_night_c_max_zscore_city"] = out["tw_night_c_max_zscore_city"].fillna(0.0)

    # H019: tw_compound_flag (any compound tw day in week)
    if "compound_tw_days_count" in out.columns:
        out["tw_compound_flag"] = (out["compound_tw_days_count"] >= 2).astype("float64")

    # H016/H017/H059: vulnerability interactions (no AC/age data — skip;
    # interaction with log_population as a structural moderator instead)
    if {"tw_night_c_max", "log_population"}.issubset(out.columns):
        out["tw_night_c_max_x_logpop"] = out["tw_night_c_max"] * out["log_population"]
    if {"tw_night_c_max", "lat"}.issubset(out.columns):
        out["tw_night_c_max_x_lat"] = out["tw_night_c_max"] * out["lat"]

    # ----- Theme 3 — compound day-night --------------------------------------
    if {"tmax_c_mean", "tmin_c_mean"}.issubset(out.columns):
        out["tmax_x_tmin"] = out["tmax_c_mean"] * out["tmin_c_mean"]
    if "compound_days_count" in out.columns:
        out["heatwave_type_ordinal"] = np.where(
            out["compound_days_count"].fillna(0) >= 2, 3,
            np.where(out["compound_days_count"].fillna(0) >= 1, 2, 0),
        ).astype("float64")
    # H032: 4-week lagged compound days count (uses prior weeks)
    if "compound_days_count" in out.columns:
        out["compound_days_4w_lag"] = (
            out.groupby("city")["compound_days_count"]
            .shift(1)
            .rolling(4, min_periods=1)
            .sum()
            .reset_index(level=0, drop=True)
        )

    # ----- Theme 4 — heat-wave definition variants ---------------------------
    if "hwmi_daily_sum" in out.columns:
        out["hwmi_daily"] = out["hwmi_daily_sum"]
    if {"hw_p95_3d_flag", "euroheat_flag", "hw_fixed_35_3d_flag"}.issubset(out.columns):
        out["hw_majority_vote"] = (
            (out["hw_p95_3d_flag"] + out["euroheat_flag"] + out["hw_fixed_35_3d_flag"]) >= 2
        ).astype("float64")

    # ----- Theme 5 — acclimatisation -----------------------------------------
    if "tw_c_mean" in out.columns:
        # Per-city minimum-mortality temperature proxy = city p75 of tw_c_mean
        # (literature MMT is at p75-85 of climatology). Compute and centre.
        p75 = out.groupby("city")["tw_c_mean"].transform(lambda s: s.quantile(0.75))
        out["tw_c_mean_minus_city_mmt"] = out["tw_c_mean"] - p75
        out["mmt_percentile_city"] = (
            out.groupby("city")["tw_c_mean"].rank(pct=True).fillna(0.5)
        )
    if "iso_year" in out.columns and "tw_c_mean" in out.columns:
        out["tw_c_mean_x_year_index"] = (
            out["tw_c_mean"] * (out["iso_year"] - 2013).clip(lower=0)
        )

    # ----- Theme 6 — lag structure -------------------------------------------
    # H046: 2-day rolling tmax max within the week (use lag-1 weekly tmax_max)
    if "tmax_c_max" in out.columns:
        out["tmax_max2d_week"] = np.maximum(
            out["tmax_c_max"],
            out.groupby("city")["tmax_c_max"].shift(1).fillna(out["tmax_c_max"]),
        )
    # H047/48/49: 0-2/0-3/0-4 weekly Tw rolling means (≈14/21/28-day windows)
    if "tw_c_mean" in out.columns:
        for nweek, name in [(2, "tw_rolling_14d_mean"),
                            (3, "tw_rolling_21d_mean"),
                            (4, "tw_rolling_28d_mean")]:
            out[name] = (
                out.groupby("city")["tw_c_mean"]
                .rolling(nweek, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
            )

    # ----- Theme 7 — vulnerability moderators (data-available subset) --------
    # H057: prior_week_pscore is in the cache; clip and impute median
    # H058: prior_4w_mean_pscore likewise
    for col in ("prior_week_pscore", "prior_4w_mean_pscore"):
        if col in out.columns:
            med = out[col].median()
            out[col] = out[col].fillna(med if not np.isnan(med) else 0.0)

    # ----- Theme 8/9/etc — categorical or composite moderators ---------------
    # H066: country fixed effects (one-hot)
    if "country" in out.columns:
        for cn in ("US", "FR", "GB", "ES", "IT", "DE", "GR", "PT", "RO",
                   "AT", "PL", "SE", "DK", "IE", "NL"):
            out[f"country_{cn}"] = (out["country"] == cn).astype("float64")

    # ----- Theme 17 — calendar -----------------------------------------------
    wk = pd.to_datetime(out["iso_week_start"])
    iso_week = wk.dt.isocalendar().week.astype("float64")
    out["week_of_year_sin"] = np.sin(2 * np.pi * iso_week / 52.0)
    out["week_of_year_cos"] = np.cos(2 * np.pi * iso_week / 52.0)
    out["days_since_jun1"] = np.where(
        wk.dt.month >= 6,
        (wk - pd.to_datetime(wk.dt.year.astype(str) + "-06-01")).dt.days.clip(lower=0),
        0,
    ).astype("float64")
    if "tw_night_c_max" in out.columns:
        out["tw_night_x_sin_week"] = out["tw_night_c_max"] * out["week_of_year_sin"]

    # Final sweep: any remaining numeric NaNs in our new columns -> column median
    new_cols = [c for c in out.columns if c not in df.columns]
    for c in new_cols:
        if out[c].dtype.kind in "fi":
            med = out[c].median()
            out[c] = out[c].fillna(med if (med == med) else 0.0)
    return out


# ---------------------------------------------------------------- model factories

_BOOST_ROUNDS = 300


def make_baseline_xgb():
    return xgb.XGBRegressor(
        objective="reg:squarederror",
        max_depth=6,
        learning_rate=0.05,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        n_estimators=_BOOST_ROUNDS,
        verbosity=0,
        n_jobs=4,
        random_state=42,
        tree_method="hist",
    )


def make_lightgbm():
    if not _HAS_LGB:
        raise RuntimeError("lightgbm is not installed")
    return lgb.LGBMRegressor(
        objective="regression",
        max_depth=6,
        learning_rate=0.05,
        min_child_samples=3,
        subsample=0.8,
        colsample_bytree=0.8,
        n_estimators=_BOOST_ROUNDS,
        n_jobs=4,
        random_state=42,
        verbosity=-1,
    )


def make_extratrees():
    return ExtraTreesRegressor(
        n_estimators=300, max_depth=None, n_jobs=4, random_state=42,
    )


def make_randomforest():
    return RandomForestRegressor(
        n_estimators=300, max_depth=None, n_jobs=4, random_state=42,
    )


def make_ridge():
    return Ridge(alpha=1.0)


TOURNAMENT = {
    "T01_xgboost": make_baseline_xgb,
    "T02_lightgbm": make_lightgbm,
    "T03_extratrees": make_extratrees,
    "T04_randomforest": make_randomforest,
    "T05_ridge": make_ridge,
}
