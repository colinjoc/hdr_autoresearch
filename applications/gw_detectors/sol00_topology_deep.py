"""
sol00_topology_deep.py — deeper dive into sol00's active topology.

Follow-ups to sol00_topology.py. Focuses on:
  1. The path from each laser to each photodetector
  2. The neighbourhood of the 2 real beamsplitters (B1_3, B3_1) and the Faraday
  3. The path through the 3 "real" arm cavities (mRL_3_3 and the trapped mUD_1_1)
  4. The role of the 200 kg masses (which specific mirrors?)
  5. Whether the 3 lasers beat against each other (same or different frequency?)
"""
from __future__ import annotations

from pathlib import Path
from collections import defaultdict, deque

from kat_parser import parse_kat
from light_path_trace import build_optical_graph, _resolve_R, active_components


PROJECT_ROOT = Path(__file__).resolve().parent
SOL00_KAT = PROJECT_ROOT / "GWDetectorZoo/solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"


def shortest_path(graph, source, target):
    """BFS shortest path between two named components."""
    if source not in graph.nodes or target not in graph.nodes:
        return None
    parents = {source: None}
    queue = deque([source])
    while queue:
        cur = queue.popleft()
        if cur == target:
            path = [cur]
            while parents[path[-1]] is not None:
                path.append(parents[path[-1]])
            return list(reversed(path))
        for nbr, _ in graph.neighbours(cur):
            if nbr not in parents:
                parents[nbr] = cur
                queue.append(nbr)
    return None


def path_with_lengths(graph, path):
    """Given a path of component names, return a string 'A --L1m-- B --L2m-- C'."""
    if path is None:
        return "(no path)"
    out = [path[0]]
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        # find edge between a and b
        L = None
        for nbr, data in graph.neighbours(a):
            if nbr == b:
                L = data["length"]
                break
        out.append(f"--[{L:.1f}m]--")
        out.append(b)
    return " ".join(out)


def main():
    doc = parse_kat(SOL00_KAT.read_text())
    graph = build_optical_graph(doc)

    print("=" * 72)
    print("sol00 deep topology: laser -> detector paths")
    print("=" * 72)

    lasers = [c.name for c in doc.components if c.type == "laser"]
    detectors = [c.name for c in doc.components
                 if c.type in ("ac_photodetector", "dc_photodetector",
                               "homodyne_detector", "quantum_noise_detector")]
    # The real readout is the qhd which is balanced homodyne between AtPD1 and AtPD2.
    # The AtPD1/AtPD2 nodes are on mirrors MDet1/MDet2.
    print(f"Lasers: {lasers}")
    print(f"Detectors: {detectors}")

    # Laser powers
    print("\nLaser powers / frequencies:")
    for c in doc.components:
        if c.type == "laser":
            p = graph.nodes[c.name]["props"]
            print(f"  {c.name}:  power={p.get('power')}  freq={p.get('frequency')}  phase={p.get('phase')}")

    # ----- Path from each laser to each "detector mirror" MDet1, MDet2 -----
    print("\nLaser -> MDet1 and MDet2 paths:")
    for L in lasers:
        for Det in ("MDet1", "MDet2"):
            path = shortest_path(graph, L, Det)
            hops = len(path) - 1 if path else -1
            print(f"\n  {L} -> {Det}  ({hops} hops)")
            print(f"    {path_with_lengths(graph, path)}")

    # ----- The 200 kg mirrors -----
    print("\n200 kg mirrors and their connectivity (neighbourhood):")
    for c in doc.components:
        if c.type != "mirror":
            continue
        mass = graph.nodes[c.name]["props"].get("mass")
        if mass is None or isinstance(mass, str):
            continue
        try:
            m = float(mass)
        except (TypeError, ValueError):
            continue
        if abs(m - 200.0) < 0.001:
            R = _resolve_R(doc, c.name, graph)
            nbrs = graph.neighbours(c.name)
            print(f"  {c.name}  R={R:.6f}  mass=200.0 kg")
            for nbr, data in nbrs:
                nR = _resolve_R(doc, nbr, graph)
                nM = graph.nodes[nbr]["props"].get("mass", "?")
                nT = graph.nodes[nbr]["type"]
                print(f"    -- {data['name']:10s} ({data['length']:8.1f}m) --> "
                      f"{nbr:12s}  type={nT:8s}  R={'?' if nR is None else f'{nR:.4f}'}  m={nM}")

    # ----- The two real beamsplitters B1_3 and B3_1, full neighbourhood -----
    print("\nReal beamsplitters' neighbourhoods:")
    for bs_name in ("B1_3", "B3_1", "B4_4"):  # B4_4 is the Faraday
        if bs_name not in graph.nodes:
            continue
        t = graph.nodes[bs_name]["type"]
        R = graph.nodes[bs_name]["props"].get("reflectivity", "n/a")
        angle = graph.nodes[bs_name]["props"].get("angle", "n/a")
        print(f"\n  {bs_name}  type={t}  R={R}  angle={angle}")
        for nbr, data in graph.neighbours(bs_name):
            nT = graph.nodes[nbr]["type"]
            nR = _resolve_R(doc, nbr, graph)
            nM = graph.nodes[nbr]["props"].get("mass", None)
            nR_s = "?" if nR is None else f"{nR:.4f}"
            nM_s = "?" if nM is None or isinstance(nM, str) else f"{float(nM):6.2f}"
            print(f"    -- {data['name']:10s} ({data['length']:8.1f}m) --> "
                  f"{nbr:12s}  type={nT:8s}  R={nR_s}  m={nM_s}")

    # ----- Walk into the arm cavities: from mRL_3_3's two endpoints, what's next? -----
    print("\nExtended neighbourhood of arm cavity mRL_3_3 (3847m, R=0.52/0.50):")
    for n in ("MB3_3_r", "MB4_3_l"):
        print(f"\n  {n} neighbours:")
        for nbr, data in graph.neighbours(n):
            nT = graph.nodes[nbr]["type"]
            nR = _resolve_R(doc, nbr, graph)
            print(f"    -- {data['name']:10s} ({data['length']:8.1f}m) --> "
                  f"{nbr:12s}  type={nT:8s}  R={'?' if nR is None else f'{nR:.4f}'}")

    print("\nExtended neighbourhood of mUD_1_1 (3670m, R=1/R=1 trapped light):")
    for n in ("MB1_1_d", "MB1_2_u"):
        print(f"\n  {n} neighbours:")
        for nbr, data in graph.neighbours(n):
            nT = graph.nodes[nbr]["type"]
            nR = _resolve_R(doc, nbr, graph)
            print(f"    -- {data['name']:10s} ({data['length']:8.1f}m) --> "
                  f"{nbr:12s}  type={nT:8s}  R={'?' if nR is None else f'{nR:.4f}'}")

    print("\nExtended neighbourhood of mUD_3_1 (3670m, R=0/0.002 through-pass):")
    for n in ("MB3_1_d", "MB3_2_u"):
        print(f"\n  {n} neighbours:")
        for nbr, data in graph.neighbours(n):
            nT = graph.nodes[nbr]["type"]
            nR = _resolve_R(doc, nbr, graph)
            nM = graph.nodes[nbr]["props"].get("mass", None)
            nM_s = "?" if nM is None or isinstance(nM, str) else f"{float(nM):6.2f}"
            print(f"    -- {data['name']:10s} ({data['length']:8.1f}m) --> "
                  f"{nbr:12s}  type={nT:8s}  R={'?' if nR is None else f'{nR:.4f}'} m={nM_s}")


if __name__ == "__main__":
    main()
