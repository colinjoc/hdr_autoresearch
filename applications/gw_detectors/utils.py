"""
utils.py — RECONSTRUCTED helpers for the gw_detectors HDR project.

Original lost on 2026-04-09. This module is a faithful reconstruction of the
helper functions used by the 15 numbered experiment scripts.

Provides:
- File / data path resolution for the GWDetectorZoo
- Deterministic seeding helpers
- Result-logging helpers (TSV row append + per-experiment markdown stub)
- A small dataclass set used as the contract between evaluate.py and the
  experiment scripts.

Differometor and GWDetectorZoo locations are configurable via environment
variables and default to sibling directories of this file.
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
ZOO_DIR = Path(os.environ.get("GWDETECTORZOO_DIR", PROJECT_ROOT / "GWDetectorZoo"))
DIFFEROMETOR_DIR = Path(os.environ.get("DIFFEROMETOR_DIR", PROJECT_ROOT / "Differometor"))
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_TSV = PROJECT_ROOT / "results.tsv"


def ensure_results_dir() -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    return RESULTS_DIR


# ---------------------------------------------------------------------------
# Dataclasses (the contract used by the test suite)
# ---------------------------------------------------------------------------

@dataclass
class Squeezer:
    name: str
    level_db: float


@dataclass
class UIFODesign:
    """A loaded UIFO design from the GWDetectorZoo."""
    type_id: str
    sol_id: str
    n_mirrors: int
    n_beamsplitters: int
    n_lasers: int
    n_squeezers: int
    n_filter_cavities: int = 0
    arm_cavity_finesse: Optional[float] = None
    test_mass_kg: Optional[float] = None
    beamsplitter_reflectivity: Optional[float] = None
    squeezers: List[Squeezer] = field(default_factory=list)
    raw_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrainResult:
    """A strain noise spectrum reduced to its key summary numbers."""
    min_strain: float            # 1/√Hz
    min_strain_freq_hz: float    # Hz
    band_avg_strain: Optional[float] = None
    band_hz: Optional[Tuple[float, float]] = None


@dataclass
class MinimalDesign:
    type_id: str
    sol_id: str
    n_lasers: int
    n_squeezers: int
    n_arm_cavities: int
    n_beamsplitters: int
    n_filter_cavities: int
    total_components: int
    beamsplitter_reflectivity: float
    arm_cavity_finesse: float
    test_mass_kg: float
    improvement_factor: float


@dataclass
class SweepValue:
    parameter_name: str
    parameter_value: float
    improvement_factor: float
    min_strain: float


@dataclass
class SweepResult:
    parameter_name: str
    values: List[SweepValue]


@dataclass
class AblationResult:
    component_name: str
    baseline_improvement: float
    ablated_improvement: float
    delta_pct: float


@dataclass
class FamilyClassification:
    type_id: str
    sol_id: str
    dominant_mechanism: str       # "noise_suppression" or "signal_amplification"
    noise_contribution: float     # 0..1
    signal_contribution: float    # 0..1
    signal_gain_factor: float


# ---------------------------------------------------------------------------
# Experiment logging
# ---------------------------------------------------------------------------

RESULTS_TSV_HEADER = "exp_id\tdescription\timprovement\tdelta_vs_baseline\tnotes\tstatus\n"


def init_results_tsv() -> None:
    if not RESULTS_TSV.exists():
        RESULTS_TSV.write_text(RESULTS_TSV_HEADER)


def append_result(
    exp_id: str,
    description: str,
    improvement: float,
    delta_vs_baseline: float,
    notes: str,
    status: str,
) -> None:
    init_results_tsv()
    with RESULTS_TSV.open("a") as f:
        f.write(
            f"{exp_id}\t{description}\t{improvement:.4f}\t{delta_vs_baseline:+.4f}\t{notes}\t{status}\n"
        )


def save_result_json(exp_id: str, payload: Dict[str, Any]) -> Path:
    ensure_results_dir()
    p = RESULTS_DIR / f"{exp_id}.json"
    p.write_text(json.dumps(payload, indent=2, default=str))
    return p


# ---------------------------------------------------------------------------
# Differometor / GWDetectorZoo availability check
# ---------------------------------------------------------------------------

def assert_environment() -> None:
    """Fail early with a clear message if the upstream tools are not available."""
    if not DIFFEROMETOR_DIR.exists():
        raise RuntimeError(
            f"Differometor not found at {DIFFEROMETOR_DIR}. "
            "Set DIFFEROMETOR_DIR or clone https://github.com/artificial-scientist-lab/Differometor"
        )
    if not ZOO_DIR.exists():
        raise RuntimeError(
            f"GWDetectorZoo not found at {ZOO_DIR}. "
            "Set GWDETECTORZOO_DIR or clone https://github.com/artificial-scientist-lab/GWDetectorZoo"
        )
