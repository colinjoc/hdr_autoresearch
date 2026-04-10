"""Tests for generate_plots.py -- verify all four plots are created and valid."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PLOTS_DIR = PROJECT_ROOT / "plots"
EXPECTED_PLOTS = [
    "pred_vs_actual.png",
    "feature_importance.png",
    "headline_finding.png",
    "tree_to_linear.png",
]


@pytest.fixture(scope="module")
def run_generate_plots():
    """Run the generate_plots module once for all tests in this module."""
    import generate_plots
    generate_plots.main()


def test_plots_directory_exists(run_generate_plots):
    assert PLOTS_DIR.is_dir(), f"plots/ directory not found at {PLOTS_DIR}"


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_file_created(run_generate_plots, filename):
    path = PLOTS_DIR / filename
    assert path.is_file(), f"Missing plot: {path}"


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_file_not_empty(run_generate_plots, filename):
    path = PLOTS_DIR / filename
    assert path.stat().st_size > 1000, (
        f"Plot file {filename} is suspiciously small ({path.stat().st_size} bytes)"
    )


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_is_valid_png(run_generate_plots, filename):
    """Check the PNG magic bytes."""
    path = PLOTS_DIR / filename
    with open(path, "rb") as f:
        header = f.read(8)
    assert header[:4] == b"\x89PNG", f"{filename} does not have a valid PNG header"
