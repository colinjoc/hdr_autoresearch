"""
Evaluation harness for [YOUR SCIENTIFIC QUESTION].

Trains a model on per-sample features and evaluates across all benchmark tasks.
This file is NOT modified during HDR experiments -- only strategy.py changes.

Usage:
    python evaluate.py                         # Run all benchmark tasks
    python evaluate.py --task "task_name"       # Run one specific task
    python evaluate.py --quick                  # Run fastest task only

Adapt this template:
1. Define your BENCHMARK_TASKS (data splits, evaluation conditions)
2. Implement get_train_test_split() for your splitting logic
3. Implement evaluate_predictions() for your metrics
4. Adjust samples_to_tabular() if your data is not time-series
"""

import argparse
import pickle
import time
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
    accuracy_score, mean_squared_error, r2_score, fbeta_score,
)

from strategy import build_features, get_xgb_params

DATA_DIR = Path(__file__).parent / "data"
PICKLE_FILE = DATA_DIR / "dataset.pickle"


# ============================================================================
# CONFIGURE: Benchmark tasks
# ============================================================================

# Define all evaluation tasks. Each task specifies a train/test splitting
# strategy. Evaluate on ALL tasks every experiment (no cherry-picking).
#
# Example for cross-domain prediction:
# BENCHMARK_TASKS = [
#     {"split": "zero_shot", "target_group": "group_a", "label": "Group A zero-shot"},
#     {"split": "few_shot",  "target_group": "group_a", "label": "Group A few-shot"},
#     {"split": "many_shot", "target_group": "group_a", "label": "Group A many-shot"},
#     {"split": "zero_shot", "target_group": "group_b", "label": "Group B zero-shot"},
#     ...
# ]
#
# Example for simple train/test:
# BENCHMARK_TASKS = [
#     {"split": "standard", "label": "Main evaluation"},
# ]

BENCHMARK_TASKS = [
    # Define your tasks here
]

# For time-series classification: how many timesteps before the event
# are labeled positive, per group. Set to None for non-time-series data.
# LABEL_WINDOWS = {"group_a": 10, "group_b": 75, "group_c": 200}
LABEL_WINDOWS = None


# ============================================================================
# DATA LOADING
# ============================================================================

def load_dataset():
    """Load the preprocessed dataset."""
    print("Loading dataset...")
    with open(PICKLE_FILE, "rb") as f:
        dataset = pickle.load(f)
    print(f"  {len(dataset)} samples loaded")
    return dataset


# ============================================================================
# TRAIN/TEST SPLITTING: Adapt to your evaluation protocol
# ============================================================================

def get_train_test_split(dataset, task, seed=42, test_fraction=0.15):
    """Split dataset into train and test indices for a given task.

    Args:
        dataset: dict of {idx: {'data': array, 'label': int, 'group': str}}
        task: one entry from BENCHMARK_TASKS
        seed: random seed for reproducibility
        test_fraction: fraction of target group to hold out for testing

    Returns:
        (train_indices, test_indices) as lists
    """
    import random
    import math

    rand = random.Random(seed)
    split_type = task.get("split", "standard")
    target_group = task.get("target_group", None)

    all_keys = set(dataset.keys())

    if split_type == "standard":
        # Simple random split
        keys = list(all_keys)
        rand.shuffle(keys)
        n_test = math.ceil(test_fraction * len(keys))
        return keys[n_test:], keys[:n_test]

    # Cross-domain splits
    target = {k for k in all_keys if dataset[k]["group"] == target_group}
    source = all_keys - target
    positive = {k for k in all_keys if dataset[k]["label"] == 1}
    negative = all_keys - positive

    # Test set: fraction of target group
    target_list = list(target)
    rand.shuffle(target_list)
    n_test = math.ceil(test_fraction * len(target_list))
    test_inds = set(target_list[:n_test])

    # Remove test from available pools
    target -= test_inds
    source -= test_inds

    if split_type == "zero_shot":
        # Train on source groups only (no target data)
        train_inds = source
    elif split_type == "few_shot":
        # Train on source + limited target positives
        n_few = task.get("n_few", 20)
        target_pos = list(target & positive)
        rand.shuffle(target_pos)
        few = set(target_pos[:n_few])
        train_inds = source | (target & negative) | few
    elif split_type == "many_shot":
        # Train on all available data
        train_inds = source | target
    else:
        raise ValueError(f"Unknown split type: {split_type}")

    return list(train_inds), list(test_inds)


# ============================================================================
# FEATURE CONVERSION: Adapt for your data structure
# ============================================================================

def samples_to_tabular(dataset, indices, include_group_indicators=True):
    """Convert samples into flat tabular format for XGBoost.

    For TIME-SERIES data: each timestep becomes one row. Labels are assigned
    based on LABEL_WINDOWS (positive = within N timesteps of event).

    For TABULAR data: each sample is one row.

    Returns X (features), y (labels), and sample_metadata.
    """
    all_X = []
    all_y = []
    sample_meta = []

    for idx in indices:
        sample = dataset[idx]
        data = sample["data"]
        label = sample["label"]
        group = sample["group"]

        features = build_features(data, group, include_group_indicators)

        if data.ndim > 1 and LABEL_WINDOWS is not None:
            # Time-series: per-timestep labeling
            n_steps = len(data)
            window = LABEL_WINDOWS.get(group, 0)
            if label == 1 and window > 0:
                y_sample = np.zeros(n_steps, dtype=np.int32)
                y_sample[max(0, n_steps - window):] = 1
            else:
                y_sample = np.zeros(n_steps, dtype=np.int32)
            all_y.append(y_sample)
        else:
            # Tabular: one label per sample
            all_y.append(np.array([label], dtype=np.int32))

        all_X.append(features)
        sample_meta.append({
            "idx": idx,
            "group": group,
            "label": label,
            "n_timesteps": len(data) if data.ndim > 1 else 1,
        })

    X = np.vstack(all_X)
    y = np.concatenate(all_y)

    return X, y, sample_meta


# ============================================================================
# PREDICTION: Generate per-sample predictions
# ============================================================================

def predict_samples(model, scaler, dataset, test_indices,
                    include_group_indicators=True):
    """Generate predictions for test samples.

    Returns a dict of predictions suitable for your evaluation function.
    """
    predictions = {}

    for idx in test_indices:
        sample = dataset[idx]
        data = sample["data"]
        group = sample["group"]
        label = sample["label"]

        features = build_features(data, group, include_group_indicators)
        features_scaled = scaler.transform(features)
        dmat = xgb.DMatrix(features_scaled)
        proba = model.predict(dmat)

        sample_key = f"{group}_{idx}"
        predictions[sample_key] = {
            "proba": proba,
            "label": label,
            "group": group,
        }

        # For time-series: add timing information
        if data.ndim > 1:
            n_steps = len(data)
            # Adjust dt to your sampling rate
            dt = 1.0  # seconds per timestep
            predictions[sample_key]["time"] = np.arange(n_steps) * dt

    return predictions


# ============================================================================
# EVALUATION: Compute metrics from predictions
# ============================================================================

def evaluate_predictions(predictions):
    """Compute evaluation metrics from predictions.

    Adapt this to your specific metrics. For sample-level binary classification:
    aggregate per-timestep predictions to per-sample, then compute metrics.
    """
    all_labels = []
    all_probas = []

    for key, pred in predictions.items():
        label = pred["label"]
        proba = pred["proba"]

        # For time-series: aggregate to sample-level (max probability)
        sample_proba = float(np.max(proba))
        all_labels.append(label)
        all_probas.append(sample_proba)

    y_true = np.array(all_labels)
    y_score = np.array(all_probas)
    y_pred = (y_score >= 0.5).astype(int)

    results = {}
    try:
        results["auc"] = roc_auc_score(y_true, y_score)
    except ValueError:
        results["auc"] = float("nan")

    results["f2"] = fbeta_score(y_true, y_pred, beta=2, zero_division=0)
    results["f1"] = f1_score(y_true, y_pred, zero_division=0)
    results["precision"] = precision_score(y_true, y_pred, zero_division=0)
    results["recall"] = recall_score(y_true, y_pred, zero_division=0)
    results["accuracy"] = accuracy_score(y_true, y_pred)

    return results


# ============================================================================
# TASK RUNNER
# ============================================================================

def run_task(dataset, task):
    """Run a single benchmark task: split, train, predict, evaluate."""
    task_label = task["label"]
    print(f"\n{'=' * 60}")
    print(f"Task: {task_label}")
    print(f"{'=' * 60}")

    t0 = time.time()

    # Split
    train_inds, test_inds = get_train_test_split(dataset, task)
    print(f"  Train: {len(train_inds)} samples, Test: {len(test_inds)} samples")

    # Build tabular features
    print("  Building features...")
    X_train, y_train, train_meta = samples_to_tabular(dataset, train_inds)
    print(f"  Train: {X_train.shape[0]} rows, {X_train.shape[1]} features, "
          f"{y_train.sum()} positive ({100 * y_train.mean():.1f}%)")

    # Scale
    scaler = RobustScaler()
    X_train = scaler.fit_transform(X_train)

    # Train XGBoost
    print("  Training XGBoost...")
    params = get_xgb_params()
    num_rounds = params.pop("num_boost_round", 200)
    dtrain = xgb.DMatrix(X_train, label=y_train)
    model = xgb.train(params, dtrain, num_boost_round=num_rounds)

    train_time = time.time() - t0
    print(f"  Training complete ({train_time:.1f}s)")

    # Predict
    print("  Generating predictions...")
    predictions = predict_samples(model, scaler, dataset, test_inds)

    # Evaluate
    print("  Evaluating...")
    results = evaluate_predictions(predictions)

    # Print results
    print(f"\n  Results:")
    for metric, value in results.items():
        print(f"    {metric:>15}: {value:.4f}")

    return {
        "task": task_label,
        **results,
        "train_samples": len(train_inds),
        "test_samples": len(test_inds),
        "train_time": train_time,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="HDR Evaluation Harness")
    parser.add_argument("--task", type=str, help="Run a specific task by label")
    parser.add_argument("--quick", action="store_true",
                        help="Run only the first task (fastest)")
    args = parser.parse_args()

    dataset = load_dataset()

    if args.quick:
        tasks = BENCHMARK_TASKS[:1]
    elif args.task:
        tasks = [t for t in BENCHMARK_TASKS if t["label"] == args.task]
        if not tasks:
            print(f"Task '{args.task}' not found. Available:")
            for t in BENCHMARK_TASKS:
                print(f"  - {t['label']}")
            sys.exit(1)
    else:
        tasks = BENCHMARK_TASKS

    all_results = []
    for task in tasks:
        result = run_task(dataset, task)
        all_results.append(result)

    # Summary table
    if all_results:
        metric_names = [k for k in all_results[0] if k not in
                        ("task", "train_samples", "test_samples", "train_time")]

        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        header = f"{'Task':<30}" + "".join(f"{m:>10}" for m in metric_names)
        print(header)
        print("-" * 80)
        for r in all_results:
            row = f"{r['task']:<30}"
            for m in metric_names:
                row += f"{r[m]:>10.4f}"
            print(row)

        if len(all_results) > 1:
            print("-" * 80)
            means = f"{'MEAN':<30}"
            for m in metric_names:
                mean_val = np.mean([r[m] for r in all_results
                                    if not np.isnan(r[m])])
                means += f"{mean_val:>10.4f}"
            print(means)

    # Save to results.tsv
    results_file = Path(__file__).parent / "results.tsv"
    header_needed = not results_file.exists()
    with open(results_file, "a") as f:
        if header_needed:
            cols = list(all_results[0].keys()) if all_results else []
            f.write("\t".join(cols) + "\n")
        for r in all_results:
            vals = [f"{v:.4f}" if isinstance(v, float) else str(v)
                    for v in r.values()]
            f.write("\t".join(vals) + "\n")

    print(f"\nResults appended to {results_file}")


if __name__ == "__main__":
    main()
