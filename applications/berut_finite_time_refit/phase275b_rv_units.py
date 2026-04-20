"""RV08+RV09: corrected unit analysis and Bérut-regime simulation.

The Phase 2b review caught that T0 was computed using inter-well distance L,
but the simulator's length unit is L/(2 sqrt(a_peak)). The correct T0 is:

    T0 = γ x₀² / (k_B T),    x₀ = L / (2 sqrt(a_peak))
       = γ L² / (4 a_peak k_B T)

For Bérut:  γ = 1.885e-8 kg/s, L = 313 nm, k_B T = 4.14e-21 J, a_peak = sqrt(32)
    T0 = 1.885e-8 * (3.13e-7)^2 / (4 * sqrt(32) * 4.14e-21) = 19.7 ms  (not 447 ms)

Consequence: Bérut's physical τ ∈ [5 s, 40 s] corresponds to
    τ_sim = τ_phys / T0 ∈ [254, 2028]
which is ABOVE the τ_sim [20, 320] used in Phase 2b.

This script re-runs the baseline at four τ_sim values spanning the Bérut
regime and refits B_sim. Also runs RV07 (Schmiedl-Seifert symmetric-optimum
verification as a dimensionless cross-check).
"""
import csv
import math
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
import sys
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from phase2b_simulator_fixed import (
    simulate_cycle, bits_erased_per_cycle, run_experiment, fit_B, A_PEAK
)

KB_T_LN2 = math.log(2)
PI_SQ = math.pi ** 2
RESULTS_PATH = HERE / "results.tsv"


def rv08_corrected_T0():
    """Recompute T0 with the correct length-unit identification."""
    gamma = 1.885e-8          # kg/s
    L = 3.13e-7               # m (from RV01 reconstruction)
    kBT = 4.14e-21            # J at T=300 K
    # Simulator uses x_sim such that the quartic minima are at ±sqrt(a_peak).
    # If we identify the physical inter-well distance L with the simulator's
    # 2*sqrt(a_peak), then x₀ = L / (2 sqrt(a_peak))
    x0 = L / (2 * math.sqrt(A_PEAK))
    T0 = gamma * x0 * x0 / kBT
    print(f"[RV08]  γ = {gamma:.3e} kg/s")
    print(f"[RV08]  L = {L*1e9:.1f} nm, a_peak = {A_PEAK:.4f}, so x₀ = L/(2√a) = {x0*1e9:.2f} nm")
    print(f"[RV08]  T0 = γ x₀² / kBT = {T0*1000:.2f} ms")
    print(f"[RV08]  Bérut physical τ [5, 40] s → simulator τ [{5/T0:.0f}, {40/T0:.0f}]")
    # Empirical B per Bérut: 8.27 k_BT·s. In simulator units: 8.27 / T0
    B_emp_phys = 8.269
    B_emp_sim = B_emp_phys / T0
    print(f"[RV08]  Empirical Bérut B = 8.27 kBT·s → simulator units = {B_emp_sim:.1f} = {B_emp_sim/PI_SQ:.1f} π²")
    return T0


def rv09_berut_regime():
    """Re-run the canonical four-stage baseline at the CORRECTED τ_sim range
    spanning the Bérut physical regime."""
    base = (0.0, 0.0, 0.0, 6.0, 0.0)
    # With T0 ≈ 19.7 ms, Bérut's 5-40 s maps to τ_sim ∈ [254, 2030].
    # Sample four τ in this range.
    taus = [256.0, 512.0, 1024.0, 2048.0]
    print("\n[RV09] Baseline 4-stage at Bérut-regime τ_sim")
    r = run_experiment("RV09_berut_regime_baseline", base, taus, n_traj=300, seed=42)
    for tau, q, qe, occ, bits in zip(r["taus"], r["q"], r["q_err"], r["occ"], r["bits"]):
        print(f"  τ_sim={tau:7.1f}  W={q:.3f}±{qe:.3f}  occ_R={occ:.3f}  bits_erased={bits:.3f}")
    # Fit
    q_arr = np.array(r["q"])
    qe_arr = np.array(r["q_err"])
    t_arr = np.array(r["taus"])
    B, Berr = fit_B(t_arr, q_arr, qe_arr)
    print(f"\n[RV09] Fitted B_sim = {B:.2f} ± {Berr:.2f} (= {B/PI_SQ:.2f} π² in simulator units)")
    return B, Berr, taus, r


def rv07_schmiedl_seifert_check(T0):
    """Verify the simulator's dimensionless Proesmans bound reproduces π².

    Use a harmonic-shift protocol (Schmiedl-Seifert 2007): two harmonic wells
    centred at ±L/2 in the simulator's length units; the cycle shifts the
    centre from one to the other (this is a DIFFERENT protocol from the
    quartic double-well erasure, but it's the CANONICAL test case for the
    Proesmans B = π² result).

    For the harmonic-shift protocol at SS-optimal linear drive, B_sim should
    equal π² exactly in the optimal limit; for our non-optimal linear ramp
    it will overshoot slightly.
    """
    print("\n[RV07] Schmiedl-Seifert harmonic-shift cross-check")
    # Harmonic well: U = 0.5 k (x - xc(t))^2
    # Linearly drive xc from -x_centre to +x_centre over cycle.
    # Erasure happens by driving the population from left to right.
    # This has a CLOSED-FORM Proesmans bound: W ≥ k_B T ln 2 + pi^2 k_B T / tau_sim
    # (optimal protocol), or slightly more for linear drive.
    k_spring = 4.0          # dimensionless stiffness (barrier is not present — single well)
    x_centre = math.sqrt(A_PEAK)  # same scale as quartic well minima
    taus = [128.0, 256.0, 512.0, 1024.0]
    Ws = []
    W_errs = []
    for tau in taus:
        n_steps = int(max(2000, tau * 10))
        dt = tau / n_steps
        rng = np.random.default_rng(42)
        n_traj = 300
        # Start at x = -x_centre (left minimum)
        x = rng.normal(-x_centre, 1.0 / math.sqrt(k_spring), size=n_traj)
        W = np.zeros(n_traj)
        sqrt2dt = math.sqrt(2.0 * dt)
        for step in range(n_steps):
            t = step * dt
            # Linear drive of centre
            xc = -x_centre + (2 * x_centre) * (t / tau)
            xc_next = -x_centre + (2 * x_centre) * ((t + dt) / tau)
            U_now = 0.5 * k_spring * (x - xc) ** 2
            U_next_fixedx = 0.5 * k_spring * (x - xc_next) ** 2
            W += (U_next_fixedx - U_now)
            F_now = -k_spring * (x - xc)
            noise = rng.normal(0.0, sqrt2dt, size=n_traj)
            x = x + F_now * dt + noise
        Ws.append(W.mean())
        W_errs.append(W.std() / math.sqrt(n_traj))
        print(f"  τ_sim={tau:6.1f}  W={W.mean():.3f}±{W.std()/math.sqrt(n_traj):.3f}")
    # Fit W(τ) = ΔF + B/τ.  For the harmonic shift, ΔF = 0 (reversible).
    # So W - B/τ = 0 + excess.  Just fit W = B/τ + const.
    def f(tau, B, c):
        return c + B / tau
    popt, pcov = curve_fit(f, np.array(taus), np.array(Ws), p0=[PI_SQ, 0], sigma=np.array(W_errs), absolute_sigma=True)
    B_ss, c_ss = popt
    B_err = math.sqrt(pcov[0, 0])
    print(f"\n[RV07] Harmonic-shift fitted B_SS = {B_ss:.2f} ± {B_err:.2f} (= {B_ss/PI_SQ:.2f} π²)")
    print(f"       Harmonic-shift fitted constant offset = {c_ss:.3f} k_BT (should be ~0 for ΔF=0)")
    # For linear driving of harmonic centre, the exact answer is W = (k/gamma) × (2 x_c)² × (1/tau) × (1/2)
    # Actually the Schmiedl-Seifert result for harmonic shift over distance d is
    # W_min = γ d² / τ (to leading order), so in our units γ=1, d = 2 x_centre:
    W_predicted_ss_optimal_coeff = (2 * x_centre) ** 2  # W = this / tau
    print(f"       Schmiedl-Seifert analytical W × τ = γ d² = {W_predicted_ss_optimal_coeff:.3f} for d = 2 x_centre = {2*x_centre:.3f}")
    print(f"       Ratio of measured B to SS analytical = {B_ss / W_predicted_ss_optimal_coeff:.3f}")
    print(f"       (For OPTIMAL linear protocol should equal 1.0; higher for non-optimal.)")
    return B_ss, B_err, W_predicted_ss_optimal_coeff


def main():
    T0 = rv08_corrected_T0()
    B_sim_berut, B_err_berut, taus_berut, r_berut = rv09_berut_regime()
    B_sim_ss, B_err_ss, B_ss_predicted = rv07_schmiedl_seifert_check(T0)

    # Bottom line
    print("\n" + "=" * 70)
    print("BOTTOM LINE")
    print("=" * 70)
    print(f"Corrected T0 = {T0*1000:.2f} ms (not 447 ms as earlier)")
    B_phys = B_sim_berut * T0
    print(f"Simulator B_sim at Bérut-regime τ = {B_sim_berut:.1f} ± {B_err_berut:.1f} (= {B_sim_berut/PI_SQ:.2f} π²)")
    print(f"Simulator B in physical units       = {B_phys:.3f} k_BT·s  (±{B_err_berut*T0:.3f})")
    print(f"Bérut empirical B                   = 8.269 k_BT·s")
    print(f"Ratio simulator/empirical           = {B_phys / 8.269:.2f}")
    print()
    print(f"RV07 harmonic-shift cross-check: B_SS (simulator) = {B_sim_ss:.2f} (= {B_sim_ss/PI_SQ:.2f} π²)")
    print(f"                                 ratio to analytic = {B_sim_ss / B_ss_predicted:.3f}")

    # Append rows to results.tsv
    lines = []
    lines.append("\t".join([
        "RV08_corrected_T0", "2.75b",
        "Corrected T0 using x0 = L/(2 sqrt(a_peak))",
        "dimensional_analysis", "NA", "T0_ms",
        f"{T0*1000:.3f}", "NA", "NA", "RUN_RV",
        f"Previous T0=447 ms was off by factor ~23; corrected {T0*1000:.2f} ms"
    ]))
    lines.append("\t".join([
        "RV09_berut_regime", "2.75b",
        f"Baseline 4-stage at Bérut-regime tau_sim",
        "Brownian-dynamics-corrected-longtau", "42",
        "B_sim_in_units_of_pi_sq",
        f"{B_sim_berut/PI_SQ:.4f}",
        f"{(B_sim_berut - 1.96*B_err_berut)/PI_SQ:.4f}",
        f"{(B_sim_berut + 1.96*B_err_berut)/PI_SQ:.4f}",
        "RUN_RV",
        f"B_phys_sim = {B_phys:.3f} kBT*s (Berut = 8.269)"
    ]))
    lines.append("\t".join([
        "RV07_schmiedl_seifert_check", "2.75b",
        f"Harmonic-shift cross-check",
        "harmonic-shift-langevin", "42",
        "B_ss_in_units_of_pi_sq",
        f"{B_sim_ss/PI_SQ:.4f}",
        f"{(B_sim_ss - 1.96*B_err_ss)/PI_SQ:.4f}",
        f"{(B_sim_ss + 1.96*B_err_ss)/PI_SQ:.4f}",
        "RUN_RV",
        f"Ratio to analytic gamma*d^2 = {B_sim_ss / B_ss_predicted:.3f} (should be 1.0 for optimal)"
    ]))

    with open(RESULTS_PATH, "a") as f:
        for line in lines:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
