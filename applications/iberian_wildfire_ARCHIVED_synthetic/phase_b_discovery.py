"""
Phase B Discovery: Map VLF risk across Iberia and identify
critical thresholds.

Produces:
1. Top 20 municipalities at highest 2026 VLF risk
2. FWI threshold where VLF probability exceeds 50%
3. LFMC threshold where VLF probability exceeds 50%
4. Pareto front: prescribed burning investment vs risk reduction
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import RobustScaler

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    load_dataset, NUTS3_REGIONS, FIRE_SPREAD_MULTIPLIER,
    _compute_fwi_from_weather,
)
from model import get_feature_columns, SENTINEL2_FEATURES, prepare_features


def train_final_model(df: pd.DataFrame):
    """Train the final Ridge model on all pre-2025 data."""
    feature_cols = get_feature_columns()
    train_df = df[df["year"] < 2025].copy()

    X = train_df[feature_cols].copy()
    for col in SENTINEL2_FEATURES:
        if col in X.columns:
            X[col] = X[col].fillna(X[col].median())
    X = X.fillna(0).values.astype(np.float32)
    y = train_df["is_vlf"].values

    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    model.fit(X_scaled, y)

    return model, scaler, feature_cols


def compute_feature_coefficients(model, feature_cols):
    """Extract and rank feature coefficients from logistic regression."""
    coeffs = model.coef_[0]
    coeff_df = pd.DataFrame({
        "feature": feature_cols,
        "coefficient": coeffs,
        "abs_coefficient": np.abs(coeffs),
    }).sort_values("abs_coefficient", ascending=False)
    return coeff_df


def find_thresholds(df, model, scaler, feature_cols):
    """Find FWI and LFMC thresholds where VLF probability exceeds 50%."""
    # Use median values for all features
    medians = {}
    for col in feature_cols:
        vals = df[col].dropna()
        medians[col] = vals.median() if len(vals) > 0 else 0

    print("\n  --- FWI Threshold Analysis ---")
    fwi_range = np.arange(0, 80, 0.5)
    fwi_probs = []
    for fwi_val in fwi_range:
        row = {col: medians[col] for col in feature_cols}
        row["fwi"] = fwi_val
        X = np.array([[row[c] for c in feature_cols]], dtype=np.float32)
        X_scaled = scaler.transform(X)
        prob = model.predict_proba(X_scaled)[0, 1]
        fwi_probs.append(prob)

    fwi_probs = np.array(fwi_probs)
    fwi_50 = None
    for i, p in enumerate(fwi_probs):
        if p >= 0.50:
            fwi_50 = fwi_range[i]
            break

    if fwi_50:
        print(f"    FWI threshold for 50% VLF probability: {fwi_50:.1f}")
    else:
        max_prob = fwi_probs.max()
        print(f"    FWI never reaches 50% VLF probability (max: {max_prob:.3f} at FWI={fwi_range[np.argmax(fwi_probs)]:.1f})")
        # Find the FWI where probability doubles from baseline
        base_prob = fwi_probs[0]
        for i, p in enumerate(fwi_probs):
            if p >= 2 * base_prob:
                print(f"    FWI threshold for 2x baseline risk: {fwi_range[i]:.1f}")
                break

    print("\n  --- LFMC Threshold Analysis ---")
    lfmc_range = np.arange(30, 200, 1)
    lfmc_probs = []
    for lfmc_val in lfmc_range:
        row = {col: medians[col] for col in feature_cols}
        row["lfmc"] = lfmc_val
        X = np.array([[row[c] for c in feature_cols]], dtype=np.float32)
        X_scaled = scaler.transform(X)
        prob = model.predict_proba(X_scaled)[0, 1]
        lfmc_probs.append(prob)

    lfmc_probs = np.array(lfmc_probs)
    lfmc_50 = None
    for i in range(len(lfmc_probs) - 1, -1, -1):  # Decreasing LFMC = more risk
        if lfmc_probs[i] >= 0.50:
            lfmc_50 = lfmc_range[i]
            break

    if lfmc_50:
        print(f"    LFMC threshold for 50% VLF probability: {lfmc_50:.0f}%")
    else:
        max_prob = lfmc_probs.max()
        print(f"    LFMC never reaches 50% VLF probability (max: {max_prob:.3f} at LFMC={lfmc_range[np.argmax(lfmc_probs)]:.0f}%)")
        base_prob = lfmc_probs[-1]  # High LFMC = low risk
        for i in range(len(lfmc_probs) - 1, -1, -1):
            if lfmc_probs[i] >= 2 * base_prob:
                print(f"    LFMC threshold for 2x baseline risk: {lfmc_range[i]:.0f}%")
                break

    return {
        "fwi_threshold_50": fwi_50,
        "lfmc_threshold_50": lfmc_50,
        "fwi_probs": (fwi_range, fwi_probs),
        "lfmc_probs": (lfmc_range, lfmc_probs),
    }


def rank_municipalities(df, model, scaler, feature_cols):
    """Rank NUTS-3 municipalities by predicted 2026 VLF risk."""
    print("\n  --- Top 20 Municipalities at Highest 2026 VLF Risk ---")

    # Use 2025 fire season conditions (worst year) as proxy for 2026 risk
    df_2025 = df[df["year"] == 2025].copy()

    muni_risks = []
    for nuts3, info in NUTS3_REGIONS.items():
        # Get fires in this region
        region_fires = df_2025[df_2025["nuts3"] == nuts3]
        if len(region_fires) == 0:
            region_fires = df[df["nuts3"] == nuts3]

        if len(region_fires) == 0:
            continue

        # Use mean conditions in the fire season (July-Aug)
        summer = region_fires[region_fires["month"].isin([7, 8])]
        if len(summer) == 0:
            summer = region_fires

        X = summer[feature_cols].copy()
        for col in SENTINEL2_FEATURES:
            if col in X.columns:
                X[col] = X[col].fillna(X[col].median())
        X = X.fillna(0).values.astype(np.float32)
        X_scaled = scaler.transform(X)

        probs = model.predict_proba(X_scaled)[:, 1]
        mean_vlf_prob = probs.mean()
        max_vlf_prob = probs.max()
        n_fires = len(summer)
        vlf_count = summer["is_vlf"].sum()

        muni_risks.append({
            "nuts3": nuts3,
            "name": info["name"],
            "country": info["country"],
            "lat": info["lat"],
            "eucalyptus_frac": info["eucalyptus_frac"],
            "mean_vlf_prob": mean_vlf_prob,
            "max_vlf_prob": max_vlf_prob,
            "n_fires": n_fires,
            "vlf_count": vlf_count,
        })

    risk_df = pd.DataFrame(muni_risks).sort_values("mean_vlf_prob", ascending=False)

    print(f"\n  {'Rank':<5} {'NUTS-3':<8} {'Name':<30} {'Country':<5} "
          f"{'Mean VLF%':<10} {'Max VLF%':<10} {'Eucalyptus':<12} {'Fires':<7}")
    print("  " + "-" * 90)
    for i, row in risk_df.head(20).iterrows():
        rank = list(risk_df.index).index(i) + 1
        print(f"  {rank:<5} {row['nuts3']:<8} {row['name']:<30} {row['country']:<5} "
              f"{row['mean_vlf_prob']:>8.1%}  {row['max_vlf_prob']:>8.1%}  "
              f"{row['eucalyptus_frac']:>10.0%}  {row['n_fires']:>5}")

    return risk_df


def pareto_analysis(risk_df):
    """Estimate prevention investment vs risk reduction Pareto front."""
    print("\n  --- Pareto Front: Prevention Investment vs Risk Reduction ---")
    print("  (Estimated based on eucalyptus fraction and fire density)")
    print()

    # Simple model: prescribed burning reduces risk proportional to area treated
    # Cost: ~500 EUR/ha for prescribed burning in Mediterranean scrubland
    # Fuel break construction: ~5000 EUR/km
    # Each 10% reduction in eucalyptus fraction -> ~15% VLF risk reduction

    risk_df = risk_df.copy()
    risk_df["risk_score"] = risk_df["mean_vlf_prob"] * risk_df["n_fires"]

    # Pareto-efficient prevention targets
    print(f"  {'Municipality':<30} {'Risk Score':<12} {'Est. Annual Cost':<18} {'Risk Reduction':<15}")
    print("  " + "-" * 75)

    total_cost = 0
    total_reduction = 0
    for _, row in risk_df.head(10).iterrows():
        # Simplified cost model
        area_to_treat = row["n_fires"] * 50  # 50 ha prescribed burn per fire risk area
        cost = area_to_treat * 500  # EUR per ha
        reduction = row["risk_score"] * 0.3  # 30% risk reduction from treatment
        total_cost += cost
        total_reduction += reduction

        print(f"  {row['name']:<30} {row['risk_score']:<12.3f} "
              f"EUR {cost:>12,.0f}  {reduction:>12.3f}")

    print(f"\n  Total estimated prevention budget (top 10 municipalities): EUR {total_cost:,.0f}")
    print(f"  Total estimated risk reduction: {total_reduction:.3f}")


def main():
    print("=" * 60)
    print("  Phase B: Discovery — VLF Risk Mapping")
    print("=" * 60)

    df = load_dataset()
    df = prepare_features(df)

    model, scaler, feature_cols = train_final_model(df)
    print(f"\n  Model trained on {len(df[df['year'] < 2025])} fires (2006-2024)")

    # Feature coefficients
    coeff_df = compute_feature_coefficients(model, feature_cols)
    print("\n  --- Feature Coefficients (Logistic Regression) ---")
    for _, row in coeff_df.iterrows():
        direction = "+" if row["coefficient"] > 0 else "-"
        print(f"    {row['feature']:25s} {direction} {row['abs_coefficient']:.4f}")

    # Thresholds
    thresholds = find_thresholds(df, model, scaler, feature_cols)

    # Municipality ranking
    risk_df = rank_municipalities(df, model, scaler, feature_cols)

    # Save discoveries
    discoveries_dir = APP_DIR / "discoveries"
    discoveries_dir.mkdir(exist_ok=True)
    risk_df.to_csv(discoveries_dir / "municipality_vlf_risk.csv", index=False)
    coeff_df.to_csv(discoveries_dir / "feature_coefficients.csv", index=False)

    # Pareto analysis
    pareto_analysis(risk_df)

    print(f"\n  Discoveries saved to {discoveries_dir}/")


if __name__ == "__main__":
    main()
