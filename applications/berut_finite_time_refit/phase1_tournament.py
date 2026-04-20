"""Phase 1 tournament for berut_finite_time_refit.

Four fundamentally different functional forms fitted to the same 10 Berut
points. Tournament records per-family AICc, residual-RMS, and recovered B (in
units of π² where applicable).

Families:
  F1  canonical Proesmans:  W = ln2 + B/tau
  F2  Van-Vu-Saito next order:  W = ln2 + B/tau + C/tau^2
  F3  free-exponent power law (linear-model sanity check):  W = a + b/tau^alpha
  F4  activated-process sanity check:  W = a + b * exp(-tau/tau0)
"""

import csv
import math
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

DATA_PATH = Path(__file__).parent / "data" / "raw" / "berut_2012_qdiss_vs_tau.csv"
RESULTS_PATH = Path(__file__).parent / "results.tsv"
TOURN_PATH = Path(__file__).parent / "tournament_results.csv"

KB_T_LN2 = math.log(2)
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

def f1(tau, B):
    return KB_T_LN2 + B / tau

def f2(tau, B, C):
    return KB_T_LN2 + B / tau + C / (tau ** 2)

def f3(tau, a, b, alpha):
    return a + b / (tau ** alpha)

def f4(tau, a, b, tau0):
    return a + b * np.exp(-tau / tau0)

def fit_family(model, p0, tau, q, err, name, k):
    popt, pcov = curve_fit(model, tau, q, p0=p0, sigma=err, absolute_sigma=True, maxfev=30000)
    pred = model(tau, *popt)
    residuals = q - pred
    chi2 = np.sum((residuals / err) ** 2)
    n = len(tau)
    rmse = math.sqrt(np.mean(residuals ** 2))
    aic = chi2 + 2 * k
    aicc = aic + (2 * k * (k + 1)) / max(1, n - k - 1)
    perr = np.sqrt(np.diag(pcov))
    return {
        "name": name,
        "k": k,
        "popt": popt,
        "perr": perr,
        "chi2": chi2,
        "rmse": rmse,
        "aic": aic,
        "aicc": aicc,
    }

def main():
    tau, q, err = load_data()

    runs = [
        fit_family(f1, [PI_SQ], tau, q, err, "F1_Proesmans_1/tau", 1),
        fit_family(f2, [PI_SQ, 0.0], tau, q, err, "F2_VanVu-Saito_1/tau+1/tau^2", 2),
        fit_family(f3, [KB_T_LN2, PI_SQ, 1.0], tau, q, err, "F3_free_power_law", 3),
        fit_family(f4, [KB_T_LN2, 2.5, 5.0], tau, q, err, "F4_activated_process", 3),
    ]

    # Write tournament results
    with open(TOURN_PATH, "w") as f:
        f.write("family,k,chi2,rmse,aic,aicc,popt,perr\n")
        for r in runs:
            f.write(f"{r['name']},{r['k']},{r['chi2']:.4f},{r['rmse']:.4f},{r['aic']:.4f},{r['aicc']:.4f},\"{list(np.round(r['popt'], 4))}\",\"{list(np.round(r['perr'], 4))}\"\n")

    # Rank by AICc
    runs_sorted = sorted(runs, key=lambda r: r["aicc"])
    winner = runs_sorted[0]
    print("Tournament ranking (by AICc, lower = better):")
    for i, r in enumerate(runs_sorted):
        delta = r["aicc"] - winner["aicc"]
        print(f"  {i+1}. {r['name']:<35}  AICc={r['aicc']:7.3f}  ΔAICc={delta:+6.3f}  chi2={r['chi2']:6.3f}  rmse={r['rmse']:.4f}")
    print(f"\nWinner: {winner['name']}")
    print(f"  popt = {winner['popt']}")
    print(f"  perr = {winner['perr']}")

    # Append the four tournament rows to results.tsv
    append_rows = []
    for r in runs:
        for i, (v, e) in enumerate(zip(r["popt"], r["perr"])):
            exp_id = f"T{runs.index(r)+1:02d}_{i}"
            append_rows.append("\t".join([
                exp_id,
                "1",
                f"Phase 1 tournament: {r['name']} parameter #{i}",
                r["name"],
                "42",
                f"param_{i}",
                f"{v:.6f}",
                f"{v - 1.96*e:.6f}",
                f"{v + 1.96*e:.6f}",
                "KEEP" if r is winner else "TOURN",
                f"AICc={r['aicc']:.3f}, chi2={r['chi2']:.3f}, rmse={r['rmse']:.4f}",
            ]))

    with open(RESULTS_PATH, "a") as f:
        for line in append_rows:
            f.write(line + "\n")
    print(f"\nAppended {len(append_rows)} rows to results.tsv")

if __name__ == "__main__":
    main()
