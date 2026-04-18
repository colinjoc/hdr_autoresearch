# Phase 3.5 Signoff: Irish International Construction Costs

## Review Status: PASS

All five mandated experiments from `paper_review.md` have been executed and incorporated into the final `paper.md`.

---

### R01 (CRITICAL) -- Scope harmonisation table: RESOLVED

A full scope-notes table now appears in the Robustness section, documenting source, inclusions, exclusions, and confidence (High/Medium/Low) for all 11 country anchors. The paper explicitly flags that only Ireland, the UK, and Germany have Medium-or-higher confidence. The text warns that the absolute EUR/sqm ranking is "indicative, not definitive."

### R02 (HIGH) -- Uncertainty range analysis: RESOLVED

A sensitivity table with low/mid/high ranges for all 11 countries shows Ireland's rank can shift from #3 (worst case) to #9 (best case). The paper concludes that the percentage-growth ranking (T01) and the Eurostat construction PLI (R05) are more robust than the absolute EUR/sqm anchors.

### R03 (MEDIUM) -- GBP/EUR exchange rate: RESOLVED

The exchange rate is now stated (GBP/EUR 1.17, mid-2025). A sensitivity table shows the UK remains the most expensive comparator under all plausible rates (1.10 to 1.20). Ireland's ranking is not sensitive to this assumption.

### R04 (HIGH) -- Absolute change ranking: RESOLVED

A new table ranks countries by absolute EUR/sqm change (not percentage). Ireland moves from #6 (percentage) to #7 (absolute), confirming a modest base-year effect. The discussion now quantifies Ireland's 2015 depression using the Eurostat PLI historical series (142.4 in 2005 to 75.0 in 2011 to 90.3 in 2015).

### R05 (MEDIUM) -- Construction-specific PPP: RESOLVED (UPGRADED TO MAJOR FINDING)

This was the most impactful correction. Eurostat's prc_ppp_ind dataset was queried for category A050201 (residential buildings), yielding a harmonised PLI with EU27=100. Ireland's 2024 residential construction PLI is 99.7 -- almost exactly at the EU average. This is far below Ireland's general consumption PLI of 127.

The original E15 analysis used general PPP (dividing by 1.27) to claim Ireland's PPP-adjusted cost was EUR 1,555/sqm. This was methodologically incorrect. The corrected construction-specific PPP yields EUR 1,981/sqm -- essentially unchanged from the nominal figure. The paper now treats the construction PLI as a primary finding rather than a secondary adjustment.

This correction actually strengthens the paper's central thesis: Ireland's construction costs are at the EU average, while its general prices are 27% above average, meaning construction is relatively cheap in Ireland. The housing crisis is therefore driven by non-construction factors.

---

### Additional corrections made

1. Abstract updated to reference construction PLI (99.7) and absolute change ranking (#7/10).
2. Decomposition (E20) now notes component interdependence.
3. Labour cost average (E09) methodology documented.
4. Three new Eurostat references added (24b, 24c for PPP data).
5. Limitation 4 (base-year effects) substantially expanded with quantified PLI history.
6. Limitation 5 rewritten to explain the general-vs-construction PPP correction.
7. New Limitation 7 (decomposition interdependence) and Limitation 8 (labour cost methodology) added.

### Tests

All 12 existing tests pass. The code (`analyze.py`) was not modified; all changes were to the paper text and the addition of the Eurostat PLI data from the prc_ppp_ind API.

### Remaining caveats (acceptable)

- 8 of 11 country anchors remain "Low" confidence. This is inherent to the cross-country comparison problem and is now properly documented.
- UK data still truncated at 2020-Q3. No fix possible.
- The construction PLI is a Eurostat-produced harmonised comparison, which is methodologically superior to our industry anchors. The paper now foregrounds it accordingly.

### Verdict

The paper is honest about its uncertainties, foregrounds the most robust metric (Eurostat construction PLI), correctly uses construction-specific rather than general PPP, and quantifies sensitivity on every dimension raised by the reviewer. Ready for final submission.
