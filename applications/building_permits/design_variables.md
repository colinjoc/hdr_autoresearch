# Design variables — building permit processing times

Structured catalogue of features and design dimensions the HDR loop can use. Each entry lists type, units, typical range, source, mechanism citations (to `papers.csv`), whether it is a Phase B discovery-sweep lever, and notes. Coverage is restricted to what the seven working loaders in `data_loaders.py` expose, plus macro features from documented public sources and derived features that can be computed from the normalised schema or the raw parquet cache.

Abbreviations: SF = San Francisco, NYC = New York City, LA = Los Angeles, CHI = Chicago, AUS = Austin, SEA = Seattle, PDX = Portland. "RPC" = raw parquet cache stored by `data_loaders.py` in `data/raw/<city>.parquet`.

---

## 1. Permit-level numeric features

### valuation_usd
- **Type**: continuous
- **Units**: USD
- **Range / typical values**: $1,000 – $50,000,000; P5 ~ $5,000 residential repair, P50 ~ $100,000–$300,000 new SFR/duplex, P95 ~ $5,000,000 commercial / large multifamily. SF `estimated_cost` ranges $0 – hundreds of millions; `revised_cost` is updated during plan check.
- **Sources**: `data_loaders.py:load_sf()` via `_money(revised_cost).fillna(estimated_cost)`; `load_nyc()` via `initial_cost` (currency string); `load_la()` via `valuation`; `load_chicago()` via `reported_cost`; `load_portland()` via `SUBMITTEDVALUATION` with `FINALVALUATION` fallback. Missing entirely in `load_austin()` (Austin 3syk-w9eu does not expose valuation) and `load_seattle()` (not in `tqk8-y2z5`).
- **Mechanism**: A canonical project-complexity proxy. Glaeser-Gyourko's regulatory-tax framing [5, 7, 8, 9, 161] treats valuation as the base for the zoning tax measurement. Mayer & Somerville [14] and Ihlanfeldt [15] use valuation as a control. The NMHC-NAHB 2022 survey [50, 214, 215] uses valuation to compute the 40.6% regulatory share. Higher valuation implies larger, more complex projects requiring more review time.
- **Phase B dimension**: yes — for sweep over log transform, monotonicity constraint, interaction with city.
- **Notes**: Heavy-tailed; use log1p for modeling. SF ships as string; NYC ships as `"$154,000.00"` currency string; CHI and LA are plain numeric. Null in Austin and Seattle. Use `_money()` coercion for the string-valued cities. Impute missing as city median before log.

### unit_count
- **Type**: count
- **Units**: dwelling units (integer)
- **Range / typical values**: 0 – 500+; P50 = 1 (SFR) or 2 (duplex) for the research question's subset; P95 = 50–200 for large multifamily.
- **Sources**: `load_sf()` via `proposed_units`; `load_nyc()` via `proposed_dwelling_units` (legacy BIS); `load_la()` via `du_changed` (dwelling-unit delta); `load_portland()` via `NUMNEWUNITS`; `load_seattle()` via aggregated `housingunits`. Null in Austin (not exposed) and Chicago (no unit_count column at all — `data_acquisition_notes.md` section "Filter to comparable projects").
- **Mechanism**: Unit count distinguishes the duplex research question from single-family and large multifamily. Pendall [18] and Rothwell & Massey [19] use unit counts as the regression target for zoning-effect studies. The research question pins duplexes (`unit_count=2`) as the canonical test case.
- **Phase B dimension**: yes — log1p transform, monotonicity, used for permit-type stratification (H044, H045, H118).
- **Notes**: Austin has NO unit column (filter on `permit_class='R- 103 Two Family Bldgs'` instead). Chicago has NO unit column (text-match `work_description` for "duplex"/"2-flat"/"two-flat"). LA's `du_changed` is signed — can be negative for conversions.

### square_feet
- **Type**: continuous
- **Units**: sqft
- **Range / typical values**: 500 – 1,000,000; P50 ~ 1,500–3,000 sqft (SFR/duplex), P95 ~ 50,000 sqft commercial.
- **Sources**: `load_nyc()` via `total_construction_floor_area`; `load_la()` via `square_footage`; `load_portland()` via `TOTALSQFT`. NOT exposed in SF (not in DBI schema), Austin (not in 3syk-w9eu per `data_acquisition_notes.md`), Chicago (not exposed), or Seattle (not in Plan Review dataset).
- **Mechanism**: Square footage is a direct proxy for reviewer-page-count load. Florida HB 267 [56] uses a 7,500 sqft threshold as a statutory breakpoint, making this a known institutional lever. Classical queueing [113, 114] predicts service time per unit is proportional to "work content", which for permits is approximately pages of plans.
- **Phase B dimension**: yes — log1p transform, monotonicity constraint, interaction with permit_subtype.
- **Notes**: Missing in SF, Austin, Chicago, Seattle. Impute as median-per-subtype per city when doing pooled modeling. Heavy-tailed.

### valuation_delta_usd (derived, SF only)
- **Type**: continuous
- **Units**: USD
- **Range / typical values**: -$5,000,000 – +$50,000,000; zero for most permits that are not revised. Non-zero delta correlates with long plan-check.
- **Sources**: derived from SF `revised_cost - estimated_cost` in RPC.
- **Mechanism**: A non-zero upward revision during plan check indicates complexity discovered late. Discretionary-review studies [30, 281, 40, 82] document revisions driven by reviewer comments. H010.
- **Phase B dimension**: yes — useful as a leakage check and a weak signal.
- **Notes**: SF only; undefined elsewhere. Only available post-plan-check, so risks leakage if used naively. Treat as a censored feature.

### plansets (SF only)
- **Type**: count
- **Units**: plan copies (integer)
- **Range / typical values**: 1 – 20
- **Sources**: SF raw parquet cache (`i98e-djp9.plansets`) — not currently in the normalised schema.
- **Mechanism**: Number of plan sets submitted correlates with project size and reviewer-page count. `data_acquisition_notes.md` flags this as a high-value SF-specific field not in `COLUMNS`.
- **Phase B dimension**: no — low signal.
- **Notes**: SF only. May be sparse/missing for online submissions.

### total_fee (Chicago only)
- **Type**: continuous
- **Units**: USD
- **Range / typical values**: $100 – $100,000; P50 ~ $500 for small residential.
- **Sources**: Chicago raw parquet cache (`ydr8-5enu.total_fee`).
- **Mechanism**: Permit-office-computed total fee is an independent quantification of project complexity (the city priced the effort). Correlated but not identical to valuation. Fees also include impact-fee components [179] where applicable.
- **Phase B dimension**: yes — log1p transform, useful only in Chicago where valuation signal is weak.
- **Notes**: Chicago exposes building/zoning/other fee breakouts. H094, H095.

---

## 2. Permit-level categorical features

### city
- **Type**: categorical
- **Units**: jurisdiction identifier
- **Range / typical values**: one of {sf, nyc, la, chicago, austin, seattle, portland}
- **Sources**: `load_*()` functions; `_frame("city", ...)` sets this constant per loader.
- **Mechanism**: The primary cross-city axis. SF vs Austin duplex durations differ by ~3x [83]; WRLURI [2, 3] and Saiz [1] predict city-level mean shifts; Einstein-Glick-Palmer [169] documents city-level political culture. The baseline must condition on city to reproduce the headline gap.
- **Phase B dimension**: yes — central axis for per-city vs global model sweep (H021, H022, H109, H110, H111).
- **Notes**: One-hot encoded or used as grouping for per-city models. 7 levels.

### permit_type
- **Type**: categorical
- **Units**: permit-class identifier
- **Range / typical values**: SF `permit_type_definition` {"new construction", "additions alterations or repairs", ...} ~8 levels; NYC `job_type` {A1, A2, NB, DM} ~4 levels; LA `permit_type` {Bldg-New, Bldg-Alter/Repair, Bldg-Demolition, ...}; CHI `permit_type` {PERMIT - SIGNS, PERMIT - NEW CONSTRUCTION, ...}; Austin `permit_type_desc`; Portland `PERMIT`.
- **Sources**: all loaders expose `permit_type`.
- **Mechanism**: Distinguishes new construction from alterations and demolition. New construction runs through plan check; alterations often skip zoning. Mayer & Somerville [14] and Ihlanfeldt [15] stratify on permit type.
- **Phase B dimension**: yes — used for new vs alter stratification (H044).
- **Notes**: Per-city vocabulary. Not cross-comparable as-is. Map to canonical buckets {new, alter, demo, repair, other} before modeling.

### permit_subtype
- **Type**: categorical
- **Units**: permit sub-class
- **Range / typical values**: SF `proposed_use` (free text, hundreds of levels — "apartments", "1 family dwelling", "office", ...); NYC `building_class` ~30 levels (R0, R1, ..., C1, C2, ...); LA `permit_sub_type` {1 or 2 Family Dwelling, Apartment, Commercial, ...}; CHI `review_type` {NEW CONSTRUCTION, STANDARD PLAN REVIEW, EASY PERMIT, SIGN PERMIT, ...}; AUS `permit_class` {R- 103 Two Family Bldgs, R- 101 Single Family, ...}; SEA `permitclass` {Single Family/Duplex, Commercial, ...}; PDX `TYPE` {Duplex, ADU, Single Family Residence, ...}.
- **Sources**: all loaders.
- **Mechanism**: The primary within-city segmentation. Each sub-class flows through a different pipeline track (fast-track residential vs regular plan check vs commercial). `data_sources.md` confirms this is the duplex filter key for every city.
- **Phase B dimension**: yes — target encoding (H019), per-subtype stratification, duplex filter.
- **Notes**: High cardinality (SF `proposed_use` is free text). Use target encoding with K-fold to avoid leakage. Must be harmonised to a canonical bucket before cross-city modeling. Per `data_acquisition_notes.md` recommended filter: `str.contains("family|duplex|Two Family|1 or 2 Family|Single Family", case=False, regex=True, na=False)`.

### use_code
- **Type**: categorical
- **Units**: occupancy/use classification
- **Range / typical values**: SF `proposed_occupancy` (B, R-2, R-3, M, ...); NYC `proposed_occupancy` or `existing_occupancy`; LA `use_desc`; Austin `work_class`; Portland `OCCUPANCYGROUP`; Seattle `permittypedesc`.
- **Sources**: all loaders except Chicago.
- **Mechanism**: IBC occupancy group determines which code chapters apply to plan review. Residential R-3 is a different pipeline than commercial B or mercantile M. Indirectly encodes fire-review and accessibility requirements.
- **Phase B dimension**: yes — target encoding, interaction with fire-review city-specific features.
- **Notes**: SF free text; NYC uses IBC codes; LA mixed. Harmonise to `{R1, R2, R3, B, M, F, other}` before cross-city modeling.

### status
- **Type**: categorical
- **Units**: current permit status
- **Range / typical values**: SF `{filed, plan check, issued, expired, complete, withdrawn, reinstated}`; NYC `job_status_descrp` `{SIGNED OFF, COMPLETED, DISAPPROVED, PENDING, ...}`; Austin `status_current` `{Active, Expired, Final, Withdrawn, Void, Approved}`; LA `status_desc`; Seattle `housingcategory` (reused slot — not strictly a status).
- **Sources**: all loaders.
- **Mechanism**: Status determines the censoring label. `issued_date IS NULL` and `status = "Pending"` imply right-censoring at extraction date. `status = "Withdrawn"` implies a competing-risks non-event. `data_acquisition_notes.md` section "Status-code semantics" warns against treating these as cross-city features.
- **Phase B dimension**: no — NOT a direct feature (leakage / post-outcome). Used ONLY to derive `event` indicator for survival models (H084, H085).
- **Notes**: Per-city remapping required. Do not use as a prediction input; use only to derive `event` and `duration`.

### parcel_id
- **Type**: categorical (high cardinality, effectively identifier)
- **Units**: parcel identifier
- **Range / typical values**: SF `block/lot` ~200k unique; NYC `bin__` ~1M unique; LA `apn` ~500k; Austin `tcad_id`; Portland `STATEIDKEY`. CHI not exposed.
- **Sources**: all loaders except Chicago.
- **Mechanism**: Lets the HDR loop cluster parallel permits at the same parcel into projects (H072) — e.g. architectural + MEP permits for the same duplex build. Parcel history (repeat applications, prior denials) is a rough reliability indicator.
- **Phase B dimension**: yes — used for parcel-level project clustering.
- **Notes**: Identifier-style; do not use as a direct model feature. Derive `parcel_prior_permit_count` as a repeat-applicant signal.

### permit_id
- **Type**: categorical (identifier, unique)
- **Units**: internal key
- **Range / typical values**: unique per row.
- **Sources**: all loaders.
- **Mechanism**: Used for deduplication across datasets and for joining to per-cycle Seattle data or NYC BIS/DOB NOW union (H083).
- **Phase B dimension**: no.
- **Notes**: Do not use as a feature. Identifier only.

---

## 3. Temporal features

### filed_date
- **Type**: date
- **Units**: calendar date
- **Range / typical values**: 2000-01-01 – 2026-04-08 after sentinel filter. SF has a 1901 sentinel that must be dropped (H008).
- **Sources**: all loaders: `filed_date` column.
- **Mechanism**: The start of the pipeline clock. Without this the research question cannot be asked.
- **Phase B dimension**: not directly — but derived features (year, month, dow, era) are swept.
- **Notes**: Sentinel date filtering required (H008). See derived features below.

### issued_date
- **Type**: date
- **Units**: calendar date
- **Range / typical values**: as above; null for pending/withdrawn permits.
- **Sources**: all loaders: `issued_date` column.
- **Mechanism**: End of the pipeline clock. Null in ~20-38% of rows depending on city, per `data_acquisition_notes.md` smoke test. Null rows are the right-censored observations (H084).
- **Phase B dimension**: not directly — but derived `duration_days = issued - filed` is the target.
- **Notes**: Never a feature. Used as target and, when null, for right-censoring label.

### filed_year
- **Type**: count (ordinal) / categorical
- **Units**: year
- **Range / typical values**: 2000 – 2026
- **Sources**: derived from `filed_date.year`.
- **Mechanism**: Captures long-term pipeline evolution — SF slowdown, Austin speedup, NYC DOB NOW rollout. Regulatory reforms happen on year boundaries (SB 423 [136] 2024-01-01; HOME-1 [186] late 2023; HB 267 [56] 2024-07-01). H016.
- **Phase B dimension**: yes — swept with binning (H093) and interaction (H036).
- **Notes**: Treat as ordinal for XGBoost; for linear models one-hot.

### filed_month
- **Type**: cyclic
- **Units**: 1-12
- **Range / typical values**: 1-12; seasonal load peaks in spring (Mar-May).
- **Sources**: derived from `filed_date.month`.
- **Mechanism**: Permit offices experience seasonal load. M/M/c with time-varying arrivals [115]; Mayer-Somerville [14] show seasonal permit-volume patterns. H015.
- **Phase B dimension**: yes — cyclic encoding `(sin(2*pi*m/12), cos(2*pi*m/12))`.
- **Notes**: Cyclic encoding beats one-hot for tree-based models modestly.

### filed_dow (day-of-week)
- **Type**: cyclic / categorical
- **Units**: 0 (Monday) – 6 (Sunday)
- **Range / typical values**: Monday-Friday dominant (~90%); weekend filings rare and mostly online.
- **Sources**: derived from `filed_date.weekday()`.
- **Mechanism**: Monday filings enter service the same day; Friday filings wait 2-3 days before active review. Classical arrival-time offset. H014.
- **Phase B dimension**: yes — small effect.
- **Notes**: One-hot or cyclic. Low signal but cheap.

### is_holiday_week (derived)
- **Type**: binary
- **Units**: 0/1
- **Range / typical values**: ~10% positive
- **Sources**: derived from `filed_date` vs US federal holiday calendar (pandas `USFederalHolidayCalendar`).
- **Mechanism**: Holiday weeks have reduced working days. H017.
- **Phase B dimension**: yes.
- **Notes**: Cheap. Use python's `holidays` package.

### is_holiday_season (derived, coarser)
- **Type**: binary
- **Units**: 0/1
- **Range / typical values**: Nov 15 – Jan 2 ≈ 13% of calendar.
- **Sources**: derived.
- **Mechanism**: Thanksgiving / Christmas / New Year office closure clusters. H120.
- **Phase B dimension**: yes.
- **Notes**: Coarser than `is_holiday_week` but captures multi-week pauses.

### covid_era (derived)
- **Type**: binary
- **Units**: 0/1
- **Range / typical values**: ~10% positive on 2000-2026 window
- **Sources**: derived (`2020-03-01 <= filed_date <= 2021-06-30`).
- **Mechanism**: Permit office closures, rushed digitisation, inspector furloughs [190]. H018.
- **Phase B dimension**: yes — definition-of-window sweep.
- **Notes**: Alternative: use a 3-bin era (pre-2020, 2020-2021, 2022+) instead of binary.

### era (4-bin filed_year)
- **Type**: categorical (ordinal)
- **Units**: {pre-2015, 2015-2019, 2020-2021, 2022+}
- **Sources**: derived.
- **Mechanism**: Coarse eras correspond to pre-digital, digital rollout, COVID, post-COVID-reform. Tree models handle coarse bins robustly. H093.
- **Phase B dimension**: yes.
- **Notes**: Alternative to raw `filed_year`.

---

## 4. Per-stage timing features (derived from loader timestamps)

### duration_days (target)
- **Type**: continuous (count of days)
- **Units**: days
- **Range / typical values**: 1 – 2000 (after clipping per H009); P50 Austin ~60–90, SF ~200–300; tail can exceed 1,400 [83].
- **Sources**: derived `(issued_date - filed_date).dt.days` from all loaders.
- **Mechanism**: The research question's target.
- **Phase B dimension**: not a feature — this is the target.
- **Notes**: Log-transform strongly recommended.

### pre_approval_days (SF, NYC derived)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 0 – 1,500; dominated by SF discretionary review [30, 281].
- **Sources**: derived. SF: `approved_date - filed_date` (via `plan_check_start_date` / `plan_check_end_date` already in schema). NYC: `approved - pre__filing_date`. Not computable for Chicago, Austin, LA, Seattle without extra fields.
- **Mechanism**: Separates the "political and plan-check" wait from "administrative issuance" wait. H006, H007.
- **Phase B dimension**: yes — becomes target in two-model decomposition (H007).
- **Notes**: Use as target in decomposition models, not as feature.

### post_approval_days (SF, NYC derived)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 0 – 200; mostly fee/sign-off bookkeeping.
- **Sources**: SF `issued_date - approved_date`; NYC `fully_permitted - approved`.
- **Mechanism**: The administrative bucket after plan check approval. Typically small and city-stable. H006.
- **Phase B dimension**: yes — target for decomposition part 2.
- **Notes**: Can go negative if dates are out of order; clip to [0, inf).

### paid_lag_days (NYC)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 0 – 180; median 0–5.
- **Sources**: NYC legacy BIS `paid - pre__filing_date`, from RPC.
- **Mechanism**: Fee-processing lag after filing. Feed-collection queue; evidence of applicant-side delay.
- **Phase B dimension**: yes — NYC-specific feature. H004.
- **Notes**: Requires BIS dataset specifically; DOB NOW has different field semantics.

### fully_paid_lag_days (NYC)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 0 – 90.
- **Sources**: NYC `fully_paid - paid`.
- **Mechanism**: Time from initial fee to full payment; applicant response latency on fee disputes. H004.
- **Phase B dimension**: yes.
- **Notes**: NYC BIS only.

### approve_to_issue_days (NYC)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 0 – 180.
- **Sources**: NYC `fully_permitted - approved`.
- **Mechanism**: Administrative gap between plan-check approval and formal issuance. Direct hand-off bottleneck [87, 107]. H005.
- **Phase B dimension**: yes.
- **Notes**: NYC BIS only; DOB NOW's `first_permit_date` is slightly different semantics.

### intake_to_plancheck_days (Portland)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 0 – 120
- **Sources**: Portland `INTAKECOMPLETEDATE - CREATEDATE` via `_ms_dt()`.
- **Mechanism**: Portland uniquely isolates the intake phase via `INTAKECOMPLETEDATE` [data_sources.md section 16]. The cleanest intake/plan-check split of any city.
- **Phase B dimension**: yes — part of per-stage decomposition.
- **Notes**: Portland only.

### plancheck_to_issue_days (Portland, SF, LA)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 10 – 1,000 for large projects.
- **Sources**: Portland `ISSUED - INTAKECOMPLETEDATE`; SF `issued_date - approved_date`; LA n/a (issue_date is the only plan-check endpoint).
- **Mechanism**: Isolates active plan-check stage from administrative wait.
- **Phase B dimension**: yes.
- **Notes**: Same treatment as pre/post split.

### numberreviewcycles (Seattle)
- **Type**: count
- **Units**: cycles
- **Range / typical values**: 1 – 10+; median 2–3 for duplex per `data_sources.md` sample.
- **Sources**: Seattle RPC `tqk8-y2z5.numberreviewcycles`; not in the normalised schema but computable via `raw.groupby('permitnum').numberreviewcycles.max()`.
- **Mechanism**: **The single highest-signal feature in the inventory.** Direct per-permit rework count. Austin's 10-business-days-per-cycle rule of thumb [338] and BPIC 2015 [107] make this the most mechanically explanatory variable for Seattle durations. H002, H082.
- **Phase B dimension**: yes — core per-stage feature.
- **Notes**: Seattle only. The closest analogues in other cities must be derived from repeat-applicant patterns or free-text NLP.

### daysinitialplanreview (Seattle)
- **Type**: count (days)
- **Units**: days
- **Range / typical values**: 0 – 365; median 30–60 for SFR/duplex.
- **Sources**: Seattle RPC `tqk8-y2z5.daysinitialplanreview`.
- **Mechanism**: Service time in the first round of plan review, excluding later rework and corrections. Pre-computed by SDCI. H080.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### daysplanreviewcity (Seattle)
- **Type**: count (days)
- **Units**: days
- **Range / typical values**: 0 – 500; median 50–100 for SFR/duplex.
- **Sources**: Seattle RPC `tqk8-y2z5.daysplanreviewcity`.
- **Mechanism**: Cumulative city-side review time (reviewer actively holding the case). Distinguishes from `daysoutcorrections` (applicant-side). H081.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### daysoutcorrections (Seattle)
- **Type**: count (days)
- **Units**: days
- **Range / typical values**: 0 – 900; example row has 825 days [data_sources.md section 14].
- **Sources**: Seattle RPC `tqk8-y2z5.daysoutcorrections`.
- **Mechanism**: Applicant-side correction-response time. Typically the dominant component of Seattle duration for slow cases. The "smoking gun" the research question asks about. H003.
- **Phase B dimension**: yes.
- **Notes**: Seattle only. One of the highest-expected-effect features in the inventory.

### totaldaysplanreview (Seattle)
- **Type**: count (days)
- **Units**: days
- **Range / typical values**: 0 – 1,100
- **Sources**: Seattle RPC `tqk8-y2z5.totaldaysplanreview`.
- **Mechanism**: Pre-computed sum of city + corrections + other plan review time. Validation and cross-check.
- **Phase B dimension**: no — close to target leakage.
- **Notes**: Do NOT use as feature when predicting `duration_days` — very close to target. Use only for validation and per-stage consistency checks.

### rework_rate (derived, Seattle)
- **Type**: continuous
- **Units**: cycles per reviewtype
- **Range / typical values**: 1.0 – 4.0
- **Sources**: derived `numberreviewcycles / num_distinct_reviewtypes`.
- **Mechanism**: Normalised rework intensity; independent of how many review types a permit went through. Connected to process-mining rework-rate metrics [87, 92, 93, 94, 107]. H079.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### standardplan (Seattle boolean)
- **Type**: binary
- **Units**: 0/1
- **Range / typical values**: ~5-15% positive.
- **Sources**: Seattle RPC `tqk8-y2z5.standardplan`.
- **Mechanism**: Pre-approved prototype plans skip normal plan check entirely. A direct fast-track indicator. H074.
- **Phase B dimension**: yes.
- **Notes**: Seattle only. Treat standardplan=True permits as a control group for the rework analysis.

### reviewcomplexity (Seattle categorical)
- **Type**: categorical (ordinal)
- **Units**: {Basic, Basic+, Full, Full+}
- **Sources**: Seattle RPC `tqk8-y2z5.reviewcomplexity`.
- **Mechanism**: Permit-office-assigned complexity label, directly related to expected review effort. H075.
- **Phase B dimension**: yes — encoded ordinally.
- **Notes**: Seattle only.

### reviewer (Seattle high-cardinality categorical)
- **Type**: categorical (high cardinality)
- **Units**: reviewer name
- **Range / typical values**: hundreds of distinct reviewers.
- **Sources**: Seattle RPC `tqk8-y2z5.reviewer`.
- **Mechanism**: Individual reviewer throughput varies. Literature review open question #3 flags this as the principal unobserved driver outside Seattle. H076.
- **Phase B dimension**: yes — K-fold target encoding.
- **Notes**: Seattle only. Must use K-fold target encoding to avoid leakage.

### reviewteam (Seattle categorical)
- **Type**: categorical
- **Units**: review team name
- **Range / typical values**: ~20-30 distinct teams.
- **Sources**: Seattle RPC.
- **Mechanism**: Coarser grouping than individual reviewer, more stable. H077.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### reviewtype_set (Seattle derived)
- **Type**: categorical (set)
- **Units**: set of review types {Zoning, Structural Engineer, Fire, Building, MEP, ...}
- **Sources**: derived from Seattle RPC grouped.
- **Mechanism**: Permits triggering fire review or structural engineering review are systematically slower. This is the Seattle-only analog of per-discipline stage decomposition.
- **Phase B dimension**: yes — binarised per review type.
- **Notes**: Seattle only. Multi-hot encoding.

### fitness_score (Seattle process-mining derived)
- **Type**: continuous
- **Units**: [0, 1]
- **Range / typical values**: 0.5 – 1.0
- **Sources**: derived from pm4py inductive miner + alignment [89, 90, 95, 96].
- **Mechanism**: Per-trace conformance fitness to a discovered reference Petri net. Low fitness = unusual routing = long duration. H104.
- **Phase B dimension**: yes.
- **Notes**: Seattle only. Requires inductive miner to have been run first.

---

## 5. Location / political-context features

### neighborhood
- **Type**: categorical (high cardinality)
- **Units**: locally-defined neighborhood/area
- **Range / typical values**: SF `neighborhoods_analysis_boundaries` (41 neighborhoods); NYC `gis_nta_name` (195 NTAs); Chicago `community_area` (77); Austin `council_district` (10); LA `cpa` (Community Plan Area); Seattle `zoning` (reused); Portland `NEIGHBORHOOD`.
- **Sources**: all loaders.
- **Mechanism**: Literature open question #5 — neighborhood-level heterogeneity is large. Historic districts, community board culture, recent development conflict. Einstein et al. [169], Fischel [25, 220]. H020.
- **Phase B dimension**: yes — target encoding central feature.
- **Notes**: Non-comparable across cities. Use per-city target encoding. Seattle's current mapping uses `zoning` — alternative would be a true neighborhood field not present in the Plan Review dataset.

### supervisor_district (SF only)
- **Type**: categorical
- **Units**: 1–11
- **Sources**: SF RPC `supervisor_district`.
- **Mechanism**: SF's 11 supervisor districts correlate with discretionary-review patterns [25, 220]. H096.
- **Phase B dimension**: yes.
- **Notes**: SF only.

### community_board (NYC)
- **Type**: categorical
- **Units**: 1–59 plus borough
- **Sources**: NYC RPC `community___board`.
- **Mechanism**: First ULURP gate [133, 134]. Einstein-Glick-Palmer [169] documents per-board NIMBY variation. H097.
- **Phase B dimension**: yes.
- **Notes**: NYC only. Target encode.

### council_district (LA, Austin)
- **Type**: categorical
- **Units**: LA 1–15; Austin 1–10.
- **Sources**: LA RPC `cd`; Austin RPC `council_district` already in normalised schema.
- **Mechanism**: Member-deference effects [65, 66, 193, 194]. H098.
- **Phase B dimension**: yes.
- **Notes**: Target encode.

### ward (Chicago)
- **Type**: categorical
- **Units**: 1–50.
- **Sources**: Chicago RPC `ward`.
- **Mechanism**: Chicago's aldermanic privilege [43, 187, 188] makes ward the single most important political variable for Chicago permits. H099.
- **Phase B dimension**: yes.
- **Notes**: Chicago only. Target encode.

### neighborhood_coalition (Portland)
- **Type**: categorical
- **Units**: ~7 coalitions
- **Sources**: Portland RPC `NEIGHBORHOOD_COALITION`.
- **Mechanism**: Portland's neighborhood-group political structure drives appeal activity. H100.
- **Phase B dimension**: yes.
- **Notes**: Portland only.

### zoning_dist1 (NYC)
- **Type**: categorical
- **Units**: NYC zoning codes (R1, R2, ..., C1, C2, ...)
- **Range / typical values**: ~100 distinct codes.
- **Sources**: NYC RPC.
- **Mechanism**: NYC zoning directly controls as-of-right vs ULURP path [133, 134]. H068.
- **Phase B dimension**: yes.
- **Notes**: NYC only. Target encode.

### zone (LA)
- **Type**: categorical
- **Units**: LA zoning codes
- **Sources**: LA RPC `zone`.
- **Mechanism**: LA zoning directly controls which review path applies.
- **Phase B dimension**: yes.
- **Notes**: LA only.

### application_submission_method (SF)
- **Type**: categorical
- **Units**: {in-house, online}
- **Sources**: SF RPC `application_submission_method`.
- **Mechanism**: Online submissions flow through a digital track; counter submissions are slower. H065. Flagged in `data_acquisition_notes.md` as high-value.
- **Phase B dimension**: yes.
- **Notes**: SF only.

### change_of_use (SF derived)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived from SF `existing_use != proposed_use`.
- **Mechanism**: Change-of-use triggers additional zoning review. H067.
- **Phase B dimension**: yes.
- **Notes**: SF only.

### professional_cert (NYC)
- **Type**: binary
- **Units**: 0/1
- **Sources**: NYC RPC `professional_cert`.
- **Mechanism**: Licensed professional self-certification skips DOB review. Major NYC fast track. H069.
- **Phase B dimension**: yes.
- **Notes**: NYC only. Flagged in `data_acquisition_notes.md` as high-value.

### business_unit (LA)
- **Type**: categorical
- **Units**: {Regular Plan Check, Express Permit, OTC}
- **Sources**: LA RPC `business_unit`.
- **Mechanism**: Direct pipeline-lane indicator. H041. Flagged in `data_acquisition_notes.md` and `data_sources.md` section 6.
- **Phase B dimension**: yes.
- **Notes**: LA only.

### review_type (Chicago)
- **Type**: categorical
- **Units**: {NEW CONSTRUCTION, STANDARD PLAN REVIEW, EASY PERMIT, SIGN PERMIT, DIRECT DEVELOPER SERVICES, ...}
- **Sources**: Chicago RPC `review_type`.
- **Mechanism**: Analogous to LA `business_unit`. H042. Already in normalised schema as `permit_subtype`.
- **Phase B dimension**: yes.
- **Notes**: Chicago only. Distinct pipeline lanes.

### masterpermitnum (Austin)
- **Type**: categorical (grouping key)
- **Sources**: Austin RPC `masterpermitnum`.
- **Mechanism**: Groups sibling permits (BP, MP, EP, PP) for a single project. H070.
- **Phase B dimension**: yes — via derived `master_group_size`.
- **Notes**: Austin only.

### project_id (Austin)
- **Type**: categorical (grouping key)
- **Sources**: Austin RPC `project_id`.
- **Mechanism**: Alternative grouping. H071.
- **Phase B dimension**: yes.
- **Notes**: Austin only.

### contractor_name (Chicago, Portland)
- **Type**: categorical (high cardinality)
- **Sources**: Chicago RPC `contact_1_name` / `contact_1_type`; Portland RPC unknown but typically present.
- **Mechanism**: Contractor identity captures experience and repeat-applicant quality. H073.
- **Phase B dimension**: yes — via `contractor_prior_count`.
- **Notes**: Chicago and Portland only. Target encode.

---

## 6. Process-mining derived features

### num_distinct_reviewtypes (Seattle)
- **Type**: count
- **Units**: integer
- **Range / typical values**: 1 – 8
- **Sources**: derived from Seattle RPC grouped by `permitnum`.
- **Mechanism**: Number of distinct review disciplines (zoning, fire, structural, building, MEP). More disciplines = more hand-offs.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### alpha_miner_trace_length (Seattle)
- **Type**: count
- **Units**: events per trace
- **Range / typical values**: 5 – 50
- **Sources**: derived via pm4py [328].
- **Mechanism**: Number of events in the per-permit trace. Longer traces indicate more complex routing. H102.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### inductive_miner_loop_count (Seattle)
- **Type**: count
- **Units**: loop executions
- **Range / typical values**: 0 – 10
- **Sources**: derived from pm4py inductive miner [95, 96].
- **Mechanism**: Counts the number of times a case traversed a known loop in the discovered process model. H101.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### conformance_cost (Seattle)
- **Type**: continuous
- **Units**: alignment cost
- **Range / typical values**: 0 – 20
- **Sources**: derived from pm4py alignments [89, 90].
- **Mechanism**: Log-based distance from the discovered reference Petri net. H104.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

### heuristic_miner_complexity (Seattle)
- **Type**: continuous
- **Units**: dependency graph complexity
- **Sources**: derived from pm4py heuristic miner [92, 93, 94]. H103.
- **Mechanism**: Captures routing complexity of the case.
- **Phase B dimension**: yes.
- **Notes**: Seattle only.

---

## 7. City-level static covariates (external / contextual)

### wrluri_score
- **Type**: continuous
- **Units**: standardised index (mean 0, sd 1)
- **Range / typical values**: -2.0 – +2.5; SF ~+2, Austin ~0, Chicago ~-0.5 (illustrative).
- **Sources**: Gyourko-Saiz-Summers 2008 [2] and Gyourko-Hartley-Krimmel 2021 [3]. Public at wrluri.com.
- **Mechanism**: Standard regulatory-stringency covariate; should explain a lot of cross-city mean duration. H046.
- **Phase B dimension**: yes — alternative to city one-hot.
- **Notes**: Only 2 time points (2006, 2018) — treat as static. Join by city to all rows.

### acs_density
- **Type**: continuous
- **Units**: residents per sq mile (tract or block-group)
- **Range / typical values**: 0 – 100,000; P50 ~ 10,000 urban.
- **Sources**: Census ACS 5-year estimates. Join by zip code (H048).
- **Mechanism**: Density correlates with zoning stringency and neighborhood demographics [18, 19].
- **Phase B dimension**: yes.
- **Notes**: Join granularity is zip or tract; match to permit `zipcode` or derived tract.

### bps_monthly_permits
- **Type**: count
- **Units**: permits per place per month
- **Range / typical values**: 0 – 2,000.
- **Sources**: US Census BPS [71, 72, 73, 301–308] Place files. See `data_sources.md` section 11.
- **Mechanism**: Captures pipeline-level load (input arrival rate). Directly feeds Little's-Law ρ computation [116, 117]. H047.
- **Phase B dimension**: yes.
- **Notes**: Aggregate only — no per-permit info. Join by place code + month.

### rolling_30d_permit_count_city (derived)
- **Type**: count
- **Units**: permits in prior 30 days, same city
- **Range / typical values**: 0 – 10,000.
- **Sources**: derived from each city's own dataset.
- **Mechanism**: Direct within-dataset load proxy. H053. Avoids BPS join and is finer-grained.
- **Phase B dimension**: yes.
- **Notes**: Compute as `filed_date`-indexed rolling count grouped by city.

### rolling_90d_permit_count_city
- **Type**: count
- **Units**: permits in prior 90 days
- **Range / typical values**: 0 – 30,000.
- **Sources**: derived.
- **Mechanism**: Seasonal-scale load proxy. H054.
- **Phase B dimension**: yes.
- **Notes**: Alternative horizon for H053.

### rolling_90d_permit_count_neighborhood
- **Type**: count
- **Units**: permits in prior 90 days, same neighborhood
- **Sources**: derived.
- **Mechanism**: Neighborhood-level load — captures localised reviewer assignment. H116.
- **Phase B dimension**: yes.
- **Notes**: Null if neighborhood is sparse.

### nbhd_days_since_last_permit
- **Type**: continuous
- **Units**: days
- **Sources**: derived.
- **Mechanism**: Recency measure — new in a recently-active neighborhood is different from new in a quiet one. H052.
- **Phase B dimension**: yes.
- **Notes**: Null for first permit in neighborhood.

### fred_mortgage_rate
- **Type**: continuous
- **Units**: percent
- **Range / typical values**: 2.5 – 8.0
- **Sources**: FRED MORTGAGE30US, joined by filing month.
- **Mechanism**: Macro demand proxy. H049.
- **Phase B dimension**: yes.
- **Notes**: National series — not city-specific.

### fred_housing_starts
- **Type**: continuous
- **Units**: thousands per month
- **Range / typical values**: 500 – 2,500 (national)
- **Sources**: FRED HOUST, or HOUST1FQ by region.
- **Mechanism**: Regional pipeline pressure. H051.
- **Phase B dimension**: yes.
- **Notes**: Regional series.

### bls_construction_employment
- **Type**: continuous
- **Units**: employees (thousands)
- **Range / typical values**: varies by MSA.
- **Sources**: BLS CES construction employment, joined by MSA and month.
- **Mechanism**: Local construction-sector activity; correlated with contractor availability and pipeline demand. H050.
- **Phase B dimension**: yes.
- **Notes**: MSA-level series.

### contractor_prior_permit_count (derived)
- **Type**: count
- **Units**: prior permits filed by same contractor
- **Sources**: derived rolling count.
- **Mechanism**: Repeat applicants submit cleaner packets. H073.
- **Phase B dimension**: yes.
- **Notes**: Chicago, Portland only (contractor names exposed).

### parcel_prior_permit_count (derived)
- **Type**: count
- **Units**: prior permits at same parcel
- **Sources**: derived.
- **Mechanism**: Parcels with prior permits have established history — either smoother (contractor knows the site) or rougher (prior denials). Ambiguous sign.
- **Phase B dimension**: yes.
- **Notes**: SF, NYC, LA, Austin, Portland.

---

## 8. Reform / natural-experiment indicators

### post_sb423 (CA cities only)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived `filed_date >= 2024-01-01` for SF and LA only.
- **Mechanism**: SB 423 [136, 138, 276, 277, 278] extended SB 35 streamlining. SF 114-day vs 280-day effect documented [83]. H037, H038.
- **Phase B dimension**: yes — RD design sweeps window width.
- **Notes**: California cities only; CA SF, LA, (Austin is TX and exempt; Seattle is WA; Portland is OR). Only applies to qualifying multifamily projects per the statute.

### post_home1 (Austin only)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived `filed_date >= 2023-12-05` for Austin. (HOME-1 enacted late 2023.)
- **Mechanism**: Austin HOME Phase 1 [62, 63, 64, 186, 258] legalised 3-unit-on-SFR lot. 86% permit volume increase in first year [64]. H037, H039.
- **Phase B dimension**: yes.
- **Notes**: Austin only.

### post_home2 (Austin only)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived `filed_date >= 2024-05-16` for Austin.
- **Mechanism**: HOME Phase 2 further reduced minimum lot size. Distinct natural experiment from HOME-1. H037.
- **Phase B dimension**: yes.
- **Notes**: Austin only.

### post_dob_now (NYC, by work type)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived from staggered DOB NOW rollout dates [74, 75, 76, 190].
- **Mechanism**: DOB NOW is a fundamentally different IT system than BIS. Durations should structurally change post-rollout. H040, H117.
- **Phase B dimension**: yes.
- **Notes**: NYC only. Requires knowledge of per-work-type rollout dates.

### post_hb267 (FL)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived — but FL is not in the loader set, so this is a placeholder for future expansion.
- **Mechanism**: Florida HB 267 [56] mandates 30-day processing for small residential. H037.
- **Phase B dimension**: no (no FL loader).
- **Notes**: Feature defined but not applicable to current city set.

### post_ab2011 (CA)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived `filed_date >= 2023-07-01` for SF and LA.
- **Mechanism**: AB 2011 [137, 271–273] legalised multifamily on commercial corridors. H037.
- **Phase B dimension**: yes.
- **Notes**: CA cities only.

### post_ab130 (CA)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived `filed_date >= 2025-07-01` for SF and LA.
- **Mechanism**: California AB 130 [270, 285] exempts most infill urban housing from CEQA.
- **Phase B dimension**: yes.
- **Notes**: CA cities only.

### days_since_reform_X
- **Type**: continuous
- **Units**: days since specific reform.
- **Sources**: derived.
- **Mechanism**: Running variable in regression discontinuity designs. H038, H039.
- **Phase B dimension**: yes.
- **Notes**: One per reform.

### reform_decay_exponential
- **Type**: continuous
- **Units**: `exp(-days_since_reform/tau)`, tau ~ 90 days
- **Range / typical values**: [0, 1]
- **Sources**: derived.
- **Mechanism**: Smooth reform-uptake curve. H119.
- **Phase B dimension**: yes — sweep tau.
- **Notes**: One per reform.

### disaster_rebuild_flag (per city)
- **Type**: binary
- **Units**: 0/1
- **Sources**: derived — Camp Fire 2018 (Paradise, not loaded), LA 2025 fires (LA), Hurricane Ian 2022 (FL, not loaded), etc.
- **Mechanism**: Emergency fast-tracks after disasters. H112.
- **Phase B dimension**: yes.
- **Notes**: Requires per-city disaster-event table.

---

## 9. Target and censoring labels

### duration_days (target)
- **Type**: continuous
- **Units**: days
- **Range / typical values**: 1 – 2000 after clipping.
- **Sources**: derived `(issued_date - filed_date).dt.days`.
- **Mechanism**: Primary target variable.
- **Phase B dimension**: not a feature — target.
- **Notes**: See H009, H031, H032, H033 for transform variants.

### event (censoring indicator)
- **Type**: binary
- **Units**: 0 (censored) / 1 (issued)
- **Sources**: derived `event = (issued_date is not None)`.
- **Mechanism**: Required for Cox/AFT survival models [118, 121, 122]. H084.
- **Phase B dimension**: not a feature — label.
- **Notes**: All survival-analysis hypotheses require this.

### censored_duration
- **Type**: continuous
- **Units**: days
- **Sources**: derived `today - filed_date` for rows where `issued_date is None`.
- **Mechanism**: Lower bound on true duration for right-censored cases. H084.
- **Phase B dimension**: not a feature — label component.
- **Notes**: Pair with `event = 0`.

### terminal_state (competing risks)
- **Type**: categorical
- **Units**: {issued, withdrawn, denied, expired, open}
- **Sources**: derived from `status`.
- **Mechanism**: Distinguishes right-censoring from competing-risks exits. Required for DeepHit [124, 125]. H085.
- **Phase B dimension**: not a feature — label.
- **Notes**: Per-city status code mapping required.

---

## 10. Variable summary table

Legend: Baseline = used by Phase 0.5 quantile regression baseline; Phase 2 = hypothesis set in `research_queue.md`; Phase B = swept in discovery sweep.

| Variable | Type | Primary source | Baseline | Phase 2 | Phase B |
|---|---|---|:-:|:-:|:-:|
| city | cat | all loaders | yes | yes | yes |
| permit_type | cat | all loaders | yes | yes | yes |
| permit_subtype | cat | all loaders | yes | yes | yes |
| use_code | cat | all except chi | no | yes | yes |
| status | cat | all loaders | no (label only) | yes (label) | no |
| parcel_id | cat (id) | all except chi | no | yes (grouping) | no |
| valuation_usd | num | sf/nyc/la/chi/pdx | yes | yes | yes |
| log1p_valuation_usd | num | derived | no | yes (H011) | yes |
| unit_count | num | sf/nyc/la/pdx/sea | yes | yes | yes |
| log1p_unit_count | num | derived | no | yes (H012) | yes |
| square_feet | num | nyc/la/pdx | no | yes | yes |
| log1p_square_feet | num | derived | no | yes (H013) | yes |
| valuation_delta_usd | num | sf derived | no | yes (H010) | yes |
| plansets | num | sf rpc | no | yes (H066) | no |
| total_fee | num | chi rpc | no | yes (H094) | yes |
| filed_date | date | all | yes | yes | no |
| issued_date | date | all | yes (target) | yes (target) | no |
| filed_year | ord | derived | yes | yes (H016) | yes |
| filed_month | cyc | derived | no | yes (H015) | yes |
| filed_dow | cyc | derived | no | yes (H014) | yes |
| is_holiday_week | bin | derived | no | yes (H017) | yes |
| is_holiday_season | bin | derived | no | yes (H120) | yes |
| covid_era | bin | derived | no | yes (H018) | yes |
| era (4-bin) | cat | derived | no | yes (H093) | yes |
| pre_approval_days | num | sf/nyc derived | no | yes (H006, H007) | yes |
| post_approval_days | num | sf/nyc derived | no | yes (H006, H007) | yes |
| paid_lag_days | num | nyc rpc | no | yes (H004) | yes |
| fully_paid_lag_days | num | nyc rpc | no | yes (H004) | yes |
| approve_to_issue_days | num | nyc derived | no | yes (H005) | yes |
| intake_to_plancheck_days | num | pdx derived | no | yes | yes |
| plancheck_to_issue_days | num | sf/pdx derived | no | yes | yes |
| numberreviewcycles | num | sea rpc | no | yes (H002) | yes |
| daysinitialplanreview | num | sea rpc | no | yes (H080) | yes |
| daysplanreviewcity | num | sea rpc | no | yes (H081) | yes |
| daysoutcorrections | num | sea rpc | no | yes (H003) | yes |
| totaldaysplanreview | num | sea rpc | no | no (leakage) | no |
| rework_rate | num | sea derived | no | yes (H079) | yes |
| standardplan | bin | sea rpc | no | yes (H074) | yes |
| reviewcomplexity | ord | sea rpc | no | yes (H075) | yes |
| reviewer | cat | sea rpc | no | yes (H076) | yes |
| reviewteam | cat | sea rpc | no | yes (H077) | yes |
| reviewtype_set | multi-hot | sea rpc | no | yes | yes |
| fitness_score | num | sea derived | no | yes (H104) | yes |
| alpha_miner_trace_length | num | sea derived | no | yes (H102) | yes |
| inductive_miner_loop_count | num | sea derived | no | yes (H101) | yes |
| conformance_cost | num | sea derived | no | yes (H104) | yes |
| heuristic_miner_complexity | num | sea derived | no | yes (H103) | yes |
| num_distinct_reviewtypes | num | sea derived | no | yes | yes |
| neighborhood | cat | all loaders | no | yes (H020) | yes |
| supervisor_district | cat | sf rpc | no | yes (H096) | yes |
| community_board | cat | nyc rpc | no | yes (H097) | yes |
| council_district | cat | la/aus rpc | no | yes (H098) | yes |
| ward | cat | chi rpc | no | yes (H099) | yes |
| neighborhood_coalition | cat | pdx rpc | no | yes (H100) | yes |
| zoning_dist1 | cat | nyc rpc | no | yes (H068) | yes |
| zone | cat | la rpc | no | yes | yes |
| application_submission_method | cat | sf rpc | no | yes (H065) | yes |
| change_of_use | bin | sf derived | no | yes (H067) | yes |
| professional_cert | bin | nyc rpc | no | yes (H069) | yes |
| business_unit | cat | la rpc | no | yes (H041) | yes |
| review_type | cat | chi rpc | no | yes (H042) | yes |
| masterpermitnum_group_size | num | aus derived | no | yes (H070) | yes |
| project_id_group_size | num | aus derived | no | yes (H071) | yes |
| contractor_prior_permit_count | num | chi/pdx derived | no | yes (H073) | yes |
| parcel_prior_permit_count | num | derived | no | yes | yes |
| wrluri_score | num | external [2, 3] | no | yes (H046) | yes |
| acs_density | num | external | no | yes (H048) | yes |
| bps_monthly_permits | num | external [71-73] | no | yes (H047) | yes |
| rolling_30d_permit_count_city | num | derived | no | yes (H053) | yes |
| rolling_90d_permit_count_city | num | derived | no | yes (H054) | yes |
| rolling_90d_permit_count_neighborhood | num | derived | no | yes (H116) | yes |
| nbhd_days_since_last_permit | num | derived | no | yes (H052) | yes |
| fred_mortgage_rate | num | external FRED | no | yes (H049) | yes |
| fred_housing_starts | num | external FRED | no | yes (H051) | yes |
| bls_construction_employment | num | external BLS | no | yes (H050) | yes |
| post_sb423 | bin | derived | no | yes (H037, H038) | yes |
| post_home1 | bin | derived | no | yes (H037, H039) | yes |
| post_home2 | bin | derived | no | yes (H037) | yes |
| post_dob_now | bin | derived | no | yes (H040, H117) | yes |
| post_ab2011 | bin | derived | no | yes (H037) | yes |
| post_ab130 | bin | derived | no | yes (H037) | yes |
| days_since_reform_X | num | derived | no | yes (H038, H039) | yes |
| reform_decay_exponential | num | derived | no | yes (H119) | yes |
| disaster_rebuild_flag | bin | external | no | yes (H112) | yes |
| city_year interaction | derived cat | derived | no | yes (H036) | yes |
| duration_days (target) | num | derived | yes | yes | no |
| event (label) | bin | derived | no | yes (H084) | no |
| censored_duration | num | derived | no | yes (H084) | no |
| terminal_state | cat | derived | no | yes (H085) | no |

---

## Notes on coverage gaps

The following design dimensions are referenced in the literature review but are NOT in the current loader set and would require new data pulls:

- **Per-RFI correction letter timestamps** for cities other than Seattle. Would require scraping SF DBI public records, NYC BIS detail pages, or filing FOIA requests. Mentioned in `data_acquisition_notes.md` as Gap #1.
- **Reviewer identity** for cities other than Seattle. Gap #3 in `data_acquisition_notes.md`.
- **Full BPI Challenge 2015 event log** [102, 103] for the Dutch municipalities validation benchmark. Not yet in the loader.
- **NYC DOB NOW joined with BIS** — requires implementing H083 to union `ic3t-wcy2` and `w9ak-ipjd`.
- **Boston and Philadelphia filing dates** — blocked per `data_acquisition_notes.md` Gap #2.
- **Chicago work_description free text** for duplex detection — requires NLP on top of the normalised schema. Gap #4.

Also worth noting: feature encoding dimensions (target encoding K, monotonicity constraint set, XGBoost `max_depth`/`learning_rate`/`min_child_weight`/`subsample`/`colsample_bytree`/`reg_alpha`/`reg_lambda`/`n_estimators`) are themselves Phase B sweep levers and are covered in H086-H092 of `research_queue.md`. They are not listed individually here because they are model hyperparameters, not input features.
