"""Tests for evaluation harness."""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestEvaluationHarness:
    """Test the model evaluation pipeline."""

    def test_baseline_model_trains(self):
        from evaluate import train_and_evaluate
        results = train_and_evaluate(months=[1, 2], model_type='ridge')
        assert 'cv_auc' in results
        assert 'cv_f1' in results
        assert results['cv_auc'] > 0.5  # Better than random

    def test_xgboost_trains(self):
        from evaluate import train_and_evaluate
        results = train_and_evaluate(months=[1, 2], model_type='xgboost')
        assert results['cv_auc'] > 0.5

    def test_holdout_evaluation(self):
        from evaluate import train_and_evaluate
        results = train_and_evaluate(
            months=[1, 2, 3],
            model_type='ridge',
            holdout_months=[4],
        )
        assert 'holdout_auc' in results
        assert results['holdout_auc'] > 0.5

    def test_feature_importances_returned(self):
        from evaluate import train_and_evaluate
        results = train_and_evaluate(months=[1, 2], model_type='xgboost')
        assert 'feature_importances' in results
        assert len(results['feature_importances']) > 0

    def test_variance_decomposition(self):
        """Test that we can decompose delay variance into components."""
        from evaluate import decompose_delay_variance
        decomp = decompose_delay_variance(months=[1])
        assert 'rotation' in decomp  # LateAircraftDelay component
        assert 'weather' in decomp
        assert 'carrier' in decomp
        assert 'nas' in decomp  # NAS = National Airspace System (congestion/ATC)
        assert 'security' in decomp
        # Fractions should sum to ~1.0
        total = sum(decomp.values())
        assert 0.8 < total < 1.2  # Allow some slack for unexplained

    def test_propagation_depth_analysis(self):
        """Test that we can measure how far delays propagate through rotation chains."""
        from evaluate import measure_propagation_depth
        prop = measure_propagation_depth(months=[1])
        assert 'mean_depth' in prop
        assert 'max_depth' in prop
        assert 'containment_rate' in prop  # Fraction of delays that don't propagate
        assert prop['mean_depth'] >= 1.0
