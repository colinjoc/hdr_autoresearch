"""
Welding parameter-to-quality evaluation harness.

Phase A: Predict Heat-Affected Zone (HAZ) half-width from welding parameters.
    5-fold cross-validation on the steel subset of data/welding.csv.
Phase B: Discover parameter combinations on the strength/HAZ Pareto front
    via `phase_b_discovery.py`.

DO NOT MODIFY THIS FILE.
The autoresearch agent only modifies `model.py`.

Usage:
    python evaluate.py              # Phase A only
    python evaluate.py --discover   # Phase A + Phase B
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

DATA_PATH = Path(__file__).parent / "data" / "welding.csv"
RESULTS_DIR = Path(__file__).parent / "discoveries"
N_FOLDS = 5
RANDOM_SEED = 42

# Keep only the steel arc-welding subset for the primary regression
# (FSW is held out as an out-of-family sanity check in hdr_phase25.py).
STEEL_PROCESSES = ("GMAW", "GTAW")


def load_dataset(include_fsw: bool = False) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    if not include_fsw:
        df = df[df["process"].isin(STEEL_PROCESSES)].reset_index(drop=True)
    return df


def cross_validate(model_class, df: pd.DataFrame):
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
        print(f"  fold {fold_idx+1}: MAE={mae:.3f} mm  R²={r2:.4f}")
        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())
    y_true = np.array(all_y_true)
    y_pred = np.array(all_y_pred)
    return {
        "mae":  float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(math.sqrt(mean_squared_error(y_true, y_pred))),
        "r2":   float(r2_score(y_true, y_pred)),
        "n":    int(len(df)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true")
    args = parser.parse_args()

    start = time.time()
    df = load_dataset()
    print(f"dataset: {len(df)} arc-welding rows; HAZ range "
          f"{df['haz_width_mm'].min():.2f}–{df['haz_width_mm'].max():.2f} mm\n")

    from model import WeldingModel
    print("=" * 60)
    print("PHASE A: HAZ half-width prediction (5-fold CV)")
    print("=" * 60)
    pred = cross_validate(WeldingModel, df)
    print(f"\n  MAE:  {pred['mae']:.3f} mm")
    print(f"  RMSE: {pred['rmse']:.3f} mm")
    print(f"  R²:   {pred['r2']:.4f}")

    if args.discover:
        print("\n" + "=" * 60)
        print("PHASE B: discovery (delegated to phase_b_discovery.py)")
        print("=" * 60)
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / "phase_b_discovery.py")])

    elapsed = time.time() - start
    print(f"\nelapsed: {elapsed:.1f} s")


if __name__ == "__main__":
    main()
