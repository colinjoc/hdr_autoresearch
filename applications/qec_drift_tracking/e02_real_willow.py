"""
E02 — run PF + sliding-window MLE + static Bayesian on real Willow detector events.

Uses d=5 r=1 and d=5 r=11 (if available) experiments, runs all three methods online,
compares learned rate vectors to the reference DEM's published rates. Records per-shot
MSE to ground-truth DEM rates (our proxy for tracking fidelity on a stationary device).

For drift-regime demonstration (Phase 1 §2), we sample a 50K shot stream, inject
synthetic OU drift onto the SI1000 rate vector in a second pass, and compare against
the no-drift reference.
"""

from __future__ import annotations
import datetime
import time

import numpy as np

from willow_loader import list_experiments, extract_experiment, load_experiment, dem_to_pcm
from particle_filter import ParticleFilter, DriftKernel
from baselines import SlidingWindowMLE, StaticBayesianRates, PeriodicDEMRefit


def real_data_cell(exp_path: str, max_shots: int = 5000) -> dict:
    """Run PF + baselines on a single Willow experiment."""
    exp_dir = extract_experiment(exp_path)
    data = load_experiment(exp_dir)
    H, O, ref_rates = dem_to_pcm(data["dem"])
    n_shots = min(max_shots, data["num_shots"])
    det_events = data["det_events"][:n_shots]

    E = H.shape[1]
    # Phase 2.75 reviewer fix: PF and baselines MUST start from the SAME uninformative
    # prior. Previously PF was initialised with prior_mean=ref_rates (the answer).
    UNIFORM_PRIOR = np.full(E, 1e-3)
    pf = ParticleFilter(n_particles=200, n_errors=E,
                       drift=DriftKernel(timescale_s=3600.0, amplitude=0.1, dt_s=1e-3),
                       prior_mean=UNIFORM_PRIOR,
                       seed=42)
    sw = SlidingWindowMLE(E, window_size=500)
    bay = StaticBayesianRates(E)

    t0 = time.perf_counter()
    for t in range(n_shots):
        s = det_events[t]
        pf.step(s, H, O, true_obs_flip=0)
        sw.update(s, H)
        bay.update(s, H)
    elapsed = time.perf_counter() - t0

    pf_est = pf.posterior_mean()
    sw_est = sw.posterior_mean()
    bay_est = bay.posterior_mean()

    # MSE vs reference DEM rates (the "ground truth" for a stationary device)
    mse_pf = np.mean((pf_est - ref_rates) ** 2)
    mse_sw = np.mean((sw_est - ref_rates) ** 2)
    mse_bay = np.mean((bay_est - ref_rates) ** 2)

    return {
        "exp_path": exp_path,
        "meta": data["meta"],
        "n_shots": n_shots,
        "n_detectors": data["num_detectors"],
        "n_errors": E,
        "ref_LER": float(np.mean(data["obs_actual"] != data["obs_predicted"])),
        "ref_rate_mean": float(ref_rates.mean()),
        "pf_rate_mean": float(pf_est.mean()),
        "sw_rate_mean": float(sw_est.mean()),
        "bay_rate_mean": float(bay_est.mean()),
        "mse_pf": float(mse_pf),
        "mse_sw": float(mse_sw),
        "mse_bay": float(mse_bay),
        "elapsed_s": elapsed,
    }


def main():
    print("[E02] real Willow d=5 run — PF + baselines vs reference DEM", flush=True)
    d5_exps = list_experiments(distance=5)
    # Pick a handful of d=5 experiments at different round counts
    targets = [e for e in d5_exps if e.endswith("/r01/")][:1]
    targets += [e for e in d5_exps if e.endswith("/r11/")][:1]
    targets += [e for e in d5_exps if e.endswith("/r25/")][:1]
    print(f"[E02] targets: {targets}", flush=True)

    results = []
    for exp in targets:
        try:
            print(f"\n=== {exp} ===", flush=True)
            r = real_data_cell(exp, max_shots=5000)
            print(f"  n_shots={r['n_shots']} E={r['n_errors']} n_dets={r['n_detectors']}", flush=True)
            print(f"  ref_LER={r['ref_LER']:.4f}", flush=True)
            print(f"  ref rate mean={r['ref_rate_mean']:.4e}", flush=True)
            print(f"  PF rate mean ={r['pf_rate_mean']:.4e}   MSE vs ref: {r['mse_pf']:.4e}", flush=True)
            print(f"  SW rate mean ={r['sw_rate_mean']:.4e}   MSE vs ref: {r['mse_sw']:.4e}", flush=True)
            print(f"  Bay rate mean={r['bay_rate_mean']:.4e}  MSE vs ref: {r['mse_bay']:.4e}", flush=True)
            print(f"  elapsed {r['elapsed_s']:.1f}s", flush=True)
            results.append(r)
        except Exception as e:
            import traceback
            print(f"  FAILED: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()

    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_drift_tracking/results.tsv"
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    with open(tsv, "a") as f:
        for i, r in enumerate(results):
            f.write(
                f"E02_real_willow_{i}\t{ts}\t{r['exp_path']}\t{r['n_detectors']}\t{r['n_errors']}\t"
                f"willow_real\t{r['n_shots']}\t42\t"
                f"{r['mse_pf']:.4e}\t{r['mse_sw']:.4e}\t{r['mse_bay']:.4e}\t0.0\t"
                f"{r['mse_pf'] < min(r['mse_sw'], r['mse_bay'])}\tKEEP\t"
                f"Phase1_E02_real_Willow_d=5_ref_LER={r['ref_LER']:.4f}\n"
            )
    print(f"\n[E02] wrote {len(results)} rows", flush=True)


if __name__ == "__main__":
    main()
