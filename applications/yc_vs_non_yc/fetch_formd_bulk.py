"""Download SEC DERA Form D quarterly ZIPs, 2014Q1 → 2024Q4.

Rate-limited (≥0.15s between requests; SEC's 10 req/s cap is very generous
but we stay well under to be polite). Skips files already on disk.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
OUT = HERE / "data" / "sec_formd"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "HDR research col@example.com"}
URL = "https://www.sec.gov/files/structureddata/data/form-d-data-sets/{y}q{q}_d.zip"


def main(start_year: int = 2014, end_year: int = 2024) -> int:
    for y in range(start_year, end_year + 1):
        for q in (1, 2, 3, 4):
            name = f"{y}q{q}_d.zip"
            dst = OUT / name
            if dst.exists() and dst.stat().st_size > 100_000:
                continue
            url = URL.format(y=y, q=q)
            print(f"GET {url}", flush=True)
            r = requests.get(url, headers=HEADERS, timeout=60)
            if r.status_code != 200:
                print(f"  -> {r.status_code}; skip", flush=True)
                continue
            dst.write_bytes(r.content)
            print(f"  saved {len(r.content)//1024} KB", flush=True)
            time.sleep(0.2)
    print("done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
