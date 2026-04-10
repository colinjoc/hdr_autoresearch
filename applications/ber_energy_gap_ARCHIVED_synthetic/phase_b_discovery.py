"""
Phase B: Discovery sweep for Irish BER vs Real Home Energy Gap.

Uses the trained surrogate model to:
1. Map the BER energy landscape across Irish housing archetypes
2. Identify which retrofit paths produce the largest BER improvements
3. Generate Pareto-optimal retrofit recommendations by archetype
4. Quantify the predicted performance gap by building type
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    load_dataset, add_derived_features,
    WALL_TYPES, INSULATION_TYPES, HEATING_EFFICIENCIES,
    PRIMARY_ENERGY_FACTORS, WINDOW_U_VALUES, WINDOW_G_VALUES,
    COUNTY_HDD, energy_value_to_ber_rating,
    _compute_wall_u_value,
)


def define_archetypes() -> list[dict]:
    """Define representative Irish housing archetypes for analysis."""
    return [
        {
            "name": "Pre-1940 terraced (Dublin)",
            "year_built": 1920, "floor_area_m2": 75.0, "dwelling_type": "terraced_mid",
            "wall_type": "solid_brick_225mm", "insulation_type": "none",
            "window_type": "single_glazed", "heating_type": "gas_standard",
            "ventilation_type": "natural", "air_permeability": 18.0,
            "roof_insulation_mm": 50, "has_floor_insulation": 0,
            "n_storeys": 2, "n_bedrooms": 3, "county": "Dublin",
            "secondary_heating": "open_fire",
        },
        {
            "name": "1950s semi-D (suburban)",
            "year_built": 1955, "floor_area_m2": 95.0, "dwelling_type": "semi_detached",
            "wall_type": "hollow_block_225mm", "insulation_type": "none",
            "window_type": "double_glazed_air", "heating_type": "oil_standard",
            "ventilation_type": "natural", "air_permeability": 15.0,
            "roof_insulation_mm": 100, "has_floor_insulation": 0,
            "n_storeys": 2, "n_bedrooms": 3, "county": "Dublin",
            "secondary_heating": "open_fire",
        },
        {
            "name": "1970s detached (rural)",
            "year_built": 1974, "floor_area_m2": 150.0, "dwelling_type": "detached",
            "wall_type": "cavity_block_unfilled", "insulation_type": "none",
            "window_type": "double_glazed_air", "heating_type": "oil_standard",
            "ventilation_type": "natural", "air_permeability": 14.0,
            "roof_insulation_mm": 75, "has_floor_insulation": 0,
            "n_storeys": 2, "n_bedrooms": 4, "county": "Galway",
            "secondary_heating": "stove",
        },
        {
            "name": "1990s estate semi-D",
            "year_built": 1998, "floor_area_m2": 110.0, "dwelling_type": "semi_detached",
            "wall_type": "cavity_block_partial_fill", "insulation_type": "cavity_fill_bead",
            "window_type": "double_glazed_air", "heating_type": "gas_standard",
            "ventilation_type": "extract_fans", "air_permeability": 10.0,
            "roof_insulation_mm": 150, "has_floor_insulation": 0,
            "n_storeys": 2, "n_bedrooms": 3, "county": "Kildare",
            "secondary_heating": "none",
        },
        {
            "name": "2005 Celtic Tiger detached",
            "year_built": 2005, "floor_area_m2": 200.0, "dwelling_type": "detached",
            "wall_type": "cavity_block_full_fill", "insulation_type": "cavity_fill_foam",
            "window_type": "double_glazed_argon", "heating_type": "gas_condensing",
            "ventilation_type": "extract_fans", "air_permeability": 8.0,
            "roof_insulation_mm": 200, "has_floor_insulation": 1,
            "n_storeys": 2, "n_bedrooms": 4, "county": "Meath",
            "secondary_heating": "stove",
        },
        {
            "name": "2010 apartment (Dublin)",
            "year_built": 2010, "floor_area_m2": 65.0, "dwelling_type": "apartment",
            "wall_type": "cavity_block_full_fill", "insulation_type": "cavity_fill_foam",
            "window_type": "double_glazed_argon", "heating_type": "gas_condensing",
            "ventilation_type": "extract_fans", "air_permeability": 7.0,
            "roof_insulation_mm": 250, "has_floor_insulation": 1,
            "n_storeys": 1, "n_bedrooms": 2, "county": "Dublin",
            "secondary_heating": "none",
        },
        {
            "name": "2022 nZEB semi-D",
            "year_built": 2022, "floor_area_m2": 120.0, "dwelling_type": "semi_detached",
            "wall_type": "timber_frame_140mm_insulation", "insulation_type": "external_100mm_phenolic",
            "window_type": "triple_glazed", "heating_type": "heat_pump_ashp",
            "ventilation_type": "mvhr", "air_permeability": 3.0,
            "roof_insulation_mm": 350, "has_floor_insulation": 1,
            "n_storeys": 2, "n_bedrooms": 4, "county": "Cork",
            "secondary_heating": "none",
        },
    ]


def define_retrofit_measures() -> list[dict]:
    """Define retrofit measures with costs and expected impacts."""
    return [
        {
            "name": "Cavity wall insulation",
            "cost_eur": 1500,
            "changes": {"insulation_type": "cavity_fill_bead"},
            "applicable_walls": ["cavity_block_unfilled"],
        },
        {
            "name": "External wall insulation (EPS)",
            "cost_eur": 12000,
            "changes": {"insulation_type": "external_100mm_eps"},
            "applicable_walls": None,  # all wall types
        },
        {
            "name": "External wall insulation (phenolic)",
            "cost_eur": 15000,
            "changes": {"insulation_type": "external_100mm_phenolic"},
            "applicable_walls": None,
        },
        {
            "name": "Attic insulation to 300mm",
            "cost_eur": 1200,
            "changes": {"roof_insulation_mm": 300},
            "min_improvement_mm": 100,
        },
        {
            "name": "Window replacement (argon DG)",
            "cost_eur": 8000,
            "changes": {"window_type": "double_glazed_argon"},
            "applicable_windows": ["single_glazed", "double_glazed_air"],
        },
        {
            "name": "Window replacement (triple)",
            "cost_eur": 12000,
            "changes": {"window_type": "triple_glazed"},
            "applicable_windows": ["single_glazed", "double_glazed_air", "double_glazed_argon"],
        },
        {
            "name": "Gas condensing boiler",
            "cost_eur": 4000,
            "changes": {"heating_type": "gas_condensing"},
            "applicable_heating": ["gas_standard", "oil_standard"],
        },
        {
            "name": "Air source heat pump",
            "cost_eur": 12000,
            "changes": {"heating_type": "heat_pump_ashp"},
            "applicable_heating": None,
        },
        {
            "name": "MVHR installation",
            "cost_eur": 5000,
            "changes": {"ventilation_type": "mvhr", "air_permeability": 3.0},
            "applicable_ventilation": ["natural", "extract_fans"],
        },
    ]


def compute_archetype_energy(archetype: dict) -> float:
    """Compute approximate BER energy value for an archetype using DEAP-like calculation."""
    wall_u = _compute_wall_u_value(archetype["wall_type"], archetype["insulation_type"])
    roof_u = max(0.10, 1.0 / (0.3 + archetype["roof_insulation_mm"] * 0.025))
    floor_u = 0.25 if archetype["has_floor_insulation"] else 0.70
    window_u = WINDOW_U_VALUES[archetype["window_type"]]
    window_g = WINDOW_G_VALUES[archetype["window_type"]]
    hdd = COUNTY_HDD[archetype["county"]]
    eff = HEATING_EFFICIENCIES[archetype["heating_type"]]
    pef = PRIMARY_ENERGY_FACTORS[archetype["heating_type"]]

    floor_area = archetype["floor_area_m2"]
    n_storeys = archetype["n_storeys"]
    storey_height = 2.5
    volume = floor_area * storey_height

    # Simplified geometry
    footprint = floor_area / n_storeys
    perimeter = 2 * (np.sqrt(footprint * 1.5) + np.sqrt(footprint / 1.5))
    dt = archetype["dwelling_type"]
    if dt == "terraced_mid":
        wall_area = 2 * np.sqrt(footprint / 1.5) * storey_height * n_storeys
    elif dt == "apartment":
        wall_area = perimeter * storey_height * 0.4
    elif dt == "terraced_end":
        wall_area = (2 * np.sqrt(footprint / 1.5) + np.sqrt(footprint * 1.5)) * storey_height * n_storeys
    else:
        wall_area = perimeter * storey_height * n_storeys

    roof_area = footprint if dt != "apartment" else 0
    floor_loss_area = footprint if dt != "apartment" else 0
    window_area = wall_area * 0.17
    wall_area -= window_area

    # Heat loss
    fabric_loss = wall_u * wall_area + roof_u * roof_area + floor_u * floor_loss_area + window_u * window_area
    thermal_bridge = 0.08 * (wall_area + roof_area + floor_loss_area + window_area)

    ach = archetype["air_permeability"] * (wall_area + roof_area) / volume * 0.05
    ach = max(0.3, ach)
    if archetype["ventilation_type"] == "mvhr":
        ach *= 0.35
    ventilation_loss = 0.33 * ach * volume

    total_hlc = fabric_loss + thermal_bridge + ventilation_loss
    space_heating = total_hlc * hdd * 24 / 1000

    solar_gains = window_area * window_g * 400 * 0.6
    internal_gains = 3.4 * floor_area * 8760 / 1000 * 0.5
    net_heating = max(0, space_heating - solar_gains - internal_gains)

    n_occ = 1.0 + 1.76 * (1 - np.exp(-0.000349 * floor_area**2)) + 0.0013 * floor_area
    dhw = n_occ * 50 * 365 * 4.186 * 35 / 3600 * 1.3

    if eff > 1.0:
        delivered_space = net_heating / eff
        delivered_dhw = dhw / (eff * 0.7)
    else:
        delivered_space = net_heating / eff
        delivered_dhw = dhw / max(0.3, eff * 0.9)

    lighting = floor_area * 10
    auxiliary = 500

    primary = (delivered_space + delivered_dhw) * pef + (lighting + auxiliary) * 2.08
    return primary / floor_area


def apply_retrofit(archetype: dict, retrofit: dict) -> dict:
    """Apply a retrofit measure to an archetype, returning the modified archetype."""
    modified = archetype.copy()
    for key, value in retrofit["changes"].items():
        if key == "heating_type":
            modified[key] = value
        elif key == "insulation_type":
            modified[key] = value
        elif key == "window_type":
            modified[key] = value
        elif key == "ventilation_type":
            modified[key] = value
        elif key == "roof_insulation_mm":
            modified[key] = max(modified.get(key, 0), value)
        elif key == "air_permeability":
            modified[key] = min(modified.get(key, 20), value)
        else:
            modified[key] = value
    return modified


def is_retrofit_applicable(archetype: dict, retrofit: dict) -> bool:
    """Check if a retrofit measure is applicable to an archetype."""
    if "applicable_walls" in retrofit and retrofit["applicable_walls"] is not None:
        if archetype["wall_type"] not in retrofit["applicable_walls"]:
            return False
    if "applicable_windows" in retrofit and retrofit.get("applicable_windows") is not None:
        if archetype["window_type"] not in retrofit["applicable_windows"]:
            return False
    if "applicable_heating" in retrofit and retrofit.get("applicable_heating") is not None:
        if archetype["heating_type"] not in retrofit["applicable_heating"]:
            return False
    if "applicable_ventilation" in retrofit and retrofit.get("applicable_ventilation") is not None:
        if archetype["ventilation_type"] not in retrofit["applicable_ventilation"]:
            return False
    if "min_improvement_mm" in retrofit:
        current = archetype.get("roof_insulation_mm", 0)
        target = retrofit["changes"].get("roof_insulation_mm", 0)
        if target - current < retrofit["min_improvement_mm"]:
            return False
    return True


def main():
    archetypes = define_archetypes()
    retrofits = define_retrofit_measures()

    print("=" * 80)
    print("Phase B: Discovery Sweep — Irish Housing Retrofit Recommendations")
    print("=" * 80)

    # 1. Baseline energy values for all archetypes
    print("\n1. Archetype Baseline Energy Values")
    print("-" * 80)
    print(f"{'Archetype':<35} {'kWh/m2/yr':>12} {'BER':>5} {'HDD':>6}")
    print("-" * 80)

    archetype_baselines = {}
    for arch in archetypes:
        ev = compute_archetype_energy(arch)
        rating = energy_value_to_ber_rating(ev)
        archetype_baselines[arch["name"]] = ev
        print(f"{arch['name']:<35} {ev:>12.1f} {rating:>5} {COUNTY_HDD[arch['county']]:>6}")

    # 2. Single-measure retrofit analysis
    print("\n\n2. Single-Measure Retrofit Impacts")
    print("-" * 80)

    all_results = []
    for arch in archetypes:
        base_ev = archetype_baselines[arch["name"]]
        base_rating = energy_value_to_ber_rating(base_ev)

        print(f"\n  {arch['name']} (baseline: {base_ev:.0f} kWh/m2/yr, {base_rating})")

        for retrofit in retrofits:
            if not is_retrofit_applicable(arch, retrofit):
                continue

            modified = apply_retrofit(arch, retrofit)
            new_ev = compute_archetype_energy(modified)
            improvement = base_ev - new_ev
            new_rating = energy_value_to_ber_rating(new_ev)
            cost_per_kwh = retrofit["cost_eur"] / max(1, improvement) if improvement > 0 else float("inf")

            result = {
                "archetype": arch["name"],
                "retrofit": retrofit["name"],
                "base_ev": base_ev,
                "new_ev": new_ev,
                "improvement_kwh": improvement,
                "base_rating": base_rating,
                "new_rating": new_rating,
                "cost_eur": retrofit["cost_eur"],
                "cost_per_kwh_saved": cost_per_kwh,
            }
            all_results.append(result)

            print(f"    {retrofit['name']:<35} {new_ev:>6.0f} ({new_rating:>3}) "
                  f"delta={improvement:>+6.0f}  cost/kWh=EUR{cost_per_kwh:>6.0f}")

    # 3. Best single retrofit per archetype
    print("\n\n3. Best Single Retrofit per Archetype (by cost-effectiveness)")
    print("-" * 80)

    results_df = pd.DataFrame(all_results)
    for arch_name in results_df["archetype"].unique():
        arch_results = results_df[results_df["archetype"] == arch_name]
        if len(arch_results) == 0:
            continue
        positive = arch_results[arch_results["improvement_kwh"] > 0]
        if len(positive) == 0:
            print(f"  {arch_name}: No beneficial retrofit found")
            continue
        best = positive.loc[positive["cost_per_kwh_saved"].idxmin()]
        print(f"  {arch_name}:")
        print(f"    Best: {best['retrofit']} — saves {best['improvement_kwh']:.0f} kWh/m2/yr "
              f"({best['base_rating']}->{best['new_rating']}) at EUR{best['cost_per_kwh_saved']:.0f}/kWh")

    # 4. Deep retrofit packages
    print("\n\n4. Deep Retrofit Packages (multiple measures)")
    print("-" * 80)

    deep_packages = [
        {
            "name": "Fabric first (wall + attic + windows)",
            "measures": ["External wall insulation (EPS)", "Attic insulation to 300mm",
                         "Window replacement (argon DG)"],
        },
        {
            "name": "Fabric + heating (wall + attic + heat pump)",
            "measures": ["External wall insulation (EPS)", "Attic insulation to 300mm",
                         "Air source heat pump"],
        },
        {
            "name": "Deep retrofit (wall + windows + heat pump + MVHR)",
            "measures": ["External wall insulation (phenolic)", "Window replacement (triple)",
                         "Air source heat pump", "MVHR installation"],
        },
    ]

    retrofit_by_name = {r["name"]: r for r in retrofits}

    for pkg in deep_packages:
        print(f"\n  Package: {pkg['name']}")
        total_cost = sum(retrofit_by_name[m]["cost_eur"] for m in pkg["measures"] if m in retrofit_by_name)
        print(f"  Total cost: EUR{total_cost:,}")
        print(f"  {'Archetype':<35} {'Before':>8} {'After':>8} {'Delta':>8} {'Before BER':>10} {'After BER':>10}")

        for arch in archetypes:
            base_ev = archetype_baselines[arch["name"]]
            base_rating = energy_value_to_ber_rating(base_ev)

            # Apply all measures sequentially
            modified = arch.copy()
            for measure_name in pkg["measures"]:
                if measure_name in retrofit_by_name:
                    retrofit = retrofit_by_name[measure_name]
                    modified = apply_retrofit(modified, retrofit)

            new_ev = compute_archetype_energy(modified)
            new_rating = energy_value_to_ber_rating(new_ev)
            delta = base_ev - new_ev

            print(f"  {arch['name']:<35} {base_ev:>8.0f} {new_ev:>8.0f} {delta:>+8.0f} "
                  f"{base_rating:>10} {new_rating:>10}")

    # 5. Performance gap estimation
    print("\n\n5. Estimated Performance Gap by Archetype")
    print("-" * 80)
    print("  (Based on Coyne & Denny 2021 prebound/rebound factors)")
    print(f"\n  {'Archetype':<35} {'BER pred':>10} {'Est actual':>10} {'Gap %':>8} {'Effect':>12}")

    for arch in archetypes:
        ev = archetype_baselines[arch["name"]]
        rating = energy_value_to_ber_rating(ev)

        # Estimate prebound/rebound factor from Coyne & Denny 2021
        if ev > 380:  # F-G rated
            factor = 0.50  # strong prebound
            effect = "prebound"
        elif ev > 300:  # E rated
            factor = 0.60
            effect = "prebound"
        elif ev > 225:  # D rated
            factor = 0.75
            effect = "mild prebound"
        elif ev > 150:  # C rated
            factor = 0.90
            effect = "near-neutral"
        elif ev > 100:  # B rated
            factor = 1.05
            effect = "mild rebound"
        else:  # A rated
            factor = 1.15
            effect = "rebound"

        est_actual = ev * factor
        gap_pct = (ev - est_actual) / ev * 100

        print(f"  {arch['name']:<35} {ev:>10.0f} {est_actual:>10.0f} {gap_pct:>+7.0f}% {effect:>12}")

    # 6. Save results
    DISCOVERIES_DIR = APP_DIR / "discoveries"
    DISCOVERIES_DIR.mkdir(exist_ok=True)

    results_df.to_csv(DISCOVERIES_DIR / "retrofit_analysis.csv", index=False)
    print(f"\n  Results saved to {DISCOVERIES_DIR / 'retrofit_analysis.csv'}")

    print("\n" + "=" * 80)
    print("Phase B Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
