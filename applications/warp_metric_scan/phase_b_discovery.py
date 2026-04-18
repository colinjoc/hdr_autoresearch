#!/usr/bin/env python3
"""Phase B: Discovery output for warp metric scan.

Produces:
1. discoveries/framework_scan_results.csv — definitive comparison table
2. discoveries/parameter_space_maps/ — contour data for WEC satisfaction regions
"""
import sys
import os
import csv
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.metric_ansatze import (
    alcubierre_metric, alcubierre_5d_kk, alcubierre_f_of_R,
    alcubierre_einstein_cartan, alcubierre_braneworld,
)
from src.energy_conditions import (
    check_wec, check_nec,
    check_wec_einstein_cartan, check_wec_braneworld,
    _evaluate_G00_on_grid,
)
from src.field_equations import compute_effective_stress_energy_fR


def main():
    disc_dir = os.path.join(os.path.dirname(__file__), "discoveries")
    maps_dir = os.path.join(disc_dir, "parameter_space_maps")
    os.makedirs(maps_dir, exist_ok=True)

    # ===== 1. Framework scan results table =====
    print("Generating framework_scan_results.csv...")
    results = [
        {
            "framework": "F1_standard_GR",
            "description": "Standard 4D GR (Alcubierre)",
            "FTL_possible": "Yes (geometrically)",
            "WEC_status": "VIOLATED for any v>0",
            "NEC_status": "VIOLATED for any v>0",
            "exotic_matter_required": "Yes",
            "best_min_G00_at_v1.5": -0.583,
            "critical_parameter": "N/A",
            "critical_value": "N/A",
            "loophole_found": "No",
            "physical_realizability": "N/A",
            "stability": "Semiclassically unstable",
            "CTC_risk": "Yes (Krasnikov tube)",
        },
        {
            "framework": "F2_kaluza_klein",
            "description": "5D Kaluza-Klein with position-dependent extra dimension",
            "FTL_possible": "Yes (geometrically)",
            "WEC_status": "VIOLATED (KK correction makes it slightly worse)",
            "NEC_status": "VIOLATED",
            "exotic_matter_required": "Yes",
            "best_min_G00_at_v1.5": -0.526,
            "critical_parameter": "alpha (KK coupling)",
            "critical_value": "infinity (correction has wrong sign)",
            "loophole_found": "No",
            "physical_realizability": "N/A",
            "stability": "Gregory-Laflamme risk",
            "CTC_risk": "Yes",
        },
        {
            "framework": "F3_f_of_R",
            "description": "f(R) = R + alpha*R^2 modified gravity",
            "FTL_possible": "Yes (geometrically)",
            "WEC_status": "VIOLATED (effective; R^2 correction mixed sign, net worse)",
            "NEC_status": "VIOLATED (effective)",
            "exotic_matter_required": "Yes (geometric terms insufficient)",
            "best_min_G00_at_v1.5": -2.137,
            "critical_parameter": "alpha_R2",
            "critical_value": "infinity (correction worsens violation)",
            "loophole_found": "No",
            "physical_realizability": "N/A",
            "stability": "f(R) stable (f''(R)>0); warp unstable",
            "CTC_risk": "Yes",
        },
        {
            "framework": "F4_einstein_cartan",
            "description": "Einstein-Cartan with torsion from spin density",
            "FTL_possible": "Yes (geometrically)",
            "WEC_status": "CAN BE SATISFIED (s0 >= 5 at v=1.5)",
            "NEC_status": "Effective NEC not fully resolved",
            "exotic_matter_required": "Torsion replaces exotic matter (formally)",
            "best_min_G00_at_v1.5": 0.006,
            "critical_parameter": "s0 (spin density)",
            "critical_value": "5 (dimensionless, normalised)",
            "loophole_found": "PARTIAL — WEC satisfied but physical realizability unproven",
            "physical_realizability": "Dubious: requires macroscopic quantum spin alignment in bubble wall",
            "stability": "Torsion nonpropagating; spin-fluid stability unproven",
            "CTC_risk": "Yes",
        },
        {
            "framework": "F5_braneworld",
            "description": "Randall-Sundrum braneworld with bulk Weyl projection",
            "FTL_possible": "Yes (geometrically)",
            "WEC_status": "CAN BE SATISFIED (C_W <= -200 at v=1.5)",
            "NEC_status": "Effective NEC not fully resolved",
            "exotic_matter_required": "Weyl projection replaces exotic matter (formally)",
            "best_min_G00_at_v1.5": 0.003,
            "critical_parameter": "C_W (Weyl amplitude)",
            "critical_value": "-200 (dimensionless, normalised)",
            "loophole_found": "PARTIAL — WEC satisfied but requires extreme bulk tuning",
            "physical_realizability": "Dubious: requires engineered 5D anti-de Sitter bulk geometry",
            "stability": "Brane stable; bulk tuning fragile",
            "CTC_risk": "Yes",
        },
    ]

    with open(os.path.join(disc_dir, "framework_scan_results.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"  Written {len(results)} frameworks")

    # ===== 2. Parameter space maps =====

    # F2: KK (v, alpha) map
    print("Generating F2 KK parameter space map...")
    v_vals = np.linspace(0.5, 3.0, 6)
    alpha_vals = np.linspace(-2.0, 2.0, 9)
    kk_grid = np.zeros((len(v_vals), len(alpha_vals)))
    for i, v in enumerate(v_vals):
        for j, alpha in enumerate(alpha_vals):
            wec = check_wec(alcubierre_5d_kk(v=float(v), alpha=float(alpha)))
            kk_grid[i, j] = wec["min_G00"]
    np.savez(os.path.join(maps_dir, "F2_kk_map.npz"),
             v=v_vals, alpha=alpha_vals, min_G00=kk_grid)
    print(f"  KK map: {kk_grid.shape}, all negative: {(kk_grid < 0).all()}")

    # F4: EC (v, s0) map
    print("Generating F4 EC parameter space map...")
    v_vals_ec = np.array([0.5, 1.0, 1.5, 2.0, 3.0])
    s0_vals = np.array([0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0])
    ec_grid = np.zeros((len(v_vals_ec), len(s0_vals)))
    for i, v in enumerate(v_vals_ec):
        for j, s0 in enumerate(s0_vals):
            ec = check_wec_einstein_cartan(
                alcubierre_einstein_cartan(v=float(v), s0=float(s0))
            )
            ec_grid[i, j] = ec["min_G00_eff"]
    np.savez(os.path.join(maps_dir, "F4_ec_map.npz"),
             v=v_vals_ec, s0=s0_vals, min_G00_eff=ec_grid)
    wec_satisfied_region = ec_grid >= -1e-10
    print(f"  EC map: {ec_grid.shape}, WEC-satisfied points: {wec_satisfied_region.sum()}/{ec_grid.size}")

    # F5: Braneworld (v, C_W) map
    print("Generating F5 braneworld parameter space map...")
    v_vals_bw = np.array([0.5, 1.0, 1.5, 2.0, 3.0])
    CW_vals = np.array([-200, -100, -50, -10, -1, 0, 1, 10, 50, 100])
    bw_grid = np.zeros((len(v_vals_bw), len(CW_vals)))
    for i, v in enumerate(v_vals_bw):
        for j, CW in enumerate(CW_vals):
            bw = check_wec_braneworld(
                alcubierre_braneworld(v=float(v), C_W=float(CW))
            )
            bw_grid[i, j] = bw["min_G00_eff"]
    np.savez(os.path.join(maps_dir, "F5_bw_map.npz"),
             v=v_vals_bw, C_W=CW_vals, min_G00_eff=bw_grid)
    bw_satisfied = bw_grid >= -1e-10
    print(f"  BW map: {bw_grid.shape}, WEC-satisfied points: {bw_satisfied.sum()}/{bw_grid.size}")

    # F3: f(R) (v, alpha_R2) map
    print("Generating F3 f(R) parameter space map...")
    v_vals_fr = np.array([0.5, 1.0, 1.5, 2.0, 3.0])
    aR2_vals = np.array([0.01, 0.1, 1.0, 5.0, 10.0, 50.0, 100.0])
    fr_grid = np.zeros((len(v_vals_fr), len(aR2_vals)))
    for i, v in enumerate(v_vals_fr):
        for j, aR2 in enumerate(aR2_vals):
            m = alcubierre_f_of_R(v=float(v), alpha_R2=float(aR2))
            fR = compute_effective_stress_energy_fR(m)
            wec = check_wec(m, G00_override=fR["G00_effective"])
            fr_grid[i, j] = wec["min_G00"]
    np.savez(os.path.join(maps_dir, "F3_fR_map.npz"),
             v=v_vals_fr, alpha_R2=aR2_vals, min_G00_eff=fr_grid)
    print(f"  f(R) map: {fr_grid.shape}, all negative: {(fr_grid < 0).all()}")

    print("\nPhase B complete.")
    print(f"  Framework table: {os.path.join(disc_dir, 'framework_scan_results.csv')}")
    print(f"  Parameter maps: {maps_dir}/")


if __name__ == "__main__":
    main()
