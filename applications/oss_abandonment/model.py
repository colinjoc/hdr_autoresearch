"""
OSS abandonment XGBoost baseline.

Build features from the per-(repo_id, date) panel (output of data_loaders.aggregate),
label each repo based on prior-vs-forward human-commit activity, train XGBoost,
and report PR-AUC, ROC-AUC, Brier, precision@k metrics with bootstrap CIs.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    average_precision_score, brier_score_loss, roc_auc_score,
)


FEATURES = [
    # Activity (A family)
    "human_commits_prior",
    "bot_commits_prior",
    "log1p_human_commits_prior",
    "distinct_authors_prior",
    "days_active_prior",
    # Response/engagement
    "issues_opened_prior",
    "issues_closed_prior",
    "issue_comments_prior",
    "prs_opened_prior",
    "prs_merged_prior",
    "pr_review_comments_prior",
    # Popularity
    "stars_prior",
    "forks_prior",
    "releases_prior",
    "member_changes_prior",
    # Derived ratios
    "bot_human_ratio",
    "pr_merge_rate",
    "issue_close_rate",
]


def build_observation_table(panel: pd.DataFrame,
                            prior_dates: list[str],
                            forward_dates: list[str]) -> pd.DataFrame:
    """Collapse the daily panel into one row per repo with prior + forward counts.

    prior_dates: UTC dates to include as the "at T and earlier" activity window.
    forward_dates: UTC dates to include as the "after T" horizon window.
    Returns a DataFrame keyed by repo_id with features and the 'label_abandoned' column.
    """
    panel = panel.copy()
    panel["date"] = panel["date"].astype(str)

    prior = panel[panel["date"].isin(prior_dates)]
    fwd = panel[panel["date"].isin(forward_dates)]

    agg_cols = [
        "human_commits", "bot_commits", "distinct_authors",
        "issues_opened", "issues_closed", "issue_comments",
        "prs_opened", "prs_closed", "prs_merged", "pr_review_comments",
        "stars", "forks", "releases", "member_changes",
    ]

    prior_g = prior.groupby("repo_id")[agg_cols].sum()
    prior_g["days_active"] = prior.groupby("repo_id")["date"].nunique()
    prior_g.columns = [f"{c}_prior" if c != "days_active" else "days_active_prior"
                       for c in prior_g.columns]

    fwd_g = fwd.groupby("repo_id")["human_commits"].sum().rename("human_commits_forward")

    rows = prior_g.join(fwd_g, how="left")
    rows["human_commits_forward"] = rows["human_commits_forward"].fillna(0).astype(int)

    # Derived
    rows["log1p_human_commits_prior"] = np.log1p(rows["human_commits_prior"])
    rows["bot_human_ratio"] = rows["bot_commits_prior"] / (rows["human_commits_prior"] + 1)
    rows["pr_merge_rate"] = rows["prs_merged_prior"] / (rows["prs_closed_prior"] + 1)
    rows["issue_close_rate"] = rows["issues_closed_prior"] / (rows["issues_opened_prior"] + 1)

    # Label: abandoned iff 0 human commits in forward window
    rows["label_abandoned"] = (rows["human_commits_forward"] == 0).astype(int)

    # Filter to "active at T": at least one human commit in prior
    rows = rows[rows["human_commits_prior"] >= 1].copy()
    return rows.reset_index()


def bootstrap_ci(fn, y_true, y_pred, n: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    N = len(y_true)
    vals = []
    for _ in range(n):
        idx = rng.integers(0, N, N)
        try:
            vals.append(fn(y_true[idx], y_pred[idx]))
        except Exception:
            pass
    vals = np.array(vals)
    return float(np.mean(vals)), float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


@dataclass
class BaselineResult:
    pr_auc: float
    pr_auc_lo: float
    pr_auc_hi: float
    roc_auc: float
    brier: float
    prec_at_top10pct: float
    n_train: int
    n_test: int
    n_pos_test: int
    base_rate_test: float


def train_baseline(df: pd.DataFrame,
                   features: list[str] = FEATURES,
                   label_col: str = "label_abandoned",
                   test_frac: float = 0.25,
                   seed: int = 42,
                   xgb_params: dict | None = None) -> tuple[BaselineResult, xgb.Booster, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(df))
    n_test = int(len(df) * test_frac)
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]

    d_train = df.iloc[train_idx]
    d_test = df.iloc[test_idx]

    X_train = d_train[features].values
    y_train = d_train[label_col].values
    X_test = d_test[features].values
    y_test = d_test[label_col].values

    params = {
        "objective": "binary:logistic",
        "eval_metric": ["logloss", "aucpr"],
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_weight": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": float((y_train == 0).sum() / max(1, (y_train == 1).sum())),
        "verbosity": 0,
    }
    if xgb_params:
        params.update(xgb_params)

    dtr = xgb.DMatrix(X_train, label=y_train, feature_names=features)
    dte = xgb.DMatrix(X_test, label=y_test, feature_names=features)
    booster = xgb.train(params, dtr, num_boost_round=200,
                        evals=[(dtr, "tr"), (dte, "te")],
                        early_stopping_rounds=30, verbose_eval=False)
    p_test = booster.predict(dte)

    pr_auc, pr_lo, pr_hi = bootstrap_ci(average_precision_score, y_test, p_test, n=500)
    roc = float(roc_auc_score(y_test, p_test)) if len(set(y_test)) > 1 else float("nan")
    brier = float(brier_score_loss(y_test, p_test))

    # Precision at top 10%
    k = max(1, int(0.1 * len(y_test)))
    top_k = np.argsort(-p_test)[:k]
    prec_k = float(y_test[top_k].mean())

    res = BaselineResult(
        pr_auc=pr_auc, pr_auc_lo=pr_lo, pr_auc_hi=pr_hi,
        roc_auc=roc, brier=brier, prec_at_top10pct=prec_k,
        n_train=len(y_train), n_test=len(y_test),
        n_pos_test=int(y_test.sum()),
        base_rate_test=float(y_test.mean()),
    )
    return res, booster, d_train, d_test.assign(score=p_test)
