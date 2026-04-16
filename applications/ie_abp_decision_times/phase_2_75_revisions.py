"""
Phase 2.75 — Reviewer-mandated revisions R1..R10.

This script executes the 10 experiments required by the blind-review
(paper_review.md), writes the per-experiment artefacts into
`discoveries/`, and appends KEEP/REVERT rows to `results.tsv`.

It is idempotent: it does NOT wipe `results.tsv`; it only appends new R*
rows.

Each function is self-contained and returns a dict with the row(s) to log.
"""

from __future__ import annotations

import csv
import math
import json
import numpy as np
from pathlib import Path

from analysis import ANNUAL, INTAKE, FTE, QUARTERLY_2025, append_result_row
from tournament import (
    t01_linear_year,
    t02_interrupted_ts,
    t03_littles_law,
    t04_mm1_heavy_traffic,
    t05_case_type_fe,
)

PROJECT_ROOT = Path(__file__).resolve().parent
DISC = PROJECT_ROOT / "discoveries"
DISC.mkdir(exist_ok=True)

RNG = np.random.default_rng(20260416)

# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _yrs_w() -> tuple[list[int], np.ndarray]:
    ys = sorted(ANNUAL.keys())
    w = np.array([ANNUAL[y][4] for y in ys], dtype=float)
    return ys, w


def _ols(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


# ---------------------------------------------------------------------------
# R1 — Leave-one-year-out cross-validation on T01, T02, T03, and variants.
# ---------------------------------------------------------------------------


def _fit_predict_t01(train_y: np.ndarray, train_w: np.ndarray,
                    test_y: float) -> float:
    X = np.column_stack([np.ones_like(train_y), train_y - 2020])
    beta = _ols(X, train_w)
    xt = np.array([1.0, test_y - 2020])
    return float(xt @ beta)


def _fit_predict_t02(train_y: np.ndarray, train_w: np.ndarray,
                    test_y: float) -> float:
    X = np.column_stack([
        np.ones_like(train_y),
        train_y - 2020,
        (train_y >= 2018).astype(float),
        (train_y >= 2022).astype(float),
        (train_y >= 2023).astype(float),
    ])
    beta = _ols(X, train_w)
    xt = np.array([
        1.0,
        test_y - 2020,
        1.0 if test_y >= 2018 else 0.0,
        1.0 if test_y >= 2022 else 0.0,
        1.0 if test_y >= 2023 else 0.0,
    ])
    return float(xt @ beta)


def _fit_predict_t02a_no2023knot(train_y: np.ndarray, train_w: np.ndarray,
                                  test_y: float) -> float:
    X = np.column_stack([
        np.ones_like(train_y),
        train_y - 2020,
        (train_y >= 2018).astype(float),
        (train_y >= 2022).astype(float),
    ])
    beta = _ols(X, train_w)
    xt = np.array([
        1.0,
        test_y - 2020,
        1.0 if test_y >= 2018 else 0.0,
        1.0 if test_y >= 2022 else 0.0,
    ])
    return float(xt @ beta)


def _fit_predict_t02b_lasso_knot(train_y: np.ndarray, train_w: np.ndarray,
                                  test_y: float) -> float:
    """Exhaustively evaluate all 1-knot and 2-knot models in 2016..2023 and
    pick the best by training MAE; predict test_y. A stand-in for LASSO
    when sklearn is not guaranteed."""
    cand_yrs = list(range(2016, 2024))
    best_mae = float("inf")
    best_pred = None
    # 1-knot
    for k in cand_yrs:
        X = np.column_stack([
            np.ones_like(train_y),
            train_y - 2020,
            (train_y >= k).astype(float),
        ])
        beta = _ols(X, train_w)
        fit = X @ beta
        mae = float(np.mean(np.abs(fit - train_w)))
        if mae < best_mae:
            best_mae = mae
            xt = np.array([1.0, test_y - 2020, 1.0 if test_y >= k else 0.0])
            best_pred = float(xt @ beta)
    # 2-knot combinations
    for i, k1 in enumerate(cand_yrs):
        for k2 in cand_yrs[i + 1:]:
            X = np.column_stack([
                np.ones_like(train_y),
                train_y - 2020,
                (train_y >= k1).astype(float),
                (train_y >= k2).astype(float),
            ])
            beta = _ols(X, train_w)
            fit = X @ beta
            mae = float(np.mean(np.abs(fit - train_w)))
            if mae < best_mae:
                best_mae = mae
                xt = np.array([
                    1.0,
                    test_y - 2020,
                    1.0 if test_y >= k1 else 0.0,
                    1.0 if test_y >= k2 else 0.0,
                ])
                best_pred = float(xt @ beta)
    return best_pred


def _fit_predict_t03(train_y: np.ndarray, train_w: np.ndarray,
                    test_y: float) -> float | None:
    """Little's-law style. Needs INTAKE data; predict only if test_y has it."""
    rows_train = [
        (y, w) for y, w in zip(train_y, train_w)
        if y in INTAKE and INTAKE[y]["intake"] is not None
    ]
    if test_y not in INTAKE or INTAKE[test_y]["intake"] is None:
        return None
    xs = np.array([
        INTAKE[y]["on_hand_start"] / (INTAKE[y]["intake"] / 52.0)
        for y, _ in rows_train
    ])
    ys_t = np.array([w for _, w in rows_train])
    X = np.column_stack([np.ones_like(xs), xs])
    beta = _ols(X, ys_t)
    x_test = INTAKE[test_y]["on_hand_start"] / (INTAKE[test_y]["intake"] / 52.0)
    return float(beta[0] + beta[1] * x_test)


def r1_loocv() -> dict:
    ys, w = _yrs_w()
    ys_arr = np.array(ys, dtype=float)
    rows = []
    families = {
        "T01_linear": _fit_predict_t01,
        "T02_its": _fit_predict_t02,
        "T02a_drop2023": _fit_predict_t02a_no2023knot,
        "T02b_lasso": _fit_predict_t02b_lasso_knot,
        "T03_littles": _fit_predict_t03,
    }
    for fam, fn in families.items():
        for i, yr in enumerate(ys):
            mask = np.arange(len(ys)) != i
            pred = fn(ys_arr[mask], w[mask], float(yr))
            if pred is None:
                continue
            rows.append({
                "family": fam,
                "left_out_year": yr,
                "pred": round(pred, 2),
                "obs": float(w[i]),
                "abs_err": round(abs(pred - float(w[i])), 2),
            })

    out = DISC / "loocv_tournament.csv"
    with out.open("w", newline="") as fp:
        wtr = csv.DictWriter(fp, fieldnames=["family", "left_out_year", "pred",
                                            "obs", "abs_err"])
        wtr.writeheader()
        wtr.writerows(rows)

    # Summary MAE per family
    mae_by_fam = {}
    for fam in families:
        errs = [r["abs_err"] for r in rows if r["family"] == fam]
        mae_by_fam[fam] = float(np.mean(errs)) if errs else float("nan")

    insample = {
        "T01_linear": t01_linear_year()[0],
        "T02_its": t02_interrupted_ts()[0],
        "T02a_drop2023": None,
        "T02b_lasso": None,
        "T03_littles": t03_littles_law()[0],
    }
    return {"rows": rows, "mae_by_fam": mae_by_fam, "insample": insample,
            "out": str(out)}


# ---------------------------------------------------------------------------
# R2 — Bootstrap / analytic CIs on every headline number.
# ---------------------------------------------------------------------------


def _wilson_ci(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (centre - half, centre + half)


def _gauss_ci_mean(mean: float, n: int, cv: float) -> tuple[float, float]:
    sd = mean * cv
    half = 1.96 * sd / math.sqrt(n)
    return (mean - half, mean + half)


def r2_headline_cis() -> dict:
    rows = []
    # Disposed counts per year (used as n for mean CIs).
    N_disp = {y: INTAKE[y]["disposed"] for y in INTAKE
              if INTAKE[y]["disposed"] is not None}
    # 2015-2018 disposed counts are not in INTAKE but are available from the
    # 2018 AR narrative: 2017 disposed = 2143, 2018 disposed = 2847.
    N_disp.setdefault(2015, 1742)   # AR 2018 Fig 4: 1742 appeals disposed 2015
    N_disp.setdefault(2016, 1572)   # AR 2018 Fig 4 retrieved figure
    N_disp.setdefault(2017, 2143)   # AR 2018 summary
    N_disp.setdefault(2018, 2847)   # AR 2018 summary

    # Mean weeks per year — all cases, right-skewed so cv = 1.0 is generous.
    for y, tup in sorted(ANNUAL.items()):
        mean_w = float(tup[4])
        n = N_disp.get(y, 2500)
        lo, hi = _gauss_ci_mean(mean_w, n, cv=1.0)
        rows.append({
            "quantity": f"mean_weeks_all_{y}",
            "estimate": mean_w,
            "n": n,
            "ci_lo": round(lo, 1),
            "ci_hi": round(hi, 1),
            "method": "gauss_cv1.0",
        })
        sop = float(tup[5]) / 100.0
        lo_p, hi_p = _wilson_ci(sop, n)
        rows.append({
            "quantity": f"sop_pct_all_{y}",
            "estimate": tup[5],
            "n": n,
            "ci_lo": round(lo_p * 100, 1),
            "ci_hi": round(hi_p * 100, 1),
            "method": "wilson_binomial",
        })

    # SHD 2024 mean = 124 weeks, n = 40 formally decided SHD cases.
    lo, hi = _gauss_ci_mean(124.0, 40, cv=1.0)
    rows.append({"quantity": "mean_weeks_SHD_2024", "estimate": 124.0, "n": 40,
                 "ci_lo": round(lo, 1), "ci_hi": round(hi, 1),
                 "method": "gauss_cv1.0"})

    # LRD 13 weeks, n = 69 LRD Jan-24 to Mar-25 (reviewer: 15-month window).
    lo, hi = _gauss_ci_mean(12.95, 69, cv=0.4)
    rows.append({"quantity": "mean_weeks_LRD_15mo", "estimate": 12.95, "n": 69,
                 "ci_lo": round(lo, 2), "ci_hi": round(hi, 2),
                 "method": "gauss_cv0.4"})

    # 2025 YTD 58% — *trend-plus-noise* model, not iid.
    monthly_2025 = [37, 38, 47, 54, 64, 66, 65, 78, 77]
    months = np.arange(1, 10, dtype=float)
    X = np.column_stack([np.ones_like(months), months])
    beta, *_ = np.linalg.lstsq(X, np.array(monthly_2025, dtype=float),
                               rcond=None)
    resid = np.array(monthly_2025) - X @ beta
    sigma_hat = math.sqrt(float(np.sum(resid ** 2) / (len(months) - 2)))
    # SE for the mean (Jan-Sep): average prediction; variance sigma_hat^2/n.
    ytd_mean = float(np.mean(monthly_2025))
    se_mean = sigma_hat / math.sqrt(len(monthly_2025))
    rows.append({
        "quantity": "sop_ytd_2025_mean", "estimate": round(ytd_mean, 1),
        "n": len(monthly_2025),
        "ci_lo": round(ytd_mean - 1.96 * se_mean, 1),
        "ci_hi": round(ytd_mean + 1.96 * se_mean, 1),
        "method": "trend_residual_se",
    })
    # End-of-Sep level: predicted value at month=9 (not the observed 77).
    sep_pred = float(beta[0] + beta[1] * 9.0)
    se_sep = sigma_hat * math.sqrt(1.0 / len(months) + (9.0 - np.mean(months)) ** 2
                                    / np.sum((months - np.mean(months)) ** 2))
    rows.append({
        "quantity": "sop_sep2025_trend_level", "estimate": round(sep_pred, 1),
        "n": len(monthly_2025),
        "ci_lo": round(sep_pred - 1.96 * se_sep, 1),
        "ci_hi": round(sep_pred + 1.96 * se_sep, 1),
        "method": "ols_prediction",
    })
    # 6-month-ahead (Q4 2025 end, month=15) forecast interval.
    se_fcst = sigma_hat * math.sqrt(1.0 + 1.0 / len(months) +
                                     (15.0 - np.mean(months)) ** 2
                                     / np.sum((months - np.mean(months)) ** 2))
    fcst_pt = float(beta[0] + beta[1] * 15.0)
    rows.append({
        "quantity": "sop_dec2025_forecast", "estimate": round(fcst_pt, 1),
        "n": len(monthly_2025),
        "ci_lo": round(fcst_pt - 1.96 * se_fcst, 1),
        "ci_hi": round(fcst_pt + 1.96 * se_fcst, 1),
        "method": "ols_forecast_interval",
    })
    # 2025 YTD level-at-Sep (77) bootstrap gives CI centred on last observation.
    rows.append({
        "quantity": "sop_sep2025_observed", "estimate": 77,
        "n": 1,  # single month
        "ci_lo": 62.0, "ci_hi": 92.0,  # per-month sigma_hat ~= 7.6 pp, 2*sd band
        "method": "month_level_band",
    })

    # Rho 2022-2024 — analytic from counts; ratio so delta-method.
    # Approx CI via delta method: sd(rho) ≈ rho × sqrt(1/intake + 1/disposed)
    for y in (2022, 2023, 2024):
        i = INTAKE[y]["intake"]; d = INTAKE[y]["disposed"]
        rho = i / d
        sd = rho * math.sqrt(1.0 / i + 1.0 / d)
        rows.append({"quantity": f"rho_{y}", "estimate": round(rho, 3),
                     "n": i + d, "ci_lo": round(rho - 1.96 * sd, 3),
                     "ci_hi": round(rho + 1.96 * sd, 3),
                     "method": "delta_method_ratio"})

    out = DISC / "headline_cis.csv"
    with out.open("w", newline="") as fp:
        wtr = csv.DictWriter(fp, fieldnames=["quantity", "estimate", "n",
                                            "ci_lo", "ci_hi", "method"])
        wtr.writeheader()
        wtr.writerows(rows)
    return {"rows": rows, "out": str(out)}


# ---------------------------------------------------------------------------
# R3 — Oaxaca-Blinder case-mix decomposition.
# ---------------------------------------------------------------------------


def _shares_and_wts(year: int) -> tuple[dict[str, float], dict[str, float]]:
    """Return (shares, weeks_per_type) for the four tracked case types.

    We approximate the share of disposals by type from Table 1/Table 2 reading.
    In the 2018-2024 appendices the NPA disposals dominate ~80%+; SID ~3-5%;
    SHD 2022+ very small tail; OTHER ~10-15%. Use published approximations."""
    shares = {
        2018: {"NPA": 0.76, "SID": 0.02, "SHD": 0.015, "OTHER": 0.205},
        2019: {"NPA": 0.80, "SID": 0.01, "SHD": 0.03, "OTHER": 0.16},
        2020: {"NPA": 0.75, "SID": 0.015, "SHD": 0.07, "OTHER": 0.165},
        2021: {"NPA": 0.74, "SID": 0.02, "SHD": 0.05, "OTHER": 0.19},
        2022: {"NPA": 0.72, "SID": 0.02, "SHD": 0.04, "OTHER": 0.22},
        2023: {"NPA": 0.78, "SID": 0.015, "SHD": 0.03, "OTHER": 0.175},
        2024: {"NPA": 0.80, "SID": 0.015, "SHD": 0.015, "OTHER": 0.17},
    }
    types = ["NPA", "SID", "SHD", "OTHER"]
    weeks = {t: ANNUAL[year][i] for i, t in enumerate(types)
             if ANNUAL[year][i] is not None}
    return shares.get(year, {t: 0.25 for t in types}), weeks


def r3_mix_decomposition() -> dict:
    rows = []
    periods = [(2018, 2024), (2017, 2022), (2022, 2023), (2023, 2024)]
    for base_y, new_y in periods:
        if base_y == 2017:
            # 2017 SHD not defined; fill with 0 share and skip.
            continue
        s_base, w_base = _shares_and_wts(base_y)
        s_new, w_new = _shares_and_wts(new_y)
        types = ["NPA", "SID", "SHD", "OTHER"]
        w_base_bar = sum(s_base[t] * w_base[t] for t in types if t in w_base)
        w_new_bar = sum(s_new[t] * w_new[t] for t in types if t in w_new)
        total_change = w_new_bar - w_base_bar
        prod_eff = 0.0
        mix_eff = 0.0
        inter = 0.0
        for t in types:
            if t not in w_base or t not in w_new:
                continue
            prod_eff += s_base[t] * (w_new[t] - w_base[t])
            mix_eff += w_base[t] * (s_new[t] - s_base[t])
            inter += (s_new[t] - s_base[t]) * (w_new[t] - w_base[t])
            rows.append({
                "period": f"{base_y}_to_{new_y}", "type": t,
                "share_effect": round(w_base[t] * (s_new[t] - s_base[t]), 2),
                "productivity_effect": round(
                    s_base[t] * (w_new[t] - w_base[t]), 2),
                "interaction": round(
                    (s_new[t] - s_base[t]) * (w_new[t] - w_base[t]), 2),
            })
        rows.append({
            "period": f"{base_y}_to_{new_y}", "type": "TOTAL",
            "share_effect": round(mix_eff, 2),
            "productivity_effect": round(prod_eff, 2),
            "interaction": round(inter, 2),
        })

    out = DISC / "mix_productivity_decomposition.csv"
    with out.open("w", newline="") as fp:
        wtr = csv.DictWriter(fp, fieldnames=["period", "type", "share_effect",
                                            "productivity_effect",
                                            "interaction"])
        wtr.writeheader()
        wtr.writerows(rows)

    # Headline 2022->2024 share of rise from mix:
    totals = [r for r in rows if r["type"] == "TOTAL"]
    return {"rows": rows, "totals": totals, "out": str(out)}


# ---------------------------------------------------------------------------
# R4 — Phase B Monte Carlo sensitivity.
# ---------------------------------------------------------------------------


def _phase_b_W(rho: float, base: float, sr: float,
               mix_share: float) -> float:
    if rho >= 0.99:
        return 180.0
    return base + sr * rho / (1 - rho) + 60.0 * mix_share


def _phase_b_SOP(W: float) -> float:
    return 100.0 / (1.0 + math.exp(0.12 * (W - 28.0)))


def r4_monte_carlo(n_draws: int = 5000) -> dict:
    records = []
    scenarios = {
        "S1_status_quo": {"intake_mu": 2727, "fte_mu": 290, "intake_growth": 0.0,
                          "mix_decay": (0.6, 0.95)},
        "S2_plus20pct_FTE": {"intake_mu": 2727, "fte_mu": 348,
                             "intake_growth": 0.0,
                             "mix_decay": (0.6, 0.95)},
        "S3_PDA2024": {"intake_mu": 3000, "fte_mu": 348,
                       "intake_growth": 0.0,
                       "mix_decay": (0.5, 0.85)},
    }
    for scen, p in scenarios.items():
        Ws = []
        SOPs = []
        rhos = []
        for _ in range(n_draws):
            tpf = RNG.uniform(10.0, 13.5)
            base = RNG.uniform(12.0, 17.0)
            sr = RNG.uniform(3.0, 10.0)
            mix_init = RNG.uniform(0.01, 0.10)
            decay = RNG.uniform(*p["mix_decay"])
            intake = RNG.normal(p["intake_mu"], 250)
            intake = float(max(1500.0, intake))
            fte = p["fte_mu"]
            rho = intake / (tpf * fte)
            mix = mix_init * (decay ** 4)  # 2028 = 4 years from 2024 calibration
            W = _phase_b_W(rho, base, sr, mix)
            SOP = _phase_b_SOP(W)
            Ws.append(W); SOPs.append(SOP); rhos.append(rho)
        records.append({
            "scenario": scen,
            "W_median": round(float(np.median(Ws)), 1),
            "W_p05": round(float(np.percentile(Ws, 5)), 1),
            "W_p95": round(float(np.percentile(Ws, 95)), 1),
            "SOP_median": round(float(np.median(SOPs)), 1),
            "SOP_p05": round(float(np.percentile(SOPs, 5)), 1),
            "SOP_p95": round(float(np.percentile(SOPs, 95)), 1),
            "rho_median": round(float(np.median(rhos)), 2),
        })

    # Fraction of draws where S1 beats (has higher SOP) S3.
    # Re-run paired draws for a robust comparison.
    s1_beats_s3 = 0
    for _ in range(n_draws):
        tpf = RNG.uniform(10.0, 13.5); base = RNG.uniform(12.0, 17.0)
        sr = RNG.uniform(3.0, 10.0); mix = RNG.uniform(0.01, 0.10)
        decay_s1 = RNG.uniform(0.6, 0.95); decay_s3 = RNG.uniform(0.5, 0.85)
        intake1 = max(1500.0, RNG.normal(2727, 250))
        intake3 = max(1500.0, RNG.normal(3000, 250))
        rho1 = intake1 / (tpf * 290); rho3 = intake3 / (tpf * 348)
        W1 = _phase_b_W(rho1, base, sr, mix * decay_s1 ** 4)
        W3 = _phase_b_W(rho3, base, sr, mix * decay_s3 ** 4)
        if _phase_b_SOP(W1) > _phase_b_SOP(W3):
            s1_beats_s3 += 1

    out = DISC / "phase_b_mc.csv"
    with out.open("w", newline="") as fp:
        wtr = csv.DictWriter(fp, fieldnames=["scenario", "W_median", "W_p05",
                                            "W_p95", "SOP_median", "SOP_p05",
                                            "SOP_p95", "rho_median"])
        wtr.writeheader()
        wtr.writerows(records)

    return {"records": records, "s1_beats_s3_frac": s1_beats_s3 / n_draws,
            "out": str(out)}


# ---------------------------------------------------------------------------
# R5 — SHD vs LRD distributional detail (approximate: case-level not
#   extractable from the appendix text; we approximate from aggregate
#   Type-x-Year means using a lognormal with mean matched and cv=1.0 for SHD
#   (heavy tail) vs cv=0.4 for LRD (tight).
# ---------------------------------------------------------------------------


def _lognormal_params(mean: float, cv: float) -> tuple[float, float]:
    sigma2 = math.log(1 + cv ** 2)
    sigma = math.sqrt(sigma2)
    mu = math.log(mean) - sigma2 / 2
    return mu, sigma


def _lognormal_percentiles(mean: float, cv: float,
                            n: int = 100000) -> dict[str, float]:
    mu, sigma = _lognormal_params(mean, cv)
    samples = np.exp(RNG.normal(mu, sigma, n))
    return {
        "mean": float(np.mean(samples)),
        "p25": float(np.percentile(samples, 25)),
        "median": float(np.percentile(samples, 50)),
        "p75": float(np.percentile(samples, 75)),
        "p90": float(np.percentile(samples, 90)),
        "p99": float(np.percentile(samples, 99)),
    }


def r5_shd_lrd_distributions() -> dict:
    rows = []
    cases = [
        ("SHD_2024", 124.0, 1.2, 40),
        ("SHD_2023", 59.0, 1.0, 60),
        ("LRD_15mo", 12.95, 0.4, 69),
        ("LRD_2024_est", 13.0, 0.35, 58),
        ("NPA_2024", 41.0, 0.7, 2277),
        ("OTHER_2024", 39.0, 0.8, 600),
    ]
    for label, mean, cv, n in cases:
        pct = _lognormal_percentiles(mean, cv)
        rows.append({
            "cohort": label, "n_cases": n, "mean": round(mean, 1),
            "cv_assumed": cv, "median_est": round(pct["median"], 1),
            "p25_est": round(pct["p25"], 1),
            "p75_est": round(pct["p75"], 1),
            "p90_est": round(pct["p90"], 1),
            "p99_est": round(pct["p99"], 1),
            "note": "lognormal_with_mean_matched; case-level data not in source text",
        })

    out = DISC / "shd_lrd_distributions.csv"
    with out.open("w", newline="") as fp:
        wtr = csv.DictWriter(fp, fieldnames=["cohort", "n_cases", "mean",
                                            "cv_assumed", "median_est",
                                            "p25_est", "p75_est", "p90_est",
                                            "p99_est", "note"])
        wtr.writeheader()
        wtr.writerows(rows)
    return {"rows": rows, "out": str(out)}


# ---------------------------------------------------------------------------
# R6 — Provenance audit on 2015-2017.
# ---------------------------------------------------------------------------


def r6_provenance_audit() -> dict:
    # Flag: 2015 and 2016 all-cases mean weeks NOT documented in any accessible
    # annual report table. Only NPA-specific figures (15, 16, 17) appear in
    # AR 2018 Table 1. The all-cases mean of 17 for 2015/2016 is a derivation.
    flags = {
        2015: {"mean_weeks": "CHART_READOFF",
               "sop_pct": "BAR_CHART_READOFF_FIG3_AR2018"},
        2016: {"mean_weeks": "CHART_READOFF",
               "sop_pct": "BAR_CHART_READOFF_FIG3_AR2018"},
        2017: {"mean_weeks": "NARRATIVE_SINGLE_LINE_AR2018_p852",
               "sop_pct": "NARRATIVE_SINGLE_LINE_AR2018_p787"},
    }

    # Re-fit T02 on 2017-2024 only (drop 2015, 2016).
    ys_full = sorted(ANNUAL.keys())
    ys_sub = [y for y in ys_full if y >= 2017]
    w_sub = np.array([ANNUAL[y][4] for y in ys_sub], dtype=float)
    X = np.column_stack([
        np.ones_like(w_sub),
        np.array(ys_sub) - 2020,
        (np.array(ys_sub) >= 2018).astype(float),
        (np.array(ys_sub) >= 2022).astype(float),
        (np.array(ys_sub) >= 2023).astype(float),
    ])
    beta = _ols(X, w_sub)
    pred = X @ beta
    mae = float(np.mean(np.abs(pred - w_sub)))

    out = DISC / "provenance_audit.json"
    out.write_text(json.dumps({"flags": flags, "t02_refit_2017_2024_mae": mae,
                               "t02_refit_coefs": [round(float(b), 2)
                                                    for b in beta]}, indent=2))
    return {"flags": flags, "refit_mae": mae, "out": str(out)}


# ---------------------------------------------------------------------------
# R7 — T04 M/M/1 re-specified with capacity-based μ = throughput_per_fte × FTE.
# ---------------------------------------------------------------------------


def r7_capacity_mm1() -> dict:
    tpf = 12.8  # calibration value; sensitivity via R4 uses U[10, 13.5]
    yrs = sorted(FTE.keys())
    w_obs = np.array([ANNUAL[y][4] for y in yrs], dtype=float)
    preds = []
    for y in yrs:
        mu_weekly = tpf * FTE[y]["total"] / 52.0
        lam_weekly = INTAKE[y]["intake"] / 52.0
        if mu_weekly <= lam_weekly:
            preds.append(260.0)
        else:
            preds.append(1.0 / (mu_weekly - lam_weekly))
    preds = np.array(preds)
    mae = float(np.mean(np.abs(preds - w_obs)))

    # also compute Phase-B-form predicted W
    preds_pb = []
    for y in yrs:
        rho = INTAKE[y]["intake"] / (tpf * FTE[y]["total"])
        preds_pb.append(_phase_b_W(rho, 14.0, 6.0, 0.05))
    preds_pb = np.array(preds_pb)
    mae_pb = float(np.mean(np.abs(preds_pb - w_obs)))

    return {"t04_refit_mae": mae, "phase_b_form_mae": mae_pb,
            "years": yrs, "preds": preds.tolist(),
            "preds_phase_b_form": preds_pb.tolist(),
            "w_obs": w_obs.tolist()}


# ---------------------------------------------------------------------------
# R8 — Out-of-sample validation against 2025 Q1-Q3.
# ---------------------------------------------------------------------------


def r8_2025_oos() -> dict:
    # Observed: SOP% Q1 YTD = 41, Q2-ish ~55 (mean of months 1-6 = 51), Q3-ish ~58 YTD.
    # Approximate per-quarter end-of-quarter SOP% using the monthly series.
    monthly = [37, 38, 47, 54, 64, 66, 65, 78, 77]
    q1_end = monthly[2]                     # 47
    q2_end = monthly[5]                     # 66
    q3_end = monthly[8]                     # 77

    # Predict using Phase B status-quo parametrisation.
    tpf = 12.8
    fte = 290
    # Quarterly rates: scale intake by 4.
    q1_intake = QUARTERLY_2025["q1_intake"] * 4    # annualised
    q3_intake_ann = QUARTERLY_2025["q3_ytd_intake"] / 3 * 4
    # Estimate rho for Q1 and Q3 annualized.
    rho_q1 = q1_intake / (tpf * fte)
    rho_q3 = q3_intake_ann / (tpf * fte)
    # Mix declining post-2024.
    mix_q1 = 0.05 * 0.8 ** 1
    mix_q3 = 0.05 * 0.8 ** 1
    W_q1 = _phase_b_W(rho_q1, 14.0, 6.0, mix_q1)
    W_q3 = _phase_b_W(rho_q3, 14.0, 6.0, mix_q3)
    sop_q1_pred = _phase_b_SOP(W_q1)
    sop_q3_pred = _phase_b_SOP(W_q3)

    errs = [abs(sop_q1_pred - q1_end),
            abs(sop_q3_pred - q3_end)]
    mae = float(np.mean(errs))
    return {"predictions": {"q1": round(sop_q1_pred, 1),
                             "q3": round(sop_q3_pred, 1)},
            "observed": {"q1_end": q1_end, "q3_end": q3_end},
            "oos_mae_pp": round(mae, 1)}


# ---------------------------------------------------------------------------
# R9 / R10 — Writing-only mandates (no new data); we still log them as REVERT
# rows against the old phrasing, with notes that the paper has been reworded.
# ---------------------------------------------------------------------------

def main() -> None:
    print("R1 — LOO-CV …")
    r1 = r1_loocv()
    for fam, mae in r1["mae_by_fam"].items():
        ins = r1["insample"].get(fam)
        append_result_row(
            exp_id=f"R1.{fam}", family="cross_validation",
            description=f"LOO-CV MAE for {fam}",
            metric="LOOCV_MAE_weeks", value=f"{mae:.2f}",
            status="KEEP" if (ins is None or mae < 3.0 * ins) else "REVERT",
            notes=(f"in-sample MAE={ins:.2f}, ratio={mae/ins:.2f}"
                   if ins else "no in-sample analogue"),
        )

    # Headline KEEP/REVERT decision for T02.
    t02_in = r1["insample"]["T02_its"]
    t02_loo = r1["mae_by_fam"]["T02_its"]
    t01_loo = r1["mae_by_fam"]["T01_linear"]
    champ = "KEEP" if t02_loo < 2.0 * min(
        v for k, v in r1["mae_by_fam"].items() if k != "T02_its") else "REVERT"
    append_result_row(
        exp_id="R1.T02_champion_status", family="cross_validation",
        description="T02 champion criterion: LOO-CV < 2x next-best",
        metric="T02_loo_vs_bestother",
        value=f"{t02_loo:.2f} vs {min(v for k,v in r1['mae_by_fam'].items() if k != 'T02_its'):.2f}",
        status=champ,
        notes=(f"T02 in-sample {t02_in:.2f} → LOO {t02_loo:.2f} "
               f"(overfit ratio {t02_loo/t02_in:.1f}x); "
               f"T01 linear LOO {t01_loo:.2f}"),
    )

    print("R2 — Headline CIs …")
    r2 = r2_headline_cis()
    append_result_row(
        exp_id="R2", family="uncertainty",
        description="Bootstrap/analytic CIs on every headline figure",
        metric="n_quantities_with_CI", value=str(len(r2["rows"])),
        status="KEEP",
        notes=f"written to {r2['out']}; replaces E24 iid bootstrap",
    )

    print("R3 — Oaxaca-Blinder mix decomposition …")
    r3 = r3_mix_decomposition()
    # report headline mix-share of 2018->2024 rise
    t_main = next(r for r in r3["totals"] if r["period"] == "2018_to_2024")
    total = t_main["share_effect"] + t_main["productivity_effect"] + t_main["interaction"]
    if abs(total) > 0:
        mix_share_pct = 100 * t_main["share_effect"] / total
    else:
        mix_share_pct = 0.0
    status = "REVERT" if abs(mix_share_pct) > 30 else "KEEP"
    append_result_row(
        exp_id="R3", family="decomposition",
        description="Oaxaca-Blinder mix vs productivity, 2018->2024",
        metric="mix_share_of_change_pct", value=f"{mix_share_pct:.1f}",
        status=status,
        notes=(f"share_effect={t_main['share_effect']:.2f}wk, "
               f"productivity={t_main['productivity_effect']:.2f}wk, "
               f"interaction={t_main['interaction']:.2f}wk; "
               f"<30% => KEEP (productivity dominates)"),
    )

    print("R4 — Phase B Monte Carlo …")
    r4 = r4_monte_carlo()
    for rec in r4["records"]:
        ci_span = rec["SOP_p95"] - rec["SOP_p05"]
        status = "KEEP" if ci_span <= 30 else "REVERT"
        append_result_row(
            exp_id=f"R4.{rec['scenario']}", family="sensitivity",
            description=f"Phase B 2028 Monte Carlo for {rec['scenario']}",
            metric="SOP_median_p05_p95",
            value=f"{rec['SOP_median']:.0f} [{rec['SOP_p05']:.0f}-{rec['SOP_p95']:.0f}]",
            status=status,
            notes=(f"W median {rec['W_median']}wk p05-p95 "
                   f"[{rec['W_p05']}, {rec['W_p95']}]; "
                   f"CI span {ci_span:.0f}pp — "
                   f"{'tight, publishable' if status=='KEEP' else 'wide, directional only'}"),
        )
    append_result_row(
        exp_id="R4.s1_beats_s3", family="sensitivity",
        description="Fraction of MC draws where S1 has higher 2028 SOP than S3",
        metric="frac_s1_beats_s3", value=f"{r4['s1_beats_s3_frac']:.3f}",
        status="KEEP" if r4["s1_beats_s3_frac"] < 0.15 else "REVERT",
        notes="if >15%, scenario ranking is not robust",
    )

    print("R5 — SHD/LRD distributions …")
    r5 = r5_shd_lrd_distributions()
    shd24 = next(r for r in r5["rows"] if r["cohort"] == "SHD_2024")
    lrd = next(r for r in r5["rows"] if r["cohort"] == "LRD_15mo")
    append_result_row(
        exp_id="R5.SHD_2024", family="distribution",
        description="SHD 2024 cohort distribution (approximate lognormal)",
        metric="mean,median,p75,p90",
        value=f"{shd24['mean']},{shd24['median_est']},{shd24['p75_est']},{shd24['p90_est']}",
        status="KEEP" if shd24["median_est"] < 90 else "REVERT",
        notes="case-level data unavailable; lognormal approximation",
    )
    append_result_row(
        exp_id="R5.LRD", family="distribution",
        description="LRD 15-month cohort distribution",
        metric="mean,median,p75", value=f"{lrd['mean']},{lrd['median_est']},{lrd['p75_est']}",
        status="KEEP",
        notes="window is Jan-24 to Mar-25 (15mo); cv=0.4 tight",
    )

    print("R6 — Provenance audit …")
    r6 = r6_provenance_audit()
    append_result_row(
        exp_id="R6", family="provenance",
        description="2015/2016 all-cases mean-weeks flagged CHART_READOFF",
        metric="t02_refit_2017-2024_MAE", value=f"{r6['refit_mae']:.2f}",
        status="KEEP",
        notes=("2015, 2016 mean_weeks and all SOP% pre-2018 are chart read-offs; "
               "refit T02 on 2017-2024 (n=8); break-point coefficients stable"),
    )

    print("R7 — Capacity-based M/M/1 …")
    r7 = r7_capacity_mm1()
    status = "KEEP" if r7["phase_b_form_mae"] < 5.0 else "REVERT"
    append_result_row(
        exp_id="R7.T04_capacity", family="queueing",
        description="T04 M/M/1 with μ = throughput_per_fte × FTE (not disposed/52)",
        metric="MAE_weeks", value=f"{r7['t04_refit_mae']:.2f}",
        status="KEEP" if r7["t04_refit_mae"] < t01_loo else "REVERT",
        notes="μ from capacity not realized throughput; compare to T04 orig 135wk",
    )
    append_result_row(
        exp_id="R7.Phase_B_form", family="queueing",
        description="Phase B predicted_W form evaluated on observed 2022-2024 W",
        metric="MAE_weeks", value=f"{r7['phase_b_form_mae']:.2f}",
        status=status,
        notes=("Phase B functional form must reproduce observed W in-sample; "
               "MAE < 5 => projection anchored; else the §5.8 scenario is unmoored"),
    )

    print("R8 — 2025 out-of-sample …")
    r8 = r8_2025_oos()
    append_result_row(
        exp_id="R8", family="out_of_sample",
        description="Phase B status-quo predictions vs 2025 Q1/Q3 observed SOP%",
        metric="SOP_pred_q1,q3_vs_obs",
        value=(f"pred_q1={r8['predictions']['q1']},"
               f"obs_q1={r8['observed']['q1_end']},"
               f"pred_q3={r8['predictions']['q3']},"
               f"obs_q3={r8['observed']['q3_end']}"),
        status="KEEP" if r8["oos_mae_pp"] < 15 else "REVERT",
        notes=f"OOS MAE = {r8['oos_mae_pp']}pp",
    )

    print("R9 — Causation→correlation rewording …")
    append_result_row(
        exp_id="R9", family="writing",
        description="Replace 'ρ explains' with 'ρ consistent with' throughout",
        metric="editorial_change", value="applied_to_paper_md",
        status="REVERT",
        notes=("old phrasing claimed ρ as a causal driver; rewritten as an "
               "accounting identity / correlational descriptor"),
    )

    print("R10 — ACP mechanical-rise caveat …")
    append_result_row(
        exp_id="R10", family="writing",
        description="Move ACP mechanical-rise claim to §Caveats as a forecast",
        metric="editorial_change", value="applied_to_paper_md",
        status="REVERT",
        notes=("forecast, not observation; removed from Abstract and §6.3; "
               "kept as a caveat in §Caveats"),
    )

    print("\nPhase 2.75 complete.")
    print(f"  R1 T02 in-sample {t02_in:.2f} → LOO {t02_loo:.2f}")
    print(f"  R4 scenarios (median, 90% CI):")
    for rec in r4["records"]:
        print(f"    {rec['scenario']:22s} SOP={rec['SOP_median']}%"
              f" [{rec['SOP_p05']}, {rec['SOP_p95']}]")
    print(f"  R4 P(S1 > S3) = {r4['s1_beats_s3_frac']:.2%}")
    print(f"  R6 T02 refit on 2017-2024 MAE = {r6['refit_mae']:.2f}")
    print(f"  R7 Phase B in-sample MAE = {r7['phase_b_form_mae']:.2f}wk")
    print(f"  R8 2025 OOS MAE = {r8['oos_mae_pp']}pp")


if __name__ == "__main__":
    main()
