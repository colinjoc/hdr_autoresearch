"""Phase 2 Brownian-dynamics simulator for Bérut-like finite-time erasure.

Overdamped Langevin in a time-dependent double-well quartic potential:

    U(x, t) = (b(t)/4) * x^4 - (a(t)/2) * x^2 + c(t) * x

with a(t) controlling barrier height, b(t) controlling well separation (kept
fixed as a single "well width" parameter), and c(t) the tilt. Units are
dimensionless: length in units of well separation, energy in k_B T, time in
units of relaxation time gamma / (a_peak), where gamma is the friction.

The Bérut protocol is implemented as three equal-duration stages of total
cycle time tau (in dimensionless units):

    Stage 1 (barrier lowering):  a(t) ramps from a_peak down to a_mid (knob K5 sets a_mid)
    Stage 2 (tilt):              c(t) ramps up to c_max then back (knob K4 sets c_max, K2 sets shape)
    Stage 3 (barrier restore):   a(t) ramps back up to a_peak (knob K1 sets shape)

Heat dissipated per cycle:  Q_diss = -integral( dU/dt ) along trajectory minus work done.
Equivalently Q_diss = W - dF, where dF = 0 for a cyclic protocol (same start & end U).

See protocol_family_analysis.md for knob definitions. This simulator exposes
knobs K1 (lowering ramp shape), K2 (tilt ramp shape), K3 (overlap fraction),
K5 (residual barrier fraction at peak tilt), and K4 (peak tilt amplitude).
K6/K7/K8 are fixed at zero / nominal for this sweep.
"""
import csv
import math
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

RESULTS_PATH = Path(__file__).parent / "results.tsv"
SIMDATA_PATH = Path(__file__).parent / "data" / "simulated_qdiss_vs_tau.csv"

KB_T_LN2 = math.log(2)
PI_SQ = math.pi ** 2


def ramp(t, t_start, t_end, shape_sigma):
    """Monotone ramp from 0 to 1 over [t_start, t_end]; shape_sigma in [0,1]
    interpolates linear (0) -> sigmoidal (1)."""
    if t <= t_start:
        return 0.0
    if t >= t_end:
        return 1.0
    u = (t - t_start) / (t_end - t_start)
    linear = u
    sigm = 1.0 / (1.0 + math.exp(-8.0 * (u - 0.5)))
    # Normalise sigmoid to hit 0 at u=0 and 1 at u=1 exactly.
    sigm = (sigm - 1.0 / (1.0 + math.exp(4.0))) / (1.0 / (1.0 + math.exp(-4.0)) - 1.0 / (1.0 + math.exp(4.0)))
    return (1 - shape_sigma) * linear + shape_sigma * sigm


def protocol(t, tau, K1, K2, K3, K4, K5):
    """Return (a(t), c(t)) at time t in [0, tau]."""
    # Stage boundaries with overlap K3 in [0, 0.5]
    t1_start = 0.0
    t1_end = tau / 3 + K3 * tau / 6
    t2_start = tau / 3 - K3 * tau / 6
    t2_end = 2 * tau / 3 + K3 * tau / 6
    t3_start = 2 * tau / 3 - K3 * tau / 6
    t3_end = tau

    a_peak = 8.0
    a_mid = K5 * a_peak
    c_max = K4

    # Barrier: start at a_peak, drop to a_mid over stage 1, stay, rise back to a_peak over stage 3
    lower_progress = ramp(t, t1_start, t1_end, K1)
    raise_progress = ramp(t, t3_start, t3_end, K1)
    a_t = a_peak - (a_peak - a_mid) * lower_progress * (1 - raise_progress) - (a_peak - a_mid) * (1 - raise_progress) * 0
    # Simpler: a(t) goes from a_peak to a_mid over stage 1, stays a_mid during stage 2, rises over stage 3
    if t < t1_end:
        a_t = a_peak - (a_peak - a_mid) * lower_progress
    elif t < t3_start:
        a_t = a_mid
    else:
        a_t = a_mid + (a_peak - a_mid) * raise_progress

    # Tilt: 0 -> c_max -> 0 over stage 2 (triangular shape, tilt sigmoidal by K2)
    if t < t2_start:
        c_t = 0.0
    elif t < (t2_start + t2_end) / 2:
        rise_progress_tilt = ramp(t, t2_start, (t2_start + t2_end) / 2, K2)
        c_t = c_max * rise_progress_tilt
    elif t < t2_end:
        fall_progress_tilt = ramp(t, (t2_start + t2_end) / 2, t2_end, K2)
        c_t = c_max * (1 - fall_progress_tilt)
    else:
        c_t = 0.0

    return a_t, c_t


def U_and_F(x, a, c):
    """Potential U(x) = x^4/4 - a x^2 / 2 + c x. Force F = -dU/dx."""
    U = 0.25 * x ** 4 - 0.5 * a * x ** 2 + c * x
    F = -(x ** 3 - a * x + c)
    return U, F


def simulate_cycle(tau, knobs, n_traj=400, n_steps=800, seed=42):
    """Simulate n_traj Langevin trajectories over one cycle of duration tau.

    For a cyclic protocol (U(x, 0) == U(x, tau)), the cycle-averaged heat
    dissipated to the bath equals the work done on the system by the external
    agent: <Q_diss> = <W> = < integral dt * (∂U/∂t at fixed x) >.
    We track only W; no separate heat accounting is needed.

    The initial distribution is bimodal symmetric — half the trajectories
    start in the left well, half in the right well — i.e., a proper 1-bit
    mixed state that the protocol then erases into the right well.

    Returns mean and stderr of W per cycle, in units of k_B T.
    """
    rng = np.random.default_rng(seed)
    dt = tau / n_steps

    # Bimodal initial condition: half in left well, half in right well.
    a_start = 8.0
    x_min = math.sqrt(a_start)   # right well minimum
    n_left = n_traj // 2
    n_right = n_traj - n_left
    x = np.concatenate([
        rng.normal(-x_min, 1.0 / math.sqrt(2 * a_start), size=n_left),  # left well
        rng.normal(+x_min, 1.0 / math.sqrt(2 * a_start), size=n_right),  # right well
    ])

    W = np.zeros(n_traj)

    for step in range(n_steps):
        t = step * dt
        a_t, c_t = protocol(t, tau, *knobs[:5])
        a_tp, c_tp = protocol(t + dt, tau, *knobs[:5])

        # Work increment: dW = U(x, t+dt) - U(x, t) at fixed x (before the step).
        U_now, F_now = U_and_F(x, a_t, c_t)
        U_next_fixedx, _ = U_and_F(x, a_tp, c_tp)
        W += (U_next_fixedx - U_now)

        # Overdamped Langevin step (γ = k_BT = 1):
        noise = rng.normal(0.0, math.sqrt(2 * dt), size=n_traj)
        x = x + F_now * dt + noise

    return W.mean(), W.std() / math.sqrt(n_traj)


def fit_B(taus, q_means, q_errs):
    """Fit Q = ln2 + B/tau to simulated points, returning B and its stderr."""
    def f(tau, B):
        return KB_T_LN2 + B / tau
    popt, pcov = curve_fit(f, taus, q_means, p0=[PI_SQ], sigma=q_errs, absolute_sigma=True)
    return popt[0], math.sqrt(pcov[0, 0])


def experiment(name, knobs, taus, n_traj=400, seed=42):
    """Run a full (tau_sweep, fit) experiment for one knob configuration."""
    q_means, q_errs = [], []
    for tau in taus:
        m, s = simulate_cycle(tau, knobs, n_traj=n_traj, seed=seed)
        q_means.append(m)
        q_errs.append(max(s, 0.01))
    B, B_err = fit_B(np.array(taus), np.array(q_means), np.array(q_errs))
    return {
        "name": name,
        "knobs": knobs,
        "taus": taus,
        "q_means": q_means,
        "q_errs": q_errs,
        "B": B,
        "B_err": B_err,
        "B_pi_sq": B / PI_SQ,
    }


def main():
    # Use a coarser tau grid in dimensionless time.
    # In dimensionless units, "quasistatic" is tau >> 1 (relaxation time).
    # Use tau values comparable to the Berut range relative to the Kramers timescale.
    taus = [1.0, 2.0, 4.0, 8.0, 16.0]

    # Knob sweep — 20 experiments varying single knobs then pairs.
    #   Base: K1=0 (linear), K2=0 (linear), K3=0 (sequential), K4=6 (tilt), K5=0 (fully lowered)
    base = (0.0, 0.0, 0.0, 6.0, 0.0)
    experiments = []

    # E01: baseline
    experiments.append(experiment("E01_baseline", base, taus))
    # K1 variations
    experiments.append(experiment("E02_K1_sigmoidal_lowering", (1.0, 0.0, 0.0, 6.0, 0.0), taus))
    experiments.append(experiment("E03_K1_half_sigmoidal", (0.5, 0.0, 0.0, 6.0, 0.0), taus))
    # K2 variations
    experiments.append(experiment("E04_K2_sigmoidal_tilt", (0.0, 1.0, 0.0, 6.0, 0.0), taus))
    experiments.append(experiment("E05_K2_half_sigmoidal_tilt", (0.0, 0.5, 0.0, 6.0, 0.0), taus))
    # K3 variations
    experiments.append(experiment("E06_K3_light_overlap", (0.0, 0.0, 0.25, 6.0, 0.0), taus))
    experiments.append(experiment("E07_K3_heavy_overlap", (0.0, 0.0, 0.5, 6.0, 0.0), taus))
    # K4 variations
    experiments.append(experiment("E08_K4_strong_tilt", (0.0, 0.0, 0.0, 8.0, 0.0), taus))
    experiments.append(experiment("E09_K4_weak_tilt", (0.0, 0.0, 0.0, 4.0, 0.0), taus))
    # K5 variations
    experiments.append(experiment("E10_K5_residual_25pct", (0.0, 0.0, 0.0, 6.0, 0.25), taus))
    experiments.append(experiment("E11_K5_residual_50pct", (0.0, 0.0, 0.0, 6.0, 0.50), taus))
    # Pair combinations (Phase 2.5)
    experiments.append(experiment("E12_K1K2_both_sigmoidal", (1.0, 1.0, 0.0, 6.0, 0.0), taus))
    experiments.append(experiment("E13_K1K3_sigmoidal+overlap", (1.0, 0.0, 0.5, 6.0, 0.0), taus))
    experiments.append(experiment("E14_K2K5_sigmoidal+residual", (0.0, 1.0, 0.0, 6.0, 0.25), taus))
    experiments.append(experiment("E15_K3K5_overlap+residual", (0.0, 0.0, 0.5, 6.0, 0.25), taus))
    # Best-guess optimised (heuristic, matching the authors' description)
    experiments.append(experiment("E16_best_guess_optimised", (0.7, 0.7, 0.2, 7.0, 0.1), taus))
    # Worst-case adversarial
    experiments.append(experiment("E17_adversarial", (1.0, 1.0, 0.0, 4.0, 0.5), taus))
    # Symmetric (for Proesmans cross-check)
    experiments.append(experiment("E18_symmetric_optimal_proxy", (0.5, 0.5, 0.3, 6.0, 0.0), taus))
    # Two seed-stability checks
    experiments.append(experiment("E19_baseline_seed43", base, taus, seed=43))
    experiments.append(experiment("E20_baseline_seed44", base, taus, seed=44))
    # Larger tau grid run on baseline
    experiments.append(experiment("E21_baseline_coarse_tau", base, [0.5, 1.0, 2.0, 4.0, 8.0]))

    # Save simulated curves
    with open(SIMDATA_PATH, "w") as f:
        f.write("exp,tau,q_mean,q_err,knob_K1,knob_K2,knob_K3,knob_K4,knob_K5\n")
        for r in experiments:
            for tau, m, s in zip(r["taus"], r["q_means"], r["q_errs"]):
                f.write(f"{r['name']},{tau},{m:.4f},{s:.4f},{r['knobs'][0]},{r['knobs'][1]},{r['knobs'][2]},{r['knobs'][3]},{r['knobs'][4]}\n")

    # Append rows to results.tsv
    lines = []
    for r in experiments:
        status = "KEEP"
        notes = f"knobs={r['knobs']}, B={r['B']:.3f}±{r['B_err']:.3f}, B/pi^2={r['B_pi_sq']:.3f}"
        lines.append("\t".join([
            r["name"],
            "2" if r["name"] <= "E11" else "2.5" if r["name"] <= "E15" else "2",
            f"Phase 2 simulator: {r['name']}",
            "Brownian-dynamics-quartic",
            "42",
            "B_sim_in_units_of_pi_sq",
            f"{r['B_pi_sq']:.4f}",
            f"{(r['B'] - 1.96*r['B_err']) / PI_SQ:.4f}",
            f"{(r['B'] + 1.96*r['B_err']) / PI_SQ:.4f}",
            status,
            notes,
        ]))

    with open(RESULTS_PATH, "a") as f:
        for line in lines:
            f.write(line + "\n")

    # Print summary
    print("Phase 2 simulator sweep complete.")
    print(f"{'Name':<40}  {'B (k_BT.s)':>11}  {'B/π²':>8}  {'K1':>4} {'K2':>4} {'K3':>4} {'K4':>4} {'K5':>4}")
    for r in sorted(experiments, key=lambda r: r["B_pi_sq"]):
        print(f"{r['name']:<40}  {r['B']:>10.3f}   {r['B_pi_sq']:>8.3f}  {r['knobs'][0]:>4} {r['knobs'][1]:>4} {r['knobs'][2]:>4} {r['knobs'][3]:>4} {r['knobs'][4]:>4}")

    # Compare to empirical
    B_emp = 8.269
    B_emp_pi = B_emp / PI_SQ
    print(f"\nEmpirical (E00): B = {B_emp:.3f} k_BT·s = {B_emp_pi:.3f} π²")
    Bs_sim = sorted([r["B_pi_sq"] for r in experiments])
    print(f"Simulator sweep range: B/π² ∈ [{min(Bs_sim):.3f}, {max(Bs_sim):.3f}]")
    print(f"Simulator median B/π² = {Bs_sim[len(Bs_sim)//2]:.3f}")


if __name__ == "__main__":
    main()
