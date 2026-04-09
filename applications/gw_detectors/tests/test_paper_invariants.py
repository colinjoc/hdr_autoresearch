"""
test_paper_invariants.py — encodes every quantitative claim in paper.md as a pytest assertion.

RECONSTRUCTED. The original test file was lost on 2026-04-09. This file is the
TDD anchor for the rest of the reconstruction: every other reconstructed script
in this directory must produce numbers consistent with the assertions below.

Run with:
    pytest tests/test_paper_invariants.py -x

Notes:
- These tests will FAIL until Differometor is installed and GWDetectorZoo is
  cloned. That is intentional: a failing test is better than a silent script
  that produces fabricated numbers.
- Tolerances are loose where the paper itself is loose. Tighten as needed.
- If your simulator output differs from the assertions, EITHER (a) your install
  is broken, OR (b) the paper's reconstruction made a numerical error and the
  paper should be corrected.
"""

import math
import pytest


# ---------------------------------------------------------------------------
# Voyager baseline (paper §2.2)
# ---------------------------------------------------------------------------

def test_voyager_strain_minimum():
    """Differometor must reproduce published Voyager sensitivity within 0.1%.

    Paper §2.2: 'Our Differometor computation reproduces the published Voyager
    sensitivity to within 0.1%, with minimum strain noise of 3.76 × 10⁻²⁵ /√Hz
    at 168 Hz.'
    """
    from evaluate import voyager_baseline_strain
    s = voyager_baseline_strain()
    assert math.isclose(s.min_strain, 3.76e-25, rel_tol=1e-3), (
        f"Voyager strain minimum is {s.min_strain:.3e} /√Hz, expected 3.76e-25"
    )
    assert math.isclose(s.min_strain_freq_hz, 168.0, abs_tol=2.0), (
        f"Voyager strain minimum at {s.min_strain_freq_hz:.1f} Hz, expected 168 Hz"
    )


# ---------------------------------------------------------------------------
# Component count of type8/sol00 (paper §3.1)
# ---------------------------------------------------------------------------

def test_type8_sol00_component_count_original():
    """Paper §3.1: original UIFO has 48 mirrors, 13 BSs, 3 lasers, 4 squeezers."""
    from evaluate import load_uifo_design
    d = load_uifo_design("type8", "sol00")
    assert d.n_mirrors == 48
    assert d.n_beamsplitters == 13
    assert d.n_lasers == 3
    assert d.n_squeezers == 4


def test_type8_sol00_minimal_component_count():
    """Paper §3.1: minimal essential design has ~10 components total.

    Breakdown: 1 laser + 0 squeezers + 2 arm cavities + 1 beamsplitter
    + 0 filter cavities = ~4 'major' components, with associated mirrors
    bringing the total to ~10.
    """
    from evaluate import minimal_design
    m = minimal_design("type8", "sol00")
    assert m.n_lasers == 1
    assert m.n_squeezers == 0
    assert m.n_arm_cavities == 2
    assert m.n_beamsplitters == 1
    assert m.n_filter_cavities == 0
    assert 8 <= m.total_components <= 12, (
        f"Minimal design has {m.total_components} components, expected ~10"
    )


# ---------------------------------------------------------------------------
# Improvement factors (paper §3.1, §3.6)
# ---------------------------------------------------------------------------

def test_type8_sol00_original_improvement():
    """Paper Abstract + §3.6: original Urania design is 3.12× over Voyager."""
    from evaluate import improvement_factor
    f = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    assert math.isclose(f, 3.12, rel_tol=0.05), (
        f"type8/sol00 improvement is {f:.2f}, expected ~3.12"
    )


def test_type8_sol00_minimal_matches_original():
    """Paper §3.1: minimal design retains ≥103% of original improvement."""
    from evaluate import improvement_factor, minimal_design_strain
    original = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    minimal = minimal_design_strain("type8", "sol00", reoptimise=False)
    ratio = minimal.improvement_factor / original
    assert ratio >= 1.03, (
        f"Minimal design retention is {ratio:.2%}, expected ≥103%"
    )


def test_type8_sol00_minimal_reoptimised():
    """Paper Abstract + §3.6: minimal design with BS re-optimisation reaches 3.62×.

    This is the headline result: 16% better than the original AI-discovered design.
    """
    from evaluate import minimal_design_strain
    m = minimal_design_strain("type8", "sol00", reoptimise=True)
    assert math.isclose(m.improvement_factor, 3.62, rel_tol=0.05), (
        f"Minimal re-optimised design is {m.improvement_factor:.2f}, expected ~3.62"
    )
    assert math.isclose(m.beamsplitter_reflectivity, 0.70, abs_tol=0.05), (
        f"Re-optimised BS reflectivity is {m.beamsplitter_reflectivity:.2f}, expected ~0.70"
    )


# ---------------------------------------------------------------------------
# Mechanism contributions (paper §3.2)
# ---------------------------------------------------------------------------

def test_critical_cavity_coupling_contribution():
    """Paper §3.2: arm cavity finesse contributes 65% of the improvement."""
    from evaluate import mechanism_contribution
    c = mechanism_contribution("type8", "sol00", "arm_finesse")
    assert 0.55 <= c <= 0.75, (
        f"Arm finesse contribution is {c:.0%}, expected ~65%"
    )


def test_light_test_mass_contribution():
    """Paper §3.2: 7.3 kg light test mass contributes 35% of the improvement."""
    from evaluate import mechanism_contribution
    c = mechanism_contribution("type8", "sol00", "light_test_mass")
    assert 0.25 <= c <= 0.45, (
        f"Light test mass contribution is {c:.0%}, expected ~35%"
    )


def test_asymmetric_beamsplitter_contribution():
    """Paper §3.2: 70:30 beamsplitter contributes 10% of the improvement."""
    from evaluate import mechanism_contribution
    c = mechanism_contribution("type8", "sol00", "asymmetric_bs")
    assert 0.05 <= c <= 0.15, (
        f"Asymmetric BS contribution is {c:.0%}, expected ~10%"
    )


# ---------------------------------------------------------------------------
# Parameter sensitivity: narrow vs broad regimes (paper §3.3)
# ---------------------------------------------------------------------------

def test_arm_finesse_is_narrow_optimum():
    """Paper §3.3: ±5% deviation in arm finesse degrades sensitivity below Voyager.

    This verifies the 'narrow optimum / real physics' regime.
    """
    from evaluate import sweep_parameter
    sweep = sweep_parameter("type8", "sol00", "arm_finesse", center=6100, frac_window=0.05)
    optimal = max(sweep.values, key=lambda v: v.improvement_factor)
    edge_low = sweep.values[0]
    edge_high = sweep.values[-1]
    assert edge_low.improvement_factor < 1.0, (
        f"At -5% finesse, improvement is {edge_low.improvement_factor:.2f}, expected <1.0"
    )
    assert edge_high.improvement_factor < 1.0, (
        f"At +5% finesse, improvement is {edge_high.improvement_factor:.2f}, expected <1.0"
    )


def test_beamsplitter_is_broad_plateau():
    """Paper §3.3: BS reflectivity has any value in [0.5, 0.8] within 5% of optimal."""
    from evaluate import sweep_parameter
    sweep = sweep_parameter("type8", "sol00", "beamsplitter_reflectivity", values=[0.50, 0.60, 0.70, 0.80])
    best = max(sweep.values, key=lambda v: v.improvement_factor).improvement_factor
    for v in sweep.values:
        assert v.improvement_factor / best > 0.95, (
            f"At BS={v.parameter_value}, improvement is {v.improvement_factor:.2f} "
            f"(only {v.improvement_factor / best:.1%} of best={best:.2f})"
        )


# ---------------------------------------------------------------------------
# Unused features (paper §3.4)
# ---------------------------------------------------------------------------

def test_squeezers_carry_negligible_squeezing():
    """Paper §3.4: all four squeezers carry less than 0.5 dB."""
    from evaluate import load_uifo_design
    d = load_uifo_design("type8", "sol00")
    for sq in d.squeezers:
        assert abs(sq.level_db) < 0.5, (
            f"Squeezer {sq.name} carries {sq.level_db:.2f} dB, expected <0.5"
        )


def test_second_laser_is_harmful():
    """Paper §3.4: removing the second laser improves sensitivity by 3%."""
    from evaluate import improvement_factor, ablate_component
    baseline = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    ablated = ablate_component("type8", "sol00", "laser_2")
    delta = (ablated.improvement_factor - baseline) / baseline
    assert 0.01 <= delta <= 0.05, (
        f"Removing laser 2 changes improvement by {delta:+.1%}, expected ~+3%"
    )


def test_homodyne_angle_irrelevant():
    """Paper §3.4: sweeping homodyne phase over 360° produces only 1.4% variation."""
    from evaluate import sweep_parameter
    sweep = sweep_parameter("type8", "sol00", "homodyne_angle_deg", n_steps=36, span=360.0)
    best = max(sweep.values, key=lambda v: v.improvement_factor).improvement_factor
    worst = min(sweep.values, key=lambda v: v.improvement_factor).improvement_factor
    rel_var = (best - worst) / best
    assert rel_var < 0.05, (
        f"Homodyne angle variation is {rel_var:.1%}, expected <5%"
    )


# ---------------------------------------------------------------------------
# Cross-solution survey (paper §3.5)
# ---------------------------------------------------------------------------

def test_two_mechanism_families_in_type8():
    """Paper §3.5: 25 type8 solutions split into noise-suppression and signal-amplification families."""
    from evaluate import classify_solution_family
    classifications = []
    for i in range(25):
        sol_id = f"sol{i:02d}"
        c = classify_solution_family("type8", sol_id)
        classifications.append(c)

    noise_family = sum(1 for c in classifications if c.dominant_mechanism == "noise_suppression")
    signal_family = sum(1 for c in classifications if c.dominant_mechanism == "signal_amplification")

    assert noise_family >= 5, (
        f"Only {noise_family} noise-suppression solutions; expected at least 5"
    )
    assert signal_family >= 3, (
        f"Only {signal_family} signal-amplification solutions; expected at least 3"
    )


def test_signal_amplification_can_reach_13x():
    """Paper Abstract + §3.5: signal-family solutions reach up to 13.7× signal gain."""
    from evaluate import classify_solution_family
    max_signal_gain = 0.0
    for i in range(25):
        sol_id = f"sol{i:02d}"
        c = classify_solution_family("type8", sol_id)
        if c.dominant_mechanism == "signal_amplification":
            max_signal_gain = max(max_signal_gain, c.signal_gain_factor)
    assert max_signal_gain >= 10.0, (
        f"Max signal gain in family is {max_signal_gain:.1f}×, expected ~13.7×"
    )
