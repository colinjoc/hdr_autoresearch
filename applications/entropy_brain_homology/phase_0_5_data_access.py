"""Phase 0.5 Allen Neuropixels data-access smoke test — runnable entrypoint.

Per `~/.claude/projects/-home-col/memory/feedback_verify_data_access_before_phase_0`:
this must succeed before Phase 1 pipeline code is written.

Uses the DANDI route (dandiset 000021 = Allen Brain Observatory 1.1 Neuropixels)
rather than allensdk, which has a Python-3.12 compat issue.

Usage:
    ./venv/bin/python phase_0_5_data_access.py [--download]
    (default: metadata only; --download streams ~2 GB and is slower)
"""

from __future__ import annotations

import argparse
import sys
import time

ALLEN_VISUAL_CODING_DANDISET = "000021"


def smoke_test(download: bool = False) -> int:
    print("=== Phase 0.5 Allen Neuropixels data-access smoke test (DANDI) ===\n")

    print("[1/4] importing dandi + pynwb...", end=" ", flush=True)
    t0 = time.time()
    try:
        from dandi.dandiapi import DandiAPIClient
        import pynwb  # noqa: F401
    except ImportError as exc:
        print(f"FAIL\n  {exc}")
        print("\nFix: ./venv/bin/pip install dandi pynwb")
        return 1
    print(f"ok ({time.time() - t0:.1f}s)")

    print(f"[2/4] resolving dandiset {ALLEN_VISUAL_CODING_DANDISET}...",
          end=" ", flush=True)
    t0 = time.time()
    try:
        with DandiAPIClient() as client:
            dandiset = client.get_dandiset(
                ALLEN_VISUAL_CODING_DANDISET, "draft"
            )
            meta = dandiset.get_raw_metadata()
            name = meta.get("name", "?")
    except Exception as exc:
        print(f"FAIL\n  {exc}")
        print("\nFix: check network or DANDI API at https://api.dandiarchive.org")
        return 2
    print(f"ok ({time.time() - t0:.1f}s)")
    print(f"      dandiset name: {name}")

    print("[3/4] listing NWB assets...", end=" ", flush=True)
    t0 = time.time()
    with DandiAPIClient() as client:
        dandiset = client.get_dandiset(
            ALLEN_VISUAL_CODING_DANDISET, "draft"
        )
        assets = [a for a in dandiset.get_assets() if a.path.endswith(".nwb")]
    print(f"ok ({len(assets)} sessions, {time.time() - t0:.1f}s)")
    total_gb = sum(a.size for a in assets) / 1e9
    sizes_gb = sorted(a.size / 1e9 for a in assets)
    print(f"      total {total_gb:.1f} GB; "
          f"smallest {sizes_gb[0]:.1f} GB; "
          f"median {sizes_gb[len(sizes_gb) // 2]:.1f} GB")

    if not download:
        print("[4/4] skipping NWB stream (pass --download to enable).")
        print("\nGate PASSED (metadata only). Run with --download before Phase 1.")
        return 0

    print("[4/4] streaming smallest NWB session via remfile+pynwb "
          "(opens remote HDF5 without full download)...", end=" ", flush=True)
    t0 = time.time()
    try:
        import h5py
        import remfile
        with DandiAPIClient() as client:
            dandiset = client.get_dandiset(
                ALLEN_VISUAL_CODING_DANDISET, "draft"
            )
            nwb_assets = sorted(
                (a for a in dandiset.get_assets() if a.path.endswith(".nwb")),
                key=lambda a: a.size,
            )
            smallest = nwb_assets[0]
            url = smallest.get_content_url(
                follow_redirects=1, strip_query=False
            )

        file = remfile.File(url)
        with h5py.File(file, "r") as h5:
            with pynwb.NWBHDF5IO(file=h5, load_namespaces=True) as io:
                nwb = io.read()
                units = nwb.units
                n_units = len(units["spike_times"][:])
    except Exception as exc:
        print(f"FAIL\n  {exc}")
        return 3
    print(f"ok ({n_units} sorted units, {time.time() - t0:.1f}s)")
    print(f"      session: {smallest.path} ({smallest.size / 1e9:.1f} GB total)")

    print("\nGate PASSED — Phase 0.5 data access verified for Allen Neuropixels.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--download",
        action="store_true",
        help="Stream one NWB session to confirm spike-times are readable.",
    )
    args = parser.parse_args()
    sys.exit(smoke_test(download=args.download))
