# Design Variables — YC vs Non-YC

50 candidate features grouped by source, with leakage-risk annotations.

**Leakage codes:**
- `SAFE` — known at batch-entry / filing-date; no leakage.
- `MAYBE` — could be point-in-time-safe if we capture a historical snapshot; LEAKY if scraped today.
- `LEAKY` — contemporaneous snapshot reflects post-treatment outcomes; do NOT use as a pre-treatment covariate.
- `OUTCOME` — this is a dependent variable, not a covariate.

---

## Group 1 — YC JSON (yc-oss/api all.json)

| # | Feature | Type | Source field | Leakage | Notes |
|---|---|---|---|---|---|
| 1 | `batch` | categorical | `batch` (e.g., S05, W24) | SAFE | Primary strata key. |
| 2 | `batch_year` | int | derived from `batch` | SAFE | |
| 3 | `batch_season` | S/W | derived | SAFE | |
| 4 | `batch_size` | int | count per batch from JSON | SAFE | Time-varying (grew over years). |
| 5 | `industries` | list[str] | `industries` | SAFE | YC-supplied industry tags. |
| 6 | `industry_primary` | str | first entry of `industries` | SAFE | |
| 7 | `regions` | list[str] | `regions` | MAYBE | Location at time of batch; may reflect post-program HQ move. |
| 8 | `long_description` | text | `long_description` | MAYBE | Often updated post-batch; Wayback snapshot preferred. |
| 9 | `long_description_embedding` | vec[768] | sentence-BERT of #8 | MAYBE | Inherits #8 leakage. |
| 10 | `long_description_length` | int | derived | MAYBE | |
| 11 | `website_domain` | str | `website` | SAFE | Domain registration date proxies founding date. |
| 12 | `has_website` | bool | derived | SAFE | |
| 13 | `all_locations` | str | `all_locations` | LEAKY | Current offices — reflects post-batch growth. |
| 14 | `launched_at` | timestamp | `launched_at` | SAFE | Product-launch date. |
| 15 | `stage_at_batch` | enum | `stage` | LEAKY | Field is current stage; must be mapped back to batch time or discarded. |
| 16 | `team_size` | int | `team_size` | **LEAKY** | Contemporaneous; reflects growth — DO NOT use as pre-treatment covariate. Use only as outcome-adjacent. |
| 17 | `status` | enum {Active, Inactive, Acquired, Public} | `status` | OUTCOME | This is the primary outcome. |
| 18 | `slug` | str | `slug` | SAFE | Identifier only. |
| 19 | `name` | str | `name` | SAFE | Used for CIK/Form D fuzzy match. |
| 20 | `tags` | list[str] | derived from `industries` | SAFE | |

## Group 2 — SEC EDGAR Form D primary_doc.xml

| # | Feature | Type | Source field | Leakage | Notes |
|---|---|---|---|---|---|
| 21 | `cik` | int | CIK | SAFE | Entity identifier. |
| 22 | `issuer_name` | str | `issuer.name` | SAFE | |
| 23 | `issuer_state` | str | `issuer.address.state` | SAFE | State at filing. |
| 24 | `filing_date` | date | filing timestamp | SAFE | |
| 25 | `filing_quarter` | str | derived | SAFE | Align with YC batch quarter. |
| 26 | `total_offering_amount` | float | `totalOfferingAmount` | SAFE | Can be "Indefinite" — handle as NA. |
| 27 | `total_amount_sold` | float | `totalAmountSold` | SAFE | |
| 28 | `min_investment_accepted` | float | `minimumInvestmentAccepted` | SAFE | |
| 29 | `offering_exemption` | enum | `typesOfExemption` | SAFE | 506(b) vs 506(c) vs 504. |
| 30 | `industry_group` | str | `industryGroup` | SAFE | Form D industry code. |
| 31 | `type_of_filer` | enum | `typeOfFiler` | SAFE | Corp/LLC/LP. |
| 32 | `year_of_incorporation` | int | `yearOfIncorporation` | SAFE | |
| 33 | `incorporated_within_5_years` | bool | derived from #32 | SAFE | |
| 34 | `number_of_investors` | int | `numberOfInvestors` | SAFE | |
| 35 | `sales_commission_paid` | float | `salesCommissions` | SAFE | |
| 36 | `finders_fees_paid` | float | `findersFeesPaid` | SAFE | |
| 37 | `related_persons_count` | int | count of `relatedPersons` | SAFE | Proxy for board/founder team size. |
| 38 | `related_persons_states` | set[str] | from relatedPersons | SAFE | Co-investor geography. |
| 39 | `is_delaware_corp` | bool | derived | SAFE | DE-incorporation is startup-standard. |
| 40 | `first_sale_date` | date | `firstSale` | SAFE | |

## Group 3 — Derived & Matching Covariates

| # | Feature | Type | Source | Leakage | Notes |
|---|---|---|---|---|---|
| 41 | `log_offering_amount` | float | log(1 + #26) | SAFE | Primary size covariate. |
| 42 | `offering_size_band` | enum | bucket of #26 | SAFE | Discretised for CEM. |
| 43 | `msa_vc_density` | float | external (Pitchbook/Chen et al. 2010) joined on state/MSA at filing year | SAFE | Key ecosystem confounder. |
| 44 | `sector_naics_2` | str | crosswalk from #5 or #30 to NAICS 2-digit | SAFE | Harmonises YC and Form D sectors. |
| 45 | `is_sf_bay_area` | bool | from state + MSA lookup | SAFE | Explicit Bay Area indicator (Chen et al. 2010). |
| 46 | `is_nyc_metro` | bool | derived | SAFE | |
| 47 | `is_boston_metro` | bool | derived | SAFE | |
| 48 | `quarter_year_vc_total_raised` | float | external Pitchbook / NVCA | SAFE | Market-cycle covariate. |
| 49 | `quarter_year_ipo_count` | int | Ritter/SDC | SAFE | |
| 50 | `vix_at_filing` | float | CBOE VIX on filing date | SAFE | Macro risk covariate. |
| 51 | `founding_year_bucket` | enum | derived | SAFE | {2005–2009, 2010–2014, 2015–2019, 2020–2024}. |
| 52 | `pre_aws_era` | bool | #51 ≤ 2008 | SAFE | Per Ewens-Nanda-Rhodes-Kropf (2018). |

## Group 4 — Outcome Features (NOT covariates)

| # | Feature | Type | Source | Leakage | Notes |
|---|---|---|---|---|---|
| 53 | `follow_on_raise_within_3y` | bool | later Form D under same CIK, or Crunchbase join | OUTCOME | Primary outcome C1. |
| 54 | `cumulative_raised_3y` | float | sum of later Form D | OUTCOME | Outcome C6. |
| 55 | `acquired_within_7y` | bool | 8-K item 2.01 under CIK | OUTCOME | Outcome C3. |
| 56 | `ipo_within_10y` | bool | S-1 or 8-A12B under CIK | OUTCOME | Outcome C4. |
| 57 | `status_inactive_at_5y` | bool | derived from #17 + time | OUTCOME | Outcome C2. |
| 58 | `time_to_next_raise` | float days | derived | OUTCOME | Outcome C7 (survival). |
| 59 | `unicorn_flag` | bool | external valuations list (Crunchbase, CB Insights) | OUTCOME | Outcome C8; coarse. |
| 60 | `composite_success` | bool | #53 ∨ #55 ∨ #56 | OUTCOME | Outcome C5. |

## Group 5 — Optional / LEAKY features (document but do not use unless snapshot available)

| # | Feature | Type | Source | Leakage | Notes |
|---|---|---|---|---|---|
| 61 | `current_team_size` | int | YC JSON `team_size` | LEAKY | Duplicates #16. Only use if historical snapshot. |
| 62 | `twitter_followers` | int | scraped | LEAKY | Post-batch growth. |
| 63 | `linkedin_employees` | int | scraped | LEAKY | |
| 64 | `crunchbase_funding_total` | float | Crunchbase join | LEAKY for pre-treatment use | OK for outcome aggregation. |
| 65 | `founder_ivy_league` | bool | LinkedIn lookup | MAYBE | OK if snapshot is pre-batch. |
| 66 | `founder_prior_exit` | bool | LinkedIn / Crunchbase | MAYBE | OK if snapshot is pre-batch; Gompers et al. 2010 relevant. |
| 67 | `website_wayback_stack` | list[str] | archive.org snapshot at batch-start | SAFE (if snapshot is at batch-start) | G4 in research_queue. |

---

## Leakage-Safety Checklist (for Phase 2)

Before any covariate is included in the propensity model, verify:

1. **Date-of-measurement** is ≤ batch-start date.
2. **Source snapshot** is point-in-time, not current API value. Wayback Machine / SEC filing timestamps acceptable.
3. **No derivation involving outcome variables** (e.g., `log_total_raised` includes follow-on raises → LEAKY; `log_total_offered_at_batch` is SAFE).
4. **Missingness pattern is independent of treatment.** If YC companies systematically have more complete metadata because of YC's own curation, fill missing Form D fields with matched-sector-quarter medians; document that this is a known imbalance.

## Covariate Sets to Compare (named)

- **M0 (null):** batch quarter only.
- **M1 (basic):** quarter + sector NAICS-2 + state.
- **M2 (size):** M1 + log offering amount + offering size band.
- **M3 (ecosystem):** M2 + MSA VC density + Bay/NYC/Boston flags.
- **M4 (macro):** M3 + VIX + quarter-year VC totals.
- **M5 (text):** M4 + long_description embeddings.
- **M6 (founder-if-available):** M5 + ivy-league flag + prior-exit flag.

Effect attenuation across M0 → M6 is itself a headline result per **E6** in research_queue.
