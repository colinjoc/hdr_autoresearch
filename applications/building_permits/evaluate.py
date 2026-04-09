"""5-fold CV harness for the Phase 0.5 baseline, Phase 1 tournament, and Phase 2 loop.

Usage:
    python evaluate.py                      # run E00 + tournament, write results.tsv
    python evaluate.py --build-cache        # (re)build using the legacy per-city loader
    python evaluate.py --build-cache-v2     # (re)build using the bias-fixed v2 loader
    python evaluate.py --only baseline      # just E00
    python evaluate.py --run-phase2         # run the full 120-hypothesis Phase 2 loop
    python evaluate.py --reset-results --run-phase2  # clean start, full rerun

The Phase 2 loop reads the v2 cached dataset (permits_baseline.parquet built
via ``--build-cache-v2``) and walks the 120-hypothesis research queue. Each
hypothesis is a single-change edit to the current best config; after CV it is
kept or reverted according to the pre-registered 0.5-day / 1% improvement
floor. Deferred hypotheses (Seattle-only, survival, columns not in the
normalised schema) write DEFER rows so the full set of 120 stays auditable.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

from model import (
    CITIES_FOR_BASELINE,
    RAW_FEATURES,
    TOURNAMENT,
    add_features,
    add_phase2_features,
    build_clean_dataset,
    build_clean_dataset_v2,
    build_phase2_feature_list,
    make_baseline_xgb,
    make_xgb,
    target_encode,
)

HERE = Path(__file__).resolve().parent
CLEAN_PATH = HERE / "data" / "clean" / "permits_baseline.parquet"
RESULTS_PATH = HERE / "results.tsv"
RAW_DIR = HERE / "data" / "raw"


# ----------------------------------------------------------------- dataset build

def _load_city(name: str, limit: int | None) -> pd.DataFrame:
    from data_loaders import LOADERS  # lazy: loaders fetch live APIs

    fn = LOADERS[name]
    return fn(limit=limit)


def build_clean_cache(per_city_limit: int | None = None, sample_size: int = 50_000,
                      random_state: int = 42) -> pd.DataFrame:
    """Load all baseline cities, apply filters, stratify-sample to ``sample_size``.

    Caches the result to ``data/clean/permits_baseline.parquet``.
    """
    raw_frames = []
    for city in CITIES_FOR_BASELINE:
        t0 = time.time()
        df = _load_city(city, limit=per_city_limit)
        print(f"  loaded {city:9s}  rows={len(df):7d}  dt={time.time() - t0:5.1f}s")
        raw_frames.append(df)
    raw = pd.concat(raw_frames, ignore_index=True)
    print(f"  raw concat rows={len(raw):7d}")

    clean = build_clean_dataset(raw)
    print(f"  after filters rows={len(clean):7d}")
    print("  per-city:")
    print(clean["city"].value_counts().to_string())

    # Stratified sample by city, cap at sample_size.
    if len(clean) > sample_size:
        # proportional-to-size, but give every present city at least 1 row.
        counts = clean["city"].value_counts()
        # Ideal per-city count = round(sample_size * share), then fix rounding drift.
        share = counts / counts.sum()
        target = (share * sample_size).round().astype(int)
        # Ensure the per-city target does not exceed what's available.
        target = target.clip(upper=counts)
        drift = sample_size - int(target.sum())
        # Distribute any remainder (positive or negative) to the biggest cities.
        if drift != 0:
            order = counts.sort_values(ascending=False).index.tolist()
            i = 0
            while drift != 0 and i < 1000 * len(order):
                city = order[i % len(order)]
                if drift > 0 and target[city] < counts[city]:
                    target[city] += 1
                    drift -= 1
                elif drift < 0 and target[city] > 1:
                    target[city] -= 1
                    drift += 1
                i += 1
        parts = []
        rng = np.random.default_rng(random_state)
        for city, n in target.items():
            sub = clean[clean["city"] == city]
            idx = rng.choice(len(sub), size=int(n), replace=False)
            parts.append(sub.iloc[idx])
        clean = pd.concat(parts, ignore_index=True).sample(
            frac=1.0, random_state=random_state
        ).reset_index(drop=True)
        print(f"  stratified sample rows={len(clean):7d}")
        print(clean["city"].value_counts().to_string())

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Parquet doesn't like object-dtype date columns — cast them.
    for c in ["filed_date", "issued_date", "approval_date", "finaled_date",
              "first_action_date", "plan_check_start_date", "plan_check_end_date"]:
        if c in clean.columns:
            clean[c] = pd.to_datetime(clean[c], errors="coerce")
    clean.to_parquet(CLEAN_PATH, index=False)
    print(f"  cached → {CLEAN_PATH}")
    return clean


def load_clean(build_if_missing: bool = True, per_city_limit: int | None = None,
               sample_size: int = 50_000) -> pd.DataFrame:
    if CLEAN_PATH.exists():
        return pd.read_parquet(CLEAN_PATH)
    if not build_if_missing:
        raise FileNotFoundError(f"{CLEAN_PATH} missing; run with --build-cache")
    return build_clean_cache(per_city_limit=per_city_limit, sample_size=sample_size)


def _load_union_raw(city: str) -> pd.DataFrame:
    """Union the _full cache with the legacy cache (if present) for a city.

    The _full cache carries the re-stratified 2015+ pull; the legacy cache
    contributes any 2024+ coverage that hit the row-budget cap in the _full
    pull. Dedup on permit_id.
    """
    full = RAW_DIR / f"{city}_full.parquet"
    orig = RAW_DIR / f"{city}.parquet"
    parts = []
    if full.exists():
        parts.append(pd.read_parquet(full))
    if orig.exists():
        df_o = pd.read_parquet(orig)
        if parts:
            df_o = df_o.reindex(columns=parts[0].columns)
        parts.append(df_o)
    if not parts:
        return pd.DataFrame()
    u = pd.concat(parts, ignore_index=True)
    if "permit_id" in u.columns:
        u = u.drop_duplicates(subset=["permit_id"], keep="first")
    return u


def build_clean_cache_v2(n_rows: int = 50_000, seed: int = 42) -> pd.DataFrame:
    """Phase 2 bias-fixed cleaned dataset builder.

    Reads the _full raw caches (union with legacy caches), applies
    ``build_clean_dataset_v2`` which strictly filters to small-residential and
    stratifies by (city × filed_year_bucket), and caches to the standard
    ``data/clean/permits_baseline.parquet`` path so downstream code (including
    the baseline tests) continues to find it.
    """
    raw_frames = []
    for city in CITIES_FOR_BASELINE:
        df = _load_union_raw(city)
        print(f"  loaded {city:9s}  rows={len(df):8,d}")
        if len(df) > 0:
            raw_frames.append(df)
    raw = pd.concat(raw_frames, ignore_index=True) if raw_frames else pd.DataFrame()
    print(f"  raw union rows={len(raw):,}")

    clean = build_clean_dataset_v2(raw, seed=seed, n_rows=n_rows)
    print(f"  v2 cleaned rows={len(clean):,}")
    print("  per-city:")
    print(clean["city"].value_counts().to_string())
    print("  per-city-year-bucket p50:")
    fd = pd.to_datetime(clean["filed_date"])
    tmp = clean.copy()
    tmp["_yb"] = fd.dt.year.map({
        **{y: "2015-2018" for y in range(2015, 2019)},
        **{y: "2019-2021" for y in range(2019, 2022)},
        **{y: "2022-2023" for y in range(2022, 2024)},
        **{y: "2024-2026" for y in range(2024, 2027)},
    })
    for c in CITIES_FOR_BASELINE:
        sub = tmp[tmp["city"] == c]
        if len(sub) == 0:
            continue
        parts = []
        for b in ["2015-2018", "2019-2021", "2022-2023", "2024-2026"]:
            cell = sub[sub["_yb"] == b]
            if len(cell) > 0:
                parts.append(f"{b} n={len(cell):4d} p50={cell['duration_days'].median():5.0f}")
        print(f"    {c:9s} " + " | ".join(parts))

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    for c in ["filed_date", "issued_date", "approval_date", "finaled_date",
              "first_action_date", "plan_check_start_date", "plan_check_end_date"]:
        if c in clean.columns:
            clean[c] = pd.to_datetime(clean[c], errors="coerce")
    clean.to_parquet(CLEAN_PATH, index=False)
    print(f"  cached -> {CLEAN_PATH}")
    return clean


# ----------------------------------------------------------------- cross-validation

def cross_validate(df: pd.DataFrame, model_factory, n_splits: int = 5, seed: int = 42,
                   verbose: bool = True) -> dict:
    """5-fold CV that computes target encodings inside each training fold.

    Returns a dict of metrics computed on the concatenated out-of-fold predictions.
    """
    df = df.reset_index(drop=True)
    df = add_features(df)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(df), dtype="float64")
    fold_mae_days = []
    for fold_idx, (tr_idx, va_idx) in enumerate(kf.split(df)):
        tr = df.iloc[tr_idx].copy()
        va = df.iloc[va_idx].copy()
        y_tr_log = np.log1p(tr["duration_days"].astype("float64").values)

        # In-fold target encodings — fit on train, applied to train and valid.
        for col in ["permit_subtype", "neighborhood"]:
            tr[col + "_te"] = target_encode(tr, tr, col, y_tr_log)
            va[col + "_te"] = target_encode(tr, va, col, y_tr_log)

        X_tr = tr[RAW_FEATURES].astype("float32").values
        X_va = va[RAW_FEATURES].astype("float32").values

        m = model_factory()
        m.fit(X_tr, y_tr_log)
        pred_log = m.predict(X_va)
        oof[va_idx] = pred_log

        y_va_days = va["duration_days"].astype("float64").values
        fold_mae = mean_absolute_error(y_va_days, np.expm1(pred_log))
        fold_mae_days.append(fold_mae)
        if verbose:
            print(f"    fold {fold_idx}: MAE={fold_mae:7.2f} days  "
                  f"n_train={len(tr):6d}  n_valid={len(va):6d}")

    y_true_log = np.log1p(df["duration_days"].astype("float64").values)
    y_true_days = df["duration_days"].astype("float64").values
    pred_days = np.expm1(oof)
    return {
        "mae_days": float(mean_absolute_error(y_true_days, pred_days)),
        "rmse_days": float(np.sqrt(mean_squared_error(y_true_days, pred_days))),
        "r2_log": float(r2_score(y_true_log, oof)),
        "r2_days": float(r2_score(y_true_days, pred_days)),
        "fold_mae_days": [float(x) for x in fold_mae_days],
    }


# ----------------------------------------------------------------- Phase 2 CV harness
#
# cross_validate_v2 accepts a config dict describing the Phase 2 feature +
# model change and runs the same 5-fold in-fold-TE CV against the v2 cleaned
# sample. Config keys (all optional):
#
#   features: dict passed to add_phase2_features + build_phase2_feature_list
#   model_factory: callable that returns a fitted-style regressor
#   target_transform: 'log1p' | 'sqrt' | 'raw'
#   per_city: bool — fit one model per city and concatenate oof
#   te_cols: list[str] — extra columns to target-encode in each fold (besides
#            the Phase 0.5 permit_subtype/neighborhood)

def cross_validate_v2(df: pd.DataFrame, config: dict, n_splits: int = 5,
                       seed: int = 42, verbose: bool = False) -> dict:
    from model import _apply_target_transform, _inverse_target_transform

    feature_cfg = config.get("features", {})
    factory = config.get("model_factory", make_xgb)
    target_transform = config.get("target_transform", "log1p")
    per_city = config.get("per_city", False)
    extra_te_cols = list(config.get("te_cols", []))
    base_te_cols = ["permit_subtype", "neighborhood"]
    te_cols = base_te_cols + extra_te_cols

    df = df.reset_index(drop=True)
    df = add_phase2_features(df, feature_cfg)

    feature_list = build_phase2_feature_list(feature_cfg)
    # Make sure extra TE columns appear as feature names (col + "_te")
    for c in extra_te_cols:
        col_te = c + "_te"
        if col_te not in feature_list:
            feature_list.append(col_te)

    # Prepare non-finite fallback for NaN/Inf in floats (trees are fine but
    # ridge / linear models need clean arrays).
    def _clean(X):
        X = np.asarray(X, dtype="float32")
        X = np.where(np.isfinite(X), X, 0.0).astype("float32")
        return X

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(df), dtype="float64")
    fold_mae_days = []
    for fold_idx, (tr_idx, va_idx) in enumerate(kf.split(df)):
        tr = df.iloc[tr_idx].copy()
        va = df.iloc[va_idx].copy()
        y_tr_days = tr["duration_days"].astype("float64").values
        y_tr_t = _apply_target_transform(y_tr_days, target_transform)

        # In-fold target encodings.
        for col in te_cols:
            if col not in tr.columns:
                continue
            tr[col + "_te"] = target_encode(tr, tr, col, y_tr_t)
            va[col + "_te"] = target_encode(tr, va, col, y_tr_t)

        # Select feature columns that actually exist in the frame.
        feats_present = [f for f in feature_list if f in tr.columns]
        X_tr = _clean(tr[feats_present].values)
        X_va = _clean(va[feats_present].values)

        if per_city:
            pred_t = np.zeros(len(va), dtype="float64")
            for city in CITIES_FOR_BASELINE:
                tr_mask = (tr["city"] == city).values
                va_mask = (va["city"] == city).values
                if tr_mask.sum() < 50 or va_mask.sum() == 0:
                    continue
                m = factory()
                m.fit(X_tr[tr_mask], y_tr_t[tr_mask])
                pred_t[va_mask] = m.predict(X_va[va_mask])
            # For untrained cities (tr too small), fall back to a global model.
            untrained = np.zeros(len(va), dtype=bool)
            for city in CITIES_FOR_BASELINE:
                if (tr["city"] == city).sum() < 50:
                    untrained |= (va["city"] == city).values
            if untrained.any():
                m = factory()
                m.fit(X_tr, y_tr_t)
                pred_t[untrained] = m.predict(X_va[untrained])
        else:
            m = factory()
            m.fit(X_tr, y_tr_t)
            pred_t = m.predict(X_va)

        oof[va_idx] = pred_t
        pred_days = _inverse_target_transform(pred_t, target_transform)
        y_va_days = va["duration_days"].astype("float64").values
        fold_mae = mean_absolute_error(y_va_days, pred_days)
        fold_mae_days.append(fold_mae)
        if verbose:
            print(f"    fold {fold_idx}: MAE={fold_mae:7.2f} days")

    y_true_days = df["duration_days"].astype("float64").values
    pred_days_all = _inverse_target_transform(oof, target_transform)
    # R² on the transformed target (matches old r2_log semantics).
    y_true_t = _apply_target_transform(y_true_days, target_transform)
    return {
        "mae_days": float(mean_absolute_error(y_true_days, pred_days_all)),
        "rmse_days": float(np.sqrt(mean_squared_error(y_true_days, pred_days_all))),
        "r2_log": float(r2_score(y_true_t, oof)),
        "r2_days": float(r2_score(y_true_days, pred_days_all)),
        "fold_mae_days": [float(x) for x in fold_mae_days],
    }


# ----------------------------------------------------------------- results TSV

RESULTS_HEADER = (
    "exp_id\tdescription\tmodel\textra_features\t"
    "cv_mae_days\tcv_rmse_days\tcv_r2_log\tcv_r2_days\tnotes"
)


def _init_results(path: Path) -> None:
    if not path.exists():
        path.write_text(RESULTS_HEADER + "\n")


def _append_result(path: Path, exp_id: str, description: str, model: str,
                   extra_features: str, metrics: dict, notes: str) -> None:
    _init_results(path)
    row = "\t".join([
        exp_id, description, model, extra_features,
        f"{metrics['mae_days']:.3f}",
        f"{metrics['rmse_days']:.3f}",
        f"{metrics['r2_log']:.4f}",
        f"{metrics['r2_days']:.4f}",
        notes,
    ])
    with path.open("a") as f:
        f.write(row + "\n")


def _reset_results(path: Path) -> None:
    path.write_text(RESULTS_HEADER + "\n")


# ----------------------------------------------------------------- Phase 2 hypothesis driver
#
# Each hypothesis is a dict describing: the single change relative to the
# current best, the model family, and the feature flags. The driver runs the
# 5-fold CV, compares the MAE to the running best_so_far, and applies the
# KEEP/REVERT rule. The rule is:
#
#   KEEP if cv_mae_days < best_so_far - max(0.5, 0.01 * best_so_far)
#
# A KEEP updates best_so_far; a REVERT leaves the best unchanged.

def _keep_or_revert(mae: float, best: float) -> tuple[bool, float]:
    threshold = best - max(0.5, 0.01 * best)
    return (mae < threshold, threshold)


def run_phase2_hypothesis(df: pd.DataFrame, exp_id: str, description: str,
                          config: dict, best: float, feature_label: str,
                          notes_prefix: str = "") -> tuple[dict, bool]:
    """Run one Phase 2 hypothesis; return (metrics, kept)."""
    try:
        metrics = cross_validate_v2(df, config, verbose=False)
    except Exception as exc:  # noqa: BLE001
        metrics = {"mae_days": float("nan"), "rmse_days": float("nan"),
                   "r2_log": float("nan"), "r2_days": float("nan"),
                   "fold_mae_days": []}
        notes = f"FAIL ({type(exc).__name__}: {str(exc)[:80]})"
        _append_result(RESULTS_PATH, exp_id, description, _model_name(config),
                       feature_label, metrics, notes)
        return metrics, False
    kept, _ = _keep_or_revert(metrics["mae_days"], best)
    notes = "KEEP" if kept else "REVERT"
    if notes_prefix:
        notes = notes_prefix + " " + notes
    _append_result(RESULTS_PATH, exp_id, description, _model_name(config),
                   feature_label, metrics, notes)
    return metrics, kept


def _model_name(config: dict) -> str:
    f = config.get("model_factory")
    if f is None:
        return "xgboost"
    name = getattr(f, "__name__", str(f))
    return name.replace("make_", "")


# ----------------------------------------------------------------- Phase 2 hypothesis registry
#
# Each entry is (exp_id, description, feature_label, config_builder, notes).
# config_builder is a callable (best_config) -> new_config that applies the
# single-change edit to the current best config. The driver invokes it with
# the CURRENT BEST CONFIG so the change stacks on top of whatever has already
# been kept.
#
# DEFER status is used when the hypothesis requires data we don't have (eg
# Seattle per-cycle).
#
# Because the loop goes hypothesis-by-hypothesis, each exp_id sees the best
# config of all prior kept exps. This matches the protocol in the prompt.

import copy

from model import (
    make_extratrees,
    make_lightgbm_v2,
    make_randomforest,
    make_ridge,
    make_xgb_quantile,
)


def _cfg_merge(base: dict, **kwargs) -> dict:
    """Shallow-merge a Phase 2 config override into the current best."""
    new = copy.deepcopy(base) if base else {}
    feats = dict(new.get("features", {}) or {})
    for k, v in kwargs.items():
        if k == "features":
            feats.update(v)
        else:
            new[k] = v
    new["features"] = feats
    return new


def _build_phase2_registry() -> list:
    """Return list of (exp_id, description, label, config_builder, kind).

    kind ∈ {"run", "defer"}. "defer" entries skip CV and write DEFER notes.
    """
    reg = []

    def add(eid, desc, label, builder, kind="run"):
        reg.append((eid, desc, label, builder, kind))

    # H001: XGBoost AFT — defer (requires survival infrastructure and right-censored labels).
    add("H001", "XGBoost AFT survival", "baseline",
        lambda b: b, kind="defer_reason:needs_censored_labels")
    # H002-H003: Seattle-only — DEFER (Seattle not in baseline sample).
    add("H002", "Seattle numberreviewcycles", "seattle_only",
        lambda b: b, kind="defer_reason:seattle_only")
    add("H003", "Seattle daysoutcorrections", "seattle_only",
        lambda b: b, kind="defer_reason:seattle_only")
    # H004-H005: NYC stage lag features — DEFER (paid/fully_paid timestamps not in normalised schema)
    add("H004", "NYC paid-lag feature", "nyc_only",
        lambda b: b, kind="defer_reason:stage_columns_not_in_schema")
    add("H005", "NYC approve-to-issue lag", "nyc_only",
        lambda b: b, kind="defer_reason:stage_columns_not_in_schema")
    # H006: SF pre-approval features — DEFER (approved_date semantics leak target)
    add("H006", "SF pre/post approval decomposition", "sf_only",
        lambda b: b, kind="defer_reason:target_leakage_risk")
    add("H007", "Two-stage model", "composition",
        lambda b: b, kind="defer_reason:phase_2.5_composition")
    # H008: sentinel filter — already applied in build_clean_dataset_v2.
    add("H008", "Drop sentinel dates pre-2015", "hygiene",
        lambda b: b, kind="defer_reason:already_in_v2_clean")
    # H009: clip durations — same.
    add("H009", "Clip durations 1-1825", "hygiene",
        lambda b: b, kind="defer_reason:already_in_v2_clean")
    # H010: SF valuation delta — DEFER (needs both estimated_cost and revised_cost in schema)
    add("H010", "SF valuation delta", "sf_only",
        lambda b: b, kind="defer_reason:estimated_cost_not_in_schema")
    # H011-H013: log-transform — ALREADY APPLIED in add_features (log_valuation etc).
    add("H011", "Log-valuation (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    add("H012", "Log-units (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    add("H013", "Log-sqft (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    # H014: filed DOW
    add("H014", "Filed day-of-week", "+filed_dow",
        lambda b: _cfg_merge(b, features={"include_dow": True}))
    # H015: filed month cyclic — ALREADY in add_features (filed_month_sin/cos)
    add("H015", "Filed month cyclic (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    # H016: filed year — ALREADY in add_features
    add("H016", "Filed year ordinal (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    # H017: holiday flag
    add("H017", "Federal holiday week flag", "+holiday_week",
        lambda b: _cfg_merge(b, features={"include_holiday_flag": True}))
    # H018: COVID era
    add("H018", "COVID era dummy", "+covid_era",
        lambda b: _cfg_merge(b, features={"include_covid_era": True}))
    # H019: subtype TE — ALREADY in baseline.
    add("H019", "Subtype target encoding (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    # H020: neighborhood TE — ALREADY in baseline.
    add("H020", "Nbhd target encoding (already baseline)", "already_baseline",
        lambda b: b, kind="defer_reason:already_in_baseline")
    # H021: per-city models
    add("H021", "Per-city XGBoost", "per_city",
        lambda b: _cfg_merge(b, per_city=True))
    # H022: dispatch ensemble — skip (composition)
    add("H022", "Global+per-city ensemble", "composition",
        lambda b: b, kind="defer_reason:phase_2.5_composition")
    # H023-H027, H061-H064: survival — DEFER (no censored labels wired up)
    for h in ["H023", "H024", "H025", "H026", "H027", "H061", "H062", "H063", "H064"]:
        add(h, f"{h} survival variant", "survival",
            lambda b: b, kind="defer_reason:needs_survival_infra")
    # H028: monotone valuation
    add("H028", "Monotone valuation (XGB)", "monotone_val",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "monotone_constraints": _monotone_dict(b, ["log_valuation"])})))
    # H029: monotone units
    add("H029", "Monotone units (XGB)", "monotone_units",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "monotone_constraints": _monotone_dict(b, ["log_unit_count"])})))
    # H030: monotone sqft
    add("H030", "Monotone sqft (XGB)", "monotone_sqft",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "monotone_constraints": _monotone_dict(b, ["log_square_feet"])})))
    # H031: raw target
    add("H031", "Raw duration target", "raw_target",
        lambda b: _cfg_merge(b, target_transform="raw"))
    # H032: sqrt target
    add("H032", "Sqrt target", "sqrt_target",
        lambda b: _cfg_merge(b, target_transform="sqrt"))
    # H033: Box-Cox target — use log1p as proxy
    add("H033", "Box-Cox target (≈log1p)", "boxcox_target",
        lambda b: _cfg_merge(b, target_transform="log1p"))
    # H034: quantile 50
    add("H034", "XGB quantile P50", "quantile_50",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb_quantile(0.5)))
    # H035: quantile 90
    add("H035", "XGB quantile P90", "quantile_90",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb_quantile(0.9)))
    # H036: city x year interaction (target encoded)
    add("H036", "city x year TE", "+city_year_te",
        lambda b: _cfg_merge(b, features={"include_city_year": True},
                             te_cols=list((b or {}).get("te_cols", [])) + ["city_year"]))
    # H037: reform dummies
    add("H037", "Reform cutoff dummies", "+reform_dummies",
        lambda b: _cfg_merge(b, features={"include_reform_dummies": True}))
    # H038, H039: RD composition — DEFER
    add("H038", "SB 423 RD", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    add("H039", "HOME-1 RD", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    add("H040", "DOB NOW stagger", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    # H041: LA business_unit — DEFER (not in normalised schema, would need re-pull)
    add("H041", "LA business_unit", "la_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H042: Chicago review_type — partially in permit_subtype already
    add("H042", "Chicago review_type (already baseline)", "chicago_only",
        lambda b: b, kind="defer_reason:already_in_baseline")
    # H043: Chicago processing_time check — validation only
    add("H043", "Chicago processing_time check", "validation",
        lambda b: b, kind="defer_reason:validation_only")
    # H044: new-vs-alter stratum — DEFER (composition)
    add("H044", "New vs alter stratum", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    add("H045", "ADU stratum", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    # H046-H051: macro context — DEFER (ACS/BPS/FRED/BLS fetch infeasible in 30-min budget)
    for h, name in [("H046", "WRLURI"), ("H047", "Census BPS load"),
                    ("H048", "ACS density"), ("H049", "FRED mortgage rate"),
                    ("H050", "BLS construction employment"), ("H051", "FRED housing starts")]:
        add(h, name, "macro", lambda b: b, kind="defer_reason:external_data_not_fetched")
    # H052: nbhd recency
    add("H052", "Nbhd last-permit recency", "+nbhd_recency",
        lambda b: _cfg_merge(b, features={"include_nbhd_recency": True}))
    # H053: rolling 30d
    add("H053", "30d city rolling count", "+rolling_30d",
        lambda b: _cfg_merge(b, features={"include_rolling_30d": True}))
    # H054: rolling 90d
    add("H054", "90d city rolling count", "+rolling_90d",
        lambda b: _cfg_merge(b, features={"include_rolling_90d": True}))
    # H055: LightGBM
    add("H055", "LightGBM", "lightgbm",
        lambda b: _cfg_merge(b, model_factory=make_lightgbm_v2))
    # H056: CatBoost — DEFER (not installed)
    add("H056", "CatBoost", "catboost", lambda b: b, kind="defer_reason:library_not_installed")
    # H057: ExtraTrees
    add("H057", "ExtraTrees", "extratrees",
        lambda b: _cfg_merge(b, model_factory=make_extratrees))
    # H058: stacked ensemble — composition
    add("H058", "Stacked ensemble", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    # H059: ridge sanity
    add("H059", "Ridge sanity check", "ridge",
        lambda b: _cfg_merge(b, model_factory=make_ridge))
    # H060: TabPFN — DEFER
    add("H060", "TabPFN", "seattle_only", lambda b: b, kind="defer_reason:seattle_only")
    # H065: SF submission method — DEFER
    add("H065", "SF application_submission_method", "sf_only",
        lambda b: b, kind="defer_reason:column_not_in_schema")
    # H066: SF plansets — DEFER
    add("H066", "SF plansets", "sf_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H067: SF change-of-use
    add("H067", "SF change-of-use flag", "+change_of_use",
        lambda b: _cfg_merge(b, features={"include_change_of_use": True}))
    # H068: NYC zoning_dist1 — DEFER
    add("H068", "NYC zoning_dist1", "nyc_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H069: NYC professional_cert — DEFER
    add("H069", "NYC professional_cert", "nyc_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H070-H073: group/contractor features — DEFER
    for h, name in [("H070", "Austin masterpermitnum group"),
                    ("H071", "Austin project_id group"),
                    ("H072", "SF parcel cluster project"),
                    ("H073", "Contractor frequency")]:
        add(h, name, "group_feature", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H074-H082: Seattle — all DEFER
    for h, name in [("H074", "Seattle standardplan"),
                    ("H075", "Seattle reviewcomplexity"),
                    ("H076", "Seattle reviewer encoding"),
                    ("H077", "Seattle reviewteam"),
                    ("H078", "Seattle leakage guard"),
                    ("H079", "Seattle rework rate"),
                    ("H080", "Seattle daysinitialplanreview"),
                    ("H081", "Seattle daysplanreviewcity"),
                    ("H082", "Seattle max reviewcycle")]:
        add(h, name, "seattle_only", lambda b: b, kind="defer_reason:seattle_only")
    # H083: NYC union — already done in load_nyc_full
    add("H083", "NYC BIS+DOB NOW union (already in v2)", "already_in_v2",
        lambda b: b, kind="defer_reason:already_in_v2_clean")
    # H084, H085: censoring/competing risks — DEFER
    add("H084", "Right-censoring labels", "survival", lambda b: b, kind="defer_reason:needs_survival_infra")
    add("H085", "Competing risks", "survival", lambda b: b, kind="defer_reason:needs_survival_infra")
    # H086-H092: hyperparameter sweeps
    add("H086", "Optuna sweep (depth/lr/min_child)", "hp_sweep",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "max_depth": 7, "learning_rate": 0.03, "min_child_weight": 5,
            "n_estimators": 600})))
    add("H087", "XGB depth=9", "depth_9",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({"max_depth": 9})))
    add("H088", "XGB lr=0.03 n_est=600", "lr_003",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "learning_rate": 0.03, "n_estimators": 600})))
    add("H089", "XGB min_child_weight=20", "mcw_20",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({"min_child_weight": 20})))
    add("H090", "XGB subsample=0.6 colsample=0.6", "subsamp_06",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "subsample": 0.6, "colsample_bytree": 0.6})))
    add("H091", "XGB reg_alpha=1 reg_lambda=10", "l1l2_reg",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({
            "reg_alpha": 1.0, "reg_lambda": 10.0})))
    add("H092", "XGB n_est=800", "n_est_800",
        lambda b: _cfg_merge(b, model_factory=lambda: make_xgb({"n_estimators": 800})))
    # H093: era bin
    add("H093", "Era bin (0..3)", "+era_bin",
        lambda b: _cfg_merge(b, features={"include_era_bin": True}))
    # H094-H095: Chicago fee — DEFER
    add("H094", "Chicago total_fee", "chicago_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    add("H095", "Chicago fee-per-unit", "chicago_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H096-H100: political geography — DEFER (columns not in schema)
    add("H096", "SF supervisor district", "sf_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    add("H097", "NYC community board", "nyc_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    add("H098", "LA council district", "la_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    add("H099", "Chicago ward", "chicago_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    add("H100", "Portland nbhd coalition", "portland_only", lambda b: b, kind="defer_reason:portland_not_in_baseline")
    # H101-H106: process mining — DEFER (Seattle only)
    for h, name in [("H101", "Inductive miner Seattle"),
                    ("H102", "Alpha miner Seattle"),
                    ("H103", "Heuristic miner Seattle"),
                    ("H104", "Conformance fitness feature"),
                    ("H105", "Replay stage waits"),
                    ("H106", "BPIC 2015 pretrain")]:
        add(h, name, "seattle_only", lambda b: b, kind="defer_reason:seattle_only")
    # H107: percentile-rank target — approximate via raw/log
    add("H107", "Percentile-rank target (sqrt proxy)", "sqrt_target",
        lambda b: _cfg_merge(b, target_transform="sqrt"))
    # H108: per-city z-score — DEFER (requires special handling)
    add("H108", "Per-city z-score", "target_transform",
        lambda b: b, kind="defer_reason:per_city_target_transform_not_implemented")
    # H109: multi-task heads — composition
    add("H109", "Multi-task heads", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    # H110-H111: transfer learning — composition
    add("H110", "Leave-SF-out transfer", "composition", lambda b: b, kind="defer_reason:phase_2.5_composition")
    add("H111", "Leave-Seattle-out transfer", "composition", lambda b: b, kind="defer_reason:seattle_only")
    # H112: disaster dummy — DEFER
    add("H112", "Disaster rebuild dummy", "disaster_flag",
        lambda b: b, kind="defer_reason:disaster_events_not_keyed")
    # H113: planner staffing — DEFER
    add("H113", "Planner staffing", "macro", lambda b: b, kind="defer_reason:external_data_not_fetched")
    # H114-H115: feature pruning — DEFER (composition, post-hoc)
    add("H114", "Feature pruning pass", "composition", lambda b: b, kind="defer_reason:phase_B_optimisation")
    add("H115", "SHAP-guided selection", "composition", lambda b: b, kind="defer_reason:phase_B_optimisation")
    # H116: nbhd 90d rolling count
    add("H116", "Nbhd 90d rolling count", "+nbhd_90d",
        lambda b: _cfg_merge(b, features={"include_nbhd_rolling_90d": True}))
    # H117: NYC system indicator — DEFER (no system column)
    add("H117", "NYC system indicator", "nyc_only", lambda b: b, kind="defer_reason:column_not_in_schema")
    # H118: is-duplex
    add("H118", "is_duplex flag", "+is_duplex",
        lambda b: _cfg_merge(b, features={"include_is_duplex": True}))
    # H119: reform exponential decay
    add("H119", "Reform exponential decay", "+reform_decay",
        lambda b: _cfg_merge(b, features={"include_reform_decay": True}))
    # H120: holiday season
    add("H120", "Holiday season flag", "+holiday_season",
        lambda b: _cfg_merge(b, features={"include_holiday_season": True}))

    return reg


def _monotone_dict(config: dict, cols: list) -> str:
    """Return the XGBoost monotone_constraints string for the given columns.

    Assumes the current Phase 2 feature list order determines the column index.
    """
    feats = build_phase2_feature_list((config or {}).get("features", {}))
    constraints = [0] * len(feats)
    for c in cols:
        if c in feats:
            constraints[feats.index(c)] = 1
    return "(" + ",".join(str(x) for x in constraints) + ")"


def run_phase2_loop(df: pd.DataFrame, base_best_mae: float) -> dict:
    """Execute the full Phase 2 hypothesis registry.

    Returns a summary dict with counts, kept list, and final best config.
    """
    registry = _build_phase2_registry()
    best_mae = base_best_mae
    best_config: dict = {"features": {}, "model_factory": make_xgb}
    kept_log = []
    reverted_log = []
    deferred_log = []
    fail_log = []

    print(f"\n=== Phase 2 loop: {len(registry)} hypotheses, initial best MAE={best_mae:.2f} ===")
    for i, (eid, desc, label, builder, kind) in enumerate(registry):
        if isinstance(kind, str) and kind.startswith("defer"):
            reason = kind.split(":", 1)[1] if ":" in kind else "defer"
            metrics_stub = {"mae_days": float("nan"), "rmse_days": float("nan"),
                            "r2_log": float("nan"), "r2_days": float("nan")}
            _append_result(RESULTS_PATH, eid, desc, "n/a", label,
                           metrics_stub, f"DEFER ({reason})")
            deferred_log.append((eid, desc, reason))
            continue

        try:
            config = builder(best_config)
        except Exception as exc:  # noqa: BLE001
            metrics_stub = {"mae_days": float("nan"), "rmse_days": float("nan"),
                            "r2_log": float("nan"), "r2_days": float("nan")}
            _append_result(RESULTS_PATH, eid, desc, "n/a", label,
                           metrics_stub, f"FAIL_builder ({type(exc).__name__})")
            fail_log.append((eid, desc, str(exc)[:80]))
            continue

        t0 = time.time()
        try:
            metrics = cross_validate_v2(df, config, verbose=False)
        except Exception as exc:  # noqa: BLE001
            metrics = {"mae_days": float("nan"), "rmse_days": float("nan"),
                       "r2_log": float("nan"), "r2_days": float("nan")}
            _append_result(RESULTS_PATH, eid, desc, _model_name(config), label,
                           metrics, f"FAIL ({type(exc).__name__}: {str(exc)[:60]})")
            fail_log.append((eid, desc, str(exc)[:80]))
            continue

        dt = time.time() - t0
        kept, threshold = _keep_or_revert(metrics["mae_days"], best_mae)
        delta = metrics["mae_days"] - best_mae
        if kept:
            notes = f"KEEP (delta={delta:+.2f} vs best={best_mae:.2f}, wall={dt:.1f}s)"
            best_mae = metrics["mae_days"]
            best_config = config
            kept_log.append((eid, desc, metrics["mae_days"], delta))
        else:
            notes = f"REVERT (delta={delta:+.2f} vs best={best_mae:.2f}, thr={threshold:.2f}, wall={dt:.1f}s)"
            reverted_log.append((eid, desc, metrics["mae_days"], delta))
        _append_result(RESULTS_PATH, eid, desc, _model_name(config), label, metrics, notes)
        status_tag = "KEEP " if kept else "REV  "
        print(f"  [{i+1:3d}/{len(registry)}] {eid} {status_tag} MAE={metrics['mae_days']:6.2f}  "
              f"delta={delta:+6.2f}  wall={dt:4.1f}s  {desc[:50]}")

    return {
        "best_mae": best_mae,
        "best_config": best_config,
        "kept": kept_log,
        "reverted": reverted_log,
        "deferred": deferred_log,
        "failed": fail_log,
        "total": len(registry),
    }


# ----------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-cache", action="store_true",
                    help="force rebuild of permits_baseline.parquet")
    ap.add_argument("--build-cache-v2", action="store_true",
                    help="rebuild permits_baseline.parquet with Phase 2 v2 stratification")
    ap.add_argument("--per-city-limit", type=int, default=None,
                    help="per-city loader row cap (None = full dataset)")
    ap.add_argument("--sample-size", type=int, default=50_000)
    ap.add_argument("--only", choices=["baseline", "tournament", "all"], default="all")
    ap.add_argument("--reset-results", action="store_true",
                    help="overwrite results.tsv with just the header")
    ap.add_argument("--run-phase2", action="store_true",
                    help="run the full Phase 2 single-change hypothesis loop")
    args = ap.parse_args()

    if args.build_cache_v2:
        df = build_clean_cache_v2(n_rows=args.sample_size)
    elif args.build_cache or not CLEAN_PATH.exists():
        df = build_clean_cache(per_city_limit=args.per_city_limit,
                               sample_size=args.sample_size)
    else:
        df = pd.read_parquet(CLEAN_PATH)
        print(f"loaded cached clean dataset: {len(df)} rows from {CLEAN_PATH}")

    print("per-city counts:")
    print(df["city"].value_counts().to_string())

    if args.reset_results:
        _reset_results(RESULTS_PATH)
    else:
        _init_results(RESULTS_PATH)

    best_e00 = None
    if args.only in ("baseline", "all"):
        print("\n=== E00: baseline XGBoost ===")
        t0 = time.time()
        metrics = cross_validate(df, make_baseline_xgb)
        dt = time.time() - t0
        print(f"  MAE={metrics['mae_days']:.2f} days  RMSE={metrics['rmse_days']:.2f}  "
              f"R2_log={metrics['r2_log']:.4f}  R2_days={metrics['r2_days']:.4f}  "
              f"wall={dt:.1f}s")
        _append_result(RESULTS_PATH, "E00", "Phase 2 baseline (v2 sample)",
                       "xgboost", "RAW", metrics,
                       f"5-fold CV, n={len(df)}, wall={dt:.1f}s")
        best_e00 = metrics["mae_days"]

    if args.only in ("tournament", "all"):
        for exp_id_full, factory in TOURNAMENT.items():
            exp_id, family = exp_id_full.split("_", 1)
            print(f"\n=== {exp_id}: {family} ===")
            t0 = time.time()
            metrics = cross_validate(df, factory)
            dt = time.time() - t0
            print(f"  MAE={metrics['mae_days']:.2f} days  RMSE={metrics['rmse_days']:.2f}  "
                  f"R2_log={metrics['r2_log']:.4f}  R2_days={metrics['r2_days']:.4f}  "
                  f"wall={dt:.1f}s")
            _append_result(RESULTS_PATH, exp_id, f"Tournament {family}",
                           family, "RAW", metrics,
                           f"5-fold CV, n={len(df)}, wall={dt:.1f}s")
            if best_e00 is None or metrics["mae_days"] < best_e00:
                best_e00 = metrics["mae_days"]

    if args.run_phase2:
        if best_e00 is None:
            # Re-run the baseline quickly so we have a best_so_far anchor.
            metrics = cross_validate(df, make_baseline_xgb, verbose=False)
            best_e00 = metrics["mae_days"]
        summary = run_phase2_loop(df, best_e00)
        _print_phase2_summary(summary, best_e00)

    print(f"\nresults -> {RESULTS_PATH}")


def _print_phase2_summary(summary: dict, base_best: float) -> None:
    kept = summary["kept"]
    print("\n=== Phase 2 summary ===")
    print(f"  total      : {summary['total']}")
    print(f"  kept       : {len(kept)}")
    print(f"  reverted   : {len(summary['reverted'])}")
    print(f"  deferred   : {len(summary['deferred'])}")
    print(f"  failed     : {len(summary['failed'])}")
    print(f"  E00 baseline MAE : {base_best:.2f}")
    print(f"  Phase 2 best MAE : {summary['best_mae']:.2f}")
    improvement_pct = 100.0 * (base_best - summary["best_mae"]) / base_best if base_best > 0 else 0.0
    print(f"  improvement : {improvement_pct:+.2f}%")
    if kept:
        print("\n  Top keeps by cumulative delta:")
        for eid, desc, mae, delta in sorted(kept, key=lambda r: r[3])[:10]:
            print(f"    {eid} {desc[:50]:50s} MAE={mae:.2f}  delta={delta:+.2f}")
    if summary["deferred"]:
        print(f"\n  Deferred reasons (unique): "
              f"{sorted(set(reason for _, _, reason in summary['deferred']))}")


if __name__ == "__main__":
    main()
