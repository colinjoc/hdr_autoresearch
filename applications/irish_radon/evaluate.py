"""Evaluation harness for Irish radon prediction.

Uses spatial CV grouped by county to prevent data leakage.
Reports both regression (MAE on % homes > 200 Bq/m3) and
classification (High Radon Area: >= 10%) metrics.
"""
import os
import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    mean_absolute_error,
    f1_score,
    accuracy_score,
    precision_score,
    recall_score,
)

from data_loaders import build_dataset

HRA_THRESHOLD = 10.0  # % homes above reference level for High Radon Area


def make_spatial_cv_splits(X, y, groups, n_splits=None):
    """Create spatial CV splits grouped by county.

    Uses GroupKFold so no county appears in both train and test.
    Counties with fewer grid squares are grouped together.
    """
    if n_splits is None:
        # Use min(n_groups, 10) folds
        n_groups = groups.nunique()
        n_splits = min(n_groups, 10)

    gkf = GroupKFold(n_splits=n_splits)
    splits = list(gkf.split(X, y, groups))
    return splits


def evaluate_model(model_fn, n_splits=None):
    """Evaluate a model using spatial CV.

    Args:
        model_fn: callable that returns (model, feature_names) tuple.
                  model must have .fit(X, y) and .predict(X) methods.
        n_splits: number of CV folds (default: min(n_counties, 10))

    Returns:
        dict with metrics:
        - mae_mean, mae_std: MAE across folds
        - hra_f1, hra_accuracy, hra_precision, hra_recall: HRA classification
        - per_county_mae: dict of county -> MAE
        - feature_importance: dict of feature -> importance (if available)
    """
    X, y, groups = build_dataset()
    splits = make_spatial_cv_splits(X, y, groups, n_splits=n_splits)

    fold_maes = []
    all_preds = np.full(len(y), np.nan)
    per_county_maes = {}

    for fold_idx, (train_idx, test_idx) in enumerate(splits):
        X_train = X.iloc[train_idx]
        y_train = y.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_test = y.iloc[test_idx]

        model, feature_names = model_fn()

        # Select only numeric features that exist
        available_features = [f for f in feature_names if f in X_train.columns]
        X_tr = X_train[available_features].fillna(0)
        X_te = X_test[available_features].fillna(0)

        model.fit(X_tr, y_train)
        preds = model.predict(X_te)

        # Clip predictions to valid range
        preds = np.clip(preds, 0, 100)

        fold_mae = mean_absolute_error(y_test, preds)
        fold_maes.append(fold_mae)
        all_preds[test_idx] = preds

        # Per-county MAE
        for county in groups.iloc[test_idx].unique():
            county_mask = groups.iloc[test_idx] == county
            county_test_idx = test_idx[county_mask.values]
            county_mae = mean_absolute_error(
                y.iloc[county_test_idx],
                all_preds[county_test_idx]
            )
            per_county_maes[county] = county_mae

    # Overall metrics
    valid = ~np.isnan(all_preds)
    overall_mae = mean_absolute_error(y[valid], all_preds[valid])

    # HRA classification
    y_hra = (y[valid] >= HRA_THRESHOLD).astype(int)
    pred_hra = (all_preds[valid] >= HRA_THRESHOLD).astype(int)

    # Feature importance from last fold
    feature_importance = {}
    if hasattr(model, "feature_importances_"):
        for fname, imp in zip(available_features, model.feature_importances_):
            feature_importance[fname] = float(imp)

    metrics = {
        "mae_mean": float(np.mean(fold_maes)),
        "mae_std": float(np.std(fold_maes)),
        "mae_overall": float(overall_mae),
        "hra_f1": float(f1_score(y_hra, pred_hra, zero_division=0)),
        "hra_accuracy": float(accuracy_score(y_hra, pred_hra)),
        "hra_precision": float(precision_score(y_hra, pred_hra, zero_division=0)),
        "hra_recall": float(recall_score(y_hra, pred_hra, zero_division=0)),
        "per_county_mae": per_county_maes,
        "feature_importance": feature_importance,
        "n_samples": int(len(y)),
        "n_features": len(available_features),
    }

    return metrics


def record_result(experiment_id, description, metrics, kept,
                  results_path=None):
    """Append experiment result to results.tsv."""
    if results_path is None:
        results_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "results.tsv"
        )

    row = {
        "experiment_id": experiment_id,
        "description": description,
        "mae_mean": f"{metrics.get('mae_mean', 0):.4f}",
        "mae_std": f"{metrics.get('mae_std', 0):.4f}",
        "hra_f1": f"{metrics.get('hra_f1', 0):.4f}",
        "hra_accuracy": f"{metrics.get('hra_accuracy', 0):.4f}",
        "kept": kept,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    df = pd.DataFrame([row])
    header = not os.path.exists(results_path) or os.path.getsize(results_path) == 0
    df.to_csv(results_path, sep="\t", mode="a", header=header, index=False)


if __name__ == "__main__":
    from model import build_model
    print("Evaluating model with spatial CV...")
    metrics = evaluate_model(build_model)
    print(f"\nMAE: {metrics['mae_mean']:.2f} +/- {metrics['mae_std']:.2f}")
    print(f"HRA F1: {metrics['hra_f1']:.3f}")
    print(f"HRA Accuracy: {metrics['hra_accuracy']:.3f}")
    print(f"\nPer-county MAE:")
    for county, mae in sorted(metrics["per_county_mae"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {county}: {mae:.2f}")
    if metrics["feature_importance"]:
        print(f"\nTop features:")
        for fname, imp in sorted(metrics["feature_importance"].items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"  {fname}: {imp:.4f}")
