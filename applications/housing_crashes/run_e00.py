"""E00 baseline for housing-crash prediction.

Simple logistic regression with ecosystem-minimal SAFE feature set; temporal
split: train 2016-08 → 2022-06, test 2022-07 → 2023-12 (the Austin/Boise/
Phoenix crash era is the out-of-sample test).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import Result, append_result, classifier_metrics  # noqa: E402


SAFE_FEATURES = [
    "zhvi_3mo_ret", "zhvi_6mo_ret", "zhvi_12mo_ret", "zhvi_24mo_ret",
    "mortgage_30yr", "mortgage_30yr_delta_12mo",
    "log1p_active_listing_count", "log1p_new_listing_count",
    "median_days_on_market", "price_reduced_share",
]

TRAIN_END = pd.Timestamp("2022-06-01")


def main():
    panel = pd.read_parquet(HERE / "data" / "panel.parquet")
    panel["month"] = pd.to_datetime(panel["month"])

    feats = [f for f in SAFE_FEATURES if f in panel.columns]
    print(f"features ({len(feats)}): {feats}", flush=True)

    # Drop rows missing any feature
    usable = panel.dropna(subset=feats + ["crash_next_12mo"]).copy()
    print(f"usable: {len(usable):,} / {len(panel):,} rows  "
          f"crash rate {usable['crash_next_12mo'].mean():.3%}", flush=True)

    train = usable[usable["month"] <= TRAIN_END]
    test = usable[usable["month"] > TRAIN_END]
    print(f"train: {len(train):,} rows, {train['crash_next_12mo'].sum()} crashes "
          f"({train['crash_next_12mo'].mean():.3%})", flush=True)
    print(f"test : {len(test):,} rows, {test['crash_next_12mo'].sum()} crashes "
          f"({test['crash_next_12mo'].mean():.3%})", flush=True)

    X_tr = train[feats].values
    y_tr = train["crash_next_12mo"].values
    X_te = test[feats].values
    y_te = test["crash_next_12mo"].values

    scaler = StandardScaler().fit(X_tr)
    X_tr_s = scaler.transform(X_tr)
    X_te_s = scaler.transform(X_te)

    # Handle heavy class imbalance: class_weight='balanced' up-weights positives
    clf = LogisticRegression(max_iter=5000, solver="liblinear",
                              class_weight="balanced", C=1.0)
    clf.fit(X_tr_s, y_tr)
    prob_te = clf.predict_proba(X_te_s)[:, 1]

    m = classifier_metrics(y_te, prob_te, k_frac=0.05)
    print(f"\nE00 test-set performance:", flush=True)
    print(f"  n_test={len(y_te):,}  base_rate={m['base_rate']:.3%}", flush=True)
    print(f"  PR-AUC = {m['pr_auc']:.4f}  "
          f"(lift over random = {m['pr_auc_lift_over_base']:.2f}×)", flush=True)
    print(f"  ROC-AUC = {m['roc_auc']:.4f}", flush=True)
    print(f"  Brier  = {m['brier']:.4f}", flush=True)
    print(f"  top-5% precision = {m['top_k_precision']:.4f}  (k={m['top_k_k']})", flush=True)

    # Feature coefficients (after standardization: comparable across features)
    coefs = dict(zip(feats, clf.coef_[0]))
    print("\nstandardized coefficients (|β|):", flush=True)
    for f, c in sorted(coefs.items(), key=lambda x: -abs(x[1])):
        print(f"  {f:40s} {c:+.4f}", flush=True)

    append_result(Result(
        exp_id="E00",
        description="Logistic (balanced) w/ SAFE features; train ≤2022-06, test >2022-06",
        n_train=len(train), n_test=len(test),
        pos_rate_train=float(y_tr.mean()), pos_rate_test=float(y_te.mean()),
        roc_auc=m["roc_auc"], pr_auc=m["pr_auc"],
        pr_auc_lift_over_base=m["pr_auc_lift_over_base"],
        brier=m["brier"], log_loss=m["log_loss"],
        top_k_precision=m["top_k_precision"], top_k_k=m["top_k_k"],
        status="BASELINE",
    ))


if __name__ == "__main__":
    main()
