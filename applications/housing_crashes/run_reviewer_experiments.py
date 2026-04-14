"""Phase 2.75 mandatory follow-up experiments RV-1..RV-7."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from evaluate import Result, append_result, classifier_metrics  # noqa: E402
from hdr_loop import BASE_FEATURES, split, fit_l2  # noqa: E402


def main():
    panel = pd.read_parquet(HERE / "data" / "panel.parquet")
    panel["month"] = pd.to_datetime(panel["month"])

    train, test, feats = split(panel)
    prob_te, y_te, y_tr, _, _ = fit_l2(train, test, feats)
    base_rate_te = float(y_te.mean())
    obs_pr_auc = float(average_precision_score(y_te, prob_te))
    print(f"Reference: PR-AUC={obs_pr_auc:.4f}  base_rate={base_rate_te:.4f}  "
          f"n_test={len(y_te):,}  n_pos={int(y_te.sum())}", flush=True)

    # First, audit the 95 positives: how many distinct metros?
    crashed = test[test["crash_next_12mo"] == 1]
    crash_metros = crashed["cbsa_code"].nunique()
    print(f"\n=== AUDIT: 95 positive rows → {crash_metros} distinct metros ===", flush=True)
    print("Top 10 crashing metros by row count:", flush=True)
    print(crashed.groupby(["cbsa_code", "cbsa_title"]).size().sort_values(ascending=False)
          .head(10).to_string(), flush=True)

    # --- RV-4: single-feature baseline (fastest, most damaging) ---
    print("\n[RV-4] Single-feature baseline: score = -zhvi_12mo_ret", flush=True)
    score = -test["zhvi_12mo_ret"].values  # more-negative past return → higher risk
    sf_pr = float(average_precision_score(y_te, score))
    sf_roc = float(roc_auc_score(y_te, score))
    print(f"  PR-AUC = {sf_pr:.4f}  ROC = {sf_roc:.4f}  "
          f"lift = {sf_pr/base_rate_te:.2f}×", flush=True)
    print(f"  L2 PR-AUC / single-feature PR-AUC = {obs_pr_auc/sf_pr:.3f}", flush=True)
    append_result(Result(
        exp_id="RV-4",
        description="Single-feature baseline: score = -zhvi_12mo_ret",
        n_train=len(train), n_test=len(test),
        pos_rate_test=base_rate_te,
        pr_auc=sf_pr, roc_auc=sf_roc,
        pr_auc_lift_over_base=sf_pr / base_rate_te,
        status="REVIEW",
    ))

    # --- RV-3: collapse test positives to metro-events ---
    print("\n[RV-3] Collapse positives to one row per metro", flush=True)
    te2 = test.copy()
    te2["_prob"] = prob_te
    pos_rows = (te2[te2["crash_next_12mo"] == 1]
                .sort_values("_prob", ascending=False)
                .drop_duplicates("cbsa_code", keep="first"))
    neg_rows = (te2[te2["crash_next_12mo"] == 0]
                .sort_values("_prob", ascending=False)
                .drop_duplicates("cbsa_code", keep="first"))
    collapsed = pd.concat([pos_rows, neg_rows])
    y_c = collapsed["crash_next_12mo"].values
    p_c = collapsed["_prob"].values
    m = classifier_metrics(y_c, p_c)
    print(f"  n_pos={int(y_c.sum())}  n_neg={int((1-y_c).sum())}  "
          f"PR-AUC={m['pr_auc']:.4f}  ROC={m['roc_auc']:.4f}  "
          f"lift={m['pr_auc_lift_over_base']:.2f}×", flush=True)
    append_result(Result(
        exp_id="RV-3",
        description=f"Metro-collapsed test: 1 row/metro (n_pos={int(y_c.sum())}, n_neg={int((1-y_c).sum())})",
        n_train=len(train), n_test=len(collapsed),
        pos_rate_test=float(y_c.mean()),
        pr_auc=m["pr_auc"], roc_auc=m["roc_auc"],
        pr_auc_lift_over_base=m["pr_auc_lift_over_base"],
        top_k_precision=m["top_k_precision"], top_k_k=m["top_k_k"],
        status="REVIEW",
    ))

    # --- RV-6: population-weighted evaluation ---
    print("\n[RV-6] Population-weighted PR-AUC", flush=True)
    w = 1.0 / np.sqrt(test["size_rank"].values.astype(float))
    w = w / w.mean()
    w_pr = float(average_precision_score(y_te, prob_te, sample_weight=w))
    # ROC also weighted
    w_roc = float(roc_auc_score(y_te, prob_te, sample_weight=w))
    print(f"  weighted PR-AUC = {w_pr:.4f}  (vs unweighted {obs_pr_auc:.4f})", flush=True)
    print(f"  weighted ROC    = {w_roc:.4f}", flush=True)
    append_result(Result(
        exp_id="RV-6",
        description="Population-weighted PR-AUC (inverse sqrt size_rank weights)",
        n_test=len(test), pos_rate_test=base_rate_te,
        pr_auc=w_pr, roc_auc=w_roc,
        pr_auc_lift_over_base=w_pr / base_rate_te,
        status="REVIEW",
    ))

    # --- RV-1: metro-clustered block bootstrap ---
    print("\n[RV-1] Metro-clustered block bootstrap (2000 resamples)", flush=True)
    rng = np.random.default_rng(17)
    metros = test["cbsa_code"].unique()
    metro_to_idx = {m: np.where(test["cbsa_code"].values == m)[0] for m in metros}
    boots = np.empty(2000)
    for b in range(2000):
        sampled = rng.choice(metros, size=len(metros), replace=True)
        idx = np.concatenate([metro_to_idx[m] for m in sampled])
        boots[b] = average_precision_score(y_te[idx], prob_te[idx])
    lo, hi = float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))
    print(f"  95% CI = [{lo:.4f}, {hi:.4f}]  "
          f"point = {obs_pr_auc:.4f}  "
          f"base = {base_rate_te:.4f}", flush=True)
    print(f"  CI excludes base rate? {lo > base_rate_te}", flush=True)
    append_result(Result(
        exp_id="RV-1",
        description=f"Metro-clustered block bootstrap PR-AUC CI = [{lo:.4f}, {hi:.4f}]",
        n_test=len(test), pos_rate_test=base_rate_te,
        pr_auc=obs_pr_auc, pr_auc_lift_over_base=obs_pr_auc / base_rate_te,
        status="REVIEW",
    ))

    # --- RV-7: within-month detrended features ---
    print("\n[RV-7] Within-month standardised features (remove national trend)", flush=True)
    p2 = panel.copy()
    for f in BASE_FEATURES:
        if f not in p2.columns:
            continue
        g = p2.groupby("month")[f]
        mu = g.transform("mean"); sd = g.transform("std").replace(0, 1)
        p2[f] = (p2[f] - mu) / sd
    tr, te, feats2 = split(p2)
    prob2, y2, _, _, _ = fit_l2(tr, te, feats2)
    m = classifier_metrics(y2, prob2)
    print(f"  PR-AUC={m['pr_auc']:.4f}  ROC={m['roc_auc']:.4f}  "
          f"lift={m['pr_auc_lift_over_base']:.2f}×", flush=True)
    append_result(Result(
        exp_id="RV-7",
        description="L2 on within-month standardised features (national trend removed)",
        n_train=len(tr), n_test=len(te),
        pos_rate_test=float(y2.mean()),
        pr_auc=m["pr_auc"], roc_auc=m["roc_auc"],
        pr_auc_lift_over_base=m["pr_auc_lift_over_base"],
        top_k_precision=m["top_k_precision"], top_k_k=m["top_k_k"],
        status="REVIEW",
    ))

    # --- RV-5: leave-one-metro-out ---
    print("\n[RV-5] Leave-one-metro-out PR-AUC sensitivity", flush=True)
    impacts = []
    crashing = test[test["crash_next_12mo"] == 1]["cbsa_code"].unique()
    for metro in crashing:
        mask = test["cbsa_code"].values != metro
        pr = float(average_precision_score(y_te[mask], prob_te[mask]))
        drop = (obs_pr_auc - pr) / obs_pr_auc
        impacts.append((metro, pr, drop))
    impacts.sort(key=lambda x: -x[2])
    print(f"  baseline PR-AUC = {obs_pr_auc:.4f}")
    print(f"  top 5 metros whose removal drops PR-AUC the most:")
    for m, pr, d in impacts[:5]:
        title = crashed[crashed["cbsa_code"] == m]["cbsa_title"].iloc[0]
        print(f"    {m} {title[:40]:40s}  PR-AUC={pr:.4f}  drop={d:+.1%}", flush=True)
    worst_drop = impacts[0][2]
    append_result(Result(
        exp_id="RV-5",
        description=f"LOMO: max PR-AUC drop from removing single metro = {worst_drop:.1%}",
        n_test=len(test), pos_rate_test=base_rate_te,
        pr_auc=obs_pr_auc,
        pr_auc_lift_over_base=worst_drop,  # overloaded: drop ratio
        status="REVIEW",
    ))

    # --- RV-2: within-metro block-permutation null ---
    print("\n[RV-2] Metro-block permutation null (500 perms)", flush=True)
    rng = np.random.default_rng(17)
    metro_has_crash = train.groupby("cbsa_code")["crash_next_12mo"].any()
    crash_labels = metro_has_crash.values.astype(int)
    cbsas = metro_has_crash.index.values
    perm_prs = []
    for b in range(500):
        shuffled = rng.permutation(crash_labels)
        mapping = dict(zip(cbsas, shuffled))
        tr2 = train.copy()
        # For each row: keep its original crash label ONLY if its metro was drawn
        # as "crash metro" — else zero it.
        tr2["crash_next_12mo"] = (tr2["crash_next_12mo"].values
                                    * tr2["cbsa_code"].map(mapping).fillna(0).astype(int).values)
        if tr2["crash_next_12mo"].sum() < 3:
            continue
        prob2, _, _, _, _ = fit_l2(tr2, test, feats)
        perm_prs.append(float(average_precision_score(y_te, prob2)))
        if (b + 1) % 100 == 0:
            print(f"    ... {b+1}/500 done", flush=True)
    perm_prs = np.array(perm_prs)
    p_block = float((perm_prs >= obs_pr_auc).mean())
    print(f"  observed PR-AUC = {obs_pr_auc:.4f}", flush=True)
    print(f"  block-perm mean = {perm_prs.mean():.4f}  (n_valid={len(perm_prs)})", flush=True)
    print(f"  block-perm p-value = {p_block:.4f}", flush=True)
    append_result(Result(
        exp_id="RV-2",
        description=f"Metro-block-permutation null p-value = {p_block:.4f} ({len(perm_prs)} perms)",
        n_test=len(test), pos_rate_test=base_rate_te,
        pr_auc=obs_pr_auc,
        pr_auc_lift_over_base=p_block,  # overloaded: p-value
        status="REVIEW",
    ))

    print("\n=== Phase 2.75 mandatory follow-ups complete ===", flush=True)


if __name__ == "__main__":
    main()
