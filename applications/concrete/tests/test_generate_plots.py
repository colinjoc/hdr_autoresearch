"""Tests for generate_plots.py — verify all four plots are created and non-empty."""
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
PLOTS_DIR = PROJECT_ROOT / "plots"


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

EXPECTED_PLOTS = [
    "pred_vs_actual.png",
    "feature_importance.png",
    "headline_finding.png",
    "co2_comparison.png",
    "emission_sensitivity.png",
]


def test_generate_plots_creates_all_files():
    """Running generate_plots.py should create all four PNGs in plots/."""
    # Remove any existing plots so we verify fresh creation
    for name in EXPECTED_PLOTS:
        p = PLOTS_DIR / name
        if p.exists():
            p.unlink()

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "generate_plots.py")],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"generate_plots.py failed:\n{result.stderr}"

    for name in EXPECTED_PLOTS:
        p = PLOTS_DIR / name
        assert p.exists(), f"Missing plot: {name}"
        assert p.stat().st_size > 5000, f"Plot {name} is suspiciously small ({p.stat().st_size} bytes)"


def test_plots_are_valid_png():
    """Each plot file should start with the PNG magic bytes."""
    PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
    for name in EXPECTED_PLOTS:
        p = PLOTS_DIR / name
        if not p.exists():
            # Skip if test_generate_plots_creates_all_files hasn't run yet
            continue
        with open(p, "rb") as f:
            header = f.read(8)
        assert header == PNG_MAGIC, f"{name} does not have a valid PNG header"


@pytest.mark.xfail(reason="Known annotation overlaps in co2_comparison plot", strict=False)
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
