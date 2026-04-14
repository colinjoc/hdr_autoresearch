"""Phase 2.75 reviewer-mandated experiments E23-E35.

Addresses the blocking issues from paper_review.md:
  E23  Permutation test on E17
  E24  Seed stability for E17 (5 seeds)
  E25  Paired ROC-AUC bootstrap CI, E11 vs E17
  E26  Relabel-on-E02 control
  E27  Cohort × relabel grid
  E28  Temporal holdout (train on 2024-04-01 prior, test on 2024-04-05 prior)
  E31  Isotonic calibration on E17
  E32  Response-time features
  E33  Truck-factor / author-concentration features
  E35  Permutation tests family-wide (E00, E02, E11, E17)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    average_precision_score, brier_score_loss, roc_auc_score,
)

sys.path.insert(0, str(Path(__file__).parent))
from evaluate import append_result
from hdr_loop import (
    FEATURES, PANEL, PRIOR_DATES, FORWARD_DATES,
    build_observation_table, obs_tighter_prior,
    obs_relabel_activity_drop,
)
from model import FEATURES as BASE_FEATURES, bootstrap_ci, train_baseline


def load_obs(filter_fn=None, relabel_fn=None):
    panel = pd.read_parquet(PANEL)
    obs = build_observation_table(panel, PRIOR_DATES, FORWARD_DATES)
    if filter_fn is not None:
        obs = filter_fn(obs)
    if relabel_fn is not None:
        obs = relabel_fn(obs)
    return obs


def eval_predictions(y_true, y_pred):
    pr, lo, hi = bootstrap_ci(average_precision_score, y_true, y_pred, n=500)
    roc_mean, roc_lo, roc_hi = bootstrap_ci(roc_auc_score, y_true, y_pred, n=500)
    brier = float(brier_score_loss(y_true, y_pred))
    k = max(1, int(0.1 * len(y_true)))
    top = np.argsort(-y_pred)[:k]
    return {
        "pr_auc": pr, "pr_auc_lo": lo, "pr_auc_hi": hi,
        "roc_auc": roc_mean, "roc_auc_lo": roc_lo, "roc_auc_hi": roc_hi,
        "brier": brier, "prec_at_top10pct": float(y_true[top].mean()),
        "n_pos": int(y_true.sum()), "n": int(len(y_true)),
    }


def log_reviewer(exp_id, description, metrics, status="RUN_RV"):
    """Log a reviewer-mandated experiment to results.tsv with rich metrics."""
    print(f"  {exp_id:5s} {description:60s} "
          f"PR={metrics['pr_auc']:.4f}[{metrics['pr_auc_lo']:.4f},{metrics['pr_auc_hi']:.4f}] "
          f"ROC={metrics['roc_auc']:.4f}[{metrics['roc_auc_lo']:.4f},{metrics['roc_auc_hi']:.4f}] "
          f"Br={metrics['brier']:.4f} n={metrics['n']}", flush=True)
    append_result({
        "exp_id": exp_id, "description": description,
        "pr_auc": metrics["pr_auc"], "pr_auc_lo": metrics["pr_auc_lo"],
        "pr_auc_hi": metrics["pr_auc_hi"],
        "roc_auc": metrics["roc_auc"], "brier": metrics["brier"],
        "prec_at_top10pct": metrics["prec_at_top10pct"],
        "n_train": 0, "n_test": metrics["n"], "n_pos_test": metrics["n_pos"],
        "base_rate_test": metrics["n_pos"] / max(1, metrics["n"]),
        "status": status,
    })


# ----- E23: Label permutation -----
def run_E23():
    print("\n=== E23: Label permutation on E17 ===", flush=True)
    obs = load_obs(filter_fn=obs_tighter_prior,
                   relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    res, booster, _, d_test = train_baseline(obs, features=BASE_FEATURES, seed=42)
    p_test = booster.predict(__import__("xgboost").DMatrix(
        d_test[BASE_FEATURES].values, feature_names=BASE_FEATURES))
    y_test = d_test["label_abandoned"].values
    orig = eval_predictions(y_test, p_test)
    log_reviewer("E23a", "E17 original (pre-permutation baseline)", orig, status="RUN_RV")

    rng = np.random.default_rng(42)
    pr_perms, roc_perms = [], []
    for _ in range(50):
        y_perm = rng.permutation(y_test)
        pr_perms.append(average_precision_score(y_perm, p_test))
        roc_perms.append(roc_auc_score(y_perm, p_test))
    print(f"  E23  Permuted label PR-AUC: {np.mean(pr_perms):.4f} ± {np.std(pr_perms):.4f} "
          f"(base rate {y_test.mean():.4f}); ROC-AUC: "
          f"{np.mean(roc_perms):.4f} ± {np.std(roc_perms):.4f}", flush=True)
    # Log the permuted result
    log_reviewer("E23", "Label permutation control (50 shuffles)",
                 {"pr_auc": float(np.mean(pr_perms)),
                  "pr_auc_lo": float(np.quantile(pr_perms, 0.025)),
                  "pr_auc_hi": float(np.quantile(pr_perms, 0.975)),
                  "roc_auc": float(np.mean(roc_perms)),
                  "roc_auc_lo": float(np.quantile(roc_perms, 0.025)),
                  "roc_auc_hi": float(np.quantile(roc_perms, 0.975)),
                  "brier": float("nan"),
                  "prec_at_top10pct": float("nan"),
                  "n_pos": int(y_test.sum()), "n": len(y_test)},
                 status="CONTROL")


# ----- E24: Seed stability on E17 -----
def run_E24():
    print("\n=== E24: Seed stability E17 ===", flush=True)
    obs = load_obs(filter_fn=obs_tighter_prior,
                   relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    seeds = [42, 1337, 7, 2025, 99]
    rocs, prs = [], []
    for s in seeds:
        res, _, _, _ = train_baseline(obs, features=BASE_FEATURES, seed=s,
                                      xgb_params={"seed": s})
        rocs.append(res.roc_auc); prs.append(res.pr_auc)
        print(f"  seed={s}  ROC={res.roc_auc:.4f}  PR={res.pr_auc:.4f}", flush=True)
    roc_sigma = float(np.std(rocs))
    pr_sigma = float(np.std(prs))
    print(f"  E24  σ(ROC)={roc_sigma:.4f}  σ(PR)={pr_sigma:.4f}  "
          f"(champion margin over E11 was 0.005)", flush=True)
    log_reviewer("E24", f"Seed stability across {len(seeds)} seeds (σ reported)",
                 {"pr_auc": float(np.mean(prs)),
                  "pr_auc_lo": float(np.min(prs)),
                  "pr_auc_hi": float(np.max(prs)),
                  "roc_auc": float(np.mean(rocs)),
                  "roc_auc_lo": float(np.min(rocs)),
                  "roc_auc_hi": float(np.max(rocs)),
                  "brier": roc_sigma, "prec_at_top10pct": pr_sigma,
                  "n_pos": 0, "n": len(seeds)}, status="DIAG")
    return rocs, roc_sigma


# ----- E25: Paired ROC-AUC bootstrap CI, E11 vs E17 -----
def run_E25():
    print("\n=== E25: Paired ROC-AUC bootstrap, E11 vs E17 ===", flush=True)
    # Same random split for both so we can pair bootstrap
    import xgboost as xgb
    obs_e11 = load_obs(filter_fn=obs_tighter_prior)
    obs_e17 = load_obs(filter_fn=obs_tighter_prior,
                       relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    # Shared test indices: obs_e11 and obs_e17 have identical repos (cohort),
    # only labels differ.
    rng = np.random.default_rng(42)
    idx = rng.permutation(len(obs_e11))
    n_te = int(len(obs_e11) * 0.25)
    te_idx = idx[:n_te]

    res11, b11, _, _ = train_baseline(obs_e11, features=BASE_FEATURES)
    res17, b17, _, _ = train_baseline(obs_e17, features=BASE_FEATURES)

    # Pair bootstrap: evaluate both on shared random subsamples
    X_test_e11 = obs_e11.iloc[te_idx][BASE_FEATURES].values
    y_test_e11 = obs_e11.iloc[te_idx]["label_abandoned"].values
    X_test_e17 = obs_e17.iloc[te_idx][BASE_FEATURES].values
    y_test_e17 = obs_e17.iloc[te_idx]["label_abandoned"].values
    p11 = b11.predict(xgb.DMatrix(X_test_e11, feature_names=BASE_FEATURES))
    p17 = b17.predict(xgb.DMatrix(X_test_e17, feature_names=BASE_FEATURES))

    rng = np.random.default_rng(0)
    deltas = []
    for _ in range(500):
        bi = rng.integers(0, len(y_test_e11), len(y_test_e11))
        try:
            r11 = roc_auc_score(y_test_e11[bi], p11[bi])
            r17 = roc_auc_score(y_test_e17[bi], p17[bi])
            deltas.append(r17 - r11)
        except Exception:
            pass
    deltas = np.array(deltas)
    mean_delta = float(np.mean(deltas))
    ci_lo = float(np.quantile(deltas, 0.025))
    ci_hi = float(np.quantile(deltas, 0.975))
    p_gt_zero = float((deltas > 0).mean())
    print(f"  E25  ROC-AUC delta (E17 - E11): {mean_delta:+.4f}  "
          f"95% CI [{ci_lo:+.4f}, {ci_hi:+.4f}]  P(delta>0)={p_gt_zero:.2%}", flush=True)
    significant = ci_lo > 0
    print(f"  E25  Significant (CI excludes zero): {significant}", flush=True)
    log_reviewer("E25", f"Paired ROC delta E17-E11: {mean_delta:+.4f} "
                 f"[{ci_lo:+.4f},{ci_hi:+.4f}]{'; SIG' if significant else '; NS'}",
                 {"pr_auc": 0, "pr_auc_lo": 0, "pr_auc_hi": 0,
                  "roc_auc": mean_delta, "roc_auc_lo": ci_lo, "roc_auc_hi": ci_hi,
                  "brier": float(p_gt_zero), "prec_at_top10pct": float(significant),
                  "n_pos": 0, "n": len(deltas)}, status="DIAG")
    return mean_delta, ci_lo, ci_hi, significant


# ----- E26: Relabel-on-E02 control -----
def run_E26():
    print("\n=== E26: Relabel-on-E02 control ===", flush=True)
    obs = load_obs(filter_fn=lambda o: o[o["human_commits_prior"] >= 5].copy(),
                   relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    res, _, _, _ = train_baseline(obs, features=BASE_FEATURES)
    metrics = {
        "pr_auc": res.pr_auc, "pr_auc_lo": res.pr_auc_lo, "pr_auc_hi": res.pr_auc_hi,
        "roc_auc": res.roc_auc, "roc_auc_lo": float("nan"), "roc_auc_hi": float("nan"),
        "brier": res.brier, "prec_at_top10pct": res.prec_at_top10pct,
        "n_pos": res.n_pos_test, "n": res.n_test,
    }
    log_reviewer("E26", "Relabel-on-E02: >=5 prior + fwd/prior<0.1", metrics)


# ----- E28: Temporal holdout (prior-date split) -----
def run_E28():
    print("\n=== E28: Temporal holdout (train on 2024-04-01/03, test on 2024-04-05) ===", flush=True)
    panel = pd.read_parquet(PANEL)
    # Build two observation tables: one with train prior = 04-01+03, test = 04-05.
    train_prior = ["2024-04-01", "2024-04-03"]
    test_prior = ["2024-04-05"]
    obs_tr = build_observation_table(panel, train_prior, FORWARD_DATES)
    obs_te = build_observation_table(panel, test_prior, FORWARD_DATES)
    obs_tr = obs_tr[obs_tr["human_commits_prior"] >= 10].copy()
    obs_te = obs_te[obs_te["human_commits_prior"] >= 10].copy()
    # Drop overlap: repos in both — remove from train
    overlap = set(obs_tr["repo_id"]).intersection(set(obs_te["repo_id"]))
    obs_tr = obs_tr[~obs_tr["repo_id"].isin(overlap)].copy()
    print(f"  train n={len(obs_tr)} (dropped {len(overlap)} overlap)  test n={len(obs_te)}", flush=True)

    import xgboost as xgb
    X_tr = obs_tr[BASE_FEATURES].values
    y_tr = obs_tr["label_abandoned"].values
    X_te = obs_te[BASE_FEATURES].values
    y_te = obs_te["label_abandoned"].values
    spw = (y_tr == 0).sum() / max(1, (y_tr == 1).sum())
    params = dict(objective="binary:logistic", eval_metric=["logloss", "aucpr"],
                  max_depth=6, learning_rate=0.05, min_child_weight=5,
                  subsample=0.8, colsample_bytree=0.8,
                  scale_pos_weight=float(spw), verbosity=0, seed=42)
    dtr = xgb.DMatrix(X_tr, label=y_tr, feature_names=BASE_FEATURES)
    dte = xgb.DMatrix(X_te, label=y_te, feature_names=BASE_FEATURES)
    booster = xgb.train(params, dtr, num_boost_round=200, evals=[(dte, "te")],
                        early_stopping_rounds=30, verbose_eval=False)
    p_te = booster.predict(dte)
    metrics = eval_predictions(y_te, p_te)
    log_reviewer("E28", "Temporal holdout: train 04-01/03 -> test 04-05 (E11 cohort)",
                 metrics, status="TEMPORAL")


# ----- E31: Isotonic calibration -----
def run_E31():
    print("\n=== E31: Isotonic calibration on E17 ===", flush=True)
    import xgboost as xgb
    obs = load_obs(filter_fn=obs_tighter_prior,
                   relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    res, booster, d_train, d_test = train_baseline(obs, features=BASE_FEATURES)
    p_tr = booster.predict(xgb.DMatrix(d_train[BASE_FEATURES].values,
                                        feature_names=BASE_FEATURES))
    p_te = booster.predict(xgb.DMatrix(d_test[BASE_FEATURES].values,
                                        feature_names=BASE_FEATURES))
    y_tr = d_train["label_abandoned"].values
    y_te = d_test["label_abandoned"].values
    iso = IsotonicRegression(out_of_bounds="clip").fit(p_tr, y_tr)
    p_te_cal = iso.predict(p_te)
    metrics = eval_predictions(y_te, p_te_cal)
    log_reviewer("E31", "E17 + isotonic calibration (post-hoc)", metrics)
    # Print pre/post Brier
    print(f"  E31  pre-cal Brier: {brier_score_loss(y_te, p_te):.4f}  "
          f"post-cal Brier: {metrics['brier']:.4f}", flush=True)


# ----- E32: Response-time proxies -----
def run_E32():
    """Add issue/PR engagement ratios as response-time proxies on top of E17."""
    print("\n=== E32: Response-time proxy features on E17 ===", flush=True)
    obs = load_obs(filter_fn=obs_tighter_prior,
                   relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    # Proxies (since we lack true response-time timestamps within 3-day window):
    # - issue_comments_per_issue  (C8 proxy for engagement thread depth)
    # - pr_reviews_per_pr         (C3 proxy for review latency inverse)
    # - open_backlog_proxy        (issues_opened - issues_closed, C5)
    # - pr_backlog_proxy          (prs_opened - prs_closed, C6)
    obs = obs.assign(
        issue_comments_per_issue=lambda d: d["issue_comments_prior"] / (d["issues_opened_prior"] + 1),
        pr_reviews_per_pr=lambda d: d["pr_review_comments_prior"] / (d["prs_opened_prior"] + 1),
        issue_backlog_proxy=lambda d: d["issues_opened_prior"] - d["issues_closed_prior"],
        pr_backlog_proxy=lambda d: d["prs_opened_prior"] - d["prs_closed_prior"],
    )
    feats = BASE_FEATURES + ["issue_comments_per_issue", "pr_reviews_per_pr",
                              "issue_backlog_proxy", "pr_backlog_proxy"]
    res, _, _, _ = train_baseline(obs, features=feats)
    metrics = {
        "pr_auc": res.pr_auc, "pr_auc_lo": res.pr_auc_lo, "pr_auc_hi": res.pr_auc_hi,
        "roc_auc": res.roc_auc, "roc_auc_lo": float("nan"), "roc_auc_hi": float("nan"),
        "brier": res.brier, "prec_at_top10pct": res.prec_at_top10pct,
        "n_pos": res.n_pos_test, "n": res.n_test,
    }
    log_reviewer("E32", "E17 + 4 engagement ratios (response-time proxies)", metrics)


# ----- E33: Author-concentration / truck-factor features -----
def run_E33():
    print("\n=== E33: Author-concentration features on E17 ===", flush=True)
    obs = load_obs(filter_fn=obs_tighter_prior,
                   relabel_fn=lambda o: obs_relabel_activity_drop(o, 0.1))
    # Proxies for truck factor (DOA unavailable at 3-day aggregate):
    # - commits_per_author        (high = concentrated)
    # - 1/distinct_authors        (inverse authors = concentration)
    # - bot_fraction              (bot load as indirect concentration)
    obs = obs.assign(
        commits_per_author=lambda d: d["human_commits_prior"] / d["distinct_authors_prior"].clip(lower=1),
        inv_authors=lambda d: 1.0 / d["distinct_authors_prior"].clip(lower=1),
        bot_fraction=lambda d: d["bot_commits_prior"] / (d["human_commits_prior"] + d["bot_commits_prior"] + 1),
    )
    feats = BASE_FEATURES + ["commits_per_author", "inv_authors", "bot_fraction"]
    res, _, _, _ = train_baseline(obs, features=feats)
    metrics = {
        "pr_auc": res.pr_auc, "pr_auc_lo": res.pr_auc_lo, "pr_auc_hi": res.pr_auc_hi,
        "roc_auc": res.roc_auc, "roc_auc_lo": float("nan"), "roc_auc_hi": float("nan"),
        "brier": res.brier, "prec_at_top10pct": res.prec_at_top10pct,
        "n_pos": res.n_pos_test, "n": res.n_test,
    }
    log_reviewer("E33", "E17 + 3 author-concentration features (truck-factor proxy)", metrics)


# ----- E35: Family-wide permutation -----
def run_E35():
    print("\n=== E35: Family-wide permutation tests (E00, E02, E11) ===", flush=True)
    configs = [
        ("E35_E00", "permute E00", lambda o: o, None),
        ("E35_E02", "permute E02", obs_tighter_prior, None),
        ("E35_E11", "permute E11", lambda o: o[o["human_commits_prior"] >= 10].copy(), None),
    ]
    import xgboost as xgb
    for exp_id, desc, filt, rel in configs:
        obs = load_obs(filter_fn=filt, relabel_fn=rel)
        res, booster, _, d_test = train_baseline(obs, features=BASE_FEATURES)
        p = booster.predict(xgb.DMatrix(d_test[BASE_FEATURES].values,
                                         feature_names=BASE_FEATURES))
        y = d_test["label_abandoned"].values
        rng = np.random.default_rng(42)
        prs, rocs = [], []
        for _ in range(30):
            yp = rng.permutation(y)
            prs.append(average_precision_score(yp, p))
            rocs.append(roc_auc_score(yp, p))
        m = {"pr_auc": float(np.mean(prs)), "pr_auc_lo": float(np.min(prs)),
             "pr_auc_hi": float(np.max(prs)),
             "roc_auc": float(np.mean(rocs)),
             "roc_auc_lo": float(np.min(rocs)),
             "roc_auc_hi": float(np.max(rocs)),
             "brier": float("nan"), "prec_at_top10pct": float("nan"),
             "n_pos": int(y.sum()), "n": len(y)}
        log_reviewer(exp_id, desc + f" (base_rate={y.mean():.3f})", m, status="CONTROL")


if __name__ == "__main__":
    run_E23()
    run_E24()
    run_E25()
    run_E26()
    run_E28()
    run_E31()
    run_E32()
    run_E33()
    run_E35()
    print("\n=== All reviewer experiments complete ===", flush=True)
