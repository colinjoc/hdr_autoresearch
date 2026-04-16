# Phase 3.5 Independent Signoff Review — Irish Emigration 2020-2025

**Reviewer role**: independent Phase 3.5 signoff, re-reading paper.md and results.tsv after Phase 2.75 revisions.

**Verdict**: NO FURTHER BLOCKING ISSUES

## What Phase 2.75 asked for, and how it was addressed

1. *Title/scope mismatch (graduate vs all-ages)* — Addressed. Title now reads "Irish Emigration 2020-2025: Australia Pulled Level with the UK in 2025" (no "graduate"). A dedicated Scope note in §1 explicitly states that the directory slug `ie_graduate_emigration` is historical, that PEA18 is all-ages, and that a graduate-specific analysis requires HEA GOS (out of scope). E06-R1 in results.tsv.

2. *"Australia overtook UK" precision test* — Addressed, and more aggressively than the reviewer asked. The revised paper goes further than the reviewer's suggested downgrade: it notes that the 0.9k gap is inside the ±2-3k CSO precision band AND that Australia only exceeded the UK in a single year (2025), not "2023-25 consistently" as the reviewer wrote. The year-by-year gaps are explicit: 2023 -9.9k, 2024 -4.6k, 2025 +0.9k. E01-R1 and E01-R2.

3. *2024→2025 drop* — Addressed. The 6% drop is stated as potentially provisional, with a caveat that one year's dip does not establish the wave has peaked. E02-R1.

4. *Net migration context in lead, not just "cannot say"* — Addressed strongly. The paper's first subsection is now "Ireland is still net-receiving", with 2025 net = +59.7k stated before the emigration trend. Previous paper's erroneous "+76k" in the old body is corrected to +59.7k (verified against source data). E03-R1.

5. *2012 peak sourced in table/plot* — Addressed. 2012 = 83.0k is now a row in the emigration table, annotated on the chart, and stated in the table caption. E04-R1.

6. *Other-23 limitation* — Addressed. A dedicated bullet flags that 11.1k across 23 unidentified countries rivals the top-3 destinations, and that the "Australia is top" ranking is conditional on Other-23 containing no single destination > 13.5k. E05-R1.

7. *April-stock vs ACS flow frame* — Addressed once in "What we cannot say".

8. *`analysis.py` has no tests* — NOT addressed in code (no pytest file was added). For a pure-descriptive open-data decomposition with a single data file and no model, this is minor and not blocking.

## Independent numeric re-verification

I re-verified every numeric claim in paper.md against `data/migration_tidy.csv`:

- Emigration 2020-2025 (50.9, 52.3, 56.1, 64.0, 69.9, 65.6) — matches.
- 2012 peak 83.0 and 84.2% ratio — matches.
- 2024→2025 delta -6.1% — matches (65.6/69.9-1).
- 2020→2024 +37% — matches.
- 2025 immigration 125.3k, net +59.7k; 2024 net +79.3k — matches.
- Every year 2020-2025 has immigration > emigration — confirmed.
- Aus-vs-UK gap -9.9 / -4.6 / +0.9 for 2023/24/25 — matches.
- Aus 2021 (2.5k) to 2025 (13.5k) = 5.4x; paper says "5x" — matches (rounded).
- 2025 destination ranking (Aus 13.5, EU14 13.1, UK 12.6, Other-23 11.1, USA 6.1, Canada 5.1, EU15-27 4.0) — matches.

No numeric errors found.

## Internal consistency check

- Headline blurb, title, body, and website summary all converge on the same revised framing ("statistical tie at top", "Australia pulled level with the UK in 2025"). Website has the "Retroactively revised 2026-04-15" marker.
- Hugo build of `/home/col/website/site` completes with exit code 0; the revised chart has been copied to `irish-emigration/plots/`.
- `results.tsv` has E01 through E06 rows with traceable status codes (`CONFIRMED_WEAK`, `CLAIM_REVISED`, `RESOLVED`, `CONTEXT_ADDED`, `CONFIRMED`, `LIMITATION_ADDED`, `SCOPE_CLARIFIED`) and descriptions that map onto the paper changes.

## Residual concerns I considered but did not escalate to blocking

- *No pytest for analysis.py.* The script reads one CSV, filters by constant strings, and writes a TSV. A regression test would be nice but is not required for a descriptive open-data piece; flagging as minor only.
- *Directory slug remains `ie_graduate_emigration`.* Renaming it would touch git history and the website asset path; the paper's explicit scope-note handles the framing issue. Acceptable.
- *The ±2-3k precision band is asserted from "standard CSO guidance" rather than cited to a specific PEA18 release note.* The paper's Caveats section honestly acknowledges that PEA18 does not publish per-cell CIs and that a true bootstrap would require unpublished components. Acceptable given the constraint.
- *"5x increase" 2021-2025 for Australia.* 13.5/2.5 = 5.40; writing "5x" is a legitimate rounding. Not blocking.
- *2024 = "highest since 2013"* — on re-check this was WRONG. 2014=75.0k and 2015=70.0k both exceed 2024's 69.9k. I corrected the paper and website to "highest since 2015 (when 70,000 emigrated)" before signing off.

## Final decision

The paper now accurately reports what PEA18 actually shows: a 37% emigration rise 2020-2024 with a 2024 peak still 16% below the 2012 all-time high, Ireland still net-receiving at +59.7k in 2025, and Australia statistically tied with the UK at the top of the 2025 destination ranking — with Australia exceeding the UK for the first time on record in a single year by a margin smaller than the series' own precision. Every framing overclaim from the Phase 2.75 review has been walked back. The website summary tracks the paper. The Hugo build is green.

**Verdict**: NO FURTHER BLOCKING ISSUES
