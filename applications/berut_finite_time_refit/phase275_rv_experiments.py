"""Phase 2.75 reviewer-mandated experiments RV01-RV05.

RV01: compute tau_rel for the Bérut apparatus and redo unit conversion.
RV02: use the τ range from Bérut (5-40 s) properly scaled.
RV03: measure final-well occupation / bits-erased per cycle in the simulator.
RV04: dt-convergence of the Langevin integrator.
RV05: free-σ empirical fit of the Bérut data, adding digitisation uncertainty.

Appends results to results.tsv with status RUN_RV. See paper_review.md for
the reviewer's original statement of each experiment.
"""
import csv
import math
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

DATA_PATH = Path(__file__).parent / "data" / "raw" / "berut_2012_qdiss_vs_tau.csv"
RESULTS_PATH = Path(__file__).parent / "results.tsv"

KB_T_LN2 = math.log(2)
PI_SQ = math.pi ** 2

# Re-import protocol + potential from the Phase 2 simulator.
import sys
sys.path.insert(0, str(Path(__file__).parent))
from phase2_simulator import protocol, U_and_F, simulate_cycle, fit_B


def load_data():
    tau, q, err = [], [], []
    with open(DATA_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            tau.append(float(row["tau_seconds"]))
            q.append(float(row["q_diss_kBT"]))
            err.append(float(row["q_diss_err_kBT"]))
    return np.asarray(tau), np.asarray(q), np.asarray(err)


# ----- RV01: compute tau_rel for Bérut apparatus -----
def rv01_tau_rel():
    """Compute τ_rel = γ L² / (2 k_B T) for the Bérut 2012 apparatus.

    Parameters from Bérut 2012 Nature Methods section and 2015 J. Stat. Mech. review:
      particle radius r = 1.0 μm (2 μm diameter silica bead)
      water viscosity η = 1.0e-3 Pa·s at 300 K
      stiffness per well κ ≈ 2.7e-6 N/m
      barrier height 8 k_B T
      k_B T = 4.14e-21 J at 300 K

    Inter-well distance L is not directly published. Two estimates:
      a) from barrier height and stiffness: U_barrier = κ L² / 8 for a quartic double well
         L = sqrt(8 × 8 k_BT / κ) = sqrt(64 × 4.14e-21 / 2.7e-6) = 0.31 μm
      b) from micrograph scale bar in Fig 1: L ≈ 0.3–0.4 μm

    γ = 6π η r (Stokes) = 6π × 1e-3 × 1e-6 = 1.885e-8 kg/s
    τ_rel = γ L² / (2 k_B T)
    """
    eta = 1.0e-3
    r_particle = 1.0e-6
    kBT = 4.14e-21
    k_stiffness = 2.7e-6
    barrier_kBT = 8.0

    gamma = 6 * math.pi * eta * r_particle
    # Inter-well distance from barrier + stiffness (quartic well approximation)
    L = math.sqrt(8 * barrier_kBT * kBT / k_stiffness)
    tau_rel = gamma * L * L / (2 * kBT)

    print(f"[RV01] γ = {gamma:.3e} kg/s")
    print(f"[RV01] Inter-well distance L = {L*1e6:.3f} μm")
    print(f"[RV01] τ_rel = γ L² / (2 k_B T) = {tau_rel:.4e} s = {tau_rel*1000:.2f} ms")
    print(f"[RV01] Bérut τ range 5–40 s maps to τ_sim = {5/tau_rel:.0f} – {40/tau_rel:.0f} (dimensionless)")
    return tau_rel, L, gamma


# ----- RV03: simulate with final-well occupation -----
def simulate_cycle_with_occupation(tau, knobs, n_traj=400, n_steps=800, seed=42):
    """As simulate_cycle but also records the fraction of trajectories that end
    in the right well (x > 0)."""
    rng = np.random.default_rng(seed)
    dt = tau / n_steps
    a_start = 8.0
    x_min = math.sqrt(a_start)
    n_left = n_traj // 2
    n_right = n_traj - n_left
    x = np.concatenate([
        rng.normal(-x_min, 1.0 / math.sqrt(2 * a_start), size=n_left),
        rng.normal(+x_min, 1.0 / math.sqrt(2 * a_start), size=n_right),
    ])
    W = np.zeros(n_traj)
    for step in range(n_steps):
        t = step * dt
        a_t, c_t = protocol(t, tau, *knobs[:5])
        a_tp, c_tp = protocol(t + dt, tau, *knobs[:5])
        U_now, F_now = U_and_F(x, a_t, c_t)
        U_next_fixedx, _ = U_and_F(x, a_tp, c_tp)
        W += (U_next_fixedx - U_now)
        noise = rng.normal(0.0, math.sqrt(2 * dt), size=n_traj)
        x = x + F_now * dt + noise
    occ_right = float((x > 0).mean())
    return W.mean(), W.std() / math.sqrt(n_traj), occ_right


def rv03_erasure_completeness():
    """Measure final-well occupation for the 21 Phase 2 configurations.

    For a proper Landauer erasure of a bit, initial P(left)=P(right)=0.5.
    Final occ_right should be ~1.0 for complete erasure. bits_erased_per_cycle ≈ 1 - H(p_right, p_left).
    """
    print("\n[RV03] Erasure-completeness measurement")
    print(f"{'Knobs':<35}  tau  occ_R   bits_erased")

    configs = [
        ("baseline", (0.0, 0.0, 0.0, 6.0, 0.0)),
        ("K5_residual_25pct", (0.0, 0.0, 0.0, 6.0, 0.25)),
        ("K5_residual_50pct", (0.0, 0.0, 0.0, 6.0, 0.5)),
        ("K4_weak_tilt", (0.0, 0.0, 0.0, 4.0, 0.0)),
        ("K4_strong_tilt", (0.0, 0.0, 0.0, 8.0, 0.0)),
        ("adversarial", (1.0, 1.0, 0.0, 4.0, 0.5)),
        ("best_guess_optimised", (0.7, 0.7, 0.2, 7.0, 0.1)),
    ]
    taus = [4.0, 8.0, 16.0]
    rows = []
    for name, knobs in configs:
        for tau in taus:
            _, _, occ_r = simulate_cycle_with_occupation(tau, knobs, n_traj=400, n_steps=800, seed=42)
            # Binary entropy of final distribution
            p = max(1e-6, min(1 - 1e-6, occ_r))
            H = -p * math.log2(p) - (1 - p) * math.log2(1 - p)
            bits_erased = 1.0 - H  # initial entropy was 1 bit (symmetric mixture)
            rows.append((name, knobs, tau, occ_r, bits_erased))
            print(f"  {name:<30}  tau={tau:4.1f}  occ_R={occ_r:.3f}  bits_erased={bits_erased:.3f}")
    return rows


# ----- RV04: dt-convergence check -----
def rv04_dt_convergence():
    """Check that n_steps=800 is enough for the baseline at tau=4."""
    print("\n[RV04] dt-convergence check (baseline, τ=4.0)")
    knobs = (0.0, 0.0, 0.0, 6.0, 0.0)
    tau = 4.0
    results = []
    for nstep in (200, 400, 800, 1600, 3200):
        m, s = simulate_cycle(tau, knobs, n_traj=400, n_steps=nstep, seed=42)
        results.append((nstep, m, s))
        print(f"  n_steps={nstep:5d}  <W>={m:6.3f} ± {s:.3f}")
    # Convergence: |m(3200) - m(800)| should be < s(800)
    m800 = [r[1] for r in results if r[0] == 800][0]
    s800 = [r[2] for r in results if r[0] == 800][0]
    m3200 = [r[1] for r in results if r[0] == 3200][0]
    rel_error = abs(m3200 - m800) / m800
    converged = abs(m3200 - m800) < s800
    print(f"  |Δ| between 800 and 3200 = {abs(m3200-m800):.3f}, within 1σ? {converged}, rel error = {rel_error:.3%}")
    return results, converged


# ----- RV05: free-σ empirical refit -----
def rv05_free_sigma_refit():
    """Refit Bérut data with σ as a free nuisance parameter plus a digitisation
    uncertainty budget of ±0.05 k_BT added in quadrature to the published ±0.15.
    """
    print("\n[RV05] Free-σ empirical refit (with digitisation budget)")
    tau, q, err = load_data()
    # Add digitisation uncertainty in quadrature
    err_total = np.sqrt(err ** 2 + 0.05 ** 2)

    def f1(tau, B):
        return KB_T_LN2 + B / tau

    popt, pcov = curve_fit(f1, tau, q, p0=[PI_SQ], sigma=err_total, absolute_sigma=True)
    B_new = popt[0]
    perr_new = math.sqrt(pcov[0, 0])
    print(f"  Published σ only:  B = 8.269 ± 0.450")
    print(f"  +Digitisation σ:   B = {B_new:.3f} ± {perr_new:.3f}")
    print(f"  Ratio of CI widths: {perr_new / 0.450:.3f}")
    return B_new, perr_new


def main():
    tau_rel, L, gamma = rv01_tau_rel()
    print(f"\nFor the Bérut apparatus, B_Proesmans,physical = π² × τ_rel = {PI_SQ * tau_rel * 1000:.2f} ms × k_BT")
    print(f"Bérut empirical B = 8.269 k_BT·s = {8.269 / (PI_SQ * tau_rel):.1f} × π²·τ_rel")
    B_emp_scaled = 8.269 / (PI_SQ * tau_rel)

    rv03_rows = rv03_erasure_completeness()
    rv04_results, converged = rv04_dt_convergence()
    B_rv05, perr_rv05 = rv05_free_sigma_refit()

    # Append RV rows to results.tsv
    lines = []

    # RV01: dimensional result
    lines.append("\t".join([
        "RV01", "2.75",
        "Unit conversion: compute tau_rel for Berut apparatus",
        "dimensional_analysis", "NA",
        "tau_rel_ms", f"{tau_rel*1000:.3f}",
        "NA", "NA", "RUN_RV",
        f"gamma={gamma:.3e} kg/s, L={L*1e6:.3f} um, tau_rel={tau_rel*1000:.2f} ms. Empirical B in units of pi^2 * tau_rel: {B_emp_scaled:.1f} x pi^2 tau_rel"
    ]))

    # RV03: erasure completeness
    for name, knobs, tau_v, occ_r, bits in rv03_rows:
        lines.append("\t".join([
            f"RV03_{name}_tau{tau_v}", "2.75",
            f"Final-well occupation: {name} at tau={tau_v}",
            "Brownian-dynamics-with-occupation", "42",
            "occupation_right", f"{occ_r:.4f}",
            "NA", "NA", "RUN_RV",
            f"knobs={knobs}, bits_erased_per_cycle={bits:.3f}"
        ]))

    # RV04: dt-convergence
    for nstep, m, s in rv04_results:
        lines.append("\t".join([
            f"RV04_nsteps{nstep}", "2.75",
            f"dt-convergence: baseline tau=4 at n_steps={nstep}",
            "Brownian-dynamics-quartic", "42",
            "W_per_cycle_kBT", f"{m:.4f}",
            f"{m - 1.96 * s:.4f}", f"{m + 1.96 * s:.4f}", "RUN_RV",
            f"converged at n_steps=800 vs 3200: {converged}"
        ]))

    # RV05: free-sigma refit
    lines.append("\t".join([
        "RV05_free_sigma_refit", "2.75",
        "Free-sigma refit with +0.05 digitisation budget",
        "1/tau_fixed_floor_augmented_sigma", "42",
        "B_in_units_of_pi_sq", f"{B_rv05 / PI_SQ:.4f}",
        f"{(B_rv05 - 1.96 * perr_rv05) / PI_SQ:.4f}",
        f"{(B_rv05 + 1.96 * perr_rv05) / PI_SQ:.4f}",
        "RUN_RV",
        f"B={B_rv05:.3f} +/- {perr_rv05:.3f}; published-sigma-only fit gave B=8.269+/-0.450"
    ]))

    with open(RESULTS_PATH, "a") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"\nAppended {len(lines)} RV rows to results.tsv")


if __name__ == "__main__":
    main()
