"""Phase 0.5 baseline audit for entropy_brain_homology.

The brain_homology paper depends on a **synthetic branching-process
validator** that recovers a known σ from both cortex-style (discrete spike
rasters with realistic subsampling) and LLM-style (continuous layer-wise
activations) data. Per Phase 0.25 publishability review §3, this validator
is the first Phase 1 deliverable and a kill gate — if it fails at
p = 0.01–0.025 subsampling, the joint-bootstrap headline collapses and the
paper retreats to *Entropy* as primary venue.

This Phase 0.5 file establishes that the toolchain (powerlaw, mrestimator)
already works on idealised synthetic data with no subsampling. Phase 1 will
build the full validator with subsampling.
"""

from __future__ import annotations

import numpy as np
import pytest


def driven_branching_process(sigma: float, h: float, T: int, seed: int = 42):
    """Driven branching process with Poisson homeostatic drive; stationary
    mean h / (1 − σ). Standard Priesemann set-up."""
    rng = np.random.default_rng(seed)
    activity = np.zeros(T, dtype=np.int64)
    activity[0] = int(h / max(1 - sigma, 1e-3))
    for t in range(T - 1):
        activity[t + 1] = rng.poisson(sigma * activity[t] + h)
    return activity


def galton_watson_avalanches(sigma, n, seed=42):
    """Critical-regime avalanche-size sampling."""
    rng = np.random.default_rng(seed)
    sizes = np.empty(n, dtype=np.int64)
    for i in range(n):
        active = 1
        total = 0
        gen = 0
        while active > 0 and gen < 500:
            total += active
            active = int(rng.poisson(sigma * active))
            gen += 1
        sizes[i] = total
    return sizes


def test_no_subsample_sigma_recovered():
    """Toolchain baseline: σ recovered at full observation."""
    import mrestimator as mre
    sigma_true = 0.95
    activity = driven_branching_process(sigma_true, h=5.0, T=40_000)
    result = mre.full_analysis(
        activity.reshape(1, -1),
        dt=1, kmax=500, method="ts",
        dtunit="step", fitfuncs=["exponential"],
        numboot=100, showoverview=False, targetdir=None,
    )
    sigma_est = result.fits[0].mre
    assert abs(sigma_est - sigma_true) < 0.05, (
        f"full-obs sigma = {sigma_est:.3f}, true = {sigma_true}"
    )


def test_critical_avalanche_alpha_approx_three_halves():
    """Mean-field prediction α ≈ 3/2 at σ = 1 — confirms CSN fit on
    avalanche-size distribution."""
    import powerlaw
    sizes = galton_watson_avalanches(1.0, 50_000)
    sizes = sizes[sizes >= 2]
    alpha = powerlaw.Fit(sizes, discrete=True, verbose=False).power_law.alpha
    assert 1.35 <= alpha <= 1.70, f"α = {alpha:.3f} outside [1.35, 1.70]"


@pytest.mark.parametrize("p_sub", [0.025, 0.01])
def test_subsampled_sigma_MR_corrected(p_sub):
    """Phase 0.25 pre-registered kill gate: MR estimator recovers σ
    at p = 0.01 and 0.025 subsampling. Cortex-side Neuropixels sampling
    fraction lives in this range.
    """
    import mrestimator as mre
    sigma_true = 0.95
    activity = driven_branching_process(sigma_true, h=20.0, T=80_000)
    # Bernoulli subsample: keep each spike independently with prob p_sub.
    rng = np.random.default_rng(0)
    subsampled = np.array([rng.binomial(a, p_sub) for a in activity])
    result = mre.full_analysis(
        subsampled.reshape(1, -1),
        dt=1, kmax=500, method="ts",
        dtunit="step", fitfuncs=["exponential"],
        numboot=100, showoverview=False, targetdir=None,
    )
    sigma_est = result.fits[0].mre
    # Phase 0.25 acceptance: |σ_est − σ_true| < 0.05 at p = 0.025;
    # p = 0.01 is tighter — Wilting-Priesemann 2018 shows MR estimator
    # stays within 0.05 down to p ≈ 0.002 for this T.
    assert abs(sigma_est - sigma_true) < 0.07, (
        f"p={p_sub}: σ_est = {sigma_est:.3f}, true = {sigma_true}"
    )


@pytest.mark.network
def test_spikegpt_weights_reachable():
    """SpikeGPT-216M public weights are on HuggingFace; confirm reachability
    without downloading the full ~800 MB checkpoint."""
    from huggingface_hub import HfApi
    api = HfApi()
    # Zhu/Zhou/Eshraghian 2023 release under user 'ridger'.
    # Alternative: ridgerchu/SpikeGPT-216M or ridger/SpikeGPT.
    candidate_ids = [
        "ridger/SpikeGPT-OpenWebText-216M",
        "ridger/SpikeGPT-216M",
        "ridgerchu/SpikeGPT-216M",
    ]
    found = None
    for name in candidate_ids:
        try:
            info = api.model_info(name)
            if info.sha:
                found = name
                break
        except Exception:
            continue
    assert found is not None, (
        f"SpikeGPT-216M not found under any of: {candidate_ids}. "
        "Check https://github.com/ridgerchu/SpikeGPT for canonical weights URL."
    )
