# Autoresearch: [YOUR SCIENTIFIC QUESTION] — HDR

**Local**: `/path/to/your/project/`
**Venv**: `source /path/to/venv/bin/activate`

---

## Phase exit criteria (machine-checkable, BLOCKING)

A phase is **complete** only when the named artifact exists on disk AND the
named content marker is inside it. Summarising intent in another document
does NOT satisfy an exit criterion. A task-tracker entry cannot be marked
complete unless these are true.

| Phase | Required artifact(s) in `applications/<project>/` | Content marker / rule |
|---|---|---|
| 0 | `papers.csv` + `literature_review.md` + `knowledge_base.md` + `research_queue.md` + `design_variables.md` | ≥200 citations in `papers.csv`; ≥100 hypotheses in `research_queue.md` |
| 0.5 | `E00` row in `results.tsv` + `data_sources.md` | Real data only (no synthetic); seed-stable |
| 1 | ≥4 model families in `results.tsv` + `tournament_results.csv` | Include a linear-model sanity check |
| 2 | ≥20 rows in `results.tsv` with `status` ∈ {KEEP, REVERT} | Every KEEP ties to a commit and re-runs from cache |
| 2.5 | Pairwise-interaction rows in `results.tsv` | Top-N near-miss features actually tested |
| **2.75** | `paper_review.md` AND all reviewer-mandated experiments present in `results.tsv` with `status` in {RUN_RV, CONTROL, TEMPORAL, DIAG} | `paper_review.md` must be written by a **different sub-agent invocation** from the HDR author; "documented in §Limitations" is NOT a valid completion |
| 3 | `paper.md` | References each KEEP experiment by ID |
| **3.5** | `paper_review_signoff.md` | Must contain the literal string `NO FURTHER BLOCKING ISSUES`; written by a **different sub-agent invocation** from Phase 2.75 |
| B | `phase_b_discovery.py` output in `results.tsv` or `discoveries/` | Actual inverse-design outputs, not more training runs |
| Publish | `~/website/site/content/hdr/results/<slug>/index.md` | **Requires `paper_review_signoff.md` to exist in the project first.** Hugo build passes. |

**Anti-pattern watchlist** (explicit — these were cut corners in prior runs):
- Marking Phase 2.75 "complete" by inlining limitations into `paper.md §8`.
  The whole point of Phase 2.75 is a **blind independent reviewer**; the author
  cannot play both roles.
- Publishing to the website before `paper_review_signoff.md` exists.
- Claiming a "champion" on a random-split holdout without a temporal-split
  confirmation (`status=TEMPORAL` in `results.tsv`).
- Claiming framework novelty when hardware resolution is ≥10× below the
  published frontier — call it replication, not a contribution.

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

### Hypothesis Selection: Impact Scoring

"Highest-impact first" must be explicit, not vibes. Each hypothesis in `research_queue.md` gets a 3-axis score:

| Axis | 1 (low) | 2 (medium) | 3 (high) |
|------|---------|------------|----------|
| **Expected Δ** | < noise floor | 1–3× noise | > 3× noise |
| **Novelty** | Standard technique, well-explored | Published but untested in this domain | No prior work; genuinely new combination |
| **Mechanistic clarity** | "Might help" | Plausible causal story | Clear physics/domain mechanism with literature support |

**Impact = Expected Δ + Novelty + Mechanistic clarity** (range 3–9). Pick the highest-scoring OPEN hypothesis. Break ties by preferring the one with the prior closest to 0.5 (maximum expected information gain — see Prior Discipline below).

**Long-shot quota:** At least 20% of hypotheses in `research_queue.md` must have a stated prior ≤ 0.3. This prevents the queue from being dominated by "safe" confirmatory hypotheses. If the queue falls below the 20% long-shot ratio after pruning, add new speculative hypotheses from the literature before continuing. Long-shots are where the surprising discoveries come from — the methodology must not systematically avoid them.

### How many experiments is "enough"? — the saturation heuristic for Phase 2

Mirroring the Phase 0 saturation rule: stop the HDR loop when both signals fire.

1. **Sustained revert streak.** When 20 consecutive experiments are reverted (no improvement above the noise floor), the local search is exhausted. Re-run Phase 1 (tournament) to look for a fundamentally different approach, or stop and write the paper.
2. **Research-queue exhaustion.** When fewer than 5 hypotheses remain OPEN in `research_queue.md` AND each has a Bayesian prior below 20 percent, the productive ideas are gone. Add 20+ new hypotheses from a fresh pass over the lit review, or stop.

Stopping at 100 experiments because you "hit the count" is wrong if either signal still says "keep going". Stopping at 50 experiments because the research queue is exhausted AND the last 20 experiments were all reverts is correct.

### Principles
- **Domain-first**: every hypothesis grounded in domain science
- **Isolation**: one change per experiment (but see Interaction Sweep below)
- **Bayesian**: state beliefs before data, update after (see Prior Discipline below)
- **Cumulative**: every experiment produces knowledge, even failures
- **Plateau detection — distinguish optimisation plateau from physical floor.**
  - **Optimisation plateau** (5+ consecutive reverts at moderate margins): re-tournament. The HDR loop has exhausted the current approach.
  - **Physical floor** (improvements smaller than the simulator's noise floor across many experiments): pivot to a new problem dimension instead of pushing harder. If a fundamental physical limit is binding, no amount of optimisation will help. Move to a different objective, hardware regime, or problem formulation.
- **Tighten the revert threshold late-loop.** Early experiments (1–20) accept any positive Δ above noise. Mid-loop (20–50), require Δ > 2× the experimental noise floor. Late-loop (50+), require Δ > 3× noise OR a parallel benefit (inference speed, robustness, simplicity). Otherwise the loop drowns in tied experiments.

### Interaction Sweep (Phase 2.5)

The isolation principle is analogous to coordinate descent: it finds improvements along single axes but misses combinatorial effects. A change that fails in isolation may succeed in combination with another. After the main Phase 2 loop converges, run an interaction sweep to catch these.

**When to run:** After Phase 2 converges (sustained revert streak OR research-queue exhaustion), before writing the paper.

**Procedure:**
1. **Collect near-miss rejects.** From `results.tsv`, identify all reverted experiments where the result was within 1× the noise floor of the KEEP threshold (the "almost worked" changes). Take the top N candidates (N ≤ 8, typically 5).
2. **Run a fractional factorial.** Test all pairs of near-miss rejects applied simultaneously (N×(N-1)/2 experiments). For N=5 this is 10 experiments; for N=8 this is 28. Each experiment applies exactly two reverted changes together.
3. **Escalate winners.** Any pair that passes the KEEP threshold is kept as a unit. If multiple pairs win, test the union of all winning pairs as a single experiment.
4. **Record interaction findings.** In `results.tsv`, tag interaction experiments with `interaction=True` and note which individual experiments they combine. In `knowledge_base.md`, document which interactions were synergistic and hypothesise why — this is often a genuine discovery about the problem structure.

**What this is NOT:** It is not a full combinatorial search (2^N is intractable for large N). It is a targeted sweep over the most promising rejected changes. The methodology is closer to coordinate descent with a post-hoc pairwise interaction check than a full design-of-experiments approach. This is an explicit trade-off: tractability over completeness.

**Scope limit:** If no reverted experiments are within 1× noise of the KEEP threshold, skip the interaction sweep — the rejected changes were clearly bad individually and unlikely to rescue each other.

### Prior Discipline

Bayesian priors are only useful if they are (a) calibrated, (b) used to order work, and (c) updated after each experiment. Without all three, stating a prior is performative rather than functional.

#### 1. Calibration Tracking

After every 20 experiments, compute a calibration check: bin all stated priors into buckets (0–0.3, 0.3–0.5, 0.5–0.7, 0.7–1.0) and compare the stated probability against the actual KEEP rate in each bucket. Record this in `results.tsv` as a calibration row.

- If priors in the 0.7–1.0 bucket have a KEEP rate below 0.4, the agent is systematically overconfident. Apply a blanket 0.7× deflation to all future priors until the next calibration check.
- If priors in the 0–0.3 bucket have a KEEP rate above 0.5, the agent is systematically underconfident about long-shots. Raise the long-shot quota (see Hypothesis Selection above) to 30%.
- If calibration is reasonable (within ±15pp per bucket), no adjustment needed.

Over time this produces a calibration curve that is itself a finding about how well the methodology predicts its own outcomes.

#### 2. Prior-Informed Queue Ordering

Hypotheses where the prior is far from 0.5 (strong belief either way) are less informative — you mostly already know what will happen. Hypotheses near 0.5 with high impact scores should go first because they maximise expected information gain.

**Ordering formula:** When two hypotheses have the same impact score, break ties by preferring the one whose prior is closest to 0.5. When impact scores differ, impact wins — a high-impact hypothesis at 0.8 prior still beats a low-impact one at 0.5 prior. But among equals, chase uncertainty.

#### 3. Posterior Updating

After each experiment, compute and record the updated belief:
- **KEEP result**: posterior = prior × 1.5 (capped at 0.95) for related hypotheses in the same cluster (e.g. if a VIX feature worked, raise priors for other volatility features)
- **REVERT result**: posterior = prior × 0.5 for related hypotheses

Record the posterior in `research_queue.md` alongside the prior. If a cluster of related hypotheses all converge toward posterior < 0.1 after multiple experiments, retire the cluster — the mechanism is not active in this problem. Conversely, if a cluster converges toward posterior > 0.8, the mechanism is confirmed; shift effort elsewhere.

This prevents two failure modes: (a) endlessly testing variants of a dead idea, and (b) abandoning a productive direction after a single failure.

#### 4. Known Bias Corrections

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

## Phase 2.75: Adversarial Results Review

**Mandatory. Do not skip. Do not combine with the HDR agent's own context.**

After Phase 2.5 (interaction sweep) converges and before writing the paper, a **separate reviewer agent** audits the project. The reviewer must run in a fresh context with no access to the HDR agent's conversation history — it sees only the project artifacts on disk. Its job is to find flaws, not confirm quality.

### Reviewer inputs (read-only)

The reviewer reads these files from `applications/<project>/`:
- `results.tsv` — every experiment result
- `knowledge_base.md` — accumulated claims
- `research_queue.md` — what was tested and what wasn't
- `literature_review.md` — what the literature says
- `model.py`, `evaluate.py` — the code
- `data/` — the actual data (or `data_sources.md` to fetch it)

### Review protocol

The reviewer produces `review.md` with structured findings:

**1. Reproducibility check.** Re-run 5 randomly selected experiments from `results.tsv` using the committed code. Verify the numbers match within the stated noise floor. Flag any that don't.

**2. Cherry-picking audit.** Compare the number of git commits tagged as experiments to the number of rows in `results.tsv`. They should match. Check that REVERT experiments are recorded, not just KEEPs. Flag any gaps.

**3. Overclaiming check.** For every claim in `knowledge_base.md`, trace it to a specific experiment in `results.tsv`. Flag any claim not directly supported by experimental evidence. Check that effect sizes are described accurately (not rounded up, not stripped of uncertainty).

**4. Statistical validity.** Check whether reported improvements exceed the experimental noise floor. Check for per-task regressions hidden under positive aggregate means. Check whether the evaluation metric is appropriate for the claim being made.

**5. Missing experiments.** This is the highest-value step. The reviewer proposes 5–10 experiments that the HDR agent did not run but should have, given the literature review, the results so far, and obvious robustness/generalisability gaps. These are not optional suggestions.

**6. Scope and framing audit.** Check whether the headline finding, title, and abstract carry appropriate qualifiers. Flag any result presented without the conditions under which it holds (e.g. "works on a single-lane ring road" omitted from a claim about traffic).

### Each finding has a severity

| Severity | Definition | HDR agent obligation |
|----------|-----------|---------------------|
| **CRITICAL** | Result is wrong or unreproducible | Must fix before proceeding |
| **MAJOR** | Overclaim, missing qualifier, or significant gap | Must fix or rebut with specific experimental evidence |
| **MINOR** | Style, clarity, or a nice-to-have experiment | Should fix; may acknowledge as limitation |

### HDR agent response protocol

The HDR agent writes `review_response.md` addressing every finding. Each response must be one of:

- **FIX** — change the code, re-run the experiment, or revise the claim. Show the diff or new result.
- **REBUT** — cite a specific experiment (by ID in `results.tsv`) that contradicts the finding. "I disagree" without evidence is not a valid rebuttal.
- **ACKNOWLEDGE** — add to `knowledge_base.md` limitations and flag for the paper's Discussion section.

### Suggested experiments are mandatory

**When the reviewer proposes missing experiments, the HDR agent MUST run them.** This is not optional. The reviewer's missing-experiment suggestions are treated as new entries in `research_queue.md` with priority above all remaining queued hypotheses. The HDR agent:

1. Adds each suggested experiment to `research_queue.md` with a prior and mechanism (the reviewer may suggest these, or the HDR agent states them).
2. Runs each experiment through the standard Phase 2 loop (implement, evaluate, record, update).
3. Reports results in `review_response.md` with the experiment ID from `results.tsv`.

If a suggested experiment reveals a problem (e.g. the headline finding doesn't hold under different conditions), this is a genuine discovery and must be reported honestly — not suppressed. The paper must reflect whatever the experiments show, even if it weakens the headline.

### Second pass

After the HDR agent submits `review_response.md`, the reviewer gets one more pass. If all CRITICAL and MAJOR findings are resolved, the reviewer signs off. If not, the cycle repeats. Maximum 3 review rounds — if findings are still unresolved after 3 rounds, they go into the paper as open limitations.

### Deliverables

```
applications/<project>/
├── review.md              # Reviewer's structured findings
├── review_response.md     # HDR agent's responses + new experiment results
└── review_signoff.md      # Final reviewer pass — approved or open items noted
```

---

## Phase 3: paper.md (the only writeup the project owns)

After the review cycle is complete (reviewer sign-off obtained), produce a single deliverable: `paper.md`, a formal academic paper. This is the canonical source of truth for the project. The public-facing website summary is generated automatically by the website summary pipeline (`~/website/pipeline/`) directly from `paper.md` — projects no longer maintain their own `summary.md`.

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

- **Section ordering for paper.md**: Abstract → Introduction → **Detailed Baseline** → **Detailed Solution** → Methods (the iteration process) → Results → Discussion → Conclusion → References. The two new sections sit between the introduction and the methods because they establish what is being compared *before* the reader sees how the comparison was done.

### Plots and figures in paper.md (mandatory)

Every paper.md must include plots generated by a `generate_plots.py` script in the project directory. Plots are saved as PNG (300 DPI) to a `plots/` subdirectory and referenced in the markdown as `![caption](plots/filename.png)`. Commit the PNGs to git alongside the paper.

**Rule of thumb: add a plot when the finding would take more than 2 sentences to describe in text.** If you're writing a paragraph of numbers comparing 5 things, that's a chart, not prose.

**Mandatory plots (every project):**

1. **Predicted vs actual scatter** — shows model quality at a glance. Tight diagonal = good, scatter = bad. Include the 1:1 reference line.
2. **Feature importance (top 10-15)** — horizontal bar chart of permutation importance or SHAP values. This IS the mechanism finding — what the model actually relies on.
3. **The headline finding visualised** — whatever the "surprise" is (the refutation, the threshold, the decomposition, the Pareto front) as a single compelling figure. This is the figure a journalist would use.

**Conditional plots (add when the trigger applies):**

| Trigger | Plot type |
|---|---|
| Phase 2 had multiple keeps | Waterfall chart of cumulative improvement, experiment by experiment |
| Phase B produced a Pareto front | Pareto scatter with labelled knee points and the baseline marked |
| Data has a geographic dimension | Choropleth map or station-level heatmap |
| Data has a time dimension | Time series with the key event or anomaly highlighted |
| Two competing hypotheses tested | Side-by-side grouped bar chart or paired dot plot |
| Distribution shape matters to the story | Histogram with annotated thresholds (e.g. the 200 Bq/m³ radon line) |
| Before/after comparison | Paired scatter or back-to-back histogram showing the shift |
| Cross-city or cross-country comparison | Faceted small-multiples or a single ranked bar chart |

**Style rules for plots:**
- Use `matplotlib` with a clean style (`plt.style.use('seaborn-v0_8-whitegrid')` or similar)
- Label axes with units. Title optional (the caption in the markdown serves as the title).
- Use colourblind-safe palettes (e.g. `tab10`, `Set2`, or the Wong palette)
- `dpi=300, bbox_inches='tight'` for every `savefig`
- Keep each PNG under 500 KB (resize if needed)
- No more than 8-10 plots per paper — each one must earn its place

**File structure:**
```
applications/<project>/
├── generate_plots.py    # reads results.tsv + cached data, produces all PNGs
├── plots/
│   ├── pred_vs_actual.png
│   ├── feature_importance.png
│   ├── headline_finding.png
│   └── ...
├── paper.md             # references plots as ![](plots/filename.png)
└── ...
```

`generate_plots.py` must be runnable standalone (`python generate_plots.py`) and produce all plots from cached data without re-running the model. It reads `results.tsv`, any cached predictions, and the cleaned dataset.

### Public summary (auto-generated, do not maintain by hand)

The website summary pipeline at `~/website/pipeline/` runs daily, scans every `applications/<project>/paper.md`, and regenerates `~/website/site/content/hdr/results/<project>.md` whenever the paper changes (hash-diff detection). The pipeline takes care of:
- Hugo frontmatter
- Tech-leaning-layman tone
- Resolving hyperlinks for benchmarks, datasets, simulators, and code repos
- Footer links to source code and HDR methodology
- Auto-commit and push to the website repo

**Do not write `summary.md` in the project directory.** It is deprecated; the pipeline owns the public version.

---

## Phase 3.5: Adversarial Paper Review

**Mandatory. Do not skip. The paper must survive independent review before publication.**

After the Phase 3 paper draft is complete, a **separate reviewer agent** reads `paper.md` in isolation — simulating a blind peer reviewer. This agent has no access to the HDR agent's conversation, `results.tsv`, or code. It sees only what a journal reviewer would see: the paper itself.

### Reviewer inputs

- `paper.md` only (plus any figures in `plots/`)
- The reviewer does NOT see `results.tsv`, `review.md`, `knowledge_base.md`, or code

### Review protocol

The reviewer produces `paper_review.md` with findings in these categories:

**1. Claims vs evidence.** For every quantitative claim in the paper, does the Methods section describe an experiment that would produce that number? Are confidence intervals or noise floors reported? Flag any number that appears without methodological support.

**2. Scope vs framing.** Does the title accurately reflect the scope of the work? Does the abstract carry the same qualifiers as the Discussion? Flag any case where the headline framing omits conditions that limit the result. Example: a finding demonstrated on a single-lane ring road simulation should not be titled as if it applies to real highways.

**3. Reproducibility.** Could a reader replicate the work from the paper alone? Are all parameters specified? Is the dataset identified with version/URL? Are evaluation metrics defined precisely? Flag anything a replicator would have to guess.

**4. Missing experiments.** Based on the claims made, what obvious follow-up experiments would a reviewer demand? These are experiments the *paper itself implies should exist* but doesn't report. Examples: robustness to parameter variation, sensitivity to dataset size, generalisation to a second dataset or domain, ablation of key components.

**5. Overclaiming and language.** Check for hedging failures: "we prove" when "we find evidence for" is appropriate; "always" when "in all tested conditions" is accurate; causal language when only correlation was demonstrated.

**6. Literature positioning.** Does the paper fairly represent prior work? Are there obvious missing citations that a domain expert would notice? Does the paper claim novelty for something already published?

### Severity and response

Same severity scale as Phase 2.75 (CRITICAL / MAJOR / MINOR). Same response obligations (FIX / REBUT / ACKNOWLEDGE).

### Suggested experiments are mandatory

**This is the most important rule in the review process.** When the paper reviewer identifies missing experiments — robustness checks, sensitivity analyses, generalisation tests, ablations — the HDR agent MUST run them. These experiments are not optional follow-up work. They are required before publication.

The HDR agent:
1. Runs each suggested experiment through the standard evaluation harness
2. Adds results to `results.tsv`
3. Adds a new section or extends the Results section of `paper.md` with the findings
4. **Reports the results honestly, even if they weaken the headline.** If a robustness check fails, the paper must say so. Suppressing a negative result from a reviewer-suggested experiment is the single most damaging thing the methodology can do to its credibility.

If reviewer-suggested experiments significantly change the findings, the paper may need substantial revision — new abstract, revised conclusions, updated title. This is expected, not a failure. A paper that survives adversarial review is worth more than one that was never challenged.

### Revision cycle

1. HDR agent revises `paper.md` and writes `paper_review_response.md`
2. Reviewer gets a second pass on the revised paper
3. If all CRITICAL and MAJOR items are resolved, the reviewer signs off in `paper_review_signoff.md`
4. Maximum 3 rounds. Unresolved items after 3 rounds become mandatory entries in the Discussion/Limitations section.

### Deliverables

```
applications/<project>/
├── paper_review.md              # Reviewer's structured findings on the paper
├── paper_review_response.md     # HDR agent's responses + paper revisions
└── paper_review_signoff.md      # Final reviewer approval or noted open items
```

### Only after sign-off

The website summary pipeline should not publish a project until `paper_review_signoff.md` exists. A paper without reviewer sign-off is a draft, not a result.

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
