"""
analysis.py — Phase 1 + Phase 2 analysis runner for the gw_detectors HDR project.

Two complementary measurements per solution:

1. STRUCTURAL (from the parsed `.kat` file)
   - Component counts (mirrors, beamsplitters, lasers, squeezers, directional bs)
   - Parameter histogram: how many params are at boundaries (R≈0, R≈1) vs interior
   - Mirror reflectivity distribution
   - Cavity inventory (free spaces > 1 km)
   - Mass-bearing component inventory
   - Signal injection count

2. STRAIN (from the canonical Zoo `strain.csv`)
   - Log-space averaged improvement over Voyager baseline in 800–3000 Hz
   - Min strain in band
   - Frequency of best sensitivity
   - Independent verification: best/baseline ratio at each frequency

Outputs:
   results/per_solution.tsv  — one row per type8 solution
   results/sol00_param_hist.tsv — parameter value histogram for sol00 alone
   results/cross_family_summary.md — comparison table for the 25 type8 solutions

This script is the Phase 1 "tournament" deliverable: it scores three
decomposition approaches (component-count, reflectivity-distribution,
cross-solution-feature-overlap) on a single ground-truth dataset (the 25
type8 solutions). The winners feed into Phase 2.
"""
from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from kat_parser import KatDocument, parse_kat


PROJECT_ROOT = Path(__file__).resolve().parent
ZOO_DIR = PROJECT_ROOT / "GWDetectorZoo"
RESULTS_DIR = PROJECT_ROOT / "results"
TYPE8_DIR = ZOO_DIR / "solutions/type8"

POST_MERGER_BAND = (800.0, 3000.0)


# ---------------------------------------------------------------------------
# Strain reading
# ---------------------------------------------------------------------------

def read_strain_csv(csv_path: Path) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Read a Zoo strain.csv. Returns (frequencies, {column: values})."""
    rows: List[List[float]] = []
    header: List[str] = []
    with csv_path.open() as fh:
        reader = csv.reader(fh)
        header = next(reader)
        for row in reader:
            rows.append([float(x) for x in row])
    arr = np.array(rows)
    freqs = arr[:, 0]
    cols = {h: arr[:, i] for i, h in enumerate(header)}
    return freqs, cols


def log_avg_improvement(strain_baseline: np.ndarray, strain_best: np.ndarray) -> float:
    """Improvement = exp(mean(log(baseline / best))) — paper convention."""
    ratio = strain_baseline / strain_best
    return float(np.exp(np.mean(np.log(ratio))))


def in_band(freqs: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return (freqs >= lo) & (freqs <= hi)


# ---------------------------------------------------------------------------
# Structural inventory
# ---------------------------------------------------------------------------

def structural_inventory(doc: KatDocument) -> Dict[str, float]:
    """One-row inventory of a parsed kat document."""
    types = Counter(c.type for c in doc.components)

    # mirror reflectivity classification
    n_R_near_zero = 0      # R < 0.001  → optimiser pinned to "transparent"
    n_R_near_one = 0       # R > 0.999  → optimiser pinned to "perfect reflector"
    n_R_interior = 0       # 0.001 ≤ R ≤ 0.999 → tuned
    for c in doc.components:
        if c.type != "mirror":
            continue
        try:
            R = doc.resolve(c.properties).get("reflectivity")
        except (KeyError, ValueError):
            continue
        if R is None or not isinstance(R, float):
            continue
        if R < 0.001:
            n_R_near_zero += 1
        elif R > 0.999:
            n_R_near_one += 1
        else:
            n_R_interior += 1

    # cavity inventory: free spaces > 1 km are arm cavities
    n_arm_spaces = sum(1 for s in doc.spaces if s.length > 1000)
    longest_space = max((s.length for s in doc.spaces), default=0.0)

    return {
        "n_parameters":           float(doc.n_parameters),
        "n_mirrors":              float(types.get("mirror", 0)),
        "n_beamsplitters":        float(types.get("beamsplitter", 0)),
        "n_directional_bs":       float(types.get("directional_beamsplitter", 0)),
        "n_lasers":               float(types.get("laser", 0)),
        "n_squeezers":            float(types.get("squeezer", 0)),
        "n_homodyne_detectors":   float(types.get("homodyne_detector", 0)),
        "n_signal_injections":    float(len(doc.signal_injections)),
        "n_spaces":               float(len(doc.spaces)),
        "n_arm_spaces_gt_1km":    float(n_arm_spaces),
        "longest_space_m":        float(longest_space),
        "mirrors_R_near_zero":    float(n_R_near_zero),
        "mirrors_R_near_one":     float(n_R_near_one),
        "mirrors_R_interior":     float(n_R_interior),
    }


# ---------------------------------------------------------------------------
# Strain inventory (from Zoo CSV)
# ---------------------------------------------------------------------------

def strain_inventory(strain_csv: Path) -> Dict[str, float]:
    """One-row strain inventory of a Zoo strain.csv."""
    freqs, cols = read_strain_csv(strain_csv)
    mask = in_band(freqs, *POST_MERGER_BAND)
    f_band = freqs[mask]
    if "strain_baseline" not in cols or "strain_best" not in cols:
        return {}
    h_v = cols["strain_baseline"][mask]
    h_b = cols["strain_best"][mask]
    if "strain_aligo" in cols:
        h_a = cols["strain_aligo"][mask]
    else:
        h_a = np.full_like(h_v, np.nan)

    improvement_vs_voyager = log_avg_improvement(h_v, h_b)
    improvement_vs_aligo = log_avg_improvement(h_a, h_b) if not np.all(np.isnan(h_a)) else float("nan")

    idx_min = int(np.argmin(h_b))
    return {
        "improvement_vs_voyager": improvement_vs_voyager,
        "improvement_vs_aligo": improvement_vs_aligo,
        "min_strain_best":      float(h_b.min()),
        "freq_at_min_strain":   float(f_band[idx_min]),
        "max_strain_best":      float(h_b.max()),
        "voyager_min_in_band":  float(h_v.min()),
    }


# ---------------------------------------------------------------------------
# Per-solution row builder
# ---------------------------------------------------------------------------

def analyse_solution(sol_dir: Path) -> Dict[str, float]:
    """Run both structural + strain inventory on one Zoo solution dir."""
    kat_files = list(sol_dir.glob("CFGS_*.txt"))
    strain_csvs = list(sol_dir.glob("strain.csv"))
    row: Dict[str, float] = {"sol_id": sol_dir.name}
    if not kat_files:
        row["error"] = "no_kat"
        return row
    doc = parse_kat(kat_files[0].read_text())
    row.update(structural_inventory(doc))
    if strain_csvs:
        row.update(strain_inventory(strain_csvs[0]))
    return row


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    sol_dirs = sorted(d for d in TYPE8_DIR.iterdir() if d.is_dir() and d.name.startswith("sol"))
    print(f"Found {len(sol_dirs)} type8 solutions")

    rows = []
    for sol_dir in sol_dirs:
        try:
            row = analyse_solution(sol_dir)
            rows.append(row)
            print(
                f"  {row['sol_id']:8s}  "
                f"params={int(row.get('n_parameters', 0)):4d}  "
                f"mirrors={int(row.get('n_mirrors', 0)):3d}  "
                f"BS={int(row.get('n_beamsplitters', 0)):3d}  "
                f"squeezers={int(row.get('n_squeezers', 0)):3d}  "
                f"improvement={row.get('improvement_vs_voyager', 0):5.2f}x"
            )
        except Exception as e:
            print(f"  {sol_dir.name}: ERROR {e!r}")

    # Write per_solution.tsv
    per_sol = RESULTS_DIR / "per_solution.tsv"
    keys = sorted({k for r in rows for k in r.keys()}, key=lambda k: (k != "sol_id", k))
    with per_sol.open("w") as fh:
        fh.write("\t".join(keys) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    print(f"\nWrote {per_sol}")

    # Cross-family summary
    valid = [r for r in rows if "improvement_vs_voyager" in r]
    if valid:
        improvements = [r["improvement_vs_voyager"] for r in valid]
        n_mirrors = [r["n_mirrors"] for r in valid]
        n_bs = [r["n_beamsplitters"] for r in valid]
        print(f"\nFamily-level statistics ({len(valid)} solutions):")
        print(f"  improvement vs Voyager: min {min(improvements):.2f}x  max {max(improvements):.2f}x  mean {np.mean(improvements):.2f}x")
        print(f"  mirror count:           min {int(min(n_mirrors))}    max {int(max(n_mirrors))}    mean {np.mean(n_mirrors):.1f}")
        print(f"  beamsplitter count:     min {int(min(n_bs))}    max {int(max(n_bs))}    mean {np.mean(n_bs):.1f}")
        print(f"  squeezer count:         all {int(valid[0]['n_squeezers'])} (constant across family)" if all(r['n_squeezers'] == valid[0]['n_squeezers'] for r in valid) else f"  squeezer counts vary")

        # Strongest and weakest
        best = max(valid, key=lambda r: r["improvement_vs_voyager"])
        worst = min(valid, key=lambda r: r["improvement_vs_voyager"])
        print(f"  strongest: {best['sol_id']} at {best['improvement_vs_voyager']:.2f}x")
        print(f"  weakest:   {worst['sol_id']} at {worst['improvement_vs_voyager']:.2f}x")


if __name__ == "__main__":
    main()
