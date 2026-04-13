"""Bulk-download GH Archive hourly files in an INTERLEAVED order so that
partial completion still covers all target days.

Plan: 6 hours × 6 days = 36 files ≈ 4.5 GB.
Prior:   2024-04-01, 03, 05 (hours 12,14,16,18,20,22)
Forward: 2025-04-01, 03, 05 (same hours)

Interleaving guarantees that after the first 6 files completed, we have 1 hour
from each target day — enough for a minimum-viable baseline.
"""

from __future__ import annotations

import concurrent.futures as cf
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data_loaders import download_hour

CACHE = Path(__file__).parent / "data" / "raw"

PRIOR_DATES = ["2024-04-01", "2024-04-03", "2024-04-05"]
FORWARD_DATES = ["2025-04-01", "2025-04-03", "2025-04-05"]
HOURS = [12, 14, 16, 18, 20, 22]


def all_hours_interleaved() -> list[datetime]:
    """Interleave: for hour h, yield all 6 dates at that hour; then next hour; …"""
    out = []
    for h in HOURS:
        for day in PRIOR_DATES + FORWARD_DATES:
            d = datetime.strptime(day, "%Y-%m-%d").replace(hour=h)
            out.append(d)
    return out


def main():
    hours = all_hours_interleaved()
    print(f"Plan: download {len(hours)} hourly files to {CACHE} (interleaved)", flush=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    done = 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = []
        for h in hours:
            futs.append(ex.submit(download_hour, h, CACHE))
        for f in cf.as_completed(futs):
            try:
                p = f.result()
                done += 1
                size_mb = p.stat().st_size / 1e6
                elapsed = time.time() - t0
                print(f"  [{done:2d}/{len(hours)}]  {p.name}  {size_mb:.0f} MB  t+{elapsed/60:.1f}m",
                      flush=True)
            except Exception as e:
                print(f"  FAIL: {e}", flush=True)
    print(f"Done: {done}/{len(hours)} in {(time.time()-t0)/60:.1f}m", flush=True)


if __name__ == "__main__":
    main()
