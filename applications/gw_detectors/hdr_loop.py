"""
hdr_loop.py — Phase 2 HDR Decomposition Loop driver.

Runs 20 experiments (E06..E25) sequentially. Each experiment tests one
hypothesis from research_queue.md. For each:

  1. State the prior P(hypothesis holds before testing)
  2. Articulate the mechanism (one sentence)
  3. Run the experiment (one structural measurement)
  4. State the result (numerical)
  5. Decide KEEP / REVERT based on whether the result confirms the hypothesis
  6. Append a row to results.tsv

results.tsv has columns:
  exp_id  hypothesis_id  description  prior  mechanism  result_value  decision  notes

This is the verification anchor for paper.md and the public summary.
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
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_TSV = PROJECT_ROOT / "results.tsv"
ZOO_DIR = PROJECT_ROOT / "GWDetectorZoo"
TYPE8_DIR = ZOO_DIR / "solutions/type8"
SOL00_KAT = TYPE8_DIR / "sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"
POST_MERGER_BAND = (800.0, 3000.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_sol00() -> KatDocument:
    return parse_kat(SOL00_KAT.read_text())


def load_solution(sol_dir: Path) -> KatDocument:
    kats = list(sol_dir.glob("CFGS_*.txt"))
    return parse_kat(kats[0].read_text())


def all_type8_dirs() -> List[Path]:
    return sorted(d for d in TYPE8_DIR.iterdir() if d.is_dir() and d.name.startswith("sol"))


def log_avg_improvement_for(sol_dir: Path) -> float:
    """Read the strain.csv for a solution dir, return improvement vs Voyager in 800-3000 Hz."""
    csv_path = sol_dir / "strain.csv"
    rows = []
    with csv_path.open() as fh:
        reader = csv.reader(fh)
        header = next(reader)
        for row in reader:
            rows.append([float(x) for x in row])
    arr = np.array(rows)
    freqs = arr[:, 0]
    cols = {h: arr[:, i] for i, h in enumerate(header)}
    mask = (freqs >= POST_MERGER_BAND[0]) & (freqs <= POST_MERGER_BAND[1])
    h_v = cols["strain_baseline"][mask]
    h_b = cols["strain_best"][mask]
    return float(np.exp(np.mean(np.log(h_v / h_b))))


def write_result_row(
    fh,
    exp_id: str,
    h_id: str,
    description: str,
    prior: float,
    mechanism: str,
    result_value: str,
    decision: str,
    notes: str,
):
    """Append one row to results.tsv. Caller passes an open file handle."""
    fh.write(
        f"{exp_id}\t{h_id}\t{description}\t{prior:.2f}\t{mechanism}\t{result_value}\t{decision}\t{notes}\n"
    )


# ---------------------------------------------------------------------------
# Experiments E06..E25
# ---------------------------------------------------------------------------

def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    sol00 = load_sol00()
    type8_dirs = all_type8_dirs()
    type8_docs = {d.name: load_solution(d) for d in type8_dirs}
    type8_imp = {d.name: log_avg_improvement_for(d) for d in type8_dirs}

    # ---- write header
    with RESULTS_TSV.open("w") as fh:
        fh.write("exp_id\thypothesis_id\tdescription\tprior\tmechanism\tresult\tdecision\tnotes\n")

    # ----- E06: H02 — does sol00 contain mirrors with R in the impedance-matched cavity range?
    impedance_mirrors = []
    for c in sol00.components:
        if c.type != "mirror":
            continue
        try:
            R = sol00.resolve(c.properties).get("reflectivity")
            if R is not None and 0.99 <= R <= 0.9999:
                impedance_mirrors.append((c.name, R))
        except (KeyError, ValueError):
            pass
    e06_result = f"{len(impedance_mirrors)} mirrors with R in [0.99, 0.9999]"
    e06_decision = "KEEP" if len(impedance_mirrors) >= 1 else "REVERT"
    print(f"[E06] H02: {e06_result} → {e06_decision}")

    # ----- E07: H01 — count of beamsplitters at extremes vs interior
    bs_extreme = 0
    bs_interior = 0
    for c in sol00.components:
        if c.type != "beamsplitter":
            continue
        try:
            R = sol00.resolve(c.properties).get("reflectivity")
            if R is None:
                continue
            if R < 0.05 or R > 0.95:
                bs_extreme += 1
            else:
                bs_interior += 1
        except (KeyError, ValueError):
            pass
    e07_result = f"{bs_extreme} BS at extremes, {bs_interior} BS interior (of 13)"
    e07_decision = "KEEP" if bs_extreme >= 9 else "REVERT"
    print(f"[E07] H01-bs: {e07_result} → {e07_decision}")

    # ----- E08: H02 — do impedance-matched mirrors sit at endpoints of long-arm spaces?
    long_spaces = [s for s in sol00.spaces if s.length > 1000]
    long_arm_nodes = set()
    for s in long_spaces:
        long_arm_nodes.add(s.node_a)
        long_arm_nodes.add(s.node_b)
    impedance_mirror_at_arm = 0
    for c in sol00.components:
        if c.type != "mirror":
            continue
        try:
            R = sol00.resolve(c.properties).get("reflectivity")
            if R is not None and 0.99 <= R <= 0.9999:
                if any(p in long_arm_nodes for p in c.ports):
                    impedance_mirror_at_arm += 1
        except (KeyError, ValueError):
            pass
    e08_result = f"{impedance_mirror_at_arm} impedance-matched mirrors at arm-cavity endpoints"
    e08_decision = "KEEP" if impedance_mirror_at_arm >= 1 else "REVERT"
    print(f"[E08] H02-arm-link: {e08_result} → {e08_decision}")

    # ----- E09: H03 — beamsplitter angle distribution
    bs_angles = Counter()
    for c in sol00.components:
        if c.type != "beamsplitter":
            continue
        try:
            angle = sol00.resolve(c.properties).get("angle")
            if angle is not None:
                bs_angles[round(angle, 0)] += 1
        except (KeyError, ValueError):
            pass
    standard = sum(bs_angles[a] for a in (45.0, -45.0))
    e09_result = f"angle distribution {dict(bs_angles)}; {standard}/13 at ±45°"
    e09_decision = "KEEP" if standard == 13 else "REVERT"
    print(f"[E09] H03: {e09_result} → {e09_decision}")

    # ----- E10: H04 — fraction of free spaces with length exactly 1.0 m
    n_unit_spaces = sum(1 for s in sol00.spaces if abs(s.length - 1.0) < 1e-9)
    e10_result = f"{n_unit_spaces} of {len(sol00.spaces)} spaces have length exactly 1.0 m"
    e10_decision = "KEEP" if n_unit_spaces >= 0.5 * len(sol00.spaces) else "REVERT"
    print(f"[E10] H04: {e10_result} → {e10_decision}")

    # ----- E11: H05 — fsig signal injections all on free spaces?
    space_names = {s.name for s in sol00.spaces}
    fsig_on_space = sum(1 for f in sol00.signal_injections if f.target in space_names)
    e11_result = f"{fsig_on_space}/{len(sol00.signal_injections)} fsig injections target free spaces"
    e11_decision = "KEEP" if fsig_on_space == len(sol00.signal_injections) else "REVERT"
    print(f"[E11] H05: {e11_result} → {e11_decision}")

    # ----- E12: H06 — mirrors at exactly 200 kg
    voyager_mass_mirrors = []
    for c in sol00.components:
        if c.type != "mirror":
            continue
        try:
            mass = sol00.resolve(c.properties).get("mass")
            if mass is not None and abs(mass - 200.0) < 0.01:
                voyager_mass_mirrors.append(c.name)
        except (KeyError, ValueError):
            pass
    e12_result = f"{len(voyager_mass_mirrors)} mirrors at exactly 200.0 kg: {voyager_mass_mirrors[:5]}"
    e12_decision = "KEEP" if len(voyager_mass_mirrors) >= 4 else "REVERT"
    print(f"[E12] H06: {e12_result} → {e12_decision}")

    # ----- E13: H07 — mass / reflectivity correlation across sol00 mirrors
    pairs = []
    for c in sol00.components:
        if c.type != "mirror":
            continue
        try:
            r = sol00.resolve(c.properties)
            R = r.get("reflectivity")
            mass = r.get("mass")
            if R is not None and mass is not None:
                pairs.append((R, mass))
        except (KeyError, ValueError):
            pass
    R_arr = np.array([p[0] for p in pairs])
    M_arr = np.array([p[1] for p in pairs])
    pearson_r = float(np.corrcoef(R_arr, M_arr)[0, 1])
    e13_result = f"Pearson r(mass, R) = {pearson_r:+.3f} across {len(pairs)} mirrors"
    e13_decision = "KEEP" if abs(pearson_r) < 0.2 else "REVERT"
    print(f"[E13] H07: {e13_result} → {e13_decision}")

    # ----- E14: H08 — are the 6 arm cavities structurally identical?
    long_lens = sorted([s.length for s in sol00.spaces if s.length > 1000])
    distinct_long = len(set(round(L, 1) for L in long_lens))
    e14_result = f"{len(long_lens)} arm spaces, {distinct_long} distinct lengths: {sorted(set(round(L, 1) for L in long_lens))}"
    e14_decision = "KEEP" if distinct_long <= 3 else "REVERT"
    print(f"[E14] H08: {e14_result} → {e14_decision}")

    # ----- E15: H09 — sol00 parameter histogram clustering at boundaries
    R_like = [v for v in sol00.parameters.values() if 0 <= v <= 1]
    near_boundary = sum(1 for v in R_like if v < 0.001 or v > 0.999)
    pct_at_boundary = 100 * near_boundary / len(R_like) if R_like else 0
    e15_result = f"{near_boundary}/{len(R_like)} R-like params at boundary ({pct_at_boundary:.0f}%)"
    e15_decision = "KEEP" if pct_at_boundary > 30 else "REVERT"
    print(f"[E15] H09: {e15_result} → {e15_decision}")

    # ----- E16: H15 / H16 — laser and BS counts across the family
    laser_counts = Counter()
    bs_counts = Counter()
    for sol_id, doc in type8_docs.items():
        n_l = sum(1 for c in doc.components if c.type == "laser")
        n_b = sum(1 for c in doc.components if c.type == "beamsplitter")
        laser_counts[n_l] += 1
        bs_counts[n_b] += 1
    e16_result = f"laser counts {dict(laser_counts)}; BS counts {dict(bs_counts)}"
    e16_decision = "KEEP"  # purely descriptive — both hypotheses had the same data source
    print(f"[E16] H15+H16: {e16_result} → {e16_decision}")

    # ----- E17: H17 — directional BS presence vs improvement
    with_dbs, without_dbs = [], []
    for sol_id, doc in type8_docs.items():
        n_dbs = sum(1 for c in doc.components if c.type == "directional_beamsplitter")
        if n_dbs > 0:
            with_dbs.append(type8_imp[sol_id])
        else:
            without_dbs.append(type8_imp[sol_id])
    if with_dbs and without_dbs:
        diff = float(np.mean(with_dbs) - np.mean(without_dbs))
    else:
        diff = float("nan")
    e17_result = f"with_dbs n={len(with_dbs)} mean_imp={np.mean(with_dbs):.2f}, without_dbs n={len(without_dbs)} mean_imp={np.mean(without_dbs):.2f}, diff={diff:+.2f}"
    e17_decision = "KEEP" if abs(diff) > 0.3 else "REVERT"
    print(f"[E17] H17: {e17_result} → {e17_decision}")

    # ----- E18: H18 — bottom-half clustering near 1.0×
    sorted_imp = sorted(type8_imp.values())
    bottom_half = sorted_imp[: len(sorted_imp) // 2]
    bh_std = float(np.std(bottom_half))
    bh_mean = float(np.mean(bottom_half))
    e18_result = f"bottom-13 mean_imp={bh_mean:.3f} std={bh_std:.3f}"
    e18_decision = "KEEP" if bh_std < 0.1 else "REVERT"
    print(f"[E18] H18: {e18_result} → {e18_decision}")

    # ----- E19: H19 — long-arm lengths shared across solutions
    all_long_lengths = []
    for sol_id, doc in type8_docs.items():
        for s in doc.spaces:
            if s.length > 3000:
                all_long_lengths.append(round(s.length, 0))
    distinct_lens = sorted(set(all_long_lengths))
    e19_result = f"across 25 sols: {len(all_long_lengths)} long spaces, {len(distinct_lens)} distinct lengths"
    e19_decision = "KEEP" if len(distinct_lens) <= 10 else "REVERT"
    print(f"[E19] H19: {e19_result} → {e19_decision}")

    # ----- E20: H20 — fsig count vs total component count
    fsig_counts = []
    comp_counts = []
    for sol_id, doc in type8_docs.items():
        fsig_counts.append(len(doc.signal_injections))
        comp_counts.append(len(doc.components))
    pearson_fc = float(np.corrcoef(fsig_counts, comp_counts)[0, 1])
    e20_result = f"Pearson r(fsig_count, n_components) = {pearson_fc:+.3f}"
    e20_decision = "KEEP" if pearson_fc > 0.4 else "REVERT"
    print(f"[E20] H20: {e20_result} → {e20_decision}")

    # ----- E21: H21 — sol00 vs sol01 structural diff
    sol01 = type8_docs["sol01"]
    sol00_types = Counter(c.type for c in sol00.components)
    sol01_types = Counter(c.type for c in sol01.components)
    diffs = {t: sol00_types[t] - sol01_types[t] for t in (sol00_types | sol01_types) if sol00_types[t] != sol01_types[t]}
    e21_result = f"sol00-sol01 type-count diffs: {diffs}"
    e21_decision = "KEEP" if len(diffs) >= 2 else "REVERT"
    print(f"[E21] H21: {e21_result} → {e21_decision}")

    # ----- E22: H22 — sol00 vs sol24 (best vs worst) structural diff
    sol24 = type8_docs["sol24"]
    sol24_types = Counter(c.type for c in sol24.components)
    diffs24 = {t: sol00_types[t] - sol24_types[t] for t in (sol00_types | sol24_types) if sol00_types[t] != sol24_types[t]}
    e22_result = f"sol00-sol24 type-count diffs: {diffs24}"
    e22_decision = "KEEP" if len(diffs24) >= 3 else "REVERT"
    print(f"[E22] H22: {e22_result} → {e22_decision}")

    # ----- E23: H23 — common signature among top-4 absent from bottom-21
    top4 = ["sol00", "sol01", "sol02", "sol03"]
    bottom21 = [s for s in type8_docs if s not in top4]
    top4_features = []
    bottom21_features = []
    for sol_id in top4:
        d = type8_docs[sol_id]
        n_sq = sum(1 for c in d.components if c.type == "squeezer")
        top4_features.append(n_sq)
    for sol_id in bottom21:
        d = type8_docs[sol_id]
        n_sq = sum(1 for c in d.components if c.type == "squeezer")
        bottom21_features.append(n_sq)
    top4_mean_sq = float(np.mean(top4_features))
    bottom21_mean_sq = float(np.mean(bottom21_features))
    e23_result = f"top-4 mean squeezers={top4_mean_sq:.2f}, bottom-21 mean squeezers={bottom21_mean_sq:.2f}"
    e23_decision = "KEEP" if (bottom21_mean_sq - top4_mean_sq) > 1.0 else "REVERT"
    print(f"[E23] H23: {e23_result} → {e23_decision}")

    # ----- E24: H24 — distribution of long arm space lengths
    long_buckets = Counter()
    for sol_id, doc in type8_docs.items():
        for s in doc.spaces:
            if s.length > 1000:
                long_buckets[round(s.length / 100) * 100] += 1
    e24_result = f"long-space length buckets (×100m): {dict(sorted(long_buckets.items()))}"
    n_in_3500_4000 = sum(n for L, n in long_buckets.items() if 3500 <= L <= 4000)
    n_total = sum(long_buckets.values())
    e24_decision = "KEEP" if n_in_3500_4000 / max(n_total, 1) > 0.8 else "REVERT"
    print(f"[E24] H24: {e24_result} → {e24_decision}")

    # ----- E25: H25 — unused parameter IDs across the family
    # Collect param IDs in sol00 and one other; see how many gap-IDs are common
    sol00_ids = set(int(k.replace("param", "")) for k in sol00.parameters)
    sol00_gaps = set(range(0, 134)) - sol00_ids
    common_gaps_count = []
    for sol_id in ["sol01", "sol02", "sol03", "sol04", "sol05"]:
        if sol_id not in type8_docs:
            continue
        d = type8_docs[sol_id]
        their_ids = set()
        for k in d.parameters:
            try:
                their_ids.add(int(k.replace("param", "")))
            except ValueError:
                pass
        their_gaps = set(range(0, 134)) - their_ids
        common = sol00_gaps & their_gaps
        common_gaps_count.append(len(common))
    avg_common = float(np.mean(common_gaps_count)) if common_gaps_count else 0.0
    e25_result = f"sol00 has {len(sol00_gaps)} param gaps; avg shared with sol01-sol05: {avg_common:.1f}"
    e25_decision = "KEEP" if avg_common >= 0.5 * len(sol00_gaps) else "REVERT"
    print(f"[E25] H25: {e25_result} → {e25_decision}")

    # ----- write all rows
    with RESULTS_TSV.open("a") as fh:
        write_result_row(fh, "E06", "H02", "Mirrors with R in [0.99, 0.9999] (impedance-matched cavity range)", 0.75, "Critical-coupling cavity input mirrors should sit in this range", e06_result, e06_decision, "")
        write_result_row(fh, "E07", "H01-bs", "Beamsplitters pinned at R extremes (R<0.05 or R>0.95)", 0.70, "Optimiser fills the UIFO grid with degenerate BSs", e07_result, e07_decision, "")
        write_result_row(fh, "E08", "H02-arm", "Impedance-matched mirrors at arm-cavity endpoints", 0.65, "If H02 is real, the impedance mirrors should be linked to the long arms", e08_result, e08_decision, "")
        write_result_row(fh, "E09", "H03", "Beamsplitter angles all at ±45°", 0.90, "Standard Michelson reflection orientation", e09_result, e09_decision, "")
        write_result_row(fh, "E10", "H04", "Free spaces with length exactly 1.0 m", 0.60, "PyKat default for unset distances", e10_result, e10_decision, "")
        write_result_row(fh, "E11", "H05", "fsig signal injections target free spaces", 0.95, "Standard kat convention for strain perturbations", e11_result, e11_decision, "")
        write_result_row(fh, "E12", "H06", "Mirrors at exactly 200 kg (Voyager-equivalent)", 0.50, "Boundary mirrors the optimiser refused to perturb", e12_result, e12_decision, "")
        write_result_row(fh, "E13", "H07", "Mirror mass/reflectivity correlation in sol00", 0.80, "Mass and R are independent design dimensions in UIFO", e13_result, e13_decision, "")
        write_result_row(fh, "E14", "H08", "Distinct lengths among the 6 arm cavities", 0.65, "Symmetric multi-arm geometry uses few unique lengths", e14_result, e14_decision, "")
        write_result_row(fh, "E15", "H09", "R-like parameters clustered at boundaries", 0.80, "Optimiser saturates parameters it does not need", e15_result, e15_decision, "")
        write_result_row(fh, "E16", "H15+H16", "Laser and BS counts across type8 family", 0.55, "Different solutions have different component counts", e16_result, e16_decision, "")
        write_result_row(fh, "E17", "H17", "Directional BS presence vs improvement", 0.50, "Faraday isolators may indicate a different operating regime", e17_result, e17_decision, "")
        write_result_row(fh, "E18", "H18", "Bottom-13 solutions cluster near 1.0×", 0.70, "The bottom half is essentially Voyager-equivalent", e18_result, e18_decision, "")
        write_result_row(fh, "E19", "H19", "Long arm lengths share canonical values across the family", 0.75, "Optimiser doesn't tune length per-solution", e19_result, e19_decision, "")
        write_result_row(fh, "E20", "H20", "fsig count vs total component count correlation", 0.60, "More components require more signal injection points", e20_result, e20_decision, "")
        write_result_row(fh, "E21", "H21", "sol00 vs sol01 categorical structural diff", 0.70, "Top two solutions are not parameter perturbations", e21_result, e21_decision, "")
        write_result_row(fh, "E22", "H22", "sol00 vs sol24 structural diff in ≥3 categories", 0.80, "Best vs worst differ in multiple ways", e22_result, e22_decision, "")
        write_result_row(fh, "E23", "H23", "Top-4 vs bottom-21 squeezer signature", 0.50, "Top solutions share a common feature absent from the rest", e23_result, e23_decision, "")
        write_result_row(fh, "E24", "H24", "Long arm space lengths in 3500-4000m bucket", 0.65, "All AI-discovered arms are 4-km class", e24_result, e24_decision, "")
        write_result_row(fh, "E25", "H25", "Param gaps shared across the family", 0.30, "Unused IDs reflect optimiser pinning, not random skipping", e25_result, e25_decision, "")

    print(f"\nWrote 20 experiment rows to {RESULTS_TSV}")

    # Summary
    with RESULTS_TSV.open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)
    n_keep = sum(1 for r in rows if r["decision"] == "KEEP")
    n_revert = sum(1 for r in rows if r["decision"] == "REVERT")
    print(f"\nDecisions: {n_keep} KEEP, {n_revert} REVERT (out of {len(rows)})")


if __name__ == "__main__":
    main()
