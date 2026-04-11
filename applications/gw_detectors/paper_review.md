# Adversarial Review: Structural Decomposition of the Urania type8 Family of AI-Discovered Gravitational-Wave Detectors

**Reviewer:** Automated adversarial review (HDR cycle)
**Date:** 2026-04-10

---

## Category 1: Claims vs. Evidence

### C1.1 [CRITICAL] The candidate mechanism (distributed signal injection) is proposed but never quantitatively validated

The paper's central claim -- that sol00's 4.05x improvement comes from "distributed gravitational-wave signal injection across 26 free-space perturbation points" -- is presented as the "most plausible remaining explanation" after excluding four classical mechanisms. However, no numerical simulation, analytical model, or even back-of-envelope calculation is provided to show this mechanism *can* produce a 4x improvement. The paper acknowledges the Differometor converter is "off by a factor of approximately 10^6 in absolute scale" (Section 4.5), which means the quantitative pathway is completely blocked. The argument is therefore purely eliminative: "it's not X, Y, Z, or W, so it must be this." Eliminative reasoning is valid only if the candidate list is exhaustive, which is not demonstrated.

**Specific gap:** The paper claims the "multiplicity (26 injection points versus 2 in a conventional dual-arm Michelson) is the geometric factor that the optimiser found" (Section 4.1). But no derivation is given for how 26 injection points translate to a 4x improvement. A naive signal-accumulation model would predict improvement proportional to sqrt(26/2) ~ 3.6x, which is suspiciously close to 4.05x but is never stated or tested. If this is the intended argument, it should be made explicit and its assumptions examined.

### C1.2 [MAJOR] The paper conflates "not present in sol00" with "excluded as a mechanism"

Several exclusions are stated in absolute terms but rest on structural absence, not on demonstrated irrelevance. For example:
- "Balanced-homodyne classical-noise rejection is excluded" (Section 3.8, M01) -- this is well-supported; one port is genuinely orphaned.
- "Voyager-style radiation-pressure suppression is excluded" (M03) -- the argument is that the 200-kg mirrors sit on transparent components. But radiation pressure noise suppression in an interferometer depends on all test masses in the optical path, not just the named "200-kg" ones. The 18 mirrors below 50 kg that *are* in the optical path could still be contributing to radiation-pressure effects. The exclusion is too sweeping.
- "Multi-arm Fabry-Perot averaging is excluded" (M02) -- only 1 of 6 arm-class spaces is a symmetric cavity, but the asymmetric cavity (mRL_3_4, R_A=0.953, R_B=0.081) and the one-sided wall (mUD_2_1, R_A=0.086, R_B=1.0) are both optically non-trivial. They are not high-finesse cavities, but they are not nothing either. The exclusion should be more nuanced.

### C1.3 [MINOR] The 4.05x vs 3.12x comparison is not explained

The abstract claims "substantially higher than artifact-derived prior claims of 3.12x" but never explains what the 3.12x value was, where it came from, or why it was an artifact. This should either be documented or removed.

---

## Category 2: Methodology

### C2.1 [MAJOR] No ablation study despite claiming component-level findings

The paper identifies specific components as "filler" (29 of 57 mirrors, 11 of 13 beamsplitters, 50 of 78 spaces) but never removes them and re-runs the simulator to confirm they are non-load-bearing. Section 4.5 acknowledges this, but the paper still draws strong conclusions from structural analysis alone. Specifically: "the optimiser has either decided they should not exist or that they should function as fixed boundary conditions" (Section 3.3) -- but this is speculation, not measurement.

The paper's own criteria for "filler" (R < 0.001 or R > 0.999) are chosen thresholds, not physically justified cutoffs. A mirror at R = 0.0009 transmits 99.91% of light, which sounds "transparent," but in a multi-pass configuration the cumulative effect of many near-transparent elements could be significant. This is never addressed.

### C2.2 [MAJOR] Pearson correlation on 25 data points with a dominant outlier

The cross-family correlations (Section 3.6) are computed as Pearson r values on 25 data points, with sol00 as a massive outlier (4.05x vs median 1.11x). Pearson correlation is sensitive to outliers; the reported r = -0.50 for squeezers and r = +0.51 for transparent mirrors could be driven entirely by sol00 (which has 0 squeezers and 20 transparent mirrors). The paper should report:
1. Spearman rank correlation (robust to outliers)
2. Correlation with sol00 removed
3. Confidence intervals on the correlation coefficients

Without these, the "more squeezers = worse performance" claim is not adequately supported.

### C2.3 [MINOR] The improvement factor metric is not sensitivity-weighted

The log-space-averaged improvement factor (Section 2.2) treats all frequencies in 800-3000 Hz equally. But gravitational-wave science targets often have specific frequency content (e.g., post-merger oscillation peaks near 2-3 kHz). A sensitivity-weighted metric using a representative source spectrum would be more physically meaningful. This is a minor concern since the paper follows the convention of Krenn et al., but it should be noted.

---

## Category 3: Completeness

### C3.1 [MAJOR] The topological analysis is incomplete -- only sol00 is deeply analyzed

The topological analysis (Section 3.8) -- phantom homodyne, arm cavity classification, signal injection pattern -- is performed only on sol00. The paper mentions briefly that "4 of the top 5 type8 solutions share this phantom-MDet pattern" but does not classify arm cavities, trace light paths, or identify candidate mechanisms for sol01-sol04. Given that sol01 achieves 3.36x with a different architecture (true balanced readout), comparing the sol00 and sol01 mechanisms would significantly strengthen the paper.

### C3.2 [MAJOR] Reference numbering has gaps and one duplicate

The reference list jumps from [5] to [8], skipping [6] and [7]. References [9] and [17] both cite Caves 1980 (Phys. Rev. Lett. 45, 75) for different purposes -- [10] is the Caves 1980 letter and [17] is labeled "squeezed-light proposal" but points to the same paper. Several citations in the text ([6], [7], [12], etc.) are not defined in the reference list. This is sloppy.

### C3.3 [MINOR] No discussion of whether the 26-fsig pattern is a Finesse modeling convention vs a physical feature

The 26 `fsig` signal injection points are described as physically meaningful (Section 3.8, M09) and central to the candidate mechanism. But in Finesse/PyKat, `fsig` declarations specify how the simulator *models* gravitational-wave coupling -- they are part of the simulation setup, not an inherent property of the detector topology. The paper should clarify whether the 26-point injection pattern is a consequence of the UIFO grid formalism (every free space automatically gets a signal injection) or a deliberate optimiser choice. If the former, then "distributed signal injection" is an artifact of the parameterisation, not a physical mechanism.

---

## Category 4: Writing Quality

### C4.1 [MAJOR] The abstract is 450+ words -- far too long

The abstract attempts to present all five findings with full quantitative detail and mechanism exclusions. This makes it nearly unreadable. An abstract should be 150-250 words presenting the key result and approach. The detailed findings belong in the body.

### C4.2 [MINOR] Inconsistent precision in reported values

Improvement factors are variously reported as 4.05x (2 decimal places), 1.10x (2 decimal places), and 1.00x (2 decimal places). But per_solution.tsv shows sol00 at 4.0488... -- the paper rounds to 4.05, which is fine, but the precision is inconsistent with the more precise values in the arm cavity classification table (e.g., R = 0.5186815e-01).

### C4.3 [MINOR] Section 3.7 lists 20 experiments but only discusses 8 in detail

Experiments E06-E25 are described as "20 hypothesis-driven experiments" but only a subset receive detailed discussion. The results.tsv has rows for E06-E25 (16 rows visible). The experiment count (20 in text vs 16 in TSV) should be reconciled.

---

## Category 5: Reproducibility

### C5.1 [MINOR] The PyKat cross-validation patch is described but not distributed

Section 2.1 describes three patches to restore PyKat on Python 3.12. These patches are described in prose but not provided as a patch file or script. For reproducibility, they should be included in the repository.

### C5.2 [MINOR] The Differometor converter is acknowledged as non-functional (10^6 scale error)

The kat-to-Differometor converter is described as "structurally complete" but off by 10^6. This is mentioned honestly in Sections 4.5 and 4.6, but it means that the single most important validation pathway -- independent numerical reconstruction of sol00's strain spectrum -- is blocked. The paper is transparent about this, so the rating is MINOR rather than MAJOR, but it significantly limits the paper's ability to confirm its central claim.

---

## Category 6: Novelty and Significance

### C6.1 [MINOR] The contribution is structural analysis, not new physics

The paper explicitly frames itself as a decomposition study, not a discovery paper. The five findings are about the Urania optimiser's behaviour (over-parameterisation, phantom detectors, squeezer anti-correlation) and about what sol00 is *not* (not a Fabry-Perot Michelson), rather than about what sol00 *is* (the candidate mechanism is unconfirmed). This is honest and appropriate for a first analysis, but the paper would be stronger if it could confirm at least one positive mechanism claim numerically.

### C6.2 [MINOR] No comparison to other AI-for-science decomposition work

The paper does not reference prior work on reverse-engineering AI-discovered scientific results. There is a growing literature on mechanistic interpretability of AI models and on decomposing AI-generated experimental designs. A brief discussion of how this work relates to that literature would strengthen the contribution.

---

## Summary

| Category | Critical | Major | Minor |
|---|---|---|---|
| Claims vs Evidence | 1 | 1 | 1 |
| Methodology | 0 | 2 | 1 |
| Completeness | 0 | 2 | 1 |
| Writing Quality | 0 | 1 | 2 |
| Reproducibility | 0 | 0 | 2 |
| Novelty/Significance | 0 | 0 | 2 |
| **Total** | **1** | **6** | **9** |

**Verdict:** The paper presents genuinely interesting structural findings about the GWDetectorZoo, and the eliminative analysis excluding four classical mechanisms is well-executed. However, the CRITICAL gap is the absence of any quantitative validation for the proposed candidate mechanism. The paper reaches too far in claiming "distributed signal injection" as the explanation when it has only shown that four other things are *not* the explanation. The six MAJOR issues (no ablation, outlier-sensitive correlations, incomplete topological coverage, reference errors, abstract length, and the radiation-pressure exclusion overreach) are all addressable. The paper should either confirm the candidate mechanism numerically or significantly soften the claim.
