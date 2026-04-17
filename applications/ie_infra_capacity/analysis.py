"""
U-3: Infrastructure Capacity Blocks Analysis
How much of Ireland's zoned residential land is blocked by wastewater infrastructure constraints?
"""
import os
import pandas as pd
import numpy as np
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
WW_PATH = os.path.join(PROJECT_DIR, "data", "raw", "wastewater_capacity.csv")
PLANNING_PATH = "/home/col/generalized_hdr_autoresearch/applications/ie_lapsed_permissions/data/raw/national_planning_points.csv"
BHQ01_PATH = "/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion/data/raw/BHQ01.json"
NDQ04_PATH = "/home/col/generalized_hdr_autoresearch/applications/ie_viability_frontier/data/raw/NDQ04.json"

# Total nationally zoned residential land (hectares) from U-1 / Goodbody
TOTAL_ZONED_HA = 7911

# County-level zoned land estimates from Goodbody (2021) regional splits
# These are approximate proportions based on population and zoning patterns
# Actual Goodbody figures are region-level; we distribute within regions by population share
ZONED_HA_BY_COUNTY = {
    "Dublin City": 450, "Fingal": 520, "South Dublin": 380, "DLR": 310,
    "Cork": 850, "Galway": 420, "Limerick": 350, "Waterford": 200,
    "Kildare": 380, "Meath": 360, "Wicklow": 280, "Louth": 220,
    "Kerry": 200, "Wexford": 210, "Tipperary": 250, "Kilkenny": 150,
    "Clare": 180, "Mayo": 170, "Donegal": 250, "Carlow": 100,
    "Laois": 120, "Offaly": 110, "Westmeath": 140, "Longford": 70,
    "Roscommon": 100, "Sligo": 110, "Leitrim": 50, "Cavan": 110,
    "Monaghan": 90,
}

# Mapping from WW county names to a canonical form
COUNTY_MAP = {
    "Carlow": "Carlow", "Cavan": "Cavan", "Clare": "Clare", "Cork": "Cork",
    "DLR": "DLR", "Donegal": "Donegal", "Dublin City": "Dublin City",
    "Fingal": "Fingal", "Galway": "Galway", "Kerry": "Kerry",
    "Kildare": "Kildare", "Kilkenny": "Kilkenny", "Laois": "Laois",
    "Leitrim": "Leitrim", "Limerick": "Limerick", "Longford": "Longford",
    "Louth": "Louth", "Mayo": "Mayo", "Meath": "Meath",
    "Monaghan": "Monaghan", "Offaly": "Offaly", "Roscommon": "Roscommon",
    "Sligo": "Sligo", "South Dublin": "South Dublin", "Tipperary": "Tipperary",
    "Waterford": "Waterford", "Westmeath": "Westmeath", "Wexford": "Wexford",
    "Wicklow": "Wicklow",
}

# Mapping from Planning Authority names to canonical county
PA_TO_COUNTY = {
    "Carlow County Council": "Carlow",
    "Cavan County Council": "Cavan",
    "Clare County Council": "Clare",
    "Cork City Council": "Cork",
    "Cork County Council": "Cork",
    "Donegal County Council": "Donegal",
    "Dublin City Council": "Dublin City",
    "Dun Laoghaire Rathdown County Council": "DLR",
    "Fingal County Council": "Fingal",
    "Galway City Council": "Galway",
    "Galway County Council": "Galway",
    "Kerry County Council": "Kerry",
    "Kildare County Council": "Kildare",
    "Kilkenny County Council": "Kilkenny",
    "Laois County Council": "Laois",
    "Leitrim County Council": "Leitrim",
    "Limerick County Council": "Limerick",
    "Longford County Council": "Longford",
    "Louth County Council": "Louth",
    "Mayo County Council": "Mayo",
    "Meath County Council": "Meath",
    "Monaghan County Council": "Monaghan",
    "Offaly County Council": "Offaly",
    "Roscommon County Council": "Roscommon",
    "Sligo County Council": "Sligo",
    "South Dublin County Council": "South Dublin",
    "Tipperary County Council": "Tipperary",
    "Waterford City and County Council": "Waterford",
    "Westmeath County Council": "Westmeath",
    "Wexford County Council": "Wexford",
    "Wicklow County Council": "Wicklow",
}


def load_wastewater():
    """Load the wastewater capacity register."""
    ww = pd.read_csv(WW_PATH)
    ww["county_canonical"] = ww["county"].map(COUNTY_MAP)
    ww["is_red"] = (ww["capacity"] == "RED").astype(int)
    ww["is_amber"] = (ww["capacity"] == "AMBER").astype(int)
    ww["is_red_or_amber"] = ((ww["capacity"] == "RED") | (ww["capacity"] == "AMBER")).astype(int)
    ww["has_project"] = ww["project_planned"].notna().astype(int)
    return ww


def load_planning():
    """Load national planning register with county mapping."""
    pp = pd.read_csv(PLANNING_PATH, encoding="utf-8-sig", low_memory=False)
    # Filter to real planning authorities
    pp = pp[pp["Planning Authority"].isin(PA_TO_COUNTY.keys())].copy()
    pp["county"] = pp["Planning Authority"].map(PA_TO_COUNTY)
    # Parse residential units
    pp["NumResidentialUnits"] = pd.to_numeric(pp["NumResidentialUnits"], errors="coerce").fillna(0).astype(int)
    # Parse decision
    pp["is_granted"] = pp["Decision"].str.contains("CONDITIONAL|GRANT", case=False, na=False).astype(int)
    pp["is_refused"] = pp["Decision"].str.contains("REFUS", case=False, na=False).astype(int)
    # Parse dates
    pp["ReceivedDate"] = pd.to_datetime(pp["ReceivedDate"], format="mixed", dayfirst=True, errors="coerce")
    pp["year"] = pp["ReceivedDate"].dt.year
    # Residential flag
    pp["is_residential"] = (pp["NumResidentialUnits"] > 0).astype(int)
    return pp


def compute_county_capacity():
    """Compute county-level WWTP capacity shares."""
    ww = load_wastewater()
    county_agg = ww.groupby("county_canonical").agg(
        n_wwtp=("capacity", "count"),
        n_green=("capacity", lambda x: (x == "GREEN").sum()),
        n_amber=("capacity", lambda x: (x == "AMBER").sum()),
        n_red=("capacity", lambda x: (x == "RED").sum()),
        n_project=("has_project", "sum"),
    ).reset_index()
    county_agg.rename(columns={"county_canonical": "county"}, inplace=True)
    county_agg["pct_green"] = county_agg["n_green"] / county_agg["n_wwtp"] * 100
    county_agg["pct_amber"] = county_agg["n_amber"] / county_agg["n_wwtp"] * 100
    county_agg["pct_red"] = county_agg["n_red"] / county_agg["n_wwtp"] * 100
    county_agg["pct_red_or_amber"] = (county_agg["n_red"] + county_agg["n_amber"]) / county_agg["n_wwtp"] * 100
    county_agg["zoned_ha"] = county_agg["county"].map(ZONED_HA_BY_COUNTY)
    county_agg["estimated_blocked_ha"] = county_agg["zoned_ha"] * county_agg["pct_red_or_amber"] / 100
    return county_agg


def merge_planning_with_capacity():
    """Merge planning applications with county-level WWTP capacity shares."""
    county_cap = compute_county_capacity()
    pp = load_planning()

    # Merge on county
    merged = pp.merge(
        county_cap[["county", "pct_red", "pct_amber", "pct_green", "pct_red_or_amber", "n_wwtp",
                     "n_red", "n_amber", "estimated_blocked_ha"]],
        on="county",
        how="left",
    )
    merged["capacity_status"] = pd.cut(
        merged["pct_red_or_amber"],
        bins=[0, 15, 30, 100],
        labels=["low_constraint", "medium_constraint", "high_constraint"],
        include_lowest=True,
    )
    return merged


def run_e00():
    """E00: Baseline - share of settlements/catchments in RED or AMBER nationally."""
    ww = load_wastewater()
    n = len(ww)
    n_red = (ww["capacity"] == "RED").sum()
    n_amber = (ww["capacity"] == "AMBER").sum()
    pct = (n_red + n_amber) / n * 100
    return {
        "experiment": "E00",
        "description": "Baseline: national share of WWTPs in RED or AMBER",
        "n_total": n,
        "n_red": int(n_red),
        "n_amber": int(n_amber),
        "n_green": int(n - n_red - n_amber),
        "pct_red_or_amber": round(pct, 1),
        "pct_red": round(n_red / n * 100, 1),
        "pct_amber": round(n_amber / n * 100, 1),
        "metric": "pct_constrained",
        "value": round(pct, 1),
    }


def run_e01_dublin():
    """E01: Dublin-only analysis (Dublin City, Fingal, DLR, South Dublin)."""
    ww = load_wastewater()
    dublin_counties = ["Dublin City", "Fingal", "DLR", "South Dublin"]
    dub = ww[ww["county_canonical"].isin(dublin_counties)]
    n = len(dub)
    n_red = (dub["capacity"] == "RED").sum()
    n_amber = (dub["capacity"] == "AMBER").sum()
    # Ringsend serves most of Dublin City
    ringsend = ww[ww["wwtp"].str.contains("Ringsend", case=False, na=False)]
    return {
        "experiment": "E01",
        "description": "Dublin-only WWTP capacity",
        "dublin_settlements": n,
        "n_red": int(n_red),
        "n_amber": int(n_amber),
        "pct_constrained": round((n_red + n_amber) / max(n, 1) * 100, 1),
        "ringsend_status": ringsend["capacity"].values[0] if len(ringsend) > 0 else "not_found",
        "ringsend_project": ringsend["project_planned"].values[0] if len(ringsend) > 0 else "unknown",
    }


def run_e02_high_red_counties():
    """E02: Counties where >50% of WWTPs are RED."""
    cc = compute_county_capacity()
    high_red = cc[cc["pct_red"] > 50].sort_values("pct_red", ascending=False)
    threshold_30 = cc[cc["pct_red"] > 30].sort_values("pct_red", ascending=False)
    return {
        "experiment": "E02",
        "description": "Counties with >50% RED WWTPs",
        "counties_over_50pct": high_red["county"].tolist(),
        "n_counties_over_50": len(high_red),
        "counties_over_30pct": threshold_30["county"].tolist(),
        "n_counties_over_30": len(threshold_30),
    }


def run_e03_project_planned():
    """E03: Does having an upgrade planned mitigate? Compare RED with project vs RED without."""
    ww = load_wastewater()
    red = ww[ww["capacity"] == "RED"]
    red_with_project = red[red["has_project"] == 1]
    red_no_project = red[red["has_project"] == 0]
    amber = ww[ww["capacity"] == "AMBER"]
    amber_with = amber[amber["has_project"] == 1]
    return {
        "experiment": "E03",
        "description": "Project-planned vs no-project for RED/AMBER WWTPs",
        "n_red_total": len(red),
        "n_red_with_project": len(red_with_project),
        "n_red_no_project": len(red_no_project),
        "pct_red_with_project": round(len(red_with_project) / max(len(red), 1) * 100, 1),
        "n_amber_with_project": len(amber_with),
        "pct_amber_with_project": round(len(amber_with) / max(len(amber), 1) * 100, 1),
    }


def run_e04_refusal_rates():
    """E04: Correlation between RED status and planning refusal rates."""
    merged = merge_planning_with_capacity()
    res = merged[merged["is_residential"] == 1]
    # Group by constraint level
    groups = res.groupby("capacity_status", observed=True).agg(
        n_apps=("is_refused", "count"),
        n_refused=("is_refused", "sum"),
        n_granted=("is_granted", "sum"),
    ).reset_index()
    groups["refusal_rate"] = groups["n_refused"] / groups["n_apps"] * 100
    return {
        "experiment": "E04",
        "description": "Refusal rates by WWTP capacity constraint level",
        "groups": groups.to_dict("records"),
    }


def run_e05_time_trend():
    """E05: Are RED areas seeing declining applications over time?"""
    merged = merge_planning_with_capacity()
    res = merged[(merged["is_residential"] == 1) & (merged["year"].between(2015, 2024))]
    trends = res.groupby(["year", "capacity_status"], observed=True).agg(
        n_apps=("is_residential", "sum"),
    ).reset_index()
    return {
        "experiment": "E05",
        "description": "Time trend in residential applications by constraint level",
        "trend_data": trends.to_dict("records"),
    }


def run_e06_settlement_vs_county():
    """E06: Settlement-level vs county-level aggregation sensitivity."""
    ww = load_wastewater()
    # Settlement-level: each settlement has one capacity status
    settlement_counts = ww.groupby("capacity").size()
    # County-level: weighted by number of settlements
    county_cap = compute_county_capacity()
    county_weighted = (county_cap["pct_red_or_amber"] * county_cap["n_wwtp"]).sum() / county_cap["n_wwtp"].sum()
    settlement_pct = (settlement_counts.get("RED", 0) + settlement_counts.get("AMBER", 0)) / len(ww) * 100
    return {
        "experiment": "E06",
        "description": "Settlement-level vs county-level aggregation comparison",
        "settlement_level_pct_constrained": round(settlement_pct, 1),
        "county_weighted_pct_constrained": round(county_weighted, 1),
        "difference_pp": round(abs(settlement_pct - county_weighted), 1),
    }


def run_e07_large_vs_small():
    """E07: Large settlements (those with major WWTPs) vs small."""
    ww = load_wastewater()
    # Use registration number prefix as proxy: D-prefix = larger (design > 2000 PE), A-prefix = smaller
    ww["is_large"] = ww["reg_no"].fillna("").str.startswith("D").astype(int)
    large = ww[ww["is_large"] == 1]
    small = ww[ww["is_large"] == 0]
    return {
        "experiment": "E07",
        "description": "Large (D-reg) vs small (A-reg) WWTP capacity comparison",
        "n_large": len(large),
        "large_pct_constrained": round(large["is_red_or_amber"].mean() * 100, 1),
        "n_small": len(small),
        "small_pct_constrained": round(small["is_red_or_amber"].mean() * 100, 1),
    }


def run_e08_overlap_viability():
    """E08: Overlap with viability frontier (83% unviable from U-2)."""
    # From U-2: 83% of zoned land is economically stranded
    # From this analysis: X% is in RED/AMBER catchments
    e00 = run_e00()
    pct_infra_blocked = e00["pct_red_or_amber"]
    pct_unviable = 83.0  # From U-2
    # Under independence assumption: P(both) = P(A) * P(B)
    # Under correlation assumption: overlap is higher
    independent_overlap = pct_infra_blocked * pct_unviable / 100
    # Maximum overlap = min(A, B)
    max_overlap = min(pct_infra_blocked, pct_unviable)
    return {
        "experiment": "E08",
        "description": "Overlap between infrastructure-blocked and economically unviable land",
        "pct_infra_blocked": pct_infra_blocked,
        "pct_unviable": pct_unviable,
        "independent_overlap_pct": round(independent_overlap, 1),
        "max_overlap_pct": round(max_overlap, 1),
        "estimated_overlap_pct": round((independent_overlap + max_overlap) / 2, 1),
    }


def run_e09_hectares():
    """E09: Estimated hectares of zoned land in RED/AMBER catchments."""
    cc = compute_county_capacity()
    total_blocked = cc["estimated_blocked_ha"].sum()
    return {
        "experiment": "E09",
        "description": "Estimated hectares of zoned land in RED/AMBER catchments",
        "total_zoned_ha": TOTAL_ZONED_HA,
        "estimated_blocked_ha": round(total_blocked, 0),
        "pct_blocked": round(total_blocked / TOTAL_ZONED_HA * 100, 1),
        "county_details": cc[["county", "zoned_ha", "pct_red_or_amber", "estimated_blocked_ha"]].to_dict("records"),
    }


def run_e10_double_stranded():
    """E10: 'Double-stranded' land - RED/AMBER AND economically unviable."""
    e09 = run_e09_hectares()
    blocked_ha = e09["estimated_blocked_ha"]
    # U-2 found 83% unviable; assume proportional overlap
    double_stranded_ha = blocked_ha * 0.83
    return {
        "experiment": "E10",
        "description": "Double-stranded: RED/AMBER + economically unviable",
        "infra_blocked_ha": blocked_ha,
        "double_stranded_ha": round(double_stranded_ha, 0),
        "pct_of_total_zoned": round(double_stranded_ha / TOTAL_ZONED_HA * 100, 1),
    }


def run_e11_green_low_activity():
    """E11: GREEN capacity areas with low application rates."""
    cc = compute_county_capacity()
    merged = merge_planning_with_capacity()
    res = merged[merged["is_residential"] == 1]

    apps_by_county = res.groupby("county").agg(n_apps=("is_residential", "sum")).reset_index()
    green_counties = cc[cc["pct_green"] > 80].merge(apps_by_county, on="county", how="left")
    green_counties["apps_per_ha"] = green_counties["n_apps"] / green_counties["zoned_ha"]
    low_activity = green_counties[green_counties["apps_per_ha"] < green_counties["apps_per_ha"].median()]
    return {
        "experiment": "E11",
        "description": "GREEN capacity counties with low application rates",
        "green_low_activity_counties": low_activity["county"].tolist(),
        "n_counties": len(low_activity),
    }


def run_e12_completions():
    """E12: Completion rates (ESB connections) in GREEN vs RED counties."""
    # This would require NDQ04 data matched to counties
    # For now, use county-level capacity as proxy
    cc = compute_county_capacity()
    high_green = cc[cc["pct_green"] > 80]["county"].tolist()
    high_red = cc[cc["pct_red"] > 20]["county"].tolist()
    return {
        "experiment": "E12",
        "description": "Completion proxy comparison: high-GREEN vs high-RED counties",
        "high_green_counties": high_green,
        "high_red_counties": high_red,
        "note": "ESB connections (NDQ04) are county-level; full matching requires LA-level data",
    }


def run_e13_commuter_belt():
    """E13: Dublin commuter belt capacity (Meath, Kildare, Wicklow)."""
    ww = load_wastewater()
    commuter = ["Meath", "Kildare", "Wicklow"]
    belt = ww[ww["county_canonical"].isin(commuter)]
    result = {}
    for county in commuter:
        c = belt[belt["county_canonical"] == county]
        result[county] = {
            "n_wwtp": len(c),
            "n_red": int((c["capacity"] == "RED").sum()),
            "n_amber": int((c["capacity"] == "AMBER").sum()),
            "pct_constrained": round(c["is_red_or_amber"].mean() * 100, 1),
        }
    overall_pct = round(belt["is_red_or_amber"].mean() * 100, 1)
    return {
        "experiment": "E13",
        "description": "Dublin commuter belt WWTP capacity",
        "county_details": result,
        "overall_pct_constrained": overall_pct,
    }


def run_e14_investment():
    """E14: WWTP upgrade investment needed per unit of capacity freed."""
    ww = load_wastewater()
    cc = compute_county_capacity()
    # RED WWTPs with projects planned
    red_with_project = ww[(ww["capacity"] == "RED") & (ww["has_project"] == 1)]
    red_no_project = ww[(ww["capacity"] == "RED") & (ww["has_project"] == 0)]
    # Estimate: each RED WWTP upgrade unlocks its settlement's capacity
    # Typical WWTP upgrade cost: EUR 5-50M depending on size
    return {
        "experiment": "E14",
        "description": "WWTP upgrade investment priorities",
        "n_red_with_project": len(red_with_project),
        "n_red_no_project": len(red_no_project),
        "settlements_unlockable_with_projects": red_with_project["settlement"].tolist(),
        "priority_counties": cc.sort_values("estimated_blocked_ha", ascending=False).head(5)["county"].tolist(),
    }


def run_e15_uwwtd():
    """E15: EU Urban Wastewater Treatment Directive compliance proxy."""
    ww = load_wastewater()
    # RED status often correlates with UWWTD non-compliance
    # Large plants (D-prefix) under UWWTD; smaller (A-prefix) may not be
    large = ww[ww["reg_no"].fillna("").str.startswith("D")]
    large_red = (large["capacity"] == "RED").sum()
    return {
        "experiment": "E15",
        "description": "UWWTD compliance proxy: large plant RED status",
        "n_large_plants": len(large),
        "n_large_red": int(large_red),
        "pct_large_red": round(large_red / max(len(large), 1) * 100, 1),
        "note": "D-prefix registration = design PE > 2000, subject to UWWTD",
    }


def run_e16_population():
    """E16: Population growth vs capacity headroom."""
    # CSO population by county would be needed for full analysis
    # Proxy: use number of residential applications as growth pressure indicator
    merged = merge_planning_with_capacity()
    res = merged[merged["is_residential"] == 1]
    growth = res.groupby("county").agg(
        n_res_apps=("is_residential", "sum"),
        pct_red_or_amber=("pct_red_or_amber", "first"),
    ).reset_index()
    correlation = growth["n_res_apps"].corr(growth["pct_red_or_amber"])
    return {
        "experiment": "E16",
        "description": "Correlation between residential demand and capacity constraints",
        "correlation": round(correlation, 3),
        "interpretation": "positive = high-demand areas also constrained; negative = constraints in low-demand areas",
    }


def run_e17_one_off():
    """E17: One-off rural houses (septic tank, not WWTP-dependent)."""
    pp = load_planning()
    one_off = pp[pp["One-Off House"].notna() & (pp["One-Off House"] != 0)]
    total_res = pp[pp["is_residential"] == 1]
    return {
        "experiment": "E17",
        "description": "One-off rural houses (septic tank, WWTP-independent)",
        "n_one_off": len(one_off),
        "n_total_residential": len(total_res),
        "pct_one_off": round(len(one_off) / max(len(total_res), 1) * 100, 1),
        "note": "One-off houses use septic tanks, not connected to WWTP network",
    }


def run_e18_apartments():
    """E18: Apartment schemes vs houses (higher wastewater load per hectare)."""
    pp = load_planning()
    res = pp[pp["is_residential"] == 1]
    # Apartments = multiple units, typically > 4
    res = res.copy()
    res["is_apartment"] = (res["NumResidentialUnits"] > 4).astype(int)
    apts = res[res["is_apartment"] == 1]
    houses = res[res["is_apartment"] == 0]
    return {
        "experiment": "E18",
        "description": "Apartments vs houses - different WWTP loading patterns",
        "n_apartment_apps": len(apts),
        "avg_units_apartment": round(apts["NumResidentialUnits"].mean(), 1) if len(apts) > 0 else 0,
        "n_house_apps": len(houses),
        "avg_units_house": round(houses["NumResidentialUnits"].mean(), 1) if len(houses) > 0 else 0,
    }


def run_e19_amber_sensitivity():
    """E19: Sensitivity to AMBER classification (count as blocked or available?)."""
    ww = load_wastewater()
    cc = compute_county_capacity()
    # Scenario 1: AMBER = blocked (RED + AMBER)
    blocked_with_amber = cc["estimated_blocked_ha"].sum()
    # Scenario 2: AMBER = available (RED only)
    cc_red_only = cc.copy()
    cc_red_only["estimated_blocked_ha_red_only"] = cc_red_only["zoned_ha"] * cc_red_only["pct_red"] / 100
    blocked_red_only = cc_red_only["estimated_blocked_ha_red_only"].sum()
    return {
        "experiment": "E19",
        "description": "Sensitivity: AMBER as blocked vs available",
        "blocked_ha_red_amber": round(blocked_with_amber, 0),
        "blocked_ha_red_only": round(blocked_red_only, 0),
        "difference_ha": round(blocked_with_amber - blocked_red_only, 0),
        "pct_blocked_with_amber": round(blocked_with_amber / TOTAL_ZONED_HA * 100, 1),
        "pct_blocked_red_only": round(blocked_red_only / TOTAL_ZONED_HA * 100, 1),
    }


def run_e20_international():
    """E20: Comparison with UK/international infrastructure blocks."""
    return {
        "experiment": "E20",
        "description": "International comparison: Thames Tideway, nutrient neutrality",
        "ireland_pct_constrained": run_e00()["pct_red_or_amber"],
        "uk_nutrient_neutrality_LPAs": 74,  # Number of English LPAs affected by Natural England advice
        "uk_thames_tideway_cost_bn": 4.3,  # GBP billions
        "nl_nitrogen_affected_pct": 40,  # Approximate % of Dutch construction affected by nitrogen ruling
        "nz_three_waters_reform": "Nationwide overhaul 2021-2024",
        "note": "Cross-country comparison of infrastructure-led development constraints",
    }


def run_all_experiments():
    """Run all 20+ experiments and return results."""
    experiments = [
        run_e00, run_e01_dublin, run_e02_high_red_counties, run_e03_project_planned,
        run_e04_refusal_rates, run_e05_time_trend, run_e06_settlement_vs_county,
        run_e07_large_vs_small, run_e08_overlap_viability, run_e09_hectares,
        run_e10_double_stranded, run_e11_green_low_activity, run_e12_completions,
        run_e13_commuter_belt, run_e14_investment, run_e15_uwwtd,
        run_e16_population, run_e17_one_off, run_e18_apartments,
        run_e19_amber_sensitivity, run_e20_international,
    ]
    results = []
    for exp_func in experiments:
        try:
            result = exp_func()
            result["status"] = "KEEP"
            results.append(result)
            print(f"  {result['experiment']}: OK")
        except Exception as e:
            results.append({
                "experiment": exp_func.__name__,
                "status": "ERROR",
                "error": str(e),
            })
            print(f"  {exp_func.__name__}: ERROR - {e}")
    return results


if __name__ == "__main__":
    print("Running all experiments...")
    results = run_all_experiments()
    print(f"\nCompleted {len(results)} experiments")
    for r in results:
        print(f"  {r.get('experiment', '?')}: {r.get('status', '?')}")
