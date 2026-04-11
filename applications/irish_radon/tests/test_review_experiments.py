"""Tests for the review experiment script.

Verifies that each experiment function:
1. Runs without error on real data
2. Produces expected output types
3. Generates expected plot files
"""
import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(DATA_DIR, "epa_radon", "radon_grid_map.geojson")),
    reason="Data not downloaded yet"
)


@pytest.fixture(scope="module")
def dataset():
    from data_loaders import build_dataset
    return build_dataset()


class TestSHAP:
    def test_shap_returns_importance_dict(self, dataset):
        from run_review_experiments import experiment_shap
        X, y, groups = dataset
        shap_imp, shap_vals, features = experiment_shap(X, y, groups)
        assert isinstance(shap_imp, dict)
        assert len(shap_imp) > 0
        # All values are non-negative (mean absolute SHAP)
        assert all(v >= 0 for v in shap_imp.values())

    def test_shap_plot_created(self, dataset):
        from run_review_experiments import PLOTS_DIR
        assert (PLOTS_DIR / 'shap_importance.png').exists()
        assert (PLOTS_DIR / 'shap_beeswarm.png').exists()


class TestPrecisionRecall:
    def test_threshold_df_has_required_columns(self, dataset):
        from run_review_experiments import experiment_precision_recall
        X, y, groups = dataset
        df = experiment_precision_recall(X, y, groups)
        assert 'threshold' in df.columns
        assert 'precision' in df.columns
        assert 'recall' in df.columns
        assert 'f1' in df.columns

    def test_threshold_sensitivity_plot(self, dataset):
        from run_review_experiments import PLOTS_DIR
        assert (PLOTS_DIR / 'threshold_sensitivity.png').exists()


class TestRandomCV:
    def test_random_cv_inflates_metrics(self, dataset):
        from run_review_experiments import experiment_random_cv
        X, y, groups = dataset
        results = experiment_random_cv(X, y, groups)
        # Random CV should produce lower MAE than spatial CV
        assert results['random']['mae'] < results['spatial']['mae']
        # Random CV should produce higher F1 than spatial CV
        assert results['random']['f1'] >= results['spatial']['f1']


class TestCalibration:
    def test_calibration_returns_data(self, dataset):
        from run_review_experiments import experiment_calibration
        X, y, groups = dataset
        pred_means, actual_means, counts = experiment_calibration(X, y, groups)
        assert len(pred_means) > 3
        assert all(c > 0 for c in counts)

    def test_calibration_plot(self, dataset):
        from run_review_experiments import PLOTS_DIR
        assert (PLOTS_DIR / 'calibration.png').exists()
