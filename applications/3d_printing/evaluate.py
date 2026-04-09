"""Evaluation harness for the Fused Deposition Modelling (FDM) project.

Phase A: Predict ultimate tensile strength (UTS, megapascals) on the
         Kaggle 3D Printer Dataset via 5-fold cross-validation.
Phase B: Generate and score candidate parameter vectors on three
         objectives: predicted tensile strength, a print-time proxy,
         and an energy-consumption proxy.

DO NOT MODIFY THIS FILE during the Hypothesis-Driven Research (HDR) loop.
The only file the HDR agent modifies is model.py.

Usage:
    python evaluate.py              # Both phases
    python evaluate.py --predict    # Phase A only
    python evaluate.py --discover   # Phase B only
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

DATA_PATH = Path(__file__).parent / "data" / "3d_printing.csv"
RESULTS_DIR = Path(__file__).parent / "discoveries"
N_FOLDS = 5
RANDOM_SEED = 42


def load_dataset() -> pd.DataFrame:
    """Load the semicolon-separated Kaggle 3D Printer Dataset."""
    return pd.read_csv(DATA_PATH, sep=";")


# -----------------------------------------------------------------------------
# Phase A: 5-fold cross-validation
# -----------------------------------------------------------------------------


def cross_validate(model_class, df: pd.DataFrame) -> dict:
    """Run 5-fold KFold cross-validation using the HDR-owned model_class.

    The model class must expose three methods: featurize(df) -> (X, y),
    train(X, y), and predict(X). This keeps the harness agnostic to the
    concrete model family chosen during the HDR loop.
    """
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
        print(f"  Fold {fold_idx + 1}: MAE = {mae:.3f} MPa, "
              f"R2 = {r2:.4f}")
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


# -----------------------------------------------------------------------------
# Phase B: Discovery on the trained model
# -----------------------------------------------------------------------------


def run_discovery(model_class, df: pd.DataFrame) -> dict | None:
    """Legacy single-file discovery path. The canonical Phase B sweep lives
    in phase_b_discovery.py."""
    model = model_class()
    X_train, y_train = model.featurize(df)
    model.train(X_train, y_train)

    if not hasattr(model, "generate_candidates"):
        print("  model.py has no generate_candidates() -- skipping.")
        return None

    candidates = model.generate_candidates()
    if not candidates:
        return None

    import phase_b_discovery as pb

    rows = []
    for cand in candidates:
        feat = model.featurize_single(cand)
        if feat is None:
            continue
        strength = float(model.predict(feat.reshape(1, -1))[0])
        t_h = pb.print_time_proxy(cand)
        e_kwh = pb.energy_proxy(cand)
        rows.append({
            **cand,
            "predicted_strength": strength,
            "print_time_hours": t_h,
            "energy_kwh": e_kwh,
            "strength_per_hour": strength / t_h if t_h > 0 else 0.0,
        })

    cand_df = pd.DataFrame(rows).sort_values("predicted_strength", ascending=False)
    RESULTS_DIR.mkdir(exist_ok=True)
    cand_df.to_csv(RESULTS_DIR / "candidates.csv", index=False)

    front = pb.pareto_front_strength_time(cand_df)
    front.to_csv(RESULTS_DIR / "pareto_front.csv", index=False)

    return {
        "n_candidates": len(cand_df),
        "n_pareto": len(front),
        "max_strength": float(cand_df["predicted_strength"].max()),
        "min_time": float(cand_df["print_time_hours"].min()),
        "best_eff": float(cand_df["strength_per_hour"].max()),
        "candidates_df": cand_df,
        "pareto_df": front,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predict", action="store_true")
    parser.add_argument("--discover", action="store_true")
    args = parser.parse_args()
    run_predict = not args.discover or args.predict
    run_discover = not args.predict or args.discover

    start = time.time()
    df = load_dataset()
    print(f"Dataset: {len(df)} samples, tensile strength range "
          f"{df['tension_strength'].min():.1f} - "
          f"{df['tension_strength'].max():.1f} MPa\n")

    from model import PrinterModel

    pred = None
    if run_predict:
        print("=" * 56)
        print("PHASE A: Tensile Strength Prediction (5-fold CV)")
        print("=" * 56)
        pred = cross_validate(PrinterModel, df)
        print(f"\n  MAE : {pred['mae']:.3f} MPa")
        print(f"  RMSE: {pred['rmse']:.3f} MPa")
        print(f"  R2  : {pred['r2']:.4f}\n")

    disc = None
    if run_discover:
        print("=" * 56)
        print("PHASE B: FDM Parameter Discovery")
        print("=" * 56)
        disc = run_discovery(PrinterModel, df)
        if disc:
            print(f"\n  Candidates  : {disc['n_candidates']}")
            print(f"  Pareto front: {disc['n_pareto']} designs")
            print(f"  Max strength: {disc['max_strength']:.1f} MPa")
            print(f"  Min time    : {disc['min_time']:.2f} hours")
            print(f"  Best strength/hour: {disc['best_eff']:.2f}")
            print("\n  Saved: discoveries/candidates.csv, "
                  "discoveries/pareto_front.csv")

    elapsed = time.time() - start
    print(f"\n{'=' * 56}")
    print("SUMMARY")
    print(f"{'=' * 56}")
    if pred:
        print(f"  Predictor: MAE = {pred['mae']:.3f} MPa, "
              f"R2 = {pred['r2']:.4f}")
    if disc:
        print(f"  Discovery: {disc['n_pareto']} Pareto designs, "
              f"max strength {disc['max_strength']:.1f} MPa")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"{'=' * 56}")


if __name__ == "__main__":
    main()
    sys.exit(0)
