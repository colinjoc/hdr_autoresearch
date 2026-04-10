"""
Phase 2.5 (composition retest + blackout day analysis) and
Phase B (discovery sweep) for Iberian blackout cascade prediction.

Generates:
- Detailed blackout day analysis with feature contributions
- Risk surface: SNSP vs inertia proxy
- Pareto front: RE penetration vs predicted stability margin
- Top-N most dangerous historical hours
- Counterfactual analysis for April 28

Usage:
    python phase_b_discovery.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, get_train_test_split
from model import build_model, prepare_features, get_feature_columns

DISCOVERIES_DIR = APP_DIR / "discoveries"
DISCOVERIES_DIR.mkdir(exist_ok=True)


def train_final_model(df: pd.DataFrame):
    """Train the final model on all pre-blackout data."""
    train_df, test_df = get_train_test_split(df, test_date="2025-04-28")
    X_train, y_train = prepare_features(train_df)

    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    clf = build_model()
    clf.fit(X_train_scaled, y_train)

    return clf, scaler, train_df, test_df


def phase_25_composition_retest(df: pd.DataFrame):
    """Phase 2.5: Verify the composition of kept changes still works together."""
    print("=" * 70)
    print("Phase 2.5: Composition Retest")
    print("=" * 70)

    clf, scaler, train_df, test_df = train_final_model(df)
    feature_cols = get_feature_columns()

    # Evaluate on full training set to check for overfitting
    X_train, y_train = prepare_features(train_df)
    X_train_scaled = scaler.transform(X_train)
    train_proba = clf.predict_proba(X_train_scaled)[:, 1]

    from sklearn.metrics import roc_auc_score
    train_auc = roc_auc_score(y_train, train_proba)
    print(f"\n  Train AUC: {train_auc:.4f}")

    # Evaluate on holdout (April 28)
    if len(test_df) > 0:
        X_test, y_test = prepare_features(test_df)
        X_test_scaled = scaler.transform(X_test)
        test_proba = clf.predict_proba(X_test_scaled)[:, 1]

        test_auc = roc_auc_score(y_test, test_proba)
        print(f"  Holdout AUC: {test_auc:.4f}")

        # Blackout day detailed
        hours = test_df.index.hour
        print(f"\n  April 28, 2025 — hour-by-hour risk scores:")
        print(f"  {'Hour':>6} {'True':>6} {'P(risk)':>8} {'SNSP':>8} {'InertiaS':>10} {'Ramp':>10}")
        for i in range(len(test_df)):
            h = hours[i]
            flag = " ***" if test_proba[i] == test_proba.max() else ""
            flag = " <<< CASCADE" if (h == 12 and y_test[i] == 1) else flag
            print(f"  {h:>6} {y_test[i]:>6} {test_proba[i]:>8.4f} "
                  f"{test_df.iloc[i]['snsp']:>8.3f} "
                  f"{test_df.iloc[i].get('inertia_proxy_s', 0):>10.2f} "
                  f"{test_df.iloc[i].get('total_ramp_1h_mw', 0):>10.0f}{flag}")

        # Pre-cascade detection test
        # The cascade started at ~12:33 CET. Can the model flag 10-12 as high risk?
        pre_cascade = test_proba[(hours >= 10) & (hours < 12)]
        if len(pre_cascade) > 0:
            max_pre_cascade = pre_cascade.max()
            # Use risk ranking instead of threshold
            all_proba_sorted = np.sort(train_proba)[::-1]
            pct_rank = (all_proba_sorted < max_pre_cascade).mean()
            print(f"\n  Pre-cascade (10:00-11:59) max risk score: {max_pre_cascade:.4f}")
            print(f"  Percentile rank vs training data: top {(1-pct_rank)*100:.1f}%")

    # Feature importance
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        pairs = sorted(zip(feature_cols, importances), key=lambda x: -x[1])
        print(f"\n  Feature importances (top 15):")
        for fname, imp in pairs[:15]:
            bar = "#" * int(imp * 200)
            print(f"    {fname:>30}: {imp:.4f} {bar}")

    return clf, scaler


def phase_b_top_dangerous_hours(df: pd.DataFrame, clf, scaler, top_n: int = 20):
    """Identify the most dangerous hours in the historical record."""
    print("\n" + "=" * 70)
    print(f"Phase B: Top {top_n} Most Dangerous Historical Hours")
    print("=" * 70)

    X_all, y_all = prepare_features(df)
    X_all_scaled = scaler.transform(X_all)
    all_proba = clf.predict_proba(X_all_scaled)[:, 1]

    # Add predictions to dataframe
    df_scored = df.copy()
    df_scored["risk_score"] = all_proba
    df_scored["true_excursion"] = y_all

    # Top N most dangerous hours
    top = df_scored.nlargest(top_n, "risk_score")
    print(f"\n  {'Rank':>4} {'Timestamp':>20} {'P(risk)':>8} {'True':>6} {'SNSP':>8} {'InertiaS':>10}")
    for rank, (idx, row) in enumerate(top.iterrows(), 1):
        flag = " *** CONFIRMED" if row["true_excursion"] == 1 else ""
        print(f"  {rank:>4} {str(idx):>20} {row['risk_score']:>8.4f} "
              f"{int(row['true_excursion']):>6} {row['snsp']:>8.3f} "
              f"{row.get('inertia_proxy_s', 0):>10.2f}{flag}")

    # Save discoveries
    top.to_csv(DISCOVERIES_DIR / "top_dangerous_hours.csv")
    print(f"\n  Saved to {DISCOVERIES_DIR / 'top_dangerous_hours.csv'}")

    return df_scored


def phase_b_risk_surface(df_scored: pd.DataFrame):
    """Generate 2D risk surface: SNSP vs inertia proxy."""
    print("\n" + "=" * 70)
    print("Phase B: Risk Surface (SNSP vs Inertia)")
    print("=" * 70)

    # Bin SNSP and inertia
    snsp_bins = np.linspace(0, 0.8, 17)
    inertia_bins = np.linspace(1.5, 5.0, 15)

    df_scored["snsp_bin"] = pd.cut(df_scored["snsp"], bins=snsp_bins)
    df_scored["inertia_bin"] = pd.cut(df_scored["inertia_proxy_s"], bins=inertia_bins)

    # Mean risk per bin
    pivot = df_scored.groupby(["snsp_bin", "inertia_bin"])["risk_score"].mean()
    pivot_2d = pivot.unstack()

    # Print as text heatmap
    print("\n  Mean risk score by SNSP (rows) and Inertia_s (columns):")
    print("  (Higher = more dangerous)")

    if not pivot_2d.empty:
        # Print top 10 most dangerous SNSP-inertia combinations
        risk_combos = []
        for (snsp_b, inertia_b), risk in pivot.items():
            if not np.isnan(risk):
                risk_combos.append({
                    "snsp_range": str(snsp_b),
                    "inertia_range": str(inertia_b),
                    "mean_risk": risk,
                    "n_hours": df_scored[
                        (df_scored["snsp_bin"] == snsp_b) &
                        (df_scored["inertia_bin"] == inertia_b)
                    ].shape[0],
                })

        risk_combos.sort(key=lambda x: -x["mean_risk"])
        print(f"\n  Top 10 most dangerous grid-state regions:")
        print(f"  {'Rank':>4} {'SNSP Range':>20} {'Inertia Range':>20} {'Mean Risk':>10} {'N Hours':>8}")
        for i, combo in enumerate(risk_combos[:10], 1):
            print(f"  {i:>4} {combo['snsp_range']:>20} {combo['inertia_range']:>20} "
                  f"{combo['mean_risk']:>10.4f} {combo['n_hours']:>8}")

        # Save
        pd.DataFrame(risk_combos).to_csv(DISCOVERIES_DIR / "risk_surface.csv", index=False)
        print(f"\n  Saved to {DISCOVERIES_DIR / 'risk_surface.csv'}")


def phase_b_pareto_front(df_scored: pd.DataFrame):
    """Generate Pareto front: RE penetration % vs predicted frequency stability margin."""
    print("\n" + "=" * 70)
    print("Phase B: Pareto Front — RE Penetration vs Stability")
    print("=" * 70)

    # Bin RE fraction into 5% increments
    re_bins = np.arange(0, 0.85, 0.05)
    df_scored["re_bin"] = pd.cut(df_scored["re_fraction"], bins=re_bins)

    pareto_data = []
    for bin_label in df_scored["re_bin"].dropna().unique():
        subset = df_scored[df_scored["re_bin"] == bin_label]
        if len(subset) < 10:
            continue
        pareto_data.append({
            "re_fraction_midpoint": (bin_label.left + bin_label.right) / 2,
            "mean_risk": subset["risk_score"].mean(),
            "p95_risk": subset["risk_score"].quantile(0.95),
            "max_risk": subset["risk_score"].max(),
            "excursion_rate": subset["true_excursion"].mean(),
            "n_hours": len(subset),
            "mean_snsp": subset["snsp"].mean(),
            "mean_inertia_s": subset["inertia_proxy_s"].mean(),
        })

    pareto_df = pd.DataFrame(pareto_data).sort_values("re_fraction_midpoint")

    print(f"\n  RE Penetration vs Risk:")
    print(f"  {'RE%':>8} {'Mean Risk':>10} {'P95 Risk':>10} {'Exc Rate':>10} {'Hours':>8} {'Mean SNSP':>10}")
    for _, row in pareto_df.iterrows():
        print(f"  {row['re_fraction_midpoint']*100:>7.1f}% "
              f"{row['mean_risk']:>10.4f} {row['p95_risk']:>10.4f} "
              f"{row['excursion_rate']:>10.4f} {row['n_hours']:>8.0f} "
              f"{row['mean_snsp']:>10.3f}")

    # Identify "cliff edge" — where risk jumps
    if len(pareto_df) > 2:
        pareto_df["risk_gradient"] = pareto_df["mean_risk"].diff() / 0.05
        max_gradient_idx = pareto_df["risk_gradient"].abs().idxmax()
        if not np.isnan(max_gradient_idx):
            cliff = pareto_df.loc[max_gradient_idx]
            print(f"\n  Steepest risk gradient at RE = {cliff['re_fraction_midpoint']*100:.0f}%")
            print(f"  (This is where adding more renewables most rapidly increases risk)")

    pareto_df.to_csv(DISCOVERIES_DIR / "pareto_front.csv", index=False)
    print(f"\n  Saved to {DISCOVERIES_DIR / 'pareto_front.csv'}")


def phase_b_counterfactual(df: pd.DataFrame, clf, scaler):
    """Counterfactual: What if SNSP had been 60% on April 28?"""
    print("\n" + "=" * 70)
    print("Phase B: Counterfactual Analysis — April 28 at Lower SNSP")
    print("=" * 70)

    _, test_df = get_train_test_split(df, test_date="2025-04-28")
    if len(test_df) == 0:
        print("  No blackout day data available")
        return

    feature_cols = get_feature_columns()

    # Original predictions
    X_test, y_test = prepare_features(test_df)
    X_test_scaled = scaler.transform(X_test)
    original_proba = clf.predict_proba(X_test_scaled)[:, 1]

    # Counterfactual: reduce SNSP to 60% by increasing synchronous gen
    counterfactual_df = test_df.copy()

    # Find the SNSP and hour_snsp columns in feature list
    snsp_idx = feature_cols.index("snsp") if "snsp" in feature_cols else None
    hour_snsp_idx = feature_cols.index("hour_snsp") if "hour_snsp" in feature_cols else None

    print(f"\n  Scenario: What if SNSP had been capped at 60% on April 28?")
    print(f"  (Simulating more synchronous generation online)")

    # Modify the relevant features
    X_cf = X_test.copy()
    for i in range(len(X_cf)):
        row = test_df.iloc[i]
        actual_snsp = row["snsp"]
        if actual_snsp > 0.60:
            # Scale down wind and solar proportionally
            scale = 0.60 / max(actual_snsp, 0.01)
            wind_idx = feature_cols.index("gen_wind_mw") if "gen_wind_mw" in feature_cols else None
            solar_idx = feature_cols.index("gen_solar_mw") if "gen_solar_mw" in feature_cols else None
            if wind_idx is not None:
                X_cf[i, wind_idx] *= scale
            if solar_idx is not None:
                X_cf[i, solar_idx] *= scale
            # Update residual demand
            rd_idx = feature_cols.index("residual_demand_mw") if "residual_demand_mw" in feature_cols else None
            if rd_idx is not None:
                load_idx = feature_cols.index("load_total_mw")
                X_cf[i, rd_idx] = X_cf[i, load_idx] - X_cf[i, wind_idx or 0] - X_cf[i, solar_idx or 0]

    X_cf_scaled = scaler.transform(X_cf)
    cf_proba = clf.predict_proba(X_cf_scaled)[:, 1]

    hours = test_df.index.hour
    print(f"\n  {'Hour':>6} {'Actual P':>10} {'CF P(60%)':>10} {'Change':>10}")
    for i in range(len(test_df)):
        delta = cf_proba[i] - original_proba[i]
        print(f"  {hours[i]:>6} {original_proba[i]:>10.4f} {cf_proba[i]:>10.4f} {delta:>+10.4f}")

    print(f"\n  Mean risk reduction from SNSP cap at 60%: "
          f"{(original_proba.mean() - cf_proba.mean())*100:+.2f}pp")
    print(f"  Max risk hour (original): P={original_proba.max():.4f}")
    print(f"  Max risk hour (counterfactual): P={cf_proba.max():.4f}")


def main():
    print("Loading dataset...")
    df = load_dataset()

    # Need to add computed features that Phase 2 added
    if "hour_snsp" not in df.columns:
        df["hour_snsp"] = df["hour_sin"] * df["snsp"]
    if "residual_demand_ramp_1h" not in df.columns:
        df["residual_demand_ramp_1h"] = df["residual_demand_mw"].diff(1).fillna(0)
    if "expected_rocof" not in df.columns:
        df["expected_rocof"] = 6000 / (2 * df["inertia_proxy_mws"].clip(lower=1))
    if "inertia_floor_dist" not in df.columns:
        df["inertia_floor_dist"] = df["inertia_proxy_s"] - 3.0
    if "snsp_above_65pct" not in df.columns:
        df["snsp_above_65pct"] = (df["snsp"] > 0.65).astype(float)
    if "snsp_above_75pct" not in df.columns:
        df["snsp_above_75pct"] = (df["snsp"] > 0.75).astype(float)
    if "snsp_times_inertia" not in df.columns:
        df["snsp_times_inertia"] = df["snsp"] * df["inertia_proxy_s"]
    if "snsp_squared" not in df.columns:
        df["snsp_squared"] = df["snsp"] ** 2

    # Set model to Phase 2 winning config
    import model as M
    M.EXTRA_FEATURES.clear()
    M.EXTRA_FEATURES.extend(["total_ramp_1h_mw", "residual_demand_mw", "hour_snsp"])

    print(f"Features: {M.get_feature_columns()}")

    # Phase 2.5
    clf, scaler = phase_25_composition_retest(df)

    # Phase B
    df_scored = phase_b_top_dangerous_hours(df, clf, scaler)
    phase_b_risk_surface(df_scored)
    phase_b_pareto_front(df_scored)
    phase_b_counterfactual(df, clf, scaler)

    print("\n" + "=" * 70)
    print("Phase 2.5 + Phase B COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
