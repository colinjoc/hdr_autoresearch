"""
Evaluation harness for solar flare prediction.

DO NOT MODIFY THIS FILE — it is fixed infrastructure.
The autoresearch agent only modifies strategy.py.

Usage:
    python prepare.py
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss

DATA_DIR = Path(__file__).parent / "data"


def true_skill_statistic(y_true, y_prob, n_thresholds=200):
    """Compute max TSS over a range of probability thresholds."""
    thresholds = np.linspace(0, 1, n_thresholds)
    best_tss = -1
    best_thresh = 0.5
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        tp = ((y_pred == 1) & (y_true == 1)).sum()
        fn = ((y_pred == 0) & (y_true == 1)).sum()
        fp = ((y_pred == 1) & (y_true == 0)).sum()
        tn = ((y_pred == 0) & (y_true == 0)).sum()
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        tss = tpr - fpr
        if tss > best_tss:
            best_tss = tss
            best_thresh = t
    return best_tss, best_thresh


def brier_skill_score(y_true, y_prob):
    """Compute BSS relative to climatological forecast."""
    bs = brier_score_loss(y_true, y_prob)
    clim_rate = y_true.mean()
    bs_clim = brier_score_loss(y_true, np.full_like(y_prob, clim_rate))
    if bs_clim == 0:
        return 0.0
    return 1 - bs / bs_clim


def load_data():
    """Load and split dataset into train and test."""
    df = pd.read_csv(DATA_DIR / "AR_flare_ml_23_24.csv")
    df["date"] = pd.to_datetime(df["AR issue_date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Binary target: C+ flare (>= C class) in next 24 hours
    df["target"] = (df["C+"] > 0).astype(int)

    # Chronological 80/20 split
    split_idx = int(len(df) * 0.8)
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()

    return train, test


def main():
    from strategy import featurize, get_model

    print("Loading data...")
    train, test = load_data()
    print(f"  Train: {len(train)} samples ({train['date'].min().date()} to {train['date'].max().date()})")
    print(f"  Test:  {len(test)} samples ({test['date'].min().date()} to {test['date'].max().date()})")
    print(f"  Train flare rate: {train['target'].mean():.3%}")
    print(f"  Test flare rate:  {test['target'].mean():.3%}")
    print()

    t0 = time.time()

    # Featurize
    print("Featurizing...")
    X_train = featurize(train)
    X_test = featurize(test)
    y_train = train["target"].values
    y_test = test["target"].values

    # Train
    print("Training...")
    model = get_model()
    model.fit(X_train, y_train)

    # Predict probabilities
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        y_prob = model.predict(X_test)

    elapsed = time.time() - t0

    # Metrics
    tss, thresh = true_skill_statistic(y_test, y_prob)
    bss = brier_skill_score(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    print()
    print("=" * 60)
    print(f"RESULTS — Solar Flare C+ Prediction")
    print("=" * 60)
    print(f"  TSS:             {tss:.4f} (at threshold {thresh:.2f})")
    print(f"  BSS:             {bss:.4f}")
    print(f"  AUC-ROC:         {auc:.4f}")
    print(f"  Elapsed Time:    {elapsed:.1f}s")
    print("=" * 60)

    return {"tss": tss, "bss": bss, "auc": auc, "threshold": thresh}


if __name__ == "__main__":
    main()
