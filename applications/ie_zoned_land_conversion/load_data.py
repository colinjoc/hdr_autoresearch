"""
Data loading utilities for IE Zoned Land Conversion project.
Loads CSO JSON-stat files and the national planning register.
"""
import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

PROJECT_DIR = Path("/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion")
RAW_DIR = PROJECT_DIR / "data" / "raw"
PLANNING_CSV = Path("/home/col/generalized_hdr_autoresearch/applications/ie_lapsed_permissions/data/raw/national_planning_points.csv")

# ── Goodbody Sep-2024 hard-coded figures ──
GOODBODY = {
    "total_zoned_ha": 7911,
    "east_midlands_ha": 2611,  # 33%
    "southern_ha": 2057,       # 26%
    "north_western_ha": 3164,  # 40% (actually ~41% rounding)
    "potential_units": 417000,
    "density_units_per_ha": 53,  # ~417000/7911
    "activation_fraction_per_cycle": 1/6,
    "zoned_2014_ha": 17434,
    "zoned_2024_ha": 7911,
    "fingal_ha": 3519,
}

# ── LA → Region mapping (NUTS 3 → Goodbody regions) ──
# East+Midlands: Dublin (4 LAs), Kildare, Meath, Wicklow, Louth, Laois, Offaly, Westmeath, Longford
# Southern: Cork (2), Kerry, Limerick, Tipperary, Waterford, Wexford, Kilkenny, Carlow, Clare
# Northern+Western: Galway (2), Mayo, Roscommon, Sligo, Leitrim, Donegal, Cavan, Monaghan
LA_REGION = {
    "Dublin City Council": "East+Midlands",
    "Dun Laoghaire Rathdown County Council": "East+Midlands",
    "Fingal County Council": "East+Midlands",
    "South Dublin County Council": "East+Midlands",
    "Kildare County Council": "East+Midlands",
    "Meath County Council": "East+Midlands",
    "Wicklow County Council": "East+Midlands",
    "Louth County Council": "East+Midlands",
    "Laois County Council": "East+Midlands",
    "Offaly County Council": "East+Midlands",
    "Westmeath County Council": "East+Midlands",
    "Longford County Council": "East+Midlands",
    "Cork County Council": "Southern",
    "Cork City Council": "Southern",
    "Kerry County Council": "Southern",
    "Limerick City and County Council": "Southern",
    "Tipperary County Council": "Southern",
    "Waterford City and County Council": "Southern",
    "Wexford County Council": "Southern",
    "Kilkenny County Council": "Southern",
    "Carlow County Council": "Southern",
    "Clare County Council": "Southern",
    "Galway County Council": "Northern+Western",
    "Galway City Council": "Northern+Western",
    "Mayo County Council": "Northern+Western",
    "Roscommon County Council": "Northern+Western",
    "Sligo County Council": "Northern+Western",
    "Leitrim County Council": "Northern+Western",
    "Donegal County Council": "Northern+Western",
    "Cavan County Council": "Northern+Western",
    "Monaghan County Council": "Northern+Western",
}

# Dublin LAs for Dublin vs non-Dublin splits
DUBLIN_LAS = {
    "Dublin City Council",
    "Dun Laoghaire Rathdown County Council",
    "Fingal County Council",
    "South Dublin County Council",
}

# CSO population by LA (Census 2022 approximate)
LA_POPULATION_2022 = {
    "Carlow County Council": 61931,
    "Cavan County Council": 81706,
    "Clare County Council": 127419,
    "Cork City Council": 215904,
    "Cork County Council": 345518,
    "Donegal County Council": 166321,
    "Dublin City Council": 592713,
    "Dun Laoghaire Rathdown County Council": 233860,
    "Fingal County Council": 330506,
    "Galway City Council": 85910,
    "Galway County Council": 179390,
    "Kerry County Council": 156458,
    "Kildare County Council": 247328,
    "Kilkenny County Council": 104160,
    "Laois County Council": 95199,
    "Leitrim County Council": 35583,
    "Limerick City and County Council": 204303,
    "Longford County Council": 46634,
    "Louth County Council": 139703,
    "Mayo County Council": 137970,
    "Meath County Council": 220296,
    "Monaghan County Council": 64832,
    "Offaly County Council": 83045,
    "Roscommon County Council": 70259,
    "Sligo County Council": 70198,
    "South Dublin County Council": 283403,
    "Tipperary County Council": 167895,
    "Waterford City and County Council": 127085,
    "Westmeath County Council": 95840,
    "Wexford County Council": 163919,
    "Wicklow County Council": 155851,
}


def parse_jsonstat(filepath):
    """Parse a CSO JSON-stat 2.0 file into a DataFrame."""
    with open(filepath) as f:
        data = json.load(f)

    dims = data["dimension"]
    dim_order = list(data["role"]["time"]) + [k for k in dims if k not in data["role"].get("time", [])]
    # Use the order from 'id' key
    dim_order = data["id"]

    dim_labels = {}
    dim_keys = {}
    for dim_id in dim_order:
        dim = dims[dim_id]
        cat = dim["category"]
        idx = cat.get("index", {})
        lab = cat.get("label", {})
        if isinstance(idx, dict):
            sorted_keys = sorted(idx.keys(), key=lambda k: idx[k])
        else:
            sorted_keys = list(lab.keys())
        dim_labels[dim_id] = [lab[k] for k in sorted_keys]
        dim_keys[dim_id] = sorted_keys

    # Build multi-index
    import itertools
    combos = list(itertools.product(*[dim_labels[d] for d in dim_order]))

    values = data["value"]
    # Convert sparse dict to list if needed
    if isinstance(values, dict):
        n = 1
        for d in dim_order:
            n *= len(dim_labels[d])
        val_list = [None] * n
        for k, v in values.items():
            val_list[int(k)] = v
        values = val_list

    df = pd.DataFrame(combos, columns=[dims[d]["label"] for d in dim_order])
    df["value"] = values
    return df


def load_bhq01():
    """Load CSO BHQ01 — Planning Permissions by LA by quarter."""
    return parse_jsonstat(RAW_DIR / "BHQ01.json")


def load_rzlpa02():
    """Load CSO RZLPA02 — Residential Zoned Land Prices 2024."""
    return parse_jsonstat(RAW_DIR / "RZLPA02.json")


def load_hpa09():
    """Load CSO HPA09 — Property transactions."""
    return parse_jsonstat(RAW_DIR / "HPA09.json")


def load_planning_register():
    """Load the national planning register as a DataFrame."""
    df = pd.read_csv(PLANNING_CSV, encoding="utf-8-sig", low_memory=False)

    # Parse dates
    date_cols = ["ReceivedDate", "DecisionDate", "GrantDate", "ExpiryDate", "WithdrawnDate"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], format="mixed", dayfirst=False, errors="coerce")

    # Extract year
    df["ReceivedYear"] = df["ReceivedDate"].dt.year

    # Normalize Application Type
    df["AppType_clean"] = df["Application Type"].str.strip().str.upper()

    # Normalize Decision
    df["Decision_clean"] = df["Decision"].str.strip().str.upper()

    # Classify as residential using keywords in description + NumResidentialUnits
    desc = df["Development Description"].fillna("").str.lower()
    nru = pd.to_numeric(df["NumResidentialUnits"], errors="coerce").fillna(0)

    residential_keywords = [
        "dwelling", "house", "apartment", "residential", "home",
        "bungalow", "duplex", "townhouse", "semi-detached", "detached",
        "housing", "flat"
    ]
    has_keyword = desc.apply(lambda x: any(kw in x for kw in residential_keywords))
    df["is_residential"] = (has_keyword | (nru > 0))

    # Classify one-off vs multi-unit
    df["NumResUnits"] = nru
    df["is_one_off"] = (df["One-Off House"].str.strip().str.lower() == "yes") | (nru == 1)
    df["is_multi_unit"] = nru > 1

    # Classify apartment vs house from description
    df["is_apartment"] = desc.str.contains("apartment|flat|duplex", regex=True)
    df["is_house"] = desc.str.contains("house|dwelling|bungalow|semi-detached|detached", regex=True) & ~df["is_apartment"]

    # Grant classification
    grant_decisions = ["CONDITIONAL", "GRANT PERMISSION", "UNCONDITIONAL",
                       "GRANTED (CONDITIONAL)", "GRANT OF PERMISSION",
                       "GRANT OUTLINE PERMISSION", "SPLIT DECISION"]
    df["is_granted"] = df["Decision_clean"].isin(grant_decisions) | df["Decision_clean"].str.contains("GRANT", na=False)

    refuse_decisions = ["REFUSED", "REFUSE PERMISSION", "REFUSE"]
    df["is_refused"] = df["Decision_clean"].isin(refuse_decisions) | df["Decision_clean"].str.contains("REFUSE", na=False)

    # Region mapping
    df["Region"] = df["Planning Authority"].map(LA_REGION)
    df["is_dublin"] = df["Planning Authority"].isin(DUBLIN_LAS)

    return df


def get_planning_by_la_year(df, year_range=(2015, 2025)):
    """Aggregate planning applications by LA and year."""
    mask = (df["ReceivedYear"] >= year_range[0]) & (df["ReceivedYear"] <= year_range[1])
    sub = df[mask].copy()

    # All applications
    all_apps = sub.groupby(["Planning Authority", "ReceivedYear"]).size().reset_index(name="total_applications")

    # Permission applications only
    perm_mask = sub["AppType_clean"].str.contains("PERMISSION", na=False)
    perm_apps = sub[perm_mask].groupby(["Planning Authority", "ReceivedYear"]).size().reset_index(name="permission_applications")

    # Residential applications
    res_mask = sub["is_residential"]
    res_apps = sub[res_mask].groupby(["Planning Authority", "ReceivedYear"]).size().reset_index(name="residential_applications")

    # Residential permission applications
    res_perm = sub[perm_mask & res_mask].groupby(["Planning Authority", "ReceivedYear"]).size().reset_index(name="residential_permission_applications")

    # Granted
    granted = sub[sub["is_granted"]].groupby(["Planning Authority", "ReceivedYear"]).size().reset_index(name="granted")

    # Refused
    refused = sub[sub["is_refused"]].groupby(["Planning Authority", "ReceivedYear"]).size().reset_index(name="refused")

    # Merge
    result = all_apps
    for other in [perm_apps, res_apps, res_perm, granted, refused]:
        result = result.merge(other, on=["Planning Authority", "ReceivedYear"], how="left")

    result = result.fillna(0)
    result["approval_rate"] = result["granted"] / (result["granted"] + result["refused"]).replace(0, np.nan)
    result["Region"] = result["Planning Authority"].map(LA_REGION)
    result["is_dublin"] = result["Planning Authority"].isin(DUBLIN_LAS)

    return result


if __name__ == "__main__":
    print("Loading BHQ01...")
    bhq = load_bhq01()
    print(f"  BHQ01: {bhq.shape}")

    print("Loading RZLPA02...")
    rzl = load_rzlpa02()
    print(f"  RZLPA02: {rzl.shape}")

    print("Loading HPA09...")
    hpa = load_hpa09()
    print(f"  HPA09: {hpa.shape}")

    print("Loading planning register...")
    pl = load_planning_register()
    print(f"  Planning register: {pl.shape}")
    print(f"  Years: {pl['ReceivedYear'].min()} - {pl['ReceivedYear'].max()}")
    print(f"  Residential: {pl['is_residential'].sum()}")

    print("\nAggregating by LA/year...")
    agg = get_planning_by_la_year(pl)
    print(f"  Aggregated: {agg.shape}")
    print(f"  Total residential permission apps (2015-2025):",
          int(agg["residential_permission_applications"].sum()))
