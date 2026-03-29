"""
Prepare data from raw source files into the format expected by evaluate.py.

This script is run ONCE during setup. It is NOT modified during HDR experiments.

Adapt this template to your specific data format. The output should be a pickle
file containing a dictionary of samples, each with:
  - 'data': numpy array of features (n_timesteps, n_features) for time-series,
            or (n_features,) for tabular
  - 'label': integer class label (0/1 for binary, 0..K for multiclass)
  - 'group': string identifier for the sample's group/source/domain
             (used for train/test splitting and cross-domain evaluation)

Steps:
1. Load raw data files
2. Extract common features across all groups/sources
3. Handle missing values (forward-fill, interpolation, imputation)
4. Resample if needed (align different sources to common resolution)
5. Package per-sample as {idx: {'data': array, 'label': int, 'group': str}}
6. Save as pickle
"""

import numpy as np
import pickle
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_FILE = DATA_DIR / "dataset.pickle"

# ============================================================================
# CONFIGURE: Define your features and data sources
# ============================================================================

# List of feature names in the order they appear in the data array
FEATURE_NAMES = [
    # "feature_1",
    # "feature_2",
    # ...
]

# Data sources / groups (e.g., different experimental sites, domains, conditions)
GROUPS = {
    # "group_a": {
    #     "file": "group_a_data.csv",  # or .mat, .parquet, .h5, etc.
    #     "sample_rate": 1.0,          # native sample rate
    #     "target_rate": 1.0,          # target sample rate (for resampling)
    # },
    # "group_b": { ... },
}


# ============================================================================
# DATA LOADING: Implement for your specific file format
# ============================================================================

def load_group_data(group_name: str) -> dict:
    """Load raw data for one group/source.

    Returns dict with keys:
        'sample_ids': array of sample identifiers
        'features': (n_total_timesteps, n_features) array
        'labels': per-sample labels (however your data encodes them)
        ... any other metadata needed for sample extraction
    """
    cfg = GROUPS[group_name]
    filepath = RAW_DIR / cfg["file"]
    print(f"Loading {group_name} from {filepath}...")

    # ---- IMPLEMENT: Load your specific file format ----
    # Examples:
    #   CSV:   data = pd.read_csv(filepath)
    #   MAT:   data = scipy.io.loadmat(str(filepath))
    #   HDF5:  data = h5py.File(filepath, 'r')
    #   Parquet: data = pd.read_parquet(filepath)

    raise NotImplementedError("Implement load_group_data for your data format")


# ============================================================================
# SAMPLE PROCESSING: Adapt to your data structure
# ============================================================================

def process_sample(features: np.ndarray, resample_factor: int = 1) -> np.ndarray:
    """Process a single sample: handle missing values, resample if needed.

    Args:
        features: (n_timesteps, n_features) raw feature array
        resample_factor: integer factor for upsampling (1 = no change)

    Returns:
        Processed feature array as float32
    """
    data = features.copy()

    # Forward-fill NaN values within the sample
    for col in range(data.shape[1]):
        mask = np.isnan(data[:, col])
        if mask.any():
            idx = np.where(~mask, np.arange(len(mask)), 0)
            np.maximum.accumulate(idx, out=idx)
            data[:, col] = data[idx, col]
            # Backfill leading NaNs with first valid value
            first_valid = np.argmax(~mask)
            data[:first_valid, col] = data[first_valid, col]

    # Resample via forward-fill (repeat each timestep)
    if resample_factor > 1:
        data = np.repeat(data, resample_factor, axis=0)

    return data.astype(np.float32)


# ============================================================================
# MAIN: Orchestrate the data preparation
# ============================================================================

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    dataset = {}
    idx = 0
    stats = {"total": 0, "positive": 0}

    for group_name in GROUPS:
        group_data = load_group_data(group_name)
        group_positive = 0

        # ---- IMPLEMENT: Extract individual samples from group_data ----
        # This loop structure assumes your data contains multiple samples
        # (e.g., multiple experimental runs, patients, time windows).
        # Adapt the iteration and label extraction to your data structure.

        # for sample_id in group_data["sample_ids"]:
        #     features = ...  # extract this sample's features
        #     label = ...     # extract this sample's label (0 or 1)
        #
        #     data = process_sample(features, GROUPS[group_name].get("upsample", 1))
        #
        #     # Skip very short samples if applicable
        #     if len(data) < MIN_LENGTH:
        #         continue
        #
        #     dataset[idx] = {
        #         "data": data,
        #         "label": label,
        #         "group": group_name,
        #     }
        #     idx += 1
        #     stats["total"] += 1
        #     if label == 1:
        #         stats["positive"] += 1
        #         group_positive += 1

        raise NotImplementedError("Implement sample extraction loop")

    print(f"\nTotal: {stats['total']} samples, {stats['positive']} positive "
          f"({100 * stats['positive'] / stats['total']:.1f}%)")

    # Save
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(dataset, f)

    fsize = os.path.getsize(OUTPUT_FILE) / (1024 ** 2)
    print(f"Saved to {OUTPUT_FILE} ({fsize:.1f} MB)")

    # Print feature order for reference
    print(f"\nFeature order (0-indexed):")
    for i, name in enumerate(FEATURE_NAMES):
        print(f"  {i}: {name}")


if __name__ == "__main__":
    main()
