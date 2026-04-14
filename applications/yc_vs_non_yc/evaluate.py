"""Evaluation harness for the YC vs non-YC baseline.

Metrics:
- Outcome classification: ROC-AUC, PR-AUC, Brier, log-loss.
- Treatment-effect:
  - Unconditional diff-of-means (risk difference) with 95% CI.
  - Paired bootstrap on sector×quarter-matched pairs.
  - Rosenbaum-style sensitivity in Phase 2 (not here).

Logs results to results.tsv with append semantics so the HDR loop can stream.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import (brier_score_loss, log_loss,
                              precision_recall_curve, roc_auc_score,
                              average_precision_score)

HERE = Path(__file__).parent
RESULTS_TSV = HERE / "results.tsv"

RESULT_COLS = [
    "timestamp", "exp_id", "description",
    "n_treated", "n_control",
    "rate_treated", "rate_control",
    "risk_diff", "rd_ci_lo", "rd_ci_hi",
    "roc_auc", "pr_auc", "brier", "log_loss",
    "n_train", "n_test",
    "status",
]


@dataclass
class ExperimentResult:
    exp_id: str
    description: str
    n_treated: int = 0
    n_control: int = 0
    rate_treated: float = float("nan")
    rate_control: float = float("nan")
    risk_diff: float = float("nan")
    rd_ci_lo: float = float("nan")
    rd_ci_hi: float = float("nan")
    roc_auc: float = float("nan")
    pr_auc: float = float("nan")
    brier: float = float("nan")
    log_loss: float = float("nan")
    n_train: int = 0
    n_test: int = 0
    status: str = "RUN"


def ensure_results_file():
    if not RESULTS_TSV.exists():
        with RESULTS_TSV.open("w", newline="") as fh:
            csv.writer(fh, delimiter="\t").writerow(RESULT_COLS)


def append_result(r: ExperimentResult):
    ensure_results_file()
    with RESULTS_TSV.open("a", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow([
            dt.datetime.now().isoformat(timespec="seconds"),
            r.exp_id, r.description,
            r.n_treated, r.n_control,
            f"{r.rate_treated:.4f}", f"{r.rate_control:.4f}",
            f"{r.risk_diff:+.4f}", f"{r.rd_ci_lo:+.4f}", f"{r.rd_ci_hi:+.4f}",
            f"{r.roc_auc:.4f}" if not np.isnan(r.roc_auc) else "nan",
            f"{r.pr_auc:.4f}" if not np.isnan(r.pr_auc) else "nan",
            f"{r.brier:.4f}" if not np.isnan(r.brier) else "nan",
            f"{r.log_loss:.4f}" if not np.isnan(r.log_loss) else "nan",
            r.n_train, r.n_test,
            r.status,
        ])


def risk_diff_with_ci(y_treat: Sequence[int], y_ctrl: Sequence[int],
                     n_boot: int = 2000, seed: int = 17) -> tuple[float, float, float]:
    """Return (risk_diff, ci_lo, ci_hi). risk_diff = E[Y|T=1] - E[Y|T=0]."""
    rng = np.random.default_rng(seed)
    y_t = np.asarray(y_treat)
    y_c = np.asarray(y_ctrl)
    rd = y_t.mean() - y_c.mean()
    n_t, n_c = len(y_t), len(y_c)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        bt = rng.choice(y_t, size=n_t, replace=True)
        bc = rng.choice(y_c, size=n_c, replace=True)
        boots[b] = bt.mean() - bc.mean()
    return rd, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def classifier_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    return {
        "roc_auc": roc_auc_score(y_true, y_prob),
        "pr_auc": average_precision_score(y_true, y_prob),
        "brier": brier_score_loss(y_true, y_prob),
        "log_loss": log_loss(y_true, np.clip(y_prob, 1e-6, 1 - 1e-6)),
    }
