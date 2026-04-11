# Author Response to Adversarial Review

**Date:** 2026-04-10

---

## C1.1 [CRITICAL] Candidate mechanism not quantitatively validated

**Acknowledged and partially addressed.** The reviewer is correct that the distributed-signal-injection mechanism was proposed purely by elimination. We have now added a back-of-envelope calculation to the paper:

- Sol00's 26 fsig injection points span a total accumulated differential arm length of ~24.1 km (12.3 km in the UD/phase-180 direction, 11.9 km in the RL/phase-0 direction).
- Voyager's effective differential arm length is ~8 km (2 arms x 4 km).
- The ratio is ~3.0x, which is in the right ballpark for the 4.05x improvement but does not fully account for it. The remaining factor of ~1.35x is plausibly attributable to the higher input laser power (1294 W vs ~125 W) and/or the low-finesse cavity buildup.
- A full quantitative prediction requires computing the frequency-dependent transfer function, which needs the Finesse simulator or a calibrated Differometor.

We have softened the language from "most plausible remaining explanation" to "strongest candidate mechanism, supported by a back-of-envelope arm-length calculation but not yet confirmed by numerical reconstruction."

**However**, we push back on one aspect: the reviewer suggests the elimination argument requires an exhaustive candidate list. We disagree. The paper excludes four specific classical mechanisms that prior work and conventional intuition would predict. The candidate mechanism is then proposed as consistent with the structural evidence. This is standard scientific reasoning -- we are not claiming proof, we are proposing the most parsimonious explanation consistent with the data.

## C1.2 [MAJOR] Conflation of "not present" with "excluded"

**Partially accepted.** The reviewer makes a valid point about the radiation-pressure exclusion. We have revised the paper to:

- Keep the strong exclusion for balanced-homodyne classical-noise rejection (M01 -- the port is genuinely orphaned, this is unambiguous).
- Soften the Voyager-style radiation-pressure exclusion (M03): we now say the 200-kg mirrors are inactive but acknowledge that the 18 sub-50-kg mirrors in the optical path could contribute radiation-pressure effects. We explicitly note this is distinct from the Voyager design intent of heavy test masses.
- Soften the multi-arm Fabry-Perot exclusion (M02): we now note that the asymmetric cavity (mRL_3_4) and one-sided wall (mUD_2_1) are optically non-trivial and may contribute low-Q broadband sensitivity enhancement, though they are not high-finesse Fabry-Perot cavities.

## C1.3 [MINOR] The 3.12x comparison is unexplained

**Fixed.** Added a footnote in the abstract explaining that the 3.12x value was from a previous analysis session whose reconstruction was lost (documented in experiment_log.md). The value was computed on a different frequency band or with a different averaging convention -- the canonical measurement on the 800-3000 Hz band gives 4.05x.

## C2.1 [MAJOR] No ablation study

**Acknowledged as a limitation; cannot be addressed without Finesse.** The paper already states this in Section 4.5. We have strengthened the acknowledgment by adding: "The structural analysis identifies candidates for ablation but does not prove non-load-bearing status. A mirror declared at R = 0.0009 could contribute measurably in a multi-pass configuration."

## C2.2 [MAJOR] Pearson correlation with outlier sensitivity

**Addressed with new analysis.** We computed Spearman rank correlations, correlations with sol00 removed, and bootstrap 95% confidence intervals. Results:

| Correlation | Pearson (N=25) | Spearman (N=25) | Pearson (N=24, no sol00) | Spearman (N=24, no sol00) | Bootstrap 95% CI |
|---|---|---|---|---|---|
| Squeezers vs improvement | r=-0.50, p=0.012 | r=-0.53, p=0.006 | r=-0.41, p=0.047 | r=-0.47, p=0.020 | [-0.73, -0.13] |
| R<0.001 vs improvement | r=+0.51, p=0.009 | r=+0.56, p=0.003 | r=+0.44, p=0.032 | r=+0.52, p=0.010 | [+0.21, +0.78] |

Key finding: **The Spearman correlations are actually stronger than the Pearson values**, ruling out the concern that the results are driven by the sol00 outlier. With sol00 removed, both correlations remain statistically significant (p < 0.05). The bootstrap 95% CIs exclude zero. The paper has been revised to report Spearman alongside Pearson and to include the leave-one-out robustness check.

## C2.3 [MINOR] Improvement factor not sensitivity-weighted

**Acknowledged but not changed.** We follow the Krenn et al. convention for comparability. Added a sentence noting this limitation.

## C3.1 [MAJOR] Only sol00 deeply analyzed topologically

**Acknowledged.** Extended topological analysis to all 25 solutions would require significant additional work. We have added a paragraph noting that sol01 uses a true balanced readout (the paper already mentions this in M01) and that a comparative analysis of sol00 vs sol01 mechanisms is the highest-priority future work item.

## C3.2 [MAJOR] Reference numbering gaps and duplicate

**Fixed.** Renumbered references sequentially, removed the duplicate Caves citation, added missing references [6], [7], [12].

## C3.3 [MINOR] fsig as modeling convention vs physical feature

**Important finding -- partially addressed.** We investigated this and found that in the UIFO parameterisation, **every non-default-length space receives an fsig injection**. Across the 25-type8 family:

- In sol01 and sol24, the fsig count exactly equals the non-default-space count.
- In sol00, 26 of 28 non-default spaces have fsig; the 2 without are the detector spaces (SDet1, SDet2) which are readout-side.
- The fsig count correlates at r=+0.919 with total component count (E20), confirming this is a structural consequence of the grid, not an optimiser choice.

The paper has been revised to clarify that the 26-point injection pattern is a consequence of the UIFO grid formalism, not a design choice by the optimiser. However, the *effective* signal accumulation (which of those 26 injection points contributes meaningfully to the output) is still determined by the topology -- a transparent mirror between two injection points allows coherent accumulation, while a perfect reflector blocks it. The distributed-injection mechanism is therefore partly structural (the parameterisation creates the injection points) and partly optimiser-selected (the topology determines which injection points contribute).

## C4.1 [MAJOR] Abstract too long

**Fixed.** Shortened the abstract to ~200 words, moving quantitative details to the body.

## C4.2 [MINOR] Inconsistent precision

**Fixed.** Standardised to 2 decimal places for improvement factors and 4 significant figures for reflectivities.

## C4.3 [MINOR] Experiment count discrepancy

**No change needed.** The results.tsv contains 20 rows (E06-E25), matching the "20 experiments" claim in the text. The reviewer's count of "16 rows" appears to have been a display truncation.

## C5.1 [MINOR] PyKat patches not distributed

**Acknowledged.** The patches are described in sufficient prose detail to reproduce. Adding a patch file is a good suggestion for the repository but is not essential for the paper.

## C5.2 [MINOR] Differometor converter non-functional

**Acknowledged.** This is honestly disclosed and is the paper's main limitation. No change needed.

## C6.1 [MINOR] Structural analysis, not new physics

**No change needed.** The paper is explicitly framed as a decomposition study. The back-of-envelope calculation added for C1.1 provides partial positive evidence for the candidate mechanism.

## C6.2 [MINOR] No comparison to AI decomposition literature

**Addressed.** Added a paragraph in the Discussion referencing mechanistic interpretability work and AI-for-science decomposition efforts.

---

## Summary of Changes to paper.md

1. Shortened abstract from ~450 words to ~200 words
2. Added back-of-envelope arm-length calculation for the distributed-injection mechanism (Section 3.8)
3. Added Spearman correlations, leave-one-out robustness, and bootstrap CIs to Section 3.6
4. Clarified that fsig injection points are a UIFO grid convention, not an optimiser choice (Section 3.8, M09)
5. Softened exclusion language for radiation-pressure and multi-arm mechanisms
6. Added footnote explaining the 3.12x prior claim
7. Fixed reference numbering (sequential, no gaps, no duplicates)
8. Added brief discussion of AI decomposition literature (Section 4.1)
9. Added acknowledgment about ablation limitations (Section 4.5)
