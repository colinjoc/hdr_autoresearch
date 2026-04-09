"""
Concrete mix design evaluation harness.

Phase A: Predict compressive strength (5-fold CV on UCI dataset)
Phase B: Discover optimal mix designs (multi-objective: strength, cost, CO2)

DO NOT MODIFY THIS FILE.
The autoresearch agent only modifies model.py.

Usage:
    python evaluate.py              # Both phases
    python evaluate.py --predict    # Phase A only
    python evaluate.py --discover   # Phase B only
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

DATA_PATH = Path(__file__).parent / "data" / "concrete.csv"
RESULTS_DIR = Path(__file__).parent / "discoveries"
N_FOLDS = 5
RANDOM_SEED = 42

# Short column names
COL_MAP = {
    "Cement (component 1)(kg in a m^3 mixture)": "cement",
    "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": "slag",
    "Fly Ash (component 3)(kg in a m^3 mixture)": "fly_ash",
    "Water  (component 4)(kg in a m^3 mixture)": "water",
    "Superplasticizer (component 5)(kg in a m^3 mixture)": "superplasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": "coarse_agg",
    "Fine Aggregate (component 7)(kg in a m^3 mixture)": "fine_agg",
    "Age (day)": "age",
    "Concrete compressive strength(MPa. megapascals)": "strength",
}

# CO2 emissions (kg CO2e per kg of ingredient)
CO2_PER_KG = {
    "cement": 0.90, "slag": 0.07, "fly_ash": 0.01,
    "water": 0.001, "superplasticizer": 1.50,
    "coarse_agg": 0.005, "fine_agg": 0.005,
}

# Cost (USD per kg of ingredient)
COST_PER_KG = {
    "cement": 0.15, "slag": 0.10, "fly_ash": 0.05,
    "water": 0.001, "superplasticizer": 3.00,
    "coarse_agg": 0.015, "fine_agg": 0.012,
}


def load_dataset():
    df = pd.read_csv(DATA_PATH)
    df = df.rename(columns=COL_MAP)
    return df


def compute_mix_co2(mix):
    """CO2 emissions in kg CO2e per m³ of concrete."""
    return sum(mix.get(k, 0) * v for k, v in CO2_PER_KG.items())


def compute_mix_cost(mix):
    """Cost in USD per m³ of concrete."""
    return sum(mix.get(k, 0) * v for k, v in COST_PER_KG.items())


# ── Phase A ──

def cross_validate(model_class, df):
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    all_y_true, all_y_pred = [], []

    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(df)):
        model = model_class()
        X_train, y_train = model.featurize(df.iloc[train_idx])
        X_test, y_test = model.featurize(df.iloc[test_idx])
        model.train(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(f"  Fold {fold_idx+1}: MAE={mae:.2f} MPa, R²={r2:.4f}")
        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())

    y_true = np.array(all_y_true)
    y_pred = np.array(all_y_pred)
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "r2": r2_score(y_true, y_pred),
        "n": len(df),
    }


# ── Phase B ──

def run_discovery(model_class, df):
    model = model_class()
    X_train, y_train = model.featurize(df)
    model.train(X_train, y_train)

    if not hasattr(model, "generate_candidates"):
        print("  model.py has no generate_candidates() — skipping.")
        return None

    candidates = model.generate_candidates()
    if not candidates:
        return None

    results = []
    for cand in candidates:
        feat = model.featurize_single(cand)
        if feat is None:
            continue
        strength = float(model.predict(feat.reshape(1, -1))[0])
        co2 = compute_mix_co2(cand)
        cost = compute_mix_cost(cand)
        # Efficiency: strength per unit CO2
        efficiency = strength / co2 if co2 > 0 else 0
        results.append({**cand, "predicted_strength": strength,
                        "co2_kg_per_m3": co2, "cost_usd_per_m3": cost,
                        "strength_per_co2": efficiency})

    results_df = pd.DataFrame(results).sort_values("predicted_strength", ascending=False)
    RESULTS_DIR.mkdir(exist_ok=True)
    results_df.to_csv(RESULTS_DIR / "candidates.csv", index=False)

    # Pareto front (strength vs CO2)
    pareto = []
    for _, row in results_df.iterrows():
        dominated = False
        for _, other in results_df.iterrows():
            if (other["predicted_strength"] >= row["predicted_strength"] and
                other["co2_kg_per_m3"] <= row["co2_kg_per_m3"] and
                (other["predicted_strength"] > row["predicted_strength"] or
                 other["co2_kg_per_m3"] < row["co2_kg_per_m3"])):
                dominated = True
                break
        if not dominated:
            pareto.append(row)
    pareto_df = pd.DataFrame(pareto)
    if len(pareto_df) > 0:
        pareto_df.to_csv(RESULTS_DIR / "pareto_front.csv", index=False)

    return {
        "n_candidates": len(results_df),
        "n_pareto": len(pareto_df),
        "max_strength": results_df["predicted_strength"].max(),
        "min_co2": results_df["co2_kg_per_m3"].min(),
        "best_efficiency": results_df["strength_per_co2"].max(),
        "candidates_df": results_df,
        "pareto_df": pareto_df,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predict", action="store_true")
    parser.add_argument("--discover", action="store_true")
    args = parser.parse_args()
    run_predict = not args.discover or args.predict
    run_discover = not args.predict or args.discover

    start = time.time()
    df = load_dataset()
    print(f"Dataset: {len(df)} samples, strength range {df['strength'].min():.1f}–{df['strength'].max():.1f} MPa\n")

    from model import ConcreteModel

    pred = None
    if run_predict:
        print("=" * 50)
        print("PHASE A: Strength Prediction (5-fold CV)")
        print("=" * 50)
        pred = cross_validate(ConcreteModel, df)
        print(f"\n  MAE:  {pred['mae']:.2f} MPa")
        print(f"  RMSE: {pred['rmse']:.2f} MPa")
        print(f"  R²:   {pred['r2']:.4f}\n")

    disc = None
    if run_discover:
        print("=" * 50)
        print("PHASE B: Mix Design Discovery")
        print("=" * 50)
        disc = run_discovery(ConcreteModel, df)
        if disc:
            print(f"\n  Candidates: {disc['n_candidates']}")
            print(f"  Pareto front: {disc['n_pareto']} designs")
            print(f"  Max strength: {disc['max_strength']:.1f} MPa")
            print(f"  Min CO₂: {disc['min_co2']:.1f} kg/m³")
            print(f"  Best efficiency: {disc['best_efficiency']:.2f} MPa/(kg CO₂)")
            if disc.get("pareto_df") is not None and len(disc["pareto_df"]) > 0:
                print("\n  Pareto front (strength vs CO₂):")
                for _, r in disc["pareto_df"].head(10).iterrows():
                    print(f"    {r['predicted_strength']:5.1f} MPa | {r['co2_kg_per_m3']:5.1f} kg CO₂ | "
                          f"${r['cost_usd_per_m3']:.1f}/m³ | eff={r['strength_per_co2']:.2f}")
            print(f"\n  Saved: discoveries/candidates.csv, discoveries/pareto_front.csv")

    elapsed = time.time() - start
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    if pred:
        print(f"  Predictor: MAE={pred['mae']:.2f} MPa, R²={pred['r2']:.4f}")
    if disc:
        print(f"  Discovery: {disc['n_pareto']} Pareto designs, best eff={disc['best_efficiency']:.2f}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
    sys.exit(0)
