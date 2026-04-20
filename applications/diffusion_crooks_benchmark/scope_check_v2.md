# Scope Check v2 — diffusion_crooks_benchmark

Round 2 of 3. Reviewer: grouchy ML-theory / stochastic-thermodynamics.
Inputs: `program.md` (Phase −0.5) and `proposal_v2.md`. Not read: v1 artifacts.

## 1. Novelty of the training-dynamics pivot

Measuring an empirical Crooks-ratio slope β̂(k) during DDPM training is, as far as I can tell, *not* a named diagnostic anywhere in the 2023–2025 generative-modelling literature. What has been tracked during training is the ELBO, the score-matching loss, FID, and (more recently) the per-timestep loss curve à la Karras et al. and the log-likelihood gap of Masrani/Wu/Wood's TVO. None of these is β̂(k). The closest neighbour is Grosse et al.-style AIS log-Z estimates on intermediate checkpoints, but those report ratios of partition functions, not the slope of the forward-vs-reverse work-ratio log. So the pivot is *plausibly* novel — call it "weakly novel." The risk is that once Phase 0 runs, someone at ICML 2024/25 will turn up having already tracked a per-step fluctuation-theorem residual on a toy diffusion. I would estimate ~25% probability that exact prior art exists and has simply not been cited yet. The proposal's promise to search ICLR/NeurIPS/ICML/TMLR 2023–2026 for "ELBO-gap" and "training-dynamics + fluctuation" terms is correct but needs to include "consistency violations", "detailed balance residual", and "score-matching residual" as synonyms.

## 2. Falsifiability

O2, O3, O4, O5 are genuinely binary and genuinely falsifiable. Good.

O1 is borderline. "β̂(0) ≠ β at random init" is close to the tautology "an untrained network is not a trained network." The proposal half-recognises this by adding the alternative branch ("consistent by accident → task is trivial"), but both branches still amount to a sanity check, not a test of a substantive claim. Recommend reframing O1 as a *calibration* check, not a kill-outcome, and elevating O4 or O5 to compensate. With that edit, five truly-falsifiable kills drop to four, which is still acceptable.

## 3. Does TMLR actually want this?

Maybe. TMLR publishes diagnostics without requiring SOTA, and the bar is "rigorous and reproducible, of interest to some subset of the community." β̂(k) clears that bar *if* the paper demonstrates it sees something ELBO does not — e.g. schedule-dependence that is invisible in the loss curve, or a κ that saturates later than the loss does. If the β̂(k) and the loss curve turn out to be essentially redundant, the paper is a toy curiosity and TMLR will reject on "insufficient contribution." The proposal's O3/O4 structure allows this outcome to be reported either way, which is healthy.

## 4. Scope transfer

Stopping at 2-D is the honest move and the proposal acknowledges that β is not analytically available in higher dimensions. But a paper that measures a diagnostic only on 1-D Gaussian + 2-D mixture-of-Gaussians cannot claim the diagnostic is practically useful — only that it is *well-defined and measurable*. This is acceptable for TMLR as a methods paper but *only if* §1 and the abstract are rewritten to advertise a measurement-framework contribution, not a training-diagnostics contribution. One real-data extension where β is estimated rather than analytically known (e.g. a learned near-Gaussian surrogate on MNIST-2) would substantially widen the usable range without re-introducing the tautology. Strongly recommend adding this.

## 5. Top three killer objections

**K1 — "Your diagnostic is redundant with the ELBO loss." (MAJOR.)** If β̂(k) convergence rate κ correlates ≥ 0.95 with ELBO-loss convergence rate across the two schedules, the β̂(k) signal contains no independent information and the paper becomes a reformulation. *Mitigation:* pre-register a decorrelation threshold (|ρ| ≤ 0.8) as an additional kill-outcome O6, and design the schedule perturbation to maximise expected β̂/ELBO decoupling.

**K2 — "1-D / 2-D Gaussian is too small to matter." (MAJOR.)** A reviewer will object that a diagnostic demonstrated only on analytically-tractable toys is a curiosity. *Mitigation:* add the MNIST-2 or ring-distribution extension described in §4 above, with β estimated numerically and error bars reported.

**K3 — "Prior art exists and you missed it." (MAJOR → FATAL if realised.)** The Phase 0 lit search must explicitly include "detailed-balance residual," "reverse-process consistency," "trajectory-asymmetry loss," "CFT residual on diffusion models," and scan the 2023–2025 score-based-modelling training-dynamics literature (e.g. Karras, De Bortoli, Song post-2022). *Mitigation:* pre-commit that if any 2023–2025 paper tracks a slope-like fluctuation-theorem quantity during training, the project immediately reframes to a measurement-rate / schedule-dependence study and the novelty claim is dropped.

Minor issue: O1 is not a real kill. Demote to calibration.

## Verdict

The v1 objections are adequately addressed. The pivot is defensible. The scope is narrow but honest. The five kill-outcomes are 4/5 genuinely falsifiable (O1 weak, see above). TMLR fit is plausible contingent on either (a) demonstrating ELBO-β̂ decorrelation, or (b) adding a real-data extension. The proposal as written is acceptable to proceed; required edits are tracked in K1–K3 and the O1 demotion and should be carried into `research_queue.md` as `pre-empt-reviewer` hypotheses in Phase 0.

VERDICT: PROCEED
