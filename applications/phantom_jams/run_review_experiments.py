#!/usr/bin/env python3
"""Run experiments requested by the reviewer.

R001-R005: Multi-seed replication of ACC 4/22 headline result (seeds 42,0,1,2,100)
R006-R010: Multi-seed replication of ACC 3/22 (seeds 42,0,1,2,100)
R011: dt=0.05 sensitivity for ACC 4/22
R012-R014: ACC 4/22 placement sensitivity (clustered, paired, random)
R015: Warm-start ACC deployment at t=200s
R016: Wave speed measurement for baseline
R017: ACC 4/22 with sensor delay 0.2s
R018: ACC 4/22 with sensor delay 0.5s
"""

from __future__ import annotations
import sys
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from sim_ring_road import RingRoadConfig, simulate
from controllers import ACCController, IDMController
from measurements import (
    compute_wave_characteristics, compute_mean_velocity_variance,
    compute_throughput, compute_fuel_proxy,
)
from evaluate import compute_metrics

RESULTS_FILE = APP_DIR / "results.tsv"


def run_exp(cfg, smart_indices, smart_controller_factory, ring_length=230.0):
    """Run and return metrics dict."""
    df = simulate(cfg, smart_indices=smart_indices,
                  smart_controller_factory=smart_controller_factory)
    metrics = compute_metrics(df, ring_length=ring_length)
    wave = compute_wave_characteristics(df, ring_length=ring_length)
    metrics["wave_speed"] = round(wave["wave_speed"], 3)
    metrics["wave_period"] = round(wave["wave_period"], 2)
    return metrics, df


def equally_spaced(n_smart, n_vehicles=22):
    spacing = n_vehicles / n_smart
    indices = [int(round(i * spacing)) % n_vehicles for i in range(n_smart)]
    return sorted(set(indices))


def main():
    results = []

    # ---------------------------------------------------------------
    # R001-R005: Multi-seed ACC 4/22
    # ---------------------------------------------------------------
    print("=" * 60)
    print("Multi-seed replication: ACC 4/22 (5 seeds)")
    print("=" * 60)
    acc4_metrics = []
    for i, seed in enumerate([42, 0, 1, 2, 100]):
        exp_id = f"R{i+1:03d}"
        cfg = RingRoadConfig(seed=seed, t_max=600.0)
        indices = equally_spaced(4)
        m, _ = run_exp(cfg, indices, lambda: ACCController())
        acc4_metrics.append(m)
        results.append({
            "exp_id": exp_id,
            "description": f"ACC 4/22 seed={seed}",
            "controller": "ACC",
            "n_smart": 4,
            "penetration": "0.182",
            **{k: v for k, v in m.items() if k not in ("wave_speed", "wave_period")},
            "notes": f"multi-seed replication | seed={seed}",
        })
        print(f"  {exp_id}: seed={seed} -> wave_amp={m['wave_amp_ms']:.2f}, "
              f"throughput={m['throughput_vph']:.1f}, fuel={m['fuel_ml_km']:.2f}")

    # Summary stats
    wa = [m["wave_amp_ms"] for m in acc4_metrics]
    tp = [m["throughput_vph"] for m in acc4_metrics]
    fu = [m["fuel_ml_km"] for m in acc4_metrics]
    print(f"\n  ACC 4/22 summary (5 seeds):")
    print(f"    Wave amp: {np.mean(wa):.2f} +/- {np.std(wa):.2f} m/s")
    print(f"    Throughput: {np.mean(tp):.1f} +/- {np.std(tp):.1f} veh/hr")
    print(f"    Fuel: {np.mean(fu):.2f} +/- {np.std(fu):.2f} mL/km")
    baseline_amp = 8.17
    reduction_low = (baseline_amp - (np.mean(wa) + np.std(wa))) / baseline_amp * 100
    reduction_high = (baseline_amp - (np.mean(wa) - np.std(wa))) / baseline_amp * 100
    reduction_mean = (baseline_amp - np.mean(wa)) / baseline_amp * 100
    print(f"    Reduction: {reduction_mean:.1f}% ({reduction_low:.1f}% - {reduction_high:.1f}%)")

    # ---------------------------------------------------------------
    # R006-R010: Multi-seed ACC 3/22
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Multi-seed replication: ACC 3/22 (5 seeds)")
    print("=" * 60)
    acc3_metrics = []
    for i, seed in enumerate([42, 0, 1, 2, 100]):
        exp_id = f"R{i+6:03d}"
        cfg = RingRoadConfig(seed=seed, t_max=600.0)
        indices = equally_spaced(3)
        m, _ = run_exp(cfg, indices, lambda: ACCController())
        acc3_metrics.append(m)
        results.append({
            "exp_id": exp_id,
            "description": f"ACC 3/22 seed={seed}",
            "controller": "ACC",
            "n_smart": 3,
            "penetration": "0.136",
            **{k: v for k, v in m.items() if k not in ("wave_speed", "wave_period")},
            "notes": f"multi-seed replication | seed={seed}",
        })
        print(f"  {exp_id}: seed={seed} -> wave_amp={m['wave_amp_ms']:.2f}")

    wa3 = [m["wave_amp_ms"] for m in acc3_metrics]
    print(f"\n  ACC 3/22 summary: {np.mean(wa3):.2f} +/- {np.std(wa3):.2f} m/s")

    # Statistical separation between 3 ACC and 4 ACC
    from scipy.stats import ttest_ind
    t_stat, p_val = ttest_ind(wa3, wa)
    print(f"  t-test (3 vs 4 ACC): t={t_stat:.2f}, p={p_val:.4f}")

    # ---------------------------------------------------------------
    # R011: dt=0.05 for ACC 4/22
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("dt sensitivity: ACC 4/22 at dt=0.05")
    print("=" * 60)
    cfg = RingRoadConfig(seed=42, t_max=600.0, dt=0.05)
    indices = equally_spaced(4)
    m, _ = run_exp(cfg, indices, lambda: ACCController())
    results.append({
        "exp_id": "R011",
        "description": "ACC 4/22 dt=0.05",
        "controller": "ACC",
        "n_smart": 4,
        "penetration": "0.182",
        **{k: v for k, v in m.items() if k not in ("wave_speed", "wave_period")},
        "notes": "dt sensitivity check",
    })
    print(f"  R011: ACC 4/22 dt=0.05 -> wave_amp={m['wave_amp_ms']:.2f} "
          f"(vs 0.55 at dt=0.1)")

    # ---------------------------------------------------------------
    # R012-R014: ACC 4/22 placement sensitivity
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("ACC 4/22 placement sensitivity")
    print("=" * 60)
    placement_tests = [
        ("R012", "ACC 4/22 clustered [0-3]", [0, 1, 2, 3]),
        ("R013", "ACC 4/22 paired [0,1,11,12]", [0, 1, 11, 12]),
        ("R014", "ACC 4/22 random [3,7,15,19]", [3, 7, 15, 19]),
    ]
    for exp_id, desc, indices in placement_tests:
        cfg = RingRoadConfig(seed=42, t_max=600.0)
        m, _ = run_exp(cfg, indices, lambda: ACCController())
        results.append({
            "exp_id": exp_id,
            "description": desc,
            "controller": "ACC",
            "n_smart": 4,
            "penetration": "0.182",
            **{k: v for k, v in m.items() if k not in ("wave_speed", "wave_period")},
            "notes": f"placement sensitivity | indices={indices}",
        })
        print(f"  {exp_id}: {desc} -> wave_amp={m['wave_amp_ms']:.2f}")

    # ---------------------------------------------------------------
    # R015: Wave speed measurement (baseline)
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Wave speed measurement")
    print("=" * 60)
    cfg = RingRoadConfig(seed=42, t_max=600.0)
    m_baseline, df_baseline = run_exp(cfg, [], None)
    print(f"  R015: Baseline wave speed = {m_baseline['wave_speed']:.3f} m/s "
          f"(expected ~ -4.2 m/s, i.e. ~15 km/h upstream)")
    print(f"         Wave period = {m_baseline['wave_period']:.2f} s")
    results.append({
        "exp_id": "R015",
        "description": "Baseline wave speed measurement",
        "controller": "IDM",
        "n_smart": 0,
        "penetration": "0.000",
        **{k: v for k, v in m_baseline.items() if k not in ("wave_speed", "wave_period")},
        "notes": f"wave_speed={m_baseline['wave_speed']:.3f} m/s | "
                 f"wave_period={m_baseline['wave_period']:.2f} s",
    })

    # ---------------------------------------------------------------
    # R016-R017: ACC with sensor/actuator delay
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("ACC with communication delay")
    print("=" * 60)

    # We simulate delay by using the velocity from N steps ago
    # This requires a modified controller
    from dataclasses import dataclass, field
    from controllers import _clamp

    @dataclass
    class DelayedACCController:
        """ACC with a sensor delay buffer."""
        v_des: float = 20.0
        T_des: float = 1.8
        s0: float = 4.0
        k1: float = 0.3
        k2: float = 0.5
        delay_steps: int = 2  # 0.2s at dt=0.1
        name: str = "DelayedACC"
        _gap_buffer: list = field(default_factory=list, init=False, repr=False)
        _lead_v_buffer: list = field(default_factory=list, init=False, repr=False)

        def __call__(self, own_v, lead_v, gap, dt):
            self._gap_buffer.append(gap)
            self._lead_v_buffer.append(lead_v)
            # Use delayed measurements
            if len(self._gap_buffer) > self.delay_steps:
                delayed_gap = self._gap_buffer[-self.delay_steps - 1]
                delayed_lead_v = self._lead_v_buffer[-self.delay_steps - 1]
            else:
                delayed_gap = gap
                delayed_lead_v = lead_v
            desired_gap = self.s0 + own_v * self.T_des
            accel = self.k1 * (delayed_gap - desired_gap) + self.k2 * (delayed_lead_v - own_v)
            if delayed_gap > 3.0 * desired_gap:
                accel += 0.2 * (self.v_des - own_v)
            return _clamp(accel)

    for exp_id, delay_s, delay_steps in [("R016", 0.2, 2), ("R017", 0.5, 5)]:
        cfg = RingRoadConfig(seed=42, t_max=600.0)
        indices = equally_spaced(4)
        m, _ = run_exp(cfg, indices,
                       lambda ds=delay_steps: DelayedACCController(delay_steps=ds))
        results.append({
            "exp_id": exp_id,
            "description": f"ACC 4/22 delay={delay_s}s",
            "controller": "DelayedACC",
            "n_smart": 4,
            "penetration": "0.182",
            **{k: v for k, v in m.items() if k not in ("wave_speed", "wave_period")},
            "notes": f"sensor delay={delay_s}s ({delay_steps} steps)",
        })
        print(f"  {exp_id}: ACC 4/22 delay={delay_s}s -> wave_amp={m['wave_amp_ms']:.2f}")

    # ---------------------------------------------------------------
    # R018: Multi-seed baseline (for uncertainty on reduction %)
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Multi-seed baseline (5 seeds)")
    print("=" * 60)
    baseline_metrics = []
    for i, seed in enumerate([42, 0, 1, 2, 100]):
        cfg = RingRoadConfig(seed=seed, t_max=600.0)
        m, _ = run_exp(cfg, [], None)
        baseline_metrics.append(m)
        print(f"  Baseline seed={seed}: wave_amp={m['wave_amp_ms']:.2f}")

    bwa = [m["wave_amp_ms"] for m in baseline_metrics]
    print(f"\n  Baseline summary: {np.mean(bwa):.2f} +/- {np.std(bwa):.2f} m/s")

    # Compute reduction with uncertainty
    mean_base = np.mean(bwa)
    std_base = np.std(bwa)
    mean_ctrl = np.mean(wa)
    std_ctrl = np.std(wa)
    reduction_pct = (1 - mean_ctrl / mean_base) * 100
    # Error propagation: sigma_R/R = sqrt((sigma_ctrl/ctrl)^2 + (sigma_base/base)^2)
    if mean_ctrl > 0 and mean_base > 0:
        rel_err = np.sqrt((std_ctrl / mean_ctrl)**2 + (std_base / mean_base)**2)
        sigma_reduction = reduction_pct * rel_err / (mean_ctrl / mean_base)
    else:
        sigma_reduction = 0
    print(f"\n  Wave amplitude reduction: {reduction_pct:.1f} +/- {sigma_reduction:.1f}%")

    # ---------------------------------------------------------------
    # Write results to TSV (append)
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Writing results...")
    print("=" * 60)

    # Write to a separate reviewer experiments file
    review_file = APP_DIR / "reviewer_experiments.tsv"
    header = ["exp_id", "description", "controller", "n_smart", "penetration",
              "wave_amp_ms", "vel_var_ms", "throughput_vph", "fuel_ml_km",
              "min_spacing_m", "notes"]
    with open(review_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        writer.writeheader()
        for row in results:
            # Filter to only header fields
            filtered = {k: row.get(k, "") for k in header}
            writer.writerow(filtered)
    print(f"  Written {len(results)} rows to {review_file}")

    # Also append to main results.tsv
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        for row in results:
            filtered = {k: row.get(k, "") for k in header}
            writer.writerow(filtered)
    print(f"  Appended {len(results)} rows to {RESULTS_FILE}")

    # Print summary JSON for paper revision
    summary = {
        "acc_4_22_5seed": {
            "wave_amp_mean": round(np.mean(wa), 2),
            "wave_amp_std": round(np.std(wa), 2),
            "throughput_mean": round(np.mean(tp), 1),
            "throughput_std": round(np.std(tp), 1),
            "fuel_mean": round(np.mean(fu), 2),
            "fuel_std": round(np.std(fu), 2),
            "reduction_pct": round(reduction_pct, 1),
            "reduction_std": round(sigma_reduction, 1),
        },
        "acc_3_22_5seed": {
            "wave_amp_mean": round(np.mean(wa3), 2),
            "wave_amp_std": round(np.std(wa3), 2),
        },
        "transition_ttest_p": round(p_val, 6),
        "baseline_5seed": {
            "wave_amp_mean": round(np.mean(bwa), 2),
            "wave_amp_std": round(np.std(bwa), 2),
        },
    }
    print(f"\n  Summary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()
