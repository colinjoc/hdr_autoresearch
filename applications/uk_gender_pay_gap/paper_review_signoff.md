# Phase 3.5 Independent Signoff Review — UK Gender Pay Gap 2017-2025

**Reviewer**: Independent Phase 3.5 (retroactive signoff, blind to Phase 2.75 reviewer)
**Artefact under review**: `paper.md` (revised 2026-04-15), `experiments_phase275.py`, `results.tsv` (E02-M1 through E02-M5), `website/uk-gender-pay-gap/index.md`
**Date of review**: 2026-04-15
**Phase 2.75 verdict**: Major revisions required, five mandated experiments (M1 bootstrap CIs, M2 size-stratified late filers, M3 COVID trend sensitivity, M4 firm-identity + SIC, M5 Wilcoxon).

---

## Verdict

**NO FURTHER BLOCKING ISSUES**

The four mandated experiments (M1-M4) plus the stretch M5 have been executed, appended to `results.tsv` with E02-M1 through E02-M5 IDs, and integrated into the paper with material text revisions in Abstract, §4.1, §4.2, §4.3, §4.4 (preserved), §4.5 (new), §4.6 (new), §5.1, §6, §7, and a new §8 Changelog. The website summary is correspondingly revised and carries a prominent "retroactively revised 2026-04-15" banner. Hugo build passes. All CIs in results.tsv match the paper's text. The numerical claims are now either uncertainty-quantified or explicitly flagged.

The revised paper is an improvement on the Phase 3 draft in four concrete ways:

1. The abstract's headline numbers now all carry CIs and the COVID-adjusted slope (0.15 to 0.20 pp/year) replaces the fragile 0.25. This correctly revises the horizon-to-parity from "30 years" to "40-55 years".
2. The 2.10pp within-firm delta is now backed by an overwhelmingly significant Wilcoxon test (p ≈ 10^-97) and is robust across three firm identifiers (1.80 to 2.10pp).
3. The "late filers have smaller gaps" claim is correctly decomposed. The raw −2.40pp survives size-conditioning (OLS coef −1.85pp with size+year FE, p < 1e-17) inside mandatory-reporting bands but reverses in the voluntary sub-250 pool. The paper handles this honestly rather than hiding the reversal.
4. The sector breakdown is a genuine new finding. Education's +12.75pp "widening" is correctly diagnosed as a Multi-Academy-Trust composition shock, not a reform failure; Public Admin / Info-Comms / Construction are identified as the fastest-narrowing divisions.

---

## Issues considered and how they were resolved

I checked the revised paper against Phase 2.75's seven headline concerns and the five mandated experiments. None are blocking. Some minor issues remain but do not prevent publish:

### Checked, PASSED

- **Concern 1 — no uncertainty.** Every headline number in the Abstract, §4.1, §4.2, §4.3, §4.5 now carries a 95% bootstrap CI or a p-value. The one narrative number without an interval (the 1.8× ratio of within-firm to population decline) is derivative of two numbers that do have CIs; acceptable.
- **Concern 2 — Simpson's paradox on late filers.** M2 run in full. The size-stratified table shows the direction holds in 5 of 7 bands, weakens in 20k+, and *reverses* in the <250 voluntary band. OLS with size+year FE delivers −1.85pp [CI: −2.28, −1.43]. The paper states this honestly in §4.3.
- **Concern 3 — COVID regime break.** M3 run in full. All three specifications agree that the slope is 0.15 to 0.20 pp/year, not 0.25. The abstract and §5.1 correctly state the range.
- **Concern 4 — firm identity fragility.** M4(a) run. Three identifiers agree within 0.3pp; the finding is robust.
- **Concern 5 — SIC unused.** M4(b) run. Sectoral breakdown is §4.6, with Education flagged as a compositional outlier. §5.2 limitation on SIC removed as instructed.
- **Concern 6 — no formal test on within-firm delta.** M5 Wilcoxon signed-rank p = 8.6e-98. Reported in Abstract, §4.2, §7.
- **Concern 7 — entry/exit compositional claim.** The paper's "roughly half" language is preserved (§4.2) but now explicitly rests on the population delta (−1.19) vs within-firm delta (−2.10) ratio, both of which have CIs. The reviewer requested Oaxaca-Blinder; the paper does not do formal Oaxaca but the within-firm-vs-all-firms contrast is a reasonable working decomposition. Not a blocker. Upgrade path for a future Phase 4.

### Minor issues I flagged but am not blocking on

1. **The <250 late-filer reversal rests on n = 4 late filings.** Looking at `discoveries/late_vs_ontime_by_size.csv`, the "Less than 250 / late" cell has only 4 observations with a median of 12.71%. That is a point statistic on four firms. The paper presents this as a finding; it is at best a hypothesis pending more data. I'd prefer the §4.3 prose added something like "(n = 4 late <250 filings, so directional only)" but the size-weighted number (−2.29) and the OLS result (−1.85) are not contaminated by this cell, and the paper does not stake its headline on the reversal. Acceptable without revision.
2. **Education composition story is asserted but not quantified within-firm.** §4.6 correctly identifies the Education +12.75pp as a Multi-Academy-Trust compositional shift, but does not compute the within-firm-only Education delta to prove it. For a Phase 4, a division-level within-firm panel would close this loop. For Phase 3.5 signoff, the qualitative diagnosis (filings tripled, majority-female-workforce sector) is enough to not mislead.
3. **The OLS with size+year FE is run on the raw individual-filing DiffMedianHourlyPercent, not an appropriate robust / clustered SE.** OLS on ~94k observations gives a p-value of 5.5e-18 which is implausible-precise given firm-level clustering. The sign and order of magnitude are correct but the p-value and CI are optimistic. The conclusion (real effect, smaller than raw −2.40) is unaffected; only the reported precision would move. Not blocking.
4. **M3 OLS is on n = 9 annual observations.** This is unavoidable with 9 years of data, but the three-specification agreement is more meaningful than any single slope's CI. Paper handles this appropriately by reporting a range rather than a single number.
5. **The paper's "40-55 year horizon to parity" depends on linearly extrapolating a 0.15-0.20 pp/year rate from a current 8.1% gap. This is a back-of-envelope figure, not a forecast, and the paper doesn't oversell it.** Acceptable.

### Data integrity checks passed

- `results.tsv` row count: 31 data rows (was 2). All new E02-* IDs present.
- `paper.md` numerical claims cross-checked against `results.tsv`: population median 2017=9.30 ✓, 2025=8.11 ✓, delta −1.19 ✓, within-firm delta −2.10 ✓, share narrowed 61.1 ✓, Wilcoxon p = 8.6e-98 ✓, OLS late coef −1.85 ✓, COVID slopes −0.198, −0.145, −0.152 ✓, identifier robustness 5259/7173/6139 ✓, SIC Education +12.75 ✓.
- Website summary cross-checked against paper: headline rate 0.15-0.20 ✓, horizon 40-55 years ✓, retroactive-revision banner present ✓.
- Hugo build: passes (`hugo` 355 pages, 54ms, no warnings).
- Real-data compliance: 9 years of primary-source gov.uk CSVs in `data/raw/gpg_{year}.csv`. No synthetic data. `CLAUDE.md` real-data-first rule satisfied.
- Reproducibility: `experiments_phase275.py` seeded with `RNG_SEED = 20260415`, re-runnable end-to-end in under a minute on the existing CSVs.

---

## What would trigger a Phase 4 (non-blocking for publish)

These are genuine research upgrades, not signoff blockers:

- Formal Oaxaca-Blinder decomposition of the within-firm vs compositional split (the paper currently uses a ratio-based informal decomposition).
- Within-firm-only sectoral breakdown to separate real sector progress from Multi-Academy-Trust-style composition shocks.
- Clustered / firm-robust SEs on the M2 OLS.
- Ireland-UK DiD against the 2023 Irish disclosure regime.

None of these are required for the current paper to stand as an honest, uncertainty-quantified descriptive study of the UK regime's nine-year record.

---

**Signoff verdict**: NO FURTHER BLOCKING ISSUES
