"""Tests for the evaluation harness and source attribution model."""
import pytest
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '/home/col/generalized_hdr_autoresearch/applications/dublin_no2')


def test_source_attribution_sums_to_total():
    """Source contributions should approximately sum to measured total."""
    from evaluate import attribute_sources
    results = attribute_sources(station='IE005AP')
    for year in results['year'].unique():
        yr_data = results[results['year'] == year]
        measured = yr_data['measured_annual'].iloc[0]
        attributed = yr_data['traffic'].iloc[0] + yr_data['heating'].iloc[0] + yr_data['background'].iloc[0] + yr_data['residual'].iloc[0]
        # Should be within 1% of measured
        assert abs(attributed - measured) / measured < 0.01, \
            f"Year {year}: attributed {attributed:.1f} != measured {measured:.1f}"


def test_traffic_dominant_at_traffic_stations():
    """Traffic should be the dominant source at traffic-type stations."""
    from evaluate import attribute_sources
    results = attribute_sources(station='IE005AP')  # Winetavern, traffic
    # In non-COVID years, traffic should be > 30% of total
    for year in [2019, 2022, 2023]:
        yr_data = results[results['year'] == year]
        if len(yr_data) > 0:
            traffic_pct = yr_data['traffic_pct'].iloc[0]
            assert traffic_pct > 30, \
                f"Traffic at Winetavern {year}: {traffic_pct:.0f}% — expected >30%"


def test_covid_reduces_traffic_contribution():
    """COVID lockdown should dramatically reduce traffic contribution."""
    from evaluate import attribute_sources_monthly
    results = attribute_sources_monthly(station='IE005AP')
    # April 2020 vs April 2019
    apr_2020 = results[(results['year'] == 2020) & (results['month'] == 4)]
    apr_2019 = results[(results['year'] == 2019) & (results['month'] == 4)]
    if len(apr_2020) > 0 and len(apr_2019) > 0:
        assert apr_2020['traffic'].iloc[0] < apr_2019['traffic'].iloc[0], \
            "Traffic contribution should be lower during COVID lockdown"


def test_heating_seasonal():
    """Heating contribution should peak in winter, minimal in summer."""
    from evaluate import attribute_sources_monthly
    results = attribute_sources_monthly(station='IE0036A')  # Ballyfermot, residential
    # Aggregate across years
    summer = results[results['month'].isin([6, 7, 8])]['heating'].mean()
    winter = results[results['month'].isin([12, 1, 2])]['heating'].mean()
    assert winter > summer, f"Winter heating ({winter:.1f}) should exceed summer ({summer:.1f})"


def test_background_matches_rural():
    """Background contribution should approximately match rural station levels."""
    from evaluate import attribute_sources
    results = attribute_sources(station='IE005AP')
    for year in results['year'].unique():
        yr_data = results[results['year'] == year]
        bg = yr_data['background'].iloc[0]
        # Background should be 1-10 µg/m³ (matching rural stations)
        assert 0 < bg < 15, f"Background {year}: {bg:.1f} — expected 1-15 µg/m³"


def test_who_exceedance_summary():
    """WHO exceedance summary should be computed correctly."""
    from evaluate import who_exceedance_summary
    summary = who_exceedance_summary()
    assert 'station' in summary.columns
    assert 'annual_mean' in summary.columns
    assert 'exceeds_who_annual' in summary.columns
    assert 'days_exceeding_24h' in summary.columns
    # Winetavern should always exceed
    wt = summary[summary['station'] == 'IE005AP']
    assert wt['exceeds_who_annual'].all()


def test_results_tsv_format():
    """Results can be appended to results.tsv in standard HDR format."""
    from evaluate import run_baseline_evaluation
    result = run_baseline_evaluation()
    assert 'experiment' in result
    assert 'metric' in result
    assert 'value' in result
    assert isinstance(result['value'], float)
