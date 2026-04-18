"""Tests for Phase 2.75 mandated experiments (E30-E34)."""
import pytest
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestE30InternetCorrelation:
    """E30: Sighting volume correlation with US internet adoption."""

    def test_returns_correlation_and_pvalue(self):
        from review_experiments import run_E30_internet_correlation
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E30_internet_correlation(df)
        assert 'pearson_r' in result
        assert 'p_value' in result
        assert -1 <= result['pearson_r'] <= 1
        assert 0 <= result['p_value'] <= 1

    def test_positive_correlation_during_growth(self):
        from review_experiments import run_E30_internet_correlation
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E30_internet_correlation(df)
        # Internet and sighting growth should correlate positively 1990-2014
        assert result['pearson_r'] > 0.5, f"Expected strong positive correlation, got r={result['pearson_r']}"


class TestE31StarlinkITS:
    """E31: Interrupted time series for Starlink formation effect."""

    def test_returns_its_results(self):
        from review_experiments import run_E31_starlink_its
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E31_starlink_its(df)
        assert 'intercept_shift' in result
        assert 'intercept_shift_pvalue' in result
        assert 'absolute_rate_ratio' in result
        assert 'fractional_rate_ratio' in result

    def test_reports_both_absolute_and_fractional(self):
        from review_experiments import run_E31_starlink_its
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E31_starlink_its(df)
        assert result['absolute_rate_ratio'] > 0
        assert result['fractional_rate_ratio'] > 0


class TestE32Overdispersion:
    """E32: Negative binomial vs Poisson for state counts."""

    def test_returns_dispersion_diagnostic(self):
        from review_experiments import run_E32_overdispersion
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E32_overdispersion(df)
        assert 'poisson_aic' in result
        assert 'nb_aic' in result
        assert 'dispersion_ratio' in result
        assert 'nb_coefficient' in result

    def test_detects_overdispersion(self):
        from review_experiments import run_E32_overdispersion
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E32_overdispersion(df)
        # State-level counts should be overdispersed
        assert result['dispersion_ratio'] > 1, "Expected overdispersion in state counts"


class TestE33Ngrams:
    """E33: Google Ngrams correlation with shape fractions."""

    def test_returns_correlation_results(self):
        from review_experiments import run_E33_cultural_indicators
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E33_cultural_indicators(df)
        assert 'flying_saucer_disk_corr' in result
        assert 'method' in result


class TestE34StateLevelFormation:
    """E34: State-level formation analysis post-Starlink."""

    def test_returns_state_formation_results(self):
        from review_experiments import run_E34_state_formation
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        result = run_E34_state_formation(df)
        assert 'top_formation_states' in result
        assert 'latitude_correlation' in result
        assert len(result['top_formation_states']) >= 5
