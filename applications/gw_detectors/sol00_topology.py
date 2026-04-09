"""
sol00_topology.py — Path 1 exploration driver.

Builds the optical graph for sol00, prints:
  - Number of connected components
  - Which components are in the active (laser-reachable) subgraph
  - Which 6 arm-cavity spaces map to which component endpoints
  - The mirror R / mass profile on the active subgraph vs the dead subgraph
  - Candidate compound-cavity mirror pairs (moderate-R mirrors in series)

Outputs:
  results/sol00_active_nodes.tsv  one row per component, with active flag
  results/sol00_arm_cavity_map.tsv  one row per arm-cavity space
  results/sol00_compound_pairs.tsv  one row per candidate compound-cavity pair
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from kat_parser import parse_kat
from light_path_trace import (
    build_optical_graph,
    active_components,
    arm_cavity_endpoints,
    series_mirror_pairs_on_active_path,
    is_arm_cavity_length,
    _resolve_R,
)


PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"
SOL00_KAT = PROJECT_ROOT / "GWDetectorZoo/solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    doc = parse_kat(SOL00_KAT.read_text())
    graph = build_optical_graph(doc)

    print("=" * 72)
    print("sol00 light-path topology")
    print("=" * 72)
    print(f"nodes: {graph.num_nodes()}   edges: {graph.num_edges()}")

    # ----- connected components -----
    seen_cc_ids = {}
    cc_members = defaultdict(list)
    cc_id = 0
    for name in graph.nodes:
        if name in seen_cc_ids:
            continue
        cc = graph.connected_component(name)
        for m in cc:
            seen_cc_ids[m] = cc_id
        cc_members[cc_id] = sorted(cc)
        cc_id += 1

    print(f"\nTotal connected components: {len(cc_members)}")

    # How many components have a laser
    laser_names = {c.name for c in doc.components if c.type == "laser"}
    laser_cc_ids = {seen_cc_ids[l] for l in laser_names if l in seen_cc_ids}
    active_set = active_components(graph)

    cc_with_laser = 0
    for cid, members in cc_members.items():
        type_counts = Counter(graph.nodes[m]["type"] for m in members)
        has_laser = cid in laser_cc_ids
        if has_laser:
            cc_with_laser += 1
        print(f"  CC#{cid:2d} size={len(members):3d}  laser={'*' if has_laser else ' '}  {dict(type_counts)}")

    print(f"\nConnected components containing a laser: {cc_with_laser}")
    print(f"Components in active (laser-reachable) subgraph: {len(active_set)} / {graph.num_nodes()}")

    # ----- mirror active vs dead -----
    active_mirrors = [n for n in active_set if graph.nodes[n]["type"] == "mirror"]
    dead_mirrors = [
        n for n, a in graph.nodes.items()
        if a["type"] == "mirror" and n not in active_set
    ]
    print(f"\nActive mirrors: {len(active_mirrors)}")
    print(f"Dead (isolated) mirrors: {len(dead_mirrors)}")

    # R distribution on active vs dead
    def classify(R):
        if R is None:
            return "NaN"
        if R < 0.001: return "R<0.001"
        if R < 0.01:  return "R<0.01"
        if R < 0.1:   return "R<0.1"
        if R < 0.4:   return "R<0.4"
        if R < 0.6:   return "R<0.6"
        if R < 0.9:   return "R<0.9"
        if R < 0.99:  return "R<0.99"
        if R < 0.999: return "R<0.999"
        return "R>=0.999"

    active_bins = Counter(classify(_resolve_R(doc, n, graph)) for n in active_mirrors)
    dead_bins   = Counter(classify(_resolve_R(doc, n, graph)) for n in dead_mirrors)

    print("\n  R range     active  dead")
    for k in ["R<0.001","R<0.01","R<0.1","R<0.4","R<0.6","R<0.9","R<0.99","R<0.999","R>=0.999"]:
        print(f"  {k:12s}  {active_bins.get(k,0):5d}  {dead_bins.get(k,0):5d}")

    # mass stats
    def mass_of(n):
        p = graph.nodes[n]["props"]
        m = p.get("mass")
        if m is None or isinstance(m, str):
            return None
        try:
            return float(m)
        except (TypeError, ValueError):
            return None

    active_masses = [mass_of(n) for n in active_mirrors if mass_of(n) is not None]
    dead_masses   = [mass_of(n) for n in dead_mirrors   if mass_of(n) is not None]
    if active_masses:
        print(f"\nActive mirror mass:  median={np.median(active_masses):7.2f}  "
              f"range={min(active_masses):7.2f}..{max(active_masses):7.2f}  "
              f"n={len(active_masses)}")
    if dead_masses:
        print(f"Dead   mirror mass:  median={np.median(dead_masses):7.2f}  "
              f"range={min(dead_masses):7.2f}..{max(dead_masses):7.2f}  "
              f"n={len(dead_masses)}")

    # ----- arm cavity endpoints -----
    print("\nArm-cavity (L>1km) endpoints:")
    endpoints = arm_cavity_endpoints(doc, graph)
    for sp_name, (ca, cb, L) in sorted(endpoints.items(), key=lambda kv: -kv[1][2]):
        ra = _resolve_R(doc, ca, graph) if ca else None
        rb = _resolve_R(doc, cb, graph) if cb else None
        ma = mass_of(ca) if ca else None
        mb = mass_of(cb) if cb else None
        active_a = "ACT" if ca in active_set else "DEAD"
        active_b = "ACT" if cb in active_set else "DEAD"
        ta = graph.nodes[ca]["type"][:8] if ca in graph.nodes else "?"
        tb = graph.nodes[cb]["type"][:8] if cb in graph.nodes else "?"
        def fR(x): return f"{x:.4f}" if x is not None else "   ?  "
        def fM(x): return f"{x:7.2f}" if x is not None else "     ? "
        print(f"  {sp_name:10s}  L={L:8.2f}m  {ca:12s}[{ta}|{active_a}] R={fR(ra)} m={fM(ma)}  <->  {cb:12s}[{tb}|{active_b}] R={fR(rb)} m={fM(mb)}")

    # ----- active subgraph edge walk from each laser -----
    print("\nWalk from each laser (BFS level 0..3):")
    for L in sorted(laser_names):
        print(f"\nLaser {L}:")
        levels = {L: 0}
        queue = [L]
        max_depth = 6
        while queue:
            cur = queue.pop(0)
            if levels[cur] >= max_depth:
                continue
            for nbr, edata in graph.neighbours(cur):
                if nbr not in levels:
                    levels[nbr] = levels[cur] + 1
                    queue.append(nbr)
        by_depth = defaultdict(list)
        for k, v in levels.items():
            by_depth[v].append((k, graph.nodes[k]["type"]))
        for d in sorted(by_depth.keys()):
            if d > 4:
                break
            items = by_depth[d]
            # show compactly
            items_s = ", ".join(f"{n}({t[:3]})" for n, t in items[:8])
            more = "..." if len(items) > 8 else ""
            print(f"  depth {d}: {len(items):3d} nodes   {items_s}{more}")

    # ----- compound cavity candidates -----
    print("\nCompound-cavity candidate pairs (both mirrors in [0.05, 0.95]):")
    pairs = series_mirror_pairs_on_active_path(doc, graph, r_min=0.05, r_max=0.95)
    for m1, m2, L in pairs:
        R1 = _resolve_R(doc, m1, graph)
        R2 = _resolve_R(doc, m2, graph)
        # effective finesse of a 2-mirror cavity
        # F = pi * (r1*r2)^(1/2) / (1 - r1*r2), where r = sqrt(R)
        r1 = R1 ** 0.5
        r2 = R2 ** 0.5
        F = 3.14159265 * (r1 * r2) ** 0.5 / (1 - r1 * r2) if (r1 * r2) < 1 else float("inf")
        print(f"  {m1:12s} (R={R1:.4f}) <-> {m2:12s} (R={R2:.4f})  L={L:8.2f} m  finesse≈{F:7.1f}")

    # ----- write outputs -----
    with (RESULTS_DIR / "sol00_active_nodes.tsv").open("w") as fh:
        fh.write("name\ttype\tactive\tR\tmass\n")
        for n, a in sorted(graph.nodes.items()):
            R = _resolve_R(doc, n, graph)
            m = mass_of(n)
            fh.write(f"{n}\t{a['type']}\t{int(n in active_set)}\t"
                     f"{'' if R is None else f'{R:.6e}'}\t"
                     f"{'' if m is None else f'{m:.6e}'}\n")

    with (RESULTS_DIR / "sol00_arm_cavity_map.tsv").open("w") as fh:
        fh.write("space\tlength_m\tcomp_a\ttype_a\tR_a\tmass_a\tcomp_b\ttype_b\tR_b\tmass_b\tactive_a\tactive_b\n")
        for sp, (ca, cb, L) in sorted(endpoints.items()):
            ra = _resolve_R(doc, ca, graph) if ca else None
            rb = _resolve_R(doc, cb, graph) if cb else None
            ma = mass_of(ca) if ca else None
            mb = mass_of(cb) if cb else None
            ta = graph.nodes[ca]["type"] if ca in graph.nodes else ""
            tb = graph.nodes[cb]["type"] if cb in graph.nodes else ""
            fh.write(f"{sp}\t{L:.4f}\t{ca or ''}\t{ta}\t"
                     f"{'' if ra is None else f'{ra:.6e}'}\t{'' if ma is None else f'{ma:.4e}'}\t"
                     f"{cb or ''}\t{tb}\t"
                     f"{'' if rb is None else f'{rb:.6e}'}\t{'' if mb is None else f'{mb:.4e}'}\t"
                     f"{int(ca in active_set) if ca else 0}\t{int(cb in active_set) if cb else 0}\n")

    with (RESULTS_DIR / "sol00_compound_pairs.tsv").open("w") as fh:
        fh.write("mirror_a\tR_a\tmirror_b\tR_b\tlength_m\tfinesse_est\n")
        for m1, m2, L in pairs:
            R1 = _resolve_R(doc, m1, graph)
            R2 = _resolve_R(doc, m2, graph)
            r1 = R1 ** 0.5
            r2 = R2 ** 0.5
            F = 3.14159265 * (r1 * r2) ** 0.5 / (1 - r1 * r2) if (r1 * r2) < 1 else float("inf")
            fh.write(f"{m1}\t{R1:.6e}\t{m2}\t{R2:.6e}\t{L:.4f}\t{F:.2f}\n")

    print("\nWrote results/sol00_active_nodes.tsv, results/sol00_arm_cavity_map.tsv, results/sol00_compound_pairs.tsv")


if __name__ == "__main__":
    main()
