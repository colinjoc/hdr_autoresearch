# Matbench Benchmark -- Comprehensive Research Document

## 1. Overview

**Matbench** is a standardized benchmark for machine learning prediction of materials properties, hosted by the Materials Project. It provides 13 curated, pre-cleaned ML tasks spanning optical, thermal, electronic, thermodynamic, tensile, and elastic properties of inorganic materials. It is designed as an "ImageNet for materials science."

**Paper**: Dunn, A., Wang, Q., Ganose, A., Dopp, D., Jain, A. "Benchmarking Materials Property Prediction Methods: The Matbench Test Set and Automatminer Reference Algorithm." npj Computational Materials 6, 138 (2020). https://doi.org/10.1038/s41524-020-00406-3

**Website**: https://matbench.materialsproject.org/
**GitHub**: https://github.com/materialsproject/matbench
**PyPI**: `pip install matbench` (version 0.6 as of latest)

---

## 2. All 13 Tasks -- Complete Specification

### Composition-Only Tasks (4 tasks -- no crystal structure needed)

| Task Name | Property | Samples | Units | Metric | MAD Baseline |
|-----------|----------|---------|-------|--------|-------------|
| `matbench_steels` | Yield strength | 312 | MPa | MAE | 229.74 |
| `matbench_expt_gap` | Experimental band gap | 4,604 | eV | MAE | 1.14 |
| `matbench_expt_is_metal` | Metallic vs non-metallic | 4,921 | binary | ROC-AUC | 0.50 |
| `matbench_glass` | Glass-forming ability | 5,680 | binary | ROC-AUC | 0.71 |

### Structure-Required Tasks (9 tasks -- need crystal structure)

| Task Name | Property | Samples | Units | Metric | MAD Baseline |
|-----------|----------|---------|-------|--------|-------------|
| `matbench_jdft2d` | Exfoliation energy (2D) | 636 | meV/atom | MAE | 67.20 |
| `matbench_phonons` | Last phonon DOS peak | 1,265 | cm^-1 | MAE | 323.79 |
| `matbench_dielectric` | Refractive index | 4,764 | unitless | MAE | 0.81 |
| `matbench_log_gvrh` | Log10 shear modulus (VRH) | 10,987 | log10(GPa) | MAE | 0.29 |
| `matbench_log_kvrh` | Log10 bulk modulus (VRH) | 10,987 | log10(GPa) | MAE | 0.29 |
| `matbench_perovskites` | Formation energy (perovskites) | 18,928 | eV/unit cell | MAE | 0.57 |
| `matbench_mp_gap` | Band gap (DFT PBE) | 106,113 | eV | MAE | 1.33 |
| `matbench_mp_is_metal` | Metallic classification | 106,113 | binary | ROC-AUC | 0.43 |
| `matbench_mp_e_form` | Formation energy per atom | 132,752 | eV/atom | MAE | 1.01 |

### Data Sources
- Materials Project (MP): `mp_e_form`, `mp_gap`, `mp_is_metal`, `log_gvrh`, `log_kvrh`, `dielectric`, `phonons`
- JARVIS-DFT: `jdft2d`
- Castelli perovskites: `perovskites`
- Citrine/experimental: `expt_gap`, `expt_is_metal`
- Zhuo et al.: `glass`
- Bhole et al.: `steels`

---

## 3. Evaluation Protocol

### Nested Cross-Validation (NCV)
- **5-fold cross-validation** with fixed, deterministic splits
- **Regression**: scikit-learn `KFold(n_splits=5, shuffle=True, random_state=18012019)`
- **Classification**: scikit-learn `StratifiedKFold(n_splits=5, shuffle=True, random_state=18012019)`
- Splits are predetermined and built into the `matbench` package -- no user-defined splits
- Per fold: train on 80%, predict on 20% held-out test
- Report mean and std of metric across 5 folds
- **Primary metrics**: MAE for regression, ROC-AUC for classification
- **Additional metrics reported**: RMSE, MAPE, max_error (regression); accuracy, balanced_accuracy, F1 (classification)

### Key Rules
1. Train/validate using ONLY training data for each fold
2. No leakage: test targets are not available during training
3. All hyperparameter tuning must use inner CV or train/val splits WITHIN the training fold
4. Record predictions for all 5 folds of all 13 tasks (for complete benchmark)

---

## 4. Installation and Data Access

### Installation
```bash
pip install matbench
```

**Dependencies** (from setup.py):
- matminer >= 0.7.4
- scipy >= 1.9.0
- monty >= 2022.4.26
- scikit-learn >= 1.0.1

**Platform**: Officially supported on Unix. May work on Windows but not officially supported.
**Python**: 3.8+

### Data Download
Data is automatically downloaded via matminer when tasks are loaded. No separate download step.

### Basic Usage
```python
from matbench.bench import MatbenchBenchmark

# Load full benchmark (all 13 tasks)
mb = MatbenchBenchmark(autoload=False)

for task in mb.tasks:
    task.load()
    for fold in task.folds:
        # Get training data
        train_inputs, train_outputs = task.get_train_and_val_data(fold)

        # Train your model
        my_model.fit(train_inputs, train_outputs)

        # Get test inputs (no targets!)
        test_inputs = task.get_test_data(fold, include_target=False)

        # Predict and record
        predictions = my_model.predict(test_inputs)
        task.record(fold, predictions)

# Save results
mb.to_file("my_results.json.gz")
```

### Subset Benchmarks (Presets)
```python
# Composition-only tasks
mb = MatbenchBenchmark.from_preset("composition")

# Structure-only tasks
mb = MatbenchBenchmark.from_preset("structure")

# Regression only
mb = MatbenchBenchmark.from_preset("regression")

# Classification only
mb = MatbenchBenchmark.from_preset("classification")

# Specific tasks
mb = MatbenchBenchmark(subset=["matbench_steels", "matbench_expt_gap"])
```

### Input Data Format
- **Composition tasks**: inputs are composition strings (e.g., "Fe2O3")
- **Structure tasks**: inputs are `pymatgen.core.Structure` objects (contain full crystal structure info including lattice parameters, atomic coordinates, species)

### API Reference (MatbenchBenchmark class)
Key properties:
- `mb.tasks` -- list of MatbenchTask objects
- `mb.scores` -- nested dict of all metrics per task
- `mb.is_valid` -- bool: all folds recorded and properly formatted
- `mb.is_complete` -- bool: all 13 tasks present
- `mb.is_composition_complete` / `mb.is_structure_complete`
- `mb.matbench_<task_name>` -- direct task access

Key methods:
- `mb.load()` -- load all tasks
- `mb.validate()` -- run validation, returns error dict
- `mb.add_metadata(dict)` -- attach algorithm metadata
- `mb.to_file(path)` / `MatbenchBenchmark.from_file(path)` -- save/load
- `mb.get_info()` -- log benchmark status

---

## 5. Leaderboard Submission Process

### Required Files
Create a directory `matbench/benchmarks/matbench_v0.1_<algorithm_name>/` containing:

1. **`results.json.gz`** -- output of `mb.to_file()` (exact filename required)
2. **`info.json`** -- metadata with required keys:
   - `authors` -- name(s)
   - `algorithm` -- short name (5-15 chars)
   - `algorithm_long` -- extended description (up to 1000 words)
   - `bibtex_refs` -- citations in BibTeX format
   - `notes` -- freeform (compute resources, methodology)
   - `requirements` -- dict of software dependencies
3. **Source code** -- Jupyter notebook (.ipynb) preferred, or Python files with comments

### Submission Steps
1. Clone the matbench GitHub repository
2. Add your folder to `matbench/benchmarks/`
3. Commit and create a pull request
4. Label the PR with `new_benchmark`
5. Automated tests run; upon passing, results appear on leaderboard

---

## 6. Current Top Models and Rankings

### Overall Top Performers (across all structure tasks)

**Tier 1 -- Graph Neural Networks (structure-based, best on large datasets)**:
| Model | Type | mp_e_form MAE | mp_gap MAE | perovskites MAE | Tasks Done |
|-------|------|---------------|------------|-----------------|------------|
| coGN | GNN | 0.0170 | 0.1559 | 0.0269 | 9/13 |
| coNGN | GNN | 0.0178 | 0.1697 | 0.0290 | 9/13 |
| ALIGNN | GNN | 0.0215 | 0.1861 | 0.0288 | 9/13 |
| SchNet (kgcnn) | GNN | 0.0218 | 0.2352 | 0.0342 | 9/13 |
| DimeNet++ (kgcnn) | GNN | 0.0235 | 0.1993 | 0.0376 | 9/13 |
| MegNet (kgcnn) | GNN | 0.0252 | 0.1934 | 0.0352 | 9/13 |
| CGCNN v2019 | GNN | 0.0337 | 0.2972 | 0.0452 | 9/13 |
| DeeperGATGNN | GNN | 0.0340 | 0.1694 | 0.0288 | 9/13 |

**Tier 2 -- Feature-Based Neural Networks (handle both composition and structure)**:
| Model | Type | mp_e_form MAE | expt_gap MAE | Tasks Done |
|-------|------|---------------|-------------|------------|
| MODNet (v0.1.12) | Feed-forward NN | 0.0448 | 0.3327 | 13/13 |
| MODNet (v0.1.10) | Feed-forward NN | 0.0448 | 0.3470 | 13/13 |

**Tier 3 -- Composition-Based and Tabular Models**:
| Model | Type | expt_gap MAE | steels MAE | Tasks Done |
|-------|------|-------------|------------|------------|
| Darwin | AutoML | 0.2865 | 123.29 | varies |
| CrabNet | Attention-based | 0.3463 | 107.32 | varies |
| AMMExpress v2020 | AutoML/TPOT | 0.4161 | 97.49 | 13/13 |
| RF-SCM/Magpie | Random Forest | 0.4461 | 103.51 | 13/13 |
| TPOT-Mat | AutoML | -- | 79.95 | varies |

### Per-Task Leaderboard Highlights

**matbench_mp_e_form** (formation energy, 132k samples -- flagship task):
1. coGN: 0.0170
2. coNGN: 0.0178
3. ALIGNN: 0.0215
4. SchNet: 0.0218
5. DimeNet++: 0.0235
6. MegNet: 0.0252
7. CGCNN: 0.0337
8. DeeperGATGNN: 0.0340
9. MODNet: 0.0448
10. CrabNet: 0.0862
11. RF-SCM/Magpie: 0.1165
12. AMMExpress: 0.1726
13. Dummy: 1.0059

**matbench_expt_gap** (composition-only, 4.6k samples):
1. Darwin: 0.2865
2. Ax/SAASBO CrabNet: 0.3310
3. MODNet v0.1.12: 0.3327
4. CrabNet: 0.3463
5. AMMExpress: 0.4161
6. RF-SCM/Magpie: 0.4461
7. gptchem: 0.4544
8. Dummy: 1.1435

**matbench_steels** (composition-only, 312 samples -- smallest):
1. TPOT-Mat: 79.95
2. AutoML-Mat: 82.30
3. MODNet v0.1.12: 87.76
4. RF-Regex Steels: 90.59
5. AMMExpress: 97.49
6. RF-SCM/Magpie: 103.51
7. CrabNet: 107.32
8. Darwin: 123.29
9. Dummy: 229.74

---

## 7. Model Descriptions

### coGN (Connectivity Optimized Graph Network)
- **Type**: Graph Neural Network
- **Input**: Crystal structures (atomic positions + lattice)
- **Features**: Atomic mass, atomic radius, edge embeddings (32 distance bins), 8.0A cutoff
- **Tasks completed**: 9/13 (structure-only)
- **Strengths**: Best on large structure tasks (mp_e_form, mp_gap, perovskites)
- **Reference**: Ruff et al. (2023) "Connectivity Optimized Nested Graph Networks for Crystal Structures" (arXiv:2302.14102)
- **Dependencies**: kgcnn==3.0.0

### ALIGNN (Atomistic Line Graph Neural Network)
- **Type**: Graph Neural Network with line graph (encodes bond angles)
- **Input**: Crystal structures
- **Features**: CGCNN atom features, 8.0A cutoff, line graph for angle encoding
- **Tasks completed**: 9/13 (structure-only)
- **Strengths**: Explicitly models triplet (angle) interactions
- **Dependencies**: PyTorch, DGL, alignn package

### MODNet (Materials Optimal Descriptor Network)
- **Type**: Feed-forward neural network with feature selection
- **Input**: Both composition and structure (uses matminer featurizers)
- **Features**: All compatible matminer features + relevance-redundancy feature selection
- **Tasks completed**: 13/13 (the only top model to complete ALL tasks)
- **Hyperparameter optimization**: Nested grid search (small tasks), genetic algorithm (large tasks)
- **Strengths**: Works on composition-only AND structure tasks; best on dielectric task

### CrabNet (Compositionally Restricted Attention-Based Network)
- **Type**: Transformer/attention-based network
- **Input**: Composition only (no structure needed)
- **Tasks completed**: Varies (focus on composition tasks)
- **Strengths**: Strong on composition-only tasks
- **Note**: Ax/SAASBO variant uses Bayesian hyperparameter optimization (23 hyperparameters, 100 iterations)

### AMMExpress / Automatminer (Reference Algorithm)
- **Type**: Automated ML pipeline (AutoML)
- **Input**: Both composition and structure (via matminer featurizers)
- **Pipeline**: matminer featurization -> feature reduction (correlation + tree-based) -> TPOT AutoML
- **Tasks completed**: 13/13
- **Models evolved**: GradientBoosting, RandomForest, ExtraTrees (most common)
- **Strengths**: Fully automated, no user intervention, complete benchmark coverage
- **Config**: Express preset, 10 parallel jobs, 1440-min total TPOT time, 200 population

### RF-SCM/Magpie (Random Forest Baseline)
- **Type**: Random Forest with Magpie features + Sine Coulomb Matrix
- **Input**: Composition (Magpie stats) + Structure (Sine Coulomb Matrix)
- **Tasks completed**: 13/13
- **Strengths**: Fast, interpretable, solid baseline

### CGCNN (Crystal Graph Convolutional Neural Network)
- **Type**: Graph Neural Network
- **Input**: Crystal structures
- **Hardware**: 1x NVIDIA 1080Ti GPU + 2x Intel Xeon E5-2623 CPUs + 60GB RAM
- **Training**: 60/20/20 train/val/test per outer fold, 128-sample batches, early stopping (500 epoch patience)
- **Tasks completed**: 9/13 (structure-only)

---

## 8. Input Representations and Featurization

### For Composition-Only Tasks
**Matminer composition featurizers** (recommended):
- `ElementProperty.from_preset("magpie")` -- Magpie elemental statistics (mean, std, min, max, range, mode of elemental properties like electronegativity, atomic radius, etc.)
- `ElementProperty.from_preset("deml")` -- DEML elemental features
- `ElementProperty.from_preset("matscholar_el")` -- MatScholar learned element embeddings
- `ElementProperty.from_preset("megnet_el")` -- MEGNet learned element embeddings
- Additional featurizers: `Stoichiometry`, `BandCenter`, `ElementFraction`, `TMetalFraction`, `Meredig`, `ValenceOrbital`, `IonProperty`, `AtomicOrbitals`, `Miedema`, `YangSolidSolution`

Matminer has 44 featurization classes generating thousands of individual descriptors.

**Other composition representations**:
- CrabNet: learned element embeddings via attention mechanism
- ROOST: composition-based graph network
- gptchem: text-based (GPT-3 fine-tuning on composition strings)

### For Structure Tasks
**Graph representations** (for GNNs):
- Crystal graph: atoms = nodes, bonds within cutoff = edges
- CGCNN: atom features (one-hot element) + bond features (Gaussian expansion of distance)
- ALIGNN: crystal graph + line graph (bond-bond adjacency for angle encoding)
- coGN: optimized connectivity with distance bins
- MEGNet: crystal graph with global state vector

**Descriptor-based** (for tabular ML):
- Sine Coulomb Matrix (structure fingerprint)
- matminer structure featurizers: `DensityFeatures`, `GlobalSymmetryFeatures`, `Dimensionality`, `RadialDistributionFunction`, `CoulombMatrix`, `SineCoulombMatrix`, `OrbitalFieldMatrix`, `BondFractions`, `StructuralHeterogeneity`, `ChemicalOrdering`, `MaximumPackingEfficiency`
- Voronoi-based features: coordination numbers, local environments

### Recommended Approach by Task Type
| Task Type | Best Representations | Best Models |
|-----------|---------------------|-------------|
| Composition-only, small (<1k) | Magpie/matminer features | RF, XGBoost, TPOT |
| Composition-only, medium (1k-10k) | Magpie + matminer features | MODNet, CrabNet, XGBoost |
| Structure, small (<1k) | Graph or matminer structure features | GNNs or RF+descriptors |
| Structure, medium (1k-50k) | Crystal graph | ALIGNN, coGN, MODNet |
| Structure, large (>50k) | Crystal graph | coGN, ALIGNN, SchNet |

---

## 9. Which Tasks Suit Which Model Types

### Best for Tabular ML (XGBoost, RF, GBM)
1. **matbench_steels** (312 samples, composition) -- TPOT-Mat (tree-based) is #1
2. **matbench_expt_gap** (4,604 samples, composition) -- tabular models competitive
3. **matbench_glass** (5,680 samples, composition) -- classification, tabular works well
4. **matbench_expt_is_metal** (4,921 samples, composition) -- classification, tabular works well
5. **matbench_log_gvrh** / **matbench_log_kvrh** (10,987 samples) -- RF competitive with GNNs

**Key finding from paper**: Automatminer (tree-based AutoML) achieved best performance on 8/13 tasks in the original benchmark. GNNs showed advantages only with larger datasets (>10,000 samples).

### Best for Graph Neural Networks
1. **matbench_mp_e_form** (132k, structure) -- GNNs dominate (coGN 0.017 vs RF 0.117)
2. **matbench_mp_gap** (106k, structure) -- GNNs dominate
3. **matbench_mp_is_metal** (106k, structure) -- GNNs have advantage
4. **matbench_perovskites** (18.9k, structure) -- GNNs clearly better
5. **matbench_phonons** (1.3k, structure) -- GNNs better despite small size (structural info matters)

### Mixed / Either Approach
1. **matbench_dielectric** (4.8k, structure) -- MODNet (feature-based) beats most GNNs
2. **matbench_jdft2d** (636, structure) -- small dataset, high variance, no clear winner
3. **matbench_log_gvrh/kvrh** (11k, structure) -- feature-based and GNN both competitive

---

## 10. Computational Requirements

### CPU-Only Models
- **Random Forest / XGBoost / tabular models**: Run entirely on CPU
- **AMMExpress/Automatminer**: CPU-only (TPOT evolves sklearn pipelines)
- **MODNet**: Can run on CPU (feed-forward NN, not huge)
- **Estimated time**: Full 13-task benchmark with RF+Magpie features: ~1-4 hours on modern CPU
- **Estimated time**: Automatminer (full benchmark): hours to days (TPOT has time limits per pipeline)

### GPU Models
- **CGCNN**: 1x NVIDIA 1080Ti (documented in benchmark submission)
- **ALIGNN**: GPU recommended (PyTorch + DGL)
- **coGN**: GPU required for practical training times (kgcnn/TensorFlow)
- **SchNet, DimeNet++, MegNet**: GPU recommended (kgcnn implementations)
- **CrabNet**: GPU recommended ("can take several days to run" with Bayesian HP optimization)

### Practical Estimates
- **Composition-only tasks with XGBoost/RF** (4 tasks): ~30 minutes to 2 hours total on CPU
- **Full 13 tasks with GNN** (5 folds each): ~1-7 days on single GPU depending on model
- **Full 13 tasks with MODNet**: ~4-24 hours (CPU or GPU)
- **Single large task (mp_e_form, 132k) with GNN**: ~2-12 hours per fold on GPU
- **Single small task (steels, 312) with RF**: ~seconds

### Can It Run on CPU?
**Yes** for tabular models (RF, XGBoost, MODNet). For GNNs, CPU is technically possible but impractically slow for the large tasks (mp_e_form with 132k samples, mp_gap with 106k samples). A single GPU is sufficient for all models.

---

## 11. Baseline Models in the Paper

The original paper tested 4 baseline/reference algorithms:

1. **Dummy**: Predicts mean (regression) or random proportional label (classification). This is the MAD baseline.
2. **RF-SCM/Magpie**: Random Forest using Magpie elemental statistics (composition) + Sine Coulomb Matrix (structure). Solid baseline for all tasks.
3. **CGCNN**: Crystal Graph Convolutional Neural Network (Xie & Grossman, 2018). Graph-based baseline for structure tasks.
4. **MEGNet**: Graph Networks for Molecules and Crystals (Chen et al., 2019). Another graph-based baseline.
5. **Automatminer (AMMExpress)**: The reference AutoML algorithm. Uses matminer featurization + TPOT pipeline evolution.

---

## 12. Matbench Discovery (Separate Benchmark)

**Matbench Discovery** is a DIFFERENT benchmark from Matbench v0.1, focused on crystal stability prediction for materials discovery.

- **Website**: https://matbench-discovery.materialsproject.org/
- **Paper**: Riebesell et al. "Matbench Discovery -- A framework to evaluate machine learning crystal stability predictions" (Nature Machine Intelligence, 2025)
- **Install**: `pip install matbench-discovery`

### Key Differences from Matbench v0.1
| Aspect | Matbench v0.1 | Matbench Discovery |
|--------|---------------|-------------------|
| Focus | Property prediction (13 tasks) | Crystal stability prediction |
| Tasks | 13 diverse property predictions | Stability on convex hull |
| Training set | Per-task, built-in splits | Materials Project (~150k) |
| Test set | 5-fold CV within each task | WBM dataset (~257k structures) |
| Metric | MAE / ROC-AUC per task | F1, DAF, precision, recall |
| Input | Composition or structure | Unrelaxed crystal structures |
| Top models | coGN, MODNet, ALIGNN | MACE, CHGNet, M3GNet (UIPs) |

### Matbench Discovery Top Models (by F1)
1. EquiformerV2 + DeNS
2. Orb
3. SevenNet
4. MACE
5. CHGNet
6. M3GNet
7. ALIGNN
8. MEGNet
9. CGCNN

Universal interatomic potentials (MACE, CHGNet, M3GNet) dominate because they learn from forces and stresses, not just energies.

---

## 13. Key Libraries and Tools

### Core
- `matbench` -- benchmark framework, data loading, evaluation
- `matminer` -- featurization library (composition and structure descriptors)
- `pymatgen` -- materials science Python library (Structure objects, Composition parsing)

### Featurization
- `matminer` -- 44 featurizer classes, thousands of descriptors
- `CBFV` -- Composition-Based Feature Vectors
- `xenonpy` -- alternative elemental feature library

### Models
- `automatminer` -- AutoML pipeline (matminer + TPOT)
- `modnet` -- MODNet implementation (`pip install modnet`)
- `alignn` -- ALIGNN implementation (JARVIS tools)
- `kgcnn` -- Keras Graph CNN (implementations of SchNet, DimeNet++, MegNet, coGN, coNGN)
- `cgcnn` -- Original CGCNN implementation
- `crabnet` -- CrabNet implementation

### Useful Presets for Quick Start
```python
# Minimal featurization (fast, composition-only)
from matminer.featurizers.conversions import StrToComposition
from matminer.featurizers.composition import ElementProperty
featurizer = ElementProperty.from_preset("magpie")
# Generates ~132 features from composition

# Comprehensive featurization (slow but thorough)
# Use automatminer's "express" preset which applies many featurizers
from automatminer import MatPipe
pipe = MatPipe.from_preset("express")
```

---

## 14. Quick Start Code -- Complete Example

```python
from matbench.bench import MatbenchBenchmark
from matminer.featurizers.conversions import StrToComposition
from matminer.featurizers.composition import ElementProperty
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.impute import SimpleImputer
import pandas as pd
import numpy as np

# Load composition-only tasks
mb = MatbenchBenchmark.from_preset("composition", autoload=False)

for task in mb.tasks:
    task.load()
    is_classification = task.metadata["task_type"] == "classification"

    for fold in task.folds:
        train_inputs, train_outputs = task.get_train_and_val_data(fold)
        test_inputs = task.get_test_data(fold, include_target=False)

        # Featurize compositions
        featurizer = ElementProperty.from_preset("magpie")

        # Train features
        train_df = pd.DataFrame({"composition": train_inputs})
        train_df = StrToComposition().featurize_dataframe(
            train_df, "composition"
        )
        train_features = featurizer.featurize_dataframe(
            train_df, col_id="composition_obj"
        )
        X_train = train_features.select_dtypes(include=[np.number])

        # Test features (same pipeline)
        test_df = pd.DataFrame({"composition": test_inputs})
        test_df = StrToComposition().featurize_dataframe(
            test_df, "composition"
        )
        test_features = featurizer.featurize_dataframe(
            test_df, col_id="composition_obj"
        )
        X_test = test_features.select_dtypes(include=[np.number])

        # Handle NaN
        imputer = SimpleImputer()
        X_train = imputer.fit_transform(X_train)
        X_test = imputer.transform(X_test)

        # Train model
        if is_classification:
            model = RandomForestClassifier(n_estimators=500)
        else:
            model = RandomForestRegressor(n_estimators=500)

        model.fit(X_train, train_outputs)
        predictions = model.predict(X_test)

        # For classification, matbench expects boolean predictions
        if is_classification:
            predictions = predictions.astype(bool)

        task.record(fold, predictions)

# Save
mb.to_file("rf_magpie_composition.json.gz")

# Check scores
for task in mb.tasks:
    print(f"{task.dataset_name}: {task.scores}")
```

---

## 15. Strategy Recommendations for Autoresearch

### Phase 1: Start with Composition-Only Tasks
1. Only 4 tasks, all runnable on CPU
2. Use Magpie features + XGBoost/RF as baseline (~30 min)
3. Compete with MODNet, CrabNet, RF-SCM/Magpie baselines
4. Target scores: steels MAE < 90, expt_gap MAE < 0.35

### Phase 2: Add Structure Tasks with Feature-Based Approach
1. Use matminer structure featurizers (no GPU needed)
2. MODNet-style: comprehensive matminer features + feature selection + NN/XGBoost
3. This can complete all 13 tasks on CPU
4. Target: beat RF-SCM/Magpie on all tasks

### Phase 3: Graph Neural Networks (GPU)
1. Use ALIGNN or coGN for structure tasks
2. Requires GPU; single GPU sufficient
3. Target: top-5 on large tasks (mp_e_form, mp_gap)

### Key Insights for Autoresearch
- **Composition tasks are the low-hanging fruit** -- tabular ML is competitive or best
- **Structure tasks >10k samples** -- GNNs clearly dominate (6-10x better than tabular)
- **Small structure tasks (<5k)** -- feature-based approaches can match GNNs
- **MODNet is the only model completing all 13 tasks in the top tier** -- worth studying
- **Feature engineering matters most** for composition tasks (Magpie features are the standard)
- **matbench_steels (312 samples)** is the hardest task -- small data, tabular approaches dominate
- **matbench_jdft2d (636 samples)** has the highest variance across folds
- **The 3 MP tasks (mp_e_form, mp_gap, mp_is_metal)** are the largest and most well-studied

---

## 16. References

1. Dunn, A., Wang, Q., Ganose, A., Dopp, D., Jain, A. npj Computational Materials 6, 138 (2020). https://doi.org/10.1038/s41524-020-00406-3
2. Ruff, R. et al. "Connectivity Optimized Nested Graph Networks for Crystal Structures" (2023). arXiv:2302.14102
3. De Breuck, P. et al. "Robust model benchmarking and bias-imbalance in data-driven materials science" npj Computational Materials (2021) -- MODNet
4. Xie, T. & Grossman, J.C. "Crystal Graph Convolutional Neural Networks" PRL 120, 145301 (2018) -- CGCNN
5. Chen, C. et al. "Graph Networks as a Universal ML Framework for Molecules and Crystals" Chemistry of Materials (2019) -- MEGNet
6. Choudhary, K. & DeCost, B. "Atomistic Line Graph Neural Network" npj Computational Materials (2021) -- ALIGNN
7. Wang, A.Y. et al. "Compositionally restricted attention-based network" npj Computational Materials (2021) -- CrabNet
8. Riebesell, J. et al. "Matbench Discovery" Nature Machine Intelligence (2025) -- Matbench Discovery
