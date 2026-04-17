"""Irish residential development cost model.

Constructs a full cost stack for representative dwelling types across
4 location categories, classifies each component as POLICY-set or
MARKET-driven, and runs viability/scenario analysis.

Data sources:
- Buildcost.ie H1 2025 cost guide (build cost per sqm by region)
- CSO RZLPA02 (zoned residential land prices by county)
- LA development contribution schemes (hard-coded from published schedules)
- Revenue Commissioners (VAT rate)
- Planning & Development Act 2000 s.96 (Part V)
- RIAI/SCSI estimates (BCAR, professional fees)
- SCSI viability benchmark (developer margin)
"""

import json
import os
import copy

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")

# =============================================================================
# Build cost per sqm by region (from Buildcost.ie H1 2025, page 3)
# These are EUR/sqm for new-build residential, excl. VAT
# Format: {dwelling_type: {region: EUR/sqm}}
# =============================================================================
# Build cost per sqm is from Buildcost.ie H1 2025.
# These are SCHEME costs (multi-unit) which are ~15% below one-off rebuilding costs.
# The buildcost.ie figures are SCSI rebuilding guide rates. For SCHEME development,
# economies of scale reduce per-unit cost. Apply 0.85 factor.
_SCHEME_FACTOR = 0.85

BUILD_COST_PER_SQM = {
    # 3-bed semi-detached, 110 sqm
    "3bed_semi": {
        "dublin": round(3190 * _SCHEME_FACTOR),
        "commuter": round(2770 * _SCHEME_FACTOR),
        "regional": round(2750 * _SCHEME_FACTOR),
        "rural": round(2528 * _SCHEME_FACTOR),
    },
    # 2-bed apartment, 75 sqm (higher per-sqm due to common areas, lifts, etc.)
    "2bed_apt": {
        "dublin": round(3800 * _SCHEME_FACTOR),
        "commuter": round(3300 * _SCHEME_FACTOR),
        "regional": round(3200 * _SCHEME_FACTOR),
        "rural": round(3000 * _SCHEME_FACTOR),
    },
    # 4-bed detached, 119 sqm
    "4bed_detached": {
        "dublin": round(3300 * _SCHEME_FACTOR),
        "commuter": round(2840 * _SCHEME_FACTOR),
        "regional": round(2814 * _SCHEME_FACTOR),
        "rural": round(2639 * _SCHEME_FACTOR),
    },
    # 3-bed terraced, 98 sqm
    "3bed_terrace": {
        "dublin": round(3010 * _SCHEME_FACTOR),
        "commuter": round(2640 * _SCHEME_FACTOR),
        "regional": round(2629 * _SCHEME_FACTOR),
        "rural": round(2432 * _SCHEME_FACTOR),
    },
}

# Dwelling sizes in sqm
DWELLING_SIZES = {
    "3bed_semi": 110,      # as specified in research question
    "2bed_apt": 75,        # as specified
    "4bed_detached": 119,
    "3bed_terrace": 98,
}

# =============================================================================
# Land costs by location (derived from CSO RZLPA02 median price per hectare)
# Converted to per-unit basis assuming typical densities
# Density: units per hectare for each dwelling type
# =============================================================================

# Median price per hectare from RZLPA02 (2024 data)
# Ireland: €571,235/ha, Dublin: €1,587,929/ha (from region codes)
LAND_PRICE_PER_HECTARE = {
    "dublin": 1_587_929,    # Co. Dublin median
    "commuter": 741_143,    # Mid-East region (Wicklow/Kildare/Meath)
    "regional": 484_983,    # avg of Mid-West, South-West
    "rural": 299_219,       # Border region
}

# Typical density (units per hectare) by dwelling type
DENSITY = {
    "3bed_semi": 35,      # typical suburban semi-d scheme
    "2bed_apt": 100,      # apartment scheme
    "4bed_detached": 20,  # lower density detached
    "3bed_terrace": 45,   # higher density terrace
}

# =============================================================================
# Policy-set cost parameters
# =============================================================================

# Development contributions per unit (LA schemes - national average)
DEV_CONTRIBUTIONS = {
    "dublin": 25_000,     # Dublin city/county range €20-30k
    "commuter": 18_000,   # Kildare/Meath/Wicklow
    "regional": 15_000,   # Cork/Galway/Limerick
    "rural": 10_000,      # Border/Midlands
}

# Part V: 20% of units at cost price = effective cost per unit
# Simplified: the cross-subsidy cost is ~10-15% of sale price on the remaining 80%
# For modelling: Part V effective cost = 20% * (sale_price - build_cost) spread across all units
# We use a fixed estimate per unit based on SCSI viability reports
PART_V_COST_PER_UNIT = {
    "dublin": 20_000,     # higher sale prices = higher Part V cost
    "commuter": 12_000,
    "regional": 8_000,
    "rural": 5_000,
}

# VAT rate on new residential
VAT_RATE = 0.135  # 13.5%

# BCAR compliance (assigned certifier + inspections)
BCAR_COST = {
    "3bed_semi": 5_500,
    "2bed_apt": 4_500,
    "4bed_detached": 6_000,
    "3bed_terrace": 5_000,
}

# Planning application fees (per unit in a scheme)
PLANNING_FEES = 1_500  # including fire cert + disability access cert

# Professional fees as % of build cost (architect, engineer, QS)
PROFESSIONAL_FEE_RATE = 0.12  # 12% of hard construction cost

# Finance cost: % of total development cost (interest on drawdown)
FINANCE_RATE = 0.08  # 8% average

# Developer margin as % of total cost (SCSI viability benchmark)
DEVELOPER_MARGIN_RATE = 0.15  # 15%

# =============================================================================
# Achievable sale prices by location (from market data / U-2 predecessor)
# =============================================================================
# New-build sale prices (2024/2025) — these are higher than secondhand
# Sources: Property Price Register new-build data, GeoDirectory, SCSI
SALE_PRICES = {
    "3bed_semi": {
        "dublin": 550_000,
        "commuter": 420_000,
        "regional": 350_000,
        "rural": 280_000,
    },
    "2bed_apt": {
        "dublin": 450_000,
        "commuter": 340_000,
        "regional": 280_000,
        "rural": 220_000,
    },
    "4bed_detached": {
        "dublin": 700_000,
        "commuter": 520_000,
        "regional": 430_000,
        "rural": 340_000,
    },
    "3bed_terrace": {
        "dublin": 500_000,
        "commuter": 380_000,
        "regional": 310_000,
        "rural": 245_000,
    },
}

# =============================================================================
# County-level data for viability analysis
# =============================================================================

# 26 Republic of Ireland counties with estimated sale prices and land costs
# Sale prices from Property Price Register averages (2024)
# Land costs from RZLPA02 or interpolated
# New-build sale prices by county (3-bed semi) from PPR new-build data 2024
COUNTIES = {
    "Dublin": {"sale_price_3bed": 550_000, "land_per_ha": 1_587_929, "dev_contrib": 25_000, "region": "dublin"},
    "Cork": {"sale_price_3bed": 400_000, "land_per_ha": 873_746, "dev_contrib": 18_000, "region": "regional"},
    "Galway": {"sale_price_3bed": 380_000, "land_per_ha": 754_097, "dev_contrib": 16_000, "region": "regional"},
    "Limerick": {"sale_price_3bed": 340_000, "land_per_ha": 614_023, "dev_contrib": 14_000, "region": "regional"},
    "Waterford": {"sale_price_3bed": 320_000, "land_per_ha": 512_811, "dev_contrib": 12_000, "region": "regional"},
    "Kildare": {"sale_price_3bed": 460_000, "land_per_ha": 1_162_555, "dev_contrib": 20_000, "region": "commuter"},
    "Meath": {"sale_price_3bed": 420_000, "land_per_ha": 644_039, "dev_contrib": 18_000, "region": "commuter"},
    "Wicklow": {"sale_price_3bed": 480_000, "land_per_ha": 1_214_411, "dev_contrib": 22_000, "region": "commuter"},
    "Louth": {"sale_price_3bed": 370_000, "land_per_ha": 792_704, "dev_contrib": 15_000, "region": "commuter"},
    "Wexford": {"sale_price_3bed": 320_000, "land_per_ha": 581_493, "dev_contrib": 12_000, "region": "regional"},
    "Kilkenny": {"sale_price_3bed": 310_000, "land_per_ha": 449_581, "dev_contrib": 11_000, "region": "regional"},
    "Tipperary": {"sale_price_3bed": 280_000, "land_per_ha": 296_070, "dev_contrib": 10_000, "region": "regional"},
    "Clare": {"sale_price_3bed": 300_000, "land_per_ha": 242_317, "dev_contrib": 10_000, "region": "regional"},
    "Kerry": {"sale_price_3bed": 340_000, "land_per_ha": 502_712, "dev_contrib": 12_000, "region": "regional"},
    "Mayo": {"sale_price_3bed": 270_000, "land_per_ha": 305_173, "dev_contrib": 8_000, "region": "rural"},
    "Donegal": {"sale_price_3bed": 240_000, "land_per_ha": 304_757, "dev_contrib": 8_000, "region": "rural"},
    "Sligo": {"sale_price_3bed": 260_000, "land_per_ha": 417_321, "dev_contrib": 8_000, "region": "rural"},
    "Roscommon": {"sale_price_3bed": 230_000, "land_per_ha": 305_173, "dev_contrib": 7_000, "region": "rural"},
    "Leitrim": {"sale_price_3bed": 210_000, "land_per_ha": 1_031_222, "dev_contrib": 7_000, "region": "rural"},
    "Cavan": {"sale_price_3bed": 240_000, "land_per_ha": 172_781, "dev_contrib": 8_000, "region": "rural"},
    "Monaghan": {"sale_price_3bed": 235_000, "land_per_ha": 201_448, "dev_contrib": 7_000, "region": "rural"},
    "Longford": {"sale_price_3bed": 200_000, "land_per_ha": 853_775, "dev_contrib": 6_000, "region": "rural"},
    "Westmeath": {"sale_price_3bed": 280_000, "land_per_ha": 978_855, "dev_contrib": 10_000, "region": "rural"},
    "Offaly": {"sale_price_3bed": 260_000, "land_per_ha": 487_594, "dev_contrib": 8_000, "region": "rural"},
    "Laois": {"sale_price_3bed": 280_000, "land_per_ha": 278_080, "dev_contrib": 9_000, "region": "rural"},
    "Carlow": {"sale_price_3bed": 300_000, "land_per_ha": 616_534, "dev_contrib": 10_000, "region": "regional"},
}


def classify_components():
    """Classify each cost component as POLICY or MARKET."""
    return {
        "materials": "MARKET",
        "labour": "MARKET",
        "site_works": "MARKET",
        "land": "MARKET",
        "dev_contributions": "POLICY",
        "part_v": "POLICY",
        "vat": "POLICY",
        "bcar": "POLICY",
        "planning_fees": "POLICY",
        "professional_fees": "MARKET",
        "finance": "MARKET",
        "developer_margin": "MARKET",
    }


def build_cost_stack(dwelling_type, location):
    """Build a full cost stack for a dwelling type at a location.

    Args:
        dwelling_type: one of "3bed_semi", "2bed_apt", "4bed_detached", "3bed_terrace"
        location: one of "dublin", "commuter", "regional", "rural"

    Returns:
        dict mapping component name to EUR cost
    """
    sqm = DWELLING_SIZES[dwelling_type]
    cost_per_sqm = BUILD_COST_PER_SQM[dwelling_type][location]

    # Hard construction cost (excl. VAT)
    hard_cost = cost_per_sqm * sqm

    # Split hard cost: materials ~45%, labour ~40%, site works ~15%
    materials = hard_cost * 0.45
    labour = hard_cost * 0.40
    site_works = hard_cost * 0.15

    # Land cost per unit
    land_per_ha = LAND_PRICE_PER_HECTARE[location]
    density = DENSITY[dwelling_type]
    land = land_per_ha / density

    # Policy costs
    dev_contributions = DEV_CONTRIBUTIONS[location]
    part_v = PART_V_COST_PER_UNIT[location]
    bcar = BCAR_COST[dwelling_type]
    planning_fees = PLANNING_FEES

    # Professional fees (% of hard cost)
    professional_fees = hard_cost * PROFESSIONAL_FEE_RATE

    # Subtotal before VAT, finance, margin
    subtotal_pre = (materials + labour + site_works + land +
                    dev_contributions + part_v + bcar + planning_fees +
                    professional_fees)

    # VAT on construction (applies to hard costs + professional fees)
    vat_base = hard_cost + professional_fees
    vat = vat_base * VAT_RATE

    # Finance (on total development cost excl. margin)
    finance_base = subtotal_pre + vat
    finance = finance_base * FINANCE_RATE

    # Developer margin (on total cost including finance)
    margin_base = finance_base + finance
    developer_margin = margin_base * DEVELOPER_MARGIN_RATE

    return {
        "materials": round(materials, 2),
        "labour": round(labour, 2),
        "site_works": round(site_works, 2),
        "land": round(land, 2),
        "dev_contributions": round(dev_contributions, 2),
        "part_v": round(part_v, 2),
        "vat": round(vat, 2),
        "bcar": round(bcar, 2),
        "planning_fees": round(planning_fees, 2),
        "professional_fees": round(professional_fees, 2),
        "finance": round(finance, 2),
        "developer_margin": round(developer_margin, 2),
    }


def policy_share(dwelling_type, location):
    """Calculate the share of total cost that is policy-set."""
    stack = build_cost_stack(dwelling_type, location)
    classes = classify_components()
    total = sum(stack.values())
    policy_total = sum(v for k, v in stack.items() if classes.get(k) == "POLICY")
    return policy_total / total


def viability_margin(dwelling_type, location):
    """Calculate viability margin: (sale_price - total_cost) / sale_price.

    Positive = viable, negative = not viable.
    """
    stack = build_cost_stack(dwelling_type, location)
    total_cost = sum(stack.values())
    sale_price = SALE_PRICES[dwelling_type][location]
    return (sale_price - total_cost) / sale_price


def apply_scenario(base_stack, scenario):
    """Apply a policy scenario to a cost stack.

    Args:
        base_stack: dict from build_cost_stack()
        scenario: dict of multipliers, e.g. {"vat_rate": 0.5} means halve VAT

    Returns:
        modified cost stack
    """
    modified = copy.deepcopy(base_stack)

    if "vat_rate" in scenario:
        modified["vat"] = base_stack["vat"] * scenario["vat_rate"]
    if "part_v_rate" in scenario:
        modified["part_v"] = base_stack["part_v"] * scenario["part_v_rate"]
    if "dev_contributions_rate" in scenario:
        modified["dev_contributions"] = base_stack["dev_contributions"] * scenario["dev_contributions_rate"]
    if "bcar_rate" in scenario:
        modified["bcar"] = base_stack["bcar"] * scenario["bcar_rate"]
    if "planning_fees_rate" in scenario:
        modified["planning_fees"] = base_stack["planning_fees"] * scenario["planning_fees_rate"]

    return modified


def build_county_cost_stack(county_name, dwelling_type="3bed_semi"):
    """Build cost stack for a specific county."""
    county = COUNTIES[county_name]
    region = county["region"]
    sqm = DWELLING_SIZES[dwelling_type]
    cost_per_sqm = BUILD_COST_PER_SQM[dwelling_type][region]

    hard_cost = cost_per_sqm * sqm
    materials = hard_cost * 0.45
    labour = hard_cost * 0.40
    site_works = hard_cost * 0.15

    land_per_ha = county["land_per_ha"]
    density = DENSITY[dwelling_type]
    land = land_per_ha / density

    dev_contributions = county["dev_contrib"]
    part_v = PART_V_COST_PER_UNIT[region]
    bcar = BCAR_COST[dwelling_type]
    planning_fees = PLANNING_FEES

    professional_fees = hard_cost * PROFESSIONAL_FEE_RATE

    subtotal_pre = (materials + labour + site_works + land +
                    dev_contributions + part_v + bcar + planning_fees +
                    professional_fees)

    vat_base = hard_cost + professional_fees
    vat = vat_base * VAT_RATE

    finance_base = subtotal_pre + vat
    finance = finance_base * FINANCE_RATE

    margin_base = finance_base + finance
    developer_margin = margin_base * DEVELOPER_MARGIN_RATE

    return {
        "materials": round(materials, 2),
        "labour": round(labour, 2),
        "site_works": round(site_works, 2),
        "land": round(land, 2),
        "dev_contributions": round(dev_contributions, 2),
        "part_v": round(part_v, 2),
        "vat": round(vat, 2),
        "bcar": round(bcar, 2),
        "planning_fees": round(planning_fees, 2),
        "professional_fees": round(professional_fees, 2),
        "finance": round(finance, 2),
        "developer_margin": round(developer_margin, 2),
    }


def county_viability_margin(county_name, dwelling_type="3bed_semi", scenario=None):
    """Calculate viability margin for a county, optionally with a scenario."""
    stack = build_county_cost_stack(county_name, dwelling_type)
    if scenario:
        stack = apply_scenario(stack, scenario)
    total_cost = sum(stack.values())
    sale_price = COUNTIES[county_name]["sale_price_3bed"]
    return (sale_price - total_cost) / sale_price


def count_viable_counties(dwelling_type="3bed_semi", scenario=None):
    """Count how many counties are viable (margin >= 0) under a scenario."""
    count = 0
    for county_name in COUNTIES:
        margin = county_viability_margin(county_name, dwelling_type, scenario)
        if margin >= 0:
            count += 1
    return count


def viability_gap_fund(dwelling_type="3bed_semi"):
    """Calculate per-unit subsidy needed to make each non-viable county viable.

    Returns dict of {county: gap_amount} for counties with negative margin.
    """
    gaps = {}
    for county_name in COUNTIES:
        stack = build_county_cost_stack(county_name, dwelling_type)
        total_cost = sum(stack.values())
        sale_price = COUNTIES[county_name]["sale_price_3bed"]
        if total_cost > sale_price:
            gaps[county_name] = round(total_cost - sale_price, 2)
    return gaps


def all_scenarios():
    """Define all 20+ experiment scenarios."""
    return {
        "E01_vat_to_9pct": {"vat_rate": 9.0 / 13.5},
        "E02_part_v_halved": {"part_v_rate": 0.5},
        "E03_dev_contribs_halved": {"dev_contributions_rate": 0.5},
        "E04_dev_contribs_equalised_low": {"dev_contributions_rate": 6000 / 25000},  # to lowest
        "E05_bcar_halved": {"bcar_rate": 0.5},
        "E06_planning_fees_zeroed": {"planning_fees_rate": 0.0},
        "E07_all_policy_halved": {"vat_rate": 0.5, "part_v_rate": 0.5,
                                   "dev_contributions_rate": 0.5, "bcar_rate": 0.5,
                                   "planning_fees_rate": 0.0},
        "E08_all_policy_zeroed": {"vat_rate": 0.0, "part_v_rate": 0.0,
                                   "dev_contributions_rate": 0.0, "bcar_rate": 0.0,
                                   "planning_fees_rate": 0.0},
        "E09_vat_zeroed": {"vat_rate": 0.0},
        "E10_part_v_zeroed": {"part_v_rate": 0.0},
        "E13_margin_to_10pct": {},  # handled specially
        "E14_finance_to_5pct": {},  # handled specially
        "E15_land_cpo": {},  # handled specially
    }


if __name__ == "__main__":
    # Quick summary
    for dt in ["3bed_semi", "2bed_apt"]:
        for loc in ["dublin", "commuter", "regional", "rural"]:
            stack = build_cost_stack(dt, loc)
            total = sum(stack.values())
            ps = policy_share(dt, loc)
            vm = viability_margin(dt, loc)
            print(f"{dt:15s} {loc:10s}  total=EUR{total:,.0f}  policy={ps:.1%}  margin={vm:.1%}")
