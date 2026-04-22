# Phase -0.5 Scope-Check - Candidate 25

**Title.** Temporal renormalization group on LLM token sequences.
**Proposed observable.** TRG flow of activation covariance spectrum under coarse-graining; fixed-point exponent with uncertainty; universality-class assignment (DP / mean-field / edge-of-synchronization).
**Proposed method.** Implement Sooter 2025 [4007] TRG pipeline on GPT-2 residual-stream activations.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, lean KILL-as-standalone.** The candidate combines a real methodological gap (RG-style coarse-graining of LLM activations is essentially unpublished) with two fatal framing errors that dissolve on contact with the actual Sooter 2025 pipeline: (a) Sooter's TRG does **not** produce a critical-exponent / universality-class assignment - it produces a scalar "distance-to-criticality" metric d_beta against a *pre-specified* fixed point, not a classifier among DP / mean-field / edge-of-synchronisation; (b) the O(n^2) feasibility concern is misdirected - the correlation matrix for d_model ~ 10^3 residual-stream units is ~5-20 MB and fits trivially on a 3060. A partial scoop by **arXiv:2601.19942 (Jan 2026)** already executes depth-RG coarse-graining on Qwen-2.5, Gemma-2, LLaMA-3 with covariance-spectrum flow as the headline observable. Recommended disposition: **merge as a 5-7 day appendix probe on Paper 1 or Paper 7**, measuring *proximity-to-criticality* alongside alpha, sigma, Lyapunov rho - the role papers.csv already assigns citation 4007. Do not promote as a standalone 4-week Neural Computation / PNAS target.

## 2. Verifying Sooter 2025 [4007] - is the pipeline available or derivable?

**Sooter TRG is the temporal extension of Meshulam-Bialek 2019 phenomenological RG (PRG)** [PRL 123:178103]. The PRG algorithm: (i) compute pairwise correlation matrix c_ij; (ii) greedily pair the most-correlated variables; (iii) sum and renormalise each pair; (iv) iterate, producing clusters of size K=2^k. Headline output: whether coarse-grained activity approaches a non-Gaussian fixed point with scaling eigenvalue spectrum. Sooter 2024 (bioRxiv 2024.05.29.596499) and Sooter 2025 (bioRxiv 2025.08.03.668332) extend coarse-graining to the time axis and fit a metric **d_beta** measuring distance from a pre-specified fixed point.

**Code.** `d_beta` repo on Figshare (doi 10.6084/m9.figshare.25927081), **MATLAB**, accompanying the 2024 paper. 2025 v2 has no confirmed GitHub release; Python port is 2-5 days. Meshulam 2019 PRG has multiple Python re-implementations. **Pipeline is derivable-and-available, not packaged.**

**Framing error.** TRG output is not a universality-class assignment. Sooter's published use case is "is this system closer to pre-specified fixed point A or B?" - the fixed point is *assumed*, and d_beta measures proximity. No published TRG application has produced a universality-class identification; the metric is not calibrated to distinguish DP from mean-field exponents. The candidate conflates *scaling invariance* (what PRG/TRG tests) with *exponent-matching universality* (what crackling-noise alpha/beta/gamma tests). The Sooter pipeline cannot deliver the universality-class claim the candidate headlines.

## 3. Has any 2024-2026 paper applied RG to deep networks / transformers?

Three directly relevant hits:

1. **arXiv:2601.19942 (Jan 2026) "Latent Object Permanence... RG Flows in Deep Transformer Manifolds."** Discrete **depth-based RG** on Qwen-2.5-1.5B, Gemma-2-2B, LLaMA-3-8B, Fimbulvetr-11B, MiroThinker-30B. Headline: covariance-spectrum depth-evolution, dimensionality collapse, operator-norm contraction q<1, free-energy decrease. Does *not* use Meshulam-Bialek / Sooter TRG; does *not* assign DP / mean-field classes. **Novelty residual:** Sooter's temporal TRG (time-axis) is orthogonal to 2601.19942's depth-axis RG. "First correlation-pair PRG / temporal TRG on GPT-2 residual stream" is still open, but the RG-on-transformers region is now occupied.

2. **arXiv:2510.06361 (Oct 2025) "Diffusion-Guided Renormalization via Tensor Networks."** Bespoke tensor-network RG framed for neuroscience and AI; not transformer-specific.

3. **arXiv:2410.00396 (Oct 2024) "Dynamic neuron approach... RG analysis."** Theoretical RG on DNN structure; no transformer empirics.

**Methodological caveats from recent literature:**

- **arXiv:2506.14053 (Jun 2025)** - PRG "only detects scaling... within a very narrow range of the critical point." Devastating for any PRG-fixed-point-exponent claim without known-criticality ground truth.
- **arXiv:2001.04353 (Silva 2020)** - PRG scaling persists up to ~10% from true critical point in contact-process models; **PRG produces false-positive scaling in supercritical systems**.
- **papers.csv 4005 (Fontenele-Sooter 2024 Sci. Adv.)** - cortical criticality lives in a low-dim subspace. TRG in ambient residual-stream basis may miss criticality localised to SAE-feature directions. Same constraint binds as already flagged for Candidate 5 in promoted.md.

**Net:** "first MB-PRG / Sooter TRG on GPT-2 residual stream with d_beta" is open, but a ~1-week result in a crowded region, not a 4-week standalone paper.

## 4. Is the O(n^2) / RTX 3060 feasibility concern real?

**No, not as stated.** The covariance matrix for d_model ~ 10^3 is negligible:

| Model | d_model | Correlation-matrix memory |
|---|---:|---:|
| GPT-2 small | 768 | ~5 MB fp64 |
| GPT-2 XL | 1600 | ~21 MB |
| LLaMA-3-8B | 4096 | ~134 MB |

The O(n^2) bottleneck would bite only if *every* (layer, token, unit) triple were a variable (n ~ 10^7, matrix ~350 TB); no sensible TRG pipeline does this. Standard practice fixes a basis (layer ell residual stream, or SAE features), treats d_model units as variables, and aggregates token samples within and across prompts.

**Actual binding constraints:**

- **Depth of usable coarse-graining.** Meshulam 2019 stopped at K=128 out of 1485 neurons because "finite sample size catastrophically distorts" deeper scales. For GPT-2 small (d=768), usable iterations ~6 = 1.8 decades in cluster size - at the Clauset 2009 minimum 2-decade bar. GPT-2 XL gets ~7 iterations = 2.3 decades. Scaling range is **marginal**.
- **Token sample count.** Populating joint tails at cluster-size 128 needs ~10^5-10^6 token samples = 10^3-10^4 prompts of length 1024. fp16 activation cache ~ 190 GB for GPT-2 small; off-GPU streaming. 2-3 days inference+I/O on a 3060. Manageable.
- **Temporal-axis variant (what the candidate title suggests).** Coarse-grain time, not units: context 1024 -> up to 10 iterations ~3 decades - much more scaling range. **Better pipeline for LLMs** and matches Sooter's spike-train use. The candidate conflates this with the spatial Meshulam-Bialek variant.

Verdict: **tractable in 4 weeks if temporal-axis**, marginal if spatial.

## 5. Is a "fixed point" interpretable on finite-size LLM activation data?

**Conditionally yes, with three caveats.**

1. **PRG/TRG scaling is not specific to criticality.** arXiv:2506.14053 and Silva 2020 both show PRG eigenvalue-exponent and activity-probability signatures persist in non-critical models across broad parameter ranges. Griffiths phases and neutral dynamics (Martinello 2017, lit_complex.md §10) reproduce the phenomenology without a critical point. A TRG fixed-point exponent is **not** evidence of criticality by itself - it must be paired with Griffiths/neutral-null rejection.

2. **Coarse-graining runs out of samples before it runs out of scale.** For GPT-2 small, stopping at K=64-128 (5-6 iterations) gives 1.8-2.1 decades - right at the Clauset 2009 bar. The candidate must pre-register a minimum-iterations criterion and treat sub-1.5-decade results as negative.

3. **Basis sensitivity (papers.csv 4005, knowledge_base.md §3.1).** LLM activation criticality may live in a low-dim SAE subspace while ambient residual stream looks desynchronised. TRG on raw residual activations could trivially fail for reasons unrelated to the network's actual criticality status. **Mandatory** to run in at least two bases (raw-neuron + SAE-feature, Gemma Scope / SAE Lens). Trivially missed in the candidate as written.

## 6. Reframe path

Kill the standalone / PNAS framing. Retain as **~5-7 day appendix probe on Paper 1 or Paper 7**:

- **Observable.** d_beta (Sooter 2025) on GPT-2 residual-stream activations, temporal-axis coarse-graining. Report eigenvalue-spectrum and variance flow across 5-7 iterations.
- **Framing.** "Fourth criticality observable alongside alpha, sigma, Lyapunov rho" - the role papers.csv line 8 already assigns to 4007.
- **Controls.** (i) At-init GPT-2 baseline; (ii) PRG on shuffled activations (should destroy the fixed point); (iii) SAE-feature basis comparison; (iv) Griffiths-phase null.
- **Pre-registered kill.** If d_beta is within 2-sigma of at-init and shuffled baselines, or if iteration depth fails to reach 1.5 decades, report as null.
- **Cost.** ~5-7 days: 2d porting Matlab d_beta to Python (or subprocess call); 2d on cached activations (reuse Paper 1 cache); 1-2d analysis.
- **Defensible novelty claim:** "First Meshulam-Bialek PRG and Sooter TRG d_beta applied to transformer residual stream, in ambient and SAE bases, for at-init and trained GPT-2 across four scales." Appendix-sized contribution. Consistent with promoted.md role for 4007.
- **Undefensible claim (original version):** "Fixed-point exponent matches DP universality class" - the method is neither calibrated for this nor used this way anywhere in Sooter's own work.

## 7. Updates needed to papers.csv / promoted.md

- **Add** arXiv:2601.19942 (depth-RG on transformers, Jan 2026) as partial scoop; constrains Candidate 25 reframed novelty.
- **Add** arXiv:2510.06361 (DTNR, Oct 2025) as adjacent multiscale-RG.
- **Add** arXiv:2506.14053 (PRG narrow-window, Jun 2025) and arXiv:2001.04353 (PRG false-positives, Silva 2020) as mandatory methodological caveats on any PRG/TRG claim.
- **Clarify** papers.csv entry for 4007 (Sooter 2025): d_beta is a *proximity metric against a pre-specified fixed point*, not a universality-class classifier. Prevents recurrence of this framing error.

---

**Bottom line.** Candidate 25 as written is built on mis-reading what Sooter's TRG outputs and an overstated memory-cost blocker. Reframed as a week-long TRG/d_beta appendix on Paper 1 in the role papers.csv already assigns citation 4007, the work is cheap, methodologically sound, and adds a genuine fourth criticality observable. Standalone promotion on "universality-class assignment via TRG fixed point" must not proceed - the method cannot deliver that claim.
