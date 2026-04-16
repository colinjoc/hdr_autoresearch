# Phase 3.5 Independent Signoff Review — ie_lda_delivery

**Paper**: "How Much Housing Does the Land Development Agency Actually Deliver?"
**Reviewer**: fresh-eyes independent signoff (Phase 3.5, not the Phase 2.75 reviewer)
**Date**: 2026-04-16
**Paper revision reviewed**: `paper.md` dated 2026-04-15
**Decision**: **NO FURTHER BLOCKING ISSUES**

---

## Scope of this signoff

Phase 2.75 (2026-04-15) issued MAJOR REVISIONS with five mandated experiments
(R1–R5) and a structural double-count caveat. This signoff re-verifies the
revision from scratch against primary sources, without assuming the Phase 2.75
reviewer's conclusions.

## Verification of mandated revisions

### R1 — replace "854" with "ca. 850" + tenure breakdown

- `grep 854 data/raw/lda_2023.txt` → **0 matches** (confirms "854" was never in the primary source).
- `grep 854 paper.md` → "854" appears only in §2 as a reference to *the earlier draft's error* ("The earlier draft of this paper reported the 2023 figure as '854'") and in §3 referring to the earlier draft's arithmetic (`2,054 − 854 = 1,200`). No headline claim uses "854" any more. Acceptable — these are historical callouts to the prior error, not live claims.
- Paper §2 lines 22–24 carry the verbatim report language ("ca. 650 Cost Rental", "ca. 200 Affordable for Sale", "Delivering ca. 850 homes"). All three strings verified in `data/raw/lda_2023.txt` at lines 129, 137, 149 respectively.
- The "100% Project Tosaigh, zero direct-build" framing (paper §2 line 26) is load-bearing and present. Shanganagh noted as first direct-build, expected 2025.
- **R1 satisfied.**

### R2 — two denominators side-by-side

- Paper §3 table (lines 38–44) presents both NDA12-towns and CSO all-Ireland denominators for 2023, 2024, 2025 with corresponding share columns.
- 2023: 850/24,316 = 3.495% → 3.5% (NDA12); 850/32,695 = 2.599% → 2.6% (CSO). Arithmetic correct.
- Blurb (line 5) says "2.6–3.5% of national completions depending on the denominator used" — consistent with table.
- `analysis.py` writes `discoveries/national_completions_reconciliation.csv` as the reviewer requested artifact.
- **R2 satisfied.**

### R3 — pre-2023 annual rows dropped (not reverse-engineered)

- Paper §3 table starts at 2023; no 2018–2022 annual rows present.
- Paper §2.2 (lines 30–32) explicitly states: "The LDA did not publish annual reports before 2023. The earlier draft of this paper gave year-by-year figures for 2018-2022 ... that summed exactly to 2,054 − 854 = 1,200 — i.e., they were back-fit to a single secondary-source cumulative. Those rows are dropped from this revision."
- `analysis.py` lines 58–63 only instantiate 2023, 2024, 2025 rows.
- **R3 satisfied.**

### R4 — share only for 2023 (audited/audited); 2024/2025 approximate

- Paper §3 table: 2023 shares bolded (3.5%, 2.6%); 2024 and 2025 shares carry the † dagger marker. Footnote (line 44): "2024 and 2025 shares have unaudited numerators and should be read as approximate. Only 2023 uses an audited numerator *and* an audited denominator."
- Blurb lead figure is "2.6-3.5% of national completions" for 2023 — not the 4.3% from the discredited earlier draft.
- **R4 satisfied.**

### R5 — forward target is 8,000 by 2028, not 14,000

- `grep 14,000 data/raw/lda_2023.txt` → 0 matches (confirms 14,000 is not in the primary source).
- Paper §6 (lines 52–58) explicitly states: "The earlier draft cited a '14,000 by 2028' internal target. That number is not in the LDA 2023 Annual Report." Verbatim quotes "to deliver 8,000 homes by 2028" and "a pipeline of over 10,000" given.
- Both verbatim quotes cross-checked in raw text: "8,000 homes by 2028" appears at lines 323 and 1041 of `lda_2023.txt`; "pipeline of over 10,000" at line 160.
- `analysis.py` chart right-panel axhline is at 8,000, not 14,000 (line 103).
- **R5 satisfied.**

### Double-count caveat

- Paper §4 "A structural double-count caveat" (lines 46–48) explicitly labels the share as *attribution* share not *additionality* share, and notes Project Tosaigh homes appear in both the numerator and the national denominator.
- Repeated in §7 "What this does NOT establish" under "Not additionality".
- `analysis.py` print statement on line 82 records the caveat in run output.
- **Double-count caveat satisfied.**

## Cross-verification against primary source

Raw-text hits in `data/raw/lda_2023.txt`:

| Expected string | Paper uses it? | Raw-text line(s) |
|---|---|---|
| "ca. 650 Cost Rental homes delivered" | yes | 129 |
| "ca. 200 Affordable for Sale" | yes | 137 |
| "Delivering ca. 850 homes" | yes | 149 |
| "pipeline of over 10,000" | yes | 160 |
| "8,000 homes by 2028" | yes | 323, 1041 |
| "854" | **no (correct)** | *not present* |
| "14,000" | **no (correct)** | *not present* |

All numerical claims in the paper that are attributed to the LDA 2023 Annual Report trace back to verbatim text in the extracted PDF.

## Website summary consistency

`/home/col/website/site/content/hdr/results/irish-lda-delivery/index.md` reviewed against `paper.md`:

- Blurb: ca. 850 headline, 2,054 cumulative end-2024 (IT Sep-2025), 8,000 by 2028 target, "~3% of 50,500-per-year". Consistent.
- Table (lines 30–34) identical to paper.md table including the † dagger on 2024/2025 rows.
- Double-count caveat present (line 40).
- "What the earlier draft got wrong" section (lines 53–62) lists all four Phase 2.75 corrections (854→ca.850, dropped pre-2023 rows, two denominators, 14,000→8,000).
- No reference to the discredited "14,000" target as a live claim.
- **Website summary is consistent with paper.md.**

## Arithmetic spot-checks

| Check | Computation | Paper value | Pass |
|---|---|---|---|
| 2023 share NDA12 | 850/24,316 = 0.03495 | 3.5% | yes |
| 2023 share CSO | 850/32,695 = 0.02600 | 2.6% | yes |
| 2024 implied delivery | 2,054 − 850 | ~1,200 (paper) / 1,204 (analysis.py) | consistent within rounding |
| 2024 share NDA12 | 1,200/22,136 = 0.05421 | 5.4% | yes |
| 2024 share CSO | 1,200/30,330 = 0.03957 | 4.0% | yes |
| 2025 share NDA12 | 1,500/25,237 = 0.05944 | 5.9% | yes |
| 2025 share CSO | 1,500/35,000 = 0.04286 | 4.3% | yes |
| Cumulative end-2025 range | 2,054 + [1,200..1,800] | 3,254–3,854, stated as "~3,200–3,900" | yes |
| Cumulative end-2025 midpoint | ~3,550 | "~3,500 homes" | yes |

All arithmetic reproducible.

## Residual minor observations (NON-BLOCKING)

These are observations I would raise in a normal referee report but which do not rise to blocking-issue level:

1. Paper §3 header says "Cumulative delivery through end-2025: ~3,500 homes, not ~4,500" — the ~3,500 figure is mid-range of the stated 3,200–3,900 band. The reader has to do their own arithmetic (2,054 + 1,500 midpoint = 3,554) to see this. Minor, non-blocking.
2. `analysis.py` computes `DELIVERED_2024 = 1,204` but the paper table rounds to 1,200. The rounding is defensible given the source (~2,054) is itself approximate. Minor, non-blocking.
3. The ≈1,600/year figure in paper §6 (8,000 cumulative / 5 years 2024–2028) implicitly assumes linear level-out from 2024; this is not what the cited 2023 annual report claims and is a reader-facing gloss. Also non-blocking because the paper's framing ("requires the direct-delivery pipeline to come online on schedule") hedges appropriately.
4. The paper no longer publishes a chart for any 2018–2022 rows but `analysis.py`'s right-panel title still says "cumulative LDA (author estimate pre-2023)" in the legend (line 102). Since the dataframe only has 2023+, the "pre-2023" label is a cosmetic leftover. Non-blocking; would be a nice cleanup but does not affect any claim.

None of these are sufficient to block Phase Publish.

## Decision

**NO FURTHER BLOCKING ISSUES**

All five mandated revisions (R1, R2, R3, R4, R5) and the Project Tosaigh
double-count caveat are executed correctly in `paper.md`, propagated through to
`analysis.py` and `results.tsv`, and mirrored faithfully in the public website
summary at `/home/col/website/site/content/hdr/results/irish-lda-delivery/index.md`.
Every live numeric claim attributed to the LDA 2023 Annual Report is verbatim
traceable to `data/raw/lda_2023.txt`; the two fabricated numbers flagged by the
Phase 2.75 reviewer ("854" and "14,000 by 2028") do not appear as live claims
and are explicitly called out as errors of the earlier draft.

The paper is cleared for Phase Publish.
