# Neuroscience Literature Review — Criticality and Edge-of-Chaos in Neural Systems

Scope: neuroscience-half of the landscape review for the entropy-ideation workspace. Covers the critical-brain hypothesis from Beggs & Plenz 2003 through the modern subsampling-corrected branching-ratio literature, alternative signatures, criticisms, functional consequences, developmental / clinical trajectories, and methodology. Inline `[Author Year]` citations resolve to `papers_neuro.csv`. Entries whose publication year or venue I could not verify first-hand from memory are annotated `[VERIFY]`.

---

## Theme 1. Cortical avalanches and the critical-brain hypothesis

The central empirical discovery underwriting the entire field is that spontaneous neuronal activity in cortical tissue organises itself into cascades — *neuronal avalanches* — whose sizes and durations follow heavy-tailed, apparently power-law distributions. The foundational paper is [Beggs & Plenz 2003], published in the *Journal of Neuroscience*. Working with organotypic cultures and acute slices of rat somatosensory cortex, Beggs and Plenz recorded spontaneous local field potentials (LFPs) on 8×8 multielectrode arrays, thresholded the signals, grouped supra-threshold events into contiguous time bins of width Δt equal to the mean inter-event interval, and defined an *avalanche* as a sequence of consecutive bins in which at least one electrode exceeded threshold, bracketed by empty bins. The size *s* of an avalanche was the total number of supra-threshold electrodes across its constituent bins; its duration *T* was the bin count. The headline result: P(s) was well fit by a power law P(s) ∝ s^{−α} with α ≈ 3/2, and P(T) ∝ T^{−β} with β ≈ 2. Both exponents match the mean-field critical branching process, an equivalence class also occupied by directed percolation in high dimension. This specific 3/2-and-2 pairing has since become the canonical spectroscopic signature against which virtually every subsequent claim of "critical neural dynamics" is measured.

Within a few years the result was extended across preparations and species. [Beggs 2008] in *Philosophical Transactions of the Royal Society B* [VERIFY: Beggs single-author 2008 was in *Phil. Trans. R. Soc. B*, "The criticality hypothesis"] consolidated the theoretical frame, connecting the observed exponents to a branching ratio σ close to unity — the signature of a critical branching process sitting at the boundary between extinction (σ<1, subcritical, activity dies) and explosion (σ>1, supercritical, activity saturates). [Plenz & Thiagarajan 2007] in *Trends in Neurosciences* reviewed the early avalanche evidence and argued that neuronal avalanches and neural oscillations were complementary, not competing, descriptions of cortical dynamics.

Recording *in vivo* — as opposed to in slice — took longer because the technical obstacles (smaller effective population fraction recorded, movement artifacts, richer input statistics) partially obscure power-law signatures. [Petermann et al. 2009] in *PNAS* reported avalanches in awake macaque motor cortex using LFPs, showing that the 3/2 exponent survived the transition from slice to intact, behaving animal. Later, [Hahn et al. 2010] extended the evidence to cat cortex, and [Bellay et al. 2015] in *eLife* [VERIFY] reported avalanches in awake behaving mouse cortex using two-photon imaging and extracellular arrays, arguing that criticality co-exists with ongoing up/down states. [Ma et al. 2019] in *Neuron* showed that during awake behaviour the rat cortex operates "in a reverberating regime slightly below criticality" — a quantitatively important refinement discussed further in Theme 2.

Developmental and human studies rounded out the corpus. [Gireesh & Plenz 2008] in *PNAS* tracked avalanches during the first two weeks *in vitro* of rat cortical cultures and showed that the power-law signature emerges gradually with synaptic maturation, consistent with a homeostatic drift toward criticality as the network self-assembles. Human magnetoencephalography (MEG) data [Shriki et al. 2013 *J. Neurosci.*] reproduced avalanche statistics with α ≈ 3/2 and β ≈ 2, establishing that the phenomenon is not a culture artifact.

The review article that most researchers point newcomers toward is [Shew & Plenz 2013] in *The Neuroscientist* — it presents the taxonomy of evidence (avalanches, dynamic range, mutual information, long-range correlations) in a pedagogical form. [Chialvo 2010] in *Nature Physics* is the philosophical companion piece: the "critical brain" as a unifying principle for neural computation and cognition.

Crucially, the crackling-noise universality framework supplies a non-trivial cross-check on the two marginal exponents. If a system is truly sitting at a critical point within a given universality class, then α, β, and the avalanche-duration scaling exponent γ (defined by ⟨s⟩(T) ∝ T^γ, the mean size conditioned on duration) must satisfy the *exponent relation* γ = (β−1)/(α−1). For α = 3/2 and β = 2 this predicts γ = 2. [Friedman et al. 2012 *PRL*] measured all three exponents in cultured networks and reported consistency with this relation, elevating the evidence beyond mere single-exponent heavy tails. The exponent-relation test is now considered a mandatory check — reporting α alone is no longer sufficient.

By the end of this decade the central empirical pattern was robust enough to serve as a target for theory: cortical populations across preparations, species, and recording modalities exhibit scale-invariant avalanches whose exponents are close to (but not always exactly equal to) the mean-field branching-process values. What the exponents *mean*, and whether the apparent universality survives closer methodological scrutiny, is the topic of Themes 2 through 4. Key lineage papers — [Beggs & Plenz 2003], [Gireesh & Plenz 2008], [Petermann 2009], [Friedman 2012], [Shew & Plenz 2013], [Ma 2019] — constitute the core reading any ML-criticality claim should be benchmarked against.

---

## Theme 2. Branching ratio and its estimation — the subsampling problem

Power-law avalanche distributions are suggestive but degenerate — many mechanisms generate them, including non-critical ones (Theme 4). The more *model-specific* criticality predictor is the **branching ratio** σ, defined for a branching process [Harris 1963 *Theory of Branching Processes*] as the expected number of descendant events produced by a single ancestor event. For a neural population this is operationalised as σ = E[A_{t+1} | A_t] / A_t where A_t is the count of active units at time t. A critical branching process sits exactly at σ = 1; σ < 1 is subcritical (activity dies out exponentially); σ > 1 is supercritical (activity explodes).

Early estimates used a naïve regression of A_{t+1} on A_t on binned multi-electrode-array data and routinely reported σ close to 1 in slice and culture. The trouble is that this estimator is **catastrophically biased when only a small fraction of neurons is observed** — which is always the case in real experiments, where even a dense Utah array samples <10^−3 of the local population.

The decisive methodological intervention is the work of **Priesemann and colleagues**. [Priesemann et al. 2013 *PLoS CB*] [VERIFY exact journal] demonstrated in simulation that subsampled branching networks whose bulk branching ratio is σ = 1 can appear subcritical (σ̂ ≪ 1) when only a small fraction of units is recorded. They further showed that the bias depends on the *subsampling fraction*, the *interaction range*, and the *bin width* — making naïve comparisons across preparations invalid.

[Wilting & Priesemann 2018 *Nature Communications*] introduced the **Multistep Regression (MR) estimator**: rather than regressing A_{t+1} on A_t, fit the autocorrelation r_k = Cov(A_{t+k}, A_t) as a function of lag k to an exponential r_k ∝ m^k, where m is the branching ratio. The key insight: the subsampling bias corrupts the *amplitude* of r_k but not its *decay rate*. The MR estimator is therefore asymptotically unbiased under arbitrarily sparse subsampling, provided the underlying process is a stationary autoregressive branching process with a single dominant eigenvalue.

Applying the MR estimator to awake mammalian cortex, Wilting, Priesemann and colleagues repeatedly found σ̂ ≈ 0.98 — *close to but systematically below* criticality. This inaugurated the "reverberating regime" or "slightly subcritical" picture in which cortex sits just inside the absorbing phase, enjoying most of the computational benefits of critical dynamics (long memory, high dynamic range) while retaining controllability. [Wilting & Priesemann 2019 *Front. Syst. Neurosci.*] is the review-length treatment.

[Levina & Priesemann 2017] [VERIFY] showed a parallel problem for avalanche distributions: subsampling *does* preserve power-law tails in some regimes but distorts exponents in others, and the direction of distortion depends on the thresholding convention. The combination means that a naïve observer of a truly critical network can report either (a) subcritical branching ratio with power-law avalanches, (b) near-critical branching ratio with distorted avalanche exponents, or (c) critical-looking statistics that are actually generated by a non-critical bulk process — depending on which diagnostic they apply.

Beyond subsampling, additional methodological hazards sit inside branching-ratio estimation:

- **Bin width.** The branching process is defined in discrete time; empirical time bins must be chosen. Beggs & Plenz used Δt = mean inter-event interval, which varies with threshold, with state (up vs down), and with population size. [Priesemann et al. 2014 *Front. Syst. Neurosci.*] discussed how mis-chosen bin widths *create* spurious power laws in non-critical data.
- **Threshold choice.** Converting continuous LFPs or calcium signals to binary "events" requires a threshold. [Villegas et al. 2019] [VERIFY] and others have shown that exponent estimates move continuously with threshold.
- **Non-stationarity.** Cortical state changes on the time-scale of seconds to minutes (sleep, attention, locomotion). A stationary branching model over a 10-minute recording cannot capture this.
- **Finite-size scaling.** Truly critical systems show finite-size *scaling* — the cut-off of P(s) should scale as a known power of system size N. Few neural datasets span enough of N to test this; the absence of the test is easy to overlook.

Software: the **Mrestimator** toolbox (Spitzner et al. 2018) [VERIFY Spitzner 2018 *PLoS ONE*] implements the MR estimator with confidence intervals. **NCC** (Marshall et al.) is a competing Matlab package focused on avalanche statistics.

For ML practitioners, the take-away is blunt: if you compute a naïve branching ratio on a subsampled slice of a network's activations and report σ ≈ 1, you have proved nothing. You must either (a) use an unbiased estimator such as MR, (b) analytically relate the observed statistic to the known true population, or (c) perform the subsampling control on synthetic critical and non-critical networks to characterise the bias for your pipeline. The subsampling problem is the single most important methodological pitfall in the entire field — discussed in every recent review [Wilting & Priesemann 2019; Zimmern 2020].

---

## Theme 3. Alternative signatures of criticality

Power-law avalanches and σ = 1 are the two most cited signatures, but the critical-brain hypothesis has accumulated a richer portfolio of *independent* diagnostics. Converging evidence across signatures is what makes the claim strong; a single power law on a subsampled array is not enough.

**Dynamic range.** [Kinouchi & Copelli 2006 *Nature Physics*] proved analytically in a branching-process model of sensory cortex that the dynamic range — the ratio of saturating to just-detectable stimulus — is *maximised* precisely at the critical point σ = 1. This is a functional, not spectroscopic, signature and is arguably the most theoretically-motivated reason to care whether a neural network sits at criticality. [Shew et al. 2009 *J. Neurosci.*] tested the prediction empirically in cortical slice, pharmacologically pushing the network subcritical (bicuculline block of GABA-A) and supercritical (picrotoxin excess excitation) and demonstrating an inverted-U relationship between dynamic range and distance-from-criticality, peaked exactly at the condition where avalanches followed the 3/2 power law.

**Mutual information, information transmission, capacity.** [Shew et al. 2011 *J. Neurosci.*] extended the dynamic-range story to information-theoretic measures: mutual information between stimulus and cortical response was maximised at criticality, as was the *entropy* of the response distribution. These predictions have theoretical backing from the statistical physics literature on critical Ising-like models, in which the susceptibility (and hence the information capacity in linear response) diverges at T = Tc.

**Integrated information, synergy, coalition entropy.** A separate, more Tononi-flavoured literature (integrated information theory, Φ [VERIFY Tononi 2008 *Biol. Bull.*]) has argued that information integration — the irreducibility of whole-system entropy to sum-of-parts — peaks near criticality. [Timme et al. 2016] [VERIFY] reported empirical peaks of partial-information-decomposition synergy measures near σ ≈ 1 in cortical cultures. *Coalition entropy* and *perturbational complexity* [Casali et al. 2013 *Sci. Transl. Med.*] have been used as clinical indices of consciousness, and loss of consciousness (anaesthesia, NREM sleep) is associated with a retreat from criticality — a convergence line we return to in Theme 6.

**Long-range temporal correlations and DFA.** [Linkenkaer-Hansen et al. 2001 *J. Neurosci.*] introduced Detrended Fluctuation Analysis (DFA) as a tool to measure long-range temporal autocorrelations in amplitude envelopes of cortical oscillations. Scaling exponents 0.5 < H < 1 (persistent long-memory correlations) are ubiquitous in healthy human EEG/MEG and are the hallmark of 1/f^α noise, itself a classic fingerprint of self-organized criticality [Bak, Tang & Wiesenfeld 1987 *PRL*]. DFA is attractive because it is relatively robust to non-stationarity and does not require event-detection thresholds; it is, however, *not* a clean criticality test — long-range correlations are generated by many non-critical mechanisms (fractional Brownian motion, long-tailed inter-event intervals).

**In vivo network avalanches.** [Hahn et al. 2017 *Cell Reports*] [VERIFY] extended the avalanche framework to simultaneously-recorded cortical populations *in vivo* across brain states, showing that the avalanche profile shrinks but does not disappear during anaesthesia — again pointing to a reversible distance-from-criticality that tracks functional state.

No single signature is decisive. Best practice is to report at least *avalanche size and duration exponents*, *exponent relation γ*, *branching ratio (MR-corrected)*, and at least one functional measure (dynamic range or mutual information) on the same dataset. ML replications should do the same.

---

## Theme 4. Competing interpretations and criticisms

The critical-brain literature is not uncontested, and any ML-side project that hopes to survive peer review must engage seriously with the main counter-arguments.

**Power laws are cheap.** [Touboul & Destexhe 2010 *PLoS ONE*] [VERIFY] — the single most cited critical response — showed that *stochastic* neural-activity models with no critical bulk can generate apparently-power-law avalanche distributions over 2–3 decades, the range typically fit in experiment. More pointedly, they demonstrated that a Poisson process with an appropriate rate can pass the same eyeball log-log-plot test used to claim criticality in experimental data. They recommended formal goodness-of-fit (Theme 7). A later, gentler follow-up [Touboul & Destexhe 2017] argued that many critical-brain claims survive formal tests but that reporting must include them.

**The subsampling artefact as a null.** [Priesemann et al. 2013] is cited in Theme 2 as the foundational work on subsampling; it is equally cited as a *criticism* — subsampled networks that are in fact subcritical can look critical on avalanche statistics, and subsampled networks that are in fact critical look subcritical on branching-ratio statistics. The direction of bias depends on the metric, which is uncomfortable.

**"Critical-like" versus truly critical.** [Martinello et al. 2017 *PRL*] and [di Santo et al. 2018 *PNAS*] introduced the notion of **Griffiths phases**: extended *regions* of parameter space, not just isolated points, in which a disordered system exhibits scale-invariant behaviour resembling criticality but without fine-tuning. Heterogeneous, modular neural networks are natural candidates for Griffiths phases. The operational implication: the canonical 3/2 exponent can arise across a wide range of parameters in a quenched-disorder network, so observing it does *not* imply the network is poised at a single critical point. This is probably the most intellectually serious alternative to strict SOC in cortex and is underappreciated in ML criticality work.

**Stochastic up-down / bistability.** Cortical populations spontaneously alternate between up-states (depolarised, active) and down-states (hyperpolarised, silent). [Millman et al. 2010 *Nature Physics*] [VERIFY] showed that up-state dynamics alone can produce power-law-like avalanches via a mechanism closer to quasi-periodic bistability than to genuine SOC.

**Subsampled critical = genuinely subcritical?** A recurring debate: is cortex *at* σ = 1 but appearing σ ≈ 0.98 due to finite-sample bias, or is it *genuinely* at σ ≈ 0.98, slightly subcritical by design? [Wilting & Priesemann 2018] argued for the latter on theoretical grounds (robustness, avoidance of runaway activity), while others have argued that the residual gap is methodological.

**Universality class identification.** Even granting criticality, which universality class? Mean-field directed percolation (MF-DP) gives α = 3/2, β = 2 in the appropriate mean-field limit; so does the mean-field branching process; so do a handful of other classes. Exponent coincidence is not class identification. [Villegas et al. 2019] [VERIFY] argued that cortex may be in a non-MF-DP class; resolving this requires higher-dimensional scaling data than any current experiment provides.

**Take-home.** Power-law avalanches, branching ratio near 1, and long-range temporal correlations are each *individually* consistent with many non-critical or only-marginally-critical mechanisms. The critical-brain claim is strong only when multiple signatures converge *and* the crackling-noise exponent relation is satisfied *and* subsampling bias is controlled *and* a Griffiths-phase explanation has been excluded. Most ML-side replication attempts check one or two of these. A programme that checks all of them would be genuinely novel.

---

## Theme 5. Functional consequences of criticality

If criticality is real, does it matter? The functional case rests on a small number of measurable advantages.

**Information transmission and storage.** [Shew et al. 2011 *J. Neurosci.*] measured mutual information between stimulus sequences and cortical-slice responses, and found a single peak at the pharmacological condition producing α ≈ 3/2 avalanches. The peak in mutual information is quantitatively substantial (factors of 2-3 relative to moderately subcritical conditions). [Beggs 2008] surveyed the theoretical case that information transmission, information storage, and computational capacity are jointly optimised near σ = 1.

**Dynamic range.** [Kinouchi & Copelli 2006] — the analytic calculation — predicts dynamic range diverges logarithmically with N at σ = 1 in a branching-process model of sensory input. [Shew et al. 2009] is the experimental test: pharmacologically manipulated cortical slices show a precise inverted-U in dynamic range vs distance-from-criticality.

**Computational capacity.** At the interface of this literature with the dynamical-systems / reservoir-computing literature (covered in the physics/ML half) is the claim that computational capacity — the ability of a recurrent network to solve a benchmark task — peaks at the edge of chaos. [Bertschinger & Natschläger 2004 *Neural Comp.*] is the canonical reference on the ML side; the neural equivalent is the Shew & Plenz line.

**Pharmacological manipulation.** The neatest experimental demonstration that criticality is a *controllable* variable is pharmacological. [Shew et al. 2010 *J. Neurosci.*] perturbed cortical slices with GABA-A antagonists (reducing inhibition, pushing supercritical) and AMPA antagonists (reducing excitation, pushing subcritical) and demonstrated smooth, reversible movement along the criticality axis. Functional measures (dynamic range, MI) moved in lockstep, peaking at the pharmacological E/I balance associated with α ≈ 3/2.

**Human and clinical validation.** [Fagerholm et al. 2015 *J. Neurosci.*] demonstrated that altered states of consciousness (psilocybin, ketamine) shift human MEG-derived criticality metrics, with behavioural correlates; the direction of shift depends on the drug's excitatory/inhibitory profile.

The functional case is, on the whole, *suggestive rather than decisive*. The gap between "mutual information is modestly higher near criticality" and "cortex is tuned to criticality because evolution optimised for information transmission" is substantial; the intermediate claim — that evolution needs only to avoid the dead subcritical regime and the epileptic supercritical one, with a broad maximum in between — is arguably more defensible.

---

## Theme 6. Developmental, sleep, pathology

Longitudinal and cross-state measurements give the critical-brain hypothesis most of its *quantitative* predictive content: criticality metrics should follow specific trajectories during development, sleep, and disease.

**Development.** [Gireesh & Plenz 2008 *PNAS*] showed that cortical cultures drift *toward* criticality during the first two weeks *in vitro*, with avalanche exponents sharpening toward 3/2 as synaptic connectivity matures. [Tetzlaff et al. 2010] [VERIFY] built a homeostatic-plasticity model in which the critical fixed point is the stable attractor of local plasticity rules — a theoretical justification for why criticality should be a *developmental* endpoint rather than a fine-tuned point.

**Sleep and wake.** [Meisel et al. 2013 *PLoS CB*] and [Meisel et al. 2015 *J. Neurosci.*] [VERIFY] showed that sleep deprivation pushes human EEG-derived criticality measures *past* the critical point toward supercritical, and that recovery sleep restores the pre-deprivation state. This is consistent with the synaptic-homeostasis hypothesis [Tononi & Cirelli 2014 *Neuron*]: wake potentiates synapses, pushing the network toward runaway activity; sleep renormalises.

**Epilepsy.** [Meisel 2015] and others have argued that epilepsy is the clinical instantiation of a supercritical transition. Interictal periods retain near-critical statistics; seizures are the runaway event. This framing has motivated attempts to use branching-ratio estimators as *seizure-prediction* features.

**Schizophrenia.** [Hobbs et al. 2010] [VERIFY] reported altered avalanche statistics in medial prefrontal cortex of a mouse model of the 22q11 deletion, a genetic risk factor for schizophrenia, showing that dopaminergic perturbation shifts avalanche exponents.

**Clinical signatures more broadly.** [Zimmern 2020 *Front. Phys.*] [VERIFY] is a useful integrative review: criticality metrics differ between healthy and diseased populations across Alzheimer's, Parkinson's, depression, and schizophrenia, in roughly the direction predicted by the excitation/inhibition-balance hypothesis. Caveats — effect sizes are modest, single-signature reliance is common, and subsampling controls are rare in the clinical literature.

**The two-axis picture.** Taken together, these studies support a two-dimensional state-space for cortex: a *criticality axis* (subcritical–critical–supercritical) orthogonal to an *arousal axis* (asleep–awake–hyperaroused). Brain state trajectories can be mapped on this plane.

---

## Theme 7. Methodology and software

All of the above is only as reliable as the statistical methodology. The field has undergone a quiet methodological revolution between roughly 2009 and 2020.

**Power-law goodness-of-fit.** The indispensable reference is [Clauset, Shalizi & Newman 2009 *SIAM Review*]. They argue that visual log-log plots are essentially uninformative, and lay out a three-step protocol: (i) maximum-likelihood estimation of the exponent α conditional on a lower cut-off x_min, (ii) selection of x_min by Kolmogorov-Smirnov minimisation between empirical and fitted CDF, (iii) *bootstrap goodness-of-fit*: simulate many synthetic power-law datasets from the fitted parameters, compute KS statistics, and compare to the empirical KS. A p-value > 0.1 is weak evidence for consistency with a power law; anything less is evidence *against*. Most avalanche datasets published before 2009 would fail this test if re-analysed. [Deluca & Corral 2013 *Acta Geophysica*] [VERIFY] offered a complementary formal treatment and is widely used in the SOC / geophysical literature.

**Comparison with alternative distributions.** Clauset et al. also argue for explicit likelihood-ratio comparison against log-normal, stretched exponential, and truncated power-law alternatives. Many cortical avalanche distributions are statistically better-fit by truncated power laws or log-normals; the presence of a finite cut-off is *not* a refutation of criticality (finite-size scaling predicts one), but the burden shifts to demonstrating that the cut-off scales appropriately with N.

**The MR estimator.** [Wilting & Priesemann 2018] is the canonical citation for subsampling-corrected branching-ratio estimation. The method requires stationarity, a single dominant eigenvalue, and adequate time resolution; violations produce biased estimates. The associated software package **Mrestimator** [Spitzner et al. 2018 *PLoS ONE*] [VERIFY] provides Python and Matlab implementations with bootstrap confidence intervals.

**Avalanche detection.** Choices: (a) temporal bin width — usually ⟨ISI⟩ but this depends on state; (b) threshold — typically 2–3 SD above noise, but exponents drift with threshold; (c) inclusion of "off" bins of width greater than one — affects whether close events are merged; (d) handling of multi-electrode coincidences. [Marshall et al. 2016] [VERIFY] and the **Neural Complexity and Criticality (NCC)** toolbox document best practices. The **avalanche_analysis** Python package (various authors) is widely used.

**Exponent-relation test.** Reporting α alone is insufficient. Minimal standard: report α, β, γ and check γ = (β−1)/(α−1) within bootstrap error bars [Friedman et al. 2012 *PRL*].

**Surrogate controls.** Shuffling spike times within-neuron (destroying cross-neuron correlations) is the minimal surrogate; it should destroy the power-law signature. Preserving temporal autocorrelation while breaking inter-neuronal correlations is a stronger control. [Priesemann et al. 2014 *Front. Syst. Neurosci.*] discusses protocols.

**Open data and reproducibility.** The field has been slow to adopt open data standards. The **CRCNS** archive hosts some cortical-avalanche datasets; the **Allen Brain Observatory** publishes large-scale two-photon and Neuropixels data; the **DANDI** archive hosts NWB-format neural datasets including Neuropixels recordings relevant to avalanche analysis.

**Bottom line for ML replications.** Any pipeline that computes avalanche statistics on a neural-network's activations must (i) use ML-estimated α with x_min by KS, (ii) bootstrap the goodness-of-fit p-value, (iii) compare against log-normal and truncated-power-law alternatives, (iv) report α, β, γ together with the exponent-relation check, (v) include surrogate shuffling controls, and (vi) sweep the analysis choices (threshold, bin width) to demonstrate robustness. Otherwise the result is unpublishable in a field that has moved past log-log eyeballing.

---

## Stylised facts

**Robustly known (high confidence, multiple independent lines of evidence):**

- **Power-law-*like* avalanche size distributions exist** in cortical slice, culture, and awake in vivo, with exponents near α ≈ 3/2 and β ≈ 2 [Beggs & Plenz 2003; Petermann 2009; Shriki 2013; Friedman 2012].
- **The crackling-noise exponent relation γ = (β−1)/(α−1) holds** within bootstrap error in multiple cortical datasets [Friedman 2012], giving the criticality claim multi-exponent support rather than single-exponent coincidence.
- **Dynamic range is maximised at pharmacological conditions producing α ≈ 3/2** [Shew et al. 2009], consistent with the Kinouchi-Copelli prediction.
- **Criticality metrics track brain state**: they shift reproducibly with sleep/wake [Meisel 2013, 2015], pharmacology [Shew 2010; Fagerholm 2015], and development [Gireesh & Plenz 2008].
- **The naïve branching-ratio estimator is severely biased under subsampling** [Priesemann 2013; Wilting & Priesemann 2018]. The MR estimator is the field-standard correction.

**Contested (active debate, depends on methodology):**

- Whether cortex is *at* criticality or *slightly subcritical* ("reverberating regime", σ ≈ 0.98). [Ma et al. 2019] and [Wilting & Priesemann 2018] favour the latter; others argue the gap is methodological.
- Whether the apparent universality is genuine mean-field-DP or a **Griffiths phase** in a heterogeneous quenched-disorder network [Martinello 2017; di Santo 2018].
- Whether functional consequences (information transmission, dynamic range) are *caused* by criticality or are *correlated* with it via shared pharmacological drivers.
- Whether the statistics are robust to state changes within a single recording, or require explicit non-stationary models.

**Methodologically fragile (high risk of false positives):**

- **Subsampling bias** — the single biggest pitfall. Naïve branching-ratio estimation on sparse recordings systematically underestimates σ, and avalanche-exponent estimation is threshold-dependent in subsampled data.
- **Log-log eyeballing** — without Clauset-Shalizi-Newman bootstrap, heavy tails look like power laws even when they aren't.
- **Bin-width and threshold dependence** — many reported exponents would shift by >0.2 if these were re-selected.
- **Absence of surrogate controls** — many older papers do not include even the minimal within-neuron shuffle.
- **Universality-class inference from exponents alone** — α ≈ 3/2 is compatible with several classes and with Griffiths phases.
