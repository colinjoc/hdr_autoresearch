# Phase 3.5 blind peer review signoff — asset_correlation_regimes

**Verdict**: ACCEPT WITH MINOR REVISIONS
**Reviewer**: fresh Claude subagent, 2026-04-20, no prior context
**Project type**: exploratory (not a publication target; bar is "honest, defensible, internally consistent")

## Summary of the paper in 2-3 sentences

The paper describes rolling 90-day Pearson correlations between SPY and {GLD, BTC, WTI, DBC} over 2004–2026 using moving-block-bootstrap confidence intervals, and compares the post-November-2025 window against the GFC, COVID, 2022 inflation and March–May 2025 tariff episodes. The headline finding is that the SPY-GLD "highest in 22 years" claim from earlier drafts is retracted: the current +0.170 mean is statistically indistinguishable from the +0.174 TARIFF25 mean, though both sit clearly above the +0.049 22-year median. SPY-BTC is the cleaner finding (+0.511 vs +0.159 long-run median, robust across 30d/90d/250d windows, consistent with the post-ETF regime shift) while SPY-WTI and SPY-DBC are actually *decoupled downward*, falsifying the casual "everything moves together" premise. A predictive macro-feature tournament yields strongly negative out-of-sample R² with 90-day-embargoed cross-validation, so the paper ends up descriptive rather than inferential.

## Phase 2.75 response audit

Phase 2.75 (`paper_review.md`) required six actions. Verdict on each:

1. **Replace IID bootstrap with moving-block bootstrap** — ADDRESSED. §3.3 declares block length 90, 2,000 resamples; §6 explicitly narrates the IID-vs-block retraction. All CIs in §4 tables derive from `crisis_block_bootstrap.csv` / `regime_correlation_table.csv`, which I re-verified against the CSVs row by row.

2. **Retract "highest in 22 years" headline** — ADDRESSED prominently. TL;DR states "we **cannot** conclude that the current regime is higher than those prior episodes" and calls out that TARIFF25 (+0.174) exceeds CURRENT (+0.170) on point estimate. §4.2 re-states this in the body; §6 is a dedicated post-mortem.

3. **Pre-register crisis windows + sensitivity to CURRENT start** — ADDRESSED honestly. §7 bullet 1 explicitly states "All R5 crisis windows are post-hoc." §4.5 provides start-date sensitivity for 2025-09/10/11/12 with CIs; the observation "the elevation intensifies the later we start" is flagged as evidence of a trending series rather than a discrete regime break. This is stronger (more honest) than a retrospective timestamp would have been.

4. **Fix `R2_inf=nan` bug** — ADDRESSED silently. `results.tsv` row E25 is now `R3_dxy_neutral_GLD` (the old R2_inf=nan row is gone), and the 68-cell `regime_correlation_table.csv` contains no NaN-regime rows. The paper does NOT mention the fix in Limitations or §6; this is a minor communication gap — an adversarial reader comparing pre- and post-fix tables would notice. (Not blocking.)

5. **Apply BH or declare descriptive** — ADDRESSED. §3.3 closes with "No p-values or multiple-comparisons corrections are reported. We treat this as a descriptive partition, not a hypothesis test." §7 bullet 3 repeats this. Clean.

6. **Embargoed CV** — ADDRESSED. §3.4 specifies "5-fold time-series cross-validation (CV) and a 90-day embargo"; §4.7 confirms "this was the same conclusion from the unembargoed CV; adding the embargo did not rescue it." Negative R² story is kept but appropriately softened ("This does **not** mean correlations are unforecastable in general — it means our feature set and panel are not sufficient").

All six required actions are addressed. Action 4 is the only one handled silently rather than explicitly.

## Numerical spot-check

Ten numbers verified against source CSVs:

| Claim in paper | Paper value | CSV source | CSV value | Match? |
|---|---|---|---|---|
| §4.1 SPY-GLD median | +0.049 | results.tsv E00_SPY_GLD | 0.0487 | ✓ |
| §4.1 SPY-BTC median | +0.159 | results.tsv E00_SPY_BTC | 0.1586 | ✓ |
| §4.1 SPY-QQQ median | +0.918 | results.tsv E00_SPY_QQQ | 0.9184 | ✓ |
| §4.2 TARIFF25 GLD mean/CI | +0.174, [+0.116, +0.256] | crisis_block_bootstrap.csv | 0.1737, [0.1164, 0.2557] | ✓ |
| §4.2 CURRENT GLD mean/CI | +0.170, [+0.156, +0.185] | crisis_block_bootstrap.csv | 0.1697, [0.1563, 0.1851] | ✓ |
| §4.2 INFL2022 GLD CI | [−0.251, +0.165] | crisis_block_bootstrap.csv | [−0.2507, +0.1647] | ✓ |
| §4.3 CURRENT BTC mean/CI | +0.511, [+0.460, +0.549] | regime_correlation_table.csv | 0.5111, [0.4604, 0.5493] | ✓ |
| §4.4 250d GLD mean | +0.032 | sensitivity_window.csv | 0.0320 | ✓ |
| §4.5 2025-09 start GLD | +0.098, [+0.030, +0.175] | sensitivity_current_start.csv | 0.0976, [0.0295, 0.1751] | ✓ |
| §4.6 R1 hiking GLD | +0.128, [+0.031, +0.291] | regime_correlation_table.csv | 0.1282, [0.0308, 0.2906] | ✓ |
| §4.7 OLS/GLD R² | −2.85 | results.tsv T01 | −2.8475 | ✓ |
| §6 AR(1) N_eff range | "1 to 8" across windows | block_bootstrap_R5.csv | min 1.0, max 8.27 (CURRENT/GLD) | ✓ |
| §6 ρ₁ range across windows | "0.87–0.997" | block_bootstrap_R5.csv | min 0.865 (TARIFF25_BTC), max 0.997 | ✓ (the 0.87 figure rounds TARIFF25_BTC ρ₁=0.865) |

All numerical claims spot-check clean. No fabricated or mis-rounded values found.

## Strengths

- The retraction narrative (§6 "Why the naive IID bootstrap was wrong") is exemplary: it states the error, quantifies it (2–8× too tight), identifies the mechanism (AR(1) ρ₁ up to 0.997 → N_eff = 1 for GFC/INFL2022/COVID), and credits Phase 2.75 by name. This is the right way for a post-mortem to read.
- TL;DR does the limitations work in the first paragraph rather than burying them in §7. Anyone reading only the TL;DR gets the honest picture.
- Asset-specific finding (WTI and DBC decoupled *downward*) is flagged prominently and contradicts the casual-narrative premise — this is a genuine exploratory insight the draft could easily have omitted.
- Window-length robustness (§4.4) honestly reports that the 250d GLD value (+0.032) is indistinguishable from the long-run median. This is the kind of qualifier a lazier paper would hide in an appendix.
- References align: Künsch 1989, Longin–Solnik 2001, Forbes–Rigobon 2002, Engle 2002, Baur–Lucey 2010, Akhtaruzzaman et al. 2021, Conlon–McGee 2020, Tang–Xiong 2012, Cheng–Xiong 2014 are all real papers and cited for facts they genuinely support. No obvious fabrications.
- Methodology is baseline + iteration, not Phase 0 stats, per the global writing rules.

## Issues

### Required before signoff

None. The paper meets the exploratory-project bar ("honest, defensible, internally consistent") and addresses every blocking Phase 2.75 finding. There is nothing that, if a website visitor clicked through, would be materially misleading.

### Recommended

1. **Silent fix of the `R2_inf=nan` bug should be acknowledged** in §6 or §8. One-sentence note: "The NaN-category regime row identified in Phase 2.75 has been dropped from `regime_correlation_table.csv`." Without this, a reader comparing the old and new 68-cell tables has to infer the fix. Not blocking but trivially cheap to add.

2. **Expand a few abbreviations on first use**: Mean Absolute Error (MAE, §4.7 table header), Global Financial Crisis (GFC, first appearing in §4.2), Ordinary Least Squares (OLS, §3.4), Exchange-Traded Fund (ETF, §5), autoregressive order-1 (AR(1), §6). Most technical readers know these, but the global writing rule is strict and the author hit DCC-GARCH, CV, YoY, GBR, RF, CPI, DXY, GPR correctly — worth being consistent.

3. **DCC-GARCH robustness not attempted**, even for SPY-GLD. Phase 2.75 listed this as "recommended but not required"; the paper flags it honestly in §7 ("deferred ... publication would require DCC-GARCH triangulation"). For an exploratory project this is fine, but it would be the single biggest credibility add if the author has another afternoon.

4. **GPR-index gap**: §2 notes "the public CSV mirror was unreachable on all three fetch attempts" and §7 flags it. Dallas Fed hosts a working CSV at a different URL (per Phase 2.75 m6). Not blocking for exploratory but the workaround is ~30 minutes of code.

5. **Minor**: §4.3 interpretation column for WTI says "Decoupled downward — less correlated than usual" but the CI [−0.114, +0.156] crosses the long-run median (+0.204) only at the upper edge. "Weakly decoupled / indistinguishable from weak positive" would be more precise. Similarly DBC's CI [+0.054, +0.332] does overlap the long-run +0.339 at the upper edge; "half the long-run commodity-equity correlation" is fine on point estimate but the overlap is worth one sentence.

## Signoff decision

**ACCEPT WITH MINOR REVISIONS.** The paper cleanly addresses every blocking finding from Phase 2.75. The headline is honestly reframed, CIs are now block-bootstrap throughout and the IID-vs-block story is narrated as a retraction rather than buried, the post-hoc nature of both the CURRENT window and the regime thresholds is stated prominently in §7 and reinforced with the §4.5 start-date sensitivity table, and the predictive tournament uses the required embargoed CV. Numerical claims spot-check exactly against the source CSVs. The only Phase 2.75 item handled silently is the NaN-regime-row fix (recommend a one-sentence acknowledgement). For an exploratory project with the stated bar of "honest, defensible, internally consistent," this paper clears it comfortably — it is ready to publish to the website. The minor-revision items are cosmetic/communication improvements, not substantive corrections, and can be rolled in at the author's convenience without re-review.
