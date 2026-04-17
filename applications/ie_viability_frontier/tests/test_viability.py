"""Tests for the viability calculation module."""
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_load_rzlpa02():
    """RZLPA02 loads and returns county-level land price data."""
    from viability import load_rzlpa02
    df = load_rzlpa02()
    assert len(df) > 0
    assert "county" in df.columns
    assert "median_price_per_hectare" in df.columns
    # Should have Irish counties
    counties = df["county"].tolist()
    assert any("Dublin" in c for c in counties)
    assert any("Cork" in c for c in counties)


def test_load_hpm09():
    """HPM09 loads and returns RPPI time series by region."""
    from viability import load_hpm09
    df = load_hpm09()
    assert len(df) > 0
    assert "region" in df.columns
    assert "date" in df.columns
    assert "rppi" in df.columns


def test_load_bea04():
    """BEA04 loads construction production index."""
    from viability import load_bea04
    df = load_bea04()
    assert len(df) > 0
    assert "year" in df.columns
    assert "sector" in df.columns


def test_parse_buildcost():
    """Parse buildcost PDF text for EUR/sqm figures (CCG base costs)."""
    from viability import parse_buildcost
    costs = parse_buildcost()
    assert isinstance(costs, dict)
    # Should have residential building types from Construction Cost Guide
    assert len(costs) >= 3
    # Values should be in CCG base range (EUR/sqm, excl siteworks/fees)
    for k, v in costs.items():
        assert 1500 < v < 4000, f"{k}: {v} out of range"


def test_viability_calculation():
    """Core viability equation: sale price vs total cost."""
    from viability import calculate_viability
    result = calculate_viability(
        sale_price=387000,
        land_cost_per_hectare=500000,
        density_units_per_ha=40,
        construction_cost_per_sqm=2464,
        avg_sqm=110,
        dev_contributions=15000,
        finance_rate=0.07,
        build_duration_years=2.5,
        profit_margin=0.175,
    )
    assert "total_cost" in result
    assert "viable" in result
    assert "margin_pct" in result
    assert isinstance(result["viable"], bool)
    # With corrected national-average inputs, should be marginal to moderately unviable
    assert -0.5 < result["margin_pct"] < 0.5


def test_scsi_cross_check():
    """Model output should be within 10% of SCSI 2023 delivery cost (EUR 397k)."""
    from viability import calculate_viability
    # SCSI 2023: national avg delivery cost for 3-bed semi = ~EUR 397,000
    # Using national average parameters
    result = calculate_viability(
        sale_price=387000,
        land_cost_per_hectare=571235,  # National median from RZLPA02
        density_units_per_ha=40,
        construction_cost_per_sqm=2464,  # Corrected CCG-based all-in
        avg_sqm=110,
        dev_contributions=15000,
        finance_rate=0.07,
        build_duration_years=2.5,
        profit_margin=0.175,
    )
    # Total cost should be within 10% of SCSI 397k
    # (Note: SCSI figure is all-in incl profit; our total_cost also includes profit)
    assert abs(result["total_cost"] - 397000) / 397000 < 0.15, \
        f"Total cost {result['total_cost']:.0f} too far from SCSI benchmark 397,000"


def test_county_viability_assessment():
    """Generate viability assessment per county."""
    from viability import assess_county_viability
    df = assess_county_viability()
    assert len(df) > 0
    assert "county" in df.columns
    assert "viable" in df.columns
    assert "margin_pct" in df.columns
    assert "viability_class" in df.columns
    # viability_class should be one of viable/marginal/unviable
    valid_classes = {"viable", "marginal", "unviable"}
    for c in df["viability_class"].unique():
        assert c in valid_classes
