# Autoresearch: [YOUR SCIENTIFIC QUESTION] — HDR

**Local**: `/path/to/your/project/`
**Venv**: `source /path/to/venv/bin/activate`

---

## GLOBAL RULE

**EVERY phase in this document MUST be completed on EVERY project. NO EXCEPTIONS.**

Every project is classified into one of **two target types** before work begins:

- **exploratory** — internal analysis, no novelty gates. Phase 0 runs at compact scale. Website summary still produced.
- **publication-target** — manuscript for a named journal. Novelty gates (Phase −0.5, Phase 0.25) and all methodology gates are mandatory.

**Both types always produce a website summary** at `~/website/site/content/hdr/results/<slug>/` upon completion.

The target type is declared on the first line of `README.md`: `**Target type**: exploratory` or `**Target type**: publication-target`. Default is exploratory. Projects can be promoted by retroactively running Phase −0.5 and Phase 0.25.

### Phase Matrix

| Phase | exploratory | publication-target |
|---|---|---|
| −0.5 (scope check) | skip | **required** |
| 0 (lit review) | compact (30–80 citations, 2–4 themes, ≥ 20 hypotheses) | **full (200+ citations, 7 themes, 100+ hypotheses)** |
| 0.25 (publishability review) | skip | **required** |
| 0.5 (baseline + data smoke test) | **required** | **required** |
| 1 (tournament) | **required** (≥ 2 families) | **required** (≥ 4 families) |
| 2 (HDR loop) | **required** (≥ 10 experiments) | **required** (≥ 20) |
| 2.5 (pairwise interaction sweep) | optional | **required** |
| 2.75 (adversarial results review) | **required** | **required** |
| 3 (paper.md) | **required** (short-form acceptable) | **required** (full academic form) |
| 3.5 (adversarial paper review) | **required** | **required** |
| B (discovery) | optional | **required** |
| Publish (website summary) | **required** | **required** |

### Phase Exit Criteria (machine-checkable, BLOCKING)

A phase is **complete** only when the named artifact exists on disk AND the content marker is inside it.

| Phase | Required artifact(s) | Content marker / rule |
|---|---|---|
| all | `README.md` | First line declares target type |
| **−0.5** (pub only) | `proposal.md` + `scope_check.md` | `scope_check.md` ends with `VERDICT: PROCEED`; written by a **different sub-agent** |
| 0 | `papers.csv` + `literature_review.md` + `knowledge_base.md` + `research_queue.md` + `design_variables.md` | Pub: ≥ 200 citations, ≥ 100 hypotheses. Exploratory: ≥ 30 citations, ≥ 20 hypotheses |
| **0.25** (pub only) | `publishability_review.md` | All five checklist sections answered; ends with `VERDICT: PROCEED`; **different sub-agent** from Phase −0.5 |
| 0.5 | `E00` row in `results.tsv` + `data_sources.md` | Real data only; seed-stable. Option D: CAS versions + textbook reproduction |
| 1 | `results.tsv` + `tournament_results.csv` | Pub: ≥ 4 families. Exploratory: ≥ 2. Both include linear-model sanity check. Option D: ≥ 3 frameworks incl. textbook baseline |
| 2 | Rows in `results.tsv` with `status` ∈ {KEEP, REVERT} | Pub: ≥ 20 rows. Exploratory: ≥ 10. Every KEEP tied to a commit |
| 2.5 (pub required) | Pairwise-interaction rows in `results.tsv` | Top-N near-miss features tested |
| **2.75** | `paper_review.md` + reviewer experiments in `results.tsv` | **Different sub-agent**; "documented in §Limitations" is NOT valid completion |
| 3 | `paper.md` | References each KEEP experiment by ID |
| **3.5** | `paper_review_signoff.md` | Contains literal `NO FURTHER BLOCKING ISSUES`; **different sub-agent** from Phase 2.75 |
| B (pub required) | `phase_b_discovery.py` output | Actual discovery outputs, not more training runs |
| Publish | `~/website/site/content/hdr/results/<slug>/index.md` | Requires `paper_review_signoff.md` first. Hugo build passes. |

### Anti-Pattern Watchlist

- Marking Phase 2.75 "complete" by inlining limitations into `paper.md §8` — the reviewer is a **blind independent agent**, not the author
- Publishing to the website before `paper_review_signoff.md` exists
- Claiming a "champion" on a random-split holdout without temporal-split confirmation
- Claiming novelty when hardware resolution is ≥10× below published frontier — call it replication

### Forbidden Shortcuts (apply to ALL phases)

These have been observed in practice. Each is FORBIDDEN regardless of project type. **VIOLATION OF ANY IS A MANDATORY PAUSE OR RETRACTION:**

- Skipping any required phase ("this project is descriptive-only / simple / a clone")
- Self-reviewing ("I'll play the reviewer role") — reviewer MUST be a different sub-agent invocation
- Skipping reviewer because "tight on context budget" — PAUSE the project instead
- "Inlined reviewer concerns in limitations section" — not a substitute for running the experiment
- Publishing before `paper_review_signoff.md` contains `NO FURTHER BLOCKING ISSUES`
- Running Phase 0.25 on the same sub-agent that did Phase −0.5
- "Went straight from analysis to website" — paper.md + Phase 3.5 signoff still required
- Combining phases or reusing artifacts from another project's phases

**If an artifact cannot be created due to a genuine external blocker, the project is PAUSED — not published.**

---

## Core Principle

**The goal is DISCOVERY, not model-fitting.** A model is infrastructure. The novel result is what the model finds.

Every project has two phases:
- **Phase A (Infrastructure, <30% of effort)**: Build predictor/simulator, validate on known cases
- **Phase B (Discovery, >70% of effort)**: Use the tool to explore the unknown

---

## Objective

### Option A: Dataset-Based
Maximise **[METRIC]** on [BENCHMARK] via HDR. Then USE the model for discovery.

### Option B: Simulation-Based
Optimise **[OBJECTIVE]** by modifying **[DESIGN VARIABLES]** evaluated via **[SIMULATOR]**.

### Option C: Decomposition-Based
Reverse-engineer an existing AI-discovered or black-box solution. Identify which components carry the win, which are artifacts, and what mechanism explains the performance. Uses systematic ablation. See "Phase 2 Variant: Decomposition Loop" below.

### Option D: Symbolic/Analytical
Derive, verify, or classify **mathematical expressions** using a CAS as the evaluation oracle. Appropriate when the primary output is a symbolic expression, classification, or proof. See "Appendix: Option D Variants" at end of document.

**When to use D (not B):** Primary output is symbolic, evaluation is constraint satisfaction (not optimisation), search space is qualitatively different frameworks, result includes analytical bounds or symmetry classifications.

---

## Novelty Gates (Phase −0.5 and Phase 0.25, publication-target only)

These two gates catch novelty weakness and venue mismatch before expensive computation begins. Both share the same mechanics: a fresh sub-agent reviewer produces a verdict file; the researcher may reframe up to twice before auto-KILL.

**Shared verdict mechanics:**
- **PROCEED** → project continues; reviewer's killer objections added to `research_queue.md`
- **REFRAME** → proposal rewritten addressing specific points; re-reviewed by fresh sub-agent. Max 2 reframe cycles; 3rd non-PROCEED is auto-KILL
- **KILL** → downgrade to exploratory or abandon. Decision recorded in verdict file.

### Phase −0.5: Scope Check

Runs before Phase 0 (no lit review yet). The researcher writes `proposal.md` — a single page with five sections, each ≤ 1 paragraph:

1. **Question.** One sentence.
2. **Proposed contribution.** Concrete enough to judge novelty.
3. **Why now.** What motivating development makes this timely.
4. **Falsifiability.** The specific outcome that would kill the result.
5. **Target venue.** Primary venue + one reason it fits.

The scope-check reviewer is a fresh sub-agent reading only `proposal.md`. Prompt template at `prompts/scope_check_reviewer.md`. Produces `scope_check.md` ending with a VERDICT.

### Phase 0.25: Publishability Review

Runs between Phase 0 and Phase 0.5. The reviewer reads `proposal.md`, `literature_review.md`, `knowledge_base.md`, `research_queue.md`, and `scope_check.md`. Does NOT see `papers.csv` or code. Must be a **different sub-agent** from Phase −0.5.

Produces `publishability_review.md` answering five mandatory sections:

**1. Novelty taxonomy.** Categorise as: *extension*, *synthesis*, *application*, or *genuinely new*. For anything other than genuinely new, name the specific prior work. For genuinely new, list the 5 closest existing papers.

**2. Falsifiability.** Name the specific measurable kill-outcome. Unfalsifiable-in-disguise patterns: "tends to increase", "is consistent with observation", "accounts for", "bridges frameworks".

**3. Load-bearing parameters.** List every numerical parameter the headline depends on, with: value used, literature-consensus uncertainty, and how the headline scales in that parameter. Flag any parameter whose uncertainty makes the headline unstable.

**4. Venue fit.** Name 2-3 candidate journals with one reason each is a fit and one typical objection class.

**5. Killer objections.** Top three objections scored fatal/major/minor with mitigation plans. **Any fatal objection without clear mitigation → REFRAME.**

On PROCEED, the top three killer objections are added to `research_queue.md` with flag `pre-empt-reviewer`.

---

## Phase 0: Literature Review

### Deliverables
1. `literature_review.md` — 7 themes (compact: 2-4), 3000+ words each
2. `papers.csv` — 200+ entries (compact: 30+). Composition: 5–10 textbooks, 10–20 reviews, 60–100 recent results, 30–60 methods, 20–40 cross-disciplinary
3. `feature_candidates.md` / `design_variables.md` — domain quantities → computable proxies
4. `research_queue.md` — 100+ hypotheses (compact: 20+), each with design variable, expected outcome, metric, baseline, Bayesian prior
5. `knowledge_base.md` — established results, what works, what doesn't

### Themes
1. Domain fundamentals (textbooks, governing equations)
2. Phenomena of interest (mechanisms, precursors)
3. Candidate features / design variables
4. ML/optimisation for this problem
5. Objective function design / feature engineering
6. Transfer / generalisation across conditions
7. Related problems (cross-domain insights)

### Quality Gate
- 200+ papers.csv entries with 5+ textbooks, 10+ reviews
- 15+ candidate features/variables with physics justification
- 100+ hypotheses in research_queue.md
- The saturation heuristic below has been satisfied

### Saturation Heuristic (when to stop)

Three independent checks; stop when all three are satisfied:

1. **Marginal information gain.** Stop when 20 consecutive new fetches add zero new facts to `knowledge_base.md`.
2. **Citation-graph closure.** 90% of any new paper's references are already in `papers.csv` (rolling average over last 10 papers).
3. **Standard textbook coverage.** Every chapter heading in the canonical textbook has ≥ 3 representative papers in `papers.csv`.

**Do not stop early because the count crossed a threshold.** A 250-citation review where 80% of fetches still add new facts is INCOMPLETE. A 180-citation review where saturation is reached is COMPLETE.

---

## Phase 0.5: Baseline Audit

1. Read all code — find bugs, suboptimal defaults
2. Decompose the score — where does improvement effort have highest ROI?
3. Validate the validation — does it predict real-world performance?
4. Audit data/simulation fidelity
5. Missing data audit — what proxies exist?
6. Record baseline in `results.tsv` as `E00`

### Sanity Checks Before HDR Loop

1. **Reproduce published SOTA** on the same system within 0.1–0.5%. A larger gap means your setup is broken.
2. **Featurizer speed audit at 500 samples.** Cache featurization output to disk on first run.
3. **Validation must not overlap training.** Run leave-one-condition-out CV alongside holdout. Trust the leave-one-out if they disagree.
4. **Linear baseline first.** If tree methods are not >2× better than Ridge/Logistic, skip neural models.

### Use Published Simulators and Datasets — CRITICAL

Always use the standard published simulator/dataset. Never build a custom one unless genuinely no standard tool exists.

**Acceptable speed tradeoffs:** Lower fidelity, published surrogate models, GPU acceleration, caching.
**Unacceptable:** Reimplementing for speed, replacing complex physics with simple analytical models.

### REAL DATA ONLY — CRITICAL

Always download real data first. Synthetic is acceptable ONLY when: (a) real data genuinely doesn't exist in downloadable form, (b) the project can't proceed without it, (c) the lit review confirms no open dataset exists. When synthetic IS the only option, label all results as conditional. Simulation-based projects (Option B) are exempt — running a physics simulator is the project's evaluation method by design.

**If you find yourself writing `np.random` to generate training data for a project that has a real dataset in `data_sources.md`, STOP.**

---

## Phase 1: Tournament

Compare ≥4 fundamentally different approaches (exploratory: ≥2) with ~5 experiments each on the same features/data. Record in `tournament_results.csv`. Select 1-2 winners. Always include a **linear-model sanity check**. Re-run the tournament if HDR loop plateaus (5+ consecutive reverts).

### Tournament Anti-Patterns
- **Bagging beats boosting for small N.** When N < 400, ExtraTrees/RF typically beats XGBoost/LightGBM.
- **Per-task model selection is mandatory.** Don't pick one family for the whole project.
- **Hard thresholds beat soft blends for bimodal targets.**

---

## Phase A → Phase B Bridge

Before Phase B, verify:
- Feature availability check on 5-10 synthetic candidates spanning the design space (no feature defaults to placeholder)
- Predictor returns scores in same range on candidates as on training data
- Stability/feasibility post-filter implemented
- Combinatorial template inventory (≥3 template families)

**Combinatorial template diversity beats predictor improvement.** Going from 1 template family to 5 typically yields 2–10× more discoveries.

---

## Phase 2: The HDR Loop

```
1. Pick Question        ← highest-impact OPEN from research_queue.md
2. State Prior          ← probability (0-100%) BEFORE testing
3. Articulate Mechanism ← WHY would this work? Causal story.
4. Implement ONE Change ← git commit BEFORE running
5. Evaluate             ← run on ALL tasks
6. Record Results       ← append to results.tsv (no cherry-picking)
7. Update Beliefs       ← keep or revert
8. Update Knowledge     ← knowledge_base.md, research_queue.md
```

**Target: 100+ experiments minimum.** The 20-experiment floor is a compact bar; aim for 300–1000+ with rich research queues.

### Experiment Priority
1. Fix bugs (highest ROI)
2. Domain-informed features / design parameterisations
3. Data utilisation / simulation fidelity
4. Training improvements
5. Architecture changes
6. Speed optimisation

### Hypothesis Selection: Impact Scoring

| Axis | 1 (low) | 2 (medium) | 3 (high) |
|------|---------|------------|----------|
| **Expected Δ** | < noise floor | 1–3× noise | > 3× noise |
| **Novelty** | Standard, well-explored | Published but untested here | No prior work |
| **Mechanistic clarity** | "Might help" | Plausible causal story | Clear mechanism with literature support |

**Impact = Expected Δ + Novelty + Mechanistic clarity** (3–9). Break ties by prior closest to 0.5 (max information gain). **Long-shot quota:** ≥ 20% of hypotheses must have prior ≤ 0.3.

### Saturation Heuristic (when to stop)

1. **Sustained revert streak.** 20 consecutive reverts → re-tournament or stop.
2. **Research-queue exhaustion.** Fewer than 5 OPEN hypotheses all with prior < 20% → add 20+ new hypotheses or stop.

### Prior Discipline

- **Calibration.** Every 20 experiments, bin priors into buckets and compare to actual KEEP rate. If 0.7–1.0 bucket has KEEP < 0.4, deflate all future priors by 0.7×. If 0–0.3 bucket has KEEP > 0.5, raise long-shot quota to 30%.
- **Queue ordering.** Equal impact → prefer prior closest to 0.5.
- **Posterior updating.** KEEP → multiply related priors by 1.5 (cap 0.95). REVERT → multiply by 0.5. Retire clusters converging to < 0.1.
- **Known biases.** Training-trick priors overconfident (default ≤ 30%). Domain-feature priors well-calibrated. Architecture-pivot priors catastrophically overconfident (~10% real success). Inference optimisations reliable and stackable.

### Principles
- **Domain-first**: every hypothesis grounded in domain science
- **Isolation**: one change per experiment
- **Bayesian**: state beliefs before data, update after
- **Cumulative**: every experiment produces knowledge
- **Plateau detection**: distinguish optimisation plateau (re-tournament) from physical floor (pivot to new problem dimension)
- **Tighten revert threshold late-loop**: early (any positive Δ), mid (>2× noise), late (>3× noise OR parallel benefit)

### Mandatory Lookalike-Placebo for Reporting-Channel Outcomes

When the outcome is observed via a reporting mechanism (filings, permits, claims, scrapes), Phase 2 MUST include a lookalike placebo: fit propensity model, take top-N untreated by propensity score, compare their outcome rate against the remaining untreated pool. A large gap (|RD| > 10pp, CI excludes zero) means the matched controls are channel-selected and the primary ATT is biased. Report prominently; do not skip.

### Anti-Patterns
- "Slightly tied" complex variants → revert (Occam wins)
- Per-scenario regressions hiding under positive means → always report per-task results
- Rules of form `improvement > K%` don't scale — prefer absolute conditions
- Random init for parameterised search → always warm-start from known-good baseline
- Cache custom featurization on first run

### Interaction Sweep (Phase 2.5)

After Phase 2 converges, before writing the paper. Collect near-miss rejects (within 1× noise of KEEP threshold). Test all pairs (N×(N-1)/2, N ≤ 8). Escalate winners. If no near-misses exist, run at least one interaction test between top-2 KEEPs.

### Phase 2 Variant: Decomposition Loop (Option C)

Replace the standard HDR loop with:

```
1. Pick component to ablate       ← from structured list of all components
2. State expected effect           ← essential / important / redundant
3. Ablate one thing                ← set to 0/infinity/remove; commit first
4. Measure performance change      ← <1.2× = redundant, 1.2–2× = important, >2× = essential
5. Cross-validate                  ← second simulator or published results
6. Rebuild minimal essential design
7. Re-optimise simplified design
8. Survey solution family          ← repeat on 3–5 solutions; classify by mechanism
```

Rules: component ablation before parameter sweeps; distinguish narrow optima from broad robustness; cross-validate against independent source; verify simplified design matches or beats original.

---

## Adversarial Review Protocol (Phase 2.75 and Phase 3.5)

Both phases use the same structure: a **fresh sub-agent** (no access to the HDR agent's conversation) reads project artifacts and produces a structured review. The HDR agent must respond to every finding and run every suggested experiment.

### Severity Scale

| Severity | Definition | Obligation |
|----------|-----------|------------|
| **CRITICAL** | Result wrong or unreproducible | Must fix before proceeding |
| **MAJOR** | Overclaim, missing qualifier, significant gap | Must fix or rebut with experimental evidence |
| **MINOR** | Style, clarity, nice-to-have experiment | Should fix; may acknowledge as limitation |

### Response Protocol

Each finding gets one of:
- **FIX** — change code, re-run experiment, or revise claim. Show the diff or new result.
- **REBUT** — cite a specific experiment by ID that contradicts the finding. "I disagree" without evidence is invalid.
- **ACKNOWLEDGE** — add to limitations.

### Suggested Experiments Are MANDATORY

**When the reviewer proposes missing experiments, the HDR agent MUST run them.** They are added to `research_queue.md` with priority above all queued hypotheses. Results are reported honestly even if they weaken the headline. Suppressing a negative result from a reviewer-suggested experiment is the single most damaging thing the methodology can do to its credibility.

### Revision Cycle

Max 3 rounds. If all CRITICAL and MAJOR items resolved, reviewer signs off. Unresolved items after 3 rounds become mandatory Discussion/Limitations entries.

### Phase 2.75: Results Review

**Runs after Phase 2.5, before writing the paper.**

**Reviewer inputs:** `results.tsv`, `knowledge_base.md`, `research_queue.md`, `literature_review.md`, model code, data.

**Review protocol:**
1. **Reproducibility check.** Re-run 5 random experiments; verify numbers match.
2. **Cherry-picking audit.** Compare git commits to `results.tsv` rows; verify REVERTs recorded.
3. **Overclaiming check.** Trace every claim in `knowledge_base.md` to an experiment.
4. **Statistical validity.** Check improvements exceed noise floor; check for per-task regressions.
5. **Missing experiments.** Propose 5–10 experiments the HDR agent should have run.
6. **Scope and framing audit.** Check headline carries appropriate qualifiers.

**Deliverables:** `paper_review.md`, `review_response.md`, `review_signoff.md`

### Phase 3.5: Paper Review

**Runs after Phase 3 paper draft, before Phase B or Publish.**

**Reviewer inputs:** `paper.md` only (plus `plots/`). Does NOT see `results.tsv`, code, or `knowledge_base.md`.

**Review protocol:**
1. **Claims vs evidence.** Every quantitative claim supported by Methods?
2. **Scope vs framing.** Title/abstract carry same qualifiers as Discussion?
3. **Reproducibility.** Could a reader replicate from the paper alone?
4. **Missing experiments.** What follow-ups does the paper itself imply?
5. **Overclaiming and language.** "We prove" vs "we find evidence for"; causal language for correlational results.
6. **Literature positioning.** Fair representation of prior work? Missing citations?

**Deliverables:** `paper_review.md`, `paper_review_response.md`, `paper_review_signoff.md`

`paper_review_signoff.md` must contain `NO FURTHER BLOCKING ISSUES`. **Publishing before this exists is a retraction-grade failure.**

---

## Phase 3: paper.md

A publication-quality academic paper. Structure:

1. **Abstract** — 200-300 words
2. **Introduction** — context, prior work, the gap
3. **Detailed Baseline** — mathematical formulation, origin, assumptions, parameter values, known failure modes. Reader can reproduce.
4. **Detailed Solution** — final discovered solution in equivalent depth. Code block for code-based solutions. Causal mechanism for why it works. Reader can reproduce.
5. **Methods** — the iteration process: baseline calculation + how we iterated
6. **Results** — every kept experiment, tables and figures, quantitative findings
7. **Discussion** — physical interpretation, limitations, threats to validity
8. **Conclusion** — punchline + implications + future work
9. **References** — 30+ citations from `papers.csv`

### Writing Rules
- **Expand abbreviations on first use.** Every acronym spelled out the first time.
- **Methodology section answers two questions only:** (a) baseline + how calculated, (b) iteration approach + keep-vs-revert criterion. No citation counts, hypothesis counts, or work-effort metrics.
- **Never reference the internal review process.** No "reviewer", "sub-agent", "Phase 2.75", "blind review". Every finding from the review cycle is reported as if part of the original analysis plan.
- **Never report work-effort metrics as findings.** "We ran 34 experiments" belongs in logs, not the paper. The publishable fact is what was tested and what the result was.

### Plots (mandatory)

`generate_plots.py` produces all PNGs (300 DPI) to `plots/`. Must be runnable standalone from cached data.

**Three mandatory plots:**
1. Predicted vs actual scatter (with 1:1 reference line)
2. Feature importance (top 10-15, horizontal bar)
3. Headline finding visualised

**Conditional plots:** Add when the trigger applies — waterfall for multiple KEEPs, Pareto scatter for Phase B, choropleth for geographic data, time series for temporal data, side-by-side for competing hypotheses.

Style: `matplotlib`, colourblind-safe palettes, labelled axes with units, max 8-10 plots per paper.

### Public Summary (auto-generated)

The website summary pipeline at `~/website/pipeline/` regenerates summaries from `paper.md`. Do not write `summary.md` by hand. Hard constraints and craft rules for summaries are defined in `~/website/pipeline/hdr_summary_pipeline.md`.

---

## Phase B: Discovery

**Phase B is not "run more training experiments". It is "use the tool to explore the unknown".** Output: ranked list, discovered candidate, flagged anomaly, Pareto front, or specification — not another tournament row.

For descriptive projects: Phase B is a rank-list output written to `discoveries/`. For Option D projects: see Appendix.

**Artifacts:** `phase_b_discovery.py` (standalone), `discoveries/` directory, ≥1 `status=DISCOVERY` row in `results.tsv`.

---

## Phase Publish: Website Summary

**NOT permitted unless:**
- `paper_review_signoff.md` exists AND contains `NO FURTHER BLOCKING ISSUES`
- `paper.md` revised to incorporate all mandated changes
- Phase B output exists (publication-target)
- Hugo build passes locally
- Git commit and push to `colinjoc.github.io`

---

## Novelty Checklist

Before declaring done:
- [ ] Results exceed published SOTA (or match with simpler/faster/more robust method)
- [ ] At least one surprising finding
- [ ] Knowledge base contains insights valuable to other researchers
- [ ] Paper.md drafted with all required sections

---

## Repository Hygiene

**The git repo must contain ONLY code and markdown — never data files, never paper PDFs.** Maintain a `.gitignore` excluding `data/`, `literature/`, `venv/`, `__pycache__/`, model weights, and large CSVs. Every external data source documented in `data_sources.md` with URL, size, checksum, license, local path, and download command.

---

## Constraints

- ONE change per experiment
- ALWAYS test on small data before full runs
- ALWAYS commit before evaluation
- ALWAYS record in results.tsv
- ALWAYS use GPU if available
- Ground every hypothesis in domain science
- NEVER stop — keep iterating until the human stops you

---

## Appendix: Option D Variants (Symbolic/Analytical)

### Objective
Establish whether **[MATHEMATICAL STRUCTURE]** satisfies **[CONSTRAINT SET]** under **[PARAMETER REGIME]**, and identify the minimal structure and parameter bounds.

### Phase 0.5: Symbolic Verification

Before the HDR loop, verify the CAS pipeline:
1. **Reproduce a textbook result** — if the CAS gives wrong answers on known cases, everything downstream is suspect.
2. **Grid convergence test** — 3 resolutions, result changes < 1%. Record as `E00_convergence`.
3. **Simplification sanity check** — compare unsimplified vs simplified at 5 test points.
4. **Dimension/unit consistency** — verify every term has consistent dimensions.

`E00` records the baseline framework with constraint satisfaction status. `data_sources.md` lists CAS libraries with versions and reference results.

### Phase 1: Framework Tournament

Compare ≥3 fundamentally different mathematical frameworks (different field equations, symmetry groups, dimensionality). Include the textbook/standard framework as baseline. Record: framework name, constraint satisfaction, margin, CAS wall time, expression complexity (term count). Select 1-2 winners.

### Phase 2: Symbolic Analysis Loop

```
1. Pick structure to test          ← ansatz modification, coupling term, boundary condition
2. State prior                     ← probability of constraint satisfaction
3. Articulate mechanism            ← sign argument, symmetry argument, dimensional argument
4. Implement ONE symbolic change   ← modify ansatz; commit first
5. Evaluate symbolically           ← CAS → check constraints → grid-evaluate if needed
6. Record results                  ← append to results.tsv
7. Update beliefs                  ← KEEP or REVERT
8. Update knowledge                ← knowledge_base.md gains a symbolic fact
```

**Results schema:** `experiment_id | description | constraint | margin | status | symbolic_result | notes`. Positive margin = satisfied, negative = violated.

**Rules:**
- **Sign arguments before parameter sweeps** — wrong sign will never help regardless of parameters
- **Limiting cases as free theorems** — evaluate in ≥ 2 limits; if wrong, implementation has a bug
- **Simplification is an experiment** — often reveals the essential mechanism
- **Expression complexity as secondary metric** — prefer simpler between two that both satisfy
- **Cross-validate symbolically with numerics** — spot-check at ≥ 5 test points
- **Parameter-regime mapping** — after structural confirmation, map the full boundary where constraint satisfaction flips

### Phase B: Analytical Discovery

Produces one or more of:
1. **Minimal sufficient structure** — fewest terms that still satisfy the constraint
2. **Analytical bounds** — closed-form expressions for the satisfying parameter regime
3. **Classification of solution families** — by mathematical mechanism
4. **Conjectures and proof sketches** — with supporting evidence
