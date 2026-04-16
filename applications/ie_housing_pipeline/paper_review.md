# Blind review — Irish housing pipeline paper

**Reviewer**: retroactive Phase 2.75 blind agent
**Date**: 2026-04-15
**Verdict**: **MINOR REVISIONS** — headline claims are defensible but several methodological caveats must be surfaced in the paper, not only in the script comments.

---

## 1. What works

- The headline finding (permissions flat 32–43k; completions doubled 15.9k → 25.2k; 2-yr conversion 41% → 65%) is reproducible from `pipeline_annual.csv` and matches the paper's Table 1 exactly.
- The policy framing (bottleneck = permission volume, not conversion) is well-supported by the observed data.
- The "What we cannot say" section is honest about case-level vs aggregate matching, cancellations, and tenure.
- Data integrity verified: BHQ15 has no missing quarters 2019Q1–2025Q4; NDA12 has zero null cells across 867 areas × 14 years × 4 house types. The "missing area-year" risk flagged in the review brief is **not realised** in this dataset.
- Double-count check verified: BHQ15 2019 totals are `Apartment=18,898 + All-house=19,563 = 38,461` ✓ matches paper. "Multi-development house units" is a **subset** of "All house units" (13,941 ≤ 19,563), and the script correctly excludes it. Flag resolved.

## 2. Required revisions (must fix before sign-off)

### R1. Cohort-mismatch disclaimer on 2-year conversion
The 2-yr conversion rate is a population-level ratio of completions in T+2 ÷ permissions in T. It is **not** a cohort-tracked conversion. Some 2019 permissions will complete in 2026; some 2022 completions reflect 2018 permissions (for which BHQ15 has no pre-2019 coverage). The rising conversion ratio could partly reflect a changing mix of fast-build apartment completions landing in the numerator against a stable permissions denominator — not genuinely higher follow-through. **Add one sentence to Table 1 footnote**: *"Ratios are population-level T+2 aggregates, not case-level tracking; pre-2019 permissions feeding 2020–2021 completions are not observed."*

### R2. Pre-2019 comparison is impossible — state it
The claim "the system is getting better at turning permissions into homes" rests on a 2019-start series. Without pre-2019 permissions, we cannot distinguish "improving pipeline efficiency" from "recovery from an unusually slow 2019–2021 build-out (COVID, raw-material disruption)." The completions doubling 2019 → 2025 is at least as consistent with **post-COVID catch-up of pre-2019 permissions** as with efficiency gains. Add this framing to §"What it means" before the "chokepoint" conclusion.

### R3. SHD vs Non-SHD comparison is not apples-to-apples
SHD = apartment-dominant 100+ unit schemes; Non-SHD = mixed single houses, scheme houses, and small apartments. Comparing 60,605 vs 63,218 units as if they were equivalent productivity is misleading. Either (a) normalise by scheme count, or (b) drop the SHD-vs-non-SHD volume comparison and limit §"SHD window" to a descriptive note that both streams cleared in roughly equal volume without a productivity inference.

### R4. "Permission-to-completion" pipeline omits commencement notices
CSO NHC01 (commencement notices) is the missing middle stage. The paper's §"How we did it" claims a permission-to-completion pipeline but measures only stages 1 and 3. Either (a) add commencement as a third stage, or (b) retitle to "permission-vs-completion" (comparison, not pipeline). The script docstring is honest; the paper headline is not.

## 3. Recommended (not blocking)

- **Bootstrap CI on conversion rate.** A block-bootstrap over quarters would let you put ±X pp on the 41% → 65% jump. Without it, the "substantial improvement" claim is a point estimate with no uncertainty quantification.
- **Expiry/lapse accounting.** Irish planning permissions lapse at 5 years. Cohort 2019 permissions have an observable lapse window closing 2024; the 5-yr conversion for 2019 is computable from current data and would strengthen the paper.
- **Sensitivity to 2-yr lag choice.** Show the 1-yr, 2-yr, 3-yr lagged ratios side by side; if the ranking of years is robust to lag choice, the finding is more credible.

## 4. Sign-off criteria

- [ ] R1 footnote added to Table 1
- [ ] R2 alternative explanation (COVID catch-up) acknowledged in §"What it means"
- [ ] R3 SHD comparison either normalised or softened
- [ ] R4 commencement stage added OR title retargeted
- [ ] (recommended) bootstrap CI or lag-sensitivity table

Once R1–R4 are actioned, the paper is acceptable. The core findings are sound; the issues are framing and disclosure, not computation.
