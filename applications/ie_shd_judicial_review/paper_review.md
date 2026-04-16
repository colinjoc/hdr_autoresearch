# Blind Reviewer — SHD Judicial Review (RETROACTIVE)

**Verdict: MAJOR REVISIONS REQUIRED.**

## Critical issues
1. **Parser validity unproven.** Regex split on `\d+\. DD/MM/YYYY` yielded earlier false positives (2001, 2010). No post-fix unit tests confirm the corrected parser recovers all SHD cases. Manual ground-truth for at least 5 cases is missing.
2. **Discrepancy unexplained.** Press-reported 35/91% vs. parsed 20/85% is hand-waved as "procedural concessions." Paper must either reconcile or drop press figure.
3. **Outcome classification fragile.** `"quashed" in low` will match "not quashed" / "quashing refused." No confusion matrix vs. manual labels.
4. **Legal-costs claim unverified.** €3.5M→€8.2M cited from press; ABP annual accounts not consulted despite being public.
5. **2022 undercount.** PDF is October 2022; 2022 row missing from table silently.
6. **results.tsv says "22 SHD cases identified" but n=20** — internal inconsistency.

## Required before sign-off
- Manual verification of all 20 cases against OPR source.
- Reconcile with ABP statutory accounts for cost figures.
- Add regex unit tests; flag 2022 as partial-year in table.
- Label headline as "OPR-canonical subset" not total SHD JR universe.
