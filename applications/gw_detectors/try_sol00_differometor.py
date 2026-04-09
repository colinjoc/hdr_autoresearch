"""
try_sol00_differometor.py — attempt to simulate sol00 in Differometor.

This script converts sol00 to a Differometor Setup and tries to run df.run()
over a frequency sweep, then compares the output sensitivity to the Zoo's
canonical strain.csv in the 800-3000 Hz band.

It is expected to fail or produce incorrect results at first pass; the aim is
to see the specific failure mode and iterate.
"""
from __future__ import annotations

import csv
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import jax.numpy as jnp
import differometor as df

from kat_parser import parse_kat
from kat_to_differometor import kat_to_differometor


PROJECT_ROOT = Path(__file__).resolve().parent
SOL00_KAT = PROJECT_ROOT / "GWDetectorZoo/solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"
SOL00_STRAIN = PROJECT_ROOT / "GWDetectorZoo/solutions/type8/sol00/strain.csv"
POST_MERGER_BAND = (800.0, 3000.0)


def read_strain_csv(path: Path):
    rows = []
    with path.open() as fh:
        reader = csv.reader(fh)
        header = next(reader)
        for row in reader:
            rows.append([float(x) for x in row])
    arr = np.array(rows)
    return arr[:, 0], {h: arr[:, i] for i, h in enumerate(header)}


def main():
    doc = parse_kat(SOL00_KAT.read_text())
    print(f"Parsed sol00: {len(doc.components)} components, {len(doc.spaces)} spaces, "
          f"{len(doc.signal_injections)} fsig injections")

    S, meta = kat_to_differometor(doc)
    print(f"Converted to Differometor setup:")
    print(f"  nodes placed:         {sum(1 for _ in S.nodes(data=False))}")
    print(f"  space edges placed:   {meta['n_space_edges_placed']}")
    print(f"  orphan spaces skipped:{meta['n_orphan_spaces']}")
    print(f"  signal nodes placed:  {meta['n_signal_nodes']}")
    print(f"  detectors attached:   {meta['n_detectors_attached']}")

    # Count by type
    from collections import Counter
    type_counts = Counter(data["component"] for _n, data in S.nodes)
    print(f"  component counts:     {dict(type_counts)}")

    # Show the first few nodes and edges
    print("\nFirst 10 nodes in the setup:")
    for i, (name, data) in enumerate(S.nodes):
        if i >= 10:
            break
        print(f"  {name:20s}  {data['component']}")

    print("\nFirst 10 edges in the setup:")
    for i, (src, tgt, edata) in enumerate(S.edges(data=True)):
        if i >= 10:
            break
        print(f"  {src:20s} -> {tgt:20s}  length={edata['properties'].get('length', '?')}")

    # Try a single-frequency run first to check the setup is simulable.
    print("\nAttempting df.run() with frequency sweep in post-merger band...")
    frequencies = jnp.logspace(jnp.log10(POST_MERGER_BAND[0]),
                                jnp.log10(POST_MERGER_BAND[1]), 20)
    try:
        carrier, signal, noise, detector_ports, *rest = df.run(
            S, [("f", "frequency")], frequencies
        )
        print(f"  carrier shape: {carrier.shape}")
        print(f"  signal shape:  {signal.shape}")
        print(f"  noise shape:   {noise.shape}")
        print(f"  detector_ports: {detector_ports}")

        signals_det = df.signal_detector(carrier, signal)[detector_ports]
        # For sol00 there may be 1 or 2 detector ports depending on MDet1 phantom status
        if len(detector_ports) >= 2:
            balanced = signals_det[0] - signals_det[1]
        else:
            balanced = signals_det.squeeze()
        sensitivity = noise / jnp.abs(balanced)
        print(f"\nDifferometor-computed sensitivity in band:")
        print(f"  min:    {float(sensitivity.min()):.3e}")
        print(f"  max:    {float(sensitivity.max()):.3e}")
        print(f"  median: {float(jnp.median(sensitivity)):.3e}")

        # Compare to Zoo ground truth
        freqs_gt, cols = read_strain_csv(SOL00_STRAIN)
        mask = (freqs_gt >= POST_MERGER_BAND[0]) & (freqs_gt <= POST_MERGER_BAND[1])
        gt_best = cols["strain_best"][mask]
        print(f"\nZoo canonical sol00 strain_best in band:")
        print(f"  min:    {float(gt_best.min()):.3e}")
        print(f"  max:    {float(gt_best.max()):.3e}")
        print(f"  median: {float(np.median(gt_best)):.3e}")

        ratio = float(jnp.median(sensitivity)) / float(np.median(gt_best))
        print(f"\nMedian ratio (differometor / ground truth): {ratio:.3e}")
        if 0.1 < ratio < 10.0:
            print("  -> Within an order of magnitude. Converter is viable.")
        else:
            print("  -> Disagreement > 10x. Converter needs more work.")

    except Exception as e:
        print(f"\ndf.run() FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
