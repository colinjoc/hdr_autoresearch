# Blind Review: PL-4 Lapsed Irish Planning Permissions

**Reviewer:** Independent Phase 2.75 blind reviewer
**Date:** 2026-04-16
**Decision:** MAJOR REVISION

---

## Summary assessment

The paper asks an important and policy-relevant question -- what share of Irish residential planning permissions lapse without being built? -- and brings genuinely useful data to bear (national planning register + BCMS commencement notices). However, the paper's central empirical finding is fundamentally compromised by a failure to distinguish **permission lapse** from **data-join failure**. The distinction is not merely academic: my spot-checks of the raw data reveal that the entire LA-level variation in "lapse rates" (from 0% to 56%) is almost perfectly explained by whether the Planning Authority's application-number format is compatible between NPR and BCMS, rather than by any genuine difference in commencement behaviour.

The paper does acknowledge this issue in Section 8 (Caveats) and partially addresses it through normalisation experiments (E02, E19). But the acknowledgement is inadequate relative to the severity of the problem. The headline 27.4% figure, the 23.1% "preferred" figure, the GBM champion model, the Phase B stratum probabilities, and the policy conclusions all rest on an assumption that the remaining non-matches after normalisation are predominantly genuine lapses. My review finds this assumption to be unsupported and likely false.

---

## Critical findings from spot-checks

### 1. Application-number format mismatch drives LA-level variation

I examined the raw application-number formats for LAs at both extremes of the "lapse" distribution:

- **0% "lapse" LAs** (Carlow, Laois, Leitrim, Sligo, Galway City): These use simple numeric formats (e.g., `18222`, `17409`, `171`) that are trivially matchable to BCMS records using the same format.

- **High "lapse" LAs** (Cork County 55.4%, Cork City 56.6%, DCC 49.2%, Donegal 48.9%, Tipperary 43.7%): These use complex formats with year-prefixes, leading zeros, and fundamentally different conventions between NPR and BCMS. For example:
  - **Cork County** NPR: `08/693`, `25/4037` -- normalises to `8693`, `254037`. BCMS: `244669`, `22/06627` -- normalises to `244669`, `2206627`. These formats are structurally incompatible even after normalisation.
  - **Donegal** NPR: `2351312`, `2660002`. BCMS: `23/51546`, `PG22/12`. Completely different format conventions.
  - **Tipperary** NPR: `17600100`, `18600239`. BCMS: `20/283 PL92.308934`, `2360984`. Again, structurally incompatible.

The "0% lapse" finding for Carlow, Laois, etc. does not mean every permission commenced; it means the application-number format is simple enough that the join succeeds for every row. Conversely, Cork County's 55.4% "lapse" with n=8,512 (the single largest contributor to the headline rate) is almost certainly dominated by join failure, not genuine lapse.

### 2. The GBM is predicting join quality, not lapse

I reproduced the GBM feature importances:

| Feature | Importance |
|---------|-----------|
| la_enc (Planning Authority) | **0.845** |
| NumResidentialUnits | 0.059 |
| dublin | 0.043 |
| grant_year | 0.021 |
| has_nru | 0.018 |
| fi_requested | 0.006 |
| appealed | 0.004 |
| one_off | 0.003 |
| shd_era | 0.001 |

**84.5% of the model's predictive power comes from the Planning Authority label.** The model is learning which LAs have compatible application-number formats, not which permissions genuinely lapse. The AUC of 0.826 is a measurement of join-quality heterogeneity across LAs, not predictive power for lapse. The temporal validation AUC of 0.836 (E25) similarly reflects that LA format differences are temporally stable -- of course they are; Cork County did not change its numbering convention between 2017 and 2019.

This invalidates the entire model-based narrative in Sections 3.3-3.4 and the Phase B commencement-probability strata, which inherit the same artefact.

### 3. The `0_or_na` band (n=27,488) is contaminated

The `0_or_na` size band comprises 59.7% of the cohort (27,488 of 46,073 rows) and shows 39.4% "lapse." These are rows where NumResidentialUnits is not populated, identified as "residential" solely by description-keyword matching. My spot-check of descriptions in this band reveals:

- **"storey" false positives** (5,694 rows): "a single storey stand-alone building... used as a photo-booth facility", "a single storey extension to the rear of an existing retail premises", "a single storey industrial unit." These are clearly non-residential.
- **"flat" false positives** (662 rows): "inflatable, multi use, floating play area" (matching "flat" in "inflatable").
- **"domestic" false positives** (607 rows): "extension to existing domestic garage" for commercial use, "change of use of domestic garage to pre-school facility."

At minimum 5,694 rows (and likely many more) in the `0_or_na` band are non-residential applications that were misclassified by the keyword regex. These non-residential applications would naturally not have BCMS commencement notices (since BCMS is primarily for building-regulation purposes on actual construction), inflating the apparent "lapse" rate. The paper mentions this issue in Section 2.1 but does not quantify the false-positive rate or exclude these rows from the headline.

### 4. The BHQ15 cross-check (E20) is inconsistent

E20 reports a ratio of 1.297 -- the paper's 2019 NRU sum (18,012 units) is 30% higher than CSO BHQ15 (13,885 units). The paper treats this as a "broad sanity check" (the test asserts only 0.1 < ratio < 10). But a 30% excess is not reassuring; it suggests the paper's residential filter is over-inclusive, consistent with the false-positive problem above. CSO BHQ15 counts permissions granted by LAs; there is no reason our NRU-only count for the same year and application type should exceed it by 30% unless either (a) our definition of "residential" is broader than CSO's, or (b) there is a counting discrepancy. This should be investigated, not hand-waved.

### 5. Pre-2014 BCMS coverage concern

BCMS became operational around 2014. The paper's cohort includes 2014 and 2015 grants. A permission granted in early 2014 could have been commenced before BCMS was fully operational, in which case the commencement notice might not exist in the database -- producing a false "lapse." The paper does not test whether 2014 grants have anomalously high non-commencement rates purely due to BCMS coverage gaps (as distinct from the NRU-field-coverage issue it does discuss). The 2014 rate of 55.4% is the highest single year and could be partly explained by this.

### 6. The 23.1% "preferred" headline (2017-2019) is still contaminated

The paper identifies E15 (NRU>0 only, 2017-2019) as showing a 9.49% lapse rate, but then buries this in the experiments section and instead promotes the 23.1% (2017-2019 all) as the "preferred headline." The 23.1% figure still includes the `0_or_na` band for 2017-2019 (n=20,101 desc-only rows with 35.6% "lapse" per E24). The honest preferred figure should be 9.5% (NRU>0 only), which is consistent with international comparables (UK 6-14%, NZ 10-20%) and does not require the description-matching filter that introduces false positives.

---

## Mandated experiments

### R1: Formal join-failure audit

For each LA, compute the match rate separately for NPR records where the Application Number format is "simple" (purely numeric) vs "complex" (contains letters, slashes, or mixed conventions). Report the per-LA match rate for simple-format records only, and compare to the per-LA match rate for complex-format records. This will quantify what fraction of "non-matches" is driven by format incompatibility. As a further check, manually inspect 50 random non-matched records from Cork County, Tipperary, and Donegal to determine whether the commencement notice exists in BCMS under a different number format.

### R2: Restrict headline to NRU>0 subsample only

The preferred headline rate must be computed on the NRU>0 subsample (E15 = 9.49%, n=18,403 for 2017-2019). The full-cohort 27.4% and the 2017-2019 23.1% must be clearly labelled as "upper bounds that include description-matched rows with high false-positive rates and format-driven join failures." The abstract must lead with the NRU>0 figure, not the inflated all-cohort figure.

### R3: DCC-specific format analysis

Dublin City Council (49.2% "lapse", n=2,559) uses `NNNN/YY` and `WEBxxxx/YY` formats. BCMS for DCC appears to use the same convention. Therefore DCC's high rate may reflect genuine non-commencement rather than format mismatch. Verify this by computing the DCC match rate separately for `NNNN/YY` vs `WEBxxxx/YY` format records, and compare to non-Dublin LAs that also use slash-separated formats (e.g., Cork County `YY/NNNN`). Report the DCC-specific NRU>0 lapse rate with Wilson CI.

### R4: Exclude or flag 2014-2015 permissions

Compute the headline rate excluding 2014-2015 (i.e., 2016-2019 only) to test whether BCMS coverage gaps in its early operational years inflate the non-commencement rate for the earliest cohort years. If the 2016 rate is materially different from 2014-2015, the paper should restrict the primary analysis window to 2016-2019 or 2017-2019.

### R5: Bootstrap CIs on the preferred headline rate

The current Wilson CIs assume IID observations. Permissions within the same LA are not independent (LA-level format effects create intra-cluster correlation). Compute cluster-bootstrap 95% CIs (clustered by LA) on the NRU>0 headline rate to assess whether the apparent precision (CI width ~0.8pp) is overstated.

### R6: GBM sensitivity analysis -- matching artefact vs genuine predictors

Retrain the GBM excluding `la_enc` and `dublin` (the format-proxy features). Report the resulting AUC. I predict it will drop to approximately 0.55-0.65, confirming that the model has negligible genuine predictive power for lapse after removing format-driven features. If so, the paper must substantially revise or remove the model narrative. Also train the GBM on the NRU>0 subsample only (where format effects are attenuated by more complete data) and report that AUC separately.

### R7: False-positive rate in description matching

For a random sample of 200 rows from the `0_or_na` band, manually classify each development description as (a) genuinely residential, (b) non-residential but matched by keyword, or (c) ambiguous. Report the false-positive rate. If it exceeds 15%, the description-matched rows should be excluded from the primary analysis and reported only as a sensitivity check.

### R8: Cork County reconciliation

Cork County Council contributes 8,512 rows (18.5% of the cohort) with a 55.4% "lapse" rate. Given the demonstrated format incompatibility between NPR (`YY/NNN`) and BCMS (`YYNNNNN` or `YY/0NNNN`), this LA alone contributes approximately 4,700 false "lapses" -- roughly 37% of the total 12,631 non-matches. The paper must either (a) develop a Cork-specific normalisation that accounts for the different zero-padding and separator conventions, or (b) exclude Cork County from the headline and report it separately with a format-mismatch caveat.

### R9: Validate 0% lapse LAs

The five LAs with 0% lapse (Carlow, Laois, Leitrim, Galway City, Cavan/Sligo) should be validated by checking whether they genuinely have 100% commencement or whether the 0% rate simply reflects perfect format matching. Specifically: for these LAs, check whether any permissions in the cohort have an ExpiryDate that has passed (i.e., the 5-year validity has expired without extension). If such expired-and-unmatched permissions exist, the 0% rate is correct; if all permissions have future expiry dates or extensions, the 0% rate is an artefact of the data window.

### R10: Phase B stratum revision

All Phase B commencement-probability strata must be recomputed on the NRU>0 subsample only, and flagged for LA-level format-matching reliability. Strata for Cork County, Donegal, and Tipperary should be marked as unreliable due to demonstrated format incompatibility. The risk-category classification should not be presented as actionable without the join-failure caveat.

---

## Additional issues

1. **Paper Section 4.3 claims the Dublin premium "persists across all size bands"** but the interaction experiments (IX_size=1_dub=True: 38.7%, n=452 vs IX_size=1_dub=False: 8.3%, n=15,971) show that even for single-unit permissions, Dublin has 4.7x the "lapse" rate. For single-unit permissions from NRU-flagged records, a 38.7% non-commencement rate is implausible as genuine lapse (single-unit = likely self-build = high commencement intent). This strongly suggests a Dublin-specific format issue rather than genuine lapse.

2. **The paper frames lapse through real-options theory** (Sections 1, literature review). This framing is intellectually interesting but premature: you first need to establish that the signal is real (i.e., that non-matches represent genuine non-commencement), and only then interpret the magnitude through an economic lens. Currently the paper is constructing an economic narrative around what is substantially a data-quality measurement.

3. **E03 one-off house analysis** (n=762, of which only 253 flagged) is severely underpowered. The paper acknowledges this but still reports a 33.6% one-off lapse rate. With n=253, the sampling noise is large, and the one-off flag is too sparsely populated to support any conclusion.

4. **The commencement-timing analysis (E23)** is only computed for matched records and is therefore selection-biased: it describes timing for permissions that successfully matched, not for all commenced permissions. If format-mismatched permissions have different timing characteristics (e.g., faster commencement from simple-format rural LAs), the median 128 days is biased.

5. **Section 7.1 policy claim** ("reduces actionable near-term supply by roughly one-quarter") directly uses the contaminated headline rate. This claim must be revised to use the NRU>0 rate (9.5%), which would change the policy conclusion to "reduces actionable supply by roughly one-tenth" -- a materially different message.

6. **The paper's literature review is strong** (7 themes, international comparables, real-options theory, Irish planning law). This is genuine intellectual work. The methods are also generally sound (Wilson CIs, proper cohort definition, survival analysis). The problem is not the framework -- it is the data-join quality, which undermines the empirical foundation.

---

## Decision rationale

The paper cannot be accepted in its current form because the headline finding (27.4% lapse, or 23.1% preferred) is not distinguishable from join failure, and the GBM model is predicting join quality rather than lapse. These are not minor caveats -- they are load-bearing for every claim in the paper. The mandated experiments (R1-R10) are designed to separate signal from artefact. If the NRU>0, format-audited lapse rate converges to ~9-12%, the paper becomes a solid contribution with an honest, lower headline. If the format-audit reveals that the normalisation function recovers most Cork/Donegal/Tipperary matches, the current headline may be approximately correct. Either way, the paper must present the evidence and let the reader judge, rather than burying E15 (9.5%) in the experiments section while promoting 27.4% in the abstract.

**Decision: MAJOR REVISION.** All 10 mandated experiments (R1-R10) must be completed before resubmission.
