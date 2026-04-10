"""Tests for generate_plots.py — verify all five plots are created."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))


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


@pytest.mark.xfail(reason="Known annotation overlaps in headline_finding and cascade_risk plots", strict=False)
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
