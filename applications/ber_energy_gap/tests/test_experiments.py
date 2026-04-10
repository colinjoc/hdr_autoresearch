"""Tests for experiment pipeline."""
import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

PARQUET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "ber_raw.parquet"
)
HAS_DATA = os.path.exists(PARQUET_PATH)


class TestAddEngineeredFeatures:
    """Test that engineered features are valid."""

    @pytest.fixture
    def sample_data(self):
        """Create sample X and df_model for testing feature engineering."""
        from prepare import get_model_features
        n = 100
        rng = np.random.RandomState(42)

        features = get_model_features()
        X = pd.DataFrame(
            rng.randn(n, len(features)) * 10 + 50,
            columns=features
        )
        # Make physically sensible values
        X["uvaluewall"] = rng.uniform(0.1, 2.5, n)
        X["uvalueroof"] = rng.uniform(0.1, 1.0, n)
        X["uvaluefloor"] = rng.uniform(0.1, 1.0, n)
        X["uvaluewindow"] = rng.uniform(1.0, 5.0, n)
        X["uvaluedoor"] = rng.uniform(1.0, 3.0, n)
        X["ground_floor_area"] = rng.uniform(40, 300, n)
        X["wall_area"] = rng.uniform(50, 300, n)
        X["roof_area"] = rng.uniform(30, 200, n)
        X["floor_area"] = rng.uniform(40, 300, n)
        X["window_area"] = rng.uniform(10, 60, n)
        X["door_area"] = rng.uniform(2, 10, n)
        X["year_built"] = rng.randint(1900, 2024, n).astype(float)
        X["hs_efficiency"] = rng.uniform(60, 400, n)
        X["envelope_u_avg"] = rng.uniform(0.3, 2.0, n)
        X["no_chimneys"] = rng.choice([0, 1, 2], n).astype(float)
        X["no_open_flues"] = rng.choice([0, 1], n).astype(float)
        X["permeability_result"] = rng.uniform(0, 15, n)
        X["hlp_proxy"] = rng.uniform(0.5, 5.0, n)
        X["is_heat_pump"] = rng.choice([0, 1], n).astype(float)

        df_model = pd.DataFrame({
            "fuel_group": rng.choice(["gas", "oil", "electricity", "solid"], n),
            "sh_fraction": rng.uniform(0.3, 0.9, n),
            "ber_kwh_m2": rng.uniform(30, 500, n),
            "energy_rating": rng.choice(["A2", "B2", "C2", "D1", "E1", "G"], n),
            "is_heat_pump": X["is_heat_pump"].values,
            "county": rng.choice(["Dublin", "Cork", "Galway"], n),
            "dwelling_type": rng.choice(["Detached house", "Semi-detached house"], n),
            "age_category": rng.choice(["pre-1930", "1978-2005", "2006-2011"], n),
        })

        return X, df_model

    def test_compactness_ratio(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        X_out = add_engineered_features(X, df_model)
        assert "compactness_ratio" in X_out.columns
        assert X_out["compactness_ratio"].notna().all()
        assert (X_out["compactness_ratio"] > 0).all()

    def test_wall_era_interaction(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        X_out = add_engineered_features(X, df_model)
        assert "wall_era_interaction" in X_out.columns
        assert X_out["wall_era_interaction"].notna().all()

    def test_heating_fabric_interaction(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        X_out = add_engineered_features(X, df_model)
        assert "heating_fabric_interaction" in X_out.columns
        assert X_out["heating_fabric_interaction"].notna().all()

    def test_primary_energy_factor(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        X_out = add_engineered_features(X, df_model)
        assert "primary_energy_factor" in X_out.columns
        # PE factors should be between 0.5 and 3
        assert (X_out["primary_energy_factor"] >= 0.5).all()
        assert (X_out["primary_energy_factor"] <= 3.0).all()

    def test_no_nan_in_output(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        X_out = add_engineered_features(X, df_model)
        for col in X_out.columns:
            assert X_out[col].notna().all(), f"NaN found in {col}"

    def test_original_features_preserved(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        original_cols = set(X.columns)
        X_out = add_engineered_features(X, df_model)
        # All original columns should still be present
        for col in original_cols:
            assert col in X_out.columns, f"Lost original column {col}"

    def test_feature_count_increases(self, sample_data):
        from run_experiments import add_engineered_features
        X, df_model = sample_data
        X_out = add_engineered_features(X, df_model)
        assert X_out.shape[1] > X.shape[1]


@pytest.mark.skipif(not HAS_DATA, reason="BER data not downloaded")
class TestIntegrationWithRealData:
    """Integration tests using real BER data."""

    @pytest.fixture(scope="class")
    def real_data(self):
        from prepare import load_raw, clean_and_feature_engineer, prepare_modelling_data
        raw = load_raw()
        clean = clean_and_feature_engineer(raw)
        X, y, df_model = prepare_modelling_data(clean)
        # Use a small subsample for speed
        rng = np.random.RandomState(42)
        idx = rng.choice(len(X), 5000, replace=False)
        return X.iloc[idx].reset_index(drop=True), y[idx], df_model.iloc[idx].reset_index(drop=True)

    def test_engineered_features_on_real_data(self, real_data):
        from run_experiments import add_engineered_features
        X, y, df_model = real_data
        X_out = add_engineered_features(X, df_model)
        assert X_out.shape[0] == X.shape[0]
        assert X_out.shape[1] > X.shape[1]
        # No NaN
        for col in X_out.columns:
            assert X_out[col].notna().all(), f"NaN in {col}"

    def test_lgbm_runs_on_enhanced_features(self, real_data):
        from run_experiments import add_engineered_features
        from model import lgbm_model
        from evaluate import cross_validate
        X, y, df_model = real_data
        X_out = add_engineered_features(X, df_model)
        metrics = cross_validate(lgbm_model, X_out, y, n_splits=3)
        assert metrics["r2"] > 0.8  # Should do reasonably well
        assert metrics["mae"] < 40  # Reasonable bound
