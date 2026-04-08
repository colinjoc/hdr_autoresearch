# Autoresearch as Derivative-Free Optimization in Program Space

## 1. The Core Abstraction

Autoresearch is **LLM-guided derivative-free optimization** where the search space is programs and the surrogate model is an LLM.

### Formal Definition

An autoresearch problem is a tuple **(P, E, I, T)** where:

- **P** is a **program space** — the set of all valid programs conforming to a fixed interface (e.g., a `Strategy` class with `train()` and `on_bar()` methods)
- **E: P → ℝ** is an **evaluation oracle** — a deterministic (or low-variance) function that executes a program and returns a scalar metric
- **I** is an **information structure** — the interface specification, domain knowledge, and experiment history available to the search operator
- **T** is a **time budget** per evaluation

The objective is to find:

> **p\* = argmax_{p ∈ P} E(p)**

subject to: each evaluation E(p) completes within time budget T.

### The Three Fixed Components

Every autoresearch instance has the same architecture:

| Component | Role | Formal element |
|-----------|------|----------------|
| `program.md` | Defines the search space constraints and domain knowledge | **P** (constrains which programs are valid) and **I** (provides the LLM with domain priors) |
| `prepare.py` / `backtest.py` | Implements the evaluation oracle | **E** |
| `strategy.py` / `train.py` | The current point in program space being edited | **p ∈ P** |

The commit/revert mechanism ensures **monotonic improvement**: the current program p_best is only replaced when E(p_new) > E(p_best).

---

## 2. Relationship to Standard DFO

### Standard Derivative-Free Optimization

In classical DFO, the search space is a parameter vector **x ∈ ℝ^n** and the objective f(x) is a black-box function. The standard toolkit:

- **Direct search** (Nelder-Mead, pattern search) — geometric exploration
- **Model-based** (Bayesian optimization) — fit a surrogate (Gaussian process), use an acquisition function to balance exploration and exploitation
- **Population-based** (CMA-ES, evolutionary strategies) — maintain a population, mutate, select
- **Random search** — competitive in high dimensions (Bergstra & Bengio 2012)

All of these assume the search space has a **topology** where nearby points (in Euclidean distance) tend to have similar objective values. Convergence guarantees require **smoothness** — typically Lipschitz continuity.

### Why Program Space Breaks the Standard Framework

Autoresearch searches over **programs**, not parameter vectors. This breaks classical DFO assumptions:

**No natural distance metric.** Three notions of program proximity exist, and they don't align:

| Distance | Definition | Problem |
|----------|-----------|---------|
| Edit distance (syntactic) | Character-level differences | Changing `>` to `>=` is 1 character but can flip behavior entirely |
| AST edit distance (structural) | Tree operations on the parse tree | Structurally similar programs can have opposite behavior |
| Semantic distance (behavioral) | Divergence in outputs | Programs that look nothing alike can behave identically |

A Gaussian process surrogate over Levenshtein distance is meaningless — syntactic proximity does not imply behavioral proximity.

**Discontinuous landscape.** The objective E(p) over program space is riddled with cliffs, plateaus, and disconnected basins. A single-character change can crash the program, change the algorithm entirely, or have zero effect. Standard convergence proofs (which require continuity) do not apply.

**Hierarchical and combinatorial structure.** A program is not a vector of independent parameters. It is a tree of nested decisions: which algorithm, which features, which control flow, which constants. Changing a high-level decision (e.g., switching from RSI to XGBoost) reshapes the entire sub-space of meaningful lower-level changes.

---

## 3. The LLM as Acquisition Function

In Bayesian optimization, the **acquisition function** (Expected Improvement, Upper Confidence Bound, etc.) uses a surrogate model to answer: *"Where should I evaluate next to maximize expected improvement?"*

The LLM serves an analogous role:

| | Bayesian Optimization | Autoresearch |
|---|---|---|
| **Surrogate model** | Gaussian process over ℝ^n | LLM's implicit world model over program space |
| **Prior** | Kernel encodes smoothness assumption | Domain knowledge from pretraining encodes structural priors |
| **Acquisition** | Analytic function balancing explore/exploit | Chain-of-thought reasoning balancing explore/exploit |
| **Dimensionality** | Struggles above ~20 dimensions | Operates in effectively infinite-dimensional space |
| **Learning** | Only from observed evaluations | Massive prior from pretraining + observed evaluations |

### The Implicit Smoothing Property

The key theoretical insight is that **the LLM implicitly operates in a learned latent representation where the objective landscape is smoother than in the raw program space**.

When the LLM considers two strategies "similar ideas" — e.g., RSI mean-reversion and Bollinger Band mean-reversion — they likely have correlated performance, even if the code is syntactically very different. The LLM navigates program space using **semantic similarity** (what the code *does*) rather than syntactic similarity (what the code *looks like*).

This implicit smoothing is what makes the search tractable in a space where traditional methods fail. The LLM's pretraining has built an internal representation of "strategy space" (or "model space", or "algorithm space") that has much lower effective dimensionality than the raw program space.

---

## 4. Relationship to Genetic Programming

The closest established field is **genetic programming (GP)**, which also searches program spaces.

| | Genetic Programming | Autoresearch |
|---|---|---|
| **Mutation** | Random subtree swap, constant perturbation | LLM-informed edit with causal reasoning |
| **Crossover** | Recombine subtrees from two programs | No explicit crossover, but LLM can mentally recombine ideas from training corpus and experiment history |
| **Selection** | Population-based (tournament, fitness-proportionate) | Greedy hill climbing (commit/revert) |
| **Representation** | S-expressions or AST nodes | Free-form code in a real programming language |
| **Domain knowledge** | None (domain-agnostic operators) | Extensive (LLM brings priors about finance, physics, ML, etc.) |

Google's **FunSearch** (Romera-Paredes et al., 2024) is the closest prior work — LLMs as mutation operators in an evolutionary algorithm, discovering novel mathematical constructions. FunSearch retained population-based selection rather than greedy hill climbing.

### The Local Optima Risk

Greedy hill climbing (commit/revert) can get stuck in **local optima**. Population-based methods maintain diversity to escape them. The LLM partially compensates by making intelligent jumps to distant regions of the search space, but there is no explicit mechanism ensuring exploration diversity.

The Bayesian hypothesis-driven extension (research queue, prior/posterior tracking) partially addresses this: the research queue forces the agent to systematically explore different structural hypotheses rather than greedily hill-climbing within a single algorithmic family.

---

## 5. Applicability Conditions

### Necessary Conditions

An autoresearch problem must satisfy:

1. **Computable evaluation.** E(p) terminates and returns a scalar for any valid p ∈ P.
2. **Fixed interface.** P is constrained by a known interface, so the evaluation harness can execute any p without modification.
3. **Text-representable solutions.** Programs in P are expressed in a language the LLM can read and modify.

### Practical Conditions (the Goldilocks Zone)

For autoresearch to be *effective* (not just applicable), the following should hold:

| Condition | Why |
|-----------|-----|
| **T is minutes, not hours** | Need ~100 iterations overnight. At 12h runtime: T < ~7 min for 100 experiments. |
| **E is deterministic or low-variance** | Noisy evaluations corrupt the commit/revert signal. If E is stochastic, you need repeated evaluation, multiplying cost. |
| **P is high-dimensional and structured** | If it's just 3 continuous parameters, use Bayesian optimization or grid search. |
| **Domain knowledge helps navigate P** | The LLM's prior must be valuable — otherwise a domain-agnostic search method works just as well. |
| **Structural changes matter** | If the solution is purely parameter tuning, Optuna or CMA-ES wins. Autoresearch shines when the *algorithm itself* needs to change. |
| **The metric faithfully captures the goal** | Goodhart's law — the loop will ruthlessly optimize whatever you measure. A bad metric produces a bad solution. |

### The Evaluation Time Constraint Visualized

```
Seconds                Minutes                   Hours                    Days
|--- brute-force ---|--- autoresearch ---|--- surrogate-assisted ---|--- manual ---|
    (10^4+ evals)       (~100 evals)         (outer: 10-50 evals)     (human-paced)
                                              (inner: fast surrogate)
```

Autoresearch occupies the middle ground: evaluation is too expensive for brute-force search, but cheap enough for ~100 informed iterations.

---

## 6. Mapping Examples to the Formalism

| Domain | P (program space) | E (evaluation) | T (budget) | Notes |
|--------|-------------------|----------------|------------|-------|
| **S&P 500 spread betting** | `strategy.py` — entry/exit logic, indicators, ML models | Cumulative return on 2025 test set | ~60s | Current implementation |
| **Disruption prediction** | Model architecture, features, thresholds | AUC / recall on held-out shots | ~minutes | Recall > precision due to domain |
| **Turbine blade CFD** | Blade geometry parameterization | Efficiency or noise from CFD sim (e.g., OpenFOAM) | ~minutes | Feasible if mesh is pre-built |
| **Materials / DFT** | Crystal structure, composition | Energy / band gap from DFT simulation | **Hours** | Likely requires surrogate model — two-level loop |
| **Drug discovery** | Molecular structure or SMILES | Binding affinity from molecular dynamics | Variable | May need fast surrogate (e.g., GNN) |
| **Neural architecture search** | Model architecture code | Validation loss after N epochs | ~minutes | Well-studied; autoresearch is strictly more expressive than fixed NAS grammars |

### The DFT / Long-Evaluation Problem

When T is too large (hours/days), autoresearch needs a **two-level approach**:

1. **Outer loop (expensive):** Run the real simulation (DFT, long CFD) to generate ground-truth data points
2. **Inner loop (autoresearch):** Train a fast surrogate model on those data points, then run autoresearch against the surrogate

The outer loop provides fidelity; the inner loop provides iteration speed. This is established practice in simulation-based optimization (surrogate-assisted optimization) and maps cleanly onto the autoresearch framework — the surrogate *becomes* the evaluation oracle.

---

## 7. Convergence: When Does It Work?

Standard DFO has convergence guarantees under smoothness. For autoresearch, the analogous question is: **under what conditions does LLM-guided program search converge to a good solution?**

Three factors determine convergence quality:

### 7.1 Quality of the LLM's Prior

How well does the LLM's domain knowledge align with the problem? If the LLM understands the domain (finance, physics, ML), it can navigate efficiently — proposing changes that are likely to help and avoiding dead ends. If the domain is genuinely novel (nothing like it in pretraining data), the LLM's search is closer to random and convergence is slow.

### 7.2 Informativeness of the Objective

A single scalar metric gives the LLM limited signal for reasoning about *why* a change helped or hurt. Richer feedback (per-trade breakdown, feature importances, loss curves, intermediate diagnostics) enables more targeted hypotheses. The `results.tsv` log and knowledge base serve this purpose — they transform a scalar signal into a structured history the LLM can reason over.

### 7.3 Smoothness in the LLM's Implicit Representation

If the LLM's internal notion of "similar strategies" actually correlates with similar performance, the search is efficient. The LLM is implicitly assuming a smooth landscape in its own latent concept space. When this assumption holds (the LLM's priors are well-calibrated), convergence is fast. When it doesn't (the domain violates the LLM's expectations), the search degrades.

---

## 8. Directions for Improvement

This formalization suggests several concrete extensions:

### 8.1 Explicit Exploration-Exploitation Balance
The current methodology relies on the LLM's judgment to balance exploration and exploitation. An explicit mechanism — e.g., periodically prompting "propose something structurally different from anything tried" or tracking coverage of the research queue — could prevent premature convergence.

### 8.2 Population / Branch-Based Search
Instead of a single commit chain (greedy hill climbing), maintain 2-3 git branches exploring different structural approaches in parallel. Periodically compare and prune. This addresses the local optima problem that greedy commit/revert is vulnerable to.

### 8.3 Multi-Fidelity Evaluation
Screen candidates with a cheap approximate evaluation (fewer epochs, subset of dates, coarser simulation) before committing to the full evaluation. This increases the effective number of iterations within the same time budget.

### 8.4 Richer Feedback Signals
Return structured diagnostics alongside the scalar metric — feature importances, per-segment breakdowns, sensitivity analysis. This gives the LLM more signal for hypothesis formation, improving the quality of each search step.

### 8.5 Surrogate-Assisted Mode for Expensive Evaluations
For domains where T is hours (DFT, long CFD), implement the two-level loop: accumulate ground-truth evaluations, train a fast surrogate, run autoresearch against the surrogate, periodically validate against the real simulation.

---

## 9. One-Line Summary

**Autoresearch is derivative-free optimization where the search space is programs, the surrogate model is an LLM, and the acquisition function is chain-of-thought reasoning. The LLM's pretrained knowledge provides an implicit smoothing of the objective landscape over an otherwise intractable combinatorial space.**
