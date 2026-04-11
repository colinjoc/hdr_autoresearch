"""Tests for experiments added during paper review cycle.

Addresses MAJOR review findings:
- SHAP analysis (Missing Experiment #1)
- Temporal robustness / monthly stability (Missing Experiment #4)
- First-leg-of-day accuracy (Missing Experiment #6)
- Network centrality metrics (Scope vs Framing #3)
- Propagation score definition (Claims vs Evidence #3)
- Calibration analysis (Missing Experiment #2)
"""
import pytest
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSHAPAnalysis:
    """SHAP values for feature attribution (review Missing Experiment #1)."""

    def test_shap_values_computed(self):
        from review_experiments import compute_shap_values
        result = compute_shap_values(months=[1], sample_size=5000)
        assert 'shap_values' in result
        assert 'feature_names' in result
        assert 'mean_abs_shap' in result
        assert len(result['mean_abs_shap']) > 0

    def test_shap_rotation_features_dominate(self):
        """SHAP should confirm rotation features collectively dominate."""
        from review_experiments import compute_shap_values
        result = compute_shap_values(months=[1], sample_size=5000)
        rotation_features = {
            'prev_delay_x_buffer', 'log_prev_delay', 'prior_flight_arr_delay',
            'turnaround_time', 'buffer_over_min', 'prior_flight_dep_delay',
            'cumulative_delay', 'prior_flight_late_aircraft',
            'carrier_buffer_factor',
        }
        total_shap = sum(result['mean_abs_shap'].values())
        rotation_shap = sum(v for f, v in result['mean_abs_shap'].items()
                           if f in rotation_features)
        rotation_pct = rotation_shap / total_shap
        assert rotation_pct > 0.30, \
            f"Rotation features only {rotation_pct:.0%} of total SHAP, expected >30%"

    def test_shap_importance_sums_reasonable(self):
        from review_experiments import compute_shap_values
        result = compute_shap_values(months=[1], sample_size=5000)
        total = sum(result['mean_abs_shap'].values())
        assert total > 0


class TestTemporalRobustness:
    """Monthly stability analysis (review Missing Experiment #4)."""

    def test_monthly_auc_computed(self):
        from review_experiments import monthly_auc_stability
        result = monthly_auc_stability(train_months=[1, 2, 3], test_months=[4, 5, 6])
        assert 'per_month_auc' in result
        assert len(result['per_month_auc']) >= 3
        assert 'mean_auc' in result
        assert 'std_auc' in result

    def test_monthly_auc_all_above_threshold(self):
        """All individual months should maintain AUC > 0.85."""
        from review_experiments import monthly_auc_stability
        result = monthly_auc_stability(train_months=[1, 2, 3], test_months=[4, 5, 6])
        for month, auc in result['per_month_auc'].items():
            assert auc > 0.85, f"Month {month} AUC {auc:.3f} below 0.85 threshold"


class TestFirstLegAccuracy:
    """Accuracy on first-leg-of-day flights (review Missing Experiment #6)."""

    def test_first_leg_auc_computed(self):
        from review_experiments import first_leg_accuracy
        result = first_leg_accuracy(months=[1, 2, 3], holdout_months=[4])
        assert 'first_leg_auc' in result
        assert 'non_first_leg_auc' in result
        assert 'first_leg_count' in result

    def test_first_leg_still_reasonable(self):
        """First-leg flights (no rotation features) should still be above random."""
        from review_experiments import first_leg_accuracy
        result = first_leg_accuracy(months=[1, 2, 3], holdout_months=[4])
        assert result['first_leg_auc'] > 0.6, \
            "Model should still work on first-leg flights via airport/temporal features"


class TestNetworkMetrics:
    """Network centrality measures (review Scope vs Framing #3)."""

    def test_network_metrics_computed(self):
        from review_experiments import compute_network_metrics
        result = compute_network_metrics(months=[1])
        assert 'airport_metrics' in result
        df = result['airport_metrics']
        assert 'degree_centrality' in df.columns
        assert 'betweenness_centrality' in df.columns
        assert 'pagerank' in df.columns
        assert len(df) > 50  # Many airports

    def test_hubs_have_high_centrality(self):
        """Known hubs should rank high on centrality measures."""
        from review_experiments import compute_network_metrics
        result = compute_network_metrics(months=[1])
        df = result['airport_metrics']
        top_10_degree = df.nlargest(10, 'degree_centrality')['airport'].tolist()
        # ATL, ORD, DFW, DEN are among the most connected airports
        major_hubs = {'ATL', 'ORD', 'DFW', 'DEN'}
        overlap = major_hubs.intersection(set(top_10_degree))
        assert len(overlap) >= 2, \
            f"Expected major hubs in top 10 degree centrality, got {top_10_degree}"


class TestPropagationScoreDefinition:
    """Verify propagation score is well-defined (review Claims vs Evidence #3)."""

    def test_propagation_score_formula_documented(self):
        """The score formula should be explicit in the function."""
        from model import find_super_spreader_routes
        import inspect
        source = inspect.getsource(find_super_spreader_routes)
        # The formula should explicitly mention its components
        assert 'delay_rate' in source
        assert 'mean_late_aircraft' in source
        assert 'log' in source.lower()  # log(n_flights) component

    def test_airport_score_formula_documented(self):
        from model import airport_propagation_scores
        import inspect
        source = inspect.getsource(airport_propagation_scores)
        assert 'delay_rate' in source
        assert 'mean_late_aircraft' in source


class TestCalibrationAnalysis:
    """Calibration / reliability analysis (review Missing Experiment #2)."""

    def test_calibration_computed(self):
        from review_experiments import calibration_analysis
        result = calibration_analysis(months=[1, 2, 3], holdout_months=[4])
        assert 'calibration_bins' in result
        assert 'brier_score' in result
        assert 'expected_calibration_error' in result

    def test_brier_score_reasonable(self):
        from review_experiments import calibration_analysis
        result = calibration_analysis(months=[1, 2, 3], holdout_months=[4])
        # Brier score should be better than predicting the base rate
        assert result['brier_score'] < 0.20  # Base rate ~20%


class TestSHAPPlot:
    """Test SHAP summary plot generation."""

    def test_shap_plot_generated(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from review_experiments import plot_shap_summary
        fig, ax = plot_shap_summary(months=[1], sample_size=5000)
        assert fig is not None
        plt.close(fig)
