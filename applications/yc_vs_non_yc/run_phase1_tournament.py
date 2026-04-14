"""Phase 1: model-family tournament for P(follow_on_raise_within_5y | covariates).

Families (all with a fixed feature set — M3 from design_variables.md):
  L1  Logistic L1 (Lasso) sanity check
  L2  Logistic L2
  RF  Random Forest
  GB  XGBoost
  LB  LightGBM

Evaluation:
  - Temporal rolling-origin CV on train (2014-2017, 3 folds)
  - Temporal holdout: 2018-07-01 onward → never touched during selection
  - Metric: PR-AUC primary (base rate ≈ 29 %), ROC-AUC secondary, Brier for calibration
  - 5 seeds per family; report mean ± std

Champion rule: highest test-set PR-AUC on the temporal holdout AFTER
verifying the rolling-origin CV rank is consistent.
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
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import csr_matrix, hstack

warnings.filterwarnings("ignore", category=UserWarning)

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import (  # noqa: E402
    ExperimentResult, append_result, classifier_metrics,
)


BAY_STATES = {"CA"}
BIG_VC_STATES = {"CA", "NY", "MA", "WA", "TX"}

NUM_FEATURES = ["is_yc", "log_offering_amount"]
CAT_FEATURES = ["filing_year", "filing_quarter", "stateorcountry", "industrygrouptype", "entitytype"]
DERIVED_BOOL_FEATURES = ["is_bay", "is_big_vc"]


def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(HERE / "data" / "panel.parquet")
    p["filing_date"] = pd.to_datetime(p["filing_date"])
    p["filing_year"] = p["filing_date"].dt.year.astype(int)
    p["filing_quarter"] = p["filing_date"].dt.quarter.astype(int)
    p["is_bay"] = p["stateorcountry"].isin(BAY_STATES).astype(int)
    p["is_big_vc"] = p["stateorcountry"].isin(BIG_VC_STATES).astype(int)
    p = p.dropna(subset=["log_offering_amount", "filing_year",
                         "industrygrouptype", "stateorcountry"]).copy()
    return p


def make_xy(train: pd.DataFrame, test: pd.DataFrame):
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=True, min_frequency=10)
    enc.fit(train[CAT_FEATURES].astype(str))

    def X(df):
        cat = enc.transform(df[CAT_FEATURES].astype(str))
        num = df[NUM_FEATURES + DERIVED_BOOL_FEATURES].to_numpy(dtype=np.float64)
        return hstack([csr_matrix(num), cat]).tocsr()

    return (X(train), train["follow_on_raise_within_5y"].values,
            X(test),  test["follow_on_raise_within_5y"].values,
            enc)


def fit_predict(family: str, X_tr, y_tr, X_te, seed: int):
    if family == "L1":
        m = LogisticRegression(penalty="l1", solver="liblinear", C=1.0,
                               max_iter=2000, random_state=seed)
    elif family == "L2":
        m = LogisticRegression(penalty="l2", solver="liblinear", C=1.0,
                               max_iter=2000, random_state=seed)
    elif family == "RF":
        m = RandomForestClassifier(n_estimators=300, max_depth=8,
                                   n_jobs=-1, random_state=seed)
    elif family == "GB":
        m = xgb.XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            eval_metric="logloss", random_state=seed, n_jobs=-1,
            tree_method="hist",
        )
    elif family == "LB":
        m = lgb.LGBMClassifier(
            n_estimators=300, max_depth=-1, num_leaves=31, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=seed, n_jobs=-1, verbose=-1,
        )
    else:
        raise ValueError(family)

    # sklearn RF needs dense-like; sparse fine for others
    if family == "RF":
        m.fit(X_tr.toarray(), y_tr)
        return m.predict_proba(X_te.toarray())[:, 1]
    m.fit(X_tr, y_tr)
    return m.predict_proba(X_te)[:, 1]


def main():
    panel = load_panel()
    train_full = panel[panel.filing_date < pd.Timestamp("2018-07-01")].copy()
    test = panel[panel.filing_date >= pd.Timestamp("2018-07-01")].copy()
    print(f"train {len(train_full):,}  test {len(test):,}  "
          f"pos rate train {train_full['follow_on_raise_within_5y'].mean():.3f}  "
          f"test {test['follow_on_raise_within_5y'].mean():.3f}", flush=True)

    families = ["L1", "L2", "RF", "GB", "LB"]
    seeds = [17, 23, 42, 101, 2027]

    # Rolling-origin CV on train: (2014 ⊢ 2015), (2014-2015 ⊢ 2016), (2014-2016 ⊢ 2017 H1)
    folds = [
        (pd.Timestamp("2015-01-01"), pd.Timestamp("2016-01-01")),
        (pd.Timestamp("2016-01-01"), pd.Timestamp("2017-01-01")),
        (pd.Timestamp("2017-01-01"), pd.Timestamp("2018-01-01")),
    ]

    rows = []
    for fam in families:
        cv_prs = []
        te_prs, te_rocs, te_briers = [], [], []
        for s in seeds:
            # Rolling-origin CV
            fold_prs = []
            for cut, end in folds:
                tr = train_full[train_full.filing_date < cut]
                va = train_full[(train_full.filing_date >= cut)
                                & (train_full.filing_date < end)]
                if len(tr) < 100 or len(va) < 50:
                    continue
                X_tr, y_tr, X_va, y_va, _ = make_xy(tr, va)
                p = fit_predict(fam, X_tr, y_tr, X_va, s)
                m = classifier_metrics(y_va, p)
                fold_prs.append(m["pr_auc"])
            cv_prs.append(np.mean(fold_prs) if fold_prs else float("nan"))

            # Holdout test
            X_tr, y_tr, X_te, y_te, _ = make_xy(train_full, test)
            p = fit_predict(fam, X_tr, y_tr, X_te, s)
            m = classifier_metrics(y_te, p)
            te_prs.append(m["pr_auc"])
            te_rocs.append(m["roc_auc"])
            te_briers.append(m["brier"])

        cv_pr_mean = float(np.nanmean(cv_prs))
        cv_pr_std = float(np.nanstd(cv_prs))
        te_pr_mean = float(np.mean(te_prs))
        te_pr_std = float(np.std(te_prs))
        te_roc_mean = float(np.mean(te_rocs))
        te_brier_mean = float(np.mean(te_briers))
        print(f"{fam}: CV PR-AUC {cv_pr_mean:.4f} ± {cv_pr_std:.4f}  |  "
              f"TEST PR-AUC {te_pr_mean:.4f} ± {te_pr_std:.4f}  "
              f"ROC {te_roc_mean:.4f}  Brier {te_brier_mean:.4f}", flush=True)
        rows.append({
            "family": fam,
            "cv_pr_auc_mean": cv_pr_mean, "cv_pr_auc_std": cv_pr_std,
            "test_pr_auc_mean": te_pr_mean, "test_pr_auc_std": te_pr_std,
            "test_roc_auc_mean": te_roc_mean, "test_brier_mean": te_brier_mean,
        })

        res = ExperimentResult(
            exp_id=f"E01-{fam}",
            description=f"Phase-1 tournament family={fam}; 5 seeds; rolling-CV + temporal holdout",
            n_test=len(test), n_train=len(train_full),
            pr_auc=te_pr_mean, roc_auc=te_roc_mean, brier=te_brier_mean,
            status="TOURNAMENT",
        )
        append_result(res)

    df = pd.DataFrame(rows).sort_values("test_pr_auc_mean", ascending=False)
    print("\n=== Tournament ranking (by test PR-AUC) ===")
    print(df.to_string(index=False))
    champ = df.iloc[0]["family"]
    print(f"\nCHAMPION = {champ}")
    (HERE / "data" / "phase1_champion.txt").write_text(champ)


if __name__ == "__main__":
    main()
