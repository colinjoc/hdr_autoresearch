"""Activation-avalanche detection.

Definition (per ~/entropy_ideation/knowledge_base.md §2.1):
- Event: a unit's activation > threshold θ at a given token/time.
- Avalanche: contiguous time-windows of non-zero events, bounded by
  quiescent (all-below-θ) intervals.

For a layer of shape (T, d_model), we slide a bin of size Δ_T across the T
axis, count active units per bin, and identify avalanches as runs of
positive bin-counts separated by zero bins.
"""

from __future__ import annotations

import numpy as np


def binarise_activations(
    acts: np.ndarray, threshold: float, zscore: bool = False, eps: float = 1e-6,
) -> np.ndarray:
    """Return a (T, d) boolean mask of units with activation-event.

    Parameters
    ----------
    acts : (T, d) activations
    threshold : scalar, units depend on ``zscore``
    zscore : if True, z-score each column (neuron) before thresholding, so
             threshold is in standard-deviation units. This is the standard
             cortical-avalanche-detection protocol (Beggs-Plenz 2003) and
             produces sparse event rasters even for dense continuous signals.
             If False, threshold is the raw activation magnitude.
    """
    if zscore:
        mu = acts.mean(axis=0, keepdims=True)
        sigma = acts.std(axis=0, keepdims=True) + eps
        z = (acts - mu) / sigma
        return np.abs(z) > threshold
    return np.abs(acts) > threshold


def detect_avalanches(
    binary: np.ndarray,
    bin_size: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Detect avalanches from a binarised (T, d) boolean event matrix.

    Returns
    -------
    sizes     : 1-D int array of avalanche sizes (sum of events within)
    durations : 1-D int array of avalanche durations in bins

    Methodology:
    - bin_size > 1 coarsens time: per-bin event-count = sum over bin
      window of per-token event counts.
    - An avalanche starts when a bin has > 0 events after ≥ 1 zero bin,
      and ends at the next zero bin.
    """
    per_bin = binary.sum(axis=1)  # (T,) int
    if bin_size > 1:
        T = len(per_bin)
        trunc = (T // bin_size) * bin_size
        per_bin = per_bin[:trunc].reshape(-1, bin_size).sum(axis=1)

    if per_bin.size == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64)

    active = per_bin > 0
    # Use transitions to find avalanche start/end indices.
    diffs = np.diff(active.astype(np.int8), prepend=0, append=0)
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]  # exclusive end

    sizes = np.array(
        [per_bin[s:e].sum() for s, e in zip(starts, ends)], dtype=np.int64
    )
    durations = (ends - starts).astype(np.int64)
    return sizes, durations


def threshold_plateau(
    acts: np.ndarray,
    thresholds: list[float],
    bin_size: int = 1,
    zscore: bool = False,
) -> dict[float, tuple[np.ndarray, np.ndarray]]:
    """Return {threshold: (sizes, durations)} across a threshold sweep.

    Used to verify that inferred exponents plateau across a reasonable
    θ range — a mandatory-evidence-bar item per knowledge_base §5.
    """
    return {
        th: detect_avalanches(binarise_activations(acts, th, zscore=zscore), bin_size)
        for th in thresholds
    }
