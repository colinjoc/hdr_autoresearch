# Knowledge base — PL-1 commencement-notice cohort study

Living record of stylised facts, known pitfalls, and findings as they accumulate. Updated after each KEEP experiment.

## Stylised facts (pre-experiment, from literature)

- Harter & Morris (2021) US permit-to-completion: single-family ~18 months, multifamily ~28 months median.
- Bromilow (1969) T = K C^B duration-on-cost regression is the classical construction-duration benchmark.
- ESRI QEC box (multiple years) estimates the Irish permission-to-completion aggregate cross-correlation lag at 7-9 quarters.
- Apartment viability studies (SCSI 2020 / Duff 2020 / Coyne 2022) predict apartment cohort durations should exceed dwelling-house cohort durations by 12+ months.
- Real-options theory (Capozza-Helsley 1990, Bulan-Mayer-Somerville 2009) predicts a non-zero "dark permission" fraction that grows with volatility.
- SHD regime (2017-2021) bypassed first-instance LA; litigation high; expected mixed effect on commencement timing.
- BCAR 2014 implementation was 2014 onwards; pre-2014 commencements are either grandfathered or absent.
- Building permission default life is 5 years; Section 42 extensions add 2-5 more.
- Dublin 4-LA area dominates apartment stock; rest of country dominates one-off dwelling stock.

## Known data pitfalls

- CN_Date_Granted has min=1900 and max=2121 in raw data — clerical entries; filter to [2000, 2026].
- CN_Proposed_end_date has min=1900 and max=2122 similarly — mostly useless as a covariate.
- CCC_Date_Validated populated for only 39% of rows — this is structurally right-censoring, not missingness.
- CCC_Units_Completed often 0 for residential rows — administrative filings that don't complete the unit count field.
- CN_Sub_Group has Unicode carets ("^") around tokens — needs stripping.
- Some projects have multiple rows (one per building or phase) — de-duplicate on CN_Planning_Permission_Number for project-level analysis.
- Opt_Out_Comm_Notice projects are predominantly one-off self-builds and have a different cohort structure.
- LocalAuthority field is inconsistent casing ("Dublin City Council" vs "dublin_city_council"); LA grouping needs normalisation.

## Findings (from Phase 0.5, 1, 2, 2.5, B)

### E00 — baseline (full residential cohort)
- Permission-to-commencement median: **232 days** (observed-event rows, N=183,621). KM median identical.
- Bootstrap 95% CI: 231.0–234.0 days (E24).
- Commencement-to-CCC median: **498 days** (N=76,565).
- Permission-to-CCC median (complete-timeline subcohort): **962 days** ≈ 32 months (N=71,599).
- 25th percentile perm-to-comm: 97d (fast one-off dwellings).
- 75th percentile perm-to-comm: 550d (slow large schemes).
- Cumulative commencement at 24/48/72 months: 82.3% / 95.4% / 99.7% (E17).

### Phase 1 tournament — champion
- Log-normal AFT wins AIC (690,626) and concordance (0.622) narrowly.
- Weibull AFT very close (AIC 691,877, concordance 0.621).
- Cox PH concordance 0.621.
- LightGBM dark-permission classifier AUROC **0.933**; logistic baseline 0.696 — strong evidence of non-linearity.

### KEEP findings from Phase 2 (E01-E26)
- **E02 multi-unit restrict**: median jumps from 232d to 399d (+167d) — single-unit dwellings dominate the fast-start mode.
- **E04 size-stratum monotone**: 160 / 291 / 356 / 392 / 574 days as size grows. 200+ schemes take 3.6× longer to commence than 1-unit.
- **E06 Dublin < non-Dublin**: 195 vs 240 days (Dublin faster, driven by composition — fewer one-offs).
- **E07 SHD era**: permissions granted 2017-2021 commence 73d later than non-SHD.
- **E09 apartment vs dwelling CCC**: +54d for apartments.
- **E10 AHB vs private CCC**: AHB +46d slower to certify (contrary to prior — likely funding-compliance overhead).
- **E11 Section 42 extension proxy**: +446d — largest single Phase 2 effect. Real-options evidence.
- **E12 multi-phase**: +288d permission-to-commencement — second-largest single lever.
- **E15 small vs large CCC**: large -46d faster to CCC (economies of scale).
- **E17 cumulative shares**: at 24m 82.3%; at 48m 95.4%; at 72m 99.7% (dark fraction 0.3% by KM definition).
- **E19 LA dispersion CV 0.272**: significant LA heterogeneity (min 162d, max 454d).
- **E20 dark-permission AUROC 0.933**: strong predictive classifier.
- **E23 near-expiry mode 1.3%**: below the 2% threshold — real-options near-expiry-commencement is NOT a dominant pattern.
- **E25 placebo**: LA-shuffle collapses CV from 0.272 to 0.020 — LA signal is real.
- **E26 channel**: CCC filing rate CV 0.47 across LAs, range 11-69% — large channel-reporting artefact.

### Phase 2.5 interaction findings
- **I01 Dublin × apartment = +132d**: Dublin apartments take 607d to CCC vs 453d for Dublin dwellings (154d Dublin-only gap) vs 22d non-Dublin gap. Apartment slowdown is Dublin-specific.
- **I02 AHB × size = +44d**: AHB speedup vanishes for large schemes.
- **I03 Dublin × COVID = +14d**: Dublin slightly more COVID-slowed.
- **I04 apartment × COVID = -41d**: apartment cohort post-COVID selected for faster projects (cohort-composition effect).
- **I05 year × Dublin Cox**: +0.00005 per year (p=0.003) — Dublin's relative hazard rising slowly.

### Phase B discovery
- Top 15 delivery cells dominated by mid-to-large dwelling schemes in Dublin commuter counties (Fingal, South Dublin, Wicklow) and selected urban LAs (Clare, Kilkenny, Cork City, Galway).
- Wicklow 200+ dwelling: 94% completion probability within 48 months.
- Bottom cells: single-unit dwellings in slow-filing counties — but this is largely channel-reporting (owners don't file CCC), not true non-completion.
- Recommendation: scale-up of mid-size (10-199 unit) dwelling-house schemes in high-execution LAs is the empirically supported delivery pattern.

## Overclaim guardrails
- Median perm-to-comm is for OBSERVED commencement events only; KM-adjusted median (including censored) is identical (232d) because >99% of permissions commence by 72m.
- "Dark permission rate 0.3%" in the BCMS data should be read as lower-bound on the *filed* dark rate; true economic dark rate is unknown due to channel-reporting.
- LA-level CCC-rate comparisons confound filing rigor with completion rate.
- Apartment-cohort size is small (4,481 CCC observations) — conclusions about apartment interactions should be robustness-checked.
- No causal claims; all estimands are descriptive conditional on BCMS data availability.

## Methodology guardrails

- Never impute CCC_Date_Validated; treat as right-censored.
- Always report both unit-weighted and project-weighted aggregates.
- Always stratify by (a) apartment/dwelling and (b) Dublin/non-Dublin when publishing a single-number result.
- Include cohort-year FEs and LA FEs in every Cox fit; omit only for illustrative Kaplan-Meier.
- Bootstrap CIs (1000 replicates) for any published point estimate.
- Seed `np.random.default_rng(42)`.
