"""Tests for generate_plots.py — verify all plot files exist and are valid PNGs."""
import os
import pytest

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOTS_DIR = os.path.join(PROJ_DIR, "plots")

EXPECTED_PLOTS = [
    "pred_vs_actual.png",
    "feature_importance.png",
    "headline_finding.png",
    "era_comparison.png",
    "retrofit_cost_effectiveness.png",
]


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_exists(filename):
    """Each expected plot file must exist."""
    path = os.path.join(PLOTS_DIR, filename)
    assert os.path.exists(path), f"Missing plot: {path}"


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_is_valid_png(filename):
    """Each plot file must be a valid PNG (starts with PNG magic bytes)."""
    path = os.path.join(PLOTS_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"Plot not generated yet: {filename}")
    with open(path, "rb") as f:
        header = f.read(8)
    # PNG magic: \x89PNG\r\n\x1a\n
    assert header[:4] == b"\x89PNG", f"{filename} is not a valid PNG"


@pytest.mark.parametrize("filename", EXPECTED_PLOTS)
def test_plot_not_empty(filename):
    """Each plot file must have non-trivial size (> 10 KB for a real chart)."""
    path = os.path.join(PLOTS_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"Plot not generated yet: {filename}")
    size = os.path.getsize(path)
    assert size > 10_000, f"{filename} is suspiciously small ({size} bytes)"
