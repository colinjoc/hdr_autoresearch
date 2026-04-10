"""Evaluation harness for the phantom-jam ring-road experiments.

Runs simulation configs, records metrics, and produces results.tsv.

Usage:
    python evaluate.py --baseline       # E00 baseline + 5-seed sweep
    python evaluate.py --tournament     # T01-T12 controller tournament
    python evaluate.py --all            # baseline + tournament
    python evaluate.py --experiment H001  # single hypothesis (Phase 2)
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Ensure application root is importable
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from sim_ring_road import RingRoadConfig, simulate
from controllers import (
    FollowerStopper,
    PIWithSaturation,
    ACCController,
    ConstantVelocityController,
    make_controller,
)
from measurements import (
    compute_wave_characteristics,
    compute_mean_velocity_variance,
    compute_throughput,
    compute_fuel_proxy,
)


# -----------------------------------------------------------------------
# Results file
# -----------------------------------------------------------------------

RESULTS_FILE = APP_DIR / "results.tsv"

TSV_HEADER = [
    "exp_id", "description", "controller", "n_smart", "penetration",
    "wave_amp_ms", "vel_var_ms", "throughput_vph", "fuel_ml_km",
    "min_spacing_m", "notes",
]


def _write_results(rows: list[dict], append: bool = False) -> None:
    """Write or append rows to results.tsv."""
    mode = "a" if append else "w"
    file_exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with open(RESULTS_FILE, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TSV_HEADER, delimiter="\t")
        if not append or not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


# -----------------------------------------------------------------------
# Metric extraction
# -----------------------------------------------------------------------

def compute_metrics(
    df: pd.DataFrame,
    ring_length: float = 230.0,
) -> dict[str, float]:
    """Extract all standard metrics from a trajectory DataFrame."""
    wave = compute_wave_characteristics(df, ring_length=ring_length)
    vel_var = compute_mean_velocity_variance(df)
    throughput = compute_throughput(df, lane_length=ring_length)
    fuel = compute_fuel_proxy(df)

    # Min spacing (gap) in the steady-state window (last 2/3)
    t_max = df["time"].max()
    steady_start = t_max / 3.0
    late = df[df["time"] >= steady_start]
    min_spacing = float(late["gap"].min())

    return {
        "wave_amp_ms": round(wave["wave_amplitude_mean"], 2),
        "vel_var_ms": round(vel_var, 2),
        "throughput_vph": round(throughput, 1),
        "fuel_ml_km": round(fuel, 2),
        "min_spacing_m": round(min_spacing, 2),
    }


# -----------------------------------------------------------------------
# Experiment runner
# -----------------------------------------------------------------------

def run_experiment(
    exp_id: str,
    description: str,
    controller_name: str = "IDM",
    n_smart: int = 0,
    n_vehicles: int = 22,
    ring_length: float = 230.0,
    t_max: float = 600.0,
    seed: int = 42,
    smart_controller_factory: Any = None,
    smart_indices: list[int] | None = None,
    notes: str = "",
    **cfg_overrides,
) -> dict:
    """Run a single experiment and return the result row."""
    cfg = RingRoadConfig(
        n_vehicles=n_vehicles,
        ring_length=ring_length,
        t_max=t_max,
        seed=seed,
        **cfg_overrides,
    )

    # Determine smart vehicle indices: default to equally spaced
    if smart_indices is None and n_smart > 0:
        spacing = n_vehicles / n_smart
        smart_indices = [int(round(i * spacing)) % n_vehicles for i in range(n_smart)]
        # Deduplicate
        smart_indices = sorted(set(smart_indices))
        # If dedup reduced count, fill from unused indices
        all_ids = set(range(n_vehicles))
        while len(smart_indices) < n_smart:
            remaining = sorted(all_ids - set(smart_indices))
            if not remaining:
                break
            smart_indices.append(remaining[0])
        smart_indices = sorted(smart_indices)

    if smart_indices is None:
        smart_indices = []

    df = simulate(cfg, smart_indices=smart_indices,
                  smart_controller_factory=smart_controller_factory)
    metrics = compute_metrics(df, ring_length=ring_length)

    penetration = n_smart / n_vehicles if n_vehicles > 0 else 0.0

    row = {
        "exp_id": exp_id,
        "description": description,
        "controller": controller_name,
        "n_smart": n_smart,
        "penetration": f"{penetration:.3f}",
        **metrics,
        "notes": notes,
    }
    return row


def run_seed_sweep(
    base_config: dict,
    seeds: list[int] = (42, 0, 1, 2, 100),
) -> dict[str, tuple[float, float]]:
    """Run the same config across multiple seeds.

    Returns dict mapping metric name to (mean, std).
    """
    all_metrics: dict[str, list[float]] = {}

    for seed in seeds:
        cfg = RingRoadConfig(
            n_vehicles=base_config.get("n_vehicles", 22),
            ring_length=base_config.get("ring_length", 230.0),
            t_max=base_config.get("t_max", 600.0),
            seed=seed,
        )
        df = simulate(cfg)
        metrics = compute_metrics(df, ring_length=cfg.ring_length)
        for k, v in metrics.items():
            all_metrics.setdefault(k, []).append(v)

    result = {}
    for k, vals in all_metrics.items():
        arr = np.array(vals)
        result[k] = (float(np.mean(arr)), float(np.std(arr)))
    return result


# -----------------------------------------------------------------------
# Phase 0.5 Baseline
# -----------------------------------------------------------------------

def run_baseline() -> list[dict]:
    """Run the all-IDM baseline (E00) and 5-seed sweep."""
    print("=" * 60)
    print("Phase 0.5: Baseline (All-IDM ring)")
    print("=" * 60)

    # Single canonical run
    row = run_experiment(
        exp_id="E00",
        description="All-IDM baseline",
        controller_name="IDM",
        n_smart=0,
        seed=42,
        notes="canonical Sugiyama config",
    )
    print(f"\nE00 All-IDM baseline (seed=42):")
    for k in ["wave_amp_ms", "vel_var_ms", "throughput_vph", "fuel_ml_km", "min_spacing_m"]:
        print(f"  {k} = {row[k]}")

    # 5-seed sweep for noise floor
    print("\n5-seed sweep (seeds: 42, 0, 1, 2, 100):")
    sweep = run_seed_sweep({"n_vehicles": 22, "ring_length": 230.0, "t_max": 600.0})
    for k, (mean, std) in sweep.items():
        print(f"  {k}: {mean:.2f} +/- {std:.2f}")

    print(f"\nNoise floor (1-sigma, threshold for KEEP/REVERT):")
    for k, (mean, std) in sweep.items():
        print(f"  {k}: {std:.4f}")

    return [row]


# -----------------------------------------------------------------------
# Phase 1 Tournament
# -----------------------------------------------------------------------

CONTROLLER_FACTORIES = {
    "IDM": lambda: make_controller("IDM", v0=30.0, T=1.0, a=1.3, b=2.0, s0=2.0),
    "FollowerStopper": lambda: FollowerStopper(),
    "PIWithSaturation": lambda: PIWithSaturation(),
    "ACC": lambda: ACCController(),
    "ConstantVelocity": lambda: ConstantVelocityController(),
}


def run_tournament() -> list[dict]:
    """Run the Phase 1 controller family tournament (T01-T12)."""
    print("\n" + "=" * 60)
    print("Phase 1: Controller Family Tournament")
    print("=" * 60)

    rows = []
    exp_counter = 1

    # T01-T10: Each controller at 1/22 and 4/22 penetration
    for ctrl_name, factory in CONTROLLER_FACTORIES.items():
        for n_smart, pen_label in [(1, "4.5%"), (4, "18.2%")]:
            exp_id = f"T{exp_counter:02d}"
            desc = f"{ctrl_name} {pen_label} ({n_smart}/{22})"
            row = run_experiment(
                exp_id=exp_id,
                description=desc,
                controller_name=ctrl_name,
                n_smart=n_smart,
                smart_controller_factory=factory,
                notes=f"equally spaced",
            )
            rows.append(row)
            print(f"  {exp_id}: {desc} -> wave_amp={row['wave_amp_ms']}")
            exp_counter += 1

    # T11: All 22 FollowerStopper (100% penetration ceiling)
    exp_id = "T11"
    desc = "All-FollowerStopper 100% (22/22)"
    row = run_experiment(
        exp_id=exp_id,
        description=desc,
        controller_name="FollowerStopper",
        n_smart=22,
        smart_controller_factory=lambda: FollowerStopper(),
        notes="ceiling check: can wave be fully suppressed?",
    )
    rows.append(row)
    print(f"  {exp_id}: {desc} -> wave_amp={row['wave_amp_ms']}")

    # T12: All 22 ACC (100% penetration ceiling)
    exp_id = "T12"
    desc = "All-ACC 100% (22/22)"
    row = run_experiment(
        exp_id=exp_id,
        description=desc,
        controller_name="ACC",
        n_smart=22,
        smart_controller_factory=lambda: ACCController(),
        notes="ceiling check: can wave be fully suppressed?",
    )
    rows.append(row)
    print(f"  {exp_id}: {desc} -> wave_amp={row['wave_amp_ms']}")

    return rows


# -----------------------------------------------------------------------
# Analysis
# -----------------------------------------------------------------------

def analyze_tournament(baseline_row: dict, tournament_rows: list[dict]) -> None:
    """Print tournament analysis."""
    print("\n" + "=" * 60)
    print("Tournament Analysis")
    print("=" * 60)

    baseline_amp = float(baseline_row["wave_amp_ms"])
    print(f"\nBaseline wave amplitude: {baseline_amp:.2f} m/s")

    # Find best at 18.2% penetration
    at_18 = [r for r in tournament_rows
             if r["penetration"] == "0.182" and r["exp_id"].startswith("T")]
    if at_18:
        best_18 = min(at_18, key=lambda r: float(r["wave_amp_ms"]))
        best_amp = float(best_18["wave_amp_ms"])
        ratio = best_amp / baseline_amp if baseline_amp > 0 else float("inf")
        print(f"\nBest controller at 18.2%: {best_18['controller']}")
        print(f"  Wave amplitude: {best_amp:.2f} m/s")
        print(f"  Controller-to-baseline ratio: {ratio:.3f}")
        if ratio < 0.1:
            print(f"  VERDICT: Nearly suppresses the wave (ratio < 0.1)")
        elif ratio < 0.5:
            print(f"  VERDICT: Meaningful wave reduction (0.1 < ratio < 0.5)")
        else:
            print(f"  VERDICT: Barely helps (ratio > 0.5)")

    # Find best at 4.5% penetration
    at_45 = [r for r in tournament_rows
             if r["penetration"] == "0.045" and r["exp_id"].startswith("T")]
    if at_45:
        best_45 = min(at_45, key=lambda r: float(r["wave_amp_ms"]))
        best_amp_45 = float(best_45["wave_amp_ms"])
        ratio_45 = best_amp_45 / baseline_amp if baseline_amp > 0 else float("inf")
        print(f"\nBest controller at 4.5%: {best_45['controller']}")
        print(f"  Wave amplitude: {best_amp_45:.2f} m/s")
        print(f"  Controller-to-baseline ratio: {ratio_45:.3f}")

    # Ceiling checks
    t11 = [r for r in tournament_rows if r["exp_id"] == "T11"]
    t12 = [r for r in tournament_rows if r["exp_id"] == "T12"]
    if t11:
        t11_amp = float(t11[0]["wave_amp_ms"])
        print(f"\nT11 ceiling (All-FollowerStopper 100%): wave_amp = {t11_amp:.2f} m/s")
        print(f"  Ratio: {t11_amp / baseline_amp:.3f}")
        if t11_amp < 1.0:
            print(f"  Wave fully suppressed at 100% FollowerStopper")
        else:
            print(f"  Residual wave at 100% FollowerStopper")

    if t12:
        t12_amp = float(t12[0]["wave_amp_ms"])
        print(f"\nT12 ceiling (All-ACC 100%): wave_amp = {t12_amp:.2f} m/s")
        print(f"  Ratio: {t12_amp / baseline_amp:.3f}")
        if t12_amp < 1.0:
            print(f"  Wave fully suppressed at 100% ACC")
        else:
            print(f"  Residual wave at 100% ACC")

    # Full tournament table
    print("\n\nFull Tournament Table:")
    print(f"{'exp_id':<6} {'description':<40} {'wave_amp':>9} {'vel_var':>9} "
          f"{'throughput':>11} {'fuel':>10} {'min_gap':>9}")
    print("-" * 100)
    all_rows = [baseline_row] + tournament_rows
    for r in all_rows:
        print(f"{r['exp_id']:<6} {r['description']:<40} {r['wave_amp_ms']:>9} "
              f"{r['vel_var_ms']:>9} {r['throughput_vph']:>11} "
              f"{r['fuel_ml_km']:>10} {r['min_spacing_m']:>9}")


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phantom-jam evaluation harness")
    parser.add_argument("--baseline", action="store_true",
                        help="Run E00 baseline + 5-seed sweep")
    parser.add_argument("--tournament", action="store_true",
                        help="Run T01-T12 controller tournament")
    parser.add_argument("--all", action="store_true",
                        help="Run baseline + tournament")
    parser.add_argument("--experiment", type=str, default=None,
                        help="Run a single hypothesis by ID (Phase 2)")
    args = parser.parse_args()

    if not any([args.baseline, args.tournament, args.all, args.experiment]):
        args.all = True

    all_rows = []

    if args.baseline or args.all:
        baseline_rows = run_baseline()
        all_rows.extend(baseline_rows)

    if args.tournament or args.all:
        tournament_rows = run_tournament()
        all_rows.extend(tournament_rows)

    # Write results
    _write_results(all_rows)
    print(f"\nResults written to {RESULTS_FILE}")

    # Analysis
    if args.all or (args.baseline and args.tournament):
        baseline_row = all_rows[0]
        tournament_rows = all_rows[1:]
        analyze_tournament(baseline_row, tournament_rows)

    if args.experiment:
        print(f"\nExperiment {args.experiment} not yet implemented (Phase 2)")


if __name__ == "__main__":
    main()
