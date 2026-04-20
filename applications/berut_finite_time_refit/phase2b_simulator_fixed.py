"""Phase 2b — fixed Brownian-dynamics simulator.

Corrects the three bugs from Phase 2 that Phase 2.75 review caught:

  1. Barrier height: the potential U = x^4/4 - a x^2 / 2 has barrier a^2 / 4,
     NOT a. Previous a = 8 gave a 16 k_BT barrier; to match Bérut's 8 k_BT
     barrier we need a = sqrt(32) = 4*sqrt(2) ≈ 5.657.

  2. Dimensionless-time regime: τ_sim ∈ [1, 16] of Phase 2 was below the
     Bérut regime. With the corrected a we run τ_sim ∈ {20, 40, 80, 160, 320}
     which covers and exceeds the equivalent of Bérut 5–40 s.

  3. Erasure completeness: we explicitly track final-well occupancy and
     bits-erased-per-cycle. Any run below 0.9 bits is marked INCOMPLETE and
     excluded from the B fit.

After running, we also convert B_sim to physical B via the unit identification
τ_phys [s] = τ_sim × T0, where T0 = γ L^2 / (k_B T) ≈ 0.446 s for the
Bérut apparatus (see RV01).
"""
import csv
import math
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

HERE = Path(__file__).parent
RESULTS_PATH = HERE / "results.tsv"
SIMDATA_PATH = HERE / "data" / "simulated_qdiss_vs_tau_fixed.csv"

KB_T_LN2 = math.log(2)
PI_SQ = math.pi ** 2
A_PEAK = math.sqrt(32.0)  # barrier = a^2/4 = 8 k_BT
T0_BERUT_S = 0.4468        # γ L^2 / (k_B T) for Bérut params (RV01 gave τ_rel = 0.2234 s; T0 = 2 τ_rel)


def ramp(t, t_start, t_end, shape_sigma):
    """Monotone ramp from 0→1 over [t_start, t_end]; sigma in [0,1]
    interpolates linear (0) → sigmoidal (1)."""
    if t <= t_start:
        return 0.0
    if t >= t_end:
        return 1.0
    u = (t - t_start) / (t_end - t_start)
    linear = u
    sig = 1.0 / (1.0 + math.exp(-8.0 * (u - 0.5)))
    lo = 1.0 / (1.0 + math.exp(4.0))
    hi = 1.0 / (1.0 + math.exp(-4.0))
    sig = (sig - lo) / (hi - lo)
    return (1 - shape_sigma) * linear + shape_sigma * sig


def protocol(t, tau, K1, K2, K3, K4, K5):
    """Canonical four-stage Landauer erasure protocol:
       stage 1  [0,   τ/4]:  lower barrier (a: a_peak → a_mid), no tilt
       stage 2a [τ/4, τ/2]:  tilt rises (c: 0 → c_max), barrier held low
       stage 2b [τ/2, 3τ/4]: barrier raises (a: a_mid → a_peak), tilt held at c_max
       stage 3  [3τ/4, τ]:   tilt released (c: c_max → 0), barrier held high

    The critical step is 2b: the barrier re-forms while the tilt is still on,
    trapping the population on one side before the tilt is released. This was
    missing from the earlier three-stage version, which let stage-3 thermal
    hopping re-equilibrate the distribution during the short low-barrier
    window.

    K1 = shape of a(t) ramps (linear → sigmoidal)
    K2 = shape of c(t) ramps
    K3 = deprecated in 4-stage form (kept for signature compatibility)
    K4 = c_max (tilt amplitude)
    K5 = residual barrier fraction during stages 2a-2b (0 = fully lowered)
    """
    a_peak = A_PEAK
    a_mid = K5 * a_peak
    c_max = K4

    t1_end = tau / 4
    t2a_end = tau / 2
    t2b_end = 3 * tau / 4
    # stage 3: from t2b_end to tau

    if t < t1_end:
        # Stage 1: lower barrier
        prog = ramp(t, 0.0, t1_end, K1)
        a_t = a_peak - (a_peak - a_mid) * prog
        c_t = 0.0
    elif t < t2a_end:
        # Stage 2a: tilt rises
        prog = ramp(t, t1_end, t2a_end, K2)
        a_t = a_mid
        c_t = c_max * prog
    elif t < t2b_end:
        # Stage 2b: barrier re-forms while tilt holds
        prog = ramp(t, t2a_end, t2b_end, K1)
        a_t = a_mid + (a_peak - a_mid) * prog
        c_t = c_max
    else:
        # Stage 3: tilt released, barrier held
        prog = ramp(t, t2b_end, tau, K2)
        a_t = a_peak
        c_t = c_max * (1 - prog)
    return a_t, c_t


def U_F(x, a, c):
    U = 0.25 * x ** 4 - 0.5 * a * x ** 2 + c * x
    F = -(x ** 3 - a * x + c)
    return U, F


def simulate_cycle(tau, knobs, n_traj=400, n_steps=None, seed=42):
    """Returns (<W>, stderr<W>, occupancy_right)."""
    if n_steps is None:
        # Roughly 20 steps per unit dimensionless time, capped
        n_steps = min(20000, max(800, int(tau * 30)))
    rng = np.random.default_rng(seed)
    dt = tau / n_steps

    a0 = A_PEAK
    x_well = math.sqrt(a0)  # well minima at ±sqrt(a)
    n_left = n_traj // 2
    n_right = n_traj - n_left
    sigma_well = 1.0 / math.sqrt(2 * a0)  # harmonic width inside well
    x = np.concatenate([
        rng.normal(-x_well, sigma_well, size=n_left),
        rng.normal(+x_well, sigma_well, size=n_right),
    ])

    W = np.zeros(n_traj)
    sqrt2dt = math.sqrt(2.0 * dt)
    for step in range(n_steps):
        t = step * dt
        a_t, c_t = protocol(t, tau, *knobs[:5])
        a_tp, c_tp = protocol(t + dt, tau, *knobs[:5])
        U_now, F_now = U_F(x, a_t, c_t)
        U_next_fixedx, _ = U_F(x, a_tp, c_tp)
        W += (U_next_fixedx - U_now)
        noise = rng.normal(0.0, sqrt2dt, size=n_traj)
        x = x + F_now * dt + noise
    occ_right = float((x > 0).mean())
    return W.mean(), W.std() / math.sqrt(n_traj), occ_right


def bits_erased_per_cycle(occ_right):
    """Initial entropy is 1 bit (50/50 mixture). Final entropy is H(occ_right)."""
    p = max(1e-9, min(1 - 1e-9, occ_right))
    H = -p * math.log2(p) - (1 - p) * math.log2(1 - p)
    return 1.0 - H


def run_experiment(name, knobs, taus, n_traj=400, seed=42):
    out = {"name": name, "knobs": knobs, "taus": list(taus), "q": [], "q_err": [], "occ": [], "bits": []}
    for tau in taus:
        m, s, occ = simulate_cycle(tau, knobs, n_traj=n_traj, seed=seed)
        out["q"].append(m)
        out["q_err"].append(max(s, 1e-3))
        out["occ"].append(occ)
        out["bits"].append(bits_erased_per_cycle(occ))
    return out


def fit_B(taus, q, q_err):
    def f(tau, B):
        return KB_T_LN2 + B / tau
    popt, pcov = curve_fit(f, taus, q, p0=[PI_SQ], sigma=q_err, absolute_sigma=True)
    return popt[0], math.sqrt(pcov[0, 0])


def main():
    # Use longer taus to reach the Bérut regime and allow barrier crossing
    taus = [20.0, 40.0, 80.0, 160.0, 320.0]

    base = (0.0, 0.0, 0.0, 6.0, 0.0)  # linear ramps, no overlap, c_max=6, fully lowered
    experiments = []

    experiments.append(run_experiment("E01B_baseline", base, taus))
    experiments.append(run_experiment("E02B_K1_sigmoidal", (1.0, 0.0, 0.0, 6.0, 0.0), taus))
    experiments.append(run_experiment("E03B_K2_sigmoidal_tilt", (0.0, 1.0, 0.0, 6.0, 0.0), taus))
    experiments.append(run_experiment("E04B_K3_overlap", (0.0, 0.0, 0.5, 6.0, 0.0), taus))
    experiments.append(run_experiment("E05B_K4_stronger_tilt", (0.0, 0.0, 0.0, 8.0, 0.0), taus))
    experiments.append(run_experiment("E06B_K4_weaker_tilt", (0.0, 0.0, 0.0, 4.0, 0.0), taus))
    experiments.append(run_experiment("E07B_K5_residual", (0.0, 0.0, 0.0, 6.0, 0.25), taus))
    experiments.append(run_experiment("E08B_best_guess_optimised", (0.7, 0.7, 0.2, 7.0, 0.0), taus))
    experiments.append(run_experiment("E09B_baseline_seed43", base, taus, seed=43))
    experiments.append(run_experiment("E10B_baseline_seed44", base, taus, seed=44))

    print(f"{'name':<30}  erasure-bits at each τ  →  B_sim  (kept?)")
    for r in experiments:
        bits_str = " ".join(f"{b:5.3f}" for b in r["bits"])
        # Select only points with ≥0.9 bits erased for the B fit
        mask = [b >= 0.9 for b in r["bits"]]
        if sum(mask) >= 3:
            fit_taus = np.array([t for t, m in zip(r["taus"], mask) if m])
            fit_q = np.array([q for q, m in zip(r["q"], mask) if m])
            fit_qe = np.array([e for e, m in zip(r["q_err"], mask) if m])
            B, Berr = fit_B(fit_taus, fit_q, fit_qe)
            r["B"] = B
            r["Berr"] = Berr
            r["B_pi_sq"] = B / PI_SQ
            r["complete_fit"] = True
            print(f"{r['name']:<30}  {bits_str}  →  B={B:6.2f}±{Berr:4.2f}  ({B/PI_SQ:5.2f}π²)  KEEP")
        else:
            r["B"] = float("nan")
            r["Berr"] = float("nan")
            r["B_pi_sq"] = float("nan")
            r["complete_fit"] = False
            print(f"{r['name']:<30}  {bits_str}  →  INCOMPLETE erasure, excluded")

    # Save curves
    with open(SIMDATA_PATH, "w") as f:
        f.write("exp,tau,q,q_err,occ_right,bits_erased,K1,K2,K3,K4,K5\n")
        for r in experiments:
            for tau, q, qe, occ, bits in zip(r["taus"], r["q"], r["q_err"], r["occ"], r["bits"]):
                f.write(f"{r['name']},{tau},{q:.4f},{qe:.4f},{occ:.4f},{bits:.4f},{r['knobs'][0]},{r['knobs'][1]},{r['knobs'][2]},{r['knobs'][3]},{r['knobs'][4]}\n")

    # Append rows to results.tsv
    lines = []
    for r in experiments:
        status = "KEEP" if r["complete_fit"] else "REVERT"
        if r["complete_fit"]:
            B_phys = r["B"] * T0_BERUT_S
            notes = f"knobs={r['knobs']}, B_sim={r['B']:.2f}±{r['Berr']:.2f} ({r['B_pi_sq']:.2f}π²), B_phys={B_phys:.3f} kBT·s, mean_bits_erased={np.mean(r['bits']):.3f}"
            value = f"{r['B_pi_sq']:.4f}"
            lo = f"{(r['B'] - 1.96*r['Berr']) / PI_SQ:.4f}"
            hi = f"{(r['B'] + 1.96*r['Berr']) / PI_SQ:.4f}"
        else:
            notes = f"knobs={r['knobs']}, erasure incomplete (bits={r['bits']}); excluded from fit"
            value = "NaN"
            lo = "NaN"
            hi = "NaN"
        lines.append("\t".join([
            r["name"], "2", f"Phase 2b fixed: {r['name']}", "Brownian-dynamics-corrected",
            "42" if "seed" not in r["name"] else r["name"].split("seed")[1],
            "B_sim_in_units_of_pi_sq", value, lo, hi, status, notes,
        ]))

    with open(RESULTS_PATH, "a") as f:
        for line in lines:
            f.write(line + "\n")

    # Headline summary
    print()
    kept_B = [r["B_pi_sq"] for r in experiments if r["complete_fit"]]
    if kept_B:
        print(f"Simulator B_sim/π² range (complete-erasure runs only): [{min(kept_B):.2f}, {max(kept_B):.2f}]")
        print(f"Simulator median B_sim/π² = {np.median(kept_B):.2f}")
        B_emp_phys = 8.269  # k_B T · s  (E00 empirical fit)
        B_emp_sim = B_emp_phys / T0_BERUT_S
        print(f"\nEmpirical Bérut B_phys = {B_emp_phys:.3f} k_BT·s = {B_emp_sim/PI_SQ:.2f}π² in simulator-time units (T0={T0_BERUT_S} s)")
        B_phys_sim = np.median(kept_B) * PI_SQ * T0_BERUT_S
        print(f"Simulator median B in physical units: {B_phys_sim:.3f} k_BT·s")
        print(f"\nRatio B_sim_median / B_empirical = {B_phys_sim / B_emp_phys:.2f}")


if __name__ == "__main__":
    main()
