"""
Phase B Discovery: Viability map by county and stranded hectares analysis.

Outputs:
  discoveries/viability_map_by_county.csv — viable/marginal/unviable per county with margin %
  discoveries/stranded_hectares.csv — hectares of zoned land in unviable areas
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from viability import (
    assess_county_viability, calculate_viability,
    COUNTY_SALE_PRICES_2025, DEV_CONTRIBUTIONS, ZONED_HECTARES,
    get_construction_cost_per_sqm, load_rzlpa02,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DISC_DIR = os.path.join(PROJECT_DIR, "discoveries")
os.makedirs(DISC_DIR, exist_ok=True)


def generate_viability_map():
    """Generate viability classification for every county."""
    df = assess_county_viability()

    # Compute break-even sale price for each county
    breakevens = []
    for _, row in df.iterrows():
        county = row["county"]
        lo, hi = 100000, 1200000
        for _ in range(50):
            mid = (lo + hi) / 2
            r = calculate_viability(
                sale_price=mid,
                land_cost_per_hectare=row["land_cost_per_hectare"],
                construction_cost_per_sqm=get_construction_cost_per_sqm(county),
                avg_sqm=110,
                dev_contributions=DEV_CONTRIBUTIONS.get(county, 12000),
            )
            if r["margin"] > 0:
                hi = mid
            else:
                lo = mid
        breakevens.append(round(mid))

    df["break_even_price"] = breakevens
    df["price_gap"] = df["break_even_price"] - df["sale_price"]
    df["price_gap_pct"] = (df["price_gap"] / df["sale_price"] * 100).round(1)

    # Select output columns
    output = df[[
        "county", "sale_price", "land_cost_per_hectare", "land_cost_per_unit",
        "construction_cost", "dev_contributions", "finance_cost", "required_profit",
        "total_cost", "margin", "margin_pct", "viable", "viability_class",
        "break_even_price", "price_gap", "price_gap_pct",
        "zoned_hectares", "potential_units",
    ]].copy()

    output["margin_pct"] = (output["margin_pct"] * 100).round(1)
    output = output.sort_values("margin_pct", ascending=False)

    path = os.path.join(DISC_DIR, "viability_map_by_county.csv")
    output.to_csv(path, index=False)
    print(f"Written: {path}")
    print(f"  {len(output)} counties assessed")
    print(f"  Viable: {sum(output['viable'])} counties")
    print(f"  Marginal: {sum(output['viability_class'] == 'marginal')} counties")
    print(f"  Unviable: {sum(output['viability_class'] == 'unviable')} counties")

    return output


def generate_stranded_hectares():
    """Generate stranded hectares analysis."""
    df = assess_county_viability()

    stranded = df[~df["viable"]].copy()
    stranded["stranded_hectares"] = stranded["zoned_hectares"]
    stranded["stranded_units"] = stranded["potential_units"]
    stranded["rzlt_annual_liability"] = stranded["land_cost_per_hectare"] * stranded["zoned_hectares"] * 0.03

    output = stranded[[
        "county", "viability_class", "margin_pct", "zoned_hectares",
        "stranded_hectares", "stranded_units", "rzlt_annual_liability",
        "sale_price", "total_cost",
    ]].copy()

    output["margin_pct"] = (output["margin_pct"] * 100).round(1)
    output["rzlt_annual_liability"] = output["rzlt_annual_liability"].round(0)
    output = output.sort_values("stranded_hectares", ascending=False)

    path = os.path.join(DISC_DIR, "stranded_hectares.csv")
    output.to_csv(path, index=False)
    print(f"\nWritten: {path}")
    print(f"  Total stranded hectares: {output['stranded_hectares'].sum():,.0f}")
    print(f"  Total stranded units: {output['stranded_units'].sum():,.0f}")
    print(f"  Total annual RZLT liability on unviable land: €{output['rzlt_annual_liability'].sum():,.0f}")

    return output


if __name__ == "__main__":
    print("=" * 60)
    print("Phase B Discovery: Viability Map & Stranded Hectares")
    print("=" * 60)
    generate_viability_map()
    generate_stranded_hectares()
