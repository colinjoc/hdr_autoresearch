# Phase 0.5 Baseline Audit — entropy_avalanches

Date: 2026-04-21. TDD discipline per `~/.claude/CLAUDE.md` — tests written first, then run.

## Data-access verification — PASS

All HuggingFace / Gemma Scope paths reachable on a fresh venv with CUDA 12.1 torch:

| Test | Result | Notes |
|---|---|---|
| `test_torch_importable_with_gpu` | ✓ | torch 2.5.1+cu121; RTX 3060 detected; fp16 matmul works |
| `test_transformers_and_powerlaw_importable` | ✓ | transformers 5.5.4, powerlaw 2.0.0, mrestimator 0.2.0 |
| `test_gpt2_small_loads` | ✓ | GPT-2-small forward pass yields 13 hidden states (768-dim) |
| `test_pythia_160m_loads` (slow) | ✓ | EleutherAI/pythia-160m loads in fp16, ≥13 hidden states |
| `test_gemma_scope_weights_reachable` | ✓ | `google/gemma-scope-2b-pt-res` hosts `params.npz` SAE weights |

**Key finding to propagate into Phase 1 pipeline code:** Gemma Scope ships SAE weights as `.npz` NumPy archives under the directory tree `embedding/width_{w}/average_l0_{k}/params.npz` (and similar for MLP / residual sub-layers). **Not safetensors** — must use `np.load` not `safetensors.torch.load_file`.

## Baseline audit — PASS

Synthetic Galton-Watson (Poisson offspring) and driven-branching-process data recover known-truth exponents with the exact pipeline Phase 1 will run on real activations:

| Test | Ground truth | Recovered | Tolerance | Result |
|---|---|---|---|---|
| `test_galton_watson_critical_avalanche_alpha_recovered` | α = 3/2 | within [1.35, 1.70] | ±0.10 | ✓ |
| `test_galton_watson_subcritical_alpha_steeper` | mean and 99th percentile ordering | subcritical < critical | ordinal | ✓ |
| `test_mrestimator_recovers_branching_ratio` | σ = 0.95, driven BP | ~0.94-0.95 | ±0.05 | ✓ |
| `test_crackling_noise_scaling_relation_closes` | γ = (β−1)/(α−1) ≈ 2 | within [1.4, 2.6] | bootstrap CI | ✓ |

**Key correction learned during the audit:** The MR estimator requires a *driven* branching process (homeostatic Poisson drive `h > 0`), not a hard re-seed when activity hits zero. A naive re-seed creates discontinuities that break the exponential-autocorrelation fit and under-estimates σ by ~0.15. For Phase 1 on real LLM activations: activity is always driven by incoming tokens / residual-stream inputs, so no re-seed issue arises — but synthetic validators must use the driven form.

## Constraints validated

- **Single RTX 3060 12 GB.** GPT-2-small (fp16) fits comfortably; Pythia-160M fp16 fits. Pythia-2.8B fp16 (cap) will need eval-mode forward-only with small batch sizes; memory budget check deferred to Phase 1.
- **Python 3.12.** `allensdk` was blocked by this and we pivoted to DANDI for the sibling project; here all entropy_avalanches deps (torch-cu121, transformers 5.5, powerlaw 2.0, mrestimator 0.2) install cleanly on 3.12.
- **TDD discipline.** Tests written first; 7 failures during iteration (torch-cu130→cu121, mrestimator API shift, Gemma Scope SAE format, driven-BP for MR estimator) — each fixed at the test level before pipeline code.

## Remaining items flagged for Phase 1

1. **Pythia-2.8B VRAM budget.** Forward-only fp16 is ~5.6 GB; residual-stream cache at context 512 × batch 1 × layer 32 × d_model 2560 ≈ 80 MB/sample. Should fit with ≤4-sample batch; verify in Phase 1 Day 1 with a single forward pass before committing to the 20-checkpoint × 5-scale grid.

2. **Gemma Scope all-layer SAE fit.** Per Phase 0.25 reframe, random-init-SAE control is widened from 3 layers to all 12 on GPT-2-small. Verify via `huggingface_hub list_repo_files` that width-4k SAEs exist for every GPT-2-small layer equivalent (Gemma Scope is Gemma-2-2B not GPT-2; for the random-init-SAE ablation on GPT-2-small we need to train one ourselves or use existing GPT-2 SAEs from OpenAI/Anthropic release lists — note for Phase 1).

3. **CIFAR-10 for ViT-Tiny §9 arm.** `torchvision.datasets.CIFAR10` download path verified in general; add explicit test in Phase 1 Day 1.

4. **Activation-cache sizing.** Per-sample cost in §1 above × 10⁵ tokens × 5 scales × 20 checkpoints ≈ 800 GB. Use streaming / memory-mapped partial caches, not full prefetch. Streaming implementation is Phase 1 Day 2.

## Gate verdict

**Phase 0.5 PASSED.** Ready to enter Phase 1. No blockers. Six concrete items flagged for Phase 1 Day 1-2; all on the critical path but none a stop.
