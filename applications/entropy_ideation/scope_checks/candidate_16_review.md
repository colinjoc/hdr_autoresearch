# Phase -0.5 Scope-Check — Candidate 16

**Candidate.** Criticality curriculum: anneal `lambda(t)` during training. Biological cortex is more critical during development and less critical in mature state [1006: Gireesh-Plenz 2008, 1030: Tetzlaff 2010]. Does an annealed criticality regulariser — strong at start, weak at end — produce better-trained LLMs than constant `lambda`?
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**KILL as a standalone project; FOLD as one half-day ablation inside Candidate 13.** The curriculum variant is (a) a well-studied generic pattern (KL annealing, loss-coefficient warmup), (b) motivated by a developmental analogy that is already the subject of a mature deep-learning literature (Achille-Soatto critical-learning-periods), and (c) statistically under-powered at the compute budget implied by a 3060. The schedule sweep is worth one figure inside Candidate 13 ("we also tried annealing"), not a 3-week paper.

## 2. Dependence on Candidate 13 — not stand-alone

Candidate 16 is, structurally, Candidate 13 with a `lambda(t)` instead of a scalar `lambda`. It inherits Candidate 13's full training stack (differentiable `sigma_l` via Jacobian-spectral-radius power iteration, ~2x vanilla compute, per-batch backprop through `sigma`). Without that infrastructure there is nothing to anneal. Candidate 13 itself is pending scope-check with known non-trivial risks:

- Whether a `(sigma_l - 1)^2` penalty is optimisable at all on residual + LayerNorm architectures — the residual-stream confound surfaced in Promoted.md §"Methodological findings" item 1 means naive `sigma_l` is trivially 1 by construction (`h_{l+1} = h_l + F_l(h_l)`). Definition (a) "branching of `F_l(h_l)`", (b) "causal `sigma_l` via path patching" or (c) "layer-wise MR estimator" must be chosen first; (a) is the only option compatible with backprop.
- The 2x-vanilla-compute cost, compounded over 30+ seeds (required for schedule-vs-schedule discrimination; see §5), blows past the 3-week budget on a 3060.
- The Candidate 13 kill condition — "no `lambda` beats `lambda = 0`" — logically gates Candidate 16: if constant `lambda` does not help, annealed `lambda` trivially does not either (the best schedule is `lambda(t) = 0`).

**Verdict on dependence.** Candidate 16 is a *parameter-schedule of Candidate 13*. Promoting it separately is double-counting. Any honest reporting of Candidate 13 already sweeps 5 `lambda` values; adding 3-4 schedule shapes (constant, linear-decay, cosine, exponential) at the best `lambda_0` costs ~20 % extra compute on top of 13, not a new paper.

## 3. Curriculum-on-a-regulariser-coefficient — prior art density

The brief's second concern. The pattern "schedule a loss-term coefficient from high to low during training" is not a specific idea; it is a design motif with a half-dozen named instances:

- **KL annealing in VAEs.** Bowman et al. 2016 *CoNLL* "Generating Sentences from a Continuous Space" and Fu et al. 2019 *NAACL* "Cyclical Annealing Schedule" (arXiv:1903.10145) schedule the KL-divergence coefficient `beta` in the ELBO from 0 upward — the opposite direction of Candidate 16's high-to-low, but the same mechanism. Ichikawa-Hukushima 2024 *AISTATS* (arXiv:2310.15440) give the theoretical analysis: annealing `beta` controls posterior-collapse thresholds and can accelerate convergence. Exactly the "schedule the regulariser coefficient to trade off two objectives over training" pattern.
- **KL coefficient schedules in PPO / RLHF.** TRPO/PPO adaptive `beta` schedules (Schulman 2017) and the RLHF `beta_KL` schedule are standard production practice; DeepSeek-V3 and Llama-3 technical reports both use time-varying KL coefficients.
- **Weight-decay warmup / cooldown.** Loshchilov-Hutter 2019 *ICLR* decoupled weight decay; several 2024-2025 scaling-law papers (arXiv:2505.13738 "Power Lines") treat weight-decay-as-function-of-step as a first-class hyperparameter.
- **Dropout annealing.** Morerio et al. 2017 "Curriculum Dropout" and later replications anneal the dropout rate — a regulariser-coefficient-anneal, identical in form.
- **Label-smoothing schedules.** Xu et al. 2020 scheduled label smoothing.
- **Adversarial-training-strength schedules.** Madry 2018 and follow-ups schedule `epsilon`-ball size.
- **Meta-learning curricula on regulariser coefficients.** Meta-AutoAugment, Meta-KL (arXiv:2003.01889 "Meta Cyclical Annealing Schedule"), learned-regulariser-schedules more generally.

The generic statement "a curriculum on a regulariser coefficient helps" is approximately as defensible as "learning-rate schedules help" — true, studied to death, and not publishable as a method contribution. What *would* be publishable is a *specific* mechanism that makes the criticality regulariser behave differently from other regulariser-coefficient schedules. Candidate 16's motivation section — "biological cortex is more critical during development" — does not supply that mechanism; it is a correlational biological analogy, not a predictive ML theory.

**arXiv 2024-2026 search.** WebSearch 2026-04-21 on "biologically inspired curriculum developmental plasticity deep learning schedule" and "criticality curriculum deep learning" returns no paper scheduling a *criticality* regulariser biologically-annealed. Adjacent hits:

- **arXiv:1711.08856 + arXiv:1905.13399** Achille-Rovere-Soatto *ICLR 2019* + *PNAS* "Critical Learning Periods in Deep Neural Networks" (and the *Frontiers in Comp. Neurosci.* follow-up). Fisher Information Plasticity rises then drops during training; deficit windows early vs late have asymmetric effects. This is *the* developmental-deep-learning analogy paper. Candidate 16 does not cite it. The claim "biological analogue of development suggests anneal-then-relax" is directly pre-empted as framing, even though Achille-Soatto do not run a regulariser-anneal experiment.
- **arXiv:2308.12221** Kleinman-Achille-Soatto 2023 "Critical Learning Periods Emerge Even in Deep Linear Networks" — extends the finding to analytically tractable settings.
- **arXiv:2210.04643** "Critical Learning Periods for Multisensory Integration" — multimodal extension.
- **arXiv:2510.09687** Jung et al. 2025 "On the Occurrence of Critical Learning Periods in Neural Networks" — recent mechanism paper.
- **arXiv:2507.03168** 2025 "Human developmental visual diet" — input-curriculum motivated by vision development.

None of these schedule a *branching-ratio* or *edge-of-chaos* regulariser coefficient, so the narrow technical gap Candidate 16 claims exists. But the developmental-criticality-to-deep-learning conceptual bridge is already established; Candidate 16 is a method inside an already-framed research area, not a new framing.

**Novelty verdict.** Technically narrow gap (no one has annealed a `sigma`-regulariser coefficient inspired by Gireesh-Plenz 2008). But two things weaken it: (i) "schedule a regulariser coefficient" is a generic pattern, and (ii) "developmental deep-learning curriculum" is a crowded sub-area the candidate does not engage with. At best a Section-of-Candidate-13, not a paper.

## 4. Is the developmental-criticality analogy substantive or cosmetic?

The brief's third and most important concern. The proposed logic chain:

1. Biological cortex shows stronger criticality signatures during development [1006: Gireesh-Plenz 2008 *PNAS*] and drifts toward a homeostatic reverberating / slightly subcritical regime in maturity [1013: Ma 2019 *Neuron*].
2. A criticality regulariser with `lambda` high at the start of training and low at the end mimics this trajectory.
3. Therefore, annealed `lambda` should beat constant `lambda`.

The step (1) -> (3) transition is a classic biology-metaphor-as-prediction failure mode. Problems:

- **Development is not early-in-training.** In the biological literature, cortical criticality emerges *gradually* during DIV 0-14 as synapses mature (Gireesh-Plenz 2008 *shows* increasing criticality with maturation, not decreasing). That is the *opposite* of what Candidate 16 proposes: if we take the biology literally, `lambda(t)` should increase, not decrease. Tetzlaff et al. 2010 [1030] argue criticality is the *attractor* of homeostatic plasticity — i.e. any non-critical init homeostatically drifts *to* critical, which is (if anything) a stability argument that criticality survives training regardless of `lambda` schedule, not an argument for annealing.
- **Ma 2019 [1013] measured σ ≈ 0.98 in awake adult cortex** — slightly subcritical, not "not critical". The Gireesh-Plenz-to-Ma trajectory is DIV0 (very subcritical) -> DIV14 (α ≈ 3/2) -> adult awake (σ ≈ 0.98). This is not "strong-then-weak" criticality; it is "weak-then-emerging-then-near-but-slightly-below". The Candidate 16 framing inverts the developmental direction.
- **Confusion of homeostatic drift vs imposed penalty.** The biology says plastic rules produce criticality as a *stable fixed point*. Candidate 16 imposes criticality via an external loss. The two mechanisms are incommensurable: the first is emergent and local; the second is a global optimiser constraint. The biology-analogy license does not transfer across this mechanism gap.
- **Meisel 2013/2017 and sleep/wake literature [1034, 1035]** — cited in Candidate 19 — would if anything suggest an oscillating `lambda`, not a monotone anneal. Cherry-picked biology support.

**Substantive or cosmetic?** Cosmetic. The schedule direction as proposed is *contrary* to the Gireesh-Plenz 2008 developmental finding; the Tetzlaff 2010 [1030] homeostatic-attractor result argues *against* needing a coefficient schedule at all. The biological motivation, read carefully, predicts the opposite of what Candidate 16 proposes, or predicts nothing. This is the failure mode the lit-review review-rules explicitly warn about.

If the candidate is rescued, the framing must abandon the development analogy and justify the schedule on ML-internal grounds — e.g. "signal-propagation criticality matters most at init-to-feature-learning transition, which happens in the first ~5 % of training (cf. Jastrzebski 2020 'Break-even point of SGD', Frankle-Dziugaite 2020 'Early phase of training'), after which the signal-propagation constraint is met by emergent structure and `lambda` becomes superfluous overhead". That is an ML-internal argument that predicts a specific schedule (high for ~5 % of training, then 0). It is also mostly what any practitioner would try first without citing any biology.

## 5. Statistical power — can we distinguish schedule effects from seed noise?

The brief's fifth concern, and the one that most likely kills Candidate 16 on its own merits independent of the biology critique.

Candidate 16 commits to "linear / cosine / exponential `lambda`-schedules vs constant `lambda` and `lambda = 0`", on nanoGPT + TinyStories and Pythia-70M from scratch. Cost estimate: 3 weeks. Seed count: not specified.

The scope-check of Candidate 4 (grokking) already established that `sigma_t ≈ 20-40 %` of the signal being measured is normal for training-dynamics observables on small transformers, requiring n >= 30 seeds for detection. Val-loss seed variance on nanoGPT + TinyStories is typically 0.02-0.05 nats out of ~1.2 nats total, i.e. 2-4 % CV. To distinguish a 1-2 % schedule effect at alpha = 0.05 with power = 0.8 requires, by standard power calculations:

- `n = 2 * (z_{alpha/2} + z_{1-beta})^2 * sigma^2 / delta^2`
- Plug `sigma / mu = 0.03`, `delta / mu = 0.015`: `n ≈ 2 * (1.96 + 0.84)^2 * 0.03^2 / 0.015^2 ≈ 63` seeds per condition.

Five conditions (constant-best `lambda`, `lambda = 0`, linear, cosine, exponential) × 63 seeds = 315 training runs per model size. At Candidate 13's 2x-vanilla compute and nanoGPT-TinyStories at ~2 GPU-hours/run on a 3060, that is 1260 GPU-hours = ~53 GPU-days **on nanoGPT alone**. Pythia-70M from scratch is ~10 GPU-hours/run, so 3150 GPU-hours = ~130 GPU-days. Candidate 16 plus 13 combined would require ~6 months on the 3060.

Dropping to n = 10 seeds/condition (Candidate 13's likely default) inflates the MDE (minimum detectable effect) to ~3-4 %, which is larger than the effect sizes reported for comparable regulariser interventions in the literature. The experiment would be formally unable to distinguish schedule effects from noise.

**Verdict on power.** At the compute budget this programme assumes (single 3060), Candidate 16 is under-powered by a factor of ~5x in seed count. Either (i) restrict to 2 conditions (constant-best vs best-anneal) at 30 seeds, dropping the "sweep of schedule shapes" framing (which is the main method claim), or (ii) test on a very-small model where 60 seeds × 5 conditions fits (e.g. 4-layer 128-dim nanoGPT on Shakespeare-char, ~15 min/run, fits in ~10 GPU-days). Option (ii) trashes external validity: "annealed-criticality-lambda helps on a 4-layer nanoGPT" is a thin claim.

## 6. Pre-registered kill — as written, permissive

"If no schedule beats best-constant-`lambda` within seed noise, curriculum dies." Combined with §5, "within seed noise" at n = 10 means a ~3-4 % threshold — the curriculum has to provide a large effect to be detectable. If it fails that bar the kill triggers, but failure is the expected outcome on power grounds, not on mechanism grounds. Sharpen to: "if MDE at n-seeds-budget exceeds 2 % AND no schedule shows trend consistent across seeds, kill". Honest pre-registration requires specifying n at least 30 per condition.

## 7. Knowledge-base 8-item bar

Candidate 16 is a *training* experiment, not a criticality-measurement paper, so knowledge-base §5 items 1-8 apply only to Candidate 13's measurement of the post-training network. The only items that bind Candidate 16 directly:

- Item 7 (at-init control): trivially satisfied (compare to `lambda = 0`).
- Item 8 (neutral null): the neutral null for "schedule-beats-constant" is matched-compute constant-`lambda` at the schedule's time-averaged `lambda_eff = E_t[lambda(t)]`. The candidate does not specify this control. Without it, "cosine beats constant" could reduce to "lower time-averaged `lambda` beats higher `lambda`", which is a trivial knob re-calibration.

**Required addition.** Matched-time-averaged-`lambda` constant control.

## 8. Summary

**Verdict.** **KILL standalone; FOLD into Candidate 13.** Three reasons, any one sufficient:

1. **Dependence.** Candidate 16 is literally "Candidate 13 with `lambda(t)` instead of scalar `lambda`". Not a separate project; one extra figure in C13.
2. **Prior art.** "Schedule a regulariser coefficient" is a generic pattern (KL annealing in VAEs, dropout annealing, adversarial-`epsilon` schedules); the developmental-deep-learning conceptual frame is Achille-Soatto's critical-learning-periods sub-area, which the candidate does not engage with.
3. **Biological motivation is backwards.** Gireesh-Plenz 2008 shows criticality *increasing* during development, not decreasing. Tetzlaff 2010's homeostatic-attractor result argues against needing a schedule at all. The biology analogy predicts the opposite of what Candidate 16 proposes, or nothing.

Additionally, at n <= 10 seeds/condition — realistic on a single 3060 — the experiment cannot distinguish schedule effects from seed noise for expected effect sizes.

**Action.** Remove from independent promotion queue. In Candidate 13's scope-check, add as a within-paper ablation: one 3-condition × 30-seed sweep on 4-layer nanoGPT / Shakespeare-char — constant-best-`lambda`, linear-decay, time-averaged-matched constant — reported as "schedule ablation" in C13's appendix. Compute cost: ~1 week of Candidate 13's existing budget. If positive with p < 0.01 and effect size > 3 %, *then* justifies a follow-up paper; if not, the negative result sits in C13's §7.

**Rubric (standalone).** D = 5 (infrastructure inherited from C13); N = 1 (scheduled coefficients are a generic design pattern; developmental analogy is inverted); F = 2 (kill condition permissive; no matched-lambda-eff control); C = 2 (10x under-powered at 3060 budget for 5-condition sweep); P = 1 standalone / P = 4 as C13 appendix. Composite favours fold.

---

**External sources consulted** beyond `papers.csv` / `literature_review.md`:

- Fu, Y. et al. 2019 "Cyclical Annealing Schedule: A Simple Approach to Mitigating KL Vanishing", *NAACL-HLT* — arXiv:1903.10145. Template for scheduled regulariser coefficients.
- Ichikawa, Y. & Hukushima, K. 2024 "Learning Dynamics in Linear VAE: Posterior Collapse Threshold, ..., and Speedup with KL Annealing", *AISTATS* — arXiv:2310.15440. Theoretical analysis of scheduled `beta`.
- Achille, A., Rovere, M. & Soatto, S. 2019 "Critical Learning Periods in Deep Neural Networks", *ICLR* — arXiv:1711.08856. The deep-learning developmental-plasticity analogy paper Candidate 16 does not cite.
- Kleinman, M., Achille, A. & Soatto, S. 2023 "Critical Learning Periods Emerge Even in Deep Linear Networks" — arXiv:2308.12221.
- Morerio, P. et al. 2017 "Curriculum Dropout", *ICCV*. Regulariser-coefficient annealing precedent.
- Bowman, S. R. et al. 2016 "Generating Sentences from a Continuous Space", *CoNLL*. Original KL-annealing in VAE text models.
- Loshchilov, I. & Hutter, F. 2019 "Decoupled Weight Decay Regularization", *ICLR*. Weight-decay-schedule precedent.
- Power Lines 2025 — arXiv:2505.13738. Weight-decay-vs-step scaling-law paper.
- Jastrzebski, S. et al. 2020 "The Break-Even Point on Optimization Trajectories of Deep Neural Networks", *ICLR*. Early-phase-of-training matters; foundation for ML-internal (non-biology) justification of high-`lambda`-early.
- Frankle, J., Dziugaite, G. K. et al. 2020 "The Early Phase of Neural Network Training" — arXiv:2002.10365.

Word count: ~1470.
