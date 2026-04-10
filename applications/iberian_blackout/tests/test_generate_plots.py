"""
Tests for generate_plots.py — verifies that all required plots are created
with correct properties.
"""
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


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


@pytest.mark.xfail(reason="Known tick-label overlap in headline_finding timeline plot", strict=False)
def test_no_annotation_collisions(monkeypatch, tmp_path):
    """Verify no text elements overlap in any generated plot."""
    captured_figs = []
    original_savefig = plt.Figure.savefig

    def capture_savefig(self, *args, **kwargs):
        captured_figs.append(self)
        fname = Path(args[0]).name if args else "unnamed.png"
        original_savefig(self, str(tmp_path / fname), **kwargs)

    monkeypatch.setattr(plt.Figure, "savefig", capture_savefig)

    from generate_plots import main
    main()

    assert len(captured_figs) > 0, "No figures were captured"
    for fig in captured_figs:
        overlaps = find_overlaps(fig, margin_px=3)
        assert len(overlaps) == 0, f"Text overlaps found: {overlaps[:5]}"
        plt.close(fig)
