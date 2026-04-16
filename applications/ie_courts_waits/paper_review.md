# Blind Review: Irish Courts — Which Court Is Drowning Fastest?

Reviewer: Phase 2.75 blind reviewer (retroactive)
Date: 2026-04-15
Artifact: `paper.md`, `analysis.py`, `data/raw/courts_2017..2024.csv` (1,189 rows)

---

## Decision

**Major revisions required** — headline direction is defensible, but the single strongest claim ("88 percent resolution ratio", "+57,896 backlog") conflates *flow* with *stock* and is stated without any uncertainty envelope. The paper is publishable as a descriptive flow analysis only after (i) explicit relabelling of "backlog" as "net flow surplus", (ii) sensitivity analysis to category-definition drift, (iii) bootstrap/CI on the headline ratios, and (iv) at least one external cross-check against a published Courts Service stock figure.

The current framing ("District Court is drowning") overstates what a flow-only dataset can support. Reject the sentence "a new filing has a roughly 2-in-5 chance of waiting more than a year" — this is not inferable from incoming/resolved counts without a survival model.

---

## Headline concerns

### C1. Flow is not stock — "cumulative backlog since 2017" is wrong as stated
The paper's central chart and headline number compute `cumsum(incoming − resolved)` from 2017 and call this "cumulative backlog growth". This is only valid if:
- the 2017 opening balance is zero (it is not — the District Court had decades of pending cases on 1 Jan 2017), AND
- every "resolved" case in year *t* was also "incoming" in year *t*.

Neither holds. A case incoming in 2019 that resolves in 2023 contributes `+1` to 2019 net and `−1` to 2023 net, which the cumsum correctly handles — but a 2016 pending case resolved in 2018 contributes only `−1` (spurious backlog clearance), and a 2024 filing resolving in 2025 contributes only `+1` (spurious backlog growth). **Without the opening balance and a case-level longitudinal join, the cumulative curve mixes flow and legacy-stock effects.** Rename to "net filing surplus since 2017" throughout and move any stock language to a limitations paragraph.

### C2. "88% resolution ratio" has no uncertainty
493,151 incoming and 435,255 resolved is treated as a point estimate. Even as a flow descriptor, year-to-year variation across 2017-2024 should anchor a ±band. A bootstrap over (category × year) rows within the District Court would give a CI on the 88% figure. Expect it to be wider than the paper implies — some categories swing 15+ percentage points year to year.

### C3. Category-definition drift is unaudited
94 categories across 8 years is a lot of room for reclassification. If "Road Traffic" in 2017 bundled minor offences that were split into "Road Traffic" + "Fixed-Charge Overflow" in 2022, year-over-year deltas are definition artefacts not caseload artefacts. The paper asserts "newly-open CSV" — category stability across those eight CSVs must be diffed explicitly. I see no such check in `analysis.py`.

### C4. Aggregation masks per-venue heterogeneity
24 District Court venues are collapsed into one. Dublin District may be drowning while Letterkenny may be clearing. "The District Court is the bottleneck" is not the same claim as "every District Court venue is overloaded" and the paper slides between them.

### C5. No external validity check
A flow surplus of +57,896 cases in 2024 is a large, specific number. The Courts Service publishes quarterly bulletins and the Department of Justice tracks court waiting lists. If neither source's public statistics land within 10% of the paper's figure, the headline needs re-derivation. No such cross-check is attempted.

### C6. Child Care 60% claim is load-bearing and under-evidenced
The emotive "2-in-5 chance of waiting more than a year" reads as a survival-analysis result. It is a ratio of annual counts and cannot make that claim. Either add a proper within-year cohort survival analysis (if case-level dates are obtainable from the raw report PDFs) or remove the per-claimant interpretation entirely.

---

## Mandated experiments (must complete before resubmission)

### M1. Opening-balance correction
Locate the 2016 (or earliest pre-window) Courts Service annual report. Extract the jurisdiction-level opening pending caseload. Re-anchor the cumulative trajectory so year 0 = actual pending stock, not zero. If opening stock is unavailable, drop the word "cumulative backlog" everywhere and report only annual net flow with an explicit disclaimer.

### M2. Bootstrap CIs on all headline ratios
For each jurisdiction and each headline category, resample (category-row) with replacement within 2024 (B=1000) and report 95% CI on:
- District Court resolution ratio (currently stated as 88%)
- Road Traffic backlog growth (currently +23,583)
- Child Care resolution ratio (currently 60%)
- High Court Breach-of-Contract resolution (currently 17%)

If any CI crosses the "keeping pace" threshold (100%), soften the claim.

### M3. Category-stability diff across 2017-2024 CSVs
Produce a heatmap of `(category × year) → rows present` from the eight raw CSVs. Any category missing in ≥2 years, or whose incoming count shifts by >3× between consecutive years without a national policy event, must be flagged. Refit headline metrics on the stable-category subset and report delta vs full-set.

### M4. Cross-validation against an independent source
Pull at least one of: (a) Department of Justice annual waiting-list bulletin, (b) Courts Service quarterly statistical update, (c) CSO crime/court statistics. For Road Traffic and Child Care specifically, compare the paper's 2024 flow figures against the external source. Report absolute and percentage discrepancy. If >10%, reconcile or retract.

### M5. (Nice-to-have) Per-capita and per-judge normalisation
Backlog of 57,896 in a system with N judges is a very different story from the same backlog with 2N judges. Add per-sitting-judge and per-capita normalisers (CSO population by year). This reframes the policy implication without changing the core numbers.

---

## Things done well

- **Real data, freely downloaded** — the project does not fabricate. The 2017-2024 CSVs are the actual Courts Service release, used directly. This passes the real-data-first bar cleanly.
- **Correctly restrained causal language** in the "What this does not establish" section: the paper explicitly declines to attribute cause (judicial capacity, garda pipeline, COVID).
- **Policy framing is proportionate** — the Road-Traffic-diversion suggestion is posed as a question, not a prescription, and distinguishes it cleanly from "hire more judges".
- **Jurisdiction decomposition is the right first cut** — the table on line 28 is the most informative artefact in the paper and does the work the headline claims.
- **Reproducibility is near-complete** — a single script, a single `results.tsv`, deterministic cumsum. Easy to re-run.
- **Honest about missing wait-time data** — the "no wait-time per case" caveat is stated up front, though it then gets violated in the "2-in-5 chance" sentence, which should be removed.

---

## Summary for authors

The data is real, the decomposition is right, the script is reproducible. The statistical framing is where this falls short: flow is presented as stock, point estimates as certainties, and aggregated jurisdictions as homogeneous. Address M1-M4 and the paper becomes a solid descriptive piece. Without them, the "drowning" headline is rhetorically stronger than the evidence allows.
