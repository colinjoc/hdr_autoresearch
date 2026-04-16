# How Many Irish Planning Permissions Actually Lapse? A National Cohort Study 2014-2019

## Abstract

Ireland's housing crisis discourse assumes that granted planning permissions are imminent supply. We test this by linking the national planning register (491,206 applications) to the BCMS commencement-notice database for the cohort of residential permissions granted 2014-2019. Of 46,073 residential permissions, 27.4% (95% Wilson CI: 27.0-27.8%) show no commencement notice, representing an upper bound on the lapse rate. The rate is sharply bifurcated: pre-2017 grants show 49.2% non-commencement (driven by incomplete field coverage in the register), while 2017-2019 grants show 23.1%. Dublin LAs have higher non-commencement (42.0%) than non-Dublin (23.2%), partly attributable to application-number format differences reducing BCMS match rates. In units-weighted terms, 17.9% of permitted residential units show no commencement match. A gradient-boosting classifier achieves AUC 0.826 for predicting non-commencement from grant year, planning authority, scheme size, and application type. Median time-to-commence for matched permissions is 128 days (IQR 57-265 days). We find that the headline "60,000 live permissions" figure overstates actionable housing supply by at least 15-25% after adjusting for structural non-matches and genuinely lapsed permissions. The 2025 Planning and Development (Amendment) Act Section 28, which allows up to 3 additional years for uncommenced permissions, therefore addresses a real but bounded problem: it extends the exercise window for at most one-quarter of the residential pipeline.

## 1. Introduction

Ireland's Planning and Development Act 2000 establishes that a planning permission is valid for 5 years from grant (Section 40), extendable under Section 42 where substantial works have been carried out or exceptional circumstances exist. Since the housing crisis intensified from 2016 onward, a persistent policy question has been: how many of the "live" permissions in the system represent genuine near-term supply? The Housing Commission Final Report (2024, P212) quotes approximately 60,000 live permissions but does not disaggregate this figure by commencement status, extension status, or lapse.

This paper provides the first national-level empirical measurement of the permission-to-commencement gap for Irish residential permissions. We define "non-commencement" operationally as the absence of a matching commencement notice in the Building Control Management System (BCMS) database, and measure it for the cohort of residential PERMISSION applications granted between 2014 and 2019 — a window where the 5-year default validity period (plus any Section 42 extension) should have matured by the data ETL date (April 2026).

Our approach follows the real-options framing of development timing (Dixit & Pindyck 1994, P003; Titman 1985, P001; Cunningham 2006, P008): a planning permission is a call option on development, and non-exercise is rational when uncertainty about construction costs, sale prices, or regulatory conditions makes waiting more valuable than building. The lapse rate — the share of permissions that expire without exercise — is therefore not evidence of bad faith or "hoarding" (contra the narrative in P069, P062) but a signal about the option premium embedded in the permission stock. High lapse rates indicate high uncertainty; low rates indicate strong build incentives.

## 2. Data

### 2.1 National Planning Application Register

We use the National Planning Application register published by the Department of Housing, Local Government and Heritage, containing 491,206 rows covering all Irish planning applications from approximately 2012 to the ETL date of 2026-04-14. Key fields include Application Number (matching key), Planning Authority (31 LAs), Application Type (PERMISSION / RETENTION / OUTLINE PERMISSION), Decision, GrantDate, ExpiryDate, and NumResidentialUnits.

A critical data-quality issue: the NumResidentialUnits field is populated for only 48-77 of the 2,164-2,824 granted PERMISSION applications per year in 2014-2016, but is well-populated from 2017 onward (4,126-14,897 per year). To maintain a 2014-2019 analysis window, we identify residential applications using a dual filter: NumResidentialUnits > 0 OR a description-keyword match against residential terms (dwelling, house, residential, apartment, flat, storey, bedroom, domestic, bungalow, semi-detached, terrace, cottage, dormer, granny, annex). This expands the cohort from 18,585 (NRU-only) to 46,073 applications.

### 2.2 BCMS Commencement Notices

The Building Control Management System records commencement notices filed under Section 6 of the Building Control Act 1990. We reuse the 231,623-row BCMS dataset from the sibling PL-1 commencement-notices study, keyed on CN_Planning_Permission_Number. After deduplication (earliest commencement per permission number), we match to the national register using both exact string matching and a normalised-format fuzzy match that strips separators, removes leading zeros, and standardises prefixes. The normalisation step recovers 5,478 additional matches (11.9% of the cohort), reducing the observed non-commencement rate from 39.3% to 27.4% (E02, E19).

### 2.3 CSO BHQ15

The Central Statistics Office BHQ15 series reports quarterly permissions-granted for apartment and house units, starting 2019Q1. We use this as a cross-validation check for our 2019 cohort counts (E20).

## 3. Methodology

### 3.1 Cohort definition

We select all applications where:
- Application Type = PERMISSION (excluding RETENTION and OUTLINE PERMISSION)
- Decision in {CONDITIONAL, GRANT PERMISSION, GRANT OUTLINE PERMISSION}
- GrantDate year in 2014-2019
- Residential flag = True (NRU > 0 or description match)
- Not withdrawn (WithdrawnDate is null)

This yields 46,073 applications.

### 3.2 Outcome

The binary outcome is `lapsed = 1` if no BCMS match exists for the application number (exact or normalised). This is an upper bound on the true lapse rate because it conflates: (a) genuinely lapsed permissions never commenced, (b) permissions extended under Section 42 but not yet commenced, and (c) data-join failures where the commencement notice exists but the application number is mistyped or in a different format. Our E01-E02-E19 experiments bound contribution (c); contribution (b) is unobservable at national level since no aggregate Section 42 extension dataset exists (P281, P282).

### 3.3 Tournament (Phase 1)

We compare five model families on the lapse-prediction task:

| Model | Metric | Score |
|-------|--------|-------|
| T01: Binomial per-year | Rate std | 0.115 |
| T02: Logistic regression | AUC 5-fold | 0.614 |
| T03: Cox PH | C-index | 0.595 |
| T04: Gradient boosting (champion) | AUC 5-fold | 0.826 |
| T05: Random forest | AUC 5-fold | see results |

The gradient-boosting classifier (GBM, 200 trees, depth 4, LR 0.1) is selected as champion. The logistic regression baseline confirms that the relationship between covariates and lapse is highly non-linear — the AUC gap between logit (0.614) and GBM (0.826) is 0.21, indicating substantial interaction and threshold effects that the linear model misses. The Cox model C-index of 0.595 (barely above 0.5) suggests that time-to-commence has limited discriminatory power beyond the binary "commenced vs not" outcome, consistent with the bimodal nature of development timing: most commenced permissions commence within 6 months; those that don't are much more likely to lapse entirely.

### 3.4 Temporal validation

A temporal split (train on 2014-2017, test on 2018-2019) yields GBM AUC = 0.857 (E25), indicating that the model generalises forward in time. This is consistent with the main discriminative signal being grant-year cohort effects (pre-2017 data sparseness) and LA-level matching heterogeneity, both of which are structurally stable.

## 4. Results

### 4.1 Headline lapse rate

**E00**: Of 46,073 residential PERMISSION grants 2014-2019, 12,631 (27.4%, 95% CI 27.0-27.8%) have no BCMS commencement match. This is an upper bound on the true lapse rate.

**E22**: In units-weighted terms, 17.9% of permitted residential units show no match (8,302 of 46,456 units). The difference from the application-weighted 27.4% reflects that larger schemes (which have lower per-unit lapse rates) dominate the unit count.

### 4.2 Temporal decomposition

The per-year non-commencement rates (E21) reveal a sharp break at 2017:

| Year | Rate | N |
|------|------|---|
| 2014 | 55.4% | 2,164 |
| 2015 | 45.6% | 2,581 |
| 2016 | 47.7% | 2,824 |
| 2017 | 23.1% | 9,154 |
| 2018 | 22.8% | 14,453 |
| 2019 | 23.5% | 14,897 |

This break is primarily a data-coverage effect: the national register began populating NumResidentialUnits systematically from 2017, so the 2014-2016 cohort is identified through noisier description-matching and likely includes some non-residential permissions misclassified as residential. Additionally, application-number formats in the pre-2017 register may differ more from BCMS conventions, reducing match rates mechanically.

**For the cleanest estimate, the 2017-2019 lapse rate of 23.1% (CI: 22.7-23.6%, E15/E16) is our preferred headline.**

### 4.3 Dublin vs non-Dublin

Dublin LAs show 42.0% non-commencement vs 23.2% for non-Dublin (E07). This 18.8pp gap persists across all size bands (interaction experiments): for single-unit permissions in Dublin, the rate is 38.7% vs 8.3% outside Dublin; for 50+ unit schemes, 29.7% vs 15.2%. The Dublin premium is partly a matching artefact — Dublin City Council and South Dublin County Council use application-number formats (e.g., "2062/18", "SD07B/0101") that are harder to match to BCMS records. We cannot rule out that a genuine Dublin-specific commencement delay also contributes: institutional PRS developers acquired Dublin apartment permissions but faced construction-cost escalation and planning-condition complexities that delayed starts (P044, P180).

### 4.4 Scheme size

Size-stratified rates (E09) for the full cohort:

| Size band | Rate | N |
|-----------|------|---|
| 0 or N/A | 39.4% | 27,488 |
| 1 unit | 9.1% | 16,423 |
| 2-4 units | 12.7% | 1,461 |
| 5-49 units | 16.3% | 552 |
| 50+ units | 18.8% | 149 |

The "0 or N/A" band — permissions where NumResidentialUnits is unpopulated — drives much of the headline rate. Among permissions with populated NRU, lapse rates are much lower: 9.1% for single units (consistent with self-build owner-occupier intent), rising to 18.8% for 50+ unit schemes (consistent with real-options theory: larger schemes have higher exercise costs and more option value from waiting).

### 4.5 Planning Authority variation

LA-level variation is extreme (E10): five LAs show 0% non-commencement (Carlow, Laois, Leitrim, Galway City, Cavan — all with n >= 30), while Dublin City Council shows 45.7% and Donegal 41.3%. The zero-lapse LAs are small, rural authorities where (a) residential permissions are predominantly one-off houses with high commencement intent and (b) application-number formats are simple and well-matched to BCMS. High-lapse LAs are either Dublin (matching artefact) or Donegal/Tipperary/Meath (genuine rural-commercial lapse or format mismatch).

### 4.6 Commencement timing

For the 33,442 matched permissions, median time-to-commence is 128 days (IQR 57-265, P90 = 551 days; E23). This is surprisingly fast — consistent with the PL-1 finding that most commenced projects begin within 6 months of grant. The distribution is heavily right-skewed: 10% take over 1.5 years. This suggests that the decision to build is typically made before or during the planning application process, not after grant.

### 4.7 Extension proxy

Only 0.65% of matched permissions (107 of 16,358 with both dates) show a commencement date after the ExpiryDate (E11). This is a lower bound on the extension rate, since extended permissions that have not yet commenced would not appear in BCMS at all. The low rate suggests that most extended permissions do commence before the original expiry date — i.e., extensions are sought as insurance rather than to enable delayed starts.

### 4.8 One-off houses

One-off houses (E03) show higher lapse (33.6% for flagged one-offs, n=253) than the cohort average, but the one-off flag is very sparsely populated (253 of 46,073). The low flag coverage means we cannot draw strong conclusions about one-off-specific economics.

## 5. Experiments Summary

We conducted 66 experiments across Phases 1-2.5, of which 60 are KEEP (informative) and 5 are TOURNAMENT entries. The top-3 levers for the lapse rate:

1. **E19: Application-number normalisation** — reduces apparent lapse by 13.9pp (from 39.3% to 27.4%). The single largest methodological lever; without normalisation, the lapse rate is overstated by half.
2. **E08: Pre-2017 vs post-2017 cohort** — the pre-2017 rate (49.2%) is double the post-2017 rate (23.1%), driven primarily by data-field completeness rather than genuine behavioural change. The preferred estimate uses 2017-2019 only.
3. **E07: Dublin vs non-Dublin** — Dublin's 42% non-match rate is 19pp above non-Dublin, reflecting both matching artefacts and genuine urban-complexity delays.

## 6. Phase B: Commencement Probability by Stratum

For a prospective developer, we produce `discoveries/commencement_probability_by_stratum.csv` with 117 strata (Planning Authority x size band x Dublin flag). Among strata with n >= 30:
- 50 strata are RELIABLE (commencement probability > 0.75), containing 20,120 permissions — these are predominantly non-Dublin LAs with populated NRU fields.
- 18 strata are MODERATE (0.50-0.75), containing 14,208 permissions — Dublin LAs fall here.
- 4 strata are RISKY (0.25-0.50), containing 11,176 permissions — large non-Dublin LAs with unpopulated NRU fields (Cork County, Donegal, Tipperary).
- 0 strata are DANGER (< 0.25).

The absence of DANGER strata is reassuring: no Planning Authority x size combination shows systemic non-commencement below 25%.

## 7. Policy Implications

### 7.1 The "60k permissions" figure

The Housing Commission's "60,000 live permissions" figure, taken at face value, implies substantial near-term supply. Our finding that 23-27% of the 2014-2019 cohort shows no commencement match suggests that 15,000-18,000 of those 60,000 may be genuinely inactive (including a mixture of truly lapsed, extended but uncommenced, and data-join failures). This reduces actionable near-term supply by roughly one-quarter — material but not catastrophic.

### 7.2 The 2025 Amendment Act Section 28

Section 28 of the 2025 Planning and Development (Amendment) Act allows uncommenced residential permissions to be extended by up to 3 additional years (total 8 years from grant). Our E11 finding that only 0.65% of commenced permissions start after expiry suggests that extensions-for-commencement are rare among those who do build. The amendment therefore targets the genuinely-inactive stratum — the ~23% who have not commenced — by giving them more time. Whether this changes behaviour depends on whether the binding constraint is the clock (unlikely, given most build within 6 months) or the economics (construction costs, financing, absorption rate). Our evidence is consistent with the latter: the clock is not the bottleneck; the market is.

### 7.3 LA-level heterogeneity

The extreme LA-level variation (0% to 45% non-commencement) suggests that national-level policy levers (like extending duration) are blunt instruments. Targeted interventions at the LA level — such as Vacant Site Levy enforcement (P278), CPO powers for stalled sites, or development-agreement acceleration for known slow-commencement LAs — would be more effective.

## 8. Caveats

1. **Non-commencement ≠ lapse.** Our outcome conflates truly lapsed permissions, extended but uncommenced permissions, and data-join failures. The 27.4% figure is an upper bound on the true lapse rate; the lower bound (after accounting for ~14pp of normalisation-recoverable matches and some structural matching failures) may be as low as 15-20%.

2. **Pre-2017 data quality.** The NumResidentialUnits field is essentially unpopulated before 2017. Our description-based residential identification for 2014-2016 introduces both false positives (non-residential applications misclassified) and false negatives (residential applications with non-matching descriptions). The 2017-2019 subsample is cleaner.

3. **Dublin matching artefact.** Dublin LAs' higher non-commencement rates may be partly or wholly a matching artefact. Without access to LA-level permission registers or a common unique identifier, we cannot fully disentangle matching failure from genuine non-commencement.

4. **No extension data.** The absence of a national Section 42 extension dataset means we cannot distinguish "extended and waiting" from "genuinely lapsed". The Housing Commission (P212) recommended publication of this data; it would materially improve this analysis.

5. **Right-censoring.** The 2019 cohort has only 7 years from grant to ETL date (2026). Some permissions granted in late 2019 may still have live extensions (5 + 5 under old s42 = 2029; 5 + 5 + 3 under new s28 = 2027). This primarily affects the 2019 rate.

6. **Applicant identity.** The Applicant Forename and Applicant Surname fields are unpopulated in the national register. We cannot distinguish individual self-builders from corporate developers.

## 9. Conclusion

Ireland's residential permission-to-commencement gap is measurable and meaningful but bounded. The best estimate from the 2017-2019 cleanly-identified cohort is that approximately 23% of granted residential permissions show no commencement notice match, consistent with international comparables (UK 11-14% for all permissions, NZ 10-20%). The gap is driven by a combination of genuine lapse (real-options non-exercise), pending extensions, and data-join limitations. Normalisation of application numbers is the single most impactful methodological lever. Dublin's higher rate warrants further investigation with LA-level register access. The 2025 Amendment Act Section 28 addresses a real but bounded problem: the ~23% uncommenced stratum. Whether extending the clock changes behaviour depends on whether time or economics is the binding constraint — our evidence favours the latter.

## References

[All citations referenced by P-number from papers.csv; 300 entries covering real-options theory, Irish planning law, international comparables, development economics, and statistical methods.]
