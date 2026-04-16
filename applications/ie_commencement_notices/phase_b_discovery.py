"""Phase B: inverse-design / discovery.

For the commencement-notice cohort study, the discovery question is:
  Given the fitted champion survival model, which (LA x size-stratum x
  apartment/dwelling) cells maximise the predicted probability that a
  permission is completed within 48 months of grant?

We score every cell on the observed cohort, filter by minimum cell size,
and rank by empirical P(complete within 48m of grant).  Output to
discoveries/optimal_la_scheme_recommendations.csv.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import analysis  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "discoveries" / "optimal_la_scheme_recommendations.csv"
MIN_CELL = 30
CENSOR = analysis.CENSOR_DATE


def main():
    df = analysis.load_cohort()
    # Restrict to permissions granted at least 48 months ago so completion is judgeable
    cutoff = CENSOR - pd.DateOffset(months=48)
    m = df["CN_Date_Granted"].notna() & (df["CN_Date_Granted"] <= cutoff) & (df["grant_year"] >= 2014)
    sub = df.loc[m].copy()

    sub["ccc_within_48m"] = (
        sub["CCC_Date_Validated"].notna()
        & ((sub["CCC_Date_Validated"] - sub["CN_Date_Granted"]).dt.days <= 48 * 30)
    ).astype(int)
    sub["commence_within_48m"] = (
        sub["CN_Commencement_Date"].notna()
        & ((sub["CN_Commencement_Date"] - sub["CN_Date_Granted"]).dt.days <= 48 * 30)
    ).astype(int)
    sub["type"] = np.where(
        sub["apartment_flag"] == 1,
        "apartment",
        np.where(sub["dwelling_flag"] == 1, "dwelling", "other_residential"),
    )

    g = (
        sub.groupby(["LA_clean", "size_stratum", "type"], observed=True)
        .agg(
            n=("CN_Date_Granted", "size"),
            p_commence_48m=("commence_within_48m", "mean"),
            p_complete_48m=("ccc_within_48m", "mean"),
            median_units=("units_filled", "median"),
        )
        .reset_index()
    )
    g = g.loc[g["n"] >= MIN_CELL].copy()
    g = g.sort_values("p_complete_48m", ascending=False)

    # Phase B rec file — full table
    OUT.parent.mkdir(parents=True, exist_ok=True)
    g.to_csv(OUT, index=False)
    print(f"Wrote {len(g)} (LA × size × type) recommendations to {OUT}")

    # Top 15 summary
    print("\n== Top 15 cells by predicted 48-month completion probability ==")
    print(g.head(15).to_string(index=False))

    print("\n== Bottom 15 cells (delivery risk) ==")
    print(g.tail(15).to_string(index=False))

    # Aggregate to per-LA recommendation: the best-performing size stratum for each LA
    best = g.loc[g.groupby("LA_clean")["p_complete_48m"].idxmax()].sort_values("p_complete_48m", ascending=False)
    best_path = ROOT / "discoveries" / "per_la_best_stratum.csv"
    best.to_csv(best_path, index=False)
    print(f"\nPer-LA best-stratum written to {best_path}")


if __name__ == "__main__":
    main()
