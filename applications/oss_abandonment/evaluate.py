"""Phase 0.5 entrypoint: load cached GH Archive data, build features, train E00 baseline.

Usage:
    python evaluate.py                  # full pipeline
    python evaluate.py --build-panel    # just aggregate raw files -> panel
    python evaluate.py --train-only     # assume panel already cached
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from data_loaders import aggregate_hour, agg_to_dataframe
from model import FEATURES, build_observation_table, train_baseline


HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
PANEL = HERE / "data" / "panel.parquet"
OBS = HERE / "data" / "observations.parquet"
RESULTS = HERE / "results.tsv"

PRIOR_DATES = ["2024-04-01", "2024-04-03", "2024-04-05"]
FORWARD_DATES = ["2025-04-01", "2025-04-03", "2025-04-05"]


def build_panel(force: bool = False) -> pd.DataFrame:
    if PANEL.exists() and not force:
        print(f"Loading cached panel from {PANEL}", flush=True)
        return pd.read_parquet(PANEL)

    files = sorted(RAW.glob("*.json.gz"))
    print(f"Aggregating {len(files)} hourly files...", flush=True)
    agg: dict[tuple, object] = {}
    t0 = time.time()
    for i, f in enumerate(files, 1):
        aggregate_hour(f, agg)
        if i % 12 == 0:
            print(f"  {i}/{len(files)}  {(time.time()-t0)/60:.1f}m  repos so far={len(agg)}", flush=True)
    print(f"Total (repo, date) rows: {len(agg)}", flush=True)
    df = agg_to_dataframe(agg)
    PANEL.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PANEL)
    print(f"Saved panel {PANEL} ({len(df)} rows)", flush=True)
    return df


def append_result(row: dict):
    """Append one experiment result row to results.tsv (creating header if needed)."""
    header = "exp_id\tdescription\tpr_auc\tpr_auc_lo\tpr_auc_hi\troc_auc\tbrier\tprec_at_top10pct\tn_train\tn_test\tn_pos_test\tbase_rate_test\tstatus\n"
    exists = RESULTS.exists() and RESULTS.stat().st_size > 0
    with open(RESULTS, "a") as fh:
        if not exists:
            fh.write(header)
        fh.write(
            f"{row['exp_id']}\t{row['description']}\t"
            f"{row['pr_auc']:.4f}\t{row['pr_auc_lo']:.4f}\t{row['pr_auc_hi']:.4f}\t"
            f"{row['roc_auc']:.4f}\t{row['brier']:.4f}\t{row['prec_at_top10pct']:.4f}\t"
            f"{row['n_train']}\t{row['n_test']}\t{row['n_pos_test']}\t"
            f"{row['base_rate_test']:.4f}\t{row['status']}\n"
        )


def main(args):
    panel = build_panel(force=args.rebuild_panel)
    if args.build_panel:
        return

    obs = build_observation_table(panel, PRIOR_DATES, FORWARD_DATES)
    print(f"Observation table: {len(obs)} repos active in prior window", flush=True)
    print(f"  Base rate (abandoned): {obs['label_abandoned'].mean():.3f}", flush=True)
    obs.to_parquet(OBS)

    print("\nTraining E00 baseline (XGBoost)...", flush=True)
    res, booster, d_train, d_test = train_baseline(obs, features=FEATURES)
    print(f"  PR-AUC: {res.pr_auc:.4f} [{res.pr_auc_lo:.4f}, {res.pr_auc_hi:.4f}]", flush=True)
    print(f"  ROC-AUC: {res.roc_auc:.4f}", flush=True)
    print(f"  Brier: {res.brier:.4f}", flush=True)
    print(f"  Prec@top10%: {res.prec_at_top10pct:.4f}", flush=True)
    print(f"  n_train={res.n_train}  n_test={res.n_test}  n_pos_test={res.n_pos_test}  "
          f"base_rate_test={res.base_rate_test:.3f}", flush=True)

    append_result({
        "exp_id": "E00",
        "description": "Baseline XGBoost on 18 features (prior=3d 2024-04, forward=3d 2025-04)",
        "pr_auc": res.pr_auc, "pr_auc_lo": res.pr_auc_lo, "pr_auc_hi": res.pr_auc_hi,
        "roc_auc": res.roc_auc, "brier": res.brier,
        "prec_at_top10pct": res.prec_at_top10pct,
        "n_train": res.n_train, "n_test": res.n_test,
        "n_pos_test": res.n_pos_test, "base_rate_test": res.base_rate_test,
        "status": "BASELINE",
    })
    print(f"\nLogged E00 to {RESULTS}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-panel", action="store_true")
    ap.add_argument("--rebuild-panel", action="store_true")
    ap.add_argument("--train-only", action="store_true")
    args = ap.parse_args()
    main(args)
