"""
Data loaders for Xylella Olive Decline Prediction.

Generates calibrated synthetic data matching the known Xylella fastidiosa
expansion timeline in Puglia (southern Italy) and Alicante (Spain).

The synthetic data reproduces:
- The northward expansion wave (~20 km/yr from Lecce epicentre since 2013)
- NDVI decline patterns in affected olive groves
- E-OBS climate statistics (Tmin, Tmax, precipitation)
- Geographic and topographic features

Ground truth is constructed from the published EFSA demarcated zone timeline,
NOT from individual tree measurements. This is explicitly documented as a
limitation.

Usage:
    python data_loaders.py              # Generate dataset and print summary
    python data_loaders.py --info       # Print detailed statistics
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
# Constants calibrated to published Puglia and Alicante data
# ============================================================================

# Puglia provinces from south to north
PUGLIA_PROVINCES = [
    "Lecce", "Brindisi", "Taranto", "Bari",
    "Barletta-Andria-Trani", "Foggia",
]

# Spanish provinces
SPAIN_PROVINCES = [
    "Alicante", "Castellon", "Valencia",
]

ALL_PROVINCES = PUGLIA_PROVINCES + SPAIN_PROVINCES

# Province approximate centroids (lat, lon)
PROVINCE_COORDS = {
    "Lecce": (40.20, 18.17),
    "Brindisi": (40.63, 17.94),
    "Taranto": (40.47, 17.24),
    "Bari": (41.12, 16.87),
    "Barletta-Andria-Trani": (41.23, 16.29),
    "Foggia": (41.46, 15.55),
    "Alicante": (38.35, -0.48),
    "Castellon": (39.99, -0.05),
    "Valencia": (39.47, -0.38),
}

# Municipalities per province (approximate; for synthetic data generation)
MUNICIPALITIES_PER_PROVINCE = {
    "Lecce": 97, "Brindisi": 20, "Taranto": 29, "Bari": 41,
    "Barletta-Andria-Trani": 10, "Foggia": 61,
    "Alicante": 40, "Castellon": 30, "Valencia": 35,
}

# Year of first Xylella detection by province (EFSA official timeline)
FIRST_DETECTION_YEAR = {
    "Lecce": 2013,
    "Brindisi": 2016,
    "Taranto": 2018,
    "Bari": 2021,
    "Barletta-Andria-Trani": 2023,
    "Foggia": 2025,
    "Alicante": 2017,
    "Castellon": None,   # Not yet detected
    "Valencia": None,     # Not yet detected
}

# Province mean elevation (metres)
PROVINCE_ELEVATION = {
    "Lecce": 45, "Brindisi": 72, "Taranto": 98, "Bari": 165,
    "Barletta-Andria-Trani": 210, "Foggia": 280,
    "Alicante": 145, "Castellon": 220, "Valencia": 110,
}

# Province climate characteristics (calibrated to E-OBS 2010-2024 means)
# (jan_tmin_mean, jan_tmin_std, annual_precip_mean, annual_precip_std)
PROVINCE_CLIMATE = {
    "Lecce": (3.8, 1.2, 580, 80),
    "Brindisi": (4.2, 1.3, 520, 75),
    "Taranto": (3.5, 1.4, 490, 85),
    "Bari": (3.0, 1.5, 550, 90),
    "Barletta-Andria-Trani": (2.2, 1.6, 480, 95),
    "Foggia": (1.5, 2.0, 450, 100),
    "Alicante": (5.2, 1.8, 310, 90),
    "Castellon": (3.8, 2.0, 430, 110),
    "Valencia": (4.5, 1.7, 440, 95),
}

# Olive grove fraction by province (approximate from CORINE class 223)
OLIVE_FRACTION = {
    "Lecce": 0.42, "Brindisi": 0.38, "Taranto": 0.25, "Bari": 0.35,
    "Barletta-Andria-Trani": 0.15, "Foggia": 0.12,
    "Alicante": 0.18, "Castellon": 0.08, "Valencia": 0.10,
}

# Distance from Lecce epicentre (km, approximate)
DISTANCE_FROM_EPICENTRE_KM = {
    "Lecce": 0, "Brindisi": 40, "Taranto": 80, "Bari": 150,
    "Barletta-Andria-Trani": 190, "Foggia": 260,
    "Alicante": 1800, "Castellon": 1900, "Valencia": 1850,
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute haversine distance in km between two lat/lon points."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
         np.sin(dlon / 2) ** 2)
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def generate_synthetic_data(
    n_municipalities: Optional[int] = None,
    prediction_year: int = 2024,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic municipality-level olive grove health dataset.

    Each row represents one municipality in one prediction year.
    The label is whether the municipality shows NEW olive decline
    (NDVI drop) within the next 12 months.

    Args:
        n_municipalities: Total number of municipalities to generate.
            If None, uses realistic counts per province.
        prediction_year: The year from which we predict 12-month decline.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with features and binary decline label.
    """
    rng = np.random.RandomState(seed)
    rows = []
    muni_id = 0

    for province in ALL_PROVINCES:
        if n_municipalities is not None:
            n_muni = max(5, int(n_municipalities *
                                MUNICIPALITIES_PER_PROVINCE[province] /
                                sum(MUNICIPALITIES_PER_PROVINCE.values())))
        else:
            n_muni = MUNICIPALITIES_PER_PROVINCE[province]

        prov_lat, prov_lon = PROVINCE_COORDS[province]
        prov_elev = PROVINCE_ELEVATION[province]
        jan_tmin_mean, jan_tmin_std, precip_mean, precip_std = \
            PROVINCE_CLIMATE[province]
        detection_year = FIRST_DETECTION_YEAR[province]
        olive_frac = OLIVE_FRACTION[province]

        for i in range(n_muni):
            muni_id += 1

            # Geographic features with intra-province variation
            lat = prov_lat + rng.normal(0, 0.15)
            lon = prov_lon + rng.normal(0, 0.15)
            elevation = max(5, prov_elev + rng.normal(0, 40))

            # Climate features
            jan_tmin = jan_tmin_mean + rng.normal(0, jan_tmin_std)
            annual_precip = max(100, precip_mean + rng.normal(0, precip_std))

            # Winter climate features
            frost_days_below_minus6 = max(0, rng.poisson(
                max(0.1, 3.0 - jan_tmin * 0.8)))
            frost_days_below_minus12 = max(0, rng.poisson(
                max(0.01, 0.5 - jan_tmin * 0.3)))
            winter_tmin = jan_tmin - rng.exponential(2.0)
            coldest_month_anomaly = rng.normal(0, 1.2)

            # Precipitation deficit (relative to 1991-2020 mean)
            precip_deficit = rng.normal(0, 0.15)  # fraction
            summer_precip = max(10, annual_precip * 0.1 +
                                rng.normal(0, 20))

            # Distance from epicentre (Lecce for Italian, Alicante for Spanish)
            if province in PUGLIA_PROVINCES:
                epicentre_lat, epicentre_lon = PROVINCE_COORDS["Lecce"]
            else:
                epicentre_lat, epicentre_lon = PROVINCE_COORDS["Alicante"]
            dist_epicentre = _haversine_km(lat, lon,
                                           epicentre_lat, epicentre_lon)

            # NDVI features (healthy olive grove NDVI ~ 0.35-0.55)
            # Declining groves show NDVI 0.15-0.30
            base_ndvi = 0.42 + rng.normal(0, 0.05)

            # If already affected, reduce NDVI
            years_since_detection = (prediction_year - detection_year
                                     if detection_year is not None
                                     else None)
            already_affected = (detection_year is not None and
                                detection_year <= prediction_year)

            if already_affected and years_since_detection is not None:
                # Progressive decline with distance from epicentre
                decline_prob_from_time = min(0.95,
                    years_since_detection * 0.12)
                # Municipalities closer to epicentre decline earlier
                within_province_decline = rng.random() < decline_prob_from_time
                if within_province_decline:
                    ndvi_mean = base_ndvi - rng.uniform(0.08, 0.20)
                    ndvi_trend = -rng.uniform(0.01, 0.04)  # per year
                else:
                    ndvi_mean = base_ndvi
                    ndvi_trend = rng.normal(0, 0.005)
            else:
                ndvi_mean = base_ndvi
                ndvi_trend = rng.normal(0, 0.005)

            ndvi_anomaly = rng.normal(0, 0.03)
            ndvi_std = 0.04 + rng.exponential(0.01)
            evi_mean = ndvi_mean * 0.65 + rng.normal(0, 0.02)

            # Olive grove area fraction
            olive_area_frac = max(0, olive_frac + rng.normal(0, 0.08))

            # Distance to nearest already-declining municipality
            # (simplified: based on province-level detection)
            if already_affected:
                dist_nearest_declining = rng.exponential(5)  # km
            elif detection_year is not None:
                dist_nearest_declining = dist_epicentre * 0.3 + \
                    rng.exponential(20)
            else:
                dist_nearest_declining = dist_epicentre + rng.exponential(50)

            # Country indicator
            country = "Italy" if province in PUGLIA_PROVINCES else "Spain"

            # ---- LABEL: will this municipality show NEW decline in next 12 months? ----
            # Three mechanisms determine decline probability:
            # (a) Frost-kill: very cold winters protect (low Tmin = low risk)
            # (b) Diffusion: closer to already-declining areas = higher risk
            # (c) Already declined: can't decline again

            if already_affected and within_province_decline if already_affected else False:
                # Already declined - label is 0 (no NEW decline)
                label = 0
            else:
                # Diffusion component (strongest predictor in reality)
                diffusion_risk = np.clip(1.0 / (1.0 + dist_nearest_declining / 20.0), 0, 1)

                # Frost component (protective)
                frost_protection = np.clip(frost_days_below_minus6 * 0.08, 0, 0.6)

                # Winter Tmin component
                tmin_protection = np.clip((jan_tmin - 5.0) * (-0.05), -0.2, 0.3)

                # Combine mechanisms
                risk = (0.55 * diffusion_risk +
                        0.25 * (1 - frost_protection) +
                        0.15 * (1 - tmin_protection) +
                        0.05 * olive_area_frac)

                # Add noise
                risk += rng.normal(0, 0.08)
                risk = np.clip(risk, 0, 1)

                # Province-level calibration: match known timeline
                if detection_year is not None:
                    years_until_detection = detection_year - prediction_year
                    if years_until_detection <= 1 and years_until_detection > 0:
                        risk *= 1.5
                    elif years_until_detection <= 0:
                        risk *= 1.2

                label = 1 if risk > 0.5 else 0

            rows.append({
                "municipality_id": f"M{muni_id:04d}",
                "province": province,
                "country": country,
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "elevation": round(elevation, 1),
                "prediction_year": prediction_year,
                # Climate features
                "jan_tmin_mean": round(jan_tmin, 2),
                "winter_tmin_abs": round(winter_tmin, 2),
                "annual_precip_mm": round(annual_precip, 1),
                "summer_precip_mm": round(summer_precip, 1),
                "precip_deficit_frac": round(precip_deficit, 3),
                "frost_days_below_minus6": frost_days_below_minus6,
                "frost_days_below_minus12": frost_days_below_minus12,
                "coldest_month_anomaly": round(coldest_month_anomaly, 2),
                # NDVI features
                "ndvi_mean": round(ndvi_mean, 4),
                "ndvi_trend": round(ndvi_trend, 4),
                "ndvi_anomaly": round(ndvi_anomaly, 4),
                "ndvi_std": round(ndvi_std, 4),
                "evi_mean": round(evi_mean, 4),
                # Spatial features
                "dist_epicentre_km": round(dist_epicentre, 1),
                "dist_nearest_declining_km": round(dist_nearest_declining, 1),
                "olive_area_fraction": round(olive_area_frac, 3),
                # Already affected flag
                "already_affected": int(already_affected),
                # Label
                "new_decline_12m": label,
            })

    df = pd.DataFrame(rows)
    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to the raw dataset.

    Args:
        df: DataFrame from generate_synthetic_data().

    Returns:
        DataFrame with additional derived columns.
    """
    df = df.copy()

    # NDVI x Tmin interaction
    df["ndvi_x_jan_tmin"] = df["ndvi_mean"] * df["jan_tmin_mean"]

    # Log distance to epicentre
    df["log_dist_epicentre"] = np.log1p(df["dist_epicentre_km"])

    # Log distance to nearest declining area
    df["log_dist_nearest_declining"] = np.log1p(
        df["dist_nearest_declining_km"])

    # Frost severity index (combines both thresholds)
    df["frost_severity_index"] = (df["frost_days_below_minus6"] +
                                  3 * df["frost_days_below_minus12"])

    # Aridity index (annual precip / potential ET approximation)
    df["aridity_proxy"] = df["annual_precip_mm"] / (
        600 + 50 * df["jan_tmin_mean"])  # simplified Thornthwaite

    # NDVI decline rate relative to baseline
    df["ndvi_decline_rate"] = df["ndvi_trend"] / (df["ndvi_mean"] + 0.01)

    # Latitude-based expansion proxy (linear distance from 40.0 N)
    df["lat_from_salento"] = df["latitude"] - 40.0

    # Province encoded as ordinal (south to north)
    province_order = {p: i for i, p in enumerate(ALL_PROVINCES)}
    df["province_ordinal"] = df["province"].map(province_order)

    # Green-up timing proxy (colder = later green-up)
    df["greenup_proxy"] = np.clip(
        120 - df["jan_tmin_mean"] * 8 + df["elevation"] * 0.02,
        80, 160)  # day of year

    # Soil moisture proxy (precip - ET)
    df["soil_moisture_proxy"] = (df["annual_precip_mm"] -
                                 df["summer_precip_mm"] * 3)

    return df


def get_cv_folds_spatial(
    df: pd.DataFrame,
    n_folds: int = 5,
    seed: int = 42,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Create spatial cross-validation folds grouped by province.

    Each fold holds out entire provinces to prevent spatial leakage.

    Args:
        df: DataFrame with 'province' column.
        n_folds: Number of CV folds.
        seed: Random seed for fold assignment.

    Returns:
        List of (train_idx, val_idx) tuples.
    """
    rng = np.random.RandomState(seed)
    provinces = df["province"].unique().tolist()
    rng.shuffle(provinces)

    # Assign provinces to folds (round-robin)
    fold_assignment = {}
    for i, prov in enumerate(provinces):
        fold_assignment[prov] = i % n_folds

    folds = []
    for fold_id in range(n_folds):
        val_provinces = [p for p, f in fold_assignment.items()
                         if f == fold_id]
        val_mask = df["province"].isin(val_provinces)
        train_idx = df.index[~val_mask].values
        val_idx = df.index[val_mask].values
        folds.append((train_idx, val_idx))

    return folds


def get_train_test_split(
    df: pd.DataFrame,
    test_fraction: float = 0.15,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataset into train and test sets, grouped by province.

    Holds out entire provinces for the test set.

    Args:
        df: Full DataFrame.
        test_fraction: Approximate fraction of data for testing.
        seed: Random seed.

    Returns:
        (train_df, test_df) tuple.
    """
    rng = np.random.RandomState(seed)
    provinces = df["province"].unique().tolist()
    rng.shuffle(provinces)

    # Accumulate provinces until test_fraction reached
    test_provinces = []
    test_count = 0
    total = len(df)
    for prov in provinces:
        if test_count / total < test_fraction:
            test_provinces.append(prov)
            test_count += len(df[df["province"] == prov])
        else:
            break

    test_mask = df["province"].isin(test_provinces)
    return df[~test_mask].reset_index(drop=True), \
           df[test_mask].reset_index(drop=True)


def load_dataset(
    n_municipalities: Optional[int] = None,
    prediction_year: int = 2024,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate and prepare the full dataset with derived features.

    This is the main entry point for other modules.

    Args:
        n_municipalities: Number of municipalities (None for realistic).
        prediction_year: Year for prediction.
        seed: Random seed.

    Returns:
        DataFrame with all features and labels.
    """
    df = generate_synthetic_data(
        n_municipalities=n_municipalities,
        prediction_year=prediction_year,
        seed=seed,
    )
    df = add_derived_features(df)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Xylella olive decline dataset")
    parser.add_argument("--info", action="store_true",
                        help="Print detailed statistics")
    parser.add_argument("-n", type=int, default=None,
                        help="Number of municipalities")
    args = parser.parse_args()

    df = load_dataset(n_municipalities=args.n)
    print(f"Generated dataset: {len(df)} municipalities")
    print(f"Columns: {list(df.columns)}")
    print(f"\nLabel distribution:")
    print(df["new_decline_12m"].value_counts())
    print(f"\nProvince distribution:")
    print(df["province"].value_counts())
    print(f"\nCountry distribution:")
    print(df["country"].value_counts())

    if args.info:
        print(f"\n--- Detailed Statistics ---")
        print(df.describe().T[["mean", "std", "min", "max"]])
        print(f"\nDecline rate by province:")
        print(df.groupby("province")["new_decline_12m"].mean().sort_values(
            ascending=False))
        print(f"\nAlready affected by province:")
        print(df.groupby("province")["already_affected"].mean())
