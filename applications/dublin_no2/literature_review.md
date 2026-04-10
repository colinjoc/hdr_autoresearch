# Literature Review — Dublin/Cork NO2 Source Attribution

## 1. Domain Fundamentals: NOx Chemistry and Atmospheric Transport

Nitrogen dioxide (NO2) is a secondary criteria pollutant formed primarily through the oxidation of nitric oxide (NO) by ozone (O3) in the troposphere [1, 2]. The Leighton relationship governs the NO-NO2-O3 photostationary state: NO emitted from combustion sources reacts rapidly with O3 to form NO2, which is then photolysed by ultraviolet radiation back to NO [38, 39]. In urban areas near emission sources, the NO2/NOx ratio is determined by the balance between fresh NO emissions, available O3, and photolysis rates [40].

The atmospheric lifetime of NO2 is approximately 1 day, making it a relatively local pollutant compared to O3 or CO2 [1]. Dispersion depends on wind speed, mixing height (boundary layer height), atmospheric stability, and precipitation [4, 56, 57]. Temperature inversions, common on calm winter nights, trap pollutants near the surface and produce the highest NO2 episodes [59].

Key textbook references: Seinfeld and Pandis [1] provide the definitive treatment of atmospheric chemistry and physics. Finlayson-Pitts and Pitts [2] cover tropospheric chemistry in detail. Jacob [4] gives an accessible introduction to atmospheric transport. Wilks [5] covers statistical methods applicable to air quality data analysis.

## 2. Health Effects and Regulatory Framework

The WHO revised its air quality guidelines in 2021 [6], reducing the annual NO2 guideline from 40 to 10 ug/m3 and the 24-hour guideline from 200 to 25 ug/m3. This was based on meta-analyses showing associations between long-term NO2 exposure and cardiovascular mortality [22], respiratory disease [21], and childhood asthma [23]. The ESCAPE cohort study [124] found significant mortality associations at concentrations well below the previous guidelines.

The EU Air Quality Directive [7] sets the annual limit at 40 ug/m3, with a 2024 revision [8] targeting 20 ug/m3 by 2030. This creates a three-tier compliance challenge for Dublin: (1) the current EU limit of 40 ug/m3 is met, (2) the 2030 EU target of 20 ug/m3 is not met at traffic stations, and (3) the WHO guideline of 10 ug/m3 is not met at any urban station.

Ireland's EPA annual air quality reports [9, 10, 11] document this gap. The 2024 report projects Ireland at only 78% compliance with 2030 EU NO2 limits [110]. The National Emission Ceilings Directive [109] sets additional sector-level NOx emission targets.

## 3. Emission Sources: Traffic, Heating, Shipping

### Traffic

Diesel vehicles are the dominant urban NO2 source in European cities [24, 25, 152]. Real-world NOx emissions from diesel cars exceed type-approval values by factors of 3-10, a gap exposed by the Volkswagen dieselgate scandal [207] and systematically documented by the International Council on Clean Transportation [77, 208]. Euro 6d regulations significantly reduced this gap [76], but fleet turnover is slow -- the Irish fleet average age is approximately 8 years [126].

The relationship between traffic count and roadside NO2 is well established [130, 133]. Rush hour peaks at 7-9am and 4-7pm produce the highest hourly concentrations, with weekday/weekend contrasts of 10-20% at kerbside stations [131, 132]. Heavy-duty vehicles (trucks, buses) contribute disproportionate NOx per vehicle-km [190].

### Residential Heating

Ireland has a distinctive heating emission profile due to widespread use of solid fuels (coal, peat, wood) for residential heating [30, 103, 163]. The nationwide smoky-coal ban [70] addressed PM2.5 but smokeless coal, peat briquettes, and wood stoves still produce NOx [160, 161, 203]. The heating contribution is seasonal (October-March), temperature-dependent, and peaks in the evening (17-22h) when residents light fires [162].

### Shipping

Dublin Port handles approximately 30 million tonnes of cargo annually [125]. Ships at berth run auxiliary diesel engines, emitting NOx [28, 29, 80]. The contribution is spatially concentrated -- significant within 1 km of berths but diluted by distance [191]. Cold-ironing (shore power) can eliminate berthing emissions [79, 192]. Dublin Port's 2040 Masterplan includes electrification [100, 193].

## 4. Machine Learning for Air Quality Prediction

Machine learning, particularly gradient-boosted decision trees (XGBoost [41], LightGBM [42]), has become standard for urban NO2 prediction [46, 47, 48]. These methods capture nonlinear relationships between meteorological features and NO2 that linear models miss [145, 146].

The "deweathering" approach [13, 94, 95] uses random forests or gradient boosting to separate the meteorological signal from the emission trend, enabling trend analysis without confounding by weather variability. Carslaw and Taylor [13] pioneered this for UK NO2 data; Grange and Carslaw [95] refined it with random forest deweathering.

For source attribution, feature importance from tree models provides a complementary approach to traditional receptor models (Positive Matrix Factorization [16, 17], Chemical Mass Balance [18], UNMIX [19]). While receptor models decompose chemical speciation profiles, feature importance decomposition identifies which temporal and meteorological patterns drive NO2 variation -- which can then be linked to source categories [92].

SHAP values [93] provide more nuanced feature attributions than gain-based importance, but gain-based importance is sufficient for the coarse source categories (traffic, heating, port, background) used here.

## 5. Spatial Modelling and Satellite Data

Land-use regression (LUR) [50, 51] models spatial NO2 variation from traffic density, building density, and land use. The ESCAPE study [51] developed LUR models across 36 European areas. These complement monitoring-station-based approaches by providing spatial predictions between stations.

Sentinel-5P TROPOMI [52, 165] provides daily satellite-derived tropospheric NO2 column density at approximately 5.5 x 3.5 km resolution [53]. Goldberg et al. [53] demonstrated TROPOMI's ability to resolve urban NO2 hotspots. However, column-to-surface conversion requires air mass factor correction [55] and is uncertain in complex terrain. Validation against ground stations [54] shows moderate correlation (R approximately 0.5-0.7).

## 6. Irish Air Quality Studies

Dublin-specific studies include Williams et al. [31] on spatial and temporal NO2 patterns, showing Pearse Street as consistently the highest NO2 station. McNabola et al. [102] measured personal NO2 exposure among Dublin commuters, finding cyclists exposed to lower concentrations than car occupants despite being closer to traffic. Buckley et al. [101] monitored kerbside NO2 at Dublin traffic sites.

Whelan et al. [34] analysed COVID-19 lockdown effects on Dublin air quality, finding significant NO2 reductions -- the natural experiment that motivates our source attribution approach. Siew et al. [32] modelled population exposure across Ireland. Goodman et al. [33] analysed 2013-2022 NO2 trends and social equity dimensions [183].

Cork has received less attention despite having traffic stations with comparable NO2 levels [129]. The Cork Metropolitan Area Transport Strategy [158] includes air quality as a co-benefit of modal shift.

## 7. Related Problems: Congestion Charging and Low-Emission Zones

London's congestion charge [118] reduced central London NOx emissions by approximately 12% in the first year. Stockholm's congestion charge [185] achieved similar benefits. Low-emission zones (LEZs) across European cities [119, 120] show NO2 reductions of 3-8% within the zone. Zero-emission zones [186] in Dutch cities demonstrate more ambitious approaches.

Modal shift from cars to public transport and active travel [187, 188] provides dual benefits: reduced vehicle emissions and improved population health. Green infrastructure [189] has limited impact on streetlevel NO2 but reduces population exposure. These cross-domain lessons are directly applicable to Dublin policy design.
