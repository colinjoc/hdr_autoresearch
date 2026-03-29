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

## The HDR Loop

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

### Principles

- **Domain-first**: Every hypothesis should be grounded in domain science. The literature review ensures this.
- **Bayesian discipline**: State beliefs before looking at data. Let data update beliefs.
- **Isolation**: One change per cycle. If you change two things, you don't know which helped.
- **No overfitting**: Simpler is better. If a small param change destroys the model, it's overfit.
- **Cumulative knowledge**: Every cycle produces knowledge, even failures. The knowledge base prevents re-testing dead ideas.
- **Cross-task awareness**: Always evaluate on ALL benchmark tasks. A feature that helps one subset but hurts another is suspect.
- **Autonomous operation**: Every decision is logged and reversible.

---

## File Structure

```
program.md              # This file -- instructions + methodology
literature_review.md    # Comprehensive literature review (Phase 0 output)
feature_candidates.md   # Domain quantities -> computable proxies
papers.csv              # Paper/book tracking spreadsheet
observations.md         # Signal ideas and data gaps
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
pip install numpy scikit-learn pandas xgboost
# Add any domain-specific packages
```

---

## Constraints

- ONE change per experiment (isolation principle)
- ALWAYS commit before running evaluation
- ALWAYS record results in results.tsv
- ALWAYS evaluate on ALL benchmark tasks (not just best-case)
- Ground every hypothesis in domain science or ML theory
- NEVER stop -- keep iterating until the human stops you
