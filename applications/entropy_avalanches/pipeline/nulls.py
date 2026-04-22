"""Neutral-null and Griffiths-phase rejection battery.

Phase 0.25 evidence-bar item 8: any α ≈ 3/2 claim must rule out
Griffiths-phase (Moretti-Muñoz 2013, Martinello 2017, di Santo 2018) and
neutral null (Touboul-Destexhe 2010/2017) models that can produce the
same marginal distribution without a phase transition.

Tests:
1. Shuffle-in-time null: randomise per-unit time axis; if the shuffled
   data still shows power-law, the apparent criticality is purely a
   marginal-activity-distribution artefact.
2. Coherent-bursting null: generate a multiplicative-stochastic process
   with a heavy-tailed drive but no branching dynamics; confirm the real
   data is distinguishable.
3. Sethna scaling-relation check: implemented in ``exponents.py`` — the
   primary Griffiths-rejection signal (Griffiths phases do NOT generally
   close the γ = (β − 1)/(α − 1) relation).
"""

from __future__ import annotations

import dataclasses

import numpy as np


@dataclasses.dataclass
class NullRejection:
    shuffled_alpha: float
    shuffled_p: float  # p-value that shuffled data is power-law
    real_alpha: float
    real_p: float
    distinguishable: bool


def shuffle_null(
    activations: np.ndarray, threshold: float, bin_size: int = 1,
    rng_seed: int = 0,
) -> NullRejection:
    """Temporal-shuffle null: randomise each unit's time axis, re-detect
    avalanches, confirm the shuffled distribution does NOT fit a power
    law as well as the real one."""
    from pipeline.avalanche_detection import binarise_activations, detect_avalanches
    from pipeline.exponents import fit_power_law

    rng = np.random.default_rng(rng_seed)
    shuffled = activations.copy()
    for j in range(shuffled.shape[1]):
        rng.shuffle(shuffled[:, j])

    real_binary = binarise_activations(activations, threshold)
    sh_binary = binarise_activations(shuffled, threshold)
    real_sizes, _ = detect_avalanches(real_binary, bin_size=bin_size)
    sh_sizes, _ = detect_avalanches(sh_binary, bin_size=bin_size)

    try:
        real_fit = fit_power_law(real_sizes)
    except ValueError:
        real_fit = None
    try:
        sh_fit = fit_power_law(sh_sizes)
    except ValueError:
        sh_fit = None

    if real_fit is None:
        return NullRejection(
            shuffled_alpha=sh_fit.alpha if sh_fit else float("nan"),
            shuffled_p=sh_fit.p_vs_exponential if sh_fit else float("nan"),
            real_alpha=float("nan"), real_p=float("nan"),
            distinguishable=False,
        )

    # If the real α differs from shuffled α by more than 0.1 AND the real
    # fit has better log-likelihood-ratio against exponential, the
    # criticality claim is distinguishable from the shuffle null.
    if sh_fit is None:
        distinguishable = True
    else:
        distinguishable = (
            abs(real_fit.alpha - sh_fit.alpha) > 0.1
            and real_fit.p_vs_exponential < sh_fit.p_vs_exponential
        )
    return NullRejection(
        shuffled_alpha=sh_fit.alpha if sh_fit else float("nan"),
        shuffled_p=sh_fit.p_vs_exponential if sh_fit else float("nan"),
        real_alpha=real_fit.alpha, real_p=real_fit.p_vs_exponential,
        distinguishable=distinguishable,
    )
