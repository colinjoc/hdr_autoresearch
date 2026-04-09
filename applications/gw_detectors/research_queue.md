# Research Queue — gw_detectors

**Status**: Phase 0 in progress. Hypotheses are seeded from the project goal and the seed-paper claims; each will be tightened, prioritised, and traced to specific `papers.csv` entries as the lit review fills in. Target: 20+ hypotheses by end of Phase 0.

Each entry: hypothesis, evidence trail, prior (probability the hypothesis holds before testing), proposed experiment.

---

## Decomposition hypotheses (Option C / type8/sol00)

### H01 — Most components in type8/sol00 carry no light
**Hypothesis**: A majority of the 48+ mirrors in the type8/sol00 UIFO carry less than 0.1% of the input carrier power and can be removed (set to transparent or to perfect reflector with no neighbour) without measurably degrading sensitivity.
**Evidence trail**: Krenn et al. 2025 explicitly state the UIFO grid is over-parameterised. The Differometor authors' bundled `uifo_800_3000.json` has 196 nodes for what is structurally a single Michelson with one or two arm cavities.
**Prior**: 80%
**Proposed experiment**: light-path tracing in Differometor, then component-level binary ablation.

### H02 — The arm-cavity finesse is a sharp narrow optimum
**Hypothesis**: Arm cavity input-mirror reflectivity in type8/sol00 sits at the impedance-matching condition for critical coupling. A ±5% deviation drops the strain improvement below Voyager.
**Evidence trail**: Standard Fabry-Perot cavity theory (Bond et al. 2017 Living Rev). The lost reconstruction's draft claimed this with a specific finesse of ~6100 — to be verified, not assumed.
**Prior**: 70%
**Proposed experiment**: parameter sweep over the highest-reflectivity mirror.

### H03 — The beamsplitter ratio in type8/sol00 sits on a broad plateau
**Hypothesis**: The main beamsplitter reflectivity has multiple values within 5% of optimal across a [0.5, 0.8] range. The original Urania optimisation arbitrarily picked a value within this plateau.
**Evidence trail**: Symmetry / dimensional argument: at fixed test-mass-mass and arm-finesse, the BS ratio mostly trades off radiation-pressure noise against shot noise, which is a smooth function with a broad peak.
**Prior**: 50%
**Proposed experiment**: BS reflectivity sweep over [0.5, 0.85].

### H04 — A re-optimised minimal design beats the original sol00
**Hypothesis**: After identifying the essential components (H01) and re-optimising broad-plateau parameters (H03), the simplified design improves on the original 3.12× by ≥ 5%.
**Evidence trail**: H01 + H03 imply Urania converged to a local optimum within an arbitrary basin. Local optima in broad plateaus admit easy improvement via post-hoc sweeps.
**Prior**: 50%
**Proposed experiment**: build minimal design from H01-essential components, sweep H03 parameter, compare strain.

### H05 — Squeezers in type8/sol00 carry negligible squeezing
**Hypothesis**: All 4 squeezer elements in the type8/sol00 UIFO have squeezing levels less than 1 dB. The "quantum noise reduction" of the design comes from optomechanical (ponderomotive) effects, not external squeezed-light injection.
**Evidence trail**: Optomechanical squeezing is a well-known effect (Kimble et al. 2001 PRD 65 022002). It can be confused with external squeezing in a parameterised search that includes both.
**Prior**: 60%
**Proposed experiment**: read squeezer levels from the loaded UIFO; ablate all squeezers and measure delta.

### H06 — A light test mass creates an optical-spring resonance in the post-merger band
**Hypothesis**: The end-mirror mass on at least one arm of type8/sol00 is significantly lower than Voyager's 200 kg, producing an optomechanical spring resonance in the 800–3000 Hz band.
**Evidence trail**: Buonanno-Chen 2002 PRD 65 042001 — signal-recycled interferometers as optical springs.
**Prior**: 65%
**Proposed experiment**: read test-mass mass from the loaded UIFO; sweep mass and characterise the resonance.

### H07 — Type8 solutions cluster into discrete mechanism families
**Hypothesis**: The 25 type8 solutions in the GWDetectorZoo are not all variants of a single mechanism. At least two families coexist: noise-suppression (dominant) and signal-amplification (secondary).
**Evidence trail**: Krenn et al. 2025 mention that the optimisation produces qualitatively different solutions for the same target.
**Prior**: 55%
**Proposed experiment**: classify each of the 25 type8 solutions by relative signal vs noise contribution to the improvement.

---

## Methodology / cross-validation hypotheses

### H08 — Differometor reproduces Voyager strain to within 0.1%
**Hypothesis**: Differometor's bundled `voyager()` setup reproduces the published Voyager strain noise spectrum (3.76e-25 /√Hz minimum near 168 Hz) to within 0.1%.
**Evidence trail**: Adhikari et al. 2020 (Voyager design paper) reports the published spectrum.
**Prior**: 90%
**Proposed experiment**: run Differometor's voyager() and compare against the published value.
**Status**: Already verified in the previous session — `verify_reconstruction.py` showed 3.764e-25 at 169.4 Hz. This is the only carry-over from the discarded reconstruction.

### H09 — Independent simulator cross-check changes the dominant mechanism interpretation
**Hypothesis**: Computing strain via Differometor (JAX, frequency-domain) and via Finesse (PyKat, time/frequency-domain) on the same UIFO design produces noise/signal decompositions that may disagree on which mechanism is dominant. Cross-validation is mandatory before publishing mechanism claims.
**Evidence trail**: Numerical conventions (e.g., where the 1/2π factor goes, how shot noise is normalised) differ across simulators.
**Prior**: 30%
**Proposed experiment**: run the same minimal design through both simulators, compare signal and noise spectra independently.

---

## Open questions (not yet hypotheses)

- Can the decomposition protocol developed for type8 generalise to type0/1/3/5/6/9/10 (other Zoo families)?
- Is the dominant noise-reduction mechanism transferable to lower frequency bands (broadband, inspiral) by scaling test mass and finesse?
- What engineering metrics (alignment tolerance, drift sensitivity, manufacturability) are excluded from the Urania objective and would change the optimum if included?
- Does any solution in the Zoo use a topology that does not reduce to a Fabry-Perot Michelson skeleton?

---

## Phase 0 progress
- 9 hypotheses listed (target: 20+)
- Each hypothesis has at least one paper trail entry (target: every hypothesis ≥1 paper)
- 6 hypotheses are decomposition (Option C); 2 are methodology; 1 is cross-validation
- Next: read seed papers in full, refine the priors, add 11+ more hypotheses from theme 4 and 7 of the lit review
