"""Tests for AARO data extraction and analysis pipeline."""
import pytest
import os
import sys
import csv

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def test_extract_aaro_fy2024_case_counts():
    """Verify we can extract the key quantitative figures from FY2024 report."""
    from extract_data import extract_fy2024_figures
    figs = extract_fy2024_figures()
    assert figs["total_reports_cumulative"] == 1652
    assert figs["new_reports_period"] == 757
    assert figs["reports_during_period"] == 485
    assert figs["reports_prior_periods"] == 272
    assert figs["cases_resolved_period"] == 49
    assert figs["cases_resolved_total"] == 118
    assert figs["cases_pending_closure"] == 174
    assert figs["cases_merit_ic_analysis"] == 21
    assert figs["cases_active_archive"] == 444
    assert figs["cases_recommended_closure"] == 243
    assert figs["air_domain"] == 708
    assert figs["space_domain"] == 49
    assert figs["faa_reports"] == 392
    assert figs["nuclear_reports"] == 18
    assert figs["flight_safety_concerns"] == 2
    assert figs["pilots_trailed"] == 3
    assert figs["morphology_insufficient"] == 170


def test_extract_odni_2022_case_counts():
    """Verify we can extract figures from ODNI 2022 report."""
    from extract_data import extract_odni_2022_figures
    figs = extract_odni_2022_figures()
    assert figs["total_reports_cumulative"] == 510
    assert figs["new_reports_since_prelim"] == 247
    assert figs["discovered_late_reports"] == 119
    assert figs["preliminary_assessment_reports"] == 144
    assert figs["characterized_uas"] == 26
    assert figs["characterized_balloon"] == 163
    assert figs["characterized_clutter"] == 6
    assert figs["uncharacterized"] == 171


def test_extract_historical_context():
    """Verify historical context data from web sources."""
    from extract_data import get_historical_context
    ctx = get_historical_context()
    # ODNI 2021 preliminary assessment
    assert ctx["odni_2021_total"] == 144
    assert ctx["odni_2021_identified"] == 1  # the balloon
    assert ctx["odni_2021_unusual_flight"] == 18
    assert ctx["odni_2021_multi_sensor"] == 80
    # Project Blue Book
    assert ctx["blue_book_total"] == 12618
    assert ctx["blue_book_unidentified"] == 701
    # Hendry 1979
    assert ctx["hendry_total"] == 1307
    assert ctx["hendry_identified_pct"] == 88.6


def test_resolution_rate_series():
    """Test that we can compute resolution rates across reports."""
    from extract_data import compute_resolution_rates
    rates = compute_resolution_rates()
    # Should have entries for each report period
    assert len(rates) >= 3
    # Each entry should have year, total, resolved, rate
    for r in rates:
        assert "period" in r
        assert "cumulative_total" in r
        assert "resolved" in r
        assert "resolution_rate" in r
        if r["resolution_rate"] is not None:
            assert 0 <= r["resolution_rate"] <= 1


def test_backlog_growth():
    """Test backlog growth computation."""
    from extract_data import compute_backlog_growth
    bg = compute_backlog_growth()
    assert bg["intake_rate_per_month"] > 0
    assert bg["resolution_rate_per_month"] > 0
    assert "backlog_growing" in bg


def test_base_rate_comparison():
    """Test base-rate comparison with historical programs."""
    from extract_data import compute_base_rate_comparison
    comp = compute_base_rate_comparison()
    assert "blue_book_unid_rate" in comp
    assert "hendry_unid_rate" in comp
    assert "aaro_unid_rate" in comp
    assert "nuforc_explained_rate" in comp


def test_resolution_taxonomy_csv():
    """Test that resolution taxonomy CSV is generated correctly."""
    from extract_data import generate_resolution_taxonomy
    taxonomy = generate_resolution_taxonomy()
    assert len(taxonomy) > 0
    for row in taxonomy:
        assert "category" in row
        assert "count" in row or "description" in row


def test_structured_data_csv():
    """Test that structured data CSV is generated correctly."""
    from extract_data import generate_structured_data
    data = generate_structured_data()
    assert len(data) > 0
    for row in data:
        assert "source_report" in row
        assert "figure_name" in row
        assert "value" in row


def test_bayesian_posterior():
    """Test Bayesian posterior calculation."""
    from extract_data import compute_bayesian_posterior
    result = compute_bayesian_posterior()
    assert 0 < result["posterior_anomalous"] < 1
    assert 0 < result["prior_anomalous"] < 1
    assert "likelihood_ratio" in result
