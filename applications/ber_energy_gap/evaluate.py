"""Evaluation harness for BER Energy Gap analysis.

Provides consistent cross-validation, metrics, and result recording.
"""
import os
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.tsv")


def cross_validate(model_fn, X, y, n_splits=5, random_state=42):
    """Run k-fold CV and return per-fold metrics.

    Args:
        model_fn: callable() that returns a fitted-API-compatible model
        X: feature matrix (DataFrame or ndarray)
        y: target array
        n_splits: number of CV folds
        random_state: random seed

    Returns:
        dict with keys: mae, rmse, r2, mae_std, rmse_std, r2_std,
                        fold_maes, fold_rmses, fold_r2s, predictions
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    fold_maes = []
    fold_rmses = []
    fold_r2s = []
    all_preds = np.zeros(len(y))
    all_indices = np.zeros(len(y), dtype=int)

    X_arr = X.values if hasattr(X, "values") else np.asarray(X)
    y_arr = np.asarray(y)

    t0 = time.time()
    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X_arr)):
        model = model_fn()
        model.fit(X_arr[train_idx], y_arr[train_idx])
        preds = model.predict(X_arr[val_idx])

        mae = mean_absolute_error(y_arr[val_idx], preds)
        rmse = np.sqrt(mean_squared_error(y_arr[val_idx], preds))
        r2 = r2_score(y_arr[val_idx], preds)

        fold_maes.append(mae)
        fold_rmses.append(rmse)
        fold_r2s.append(r2)

        all_preds[val_idx] = preds
        all_indices[val_idx] = fold_idx

    elapsed = time.time() - t0

    return {
        "mae": np.mean(fold_maes),
        "rmse": np.mean(fold_rmses),
        "r2": np.mean(fold_r2s),
        "mae_std": np.std(fold_maes),
        "rmse_std": np.std(fold_rmses),
        "r2_std": np.std(fold_r2s),
        "fold_maes": fold_maes,
        "fold_rmses": fold_rmses,
        "fold_r2s": fold_r2s,
        "predictions": all_preds,
        "fold_indices": all_indices,
        "elapsed_s": elapsed,
    }


def evaluate_by_band(y_true, y_pred, energy_ratings):
    """Compute MAE per BER band.

    Args:
        y_true: true BER values (kWh/m2/yr)
        y_pred: predicted BER values
        energy_ratings: series of BER letter grades

    Returns:
        DataFrame with per-band MAE, RMSE, count
    """
    bands = ["A1", "A2", "A3", "B1", "B2", "B3",
             "C1", "C2", "C3", "D1", "D2", "E1", "E2", "F", "G"]

    results = []
    for band in bands:
        mask = energy_ratings == band
        n = mask.sum()
        if n > 0:
            mae = mean_absolute_error(y_true[mask], y_pred[mask])
            rmse = np.sqrt(mean_squared_error(y_true[mask], y_pred[mask]))
            r2 = r2_score(y_true[mask], y_pred[mask]) if n > 1 else float("nan")
            results.append({"band": band, "n": n, "mae": mae, "rmse": rmse, "r2": r2})

    return pd.DataFrame(results)


def record_result(experiment_id, description, metrics, kept=True):
    """Append result to results.tsv.

    Args:
        experiment_id: unique experiment identifier
        description: what was changed
        metrics: dict from cross_validate()
        kept: whether this experiment was kept (True) or reverted (False)
    """
    row = {
        "experiment_id": experiment_id,
        "description": description,
        "mae": f"{metrics['mae']:.2f}",
        "rmse": f"{metrics['rmse']:.2f}",
        "r2": f"{metrics['r2']:.4f}",
        "mae_std": f"{metrics['mae_std']:.2f}",
        "rmse_std": f"{metrics['rmse_std']:.2f}",
        "elapsed_s": f"{metrics['elapsed_s']:.1f}",
        "kept": "YES" if kept else "NO",
    }

    write_header = not os.path.exists(RESULTS_PATH)

    with open(RESULTS_PATH, "a") as f:
        if write_header:
            f.write("\t".join(row.keys()) + "\n")
        f.write("\t".join(str(v) for v in row.values()) + "\n")

    print(f"[{'KEPT' if kept else 'REVERTED'}] {experiment_id}: "
          f"MAE={metrics['mae']:.2f} RMSE={metrics['rmse']:.2f} "
          f"R2={metrics['r2']:.4f}")


def feature_importance(model, feature_names):
    """Extract feature importances from a fitted model.

    Handles sklearn tree models and linear models.
    """
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_)
    else:
        return None

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": imp,
    }).sort_values("importance", ascending=False)
    df["importance_pct"] = 100 * df["importance"] / df["importance"].sum()
    return df
