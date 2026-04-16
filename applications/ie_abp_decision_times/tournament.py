"""
Phase 1 — Tournament. Five analytical families fit to the ABP decision-time
series, evaluated on mean-absolute-error (MAE) against observed mean weeks-
to-dispose 2015-2024. Every family gets a row in tournament_results.csv
and in results.tsv (T01-T05).

Families:
  T01 — Year-fixed-effects (linear trend on year)
  T02 — Interrupted time series with knots at 2018 (Plean-IT), 2022 (crisis),
         2023 (crisis tail). Dummies + linear year.
  T03 — Capacity / Little's-law fit: W = β0 + β1 × on_hand_start / intake
  T04 — M/M/1 heavy-traffic: W = 1 / (μ - λ); μ proxied by disposed/52 (cases/wk),
         λ proxied by received/52. Closed-form prediction.
  T05 — Case-type fixed-effects OLS on (year, case_type) panel.

All four model families share the same evaluation: MAE on observed mean-weeks
-to-dispose, all-cases (T01-T04) or case-type-specific (T05).
"""

from __future__ import annotations

import csv
import numpy as np
from pathlib import Path

from analysis import ANNUAL, INTAKE, FTE, append_result_row

PROJECT_ROOT = Path(__file__).resolve().parent
TOURN = PROJECT_ROOT / "tournament_results.csv"


def _years_with_intake() -> list[int]:
    return sorted(y for y in INTAKE if INTAKE[y]["intake"] is not None)


def _yearvec() -> tuple[np.ndarray, np.ndarray]:
    ys = sorted(ANNUAL.keys())
    w = np.array([ANNUAL[y][4] for y in ys], dtype=float)
    return np.array(ys, dtype=float), w


def t01_linear_year() -> tuple[float, np.ndarray, np.ndarray]:
    """T01 linear OLS of mean-weeks on year."""
    yrs, w = _yearvec()
    X = np.column_stack([np.ones_like(yrs), yrs - 2020])
    beta, *_ = np.linalg.lstsq(X, w, rcond=None)
    pred = X @ beta
    mae = float(np.mean(np.abs(pred - w)))
    return mae, pred, w


def t02_interrupted_ts() -> tuple[float, np.ndarray, np.ndarray]:
    """T02 ITS with knots at 2018, 2022, 2023."""
    yrs, w = _yearvec()
    post2018 = (yrs >= 2018).astype(float)
    post2022 = (yrs >= 2022).astype(float)
    post2023 = (yrs >= 2023).astype(float)
    X = np.column_stack(
        [np.ones_like(yrs), yrs - 2020, post2018, post2022, post2023]
    )
    beta, *_ = np.linalg.lstsq(X, w, rcond=None)
    pred = X @ beta
    mae = float(np.mean(np.abs(pred - w)))
    return mae, pred, w


def t03_littles_law() -> tuple[float, np.ndarray, np.ndarray]:
    """T03 W = β0 + β1 × (on_hand_start / intake) × 52. Fit 2019-2024."""
    yrs = [y for y in _years_with_intake() if y in ANNUAL]
    w = np.array([ANNUAL[y][4] for y in yrs], dtype=float)
    # Little's-law-style proxy: L / λ (weeks)
    x = np.array(
        [INTAKE[y]["on_hand_start"] / (INTAKE[y]["intake"] / 52.0) for y in yrs],
        dtype=float,
    )
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, w, rcond=None)
    pred = X @ beta
    mae = float(np.mean(np.abs(pred - w)))
    return mae, pred, w


def t04_mm1_heavy_traffic() -> tuple[float, np.ndarray, np.ndarray]:
    """T04 M/M/1 closed-form: W = 1 / (μ - λ), μ = disposed/52, λ = received/52 (cases/wk)."""
    yrs = [y for y in _years_with_intake() if y in ANNUAL]
    w = np.array([ANNUAL[y][4] for y in yrs], dtype=float)
    preds = []
    for y in yrs:
        mu = INTAKE[y]["disposed"] / 52.0
        lam = INTAKE[y]["intake"] / 52.0
        # Guard against μ ≤ λ (unstable queue) by returning a capped 260 weeks.
        if mu <= lam:
            preds.append(260.0)
        else:
            preds.append(1.0 / (mu - lam))
    pred = np.array(preds)
    mae = float(np.mean(np.abs(pred - w)))
    return mae, pred, w


def t05_case_type_fe() -> tuple[float, np.ndarray, np.ndarray]:
    """T05 case-type × year fixed-effects OLS panel.
    y = α_year + γ_type + ε. Metric: MAE across the 40-cell panel."""
    types = ["NPA", "SID", "SHD", "OTHER"]
    obs = []
    yr_ix = []
    type_ix = []
    for y, tup in sorted(ANNUAL.items()):
        for i, v in enumerate(tup[:4]):
            if v is not None:
                obs.append(v)
                yr_ix.append(y)
                type_ix.append(i)
    obs = np.array(obs, dtype=float)
    yr_ix = np.array(yr_ix)
    type_ix = np.array(type_ix)
    # one-hot encode year and case-type
    uy = sorted(set(yr_ix))
    X_year = np.zeros((len(obs), len(uy)))
    for i, y in enumerate(yr_ix):
        X_year[i, uy.index(y)] = 1.0
    X_type = np.zeros((len(obs), len(types)))
    for i, t in enumerate(type_ix):
        X_type[i, t] = 1.0
    X = np.column_stack([X_year, X_type[:, 1:]])  # drop first case-type dummy
    beta, *_ = np.linalg.lstsq(X, obs, rcond=None)
    pred = X @ beta
    mae = float(np.mean(np.abs(pred - obs)))
    return mae, pred, obs


def main() -> None:
    families = [
        ("T01", "linear_year_ols", t01_linear_year, "mean-weeks ~ year"),
        ("T02", "interrupted_ts", t02_interrupted_ts,
         "mean-weeks ~ year + post2018 + post2022 + post2023"),
        ("T03", "littles_law", t03_littles_law,
         "mean-weeks ~ (on-hand-start / intake) × 52"),
        ("T04", "mm1_heavy_traffic", t04_mm1_heavy_traffic,
         "W = 1/(μ-λ) closed-form"),
        ("T05", "case_type_fe_panel", t05_case_type_fe,
         "panel OLS on year × case-type"),
    ]
    with TOURN.open("w", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["exp_id", "family", "description", "MAE_weeks", "n_obs"])
        for exp_id, name, fn, desc in families:
            mae, pred, obs = fn()
            writer.writerow([exp_id, name, desc, f"{mae:.2f}", len(obs)])
            append_result_row(
                exp_id=exp_id,
                family=name,
                description=desc,
                metric="MAE_weeks",
                value=f"{mae:.2f}",
                status="TOURNAMENT",
                notes=f"n={len(obs)} observations",
            )
    print(f"Wrote {TOURN}")
    # also print a readable ranking
    print("\nRanking (lower MAE = better):")
    with TOURN.open() as fp:
        rows = list(csv.DictReader(fp))
    rows.sort(key=lambda r: float(r["MAE_weeks"]))
    for r in rows:
        print(f"  {r['exp_id']} {r['family']:22s} MAE={r['MAE_weeks']:>6}  n={r['n_obs']}")


if __name__ == "__main__":
    main()
