# Phase -0.5 Scope-Check - Candidate 22

**Candidate.** Spiking-transformer direct biological comparison - train a small spiking transformer (SpikFormer / SpikeGPT via surrogate gradients), apply the identical Beggs-Plenz avalanche-detection pipeline to its spike raster, and compare to published cortical spike data.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, leaning KILL-as-standalone.** Candidate 22 is the most superficially exciting of the extension round and the most methodologically dangerous. The literal-brain-analogue framing begs the question; the 4-week budget on one RTX 3060 is not survivable for from-scratch surrogate-gradient training of even a small SpikeGPT; the novelty gap against Candidate 18 (cross-universality-class, LLM vs cortex) is narrow and in the wrong direction. Reframe as either (a) an inference-only analysis on **publicly-released pretrained SpikeGPT-216M / Spikingformer weights**, bundled as a second arm of Paper 7 alongside Candidate 18 and Candidate 20; or (b) kill, citing the spike-raster-on-transformer framing as a confound-inviting exercise whose positive result would be a tautology and whose negative result would be uninformative.

## 2. Codebase and weights availability, 2026-04

Citation corrections required. **SpikeGPT is arXiv:2302.13939** (Zhu, Zhou, Eshraghian 2023), not 2311.01792; code at `github.com/ridgerchu/SpikeGPT`; 45M and 216M pretrained weights public; RWKV-style linear attention replaces softmax. **Spikformer** (Zhou et al. 2023, arXiv:2209.15425) is an image classifier, not a LM - wrong base for the TinyStories plan. **Spikingformer** (arXiv:2304.11954, AAAI 2026) is image-focused but backbone for several 2025-26 LM derivatives. **snnTorch** (Eshraghian 2023, Proc. IEEE) is production-grade but ships no LM reference architecture.

Adjacent LM-oriented releases: **SpikeBERT** (Lv 2025, distilled BERT, not autoregressive); **SpikingMiniLM** (2025 NLU-tuned); **Winner-Take-All Spiking Transformer for LM** (arXiv:2604.11321, 2026, weights TBV); **Quantized Spike-Driven Transformer** (ICLR 2025 arXiv:2501.13492, vision).

**Production-grade for this candidate:** only SpikeGPT-216M has publicly-released pretrained autoregressive LM weights matching the "small spiking transformer on natural text" target. Training a second copy from scratch adds nothing.

## 3. Training feasibility on RTX 3060 / 4-week budget

**The candidate's own cost estimate (4 weeks, from-scratch on TinyStories) is unrealistic on a single RTX 3060 12 GB.** SpikeGPT-216M required ~48 V100-hours for the public checkpoint (Zhu 2023 used T=1024 context, T=4 spike steps, batch 8, 8xV100). Surrogate-gradient training stores activation and membrane-potential tensors for all T time-steps on the backward pass - memory O(T*L*d). RTX 3060 12 GB has ~0.20x V100-32GB bandwidth and ~0.15x FP16 throughput; at matched batch size memory exceeds VRAM; at reduced batch step time grows super-linearly from optimiser-state overhead. Realistic from-scratch SpikeGPT-45M training: 14-21 wall-clock days at TinyStories scale, assuming no debugging.

**arXiv:2511.08708 (Nov 2025)** "Stabilizing Direct Training of Spiking Neural Networks: MP-Init and Threshold-robust Surrogate Gradient" confirms out-of-the-box surrogate training is unstable for deep / transformer SNNs without membrane-potential-initialisation tricks. MP-Init + TrSG on top of SpikeGPT is another 1-2 weeks of engineering before stable training is confirmed. Guo 2024 and 2025 follow-ups document surrogate-gradient estimator bias; published stable recipes are for image classification, not autoregressive LM.

**Realistic path on one RTX 3060 in 4 weeks:** inference-only on SpikeGPT-216M public weights. Generate spike rasters on TinyStories / Pile prompts; no training. This is a different project from the one proposed.

## 4. Has a trained spiking transformer been shown at criticality on its task?

**No, not reported as of 2026-04.** The critical-SNN literature is dominated by reservoir-computing and E-I-balanced models (Nature Sci. Rep. 2025 s41598-025-18004-y mean-field LIF reservoir criticality; biorxiv 2025.11.17.688775 balanced-E-I criticality; arXiv:2512.18113 intrinsic-vs-latent criticality in spiking populations). These are random-weight or plastic networks, not trained autoregressive LMs. **arXiv:2311.16141** (Brain-Inspired Pruning via Criticality in SNNs, 2024) uses a branching-ratio-proxy pruning criterion on a classification SNN - adjacent, not transformer, not natural text, not a rigorous CSN + crackling-noise audit. No 2024-2026 paper measures cortex-scale avalanche exponents (α, β, γ, shape collapse, σ) on a trained spiking transformer's spike raster - the gap is real. Training-stability literature (arXiv:2511.08708, the Guo line) suggests typical trained SNNs are off-critical (saturated or quiescent); stabilisation tricks tune them to a useful activity level, not necessarily σ ≈ 1. Whether SpikeGPT-216M is critical on TinyStories is an open question with plausible negative outcome.

## 5. The literal-brain-analogue claim: a tautology risk

The candidate's core framing - "makes the brain-LLM comparison literal: spike-level observation on both sides" - is the sharpest conceptual weakness. A spiking transformer is a brain-inspired engineering artefact: LIF neurons with surrogate gradients are a design choice motivated by biological mimicry. A positive result (cortex-like avalanches) partly restates the mechanistic recipe the architecture builds in; the inference "brains and LLMs share a universality class" does not transfer from SpikeGPT to standard transformers. Candidate 18 - avalanche exponents on *standard* transformer residual-stream activations vs cortex - is the scientifically stronger question precisely because the architectures are dissimilar. A negative SpikeGPT result is also low-content: SpikeGPT is an engineering approximation of an SNN trained on text, not a cortex model.

**Reframe that survives.** Use SpikeGPT as a *positive control* within Paper 7 (brain-homology). Report exponents on SpikeGPT alongside GPT-2 residual-stream avalanches and cortical data. The three-way comparison is informative because the spiking transformer is a principled architectural interpolation between standard transformer and cortex.

## 6. Cortical comparison dataset

The original Beggs-Plenz 2003 slice recordings are not in a public archive under that paper itself (shared on request from Indiana for years). The right public targets are:

- **CRCNS ssc-3 (Somatosensory cortex 3)** - Beggs group deposit: spontaneous spiking from 512-electrode arrays on mouse somatosensory cortex slice cultures. Free account + terms-of-use. Primary target for spike-raster-level avalanche comparison. Ma-Turrigiano-Wessel-Hengen 2019 (paper 1013) data on Hengen lab figshare + CRCNS.
- **Allen Institute Neuropixels** - awake mouse V1, up to 500 simultaneous units per probe, public via `allensdk`. A different universality-class question (awake-behaving vs slice culture). Secondary target.
- **Shriki 2013 MEG data** (paper 1011) - public human resting MEG; coarser, tertiary check.

Event-definition is the hazard. Beggs-Plenz 2003 binned at minimum inter-event interval (1-4 ms), thresholded LFP, called an avalanche a set of contiguous active bins. Neuropixels uses spike-sorted times. SpikeGPT spikes are already binary per-neuron per-time-step. Matching the three pipelines on the same event / avalanche / threshold choice must be pre-registered. **Verify CRCNS account access before Phase 0** (per the `feedback_verify_data_access_before_phase_0` memory rule).

## 7. Novelty vs adjacent 2024-2026 literature

arXiv:2311.16141 establishes criticality observables can be computed on trained SNNs (adjacent, not SpikeGPT). Nat. Sci. Rep. 2025 s41598-025-18004-y gives the theoretical baseline (theory, no transformer). arXiv:2512.18113 (Dec 2025) provides transient-perturbation methodology to disambiguate intrinsic from latent criticality in spiking populations - must be cited and used as a control if C22 proceeds. SpikeGPT (arXiv:2302.13939) itself does not report avalanche statistics. Candidate 18 (LLM vs cortex universality class) is the cleaner question; C22 is one architectural arm and treating it as independent double-counts. **Verdict:** gap is real but narrow; result is uninformative about standard LLMs; natural home is one cell of Paper 7's cross-architecture universality table alongside C18 (dense) and C20 (SSM / MoE) plus cortical baselines.

## 8. Pre-registered kill and rubric

Candidate's own kill ("exponents outside published cortical CI → literal-brain-analogue dies") is inadequate - see §5. Stronger kill: inference-only on SpikeGPT-216M public weights; pre-register event definition, bin width, subsampling correction; report exponents on three systems under identical pipeline - (i) SpikeGPT-216M spike raster on TinyStories/Pile, (ii) GPT-2 residual-stream avalanches on matched text (from Paper 1), (iii) cortex baseline (CRCNS ssc-3 or Neuropixels). Positive claim requires universality-class match (α, β, γ, shape function F) between SpikeGPT and cortex *and* informative match/mismatch vs standard GPT-2, revealing whether architecture or training drives the similarity. Negative outcome publishable as a constraint on the spiking-transformer-as-brain-model narrative.

**Rubric.** D = 4 (public weights + CRCNS + Allen all accessible in reframed form). N = 2 standalone / N = 4 as Paper-7 arm. F = 3 (three pre-registered exponent tests across three systems, shape collapse, event-definition pre-registration). C = 2 as written (from-scratch training infeasible) / C = 4 reframed (~3 weeks inference + cortex download + pipeline reuse). P = 1 standalone / P = 4 as Paper-7 arm (*Neural Computation* / *PRX Life* / bridge venue).

**Composite:** PROCEED only as an inference-only arm of Paper 7, bundled with C18 and C20. Do not promote as a standalone 4-week project.

## 9. Action items

1. Fix the SpikeGPT citation in `candidate_ideas.md` (2302.13939, not 2311.01792). Drop "SpikFormer" as the LM base; SpikeGPT-216M or Spikingformer-LM is the right target.
2. Strike the "train from scratch on TinyStories" phrasing; replace with "analyse pretrained SpikeGPT-216M public weights in inference mode".
3. Pre-register cortex dataset choice (CRCNS ssc-3 primary; Allen Neuropixels secondary) and register a CRCNS account before Phase 0 (per memory rule: verify data access before Phase 0).
4. Move Candidate 22 from "standalone extension" to "second arm of Paper 7 (brain-homology)" in `promoted.md`, alongside Candidate 18 (primary) and Candidate 20 (architecture-class).
5. In Paper 7's scope, specify the three-way comparison (standard transformer / spiking transformer / cortex) so the spiking-transformer arm contributes an architectural-interpolation result rather than a literal-analogue claim.
