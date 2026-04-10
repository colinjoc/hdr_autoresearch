"""
Data loaders for Irish BER vs Real Home Energy Gap analysis.

Generates calibrated synthetic BER certificate data matching published SEAI summary
statistics, since the full SEAI BER Research Tool requires manual export or research
agreement access. The synthetic data captures the statistical properties documented
in SEAI annual BER reports, Moran et al. 2017, and Ahern & Norton 2019/2020.

Usage:
    python data_loaders.py                 # Generate dataset and save to parquet
    python data_loaders.py --info          # Print dataset summary statistics
    python data_loaders.py --force         # Regenerate from scratch
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
PARQUET_FILE = DATA_DIR / "ber_certificates.parquet"
METADATA_FILE = DATA_DIR / "dataset_metadata.json"

# ============================================================================
# Constants calibrated to published SEAI BER statistics
# ============================================================================

COUNTIES = [
    "Carlow", "Cavan", "Clare", "Cork", "Donegal", "Dublin", "Galway",
    "Kerry", "Kildare", "Kilkenny", "Laois", "Leitrim", "Limerick",
    "Longford", "Louth", "Mayo", "Meath", "Monaghan", "Offaly",
    "Roscommon", "Sligo", "Tipperary", "Waterford", "Westmeath",
    "Wexford", "Wicklow",
]

# County weights (approximate proportional to housing stock)
COUNTY_WEIGHTS = {
    "Dublin": 0.28, "Cork": 0.12, "Galway": 0.06, "Limerick": 0.05,
    "Kildare": 0.05, "Meath": 0.05, "Wexford": 0.03, "Kerry": 0.03,
    "Donegal": 0.03, "Tipperary": 0.03, "Mayo": 0.03, "Wicklow": 0.03,
    "Louth": 0.02, "Kilkenny": 0.02, "Waterford": 0.02, "Westmeath": 0.02,
    "Clare": 0.02, "Laois": 0.02, "Offaly": 0.01, "Cavan": 0.01,
    "Sligo": 0.01, "Roscommon": 0.01, "Monaghan": 0.01, "Carlow": 0.01,
    "Longford": 0.01, "Leitrim": 0.005,
}

# Heating Degree Days by county (approximate, base 15.5C)
COUNTY_HDD = {
    "Dublin": 2350, "Cork": 2250, "Galway": 2450, "Limerick": 2300,
    "Kildare": 2400, "Meath": 2450, "Wexford": 2200, "Kerry": 2150,
    "Donegal": 2600, "Tipperary": 2350, "Mayo": 2550, "Wicklow": 2400,
    "Louth": 2400, "Kilkenny": 2300, "Waterford": 2200, "Westmeath": 2450,
    "Clare": 2350, "Laois": 2400, "Offaly": 2400, "Cavan": 2550,
    "Sligo": 2500, "Roscommon": 2500, "Monaghan": 2550, "Carlow": 2350,
    "Longford": 2500, "Leitrim": 2600,
}

# County radon risk (high-risk fraction from EPA radon map)
COUNTY_RADON_RISK = {
    "Dublin": 0.05, "Cork": 0.08, "Galway": 0.15, "Limerick": 0.06,
    "Kildare": 0.07, "Meath": 0.06, "Wexford": 0.04, "Kerry": 0.12,
    "Donegal": 0.10, "Tipperary": 0.08, "Mayo": 0.12, "Wicklow": 0.20,
    "Louth": 0.05, "Kilkenny": 0.06, "Waterford": 0.05, "Westmeath": 0.07,
    "Clare": 0.10, "Laois": 0.06, "Offaly": 0.07, "Cavan": 0.09,
    "Sligo": 0.11, "Roscommon": 0.09, "Monaghan": 0.08, "Carlow": 0.06,
    "Longford": 0.07, "Leitrim": 0.10,
}

# Gas network availability by county (fraction of dwellings with gas access)
COUNTY_GAS_AVAILABLE = {
    "Dublin": 0.80, "Cork": 0.55, "Galway": 0.40, "Limerick": 0.50,
    "Kildare": 0.55, "Meath": 0.45, "Wexford": 0.25, "Kerry": 0.10,
    "Donegal": 0.05, "Tipperary": 0.20, "Mayo": 0.05, "Wicklow": 0.40,
    "Louth": 0.45, "Kilkenny": 0.25, "Waterford": 0.35, "Westmeath": 0.30,
    "Clare": 0.15, "Laois": 0.20, "Offaly": 0.15, "Cavan": 0.10,
    "Sligo": 0.15, "Roscommon": 0.05, "Monaghan": 0.05, "Carlow": 0.20,
    "Longford": 0.10, "Leitrim": 0.05,
}

# Wall types and their base U-values (W/m2K) without additional insulation
WALL_TYPES = {
    "solid_stone_300mm": 2.10,
    "solid_stone_450mm": 1.80,
    "solid_stone_600mm": 1.55,
    "solid_brick_225mm": 2.10,
    "solid_brick_330mm": 1.70,
    "hollow_block_225mm": 1.70,
    "hollow_block_300mm": 1.50,
    "cavity_block_unfilled": 1.10,
    "cavity_block_partial_fill": 0.55,
    "cavity_block_full_fill": 0.35,
    "timber_frame_uninsulated": 1.50,
    "timber_frame_90mm_insulation": 0.40,
    "timber_frame_140mm_insulation": 0.27,
    "steel_frame_insulated": 0.35,
    "insulated_concrete_form": 0.20,
}

# Insulation types and their additional R-values (m2K/W)
INSULATION_TYPES = {
    "none": 0.0,
    "dry_lining_25mm": 0.6,
    "dry_lining_50mm": 1.2,
    "cavity_fill_bead": 1.5,
    "cavity_fill_foam": 1.8,
    "external_100mm_eps": 2.5,
    "external_100mm_phenolic": 4.5,
    "internal_50mm_pir": 2.3,
    "internal_100mm_pir": 4.5,
}

DWELLING_TYPES = ["detached", "semi_detached", "terraced_end", "terraced_mid", "apartment"]
DWELLING_TYPE_WEIGHTS = [0.30, 0.28, 0.10, 0.15, 0.17]

WINDOW_TYPES = ["single_glazed", "double_glazed_air", "double_glazed_argon", "triple_glazed"]
WINDOW_U_VALUES = {"single_glazed": 4.8, "double_glazed_air": 2.8, "double_glazed_argon": 1.6, "triple_glazed": 0.8}
WINDOW_G_VALUES = {"single_glazed": 0.85, "double_glazed_air": 0.72, "double_glazed_argon": 0.63, "triple_glazed": 0.50}

HEATING_TYPES = [
    "oil_standard", "oil_condensing", "gas_standard", "gas_condensing",
    "solid_fuel_open_fire", "solid_fuel_stove", "solid_fuel_boiler",
    "electric_storage", "electric_panel", "heat_pump_ashp", "heat_pump_gshp",
]
HEATING_EFFICIENCIES = {
    "oil_standard": 0.82, "oil_condensing": 0.92,
    "gas_standard": 0.80, "gas_condensing": 0.92,
    "solid_fuel_open_fire": 0.30, "solid_fuel_stove": 0.60, "solid_fuel_boiler": 0.65,
    "electric_storage": 1.00, "electric_panel": 1.00,
    "heat_pump_ashp": 3.20, "heat_pump_gshp": 3.80,
}
PRIMARY_ENERGY_FACTORS = {
    "oil_standard": 1.1, "oil_condensing": 1.1,
    "gas_standard": 1.1, "gas_condensing": 1.1,
    "solid_fuel_open_fire": 1.0, "solid_fuel_stove": 1.0, "solid_fuel_boiler": 1.0,
    "electric_storage": 2.08, "electric_panel": 2.08,
    "heat_pump_ashp": 2.08, "heat_pump_gshp": 2.08,
}

VENTILATION_TYPES = ["natural", "extract_fans", "balanced_no_hr", "mvhr"]

# BER rating bands (kWh/m2/yr thresholds)
BER_BANDS = {
    "A1": (0, 25), "A2": (25, 50), "A3": (50, 75),
    "B1": (75, 100), "B2": (100, 125), "B3": (125, 150),
    "C1": (150, 175), "C2": (175, 200), "C3": (200, 225),
    "D1": (225, 260), "D2": (260, 300),
    "E1": (300, 340), "E2": (340, 380),
    "F": (380, 450), "G": (450, 9999),
}


def energy_value_to_ber_rating(ev: float) -> str:
    """Convert energy value (kWh/m2/yr) to BER letter grade."""
    for rating, (lo, hi) in BER_BANDS.items():
        if lo <= ev < hi:
            return rating
    return "G"


# ============================================================================
# Synthetic data generator
# ============================================================================

def _get_wall_type_for_era(year: int, dwelling_type: str, rng: np.random.Generator) -> tuple[str, str]:
    """Return (wall_type, insulation_type) based on construction era and dwelling type."""
    if year < 1940:
        wt = rng.choice(["solid_stone_300mm", "solid_stone_450mm", "solid_stone_600mm", "solid_brick_225mm"],
                        p=[0.25, 0.30, 0.20, 0.25])
        ins = rng.choice(["none", "dry_lining_25mm"], p=[0.75, 0.25])
    elif year < 1967:
        wt = rng.choice(["solid_brick_225mm", "solid_brick_330mm", "hollow_block_225mm", "hollow_block_300mm"],
                        p=[0.20, 0.20, 0.35, 0.25])
        ins = rng.choice(["none", "dry_lining_25mm", "dry_lining_50mm"], p=[0.60, 0.25, 0.15])
    elif year < 1978:
        wt = rng.choice(["hollow_block_300mm", "cavity_block_unfilled", "cavity_block_partial_fill"],
                        p=[0.30, 0.50, 0.20])
        ins = rng.choice(["none", "dry_lining_25mm", "cavity_fill_bead"], p=[0.50, 0.30, 0.20])
    elif year < 1992:
        wt = rng.choice(["cavity_block_unfilled", "cavity_block_partial_fill", "cavity_block_full_fill"],
                        p=[0.30, 0.45, 0.25])
        ins = rng.choice(["none", "dry_lining_25mm", "cavity_fill_bead", "cavity_fill_foam"],
                        p=[0.20, 0.25, 0.35, 0.20])
    elif year < 2006:
        wt = rng.choice(["cavity_block_partial_fill", "cavity_block_full_fill", "timber_frame_90mm_insulation"],
                        p=[0.30, 0.50, 0.20])
        ins = rng.choice(["cavity_fill_bead", "cavity_fill_foam", "dry_lining_50mm"],
                        p=[0.40, 0.40, 0.20])
    elif year < 2019:
        wt = rng.choice(["cavity_block_full_fill", "timber_frame_140mm_insulation", "timber_frame_90mm_insulation"],
                        p=[0.50, 0.30, 0.20])
        ins = rng.choice(["cavity_fill_foam", "external_100mm_eps", "external_100mm_phenolic"],
                        p=[0.50, 0.30, 0.20])
    else:  # nZEB era
        wt = rng.choice(["timber_frame_140mm_insulation", "insulated_concrete_form", "cavity_block_full_fill"],
                        p=[0.40, 0.30, 0.30])
        ins = rng.choice(["external_100mm_phenolic", "external_100mm_eps", "cavity_fill_foam"],
                        p=[0.50, 0.30, 0.20])
    return wt, ins


def _get_heating_type(year: int, county: str, rng: np.random.Generator) -> str:
    """Return heating system type based on era, county (gas availability), and randomness."""
    gas_avail = COUNTY_GAS_AVAILABLE[county]
    has_gas = rng.random() < gas_avail

    if year >= 2019:
        if has_gas:
            return rng.choice(["gas_condensing", "heat_pump_ashp"], p=[0.40, 0.60])
        return rng.choice(["heat_pump_ashp", "heat_pump_gshp", "oil_condensing"],
                          p=[0.50, 0.20, 0.30])
    elif year >= 2010:
        if has_gas:
            return rng.choice(["gas_condensing", "gas_standard", "heat_pump_ashp"],
                              p=[0.60, 0.25, 0.15])
        return rng.choice(["oil_condensing", "oil_standard", "heat_pump_ashp", "solid_fuel_stove"],
                          p=[0.40, 0.30, 0.15, 0.15])
    elif year >= 1992:
        if has_gas:
            return rng.choice(["gas_standard", "gas_condensing", "electric_storage"],
                              p=[0.55, 0.30, 0.15])
        return rng.choice(["oil_standard", "oil_condensing", "solid_fuel_stove", "solid_fuel_boiler"],
                          p=[0.40, 0.25, 0.20, 0.15])
    elif year >= 1967:
        if has_gas:
            return rng.choice(["gas_standard", "oil_standard", "solid_fuel_boiler"],
                              p=[0.45, 0.30, 0.25])
        return rng.choice(["oil_standard", "solid_fuel_boiler", "solid_fuel_stove",
                           "solid_fuel_open_fire"],
                          p=[0.40, 0.25, 0.20, 0.15])
    else:
        if has_gas:
            return rng.choice(["gas_standard", "solid_fuel_open_fire", "oil_standard"],
                              p=[0.30, 0.40, 0.30])
        return rng.choice(["solid_fuel_open_fire", "solid_fuel_stove", "oil_standard",
                           "solid_fuel_boiler"],
                          p=[0.40, 0.25, 0.20, 0.15])


def _compute_wall_u_value(wall_type: str, insulation_type: str) -> float:
    """Compute effective wall U-value from wall type and added insulation."""
    base_u = WALL_TYPES[wall_type]
    base_r = 1.0 / base_u
    added_r = INSULATION_TYPES[insulation_type]
    total_r = base_r + added_r
    return 1.0 / total_r


def _compute_energy_value(
    wall_u: float,
    roof_u: float,
    floor_u: float,
    window_u: float,
    window_g: float,
    floor_area: float,
    wall_area: float,
    roof_area: float,
    window_area: float,
    floor_loss_area: float,
    volume: float,
    air_permeability: float,
    heating_efficiency: float,
    primary_energy_factor: float,
    hdd: float,
    ventilation_type: str,
    dwelling_type: str,
    rng: np.random.Generator,
) -> float:
    """Approximate the DEAP energy calculation.

    This is a simplified version of the DEAP monthly energy balance method,
    calibrated to reproduce the distribution of BER energy values in the
    published SEAI BER statistics.
    """
    # Fabric heat loss (W/K)
    fabric_loss = (
        wall_u * wall_area
        + roof_u * roof_area
        + floor_u * floor_loss_area
        + window_u * window_area
    )

    # Thermal bridging (approximate Y-factor)
    thermal_bridge = 0.08 * (wall_area + roof_area + floor_loss_area + window_area)

    # Ventilation heat loss (W/K)
    # Effective air change rate from permeability
    ach = air_permeability * (wall_area + roof_area) / volume * 0.05  # simplified
    ach = max(0.3, ach)  # minimum ventilation rate
    if ventilation_type == "mvhr":
        ach *= 0.35  # 65% heat recovery
    elif ventilation_type == "balanced_no_hr":
        ach *= 0.80
    ventilation_loss = 0.33 * ach * volume

    # Total heat loss coefficient (W/K)
    total_hlc = fabric_loss + thermal_bridge + ventilation_loss

    # Space heating demand (kWh/yr)
    # Using degree-day method: Q = HLC * HDD * 24 / 1000
    space_heating_demand = total_hlc * hdd * 24 / 1000

    # Solar gains (kWh/yr) — simplified
    # Irish irradiance approximately 900-1100 kWh/m2/yr on vertical south-facing
    irradiance = 400  # average across all orientations, kWh/m2/yr
    solar_gains = window_area * window_g * irradiance * 0.6  # utilisation factor

    # Internal gains (kWh/yr)
    internal_gains = 3.4 * floor_area * 8760 / 1000 * 0.5  # ~50% utilised

    # Net space heating demand
    net_heating = max(0, space_heating_demand - solar_gains - internal_gains)

    # Hot water demand (kWh/yr) — approximately 15-25% of total
    # DEAP formula based on floor area
    n_occupants = 1.0 + 1.76 * (1 - np.exp(-0.000349 * floor_area**2)) + 0.0013 * floor_area
    dhw_demand = n_occupants * 50 * 365 * 4.186 * 35 / 3600  # litres * days * cp * deltaT / 3600

    # Storage and distribution losses (approximate)
    dhw_demand *= 1.3  # 30% losses

    # Total delivered energy
    if heating_efficiency > 1.0:
        # Heat pump: COP reduces delivered energy
        delivered_space = net_heating / heating_efficiency
        delivered_dhw = dhw_demand / (heating_efficiency * 0.7)  # lower COP for DHW
    else:
        delivered_space = net_heating / heating_efficiency
        delivered_dhw = dhw_demand / max(0.3, heating_efficiency * 0.9)

    # Lighting and auxiliary (kWh/yr)
    lighting = floor_area * 10  # approximately 10 kWh/m2/yr
    auxiliary = 500  # pumps, fans, controls

    # Total primary energy
    primary_space = delivered_space * primary_energy_factor
    primary_dhw = delivered_dhw * primary_energy_factor
    primary_lighting = lighting * 2.08  # lighting is always electric
    primary_aux = auxiliary * 2.08

    total_primary = primary_space + primary_dhw + primary_lighting + primary_aux

    # Energy value (kWh/m2/yr)
    energy_value = total_primary / floor_area

    # Add realistic noise (assessor variability, rounding, default usage)
    noise = rng.normal(0, energy_value * 0.08)  # ~8% CV
    energy_value += noise

    # Cap at realistic maximum (SEAI data rarely exceeds 700 kWh/m2/yr)
    return max(5.0, min(700.0, round(energy_value, 1)))


def generate_synthetic_ber_data(
    n_records: int = 100_000,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic BER certificate data calibrated to SEAI statistics.

    Args:
        n_records: Number of BER certificates to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with BER certificate data.
    """
    rng = np.random.default_rng(seed)
    records = []

    # Year-built distribution calibrated to CSO housing stock data
    # and SEAI BER statistics
    year_weights = np.zeros(130)  # years 1900-2029
    for y in range(1900, 1940):
        year_weights[y - 1900] = 0.4
    for y in range(1940, 1967):
        year_weights[y - 1900] = 0.5
    for y in range(1967, 1978):
        year_weights[y - 1900] = 1.2
    for y in range(1978, 1992):
        year_weights[y - 1900] = 1.5
    for y in range(1992, 2000):
        year_weights[y - 1900] = 2.0
    for y in range(2000, 2008):
        year_weights[y - 1900] = 3.5  # Celtic Tiger peak
    for y in range(2008, 2012):
        year_weights[y - 1900] = 1.0  # post-crash
    for y in range(2012, 2020):
        year_weights[y - 1900] = 1.5
    for y in range(2020, 2026):
        year_weights[y - 1900] = 1.8
    year_weights = year_weights / year_weights.sum()
    years = np.arange(1900, 2030)

    county_list = list(COUNTY_WEIGHTS.keys())
    county_probs = np.array([COUNTY_WEIGHTS[c] for c in county_list])
    county_probs = county_probs / county_probs.sum()

    dwelling_probs = np.array(DWELLING_TYPE_WEIGHTS)
    dwelling_probs = dwelling_probs / dwelling_probs.sum()

    for i in range(n_records):
        # County
        county = rng.choice(county_list, p=county_probs)
        hdd = COUNTY_HDD[county]

        # Year built
        year_built = int(rng.choice(years, p=year_weights))

        # Dwelling type
        dwelling_type = rng.choice(DWELLING_TYPES, p=dwelling_probs)

        # Floor area (depends on dwelling type and era)
        if dwelling_type == "apartment":
            floor_area = max(30, rng.normal(70, 20))
            n_storeys = 1
        elif dwelling_type == "detached":
            if year_built >= 2000:
                floor_area = max(80, rng.normal(180, 50))
            else:
                floor_area = max(60, rng.normal(130, 40))
            n_storeys = rng.choice([1, 2], p=[0.35, 0.65])
        elif dwelling_type in ("semi_detached", "terraced_end"):
            floor_area = max(50, rng.normal(100, 25))
            n_storeys = rng.choice([1, 2], p=[0.20, 0.80])
        else:  # terraced_mid
            floor_area = max(40, rng.normal(85, 20))
            n_storeys = rng.choice([1, 2], p=[0.25, 0.75])

        floor_area = round(floor_area, 1)
        n_bedrooms = max(1, round(floor_area / 25 + rng.normal(0, 0.5)))

        # Wall type and insulation
        wall_type, insulation_type = _get_wall_type_for_era(year_built, dwelling_type, rng)
        wall_u = _compute_wall_u_value(wall_type, insulation_type)

        # Roof insulation (mm)
        if year_built < 1978:
            roof_insulation_mm = max(0, rng.choice([0, 25, 50, 100], p=[0.30, 0.20, 0.30, 0.20]))
        elif year_built < 1992:
            roof_insulation_mm = max(0, rng.choice([50, 100, 150], p=[0.30, 0.40, 0.30]))
        elif year_built < 2006:
            roof_insulation_mm = max(0, rng.choice([100, 150, 200], p=[0.25, 0.45, 0.30]))
        elif year_built < 2019:
            roof_insulation_mm = max(0, rng.choice([200, 250, 300], p=[0.30, 0.40, 0.30]))
        else:
            roof_insulation_mm = max(0, rng.choice([300, 350, 400], p=[0.30, 0.40, 0.30]))
        roof_u = max(0.10, 1.0 / (0.3 + roof_insulation_mm * 0.025))

        # Floor insulation
        if year_built < 1992:
            has_floor_insulation = rng.random() < 0.10
        elif year_built < 2006:
            has_floor_insulation = rng.random() < 0.40
        else:
            has_floor_insulation = rng.random() < 0.85
        floor_u = 0.25 if has_floor_insulation else 0.70

        # Windows
        if year_built < 1992:
            window_type = rng.choice(["single_glazed", "double_glazed_air"],
                                     p=[0.40, 0.60])
        elif year_built < 2006:
            window_type = rng.choice(["double_glazed_air", "double_glazed_argon"],
                                     p=[0.55, 0.45])
        elif year_built < 2019:
            window_type = rng.choice(["double_glazed_argon", "triple_glazed"],
                                     p=[0.75, 0.25])
        else:
            window_type = rng.choice(["double_glazed_argon", "triple_glazed"],
                                     p=[0.30, 0.70])
        window_u = WINDOW_U_VALUES[window_type]
        window_g = WINDOW_G_VALUES[window_type]

        # Heating system
        heating_type = _get_heating_type(year_built, county, rng)
        heating_efficiency = HEATING_EFFICIENCIES[heating_type]
        # Add realistic variation in efficiency
        heating_efficiency *= rng.uniform(0.90, 1.05)
        pef = PRIMARY_ENERGY_FACTORS[heating_type]

        # Secondary heating
        if heating_type.startswith("solid_fuel"):
            secondary_heating = "none"
        elif rng.random() < 0.35:
            secondary_heating = rng.choice(["open_fire", "stove", "electric_heater"],
                                           p=[0.40, 0.35, 0.25])
        else:
            secondary_heating = "none"

        # Ventilation
        if year_built >= 2019:
            ventilation_type = rng.choice(["mvhr", "extract_fans"], p=[0.70, 0.30])
        elif year_built >= 2006:
            ventilation_type = rng.choice(["extract_fans", "mvhr", "natural"],
                                          p=[0.55, 0.15, 0.30])
        else:
            ventilation_type = rng.choice(["natural", "extract_fans"],
                                          p=[0.60, 0.40])

        # Air permeability
        if year_built >= 2019:
            air_perm = max(1.0, rng.normal(3.0, 1.0))
        elif year_built >= 2006:
            air_perm = max(2.0, rng.normal(7.0, 2.0))
        elif year_built >= 1992:
            air_perm = max(3.0, rng.normal(10.0, 3.0))
        else:
            air_perm = max(5.0, rng.normal(15.0, 5.0))
        air_perm = round(air_perm, 1)

        # Geometry estimation
        if dwelling_type == "apartment":
            # Apartment: external walls on 1-2 sides
            perimeter_fraction = rng.uniform(0.3, 0.6)
            storey_height = 2.6
            footprint = floor_area
            wall_area = perimeter_fraction * 4 * np.sqrt(footprint) * storey_height
            roof_area = 0  # top-floor only
            if rng.random() < 0.25:  # top floor
                roof_area = footprint
            floor_loss_area = 0  # ground floor only
            if rng.random() < 0.25:
                floor_loss_area = footprint
        else:
            storey_height = 2.7 if year_built < 1960 else 2.5
            footprint = floor_area / n_storeys
            perimeter = 2 * (np.sqrt(footprint * 1.5) + np.sqrt(footprint / 1.5))
            if dwelling_type == "terraced_mid":
                # Only front and back walls exposed
                wall_area = 2 * np.sqrt(footprint / 1.5) * storey_height * n_storeys
            elif dwelling_type == "terraced_end":
                wall_area = (2 * np.sqrt(footprint / 1.5) + np.sqrt(footprint * 1.5)) * storey_height * n_storeys
            else:
                wall_area = perimeter * storey_height * n_storeys

            roof_area = footprint
            floor_loss_area = footprint

        volume = floor_area * storey_height
        window_area = wall_area * rng.uniform(0.12, 0.22)
        wall_area -= window_area  # net wall area

        # Compute energy value
        energy_value = _compute_energy_value(
            wall_u=wall_u,
            roof_u=roof_u,
            floor_u=floor_u,
            window_u=window_u,
            window_g=window_g,
            floor_area=floor_area,
            wall_area=wall_area,
            roof_area=roof_area,
            window_area=window_area,
            floor_loss_area=floor_loss_area,
            volume=volume,
            air_permeability=air_perm,
            heating_efficiency=heating_efficiency,
            primary_energy_factor=pef,
            hdd=hdd,
            ventilation_type=ventilation_type,
            dwelling_type=dwelling_type,
            rng=rng,
        )

        # BER rating
        ber_rating = energy_value_to_ber_rating(energy_value)

        # CO2 emissions (simplified)
        co2_factor = pef * 0.2  # approximate kgCO2 per kWh primary
        if heating_type.startswith("solid_fuel"):
            co2_factor = 0.35
        elif heating_type.startswith("oil"):
            co2_factor = 0.27
        elif heating_type.startswith("gas"):
            co2_factor = 0.21
        elif heating_type.startswith("heat_pump") or heating_type.startswith("electric"):
            co2_factor = 0.32  # Irish grid electricity
        co2_emissions = round(energy_value * co2_factor, 1)

        # Assessment metadata
        # Assessment year: between year_built and 2025, weighted toward recent
        assess_earliest = max(2007, year_built)  # BER mandatory from 2007
        assess_year = int(rng.choice(
            range(assess_earliest, 2026),
            p=np.array([1.0 + 0.5 * (y - assess_earliest) for y in range(assess_earliest, 2026)]) /
              sum(1.0 + 0.5 * (y - assess_earliest) for y in range(assess_earliest, 2026))
        ))

        # Assessor ID (synthetic)
        n_assessors = 2000
        assessor_id = f"ASR{rng.integers(1, n_assessors + 1):05d}"

        records.append({
            "ber_number": f"BER{i+1:08d}",
            "county": county,
            "year_built": year_built,
            "dwelling_type": dwelling_type,
            "floor_area_m2": floor_area,
            "n_storeys": n_storeys,
            "n_bedrooms": n_bedrooms,
            "wall_type": wall_type,
            "insulation_type": insulation_type,
            "wall_u_value": round(wall_u, 3),
            "roof_insulation_mm": roof_insulation_mm,
            "roof_u_value": round(roof_u, 3),
            "has_floor_insulation": int(has_floor_insulation),
            "floor_u_value": round(floor_u, 3),
            "window_type": window_type,
            "window_u_value": round(window_u, 1),
            "window_g_value": round(window_g, 2),
            "heating_type": heating_type,
            "heating_efficiency": round(heating_efficiency, 3),
            "primary_energy_factor": pef,
            "secondary_heating": secondary_heating,
            "ventilation_type": ventilation_type,
            "air_permeability": air_perm,
            "energy_value_kwh_m2_yr": energy_value,
            "co2_emissions_kg_m2_yr": co2_emissions,
            "ber_rating": ber_rating,
            "assessment_year": assess_year,
            "assessor_id": assessor_id,
            "hdd": hdd,
            "radon_risk": COUNTY_RADON_RISK[county],
            "gas_available": COUNTY_GAS_AVAILABLE[county],
        })

    df = pd.DataFrame(records)
    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to BER dataset."""
    df = df.copy()

    # Regulation era
    conditions = [
        df["year_built"] < 1978,
        (df["year_built"] >= 1978) & (df["year_built"] < 1992),
        (df["year_built"] >= 1992) & (df["year_built"] < 2006),
        (df["year_built"] >= 2006) & (df["year_built"] < 2011),
        (df["year_built"] >= 2011) & (df["year_built"] < 2019),
        df["year_built"] >= 2019,
    ]
    choices = [0, 1, 2, 3, 4, 5]
    df["regulation_era"] = np.select(conditions, choices, default=0)

    # Vintage decade
    df["vintage_decade"] = (df["year_built"] // 10) * 10

    # Log floor area
    df["log_floor_area"] = np.log(df["floor_area_m2"])

    # Area per bedroom (occupancy density proxy)
    df["area_per_bedroom"] = df["floor_area_m2"] / df["n_bedrooms"].clip(lower=1)

    # Form factor proxy (higher for detached, lower for mid-terrace/apartments)
    form_factor_map = {
        "detached": 3.0,
        "semi_detached": 2.3,
        "terraced_end": 2.0,
        "terraced_mid": 1.5,
        "apartment": 1.2,
    }
    df["form_factor_proxy"] = df["dwelling_type"].map(form_factor_map)

    # Is heat pump
    df["is_heat_pump"] = df["heating_type"].str.contains("heat_pump").astype(int)

    # Is condensing boiler
    df["is_condensing"] = df["heating_type"].str.contains("condensing").astype(int)

    # Is solid fuel
    df["is_solid_fuel"] = df["heating_type"].str.contains("solid_fuel").astype(int)

    # Fuel type group
    fuel_map = {
        "oil_standard": "oil", "oil_condensing": "oil",
        "gas_standard": "gas", "gas_condensing": "gas",
        "solid_fuel_open_fire": "solid", "solid_fuel_stove": "solid",
        "solid_fuel_boiler": "solid",
        "electric_storage": "electric", "electric_panel": "electric",
        "heat_pump_ashp": "heat_pump", "heat_pump_gshp": "heat_pump",
    }
    df["fuel_group"] = df["heating_type"].map(fuel_map)

    # Wall quality ordinal
    df["wall_quality_ordinal"] = pd.cut(
        df["wall_u_value"],
        bins=[0, 0.25, 0.40, 0.60, 1.0, 1.5, 3.0],
        labels=[5, 4, 3, 2, 1, 0],
    ).astype(float)

    # Window quality ordinal
    window_ord = {"single_glazed": 0, "double_glazed_air": 1,
                  "double_glazed_argon": 2, "triple_glazed": 3}
    df["window_quality_ordinal"] = df["window_type"].map(window_ord)

    # Has secondary heating
    df["has_secondary_heating"] = (df["secondary_heating"] != "none").astype(int)

    # Has MVHR
    df["has_mvhr"] = (df["ventilation_type"] == "mvhr").astype(int)

    # Wall x heating interaction
    df["wall_u_x_eff_inv"] = df["wall_u_value"] * (1.0 / df["heating_efficiency"].clip(lower=0.1))

    # Building age at assessment
    df["building_age_at_assessment"] = df["assessment_year"] - df["year_built"]

    # Is nZEB (post-2019 build)
    df["is_nzeb"] = (df["year_built"] >= 2019).astype(int)

    return df


# ============================================================================
# Data loading pipeline
# ============================================================================

def load_dataset(
    n_records: int = 100_000,
    force_regenerate: bool = False,
    seed: int = 42,
) -> pd.DataFrame:
    """Load BER dataset from cache or generate synthetic data.

    Returns a DataFrame with all raw and derived features.
    """
    if PARQUET_FILE.exists() and not force_regenerate:
        print(f"Loading cached dataset from {PARQUET_FILE}")
        df = pd.read_parquet(PARQUET_FILE)
        print(f"  {len(df)} records loaded, {df.columns.size} columns")
        return df

    print(f"Generating synthetic BER data ({n_records} records)...")
    df = generate_synthetic_ber_data(n_records=n_records, seed=seed)

    print("  Computing derived features...")
    df = add_derived_features(df)

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_FILE, index=False)
    print(f"  Saved to {PARQUET_FILE} ({len(df)} records, {df.columns.size} columns)")

    # Save metadata
    metadata = {
        "n_records": len(df),
        "n_columns": int(df.columns.size),
        "data_source": "synthetic_calibrated_to_seai_statistics",
        "generated_at": datetime.now().isoformat(),
        "seed": seed,
        "ber_rating_distribution": df["ber_rating"].value_counts().sort_index().to_dict(),
        "county_distribution": df["county"].value_counts().to_dict(),
        "mean_energy_value": float(df["energy_value_kwh_m2_yr"].mean()),
        "median_energy_value": float(df["energy_value_kwh_m2_yr"].median()),
    }
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata saved to {METADATA_FILE}")

    return df


def get_train_test_split(
    df: pd.DataFrame,
    test_fraction: float = 0.15,
    seed: int = 42,
    stratify_col: str = "ber_rating",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train and test sets, stratified by BER rating.

    Returns (train_df, test_df).
    """
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(
        df, test_size=test_fraction, random_state=seed,
        stratify=df[stratify_col],
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def get_cv_folds(
    df: pd.DataFrame,
    n_folds: int = 5,
    seed: int = 42,
    stratify_col: str = "ber_rating",
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Generate stratified cross-validation folds.

    Returns list of (train_df, val_df) tuples.
    """
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    folds = []
    for train_idx, val_idx in skf.split(df, df[stratify_col]):
        folds.append((df.iloc[train_idx].copy(), df.iloc[val_idx].copy()))
    return folds


# ============================================================================
# CLI
# ============================================================================

def print_info(df: pd.DataFrame) -> None:
    """Print dataset summary statistics."""
    print(f"\n{'=' * 60}")
    print("BER Dataset Summary")
    print(f"{'=' * 60}")
    print(f"  Records: {len(df)}")
    print(f"  Columns: {df.columns.size}")
    print(f"\n  Energy Value (kWh/m2/yr):")
    print(f"    Mean:   {df['energy_value_kwh_m2_yr'].mean():.1f}")
    print(f"    Median: {df['energy_value_kwh_m2_yr'].median():.1f}")
    print(f"    Std:    {df['energy_value_kwh_m2_yr'].std():.1f}")
    print(f"    Min:    {df['energy_value_kwh_m2_yr'].min():.1f}")
    print(f"    Max:    {df['energy_value_kwh_m2_yr'].max():.1f}")
    print(f"\n  BER Rating Distribution:")
    for rating in sorted(BER_BANDS.keys()):
        count = (df["ber_rating"] == rating).sum()
        pct = 100 * count / len(df)
        bar = "#" * int(pct)
        print(f"    {rating:>3}: {count:>6} ({pct:>5.1f}%) {bar}")
    print(f"\n  Year Built: {df['year_built'].min()}-{df['year_built'].max()}")
    print(f"  Floor Area: {df['floor_area_m2'].mean():.0f} m2 (mean)")
    print(f"\n  Heating Type Distribution:")
    for ht, count in df["heating_type"].value_counts().head(8).items():
        print(f"    {ht:>30}: {count:>6} ({100*count/len(df):>5.1f}%)")
    print(f"\n  County Distribution (top 5):")
    for c, count in df["county"].value_counts().head(5).items():
        print(f"    {c:>15}: {count:>6} ({100*count/len(df):>5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="BER Data Loader")
    parser.add_argument("--info", action="store_true", help="Print dataset info")
    parser.add_argument("--force", action="store_true", help="Force regeneration")
    parser.add_argument("--n-records", type=int, default=100_000,
                        help="Number of records to generate")
    args = parser.parse_args()

    df = load_dataset(n_records=args.n_records, force_regenerate=args.force)

    if args.info:
        print_info(df)


if __name__ == "__main__":
    main()
