"""Evaluation harness: temporal split + rare-event metrics."""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, brier_score_loss,
                              log_loss, roc_auc_score)

HERE = Path(__file__).parent
RESULTS_TSV = HERE / "results.tsv"

COLS = ["timestamp", "exp_id", "description",
        "n_train", "n_test", "pos_rate_train", "pos_rate_test",
        "roc_auc", "pr_auc", "pr_auc_lift_over_base",
        "brier", "log_loss", "top_k_precision", "top_k_k",
        "status"]


@dataclass
class Result:
    exp_id: str
    description: str
    n_train: int = 0
    n_test: int = 0
    pos_rate_train: float = 0.0
    pos_rate_test: float = 0.0
    roc_auc: float = float("nan")
    pr_auc: float = float("nan")
    pr_auc_lift_over_base: float = float("nan")
    brier: float = float("nan")
    log_loss: float = float("nan")
    top_k_precision: float = float("nan")
    top_k_k: int = 0
    status: str = "RUN"


def ensure():
    if not RESULTS_TSV.exists():
        with RESULTS_TSV.open("w", newline="") as fh:
            csv.writer(fh, delimiter="\t").writerow(COLS)


def append_result(r: Result):
    ensure()
    with RESULTS_TSV.open("a", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow([
            dt.datetime.now().isoformat(timespec="seconds"),
            r.exp_id, r.description,
            r.n_train, r.n_test,
            f"{r.pos_rate_train:.4f}", f"{r.pos_rate_test:.4f}",
            f"{r.roc_auc:.4f}" if not np.isnan(r.roc_auc) else "nan",
            f"{r.pr_auc:.4f}" if not np.isnan(r.pr_auc) else "nan",
            f"{r.pr_auc_lift_over_base:.3f}" if not np.isnan(r.pr_auc_lift_over_base) else "nan",
            f"{r.brier:.4f}" if not np.isnan(r.brier) else "nan",
            f"{r.log_loss:.4f}" if not np.isnan(r.log_loss) else "nan",
            f"{r.top_k_precision:.4f}" if not np.isnan(r.top_k_precision) else "nan",
            r.top_k_k, r.status,
        ])


def classifier_metrics(y_true, y_prob, k_frac: float = 0.05) -> dict:
    base_rate = float(np.mean(y_true))
    pr_auc = float(average_precision_score(y_true, y_prob)) if base_rate > 0 else float("nan")
    roc = float(roc_auc_score(y_true, y_prob)) if base_rate > 0 else float("nan")
    brier = float(brier_score_loss(y_true, y_prob))
    ll = float(log_loss(y_true, np.clip(y_prob, 1e-6, 1 - 1e-6)))
    # Top-k precision: precision in the top k_frac of predicted probabilities
    k = max(1, int(k_frac * len(y_true)))
    top_idx = np.argsort(-y_prob)[:k]
    top_prec = float(np.mean(y_true[top_idx]))
    return {
        "roc_auc": roc, "pr_auc": pr_auc,
        "pr_auc_lift_over_base": pr_auc / base_rate if base_rate > 0 else float("nan"),
        "brier": brier, "log_loss": ll,
        "top_k_precision": top_prec, "top_k_k": k,
        "base_rate": base_rate,
    }
