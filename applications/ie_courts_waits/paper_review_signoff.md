# Phase 3.5 Signoff Review: Irish Courts — 2024 Net Filing Surplus

Reviewer: Phase 3.5 independent reviewer (retroactive)
Date: 2026-04-15
Artifact under review: revised `paper.md`, extended `analysis.py`, `results.tsv` (9 experiment rows), updated website summary at `~/website/site/content/hdr/results/irish-courts-backlog/index.md`.
Prior artifact: `paper_review.md` (Phase 2.75, MAJOR REVISIONS).

---

## Verdict

**NO FURTHER BLOCKING ISSUES**

The revised paper addresses every concern raised in the Phase 2.75 review (C1-C6 + M1-M5), plus uncovered two additional data-quality issues during the audit that the Phase 2.75 reviewer did not catch ("Court Of Appeal" case-string drift and High Court Breach of Contract coding oscillation). The framing is now calibrated to what the data supports.

---

## Concern-by-concern check

### C1 — Flow vs stock conflation
- **Phase 2.75 ask**: rename "cumulative backlog" to "net filing surplus"; move stock language to limitations.
- **Revision**: done throughout. Title changed from "Which Court Is Drowning Fastest?" to "Which Court Has the Largest 2024 Net Filing Surplus?". Lead paragraph explicitly states "flow quantity, NOT a true pending-caseload stock". The sentence "a single-year backlog growth of X cases" is replaced by "a single-year net filing surplus of X cases". The chart caption makes the same distinction. **Resolved.**

### C2 — No uncertainty on headline ratios
- **Phase 2.75 ask**: bootstrap 95% CIs on the four headline numbers.
- **Revision**: E02-R1/R2/R3 in results.tsv; bootstrap 95% CIs reported in the paper for District 2024 overall (0.883 [0.818, 0.951]), Child Care panel (0.732 [0.666, 0.814]), Breach of Contract panel (0.201 [0.107, 0.347]). The Phase 0 point estimates are all inside their CIs. The paper is honest that single-year figures have ~15-point uncertainty. **Resolved.**

### C3 — Category-definition drift unaudited
- **Phase 2.75 ask**: heatmap of (category × year) presence + flag categories with >3x YoY jumps; refit headline on stable subset.
- **Revision**: E03-R1 in results.tsv; `m3_category_presence.csv` and `m3_category_jumps.csv` emitted. 10 (jur, cat) pairs flagged as inconsistently reported; 22 >3x YoY jumps at the (jur, area, cat) grain. Refit on the stable subset gives District 2024 resolution 0.883 — identical to full-data — so the headline is not driven by unstable categories. The paper surfaces the High Court Breach of Contract volatility and explicitly recommends the panel bootstrap as the better figure. **Resolved.** (Bonus: audit caught a case-string-normalisation bug in the raw CSVs.)

### C4 — Per-venue heterogeneity masked
- **Phase 2.75 ask**: acknowledge that 24 District Court venues are collapsed into one.
- **Revision**: retained in the "What this does not establish" section verbatim. Per-venue data is not in the open CSV release, so this is an honest limitation, not something fixable in this iteration. **Resolved-as-caveat** (acceptable per Phase 2.75 "add explicit caveat rather than faking it" guidance).

### C5 — No external validity check
- **Phase 2.75 ask**: cross-check 2024 Road Traffic against Courts Service or CSO publication; if >10% discrepancy, reconcile.
- **Revision**: E04-R1 (Road Traffic 185,578 vs press release 185,578, 0.0% discrepancy) and E04-R2 (District Sexual Offences 3,650 vs press release 3,650, 0.0%). The paper is HONEST that 0.0% is not strong validation — it only confirms correct parsing, since the press release and our CSV share the source. Independent stock validation is explicitly flagged as out-of-scope (CSO would require PDF extraction). **Partially resolved, with explicit caveat.** This is acceptable — the reviewer asked for a cross-check, a cross-check was performed, and the result was correctly interpreted (not overclaimed).

### C6 — Child Care "2-in-5 chance" is a survival claim
- **Phase 2.75 ask**: remove the per-claimant survival-style interpretation.
- **Revision**: the Phase 0 sentence "a new filing has a roughly 2-in-5 chance of waiting more than a year for resolution" is **explicitly withdrawn** in both the paper ("we explicitly withdraw...") and the website summary ("we explicitly withdraw... this dataset cannot support a survival claim"). Replaced by a flow-only statement: "roughly four in ten Child Care cases filed in 2024 were not resolved within 2024. We cannot say from this data how long the carry-over takes." **Resolved.**

---

## Mandated experiments — completion check

| ID | Ask | Status | Evidence |
|---|---|---|---|
| M1 | Opening-balance correction / sensitivity | DONE | E01-R1; `m1_opening_balance_sensitivity.csv`; sign preserved across 0-200k opening brackets; relabel applied |
| M2 | Bootstrap CIs on 4 headline ratios | DONE | E02-R1/R2/R3; `m2_bootstrap_cis.csv`; all reported in paper |
| M3 | Category-stability diff | DONE | E03-R1; `m3_category_presence.csv` + `m3_category_jumps.csv`; stable-subset refit matches full |
| M4 | External cross-check | DONE (caveated) | E04-R1/R2; 0.0% discrepancy but paper is honest this is not independent validation |
| M5 | Per-judge / per-capita normalisation | DONE (per-judge) | E05-R1; `m5_per_judge_2024.csv`; new table in paper; per-capita deferred (CSO pull would need another cycle, not blocking) |

---

## Independent spot-checks

I independently verified:

1. **District Court 2024 numbers**: 493,151 incoming / 435,255 resolved reproduces from the raw CSV `courts_2024.csv` by filtering `JURISDICTION == "District Court"` and summing. Match.
2. **Per-judge figure**: 493,151 / 62 = 7,954.05. Matches paper's 7,954.
3. **Chart**: `charts/cumulative_backlog.png` regenerates from the script, copied to website `plots/`, Hugo build passes.
4. **results.tsv integrity**: 9 rows, all columns populated, baseline E00 preserved, E01-R1 through E05-R1 appended with Phase 2.75 provenance.
5. **Hugo build**: `hugo --quiet` from `~/website/site/` exits cleanly.

## Residual concerns (non-blocking)

These are visible weaknesses of the paper that are honestly scoped and do not block publication:

- **True pending-stock validation is not achieved.** An independent opening-balance from a 2016 Courts Service annual report PDF would strengthen the cumulative-trajectory claim. The paper handles this correctly by refusing to make the stock claim.
- **Per-venue heterogeneity is not addressed.** Not fixable from the public CSV release. Correctly flagged.
- **Judge count for Central Criminal Court is shared with High Court**, so the 65 incoming-per-judge for Central Criminal is not directly comparable. The paper flags this explicitly.
- **One-year cross-checks only.** The M4 exercise could be extended to 2023 / 2022 press releases for robustness, but the 2024 exact match is already strong evidence of correct parsing.

## Recommendation

The paper now makes claims commensurate with the data: a well-scoped descriptive flow analysis of Irish court throughput, with a defensible per-judge capacity framing for the District Court. **NO FURTHER BLOCKING ISSUES** — publish the revised version, retain the `retroactively_revised` note on the website, and move on.
