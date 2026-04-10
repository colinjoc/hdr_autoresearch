"""
Phase B: Discovery — Map predicted 5-year olive decline expansion.

Train the final model on all available data, then predict decline risk
for currently-unaffected olive-growing municipalities across the study area.
Identify highest-risk currently-unaffected regions.

Usage:
    python phase_b_discovery.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    load_dataset, generate_synthetic_data, add_derived_features,
    ALL_PROVINCES, PROVINCE_COORDS, PROVINCE_CLIMATE,
    PROVINCE_ELEVATION, OLIVE_FRACTION, FIRST_DETECTION_YEAR,
)
from model import (
    get_feature_columns, prepare_features, build_model,
    EXTRA_FEATURES, BASE_FEATURES,
)


def generate_future_scenarios(
    prediction_years: list[int] = [2025, 2026, 2027, 2028, 2029],
    seed: int = 42,
) -> pd.DataFrame:
    """Generate candidate municipalities for future prediction years.

    For each future year, generate the expected state of currently-unaffected
    municipalities under the diffusion + climate model.
    """
    all_rows = []
    for year in prediction_years:
        df = generate_synthetic_data(prediction_year=year, seed=seed + year)
        df = add_derived_features(df)
        # Keep only municipalities that are NOT already declined
        # (we want to predict NEW decline)
        df["prediction_year"] = year
        all_rows.append(df)

    return pd.concat(all_rows, ignore_index=True)


def run_discovery():
    """Run the full discovery analysis."""
    # Train on 2024 data
    train_df = load_dataset(prediction_year=2024)
    X_train, y_train = prepare_features(train_df)

    model = build_model()
    model.fit(X_train, y_train)

    # Feature importance
    importances = model.feature_importances_
    feature_cols = get_feature_columns()
    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": importances,
    }).sort_values("importance", ascending=False)

    print("=" * 60)
    print("FEATURE IMPORTANCE (XGBoost gain)")
    print("=" * 60)
    for _, row in importance_df.iterrows():
        bar = "#" * int(row["importance"] * 50)
        print(f"  {row['feature']:35s} {row['importance']:.4f} {bar}")

    # Generate future predictions
    print("\n" + "=" * 60)
    print("5-YEAR DECLINE EXPANSION PREDICTIONS")
    print("=" * 60)

    future_df = generate_future_scenarios()
    X_future, _ = prepare_features(future_df)
    future_df["predicted_risk"] = model.predict_proba(X_future)[:, 1]

    # Summary by province and year
    print("\nMean predicted decline risk by province and year:")
    pivot = future_df.pivot_table(
        values="predicted_risk",
        index="province",
        columns="prediction_year",
        aggfunc="mean",
    )
    print(pivot.round(3).to_string())

    # High-risk currently-unaffected municipalities
    print("\n" + "=" * 60)
    print("HIGHEST-RISK CURRENTLY-UNAFFECTED MUNICIPALITIES")
    print("=" * 60)

    # For 2025 predictions, find unaffected areas with highest risk
    future_2025 = future_df[
        (future_df["prediction_year"] == 2025) &
        (future_df["already_affected"] == 0)
    ].sort_values("predicted_risk", ascending=False)

    print(f"\nTop 20 highest-risk unaffected municipalities (2025 prediction):")
    top20 = future_2025.head(20)
    for _, row in top20.iterrows():
        print(f"  {row['municipality_id']} | {row['province']:30s} | "
              f"Risk: {row['predicted_risk']:.3f} | "
              f"NDVI: {row['ndvi_mean']:.3f} | "
              f"Dist: {row['dist_nearest_declining_km']:.1f} km | "
              f"Frost: {row['frost_severity_index']:.1f}")

    # Province-level risk summary
    print("\n" + "=" * 60)
    print("PROVINCE-LEVEL RISK SUMMARY (2025-2029)")
    print("=" * 60)

    for year in [2025, 2027, 2029]:
        year_df = future_df[future_df["prediction_year"] == year]
        unaffected = year_df[year_df["already_affected"] == 0]
        high_risk = unaffected[unaffected["predicted_risk"] > 0.5]

        print(f"\n  Year {year}:")
        for prov in ALL_PROVINCES:
            prov_data = unaffected[unaffected["province"] == prov]
            if len(prov_data) == 0:
                continue
            n_high = len(prov_data[prov_data["predicted_risk"] > 0.5])
            mean_risk = prov_data["predicted_risk"].mean()
            status = FIRST_DETECTION_YEAR.get(prov)
            status_str = f"detected {status}" if status else "undetected"
            print(f"    {prov:30s} | {status_str:15s} | "
                  f"Mean risk: {mean_risk:.3f} | "
                  f"High-risk munis: {n_high}/{len(prov_data)}")

    # Save discoveries
    discoveries_dir = APP_DIR / "discoveries"
    discoveries_dir.mkdir(exist_ok=True)

    # Save full predictions
    output_cols = [
        "municipality_id", "province", "country", "prediction_year",
        "latitude", "longitude", "already_affected",
        "predicted_risk", "ndvi_mean", "ndvi_trend",
        "dist_nearest_declining_km", "frost_severity_index",
    ]
    future_df[output_cols].to_csv(
        discoveries_dir / "five_year_predictions.csv", index=False)

    # Save high-risk unaffected
    high_risk_all = future_df[
        (future_df["already_affected"] == 0) &
        (future_df["predicted_risk"] > 0.5)
    ]
    high_risk_all[output_cols].to_csv(
        discoveries_dir / "high_risk_unaffected.csv", index=False)

    print(f"\nDiscoveries saved to {discoveries_dir}/")
    print(f"  five_year_predictions.csv: {len(future_df)} rows")
    print(f"  high_risk_unaffected.csv: {len(high_risk_all)} rows")

    return importance_df, future_df


if __name__ == "__main__":
    run_discovery()
