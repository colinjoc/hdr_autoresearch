# Reviewer Second Pass: Heat-Wave Mortality

## Overall verdict
**APPROVED WITH MINOR REVISIONS**

The authors have responded substantively to every CRITICAL and MAJOR finding from the first review. The title, abstract, and headline language have been overhauled from "refuted" to "does not improve prediction at this aggregation scale." The eight new experiments (RX01-RX08) are genuinely informative, honestly reported, and in several cases strengthen the paper beyond what a revision typically achieves. The temporal CV experiment (RX01) confirms temporal leakage and is now presented alongside the shuffled KFold throughout, which is the right call. The matched case-crossover (RX08) is a strong addition that directly engages with the epidemiological literature's preferred design, and the reversed-sign finding after Tmax conditioning is striking and honestly caveated.

Two residual issues prevent a clean sign-off, both minor and fixable without re-running experiments.

## CRITICAL findings status

### C1: "The hypothesis is refuted" language
**Status:** RESOLVED
**Comment:** The title is now "Night-Time Wet-Bulb Temperature Does Not Improve Population-Week Mortality Prediction: A Pre-Specified Test on 9,276 City-Weeks." All instances of "refuted" in the abstract, headline box (Section 5.10), and conclusion (Section 7) have been replaced with "does not improve prediction at this aggregation scale" or equivalent qualified language. The abstract now carries the same limiting conditions (weekly aggregation, predominantly temperate cities, all-ages, observational) as the Discussion. This is exactly what was requested and done well.

### C2: Keep/revert threshold of 0.5 deaths as noise floor
**Status:** RESOLVED
**Comment:** RX07 provides bootstrap CIs (MAE 40.33 [39.41, 41.23]) and reports fold-level MAE std of 1.05 deaths/week. The paper now acknowledges in Section 2.6 that the 0.5-death floor is less than one standard deviation of fold-level MAE variation. RX02 provides permutation null distributions for 5 flagship features, and RX04 confirms multi-seed stability. The combination of these three experiments transforms the noise-floor claim from an assertion into a measurement. The paper appropriately notes the threshold is "approximate" and directs readers to the CIs. Well handled.

### C3: Shuffled KFold with autocorrelation features (temporal leakage)
**Status:** RESOLVED
**Comment:** RX01 is the most important experiment in the revision. The 44% MAE degradation under temporal CV (40.33 to 58.04) confirms substantial leakage, and this is reported prominently in the abstract, Section 2.6, Section 3.1, and Section 7. The paper now presents temporal CV as the primary evaluation for forecasting claims, with shuffled KFold retained for within-panel comparisons. The 15.1% improvement is qualified throughout. Night-Tw still does not help under temporal CV (58.04 vs 58.22). The paper is now honest about what the shuffled numbers mean and what they do not mean.

### C4: AUC 0.9696 label-feature tautology
**Status:** RESOLVED
**Comment:** RX03 runs the decoupled label (p_score >= 0.10 only, no meteorological gate). AUC drops from 0.98 to 0.84, confirming label-feature coupling inflation. Night-Tw still provides no marginal improvement under the decoupled label (0.844 vs 0.844). The paper now reports both labels (Sections 5.8, 5.11, 6.3) and explicitly calls the coupled AUC a "label-construction artefact," stating the decoupled AUC of 0.84 is "the more informative number." The conclusion (Section 7) now carries the caveat parenthetically. Thorough fix.

### C5: No confidence intervals on any metric
**Status:** RESOLVED
**Comment:** RX07 provides bootstrap 95% CIs for MAE, RMSE, and R-squared, reported in Section 3.1's results table and discussed in Section 2.6. Fold-level MAE std is reported. The CIs are appropriately narrow (MAE 39.41-41.23) to support the paper's claims. Adequate fix.

### C6: Title says "Refuting" -- Discussion says "not detectable"
**Status:** RESOLVED
**Comment:** Merged with C1; both are fixed by the title and language overhaul.

## MAJOR findings status

### M1: Phase 2 MAE improvement claim (15.1% inflated by leakage)
**Status:** RESOLVED
**Comment:** The paper now reports both shuffled MAE (40.33) and temporal CV MAE (58.04) side by side in Section 3.1's table and throughout. The "15.1% improvement" is qualified in the abstract, Section 1.3, and Section 7 as "acknowledged as inflated by temporal leakage from autocorrelation features." The temporal CV evaluation is identified as "the appropriate benchmark for any deployment claim." Good fix.

### M2: Counterfactual EWS specification
**Status:** RESOLVED
**Comment:** Section 5.9.4 now specifies: the literature night-Tw rule ranks weeks by the raw value of tw_night_c_max within each city and alerts on the top 5% of weeks; the dry-bulb strawman ranks by tmax_c_max; the HDR minimal detector ranks by OOF predicted probability. All use per-city top-5%-of-weeks as the alert budget. The caveat "At other alert budgets the ordering might change" is included. This is sufficient.

### M3: "Pre-registered" language
**Status:** RESOLVED
**Comment:** All instances changed to "pre-specified." Section 1.2 explicitly distinguishes this from third-party-verified pre-registration, citing Nosek et al. (2018). Clean fix.

### M4: Data sources not versioned
**Status:** RESOLVED
**Comment:** Section 2.1 now specifies download dates: "NOAA ISD data accessed via the noaa-isd Python client on 2024-11-15; Eurostat demo_r_mwk3_t last updated 2024-10-28; CDC NCHS weekly mortality via the NCHS API, vintage 2024-12-01." Sufficient for replication.

### M5: Station IDs not listed
**Status:** PARTIALLY RESOLVED
**Comment:** Section 2.1 states station IDs are listed in data_sources.md with a cross-reference. This is acceptable for a paper with a companion repository, but the paper itself still does not contain the station IDs. For a journal submission, an appendix table with the 30 station IDs would be stronger. This is a minor remaining issue.

### M6: CDC scaling method underspecified
**Status:** RESOLVED
**Comment:** Section 2.1 now specifies: "US city mortality is estimated by multiplying state-level CDC NCHS weekly mortality by a static city-to-state population ratio from the 2022 American Community Survey 1-year estimates." Clear and reproducible.

### M7: "Strictly worse" / "strictly dominated" language
**Status:** RESOLVED
**Comment:** Section 5.9.3 now reads "worse than dry-bulb Tmax at the per-city level as a single-feature classifier across all tested cities." Section 5.9.4 includes: "At other alert budgets the ordering might change; we do not claim strict dominance in the game-theoretic sense." Accurate language.

### M8: Policy recommendation overclaiming
**Status:** RESOLVED
**Comment:** Section 6.8 now opens with the full set of limitations ("based on this single observational study at weekly aggregation with acknowledged data limitations...") and softens from "do not swap" to "our findings do not support prioritizing." A call for daily-resolution, individual-level, and tropical-city extensions is explicit. The recommendation is now appropriately scoped.

### M9: Missing engagement with case-crossover literature
**Status:** RESOLVED
**Comment:** Two significant improvements. First, Section 6.7 now includes a detailed 4-point comparison with Achebak et al. (2022) covering temporal resolution, within-city conditioning, sub-weekly lag structure, and outcome definition. Second, RX08 implements a matched case-crossover design (347 sets, 3-4 controls each) and reports the striking finding that Tmax-residualized night-Tw is *lower* in lethal weeks. This is a genuine engagement with the epidemiological standard, honestly caveated as weekly rather than daily. The RX08 result strengthens the paper substantially.

### M10: Reference list too thin
**Status:** RESOLVED
**Comment:** Expanded from 17 to 31 references. The additions include Gasparrini and Armstrong (2011), Gasparrini et al. (2017), Di Napoli et al. (2021) UTCI, Liljegren et al. (2008) WBGT, ISO 7243, Nosek et al. (2018), Casanueva et al. (2019), Kjellstrom et al. (2016), Raymond et al. (2020), Hajat et al. (2006), Buzan et al. (2015), Lowe et al. (2011), Flouris et al. (2018), and Noufaily et al. (2013). Still below 100 for a paper making a strong negative claim, but the key gaps identified in the first review are filled. Adequate for this format.

## New experiments (RX01-RX08) reporting assessment

The new experiments are honestly reported:

- **RX01 (Temporal CV):** The 44% degradation is prominently flagged, not hidden. The paper does not cherry-pick the favorable shuffled number; it leads with the temporal CV result in the abstract and conclusion. Honest.
- **RX02 (Permutation null):** All p > 0.05 reported. The response notes 200 permutations (paper says 200 in Section 5.11 but the response document says 100). This is a minor inconsistency that should be corrected -- see below.
- **RX03 (Decoupled label):** AUC drop from 0.98 to 0.84 is prominently reported. The paper calls the coupled AUC a "label-construction artefact." Honest.
- **RX04 (Multi-seed):** All 6 features stable REVERT across 5 seeds. Straightforward.
- **RX05 (Summer-only):** Baseline 37.10, +tw 37.13, +stacked 37.46. Honestly reported as night-Tw not helping even in summer.
- **RX06 (Interactions):** All REVERT. Brief but adequate.
- **RX07 (Bootstrap CIs):** MAE 40.33 [39.41, 41.23], fold std 1.05. The paper acknowledges the fold-level variance exceeds the 0.5-death floor. Honest.
- **RX08 (Case-crossover):** The -0.60 C residualized difference (opposite direction) is a strong finding. Caveated as weekly, not daily. Caveated as using a global linear coefficient for residualization. Honest.

## New issues introduced by revision

### N1: Abstract CI mismatch (MINOR)
The abstract reports temporal CV MAE as 58.0 but then gives "95% CI: 39.4-41.2 for the within-panel estimate" in the same sentence. The CI is for the shuffled KFold MAE (40.33), not the temporal CV MAE. While technically the parenthetical clarifies this, the sentence structure is confusing: a reader could misinterpret the CI as belonging to the temporal CV number. Suggest restructuring to separate the two estimates more clearly, e.g., reporting the shuffled MAE with its CI first, then the temporal CV MAE as a separate sentence.

### N2: Permutation count discrepancy (MINOR)
The author response document says "100 within-city permutations per feature" for RX02 (in the C2 response) and later says "100 permutations" (in the experiment summary table). Section 5.11 of the revised paper says "200 permutations per feature." One of these is wrong. Clarify and make consistent.

### N3: No new plots for new experiments (MINOR, not mandatory)
The RX01-RX08 experiments are reported numerically in Section 5.11 but no new plots were added. A figure showing the temporal CV performance comparison (baseline vs +tw vs +stacked under temporal split) or the case-crossover residual distribution would strengthen the presentation. Not mandatory, but recommended.

## Remaining mandatory items

1. **Fix the abstract CI/temporal-CV sentence** (N1) to avoid misattributing the within-panel CI to the temporal CV MAE.
2. **Reconcile the permutation count** (N2): 100 or 200 permutations for RX02? Make the paper and response consistent.

## Revised framing assessment

The revised framing ("not detected at this aggregation scale") is appropriate. The paper now consistently:
- Qualifies the negative finding with "at the weekly aggregation scale tested here"
- Notes the city set is "predominantly temperate"
- Distinguishes between the physiological chamber measurements and the population-week inference
- Identifies daily resolution and tropical cities as the highest-priority extensions
- Softens policy language from directive ("do not swap") to evidential ("our findings do not support prioritizing")

This is the correct register for an observational null finding with acknowledged aggregation limitations. No overclaiming remains.

## Sign-off
**SIGNED OFF** -- subject to fixing the two mandatory items above (abstract CI sentence restructuring; permutation count consistency). These are editorial corrections that do not require new experiments or analysis.

2026-04-10
