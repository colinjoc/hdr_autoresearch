"""Tests for review-response experiments.

Validates that the four experiments demanded by the adversarial review
produce well-formed results:
  1. Emission factor sensitivity analysis
  2. Local density analysis near the 120 kg cement operating point
  3. Holdout test set evaluation (separate from CV)
  4. Bootstrap confidence intervals on CV metrics
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def review_results():
    """Run the review experiments once and return the results dict."""
    from review_experiments import run_all_experiments
    return run_all_experiments()


def test_emission_sensitivity_keys(review_results):
    """Sensitivity analysis must return results for at least 3 slag EF scenarios."""
    sens = review_results["emission_sensitivity"]
    assert len(sens) >= 3, f"Expected >=3 scenarios, got {len(sens)}"
    for row in sens:
        assert "slag_ef" in row
        assert "co2_kg_per_m3" in row
        assert "pct_reduction" in row
        assert 0 < row["co2_kg_per_m3"] < 500
        assert 0 < row["pct_reduction"] < 100


def test_emission_sensitivity_headline_range(review_results):
    """The headline % reduction should vary between ~45% and ~55% across EF scenarios."""
    sens = review_results["emission_sensitivity"]
    reductions = [r["pct_reduction"] for r in sens]
    assert min(reductions) < 50, f"Min reduction {min(reductions)} should be < 50%"
    assert max(reductions) > 50, f"Max reduction {max(reductions)} should be > 50%"


def test_local_density_has_counts(review_results):
    """Local density analysis must report sample counts near the operating point."""
    ld = review_results["local_density"]
    assert "n_samples_102_140" in ld
    assert "n_samples_100_160" in ld  # wider band
    assert "total_samples" in ld
    assert ld["total_samples"] == 1030
    assert ld["n_samples_102_140"] >= 0


def test_local_density_has_local_mae(review_results):
    """Local density analysis must report local CV error for the low-cement region."""
    ld = review_results["local_density"]
    assert "local_mae_102_140" in ld
    assert ld["local_mae_102_140"] > 0


def test_holdout_split_results(review_results):
    """Holdout test set must report MAE, RMSE, R2 on never-seen data."""
    ho = review_results["holdout"]
    assert "test_mae" in ho
    assert "test_rmse" in ho
    assert "test_r2" in ho
    assert "train_size" in ho
    assert "test_size" in ho
    # Sanity: test set should be ~15-20% of 1030
    assert 100 < ho["test_size"] < 300
    assert 700 < ho["train_size"] < 950
    # MAE should be reasonable (not wildly different from CV)
    assert 1.0 < ho["test_mae"] < 6.0


def test_bootstrap_ci_results(review_results):
    """Bootstrap CIs must provide lower and upper bounds for MAE and R2."""
    bs = review_results["bootstrap_ci"]
    assert "mae_mean" in bs
    assert "mae_ci_lower" in bs
    assert "mae_ci_upper" in bs
    assert "r2_mean" in bs
    assert "r2_ci_lower" in bs
    assert "r2_ci_upper" in bs
    assert "n_bootstrap" in bs
    assert bs["n_bootstrap"] >= 100
    # CI should bracket the mean
    assert bs["mae_ci_lower"] <= bs["mae_mean"] <= bs["mae_ci_upper"]
    assert bs["r2_ci_lower"] <= bs["r2_mean"] <= bs["r2_ci_upper"]


def test_results_saved_to_json(review_results):
    """Results should be saved to a JSON file for paper reference."""
    outpath = PROJECT_ROOT / "review_experiment_results.json"
    assert outpath.exists(), "review_experiment_results.json not written"
    data = json.loads(outpath.read_text())
    assert "emission_sensitivity" in data
    assert "local_density" in data
    assert "holdout" in data
    assert "bootstrap_ci" in data
