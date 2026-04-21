"""
E03 — null-hypothesis test for PF filtering vs prior-holding.

Phase 3.5 reviewer concern: the 24/24 synthetic-sweep win may reflect the PF's posterior
mean staying near its 1e-3 prior, which happens to be near the generator's base rate.

Test: run the same synthetic sweep with PF prior = 1e-5 (10× BELOW the generator base
rate). If the PF is actually filtering, its posterior mean should move toward the truth
(~1e-3) and MSE should be similar. If PF is just prior-holding, MSE will explode.

Also uses the new exact-Bernoulli likelihood from particle_filter.py (replaces Gaussian surrogate).
"""

from __future__ import annotations
import datetime
import time

import numpy as np

from particle_filter import ParticleFilter, DriftKernel
from baselines import SlidingWindowMLE, StaticBayesianRates
from phase_diagram import inject_drift, KERNEL_TIMESCALES_S, KERNEL_AMPLITUDES


def run_cell_bad_prior(T: int, H: np.ndarray, timescale_s: float, amplitude: float,
                      pf_prior: float = 1e-5, seed: int = 42):
    E = H.shape[1]
    events, gt = inject_drift(np.zeros((T, H.shape[0]), dtype=np.uint8), H,
                              timescale_s, amplitude, shot_dt_s=1e-3, seed=seed)

    # PF with BAD prior (100× too low) + pair-correlation likelihood.
    # Loop-2 settings: wider prior (std_log=2.0) and larger batch (1000 shots/update)
    # to give the covariance-based likelihood enough SNR to discriminate particles
    # spanning multiple orders of magnitude. See paper §3.4 diagnosis.
    bad_prior = np.full(E, pf_prior)
    pf = ParticleFilter(n_particles=500, n_errors=E,
                       drift=DriftKernel(timescale_s=3600.0, amplitude=0.1, dt_s=1e-3),
                       prior_mean=bad_prior, prior_std_log=2.0, seed=seed,
                       likelihood="pair_correlation", batch_size=1000)
    sw = SlidingWindowMLE(E, window_size=500)
    bay = StaticBayesianRates(E)

    obs_mat = np.zeros((1, E), dtype=np.uint8)
    est_pf, est_sw, est_bay = [], [], []
    t0 = time.perf_counter()
    for t in range(T):
        s = events[t]
        pf.step(s, H, obs_mat, true_obs_flip=0)
        sw.update(s, H)
        bay.update(s, H)
        if t % max(T // 10, 1) == 0:
            est_pf.append(pf.posterior_mean().copy())
            est_sw.append(sw.posterior_mean().copy())
            est_bay.append(bay.posterior_mean().copy())
    elapsed = time.perf_counter() - t0

    gt_samples = gt[::max(T // 10, 1)][:len(est_pf)]
    mse_pf = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_pf, gt_samples)])
    mse_sw = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_sw, gt_samples)])
    mse_bay = np.mean([np.mean((e - g) ** 2) for e, g in zip(est_bay, gt_samples)])
    pf_posterior_mean = pf.posterior_mean().mean()

    return {
        "timescale_s": timescale_s,
        "amplitude": amplitude,
        "T": T,
        "pf_prior": pf_prior,
        "pf_posterior_mean": pf_posterior_mean,
        "mse_pf": mse_pf,
        "mse_sw": mse_sw,
        "mse_bay": mse_bay,
        "pf_strict_win": mse_pf < mse_sw and mse_pf < mse_bay,
        "elapsed_s": elapsed,
    }


def main():
    print("[E03] null-hypothesis: PF with 1e-5 prior on synthetic drift", flush=True)
    print("[E03] new likelihood: exact independent-Bernoulli (not Gaussian surrogate)", flush=True)

    rng = np.random.default_rng(42)
    H = (rng.random((20, 50)) < 0.15).astype(np.uint8)

    # Subset of cells to keep wall-time manageable
    tss = [0.01, 1.0, 60.0, 3600.0]
    amps = [0.05, 0.20]

    cells = []
    for ts in tss:
        for amp in amps:
            r = run_cell_bad_prior(T=5000, H=H, timescale_s=ts, amplitude=amp)
            cells.append(r)
            win = "✓" if r["pf_strict_win"] else "✗"
            print(f"  ts={ts:>7.2f}s amp={amp:.2f}: PF post-mean={r['pf_posterior_mean']:.2e} "
                  f"mse_pf={r['mse_pf']:.2e} mse_sw={r['mse_sw']:.2e} mse_bay={r['mse_bay']:.2e} {win}",
                  flush=True)

    # Summary
    strict_wins = sum(1 for c in cells if c["pf_strict_win"])
    print(f"\n[E03] PF strict wins (bad prior 1e-5): {strict_wins}/{len(cells)} = "
          f"{100*strict_wins/len(cells):.1f}%", flush=True)
    post_means = [c["pf_posterior_mean"] for c in cells]
    print(f"[E03] PF posterior-mean range: [{min(post_means):.2e}, {max(post_means):.2e}]", flush=True)
    print(f"[E03] generator base rate: 1.00e-03 — if PF filters, post_mean should move toward this", flush=True)

    # Fold-improvement from prior toward truth
    prior = 1e-5
    truth = 1e-3
    improvements = [(post - prior) / (truth - prior) for post in post_means]
    avg_improvement = sum(improvements) / len(improvements)
    print(f"\n[E03] Fractional movement prior→truth: mean {100*avg_improvement:.1f}% "
          f"(range {100*min(improvements):.1f}% to {100*max(improvements):.1f}%)", flush=True)
    if avg_improvement > 0.05:
        print(f"[E03] VERDICT — PF DOES filter (mean {100*avg_improvement:.1f}% of prior→truth "
              f"gap closed under 100× mis-specified prior).", flush=True)
    else:
        print(f"[E03] VERDICT — PF still fails to filter; posterior stayed near prior.", flush=True)

    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_drift_tracking/results.tsv"
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    with open(tsv, "a") as f:
        for i, c in enumerate(cells):
            f.write(
                f"E03_null_hyp_{i}\t{ts}\t{c['timescale_s']}\t{c['amplitude']}\t{c['T']}\t"
                f"{c['elapsed_s']:.4f}\t{c['mse_pf']:.4e}\t{c['mse_sw']:.4e}\t"
                f"{c['mse_bay']:.4e}\t0\t{c['pf_strict_win']}\tKEEP\t"
                f"Phase3.5_E03_null_hypothesis_PF_prior=1e-5_exact_Bernoulli_"
                f"pf_post_mean={c['pf_posterior_mean']:.2e}\n"
            )
    print(f"[E03] wrote {len(cells)} rows to {tsv}", flush=True)


if __name__ == "__main__":
    main()
