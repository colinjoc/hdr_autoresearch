# Autoresearch: [YOUR SCIENTIFIC QUESTION] -- HDR

**Local**: `/path/to/your/project/`
**Venv**: `source /path/to/venv/bin/activate`

## Objective

HDR applies to two problem types:

### Option A: Dataset-Based (Prediction/Classification/Regression)

Maximise **[PRIMARY METRIC]** and **[SECONDARY METRIC]** on [YOUR BENCHMARK / DATASET] by [PREDICTION/CLASSIFICATION/REGRESSION TASK] using Hypothesis-Driven Research (HDR).

**Primary metric: [METRIC]** (e.g., AUC, RMSE, F1)
**Secondary metric: [METRIC]** (e.g., F2-score, MAE, specificity)
**Stretch target**: [OPERATIONAL REQUIREMENT] (e.g., 95% TPR at 5% FPR)

**Benchmark**: [BENCHMARK NAME AND SOURCE]
- [Dataset size and structure]
- [Number of input features per sample]
- [Number of evaluation tasks / splits]
- Current best published result: [MODEL (METRIC VALUE)]

### Option B: Simulation-Based (Optimization/Design/Inverse Problems)

Optimise **[DESIGN OBJECTIVE]** by iteratively modifying **[DESIGN VARIABLES]** and evaluating via **[SIMULATION]** using Hypothesis-Driven Research (HDR).

**Primary metric: [METRIC]** (e.g., gate fidelity, drag coefficient, strain energy, folding accuracy)
**Secondary metric: [METRIC]** (e.g., leakage, robustness, manufacturability)
**Stretch target**: [OPERATIONAL REQUIREMENT] (e.g., 99.99% fidelity, 50% drag reduction)

**Simulation**: [SIMULATOR AND FRAMEWORK]
- Evaluation time per candidate: [seconds / minutes]
- Differentiable: [yes/no — if yes, gradients flow through the simulation]
- GPU-accelerated: [yes/no — framework and expected speedup]
- Design variable dimensionality: [number of parameters being optimised]
- Known constraints: [physical limits, manufacturing constraints, bandwidth limits]

**Key difference from dataset-based HDR**: There is no pre-existing labelled dataset to fit. The simulation IS the evaluation function — it computes the objective for any candidate design. Hypotheses modify the design parameterisation, objective function, constraints, or optimisation strategy rather than features/model architecture.

**Examples of simulation-based HDR**:
- Quantum gate pulse design (simulate Hamiltonian evolution → gate fidelity)
- Structural topology optimisation (FEM solve → compliance)
- Photonic device inverse design (FDTD solve → transmission)
- Aerodynamic shape optimisation (CFD solve → lift/drag)
- RNA sequence design (differentiable folding → structure match)
- Robot locomotion (physics engine → task reward)

---

## The Purpose of HDR: Finding Novel Solutions

**The goal is NOT to reproduce known results. The goal is to discover solutions that advance the state of the art.**

HDR is a systematic methodology for pushing beyond what has been published. The literature review, baseline audit, and tournament phases exist to establish WHERE the frontier is. The HDR loop itself exists to push PAST it.

### What "novel" means in practice

**For dataset problems**: Beat the published state of the art on a recognised benchmark. If the leaderboard says 0.92 AUC, your target is 0.93+. If no leaderboard exists, establish one and demonstrate that your approach outperforms the methods described in the literature. Novel features derived from domain theory, novel model architectures, or novel training procedures all count — but only if they produce measurably better results.

**For simulation problems**: Find designs, configurations, or control strategies that outperform published solutions on realistic simulations. "Outperform" means: better objective value, OR equal objective with better robustness/feasibility/generality, OR solving a problem variant that hasn't been addressed. Reproducing a known GRAPE result with a different framework is engineering, not research. Finding a pulse that beats GRAPE under realistic hardware constraints is research.

### How HDR enables novelty

The power of HDR is exhaustive, disciplined exploration of the design space. Humans and even automated optimisers tend to exploit one approach and miss alternatives. HDR's commit/revert cycle with mandatory hypothesis articulation forces exploration of non-obvious combinations:

- The literature review seeds 20+ hypotheses from different subfields — cross-pollination that no single researcher would attempt
- The knowledge base accumulates negative results that prune dead ends — something the literature rarely publishes
- The Bayesian belief tracking prevents both premature convergence and endless repetition
- The isolation principle (one change per experiment) identifies which ideas actually contribute, rather than bundling changes and attributing success to the wrong one

### Novelty checklist

Before declaring a project "done," verify:

- [ ] Results exceed published SOTA on the same benchmark/problem (or are within measurement uncertainty of SOTA with a simpler/faster/more robust method)
- [ ] At least one finding was surprising — something the literature didn't predict or contradicts conventional wisdom
- [ ] The knowledge base contains insights that would be valuable to other researchers (not just hyperparameter settings)
- [ ] The approach could be written up as a short paper: clear problem, clear method, clear improvement over prior work

If none of these hold, the HDR loop hasn't gone far enough. Return to the research queue, generate new hypotheses from the gaps in the knowledge base, or pivot to a harder variant of the problem.

---

## Phase 0: Literature Review

**THIS IS THE MOST IMPORTANT PHASE. DO NOT RUSH IT.**

Before any experiments, conduct a **deep, comprehensive literature review**. This is NOT a surface-level web search. This is a genuine academic review that should take hours, produce **100+ citations** in papers.csv, include **multiple textbooks**, and provide enough domain knowledge to guide every subsequent experiment. If you cannot explain the domain physics in depth without referencing the review, it is not thorough enough.

**DO NOT proceed to Phase 0.5 or any experiments until this review is genuinely comprehensive.**

### Deliverables

1. **`literature_review.md`** -- Structured review organized by theme (target: 2000+ words per theme)
2. **`papers.csv`** -- Tracking spreadsheet with **100+ entries** including textbooks, papers, reviews, and theses
3. **`feature_candidates.md`** (dataset-based) / **`design_variables.md`** (simulation-based) -- For dataset problems: domain quantities mapped to computable proxies from available features. For simulation problems: design variables, their parameterisations, physical constraints, and expected effects on the objective
4. **`research_queue.md`** -- Initial hypotheses seeded from literature findings (target: 20+ hypotheses)
5. **`knowledge_base.md`** -- Pre-populated with established results from the literature

### Citation Targets

| Source Type | Minimum Count | What to Extract |
|-------------|---------------|-----------------|
| **Textbooks** | 3-5 | Core theory, governing equations, standard derivations. These are the foundation -- not optional. |
| **Seminal papers** | 10-20 | The papers that defined the field. Every researcher in this domain would know these. |
| **Recent papers (last 3 years)** | 30-50 | Current state of the art, latest methods, recent benchmarks, new features/models. |
| **ML/method papers** | 20-30 | Specific models, architectures, feature engineering techniques applied to this domain. |
| **Review/survey papers** | 5-10 | These are the most efficient sources -- a single review paper can point to 50+ relevant works. Start here. |
| **Dataset/benchmark papers** | 5-10 | Papers describing the specific dataset, its provenance, known issues, and prior results. |
| **Total** | **100+** | Each entry must include: what was learned, how it applies to our task, and what hypothesis it generates. |

### Literature Review Themes

Structure the review around these themes. Each theme should be a substantial section (2000+ words) with multiple citations:

1. **Domain Fundamentals** -- Core theory, governing equations, established physical/biological/chemical laws. Cite the **standard textbooks** (every field has 2-3 that everyone reads). Derive the key relationships from first principles where possible. This is not optional -- you cannot do meaningful feature engineering without understanding the physics.

2. **Phenomena of Interest** -- The specific process you are predicting/classifying. Known mechanisms, pathways, timescales, observable precursors. What are the **known functional relationships** between inputs and outputs? What are the **known failure modes** of existing models?

3. **Derived/Candidate Features from Theory** (dataset-based) / **Design Variables and Parameterisations** (simulation-based) -- For dataset problems: quantities suggested by domain theory but not directly in your raw features. The bridge from theory to computable proxies is **the most valuable output of the literature review**. For simulation problems: the design variables, their parameterisations, and the tradeoffs between them. What parameterisation choices exist (piecewise constant, B-spline, Fourier, neural)? What constraints must be satisfied? What are the known tradeoffs (e.g., speed vs fidelity, robustness vs optimality)?

4. **ML / Optimisation for This Problem** -- For dataset problems: existing models, features used, results. For simulation problems: optimisation algorithms used (gradient-based, gradient-free, Bayesian, evolutionary), differentiable vs non-differentiable approaches, surrogate models, ML-accelerated simulation. What has been tried and what gaps remain. Understand **exactly** what top groups do differently.

5. **Feature Engineering Techniques** (dataset-based) / **Objective Function Design** (simulation-based) -- For dataset problems: domain-specific transformations, interaction terms, normalization strategies. For simulation problems: how the objective function is formulated — penalty terms, constraint handling, multi-objective weighting, regularisation for physical realisability. What objective formulations lead to better designs?

6. **Transfer / Generalization** -- If your problem involves multiple domains, sites, or conditions: what enables or prevents generalization across them. For simulation problems: does an optimal design for one set of parameters (e.g., one qubit frequency) transfer to another? What makes designs robust vs brittle?

7. **Related Problems** -- What can we learn from adjacent domains? Simulation-based HDR shares methodology across very different physics — optimal control in NMR informs quantum gates, structural topology optimisation informs photonic design, etc.

### How to Conduct the Review

1. **Start with review/survey papers** -- these are the most efficient entry point. A single review paper cites 50-200 references and synthesizes the field. Find 3-5 recent reviews.

2. **Read the standard textbooks** -- identify them from the review papers' references. Read (or skim) the relevant chapters. Cite specific chapters, equations, and page numbers.

3. **Read every leaderboard submission** -- for benchmark/competition tasks, find and read the paper or source code for every model on the leaderboard. Understand their exact approach.

4. **Follow citation chains** -- when a paper cites another as foundational, read that paper too. Work backwards from recent papers to find the seminal works.

5. **Search systematically** -- use multiple search queries per theme. Don't stop at the first 5 results. Search Google Scholar, arXiv, Semantic Scholar, and domain-specific databases.

6. **Read actual content** -- abstracts are not enough. Read the methods section (what did they do), results section (what did they find), and discussion (why does it work). Extract specific numbers, equations, and feature lists.

7. **Generate hypotheses** -- every paper should generate at least one testable hypothesis for research_queue.md. "This paper found X works; we should try X" is the minimum.

### Feature Engineering Guidance (Dataset-Based)

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

### Design Variable Guidance (Simulation-Based)

For simulation-based problems, the equivalent of "feature engineering" is **design parameterisation** — how you represent the space of candidate solutions. This choice profoundly affects optimisation landscape smoothness, convergence speed, and solution quality.

**High-value parameterisation choices:**
- Smooth basis functions (B-splines, Fourier series, Chebyshev polynomials) — reduce dimensionality while maintaining expressiveness
- Physics-informed constraints baked into the parameterisation (symmetry, periodicity, causality)
- Hierarchical parameterisations (coarse-to-fine, multi-resolution) — avoid local minima
- Differentiable relaxations of discrete choices (Gumbel-softmax for material selection, density methods for topology)

**Choices that often help:**
- Penalty terms that encode physical realisability (bandwidth limits, manufacturing constraints, smoothness)
- Multi-objective formulations that prevent degenerate solutions
- Normalisation of design variables to similar scales
- Warm-starting from known good solutions or analytical approximations

**Choices that often hurt:**
- Over-parameterisation (too many control points → noisy gradients, overfitting to simulation artifacts)
- Under-constrained optimisation (no regularisation → physically unrealisable designs)
- Piecewise-constant parameterisation when smoothness is physically required
- Ignoring hardware/manufacturing constraints during optimisation (designs that can't be built)

### Simulation Realism Requirement (Simulation-Based ONLY)

**CRITICAL: The simulation must be as realistic as possible so that optimised designs are applicable to reality.** A design that scores perfectly in an idealised simulation but fails on real hardware is worthless. The simulation IS the evaluation function — if it's unrealistic, the entire HDR loop optimises for the wrong thing.

**Mandatory realism checklist** — verify BEFORE starting the HDR loop:

- [ ] **All dominant physics included**: Every physical effect that contributes >0.1% to the objective must be modeled. E.g., for quantum gates: decoherence (T1/T2), not just coherent dynamics. For CFD: turbulence model, not just laminar flow. For structural: nonlinear material response if stresses are high.
- [ ] **Hardware/manufacturing constraints enforced**: The optimiser must know what is physically buildable. E.g., max drive amplitude (AWG limits), bandwidth limits, minimum feature size, material availability. Constraints can be hard (clipping, projection) or soft (penalty terms), but they MUST be present.
- [ ] **Sufficient resolution**: Enough levels/modes/mesh elements to capture the relevant physics. E.g., 4+ levels for transmon qubits (not just 2), fine enough mesh to resolve boundary layers, enough Fourier modes to capture dynamics.
- [ ] **Validated against known results**: Before optimising, verify the simulation reproduces published results for a known case. If a textbook says a Gaussian pulse on a transmon gives ~99% fidelity at 20ns, your simulation should agree.
- [ ] **Decoherence/dissipation/noise included**: Real systems are open, not closed. Include energy loss, dephasing, thermal noise, sensor noise, friction — whatever the dominant dissipation mechanisms are.
- [ ] **Constraint violations reported**: The evaluation function must flag when a design violates hardware constraints, not silently ignore them. Report feasibility alongside performance.

**Why this matters**: Optimisers are adversarial — they will exploit any gap between simulation and reality. An idealised simulation produces designs that are "optimal" only in the simulated world. Adding realism BEFORE optimising is far more valuable than adding it after. Lesson from quantum gates: a pulse with 99.99996% coherent fidelity is actually 99.88% when you add T1/T2 decoherence — the decoherence floor, not the pulse design, is the bottleneck.

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
- **Target: 100+ entries.** If you have fewer than 100, the review is not thorough enough. Go back and search more.

### Quality Gate: Is the Review Done?

Before proceeding to Phase 0.5, verify ALL of the following:

- [ ] papers.csv has 100+ entries
- [ ] At least 3 textbooks are cited with specific chapters/equations
- [ ] At least 5 review papers are cited
- [ ] Every model on the leaderboard/benchmark has been researched (not just named -- their actual method understood)
- [ ] feature_candidates.md has 15+ candidate features with physics justification and literature citation
- [ ] research_queue.md has 20+ hypotheses, each traced to a specific paper
- [ ] literature_review.md has 7 theme sections, each with multiple citations
- [ ] You can explain the domain physics in a 5-minute verbal explanation without looking at notes

If ANY of these fail, the review is incomplete. Do not proceed.

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

Read every line of the starter code / evaluation harness / simulation setup. Look for:
- **Bugs**: off-by-one errors, missing dimensions, wrong indices, mismatched slicing between training loss and evaluation metric. Fixing bugs is always the highest-ROI experiment.
- **Suboptimal defaults**: data subsampling that throws away most of the data, fixed seeds, commented-out features, hardcoded paths. For simulation problems: default solver tolerances, time step sizes, truncation of Hilbert space, boundary conditions.
- **Missing features** (dataset) / **Unused design freedom** (simulation): the baseline typically uses a minimal feature set or simplistic parameterisation. Note all available inputs, control channels, or degrees of freedom that aren't used.

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

### 4. Data Utilization Check (Dataset-Based) / Simulation Fidelity Check (Simulation-Based)

**Dataset-based**: Audit how much data is actually used:
- Is training data subsampled? By how much?
- Are some configs/classes/domains underrepresented?
- Could using more data (or better-balanced data) improve results?

Baselines often aggressively subsample data for simplicity. Using more data (with balanced sampling across configs/classes) is frequently one of the biggest single improvements after feature engineering.

**Simulation-based**: Audit the fidelity of the simulation:
- Is the Hilbert space / mesh / grid sufficiently resolved? What happens if you double resolution?
- Are physical effects being neglected (decoherence, nonlinearity, coupling to environment)?
- Is the solver converged (ODE tolerances, time step, iteration count)?
- What approximations are made and how do they affect the objective?

Low-fidelity simulation may produce designs that don't transfer to reality. Increasing fidelity is often the simulation equivalent of "using more data."

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

## Phase 1: Model Selection Tournament / Optimisation Strategy Tournament

**CRITICAL: Do NOT skip this phase.** The commit/revert mechanism in the HDR loop creates greedy lock-in -- once an approach works, you hill-climb within it and never explore alternatives seriously. This phase prevents that by forcing a fair comparison across fundamentally different approaches BEFORE committing to one.

### Why This Matters

The greedy commit/revert mechanism causes a common failure mode: the first approach that works captures all subsequent attention, and alternatives never get equal optimization effort. The tournament prevents this.

### The Tournament Protocol

1. **Select 3-5 fundamentally different approaches.** "Fundamentally different" means different inductive biases or optimisation strategies, not hyperparameter variations.

   **Dataset-based examples** (model families):
   - Neural network (MLP, CNN, etc.)
   - Gradient boosted trees (XGBoost, LightGBM)
   - Kernel methods (SVR, Gaussian Process)
   - Linear models with nonlinear features (polynomial, RBF)
   - Random Forest
   - Domain-specific model (physics-informed, analytical closure, etc.)

   **Simulation-based examples** (optimisation strategies):
   - Gradient-based optimisation (GRAPE/adjoint method with the differentiable simulator)
   - Gradient-free optimisation (Nelder-Mead, CMA-ES, differential evolution)
   - Bayesian optimisation (Gaussian process surrogate + acquisition function)
   - Reinforcement learning (policy gradient, PPO)
   - Hybrid (gradient-based with stochastic restarts, neural parameterisation + gradient descent)
   - Domain-specific method (DRAG for quantum gates, adjoint CFD, level-set for topology)

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

**8. Update ALL Documentation** (every 5-10 experiments, or after any major finding):
- `results.tsv` -- append EVERY experiment result (keep AND revert), EVERY time.
- `knowledge_base.md` -- update "What Works" and "What Doesn't Work" with experimental evidence. Update current best scores. Update featurizer timing table.
- `research_queue.md` -- mark tested hypotheses as RESOLVED. Add new hypotheses spawned by results. Re-rate impact of remaining items.
- `observations.md` -- add new observations. Update existing ones with experimental confirmation or refutation.
- `feature_candidates.md` -- move features between tiers based on experimental results. Update "Currently Used" section. Add newly discovered candidates.
- `literature_review.md` -- append experimental validation of literature predictions (confirmed/refuted).
- `papers.csv` -- add new references found during experiments.

**These files are the project's memory.** If they fall out of date, the HDR loop loses context and may re-test dead hypotheses or miss established findings. Treat documentation updates as part of the experiment, not an afterthought.

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

## Test-Driven Development

**ALL infrastructure code must be tested in isolation before integration.** Never assume a library call is fast or correct -- always verify on small data first. Untested components in a pipeline will waste hours when they fail or hang at scale.

### The TDD Protocol

**1. Test every new component on a tiny sample BEFORE adding it to the pipeline.**

When adding a new featurizer, data loader, model, or preprocessing step:
```python
# Time it on 50 samples first
import time
t0 = time.time()
result = new_component.process(tiny_data)  # 50 rows
elapsed = time.time() - t0
print(f"{component_name} on {len(tiny_data)} samples: {elapsed:.1f}s")
# Extrapolate: if 50 samples takes 5s, 5000 samples takes ~500s = 8 min
```

If a component takes >5s on 50 samples, it is too slow for the full pipeline. Either find an alternative or acknowledge the cost explicitly.

**2. Smoke test before full runs.**

Before running the full benchmark (all tasks, all folds), run a single fold of the smallest task:
```python
# Smoke test: 1 task, 1 fold
python prepare.py --tasks smallest_task  # Should complete in <2 min
```

Only proceed to the full benchmark after the smoke test passes.

**3. Write `test_strategy.py`.**

This file validates the strategy without running the full benchmark:
```python
# test_strategy.py -- run before every experiment
import strategy
import time

# Test featurization on small sample
tiny_inputs = train_inputs[:50]
t0 = time.time()
X = strategy.featurize(tiny_inputs, task_name)
print(f"Featurize 50 samples: {time.time()-t0:.1f}s, shape: {X.shape}")
assert X.shape[0] == 50
assert not np.any(np.isnan(X))

# Test model fits and predicts
model = strategy.get_model(task_name, is_classification=False)
model.fit(X, tiny_targets)
preds = model.predict(X)
assert preds.shape[0] == 50
print("PASS")
```

**4. Time every component explicitly.**

Maintain a timing table in `knowledge_base.md`:
```
| Component | 50 samples | 500 samples | 5000 samples | Status |
|-----------|-----------|-------------|--------------|--------|
| Magpie    | 0.2s      | 2s          | 20s          | OK     |
| WenAlloys | 8s        | 80s         | 800s (13 min)| TOO SLOW |
```

### When to Test

- **Before adding any new featurizer**: time it on 50 samples
- **Before changing the evaluation pipeline**: verify old results still reproduce
- **Before running any experiment**: smoke test on 1 fold of smallest task
- **After any infrastructure change** (prepare.py, data loading, caching): full smoke test

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
test_strategy.py        # Smoke tests for strategy.py (run before every experiment)
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
- ALWAYS test new components on small data before full runs (TDD protocol)
- ALWAYS run smoke test (1 fold, smallest task) before full benchmark
- ALWAYS commit before running evaluation
- ALWAYS record results in results.tsv
- ALWAYS evaluate on ALL benchmark tasks (not just best-case)
- ALWAYS use GPU for training if available
- NEVER add a library component without timing it on 50 samples first
- Ground every hypothesis in domain science or ML theory
- NEVER stop -- keep iterating until the human stops you
