**Target type**: ideation workspace (not a single project — spawns multiple publication-target projects)

# Entropy Ideation — Criticality and Edge-of-Chaos in Trained Neural Networks

## Purpose

Generate publishable, simulation-feasible research projects probing whether trained neural networks (nanoGPT, pretrained GPT-2, CNNs) operate at the edge of chaos / self-organized criticality, and how topology (skip connections, sparsity, residual paths) tunes distance-from-criticality. Each promoted idea becomes its own `applications/entropy_<slug>/` project directory with `**Target type**: publication-target`.

## Existing infrastructure

`~/entropy/` already contains:
- `nanoGPT/` — a modified nanoGPT with neuron-to-neuron skip connections as a topology knob (`n_skip_connections` ∈ {0, 100, ..., 1000}), an `ActivationAnalyzer` recording per-layer fractions of neurons with activation > threshold, and a parameter sweep across the full range.
- `gpt2_pretrained_project/` — activation analysis on HuggingFace GPT-2.
- `fashion_mnist_project/` — CNN variant for cross-architecture comparison.
- Existing sweeps at two thresholds (0 and 0.1), loss curves, activation histograms.

What's missing for an edge-of-chaos study: avalanche-size distributions, branching ratios, Lyapunov-style perturbation sensitivity, dynamic range, layer-resolved criticality, topology-vs-criticality curves.

## Constraints

- **Single consumer GPU.** All projects must run on an RTX 3060 12 GB. No multi-node training, no frontier-scale replication from scratch (pretrained models only for large-scale questions).
- **Real models first.** Use actual trained networks (the existing nanoGPT sweep, pretrained GPT-2, a trained CNN). Untrained-at-init controls are mandatory but never the headline.
- **Novelty-gated.** Each candidate goes through a Phase −0.5 scope-check against the shared literature review, run by a fresh sub-agent.
- **Deep literature first.** Per `CLAUDE.md` and `feedback_deep_literature_review.md`, ideation is driven by a real lit review spanning three fields (neuroscience, statistical physics, machine learning). Target 100+ citations at landscape stage, 200+ per promoted project.

## Pipeline

1. **Landscape lit review** (this workspace): map the three source fields, identify thematic axes, produce 10–15 candidate one-pagers.
2. **Scope-check (Phase −0.5)**: each candidate reviewed by a fresh sub-agent for novelty, falsifiability, venue fit.
3. **Promotion**: survivors move to `applications/entropy_<slug>/` with a dedicated README declaring `publication-target`.
4. **Per-project deepening**: each promoted project runs its own Phase 0 deep lit review (target 200+ citations), Phase 0.25 publishability review, and Phase 0.5 baseline audit.

## Artifacts produced here

- `literature_review.md` — 7 themes across neuroscience / complex systems / AI-ML, landscape-level depth (≥1500 words/theme)
- `papers.csv` — 100+ verified citations
- `knowledge_base.md` — stylised facts, known-good methods, known pitfalls (e.g. spurious power laws from subsampling, branching-ratio bias)
- `candidate_ideas.md` — 10–15 one-page proposals
- `scope_checks/` — one scope-check verdict per candidate (fresh sub-agent per candidate)
- `promoted.md` — table of candidates → outcome (PROCEED / REFRAME / KILL)

## Source fields and their key lineages

- **Neuroscience**: Beggs–Plenz cortical avalanches, Chialvo critical brain, Priesemann–Munk sub-sampling correction, developmental trajectories of criticality, disease signatures.
- **Statistical physics / complex systems**: Bak–Tang–Wiesenfeld self-organized criticality, branching-process universality classes, crackling noise, Clauset–Shalizi–Newman power-law fitting, directed-percolation universality.
- **Dynamical systems**: Langton's λ, Bertschinger–Natschläger computational capacity at edge of chaos, Sompolinsky random neural networks, echo-state-network reservoirs, Lyapunov spectra.
- **Deep learning theory**: Poole–Schoenholz–Pennington signal propagation, Xiao–Yang edge-of-chaos initialisation, neural tangent kernel, grokking, edge of stability in SGD, scaling laws.
- **Mechanistic interpretability**: Anthropic sparse autoencoders, superposition, activation patching, circuit analysis in transformers.
- **Network topology in ML**: lottery ticket hypothesis, structured sparsity, skip connections, small-world / scale-free analyses of trained networks.

## What this is NOT

- Not itself a publication-target project.
- Not a substitute for per-project Phase 0. The landscape scan feeds idea selection; each promoted project needs its own deeper, focused lit review.
