#!/usr/bin/env python3
"""Phase 2 (105 hypotheses) + Phase 2.5 (compositions) + Phase B (discovery sweep).

Runs all pre-registered single-change experiments from research_queue.md,
applies KEEP/REVERT logic, then compositions and the penetration sweep.
"""

from __future__ import annotations
import csv
import sys
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from sim_ring_road import RingRoadConfig, simulate
from controllers import (
    IDMController, FollowerStopper, PIWithSaturation,
    ACCController, ConstantVelocityController,
)
from measurements import (
    compute_wave_characteristics, compute_mean_velocity_variance,
    compute_throughput, compute_fuel_proxy,
)
from evaluate import compute_metrics, run_experiment, RESULTS_FILE, TSV_HEADER

# -----------------------------------------------------------------------
# Helper: run and record
# -----------------------------------------------------------------------

def run_and_record(exp_id, description, controller_name="IDM", n_smart=0,
                   n_vehicles=22, ring_length=230.0, t_max=600.0, seed=42,
                   smart_controller_factory=None, smart_indices=None,
                   notes="", **cfg_overrides):
    """Run experiment and return row dict."""
    row = run_experiment(
        exp_id=exp_id,
        description=description,
        controller_name=controller_name,
        n_smart=n_smart,
        n_vehicles=n_vehicles,
        ring_length=ring_length,
        t_max=t_max,
        seed=seed,
        smart_controller_factory=smart_controller_factory,
        smart_indices=smart_indices,
        notes=notes,
        **cfg_overrides,
    )
    return row


# -----------------------------------------------------------------------
# Phase 2: 105 hypotheses
# -----------------------------------------------------------------------

def run_phase2():
    """Run all 105 hypotheses. Returns list of row dicts and keep/revert info."""

    NOISE_FLOOR = 0.40  # 2-sigma on wave_amp
    best_wave_amp = 0.55  # T08 ACC at 18.2%

    results = []
    keeps = []
    reverts = []
    defers = []

    def evaluate_hypothesis(exp_id, desc, wave_amp, row):
        nonlocal best_wave_amp
        threshold = best_wave_amp - NOISE_FLOOR
        if wave_amp < threshold:
            decision = "KEEP"
            best_wave_amp = wave_amp
            keeps.append((exp_id, wave_amp, desc))
        else:
            decision = "REVERT"
            reverts.append((exp_id, wave_amp, desc))
        row["notes"] = f"{row.get('notes', '')} | {decision} (best={best_wave_amp:.2f})"
        return decision

    # -------------------------------------------------------------------
    # Theme 1: FS Penetration Sweep (H001-H008)
    # -------------------------------------------------------------------
    for h_id, n_smart in [("H001",1),("H002",2),("H003",3),("H004",4),
                           ("H005",6),("H006",8),("H007",11),("H008",22)]:
        desc = f"FS {n_smart}/{22} ({n_smart/22*100:.1f}%)"
        row = run_and_record(h_id, desc, "FollowerStopper", n_smart,
                             smart_controller_factory=lambda: FollowerStopper())
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 2: Controller Family Comparison (H009-H016) - repeats of T01-T10
    # -------------------------------------------------------------------
    # H009: IDM "smart" at 4.5%
    row = run_and_record("H009", "IDM smart 1/22 (control)", "IDM", 1,
                         smart_controller_factory=lambda: IDMController(v0=30.0, T=1.0, a=1.3, b=2.0, s0=2.0))
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H009", row["description"], wa, row)
    results.append(row); print(f"  H009: wave_amp={wa:.2f}")

    # H010: IDM "smart" at 18.2%
    row = run_and_record("H010", "IDM smart 4/22 (control)", "IDM", 4,
                         smart_controller_factory=lambda: IDMController(v0=30.0, T=1.0, a=1.3, b=2.0, s0=2.0))
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H010", row["description"], wa, row)
    results.append(row); print(f"  H010: wave_amp={wa:.2f}")

    # H011: PI at 4.5%
    row = run_and_record("H011", "PI 1/22 (4.5%)", "PIWithSaturation", 1,
                         smart_controller_factory=lambda: PIWithSaturation())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H011", row["description"], wa, row)
    results.append(row); print(f"  H011: wave_amp={wa:.2f}")

    # H012: PI at 18.2%
    row = run_and_record("H012", "PI 4/22 (18.2%)", "PIWithSaturation", 4,
                         smart_controller_factory=lambda: PIWithSaturation())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H012", row["description"], wa, row)
    results.append(row); print(f"  H012: wave_amp={wa:.2f}")

    # H013: ACC at 4.5%
    row = run_and_record("H013", "ACC 1/22 (4.5%)", "ACC", 1,
                         smart_controller_factory=lambda: ACCController())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H013", row["description"], wa, row)
    results.append(row); print(f"  H013: wave_amp={wa:.2f}")

    # H014: ACC at 18.2%
    row = run_and_record("H014", "ACC 4/22 (18.2%)", "ACC", 4,
                         smart_controller_factory=lambda: ACCController())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H014", row["description"], wa, row)
    results.append(row); print(f"  H014: wave_amp={wa:.2f}")

    # H015: CV at 4.5%
    row = run_and_record("H015", "ConstVel 1/22 (4.5%)", "ConstantVelocity", 1,
                         smart_controller_factory=lambda: ConstantVelocityController())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H015", row["description"], wa, row)
    results.append(row); print(f"  H015: wave_amp={wa:.2f}")

    # H016: CV at 18.2%
    row = run_and_record("H016", "ConstVel 4/22 (18.2%)", "ConstantVelocity", 4,
                         smart_controller_factory=lambda: ConstantVelocityController())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H016", row["description"], wa, row)
    results.append(row); print(f"  H016: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 3: FS Gain Tuning (H017-H026) at 4/22
    # -------------------------------------------------------------------
    fs_tuning = [
        ("H017", "FS v_des=8 4/22", dict(v_des=8.0)),
        ("H018", "FS v_des=5 4/22", dict(v_des=5.0)),
        ("H019", "FS v_des=25 4/22", dict(v_des=25.0)),
        ("H020", "FS s_st=2 4/22", dict(s_st=2.0)),
        ("H021", "FS s_st=8 4/22", dict(s_st=8.0)),
        ("H022", "FS s_go=20 4/22", dict(s_go=20.0)),
        ("H023", "FS s_go=50 4/22", dict(s_go=50.0)),
        ("H024", "FS k_v=0.2 4/22", dict(k_v=0.2)),
        ("H025", "FS k_v=1.0 4/22", dict(k_v=1.0)),
        ("H026", "FS k_v=2.0 4/22", dict(k_v=2.0)),
    ]
    for h_id, desc, params in fs_tuning:
        factory = lambda p=params: FollowerStopper(**p)
        row = run_and_record(h_id, desc, "FollowerStopper", 4,
                             smart_controller_factory=factory)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 4: PI Gain Tuning (H027-H033) at 4/22
    # -------------------------------------------------------------------
    pi_tuning = [
        ("H027", "PI k_p=0.1 4/22", dict(k_p=0.1)),
        ("H028", "PI k_p=0.8 4/22", dict(k_p=0.8)),
        ("H029", "PI k_i=0.005 4/22", dict(k_i=0.005)),
        ("H030", "PI k_i=0 4/22", dict(k_i=0.0)),
        ("H031", "PI k_i=0.05 4/22", dict(k_i=0.05)),
        ("H032", "PI T_des=0.8 4/22", dict(T_des=0.8)),
        ("H033", "PI T_des=2.5 4/22", dict(T_des=2.5)),
    ]
    for h_id, desc, params in pi_tuning:
        factory = lambda p=params: PIWithSaturation(**p)
        row = run_and_record(h_id, desc, "PIWithSaturation", 4,
                             smart_controller_factory=factory)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 5: ACC Time Headway Sweep (H034-H038) at 4/22
    # -------------------------------------------------------------------
    acc_thw = [
        ("H034", "ACC T_des=0.8 4/22", dict(T_des=0.8)),
        ("H035", "ACC T_des=1.0 4/22", dict(T_des=1.0)),
        ("H036", "ACC T_des=1.4 4/22", dict(T_des=1.4)),
        ("H037", "ACC T_des=2.5 4/22", dict(T_des=2.5)),
        ("H038", "ACC T_des=3.0 4/22", dict(T_des=3.0)),
    ]
    for h_id, desc, params in acc_thw:
        factory = lambda p=params: ACCController(**p)
        row = run_and_record(h_id, desc, "ACC", 4,
                             smart_controller_factory=factory)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 6: Ring Size (H039-H044) — baseline changes
    # -------------------------------------------------------------------
    # H039: 40/400 ring, 4 FS (10%)
    row = run_and_record("H039", "40veh/400m 4FS (10%)", "FollowerStopper", 4,
                         n_vehicles=40, ring_length=400.0,
                         smart_controller_factory=lambda: FollowerStopper())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H039", row["description"], wa, row)
    results.append(row); print(f"  H039: wave_amp={wa:.2f}")

    # H040: 40/400 ring, 8 FS (20%)
    row = run_and_record("H040", "40veh/400m 8FS (20%)", "FollowerStopper", 8,
                         n_vehicles=40, ring_length=400.0,
                         smart_controller_factory=lambda: FollowerStopper())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H040", row["description"], wa, row)
    results.append(row); print(f"  H040: wave_amp={wa:.2f}")

    # H041: 100/2000 ring, baseline (0 smart)
    row = run_and_record("H041", "100veh/2000m baseline", "IDM", 0,
                         n_vehicles=100, ring_length=2000.0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H041", row["description"], wa, row)
    results.append(row); print(f"  H041: wave_amp={wa:.2f}")

    # H042: 100/1000 ring, baseline
    row = run_and_record("H042", "100veh/1000m baseline", "IDM", 0,
                         n_vehicles=100, ring_length=1000.0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H042", row["description"], wa, row)
    results.append(row); print(f"  H042: wave_amp={wa:.2f}")

    # H043: 100/1000, 5 FS (5%)
    row = run_and_record("H043", "100veh/1000m 5FS (5%)", "FollowerStopper", 5,
                         n_vehicles=100, ring_length=1000.0,
                         smart_controller_factory=lambda: FollowerStopper())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H043", row["description"], wa, row)
    results.append(row); print(f"  H043: wave_amp={wa:.2f}")

    # H044: 200/4000, 10 FS (5%)
    row = run_and_record("H044", "200veh/4000m 10FS (5%)", "FollowerStopper", 10,
                         n_vehicles=200, ring_length=4000.0,
                         smart_controller_factory=lambda: FollowerStopper())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H044", row["description"], wa, row)
    results.append(row); print(f"  H044: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 7: Human Driver Model (H045-H054) — IDM param changes, all-IDM
    # -------------------------------------------------------------------
    idm_perturbations = [
        ("H045", "IDM T=0.7 baseline", dict(idm_T=0.7)),
        ("H046", "IDM T=1.2 baseline", dict(idm_T=1.2)),
        ("H047", "IDM T=1.5 baseline", dict(idm_T=1.5)),
        ("H048", "IDM T=2.0 baseline", dict(idm_T=2.0)),
        ("H049", "IDM a=0.73 baseline", dict(idm_a=0.73)),
        ("H050", "IDM a=2.0 baseline", dict(idm_a=2.0)),
        ("H051", "IDM b=1.0 baseline", dict(idm_b=1.0)),
        ("H052", "IDM b=3.0 baseline", dict(idm_b=3.0)),
        ("H053", "IDM s0=1.0 baseline", dict(idm_s0=1.0)),
        ("H054", "IDM s0=4.0 baseline", dict(idm_s0=4.0)),
    ]
    for h_id, desc, overrides in idm_perturbations:
        row = run_and_record(h_id, desc, "IDM", 0, **overrides)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 8: Noise Level (H055-H061)
    # -------------------------------------------------------------------
    # H055-H059: all-IDM with varying noise
    noise_experiments = [
        ("H055", "noise=0.0 baseline", 0, None, dict(noise_std=0.0)),
        ("H056", "noise=0.1 baseline", 0, None, dict(noise_std=0.1)),
        ("H057", "noise=0.5 baseline", 0, None, dict(noise_std=0.5)),
        ("H058", "noise=0.8 baseline", 0, None, dict(noise_std=0.8)),
        ("H059", "noise=1.0 baseline", 0, None, dict(noise_std=1.0)),
    ]
    for h_id, desc, n_smart, factory, overrides in noise_experiments:
        row = run_and_record(h_id, desc, "IDM", n_smart,
                             smart_controller_factory=factory, **overrides)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # H060: noise=0.5 + 4 FS
    row = run_and_record("H060", "noise=0.5 FS 4/22", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(),
                         noise_std=0.5)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H060", row["description"], wa, row)
    results.append(row); print(f"  H060: wave_amp={wa:.2f}")

    # H061: noise=0.8 + 4 FS
    row = run_and_record("H061", "noise=0.8 FS 4/22", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(),
                         noise_std=0.8)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H061", row["description"], wa, row)
    results.append(row); print(f"  H061: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 9: Initial Perturbation (H062-H065)
    # -------------------------------------------------------------------
    perturb_experiments = [
        ("H062", "no perturbation", dict(perturb_decel=0.0)),
        ("H063", "strong perturb -9", dict(perturb_decel=-9.0)),
        ("H064", "weak perturb -1", dict(perturb_decel=-1.0)),
        ("H065", "late perturb t=50", dict(perturb_time=50.0)),
    ]
    for h_id, desc, overrides in perturb_experiments:
        row = run_and_record(h_id, desc, "IDM", 0, **overrides)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 10: Placement (H066-H070) at 4 FS
    # -------------------------------------------------------------------
    # H066: clustered [0,1,2,3]
    row = run_and_record("H066", "FS 4/22 clustered [0-3]", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(),
                         smart_indices=[0,1,2,3])
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H066", row["description"], wa, row)
    results.append(row); print(f"  H066: wave_amp={wa:.2f}")

    # H067: paired [0,1,11,12]
    row = run_and_record("H067", "FS 4/22 paired [0,1,11,12]", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(),
                         smart_indices=[0,1,11,12])
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H067", row["description"], wa, row)
    results.append(row); print(f"  H067: wave_amp={wa:.2f}")

    # H068-H070: random placement
    for h_id, rseed in [("H068",0),("H069",1),("H070",2)]:
        rng = np.random.RandomState(rseed)
        indices = sorted(rng.choice(22, 4, replace=False).tolist())
        desc = f"FS 4/22 random seed={rseed} {indices}"
        row = run_and_record(h_id, desc, "FollowerStopper", 4,
                             smart_controller_factory=lambda: FollowerStopper(),
                             smart_indices=indices)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 11: Heterogeneous v0 (H071-H073)
    # H071-H072 need per-vehicle heterogeneous v0. Since our sim uses a
    # single idm_v0 for all humans, we'll approximate by creating a custom
    # simulation. For simplicity we'll use the midpoint approach:
    # vary idm_v0 around 30 but use config-level noise to approximate.
    # Actually, heterogeneous v0 requires modifying the sim. DEFER these
    # or implement a workaround.
    # -------------------------------------------------------------------
    # We can implement heterogeneous v0 by running a custom simulate call
    # with per-vehicle controllers. Let's do it properly.

    def run_hetero_v0(exp_id, desc, v0_low, v0_high, n_smart_fs=0, seed=42):
        """Run with heterogeneous desired speeds."""
        cfg = RingRoadConfig(n_vehicles=22, ring_length=230.0, t_max=600.0, seed=seed)
        rng_v0 = np.random.RandomState(seed + 1000)

        # Determine smart indices
        if n_smart_fs > 0:
            spacing = 22 / n_smart_fs
            smart_set = set(int(round(i * spacing)) % 22 for i in range(n_smart_fs))
        else:
            smart_set = set()

        # Build custom controllers list (we need to modify sim to accept per-vehicle controllers)
        # Actually, we can use the simulate function directly with a custom approach:
        # Create a factory that returns FS for smart, and custom IDM for humans
        # But the sim assigns one factory for all smart vehicles and uses config IDM for humans.
        # We need to work around this. Let's simulate directly.

        from sim_ring_road import _VehicleState, _gap
        rng = np.random.RandomState(cfg.seed)
        n_veh = cfg.n_vehicles
        ring_len = cfg.ring_length
        sp = ring_len / n_veh
        base_v = min(sp - cfg.veh_length, 10.0)

        vehicles = []
        for i in range(n_veh):
            pos = i * sp
            vel = max(0.0, base_v + rng.uniform(-0.5, 0.5))
            if i in smart_set:
                ctrl = FollowerStopper()
                is_smart = True
            else:
                v0_i = rng_v0.uniform(v0_low, v0_high)
                ctrl = IDMController(v0=v0_i, T=cfg.idm_T, a=cfg.idm_a,
                                      b=cfg.idm_b, delta=cfg.idm_delta, s0=cfg.idm_s0)
                is_smart = False
            vehicles.append(_VehicleState(position=pos, velocity=vel, controller=ctrl,
                                          is_smart=is_smart, vehicle_id=i))

        n_steps = int(cfg.t_max / cfg.dt) + 1
        total_rows = n_steps * n_veh
        times = np.empty(total_rows, dtype=np.float64)
        veh_ids = np.empty(total_rows, dtype=np.int32)
        positions = np.empty(total_rows, dtype=np.float64)
        velocities = np.empty(total_rows, dtype=np.float64)
        accelerations = np.empty(total_rows, dtype=np.float64)
        gaps_arr = np.empty(total_rows, dtype=np.float64)
        is_smart_arr = np.empty(total_rows, dtype=np.bool_)

        row_idx = 0
        for step in range(n_steps):
            t = step * cfg.dt
            accels = np.empty(n_veh)
            gap_a = np.empty(n_veh)
            for i in range(n_veh):
                leader = (i + 1) % n_veh
                g = _gap(vehicles[i].position, vehicles[leader].position, ring_len, cfg.veh_length)
                gap_a[i] = g
                acc = vehicles[i].controller(own_v=vehicles[i].velocity,
                                              lead_v=vehicles[leader].velocity,
                                              gap=g, dt=cfg.dt)
                accels[i] = acc

            if cfg.noise_std > 0:
                for i in range(n_veh):
                    if not vehicles[i].is_smart:
                        noise = rng.normal(0.0, cfg.noise_std)
                        accels[i] = float(np.clip(accels[i] + noise, -9.0, 3.0))

            if abs(t - cfg.perturb_time) < cfg.dt / 2:
                accels[cfg.perturb_vehicle] = cfg.perturb_decel

            for i in range(n_veh):
                times[row_idx] = t
                veh_ids[row_idx] = i
                positions[row_idx] = vehicles[i].position
                velocities[row_idx] = vehicles[i].velocity
                accelerations[row_idx] = accels[i]
                gaps_arr[row_idx] = gap_a[i]
                is_smart_arr[row_idx] = vehicles[i].is_smart
                row_idx += 1

            for i in range(n_veh):
                vehicles[i].velocity = max(0.0, vehicles[i].velocity + accels[i] * cfg.dt)
                vehicles[i].position = (vehicles[i].position + vehicles[i].velocity * cfg.dt) % ring_len

        df = pd.DataFrame({
            "time": times[:row_idx], "vehicle_id": veh_ids[:row_idx],
            "position": positions[:row_idx], "velocity": velocities[:row_idx],
            "acceleration": accelerations[:row_idx], "gap": gaps_arr[:row_idx],
            "is_smart": is_smart_arr[:row_idx],
        })
        metrics = compute_metrics(df, ring_length=ring_len)
        penetration = n_smart_fs / n_veh
        return {
            "exp_id": exp_id, "description": desc, "controller": "FollowerStopper" if n_smart_fs > 0 else "IDM",
            "n_smart": n_smart_fs, "penetration": f"{penetration:.3f}",
            **metrics, "notes": f"hetero v0 U({v0_low},{v0_high})",
        }

    # H071
    row = run_hetero_v0("H071", "hetero v0 U(25,35) baseline", 25, 35, 0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H071", row["description"], wa, row)
    results.append(row); print(f"  H071: wave_amp={wa:.2f}")

    # H072
    row = run_hetero_v0("H072", "hetero v0 U(20,40) baseline", 20, 40, 0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H072", row["description"], wa, row)
    results.append(row); print(f"  H072: wave_amp={wa:.2f}")

    # H073
    row = run_hetero_v0("H073", "hetero v0 U(25,35) + 4 FS", 25, 35, 4)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H073", row["description"], wa, row)
    results.append(row); print(f"  H073: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 12: Multi-Objective (H074-H077) — same configs, different primary
    # -------------------------------------------------------------------
    # H074: FS at 18.2% (reanalysis for fuel) — same as T04
    row = run_and_record("H074", "FS 4/22 fuel-focus", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(),
                         notes="primary=fuel")
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H074", row["description"], wa, row)
    results.append(row); print(f"  H074: wave_amp={wa:.2f} fuel={row['fuel_ml_km']}")

    # H075: ACC at 18.2% (throughput focus) — same as T08
    row = run_and_record("H075", "ACC 4/22 throughput-focus", "ACC", 4,
                         smart_controller_factory=lambda: ACCController(),
                         notes="primary=throughput")
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H075", row["description"], wa, row)
    results.append(row); print(f"  H075: wave_amp={wa:.2f} throughput={row['throughput_vph']}")

    # H076: FS k_v=0.3, 4/22
    row = run_and_record("H076", "FS k_v=0.3 4/22 fuel-opt", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(k_v=0.3),
                         notes="primary=fuel")
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H076", row["description"], wa, row)
    results.append(row); print(f"  H076: wave_amp={wa:.2f} fuel={row['fuel_ml_km']}")

    # H077: 6 FS (27.3%)
    row = run_and_record("H077", "FS 6/22 fuel-vs-wave", "FollowerStopper", 6,
                         smart_controller_factory=lambda: FollowerStopper())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H077", row["description"], wa, row)
    results.append(row); print(f"  H077: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 13: Run Length (H078-H080)
    # -------------------------------------------------------------------
    row = run_and_record("H078", "t_max=300 baseline", "IDM", 0, t_max=300.0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H078", row["description"], wa, row)
    results.append(row); print(f"  H078: wave_amp={wa:.2f}")

    row = run_and_record("H079", "t_max=1200 baseline", "IDM", 0, t_max=1200.0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H079", row["description"], wa, row)
    results.append(row); print(f"  H079: wave_amp={wa:.2f}")

    row = run_and_record("H080", "t_max=300 FS 4/22", "FollowerStopper", 4,
                         t_max=300.0,
                         smart_controller_factory=lambda: FollowerStopper())
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H080", row["description"], wa, row)
    results.append(row); print(f"  H080: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 14: dt Sensitivity (H081-H083)
    # -------------------------------------------------------------------
    row = run_and_record("H081", "dt=0.05 baseline", "IDM", 0, dt=0.05)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H081", row["description"], wa, row)
    results.append(row); print(f"  H081: wave_amp={wa:.2f}")

    row = run_and_record("H082", "dt=0.2 baseline", "IDM", 0, dt=0.2)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H082", row["description"], wa, row)
    results.append(row); print(f"  H082: wave_amp={wa:.2f}")

    row = run_and_record("H083", "dt=0.05 FS 4/22", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(),
                         dt=0.05)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H083", row["description"], wa, row)
    results.append(row); print(f"  H083: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 15: Cross-Controller Penetrations (H084-H087)
    # -------------------------------------------------------------------
    cross_pen = [
        ("H084", "ACC 2/22 (9.1%)", "ACC", 2, lambda: ACCController()),
        ("H085", "ACC 6/22 (27.3%)", "ACC", 6, lambda: ACCController()),
        ("H086", "FS 2/22 (9.1%)", "FollowerStopper", 2, lambda: FollowerStopper()),
        ("H087", "ACC 11/22 (50%)", "ACC", 11, lambda: ACCController()),
    ]
    for h_id, desc, ctrl, ns, factory in cross_pen:
        row = run_and_record(h_id, desc, ctrl, ns, smart_controller_factory=factory)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 16: ACC Gain Tuning (H088-H091)
    # -------------------------------------------------------------------
    acc_gains = [
        ("H088", "ACC k1=0.1 4/22", dict(k1=0.1)),
        ("H089", "ACC k1=0.6 4/22", dict(k1=0.6)),
        ("H090", "ACC k2=0.2 4/22", dict(k2=0.2)),
        ("H091", "ACC k2=1.0 4/22", dict(k2=1.0)),
    ]
    for h_id, desc, params in acc_gains:
        factory = lambda p=params: ACCController(**p)
        row = run_and_record(h_id, desc, "ACC", 4, smart_controller_factory=factory)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 17: FS Tuning at Low Penetration (H092-H095)
    # -------------------------------------------------------------------
    # H092: FS v_des=8, 1 vehicle
    row = run_and_record("H092", "FS v_des=8 1/22", "FollowerStopper", 1,
                         smart_controller_factory=lambda: FollowerStopper(v_des=8.0))
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H092", row["description"], wa, row)
    results.append(row); print(f"  H092: wave_amp={wa:.2f}")

    # H093: FS s_st=2, s_go=15, 1 vehicle
    row = run_and_record("H093", "FS s_st=2 s_go=15 1/22", "FollowerStopper", 1,
                         smart_controller_factory=lambda: FollowerStopper(s_st=2.0, s_go=15.0))
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H093", row["description"], wa, row)
    results.append(row); print(f"  H093: wave_amp={wa:.2f}")

    # H094: FS ring-tuned: v_des=6, s_st=2, s_go=12, k_v=0.8, 1 vehicle
    row = run_and_record("H094", "FS ring-tuned 1/22", "FollowerStopper", 1,
                         smart_controller_factory=lambda: FollowerStopper(
                             v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8))
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H094", row["description"], wa, row)
    results.append(row); print(f"  H094: wave_amp={wa:.2f}")

    # H095: FS ring-tuned, 4 vehicles
    row = run_and_record("H095", "FS ring-tuned 4/22", "FollowerStopper", 4,
                         smart_controller_factory=lambda: FollowerStopper(
                             v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8))
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H095", row["description"], wa, row)
    results.append(row); print(f"  H095: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 18: Noise x Controller (H096-H098)
    # -------------------------------------------------------------------
    # H096: noise=0, 1 FS
    row = run_and_record("H096", "noise=0 FS 1/22", "FollowerStopper", 1,
                         smart_controller_factory=lambda: FollowerStopper(),
                         noise_std=0.0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H096", row["description"], wa, row)
    results.append(row); print(f"  H096: wave_amp={wa:.2f}")

    # H097: noise=0, no perturbation
    row = run_and_record("H097", "noise=0 no-perturb", "IDM", 0,
                         noise_std=0.0, perturb_decel=0.0)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H097", row["description"], wa, row)
    results.append(row); print(f"  H097: wave_amp={wa:.2f}")

    # H098: noise=0.5, 4 ACC
    row = run_and_record("H098", "noise=0.5 ACC 4/22", "ACC", 4,
                         smart_controller_factory=lambda: ACCController(),
                         noise_std=0.5)
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H098", row["description"], wa, row)
    results.append(row); print(f"  H098: wave_amp={wa:.2f}")

    # -------------------------------------------------------------------
    # Theme 19: Density Variation (H099-H103)
    # -------------------------------------------------------------------
    density_exps = [
        ("H099", "18veh/230m baseline", 18, 230.0, 0, None),
        ("H100", "20veh/230m baseline", 20, 230.0, 0, None),
        ("H101", "25veh/230m baseline", 25, 230.0, 0, None),
        ("H102", "30veh/230m baseline", 30, 230.0, 0, None),
        ("H103", "25veh/230m 5FS (20%)", 25, 230.0, 5, lambda: FollowerStopper()),
    ]
    for h_id, desc, nv, rl, ns, factory in density_exps:
        ctrl_name = "FollowerStopper" if ns > 0 else "IDM"
        row = run_and_record(h_id, desc, ctrl_name, ns, n_vehicles=nv,
                             ring_length=rl, smart_controller_factory=factory)
        wa = float(row["wave_amp_ms"])
        dec = evaluate_hypothesis(h_id, desc, wa, row)
        results.append(row)
        print(f"  {h_id}: {desc} -> wave_amp={wa:.2f} [{dec}]")

    # -------------------------------------------------------------------
    # Theme 20: Mixed Controllers (H104-H105)
    # -------------------------------------------------------------------
    # H104: 2 FS + 2 ACC at 18.2%
    # Need custom: indices [0,5] get FS, [11,16] get ACC
    def run_mixed(exp_id, desc, fs_indices, acc_indices, n_vehicles=22, ring_length=230.0):
        cfg = RingRoadConfig(n_vehicles=n_vehicles, ring_length=ring_length,
                             t_max=600.0, seed=42)
        from sim_ring_road import _VehicleState, _gap
        rng = np.random.RandomState(cfg.seed)
        n_veh = cfg.n_vehicles
        sp = ring_length / n_veh
        base_v = min(sp - cfg.veh_length, 10.0)

        fs_set = set(fs_indices)
        acc_set = set(acc_indices)
        n_smart = len(fs_indices) + len(acc_indices)

        vehicles = []
        for i in range(n_veh):
            pos = i * sp
            vel = max(0.0, base_v + rng.uniform(-0.5, 0.5))
            if i in fs_set:
                ctrl = FollowerStopper()
                is_smart = True
            elif i in acc_set:
                ctrl = ACCController()
                is_smart = True
            else:
                ctrl = IDMController(v0=cfg.idm_v0, T=cfg.idm_T, a=cfg.idm_a,
                                      b=cfg.idm_b, delta=cfg.idm_delta, s0=cfg.idm_s0)
                is_smart = False
            vehicles.append(_VehicleState(position=pos, velocity=vel, controller=ctrl,
                                          is_smart=is_smart, vehicle_id=i))

        n_steps = int(cfg.t_max / cfg.dt) + 1
        total_rows = n_steps * n_veh
        times = np.empty(total_rows, dtype=np.float64)
        veh_ids = np.empty(total_rows, dtype=np.int32)
        positions_a = np.empty(total_rows, dtype=np.float64)
        velocities_a = np.empty(total_rows, dtype=np.float64)
        accelerations_a = np.empty(total_rows, dtype=np.float64)
        gaps_a = np.empty(total_rows, dtype=np.float64)
        is_smart_a = np.empty(total_rows, dtype=np.bool_)

        row_idx = 0
        for step in range(n_steps):
            t = step * cfg.dt
            accels = np.empty(n_veh)
            gap_arr = np.empty(n_veh)
            for i in range(n_veh):
                leader = (i + 1) % n_veh
                g = _gap(vehicles[i].position, vehicles[leader].position, ring_length, cfg.veh_length)
                gap_arr[i] = g
                acc = vehicles[i].controller(own_v=vehicles[i].velocity,
                                              lead_v=vehicles[leader].velocity,
                                              gap=g, dt=cfg.dt)
                accels[i] = acc

            if cfg.noise_std > 0:
                for i in range(n_veh):
                    if not vehicles[i].is_smart:
                        noise = rng.normal(0.0, cfg.noise_std)
                        accels[i] = float(np.clip(accels[i] + noise, -9.0, 3.0))

            if abs(t - cfg.perturb_time) < cfg.dt / 2:
                accels[cfg.perturb_vehicle] = cfg.perturb_decel

            for i in range(n_veh):
                times[row_idx] = t
                veh_ids[row_idx] = i
                positions_a[row_idx] = vehicles[i].position
                velocities_a[row_idx] = vehicles[i].velocity
                accelerations_a[row_idx] = accels[i]
                gaps_a[row_idx] = gap_arr[i]
                is_smart_a[row_idx] = vehicles[i].is_smart
                row_idx += 1

            for i in range(n_veh):
                vehicles[i].velocity = max(0.0, vehicles[i].velocity + accels[i] * cfg.dt)
                vehicles[i].position = (vehicles[i].position + vehicles[i].velocity * cfg.dt) % ring_length

        df = pd.DataFrame({
            "time": times[:row_idx], "vehicle_id": veh_ids[:row_idx],
            "position": positions_a[:row_idx], "velocity": velocities_a[:row_idx],
            "acceleration": accelerations_a[:row_idx], "gap": gaps_a[:row_idx],
            "is_smart": is_smart_a[:row_idx],
        })
        metrics = compute_metrics(df, ring_length=ring_length)
        pen = n_smart / n_veh
        return {
            "exp_id": exp_id, "description": desc,
            "controller": "Mixed(FS+ACC)", "n_smart": n_smart,
            "penetration": f"{pen:.3f}", **metrics,
            "notes": f"FS@{fs_indices} ACC@{acc_indices}",
        }

    row = run_mixed("H104", "2FS+2ACC 4/22", [0, 5], [11, 16])
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H104", row["description"], wa, row)
    results.append(row); print(f"  H104: wave_amp={wa:.2f}")

    row = run_mixed("H105", "1FS+1ACC 2/22", [0], [11])
    wa = float(row["wave_amp_ms"])
    evaluate_hypothesis("H105", row["description"], wa, row)
    results.append(row); print(f"  H105: wave_amp={wa:.2f}")

    return results, keeps, reverts, defers, best_wave_amp


# -----------------------------------------------------------------------
# Phase 2.5: Compositions
# -----------------------------------------------------------------------

def run_phase25(keeps, best_wave_amp):
    """Compose the top improvements."""
    NOISE_FLOOR = 0.40
    results = []
    comp_keeps = []

    print("\n" + "=" * 60)
    print("Phase 2.5: Compositional Retests")
    print("=" * 60)

    # C001: Best ACC T_hw + higher penetration + optimal placement
    # Use ACC T_des=0.8 (from H034) at 6/22 (27.3%) with equally-spaced
    row = run_and_record("C001", "ACC T_des=0.8 6/22 (27.3%)", "ACC", 6,
                         smart_controller_factory=lambda: ACCController(T_des=0.8))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C001", wa))
    row["notes"] = f"composition | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C001: ACC T_des=0.8 6/22 -> wave_amp={wa:.2f}")

    # C002: Ring-tuned FS at optimal penetration (6/22)
    row = run_and_record("C002", "FS ring-tuned 6/22", "FollowerStopper", 6,
                         smart_controller_factory=lambda: FollowerStopper(
                             v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C002", wa))
    row["notes"] = f"composition | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C002: FS ring-tuned 6/22 -> wave_amp={wa:.2f}")

    # C003: Best controller (ACC) on larger ring (100/1000)
    row = run_and_record("C003", "ACC 4/22-equiv on 100/1000 (18 ACC)", "ACC", 18,
                         n_vehicles=100, ring_length=1000.0,
                         smart_controller_factory=lambda: ACCController())
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C003", wa))
    row["notes"] = f"composition transfer test | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C003: ACC 18/100 on 1000m ring -> wave_amp={wa:.2f}")

    # C004: ACC at 18.2% with realistic noise (0.5)
    row = run_and_record("C004", "ACC 4/22 noise=0.5", "ACC", 4,
                         smart_controller_factory=lambda: ACCController(),
                         noise_std=0.5)
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C004", wa))
    row["notes"] = f"composition noise robustness | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C004: ACC 4/22 noise=0.5 -> wave_amp={wa:.2f}")

    # C005: ACC T_des=0.8 + k2=1.0 at 4/22
    row = run_and_record("C005", "ACC T_des=0.8 k2=1.0 4/22", "ACC", 4,
                         smart_controller_factory=lambda: ACCController(T_des=0.8, k2=1.0))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C005", wa))
    row["notes"] = f"composition gains | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C005: ACC T_des=0.8 k2=1.0 4/22 -> wave_amp={wa:.2f}")

    # C006: FS ring-tuned at higher penetration 8/22
    row = run_and_record("C006", "FS ring-tuned 8/22", "FollowerStopper", 8,
                         smart_controller_factory=lambda: FollowerStopper(
                             v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C006", wa))
    row["notes"] = f"composition | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C006: FS ring-tuned 8/22 -> wave_amp={wa:.2f}")

    # C007: ACC T_des=1.0 at 3/22 (~14%)
    row = run_and_record("C007", "ACC T_des=1.0 3/22", "ACC", 3,
                         smart_controller_factory=lambda: ACCController(T_des=1.0))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C007", wa))
    row["notes"] = f"composition | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C007: ACC T_des=1.0 3/22 -> wave_amp={wa:.2f}")

    # C008: ACC T_des=0.8 at 3/22 (~14%)
    row = run_and_record("C008", "ACC T_des=0.8 3/22", "ACC", 3,
                         smart_controller_factory=lambda: ACCController(T_des=0.8))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C008", wa))
    row["notes"] = f"composition | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C008: ACC T_des=0.8 3/22 -> wave_amp={wa:.2f}")

    # C009: ACC at 2/22 with T_des=0.8
    row = run_and_record("C009", "ACC T_des=0.8 2/22", "ACC", 2,
                         smart_controller_factory=lambda: ACCController(T_des=0.8))
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C009", wa))
    row["notes"] = f"composition | wave_amp={wa:.2f}"
    results.append(row)
    print(f"  C009: ACC T_des=0.8 2/22 -> wave_amp={wa:.2f}")

    # C010: Mixed 2 ACC(T_des=0.8) + 2 FS(ring-tuned)
    from sim_ring_road import _VehicleState, _gap
    cfg = RingRoadConfig(n_vehicles=22, ring_length=230.0, t_max=600.0, seed=42)
    rng = np.random.RandomState(cfg.seed)
    n_veh = 22
    ring_len = 230.0
    sp = ring_len / n_veh
    base_v = min(sp - 5.0, 10.0)

    vehicles = []
    acc_idx = {0, 11}
    fs_idx = {5, 16}
    for i in range(n_veh):
        pos = i * sp
        vel = max(0.0, base_v + rng.uniform(-0.5, 0.5))
        if i in acc_idx:
            ctrl = ACCController(T_des=0.8)
            is_smart = True
        elif i in fs_idx:
            ctrl = FollowerStopper(v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8)
            is_smart = True
        else:
            ctrl = IDMController(v0=30.0, T=1.0, a=1.3, b=2.0, s0=2.0)
            is_smart = False
        vehicles.append(_VehicleState(position=pos, velocity=vel, controller=ctrl,
                                      is_smart=is_smart, vehicle_id=i))

    n_steps = int(cfg.t_max / cfg.dt) + 1
    total_rows = n_steps * n_veh
    t_a = np.empty(total_rows, dtype=np.float64)
    vid_a = np.empty(total_rows, dtype=np.int32)
    pos_a = np.empty(total_rows, dtype=np.float64)
    vel_a = np.empty(total_rows, dtype=np.float64)
    acc_a = np.empty(total_rows, dtype=np.float64)
    gap_a = np.empty(total_rows, dtype=np.float64)
    sm_a = np.empty(total_rows, dtype=np.bool_)

    ri = 0
    for step in range(n_steps):
        t = step * cfg.dt
        accels = np.empty(n_veh)
        g_arr = np.empty(n_veh)
        for i in range(n_veh):
            leader = (i + 1) % n_veh
            g = _gap(vehicles[i].position, vehicles[leader].position, ring_len, 5.0)
            g_arr[i] = g
            acc = vehicles[i].controller(own_v=vehicles[i].velocity,
                                          lead_v=vehicles[leader].velocity, gap=g, dt=cfg.dt)
            accels[i] = acc
        if cfg.noise_std > 0:
            for i in range(n_veh):
                if not vehicles[i].is_smart:
                    noise = rng.normal(0.0, cfg.noise_std)
                    accels[i] = float(np.clip(accels[i] + noise, -9.0, 3.0))
        if abs(t - cfg.perturb_time) < cfg.dt / 2:
            accels[cfg.perturb_vehicle] = cfg.perturb_decel
        for i in range(n_veh):
            t_a[ri] = t; vid_a[ri] = i; pos_a[ri] = vehicles[i].position
            vel_a[ri] = vehicles[i].velocity; acc_a[ri] = accels[i]
            gap_a[ri] = g_arr[i]; sm_a[ri] = vehicles[i].is_smart
            ri += 1
        for i in range(n_veh):
            vehicles[i].velocity = max(0.0, vehicles[i].velocity + accels[i] * cfg.dt)
            vehicles[i].position = (vehicles[i].position + vehicles[i].velocity * cfg.dt) % ring_len

    df = pd.DataFrame({"time": t_a[:ri], "vehicle_id": vid_a[:ri], "position": pos_a[:ri],
                        "velocity": vel_a[:ri], "acceleration": acc_a[:ri],
                        "gap": gap_a[:ri], "is_smart": sm_a[:ri]})
    metrics = compute_metrics(df, ring_length=ring_len)
    row = {"exp_id": "C010", "description": "2ACC(T=0.8)+2FS(ring) 4/22",
           "controller": "Mixed", "n_smart": 4, "penetration": "0.182",
           **metrics, "notes": "composition mixed"}
    wa = float(row["wave_amp_ms"])
    if wa < best_wave_amp - NOISE_FLOOR:
        best_wave_amp = wa
        comp_keeps.append(("C010", wa))
    results.append(row)
    print(f"  C010: Mixed 2ACC+2FS -> wave_amp={wa:.2f}")

    return results, comp_keeps, best_wave_amp


# -----------------------------------------------------------------------
# Phase B: Discovery Sweep
# -----------------------------------------------------------------------

def run_phase_b():
    """Dense penetration sweep for ACC and ring-tuned FS."""
    print("\n" + "=" * 60)
    print("Phase B: Discovery Sweep — Penetration vs Wave Amplitude")
    print("=" * 60)

    sweep_rows = []

    # ACC sweep: 0 to 22 smart vehicles
    for n_smart in range(0, 23):
        factory = (lambda: ACCController()) if n_smart > 0 else None
        ctrl = "ACC" if n_smart > 0 else "IDM"
        row = run_and_record(
            f"B-ACC-{n_smart:02d}", f"ACC {n_smart}/22",
            ctrl, n_smart,
            smart_controller_factory=factory)
        row["sweep_controller"] = "ACC"
        sweep_rows.append(row)
        print(f"  ACC {n_smart}/22: wave_amp={row['wave_amp_ms']}")

    # Ring-tuned FS sweep: 0 to 22
    for n_smart in range(0, 23):
        factory = (lambda: FollowerStopper(v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8)) if n_smart > 0 else None
        ctrl = "FS-tuned" if n_smart > 0 else "IDM"
        row = run_and_record(
            f"B-FSt-{n_smart:02d}", f"FS-tuned {n_smart}/22",
            ctrl, n_smart,
            smart_controller_factory=factory)
        row["sweep_controller"] = "FS-tuned"
        sweep_rows.append(row)
        print(f"  FS-tuned {n_smart}/22: wave_amp={row['wave_amp_ms']}")

    # Default FS sweep: 0 to 22
    for n_smart in range(0, 23):
        factory = (lambda: FollowerStopper()) if n_smart > 0 else None
        ctrl = "FS-default" if n_smart > 0 else "IDM"
        row = run_and_record(
            f"B-FSd-{n_smart:02d}", f"FS-default {n_smart}/22",
            ctrl, n_smart,
            smart_controller_factory=factory)
        row["sweep_controller"] = "FS-default"
        sweep_rows.append(row)
        print(f"  FS-default {n_smart}/22: wave_amp={row['wave_amp_ms']}")

    return sweep_rows


# -----------------------------------------------------------------------
# Save helpers
# -----------------------------------------------------------------------

def save_results_tsv(phase0_rows, phase2_rows, phase25_rows):
    """Overwrite results.tsv with all rows."""
    all_rows = phase0_rows + phase2_rows + phase25_rows
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TSV_HEADER, delimiter="\t",
                                extrasaction="ignore")
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    print(f"\nResults written to {RESULTS_FILE} ({len(all_rows)} rows)")


def save_sweep_csv(sweep_rows):
    """Save Phase B sweep data."""
    disc_dir = APP_DIR / "discoveries"
    disc_dir.mkdir(exist_ok=True)

    # penetration_sweep.csv
    sweep_file = disc_dir / "penetration_sweep.csv"
    fields = ["sweep_controller", "n_smart", "penetration", "wave_amp_ms",
              "vel_var_ms", "throughput_vph", "fuel_ml_km", "min_spacing_m"]
    with open(sweep_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in sweep_rows:
            writer.writerow(row)
    print(f"Sweep data written to {sweep_file}")

    # Find critical penetration rates
    for ctrl_type in ["ACC", "FS-tuned", "FS-default"]:
        ctrl_rows = [r for r in sweep_rows if r["sweep_controller"] == ctrl_type]
        for r in ctrl_rows:
            wa = float(r["wave_amp_ms"])
            if wa < 1.0:
                pen = float(r["penetration"])
                n = int(r["n_smart"])
                print(f"  {ctrl_type}: wave_amp < 1 m/s at {n}/22 ({pen:.1%})")
                break
        else:
            print(f"  {ctrl_type}: never reaches wave_amp < 1 m/s")

    # Pareto front: wave_amp vs throughput for ACC sweep
    acc_rows = [r for r in sweep_rows if r["sweep_controller"] == "ACC"]
    pareto = []
    best_throughput = -1
    for r in sorted(acc_rows, key=lambda x: float(x["wave_amp_ms"])):
        tp = float(r["throughput_vph"])
        wa = float(r["wave_amp_ms"])
        if tp > best_throughput:
            best_throughput = tp
            pareto.append(r)

    pareto_file = disc_dir / "pareto_front.csv"
    with open(pareto_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in pareto:
            writer.writerow(row)
    print(f"Pareto front written to {pareto_file} ({len(pareto)} points)")

    return acc_rows, pareto


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2: Running 105 pre-registered hypotheses")
    print("=" * 60)

    # Read existing E00 + T01-T12 from results.tsv
    existing_rows = []
    with open(RESULTS_FILE) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            existing_rows.append(row)
    print(f"Loaded {len(existing_rows)} existing rows from results.tsv")

    # Run Phase 2
    phase2_rows, keeps, reverts, defers, best_wave_amp = run_phase2()

    print(f"\n{'='*60}")
    print(f"Phase 2 Summary: {len(keeps)} KEEP / {len(reverts)} REVERT / {len(defers)} DEFER")
    print(f"Best wave_amp after Phase 2: {best_wave_amp:.2f} m/s")
    print(f"{'='*60}")

    if keeps:
        print("\nTop keeps:")
        for eid, wa, desc in sorted(keeps, key=lambda x: x[1]):
            print(f"  {eid}: wave_amp={wa:.2f} — {desc}")

    # Run Phase 2.5
    phase25_rows, comp_keeps, best_wave_amp = run_phase25(keeps, best_wave_amp)

    print(f"\nPhase 2.5 Summary: {len(comp_keeps)} composition improvements")
    print(f"Best wave_amp after Phase 2.5: {best_wave_amp:.2f} m/s")

    # Save Phase 2 + 2.5 results
    save_results_tsv(existing_rows, phase2_rows, phase25_rows)

    # Run Phase B
    sweep_rows = run_phase_b()
    acc_rows, pareto = save_sweep_csv(sweep_rows)

    # Write headline recommendations
    disc_dir = APP_DIR / "discoveries"
    with open(disc_dir / "headline_recommendations.md", "w") as f:
        f.write("# Headline Recommendations\n\n")
        f.write("## Top 5 Actionable Findings\n\n")

        # Find critical penetration for ACC
        acc_critical = None
        for r in sorted(acc_rows, key=lambda x: int(x["n_smart"])):
            if float(r["wave_amp_ms"]) < 1.0:
                acc_critical = r
                break

        if acc_critical:
            f.write(f"1. **Minimum ACC penetration for wave suppression (<1 m/s)**: "
                    f"{acc_critical['n_smart']}/22 vehicles ({float(acc_critical['penetration']):.1%})\n\n")

        f.write("2. **ACC is the best controller family** for the Sugiyama ring road. "
                "At 18.2% penetration it reduces wave amplitude from 8.17 to 0.55 m/s (93.3% reduction).\n\n")

        f.write("3. **FollowerStopper needs ring-specific tuning** to be effective. "
                "Default FS parameters (v_des=15, s_go=35) are calibrated for highways, not the dense ring.\n\n")

        f.write("4. **PIWithSaturation is broken** at 18.2% penetration (30.13 m/s wave). "
                "Integral windup from the large gap-error on the ring causes catastrophic instability.\n\n")

        f.write("5. **The ring road is a simplified model**. Results provide an upper bound "
                "on real-highway effectiveness. No lane changes, no on-ramps, no multi-lane dynamics.\n\n")

    print(f"\nHeadline recommendations written to {disc_dir / 'headline_recommendations.md'}")

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Phase 2: {len(keeps)} KEEP / {len(reverts)} REVERT / {len(defers)} DEFER out of 105")
    print(f"Phase 2.5: {len(comp_keeps)} composition improvements out of 10")
    print(f"Phase B: {len(sweep_rows)} sweep points")
    print(f"Best wave_amp: {best_wave_amp:.2f} m/s")
