"""
Figures for paper_v6 (addresses Phase 3.5 v5 reviewer M5):
  fig1 — prior-migration trajectory of the calibrated SMC posterior mean
  fig2 — MSE vs T with per-seed spread for 3 methods
  fig3 — log-likelihood gap (truth - wrong) vs batch size, pair-correlation vs naive
"""
from __future__ import annotations
import time
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from particle_filter import ParticleFilter, DriftKernel
from baselines import SlidingWindowMLE, CorrelatedPairMLE
from phase_diagram import inject_drift

HERE = Path(__file__).parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)


def fig1_prior_migration():
    """PF posterior mean trajectory from 1e-5 prior toward 1e-3 truth, 3 seeds."""
    T = 5000
    H_shape = (20, 50)
    fig, ax = plt.subplots(figsize=(8, 5))

    for seed in [42, 43, 44]:
        rng = np.random.default_rng(seed)
        H = (rng.random(H_shape) < 0.15).astype(np.uint8)
        events, _ = inject_drift(np.zeros((T, 20), dtype=np.uint8), H, 3600.0, 0.1, 1e-3, seed)
        E = H.shape[1]
        pf = ParticleFilter(500, E, DriftKernel(3600.0, 0.1, 1e-3),
                            prior_mean=np.full(E, 1e-5), prior_std_log=2.0,
                            likelihood="pair_correlation", batch_size=1000, seed=seed)
        obs_mat = np.zeros((1, E), dtype=np.uint8)
        trajectory = []
        for t in range(T):
            pf.step(events[t], H, obs_mat, true_obs_flip=0)
            if (t + 1) % 250 == 0:
                trajectory.append((t + 1, pf.posterior_mean().mean()))
        ts, means = zip(*trajectory)
        ax.plot(ts, means, "o-", alpha=0.75, label=f"seed {seed}")

    ax.axhline(1e-5, linestyle="--", color="tab:red", alpha=0.5, label="prior (1e-5)")
    ax.axhline(1e-3, linestyle="--", color="tab:green", alpha=0.5, label="truth (1e-3)")
    ax.set_yscale("log")
    ax.set_xlabel("shots T")
    ax.set_ylabel("PF posterior mean (log)")
    ax.set_title("Prior-migration trajectory under 100× mis-specified prior\n"
                 "Calibrated SMC, pair-correlation likelihood, 3 seeds")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="center right", fontsize=9)
    fig.tight_layout()
    path = FIGS / "fig1_prior_migration.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig2_mse_vs_T():
    """MSE vs T with per-seed spread: PF, SW-MLE, CP-MLE."""
    T_points = [1000, 2000, 5000]
    methods = {}

    for seed in [42, 43, 44]:
        rng = np.random.default_rng(seed)
        H = (rng.random((20, 50)) < 0.15).astype(np.uint8)
        events, gt = inject_drift(np.zeros((5000, 20), dtype=np.uint8), H, 3600.0, 0.1, 1e-3, seed)
        E = H.shape[1]
        obs_mat = np.zeros((1, E), dtype=np.uint8)
        pf = ParticleFilter(500, E, DriftKernel(3600.0, 0.1, 1e-3),
                            prior_mean=np.full(E, 1e-5), prior_std_log=2.0,
                            likelihood="pair_correlation", batch_size=1000, seed=seed)
        sw = SlidingWindowMLE(E, window_size=500)
        cp = CorrelatedPairMLE(E, 20, window_size=500)
        for t in range(5000):
            pf.step(events[t], H, obs_mat, true_obs_flip=0)
            sw.update(events[t], H)
            cp.update(events[t], H)
            if (t + 1) in T_points:
                for name, est in [("PF", pf), ("SW-MLE", sw), ("CP-MLE (lstsq)", cp)]:
                    mse = float(((est.posterior_mean() - gt[t]) ** 2).mean())
                    methods.setdefault(name, {}).setdefault(t + 1, []).append(mse)

    fig, ax = plt.subplots(figsize=(8, 5))
    colours = {"PF": "tab:blue", "SW-MLE": "tab:orange", "CP-MLE (lstsq)": "tab:green"}
    for name in methods:
        pts = sorted(methods[name].items())
        Ts = [p[0] for p in pts]
        means = [np.mean(p[1]) for p in pts]
        lows = [min(p[1]) for p in pts]
        highs = [max(p[1]) for p in pts]
        ax.plot(Ts, means, "o-", color=colours[name], label=name)
        ax.fill_between(Ts, lows, highs, color=colours[name], alpha=0.2)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("shots T")
    ax.set_ylabel("MSE vs ground-truth rate")
    ax.set_title("MSE vs T (3 seeds, min–max spread shaded)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = FIGS / "fig2_mse_vs_T.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig3_log_L_gap_vs_batch():
    """Log-L gap between truth and 100×-wrong particle, vs batch size, for both
    independent-Bernoulli and pair-correlation likelihoods."""
    rng = np.random.default_rng(42)
    H = (rng.random((10, 30)) < 0.15).astype(np.uint8)
    T = 2000
    events, _ = inject_drift(np.zeros((T, 10), dtype=np.uint8), H, 3600.0, 0.0, 1e-3, 42)
    E = 30

    batches = [50, 100, 200, 500, 1000, 2000]
    gaps_pair = []
    gaps_naive = []

    for bs in batches:
        # Pair-correlation
        pf_pair = ParticleFilter(2, E, DriftKernel(3600.0, 0.0, 1e-3),
                                 likelihood="pair_correlation", batch_size=bs,
                                 prior_mean=np.array([1e-3]), prior_std_log=0.01, seed=42)
        pf_pair.theta = np.array([np.full(E, 1e-3), np.full(E, 1e-5)], dtype=np.float64)
        pf_pair._window = [events[t] for t in range(bs)]
        ll = pf_pair._pair_correlation_log_lik(H, pf_pair._window)
        gaps_pair.append(float(ll[0] - ll[1]))

        # Independent-Bernoulli summed over bs shots
        pf_naive = ParticleFilter(2, E, DriftKernel(3600.0, 0.0, 1e-3),
                                  likelihood="independent_bernoulli",
                                  prior_mean=np.array([1e-3]), prior_std_log=0.01, seed=42)
        pf_naive.theta = np.array([np.full(E, 1e-3), np.full(E, 1e-5)], dtype=np.float64)
        ll_sum = np.zeros(2)
        for t in range(bs):
            ll_sum += pf_naive._independent_bernoulli_log_lik(H, events[t])
        gaps_naive.append(float(ll_sum[0] - ll_sum[1]))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(batches, gaps_pair, "o-", color="tab:blue", label="Pair-correlation")
    ax.plot(batches, gaps_naive, "s-", color="tab:orange", label="Independent-Bernoulli")
    ax.axhline(1.0, linestyle=":", color="gray", alpha=0.5, label="1 nat (minimum informativeness)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("batch size (shots)")
    ax.set_ylabel("log-L gap: truth − 100×-wrong (nats)")
    ax.set_title("Likelihood informativeness vs batch size\n"
                 "(truth θ=1e-3, wrong θ=1e-5; single fixture, seed 42)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = FIGS / "fig3_log_L_gap_vs_batch.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    # Print the ratios as a table for paper text
    print(f"\nBatch size | pair gap | naive gap | ratio")
    for bs, gp, gn in zip(batches, gaps_pair, gaps_naive):
        if gn > 0:
            print(f"{bs:>10} | {gp:>8.1f} | {gn:>9.1f} | {gp/gn:.2f}")
    return path


if __name__ == "__main__":
    t0 = time.perf_counter()
    for fig_fn in (fig1_prior_migration, fig2_mse_vs_T, fig3_log_L_gap_vs_batch):
        print(f"generating {fig_fn.__name__}...", flush=True)
        p = fig_fn()
        print(f"  wrote {p}", flush=True)
    print(f"total {time.perf_counter()-t0:.1f}s")
