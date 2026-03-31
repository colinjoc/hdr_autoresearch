# Autoresearch: [YOUR SCIENTIFIC QUESTION] -- HDR

**Local**: `/path/to/your/project/`
**Venv**: `source /path/to/venv/bin/activate`

## Objective

Maximise **[PRIMARY METRIC]** and **[SECONDARY METRIC]** on [YOUR BENCHMARK / DATASET] by [PREDICTION/CLASSIFICATION/REGRESSION TASK] using Hypothesis-Driven Research (HDR).

**Primary metric: [METRIC]** (e.g., AUC, RMSE, F1)
**Secondary metric: [METRIC]** (e.g., F2-score, MAE, specificity)
**Stretch target**: [OPERATIONAL REQUIREMENT] (e.g., 95% TPR at 5% FPR)

**Benchmark**: [BENCHMARK NAME AND SOURCE]
- [Dataset size and structure]
- [Number of input features per sample]
- [Number of evaluation tasks / splits]
- Current best published result: [MODEL (METRIC VALUE)]

---

## Phase 0: Literature Review

Before any experiments, conduct a comprehensive literature review to seed the research queue with domain-informed hypotheses. This phase produces:

1. **`literature_review.md`** -- Structured review organized by theme
2. **`papers.csv`** -- Tracking spreadsheet for all reviewed papers and books
3. **`feature_candidates.md`** -- Domain quantities mapped to computable proxies from available features
4. **`research_queue.md`** -- Initial hypotheses seeded from literature findings
5. **`knowledge_base.md`** -- Pre-populated with established results

### Literature Review Themes

Structure the review around themes relevant to your scientific domain. Example themes:

1. **Domain Fundamentals** -- Core theory, governing equations, established physical/biological/chemical laws. Key textbooks and seminal papers.
2. **Phenomena of Interest** -- The specific process you are predicting/classifying. Known mechanisms, pathways, timescales, observable precursors.
3. **Derived/Candidate Features from Theory** -- Quantities suggested by domain theory but not directly in your raw features. The bridge from theory to computable proxies is the most valuable output of the literature review.
4. **ML for This Problem** -- Existing models, features used, results. What has been tried and what gaps remain.
5. **Feature Engineering Techniques** -- Domain-specific transformations, time-series features (if applicable), interaction terms, normalization strategies.
6. **Transfer / Generalization** -- If your problem involves multiple domains, sites, or conditions: what enables or prevents generalization across them.
7. **Tree/Tabular Methods on Similar Problems** -- XGBoost/GBM/tabular-ML applied to analogous scientific domains.

### Feature Engineering Guidance

The literature review should specifically identify **derived features worth computing**. Based on empirical results, features fall into three categories:

**High-value features (almost always help):**
- Non-dimensional groups from domain theory (ratios of competing scales, characteristic numbers)
- Condition/regime indicators (features that encode WHICH configuration or operating regime the data comes from)
- Physically meaningful ratios/products that encode domain knowledge not obvious from raw inputs alone
- Alignment/angle features (cosine of angle between two vector fields)

**Low-value features (network can learn these itself):**
- Simple products of existing inputs (the network learns these interactions on its own)
- Magnitude of a vector whose components are already inputs
- Monotonic transforms of existing features (log(x) when x is already an input)

**Features that often hurt:**
- Raw component features when a derived scalar already captures the information (e.g., adding vector components when magnitude + alignment are already features)
- High-cardinality features that fragment the data
- Features that vary across configs in ways that break generalization (per-config statistics)

### Literature Storage

All papers and books are stored locally for future reference:
```
literature/
  papers/           # PDFs of research papers
  books/            # PDFs of textbooks (where freely available)
```

Download papers from arXiv, open-access journals, and institutional repositories. For paywalled content, note the citation and key findings in the review without storing the PDF.

### Paper Tracking (`papers.csv`)

Columns: `id, title, authors, year, type, domain, subcategory, method, features_discussed, key_finding, hypothesis_generated, relevance`

- **type**: book / paper / thesis / review
- **domain**: [your domain categories]
- **relevance**: 1-5 (5 = directly applicable to your task)

### Review -> HDR Pipeline

The literature review feeds directly into the HDR loop:
- Each paper reviewed should generate potential **hypotheses** for research_queue.md
- Known results populate **knowledge_base.md** (so we don't repeat published work)
- Domain theory generates **feature_candidates.md** (the key bridge document)
- Identified gaps become **observations.md** entries

---

## Phase 0.5: Baseline Audit

Before running any experiments, **audit the baseline code and understand the scoring**. This phase catches free wins and sets priorities for the entire project.

### 1. Verify the Baseline Code

Read every line of the starter code / evaluation harness. Look for:
- **Bugs**: off-by-one errors, missing dimensions, wrong indices, mismatched slicing between training loss and evaluation metric. Fixing bugs is always the highest-ROI experiment.
- **Suboptimal defaults**: data subsampling that throws away most of the data, fixed seeds, commented-out features, hardcoded paths.
- **Missing features**: the baseline typically uses a minimal feature set. Note all available inputs that aren't used.

Record all findings in `observations.md`.

### 2. Score Decomposition

If the scoring metric is composite (e.g., `score = w1 * accuracy + w2 * speed`), **decompose it** to understand where improvement effort should go:

```
Score = Component_A (X% of total) + Component_B (Y% of total) + ...
```

This determines the priority order for the entire project. **Decompose the score BEFORE running any experiments.** Without this, you risk spending experiments optimizing a component that contributes <10% of the total score.

Record the decomposition in `knowledge_base.md`.

### 3. Validation Strategy

**The validation set must predict test-set performance.** Check:
- Does the validation set come from the same distribution as the test set?
- If the test set has unseen conditions (new domains, interpolation, extrapolation), does validation exercise this?
- If validation is identical to a training config, it will NOT predict generalization. Consider **leave-one-config-out cross-validation** instead.

If the provided validation set is weak, create a better internal validation scheme and note this in `observations.md`.

### 4. Data Utilization Check

Audit how much data is actually used:
- Is training data subsampled? By how much?
- Are some configs/classes/domains underrepresented?
- Could using more data (or better-balanced data) improve results?

Baselines often aggressively subsample data for simplicity. Using more data (with balanced sampling across configs/classes) is frequently one of the biggest single improvements after feature engineering.

### 5. Missing Data Audit

Identify data that **would help the model but isn't available** (or isn't being used). This is critical for two reasons: (a) it flags what to request if you can get more data, and (b) it reveals what the model fundamentally cannot learn from the available inputs.

For each candidate missing data source, document in `observations.md`:
- **What it is**: the variable, signal, or data source
- **Why it would help**: the mechanism by which it would improve predictions
- **Is it obtainable?**: could it be derived from existing data, requested from data providers, or computed from external sources?
- **Workaround**: if unavailable, what proxy can be computed from existing features?

Examples of commonly missing data:
- **Spatial context** (neighboring values) -- often unavailable in pointwise prediction tasks
- **Temporal history** (prior timesteps) -- unavailable in single-snapshot tasks
- **Metadata** (experimental conditions, instrument IDs, configuration labels) -- sometimes available but not provided as features
- **Higher-fidelity reference data** (DNS, experimental measurements) -- may exist but not in the training set
- **External data sources** (weather, market data, material databases) -- may be freely available but not included

Revisit this audit whenever the model plateaus. A plateau often means the model has extracted all learnable information from the current feature set, and progress requires new information sources.

### 6. Deployment Constraints

Document any constraints on the deployment environment:
- **Compute**: GPU available? CPU-only? Time limits?
- **Libraries**: What's installed in the evaluation environment?
- **Memory**: How much RAM/VRAM?
- **Submission format**: What files, what interface?

If training locally with GPU but deploying on CPU, implement **adaptive inference** from the start (see GPU Acceleration section). Estimate CPU training time early: `CPU_time ≈ GPU_time × 10-15x`.

### Baseline Audit Output

- Updated `observations.md` with bugs, data issues, deployment constraints
- Score decomposition in `knowledge_base.md`
- Missing data audit in `observations.md` (what data would help + workarounds)
- Validation strategy decision documented
- First entry in `results.tsv`: the unmodified baseline score

---

## Phase 1: Model Selection Tournament

**CRITICAL: Do NOT skip this phase.** The commit/revert mechanism in the HDR loop creates greedy lock-in -- once an approach works, you hill-climb within it and never explore alternatives seriously. This phase prevents that by forcing a fair comparison across fundamentally different model families BEFORE committing to one.

### Why This Matters

The greedy commit/revert mechanism causes a common failure mode: the first approach that works captures all subsequent attention, and alternative model families never get equal optimization effort. The tournament prevents this.

### The Tournament Protocol

1. **Select 3-5 fundamentally different model families.** "Fundamentally different" means different inductive biases, not hyperparameter variations. Examples:
   - Neural network (MLP, CNN, etc.)
   - Gradient boosted trees (XGBoost, LightGBM)
   - Kernel methods (SVR, Gaussian Process)
   - Linear models with nonlinear features (polynomial, RBF)
   - Random Forest
   - Domain-specific model (physics-informed, analytical closure, etc.)

2. **For each family, run a minimal but fair baseline** (~5 experiments each):
   - Use the SAME feature set for all families
   - Tune each family's most important 2-3 hyperparameters
   - Use the same train/validation split
   - Record: primary metric, inference time, training time, number of parameters

3. **Compare on equal footing.** Create a tournament table:
   ```
   | Model Family | Best Metric | Inference | Training | Params | Experiments |
   |-------------|-------------|-----------|----------|--------|-------------|
   | MLP         | ...         | ...       | ...      | ...    | 5           |
   | XGBoost     | ...         | ...       | ...      | ...    | 5           |
   | SVR         | ...         | ...       | ...      | ...    | 5           |
   ```

4. **Select 1-2 winners** for the main HDR loop. The winner is the family with the best metric that meets all constraints (inference time, training time, etc.). If two families are close, keep both and run parallel tracks.

5. **Record the tournament results** in `knowledge_base.md` with reasons. This prevents revisiting rejected families later without new evidence.

### What Counts as "Fundamentally Different"

| Same family (don't count) | Different family (do count) |
|---|---|
| MLP 128x5 vs MLP 256x3 | MLP vs XGBoost |
| XGBoost 100 trees vs 500 trees | XGBoost vs Random Forest |
| Adam vs AdamW | Neural net vs kernel method |
| ReLU vs SiLU | Parametric model vs non-parametric |
| Batch size 32k vs 64k | Discriminative vs generative |

### When to Re-Run the Tournament

If the HDR loop plateaus (5+ consecutive reverts with no improvement), return to the tournament:
- The plateau may indicate the chosen family has hit its representation limit
- Try the 2nd-place family from the original tournament with the feature engineering learned so far
- Or try a NEW family not in the original tournament

### Tournament Output

The tournament produces:
- `tournament_results.md` -- comparison table, analysis, decision rationale
- Updated `knowledge_base.md` -- what each family is good/bad at for this problem
- Updated `research_queue.md` -- hypotheses specific to the winning family

---

## Phase 2: The HDR Loop

Each experiment follows an 8-step hypothesis cycle. The agent never hill-climbs blindly -- every change is grounded in a mechanism.

```
1. Pick Question        <- highest-impact from research_queue.md
2. State Prior          <- numerical probability (0-100%) BEFORE testing
3. Articulate Mechanism <- WHY would this work? Causal story from domain theory.
4. Implement ONE Change <- edit strategy.py, git commit BEFORE running
5. Evaluate             <- run evaluation across ALL benchmark tasks
6. Record Results       <- append to results.tsv (ALL metrics, no cherry-picking)
7. Update Beliefs       <- posterior probability, keep or revert
8. Update Knowledge     <- knowledge_base.md, re-rate queue, spawn new Qs
```

### Step details

**1. Pick Question**: Pull the highest-impact OPEN question from `research_queue.md`. If empty, generate new questions from knowledge gaps, recent results, or unexplored regions. Rate impact: HIGH / MEDIUM / LOW.

**2. State Prior**: Numerical probability (0-100%) that the hypothesis improves the metric, with reasoning. Commit to a belief so data can update it.

**3. Articulate Mechanism**: WHY would this change improve results? What's the causal story from domain theory? "I expect X because [mechanism]. If true, I should see [observable consequence]." If you can't explain why, a positive result is likely noise.

**4. Implement One Change**: Exactly ONE modification (isolation principle). Edit ONLY `strategy.py`. Git commit BEFORE running evaluation. Commit message includes hypothesis and prior.

**5. Evaluate**: Run evaluation across ALL benchmark tasks. Report ALL metrics.

**6. Record Results**: Append to `results.tsv`. No cherry-picking -- record every metric for every task.

**7. Update Beliefs**:
- State posterior probability (0-100%) with evidence.
- **If metric improved**: keep the commit.
- **If metric degraded or unchanged**: `git revert HEAD --no-edit`.
- **If hypothesis refuted**: that's valuable knowledge. Log it. Don't retry.

**8. Update Knowledge Base**:
- Add findings to `knowledge_base.md` (what works, what doesn't, why).
- Re-rate impact of remaining queue items.
- Generate new questions spawned by results.
- Update `research_queue.md` -- mark resolved, add new.
- Log observations in `observations.md`.
- Repeat -- never stop.

### Priority Order for Experiments

Not all experiment types have equal expected value. Based on empirical results from multiple autoresearch projects, the priority order is:

1. **Fix bugs in baseline** (highest ROI -- free improvements)
2. **Domain-informed derived features** (biggest metric improvements; features that encode non-obvious domain knowledge the model can't learn from raw inputs alone)
3. **Data utilization** (use more data, better sampling, balanced configs)
4. **Training improvements** (more epochs, learning rate schedule, weight decay)
5. **Output transform tuning** (log scaling factor, target normalization)
6. **Architecture changes** (width, depth, activation -- usually small effect vs features)
7. **Speed optimization** (only after MSE is near its floor; fast inference, fast data loading)
8. **Ensemble methods** (diminishing returns, inference penalty)

**Key insight**: derived features that encode domain knowledge are almost always more valuable than architecture changes. The model CAN learn `x*y` from inputs `x` and `y`, but providing `x*y` directly as a feature saves capacity and improves generalization. However, features that are simple products of existing inputs typically DON'T help because the model learns these interactions easily. The valuable features are those that encode **non-obvious domain knowledge** (physical invariants, non-dimensional groups, regime indicators, condition encodings).

### Principles

- **Domain-first**: Every hypothesis should be grounded in domain science. The literature review ensures this.
- **Bayesian discipline**: State beliefs before looking at data. Let data update beliefs.
- **Isolation**: One change per cycle. If you change two things, you don't know which helped.
- **No overfitting**: Simpler is better. If a small param change destroys the model, it's overfit.
- **Cumulative knowledge**: Every cycle produces knowledge, even failures. The knowledge base prevents re-testing dead ideas.
- **Cross-task awareness**: Always evaluate on ALL benchmark tasks. A feature that helps one subset but hurts another is suspect.
- **Autonomous operation**: Every decision is logged and reversible.
- **No premature commitment**: The Model Selection Tournament (Phase 1) MUST be completed before deep optimization. Do not spend >10 experiments on a single model family without having compared at least 3 families.
- **Plateau = explore**: If 5+ consecutive experiments revert with no improvement, the current approach has hit its representation limit. Stop tuning hyperparameters and either (a) try a different model family, (b) add fundamentally new features, or (c) change the problem formulation (loss function, target variable, data sampling). Log the plateau in `observations.md`.

### Recognizing Plateaus

A plateau is NOT just "the last experiment reverted." It is:
- **5+ consecutive reverts** where the best score doesn't improve, AND
- **The changes span different categories** (architecture, features, training, loss)

When you detect a plateau:
1. Stop the current HDR loop
2. Diagnose: is this a data limit, feature limit, or model capacity limit?
   - If train loss >> val loss: overfitting → more regularization or less capacity
   - If train loss ≈ val loss and both plateau: feature/data limit → new features or more data
   - If train loss still declining but val plateaus: generalization limit → regularization or simpler model
3. **Revisit the Missing Data Audit** -- the plateau often means the model has extracted all learnable information from the current features. What additional data or features would break through?
4. Return to the Model Selection Tournament or add a fundamentally new feature
5. Resume the HDR loop with the new approach

---

## File Structure

```
program.md              # This file -- instructions + methodology
literature_review.md    # Comprehensive literature review (Phase 0 output)
feature_candidates.md   # Domain quantities -> computable proxies
papers.csv              # Paper/book tracking spreadsheet
observations.md         # Signal ideas and data gaps
tournament_results.md   # Model Selection Tournament comparison (Phase 1 output)
research_queue.md       # Prioritised questions (OPEN / RESOLVED / RETIRED)
knowledge_base.md       # Cumulative findings (what works, what doesn't, why)
results.tsv             # One row per evaluation -- all metrics
strategy.py             # ONLY file modified during HDR (features + hyperparams)
evaluate.py             # Evaluation harness (fixed after setup)
prepare.py              # Data preparation (fixed after setup)
literature/
  papers/               # Downloaded PDFs of research papers
  books/                # Downloaded PDFs of textbooks
data/                   # Prepared data files
  raw/                  # Original raw data
charts/                 # Visualisations
```

---

## Data

### Input Features

| Feature | Definition | Units | Type |
|---------|-----------|-------|------|
| feature_1 | [description] | [units or "unitless"] | continuous / categorical / binary |
| feature_2 | ... | ... | ... |
| ... | ... | ... | ... |

### Dataset Structure

| Subset / Source | Samples | Avg Length | Positive Rate |
|----------------|---------|------------|---------------|
| [subset_1] | ... | ... | ... |
| [subset_2] | ... | ... | ... |

### Evaluation Tasks

Describe the evaluation protocol:
- [Task type 1]: [description]
- [Task type 2]: [description]
- ...

### Evaluation Metrics

- [Primary metric] (primary)
- [Secondary metric] (secondary)
- [Additional metrics as needed]

### Current Baselines

| Model | Params | [Primary] | [Secondary] |
|-------|--------|-----------|-------------|
| [baseline_1] | ... | ... | ... |
| [baseline_2] | ... | ... | ... |

**Gap**: [What has not been tried / where is there room to improve]

---

## Setup

```bash
pip install numpy scikit-learn pandas xgboost torch
# Add any domain-specific packages
```

---

## GPU Acceleration

**ALWAYS use GPU if available.** Training speedup is typically 10-40x, which directly multiplies the number of experiments per hour. This is critical for autoresearch -- more iterations = better results.

### Detection and Setup

At model initialization, detect and use GPU:

```python
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
```

### Training on GPU

- Move data to GPU before the training loop (or move batches if data doesn't fit)
- For large datasets (>1M points), use mini-batch training with data on CPU and batches moved to GPU
- Use `torch.no_grad()` for validation loss computation during training

### Inference: Adaptive CPU/GPU

If the model will be deployed on a machine without GPU (e.g., competition servers), implement **adaptive inference** that uses GPU when available and falls back to a fast CPU path:

```python
def predict(self, X):
    if self.device.type == 'cuda':
        # GPU inference with torch
        X_t = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            Y_pred = self.forward(X_t)
        return Y_pred.cpu().numpy()
    else:
        # CPU inference with numpy (avoids torch CPU overhead for small models)
        h = X.astype(np.float32)
        for i in range(len(self._weights) - 1):
            h = h @ self._weights[i].T + self._biases[i]
            np.maximum(h, 0, out=h)  # ReLU in-place
        h = h @ self._weights[-1].T + self._biases[-1]
        return h
```

The numpy path avoids torch's CPU dispatch overhead and is often faster for small models (<100k parameters) on CPU. Extract weights after training:

```python
self._weights = [l.weight.detach().cpu().numpy() for l in self.layers]
self._biases = [l.bias.detach().cpu().numpy() for l in self.layers]
```

### Additional Speed Optimizations

- **Raw file I/O**: Use `np.fromfile()` instead of library-specific loaders when possible
- **Cache scaler parameters**: Extract sklearn scaler min/range as numpy arrays; apply manually during inference
- **Avoid sklearn at inference**: Sklearn's transform() has Python overhead; a manual `(X - min) / range` is faster
- **Profile before optimizing**: Measure where inference time is actually spent (data loading vs scaling vs forward pass) before optimizing

### GPU Memory Management

For datasets that don't fit in GPU memory:
- Keep training data on CPU, move mini-batches to GPU
- Use `batch_size` that fills ~50-70% of GPU memory
- Delete intermediate tensors and call `torch.cuda.empty_cache()` if needed

---

## Constraints

- ONE change per experiment (isolation principle)
- ALWAYS commit before running evaluation
- ALWAYS record results in results.tsv
- ALWAYS evaluate on ALL benchmark tasks (not just best-case)
- ALWAYS use GPU for training if available
- Ground every hypothesis in domain science or ML theory
- NEVER stop -- keep iterating until the human stops you
