"""Tests for generate_plots.py — verify all four plots are created and non-empty."""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = PROJECT_ROOT / "plots"

EXPECTED_PLOTS = [
    "pred_vs_actual.png",
    "feature_importance.png",
    "headline_finding.png",
    "co2_comparison.png",
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
