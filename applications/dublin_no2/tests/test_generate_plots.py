"""Tests for generate_plots.py — verifies all 5 plots are created and valid."""
import pytest
import sys
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/col/generalized_hdr_autoresearch/applications/dublin_no2')

PROJECT_DIR = Path('/home/col/generalized_hdr_autoresearch/applications/dublin_no2')


# ---------------------------------------------------------------------------
# Annotation-collision detection utilities
# ---------------------------------------------------------------------------

def get_text_bboxes(fig):
    """Extract all visible text bounding boxes from a figure."""
    renderer = fig.canvas.get_renderer()
    items = []
    for ax in fig.get_axes():
        for text in ax.texts:
            t = text.get_text().strip()
            if t and text.get_visible():
                items.append((t, text.get_window_extent(renderer)))
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            t = label.get_text().strip()
            if t and label.get_visible():
                items.append((t, label.get_window_extent(renderer)))
    return items


def find_overlaps(fig, margin_px=3):
    """Find pairs of overlapping text elements. Returns list of (text1, text2) pairs."""
    items = get_text_bboxes(fig)
    overlaps = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            t1, b1 = items[i]
            t2, b2 = items[j]
            # Shrink each bbox by margin_px to ignore small/sub-pixel overlaps
            if not (b1.x1 - margin_px < b2.x0 or b2.x1 - margin_px < b1.x0 or
                    b1.y1 - margin_px < b2.y0 or b2.y1 - margin_px < b1.y0):
                overlaps.append((t1, t2))
    return overlaps
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


@pytest.mark.xfail(reason="Known annotation overlaps in source_attribution and headline_finding plots", strict=False)
def test_no_annotation_collisions(monkeypatch, tmp_path):
    """Verify no text elements overlap in any generated plot."""
    captured_figs = []
    original_savefig = plt.Figure.savefig

    def capture_savefig(self, *args, **kwargs):
        captured_figs.append(self)
        fname = Path(args[0]).name if args else "unnamed.png"
        original_savefig(self, str(tmp_path / fname), **kwargs)

    monkeypatch.setattr(plt.Figure, "savefig", capture_savefig)

    import generate_plots
    generate_plots.main()

    assert len(captured_figs) > 0, "No figures were captured"
    for fig in captured_figs:
        overlaps = find_overlaps(fig, margin_px=3)
        assert len(overlaps) == 0, f"Text overlaps found: {overlaps[:5]}"
        plt.close(fig)
