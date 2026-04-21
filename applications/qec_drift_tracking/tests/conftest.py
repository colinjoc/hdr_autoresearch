"""Shared fixtures for qec_drift_tracking tests."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to sys.path so tests can import project modules.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def small_H() -> np.ndarray:
    """A deterministic 10x30 parity-check matrix (seed 42) with ~15% density."""
    rng = np.random.default_rng(42)
    return (rng.random((10, 30)) < 0.15).astype(np.uint8)


@pytest.fixture
def base_rate() -> float:
    return 1e-3


@pytest.fixture
def tiny_css_H() -> np.ndarray:
    """A hand-built repetition-code H: 2 checks × 3 qubits.
       Check 0 covers qubits 0, 1. Check 1 covers qubits 1, 2."""
    return np.array([[1, 1, 0],
                     [0, 1, 1]], dtype=np.uint8)
