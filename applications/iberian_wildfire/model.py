"""Model definitions for Iberian wildfire VLF prediction.

Phase 0.5 (baseline) and Phase 1 (5-family tournament) for predicting
which country-weeks will contain very large fire (VLF, >500 ha) activity.

The target is binary: vlf = 1 if the country-week has VLF activity.
The primary metric is AUC (area under ROC), with F2-score as secondary
(weighting recall over precision since missing a VLF is costlier).

Follows temporal cross-validation: train on years < test_year.
"""
from __future__ import annotations

from typing import List

import numpy as np
import xgboost as xgb
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

try:
    import lightgbm as lgb
    _HAS_LGB = True
except Exception:  # noqa: BLE001
    _HAS_LGB = False

from data_loaders import BASELINE_FEATURES, PHASE2_EXTRA_FEATURES


# ---------------------------------------------------------------- model factories

def make_ridge():
    """Logistic regression with L2 penalty (Ridge)."""
    return LogisticRegression(
        C=1.0, l1_ratio=0, solver="lbfgs", max_iter=5000,
        class_weight="balanced", random_state=42,
    )


def make_xgboost():
    """XGBoost classifier with moderate regularization."""
    return xgb.XGBClassifier(
        objective="binary:logistic",
        max_depth=4,
        learning_rate=0.05,
        n_estimators=300,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=10,
        eval_metric="logloss",
        verbosity=0,
        n_jobs=4,
        random_state=42,
        tree_method="hist",
    )


def make_xgboost_deep():
    """XGBoost with deeper trees (comparison)."""
    return xgb.XGBClassifier(
        objective="binary:logistic",
        max_depth=6,
        learning_rate=0.05,
        n_estimators=300,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=10,
        eval_metric="logloss",
        verbosity=0,
        n_jobs=4,
        random_state=42,
        tree_method="hist",
    )


def make_lightgbm():
    """LightGBM classifier."""
    if not _HAS_LGB:
        raise RuntimeError("lightgbm is not installed")
    return lgb.LGBMClassifier(
        objective="binary",
        max_depth=4,
        learning_rate=0.05,
        n_estimators=300,
        min_child_samples=5,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=10,
        n_jobs=4,
        random_state=42,
        verbosity=-1,
    )


def make_extratrees():
    """ExtraTrees classifier."""
    return ExtraTreesClassifier(
        n_estimators=300, max_depth=None, class_weight="balanced",
        n_jobs=4, random_state=42,
    )


def make_randomforest():
    """Random Forest classifier."""
    return RandomForestClassifier(
        n_estimators=300, max_depth=None, class_weight="balanced",
        n_jobs=4, random_state=42,
    )


# ---------------------------------------------------------------- tournament

TOURNAMENT = {
    "T01_ridge": make_ridge,
    "T02_xgboost": make_xgboost,
    "T03_xgboost_deep": make_xgboost_deep,
    "T04_extratrees": make_extratrees,
    "T05_randomforest": make_randomforest,
}

# Add LightGBM only if available
if _HAS_LGB:
    TOURNAMENT["T06_lightgbm"] = make_lightgbm


# ---------------------------------------------------------------- feature sets

def get_baseline_features() -> List[str]:
    """Return the Phase 0.5 baseline feature list."""
    return list(BASELINE_FEATURES)


def get_phase2_features() -> List[str]:
    """Return the Phase 2 feature list (baseline + extras)."""
    return list(BASELINE_FEATURES) + list(PHASE2_EXTRA_FEATURES)


# ---------------------------------------------------------------- Feature subsets for predictor family comparison
#
# NOTE: Variable names (FWI_PROXY, LFMC_PROXY, DROUGHT_PROXY) are legacy.
# The paper uses corrected terminology:
#   FWI_PROXY_FEATURES  = "Seasonal Climatology" (historical fire activity patterns)
#   LFMC_PROXY_FEATURES = "Recent Fire Activity" (ratios to norms + lagged values)
#   DROUGHT_PROXY_FEATURES = "Cumulative Season Stress" (year-to-date accumulations)
# None of these are actual fire weather, fuel moisture, or drought measurements.

FWI_PROXY_FEATURES = [
    "month_sin", "month_cos",
    "fires_avg", "area_ha_avg",
    "fires_max", "area_ha_max",
    "log_area_avg", "log_fires_avg",
    "is_fire_season", "fire_season_week",
]

LFMC_PROXY_FEATURES = [
    "month_sin", "month_cos",
    "fires_ratio", "area_ratio",
    "fires_lag1", "area_lag1",
    "fires_lag2", "area_lag2",
    "fires_2wk", "area_2wk",
]

DROUGHT_PROXY_FEATURES = [
    "month_sin", "month_cos",
    "cum_area_ytd", "cum_fires_ytd",
    "year_trend",
    "fires_4wk", "area_4wk",
]
