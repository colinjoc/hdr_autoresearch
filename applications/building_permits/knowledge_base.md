# Knowledge Base: US Building Permit Processing

Facts, formulas, and reference material for the HDR project on building permit processing times. Bracketed numbers refer to rows in `papers.csv`.

## 1. Standard Stages of a US Municipal Building Permit Pipeline

A "permit" in the US vernacular is typically the end-state of a multi-stage process whose upstream stages are legally distinct. The canonical stages, in logical order, are:

1. **Pre-application / intake.** The applicant files a completed application package: site plan, architectural drawings, structural calculations, MEP (mechanical/electrical/plumbing) drawings, title information, and required fees. The city performs a "screening" check for completeness. Outcome: accepted for review, or rejected as incomplete. Typical duration: 0-10 business days [184, 189, 191].
2. **Zoning / planning review.** The planning department verifies the proposed use is consistent with the zoning code: use permitted, density/FAR within limits, setbacks and height within limits, parking minimums met, neighborhood-specific overlays respected. In California, CEQA applicability is determined here [31, 141]. In NYC, this is where ULURP is triggered if a zoning change is needed [133, 134]. Outcome: zoning clearance or a denial that must be cured or appealed.
3. **Environmental review.** In California, CEQA may require an initial study, negative declaration, mitigated negative declaration, or full EIR. In NYC, SEQRA plays an analogous role. Federal NEPA applies only if federal funds or permits are involved. Typical duration: weeks to years depending on level of review.
4. **Plan check / building review.** The building department checks structural, life-safety, accessibility (ADA/CBC Chapter 11), egress, and building-code compliance. Plan check typically runs in rounds: the reviewer issues a list of corrections, the applicant returns corrected plans, the reviewer re-checks, and the cycle repeats. Each round is called a **corrections cycle**, **review cycle**, or **round-trip**. Austin's expedited program reports about 10 business days per round for commercial and typical residential projects [338].
5. **MEP review.** Mechanical, electrical, and plumbing plans are reviewed separately, often by different reviewers or divisions. In larger projects these are substantively distinct stages with their own queues [189, 191, 294].
6. **Fire department review.** The fire marshal reviews for sprinklers, standpipes, fire alarms, egress, and access. This is a legally separate step in most large US cities.
7. **Other third-party clearances.** Depending on the project and jurisdiction: health department (restaurants/pools), historic preservation review, coastal commission, airport-overlay clearance, school-district clearance, parks department, redevelopment agency, transportation review. Each has its own queue and its own review time.
8. **Permit issuance.** Once every clearance is satisfied and all fees are paid, the permit is issued. Calendar time between application date and issuance date is the **total throughput time** or **cycle time** most commonly reported.
9. **Inspection and sign-off.** Post-issuance construction inspections verify work matches the approved drawings. Final inspection and Certificate of Occupancy (CO / TCO) are downstream of issuance and not usually counted in "permit processing time" but are often part of the broader timeline for housing delivery.

**City-specific variations.**

- **San Francisco** has a two-organisation structure: SF Planning Department (entitlement, CEQA, conditional use, discretionary review, historic preservation) and SF Department of Building Inspection (DBI) for the building permit itself [191, 292, 293]. Each has its own backlog and separate timestamps.
- **New York City** uses the Department of Buildings (DOB) for as-of-right permits through DOB NOW [74, 75, 76, 189, 190, 340, 341]. Discretionary actions (zoning changes, special permits, variances) go through ULURP [133, 134], BSA, or the Landmarks Preservation Commission.
- **Los Angeles** has LADBS for plan check and permit, with separate Planning Department review for discretionary actions [81, 181, 182, 294–297].
- **Chicago** Department of Buildings, with historical aldermanic-privilege layer [43, 180, 187, 188, 298, 299, 300, 339].
- **Austin** has a single Development Services Department (ADS) with residential plan review, commercial plan review, expedited review, and express permit tracks [184, 185, 335, 336, 337]. HOME amendments affect the zoning layer [186].
- **Dutch municipalities** (relevant as the BPI Challenge 2015 benchmark) [102, 103, 107] have a single-agency permit process under the WABO Act with a statutory 8-week default decision window.

## 2. Key Timing Terminology

- **Calendar days vs working days.** Calendar days count all days; working days exclude weekends and holidays. Laws almost always specify one or the other. For example, Florida's 2024 HB 267 [56] mandated 30 days — in statute — for small residential permits (reading as business days in practice). California SB 423 [136] mandates 60 or 90 days written determinations (business days).
- **Median time to decision.** The 50th-percentile duration between application submission and the first formal agency decision (often either approval or a request for corrections). Not the same as time to issuance.
- **First action time.** The time between submission and the first action on the file by any reviewer. Often dramatically shorter than time to decision.
- **Time to issuance.** The duration between the application date and the date the permit is issued. This is the headline number most studies and press reports use. The SF 280-day and Austin 91-day figures in the SF Examiner report [83] are time-to-issuance medians.
- **Round-trip time.** One cycle of reviewer-to-applicant-to-reviewer. A "2-round" project has been through plan check twice. Each round typically takes 5-15 business days of reviewer time plus variable applicant response time.
- **Cycle time.** In process-mining and operations-research language, the total time a case spends in the system, synonymous with throughput time or time to issuance.
- **Waiting time vs service time.** Waiting time is time spent in a queue not being actively worked on. Service time is the time a reviewer actively spends on the file. Total = waiting + service. Most of the total delay in backlogged systems is waiting time, not service time.
- **Right-censoring.** A case that is still open at the time of data extraction has a duration greater than some known lower bound. Standard in survival analysis [118, 119, 121]. The 1,489-day backlog in SF [83] is a set of right-censored observations.
- **Left-truncation.** Cases that entered the pipeline before the observation window but are only observed from a later date. Handled by Klein and Moeschberger [121] and others.
- **Trace / case.** In process-mining terminology [87, 102], a "case" is a single permit application and a "trace" is the ordered sequence of event types (activity + timestamp) for that case.

## 3. Standard Rules of Thumb Used in the Literature

These are widely cited quantitative rules of thumb; they originate in different methodologies and should be treated as heuristics rather than facts.

- **Regulation is roughly 40.6% of multifamily development cost** (NMHC-NAHB 2022 survey [50, 214, 215]). Of this, the largest single component is cost from changes to building codes over the previous 10 years (about 11.1% of project cost).
- **NIMBY opposition adds an average of 5.6% to project cost and 7.4 months to project duration** [50]. 74.5% of surveyed developers had experienced it.
- **The SF process is roughly 3x slower than San Diego and 3x slower than Austin** in 2025 headline numbers: 280 days vs 134 days vs 91 days median time to issuance [83].
- **Each additional corrections cycle adds roughly 10 business days of reviewer time** in Austin's expedited program [338]. Applicant response time is additional.
- **ULURP is formally capped at 205 days** (60+60+30+50+5) but in practice often extends longer due to pre-certification delays and continuances [133, 134].
- **Little's Law**: in steady state, the mean number of cases in the system equals the mean arrival rate multiplied by the mean time each case spends in the system: *L = λ W* [116, 117]. For a system with a 1,300-case backlog and a 1,489-day mean time-in-system, arrival rate must be roughly 1,300 / 1,489 ≈ 0.87 cases per day. The SF data [83] is Little's-Law consistent.
- **M/M/c server utilisation and wait time**: for traffic intensity ρ = λ/(cμ), expected wait time in queue grows approximately as 1/(1-ρ) and becomes infinite as ρ → 1. Permit pipelines with chronic understaffing relative to arrivals are classic near-unit-ρ systems.
- **Austin's HOME-1 amendment produced an 86% increase in permit volumes for small multifamily structures in its first year** [64]. Rent went down about 5.5% for duplex properties over the same period while the broader market rose.
- **Around 85% of CEQA lawsuits in 2013-2015 were filed by non-environmental plaintiffs and 80% targeted infill development** (Holland & Knight 2018 [141]). Only ~7 of 254 Bay Area projects in O'Neill et al. [34] faced formal CEQA suits; the effect is therefore through deterrence rather than direct litigation.
- **Dutch municipalities' WABO 8-week limit was frequently violated in the BPIC 2015 dataset** [107], and the violation rate was the primary finding of process mining those logs.
- **New York City built approximately 185,000 new multifamily units in 2010-2020**, with almost all units on lots zoned for high-density residential, and nearly a third on lots upzoned under Bloomberg or de Blasio [45, 205].

## 4. Regulatory Landmarks

- **SB 35 (California, Wiener, 2017)** [135, 274, 275]. Streamlined ministerial approval process for qualifying affordable housing in jurisdictions failing to meet state RHNA. First statewide preemption of local discretionary review for housing.
- **SB 330 (California, Skinner, 2019)**. Housing Crisis Act; freezes downzoning in certain cases and limits fee increases mid-process.
- **SB 423 (California, Wiener, 2023)** [136, 138, 276, 277, 278]. Extended and expanded SB 35 streamlining. Effective January 1 2024. Extends streamlined ministerial approval to January 1 2036. Requires local agency written determination within 60-90 days.
- **AB 2011 (California, Wicks, 2022)** [137, 271–273]. Affordable Housing and High Road Jobs Act of 2022. Allows multifamily residential on commercial corridors statewide with prevailing-wage requirements. Effective July 1 2023.
- **AB 130 (California, 2025)** [270, 285]. Budget trailer bill exempting most infill urban housing from CEQA entirely.
- **CEQA (California Environmental Quality Act, 1970)** [141, 142, 282, 283, 284]. State-level environmental review law; separate from federal NEPA. Requires initial study, negative declaration, or EIR depending on impacts. Litigation under CEQA is a recurring source of delay.
- **HB 267 (Florida, 2024)** [56]. 30-day mandatory permit processing for small single-family, duplex, triplex and quadplex structures under 7,500 square feet.
- **HB 2001 (Oregon, 2019)** [346]. First statewide middle-housing law; preempts single-family-only zoning in cities above a population threshold.
- **Minneapolis 2040 Comprehensive Plan (2019)** [343, 344, 345]. First US city to eliminate single-family-only zoning city-wide.
- **NYC ULURP (1975 Charter)** [133, 134]. Six-phase public review process for zoning changes and discretionary land-use actions. 205-day statutory maximum.
- **NYC 421-a Tax Exemption / Affordable New York (1971, expired 2022)** [213, 286–290]. Long-standing property-tax incentive tied to affordable-housing construction. Replaced by 485-x in 2024.
- **NYC Zoning Resolution (1961, ongoing amendments)**. Primary zoning text for NYC.
- **Member Deference / Aldermanic Privilege**. Informal custom, not codified, in which individual council members can effectively veto projects in their district [65, 66, 193, 194]. Operates in NYC and Chicago and several other cities.
- **Inclusionary Zoning / IZ programs** [202, 203]. Require set-asides of affordable units in return for density bonuses. Frequent source of additional review and compliance time.
- **WABO Act (Netherlands)**. Statutory 8-week default decision window for building permits. Relevant because the BPIC 2015 dataset [102, 103] measures compliance with this target.

## 5. Embodied Delays and Throughput-Time Formulas

**Total throughput time as a sum of stage times.** In the simplest model:

    T_total = Σ_i (T_wait,i + T_service,i) + T_rework

where the sum is over stages and T_rework captures repeat reviews. For a system with N independent sequential stages where each stage has its own M/M/1 queue:

    E[T_i] = 1/(μ_i - λ_i) = (1/μ_i) / (1 - ρ_i)

and expected total time is the sum across stages, which is badly non-linear in ρ_i near 1. The non-linearity is the central operations insight for understanding permit delay: doubling arrivals at a reviewer whose utilisation is already 90% increases wait time roughly 10-fold, not 2-fold.

**With rework.** If each plan-check cycle has probability *p* of needing another cycle and expected length *τ*, the total plan-check time is geometrically distributed with mean:

    E[T_pc] = τ / (1 - p)

For τ = 10 business days and p = 0.5, the mean plan-check stage time is about 20 business days, and the 99th percentile is much larger. Most US cities report average plan-check cycles in the 2-4 range for typical projects [338], which implies p in the 0.5-0.75 range for a geometric model.

**Little's Law.** For the system as a whole:

    L = λ W

where L is mean number in system, λ is arrival rate, and W is mean time in system. Used to estimate backlog from time and vice versa [116, 117].

**Kendall notation.** A/B/c/K/N/D where A = arrival process, B = service distribution, c = number of servers, K = system capacity, N = population, D = discipline. Most permit systems are best approximated as G/G/c/∞/∞/FCFS: general arrivals, general service, multiple reviewers, unbounded capacity, First-Come-First-Served queue (though some reviewers prioritise).

**Cox proportional hazards.** The hazard h(t|x) = h_0(t) exp(β^T x) [118]. Used to estimate hazard ratios for covariates like project size, neighbourhood, application year, reviewer identity.

**Accelerated failure time.** log(T) = β^T x + σε [120, 249, 250]. Directly parameterises the log-duration as a linear function of covariates. Provides interpretable time-ratio coefficients: a coefficient of -0.5 on a covariate means cases with that covariate experience a median time ~61% of those without.

## 6. Failure Modes: Most-Cited Reasons Permits Get Stuck

Order roughly by frequency-of-citation in the literature and practitioner writing:

1. **Incomplete application / missing drawings.** First-round rejection for incompleteness is the most common single cause of delay. Chicago's rejection rate for zoning licenses due to insufficient information was reported at 17% [43]. Fast-track programs typically mandate pre-screening to reduce this.
2. **Plan-check correction cycles.** Each cycle adds reviewer time (5-15 business days) plus applicant turnaround (variable, often longer than the review itself). Process-mining analyses of BPIC 2015 [107] identified correction loops as the single biggest controllable factor in Dutch municipal throughput times.
3. **Jurisdictional hand-offs.** The transition between planning and building, or between building and MEP, or between MEP and fire, is a queue. Hand-offs are where cases wait longest because neither the sending nor receiving organisation is actively working on them.
4. **Third-party reviews.** Fire marshal, health department, historic preservation, coastal commission, school district, airport overlay, environmental consultants. Each is a separate queue. NMHC-NAHB [50] puts the aggregate third-party review cost at a meaningful share of the 40.6% regulatory total.
5. **Environmental challenges (CEQA, SEQRA, NEPA).** Not always litigation — often just the time spent preparing an initial study or EIR. Holland & Knight [141] shows formal CEQA litigation hit 80% infill projects in California. O'Neill et al. [34] show direct CEQA lawsuits are rare (7 of 254 projects) but CEQA-triggered review time affects many more.
6. **Discretionary review / conditional use / variance.** Projects not entitled by right must undergo additional hearings and public comment. In SF this is the discretionary review (DR) process [30, 281], legally optional but routinely requested by neighbours.
7. **Member deference / aldermanic privilege.** A single council member or alderman stalling or refusing a project in their district [65, 66, 193, 194]. A legally informal but empirically dominant veto point in NYC and Chicago.
8. **Planner turnover and workload spikes.** When a reviewer leaves or is reassigned, the case goes back to the queue. Seasonal workload spikes produce the same effect at system level.
9. **Reviewer backlog / understaffing.** Classical queueing: when ρ = λ/(cμ) is near 1, all cases experience large waiting times. Budget cuts are a primary driver.
10. **Inter-agency communication failures.** Stage 3 asks Stage 2 a question; Stage 2's answer never reaches Stage 3; nobody follows up. Process-mining discovery [87, 95] typically finds these.
11. **NIMBY opposition at formal hearings.** Einstein, Glick and Palmer [169] documented empirically the demographic skew of planning-meeting attendees and that opposition dominates support. Hankinson [39, 219] shows even renters oppose local development.
12. **Fee disputes and impact fees.** Impact fees averaged roughly $20,000 per LIHTC unit in California 2020-2023 [179]. Fee calculation disputes can stall projects at the permit-issuance stage.
13. **Software and IT failures.** NYC's transition from BIS to DOB NOW [76, 190] introduced a new set of IT-mediated failure modes. Multiple applicants reported being unable to submit revised drawings, having lost file histories, or being routed to non-existent reviewers.
14. **Legal challenges beyond CEQA.** Housing Accountability Act litigation [31], state-federal preemption conflicts, historic preservation disputes.

## 7. Glossary

- **ADU (Accessory Dwelling Unit).** A secondary small residential unit on a single-family lot. Legalised progressively across US cities; California ADUs have been by-right since 2017.
- **AFT (Accelerated Failure Time).** Survival-analysis model where log-duration is a linear function of covariates [120].
- **Alpha miner.** First process-discovery algorithm [91].
- **BIM (Building Information Model).** 3D-plus-metadata digital representation of a building. BIM-based process mining [232] extends standard process mining to construction.
- **BPIC / BPI Challenge.** Annual process-mining dataset challenge [106, 240]. BPIC 2015 is the Dutch municipal building-permit dataset [102, 103, 107].
- **BPS (Building Permits Survey).** US Census monthly survey of permit-issuing places [71, 72, 73, 301–308].
- **BSA (Board of Standards and Appeals, NYC).** Quasi-judicial body hearing variances and special permits.
- **CEQA.** California Environmental Quality Act [141, 142].
- **Cox PH.** Cox Proportional Hazards model [118].
- **Correction cycle / round.** One iteration of a plan reviewer's comments returned to the applicant, the applicant's response, and the reviewer's re-check.
- **DBI.** San Francisco Department of Building Inspection.
- **DOB.** Department of Buildings (most US cities).
- **DOB NOW.** NYC's electronic permit system replacing BIS [74, 75, 76, 190].
- **EIR.** Environmental Impact Report (California). Largest form of CEQA review.
- **Entitlement.** The legal permission to build, distinct from the building permit. Entitlement is typically a planning-department output; building permit is a DOB output.
- **ePlanLA / PermitLA.** LA's electronic permit platforms [181, 295, 296].
- **Event log.** In process mining [87, 102], a table of (case_id, activity, timestamp) triples.
- **FAR (Floor Area Ratio).** Ratio of total building floor area to lot area. Basic zoning-regulation unit.
- **Heuristics miner.** Noise-tolerant process-discovery algorithm [92, 93, 94].
- **HOME (Home Options for Middle-income Empowerment, Austin).** Austin 2023-2024 zoning reform [62, 63, 64, 186].
- **Hazard function.** The instantaneous rate at which events occur given survival to time t [118, 119].
- **Inductive miner.** Process-discovery algorithm with formal soundness guarantees [95, 96].
- **IZ (Inclusionary Zoning).** Requirement to set aside a percentage of units at affordable rents/prices.
- **Kendall notation.** Shorthand for queueing systems (e.g. M/M/1, M/M/c, G/G/1).
- **Little's Law.** L = λW [116, 117].
- **LADBS.** Los Angeles Department of Building and Safety [81, 181].
- **MEP.** Mechanical, Electrical, Plumbing reviews (often separate from the main building review).
- **M/M/c.** Markovian arrivals, Markovian service, c servers. Standard textbook multi-server queueing model.
- **NEPA.** National Environmental Policy Act (federal).
- **NIMBY.** Not In My Backyard. Locally-opposed new development.
- **NMHC.** National Multifamily Housing Council [50, 214, 215].
- **NAHB.** National Association of Home Builders [50, 215].
- **Objective standard.** Statutory language in SB 35/SB 423 for standards that do not involve subjective discretion and cannot be used to deny streamlined projects.
- **Process mining.** The discipline of discovering process models, checking conformance, and analysing performance from event logs [87, 110, 111, 238].
- **Process tree.** Block-structured output format of the inductive miner [95].
- **RHNA.** Regional Housing Needs Allocation (California). State-mandated production targets by jurisdiction.
- **RFI (Request For Information).** Formal reviewer question to the applicant that halts review until answered.
- **RSF (Random Survival Forests).** Ensemble survival-analysis method [123].
- **SEQRA.** NY State Environmental Quality Review Act (state analogue of NEPA/CEQA).
- **SB 35 / SB 330 / SB 423.** California streamlining statutes.
- **Traffic intensity (ρ).** ρ = λ/(cμ). Ratio of arrival rate to aggregate service capacity.
- **ULURP.** Uniform Land Use Review Procedure (NYC) [133, 134].
- **WABO.** Dutch General Environmental Law setting 8-week building permit decision window.
- **WRLURI.** Wharton Residential Land Use Regulatory Index [2, 3].
- **Zoning tax.** The implicit tax on development from restrictive land-use regulation [4, 5, 161].

## 8. Data Sources and Their Quirks

Monthly MSA-level aggregates (Census BPS) [71–73, 301–308] are the standard housing-economics dataset but cannot be used for pipeline decomposition because they have no per-permit timestamp.

Per-permit event data is published by individual cities:

- **NYC DOB NOW** [74, 75] exposes application-level timestamps including decision and issuance dates. Does not always expose intermediate stage events.
- **San Francisco DBI + Planning** [78, 79, 291–293] exposes permit histories from 1980s forward.
- **Austin** [77] publishes issued construction permits with application and issuance dates.
- **LA LADBS** [81] lookup portal.
- **Chicago** [80, 298, 299, 309] permit dataset.
- **Boston / Seattle / Portland / Philadelphia / Denver / Minneapolis / DC** all publish similar tables [310–316].

The BPI Challenge 2015 Dutch municipal data [102, 103] is the only widely-studied multi-city permit event log in the literature; it has the advantage of including intermediate stages at fine granularity. BPIC 2018 and 2020 [104, 105] cover non-permit cases but use the same format.

Variable naming across cities is inconsistent: SF's "Filed Date" is not the same as Austin's "Application Date" which is not the same as NYC's "Filing Date". Harmonisation is a non-trivial prerequisite for any cross-city analysis [83, 348].

## 9. Quick Reference: Survival Analysis Models for Permit Duration

| Method | Key assumption | Handles censoring | Interpretability | Paper |
|---|---|---|---|---|
| Kaplan-Meier | None (non-parametric) | Yes | High (survival curve) | [119] |
| Cox PH | Proportional hazards | Yes | High (hazard ratios) | [118] |
| AFT (Weibull, log-normal) | Parametric log-linear | Yes | High (time ratios) | [120, 122] |
| Random Survival Forests | None | Yes | Low (feature importance only) | [123] |
| XGBoost AFT | Parametric AFT loss | Yes | Medium (SHAP + feature importance) | [127] |
| DeepHit | None | Yes with competing risks | Low | [124] |
| Deep Survival Machines | Parametric mixture | Yes | Medium | [126] |

For a permit-duration project the recommended stack is (a) Kaplan-Meier for baseline visualisation, (b) Cox PH for the primary causal interpretation, (c) XGBoost AFT for best point-prediction with reasonable explainability, and (d) Random Survival Forests or DeepHit for non-linear validation. Scikit-survival [128] and lifelines [129] are the standard Python libraries.

## 10. Quick Reference: Process Mining Models for Permit Event Logs

| Algorithm | Strengths | Weaknesses | Paper |
|---|---|---|---|
| Alpha miner | Simple, formal | Can't handle noise, duplicates | [91] |
| Heuristics miner / FHM | Noise-tolerant | Can produce unsound models | [93, 94] |
| Inductive miner | Sound block-structured output | Less expressive | [95, 96] |
| Inductive miner infrequent | Sound + noise-tolerant | Requires frequency threshold | [96] |
| Evolutionary Tree Miner | Steerable quality tradeoffs | Slow | [97] |

For a building-permit project, **inductive miner infrequent** is the default first pass because it guarantees soundness and tolerates real-world log noise. The ProM toolkit [326], pm4py Python library [328], and bupaR R ecosystem [327] all provide mature implementations.

## 11. Minimum Dataset Columns for a Permit Pipeline HDR Project

At a minimum, for each case (permit application) the project needs:

- `case_id`: unique permit application identifier
- `city`: jurisdiction
- `application_type`: e.g. residential new, residential addition, commercial new, duplex, tenant improvement
- `filed_date`: submission timestamp (primary intake event)
- `issued_date`: permit issuance timestamp (primary terminating event)
- `withdrawn_date` / `denied_date`: non-issuance outcome timestamps (for competing risks)
- `sqft` or similar project size
- `estimated_cost`: valuation
- `neighbourhood` or zip
- `stage_events`: ordered list of (activity, timestamp) pairs for plan check, corrections, MEP, fire, etc.
- `round_count`: number of plan-check correction cycles
- `zoning_designation`: zoning at filing
- `streamlined_track`: flag for SB 35, SB 423, expedited, etc.

With this minimum set, the project can compute: (a) total cycle time per permit, (b) right-censored survival analysis, (c) a discovered process model per city, (d) stage-level duration distributions, (e) cross-city harmonised comparisons, and (f) pre/post-reform difference-in-differences.
