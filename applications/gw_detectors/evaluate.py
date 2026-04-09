"""
evaluate.py — RECONSTRUCTED harness for the gw_detectors HDR project.

Original lost on 2026-04-09. This module wraps Differometor with the small set
of high-level operations the 15 experiment scripts and the test suite call.

Status: reconstruction-faithful skeleton. Every function below has the correct
signature and return type to satisfy `tests/test_paper_invariants.py`. The
INTERNAL implementation calls into Differometor; those calls are placeholder-
faithful and need to be verified against the live Differometor API before
the tests will pass.

Verification path:
    1. pip install differometor (or `pip install -e Differometor/`)
    2. git clone https://github.com/artificial-scientist-lab/GWDetectorZoo
    3. pytest tests/test_paper_invariants.py -x
    4. Iterate on the function bodies below until the tests pass.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from utils import (
    UIFODesign, Squeezer, StrainResult, MinimalDesign,
    SweepValue, SweepResult, AblationResult, FamilyClassification,
    ZOO_DIR, DIFFEROMETOR_DIR, assert_environment,
)


# Import Differometor as `df`. Wrapped in try/except so that this module can
# at least be imported in environments where Differometor is not yet installed
# (e.g. for static analysis).
try:
    import differometor as df  # noqa: F401  pylint: disable=import-error
    _HAVE_DIFFEROMETOR = True
except ImportError:  # pragma: no cover
    df = None
    _HAVE_DIFFEROMETOR = False


# ---------------------------------------------------------------------------
# Voyager baseline
# ---------------------------------------------------------------------------

def voyager_baseline_strain() -> StrainResult:
    """Compute the LIGO Voyager strain noise spectrum.

    Paper §2.2: 200 kg silicon test masses at 123 K, 2 µm laser, 10 dB FDS,
    minimum 3.76e-25 /√Hz at 168 Hz.
    """
    assert_environment()
    # TODO: verify against actual Differometor API
    # voyager = df.designs.voyager()
    # f, h = df.compute_strain(voyager)
    # idx = np.argmin(h)
    # return StrainResult(min_strain=float(h[idx]), min_strain_freq_hz=float(f[idx]))
    raise NotImplementedError(
        "Hook me up to Differometor's actual voyager design loader. "
        "Expected output: min_strain ≈ 3.76e-25 at 168 Hz."
    )


# ---------------------------------------------------------------------------
# UIFO design loading
# ---------------------------------------------------------------------------

def load_uifo_design(type_id: str, sol_id: str) -> UIFODesign:
    """Load a UIFO design from the GWDetectorZoo by type and solution id.

    Paper §3.1 for the type8/sol00 component counts:
        48 mirrors, 13 beamsplitters, 3 lasers, 4 squeezers
    """
    assert_environment()
    # TODO: verify the actual JSON schema in GWDetectorZoo
    # zoo_path = ZOO_DIR / type_id / f"{sol_id}.json"
    # raw = json.loads(zoo_path.read_text())
    # return UIFODesign(
    #     type_id=type_id,
    #     sol_id=sol_id,
    #     n_mirrors=count_mirrors(raw),
    #     n_beamsplitters=count_beamsplitters(raw),
    #     n_lasers=count_lasers(raw),
    #     n_squeezers=count_squeezers(raw),
    #     n_filter_cavities=count_filter_cavities(raw),
    #     arm_cavity_finesse=infer_finesse(raw),
    #     test_mass_kg=infer_test_mass(raw),
    #     beamsplitter_reflectivity=infer_main_bs_reflectivity(raw),
    #     squeezers=[Squeezer(s["name"], s["level_db"]) for s in raw["squeezers"]],
    #     raw_parameters=raw,
    # )
    raise NotImplementedError(
        f"Hook me up to GWDetectorZoo loader for {type_id}/{sol_id}."
    )


# ---------------------------------------------------------------------------
# Improvement factor
# ---------------------------------------------------------------------------

def improvement_factor(
    type_id: str, sol_id: str, band_hz: Tuple[float, float]
) -> float:
    """Improvement factor over Voyager averaged in log-space across the band.

    Paper §2.1: improvement = ratio of Voyager strain to candidate strain,
    averaged in log space over the target frequency band.
    """
    assert_environment()
    # TODO: verify against actual Differometor API
    # voyager_h = df.compute_strain(df.designs.voyager(), freq_band=band_hz)
    # cand_h = df.compute_strain(df.designs.zoo(type_id, sol_id), freq_band=band_hz)
    # ratio = voyager_h / cand_h
    # return float(np.exp(np.mean(np.log(ratio))))
    raise NotImplementedError(
        f"Hook me up to compute log-space improvement for {type_id}/{sol_id} in {band_hz} Hz. "
        "Expected for type8/sol00 in (800, 3000): ~3.12"
    )


# ---------------------------------------------------------------------------
# Component ablation
# ---------------------------------------------------------------------------

def ablate_component(
    type_id: str, sol_id: str, component_name: str
) -> AblationResult:
    """Ablate one component from a design and measure the change in improvement.

    Paper §3.4: removing the second laser improves sensitivity by ~3%.
    """
    assert_environment()
    baseline = improvement_factor(type_id, sol_id, band_hz=(800, 3000))
    # TODO: actual ablation
    # design = df.designs.zoo(type_id, sol_id)
    # ablated_design = df.ablate(design, component_name)
    # ablated_h = df.compute_strain(ablated_design, freq_band=(800, 3000))
    # ablated = log_avg_improvement(voyager_h, ablated_h)
    raise NotImplementedError(
        f"Hook me up to ablate {component_name} on {type_id}/{sol_id}."
    )


# ---------------------------------------------------------------------------
# Mechanism contributions
# ---------------------------------------------------------------------------

def mechanism_contribution(
    type_id: str, sol_id: str, mechanism: str
) -> float:
    """Fraction of the total improvement attributable to one mechanism.

    Paper §3.2:
        arm_finesse        → 65%
        light_test_mass    → 35%
        asymmetric_bs      → 10%
    Sums to >100% because mechanisms partially overlap; each is measured by
    setting that one component to its Voyager-equivalent value while the
    others stay at AI-discovered values.
    """
    assert_environment()
    # TODO: implement the parameter substitution
    raise NotImplementedError(
        f"Hook me up to compute {mechanism} contribution for {type_id}/{sol_id}."
    )


# ---------------------------------------------------------------------------
# Parameter sweeps
# ---------------------------------------------------------------------------

def sweep_parameter(
    type_id: str,
    sol_id: str,
    parameter_name: str,
    *,
    center: Optional[float] = None,
    frac_window: Optional[float] = None,
    values: Optional[List[float]] = None,
    n_steps: Optional[int] = None,
    span: Optional[float] = None,
) -> SweepResult:
    """Sweep a single parameter and return the improvement at each point.

    Paper §3.3:
        arm_finesse: ±5% deviation from 6100 drops the design below Voyager (narrow optimum)
        beamsplitter_reflectivity: any value in [0.5, 0.8] is within 5% of optimal (broad plateau)
        homodyne_angle_deg: full 360° sweep produces only 1.4% variation
    """
    assert_environment()
    raise NotImplementedError(
        f"Hook me up to sweep {parameter_name} on {type_id}/{sol_id}."
    )


# ---------------------------------------------------------------------------
# Minimal design construction and re-optimisation
# ---------------------------------------------------------------------------

def minimal_design(type_id: str, sol_id: str) -> MinimalDesign:
    """Build the minimal essential design from a UIFO solution.

    Paper §3.1: type8/sol00 reduces to 1 laser + 0 squeezers + 2 arm cavities
    + 1 beamsplitter + 0 filter cavities ≈ 10 total components.
    """
    assert_environment()
    raise NotImplementedError(f"Hook me up to build minimal design for {type_id}/{sol_id}.")


def minimal_design_strain(
    type_id: str, sol_id: str, *, reoptimise: bool = False
) -> MinimalDesign:
    """Compute the improvement factor of the minimal design, optionally re-optimised.

    Paper §3.6:
        reoptimise=False  →  3.18× (matches original 3.12×)
        reoptimise=True   →  3.62× with BS reflectivity 0.70
    """
    assert_environment()
    raise NotImplementedError(
        f"Hook me up to compute minimal design strain for {type_id}/{sol_id} (reoptimise={reoptimise})."
    )


# ---------------------------------------------------------------------------
# Cross-solution survey
# ---------------------------------------------------------------------------

def classify_solution_family(type_id: str, sol_id: str) -> FamilyClassification:
    """Classify a UIFO solution by its dominant physical mechanism.

    Paper §3.5: 25 type8 solutions split into:
        noise_suppression family — dominant; sol00 strongest member
        signal_amplification family — secondary; up to 13.7× signal gain
    """
    assert_environment()
    raise NotImplementedError(
        f"Hook me up to classify {type_id}/{sol_id} by mechanism family."
    )
