# Blind Review: Irish International Construction Costs Paper

## Reviewer Assessment

### Overall Verdict: MAJOR REVISIONS REQUIRED

The paper's central claim -- that Ireland is mid-table on construction costs -- rests on an absolute EUR/sqm comparison (T05) whose anchor values are not like-for-like, and on a cumulative growth comparison (T01) that ignores base-year depression effects. Five specific concerns are detailed below with mandated experiments.

---

### Concern A: Like-for-like scope of EUR/sqm anchors

**Severity: CRITICAL**

The Ireland anchor (EUR 1,975/sqm) comes from Buildcost.ie and is explicitly described as "base construction cost" excluding land, VAT, and professional fees. However, the paper does not verify that the other 10 country anchors use the same scope. Germany's Destatis "EUR 2,000-3,000/sqm" may include some finishing works that Buildcost.ie excludes. The UK BCIS "mid-range GBP 2,400/sqm" covers "average building cost" which typically includes preliminaries, contractor margins, and some design fees.

If the Irish figure is base-only while comparators are partially all-in, Ireland's ranking could shift from #8 to #4-5 out of 11. The entire absolute-level narrative (T05, E14, E18) would be invalidated.

**Mandated experiment (R01):** Add a "scope notes" table documenting for each country anchor: (i) source, (ii) what is included/excluded (land, VAT, professional fees, developer margin, preliminaries, external works), (iii) confidence rating (high/medium/low). Add a sensitivity analysis showing Ireland's rank under "minimum scope" and "maximum scope" assumptions. Add explicit limitation language if scope cannot be fully harmonised.

---

### Concern B: Eurostat index shows relative growth, not absolute level -- robustness of anchors

**Severity: HIGH**

The absolute EUR/sqm comparison multiplies industry-source 2025 figures by the inverse of the Eurostat growth ratio to back-calculate 2015 levels. This is valid only if the 2025 anchor values are accurate. The paper uses single-point estimates (e.g., "Destatis midpoint of EUR 2,000-3,000") with ranges that span 50%. A EUR 500/sqm uncertainty on Germany alone could shift the EU-10 average by EUR 55/sqm, enough to change whether Ireland is above or below average.

**Mandated experiment (R02):** Add a sensitivity/uncertainty analysis on the absolute anchors. For each country, define a plausible range (low/mid/high). Compute Ireland's rank and position relative to the EU-10 average under worst-case (Ireland high, others low) and best-case (Ireland low, others high) scenarios. Report the range of Ireland's rank position.

---

### Concern C: GBP/EUR exchange rate sensitivity for UK comparison

**Severity: MEDIUM**

The paper converts UK BCIS GBP 2,400/sqm to EUR 2,800 without stating the exchange rate used. The GBP/EUR rate has ranged from 1.10 to 1.20 over the past 3 years. At GBP/EUR 1.10, the UK figure would be EUR 2,640; at 1.20, it would be EUR 2,880. This is a 9% range.

Since the UK is the most expensive comparator and a natural bilateral reference, the exchange rate assumption matters for the narrative.

**Mandated experiment (R03):** State the GBP/EUR rate used. Add a footnote showing the UK EUR/sqm figure at the 3-year low and high exchange rates. Verify that the UK remains the most expensive comparator under all plausible rates.

---

### Concern D: Base-year depression effect on cumulative growth interpretation

**Severity: HIGH**

Ireland experienced a severe construction crash from 2008-2014. The 2015 baseline was a trough. A country that starts from a crash trough and grows 41% may end up at a HIGHER absolute level than one that starts from a normal level and grows 50%, depending on the absolute starting points.

The paper acknowledges "base-year effects" in Limitations but does not quantify the issue. The cumulative growth ranking (T01) is the first result presented and drives the narrative. If the base-year effect substantially alters the interpretation, the paper's central claim is weakened.

**Mandated experiment (R04):** Compute the 2015 absolute level for each country (back-calculated from 2025 anchors). Show the absolute EUR/sqm change (not percentage) from 2015 to 2025 for each country. Rank countries by absolute change. Report whether Ireland's rank differs on absolute change vs percentage change. If it does, discuss the implications.

---

### Concern E: Construction-specific PPP vs general PPP

**Severity: MEDIUM**

The PPP adjustment (E15) uses the general comparative price level (127% of EU average) to deflate construction costs. Construction-specific PPP may differ substantially from general PPP because: (1) construction labour is non-tradeable and local, (2) materials are partially tradeable but subject to transport costs, (3) regulatory costs are country-specific.

Eurostat publishes construction-specific PPP in its PPP framework. Using general PPP when construction PPP is available is a methodological shortcut that may bias the result.

**Mandated experiment (R05):** Check whether Eurostat publishes a construction-specific PPP or comparative price level. If available, redo E15 with the construction-specific PPP. If not available, add explicit limitation language explaining why general PPP is used and what direction the bias might take.

---

### Minor Issues

1. **Abstract claims "Ireland ranked #8 of 11 on absolute cost level"** -- this is based on unverified anchor scopes (see Concern A). Qualify with "approximately" or "subject to scope harmonisation caveats."
2. **E09 labour cost comparison** uses "EU average ~EUR 28/hr" without source or methodology for computing the average. Which countries? Weighted or unweighted?
3. **E20 decomposition** presents four premium components as if they are independent and additive. Labour costs affect materials handling costs; regulatory requirements affect labour hours. The decomposition should note this interdependence.
4. **Limitation 4 on base-year effects** is too brief given that the base-year issue undermines the headline finding. Expand.

---

### Summary of Mandated Experiments

| ID | Description | Severity |
|----|-------------|----------|
| R01 | Scope harmonisation table + sensitivity for EUR/sqm anchors | CRITICAL |
| R02 | Uncertainty range analysis on absolute anchors | HIGH |
| R03 | GBP/EUR exchange rate sensitivity | MEDIUM |
| R04 | Absolute EUR/sqm change (not percentage) ranking | HIGH |
| R05 | Construction-specific PPP check | MEDIUM |

The paper may NOT proceed to final status until R01-R05 are addressed in the text, with either new analysis or expanded limitation language with quantified bounds on the uncertainty.
