"""UK gender pay gap 2017-2025 mandatory disclosure analysis.

Question: after nine years of mandatory reporting, has the median gender pay gap
actually narrowed? Are late filers different from on-time filers? Which employer
size classes have made progress?
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
CHARTS = HERE / "charts"
CHARTS.mkdir(exist_ok=True)
DISCOVERIES = HERE / "discoveries"
DISCOVERIES.mkdir(exist_ok=True)
RESULTS = HERE / "results.tsv"


def load_all():
    frames = []
    for f in sorted(RAW.glob("gpg_*.csv")):
        year = int(f.stem.split("_")[1])
        df = pd.read_csv(f, low_memory=False)
        df["reporting_year"] = year
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True, sort=False)
    return combined


def main():
    df = load_all()
    print(f"[load] {len(df)} employer-year rows; {df['reporting_year'].min()}-{df['reporting_year'].max()}")
    print("columns:", [c for c in df.columns[:20]])

    # Key metric: median hourly pay gap (DiffMedianHourlyPercent)
    gap_col = "DiffMedianHourlyPercent"
    mean_gap_col = "DiffMeanHourlyPercent"
    df[gap_col] = pd.to_numeric(df[gap_col], errors="coerce")
    df[mean_gap_col] = pd.to_numeric(df[mean_gap_col], errors="coerce")

    # Annual trend
    annual = df.groupby("reporting_year").agg(
        n_submissions=(gap_col, "size"),
        median_gap_median=(gap_col, "median"),
        mean_gap_median=(mean_gap_col, "median"),
        median_gap_mean=(gap_col, "mean"),
        late_count=("SubmittedAfterTheDeadline", lambda x: (x == True).sum()),
    ).reset_index()
    annual["late_pct"] = annual["late_count"] / annual["n_submissions"] * 100
    annual.to_csv(DISCOVERIES / "annual_trend.csv", index=False)
    print("\n=== annual trend ===")
    print(annual.to_string(index=False))

    # Persistence: how many employers in all 9 years?
    by_employer = df.groupby("EmployerName")["reporting_year"].nunique()
    persistent = (by_employer == 9).sum()
    once_only = (by_employer == 1).sum()
    print(f"\n=== persistence ===\nEmployers in all 9 years: {persistent}")
    print(f"Employers in only 1 year: {once_only}")
    print(f"Median #years: {int(by_employer.median())}")

    # Within-employer change for persistent employers
    # For employers in both 2017 and 2025, compute the change
    pairs = df[df["reporting_year"].isin([2017, 2025])][["EmployerName", "reporting_year", gap_col]]
    pairs = pairs.dropna().pivot_table(index="EmployerName", columns="reporting_year",
                                       values=gap_col, aggfunc="first")
    pairs = pairs.dropna()
    if 2017 in pairs.columns and 2025 in pairs.columns:
        pairs["delta_2025_minus_2017"] = pairs[2025] - pairs[2017]
        print(f"\n=== within-employer 2017 → 2025 (n={len(pairs)}) ===")
        print(f"median gap 2017: {pairs[2017].median():.2f}")
        print(f"median gap 2025: {pairs[2025].median():.2f}")
        print(f"median Δ (2025 − 2017): {pairs['delta_2025_minus_2017'].median():.2f} pp")
        print(f"share with Δ < 0 (gap narrowed): {(pairs['delta_2025_minus_2017'] < 0).mean() * 100:.1f}%")
        pairs.to_csv(DISCOVERIES / "within_employer_2017_vs_2025.csv")

    # Late vs on-time
    ont = df[df["SubmittedAfterTheDeadline"] == False][gap_col].dropna()
    late = df[df["SubmittedAfterTheDeadline"] == True][gap_col].dropna()
    print(f"\n=== late vs on-time ===")
    print(f"On-time filings: n={len(ont)}, median gap {ont.median():.2f}%")
    print(f"Late filings: n={len(late)}, median gap {late.median():.2f}%")

    # Employer size breakdown
    size_col = "EmployerSize"
    if size_col in df.columns:
        size_latest = df[df["reporting_year"] == df["reporting_year"].max()]
        by_size = size_latest.groupby(size_col)[gap_col].agg(["median", "size"]).reset_index()
        by_size = by_size.rename(columns={"size": "n"})
        by_size.to_csv(DISCOVERIES / "gap_by_employer_size_latest.csv", index=False)
        print(f"\n=== gap by employer size ({df['reporting_year'].max()}) ===")
        print(by_size.to_string(index=False))

    # Chart
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(annual["reporting_year"], annual["median_gap_median"], "o-", linewidth=1.3, color="purple", label="median of medians")
    axes[0].plot(annual["reporting_year"], annual["median_gap_mean"], "o--", linewidth=1, color="orange", label="mean of medians")
    axes[0].set_xlabel("reporting year"); axes[0].set_ylabel("median hourly pay gap (%)")
    axes[0].set_title("UK gender pay gap 2017-2025 — 9 years of mandatory reporting")
    axes[0].legend(fontsize=9); axes[0].grid(alpha=0.3)
    axes[0].axhline(0, color="black", linewidth=0.5)

    axes[1].bar(annual["reporting_year"], annual["late_pct"], color="maroon", alpha=0.7)
    axes[1].set_xlabel("reporting year"); axes[1].set_ylabel("% late submissions")
    axes[1].set_title("Share of employers filing after the deadline")
    axes[1].grid(alpha=0.3, axis="y")
    fig.tight_layout(); fig.savefig(CHARTS / "gpg_annual_trend.png", dpi=120); plt.close(fig)

    HEADER = ["experiment_id", "commit", "description", "metric", "value",
              "seed", "status", "notes"]
    rows = [
        {"experiment_id": "E00", "commit": "phase0.5",
         "description": "UK GPG 2017-2025 mandatory disclosure panel",
         "metric": "n_employer_year_obs", "value": len(df),
         "seed": 0, "status": "BASELINE",
         "notes": f"{df['EmployerName'].nunique()} unique employers"},
        {"experiment_id": "E01", "commit": "phase1",
         "description": "9-year median gender hourly pay gap trend",
         "metric": f"median_gap_2017_to_2025",
         "value": f"{annual[annual['reporting_year']==2017]['median_gap_median'].iloc[0]:.2f} → {annual[annual['reporting_year']==2025]['median_gap_median'].iloc[0]:.2f}",
         "seed": 0, "status": "KEEP", "notes": ""},
    ]
    with RESULTS.open("w") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in HEADER) + "\n")


if __name__ == "__main__":
    main()
