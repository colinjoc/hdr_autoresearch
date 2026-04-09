"""
Paint formulation evaluation harness.

Phase A: predict paint properties (5-fold cross-validation on the Zenodo
         lacquer dataset) for all four targets.
Phase B: discover optimal paint formulations (multi-objective: scratch
         hardness, gloss, hiding power, predicted Volatile Organic Compound
         (VOC) emission, cost).

DO NOT MODIFY THIS FILE.
The autoresearch agent only modifies model.py.

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
from typing import Callable, Dict

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import KFold

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "paint.csv"
RESULTS_DIR = PROJECT_ROOT / "discoveries"
N_FOLDS = 5
RANDOM_SEED = 42


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} missing. Run `python prepare_data.py` first."
        )
    return pd.read_csv(DATA_PATH)


# ---------------------------------------------------------------------------
# Phase A: per-target 5-fold cross-validation
# ---------------------------------------------------------------------------

def cross_validate(
    model_factory: Callable,
    df: pd.DataFrame,
    target: str,
    n_folds: int = N_FOLDS,
    seed: int = RANDOM_SEED,
) -> Dict[str, float]:
    """5-fold KFold CV for a single target. `model_factory` returns a new,
    untrained PaintFormulationModel instance per fold."""
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    y_true_all, y_pred_all = [], []
    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(df)):
        model = model_factory()
        X_tr, y_tr = model.featurize(df.iloc[train_idx])
        X_te, y_te = model.featurize(df.iloc[test_idx])
        model.train(X_tr, y_tr)
        y_pred = model.predict(X_te)
        y_true_all.extend(y_te.tolist())
        y_pred_all.extend(y_pred.tolist())
    y_true = np.array(y_true_all)
    y_pred = np.array(y_pred_all)
    return {
        "target": target,
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
        "n": int(len(y_true)),
    }


def cross_validate_all_targets(df: pd.DataFrame) -> pd.DataFrame:
    from model import PaintFormulationModel, TARGET_COLS
    rows = []
    for target in TARGET_COLS:
        metrics = cross_validate(
            lambda t=target: PaintFormulationModel(target=t),
            df, target=target,
        )
        rows.append(metrics)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Phase B: discovery
# ---------------------------------------------------------------------------

def run_discovery():
    """Delegate to phase_b_discovery.py — keeps evaluate.py thin."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "phase_b_discovery.py")],
        check=True,
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predict", action="store_true")
    parser.add_argument("--discover", action="store_true")
    args = parser.parse_args()
    run_predict = not args.discover or args.predict
    run_discover = not args.predict or args.discover

    start = time.time()
    df = load_dataset()
    print(f"Dataset: {len(df)} paint samples, "
          f"composition from Zenodo DOI 10.5281/zenodo.13742098\n")

    if run_predict:
        print("=" * 60)
        print("PHASE A: 5-fold Cross-Validation across all targets")
        print("=" * 60)
        results = cross_validate_all_targets(df)
        print(results.to_string(index=False))
        mean_mae = results["mae"].mean()
        print(f"\n  mean MAE across targets: {mean_mae:.4f}")
        print(f"  mean R²:                  {results['r2'].mean():.4f}")

    if run_discover:
        print("\n" + "=" * 60)
        print("PHASE B: Multi-objective candidate discovery")
        print("=" * 60)
        run_discovery()

    print(f"\nTotal elapsed: {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
    sys.exit(0)
