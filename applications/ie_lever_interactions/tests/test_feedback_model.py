"""
Tests for the housing-lever feedback-loop model.

Parameters from data_sources.md (all predecessor projects):
- Median pipeline duration: 962 days
- Finance rate: 7% on 60% drawdown
- Total dev cost (Dublin 3-bed): €592k
- Hard cost share: 53% nationally
- Viability margin (Dublin houses): -3.1%
- Viability–application correlation: r=0.91
- Current residential applications: ~21,000/yr
- Approval rate: ~68%
- Build-yield: 59.6%
- Current completions: ~35,000/yr
- Construction capacity ceiling: ~35,000/yr
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBaselineParameters:
    """Verify baseline parameters match data_sources.md."""

    def test_baseline_cost(self):
        from feedback_model import BASELINE
        assert BASELINE["total_dev_cost"] == 592_000

    def test_baseline_duration(self):
        from feedback_model import BASELINE
        assert BASELINE["pipeline_duration_days"] == 962

    def test_baseline_finance_rate(self):
        from feedback_model import BASELINE
        assert BASELINE["finance_rate"] == 0.07

    def test_baseline_hard_cost_share(self):
        from feedback_model import BASELINE
        assert BASELINE["hard_cost_share"] == 0.53

    def test_baseline_viability_margin(self):
        from feedback_model import BASELINE
        assert BASELINE["viability_margin"] == -0.031

    def test_baseline_viability_apps_correlation(self):
        from feedback_model import BASELINE
        assert BASELINE["viability_apps_r"] == 0.91

    def test_baseline_current_applications(self):
        from feedback_model import BASELINE
        assert BASELINE["current_applications"] == 21_000

    def test_baseline_approval_rate(self):
        from feedback_model import BASELINE
        assert BASELINE["approval_rate"] == 0.68

    def test_baseline_build_yield(self):
        from feedback_model import BASELINE
        assert BASELINE["build_yield"] == 0.596

    def test_baseline_current_completions(self):
        from feedback_model import BASELINE
        assert BASELINE["current_completions"] == 35_000

    def test_baseline_capacity_ceiling(self):
        from feedback_model import BASELINE
        assert BASELINE["capacity_ceiling"] == 35_000


class TestCostReduction:
    """Test that each lever produces the correct cost reduction."""

    def test_no_lever_no_reduction(self):
        from feedback_model import compute_cost_reduction
        levers = {}
        reduction = compute_cost_reduction(levers)
        assert reduction == pytest.approx(0.0, abs=1e-6)

    def test_duration_reduction_25pct(self):
        """25% duration cut saves on finance costs.
        Finance = 7% * 60% drawdown * (962/365) yrs * 592k = ~65.5k
        25% cut => saves ~16.4k => ~2.8% of total cost."""
        from feedback_model import compute_cost_reduction
        levers = {"duration_reduction": 0.25}
        reduction = compute_cost_reduction(levers)
        assert reduction > 0.02  # at least 2% saving
        assert reduction < 0.05  # not more than 5%

    def test_modular_30pct(self):
        """30% off hard costs. Hard costs = 53% of 592k = 313.8k.
        30% of that = 94.1k => 15.9% of total cost."""
        from feedback_model import compute_cost_reduction
        levers = {"modular_reduction": 0.30}
        reduction = compute_cost_reduction(levers)
        assert reduction == pytest.approx(0.30 * 0.53, rel=0.01)

    def test_vat_zero(self):
        """VAT from 13.5% to 0% saves 13.5% of pre-VAT cost.
        As fraction of total: 0.135 / 1.135 = 11.9%."""
        from feedback_model import compute_cost_reduction
        levers = {"vat_rate": 0.0}
        reduction = compute_cost_reduction(levers)
        assert reduction == pytest.approx(0.135 / 1.135, rel=0.02)

    def test_part_v_abolished(self):
        """Part V from 20% to 0%. Policy cost share = 15.5%.
        Part V is roughly 4-5% of total cost (social housing obligation)."""
        from feedback_model import compute_cost_reduction
        levers = {"part_v_rate": 0.0}
        reduction = compute_cost_reduction(levers)
        assert reduction > 0.02
        assert reduction < 0.08

    def test_dev_contribs_zeroed(self):
        """Development contributions zeroed. Approx 2-3% of total cost."""
        from feedback_model import compute_cost_reduction
        levers = {"dev_contribs_fraction": 0.0}
        reduction = compute_cost_reduction(levers)
        assert reduction > 0.01
        assert reduction < 0.05

    def test_bcar_halved(self):
        """BCAR halved. Compliance costs ~1-2% of total."""
        from feedback_model import compute_cost_reduction
        levers = {"bcar_fraction": 0.5}
        reduction = compute_cost_reduction(levers)
        assert reduction > 0.005
        assert reduction < 0.03

    def test_land_cpo_agricultural(self):
        """CPO to agricultural value. Land ~15-20% of cost in Dublin."""
        from feedback_model import compute_cost_reduction
        levers = {"land_cost_multiplier": 0.1}  # agricultural ~10% of market
        reduction = compute_cost_reduction(levers)
        assert reduction > 0.10
        assert reduction < 0.25

    def test_finance_rate_3pct(self):
        """Finance rate from 7% to 3%. Saves on financing costs.
        Saving = (0.07-0.03) * 0.60 * (962/365.25) = 6.3% of total cost."""
        from feedback_model import compute_cost_reduction
        levers = {"finance_rate_new": 0.03}
        reduction = compute_cost_reduction(levers)
        assert reduction == pytest.approx(0.0632, rel=0.05)

    def test_developer_margin_6pct(self):
        """Developer margin from 15% to 6%. Saves 9pp of cost."""
        from feedback_model import compute_cost_reduction
        levers = {"developer_margin_new": 0.06}
        reduction = compute_cost_reduction(levers)
        assert reduction > 0.05
        assert reduction < 0.12


class TestFeedbackLoop:
    """Test the full feedback loop: cost reduction -> viability -> apps -> permissions -> completions."""

    def test_baseline_produces_current_completions(self):
        """No levers applied should produce ~current completions."""
        from feedback_model import run_feedback_loop
        result = run_feedback_loop({})
        assert result["completions"] == pytest.approx(35_000, rel=0.01)

    def test_lever_increases_gross_completions(self):
        """Any cost-reducing lever should increase gross (uncapped) completions."""
        from feedback_model import run_feedback_loop
        result = run_feedback_loop({"modular_reduction": 0.20})
        assert result["gross_completions_uncapped"] > 35_000

    def test_lever_plus_workforce_increases_completions(self):
        """With workforce lever lifting ceiling, completions exceed baseline."""
        from feedback_model import run_feedback_loop
        result = run_feedback_loop({"modular_reduction": 0.20,
                                     "workforce_multiplier": 1.5})
        assert result["completions"] > 35_000

    def test_capacity_ceiling_binds(self):
        """Even with massive cost reduction, completions can't exceed ceiling."""
        from feedback_model import run_feedback_loop
        result = run_feedback_loop({"modular_reduction": 0.30, "vat_rate": 0.0},
                                    capacity_ceiling=35_000)
        assert result["completions"] <= 35_000

    def test_workforce_lever_raises_ceiling(self):
        """Workforce +50% raises capacity ceiling."""
        from feedback_model import run_feedback_loop
        result = run_feedback_loop({"modular_reduction": 0.30, "vat_rate": 0.0,
                                     "workforce_multiplier": 1.5})
        assert result["capacity_ceiling_used"] == pytest.approx(52_500, rel=0.01)

    def test_viability_improves_with_cost_reduction(self):
        """Cost reduction should improve viability margin."""
        from feedback_model import run_feedback_loop
        result = run_feedback_loop({"modular_reduction": 0.20})
        assert result["viability_margin"] > -0.031

    def test_applications_increase_with_viability(self):
        """Better viability => more applications (r=0.91)."""
        from feedback_model import run_feedback_loop
        baseline = run_feedback_loop({})
        result = run_feedback_loop({"modular_reduction": 0.20})
        assert result["applications"] > baseline["applications"]


class TestInteractionEffects:
    """Test that interaction effects can be computed."""

    def test_additive_model(self):
        """Sum of individual effects."""
        from feedback_model import run_feedback_loop
        a = run_feedback_loop({"duration_reduction": 0.25})
        b = run_feedback_loop({"modular_reduction": 0.20})
        baseline = run_feedback_loop({})

        delta_a = a["completions"] - baseline["completions"]
        delta_b = b["completions"] - baseline["completions"]
        additive = baseline["completions"] + delta_a + delta_b

        combined = run_feedback_loop({"duration_reduction": 0.25,
                                       "modular_reduction": 0.20})
        # The combined effect may differ from additive
        # This test just checks we can compute both
        assert additive > 0
        assert combined["completions"] > 0

    def test_interaction_term(self):
        """Interaction = combined - (A_alone + B_alone - baseline)."""
        from feedback_model import compute_interaction_term
        interaction = compute_interaction_term(
            {"duration_reduction": 0.25},
            {"modular_reduction": 0.20}
        )
        # Interaction term can be positive (synergy) or negative (redundancy)
        assert isinstance(interaction, float)

    def test_full_factorial_count(self):
        """Full factorial should produce 4*4*3*3*3*2*3*3*3*3 = 104,976 combos."""
        from feedback_model import generate_full_factorial
        combos = generate_full_factorial()
        assert len(combos) == 104_976


class TestMonteCarloSim:
    """Test Monte Carlo simulation with parameter uncertainty."""

    def test_mc_returns_distribution(self):
        from feedback_model import run_monte_carlo
        # Use workforce lever to lift ceiling so distribution is visible
        results = run_monte_carlo({"modular_reduction": 0.20,
                                    "workforce_multiplier": 1.5},
                                   n_draws=100, seed=42)
        assert len(results) == 100
        assert all(r > 0 for r in results)

    def test_mc_seed_stable(self):
        from feedback_model import run_monte_carlo
        levers = {"modular_reduction": 0.20, "workforce_multiplier": 1.5}
        r1 = run_monte_carlo(levers, n_draws=50, seed=42)
        r2 = run_monte_carlo(levers, n_draws=50, seed=42)
        assert r1 == r2

    def test_mc_ci(self):
        from feedback_model import run_monte_carlo
        import numpy as np
        # Use small lever + high ceiling so CI shows variance
        results = run_monte_carlo({"bcar_fraction": 0.5,
                                    "workforce_multiplier": 1.5},
                                   n_draws=1000, seed=42)
        ci_low = np.percentile(results, 2.5)
        ci_high = np.percentile(results, 97.5)
        assert ci_low < ci_high
        assert ci_low > 0
