# Phase -0.5 Scope Check - Candidate 19

**Target.** Sleep / wake analogue. Compare σ, α, crackling-noise exponents during *training* (backprop active, weights updating) vs *inference* (forward-only, frozen weights) on the same model. Map to cortical sleep-spindle vs active-waking avalanche regimes. Cited anchors: Meisel 2013 (1031, mis-ID'd as 1034 in candidate_ideas.md) + Meisel 2017 (1032, mis-ID'd as 1035).

**Reviewer inputs.** `literature_review.md`, `knowledge_base.md`, `lit_neuro.md §§Theme 6`, `papers.csv` (1031, 1032, 1017 Priesemann 2013), `candidate_ideas.md` (C3, C13, C21), `promoted.md`, arXiv 2024-2026 scan.

**Verdict up front: KILL as stated. REFRAME as "brain-state-analogue on frozen checkpoints" is possible but is a strictly weaker version of Candidate 21 (base-vs-RLHF) plus the seed-panel leg of Candidate 12. Recommend: do not promote; fold any salvageable content into Candidate 3 §appendix.**

The candidate sits on a category error about what "training mode" means in the PyTorch sense, the biological analogy is decorative rather than mechanistic, and the one experiment that would actually be scientifically interesting (activation statistics as a function of *how freshly updated* the weights are) is already in Candidate 3 by construction.

---

## 1. The category error (reviewer's concern 1, answered)

The brief flags the central issue: "backprop doesn't change forward-pass activations within a single step; the asymmetry must come from across-step weight changes accumulating." That framing is correct and is the fatal one for the candidate as written. Three distinct things are being conflated:

- **(i)** `model.train()` vs `model.eval()` PyTorch mode switches. These only affect dropout and BatchNorm/LayerNorm running statistics. In a decoder-only transformer without dropout at eval (GPT-2 / Pythia default), the forward pass is bit-identical between the two modes. Any σ/α difference would be a dropout artefact, not a criticality observation. Training-time dropout is a literal Bernoulli mask that *does* change branching statistics by construction; testing whether dropout changes branching is a 2-hour experiment with a trivial positive result, not a paper.
- **(ii)** Activations on the same input (a) at weights *w_t* and (b) at weights *w_{t+1}* = *w_t* − η∇L. The asymmetry here is of order η‖∇L‖·‖∂h/∂w‖, i.e. vanishingly small within a single step. Across many steps the drift *is* exactly the Candidate 3 observable σ(t), α(t), ρ(t) through training. Candidate 19 as written adds no observable that Candidate 3 does not already produce.
- **(iii)** Activations at a recently-updated checkpoint vs the same checkpoint after additional training steps on the same data distribution (the "offline consolidation" analogy). This is closer to the biological intuition but is just pair-differencing two points on the Candidate 3 trajectory.

None of (i)-(iii) individually constitutes a new observable. (i) is a dropout-regularisation artefact. (ii) collapses into Candidate 3. (iii) is a secondary statistic on Candidate 3's output. That is the reviewer's concern 1 confirmed.

## 2. Conflation of training-vs-inference *model state* with training-vs-test *data* (reviewer's concern 2, answered)

The candidate writes "during training, on activations from training steps" vs "post-training, on the same model frozen, same inputs." The proposal then says "same inputs" for both. If the inputs are truly identical and the weights are identical, the forward pass and therefore all activation statistics are identical modulo dropout noise. So the candidate cannot mean "same inputs, same weights" — it implicitly means one of:

- **Training-data activations** captured as the model sees them mid-training (i.e. at a non-final weight configuration, on possibly-non-i.i.d. batches), vs **held-out inputs** on the final frozen model;
- **Training-distribution inputs** at the final model vs **novel-distribution inputs** at the final model.

These are actually distinct comparisons. The first conflates time-in-training with data-distribution; the second is a pure distribution-shift test (train-set vs OOD). Neither is a sleep/wake analogue in any biologically meaningful sense; the second is a distribution-shift study that has a large ML literature already (OOD detection, DomainNet-style evaluation). The candidate as written does not pick one of these and therefore is unfalsifiable — whatever result is obtained can be attributed to either axis.

## 3. arXiv 2024-2026 scoop check

I searched for training-mode vs inference-mode activation statistics on transformers, with and without the criticality framing. No paper in 2024-2026 runs the Candidate 19 experiment as written, because (per §1) the experiment as written is ill-posed. Adjacent hits:

- **Wang 2026a/2026b (arXiv 2604.16431, 2604.04655).** Tracks dimensional criticality D(t) and avalanche-probe cascade dimension through training and through the grokking transition. This is the Candidate 3 / Candidate 4 scoop already noted in `promoted.md`. Candidate 19's "training trajectory" content is fully covered by Wang's trajectory data.
- **arXiv 2508.03616 "Hidden Dynamics of Massive Activations in Transformer Training" (2025).** Characterises emergence of massive (outlier) activations through training; closest live work to what Candidate 19 could mean if reframed as "how do tail activation statistics evolve through training." Again, this is a Candidate 3 observable, not a sleep/wake observable.
- **arXiv 2603.17811 "Dropout Robustness and Cognitive Profiling of Transformer Models via Stochastic Inference" (2026).** Directly characterises how 19 transformers behave under train-mode (dropout-active) inference via MC-dropout. If the candidate *was* a dropout paper, this scoops it. It is not framed as criticality.
- **arXiv 2509.22358 "Stochastic Activations" (2025).** Studies deliberately inserting stochasticity at inference to approximate dropout-training noise. Again, if Candidate 19 collapsed to "dropout's effect on branching," this is adjacent.
- **arXiv 2401.08623 "Wake-Sleep Consolidated Learning" (2024).** Uses a *literal* wake-sleep training loop (alternating "wake" training on new data and "sleep" replay consolidation) for continual learning. This is the real ML precedent for a sleep-wake analogue and it is an algorithm, not a criticality observable. It also precedes the candidate and would own the "sleep-wake in LLMs" framing in any venue.

**Novelty verdict: LOW-TO-NONE** on the specific observable; Wang 2026a/b already provides training-trajectory criticality observables and will beat any Candidate 19 submission to press. The "sleep/wake" framing is owned by 2401.08623 for the general ML audience and by Meisel 2013/2017 for the neuro audience — neither of which is our story.

## 4. The biological analogy is cosmetic, not mechanistic (reviewer's concern 4, answered)

Sleep/wake in cortex is defined by at least four axes, none of which have a clean LLM analogue:

- **Neuromodulation.** Wake: high acetylcholine, high noradrenaline, low adenosine. Sleep: inverted. This shifts excitation/inhibition balance and changes the effective connectivity — exactly the knob Meisel 2013 attributes the σ → 1.45 supercritical drift to during sustained wakefulness. Transformers have no neuromodulator. Temperature and top-k sampling are decoding-time knobs, not activation-time.
- **Thalamocortical coupling.** Slow-wave sleep is defined by synchronised thalamocortical up/down states. Transformers have no thalamus analogue; there is nothing gating input relay.
- **Input drive.** Wake = rich external drive; sleep = endogenous replay-driven activity. Training gets gradient signal; inference gets none. But the forward-pass activation is identical at fixed weights regardless of whether a backward pass follows. So the input-drive axis does not separate the two modes at the activation level.
- **Synaptic homeostasis.** Tononi-Cirelli's "wake potentiates, sleep renormalises" narrative (cited in `lit_neuro.md` §Theme 6) makes the testable prediction that σ rises during wake (confirmed by Meisel 2013: σ = 1.17 → 1.45 across 30+ hours of sustained wake) and falls during recovery sleep. The LLM analogue would require a weight-normalisation operation that preferentially follows training — weight decay does this, and it runs throughout training, not in distinct phases. Any sleep-analogue experiment would need to construct a deliberate phase structure (train phase + "rest" phase with weight decay only, or SWA / EMA consolidation, or an explicit Wake-Sleep Consolidated Learning setup per 2401.08623) — at which point it is an intervention paper, not a measurement paper.

The biological mapping does not survive the first level of mechanistic inspection. Keeping the "sleep/wake" label would be a reviewer red flag; the `lit_neuro.md` file itself notes "the sleep-wake axis is distinct from the criticality axis" (paraphrase of Theme 6's two-axis picture), which further undermines Candidate 19's simple conflation.

## 5. Relationship to Candidate 3 (reviewer's concern 5, answered)

Candidate 3 is already promoted as the core of Paper 3 (dynamics). It tracks σ(step), α(step), ρ(step) across training on ~20 checkpoints × 3 init regimes × 5 seeds. Candidate 19 reframed-charitably is "also look at the final frozen checkpoint." The final frozen checkpoint *is* a point on the Candidate 3 trajectory. There is no ≥2 weeks of extra work that Candidate 19 unlocks; at best, it adds a single paragraph to Candidate 3's §5 or §6: "the endpoint of the σ(step) trajectory is the frozen inference-time observable; the trajectory itself is the training-time one; the gap between them is *not* a mode-switch asymmetry, it is time-integrated drift."

That paragraph does not need a separate 2-week scope; it needs one figure in Candidate 3. The candidate as a standalone work item therefore has near-zero marginal contribution over the already-promoted Paper 3.

The ~2-week cost estimate in the candidate is also internally implausible. "Capture activations on a held-out batch mid-training (model weights frozen on that batch); compare to same model fully trained on same batch" is a checkpoint load + forward pass + activation caching — on the order of hours, not weeks, *if* Candidate 3's checkpoints already exist, which they will.

## 6. What could be salvaged

Three potentially-interesting pieces, all of which are already owned elsewhere:

- **σ shift under dropout-on vs dropout-off at the same weights.** A legitimate branching-statistics question; scoped at a few hours; result is deterministic from theory (dropout kills σ by subsampling per 1014 Hahn / 1015 Priesemann-MR). Not a paper; maybe a footnote in Paper 1.
- **σ shift under RLHF vs base.** This is Candidate 21 and is already in the promotion queue with a clear biology mapping (RLHF as "narrowing" is a crude analogue to the damping action of slow-wave sleep on supercritical drift). Candidate 21 is cleaner because it has two distinct public checkpoints of the same architecture rather than a handwave about mode-switching.
- **DFA exponents of activations as a second proxy for criticality.** Meisel 2017 (1032) uses DFA of EEG as a low-cost proxy. DFA of residual-stream activations across token time is trivially computable and sits naturally as a §7 cross-check in Paper 1. Already noted as a candidate observable in `papers.csv` row 1032 annotation.

None of these three redeems Candidate 19 as a standalone project; all three have homes elsewhere in the five-paper programme.

## 7. Falsifiability verdict

The pre-registered kill — "if no statistically-detectable difference, the mode-asymmetry claim dies" — is essentially guaranteed to trigger because, per §1, there *is* no first-order mode-asymmetry at the activation level on a dropout-off decoder-only transformer. A study whose kill condition is "the thing we can compute gives zero by construction" is not falsifiable in the Popperian sense; it is predetermined.

## 8. Rubric and final verdict

| Axis | Score | Note |
|---|---|---|
| D (data availability) | 5 | Checkpoints from Candidate 3 suffice; no new data needed. |
| N (novelty) | 1 | Observable is ill-posed; closest reframings are scooped by Wang 2026a/b (dynamics), WSCL 2401.08623 (sleep-wake framing), and covered by Candidates 3 / 21 internally. |
| F (falsifiability) | 1 | Kill condition triggers by construction at fixed weights; the "asymmetry" the candidate predicts does not exist at the activation level. |
| C (compute) | 5 | Cheap if built on Candidate 3 — but cheap × pointless is still pointless. |
| P (publishability as standalone) | 1 | Neural Computation workshop at best; the biological framing will not survive review by a neuro reviewer who knows Meisel 2013. |

**Verdict.** **KILL as a standalone candidate.** Not a separate paper. Do not promote. Update `promoted.md` to mark Candidate 19 as "absorbed / killed after scope-check; any salvageable content folds into Candidate 3 endpoint analysis or Candidate 21 (base-vs-RLHF σ shift)."

**Action items.**
1. Fix citation IDs in `candidate_ideas.md`: Meisel 2013 = 1031 (not 1034); Meisel 2017 = 1032 (not 1035). ID 1034 is Zimmern 2020 scoping review; ID 1035 is different again.
2. Update `promoted.md` row 19 verdict from "pending" to "KILL - absorbed into Candidate 3 endpoint figure / mentioned in Candidate 21 intro as wake-drift motivation."
3. Do *not* spend 2 weeks on this; redirect the freed budget to the already-promoted Paper 3 (Candidate 3+4) reframe work which is on the critical path.

---

*Wordcount: ~1470.*

Sources consulted beyond repo files: arXiv 2603.17811, 2509.22358, 2508.03616, 2401.08623, 2604.16431, 2604.04655; Meisel et al. 2013 *J. Neurosci.* 33(44):17363 (σ = 1.17 → 1.45 across sustained wakefulness); Tononi & Cirelli 2014 *Neuron* synaptic homeostasis hypothesis (cited via `lit_neuro.md` §Theme 6).
