"""
sol00_anatomy.py — Phase 2 structural anatomy of type8/sol00.

The Phase 1 cross-family analysis showed sol00 is dramatically better than
its 24 family members (4.05× over Voyager vs ~1.10× median). This script
zooms in on sol00 to find:

  - Which mirrors are at boundary R values (≈0 or ≈1) — pinned by the optimiser
  - Which mirrors are interior — actually tuned
  - Which spaces are arm-cavity-length — long-baseline cavities
  - Which mirrors form the boundaries of which arm cavities
  - Mass distribution across mass-bearing components
  - Parameter histogram by category (R values, masses, lengths, tunings)
  - Cross-correlation: are any "tuned" parameters at the same value?

Outputs:
  results/sol00_mirrors.tsv      one row per mirror (R, loss, tuning)
  results/sol00_spaces.tsv       one row per space
  results/sol00_param_histogram.tsv  parameter values bucketed
  results/sol00_correlations.md  any non-trivial correlations found
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, List

import numpy as np

from kat_parser import parse_kat


PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"
SOL00_KAT = PROJECT_ROOT / "GWDetectorZoo/solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    doc = parse_kat(SOL00_KAT.read_text())

    print("=" * 70)
    print("type8/sol00 — structural anatomy")
    print("=" * 70)
    print(f"108 parameters, 57 mirrors, 13 BSs, 3 lasers, 0 squeezers, 1 dbs\n")

    # ----- Mirror table -----
    mirror_rows = []
    for c in doc.components:
        if c.type != "mirror":
            continue
        try:
            R = doc.resolve(c.properties).get("reflectivity")
            loss = doc.resolve(c.properties).get("loss")
            tuning = doc.resolve(c.properties).get("tuning")
            mass = doc.resolve(c.properties).get("mass", float("nan"))
        except (KeyError, ValueError):
            R = loss = tuning = mass = float("nan")
        if isinstance(R, str) or R is None:
            R = float("nan")
        if isinstance(mass, str):
            mass = float("nan")
        mirror_rows.append({
            "name": c.name,
            "R": float(R) if R is not None else float("nan"),
            "loss": float(loss) if loss not in (None, "") else float("nan"),
            "tuning": float(tuning) if tuning not in (None, "") else float("nan"),
            "mass": float(mass) if not isinstance(mass, str) else float("nan"),
            "ports": ",".join(c.ports),
        })

    mirror_rows.sort(key=lambda r: -r["R"] if not np.isnan(r["R"]) else 0)
    with (RESULTS_DIR / "sol00_mirrors.tsv").open("w") as fh:
        fh.write("name\tR\tloss\ttuning\tmass\tports\n")
        for r in mirror_rows:
            fh.write(f"{r['name']}\t{r['R']:.6e}\t{r['loss']:.3e}\t{r['tuning']:.3f}\t{r['mass']:.2f}\t{r['ports']}\n")

    # Reflectivity classification
    bins = {"R<0.001": 0, "0.001-0.01": 0, "0.01-0.1": 0, "0.1-0.4": 0, "0.4-0.6": 0,
            "0.6-0.9": 0, "0.9-0.99": 0, "0.99-0.999": 0, "R>=0.999": 0}
    for r in mirror_rows:
        R = r["R"]
        if np.isnan(R):
            continue
        if R < 0.001: bins["R<0.001"] += 1
        elif R < 0.01: bins["0.001-0.01"] += 1
        elif R < 0.1: bins["0.01-0.1"] += 1
        elif R < 0.4: bins["0.1-0.4"] += 1
        elif R < 0.6: bins["0.4-0.6"] += 1
        elif R < 0.9: bins["0.6-0.9"] += 1
        elif R < 0.99: bins["0.9-0.99"] += 1
        elif R < 0.999: bins["0.99-0.999"] += 1
        else: bins["R>=0.999"] += 1

    print("Mirror reflectivity distribution:")
    for k, n in bins.items():
        print(f"  R in {k:14s}: {'#' * n:60s} {n}")

    # ----- Mass distribution -----
    masses = [r["mass"] for r in mirror_rows if not np.isnan(r["mass"])]
    if masses:
        print(f"\nMirrors with explicit mass: {len(masses)} of 57")
        print(f"  mass range: {min(masses):.2f} – {max(masses):.2f} kg")
        print(f"  median mass: {np.median(masses):.2f} kg")
        # Voyager test mass is 200 kg
        n_at_200 = sum(1 for m in masses if 199.99 < m < 200.01)
        n_below_50 = sum(1 for m in masses if m < 50)
        print(f"  exactly at 200 kg (Voyager nominal): {n_at_200}")
        print(f"  below 50 kg (light test masses): {n_below_50}")

    # ----- Space inventory -----
    print(f"\nSpace inventory: {len(doc.spaces)} total")
    long_spaces = [s for s in doc.spaces if s.length > 100]
    long_spaces.sort(key=lambda s: -s.length)
    print(f"  spaces > 100m: {len(long_spaces)}")
    for s in long_spaces[:15]:
        print(f"    {s.name:20s} length={s.length:8.1f} m  {s.node_a:25s} <-> {s.node_b}")

    with (RESULTS_DIR / "sol00_spaces.tsv").open("w") as fh:
        fh.write("name\tlength_m\tnode_a\tnode_b\n")
        for s in sorted(doc.spaces, key=lambda x: -x.length):
            fh.write(f"{s.name}\t{s.length:.6f}\t{s.node_a}\t{s.node_b}\n")

    # ----- Beamsplitter table -----
    print(f"\nBeamsplitters (13 expected):")
    bs_count = 0
    for c in doc.components:
        if c.type != "beamsplitter":
            continue
        bs_count += 1
        try:
            R = doc.resolve(c.properties).get("reflectivity")
            angle = doc.resolve(c.properties).get("angle")
        except (KeyError, ValueError):
            R = angle = float("nan")
        if isinstance(R, str): R = float("nan")
        if isinstance(angle, str): angle = float("nan")
        print(f"  {c.name:6s}  R={R:.4f}  angle={angle:+.0f}°  ports=[{', '.join(c.ports)}]")
    print(f"  total: {bs_count}")

    # ----- Parameter histogram -----
    param_values = list(doc.parameters.values())
    sub_one = sum(1 for v in param_values if 0 <= v <= 1)
    masses_in_params = sum(1 for v in param_values if 1 < v < 250)
    near_zero = sum(1 for v in param_values if abs(v) < 1e-4)
    near_one = sum(1 for v in param_values if 0.999 < v < 1.001)
    print(f"\nParameter value distribution (n={len(param_values)}):")
    print(f"  near zero    (|v| < 1e-4):    {near_zero}")
    print(f"  near one     (0.999 < v < 1.001): {near_one}")
    print(f"  in [0, 1]    (R-like):         {sub_one}")
    print(f"  in (1, 250]  (mass-like):      {masses_in_params}")

    # Save histogram
    with (RESULTS_DIR / "sol00_param_histogram.tsv").open("w") as fh:
        fh.write("param_name\tvalue\n")
        for name, value in sorted(doc.parameters.items()):
            fh.write(f"{name}\t{value:.6e}\n")

    print("\nWrote sol00_mirrors.tsv, sol00_spaces.tsv, sol00_param_histogram.tsv")


if __name__ == "__main__":
    main()
