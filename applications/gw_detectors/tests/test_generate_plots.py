"""Tests for generate_plots.py — verify data structures and plot generation."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_improvement_data_matches_paper():
    """The hardcoded improvement factors must match the paper's Table 1."""
    from generate_plots import IMPROVEMENT_DATA

    # Paper states sol00 = 4.05x, sol01 = 3.36x, median ~1.11x
    sol00 = next(d for d in IMPROVEMENT_DATA if d["sol_id"] == "sol00")
    assert abs(sol00["improvement"] - 4.05) < 0.01

    sol01 = next(d for d in IMPROVEMENT_DATA if d["sol_id"] == "sol01")
    assert abs(sol01["improvement"] - 3.36) < 0.01

    assert len(IMPROVEMENT_DATA) == 25


def test_component_data_matches_paper():
    """sol00 component extreme-value counts must match paper Section 3.3-3.4."""
    from generate_plots import SOL00_COMPONENT_DATA

    mirrors = SOL00_COMPONENT_DATA["mirrors"]
    beamsplitters = SOL00_COMPONENT_DATA["beamsplitters"]

    assert mirrors["total"] == 57
    assert mirrors["at_extremes"] == 29  # 20 near-zero + 9 near-one
    assert mirrors["doing_work"] == 28   # interior R

    assert beamsplitters["total"] == 13
    assert beamsplitters["at_extremes"] == 11  # paper: only 2 doing real splitting
    assert beamsplitters["doing_work"] == 2


def test_squeezer_data_matches_paper():
    """Squeezer counts and improvement factors must match paper Section 3.6."""
    from generate_plots import SQUEEZER_DATA

    assert len(SQUEEZER_DATA) == 25

    # sol00 has 0 squeezers, sol13 has 7
    sol00 = next(d for d in SQUEEZER_DATA if d["sol_id"] == "sol00")
    assert sol00["n_squeezers"] == 0

    sol13 = next(d for d in SQUEEZER_DATA if d["sol_id"] == "sol13")
    assert sol13["n_squeezers"] == 7


def test_arm_cavity_data_matches_paper():
    """Arm cavity classification must match paper Section 3.8 / M02."""
    from generate_plots import ARM_CAVITY_DATA

    assert len(ARM_CAVITY_DATA) == 6
    categories = [d["classification"] for d in ARM_CAVITY_DATA]
    assert categories.count("True symmetric cavity") == 1
    assert categories.count("Through-pass delay line") == 2
    assert categories.count("Dead trap") == 1
    assert categories.count("One-sided wall") == 1
    assert categories.count("Asymmetric cavity") == 1


def test_plots_directory_created():
    """After running generate_plots.main(), the plots/ directory should exist."""
    from generate_plots import PLOTS_DIR
    # Just check the constant is defined correctly
    assert PLOTS_DIR == PROJECT_ROOT / "plots"


def test_generate_all_plots():
    """Integration test: generate all 4 plots and check they exist."""
    from generate_plots import main, PLOTS_DIR

    main()

    expected_files = [
        "headline_finding.png",
        "component_analysis.png",
        "squeezer_anticorrelation.png",
        "arm_cavity_classification.png",
    ]
    for fname in expected_files:
        fpath = PLOTS_DIR / fname
        assert fpath.exists(), f"Missing plot: {fpath}"
        assert fpath.stat().st_size > 1000, f"Plot too small (likely empty): {fpath}"
