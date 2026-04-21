"""
Willow 105Q data loader.

File structure per Zenodo 13273331:
  google_105Q_surface_code_d3_d5_d7/d{distance}_at_q{x_y}/{X|Z}/r{rounds}/
    detection_events.b8        # shots × num_detectors, bit-packed
    obs_flips_actual.b8        # shots × num_observables, bit-packed (ground truth)
    measurements.b8            # shots × num_measurements, bit-packed
    circuit_ideal.stim         # Stim circuit (noiseless)
    circuit_noisy_si1000.stim  # Stim circuit with Google SI1000 noise
    metadata.json              # experiment metadata
    decoding_results/
      {decoder}_with_{prior}/
        obs_flips_predicted.b8 # decoder prediction
        error_model.dem        # reference DEM used by that decoder
"""

from __future__ import annotations
import json
import zipfile
from pathlib import Path

import numpy as np
import stim


HERE = Path(__file__).parent
ZIP_PATH = HERE / "data" / "raw" / "google_105Q_surface_code_d3_d5_d7.zip"
EXTRACT_ROOT = HERE / "data" / "extracted"


def list_experiments(distance: int = 5) -> list[str]:
    """Return list of experiment directory names matching a given distance."""
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()
    prefix = f"google_105Q_surface_code_d3_d5_d7/d{distance}_at_"
    # Unique experiment roots: {prefix}q*/X|Z/r*/
    exps = set()
    for n in names:
        if n.startswith(prefix):
            parts = n.split("/")
            if len(parts) >= 5:
                exps.add("/".join(parts[:5]))
    return sorted(exps)


def extract_experiment(exp_path: str) -> Path:
    """Extract a single experiment directory from the zip. Returns local path."""
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = [n for n in z.namelist() if n.startswith(exp_path)]
        for n in names:
            z.extract(n, EXTRACT_ROOT)
    return EXTRACT_ROOT / exp_path


def load_experiment(exp_dir: Path, decoder: str = "correlated_matching_decoder_with_si1000_prior"):
    """Load a single Willow experiment. Returns a dict with the key arrays."""
    meta = json.loads((exp_dir / "metadata.json").read_text())

    # Load the noisy SI1000 circuit and compile its sampler to get shapes
    circuit = stim.Circuit.from_file(exp_dir / "circuit_noisy_si1000.stim")
    num_dets = circuit.num_detectors
    num_obs = circuit.num_observables

    # Read detection events (bit-packed, shots × num_detectors)
    det_events = stim.read_shot_data_file(
        path=str(exp_dir / "detection_events.b8"),
        format="b8",
        num_detectors=num_dets,
        num_observables=0,
    ).astype(np.uint8)

    obs_actual = stim.read_shot_data_file(
        path=str(exp_dir / "obs_flips_actual.b8"),
        format="b8",
        num_detectors=0,
        num_observables=num_obs,
    ).astype(np.uint8)

    # Reference DEM (from the chosen decoder's directory)
    dem_path = exp_dir / "decoding_results" / decoder / "error_model.dem"
    dem = stim.DetectorErrorModel.from_file(dem_path)

    # Reference decoder predictions
    pred_path = exp_dir / "decoding_results" / decoder / "obs_flips_predicted.b8"
    obs_predicted = stim.read_shot_data_file(
        path=str(pred_path),
        format="b8",
        num_detectors=0,
        num_observables=num_obs,
    ).astype(np.uint8)

    return {
        "meta": meta,
        "circuit": circuit,
        "dem": dem,
        "det_events": det_events,
        "obs_actual": obs_actual,
        "obs_predicted": obs_predicted,
        "num_detectors": num_dets,
        "num_observables": num_obs,
        "num_shots": det_events.shape[0],
        "decoder": decoder,
    }


def dem_to_pcm(dem: stim.DetectorErrorModel) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    num_detectors = dem.num_detectors
    num_observables = dem.num_observables
    errors = []
    for instr in dem.flattened():
        if instr.type == "error":
            p = instr.args_copy()[0]
            targets = instr.targets_copy()
            det_bits = [t.val for t in targets if t.is_relative_detector_id()]
            obs_bits = [t.val for t in targets if t.is_logical_observable_id()]
            errors.append((p, det_bits, obs_bits))
    H = np.zeros((num_detectors, len(errors)), dtype=np.uint8)
    O = np.zeros((num_observables, len(errors)), dtype=np.uint8)
    rates = np.zeros(len(errors))
    for j, (p, ds, os_) in enumerate(errors):
        rates[j] = p
        for d in ds: H[d, j] = 1
        for o in os_: O[o, j] = 1
    return H, O, rates


if __name__ == "__main__":
    print("[willow_loader] smoke test", flush=True)
    d5_exps = list_experiments(distance=5)
    print(f"  d=5 experiments: {len(d5_exps)}", flush=True)
    for e in d5_exps[:3]:
        print(f"    {e}", flush=True)

    if d5_exps:
        target = d5_exps[0]
        print(f"\n  extracting {target}...", flush=True)
        p = extract_experiment(target)
        print(f"  extracted to {p}", flush=True)
        data = load_experiment(p)
        print(f"  circuit: {data['num_detectors']} detectors, {data['num_observables']} observables", flush=True)
        print(f"  shots: {data['num_shots']}", flush=True)
        print(f"  det_events shape: {data['det_events'].shape}", flush=True)
        print(f"  obs_actual shape: {data['obs_actual'].shape}", flush=True)
        print(f"  LER (reference decoder): {np.mean(data['obs_actual'] != data['obs_predicted']):.4f}", flush=True)
        H, O, rates = dem_to_pcm(data["dem"])
        print(f"  H shape: {H.shape}", flush=True)
        print(f"  rates mean: {rates.mean():.4e}", flush=True)
        print(f"  metadata: {list(data['meta'].keys())}", flush=True)
