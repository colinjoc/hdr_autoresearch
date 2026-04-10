# REFRESH-1 Report

**Date**: 2026-04-10
**Trigger**: 5 projects complete (O-4, W-5, T-1, EU-1, IE-1)
**Pool before refresh**: 140 candidates across 9 clusters

---

## Summary

- **New candidates added**: 16
- **Existing candidates re-scored**: 3
- **Updated pool total**: 156
- **Queue displacement recommendation**: Yes -- 2 new candidates should enter P6-P10 consideration

---

## 1. New candidates (16)

### Why these and not others

The search focused on:
1. Events that occurred after the original pool was generated (Apr 2025 -- Apr 2026)
2. New datasets released 2025-2026 that weren't previously available
3. EU/Ireland emphasis per user preference
4. Gaps in existing pool (water infrastructure, supply chain, citizen-science flood warning, PFAS, data centres)

### New candidates by cluster

| ID | Score | Question | Cluster | Key rationale |
|---|---|---|---|---|
| EU-19 | 30 | Valencia DANA flash flood: why did personal weather stations see it hours before the official network -- can citizen-science PWS networks close the flash-flood warning gap? | EU | 223 dead Oct 2024; HESS Copernicus 2025 paper with 225 PWSs at 7x AEMET density; Sentinel + AEMET + PWS data all open |
| EU-20 | 29 | Which European grid states are one frequency oscillation from a blackout after Iberian 2025 -- predict 0.2 Hz inter-area mode instability from ENTSO-E open data? | EU | ENTSO-E March 2026 final report identifies 0.63 Hz + 0.2 Hz oscillatory instability; ENTSO-E Transparency Platform + PyPSA-Eur open |
| EU-21 | 29 | Predict Mediterranean reservoir drought-to-crisis tipping point -- what rainfall deficit tips irrigated agriculture into collapse (Axarquia avocado crash, Po Valley, Sicily)? | EU | PNAS 2025 Axarquia paper; JRC EDO open data; Spain reservoir at 57.2% Jan 2026 after crisis; EDO API open |
| EU-22 | 29 | Which EU drinking water supplies will exceed new PFAS limits -- predict exceedances from land use + industrial history before Jan 2026 monitoring arrives? | EU | EU Drinking Water Directive PFAS monitoring mandatory from 12 Jan 2026; EEA Waterbase PFOS maps 2018-2022; 51-60% rivers exceed EQS; Forever Pollution Project map open |
| EU-23 | 28 | Why does Deutsche Bahn long-distance punctuality collapse some weeks and not others -- predict delay cascades from the open Bahn-Vorhersage archive? | EU | 59.4% punctuality Feb 2026; EUR 156M compensation in 2025; Bahn-Vorhersage CC-BY-4.0 dataset since Sep 2021 (~700 GB); mechanism (infrastructure works vs weather vs cascading) unresolved |
| EU-24 | 28 | Predict wildfire propagation speed from the new FireSpread_MedEU 3m-resolution dataset -- what landscape feature makes a fire explode vs creep? | EU | Sci Data (Nature) 2026; 320 burned area maps, 103 fires, ~3m spatial, daily temporal; 2025 was EU's most destructive wildfire season (JRC March 2026) |
| EU-25 | 28 | Where will renewable curtailment spike next in Europe -- predict from grid topology + weather + demand before 11% of green energy is wasted? | EU | 11% curtailment in Spain summer 2025; EUR 7.2B lost across 7 countries in 2024; ENTSO-E Transparency + ERA5 + EFFIS open |
| IE-18 | 29 | Predict which Irish water supply will issue the next boil-water notice -- pipe age, treatment type, or rainfall as trigger? | IE | 62,645 people on >30-day BWN in 2023 (up from 24k in 2022); Uisce Eireann fined EUR 20M in 2025; EPA water quality data + Met Eireann + Uisce Eireann annual report open |
| IE-19 | 29 | Will Ireland's data centres crash the grid this winter -- predict hour-ahead system adequacy margin from EirGrid open dashboard? | IE | Data centres = 21% of national electricity, projected 32% by 2026; record 6,024 MW peak Jan 2025; EirGrid Smart Grid Dashboard real-time open data; CRU Dec 2025 new policy |
| IE-20 | 28 | Where in Ireland's planning pipeline does housing permission die -- An Coimisiun Pleanala bottleneck vs judicial review vs utility connection? | IE | Planning permissions down 38% Q4 2024; apartment permits -52%; 147 judicial reviews in 2025 (up from 15/yr a decade ago); An Coimisiun Pleanala launched Jun 2025; new completions 75% drop |
| IE-21 | 28 | Which Irish road segment will kill a cyclist or pedestrian next -- predict from infrastructure, speed, and exposure? | IE | 190 road deaths in 2025 (highest since 2014); cyclist deaths doubled 2022-2025; RSA May 2025 + Oct 2025 reports; RSA crash data + OSM + NTA open |
| W-16 | 29 | Predict DANA-type Mediterranean flash floods 6+ hours ahead -- which cut-off low configurations actually produce 300mm/4h extremes? | W | Valencia Oct 2024 (223 dead, 1000-yr return); Copernicus HESS 2025; EGUsphere 2025; ERA5 + AEMET + EFAS open |
| W-17 | 28 | Predict European heat wave excess deaths city-by-city in real-time -- which city characteristics amplify the 16,500 climate-attributable summer 2025 toll? | W | 16,500 excess deaths summer 2025 (WWA attribution); Rome/Athens/Bucharest worst; ERA5 + Eurostat mortality + UrbClim open |
| T-19 | 28 | When will Red Sea shipping disruption tip a European port into congestion -- predict container dwell from AIS + diversion status? | T | Cape of Good Hope rerouting absorbed 9% global capacity; Europe transit +33%; MarineCadastre AIS + Port of Rotterdam open dashboard |
| Q-17 | 29 | Predict where EU combined sewer overflows contaminate bathing water after storms -- which CSO + catchment features produce pathogen spikes? | Q | Revised EU Urban Wastewater Directive Jan 2025; England EDM ~15,000 monitors open; Barcelona early-warning pilot; new RSC 2026 paper linking EDM to discharge consents |
| E-17 | 28 | Predict which EU buildings will miss the 2030 EPBD renovation trajectory -- from EPC databases, which worst-performers are unreachable? | E | Revised EPBD transposition deadline May 2026; 16% worst non-residential by 2030; national EPC databases becoming open; 4.8M UK EPCs already open |

---

## 2. Re-scored existing candidates

| ID | Old score | New score | Reason |
|---|---|---|---|
| EU-6 | 29 | 30 | 2025 was EU's most destructive wildfire season on record (JRC March 2026); EFFIS 1.08M ha confirmed; new FireSpread_MedEU dataset (Sci Data 2026) provides 3m-resolution propagation data that didn't exist at pool generation. Mechanism payoff and data availability both increase. |
| IE-9 | 27 | 29 | Storm Eowyn Jan 2025 was Ireland's worst storm since 1961: 768k customers lost power, 3,000 poles replaced, 900km cable relaid. ESB PowerCheck data confirmed open. Relatability and story-tellability both jump -- every Irish adult experienced this. |
| EU-12 | 28 | 29 | England EDM data for 2024 released March 2025 now covers ~15,000 monitors with full spill duration data. New RSC 2026 paper explicitly links EDM to discharge consents. Data availability increases from 4 to 5. |

---

## 3. Updated cluster counts

| Cluster | Before refresh | New additions | After refresh |
|---|---|---|---|
| T - Transportation | 18 | 1 (T-19) | 19 |
| E - Energy & built environment | 16 | 1 (E-17) | 17 |
| Q - Environmental quality | 14 | 1 (Q-17) | 15 |
| W - Weather & disasters | 15 | 2 (W-16, W-17) | 17 |
| A - Agriculture & ecology | 20 | 0 | 20 |
| O - Economics & operations | 13 | 0 | 13 |
| P - Wildcard physical sciences | 10 | 0 | 10 |
| IE - Ireland | 17 | 4 (IE-18 to IE-21) | 21 |
| EU - Europe-wide | 17 | 7 (EU-19 to EU-25) | 24 |
| **Total** | **140** | **16** | **156** |

---

## 4. Queue displacement recommendations

The active queue P6-P10 is currently:
- P6: IE-2 (29) Irish radon prediction
- P7: EU-3 (29) Xylella olive groves
- P8: IE-3 (29) DART punctuality cascade
- P9: EU-6 (29 -> 30) Iberian wildfire transition
- P10: T-3 (29) Flight delay propagation

### Recommended changes

1. **EU-6 re-scored to 30** -- should move up in priority within the queue. Its data availability improved substantially with FireSpread_MedEU.

2. **EU-19 (30) Valencia DANA citizen-science flash flood warning** -- scores 30/30 and should enter the active queue. It is the single most newsworthy event in Europe since the pool was generated (223 deaths), has a clear HDR angle (baseline = official AEMET network; question = does adding 225 citizen PWSs at 5-min resolution close the warning gap?), and all data is open. **Recommend inserting at P6 or P7.**

3. **IE-18 (29) Irish boil-water notice prediction** and **IE-19 (29) Irish data centre grid adequacy** -- both score 29 and are highly topical (EUR 20M fine, record grid peak). Either could replace a current P6-P10 entry of equal score if the user wants more Irish content in the near-term queue.

4. **IE-9 re-scored to 29** (Storm Eowyn outage prediction) -- now ties with other P6-P10 entries and could be considered for the queue.

### No displacement recommended for

- Agriculture cluster (A): no major new events or datasets since pool generation
- Operations cluster (O): no new open questions emerged
- Wildcard physical sciences (P): no new datasets

---

## 5. Gaps still under-represented

- **Water infrastructure** (now partially addressed by IE-18, Q-17): still no candidate for continental European drinking water pipe failure prediction. Could be added at REFRESH-2 if Uisce Eireann or a continental utility opens pipe-age data.
- **Maritime/port logistics** (partially addressed by T-19): Red Sea disruption is evolving; if ceasefire stabilises, the natural experiment ends and the candidate weakens.
- **Autonomous vehicles**: Waymo Open Dataset is excellent but the topic sits in a policy-contested zone. Excluded for now but monitor.
- **Microplastics**: pan-European river data emerging (Frontiers 2026 Danube paper) but no single open dataset with enough sites for ML yet. Monitor for REFRESH-2.

---

## 6. Search methodology

Web searches conducted across:
- arXiv, SSRN, Nature Scientific Data, Copernicus journals (HESS, ESSD, EGUsphere)
- ENTSO-E, EFFIS/JRC, EEA, Copernicus CDS
- data.gov.ie, EPA.ie, SEAI, Uisce Eireann, EirGrid
- News sources (Irish Times, Euronews, RTE, Guardian, Yale Climate Connections)
- Government/regulatory publications (CRU, RSA, AEMET, FHWA NBI, DWD)
- GitHub open dataset repositories (Bahn-Vorhersage, piebro/deutsche-bahn-data)

All 16 new candidates verified against the rubric dimensions with specific open data sources confirmed.
