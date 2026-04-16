---
title: "Irish Courts: Which Court Has the Largest 2024 Net Filing Surplus?"
date: 2026-04-16
domain: "Irish Courts"
blurb: "Using the Courts Service's newly-open 2017-2024 annual data, we decomposed the 2024 annual net filing surplus (new cases minus cases resolved in the same year — a flow quantity, NOT a true pending-caseload stock) by jurisdiction. The District Court has by far the largest 2024 net flow surplus: 493,151 incoming versus 435,255 resolved, a single-year surplus of 57,896 cases (resolution ratio 88.3 percent, bootstrap 95 percent CI [81.8, 95.1]). Road Traffic drives 23,583 of that annual surplus. Child Care resolves at 73 percent over the 8-year panel (95 percent CI [67, 81]). Circuit, Central Criminal and Supreme Courts all closed more cases than they opened in 2024."
weight: 11
tags: ["ireland", "courts", "public-services", "backlogs", "policy"]
retroactively_revised: "2026-04-15 — Phase 2.75 blind review cycle mandated relabelling of 'cumulative backlog' as 'net filing surplus' (flow, not stock), addition of bootstrap CIs, external cross-check, category-stability audit, and per-judge normalisation. See paper_review.md and paper_review_signoff.md for the audit trail."
---

*Plain-language version. Full technical write-up in the [analysis script](https://github.com/colinjoc/generalized_hdr_autoresearch/blob/main/applications/ie_courts_waits/analysis.py).*

## What this is (and what it isn't)

**This is a flow analysis of one year of Irish court activity, not a measurement of the pending-case stock.** The Courts Service annual CSVs publish, per (jurisdiction x area of law x category x year), the count of cases *incoming* in that year and the count *resolved* in that year. They do NOT publish the opening pending stock on 1 January or the closing pending stock on 31 December.

That distinction matters. A "cumulative (incoming minus resolved) since 2017" curve mixes three things: (i) real backlog accumulation of cases filed in the window, (ii) the slow grind through legacy cases filed before 2017, and (iii) a boundary artefact where a case filed in 2020 and resolved in 2024 shows up in both flows with no wait-time tag. We therefore relabel the core quantity as **annual net filing surplus** (single year) or **cumulative net filing surplus** (across years). Neither is the pending-caseload stock.

## The question

The Courts Service of Ireland was making its annual report data available as CSV for the first time at this point. Eight years of data, 1,189 rows, broken down by jurisdiction (District, Circuit, High, Central Criminal, Court of Appeal, Supreme, Special Criminal), area of law (civil, criminal, family, appeals), and case category (94 types including Road Traffic, Personal Injury, Child Care, Liquidated Debt, Bail, Probate).

The simple flow question: **for cases filed in a given year, what fraction were also resolved in that same year, and which jurisdiction has the largest year-ending surplus?**

## What we found

### The District Court has by far the largest 2024 net filing surplus

In 2024 the District Court absorbed 493,151 new cases and resolved 435,255 — a single-year net filing surplus of **57,896 cases**. That corresponds to an 88.3 percent in-year resolution ratio (bootstrap 95 percent CI [81.8, 95.1], B=1000 resampling over category rows within the District Court 2024 stratum). Roughly 12 of every 100 District Court cases incoming in 2024 were NOT resolved within 2024. Whether they resolve in 2025, 2026, or later is not in the dataset.

![Cumulative net filing surplus since 2017 by jurisdiction, anchored at zero in 2017. The District Court line is the dominant feature; everything else is close to flat. This is a flow aggregate, not a pending-stock trajectory.](plots/cumulative_backlog.png)

Cumulated across the full panel (2017-2024, with the 2017 balance arbitrarily anchored at zero — see M1 caveat below), the District Court has a cumulative net filing surplus of +750,645 cases. We do **not** interpret this as "the District Court has 750k pending cases". It is the cumulative flow imbalance of cases that both entered and left the window.

### Every other court is keeping pace or clearing

| Jurisdiction | 2024 incoming | 2024 resolved | Net (incoming − resolved) | Resolution ratio |
|---|---|---|---|---|
| District Court | 493,151 | 435,255 | **+57,896** | **88.3%** |
| High Court | 36,303 | 34,446 | +1,857 | 94.9% |
| Court of Appeal | 3,487 | 2,376 | +1,111 | **68.1%** |
| Special Criminal Court | 68 | 47 | +21 | 69.1% |
| Supreme Court | 231 | 239 | −8 | 103.5% |
| Central Criminal Court | 2,810 | 3,338 | **−528** | **118.8%** |
| Circuit Court | 63,048 | 66,417 | **−3,369** | **105.3%** |

### Per-judge normalisation reframes the story

Absolute surplus scales with court size. Normalising by authorised judge strength (District Court = 62, Circuit = 43, High = 43, Court of Appeal = 16, Supreme = 10, Special Criminal = 9; Central Criminal shares the High Court bench) gives:

| Jurisdiction | Judges | 2024 incoming per judge | 2024 net surplus per judge |
|---|---|---|---|
| District Court | 62 | **7,954** | +934 |
| Circuit Court | 43 | 1,466 | −78 |
| High Court | 43 | 844 | +43 |
| Court of Appeal | 16 | 218 | +69 |
| Central Criminal Court | 43 (shared HC) | 65 | −12 |
| Supreme Court | 10 | 23 | −1 |
| Special Criminal Court | 9 | 8 | +2 |

A single District Court judge handled roughly 7,954 incoming cases in 2024 — more than an order of magnitude more than any other jurisdiction. The "drowning" framing in the Phase 0 draft is defensible **as a per-judge capacity claim**. It is not defensible as a stock claim.

### Inside the District Court, Road Traffic and Child Care lead the 2024 surplus

| Category | 2024 incoming | 2024 resolved | Net surplus | Resolution ratio |
|---|---|---|---|---|
| Road Traffic | 185,578 | 161,995 | **+23,583** | 87.3% |
| Liquidated Debt | 19,401 | 9,802 | +9,599 | **50.5%** |
| Child Care | 21,797 | 12,973 | **+8,824** | **59.5%** |
| Public Order / Assault | 47,956 | 40,479 | +7,477 | 84.4% |
| Larceny / Fraud / Robbery | 39,038 | 32,827 | +6,211 | 84.1% |

Bootstrap CIs across the eight-year panel (year-level resample, B=1000) give wider bands than a single year would suggest:

- Road Traffic (District, 2017-2024): 76.7% mean resolution, 95% CI [68.2, 83.2]
- Child Care (District, 2017-2024): 73.2% mean resolution, 95% CI [66.6, 81.4]
- Breach of Contract (High Court, 2017-2024): 20.1% mean resolution, 95% CI [10.7, 34.7]

The Child Care 60 percent single-year figure is on the low tail of the multi-year distribution. Year-to-year variation across the panel is material (roughly 15 percentage points for most categories), so single-year headlines should be treated as point-in-time and not as steady-state parameters.

### High Court Breach of Contract: volatile and probably reporting-boundary-dependent

Breach of Contract filings at the High Court are 246 (2021), 1,458 (2022), 336 (2023), 1,435 (2024). That 4x-up-4x-down-4x-up pattern is not a real caseload oscillation. It is almost certainly an artefact of how Chancery/Commercial cases are coded in different reporting years, and the category-stability audit (below) flags it as a three-event drift. The headline "17 percent resolution ratio" in 2024 alone is an artefact of this coding; the panel-level bootstrap mean of 20 percent with a 95 percent CI reaching 35 percent is the better figure.

## External cross-check

Two checks against the Courts Service 2024 Annual Report press release (via RTE and Law Society Gazette summaries, July 2025):

- **Road Traffic 2024 incoming**: ours = 185,578; press release = 185,578. Exact match (same underlying CSV).
- **District Court Sexual Offences 2024 incoming**: ours = 3,650; press release = 3,650. Exact match.

Both cross-checks are 0.0% discrepancy because the press release and our CSV share the same source. This does NOT independently validate the CSV; it just confirms we parsed it correctly. A genuinely independent stock figure (e.g. CSO pending-case audit) would require manual extraction from the PDF annual reports and is out of scope for this iteration.

## Category-stability audit

Across the 94-category, 8-year panel: 10 (jurisdiction, category) pairs appear in fewer than all 8 years, and 22 within-jurisdiction category streams show a >3x year-on-year jump in incoming cases — likely reporting-window or classification boundary effects rather than real caseload swings. Refitting the District Court 2024 resolution ratio on the strictly-stable subset gives 88.3%, identical to the full-data figure, so the District Court headline is NOT driven by unstable categories. The volatile categories to treat with caution are: High Court Breach of Contract, District Court Licensing, and Circuit Court Drugs/Larceny (the last likely an area-of-law reclassification between Criminal and Criminal Appeals).

The raw CSVs also contain a trivial case-normalisation issue: "Court Of Appeal" and "Court of Appeal" both appear as distinct strings. We normalise to title case before aggregation; without this the original analysis was treating them as separate jurisdictions.

## What this does not establish

- **No wait-time per case.** We have flow volumes, not waiting-time distributions. We explicitly withdraw the "2-in-5 chance of waiting more than a year" sentence from the Phase 0 draft — that is a survival statement and this dataset cannot support it.
- **No true pending stock.** Without the 2017 opening balance from the pre-window annual reports (not in the open CSV release), cumulative net filing surplus is NOT pending-case stock. Our sensitivity analysis (opening brackets from 0 to 200k) preserves the sign of the District Court trend under every tested bracket, but the absolute stock level is indeterminate from this data alone.
- **No causal attribution.** Why the District Court is at capacity — judicial strength, garda-led prosecution volume, civil-recovery legislative changes, post-COVID pipeline — is not in the data. The Courts Service itself noted that 24 new judges appointed in 2023 reduced backlogs; that mechanism is external to our analysis.
- **No per-venue breakdown within a jurisdiction.** District Court has 24 venues; we do not see which.
- **No sentencing / outcome distribution.** Flow statistics only.

## What it means

For a policymaker: the District Court carries roughly an order-of-magnitude higher per-judge incoming load than any other Irish court jurisdiction, and its annual in-year resolution ratio sits around 88 percent (bootstrap 95% CI 82-95%) — i.e. roughly one in ten incoming cases each year is carried over. Road Traffic is the single largest contributor to the carry-over in absolute terms. A policy question worth asking is whether the overlap between criminal Road Traffic and the fixed-charge penalty notice regime could divert more volume out of court altogether — which is a slightly different question than "do we need more District Court judges?"

For a litigant in a specific Child Care or Liquidated Debt matter: these categories show the lowest same-year resolution rates in the District Court. Half of Liquidated Debt cases and roughly four in ten Child Care cases filed in 2024 were not resolved within 2024. We cannot say from this data how long the carry-over takes — only that the system is not in steady-state same-year throughput for these categories.

## How we did it

We downloaded the Courts Service Annual Report datasets for 2017 through 2024 from data.courts.ie (CC BY 4.0), concatenated into a 1,189-row panel (jurisdiction × area-of-law × category × year), case-normalised the jurisdiction strings, and computed the incoming-minus-resolved difference per row. Headline ratios carry bootstrap 95% confidence intervals (B=1,000 resamples). Category stability is audited via a year-presence matrix and a YoY-jump flagger at the (jurisdiction, area-of-law, category) level. External cross-checks are against the Courts Service 2024 Annual Report press release. Per-judge normalisation uses authorised-strength figures from the Association of Judges of Ireland and the Courts Service Annual Report 2024. All code and intermediate artefacts are in `analysis.py` / `discoveries/` / `results.tsv`.

## Phase 2.75 revisions

The Phase 0 version of this paper was published without a blind reviewer cycle. A retroactive Phase 2.75 review (`paper_review.md`, 2026-04-15) raised six headline concerns and mandated five experiments (M1-M5). The revisions in this version:

- **M1 (opening-balance sensitivity)**: relabelled "cumulative backlog" as "cumulative net filing surplus" throughout. Sign of the District Court trajectory preserved under all tested opening-stock brackets (0 to 200k).
- **M2 (bootstrap CIs)**: all headline ratios now carry 95% bootstrap intervals. Original 88%, 60%, 17% point estimates are all inside their CIs but the bands are material.
- **M3 (category-definition drift)**: audit surfaced 22 >3x YoY jumps at the (jur, area, category) grain, and one case-string normalisation bug in the raw CSVs. District 2024 ratio on the stable-only subset matches the full-data figure.
- **M4 (external cross-check)**: two Courts Service 2024 Annual Report press-release figures match our CSV parse exactly. Independent stock validation is not achievable from open data at this time.
- **M5 (per-judge normalisation)**: District Court incoming-per-judge is ~7,954, an order of magnitude higher than any other jurisdiction. This is the evidence for the "drowning" framing, and it is a capacity claim, not a stock claim.
- **Withdrew** the Phase 0 sentence "a new filing has a roughly 2-in-5 chance of waiting more than a year" — that is a survival claim unsupported by flow-only data.
