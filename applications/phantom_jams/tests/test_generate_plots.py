"""Tests for generate_plots.py — verify that all required plots are created."""

import os
import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))


PLOTS_DIR = APP_DIR / "plots"

REQUIRED_PLOTS = [
    "trajectory_baseline.png",
    "trajectory_suppressed.png",
    "headline_finding.png",
    "controller_comparison.png",
    "pareto_front.png",
]


@pytest.fixture(scope="session", autouse=True)
def generate_plots():
    """Run generate_plots.py once before all tests."""
    import generate_plots
    generate_plots.main()


class TestPlotsExist:
    @pytest.mark.parametrize("filename", REQUIRED_PLOTS)
    def test_plot_file_exists(self, filename):
        path = PLOTS_DIR / filename
        assert path.exists(), f"Missing plot: {path}"

    @pytest.mark.parametrize("filename", REQUIRED_PLOTS)
    def test_plot_file_not_empty(self, filename):
        path = PLOTS_DIR / filename
        assert path.stat().st_size > 1000, f"Plot too small (likely broken): {path}"

    def test_no_more_than_six_plots(self):
        pngs = list(PLOTS_DIR.glob("*.png"))
        assert len(pngs) <= 6, f"Too many plots ({len(pngs)}), max is 6"

    def test_at_least_five_plots(self):
        pngs = list(PLOTS_DIR.glob("*.png"))
        assert len(pngs) >= 5, f"Too few plots ({len(pngs)}), need at least 5"
