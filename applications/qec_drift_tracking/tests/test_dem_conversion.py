"""Tests for willow_loader.dem_to_pcm.

Invariants tested:
- Hand-built small DEM → H, O, rates match expected definition
- Output shapes consistent with num_detectors/num_observables/num_errors
- rates array is monotone with DEM error probabilities
"""
from __future__ import annotations

import numpy as np
import pytest
import stim

from willow_loader import dem_to_pcm


def test_dem_to_pcm_hand_built():
    """Hand-build a 2-detector 1-observable DEM with two error mechanisms.
    Verify H and obs_mat row/col structure by hand.
    """
    dem = stim.DetectorErrorModel()
    dem.append("error", [0.1], [stim.target_relative_detector_id(0),
                                 stim.target_relative_detector_id(1),
                                 stim.target_logical_observable_id(0)])
    dem.append("error", [0.05], [stim.target_relative_detector_id(0)])
    H, O, rates = dem_to_pcm(dem)
    # 2 detectors, 2 errors
    assert H.shape == (2, 2)
    # 1 observable, 2 errors
    assert O.shape == (1, 2)
    # First error hits detectors 0 and 1 and observable 0
    assert H[0, 0] == 1 and H[1, 0] == 1
    assert O[0, 0] == 1
    # Second error hits only detector 0
    assert H[0, 1] == 1 and H[1, 1] == 0
    assert O[0, 1] == 0
    # Rates match
    np.testing.assert_allclose(rates, [0.1, 0.05])


def test_dem_to_pcm_single_error():
    dem = stim.DetectorErrorModel()
    dem.append("error", [0.2], [stim.target_relative_detector_id(5)])
    # 6 detectors (0..5), 0 observables
    H, O, rates = dem_to_pcm(dem)
    assert H.shape == (6, 1)
    assert O.shape == (0, 1)
    assert H[5, 0] == 1
    assert H[:5, 0].sum() == 0
    assert rates[0] == pytest.approx(0.2)


def test_dem_to_pcm_dtypes():
    dem = stim.DetectorErrorModel()
    dem.append("error", [0.1], [stim.target_relative_detector_id(0),
                                 stim.target_relative_detector_id(1)])
    H, O, rates = dem_to_pcm(dem)
    assert H.dtype == np.uint8
    assert O.dtype == np.uint8
    assert rates.dtype == np.float64
