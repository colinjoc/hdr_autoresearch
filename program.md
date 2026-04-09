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

---

## Phase 0: Literature Review

**Do not skip. 100+ citations minimum.**

### Deliverables
1. `literature_review.md` — 7 themes, 2000+ words each
2. `papers.csv` — 100+ entries (3-5 textbooks, 5-10 reviews, 30-50 recent, 20-30 methods)
3. `feature_candidates.md` / `design_variables.md` — domain quantities → computable proxies
4. `research_queue.md` — 20+ hypotheses, each traced to a paper
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
- [ ] 100+ papers.csv entries with 3+ textbooks, 5+ reviews
- [ ] 15+ candidate features/variables with physics justification
- [ ] 20+ hypotheses in research_queue.md
- [ ] Can explain the domain physics without notes

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
- Results from custom simulators are **not comparable** to published benchmarks. You can't claim "we beat SOTA" unless you tested on the same simulator SOTA was measured on.
- Custom simulators tend to encode the same simplifications as the analytical baselines they replace (e.g., a Poisson + saturation flow traffic simulator IS Webster's model — beating Webster on it means nothing).
- Custom simulators miss the physics that matters in reality. The optimisation will find solutions that exploit simulator artifacts rather than real phenomena.
- Reviewers and replicators will not trust results from a one-off simulator built by the same person making claims about it.

**The rule:**
1. **Identify the standard simulator/dataset** for your field during Phase 0 lit review. Examples: SUMO for traffic, GROMACS for molecular dynamics, OpenAI Gym envs for RL, MuJoCo for robotics, Quantum ESPRESSO for DFT, FENICS for FEM, OpenFOAM for CFD, the UCI/Kaggle/papers-with-code dataset for the benchmark.
2. **Use it.** Even if it's 100x slower than a custom alternative.
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

**Lesson from the traffic signals project**: The HDR agent built a Poisson+saturation flow simulator instead of using the available SUMO installation. The 43% improvement over Webster on the custom simulator was meaningless because the custom simulator IS Webster's analytical model. Results that look impressive on toy simulators do not transfer to standard benchmarks. Always use the standard tool.

---

## Phase 1: Tournament

Compare 3-5 **fundamentally different** approaches (not hyperparameter variants) with ~5 experiments each on the same features/data. Record in `tournament_results.md`. Select 1-2 winners for the HDR loop.

Re-run the tournament if the HDR loop plateaus (5+ consecutive reverts).

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
8. Update Knowledge     ← knowledge_base.md, research_queue.md, observations.md
```

### Experiment Priority
1. Fix bugs (highest ROI)
2. Domain-informed features / design parameterisations
3. Data utilisation / simulation fidelity
4. Training improvements
5. Architecture changes
6. Speed optimisation

### Principles
- **Domain-first**: every hypothesis grounded in domain science
- **Isolation**: one change per experiment
- **Bayesian**: state beliefs before data, update after
- **Cumulative**: every experiment produces knowledge, even failures
- **Plateau = explore**: 5+ reverts → new approach, not more tuning

---

## Phase 3: Two Writeups

After the HDR loop converges (improvements plateau OR novelty checklist satisfied), produce **two writeups** as the final deliverables: a formal academic paper for credibility, and a website summary for reach.

### Output 1: `paper.md` — Formal academic paper

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

### Output 2: `summary.md` — Website-ready summary

A condensed, approachable version of the paper for the public-facing website. The same findings, communicated to a smart generalist audience rather than a domain expert.

**Structure** (use Hugo frontmatter):
```yaml
---
title: "Short, punchy title"
date: YYYY-MM-DD
domain: "Field name"
headline: "One-sentence punchline that fits in a card"
metric_name: "What was improved"
metric_value: "By how much"
tags: ["domain", "method", "topic"]
---
```

**Body sections**:
1. **The Problem** — 1-2 paragraphs. What is this, why does it matter, what was the gap.
2. **What We Found** — the headline result up front, with a number. Then the supporting findings as bullet points or a table.
3. **Key Insights** — 3-7 bullet points. Each one is a specific, surprising finding. Use numbers, not adjectives.
4. **Why This Matters** — practical implications. Who uses this? What changes?
5. **Methodology** — short paragraph or bullet list. How many experiments, what tools, link to the formal paper.
6. **Key References** — 3-5 of the most important citations with links.

**Style**:
- Bullet points over prose
- Tables over paragraphs
- Numbers over adjectives ("3.4× faster" not "significantly faster")
- One sentence per idea
- Lead with the answer, then the explanation
- A smart generalist should understand it in under 5 minutes

### Both files go in the project directory

```
applications/[project]/
  paper.md      # for credibility — the formal academic version
  summary.md    # for reach — the public-facing version
```

The `summary.md` content gets copied or symlinked into the website's `content/hdr/results/[project].md` for publication.

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

Example entry:
```markdown
## UCI Concrete Compressive Strength
- URL: https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
- Size: 56 KB
- License: CC BY 4.0
- Local path: data/concrete.csv
- Fetch: `python -c "from sklearn.datasets import fetch_openml; fetch_openml(data_id=4353, as_frame=True).frame.to_csv('data/concrete.csv', index=False)"`
```

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
