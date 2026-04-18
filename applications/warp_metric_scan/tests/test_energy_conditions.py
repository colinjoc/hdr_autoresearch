"""TDD tests for energy-condition checker.

These tests define the expected behaviour BEFORE implementation.
Each test uses a known metric with known energy-condition status.
"""
import pytest
import sympy as sp


class TestWECChecker:
    """Weak Energy Condition: T_μν u^μ u^ν ≥ 0 for all timelike u.
    In practice: ρ ≥ 0 and ρ + p_i ≥ 0 for each pressure."""

    def test_flat_spacetime_satisfies_wec(self):
        """Minkowski space has T_μν = 0 → WEC trivially satisfied."""
        from src.energy_conditions import check_wec
        from src.metric_ansatze import flat_metric
        result = check_wec(flat_metric())
        assert result["satisfied"] is True

    def test_alcubierre_at_v_gt_0_violates_wec(self):
        """Alcubierre warp with any v > 0 must violate WEC (known result)."""
        from src.energy_conditions import check_wec
        from src.metric_ansatze import alcubierre_metric
        result = check_wec(alcubierre_metric(v=0.5))
        assert result["satisfied"] is False
        assert result["rho_negative"] is True

    def test_fell_heisenberg_subluminal_satisfies_wec(self):
        """Fell-Heisenberg 2024 at v=0.04c satisfies all energy conditions."""
        from src.energy_conditions import check_wec
        from src.metric_ansatze import fell_heisenberg_metric
        result = check_wec(fell_heisenberg_metric(v=0.04))
        assert result["satisfied"] is True


class TestNECChecker:
    """Null Energy Condition: T_μν k^μ k^ν ≥ 0 for all null k."""

    def test_flat_spacetime_satisfies_nec(self):
        from src.energy_conditions import check_nec
        from src.metric_ansatze import flat_metric
        result = check_nec(flat_metric())
        assert result["satisfied"] is True

    def test_alcubierre_superluminal_violates_nec(self):
        """Santiago-Visser 2022: superluminal Alcubierre violates NEC."""
        from src.energy_conditions import check_nec
        from src.metric_ansatze import alcubierre_metric
        result = check_nec(alcubierre_metric(v=1.5))  # v > c
        assert result["satisfied"] is False


class TestFrameworkComparison:
    """Compare energy density across frameworks for the same warp geometry."""

    def test_5d_kk_adds_nonzero_terms(self):
        """5D KK with varying extra dimension must add non-zero terms to G_00."""
        from src.metric_ansatze import alcubierre_5d_kk
        from src.field_equations import compute_einstein_tensor
        G5 = compute_einstein_tensor(alcubierre_5d_kk(alpha=0.5))
        G4 = compute_einstein_tensor(alcubierre_5d_kk(alpha=0.0))
        # The difference should be non-zero (extra-dimensional contribution)
        diff = G5["G00"] - G4["G00"]
        assert diff != 0, "KK terms must contribute to energy density"

    def test_f1_baseline_reproduces_olum(self):
        """F1 standard GR must show WEC violation for v > c — validates tooling."""
        from src.energy_conditions import check_wec
        from src.metric_ansatze import alcubierre_metric
        result = check_wec(alcubierre_metric(v=2.0))
        assert result["satisfied"] is False, "Olum theorem must be reproduced"

    def test_einstein_cartan_torsion_adds_positive_contribution(self):
        """F4: Torsion H_00 must be non-negative (positive spin density)."""
        from src.metric_ansatze import alcubierre_einstein_cartan
        from src.energy_conditions import check_wec_einstein_cartan
        result = check_wec_einstein_cartan(
            alcubierre_einstein_cartan(v=0.5, s0=10.0, sigma_S=1.0)
        )
        assert result["max_H00"] is not None
        assert result["max_H00"] > 0, "Torsion must add positive energy"

    def test_einstein_cartan_large_spin_can_flip_wec(self):
        """F4: Sufficiently large spin density should flip WEC at low v."""
        from src.metric_ansatze import alcubierre_einstein_cartan
        from src.energy_conditions import check_wec_einstein_cartan
        # Very large spin density at low v should offset negative G_00
        result = check_wec_einstein_cartan(
            alcubierre_einstein_cartan(v=0.1, s0=100.0, sigma_S=1.0)
        )
        assert result["satisfied"] is True, \
            "Large spin at low v should satisfy WEC"

    def test_braneworld_weyl_contribution(self):
        """F5: Braneworld Weyl projection should add nonzero correction."""
        from src.metric_ansatze import alcubierre_braneworld
        from src.energy_conditions import check_wec_braneworld
        result = check_wec_braneworld(
            alcubierre_braneworld(v=0.5, C_W=1.0)
        )
        assert result["max_E00_contribution"] is not None
        assert result["max_E00_contribution"] > 0


class TestScanResultValidation:
    """Validate the quantitative scan results reported in the paper."""

    def test_f4_critical_s0_at_v1_5(self):
        """F4: Critical s0 at v=1.5 must be in [3, 6] (E12 reports ~4.3)."""
        import numpy as np
        from src.metric_ansatze import alcubierre_einstein_cartan
        from src.energy_conditions import check_wec_einstein_cartan
        # s0=3 should NOT flip WEC
        r_low = check_wec_einstein_cartan(
            alcubierre_einstein_cartan(v=1.5, s0=3.0, sigma_S=1.0)
        )
        assert r_low["satisfied"] is False, "s0=3 should not flip WEC at v=1.5"
        # s0=6 should flip WEC
        r_high = check_wec_einstein_cartan(
            alcubierre_einstein_cartan(v=1.5, s0=6.0, sigma_S=1.0)
        )
        assert r_high["satisfied"] is True, "s0=6 should flip WEC at v=1.5"

    def test_f5_cw_minus100_still_violates(self):
        """F5: C_W=-100 at v=1.5 should still violate WEC (E14 reports min=-0.074)."""
        from src.metric_ansatze import alcubierre_braneworld
        from src.energy_conditions import check_wec_braneworld
        result = check_wec_braneworld(
            alcubierre_braneworld(v=1.5, C_W=-100.0)
        )
        assert result["satisfied"] is False, "C_W=-100 should not flip WEC at v=1.5"
        assert result["min_G00_eff"] < 0, "Effective G00 should still be negative"

    def test_f4_grid_convergence(self):
        """F4 critical s0 must not change by >5% when grid is doubled."""
        import numpy as np
        from src.metric_ansatze import alcubierre_einstein_cartan
        from src.energy_conditions import _evaluate_G00_on_grid
        from src.field_equations import compute_einstein_tensor

        def find_critical_s0(n_pts):
            lo, hi = 1.0, 10.0
            for _ in range(30):
                mid = (lo + hi) / 2.0
                m = alcubierre_einstein_cartan(v=1.5, s0=mid, sigma_S=1.0)
                G = compute_einstein_tensor(m)
                effective = G["G00"] + m["_H00"]
                values = _evaluate_G00_on_grid(m, effective, n_points=n_pts)
                if float(np.min(values)) >= -1e-10:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2.0

        s0_base = find_critical_s0(50)
        s0_double = find_critical_s0(100)
        relative_change = abs(s0_double - s0_base) / s0_base
        assert relative_change < 0.05, (
            f"Grid convergence failed: s0 changed by {relative_change:.1%} "
            f"({s0_base:.4f} -> {s0_double:.4f})"
        )
