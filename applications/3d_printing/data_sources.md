# External Data Sources — 3D Printing (Fused Deposition Modelling) Parameter Optimisation

## Kaggle 3D Printer Dataset (primary dataset)

- **Name**: 3D Printer Dataset for Mechanical Engineers
- **Original URL**: https://www.kaggle.com/datasets/afumetto/3dprinter
- **Mirror (used in this session)**: https://raw.githubusercontent.com/SimchaGD/AIVE/f91e3ddf136c712d47893e8ead9750998d3676a3/3dprinter/data.csv
- **Size**: 50 rows, 12 columns, approximately 2 kilobytes
- **Checksum (SHA256)**: computed on the local file after download; see the local path below
- **Licence**: open (Kaggle community dataset, publicly redistributable)
- **Local path**: `data/3d_printing.csv`
- **Field separator**: semicolon (`;`)
- **Download command**:
  ```
  curl -sL "https://raw.githubusercontent.com/SimchaGD/AIVE/f91e3ddf136c712d47893e8ead9750998d3676a3/3dprinter/data.csv" -o data/3d_printing.csv
  ```
- **Columns**:
  - `layer_height` — layer thickness in millimetres (5 unique values: 0.02 – 0.20)
  - `wall_thickness` — number of perimeter / wall loops, integer 1 – 10
  - `infill_density` — infill percentage 10 – 90
  - `infill_pattern` — 0 = grid, 1 = honeycomb
  - `nozzle_temperature` — extruder temperature in degrees Celsius, 200 – 250
  - `bed_temperature` — build-plate temperature in degrees Celsius, 60 – 80
  - `print_speed` — linear feed rate in millimetres per second, 40 / 60 / 120
  - `material` — 0 = Acrylonitrile Butadiene Styrene (ABS), 1 = Poly-Lactic Acid (PLA)
  - `fan_speed` — part-cooling-fan percentage, 0 / 25 / 50 / 75 / 100
  - `roughness` — surface roughness Ra in micrometres (target for other tasks)
  - `tension_strength` — ultimate tensile strength in megapascals (the target used in this study)
  - `elongation` — elongation at break, percentage
- **Machine**: Ultimaker S5
- **Test specimen**: ASTM D638 Type I tensile bar printed in the XY orientation

## Why this dataset

The Kaggle 3D Printer Dataset is the most-cited tabular benchmark in the ML-for-FDM literature (see `papers.csv` entries [102], [11], [10], [15], [16]). It is small (N = 50) but clean, covers both of the dominant commodity thermoplastics (PLA and ABS), exercises 9 printable parameters, and reports tensile strength as a well-defined target. This is the canonical reference for studies that compare model families on FDM parameter-to-strength prediction.

## Not used in this study (but noted in the lit review)

- **APMonitor Additive Manufacturing Dataset** — 116 rows, PLA + ABS. Less standard columns; used as a robustness cross-check in the Phase-B discussion.
- **FDM-Bench (arXiv 2412.09819)** — G-code level dataset with injected anomalies. Oriented toward defect classification, not tabular parameter-to-strength regression, so out of scope for Phase A.
- **Nature Communications 1.2M image dataset** — Image-based defect detection; out of scope.
