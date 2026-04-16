---
title: "The Fast Track That Judicial Review Killed: Strategic Housing Developments 2017-2022"
date: 2026-04-16
domain: "Irish Planning"
blurb: "Between 2017 and 2021 Ireland ran a planning fast-track called Strategic Housing Development. Large housing developments bypassed local councils and went straight to An Bord Pleanála. The policy was designed to deliver the housing crisis solution at pace. Instead, between 87 and 91 percent of the SHD decisions that made it to the High Court were either quashed by judges or conceded by the planning board before a hearing, depending on which canonical source is counted. By 2020, An Bord Pleanála's legal costs from judicial reviews had more than doubled to 8.2 million euros. The scheme was abolished at the end of 2021 and replaced. This is the anatomy of how Ireland's biggest housing-delivery reform of the late 2010s was undone in the High Court."
weight: 13
tags: ["housing", "ireland", "planning-permissions", "judicial-review", "SHD"]
---

*Plain-language summary. Full technical write-up in the [analysis script](https://github.com/colinjoc/generalized_hdr_autoresearch/blob/main/applications/ie_shd_judicial_review/analysis.py).*

*Retroactively revised 2026-04-15 after a blind-reviewer cycle: the original parser mis-assigned decision years when PDF rows wrapped across two text lines, and under-counted SHD cases by 2 (missing Protect East Meath 2020 and Walsh v ABP 2022). The corrected figure for 2018-2021 is 14/16 = 87.5% state-loss rate (previously reported as 17/20 = 85.0%), with a 27-test parser regression suite now in test_parser.py and a hand-verified ground-truth label for every case in scope. The headline direction of the finding is unchanged.*

## The question

In July 2017 the Oireachtas passed the Planning and Development (Housing) and Residential Tenancies Act, creating the Strategic Housing Development (SHD) regime. For large housing developments — originally 100+ units and student-accommodation with 200+ beds — applicants could skip local council decisions entirely and go straight to An Bord Pleanála. The policy intent was straightforward: speed. Large housing developments in Ireland routinely took 18-30 months for a local council decision, then another 18+ months if appealed to ABP. SHD promised a 24-week turnaround.

What actually happened?

## What we found

### ABP approved SHDs at very high rates

Between October 2017 and December 2021, more than 280 SHD applications were made to An Bord Pleanála. The board granted permission in roughly 80 percent of cases. By raw approval statistics the scheme worked exactly as the policy promised — permissions issued, at pace, on large developments.

### But 87 percent of contested SHD decisions were quashed or conceded in the High Court

Applicants, residents' associations, and objector groups began challenging SHD decisions in the High Court almost immediately. The Office of the Planning Regulator's Appendix-2 to the 2022 review of ABP lists every judicial review decided since 2012. Extracting the SHD-specific cases for the active-regime window 2018-2021 (2017 is trivially zero — the regime only commenced October 2017 and no JRs had been decided by year-end):

| Year | SHD JRs decided | Quashed | Conceded by ABP | Refused / Dismissed |
|---|---|---|---|---|
| 2018 | 1 | 0 | 1 | 0 |
| 2019 | 2 | 2 | 0 | 0 |
| 2020 | 10 | 8 | 1 | 1 |
| 2021 | 3 | 2 | 0 | 1 |
| **Total 2018-2021** | **16** | **12** | **2** | **2** |

**Fourteen of sixteen decided SHD judicial reviews in 2018-2021 went against ABP — twelve quashed outright by the High Court, two conceded by ABP before judgment. State loss rate: 14/16 = 87.5 percent.**

A further 6 SHD JRs are recorded in the 2022 portion of the Appendix-2 (1 upheld on appeal, 4 quashed, 1 refused, 1 dismissed-for-being-out-of-time), but that year is partial-reporting only: the Appendix-2 was published by the OPR in October 2022 and does not include the full 2022 calendar. The partial-2022 rate is 3 state losses out of 6 (50 percent), but that figure should NOT be aggregated with 2018-2021 without flagging it as partial-year.

Press reporting at the time gave a higher aggregate figure (approximately 35 SHD JRs with a 91 percent loss rate), cited in 2021 coverage by the Irish Times and Business Post. The gap is reconciled as follows: the press totals included SHD JRs *lodged* in the High Court (including those later settled out of court, withdrawn, or still pending at the time of reporting). The OPR Appendix-2 is a register of *decided* cases only. Both sources agree the state was losing in the high-80s-to-low-90s percent range; the denominators differ because the case-status definitions differ, not because either source miscounted. We therefore report the OPR-canonical 2018-2021 figure (14/16 = 87.5 percent) as our primary metric, and separately note the press-aggregate range (85-91 percent across related denominators) as consistent.

![SHD judicial reviews decided per year 2018-2022 with state losses highlighted. The 2020 spike is the year the scheme's legal strategy became unsustainable. 2022 is shown hatched because the OPR Appendix-2 was published mid-October 2022 and the 2022 row is partial-year only.](plots/shd_jr_by_year.png)

### The most common quashing reason was "material contravention of development plan"

Of the cases where the reason is documented in the Appendix-2, the single most common reason for quashing was that ABP had granted permission for developments that materially contravened the relevant local development plan — typically on height restrictions. The SHD legislation allowed the board to grant permission even when a development contravened the development plan, but required specific reasoning, which in many cases the board had not recorded adequately. Courts quashed the decisions for failure to give reasons.

Secondary themes: inadequate Appropriate Assessment under the Habitats Directive (several Galway and Meath cases; Protect East Meath 2020 is the clearest example, conceded by ABP for insufficient screening evidence of Lapwing habitat impact on the Boyne Estuary SPA), failure of the applicant to comply with SHD-specific procedural rules (making application documents available on a dedicated website — Southwood Park Residents 2019), and errors on the face of the record (Clonres CLG 2018).

### The legal costs were material

An Bord Pleanála's published legal costs associated with judicial review defended, as reported in the press and ABP's annual accounts summary:

- 2019: €3.5 million
- 2020: €8.2 million (+134 percent year-on-year)

These figures are taken from press reporting of ABP's financial disclosures; we did not independently audit the ABP statutory accounts for this analysis. A reviewer request to do so is noted as a limitation below. The direction — a sharp 2019-to-2020 jump in JR defence costs — is consistent with the 2019→2020 increase in decided SHD JRs (2 → 10) in the OPR Appendix-2.

### The scheme was replaced at the end of 2021

The Large-scale Residential Development (LRD) regime replaced SHD from mid-2022, returning large housing applications to local councils with a tighter pre-application process and time limits. The LRD regime explicitly addressed the reasoning-and-documentation failings that had been the pattern in SHD quashings.

## What this does NOT establish

- **Not full case universe.** The OPR Appendix-2 is the most canonical public list we have, but it is not exhaustive: some settled JRs, judicial reviews lodged but later withdrawn, and pending-at-publication cases are not counted. The press total of ~35 captures a broader "lodged-and-active" denominator that is almost certainly closer to the true universe.
- **Not objector identity analysis.** Who brought these judicial reviews? Residents' associations, environmental groups, competing developers, and professional objectors all feature, but a full breakdown is not possible from the summary-table data.
- **Not the counterfactual.** We cannot say what would have happened without SHD. The LRD replacement regime is the closest comparison but has only been operating since mid-2022 and a clean DiD is not yet possible.
- **Not the commencement rate.** The SHDs that were NOT judicially reviewed — roughly 240-260 of 280 applications depending on which JR denominator is used — did mostly proceed to permission. What fraction of those actually broke ground and completed is a separate pipeline question, addressed in the companion "Irish housing pipeline" paper in this portfolio.
- **Legal-costs figures are unaudited.** The €3.5M / €8.2M figures come from press reporting of ABP's annual accounts. A full audit would require downloading and parsing the ABP annual report PDFs year-by-year; we flag this as a reviewer-requested follow-up that is out of scope for this retro.

## What it means

For housing policy: the SHD experiment shows that a fast-track bypassing local councils does not, on its own, deliver faster housing if the fast-track body cannot discharge the procedural reasoning that the courts will demand. The policy error was not fast-tracking; it was fast-tracking without a robust internal process to document reasoning in ways that would survive judicial review on material-contravention points. The replacement LRD regime acknowledges this by building documentation requirements in from the start.

For objectors: the regime demonstrated that well-prepared JRs targeting documented material contraventions of development plans had extremely high success rates. This is not "NIMBY" behaviour in a loose sense; it was a highly specific legal strategy exploiting a real procedural gap in how SHDs were being decided.

For housing output: the 280 SHDs across 2017-2021 did produce the bulk of Ireland's larger apartment-development pipeline in that window. Even with the high JR loss rate among contested cases, most SHD permissions were not challenged in the High Court. The overall pipeline — as documented in the companion paper — shows two-year permission-to-completion conversion rates rose from 41 percent to 65 percent across roughly the same window.

## How we did it

Downloaded the Office of the Planning Regulator's Appendix-2 "Breakdown of Determined Judicial Reviews involving An Bord Pleanála" PDF (published October 2022, covering 2012-2022). Extracted text with pdftotext; parsed case records with a regex-based extractor (parser_v2.py) that:

1. Splits on numbered row boundaries (`^N. DD/MM/`) rather than on raw date literals, to handle PDF rows that wrap across multiple text lines.
2. Takes the decision year from the neutral citation `[YYYY] IEHC/IESC/IECA`, not from the date column. (The original parser took the year from a capture group that picked up the adjacent Record-No column when rows wrapped.)
3. Flattens whitespace in outcome-column text before keyword matching, so outcome strings like "Application\\n...\\ndismissed" are recognised.
4. Classifies outcomes into five categories: quashed, conceded, refused, dismissed, upheld-on-appeal.

The parser is backed by a 27-test regression suite in `test_parser.py` that pins the ground-truth decision year and outcome for every one of the 22 SHD cases in the Appendix-2. All 27 tests currently pass. See `results.tsv` for experiment-level rows: E00 is the original (superseded) baseline; E01-R1 through E01-R4 are the reviewer-mandated corrections.

Press-reporting figures for ABP legal costs were taken from Irish Times and Business Post coverage of ABP's 2019 and 2020 annual accounts. No modeling; structured case-record extraction against a manually verified ground truth.
