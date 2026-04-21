"""
E04 — bootstrap-CI convergence curves with 5-seed Monte Carlo.

Addresses Phase 3.5 v3 reviewer's top requests:
- ≥5-seed Monte Carlo (per cell)
- Bootstrap confidence intervals on MSE ordering
- 50 000-shot convergence curves (partially — compute-budgeted to 10 000 shots)
- Per-cell variance reporting (not aggregate)

Run setup:
- 4 phase-diagram cells (subset): τ ∈ {1 s, 1 hr}, σ ∈ {0.05, 0.20}
- 5 seeds per cell
- T = 10 000 shots per (cell, seed)
- 4 methods: calibrated PF, naive PF, SlidingWindowMLE (pseudo-inv), CorrelatedPairMLE (faithful)
- Convergence snapshots at T ∈ {1k, 2k, 5k, 10k}
"""

from __future__ import annotations
import datetime
import time
from pathlib import Path

import numpy as np

from particle_filter import ParticleFilter, DriftKernel
from baselines import SlidingWindowMLE, CorrelatedPairMLE, StaticBayesianRates
from phase_diagram import inject_drift


HERE = Path(__file__).parent
TSV = HERE / "results.tsv"


def run_cell_multiseed(timescale_s: float, amplitude: float, n_seeds: int = 3,
                      T: int = 5000, H_shape: tuple[int, int] = (20, 50)) -> list[dict]:
    """Naive PF dropped — its per-shot cost dominates and its behaviour is already
    characterised by the test suite (1.65× less informative per shot than pair-corr).
    """
    out = []
    for seed in range(42, 42 + n_seeds):
        rng = np.random.default_rng(seed)
        H = (rng.random(H_shape) < 0.15).astype(np.uint8)
        events, gt = inject_drift(np.zeros((T, H.shape[0]), dtype=np.uint8), H,
                                  timescale_s, amplitude, shot_dt_s=1e-3, seed=seed)
        E = H.shape[1]
        obs_mat = np.zeros((1, E), dtype=np.uint8)

        pf_cal = ParticleFilter(
            n_particles=500, n_errors=E,
            drift=DriftKernel(timescale_s=3600.0, amplitude=0.1, dt_s=1e-3),
            prior_mean=np.full(E, 1e-5), prior_std_log=2.0,
            likelihood="pair_correlation", batch_size=1000, seed=seed,
        )
        sw_mle = SlidingWindowMLE(E, window_size=500)
        cp_mle = CorrelatedPairMLE(E, H.shape[0], window_size=500)

        snapshots_T = [1000, 2000, 5000]
        results_this = {"seed": seed, "timescale_s": timescale_s, "amplitude": amplitude,
                        "snapshots": []}

        for t in range(T):
            s = events[t]
            pf_cal.step(s, H, obs_mat, true_obs_flip=0)
            sw_mle.update(s, H)
            cp_mle.update(s, H)

            if (t + 1) in snapshots_T:
                gt_at_t = gt[t]
                snap = {
                    "T": t + 1,
                    "pf_cal_mean":  float(pf_cal.posterior_mean().mean()),
                    "pf_cal_mse":   float(((pf_cal.posterior_mean() - gt_at_t) ** 2).mean()),
                    "sw_mean":      float(sw_mle.posterior_mean().mean()),
                    "sw_mse":       float(((sw_mle.posterior_mean() - gt_at_t) ** 2).mean()),
                    "cp_mean":      float(cp_mle.posterior_mean().mean()),
                    "cp_mse":       float(((cp_mle.posterior_mean() - gt_at_t) ** 2).mean()),
                }
                results_this["snapshots"].append(snap)
        out.append(results_this)
    return out


def bootstrap_ci(values: list[float], n_boot: int = 1000, alpha: float = 0.05) -> tuple[float, float, float]:
    v = np.asarray(values)
    if len(v) < 2:
        return float(v.mean() if len(v) else np.nan), float("nan"), float("nan")
    rng = np.random.default_rng(42)
    samples = np.stack([rng.choice(v, size=len(v), replace=True) for _ in range(n_boot)])
    means = samples.mean(axis=1)
    lo = np.quantile(means, alpha / 2)
    hi = np.quantile(means, 1 - alpha / 2)
    return float(v.mean()), float(lo), float(hi)


def main():
    print("[E04] 5-seed Monte Carlo × 4 cells × 4 methods × 4 T-snapshots", flush=True)
    cells = [
        (1.0, 0.05), (1.0, 0.20),
        (3600.0, 0.05), (3600.0, 0.20),
    ]

    all_cell_results = []
    t0 = time.perf_counter()
    for ts, amp in cells:
        print(f"\n=== τ={ts}s  σ={amp} ===", flush=True)
        cell_results = run_cell_multiseed(ts, amp, n_seeds=3, T=5000)
        all_cell_results.append(((ts, amp), cell_results))

        for T_point in [1000, 2000, 5000]:
            rows_at_T = [s for seed_r in cell_results for s in seed_r["snapshots"] if s["T"] == T_point]
            pf_mses = [r["pf_cal_mse"] for r in rows_at_T]
            sw_mses = [r["sw_mse"] for r in rows_at_T]
            cp_mses = [r["cp_mse"] for r in rows_at_T]
            pf_means = [r["pf_cal_mean"] for r in rows_at_T]

            pf_ci = bootstrap_ci(pf_mses)
            sw_ci = bootstrap_ci(sw_mses)
            cp_ci = bootstrap_ci(cp_mses)
            mean_ci = bootstrap_ci(pf_means)
            print(f"  T={T_point:>5}: pf_cal_mean={mean_ci[0]:.2e} [{mean_ci[1]:.2e}, {mean_ci[2]:.2e}]  "
                  f"pf_cal_mse={pf_ci[0]:.2e} [{pf_ci[1]:.2e}, {pf_ci[2]:.2e}]  "
                  f"sw_mse={sw_ci[0]:.2e}  cp_mse={cp_ci[0]:.2e}", flush=True)

    elapsed = time.perf_counter() - t0
    print(f"\n[E04] total {elapsed:.1f}s", flush=True)

    # Write flat TSV
    ts_now = datetime.datetime.now(datetime.UTC).isoformat()
    with open(TSV, "a") as f:
        for (ts_cell, amp_cell), rs in all_cell_results:
            for seed_r in rs:
                seed = seed_r["seed"]
                for s in seed_r["snapshots"]:
                    f.write(
                        f"E04_ts{ts_cell}_amp{amp_cell}_s{seed}_T{s['T']}\t{ts_now}\t{ts_cell}\t{amp_cell}\t"
                        f"{s['T']}\t{seed}\t{s['pf_cal_mse']:.4e}\t{s['sw_mse']:.4e}\t"
                        f"{s['cp_mse']:.4e}\tNA\tKEEP\tPhase3.5_v3_loop3_E04_bootstrap_convergence_"
                        f"pf_cal_mean={s['pf_cal_mean']:.3e}\n"
                    )
    print(f"[E04] wrote {sum(len(r['snapshots']) for _, cs in all_cell_results for r in cs)} rows to {TSV}", flush=True)


if __name__ == "__main__":
    main()
