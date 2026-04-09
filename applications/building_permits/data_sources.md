# Data sources — building permit processing times

Phase 0 inventory of municipal / federal building-permit datasets that might answer:
> where in the permit pipeline (intake, plan check, corrections, approval, issuance,
> inspection, final) is time lost, and why does a duplex permit take ~50 days in
> Austin and ~600 in San Francisco?

All endpoints were hit directly with `requests.get(...)` on 2026-04-09; the row
counts / date ranges in the tables below are what the API returned that day.
"Stage granularity score" is an honest 0–5 estimate of how many distinct
per-application timestamps the dataset exposes (0 = filed + issued only,
5 = every RFI / correction letter / reviewer-assignment event).

--------------------------------------------------------------------------------
## Table of contents

1. San Francisco — DBI Building Permits (i98e-djp9)
2. New York City — DOB Job Application Filings (ic3t-wcy2)  *(primary for NYC)*
3. New York City — DOB NOW Build Job Application Filings (w9ak-ipjd)
4. New York City — DOB NOW Build Approved Permits (rbx6-tga4)
5. New York City — DOB Permit Issuance (ipu4-2q9a)
6. Los Angeles — LADBS Building Permits **Submitted** (gwh9-jnip)
7. Los Angeles — LADBS Building Permits **Issued** (pi9x-tg5x)
8. Chicago — Building Permits (ydr8-5enu)
9. Austin — Issued Construction Permits (3syk-w9eu)
10. Austin — Plan Review Cases (n8ck-xkda)
11. US Census — Building Permits Survey (BPS)
12. Boston — Approved Building Permits (CKAN 6ddcd912-…) *bonus*
13. Philadelphia — Carto `permits` + `li_permits` *bonus*
14. Seattle — Plan Review (tqk8-y2z5) **+ Plan Comments (e285-aq8h)** *bonus*
15. Seattle — Building Permits (76t5-zqzr) *bonus, weaker*
16. Portland, OR — PortlandMaps BDS_Permit FeatureServer *bonus*
17. Summary stage-granularity scoreboard

--------------------------------------------------------------------------------

## 1. San Francisco — DBI Building Permits

| field | value |
|---|---|
| Owner | SF Department of Building Inspection (DBI) |
| Dataset name | Building Permits |
| Socrata 4x4 | `i98e-djp9` |
| Landing URL | https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-djp9 |
| SODA JSON | https://data.sfgov.org/resource/i98e-djp9.json |
| License | Open Data Commons Public Domain Dedication and License (PDDL, CC0-equivalent) |
| Time range | 1901-03-10 → 2026-04-08 (API-reported `filed_date` min/max) |
| Row count | 1,285,957 |
| Update cadence | Incremental daily; since 2024-12-10 only new and updated rows are written (diff by `data_as_of` / `data_loaded_at`) |
| App token needed | No (rate limit ≈ 1000 req/hr without token, higher with) |

### Key columns

| purpose | column | notes |
|---|---|---|
| permit ID | `permit_number`, `record_id` | record_id is globally unique |
| address | `street_number` + `street_name` + `street_suffix` + `zipcode` | |
| parcel | `block`, `lot` | SF Assessor APN = block+lot |
| type | `permit_type`, `permit_type_definition` | codes 1..8 ("new construction", "additions alterations or repairs", etc.) |
| use code | `proposed_use`, `existing_use`, `proposed_occupancy` | free-text (e.g. "apartments", "1 family dwelling") |
| status | `status`, `status_date` | filed / plan check / issued / expired / complete |
| **filed** | `filed_date` | timestamp with seconds |
| **plan check approved** | `approved_date` | |
| **issued** | `issued_date` | |
| **latest activity** | `last_permit_activity_date` | proxy for CFC / final sign-off |
| valuation | `estimated_cost`, `revised_cost` | USD, string-typed |
| units | `existing_units`, `proposed_units` | string-typed |
| stories | `number_of_existing_stories`, `number_of_proposed_stories` | |
| geo | `supervisor_district`, `neighborhoods_analysis_boundaries`, `zipcode`, `location` (point) | |

### Stage granularity score: **3 / 5**

Four timestamps per row (`filed_date`, `approved_date`, `issued_date`,
`last_permit_activity_date`). Enough to decompose pipeline into
{filing → approval, approval → issuance, issuance → last-activity} but **no
RFI / correction-letter / fire / MEP per-discipline stamps** and no plan-check
cycle counter. Insufficient to say *which* corrections cycle dragged — only
that the pre-approval bucket was slow.

### Schema sample (actual API output, trimmed)

```json
[
 {"permit_number":"201903226060", "permit_type":"3",
  "filed_date":"2019-03-22T14:35:59.000",
  "approved_date":"2019-09-19T10:21:16.000",
  "issued_date":"2019-09-19T15:31:40.000",
  "last_permit_activity_date":"2019-09-19T15:10:39.000",
  "status":"expired", "status_date":"2025-10-23T09:58:35.000",
  "existing_units":"12.0", "proposed_units":"14.0",
  "estimated_cost":"15000.0", "revised_cost":"97000.0",
  "proposed_use":"apartments",
  "neighborhoods_analysis_boundaries":"Castro/Upper Market",
  "zipcode":"94114"}
]
```

### Gotchas

- `filed_date` min is 1901-03-10 — almost certainly a data-entry placeholder.
  Filter `filed_date >= '2000-01-01'` for baseline work.
- String-typed numerics (`existing_units`, `proposed_units`, `estimated_cost`)
  must be cast.
- `permit_type_definition` field spelling differs by era ("additions alterations
  or repairs" vs "additions_alterations_or_repairs").
- SF sometimes issues multiple permits for one project (architectural vs
  MEP). To recover a project-level pipeline you must cluster by
  `block+lot+filed_date ± 30 d` — the dataset has no project ID.
- There is a sibling dataset `p4e4-a5a7` ("Building Permits filed on or after
  2013-01-01") which is a filtered view of i98e-djp9; use the parent.
- The companion dataset `tyz3-vt28` ("PermitSF Permitting Data") does expose
  `submit_to_issue_cal` / `submit_to_issue_biz` pre-computed but as of
  2026-04-09 has only 1,008 rows and mostly fire-alarm / plumbing permits, so
  not useful for duplexes.

### Small-residential filter that works

```
$where=filed_date IS NOT NULL AND issued_date IS NOT NULL
       AND (proposed_use like '%1 family%' OR proposed_use like '%2 family%'
            OR proposed_use like '%duplex%')
```

Verified 996,289 rows have both `filed_date` AND `issued_date` AND a non-null
`proposed_units`, of which the 1- and 2-family subset is the target.

--------------------------------------------------------------------------------

## 2. New York City — DOB Job Application Filings  *(primary for NYC)*

| field | value |
|---|---|
| Owner | NYC Department of Buildings (DOB) — legacy BIS system |
| Dataset name | DOB Job Application Filings |
| Socrata 4x4 | `ic3t-wcy2` |
| Landing URL | https://data.cityofnewyork.us/Housing-Development/DOB-Job-Application-Filings/ic3t-wcy2 |
| SODA JSON | https://data.cityofnewyork.us/resource/ic3t-wcy2.json |
| License | Public domain (NYC Open Data Terms of Use) |
| Time range | 2000-01-01 → current (rows gated by `latest_action_date >= 2000`) |
| Row count | 2,714,628 |
| Update cadence | Daily; `dobrundate` reports the ETL run |

### Key columns (per-stage timestamps!)

| stage | column | format |
|---|---|---|
| application opened | `pre__filing_date` | `MM/DD/YYYY` |
| fee paid | `paid`, `fully_paid` | |
| plan-check approved | `approved` | |
| **fully permitted (issued)** | `fully_permitted` | |
| signed off / CofO | `signoff_date` | |
| latest status action | `latest_action_date` | |
| job number | `job__` | serves as cross-dataset key |
| doc | `doc__` | sub-doc counter (A1, A2, NB ...) |
| type | `job_type`, `building_type`, `building_class`, `job_status`, `job_status_descrp` | A1=major alter, A2=minor alter, NB=new build |
| address | `house__`, `street_name`, `borough` | |
| parcel | `block`, `lot`, `bin__`, `bbl` | |
| use | `existing_occupancy`, `proposed_occupancy`, `zoning_dist1` | |
| units | `existing_dwelling_units`, `proposed_dwelling_units` | string-typed |
| square feet | `total_construction_floor_area`, `enlargement_sq_footage` | string-typed |
| cost | `initial_cost`, `total_est__fee` | currency-formatted strings like `$154000.00` |
| geo | `gis_council_district`, `community___board`, `gis_nta_name`, `gis_census_tract` | |

### Stage granularity score: **4 / 5**

Six distinct timestamps per job: `pre__filing_date`, `paid`, `fully_paid`,
`approved`, `fully_permitted`, `signoff_date` (+ `latest_action_date` as a
tail). This is the **best per-stage detail of any of the required cities** for
the legacy DOB workflow. The only things missing for a 5/5 are individual
correction-letter stamps and reviewer IDs — those only live inside BIS and are
not exported.

### Schema sample

```json
{"job__":"104816095","doc__":"01","borough":"MANHATTAN",
 "house__":"128","street_name":"WEST 111 STREET",
 "block":"01820","lot":"00048","bin__":"1054930",
 "job_type":"A2","job_status_descrp":"SIGNED OFF",
 "pre__filing_date":"06/25/2007","paid":"07/02/2007",
 "fully_paid":"07/02/2007","approved":"07/02/2007",
 "fully_permitted":"08/23/2007","signoff_date":"11/21/2008",
 "initial_cost":"$154000.00","total_est__fee":"$1674.70",
 "proposed_dwelling_units":"3","existing_zoning_sqft":"0",
 "zoning_dist1":"R7-2","building_class":"R0"}
```

### Gotchas

- Dates are `MM/DD/YYYY` strings, not ISO. Use `pd.to_datetime(..., format='%m/%d/%Y', errors='coerce')`.
- Currency columns contain `$` and commas (`"$154,000.00"`).
- `latest_action_date` and `dobrundate` are not stage events — they are
  ETL / "last seen" timestamps.
- Since ~2020 new jobs go through DOB NOW (dataset **3** below), so
  `ic3t-wcy2` is decreasingly populated for recent years. To cover both eras
  you must UNION `ic3t-wcy2` with `w9ak-ipjd`.
- `doc__` expands one job into multiple rows (architectural / structural /
  plumbing / mechanical). For pipeline analysis, collapse per `job__`.
- `job_type='NB'` (new building) is the cleanest filter for new-construction
  duplex analysis; `A1`/`A2` are alterations.
- Verified on the live API: 2,012,682 rows have both `pre__filing_date` and
  `fully_permitted` populated (ie. ~74%). 113,112 of those are `NB`.

--------------------------------------------------------------------------------

## 3. New York City — DOB NOW Build Job Application Filings  *(post-2020 replacement of #2)*

| field | value |
|---|---|
| Owner | NYC DOB — DOB NOW Build system |
| Socrata 4x4 | `w9ak-ipjd` |
| SODA JSON | https://data.cityofnewyork.us/resource/w9ak-ipjd.json |
| License | Public domain |
| Time range | 2015-08-xx → current |
| Row count | 887,480 |
| Update cadence | Daily |

### Key columns

| stage | column |
|---|---|
| filed | `filing_date` |
| approved (plan check) | `approved_date` |
| first permit issued | `first_permit_date` |
| current status | `filing_status`, `current_status_date` |
| signoff | `signoff_date` |

Plus a huge set of boolean work-type flags
(`general_construction_work_type_`, `mechanical_systems_work_type_`,
`plumbing_work_type`, `sprinkler_work_type`, `structural_work_type_`, ...) that
let you tell whether a filing is a soup-to-nuts new build vs a plumbing-only
change.

Joining key: `job_filing_number` (a DOB NOW ID like `B00013978-I1`). It does
NOT match the legacy `job__` IDs in `ic3t-wcy2`.

### Stage granularity score: **3 / 5**

Four timestamps (filing, approved, first_permit, signoff). Fewer stages than
`ic3t-wcy2` but covers the post-2020 period that the legacy BIS dataset is
losing.

### Gotchas

- ISO-8601 dates with seconds — parses cleanly.
- `initial_cost` is a plain number string (no `$`) in this dataset.
- Same document-expansion pattern as BIS: collapse per job.
- `first_permit_date` is the first time **any** permit (trade-specific) was
  issued — not necessarily the full GC permit.

--------------------------------------------------------------------------------

## 4. New York City — DOB NOW Build – Approved Permits  *(supplementary)*

| field | value |
|---|---|
| Socrata 4x4 | `rbx6-tga4` |
| URL | https://data.cityofnewyork.us/resource/rbx6-tga4.json |
| License | Public domain |
| Row count | 920,717 |

Mostly useful for inspections and trade-permit tracking; **has no filing date**
(the sample even shows `job_filing_number="Permit is no"` as a null-like
value), so it cannot be used standalone for pipeline duration. Pair with
`w9ak-ipjd` by joining on the cleaned `job_filing_number`.

Stage granularity on its own: **1 / 5** (only `permit_status`, no elapsed time).

--------------------------------------------------------------------------------

## 5. New York City — DOB Permit Issuance  *(legacy trade permits)*

| field | value |
|---|---|
| Socrata 4x4 | `ipu4-2q9a` |
| URL | https://data.cityofnewyork.us/resource/ipu4-2q9a.json |
| License | Public domain |
| Row count | 3,986,485 |

One row per issued permit (PL, OT, EQ, FO, ...) with `filing_date`,
`issuance_date`, `job_start_date`, `expiration_date`. **This is an
issued-permits-only dataset** — applications that never reach issuance are
absent, so you get a censored view of the pipeline. For filed-but-not-issued
duration you must use `ic3t-wcy2` / `w9ak-ipjd`.

Stage granularity score: **2 / 5**.

--------------------------------------------------------------------------------

## 6. Los Angeles — LADBS Building Permits **Submitted** from 2020 to Present

| field | value |
|---|---|
| Owner | Los Angeles Department of Building & Safety (LADBS) |
| Socrata 4x4 | `gwh9-jnip` |
| URL | https://data.lacity.org/resource/gwh9-jnip.json |
| License | Not explicitly set; LA Open Data terms (public domain de facto) |
| Time range | 2020-01 → current |
| Row count | 284,763 |
| Update cadence | Daily refresh (`refresh_time` field) |

### Key columns

| stage | column |
|---|---|
| submitted | `submitted_date` |
| issued | `issue_date` |
| certificate of occupancy | `cofo_date` |
| status | `status_desc`, `status_date` |

Plus `permit_nbr`, `permit_type` (`Bldg-New`, `Bldg-Alter/Repair`, ...),
`permit_sub_type` (`1 or 2 Family Dwelling`, `Apartment`, `Commercial`, ...),
`use_code`/`use_desc`, `valuation`, `square_footage`, `du_changed` (dwelling
units delta), `height`, `work_desc`, `apn`, `zip_code`, `cd` (council district),
`zone`, `business_unit` (`Regular Plan Check` / `Express Permit` / `OTC`).

### Stage granularity score: **3 / 5**

Three real stage timestamps (`submitted_date`, `issue_date`, `cofo_date`) plus
the rolling `status_date`. The `business_unit` column is uniquely valuable: it
tells you whether the permit went through regular plan check, express, or
counter — that is itself a pipeline bucket.

### Gotchas

- `dyxf-7hc4` covers 2010–2019 and `e67z-kt2n` covers <2010 if you want
  historical; schemas are compatible.
- There are separate Submitted/Issued tables — the Submitted table
  (`gwh9-jnip`) is strictly superset-compatible for pipeline work because
  pending applications are only in the Submitted file.
- `submitted_date` is day-granularity (no time component).
- `permit_sub_type='1 or 2 Family Dwelling'` is the duplex filter (combined
  with `permit_type='Bldg-New'` for new construction).

### Sample

```json
{"permit_nbr":"22010-20000-03007","primary_address":"9421 N SEPULVEDA BLVD 1-5",
 "zip_code":"91343","permit_type":"Bldg-New","permit_sub_type":"Apartment",
 "use_desc":"Apartment","submitted_date":"2022-04-27T00:00:00.000",
 "issue_date":"2024-01-09T00:00:00.000","cofo_date":"2025-04-04T00:00:00.000",
 "status_desc":"CofO Issued","du_changed":"5","square_footage":"7374",
 "valuation":"455000","business_unit":"Regular Plan Check"}
```

--------------------------------------------------------------------------------

## 7. Los Angeles — LADBS Building Permits **Issued** from 2020 to Present

| field | value |
|---|---|
| Socrata 4x4 | `pi9x-tg5x` |
| URL | https://data.lacity.org/resource/pi9x-tg5x.json |
| License | LA Open Data |
| Row count | 383,870 |

Issued-permits-only slice. Does not include `submitted_date`! Only
`issue_date` and `status_date` are present. Useful as a cross-check of
`gwh9-jnip` issuance counts but cannot stand alone for pipeline work.

Stage granularity score: **1 / 5**.

--------------------------------------------------------------------------------

## 8. Chicago — Building Permits

| field | value |
|---|---|
| Owner | City of Chicago Department of Buildings |
| Socrata 4x4 | `ydr8-5enu` |
| URL | https://data.cityofchicago.org/Buildings/Building-Permits/ydr8-5enu |
| SODA JSON | https://data.cityofchicago.org/resource/ydr8-5enu.json |
| License | City of Chicago "Terms of Use" (public re-use permitted) |
| Time range | 2006 → current |
| Row count | 832,413 |
| Update cadence | Daily |

### Key columns

| stage | column |
|---|---|
| application opened | `application_start_date` |
| issued | `issue_date` |
| **pre-computed duration** | `processing_time` (integer days) |
| permit id | `permit_`, `id` |
| type | `permit_type`, `review_type` |
| cost | `reported_cost` |
| fees | `building_fee_*`, `zoning_fee_*`, `other_fee_*`, `total_fee` |
| address | `street_number`, `street_direction`, `street_name` |
| geo | `ward`, `community_area`, `census_tract`, `latitude`, `longitude` |
| contractors | `contact_1_*`, `contact_2_*` (type, name, city) |

Chicago also added a `PERMIT_CONDITION` column on 2025-10-15 per dataset notes
(not yet in the API sample — check before using).

### Stage granularity score: **2 / 5**

Only `application_start_date` and `issue_date` exist. But because Chicago
helpfully ships `processing_time` as a pre-computed column **and** breaks out
`review_type` (`NEW CONSTRUCTION`, `EASY PERMIT`, `STANDARD PLAN REVIEW`,
`SIGN PERMIT`, ...), you can stratify processing time by review lane without
needing per-stage stamps.

### Gotchas

- No square footage or use_code. `work_description` is free text.
- No unit count either. Duplex filtering must use
  `review_type='NEW CONSTRUCTION'` + text matching on `work_description` for
  "duplex" / "2-unit" / "two-flat".
- `permit_type` values include `PERMIT - SIGNS`, `PERMIT - ELECTRIC WIRING`,
  etc. — the residential bucket is tiny relative to the full 832 k.
- Reported cost is self-declared and noisy.

### Sample

```json
{"id":"3368573","permit_":"101046020","permit_type":"PERMIT - SIGNS",
 "review_type":"SIGN PERMIT",
 "application_start_date":"2024-03-08T00:00:00.000",
 "issue_date":"2024-09-18T00:00:00.000","processing_time":"194",
 "reported_cost":"5500","ward":"49","community_area":"1",
 "building_fee_paid":"200","total_fee":"400"}
```

--------------------------------------------------------------------------------

## 9. Austin — Issued Construction Permits

| field | value |
|---|---|
| Owner | City of Austin Development Services Department |
| Socrata 4x4 | `3syk-w9eu` |
| URL | https://data.austintexas.gov/Building-and-Development/Issued-Construction-Permits/3syk-w9eu |
| SODA JSON | https://data.austintexas.gov/resource/3syk-w9eu.json |
| License | Public Domain U.S. Government (per API metadata) |
| Time range | ~1980 → current |
| Row count | 2,350,056 |
| Update cadence | Daily |

### Key columns

| stage | column |
|---|---|
| filed | `applieddate` |
| issued | `issue_date` |
| current status | `status_current`, `statusdate` |
| expires | `expiresdate` |
| permit id | `permit_number`, `project_id`, `masterpermitnum` |
| type | `permittype` (`BP`/`EP`/`MP`/`PP`/`DS`), `permit_type_desc`, `permit_class`, `permit_class_mapped`, `work_class` |
| address | `original_address1`, `original_zip`, `council_district` |
| parcel | `tcad_id` (Travis County appraisal ID) |
| description | `description`, `legal_description` |

### Stage granularity score: **2 / 5**

`applieddate` + `issue_date` + tail `statusdate`. No per-cycle plan-check
data, no correction-letter timestamps. Austin has a **separate** Plan Review
Cases dataset (see #10) which adds a pre-filing review stage but still no RFI
details.

### Gotchas

- No valuation and no square footage in this dataset (!), which is weird —
  both fields are in Austin's internal AMANDA system but not exported.
- No unit count.
- `permit_class` distinguishes `R- 103 Two Family Bldgs`, `R- 101 Single
  Family Houses`, `C- 103 Two Family Bldgs`, etc. — the duplex filter is
  `permit_class='R- 103 Two Family Bldgs' AND permittype='BP'`. Verified
  6,624 rows on 2026-04-09.
- `applieddate` is day-granular (midnight UTC).
- Austin also issues "Mechanical Permit" (MP), "Electrical Permit" (EP),
  "Plumbing Permit" (PP), "Driveway" (DS) alongside the primary Building
  Permit (BP). Filter `permittype='BP'` for the main pipeline; join trade
  permits via `masterpermitnum` / `project_id`.
- Sample from live API:
  `permit_number='2025-063757 BP'`, `applieddate=2025-03-18`, `issue_date=2025-05-22`
  — "NEW CONDO REGIME - BLDG #1 DUPLEX UNIT #1A". About 65 days filing-to-issue,
  consistent with the research-question framing of Austin ≈ 48 days.

--------------------------------------------------------------------------------

## 10. Austin — Plan Review Cases

| field | value |
|---|---|
| Socrata 4x4 | `n8ck-xkda` |
| URL | https://data.austintexas.gov/resource/n8ck-xkda.json |
| License | Public Domain |
| Row count | 156,494 |

Pre-filing "plan review" folders (type `PR`) opened *before* a full BP is
issued. Columns: `applied_date`, `status_current`, `status_date`,
`update_date`, `sub_type` (`C-1000 Commercial Remodel`, etc.), `work_class`,
`project_name`. Can be joined to `3syk-w9eu` by `permit_number` root to find
projects whose plan review pre-dates their BP.

Stage granularity: **1 / 5** (same `applied_date` / `status_date` pattern).

--------------------------------------------------------------------------------

## 11. US Census — Building Permits Survey (BPS)

| field | value |
|---|---|
| Owner | US Census Bureau, Economic Directorate |
| Landing | https://www.census.gov/construction/bps/ |
| Raw data | https://www2.census.gov/econ/bps/ |
| License | Public domain (US federal work) |
| Update cadence | Monthly (new files ~3 weeks after month close) |
| Geography | National, Region, State, MSA/PMSA, County, **Place** (city) |

The Place-level directory
`https://www2.census.gov/econ/bps/Place/<Region>/<file>.txt` contains CSV
files named `<region>YYMM[c|y].txt` (c = current month, y = year-to-date),
e.g. `so2501c.txt` = Southern region, Jan 2025, current-month permits.

### Columns (verified on `so2501c.txt`)

```
Survey Date, State Code, 6-Digit ID, County Code, Census Place Code,
FIPS Place Code, FIPS MCD Code, Pop, CSA Code, CBSA Code, Footnote,
Central City Code, Zip, Region, Division, Source, Place Name,
1-unit  Bldgs/Units/Value,
2-units Bldgs/Units/Value,
3-4 units Bldgs/Units/Value,
5+ units Bldgs/Units/Value
```

### Stage granularity score: **0 / 5**

This is the **aggregate totals** dataset — counts of permits issued by
place/month by unit-bucket. No individual permit records, no dates, no
processing-time information. **Not usable for the pipeline question**, but
indispensable as the baseline-count sanity check ("did SF really only issue
200 duplex permits last year?") and as a population frame for the per-city
microdata.

### Gotchas

- File naming is inconsistent: Southern region uses `so`, Northeast `ne`, etc.
  You need to know the region-to-prefix map (`ne`/`mw`/`so`/`we`).
- `Value` is in dollars (not thousands). Pre-1994 data exists but with a
  different schema.
- Files are comma-separated with a 2-row header (the second row continues
  column labels), which trips up naive `pd.read_csv`.

--------------------------------------------------------------------------------

## 12. Boston — Approved Building Permits  *(bonus)*

| field | value |
|---|---|
| Owner | City of Boston Inspectional Services Department |
| Portal | CKAN at data.boston.gov |
| Dataset slug | `approved-building-permits` |
| Resource ID | `6ddcd912-32a0-43df-9908-63574f8c7e77` |
| Datastore search | `https://data.boston.gov/api/3/action/datastore_search?resource_id=6ddcd912-32a0-43df-9908-63574f8c7e77` |
| CSV | https://data.boston.gov/dataset/cd1ec3ff-6ebf-4a65-af68-8329eceab740/resource/6ddcd912-32a0-43df-9908-63574f8c7e77/download/tmp_approved_building_permits.csv |
| License | Open Data Commons Public Domain Dedication and License (PDDL) |
| Row count | 720,177 |
| Update cadence | Daily; last_modified 2026-04-04 |

### Key columns

`permitnumber`, `worktype`, `permittypedescr`, `description`, `applicant`,
`declared_valuation`, `total_fees`, **`issued_date`**, **`expiration_date`**,
`status`, `occupancytype`, `sq_feet`, `address`, `zip`, `ward`, `parcel_id`,
`y_latitude`, `x_longitude`.

### Stage granularity score: **1 / 5**

**No filing date.** Only `issued_date` and `expiration_date`. Useless for
pipeline-duration analysis by itself — Boston goes on the sidelines unless we
can find a separate `submitted-permits` dataset (I searched and could not).

### Gotchas

- `declared_valuation` and `total_fees` are formatted as currency strings
  (`"$36,500.00"`).
- `sq_feet` is zero for most rows (self-reported).
- The dataset is named "Approved" so filed-but-rejected applications are
  entirely absent — not just undated.

--------------------------------------------------------------------------------

## 13. Philadelphia — Carto `permits` + `li_permits`  *(bonus)*

| field | value |
|---|---|
| Owner | Philadelphia Dept of Licenses & Inspections (L&I) |
| Portal | OpenDataPhilly — backed by phl.carto.com |
| SQL endpoint | https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+permits+LIMIT+10 |
| License | Open Data, Philadelphia (public domain) |
| Row counts | `permits` = 913,799, `li_permits` = 626,942 |

### Columns (verified)

`permits`: `permitnumber`, `permittype`, `permitdescription`,
`commercialorresidential`, `typeofwork`, `approvedscopeofwork`,
**`permitissuedate`**, **`permitcompleteddate`**, **`certificateofoccupancydate`**,
`certificateofoccupancyrequired`, `certificateofoccupancylink`,
`denialdocumentlink`, `status`, `applicanttype`, `contractorname`,
`contractoraddress1`, `opa_account_num`, `opa_owner`, `address`, `unit_num`,
`zip`, `censustract`, `council_district`, `parentjobid`, `posse_jobid`,
`areaofdisturbance`, `numberofstories`, `numberofunits`, `occupancytype`,
`usecategories`, `zoningpermitjobid`.

`li_permits`: near-identical schema minus the CofO fields.

### Stage granularity score: **1 / 5**

**Also no filing / application date exposed.** Only
`permitissuedate`, `permitcompleteddate`, and — when applicable —
`certificateofoccupancydate`. Philly does have per-inspection data in
`li_inspections` and per-cycle plan-review data in internal POSSE, but neither
is exposed via the Carto endpoint. Philly, like Boston, is a weaker city for
the core question.

### Gotchas

- Philly has other Carto tables like `li_violations`, `li_appeals`,
  `li_inspections`, and `cofos` which could be JOINed on `permitnumber` to
  reconstruct a partial pipeline. Scope-creep risk; only pursue if Philly
  becomes critical.
- `numberofunits` is numeric and usable for duplex filtering (`numberofunits
  = 2`).

--------------------------------------------------------------------------------

## 14. Seattle — Plan Review  *(bonus, BEST per-stage dataset)*

| field | value |
|---|---|
| Owner | Seattle Department of Construction and Inspections (SDCI) |
| Socrata 4x4 | `tqk8-y2z5` |
| URL | https://data.seattle.gov/Permitting/Plan-Review/tqk8-y2z5 |
| SODA JSON | https://data.seattle.gov/resource/tqk8-y2z5.json |
| License | Public Domain |
| Row count | 253,682 |
| Update cadence | Daily |

### Key columns — this is the gem

| stage | column |
|---|---|
| filed | `applieddate` |
| **reviewer assigned** | `reviewerassigndate` |
| **reviewer finished** | `reviewerfinishdate` |
| **initial review complete** | `initialreviewcompletedate` |
| **plan review complete (all cycles)** | `planreviewcompletedate` |
| ready to issue | `readyissuedate` |
| issued | `issueddate` |
| pre-computed duration: total plan review | `totaldaysplanreview` |
| pre-computed: initial | `daysinitialplanreview` |
| pre-computed: city-side | `daysplanreviewcity` |
| **pre-computed: time out for corrections** | `daysoutcorrections` |
| **cycle counter** | `numberreviewcycles`, `reviewcycle` |
| **reviewer identity** | `reviewer`, `reviewteam` |
| **review type** | `reviewtype` (`Zoning`, `Structural Engineer`, `Fire`, `Building`, ...) |
| **review result** | `reviewresultdesc` (`Corrections Required` / `Approved` / ...) |
| **complexity** | `reviewcomplexity`, `reviewcomplexitydesc` |
| **one row per reviewer-cycle-type** | the dataset is at (permit × review type × cycle) grain! |

Plus permit metadata: `permitnum`, `permitclass` (`Single Family/Duplex`!),
`permitclassmapped`, `permittypemapped`, `permittypedesc`, `description`,
`housingunits`, `housingunitsadded`, `housingunitsremoved`, `dwellingunittype`,
`zoning`, `contractorcompanyname`, `originaladdress1`, `latitude`, `longitude`,
`standardplan`, `housingcategory` (`Middle Housing`).

### Stage granularity score: **5 / 5**

This is the only dataset I found that exposes per-reviewer per-cycle
timestamps AND separates corrections-wait from active-review time. Seattle is
effectively the ground-truth case study for the "where is time lost"
question — every correction round appears as its own row with assign/finish
timestamps and an outcome. If Phase 0.5 trains on only one city, it should be
this one.

### Sample (real row)

```json
{"permitnum":"6361129-CN","reviewcycle":"2","reviewtype":"Zoning",
 "reviewteam":"All Team Reviews - LU - Zoning","reviewer":"Emilie Voight",
 "reviewteamassigndate":"2021-07-23","reviewerassigndate":"2021-07-23",
 "reviewerfinishdate":"2021-08-10","reviewresultdesc":"Corrections Required",
 "reviewcomplexity":"Full +","permitclass":"Single Family/Duplex",
 "permittypemapped":"Building","permittypedesc":"New",
 "totaldaysplanreview":"1015","daysinitialplanreview":"130",
 "daysplanreviewcity":"190","daysoutcorrections":"825",
 "numberreviewcycles":"3","applieddate":"2018-12-17",
 "initialreviewcompletedate":"2019-04-26",
 "planreviewcompletedate":"2021-09-27","readyissuedate":"2021-09-27",
 "issueddate":"2021-09-27","housingunitsadded":"1.0","zoning":"NR3",
 "dwellingunittype":"Detached Single-Family","standardplan":false,
 "originaladdress1":"6821 25TH AVE NE",
 "contractorcompanyname":"PATRICK ARCHER CONSTRUCT INC",
 "housingcategory":"Middle Housing"}
```

Note: `daysoutcorrections` = 825 on a single SFR — that is the smoking gun the
HDR question is trying to find in other cities.

### Gotchas

- Because the grain is (permit × reviewtype × cycle), a single permit yields
  many rows. For a permit-level normalised loader, pick the **max**
  `issueddate` and `planreviewcompletedate`, **sum** `numberreviewcycles` to
  the max, and keep the **min** `applieddate`. The loader below does this.
- A sibling dataset `e285-aq8h` (Plan Comments) has the actual correction
  letter text and document dates — join on `permitnum`. 26,299 rows.
- `standardplan=true` flags pre-approved prototypes that skip normal review —
  treat as a control group.

--------------------------------------------------------------------------------

## 15. Seattle — Building Permits  *(bonus, weaker)*

| field | value |
|---|---|
| Socrata 4x4 | `76t5-zqzr` |
| URL | https://data.seattle.gov/resource/76t5-zqzr.json |
| Row count | 189,096 |

**No dates at all** — this dataset only exposes `permitnum`, `permitclass`,
`permittypemapped`, `description`, `housingunits`, `statuscurrent`, address,
and coordinates. Useful for joining onto #14 to recover metadata for permits
that never got to plan review, but useless for durations on its own.

Stage granularity: **0 / 5**.

--------------------------------------------------------------------------------

## 16. Portland, OR — PortlandMaps BDS_Permit FeatureServer  *(bonus)*

| field | value |
|---|---|
| Owner | Portland Bureau of Development Services |
| Portal | https://www.portlandmaps.com/arcgis/rest/services/Public/BDS_Permit/FeatureServer |
| Layer 5 | Residential Construction Permit (29,293 features) |
| Layer 22 | All Permits (1,445,220 features) |
| Query example | `https://www.portlandmaps.com/arcgis/rest/services/Public/BDS_Permit/FeatureServer/22/query?where=TYPE%3D%27Duplex%27&outFields=*&f=json&resultRecordCount=100` |
| License | Open by reference; PortlandMaps public GIS data (treat as public domain) |
| Update cadence | Daily per BDS publishing schedule |

### Key columns

| purpose | field |
|---|---|
| application ID | `APPLICATION` (e.g. `1997-051080-000-00-RS`) |
| permit number | `PERMIT`, `FOLDERKEY`, `SEQUENCE` |
| created | `CREATEDATE` |
| **intake complete** | `INTAKECOMPLETEDATE` |
| issued | `ISSUED` |
| finaled | `FINALED` |
| last action | `LASTACTION`, `FOLDERACTION` |
| status | `STATUS` (`Final`, `Issued`, `Cancelled`, ...) |
| work type | `PERMIT`, `TYPE` (`Accessory Dwelling Unit`, `Single Family Residence`, `Duplex`, ...), `WORK_DESCRIPTION` |
| description | `DESCRIPTION` |
| valuation | `SUBMITTEDVALUATION`, `FINALVALUATION` |
| units | `NUMNEWUNITS` |
| sqft / stories | `TOTALSQFT`, `NUMBSTORIES` |
| occupancy | `OCCUPANCYGROUP`, `CONSTRUCTIONTYPE` |
| geo | `NEIGHBORHOOD`, `NEIGHBORHOOD_COALITION`, `NEIGHBORHOOD_DISTRICT`, `COUNTY`, `CITY` |
| parcel | `STATEIDKEY` (state ID / tax lot) |

### Stage granularity score: **3 / 5**

Four timestamps (`CREATEDATE`, `INTAKECOMPLETEDATE`, `ISSUED`, `FINALED`)
plus `LASTACTION`. No reviewer cycles or corrections stamps, but the
`INTAKECOMPLETEDATE` vs `ISSUED` gap cleanly isolates the plan-check phase
from the intake phase — which is exactly the decomposition the research
question needs.

### Gotchas

- Dates are UNIX **milliseconds** (the REST sample shows `1611100320000` =
  2021-01-20). Divide by 1000 and `pd.to_datetime(..., unit='s')`.
- Use the ArcGIS REST query syntax: `where=STATUS<>%27Cancelled%27 AND
  TYPE%3D%27Duplex%27 AND CREATEDATE%3E0&outFields=*&f=json&resultOffset=0&
  resultRecordCount=1000`.
- Max 1000 records per query; must page with `resultOffset`.
- `CREATEDATE` is closer to "application received" than a formal submission
  timestamp.
- There is a nearly identical MapServer endpoint
  `/Public/BDS_Permit_Residential_Construction/MapServer` which breaks out
  residential construction by year (layer 25 = 2005-Current Res Alter; layer
  29 = 2022 Res Construction, ...). Use the FeatureServer for bulk pulls.

--------------------------------------------------------------------------------

## 17. Summary stage-granularity scoreboard

| # | City | Dataset | Rows | Filing date? | Stage score | Suitable for pipeline Q? |
|---|---|---|---:|:-:|:-:|:-:|
| 1 | San Francisco | i98e-djp9 | 1.29 M | yes | 3 | yes (filed/approved/issued/last) |
| 2 | New York City | ic3t-wcy2 (legacy BIS) | 2.71 M | yes | **4** | yes — best legacy timestamp set |
| 3 | New York City | w9ak-ipjd (DOB NOW) | 0.89 M | yes | 3 | yes — required to cover 2020+ |
| 4 | New York City | rbx6-tga4 | 0.92 M | no | 1 | metadata join only |
| 5 | New York City | ipu4-2q9a | 3.99 M | yes (issued-only) | 2 | censored — avoid standalone |
| 6 | Los Angeles | gwh9-jnip (Submitted) | 0.28 M | yes | 3 | yes |
| 7 | Los Angeles | pi9x-tg5x (Issued) | 0.38 M | no | 1 | no — issued slice only |
| 8 | Chicago | ydr8-5enu | 0.83 M | yes | 2 | yes (filed + issued + pre-computed) |
| 9 | Austin | 3syk-w9eu | 2.35 M | yes | 2 | yes — matches research question |
| 10 | Austin | n8ck-xkda (plan review) | 0.16 M | yes | 1 | supplement only |
| 11 | US Census | BPS Place files | monthly | no | **0** | macro baseline, not pipeline |
| 12 | Boston | approved-building-permits | 0.72 M | **no** | 1 | NOT usable for pipeline |
| 13 | Philadelphia | phl.carto `permits` / `li_permits` | 0.91 M / 0.63 M | **no** | 1 | NOT usable without auxiliary joins |
| 14 | Seattle | tqk8-y2z5 (Plan Review) | 0.25 M | yes | **5** | **gold standard** — per-cycle per-reviewer |
| 15 | Seattle | 76t5-zqzr (Permits) | 0.19 M | no | 0 | metadata join only |
| 16 | Portland | BDS_Permit/FeatureServer/22 | 1.45 M | yes (`CREATEDATE`) | 3 | yes — clean intake/issue/final split |

### Cities usable for "where in the pipeline is time lost"
Seattle (5) >> NYC-BIS (4) > SF (3) ≈ LA (3) ≈ Portland (3) > Chicago (2) ≈ Austin (2)

### Cities we cannot answer the question for without extra scraping
Boston, Philadelphia — the open-data feeds omit filing dates. They can still
contribute *valuation-weighted issuance counts* for the Phase 1 scale-up but
not per-stage durations. Phase 0.5 should park them unless a new dataset
surfaces.

### Authentication / rate limits

- All Socrata endpoints (SF, NYC, LA, Chicago, Austin, Seattle) work without
  a token at ~1000 req/hr. For bulk pulls (>1M rows) register an app token at
  the respective portal and export `SODA_APP_TOKEN` — `data_loaders.py` reads
  this env var and sends it as `X-App-Token`.
- Philadelphia Carto: no auth; hard limit appears to be ~100 k rows per SQL
  call, so paginate with `OFFSET`/`LIMIT`.
- Boston CKAN datastore: no auth; `datastore_search` max is 32,000 rows per
  call, paginate with `offset`.
- PortlandMaps ArcGIS REST: no auth; `resultRecordCount` max ≈ 1000 per
  query, paginate with `resultOffset`.
- Census BPS: plain HTTP file downloads, no auth.
