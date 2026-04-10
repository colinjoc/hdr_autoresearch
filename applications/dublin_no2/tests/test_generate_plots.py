"""Tests for generate_plots.py — verifies all 5 plots are created and valid."""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, '/home/col/generalized_hdr_autoresearch/applications/dublin_no2')

PROJECT_DIR = Path('/home/col/generalized_hdr_autoresearch/applications/dublin_no2')
PLOTS_DIR = PROJECT_DIR / 'plots'

EXPECTED_PLOTS = [
    'pred_vs_actual.png',
    'feature_importance.png',
    'headline_finding.png',
    'covid_validation.png',
    'source_attribution.png',
]


def test_generate_plots_creates_directory():
    """Running generate_plots should create the plots/ directory."""
    import generate_plots
    generate_plots.main()
    assert PLOTS_DIR.is_dir(), "plots/ directory was not created"


def test_all_expected_plots_exist():
    """All 5 required plot files should exist after generation."""
    for fname in EXPECTED_PLOTS:
        fpath = PLOTS_DIR / fname
        assert fpath.exists(), f"Missing plot: {fname}"


def test_plots_are_nonempty_pngs():
    """Each plot file should be a non-empty PNG (starts with PNG magic bytes)."""
    PNG_MAGIC = b'\x89PNG'
    for fname in EXPECTED_PLOTS:
        fpath = PLOTS_DIR / fname
        assert fpath.exists(), f"Missing: {fname}"
        data = fpath.read_bytes()
        assert len(data) > 1000, f"{fname} is too small ({len(data)} bytes)"
        assert data[:4] == PNG_MAGIC, f"{fname} is not a valid PNG"


def test_plots_are_300dpi():
    """Plots should be saved at 300 DPI (file size proxy: >50KB for a real chart)."""
    for fname in EXPECTED_PLOTS:
        fpath = PLOTS_DIR / fname
        assert fpath.exists(), f"Missing: {fname}"
        size_kb = fpath.stat().st_size / 1024
        assert size_kb > 50, f"{fname} is only {size_kb:.0f}KB — expected >50KB at 300 DPI"
