# HDR Approachable-Showcase Pipeline

**Generated**: 2026-04-09
**Total candidates**: 140
**Selection criteria**: see "Rubric" below
**Companion file**: `active_queue.md` tracks the in-flight top 15

---

## Purpose

This is the canonical pool for the HDR "approachable showcase" track — projects whose goal is to demonstrate the methodology's range on questions that ordinary people understand and care about. Distinct from `project_candidates.md` (the ambitious physics tier: superconductors, fusion, QEC, gravitational waves) and `approachable_projects.md` (the older 2026-04-02 catalog of 120 generic ML benchmarks). This pool is built for newsworthy showcase projects with universal relatability.

The reference gold standard is the SUMO traffic-light waiting-time project: universally relatable, real open question, mechanism-revealing.

## Rubric

Every candidate scores 1–5 on six dimensions; bar = every dimension ≥3 AND total ≥24/30:

| Dim | 1 | 5 |
|---|---|---|
| **R** Relatability | needs glossary | universal experience |
| **I** Personal impact | 0.1% niche | most adults weekly |
| **N** Open-question novelty | textbook | unresolved active 2024–2026 |
| **M** Mechanism payoff | just a number | causal "because" |
| **D** Data/sim availability | need new equipment | public dataset/sim with URL |
| **S** Story-tellability | trade journal | front-page Reddit / The Guardian / Le Monde |

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
- **[P-4]** (28) Why same magnetic storm makes wildly different aurora shapes (STEVE, picket fence, spiral)? — *NASA Aurorasaurus open citizen science + THEMIS + SuperMAG + Swarm* — Why open: 2024 JGR Space Physics; "no solid consensus on shapes."
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
- **[IE-9]** (27) Predict the next "power-out-for-a-week" Irish storm outage (Darragh, Éowyn)? — *ESB PowerCheck + Met Éireann wind gust grids + Coillte tree cover + OSI line routes* — Why open: Storm Darragh Dec 2024 (395k outages); WWA 2024 attribution.
- **[IE-11]** (26) Predict the next Irish fodder-crisis drought (1976, 2018, 2022)? — *Met Éireann SMD + Teagasc PastureBase + Bord Bia cattle prices* — Why open: Noone et al 2025 Weather; compound prediction unsolved.
- **[IE-12]** (26) Does a rewetted Irish raised bog become a net carbon sink within 5 years — methane vs CO2? — *Bord na Móna LIFE + EPA Research 401 + Sentinel-2 LUCIP + NPWS* — Why open: Wilson et al 2022 GCB + Sci Reports 2024.
- **[IE-13]** (26) Did the Feb 2025 rural 80→60 km/h speed-limit cut actually reduce crashes — diff-in-diff? — *RSA Road Traffic Collision Data + CSO + TII counters* — Why open: 73% of 2020-24 fatalities on 80+ km/h rural roads.
- **[IE-15]** (25) What's driving the 33% Irish hen harrier decline since 2015 — forestry, wind farms, or burning? — *NPWS IWM No. 147 (Feb 2024) + Coillte forest age + EirGrid wind farms + Sentinel-2 burnt area (FLARES)* — Why open: NPWS 2022 Survey + Coillte July 2024 review.
- **[IE-14]** (24) Field-level liver fluke risk forecast — push from county to paddock scale? — *DAFM Animal Health Surveillance + Met Éireann SMD + Teagasc soil maps + NPWS wetland habitat* — Why open: DAFM Nov 2024 + 3 funded 2024 projects.
- **[IE-16]** (24) Predict which peat bog / gorse area in Ireland will burn this spring + carbon released? — *EPA Research 476 (FLARES) + Sentinel-2/3 fire + Met Éireann FWI + NPWS peatland inventory* — Why open: EPA FLARES 2024.
- **[IE-17]** (24) Why bovine TB resurged from 3.27% (2016) to 6.04% (2024) despite badger vaccine? — *DAFM TB surveillance + CSO cattle movement + DAFM badger sett register* — Why open: Byrne et al 2024 + Irish Vet Journal 2024.

### Europe-wide (EU)

- **[EU-1]** (29) Why did the 28 Apr 2025 Iberian blackout cascade as it did, and which grid states are one perturbation from collapse? — *ENTSO-E Transparency Platform + REE ESIOS API + ENTSO-E blackout report annex + PyPSA-Eur open simulator* — Why open: ENTSO-E March 2026 final report + Thlon & Brozek SSRN 2025.
- **[EU-2]** (29) Predict whether Po Valley fog persists all day or burns off — including aerosol-microphysics coupling? — *ERA5 Copernicus CDS + EEA AQ E1a/E2a + ARPA Lombardia + ARPA Emilia-Romagna + CAMS regional* — Why open: Pauli et al 2024 GRL + FAIRARI ACP 2025.
- **[EU-3]** (29) Predict Xylella appearance in Spanish/Italian olive groves 12 months ahead? — *Sentinel-2 NDVI/EVI + EFSA Xylella surveillance + EU Plant Health DB + E-OBS gridded* — Why open: Calderoni 2025 Plant Pathology (€132M Salento); Oct 2025 Cagnano Varano spread.
- **[EU-6]** (29) What predicts the "very large fire" transition in Iberian wildfires? — *EFFIS Copernicus + CAMS GFAS + ERA5 + Sentinel-2 burn scars + Corine* — Why open: EFFIS 2025 record season (1.08M ha); JRC explicitly calls for new modelling.
- **[EU-4]** (28) Predict European day-ahead electricity price spikes >€500/MWh during renewable droughts? — *ENTSO-E Transparency + ERA5 + Open Power System Data* — Why open: MDPI Energies 2025 review; <5% of papers cover post-2021.
- **[EU-5]** (28) Predict Alpine glacier summer mass loss — Saharan dust albedo vs temperature? — *GLAMOS 2025 + MeteoSwiss IDAWEB + ERA5-Land + Randolph Glacier Inventory* — Why open: GLAMOS 2025 (4th-worst year); 24% loss in 10 years.
- **[EU-8]** (28) Predict European eel glass-eel run — Gulf Stream vs freshwater habitat? — *ICES WGEEL recruitment index + Copernicus Marine GLORYS12 + GBIF Anguilla* — Why open: ICES 2025 zero-catch advice; Oxford ICES JMS 2025.
- **[EU-9]** (28) Separate pesticide / habitat / climate signals in 60% European farmland bird decline? — *PECBMS open indices + EBBA2 abundance grid via GBIF + Corine + EU CAP payments* — Why open: PECBMS State of Europe's Wild Birds 2025 (>300M birds lost).
- **[EU-11]** (28) What governs Atlantic windstorm intensification (Ciarán, Éowyn) — predict sting-jet occurrence? — *ECMWF IFS reforecasts + ERA5 + UK Met Office HadUK-Grid + KNMI Climate Explorer* — Why open: Volonté 2024 Weather + Reading 2024 + EGUsphere 2024.
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
