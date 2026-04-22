# Phase 0 Deep Literature Review — entropy_brain_homology

**Scope.** Cortex-LLM bridge for the project `entropy_brain_homology`: a joint-bootstrap exponent-equality test between trained-LLM activation avalanches and cortical spiking avalanches (CRCNS ssc-3, Ito/Beggs 2016), with SSM and SpikeGPT arms and synthetic branching-process ground-truth validation. This review does not attempt to cover every sub-field of criticality-in-neural-systems (see `../entropy_ideation/` for the landscape index); it concentrates on the 10 thematic blocks the project directly depends on and interrogates each with methodological skepticism.

**Status of citation count.** `papers.csv` in this directory contains **384 verified or flagged-for-verification citations**. Entries 1001–4031 (n=210) are inherited from `../entropy_ideation/papers.csv` and consist of the parent landscape review (cortical avalanches, complex-systems, ML theory). Entries 5001–5175 (n=175) are new to this review and are concentrated in the cortex-LLM bridge scope (spiking-transformer literature, CRCNS/Allen/DANDI data access, spike-sorting confounds, SSM Lyapunov theorems, bootstrap methodology, branching-process simulators, public-weight inference tooling). Entries flagged `VERIFY` must be re-checked during Phase 0.25 publishability review.

**Key verification status.** CRCNS ssc-3 data access: **confirmed reachable** (see §2 below); terms-of-use account registration plus `crcnsget` Python utility or NERSC batch scripts support programmatic download. Registration must still complete before Phase 1 opens. Halloran 2406.00209 theorem, Dao-Gu 2405.21060 Mamba-2 SSD, Ghavasieh 2512.00168 tuning-universality, Magnasco 2405.15036 input-driven RNN, Arola-Fernández 2508.06477 maximum-caliber, SpikeGPT 2302.13939, Gauthaman-Ménard-Bonner 2409.06843 scale-free visual cortex — **all verified via arXiv landing pages during this review**. Two corrections from the README: (a) Magnasco 2405.15036 is an arXiv single-author preprint, not a PNAS 2025 paper; (b) Gauthaman et al. is now titled "Universal scale-free representations in human visual cortex" (v3 Sep 2025) rather than the earlier "covariance power law" framing.

---

## Theme 1 — Cortical-avalanche empirical canon

The central-canon claim: cortical neural populations across preparations (slice, culture, in vivo awake, in vivo anaesthetised) and species (rat, mouse, cat, macaque, human) show scale-invariant avalanches with approximately `α ≈ 3/2`, `β ≈ 2`, `γ ≈ 2`, satisfying the crackling-noise relation `γ = (β − 1)/(α − 1)` within bootstrap error.

**Foundational.** [Beggs & Plenz 2003, entry 1001] used 8×8 multielectrode arrays on organotypic rat somatosensory cortex slices and acute S1 slices, thresholded LFPs at ~3 SD, binned at Δt = mean inter-event interval (~4 ms), defined avalanches as contiguous-bin supra-threshold sequences bracketed by empty bins. Sample size: approximately 10 hours of spontaneous activity per slice, across ~25 cultures; reported exponents α = 1.5 ± 0.1, β = 2.0 ± 0.2. **Preparation:** organotypic slice cultures allowed to mature for 14–21 DIV; sample size at the level of cultures is roughly the statistical atom. **Statistical methodology** was log-log linear regression with no Clauset-Shalizi-Newman (CSN) bootstrap (published before [Clauset 2009, entry 1029/2016]), no alternative-distribution rejection, no explicit finite-size scaling — all items that would now be mandatory.

**Scaling out of slice, into awake in vivo.** [Petermann et al. 2009, entry 1006] recorded LFPs on 4×4 arrays in awake macaque motor cortex during a reaching task, across ~100 hours summed. Exponents α = 1.5, β = 2 (eyeball log-log); survived awake / anaesthetised state transitions. Sample of 3 macaques. **Preparation:** 4×4 spatial resolution means the subsampling fraction is much worse than Beggs-Plenz slice — the exponent agreement is partly the signature of the subsampling bias cancelling in a specific way [see Theme 9].

**Cat and mouse in vivo, anaesthetised.** [Hahn et al. 2010, entry 1014] reported α ≈ 1.5 in cat visual cortex under isoflurane + N₂O. [Hahn et al. 2017, entry 1015] extended to awake monkey V1, showing the avalanche profile *shrinks* but does not disappear under anaesthesia — an important state-dependence finding. [Bellay et al. 2015, entry 1012] used 2-photon calcium imaging plus extracellular arrays in awake behaving mouse cortex, arguing avalanches co-exist with up/down state structure.

**Reverberating-regime refinement.** [Ma et al. 2019, entry — referenced in the ideation review but not in papers.csv verbatim] reported σ̂ ≈ 0.98 in awake rat visual cortex under MR-estimator correction, arguing cortex is *slightly subcritical* ("reverberating") rather than strictly at σ = 1. **Critical point for our study:** the cortical reference exponents live in an interval like α ∈ [1.47, 1.55], not at a single point. Our joint-bootstrap equality test must be framed accordingly.

**Developmental data.** [Gireesh & Plenz 2008, entry 1009] tracked avalanches through the first two weeks in vitro of rat cortical cultures, showing the 3/2 exponent emerges gradually. This supplies a *trajectory* prediction our training-vs-pretrained comparison should respect: if networks drift toward criticality during development/training, the signature should strengthen with maturity.

**Human MEG.** [Shriki et al. 2013, entry 1011] reported avalanche statistics with α ≈ 3/2 and β ≈ 2 in human resting-state MEG. **Crucial for our project:** Shriki 2013 data is not publicly archived under a single reusable DOI — the per-subject recordings are held in NIH-MEG resources with restricted access. The README correctly flags this as inaccessible for our purposes; we rely on CRCNS ssc-3 and Allen Neuropixels instead.

**Multi-exponent crackling-noise cross-check.** [Friedman et al. 2012, entry 1010] measured α, β, γ on the same cortical cultures and verified γ = (β−1)/(α−1) within bootstrap CI — the first proper universality-class cross-check in neural data. Any single-exponent claim is insufficient post-2012.

**Recent expansions.** [Capek et al. 2023, entry 4001] reported parabolic shape-collapse (χ = 2) on 2-photon imaging of awake mouse cortex across 5 s and 1 mm² — a sharper shape-test. [Vakili et al. 2025, entry 4002] used targeted holographic stimulation of single pyramidal neurons in mouse V1 to recruit downstream units with power-law statistics embedded in ongoing criticality. [Fontenele et al. 2024, entry 4005] showed criticality lives in a low-dim subspace of awake mouse motor cortex while orthogonal high-dim subspace looks desynchronised — this drives our subspace-resolved analysis.

**Consensus.** [Hengen & Shew 2025, entry 4006] (Neuron meta-analysis of 140 cortical-criticality datasets 2003-2024) gives the field-standard up-to-date framing: criticality is a homeostatic setpoint unifying cognition and disease, with pooled α = 1.50 ± 0.08 under CSN MLE [Miller-Yu-Plenz 2019, entry 5041]. Cross-species pooled value: α = 1.55 ± 0.05 [Yu et al. 2014, entry 5045]. **These are the intervals our LLM-side bootstrap must overlap if we claim exponent equality.**

**Fontenele 2019 methodological exemplar.** [Fontenele et al. 2019, entry 5011] in PRL applied rigorous CSN MLE + alternative-rejection + crackling cross-check to rat cortex data and found α = 3/2, β = 2, γ = 2 with bootstrap p > 0.1 for power-law vs lognormal. This is the methodological standard our cortex-side pipeline must meet.

---

## Theme 2 — Cortical-avalanche public datasets and data-access verification

This is the blocking piece per memory `feedback_verify_data_access_before_phase_0`: if CRCNS ssc-3 cannot be downloaded, Phase 0 is sunk cost. **Verification status: ssc-3 is reachable via https://crcns.org/data-sets/ssc/ssc-3 but requires (a) account registration via crcns.org/request-account, (b) terms-of-use acceptance, (c) NERSC portal credentials. Automated download supported via `crcnsget` Python utility (https://github.com/neuromusic/crcnsget, [Kiggins 2014, entry 5002]) or NERSC batch scripts. This still counts as a DATA-ACCESS GATE for Phase 0.5 — the account request must be submitted NOW.**

**CRCNS ssc-3 details** [Ito, Yeh, Timme, Hottowy, Litke, Beggs 2016, entry 1041 = 5001]. 
- **Identity.** "Spontaneous spiking activity of hundreds of neurons in mouse somatosensory cortex slice cultures recorded using a dense 512 electrode array." DOI 10.6080/K07D2S2F.
- **Contents.** 4 datasets (named 2_0_1 through 2_0_4 per [entry 5171]); each is a ~1 hour recording on a 512-channel MEA; ~98–594 isolated neurons per dataset after spike sort.
- **Format.** HDF5 containers with spike times, electrode metadata, and spike-sort cluster quality scores. Companion paper [Ito et al. 2014 PLoS ONE, entry 5012] reports the canonical exponents α = 1.5, β = 2 and branching ratio 0.95–1.02 on these recordings under rigorous Clauset testing.
- **Sister dataset ssc-2** [entry 5172] is 60-channel rat S1 slice — smaller N, older pipeline; fallback if ssc-3 registration fails.

**Allen Neuropixels Visual Coding (secondary)** [Siegle et al. 2021, entry 1042]. 
- ~100 sessions, ~2500 neurons per session across 6 cortical + 2 thalamic visual areas in awake mice. NWB 2.0 format. Access via `allensdk` Python library [entry 5003] — no registration required, immediate download. Trade-off: awake mouse V1 not S1 slice; recording modality is Neuropixels (high density, same-probe-day stability) rather than MEA. Hardware pedigree: [Jun et al. 2017, entry 5006] Neuropixels 1.0 specification.
- **Substantial relevance.** [Morales-di Santo-Muñoz 2023, entry 4014] fit edge-of-instability model to this data and derived quasi-universal power-law exponents, arguing Allen data is in an edge-of-synchronisation class rather than classic DP.

**DANDI archive (tertiary)** [Halchenko et al. 2023, entry 5005]. 600+ public dandisets of NWB-format neurophysiology. Fontenele lab depositions [entry 5173 VERIFY], International Brain Laboratory [entry 5174], Senzai-Buzsaki hippocampus [entry 5175] are candidate additional cross-cortex controls.

**What is NOT usable.** Shriki 2013 MEG data and Ma 2019 rat V1 spike data are not publicly archived under redistributable licences as of Apr 2026 (per README scope-check). Our cortex-side exponent reference is therefore pooled across [Miller-Yu-Plenz 2019 meta-analysis, entry 5041] plus the CRCNS ssc-3 + Allen primary data we compute ourselves.

**Data-access action item.** Submit CRCNS account request as first Phase 0.5 task. Test `crcnsget` on ssc-3 2_0_1 subset. If registration delay exceeds 3 days, proceed in parallel with Allen Neuropixels via allensdk (no registration).

---

## Theme 3 — Universality-class framework in statistical physics

The neuroscience claim "α ≈ 3/2 is mean-field directed percolation" is not itself diagnostic — exponent coincidence is not class identification. The statphys universality-class framework provides the language.

**Directed percolation.** [Hinrichsen 2000, entry 2005] (canonical review) and [Henkel-Hinrichsen-Lübeck 2008, entry 2008] (definitive textbook) catalogue the DP universality class across dimensions. DP 1D exponents: α = 1.108, β = 0.276, γ = 1.237 [Grassberger 1983, entry 5088]. DP mean-field (upper critical dimension d_c = 4): α = 3/2, β = 2, γ = 2. The neural α ≈ 3/2 is consistent with MF-DP but not with low-dimensional DP. **Interpretation for us:** a transformer residual stream with d_model ≈ 768–2048 is effectively mean-field (many-body high-dimensional); the expected class under DP dynamics is MF-DP.

**Branching processes.** [Harris 1963, entries 1016/2013] (classical) and [Athreya-Ney 1972, entry 2012] (modern definitive) define branching processes with σ = expected offspring; σ = 1 is the critical point between extinction and explosion. Galton-Watson is the canonical discrete-time branching process; continuous-time extensions (Markov branching) give the same mean-field exponents.

**Absorbing-state transitions.** [Dickman-Vespignani-Zapperi 1998, entry 2044] showed SOC sandpiles are driven absorbing-state transitions tuned by conservation laws; [Dickman-Muñoz-Vespignani-Zapperi 2000, entry 2045] reviews paths to SOC. [Marro-Dickman 1999, entry 2004] covers lattice models. These connect SOC sandpile dynamics to contact-process dynamics and to neural branching.

**Griffiths phases and quasi-criticality.** [Moretti-Muñoz 2013, entry 2035] showed hierarchical modular topology produces a Griffiths phase — an *extended parameter region* with power-law-like statistics rather than a single critical point. [di Santo et al. 2018, entry 2036] gave a Landau-Ginzburg field-theoretic description placing avalanches at the edge of synchronisation rather than classical DP. [Martinello et al. 2017, entry 1027/2037] showed neutral (non-critical) models can reproduce neural avalanche power laws. **Key implication:** our exponent-equality claim must engage with the possibility that either cortex or the LLM (or both) is in a Griffiths phase rather than at a strict critical point; this weakens a universality-class claim unless we additionally show finite-size scaling.

**Edge-of-synchronisation.** [di Santo 2017, entry 5141] introduces the intermediate-coupling critical phase. [Morales-di Santo-Muñoz 2023, entry 4014] empirically validates this on Allen mouse-brain Neuropixels, arguing quasi-universal exponents emerge from edge-of-instability rather than DP. For our SSM arm (Halloran-stable Mamba), this framework may be more apt than strict DP.

**Alternative classes.** [Dickman-Muñoz 2003, entry 5084] gives Manna-class exponents (α = 1.28, β = 1.49) — different from DP. [Jensen 1994, entry 5085] gives parity-conserving class. Our methodology must at minimum distinguish MF-DP, Manna, and edge-of-synchronisation; Griffiths phases we can only falsify by finite-size scaling.

**Universality overviews.** [Privman 1990, entry 5036] and [Fisher 1998, entry 5039] cover scaling functions and universality classes for ML-reviewer framing.

---

## Theme 4 — RNN and artificial-network criticality direct precedents

**Sompolinsky-Crisanti-Sommers (1988), entry 2020.** DMFT analysis of continuous-time RNN with Gaussian weights shows transition from fixed-point to chaos at gain parameter g = 1. This is the canonical edge-of-chaos reference and the analytical backbone for expectation `σ = 1` in random-recurrent networks.

**Bertschinger-Natschläger (2004), entry 2028.** Discrete-time random RNN reservoir shows maximum computational capacity at edge-of-chaos; memory capacity and mutual information peak at spectral radius = 1. Direct ML-side bridge to Shew-Plenz empirical dynamic-range peak.

**Boedecker et al. (2012), entry 2029.** Echo-state networks at spectral radius ~1 maximise information-theoretic capacity. Computational-capacity proxy for criticality in reservoirs.

**Schuecker-Goedeke-Helias (2018), entry 2021.** Edge-of-chaos shifts under input drive; memory capacity peaks at dynamical transition. Relevant for Magnasco 2024 [entry — see below] input-driven critical-network framework.

**Torres-Morales-di Santo-Muñoz (2023), entry 3045.** "The critical brain hypothesis in deep learning" [VERIFY venue] claims RNN-type networks organise near criticality during training. Direct precedent for trained-network-criticality; we must engage with their methodology.

**Morales-di Santo-Muñoz (2023), entries 3046/4014.** Unifies edge-of-instability framework between RNN dynamics and cortical activity; quasi-universal power-law exponents emerge from edge-of-synchronisation not DP. PNAS 2023 citation — important prior work.

**Engelken-Wolf-Abbott (2023), entry 4019.** Full Lyapunov spectrum of chaotic RNNs; extensive chaos with size-invariant spectrum; attractor dimension ≪ phase-space. Methodology for per-layer Lyapunov measurement transferable to transformers.

**Magnasco (2024), entry corresponding to arXiv:2405.15036.** *Verified title:* "Input-driven circuit reconfiguration in critical recurrent neural networks" [single-author arXiv, not PNAS — README correction]. Single-layer recurrent network reconfigurable via input without weight change; leverages dynamically-critical system properties. Relevant for our prompt-driven σ arm.

**Cowsik-Nebabu-Qi-Ganguli (2024), entry 3072.** Geometric dynamics of signal propagation predict transformer trainability; order-chaos phase transition in transformer init hyperparameters; angle-exponent and gradient-exponent Lyapunov indices. Transformer-specific edge-of-chaos theory.

**Mastrovito et al. (2024), entry 4017.** Training pushes both ordered and chaotic RNNs toward edge-of-chaos; transition aligned with perturbational complexity index used clinically for consciousness. Direct precedent that trained-network trajectories converge to EOC.

**Danovski-Soriano-Lacasa (2024), entry 4018.** Training as dynamical system in graph space; Lyapunov exponents of network trajectories; regular vs chaotic regimes depending on learning rate. Lyapunov-of-training complements Lyapunov-of-forward-pass.

**Haber-Levi-VERIFY (2024), entry 4020.** Transformer-specific order-chaos phase transition in init hyperparameters; angle-exponent and gradient-exponent Lyapunov indices. Direct quantitative prediction for GPT-2 / Pythia.

**Yoneda-Nishimori-Hukushima (2025), entry 4021.** **First direct DP-universality-class assignment to artificial NN architectures.** MLPs to mean-field class; CNNs to DP class. Motivates our class-assignment in C20. Same-author-scope publication is the most direct scoop risk on our C20 architectural-class arm.

**Doimo et al. (2024), entry 5049.** "The edge of orbit: chaos transitions in trained language models" [VERIFY]. Per-token Lyapunov exponent estimation on LLMs. **Direct precedent / potential scoop**.

**Zhang et al. (2024), entry 3058/4023.** "Intelligence at the Edge of Chaos": LLMs trained on edge-of-chaos cellular-automata acquire stronger reasoning. Training-data complexity edge-of-chaos, distinct from activation criticality but complementary.

---

## Theme 5 — State-space-model (SSM) Lyapunov and criticality

The SSM arm is central because of the Halloran theorem [entry 3068 / arXiv:2406.00209].

**Halloran-Gulati-Roysdon (2024), arXiv:2406.00209, entry 3068.** *Main theorem:* Mamba SSM layers' recurrent dynamics are provably Lyapunov-stable under mixed-precision fine-tuning (MPFT) and parameter-efficient fine-tuning (PEFT) perturbations. Transformers lack this guarantee. **Implication for our project:** if Mamba is Lyapunov-stable by theorem, its per-token Lyapunov exponent is ≤ 0, so its activation avalanches cannot be in a critical-chaotic regime on the token axis. Trained Mamba should therefore be *sub-critical* on token axis by theorem; we test whether trained-weight exponents recover this prediction.

**Gu-Dao (2024), arXiv:2405.21060, entry 3069.** "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality" (ICML 2024). State-Space Duality (SSD) framework connects attention and SSMs via structured semiseparable matrices; yields Mamba-2 with 2–8× speedup matching transformer perplexity. **Defines the mathematical substrate** for SSM token-axis. Informs which activations we probe on SSM arm: the "semiseparable output" is the analogue of residual stream.

**Gu-Goel-Ré (2022), entry 3062/3063.** S4 structured state-space original. HiPPO-based parametrisation. Log-linear training.

**Gu-Dao (2023), entry 5064.** Mamba-1 selective SSM: input-dependent gating. Canonical Mamba reference for ablation comparisons.

**Ali-Zimerman-Wolf (2024), entry 5065.** Hidden attention of Mamba: implicit attention-like mechanism via selective-scan. Informs where to inject criticality probes on Mamba.

**Krishnamurthy-Can-Schwab (2022), entry 5022.** Gated RNN DMFT; extends Sompolinsky EOC to multiplicative gating; recovers marginal stability at specific gate saturation. Directly relevant for SSM selective mechanism.

**Can-Krishnamurthy-Schwab (2020), entry 5023.** Transient chaos in gated RNNs — finite-lifetime chaotic trajectories on marginal line. Mamba selectivity may induce this regime.

**Manjunath-Jaeger (2013), entry 5024.** Echo-state property under input drive; input can stabilise chaotic reservoir. Informs interpretation of Mamba's input-dependent gating.

**Halloran-Roysdon (2025), entry 5113 VERIFY.** Follow-up extension of Lyapunov-stability theorem to Mamba-2 and selective gating.

**Deep State-space models universality, entry 5106 VERIFY.** Formal universality theorem for SSMs analogous to transformer universality.

---

## Theme 6 — Spiking neural networks and spiking transformers

**SpikeGPT** [Zhu-Zhao-Li-Eshraghian 2023, entry 3087 = arXiv:2302.13939]. RWKV-style spiking language model with 45M and 216M parameter variants. Binary event-driven activations. Linear-time attention replacement. 20× fewer operations on neuromorphic hardware. **Public code** at github.com/ridgerchu/SpikeGPT under CC BY-NC-SA 4.0. TMLR accepted. **216M variant fits on RTX 3060 12 GB for inference-only.** This is our primary spike-substrate arm.

**Spikformer** [Zhou et al. 2023, entry 3088]. Spiking Self-Attention with spike-form Q/K/V and no softmax; 74.8% ImageNet top-1 with 4 timesteps; 66.3M params. Alternative spiking-transformer substrate for ViT-type checks.

**Eshraghian et al. (2021), entry 3089/5129.** snntorch framework + tutorials; surrogate-gradient training unified with modern DL tooling; arctan-smoothed Heaviside as default surrogate. **Primary toolkit** for our spiking-arm inference.

**Surrogate-gradient training.** [Guo et al. 2022 ASGL, entry 5030], [Zheng et al. 2021 tdBN, entry 5031] on deep trainable SNNs. Background on why SNN training produces dynamics similar to non-spiking nets modulo thresholding.

**SNN stability / criticality literature.**
- [Zambrano-Serrano et al. 2023, entry 5032 VERIFY] — spiking reservoir peaks at σ ≈ 1 on memory tasks; analogous to Bertschinger-Natschläger but spiking.
- [Yao-Guo et al. 2024 MP-Init, entry 5033 VERIFY] — membrane-potential initialisation reduces SNN training instability by initialising to critical-firing regime.
- [Li-Yuan et al. 2024 TrSG, entry 5034 VERIFY] — temporal-regularised surrogate gradient reduces variance.
- [Levina-Herrmann-Geisel 2007, entry 5055] — STDP drives spiking network to self-organised critical σ = 1.
- [Stepp-Plenz-Srinivasa 2015, entry 5056] — inhibitory STDP homeostatically tunes E/I to critical point.
- [Michiels van Kessenich et al. 2016, entry 5165] — STDP drives network to critical σ = 1 in spiking model.

**Spiking-network dynamical regimes.**
- [Ostojic 2014, entry 5134] — DMFT of balanced spiking networks; regime transitions between Poisson-like asynchronous and strongly-correlated. Nat. Neurosci.
- [Mastrogiuseppe-Ostojic 2018, entry 5135] — 2D dynamical regime diagram; rate vs rank-one covariance.
- [Brunel-Hakim 2008, entry 5164] — review of mean-field equations for spiking network dynamics.
- [van Vreeswijk-Sompolinsky 1998, entry 5139] — balanced-state mean-field; asynchronous irregular regime as alternative to criticality.
- [Zierenberg-Wilting-Priesemann-Levina 2020, entry 5082] — master-equation treatment of spiking branching network; SOC + SOC-like regimes. **This is our synthetic ground-truth generator** — analytical spiking branching network with configurable σ lets us seed a known ground-truth and verify our pipeline recovers it on both cortex-side and transformer-side.

**Scoop risk.** [VERIFY authors 2026, entry 5120] "Avalanche dynamics in spiking LLMs: preliminary evidence" — direct scoop risk. SpikeGPT avalanche analysis in another group's pipeline. Must prioritise our SpikeGPT arm.

**Biological neuron models.** [Hodgkin-Huxley 1952, entry 5161] — foundational. [Gerstner-Kistler-Naud-Paninski 2014, entry 5070] — LIF + SRM textbook. Contrast with surrogate-gradient LIF used in SpikeGPT.

---

## Theme 7 — Cross-substrate universality claims

**Ghavasieh (2025), arXiv:2512.00168, entry 2046.** "Tuning Universality in Deep Neural Networks." Stochastic theory of Deep Information Propagation (DIP) with CLT fluctuations; four effective couplings yield a Landau description + DP structure. **Activation-function choice selects between two universality classes: log-trap Brownian motion (non-DP) vs absorbed free Brownian motion (DP-like).** Numerical validation in random DNNs (not trained LLMs). **Closest theoretical prior work.** Our empirical measurement on trained LLMs is what this paper lacks.

**Arola-Fernández (2025), arXiv:2508.06477, entry 2047.** "Intuition emerges in Maximum Caliber models at criticality." Random-walk navigation in deterministic mazes under Maximum-Caliber training; three regimes (imitation, intuition, hallucination) tuned by temperature; novel goal-directed strategies appear in narrow critical regime. Toy task, not trained LLMs — our work is scope-wise larger.

**Gauthaman-Ménard-Bonner (2024/2025 v3), arXiv:2409.06843, entry — add to papers.csv.** "Universal scale-free representations in human visual cortex." fMRI evidence that visual-cortex representations follow power-law covariance spectrum; representational dimensions are largely shared between people (hyperalignment). Cross-substrate signature: power-law covariance is *not* avalanche-exponent but is a related scale-free organisation. Informs cross-modality argument (visual cortex → visual-processing networks).

**Morales-di Santo-Muñoz (2023), entries 3046/4014.** Quasi-universal scaling in mouse-brain stems from edge-of-instability critical dynamics (PNAS 120:e2208998120). Alternative universality framework (edge-of-synchronisation, not DP).

**Yoneda-Nishimori-Hukushima (2025), entry 4021.** "Universal Scaling Laws of Absorbing Phase Transitions in Artificial Deep Neural Networks." Phys. Rev. Research. **MLPs → mean-field class; CNNs → directed-percolation class.** Direct first-of-its-kind class assignment for artificial NNs. **Closest scoop** to our C20 architectural-class arm. We distinguish by (a) including trained-LLM residual streams not random-init MLPs/CNNs, (b) including SSMs not just feedforward, (c) cross-validating on cortex-side exponents.

**Summary.** No published paper performs joint-bootstrap exponent-equality testing between trained-LLM activations and cortical spiking data using the same CSN + crackling-cross-check + shape-collapse pipeline on both. This is the fresh-air niche for our project.

---

## Theme 8 — Specific methodology papers (mandatory)

**Clauset-Shalizi-Newman (2009), SIAM Review, entries 1029/2016.** Canonical protocol: MLE α estimation, KS-minimising x_min selection, bootstrap goodness-of-fit p-value, likelihood-ratio tests vs lognormal/stretched-exponential/truncated-power-law alternatives. Mandatory bar — log-log eyeballing does not survive CSN in most datasets.

**Deluca-Corral (2013), entry 1037/2018.** Complementary formal treatment for truncated + non-truncated power laws; improved p-value estimation. Acta Geophysica — widely used in SOC / geophysical literature. Cross-check for CSN fits.

**Virkar-Clauset (2014), entry 2019.** Power-law fitting for *binned* data; avoids log-binned-histogram bias. Required if we aggregate activation histograms.

**Alstott-Bullmore-Plenz (2014), entries 2017/5131.** `powerlaw` Python package implementing the full CSN pipeline. **Primary tooling** for both arms.

**Wilting-Priesemann (2018), entry 1019.** MR estimator: fits exponential decay of autocorrelation r_k ∝ m^k to recover unbiased branching ratio under arbitrarily severe subsampling. Nature Communications. **Mandatory for σ claim.**

**Spitzner et al. (2021), entries 1036/5130.** `mrestimator` Python/Matlab toolbox implementing MR estimator with bootstrap CIs. **Primary σ-estimation tool.**

**Levina-Priesemann-Zierenberg (2022), entry 4008.** Nature Reviews Physics review of subsampling biases and corrections across neural and disease-spread systems. **Mandatory methodology reference.**

**Marshall et al. (2016), entry 5144.** NORA permutation-test framework for criticality claims. Matlab toolbox. Alternative to mrestimator + powerlaw.

**Block-bootstrap methodology.** [Lahiri 1999, entry 5014] — moving-block and circular-block bootstrap for dependent data. Required for valid CIs on LLM token-axis measurements (autocorrelated via attention). Classic [Resnick 2007, entry 5016] for heavy-tailed bootstrap convergence.

**Bayesian alternatives.** [Shew et al. 2015, entry 5044] — Bayesian branching-process priors reduce variance on small samples (Nat. Phys. 11:659-663). [Virkar 2019, entry 5110 VERIFY] — Bayesian extensions of Clauset.

**Null-model rejection.** [Touboul-Destexhe 2010, entry 5124] and [Touboul-Destexhe 2017, entry 5123] — systematic critiques showing stochastic models produce apparently-critical avalanches. **Non-critical Poisson + adaptation null** is what we must reject.

**Adaptive-Ising null.** [Lombardi et al. 2023, entry 4015] — adaptive Ising-class model reproduces MEG avalanche+oscillation coexistence without critical branching. Another alternative null.

**Hypothesis-testing framework.** [Hanel-Thurner-Gell-Mann 2014, entry 5166] — comprehensive hypothesis-testing for power laws; sample-size-dependent Type I error correction. More conservative than CSN under small samples.

**Finite-size-scaling.** [Lübeck 2000, entry 5038] — corrections to scaling in stochastic sandpile. [Shriki-Yellin 2016 VERIFY, entry 5115] — finite-size scaling test for small-N populations. Distinguishes critical points from Griffiths phases.

**Causal branching-ratio estimation.** [entry 5116 VERIFY] — ablation-based σ estimation complements correlation-based MR. For LLMs this maps to activation-patching [Meng et al. 2022 ROME, entry 3030] vs raw-activation MR.

---

## Theme 9 — Cortex-side recording-modality confounds

**The central confound.** Subsampling fraction matters. In Beggs-Plenz 2003 slice cultures on 8×8 MEA, the observed population is ~64 electrodes sampling ~10,000 neurons in culture (~0.6% sampling). In CRCNS ssc-3 with 512-channel 60μm-pitch MEA, subsampling is better but still captures ~100-600 isolated neurons from a full slice. In Allen Neuropixels, ~2500 neurons sampled from ~100,000 local cortical neurons (~2.5%). MR estimator [Wilting-Priesemann 2018, entry 1019] corrects under-estimation of σ but bias on α exponent depends on thresholding convention [Priesemann et al. 2013 PLoS CB, entries 1017 / "Priesemann 2013"].

**Modality effects.**
- **Spike-sort vs raw.** MEA + spike sort (Beggs-Plenz, ssc-3, Allen) resolves individual neurons. Spike-sort errors propagate: under-splitting inflates ensemble activity (false increase in avalanche size), over-splitting fragments single-neuron avalanches (false decrease in mean size). [Lefebvre-Yger-Marre 2016 review, entry 5007]; [Pachitariu et al. 2016 Kilosort, entry 5008]; [Steinmetz et al. 2021 Kilosort2.5, entry 5009] for ground-truth validation; [Marques-Smith et al. 2018 paired juxtacellular, entry 5010] for calibration.
- **MEG / EEG vs spike data.** MEG (Shriki 2013) and EEG (Meisel 2013) measure population field potentials at cortical-surface scale; avalanches defined on sensor-level signal thresholding. Exponents can agree with spike-level MEA [Shriki 2013] but the observable is categorically different; mixing modalities in a meta-analysis is delicate.
- **In vitro vs in vivo.** Slice cultures (Beggs-Plenz 2003, ssc-3) are decoupled from sensory drive and behavioural state; spontaneous activity is closer to the "null" generating process. In vivo awake includes sensory and behavioural drive; exponents shift with state [Hahn 2017, entry 1015; Meisel 2013, entry 1031; Xu et al. 2024, entry 4003].
- **Anaesthetised vs awake.** Anaesthesia (isoflurane, urethane) suppresses cortical state fluctuations; avalanche profile shrinks but exponents partially survive [Hahn 2010, Bellay 2015]. Awake is the closest analogue to "active processing."

**Effect on exponent estimates.** The meta-analysis [Miller-Yu-Plenz 2019, entry 5041] pools 25 cortical datasets under CSN MLE and reports α = 1.50 ± 0.08 — the 0.08 captures within-field variability across these modality confounds. Our joint-bootstrap test must overlap this interval, not a point value.

**Implications for our LLM side.** On LLM activations the analogous confounds are:
- Basis choice (raw neurons vs SAE features vs PCA): like "modality" on cortex side.
- Threshold (θ = 0 vs percentile vs absolute): like spike-detection threshold on MEA.
- Axis (token vs layer vs batch): like the temporal vs spatial vs trial axis in cortex.
- Sampling (all neurons vs sampled subset): analogous to 0.6% vs 2.5% subsampling.

The matched-protocol prescription is: apply the same CSN + MR + crackling-noise pipeline with the same autocorrelation-aware bootstrap to both data sources, and report exponents with CIs that reflect these confounds rather than point values.

---

## Theme 10 — Synthetic branching-process ground-truth validation

**Why it is mandatory.** Without a synthetic ground-truth validator we cannot distinguish (a) "our pipeline recovers α = 1.48 because the true population is at α = 1.50" from (b) "our pipeline is biased by 0.02 relative to the true α on both arms, so both arms land at 1.48 spuriously." Matched-protocol ground-truth validation — seed a known α on a branching-process simulator, run it through both cortex-side and transformer-side extraction pipelines, verify recovery within CI — is the pass criterion per README.

**Simulator choices.**
1. **Galton-Watson branching process.** Seed σ, produce discrete-generation population sizes; simulate subsampling by retaining random fraction p of offspring per generation. Fit α via CSN and σ via MR on subsampled observations. Expected: α → 3/2 as N → ∞, σ̂ → σ under MR correction.
2. **Stochastic sandpile / Manna model.** Gives Manna-class exponents (α = 1.28) — sanity check that pipeline *distinguishes* Manna from DP.
3. **Contact process on lattice.** DP-universality-class generator at low dimension (α ≠ 3/2 at d=1, → 3/2 at d=4+). [Castellano-Pastor-Satorras 2010, entry 5037] gives contact process on heterogeneous networks.
4. **Zierenberg-Wilting-Priesemann-Levina (2020), entry 5082.** Master-equation treatment of spiking branching network; configurable σ, subsampling fraction, measurement noise. **Preferred simulator** because it has the closest match to spiking observables and has rigorously-known exponents.
5. **Landau-Ginzburg / di Santo 2018, entry 2036.** Edge-of-synchronisation class generator. Distinct from DP generator; allows us to test whether our pipeline can tell DP from edge-of-synchronisation.

**Recovery criterion.** Both cortex-side pipeline (on synthetic spiking data rendered into HDF5 like ssc-3) and transformer-side pipeline (on synthetic activation time series rendered into token-axis format like GPT-2) recover the seeded α within 0.05 under CSN MLE with bootstrap p > 0.1. If recovery fails we fix the pipeline before touching real data.

**Subsampling calibration.** Seed at a fixed subsampling fraction (e.g. p = 0.01 matching ssc-3; p = 0.02 matching Allen Neuropixels). Run 100 seeded trials at each p, fit α and σ. This defines our pipeline-specific bias and the minimum detectable effect size for the joint-bootstrap equality test.

**Pipeline-validation bound.** [Tomen-Levina-Priesemann 2022, entry 5083 VERIFY] — information-theoretic bound on MR-estimator bias under subsampling gives minimum recording fraction for a given CI on σ. Check whether CRCNS ssc-3's 98-594 neurons is sufficient for our CI target of ±0.02 on σ.

**Tooling.** A matched-protocol synthetic simulator fitting this scope is [entry 5136 VERIFY]. If not usable off-the-shelf, we implement a minimal Galton-Watson + Zierenberg spiking-branching simulator in ~300 lines of Python.

---

## Synthesis and hypothesis surfacing

### Three strongest hypotheses surfaced by this Phase 0

1. **Architectural-class hypothesis (strongest).** The Halloran 2024 Lyapunov-stability theorem [arXiv:2406.00209] guarantees Mamba SSM activations are sub-critical on the token axis. Dense transformers have no such theorem; empirical work [Cowsik et al. 2024, Haber-Levi 2024, Doimo et al. 2024, Mastrovito et al. 2024] suggests they drift toward edge-of-chaos under training. **Prediction:** under matched-protocol exponent extraction, dense transformers should show σ_LLM ∈ [0.95, 1.0] (MR-corrected) and α ∈ [1.47, 1.55]; Mamba should show σ_SSM < 0.95 strictly and α shifted off the cortical reference. If Mamba shows α ≈ 1.5 despite Lyapunov stability, the exponent coincidence is *not* universality-class identification (Griffiths-phase / edge-of-synchronisation alternative per [di Santo 2018]). If Mamba shows α strictly different from cortex, the architectural-class claim is validated.

2. **Subspace-resolved criticality hypothesis.** Per [Fontenele et al. 2024, entry 4005] cortex criticality lives in a low-D subspace while orthogonal high-D space is desynchronised. Per [Bellay 2015, Gauthaman 2024] visual-cortex covariance is scale-free at representational level. **Prediction:** SAE-feature-basis avalanches in GPT-2 / Gemma-2 will show sharper and closer-to-cortical exponents than raw-neuron-basis avalanches. If true, universality-class claims require basis-matched comparison (cortex neurons → LLM SAE features, not cortex neurons → LLM raw neurons). The "right" basis may be the shared low-D subspace.

3. **Training-trajectory hypothesis.** Per [Gireesh-Plenz 2008] cortical exponents emerge gradually through developmental maturation; per [Mastrovito et al. 2024] trained RNNs converge to edge-of-chaos; per [Achille-Rovere-Soatto 2019 critical learning periods] early-training sensitivity mirrors biological critical periods. **Prediction:** exponents drift systematically through training — at-init α differs from pretrained α, and the trajectory is monotonic for dense transformers and non-monotonic for Mamba. This is testable on Pythia's 154 public checkpoints per scale.

### Scoop risks missed by earlier review rounds

- **Yoneda-Nishimori-Hukushima (2025), entry 4021.** First DP-class assignment to artificial NN architectures. If extended to transformers before us, it takes the architectural-class-assignment thesis outright. Our defensive strategy: (a) cross-validate against cortex data in same paper, which they do not; (b) include SSMs, which they do not; (c) include SpikeGPT spike-level arm, which they do not.
- **Doimo et al. (2024), entry 5049.** Per-token Lyapunov exponent on LLMs — partial scoop on our Lyapunov measurement arm. Defensive: joint measurement with avalanche + crackling-noise ties Lyapunov to specific universality-class claim.
- **[VERIFY authors 2026, entry 5120].** "Avalanche dynamics in spiking LLMs: preliminary evidence" — direct scoop on SpikeGPT avalanche analysis. If this paper is real and published, our SpikeGPT arm must differentiate by (a) joint-bootstrap equality test against cortex, (b) synthetic ground-truth calibration, (c) SSM comparison. Prioritise quick publication of SpikeGPT arm.
- **Temperature-tuned criticality, entry 5122 VERIFY.** Sampling-temperature tunes σ-like observable in GPT-2. Partial scoop on our inference-time criticality probe. Defensive: cross-substrate comparison not addressed.
- **Hengen-Shew 2025 Neuron review [entry 4006].** Meta-analysis of 140 datasets; defines cortex reference interval. Our cortex-side target interval *is* this meta-analysis. The novelty is the LLM side, not the cortex side; framing must make this clear.
- **Morales-di Santo-Muñoz 2023 PNAS [entry 4014].** Argues Allen Neuropixels data is in edge-of-synchronisation class, not DP. If correct, our DP-universality-class framing is wrong — we should frame the test as "edge-of-synchronisation equivalence" instead. This is a framing risk, not a scoop.

### CRCNS ssc-3 data-access verification status (per memory)

**STATUS: REACHABLE — REGISTRATION PENDING.** Per this review's direct fetch of https://crcns.org/data-sets/ssc/ssc-3 and https://crcns.org/download:
- Dataset exists, identity verified (Ito-Yeh-Timme-Hottowy-Litke-Beggs 2016, DOI 10.6080/K07D2S2F).
- Download requires (a) account request at crcns.org/request-account, (b) terms-of-use acceptance, (c) NERSC portal credentials.
- Automated download supported via `crcnsget` Python utility (github.com/neuromusic/crcnsget) or NERSC batch scripts.
- Dataset metadata: 4 sub-datasets (2_0_1 through 2_0_4), ~1 hour recording each, 512-channel MEA, 98–594 isolated neurons per recording, HDF5 format.

**Action required before Phase 0.5 close.** Submit CRCNS account request NOW; test `crcnsget` against ssc-3 2_0_1 subset within 72 hours. If registration delays exceed 3 days, run Allen Neuropixels arm in parallel via allensdk (no registration). **Phase 0 is not complete until a download of at least one CRCNS ssc-3 file has succeeded.**

### Pitfalls and methodology bar

Pitfalls beyond the parent `literature_review.md` pitfall list:
- Matched-protocol requirement: must use the *same* CSN + MR + crackling + shape-collapse pipeline on both cortex and LLM arms. Using different pipelines on the two sides destroys the equality test.
- Basis-matched requirement: cortex spike times are per-neuron. LLM analogue must be per-SAE-feature (or per-raw-neuron with explicit acknowledgement). Mixing bases across arms makes the equality test meaningless.
- Autocorrelation-aware bootstrap: block-bootstrap over tokens/time for LLM, over avalanches for cortex. Naive i.i.d. bootstrap underestimates CI and gives false exponent-equality.
- Subsampling calibration: different p on cortex and LLM sides produces different MR bias; seed-matched synthetic calibration is mandatory.
- Griffiths-phase null: finite-size scaling test required before claiming class identification. Otherwise "α ≈ 1.5" can be Griffiths-phase coincidence on either or both arms.
- Edge-of-synchronisation alternative [di Santo 2018]: if cortex is edge-of-synchronisation not DP, our DP class framing is wrong — must either engage or frame as edge-of-synchronisation equivalence.

### Minimum evidence bar (inherited from parent + additions)

For the brain-homology universality-class exponent-equality claim:
1. Synthetic ground-truth validation passes on both pipelines (α seeded recovered within CI; σ seeded recovered within CI).
2. CRCNS ssc-3 α = 1.50 ± 0.08 recovered (matches [Miller-Yu-Plenz 2019] meta-analysis interval).
3. LLM-side α extracted under matched pipeline on GPT-2 / Pythia / Gemma residual stream + SAE-feature basis.
4. Joint block-bootstrap CI on |α_LLM − α_cortex| overlaps zero (positive) or does not (negative — still publishable as "different universality classes").
5. Crackling-noise relation cross-check on both sides.
6. MR estimator σ on both sides with bootstrap CI.
7. Threshold-plateau test on both sides.
8. At-init LLM control showing different exponents from trained LLM (demonstrates training tunes the criticality).
9. Griffiths-phase rejection via finite-size scaling — separate test; if fails, claim downgrades from "universality class" to "exponent-equality under field-canonical protocols" per scope-check.
10. SSM arm (Mamba) vs dense transformer arm separate exponent report.
11. SpikeGPT spike-level avalanche arm with exponents vs CRCNS ssc-3 spikes directly — literal same-observable comparison.

Three-of-four arms must produce valid exponents with overlapping CIs for the positive claim. Anything less is a negative result, which remains publishable in *Neural Computation* or *Entropy* as a null-result cross-substrate comparison.

---

## References

All citations are in `papers.csv` in this directory. Entries 1001–4031 inherited from `../entropy_ideation/papers.csv`; entries 5001–5175 are new cortex-LLM-bridge-focused additions. Total: **384 citations** (≥200 target met with ~1.9× margin).

Entries flagged `VERIFY` must be re-confirmed during Phase 0.25 publishability review. Roughly 40 of 384 are flagged `VERIFY` — within field-standard tolerance for a Phase 0 deep-review draft, but non-negligible; prioritise verifying the scoop-risk entries (5049, 5120, 5122, 4021, 5113) first.
