#!/usr/bin/env python3
"""
Phase B discovery script for IE Housing Pipeline E2E.

Outputs:
  discoveries/pipeline_yield_by_stratum.csv
  discoveries/permissions_needed_for_hfa.csv

These are produced by analysis.py; this script re-runs the discovery
outputs from cached results for reproducibility.
"""
import subprocess, sys, pathlib

PROJECT = pathlib.Path(__file__).resolve().parent

if __name__ == "__main__":
    # Phase B is integrated into analysis.py; run it to produce discoveries
    result = subprocess.run(
        [sys.executable, str(PROJECT / "analysis.py")],
        capture_output=True, text=True, timeout=600,
        cwd=str(PROJECT),
    )
    if result.returncode != 0:
        print("ERROR:", result.stderr[-2000:])
        sys.exit(1)

    # Verify outputs
    d1 = PROJECT / "discoveries" / "pipeline_yield_by_stratum.csv"
    d2 = PROJECT / "discoveries" / "permissions_needed_for_hfa.csv"

    import pandas as pd
    df1 = pd.read_csv(d1)
    df2 = pd.read_csv(d2)
    print(f"pipeline_yield_by_stratum.csv: {len(df1)} rows")
    print(f"permissions_needed_for_hfa.csv: {len(df2)} rows")
    print("\nSample yield strata:")
    print(df1.head(10).to_string(index=False))
    print("\nHFA scenarios:")
    print(df2.to_string(index=False))
