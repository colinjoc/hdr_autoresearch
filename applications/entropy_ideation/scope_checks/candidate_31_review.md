# Phase -0.5 Scope-Check - Candidate 31

**Title.** Adversarial robustness as sub-criticality proxy - measure σ on matched vanilla vs adversarially-trained vision transformers.
**Proposed observables.** σ(vanilla) vs σ(adv-trained); robust-accuracy vs |σ − 1| scaling across a RobustBench sweep.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, then PROCEED as one arm of a deployment-criticality paper bundled with C32 (quantisation) and C33 (distillation).** The mechanistic hypothesis (robust → sub-critical) is substantially correct, the RobustBench / Singh-NeurIPS-2023 ecosystem is public and production-ready, and inference fits on a 3060. Three fixes needed before Phase 0: (i) "matched vanilla ViT-B/16" baseline is underspecified — the wrong choice produces a positive result driven by the clean-accuracy gap, not criticality; (ii) top-of-leaderboard adversarial ImageNet models are *Swin-L* / *ConvNeXt-L*-ConvStem, not ViT-B/16, so the candidate either broadens to a RobustBench sweep or restricts to Singh-2023 ViT-B-ConvStem with a match caveat; (iii) one-sided σ-only framing must become dose-response + λ_max orthogonal-observable to avoid trivial-confound publication. N = 2 as proposed; N = 4 reframed.

## 2. Availability of adversarially-trained ViT checkpoints

**Strongest part of the candidate.** RobustBench (Croce et al., NeurIPS 2021 Benchmarks; `pip install robustbench`; models via `robustbench.utils.load_model`) maintains the ImageNet L∞ leaderboard at ε = 4/255 under AutoAttack. As of 2026-04-21, top entries:

| Rank | Checkpoint | Clean | Robust | Arch |
|---:|---|---:|---:|---|
| 1-2 | Liu2023/Bai2024 | 78.9/78.6 | 59.6/59.7 | Swin-L |
| 3 | Amini2024 MeanSparse | 78.8 | 62.1 | Swin-L post-hoc |
| ... | Singh2023 ConvNeXt-L-ConvStem | 77.0 | 57.7 | ConvNeXt-L |
| 12 | Singh2023 ViT-B-ConvStem | 76.3 | 54.7 | ViT-B+ConvStem |
| 19-21 | Debenedetti2022 XCiT-S/M/L12 | 72-74 | 42-48 | XCiT |

Right target for a "matched ViT-B/16 pair": **Singh et al. 2023 "Revisiting Adversarial Training for ImageNet"** (NeurIPS 2023, arXiv:2303.01870, `github.com/nmndeep/revisiting-at`) — ViT-B/S + ConvNeXt-B/T/L/S (all + ConvStem) + Swin-L trained at ε = 4/255, public checkpoints on RobustBench. Secondary: **Debenedetti-Sehwag-Mittal 2022 "Light Recipe"** (arXiv:2209.07399, SaTML 2023, `github.com/dedeswim/vits-robustness-torch`) — XCiT-S12/M12/L12 adversarially warm-started from clean ViT. Bai-2024 MIMIR and Amini-2024 MeanSparse are Swin-L only. Wang-Li-Zhu CVPR 2024 "Revisiting Adversarial Training at Scale" trains ViT-Huge but checkpoints not in RobustBench.

**Net:** one adversarial ViT-B-class public checkpoint (Singh-2023 ViT-B-ConvStem) + XCiT family; any other ViT-B/16 needs from-scratch training (~1-2 wk on 8 A100s; infeasible on 3060). Reframe to Singh-2023 ViT-B-ConvStem + XCiT-S/M/L size sweep, or full RobustBench Linf sweep with arch covariate.

## 3. Matched-vanilla baseline - the real methodological hazard

Biggest failure mode. Singh-2023 ViT-B-ConvStem differs from stock timm ViT-B/16 in (i) ConvStem vs patchify, (ii) training recipe (longer schedule, strong aug, warm-start). Comparing σ(Singh adv) vs σ(Dosovitskiy clean) confounds adversarial training with stem, aug, schedule, resolution. Options:

- Train clean-only ViT-B-ConvStem with Singh's recipe (`--eps 0`; infeasible on 3060) - or
- Use Singh's clean-trained control if released (verify `github.com/nmndeep/revisiting-at` README before Phase 0) - or
- **Pre-register an ε-sweep (0, 0.5/255, 2/255, 4/255) with a fixed Singh recipe**, so AT strength is the independent variable. This is cheapest, cleanest, and yields a dose-response rather than a two-point test.

## 4. Is the hypothesis mechanistically correct?

**Largely yes, but only one-sided as framed.**

*Support.* Madry-PGD is first-order a Lipschitz-regulariser: `min_θ max_{δ∈Bε} L(f(x+δ))` upper-bounds by `L_f · ε + L_clean`, driving training toward smaller ||J_f||. Smaller Jacobian singular values → χ_1 < 1 → ordered/sub-critical (Poole 2016; Pennington 2017; Pilarski 2023 VERIFY). Supporting lit: Cisse 2017 Parseval; Finlay-Oberman Lipschitz-loss; Prach-Lampert CVPR 2024 1-Lipschitz comparison; LipShiFT 2024 (OpenReview OfxNKIHfUA) certifiable-Lipschitz ViT; Virmaux-Scaman ACM Comput. Surv. 2024 "Adversarial Robustness from Lipschitz Calculus". Jacobian-norm story is established; recasting as "σ falls below 1" is the novel bridge.

*Counterweight 1.* AT *increases* activation sharpness and can induce feature collapse or spikier attention (Shao-Shi 2022; Kim WACV 2024 "Exploring Adversarial Robustness of ViTs in the Spectral Perspective"). Sparser bursts with heavier tails could push α *down* (more super-critical-looking) while λ_max falls. σ and α may disagree — a publishable finding, but the candidate's "overlap → dies" kill condition does not anticipate it.

*Counterweight 2.* Bai-2024 MIMIR and Amini-2024 MeanSparse apply *post-training* sparse-activation filters that mechanically shift any branching-ratio estimator. Exclude from primary analysis; appendix ablation only.

*Counterweight 3.* Benati-Falanti 2025 arXiv:2506.12810 (Lyapunov Learning at the Onset of Chaos) and Lewandowski-Tanaka-Schuurmans-Machado 2024 spectral-regularisation both aim for λ_max ≈ 0 with robustness benefits — "robust via edge-of-chaos" is a live alternative.

**Reframe as two-tailed dose-response:** |σ − 1| vs AutoAttack robust-accuracy over the Singh ε-sweep, arch as covariate. Monotone negative correlation is the positive; null or positive correlation is the negative; non-monotone U (robust at both σ ≈ 1 and σ ≪ 1) is the interesting third outcome.

## 5. Precedent check 2024-2026

Searched papers.csv (209 entries) + arXiv titles + RobustBench leaderboard with `adversarial` ∩ {`Lyapunov`, `criticality`, `spectral radius`, `branching ratio`, `avalanche`, `edge of chaos`}.

- **No paper relates σ to adversarial robustness on ViTs or any architecture, as of 2026-04.** papers.csv has zero adversarial hits; lit_ml.md discusses sensitivity only for clean nets; arXiv title search empty.
- *Adjacent, not gap-closing.* Kim WACV 2024 (Fourier-spectral attack vulnerability, not Jacobian-spectrum); Prach-Lampert CVPR 2024 (certified Lipschitz); arXiv:2410.23382 (Lipschitz-vs-arch scan); LipShiFT 2024 (certifiable-Lipschitz ViT); Nature Comm. 2025 s41467-025-56595-2 analog-IMC adversarial (hardware noise); Benati 2025 Lyapunov-Learning (trains toward λ_max = 0 but does not test robust checkpoints); Halloran 2024 Mamba-Lyapunov-Stable (not ViT, not adversarial).
- *LLM / TextFooler angle.* Jin 2020 TextFooler, Morris 2020 TextAttack, Zhu 2024 PromptBench yield attack-success rates without criticality observables. Robust-trained LLMs (SmoothLLM, certified adapters) target jailbreak/prompt threat models, not vision-style AT; the σ-vs-robustness claim does not transfer cleanly. **Defer LLM arm to future work.**

**Gap is real and clean.** Singh-2023 and Debenedetti-2022 are the natural pools; neither measures criticality.

## 6. Confounders beyond architecture match

- **Clean-accuracy gap.** AT costs ~10% clean acc. σ depends on input distribution; lower-acc models have more misclassified inputs with broader activations, confounding σ with error rate. Control: stratify σ by correctly-classified subset and prediction entropy; compare matched-entropy subsets.
- **Input distribution match.** AT networks see perturbed inputs during training, shifting internal activations even at clean test. Pre-register σ computed on *identical* clean val images across checkpoints; add input-PGD-ε sweep (0, 1/255, 2/255, 4/255) as an additional axis.
- **Activation-space basis.** Per knowledge_base.md §5, raw-neuron vs PCA vs random-projection bases give different exponents. ViT residual streams (d = 768) are anisotropic; AT may re-weight principal components. Report σ in raw, PCA-top-50, random-projection; pre-register primary basis, flag others as robustness.
- **Aug / normalisation.** Singh and clean-ViT use different RandAug/Mixup; report aug-matched σ as a robustness check.
- **Post-hoc sparsification.** Amini-2024 MeanSparse mechanically shifts branching-ratio; primary-analysis exclusion.

## 7. Compute on an RTX 3060 12 GB

Inference-only ViT-B/16: fp16 weights ~0.17 GB, peak activations < 2 GB at batch 64. 50k ImageNet val × 4 checkpoints × 3 bases × 4 input-ε ≈ 2.4M forwards at ~150 img/s ≈ 4.5 hrs; λ_max via random-vector power iteration ~3x ≈ 15 hrs total. Singh checkpoints load via RobustBench one-liner. **Budget:** 2 wk narrow, 3-4 wk reframed bundle.

## 8. Pre-registered kill and rubric

**Stronger kill** than "CIs overlap": regression log(AutoAttack-robust-acc) vs |σ − 1| across ≥ 8 checkpoints (Singh ε-sweep + XCiT-S/M/L + Swin-L + 2 clean controls). Pre-registered kill: slope 95% CI includes zero *and* |Spearman ρ| < 0.3 *and* λ_max shows no monotone trend. Secondary: two-tailed σ test; log opposite-sign as finding, not failure. Paper-kill: if |σ − 1| vs robust-acc correlation is weaker than trivial |clean − robust| vs robust-acc, σ adds no information and the "robustness proxy" claim dies.

**Rubric.** D = 5 (checkpoints + RobustBench + ImageNet val all free). N = 2 narrow / N = 4 reframed bundle. F = 3 (dose-response + arch sweep + orthogonal observable + entropy stratification; single-point comparison would be F = 1). C = 5 (4.5-15 hrs GPU, 3-4 wk wall-clock). P = 2 narrow (TMLR/workshop) / P = 4 fused with C32 + C33 as deployment-criticality short (NeurIPS/ICLR main).

**Composite:** PROCEED with: (i) ViT-B/16 → Singh-2023 ViT-B-ConvStem + ε-sweep + XCiT-S/M/L; (ii) mandatory λ_max orthogonal observable; (iii) matched-entropy stratification; (iv) fuse with C32 + C33 into one deployment-interventions paper.

## 9. Action items

1. Replace "ViT-B/16" in `candidate_ideas.md` §C31 with "Singh-2023 ViT-B-ConvStem (RobustBench) ε-sweep + XCiT-S12/M12/L12 (Debenedetti 2022)". Note Swin-L dominates top leaderboard; add as covariate, not ViT-B match.
2. Pre-register clean-vs-adv control as *same-recipe ε = 0 vs ε = 4/255* from Singh, not stock-timm-ViT vs Singh-ViT.
3. Add λ_max / Jacobian-spectrum as mandatory orthogonal observable; pre-register σ-λ_max agreement as primary test.
4. Exclude Bai-2024 MIMIR and Amini-2024 MeanSparse from primary correlation (post-hoc sparsification confound); appendix only.
5. Drop the LLM adversarial (TextFooler) secondary arm from Candidate 31 scope; threat-model mismatch. Spin off as Candidate 31b if it survives its own scope check.
6. Move Candidate 31 from "standalone 2-week" to "one arm of deployment-criticality paper alongside C32 + C33" in `promoted.md`. Budget 3-4 weeks for the bundle.
7. Verify Singh-2023 repo still hosts ConvStem-ViT-B clean-only checkpoint (or ε = 0 training config) before Phase 0 (per `feedback_verify_data_access_before_phase_0`).
