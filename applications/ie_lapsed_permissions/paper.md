# How Many Irish Planning Permissions Actually Lapse? A National Cohort Study 2014-2019

## Abstract

Ireland's housing crisis discourse assumes that granted planning permissions translate to imminent supply. We test this by linking the national planning register (491,206 applications) to the Building Control Management System (BCMS) commencement-notice database for the cohort of residential permissions granted 2014-2019. A critical methodological challenge is that non-commencement in our data conflates genuine permission lapse with data-join failure caused by incompatible application-number formats across the two registers. Our formal audit (R1) finds that "simple-format" application numbers match at 88.6% while "complex-format" numbers match at only 53.0%, confirming that application-number format drives most of the observed LA-level (Local Authority-level) variation in non-commencement rates.

Our preferred headline, restricted to the clean subsample where NumResidentialUnits (NRU) is populated (NRU>0, 2017-2019, n=18,403), yields a non-commencement rate of **9.5% (95% cluster-bootstrap CI: 4.4-15.6%)**. The wide confidence interval reflects substantial intra-cluster correlation: LA-level format-matching heterogeneity inflates uncertainty by 13x compared to naive IID assumptions. This 9.5% rate is consistent with international comparables (United Kingdom 6-14%, New Zealand 10-20%) and represents a credible lower bound on genuine lapse.

The raw all-cohort non-commencement rate (27.4%) and the 2017-2019 all-filter rate (23.1%) are upper bounds that include description-matched rows with a 15-34% false-positive rate (R7) and substantial format-driven join failures. These figures should not be cited as lapse rates. A gradient-boosting classifier trained without LA-encoding features achieves AUC 0.583 on the NRU>0 subsample (R6), indicating negligible genuine predictive power for lapse beyond data-quality artefacts. The original AUC of 0.826 was predominantly predicting which LAs have compatible application-number formats.

The policy implication is revised: the "60,000 live permissions" figure overstates actionable housing supply by approximately 5-15% due to genuine lapse, not the previously claimed 15-25%. The 2025 Planning and Development (Amendment) Act Section 28 targets a real but smaller problem than earlier estimates suggested.

## 1. Introduction

Ireland's Planning and Development Act 2000 establishes that a planning permission is valid for 5 years from grant (Section 40), extendable under Section 42 where substantial works have been carried out or exceptional circumstances exist. Since the housing crisis intensified from 2016 onward, a persistent policy question has been: how many of the "live" permissions in the system represent genuine near-term supply? The Housing Commission Final Report (2024, P212) quotes approximately 60,000 live permissions but does not disaggregate this figure by commencement status, extension status, or lapse.

This paper provides the first national-level empirical measurement of the permission-to-commencement gap for Irish residential permissions. We define "non-commencement" operationally as the absence of a matching commencement notice in the BCMS database, and measure it for the cohort of residential PERMISSION applications granted between 2014 and 2019.

Our approach follows the real-options framing of development timing (Dixit & Pindyck 1994, P003; Titman 1985, P001; Cunningham 2006, P008): a planning permission is a call option on development, and non-exercise is rational when uncertainty about construction costs, sale prices, or regulatory conditions makes waiting more valuable than building. However, we emphasise that interpreting the lapse rate through an economic lens requires first establishing that the measured non-commencement signal is genuine rather than a data-linkage artefact. This paper devotes substantial attention to that distinction.

## 2. Data

### 2.1 National Planning Application Register

We use the National Planning Application register published by the Department of Housing, Local Government and Heritage, containing 491,206 rows covering all Irish planning applications from approximately 2012 to the ETL (Extract, Transform, Load) date of 2026-04-14. Key fields include Application Number (the matching key), Planning Authority (31 LAs), Application Type, Decision, GrantDate, ExpiryDate, and NumResidentialUnits.

A critical data-quality issue: the NumResidentialUnits field is populated for only 48-77 of 2,164-2,824 granted PERMISSION applications per year in 2014-2016, but is well-populated from 2017 onward (4,126-14,897 per year). To maintain a 2014-2019 analysis window, we identify residential applications using a dual filter: NRU > 0 OR a description-keyword match against residential terms. This expands the cohort from 18,585 (NRU-only) to 46,073 applications. However, the description-keyword filter introduces false positives (Section 2.4).

### 2.2 BCMS Commencement Notices

The Building Control Management System records commencement notices filed under Section 6 of the Building Control Act 1990. We reuse the 231,623-row BCMS dataset from the sibling PL-1 commencement-notices study, keyed on CN_Planning_Permission_Number. After deduplication (earliest commencement per permission number), we match to the national register using both exact string matching and a normalised-format match that strips separators, removes leading zeros, and standardises prefixes.

### 2.3 Join-failure vs genuine lapse: the central methodological challenge

**This section addresses the reviewer's primary finding and is critical to interpreting all results in this paper.**

The non-commencement rate observed in any register-linkage study is the sum of two components:

1. **Genuine lapse**: permissions that expire without being built, due to economic conditions, changed plans, speculative applications, or construction-cost barriers.

2. **Join failure**: permissions for which a commencement notice exists in BCMS but cannot be matched because the application-number format differs between the two registers.

Our formal join-failure audit (R1) demonstrates that these two components are not separable at the aggregate level without manual reconciliation. Key findings:

- **Format-driven match gap**: Application numbers in "simple" format (purely numeric, e.g., `18222`) match at **88.6%** (n=24,055). Application numbers in "complex" format (containing slashes, letters, or mixed conventions, e.g., `08/693`, `WEB1234/19`) match at only **53.0%** (n=22,018). The 35.6pp gap is almost entirely attributable to format incompatibility, not genuine lapse.

- **LA-level correlation**: The correlation between the share of simple-format application numbers and match rate across LAs is r=0.675. LAs with simple formats (Carlow, Laois, Leitrim, Galway City, Sligo) show 0% non-commencement; LAs with complex formats (Cork County, DCC, Donegal, Tipperary) show 40-55% non-commencement. The 0% rate for simple-format LAs was validated (R9): all five LAs use 100% simple-format numbers, all permissions have passed their expiry dates, and zero expired-unmatched records exist.

- **Cork County case study (R8)**: Cork County Council contributes 8,512 rows (18.5% of the cohort) with a 55.4% "non-commencement" rate. Enhanced normalisation recovers 1,942 additional matches (reducing the rate to 32.6%), but a substantial residual remains. Cork alone contributes 37% of all non-matches in the dataset. The Cork NPR uses `YY/NNN` format while BCMS uses `YYNNNNN` with different zero-padding, making reconciliation inherently lossy.

- **Manual audit**: Of 50 sampled non-matched records from Cork County, 40% could be recovered through alternative format normalisations. For Tipperary and Donegal, 0% could be recovered via simple format changes, suggesting either genuinely different BCMS conventions or incomplete BCMS coverage for those LAs.

### 2.4 Description-matching false positives

The `0_or_na` size band (NRU not populated, identified as residential by description keywords alone) comprises 27,488 rows (59.7% of the full cohort) and shows a 39.4% non-commencement rate. Our false-positive audit (R7) of 200 randomly sampled descriptions from this band found:

- **Clearly residential**: 47.0% (94/200)
- **Clearly non-residential**: 15.0% (30/200) -- examples include schools, hotels, industrial units, and commercial extensions matched by keywords like "storey" or "bedroom"
- **Ambiguous**: 38.0% (76/200) -- descriptions where residential vs non-residential classification requires subjective judgment

The conservative false-positive rate of 15% (considering only clearly non-residential) and the liberal rate of 34% (including half of ambiguous cases) mean that 4,100-9,300 rows in the `0_or_na` band are likely non-residential applications that would naturally have no commencement notice, mechanically inflating the apparent lapse rate.

### 2.5 CSO BHQ15 Cross-Check

The Central Statistics Office BHQ15 series reports quarterly permissions-granted for apartment and house units. Our 2019 NRU sum (18,012 units) exceeds CSO BHQ15 (13,885 units) by a ratio of 1.30 (E20), consistent with our residential filter being broader than CSO's definition. This 30% excess further supports the conclusion that description-matching over-includes non-residential applications.

## 3. Methodology

### 3.1 Cohort definition

We select all applications where Application Type = PERMISSION, Decision in {CONDITIONAL, GRANT PERMISSION, GRANT OUTLINE PERMISSION}, GrantDate year in 2014-2019, residential flag = True (NRU > 0 or description match), and not withdrawn. This yields 46,073 applications.

**Primary analysis cohort**: For the headline lapse rate, we restrict to NRU>0 and grant years 2017-2019 (n=18,403), where field coverage is reliable and description-matching false positives are excluded.

### 3.2 Outcome

The binary outcome is `lapsed = 1` if no BCMS match exists. This is an **upper bound** on the true lapse rate because it conflates genuine lapse with join failure. We present the NRU>0, 2017-2019 rate as the preferred estimate because (a) it excludes description-matched false positives and (b) the 2017-2019 window avoids BCMS ramp-up coverage gaps.

### 3.3 Tournament (Phase 1)

We compared five model families on the full-cohort lapse-prediction task:

| Model | Metric | Score |
|-------|--------|-------|
| T01: Binomial per-year | Rate std | 0.115 |
| T02: Logistic regression | AUC 5-fold | 0.739 |
| T03: Cox PH (Proportional Hazards) | C-index | 0.595 |
| T04: Gradient boosting (GBM) | AUC 5-fold | 0.826 |
| T05: Random forest | AUC 5-fold | 0.819 |

The GBM champion achieves AUC 0.826, but this result is misleading. Feature importance analysis shows that LA encoding (`la_enc`) accounts for 84.5% of the model's predictive power. The model is learning which LAs have compatible application-number formats, not which permissions genuinely lapse.

### 3.4 GBM sensitivity analysis (R6)

To test whether the model has genuine predictive power beyond format-compatibility:

- **Full model (with la_enc, dublin)**: AUC = 0.826
- **Without la_enc and dublin**: AUC = 0.727 -- a drop of 0.10, but still inflated by the `has_nru` feature (which captures whether the NRU field is populated, itself a data-quality proxy rather than a lapse predictor)
- **NRU>0 subsample without la_enc**: AUC = **0.583** -- barely above chance

The NRU>0 result is definitive: once format-proxy features are removed and the sample is restricted to well-identified residential permissions, the GBM has negligible predictive power for lapse. The remaining feature importances in the no-LA model (has_nru=0.429, NumResidentialUnits=0.329) further confirm that the model is predicting data completeness, not genuine lapse risk.

**Implication**: We do not present the GBM as a valid lapse-prediction model. The model narrative from the original draft is retracted. The feature importances are presented only as evidence of the data-quality artefact.

## 4. Results

### 4.1 Preferred headline: NRU>0, 2017-2019

**R2**: Of 18,403 residential permissions with populated NRU granted 2017-2019, **9.5% (95% Wilson CI: 9.1-9.9%)** show no BCMS commencement match.

The cluster-bootstrap confidence interval (R5), which accounts for intra-LA correlation in format-matching quality, is substantially wider: **4.4-15.6%**. The 13x inflation over the naive Wilson CI reflects that LA-level format effects create strong within-cluster dependence. The cluster-bootstrap CI should be preferred for policy use.

### 4.2 Upper-bound estimates (reported for transparency)

| Estimate | Rate | N | Notes |
|----------|------|---|-------|
| All-cohort 2014-2019 | 27.4% | 46,073 | Includes join failure + FPs |
| 2017-2019 all-filter | 23.1% | 38,504 | Still includes desc-FPs |
| 2016-2019 all-filter (R4) | 24.8% | 41,328 | Drops BCMS ramp-up years |
| NRU>0 all years | 9.3% | 18,585 | Some 2014-2016 NRU coverage gap |
| **NRU>0, 2017-2019 (preferred)** | **9.5%** | **18,403** | **Clean subsample** |

The consistent finding across all NRU>0 subsamples is a non-commencement rate near 9-10%, regardless of whether 2014-2016 is included. This stability suggests the 9.5% figure is robust to cohort-window choices.

### 4.3 Temporal decomposition

Per-year non-commencement rates (full cohort, E21):

| Year | Rate | N |
|------|------|---|
| 2014 | 55.4% | 2,164 |
| 2015 | 45.6% | 2,581 |
| 2016 | 47.7% | 2,824 |
| 2017 | 23.1% | 9,154 |
| 2018 | 22.8% | 14,453 |
| 2019 | 23.5% | 14,897 |

The break at 2017 is primarily a data-coverage effect (NRU field population) compounded by BCMS ramp-up in 2014-2015 (R4). The 2014-2015 rate (50.1%) is 2.8pp higher than 2016 (47.7%), consistent with early BCMS coverage gaps but not dramatically different, suggesting format mismatch rather than BCMS coverage is the dominant driver even for early years.

### 4.4 Dublin analysis (R3)

Dublin City Council (DCC) is a special case. DCC uses `NNNN/YY` and `WEBxxxx/YY` application-number formats. The DCC NRU>0 lapse rate is 45.7% (n=315) -- much higher than the national NRU>0 rate of 9.5%.

However, DCC's slash-format records match at only 50.0% (n=2,056), compared to Cork County's slash-format at 44.6% (n=8,512). The DCC format is structurally similar to BCMS conventions, suggesting that DCC's high non-commencement rate may contain a genuine signal -- potentially reflecting Dublin's institutional PRS developers who acquired apartment permissions but faced construction-cost escalation. However, without DCC-specific BCMS reconciliation, we cannot fully separate format effects from genuine lapse for DCC.

### 4.5 Scheme size

Size-stratified rates for the NRU>0 subsample:

| Size band | Rate | N |
|-----------|------|---|
| 1 unit | 9.1% | 16,423 |
| 2-4 units | 12.7% | 1,461 |
| 5-49 units | 16.3% | 552 |
| 50+ units | 18.8% | 149 |

The monotonically increasing rate with scheme size is consistent with real-options theory: larger schemes have higher exercise costs and more option value from waiting. The 9.1% rate for single-unit permissions (predominantly self-builds) represents the strongest signal of genuine non-commencement, as these have the simplest application-number formats and highest commencement intent.

### 4.6 Planning Authority variation

LA-level variation is extreme (E10): five LAs show 0% non-commencement (all using simple numeric formats validated in R9), while Cork County shows 55.4% and Cork City 56.6%.

The 0% rate for Carlow, Laois, Leitrim, Galway City, and Sligo has been validated: these LAs use 100% simple-format application numbers, all permissions in the cohort have passed their expiry dates, and zero expired-unmatched records exist. The 0% rate reflects perfect format matching, not necessarily 100% commencement. However, the absence of any expired-unmatched records is consistent with very high genuine commencement rates in these rural LAs.

### 4.7 Commencement timing

For matched permissions, median time-to-commence is 128 days (IQR 57-265 days, P90 = 551 days; E23). This is computed only for successfully matched records and is therefore selection-biased: it describes timing for permissions where format matching succeeded, which may differ from the full population.

### 4.8 Extension proxy

Only 0.77% of matched permissions with both dates show commencement after ExpiryDate (E11, n=179). This low rate suggests that most commenced permissions start well before the 5-year validity expires.

## 5. Phase B: Commencement Probability by Stratum (Revised, R10)

Phase B strata have been recomputed on the NRU>0, 2017-2019 subsample only, with format-reliability flags. Strata for Cork County, Donegal, and Tipperary are marked as UNRELIABLE due to demonstrated format incompatibility. Among the 87 strata:

- 72 strata are format-RELIABLE
- 15 strata are format-UNRELIABLE (Cork County, Donegal, Tipperary)

Risk distribution for strata with n >= 30:
- RELIABLE (commencement probability > 0.75): 30 strata, 14,186 permissions
- MODERATE (0.50-0.75): 9 strata, 3,538 permissions
- RISKY (0.25-0.50): 2 strata, 99 permissions
- DANGER (< 0.25): 0 strata

**Caveat**: Even the RELIABLE strata inherit the overall 9.5% non-commencement rate, which itself is an upper bound on genuine lapse. The strata should be used for comparative ranking across LAs and size bands, not as absolute lapse probabilities.

## 6. Policy Implications

### 6.1 The "60k permissions" figure (revised)

The Housing Commission's "60,000 live permissions" figure should be adjusted by the NRU>0 non-commencement rate of approximately 9.5% (cluster-bootstrap CI: 4.4-15.6%). This implies that **3,000-9,000 of the 60,000 may be genuinely inactive**, reducing actionable near-term supply by **5-15%** -- material but substantially less than the 15-25% implied by the original 23-27% headline.

The previous estimate of "roughly one-quarter" is retracted as it was inflated by join failure and description-matching false positives.

### 6.2 The 2025 Amendment Act Section 28

Section 28 of the 2025 Planning and Development (Amendment) Act allows uncommenced residential permissions to be extended by up to 3 additional years. Our revised estimate suggests it targets approximately 5-15% of the permission pipeline, not 23-27%. Whether this changes behaviour depends on whether the binding constraint is the clock or the economics -- our evidence favours the latter.

### 6.3 LA-level heterogeneity

The extreme LA-level variation (0% to 55%) is primarily a data-linkage artefact. After restricting to NRU>0, the variation narrows substantially. Genuine heterogeneity likely exists (Dublin vs rural LAs) but cannot be reliably estimated without LA-specific application-number reconciliation.

## 7. Caveats

1. **Non-commencement does not equal lapse.** Our 9.5% headline is still an upper bound on genuine lapse. It includes some residual join failure (particularly for LAs with complex number formats) and permissions extended under Section 42 but not yet commenced.

2. **Join-failure contamination is not fully resolved.** Even in the NRU>0 subsample, LAs with complex formats contribute non-matches that inflate the rate. The cluster-bootstrap CI (4.4-15.6%) captures this uncertainty.

3. **Pre-2017 data is excluded from the headline.** The 2014-2016 cohort is identified through noisier description-matching and contributes disproportionately to the inflated all-cohort rate (49.2% vs 23.1%).

4. **Description-matching false positives inflate the all-cohort rate.** The 0_or_na band has a 15-34% false-positive rate (R7). Non-residential applications matched by keywords like "storey" or "domestic" would naturally lack BCMS commencement notices.

5. **No extension data.** The absence of a national Section 42 extension dataset means we cannot distinguish "extended and waiting" from "genuinely lapsed."

6. **GBM model is retracted as a lapse predictor.** The original AUC of 0.826 reflected format-matching quality, not lapse risk. On the clean NRU>0 subsample without LA features, AUC drops to 0.583 (R6).

7. **Cork County alone contributes 37% of all non-matches.** The Cork NPR-to-BCMS format incompatibility is the single largest source of apparent non-commencement. Enhanced normalisation recovers 1,942 additional matches (R8) but a substantial residual remains.

8. **Dublin's elevated rate may reflect genuine signal but is unconfirmed.** DCC's NRU>0 rate of 45.7% is an outlier that could reflect either format effects or genuine Dublin-specific non-commencement. Without DCC-specific BCMS reconciliation, this cannot be resolved.

9. **Right-censoring affects 2019.** Some 2019 permissions may still have live extensions (up to 2029 under old s42, 2027 under new s28).

10. **Commencement-timing statistics are selection-biased.** The median 128 days is computed only for successfully matched records. If format-mismatched permissions have different timing profiles, this median is biased.

## 8. Conclusion

Ireland's residential permission-to-commencement gap is measurable and meaningful but smaller than raw register-linkage suggests. The best estimate from the clean NRU>0, 2017-2019 cohort is that approximately **9.5% (cluster-bootstrap CI: 4.4-15.6%)** of granted residential permissions show no commencement notice match. This is consistent with international comparables (UK 6-14%, NZ 10-20%) and represents a credible upper bound on genuine lapse.

The raw all-cohort rate of 27.4% and the 2017-2019 rate of 23.1% are substantially inflated by (a) application-number format incompatibility between registers (accounting for a 35.6pp match-rate gap between simple and complex formats), (b) description-matching false positives (15-34% of the 0_or_na band), and (c) BCMS coverage gaps in 2014-2015. These figures should be cited only as upper bounds with explicit join-failure caveats.

The gradient-boosting model is retracted as a lapse predictor: its AUC of 0.826 was predicting join quality (84.5% feature importance on LA encoding), not genuine lapse risk. On the clean subsample without format-proxy features, AUC drops to 0.583.

The policy implication is bounded: Ireland's permission pipeline loses approximately 5-15% to genuine non-commencement, not 15-25% as raw rates suggest. The 2025 Amendment Act Section 28 targets a real but bounded problem. The binding constraint on permission exercise is likely economic (construction costs, financing, market absorption) rather than temporal (the 5-year validity clock).

## 9. Change Log: R1-R10 Mandated Experiments

| ID | Description | Key Finding |
|----|-------------|-------------|
| R1 | Formal join-failure audit | Simple-format match rate 88.6% vs complex 53.0%; r=0.675 correlation between format simplicity and match rate. Manual audit: 40% of Cork non-matches recoverable via format changes; 0% for Tipperary/Donegal. |
| R2 | NRU>0 headline | 9.5% [9.1-9.9%] for n=18,403 (2017-2019). Replaces 27.4% all-cohort and 23.1% 2017-2019 all-filter as headline. |
| R3 | DCC-specific format analysis | DCC NRU>0 lapse 45.7% (n=315). DCC slash-format match rate 50.0% vs Cork 44.6%. DCC may have genuine elevated lapse but cannot be confirmed without LA-specific reconciliation. |
| R4 | Exclude 2014-2015 | 2016-2019 rate 24.8% (full cohort), 9.6% (NRU>0). 2014-2015 at 50.1% vs 2016 at 47.7%: BCMS ramp-up contributes ~2.8pp but format mismatch dominates. |
| R5 | Cluster-bootstrap CIs | CI inflated 13.3x vs Wilson: [4.4%, 15.6%] vs [9.1%, 9.9%]. LA-level clustering creates substantial within-cluster dependence. |
| R6 | GBM without format proxies | AUC drops from 0.826 to 0.727 (no LA/Dublin) to 0.583 (NRU>0 no LA). Model has negligible genuine predictive power. Retracted as lapse predictor. |
| R7 | Description FP audit | 15.0% conservative, 34.0% liberal false-positive rate in 0_or_na band. Schools, hotels, industrial matched by "storey", "bedroom" keywords. |
| R8 | Cork County reconciliation | Enhanced normalisation recovers 1,942 of 4,715 non-matches (41%). Revised Cork rate: 32.6%. Cork contributes 37% of all non-matches nationally. |
| R9 | 0% LA validation | All five 0%-lapse LAs (Carlow, Laois, Leitrim, Galway City, Sligo) use 100% simple-format numbers. Zero expired-unmatched records. Consistent with very high genuine commencement but driven by perfect format matching. |
| R10 | Revised Phase B strata | 87 strata on NRU>0, 2017-2019; 15 marked format-UNRELIABLE (Cork, Donegal, Tipperary). 30 RELIABLE strata contain 14,186 permissions. |

## References

[All citations referenced by P-number from papers.csv; 300 entries covering real-options theory, Irish planning law, international comparables, development economics, and statistical methods.]
