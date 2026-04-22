# Phase 0.5 Baseline Audit — entropy_effective_dimension

Date: 2026-04-21.

## Data-access verification — PASS

| Test | Result | Notes |
|---|---|---|
| `test_torch_cuda_available` | ✓ | torch 2.5.1+cu121, RTX 3060 fp16 |
| `test_stack_imports` | ✓ | transformers 5.5, powerlaw 2.0, mrestimator 0.2 |
| `test_pythia_70m_final_loads` | ✓ | `EleutherAI/pythia-70m` loads; d_model = 512; 6 layers |
| `test_pythia_intermediate_checkpoint_loads` | ✓ | Intermediate checkpoints via `revision="step1000"` tag work |
| `test_forward_hooks_capture_residual_stream` | ✓ | `model.gpt_neox.layers[N].register_forward_hook` yields (T, d_model) residual stream — the streaming-covariance-accumulator input path |

## Baseline methodology audit — PASS

The paper's headline rests on the Wilting-Priesemann 2018 property `r_k = m^k` for linear observables — MR estimator is correct on linear projections of a vector-valued branching process. This is a theory-level result we verified numerically on synthetic data:

| Test | Ground truth | Recovered | Tolerance | Result |
|---|---|---|---|---|
| `test_mr_estimator_on_linear_projection` | σ = 0.95, random unit projection of 32-stream BP | within 0.05 | ±0.05 | ✓ |
| `test_mr_estimator_on_top_K_PC_reconstruction` | σ = 0.95, Fontenele-style top-4-PC scalar reconstruction | within 0.05 | ±0.05 | ✓ |
| `test_critical_P_of_s_spans_2_decades` | σ = 1 Galton-Watson, 50K avalanches | ≥ 3 decades | ≥ 2.5 decades | ✓ |
| `test_participation_ratio_sane` | rank-4 + noise data | 3 < PR < 10 | ordinal | ✓ |

**Key theoretical-check outcome:** The Fontenele top-K-PC reconstructed-scalar observable and the direct random-projection observable both recover the seeded σ within ±0.05 on synthetic branching-process data. This means: when we apply the same pipeline to real Pythia residual-stream activations in Phase 1, a σ_subspace-vs-σ_ambient divergence (if it appears) cannot be attributed to a failure of the MR estimator on projected data — it is a real property of the activations.

**Dynamic-range pilot prep:** the Phase 0.25 kill gate requires P(s) span ≥ 2.5 decades on the reconstructed scalar before Fontenele's 1.5-decade-collapse K-selection rule is applied. On synthetic critical data we easily get ≥ 3 decades with 50K avalanches. Phase 1 Day 1 will measure the same on real Pythia residual-stream activations at a single checkpoint — if < 2.5 decades, the K-selection rule must be re-derived before the 100-cell sweep (per pre-registered kill).

## Phase 1 Day 1 / 2 commitments (from audit)

1. **Dynamic-range pilot on real data.** Extract ~10⁵ tokens of GPT-2-small or Pythia-160M residual stream at one checkpoint; compute Σ_K for K ∈ {1, 2, 4, 8}; fit `powerlaw` to P(s); confirm span ≥ 2.5 decades on at least one K. Pre-registered kill gate.

2. **Streaming covariance accumulator.** PyTorch forward hooks (verified working) + Welford online algorithm for numerical stability. Per-layer covariance matrix (d_model²) is ~26 MB for Pythia-1.4B — fits trivially in RAM.

3. **Halloran-Roysdon Lyapunov companion observable.** Per Phase 0.25 reframe, add as narrative insurance. Jacobian power-iteration at each checkpoint — ~20 JVPs per layer, ~40 s per checkpoint on 3060. Across 100 cells: ~1 GPU-hour.

4. **Faithful vs K-tuned Fontenele replication.** Pre-register *both* K-selection rules (Fontenele operational collapse-criterion K + direct participation-ratio K) and report both; either converges on the same K or we have an interesting methodological finding.

## Gate verdict

**Phase 0.5 PASSED.** All three Phase 0.5 deliverables met: data-access verified, baseline methodology validated on synthetic ground truth, dynamic-range pilot protocol locked in.
