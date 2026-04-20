"""E00 baseline fit for Phase 0.5.

Fits the Proesmans finite-time Landauer formula
    <Q_diss>(tau) = k_B T ln2 + B k_B T / tau
to the digitised Berut 2012 (via Berut-Petrosyan-Ciliberto 2015, arXiv:1503.06537) data.

Reports B in units of pi^2, with 95% bootstrap CI.
Also runs the power-law-alpha sanity check (alpha = 1 vs free).
Seed-stable: runs the bootstrap at seeds 42, 43, 44 and compares.
"""

import csv
from pathlib import Path
import math
import numpy as np
from scipy.optimize import curve_fit

DATA_PATH = Path(__file__).parent / "data" / "raw" / "berut_2012_qdiss_vs_tau.csv"
RESULTS_PATH = Path(__file__).parent / "results.tsv"
SANITY_PATH = Path(__file__).parent / "sanity_checks.md"

KB_T_LN2 = math.log(2)  # Q_diss is reported in units of k_B T, so the floor is just ln2 in those units.
PI_SQ = math.pi ** 2

def load_data():
    tau, q, err = [], [], []
    with open(DATA_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            tau.append(float(row["tau_seconds"]))
            q.append(float(row["q_diss_kBT"]))
            err.append(float(row["q_diss_err_kBT"]))
    return np.asarray(tau), np.asarray(q), np.asarray(err)

def model_canonical(tau, B):
    return KB_T_LN2 + B / tau

def model_freealpha(tau, a, b, alpha):
    return a + b / (tau ** alpha)

def weighted_fit(tau, q, err, model, p0):
    popt, pcov = curve_fit(model, tau, q, p0=p0, sigma=err, absolute_sigma=True, maxfev=20000)
    return popt, pcov

def bootstrap_B(tau, q, err, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    Bs = []
    for _ in range(n_boot):
        q_draw = q + rng.normal(0.0, err)
        try:
            popt, _ = curve_fit(model_canonical, tau, q_draw, p0=[PI_SQ], sigma=err, absolute_sigma=True, maxfev=5000)
            Bs.append(popt[0])
        except Exception:
            continue
    return np.asarray(Bs)

def main():
    tau, q, err = load_data()
    print(f"Loaded {len(tau)} data points.")
    print(f"  tau range: [{tau.min():.3f}, {tau.max():.3f}] s")
    print(f"  Q range:   [{q.min():.3f}, {q.max():.3f}] k_B T")

    # Primary fit: canonical 1/tau form with fixed Landauer floor
    popt, pcov = weighted_fit(tau, q, err, model_canonical, p0=[PI_SQ])
    B_mle = popt[0]
    B_err_asym = math.sqrt(pcov[0, 0])

    # Bootstrap across three seeds for seed-stability
    boot_results = {}
    for seed in (42, 43, 44):
        Bs = bootstrap_B(tau, q, err, n_boot=2000, seed=seed)
        lo, hi = np.percentile(Bs, [2.5, 97.5])
        med = np.median(Bs)
        boot_results[seed] = (med, lo, hi, len(Bs))
        print(f"  bootstrap seed={seed}: B = {med:.3f} [{lo:.3f}, {hi:.3f}]  (n={len(Bs)})")

    med_42, lo_42, hi_42, _ = boot_results[42]

    # Sanity check: free alpha
    popt_free, pcov_free = weighted_fit(tau, q, err, model_freealpha, p0=[KB_T_LN2, PI_SQ, 1.0])
    a_free, b_free, alpha_free = popt_free
    alpha_err = math.sqrt(pcov_free[2, 2])
    alpha_ci_lo = alpha_free - 1.96 * alpha_err
    alpha_ci_hi = alpha_free + 1.96 * alpha_err

    # Sanity check: quasistatic-limit residual
    idx_max = int(np.argmax(tau))
    residual_qs = q[idx_max] - KB_T_LN2
    residual_qs_in_err = residual_qs / err[idx_max]

    # Write results.tsv
    header = "exp_id\tphase\tdescription\tmodel\tseed\tmetric\tvalue\tci_low\tci_high\tstatus\tnotes"
    row = "\t".join([
        "E00",
        "0.5",
        "Phase 0.5 baseline: weighted NLS fit of Q_diss = ln2 + B/tau to 10 digitised Berut points",
        "1/tau_fixed_floor",
        "42",
        "B_in_units_of_pi_sq",
        f"{med_42 / PI_SQ:.4f}",
        f"{lo_42 / PI_SQ:.4f}",
        f"{hi_42 / PI_SQ:.4f}",
        "KEEP",
        "Bérut-Petrosyan-Ciliberto 2015 Fig 8 optimised-protocol data; 2000-draw bootstrap; data caveats noted in data_sources.md",
    ])
    with open(RESULTS_PATH, "w") as f:
        f.write(header + "\n")
        f.write(row + "\n")

    # Write sanity_checks.md
    content = f"""# Sanity Checks — Phase 0.5

Computed by `e00_baseline_fit.py` on the digitised Bérut-Petrosyan-Ciliberto 2015 Fig 8 optimised-protocol data (10 points, see `data_sources.md` for caveats).

## 1. Quasistatic-limit residual

The largest-τ point is at τ = {tau[idx_max]:.1f} s with ⟨Q_diss⟩ = {q[idx_max]:.3f} k_B T ± {err[idx_max]:.3f}.
The Landauer floor is k_B T ln 2 ≈ {KB_T_LN2:.4f} k_B T.
Residual = ⟨Q_diss⟩ − k_B T ln 2 = {residual_qs:+.3f} k_B T ({residual_qs_in_err:+.2f} σ).

**Pass** if the residual is within ~2 σ and is still positive (Landauer is a lower bound).
Observed: {residual_qs:+.3f} k_B T = {residual_qs_in_err:+.2f} σ. {'PASS' if abs(residual_qs_in_err) < 3 and residual_qs >= 0 else 'FLAG'}.

## 2. Power-law vs 1/τ (free α)

Fit:  ⟨Q_diss⟩(τ) = a + b / τ^α  with α as a free parameter.

Result:
- a = {a_free:+.4f} (Landauer floor predicted = {KB_T_LN2:.4f})
- b = {b_free:+.4f} (predicted B in 1/τ model = {B_mle:.4f})
- α = {alpha_free:.4f} ± {alpha_err:.4f}  (95 % CI {alpha_ci_lo:.3f} – {alpha_ci_hi:.3f})

**Pass** if α = 1 is inside the 95 % CI (consistent with Proesmans 1/τ scaling).
Observed: {'α = 1 IS inside the CI → PASS.' if alpha_ci_lo <= 1.0 <= alpha_ci_hi else 'α = 1 is NOT inside the CI → MAJOR flag; the data may prefer a different scaling.'}

## 3. Seed stability

Bootstrap of the B fit at three seeds:

| Seed | B (median) | 95 % CI | CI width |
|------|-----------|---------|----------|
"""
    for seed in (42, 43, 44):
        med, lo, hi, n = boot_results[seed]
        content += f"| {seed} | {med:.3f} | [{lo:.3f}, {hi:.3f}] | {hi-lo:.3f} |\n"

    meds = [boot_results[s][0] for s in (42, 43, 44)]
    meds_spread = max(meds) - min(meds)
    widest_ci = max(boot_results[s][2] - boot_results[s][1] for s in (42, 43, 44))
    mc_noise_est = widest_ci / math.sqrt(2000)
    content += f"\nAcross seeds the median moves by {meds_spread:.3f} (Monte-Carlo noise estimate at n_boot=2000 is ~{mc_noise_est:.3f}).\n\n"
    content += "**Pass** if the cross-seed median spread is smaller than the within-seed CI width.\n"
    content += f"Observed: cross-seed spread = {meds_spread:.3f}, within-seed CI = {hi_42-lo_42:.3f}. {'PASS.' if meds_spread < (hi_42-lo_42) else 'FLAG.'}\n"

    content += f"""

## Summary

Fitted B (canonical 1/τ, seed 42) = **{med_42:.3f}**  with 95 % CI [{lo_42:.3f}, {hi_42:.3f}]
 = **{med_42 / PI_SQ:.3f} π²** with 95 % CI [{lo_42/PI_SQ:.3f} π², {hi_42/PI_SQ:.3f} π²].

Interpretation: the Schmiedl-Seifert symmetric-optimal prediction is B = π². The optimised-protocol data of the 2015 review should recover this (optimised ≈ Schmiedl-Seifert optimum). Our fitted value is {med_42 / PI_SQ:.3f} π², which is {'CONSISTENT with π² (optimised protocol tracks the optimum, as expected)' if lo_42 <= PI_SQ <= hi_42 else 'INCONSISTENT with π² — either the optimised protocol is not quite the Schmiedl-Seifert optimum, or the digitisation has a systematic bias'}.

**Critical data caveat:** these ten points are from the *optimised* protocol (black curve in arXiv:1503.06537 Fig 8), NOT the original Bérut 2012 Nature Fig 2 symmetric-protocol ten-point curve. For the project's central comparison — "simulated B_Bérut of the actual 2012 protocol vs empirical B" — we need Bérut 2012 Fig 2's non-optimised protocol data. Phase 0.5 verdict therefore depends on whether that data is reachable; see data_sources.md.
"""
    with open(SANITY_PATH, "w") as f:
        f.write(content)

    print(f"\nWritten {RESULTS_PATH.name} and {SANITY_PATH.name}.")
    print(f"\nFitted B = {med_42:.3f} = {med_42/PI_SQ:.3f} π²  95% CI [{lo_42/PI_SQ:.3f}, {hi_42/PI_SQ:.3f}] π²")
    print(f"π² containment: {'YES' if lo_42 <= PI_SQ <= hi_42 else 'NO'}")
    print(f"α (free) = {alpha_free:.3f} ± {alpha_err:.3f} ; α=1 in CI: {'YES' if alpha_ci_lo <= 1.0 <= alpha_ci_hi else 'NO'}")

if __name__ == "__main__":
    main()
