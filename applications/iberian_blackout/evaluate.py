"""
Evaluation harness for the Iberian Blackout cascade prediction project.

This module provides:
- Labeling function: identifies high-risk grid days
- Model evaluation: cross-validated metrics
- Full evaluation pipeline

The approach uses Option C (decomposition): we reverse-engineer the blackout
cascade to understand which grid state features predict collapse proximity.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import warnings

from data_loader import build_daily_feature_matrix, compute_grid_stress_indicators


def label_blackout_risk(
    features: pd.DataFrame,
    blackout_dates: list = None,
    stress_threshold: float = None,
) -> pd.Series:
    """
    Label days as high-risk (1) or normal (0) for blackout cascade.

    The primary label is the known blackout date (April 28, 2025).
    Additional high-risk days are identified using grid stress indicators:
    days with extreme renewable penetration AND low synchronous generation
    AND negative/very low prices (indicating dangerously low inertia dispatch).

    Parameters
    ----------
    features : pd.DataFrame
        Output of build_daily_feature_matrix
    blackout_dates : list, optional
        Known blackout dates. Default: ['2025-04-28']
    stress_threshold : float, optional
        Percentile threshold for labeling additional stress days

    Returns
    -------
    pd.Series
        Binary labels, 1 = high-risk, 0 = normal
    """
    if blackout_dates is None:
        blackout_dates = [pd.Timestamp("2025-04-28", tz="UTC")]
    else:
        blackout_dates = [pd.Timestamp(d, tz="UTC") for d in blackout_dates]

    labels = pd.Series(0, index=features.index, dtype=int)

    # Label known blackout dates
    for bd in blackout_dates:
        bd_norm = bd.normalize()
        mask = features.index.normalize() == bd_norm
        labels[mask] = 1

    # Label additional stress days using composite indicators
    stress = compute_grid_stress_indicators(features)

    if "composite_risk_score" in stress.columns:
        scores = stress["composite_risk_score"].dropna()
        if len(scores) > 10:
            # Use top 5th percentile as additional high-risk days
            threshold = scores.quantile(0.95)
            high_risk = stress["composite_risk_score"] >= threshold
            labels[high_risk] = 1

    return labels


def evaluate_model(
    stress_features: pd.DataFrame,
    labels: pd.Series,
    model=None,
) -> dict:
    """
    Evaluate a model on the grid stress prediction task.

    Uses Leave-One-Out Cross Validation given the small dataset
    and extreme class imbalance.

    Parameters
    ----------
    stress_features : pd.DataFrame
        Feature matrix (stress indicators)
    labels : pd.Series
        Binary labels
    model : sklearn estimator, optional
        Default: LogisticRegression (baseline)

    Returns
    -------
    dict
        Metrics: accuracy, precision, recall, f1, auc_roc
    """
    # Align features and labels
    common_idx = stress_features.index.intersection(labels.index)
    X = stress_features.loc[common_idx].copy()
    y = labels.loc[common_idx].copy()

    # Drop rows with NaN features
    valid_mask = X.notna().all(axis=1) & y.notna()
    X = X[valid_mask]
    y = y[valid_mask]

    if len(X) < 10 or y.sum() < 1:
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "auc_roc": None,
        }

    # Select numeric columns only
    X = X.select_dtypes(include=[np.number])

    if model is None:
        model = LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        )

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # LOO-CV for small datasets
    loo = LeaveOneOut()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y_pred = cross_val_predict(model, X_scaled, y, cv=loo, method="predict")

    # For AUC, try to get probabilities
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y_prob = cross_val_predict(
                model, X_scaled, y, cv=loo, method="predict_proba"
            )[:, 1]
        auc = roc_auc_score(y, y_prob)
    except Exception:
        auc = None

    metrics = {
        "accuracy": accuracy_score(y, y_pred),
        "precision": precision_score(y, y_pred, zero_division=0),
        "recall": recall_score(y, y_pred, zero_division=0),
        "f1": f1_score(y, y_pred, zero_division=0),
        "auc_roc": auc,
    }

    return metrics


def run_full_evaluation(data_dir: str, model=None) -> dict:
    """
    Run the complete evaluation pipeline.

    Parameters
    ----------
    data_dir : str
        Path to the data directory
    model : sklearn estimator, optional

    Returns
    -------
    dict
        Contains 'metrics', 'predictions', 'features_used'
    """
    # Build features
    features = build_daily_feature_matrix(data_dir)
    stress = compute_grid_stress_indicators(features)
    labels = label_blackout_risk(features)

    # Evaluate
    metrics = evaluate_model(stress, labels, model=model)

    # Get predictions for analysis
    common_idx = stress.index.intersection(labels.index)
    X = stress.loc[common_idx].select_dtypes(include=[np.number])
    y = labels.loc[common_idx]
    valid_mask = X.notna().all(axis=1) & y.notna()

    predictions = pd.DataFrame(
        {"label": y[valid_mask], "risk_score": stress.loc[valid_mask, "composite_risk_score"] if "composite_risk_score" in stress.columns else np.nan},
        index=y[valid_mask].index,
    )

    return {
        "metrics": metrics,
        "predictions": predictions,
        "features_used": list(stress.columns),
        "n_samples": len(y[valid_mask]),
        "n_positive": int(y[valid_mask].sum()),
    }


if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    results = run_full_evaluation(data_dir)
    print("=== Evaluation Results ===")
    print(f"Samples: {results['n_samples']} ({results['n_positive']} positive)")
    print(f"Features: {results['features_used']}")
    for k, v in results["metrics"].items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")
