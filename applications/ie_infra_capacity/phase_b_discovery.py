"""
Phase B Discovery: U-3 Infrastructure Capacity Blocks

Outputs:
  discoveries/blocked_hectares_by_county.csv
  discoveries/infrastructure_investment_priorities.csv

These are the actionable discovery outputs of the study.
"""
import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis import (
    load_wastewater, compute_county_capacity, merge_planning_with_capacity,
    TOTAL_ZONED_HA, ZONED_HA_BY_COUNTY
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DISC_DIR = os.path.join(PROJECT_DIR, "discoveries")
os.makedirs(DISC_DIR, exist_ok=True)


def generate_blocked_hectares():
    """
    Discovery 1: Estimated hectares of zoned residential land blocked
    by wastewater infrastructure constraints, by county.
    """
    cc = compute_county_capacity()

    # Add RED-only scenario
    cc["blocked_ha_red_only"] = cc["zoned_ha"] * cc["pct_red"] / 100
    cc["blocked_ha_red_amber"] = cc["estimated_blocked_ha"]

    # Add context columns
    cc["pct_of_national_zoned"] = cc["zoned_ha"] / TOTAL_ZONED_HA * 100
    cc["pct_of_county_zoned_blocked"] = cc["pct_red_or_amber"]

    # Sort by blocked hectares descending
    out = cc[[
        "county", "n_wwtp", "n_green", "n_amber", "n_red",
        "pct_green", "pct_amber", "pct_red", "pct_red_or_amber",
        "zoned_ha", "blocked_ha_red_only", "blocked_ha_red_amber",
        "pct_of_national_zoned", "pct_of_county_zoned_blocked",
        "n_project",
    ]].sort_values("blocked_ha_red_amber", ascending=False)

    # Round
    for col in ["pct_green", "pct_amber", "pct_red", "pct_red_or_amber",
                "blocked_ha_red_only", "blocked_ha_red_amber",
                "pct_of_national_zoned", "pct_of_county_zoned_blocked"]:
        out[col] = out[col].round(1)

    # Add national total row
    national = pd.DataFrame([{
        "county": "NATIONAL TOTAL",
        "n_wwtp": out["n_wwtp"].sum(),
        "n_green": out["n_green"].sum(),
        "n_amber": out["n_amber"].sum(),
        "n_red": out["n_red"].sum(),
        "pct_green": round(out["n_green"].sum() / out["n_wwtp"].sum() * 100, 1),
        "pct_amber": round(out["n_amber"].sum() / out["n_wwtp"].sum() * 100, 1),
        "pct_red": round(out["n_red"].sum() / out["n_wwtp"].sum() * 100, 1),
        "pct_red_or_amber": round((out["n_red"].sum() + out["n_amber"].sum()) / out["n_wwtp"].sum() * 100, 1),
        "zoned_ha": TOTAL_ZONED_HA,
        "blocked_ha_red_only": round(out["blocked_ha_red_only"].sum(), 1),
        "blocked_ha_red_amber": round(out["blocked_ha_red_amber"].sum(), 1),
        "pct_of_national_zoned": 100.0,
        "pct_of_county_zoned_blocked": round((out["n_red"].sum() + out["n_amber"].sum()) / out["n_wwtp"].sum() * 100, 1),
        "n_project": out["n_project"].sum(),
    }])
    out = pd.concat([out, national], ignore_index=True)

    path = os.path.join(DISC_DIR, "blocked_hectares_by_county.csv")
    out.to_csv(path, index=False)
    print(f"  Saved {path}")
    print(f"  National total: {out.iloc[-1]['blocked_ha_red_amber']} ha blocked (RED+AMBER)")
    print(f"  National total: {out.iloc[-1]['blocked_ha_red_only']} ha blocked (RED only)")
    return out


def generate_investment_priorities():
    """
    Discovery 2: Which WWTP upgrades would unlock the most zoned land?
    Ranking by estimated impact on housing capacity.
    """
    ww = load_wastewater()
    cc = compute_county_capacity()

    # Focus on RED and AMBER plants
    constrained = ww[ww["is_red_or_amber"] == 1].copy()

    # For each constrained plant, estimate the hectares it blocks
    # Assumption: each plant's share of blocked land = 1 / n_constrained_in_county * county_blocked_ha
    county_blocked = cc.set_index("county")[["estimated_blocked_ha", "n_red", "n_amber"]].to_dict("index")

    def estimate_plant_blocked_ha(row):
        county = row["county_canonical"]
        if county in county_blocked:
            info = county_blocked[county]
            n_constrained = info["n_red"] + info["n_amber"]
            if n_constrained > 0:
                return info["estimated_blocked_ha"] / n_constrained
        return 0.0

    constrained["estimated_blocked_ha"] = constrained.apply(estimate_plant_blocked_ha, axis=1)
    constrained["has_project_flag"] = constrained["has_project"].map({1: "Yes", 0: "No"})

    # Priority score: blocked hectares weighted by whether there's no project (more urgent)
    constrained["priority_score"] = constrained["estimated_blocked_ha"] * (2 - constrained["has_project"])

    out = constrained[[
        "county_canonical", "settlement", "wwtp", "reg_no", "capacity",
        "has_project_flag", "estimated_blocked_ha", "priority_score"
    ]].sort_values("priority_score", ascending=False).copy()

    out.columns = [
        "county", "settlement", "wwtp_name", "registration_no", "capacity_status",
        "upgrade_project_planned", "estimated_blocked_ha", "priority_score"
    ]

    for col in ["estimated_blocked_ha", "priority_score"]:
        out[col] = out[col].round(2)

    path = os.path.join(DISC_DIR, "infrastructure_investment_priorities.csv")
    out.to_csv(path, index=False)
    print(f"  Saved {path}")
    print(f"  Top 10 priority plants:")
    print(out.head(10)[["county", "settlement", "capacity_status", "upgrade_project_planned",
                         "estimated_blocked_ha", "priority_score"]].to_string(index=False))
    return out


if __name__ == "__main__":
    print("Phase B Discovery: U-3 Infrastructure Capacity Blocks")
    print("=" * 60)
    print("\nDiscovery 1: Blocked hectares by county")
    blocked = generate_blocked_hectares()
    print(f"\nDiscovery 2: Investment priorities")
    priorities = generate_investment_priorities()
    print(f"\nPhase B complete. Outputs in {DISC_DIR}/")
