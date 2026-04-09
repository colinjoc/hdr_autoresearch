"""
type8_detector_survey.py — is the phantom-MDet1 pattern family-wide?

In sol00, the balanced homodyne `qhd` reads AtPD1 − AtPD2, but AtPD1 is
only connected to a mirror (MDet1) whose back port is never wired to any
free space. So AtPD1 receives no light from the interferometer — the
balanced homodyne reduces to a single-port readout on AtPD2.

This script scans all 25 type8 solutions and asks: for each solution,
how many MDetX mirrors are "phantom" (back port not referenced by any
space)? And how many are "real"?
"""
from __future__ import annotations

from pathlib import Path
from collections import defaultdict

from kat_parser import parse_kat


PROJECT_ROOT = Path(__file__).resolve().parent
TYPE8_DIR = PROJECT_ROOT / "GWDetectorZoo/solutions/type8"


def analyse(doc):
    """Return (n_mdet_mirrors, n_phantom, n_real, details)"""
    # Collect all port-name strings that appear in spaces (either side).
    wired_ports = set()
    for sp in doc.spaces:
        wired_ports.add(sp.node_a)
        wired_ports.add(sp.node_b)

    n_mdet = 0
    phantom = []
    real = []
    for c in doc.components:
        if c.type != "mirror" or not c.name.startswith("MDet"):
            continue
        n_mdet += 1
        # A "phantom" MDet has its non-laser-side port orphaned.
        # The port naming convention is: port[0]=nMDetX_laser, port[1]=nMBX_0_dSetup.
        side_ports_wired = [p in wired_ports for p in c.ports]
        both_wired = all(side_ports_wired)
        # Count as phantom if the back port (second) is not wired.
        if len(c.ports) >= 2 and c.ports[1] not in wired_ports:
            phantom.append(c.name)
        else:
            real.append(c.name)
    return n_mdet, len(phantom), len(real), (phantom, real)


def main():
    sol_dirs = sorted(d for d in TYPE8_DIR.iterdir() if d.is_dir() and d.name.startswith("sol"))
    print(f"Scanning {len(sol_dirs)} type8 solutions for phantom MDet mirrors...\n")
    print(f"{'sol':6s}  {'n_mdet':>6s}  {'phantom':>8s}  {'real':>6s}  details")
    phantom_count = 0
    for d in sol_dirs:
        kat_files = list(d.glob("CFGS_8_*.txt"))
        if not kat_files:
            continue
        doc = parse_kat(kat_files[0].read_text())
        n_mdet, n_phantom, n_real, (ph, rl) = analyse(doc)
        if n_phantom > 0:
            phantom_count += 1
        print(f"{d.name:6s}  {n_mdet:>6d}  {n_phantom:>8d}  {n_real:>6d}  phantom={ph} real={rl}")
    print(f"\nSolutions with at least 1 phantom MDet: {phantom_count}/{len(sol_dirs)}")


if __name__ == "__main__":
    main()
