"""
Strategy for [YOUR SCIENTIFIC QUESTION].

This is the ONLY file modified during HDR experiments.
Contains feature engineering and model hyperparameters.

Current experiment: [Exp N]: [description] (prior [X]%)
"""

import numpy as np


# ============================================================================
# CONFIGURE: Feature column indices in raw data
# ============================================================================

# Map feature names to their column indices in the raw data array.
# Example:
# COL_TEMPERATURE = 0
# COL_PRESSURE = 1
# COL_CONCENTRATION = 2

# Group identifiers (must match the 'group' field in dataset.pickle)
GROUP_IDS = {
    # "group_a": 0,
    # "group_b": 1,
    # "group_c": 2,
}


# ============================================================================
# FEATURE ENGINEERING HELPERS
# ============================================================================

def _finite_diff(signal: np.ndarray, window: int) -> np.ndarray:
    """Compute finite difference over a window: (x[t] - x[t-window]) / window.

    For time-series data. First `window` values use available history.
    """
    result = np.zeros_like(signal)
    for i in range(len(signal)):
        w = min(i, window)
        if w > 0:
            result[i] = (signal[i] - signal[i - w]) / w
    return result


def _rolling_std(signal: np.ndarray, window: int) -> np.ndarray:
    """Compute rolling standard deviation over a window.

    For time-series data. Uses cumulative sum for efficiency.
    """
    result = np.zeros_like(signal)
    cumsum = np.cumsum(signal)
    cumsum2 = np.cumsum(signal ** 2)
    for i in range(len(signal)):
        w = min(i + 1, window)
        if w < 2:
            result[i] = 0.0
            continue
        start = i + 1 - w
        s = cumsum[i] - (cumsum[start - 1] if start > 0 else 0)
        s2 = cumsum2[i] - (cumsum2[start - 1] if start > 0 else 0)
        var = s2 / w - (s / w) ** 2
        result[i] = np.sqrt(max(var, 0.0))
    return result


def _rolling_mean(signal: np.ndarray, window: int) -> np.ndarray:
    """Compute rolling mean over a window."""
    result = np.zeros_like(signal)
    cumsum = np.cumsum(signal)
    for i in range(len(signal)):
        w = min(i + 1, window)
        start = i + 1 - w
        s = cumsum[i] - (cumsum[start - 1] if start > 0 else 0)
        result[i] = s / w
    return result


# ============================================================================
# MAIN FEATURE BUILDER: Edit this function during HDR experiments
# ============================================================================

def build_features(data: np.ndarray, group: str,
                   include_group_indicators: bool = True) -> np.ndarray:
    """Build feature matrix from raw sample data.

    This is the primary function modified during HDR experiments.
    Each experiment adds/removes/modifies derived features here.

    Args:
        data: (n_timesteps, n_raw_features) array for time-series data,
              or (n_raw_features,) for tabular data.
              Features are in the order defined in prepare.py FEATURE_NAMES.
        group: identifier string (e.g., "group_a") for the sample's source
        include_group_indicators: whether to add one-hot group columns

    Returns:
        features: (n_timesteps, n_total_features) array
    """
    n = len(data) if data.ndim > 1 else 1
    is_timeseries = data.ndim > 1
    derived = []

    # ---- IMPLEMENT: Add derived features below ----
    #
    # During HDR, you'll add features one experiment at a time.
    # Examples for time-series data:
    #
    # --- Time derivatives at multiple scales ---
    # key_cols = [0, 1, 2]  # columns to differentiate
    # windows = [10, 40, 100]  # timesteps (adjust to your sampling rate)
    # for col in key_cols:
    #     signal = data[:, col]
    #     for w in windows:
    #         deriv = _finite_diff(signal, w)
    #         derived.append(deriv.reshape(-1, 1))
    #
    # --- Log-transform for exponential processes ---
    # signal = data[:, COL_SOMETHING]
    # log_signal = np.log(np.abs(signal) + 1e-10).reshape(-1, 1)
    # derived.append(log_signal)
    #
    # --- Rolling statistics (volatility, trend) ---
    # for col in [0, 1, 2]:
    #     signal = data[:, col]
    #     for w in [10, 40]:
    #         derived.append(_rolling_std(signal, w).reshape(-1, 1))
    #
    # --- Interaction features (domain-motivated products/ratios) ---
    # feature_a = data[:, COL_A]
    # feature_b = data[:, COL_B]
    # interaction = (feature_a * feature_b).reshape(-1, 1)
    # derived.append(interaction)
    #
    # Examples for tabular (non-time-series) data:
    #
    # --- Interaction features ---
    # interaction = (data[COL_A] * data[COL_B]).reshape(1)
    # derived.append(interaction)
    #
    # --- Log-transform ---
    # log_feat = np.log(np.abs(data[COL_X]) + 1e-10).reshape(1)
    # derived.append(log_feat)

    # Sanitize derived features: replace inf/nan with 0, clip extremes
    for i in range(len(derived)):
        d = derived[i]
        d = np.nan_to_num(d, nan=0.0, posinf=0.0, neginf=0.0)
        np.clip(d, -1e6, 1e6, out=d)
        derived[i] = d

    # Stack: raw features + derived + group indicators
    if is_timeseries:
        parts = [data] + derived
        if include_group_indicators and GROUP_IDS:
            tok = np.zeros((n, len(GROUP_IDS)), dtype=np.float32)
            if group in GROUP_IDS:
                tok[:, GROUP_IDS[group]] = 1.0
            parts.append(tok)
    else:
        parts = [data.reshape(1, -1)] + [d.reshape(1, -1) for d in derived]
        if include_group_indicators and GROUP_IDS:
            tok = np.zeros((1, len(GROUP_IDS)), dtype=np.float32)
            if group in GROUP_IDS:
                tok[:, GROUP_IDS[group]] = 1.0
            parts.append(tok)

    return np.hstack(parts)


# ============================================================================
# MODEL HYPERPARAMETERS: Edit this function during HDR experiments
# ============================================================================

def get_xgb_params() -> dict:
    """Return XGBoost training parameters.

    Returns dict with both booster params and num_boost_round.
    Tune these during HDR experiments (especially scale_pos_weight
    for imbalanced problems).
    """
    return {
        "objective": "binary:logistic",  # or "reg:squarederror", "multi:softprob"
        "eval_metric": "auc",            # match your primary metric
        "max_depth": 6,
        "learning_rate": 0.1,
        "min_child_weight": 10,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": 1.0,         # KEY KNOB for imbalanced classification
        "tree_method": "hist",
        "device": "cuda",                # "cpu" if no GPU
        "verbosity": 0,
        "num_boost_round": 200,
    }
