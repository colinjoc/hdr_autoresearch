"""Phase 2 HDR-loop runner: execute pre-registered experiments from research_queue.md,
each as a single-change variant of E00, and log to results.tsv.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from evaluate import append_result
from model import FEATURES, build_observation_table, train_baseline


HERE = Path(__file__).parent
PANEL = HERE / "data" / "panel.parquet"
PRIOR_DATES = ["2024-04-01", "2024-04-03", "2024-04-05"]
FORWARD_DATES = ["2025-04-01", "2025-04-03", "2025-04-05"]


def run_experiment(exp_id: str, description: str,
                   panel_transform: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
                   obs_transform: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
                   features: list[str] | None = None,
                   xgb_params: dict | None = None,
                   prior_dates: list[str] | None = None,
                   forward_dates: list[str] | None = None,
                   status: str = "RUN"):
    """Run a single experiment variant and log to results.tsv."""
    panel = pd.read_parquet(PANEL)
    if panel_transform:
        panel = panel_transform(panel)
    obs = build_observation_table(panel,
                                  prior_dates or PRIOR_DATES,
                                  forward_dates or FORWARD_DATES)
    if obs_transform:
        obs = obs_transform(obs)
    feats = features or FEATURES
    # Drop rows with missing features
    obs = obs.dropna(subset=feats)
    if len(obs) == 0:
        print(f"{exp_id}: 0 rows after filter — skip")
        return None
    res, _, _, _ = train_baseline(obs, features=feats, xgb_params=xgb_params)
    print(f"{exp_id:5s} {description:70s} "
          f"PR={res.pr_auc:.4f} ROC={res.roc_auc:.4f} Br={res.brier:.4f} "
          f"P@10={res.prec_at_top10pct:.4f} n={res.n_test} bpos={res.base_rate_test:.3f}",
          flush=True)
    append_result({
        "exp_id": exp_id, "description": description,
        "pr_auc": res.pr_auc, "pr_auc_lo": res.pr_auc_lo, "pr_auc_hi": res.pr_auc_hi,
        "roc_auc": res.roc_auc, "brier": res.brier,
        "prec_at_top10pct": res.prec_at_top10pct,
        "n_train": res.n_train, "n_test": res.n_test, "n_pos_test": res.n_pos_test,
        "base_rate_test": res.base_rate_test, "status": status,
    })
    return res


def obs_tighter_prior(obs: pd.DataFrame) -> pd.DataFrame:
    # Require ≥5 human commits in prior window (vs 1 in baseline)
    return obs[obs["human_commits_prior"] >= 5].copy()


def obs_require_distinct_authors(obs: pd.DataFrame) -> pd.DataFrame:
    return obs[obs["distinct_authors_prior"] >= 2].copy()


def obs_relabel_activity_drop(obs: pd.DataFrame, drop_threshold: float = 0.1) -> pd.DataFrame:
    """Relabel: abandoned iff forward_commits / prior_commits < drop_threshold."""
    ratio = obs["human_commits_forward"] / (obs["human_commits_prior"] + 1)
    obs = obs.copy()
    obs["label_abandoned"] = (ratio < drop_threshold).astype(int)
    return obs


def obs_drop_bot_dominated(obs: pd.DataFrame) -> pd.DataFrame:
    return obs[obs["bot_human_ratio"] < 2.0].copy()


def main():
    print("=== Phase 2 HDR loop (single-change experiments) ===", flush=True)

    # E01: log1p + log1p of forks/stars (noise features)
    run_experiment(
        "E01",
        "Add log1p_stars, log1p_forks as features (H8 family)",
        obs_transform=lambda o: o.assign(
            log1p_stars=np.log1p(o["stars_prior"]),
            log1p_forks=np.log1p(o["forks_prior"]),
        ),
        features=FEATURES + ["log1p_stars", "log1p_forks"],
        status="KEEP_CANDIDATE",
    )

    # E02: tighter prior filter (≥5 human commits)
    run_experiment(
        "E02", "Tighter prior filter: require >=5 human commits in 3d window",
        obs_transform=obs_tighter_prior,
        status="KEEP_CANDIDATE",
    )

    # E03: require ≥2 distinct authors (filters solo hobby repos)
    run_experiment(
        "E03", "Require >=2 distinct authors in prior (filter solo hobby)",
        obs_transform=obs_require_distinct_authors,
        status="KEEP_CANDIDATE",
    )

    # E04: relabel as activity-drop (new target)
    run_experiment(
        "E04", "Relabel: abandoned iff fwd/prior ratio < 0.1 (G-family)",
        obs_transform=lambda o: obs_relabel_activity_drop(o, 0.1),
        status="KEEP_CANDIDATE",
    )

    # E05: drop bot-dominated repos
    run_experiment(
        "E05", "Drop bot_human_ratio>=2 (human-dominated repos only)",
        obs_transform=obs_drop_bot_dominated,
        status="KEEP_CANDIDATE",
    )

    # E06: max_depth 4 (I1 — regularization)
    run_experiment(
        "E06", "max_depth 6->4 (regularize)",
        xgb_params={"max_depth": 4},
        status="KEEP_CANDIDATE",
    )

    # E07: learning_rate 0.03 (I2)
    run_experiment(
        "E07", "learning_rate 0.05->0.03 (slower descent)",
        xgb_params={"learning_rate": 0.03},
        status="KEEP_CANDIDATE",
    )

    # E08: drop weakest features (keep only activity + distinct_authors)
    run_experiment(
        "E08", "Feature subset: activity + distinct_authors only (6 features)",
        features=["human_commits_prior", "log1p_human_commits_prior",
                  "distinct_authors_prior", "days_active_prior",
                  "issues_opened_prior", "prs_opened_prior"],
        status="KEEP_CANDIDATE",
    )

    # E09: combine tighter prior + activity-drop relabel
    run_experiment(
        "E09", "E02 + E04 combined: tighter prior AND activity-drop label",
        obs_transform=lambda o: obs_relabel_activity_drop(obs_tighter_prior(o), 0.1),
        status="KEEP_CANDIDATE",
    )

    # E10: commit-to-author ratio feature (concentration signal)
    run_experiment(
        "E10", "Add commits_per_author ratio feature (B1 proxy)",
        obs_transform=lambda o: o.assign(
            commits_per_author=o["human_commits_prior"] / o["distinct_authors_prior"].clip(lower=1),
        ),
        features=FEATURES + ["commits_per_author"],
        status="KEEP_CANDIDATE",
    )

    # --- Phase 2b: build on E02 (new champion, ROC 0.8607) ---
    # E11: E02 + even tighter prior (≥10 commits)
    run_experiment(
        "E11", "Tighter prior: >=10 human commits in 3d (vs 5 in E02)",
        obs_transform=lambda o: o[o["human_commits_prior"] >= 10].copy(),
        status="KEEP_CANDIDATE",
    )

    # E12: E02 + commits_per_author feature
    run_experiment(
        "E12", "E02 + commits_per_author feature",
        obs_transform=lambda o: obs_tighter_prior(o).assign(
            commits_per_author=lambda d: d["human_commits_prior"] / d["distinct_authors_prior"].clip(lower=1),
        ),
        features=FEATURES + ["commits_per_author"],
        status="KEEP_CANDIDATE",
    )

    # E13: E02 + log1p_stars / log1p_forks
    run_experiment(
        "E13", "E02 + log1p_stars + log1p_forks",
        obs_transform=lambda o: obs_tighter_prior(o).assign(
            log1p_stars=lambda d: np.log1p(d["stars_prior"]),
            log1p_forks=lambda d: np.log1p(d["forks_prior"]),
        ),
        features=FEATURES + ["log1p_stars", "log1p_forks"],
        status="KEEP_CANDIDATE",
    )

    # E14: E02 + issue/pr engagement ratios
    run_experiment(
        "E14", "E02 + engagement ratios (commits_per_issue, merge_rate already in)",
        obs_transform=lambda o: obs_tighter_prior(o).assign(
            commits_per_issue=lambda d: d["human_commits_prior"] / (d["issues_opened_prior"] + 1),
            prs_per_issue=lambda d: d["prs_opened_prior"] / (d["issues_opened_prior"] + 1),
        ),
        features=FEATURES + ["commits_per_issue", "prs_per_issue"],
        status="KEEP_CANDIDATE",
    )

    # E15: E02 + scale_pos_weight off (test: does class rebalancing help?)
    run_experiment(
        "E15", "E02 + scale_pos_weight=1 (no rebalancing)",
        obs_transform=obs_tighter_prior,
        xgb_params={"scale_pos_weight": 1.0},
        status="KEEP_CANDIDATE",
    )


if __name__ == "__main__":
    main()
