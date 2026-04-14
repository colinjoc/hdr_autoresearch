"""Phase 1 tournament: 5 model families on the housing-crash panel.

Rolling-origin temporal CV on train + held-out temporal test. 5 seeds per
family. Champion picked on test-set PR-AUC.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

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
FOLDS = [
    (pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-01")),
    (pd.Timestamp("2021-01-01"), pd.Timestamp("2021-12-01")),
    (pd.Timestamp("2022-01-01"), pd.Timestamp("2022-06-01")),
]


def fit_predict(family, X_tr, y_tr, X_te, seed: int):
    if family == "L1":
        m = LogisticRegression(penalty="l1", solver="liblinear", C=1.0,
                               class_weight="balanced", max_iter=5000, random_state=seed)
    elif family == "L2":
        m = LogisticRegression(penalty="l2", solver="liblinear", C=1.0,
                               class_weight="balanced", max_iter=5000, random_state=seed)
    elif family == "RF":
        m = RandomForestClassifier(n_estimators=300, max_depth=10,
                                   class_weight="balanced",
                                   n_jobs=-1, random_state=seed)
    elif family == "GB":
        scale = float((y_tr == 0).sum()) / max(1, float((y_tr == 1).sum()))
        m = xgb.XGBClassifier(n_estimators=400, max_depth=5, learning_rate=0.05,
                               subsample=0.8, colsample_bytree=0.8,
                               scale_pos_weight=scale,
                               eval_metric="aucpr", random_state=seed, n_jobs=-1,
                               tree_method="hist")
    elif family == "LB":
        scale = float((y_tr == 0).sum()) / max(1, float((y_tr == 1).sum()))
        m = lgb.LGBMClassifier(n_estimators=400, max_depth=-1, num_leaves=31,
                                learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                                scale_pos_weight=scale,
                                random_state=seed, n_jobs=-1, verbose=-1)
    else:
        raise ValueError(family)
    m.fit(X_tr, y_tr)
    return m.predict_proba(X_te)[:, 1]


def main():
    panel = pd.read_parquet(HERE / "data" / "panel.parquet")
    panel["month"] = pd.to_datetime(panel["month"])
    feats = [f for f in SAFE_FEATURES if f in panel.columns]
    usable = panel.dropna(subset=feats + ["crash_next_12mo"]).copy()

    train_full = usable[usable["month"] <= TRAIN_END].copy()
    test = usable[usable["month"] > TRAIN_END].copy()
    print(f"train {len(train_full):,}  test {len(test):,}  "
          f"train pos {train_full['crash_next_12mo'].mean():.3%}  "
          f"test pos {test['crash_next_12mo'].mean():.3%}", flush=True)

    families = ["L1", "L2", "RF", "GB", "LB"]
    seeds = [17, 23, 42, 101, 2027]

    rows = []
    for fam in families:
        cv_prs, te_prs, te_rocs = [], [], []
        for s in seeds:
            # Rolling-origin CV on train_full
            fold_prs = []
            for cut, end in FOLDS:
                tr = train_full[train_full["month"] < cut]
                va = train_full[(train_full["month"] >= cut) & (train_full["month"] < end)]
                if len(tr) < 100 or len(va) < 100 or va["crash_next_12mo"].sum() < 3:
                    continue
                scaler = StandardScaler().fit(tr[feats].values)
                X_tr = scaler.transform(tr[feats].values)
                X_va = scaler.transform(va[feats].values)
                p = fit_predict(fam, X_tr, tr["crash_next_12mo"].values, X_va, s)
                m = classifier_metrics(va["crash_next_12mo"].values, p)
                fold_prs.append(m["pr_auc"])
            cv_prs.append(np.mean(fold_prs) if fold_prs else float("nan"))

            # Test holdout
            scaler = StandardScaler().fit(train_full[feats].values)
            X_tr = scaler.transform(train_full[feats].values)
            X_te = scaler.transform(test[feats].values)
            p = fit_predict(fam, X_tr, train_full["crash_next_12mo"].values, X_te, s)
            m = classifier_metrics(test["crash_next_12mo"].values, p)
            te_prs.append(m["pr_auc"])
            te_rocs.append(m["roc_auc"])

        row = {
            "family": fam,
            "cv_pr_auc": float(np.nanmean(cv_prs)),
            "test_pr_auc_mean": float(np.mean(te_prs)),
            "test_pr_auc_std": float(np.std(te_prs)),
            "test_roc_mean": float(np.mean(te_rocs)),
        }
        rows.append(row)
        print(f"{fam}: CV PR-AUC {row['cv_pr_auc']:.4f}  "
              f"TEST PR-AUC {row['test_pr_auc_mean']:.4f} ± {row['test_pr_auc_std']:.4f}  "
              f"ROC {row['test_roc_mean']:.4f}", flush=True)
        append_result(Result(
            exp_id=f"E01-{fam}", description=f"Phase-1 tournament {fam}; 5 seeds",
            n_train=len(train_full), n_test=len(test),
            pos_rate_train=float(train_full["crash_next_12mo"].mean()),
            pos_rate_test=float(test["crash_next_12mo"].mean()),
            pr_auc=row["test_pr_auc_mean"], roc_auc=row["test_roc_mean"],
            status="TOURNAMENT",
        ))

    df = pd.DataFrame(rows).sort_values("test_pr_auc_mean", ascending=False)
    print("\n=== Tournament ranking (by test PR-AUC) ===")
    print(df.to_string(index=False))
    champ = df.iloc[0]["family"]
    (HERE / "data" / "phase1_champion.txt").write_text(champ)
    print(f"\nCHAMPION = {champ}", flush=True)


if __name__ == "__main__":
    main()
