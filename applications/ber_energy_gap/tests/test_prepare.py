"""Tests for data preparation module."""
import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from prepare import (
    BER_BANDS, BER_ORDINAL, FUEL_GROUPS,
    normalise_county, clean_and_feature_engineer,
    get_model_features, get_categorical_features,
    prepare_modelling_data, load_raw,
)

PARQUET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ber_raw.parquet")
HAS_DATA = os.path.exists(PARQUET_PATH)


# --- Unit tests (no data required) ---

class TestBERBands:
    def test_all_15_bands(self):
        assert len(BER_BANDS) == 15

    def test_band_boundaries_contiguous(self):
        bands = ["A1", "A2", "A3", "B1", "B2", "B3",
                 "C1", "C2", "C3", "D1", "D2", "E1", "E2", "F", "G"]
        for i in range(len(bands) - 1):
            _, upper = BER_BANDS[bands[i]]
            lower, _ = BER_BANDS[bands[i + 1]]
            assert upper == lower, f"Gap between {bands[i]} and {bands[i+1]}"

    def test_ordinal_monotonic(self):
        bands = ["A1", "A2", "A3", "B1", "B2", "B3",
                 "C1", "C2", "C3", "D1", "D2", "E1", "E2", "F", "G"]
        for i in range(len(bands) - 1):
            assert BER_ORDINAL[bands[i]] < BER_ORDINAL[bands[i + 1]]


class TestNormaliseCounty:
    def test_dublin_postal_districts(self):
        assert normalise_county("Dublin 15") == "Dublin"
        assert normalise_county("Dublin 6") == "Dublin"

    def test_county_prefix(self):
        assert normalise_county("Co. Cork") == "Cork"
        assert normalise_county("Co. Galway") == "Galway"

    def test_city_suffix(self):
        assert normalise_county("Cork City") == "Cork"
        assert normalise_county("Galway City") == "Galway"

    def test_nan(self):
        assert normalise_county(None) == "Unknown"
        assert normalise_county(np.nan) == "Unknown"


class TestFuelGroups:
    def test_main_fuels_mapped(self):
        assert FUEL_GROUPS["Mains Gas"] == "gas"
        assert FUEL_GROUPS["Heating Oil"] == "oil"
        assert FUEL_GROUPS["Electricity"] == "electricity"


class TestCleanAndFeatureEngineer:
    """Test feature engineering on a minimal synthetic DataFrame."""

    @pytest.fixture
    def minimal_df(self):
        return pd.DataFrame({
            "BerRating": ["150.0", "300.0", "50.0"],
            "EnergyRating": ["C1", "E1", "A3"],
            "UValueWall": ["0.5", "1.5", "0.2"],
            "UValueRoof": ["0.3", "0.8", "0.1"],
            "UValueFloor": ["0.4", "0.6", "0.15"],
            "UValueWindow": ["2.0", "3.0", "1.0"],
            "UvalueDoor": ["2.0", "3.0", "1.5"],
            "GroundFloorArea(sq m)": ["100", "80", "120"],
            "WallArea": ["100", "80", "120"],
            "RoofArea": ["50", "40", "60"],
            "FloorArea": ["100", "80", "120"],
            "WindowArea": ["20", "15", "25"],
            "DoorArea": ["5", "4", "6"],
            "Year_of_Construction": ["2010", "1960", "2020"],
            "NoStoreys": ["2", "1", "2"],
            "DwellingTypeDescr": ["Semi-detached house", "Detached house", "Mid-terrace house"],
            "CountyName": ["Dublin 15", "Co. Cork", "Galway City"],
            "MainSpaceHeatingFuel": ["Mains Gas", "Heating Oil", "Electricity"],
            "HSMainSystemEfficiency": ["90", "80", "350"],
            "VentilationMethod": ["Natural vent.", "Natural vent.", "Bal.whole mech.vent heat recvr"],
            "StructureType": ["Masonry", "Masonry", "Timber or Steel Frame"],
            "ThermalBridgingFactor": ["0.08", "0.15", "0.05"],
            "LowEnergyLightingPercent": ["50", "10", "100"],
            "DeliveredEnergyMainSpace": ["5000", "12000", "2000"],
            "DeliveredEnergyMainWater": ["2000", "3000", "1500"],
            "DeliveredLightingEnergy": ["300", "500", "200"],
            "DeliveredEnergyPumpsFans": ["100", "50", "200"],
            "TotalDeliveredEnergy": ["10000", "20000", "5000"],
            "PrimaryEnergyMainSpace": ["6000", "15000", "2500"],
            "PrimaryEnergyMainWater": ["2500", "3500", "1800"],
            "PrimaryEnergyLighting": ["400", "600", "250"],
            "CO2Rating": ["30", "70", "15"],
            "TypeofRating": ["Existing", "Existing", "Final"],
            "NoOfChimneys": ["0", "2", "0"],
            "NoOfOpenFlues": ["0", "1", "0"],
            "DraftLobby": ["NO", "NO", "YES"],
            "PercentageDraughtStripped": ["80", "0", "100"],
            "PermeabilityTest": ["NO", "NO", "YES"],
            "PermeabilityTestResult": ["0", "0", "3.5"],
        })

    def test_target_column(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert "ber_kwh_m2" in result.columns
        np.testing.assert_array_almost_equal(
            result["ber_kwh_m2"].values, [150.0, 300.0, 50.0]
        )

    def test_ordinal_encoding(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert result["energy_rating_ordinal"].iloc[0] == BER_ORDINAL["C1"]
        assert result["energy_rating_ordinal"].iloc[1] == BER_ORDINAL["E1"]

    def test_county_normalisation(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert result["county"].iloc[0] == "Dublin"
        assert result["county"].iloc[1] == "Cork"
        assert result["county"].iloc[2] == "Galway"

    def test_fuel_group(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert result["fuel_group"].iloc[0] == "gas"
        assert result["fuel_group"].iloc[1] == "oil"
        assert result["fuel_group"].iloc[2] == "electricity"

    def test_heat_pump_detection(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert result["is_heat_pump"].iloc[0] == 0  # gas, eff=90
        assert result["is_heat_pump"].iloc[2] == 1  # electricity, eff=350

    def test_envelope_u_avg(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert result["envelope_u_avg"].notna().all()
        # Row 0: weighted average should be between min and max U-values
        assert 0.2 < result["envelope_u_avg"].iloc[0] < 2.1

    def test_window_wall_ratio(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        # Row 0: 20/100 = 0.2
        np.testing.assert_almost_equal(result["window_wall_ratio"].iloc[0], 0.2)

    def test_mechanical_vent(self, minimal_df):
        result = clean_and_feature_engineer(minimal_df)
        assert result["is_mechanical_vent"].iloc[0] == 0
        assert result["is_mechanical_vent"].iloc[2] == 1


class TestPrepareModellingData:
    def test_filters_invalid_target(self):
        df = pd.DataFrame({
            "ber_kwh_m2": [100, -50, np.nan, 200, 5000],
            "energy_rating": ["B2", "X", "C1", "C3", "G"],
        })
        # Add minimal features
        for feat in get_model_features() + get_categorical_features():
            if feat not in df.columns:
                df[feat] = 0

        X, y, _ = prepare_modelling_data(df, drop_outliers=False)
        # Should exclude negative, nan, and >1000
        assert len(y) == 2  # 100 and 200


# --- Integration tests (require real data) ---

@pytest.mark.skipif(not HAS_DATA, reason="BER data not downloaded")
class TestWithRealData:
    @pytest.fixture(scope="class")
    def raw_df(self):
        return load_raw()

    @pytest.fixture(scope="class")
    def clean_df(self, raw_df):
        return clean_and_feature_engineer(raw_df)

    def test_raw_shape(self, raw_df):
        assert raw_df.shape[0] > 1_000_000
        assert raw_df.shape[1] == 211

    def test_clean_has_target(self, clean_df):
        assert "ber_kwh_m2" in clean_df.columns
        valid = clean_df["ber_kwh_m2"].notna()
        assert valid.sum() > 1_000_000

    def test_all_ber_bands_present(self, clean_df):
        bands = clean_df["energy_rating"].unique()
        for b in ["A1", "A2", "A3", "B1", "B2", "B3",
                   "C1", "C2", "C3", "D1", "D2", "E1", "E2", "F", "G"]:
            assert b in bands, f"Missing band {b}"

    def test_modelling_data_shape(self, clean_df):
        X, y, _ = prepare_modelling_data(clean_df)
        assert len(X) > 900_000
        assert X.shape[1] > 30  # numeric + one-hot encoded
        assert len(y) == len(X)
        assert np.all(np.isfinite(X.values))

    def test_no_target_leakage(self, clean_df):
        """Model features must not include the target or energy rating."""
        X, y, _ = prepare_modelling_data(clean_df)
        for col in X.columns:
            assert "ber_kwh" not in col.lower()
            assert "energy_rating" not in col.lower()
            assert "berrating" not in col.lower()
