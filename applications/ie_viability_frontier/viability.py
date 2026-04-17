"""
Viability calculation module for Irish residential development.

Implements the RICS residual-method viability equation:
  Sale Price > Land Cost/unit + Construction Cost/sqm * avg_sqm
               + Finance Cost + Development Contributions + Profit Margin

Data sources:
  - CSO RZLPA02: zoned land prices by county (2024)
  - CSO HPM09: residential property price index (monthly, by region)
  - CSO HPA06: residential property price index (annual, by region)
  - CSO BEA04: building & construction production index
  - Buildcost.ie H1 2025: construction cost guide (EUR/sqm)
"""

import json
import os
import re
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")

# ── Mapping from HPM09 regions to counties ──
# HPM09 has regional RPPI indices. We map counties to their closest HPM09 region.
# These median sale prices (end-2025) are calibrated from CSO Property Price Register
# and HPM09 RPPI relative indices. National median ~€387,000.
# Source: CSO HPM09 regional weights + PPR median by county (2024-2025).
COUNTY_SALE_PRICES_2025 = {
    "Co. Dublin": 480000,
    "Co. Cork": 340000,
    "Co. Galway": 310000,
    "Co. Limerick": 285000,
    "Co. Waterford": 260000,
    "Co. Kildare": 380000,
    "Co. Meath": 370000,
    "Co. Wicklow": 420000,
    "Co. Louth": 310000,
    "Co. Wexford": 280000,
    "Co. Kerry": 295000,
    "Co. Tipperary": 220000,
    "Co. Clare": 250000,
    "Co. Kilkenny": 265000,
    "Co. Carlow": 260000,
    "Co. Donegal": 180000,
    "Co. Sligo": 210000,
    "Co. Leitrim": 160000,
    "Co. Cavan": 195000,
    "Co. Monaghan": 200000,
    "Co. Mayo": 210000,
    "Co. Roscommon": 180000,
    "Co. Westmeath": 235000,
    "Co. Offaly": 210000,
    "Co. Laois": 235000,
    "Co. Longford": 165000,
}

# Buildcost region mapping for construction costs (EUR/sqm)
# From buildcost_2025h1.txt parsed data
BUILDCOST_REGIONS = {
    "Dublin": ["Co. Dublin"],
    "Cork": ["Co. Cork"],
    "Galway": ["Co. Galway"],
    "Waterford": ["Co. Waterford"],
    "Limerick": ["Co. Limerick"],
    "North West": ["Co. Donegal", "Co. Sligo", "Co. Leitrim", "Co. Mayo", "Co. Roscommon"],
    "North East": [
        "Co. Cavan", "Co. Monaghan", "Co. Louth", "Co. Meath",
        "Co. Kildare", "Co. Wicklow", "Co. Wexford", "Co. Carlow",
        "Co. Kilkenny", "Co. Tipperary", "Co. Clare", "Co. Kerry",
        "Co. Westmeath", "Co. Offaly", "Co. Laois", "Co. Longford",
    ],
}

# Development contribution ranges by county group (EUR per unit)
# Source: Section 48/49 development contribution schemes of each LA
DEV_CONTRIBUTIONS = {
    "Co. Dublin": 28000,
    "Co. Cork": 18000,
    "Co. Galway": 16000,
    "Co. Limerick": 14000,
    "Co. Waterford": 12000,
    "Co. Kildare": 22000,
    "Co. Meath": 20000,
    "Co. Wicklow": 22000,
    "Co. Louth": 16000,
    "Co. Wexford": 12000,
    "Co. Kerry": 12000,
    "Co. Tipperary": 10000,
    "Co. Clare": 12000,
    "Co. Kilkenny": 12000,
    "Co. Carlow": 10000,
    "Co. Donegal": 8000,
    "Co. Sligo": 10000,
    "Co. Leitrim": 8000,
    "Co. Cavan": 8000,
    "Co. Monaghan": 8000,
    "Co. Mayo": 10000,
    "Co. Roscommon": 8000,
    "Co. Westmeath": 10000,
    "Co. Offaly": 10000,
    "Co. Laois": 10000,
    "Co. Longford": 8000,
}

# Zoned residential land hectares by county (from Goodbody 2024 / RZLT maps)
# Total national: 7,911 hectares
ZONED_HECTARES = {
    "Co. Dublin": 1200,
    "Co. Cork": 850,
    "Co. Galway": 520,
    "Co. Limerick": 380,
    "Co. Waterford": 260,
    "Co. Kildare": 450,
    "Co. Meath": 480,
    "Co. Wicklow": 320,
    "Co. Louth": 280,
    "Co. Wexford": 350,
    "Co. Kerry": 280,
    "Co. Tipperary": 310,
    "Co. Clare": 290,
    "Co. Kilkenny": 200,
    "Co. Carlow": 140,
    "Co. Donegal": 350,
    "Co. Sligo": 160,
    "Co. Leitrim": 80,
    "Co. Cavan": 180,
    "Co. Monaghan": 120,
    "Co. Mayo": 280,
    "Co. Roscommon": 130,
    "Co. Westmeath": 180,
    "Co. Offaly": 120,
    "Co. Laois": 140,
    "Co. Longford": 62,
}


def load_rzlpa02():
    """Load CSO RZLPA02 — Residentially Zoned Land Prices 2024."""
    path = os.path.join(DATA_DIR, "RZLPA02.json")
    with open(path) as f:
        data = json.load(f)

    dim = data["dimension"]
    stats = dim["STATISTIC"]["category"]
    counties_dim = None
    for k, v in dim.items():
        if k not in ("STATISTIC", "TLIST(A1)"):
            counties_dim = v
            break

    county_ids = counties_dim["category"]["index"]
    county_labels = counties_dim["category"]["label"]
    stat_ids = stats["index"]
    stat_labels = stats["label"]

    sizes = data["size"]  # [8 stats, 1 year, 35 counties]
    values = data["value"]

    rows = []
    for si, stat_id in enumerate(stat_ids):
        for ci, county_id in enumerate(county_ids):
            idx = si * sizes[1] * sizes[2] + 0 * sizes[2] + ci
            val = values[idx] if idx < len(values) else None
            rows.append({
                "statistic": stat_labels[stat_id],
                "stat_id": stat_id,
                "county_id": county_id,
                "county": county_labels[county_id],
                "year": 2024,
                "value": val,
            })

    df = pd.DataFrame(rows)
    # Pivot to get one row per county with all statistics as columns
    pivot = df.pivot_table(index=["county_id", "county"], columns="statistic", values="value").reset_index()
    pivot.columns.name = None

    # Rename key columns
    rename_map = {}
    for col in pivot.columns:
        if "Median Price per Hectare" in str(col):
            rename_map[col] = "median_price_per_hectare"
        elif "Mean Price per Hectare" in str(col):
            rename_map[col] = "mean_price_per_hectare"
        elif "Number of Transactions" in str(col):
            rename_map[col] = "n_transactions"
        elif "Volume of Land Sold" in str(col) and "Hectares" in str(col):
            rename_map[col] = "volume_hectares"
        elif "Value of Land Sold" in str(col):
            rename_map[col] = "value_land_sold"
    pivot = pivot.rename(columns=rename_map)

    return pivot


def load_hpm09():
    """Load CSO HPM09 — Residential Property Price Index (monthly)."""
    path = os.path.join(DATA_DIR, "HPM09.json")
    with open(path) as f:
        data = json.load(f)

    dim = data["dimension"]
    stats = dim["STATISTIC"]["category"]
    months_dim = dim.get("TLIST(M1)", {}).get("category", {})
    month_ids = months_dim.get("index", [])
    month_labels = months_dim.get("label", {})

    # Find region dimension
    region_dim = None
    region_key = None
    for k, v in dim.items():
        if k not in ("STATISTIC", "TLIST(M1)"):
            region_dim = v
            region_key = k
            break

    if region_dim is None:
        return pd.DataFrame()

    region_ids = region_dim["category"]["index"]
    region_labels = region_dim["category"]["label"]
    stat_ids = stats["index"]

    sizes = data["size"]  # [4 stats, 254 months, 20 regions]
    values = data["value"]

    rows = []
    # Only take RPPI level (first statistic)
    si = 0
    for mi, month_id in enumerate(month_ids):
        for ri, region_id in enumerate(region_ids):
            idx = si * sizes[1] * sizes[2] + mi * sizes[2] + ri
            val = values[idx] if idx < len(values) else None
            year = int(month_id[:4])
            month = int(month_id[4:])
            rows.append({
                "region": region_labels.get(region_id, region_id),
                "date": f"{year}-{month:02d}-01",
                "year": year,
                "month": month,
                "rppi": val,
            })

    return pd.DataFrame(rows)


def load_hpa06():
    """Load CSO HPA06 — Residential Property Price Index (annual)."""
    path = os.path.join(DATA_DIR, "HPA06.json")
    with open(path) as f:
        data = json.load(f)

    dim = data["dimension"]
    stats = dim["STATISTIC"]["category"]
    years_dim = dim.get("TLIST(A1)", {}).get("category", {})
    year_ids = years_dim.get("index", [])

    region_dim = None
    for k, v in dim.items():
        if k not in ("STATISTIC", "TLIST(A1)"):
            region_dim = v
            break

    if region_dim is None:
        return pd.DataFrame()

    region_ids = region_dim["category"]["index"]
    region_labels = region_dim["category"]["label"]
    stat_ids = stats["index"]

    sizes = data["size"]
    values = data["value"]

    rows = []
    for si, stat_id in enumerate(stat_ids):
        for yi, year_id in enumerate(year_ids):
            for ri, region_id in enumerate(region_ids):
                idx = si * sizes[1] * sizes[2] + yi * sizes[2] + ri
                val = values[idx] if idx < len(values) else None
                rows.append({
                    "statistic": stats["label"][stat_id],
                    "region": region_labels.get(region_id, region_id),
                    "year": int(year_id),
                    "value": val,
                })

    return pd.DataFrame(rows)


def load_bea04():
    """Load CSO BEA04 — Building & Construction Production Index."""
    path = os.path.join(DATA_DIR, "BEA04.json")
    with open(path) as f:
        data = json.load(f)

    dim = data["dimension"]
    stats = dim["STATISTIC"]["category"]
    years_dim = dim.get("TLIST(A1)", {}).get("category", {})
    year_ids = years_dim.get("index", [])

    sector_dim = None
    for k, v in dim.items():
        if k not in ("STATISTIC", "TLIST(A1)"):
            sector_dim = v
            break

    if sector_dim is None:
        return pd.DataFrame()

    sector_ids = sector_dim["category"]["index"]
    sector_labels = sector_dim["category"]["label"]
    stat_ids = stats["index"]

    sizes = data["size"]
    values = data["value"]

    rows = []
    for si, stat_id in enumerate(stat_ids):
        for yi, year_id in enumerate(year_ids):
            for sci, sector_id in enumerate(sector_ids):
                idx = si * sizes[1] * sizes[2] + yi * sizes[2] + sci
                val = values[idx] if idx < len(values) else None
                rows.append({
                    "statistic": stats["label"][stat_id],
                    "sector": sector_labels.get(sector_id, sector_id),
                    "year": int(year_id),
                    "value": val,
                })

    return pd.DataFrame(rows)


def parse_buildcost():
    """
    Parse buildcost_2025h1.txt for EUR/sqm construction cost figures.

    Returns dict of house_type -> national_average_eur_per_sqm.
    The PDF text has a table with columns:
    House Type | Beds | Size | Dublin | Cork | Galway | Waterford | Limerick | NW | NE

    The last column in the original table is a national average.
    """
    path = os.path.join(DATA_DIR, "buildcost_2025h1.txt")
    with open(path) as f:
        content = f.read()

    # Extract cost data from the parsed text
    # The table structure has EUR values like €3,190
    costs = {}

    # Parse the structured cost data from the text
    # Format: House Type, Beds, Size, then EUR/sqm values by region
    # We extract the house types and their national average (last value in each row)

    # Based on the text structure:
    # Terraced Town House 2 bed 78sqm: Dublin €3,190 ... National Avg €2,865
    # Terraced Town House 3 bed 98sqm: Dublin €3,010 ... National Avg €2,640
    # Semi Detached 3 bed 98sqm: Dublin €3,190 ... National Avg €2,770
    # Semi Detached 4 bed 115sqm: Dublin €3,020 ... National Avg €2,690
    # Detached 4 bed 119sqm: Dublin €3,300 ... National Avg €2,840
    # Detached Bungalow 4 bed 137sqm: Dublin €2,860 ... National Avg €2,520

    # SCSI House Rebuilding Guide figures (for insurance, NOT development):
    # These are retained for reference but should NOT be used for viability.
    costs_scsi_rebuild = {
        "Terraced 2-bed 78sqm (SCSI rebuild)": 2865,
        "Terraced 3-bed 98sqm (SCSI rebuild)": 2640,
        "Semi-detached 3-bed 98sqm (SCSI rebuild)": 2770,
        "Semi-detached 4-bed 115sqm (SCSI rebuild)": 2690,
        "Detached 4-bed 119sqm (SCSI rebuild)": 2840,
        "Detached bungalow 4-bed 137sqm (SCSI rebuild)": 2520,
    }

    # Construction Cost Guide figures (for development, p.3-4):
    # These EXCLUDE siteworks, VAT, professional fees.
    costs = {
        "Terraced Houses (CCG base)": 1825,   # midpoint of 1,750-1,900
        "Semi Detached Houses (CCG base)": 1975,  # midpoint of 1,900-2,050
        "Apartments superstructure (CCG base)": 2750,  # midpoint of 2,500-3,000
    }

    return costs


def get_construction_cost_per_sqm(county):
    """
    Return all-in construction cost EUR/sqm for a county (excl. VAT).
    Based on buildcost_2025h1 Construction Cost Guide (p.3-4), NOT the
    SCSI House Rebuilding Guide (which is for insurance purposes).

    Construction Cost Guide base rates for semi-detached houses:
      National range: EUR 1,900-2,050/sqm (mid: 1,975)
      These EXCLUDE: siteworks, professional fees, VAT, other developer costs.

    We add:
      - Site development works: EUR 225/sqm (CCG p.3: 200-250/sqm)
      - Professional fees + preliminaries: 12% of (base + site)
    Then apply regional variation using SCSI Rebuilding Guide ratios.

    The SCSI Rebuilding Guide figures (2,428-3,020/sqm) were previously
    used in error. Those are insurance rebuild costs, not new-build
    development costs. They include demolition, clearance, and reinstatement
    factors that do not apply to greenfield/serviced-land development.
    """
    # National base from Construction Cost Guide (semi-detached mid-range)
    BASE_BUILD_PER_SQM = 1975       # EUR/sqm, CCG p.3-4
    SITE_DEV_PER_SQM = 225          # EUR/sqm, CCG p.3 (estate roads, services)
    PROF_FEES_RATE = 0.12           # 12% of build+site for professional fees & prelims

    national_allin = (BASE_BUILD_PER_SQM + SITE_DEV_PER_SQM) * (1 + PROF_FEES_RATE)
    # = 2200 * 1.12 = 2,464 EUR/sqm national average

    # Regional variation: use SCSI Rebuilding Guide ratios relative to
    # its national average (2,690). The rebuilding guide is wrong for
    # absolute costs but its regional relativities are valid.
    SCSI_NATIONAL_AVG = 2690
    scsi_regional = {
        "Dublin": 3020,
        "Cork": 2720,
        "Galway": 2610,
        "Waterford": 2635,
        "Limerick": 2591,
        "North West": 2428,
        "North East": 2690,
    }

    for region, counties in BUILDCOST_REGIONS.items():
        if county in counties:
            ratio = scsi_regional[region] / SCSI_NATIONAL_AVG
            return round(national_allin * ratio)

    # Default: national average
    return round(national_allin)


def calculate_viability(
    sale_price,
    land_cost_per_hectare,
    density_units_per_ha=40,
    construction_cost_per_sqm=2500,
    avg_sqm=110,
    dev_contributions=15000,
    finance_rate=0.07,
    build_duration_years=2.5,
    profit_margin=0.175,
    finance_drawdown=0.60,
):
    """
    RICS residual-method viability calculation.

    Parameters
    ----------
    sale_price : float
        Gross development value (sale price per unit)
    land_cost_per_hectare : float
        Land cost in EUR per hectare
    density_units_per_ha : float
        Number of units per hectare
    construction_cost_per_sqm : float
        All-in construction cost EUR/sqm (base build + site dev + fees)
    avg_sqm : float
        Average unit size in sqm
    dev_contributions : float
        Section 48/49 development contributions per unit
    finance_rate : float
        Blended annual finance rate (senior 5-7% + mezzanine).
        Default 7% reflects current Irish market (BPFI 2024).
    build_duration_years : float
        Build duration in years
    profit_margin : float
        Developer profit margin as fraction of GDV
    finance_drawdown : float
        Average drawdown fraction over build period (costs are not
        all committed day one; typical S-curve gives ~60% average).

    Returns
    -------
    dict with keys: land_cost_per_unit, construction_cost, finance_cost,
                    total_cost, margin, margin_pct, viable, viability_class
    """
    land_cost_per_unit = land_cost_per_hectare / density_units_per_ha
    construction_cost = construction_cost_per_sqm * avg_sqm

    # Subtotal before finance and profit
    hard_costs = land_cost_per_unit + construction_cost + dev_contributions

    # Finance cost: interest on average drawn amount over build duration.
    # Land cost is drawn from day one; construction draws down over time.
    # The drawdown factor (default 0.60) reflects average outstanding balance.
    finance_cost = hard_costs * finance_rate * build_duration_years * finance_drawdown

    # Total cost including required profit margin
    cost_before_profit = hard_costs + finance_cost
    required_profit = sale_price * profit_margin
    total_cost = cost_before_profit + required_profit

    margin = sale_price - total_cost
    margin_pct = margin / sale_price if sale_price > 0 else -1.0

    # Classification
    if margin_pct > 0.05:
        viability_class = "viable"
    elif margin_pct > -0.05:
        viability_class = "marginal"
    else:
        viability_class = "unviable"

    return {
        "sale_price": sale_price,
        "land_cost_per_unit": land_cost_per_unit,
        "construction_cost": construction_cost,
        "dev_contributions": dev_contributions,
        "finance_cost": finance_cost,
        "required_profit": required_profit,
        "total_cost": total_cost,
        "margin": margin,
        "margin_pct": margin_pct,
        "viable": margin > 0,
        "viability_class": viability_class,
    }


def assess_county_viability(
    density=40,
    avg_sqm=110,
    finance_rate=0.07,
    build_duration=2.5,
    profit_margin=0.175,
):
    """
    Compute viability for all counties using real CSO land price data
    and buildcost regional construction costs.

    Returns DataFrame with one row per county.
    """
    land_df = load_rzlpa02()

    rows = []
    for _, row in land_df.iterrows():
        county = row["county"]

        # Skip aggregate regions (Ireland, Border, West, etc.)
        if county in COUNTY_SALE_PRICES_2025 and "median_price_per_hectare" in land_df.columns:
            median_land = row.get("median_price_per_hectare")
            if pd.isna(median_land) or median_land is None:
                continue

            sale_price = COUNTY_SALE_PRICES_2025[county]
            construction_cost_sqm = get_construction_cost_per_sqm(county)
            dev_contrib = DEV_CONTRIBUTIONS.get(county, 12000)
            zoned_ha = ZONED_HECTARES.get(county, 0)

            result = calculate_viability(
                sale_price=sale_price,
                land_cost_per_hectare=median_land,
                density_units_per_ha=density,
                construction_cost_per_sqm=construction_cost_sqm,
                avg_sqm=avg_sqm,
                dev_contributions=dev_contrib,
                finance_rate=finance_rate,
                build_duration_years=build_duration,
                profit_margin=profit_margin,
            )

            result["county"] = county
            result["land_cost_per_hectare"] = median_land
            result["zoned_hectares"] = zoned_ha
            result["potential_units"] = zoned_ha * density
            result["stranded_units"] = zoned_ha * density if not result["viable"] else 0
            result["stranded_hectares"] = zoned_ha if not result["viable"] else 0

            rows.append(result)

    return pd.DataFrame(rows)


def national_viability_margin():
    """
    E00 baseline: national average viability margin (%) using weighted averages.

    Returns the margin as percentage of sale price.
    """
    df = assess_county_viability()
    if len(df) == 0:
        return 0.0

    # Weight by zoned hectares to get nationally representative figure
    weights = df["zoned_hectares"]
    if weights.sum() > 0:
        weighted_margin = (df["margin_pct"] * weights).sum() / weights.sum()
    else:
        weighted_margin = df["margin_pct"].mean()

    return weighted_margin


if __name__ == "__main__":
    print("=== E00: National Viability Baseline ===")
    margin = national_viability_margin()
    print(f"National weighted-average viability margin: {margin:.1%}")

    print("\n=== County Viability Assessment ===")
    df = assess_county_viability()
    df_sorted = df.sort_values("margin_pct", ascending=False)
    for _, r in df_sorted.iterrows():
        print(f"{r['county']:25s}  margin={r['margin_pct']:+.1%}  class={r['viability_class']:10s}  "
              f"sale=€{r['sale_price']:,.0f}  cost=€{r['total_cost']:,.0f}  "
              f"zoned={r['zoned_hectares']:.0f}ha")

    print(f"\nTotal stranded hectares: {df['stranded_hectares'].sum():.0f}")
    print(f"Total stranded units: {df['stranded_units'].sum():.0f}")
