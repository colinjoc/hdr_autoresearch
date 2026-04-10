"""
Tests for generate_plots.py — verifies that all required plots are created
with correct properties.
"""
import os
import sys
import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")

REQUIRED_PLOTS = [
    "pred_vs_actual.png",
    "feature_importance.png",
    "headline_finding.png",
    "tournament_comparison.png",
    "ablation.png",
]


@pytest.fixture(scope="module")
def generate_all_plots():
    """Run the plot generation script once for all tests."""
    from generate_plots import main
    main()


def test_plots_directory_exists(generate_all_plots):
    assert os.path.isdir(PLOTS_DIR), f"plots/ directory not found at {PLOTS_DIR}"


@pytest.mark.parametrize("filename", REQUIRED_PLOTS)
def test_plot_file_exists(generate_all_plots, filename):
    path = os.path.join(PLOTS_DIR, filename)
    assert os.path.isfile(path), f"Missing plot: {filename}"


@pytest.mark.parametrize("filename", REQUIRED_PLOTS)
def test_plot_file_not_empty(generate_all_plots, filename):
    path = os.path.join(PLOTS_DIR, filename)
    assert os.path.getsize(path) > 1000, f"Plot file too small (likely empty): {filename}"


def test_plot_files_are_valid_png(generate_all_plots):
    """Check PNG magic bytes for each plot."""
    png_magic = b"\x89PNG\r\n\x1a\n"
    for filename in REQUIRED_PLOTS:
        path = os.path.join(PLOTS_DIR, filename)
        with open(path, "rb") as f:
            header = f.read(8)
        assert header == png_magic, f"{filename} is not a valid PNG file"
