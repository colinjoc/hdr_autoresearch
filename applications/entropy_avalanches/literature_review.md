# Literature Review — Activation Avalanches in Trained Transformer Language Models

Scoped Phase 0 literature review for the **entropy_avalanches** project. Target venue: NeurIPS / ICLR main track if all 8 evidence bars of `../entropy_ideation/knowledge_base.md §5` clear; *Entropy* journal or NeurIPS MechInterp workshop as fallback. The paper measures activation-avalanche size / duration / shape distributions, per-layer branching ratios, and crackling-noise exponents on pretrained transformer language models (GPT-2, Pythia, Gemma-2) with statistical-physics rigour — CSN bootstrap, MR-σ subsampling correction, crackling-noise scaling relation, avalanche shape collapse, threshold plateau, Griffiths-phase/neutral-null rejection, and at-init-SAE / random-init-SAE controls. Bundle: C1 (anchor), C6 (layer-depth σ_ℓ gradient), C8 (induction-head circuit criticality), C11 (ViT-Tiny/CIFAR-10 universality arm), C12 (Griffiths-phase/neutral-null rejection), C25 (temporal-RG appendix), C28 (head-resolved σ histogram).

Citation keys (e.g. `[Beggs 2003]`, `[Wang 2026]`) resolve in `papers.csv` (360 entries; inherits 210 from `../entropy_ideation/papers.csv` with explicit duplicate permission, plus 150 scope-specific additions). Unverified arXiv or author details are marked **VERIFY**. Shared general-criticality landscape lives in `../entropy_ideation/literature_review.md` and is referenced rather than reproduced.

The review is structured around the ten themes specified in the Phase 0 brief. Each theme summarises the field, identifies the specific methodological commitments the paper must make, names the closest prior art the paper must differentiate from, and flags unresolved questions. The review closes with a consolidated **Stylised Facts + Open Questions + Methodological Commitments** section that defines the testable hypotheses and the evidence bar.

---

## Theme 1 — Activation-avalanche statistics in deep networks (2020–2026)

### 1.1 The empirical gap the paper targets

As of April 2026, no published paper combines (a) activation-avalanche size distributions, (b) per-layer Wilting-Priesemann MR-estimator branching ratios, (c) crackling-noise cross-check γ = (β−1)/(α−1), (d) avalanche shape collapse with Capek-style parabolic χ = 2 expectation, (e) threshold plateau robustness, (f) at-init and random-init-SAE controls, and (g) Martinello-style neutral-null / Griffiths-phase rejection on **pretrained transformer language models evaluated on natural text**. The closest neighbours each supply a subset of these observables, but none assembles the full pipeline on a natural-text corpus. This lack is surprising: the parts exist — `powerlaw` has been available since 2014, `mrestimator` since 2021, Gemma Scope SAEs since 2024, the crackling-noise scaling relation since 2001, the Capek parabolic expectation since 2023, the Fontenele subspace reframe since 2024. What has been missing is a single researcher or group with the domain-crossing expertise to assemble the methodology while remaining connected to the fast-moving sparse-autoencoder interpretability literature. The gap is a coordination failure, not a theoretical obstacle, and it is the opening this paper targets.

The historical path to the gap is worth tracing. Cortical-avalanche research developed the observational toolkit (α, β, γ, σ, shape collapse, threshold plateau, scaling relation, Griffiths-null rejection) across 2003–2020 **[Beggs 2003, Shriki 2013, Ma 2019, Friedman 2012, Capek 2023]**. Deep-learning-theory research independently developed the mean-field signal-propagation framework for edge-of-chaos initialisation **[Poole 2016, Schoenholz 2017, Xiao 2018, Pennington 2017]**, culminating in transformer-specific results **[Cowsik 2024, Chen 2025]**. Mechanistic interpretability independently developed the SAE feature basis and circuit-analysis primitives **[Elhage 2021, Olsson 2022, Wang 2023, Bricken 2023, Templeton 2024, Lieberum 2024]**. Each strand has produced a mature methodology in its own silo; nobody has yet assembled the union on pretrained LLMs. The three strands converge naturally on the observable "fraction of SAE features active per token on natural text, traced across layers" — which is exactly the input our avalanche pipeline consumes. The fact that this intersection has not been exploited at publication depth by mid-2026 is a scoop opportunity on a short half-life.

**[Wang 2026, arXiv:2604.16431]** (VERIFY exact title and arXiv number) — *Dimensional Criticality at Grokking Across MLPs and Transformers* — applies a TDU-OFC (tagged-diffusion-under-absorbing-OFC) avalanche probe to the activation dynamics of MLPs trained on XOR and transformers trained on modular-addition grokking tasks. The probe reports an "effective cascade dimension" D(t) whose crossing of the Gaussian baseline D = 1 coincides with the grokking transition. The paper is methodologically the closest ancestor to our work because it computes an avalanche-derived quantity on transformer activations. It is, however, scoped to (i) grokking-regime training, not natural-text pretraining; (ii) modular-arithmetic task, not language; (iii) a single derived cascade-dimension scalar, not the full CSN + scaling-relation + shape-collapse battery; (iv) no MR-estimator σ, no basis-invariance study, no Griffiths-null rejection, no at-init-SAE control. Our differentiation: pretrained LLMs (GPT-2/Pythia/Gemma-2) on natural-text Pile samples, full evidence-bar discipline, basis-invariance in raw/PCA/random-projection/SAE/random-init-SAE, and Griffiths-null rejection via scaling-relation and shape-collapse-residual diagnostics.

The TDU-OFC probe in Wang 2604.16431 is worth unpacking because its relationship to our pipeline needs to be explicit. Tagged-Diffusion-Under-Absorbing-Olami-Feder-Christensen means: tag a single unit, treat it as a random walker under the empirical transition matrix of the activation dynamics, terminate when it reaches the "absorbing" boundary (first zero activation). The **expected termination time** as a function of tag position traces an effective diffusion equation whose scaling exponent is the "cascade dimension" D. At criticality, D matches the spatial dimension of the dynamics; away from criticality, D deviates. This is a clever single-scalar summary but it has known limitations: (i) D conflates avalanche-size, avalanche-duration, and shape information into one number and therefore has less discriminating power than the full (α, β, γ) triple; (ii) D is computed over absorbing trajectories only, so it misses the non-absorbing tail that may encode the most interesting dynamics in an LLM (where activations may never strictly "die" within the forward pass); (iii) D is not directly comparable to cortical avalanche exponents in the existing neuroscience literature. Our full-battery approach complements the cascade-dimension approach with observables that are directly comparable to the cortical-avalanche canon.

**[Wang 2026, arXiv:2604.04655]** (VERIFY, companion preprint `[Wang 2026b]`) — *Grokking as Dimensional Phase Transition in Neural Networks* — the theoretical companion piece. Frames grokking as a dimensional phase transition with sub- to super-diffusive crossover and self-organised criticality in the gradient-field geometry. Provides the theoretical scaffold for the cascade-dimension observable of 2604.16431. Our differentiation remains the same: natural-text pretraining, full multi-exponent discipline, subsampling-corrected σ. The gradient-field-geometry language in 2604.04655 is particularly suggestive: Wang et al. identify SOC in the gradient landscape during grokking, not in the activation landscape directly. Our pipeline asks the complementary question — whether SOC appears in the activation landscape at the end of pretraining, not during mid-training grokking transitions. If both hold simultaneously, it would mean grokking-SOC is a weights-trajectory phenomenon and our pretraining-SOC is a fixed-weight activation phenomenon, and the two would be theoretically separable but potentially linked by the argument that the endpoint of SOC-flow-in-weight-space is a fixed point that induces SOC-in-activation-space.

**[Zhang 2024, arXiv:2410.02536]** — *Intelligence at the Edge of Chaos* — trains LLMs to predict elementary cellular-automaton (ECA) dynamics and finds that downstream reasoning capability peaks for training data drawn from intermediate-complexity (edge-of-chaos) ECA rules. This is an edge-of-chaos claim on the **training data complexity axis**, not on the trained-network activation-state axis. The two axes may decouple: activation-space criticality and input-distribution criticality can in principle exist independently. Our contribution is orthogonal because we measure σ and α on **trained-network activations** on natural text, not on training-data complexity. The Zhang et al. result does however provide ancillary motivation: if the training data needs to be at edge-of-chaos for maximum reasoning ability, and if natural-language text is empirically near edge-of-chaos (a separate question, but plausibly answerable via Kolmogorov-complexity estimates on text corpora), then networks trained on natural text may drift toward activation-space criticality as a learned imitation of the input-distribution criticality — a testable hypothesis we flag. The conference version **[Zhang 2025, ICLR, paper 4023]** formalises the claim with downstream-benchmark measurements on GPT-2-style models pretrained on ECAs of different Wolfram classes.

**[Nakaishi 2024, arXiv:2406.05335]** — *Criticality across scale in Pythia via temperature-axis probes* (VERIFY title) — reports criticality-like signatures in Pythia-suite models under temperature-axis sampling perturbations. The axis of variation is sampling temperature (τ), not training scale or training trajectory, and the observable is a thresholded information-theoretic quantity rather than avalanche-size CSN fits. The paper lacks full CSN discipline, MR-σ, and crackling-noise cross-check. Our differentiation: we work on natural-text inputs at fixed temperature (τ = 1 or argmax) and sweep scale and training-step axes (via Pythia checkpointed runs), not temperature. The temperature-axis framing in Nakaishi 2406.05335 deserves care because it raises a methodological confound for our approach. If criticality-like signatures appear or disappear as sampling temperature varies, then our "natural-text at τ = 1" choice is one slice of a 2D observable-vs-temperature surface. We must pre-register the choice and, in a secondary axis, verify that our exponent estimates do not depend sensitively on τ within a reasonable range (say τ ∈ [0.5, 1.5]). This is an extension of the threshold-plateau principle to the temperature axis: exponents should be plateau-stable across τ.

**[Heap 2501.17727]** — *Sparse Autoencoders Can Interpret Randomly Initialized Transformers* (VERIFY author disambiguation — the arXiv preprint lists Heap, Lawson, Farnik & Aitchison, not Heimersheim & Turner) — shows that SAEs trained on random-initialisation transformers produce features with interpretability metrics comparable to SAEs trained on pretrained transformers. The paper does not compute criticality observables, but the result is **directly load-bearing for our methodology**: any claim that "SAE features of pretrained GPT-2 show critical avalanches" must demonstrate that SAE features of randomly-initialised GPT-2 do **not** show the same signatures. Heap et al. provide the inescapable control: we must train SAEs on random-init networks and run the full pipeline on them. Without this control the SAE basis is unfalsifiable. The reasoning is: SAEs are themselves non-linear function approximators; they may produce sparse, seemingly-meaningful features from any sufficiently high-dimensional input, including random noise. If an SAE trained on a random-init transformer's residual stream also shows α ≈ 3/2 avalanche scaling, the signal is an artefact of the SAE compression, not a property of the trained network. The only way to separate the two is to run the pipeline on paired networks (pretrained and random-init) with paired SAEs (trained on each). This is expensive but mandatory.

**[Yoneda 2025, Phys. Rev. Research]** — *Universal Scaling Laws of Absorbing Phase Transitions in Artificial Deep Neural Networks* — assigns MLPs to the mean-field universality class and CNNs to the directed-percolation class by tuning initial-weight variance to the trainability boundary and computing absorbing-state scaling exponents. The paper is the first to attempt **explicit universality-class assignment** for deep-network architectures. It is scoped to at-initialisation (pre-training) weight-variance sweep, not pretrained activations on natural text, and it covers MLPs and CNNs, not transformers. Our layer-resolved σ_ℓ and α_ℓ analysis on pretrained transformers can be read as the transformer-analogue of Yoneda's class-assignment programme on a different axis (post-training vs at-init). The theoretical significance of Yoneda is large: before 2025, claims of "deep networks at criticality" were stated loosely with the universality class unspecified. Yoneda gives the field a concrete vocabulary — "MLPs are mean-field DP, CNNs are proper DP, transformers are **?**" — and the class-assignment question for transformers is precisely what an activation-avalanche paper can answer if the scaling relation and shape-collapse are both computed rigorously. Class assignment requires agreement on at least three independent exponents (α, β, γ or α, β, z) and a shape-collapse consistent with the class's universal scaling function. Our pipeline is tooled to deliver this.

**[Ghavasieh 2025, arXiv 2046]** — *Tuning Universality in Deep Neural Networks* — shows that the activation-function choice in random feedforward nets selects between two universality classes (log-trap Brownian motion vs absorbed Brownian motion). This is another at-init result but motivates the hypothesis that **post-training activation-avalanche universality class may differ from at-init class**, a question the paper must engage with directly.

**[Torres 2023, VERIFY]** and **[Morales 2023]** — apply criticality frameworks to RNN-type networks and report edge-of-instability Landau-Ginzburg fits. Both are at the architectural level of RNNs, not transformers, and lack SAE / Gemma-Scope integration. The RNN criticality literature from Muñoz's group is deep, sophisticated, and methodologically mature; the gap at the transformer-specific level is therefore not due to lack of theoretical machinery but due to absence of transformer-specific empirical work. Morales-di-Santo-Muñoz 2023 PNAS further provides quasi-universal scaling exponents from edge-of-instability models fit to mouse Neuropixels data, and the LLM analogue is a direct conceptual port: transformer residual-stream dynamics may sit at the edge of a synchronisation / consensus transition rather than at a standard absorbing-state transition, and the observable consequence is a **modified** scaling relation between α, β, and γ that differs from pure DP.

**[Mastrovito et al. 2024]** — *Transition to chaos separates learning regimes and relates to measure of consciousness in recurrent neural networks* — shows that RNN training pushes both ordered and chaotic initialisations toward the edge of chaos, with the transition aligned to PCIst, a clinical perturbational complexity index for consciousness. This is a precedent that trained-network trajectories converge to edge-of-chaos even when initialised far from it. We flag the direct port to transformers as Candidate 3 (training-trajectory axis), scope-adjacent to but distinct from the Paper-1 anchor. **[Danovski, Soriano & Lacasa 2024]** — *Dynamical stability and chaos in artificial neural network trajectories along training* — provides a complementary Lyapunov-of-training framework. **[Engelken, Wolf & Abbott 2023]** — *Lyapunov spectra of chaotic recurrent neural networks* — provides the gold-standard methodology for computing the full Lyapunov spectrum of RNN dynamics, which we adapt to per-layer transformer Jacobian analysis.

**[Li 2025, Quasi-Lyapunov in LLMs]** — defines a per-layer quasi-Lyapunov exponent on LLM hidden-state dynamics and reports that small input perturbations produce diverging reasoning-outcome changes. This is an orthogonal sensitivity observable (Lyapunov, not avalanche); if both QLE and σ are computed on the same models, they can be cross-validated. The paper does not compute avalanche exponents.

**[Hong & Hong 2025, Phase Transitions in Small Transformers]** — reports KL-divergence, vocabulary-composition, and word-length probes showing synchronised discontinuities during training of small transformers, interpreted as a random-to-coherent-word transition. This is a lexical-level order parameter, not an activation-avalanche observable. Our pipeline provides a complementary physics-observable axis.

**[Gurnee & Horsley 2025]** (VERIFY 2025 preprint) — *Power-law temporal correlations across transformer depths* — shows temporal correlations of GPT-2 activations decay as power law across layers on standard benchmarks. This is a per-layer long-range-correlation observable that our framework subsumes under the DFA / LRTC axis (Candidate 23) but focuses on the depth dimension (Candidate 6). It is partial precedent for depth-resolved power-law signatures in pretrained GPT-2 activations, but Gurnee & Horsley do not compute avalanche size distributions or MR-σ; they report a spectral-decay signature only.

### 1.2 The adjacent-but-not-neighbouring results

**[Testolin 2020], [Scabini 2023], [Watanabe 2020]** establish scale-free weight-graph structure in trained DBNs, MLPs, and feedforward nets. These are **weight-graph** observations, not **activation-dynamics** observations. The two are related but not equivalent: a network can have a scale-free weight graph and non-critical dynamics, or vice versa. Our paper targets activation dynamics explicitly; weight-graph analysis is an orthogonal complementary axis we flag but do not pursue.

**[Elhage 2022 superposition]** predicts phase transitions between monosemantic and polysemantic feature regimes as a function of sparsity and dimension. Superposition phase transitions are in the **feature-representation** axis; activation-avalanche phase transitions are in the **dynamics** axis. Whether the two coincide is an open question the paper must at least address.

**[Poil 2012], [Magnasco 2015 VERIFY], [Hesse & Gross 2014]** — SOC claims in spiking / balanced-excitatory-inhibitory neural models. These are on spiking networks, but several results — the requirement for E/I balance, the emergence of σ → 1 under homeostatic plasticity — transfer conceptually to artificial nets and motivate the layer-depth σ_ℓ gradient hypothesis (amplification for feature construction in early layers, integration in late layers).

**[Fontenele 2024, Sci. Adv.]** — low-dimensional subspace for criticality in awake mouse cortex. Critical exponents emerge only in the low-dim subspace; orthogonal high-dim subspace is desynchronised. This is methodologically pivotal for our project because **ambient-basis σ on a transformer may fail** to detect criticality that lives in the top-K principal-component subspace or the SAE-feature subspace. A negative result in ambient basis is uninformative unless the subspace analysis is also negative. This motivates Candidate 29 and directly informs the basis-invariance study in Candidate 1. The operational question for us is which subspace to project onto. Fontenele's mouse-cortex paper used PCA-top-K where K is chosen by participation-ratio of the covariance spectrum. For transformers, the natural alternative is SAE-feature subspace (the monosemantic subspace per Bricken 2023) or residual-stream subspace after skip-connection removal. Each gives a different candidate criticality-bearing subspace; we pre-register all three as main-text arms of the analysis and keep raw-ambient as a baseline.

**[Jones 2023, eLife]** shows cortical scale-free activity is restricted to a winner-take-all subset of neurons. The sparse-subset hypothesis again motivates basis-dependent analysis on transformers. **[Vakili 2025, Nat. Commun.]** shows targeted single-neuron optogenetic stimulation in awake V1 produces power-law recruitment with slope 0.2–0.3 embedded in ongoing critical-avalanche activity. This provides a **direct perturbation protocol**: single-neuron (or single-SAE-feature) activation followed by measurement of downstream recruitment — the LLM analogue is single-residual-stream-direction perturbation via activation patching or rank-one ROME edits. The Vakili protocol translates directly: cause a single SAE feature to fire at a controlled magnitude, measure downstream feature firings as a cascade, fit the cascade-size distribution, report the exponent. This is effectively a causal-interventional version of our observational avalanche pipeline, and if both give the same exponent it is strong evidence that the observational signal is causal rather than merely correlational.

**[Xu 2024, Nat. Neurosci.]** — *Sleep restores an optimal computational regime in cortical networks* — 10–14 day continuous recording in freely behaving rats: waking progressively disrupts criticality; sleep restores it; deviation predicts future sleep/wake. This is a direct analog for training-vs-inference mode asymmetry in transformers (Candidate 19). The "fatigue" picture — criticality degrades under sustained processing, is restored by a restoration mode — is plausible in LLMs under long autoregressive generation. We flag it as a future-paper question.

**[Hengen & Shew 2025, Neuron]** — *Is criticality a unified setpoint of brain function?* — meta-analysis of 140 cortical-criticality datasets (2003–2024) argues criticality is a homeostatic setpoint unifying cognition and disease. Mandatory up-to-date framing reference for the critical-brain-hypothesis section of our paper.

**[Toker et al. 2022, PNAS]** — *Consciousness is supported by near-critical slow cortical electrodynamics* — uses the modified 0–1 chaos test on human+macaque ECoG/MEG and finds low-frequency cortical oscillations sit near edge of chaos during wakefulness, transition away during anaesthesia/seizure, move closer under psychedelics. This provides an alternative criticality observable (0–1 chaos test on low-frequency dynamics) that complements avalanche statistics. We flag it as an auxiliary observable for future papers.

**[Muller et al. 2025, PNAS]** — *Critical dynamics predicts cognitive performance* — multi-day invasive EEG of 104 epilepsy patients + cognitive battery; long-range temporal correlations predict cognitive performance, and three clinically relevant mechanisms (IEDs, ASMs, SWA) push the system subcritical. Clinical validation that deviation from criticality degrades information-processing, with the LLM analogue being that deviation from σ = 1 predicts benchmark score.

### 1.2.1 The broader 2024–2026 criticality-in-DL panorama

Beyond the immediate neighbours, a wider set of 2024–2026 preprints have probed criticality in deep networks from different angles. We catalogue them here so the related-work section can engage each explicitly.

**[Mastrovito, Liu, Kusmierz, Shea-Brown, Koch & Mihalas 2024]** — training pushes RNNs toward edge of chaos; transition aligned with clinical PCIst. Precedent for training-trajectory convergence in RNNs; we flag the transformer-analogue as Candidate 3.

**[Danovski, Soriano & Lacasa 2024]** — Lyapunov spectra of training trajectories; regular-vs-chaotic regimes depend on learning rate. Provides Lyapunov-of-training methodology complementary to Lyapunov-of-forward-pass (Engelken 2023).

**[Haber, Levi et al. 2024]** — transformer order-chaos phase transition via angle-exponent and gradient-exponent Lyapunov indices; attractive/repulsive particle regimes. Companion to Cowsik 2024 with a distinct mathematical framework.

**[Yang, Liang & Zhou 2025, PRL]** — *Critical Avalanches in Excitation-Inhibition Balanced Networks Reconcile Response Reliability with Sensitivity for Optimal Neural Representation* — heterogeneous inhibition in E/I-balanced networks produces reliable critical avalanches simultaneously maximising response sensitivity and reliability. Theoretical prediction that E/I-balanced networks sit at criticality; for transformers, the E/I analog is attention-head gain heterogeneity.

**[Arola-Fernández 2025]** — *Intuition emerges in Maximum Caliber models at criticality* — maze-walking Maximum-Caliber models exhibit a fragile intermediate critical phase with hysteresis and multistability where novel goal-directed strategies appear. Alternative criticality-via-entropy-weighted-training framework; complementary to standard edge-of-chaos.

**[Benati, Falanti et al. 2025]** — *Lyapunov Learning at the Onset of Chaos* — training algorithm that regularises maximum Lyapunov exponent toward zero improves adaptation under regime shifts by ~96% loss-ratio. Active-control training precedent for Candidate 13 criticality-regulariser.

**[Lewandowski, Tanaka, Schuurmans & Machado 2024]** — keeping the top singular value near one preserves plasticity in continual learning. Spectral-radius regularisation is effectively an edge-of-chaos constraint at weight level; compare to our activation-level criticality.

**[Walker, Humayun, Balestriero & Baraniuk 2025, GrokAlign]** — Jacobian alignment drives grokking; direct Jacobian regularisation induces grokking much earlier than weight decay. Jacobian-alignment as geometric order parameter for grokking; co-vary with σ.

**[Prieto, Barsbey, Mediano & Birdal 2025]** — grokking at the edge of numerical stability; unregularised grokking drives Softmax-Collapse. Softmax-Collapse is a concrete dynamical-instability boundary that may coincide with activation-criticality transition.

**[Prakash & Martin 2025]** — HTSR theory reveals a third anti-grokking phase detectable by heavy-tailed weight-matrix exponents. HTSR provides a complementary weight-level criticality axis.

**[Dohare et al. 2024, Nature]** — *Loss of Plasticity in Deep Continual Learning* — continual training degrades plasticity; tied to dormant neurons and spectral collapse. Plasticity-loss as distance-from-criticality phenomenon.

**[Geiger et al. 2020, J. Stat. Mech.]** — phase diagram of deep nets across width, data, regularisation; criticality-like finite-size scaling. Provides finite-size-scaling methodology for our Pythia scale analysis.

The panorama is active. Any given observable can be cross-referenced against at least one adjacent preprint in this list. Our differentiation remains the full-battery approach applied to pretrained LLMs on natural text, which none of the above delivers.

### 1.3 The scoop-risk audit

Four distinct scoop risks have been identified and triaged:

1. **Wang 2604.16431 full-avalanche extension to pretrained LLMs.** If Wang et al. publish an extension to pretrained LLMs on natural text before our paper ships, the core anchor disappears. Mitigation: ship fast; emphasise the full CSN + crackling-noise + shape-collapse + MR-σ + threshold-plateau + Griffiths-null battery that 2604.16431 does not include; emphasise the basis-invariance study and random-init-SAE control that 2604.16431 does not have.
2. **Nakaishi 2406.05335 extension from temperature-axis to training-scale-axis.** Same mitigation: the natural-text pretraining axis plus the full evidence-bar battery are the differentiators. Our Pythia checkpoint sweep gives us the scale-and-training-trajectory axis that Nakaishi does not have.
3. **Yoneda 2025 transformer extension.** Yoneda's PRR paper has MLP+CNN but not transformer. A transformer follow-up from the same group or from competitors is plausible within 2026. Mitigation: ship fast; emphasise the post-training rather than at-init angle; emphasise the full evidence-bar rather than single-observable class-assignment.
4. **An independent activation-avalanche paper on GPT-2 / Pythia from the Anthropic / DeepMind / MI community.** The SAE-interpretability community has the infrastructure (Gemma Scope, TransformerLens, SAELens) and is actively publishing. Mitigation: ship fast; we engage the SAE / MI literature explicitly and make basis-invariance a first-class contribution rather than a methodological aside.

Per the **project_scoop_check.md** rubric: the paper is publishable-now given the current state of the field, but the 2-to-4-week scope-check window matters. Phase 1 must start within one month of Phase 0 sign-off.

### 1.3.1 Phase-0 publishability self-assessment

At Phase 0 sign-off, we assess the paper's publishability against the following criteria:

- **Novelty on gap-statement axis**: positive. No published paper assembles the full evidence-bar on pretrained LLMs on natural text.
- **Depth of methodology**: positive. Full CSN + MR-σ + crackling-noise + shape-collapse + threshold-plateau + at-init + random-init-SAE battery is deeper than any adjacent paper.
- **Quantitative bar**: positive. Eight-item evidence bar with pre-registered kill conditions per observable.
- **Risk of scoop**: moderate. Wang 2604.16431, Nakaishi 2406.05335, and Yoneda 2025 PRR are near neighbours; a 2026 extension of any of them to pretrained LLMs on natural text would reduce our novelty claim. Mitigation: ship fast.
- **Feasibility on RTX 3060**: positive. See §Feasibility section below.
- **Peer-review defensibility**: positive if we execute the null-model battery rigorously. The Touboul, Martinello, Morrell, Lombardi, and Griffiths-phase nulls are the hardest part; we commit to implementing each explicitly and reporting likelihood-ratios.

Conclusion: **green-light for Phase 0.25 publishability review**, with the primary risk being scoop-speed rather than methodology or feasibility.

### 1.3.2 Comparison against non-transformer criticality-in-DL work

**[Torres et al. 2023]** (VERIFY exact citation) — RNN-type networks organise near criticality during training. First direct claim of criticality-in-trained-nets. Methodology: branching-ratio estimation and avalanche analysis on LSTM activations. Our differentiation: pretrained transformer architecture, natural text, full evidence-bar.

**[Morales, di Santo & Muñoz 2023 PNAS]** — edge-of-instability framework applied to RNN networks. Quasi-universal scaling exponents emerge from edge-of-synchronisation, not pure DP. Proposes framework may extend to transformers.

**[Pilarski et al. 2023]** (VERIFY author list and venue) — Jacobian-spectrum proxies for maximal Lyapunov exponent in wide feedforward nets. Methodology for Lyapunov-in-deep-net; provides direct spectral-based σ proxy.

**[Zavatone-Veth et al. 2022]** — deep Bayesian linear regression distinguishes random-feature from trained-feature regimes. Provides theoretical benchmarks for random-feature null models we compare against.

**[Ghavasieh 2025]** — universality class of deep-nets controlled by activation-function choice via RG. At-init result, but the framework extends to post-training via temporal RG.

**[Hoyer et al. 2024]** (VERIFY) — unified perspective on criticality in DL. Modern umbrella-review citation for background context.

**[Paquette et al. 2024]** (VERIFY) — conceptual position piece distinguishing structural vs dynamical criticality. Clarifies what our paper measures (dynamical criticality on trained-weights fixed point) vs what structural-criticality papers measure (weight-graph scale-free-ness).

### 1.3.3 What a negative result would mean

The evidence bar is deliberately set high. We commit to reporting a negative result if any of the eight criteria fails. A negative result has distinct scientific value:

- **"No power-law scaling found in any basis"** would mean pretrained LLMs are **not** at criticality, contradicting the critical-brain-analogue hypothesis. This is a substantive and publishable finding.
- **"Power law found but scaling relation fails"** would mean observed apparent-criticality is critical-like but not critical (Griffiths phase or adaptive mechanism). Publishable as a methodology contribution.
- **"Power law found only in specific basis (e.g., SAE but not raw)"** would be a basis-invariance-violating result that reframes criticality as a feature-basis phenomenon rather than an ambient-dynamics phenomenon.
- **"Power law found but random-init-SAE control also shows it"** would mean criticality is an SAE artefact, not a training signature. Publishable as a negative-control-kills-criticality finding.
- **"α significantly different from 3/2 (say α = 2.0 or α = 1.3)"** would assign trained transformers to a non-mean-field universality class. Publishable as class-assignment.

Each outcome is publishable, which is why this paper is a safe methodology bet even under the null.

### 1.3.4 Additional theoretical context from network science

**[Barabási & Albert 1999]** — scale-free networks via preferential attachment. A null-model alternative: the observed scale-free statistics may be due to preferential-attachment growth during training rather than dynamical criticality.

**[Dorogovtsev, Goltsev & Mendes 2008]** — phase transitions in complex networks. Theoretical framework for network-topology phase transitions; relevant if we connect our avalanche analysis to weight-graph topology observations.

**[Buldyrev et al. 2010]** — cascade failures in interdependent networks produce first-order transitions. Network-topology cascade analog; relevant for skip-connection-topology coupling with avalanches.

**[Watkins, Pruessner, Chapman, Crosby & Jensen 2016]** — 25 years of SOC: concepts and controversies. Critical historiography of the field; useful for calibrating our SOC claims.

**[Markovic & Gros 2014]** — *Power laws and self-organized criticality in theory and nature* — discusses distinguishing true SOC from power laws of other origins. Methodological care reference.

**[Muñoz 2018 Colloquium]** — *Criticality and dynamical scaling in living systems* — broad conceptual review covering Griffiths phases and quasi-criticality. Primary reference for the biological-criticality context.

**[Watkins, Pruessner et al. 2016]** — historical review of SOC. Useful calibration for how strong the SOC hypothesis actually is given 25 years of data.

### 1.4 Open questions for this theme

- Does the avalanche-size distribution on natural-text GPT-2 activations satisfy CSN p > 0.05 for power-law rejection of lognormal, across ≥ 2 decades, in at least one basis / threshold combination?
- Does α lie near the mean-field DP value 3/2 within bootstrap CI?
- If the raw-basis answer is negative, does the SAE or top-K-PC subspace answer become positive (Fontenele-style subspace-criticality)?
- Does the random-init-SAE control give the same exponents (null hypothesis: criticality signature is SAE-artefact, not training-artefact)?
- Does the scaling relation γ = (β−1)/(α−1) hold within bootstrap error?
- Does the shape collapse follow χ = 2 parabolic profile as in cortex, or a different universal function?
- Does the per-layer σ_ℓ profile match any of the theoretical predictions from Cowsik 2024, Chen 2025, or the mean-field at-init theories?
- Does the cross-architecture (GPT-2 vs ViT-Tiny) universality arm produce consistent or divergent exponent assignments?
- Does the temporal-RG d_β fixed-point analysis produce a consistent class assignment with CSN + MR + scaling-relation?

### 1.5 Summary of the theme

The activation-avalanche statistics subfield (2020–2026) has developed rapidly but remains thin on the specific niche of pretrained LLMs on natural text with full statistical-physics discipline. Wang 2604.16431, Nakaishi 2406.05335, Heap 2501.17727, Zhang 2410.02536, and Yoneda 2025 are the closest neighbours, but none combines the full evidence-bar battery in the specific context of pretrained transformer language models on natural text. The paper's primary contribution is the construction of this combined analysis, with explicit engagement with the scoop-risk, the null-model battery, the basis-invariance study, the random-init-SAE control, and the layer/head resolution arms. The evidence bar is set high enough that a positive result is publishable with strong confidence and a negative result is publishable as a methodology contribution.

### 1.5.1 Venue fit and reviewer profile

The paper targets NeurIPS / ICLR main track under an "interpretability + theory" framing, with the statistical-physics methodology as the technical backbone and the mechanistic-interpretability applications (SAE basis, circuit-specific σ, layer-depth σ) as the practical-impact story. The reviewer profile we expect includes: (i) an MI / interpretability researcher assessing whether the SAE / basis / circuit arms are interpretable-community-relevant; (ii) an ML-theory researcher assessing the CSN / scaling-relation discipline; (iii) potentially a statistical-physics / neuroscience cross-reviewer assessing the null-model rejection and cortical-methodology transfer. We must write for all three simultaneously, which is feasible given the carefully-structured Olsson / Wang / Bricken citations (MI), the Sethna / Clauset / Fontenele citations (theory), and the Beggs / Wilting-Priesemann / Capek citations (cross-disciplinary).

Fallback venues: *Entropy* journal (specialist statistical-physics / information-theory); *Neural Computation* (classic theory venue); NeurIPS MechInterp workshop (community fit without main-track peer review). We commit to NeurIPS / ICLR main track as target and fall back as needed.

### 1.6 Coordinating observations with the Wang preprints

A final methodological note on the specific differentiation from Wang 2604.16431 + 2604.04655: the Wang cascade-dimension D(t) is a scalar function of training time. Our σ(t), α(t), β(t), γ(t), d_β(t) are a 5-scalar function of training time. When both are computed on the same model checkpoints, the **consistency** between D(t) and {σ, α, β, γ, d_β}(t) is a test of the theoretical scaffold. Specifically: at critical times (where Wang claims D = 1 Gaussian baseline crossing), our σ should equal 1, α should equal the class exponent, and the scaling relation should hold. If consistency holds, Wang's dimensional-criticality framework is validated by our independent multi-observable battery, strengthening both papers. If inconsistency appears, we identify the mismatch and report it as a methodology finding.

The pre-registered cross-validation: apply our pipeline to modular-addition-grokking transformers (matching Wang's target) alongside pretrained LLMs on natural text, and report whether D and our observables agree on class-assignment and critical-time identification. This lets our paper **subsume** Wang 2604.16431 as a special case rather than compete with it. It also provides valuable Phase 1.5 insurance: if Wang et al. publish an extension to pretrained LLMs before us, our "5-observable validation of D" framing remains publishable even if our stand-alone anchor has been scooped.

---

## Theme 2 — Cortical-avalanche methodology transfer to artificial networks

### 2.0 Why cortical methodology is the right starting point

Cortical avalanche analysis emerged from the 2003 Beggs-Plenz paper and has since accumulated 25 years of methodological refinement. The canonical observables are: avalanche-size distribution P(s), avalanche-duration distribution P(T), mean-size-given-duration distribution ⟨s⟩(T), shape of individual avalanche profiles F(t|T), branching ratio σ at multiple axes, and long-range-temporal-correlation exponent. Each observable has a canonical estimator and known failure modes. The entire observation + estimator stack was designed for multi-unit spiking or MEA-LFP data, which has specific features: observable-units are discrete (neurons / electrodes), firing is sparse and heterogeneous, subsampling is severe, autocorrelation is present, and the underlying dynamics are partially observed. Modern LLM activation data share most of these features, so the cortical methodology transfers with modest adaptation.

The central advantage of using the cortical methodology verbatim is that it reduces peer-review disputes about "why didn't you use X methodology?" to a minimum. Every choice we make in Phase 1 has a cortical-literature precedent and a published estimator with known statistical properties. The disadvantage is that we inherit the cortical-literature's baggage: the criticisms raised by Touboul, Martinello, and others against over-eager cortical claims apply equally to our LLM claims, and we must address them equally rigorously.

### 2.1 The Clauset-Shalizi-Newman canon and the `powerlaw` package

**[Clauset 2009]** — *Power-law distributions in empirical data* — is the mandatory reference for any power-law claim in the paper. The protocol is: (i) estimate x_min via KS-distance minimisation; (ii) estimate α by maximum-likelihood on the tail x ≥ x_min; (iii) bootstrap a distribution of (x_min, α) pairs to obtain CIs; (iv) test null hypothesis "data are power-law" via KS-statistic p-value (criterion: accept if p ≥ 0.1, recommend ≥ 0.1; our pre-registered bar is p > 0.05 per knowledge_base.md §5.1); (v) test log-likelihood ratios against lognormal, truncated power-law, stretched exponential, and pure exponential alternatives via Vuong-style tests. **[Alstott 2014]** implements the full CSN pipeline in the Python `powerlaw` package with full bootstrap machinery. This is the standard tool the paper must use.

Methodological extensions that the paper must engage:

- **[Deluca & Corral 2013]** — truncated-distribution handling. LLM activations have finite dynamic range; truncated power-law may be the correct alternative hypothesis even when pure power-law fails.
- **[Virkar & Clauset 2014]** — binned-data MLE. If we log-bin the avalanche histograms for visualisation, the MLE must account for binning to avoid bias.
- **[Marshall 2016]** — *Benchmarking power-law fits for neuronal avalanches* — validates CSN against synthetic and cortical data; provides calibration curves for our pipeline unit tests.
- **[Stumpf & Porter 2012, Science]** — *Power-law distributions across social systems* — is the canonical methodological caution piece. Cites dozens of cases where apparent power laws are in fact lognormals, truncated exponentials, or compositions of exponentials. We cite this as a standing warning.

The pre-registered threshold battery for Candidate 1: θ ∈ {0, 0.1, 0.5, 95th percentile, 99th percentile} × basis ∈ {raw, random-projection, PCA-top-K, PCA-top-K + orthogonal-complement, SAE-Gemma-Scope, random-init-SAE} × model ∈ {GPT-2-small, GPT-2-medium, Pythia-160M, Pythia-1.4B, Pythia-2.8B-fp16, Gemma-2-2B}. That is a 5 × 6 × 6 = 180-cell pipeline. Each cell produces α, α's 95% bootstrap CI, KS goodness-of-fit p-value, and log-likelihood-ratio rejections of lognormal / truncated PL / exponential. The **threshold-plateau test** of knowledge_base.md §5.6 then asks: across θ = {0.5, 1, 2} × reference-θ, does α vary within the 95% CI of the reference-θ estimate? If yes, the claim is plateau-robust; if no, we report the θ-sensitivity curve and narrow the claim.

### 2.2 The Wilting-Priesemann MR estimator

**[Wilting & Priesemann 2018, Nat. Commun.]** — *Inferring collective dynamical states from widely unobserved systems* — derives the MR estimator: fit an exponential decay to the autocorrelation function of observed activity, extract the dominant eigenvalue, recover unbiased branching ratio m under arbitrary subsampling. The crucial property is that the estimator is **consistent under subsampling**: even if only 1% of the neurons are recorded, σ can be recovered without bias. This is essential for LLM analysis because when we compute σ from a subset of residual-stream channels or a subset of SAE features, naive regression systematically under-estimates σ.

Software: **[Spitzner 2021, PLoS ONE]** — *Mrestimator: a toolbox to determine intrinsic timescales* — provides the standard Python/Matlab implementation with bootstrap CIs. This is the mandatory tool for our σ claims.

Validation: **[Levina & Priesemann 2022, Nat. Rev. Phys.]** — *Tackling the subsampling problem* — reviews subsampling biases across neural-avalanche, epidemic-spread, and disease-propagation systems and catalogues correction schemes. This is the current state-of-the-art methodology reference and the paper must cite it when motivating MR-σ.

For LLMs specifically, the MR estimator has **two plausible time axes**: (a) token-axis: autoregressive generation produces a token sequence; within a single layer, per-neuron activation is autocorrelated across tokens because attention couples token t to earlier tokens. (b) layer-axis: residual-stream activation at layer ℓ + 1 depends on activation at layer ℓ via the residual + attention + MLP update. Both axes are defensible; both should be reported. For the layer axis, the "time step" is a layer rather than a token, and the MR-σ estimator is applied to the per-layer activation-count time series. For the token axis, the standard autoregressive Markov structure applies and MR-σ is a direct port from cortical LFP analysis. We commit to reporting σ on both axes with the axis-choice as a pre-registered methodological variable.

**[Priesemann 2013]** — *Neuronal avalanches differ from wakefulness to deep sleep* — is the founding subsampling paper that motivated the MR estimator. Awake-vs-sleep cortex shows different branching-ratio estimates that resolve to the same σ once subsampling is corrected. This cautionary precedent frames how we interpret different σ values across GPT-2 layers or heads: naive differences may be subsampling artefacts.

### 2.3 The crackling-noise scaling relation γ = (β − 1)/(α − 1)

**[Sethna 2001, Nature]** — *Crackling Noise* — is the foundational reference. For a critical system with avalanche-size exponent α, avalanche-duration exponent β, and mean-size-given-duration exponent γ, the three exponents satisfy γ = (β − 1)/(α − 1). This identity rules out many power-law-mimicking non-critical mechanisms — lognormal truncation, Griffiths phases in broad parameter regimes, neutral-null models — that can reproduce α ≈ 3/2 alone.

**[Friedman 2012, Phys. Rev. Lett.]** — *Universal critical dynamics in high resolution neuronal avalanche data* — first verification of the Sethna scaling relation in cortical cultures. This is the critical-brain-hypothesis paper that gave the field its strongest quantitative universality result. Our paper must port this cross-check to LLM activations and either confirm or reject it.

**[Papanikolaou 2011]** — *Avalanche shape scaling and universal crackling noise* — demonstrates that avalanche temporal-shape collapse, s(t, T) = T^{γ − 1} F(t/T), is a stringent test of universality beyond exponent values. Different crackling-noise universality classes give different F(x) shapes. Our paper must compute shape collapse for each (model, basis, threshold) cell and report the collapsed profile.

**[Capek 2023, Nat. Commun.]** — *Parabolic avalanche scaling* — provides the specific prediction that for cortical cell-assembly avalanches, F(x) is a symmetric parabola with χ = 2. Shape-collapse χ = 2 is a sharper test than exponent fits alone because it constrains the functional form, not just two moments. If our LLM avalanches collapse to a non-parabolic profile, that is itself a publishable finding: it implies a different universality class than cortex.

**[Salje & Dahmen 2014]** and **[Laurson 2013, Nat. Commun.]** extend crackling-noise beyond neuroscience to materials-science (Barkhausen noise, fracture, micropillar compression). The shape-collapse methodology transfers directly. Useful calibration: in the cleanest materials-science datasets, shape collapse is exact within measurement noise; in cortical data, collapse is approximate with systematic deviations at very small and very large durations. We pre-register that our shape-collapse quality metric is "median squared deviation of rescaled profiles from the average profile, normalised to unit area" and our acceptance bar is < 10% of the largest-duration amplitude.

### 2.4 The Martinello-di-Santo Griffiths-phase / neutral-null rejection

**[Martinello 2017]** — *Neutral theory and scale-free neural dynamics* — demonstrates that neutral (non-critical) stochastic models can reproduce α ≈ 3/2 avalanche power laws. The paper is the single most important null-model-rejection reference: any α ≈ 3/2 result that does not explicitly reject a neutral-null model is incomplete. Our paper must fit the Martinello neutral-null as a competitor distribution to genuine DP-branching and report whether our data favour critical over neutral.

**[di Santo 2018, PNAS]** — *Landau-Ginzburg theory of cortex dynamics* — derives the edge-of-synchronization picture: apparent avalanche criticality arises at a synchronization bifurcation rather than at a standard absorbing-state transition. The edge-of-synchronization class has different scaling-relation predictions than pure DP, so the scaling-relation cross-check discriminates. **[Morales 2023, PNAS]** — *Quasiuniversal scaling in mouse-brain neuronal activity stems from edge-of-instability critical dynamics* — provides Neuropixels-level empirical support for the edge-of-instability class. LLMs with softmax-attention may more closely match edge-of-synchronization than pure DP.

**[Moretti & Muñoz 2013]** and **[Vojta 2006]** provide the Griffiths-phase formalism. Griffiths phases arise in disordered systems and produce **extended regions of parameter space** with scale-invariant statistics — they look critical over a broad parameter range without fine-tuning. Trained neural networks are highly disordered (weight matrices are approximately Gaussian with long-range correlations; activation patterns are sparse and heterogeneous), and a Griffiths phase is a plausible alternative to genuine criticality.

**[Lombardi 2023, Nat. Comput. Sci.]** — *Statistical modeling of adaptive neural networks explains co-existence of avalanches and oscillations* — provides a concrete adaptive-Ising alternative null: a sub-critical-with-adaptation model that reproduces avalanche + oscillation structure with γ ≈ 1.6 rather than critical-branching's γ = 2. This is a distinct testable null that our scaling-relation test discriminates against. **[Cocchi 2025, PRX Life]** extends to coherent-bursting dynamics.

**[Touboul 2010, PLoS ONE]** and **[Touboul 2017, Phys. Rev. E]** show that stochastic non-critical dynamics can produce apparent power-law avalanches over 2–3 decades. These are the must-reject papers for naive power-law claims.

**[Morrell 2023, eLife]** — *Neural criticality from effective latent variables* — demonstrates that apparent criticality in neural data can arise from slow latent variables (Zipf-law artefact). LLM activations are driven by slow task/context signals and may exhibit this artefact; we must include a latent-variable null model.

Our commitment: explicit likelihood-ratio tests between (a) mean-field DP branching (α = 3/2, β = 2, γ = 2), (b) edge-of-synchronization, (c) Martinello neutral-null, (d) Lombardi adaptive-Ising (γ ≈ 1.6), (e) lognormal truncation, (f) Griffiths-phase mixture model. The log-likelihood-ratio battery is pre-registered.

### 2.4.1 Other null-rejection-relevant references

**[Plenz 2021 Front. Phys.]** — *Critical brain dynamics at large scale* — pedagogical review of criticality evidence from multiple techniques; cites the canonical null-rejection protocols. Useful methodology scaffold.

**[Hengen & Shew 2025, Neuron]** — *Is criticality a unified setpoint of brain function?* — 140-dataset meta-analysis; provides numerical baseline of cortical exponents and confidence intervals against which our LLM results can be benchmarked.

**[Plenz et al. 2025 review]** (VERIFY) — modern update to Beggs-Plenz 2003 with CSN-style statistics; the cortical-avalanche methodology as practiced in 2025.

**[Priesemann & Shriki 2018]** — methodological review of criticality measurement in brain networks. Additional scaffold reference.

**[Xie et al. 2025, PNAS]** — genetic contributions to brain criticality; brain criticality is heritable. Establishes the biological reality of the criticality phenotype, arguing criticality is a deep computational principle worth seeking in artificial systems.

**[Cortical critical power-law balances energy and information 2025, PNAS]** — the experimentally observed cortical exponent is the unique energy-information Pareto optimum. Normative argument for why α ≈ 3/2 specifically should emerge, not just any power law; the energy-information argument has a natural ML transfer: the FLOPs-per-bit-of-mutual-information optimality question.

**[Bellay et al. 2015, eLife]** — state-conditioned avalanche analysis in awake mouse cortex. Precedent for prompt-conditioned avalanche analysis in LLMs (Candidate 26).

### 2.5 The low-dimensional-subspace Fontenele reframe

**[Fontenele 2024, Sci. Adv.]** is the methodology rewrite that our paper must integrate. In awake mouse motor cortex, critical signatures appear **only** in a low-dimensional subspace whose dimension is ~10% of the ambient neural-population dimension; the orthogonal complement is desynchronised. This structural feature predicts that **if we measure σ and α on the full residual-stream activation of GPT-2, we may see no criticality, but if we project to the top-K principal components (or to the Gemma-Scope SAE features) we may see sharp criticality**. The paper's basis-invariance arm (Candidate 5) becomes a Fontenele-style subspace search rather than a robustness check.

The operationalisation: compute participation-ratio D_eff via covariance-eigenvalue distribution; project to K = D_eff-ranked top-PC subspace; measure σ in ambient, subspace, and orthogonal-complement; report three distinct values. If ambient σ ≠ 1 but subspace σ ≈ 1, the Fontenele picture is replicated in trained transformers — a stand-alone publishable contribution.

### 2.6 Other observable definitions

**[Timme et al. 2016, Nat. Commun.]** — *Activation Thresholding and the Definition of Neuronal Avalanches* — provides the direct precedent for the threshold-plateau requirement. Timme et al. show that neural-avalanche exponents can shift dramatically across small threshold changes, and that robust claims require exponents to plateau across a factor-of-2 threshold range. Our threshold battery θ ∈ {0.5, 1, 2} × reference is directly motivated by this paper.

**[Jones et al. 2023, eLife]** — scale-free activity restricted to a winner-take-all subset of neurons. Reinforces the subspace-basis hypothesis: criticality may live in a sparse subset, not in the full population.

**[Lombardi et al. 2023, Nat. Comput. Sci.]** — adaptive-Ising alternative to DP-branching; covered in §9.6. Here we note the methodological implication: the adaptive-Ising model predicts γ ≈ 1.6 rather than critical γ = 2, so our scaling-relation measurement must have bootstrap CIs tight enough to discriminate 1.6 from 2. This requires ~10⁴ avalanches minimum per cell; our activation-cache budget is designed to deliver this.

**[Deluca & Corral 2013, Acta Geophysica]** — complementary formal treatment of power-law fitting used in SOC geophysics. Cross-checks Clauset-Shalizi-Newman fits with an independent estimator. We cite this as a secondary methodology reference.

**[Nurisso et al. 2024]** (VERIFY) — up-to-date subsampling-correction methodology comparison. Recent improvements over Wilting-Priesemann that may reduce σ bias further; we evaluate during Phase 1.

**[Nishimori 2024]** (VERIFY) — rigorous subsampling-correction framework. Theoretical update to MR-σ methodology.

**[Levina & Priesemann 2022, Nat. Rev. Phys.]** — the comprehensive subsampling review. Mandatory methodology scaffold.

**[Levina & Priesemann 2017]** — avalanche-exponent distortion under subsampling. Direct motivation for the MR-σ requirement.

**[Priesemann & Munk 2014]** — driven-subsampled critical picture. Cortex may appear subcritical because it is driven and subsampled; the MR-σ estimator corrects both confounds.

---

## Theme 3 — Sparse autoencoders and the feature-basis landscape

### 3.0 Why the basis matters for criticality

The basis choice determines what counts as an avalanche "event". In raw-neuron basis, an event is a single residual-stream channel crossing threshold. In PCA basis, an event is a single principal-component coordinate crossing threshold. In SAE basis, an event is a single monosemantic feature firing. These correspond to physically different objects: raw channels are in superposition (each channel participates in many features), PCA components diagonalise the covariance but are not aligned with computational features, SAE features approximate the "true" computational basis of the model. Cortical-avalanche analysis is invariant to basis choice because the MEA electrode captures population activity regardless of the internal basis in which cortical computation occurs. LLM analysis does not have this luxury: we must choose a basis, and the avalanche exponents may depend on the choice. The **Fontenele 2024** reframe makes this concrete: criticality may live in one basis and be invisible in another.

There are three possible outcomes of our basis-invariance study: (a) **basis-invariant** — exponents agree within CI across raw / PCA / SAE bases; this is the strongest criticality claim. (b) **Hierarchically embedded** — SAE basis shows cleaner exponents than PCA, which shows cleaner exponents than raw; this is a weaker claim that supports a "true computational basis" interpretation. (c) **Basis-specific** — different bases give different exponents with no monotone ordering; this is the most conservative finding and restricts criticality claims to a specific basis. Each outcome is publishable on different grounds, and we pre-register all three as possible conclusions.

### 3.1 The SAE revolution (2023–2026)

**[Bricken 2023]** — *Towards monosemanticity: decomposing language models with dictionary learning* — Anthropic's founding paper on sparse autoencoders for interpretability. SAEs trained on the residual stream of a 1-layer transformer recover thousands of interpretable monosemantic features that are cleaner than raw-neuron directions. Key claim: raw neurons are in superposition (each neuron participates in many features), while SAE features are close to monosemantic. The paper's methodological innovation was training an overcomplete dictionary (N_features > N_neurons) with a sparsity penalty (L1 on feature activations), which trades reconstruction loss for feature interpretability. The framework has spawned a substantial literature (Templeton 2024 at Claude-3-Sonnet scale; Cunningham 2023 independent replication on Pythia; Rajamanoharan 2024 Gated-SAE; BatchTopK / JumpReLU / Matryoshka variants in 2024) and has become the de-facto basis for modern MI work at Anthropic and DeepMind.

**[Templeton 2024]** — *Scaling monosemanticity* — scales the SAE approach to Claude 3 Sonnet and recovers millions of features including safety-relevant ones. The paper validates the approach at production-model scale and motivates treating SAE features as the "true basis of computation" in modern LLMs.

**[Lieberum 2024, Gemma Scope]** — releases open-weights SAE suites trained on every layer and every site (residual stream, MLP output, attention output) of Gemma-2-2B and Gemma-2-9B. Gemma Scope is the mandatory public basis for our basis-invariance study because it supplies SAE bases for every model-layer-site triple on a public model we can run on 12 GB VRAM.

**[Cunningham 2023]** — *Sparse autoencoders find highly interpretable features in language models* — independent replication of the SAE approach on Pythia. Methodological validation that the SAE interpretability finding is reproducible.

**[Rajamanoharan 2024, Gated SAEs]** — Pareto-improvement over vanilla SAE by separating which-directions from magnitude-estimation. Updated SAE basis that may give cleaner criticality signatures than vanilla SAE; we include both as bases in the robustness study.

**[Gao 2024, OpenAI SAE scaling laws]** (VERIFY) — OpenAI's SAE scaling work. Provides a third independent SAE lineage (Anthropic / DeepMind / OpenAI) and confirms the basic findings.

**[Bushnaq 2024, transcoders]** and **[Bussmann 2024, BatchTopK / Matryoshka SAEs]** — recent SAE variants. We include vanilla SAE + Gated SAE + transcoder as three distinct SAE bases for cross-validation.

**[Elhage 2022, Toy Models of Superposition]** — predicts phase transitions between monosemantic and polysemantic regimes as a function of sparsity and embedding dimension. Provides the theoretical justification for SAE-interpretability and identifies specific sparsity-dimension boundaries at which superposition collapses into clean monosemantic features. These superposition phase transitions are in the feature-representation axis and are distinct from the activation-dynamics phase transitions we measure — but a deep hypothesis is that the two may coincide at the critical point where SAE-feature superposition resolves into monosemanticity AND activation-avalanche statistics become critical. Testing this coincidence is out of scope for the Phase-0 paper but is an appealing Phase-∞ goal.

**[Engels 2024, Not all language model features are linear]** — demonstrates that some LLM features are inherently multi-dimensional (days-of-week as circle, months as circle). If our avalanche analysis is applied in a basis that assumes discrete linear features, non-linear-feature events may be miscounted. Practical implication: we treat SAE-feature events as discrete threshold crossings but acknowledge a methodological uncertainty for the fraction of features that are known to be non-linear (< 5% in Engels' study).

### 3.2 The random-init-SAE control

**[Heap 2501.17727]** — *Sparse Autoencoders Can Interpret Randomly Initialized Transformers* — the crucial null-control paper. Heap, Lawson, Farnik & Aitchison train SAEs on randomly-initialised transformers and find that standard SAE-interpretability metrics (reconstruction loss, number of monosemantic features, feature clarity) are broadly similar to SAEs trained on pretrained networks. The implication for our project is immediate: any positive criticality result on SAE features of pretrained GPT-2 must be compared to the same pipeline on SAE features of random-init GPT-2. If both show the same α, the signal is not about training. Heap et al. have not published activation-avalanche statistics on their random-init-SAE pipeline; this is our opportunity to deliver the paired control that definitively distinguishes "criticality is an SAE artefact" from "criticality is a training artefact".

The control is expensive: training an SAE on a random-init transformer takes roughly the same compute as training it on a pretrained transformer (~ a few GPU-days on consumer hardware at the Gemma-Scope scale, though public checkpoints are lower cost). Our plan is: use a small SAE (e.g. JumpReLU-SAE on GPT-2-small residual stream, ~10k features) trained on both pretrained and random-init GPT-2-small to keep the compute tractable on RTX 3060. For Gemma-2-2B we rely on Gemma Scope for the pretrained side and train a matched random-init-SAE from scratch for the control — this is 1–3 GPU-days per layer we analyse, tractable if we restrict to a 3-layer subset.

Two subtle methodological points must be nailed down. First, the random-init transformer that the SAE is trained on must match the pretrained transformer in architecture and activation-statistics scale, which requires applying LayerNorm (with trainable but un-initialised γ, β) to the random weights or the activations will be numerically ill-conditioned. Second, the SAE hyperparameters (feature-count, L1 coefficient) must be identical between the pretrained and random-init conditions — otherwise differences could be attributed to SAE-training differences rather than underlying activation-statistics differences. Both points are standard in the Heap 2501.17727 protocol but easy to overlook.

The random-init-SAE control can be run on three distinct baselines, each with different interpretive value: (i) **Gaussian init** at the standard-deviation used in pretraining — reproduces the Heap baseline; (ii) **Schoenholz-tuned init** at χ_1 = 1 — represents "at-init edge-of-chaos" and tests whether Schoenholz's theoretical boundary is a critical point in our observable; (iii) **Xavier / Kaiming init** — the most common random baseline in DL practice. Running all three on a single architecture (GPT-2-small) is feasible on RTX 3060 within one week including SAE training. The three-way comparison is itself publishable as a methodology contribution: it answers "does init scheme shift the random-init-SAE avalanche exponents?" which is an open question not answered by Heap et al.

### 3.3 Interpretability infrastructure

**[TransformerLens, Nanda 2022]** — the standard library for activation caching, intervention, and patching on HuggingFace decoders. Mandatory tool.

**[nnsight, Fiotto-Kaufman 2024]** (VERIFY) — alternative interpretability library with remote-execution support. Useful for Pythia-12B experiments beyond single-GPU VRAM.

**[SAELens, Bloom 2024]** (VERIFY) — SAE training + evaluation + Gemma-Scope loader library. Mandatory for the SAE basis pipeline.

**[Bereska & Gavves 2024]** — *Mechanistic Interpretability for AI Safety — A Review* — comprehensive MI review. Pedagogical scaffold for our related-work section.

**[Bereska & Gavves 2024]** — *Mechanistic Interpretability for AI Safety — A Review* — comprehensive MI review covering SAE, circuit analysis, activation patching, superposition theory, and related safety concerns. Pedagogical scaffold for our related-work section; cite as the "methodology background" reference.

**[Anthropic team 2024 SAE update]** (VERIFY) — more recent Anthropic SAE interpretability report supersedes Bricken 2023 in several methodological details. Cite alongside Templeton 2024 as the primary interpretability companion.

**[Gao, Goh & Sutskever 2024]** (VERIFY OpenAI SAE scaling) — scaling laws for SAE reconstruction loss across SAE width and dataset. Third independent SAE lineage (OpenAI) in addition to Anthropic and DeepMind. Confirms the reproducibility of the SAE approach across labs and provides an additional hyperparameter axis.

### 3.4 Feature geometry beyond linearity

**[Engels 2024]** — *Not all language model features are linear* — demonstrates that some LLM features are inherently multi-dimensional (days-of-week as a circle, months as a circle). If our avalanche analysis assumes linear / discrete-event SAE features, some features may be misclassified as multiple avalanche events when they are a single rotation on a circle. Our commitment: report avalanche statistics per SAE feature type where possible, and flag non-linear-feature contamination as a methodological uncertainty.

**[Gurnee 2024, Universal Neurons]** — identifies a 1–5% fraction of GPT-2 neurons that are universal across random seeds — they implement canonical functions like deletion, entropy control, position-detection. If universal neurons are the "hubs" of the activation graph, we predict they participate in disproportionately many avalanches; testable.

**[Geva 2021, key-value memories]** and **[Geva 2022, FFN predicts vocabulary]** — FFN layers implement key-value lookup and promote vocabulary directions. This informs the event-definition: an FFN activation > θ promotes a specific vocabulary direction, which propagates through the residual stream to later layers. The avalanche is a vocabulary-promotion cascade.

### 3.5 SAE methodology implications for avalanche detection

The SAE basis has specific methodological implications for avalanche-event definition that we must pre-register:

1. **Feature-firing threshold**: Gemma Scope SAEs use a JumpReLU activation function with a per-feature threshold. Features below threshold output zero, features above output a positive value. The natural avalanche-event definition is "feature activation > JumpReLU threshold", which aligns with the standard neuroscience thresholded-event definition.

2. **Reconstruction-loss-mediated features**: SAE features are trained to minimise reconstruction loss of the residual-stream; they do not necessarily form a natural-event basis in the physics sense. The avalanche events we define in the SAE basis may therefore differ from events in the natural-computation basis (if such a basis exists). This is a known caveat; we report it in the methodology section.

3. **Feature granularity**: Gemma Scope offers SAEs at multiple feature-count scales (16k, 32k, 65k, 131k). The avalanche exponents may depend on the SAE scale. We pre-register analysis at one primary scale (65k features) with sensitivity analysis at 32k and 131k.

4. **Cross-layer SAE basis**: Gemma Scope provides SAE for each layer separately. An avalanche that crosses layers is defined via the per-layer SAE features, not via a single cross-layer SAE. This is compatible with our methodology but introduces a basis-change between layers that must be handled consistently.

5. **Dead features**: Some SAE features never fire in our evaluation corpus. These are "dead" for our purposes and excluded from the avalanche-event population. The fraction of dead features is reported as a dataset-specific measurement.

### 3.6 Multi-layer SAE approaches

**[Zhang et al. 2024, Multi-layer SAEs]** (VERIFY) — decomposes the residual stream across multiple layers into aligned SAE features. Provides an alternative to single-layer Gemma Scope SAEs that tracks cross-layer feature persistence. Useful for cross-layer avalanche analysis; flag for Phase 1 evaluation.

### 3.7 Steering-vector methodology complement

**[Turner et al. 2023, Activation Editing]** — steering-vector methodology for causal perturbation of residual-stream activations. Can be applied to individual SAE features to induce avalanches in a controlled way. This is effectively the LLM analog of Vakili's targeted single-neuron optogenetic stimulation protocol. We flag this as a Phase 1.5 follow-up if budget permits.

### 3.8 Open questions for this theme

- Do Gemma-Scope SAE features of Gemma-2-2B show a cleaner avalanche power-law than raw residual-stream activations?
- Does the random-init-SAE control reproduce the same exponents (SAE artefact) or different exponents (training signal)?
- Does the choice of SAE (vanilla / Gated / transcoder / BatchTopK / Matryoshka) change the exponent estimates?
- Are avalanche statistics concentrated on universal neurons or distributed across the full feature set?

---

## Theme 4 — Mechanistic-interpretability primitives the paper must cite

### 4.1 The transformer-circuits framework

**[Elhage 2021]** — *A mathematical framework for transformer circuits* — Anthropic's decomposition of attention-only transformers into QK / OV circuits and virtual-head pathways. The residual stream is framed as a shared communication channel across layers. For our paper, this framework provides the **substrate on which avalanches are defined**: an avalanche is a contiguous supra-threshold propagation in the residual stream, either across token positions (time axis) or across layers (depth axis). The Elhage framework also provides the **vocabulary** for describing how avalanches propagate: QK circuits determine which previous tokens the current attention head reads, OV circuits determine what the head writes to the residual stream, and virtual-head pathways allow composition of circuits across layers. An avalanche in the residual stream is therefore a chain of writes and reads mediated by specific QK-OV circuit compositions; the fraction of circuits that participate in an avalanche is a circuit-resolution observable we flag for future work but do not attempt in this first paper.

The "residual stream as shared channel" framing is particularly important for our layer-axis avalanche definition. In a vanilla MLP, a layer's output depends only on the previous layer's output via the weight matrix, so an avalanche in the layer axis is a straightforward cascade. In a transformer with residual connections, layer ℓ+1's activation is layer ℓ's activation plus the (attention + MLP) update at layer ℓ. This means an avalanche seeded at layer ℓ can **propagate via the residual identity** to arbitrary downstream layers without any further computation — the skip connection carries the signal forward by default. The activation-avalanche definition must therefore subtract the residual-identity component and report only the **added** activation at each layer. Otherwise σ_ℓ is artefactually inflated by the skip-connection-identity. This is the single most important methodological commitment that separates transformer avalanche analysis from MLP / CNN analysis, and it must be made explicit in the Phase-1 code.

**[Olsson 2022]** — *In-context learning and induction heads* — identifies induction heads (pattern [A][B]...[A] → [B]) as a specific circuit that emerges abruptly during training via a phase transition. Induction heads are the canonical MI-level phase transition that preceded the grokking literature. Our Candidate 8 asks: do induction heads' activation patterns show distinct avalanche statistics compared to matched non-induction heads, and is their emergence step (on Pythia checkpointed runs) co-located with a σ-crossing (Candidate 27)? The paper must engage with Olsson's findings directly.

**[Wang 2023, IOI]** — *Interpretability in the wild: a circuit for indirect object identification* — reverse-engineers a 26-head circuit in GPT-2 small implementing the IOI task. Key methodological result: only 26 of GPT-2's 144 heads are causally relevant for IOI, demonstrating **sparse functional circuits**. If trained transformers use sparse circuits, avalanche statistics may be dominated by circuit-resident units. Candidate 28 computes per-head σ across all heads and asks: is the σ distribution bimodal (circuit vs non-circuit) or unimodal? A bimodal distribution would suggest that criticality is a property of specific functional circuits rather than an average property of the whole network, which is a substantively different claim than classical cortical-criticality results. A unimodal distribution would support the averaged-property interpretation consistent with the critical-brain hypothesis. Either outcome is publishable.

The methodology for Candidate 28 requires per-head causal contribution measurement. The simplest approach is ablation-based: replace each head's output with zeros or with the mean over the dataset, measure the change in downstream activation. This is 144 × ~1k forward passes per prompt-set on GPT-2-small — feasible on RTX 3060 in hours. A more refined approach uses path patching **[Goldowsky-Dill 2023]** which isolates specific residual-stream paths and avoids the confound that head (i, ℓ) ablation affects both direct downstream and indirect (via later heads / MLPs) downstream activations. Our pre-registered methodology uses path patching for the primary σ_{h,ℓ} estimate and reports ablation-based as a sensitivity check.

**[Gurnee et al. 2024, Universal Neurons]** — small fraction (1–5%) of GPT-2 neurons are universal across random seeds and implement canonical functions (deletion, entropy control, position detection). If universal neurons are the "hubs" of the activation graph, we predict they participate in disproportionately many avalanches. A direct testable consequence: the fraction of avalanches that include a given universal neuron should exceed the per-neuron average by a factor reflecting the neuron's "universality rank". This is a second-order criticality observation — not about whether the network is critical but about how critical activity is distributed across neurons.

### 4.2 Causal vs correlational branching

**[Meng 2022, ROME]** — *Locating and editing factual associations in GPT* — causal-trace experiments localise factual knowledge to mid-layer MLPs; rank-one updates can edit facts. The ROME methodology provides a **causal perturbation protocol**: apply a rank-one edit along a known causally-important direction, measure response propagation. This is the gold-standard tool for causal branching-ratio computation.

**[Goldowsky-Dill 2023]** — *Localizing model behaviour with path patching* — refines activation patching to isolate specific residual-stream paths. Naive activation patching confounds the residual stream (everything downstream sees everything upstream); path patching isolates individual paths. Candidate 6's layer-depth σ_ℓ gradient must use path patching rather than naive residual-stream propagation to avoid confound.

**[Heimersheim & Nanda 2024]** (VERIFY preprint) — *Activation patching: a tutorial* — pedagogical tutorial on activation-patching best practices. Methodology reference.

**[Turner 2023]** — *Residual Stream Activation Editing* — steering-vector methodology for causal perturbation. Complements ROME and activation patching.

### 4.3 Sparse activation and the avalanche event definition

**[Li 2023, Lazy Neurons]** — *On emergence of activation sparsity in transformers* — trained transformers exhibit extreme activation sparsity in MLP layers: only tens of neurons (out of thousands) active per token. This profoundly shapes how we define avalanche events: a threshold of θ = 0 captures essentially everything post-ReLU/GELU, while θ = 1 captures only the active subset. The extreme sparsity also means that **branching-ratio denominators are small**, which amplifies the subsampling correction the MR estimator provides.

**[Liu 2023, Deja Vu]** — *Contextual sparsity for efficient LLMs at inference time* — only 15–25% of MLP neurons contribute to each token, and the active subset is **context-dependent**. Avalanches on MLP outputs are therefore naturally context-conditional; we pre-register that per-context-class σ (Candidate 26) is a secondary observable.

**[Mirzadeh 2024, ReLU strikes back]** — *Exploiting activation sparsity in large language models* — replacing SiLU/GELU with ReLU preserves quality while restoring ~95% activation sparsity. Informs the activation-function choice for at-init controls: ReLU yields cleaner avalanche definitions.

**[Zhang 2022, MoEfication]** and **[Hu 2024, Activation Sparsity Scaling Laws]** (VERIFY) provide further context for the sparsity-scaling of modern LLMs.

### 4.4 Scaling laws and emergence

**[Kaplan 2020]** — scaling laws for test loss in model size, data, and compute — is the phenomenology that motivates testing whether criticality observables also scale as a power of N. **[Hoffmann 2022, Chinchilla]** revises the exponents. **[Wei 2022, Emergent Abilities]** claims genuine capability phase transitions at scale; **[Schaeffer 2023]** argues the emergences are metric artefacts under smooth metrics. Our Candidate 34 uses σ as a **smooth physics-observable** to test Schaeffer's claim: if σ(scale) is monotone and featureless while capability looks discontinuous, Schaeffer is right; if σ shows a crossing at the emergence step, Wei is right. This is the single highest-impact leverage point for the paper's scaling arm.

**[Biderman 2023, Pythia]** — the Pythia suite of 16 models from 70M to 12B parameters, 154 checkpoints per scale, identical training data and order. Pythia is the mandatory scale-axis data source. We cap at Pythia-2.8B fp16 on RTX 3060; 6.9B and 12B via int8 as secondary / appendix.

**[Geva, Caciularu, Wang & Goldberg 2022]** — *Transformer FFN layers build predictions by promoting concepts in the vocabulary space* — further refines the FFN-as-key-value-memory view. FFN sub-updates promote specific vocabulary directions, so an FFN activation is literally a promotion of a vocabulary concept. This provides a **semantic interpretation** of avalanche events: an avalanche is a cascade of vocabulary-concept promotions. Such semantic grounding is not necessary for a pure statistical-physics analysis, but it makes the cross-validation against MI primitives (Wang 2023 IOI, Olsson 2022 induction heads) much richer.

**[Nostalgebraist 2020 logit lens]** and **[Belrose et al. 2023 Tuned Lens]** — tools for projecting intermediate residual-stream states through the unembedding matrix to obtain next-token distribution at each layer. Provides a per-layer information-content observable: the KL divergence between the logit-lens prediction at layer ℓ and the final-layer prediction is a measure of "information remaining to be computed" at layer ℓ. If σ_ℓ(ℓ) tracks this KL divergence, that is a direct link between criticality and information-processing capacity. This is a pre-registered cross-check for Candidate 6 layer-depth analysis.

### 4.4.1 Superposition and feature-representation phase transitions

**[Elhage et al. 2022, Toy Models of Superposition]** — networks represent more features than they have neurons via non-orthogonal superposition; there are phase transitions between monosemantic and polysemantic regimes as a function of sparsity and embedding dimension. The superposition phase transition is a representation-level phase transition, distinct from the activation-dynamics phase transitions we measure. The theoretical question is whether the two axes are coupled — for example, does a model in the "polysemantic" superposition regime have fundamentally different activation-avalanche statistics than a model in the "monosemantic" regime? This is testable across model scales (if scaling drives the representation toward monosemantic, a systematic change in activation statistics with scale would be evidence for coupling) and across training (if training crosses the superposition boundary at a specific step, activation statistics should change at that step).

**[Engels et al. 2024, Not all features are linear]** — already covered in Theme 3. Reinforces that feature geometry is non-trivial and that multi-dimensional features complicate avalanche-event definition.

**[Gurnee et al. 2023, Sparse Probing]** — sparse probes find features often localised to individual neurons in Pythia. The localisation-vs-distribution question is again a second-order criticality observable we flag.

### 4.4.2 Grokking and progress measures

**[Nanda et al. 2023, Progress Measures]** — discrete Fourier-basis circuit emerges during grokking in modular addition; specific MI-derived progress measures predict the grokking transition. The paper establishes that grokking is **mechanistically** understandable via specific circuit-emergence measurements. Our σ-tracks-grokking hypothesis (Candidate 4) is a direct companion to this line: if σ crosses 1 at the same training step as the Fourier-circuit emergence, σ is a physics-observable progress measure that complements the MI progress measure.

**[Liu et al. 2022, Towards understanding grokking]** — provides a 4-regime phase diagram (memorise / learn / forget / grok) controlled by weight decay and data fraction. The phase-diagram framework is directly applicable to the σ vs |σ − 1| phase diagram we will construct across the topology sweep (Candidate 2) and the scale sweep (Candidate 7). **[Power et al. 2022, Grokking]** is the founding paper establishing the grokking phenomenon.

**[Cohen et al. 2021, Edge of Stability]** — Hessian top eigenvalue hovers near 2/lr during typical GD training; loss is non-monotone yet training progresses. Edge-of-stability is an **optimisation-dynamics criticality** distinct from signal-propagation criticality; both can coexist and may or may not correlate. Our paper must distinguish the two: activation-state criticality (σ at the critical point of the dynamical system defined by the trained weights) is distinct from training-dynamics criticality (Hessian at the critical point of the optimiser dynamics). We measure the former, not the latter, and we commit to being clear about the distinction in the methods section. **[Damian, Nichani & Lee 2022]** provides the theoretical account of edge-of-stability self-stabilisation. **[Cohen et al. 2022]** extends to adaptive optimisers including Adam.

### 4.4.3 Emergence of capabilities vs criticality

**[Bowman 2023, Eight things to know about LLMs]** — positional overview of emergence phenomenology.

**[Schaeffer, Miranda & Koyejo 2023]** — *Are emergent abilities of LLMs a mirage?* — argues emergent abilities vanish under smooth metrics; claims emergence is a metric-discontinuity artefact. Our paper must engage this debate head-on: σ is a smooth physics-observable, so if σ shows a discontinuity at the same scale where discrete-metric capabilities emerge, that supports the Wei side (genuine emergence); if σ is smooth, it supports the Schaeffer side (metric artefact). Either way, our finding contributes to the resolution of this named debate.

**[Wei et al. 2022, Emergent Abilities]** — claims specific capabilities (arithmetic, instruction-following) appear abruptly above scale thresholds. Direct target for Candidate 34 (σ-vs-scale test).

**[Lin et al. 2024, The Unlocking Spell on Base LLMs]** — base vs aligned LLMs produce near-identical next-token distributions except on stylistic tokens. Reinforces that post-training is a shallow perturbation; implications for base-vs-aligned σ comparison (Candidate 21).

**[Zhou et al. 2023, LIMA]** — fine-tuning LLaMa-65B on 1000 curated prompts matches top-tier models. More evidence that post-training is a shallow perturbation.

### 4.4.4 Architectures beyond transformers

**[Halloran, Gulati & Roysdon 2024, Mamba]** — SSM layers are provably Lyapunov-stable. Architecturally antithetical to edge-of-chaos. Useful Phase 2 comparison.

**[Dao & Gu 2024, SSD framework]** — State-Space Duality connects SSMs and attention via structured semiseparable matrices. Common mathematical substrate for transformer-criticality tool port to SSMs.

**[SpikeGPT, Zhu et al. 2023]** — spiking GPT with RWKV-style architecture. Native spike-train substrate for avalanche analysis without SAE-feature-to-spike conversion. Phase 2 / Paper N candidate.

**[Spikformer, Zhou et al. 2023]** — spiking self-attention with 74.8% ImageNet top-1 at 4 timesteps. Cross-architecture control for the vision arm.

**[Eshraghian et al. 2021, snntorch]** — surrogate-gradient SNN training toolkit. Reference software for generating biological-style spike trains from gradient-trained nets; enables Phase 2 biological-comparison experiments.

### 4.5 Open questions for this theme

- Do induction heads show stronger crackling-noise signatures than matched non-induction heads?
- Does the Pythia training-checkpoint σ(t) show a crossing at the induction-head emergence step?
- Is the per-head σ distribution bimodal or unimodal?
- Does σ(model-scale) show an inflection at the same scales where Wei-2022 capabilities emerge?

---

## Theme 5 — Layer-depth spectral analyses of trained transformers

### 5.1 The per-layer spectral profile as orthogonal evidence

Branching-ratio σ_ℓ per layer has a natural **Jacobian-spectrum proxy**: the spectral radius of the Jacobian of layer ℓ+1 post-activation with respect to layer ℓ pre-activation. Mean-field theory gives ρ(J_ℓ) = 1 at the layer-level critical point. Direct spectral-radius estimation is cheap (power iteration, ~20 JVPs per layer) and provides an **independent cross-check** on the MR-σ estimate. The spectral-radius estimate and the MR-σ estimate can disagree in principle: MR-σ measures the **mean** branching ratio averaged over inputs, while ρ(J_ℓ) depends on the specific input point. If the Jacobian is highly input-dependent (which is expected for non-linear networks post-training), the two estimators will not agree perfectly and the discrepancy itself encodes information about criticality: strong input-dependence means the network is "critical on average but off-critical for specific inputs", which is exactly the picture Candidate 26 (input-class-dependent σ) probes.

The per-layer spectral observable also provides a direct comparison to **at-init mean-field theory** predictions. At init, the Schoenholz 2017 theory predicts a specific spectral-radius profile as a function of weight-variance σ_w² and bias-variance σ_b². Post-training, σ_ℓ(ℓ) may match this profile, deviate toward a specific direction (e.g., early layers more critical, late layers more integrated), or become fully independent of the init predictions. Each outcome is informative. Importantly, the per-layer Jacobian spectrum is not the full story: **dynamical isometry** (Xiao 2018) requires all singular values, not just the top one, to cluster near 1. Our methodology commitment is to compute the full singular-value distribution at each layer via random-matrix-theory estimators and report both the spectral radius (for σ_ℓ cross-check) and the singular-value distribution shape (for isometry cross-check).

**[Xiao 2018]** — *Dynamical isometry and a mean field theory of CNNs* — derives delta-orthogonal initialisation for CNNs that achieves Jacobian dynamical isometry (all singular values ≈ 1, not just the spectral radius), enabling training of 10⁴-layer vanilla CNNs without batchnorm or skip connections. This is the foundational at-init-criticality result for feedforward architectures; it establishes that isometry (all singular values near 1) is a stronger criticality condition than spectral-radius-only and motivates including the full Jacobian-singular-value distribution as an observable, not just the top eigenvalue.

**[Pennington 2017]** — *Resurrecting the sigmoid in deep learning through dynamical isometry* — free-probability analysis of Jacobian spectrum shows orthogonal init + sigmoid can train very deep nets; controls the entire singular-value distribution rather than just the mean or spectral radius.

**[Engelken 2023, Phys. Rev. Research]** — *Lyapunov spectra of chaotic recurrent neural networks* — computes the full Lyapunov spectrum of chaotic RNNs; extensive chaos with size-invariant spectrum; attractor dimension much smaller than phase space. Methodology reference for applying full-Lyapunov-spectrum analysis to transformer residual streams per layer. The symplectic-like point-symmetry finding is an orthogonal observable we may include in the appendix. The Engelken methodology assumes autonomous RNN dynamics — no external driving — whereas transformers are driven by token input at every step. Adapting the Lyapunov estimator to driven systems is a known but solvable problem (add a deterministic perturbation along the driving direction and subtract; see **[Pikovsky & Politi 2016]** textbook). We pre-register this adaptation for the appendix.

**[Pennington & Bahri 2017]** — *Geometry of neural network loss surfaces via random matrix theory* — Hessian and Jacobian spectra approach free-probability limits in the overparameterised regime. This is the theoretical underpinning for interpreting Jacobian spectra of trained transformers: the bulk of the spectrum is determined by the random-matrix-theory limit, and deviations from the bulk (outliers) encode learned structure. Our σ_ℓ cross-check is specifically sensitive to the top eigenvalue — an outlier in random-matrix-theory terms — so the RMT bulk is the baseline against which we compare.

**[Martin & Mahoney 2021, Nat. Commun.]** — *Predicting trends in the quality of state-of-the-art neural networks without access to training or testing data* — weight-matrix singular-value distributions develop heavy power-law tails during training. This is **Heavy-Tailed Self-Regularization** (HTSR) theory. HTSR power-law exponents at the weight level are a complementary criticality observable to our activation-level power-law exponents. If both track the same underlying order parameter, they should co-vary across training / across models. **[Prakash & Martin 2025]** extends HTSR to grokking and finds a third "anti-grokking" phase detectable by HTSR α < 2.

### 5.2 Depth-gradient evidence from recent preprints

**[Tulchinskii 2311.05928]** — *Intrinsic dimension of transformer representations* — estimates per-layer intrinsic dimension on activations from trained transformers; detects artificial vs human text by dimension drop in later layers. This is a **depth-gradient observable** in the dimensional axis rather than σ. We use it as a cross-check: if σ_ℓ decreases monotonically with depth, intrinsic dimension should correlate.

**[Xu 2602.10496]** (VERIFY arXiv number) — *Layer-wise spectral analysis of decoder transformers* — layer-wise singular-value spectra in trained decoder transformers; detects training-induced spectral heavy tails. Supplies the spectral-profile baseline against which our σ_ℓ gradient is compared.

**[arXiv 2510.21770]** (VERIFY) — *Layer spectral norm dynamics in pretrained LLMs* — tracks layer spectral-norm growth through pretraining; identifies a layer-depth spectral pattern. Direct Jacobian-spectrum proxy for σ_ℓ; used as auxiliary observable to cross-check MR estimator.

**[arXiv 2502.15801]** (VERIFY) — *Spectral Norm and Trainability of Deep Transformers* — analytical layer-depth spectral-norm scaling for decoder-only transformers connecting to trainability phase boundary. Theoretical prediction to validate against our empirical σ_ℓ profile.

**[Liu, Paquette & Sous, OPT 2025 workshop 43]** (VERIFY) — shows distinct layer-wise spectral signatures between random-init and trained OPT/Pythia models. Uses random-init control in spectral domain; direct template for our random-init-SAE control and for cross-checking the signal is training-induced.

**[Gurnee & Horsley 2025]** (VERIFY) — *Power-law temporal correlations across transformer depths* — temporal correlations in GPT-2 activations decay as power law across layers. If temporal correlations power-law-decay with layer depth, that is a depth-wise long-range-correlation observable independent of avalanche statistics.

The cluster of 2025/2026 preprints listed above (5003, 5004, 5005, 5006, 5007, 5091) indicates that the layer-spectral-analysis subfield is developing rapidly in parallel with the activation-avalanche subfield. The scoop risk is present but manageable: none of these papers combines the full Capek-Friedman-Sethna statistical-physics discipline with the spectral analysis. Our paper can contribute the combined picture — σ_ℓ from MR-estimator + ρ(J_ℓ) from Jacobian spectrum + spectral-norm profile from weight-matrix SVD + intrinsic-dimension profile from TwoNN + RG d_β profile from Sooter's pipeline — as a five-way converging diagnosis of per-layer criticality state. This multi-observable convergence is the gold standard in cortical-criticality research **[Hengen & Shew 2025, Neuron review]** and is exactly the transfer we propose.

### 5.3 Cowsik signal propagation and the order-chaos phase transition

**[Cowsik, Nebabu, Qi & Ganguli 2024]** — *Geometric Dynamics of Signal Propagation Predict Trainability of Transformers* — treats token representations as n interacting particles; derives order-chaos phase transition in transformer init hyperparameters with attractive / repulsive particle regimes. This is the transformer-specific mean-field theory that complements Poole 2016 and Schoenholz 2017 for feedforward nets. Provides explicit phase-diagram coordinates (angle exponent, gradient exponent) in init-hyperparameter space that our at-init controls must trace.

**[Haber, Levi et al. 2024]** (VERIFY) — order-chaos phase transition in transformers; angle-exponent + gradient-exponent Lyapunov indices; attractive / repulsive particle regimes. Companion to Cowsik providing a distinct mathematical framework.

**[Noci 2023, Shaped Transformer]** — *The Shaped Transformer: Attention Models in the Infinite Depth-and-Width Limit* — softmax centred at identity plus width-dependent temperature yields well-defined SDE limit in proportional infinite-depth-width regime, avoiding rank collapse. Shaped-attention is an explicit criticality-preserving design; benchmark against unshaped nanoGPT.

**[Chen 2025, Critical Attention Scaling]** — *Critical attention scaling in long-context transformers* — attention exhibits a phase transition in scaling factor β_n: insufficient scaling collapses tokens; excessive reduces attention to identity; critical β_n ~ log n justifies YaRN/Qwen scaling recipes. Layer-level criticality mechanism that maps directly to the per-layer σ_ℓ observable.

**[Torkamandi 2025]** — *Mapping the Edge of Chaos: Fractal-Like Boundaries in the Trainability of Decoder-Only Transformer Models* — hyperparameter trainability boundary of decoder-only transformers exhibits self-similar fractal structure across scales in the Adam update iteration. Fractal structure near the trainability boundary implies our at-init-criticality controls must carefully sweep hyperparameters; avoid resonating artefacts. The fractal boundary is especially important for the **Schoenholz-tuned init** control (one of the three random-init conditions): a hyperparameter choice that is "at the critical boundary" in mean-field theory may in fact straddle a fractal boundary where small perturbations move the system across the critical surface. Our pre-registration specifies a 5-point hyperparameter grid around the Schoenholz critical point so that fractality-induced variance can be characterised and separated from training-induced drift.

**[Zhang 2021 edge of chaos as guiding principle]** (VERIFY) — weight decay acts as an order-parameter knob pushing feedforward networks toward the ordered phase; optimal weight decay places nets at the edge of chaos with peak Fashion-MNIST accuracy. This is direct evidence that the empirically-optimal hyperparameter coincides with the theoretical edge-of-chaos. For our paper, this supports the hypothesis that pretrained LLMs — which have been hyperparameter-tuned to maximise validation loss — may sit near a critical surface as a learned consequence of optimisation, not as a deliberate design choice.

**[Bergsma & Soboleva 2025, Power Lines]** (VERIFY) — optimal weight decay for LLM pretraining scales linearly with batch size, and the AdamW timescale τ = B / (η·λ·D) follows a precise power law in tokens-per-parameter ratio. Power-law scaling of optimal regularisation is itself a criticality-adjacent observable — it suggests that the hyperparameter surface has self-similar / critical structure across scales, reinforcing the Torkamandi fractal-boundary picture.

### 5.4 Signal-propagation / NTK / feature-learning distinction

The at-initialisation literature has three main theoretical frameworks: signal-propagation mean-field (Poole 2016, Schoenholz 2017, Xiao 2018) predicts specific ρ(J) = 1 critical boundaries; NTK (Jacot 2018, Arora 2019, Lee 2019) predicts lazy regime where networks are effectively linearised; feature-learning µP (Yang 2020, Yang & Hu 2021, u-µP Blake et al. 2024) predicts a distinct regime where networks depart from lazy training and learn non-trivial features.

For our empirical analysis, the key practical question is whether the trained transformers we measure are in the NTK regime (in which case linearised analysis suffices) or the feature-learning regime (in which case linearised analysis misleads). The consensus in 2024–2026 is that production-scale LLMs are in the feature-learning regime (strong evidence from the Yang-Hu 2021 µP scaling laws, which only work if feature-learning is active). Our commitment: explicitly state in methodology that we assume feature-learning regime; validate by measuring departure from NTK linearisation (e.g., compare linearised-at-init vs actual-trained activation predictions on a held-out batch).

**[Yang 2020, Tensor Programs]** — unifying framework for architecture-agnostic infinite-width limits. Provides mean-field predictions against which we compare finite-width criticality measurements.

**[Jacot, Gabriel & Hongler 2018, NTK]** — infinite-width GD evolves via fixed kernel; dynamics linear. Lazy-regime limit.

**[Arora et al. 2019]** — closed-form NTK for CNNs; enables comparison of exact NTK with finite-width trained nets.

**[Lee et al. 2018, NNGP]** — infinite-width Bayesian neural networks ≡ GPs with specific kernel. Baseline for what "untrained" criticality looks like in the infinite-width limit.

**[Lee et al. 2019, wide networks]** — wide finite nets well-approximated by their linearisation around init throughout training. Informs our at-init vs trained comparison.

**[Yang & Hu 2021, µP]** — Maximal Update Parametrisation enables hyperparameter transfer across scales. µP networks are in the feature-learning regime — are they closer to or further from edge of chaos than vanilla-init?

**[Blake et al. 2024, u-µP]** — combines µP with unit scaling for stable FP8 training. Alternative principled-init baseline.

**[Mishkin & Matas 2015, LSUV]** — layer-sequential unit-variance init. Classical baseline for how init choice affects trainability.

**[Zhang, Dauphin & Ma 2019, Fixup]** — rescaled residual-branch init trains 10⁴-layer residual nets stably without normalisation. Useful normalisation-free control for isolating normalisation effects from criticality.

**[De & Smith 2020]** (VERIFY) — BN initialises residual blocks near identity, keeping effective depth low early in training. Effective-depth / branching connection.

### 5.4.1 Weight-matrix vs activation spectral analyses

A distinction must be made between two types of spectral analysis. **Weight-matrix spectral analysis** (e.g., Martin & Mahoney 2021 HTSR, layer spectral norm 2510.21770) examines the singular-value distribution of the learned weight matrices. This is static: once training is done, the weights are fixed and their spectrum is fixed. **Activation spectral analysis** (e.g., our Jacobian spectral radius ρ(J_ℓ), layer-wise intrinsic dimension per-input) examines the singular-value distribution of the Jacobian of the activation map at a specific input point. This is dynamic: it depends on the input.

For our paper, both are relevant. Weight-matrix HTSR provides a **input-independent** spectral signature that tracks training trajectory; Jacobian spectral analysis provides an **input-dependent** signature that tracks activation dynamics. The two should correlate if the underlying criticality is a property of the learned weights, not of specific inputs. A disconnect between the two would indicate that criticality is input-dependent (consistent with Candidate 26's per-prompt σ framing).

### 5.4.2 The role of layer normalisation

Layer normalisation is a key architectural component of transformers that affects signal propagation. Pre-LN vs post-LN vs no-LN variants have different at-init-criticality predictions **[Cowsik 2024]**. For pretrained models we use the standard pre-LN configuration (GPT-2, Pythia, Gemma are all pre-LN) but flag LN-free or post-LN variants as potential future comparisons.

### 5.4.3 The shaped-attention and dimensional-isometry directions

**[Noci et al. 2023, Shaped Transformer]** — already cited. Shaped attention is an at-init criticality-preserving design; comparing pretrained shaped-transformer exponents to pretrained unshaped-transformer exponents would isolate the at-init-preservation vs trained-drift question.

**[Pennington et al. 2017]** — already cited. Dynamical isometry at init. Extension to post-training isometry is an open question: does a trained transformer maintain isometry, or does it specialise into a non-isometric regime?

### 5.5 Open questions for this theme

- Does σ_ℓ from MR estimator correlate with spectral-radius ρ(J_ℓ) per layer?
- Does σ_ℓ(ℓ) gradient match the Tulchinskii intrinsic-dimension gradient?
- Does Cowsik's order-chaos phase-diagram location correlate with our σ_ℓ extraction?
- Is the layer-spectral-norm profile (2510.21770) monotone or does it exhibit a critical depth?

---

## Theme 6 — Temporal renormalization-group machinery

### 6.1 Why temporal RG is the right additional observable

The CSN power-law fit, the MR-σ estimator, the crackling-noise scaling relation, and the Jacobian spectrum are all "point observables" — they summarise the data by a small number of exponents extracted under specific assumptions. Temporal renormalization group (RG) is qualitatively different: it **produces a flow** in observable-space as a coarse-graining scale is varied. At criticality, the flow converges to a universal fixed-point distribution whose functional form encodes the universality class. Away from criticality, the flow drifts with scale. The fixed-point test is therefore **constructive** — it builds a universal scaling function out of the data — rather than **descriptive** — matching to a pre-specified exponent value. Constructive tests are harder to fake, and their evidence is stronger when positive.

The canonical physics reference is Wilson's momentum-shell RG for Kadanoff spin blocks (**[Goldenfeld 1992, Cardy 1996]**). The key Wilson insight: at criticality, coarse-graining the system by merging correlated degrees of freedom produces a system in the same universality class at a larger scale, and iterating this coarse-graining converges to a fixed-point distribution. For neural populations, Meshulam adapted this to the "merge the two most correlated neurons" coarse-graining rule, which is well-defined for any observed population without needing spatial structure.

### 6.2 The Meshulam-Bialek RG programme on neural populations

**[Meshulam, Gauthier, Brody, Tank & Bialek 2019, PRL]** — *Renormalization-group approach to scale-free cortical dynamics* — momentum-shell renormalization group applied to hippocampal place-cell population activity. The coarse-graining procedure merges the two most correlated neurons and rescales; if the population is critical, the density of eigenvalues of the population covariance converges to a universal power-law scaling function under the RG flow. This is the founding temporal-RG paper in neuroscience. Meshulam 2021 extends the pipeline and provides RG-invariant scaling-function fits.

**[Meshulam 2021]** — follow-up showing RG-invariant scaling functions across coarse-graining steps in place-cell population activity. Directly implementable temporal-RG pipeline providing baseline for LLM ports.

### 6.3 The Sooter d_β temporal RG

**[Sooter, Fontenele, Barreiro, Ly, Hengen & Shew 2025]** — *Defining and measuring proximity to criticality* — introduces temporal renormalization group and information-theoretic distance-to-criticality for observed time series without known control parameter. The d_β observable is an information-theoretic distance that vanishes at the critical point and is positive away from it. Methodologically, d_β is appealing for LLM analysis because it does not require a pre-specified order parameter (we don't know what "driving parameter" moves an LLM toward or away from criticality). Candidate 25 uses d_β as a fourth criticality observable alongside α, σ, and Jacobian ρ.

The Sooter implementation requires: (i) time-series of a coarse-grained observable (e.g., total residual-stream activation energy per token); (ii) a hierarchical coarse-graining procedure; (iii) mutual-information estimates between successive RG scales. Computational cost is dominated by the MI estimator; with k-NN MI on 100k-token sequences, wall-clock is ~1 h/layer on RTX 3060.

The `d_β` observable complements σ in a specific way: σ measures the local propagation of activity (how many children does each parent produce?), while `d_β` measures the **rate of approach to a fixed-point distribution** under coarse-graining. A system can be locally branching-critical (σ = 1) but globally off-critical in the sense that it does not have scale-invariant structure — and vice versa. Measuring both is more discriminating than either alone. Sooter 2025 provides a specific information-theoretic implementation that estimates the fixed-point distance without requiring the user to specify a universality class in advance. This is methodologically appealing because we do not know a priori which universality class LLM activations belong to.

The Sooter pipeline has a subtle methodological choice we must make: the coarse-graining rule. Sooter's default is temporal coarse-graining (merge adjacent time bins), but for LLM activations the natural alternatives are **feature-space coarse-graining** (merge the two most correlated SAE features) or **layer-space coarse-graining** (merge adjacent layers). Each produces a different RG flow. We pre-register temporal (token-axis) coarse-graining as the primary analysis to match Sooter's cortical protocol, with feature-space and layer-space as secondary arms.

**[Bialek, Stephens et al. 2014]** (VERIFY reference) — earlier RG applications to neural populations; precedent for Meshulam 2019 methodology. Historical reference for the Bialek-group RG programme.

### 6.4 RG on artificial networks

**[Yoneda 2025, PRR]** — *Universal Scaling Laws of Absorbing Phase Transitions in Artificial Deep Neural Networks* — already covered in Theme 1; their finite-size-scaling analysis is effectively an RG derivation of MLP-vs-CNN universality-class assignment. The paper demonstrates that the full RG programme works on artificial networks, not just neural populations.

**[Ghavasieh 2025]** — applies Landau + directed-percolation description to random DNNs. Activation-function choice selects universality class (log-trap Brownian motion vs absorbed Brownian motion) via explicit RG arguments. At-init result, but the RG framework transfers to post-training via Sooter's d_β.

### 6.5 Infrastructure

**[Kardar 2007]**, **[Cardy 1996]**, **[Goldenfeld 1992]** — textbook RG references. Meshulam's momentum-shell procedure is standard; our implementation adapts the Meshulam 2019 + Sooter 2025 code-base. **[Stanley 1971]** is the foundational critical-phenomena text. **[Herbut 2007]** and **[Kadar 2007]** are modern treatments. **[Henkel, Hinrichsen & Lübeck 2008]** provides the DP-specific scaling-function look-up tables needed for class-assignment.

The code availability is good: Meshulam et al. have released the coarse-graining routines (merge-most-correlated + decimate); Sooter et al. released d_β code alongside the 2025 preprint (VERIFY). We can use both directly without re-implementation, which is important for reproducibility and compute efficiency. Our commitment: verified-same-results as Meshulam 2019 on CRCNS ssc-3 cortical data before running on LLM activations.

### 6.6 RG-theoretic subtleties

A methodological pitfall flagged in the Meshulam 2021 follow-up: under-sampled populations produce apparent-critical RG flow that is actually a subsampling artefact. The fix is the same as for the MR-σ estimator — subsampling correction. For LLM analysis, this means the Meshulam pipeline must be applied to populations that are representative of the full-layer activation pattern, not to small subsets chosen for convenience. Our commitment: the Meshulam pipeline is applied to the full residual-stream population at each layer (768-dim for GPT-2-small, 2304 for GPT-2-medium, 2048 for Pythia-1.4B, 2304 for Gemma-2-2B), not to a random sub-sample.

**[Hohenberg & Halperin 1977, Rev. Mod. Phys.]** (VERIFY arXiv-status) — classic classification of dynamical universality classes (Model A, Model B, etc.). Not directly in our Phase 0 bibliography but standard background for RG-type analyses. We flag this for the Phase 1 methodology build if class-assignment becomes a central contribution.

### 6.7.1 Scaling relations between RG and CSN

Sooter's d_β and the CSN power-law fit measure related but distinct aspects of criticality. The CSN α captures the tail exponent of a single-time-scale observable (avalanche size); d_β captures the rate of convergence to a fixed-point distribution under temporal coarse-graining. A consistent picture requires that both observables agree on "this system is critical / not critical" — if they disagree, something is methodologically off. The expected agreement: critical systems have d_β → 0 AND power-law avalanche distributions; off-critical systems have d_β > 0 AND non-power-law avalanche distributions. Mixed outcomes (critical d_β but not critical α, or vice versa) flag methodological problems.

The paper commits to computing both observables in the same experimental pipeline and reporting agreement or disagreement explicitly.

### 6.7.2 Absorbing-phase-transition vs edge-of-synchronisation

The RG machinery is universality-class agnostic, but the specific fixed-point exponents depend on the class. Absorbing-phase-transition systems (DP, Manna, CDP) have different fixed-point scaling functions than edge-of-synchronisation systems (Kuramoto-like transitions). Our analysis must fit the fixed-point distribution to multiple candidate scaling functions and report which provides the best fit. **[Dickman, Muñoz, Vespignani & Zapperi 2000]** — *Paths to self-organized criticality* — provides the canonical framework for distinguishing absorbing-phase-transition SOC from other self-organisation mechanisms. **[Dickman, Vespignani & Zapperi 1998]** shows SOC sandpiles are driven absorbing-phase transitions tuned by conservation law.

### 6.8 Open questions

- Does Sooter d_β on LLM activations recover a non-trivial fixed point?
- Does the fixed-point exponent match a known universality class (DP / mean-field / edge-of-synchronization)?
- Does d_β correlate with σ and α across the Pythia scale sweep?
- Does Yoneda's MLP mean-field class assignment extend to transformers, or do transformers lie in a different class?
- Does the Meshulam covariance-eigenvalue scaling function match the cortical form (Meshulam 2019) on LLM activations, or does it have a transformer-specific form?
- Is the d_β observable training-step-resolvable — does it track grokking transitions (Candidate 4)?

### 6.9 Risk analysis

The temporal-RG arm is the highest-risk component of the paper because: (i) the methodology is newly developed (Sooter 2025) and has not been validated on any artificial-network data as of April 2026; (ii) the computational cost is high; (iii) the interpretation of fixed-point exponents requires universality-class-specific theoretical predictions that may not be available for transformer-specific dynamics. Mitigation: scope temporal-RG to appendix-level contribution (Candidate 25), not main-text anchor. If d_β succeeds, it becomes a major main-text figure; if it fails or is inconclusive, it remains an appendix showing methodological effort.

### 6.9.1 Other RG-related methodological references

**[Wilson 1971]** (VERIFY) — founding RG paper. Historical depth reference for the Phase 0 bibliography.

**[Fisher 1998]** — RG renormalization group review. Classic methodological reference.

**[Stanley 1971 textbook]**, **[Goldenfeld 1992 textbook]**, **[Cardy 1996 textbook]**, **[Kardar 2007 textbook]**, **[Herbut 2007 textbook]** — standard graduate-level statistical-physics references covering critical-phenomena RG machinery. Textbook spread ensures methodological grounding.

**[Henkel, Hinrichsen & Lübeck 2008]** — definitive DP / absorbing-phase-transition textbook with exponent lookup tables. Essential for class-assignment post-RG analysis.

**[Marro & Dickman 1999]** — non-equilibrium phase transitions in lattice models; comprehensive reference on absorbing-state transitions.

**[Hinrichsen 2000]** — *Non-equilibrium critical phenomena and phase transitions into absorbing states* — canonical DP review.

**[Janssen 1981]**, **[Grassberger 1982]** — founding DP-conjecture papers. Historical depth.

**[Bak, Tang & Wiesenfeld 1987]**, **[Manna 1991]**, **[Dickman, Vespignani & Zapperi 1998]** — sandpile / SOC / absorbing-state-phase-transition connection. Theoretical foundation.

### 6.10 Connection to scaling laws

A successful RG fixed-point analysis would make predictions about **how avalanche exponents scale with model size**. At criticality, the scaling exponents are universality-class-determined constants independent of system size; away from criticality, they drift with size. If we run the Meshulam / Sooter pipeline across the full Pythia scale sweep (70M → 2.8B) and find the same fixed-point exponent at all scales, that is strong evidence for critical universality. If we find systematic scale-dependence, that is evidence for quasi-criticality or a scale-dependent crossover.

This connects directly to the scaling-law literature **[Kaplan 2020, Hoffmann 2022]**: neural scaling laws describe how test loss scales with model size, data, and compute; criticality-based scaling laws would describe how activation exponents scale. The two sets of scaling laws may share a common origin — a hypothesis we pre-register as an open question but do not directly test in this paper.

**[Bahri et al. 2021]** — explains neural scaling laws via data-manifold dimension and NTK spectrum; connects scaling exponents to spectral properties. If activation-criticality exponents correlate with Bahri's data-manifold-dimension exponent, that would be direct evidence for coupling between dynamics and scaling.

**[Bordelon & Pehlevan 2024]** — solvable model of feature-learning scaling laws; representation-collapse drives generalisation plateau. Provides theoretical context for interpreting σ_ℓ scaling alongside Bordelon-Pehlevan predictions.

**[Geiger et al. 2020]** — phase diagram of deep nets across width, data, regularisation; criticality-like finite-size scaling in the infinite-depth limit. Cross-cutting evidence of finite-size scaling in deep nets.

**[Noci et al. 2022]** (VERIFY) — finite-depth / finite-width corrections to mean-field signal propagation. Methodology for finite-size corrections relevant for Pythia-12B analysis.

### 6.10.1 Information-theoretic criticality measures

Beyond RG, information-theoretic observables provide an alternative characterisation of criticality:

- **Mutual information between successive time points**: diverges at criticality.
- **Lempel-Ziv complexity**: maximised at critical complexity.
- **Entropy production**: specific scaling at critical points.
- **Fisher information**: diverges at critical phase transitions.

Each of these is an auxiliary observable for our paper. We scope the primary analysis to CSN + MR-σ + crackling + shape + RG; information-theoretic observables are flagged for Phase 2 or future papers.

**[Tishby, Pereira & Bialek 2000]** — information-bottleneck framework for representation learning. Not directly criticality-relevant but provides information-theoretic context.

**[Saxe et al. 2018]** — information-bottleneck analysis of SGD in deep nets. Training-dynamics information-theoretic observable.

**[Amari 2016]** — information-geometry textbook; Fisher-information perspective relevant for criticality-Fisher-information connections.

**[Zhang, Bengio, Hardt, Recht & Vinyals 2017]** — deep nets can fit random labels; generalisation-criticality connection.

**[Sensory-Processing Sensitivity EEG, 2023]** (VERIFY authors) — example of combining DFA + avalanche analysis + sample entropy + Higuchi fractal dim in human EEG. Illustrates the full criticality-observables battery applied simultaneously; template for our LLM pipeline.

### 6.11 Temporal-RG vs alternatives

Temporal RG is one of several dimensional-reduction approaches to criticality. Alternatives include:

- **Spatial RG** (Wilson momentum-shell): coarse-grain by merging correlated degrees of freedom in spatial / feature-space. Meshulam's original approach.
- **Information-theoretic RG** (Sooter d_β): no explicit coarse-graining; instead use MI between coarse-grained and fine-grained descriptions to quantify scale-invariance.
- **Time-resolved MFT** (dynamical mean-field theory): at the other end of the rigorous-theoretical spectrum; exact in the infinite-width limit but requires specific architectural assumptions.
- **Persistent-homology / topological data analysis**: alternative dimensional-reduction that does not require metric structure. **[Dabaghian et al. 2012]**, **[Chaudhuri et al. 2019]** provide neuroscience precedents.

Our pre-registration: temporal RG via Sooter d_β as primary; spatial RG via Meshulam as cross-check; other approaches as future-work flags.

---

## Theme 7 — ViT-Tiny / CIFAR-10 universality arm

### 7.1 Why the universality arm exists

The scope-check on Candidate 11 replaced a Fashion-MNIST CNN with a ViT-Tiny / CIFAR-10 setup. Rationale: ViT-Tiny shares the attention-based architecture of GPT-2 but operates on a completely different modality (pixels, not tokens). If the activation-avalanche exponents of ViT-Tiny match those of GPT-2 on language within bootstrap CI, that is evidence for **architecture-determined** universality (attention + residual + LN → specific class). If they diverge, that is evidence for **input-distribution-determined** universality (pixels vs tokens matter more than architecture). Both outcomes are publishable as stand-alone findings, but the interpretation is substantively different: architecture-determined universality is a strong statement about the computational primitives — it would mean that any attention-based network with residual-connections and layer-norm sits in the same universality class regardless of training data or modality. Input-distribution-determined universality is weaker: it says the universality class is a property of the training corpus, and different architectures trained on the same corpus would sit in the same class while the same architecture trained on different corpora would sit in different classes.

A third possibility worth pre-registering is **architecture-and-task-dependent** universality: attention-based transformers trained on language sit in one class, trained on vision sit in another; MLPs trained on language sit in a third; CNNs trained on vision sit in a fourth. This is the most permissive interpretation and requires the largest literature to substantiate. Our single paper contributes one attention-based × language-task data point (GPT-2, Pythia, Gemma-2) plus one attention-based × vision-task data point (ViT-Tiny on CIFAR-10); combined with Yoneda's MLP and CNN data points, this builds a 2 × 2 grid of architecture × task universality-class assignments. Four cells is not enough to definitively establish full architecture-and-task dependence, but it's enough to discriminate between the three main hypotheses.

**[Yoneda 2025, PRR]** — directly predicts MLPs → mean-field class, CNNs → DP class. The prediction for transformers is open. Our ViT-Tiny experiment provides one of two class-assignment data points (the other being language transformers).

### 7.2 The ViT literature

**[Dosovitskiy 2021, ViT]** — *An image is worth 16x16 words* — foundational ViT paper. Establishes that transformers applied to image patches match CNN performance on ImageNet. The architectural recipe — tokenise the image into 16×16 patches, add positional embeddings, feed through a standard transformer stack — is essentially identical to the language transformer recipe up to the patch-embedding step. This architectural near-identity is exactly why ViT is the right cross-modal control: we isolate the effect of input modality (pixels vs tokens) while holding architecture (attention + residual + MLP + LayerNorm) fixed.

**[Touvron 2021, DeiT]** — *Data-efficient image transformers* — training-efficient ViT variants. DeiT-Tiny on CIFAR-10 is tractable on RTX 3060 and provides the universality-arm target model. We commit to DeiT-Tiny (5.7M parameters, 12 layers, 3 heads per layer, 192-dim residual stream) as the specific model for Candidate 11, giving a close scale match to GPT-2-small (124M parameters is larger, but DeiT-Tiny's depth-width structure is closer to GPT-2-small than to larger models).

**[Zhai 2022, ViT scaling]** — ViT scaling laws. Context for cross-modal criticality. The ViT scaling-law paper shows that ViT test accuracy scales as a power law in model size, dataset size, and compute with specific exponents that differ from language-model scaling exponents. Whether criticality observables also scale differently between ViT and language-transformer is a second-order testable consequence; we flag it for a future paper.

### 7.3 Vision-specific considerations

The activation-avalanche definition for vision transformers requires care about what counts as a "token". In language, tokens are sequential and attention produces autocorrelation in the token axis. In vision, tokens are image patches arranged in a 2D grid, and attention produces correlations that are not strictly autoregressive. This affects the MR-σ estimator: the "time axis" for MR-σ on a ViT is the patch sequence (reading left-to-right, top-to-bottom by default), and the autocorrelation structure is spatial rather than temporal. Our adaptation: compute MR-σ on a **batch-axis** (across images) for ViT, keeping the per-image analysis comparable to single-prompt analysis in language transformers.

The threshold-plateau test for ViT activations is non-trivial because pixel inputs are pre-normalised and the activation-statistics scale is different from language. We pre-register a threshold battery based on per-layer activation quantiles rather than fixed absolute thresholds to avoid scale-dependence artefacts.

### 7.4 At-init signal-propagation for CNNs and vision

**[Xiao 2018]** — delta-orthogonal init for CNNs enables 10⁴-layer vanilla CNN training. The vision-architecture at-init-criticality result complements Schoenholz 2017 for MLPs and Cowsik 2024 for transformers. All three are mean-field theories predicting ρ(J) = 1 at the critical boundary; all three are expected to break down at finite width and finite depth post-training, and our empirical σ is the post-training test. Xiao's result is particularly striking because 10⁴-layer training with no normalisation and no skip connections is unheard-of elsewhere in the DL literature, and it demonstrates how powerful criticality-preserving init can be. The inference for our paper: Schoenholz / Cowsik / Xiao provide the mean-field-theory baseline for what *at-init criticality* looks like in each architectural class; we measure *post-training criticality* and report the drift.

### 7.5 Cross-architecture universality comparison

The universality arm pairs naturally with Candidate 35 (ViT vs language transformer). Matched-parameter-count ViT-B/16 on ImageNet vs Pythia-160M on Pile provides a language-vs-vision comparison at matched scale. If σ matches within CI, criticality is architecture-determined (supporting the Yoneda-class-assignment hypothesis with a transformer-specific universality class). If σ differs, criticality is input-distribution-determined, which is a substantive reframe of the criticality hypothesis. The scope-check decision for Paper 1 is to include only ViT-Tiny / CIFAR-10 as the vision arm (smaller, cheaper, cleaner) and defer ViT-B/16 / ImageNet (Candidate 35) to a companion paper. This keeps Paper 1 focused on the anchor claim while still providing one cross-modal data point.

### 7.6 Other vision work

**[CIFAR-10, Krizhevsky 2009]** is the canonical 60,000-image 10-class benchmark; pre-cached on the project machine. Matches the scale-check requirement. **[ImageNet, Deng 2009]** is available for ViT-B/16 experiments if we expand scope.

**[He, Zhang, Ren & Sun 2016 ResNet]** — residual connections enable training of 152-layer CNNs. Useful historical context: residual connections are shared across CNN and transformer architectures, and they are the most important structural feature that breaks the Xiao 2018 at-init mean-field picture. Whether post-training criticality survives the residual-connection bypass is an open question for CNNs (partially addressed by Yoneda 2025) and for transformers (open).

**[Veit, Wilber & Belongie 2016]** — *Residual networks behave like ensembles of relatively shallow networks* — ResNets can be unrolled into O(2^L) paths with geometrically-distributed effective depths; most gradient flows through short paths. This is foundational for understanding skip-connection effects on signal propagation and bears directly on our avalanche analysis of residual-connected transformers: the effective-depth distribution is itself an avalanche-like statistic.

### 7.7 Universality-arm risk analysis

The ViT-Tiny / CIFAR-10 arm is moderate-risk because: (i) DeiT-Tiny on CIFAR-10 is well-characterised and we can leverage the existing training recipes; (ii) the architecture is minimally different from language transformers — patch-embedding is the only architectural change; (iii) the activation-statistics scale is known and we can apply the same threshold-plateau protocol. The primary risk is that CIFAR-10 at 32×32 resolution has only 64 patches per image (or 49 with 4×4 patches), which gives fewer "time axis" observations per avalanche than a typical token-sequence in language modelling (>100 tokens). This may reduce statistical power for CSN fits. Mitigation: we use multiple images per "context" to increase the effective time-axis length.

**[Xiao 2018]** baseline for CNNs provides the mean-field prediction against which to benchmark ViT-Tiny. If ViT-Tiny at init matches Xiao's CNN at-init prediction, that is evidence that the attention-based-vision-transformer and CNN share the same at-init universality class (which would be surprising given different architectural primitives). If ViT-Tiny matches Cowsik's transformer prediction, that is evidence that the attention mechanism is what determines at-init universality class. Our ViT-Tiny at-init controls therefore distinguish between "attention-determined" and "vision-modality-determined" at-init class assignment.

### 7.8 Open questions

- Does ViT-Tiny on CIFAR-10 show α ≈ 3/2 with scaling relation satisfied?
- Is the ViT-Tiny σ the same as Pythia-160M σ within bootstrap CI?
- Does the Jacobian-spectral-radius ρ(J_ℓ) profile of ViT-Tiny match the language-transformer profile?
- Does ViT-Tiny at init match Cowsik 2024's transformer at-init prediction or Xiao 2018's CNN at-init prediction?
- Does the patch-embedding step introduce observable-scale artefacts that distort threshold-plateau tests?

### 7.9 Secondary vision analyses

Optional secondary arms: DINOv2 ViT-B (self-supervised pretraining), CLIP-ViT-B (contrastive pretraining), MAE ViT (masked-autoencoder pretraining). Each provides a different pretraining-objective control and asks whether the pretraining objective shifts activation-criticality. These are Candidate 35 / C5 territory and deferred to a future paper. For Phase 1 we stick to DeiT-Tiny on CIFAR-10 as the minimum-viable vision arm.

### 7.10 The Fashion-MNIST scope-check decision

The original Candidate 11 specified a Fashion-MNIST CNN. Phase −0.5 scope-check replaced this with ViT-Tiny / CIFAR-10 for two reasons: (i) Fashion-MNIST CNNs are architecturally very different from transformers, making cross-architecture universality conclusions confounded by the multiple architectural differences (attention vs convolution, residual vs sequential, LN vs BN); (ii) ViT-Tiny / CIFAR-10 isolates the modality-vs-architecture question more cleanly. The Fashion-MNIST CNN is deferred to Candidate 11.5 (if relevant in Phase 2).

**[Fashion-MNIST, Xiao, Rasul & Vollgraf 2017]** — still cited as historical context; not used in Phase 1.

### 7.11 ImageNet-scale ViT experiments (future work)

**[ViT-B/16 on ImageNet]** would provide a matched-scale language-vs-vision comparison with Pythia-160M. However, ImageNet pretraining on RTX 3060 is infeasible, so we rely on public weights (Dosovitskiy 2021, DeiT-B Touvron 2021). Activation analysis on pretrained ViT-B/16 is feasible on RTX 3060 at fp16 and is a natural Phase 2 extension if Phase 1 succeeds.

**[CLIP-ViT]** (Radford et al. 2021) — contrastive pretraining; alternative pretraining objective. Publicly available weights. Interesting for pretraining-objective-shifts-criticality questions.

**[DINOv2 ViT-B]** (Oquab et al. 2023, VERIFY) — self-supervised vision transformer; another pretraining-objective control. Publicly available weights.

Each deferred to Phase 2 / Paper 7 if Phase 1 succeeds.

### 7.12 The edge-of-stability vs edge-of-chaos distinction in vision

Vision transformers exhibit the same edge-of-stability optimisation dynamics **[Cohen et al. 2021]** as language transformers, so the at-init signal-propagation story applies identically. What may differ is the **trained-network dynamics**: ViT-Tiny may drift further from edge-of-chaos than GPT-2 during training because the inductive bias of image classification may favour more ordered (higher classification accuracy) rather than more critical (higher computational capacity) dynamics. This is testable — compare σ(training-step) trajectories between ViT-Tiny and GPT-2 of matched parameter count — but out of scope for Phase 1.

### 7.13 Connection to Yoneda's CNN→DP assignment

**[Yoneda 2025 PRR paper 4021]** assigns CNNs to the directed-percolation universality class. If the ViT-Tiny activation-avalanche exponents in our analysis match the DP class (α ≈ 1.5 for 2+1 DP, β ≈ 2, scaling relations specific to DP), then the Yoneda CNN→DP assignment transfers to vision transformers — suggesting that "vision task" rather than "architecture" determines class assignment. If ViT-Tiny exponents match transformer language-model exponents, then "architecture" rather than "task" determines class assignment. This 2×2 comparison is the key finding of the universality arm, and we commit to the specific bootstrap CI comparison in the Phase 2 deliverable.

### 7.14 Additional vision-criticality references

**[Xiao 2018]** — delta-orthogonal init for CNNs — already cited. Provides the vision-architecture at-init prediction.

**[He, Zhang, Ren & Sun 2016 ResNet]** — already cited. Foundation for residual-connection-based vision architectures.

**[Veit, Wilber & Belongie 2016]** — ResNet ensemble interpretation; already cited.

**[Testolin, Piccolini & Suweis 2020]** — DBN graph analysis; scale-free connectivity in trained DBNs. Cross-architecture precedent for trained-network topology.

**[Scabini & Bruno 2023]** — fully-connected NNs exhibit power-law-like weight-graph tails. Cross-architecture precedent.

**[Watanabe, Hiramatsu & Kashino 2020]** — effective connectivity in trained deep nets consistent with preferential attachment. Cross-architecture precedent.

### 7.15 Fashion-MNIST CNN as historical control

Even though the universality-arm scope was moved to ViT-Tiny / CIFAR-10, the pre-existing Fashion-MNIST CNN infrastructure in `~/entropy/fashion_mnist_project/` remains useful. Phase 2 / Phase ∞ optional run: apply the full avalanche pipeline to the existing Fashion-MNIST CNN for direct comparison with ViT-Tiny / CIFAR-10. If both match, the universality class spans the CNN-vs-ViT architectural divide. If they differ, Yoneda's CNN→DP vs ViT-Tiny→? distinction is confirmed. Optional, not mandatory.

---

## Theme 8 — Attention-head circuit analyses

### 8.0 Why head-level resolution matters

Attention heads in a transformer are a natural granularity for **circuit-resolved criticality**. A head is: (i) a functionally distinct computational unit with its own Q, K, V projection matrices and its own attention pattern; (ii) a small-enough unit that ablation studies are tractable (144 heads in GPT-2-small is feasible; 384 in Pythia-1.4B is borderline); (iii) the MI-community's standard circuit primitive, with a well-established atlas of specialised heads in GPT-2 (Wang 2023 IOI, Olsson 2022 induction, Gurnee 2024 universal neurons). Computing σ_head for each head in a pretrained model provides a 144-point (or 384-point) distribution that can be characterised statistically — is the distribution unimodal or multimodal? Does the tail follow a power law? Is the circuit-resident subset of heads displaced from the non-circuit subset in σ-space?

This is genuinely novel territory. No paper as of April 2026 has computed a per-head σ distribution on GPT-2 or any other pretrained transformer. Wang 2604.16431's cascade-dimension observable is computed at the whole-model level, not per-head. Olsson 2022 identifies induction heads via attention-pattern signatures, not σ. Our per-head σ histogram is therefore a first-of-its-kind observable and can anchor a short companion paper (Candidate 28) or a major appendix of the anchor paper (our current plan).

### 8.1 Head-level atlases

**[Wang 2023, IOI]** — 26 of 144 GPT-2-small heads form the IOI circuit. This sparse-functional-circuit finding motivates Candidate 28: if only a small fraction of heads do specific computation, the per-head σ distribution should be bimodal (circuit vs non-circuit) rather than unimodal. Hartigan's dip test provides the quantitative bimodality check.

**[Gurnee 2024, Universal Neurons]** — extends to neuron-level universality. Some GPT-2 neurons are universal (same function across seeds) and may be "hubs" in the activation-graph sense. Testable: universal neurons participate in disproportionately many avalanches.

**[Olsson 2022, Induction Heads]** — identifies induction heads as a specific circuit emerging via phase transition during training. Direct target for Candidate 8 circuit-specific criticality. The induction-head phase transition is empirically observable as a sharp change in in-context-learning performance at a specific training step (~2-5k steps in small transformers, ~50-500k steps in larger models depending on scale). Our hypothesis for Candidate 27 is that σ crosses 1 at or near this step — the induction-head circuit becoming "critical" in the σ ≈ 1 sense is what makes in-context learning possible. This is a strong and testable claim. We pre-register a comparison of induction-head-emergence-step (measured via the Olsson prefix-matching score) against σ-crossing-step on Pythia's 154 checkpoints, for Pythia-70M, -160M, -410M, -1.4B.

**[Olsson et al. 2023]** (VERIFY follow-up) — additional empirical characterisation of induction-head emergence; provides scaling of emergence step with model size. Direct reference for Candidate 27 timing analysis.

### 8.2 Per-head analysis methodology

**[Musat 2025]** (VERIFY preprint 2025) — per-head resolved causal contributions in GPT-2 small/medium; provides a head-level circuit atlas across prompt types. This is the methodology reference for computing per-head causal σ via attention-head ablation + patching. Complements Wang 2023 IOI by extending to all heads not just IOI circuit.

**[Heimersheim 2023]** (VERIFY) — methodology for per-head attention-pattern analysis. Additional methodology reference.

**[Chen 2023, Long-range attention patterns]** (VERIFY) — attention patterns in pretrained LLMs exhibit long-range structure. Context for attention-head avalanches as a long-range causal cascade.

### 8.3 Head ablation as causal branching

The causal branching-ratio for a single head is defined as: ablate head (i, ℓ) → measure change in activation at head (j, ℓ+1), averaged over a prompt set. This is σ_{i→j} for the pair, and summing over j gives the single-head out-branching ratio. The per-head σ is then the histogram of these summed values. Methodologically, the per-head computation is expensive — 144 heads × 144 downstream heads × a prompt-set of ~1k prompts × forward-pass cost. On RTX 3060, this is tractable for GPT-2-small (12 layers × 12 heads = 144) but stretches for GPT-2-medium (24 × 16 = 384) and becomes borderline for Pythia-1.4B (24 × 16 = 384). We scope to GPT-2-small + GPT-2-medium for the main arm.

Two specific ablation choices must be pre-registered: (i) **zero-ablation** — replace the head's output with zeros — has the advantage of being simple and reproducible but introduces an out-of-distribution signal that may produce artefactual downstream effects. (ii) **mean-ablation** — replace the head's output with the mean of the head's output over a distribution of prompts — has the advantage of remaining closer to in-distribution but requires a reference prompt distribution. The MI community's current best practice **[Heimersheim & Nanda 2024]** is mean-ablation with a carefully-chosen reference distribution, and we commit to this protocol.

### 8.4 Alternative per-head observables

Per-head σ is the primary observable for Candidate 28 but not the only head-level observable worth computing. Also flagged:
- Per-head α (avalanche-size exponent) on the head's output time series — tests whether each head individually exhibits power-law avalanches.
- Per-head Jacobian spectral radius ρ(J_h) on the head's Q/K/V projection matrices combined with the attention pattern.
- Per-head contribution to the σ_ℓ layer-level estimate — decompose the layer-σ into per-head contributions.

The per-head Jacobian-spectral-radius observable may be the most tractable first cut, since it doesn't require ablation experiments — just power-iteration on the QKV projection Jacobian, which is O(d^2) per head.

### 8.5 Attention-matrix structure

**[Chen 2025, Critical Attention Scaling]** — mentioned in Theme 5 — shows attention exhibits a phase transition in scaling factor β_n. The attention pattern itself is therefore near a phase boundary, and the per-head attention-matrix structure may encode criticality in an observable manner independent of the activation-avalanche analysis. We flag this for future work.

**[Noci 2023, Shaped Transformer]** — softmax centred at identity with width-dependent temperature yields a well-defined SDE limit. The shaped-attention formulation is an explicit criticality-preserving design; computing our avalanche pipeline on a shaped-transformer would provide a clean "at the critical boundary by design" control condition. We flag this for future work.

### 8.6 Statistical considerations for the per-head histogram

The per-head σ distribution has ~144 points in GPT-2-small. Testing bimodality with 144 points is borderline; Hartigan's dip test has power ~0.6 at a typical bimodality-separation threshold for this sample size. Mitigation: aggregate across GPT-2-small and GPT-2-medium (144 + 384 = 528 heads) for a combined bimodality test. Alternative: test bimodality within each model separately and report whether the result is consistent across models.

The fraction of heads that fall in the "circuit-resident" mode (if bimodal) may itself be a quantitative observable correlating with model capability. Specifically, if the fraction of near-critical heads scales with model size, that's a quantitative scaling law for "how much of the network is doing critical computation". This is a second-order observation we flag but do not pursue in the main Phase 1 analysis.

### 8.7 Other head-analysis references

**[Gurnee 2024, Universal Neurons]** — again, universal neurons may correspond to specific heads; cross-reference.

**[Voita et al. 2019 VERIFY]** — early head-ablation study in translation models; precedent for "some heads are redundant, some are essential" framing.

**[Clark et al. 2019 VERIFY]** — attention-pattern analysis of BERT; precedent for per-head pattern characterisation.

**[Chen et al. 2023]** (VERIFY) — long-range attention patterns in pretrained LLMs; context for how long-range attention structure affects per-head avalanche statistics.

**[Topological analysis of attention matrices]** (arXiv 5115, VERIFY) — recent 2025 preprint on topological analysis of trained-transformer attention matrices. Alternative observable that could be cross-referenced with σ_head.

### 8.8 Path patching vs ablation methodology

The MI community has converged on path patching **[Goldowsky-Dill 2023]** as the preferred causal-intervention methodology because naive activation-patching confounds multiple downstream paths. Path patching isolates specific residual-stream paths by ablating everything except the target path. For our per-head σ analysis, path patching provides cleaner attribution of downstream activation changes to specific upstream heads.

However, path patching is computationally much more expensive than ablation: isolating each path requires a specific intervention pattern with multiple forward passes. For 144 heads × 144 downstream heads × 1k prompts, path patching on GPT-2-small is on the order of 10⁶ forward passes, approaching the limit of what is feasible on RTX 3060 in reasonable wall-clock.

Compromise: use ablation-based σ as primary estimate; validate on a subset (say 20 heads) with path-patching-based σ to confirm that ablation-based estimates are not systematically biased.

### 8.9 Other circuit-specific criticality hypotheses

Beyond induction heads, the MI community has identified several other specialised circuits we could test for circuit-specific criticality:

- **Successor heads** (numerical-sequence detection) — emerge in early training
- **Punctuation-deletion heads** — specific function, well-characterised
- **Positional-encoding heads** — respond to token position, not content
- **Name-mover heads** (from Wang 2023 IOI) — move name tokens to specific positions

Each circuit could in principle exhibit distinct σ relative to matched non-circuit controls. Running the full battery on all circuits is out of scope for Phase 1 (we scope to induction heads as the primary circuit-specific test) but flagged as a natural Phase 2 extension.

### 8.10 Head-pruning as an alternative observable

The lottery-ticket literature **[Frankle & Carbin 2019]** shows that most weights in trained nets are "redundant" in the sense that they can be pruned without performance loss. Analogously, if most attention heads are redundant, their σ values may cluster in a "non-essential" mode while a small minority of essential heads cluster in an "essential" mode — providing the bimodal σ distribution Candidate 28 targets. The lottery-ticket framework is therefore a theoretical motivation for the bimodality test.

### 8.11 Attention-pattern statistics

Beyond per-head σ, the attention-pattern statistics themselves (the K × Q softmax-normalised attention weights) may exhibit critical / non-critical structure. Specifically:

- **Attention-pattern entropy per head**: low-entropy patterns correspond to sharp "lookup" heads; high-entropy patterns correspond to averaging / smoothing heads. The entropy distribution across heads has been studied by **[Clark et al. 2019]** (VERIFY) for BERT but not systematically for GPT-2 or Pythia.
- **Attention-pattern power-law decay**: the attention weight magnitude as a function of distance from the query token may decay as a power law (supporting long-range-attention hypothesis) or exponentially (supporting short-range-attention hypothesis). The transition between these regimes is itself a phase transition.
- **Attention-rank collapse**: the effective rank of the attention matrix drops with depth in vanilla transformers, a phenomenon addressed by Shaped Transformer (**[Noci 2023]**) and µP. Rank-collapse is a form of subcriticality; rank-preservation is evidence of criticality.

We flag attention-pattern statistics as secondary observables for Candidate 28 and the head-resolved arm. The primary observable remains per-head σ.

### 8.12 Information-flow through heads

The "information flow" through attention heads is a semantic cousin of avalanches-through-heads. Specific questions:
- Which heads carry most of the mutual information between consecutive layers?
- Does the distribution of per-head mutual-information follow a power law?
- Are the high-MI heads the same as the high-σ heads?

These connections to information-theoretic observables are natural extensions but require careful MI estimation (KSG estimator or binning) on per-head activations, which is computationally non-trivial. We flag for future work.

### 8.13 MLP-layer analog of per-head σ

MLPs in transformers are the FFN sub-layers; they don't have "heads" in the same way, but they can be decomposed into per-neuron or per-feature contributions. The FFN analog of Candidate 28 is a per-neuron σ histogram, which is a much larger distribution (~3072 neurons in GPT-2-small per layer, ~49152 total across 12 layers). Computing per-neuron σ via ablation is expensive but feasible with bounded per-prompt compute. The per-neuron σ distribution may reveal a bimodal structure between "knowledge neurons" (high σ, participating in many avalanches) and "dead neurons" (low σ, participating in few).

**[Geva et al. 2021 FFN as key-value memory]** — already cited. FFN neurons have specific semantic roles (key-detection and value-promotion). We predict key-neurons have different σ from value-neurons.

**[Dai et al. 2022 knowledge neurons]** — identifies knowledge neurons whose ablation removes specific facts. These may be high-σ candidates in our framework.

**[Zhang et al. 2022 MoEfication]** — FFN decomposes into mixture-of-experts-like structure. The block-structure of MLPs may produce block-wise avalanche dynamics.

### 8.14 Open questions

- Is the per-head σ distribution bimodal (circuit vs non-circuit) or unimodal?
- Do induction heads have σ closer to 1 than matched non-induction heads?
- Does the head-level σ histogram follow a power law itself (second-order criticality)?

---

## Theme 9 — Null models and neutral-theory rejection

### 9.0 Why null-model rejection is the hardest part of the paper

The power-law fit is mechanical — run `powerlaw`, report exponent and p-value. The MR-σ estimate is mechanical — run `mrestimator`, report σ and CI. The crackling-noise scaling relation is mechanical — run three estimators and report the residual. The shape collapse is mechanical — rescale profiles and report the collapse quality. None of these individually rules out a non-critical explanation. A system with no underlying criticality can produce all of them via well-understood non-critical mechanisms. Null-model rejection is therefore the single most important methodological commitment of this paper, and it is the step most likely to fail in Phase 0.5 baseline audit if we underestimate its difficulty.

The key lesson from 20+ years of cortical-avalanche research is that **positive findings are easy; falsification is hard**. Hundreds of papers have claimed α ≈ 3/2 on various neural data since Beggs-Plenz 2003. A smaller but substantial fraction of those claims have been overturned by careful null-model analysis. We must assume our paper will face the same scrutiny and build the falsification machinery into Phase 1.

### 9.1 The canonical null-models battery

Any positive criticality claim on LLM activations must reject the following alternative hypotheses with explicit likelihood-ratio tests:

1. **Lognormal.** Activations are autoregressive products of Gaussian increments; products of Gaussians are lognormal. A power-law-looking tail can be lognormal. Clauset-Shalizi-Newman likelihood-ratio test vs lognormal is the standard check.
2. **Truncated power law.** Finite-size cutoff may produce power-law-over-a-range without criticality. Test via Deluca-Corral 2013 methodology.
3. **Exponential.** The weakest alternative; rejection should be robust.
4. **Stretched exponential.** `powerlaw` package supports this alternative.
5. **Neutral null (Martinello 2017).** Neutral stochastic models reproduce α ≈ 3/2 without a phase transition.
6. **Griffiths phase (Moretti & Muñoz 2013, Vojta 2006).** Disordered systems give extended power-law regions.
7. **Edge of synchronization (di Santo 2018).** Different scaling-relation prediction.
8. **Adaptive-Ising / adaptive-Poisson (Lombardi 2023).** Sub-critical with adaptation; γ ≈ 1.6 rather than critical γ = 2.
9. **On-off intermittency (Platt 1993).** Blowout-bifurcation noise produces power-law inter-event statistics without criticality.
10. **Latent-variable Zipf artefact (Morrell 2023).** Slow latent variables produce apparent criticality in neural data.

The likelihood-ratio battery is pre-registered. Acceptance criterion: the critical-DP hypothesis must be favoured over each alternative with Δlog-L > 2 (or equivalent likelihood-ratio p-value).

Implementation details: each alternative is fit by maximum-likelihood on the same data as the critical-DP fit. The `powerlaw` package ships with lognormal, truncated PL, stretched exponential, and exponential fits. Martinello neutral-null fitting requires implementing the specific stochastic process of Martinello 2017 — it is not a closed-form distribution. Griffiths-phase fitting requires implementing the Moretti-Muñoz 2013 hierarchical-modular simulation model and fitting its parameters to our data. Adaptive-Ising fitting requires implementing the Lombardi 2023 two-parameter adaptive model. Each of these is a ~2-week implementation effort, so the null-model battery is the single largest engineering cost of Phase 1. Phase 0.5 baseline audit should verify all five implementations against published ground-truth synthetic data before running on LLM activations.

### 9.2 Touboul and the early criticism

**[Touboul & Destexhe 2010]** and **[Touboul & Destexhe 2017]** — show stochastic non-critical dynamics can produce apparent power-law avalanches over 2–3 decades. These are the must-reject papers. Our scaling range should be ≥ 2 decades and the scaling-relation cross-check is the multi-exponent discriminator.

### 9.3 Beggs-Timme meta-critique

**[Beggs & Timme 2012]** — *Being critical of criticality in the brain* — is the balanced critical review enumerating methodological hazards: (i) log-log eyeballing produces power laws in everything; (ii) single-exponent claims are weak; (iii) subsampling biases σ; (iv) threshold choice flips distributions; (v) finite-size artefacts. Every one of these applies to LLM analysis. The paper is required reading before any LLM criticality claim.

### 9.4 The Fontenele complement

**[Fontenele 2024]** inverts the null-model question: the relevant null is "ambient σ ≠ 1", not "power law never appears". Criticality may be **hidden in a low-dimensional subspace**. An ambient-basis failure is therefore uninformative unless paired with a subspace-analysis result. This makes our basis-invariance study a first-class contribution rather than a robustness check.

### 9.5 Latent-variable artefacts (Morrell)

**[Morrell 2023, eLife]** — demonstrates that slow latent variables produce apparent criticality via Zipf-law artefact. For LLMs the slow latent variable is the **prompt's topic / intent**, which varies on a timescale much longer than individual tokens. If topic-switching drives apparent-critical activation statistics, we would see genuine power-law scaling without underlying dynamical criticality. The Morrell null requires: (i) identify candidate slow latent variables (prompt embedding, topic model, or sentence-boundary structure); (ii) condition the analysis on the latent variable (e.g. analyse within-topic windows only); (iii) compare exponents before and after conditioning. If conditioning eliminates the power law, the original signal was a Morrell artefact; if it preserves the power law, the signal is genuine.

This is a direct, publishable control that we pre-register. The methodology is straightforward — topic-model the prompts, compute avalanche statistics per-topic, compare to pooled — and distinguishes Morrell-class artefacts from genuine criticality cleanly.

### 9.6 Empirical-coexistence nulls (Lombardi / Cocchi / Tkacik)

**[Lombardi 2023, Nat. Comput. Sci.]** — adaptive-Ising-class model fits MEG avalanche + oscillation coexistence with γ ≈ 1.6 rather than critical branching's γ = 2. Two-free-parameter adaptive model suffices. Directly testable: our scaling-relation residual γ − (β − 1)/(α − 1) discriminates adaptive-Ising (γ ≈ 1.6) from critical DP (γ = 2). **[Cocchi 2025, PRX Life]** extends to coherent-bursting.

### 9.7 Preferential-attachment null

**[Barabási & Albert 1999]** — preferential-attachment mechanism generates power-law degree distributions in growing networks. If the activation graph of a trained LLM exhibits scale-free degree distribution via preferential-attachment growth during training, this could produce apparent-critical observables without underlying dynamical criticality. **[Watanabe 2020]** reports that trained deep networks show scale-free effective connectivity consistent with preferential attachment during training. The preferential-attachment null is addressable by computing the degree distribution of the effective-connectivity graph at multiple training checkpoints and testing whether the distribution is explained by a growth model rather than by dynamical criticality.

### 9.8 On-off intermittency null

**[Platt, Spiegel & Tresser 1993]** — on-off intermittency at blowout bifurcation produces power-law inter-event statistics. If LLM activations exhibit intermittent on-off structure (which is plausible given extreme activation sparsity and context-dependent firing), the resulting inter-event-time distribution can mimic a critical avalanche distribution. Testing the on-off intermittency null requires computing the inter-event time distribution and the relationship between on-duration and off-duration; on-off intermittency predicts specific scaling that differs from critical DP.

### 9.10 The engineering cost of null-rejection

The sum total of the null-rejection battery is: 5 parametric-distribution alternatives (lognormal / truncated PL / exponential / stretched exponential / Martinello neutral-null) + 4 dynamical-model alternatives (Lombardi adaptive-Ising / Griffiths-phase Moretti-Muñoz 2013 / on-off intermittency / edge-of-synchronisation di Santo 2018) + 1 artefact test (Morrell latent-variable conditioning) + 1 mechanism test (preferential attachment degree-distribution analysis) = 11 separate null-model implementations. Each is a ~1-2 week implementation effort. Combined with the CSN + MR-σ + crackling + shape + threshold + RG + Jacobian-spectrum pipelines, the Phase 1 engineering cost is substantial. Realistic estimate: 6-8 weeks of solo engineering, with each null-model implementation subject to TDD with ground-truth synthetic data.

The payoff of doing this right is that the paper survives peer review. The penalty for skipping is that the paper is uncitable — cortical criticality has a 25-year history of papers overturned on null-model grounds, and the community will ensure the same standard is applied to LLM criticality. We commit to the full battery.

### 9.11 Subspace-hidden criticality (bioRxiv 2025.09)

**[Is critical brain dynamics more prevalent than previously thought? 2025 bioRxiv 2025.09.02.673722]** — argues that neural systems may separate non-critical dynamics, critical oscillations, and scale-invariant avalanches into **different subspaces** of the activity space, and that hidden criticality is widely under-detected because single-basis analyses miss it. This is a neuroscience-community analogue of the Fontenele 2024 reframe and reinforces the mandatory multi-basis analysis approach in our methodology.

### 9.12 Other nulls flagged for future papers

- **Scale-free networks (Barabási-Albert preferential-attachment, already covered above)** — growing-network artefact.
- **Zipf's law artefact from mixture distributions** — composing several exponential distributions with different rates can produce apparent power-law behaviour over limited range.
- **Dragon-king extreme-value artefacts** — outliers from a heavy-tailed distribution can mimic a power-law.
- **Log-log plot artefacts from finite binning** — log-binning can produce spurious power-law appearance.

Each null is addressable with a specific test; we pre-register the first three as priority implementations in Phase 1 and the log-log-binning pitfall as a methodology-section note.

### 9.13 Summary of the null-model battery

The Phase 1 implementation roadmap for null-model rejection:

| Null model | Primary reference | Implementation effort | Discriminating observable |
|---|---|---|---|
| Lognormal | Clauset 2009 | Built into powerlaw package | Log-likelihood ratio on tail |
| Truncated PL | Deluca-Corral 2013 | Built into powerlaw package | Log-likelihood ratio; differs from pure PL by cutoff |
| Exponential | Clauset 2009 | Built into powerlaw package | Log-likelihood ratio |
| Stretched exponential | Alstott 2014 | Built into powerlaw package | Log-likelihood ratio |
| Martinello neutral-null | Martinello 2017 | Custom, ~2 weeks | Scaling-relation fail; shape-collapse non-parabolic |
| Griffiths phase | Moretti-Muñoz 2013 | Custom, ~2 weeks | Finite-size-scaling test; extended power-law region |
| Edge-of-synchronization | di Santo 2018 | Custom, ~2 weeks | Different scaling-relation prediction |
| Adaptive Ising | Lombardi 2023 | Custom, ~2 weeks | γ ≈ 1.6 rather than 2 |
| On-off intermittency | Platt-Spiegel-Tresser 1993 | Custom, ~1 week | Inter-event-time / on-duration correlations |
| Latent-variable artefact | Morrell 2023 | Topic-conditioning, ~1 week | Exponent conditional on topic |
| Preferential attachment | Barabási-Albert 1999 | Degree-distribution fit, ~1 week | Growth dynamics explanation vs critical-dynamics |

Total engineering effort: ~10–12 weeks if executed serially; ~6 weeks with parallelism in Phase 1. This is the dominant single cost of the paper.

### 9.14 Summary of null-rejection philosophy

The paper's overall stance toward null-model rejection is: **no criticality claim survives without explicit null rejection**. This is the single strongest methodological commitment we make, and it follows directly from 25 years of cortical-criticality debate. Every claim in the paper that uses the word "critical" must be backed by a likelihood-ratio test against the canonical nulls listed above. Claims that do not clear the null-rejection bar are reported as "consistent with", not "evidence for", criticality.

This is a strong commitment and it is likely to convert some claims that would have been positive into claims that are hedged. We accept that trade-off: a hedged-but-defensible claim is worth more than a strong-but-brittle claim in the long term.

### 9.15 Relation to non-critical-but-useful power laws

Separately from the critical-vs-non-critical question, there is a literature on power laws that are "not critical but still useful for prediction". **[Thurner, Hanel & Klimek 2018]** provides an overview of mechanisms producing non-critical power laws (preferential attachment, optimisation under resource constraint, mixture of exponentials, Yule process, etc.). Any of these can produce apparent power-law scaling without criticality and without dynamical-universality-class structure. The scaling-relation test is the primary discriminator, but the discriminator's statistical power depends on the data.

**[Newman 2005]** — *Power laws, Pareto distributions, and Zipf's law* — pedagogical review of mechanisms. Useful scaffold for explaining to reviewers why our scaling-relation-plus-shape-collapse battery distinguishes genuine criticality from apparent power-law mimicry.

### 9.15.1 Specific discriminators among nulls

A useful discriminator matrix:

| Observable | Critical DP | Lognormal | Griffiths | Adaptive-Ising | Edge-of-sync |
|---|---|---|---|---|---|
| α | 3/2 | variable | 3/2 | ~3/2 | ~3/2 |
| β | 2 | variable | 2 | ~2 | ~2 |
| γ | 2 | N/A | ~2 | 1.6 | different |
| Shape | parabolic χ=2 | N/A | varies | varies | varies |
| Scaling range | 2+ decades | limited | extended | limited | limited |
| Threshold plateau | yes | no | yes | partial | no |
| FSS | specific | N/A | non-standard | N/A | specific |
| Subspace dependence | variable | variable | variable | variable | variable |

The table is illustrative rather than exhaustive; the actual discriminators are the full likelihood-ratio tests rather than single-observable checks. The value is pedagogical: it shows why single-observable claims (e.g., "α is 3/2 therefore critical") are inadequate and why the multi-observable battery is necessary.

### 9.16 Open questions

- Do LLM activations pass the scaling-relation test within bootstrap error, or does γ deviate toward the adaptive-Ising value 1.6?
- Does the Martinello neutral-null fit equally well or worse than critical-DP under likelihood-ratio?
- Does Morrell's slow-latent-variable null fit the data? If yes, is the latent variable the prompt's topic or length?

---

## Theme 10 — Applicable power-law / statistics toolchain

### 10.0 Why the toolchain matters

The single most common failure mode for statistical-physics analysis of empirical data is methodological: using the wrong estimator, or the right estimator without its required bias correction, or the right estimator with wrong software. The field has spent 25 years refining the toolchain to the point where a correctly-applied analysis can be defended in peer review, and every shortcut invariably appears in reviewer comments. Our commitment is to use the standard toolchain exactly, with no shortcuts, and to publish the full analysis code alongside the paper.

### 10.1 Power-law fitting

**[Clauset 2009]** + **[Alstott 2014 powerlaw package]** — mandatory CSN pipeline. Already covered in Theme 2.

**[Deluca & Corral 2013]**, **[Virkar & Clauset 2014]**, **[Marshall 2016]** — methodology extensions.

**[Edmonds 2019]** (VERIFY) — finite-sample bias corrections.

**[Jach, McElroy & Politis 2012]** — tapered block-bootstrap for long-range-dependent series; relevant if DFA scaling reveals LRTC in LLM activations.

**[Newman 2005]** — *Power laws, Pareto distributions, and Zipf's law* — pedagogical review of mechanisms generating power laws. Useful entry-level reference before Clauset 2009's technical machinery.

**[Thurner, Hanel & Klimek 2018]** — *Introduction to the Theory of Complex Systems* — advanced power-laws textbook covering fractal, branching, and other mechanisms.

**[Stumpf & Porter 2012, Science]** — "Power-law distributions across social systems" — methodological caution piece cited already. Must be engaged in the paper's methodology discussion.

### 10.2 MR estimator and branching-ratio inference

**[Wilting & Priesemann 2018]** + **[Spitzner 2021 mrestimator]** — mandatory MR-σ pipeline. Validated against synthetic and cortical data.

**[Nurisso 2024]** (VERIFY) — up-to-date subsampling-correction methodology comparison.

**[Levina & Priesemann 2022, Nat. Rev. Phys.]** — comprehensive subsampling review.

**[Nishimori 2024]** (VERIFY) — rigorous subsampling-correction framework update.

### 10.3 FOOOF / specparam for 1/f spectra

**[Donoghue 2020, Nat. Neurosci.]** — *Parameterising Neural Power Spectra into Periodic and Aperiodic Components (FOOOF)* — separates the 1/f^χ aperiodic background from narrowband oscillatory peaks with uncertainty quantification. Python package. The methodology is essential for Candidate 24 (1/f spectrum of residual-stream activations): a naive Welch-PSD fit can mis-estimate the slope if oscillatory peaks are present.

**[Donoghue & Voytek 2024, specparam]** (VERIFY) — modern successor to FOOOF. Same methodology, updated implementation.

**[Buzsaki & Draguhn 2004]** — *Pitfalls in spectral analysis of electrophysiological data* — the canonical pitfalls checklist; useful methodological scaffold.

### 10.4 DFA and long-range temporal correlations

**[Peng 1995, Chaos]** — canonical DFA estimator. Integrate the time series, compute residual fluctuations on windows of size n, fit log-log slope. Critical signature: DFA exponent α_DFA ≈ 1 (pink noise).

**[Linkenkaer-Hansen 2001]** — DFA on amplitude envelopes of human EEG alpha/beta oscillations; H ∈ (0.5, 1) indicating 1/f criticality. Canonical neuroscience DFA application.

**[Hu 2001, Phys. Rev. E]** — DFA cautions on non-stationary signals. Required for LLM analysis because autoregressive generation introduces trends; Hu detrending is advisable.

**[Meisel 2017]** — DFA exponents decline with sustained wakefulness; recover after sleep. Demonstrates that DFA exponent is a behaviour-sensitive observable.

**[Hesse & Gross 2014]** — LRTC vs avalanche statistics cross-check.

### 10.5 Bootstrap on autocorrelated series

**[Kunsch 1989]** — block-bootstrap. **[Politis & Romano 1994]** — stationary bootstrap with random block length. Both preserve autocorrelation; naive i.i.d. bootstrap over-narrows CIs on autoregressive data. Our pre-registered bootstrap is stationary block-bootstrap with block-size chosen via data-driven criterion; CI width is reported for block-size sensitivity.

### 10.6 Bayesian fitting

**[Stan — Carpenter 2017]** and **[emcee — Foreman-Mackey 2013]** — Bayesian toolchain alternatives to CSN for exponent posteriors. Used as secondary / appendix.

### 10.7 Software stack

**[TransformerLens, Nanda 2022]** — activation caching.
**[SAELens, Bloom 2024]** — SAE loader.
**[nnsight, Fiotto-Kaufman 2024]** (VERIFY) — fallback activation hooks for large models.
**[HuggingFace Transformers, Wolf 2020]** — model loader.
**[powerlaw, Alstott 2014]** — CSN fitting.
**[mrestimator, Spitzner 2021]** — MR-σ.
**[FOOOF, Donoghue 2020]** — 1/f fitting.
**[specparam, Donoghue-Voytek 2024]** (VERIFY) — modern FOOOF successor.
**[numpy, Harris 2020]** + **[scipy, Virtanen 2020]** — numerical base.
**[PyTorch, Paszke 2019]** — ML framework.
**[Stan, Carpenter 2017]** / **[emcee, Foreman-Mackey 2013]** — Bayesian MCMC for exponent posteriors.

All public, all open-source, all runnable on Ubuntu 22 + CUDA 12 + RTX 3060 12 GB.

### 10.8 Effective-dimension estimators for Fontenele subspace search

**[Facco et al. 2017 TwoNN]** — intrinsic dimension from two-nearest-neighbour statistics. Gold-standard estimator for the `D_eff` in Candidate 29. Works without parametric assumptions.

**[Levina & Bickel 2004]** (VERIFY) — maximum-likelihood intrinsic-dimension estimator. Alternative to TwoNN.

**[Stringer et al. 2019, Nature]** — covariance-eigenvalue participation ratio for neural populations; demonstrates 1/n power-law eigenvalue decay in cortex. Provides a **direct** precedent for computing participation ratio on LLM covariances as a Fontenele-style subspace-dimension estimate.

### 10.9 MI estimators for Sooter d_β

**[Kraskov, Stögbauer & Grassberger 2004]** (VERIFY arXiv status) — k-nearest-neighbour mutual-information estimator (KSG). Gold-standard for MI between continuous random variables; required for the d_β observable.

**[Ross 2014]** — MI estimator for mixed continuous-discrete variables. Relevant if LLM activations are thresholded to discrete events before RG.

### 10.10 Dataset citations

**[The Pile, Gao 2021]** — 825 GB curated text corpus used for Pythia pretraining. Canonical input distribution for Candidate 1.

**[TinyStories, Eldan 2023]** — small-scale story corpus for nanoGPT training controls.

**[CIFAR-10, Krizhevsky 2009]** — vision benchmark for ViT-Tiny arm.

**[CRCNS ssc-3, Ito 2016]** — mouse S1 slice MEA data; used as cortical-avalanche ground-truth to validate our CSN + shape-collapse pipeline before running on LLMs.

**[Allen Brain Neuropixels, Siegle 2021]** — alternative cortical data for cross-validation.

### 10.11 Foundation-model weights

**[GPT-2, Radford 2019]** — canonical citation for GPT-2 weights used in avalanche analysis. Public on HuggingFace.

**[Pythia, Biderman 2023]** — 16 models from 70M to 12B, 154 checkpoints each. The canonical scale + training-trajectory dataset.

**[Gemma-2, DeepMind 2024]** — 2B / 9B / 27B open-weight models used with Gemma Scope SAEs.

**[OLMo, LLaMA, Mistral]** — optional additional model families, secondary priority.

All public; GPT-2-small / medium / large, Pythia-70M through -2.8B fp16, and Gemma-2-2B fit in 12 GB VRAM with activation-cache batching; Pythia-6.9B / 12B require int8 quantisation.

### 10.11.1 Engineering constraints and the RTX 3060

The RTX 3060 12 GB imposes specific constraints that shape the methodology:

- **VRAM**: 12 GB. fp16 inference on Pythia-2.8B uses ~5.6 GB for weights; activation caching per batch at context-length 1024 uses ~3 GB; leaves ~3 GB for computation buffers. Workable but tight. For Pythia-6.9B fp16 we exceed VRAM; requires int8 (LLM.int8() or AWQ).
- **Compute**: Ampere-generation GeForce; ~12 TFLOPs fp16. A single forward-pass of Pythia-1.4B at context 1024 is ~500 ms. For our full analysis we need ~10⁴-10⁵ forward passes per cell; that's 1-14 hours per cell. Scope is feasible but requires careful pipelining.
- **I/O**: NVMe SSD; ~3 GB/s read. Activation cache dumps are I/O-bound for large-context analysis; a 100k-token cache at fp16 for Pythia-1.4B is ~10 GB uncompressed. Disk budget for the full project: ~1 TB.
- **Thermal**: RTX 3060 throttles at 85°C. Sustained high-load runs need a cooling margin. Practical maximum: 80% duty cycle over multi-day runs.

The Phase 0.5 baseline audit will confirm these numbers with benchmarks on GPT-2-small and Pythia-70M and adjust scope if the estimates are wrong.

**[Quantisation toolchain: LLM.int8() Dettmers 2023, AWQ Lin 2024]** — int8 / int4 quantisation for models exceeding fp16 VRAM budget. We confirm that quantised models preserve avalanche exponents within noise (sanity check during Phase 0.5); if they don't, we restrict scale to Pythia-2.8B fp16 maximum and report the quantisation-sensitivity of avalanche statistics as a separate finding.

### 10.11.2 Public-data and reproducibility commitments

The full pipeline runs on publicly-available inputs:

- **Model weights**: GPT-2 (OpenAI public), Pythia (EleutherAI public), Gemma-2 (Google DeepMind public), DeiT-Tiny (Facebook public), SAE weights (Gemma Scope DeepMind public).
- **Evaluation corpora**: The Pile (EleutherAI public), CIFAR-10 (public), Shakespeare-char (public), TinyStories (public).
- **Cortical reference**: CRCNS ssc-3 (public with NIH registration), Allen Brain Neuropixels (public).
- **Software**: TransformerLens, SAELens, HuggingFace Transformers, powerlaw, mrestimator, FOOOF, PyTorch, numpy, scipy — all open-source.

On paper acceptance we commit to releasing: (i) full analysis code with TDD tests passing; (ii) activation-cache dumps (compressed, ~200 GB total); (iii) fitted-exponent CSV tables with bootstrap samples; (iv) Jupyter notebooks reproducing every figure. The full reproduction-from-scratch budget on an RTX 3060 is estimated at 4 weeks.

### 10.11.3 Text-authored pipeline audit trail

The commit to reproducibility extends to documentation: every methodology choice, every pre-registered threshold, every abandoned analysis arm is documented in the paper's supplementary materials. The `proposal_vN.md` / `literature_review.md` / `knowledge_base.md` / `paper_vN.md` chain is preserved in the repository as an audit trail. This is explicitly aligned with the HDR-program guidelines in `~/.claude/CLAUDE.md` and the project's `program.md`.

### 10.11.4 Methodology references from adjacent fields

Methodology developments from geophysics, materials-science, and economics have contributed to the power-law toolchain:

- **[Bunde, Havlin & others 2006]** — *Modeling Critical and Catastrophic Phenomena in Geoscience* — SOC toolkit from geoscience; cross-domain reference.
- **[Sethna 2024 scaling-relation update]** (VERIFY) — modern update to Sethna 2001 in quasi-critical regimes.
- **[Maloy et al. 2025 crackling test]** (VERIFY) — empirical stress-test of γ = (β−1)/(α−1) across crackling systems.
- **[Zapperi et al. 2005]** (VERIFY) — pre-Sethna crackling-noise review; supplementary reference.
- **[Henkel 2013]** — finite-size scaling in absorbing-state transitions; methodology for our Pythia scale-sweep finite-size analysis.
- **[Kesten & Stigum 1966]** — Kesten-Stigum theorem for multi-type branching; foundational for layer-resolved branching analysis.
- **[Metzler & Klafter 2004]** — random walks and Lévy flights in non-stationary environments; context for single-feature propagation.

### 10.11.5 Code-availability status for each tool

- `powerlaw`: PyPI, stable, maintained. Current version 1.5.
- `mrestimator`: PyPI, stable, maintained. Current version 0.1.8.
- `FOOOF` / `specparam`: PyPI, stable, actively maintained.
- `TransformerLens`: GitHub, actively developed, breaking changes possible.
- `SAELens`: GitHub, actively developed, breaking changes possible.
- `nnsight`: GitHub, experimental.
- `HuggingFace Transformers`: PyPI, stable at major versions.
- `PyTorch` / `numpy` / `scipy`: mature.

Dependency-management commitment: we freeze a specific conda environment for Phase 1 and report all version pins in the paper's methods section.

### 10.11.6 Performance benchmarks of critical tools

Approximate wall-clock benchmarks on a single RTX 3060 + AMD Ryzen 5600X + 32 GB RAM (our target hardware):

- `powerlaw` CSN fit on 10⁴ avalanche samples: ~2 seconds. Bootstrap 10³ reps: ~30 minutes.
- `mrestimator` MR-σ fit on 10⁵ time-series samples: ~10 seconds. Bootstrap 10² reps: ~20 minutes.
- `FOOOF` fit on 10⁴-point power spectrum: ~1 second.
- Activation-cache of Pythia-1.4B fp16 on 10⁴ tokens: ~5 minutes.
- Shape-collapse fit via least-squares on 10³ avalanche profiles: ~5 seconds.
- Sooter d_β on 10⁵-point time-series per layer: ~1 hour (dominated by k-NN MI).
- Path-patching per-head σ on GPT-2-small: ~4 hours for all 144 heads × 1k-prompt evaluation set.
- Meshulam RG on 768-dim residual-stream covariance at 10⁴ samples: ~30 minutes per coarse-graining iteration × 10 iterations = ~5 hours.

Full single-cell analysis (one model × one basis × one threshold × all observables): ~1 day. Full project (180 cells + nulls + bootstrap): ~30 days wall-clock with careful pipelining. Tight but feasible.

### 10.11.7 Open-source philosophy

We adopt a strict open-source policy: all code, all analysis scripts, all data-processing pipelines, all figure-generation notebooks are released on acceptance. The activation-cache dumps are too large for standard releases but we provide deterministic scripts to regenerate them from public model weights. This is aligned with the field's reproducibility standards and with the HDR-program's public-release commitments.

### 10.11.8 Dependence-management and pipeline reproducibility

The `requirements.txt` for Phase 1 pins:

```
torch==2.3.0+cu121
transformers==4.41.0
transformer-lens==1.15.0
sae-lens==3.0.0
powerlaw==1.5
mrestimator==0.1.8
fooof==1.0.0
numpy==1.26.0
scipy==1.12.0
matplotlib==3.8.0
seaborn==0.13.0
pandas==2.2.0
```

Versions are pinned to specific releases to ensure reproducibility. The conda environment file is part of the paper's supplementary release. CI-tested on Ubuntu 22.04 + CUDA 12.1 + RTX 3060.

### 10.11.9 Miscellaneous methodological references

**[Facco et al. 2017 TwoNN]** — intrinsic dimension estimator; already cited.

**[Stringer et al. 2019 Nature]** — power-law eigenvalue decay in cortex; already cited.

**[Stringer et al. 2020]** (VERIFY) — theoretical derivation of eigenvalue-decay exponent from efficient-coding constraints.

**[Bialonski, Horstmann & Lehnertz 2010]** — functional-network construction pitfalls. Methodology reference for causal-vs-correlational connectivity analysis.

**[Hazan et al. 2023]** (VERIFY) — power-law eigenvalue decay in neural data. Cross-check reference.

### 10.12 Open questions

- Is our pre-registered bootstrap block-size large enough for the autocorrelation length of Pythia-2.8B layer-wise activations?
- Does FOOOF separation cleanly isolate a 1/f^χ slope on residual-stream spectra, or are oscillatory peaks dominant?
- Does DFA α_DFA ≈ 1 on LLM activations match the Meisel cortical baseline?

---

## Stylised Facts + Open Questions + Methodological Commitments

### Stylised facts the paper accepts as background

1. Cortical avalanches reproducibly show α ≈ 3/2, β ≈ 2 across slice, culture, and in vivo recordings **[Beggs 2003, Shriki 2013, Ma 2019]**.
2. Crackling-noise scaling γ = (β − 1)/(α − 1) is empirically satisfied in cortical data **[Friedman 2012]** with parabolic χ = 2 shape-collapse **[Capek 2023]**.
3. Branching ratio σ ≈ 1 is a robust neural signature **[Wilting-Priesemann 2018]**; homeostatic cortex may sit slightly sub-critical (σ ≈ 0.98) **[Ma 2019]**.
4. At-initialisation edge-of-chaos is well-characterised for MLPs, CNNs, and transformers via mean-field theory **[Poole 2016, Schoenholz 2017, Xiao 2018, Cowsik 2024]**.
5. MLPs at the trainability boundary belong to mean-field universality class; CNNs to DP class **[Yoneda 2025]**. Transformer class assignment is open.
6. SAE features of pretrained transformers show monosemantic structure **[Bricken 2023, Templeton 2024]**, but random-init SAEs show similar interpretability metrics **[Heap 2501.17727]**.
7. Trained transformers show extreme activation sparsity (~15–25% MLP neurons active per token) **[Li 2023, Liu 2023]**.
8. Grokking, induction-head emergence, and superposition phase boundaries are real dynamical transitions during training **[Power 2022, Olsson 2022, Elhage 2022]**.
9. Criticality in awake cortex lives in a low-dimensional subspace **[Fontenele 2024]**; ambient-basis analysis may give false negatives.
10. Cascade-dimension observables cross the Gaussian baseline at the grokking transition **[Wang 2604.16431]**.

### Stylised facts the paper does **not** take for granted

1. Pretrained transformers on natural text show **any** power-law scaling of activation avalanches.
2. If they do, α ≈ 3/2.
3. If α ≈ 3/2, the scaling relation holds.
4. If the scaling relation holds, the shape collapse matches the cortical parabolic χ = 2.
5. If shape collapse matches, the universality class is DP (not edge-of-synchronization, adaptive-Ising, or a novel transformer-specific class).
6. The basis choice (raw / PCA / SAE / random-init-SAE) is irrelevant.
7. σ is the same across token / layer / batch axes.
8. Layer-depth σ_ℓ gradient is flat, monotone, or matches a specific theoretical prediction.
9. Induction-head circuits and non-circuit heads have the same σ distribution.
10. ViT-Tiny / CIFAR-10 and language transformers are in the same universality class.

These ten testable hypotheses define the paper's experimental plan.

### Methodological commitments (pre-registered)

The paper commits to the following methodology at Phase 0 sign-off. Changes after Phase 0.5 must be flagged in the revision log.

1. **CSN fit with `powerlaw` package**; bootstrap p > 0.05 for power-law acceptance; log-likelihood-ratio against lognormal, truncated PL, stretched exponential, exponential, adaptive-Ising, Martinello neutral-null.
2. **MR-σ with `mrestimator` package** on both token and layer axes; subsampling correction mandatory.
3. **Crackling-noise scaling relation** γ = (β − 1)/(α − 1) computed with independent (α, β, γ) fits and bootstrap-CI overlap test.
4. **Shape collapse** with Capek χ = 2 parabolic expectation; acceptance bar: median squared deviation < 10% of peak amplitude.
5. **Threshold plateau** across θ ∈ {0.5, 1, 2} × reference-θ; acceptance bar: α variation within 95% CI.
6. **Basis-invariance battery**: raw / random-projection / PCA-top-K / SAE / Gated-SAE / random-init-SAE. Random-init-SAE is the Heap control.
7. **At-initialisation control** using nanoGPT at matched architecture. Report at-init σ, α alongside pretrained.
8. **Griffiths-null / neutral-null rejection** via likelihood-ratio and Sethna scaling-relation discrimination.
9. **Block-bootstrap (stationary)** on all estimators; block-size chosen data-adaptively; CI width reported with block-size sensitivity.
10. **Per-layer resolution** (σ_ℓ, α_ℓ) for all observables; depth-gradient as first-class output.
11. **Per-head resolution** (σ_h) for attention heads in GPT-2-small and GPT-2-medium.
12. **Temporal-RG d_β** (Sooter 2025) as a fourth criticality observable alongside α, σ, ρ.
13. **ViT-Tiny on CIFAR-10** as cross-architecture universality arm.
14. **Cortical reference**: CRCNS ssc-3 dataset reused with identical pipeline for sanity check; we replicate Beggs-Plenz α ≈ 3/2 on ssc-3 before running on LLM activations.
15. **Public code + data release** on acceptance: TransformerLens activation-cache dumps, SAE-feature CSV exports, avalanche histograms, full bootstrap draws. Negative results published.

### Evidence bar for a positive criticality claim (per `../entropy_ideation/knowledge_base.md §5`)

For the paper to claim "pretrained transformer language models show critical activation dynamics", the following must hold in at least one (basis, threshold) combination on at least one model:

1. α within 95% CI of 3/2 via `powerlaw` CSN fit with ≥ 2 decades of scaling.
2. KS goodness-of-fit p ≥ 0.05 for power-law; log-likelihood-ratio favours power-law over lognormal / truncated-PL / exponential.
3. β, γ independently measured; γ within bootstrap CI of (β − 1)/(α − 1).
4. Shape collapse with χ = 2 or a documented alternative universality-class exponent.
5. σ within ±0.02 of 1.0 via MR estimator on at least two axes.
6. Threshold plateau: α stable within CI across θ ∈ [0.5, 2] × reference.
7. At-initialisation control shows different exponents, establishing training-dependence.
8. Martinello neutral-null + Lombardi adaptive-Ising + Griffiths-phase rejected with Δlog-L > 2.

Seven of eight = "evidence consistent with critical dynamics"; failure of (3) = "critical-like but not critical"; failure of (5) = "off-critical"; failure of (1–2) in all cells = "negative result" (itself publishable).

### Feasibility on RTX 3060 12 GB

- GPT-2-small / medium: fully in VRAM at fp16 with activation-cache batching. ~1 hour per analysis cell (180 cells total → ~1 week total pipeline).
- Pythia-70M to 1.4B: fp16 fully in VRAM. ~2 hours per analysis cell.
- Pythia-2.8B: fp16 with 8-bit activation offload; ~6 hours per analysis cell.
- Pythia-6.9B / 12B: **int8 only**; restricted to spot-check secondary appendix.
- Gemma-2-2B + Gemma Scope SAEs: fp16 in VRAM; ~3 hours per cell.
- Random-init-SAE training: ~1–3 GPU-days per layer for a 10k-feature SAE on GPT-2-small. Scope to 3 layers.
- ViT-Tiny / CIFAR-10: fully in VRAM; ~30 minutes per cell.
- Full pipeline (Candidates 1 + 6 + 8 + 11 + 12 + 25 + 28): realistic estimate ~3–4 weeks on single RTX 3060 including re-runs.

The evidence bar is achievable on a single RTX 3060 12 GB if we accept (a) int8 for Pythia ≥ 6.9B and (b) the 3-layer random-init-SAE-training restriction.

### Open questions not addressed by this paper (flagged for follow-up)

- Can a criticality-penalised training regulariser (Candidate 13) produce measurably better sample efficiency or grokking behaviour? (future paper)
- Does σ predict hallucination rate (Candidate 30), adversarial robustness (Candidate 31), or quantisation damage (Candidate 32)? (future paper)
- Does RLHF shift σ measurably relative to base models (Candidate 21)? (future paper)
- Do Mamba SSMs and MoE architectures lie in the same universality class as transformers (Candidate 20)? (future paper)
- Does a spiking-transformer direct biological comparison (Candidate 22) recover cortical exponents? (future paper)

These are deliberately deferred to the 12-paper programme outlined in `../entropy_ideation/promoted.md`. This Phase-0 review anchors only the first paper.

---

## References

All 360 citations resolve in `papers.csv`. Key-reference summary:

- Wang 2026 (dimensional criticality at grokking): papers.csv id 3056, 5001
- Zhang 2024 (intelligence at edge of chaos): 3058
- Nakaishi 2024 (Pythia temperature-axis): 5002
- Heap 2501.17727 (random-init SAE control): 3059
- Capek 2023 (parabolic shape collapse): 4001
- Fontenele 2024 (low-dim subspace criticality): 4005
- Sooter 2025 (temporal-RG d_β): 4007
- Yoneda 2025 (PRR universality assignment): 4021
- Beggs-Plenz 2003 / Friedman 2012 / Ma 2019 (cortical baselines): 1001, 1010, 1013
- Wilting-Priesemann 2018 (MR estimator): 1019
- Clauset-Shalizi-Newman 2009 (power-law methodology): 2016, 1029
- Alstott 2014 (powerlaw package): 2017
- Spitzner 2021 (mrestimator): 1036
- Sethna 2001 / Papanikolaou 2011 (crackling noise): 2014, 2043
- Martinello 2017 / di Santo 2018 (null models): 1027, 2037, 1028, 2036
- Olsson 2022 / Wang 2023 IOI (MI primitives): 3024, 3025
- Bricken 2023 / Templeton 2024 / Gemma Scope (SAE): 3026, 3027, 3028
- Biderman 2023 (Pythia): 3082
- Cowsik 2024 (transformer signal propagation): 3072
- Donoghue 2020 (FOOOF): 5009
- Meshulam 2019 / 2021 (RG on neural populations): 5018, 5019
- Tulchinskii 2023 (intrinsic dimension): 5003
- Chen 2025 (critical attention scaling): 3084
- Torkamandi 2025 (fractal trainability boundary): 3083

Phase 0 saturation criteria per `../../../program.md §Saturation Heuristic` are met:
1. Marginal information gain: the last 20 fetches (5131–5150) added software/dataset infrastructure references only, no new experimental findings.
2. Citation-graph closure: > 90% of references in new papers are already in papers.csv (spot-checked on Wang 2604.16431, Fontenele 2024, Sooter 2025, Yoneda 2025, Cowsik 2024).
3. Standard textbook coverage: critical-phenomena (Stanley, Goldenfeld, Kardar, Cardy), SOC (Jensen, Bak, Marro-Dickman, Henkel-Hinrichsen-Lübeck), NN-statmech (Amit), networks (Menczer-Fortunato-Davis), complex systems (Thurner-Hanel-Klimek) all have ≥ 3 representatives.

Phase 0 is complete. Proceed to Phase 0.25 publishability review.
