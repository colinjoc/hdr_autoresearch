# HDR Approachable-Showcase Pipeline

**Generated**: 2026-04-09
**Total candidates**: 171 (140 original + 16 from REFRESH-1 + 15 from REFRESH-2)
**Selection criteria**: see "Rubric" below
**Companion file**: `active_queue.md` tracks the in-flight top 15

---

## Purpose

This is the canonical pool for the HDR "approachable showcase" track — projects whose goal is to demonstrate the methodology's range on questions that ordinary people understand and care about. Distinct from `project_candidates.md` (the ambitious physics tier: superconductors, fusion, QEC, gravitational waves) and `approachable_projects.md` (the older 2026-04-02 catalog of 120 generic ML benchmarks). This pool is built for newsworthy showcase projects with universal relatability.

The reference gold standard is the SUMO traffic-light waiting-time project: universally relatable, real open question, mechanism-revealing.

## Rubric

The 8-dim score below is the **input** to ranking, not the output. After scoring, every candidate that clears the bar is re-ranked by **Drake-decomposed PriorImpact** per `program.md` "Phase −0.5 §7" and `applications/meta_analysis.md`:

> `PriorImpact = Pr(reach Phase 3) × Pr(non-null | reach Phase 3) × audience_size × novelty_factor / engineer_weeks`

with the first two factors taken from the empirical conversion-rate prior in `meta_analysis.md` (do NOT estimate from scratch). The 8-dim rubric below screens *fit*; the Drake decomposition ranks *expected impact distribution*. Final execution order: sort surviving candidates by P25(PriorImpact), then by P50 for ties — risk-averse ordering, matches the Astro2020 community-consensus heuristic (gives reviewers cover against P50-optimistic projects that don't survive).

Every candidate scores 1–5 on **eight** dimensions; bar = every dimension ≥3 AND total ≥32/40 (proportional to the prior 24/30 bar):

| Dim | 1 | 5 |
|---|---|---|
| **R** Relatability | needs glossary | universal experience |
| **I** Personal impact | 0.1% niche | most adults weekly |
| **N** Open-question novelty | textbook | unresolved active 2024–2026 |
| **M** Mechanism payoff | just a number | causal "because" |
| **D** Data/sim availability | need new equipment | public dataset/sim with URL |
| **S** Story-tellability | trade journal | front-page Reddit / The Guardian / Le Monde |
| **E** Anglosphere relevancy | local to non-Anglosphere region only | directly topical in all of US, IE, UK, AU (English-language press cycle) |
| **G** Civic grievance / live public argument | no one is arguing about it; technical curiosity only | actively on the Oireachtas / Westminster / Congress floor, in letters to editors, with named institutional voices disagreeing |

**Note on Anglosphere relevancy (E)**. Added 2026-04-15 after the irish-fuel-profiteering off-queue project demonstrated that audience-aligned framing materially lifts engagement on the website portfolio. The portfolio's reader base skews Anglo-North-Atlantic; projects that resonate with US/IE/UK/AU readers compound the methodology-showcase value. Score 5 = the question is being actively asked in English-language press in at least three of {US, IE, UK, AU}; score 1 = geographically local to a non-Anglosphere region with no English-press resonance.

**Note on Civic Grievance (G)**. Added 2026-04-15 after the DART-punctuality and Irish-fuel-profiteering projects resonated with general-audience readers in a way most technical-curiosity projects had not. The common thread: both were **"is the system cheating me?"** questions with active institutional voices disagreeing. A project scoring high on G answers a question that regular people are already arguing about at dinner tables and in radio call-ins — not just one they'd find interesting if explained. Examples: DART reliability = 5 (stood-on-the-platform experience, CIÉ vs commuter complaints); Irish fuel profiteering 2022 = 5 (Taoiseach on moral reprehensibility vs Fuels for Ireland rebuttal); SSW polar vortex = 2 (no one is arguing about it publicly); SWIO cyclone RI = 3 (Madagascar/Mozambique deaths are real news, no live disagreement about cause). **Critical non-dilution rule**: G ≥ 3 alone does not admit a candidate. It must still clear N ≥ 3 (novel question) and M ≥ 3 (mechanism payoff). This keeps out pure-outrage stories with no interesting research question.

## Hard exclusions

- Personal health & lifestyle (sleep, diet, fitness, individual mental health, individual disease management). Public-health-at-policy-level is OK.
- Culture, media, music, video, sports, viral content
- Education (whole cluster removed at user request)
- Partisan political opinion
- Topics with US-style racial / minority framing (community-policy framing in Europe is allowed if it isn't identity politics)
- Topics where the data isn't actually open

## Cluster IDs

| Prefix | Cluster |
|---|---|
| T | Transportation & mobility |
| E | Energy & built environment |
| Q | Environmental quality, public-health-at-policy-level, road safety |
| W | Weather, climate hazards & natural disasters |
| A | Agriculture, ecology & biodiversity |
| O | Economics, urban operations & public services |
| P | Wildcard physical sciences with everyday hooks |
| IE | Ireland-specific |
| EU | Europe-wide (excluding Ireland) |

---

## Active queue (top 15)

See `active_queue.md` for live status.

| Order | ID | Score | Question | Cluster |
|---|---|---|---|---|
| 1 | O-4 | 30 | Where in the building-permit pipeline does the time go (Austin 48d vs SF 605+d) | O |
| 2 | W-5 | 30 | Predict heat-wave excess deaths — is night-time wet-bulb the missing variable | W |
| 3 | T-1 | 30 | Phantom highway traffic jams — can a few smart cars dissolve them | T |
| 4 | EU-1 | 29 | Iberian blackout cascade prediction — which grid states are one perturbation away | EU |
| 5 | IE-1 | 29 | Irish BER vs real home energy gap — which retrofit features actually save kWh | IE |
| 6 | IE-2 | 29 | Predict dangerous Irish radon homes before measurement | IE |
| 7 | EU-3 | 29 | Xylella prediction in Spanish/Italian olive groves 12 months ahead | EU |
| 8 | IE-3 | 29 | DART punctuality cascade prediction (92.8 → 64.5% in 4 months) | IE |
| 9 | EU-6 | 29 | Iberian wildfire "very large fire" transition predictor | EU |
| 10 | T-3 | 29 | Flight delay propagation through the network — what makes it contagious | T |
| 11 | IE-7 | 29 | Dublin/Cork NO2 source attribution under WHO 2021 limits | IE |
| 12 | T-9 | 29 | Did NYC congestion charge actually reduce traffic or push it to side streets | T |
| 13 | O-10 | 29 | Aircraft turnaround time mechanism (32 vs 71 min for same flight) | O |
| 14 | E-4 | 29 | Why 75% of Time-of-Use customers don't shift load when prices spike | E |
| 15 | EU-2 | 29 | Po Valley fog persistence + aerosol coupling | EU |

Refresh checkpoints: after P5, P10, P15.

---

## Full pool

### Transportation & mobility (T)

- **[T-1]** (30) Phantom highway traffic jams — can a handful of smart cars dissolve them? — *I-24 MOTION trajectory dataset + SUMO/Flow ring-road simulator* — Why open: arXiv 2509.09441 + 2504.11372 (2025) explicitly call suppression mechanism + minimum penetration rate open after MegaVanderTest.
- **[T-3]** (29) Flight delay propagation through the network — what makes one delay contagious vs contained? — *BTS On-Time Performance + OpenSky Network ADS-B + BlueSky open ATM simulator* — Why open: 2 separate 2025 review papers (Wiley ATR + Springer LLM) flag propagation mechanism as unresolved.
- **[T-4]** (29) What tips a packed crowd into a crush — precursor signal seconds before? — *Lyon Festival of Lights 2025 trajectory dataset + Jülich pedestrian experiments + PedSim/Menge* — Why open: arXiv 2505.05826 + Sci Data 2025 paper on Lyon FoL.
- **[T-5]** (29) Why nighttime pedestrian deaths exploded — headlight, SUV shape, darkness, or speed? — *NHTSA FARS + IIHS Headlight Ratings + CARLA simulator* — Why open: AAA Foundation 2024 + IIHS Oct 2025 reversal on glare assumption.
- **[T-7]** (29) Why bus ridership came back post-COVID but commuter rail didn't? — *NTD + APTA + agency fare-card releases (BART, Metra, MBTA, LIRR)* — Why open: GAO-25-107511 (2025).
- **[T-9]** (29) Did NYC congestion charge actually reduce traffic, or just push cars to side streets? — *NYC DOT counts + MTA B&T + TLC trip records + Streetlight* — Why open: NBER WP 33584 (2025) + npj Clean Air 2025; data only since Jan 2025.
- **[T-2]** (28) Why two scheduled buses always show up together — bus bunching prediction — *MTA Bus Time + TfL iBus + OneBusAway feeds + BusSim/SUMO transit* — Why open: 2024 Transport Reviews comprehensive review (10.1080/01441647.2024.2313969).
- **[T-6]** (28) Why "induced demand" makes new lanes fail to reduce congestion — and how fast does it kick in? — *FHWA HPMS + Caltrans PeMS + MATSim activity-based simulator* — Why open: UCLA Manville 2024 + CARB 2025 brief; elasticity 0.2 to >1.0.
- **[T-8]** (28) Container ship congestion at LA/LB — what tips a port from busy to congested? — *MarineCadastre AIS + World Bank CPPI + SimPy port sims* — Why open: Frontiers 2025 + Tandfonline 2025; LA dwell still 5.7 days.
- **[T-10]** (28) Why delivery drivers waste so much time in the "last 50 feet"? — *Amazon Last Mile Routing Challenge + Urban Freight Lab Seattle Final 50 Feet* — Why open: MDPI Sustainability 2025 + Urban Freight Lab.
- **[T-11]** (28) When does a bike lane crash rate spike instead of dropping? — *CYCLANDS (1.6M crashes) + CycleCrash WACV 2025 video dataset + OSM* — Why open: 2024 Transport Reviews scoping review.
- **[T-12]** (26) Predict next-departure delay from touchdown — what breaks a turnaround? — *BTS On-Time + airport gate logs + Eurocontrol DDR2 + BlueSky* — Why open: ScienceDirect 2025 review on airport gate ML.
- **[T-13]** (24) Truck parking shortage — temporal mismatch or something deeper? — *ATRI GPS + FHWA Jason's Law + SUMO freight* — Why open: FMCSA 2025 driver survey + Geotab study.
- **[T-14]** (27) When does an e-scooter trip replace a car vs add a new trip? — *Ride Report Global Dashboard + city scooter datasets (Louisville, Austin, Minneapolis, Chicago)* — Why open: ITS JPO May 2025 Executive Briefing.
- **[T-15]** (27) Curb-space allocation rule for delivery + rideshare + parking — *Open Mobility Foundation Curb Data Specification + Boston Curb Lab + SUMO curb-microsim* — Why open: Transportation Science 2024 (Lim & Masoud).
- **[T-16]** (27) Which work-zone layout feature is the real crash killer (taper, lane shift, speed drop, cone spacing)? — *FARS + FMCSA MCMIS + Tennessee work-zone dataset + SUMO/VISSIM* — Why open: MDPI 2025 + Accident Analysis & Prevention 2024.
- **[T-17]** (26) Ride-hail "deadheading" — what dispatch rule cuts empty driving? — *NYC TLC trip records + Chicago TNP + Didi Chuxing GAIA + CPUC Waymo + MATSim DRT* — Why open: 2025 Transportation paper on deadheading; Waymo still 44% deadhead Sept 2025.
- **[T-18]** (25) EV charger wait time prediction — connectors, grid, or dwell as bottleneck? — *DOE AFDC + ACN-Data Caltech + PlugShare/OpenChargeMap APIs* — Why open: Sci Reports 2025 + multiple 2025 forecasting papers.

### Energy & built environment (E)

- **[E-1]** (29) Why does the same heat pump work in one neighbor's house and not the next? — *HEAPO Swiss open dataset (1,408 households) + Nature Comms 2025 17%-fail dataset + HeatpumpMonitor.org UK + BfEE Germany* — Why open: arXiv 2503.16993 + Nature Comms 2025 (s41467-025-58014-y); 17% of air-source units fail efficiency standards. Note: this absorbs the Europe agent's EU-7 candidate which used the same data.
- **[E-4]** (29) Why do ¾ of households on Time-of-Use rates not shift load when prices spike? — *Pecan Street Dataport + OpenEI Demand Response* — Why open: Utility Dive 2025 + Arcturus survey of 400+ ToU programs.
- **[E-3]** (28) Why two "identical" code-built homes use wildly different energy? — *UK ONS Energy Efficiency dataset (4.8M EPC records, 2024) + Building Data Genome Project 2* — Why open: 2024-25 Building Research & Information papers; "performance gap" / "prebound/rebound" actively debated.
- **[E-2]** (28) Why so many EV fast chargers don't work — predict next failure? — *ChargerHelp/Paren reliability tables + DOE AFDC + ACN-Data* — Why open: Paren 2024-25 data shows ~84% true uptime vs 95–98% self-reported; ~50% of DCFC saw outage in H2 2023.
- **[E-6]** (28) Predict where and when the next big storm power outage will hit? — *EAGLE-I 2014–2024 county-level outage data + NWS weather + DOE-417* — Why open: arXiv 2512.22699 (2025); current models miss ~40% of severe outages.
- **[E-7]** (28) Why two neighbors' EVs degrade at different rates for the same miles? — *Geotab 22,700-vehicle public + Nature Comms 2025 multi-modal SOH dataset + Stanford-Toyota fast-charging* — Why open: variance > mean; intrinsic vs usage debated.
- **[E-10]** (28) Why does one street feel 5°C hotter than the next in a heat wave? — *FAIRUrbTemp dataset (811 sensors, Sci Data 2026) + Landsat + Sentinel-2 + OSM + ERA5-Land* — Why open: dataset built precisely because street-scale UHI variation is poorly characterized.
- **[E-8]** (27) Why identical wind turbines produce different power, and 40-km cluster wakes — *OpenWindSCADA (89 turbine-years, Zenodo 14006163) + PyWake/FLORIS open wake simulators* — Why open: WES (Copernicus) 2025 + arXiv 2408.15028; 30% larger losses than traditional estimates.
- **[E-5]** (27) Why solar farms underperform — modeler or weather to blame? — *NREL Solar Power Data + NREL PySAM + SolarAnywhere* — Why open: NREL 2025 "Open Data Sets for Assessing Photovoltaic System Reliability."
- **[E-9]** (26) Predict gas pipeline super-emitter leaks before they happen? — *Carbon Mapper + MethaneSAT + PHMSA NPMS pipeline data* — Why open: Johns Hopkins 2025 + ES&T 2024; top 10% emitters = 60-80% of total.
- **[E-11]** (26) Will the water main outside your house break this year? — *Kitchener open water main + breaks dataset + EPANET hydraulic simulator + NYC DEP / Tampa* — Why open: Tandfonline 2024 + Applied Water Science 2025; 30-50% of failures unexplained.
- **[E-12]** (26) Why do combined-sewer overflows happen on small storms but not bigger ones? — *arXiv 2408.11619 German CSS dataset + EPA SWMM* — Why open: 2024 paper + MDPI Water 2025.
- **[E-13]** (26) Why two visually identical buildings have 2× the embodied carbon footprint? — *Sci Data 2025 harmonized 292-project LCA dataset + EC3 EPD database* — Why open: NIST SP 1324 (2024) review.
- **[E-14]** (26) Why some office AC bills are 2× a similar building's? — *Building Data Genome Project 2 + EnergyPlus + Sinergym RL benchmark 2025* — Why open: ASHRAE GEPIII results plateau, 2024-25 digital twin papers report 8-16% savings still possible.
- **[E-16]** (26) Why "red flag day" power-line wildfires happen and others don't? — *CPUC public fire incident reports (PG&E + SCE + SDG&E) + PG&E PSPS + CAL FIRE FRAP* — Why open: UCR 2025 data-driven analysis + Berkeley Haas WP 347R.
- **[E-15]** (25) Rooftop solar underperformance — dirt, thermal, or mismatch? — *Public BAPV soiling datasets + PVlib python* — Why open: Sci Reports 2025 (s41598-025-25846-z); cleaning schedules poorly optimized.

### Environmental quality, public-health-at-policy-level, road safety (Q)

- **[Q-3]** (29) Which intersection will produce the next pedestrian/cyclist fatality? — *NYC Vision Zero crash data + NHTSA FARS + OSM + Strava Metro + SUMO countermeasure sim* — Why open: MDPI Infrastructures 2025 + Streetsblog Dec 2025.
- **[Q-1]** (29) Why does PM2.5 vary 5–10× across blocks just feet apart? — *EPA AirNow + PurpleAir API + Google Street View air sensor + TROPOMI NO2 + OpenAQ* — Why open: 2025 npj Clean Air + npj Climate & Atmos Sci.
- **[Q-2]** (29) Predict indoor PM2.5 in your house during wildfire smoke from house features alone? — *Paired PurpleAir sensors + NOAA HRRR-Smoke + EnergyPlus* — Why open: npj Clean Air 2025 (Eaton Fire) + ACS ES&T Air 2024.
- **[Q-5]** (29) Predict harmful algal blooms in small inland lakes 2 weeks ahead? — *Sentinel-2 MSI + EPA CyAN + USGS NWIS + NOAA HAB forecasts + CyFi DrivenData benchmark* — Why open: arXiv 2505.03808 (2025) + NASA/Microsoft CyFi competition.
- **[Q-6]** (29) Predict groundwater PFAS exceedance at the well from public records? — *USGS PFAS + EPA UCMR5 + EWG PFAS Map + EPA ECHO* — Why open: Tokranov et al., Science Oct 2024; 71-95M people potentially exposed.
- **[Q-7]** (29) Why same rainfall floods one street and not the next? — *EPA SWMM + NOAA Atlas-14 + USGS 3DEP 1m DEMs + NYC 311 + NLCD* — Why open: npj Natural Hazards 2026 + J Digital Earth 2025 review.
- **[Q-11]** (28) Why is ground-level ozone rising in some cities and falling in others despite NOx cuts? — *EPA AQS + TROPOMI HCHO/NO2 + CMAQ + NEI* — Why open: ACP 2025 + Nature Comms 2024.
- **[Q-9]** (27) Predict which blocks cross WHO night-noise from a windowsill sensor? — *SONYC-UST-V2 + NYC 311 noise + DOT counts + OSM* — Why open: SONYC project active through 2025; predictive forecasting almost absent.
- **[Q-10]** (27) Predict 48-hour drowning probability on a given beach? — *NOAA WaveWatch III + USLA stats + NWS rip catalog + Great Lakes Surf Rescue Project* — Why open: NOAA 2021 model is calibrated, not skill-discriminating; 2025 Tandfonline + ScienceDirect.
- **[Q-12]** (27) Predict where wildlife-vehicle collisions cluster during deer rut? — *State DOT crash data (MT, ID, CA, WY) + California Roadkill Observation System + iNaturalist + OSM + MODIS* — Why open: Oxford TSE 2024 + MDPI Sustainability 2025 review.
- **[Q-13]** (27) Which urban garden soils are safe to grow tomatoes from pre-garden records? — *Dryad global soil dataset (796k points, 2025) + Sanborn historical fire-insurance maps + USGS geochemistry* — Why open: Sci Reports 2024; soil-Pb model R² ~0.59.
- **[Q-14]** (27) Predict indoor radon from address alone, no measurement needed? — *PNAS 2024 national radon dataset + state radon DBs (PA, MN, MI, NC) + USGS geochemistry* — Why open: PNAS 2024 + ScienceDirect 2025 explainable AI.
- **[Q-15]** (26) Predict next disinfection-byproduct violations in small water systems? — *EPA SDWIS + USGS NWIS DOC + NLCD + PRISM* — Why open: ScienceDirect 2025 + EST 2025 roadmap.
- **[Q-16]** (26) Predict warehouse heat-illness injuries under heat domes? — *OSHA Severe Injury Reports + BLS QCEW + Microsoft Building Footprints + PRISM* — Why open: PMC 2025 + OSHA Heat NPRM hearings 2025.

### Weather, climate hazards & natural disasters (W)

- **[W-5]** (30) Predict which heat waves cause excess deaths vs just discomfort — is night-time wet-bulb the missing variable? — *ERA5 + CDC Wonder mortality + Eurostat + GHCN + HadISDH.extremes* — Why open: Nature Comms 2025/2026; 35°C wet-bulb threshold is wrong.
- **[W-1]** (29) Predict hurricane rapid intensification — which storms explode? — *IBTrACS + HURDAT2 + SHIPS + ERA5 + HAFS simulator* — Why open: NOAA CRS 2024; Google Melissa AI breakthrough 2025; RI is largest TC error source.
- **[W-2]** (29) Predict tornado outbreak severity days ahead — handful or 100+? — *NOAA SPC severe weather DB + GridRad-Severe + ERA5 + GEFS reforecasts* — Why open: NHESS 2026 (Copernicus) GEFS event set.
- **[W-4]** (29) Which atmospheric river will be catastrophic vs just refill reservoirs? — *Scripps CW3E AR catalog + ERA5 IVT + GEFS/ECMWF reforecasts + USGS streamflow* — Why open: npj Climate & Atmos Sci 2024; S2S AR skill at low level.
- **[W-6]** (29) Which streams will flash flood in next 6 hours given the rain forecast? — *MRMS QPE + USGS NWIS gauges + NWS Stage IV + GridMET + HydroSHEDS* — Why open: Nature npj Nat Haz 2025 P2M framework + ML4FF benchmark.
- **[W-7]** (29) Which homes will burn in a wildfire given ignition + weather? — *CAL FIRE DINS structure database + LANDFIRE + GRIDMET + Sentinel-2 + ELMFIRE/FARSITE* — Why open: Fire Technology June 2025 + 2025 Palisades/Eaton fires.
- **[W-12]** (29) Which polar vortex collapses actually deliver the cold blast and where? — *ERA5 stratospheric + NOAA CPC AO/NAO/SSW archive + GHCN-Daily + S2S reforecast* — Why open: March 2025 SSW anomaly; Nature Comms 2026 NAO paper.
- **[W-9]** (28) How many large aftershocks will follow this earthquake — and when does the sequence end? — *USGS ANSS ComCat + SCEDC + Japan JMA + EarthquakeNPP NeurIPS 2024 benchmark* — Why open: no neural point process beats ETAS yet.
- **[W-3]** (27) Will this thunderstorm complex become a 1000-km derecho? — *SPC + NCEI Storm Events + MRMS + HRRR + ERA5* — Why open: Squitieri et al. 2025 W&F; 72% of warm-season derechos low predictability.
- **[W-8]** (27) Will a flash drought start in this county within 4 weeks? — *NLDAS-2 + USDM + SPEI/EDDI gridMET + ERA5-Land* — Why open: Xu et al GRL 2024; ML captures only 33% of onsets at 7-day lead.
- **[W-10]** (27) Predict where lake-effect snow band will dump 3+ feet inland? — *MRMS QPE + NEXRAD + HRRR + GLERL lake temps + ERA5* — Why open: NWS + UAlbany OWLeS follow-up.
- **[W-11]** (27) Will this rainfall trigger a shallow landslide here? — *NASA Global Landslide Catalog + USGS landslide inventory + IMERG + SMAP soil moisture + Copernicus DEM* — Why open: Landslides journal Springer 2025.
- **[W-13]** (27) Will this storm produce baseball-sized hail or pea gravel? — *NOAA NCEI Storm Events + MRMS MESH + GridRad-Severe + NEXRAD dual-pol* — Why open: Frontiers 2025 4th European Hail Workshop; npj C&AS 2024.
- **[W-14]** (26) Predict microbursts more than 15 minutes ahead? — *NEXRAD Level II + MRMS + HRRR/WoFS + NCEI + ERA5 soundings* — Why open: NOAA WPO 2024; environment is predictable but timing/location not.
- **[W-15]** (26) Will this king-tide event close coastal roads? — *NOAA Tides and Currents + USGS coastal gauges + GFS waves + ERA5 winds + Digital Coast NOAA* — Why open: NOAA 2024 high-tide flood outlook; NOAA PSL 2025 weeks-ahead.

### Agriculture, ecology & biodiversity (A)

- **[A-1]** (29) Predict honey bee colony collapse from sensor + mite/virus data before keeper notices? — *Bee Informed Partnership + USDA NASS + HiveTracks/BroodMinder open archives* — Why open: Jan 2025 60% commercial colony loss; USDA ARS 2025 traced to amitraz-resistant Varroa; tipping point unsolved.
- **[A-2]** (29) What drives huge swings in monarch overwintering numbers? — *Journey North + Monarch Watch tagging + WWF Mexico + Project Monarch Health (OE) + iNaturalist milkweed + eBird* — Why open: Dec 2024 1.79 ha rebound; UGA 2024 vs Nature E&E 2021 contradict on dominant cause.
- **[A-3]** (28) Predict Lake Erie HAB severity weeks ahead from nutrients + weather? — *NOAA NCCOS Lake Erie HAB time series + Heidelberg Tributary Loading + MODIS/Sentinel-3 OLCI + GLERL* — Why open: 2024 SI 4.2 vs 2025 SI 2.4 swing surprised ensemble.
- **[A-4]** (28) Which native bees are actually declining, where and why? — *iNaturalist Research Grade + GBIF + USGS Bee Inventory + Xerces Bumble Bee Watch* — Why open: PNAS 2025; >20% North American pollinators at elevated risk but evidence limited.
- **[A-5]** (28) Predict bark beetle outbreak onset before defoliation? — *USFS Aerial Detection Survey + PRISM/gridMET + Landsat NDMI/NBR + USFS FIA* — Why open: Springer 2024 review; 85,000 sq mi killed since 2000.
- **[A-6]** (28) Why aerial insectivores (swallows, swifts, nightjars) are crashing fastest? — *USGS BBS 1966–2024 + eBird Status & Trends + MODIS LSP + Rothamsted insect biomass* — Why open: 2024 BBS report; house martin -44%.
- **[A-7]** (28) Predict which planted street trees die within 5 years? — *NYC Street Tree Census 1995/2005/2015 + OpenTreeMap + iTree + Google Street View virtual re-survey* — Why open: ISA 2024 review; single-cohort mortality 0.6%–68.5%.
- **[A-8]** (27) What caused the 2018-21 Bering Sea snow crab collapse — predict the next? — *NOAA RACE Groundfish + RAM Legacy Stock Assessment + ERSST + NOAA Coral Reef Watch MHW* — Why open: Science 2024; metabolic stress mechanism not in models.
- **[A-10]** (27) Why oak/beech masting synchronizes — predict mast year for acorns/Lyme — *MASTIF seed-trap network + USFS FIA + PRISM + ICP Forests* — Why open: Ecology Letters 2025 + PNAS 2025; cue weather variable disputed.
- **[A-11]** (27) Predict per-turbine bird/bat fatalities for smart curtailment — *AWWI/AWWIC + NEXRAD BirdCast + USGS bat acoustic network + ERA5* — Why open: PLOS ONE 2024; offshore buildout urgent.
- **[A-17]** (27) Does "no mow May" lawn-to-native conversion scale to neighborhood pollinators? — *iNaturalist City Nature Challenge + eBird urban hotspots + NLCD/NAIP + Homegrown National Park* — Why open: Ulrich et al 2025 + Ranalli 2025.
- **[A-9]** (26) When do salt marshes lose to sea-level rise? — *NOAA Digital Coast + NEON aquatic sites + USGS Coastal Change Hazards + Landsat marsh time series* — Why open: GRL 2025.
- **[A-12]** (26) Forecast Gulf dead zone from field-level features instead of bulk loads? — *USGS NWIS Mississippi nutrient flux + USDA CDL + NHDPlus + MODIS tile drainage* — Why open: 2025 Hypoxia Task Force target will be missed.
- **[A-13]** (26) Why one farm field yields 30% more than its neighbor under identical weather? — *USDA NASS + Sentinel-2 HLS Google Earth Engine + SSURGO + gridMET* — Why open: 2024-25 sat-yield literature plateaus R² 0.6-0.75.
- **[A-14]** (26) Predict cheatgrass / kudzu / knotweed spread, genotype-aware? — *EDDMapS + iNaturalist + GBIF + LANDFIRE + MTBS + USGS RAP* — Why open: Nature Comms 2025; ~19 cheatgrass genotypes complicate niche models.
- **[A-15]** (26) When will an ash stand die after EAB detection — and best management spend? — *USDA APHIS EAB + USA-NPN + USFS FIA + OpenTreeMap* — Why open: 2024 ND/BC confirmation; J Econ Entomology 2025 bioeconomic.
- **[A-16]** (26) Predict post-wildfire vegetation recovery (conifer return vs shrub flip)? — *MTBS + LANDFIRE 2024 + Landsat NBR time series + USFS post-fire regen plots + PRISM* — Why open: Feb 2025 "Green is the new black."
- **[A-20]** (26) Predict delayed post-drought tree mortality from satellite, 1-3 years ahead? — *USFS FIA + Landsat NBR/NDMI + MODIS EVI + NLDAS soil moisture* — Why open: GRL 2026 + PMC 2025; legacy effects up to 3 years.
- **[A-18]** (25) Where do marine plastics end up — source attribution at depth? — *TOPIOS + OceanParcels + GlobCurrent + WaveWatch III + Ocean Conservancy TIDES* — Why open: Nature 2025 1,885-station synthesis.
- **[A-19]** (24) Verify cover-crop carbon sequestration claims at farm scale? — *USDA NRCS + COMET-Farm + FLUXNET + USDA CDL* — Why open: SSSA 2025 + Earth's Future 2024; potential ~1/5 of earlier estimates.

### Economics, urban operations & public services (O)

- **[O-4]** (30) Why does a duplex take 48 days to permit in Austin and 605+ days in SF — where in the pipeline is the time lost? — *SF DBI permit tracker + NYC DOB NOW + LA LADBS + Chicago Building Permits + Census BPS monthly* — Why open: SF Examiner Oct 2025 + davisbucco.com 2025; SB 423 6-month mandate routinely missed.
- **[O-3]** (29) Why one block's pothole gets fixed in 3 days, an identical block in 3 months? — *NYC 311 + Chicago 311 + SF311 + LA MyLA311 (~20M records)* — Why open: arXiv 2502.08649 explicitly says heterogeneity unexplained. **Framing**: operations / queue routing only, not equity.
- **[O-10]** (29) Why does the same flight, same gate, same aircraft turn around in 32 vs 71 minutes? — *BTS On-Time + FlightAware ADS-B + FAA ASPM + BTS T-100* — Why open: arXiv 2601.00875 + PMC 2024 Petri-net.
- **[O-1]** (28) Why two gas stations on the same intersection post 40-cent different prices? — *GasBuddy + OPIS + EIA + OSM + ACS* — Why open: JPE 2024 (Clark et al.) + Tandfonline 2025 + Dallas Fed WP 2509.
- **[O-2]** (28) Why does the same ER have a 20-minute wait Tuesday and 4-hour Wednesday? — *CMS Hospital Compare + HCUP SEDD + MIMIC-IV-ED* — Why open: BMC HSR Mar 2025 + JMIR Med Inf 2025; AUC ceiling ~0.75. **Framing**: operations only, not clinical.
- **[O-5]** (28) Why does the same Instacart cart cost 23% more for some shoppers? — *Crowdsourced Instacart price scrapes (GitHub) + USDA AMS + Numerator* — Why open: NY AG Feb 2026 + Groundwork Collaborative Dec 2024; black-box A/B test.
- **[O-8]** (27) Why a 3-yr Honda Civic depreciates differently in Phoenix vs Boston? — *Manheim UVVI + Cars.com + CarGurus + KBB + CarMax* — Why open: Sept 2025 UVVI shows >5% regional residual unexplained.
- **[O-9]** (27) Why same building has 6% then 14% vacancy across quarters? — *Zillow ZORI + Apartment List + ACS + Census HVS + Redfin* — Why open: Zillow Nov 2025 (39.3% concession share, all-time high).
- **[O-14]** (27) Why same restaurant fails inspection 10 months after Yelp drop in one city, 2 months in another? — *Chicago Food Inspections + NYC DOHMH + SF DPH + LA County + Yelp Fusion API* — Why open: Chicago Food Inspections Evaluation tops out AUC ~0.68.
- **[O-12]** (26) Predict who will no-show jury duty — cut summonses by 30%? — *County court yields + Census ACS + Pew juror survey* — Why open: Marquette Law Faculty Blog Dec 2025; sub-50% national. **Framing**: operations only, no representation/composition framing.
- **[O-6]** (26) Why parcel reliability swung from 90 to 94% on-time, which lever? — *USPS SPM + ShipMatrix + FedEx/UPS APIs + Pitney Bowes Parcel Index* — Why open: USPS Jan 2025 ambiguous attribution + Frontiers 2025.
- **[O-11]** (26) Why a container sits 4 days at LA and 9 at Savannah? — *MarineCadastre AIS + BTS Port Performance + BEA + PMSA + SONAR free* — Why open: Tandfonline Jul 2025 + Frontiers Marine Sci 2025.
- **[O-17]** (25) Why state A processes UI claims in 3 days and state B in 31? — *DOL ETA reports + state UI portals + BLS LAUS + ImproveUnemployment.com* — Why open: Minneapolis Fed 2025; 10x throughput variance unexplained by complexity.

### Wildcard physical sciences with everyday hooks (P)

- **[P-2]** (28) Why some sinkholes give weeks of warning and others appear instantly? — *Sentinel-1 InSAR + Florida Geological Survey sinkhole DB + USGS groundwater + MODFLOW* — Why open: NASA JPL 2024-25 + Pure & Applied Geophysics 2025.
- **[P-3]** (28) Why glaciers calve in violent bursts vs steadily? — *NASA ITS_LIVE + Sentinel-1/2 + BedMachine bathymetry + Elmer/Ice + ISSM* — Why open: 47-Year Antarctic Calving Events GRL 2024-25 + Nature Geoscience 2025 Thwaites.
- **[P-4]** (29) Why same magnetic storm makes wildly different aurora shapes (STEVE, picket fence, spiral)? — *NASA Aurorasaurus open citizen science + THEMIS + SuperMAG + Swarm + SWFO-L1 magnetometer (operational spring 2026)* — Why open: Solar cycle 25 produced strongest storm since 1989 (May 2024 Gannon storm, Kp=9); Aurorasaurus record submissions Nov 2025 (X5.1 flare); SWFO-L1 adds real-time solar wind data; "no solid consensus on shapes."
- **[P-5]** (28) Why some landslides creep weeks first and others fail with no precursor? — *NASA COOLR Global Landslide Catalog + Sentinel-1 InSAR + GNSS + USGS landslide inventories + r.avaflow* — Why open: Landslides 2024 + Sci Reports 2024.
- **[P-1]** (27) Why some natural arches collapse and others survive millennia? — *USGS 3DEP lidar Utah/Arizona + NPS arch inventory + Sentinel-1 InSAR + YADE/MERCURYdpm DEM sims + Moab passive seismic* — Why open: NPS + Phys.org Aug 2024 Double Arch collapse.
- **[P-9]** (27) Why some beaches get hit by meteotsunamis in same squall line and others don't? — *NOAA NDBC buoys + Great Lakes water-level stations + HRRR/GFS pressure jumps + ADCIRC/SCHISM + MRMS* — Why open: NOAA GLERL 2024 + NHESS 2024.
- **[P-10]** (27) Why some bridges scour and fall while identical bridges nearby survive? — *USGS stream gauge + sediment + bathymetry + FHWA NBI + HEC-RAS + FaSTMECH/Delft3D + InSAR* — Why open: AQUA + Frontiers 2024-25; HEC-18 over/underpredicts by 2-10×.
- **[P-6]** (26) Why permafrost suddenly rips open in retrogressive thaw slumps? — *ArcticDEM 2m + Nitze pan-Arctic RTS inventory + ESA CCI Permafrost + Sentinel-2 + CryoGrid* — Why open: Nat Comms 2025; RTS counts grew 50× since 1984.
- **[P-7]** (26) Why karst springs reverse, brackify, or stop after ordinary rain? — *USGS NWIS + Suwannee River WMD + EPA SWMM + MODFLOW-CFP karst-conduit* — Why open: WRR 2024 (Klammler et al.) + Comm Earth Env 2025.
- **[P-8]** (26) Why HAB onset is unpredictable from "worse" nutrient conditions? — *NOAA CyAN + USGS WQP + CE-QUAL-W2 simulator* — Why open: Nature Comms 2025 + USGS OFR 2025-1004; bacterial precursor 24h ahead exists.

### Ireland-specific (IE)

- **[IE-1]** (29) Why does an A-rated Irish home use almost as much energy as a G-rated one — which retrofits actually save kWh? — *SEAI BER Public Search (~1M certs) + SEAI Retrofit reports* — Why open: Coyne & Denny 2021 (PMC8550629) + ESRI March 2026 "lagging" + EPA UNVEIL 2024.
- **[IE-2]** (29) Predict which Irish homes have dangerous radon before measurement? — *EPA Radon Map + GSI Tellus radiometric/geochemistry + JRC European Indoor Radon Maps 2024 (JRC144439)* — Why open: Ireland 8th-highest indoor radon globally; National Radon Survey 2025 live; UNVEIL shows retrofits trap radon (tension with IE-1).
- **[IE-3]** (29) Why DART punctuality collapsed (92.8% Jun → 64.5% Oct 2024) — predict next cascading day? — *NTA GTFS-Realtime feeds + Irish Rail punctuality reports + Met Éireann* — Why open: Irish Times Dec 2024.
- **[IE-7]** (29) Where and when does Dublin/Cork NO2 exceed WHO 2021 limits — which source? — *EPA AirQuality.ie + Dublin City Council traffic counts + Dublin Port AIS + solid fuel sales* — Why open: EPA Air Quality in Ireland 2024 (78% projected 2030 compliance).
- **[IE-4]** (28) M50 traffic flow breakdown — structural vs weather vs incident? — *TII Traffic Data portal (300 counters, 6.5B records) + DATEX II + Met Éireann* — Why open: Springer 2024-25 chapter "Traffic Flow Breakdown M50."
- **[IE-6]** (28) Why are 144 Irish salmon rivers collapsing — which is next? — *Inland Fisheries Ireland Fish Counter (2002-2025) + EPA water quality + Marine Institute SST buoys* — Why open: only 28% of designated rivers met Conservation Limits in 2024; IFI-UCC-Teagasc GeneFlow 2024.
- **[IE-10]** (28) What rainfall + saturation + tide combination triggers Dublin/Cork pluvial flooding — beat Met Éireann's new Flood Forecasting Centre? — *Met Éireann FFC 36 catchment models + OPW flood maps + Marine Institute tide gauges + DCC/CCC drainage* — Why open: €2.8M Met Éireann research call 2024 + IMUFF project.
- **[IE-5]** (27) Predict Irish wind curtailment hour-by-hour for "free green power" signal? — *EirGrid Smart Grid Dashboard + EirGrid System & Renewable Reports + Met Éireann wind grids* — Why open: ROI dispatch-down 11.3% in 2025.
- **[IE-8]** (27) When does an Irish beach exceed bacterial limits after rain — 12h-ahead "don't swim"? — *EPA beaches.ie + EPA wastewater + Met Éireann radar + Uisce Éireann CSO records* — Why open: EPA 2024 + Sandymount Strand classified Poor.
- **[IE-9]** (30) Predict the next "power-out-for-a-week" Irish storm outage (Darragh, Éowyn)? — *ESB PowerCheck + Met Éireann wind gust grids + Coillte tree cover + OSI line routes* — Why open: Storm Éowyn Jan 2025 was Ireland's worst storm since 1961: 768k customers, 3,000 poles, 900 km cable, EUR 150M+ economic cost (CRU Dec 2025). ESB PowerCheck data confirmed open. Pattern validated by completed EU-1.
- **[IE-11]** (26) Predict the next Irish fodder-crisis drought (1976, 2018, 2022)? — *Met Éireann SMD + Teagasc PastureBase + Bord Bia cattle prices* — Why open: Noone et al 2025 Weather; compound prediction unsolved.
- **[IE-12]** (26) Does a rewetted Irish raised bog become a net carbon sink within 5 years — methane vs CO2? — *Bord na Móna LIFE + EPA Research 401 + Sentinel-2 LUCIP + NPWS* — Why open: Wilson et al 2022 GCB + Sci Reports 2024.
- **[IE-13]** (26) Did the Feb 2025 rural 80→60 km/h speed-limit cut actually reduce crashes — diff-in-diff? — *RSA Road Traffic Collision Data + CSO + TII counters* — Why open: 73% of 2020-24 fatalities on 80+ km/h rural roads.
- **[IE-15]** (25) What's driving the 33% Irish hen harrier decline since 2015 — forestry, wind farms, or burning? — *NPWS IWM No. 147 (Feb 2024) + Coillte forest age + EirGrid wind farms + Sentinel-2 burnt area (FLARES)* — Why open: NPWS 2022 Survey + Coillte July 2024 review.
- **[IE-14]** (24) Field-level liver fluke risk forecast — push from county to paddock scale? — *DAFM Animal Health Surveillance + Met Éireann SMD + Teagasc soil maps + NPWS wetland habitat* — Why open: DAFM Nov 2024 + 3 funded 2024 projects.
- **[IE-16]** (24) Predict which peat bog / gorse area in Ireland will burn this spring + carbon released? — *EPA Research 476 (FLARES) + Sentinel-2/3 fire + Met Éireann FWI + NPWS peatland inventory* — Why open: EPA FLARES 2024.
- **[IE-17]** (24) Why bovine TB resurged from 3.27% (2016) to 6.04% (2024) despite badger vaccine? — *DAFM TB surveillance + CSO cattle movement + DAFM badger sett register* — Why open: Byrne et al 2024 + Irish Vet Journal 2024.
- **[IE-18]** (28) Close the "weather-we-can-predict / floods-we-can't-warn" gap — property-level flood warning for any Irish address, 6-24h ahead? — *Met Éireann FFC catchment forecasts + OPW CFRAM flood maps + OPW/EPA water-level gauges + Met Éireann radar/NWP + historical flood events (insurance + newspaper archives) + elevation (EU-DEM/Tailte Éireann LIDAR)* — Why open: RTÉ Clarity 2026-04-12 "Ireland can predict weather, why can't it warn of floods?" (www.rte.ie/news/clarity/2026/0412/1567613-weather-flooding-clarity/) argues the national warning gap persists despite strong weather forecasting; Met Éireann FFC covers only 36 catchments with no public property-level product. Distinct from IE-10 (catchment-model benchmarking) — this is integration + address-level warning.

### Europe-wide (EU)

- **[EU-1]** (29) Why did the 28 Apr 2025 Iberian blackout cascade as it did, and which grid states are one perturbation from collapse? — *ENTSO-E Transparency Platform + REE ESIOS API + ENTSO-E blackout report annex + PyPSA-Eur open simulator* — Why open: ENTSO-E March 2026 final report + Thlon & Brozek SSRN 2025.
- **[EU-2]** (29) Predict whether Po Valley fog persists all day or burns off — including aerosol-microphysics coupling? — *ERA5 Copernicus CDS + EEA AQ E1a/E2a + ARPA Lombardia + ARPA Emilia-Romagna + CAMS regional* — Why open: Pauli et al 2024 GRL + FAIRARI ACP 2025.
- **[EU-3]** (29) Predict Xylella appearance in Spanish/Italian olive groves 12 months ahead? — *Sentinel-2 NDVI/EVI + EFSA Xylella surveillance + EU Plant Health DB + E-OBS gridded* — Why open: Calderoni 2025 Plant Pathology (€132M Salento); Oct 2025 Cagnano Varano spread.
- **[EU-6]** (29) What predicts the "very large fire" transition in Iberian wildfires? — *EFFIS Copernicus + CAMS GFAS + ERA5 + Sentinel-2 burn scars + Corine* — Why open: EFFIS 2025 record season (1.08M ha); JRC explicitly calls for new modelling.
- **[EU-4]** (28) Predict European day-ahead electricity price spikes >€500/MWh during renewable droughts? — *ENTSO-E Transparency + ERA5 + Open Power System Data* — Why open: MDPI Energies 2025 review; <5% of papers cover post-2021.
- **[EU-5]** (28) Predict Alpine glacier summer mass loss — Saharan dust albedo vs temperature? — *GLAMOS 2025 + MeteoSwiss IDAWEB + ERA5-Land + Randolph Glacier Inventory* — Why open: GLAMOS 2025 (4th-worst year); 24% loss in 10 years.
- **[EU-8]** (28) Predict European eel glass-eel run — Gulf Stream vs freshwater habitat? — *ICES WGEEL recruitment index + Copernicus Marine GLORYS12 + GBIF Anguilla* — Why open: ICES 2025 zero-catch advice; Oxford ICES JMS 2025.
- **[EU-9]** (28) Separate pesticide / habitat / climate signals in 60% European farmland bird decline? — *PECBMS open indices + EBBA2 abundance grid via GBIF + Corine + EU CAP payments* — Why open: PECBMS State of Europe's Wild Birds 2025 (>300M birds lost).
- **[EU-11]** (29) What governs Atlantic windstorm intensification (Ciarán, Éowyn) — predict sting-jet occurrence? — *ECMWF IFS reforecasts (cycle 49r3, Oct 2025) + ERA5 + UK Met Office HadUK-Grid + KNMI Climate Explorer* — Why open: Storm Éowyn Jan 2025 confirmed as sting-jet event by UK Met Office + ECMWF reanalysis; new IFS cycle 49r3 improved sting-jet diagnostics; EU-1 project demonstrated HDR handles storm cascade questions.
- **[EU-12]** (28) Which UK Combined Sewer Overflow will spill — every one now monitored? — *Environment Agency Event Duration Monitor 2020-2025 + Met Office HadUK-Grid + OS impermeable surface* — Why open: March 2025 EDM release covers ~15,000 monitors; spatial heterogeneity unexplained.
- **[EU-13]** (28) Which European street-canyon NO2 hotspots can Sentinel-5P resolve and which can't? — *Sentinel-5P TROPOMI L2 NO2 + EEA station + AirParif + Madrid Ayuntamiento + LAQN* — Why open: ACP 2024 + AirParif 2024.
- **[EU-10]** (27) Predict ≥2 cm hail days over Germany — what's the missing predictor beyond CAPE × Shear? — *DWD Open Data radar 2005-2024 + European Severe Weather Database + ERA5* — Why open: Frontiers 2025 4th European Hail Workshop.
- **[EU-14]** (27) Mediterranean Posidonia mass flowering after 2024 marine heatwave — stress signal or recovery? — *Copernicus Marine Med reanalysis + Sentinel-2 benthic + Medseagrass + GBIF* — Why open: ScienceDirect 2025 + García-Escudero 2024.
- **[EU-16]** (27) Which European livestock operations dominate ammonia emissions — satellite-visible vs invisible? — *Sentinel-5P NH3 + CrIS + EEA NEC Directive + AP-AMMO 2025 + E-PRTR* — Why open: ACP 2024 + Nature Sci Data 2025.
- **[EU-18]** (27) What triggers Åknes rockslide creep bursts — predict next one hours ahead? — *NORSAR Åknes monitoring portal + NVE GeoNorge + Sentinel-1 InSAR + met.no Frost API* — Why open: Aspaas et al 2024 JGR Earth Surface; full collapse would tsunami Storfjord.
- **[EU-15]** (25) Predict Rotterdam/Antwerp container berth wait times hour-ahead? — *Port of Rotterdam dashboard + Port of Antwerp open data + AIS via Aishub/Spire + Copernicus Marine* — Why open: Tandfonline 2025 review; 48-72h delays at World Gateway in Jun 2025.
- **[EU-17]** (25) Where does MeteoSwiss ICON-CH1 ensemble miss foehn onset by >3 hours and why? — *MeteoSwiss foehn index + PeakWeather benchmark dataset 2025 + ICON-CH1-EPS open reforecasts + COSMO-REA6* — Why open: ICON-CH1-EPS operational May 2024.

---

## Excluded from showcase (transparency)

26 candidates removed before this pool was finalized:

**Whole education cluster (20)** — dropped per user instruction. The full L-1 to L-20 list lived in an earlier draft and is preserved in conversation history if it's ever wanted back.

**6 individual drops** for US-style racial / minority framing risk:

- Q-8 (racial PM2.5 disparities) — explicit racial framing
- Q-4 (lead service lines) — heavily Flint-coded in US discourse
- O-7 (dollar stores / food access) — food-desert literature is racially-coded
- O-13 (NYCHA public housing work orders) — racially-coded in US
- O-15 (gentrification block tipping) — racialised
- O-16 (small-business survival neighborhood heterogeneity) — adjacent to redlining

If any of those should come back with strict "operations / infrastructure framing only", they can be rehabilitated.

---

## Refresh schedule

| Checkpoint | After | Action |
|---|---|---|
| REFRESH-1 | P1-P5 | Re-search candidate pool, update both files |
| REFRESH-2 | P6-P10 | Re-search and update |
| REFRESH-3 | P11-P15 | Re-search and update; pick next 5 from refreshed pool |

Each refresh runs the same field-cluster sub-agent fan-out used in this round. Goal at each refresh: surface candidates that didn't exist or weren't yet known when this pool was generated.

---

## Notes for future work

- **Cross-cluster overlaps already noted**: HABs (A-3, Q-5, P-8 — three different angles); Wildfires (W-7, Q-2, E-16, EU-6); Heat (W-5, E-10, Q-16); Landslides (W-11, P-5).
- **Citizen-science datasets are underused**: NASA Aurorasaurus, eBird, iNaturalist, Project Monarch Health, BroodMinder, PurpleAir — all suitable HDR loop inputs without new equipment.
- **Post-COVID "why didn't it bounce back" recurring genre**: T-7 (commuter rail), IE-3 (DART) — all 28-29/30, all have 2024-2025 papers explicitly saying mechanism is open.
- **"Variation between neighbours" recurring genre**: O-1, O-3, O-4, P-1, P-2, P-3, P-10, A-7, E-1, E-3, Q-1, Q-13, IE-1. Perfect for HDR — baseline = "predict the average", question = "what feature lifts you above the baseline?", mechanism falls out.
- **Wildcard physical sciences cluster has 8 strong candidates cut for impact <3** (ball lightning, red sprites, megacryometeors, Old Faithful drift, fairy circles, earthquake lights, Morning Glory cloud, ice shoves). They're scientifically beautiful but only ~1% of adults experience them. Could be re-added if "showcase wow factor" is later prioritized over "weekly impact."

---

## REFRESH-1 additions (2026-04-10)

16 new candidates added after 5 completed projects (O-4, W-5, T-1, EU-1, IE-1). Focused on events and datasets that emerged between Apr 2025 and Apr 2026. See `refresh_1_report.md` for full rationale and re-scoring.

### Re-scored existing candidates

- **[EU-6]** 29 → **30** — 2025 was EU's most destructive wildfire season on record (JRC March 2026); new FireSpread_MedEU 3m-resolution propagation dataset (Sci Data 2026).
- **[IE-9]** 27 → **29** — Storm Éowyn Jan 2025 was Ireland's worst storm since 1961: 768k customers lost power, 3,000 poles replaced. ESB PowerCheck data confirmed open.
- **[EU-12]** 28 → **29** — England EDM 2024 data released March 2025 covers ~15,000 CSO monitors. New RSC 2026 paper links EDM to discharge consents.

### Europe-wide (EU) — new

- **[EU-19]** (30) Can citizen-science personal weather stations close the flash-flood warning gap — why did 225 PWSs see the Valencia DANA 300mm/4h event hours before AEMET's official network? — *AEMET rain gauge + Netatmo/Wunderground PWS API + EFAS Copernicus + Sentinel-1/2 + ERA5* — Why open: HESS Copernicus 2025 paper (29/6715/2025); 223 dead Oct 2024; PWS density 7× AEMET; PWS 5-min resolution vs AEMET 1-hour public.
- **[EU-20]** (29) Predict which European grid states are one frequency oscillation from blackout — 0.2 Hz inter-area mode instability from ENTSO-E open data? — *ENTSO-E Transparency Platform + PyPSA-Eur open simulator + ERA5 wind/solar* — Why open: ENTSO-E Expert Panel Final Report March 2026 identifies 0.63 Hz local + 0.2 Hz inter-area oscillations as root cause of April 2025 Iberian blackout; mechanism applicable to all interconnectors.
- **[EU-21]** (29) Predict Mediterranean reservoir drought-to-crisis tipping — what rainfall deficit tips irrigated agriculture into collapse? — *JRC European Drought Observatory (EDO) API + Copernicus CDS ERA5-Land + AEMET + ARPA + USGS-equivalent EU hydrometric* — Why open: PNAS 2025 Axarquia avocado crash; Spain reservoirs 57.2% Jan 2026; JRC May 2025 drought alert; open EDO download portal.
- **[EU-22]** (29) Predict which EU drinking water supplies will exceed new PFAS limits — from land use + industrial history before monitoring data arrives? — *EEA Waterbase PFOS maps 2018-2022 + Forever Pollution Project map + Corine land cover + E-PRTR industrial emissions* — Why open: EU Drinking Water Directive PFAS monitoring mandatory from 12 Jan 2026 (0.1 µg/l individual, 0.5 µg/l total); 51-60% of rivers already exceed PFOS EQS; first national results from France published 2025.
- **[EU-23]** (28) Why does Deutsche Bahn long-distance punctuality collapse some weeks and not others — predict delay cascades from open archive? — *Bahn-Vorhersage CC-BY-4.0 dataset (Sep 2021–present, ~700 GB) + OpenStreetMap rail + DWD Open Weather* — Why open: 59.4% punctuality Feb 2026; EUR 156M compensation 2025; mechanism (infrastructure works vs weather vs cascading) unresolved despite dataset availability.
- **[EU-24]** (28) Predict wildfire propagation speed from 3m-resolution satellite time series — what landscape feature makes a fire explode vs creep? — *FireSpread_MedEU (320 maps, 103 fires, ~3m spatial, daily temporal, Sci Data 2026) + EFFIS Copernicus + ERA5 + Corine* — Why open: dataset published Feb 2026; 2025 was EU's most destructive fire season; JRC March 2026 explicitly calls for new propagation modelling.
- **[EU-25]** (28) Predict where renewable energy curtailment will spike next in Europe — what grid topology + weather pattern wastes 11% of green output? — *ENTSO-E Transparency + ERA5 + Open Power System Data + EirGrid Smart Grid Dashboard* — Why open: 11% curtailment in Spain summer 2025; EUR 7.2B lost in 7 countries 2024; 1,700 GW stuck in connection queues; strategic priority for EU Grids Package Dec 2025.

### Ireland-specific (IE) — new

- **[IE-18]** (29) Predict which Irish water supply will issue the next boil-water notice — pipe age, treatment type, rainfall, or turbidity as trigger? — *EPA drinking water quality reports + Uisce Éireann annual report + Met Éireann radar + EPA Geoportal hydrometric data* — Why open: 62,645 people on >30-day BWN in 2023 (up from 24k); Uisce Éireann fined EUR 20M Nov 2025; 40% of treated water lost to leaks; Wexford 22k-person BWN Dec 2025.
- **[IE-19]** (29) Will Ireland's data centres crash the grid this winter — predict hour-ahead system adequacy margin? — *EirGrid Smart Grid Dashboard (real-time open) + EirGrid System Reports + Met Éireann wind grids + CRU reports* — Why open: data centres = 21% of national electricity (projected 32% by 2026); record 6,024 MW peak Jan 2025; EirGrid Winter Outlook 2025/26 warns of "alert state"; CRU Dec 2025 new 80%-renewable connection policy.
- **[IE-20]** (28) Where in Ireland's planning pipeline does housing permission die — An Coimisiún Pleanála bottleneck, judicial review, or utility connection? — *An Coimisiún Pleanála decisions portal + CSO planning permissions + Uisce Éireann connection data + ESB connection data* — Why open: planning permissions -38% Q4 2024; apartment permits -52%; judicial reviews hit 147/yr (up from 15/yr a decade ago); An Coimisiún Pleanála launched Jun 2025; completions fell 75%.
- **[IE-21]** (28) Which Irish road segment will kill a cyclist or pedestrian next — predict from infrastructure, speed, and exposure? — *RSA Road Traffic Collision Data + TII counters + NTA GTFS + OSM cycling infrastructure + CSO census commuting data* — Why open: 190 road deaths 2025 (highest since 2014); cyclist deaths doubled 2022-2025 (7 → 14); RSA May 2025 + Oct 2025 cyclist safety reports; single-cyclist collisions linked to infrastructure gaps.

### Weather, climate hazards & natural disasters (W) — new

- **[W-16]** (29) Predict DANA-type Mediterranean cut-off-low flash floods 6+ hours ahead — which configurations actually produce 300mm/4h extremes? — *ERA5 + AEMET + EFAS Copernicus + Sentinel-1/2 + HRRR-equivalent ECMWF IFS high-res* — Why open: Valencia Oct 2024 (223 dead, >1000-yr return period rainfall); Copernicus HESS 2025 + EGUsphere 2025 papers; EFAS v5.5 open since Sep 2025.
- **[W-17]** (28) Predict European heat wave excess deaths city-by-city in real time — which city characteristics amplify the 16,500 climate-attributable toll from summer 2025? — *ERA5 + Eurostat weekly mortality + Copernicus UrbClim 100-city UHI + WHO/Euro EuroMOMO + FAIRUrbTemp (Sci Data 2026)* — Why open: WWA Sep 2025 attribution study; 2,300 dead in 10 days Jun-Jul 2025; Rome/Athens/Bucharest worst per-capita; city-level mechanism (green cover, building mass, AC penetration) actively debated.

### Transportation & mobility (T) — new

- **[T-19]** (28) When will Red Sea shipping disruption tip a European port into congestion — predict container dwell from AIS + rerouting status? — *MarineCadastre/Spire AIS + Port of Rotterdam open dashboard + Port of Antwerp open data + Copernicus Marine + UNCTAD shipping data* — Why open: Cape of Good Hope rerouting absorbed 9% of global container capacity; Europe transit times +33%; 48-72h delays at World Gateway Jun 2025; natural experiment still running as of Apr 2026.

### Environmental quality (Q) — new

- **[Q-17]** (29) Predict where EU combined sewer overflows contaminate bathing water after storms — which CSO + catchment features produce pathogen spikes? — *England Environment Agency EDM 2020-2025 (~15,000 monitors) + Met Office HadUK-Grid + OS impermeable surface + EPA beaches.ie + EEA Bathing Water Directive data* — Why open: revised EU Urban Wastewater Directive Jan 2025 (2% CSO cap by 2039); RSC 2026 paper linking EDM to discharge consents; Barcelona early-warning pilot; political salience high (UK water company scandals 2024-25).

### Energy & built environment (E) — new

- **[E-17]** (28) Predict which EU buildings will miss the 2030 EPBD renovation trajectory — from EPC databases, which worst-performers are unreachable? — *UK ONS 4.8M EPC records + Irish SEAI BER (~1M certs) + EU Building Stock Observatory + Copernicus Urban Atlas* — Why open: revised EPBD transposition deadline May 2026; 16% worst non-residential must be renovated by 2030; national EPC databases becoming open across EU; cross-country comparison of "performance gap" unsolved.

---

## REFRESH-2 additions (2026-04-10)

15 new candidates added after 9 completed projects (O-4, W-5, T-1, EU-1, IE-1, IE-2, EU-3/blocked, IE-3, EU-6, T-3). Focused on closing gaps in water/hydrology, marine/ocean, astronomy/space weather, and robotics. See `refresh_2_report.md` for full rationale and re-scoring.

### Re-scored existing candidates

- **[IE-9]** 29 → **30** — CRU Dec 2025 report quantified EUR 150M+ economic cost of Storm Eowyn and identified specific infrastructure vulnerabilities (overhead vs underground, tree proximity). ESB PowerCheck open data fully available. Pattern validated by completed EU-1 (Iberian blackout).
- **[P-4]** 28 → **29** — Solar cycle 25 produced the strongest geomagnetic storm since 1989 (May 2024 Gannon storm, Kp=9). Aurorasaurus citizen-science database saw record submissions Nov 2025 (X5.1 flare). SWFO-L1 magnetometer operational spring 2026 adds new real-time data.
- **[EU-11]** 28 → **29** — Storm Eowyn (Jan 2025) explicitly confirmed as sting-jet event by UK Met Office and ECMWF reanalysis. New ECMWF IFS cycle 49r3 with improved sting-jet diagnostics operational Oct 2025.
- **[W-17]** 28 → **absorbed into EU-26** — EU-26 supersedes W-17 with sharper 854-city framing (LSHTM/Imperial Sep 2025 study) and FAIRUrbTemp dataset. W-17 remains in pool but should not be selected independently.

### Wildcard physical sciences (P) — new

- **[P-11]** (29) Predict which LEO satellites will lose altitude in the next solar storm — can the CRASH Clock be made predictive instead of retrospective? — *SpaceTrack-TimeSeries dataset (7M TLEs, 14,213 objects incl. 7,149 Starlink, Figshare open) + Space-Track.org TLE archive + NOAA SWPC geomagnetic indices + SWFO-L1 magnetometer (operational spring 2026) + JB2008/NRLMSISE atmospheric density models* — Why open: Princeton CRASH Clock paper Dec 2025 shows LEO is 2.8 days from catastrophic collision if maneuvers stop (43x worse than 2018); Frontiers 2025 tracked Starlink reentries vs geomagnetic activity; arXiv 2509.19647 deep-dive on LEO network impact; mechanism (thermospheric density surge vs drag coefficient vs orbit shell altitude) actively debated; universal hook = "your Starlink internet is 2.8 days from a solar storm away from going dark."
- **[P-12]** (28) Predict which European bridges are deforming before inspectors visit — mm-scale displacement from free satellite radar? — *ESA Sentinel-1 InSAR + European Ground Motion Service (EGMS) + NASA NISAR (launched Jul 2025, 12-day revisit, open data) + FHWA NBI (US) + France national bridge inventory + OpenStreetMap* — Why open: NISAR launched Jul 2025 with free/open data policy; ScienceDaily Mar 2026 shows InSAR detects pre-failure deformation signals; Germany needs EUR 100B bridge repairs, Dresden Carolabrucke collapsed Sep 2024; France surveyed 45,000 bridges; method could triple actively monitored bridges from <20% to >60% of long-span inventory.

### Weather, climate hazards & natural disasters (W) — new

- **[W-18]** (29) Predict Mediterranean marine mass mortality events from sea temperature profiles — which heatwave configurations kill gorgonians and sponges at depth? — *T-MEDNet database (20M+ temperature samples, 70+ sites, CC-BY-SA) + MME-T-MEDNet mass mortality database (791,887 records, OBIS/GBIF open) + Copernicus Marine Med reanalysis + Sentinel-2 benthic* — Why open: record Med SST summer 2025 (6C above normal in places); Nature Comms 2025 (s41467-025-55949-0) vulnerability of 389 species 1986-2020; 2022 event hit 30m depth for first time with lethal threshold 25C breached; mechanism (depth penetration x exposure duration x species trait) actively debated.
- **[W-19]** (28) Predict European river flood peaks in ungauged catchments — which landscape features control the translation from rainfall to discharge? — *EStreams dataset (17,130 catchments, up to 120 years, Zenodo open, Sci Data 2024) + EFAS v5.5 (open since Sep 2025) + ERA5-Land + Copernicus DEM + Corine land cover* — Why open: Nature 2024 showed ML predictions at 5-day lead match current same-day skill for ungauged watersheds; EFAS major upgrade 2025; EStreams consolidates 50+ providers across 41 countries; mechanism (soil permeability x slope x antecedent moisture x land cover) is the core hydrological question; fills water/hydrology gap.

### Europe-wide (EU) — new

- **[EU-26]** (30) Predict city-level heat-wave excess deaths across 854 European cities in real time — which urban features amplify the 16,500 climate-attributable toll? — *FAIRUrbTemp dataset (811 sensors, Sci Data 2026) + Copernicus UrbClim 100-city UHI + Eurostat weekly mortality + ERA5 + Copernicus Urban Atlas* — Why open: LSHTM/Imperial Sep 2025 attribution study across 854 cities found climate change tripled heat deaths (16,500 excess summer 2025); Rome/Athens/Bucharest worst per-capita; city-level mechanism (green cover fraction, building thermal mass, AC penetration rate, demographic age structure) is unresolved; 30% tree cover could prevent 2,644 deaths (1.8% of summer mortality). Absorbs and supersedes W-17 from REFRESH-1 with sharper framing.
- **[EU-27]** (29) Predict where the next floating algae bloom will strand on European/Caribbean coasts — from satellite FAI, ocean currents, and wind? — *Copernicus Marine Sentinel-3 OLCI Floating Algae Index (released Nov 2025) + USF Sargassum Watch System (SaWS) open archive + CARICOOS tracker + Copernicus Marine currents + ERA5 winds* — Why open: EUMETSAT declared 2025 a record Sargassum year; Copernicus Nov 2025 release added FAI detection product; USF 2-month-ahead bulletin exists but skill degrades at shore approach; stranding prediction is the open problem; fills marine/ocean gap with immediate tourism + fisheries hook.
- **[EU-28]** (28) Predict which Mediterranean benthic species will suffer mass mortality in the next marine heatwave — from temperature profiles and species traits? — *MME-T-MEDNet database (791,887 records, OBIS/GBIF open) + T-MEDNet temperature time series (20M+ samples, 70+ sites) + Copernicus Marine Med reanalysis + Nature Comms 2025 trait vulnerability dataset (GitHub open)* — Why open: Nature Comms 2025 analyzed 389 species across 1986-2020 but trait-based prediction at site level is unsolved; T-MEDNet is the richest open benthic monitoring network in any sea; mechanism (thermal history x depth x trait category) maps directly to HDR "which feature matters most" framing.

### Ireland-specific (IE) — new

- **[IE-22]** (29) Predict which Irish river catchment will breach nitrogen limits next — from farm intensity, soil drainage class, and rainfall timing? — *EPA catchments.ie open data (1,000+ monitoring stations) + EPA nitrogen/phosphorus annual reports + FLAG map (catchment-level N/P reduction targets) + Teagasc soil maps + Met Eireann rainfall + CSO agricultural census* — Why open: EPA Mar 2026 reported nitrogen up 10% in 2025 (after 16% rise H1 2025); 44% of river sites have high nitrate; agriculture = 85% of N loading in rural catchments; Ireland will miss EU 2027 Water Framework Directive target; mechanism (freely draining soils x dairy intensity x winter rainfall) is the core question.
- **[IE-23]** (28) Predict where Ireland's public EV charger network will fail or be unavailable — from grid capacity, charger age, location, and usage patterns? — *Open Charge Map API + ESB eCars network status + Irish EV Association annual review + EirGrid Smart Grid Dashboard + Met Eireann* — Why open: ESB claims 98% reliability but users report persistent failures (RTE Nov 2025); 43% fast-charger growth in 2025 but west/northwest gaps remain; 35 planned locations (160+ connectors) stalled by grid connection delays; mechanism (grid constraint vs charger hardware vs usage surge vs weather) is unresolved.
- **[IE-24]** (28) Predict which Irish rental tenancy will receive an eviction notice — from landlord type, rent level, location, and policy regime? — *RTB Rent Index (open) + RTB quarterly reports + Daft.ie rental reports + CSO housing data + An Coimisiun Pleanala decisions* — Why open: RTB Q4 2025 reports eviction notices up 41% YoY; 42,300 rental units lost since Jan 2020; fewer than 1,800 homes listed Feb 2026 (20-year low); new national rent control from Mar 2026 creates natural experiment; Dept of Finance says crisis will last 15 more years; mechanism (landlord exit vs rent pressure vs policy change) is the question.

### Environmental quality (Q) — new

- **[Q-18]** (29) Predict where European coastal flooding will hit from compound storm-surge + tide + river discharge events — using new SWOT satellite sea-level data? — *Copernicus Marine SWOT-KaRIn 2D sea-level dataset (released Nov 2025) + Copernicus Marine coastal bathymetry (Nov 2025) + EEA coastal hazard maps + ERA5 storm surge + tide gauge networks + EFAS river discharge* — Why open: NHESS 2026 compound flooding framework published; NHESS 2026 Mediterranean urban beach early-warning pilot; SWOT-KaRIn adds 2D swath data that no prediction study has yet exploited; Copernicus free data; fills marine/coastal gap.
- **[Q-19]** (28) Predict which European river will breach microplastic safety thresholds — from land use, population density, wastewater treatment level, and flow regime? — *Frontiers in Water 2026 Danube quantitative dataset + NOAA NCEI marine microplastics database (open) + EEA Waterbase + Corine land cover + EU Urban Wastewater Directive monitoring* — Why open: EU Drinking Water Directive microplastics monitoring mandatory from 2026; Wiley 2024 review covers 6 major European rivers; standardization gap means ML could exploit heterogeneous monitoring data; no integrated pan-European prediction model exists; fills emerging pollutant gap.

### Transportation & mobility (T) — new

- **[T-20]** (28) Predict where autonomous sidewalk delivery robots will get stuck, block pedestrians, or fail — from terrain, weather, pedestrian density, and fleet scale? — *City PDD permit data + OSM sidewalk/curb data + NOAA weather + US Census pedestrian exposure + Starship/Serve public incident reports + university campus deployment logs* — Why open: Starship surpassed 8M deliveries; Serve scaled to 2,000+ robots in 20 US cities; University of Pittsburgh pulled fleet after wheelchair-blocking incidents 2025; incident rate <0.3 per 10,000 but accessibility conflicts emerging in 37 states with PDD legislation; mechanism (terrain grade vs curb cut availability vs pedestrian density vs weather) is uncharacterized; fills robotics gap.

### Agriculture & ecology (A) — new

- **[A-21]** (28) Predict which European sandy beach will lose >10m of shoreline this decade — from wave climate, sediment budget, and coastal development pressure? — *ESA Coastal Erosion 2 project (2,800 km mapped, 30,000+ satellite images, 25 years) + NISAR 12-day InSAR (open from 2026) + Copernicus coastal bathymetry (Nov 2025) + JRC coastal erosion hazard maps + Corine + ERA5 wave data* — Why open: Frontiers 2025 Greek/Italian harmonized framework published; NISAR will triple monitored coastline; mechanism (wave energy x sediment supply x hard coastal structure x sea-level rise) is the key question for EUR 500M+/yr European coastal protection spending.

### Economics & operations (O) — new

- **[O-18]** (28) Predict which Irish infrastructure megaproject will miss its delivery date — from planning stage, judicial review exposure, contractor market, and procurement model? — *CSO construction output + An Coimisiun Pleanala decisions portal + Department of Public Expenditure NDP tracker + KPMG Infrastructure Outlook 2026 + Oireachtas committee transcripts* — Why open: NDP committed EUR 275B to 2035; Greater Dublin Drainage took 7 years in planning (JR settled Dec 2025, won't open until 2032); MetroLink Railway Order late 2025 but construction timeline uncertain; planning permissions -38% Q4 2024; KPMG/Irish Times Mar 2026 flags systemic delivery pattern; mechanism (JR risk x procurement model x labour market x political cycle) is uncharacterized.

- **[OSS-1]** (30) What predicts open source project abandonment — commit frequency decay, bus factor, issue response time, star/fork ratio, or maintainer burnout? — *GH Archive (BigQuery, full event stream since 2011) + GitHub REST/GraphQL API (contributor stats, issue/PR timelines) + Libraries.io (dependency graph, downstream impact) + OSS Insights (community health metrics)* — Why open: 25%+ of critical OSS dependencies have 1-2 maintainers (Harvard/Linux Foundation Census III, 2024); xz-utils backdoor (2024) highlighted single-maintainer risk; Log4Shell showed downstream blast radius of abandoned maintenance; mechanism (commit cadence decay vs contributor churn vs issue backlog growth vs corporate sponsorship loss) is uncharacterized at scale; GH Archive covers 6B+ events across 200M+ repos; every HN reader maintains or depends on OSS. HN-targeted.

- **[ECON-1]** (30) Do YC companies actually outperform non-YC startups at the same stage — or is it selection bias? — *Crunchbase Open Data Map (funding rounds, valuations, outcomes for 1M+ companies) + PitchBook public summaries + SEC EDGAR (IPO filings, S-1s) + YC public directory (all batches since 2005) + LinkedIn workforce data (employee counts as growth proxy)* — Why open: YC claims 5x higher success rate but no controlled study exists; selection bias is the obvious confounder (YC admits <2% of applicants); Crunchbase has standardised funding/outcome data for matched-pair analysis; mechanism (network effects vs mentorship vs signalling vs selection) is the key question; directly relevant to every HN reader considering applying or investing. HN-targeted.

- **[ECON-2]** (30) What predicts which housing markets crash first — and how far in advance? — *Zillow ZTRAX (transaction-level data, public) + FRED (permits, price indices, mortgage rates, income) + Census ACS (price-to-income ratios, migration) + Redfin Data Center (inventory, days-on-market, price drops) + CoreLogic public reports + FHFA House Price Index* — Why open: 2008 crash was predictable 18-24 months out from permit/inventory data but nobody had a systematic model; current cycle shows record price-to-income in 40+ metros; mechanism (permit surge → oversupply → inventory rise → price drop lag → forced selling cascade) is well-theorised but the lead indicators and their relative timing are uncharacterized across metro areas; all data freely available at metro level. HN-targeted.

---

## REFRESH-3 additions (2026-04-13)

45 new candidates added after 13 completed projects (O-4, W-5, T-1, EU-1, IE-1, IE-2, EU-3, IE-3, EU-6, T-3, IE-7, T-9, O-10, E-4, EU-2). Nine parallel cluster sub-agents (T, E, Q, W, A, O, P, IE, EU) searched for 2026-02-01 → 2026-04-13 news, data releases, and unresolved mechanisms. IE and O candidates renumbered on merge to avoid REFRESH-2 IDs already in use (IE-19..IE-24, O-18). Standout: EU-29 (GPS/GNSS jamming over European airspace) scored 30/30 — ties OSS-1, ECON-1, ECON-2 at the top of the queue.

### Transportation & mobility (T) — new

- **[T-21]** (28) Which flights in Baltic/Eastern-European airspace will lose GPS next — from jammer location, frequency, altitude, and weather? — *OpenSky Network ADS-B + Spire Aviation NIC/NACp public reports + Univ. of Gdynia TDOA Kaliningrad localisation dataset (GPS Solutions 2026) + EASA Conflict Zone Information Bulletins + flightradar24 disruption logs* — Why open: Poland logged 2,732 GPS jamming/spoofing cases Jan 2025; Lithuania 22× increase by mid-2025; Mar 2026 Helsinki–Tartu ILS-only approaches; NATO EDA funding Mar 2026; propagation + altitude exposure mechanism uncharacterised.
- **[T-22]** (28) Did Europe's city-wide 30 km/h defaults actually save lives, or did drivers shift routes — cleanly separating speed from network effects? — *Amsterdam Open Data crash + TomTom Traffic Stats + Paris/Brussels/Madrid accident data + EU CARE road-safety DB* — Why open: Amsterdam 2-yr 30 km/h anniversary Dec 2025; NTUA 2024 review found 23/37/38% reductions but couldn't isolate enforcement vs design vs modal shift; Paris Sept 2025 evaluation controversy.
- **[T-23]** (27) What precursor signal predicts a critical runway incursion — category-A near-miss vs routine deviation? — *FAA Runway Safety Office incursion DB + NASA ASRS narratives + DOT OIG March 2025 audit + OpenSky ADS-B ground-movement + METAR visibility + ALPA Runway Incursion Study* — Why open: FAA logged 498 incursions in first 4 months of FY2026; LAX Air France/Gulfstream near-miss 12 Apr 2026; DOT OIG Mar 2025 flagged no predictive model; ASRS narratives untapped.
- **[T-24]** (25) Which European rail corridor will suffer the next cascading signalling failure — predict propagation length and duration? — *ERA Common Safety Indicators + RailISAC + ADIF Spain open incident log + Eurostat rail performance + EPF punctuality + OpenTraffic GTFS-RT rail* — Why open: Madrid-Málaga high-speed corridor closed Feb–Apr 2026 (copper theft + signalling cascade, 10k+ stranded); Belgium 12 Mar 2026 strike 36h propagation; EU Rail FP1 Mar 2026 flagged propagation modelling as R&D gap.
- **[T-25]** (24) When does a lithium-ion micromobility battery fire go catastrophic vs contained — from charger type, battery age, storage context, building layout? — *NYC FDNY + London Fire Brigade e-bike/e-scooter fire registries + CPSC NEISS + CPSC Apr 2026 Rad Power recall + UL 2849 compliance + NYC DOT battery-swap cabinet telemetry* — Why open: LFB 407 fires 2024 (4× 2020); NYC 900+ since 2022; CPSC Apr 2026 Rad Power stop-use; NYC's first public battery-swap cabinets 2026-27 create natural experiment.

### Energy & built environment (E) — new

- **[E-18]** (28) Why did a 59%-solar grid collapse in 10 seconds — can we predict voltage-control failures before the next Iberian-style cascade? — *ENTSO-E Transparency + REE Spanish grid PMU releases + Red Eléctrica post-event data + final 192-page ENTSO-E Expert Panel report (20 Mar 2026)* — Why open: 28 Apr 2025 Iberian blackout (31 GW, 10+ hrs) final report 20 Mar 2026 declared voltage/reactive-power, NOT inertia, as root cause — overturning 11-month consensus; PMU traces now open. Complements completed EU-1.
- **[E-19]** (27) Why are Danish grid-connection queues for data centres 8× national peak demand — which requests actually get built? — *Energinet queue register (paused Mar 2026) + ENTSO-E TYNDP + EU data-centre KPI returns (first 15-May-2026 filings) + National Grid UK Connected Data Portal* — Why open: Energinet froze new connections Mar 2026 after 60 GW of requests against 7.3 GW peak demand; EU-wide 1.7 TW queue; first cross-country open dataset.
- **[E-20]** (27) Why did negative electricity prices jump 25% in one year — which hours and assets drive the flip below zero? — *ENTSO-E day-ahead + SMARD.de + RTE éCO2mix + Ember European Electricity Review 2026 + national curtailment logs* — Why open: 7 EU countries crossed 5%-of-hours negative threshold 2025; Germany 570+ negative hours (Bloomberg 5 Jan 2026); €7.2 bn 2024 curtailment disclosed; driver decomposition still unquantified.
- **[E-21]** (26) Are Ireland's 14,000 SEAI-grant heat pumps actually hitting UK's SCOP 3.8 — and which install choices explain the gap? — *SEAI BER + SEAI high-temp heat-pump pilot (Feb 2026) + HeatpumpMonitor.org 252-system open feed (SCOP 3.87, Jan 2026) + MPRN smart-meter half-hourly data* — Why open: Feb 2026 grant doubled to €12,500 + €2,000 radiator top-up; ESRI Mar 2026 "lagging" retrofit targets; IE-vs-UK benchmarking now possible.
- **[E-22]** (26) Can 13-year calendar-aging data separate "storage-only" from "cycling" degradation in grid batteries — rewriting BESS warranty models? — *Nov-2025 multi-SOC calendar-cycle dataset (Sci Data) + 232-cell 13-year calendar dataset + CALCE + second-life grid-storage cycling + Samsung INR21700-50E 279-cell* — Why open: three large calendar-aging releases in late 2025; Italian Terna 2026 capacity auction (38.4 GW, €1.82 bn) now pays existing batteries; warranty overstatement is hidden revenue risk.

### Environmental quality (Q) — new

- **[Q-20]** (29) Which European AQ zones will breach the revised EU AAQD's 2030 PM2.5 limit (10 μg/m³) — and is the gap from traffic, wood burning, or transboundary import? — *EEA AQ e-Reporting + Copernicus CAMS + Sentinel-5P + Eurostat residential heating + EMEP emissions* — Why open: Revised AAQD in force Dec 2024; EEA Mar 2026 flagged ~60% of urban EU still above new limit; Nature Cities 2026 source-apportionment gap paper.
- **[Q-21]** (28) Can CAMS + TROPOMI forecast city-scale PM10 from Saharan dust 48–72 h ahead — and why do some events exceed WHO limits while others stall over the Med? — *CAMS dust forecast + S-5P aerosol index + EEA AQ + AERONET + ERA5* — Why open: Feb-Mar 2026 Sahara intrusion reached N. France/Benelux >150 μg/m³ (Le Monde 6 Mar 2026); ACP 2026 paper shows CAMS skill drops sharply north of 45°N.
- **[Q-22]** (28) Which EU drinking-water utilities will fail the new PFAS-20 sum limit (0.1 μg/L) when the Jan 2026 compliance date bites? — *EU utility PFAS reports under DWD Annex I + ECHA PFAS restriction dossier + Copernicus CORINE + EPER-E-PRTR + national EPA well data* — Why open: Jan 2026 deadline; EurEau Mar 2026 estimates 12–18% non-compliant; ECHA committee opinion due 2026.
- **[Q-23]** (27) Why has EU road-death decline flatlined since 2024 — vulnerable-road-user share, e-scooter growth, or SUV fleet penetration? — *CARE European road accident DB + Eurostat transport + UNECE ITF + ACEA fleet composition + ETSC PIN* — Why open: ETSC PIN Flash 41 (Mar 2026) — only 2% fatality drop 2024–25 vs 4.5% needed for 2030 target.
- **[Q-24]** (27) Can windowsill + satellite data predict which EU neighbourhoods will breach 2026 revised END Lden>55 dB CVD-risk threshold — and how much is traffic vs canyon geometry? — *EEA END maps + CNOSSOS-EU + OSM building heights + S-2 urban morphology + Eurostat CVD admissions + NoiseCapture/Bruitparif* — Why open: END third-round deadline 2026 with mandatory CVD metric; EEA Feb 2026 flags ≥20% model–measurement divergence.

### Weather, climate hazards & natural disasters (W) — new

- **[W-20]** (29) Which SWIO tropical cyclones will undergo explosive rapid intensification and destroy a coastal city within 72 h? — *IBTrACS + JTWC + RSMC La Réunion + IMERG + Copernicus Marine SST/OHC + ERA5* — Why open: Cyclone Gezani (10 Feb 2026) intensified to 250 km/h, destroyed 90% of Toamasina (63 dead, $142M), 10 days after Fytia; SWIO RI physics differ from Atlantic and are under-benchmarked.
- **[W-21]** (28) Predict where Arctic retrogressive thaw slumps will activate and release legacy carbon + sediment next summer. — *DARTS AI-detected RTS footprints (Sci Data 2025, ~43k slumps, CC-BY) + ARTS verified polygons + PlanetScope + ArcticDEM + ERA5-Land + ESA CCI permafrost* — Why open: DARTS is the first circum-Arctic ML-ready RTS benchmark; Kanin Peninsula inventory Aug 2025; thaw-slump count rising exponentially across Siberia since 2018.
- **[W-22]** (28) Predict compound coastal flooding where rain + surge + river discharge co-occur beyond marginal-return expectations. — *C3S CDS European storm-surge/tide/wave reanalysis (open 2025) + ECFAS + GTSM + ERA5 + GloFAS + NOAA tide gauges* — Why open: NHESS 26:391 (Jan 2026) + HESS 30:401 (Feb 2026) show dependence structure is dominant uncertainty; Mar 2026 Pacific NW AR train + king tides.
- **[W-23]** (27) Predict early-season "out-of-season" heat-dome ridges that shatter records weeks before climatological peak — which Rossby-wave configs are the skill cliff? — *ERA5 500hPa + GEFS/ECMWF reforecasts + GHCN-Daily + Climate Central attribution workbooks (CC-BY) + WWA rapid-attribution archive* — Why open: Mar 2026 SW US heat dome broke 7,000+ daily records (+11–17°C), Phoenix +12.5°F; WWA found +2.6–4°C attributable; S2S skill for March ridges remains poor.
- **[W-24]** (26) Predict volcanic ash plume dispersion height and trajectory for aviation hazard from real-time satellite + sounding inputs. — *NOAA/JMA/VAAC Toulouse/Wellington advisories + Himawari/GOES/Meteosat volcanic-ash RGB + ERA5 upper-air + Smithsonian GVP + NAME/HYSPLIT* — Why open: Shiveluch FL480 and Ambae FL140 plumes Feb–Apr 2026 triggered dozens of VAAC advisories; ash-cloud ML benchmarking gap flagged.

### Agriculture, ecology & biodiversity (A) — new

- **[A-22]** (28) Can we predict BTV-3 bluetongue spread farm-by-farm across N. Europe from midge dispersal + livestock movement + climate before clinical signs? — *EFSA ADIS + EuroMOMO + ERA5 + Dutch CBS livestock register + EMA vaccine uptake + Copernicus Culicoides climate suitability* — Why open: BTV-3 hit ~6,000 Dutch farms with 75% sheep mortality; spread to AT/NO/PL/ES by 2025; two EMA vaccines 2025 with heterogeneous uptake; Science AAAS Feb 2026 flags midge-dispersal modelling gap.
- **[A-23]** (27) Can Sentinel burn-scar + biomass + phenology predict which EU27 fire-affected forest patches flip to shrubland vs regenerate conifer after the record 2025 season? — *EFFIS 2025 perimeters + S-2 NBR/NDVI + LUCAS + CLMS Forest Type + ERA5-Land + IFN Spain, IFN6 Portugal* — Why open: JRC 31 Mar 2026 confirmed 1,079,538 ha burned EU27 (highest on record); post-fire recovery trajectory for record cohort unmeasured.
- **[A-24]** (26) Predict where 2026 desert-locust swarms will cross from NW Africa into the Sahel and Mediterranean, and when to spray. — *FAO Locust Hub + MODIS/S-2 NDVI + SMAP soil moisture + ERA5 winds + eLocust3 + CHIRPS* — Why open: FAO early-2026 bulletin warns third-generation breeding (Mauritania → Morocco) will yield swarms Feb-Mar 2026; control operations insufficient per FAO.
- **[A-25]** (26) Which EU27 draft National Restoration Plans (due 1 Sep 2026) propose measurable, additional restoration vs relabelling Natura 2000? — *EU NRR Art. 14 draft NRPs + Natura 2000 polygons + CORINE + EEA Art. 17 condition reports + BirdLife NRP mid-term + LIFE registry* — Why open: NRL binding Aug 2024; draft NRPs due 1 Sep 2026; BirdLife mid-term flagged CZ/DE/FI/FR/PT/ES as frontrunners; no public "additionality" framework.
- **[A-26]** (27) Forecast 2026 trans-Atlantic sargassum inundation week-by-week at the beach scale from satellite + currents + Amazon nutrient flux. — *USF Sargassum Watch (VIIRS, MODIS) + Copernicus S-2/3 + CMEMS + HYCOM + HYBAM Amazon discharge + CaRICOOS* — Why open: USF reported record Jan (9.5 Mt) / Feb (13.6 Mt) / Mar (19.1 Mt) 2026 biomass; Cayman Compass 4 Apr 2026 "record-breaking year"; beach-landfall lead-time ≤ 2 weeks.

### Economics, urban operations & public services (O) — new

- **[O-19]** (27) When a central bank pivots to cuts in 2026-Q1, why does mortgage-rate pass-through take 6 weeks in Portugal but 6 months in the Netherlands? — *ECB MFI Interest Rate Statistics + Eurostat HICP + EBA Risk Dashboard + national central-bank pass-through series + BIS residential property prices* — Why open: ECB first-cut sequence accelerated Feb-Mar 2026 after Eurozone HICP 1.9%; ECB FSR Apr 2026 flags heterogeneous pass-through; Bruegel 11 Mar 2026 says mechanism unresolved.
- **[O-20]** (26) In the 2025-26 tech-layoff wave, why does one laid-off software engineer land a new role in 38 days and an identical-profile peer in 210? — *layoffs.fyi + BLS JOLTS + LinkedIn Economic Graph + GitHub Archive + Stack Overflow 2025 survey + Crunchbase* — Why open: Feb 2026 layoffs.fyi shows 140k tech cuts YTD post-rate-pivot; BLS Mar 2026 JOLTS bifurcation; Brookings 18 Feb 2026 identifies AI-substitution vs sector-rotation as competing hypotheses.
- **[O-21]** (26) Which firms got productivity gains from generative AI adoption in 2025, and which just absorbed licence cost — what separates them at SME level? — *Eurostat ICT enterprise survey (2026-03-20 release) + ONS MES AI module + US Census BTOS AI questions + OECD.AI firm-level open microdata* — Why open: Eurostat 2026-03-20 showed 13.5% EU firm adoption with wide productivity dispersion; Stanford AI Index 2026 flags firm heterogeneity as biggest open question.
- **[O-22]** (25) Why do some 2025-vintage CRE office loans extend-and-pretend while identical-LTV peers default in Q1 2026? — *Trepp CMBS delinquency (public summary) + FDIC Call Reports + ECB AnaCredit aggregates + MSCI Real Capital Analytics + Fed H.8 + Companies House UK* — Why open: Fed FSR Apr 2026 notes CRE-office maturity wall peaked Q1 2026 with 34% default rate but wide dispersion; JPM CRE note 4 Mar 2026 flags tenant-mix and sponsor-equity as unresolved.
- **[O-23]** (26) Why do two small EU regions with same per-capita 2021-2027 cohesion disbursement show 3× business-births gap 24 months later? — *EU ARDECO + Eurostat NUTS-3 business demography (2026) + State Aid Register + EU Cohesion Open Data Platform (2026-Q1 refresh) + Orbis Europe* — Why open: Cohesion Open Data Platform mid-term update Feb 2026; Commission 9th Cohesion Report follow-up Mar 2026 flags absorption-vs-outcome decoupling; Bruegel 27 Mar 2026 WP.

### Wildcard physical sciences (P) — new

- **[P-13]** (29) Why did this SSW crash the polar vortex and the next one barely nudge surface weather? — *NOAA CPC SSW diagnostics + ERA5 + MERRA-2 + NASA MLS + WACCM/E3SM open ensembles + NOAA CDO surface records* — Why open: Jan 2026 SSW split vortex + seeded Jan-Feb 2026 NA cold wave (≥22 deaths, ≥$4B); second major SSW 5 Mar 2026 with far weaker coupling; wave-1 vs wave-2 mechanism openly debated.
- **[P-14]** (28) Why did the Santorini-Amorgos 2025–26 swarm produce 30,000 quakes but no eruption, while smaller Reykjanes swarms kept erupting? — *EMSC + USGS ANSS + IMO SIL + ISMOSAV + Sentinel-1 InSAR + EPOS/ORFEUS GNSS + NOA broadband* — Why open: Feb 2026 papers reconstructed 13 km dike under Santorini (0.31 km³, emergency lifted 3 Mar 2026); Reykjanes swarms restarted 20-23 Mar 2026; Campi Flegrei AI paper (Stanford 2026) adds third case. "Dike-stalling vs erupting" is the open mechanism.
- **[P-15]** (27) Why is 2026 producing a fireball every three days with a sonic boom — orbital-debris re-entries, Taurid resonance, or detection bias? — *NASA CNEOS fireball log + AMS event reports + GOES-R GLM bolide detections (L2 open) + ESA DISCOS re-entry log + CAMS all-sky + USArray infrasound* — Why open: NASA 26 Mar 2026 blog reports 30/38 large events in Q1 2026 with sonic booms; Cleveland/Ohio bolide 17 Mar 2026 (CNN); attribution between natural influx vs Starlink/Kosmos re-entry unresolved.
- **[P-16]** (26) Can you predict which coast will "hear" a Pacific tsunami hours before tide gauges, using GNSS signals the way GUARDIAN did for Kamchatka? — *NASA JPL GUARDIAN TEC stream + IGS/UNAVCO/SOPAC raw GNSS + NOAA DART + NOAA tide gauges + USGS/NEIC MT + Madrigal TEC* — Why open: GUARDIAN detected the 29 Jul 2025 M8.8 Kamchatka tsunami 32 min before Hawaii gauges; arXiv 2509.00631 extended with open "ionopy" code.
- **[P-17]** (26) Why king-tide + AR compound floods wrecked some Marin/Bay Area blocks and spared neighbours one street away? — *NOAA CO-OPS tide gauges + USGS streamflow + Copernicus S-1/2 + California King Tides Project + NOAA NWM + FEMA NFHL + CA DWR ARkStorm* — Why open: Jan–Feb 2026 records; Hwy 101 submerged Corte Madera; NOAA 2025-26 high-tide-flood outlook (4-9 day median) calls compound attribution open; block-level variance is classic "why-neighbours-differ" setup.

### Ireland-specific (IE) — new

- **[IE-25]** (28) Predict which Irish ED will break its trolley record next — from admissions, staffing, bed occupancy, and respiratory-virus surveillance. — *INMO Trolley Watch (daily, per-hospital since 2004) + HSE Open Data Portal bed occupancy + HPSC respiratory surveillance + CSO population by CHO + HIQA inspections* — Why open: INMO Mar 2026 worst-ever February (11,595 trolley patients); UHL topped with 1,978; 90-year-old 45 h on a chair (RTÉ 13 Jan 2026); 2026 Waiting List Action Plan being finalised; hospital-level mechanism uncharacterised.
- **[IE-26]** (28) Where will Ireland's next GP-desert emerge — predict which Eircode loses its only practice within 24 months? — *ICGP workforce census 2026 + HSE PCRS panel lists (GMS) + CSO population projections + Medical Council retention + Pobal HP Deprivation* — Why open: ICGP told RTÉ (27 Mar 2026) Ireland has 4,600 GPs, needs >6,000; patients unable to register; ESRI 25 Feb 2026 projects +1.2M people by 2050; mechanism quantifiable.
- **[IE-27]** (27) Predict which Irish LEA is next for measles/pertussis outbreak — from MMR uptake, age structure, importation routes. — *HPSC weekly surveillance + HSE immunisation by HSE area + CSO LEA pyramids + Dublin/Rosslare traveller volumes + ECDC outbreak map* — Why open: MMR fell to 87.6% at 24 months vs WHO 95% threshold; 16 measles + 48 pertussis YTD 2026; HPSC Jan 2026 guidelines + Easter 2026 advisory; LEA-level open data resolves it.
- **[IE-28]** (27) Which Irish coastal property will be lost to erosion within 10 years — predict from LIDAR shoreline-change, wave exposure, defence type. — *Tailte Éireann LIDAR (2023 open) + GSI Coastal Vulnerability + Marine Institute wave buoys + OPW ICPSS + CSO property transactions + CORINE* — Why open: RTÉ Brainstorm 26 Feb 2026 ranked Maharees + Wexford as Very High; Rosslare residents warned 3 Apr 2026 of imminent loss (€7.6M scheme); Storm Chandra (27 Jan 2026) + Éowyn aftermath; no public property-level product. Distinct from IE-10/IE-18 (pluvial/fluvial).
- **[IE-29]** (26) Predict which Irish shellfish production area closes next for biotoxins — from Dinophysis counts, SST, upwelling. — *Marine Institute Shellfish Biotoxin Monitoring (weekly open) + Copernicus Marine SST/chl-a + Marine Institute phytoplankton + EMODnet + Met Éireann wind* — Why open: Dinophysis acuta/acuminata drive most Irish mussel closures; 2025 prolonged Bantry/Killary/Castlemaine shutdowns (€4M+/yr); 2026 data live on marine.ie.

### Europe-wide (EU) — new

- **[EU-29]** (30) Predict where European aircraft will lose GNSS signal next — which Baltic/Black Sea corridor, hour, and altitude will jam? — *GPSJam.org daily NACp maps + Flightradar24 GPS-jamming layer + EASA Conflict Zone Bulletins + EUROCONTROL Network Manager + OpenSky archive + ERA5/space-weather covariates* — Why open: EASA + EUROCONTROL joint Action Plan 26 Mar 2026 synthesises 156 confirmed aviation incidents; interference 1,500+ km from conflict zones; mechanism (emitter × propagation × altitude × TOD) is THE open operational question. Overlaps T-21 (aircraft-level) but EU-wide perspective.
- **[EU-30]** (29) Predict which European imports face the biggest CBAM cost shock — can embedded carbon be forecast from trade flows + origin grid mix before 2027 surrender? — *EU CBAM Transitional Registry + Eurostat Comext + EMBER open electricity (origin grid CO2) + IEA-equivalent open steel/cement benchmarks + EU ETS price history* — Why open: CBAM definitive phase 1 Jan 2026; first annual declaration due 31 May 2027 with €100/t penalty; 90%+ importers exempted but covered volume ≈ 99% of emissions; product-level mechanism uncharacterised.
- **[EU-31]** (29) Predict which European dairy region is highest-risk for H5N1 bovine spillover after first Dutch cow detection — from waterfowl overlap, herd density, biosecurity. — *ECDC/EFSA AI overview Dec 2025–Feb 2026 + EMPRES-i (open) + eBird/GBIF migratory waterfowl + Eurostat livestock + Copernicus land cover + WAHIS* — Why open: EFSA Feb 2026 reports 2,514 HPAI A(H5) detections in 32 countries Nov 2025–Feb 2026; first wild-bird-to-dairy-cow antibody spillover in NL (ECDC Feb 2026); risk open; mechanism is the exact HDR framing.
- **[EU-32]** (28) Predict which Med province will be hit by the next red-alert flash flood cascade from EFAS + ML on 2025–26 storm cluster. — *EFAS v5.5 (open Sep 2025) + Copernicus EMS Rapid Mapping + ESWD + Protezione Civile + AEMET + IPMA + Météo-France Vigilance + ERA5* — Why open: Storm Harry (16 Jan 2026) + Francis (late Jan 2026) killed 13+ across ES/PT/S-FR/IT with 290 mm records; Catalonia red warnings; JRC EFAS solicits ML post-processing research; mechanism (AR orientation × orography × antecedent soil moisture) open.
- **[EU-33]** (28) Predict which European city flips from "rent-affordable" to "rent-crisis" within 12 months — from 100M scraped listings + demographics + tourism pressure. — *ESPON House4All (~100k cities, Mar 2024–Mar 2025, open via CORRECTIV) + Eurostat house-price/rent Q4 2025 (released 7 Apr 2026) + OECD Affordable Housing + Eurostat tourism + Copernicus Urban Atlas + FEANTSA 2025* — Why open: EP motion 24 Mar 2026 on housing crisis; Eurostat Apr 2026 +64.9% prices since 2015 (+290% HU, +180% PT), +21.8% rents; ESPON House4All first pan-European scraped-listings dataset.
