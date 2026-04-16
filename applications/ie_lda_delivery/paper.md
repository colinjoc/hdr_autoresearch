---
title: "How Much Housing Does the Land Development Agency Actually Deliver?"
date: 2026-04-15
domain: "Irish Housing"
blurb: "The Land Development Agency (LDA) has been active as a delivery body since 2023. In its first audited year (2023) it delivered ca. 850 homes — 2.6-3.5% of national completions depending on the denominator used — entirely through Project Tosaigh acquisitions of privately-built units. Cumulative delivery through end-2024 was ~2,054 homes (Irish Times, Sep 2025), and 2025 press reporting suggests another ~1,200-1,800 on top. The LDA's own 2023 annual report sets a forward target of 8,000 homes by 2028 (not the widely-cited 14,000). On any of these figures the LDA is a structurally minor contributor to the Housing for All 50,500-homes-per-year framework."
weight: 14
tags: ["housing", "ireland", "LDA", "policy-evaluation", "retroactively-revised"]
---

*Plain-language summary. Full technical write-up in the [analysis script](https://github.com/colinjoc/generalized_hdr_autoresearch/blob/main/applications/ie_lda_delivery/analysis.py). This paper was retroactively revised on 2026-04-15 after a Phase 2.75 blind-reviewer pass flagged fabricated precision on the 2023 headline, reverse-engineered pre-2023 annual rows, an inconsistent national-completions denominator, and a structural Project-Tosaigh double-count in the original 2026-04-16 draft.*

## The question

The Land Development Agency was established by statute in September 2018 and began substantive housing delivery activity in 2023 once Project Tosaigh came on stream. The natural questions: **how many homes has the LDA actually delivered against verifiable sources, and what share of the 50,500-per-year Housing for All target does that represent?**

## What we found

### Only 2023 has an audited LDA delivery figure: ca. 850 homes

The LDA 2023 Annual Report is the only year for which the Agency publishes an audited delivery total. The report's verbatim language is:

- "ca. 650 Cost Rental homes delivered via Project Tosaigh during 2023"
- "ca. 200 Affordable for Sale" homes (also via Project Tosaigh)
- "Delivering ca. 850 homes" (headline)

Project Tosaigh is a forward-purchase programme in which the LDA buys completed or near-complete homes from private developers at an agreed price. **One hundred percent of 2023 LDA delivery was via Project Tosaigh acquisition — zero direct-build completions.** The LDA's first direct-build project (Shanganagh, Co Dublin) was not expected to complete its first homes until 2025.

The earlier draft of this paper reported the 2023 figure as "854" — a false precision. The Agency itself uses "ca. 850"; that is the correct number.

### Pre-2023 annual figures are not publishable

The LDA did not publish annual reports before 2023. The earlier draft of this paper gave year-by-year figures for 2018-2022 (0, 100, 200, 350, 550) that summed exactly to 2,054 − 854 = 1,200 — i.e., they were back-fit to a single secondary-source cumulative. Those rows are dropped from this revision; we do not have a defensible annual breakdown for 2018-2022 and nothing in the 2023 report contradicts the simplest reading that direct-delivery LDA output before 2023 was approximately zero and pre-2023 Project Tosaigh activity was small.

### Cumulative delivery through end-2025: ~3,500 homes, not ~4,500

The Irish Times (September 2025) reported cumulative LDA delivery through end-2024 as ~2,054 homes. Implied 2024 delivery is therefore 2,054 − 850 = ~1,200 homes. 2025 delivery is press-estimated in the ~1,200-1,800 range. Cumulative end-2025 is therefore ~3,200-3,900 homes — not the ~4,500 claimed in the earlier draft.

| Year | LDA delivered | Source | NDA12-towns denominator | CSO all-Ireland denominator | Share (NDA12) | Share (CSO) |
|---:|---:|:---|---:|---:|---:|---:|
| 2023 | **ca. 850** | LDA 2023 report (audited) | 24,316 | 32,695 | **3.5%** | **2.6%** |
| 2024 | ~1,200 | implied from IT Sep-2025 cumulative | 22,136 | 30,330 | 5.4%† | 4.0%† |
| 2025 | ~1,500 (range 1.2-1.8k) | press-estimated | 25,237 | 35,000 | 5.9%† | 4.3%† |

† 2024 and 2025 shares have unaudited numerators and should be read as approximate. Only 2023 uses an audited numerator *and* an audited denominator.

### A structural double-count caveat

Project Tosaigh homes are built by private developers under the standard planning and construction regime. They are therefore **already counted in the national completions denominator**. Reporting "LDA share of national completions" while 100% of LDA output is Project Tosaigh forward-purchase is therefore an *attribution* share (how many of the national total are LDA-acquired), not an *additionality* share (how many extra homes the LDA caused to be built). If the LDA did not exist, those ~850 homes would still have been built — just not acquired at the cost-rental discount. This distinction matters and was missing from the earlier draft.

![LDA delivery vs national completions (2023 onward only, with two denominators). Right panel: cumulative LDA delivery vs the LDA 2023 annual report's 8,000-by-2028 forward target.](plots/lda_delivery.png)

### The forward target in the 2023 annual report is 8,000 by 2028

The earlier draft cited a "14,000 by 2028" internal target. That number is not in the LDA 2023 Annual Report. The report's verbatim forward language is:

- "to deliver 8,000 homes by 2028" (Project Tosaigh target)
- "a pipeline of over 10,000" (combined Tosaigh + direct-delivery pipeline)

If 2023 delivery of ~850 is the realistic run-rate and 2024 implied delivery is ~1,200, reaching 8,000 cumulative by 2028 requires average delivery of ~1,500/year for 2025-2028. That is consistent with the existing trajectory but requires the direct-delivery pipeline (Shanganagh et al.) to come online on schedule.

Even at 8,000 cumulative by 2028 — or 1,600/year on a levelled basis — the LDA would represent ~3% of the 50,500-homes-per-year Housing for All target.

## What this does NOT establish

- **Not a counterfactual.** We cannot say what the LDA's delivery would have been without Covid-era supply disruption, planning reform delays, or the judicial-review backlog (see companion `ie_shd_judicial_review` project). The 850 figure is what happened; we do not know what would have happened under alternative policy settings.
- **Not additionality.** As discussed above, 2023 LDA output was 100% Project Tosaigh acquisition of privately-built homes, which are already in the national denominator. The LDA's *additionality* (homes that would not have been built but for the LDA) is a separate, harder question and is not addressed here.
- **Not tenure-weighted impact.** LDA output is specifically cost-rental and affordable-for-sale — tenures that serve different households than market-rate housing. A 3% share of the national total in a tenure band that otherwise has no supply may matter more than the arithmetic suggests.
- **Not the full state-delivery picture.** Direct local authority construction, Approved Housing Bodies, and the Housing Agency deliver separately and at different scales.

## What it means

For policy realism: the LDA is running at a ~850-1,500-per-year delivery pace against a stated 2028 cumulative target of 8,000. That target is internally consistent with the current trajectory if the direct-delivery pipeline converts on schedule. Against the 50,500-per-year Housing for All figure, even the LDA's 2028 run-rate is ~3% of the target. That is not a failure — the LDA was never designed to be the lead vehicle — but it does mean the framing "the LDA will solve the housing crisis" is inconsistent with the Agency's own targets.

For an Irish housing commentator: the right numbers to cite are ca. 850 (2023, audited), ~2,054 cumulative (through end-2024), and 8,000 cumulative by 2028 (LDA target). The "14,000 by 2028" figure in circulation does not come from the 2023 annual report.

## How we did it

Numerator: LDA 2023 Annual Report (audited 2023), Irish Times September 2025 (cumulative through end-2024), press reporting (2025 range). Denominator: CSO NDA12 table (towns-only series), also cross-checked against the CSO all-Ireland aggregate — both are reported explicitly in the table above because they give materially different share calculations. Not a modelling exercise; descriptive comparison with explicit uncertainty flags on unaudited rows.

**Phase 2.75 reviewer findings executed in this revision**: R1 (replace 854 with ca. 850 with tenure breakdown), R2 (present both denominators), R3 (drop pre-2023 reverse-engineered annual rows), R4 (restate share only for audited year, mark others), R5 (replace 14,000 forward target with 8,000 per 2023 report). Reviewer report at `paper_review.md`.
