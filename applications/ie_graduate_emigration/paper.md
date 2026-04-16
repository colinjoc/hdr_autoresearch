---
title: "Irish Emigration 2020-2025: Australia Pulled Level with the UK in 2025"
date: 2026-04-16
domain: "Irish Migration"
blurb: "Irish emigration rose 37 percent between 2020 and 2024, peaking at 69,900 people in the year to April 2024 before easing to 65,600 in 2025. The 2024 peak is about 84 percent of the 1987-present high of 83,000 reached in the 2012 financial-crisis wave. Ireland nevertheless remained net-receiving throughout: 2025 net migration was +59,700. The destination mix has also shifted — in 2025 Australia (13.5k) narrowly exceeded the UK (12.6k) for the first time on record, but the 0.9k gap is inside the CSO PEA18 precision band (±2-3k for small cells) and is only a single year, so the headline is best read as 'statistical tie at the top' rather than a confirmed structural shift."
weight: 10
tags: ["migration", "ireland", "emigration", "australia"]
---

*Plain-language summary. Full technical write-up in the [analysis script](https://github.com/colinjoc/generalized_hdr_autoresearch/blob/main/applications/ie_graduate_emigration/analysis.py). Retroactively revised 2026-04-15 following blind reviewer feedback; see `paper_review.md`.*

## The question

Every few years the Irish emigration story comes back into the public conversation. The last major wave was the post-2008 financial crisis, when emigration peaked at 83,000 people in the year to April 2012. That wave slowly receded, and by 2016-2019 emigration had settled back into the 50-55,000 range. In the 2020s something has changed. The question is by how much, where people are going, and — crucially — whether Ireland is actually losing population.

### Scope note

The directory for this analysis is named `ie_graduate_emigration`, a leftover from the original framing. The data source (CSO PxStat table PEA18) is **all-ages** and has no graduate breakdown. A graduate-specific analysis would require the Higher Education Authority's Graduate Outcomes Survey (HEA GOS) and is out of scope here. Everything below refers to total Irish emigration flows.

## What we found

### Ireland is still net-receiving

Headline first: across every year 2020-2025, Ireland's immigration exceeded its emigration. The 2025 figures are immigration 125,300, emigration 65,600, **net migration +59,700**. 2024 net was +79,300. So while emigration has risen, the net picture is unambiguously positive — population continues to grow through migration. The emigration story is about *gross* outflows, not net decline.

### Emigration is up 37 percent from 2020

CSO Population and Migration Estimates, April each year:

| Year | Emigrants (thousands) |
|---|---|
| 2012 (post-war peak) | 83.0 |
| 2020 | 50.9 |
| 2021 | 52.3 |
| 2022 | 56.1 |
| 2023 | 64.0 |
| 2024 | **69.9** |
| 2025 | 65.6 |

The 2024 figure is the highest since 2015 (when 70,000 emigrated) and is about 84 percent of the post-war peak (83,000 in 2012). 2025 eased back by 6 percent to 65,600 — still nearly 30 percent above 2020 but below the 2024 high. A one-year dip in a provisional estimate is not by itself evidence that the wave has peaked; PEA18 figures are routinely revised in subsequent releases.

![Irish emigration 1987-2025 with destination breakdown 2010-2025. The historical peak in 2012 is annotated; the current wave is approaching but not yet matching it.](plots/emigration_trajectories.png)

### Australia pulled level with the UK in 2025 — within statistical noise

The 2025 destination breakdown:

| Destination | 2025 emigrants (thousands) |
|---|---|
| **Australia** | **13.5** |
| EU14 excl. IE+UK (Germany, France, Netherlands, etc.) | 13.1 |
| UK | 12.6 |
| Other countries (23 aggregated) | 11.1 |
| USA | 6.1 |
| Canada | 5.1 |
| EU15-27 (Poland, etc.) | 4.0 |

Australia at 13.5k is nominally top, 0.9k ahead of the UK (12.6k). **This is inside the CSO PEA18 precision band** (published CSO guidance gives standard errors of roughly ±2-3k for small-cell destination estimates), so strictly speaking Australia, EU14, and the UK are all in a statistical three-way tie at the top of the 2025 ranking.

The year-by-year trajectory also matters. In 2023 the UK led Australia by 9.9k (14.6 vs 4.7); in 2024 by 4.6k (15.2 vs 10.6); in 2025 Australia is ahead by 0.9k. So the honest reading is "Australia overtook the UK for the first time on record in 2025, by a margin smaller than the series' precision", not "structural shift since 2023". A second consecutive year of Australia-above-UK in 2026 PEA18 would strengthen the structural claim; a reversion below the UK would be consistent with 2025 being a noisy single-year lead.

Australia's rise is nonetheless real at the trend level — it has gone from 2.5k in 2021 to 13.5k in 2025, a 5x increase. Drivers widely cited include the Australian post-COVID 482 skilled-visa expansion, the Irish-Australian Working Holiday programme's 2024 age extension, and the 2023 Australian visa-threshold salary reset. Germany and France have also grown inside the EU14 aggregate.

## What we cannot say from this data

- **Not graduate-specific.** PEA18 covers all ages. A graduate-specific analysis requires the HEA Graduate Outcomes Survey, which is tabulated separately.
- **"Other countries (23)" is a large opaque bucket.** 11.1k emigrants went to 23 unseparated countries in 2025 — a volume comparable to the UK or EU14. Any single country inside Other-23 could in principle rival the top three, and we cannot see it. The "Australia is top" ranking is conditional on Other-23 containing no single destination above 13.5k, which is plausible but unverified.
- **Not return-migration-net.** These are gross emigration flows only. In April 2025 Ireland's total immigration was 125,300 and net migration was approximately +59,700. Ireland is still a net-receiving country.
- **April-stock frame.** PEA18 is an April-to-April estimate frame; it is not directly comparable to flow data from other countries (e.g. US ACS) measured at different points in the year. Stated once, not repeated.
- **Not causal.** Housing costs, wage stagnation, post-COVID lifestyle preferences, and destination-country visa reforms have all been cited in the policy discussion; they are not separately identified in PEA18.

## What it means

For a prospective emigrant: Australia, the UK, and EU14 (Germany / France / Netherlands) are effectively tied as the three most-chosen destinations in 2025, each receiving 12-13k Irish emigrants. Australia's pathway has become progressively more accessible since 2023.

For a policymaker: the absolute flow is serious but below 2012 crisis magnitude (84 percent of the 2012 peak), and Ireland remains net-receiving. The destination mix is clearly diversifying away from the historical UK default, but the "Australia is now number one" framing should be treated as provisional until 2026 PEA18 either confirms or reverses the 2025 crossover.

## How we did it

CSO PxStat table PEA18 gives annual April migration estimates by sex, flow (immigration / emigration / net) and destination or origin country (EU14, EU15-27, UK, US, Canada, Australia, Other-23) from 1987 through 2025. We parsed the JSON-stat API response, computed total emigration and net migration time series, compared Australia vs UK year-by-year for 2023-2025, and ranked 2025 destinations. The ±2-3k precision band cited above comes from standard CSO guidance on small-cell estimates in PEA18 and related tables; PEA18 itself does not publish per-cell confidence intervals.

## Caveats on experiments run

E01 (Australia-vs-UK precision test) uses the CSO-documented ±2-3k precision band rather than a cell-level bootstrap, because CSO does not publish the component-level micro-estimates needed for a true bootstrap. A tighter test would require the underlying LFS / administrative components, which are not in the public PEA18 release.
