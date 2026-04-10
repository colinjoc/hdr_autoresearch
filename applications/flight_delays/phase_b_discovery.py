"""
Phase B: Discovery analysis for flight delay propagation.

Uses the trained model and the synthetic dataset to answer:
1. What fraction of delay is attributable to each mechanism?
2. Which airport pairs are the most effective delay transmitters?
3. Which tail rotations are "super-spreaders"?
4. Where should airlines add buffer for maximum system benefit?

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

from data_loaders import load_dataset, HUB_AIRPORTS, CARRIERS


def delay_variance_decomposition(df: pd.DataFrame) -> dict:
    """Decompose observed arrival delay into 4 mechanisms using BTS cause codes.

    Returns the fraction of total delay-minutes attributable to:
    (a) Aircraft rotation (late aircraft)
    (b) Airport congestion (NAS)
    (c) Weather
    (d) Carrier/crew/gate logistics
    """
    # Only delayed flights have cause codes
    delayed = df[df["arr_delay"] > 15].copy()

    cause_cols = [
        "late_aircraft_delay", "nas_delay", "weather_delay",
        "carrier_delay", "security_delay",
    ]

    total_cause_minutes = delayed[cause_cols].sum().sum()
    if total_cause_minutes == 0:
        return {}

    decomposition = {
        "aircraft_rotation_pct": (
            delayed["late_aircraft_delay"].sum() / total_cause_minutes * 100
        ),
        "airport_congestion_pct": (
            delayed["nas_delay"].sum() / total_cause_minutes * 100
        ),
        "weather_pct": (
            delayed["weather_delay"].sum() / total_cause_minutes * 100
        ),
        "carrier_crew_gate_pct": (
            (delayed["carrier_delay"].sum() + delayed["security_delay"].sum())
            / total_cause_minutes * 100
        ),
        "total_delayed_flights": len(delayed),
        "total_cause_minutes": total_cause_minutes,
    }

    return decomposition


def feature_importance_decomposition(df: pd.DataFrame) -> dict:
    """Decompose R-squared into propagation vs non-propagation features.

    Trains models with and without propagation features to measure
    the unique contribution of the tail-number rotation chain.
    """
    from sklearn.metrics import r2_score
    from model import get_feature_columns, build_model, prepare_features

    df = prepare_features(df)
    feature_cols = get_feature_columns()

    # Split into train/test (last 15%)
    unique_dates = np.sort(df["fl_date"].unique())
    n_test = max(1, int(len(unique_dates) * 0.15))
    cutoff = unique_dates[-n_test]
    train = df[df["fl_date"] < cutoff]
    test = df[df["fl_date"] >= cutoff]

    y_train = train["arr_delay"].values.astype(np.float32)
    y_test = test["arr_delay"].values.astype(np.float32)

    # Full model
    X_train_full = train[feature_cols].values.astype(np.float32)
    X_test_full = test[feature_cols].values.astype(np.float32)

    config = {"family": "xgboost", "params": {
        "n_estimators": 300, "max_depth": 6, "learning_rate": 0.05,
        "min_child_weight": 10, "subsample": 0.8, "colsample_bytree": 0.8,
        "random_state": 42, "device": "cuda",
    }}
    model_full = build_model(config)
    model_full.fit(X_train_full, y_train)
    r2_full = r2_score(y_test, model_full.predict(X_test_full))

    # Model without propagation features
    propagation_features = {
        "prev_leg_arr_delay", "prev_leg_late_aircraft", "rotation_position",
        "prev_leg_delay_x_buffer", "log_prev_delay",
    }
    non_prop_cols = [c for c in feature_cols if c not in propagation_features]

    X_train_noprop = train[non_prop_cols].values.astype(np.float32)
    X_test_noprop = test[non_prop_cols].values.astype(np.float32)

    model_noprop = build_model(config)
    model_noprop.fit(X_train_noprop, y_train)
    r2_noprop = r2_score(y_test, model_noprop.predict(X_test_noprop))

    # Model with ONLY propagation features
    prop_cols_available = [c for c in feature_cols if c in propagation_features]
    X_train_prop = train[prop_cols_available].values.astype(np.float32)
    X_test_prop = test[prop_cols_available].values.astype(np.float32)

    model_prop = build_model(config)
    model_prop.fit(X_train_prop, y_train)
    r2_prop = r2_score(y_test, model_prop.predict(X_test_prop))

    return {
        "r2_full_model": r2_full,
        "r2_without_propagation": r2_noprop,
        "r2_propagation_only": r2_prop,
        "r2_unique_propagation": r2_full - r2_noprop,
        "propagation_share_of_r2": (
            (r2_full - r2_noprop) / r2_full * 100 if r2_full > 0 else 0
        ),
    }


def contagion_network(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Map the delay contagion network: which airport pairs transmit delay most?

    For each origin-dest pair, compute:
    - Mean propagated delay (late_aircraft_delay on flights FROM this dest)
    - Fraction of flights that arrive delayed and then depart delayed on next leg
    """
    # Flights that arrive delayed
    delayed_arrivals = df[df["arr_delay"] > 15].copy()

    # Group by route and compute propagation metrics
    route_stats = delayed_arrivals.groupby(["origin", "dest"]).agg(
        n_delayed=("arr_delay", "count"),
        mean_arr_delay=("arr_delay", "mean"),
        mean_late_aircraft=("late_aircraft_delay", "mean"),
        total_late_aircraft_min=("late_aircraft_delay", "sum"),
    ).reset_index()

    # Sort by total late aircraft minutes (most contagious routes)
    route_stats = route_stats.sort_values(
        "total_late_aircraft_min", ascending=False
    ).head(top_n)

    return route_stats


def super_spreader_rotations(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Identify the tail rotations that consistently propagate the most delay.

    A "super-spreader" is a tail number whose daily rotation chain
    has above-average late_aircraft_delay across multiple legs.
    """
    # Daily rotation stats per tail number
    daily_tail = df.groupby(["fl_date", "tail_num"]).agg(
        n_legs=("flight_id", "count"),
        total_late_aircraft=("late_aircraft_delay", "sum"),
        max_late_aircraft=("late_aircraft_delay", "max"),
        mean_arr_delay=("arr_delay", "mean"),
        carrier=("carrier", "first"),
    ).reset_index()

    # Filter to tails with multiple legs (rotation chains)
    multi_leg = daily_tail[daily_tail["n_legs"] >= 3]

    # Aggregate across days
    tail_stats = multi_leg.groupby(["tail_num", "carrier"]).agg(
        n_days=("fl_date", "count"),
        mean_daily_late_aircraft=("total_late_aircraft", "mean"),
        max_daily_late_aircraft=("total_late_aircraft", "max"),
        mean_n_legs=("n_legs", "mean"),
        mean_daily_delay=("mean_arr_delay", "mean"),
    ).reset_index()

    # Sort by mean daily late aircraft minutes
    tail_stats = tail_stats.sort_values(
        "mean_daily_late_aircraft", ascending=False
    ).head(top_n)

    return tail_stats


def buffer_pareto_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the Pareto front: schedule padding vs delay propagation reduction.

    For each carrier, estimate what happens if buffer time is increased
    by 5, 10, 15 minutes: how much would propagated delay decrease?
    """
    results = []

    for carrier, info in CARRIERS.items():
        carrier_flights = df[df["carrier"] == carrier]
        if len(carrier_flights) < 100:
            continue

        n_flights = len(carrier_flights)
        mean_delay = carrier_flights["arr_delay"].mean()
        mean_propagated = carrier_flights["late_aircraft_delay"].mean()
        buffer_factor = info["buffer_factor"]

        for added_buffer in [0, 5, 10, 15, 20, 30]:
            # Estimate delay reduction from additional buffer
            # Each minute of buffer absorbs one minute of propagated delay
            # up to the amount of propagated delay available to absorb
            reduced_propagation = max(0, mean_propagated - added_buffer * 0.6)
            estimated_delay = mean_delay - (mean_propagated - reduced_propagation)
            system_cost_per_flight = added_buffer  # minutes of extra block time

            results.append({
                "carrier": carrier,
                "carrier_name": info["name"],
                "buffer_factor": buffer_factor,
                "added_buffer_min": added_buffer,
                "n_flights": n_flights,
                "original_mean_delay": round(mean_delay, 1),
                "estimated_mean_delay": round(estimated_delay, 1),
                "delay_reduction_min": round(mean_delay - estimated_delay, 1),
                "cost_minutes_per_flight": added_buffer,
                "ratio_benefit_to_cost": round(
                    (mean_delay - estimated_delay) / max(1, added_buffer), 2
                ) if added_buffer > 0 else 0,
            })

    return pd.DataFrame(results)


def recommended_buffer_additions(df: pd.DataFrame) -> list[dict]:
    """Recommend where airlines should add buffer for maximum system benefit.

    Identifies the 15 highest-impact carrier-route combinations where
    adding 15 minutes of buffer would reduce the most delay-minutes system-wide.
    """
    # Group by carrier and route
    route_carrier = df.groupby(["carrier", "origin", "dest"]).agg(
        n_flights=("flight_id", "count"),
        mean_arr_delay=("arr_delay", "mean"),
        mean_late_aircraft=("late_aircraft_delay", "mean"),
        total_late_aircraft=("late_aircraft_delay", "sum"),
    ).reset_index()

    # Estimate system-wide delay reduction from 15-minute buffer addition
    route_carrier["estimated_reduction_per_flight"] = np.minimum(
        route_carrier["mean_late_aircraft"],
        15.0 * 0.6,  # 60% of buffer absorbed
    )
    route_carrier["total_system_reduction"] = (
        route_carrier["estimated_reduction_per_flight"] * route_carrier["n_flights"]
    )

    # Top recommendations
    top = route_carrier.sort_values(
        "total_system_reduction", ascending=False
    ).head(15)

    recommendations = []
    for _, row in top.iterrows():
        carrier_info = CARRIERS.get(row["carrier"], {})
        recommendations.append({
            "carrier": row["carrier"],
            "carrier_name": carrier_info.get("name", row["carrier"]),
            "route": f"{row['origin']}-{row['dest']}",
            "n_flights": int(row["n_flights"]),
            "current_mean_delay": round(row["mean_arr_delay"], 1),
            "current_mean_propagated": round(row["mean_late_aircraft"], 1),
            "estimated_reduction_per_flight": round(row["estimated_reduction_per_flight"], 1),
            "total_system_minutes_saved": round(row["total_system_reduction"], 0),
        })

    return recommendations


def main():
    print("=" * 70)
    print("  Phase B: Flight Delay Propagation Discovery Analysis")
    print("=" * 70)

    df = load_dataset()
    df = df[df["arr_delay"].notna()].copy()

    # 1. Delay Variance Decomposition
    print(f"\n{'='*70}")
    print("  1. Delay Variance Decomposition (BTS Cause Codes)")
    print(f"{'='*70}")
    decomp = delay_variance_decomposition(df)
    print(f"  Total delayed flights (>15 min): {decomp['total_delayed_flights']:,}")
    print(f"  Total cause-coded minutes: {decomp['total_cause_minutes']:,.0f}")
    print(f"\n  Delay attribution:")
    print(f"    Aircraft rotation (late aircraft): {decomp['aircraft_rotation_pct']:.1f}%")
    print(f"    Airport congestion (NAS):          {decomp['airport_congestion_pct']:.1f}%")
    print(f"    Weather:                           {decomp['weather_pct']:.1f}%")
    print(f"    Carrier/crew/gate logistics:       {decomp['carrier_crew_gate_pct']:.1f}%")

    # 2. Feature Importance Decomposition (R-squared)
    print(f"\n{'='*70}")
    print("  2. Feature Importance Decomposition (Model-Based)")
    print(f"{'='*70}")
    feat_decomp = feature_importance_decomposition(df)
    print(f"  R2 full model:               {feat_decomp['r2_full_model']:.4f}")
    print(f"  R2 WITHOUT propagation feats: {feat_decomp['r2_without_propagation']:.4f}")
    print(f"  R2 propagation feats ONLY:    {feat_decomp['r2_propagation_only']:.4f}")
    print(f"  Unique R2 from propagation:   {feat_decomp['r2_unique_propagation']:.4f}")
    print(f"  Propagation share of R2:      {feat_decomp['propagation_share_of_r2']:.1f}%")

    # 3. Contagion Network
    print(f"\n{'='*70}")
    print("  3. Top 20 Delay Contagion Routes")
    print(f"{'='*70}")
    contagion = contagion_network(df, top_n=20)
    print(f"  {'Route':<12} {'N delayed':>10} {'Mean delay':>12} {'Mean late AC':>12} {'Total late AC':>14}")
    for _, row in contagion.iterrows():
        route = f"{row['origin']}-{row['dest']}"
        print(f"  {route:<12} {row['n_delayed']:>10} {row['mean_arr_delay']:>12.1f} "
              f"{row['mean_late_aircraft']:>12.1f} {row['total_late_aircraft_min']:>14.0f}")

    # 4. Super-Spreader Tail Numbers
    print(f"\n{'='*70}")
    print("  4. Top 20 Super-Spreader Aircraft (Tail Numbers)")
    print(f"{'='*70}")
    spreaders = super_spreader_rotations(df, top_n=20)
    print(f"  {'Tail':<8} {'Carrier':<6} {'Days':>5} {'Mean legs':>10} "
          f"{'Mean daily late AC':>18} {'Max daily late AC':>18}")
    for _, row in spreaders.iterrows():
        print(f"  {row['tail_num']:<8} {row['carrier']:<6} {row['n_days']:>5} "
              f"{row['mean_n_legs']:>10.1f} {row['mean_daily_late_aircraft']:>18.1f} "
              f"{row['max_daily_late_aircraft']:>18.1f}")

    # 5. Buffer Pareto Analysis
    print(f"\n{'='*70}")
    print("  5. Buffer Padding Pareto Analysis")
    print(f"{'='*70}")
    pareto = buffer_pareto_analysis(df)
    for carrier in pareto["carrier"].unique():
        carrier_data = pareto[pareto["carrier"] == carrier]
        name = carrier_data.iloc[0]["carrier_name"]
        bf = carrier_data.iloc[0]["buffer_factor"]
        print(f"\n  {carrier} ({name}, buffer factor={bf:.2f}):")
        for _, row in carrier_data.iterrows():
            if row["added_buffer_min"] == 0:
                print(f"    Current:        mean delay = {row['original_mean_delay']:.1f} min")
            else:
                print(f"    +{row['added_buffer_min']:>2} min buffer: "
                      f"est. delay = {row['estimated_mean_delay']:.1f} min "
                      f"(saves {row['delay_reduction_min']:.1f} min, "
                      f"ratio = {row['ratio_benefit_to_cost']:.2f})")

    # 6. Recommendations
    print(f"\n{'='*70}")
    print("  6. Top 15 Recommendations: Where to Add 15 Minutes of Buffer")
    print(f"{'='*70}")
    recs = recommended_buffer_additions(df)
    for i, rec in enumerate(recs, 1):
        print(f"  {i:>2}. {rec['carrier_name']:<12} {rec['route']:<10} "
              f"({rec['n_flights']:>5} flights): "
              f"saves {rec['estimated_reduction_per_flight']:.1f} min/flight, "
              f"{rec['total_system_minutes_saved']:,.0f} total min")

    print(f"\n{'='*70}")
    print("  Phase B Discovery Complete")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
