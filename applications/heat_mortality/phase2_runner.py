"""Phase 2 HDR loop — 116 single-change hypotheses for heat-mortality.

Each hypothesis is a small modification to the previous best configuration.
We use the same 5-fold KFold CV harness, ``random_state=42``, the same
cleaned dataset (Phase 0.5 cleaned panel), and the same metrics
(MAE deaths, RMSE, R2, AUC lethal, Brier lethal).

KEEP rule:
    cv_mae_deaths < best_so_far - max(0.5, 0.01 * best_so_far)

The script appends one row per hypothesis to ``results.tsv`` with the
schema documented in evaluate.py::RESULTS_HEADER.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sklearn.metrics import (  # noqa: E402
    brier_score_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold  # noqa: E402

import xgboost as xgb  # noqa: E402
from sklearn.ensemble import (  # noqa: E402
    ExtraTreesRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Ridge  # noqa: E402

try:
    import lightgbm as lgb  # noqa: E402
    _HAS_LGB = True
except Exception:  # noqa: BLE001
    _HAS_LGB = False

from model import (  # noqa: E402
    BASELINE_FEATURES,
    BASELINE_FEATURES_WITH_CITY,
    add_features,
    add_phase2_features,
    build_clean_dataset,
    label_lethal_heatwave,
    make_baseline_xgb,
    make_extratrees,
    make_lightgbm,
    make_randomforest,
    make_ridge,
)
from evaluate import _append_result, _init_results  # noqa: E402

CLEAN_PATH = HERE / "data" / "clean" / "heat_mortality_master.parquet"
PHASE2_CACHE = HERE / "data" / "clean" / "heat_mortality_phase2.parquet"
RESULTS_PATH = HERE / "results.tsv"


# ---------------------------------------------------------------- prep
def _prep_panel() -> pd.DataFrame:
    if not PHASE2_CACHE.exists():
        raise FileNotFoundError(
            f"{PHASE2_CACHE} missing — run build_phase2_cache.py first"
        )
    raw = pd.read_parquet(PHASE2_CACHE)
    clean = build_clean_dataset(raw)
    feat = add_features(clean)
    feat = add_phase2_features(feat)
    return feat.reset_index(drop=True)


# ---------------------------------------------------------------- metrics
def _metrics(y, pred, exp_b, y_bin) -> dict:
    y = np.asarray(y, dtype="float64")
    pred = np.asarray(pred, dtype="float64")
    exp_b = np.asarray(exp_b, dtype="float64")
    y_bin = np.asarray(y_bin, dtype="int64")
    mae = float(mean_absolute_error(y, pred))
    rmse = float(np.sqrt(mean_squared_error(y, pred)))
    r2 = float(r2_score(y, pred))
    safe_exp = np.where(exp_b > 0, exp_b, np.nan)
    p_pred = pred / safe_exp
    s = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
    auc = float("nan")
    brier = float("nan")
    if y_bin.sum() >= 1 and (len(y_bin) - y_bin.sum()) >= 1:
        try:
            auc = float(roc_auc_score(y_bin, s))
        except ValueError:
            pass
        try:
            brier = float(brier_score_loss(y_bin, s))
        except ValueError:
            pass
    return {
        "mae_deaths": mae,
        "rmse_deaths": rmse,
        "r2": r2,
        "auc_lethal": auc,
        "brier_lethal": brier,
    }


# ---------------------------------------------------------------- harness
def _cv_run(panel: pd.DataFrame,
            feature_cols: List[str],
            model_factory: Callable,
            target: str = "excess_deaths",
            target_transform: Optional[str] = None,
            seed: int = 42) -> dict:
    df = panel.reset_index(drop=True)
    X = df[feature_cols].astype("float64").fillna(0.0).values
    y_raw = df[target].astype("float64").values
    if target_transform == "log1p_pos":
        y = np.sign(y_raw) * np.log1p(np.abs(y_raw))
    elif target_transform == "arcsinh":
        y = np.arcsinh(y_raw)
    elif target_transform == "pscore":
        y = df["p_score"].astype("float64").values
    else:
        y = y_raw
    exp_b = df["expected_baseline"].astype("float64").values
    y_bin = label_lethal_heatwave(df)

    kf = KFold(n_splits=5, shuffle=True, random_state=seed)
    oof = np.zeros(len(df), dtype="float64")
    for tr, va in kf.split(df):
        m = model_factory()
        m.fit(X[tr], y[tr])
        oof[va] = m.predict(X[va])
    # back-transform
    if target_transform == "log1p_pos":
        oof_d = np.sign(oof) * (np.expm1(np.abs(oof)))
    elif target_transform == "arcsinh":
        oof_d = np.sinh(oof)
    elif target_transform == "pscore":
        oof_d = oof * exp_b
    else:
        oof_d = oof
    return _metrics(df["excess_deaths"].astype("float64").values, oof_d, exp_b, y_bin)


# ---------------------------------------------------------------- model factories
def make_xgb(**kw):
    base = dict(
        objective="reg:squarederror",
        max_depth=6, learning_rate=0.05, min_child_weight=3,
        subsample=0.8, colsample_bytree=0.8,
        n_estimators=300, verbosity=0, n_jobs=4,
        random_state=42, tree_method="hist",
    )
    base.update(kw)
    return xgb.XGBRegressor(**base)


def make_lgbm(**kw):
    if not _HAS_LGB:
        raise RuntimeError("lightgbm missing")
    base = dict(
        objective="regression",
        max_depth=6, learning_rate=0.05, min_child_samples=3,
        subsample=0.8, colsample_bytree=0.8,
        n_estimators=300, n_jobs=4, random_state=42, verbosity=-1,
    )
    base.update(kw)
    return lgb.LGBMRegressor(**base)


def make_et(**kw):
    base = dict(n_estimators=300, max_depth=None, n_jobs=4, random_state=42)
    base.update(kw)
    return ExtraTreesRegressor(**base)


def make_rf(**kw):
    base = dict(n_estimators=300, max_depth=None, n_jobs=4, random_state=42)
    base.update(kw)
    return RandomForestRegressor(**base)


def make_rdg(**kw):
    return Ridge(alpha=kw.get("alpha", 1.0))


# ---------------------------------------------------------------- hypothesis spec
class Hyp:
    """One single-change hypothesis."""
    def __init__(self, exp_id: str, desc: str, model: str,
                 add_cols: List[str] = None,
                 model_kw: Dict = None,
                 target_transform: Optional[str] = None,
                 defer: Optional[str] = None,
                 model_factory_override: Optional[Callable] = None):
        self.exp_id = exp_id
        self.desc = desc
        self.model = model
        self.add_cols = add_cols or []
        self.model_kw = model_kw or {}
        self.target_transform = target_transform
        self.defer = defer
        self.model_factory_override = model_factory_override

    def factory(self):
        if self.model_factory_override is not None:
            return self.model_factory_override
        if self.model == "xgboost":
            return lambda: make_xgb(**self.model_kw)
        if self.model == "lightgbm":
            return lambda: make_lgbm(**self.model_kw)
        if self.model == "extratrees":
            return lambda: make_et(**self.model_kw)
        if self.model == "randomforest":
            return lambda: make_rf(**self.model_kw)
        if self.model == "ridge":
            return lambda: make_rdg(**self.model_kw)
        raise ValueError(f"unknown model {self.model}")


# ---------------------------------------------------------------- queue
def build_queue() -> List[Hyp]:
    """The 116 hypotheses, prior-ranked, single-change against the previous best."""
    Q: List[Hyp] = []

    # Theme 1 — flagship night-time wet-bulb features (22)
    Q.append(Hyp("H001", "add tw_night_c_max", "extratrees", ["tw_night_c_max"]))
    Q.append(Hyp("H002", "add tw_night_c_mean", "extratrees", ["tw_night_c_mean"]))
    Q.append(Hyp("H003", "add tw_night_c_max+mean", "extratrees",
                 ["tw_night_c_max", "tw_night_c_mean"]))
    Q.append(Hyp("H004", "add consecutive_nights_tw_above_24_count",
                 "extratrees", ["consecutive_nights_tw_above_24_count"]))
    Q.append(Hyp("H005", "add tw_day_night_spread_c", "extratrees",
                 ["tw_day_night_spread_c"]))
    Q.append(Hyp("H006", "add tropical_night_count_week (Tmin>=20)",
                 "extratrees", ["tropical_night_count_week"]))
    Q.append(Hyp("H007", "add tropical_night_count_tw22 (wet-bulb)",
                 "extratrees", ["tropical_night_count_tw22"]))
    Q.append(Hyp("H008", "add tw_night_c_max_p95_anomaly", "extratrees",
                 ["tw_night_c_max_p95_anomaly"]))
    Q.append(Hyp("H009", "add tw_night_c_mean_p90_anomaly", "extratrees",
                 ["tw_night_c_mean_p90_anomaly"]))
    Q.append(Hyp("H010", "add tw_night_c_max_zscore_city", "extratrees",
                 ["tw_night_c_max_zscore_city"]))
    Q.append(Hyp("H011", "widen night window 22:00-06:00 (tw_night_c_max_nw22)",
                 "extratrees", ["tw_night_c_max_nw22", "tw_night_c_mean_nw22"]))
    Q.append(Hyp("H012", "narrow night window 02:00-06:00 (tw_night_c_max_nw02)",
                 "extratrees", ["tw_night_c_max_nw02", "tw_night_c_mean_nw02"]))
    Q.append(Hyp("H013", "add tw_night_c_min", "extratrees", ["tw_night_c_min"]))
    Q.append(Hyp("H014", "Davies-Jones wet-bulb (gated on ERA5)", "extratrees",
                 defer="needs metpy / Davies-Jones — Stull is current default"))
    Q.append(Hyp("H015", "night-time UTCI (gated on ERA5-HEAT)", "extratrees",
                 defer="needs ERA5-HEAT pull"))
    Q.append(Hyp("H016", "tw_night_c_max x age65p (gated on age data)",
                 "extratrees",
                 defer="needs age-stratified loader"))
    Q.append(Hyp("H017", "tw_night_c_max x AC penetration (gated)", "extratrees",
                 defer="needs AC penetration loader"))
    Q.append(Hyp("H018", "3-day rolling tw_night_max peak", "extratrees",
                 ["tw_night_max_roll3d"]))
    Q.append(Hyp("H019", "wet-bulb compound flag (compound_tw_days_count)",
                 "extratrees", ["compound_tw_days_count", "tw_compound_flag"]))
    Q.append(Hyp("H020", "tw degree-hours above 26 C", "extratrees",
                 ["tw_degree_hours_above_26"]))
    Q.append(Hyp("H021", "tw degree-hours above 24 C", "extratrees",
                 ["tw_degree_hours_above_24"]))
    Q.append(Hyp("H022", "4-week rolling tw_night max (heat-priming)",
                 "extratrees", ["tw_night_c_max_roll4w"]))

    # Theme 2 — wet-bulb computation choice (4)
    Q.append(Hyp("H023", "Davies-Jones whole pipeline", "extratrees",
                 defer="needs metpy install + pressure"))
    Q.append(Hyp("H024", "elevation-stratified Stull/DJ", "extratrees",
                 defer="needs DJ + elevation"))
    Q.append(Hyp("H025", "sWBGT", "extratrees",
                 defer="needs vapour-pressure-derived sWBGT (skip without ERA5)"))
    Q.append(Hyp("H026", "Liljegren WBGT", "extratrees",
                 defer="needs ERA5 + Liljegren solver"))

    # Theme 3 — compound day-night exposure (6)
    Q.append(Hyp("H027", "tmax x tmin interaction", "extratrees", ["tmax_x_tmin"]))
    Q.append(Hyp("H028", "Tang 2-day compound flag", "extratrees",
                 ["tang_compound_2d_flag"]))
    Q.append(Hyp("H029", "Yin 3-day compound flag", "extratrees",
                 ["compound_3d_flag"]))
    Q.append(Hyp("H030", "compound_days_count", "extratrees",
                 ["compound_days_count"]))
    Q.append(Hyp("H031", "heatwave_type_ordinal", "extratrees",
                 ["heatwave_type_ordinal"]))
    Q.append(Hyp("H032", "compound_days_4w_lag", "extratrees",
                 ["compound_days_4w_lag"]))

    # Theme 4 — heat-wave definition variants (8)
    Q.append(Hyp("H033", "fixed Tmax>=35 3-day flag", "extratrees",
                 ["hw_fixed_35_3d_flag"]))
    Q.append(Hyp("H034", "p95 3-day flag", "extratrees", ["hw_p95_3d_flag"]))
    Q.append(Hyp("H035", "EuroHEAT flag", "extratrees", ["euroheat_flag"]))
    Q.append(Hyp("H036", "Hobday calendar-day p90 5-day flag", "extratrees",
                 ["hobday_atm_flag"]))
    Q.append(Hyp("H037", "NWS HeatRisk feature", "extratrees",
                 defer="needs NWS HeatRisk archive"))
    Q.append(Hyp("H038", "UK HHAS feature", "extratrees",
                 defer="needs UK HHAS archive"))
    Q.append(Hyp("H039", "ensemble of 3 HW definitions vote", "extratrees",
                 ["hw_majority_vote"]))
    Q.append(Hyp("H040", "Russo HWMI", "extratrees", ["hwmi_daily"]))

    # Theme 5 — acclimatisation features (5)
    Q.append(Hyp("H041", "tw_c_mean - city MMT", "extratrees",
                 ["tw_c_mean_minus_city_mmt"]))
    Q.append(Hyp("H042", "MMT percentile", "extratrees", ["mmt_percentile_city"]))
    Q.append(Hyp("H043", "1961-1990 climatology", "extratrees",
                 defer="no historical climatology cache"))
    Q.append(Hyp("H044", "1991-2020 climatology", "extratrees",
                 defer="no historical climatology cache"))
    Q.append(Hyp("H045", "year-index x tw interaction", "extratrees",
                 ["tw_c_mean_x_year_index"]))

    # Theme 6 — lag structure (7)
    Q.append(Hyp("H046", "lag-0/1 tmax rolling max", "extratrees",
                 ["tmax_max2d_week"]))
    Q.append(Hyp("H047", "0-14 day Tw rolling mean (2-week)", "extratrees",
                 ["tw_rolling_14d_mean"]))
    Q.append(Hyp("H048", "0-21 day Tw rolling mean (3-week)", "extratrees",
                 ["tw_rolling_21d_mean"]))
    Q.append(Hyp("H049", "0-28 day Tw rolling mean (4-week)", "extratrees",
                 ["tw_rolling_28d_mean"]))
    Q.append(Hyp("H050", "DLNM-style cross-basis tw weekly lag1..4",
                 "extratrees",
                 ["tw_c_mean_lag1", "tw_c_mean_lag2", "tw_c_mean_lag3",
                  "tw_c_mean_lag4", "tw_c_max_lag1", "tw_c_max_lag2",
                  "tw_c_max_lag3", "tw_c_max_lag4"]))
    Q.append(Hyp("H051", "DLNM-style cross-basis tw_night weekly lag1..4",
                 "extratrees",
                 ["tw_night_c_max_lag1", "tw_night_c_max_lag2",
                  "tw_night_c_max_lag3", "tw_night_c_max_lag4",
                  "tw_night_c_mean_lag1", "tw_night_c_mean_lag2",
                  "tw_night_c_mean_lag3", "tw_night_c_mean_lag4"]))
    Q.append(Hyp("H052", "separate cold lag basis", "extratrees",
                 ["tmin_c_mean_lag1", "tmin_c_mean_lag2",
                  "tmin_c_mean_lag3", "tmin_c_mean_lag4"]))

    # Theme 7 — vulnerability moderators (8)
    Q.append(Hyp("H053", "pct_age_65p", "extratrees",
                 defer="needs age-stratified loader"))
    Q.append(Hyp("H054", "ac_penetration_pct", "extratrees",
                 defer="needs AC penetration loader"))
    Q.append(Hyp("H055", "UHI intensity", "extratrees", defer="needs UHI dataset"))
    Q.append(Hyp("H056", "deprivation index", "extratrees",
                 defer="needs SVI/IMD loader"))
    Q.append(Hyp("H057", "prior_week_pscore (autocorrelation)",
                 "extratrees", ["prior_week_pscore"]))
    Q.append(Hyp("H058", "prior_4w_mean_pscore", "extratrees",
                 ["prior_4w_mean_pscore"]))
    Q.append(Hyp("H059", "tw_night x lat (vulnerability proxy)",
                 "extratrees", ["tw_night_c_max_x_lat"]))
    Q.append(Hyp("H060", "city minus country p90", "extratrees",
                 defer="needs country-level percentile aggregator"))

    # Theme 8 — air pollution (5)
    for hid, name in [
        ("H061", "PM2.5 weekly mean"),
        ("H062", "O3 weekly mean"),
        ("H063", "wildfire smoke flag"),
        ("H064", "PM2.5 x tw_night"),
        ("H065", "O3 8-hour daily max"),
    ]:
        Q.append(Hyp(hid, name, "extratrees", defer="needs air-quality loader"))

    # Theme 9 — regional dummies vs per-city (4)
    Q.append(Hyp("H066", "country fixed effects",
                 "extratrees",
                 [f"country_{cn}" for cn in
                  ("US", "FR", "GB", "ES", "IT", "DE", "GR", "PT", "RO",
                   "AT", "PL", "SE", "DK", "IE", "NL")]))
    Q.append(Hyp("H067", "city fixed effects already in baseline (sanity)",
                 "extratrees", []))   # baseline already has city one-hot
    Q.append(Hyp("H068", "per-city ensemble", "extratrees",
                 defer="time budget; deferred to Phase 2.5"))
    Q.append(Hyp("H069", "Köppen-cluster ensemble", "extratrees",
                 defer="time budget"))

    # Theme 10 — target transforms (5)
    Q.append(Hyp("H070", "log-rate target (gated)", "extratrees",
                 defer="needs population column"))
    Q.append(Hyp("H071", "raw excess_deaths target (already baseline)",
                 "extratrees", []))
    Q.append(Hyp("H072", "binary classifier on p>=0.10",
                 "extratrees",
                 defer="evaluator regresses excess_deaths; classifier-only run skipped"))
    Q.append(Hyp("H073", "binary classifier on p>=0.20", "extratrees",
                 defer="same as H072"))
    Q.append(Hyp("H074", "age-standardised mortality rate", "extratrees",
                 defer="needs age strata"))

    # Theme 11 — survival/time-to-event (3)
    Q.append(Hyp("H075", "predict lag heat->mortality peak", "extratrees",
                 defer="new target family — Phase 2.5"))
    Q.append(Hyp("H076", "survival weeks-to-pscore-neg", "extratrees",
                 defer="new target family"))
    Q.append(Hyp("H077", "quantile regression tau=0.95", "lightgbm",
                 model_kw={"objective": "quantile", "alpha": 0.95}))

    # Theme 12 — DLNM cross-basis (2)
    Q.append(Hyp("H078", "DLNM-like dry-bulb cross-basis weekly lag1..4",
                 "extratrees",
                 ["tmax_c_mean_lag1", "tmax_c_mean_lag2",
                  "tmax_c_mean_lag3", "tmax_c_mean_lag4"]))
    Q.append(Hyp("H079", "penalised DLNM", "extratrees",
                 defer="needs P-spline DLNM library"))

    # Theme 13 — hyperparameter sweeps (6)
    Q.append(Hyp("H080", "LightGBM max_depth=8", "lightgbm",
                 model_kw={"max_depth": 8}))
    Q.append(Hyp("H081", "LightGBM lr=0.02 n=2000", "lightgbm",
                 model_kw={"learning_rate": 0.02, "n_estimators": 2000}))
    Q.append(Hyp("H082", "LightGBM min_child_samples=20", "lightgbm",
                 model_kw={"min_child_samples": 20}))
    Q.append(Hyp("H083", "LightGBM subsample=0.8 cb=0.8", "lightgbm",
                 model_kw={"subsample": 0.8, "colsample_bytree": 0.8}))
    Q.append(Hyp("H084", "LightGBM num_leaves=63", "lightgbm",
                 model_kw={"num_leaves": 63}))
    Q.append(Hyp("H085", "LightGBM monotone constraints (gated)",
                 "lightgbm", defer="constraint-vector building requires per-feature mapping"))

    # Theme 14 — model-family pivots (8)
    Q.append(Hyp("H086", "XGBoost re-pivot", "xgboost", []))
    Q.append(Hyp("H087", "ExtraTrees re-pivot (current best)", "extratrees", []))
    Q.append(Hyp("H088", "RandomForest re-pivot", "randomforest", []))
    Q.append(Hyp("H089", "Ridge sanity check", "ridge", []))
    Q.append(Hyp("H090", "Quantile LGBM tau=0.9", "lightgbm",
                 model_kw={"objective": "quantile", "alpha": 0.9}))
    Q.append(Hyp("H091", "Poisson LGBM (gated)", "lightgbm",
                 defer="Poisson on excess_deaths needs non-negative target"))
    Q.append(Hyp("H092", "Tweedie LGBM (gated)", "lightgbm",
                 defer="Tweedie on excess_deaths needs non-negative target"))
    Q.append(Hyp("H093", "stacked DLNM+LGBM", "lightgbm",
                 defer="stacking — Phase 2.5"))

    # Theme 15 — reanalysis (3)
    Q.append(Hyp("H094", "ERA5-Land replacement", "extratrees", defer="needs ERA5"))
    Q.append(Hyp("H095", "UHI correction", "extratrees", defer="needs ERA5"))
    Q.append(Hyp("H096", "HadISDH climatology", "extratrees", defer="needs HadISDH"))

    # Theme 16 — drought (3)
    Q.append(Hyp("H097", "SPI-3", "extratrees", defer="needs precipitation"))
    Q.append(Hyp("H098", "30-day precipitation anomaly", "extratrees",
                 defer="needs precipitation"))
    Q.append(Hyp("H099", "soil moisture percentile", "extratrees",
                 defer="needs ERA5-Land"))

    # Theme 17 — calendar (4)
    Q.append(Hyp("H100", "week-of-year cyclic", "extratrees",
                 ["week_of_year_sin", "week_of_year_cos"]))
    Q.append(Hyp("H101", "holiday flag", "extratrees", defer="needs holiday calendar"))
    Q.append(Hyp("H102", "tw_night x sin(week)", "extratrees",
                 ["tw_night_x_sin_week"]))
    Q.append(Hyp("H103", "days_since_jun1", "extratrees", ["days_since_jun1"]))

    # Theme 18 — pandemic (2)
    Q.append(Hyp("H104", "keep COVID weeks + dummy", "extratrees",
                 defer="changes panel composition; would invalidate compare"))
    Q.append(Hyp("H105", "Farrington baseline", "extratrees",
                 defer="needs Farrington baseline rebuild"))

    # Theme 19 — external shock (3)
    Q.append(Hyp("H106", "Storm Events Excessive Heat flag", "extratrees",
                 defer="needs Storm Events join"))
    Q.append(Hyp("H107", "power outage flag", "extratrees", defer="needs outage data"))
    Q.append(Hyp("H108", "wildfire acres burned", "extratrees", defer="needs NIFC"))

    # Theme 20 — calibration (4)
    for hid, name in [
        ("H109", "isotonic post-calibration"),
        ("H110", "Platt post-calibration"),
        ("H111", "conformal MAPIE"),
        ("H112", "focal loss"),
    ]:
        Q.append(Hyp(hid, name, "extratrees",
                     defer="post-calibration on regressor not directly comparable"))

    # Theme 21 — forecasting horizon (4)
    Q.append(Hyp("H113", "nowcast horizon 0 (=baseline)", "extratrees", []))
    Q.append(Hyp("H114", "1-week-ahead lagged features", "extratrees",
                 ["tw_c_mean_lag1", "tmax_c_mean_lag1", "tmin_c_mean_lag1",
                  "tw_night_c_max_lag1"]))
    Q.append(Hyp("H115", "2-week-ahead lagged features", "extratrees",
                 ["tw_c_mean_lag2", "tmax_c_mean_lag2", "tmin_c_mean_lag2",
                  "tw_night_c_max_lag2"]))
    Q.append(Hyp("H116", "3-week-ahead lagged features", "extratrees",
                 ["tw_c_mean_lag3", "tmax_c_mean_lag3", "tmin_c_mean_lag3",
                  "tw_night_c_max_lag3"]))

    return Q


# ---------------------------------------------------------------- main loop
def keep_threshold(best_so_far: float) -> float:
    return best_so_far - max(0.5, 0.01 * best_so_far)


def run_phase2() -> None:
    panel = _prep_panel()
    print(f"Phase 2 cleaned panel: rows={len(panel)} cities={panel['city'].nunique()}")
    print("per-city counts:")
    print(panel["city"].value_counts().sort_index().to_string())

    _init_results(RESULTS_PATH)

    queue = build_queue()
    print(f"\nQueue size: {len(queue)} hypotheses")

    # We start from the Phase 1 best (ExtraTrees on baseline). Re-establish.
    print("\n=== Phase 2 starting reference: ExtraTrees on baseline ===")
    base_metrics = _cv_run(panel, BASELINE_FEATURES_WITH_CITY, lambda: make_et())
    print(f"  baseline ExtraTrees MAE={base_metrics['mae_deaths']:.3f}  "
          f"R2={base_metrics['r2']:.4f}  AUC={base_metrics['auc_lethal']:.4f}")
    best_so_far = base_metrics["mae_deaths"]
    best_features = list(BASELINE_FEATURES_WITH_CITY)
    best_factory_label = ("extratrees", {})
    best_target_transform = None
    best_metrics = base_metrics

    keep_log: List[Tuple[str, str, float, float, float, float]] = []
    summary_rows: List[Dict] = []
    flagship_results: Dict[str, Dict] = {}

    t_start = time.time()
    for h in queue:
        t0 = time.time()
        if h.defer:
            metrics = {"mae_deaths": float("nan"), "rmse_deaths": float("nan"),
                       "r2": float("nan"), "auc_lethal": float("nan"),
                       "brier_lethal": float("nan")}
            note = f"DEFER ({h.defer})"
            decision = "DEFER"
        else:
            try:
                # Compose: previous best feature set + new columns (deduped, in panel)
                feat_cols = list(dict.fromkeys(best_features + h.add_cols))
                feat_cols = [c for c in feat_cols if c in panel.columns]
                metrics = _cv_run(
                    panel, feat_cols, h.factory(),
                    target_transform=h.target_transform,
                )
                thr = keep_threshold(best_so_far)
                if metrics["mae_deaths"] < thr:
                    decision = "KEEP"
                    delta = best_so_far - metrics["mae_deaths"]
                    keep_log.append((h.exp_id, h.desc, metrics["mae_deaths"],
                                     metrics["r2"], metrics["auc_lethal"], delta))
                    best_so_far = metrics["mae_deaths"]
                    best_features = feat_cols
                    best_factory_label = (h.model, dict(h.model_kw))
                    best_target_transform = h.target_transform
                    best_metrics = metrics
                else:
                    decision = "REVERT"
                note = f"5-fold CV n={len(panel)} {decision}"
            except Exception as exc:  # noqa: BLE001
                metrics = {"mae_deaths": float("nan"), "rmse_deaths": float("nan"),
                           "r2": float("nan"), "auc_lethal": float("nan"),
                           "brier_lethal": float("nan")}
                note = f"ERROR ({type(exc).__name__}: {exc})[:80]"
                decision = "ERROR"
        dt = time.time() - t0
        added = ",".join(h.add_cols) if h.add_cols else "(none)"
        _append_result(RESULTS_PATH, h.exp_id, h.desc, h.model, added,
                       metrics, f"{note} wall={dt:.1f}s")
        summary_rows.append({
            "exp_id": h.exp_id, "desc": h.desc, "model": h.model,
            "decision": decision,
            "mae": metrics["mae_deaths"], "r2": metrics["r2"],
            "auc": metrics["auc_lethal"], "brier": metrics["brier_lethal"],
            "wall_s": dt,
        })
        if h.exp_id.startswith("H0") and int(h.exp_id[1:]) <= 22:
            flagship_results[h.exp_id] = {
                "decision": decision, "metrics": metrics, "desc": h.desc,
            }
        print(f"  {h.exp_id} {decision:<6} MAE={metrics['mae_deaths']:.3f}  "
              f"AUC={metrics['auc_lethal']:.4f}  ({h.desc[:60]})")

    print(f"\nTotal Phase 2 wall time: {time.time()-t_start:.1f}s")

    # ----- summaries
    print("\n=========================================================")
    print("PHASE 2 SUMMARY")
    print("=========================================================")

    df_sum = pd.DataFrame(summary_rows)
    print("\nKEEP/REVERT/DEFER counts:")
    print(df_sum["decision"].value_counts().to_string())

    keeps = df_sum[df_sum["decision"] == "KEEP"].sort_values("mae")
    print("\nTop 15 KEEPs by MAE:")
    if len(keeps) > 0:
        cols = ["exp_id", "desc", "mae", "r2", "auc"]
        print(keeps.head(15)[cols].to_string(index=False))
    else:
        print("  (no KEEPs)")

    print(f"\nPhase 2 final best:")
    print(f"  model = {best_factory_label[0]} kw={best_factory_label[1]}")
    print(f"  features = {len(best_features)} cols (last added shown)")
    if len(best_features) > len(BASELINE_FEATURES_WITH_CITY):
        print("  added on top of baseline:",
              [c for c in best_features if c not in BASELINE_FEATURES_WITH_CITY])
    print(f"  MAE={best_metrics['mae_deaths']:.3f}  "
          f"RMSE={best_metrics['rmse_deaths']:.3f}  "
          f"R2={best_metrics['r2']:.4f}  "
          f"AUC={best_metrics['auc_lethal']:.4f}  "
          f"Brier={best_metrics['brier_lethal']:.4f}")

    # Flagship verdict
    print("\n=== Flagship night-time wet-bulb verdict (H001-H022) ===")
    f_keep = sum(1 for k, v in flagship_results.items() if v["decision"] == "KEEP")
    f_rev = sum(1 for k, v in flagship_results.items() if v["decision"] == "REVERT")
    f_def = sum(1 for k, v in flagship_results.items() if v["decision"] == "DEFER")
    print(f"  KEEP={f_keep}  REVERT={f_rev}  DEFER={f_def}  / 22")
    # best individual flagship
    indivs = [(k, v["metrics"]["mae_deaths"], v["metrics"]["auc_lethal"], v["desc"])
              for k, v in flagship_results.items()
              if v["decision"] in ("KEEP", "REVERT")
              and not np.isnan(v["metrics"]["mae_deaths"])]
    indivs.sort(key=lambda r: r[1])
    print("  Best individual flagship MAE (post baseline):")
    for k, m, a, d in indivs[:5]:
        print(f"    {k} MAE={m:.3f} AUC={a:.4f}  {d}")

    # Stacked: try adding ALL 22 flagship features
    flagship_cols = []
    for h in queue:
        if h.exp_id.startswith("H0") and int(h.exp_id[1:]) <= 22 and not h.defer:
            flagship_cols += h.add_cols
    flagship_cols = [c for c in dict.fromkeys(flagship_cols) if c in panel.columns]
    stacked_cols = list(dict.fromkeys(BASELINE_FEATURES_WITH_CITY + flagship_cols))
    stacked = _cv_run(panel, stacked_cols, lambda: make_et())
    print(f"\n  Stacked all 22 flagship feats on ExtraTrees baseline: "
          f"MAE={stacked['mae_deaths']:.3f} R2={stacked['r2']:.4f} "
          f"AUC={stacked['auc_lethal']:.4f}")

    # Single-feature classifier: tw_night_c_max alone vs baseline AUC
    only_night = _cv_run(panel,
                         ["tw_night_c_max"] + [c for c in BASELINE_FEATURES_WITH_CITY
                                               if c.startswith("city_") or c in ("lat", "log_population")],
                         lambda: make_et())
    print(f"  ExtraTrees(city + lat + log_pop + tw_night_c_max) only: "
          f"MAE={only_night['mae_deaths']:.3f} AUC={only_night['auc_lethal']:.4f}")
    base_no_atm = _cv_run(panel,
                          [c for c in BASELINE_FEATURES_WITH_CITY
                           if c.startswith("city_") or c in ("lat", "log_population")],
                          lambda: make_et())
    print(f"  ExtraTrees(city + lat + log_pop) only (no atmosphere): "
          f"MAE={base_no_atm['mae_deaths']:.3f} AUC={base_no_atm['auc_lethal']:.4f}")

    # Tree-to-linear ratio
    rdg_metrics = _cv_run(panel, best_features, lambda: make_rdg())
    if rdg_metrics["mae_deaths"] > 0:
        ratio = best_metrics["mae_deaths"] / rdg_metrics["mae_deaths"]
        verdict = ("TREES DO NON-LINEAR WORK (ratio < 0.5)"
                   if ratio < 0.5 else "RELATIONSHIP MOSTLY LINEAR")
        print(f"\n  Tree-to-linear ratio on Phase 2 best feature set: "
              f"{best_metrics['mae_deaths']:.2f} / {rdg_metrics['mae_deaths']:.2f} "
              f"= {ratio:.3f}  -- {verdict}")

    # E00 baseline comparison
    e00_mae = 47.488
    e00_r2 = 0.6974
    e00_auc = 0.8277
    print(f"\n  Improvement E00 -> Phase 2 best:")
    print(f"    MAE: {e00_mae:.3f} -> {best_metrics['mae_deaths']:.3f} "
          f"({(e00_mae - best_metrics['mae_deaths']) / e00_mae * 100:+.2f}%)")
    print(f"    R2:  {e00_r2:.4f} -> {best_metrics['r2']:.4f} "
          f"({(best_metrics['r2'] - e00_r2) * 100:+.2f}pp)")
    print(f"    AUC: {e00_auc:.4f} -> {best_metrics['auc_lethal']:.4f} "
          f"({(best_metrics['auc_lethal'] - e00_auc) * 100:+.2f}pp)")

    # Deferred reasons
    defers = df_sum[df_sum["decision"] == "DEFER"]
    print(f"\nDeferred ({len(defers)}):")
    for _, r in defers.iterrows():
        print(f"  {r['exp_id']}: {r['desc']}")


if __name__ == "__main__":
    run_phase2()
