#!/usr/bin/env python3
"""Evaluate NYC congestion charge effect decomposition.

Runs all HDR phases:
  Phase 0.5: Baseline (ExtraTrees volume prediction, 5-fold CV)
  Phase 1: Model tournament (5 families)
  Phase 2: Decomposition + DID + counterfactual analysis
  Phase 2.5: Robustness checks
  TLC/MTA supplementary analyses

Usage:
    python evaluate.py
    python evaluate.py --phase baseline
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
RESULTS_PATH = HERE / "results.tsv"

from data_loaders import (
    build_master_dataset,
    load_mta_ridership,
    aggregate_mta_weekly,
    load_tlc_summary,
    load_traffic_counts,
    aggregate_daily_volume,
    CHARGE_START,
)
from model import (
    add_features,
    build_clean_dataset,
    compute_counterfactual,
    decompose_volume_change,
    did_estimate,
    run_tournament,
    train_volume_model,
    FEATURE_COLS,
    TARGET_COL,
)


def write_result(row: dict):
    """Append a row to results.tsv."""
    df = pd.DataFrame([row])
    if RESULTS_PATH.exists():
        existing = pd.read_csv(RESULTS_PATH, sep="\t")
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(RESULTS_PATH, sep="\t", index=False)


def run_baseline():
    """Phase 0.5: baseline evaluation."""
    print("=" * 60)
    print("Phase 0.5: Baseline (ExtraTrees on weekly borough volume)")
    print("=" * 60)
    df = build_clean_dataset()
    print(f"  Clean dataset: {len(df)} rows, {df.shape[1]} columns")
    print(f"  Boroughs: {sorted(df['boro'].unique())}")
    print(f"  Date range: {df['week_start'].min()} to {df['week_start'].max()}")
    print(f"  Pre-charge rows: {(df['post_charge']==0).sum()}")
    print(f"  Post-charge rows: {(df['post_charge']==1).sum()}")

    model, metrics = train_volume_model(df)
    print(f"\n  Baseline metrics (5-fold CV):")
    for k, v in metrics.items():
        print(f"    {k}: {v:.4f}")

    write_result({"experiment": "E00_baseline", "model": "ExtraTrees",
                   **metrics, "n_rows": len(df)})

    # Feature importance
    feats = [c for c in FEATURE_COLS if c in df.columns]
    X = df[feats]
    importances = dict(zip(X.columns, model.feature_importances_))
    print("\n  Feature importance (top 10):")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1])[:10]:
        print(f"    {feat}: {imp:.4f}")

    return model, metrics


def run_tournament_phase():
    """Phase 1: model family tournament."""
    print("\n" + "=" * 60)
    print("Phase 1: Model Tournament")
    print("=" * 60)
    df = build_clean_dataset()
    results = run_tournament(df)
    print("\n  Tournament results:")
    print(results.to_string(index=False))

    for _, row in results.iterrows():
        write_result({"experiment": f"T01_{row['model']}", **row.to_dict(),
                       "n_rows": len(df)})

    winner = results.iloc[0]
    print(f"\n  Winner: {winner['model']} (MAE={winner['mae']:.2f})")
    return results


def run_decomposition():
    """Decompose volume changes into components."""
    print("\n" + "=" * 60)
    print("Congestion Charge Effect Decomposition")
    print("=" * 60)
    df = build_master_dataset()
    result = decompose_volume_change(df)

    print(f"\n  Manhattan average daily volume:")
    print(f"    Pre-charge:  {result['manhattan_pre_vol']:,.0f}")
    print(f"    Post-charge: {result['manhattan_post_vol']:,.0f}")
    print(f"    Change:      {result['total_change']:.1f}%")
    print(f"\n  Decomposition:")
    print(f"    Mode shift (to transit):    {result['mode_shift']:.1f}%")
    print(f"    Route displacement:         {result['route_displacement']:.1f}%")
    print(f"    Time-of-day shift:          {result['time_shift']:.1f}%")
    print(f"    Trip elimination:           {result['trip_elimination']:.1f}%")
    print(f"\n  Outer borough change: {result['outer_boro_change_pct']:.1f}%")

    return result


def run_did():
    """Difference-in-differences analysis."""
    print("\n" + "=" * 60)
    print("Difference-in-Differences Analysis")
    print("=" * 60)
    df = build_master_dataset()
    result = did_estimate(df)
    print(f"\n  DID coefficient: {result['did_coeff']:.2f}")
    print(f"  p-value: {result['p_value']:.4f}")
    sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else "n.s."
    print(f"  Significance: {sig}")
    return result


def run_counterfactual():
    """Counterfactual analysis: train on pre, predict post."""
    print("\n" + "=" * 60)
    print("Counterfactual Analysis")
    print("=" * 60)
    df = build_clean_dataset()
    cf = compute_counterfactual(df)
    print(f"\n  Post-charge counterfactual (n={len(cf)} borough-weeks):")
    for boro in sorted(cf["boro"].unique()):
        subset = cf[cf["boro"] == boro]
        mean_effect = subset["effect_pct"].mean()
        print(f"    {boro}: avg effect = {mean_effect:+.1f}% "
              f"(actual={subset['actual'].mean():,.0f}, "
              f"counterfactual={subset['predicted_counterfactual'].mean():,.0f})")

    # Overall Manhattan
    man_cf = cf[cf["boro"] == "Manhattan"]
    if len(man_cf) > 0:
        print(f"\n  Manhattan summary:")
        print(f"    Mean actual volume:        {man_cf['actual'].mean():,.0f}")
        print(f"    Mean counterfactual:       {man_cf['predicted_counterfactual'].mean():,.0f}")
        print(f"    Mean effect:               {man_cf['effect'].mean():+,.0f}")
        print(f"    Mean effect (%):           {man_cf['effect_pct'].mean():+.1f}%")

    return cf


def run_tlc_analysis():
    """Analyze TLC trip records for CBD vs outer borough shifts."""
    print("\n" + "=" * 60)
    print("TLC Trip Record Analysis (CBD vs Outer Boroughs)")
    print("=" * 60)
    df = load_tlc_summary()
    print(f"\n  TLC summary ({len(df)} file-period combinations):")

    for period in ["pre", "post"]:
        subset = df[df["period"] == period]
        print(f"\n  {period.upper()}:")
        print(f"    Total trips:     {subset['total_trips'].sum():,.0f}")
        print(f"    CBD pickups:     {subset['cbd_pickups'].sum():,.0f}")
        print(f"    CBD dropoffs:    {subset['cbd_dropoffs'].sum():,.0f}")
        print(f"    Outer pickups:   {subset['outer_pickups'].sum():,.0f}")
        print(f"    Outer dropoffs:  {subset['outer_dropoffs'].sum():,.0f}")
        if subset['total_trips'].sum() > 0:
            cbd_share = subset['cbd_pickups'].sum() / subset['total_trips'].sum() * 100
            print(f"    CBD pickup share: {cbd_share:.1f}%")

    # Compute changes
    pre_t = df[df["period"] == "pre"]
    post_t = df[df["period"] == "post"]
    if len(pre_t) > 0 and len(post_t) > 0:
        cbd_pu_change = (post_t["cbd_pickups"].sum() - pre_t["cbd_pickups"].sum()) / pre_t["cbd_pickups"].sum() * 100
        cbd_do_change = (post_t["cbd_dropoffs"].sum() - pre_t["cbd_dropoffs"].sum()) / pre_t["cbd_dropoffs"].sum() * 100
        outer_pu_change = (post_t["outer_pickups"].sum() - pre_t["outer_pickups"].sum()) / pre_t["outer_pickups"].sum() * 100
        print(f"\n  Changes (pre -> post):")
        print(f"    CBD pickups:   {cbd_pu_change:+.1f}%")
        print(f"    CBD dropoffs:  {cbd_do_change:+.1f}%")
        print(f"    Outer pickups: {outer_pu_change:+.1f}%")

    return df


def run_mta_analysis():
    """Analyze MTA ridership trends around congestion pricing."""
    print("\n" + "=" * 60)
    print("MTA Ridership Analysis")
    print("=" * 60)
    mta = load_mta_ridership()
    mta_weekly = aggregate_mta_weekly(mta)
    mta_weekly["post_charge"] = (mta_weekly["week_start"] >= CHARGE_START).astype(int)

    for period_name, period_val in [("Pre-charge", 0), ("Post-charge", 1)]:
        subset = mta_weekly[mta_weekly["post_charge"] == period_val]
        if len(subset) > 0:
            print(f"\n  {period_name} (n={len(subset)} weeks):")
            for col in ["subway_ridership", "bus_ridership", "bridge_tunnel_traffic",
                        "crz_entries", "cbd_entries"]:
                if col in subset.columns and subset[col].notna().any():
                    print(f"    Avg weekly {col}: {subset[col].mean():,.0f}")

    # CRZ entry trend
    if "crz_entries" in mta_weekly.columns:
        crz = mta_weekly[mta_weekly["crz_entries"].notna()].copy()
        if len(crz) > 0:
            print(f"\n  CRZ Entries trend (n={len(crz)} weeks):")
            # Monthly trend
            crz["month"] = crz["week_start"].dt.to_period("M")
            monthly = crz.groupby("month")["crz_entries"].mean()
            for month, val in monthly.items():
                print(f"    {month}: {val:,.0f} avg daily")

    # Compare Q1 2024 vs Q1 2025
    mta_weekly["week_num"] = mta_weekly["week_start"].dt.isocalendar().week.astype(int)
    mta_weekly["year"] = mta_weekly["week_start"].dt.year
    print("\n  Year-over-year Q1 comparison:")
    for year in [2024, 2025]:
        subset = mta_weekly[(mta_weekly["year"] == year) & (mta_weekly["week_num"] <= 13)]
        if len(subset) > 0:
            print(f"\n  Q1 {year} (n={len(subset)} weeks):")
            for col in ["subway_ridership", "bus_ridership", "bridge_tunnel_traffic"]:
                if col in subset.columns and subset[col].notna().any():
                    val = subset[col].mean()
                    print(f"    Avg weekly {col}: {val:,.0f}")

    return mta_weekly


def run_robustness():
    """Phase 2.5: Robustness checks."""
    print("\n" + "=" * 60)
    print("Phase 2.5: Robustness Checks")
    print("=" * 60)

    df = build_clean_dataset()

    # R01: Different train/test splits (3, 5, 10 folds)
    print("\n  R01: K-fold sensitivity")
    for k in [3, 5, 10]:
        _, metrics = train_volume_model(df, n_splits=k)
        print(f"    {k}-fold: MAE={metrics['mae']:.2f}, R2={metrics['r2']:.4f}")
        write_result({"experiment": f"R01_{k}fold", **metrics})

    # R02: Different random seeds
    print("\n  R02: Random seed sensitivity")
    maes = []
    for seed in [42, 123, 456, 789, 2024]:
        _, metrics = train_volume_model(df, seed=seed)
        maes.append(metrics["mae"])
    print(f"    MAE range: [{min(maes):.2f}, {max(maes):.2f}], "
          f"mean={np.mean(maes):.2f}, std={np.std(maes):.2f}")
    write_result({"experiment": "R02_seed_sensitivity",
                   "mae": np.mean(maes), "mae_std": np.std(maes)})

    # R03: Pre-charge only model
    print("\n  R03: Pre-charge only evaluation")
    pre = df[df["post_charge"] == 0]
    if len(pre) > 20:
        _, pre_metrics = train_volume_model(pre)
        print(f"    Pre-only MAE={pre_metrics['mae']:.2f}, R2={pre_metrics['r2']:.4f}")
        write_result({"experiment": "R03_pre_only", **pre_metrics})

    # R04: Temporal CV (train on early, test on late)
    print("\n  R04: Temporal cross-validation")
    df_sorted = df.sort_values("week_start")
    split_point = int(len(df_sorted) * 0.7)
    train = df_sorted.iloc[:split_point]
    test = df_sorted.iloc[split_point:]
    from sklearn.ensemble import ExtraTreesRegressor
    feats = [c for c in FEATURE_COLS if c in df.columns]
    m = ExtraTreesRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    X_tr, y_tr = train[feats], train[TARGET_COL]
    X_te, y_te = test[feats], test[TARGET_COL]
    # Fill NaN
    X_tr = X_tr.fillna(X_tr.median())
    X_te = X_te.fillna(X_te.median())
    m.fit(X_tr, y_tr)
    preds = m.predict(X_te)
    from sklearn.metrics import mean_absolute_error, r2_score
    temp_mae = mean_absolute_error(y_te, preds)
    temp_r2 = r2_score(y_te, preds)
    print(f"    Temporal CV: MAE={temp_mae:.2f}, R2={temp_r2:.4f}")
    write_result({"experiment": "R04_temporal_cv", "mae": temp_mae, "r2": temp_r2})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", default="all")
    args = parser.parse_args()

    t0 = time.time()

    if args.phase == "all" and RESULTS_PATH.exists():
        RESULTS_PATH.unlink()

    phases = {
        "baseline": run_baseline,
        "tournament": run_tournament_phase,
        "decomposition": run_decomposition,
        "did": run_did,
        "counterfactual": run_counterfactual,
        "tlc": run_tlc_analysis,
        "mta": run_mta_analysis,
        "robustness": run_robustness,
    }

    if args.phase == "all":
        all_results = {}
        for name, func in phases.items():
            all_results[name] = func()
        # Save decomposition
        if "decomposition" in all_results:
            decomp_path = HERE / "data" / "decomposition_results.json"
            with open(decomp_path, "w") as f:
                json.dump(all_results["decomposition"], f, indent=2, default=str)
    else:
        phases[args.phase]()

    print(f"\n{'='*60}")
    print(f"  Total wall time: {time.time()-t0:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
