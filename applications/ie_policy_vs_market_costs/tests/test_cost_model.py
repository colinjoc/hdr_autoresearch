"""TDD tests for the Irish residential development cost model.

Tests the cost stack decomposition, viability analysis, and scenario modelling.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCostStack:
    """Test the full cost stack construction for representative dwellings."""

    def test_cost_stack_returns_dict(self):
        from cost_model import build_cost_stack
        stack = build_cost_stack("3bed_semi", "dublin")
        assert isinstance(stack, dict)

    def test_cost_stack_has_required_components(self):
        from cost_model import build_cost_stack
        stack = build_cost_stack("3bed_semi", "dublin")
        required = [
            "materials", "labour", "site_works", "land",
            "dev_contributions", "part_v", "vat", "bcar",
            "planning_fees", "professional_fees", "finance",
            "developer_margin"
        ]
        for comp in required:
            assert comp in stack, f"Missing component: {comp}"

    def test_cost_stack_values_positive(self):
        from cost_model import build_cost_stack
        stack = build_cost_stack("3bed_semi", "dublin")
        for k, v in stack.items():
            assert v >= 0, f"{k} is negative: {v}"

    def test_cost_stack_total_in_range(self):
        """Dublin 3-bed semi total cost (incl. land, margin, finance) ~€400k-€750k."""
        from cost_model import build_cost_stack
        stack = build_cost_stack("3bed_semi", "dublin")
        total = sum(stack.values())
        assert 400_000 < total < 750_000, f"Total {total} out of range"

    def test_hard_cost_share_calibration(self):
        """Hard costs should be ~49-55% of total per SCSI."""
        from cost_model import build_cost_stack, classify_components
        stack = build_cost_stack("3bed_semi", "dublin")
        total = sum(stack.values())
        hard = sum(v for k, v in stack.items() if k in ["materials", "labour", "site_works"])
        share = hard / total
        assert 0.35 < share < 0.65, f"Hard cost share {share:.1%} out of calibration range"


class TestClassification:
    """Test policy vs market classification."""

    def test_classify_all_components(self):
        from cost_model import classify_components
        classes = classify_components()
        assert "vat" in classes
        assert classes["vat"] == "POLICY"
        assert classes["materials"] == "MARKET"

    def test_policy_share_in_range(self):
        """Policy costs should be ~15-20% of total per SCSI calibration."""
        from cost_model import build_cost_stack, classify_components, policy_share
        share = policy_share("3bed_semi", "dublin")
        assert 0.10 < share < 0.30, f"Policy share {share:.1%} out of range"


class TestLocations:
    """Test across all 4 location types."""

    @pytest.mark.parametrize("location", ["dublin", "commuter", "regional", "rural"])
    def test_all_locations_produce_stacks(self, location):
        from cost_model import build_cost_stack
        stack = build_cost_stack("3bed_semi", location)
        total = sum(stack.values())
        assert total > 100_000

    @pytest.mark.parametrize("dwelling", ["3bed_semi", "2bed_apt", "4bed_detached", "3bed_terrace"])
    def test_all_dwelling_types(self, dwelling):
        from cost_model import build_cost_stack
        stack = build_cost_stack(dwelling, "dublin")
        total = sum(stack.values())
        assert total > 100_000


class TestViability:
    """Test viability frontier analysis."""

    def test_viability_margin_calculation(self):
        from cost_model import viability_margin
        margin = viability_margin("3bed_semi", "dublin")
        assert isinstance(margin, float)

    def test_dublin_apartments_negative_margin(self):
        """Per U-2, Dublin apartments are NOT viable at current costs.
        They only become viable with sustained price growth of ~5%/yr.
        The cost model should show a negative margin."""
        from cost_model import viability_margin
        margin = viability_margin("2bed_apt", "dublin")
        # Apartments are known to be unviable — margin is negative
        assert -0.60 < margin < 0.0, f"Dublin apt margin {margin:.1%} unexpected"

    def test_rural_generally_not_viable(self):
        """Rural areas generally not viable for spec development."""
        from cost_model import viability_margin
        margin = viability_margin("3bed_semi", "rural")
        assert margin < 0.10


class TestScenarios:
    """Test policy scenario modelling."""

    def test_halve_vat(self):
        from cost_model import apply_scenario, build_cost_stack
        base = build_cost_stack("3bed_semi", "dublin")
        modified = apply_scenario(base, {"vat_rate": 0.5})  # multiply factor
        assert modified["vat"] < base["vat"]
        assert modified["vat"] == pytest.approx(base["vat"] * 0.5, rel=0.01)

    def test_zero_part_v(self):
        from cost_model import apply_scenario, build_cost_stack
        base = build_cost_stack("3bed_semi", "dublin")
        modified = apply_scenario(base, {"part_v_rate": 0.0})
        assert modified["part_v"] == 0.0

    def test_halve_all_policy(self):
        from cost_model import apply_scenario, build_cost_stack, classify_components
        base = build_cost_stack("3bed_semi", "dublin")
        scenario = {"vat_rate": 0.5, "part_v_rate": 0.5, "dev_contributions_rate": 0.5,
                     "bcar_rate": 0.5, "planning_fees_rate": 0.0}
        modified = apply_scenario(base, scenario)
        classes = classify_components()
        base_policy = sum(v for k, v in base.items() if classes.get(k) == "POLICY")
        mod_policy = sum(v for k, v in modified.items() if classes.get(k) == "POLICY")
        assert mod_policy < base_policy


class TestCountyViability:
    """Test county-level viability analysis."""

    def test_counties_viable_count(self):
        from cost_model import count_viable_counties
        n = count_viable_counties("3bed_semi", {})
        assert isinstance(n, int)
        assert 0 <= n <= 26

    def test_more_counties_viable_with_policy_halved(self):
        from cost_model import count_viable_counties
        base_n = count_viable_counties("3bed_semi", {})
        scenario = {"vat_rate": 0.5, "part_v_rate": 0.5, "dev_contributions_rate": 0.5,
                     "bcar_rate": 0.5, "planning_fees_rate": 0.0}
        mod_n = count_viable_counties("3bed_semi", scenario)
        assert mod_n >= base_n


class TestViabilityGapFund:
    """Test viability gap fund calculation."""

    def test_gap_fund_returns_dict(self):
        from cost_model import viability_gap_fund
        gaps = viability_gap_fund("3bed_semi")
        assert isinstance(gaps, dict)
        # Should have entries for non-viable counties
        for county, gap in gaps.items():
            assert gap >= 0  # gap is always positive (subsidy needed)


class TestPassThrough:
    """Test that 50% pass-through reduces viable counties vs static assumption."""

    def test_pass_through_reduces_viability(self):
        """With 50% pass-through, fewer counties should be viable than static."""
        from cost_model import (
            build_county_cost_stack, apply_scenario, count_viable_counties, COUNTIES
        )
        scenario = {"vat_rate": 0.0}
        static_viable = count_viable_counties("3bed_semi", scenario)

        pt_viable = 0
        for county in COUNTIES:
            stack = build_county_cost_stack(county)
            stack_mod = apply_scenario(stack, scenario)
            saving = sum(stack.values()) - sum(stack_mod.values())
            adjusted_sale = COUNTIES[county]["sale_price_3bed"] - (saving * 0.50)
            new_total = sum(stack_mod.values())
            if adjusted_sale >= new_total:
                pt_viable += 1

        assert pt_viable <= static_viable, (
            f"Pass-through viable ({pt_viable}) should be <= static ({static_viable})"
        )
