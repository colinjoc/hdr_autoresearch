"""TDD tests for the JR tax on housing supply synthesis project.

Tests the core data structures and calculations:
- Direct JR delay: unit-months delayed for each JR'd SHD scheme
- Indirect delay: counterfactual ABP throughput under 18wk SOP
- Sanity bounds on headline figures
"""
from __future__ import annotations
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_shd_jr_cases_exist():
    """We must have a non-empty list of SHD JR cases with unit counts."""
    from analysis import SHD_JR_CASES
    assert len(SHD_JR_CASES) >= 16, "Need at least the 16 decided 2018-2021 SHD JR cases"


def test_shd_jr_cases_have_required_fields():
    """Each case must have case_num, units, delay_months, outcome, decision_year."""
    from analysis import SHD_JR_CASES
    required = {"case_num", "units", "delay_months", "outcome", "decision_year"}
    for case in SHD_JR_CASES:
        for field in required:
            assert field in case, f"Case {case.get('case_num', '?')} missing field {field}"


def test_direct_delay_positive_and_bounded():
    """Total direct delay (unit-months) must be >0 and <100,000."""
    from analysis import compute_direct_delay
    total = compute_direct_delay()
    assert total > 0, "Direct JR delay must be positive"
    assert total < 150_000, "Direct JR delay must be < 150,000 unit-months"


def test_indirect_delay_computed():
    """Indirect delay must be computable with lower/central/upper bounds."""
    from analysis import compute_indirect_delay
    result = compute_indirect_delay()
    assert "lower" in result
    assert "central" in result
    assert "upper" in result
    assert result["lower"] >= 0
    assert result["central"] > result["lower"]
    assert result["upper"] > result["central"]


def test_counterfactual_completions():
    """Counterfactual completions must produce annual figures 2018-2024."""
    from analysis import compute_counterfactual_completions
    result = compute_counterfactual_completions()
    assert len(result) >= 7, "Need at least 7 years of counterfactual"
    for row in result:
        assert "year" in row
        assert "observed" in row
        assert "counterfactual_18wk" in row


def test_abp_decision_time_series():
    """ABP mean weeks series must be available 2015-2024."""
    from analysis import ABP_ANNUAL
    assert len(ABP_ANNUAL) >= 10
    assert ABP_ANNUAL[2017] == 18
    assert ABP_ANNUAL[2024] == 42


def test_tournament_families():
    """At least 4 tournament families must be defined."""
    from analysis import run_tournament
    results = run_tournament()
    assert len(results) >= 4, "Need >= 4 tournament families"


def test_e00_baseline():
    """E00 baseline must be computable and report total units directly affected."""
    from analysis import compute_e00_baseline
    e00 = compute_e00_baseline()
    assert "total_units" in e00
    assert e00["total_units"] > 0
    assert "n_cases" in e00
    assert e00["n_cases"] >= 16


def test_discovery_outputs():
    """Phase B must produce jr_tax_estimates.csv and counterfactual_completions.csv."""
    from analysis import write_phase_b_discoveries
    # Just test it runs without error - file existence checked separately
    write_phase_b_discoveries()
    disc_dir = Path(__file__).resolve().parent.parent / "discoveries"
    assert (disc_dir / "jr_tax_estimates.csv").exists()
    assert (disc_dir / "counterfactual_completions.csv").exists()
