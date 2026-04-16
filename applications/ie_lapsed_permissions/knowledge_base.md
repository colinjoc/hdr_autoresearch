# Knowledge base — lapsed permissions

## Stylised facts (from literature + smoke tests)

- Ireland's Planning and Development Act 2000 establishes 5-year default permission validity (s40), extendable via Section 42 typically up to 5 further years, and under the 2025 Planning and Development (Amendment) Act s28 by up to an additional 3 years for uncommenced residential permissions.
- The CSO BHQ15 series (starting 2019Q1) reports permissions granted by quarter and dwelling type; BHQ01 historical series covers 2001Q1 to 2014Q1; there is a temporal gap for aggregate cross-validation between 2014Q2 and 2018Q4 at national level.
- The BCMS (Building Control Management System) records commencement notices filed under S6 of the Building Control Act; it is the proximate source for CSO NDC02 commencement statistics. Matching key to planning register: `CN_Planning_Permission_Number` ↔ `Application Number`.
- The National Planning Application register has 491,206 rows (2012-2026), of which 317,041 have a populated GrantDate. Top application types: PERMISSION (286k), RETENTION (46k), OUTLINE PERMISSION (10k); top decisions: CONDITIONAL (232k), GRANT PERMISSION (58k), REFUSED (32k).
- BCMS has 183,633 residential-type rows with GrantDate populated. Not all commencement notices include the planning permission number (expect ~80-95% coverage based on sibling PL-1 project experience).
- International lapse benchmarks: UK residential 6-8% for <10 units, 11-14% overall (Lichfields 2016, 2023). NZ 10% steady-state, 20%+ post-crash (Auckland Council 2016). No comparable historic Irish aggregate.
- The 2017-2021 Strategic Housing Development regime (SHD) allowed direct-to-ABP applications for 100+ unit schemes, and produced ~50k permissions 2018-2021. Many SHD permissions faced judicial review; LRD replaced SHD in 2021.
- Housing Commission (2024) quotes ~60k "live permissions" but does not net out un-commenced vs already-commenced vs extended.

## Known methodology pitfalls

- **Reporting-channel confounding**: BCMS presence is a matching artefact; a developer can commence without filing a correctly-linked commencement notice if the permission number field is omitted, mistyped, or the scheme is phased and only later phases filed. Our E01-E02-E19 experiments bound this.
- **Right-censoring for 2019 cohort**: 2019 + 5-year default = 2024; 2019 + S42 extension = up to 2029; so 2019 cohort is NOT fully matured even at ETL 2026. E16 right-censors explicitly; headline E00 filters to 2014-2019 but treats 2019 as a sensitivity boundary.
- **RETENTION applications**: these apply for permission after construction; they do not represent a pipeline of future units. Filter them out for the lapse analysis.
- **OUTLINE permissions**: are not build-ready and require subsequent PERMISSION application before BCMS can be filed. Separating OUTLINE from PERMISSION is essential.
- **One-off houses**: different economics (owner-occupier, self-build) and should be analysed separately; lapse rate is confounded with personal-circumstance exits.
- **Application number format**: Irish LAs use varying formats (e.g. "21/123", "21-123", "P2021/0123"); exact matching misses variants. Normalisation improves match rate.
- **Multi-phase schemes**: a single permission can generate multiple BCMS rows (one per phase). Many-to-one join must count permission as matched if ≥1 BCMS row; avoid row duplication.
- **Withdrawn applications**: WithdrawnDate populated indicates the applicant pulled before grant; these should be filtered from lapse analysis since no permission was ever granted (despite some having DecisionDate backfilled).
- **Refused applications**: Decision=REFUSED means no permission to build; filter.
- **Re-granted permissions**: some sites have multiple PERMISSION applications over years; treating each independently double-counts. We document but do not deduplicate (each permission is its own option).
- **Extension events**: no national dataset exists. BCMS match occurring AFTER ExpiryDate is a proxy for extension (E11).

## Caveats to declare in paper §Caveats

1. Extension rate is unobservable at national level; "no BCMS match" conflates lapse + extended + data-join failure.
2. Applicant identity is not uniquely keyed; corporate vs individual is proxied by Forename presence.
3. LA boundary redraws (e.g. unified Cork etc) introduce minor time-series discontinuities.
4. BCMS residential filter may exclude small extensions/granny flats that nominally have planning permission.
5. 2019 cohort is right-censored at ETL 2026; main E00 number is sensitive to this — report with/without 2019.
6. Phased commencements filed years apart risk misclassification if only first filing carries the permission number.
