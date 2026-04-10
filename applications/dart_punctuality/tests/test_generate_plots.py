"""Tests for generate_plots.py — verify all five plots are created."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

PLOTS_DIR = APP_DIR / "plots"

EXPECTED_PLOTS = [
    "pred_vs_actual.png",
    "feature_importance.png",
    "headline_finding.png",
    "cascade_risk_calendar.png",
    "timetable_vs_weather.png",
]


@pytest.fixture(scope="module")
def generated_plots():
    """Run generate_plots.main() once for the test module."""
    from generate_plots import main
    main()
    return PLOTS_DIR


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_exists_and_nonempty(generated_plots, filename):
    """Each expected plot file must exist and have non-trivial size."""
    path = generated_plots / filename
    assert path.exists(), f"{filename} was not created"
    assert path.stat().st_size > 5_000, f"{filename} is suspiciously small ({path.stat().st_size} bytes)"


def test_plots_are_png(generated_plots):
    """All output files should be valid PNGs (check magic bytes)."""
    PNG_MAGIC = b"\x89PNG"
    for filename in EXPECTED_PLOTS:
        path = generated_plots / filename
        with open(path, "rb") as f:
            header = f.read(4)
        assert header == PNG_MAGIC, f"{filename} does not have PNG magic bytes"
