# Observations

Signal ideas, data gaps, and surprises discovered during experiments.

## Data Gaps

- **AR evolution data**: The `AR_flare_ml_23_24_evol.csv` dataset includes previous-day AR state and whether it flared. This would be a strong feature but we're currently using the simpler dataset.
- **Magnetic field measurements**: SDO/HMI provides photospheric magnetic field data (SHARP parameters). These are far more predictive than SRS categorical data but not in this dataset.
- **X-ray background level**: The current GOES X-ray background indicates overall solar activity level. Not available in this dataset.
- **CME association**: Whether the AR previously produced a CME may indicate eruptive potential. Available in `final_cme_list_2010_2018.csv` but not linked to this dataset.

## Initial Observations

- Class imbalance (81/19) is moderate — similar to disruption project (~4:1 ratio). Scale_pos_weight tuning was transformative there.
- McIntosh classification has 63 classes — high cardinality. Decomposing into 3 sub-components reduces this to 7 + 6 + 4 classes.
- AREA = 0 appears in the data (smallest ARs). Need to handle log(0) carefully.
- The test period (last 20%) corresponds roughly to the declining phase of solar cycle 24 (2014-2018), which has fewer flares than the peak. This tests generalization across cycle phases.
