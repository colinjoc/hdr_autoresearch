# Phase -0.5 Scope-Check: Candidate 9 — Dynamic range peaks at criticality (Kinouchi-Copelli test on LLMs)

**Verdict: REFRAME (defer + tighten).** Scientifically attractive and targets a stylised fact with a crisp analytic prediction [1022: Kinouchi-Copelli 2006; 1003: Shew et al. 2009], but premature as a standalone 3-week project. Three blockers: (i) the LLM analogue of stimulus intensity I is not defined and is genuinely non-trivial; (ii) correlating with |sigma - 1| requires a credible sigma measurement that only exists downstream of Candidate 1 (and arguably 2 or 7 for the tuning axis); (iii) a prompt-difficulty sweep without the parallel avalanche machinery cannot distinguish dynamic-range-peak-at-criticality from generic scaling-law smoothness.

---

## 1. Novelty vs `papers.csv` + 2024-2026 arXiv

Note the proposal mis-cites [1008] (Shew & Plenz 2013 review); the original analytic result is [1022: Kinouchi & Copelli 2006 Nat. Phys.]; experimental test is [1003: Shew et al. 2009].

2024-2026 arXiv sweep surfaces three directly relevant threads:

- **arXiv:2410.02536** (Zhang et al., "Intelligence at the Edge of Chaos", Oct 2024). LLMs trained to predict elementary cellular automata of graduated Wolfram-class complexity; downstream reasoning performance peaks at *intermediate* input complexity. This is arguably the first published dynamic-range-like curve for an LLM: capability rises, peaks, falls. Uses training-data complexity, not prompt difficulty; does not compute sigma or correlate with |sigma - 1|. But the headline "LLM capability peaks at an edge-of-chaos sweet spot" is now in the literature.
- **arXiv:2604.16431** ("Dimensional Criticality at Grokking", 2026). Avalanche-scaling dimension D(t) on transformers in modular addition, D=1 crossing at grokking. Overlaps Candidate 1 + 4 but not dynamic range.
- **arXiv:2512.00168** ("Tuning Universality in DNNs", Dec 2025). Avalanche-statistics-based universality-class prediction. No DR test.

**Net novelty as written**: moderate-to-narrow. "LLM capability peaks at a critical-like sweet spot" is no longer unexplored; the specific claim "capability-response dynamic range correlates with |sigma - 1| on a network-criticality axis" remains open, but depends on sigma from Candidate 1 + a tuning axis from Candidate 2 or 7. Without those, Candidate 9 collapses to a re-run of arXiv:2410.02536 with a different complexity axis.

## 2. Operationalisation — the specific concerns

### 2.1 What is "stimulus intensity I" in an LLM?

KC measure DR as `10 log10(I_0.9 / I_0.1)` where I is external Poisson drive rate. In [1003] I is pharmacologically-controlled input into a slice. In an LLM the proposal picks prompt difficulty, but there are three candidate mappings with different confounds:

- **Prompt difficulty** (arithmetic digit-count, multi-hop QA). Most intuitive but conflates *task difficulty* (target-computation property) with *stimulus intensity* (driving-input property). A harder arithmetic problem is not a stronger stimulus in any branching-process sense.
- **Token-perturbation magnitude** (embed noise of magnitude epsilon, measure `||Δ output||`). Cleaner KC analogue but essentially the Lyapunov protocol from `lit_ml.md §10` and Candidate 10 — merging would save compute.
- **Intermediate-activation-perturbation magnitude** (`knowledge_base.md §2.6`). Most faithful to the cortical-slice protocol: drive a layer with activation noise, read out downstream change. Confounded by LayerNorm rescaling.

The proposal picks (1) without addressing the conflation. This is the single largest operationalisation risk: a positive result on prompt-difficulty could be wholly explained by Kaplan/Chinchilla scaling-law smoothness (`lit_ml.md §4`). The Schaeffer 2023 warning [3016] on metric-dependent emergent capabilities applies directly — the kill condition is vulnerable to being passed or failed depending on capability-metric smoothing.

### 2.2 Cortical apparatus vs LLM probing

Cortical-slice DR [1003] requires (i) externally controllable smooth Poisson drive, (ii) instantaneous population readout, (iii) orthogonal pharmacological E/I control. None translate trivially: prompts are discrete/semantic/non-Poissonian; capability metrics are aggregated over benchmarks; topology or scale are coarse-grained. The analogy is suggestive, not literal; paper-writing burden for each mapping is substantial.

### 2.3 Dependency on Candidate 1 (and 2 or 7)

To correlate DR with |sigma - 1| across configurations the candidate needs (a) a validated avalanche/branching pipeline (Candidate 1 deliverable); (b) evidence sigma actually varies across the chosen axis (Candidate 2 kill condition); (c) at-init control + neutral-null rejection (`knowledge_base.md §5` items 7-8). Without those, Candidate 9 attempts a correlation between a poorly-calibrated x-axis and a poorly-defined y-axis. This is exactly the "stronger version of the functional-consequence theme" the user flags — and it **does** require Candidate 1 first.

## 3. Falsifiability

Pre-registered kill is concrete in form but fragile:

- **"Flat" is threshold-dependent**: Shew 2009 reports 3-4x inverted-U; would 1.5x be peak or noise?
- **"Peak near sigma = 1" needs CI**: if argmax is at sigma = 0.88, miss or hit?
- **Metric sensitivity** per [3016]: peakedness depends on smoothing choice.

Tightened kill: DR must vary >=2x across probed sigma range, argmax within 0.1 of sigma=1, under both exact-match and log-likelihood capability metrics. Otherwise withdrawn.

## 4. Required controls (vs `knowledge_base.md §5`)

Items 1-6 (power-law fit, alpha~3/2, crackling-noise relation, shape collapse, MR sigma, threshold plateau) all inherited from Candidate 1 — must be complete before Candidate 9 makes sense. Item 7 (at-init control) must be explicitly added. Item 8 (neutral-null rejection): the proposal's premise *is* that DR correlating with |sigma-1| non-trivially constitutes a neutral-null rejection — this circularity needs unpacking in the write-up.

## 5. Venue fit

If tightened and properly sequenced:

- **ICLR / NeurIPS main**: "Functional consequences of criticality in trained LLMs" if exponents are clean.
- **ICML MechInterp / NeurIPS ATTRIB workshop**: safer if the mechanistic bridge is the headline.
- **Entropy (MDPI) / Neural Computation**: natural Kinouchi-Copelli framing.

arXiv:2410.02536 precedent shows these papers get arXiv traction but have not yet hit top ML venues.

## 6. Cost

Stated 3 weeks. Realistic decomposition:

- Benchmark selection + difficulty calibration: 3-4 days.
- Capability measurement across 10-20 configurations: ~1 week on RTX 3060 (Pythia-70M..1.4B; larger models stress VRAM per Candidate 7).
- DR computation + correlation with |sigma-1|: 2-3 days *given* sigma from Candidate 1.
- Robustness to metric, block-bootstrap CIs, controls: ~1 week.

**3 weeks is correct *after* Candidates 1 + (2 or 7) deliver sigma.** Standalone 3 weeks is infeasible: sigma measurements on LLMs do not exist in the published literature.

## 7. Too speculative?

Not too speculative *conditional on* Candidate 1 succeeding. Very speculative and not justifiable as a parallel thread: the proposal is "assume we have sigma, correlate with capability", and sigma on LLMs does not exist yet.

## 8. Dependence + recommendation

**Chain**: Candidate 1 -> Candidate 2 or 7 -> Candidate 9.

**Reframing for later promotion**:

1. **Defer** until Candidate 1 delivers validated sigma on GPT-2 small and Candidate 2 or 7 shows sigma varies measurably.
2. **Commit to stimulus-intensity operationalisation in advance**. My recommendation: intermediate-activation-perturbation magnitude (cortical-slice analogue) as primary; prompt-difficulty as a secondary axis with explicit scaling-law-confound discussion. Token-perturbation should merge with Candidate 10.
3. **Differentiate from arXiv:2410.02536** explicitly: that paper does capability vs input-complexity; Candidate 9 must do capability-DR vs network-criticality observable — distinct, narrower, more mechanistic.
4. **Coordinate with Candidate 10** — shared perturbation-response pipeline.
5. **Bundle ordering**: candidate_ideas.md footer suggests 8+9+11 bundle. Better: 1+2+12 first paper; 1+9 second-paper capstone. Never standalone.

## 9. Summary verdict

**REFRAME**: do not promote to `applications/entropy_<slug>/` this round. Re-scope-check after Candidate 1 reports its sigma pipeline and Candidate 2 or 7 reports sigma variation. At that point Candidate 9 graduates from cross-domain analogy to downstream test with validated inputs.

Free methodological by-product even if Candidate 9 never runs: the operationalisation of "LLM stimulus intensity" is open and will recur for any functional-consequence test (MI peak, memory-capacity peak). Documenting the three candidate mappings — prompt difficulty / token perturbation / intermediate-activation perturbation — in `knowledge_base.md §2.6` with their respective confounds is a worthwhile deliverable independent of promotion.
