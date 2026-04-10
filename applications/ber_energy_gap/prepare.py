"""Data preparation for BER Energy Gap analysis.

Loads real SEAI BER certificate data and prepares features for modelling.
Target: BerRating (kWh/m2/yr) — the DEAP-calculated primary energy per m2.
"""
import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PARQUET_PATH = os.path.join(DATA_DIR, "ber_raw.parquet")


# BER band boundaries (kWh/m2/yr)
BER_BANDS = {
    "A1": (0, 25), "A2": (25, 50), "A3": (50, 75),
    "B1": (75, 100), "B2": (100, 125), "B3": (125, 150),
    "C1": (150, 175), "C2": (175, 200), "C3": (200, 225),
    "D1": (225, 260), "D2": (260, 300),
    "E1": (300, 340), "E2": (340, 380),
    "F": (380, 450), "G": (450, float("inf")),
}

# Ordinal encoding for BER bands
BER_ORDINAL = {
    "A1": 0, "A2": 1, "A3": 2,
    "B1": 3, "B2": 4, "B3": 5,
    "C1": 6, "C2": 7, "C3": 8,
    "D1": 9, "D2": 10,
    "E1": 11, "E2": 12,
    "F": 13, "G": 14,
}

# Fuel type grouping
FUEL_GROUPS = {
    "Mains Gas": "gas",
    "Heating Oil": "oil",
    "Electricity": "electricity",
    "Bulk LPG (propane or butane)": "lpg",
    "Bottled LPG": "lpg",
    "Solid Multi-Fuel": "solid",
    "Manufactured Smokeless Fuel": "solid",
    "House Coal": "solid",
    "Anthracite": "solid",
    "Sod Peat": "solid",
    "Peat Briquettes": "solid",
    "Wood Logs": "wood",
    "Wood Pellets (bulk supply for": "wood",
    "Wood Pellets (in bags for seco": "wood",
    "Wood Chips": "wood",
}

# County normalisation (Dublin postal districts -> Dublin)
def normalise_county(s):
    """Map Dublin postal districts and city names to standard county."""
    if pd.isna(s):
        return "Unknown"
    s = str(s).strip()
    if s.startswith("Dublin") or s == "Dublin City":
        return "Dublin"
    if s.startswith("Co. "):
        return s[4:]
    if s.endswith(" City"):
        return s[:-5]
    return s


def load_raw():
    """Load raw BER data from parquet."""
    if not os.path.exists(PARQUET_PATH):
        raise FileNotFoundError(
            f"BER data not found at {PARQUET_PATH}. Run download_data.py first."
        )
    return pd.read_parquet(PARQUET_PATH)


def clean_and_feature_engineer(df):
    """Clean data and engineer features for BER prediction.

    Returns DataFrame with features + target (ber_kwh_m2).
    """
    out = pd.DataFrame()

    # Target: BER rating in kWh/m2/yr
    out["ber_kwh_m2"] = pd.to_numeric(df["BerRating"], errors="coerce")

    # Energy rating (letter grade)
    out["energy_rating"] = df["EnergyRating"].astype(str).str.strip()
    out["energy_rating_ordinal"] = out["energy_rating"].map(BER_ORDINAL)

    # Building envelope U-values (W/m2K)
    for col in ["UValueWall", "UValueRoof", "UValueFloor", "UValueWindow", "UvalueDoor"]:
        out[col.lower()] = pd.to_numeric(df[col], errors="coerce")

    # Areas
    out["ground_floor_area"] = pd.to_numeric(df["GroundFloorArea(sq m)"], errors="coerce")
    out["wall_area"] = pd.to_numeric(df["WallArea"], errors="coerce")
    out["roof_area"] = pd.to_numeric(df["RoofArea"], errors="coerce")
    out["floor_area"] = pd.to_numeric(df["FloorArea"], errors="coerce")
    out["window_area"] = pd.to_numeric(df["WindowArea"], errors="coerce")
    out["door_area"] = pd.to_numeric(df["DoorArea"], errors="coerce")

    # Construction
    out["year_built"] = pd.to_numeric(df["Year_of_Construction"], errors="coerce")
    out["no_storeys"] = pd.to_numeric(df["NoStoreys"], errors="coerce")

    # Dwelling type
    out["dwelling_type"] = df["DwellingTypeDescr"].astype(str).str.strip()

    # County
    out["county"] = df["CountyName"].apply(normalise_county)

    # Heating
    out["main_sh_fuel"] = df["MainSpaceHeatingFuel"].astype(str).str.strip()
    out["fuel_group"] = out["main_sh_fuel"].map(FUEL_GROUPS).fillna("other")
    out["hs_efficiency"] = pd.to_numeric(df["HSMainSystemEfficiency"], errors="coerce")

    # Ventilation
    out["ventilation"] = df["VentilationMethod"].astype(str).str.strip()
    out["is_mechanical_vent"] = out["ventilation"].str.contains(
        "mech|Bal", case=False, na=False
    ).astype(int)

    # Structure type
    out["structure_type"] = df["StructureType"].astype(str).str.strip()

    # Thermal bridging
    out["thermal_bridging"] = pd.to_numeric(df["ThermalBridgingFactor"], errors="coerce")

    # Lighting
    out["low_energy_lighting_pct"] = pd.to_numeric(
        df["LowEnergyLightingPercent"], errors="coerce"
    )

    # Energy breakdown (delivered kWh)
    out["delivered_space_heating"] = pd.to_numeric(
        df["DeliveredEnergyMainSpace"], errors="coerce"
    )
    out["delivered_water_heating"] = pd.to_numeric(
        df["DeliveredEnergyMainWater"], errors="coerce"
    )
    out["delivered_lighting"] = pd.to_numeric(
        df["DeliveredLightingEnergy"], errors="coerce"
    )
    out["delivered_pumps_fans"] = pd.to_numeric(
        df["DeliveredEnergyPumpsFans"], errors="coerce"
    )
    out["total_delivered_energy"] = pd.to_numeric(
        df["TotalDeliveredEnergy"], errors="coerce"
    )

    # Primary energy components
    out["primary_space_heating"] = pd.to_numeric(
        df["PrimaryEnergyMainSpace"], errors="coerce"
    )
    out["primary_water_heating"] = pd.to_numeric(
        df["PrimaryEnergyMainWater"], errors="coerce"
    )
    out["primary_lighting"] = pd.to_numeric(
        df["PrimaryEnergyLighting"], errors="coerce"
    )

    # CO2
    out["co2_total"] = pd.to_numeric(df["CO2Rating"], errors="coerce")

    # Type of rating
    out["type_of_rating"] = df["TypeofRating"].astype(str).str.strip()

    # Chimneys and draughtproofing
    out["no_chimneys"] = pd.to_numeric(df["NoOfChimneys"], errors="coerce")
    out["no_open_flues"] = pd.to_numeric(df["NoOfOpenFlues"], errors="coerce")
    out["draft_lobby"] = (df["DraftLobby"].astype(str).str.strip().str.upper() == "YES").astype(int)
    out["pct_draught_stripped"] = pd.to_numeric(
        df["PercentageDraughtStripped"], errors="coerce"
    )

    # Permeability
    out["permeability_tested"] = (
        df["PermeabilityTest"].astype(str).str.strip().str.upper() == "YES"
    ).astype(int)
    out["permeability_result"] = pd.to_numeric(
        df["PermeabilityTestResult"], errors="coerce"
    )

    # Derived features
    # Window-to-wall ratio
    with np.errstate(divide="ignore", invalid="ignore"):
        out["window_wall_ratio"] = np.where(
            out["wall_area"] > 0,
            out["window_area"] / out["wall_area"],
            np.nan,
        )

    # Envelope average U-value (area-weighted)
    total_env_area = (
        out["wall_area"].fillna(0)
        + out["roof_area"].fillna(0)
        + out["floor_area"].fillna(0)
        + out["window_area"].fillna(0)
        + out["door_area"].fillna(0)
    )
    weighted_u = (
        out["wall_area"].fillna(0) * out["uvaluewall"].fillna(0)
        + out["roof_area"].fillna(0) * out["uvalueroof"].fillna(0)
        + out["floor_area"].fillna(0) * out["uvaluefloor"].fillna(0)
        + out["window_area"].fillna(0) * out["uvaluewindow"].fillna(0)
        + out["door_area"].fillna(0) * out["uvaluedoor"].fillna(0)
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        out["envelope_u_avg"] = np.where(
            total_env_area > 0, weighted_u / total_env_area, np.nan
        )

    # Heat loss parameter (HLP) proxy: total U*A / floor_area
    with np.errstate(divide="ignore", invalid="ignore"):
        out["hlp_proxy"] = np.where(
            out["ground_floor_area"] > 0,
            weighted_u / out["ground_floor_area"],
            np.nan,
        )

    # Building age category
    out["age_category"] = pd.cut(
        out["year_built"],
        bins=[0, 1930, 1978, 2006, 2012, 2021, 2200],
        labels=["pre-1930", "1930-1977", "1978-2005", "2006-2011", "2012-2020", "2021+"],
    )

    # Is heat pump? (efficiency > 100% indicates COP > 1)
    out["is_heat_pump"] = (out["hs_efficiency"] > 100).astype(int)

    # Space heating as fraction of total
    with np.errstate(divide="ignore", invalid="ignore"):
        out["sh_fraction"] = np.where(
            out["total_delivered_energy"] > 0,
            out["delivered_space_heating"] / out["total_delivered_energy"],
            np.nan,
        )

    return out


def get_model_features():
    """Return list of numeric feature columns for modelling."""
    return [
        "uvaluewall", "uvalueroof", "uvaluefloor", "uvaluewindow", "uvaluedoor",
        "ground_floor_area", "wall_area", "roof_area", "floor_area",
        "window_area", "door_area",
        "year_built", "no_storeys",
        "hs_efficiency",
        "is_mechanical_vent",
        "thermal_bridging",
        "low_energy_lighting_pct",
        "no_chimneys", "no_open_flues",
        "draft_lobby", "pct_draught_stripped",
        "permeability_tested", "permeability_result",
        "window_wall_ratio",
        "envelope_u_avg",
        "hlp_proxy",
        "is_heat_pump",
    ]


def get_categorical_features():
    """Return list of categorical feature columns."""
    return ["dwelling_type", "county", "fuel_group", "structure_type", "age_category"]


def prepare_modelling_data(df_clean, target="ber_kwh_m2", drop_outliers=True):
    """Prepare X, y for modelling.

    Filters to valid records, encodes categoricals, returns feature matrix + target.
    """
    df = df_clean.copy()

    # Filter: must have valid target
    df = df[df[target].notna() & (df[target] > 0) & (df[target] < 1000)]

    if drop_outliers:
        # Remove extreme outliers (>3 IQR from median)
        q1 = df[target].quantile(0.01)
        q99 = df[target].quantile(0.99)
        df = df[(df[target] >= q1) & (df[target] <= q99)]

    # Numeric features
    num_features = get_model_features()

    # Categorical features — one-hot encode
    cat_features = get_categorical_features()

    X_num = df[num_features].copy()

    # One-hot encode categoricals
    X_cat = pd.get_dummies(df[cat_features], drop_first=True, dtype=float)

    X = pd.concat([X_num, X_cat], axis=1)
    y = df[target].values

    # Fill NaN with median for numeric columns
    for col in X.columns:
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].median())

    return X, y, df


if __name__ == "__main__":
    print("Loading raw BER data...")
    raw = load_raw()
    print(f"Raw records: {len(raw):,}")

    print("Cleaning and engineering features...")
    clean = clean_and_feature_engineer(raw)
    print(f"Clean records: {len(clean):,}")

    print("Preparing modelling data...")
    X, y, df_model = prepare_modelling_data(clean)
    print(f"Model records: {len(X):,}")
    print(f"Features: {X.shape[1]}")
    print(f"Target stats: mean={y.mean():.1f}, std={y.std():.1f}")
