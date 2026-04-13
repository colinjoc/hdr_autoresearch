"""Phase 1 model tournament: XGBoost vs LightGBM vs Logistic vs RandomForest."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from model import FEATURES, bootstrap_ci


def _split(df, features, label_col="label_abandoned", test_frac=0.25, seed=42):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(df))
    n_test = int(len(df) * test_frac)
    tr = df.iloc[idx[n_test:]]
    te = df.iloc[idx[:n_test]]
    return (tr[features].values, tr[label_col].values,
            te[features].values, te[label_col].values)


def eval_scores(y_true, y_pred):
    pr_auc, lo, hi = bootstrap_ci(average_precision_score, y_true, y_pred, n=300)
    roc = float(roc_auc_score(y_true, y_pred)) if len(set(y_true)) > 1 else float("nan")
    brier = float(brier_score_loss(y_true, y_pred))
    k = max(1, int(0.1 * len(y_true)))
    top = np.argsort(-y_pred)[:k]
    prec_k = float(y_true[top].mean())
    return {"pr_auc": pr_auc, "pr_auc_lo": lo, "pr_auc_hi": hi,
            "roc_auc": roc, "brier": brier, "prec_at_top10pct": prec_k}


def run_xgboost(X_tr, y_tr, X_te, y_te):
    import xgboost as xgb
    spw = (y_tr == 0).sum() / max(1, (y_tr == 1).sum())
    params = dict(objective="binary:logistic", eval_metric=["logloss", "aucpr"],
                  max_depth=6, learning_rate=0.05, min_child_weight=5,
                  subsample=0.8, colsample_bytree=0.8,
                  scale_pos_weight=float(spw), verbosity=0)
    dtr = xgb.DMatrix(X_tr, label=y_tr)
    dte = xgb.DMatrix(X_te, label=y_te)
    b = xgb.train(params, dtr, num_boost_round=200,
                  evals=[(dte, "te")], early_stopping_rounds=30, verbose_eval=False)
    return b.predict(dte)


def run_lightgbm(X_tr, y_tr, X_te, y_te):
    import lightgbm as lgb
    dtr = lgb.Dataset(X_tr, label=y_tr)
    dte = lgb.Dataset(X_te, label=y_te, reference=dtr)
    spw = (y_tr == 0).sum() / max(1, (y_tr == 1).sum())
    params = dict(objective="binary", metric=["binary_logloss", "average_precision"],
                  num_leaves=63, learning_rate=0.05, feature_fraction=0.8,
                  bagging_fraction=0.8, bagging_freq=5, min_child_samples=10,
                  scale_pos_weight=float(spw), verbosity=-1)
    m = lgb.train(params, dtr, num_boost_round=200, valid_sets=[dte],
                  callbacks=[lgb.early_stopping(30, verbose=False)])
    return m.predict(X_te)


def run_logistic(X_tr, y_tr, X_te, y_te):
    sc = StandardScaler()
    X_tr_s = sc.fit_transform(X_tr)
    X_te_s = sc.transform(X_te)
    m = LogisticRegression(class_weight="balanced", max_iter=500, C=1.0)
    m.fit(X_tr_s, y_tr)
    return m.predict_proba(X_te_s)[:, 1]


def run_random_forest(X_tr, y_tr, X_te, y_te):
    m = RandomForestClassifier(n_estimators=300, max_depth=12,
                               min_samples_split=20, class_weight="balanced",
                               n_jobs=-1, random_state=42)
    m.fit(X_tr, y_tr)
    return m.predict_proba(X_te)[:, 1]


def run_tournament(df: pd.DataFrame, features=FEATURES):
    X_tr, y_tr, X_te, y_te = _split(df, features)
    out = []
    for name, runner in [("XGBoost", run_xgboost),
                         ("LightGBM", run_lightgbm),
                         ("Logistic", run_logistic),
                         ("RandomForest", run_random_forest)]:
        p = runner(X_tr, y_tr, X_te, y_te)
        s = eval_scores(y_te, p)
        s["model"] = name
        out.append(s)
        print(f"  {name:12s}  PR-AUC={s['pr_auc']:.4f} "
              f"[{s['pr_auc_lo']:.4f},{s['pr_auc_hi']:.4f}]  "
              f"ROC={s['roc_auc']:.4f}  Brier={s['brier']:.4f}  "
              f"P@10%={s['prec_at_top10pct']:.4f}",
              flush=True)
    return pd.DataFrame(out)[["model", "pr_auc", "pr_auc_lo", "pr_auc_hi",
                              "roc_auc", "brier", "prec_at_top10pct"]]


if __name__ == "__main__":
    obs = pd.read_parquet(Path(__file__).parent / "data" / "observations.parquet")
    print(f"Loaded {len(obs)} observations  base rate={obs['label_abandoned'].mean():.3f}",
          flush=True)
    print("Phase 1 tournament:", flush=True)
    res = run_tournament(obs)
    res.to_csv(Path(__file__).parent / "tournament_results.csv", index=False)
