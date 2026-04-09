# Data acquisition notes — building permit processing times

Phase 0 narrative complement to `data_sources.md`. All findings below come
from live API probes on 2026-04-09.

## Short version

- **Seven cities load cleanly** with the shared schema (SF, NYC, LA, Chicago,
  Austin, Seattle, Portland). Loaders were smoke-tested with `limit=1000`.
- **Per-stage timestamps exist at three tiers**:
  1. *Gold* — Seattle (per-reviewer, per-cycle, with correction wait time)
  2. *Silver* — NYC legacy BIS (6 timestamps), SF (4), LA (3), Portland (3)
  3. *Bronze* — Chicago (2 + pre-computed duration), Austin (2)
- **Two bonus cities blocked** (Boston, Philadelphia) — their open-data feeds
  omit the filing / application date entirely. A pipeline-duration question
  cannot be answered for them without a new data source.
- **Census BPS** is usable only as a macro sanity check (monthly place-level
  aggregate counts — no durations, no record-level information).

## Which cities have per-stage timestamps and which don't

| rank | city | dataset | stages exposed |
|---:|---|---|---|
| 1 | Seattle | tqk8-y2z5 | applied → reviewer-assigned → reviewer-finished (per cycle, per reviewtype) → plan-review-complete → ready-to-issue → issued. Plus pre-computed `daysoutcorrections`, `daysinitialplanreview`, `daysplanreviewcity`, `numberreviewcycles`. **Gold standard**. |
| 2 | New York City | ic3t-wcy2 | pre-filing → paid → fully-paid → approved → fully-permitted → signoff. Six timestamps per job. |
| 2b | New York City | w9ak-ipjd (DOB NOW) | filing → approved → first-permit → signoff. Four stamps. Needed for 2020+. |
| 3 | San Francisco | i98e-djp9 | filed → approved → issued → last-activity. Four timestamps — but no RFI, no plan-check cycles, no per-discipline breakdown. |
| 3 | Los Angeles | gwh9-jnip | submitted → issued → CofO, plus `business_unit` (Regular Plan Check / Express / OTC) as a pipeline-lane dimension. |
| 3 | Portland | BDS_Permit FS/22 | created → intake-complete → issued → finaled. The `INTAKECOMPLETEDATE` split cleanly isolates the plan-check phase. |
| 4 | Chicago | ydr8-5enu | application start → issued, plus pre-computed `processing_time` days and a `review_type` lane. |
| 4 | Austin | 3syk-w9eu | applied → issued → status-date. Matches the research question framing but no intra-pipeline detail. |
| — | Boston | approved-building-permits | **no filing date** — only `issued_date`, `expiration_date`. |
| — | Philadelphia | phl.carto.permits / li_permits | **no filing / application date** — only `permitissuedate`, `permitcompleteddate`, `certificateofoccupancydate`. |
| — | Census BPS | place files | aggregate-only; no durations and no record IDs. |

## Which datasets are sparse for duplexes specifically

The research question is duplex-centric ("48 days Austin vs 605 days SF"), so
the usable universe after filtering to 1-2-family new construction is much
smaller than raw row counts imply.

Verified on the live APIs:

- **SF**: 996,289 rows have both `filed_date` and `issued_date` AND a
  non-null `proposed_units`. Of those, the 1- and 2-family subset filtered by
  `proposed_use LIKE '%family%' OR LIKE '%duplex%'` is a few percent — still
  tens of thousands of rows over the dataset's 2000+ span.
- **NYC (ic3t-wcy2)**: 2,012,682 rows have `pre__filing_date` AND
  `fully_permitted`. 113,112 are new buildings (`job_type='NB'`); the
  1-4-family subset is ~30-50k.
- **Austin**: 6,624 rows have `permittype='BP'` AND `permit_class='R- 103 Two
  Family Bldgs'`. Clean duplex set, spans 1987 → present.
- **LA**: filter `permit_sub_type='1 or 2 Family Dwelling'` combined with
  `permit_type='Bldg-New'` isolates new 1-2 family residences.
- **Seattle**: filter `permitclass='Single Family/Duplex'`. The Plan Review
  dataset is the ONLY one that exposes duplexes with per-cycle timing.
- **Chicago**: no unit_count column at all. Duplex identification requires
  text matching `work_description` for "duplex" / "2-flat" / "two-flat" /
  "2 unit". Expect much lower recall.
- **Portland**: filter `TYPE='Duplex'` or `TYPE='Accessory Dwelling Unit'`
  on layer 22. `NUMNEWUNITS` helps but is null for older rows.

## Anomalies and gotchas discovered

### Sentinel / placeholder dates
- **SF**: `filed_date` ranges from `1901-03-10` to 2026-04-08. The 1901 value
  is a data-entry placeholder (DBI's AMANDA reset marker) — filter
  `filed_date >= '2000-01-01'` or similar.
- **Portland**: ArcGIS returns epoch-millisecond integers. For old or
  cancelled records, some fields contain huge negative values that trigger a
  numpy overflow inside `pandas.to_datetime(..., unit='ms')`. The loader
  clamps to (-6.2e13, 4.1e12) ms (~1950–2100) before conversion.

### Date formats
- **SF, LA, Chicago, Austin, Seattle**: ISO-8601 with seconds.
- **NYC legacy (`ic3t-wcy2`)**: `MM/DD/YYYY` strings — parses only with
  `format='%m/%d/%Y'`, not default auto-detect.
- **NYC DOB NOW (`w9ak-ipjd`)**: ISO-8601 with seconds.
- **Portland**: UNIX epoch **milliseconds** as integers.

### Currency / numeric-as-string
- **NYC legacy**: `initial_cost` is a currency string (`"$154,000.00"`).
- **Boston**: `declared_valuation` and `total_fees` same (`"$36,500.00"`).
- **SF**: `estimated_cost`, `revised_cost`, `existing_units`,
  `proposed_units` are all plain-decimal strings ("15000.0"). `pd.to_numeric`
  works.
- **Austin**: no valuation column exposed at all.

### Status-code semantics (not cross-comparable)
Each city uses its own vocabulary and it is dangerous to collapse them:

- **SF**: `status ∈ {filed, plan check, issued, expired, complete,
  withdrawn, reinstated, ...}`. Note that `expired` and `complete` both mean
  "not actively in pipeline" but for very different reasons.
- **NYC BIS**: `job_status_descrp ∈ {SIGNED OFF, COMPLETED, DISAPPROVED,
  PENDING, ...}` and `job_status ∈ {A, C, D, I, P, Q, R, S, U, W, X, ...}` —
  the letter codes are NOT documented in the public dataset.
- **Austin**: `status_current ∈ {Active, Expired, Final, Withdrawn, Void,
  Approved, ...}` — "Active" conflates "in plan check" with "issued but not
  yet built".
- **Chicago**: the main dataset has no status column at all; presence in
  `ydr8-5enu` implies "issued" per its filtering logic.
- **Seattle**: `housingcategory` is a housing-policy tag (`Middle Housing`,
  etc.), not a status code.

The normalised schema exposes raw `status` but **baseline models should not
treat status strings as cross-city features** without per-city remapping.

### Document / record granularity
- **NYC**: one job yields multiple rows (`doc__=01,02,03,...`) for
  architectural, structural, plumbing, mechanical. Collapse per `job__` for
  pipeline analysis.
- **Seattle Plan Review**: one permit yields one row per
  (`reviewtype`, `reviewcycle`) combination — a 3-cycle 4-reviewtype permit
  can produce 12 rows. `load_seattle()` collapses these to one row per
  `permitnum` (min(applieddate), max(completed/issued), last(metadata)).
- **SF**: there is no project ID; a duplex new-build often has parallel
  architectural and MEP permits that must be clustered by
  (`block`, `lot`, filing window) to recover "project" durations.
- **Austin**: `masterpermitnum` and `project_id` exist and can be used to
  group BP+MP+EP+PP permits for the same project.
- **Portland**: `FOLDERKEY` is the internal project folder. `APPLICATION`
  (e.g. `1997-051080-000-00-RS`) is a per-sub-permit id.

### What the loaders normalise vs. what they drop
The shared schema deliberately keeps only what can be normalised. These
high-value city-specific fields are **not** in `COLUMNS` and should be pulled
from the raw parquet cache when needed:

- Seattle: `reviewcycle`, `reviewtype`, `reviewer`, `reviewteam`,
  `reviewresultdesc`, `reviewcomplexity`, `daysoutcorrections`,
  `daysinitialplanreview`, `daysplanreviewcity`, `totaldaysplanreview`,
  `numberreviewcycles`
- NYC legacy: `paid`, `fully_paid` (fee-collection timestamps),
  `professional_cert`, `zoning_dist1`
- LA: `business_unit` (`Regular Plan Check` / `Express Permit` / `OTC`)
- Chicago: `processing_time` (pre-computed days), `review_type`
  (`STANDARD PLAN REVIEW` / `EASY PERMIT` / `DIRECT DEVELOPER SERVICES` /
  `SIGN PERMIT` / ...), fee breakdown columns
- Austin: `masterpermitnum`, `project_id`, `permit_class_mapped`
- SF: `plansets` (number of plan copies), `application_submission_method`
  (`in-house` vs `online`), `existing_use` vs `proposed_use` (change-of-use
  is a strong slow-down predictor)

## What a Phase 0.5 baseline could realistically use

### Target variable
`duration_days = issued_date - filed_date` (cast both to `pd.Timestamp`,
subtract, take `.dt.days`). This is the duration the research question asks
about. A log-transform is advised — the distribution is heavy-tailed and SF
has routine 600-day outliers.

### Recommended baseline input cities
Use all five major cities (SF, NYC, LA, Chicago, Austin). Seattle is powerful
but the sample size is smaller and the grain is unusual; treat it as a
validation/holdout city where a richer "stage decomposition" target is
possible.

### Filter to comparable projects
```
subset = (df.permit_subtype.str.contains("family|duplex|Two Family|1 or 2 Family|Single Family",
                                         case=False, regex=True, na=False)
          & df.filed_date.notna() & df.issued_date.notna()
          & (df.filed_date >= pd.Timestamp("2015-01-01"))
          & ((df.issued_date - df.filed_date).dt.days.between(1, 2000)))
```

### Candidate features
- `valuation_usd` (where available; missing for Austin and Chicago)
- `unit_count`, `square_feet` (where available)
- `city` one-hot
- `year(filed_date)` (pipeline backlogs are highly time-dependent)
- `neighborhood` or `council_district` (high-cardinality categorical)
- `permit_subtype` mapped per city to a canonical residential bucket
- For Seattle as a regression enrichment: `numberreviewcycles`,
  `daysoutcorrections` — these ARE the decomposition.

### Baseline models
- Quantile regression (P50/P90) predicting `duration_days`.
- Gradient-boosted trees (LightGBM / XGBoost) with monotonic constraints on
  `valuation_usd` and `square_feet` if signal is weak.
- Per-city intercept models to establish the "Austin base rate vs SF base
  rate" that the headline 48 vs 605 comes from — and to confirm how much is
  composition (NYC has fewer duplexes) vs true pipeline speed.

## Gaps that would block the discovery sweep

1. **No per-RFI / per-correction-letter data for any city except Seattle.**
   The research question explicitly asks "where in the pipeline is time
   lost". Outside Seattle we can only split pipeline into 2-3 buckets (file,
   plan check, issue/final). The 605-vs-48 answer will look like "plan
   check" without further granularity — which is true but not actionable.
   Consider scraping Seattle `e285-aq8h` Plan Comments for correction-letter
   text mining, and a targeted scrape of SF DBI's public records viewer
   (https://sfdbi.org) for RFI dates on a sampled cohort.

2. **Boston and Philadelphia blocked.** Neither open-data feed exposes a
   filing or submission date. Both publish inspections separately; a
   workaround is to treat the earliest inspection as a filing-date proxy,
   but that trims the pipeline at the wrong end. These cities should be
   parked unless a records request surfaces new data.

3. **No reviewer IDs for any city except Seattle.** Reviewer workload and
   individual backlog are plausibly the causal mechanism for SF's drag. We
   cannot measure this without per-reviewer stamps. A Phase B discovery
   experiment for SF would need a FOIA / records request.

4. **Chicago has no use_code, no unit_count, no square_feet.** Filtering to
   duplexes requires NLP on `work_description`. Signal quality will be
   materially worse than for other cities. Consider dropping Chicago from
   the duplex-specific question or keeping it only as a coarse "small
   residential" bucket.

5. **LA's `use_desc` distinguishes `Apartment` from `1 or 2 Family Dwelling`
   but the line is fuzzy for older ADU conversions and conversion permits.**
   Manual audit of ~100 rows is advisable before training.

6. **Sentinel date handling.** SF's 1901 placeholders, Portland's clamped
   ArcGIS-ms values, and NYC's empty-string dates all need explicit per-city
   filters. The loaders convert them to NaT, but a baseline that silently
   drops NaT can lose 20-35% of rows (see smoke-test null fractions).

7. **Joining permits across phases within a single city is non-trivial.** SF
   has no project ID; NYC has two coexisting job-numbering systems
   (BIS + DOB NOW); LA uses `permit_nbr` but doesn't group trades. Cross-phase
   joins (e.g. construction permit → certificate of occupancy → final
   inspection) will introduce their own error bars.

## Smoke-test output (limit=1000 per city, 2026-04-09)

```
sf         rows=  1000  null[filed_date]= 0.0%  null[issued_date]=19.9%  null[plan_check_end_date]=22.7%  null[permit_subtype]= 4.0%
nyc        rows=  1000  null[filed_date]= 0.0%  null[issued_date]=37.8%  null[plan_check_end_date]=27.0%  null[permit_subtype]= 2.2%
la         rows=  1000  null[filed_date]= 0.0%  null[issued_date]=23.9%  null[plan_check_end_date]=23.9%  null[permit_subtype]= 0.0%
chicago    rows=  1000  null[filed_date]= 0.0%  null[issued_date]= 0.0%  null[plan_check_end_date]= 0.0%  null[permit_subtype]= 0.0%
austin     rows=  1000  null[filed_date]= 0.0%  null[issued_date]= 0.0%  null[plan_check_end_date]= 0.0%  null[permit_subtype]= 0.0%
seattle    rows=   111  null[filed_date]= 0.0%  null[issued_date]= 0.0%  null[plan_check_end_date]= 0.0%  null[permit_subtype]= 0.0%
portland   rows=  1000  null[filed_date]= 0.0%  null[issued_date]=80.0%  null[plan_check_end_date]=80.0%  null[permit_subtype]= 0.0%
```

Notes on the null fractions:

- **Seattle** returns only 111 collapsed permits from 1000 raw Plan Review
  rows (one row per reviewtype x cycle). Scale-up: pulling 50,000 raw rows
  yields roughly 5-6k unique permits.
- **NYC** 37.8% null issued rate is because many pending / withdrawn jobs
  remain in the dataset — Phase 0.5 should filter on `issued_date.notna()`.
- **Portland** 80% null issued rate reflects the "All Permits" layer
  including many dormant / withdrawn / old residential-alter records that
  never reached issuance. Filter on `status='Issued'` or
  `status='Final'` before modelling durations.
- **Chicago** and **Austin** show 0% null filed/issued because Socrata pages
  return the most recent rows first and both datasets only publish issued
  permits — censored sample, as documented in `data_sources.md`.

## What to do next (Phase 0.5 ready checklist)

- [x] Verify every API URL returns 200.
- [x] Document each dataset's stage granularity honestly.
- [x] Write city-specific normaliser functions.
- [x] Smoke-test loaders at `limit=1000`.
- [ ] Pull full datasets (no limit) and write parquet cache — estimated
      total disk ~3-4 GB across the five core cities.
- [ ] Build a duplex filter per city and confirm row counts match the
      ballpark values in `data_sources.md`.
- [ ] Fit a first quantile-regression baseline on
      `log(duration_days) ~ city + year + valuation + unit_count` and
      compare per-city predicted medians to the 48 / 605 framing.
- [ ] Pull Seattle's per-cycle `daysoutcorrections` and use it as an
      auxiliary target to validate the "plan check vs corrections wait"
      decomposition.
