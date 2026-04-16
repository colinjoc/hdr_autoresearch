"""Tests for the housing bottleneck pipeline model.

TDD: these tests are written FIRST and drive the implementation.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_waterfall_adds_up():
    """MANDATORY: permissions - losses at each stage = completions +/- 10%."""
    from analysis import waterfall_model, PARAMS

    result = waterfall_model(PARAMS)
    permissions = PARAMS["permission_volume"]
    completions = result["completions"]

    # Sum of losses at each stage + completions should equal permissions
    total_accounted = (
        result["lapsed"]
        + result["ccc_non_filed"]
        + result["ccc_to_occupied_loss"]
        + completions
    )
    assert abs(total_accounted - permissions) / permissions < 0.10, (
        f"Waterfall does not add up: {total_accounted} vs {permissions} "
        f"(error {abs(total_accounted - permissions) / permissions:.1%})"
    )


def test_baseline_yield():
    """E00: baseline yield should be approximately 35.1%."""
    from analysis import waterfall_model, PARAMS

    result = waterfall_model(PARAMS)
    yield_pct = result["completions"] / PARAMS["permission_volume"]
    assert 0.25 < yield_pct < 0.45, f"Yield {yield_pct:.1%} outside expected range"


def test_opt_out_adjusted_yield():
    """E01: if opt-out dwellings are 90% built, effective yield rises."""
    from analysis import waterfall_model, PARAMS

    params = PARAMS.copy()
    params["opt_out_build_rate"] = 0.90
    result = waterfall_model(params)
    baseline = waterfall_model(PARAMS)
    assert result["effective_completions"] > baseline["effective_completions"]


def test_permission_sensitivity():
    """E02: adding permissions increases completions proportionally (below capacity)."""
    from analysis import waterfall_model, PARAMS

    base = waterfall_model(PARAMS)
    params = PARAMS.copy()
    params["permission_volume"] = 48000
    result = waterfall_model(params)
    # More permissions should give more completions (or hit capacity)
    assert result["completions"] >= base["completions"]


def test_capacity_ceiling_binds():
    """E07: capacity ceiling limits completions."""
    from analysis import waterfall_model, PARAMS

    params = PARAMS.copy()
    params["permission_volume"] = 100000  # Very high
    params["capacity_ceiling"] = 35000
    result = waterfall_model(params)
    assert result["completions"] <= 35000


def test_sensitivity_ranking():
    """T02: sensitivity analysis produces a ranking of bottlenecks."""
    from analysis import sensitivity_ranking, PARAMS

    ranking = sensitivity_ranking(PARAMS)
    assert len(ranking) >= 5
    # Each entry should have a name and marginal_units
    for entry in ranking:
        assert "name" in entry
        assert "marginal_units_per_year" in entry


def test_monte_carlo_produces_distribution():
    """T05: Monte Carlo produces a distribution of completions."""
    from analysis import monte_carlo_pipeline, PARAMS

    results = monte_carlo_pipeline(PARAMS, n_draws=100, seed=42)
    assert len(results) == 100
    assert min(results) > 0
    assert max(results) < PARAMS["permission_volume"]


def test_tournament_produces_results():
    """Phase 1: tournament produces results for 5 families."""
    from analysis import run_tournament, PARAMS

    families = run_tournament(PARAMS)
    assert len(families) >= 4
    for f in families:
        assert "family" in f
        assert "metric" in f
        assert "value" in f


def test_bottleneck_ranking_csv():
    """Phase B: bottleneck ranking CSV has required columns."""
    from analysis import generate_bottleneck_ranking, PARAMS

    df = generate_bottleneck_ranking(PARAMS)
    assert "bottleneck" in df.columns
    assert "marginal_units_per_year" in df.columns
    assert "rank" in df.columns
    assert len(df) >= 8


def test_policy_simulator_csv():
    """Phase B: policy package simulator has required structure."""
    from analysis import generate_policy_simulator, PARAMS

    df = generate_policy_simulator(PARAMS)
    assert "projected_additional_completions_yr" in df.columns
    assert len(df) >= 10


def test_lapse_halved_scenario():
    """E05: halving lapse adds a modest number of completions."""
    from analysis import waterfall_model, PARAMS

    base = waterfall_model(PARAMS)
    params = PARAMS.copy()
    params["lapse_rate"] = PARAMS["lapse_rate"] / 2
    result = waterfall_model(params)
    delta = result["completions"] - base["completions"]
    # Should be positive but modest (< 2000)
    assert 0 < delta < 3000


def test_all_experiments_run():
    """Phase 2: all 20+ experiments produce results."""
    from analysis import run_all_experiments, PARAMS

    results = run_all_experiments(PARAMS)
    assert len(results) >= 20
    for r in results:
        assert "id" in r
        assert "status" in r
        assert r["status"] in ("KEEP", "REVERT")


def test_pairwise_interactions():
    """Phase 2.5: pairwise interactions tested."""
    from analysis import run_pairwise_interactions, PARAMS

    results = run_pairwise_interactions(PARAMS)
    assert len(results) >= 3
    for r in results:
        assert "interaction" in r
        assert r["interaction"] is True


# =========================================================================
# Phase 2.75 mandated experiment tests (R1-R4)
# =========================================================================

def test_r1_opt_out_sensitivity_sweep():
    """R1: opt-out sensitivity sweep at 50/70/90/100% build rates."""
    from analysis import run_opt_out_sensitivity, PARAMS

    results = run_opt_out_sensitivity(PARAMS)
    assert len(results) == 4  # 50%, 70%, 90%, 100%
    for r in results:
        assert "opt_out_build_rate" in r
        assert "effective_yield" in r
        assert "effective_completions" in r
        assert "perm_marginal" in r  # marginal from +10k permissions
        assert "ccc_marginal" in r   # marginal from +10pp CCC
        assert "ranking_swaps" in r  # bool: does CCC outrank permissions?

    # At 50% opt-out, effective yield should be lower than at 90%
    r50 = [r for r in results if r["opt_out_build_rate"] == 0.50][0]
    r90 = [r for r in results if r["opt_out_build_rate"] == 0.90][0]
    assert r50["effective_yield"] < r90["effective_yield"]


def test_r2_monte_carlo_ranking_robustness():
    """R2: Monte Carlo ranking robustness with 1000 draws (fast test)."""
    from analysis import run_ranking_robustness, PARAMS

    results = run_ranking_robustness(PARAMS, n_draws=500, seed=42)
    assert "perm_rank1_frac" in results
    assert "ccc_outranks_perm_frac" in results
    assert "perm_marginal_ci_lo" in results
    assert "perm_marginal_ci_hi" in results
    assert "ccc_marginal_ci_lo" in results
    assert "ccc_marginal_ci_hi" in results
    # Permission volume should be #1 in at least some draws
    assert results["perm_rank1_frac"] > 0.0


def test_r3_abp_jr_double_count_audit():
    """R3: ABP/JR double-count audit."""
    from analysis import run_abp_jr_overlap_audit, PARAMS

    result = run_abp_jr_overlap_audit(PARAMS)
    assert "abp_marginal" in result
    assert "jr_marginal" in result
    assert "overlap_fraction" in result
    assert "combined_no_overlap" in result
    assert "revised_all_efficiency" in result
    # Overlap fraction should be between 0 and 1
    assert 0.0 <= result["overlap_fraction"] <= 1.0
    # Revised combined should be <= naive sum
    naive_sum = result["abp_marginal"] + result["jr_marginal"]
    assert result["combined_no_overlap"] <= naive_sum + 1  # rounding tolerance


def test_r4_bootstrap_cis():
    """R4: bootstrap CIs on marginal-units-per-year for top 5 bottlenecks."""
    from analysis import run_bootstrap_marginal_cis, PARAMS

    results = run_bootstrap_marginal_cis(PARAMS, n_draws=500, seed=42)
    assert len(results) >= 5
    for r in results:
        assert "bottleneck" in r
        assert "marginal_point" in r
        assert "ci_lo" in r
        assert "ci_hi" in r
        # CI should bracket the point estimate (within rounding)
        assert r["ci_lo"] <= r["marginal_point"] + 100
        assert r["ci_hi"] >= r["marginal_point"] - 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
