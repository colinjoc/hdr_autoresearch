# Autoresearch: [YOUR SCIENTIFIC QUESTION] — HDR

**Local**: `/path/to/your/project/`
**Venv**: `source /path/to/venv/bin/activate`

---

## Core Principle

**The goal is DISCOVERY, not model-fitting.** A model is infrastructure. The novel result is what the model finds: new materials, new designs, new physical insights. If the HDR loop never gets past improving a regression score, it has failed.

Every project has two phases:
- **Phase A (Infrastructure, <30% of effort)**: Build predictor/simulator, validate on known cases
- **Phase B (Discovery, >70% of effort)**: Use the tool to explore the unknown

---

## Objective

### Option A: Dataset-Based
Maximise **[METRIC]** on [BENCHMARK] via HDR. Then USE the model for discovery (screen novel candidates, identify non-obvious patterns, propose untested materials/designs).

### Option B: Simulation-Based
Optimise **[OBJECTIVE]** by modifying **[DESIGN VARIABLES]** evaluated via **[SIMULATOR]**. The simulation must be realistic (all dominant physics, hardware constraints, validated against known results).

### Option C: Decomposition-Based
Reverse-engineer an existing AI-discovered or black-box solution. Identify which components and parameters carry the win, which are optimisation artifacts, and what physical mechanism explains the performance. Use **systematic ablation** of the existing solution rather than forward search over a design space. Appropriate when a published result needs interpretation, not improvement. The Phase 2 loop runs in a different rhythm — see "Phase 2 Variant: Decomposition Loop" below.

---

## Phase 0: Literature Review

**Do not skip. 200+ citations is the new minimum; aim for 300–500 if the field is large; 1000+ for truly cross-disciplinary projects.** A shallow Phase 0 is the most expensive shortcut to take in HDR — almost every project that has needed major mid-loop pivots traces the failure to incomplete lit review.

### Deliverables
1. `literature_review.md` — 7 themes, 3000+ words each (was 2000)
2. `papers.csv` — 200+ entries minimum (was 100). Composition: 5–10 textbooks, 10–20 reviews, 60–100 recent results, 30–60 methods, 20–40 cross-disciplinary references
3. `feature_candidates.md` / `design_variables.md` — domain quantities → computable proxies
4. `research_queue.md` — **100+ hypotheses minimum** (was 20). Each one specifies its design variable, expected outcome, evaluation metric, baseline, and a Bayesian prior. The lit review's job is to surface the long tail of possible experiments, not just the obvious ones.
5. `knowledge_base.md` — established results, what works, what doesn't

### Themes
1. Domain fundamentals (textbooks, governing equations)
2. Phenomena of interest (mechanisms, precursors, known relationships)
3. Candidate features / design variables (the bridge from theory to computation)
4. ML/optimisation for this problem (what's been tried, what gaps remain)
5. Objective function design / feature engineering techniques
6. Transfer / generalisation across conditions
7. Related problems (cross-domain insights)

### Quality Gate
- [ ] 200+ papers.csv entries with 5+ textbooks, 10+ reviews
- [ ] 15+ candidate features/variables with physics justification
- [ ] **100+ hypotheses** in research_queue.md
- [ ] Can explain the domain physics without notes
- [ ] **The "enough citations" heuristic below has been satisfied**

### How many citations is "enough"? — the saturation heuristic

The 200-citation floor is a minimum, not a target. The right question is "have we covered the field well enough that the next paper we read is unlikely to change our priors?" Use these three independent saturation checks; the lit review is "enough" when all three are satisfied:

1. **Marginal information gain.** Track every new citation against the running `knowledge_base.md`. A new paper "contributes" if reading it adds at least one new fact, hypothesis, mechanism, or correction to the knowledge base. Maintain a rolling count of "contributing fetches per 10 fetches". When the rolling count drops to ≤ 1 in 10 (90 percent of new fetches add nothing), the citation graph is saturating. **Stop when 20 consecutive new fetches add zero new facts to `knowledge_base.md`.**

2. **Citation-graph closure.** As you add papers to `papers.csv`, also track which references each cited paper itself cites. The lit review is approaching closure when 90 percent of any new paper's references are already in `papers.csv` — the citation graph has been mostly traversed. Compute this ratio for the 10 most-recently-added papers and stop when the rolling average exceeds 0.9.

3. **Standard textbook coverage.** Identify the canonical textbook of the field (the book a graduate student in this discipline reads in their first year). For every chapter heading in that textbook, `papers.csv` should contain at least 3 references to current research that builds on that chapter. If any chapter has fewer than 3 representative papers, the lit review is missing a sub-area.

When all three are satisfied, the lit review is "enough". Most projects will hit this between 200 and 500 citations. A few cross-disciplinary projects (e.g. AI-for-physics, where the literature spans computer science AND a physics subfield AND multi-objective optimisation AND a specific dataset) may need 800+ citations before all three saturate.

**One more rule: do not stop early just because the count crossed a threshold.** A 250-citation lit review where 80 percent of fetches still add new facts is INCOMPLETE. A 180-citation lit review where 19 of the last 20 fetches added nothing is COMPLETE. The signal is the saturation, not the count.

---

## Phase 0.5: Baseline Audit

1. **Read all code** — find bugs, suboptimal defaults, unused features/design freedom
2. **Decompose the score** — where does improvement effort have highest ROI?
3. **Validate the validation** — does it predict real-world performance?
4. **Audit data/simulation fidelity** — enough data? Realistic physics? Sufficient resolution?
5. **Missing data audit** — what would help but isn't available? What proxies exist?
6. Record baseline in `results.tsv`

### Simulation Realism (Option B only)
Before optimising, verify: all dominant physics included, hardware constraints enforced, sufficient resolution, validated against published results, dissipation/noise modeled, constraint violations reported.

### Use Published Simulators and Datasets — DO NOT BUILD YOUR OWN

**CRITICAL: Always use the standard published simulator or dataset for the field, even if it's slower or more complex than building your own.** Building a simplified custom simulator is almost always the wrong choice, even when it speeds up iteration.

**Why this matters:**
- Results from custom simulators are **not comparable** to published benchmarks. You cannot claim "we beat SOTA" unless you tested on the same simulator SOTA was measured on.
- Custom simulators tend to encode the same simplifications as the analytical baselines they replace. Beating an analytical baseline on a simulator that IS that baseline is meaningless.
- Custom simulators miss the physics that matters in reality. The optimisation will find solutions that exploit simulator artifacts rather than real phenomena.
- Reviewers and replicators will not trust results from a one-off simulator built by the same person making claims about it.

**The rule:**
1. **Identify the standard simulator/dataset** for your field during Phase 0 lit review.
2. **Use it.** Even if it is 100x slower than a custom alternative.
3. **If iteration speed is a problem**, fix it the right way: smaller test cases, lower resolution, fewer simulation steps, GPU acceleration of the standard tool, surrogate models trained on the standard tool's output. NOT a custom simulator.
4. **Validate the standard simulator reproduces published results** for a known case before starting HDR. If it doesn't, your installation is broken.
5. **Only build a custom simulator if there is genuinely no standard tool**, AND the lit review confirms this. Document why explicitly.

**Acceptable speed tradeoffs:**
- Use the standard simulator at lower fidelity (coarser mesh, fewer particles, shorter time)
- Use a published surrogate model trained on the standard simulator
- Use the standard simulator with GPU acceleration if available
- Cache expensive computations within the standard tool

**Unacceptable:**
- Reimplementing the simulator yourself "for speed"
- Replacing a complex physics simulator with a simple analytical model
- Building "the simplest possible simulator that captures the essence of the problem" — this almost always misses the essence

### REAL DATA ONLY — Never Generate Synthetic Data When Real Data Exists

**CRITICAL: Always use real measured data. Synthetic data generation is not a shortcut for "the download is annoying."**

This rule exists because a retroactive audit found that agents consistently defaulted to generating synthetic data calibrated to published statistics rather than downloading the actual datasets. Results from synthetic data reflect the calibration assumptions, not reality.

**The rule:**
1. **Always download the real dataset first.** If the API requires registration, register. If it requires pagination, paginate. If it requires manual CSV download, do it.
2. **Synthetic data is acceptable ONLY when ALL of these are true:**
   - The real data genuinely does not exist in any downloadable form
   - The project cannot proceed without it
   - The lit review confirms no open dataset exists for this problem
   - The synthetic generation method and calibration are documented with exact citations
3. **When synthetic data IS the only option:**
   - Label all results as "conditional on synthetic data" in the paper and website summary
   - The paper's limitations section must lead with this
   - Phase B discovery claims are strictly hypotheses, not findings
4. **Simulation-based projects (Option B) are exempt** — running a physics simulator (SUMO, ring-road IDM, PyPSA) is not "synthetic data", it's the project's evaluation method by design.

**Rubric impact for project selection:** If a candidate problem can only be answered with synthetic data (real data genuinely unavailable), apply a -3 penalty to the Data/Sim Availability dimension. Prefer problems where real open data exists. If the penalty drops the total below 24/30, do not select the project.

**If you find yourself writing `np.random` to generate training data for a project that has a real dataset listed in `data_sources.md`, STOP. You are making a mistake. Go download the real data.**

### Sanity Checks Before the HDR Loop Starts

Four cheap calibration runs before any HDR experiment. Each one is more valuable than a new experiment because they reveal whether downstream improvements can even be trusted.

1. **Reproduce published SOTA on the same system.** Run the published state-of-the-art method exactly as described — same simulator, same parameters, same optimiser — and verify your number is within 0.1–0.5% of theirs. A larger gap means your installation, simulator fidelity, or evaluation harness is broken. Fix the gap before starting the loop.
2. **Featurizer speed audit at 500 samples.** For Option A projects, time every off-the-shelf featurizer on a 500-sample subset before running on the full dataset. Featurizers that work on toy data can hang for hours on real scale. Cache featurization output to disk on the first run, not the tenth.
3. **Validation must not overlap training.** Run leave-one-condition-out CV alongside any holdout split. If they disagree, the holdout is overlapping training in disguise (same condition, same source) and reported gains are inflated. Trust the leave-one-out result. Do not pivot to ensembles or architecture changes until validation is honest.
4. **Linear baseline first.** Fit Ridge / Logistic on the raw features before trying any tree, NN, or ensemble. If tree methods are not >2× better than the linear baseline, the relationship is mostly linear and you should skip neural models entirely. They will not help and they will overfit.

---

## Phase 1: Tournament

Compare 3-5 **fundamentally different** approaches (not hyperparameter variants) with ~5 experiments each on the same features/data. Record in `tournament_results.md`. Select 1-2 winners for the HDR loop.

Re-run the tournament if the HDR loop plateaus (5+ consecutive reverts).

### Tournament anti-patterns

- **Bagging beats boosting for small N.** When the tournament includes a task with N < 400 training examples, ExtraTrees / Random Forest typically beats XGBoost / LightGBM by 5–10%. The boosters overfit. Test bagging explicitly on small tasks.
- **Per-task model selection is mandatory.** Do not pick one model family for the whole project. Different tasks have different optimal model families, featurizers, and target transforms. Capture per-task winners in a decision table after the tournament — one-size-fits-all trades wins on ~50% of tasks.
- **Hard thresholds beat soft blends for bimodal targets.** When a target has a sharp physical boundary (metal ↔ nonmetal, stable ↔ unstable, present ↔ absent), use a two-stage classifier→regressor with a hard threshold, not a soft probability blend. Soft blends consistently lose.

---

## Phase A → Phase B Bridge

A common Phase A → Phase B failure: the predictor improves in training but cannot rank novel candidates because features it relies on are not available outside the training set. Catch this before scaling discovery.

### Feature availability check

For every feature in the predictor, verify it can be computed for an arbitrary candidate (not just training-set members). If a feature requires data that is only present for training samples (e.g. crystal structure for compositional candidates), it will default to a placeholder on candidates and the predictor will systematically under-rank them.

Add this test:
1. Generate 5–10 synthetic candidates that span the design space.
2. Run the featurizer on them. Verify no feature defaults to a placeholder value.
3. Verify the predictor returns scores in the same range as on training data.

### Combinatorial template diversity beats predictor improvement

In Phase B the highest-impact lever is usually the **diversity of candidate templates**, not the predictor's MAE. Going from 1 template family to 5 typically yields 2–10× more discoveries. A modest predictor improvement typically yields none. Allocate Phase B effort to templates first, predictor refinement second.

### Stability / feasibility post-filter

For materials, designs, and any domain with a "physically realisable?" constraint, run a lightweight feasibility filter on the top-K predictions from the predictor. Universal ML potentials and constraint solvers are typically fast (1–10 seconds per candidate). Throw away anything infeasible. This removes predictions that exploit model weaknesses and restores honest discovery counts.

---

## Phase 2: The HDR Loop

**Run hundreds of experiments. The 20-experiment-loop pattern from the early HDR projects was too short.** A real HDR project should run **100 experiments minimum** in Phase 2 before declaring convergence, and projects with rich research queues should run **300–1000+** experiments. Each experiment is cheap if the evaluation harness is fast; the cost is in the per-experiment thinking (prior, mechanism, single change), not in the compute.

```
1. Pick Question        ← highest-impact OPEN from research_queue.md
2. State Prior          ← probability (0-100%) BEFORE testing
3. Articulate Mechanism ← WHY would this work? Causal story.
4. Implement ONE Change ← git commit BEFORE running
5. Evaluate             ← run on ALL tasks
6. Record Results       ← append to results.tsv (no cherry-picking)
7. Update Beliefs       ← keep or revert
8. Update Knowledge     ← knowledge_base.md, research_queue.md, observations.md
```

### Experiment Priority
1. Fix bugs (highest ROI)
2. Domain-informed features / design parameterisations
3. Data utilisation / simulation fidelity
4. Training improvements
5. Architecture changes
6. Speed optimisation

### How many experiments is "enough"? — the saturation heuristic for Phase 2

Mirroring the Phase 0 saturation rule: stop the HDR loop when both signals fire.

1. **Sustained revert streak.** When 20 consecutive experiments are reverted (no improvement above the noise floor), the local search is exhausted. Re-run Phase 1 (tournament) to look for a fundamentally different approach, or stop and write the paper.
2. **Research-queue exhaustion.** When fewer than 5 hypotheses remain OPEN in `research_queue.md` AND each has a Bayesian prior below 20 percent, the productive ideas are gone. Add 20+ new hypotheses from a fresh pass over the lit review, or stop.

Stopping at 100 experiments because you "hit the count" is wrong if either signal still says "keep going". Stopping at 50 experiments because the research queue is exhausted AND the last 20 experiments were all reverts is correct.

### Principles
- **Domain-first**: every hypothesis grounded in domain science
- **Isolation**: one change per experiment
- **Bayesian**: state beliefs before data, update after
- **Cumulative**: every experiment produces knowledge, even failures
- **Plateau detection — distinguish optimisation plateau from physical floor.**
  - **Optimisation plateau** (5+ consecutive reverts at moderate margins): re-tournament. The HDR loop has exhausted the current approach.
  - **Physical floor** (improvements smaller than the simulator's noise floor across many experiments): pivot to a new problem dimension instead of pushing harder. If a fundamental physical limit is binding, no amount of optimisation will help. Move to a different objective, hardware regime, or problem formulation.
- **Tighten the revert threshold late-loop.** Early experiments (1–20) accept any positive Δ above noise. Mid-loop (20–50), require Δ > 2× the experimental noise floor. Late-loop (50+), require Δ > 3× noise OR a parallel benefit (inference speed, robustness, simplicity). Otherwise the loop drowns in tied experiments.

### Bayesian Prior Calibration

Stated priors are systematically wrong in characteristic directions. Adjust accordingly:

- **Training-trick priors are overconfident.** Hyperparameter tweaks (LR schedules, weight decay, optimiser changes, init strategies, loss-function variants) feel plausible but rarely transfer. Default prior should be ≤ 30% for any standard ML training trick on a problem where the data is small or physics-rich. If your gut says 60%, write down 30%.
- **Domain-feature priors are well-calibrated.** A new feature derived from domain physics with a clear mechanistic story typically lands in the 40–60% range and the realised hit rate matches.
- **Architecture-pivot priors are catastrophically overconfident.** Switching model families feels like a 50% bet but realised success is closer to 10%. Demand strong motivation; do not pivot architectures because the loop is plateauing.
- **Inference / speed-optimisation priors are well-calibrated and stack reliably.** Treat inference-level optimisation (binary I/O, manual scaling, operator fusion, caching) as a separate axis from accuracy. It is reliable, it compounds, and it never hurts the score. Run these in parallel to accuracy work.

### Anti-Patterns to Watch For

- **"Slightly tied" experiments are a sign Occam has won.** If a more complex variant is statistically tied with a simpler baseline (Δ < 0.5pp or < experimental noise), revert. Keeping the complex variant adds noise to the next experiment's signal.
- **Per-scenario regressions hide under positive means.** Always report per-scenario / per-task / per-condition results, not just aggregate. A +5% mean improvement that includes a +200% catastrophe on one condition is a regression, not a win. The aggregate mean can be a lie.
- **Absolute conditions scale; relative thresholds don't.** Rules of the form `queue == 0` (drain fully) or `confidence > 0.9` scale across regimes. Rules of the form `current − other > K` or `improvement > 5%` work in one regime and break in others. Prefer absolute conditions.
- **Random initialisation is malpractice for parameterised search.** Never start gradient-based pulse / waveform / neural ODE / Fourier basis search from random parameters. Always warm-start from a known-good baseline (analytical solution, published seed, transfer-learned weights). Random init converges to local minima with 10–100× worse fidelity.
- **Cache custom featurization on first run.** A featurizer that takes 35 seconds on first run takes 35 milliseconds on the second if cached to disk. Add the cache the moment you write the featurizer, not after the loop is slow.

### Phase 2 Variant: Decomposition Loop (for Option C projects)

When the goal is to reverse-engineer an existing AI-discovered or black-box solution rather than to forward-optimise a new one, the HDR loop runs in a different rhythm. Replace steps 1–8 above with:

```
1. Pick component / parameter to ablate     ← from a structured list of all components
2. State expected effect                    ← Bayesian prior: essential / important / redundant
3. Ablate one thing                         ← set to 0, infinity, or remove; commit before measuring
4. Measure performance change               ← <1.2× degradation = redundant, 1.2–2× = important, >2× = essential
5. Cross-validate the finding               ← run on a second independent simulator OR against published results
6. Rebuild the minimal essential design     ← only the essentials that survived ablation
7. Re-optimise the simplified design        ← one or two parameters the original may not have tuned
8. Survey solution family                   ← repeat the decomposition on 3–5 solutions; classify by mechanism
```

#### Decomposition-mode rules

- **Component ablation before parameter sweeps.** First identify which components are essential (binary on/off ablation). Only sweep parameters of components that survive. Sweeping parameters of redundant components wastes effort and gives misleading sensitivity curves.
- **Distinguish narrow optima from broad robustness.** A parameter sweep gives you a sensitivity curve. Sharp peaks (±5% kills the design) indicate real physics — lock down tight specifications. Broad plateaus indicate the optimiser over-parameterised a robust choice — simplify or reoptimise.
- **Cross-validate decomposition against an independent source.** Differentiable simulators and step-based simulators can disagree on internal scales. Verify the dominant mechanism on both before publishing the interpretation.
- **Survey the family, don't extrapolate from one solution.** After decomposing the best solution, decompose 3–5 others from the same family. They may use distinct mechanisms (e.g. signal amplification vs noise suppression). The "explanation" of the AI's discovery may be plural.
- **Verify the simplified design reaches or beats the original.** A successful decomposition produces a minimal design that, after re-optimising 1–2 free parameters, matches or exceeds the original AI-discovered performance. If it doesn't, you removed something essential.

---

## Phase 3: paper.md (the only writeup the project owns)

After the HDR loop converges (improvements plateau OR novelty checklist satisfied), produce a single deliverable: `paper.md`, a formal academic paper. This is the canonical source of truth for the project. The public-facing website summary is generated automatically by the website summary pipeline (`~/website/pipeline/`) directly from `paper.md` — projects no longer maintain their own `summary.md`.

### `paper.md` — Formal academic paper

A publication-quality academic paper. Structure:

1. **Abstract** — 200-300 words. Problem, method, key result, novelty.
2. **Introduction** — context, prior work, the gap this paper fills. Cite the foundational papers in the field.
3. **Methods** — simulator/dataset (with version), baseline, HDR protocol, evaluation metric. Reproducible from the description alone.
4. **Results** — every kept experiment, with tables and figures. Quantitative findings. Number every claim.
5. **Discussion** — physical interpretation, why it worked, what surprised us, limitations, threats to validity, what wasn't tested.
6. **Conclusion** — punchline + implications + future work.
7. **References** — 30+ citations from `papers.csv`, properly formatted (numbered or author-year, consistent throughout).

**Quality bar**:
- Every claim cited
- Every number traceable to a specific experiment in `results.tsv`
- Honest about limitations and what wasn't tested
- A reviewer should be able to replicate the work from the paper alone
- Match the conventions of the target venue (Phys. Rev. Letters, Nature Communications, or domain-specific journal)
- Standard academic tone — not breathless, not understated
- Write the paper LAST so it reflects the full HDR journey, not the original hypotheses

**Writing rules** (apply to both `paper.md` and any derived public summary):

- **Always expand abbreviations on first use.** Every acronym, shorthand, Greek letter or symbol must be spelled out the first time it appears, with the abbreviated form in parentheses, before it is used standalone. This applies even to "well-known" abbreviations — the audience may not know them. Subsequent mentions in the same document can use the short form.

- **Every paper.md and every derived public summary must contain a Detailed Baseline section and a Detailed Solution section as standalone sections.** These are in addition to the methodology section, not replacements for it.

  The **Detailed Baseline section** describes what the baseline algorithm / dataset / design actually is, in enough depth that an unfamiliar reader can understand it without external references. It must include: the name of the baseline, its mathematical formulation (formulas, equations) if applicable, its historical and theoretical origin, what it actually computes or produces step by step, its assumptions and known failure modes, the specific parameter values used in this study, and a justification for why it is the right comparison target. Examples of what counts as "the baseline" depend on the project type — it might be an analytical formula, a published algorithm, a published reference design, or a standard dataset preprocessing pipeline.

  The **Detailed Solution section** describes the final discovered solution in equivalent depth. It must include: the name of the solution, the mathematical formulation, the actual final code block for code-based solutions, a step-by-step explanation of how it works, the causal mechanism for why it works, the concrete differences from the baseline, the assumptions and limits, and how to reproduce it starting from the baseline. The reader should be able to read the code (or equations) and understand what changed.

  The reader should be able to reach the end of these two sections and understand both (a) the prior state of the art well enough to reproduce it, and (b) the new contribution well enough to reproduce it, without needing any external context.

- **The methodology section answers two questions only**: (a) what was the baseline and how was it calculated, with enough detail for reproduction, and (b) how did the project iterate on the baseline to reach the final result, including what classes of hypothesis were tested and what the keep-vs-revert criterion was. The methodology section MUST NOT include literature citation counts, hypothesis counts, or any other Phase 0 / Phase 0.5 work-effort metric. Those numbers are administrative trivia and live in `experiment_log.md`, not in the published methodology.

- **Section ordering for paper.md and summaries**: Abstract → Introduction → **Detailed Baseline** → **Detailed Solution** → Methods (the iteration process) → Results → Discussion → Conclusion → References. The two new sections sit between the introduction and the methods because they establish what is being compared *before* the reader sees how the comparison was done.

### Public summary (auto-generated, do not maintain by hand)

The website summary pipeline at `~/website/pipeline/` runs daily, scans every `applications/<project>/paper.md`, and regenerates `~/website/site/content/hdr/results/<project>.md` whenever the paper changes (hash-diff detection). The pipeline takes care of:
- Hugo frontmatter
- Tech-leaning-layman tone
- Resolving hyperlinks for benchmarks, datasets, simulators, and code repos
- Footer links to source code and HDR methodology
- Auto-commit and push to the website repo

**Do not write `summary.md` in the project directory.** It is deprecated; the pipeline owns the public version.

---

## Novelty Checklist

Before declaring done:
- [ ] Results exceed published SOTA (or match with simpler/faster/more robust method)
- [ ] At least one surprising finding
- [ ] Knowledge base contains insights valuable to other researchers
- [ ] Paper.md drafted with abstract, methods, results, discussion, references

---

## Repository Hygiene: No Data, No PDFs

**The git repo must contain ONLY code and markdown — never data files, never paper PDFs.**

### Why
- Data files bloat the repo (gigabytes of parquet/csv/h5)
- Paper PDFs may have copyright restrictions
- Other researchers should fetch data from the canonical source, not a copy
- Reproducibility requires linking to versioned upstream sources

### What gets committed
- `program.md`, `literature_review.md`, `papers.csv`, `research_queue.md`, `knowledge_base.md`, `results.tsv`, `observations.md`, `paper.md` — all markdown
- `model.py`, `evaluate.py`, `tests/` — all Python source
- `.gitignore` — exclude `data/`, `literature/`, `venv/`, `__pycache__/`, `discoveries/*.csv` if large

### What gets a URL link instead
- **Datasets** → URL in `data_sources.md`
- **Paper PDFs** → DOI/arXiv/journal URL in `papers.csv`
- **Trained model weights** → HuggingFace/Zenodo URL in `model_artifacts.md`
- **External code** → GitHub URL with commit hash in `dependencies.md`

### Required: `data_sources.md`

Single markdown file at the project root listing every external data source with:
- **Name** — what it is
- **URL** — where to download it
- **Size** — approximate
- **Checksum** — SHA256 of the canonical version (for reproducibility)
- **License** — what you can do with it
- **Local path** — where the code expects to find it after download
- **Download command** — wget/curl/gh-clone command to fetch it

### .gitignore template
```
# Data — fetched from URLs in data_sources.md
data/
discoveries/*.csv

# Literature — fetched from URLs in papers.csv
literature/papers/
literature/books/

# Python
venv/
__pycache__/
*.pyc

# Models — too large for git
*.pkl
*.ubj
*.h5
*.safetensors
```

---

## File Structure

```
program.md              # Methodology (this file)
literature_review.md    # Phase 0 narrative review
papers.csv              # 100+ citations with URLs (no PDFs)
data_sources.md         # External data URLs (no data files)
feature_candidates.md   # Domain → computable features
research_queue.md       # Prioritised hypotheses
knowledge_base.md       # Cumulative findings
results.tsv             # Every experiment result
observations.md         # Data gaps, signal ideas
paper.md                # Phase 3 academic paper writeup
model.py / strategy.py  # ONLY file modified during HDR
evaluate.py             # Evaluation harness (fixed)
tests/                  # TDD — test every component before integration
discoveries/            # Novel candidates found (Phase B output)
```

---

## Constraints

- ONE change per experiment
- ALWAYS test on small data before full runs
- ALWAYS commit before evaluation
- ALWAYS record in results.tsv
- ALWAYS use GPU if available
- Ground every hypothesis in domain science
- NEVER stop — keep iterating until the human stops you
