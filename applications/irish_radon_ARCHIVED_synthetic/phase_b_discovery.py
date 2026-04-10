"""
Phase B Discovery: Irish Radon Hidden Danger Zones.

Generates predictions for all areas and identifies the "hidden danger" zones
where radon risk is HIGH (geology predicts >200 Bq/m3), BER rating is HIGH
(airtight homes), and no radon measurement exists.

Also quantifies the BER x geology interaction (Phase 2.5).

Usage:
    python phase_b_discovery.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, get_train_test_split, COUNTIES
from model import get_feature_columns, build_model, prepare_features

DISCOVERIES_DIR = APP_DIR / "discoveries"
DISCOVERIES_DIR.mkdir(exist_ok=True)


def run_phase_25_ber_radon_tension(df: pd.DataFrame, clf, X_all, feature_cols):
    """Phase 2.5: Quantify the BER x geology interaction.

    Tests whether A-rated homes on high-radon geology have higher predicted
    radon risk than G-rated homes on the same geology.
    """
    print("\n" + "=" * 60)
    print("Phase 2.5: The Retrofit-Radon Tension")
    print("=" * 60)

    # Predict radon probability for all areas
    y_prob = clf.predict_proba(X_all)[:, 1]
    df = df.copy()
    df["radon_risk_prob"] = y_prob

    # Split by geology type and BER rating
    print("\n  Radon risk by geology type:")
    for geo_type in ["granite", "limestone_pure", "limestone_impure",
                     "black_shale", "sandstone", "shale"]:
        mask = df["bedrock_code"] == geo_type
        if mask.sum() > 10:
            risk = df.loc[mask, "radon_risk_prob"].mean()
            hra_actual = df.loc[mask, "is_hra"].mean()
            print(f"    {geo_type:>20}: predicted risk={risk:.3f}, "
                  f"actual HRA={hra_actual:.3f}, n={mask.sum()}")

    # THE HEADLINE: BER rating x geology interaction
    print("\n  BER x geology interaction (THE HEADLINE):")
    print("  " + "-" * 70)
    print(f"  {'Geology':<20} {'High BER (>10)':<20} {'Low BER (<6)':<20} {'Ratio':>8}")
    print("  " + "-" * 70)

    high_ber_mask = df["mean_ber_rating_ordinal"] > 10  # A/B rated areas
    low_ber_mask = df["mean_ber_rating_ordinal"] < 6    # E/F/G rated areas

    interactions = []
    for geo_type in ["granite", "limestone_pure", "black_shale", "sandstone"]:
        geo_mask = df["bedrock_code"] == geo_type
        high_risk = df.loc[geo_mask & high_ber_mask, "radon_risk_prob"].mean()
        low_risk = df.loc[geo_mask & low_ber_mask, "radon_risk_prob"].mean()
        n_high = (geo_mask & high_ber_mask).sum()
        n_low = (geo_mask & low_ber_mask).sum()

        if n_high > 0 and n_low > 0 and low_risk > 0:
            ratio = high_risk / low_risk
            print(f"  {geo_type:<20} {high_risk:.3f} (n={n_high:>4})"
                  f"    {low_risk:.3f} (n={n_low:>4})"
                  f"    {ratio:>7.2f}x")
            interactions.append({
                "geology": geo_type,
                "high_ber_risk": high_risk,
                "low_ber_risk": low_risk,
                "ratio": ratio,
                "n_high": n_high,
                "n_low": n_low,
            })

    if interactions:
        mean_ratio = np.mean([i["ratio"] for i in interactions])
        print(f"\n  Mean risk ratio (high BER / low BER): {mean_ratio:.2f}x")
        print(f"  Interpretation: On average, areas with airtight (A/B-rated) homes")
        print(f"  have {mean_ratio:.2f}x the predicted radon risk of areas with")
        print(f"  leaky (E/F/G-rated) homes, controlling for geology.")

    # Per-county BER-radon interaction
    print("\n  Per-county BER effect on granite:")
    granite_mask = df["bedrock_code"] == "granite"
    for county in sorted(df.loc[granite_mask, "county"].unique()):
        county_granite = granite_mask & (df["county"] == county)
        if county_granite.sum() > 5:
            high = df.loc[county_granite & high_ber_mask, "radon_risk_prob"]
            low = df.loc[county_granite & low_ber_mask, "radon_risk_prob"]
            if len(high) > 0 and len(low) > 0:
                print(f"    {county:>15}: High BER risk={high.mean():.3f} (n={len(high)}), "
                      f"Low BER risk={low.mean():.3f} (n={len(low)})")

    return interactions


def run_phase_b_discovery(df: pd.DataFrame, clf, X_all, feature_cols):
    """Phase B: Identify hidden danger zones.

    Hidden danger = high radon risk + high BER + sparse measurement.
    """
    print("\n" + "=" * 60)
    print("Phase B: Discovery — Hidden Danger Zones")
    print("=" * 60)

    y_prob = clf.predict_proba(X_all)[:, 1]
    df = df.copy()
    df["radon_risk_prob"] = y_prob

    # Define hidden danger criteria
    high_radon_risk = df["radon_risk_prob"] > 0.5  # Predicted HRA
    high_ber = df["mean_ber_rating_ordinal"] > 9   # B-rated or better (mean)
    sparse_measurements = df["n_measurements"] < 10

    hidden_danger = high_radon_risk & high_ber & sparse_measurements
    df["is_hidden_danger"] = hidden_danger.astype(int)

    n_danger = hidden_danger.sum()
    print(f"\n  Total areas: {len(df)}")
    print(f"  Predicted HRA (risk > 0.5): {high_radon_risk.sum()} ({high_radon_risk.mean()*100:.1f}%)")
    print(f"  High BER areas (mean > B3): {high_ber.sum()} ({high_ber.mean()*100:.1f}%)")
    print(f"  Sparse measurements (<10): {sparse_measurements.sum()} ({sparse_measurements.mean()*100:.1f}%)")
    print(f"  HIDDEN DANGER zones: {n_danger} ({n_danger/len(df)*100:.1f}%)")

    # Top 100 hidden danger zones
    danger_df = df[hidden_danger].sort_values("radon_risk_prob", ascending=False).head(100)

    print(f"\n  Top 20 hidden danger zones:")
    print(f"  {'Area ID':<12} {'County':<15} {'Risk':>6} {'BER':>5} {'Bedrock':<18} {'Quat':<15}")
    print("  " + "-" * 75)
    for _, row in danger_df.head(20).iterrows():
        print(f"  {row['area_id']:<12} {row['county']:<15} "
              f"{row['radon_risk_prob']:>5.3f} {row['mean_ber_rating_ordinal']:>5.1f} "
              f"{row['bedrock_code']:<18} {row['quat_code']:<15}")

    # County distribution of hidden danger zones
    print(f"\n  Hidden danger zones by county:")
    county_danger = danger_df["county"].value_counts()
    for county, count in county_danger.items():
        print(f"    {county:>15}: {count}")

    # Geology distribution
    print(f"\n  Hidden danger zones by bedrock geology:")
    geo_danger = danger_df["bedrock_code"].value_counts()
    for geo, count in geo_danger.items():
        print(f"    {geo:>20}: {count}")

    # Save discoveries
    danger_df.to_csv(DISCOVERIES_DIR / "hidden_danger_zones.csv", index=False)
    print(f"\n  Saved top 100 hidden danger zones to discoveries/hidden_danger_zones.csv")

    # Population-weighted risk map summary
    print("\n  Risk summary by county:")
    print(f"  {'County':<15} {'Mean Risk':>10} {'Pct HRA Predicted':>18} {'Pct HRA Actual':>15} {'n':>5}")
    print("  " + "-" * 68)
    for county in sorted(COUNTIES):
        mask = df["county"] == county
        if mask.sum() > 0:
            mean_risk = df.loc[mask, "radon_risk_prob"].mean()
            pct_pred = (df.loc[mask, "radon_risk_prob"] > 0.5).mean() * 100
            pct_actual = df.loc[mask, "is_hra"].mean() * 100
            n = mask.sum()
            flag = " ***" if abs(pct_pred - pct_actual) > 15 else ""
            print(f"  {county:<15} {mean_risk:>10.3f} {pct_pred:>17.1f}% {pct_actual:>14.1f}% {n:>5}{flag}")

    return danger_df


def main():
    print("Loading dataset...")
    df = load_dataset()
    print(f"  {len(df)} areas, HRA prevalence: {df['is_hra'].mean()*100:.1f}%")

    # Train model on full dataset (for discovery)
    print("\nTraining model on full dataset for discovery...")
    X_all, y_all = prepare_features(df)
    clf = build_model()
    clf.fit(X_all, y_all)

    feature_cols = get_feature_columns()

    # Phase 2.5: BER x geology interaction
    interactions = run_phase_25_ber_radon_tension(df, clf, X_all, feature_cols)

    # Phase B: Hidden danger zones
    danger_df = run_phase_b_discovery(df, clf, X_all, feature_cols)

    # Feature importance for the final model
    print("\n" + "=" * 60)
    print("Feature Importance (Final Model)")
    print("=" * 60)
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        pairs = sorted(zip(feature_cols, importances), key=lambda x: -x[1])
        for fname, imp in pairs[:20]:
            bar = "#" * int(imp * 200)
            print(f"  {fname:>30}: {imp:.4f} {bar}")

    print("\n" + "=" * 60)
    print("Phase B Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
