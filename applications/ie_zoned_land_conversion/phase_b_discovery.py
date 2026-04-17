"""
Phase B Discovery: Zoned Land Activation Scenarios and LA Rankings.

Outputs:
  discoveries/application_intensity_by_la.csv — ranked LA intensity
  discoveries/zoned_land_activation_scenarios.csv — counterfactual scenarios
"""
import sys
sys.path.insert(0, "/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion")

import pandas as pd
import numpy as np
from pathlib import Path

from load_data import (
    load_planning_register, get_planning_by_la_year,
    GOODBODY, LA_REGION, DUBLIN_LAS, LA_POPULATION_2022
)

PROJECT_DIR = Path("/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion")
DISC_DIR = PROJECT_DIR / "discoveries"
DISC_DIR.mkdir(exist_ok=True)

# ── Load data ──
print("Loading data for Phase B discovery...")
pl = load_planning_register()
agg = get_planning_by_la_year(pl, year_range=(2015, 2025))

region_ha = {
    "East+Midlands": GOODBODY["east_midlands_ha"],
    "Southern": GOODBODY["southern_ha"],
    "Northern+Western": GOODBODY["north_western_ha"],
}

# Build LA zoned land estimates
region_pop = {}
for la, reg in LA_REGION.items():
    pop = LA_POPULATION_2022.get(la, 0)
    region_pop.setdefault(reg, 0)
    region_pop[reg] += pop

la_zoned = {}
for la, reg in LA_REGION.items():
    pop = LA_POPULATION_2022.get(la, 0)
    rpop = region_pop.get(reg, 1)
    la_zoned[la] = region_ha.get(reg, 0) * pop / rpop
la_zoned["Fingal County Council"] = GOODBODY["fingal_ha"]

# ═══════════════════════════════════════════════════════════
# Discovery 1: Application intensity by LA (ranked)
# ═══════════════════════════════════════════════════════════
print("\n── Discovery 1: LA ranking by application intensity ──")
la_panel = agg[agg["ReceivedYear"].between(2018, 2024)].copy()
la_panel["zoned_ha"] = la_panel["Planning Authority"].map(la_zoned)
la_panel["population"] = la_panel["Planning Authority"].map(LA_POPULATION_2022)
la_panel["apps_per_ha"] = la_panel["residential_permission_applications"] / la_panel["zoned_ha"].replace(0, np.nan)
la_panel["apps_per_1000pop"] = la_panel["residential_permission_applications"] / (la_panel["population"]/1000).replace(0, np.nan)

la_ranked = la_panel.groupby("Planning Authority").agg(
    mean_annual_apps=("residential_permission_applications", "mean"),
    mean_intensity=("apps_per_ha", "mean"),
    mean_per_1000pop=("apps_per_1000pop", "mean"),
    approval_rate=("approval_rate", "mean"),
    zoned_ha_est=("zoned_ha", "first"),
    population=("population", "first"),
    region=("Region", "first"),
).dropna().sort_values("mean_intensity", ascending=False)

la_ranked["rank"] = range(1, len(la_ranked) + 1)
la_ranked = la_ranked[["rank", "region", "mean_intensity", "mean_annual_apps",
                        "zoned_ha_est", "population", "mean_per_1000pop", "approval_rate"]]

la_ranked.to_csv(DISC_DIR / "application_intensity_by_la.csv")
print(f"  Saved {len(la_ranked)} LAs to application_intensity_by_la.csv")
print("\n  Top 5:")
for la, row in la_ranked.head(5).iterrows():
    print(f"    {row['rank']}. {la}: {row['mean_intensity']:.2f} apps/ha/yr")
print("\n  Bottom 5:")
for la, row in la_ranked.tail(5).iterrows():
    print(f"    {row['rank']}. {la}: {row['mean_intensity']:.2f} apps/ha/yr")

# ═══════════════════════════════════════════════════════════
# Discovery 2: Activation scenarios
# ═══════════════════════════════════════════════════════════
print("\n── Discovery 2: Activation scenarios ──")

# Compute regional and national baselines
em_rate = la_panel[la_panel["Region"] == "East+Midlands"].groupby("ReceivedYear")["residential_permission_applications"].sum().mean() / region_ha["East+Midlands"]
southern_rate = la_panel[la_panel["Region"] == "Southern"].groupby("ReceivedYear")["residential_permission_applications"].sum().mean() / region_ha["Southern"]
nw_rate = la_panel[la_panel["Region"] == "Northern+Western"].groupby("ReceivedYear")["residential_permission_applications"].sum().mean() / region_ha["Northern+Western"]
national_rate = la_panel.groupby("ReceivedYear")["residential_permission_applications"].sum().mean() / GOODBODY["total_zoned_ha"]

current_total = la_panel.groupby("ReceivedYear")["residential_permission_applications"].sum().mean()

scenarios = []

# Scenario 1: All regions match East+Midlands rate
s1_total = em_rate * GOODBODY["total_zoned_ha"]
s1_additional = s1_total - current_total
scenarios.append({
    "scenario": "S1: All regions at East+Midlands rate",
    "target_rate": round(em_rate, 2),
    "projected_annual_apps": round(s1_total),
    "additional_apps_vs_current": round(s1_additional),
    "pct_increase": round(s1_additional / current_total * 100, 1),
})

# Scenario 2: All regions match Southern rate (highest)
s2_total = southern_rate * GOODBODY["total_zoned_ha"]
s2_additional = s2_total - current_total
scenarios.append({
    "scenario": "S2: All regions at Southern rate (highest)",
    "target_rate": round(southern_rate, 2),
    "projected_annual_apps": round(s2_total),
    "additional_apps_vs_current": round(s2_additional),
    "pct_increase": round(s2_additional / current_total * 100, 1),
})

# Scenario 3: Northern+Western matches national average
nw_current = nw_rate * region_ha["Northern+Western"]
nw_upgraded = national_rate * region_ha["Northern+Western"]
s3_additional = nw_upgraded - nw_current
s3_total = current_total + s3_additional
scenarios.append({
    "scenario": "S3: N+W catches up to national average",
    "target_rate": round(national_rate, 2),
    "projected_annual_apps": round(s3_total),
    "additional_apps_vs_current": round(s3_additional),
    "pct_increase": round(s3_additional / current_total * 100, 1),
})

# Scenario 4: Fingal rises to East+Midlands average
fingal_current = la_ranked.loc["Fingal County Council", "mean_annual_apps"] if "Fingal County Council" in la_ranked.index else 296
fingal_upgraded = em_rate * GOODBODY["fingal_ha"]
s4_additional = fingal_upgraded - fingal_current
s4_total = current_total + s4_additional
scenarios.append({
    "scenario": "S4: Fingal at East+Midlands rate (3,519 ha)",
    "target_rate": round(em_rate, 2),
    "projected_annual_apps": round(s4_total),
    "additional_apps_vs_current": round(s4_additional),
    "pct_increase": round(s4_additional / current_total * 100, 1),
})

# Scenario 5: RZLT reduces hold-out by 20%
# If 20% of idle land enters pipeline → 20% more applications
s5_additional = current_total * 0.20
s5_total = current_total + s5_additional
scenarios.append({
    "scenario": "S5: RZLT reduces hold-out by 20%",
    "target_rate": round(national_rate * 1.20, 2),
    "projected_annual_apps": round(s5_total),
    "additional_apps_vs_current": round(s5_additional),
    "pct_increase": 20.0,
})

# Scenario 6: Double capacity utilization (8.6% → 17.2%)
s6_total = current_total * 2
s6_additional = current_total
scenarios.append({
    "scenario": "S6: Double capacity utilization (8.6% → 17.2%)",
    "target_rate": round(national_rate * 2, 2),
    "projected_annual_apps": round(s6_total),
    "additional_apps_vs_current": round(s6_additional),
    "pct_increase": 100.0,
})

# Scenario 7: Meet Housing for All target (need 85k perms/yr at 59.6% yield)
target_perms = 85000
# Residential permission apps are a subset; ratio is ~56% of total
# But the target is for total permissions needed
s7_additional = target_perms - current_total
scenarios.append({
    "scenario": "S7: Meet HfA target (85k perms/yr)",
    "target_rate": round(target_perms / GOODBODY["total_zoned_ha"], 2),
    "projected_annual_apps": 85000,
    "additional_apps_vs_current": round(s7_additional),
    "pct_increase": round(s7_additional / current_total * 100, 1),
})

scenarios_df = pd.DataFrame(scenarios)
scenarios_df.to_csv(DISC_DIR / "zoned_land_activation_scenarios.csv", index=False)

print("\nActivation scenarios:")
for _, row in scenarios_df.iterrows():
    print(f"  {row['scenario']}")
    print(f"    Target rate: {row['target_rate']} apps/ha/yr")
    print(f"    Projected annual: {row['projected_annual_apps']:,}")
    print(f"    Additional vs current: {row['additional_apps_vs_current']:+,} ({row['pct_increase']:+.1f}%)")
    print()

# ═══════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE B DISCOVERY SUMMARY")
print("=" * 60)
print(f"\nCurrent national rate: {national_rate:.2f} apps/ha/yr")
print(f"Current annual residential applications: {current_total:,.0f}")
print(f"Annual capacity utilization: {current_total / GOODBODY['potential_units'] * 100 / GOODBODY['density_units_per_ha'] * GOODBODY['density_units_per_ha']:.1f}%")
print(f"\nKey discovery: Fingal County (3,519 ha = 44% of total zoned stock)")
print(f"  has only 0.08 apps/ha/yr vs national 2.72.")
print(f"  If Fingal matched the East+Midlands rate,")
print(f"  that alone would add ~{s4_additional:,.0f} applications per year.")
print(f"\nTo meet Housing for All (85k perms/yr), need {target_perms/GOODBODY['total_zoned_ha']:.1f}x current rate.")
print(f"  This would require {target_perms / GOODBODY['total_zoned_ha']:.2f} apps/ha/yr,")
print(f"  or {(target_perms / current_total - 1)*100:.0f}% increase in application volume.")

print(f"\nOutputs:")
print(f"  {DISC_DIR / 'application_intensity_by_la.csv'}")
print(f"  {DISC_DIR / 'zoned_land_activation_scenarios.csv'}")
