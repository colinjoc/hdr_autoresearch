# Data Sources — gw_detectors

External tools and datasets used by this project. Per repo hygiene rules in `program.md`, none of these are committed to the repo — they are fetched on demand.

## Differometor — JAX-based differentiable interferometer simulator

- **URL**: https://github.com/artificial-scientist-lab/Differometor
- **Type**: code (Python, JAX)
- **License**: see upstream
- **Local path**: `Differometor/` (sibling of this project's root, or `$DIFFEROMETOR_DIR`)
- **Fetch**:
  ```bash
  git clone https://github.com/artificial-scientist-lab/Differometor.git
  cd Differometor && pip install -e .
  ```
- **Installation note**: requires JAX. Use the GPU build if available — the per-experiment evaluation is ~1.1 s per design on GPU vs many seconds on CPU.

## GWDetectorZoo — public dataset of 50 AI-discovered GW detector designs

- **URL**: https://github.com/artificial-scientist-lab/GWDetectorZoo
- **Type**: dataset (JSON / CSV)
- **License**: see upstream
- **Local path**: `GWDetectorZoo/` (sibling of this project's root, or `$GWDETECTORZOO_DIR`)
- **Fetch**:
  ```bash
  git clone https://github.com/artificial-scientist-lab/GWDetectorZoo.git
  ```
- **Contents**: 50 designs across 7 type families. type8 (25 solutions) is the post-merger family used in this study.

## LIGO Voyager design

- **URL (DOI)**: https://doi.org/10.1088/1361-6382/aba26f
- **Reference**: Adhikari, R.X. et al. *Class. Quantum Grav.* **37**, 165003 (2020)
- **Note**: Differometor's `voyager()` design loader implements this design. Verify against the published strain noise spectrum (3.76e-25 /√Hz at 168 Hz) before trusting downstream comparisons.

## Urania paper

- **URL (DOI)**: https://doi.org/10.1103/PhysRevX.15.021012
- **Reference**: Krenn, M., Drori, Y., and Adhikari, R.X. "Digital Discovery of Interferometric Gravitational Wave Detectors." *Phys. Rev. X* **15**, 021012 (2025).
