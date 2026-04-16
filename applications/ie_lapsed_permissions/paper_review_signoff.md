# Phase 3.5 Signoff Review: PL-4 Lapsed Irish Planning Permissions

**Reviewer:** Independent Phase 3.5 signoff reviewer
**Date:** 2026-04-16
**Paper reviewed:** paper.md (post-R1-R10 revision)

---

## Verification checklist

### R1-R10 in results.tsv
- [x] R1: Join-failure audit -- present, match_rate_gap=0.356 (simple=88.6%, complex=53.0%)
- [x] R2: NRU>0 headline -- present, 9.49% [9.07%, 9.92%], n=18,403
- [x] R3: DCC format analysis -- present, DCC NRU>0 lapse=45.7%, n=315
- [x] R4: Exclude 2014-2015 -- present, 2016-2019 rate=24.8%, n=41,328
- [x] R5: Cluster-bootstrap CIs -- present, [4.39%, 15.65%], 13.3x inflation
- [x] R6: GBM without LA -- present, AUC=0.727 (full cohort), 0.583 (NRU>0)
- [x] R7: Description FP audit -- present, 15.0% conservative FP rate
- [x] R8: Cork reconciliation -- present, recovered 1,942 of 4,715 non-matches
- [x] R9: 0% LA validation -- present, all 5 LAs use 100% simple format
- [x] R10: Revised strata -- present, 72 reliable of 87 strata

All 10 experiments are in results.tsv with plausible values.

### Headline honesty

- [x] Abstract leads with 9.5% (NRU>0, 2017-2019), not 27.4% or 23.1%
- [x] Cluster-bootstrap CI (4.4-15.6%) is presented as the policy-relevant interval
- [x] 27.4% and 23.1% are explicitly labelled as upper bounds inflated by join failure
- [x] The phrase "should not be cited as lapse rates" appears in the abstract -- strong language, appropriate
- [x] Policy section revised from "roughly one-quarter" to "5-15%"
- [x] Previous estimate explicitly retracted

### Join-failure vs true-lapse distinction

- [x] Section 2.3 is a dedicated section on join-failure methodology (3 full paragraphs)
- [x] Format-driven match gap quantified (35.6pp)
- [x] LA-level correlation reported (r=0.675)
- [x] Cork County explicitly flagged as contributing 37% of all non-matches
- [x] 0% LA validation explains that 0% reflects format matching, not necessarily 100% commencement
- [x] Description FP rates reported in Section 2.4 with concrete examples

### GBM status

- [x] Model explicitly "retracted as a lapse predictor" (Caveat 6, Section 3.4)
- [x] AUC decomposition: 0.826 -> 0.727 -> 0.583 presented clearly
- [x] Feature importance showing 84.5% on la_enc cited as evidence of artefact
- [x] Original tournament table preserved for transparency but flagged as misleading

### Caveats

- [x] 10 numbered caveats covering all identified risks
- [x] Join-failure contamination acknowledged as unresolved even in NRU>0
- [x] Selection bias in commencement-timing statistics flagged
- [x] Right-censoring for 2019 noted
- [x] DCC outlier status (45.7% NRU>0) flagged as unconfirmed

### Change log

- [x] Section 9 maps all R1-R10 with experiment description and key finding
- [x] Each finding is concrete and quantitative

---

## Critical assessment

### Strengths of the revision

1. **The join-failure distinction is now load-bearing in the paper.** Section 2.3 is the longest subsection and properly frames the central methodological challenge before any results are presented.

2. **The headline is honest.** 9.5% with cluster-bootstrap CI [4.4%, 15.6%] is a defensible estimate. The wide CI is appropriate given the LA-level clustering.

3. **The GBM retraction is explicit and well-evidenced.** The three-step AUC decomposition (0.826 -> 0.727 -> 0.583) is the cleanest demonstration that the model was predicting data quality.

4. **The policy revision is material and appropriate.** "5-15%" is a fundamentally different message from "roughly one-quarter."

### Residual concerns (non-blocking)

1. **DCC NRU>0 rate of 45.7% (n=315) remains unexplained.** The paper correctly flags this as unconfirmed but does not attempt a DCC-specific format reconciliation. The small sample (315) means this could be volatile. This is a limitation, not a blocking issue.

2. **The cluster-bootstrap CI [4.4%, 15.6%] is very wide.** It spans from "trivial" to "meaningful." The paper does not take a position on which end is more likely. This is honest but limits the policy utility. Non-blocking: the width is a genuine reflection of uncertainty.

3. **The 0% LAs (R9) are slightly under-interpreted.** The paper says "not necessarily 100% commencement" but the evidence (all expired, zero unmatched) is actually consistent with near-100% genuine commencement for these small rural LAs. The paper could be slightly more confident here. Minor.

4. **R7 false-positive audit uses automated classification, not true manual review.** The audit uses regex patterns for "clearly residential" vs "clearly non-residential," which is a heuristic, not a human reading of each description. A true manual audit of 200 descriptions would be stronger. However, the 15% conservative FP rate is likely a lower bound on the true FP rate, so the paper's conclusion (that description-matching inflates rates) is directionally robust. Non-blocking.

5. **The paper still includes the full-cohort size-band table (Section 4.5) but states it is from "the NRU>0 subsample."** The size bands 1, 2-4, 5-49, 50+ are all NRU>0 by definition (since NRU is populated), but the table implicitly excludes the 0_or_na band. This is correct and clearly presented. No issue.

---

## Verdict

**NO FURTHER BLOCKING ISSUES**

The paper has addressed all 10 mandated experiments. The headline is revised to the clean 9.5% NRU>0 rate with cluster-bootstrap CI. The join-failure vs true-lapse distinction is the central framing of Section 2. The GBM is retracted with clear evidence. The policy claims use the revised rate. The caveats are comprehensive. The change log documents all R1-R10 findings.

The residual concerns (DCC unexplained, wide CI, automated R7 audit) are genuine limitations but do not constitute blocking issues. The paper is honest about what it knows and what it does not know.
