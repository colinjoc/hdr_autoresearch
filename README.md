# HDR Autoresearch

A framework for applying **Hypothesis-Driven Research (HDR)** to any scientific prediction problem using iterative, domain-grounded machine learning experimentation.

Built for use with AI coding agents (Claude Code, etc.) that can autonomously run the HDR loop: pick a hypothesis, implement it, evaluate, and update beliefs -- all grounded in domain science rather than blind hyperparameter search.

## What is HDR?

HDR is an 8-step experiment cycle that prevents aimless hill-climbing by requiring every change to be grounded in a causal mechanism:

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

Key principles:
- **Domain-first**: Every hypothesis is grounded in science, not guesswork
- **Bayesian discipline**: State beliefs before looking at data
- **Isolation**: One change per cycle -- if you change two things, you don't know which helped
- **Cumulative knowledge**: Every cycle produces knowledge, even failures

## The Full Pipeline

### Phase 0: Literature Review

Before any experiments, a comprehensive literature review seeds the system:

- **`literature_review.md`** -- Structured review of domain papers and textbooks
- **`papers.csv`** -- Tracking spreadsheet for all reviewed sources
- **`feature_candidates.md`** -- The key bridge document: maps domain-theory quantities to computable features
- **`research_queue.md`** -- Prioritized hypotheses with priors, mechanisms, and impact ratings
- **`knowledge_base.md`** -- Established results so you don't repeat published work

### Phase 1+: The HDR Loop

Iterate through the research queue, one experiment at a time. Only `strategy.py` is modified during experiments -- everything else is infrastructure.

## File Structure

```
program.md              # Master methodology document
literature_review.md    # Literature review (Phase 0 output)
feature_candidates.md   # Domain quantities -> computable proxies
papers.csv              # Paper/book tracking spreadsheet
observations.md         # Signal ideas, data gaps, surprises
research_queue.md       # Prioritized hypotheses (OPEN / RESOLVED / RETIRED)
knowledge_base.md       # Cumulative findings (what works, what doesn't, why)
results.tsv             # One row per evaluation -- all metrics, no cherry-picking

strategy.py             # ONLY file modified during HDR (features + hyperparams)
evaluate.py             # Evaluation harness (fixed after setup)
prepare.py              # Data preparation (fixed after setup)

literature/
  papers/               # Downloaded PDFs
  books/                # Downloaded textbooks
data/
  raw/                  # Original raw data
charts/                 # Visualizations
```

## Getting Started

### 1. Clone and install dependencies

```bash
git clone https://github.com/colinjoc/hdr_autoresearch.git
cd hdr_autoresearch
pip install numpy scikit-learn pandas xgboost
```

### 2. Configure for your problem

- Fill in the `[PLACEHOLDERS]` in `program.md` with your scientific question, metrics, dataset, and baselines
- Implement data loading in `prepare.py` for your file format
- Define `BENCHMARK_TASKS` in `evaluate.py` for your evaluation splits
- Set `GROUP_IDS` in `strategy.py` if you have multiple data sources

### 3. Run Phase 0

Conduct the literature review and populate:
- `literature_review.md` with paper summaries
- `papers.csv` with tracking data
- `feature_candidates.md` with domain-to-feature mappings
- `research_queue.md` with initial hypotheses
- `knowledge_base.md` with established results

### 4. Run the HDR loop

```bash
# Prepare data (once)
python prepare.py

# Run baseline (Exp 0)
python evaluate.py

# Then iterate: edit strategy.py, commit, evaluate, record, repeat
python evaluate.py                    # All tasks
python evaluate.py --task "Task Name" # One task
python evaluate.py --quick            # Fastest task only
```

## How It Works With AI Agents

Point an AI coding agent at `program.md` and it will:

1. **Literature review**: Read papers, extract hypotheses, populate the research queue
2. **HDR loop**: Pick the highest-impact question, implement the feature/hyperparameter change in `strategy.py`, run evaluation, record results, update beliefs, and repeat
3. **Knowledge accumulation**: Build up `knowledge_base.md` so no finding is lost and no dead idea is retested

The agent modifies only `strategy.py` during experiments. Everything else is either infrastructure (fixed after setup) or documentation (append-only knowledge).

## Origin

This framework was extracted from a research project on tokamak plasma disruption prediction using the [DisruptionBench](https://github.com/MIT-PSFC/disruption-bench) benchmark (MIT PSFC, 2025). Over 8 HDR cycles, the methodology achieved:

- Mean AUC: 0.84 -> 0.93 (+11%)
- Mean F2: 0.69 -> 0.87 (+26%)
- Beat all published baselines (Random Forest, GPT-2, HDL, CCNN)

The domain-specific content was removed and the methodology generalized for any scientific prediction problem.
