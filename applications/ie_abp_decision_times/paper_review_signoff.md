# Phase 3.5 Blind Signoff Review — ABP Decision Times Paper

**Reviewer:** Independent (fresh read, no prior context from Phase 2.75)
**Project:** `/home/col/generalized_hdr_autoresearch/applications/ie_abp_decision_times/`
**Artefacts reviewed:**
- `paper.md` (final, 224 lines)
- `paper_review.md` (R1–R10 mandates + 7 numbered defects)
- `results.tsv` (67 rows; 20 R-rows appended R1.T01_linear → R10)
- `phase_2_75_revisions.py` (879 lines; main() executes R1–R10)
- `discoveries/loocv_tournament.csv` (41 rows, 5 families × ≤10 left-out years)
- `discoveries/headline_cis.csv` (29 quantities with CIs)
- `discoveries/mix_productivity_decomposition.csv` (Oaxaca-Blinder)
- `discoveries/phase_b_mc.csv` (3 scenarios, median + 5/95 percentiles)
- `discoveries/shd_lrd_distributions.csv` (6 cohorts, median+IQR+p90)
- `discoveries/provenance_audit.json` (CHART_READOFF flags for 2015, 2016)

---

## Verdict

**NO FURTHER BLOCKING ISSUES**

The rewrite satisfies every R1–R10 mandate and every one of the 7 numbered defects from `paper_review.md`. The empirical core is preserved, causal over-claims are consistently demoted to correlational/accounting-identity language, Phase B is explicitly labelled directional-only with Monte Carlo uncertainty bands, pre-2018 provenance is flagged, and the out-of-sample failure in 2025 Q3 is disclosed plainly rather than papered over.

---

## Verification against each required check

### Every R1–R10 has a row in `results.tsv` with KEEP/REVERT status — CONFIRMED

20 R-rows present (lines 48–67):
- R1 (6 rows): T01_linear KEEP, T02_its KEEP, T02a_drop2023 KEEP, T02b_lasso KEEP, T03_littles KEEP, T02_champion_status KEEP
- R2 (1 row): KEEP (29 quantities with CIs)
- R3 (1 row): KEEP (mix share −3.2% of 2018→2024 rise; below 30% threshold)
- R4 (4 rows): all REVERT (SOP CI spans 60–67pp exceed 30pp threshold; s1_beats_s3 frac 0.226 > 0.15 threshold)
- R5 (2 rows): SHD_2024 KEEP, LRD KEEP
- R6 (1 row): KEEP (refit MAE 0.43 weeks on 2017–2024)
- R7 (2 rows): T04_capacity REVERT, Phase_B_form REVERT (MAE 100.13 weeks ≫ 5-week threshold)
- R8 (1 row): REVERT (OOS MAE 28.5pp > 15pp threshold)
- R9 (1 row): REVERT (writing change applied)
- R10 (1 row): REVERT (writing change applied)

The REVERT statuses on R4, R7, R8 correctly reflect that the original Phase B scenario precision could not be defended post-review; the paper correspondingly demotes them to directional bands in §5.8–§5.10.

### Every headline number carries a CI or explicit uncertainty flag — CONFIRMED

Spot-check against abstract (line 5):
- "18 weeks in 2017 (95% CI 17.2–18.8)" — matches `headline_cis.csv` row 6
- "26 weeks in 2022 (CI 24.9–27.1)" — matches row 16
- "42 weeks in 2023 and 2024 (CI 40.6–43.4 in each year)" — matches rows 18, 20
- "64% in 2017 (CI 61.9–66.0)" — matches row 7
- "25% in 2024 (CI 23.6–26.4)" — matches row 21
- "in-sample MAE 0.57 wk … LOO 1.65 wk" — matches §5.2 and LOOCV CSV aggregation (T02_its LOO-CV MAE = 1.649, recomputed independently)
- "each with 5th–95th percentile bands of 60–67 percentage points" — matches `phase_b_mc.csv`
- "S1 beats S3 in 22.6% of draws" — matches R4.s1_beats_s3 row

§2 baseline table has CI columns for every mean-weeks and SOP% row. §5.3 has ρ CIs (1.37–1.53 / 0.95–1.05 / 0.70–0.77), matching delta-method rows in `headline_cis.csv`. §5.4 SHD 2024 "95% CI 85.6–162.4" matches row 22. All 29 quantities with CIs in `headline_cis.csv` have been propagated.

### Pre-2018 numbers carry a CHART_READOFF tag or equivalent caveat — CONFIRMED

§2 Provenance column in baseline table labels 2015 and 2016 as "Bar-chart read-off, uncertain ±2 wk" and 2017 as "AR 2018 narrative (single sentence, p. 852 and Fig. 3)". §2 paragraph after the table states: "we flag them `CHART_READOFF` in `results.tsv` (R6)". Caveat 7 also flags this explicitly. `discoveries/provenance_audit.json` sets 2015 and 2016 `mean_weeks` to `CHART_READOFF` and pre-2018 `sop_pct` to `BAR_CHART_READOFF_FIG3_AR2018`. Sensitivity check (refit on 2017–2024, n=8, MAE=0.43 weeks, coefficients stable) disclosed.

### SHD duration reported as distribution (median + IQR), not only mean — CONFIRMED

§5.4 reports SHD 2024 as mean 124, median ~79, IQR 42–151, p90 ~267 — a distribution, not a bare mean. §5.4 caveat explicitly states "headline SHD-vs-LRD mean contrast (124 vs 13) survives as a median-vs-median contrast (~79 vs ~12)". Caveat 8 restates the small-n residual-tail limitation. Abstract (line 5) also leads with "mean 124 weeks, with an approximate lognormal-fit median of ~79 weeks and 25th–75th percentile 42–151 weeks".

### T02 LOO-CV out-of-sample MAE disclosed (1.65 wk) — CONFIRMED

Independent recomputation from `discoveries/loocv_tournament.csv` (aggregating the 10 left-out years for family T02_its) gives mean absolute error = 1.649 weeks, which rounds to the paper's 1.65 wk claim. Abstract, §3, §5.2, Caveat 4, and §9 Change Log row R1 all quote 1.65 weeks. Overfit ratio 2.9× disclosed in §3 and Caveat 4. Next-best LOO family (T02b_lasso at 2.91 weeks) correctly identified and disclosed.

### Phase B demoted to directional-only with MC uncertainty bands — CONFIRMED

§5.8 table reports median + 90% CI for W and SOP per scenario, CI spans 60–67pp, bold-face warning "All three scenarios have 60+ percentage-point SOP CIs, so the point estimates are directionally indicative, not quantitatively precise". §5.9 in-sample MAE 100 weeks disclosed. §5.10 2025 Q3 OOS error 51pp disclosed explicitly and stated to be outside the MC band. Caveats 5 and 6 restate both failures. Abstract (final sentence) concludes "the causal attribution and the forward scenarios are not [robust]".

### ρ language is correlation / accounting-identity, not causal — CONFIRMED

Every ρ claim is qualified:
- Abstract: "which is *arithmetically equivalent* to — not a causal explanation of — the observed backlog dynamics"
- §3: "ρ = intake ÷ disposed is an accounting identity for net-backlog change … but the data do not identify ρ as a causal *input* to decision time"
- §3: "2024 ρ = 0.74 is consistent with, not a causal driver of, the 2025 recovery"
- §5.3: "validates using ρ as an operative descriptive summary, but does not identify *which* within-type mechanism is doing the work"
- §6: "The ρ arithmetic is an accounting identity, not a mechanism"
- §7: "ρ = intake/disposed is an arithmetically compact summary of the trajectory but not a causal identifier"
- Caveat 10: "'ρ is consistent with the observed trajectory' is the strongest statement the aggregate data supports"

The three matches for "explains/caused/drove" in a `grep` of the paper (§5.5 line 124 quotes the old phrasing it is *replacing*, §5.6 line 128, and §9 changelog quoting the mandate) are either meta-references to the rewording or hypothetical-channel framing that the paper explicitly cannot identify with n=10. None of them asserts ρ as a causal input.

### ACP June-2025 forecast in caveats, not abstract/results — CONFIRMED

Abstract's only ACP mention is the institutional-name reference: "its reconstituted successor An Coimisiún Pleanála (ACP)". The "mechanical compliance rise" forecast is confined to §8 Caveat 3, explicitly labelled "This is a forecast, not an observation; the pre-ACP baseline cannot measure it (moved from Abstract and §6 per R10)". §6 (Discussion) and §7 (Conclusion) contain no ACP-SOP-mechanical-rise forecast — only the pre-ACP data's own recovery signal (37% → 77% monthly 2025 Q1–Q3), which is observed, not forecast.

### §Caveats enumerates every reviewer-raised risk — CONFIRMED

§8 lists 11 caveats, covering every numbered defect from `paper_review.md`:
- Defect 1 (T02 over-fit): Caveat 4
- Defect 2 (queueing solution correlational): Caveats 10, 11
- Defect 3 (pre-2018 chart-read-off): Caveat 7
- Defect 4 (SHD-vs-LRD mean contrast): Caveats 8, 9
- Defect 5 (Phase B no parameter uncertainty): Caveats 5, 6
- Defect 6 (mix-vs-productivity not decomposed): addressed in §5.3 body (R3 decomposition) + Caveat 1 (aggregate-year data) and Caveat 10 (ρ as outcome)
- Defect 7 (2025 YTD iid bootstrap invalid): addressed by R2 trend-plus-noise replacement in `headline_cis.csv`; no longer an iid CI in the paper
- Plus general n=10 limit (Caveat 1), SOP non-binding (Caveat 2), and ACP-mechanical-rise (Caveat 3)

---

## Critical probes (pass)

- **Any quantitative Phase B claim sneaking back as forecast?** No. The abstract frames the 15%/48%/36% numbers as "point estimates" flanked by 60–67pp CIs and immediately notes "the scenario ranking is not robust". §7 concludes "the return to a pre-2018 70–80% compliance regime by 2028 is supported by none of the three scenarios' median point estimates" — a negative statement, not a forecast of any particular 2028 outcome.
- **Any "explains / caused / due to" language attached to a correlation?** The only remaining close cases are:
  - §5.5 line 124: "because drafting must anticipate challenge" — framed inside a hypothesis ("whether high-JR-risk case types are slow because X or because Y") that the paper then says it cannot identify. Acceptable.
  - §5.6 line 128: "underlying reason-giving or Board-capacity channels that drove ABP decision time" — a mild causal attribution to proposed channels. This is the closest thing to a residual over-claim, but the surrounding text (§5.6 is a null-finding on the P&E List) and Caveats 10–11 keep the overall stance honest. Not blocking.
  - §5.9 line 152: "Because 2022 and 2023 ρ are ≥ 1 … the formula diverges" — mechanical description of the model's behaviour, not a causal claim about the world. Acceptable.
- **Any claim that 2028 SOP will be X%?** No. The three scenario medians are reported with their CIs and immediately qualified as directional.
- **LRD 13-week window ambiguity?** Disclosed in Caveat 9 and §5.4 caveat text; 2024-only restriction also reported (mean ~13, median ~12).

---

## Minor nits (non-blocking, optional polish)

1. §5.6 line 128 phrasing "channels that drove ABP decision time" is the single mildest residual causal-attribution in the paper. Could be softened to "channels that co-moved with ABP decision time" for stylistic consistency with §3 and §5.3, but is not a blocking defect.
2. §5.10 line 156 inline intake figures ("Q1 = 2,380 per year; Q3 YTD annualised = 2,871 per year") duplicate figures that the R8 discoveries row could be cross-referenced to; a one-line pointer to `discoveries/phase_b_mc.csv` provenance would aid reproducibility but is not required.
3. The paper §5.2 quotes T02 champion margin as "1.76× next-best" while the Accept-criterion in R1 mandate was "<2× next-best". Both numbers are internally consistent; the paper could more prominently state "T02 passes the <2× criterion" if desired.

None of these is blocking.

---

## Reproducibility spot-checks

- Re-aggregating `discoveries/loocv_tournament.csv` per family reproduces all five LOO-CV MAEs in `results.tsv` rows R1.* exactly (T01_linear 5.103, T02_its 1.649, T02a_drop2023 5.154, T02b_lasso 2.909, T03_littles 3.048).
- `discoveries/headline_cis.csv` has 29 non-header rows; matches `R2 n_quantities_with_CI` = 29.
- `discoveries/phase_b_mc.csv` rows match §5.8 table numerically.
- Oaxaca-Blinder TOTAL row for 2018→2024: share −0.55, productivity 17.10, interaction 0.56 — matches §5.3 prose (+17.1 weeks productivity, −0.55 wk mix, +0.56 interaction) exactly.

---

## Final verdict

**NO FURTHER BLOCKING ISSUES**

The paper is signoff-ready. Every Phase 2.75 reviewer mandate has been executed, logged with KEEP/REVERT in `results.tsv`, supported by a discoveries artefact, and reflected in the paper's prose. Quantitative claims carry CIs or explicit uncertainty flags. Phase B is unambiguously demoted to directional sensitivity bands. ρ language is disciplined. The ACP forecast is in §Caveats. The 2025 Q3 out-of-sample failure is disclosed rather than hidden.
