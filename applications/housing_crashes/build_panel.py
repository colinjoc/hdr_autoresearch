"""Build the metro-month panel for housing crash prediction.

Structure:
- key: (cbsa_code, month)
- features available at month t (strictly past, no leakage)
- outcome: y(t) = 1 iff zhvi(t+12) / zhvi(t) <= 1 - CRASH_THRESH

Training window: 2016-08 → latest month with observable outcome (month ≤ 2024-12
minus forward horizon). Outcomes after month = 2024-12 are right-censored and
must NOT appear in train/test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from loaders import (  # noqa: E402
    crosswalk_zillow_to_cbsa, load_mortgage_30yr_monthly,
    load_realtor, load_zhvi_long,
)


CRASH_DROP_THRESH = 0.10   # 12-month return ≤ −10%
FORWARD_MONTHS = 12
MAX_OBSERVED_MONTH = pd.Timestamp("2024-12-01")  # anything with outcome after this is censored


def build_panel() -> pd.DataFrame:
    zhvi = load_zhvi_long()
    realtor = load_realtor()
    mort = load_mortgage_30yr_monthly()
    xw = crosswalk_zillow_to_cbsa(zhvi, realtor)
    print(f"name-match: {len(xw)} metros", flush=True)

    # Attach cbsa_code to ZHVI via crosswalk
    zh = zhvi.merge(xw[["zillow_region_id", "cbsa_code"]], on="zillow_region_id", how="inner")
    # Rolling returns per metro
    zh = zh.sort_values(["cbsa_code", "month"]).copy()
    g = zh.groupby("cbsa_code")["zhvi"]
    zh["zhvi_1mo_ret"] = g.pct_change(1)
    zh["zhvi_3mo_ret"] = g.pct_change(3)
    zh["zhvi_6mo_ret"] = g.pct_change(6)
    zh["zhvi_12mo_ret"] = g.pct_change(12)
    zh["zhvi_24mo_ret"] = g.pct_change(24)
    # Forward return for outcome
    zh["zhvi_fwd_12mo"] = g.shift(-FORWARD_MONTHS)
    zh["zhvi_fwd_12mo_ret"] = zh["zhvi_fwd_12mo"] / zh["zhvi"] - 1
    zh["crash_next_12mo"] = (zh["zhvi_fwd_12mo_ret"] <= -CRASH_DROP_THRESH).astype(int)

    # Left-join Realtor by (cbsa_code, month) — inventory features
    panel = zh.merge(realtor, on=["cbsa_code", "month"], how="left")
    # Log-transform count features (all have fat right tails)
    for col in ("active_listing_count", "new_listing_count",
                "pending_listing_count", "total_listing_count",
                "price_reduced_count", "price_increased_count"):
        if col in panel.columns:
            panel[f"log1p_{col}"] = np.log1p(panel[col])
    # price_reduced_share = reduced / active
    if "price_reduced_count" in panel.columns and "active_listing_count" in panel.columns:
        panel["price_reduced_share"] = (panel["price_reduced_count"]
                                         / panel["active_listing_count"].clip(lower=1))
    # median days on market (raw)
    # price-to-income — defer to later (needs ACS)

    # Join mortgage rate
    panel = panel.merge(mort, on="month", how="left")
    g2 = panel.sort_values("month").groupby("cbsa_code")["mortgage_30yr"]
    panel["mortgage_30yr_delta_12mo"] = g2.diff(12)

    # Restrict to observable-outcome rows (month ≤ 2023-12 for fwd-12mo window)
    panel = panel[panel["month"] <= MAX_OBSERVED_MONTH - pd.DateOffset(months=FORWARD_MONTHS)].copy()

    # Restrict training universe to months where inventory features exist
    panel = panel[panel["month"] >= pd.Timestamp("2016-08-01")].copy()

    # Drop rows with no outcome (edge-of-series)
    panel = panel.dropna(subset=["crash_next_12mo", "zhvi_12mo_ret"]).copy()

    print(f"panel: {len(panel):,} metro-months  "
          f"({panel['cbsa_code'].nunique()} metros, "
          f"{panel['month'].min().date()} → {panel['month'].max().date()})", flush=True)
    print(f"crash rate: {panel['crash_next_12mo'].mean():.3%}", flush=True)

    out = HERE / "data" / "panel.parquet"
    panel.to_parquet(out, index=False)
    print(f"wrote {out}", flush=True)
    return panel


if __name__ == "__main__":
    build_panel()
