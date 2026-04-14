"""E00 baseline: unconditional YC effect on follow-on raise within 5 years.

E00 intentionally uses NO covariates — it is the raw headline effect,
against which every Phase-2 matched / controlled estimate will be compared
to show effect attenuation (per research_queue.md theme F and Fehder 2024).

Also trains a minimal logistic baseline with `is_yc` + `log_offering_amount`
+ calendar-quarter fixed effects for model-shape metrics (ROC/PR-AUC/Brier).
Temporal holdout: train on filing_date < 2018-07-01, test on ≥ 2018-07-01.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import hstack

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import (  # noqa: E402
    ExperimentResult, append_result,
    classifier_metrics, risk_diff_with_ci,
)


def main():
    panel = pd.read_parquet(HERE / "data" / "panel.parquet")
    panel["filing_date"] = pd.to_datetime(panel["filing_date"])

    # --- E00a: raw unconditional risk difference ---
    y_t = panel.loc[panel.is_yc == 1, "follow_on_raise_within_5y"].values
    y_c = panel.loc[panel.is_yc == 0, "follow_on_raise_within_5y"].values
    rd, lo, hi = risk_diff_with_ci(y_t, y_c, n_boot=5000, seed=17)
    r0 = ExperimentResult(
        exp_id="E00a",
        description="Unconditional risk difference: P(follow-on raise | YC) - P(... | non-YC)",
        n_treated=len(y_t), n_control=len(y_c),
        rate_treated=float(y_t.mean()), rate_control=float(y_c.mean()),
        risk_diff=float(rd), rd_ci_lo=float(lo), rd_ci_hi=float(hi),
        status="BASELINE",
    )
    append_result(r0)
    print(f"E00a: YC rate={y_t.mean():.3f}  non-YC rate={y_c.mean():.3f}  "
          f"RD={rd:+.4f} 95% CI [{lo:+.4f}, {hi:+.4f}]  n_t={len(y_t)} n_c={len(y_c)}",
          flush=True)

    # --- E00b: logistic with is_yc + log_offering_amount + filing-year FE ---
    p = panel.copy()
    p["filing_year"] = p["filing_date"].dt.year.astype(int)
    p["filing_quarter"] = p["filing_date"].dt.quarter.astype(int)
    p = p.dropna(subset=["log_offering_amount", "filing_year"])

    # temporal holdout
    train_mask = p["filing_date"] < pd.Timestamp("2018-07-01")
    test_mask = ~train_mask
    train, test = p[train_mask], p[test_mask]

    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    enc.fit(train[["filing_year", "filing_quarter"]].astype(str))

    def to_X(df):
        cat = enc.transform(df[["filing_year", "filing_quarter"]].astype(str))
        num = df[["is_yc", "log_offering_amount"]].to_numpy()
        from scipy.sparse import csr_matrix
        return hstack([csr_matrix(num), cat]).tocsr()

    X_tr, y_tr = to_X(train), train["follow_on_raise_within_5y"].values
    X_te, y_te = to_X(test), test["follow_on_raise_within_5y"].values

    # Handle imbalanced class → use liblinear L2 logistic
    clf = LogisticRegression(max_iter=2000, solver="liblinear", C=1.0)
    clf.fit(X_tr, y_tr)
    prob_te = clf.predict_proba(X_te)[:, 1]
    m = classifier_metrics(y_te, prob_te)

    # Treatment-effect on test set: holding covariates fixed
    test_yc = test[test.is_yc == 1]
    test_nonyc = test[test.is_yc == 0]
    rd2, lo2, hi2 = risk_diff_with_ci(
        test_yc["follow_on_raise_within_5y"].values,
        test_nonyc["follow_on_raise_within_5y"].values,
        n_boot=5000, seed=17,
    )

    r1 = ExperimentResult(
        exp_id="E00b",
        description="Logistic[is_yc + log_offering + year_FE + quarter_FE], temporal split 2018-07-01",
        n_treated=int((test.is_yc == 1).sum()),
        n_control=int((test.is_yc == 0).sum()),
        rate_treated=float(test_yc["follow_on_raise_within_5y"].mean()),
        rate_control=float(test_nonyc["follow_on_raise_within_5y"].mean()),
        risk_diff=float(rd2), rd_ci_lo=float(lo2), rd_ci_hi=float(hi2),
        roc_auc=m["roc_auc"], pr_auc=m["pr_auc"],
        brier=m["brier"], log_loss=m["log_loss"],
        n_train=int(train_mask.sum()), n_test=int(test_mask.sum()),
        status="BASELINE",
    )
    append_result(r1)
    print(f"E00b: test-set ROC={m['roc_auc']:.4f} PR-AUC={m['pr_auc']:.4f} "
          f"Brier={m['brier']:.4f}  RD_test={rd2:+.4f} CI [{lo2:+.4f},{hi2:+.4f}]  "
          f"n_train={int(train_mask.sum())} n_test={int(test_mask.sum())}", flush=True)

    # log coefficient on is_yc for interpretability
    feat_names = ["is_yc", "log_offering_amount"] + list(enc.get_feature_names_out())
    is_yc_idx = feat_names.index("is_yc")
    coef = clf.coef_[0, is_yc_idx]
    odds_ratio = float(np.exp(coef))
    print(f"      is_yc coefficient (log-odds) = {coef:+.4f}  odds ratio = {odds_ratio:.3f}",
          flush=True)


if __name__ == "__main__":
    main()
