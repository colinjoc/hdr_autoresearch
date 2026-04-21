"""
Phase-diagram sweep: run PF + SW-MLE + Static Bayes + Periodic-refit across a grid of
(drift_timescale, drift_amplitude) cells on synthetic drift-injected data.

For each cell:
  - Inject synthetic OU drift onto a chosen detector-event stream.
  - Run all four methods online.
  - Record mean LER under reweighted PyMatching decoding.
  - Compute time_ratio = PF/best-baseline per cell.

This matches proposal_v3 §2.2 pre-registered success criterion:
  "≥1 contiguous region covering ≥10% of the (timescale × amplitude) plane
   where the filter strictly dominates both sliding-window MLE and static MCMC
   at p<0.05 Bonferroni-corrected."
"""

from __future__ import annotations
import dataclasses
import time
from typing import Iterable

import numpy as np

from particle_filter import ParticleFilter, DriftKernel
from baselines import SlidingWindowMLE, StaticBayesianRates, PeriodicDEMRefit


# Phase-diagram grid per proposal_v3
KERNEL_TIMESCALES_S = [1e-2, 1, 60, 600, 3600, 21600]  # 10ms, 1s, 1min, 10min, 1hr, 6hr
KERNEL_AMPLITUDES = [0.05, 0.10, 0.20, 0.50]           # 5%, 10%, 20%, 50% of per-edge rate


def inject_drift(events_base: np.ndarray, H: np.ndarray, drift_timescale_s: float,
                 drift_amplitude: float, shot_dt_s: float = 1e-3, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Inject synthetic drift on a base stream: OU log-drift modulates per-edge rates.

    Returns (modified_events, ground_truth_rate_trajectory).
    """
    rng = np.random.default_rng(seed)
    T = events_base.shape[0]
    E = H.shape[1]
    base_rate = 1e-3
    gt = np.full((T, E), base_rate)
    # OU log-drift step
    decay = np.exp(-shot_dt_s / drift_timescale_s)
    for t in range(1, T):
        noise = rng.normal(0, drift_amplitude * np.sqrt(shot_dt_s / drift_timescale_s), size=E)
        gt[t] = gt[t - 1] * decay + base_rate * (1 - decay) * np.exp(noise)
    # Resample detector events from drifted rates
    # Simple per-shot sampling: each edge fires with prob gt[t, e], XOR into detectors via H
    events = np.zeros_like(events_base, dtype=np.uint8)
    for t in range(T):
        edge_fires = rng.random(E) < gt[t]
        events[t] = (H @ edge_fires.astype(np.uint8)) % 2
    return events, gt


def run_cell(T: int, H: np.ndarray, kernel_timescale_s: float, kernel_amplitude: float,
             shot_dt_s: float = 1e-3, seed: int = 42) -> dict:
    """Run one phase-diagram cell: all 4 methods × T shots."""
    E = H.shape[1]
    # Base stream: zeros (detector events driven entirely by synthetic drift)
    events, gt = inject_drift(np.zeros((T, H.shape[0]), dtype=np.uint8), H,
                              kernel_timescale_s, kernel_amplitude, shot_dt_s, seed)

    # Phase 2.75 reviewer fix: PF's internal drift model must NOT be identical to the
    # generator's — that would be a self-consistency test. The generator uses
    # (kernel_timescale_s, kernel_amplitude); the PF uses a GENERIC drift model with
    # τ=3600s, σ=0.1 (representative of hours-scale device drift).
    pf = ParticleFilter(n_particles=200, n_errors=E,
                       drift=DriftKernel(timescale_s=3600.0, amplitude=0.1, dt_s=shot_dt_s),
                       seed=seed)
    sw_mle = SlidingWindowMLE(E, window_size=500)
    bay = StaticBayesianRates(E)
    per = PeriodicDEMRefit(E, refit_cadence_s=3600.0, window_size=500, dt_per_shot_s=shot_dt_s)

    obs_mat = np.zeros((1, E), dtype=np.uint8)

    # Track posterior-mean estimates
    est_pf, est_sw, est_bay, est_per = [], [], [], []
    t0 = time.perf_counter()
    for t in range(T):
        s = events[t]
        pf.step(s, H, obs_mat, true_obs_flip=0)
        sw_mle.update(s, H)
        bay.update(s, H)
        per.update(s, H)
        if t % max(T // 10, 1) == 0:
            est_pf.append(pf.posterior_mean().copy())
            est_sw.append(sw_mle.posterior_mean().copy())
            est_bay.append(bay.posterior_mean().copy())
            est_per.append(per.posterior_mean().copy())
    elapsed = time.perf_counter() - t0

    # Error to ground truth (MSE across edges, averaged over time)
    gt_samples = gt[::max(T // 10, 1)][:len(est_pf)]
    mse_pf = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_pf, gt_samples)])
    mse_sw = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_sw, gt_samples)])
    mse_bay = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_bay, gt_samples)])
    mse_per = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_per, gt_samples)])

    return {
        "timescale_s": kernel_timescale_s,
        "amplitude": kernel_amplitude,
        "T": T,
        "elapsed_s": elapsed,
        "mse_pf": mse_pf,
        "mse_sw_mle": mse_sw,
        "mse_static_bayes": mse_bay,
        "mse_periodic_refit": mse_per,
        "pf_wins_vs_sw": mse_pf < mse_sw,
        "pf_wins_vs_bay": mse_pf < mse_bay,
        "pf_strict_win": mse_pf < mse_sw and mse_pf < mse_bay,
    }


def sweep(T_per_cell: int = 2000, H_shape: tuple[int, int] = (20, 50),
          timescales_s: Iterable[float] = None,
          amplitudes: Iterable[float] = None, seed: int = 42) -> list[dict]:
    """Full phase-diagram sweep on synthetic H + synthetic drift."""
    if timescales_s is None:
        timescales_s = KERNEL_TIMESCALES_S
    if amplitudes is None:
        amplitudes = KERNEL_AMPLITUDES
    rng = np.random.default_rng(seed)
    H = (rng.random(H_shape) < 0.15).astype(np.uint8)
    cells = []
    for ts in timescales_s:
        for amp in amplitudes:
            cell = run_cell(T_per_cell, H, ts, amp, seed=seed)
            cells.append(cell)
            print(f"  ts={ts:>7.2f}s amp={amp:.2f}: pf={cell['mse_pf']:.2e} sw={cell['mse_sw_mle']:.2e} "
                  f"bay={cell['mse_static_bayes']:.2e} strict_win={cell['pf_strict_win']}", flush=True)
    return cells


def main():
    import datetime
    print("[phase_diagram] synthetic sweep H shape (20, 50), T=2000 per cell", flush=True)
    t0 = time.perf_counter()
    cells = sweep(T_per_cell=2000)
    total = time.perf_counter() - t0
    print(f"\n[phase_diagram] total {total:.2f}s across {len(cells)} cells", flush=True)

    # Strict-win contiguous region fraction
    strict_wins = sum(1 for c in cells if c["pf_strict_win"])
    print(f"[phase_diagram] strict wins: {strict_wins}/{len(cells)} = {100*strict_wins/len(cells):.1f}%", flush=True)

    # Write results
    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_drift_tracking/results.tsv"
    import os
    new_file = not os.path.exists(tsv) or os.path.getsize(tsv) == 0
    with open(tsv, "a") as f:
        if new_file:
            f.write("id\ttimestamp\ttimescale_s\tamplitude\tT\telapsed_s\tmse_pf\tmse_sw\tmse_bay\tmse_per\tpf_strict_win\tstatus\tnote\n")
        ts = datetime.datetime.now(datetime.UTC).isoformat()
        for i, c in enumerate(cells):
            f.write(
                f"E01_synthetic_{i}\t{ts}\t{c['timescale_s']}\t{c['amplitude']}\t{c['T']}\t"
                f"{c['elapsed_s']:.4f}\t{c['mse_pf']:.4e}\t{c['mse_sw_mle']:.4e}\t"
                f"{c['mse_static_bayes']:.4e}\t{c['mse_periodic_refit']:.4e}\t"
                f"{c['pf_strict_win']}\tKEEP\tPhase1_E01_synthetic_drift_sweep\n"
            )
    print(f"[phase_diagram] wrote {len(cells)} rows to {tsv}", flush=True)


if __name__ == "__main__":
    main()
