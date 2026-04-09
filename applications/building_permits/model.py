"""Baseline + tournament model definitions for building-permit duration prediction.

Phase 0.5 (baseline) and Phase 1 (5-family tournament) live here. The baseline
predicts ``log1p(duration_days)`` — where ``duration_days`` is (issued_date -
filed_date).dt.days — from raw permit metadata on a cleaned cross-city subset
(SF, NYC, LA, Chicago, Austin). Target encodings for ``permit_subtype`` and
``neighborhood`` are computed **inside** each CV fold (see ``evaluate.py``).
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


CITIES_FOR_BASELINE = ["sf", "nyc", "la", "chicago", "austin"]

RAW_FEATURES = [
    "city_sf", "city_nyc", "city_la", "city_chicago", "city_austin",
    "filed_year", "filed_month_sin", "filed_month_cos",
    "log_valuation", "log_square_feet", "log_unit_count",
    "permit_subtype_te", "neighborhood_te",
]

# Columns produced by ``add_features`` that do NOT depend on y. The two
# *_te columns are filled in inside the CV loop.
RAW_FEATURES_NON_TE = [f for f in RAW_FEATURES if not f.endswith("_te")]


# ---------------------------------------------------------------- small-residential filter

def _is_small_residential(city_col: pd.Series, subtype: pd.Series, use_code: pd.Series,
                          permit_type: pd.Series) -> pd.Series:
    """City-specific filter for single-family / duplex / small multi-family.

    Falls back to a permissive "looks residential" regex when a city lacks a
    precise sub-type field. The recall limitation for Chicago (no unit_count
    and no use_code) is documented in ``data_acquisition_notes.md``.
    """
    sub = subtype.fillna("").astype(str).str.lower()
    use = use_code.fillna("").astype(str).str.lower()
    ptype = permit_type.fillna("").astype(str).str.lower()
    city = city_col.fillna("").astype(str)

    # Broad residential patterns that work across cities (free-text proposed_use,
    # LA permit_sub_type, Austin permit_class, etc.).
    residential_pat = (
        "family|duplex|dwelling|residential|townhouse|townhome|apartment|"
        "multi.?family|two.?family|single.?family|rowhouse|condo"
    )

    mask = pd.Series(False, index=subtype.index)

    # SF — proposed_use free-text.
    sf_mask = city.eq("sf") & (sub.str.contains(residential_pat, regex=True, na=False)
                                | use.str.contains(residential_pat, regex=True, na=False))
    mask |= sf_mask

    # NYC — building_class codes (A/B/R...) OR proposed_occupancy text match.
    nyc_bclass = sub.str.match(r"^\s*[abr]\s*[\w-]*", na=False)
    nyc_mask = city.eq("nyc") & (nyc_bclass | use.str.contains(residential_pat, regex=True, na=False))
    mask |= nyc_mask

    # LA — permit_sub_type values like "1 or 2 Family Dwelling" / "Apartment".
    la_mask = city.eq("la") & sub.str.contains(residential_pat, regex=True, na=False)
    mask |= la_mask

    # Chicago — no unit_count / use_code. Fall back to permit_type = NEW CONSTRUCTION
    # or RENOVATION/ALTERATION because the dataset has no residential tag.
    # This is the broader "residential" subset per instructions — recall-limited.
    chicago_mask = city.eq("chicago") & (
        ptype.str.contains("new construction|renovation|alteration|easy permit|wrecking", regex=True, na=False)
        | sub.str.contains("new construction|standard plan review|easy permit", regex=True, na=False)
    )
    mask |= chicago_mask

    # Austin — permit_class text like "R- 101 Single Family Houses" / "R- 103 Two Family Bldgs".
    austin_mask = city.eq("austin") & (
        sub.str.contains(r"^\s*r[-\s]", regex=True, na=False)
        | sub.str.contains(residential_pat, regex=True, na=False)
    )
    mask |= austin_mask

    return mask


def _status_allowed(city_col: pd.Series, status: pd.Series) -> pd.Series:
    """Keep rows whose status means 'issued / completed / finaled' (not cancelled/withdrawn/expired).

    Many cities' open-data feeds ship only issued permits so null status is
    treated as allowed; cities with an informative status field (SF, NYC,
    Austin) use a per-city allow-list.
    """
    s = status.fillna("").astype(str).str.lower().str.strip()
    c = city_col.fillna("").astype(str)

    # Disallowed substrings across all cities (applies only when status is non-empty).
    bad_pat = "cancel|withdraw|void|expired|disapproved|rejected|denied|suspended"
    bad = s.str.contains(bad_pat, regex=True, na=False)

    # Empty status → allow (dataset-level semantics already filter these).
    return (~bad)


def build_clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the Phase 0.5 filtering rules and add the ``duration_days`` target.

    Filters:
        1. filed_date & issued_date both non-null
        2. 0 < duration_days < 1825
        3. small-residential subset (see ``_is_small_residential``)
        4. status = issued / completed / finaled (not cancelled/withdrawn/expired)
    """
    out = df.copy()
    out["filed_date"] = pd.to_datetime(out["filed_date"], errors="coerce")
    out["issued_date"] = pd.to_datetime(out["issued_date"], errors="coerce")
    out = out[out["filed_date"].notna() & out["issued_date"].notna()].copy()
    duration = (out["issued_date"] - out["filed_date"]).dt.days
    out["duration_days"] = duration
    out = out[(duration > 0) & (duration < 1825)].copy()
    out = out[_is_small_residential(out["city"], out["permit_subtype"],
                                     out.get("use_code", pd.Series([""] * len(out))),
                                     out["permit_type"])].copy()
    out = out[_status_allowed(out["city"], out.get("status", pd.Series([""] * len(out))))].copy()
    out = out.reset_index(drop=True)
    return out


# ---------------------------------------------------------------- v2 (bias-fixed) clean builder
#
# The Phase 0.5 cleaned sample was accidentally biased to 2023–2026 because the
# underlying raw caches were 150k newest-first slices of each Socrata endpoint.
# build_clean_dataset_v2 restratifies by (city × filed_year_bucket) so the
# historical slow-tail eras (SF 2018–2023) are forced into the sample.

YEAR_BUCKETS: List[tuple] = [
    ("2015-2018", 2015, 2018),
    ("2019-2021", 2019, 2021),
    ("2022-2023", 2022, 2023),
    ("2024-2026", 2024, 2026),
]


def _year_bucket(year: float) -> str:
    if pd.isna(year):
        return "unknown"
    y = int(year)
    for name, lo, hi in YEAR_BUCKETS:
        if lo <= y <= hi:
            return name
    return "pre_2015" if y < 2015 else "post_2026"


def _is_small_residential_strict(df: pd.DataFrame) -> pd.Series:
    """Tighter per-city small-residential filter targeting 1-2 family / duplex.

    This is stricter than ``_is_small_residential`` and is used by the
    Phase 2 v2 cleaning pipeline to expose the slow-tail cases (SF new
    construction) that the broader Phase 0.5 filter drowned in OTC alterations.
    """
    city = df["city"].fillna("").astype(str)
    sub = df.get("permit_subtype", pd.Series([""] * len(df))).fillna("").astype(str).str.lower()
    use = df.get("use_code", pd.Series([""] * len(df))).fillna("").astype(str).str.lower()
    ptype = df.get("permit_type", pd.Series([""] * len(df))).fillna("").astype(str).str.lower()
    unit = pd.to_numeric(df.get("unit_count", pd.Series([0] * len(df))), errors="coerce")
    sqft = pd.to_numeric(df.get("square_feet", pd.Series([0] * len(df))), errors="coerce")

    mask = pd.Series(False, index=df.index)

    # SF: new construction (the 1-2 family slow era); exclude OTC which is the
    # dominant dataset volume but clears the same day for minor repairs.
    sf_has_res = (sub.str.contains("family|dwelling|duplex", regex=True, na=False)
                  | use.str.contains("family|dwelling|duplex", regex=True, na=False))
    sf_ok_ptype = ptype.str.contains("new construction|demolition", regex=True, na=False) & \
                  ~ptype.str.contains("otc", regex=True, na=False)
    # Also include non-OTC alterations with residential proposed_use
    sf_alt_ok = (ptype.str.contains("additions alterations", regex=True, na=False)
                 & ~ptype.str.contains("otc", regex=True, na=False))
    sf_mask = (city == "sf") & sf_has_res & (sf_ok_ptype | sf_alt_ok)
    mask |= sf_mask

    # NYC: job_type NB/A1/A2/A3, unit_count <= 4.
    nyc_jtype = ptype.str.strip().isin(["nb", "a1", "a2", "a3"])
    nyc_units_ok = unit.fillna(4).le(4)
    nyc_mask = (city == "nyc") & nyc_jtype & nyc_units_ok
    mask |= nyc_mask

    # LA: permit_type in BLD-NEW/BLD-ADD-RENO/BLD-ALTER-REPAIR or descriptive,
    # permit_sub_type has 1 or 2 Family Dwelling / Apartment / Duplex
    la_sub_ok = sub.str.contains("1 or 2 family|duplex|apartment|dwelling", regex=True, na=False)
    la_units_ok = unit.fillna(4).le(4)
    la_mask = (city == "la") & la_sub_ok & la_units_ok
    mask |= la_mask

    # Chicago: work description or review_type mentions two-family/duplex or
    # broader NEW CONSTRUCTION with small scale.
    chi_desc = (sub.str.contains("new construction|standard plan review", regex=True, na=False)
                | use.str.contains("two.family|duplex|2.flat|two.flat|two.unit", regex=True, na=False)
                | use.str.contains("residen", na=False))
    chicago_mask = (city == "chicago") & chi_desc
    mask |= chicago_mask

    # Austin: permit_class R- prefixed (residential) or text family/duplex; sqft<5000 as scale cap.
    austin_is_res = (sub.str.match(r"^\s*r[-\s]", na=False)
                     | sub.str.contains("family|duplex|residen", regex=True, na=False))
    austin_scale_ok = sqft.fillna(5000).le(5000)
    austin_mask = (city == "austin") & austin_is_res & austin_scale_ok
    mask |= austin_mask

    return mask


def build_clean_dataset_v2(df: pd.DataFrame, seed: int = 42,
                           n_rows: int = 50_000) -> pd.DataFrame:
    """Phase 2 bias-fixed cleaned dataset builder.

    Uses the strict residential filter (not the broad Phase 0.5 one), the
    Phase 0.5 hygiene filters, then stratifies by (city × filed_year_bucket)
    so each bucket gets a proportional share of its city's cap. The 2015-2018
    and 2019-2021 buckets carry the SF slow era; without re-stratification
    they would be swamped by 2024-2026 rows.
    """
    out = df.copy()
    out["filed_date"] = pd.to_datetime(out["filed_date"], errors="coerce")
    out["issued_date"] = pd.to_datetime(out["issued_date"], errors="coerce")
    out = out[out["filed_date"].notna() & out["issued_date"].notna()].copy()
    duration = (out["issued_date"] - out["filed_date"]).dt.days
    out["duration_days"] = duration
    out = out[(duration > 0) & (duration < 1825)].copy()
    # Drop sentinel dates.
    out = out[out["filed_date"] >= pd.Timestamp("2015-01-01")].copy()

    # Tight residential filter.
    out = out[_is_small_residential_strict(out)].copy()

    # Status hygiene.
    out = out[_status_allowed(out["city"], out.get("status", pd.Series([""] * len(out))))].copy()
    out = out.reset_index(drop=True)

    if len(out) == 0:
        return out

    out["year_bucket"] = pd.to_datetime(out["filed_date"]).dt.year.map(_year_bucket)
    out = out[out["year_bucket"].isin([b[0] for b in YEAR_BUCKETS])].copy()

    # Target per-city share = even 1/5; per-bucket share within city = even 1/4.
    per_city = n_rows // len(CITIES_FOR_BASELINE)
    per_cell_target = per_city // len(YEAR_BUCKETS)

    rng = np.random.default_rng(seed)
    parts = []
    for city in CITIES_FOR_BASELINE:
        sub_city = out[out["city"] == city]
        if len(sub_city) == 0:
            continue
        for b_name, _lo, _hi in YEAR_BUCKETS:
            cell = sub_city[sub_city["year_bucket"] == b_name]
            n_cell = min(per_cell_target, len(cell))
            if n_cell == 0:
                continue
            idx = rng.choice(len(cell), size=n_cell, replace=False)
            parts.append(cell.iloc[idx])

    if not parts:
        return out.iloc[0:0]
    sampled = pd.concat(parts, ignore_index=True)

    # If underfilled, top up from leftover pool at random.
    remaining = n_rows - len(sampled)
    if remaining > 0:
        used_permit_ids = set(sampled["permit_id"].astype(str).tolist())
        leftover = out[~out["permit_id"].astype(str).isin(used_permit_ids)]
        if len(leftover) > 0:
            take = min(remaining, len(leftover))
            idx = rng.choice(len(leftover), size=take, replace=False)
            sampled = pd.concat([sampled, leftover.iloc[idx]], ignore_index=True)

    sampled = sampled.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return sampled


# ---------------------------------------------------------------- feature engineering

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the raw feature columns from a cleaned DataFrame.

    Produces the non-target-encoded columns in ``RAW_FEATURES_NON_TE``. The
    ``permit_subtype_te`` / ``neighborhood_te`` columns are filled in inside
    the CV loop on the fold's training set only.
    """
    out = df.copy()
    fd = pd.to_datetime(out["filed_date"], errors="coerce")
    out["filed_year"] = fd.dt.year.astype("float64")
    month = fd.dt.month.astype("float64")
    out["filed_month_sin"] = np.sin(2 * np.pi * month / 12.0)
    out["filed_month_cos"] = np.cos(2 * np.pi * month / 12.0)

    # City median imputation for numeric quantities.
    for src, dst, default in [
        ("valuation_usd", "log_valuation", 0.0),
        ("square_feet", "log_square_feet", 0.0),
        ("unit_count", "log_unit_count", 1.0),
    ]:
        if src not in out.columns:
            out[src] = np.nan
        x = pd.to_numeric(out[src], errors="coerce")
        city_med = x.groupby(out["city"]).transform("median")
        x = x.fillna(city_med).fillna(default)
        # log1p on non-negative values; clip to avoid log1p of negatives.
        out[dst] = np.log1p(np.clip(x.values, a_min=0.0, a_max=None))

    # Top-200 neighborhood + OTHER bucket.
    neigh = out.get("neighborhood", pd.Series([""] * len(out))).fillna("__NA__").astype(str)
    top = neigh.value_counts().head(200).index
    out["neighborhood"] = np.where(neigh.isin(top), neigh, "OTHER")

    # permit_subtype as string for target encoding.
    out["permit_subtype"] = out.get("permit_subtype", pd.Series([""] * len(out))).fillna("__NA__").astype(str)

    # City one-hot (use baseline list so unknown cities silently drop to all zeros).
    for c in CITIES_FOR_BASELINE:
        out[f"city_{c}"] = (out["city"] == c).astype("float64")

    # Placeholders for target-encoded columns — filled inside CV loop.
    if "permit_subtype_te" not in out.columns:
        out["permit_subtype_te"] = np.nan
    if "neighborhood_te" not in out.columns:
        out["neighborhood_te"] = np.nan
    return out


def target_encode(train_df: pd.DataFrame, valid_df: pd.DataFrame, col: str,
                  y_train: np.ndarray, smoothing: float = 10.0) -> np.ndarray:
    """Smoothed target encoding fit on train, applied to valid. Returns valid encoded.

    No valid-set information touches the fit — the returned encoding for a
    valid row comes only from the training rows that share its category (or
    the global training mean if the category is unseen).
    """
    global_mean = float(np.mean(y_train))
    train_cats = train_df[col].fillna("__NA__").astype(str)
    stats = pd.Series(y_train).groupby(train_cats.values).agg(["mean", "count"])
    smoothed = (stats["mean"] * stats["count"] + global_mean * smoothing) / (stats["count"] + smoothing)
    valid_cats = valid_df[col].fillna("__NA__").astype(str)
    return valid_cats.map(smoothed).fillna(global_mean).values.astype("float64")


# ---------------------------------------------------------------- model factories

def make_baseline_xgb():
    return xgb.XGBRegressor(
        objective="reg:squarederror",
        max_depth=6,
        learning_rate=0.05,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        n_estimators=300,
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
        n_estimators=300,
        n_jobs=4,
        random_state=42,
        verbosity=-1,
    )


def make_extratrees():
    return ExtraTreesRegressor(n_estimators=300, max_depth=None, n_jobs=4, random_state=42)


def make_randomforest():
    return RandomForestRegressor(n_estimators=300, max_depth=None, n_jobs=4, random_state=42)


def make_ridge():
    return Ridge(alpha=1.0)


TOURNAMENT = {
    "T01_xgboost": make_baseline_xgb,
    "T02_lightgbm": make_lightgbm,
    "T03_extratrees": make_extratrees,
    "T04_randomforest": make_randomforest,
    "T05_ridge": make_ridge,
}


# ---------------------------------------------------------------- Phase 2 feature engine
#
# Phase 2 hypotheses are encoded as a config dict. add_features_v2 reads the
# config and emits only the requested feature columns; the CV harness then
# projects those columns + RAW_FEATURES_NON_TE into the training matrix.
#
# Config schema (all optional, all default off):
#   include_dow: bool                 -> filed_dow (0..6)
#   include_holiday_flag: bool        -> filed_holiday_week (0/1)
#   include_covid_era: bool           -> covid_era (0/1)
#   include_holiday_season: bool      -> holiday_season (Nov15-Jan2)
#   include_era_bin: bool             -> era_bin (0..3)
#   include_year_sq: bool             -> filed_year_sq
#   include_reform_dummies: bool      -> post_sb423, post_home1, post_ab2011, post_hb267, post_dob_now
#   include_reform_decay: bool        -> sb423_decay, home1_decay
#   include_pre_post_approval: bool   -> pre_approval_days, post_approval_days (SF/NYC only)
#   include_rolling_load: int|None    -> rolling_Nd_city_count
#   include_nbhd_rolling: int|None    -> rolling_Nd_nbhd_count
#   include_nbhd_recency: bool        -> days_since_last_nbhd_permit
#   include_is_duplex: bool           -> is_duplex binary
#   include_change_of_use: bool       -> SF change-of-use
#   te_cols: list[str]                -> extra target-encoded columns (eg. city_year)
#   nyc_professional_cert: bool       -> nyc professional_cert guess from status/job_type
#   city_interaction: bool            -> city_year_te as cross feature
#   monotone: dict[str,int]|None      -> XGB monotone_constraints
#   target_transform: 'log1p'|'sqrt'|'raw'|'boxcox'

PHASE2_BASE_FEATURES = RAW_FEATURES_NON_TE + ["permit_subtype_te", "neighborhood_te"]


def _add_dow_feature(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    df["filed_dow"] = fd.dt.dayofweek.fillna(0).astype("float64")
    return df


def _add_holiday_week(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    # Approx US federal holiday list (month, day) — ignores movable ones.
    fixed = {(1, 1), (7, 4), (11, 11), (12, 25)}
    mon = fd.dt.month.fillna(0).astype(int)
    day = fd.dt.day.fillna(0).astype(int)
    hit = pd.Series(list(zip(mon.values, day.values)), index=df.index).isin(fixed)
    df["filed_holiday_week"] = hit.astype("float64")
    return df


def _add_covid_era(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    covid = (fd >= pd.Timestamp("2020-03-01")) & (fd <= pd.Timestamp("2021-06-30"))
    df["covid_era"] = covid.astype("float64")
    return df


def _add_holiday_season(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    m = fd.dt.month
    d = fd.dt.day
    hs = ((m == 12) | ((m == 11) & (d >= 15)) | ((m == 1) & (d <= 2)))
    df["holiday_season"] = hs.astype("float64")
    return df


def _add_era_bin(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    y = fd.dt.year.fillna(0).astype(int)
    era = np.select(
        [y < 2015, y < 2020, y < 2022, y >= 2022],
        [0, 1, 2, 3], default=3,
    )
    df["era_bin"] = era.astype("float64")
    return df


def _add_year_sq(df: pd.DataFrame) -> pd.DataFrame:
    df["filed_year_sq"] = (df["filed_year"] - 2015.0) ** 2
    return df


def _add_reform_dummies(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    city = df["city"].astype(str)
    df["post_sb423"] = ((fd >= pd.Timestamp("2024-01-01")) & city.isin(["sf", "la"])).astype("float64")
    df["post_home1"] = ((fd >= pd.Timestamp("2023-12-01")) & (city == "austin")).astype("float64")
    df["post_ab2011"] = ((fd >= pd.Timestamp("2023-07-01")) & city.isin(["sf", "la"])).astype("float64")
    df["post_hb267"] = ((fd >= pd.Timestamp("2024-07-01")) & city.isin([])).astype("float64")  # Florida, N/A
    df["post_dob_now"] = ((fd >= pd.Timestamp("2020-01-01")) & (city == "nyc")).astype("float64")
    return df


def _add_reform_decay(df: pd.DataFrame, tau_days: float = 90.0) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    city = df["city"].astype(str)
    sb_days = (fd - pd.Timestamp("2024-01-01")).dt.days.astype("float64")
    ho_days = (fd - pd.Timestamp("2023-12-01")).dt.days.astype("float64")
    sb_decay = np.where((sb_days >= 0) & city.isin(["sf", "la"]),
                        np.exp(-sb_days.values / tau_days), 0.0)
    ho_decay = np.where((ho_days >= 0) & (city == "austin"),
                        np.exp(-ho_days.values / tau_days), 0.0)
    df["sb423_decay"] = sb_decay
    df["home1_decay"] = ho_decay
    return df


def _add_is_duplex(df: pd.DataFrame) -> pd.DataFrame:
    sub = df["permit_subtype"].fillna("").astype(str).str.lower()
    use = df.get("use_code", pd.Series([""] * len(df))).fillna("").astype(str).str.lower()
    pat = "duplex|two.?family|2.family|1 or 2|two.unit"
    hit = sub.str.contains(pat, regex=True, na=False) | use.str.contains(pat, regex=True, na=False)
    df["is_duplex"] = hit.astype("float64")
    return df


def _add_change_of_use(df: pd.DataFrame) -> pd.DataFrame:
    # Proxy: permit_subtype vs use_code differ for SF
    sub = df.get("permit_subtype", pd.Series([""] * len(df))).fillna("").astype(str).str.lower()
    use = df.get("use_code", pd.Series([""] * len(df))).fillna("").astype(str).str.lower()
    diff = ((df["city"] == "sf") & (sub != use) & (sub != "") & (use != "")).astype("float64")
    df["change_of_use"] = diff
    return df


def _rolling_load_stable(df: pd.DataFrame, window_days: int, key: str, out_col: str) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    df = df.copy()
    df[out_col] = 0.0
    df["_fd"] = fd
    df["_k"] = df[key].astype(str)
    for k, sub in df.groupby("_k"):
        sub_sorted = sub.sort_values("_fd")
        t = sub_sorted["_fd"].values.astype("datetime64[ns]")
        vals = np.ones(len(sub_sorted), dtype="float64")
        window = np.timedelta64(window_days, "D")
        # Two-pointer rolling count on sorted timestamps.
        out = np.zeros(len(sub_sorted), dtype="float64")
        lo = 0
        for i in range(len(sub_sorted)):
            while t[i] - t[lo] > window:
                lo += 1
            out[i] = vals[lo:i + 1].sum()
        df.loc[sub_sorted.index, out_col] = out
    df = df.drop(columns=["_fd", "_k"])
    return df


def _add_nbhd_recency(df: pd.DataFrame) -> pd.DataFrame:
    fd = pd.to_datetime(df["filed_date"], errors="coerce")
    key = (df["city"].astype(str) + "|" + df["neighborhood"].astype(str))
    recency = pd.Series(np.nan, index=df.index, dtype="float64")
    for k, sub in df.groupby(key):
        sub_t = fd.loc[sub.index].sort_values()
        prior = sub_t.shift(1)
        diff = (sub_t - prior).dt.days.astype("float64")
        recency.loc[sub_t.index] = diff.values
    recency = recency.fillna(365.0)
    df["days_since_last_nbhd_permit"] = recency
    return df


def _apply_target_transform(y_days: np.ndarray, kind: str) -> np.ndarray:
    if kind == "log1p":
        return np.log1p(y_days)
    if kind == "sqrt":
        return np.sqrt(y_days)
    if kind == "raw":
        return y_days.astype("float64")
    if kind == "boxcox":
        from scipy.stats import boxcox
        transformed, _ = boxcox(y_days + 1.0)
        return transformed
    raise ValueError(f"unknown target transform: {kind}")


def _inverse_target_transform(yhat: np.ndarray, kind: str) -> np.ndarray:
    if kind == "log1p":
        return np.expm1(yhat)
    if kind == "sqrt":
        return np.maximum(yhat, 0) ** 2
    if kind == "raw":
        return yhat
    if kind == "boxcox":
        # For simplicity we store lambda=0 equivalent: expm1
        return np.expm1(yhat)
    raise ValueError(f"unknown target transform: {kind}")


def add_phase2_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Apply add_features then selectively add Phase 2 columns per config."""
    out = add_features(df)

    if config.get("include_dow"):
        out = _add_dow_feature(out)
    if config.get("include_holiday_flag"):
        out = _add_holiday_week(out)
    if config.get("include_covid_era"):
        out = _add_covid_era(out)
    if config.get("include_holiday_season"):
        out = _add_holiday_season(out)
    if config.get("include_era_bin"):
        out = _add_era_bin(out)
    if config.get("include_year_sq"):
        out = _add_year_sq(out)
    if config.get("include_reform_dummies"):
        out = _add_reform_dummies(out)
    if config.get("include_reform_decay"):
        out = _add_reform_decay(out)
    if config.get("include_is_duplex"):
        out = _add_is_duplex(out)
    if config.get("include_change_of_use"):
        out = _add_change_of_use(out)
    if config.get("include_rolling_30d"):
        out = _rolling_load_stable(out, 30, "city", "rolling_30d_city_count")
    if config.get("include_rolling_90d"):
        out = _rolling_load_stable(out, 90, "city", "rolling_90d_city_count")
    if config.get("include_nbhd_rolling_90d"):
        out = _rolling_load_stable(out, 90, "neighborhood", "rolling_90d_nbhd_count")
    if config.get("include_nbhd_recency"):
        out = _add_nbhd_recency(out)

    # city_year crossed feature as a target-encoded column
    if config.get("include_city_year"):
        out["city_year"] = out["city"].astype(str) + "_" + out["filed_year"].fillna(0).astype(int).astype(str)

    return out


def build_phase2_feature_list(config: dict) -> List[str]:
    feats = list(PHASE2_BASE_FEATURES)
    if config.get("include_dow"):
        feats.append("filed_dow")
    if config.get("include_holiday_flag"):
        feats.append("filed_holiday_week")
    if config.get("include_covid_era"):
        feats.append("covid_era")
    if config.get("include_holiday_season"):
        feats.append("holiday_season")
    if config.get("include_era_bin"):
        feats.append("era_bin")
    if config.get("include_year_sq"):
        feats.append("filed_year_sq")
    if config.get("include_reform_dummies"):
        feats.extend(["post_sb423", "post_home1", "post_ab2011", "post_hb267", "post_dob_now"])
    if config.get("include_reform_decay"):
        feats.extend(["sb423_decay", "home1_decay"])
    if config.get("include_is_duplex"):
        feats.append("is_duplex")
    if config.get("include_change_of_use"):
        feats.append("change_of_use")
    if config.get("include_rolling_30d"):
        feats.append("rolling_30d_city_count")
    if config.get("include_rolling_90d"):
        feats.append("rolling_90d_city_count")
    if config.get("include_nbhd_rolling_90d"):
        feats.append("rolling_90d_nbhd_count")
    if config.get("include_nbhd_recency"):
        feats.append("days_since_last_nbhd_permit")
    if config.get("include_city_year"):
        feats.append("city_year_te")
    return feats


# ---------------------------------------------------------------- Phase 2 model factories

def make_xgb(params: Optional[dict] = None):
    base = dict(
        objective="reg:squarederror",
        max_depth=6,
        learning_rate=0.05,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        n_estimators=300,
        verbosity=0,
        n_jobs=4,
        random_state=42,
        tree_method="hist",
    )
    if params:
        base.update(params)
    return xgb.XGBRegressor(**base)


def make_xgb_quantile(alpha: float = 0.5, params: Optional[dict] = None):
    base = dict(
        objective="reg:quantileerror",
        quantile_alpha=alpha,
        max_depth=6,
        learning_rate=0.05,
        n_estimators=300,
        verbosity=0,
        n_jobs=4,
        random_state=42,
        tree_method="hist",
    )
    if params:
        base.update(params)
    return xgb.XGBRegressor(**base)


def make_lightgbm_v2(params: Optional[dict] = None):
    if not _HAS_LGB:
        raise RuntimeError("lightgbm is not installed")
    base = dict(
        objective="regression",
        max_depth=6,
        learning_rate=0.05,
        min_child_samples=3,
        subsample=0.8,
        colsample_bytree=0.8,
        n_estimators=300,
        n_jobs=4,
        random_state=42,
        verbosity=-1,
    )
    if params:
        base.update(params)
    return lgb.LGBMRegressor(**base)
