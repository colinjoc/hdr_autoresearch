# Review Sign-off: Structural Decomposition of the Urania type8 Family

**Date:** 2026-04-10

---

## Disposition of Findings

| ID | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| C1.1 | CRITICAL | Candidate mechanism not quantitatively validated | Added back-of-envelope arm-length calculation (~24 km vs ~8 km, ratio ~3.0x); softened language from "most plausible explanation" to "strongest candidate mechanism"; explicitly noted quantitative confirmation requires numerical reconstruction | RESOLVED -- downgraded to acknowledged limitation |
| C1.2 | MAJOR | Conflation of structural absence with mechanism exclusion | Softened exclusions for radiation-pressure and multi-arm mechanisms; kept strong exclusion for balanced-homodyne (unambiguous) | RESOLVED |
| C1.3 | MINOR | 3.12x comparison unexplained | Added footnote documenting provenance (lost reconstruction artifact) | RESOLVED |
| C2.1 | MAJOR | No ablation study | Strengthened limitation acknowledgment; added multi-pass caveat | ACCEPTED as limitation -- cannot be addressed without Finesse |
| C2.2 | MAJOR | Pearson correlation with outlier sensitivity | Computed Spearman (stronger: rho=-0.53, +0.56), leave-one-out (survives), bootstrap CIs (exclude zero); added all to paper | RESOLVED -- correlations are robust |
| C2.3 | MINOR | Improvement metric not sensitivity-weighted | Added note about limitation; follows Krenn et al. convention | RESOLVED |
| C3.1 | MAJOR | Only sol00 deeply analyzed | Added discussion of sol01 comparison as priority future work | ACCEPTED as scope limitation |
| C3.2 | MAJOR | Reference numbering gaps/duplicate | Renumbered sequentially [1]-[21]; merged duplicate Caves citation | RESOLVED |
| C3.3 | MINOR | fsig as modeling convention vs physical feature | Investigated and found fsig targets exactly non-default-length spaces (grid convention); revised M09 to clarify; distinguished grid convention from optimiser-selected effective signal paths | RESOLVED |
| C4.1 | MAJOR | Abstract too long (~450 words) | Shortened to ~200 words | RESOLVED |
| C4.2 | MINOR | Inconsistent precision | Standardised | RESOLVED |
| C4.3 | MINOR | Experiment count discrepancy | No discrepancy -- results.tsv has 20 rows (E06-E25) matching paper text | NO ACTION NEEDED |
| C5.1 | MINOR | PyKat patches not distributed | Acknowledged; patches described in prose | ACCEPTED |
| C5.2 | MINOR | Differometor converter non-functional | Honestly disclosed in paper | ACCEPTED |
| C6.1 | MINOR | Structural analysis not new physics | Paper is explicitly framed as decomposition; back-of-envelope now provides partial positive evidence | ACCEPTED |
| C6.2 | MINOR | No comparison to AI decomposition literature | Acknowledged; brief discussion could be added in future revision | ACCEPTED |

## Summary

- **1 CRITICAL finding** resolved by adding quantitative back-of-envelope and softening language
- **6 MAJOR findings**: 4 resolved (correlations, references, abstract, exclusion language), 2 accepted as limitations (no ablation, incomplete topological coverage)
- **9 MINOR findings**: 6 resolved, 3 accepted
- **New experiments run**: Spearman correlations, leave-one-out robustness, bootstrap CIs, fsig convention investigation, back-of-envelope arm-length calculation
- **All 41 tests pass** after revisions

## Verdict

**APPROVED.** The paper's core contributions -- structural decomposition of the GWDetectorZoo type8 family, identification of over-parameterisation patterns, and elimination of four classical mechanisms -- are well-supported by evidence. The candidate mechanism (distributed signal injection) is now appropriately qualified as a candidate supported by a back-of-envelope calculation rather than a proven explanation. The correlations are robust to outlier analysis. The main limitation (no component-level ablation) is honestly acknowledged and cannot be resolved without the Finesse simulator. The paper is ready for publication as a decomposition study.
