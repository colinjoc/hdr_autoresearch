"""
Phase 2: HDR Loop for Xylella Olive Decline Prediction.

Runs pre-registered single-change experiments, records results,
and makes KEEP/REVERT decisions based on spatial CV AUC improvement.

Usage:
    python run_phase2.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset
from evaluate import run_cv, run_holdout, _write_results, compute_metrics
from model import (
    BASE_FEATURES, EXTRA_FEATURES, EXTRA_CATEGORICAL,
    MODEL_FAMILY, get_feature_columns, prepare_features, build_model,
)


def run_experiment(
    exp_id: str,
    description: str,
    feature_to_add: str | None = None,
    feature_to_remove: str | None = None,
    categorical: bool = False,
    notes: str = "",
) -> dict:
    """Run a single HDR experiment.

    Temporarily modifies EXTRA_FEATURES or EXTRA_CATEGORICAL,
    runs evaluation, and returns the result.
    """
    # Temporarily add/remove feature
    if feature_to_add:
        if categorical:
            EXTRA_CATEGORICAL.append(feature_to_add)
        else:
            EXTRA_FEATURES.append(feature_to_add)

    if feature_to_remove:
        if feature_to_remove in EXTRA_FEATURES:
            EXTRA_FEATURES.remove(feature_to_remove)
        elif feature_to_remove in EXTRA_CATEGORICAL:
            EXTRA_CATEGORICAL.remove(feature_to_remove)

    t0 = time.time()
    df = load_dataset()

    feature_cols = get_feature_columns()
    n_feat = len(feature_cols)

    print(f"\n{'='*60}")
    print(f"Experiment {exp_id}: {description}")
    print(f"Features ({n_feat}): {feature_cols}")
    print(f"{'='*60}")

    cv_results = run_cv(df, verbose=True)
    holdout = run_holdout(df)
    elapsed = time.time() - t0

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": MODEL_FAMILY,
        "n_features": n_feat,
        "cv_auc_mean": cv_results["cv_auc_mean"],
        "cv_auc_std": cv_results["cv_auc_std"],
        "cv_f1_mean": cv_results["cv_f1_mean"],
        "cv_f1_std": cv_results["cv_f1_std"],
        "cv_precision_mean": cv_results["cv_precision_mean"],
        "cv_recall_mean": cv_results["cv_recall_mean"],
        "holdout_auc": holdout["auc"],
        "holdout_f1": holdout["f1"],
        "holdout_precision": holdout["precision"],
        "holdout_recall": holdout["recall"],
        "notes": f"{notes} ({elapsed:.1f}s)",
    }

    _write_results([row])

    print(f"\n  CV AUC: {cv_results['cv_auc_mean']:.4f} +/- {cv_results['cv_auc_std']:.4f}")
    print(f"  CV F1:  {cv_results['cv_f1_mean']:.4f}")
    print(f"  Holdout AUC: {holdout['auc']:.4f}")

    return row


def main():
    """Run the full HDR loop."""
    # Track best AUC for KEEP/REVERT decisions
    best_cv_auc = 0.7674  # E00 baseline
    kept_features = []
    reverted_features = []

    # Pre-registered experiments (ordered by expected impact)
    experiments = [
        # Distance features (diffusion hypothesis)
        ("E01", "Add dist_nearest_declining_km", "dist_nearest_declining_km", False),
        ("E02", "Add log_dist_nearest_declining", "log_dist_nearest_declining", False),
        ("E03", "Add log_dist_epicentre", "log_dist_epicentre", False),
        ("E04", "Add already_affected flag", "already_affected", False),
        # Frost features (climate hypothesis)
        ("E05", "Add frost_days_below_minus6", "frost_days_below_minus6", False),
        ("E06", "Add frost_days_below_minus12", "frost_days_below_minus12", False),
        ("E07", "Add winter_tmin_abs", "winter_tmin_abs", False),
        ("E08", "Add coldest_month_anomaly", "coldest_month_anomaly", False),
        ("E09", "Add frost_severity_index", "frost_severity_index", False),
        # NDVI features
        ("E10", "Add ndvi_trend", "ndvi_trend", False),
        ("E11", "Add ndvi_anomaly", "ndvi_anomaly", False),
        ("E12", "Add ndvi_std", "ndvi_std", False),
        ("E13", "Add evi_mean", "evi_mean", False),
        ("E14", "Add ndvi_decline_rate", "ndvi_decline_rate", False),
        # Precipitation features
        ("E15", "Add summer_precip_mm", "summer_precip_mm", False),
        ("E16", "Add precip_deficit_frac", "precip_deficit_frac", False),
        # Interaction and derived features
        ("E17", "Add ndvi_x_jan_tmin interaction", "ndvi_x_jan_tmin", False),
        ("E18", "Add aridity_proxy", "aridity_proxy", False),
        ("E19", "Add lat_from_salento", "lat_from_salento", False),
        ("E20", "Add greenup_proxy", "greenup_proxy", False),
        ("E21", "Add soil_moisture_proxy", "soil_moisture_proxy", False),
        # Categorical
        ("E22", "Add province_ordinal", "province_ordinal", False),
        # Country
        ("E23", "Add country indicator", "country", True),
    ]

    for exp_id, description, feature, is_categorical in experiments:
        result = run_experiment(
            exp_id=exp_id,
            description=description,
            feature_to_add=feature,
            categorical=is_categorical,
        )

        cv_auc = result["cv_auc_mean"]

        if cv_auc > best_cv_auc:
            decision = "KEEP"
            best_cv_auc = cv_auc
            kept_features.append(feature)
            print(f"  >>> KEEP (AUC {cv_auc:.4f} > {best_cv_auc:.4f})")
        else:
            decision = "REVERT"
            reverted_features.append(feature)
            # Remove the feature
            if is_categorical:
                if feature in EXTRA_CATEGORICAL:
                    EXTRA_CATEGORICAL.remove(feature)
            else:
                if feature in EXTRA_FEATURES:
                    EXTRA_FEATURES.remove(feature)
            print(f"  >>> REVERT (AUC {cv_auc:.4f} <= {best_cv_auc:.4f})")

    # Summary
    print("\n" + "=" * 60)
    print("HDR LOOP SUMMARY")
    print("=" * 60)
    print(f"Final best CV AUC: {best_cv_auc:.4f}")
    print(f"Kept features ({len(kept_features)}): {kept_features}")
    print(f"Reverted features ({len(reverted_features)}): {reverted_features}")
    print(f"Final feature list: {get_feature_columns()}")


if __name__ == "__main__":
    main()
