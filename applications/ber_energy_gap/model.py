"""Model definitions for BER Energy Gap prediction.

Predicts BerRating (kWh/m2/yr) from building characteristics.
Modified during HDR loop experiments.
"""
from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
)

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMRegressor
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False


def ridge_model():
    """Linear baseline."""
    return Ridge(alpha=1.0)


def rf_model():
    """Random Forest baseline."""
    return RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=10,
        n_jobs=-1,
        random_state=42,
    )


def et_model():
    """Extra Trees baseline."""
    return ExtraTreesRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=10,
        n_jobs=-1,
        random_state=42,
    )


def xgb_model():
    """XGBoost baseline."""
    if not HAS_XGB:
        raise ImportError("xgboost not installed")
    return XGBRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",
        device="cuda",
        random_state=42,
        n_jobs=-1,
    )


def lgbm_model():
    """LightGBM baseline."""
    if not HAS_LGBM:
        raise ImportError("lightgbm not installed")
    return LGBMRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        device="cpu",
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )


# Current best model function (updated during HDR loop)
def best_model():
    """Current best model. Updated as experiments are kept."""
    if HAS_LGBM:
        return lgbm_model()
    elif HAS_XGB:
        return xgb_model()
    else:
        return rf_model()
