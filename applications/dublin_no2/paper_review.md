# Adversarial Peer Review: "Dublin and Cork NO2 Source Attribution: Traffic Dominates Guideline Exceedance, Validated by the COVID-19 Lockdown Natural Experiment"

**Reviewer recommendation: Minor revision**

---

## 1. Claims vs Evidence

**Severity: MAJOR**

1. **The COVID validation correlation (r = 0.974) is reported for 14 stations, but the paper only shows 6 stations' numbers in the COVID lockdown table (Section 3).** The claim "correlation r = 0.97 across 14 stations" is unverifiable from the paper text. Which 14 stations? The COVID validation plot (`covid_validation.png`) shows what appears to be all stations but several show near-zero or slightly positive change at rural/background stations, which would inflate a correlation driven by the large traffic-station drops. The scatter of model-predicted traffic drop versus observed total drop is never shown as an explicit scatter plot with the regression line -- only paired bars. Showing n=14 points with a fitted line and confidence interval would be far more convincing.

2. **The "traffic is the residual" method (NO2_traffic = measured - background - heating) is tautological for the COVID validation.** If the model defines traffic as "everything not explained by background and heating," and during COVID the total NO2 drops while background and heating stay roughly constant, then by construction the model's traffic component will drop by the same amount as the total measurement. The r = 0.97 correlation partially reflects this circularity. The paper partially acknowledges this ("the model's traffic contribution explains 45-78% of the observed COVID drop") but the headline r = 0.97 is presented without this caveat in the abstract.

3. **The weekday-weekend validation is internally inconsistent.** The paper reports "weekday NO2 is 15-38% higher than weekend at all urban stations" (Section 3) but the heading says "18-38%." More substantively, the "implied traffic %" column ranges from 39% (Blanchardstown) to 68% (Cork Old Station Rd), while the station-differencing estimates for the same stations range from 71% to 61%. These are systematically different (Blanchardstown: 39% vs 71%), and the paper's explanation ("the weekday-weekend method assumes weekend traffic is zero, but it is actually about 60% of weekday levels") is hand-waving. If corrected, a 39% implied traffic fraction with a 60% weekend-to-weekday traffic ratio would yield approximately 65% -- close to 71%, which is consistent. But the correction is not actually performed numerically for any station, so the claimed agreement is asserted, not demonstrated.

**Severity: MINOR**

4. Lough Navar shows a weekday/weekend ratio of 1.15 and "implied traffic %" of 32%. This is a rural station that should have near-zero traffic. The model does not explain why a rural station has 32% implied traffic from the weekday-weekend method. This anomaly is not discussed.

---

## 2. Scope vs Framing

**Severity: MINOR**

1. **The title promises "Dublin and Cork" but Cork receives minimal treatment.** Only one Cork station (Cork Old Station Rd) appears in the analysis tables. Cork South Link Road appears in the feature importance plot but is not discussed in the text. The paper is overwhelmingly a Dublin study with Cork added for geographic breadth. Either expand the Cork analysis or adjust the title.

2. **The paper frames itself as "source attribution" but is really "source apportionment by differencing."** True source attribution in atmospheric science typically involves emission inventories, dispersion modeling, or receptor models like PMF. The station-differencing method used here is a simpler empirical approach. The paper correctly categorizes it in Section 2 but the title and abstract use "source attribution" without qualification, which may mislead atmospheric scientists expecting a more rigorous methodology.

3. **The "every urban station exceeds WHO guidelines" framing is technically correct but potentially misleading.** The WHO annual guideline of 10 ug/m3 is extremely stringent -- most European cities exceed it. Framing this as a Dublin-specific finding obscures the fact that this is a Europe-wide (indeed, global) phenomenon. The paper should contextualize Dublin's exceedance within the European distribution more explicitly.

---

## 3. Reproducibility

**Severity: MINOR**

1. **Data sources are well-documented.** The EEA Zenodo dataset and Met Eireann data.gov.ie sources are cited with sufficient detail for reproduction. This is a strength of the paper.

2. **The station-differencing model is simple enough to reproduce from the description.** The three-component additive model (background + heating + traffic) with summer baseline and rural correction is clearly specified. However, the exact choice of which background stations are used for heating estimation (Ballyfermot, Clonskeagh, Tallaght) and which rural stations for background (Lough Navar, Moate) could affect results. A sensitivity analysis using different station subsets would strengthen the claim.

3. **No code repository is mentioned.** While the method is simple, providing code would enable exact reproduction.

---

## 4. Missing Experiments

1. **No wind-direction analysis.** The paper mentions Met Eireann wind data as an input but never uses wind direction to separate traffic from heating or to identify directional sources (e.g., port emissions, motorway plumes). A simple conditional bivariate probability function (CPF) or pollution rose would add substantial value.

2. **No diurnal analysis.** The paper states it uses "daily means" and acknowledges "hourly data would enable rush-hour analysis." This is a significant limitation given that the title claims traffic dominance. Rush-hour peaks (7-9 AM, 5-7 PM) versus off-peak versus nighttime patterns would provide strong independent confirmation of traffic attribution. The data appear to be available at hourly resolution (Met Eireann provides hourly data); is hourly NO2 also available?

3. **No trend analysis.** With 9 years of data (2015-2023), the paper could examine whether Dublin's NO2 is trending downward (as diesel fleet turnover proceeds), stable, or increasing. The 2019 vs 2022 comparison in the WHO exceedance table hints at a downward trend (Winetavern Street: 43.5 to 32.5 ug/m3) but this is not analyzed systematically. A Sen-Theil slope or segmented regression would be informative for policy.

4. **No population-weighted exposure estimate.** The paper notes that "traffic stations are positioned to capture worst-case roadside exposure" and that "population-weighted exposure would be lower." A crude population-weighted estimate using Census small-area population data and station Thiessen polygons would be more policy-relevant than station-level maxima.

5. **No PM2.5/NO2 ratio analysis.** The paper mentions that "PM2.5/NO2 ratios or SO2 co-measurements could help" distinguish heating fuel types. If the EEA dataset includes PM2.5 at any of the same stations, this analysis should be attempted, not just mentioned as future work.

6. **No formal uncertainty quantification on the attribution.** The three-component model propagates measurement uncertainty, station selection uncertainty, and temporal sampling uncertainty. None of these are quantified. At minimum, bootstrap confidence intervals on the attribution percentages would indicate how robust the 80% traffic figure at Winetavern Street is.

7. **No comparison of 2020 weather to 2019 weather.** The paper acknowledges meteorological confounding but does not quantify it. A simple comparison of March-June mean temperature, wind speed, and mixing height between 2019 and 2020 would bound the meteorological contribution to the observed COVID-era NO2 drop.

---

## 5. Overclaiming

**Severity: MINOR**

1. **"Validated by the COVID-19 Lockdown Natural Experiment" in the title is somewhat strong.** The COVID validation is suggestive but has the tautological structure noted in Section 1 above. "Supported by" or "consistent with" would be more precise than "validated by."

2. **"We conclude that diesel traffic is the primary target for NO2 reduction" (abstract).** The method attributes NO2 to "traffic" generically -- it cannot distinguish diesel from petrol, private cars from trucks, or buses from vans. The word "diesel" is an inference from the known emission characteristics of the Irish fleet, not a finding of this study. The conclusion should say "road traffic" and note that diesel is the likely dominant sub-source based on fleet composition data from external sources.

3. **The claim that "even complete elimination of traffic would leave several stations above the WHO guideline" is important but rests on the assumption that the heating and background components are independent of traffic.** If traffic generates local heating of road surfaces, disperses particulate matter that affects radiative forcing, or creates urban heat island effects that change boundary-layer mixing, then eliminating traffic could also reduce the heating and background components indirectly. This is a second-order effect and likely small, but the claim "even complete elimination" is absolute and should be qualified.

---

## 6. Literature Positioning

**Severity: MAJOR**

1. **The reference list has 15 entries, which is thin for a multi-year air quality study.** Notable omissions include: the EMEP MSC-W model documentation (the standard European atmospheric transport model for NO2); the DEFRA/AURN UK NO2 source apportionment studies that use the same station-differencing approach at London sites; the Carslaw and Ropkins (2012) openair R package paper, which provides standard tools for wind-direction-dependent source analysis; the Harrison et al. (2004) paper on NOx-to-NO2 oxidation chemistry in urban settings, which is relevant because the additive model assumes NO2 is conserved when in fact it is chemically reactive.

2. **The NO2 chemistry limitation is not discussed.** NO2 is not a conserved tracer -- it participates in photochemical cycling with NO and O3. At traffic stations, much of the emitted NOx is initially NO, which oxidizes to NO2 downwind. The additive background + heating + traffic model implicitly assumes NO2 behaves like a conservative pollutant. This is approximately correct for annual means but can be significantly wrong for hourly or daily values, especially in summer when photolysis is rapid. The paper should at minimum cite Seinfeld and Pandis (which is in the reference list but never cited in the text, reference [13]) and note this limitation.

**Severity: MINOR**

3. Reference [5] (Shi and Brasseur, 2020) is about Chinese air quality during COVID, not London as cited in the discussion ("comparable to those reported for London (-36%, [5])"). The London figure likely comes from a different study (e.g., Higham et al. 2021 or Jephcote et al. 2021). This is a citation error.

---

## Summary of Required Revisions

| Category | Critical | Major | Minor |
|----------|----------|-------|-------|
| Claims vs evidence | 0 | 2 | 1 |
| Scope vs framing | 0 | 0 | 3 |
| Reproducibility | 0 | 0 | 2 |
| Missing experiments | 0 | 7 | 0 |
| Overclaiming | 0 | 0 | 3 |
| Literature positioning | 0 | 2 | 1 |
| **Total** | **0** | **11** | **10** |

This is a well-structured applied environmental science paper with a clear narrative, appropriate use of real data, and a clever exploitation of the COVID natural experiment. The station-differencing method is simple and transparent, which is a virtue. The main weaknesses are: (a) the partial tautology in the COVID validation that should be explicitly addressed, (b) the missing wind-direction and diurnal analyses that would strengthen the attribution, (c) the thin literature review that omits key atmospheric chemistry considerations, and (d) the citation error for reference [5]. The paper is close to publishable in its current form and the revisions required are achievable without new data collection.
