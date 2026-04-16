# Blind Reviewer Report — ie_lda_delivery (RETROACTIVE Phase 2.75)

**Paper**: "How Much Housing Does the Land Development Agency Actually Deliver?"
**Reviewer**: blind external (methodology-only pass)
**Date**: 2026-04-15
**Decision**: **MAJOR REVISIONS** — the headline figures in this paper are not supported by the cited source and one key number is internally inconsistent with arithmetic performed elsewhere in the same paper.

---

## Summary

The paper's central empirical claim — "roughly 4,500 homes cumulative 2018-2025, 4.3% of 2025 national completions" — relies on a table in which **six of eight annual LDA delivery figures are not from any audited source**, the one "audited" figure (854 in 2023) is a false-precision rendering of the LDA's own word "ca. 850", the pre-2023 breakdown appears to have been reverse-engineered from a single Irish Times cumulative figure, and the denominator (national completions) is different from the figures used in the companion `ie_housing_pipeline` project for the same years. At least one headline ratio in the paper (4.3%) is therefore the quotient of two unverified numbers.

This is the kind of paper where, if the referee were to be pedantic, the conclusion might survive; but the evidence chain as written does not. Accept only with the mandated experiments R1–R4 completed AND the headline table substantially redrawn.

---

## Top concerns, in order of severity

### 1. The "854" headline number is not in the LDA 2023 annual report (CRITICAL)

The author's code comment says `# 2023 from LDA report`, and the paper bolds **854** as the audited 2023 figure. A full-text search of the extracted `lda_2023.txt` turns up ZERO occurrences of the string "854". The LDA 2023 annual report in fact says:

- "**ca. 650** Cost Rental homes delivered via Project Tosaigh during 2023"
- "**ca. 200** Affordable for Sale homes delivered via Project Tosaigh"
- "Delivering **ca. 850** homes" (summary headline)

The paper's "854" is therefore (a) not traceable to the annual report and (b) false precision on a number the LDA itself reports as an approximation ("ca. 850"). The author appears to have taken "ca. 850" and replaced it with "854" — either copying from a different secondary source, or fabricating precision. Neither is acceptable in an evidence column labelled "from LDA report".

**Mandated fix (R1)**: Replace "854" with "~850 (ca. 650 cost rental + ca. 200 affordable-for-sale, via Project Tosaigh)". Note that this was ENTIRELY Project Tosaigh acquisition/forward-purchase, not direct LDA construction — the report explicitly states Shanganagh's first direct-delivery homes will come in 2025. This tenure/mode distinction is load-bearing and the current paper hides it.

### 2. The pre-2023 annual breakdown is reverse-engineered, not sourced (CRITICAL)

The 2018–2023 rows in Table 1 sum to exactly **2,054** — the exact number the paper attributes to an Irish Times September 2025 report as "cumulative through end-2024". Two possibilities:

- (a) The Irish Times figure is really cumulative through end-2023, not end-2024 — in which case the paper mis-cites the source, AND the 2024 estimate of ~1,000 is then unsupported, AND the 2018–2022 annual breakdown (0, 100, 200, 350, 550) was back-fit to sum to 2,054 − 854 = 1,200.
- (b) The Irish Times figure really is end-2024 = 2,054 — in which case the paper's own table (which sums to 3,054 through end-2024) is inconsistent with the source the paper cites, by exactly 1,000 homes. The 2024 row is double-counted or the pre-2024 rows are inflated.

Either way, the annual breakdown 2018–2022 is not evidence, it is arithmetic padding. The paper must either (i) cite the Irish Times article properly and reconcile, or (ii) drop the annual breakdown and present only cumulative figures with explicit uncertainty.

**Mandated fix (R3)**: The pre-2023 figures must be downgraded to "author estimates, not audited" in the table itself, not just in an appendix. Or they must be sourced. "Estimates calibrated to a single secondary source" is not a pass at Phase 2.75.

### 3. National completions denominator is inconsistent with companion project (HIGH)

The paper states "National completions from CSO NDA12." The companion `ie_housing_pipeline` project uses NDA12 too, but gets very different numbers for the same years:

| Year | ie_lda_delivery paper | ie_housing_pipeline (NDA12, towns only) | Difference |
|---:|---:|---:|---:|
| 2018 | 17,990 | 13,649 | +4,341 |
| 2022 | 30,009 | 22,704 | +7,305 |
| 2023 | 32,695 | 24,316 | +8,379 |
| 2024 | 30,330 | 22,136 | +8,194 |
| 2025 | 35,000 | 25,237 | +9,763 |

The companion project filters NDA12 to the 867-towns aggregate (which excludes rural completions, so is a lower bound); the LDA paper's figures look like the CSO NDQ09 "all areas" headline. Whichever the author actually used, the paper's source attribution ("NDA12") is wrong relative to the companion project's use of the same name. This matters because the 4.3% share of 2025 completions would become ~5.9% if the companion project's 25,237 denominator were used.

**Mandated fix (R2)**: Reconcile which CSO table is the correct national total, restate using the same table as `ie_housing_pipeline`, and present BOTH the NDA12-towns and NDQ09-all-Ireland denominators explicitly.

### 4. 2025 figures are pure guess and should not carry three-significant-figure precision (MEDIUM)

The 2025 row (1,500 LDA delivered, 35,000 national completions, 4.3% share) is presented in the same table as "audited" 2023 figures with no uncertainty markers. The reader cannot tell that the 4.3% headline ratio is a ratio of two estimates. The blurb and section 2 quote "4 percent of the national total" as a confident empirical finding. It is not; it is an estimate-of-an-estimate.

**Mandated fix (R4)**: Restate the national-share comparison only for the years where both numerator and denominator are audited — i.e., 2023 (which is the only such year). For 2024 and 2025, use range bands or explicitly mark as "provisional author estimate".

### 5. Minor / structural

- The paper conflates "LDA delivered" with different delivery modes (direct-build Shanganagh, Project Tosaigh forward-purchase, cost-rental acquisition). Per the 2023 annual report, 100 percent of 2023 output was Project Tosaigh acquisitions — i.e., homes built by the private sector and bought by the LDA, NOT additional supply. This matters enormously for the "share of national completions" framing, because Project Tosaigh homes are *already counted* in the national completions total. The paper is therefore double-counting LDA output within the national denominator. This is a structural error, not a rounding one.
- The "14,000 by 2028" internal LDA target cited in §2.3 is not sourced to the annual report text. The report's forward language talks about "8,000 homes by 2028" in one passage and "a pipeline of over 10,000" elsewhere. The 14,000 number requires a citation.
- "3,500 per year by 2027" is cited with no source.
- "Project Tosaigh delivered 650 cost-rental homes in 2023 alone and is expected to continue at rising pace" — the "rising pace" claim is editorial, not evidential, and the report in fact states the direct-delivery stream is expected to overtake Project Tosaigh, implying Project Tosaigh output may fall, not rise.

---

## Mandated experiments (all MUST be completed before green-light)

- **R1 [CONTROL]** — Re-extract the 2023 LDA delivery number directly from `data/raw/lda_2023.pdf` text. Replace "854" with "ca. 850" and break down by Project Tosaigh cost-rental (~650) vs Project Tosaigh affordable-purchase (~200). Confirm zero direct-build completions in 2023. Update table, prose, and code comment.

- **R2 [DIAG]** — Reconcile the national-completions denominator against the `ie_housing_pipeline` NDA12 series. Produce a reconciliation table in `discoveries/national_completions_reconciliation.csv` showing NDA12-towns vs NDQ09-all-Ireland side by side for 2018–2025, and select one canonical series for the paper. Cite the specific CSO table ID + access date. If `ie_housing_pipeline` is wrong, fix that project too.

- **R3 [RUN_RV]** — Downgrade pre-2023 annual figures to "author estimate" (italicised in the table or marked with †) OR source them from the LDA 2018, 2019, 2020, 2021, 2022 annual reports individually. (The LDA did not publish an annual report before ~2020 in any case, so this may force the author to drop those rows.) Reconcile the 2018–2024 cumulative against the Irish Times figure and state which year it covers.

- **R4 [CONTROL]** — Restate the LDA share of national completions ONLY for years where both numerator and denominator are audited — likely 2023 alone. For 2024/2025 give a range, not a point estimate. Remove "4.3%" from the blurb and replace with a bracketed range or drop entirely. Also, account for the double-count (Project Tosaigh homes are already in the national denominator) — either net them out or add a prominent caveat.

- **R5 [NEW — recommended]** — Re-examine the "14,000 by 2028" internal target. Cite it. If the LDA's own forward language is inconsistent (8,000 in one place, 10,000+ pipeline elsewhere, 14,000 cumulative in another), present all three and let the reader see the range.

---

## Decision

**MAJOR REVISIONS.** The paper's thesis — that the LDA is a structurally minor contributor to Housing for All — is probably correct directionally, and surviving the revisions above will not change that qualitative conclusion. But the current evidence base is not sound: the key audited number is a misquote, the pre-audited years are back-fit to a single secondary source, the denominator is inconsistent with the companion project, and there is a structural double-counting issue (Project Tosaigh homes appear in both the numerator and denominator of the "share" calculation). Until R1–R4 are executed the paper should not be linked from the website or included in the results table. R5 strengthens but is not strictly blocking.

Estimated effort to revise: 4–6 hours if the LDA prior-year annual reports (2019–2022) are accessible; 1–2 hours if they are not and the author accepts dropping the pre-2023 breakdown entirely.
