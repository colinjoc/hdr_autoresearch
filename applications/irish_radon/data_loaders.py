"""
Data loaders for Irish Radon Prediction.

Generates calibrated synthetic data matching published Irish radon statistics
from Fennell et al. (2002, 2021), Elío et al. (2020, 2022), and GSI Tellus
survey summaries. The synthetic data reproduces the known statistical
relationships between geology, building characteristics, and indoor radon.

Usage:
    python data_loaders.py                 # Generate dataset and print summary
    python data_loaders.py --info          # Print detailed statistics
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"

# ============================================================================
# Constants calibrated to published Irish statistics
# ============================================================================

COUNTIES = [
    "Carlow", "Cavan", "Clare", "Cork", "Donegal", "Dublin", "Galway",
    "Kerry", "Kildare", "Kilkenny", "Laois", "Leitrim", "Limerick",
    "Longford", "Louth", "Mayo", "Meath", "Monaghan", "Offaly",
    "Roscommon", "Sligo", "Tipperary", "Waterford", "Westmeath",
    "Wexford", "Wicklow",
]

# County weights (approximate EDs per county)
COUNTY_WEIGHTS = {
    "Dublin": 0.10, "Cork": 0.12, "Galway": 0.08, "Kerry": 0.05,
    "Donegal": 0.06, "Mayo": 0.05, "Tipperary": 0.05, "Clare": 0.04,
    "Limerick": 0.04, "Wexford": 0.04, "Wicklow": 0.03, "Meath": 0.04,
    "Kildare": 0.03, "Kilkenny": 0.03, "Waterford": 0.03, "Louth": 0.02,
    "Westmeath": 0.02, "Offaly": 0.02, "Laois": 0.02, "Cavan": 0.02,
    "Roscommon": 0.02, "Sligo": 0.02, "Monaghan": 0.02, "Carlow": 0.02,
    "Longford": 0.01, "Leitrim": 0.01,
}

# County approximate centroids (lat, lon)
COUNTY_COORDS = {
    "Dublin": (53.35, -6.26), "Cork": (51.90, -8.47), "Galway": (53.27, -8.86),
    "Kerry": (52.06, -9.85), "Donegal": (54.83, -7.95), "Mayo": (53.76, -9.53),
    "Tipperary": (52.67, -7.83), "Clare": (52.84, -8.98), "Limerick": (52.66, -8.63),
    "Wexford": (52.47, -6.58), "Wicklow": (52.98, -6.37), "Meath": (53.65, -6.65),
    "Kildare": (53.22, -6.78), "Kilkenny": (52.65, -7.26), "Waterford": (52.26, -7.11),
    "Louth": (53.92, -6.49), "Westmeath": (53.53, -7.34), "Offaly": (53.23, -7.60),
    "Laois": (52.99, -7.56), "Cavan": (53.99, -7.36), "Roscommon": (53.76, -8.27),
    "Sligo": (54.18, -8.47), "Monaghan": (54.15, -6.97), "Carlow": (52.71, -6.83),
    "Longford": (53.73, -7.79), "Leitrim": (54.15, -8.00),
}

# Mean eU by county (calibrated to Tellus survey summaries, ppm)
# Higher for granite counties (Wicklow, Carlow, Galway), lower for western peat
COUNTY_EU_MEAN = {
    "Dublin": 2.5, "Cork": 2.8, "Galway": 3.2, "Kerry": 2.4,
    "Donegal": 2.6, "Mayo": 1.8, "Tipperary": 2.3, "Clare": 2.9,
    "Limerick": 2.2, "Wexford": 2.7, "Wicklow": 4.5, "Meath": 2.0,
    "Kildare": 2.3, "Kilkenny": 3.0, "Waterford": 2.6, "Louth": 1.9,
    "Westmeath": 2.1, "Offaly": 2.0, "Laois": 2.4, "Cavan": 2.2,
    "Roscommon": 1.9, "Sligo": 2.3, "Monaghan": 2.0, "Carlow": 3.8,
    "Longford": 1.8, "Leitrim": 2.0,
}

# Mean elevation by county (m)
COUNTY_ELEVATION = {
    "Dublin": 60, "Cork": 120, "Galway": 80, "Kerry": 150,
    "Donegal": 130, "Mayo": 100, "Tipperary": 140, "Clare": 70,
    "Limerick": 80, "Wexford": 70, "Wicklow": 250, "Meath": 80,
    "Kildare": 100, "Kilkenny": 120, "Waterford": 100, "Louth": 60,
    "Westmeath": 90, "Offaly": 80, "Laois": 130, "Cavan": 150,
    "Roscommon": 70, "Sligo": 90, "Monaghan": 120, "Carlow": 130,
    "Longford": 70, "Leitrim": 130,
}

# Bedrock geology classes (simplified from ~500 GSI codes)
BEDROCK_CLASSES = [
    "granite", "limestone_pure", "limestone_impure", "sandstone",
    "shale", "black_shale", "quartzite", "schist", "gneiss",
    "volcanic", "dolerite", "conglomerate",
]

# Bedrock class weights by county (simplified)
BEDROCK_PROBS = {
    "granite": 0.08, "limestone_pure": 0.25, "limestone_impure": 0.15,
    "sandstone": 0.15, "shale": 0.12, "black_shale": 0.04,
    "quartzite": 0.05, "schist": 0.05, "gneiss": 0.03,
    "volcanic": 0.03, "dolerite": 0.03, "conglomerate": 0.02,
}

# Bedrock uranium content modifier (relative to eU_mean)
BEDROCK_U_MODIFIER = {
    "granite": 2.0, "limestone_pure": 0.7, "limestone_impure": 0.9,
    "sandstone": 0.8, "shale": 1.0, "black_shale": 2.5,
    "quartzite": 0.5, "schist": 1.1, "gneiss": 1.3,
    "volcanic": 0.9, "dolerite": 0.6, "conglomerate": 0.7,
}

# Bedrock permeability modifier for radon transport
BEDROCK_PERM_MODIFIER = {
    "granite": 0.8, "limestone_pure": 1.5, "limestone_impure": 1.0,
    "sandstone": 1.2, "shale": 0.5, "black_shale": 0.4,
    "quartzite": 0.6, "schist": 0.7, "gneiss": 0.7,
    "volcanic": 0.9, "dolerite": 0.5, "conglomerate": 1.0,
}

# Quaternary (subsoil) geology classes
QUATERNARY_CLASSES = [
    "till_thick", "till_thin", "sand_gravel", "alluvium",
    "peat", "rock_surface", "lacustrine",
]

QUATERNARY_PROBS = {
    "till_thick": 0.30, "till_thin": 0.20, "sand_gravel": 0.10,
    "alluvium": 0.10, "peat": 0.15, "rock_surface": 0.10,
    "lacustrine": 0.05,
}

# Quaternary permeability ordinal (1=low, 6=high)
QUATERNARY_PERMEABILITY = {
    "peat": 1, "till_thick": 2, "lacustrine": 2, "alluvium": 3,
    "till_thin": 4, "sand_gravel": 5, "rock_surface": 6,
}

# BER rating ordinal encoding (A1=15, G=1)
BER_RATINGS = {
    "A1": 15, "A2": 14, "A3": 13, "B1": 12, "B2": 11, "B3": 10,
    "C1": 9, "C2": 8, "C3": 7, "D1": 6, "D2": 5,
    "E1": 4, "E2": 3, "F": 2, "G": 1,
}


# ============================================================================
# Synthetic data generation
# ============================================================================

def generate_synthetic_radon_data(
    n_areas: int = 3400,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic area-level radon prediction data.

    Each row represents an Electoral Division (ED) or Small Area.
    Data is calibrated to published Irish radon statistics.

    Args:
        n_areas: Number of areas to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with geological, building, and radon columns.
    """
    rng = np.random.RandomState(seed)

    # Assign counties
    county_probs = np.array([COUNTY_WEIGHTS.get(c, 0.01) for c in COUNTIES])
    county_probs = county_probs / county_probs.sum()
    counties = rng.choice(COUNTIES, size=n_areas, p=county_probs)

    # Generate coordinates with county-level clustering
    lats = np.zeros(n_areas)
    lons = np.zeros(n_areas)
    elevations = np.zeros(n_areas)
    for i, county in enumerate(counties):
        clat, clon = COUNTY_COORDS[county]
        lats[i] = clat + rng.normal(0, 0.15)
        lons[i] = clon + rng.normal(0, 0.20)
        elevations[i] = max(5, COUNTY_ELEVATION[county] + rng.normal(0, 50))

    # Generate bedrock geology
    bedrock_codes = []
    for i, county in enumerate(counties):
        # County-specific bedrock probability adjustments
        probs = BEDROCK_PROBS.copy()
        if county in ("Wicklow", "Carlow", "Wexford", "Kilkenny"):
            probs["granite"] = 0.30  # Leinster Granite
        elif county in ("Galway",):
            probs["granite"] = 0.20  # Galway Granite
        elif county in ("Clare", "Kerry"):
            probs["black_shale"] = 0.15  # Namurian shales
        elif county in ("Roscommon", "Longford", "Westmeath", "Offaly"):
            probs["limestone_pure"] = 0.50  # Midlands limestone
        elif county in ("Mayo", "Donegal"):
            probs["quartzite"] = 0.15
            probs["schist"] = 0.15

        codes = list(probs.keys())
        weights = np.array(list(probs.values()))
        weights = weights / weights.sum()
        bedrock_codes.append(rng.choice(codes, p=weights))

    # Generate quaternary geology
    quat_codes = []
    for i, county in enumerate(counties):
        probs = QUATERNARY_PROBS.copy()
        if county in ("Mayo", "Donegal", "Galway", "Kerry"):
            probs["peat"] = 0.30  # Western peat
            probs["rock_surface"] = 0.15
        elif county in ("Dublin", "Meath", "Kildare", "Louth"):
            probs["till_thick"] = 0.40  # Eastern glacial till
        elif county in ("Offaly", "Laois", "Westmeath"):
            probs["peat"] = 0.25  # Midlands bog

        codes = list(probs.keys())
        weights = np.array(list(probs.values()))
        weights = weights / weights.sum()
        quat_codes.append(rng.choice(codes, p=weights))

    # Generate Tellus radiometric data
    eU_means = np.zeros(n_areas)
    eTh_means = np.zeros(n_areas)
    K_means = np.zeros(n_areas)
    for i in range(n_areas):
        county = counties[i]
        bedrock = bedrock_codes[i]
        base_eU = COUNTY_EU_MEAN[county]
        u_mod = BEDROCK_U_MODIFIER[bedrock]
        eU_means[i] = max(0.2, base_eU * u_mod + rng.normal(0, 0.5))
        eTh_means[i] = max(0.3, eU_means[i] * rng.uniform(1.5, 4.0) + rng.normal(0, 0.5))
        K_means[i] = max(0.1, rng.normal(1.8, 0.5))

    # Generate BER building features (area-level averages)
    mean_ber_ordinal = np.zeros(n_areas)
    mean_air_perm = np.zeros(n_areas)
    pct_slab = np.zeros(n_areas)
    pct_timber = np.zeros(n_areas)
    pct_mvhr = np.zeros(n_areas)
    pct_natural = np.zeros(n_areas)
    mean_year_built = np.zeros(n_areas)
    pct_post_2011 = np.zeros(n_areas)
    pct_pre_1970 = np.zeros(n_areas)
    pct_detached = np.zeros(n_areas)
    mean_floor_area = np.zeros(n_areas)

    for i, county in enumerate(counties):
        # Urban vs rural affects BER distribution
        is_urban = county in ("Dublin", "Cork", "Galway", "Limerick")
        if is_urban:
            mean_ber_ordinal[i] = rng.normal(9.0, 2.0)  # Higher BER in cities
            mean_air_perm[i] = max(1.0, rng.normal(5.0, 2.0))
            pct_slab[i] = rng.uniform(60, 90)
            pct_timber[i] = rng.uniform(5, 25)
            pct_detached[i] = rng.uniform(15, 40)
            mean_floor_area[i] = rng.normal(100, 25)
            pct_post_2011[i] = rng.uniform(10, 35)
            pct_pre_1970[i] = rng.uniform(10, 30)
        else:
            mean_ber_ordinal[i] = rng.normal(6.0, 2.5)  # Lower BER in rural
            mean_air_perm[i] = max(1.0, rng.normal(8.0, 3.0))
            pct_slab[i] = rng.uniform(40, 75)
            pct_timber[i] = rng.uniform(15, 45)
            pct_detached[i] = rng.uniform(40, 80)
            mean_floor_area[i] = rng.normal(130, 30)
            pct_post_2011[i] = rng.uniform(5, 20)
            pct_pre_1970[i] = rng.uniform(20, 50)

        mean_ber_ordinal[i] = np.clip(mean_ber_ordinal[i], 1, 15)
        pct_mvhr[i] = rng.uniform(2, 20) if pct_post_2011[i] > 15 else rng.uniform(0, 5)
        pct_natural[i] = 100 - pct_mvhr[i] - rng.uniform(5, 25)
        mean_year_built[i] = rng.normal(1985, 15)

    # Generate radon outcome (calibrated to Irish statistics)
    # Radon depends on: eU (source), quaternary permeability (pathway),
    # air permeability (inverse ventilation), floor type
    pct_above_200 = np.zeros(n_areas)
    for i in range(n_areas):
        quat_perm = QUATERNARY_PERMEABILITY[quat_codes[i]]
        bedrock_perm = BEDROCK_PERM_MODIFIER[bedrock_codes[i]]

        # Radon potential: source × pathway
        radon_potential = (
            eU_means[i] *  # uranium source
            (quat_perm / 3.5) *  # quaternary permeability (normalized)
            bedrock_perm *  # bedrock permeability
            (1.0 / (mean_air_perm[i] / 7.0)) *  # inverse ventilation (normalized)
            (1.0 + 0.3 * (pct_timber[i] / 100.0))  # timber floor bonus
        )

        # Convert to percentage above 200 Bq/m3
        # Calibrated so national average pct_above_200 is ~7% and HRA prevalence ~28%
        # The sigmoid maps radon_potential to [0, 80] with most areas below 10%
        log_pct = -2.85 + 0.65 * np.log(radon_potential + 0.1) + rng.normal(0, 0.55)
        pct_above_200[i] = np.clip(80 * (1 / (1 + np.exp(-log_pct))), 0, 80)

    is_hra = (pct_above_200 > 10).astype(int)

    # Number of measurements per area (sparse, as in reality)
    n_measurements = rng.poisson(lam=15, size=n_areas)
    n_measurements = np.maximum(n_measurements, 1)

    df = pd.DataFrame({
        "area_id": [f"ED_{i:05d}" for i in range(n_areas)],
        "county": counties,
        "latitude": np.round(lats, 4),
        "longitude": np.round(lons, 4),
        "elevation_mean": np.round(elevations, 1),
        "eU_mean": np.round(eU_means, 2),
        "eTh_mean": np.round(eTh_means, 2),
        "K_mean": np.round(K_means, 2),
        "bedrock_code": bedrock_codes,
        "quat_code": quat_codes,
        "mean_ber_rating_ordinal": np.round(mean_ber_ordinal, 1),
        "mean_air_permeability": np.round(mean_air_perm, 1),
        "pct_slab_on_ground": np.round(pct_slab, 1),
        "pct_suspended_timber": np.round(pct_timber, 1),
        "pct_mvhr": np.round(pct_mvhr, 1),
        "pct_natural_vent": np.round(pct_natural, 1),
        "mean_year_built": np.round(mean_year_built, 0).astype(int),
        "pct_post_2011": np.round(pct_post_2011, 1),
        "pct_pre_1970": np.round(pct_pre_1970, 1),
        "pct_detached": np.round(pct_detached, 1),
        "mean_floor_area": np.round(mean_floor_area, 1),
        "pct_above_200": np.round(pct_above_200, 1),
        "is_hra": is_hra,
        "n_measurements": n_measurements,
    })

    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to the radon dataset.

    Computes interaction terms, ratios, and indicator variables from
    the raw geological and building data.
    """
    df = df.copy()

    # Radiometric ratios
    df["eU_eTh_ratio"] = np.round(df["eU_mean"] / df["eTh_mean"].clip(lower=0.1), 3)
    df["total_dose_rate"] = np.round(
        0.0417 * df["K_mean"] + 0.604 * df["eU_mean"] + 0.310 * df["eTh_mean"], 3
    )
    df["log_eU"] = np.round(np.log(df["eU_mean"].clip(lower=0.1)), 3)

    # Lithology indicators
    df["is_granite"] = (df["bedrock_code"] == "granite").astype(int)
    df["is_limestone"] = df["bedrock_code"].isin(
        ["limestone_pure", "limestone_impure"]
    ).astype(int)
    df["is_shale"] = df["bedrock_code"].isin(["shale", "black_shale"]).astype(int)

    # Quaternary indicators
    df["quat_permeability"] = df["quat_code"].map(QUATERNARY_PERMEABILITY)
    df["is_rock_surface"] = (df["quat_code"] == "rock_surface").astype(int)
    df["is_peat"] = (df["quat_code"] == "peat").astype(int)

    return df


# ============================================================================
# Cross-validation and splitting (spatial)
# ============================================================================

def get_cv_folds_spatial(
    df: pd.DataFrame,
    n_folds: int = 5,
    seed: int = 42,
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Create spatial cross-validation folds grouped by county.

    Counties are assigned to folds to prevent spatial leakage.
    Each fold has roughly equal number of areas.
    """
    rng = np.random.RandomState(seed)

    # Get county sizes
    county_sizes = df.groupby("county").size().to_dict()
    counties_sorted = sorted(county_sizes.keys(),
                             key=lambda c: -county_sizes[c])

    # Assign counties to folds using greedy balancing
    fold_assignments = {}
    fold_sizes = [0] * n_folds

    for county in counties_sorted:
        # Assign to fold with fewest areas
        min_fold = int(np.argmin(fold_sizes))
        fold_assignments[county] = min_fold
        fold_sizes[min_fold] += county_sizes[county]

    # Create folds
    folds = []
    for fold_idx in range(n_folds):
        val_counties = {c for c, f in fold_assignments.items() if f == fold_idx}
        train_mask = ~df["county"].isin(val_counties)
        val_mask = df["county"].isin(val_counties)
        folds.append((df[train_mask].copy(), df[val_mask].copy()))

    return folds


def get_train_test_split(
    df: pd.DataFrame,
    test_fraction: float = 0.15,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into train and test sets by county (spatial split).

    Ensures no county appears in both train and test.
    """
    rng = np.random.RandomState(seed)

    county_sizes = df.groupby("county").size().to_dict()
    total = len(df)
    target_test = int(total * test_fraction)

    # Shuffle counties and greedily assign to test until target reached
    county_list = list(county_sizes.keys())
    rng.shuffle(county_list)

    test_counties = set()
    test_size = 0
    for county in county_list:
        if test_size >= target_test:
            break
        test_counties.add(county)
        test_size += county_sizes[county]

    test_mask = df["county"].isin(test_counties)
    return df[~test_mask].copy(), df[test_mask].copy()


def load_dataset(n_areas: int = 3400, seed: int = 42) -> pd.DataFrame:
    """Load the radon prediction dataset.

    Currently generates synthetic data. When real data becomes available,
    this function will load from data/ directory instead.
    """
    df = generate_synthetic_radon_data(n_areas=n_areas, seed=seed)
    df = add_derived_features(df)
    return df


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Irish Radon Data Loader")
    parser.add_argument("--info", action="store_true", help="Print dataset statistics")
    args = parser.parse_args()

    df = load_dataset()
    print(f"Generated {len(df)} areas")
    print(f"  Counties: {df['county'].nunique()}")
    print(f"  HRA areas: {df['is_hra'].sum()} ({df['is_hra'].mean()*100:.1f}%)")
    print(f"  Mean eU: {df['eU_mean'].mean():.2f} ppm")
    print(f"  Mean pct_above_200: {df['pct_above_200'].mean():.1f}%")

    if args.info:
        print(f"\nPer-county HRA rate:")
        for county in sorted(COUNTIES):
            mask = df["county"] == county
            if mask.sum() > 0:
                hra_rate = df.loc[mask, "is_hra"].mean() * 100
                mean_eU = df.loc[mask, "eU_mean"].mean()
                print(f"  {county:>15}: HRA={hra_rate:.0f}%, eU={mean_eU:.1f}ppm, n={mask.sum()}")

        print(f"\nPer-bedrock HRA rate:")
        for br in sorted(BEDROCK_CLASSES):
            mask = df["bedrock_code"] == br
            if mask.sum() > 0:
                hra_rate = df.loc[mask, "is_hra"].mean() * 100
                print(f"  {br:>20}: HRA={hra_rate:.0f}%, n={mask.sum()}")

        print(f"\nPer-quaternary HRA rate:")
        for qc in sorted(QUATERNARY_CLASSES):
            mask = df["quat_code"] == qc
            if mask.sum() > 0:
                hra_rate = df.loc[mask, "is_hra"].mean() * 100
                print(f"  {qc:>15}: HRA={hra_rate:.0f}%, n={mask.sum()}")
