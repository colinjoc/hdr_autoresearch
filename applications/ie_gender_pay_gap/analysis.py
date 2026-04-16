"""Irish gender pay gap 2022-2025 mandatory-disclosure analysis (paygap.ie data).

Parallel to the UK analysis: population-wide and within-firm trends across the
first four years of Irish mandatory reporting. Cross-country comparison of
narrowing rates with the UK 2017-2025 result.
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


def main():
    df = pd.read_csv(RAW / "paygap_ie_all.csv", encoding="utf-8")
    print(f"[load] {len(df)} rows; years: {sorted(df['Report Year'].unique())}")
    print("columns sample:", list(df.columns[:15]))
    df["Median Hourly Gap"] = pd.to_numeric(df["Median Hourly Gap"], errors="coerce")
    df["Mean Hourly Gap"] = pd.to_numeric(df["Mean Hourly Gap"], errors="coerce")

    # Annual trend
    annual = df.groupby("Report Year").agg(
        n_submissions=("Median Hourly Gap", "size"),
        median_gap_median=("Median Hourly Gap", "median"),
        mean_gap_median=("Mean Hourly Gap", "median"),
    ).reset_index()
    annual.to_csv(DISCOVERIES / "ie_annual_trend.csv", index=False)
    print("\n=== annual trend ===")
    print(annual.to_string(index=False))

    # Within-firm 2022 → 2025 panel
    pairs = df[df["Report Year"].isin([2022, 2025])][["Company Name", "Report Year", "Median Hourly Gap"]]
    pairs = pairs.dropna().pivot_table(index="Company Name", columns="Report Year",
                                       values="Median Hourly Gap", aggfunc="first")
    if 2022 in pairs.columns and 2025 in pairs.columns:
        pairs = pairs.dropna()
        pairs["delta_2025_minus_2022"] = pairs[2025] - pairs[2022]
        print(f"\n=== within-firm IE 2022 → 2025 (n={len(pairs)}) ===")
        print(f"median gap 2022: {pairs[2022].median():.2f}")
        print(f"median gap 2025: {pairs[2025].median():.2f}")
        print(f"median Δ: {pairs['delta_2025_minus_2022'].median():.2f} pp")
        print(f"share narrowing: {(pairs['delta_2025_minus_2022'] < 0).mean() * 100:.1f}%")
        pairs.to_csv(DISCOVERIES / "ie_within_firm_2022_2025.csv")

    # NACE sector breakdown
    sec = df[df["Report Year"] == 2025].copy()
    by_sector = sec.groupby("NACE Section")["Median Hourly Gap"].agg(["median", "size"]).reset_index()
    by_sector = by_sector.rename(columns={"size": "n"}).sort_values("median", ascending=False)
    by_sector.to_csv(DISCOVERIES / "ie_gap_by_sector_2025.csv", index=False)
    print("\n=== Top 5 & bottom 5 sectors by median gap (2025) ===")
    print(by_sector.head(5).to_string(index=False))
    print("...")
    print(by_sector.tail(5).to_string(index=False))

    # Cross-country comparison (hardcoded UK reference from EMP-02)
    uk_first = 9.30  # 2017 UK
    uk_last = 8.11   # 2025 UK
    uk_years = 2025 - 2017
    ie_first = annual[annual["Report Year"] == 2022]["median_gap_median"].iloc[0]
    ie_last = annual[annual["Report Year"] == 2025]["median_gap_median"].iloc[0]
    ie_years = 2025 - 2022
    print(f"\n=== cross-country annualised narrowing rate ===")
    print(f"UK 2017-2025: {uk_first:.2f}% → {uk_last:.2f}%  ({(uk_last-uk_first)/uk_years:+.2f} pp/year)")
    print(f"IE 2022-2025: {ie_first:.2f}% → {ie_last:.2f}%  ({(ie_last-ie_first)/ie_years:+.2f} pp/year)")

    # Chart
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(annual["Report Year"], annual["median_gap_median"], "o-", linewidth=1.3, color="teal", label="IE median-of-medians")
    axes[0].plot(annual["Report Year"], annual["mean_gap_median"], "o--", linewidth=1, color="coral", label="IE mean-of-medians")
    axes[0].plot([2017, 2025], [9.30, 8.11], "o:", linewidth=1, color="gray", alpha=0.5, label="UK endpoints for comparison")
    axes[0].set_xlabel("reporting year"); axes[0].set_ylabel("median hourly pay gap (%)")
    axes[0].set_title("Irish gender pay gap 2022-2025 (4 years of mandatory disclosure)")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
    axes[0].axhline(0, color="black", linewidth=0.5)

    top10_sector = by_sector.head(10)
    axes[1].barh(top10_sector["NACE Section"].str[:25], top10_sector["median"], color="maroon", alpha=0.7)
    axes[1].set_xlabel("median hourly gap 2025 (%)")
    axes[1].set_title("Top 10 Irish sectors by gender pay gap (2025)")
    axes[1].grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(CHARTS / "ie_gpg_trend.png", dpi=120); plt.close(fig)

    HEADER = ["experiment_id", "commit", "description", "metric", "value",
              "seed", "status", "notes"]
    rows = [
        {"experiment_id": "E00", "commit": "phase0.5",
         "description": "paygap.ie IE GPG panel 2022-2025",
         "metric": "n_employer_year_obs", "value": len(df),
         "seed": 0, "status": "BASELINE",
         "notes": f"{df['Company Name'].nunique()} unique companies"},
        {"experiment_id": "E01", "commit": "phase1",
         "description": "IE 4-year median gap trajectory",
         "metric": f"median_2022_to_2025",
         "value": f"{ie_first:.2f} → {ie_last:.2f} ({(ie_last-ie_first)/ie_years:+.2f} pp/yr)",
         "seed": 0, "status": "KEEP", "notes": f"UK comparator: {uk_first:.2f}→{uk_last:.2f} at {(uk_last-uk_first)/uk_years:+.2f}pp/yr"},
    ]
    with RESULTS.open("w") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in HEADER) + "\n")


if __name__ == "__main__":
    main()
