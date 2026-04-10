# Knowledge Base: Irish BER vs Real Home Energy Gap

## 1. The BER System and DEAP Methodology

### What is a BER?
A Building Energy Rating (BER) is Ireland's implementation of the EU Energy Performance Certificate (EPC) required by the Energy Performance of Buildings Directive (EPBD). Every dwelling offered for sale or rent in Ireland since 2009 must have a BER. The rating runs from A1 (most efficient, <25 kWh/m2/yr) to G (least efficient, >450 kWh/m2/yr) and is calculated using the Dwelling Energy Assessment Procedure (DEAP).

### How DEAP Calculates Energy
DEAP is a quasi-steady-state monthly energy balance model based on ISO 13790 and EN 15603. It calculates:

1. **Space heating demand** = Heat losses - Heat gains
   - Heat losses = Fabric loss (U-values x areas x delta-T) + Ventilation loss (air changes x volume x delta-T)
   - Heat gains = Solar gains (window g-values x areas x irradiance) + Internal gains (fixed at ~3.4 W/m2 for domestic)
   - Delta-T based on degree-day method: standard external temperatures from Met Eireann, standard internal temperature 20.0C (living) / 18.0C (rest of dwelling)

2. **Water heating demand** = f(occupancy, daily hot water use) - fixed formula based on floor area

3. **Delivered energy** = Demand / System efficiency
   - Boiler seasonal efficiency from HARP database or defaults
   - Heat pump COP (Coefficient of Performance) from MCS database or defaults
   - Distribution and storage losses from standard factors

4. **Primary energy** = Delivered energy x Fuel factor
   - Gas: 1.1, Oil: 1.1, Electricity: 2.08 (reflecting grid carbon intensity)
   - The BER Energy Value in kWh/m2/yr is the primary energy divided by floor area

### Key Standard Assumptions in DEAP
- Internal temperature: 20.0C living areas, 18.0C elsewhere
- Occupancy: derived from floor area (approximately 2.5 people for typical 100m2 house)
- Heating schedule: 16 hours/day in living areas, 7 hours/day elsewhere
- Hot water: function of floor area (approximately 50-80 litres/day for typical house)
- Climate: standard regional data (one of 14 weather stations)
- Ventilation: based on declared air permeability or default (typically 7-10 m3/h/m2 at 50 Pa for older homes)

These standardized assumptions are the PRIMARY reason for the performance gap. Real occupants do not behave like the DEAP standard occupant.

## 2. The Performance Gap: Prebound and Rebound

### Definitions
- **Performance gap**: the difference between DEAP-calculated energy and actual metered energy
- **Prebound effect** (Sunikka-Blank & Galvin 2012): occupants of poorly-rated homes use LESS energy than DEAP predicts, because they under-heat to save money or tolerate cold. Ratio of actual/predicted < 1 for low-rated homes. Irish evidence: Coyne & Denny 2021 found prebound factors of 0.45-0.65 for E-G rated homes.
- **Rebound effect** (Sorrell 2009): occupants of well-rated homes use MORE energy than DEAP predicts, because they heat the whole house to comfortable temperatures, keep heating on longer, or increase setpoint. Also called "comfort taking" (Oreszczyn 2006) or "take-back effect" (Galvin & Sunikka-Blank 2016). Rebound ratios of actual/predicted > 1 for A-C rated homes.
- **Net convergence**: the combination of prebound (low-rated use less than predicted) and rebound (high-rated use more than predicted) means actual consumption is much more compressed across rating bands than BER predicts. An A-rated Irish home might use 8,000-12,000 kWh/yr while a G-rated home uses 12,000-20,000 kWh/yr — a factor of 1.5-2.5x, not the 5-10x that BER ratings would suggest.

### Coyne & Denny 2021 Key Findings (Irish BER + Smart Meter Data)
- Matched ~3000 BER certificates to CER smart meter trial electricity data and gas meter data
- Found prebound effect: E-G rated homes used 35-55% less energy than BER predicted
- Found rebound effect: A-B rated homes used 10-30% more energy than BER predicted
- The gap was largest for space heating and smallest for hot water
- Building vintage (year built) was the strongest predictor of the gap
- Rural homes had larger performance gaps than urban homes (different heating patterns)

## 3. Irish Housing Stock Characteristics

### Construction Periods and Typical Features
- **Pre-1940**: Solid stone/brick walls (U ~ 1.5-2.5 W/m2K), single-glazed windows, no insulation. ~15% of stock. Mostly terraced in cities, detached farmhouses in rural areas.
- **1940-1966**: Solid concrete block walls (U ~ 1.2-2.0), early cavity walls in later period. ~10% of stock.
- **1967-1977**: Cavity block construction begins, typically unfilled. First building regulations (1972). ~12% of stock. The "worst generation" — large detached houses with cavity walls that are easy to insulate but were built without any.
- **1978-1991**: First insulation requirements (Part L 1978). Partial cavity fill, some attic insulation. ~18% of stock.
- **1992-2005**: Improved Part L standards. Full cavity fill, double glazing, attic insulation. ~25% of stock. Celtic Tiger era — large houses, often poorly supervised construction.
- **2006-2010**: BER requirement introduced (2006). Significantly improved insulation standards. ~10% of stock.
- **2011-present**: nZEB pathway. SI 426 (2019) requires near-zero energy for new builds. ~10% of stock. Heat pumps, MVHR, triple glazing becoming standard.

### Heating Systems
- **Oil boilers**: ~37% of stock (2024), declining. Dominant in rural areas. Typical DEAP efficiency 85-91%.
- **Gas boilers**: ~34% of stock, mostly urban. Typical DEAP efficiency 89-96% (condensing).
- **Solid fuel**: ~12% (coal, peat, wood). Declining rapidly. DEAP efficiency 50-70%.
- **Heat pumps**: ~8% and growing rapidly. DEAP COP 2.5-4.5. Grant-supported since 2018.
- **Electric storage/panel heaters**: ~7%. Common in apartments.
- **Other (district, biomass, solar thermal)**: ~2%.

### BER Rating Distribution (~1M certificates as of 2024)
- A1-A3: ~3% (almost all post-2019 new builds)
- B1-B3: ~12% (recent builds, some deep retrofits)
- C1-C3: ~25% (improved existing stock, modern builds pre-nZEB)
- D1-D2: ~28% (most common — moderate existing stock)
- E1-E2: ~18% (older stock, some improvements)
- F: ~9% (poor existing stock)
- G: ~5% (worst existing stock, pre-1940s unrenovated)

## 4. DEAP Model Sensitivities

### What Drives the BER Energy Value?
In descending order of typical sensitivity:
1. **Wall U-value** (largest single contributor to fabric heat loss for Irish housing)
2. **Heating system efficiency** (boiler type determines how much fuel per unit of heat)
3. **Air permeability** (ventilation heat loss is 30-50% of total in older homes)
4. **Floor area** (energy value is per m2, but absolute demand scales with area)
5. **Window U-value and g-value** (heat loss AND solar gain both matter)
6. **Roof insulation** (easy and cheap to improve — most homes already have some)
7. **Floor insulation** (often missing but smaller contributor than walls)
8. **Hot water system** (secondary contributor — 15-25% of total energy)
9. **Lighting** (small contributor in residential — ~5%)
10. **Climate zone** (western Ireland has higher HDD and lower solar than southeast)

### Known DEAP Biases
- **Overestimates heat loss through solid walls**: DEAP uses tabulated U-values that assume worst-case; in-situ measurements show 20-40% lower U-values (Byrne et al 2019)
- **Underestimates beneficial thermal mass**: Monthly steady-state method doesn't capture thermal mass benefits of heavy construction
- **Assumes standard occupancy**: Real occupancy density varies hugely (student houses vs elderly couples)
- **Assumes standard temperatures**: Irish homes are typically heated to 18-19C, not the 20-21C DEAP assumes (Humphreys et al 2015, Orr et al 2009)
- **Does not model part-house heating**: Many Irish households only heat the living room, not the whole house
- **Defaults are pessimistic**: When an assessor cannot determine a value, DEAP defaults to the worst plausible case

## 5. Retrofit Effectiveness: What Works?

### Measures Ranked by Typical BER Impact
1. **External wall insulation**: Largest BER improvement for worst-rated homes. Typical improvement 100-200 kWh/m2/yr. Cost €8,000-15,000 for semi-D.
2. **Cavity wall insulation**: Cheapest per kWh saved. Improvement 50-100 kWh/m2/yr. Cost €1,000-2,500.
3. **Heat pump installation**: Replaces oil/gas boiler. Improvement 50-150 kWh/m2/yr. Cost €8,000-16,000. Requires good fabric to work well.
4. **Attic insulation upgrade**: To 300mm+ from typical 50-100mm. Improvement 20-50 kWh/m2/yr. Cost €500-2,000.
5. **Window replacement**: Double to triple glazing. Improvement 20-40 kWh/m2/yr. Cost €5,000-15,000.
6. **Solar thermal panels**: Hot water contribution. Improvement 10-30 kWh/m2/yr. Cost €3,000-5,000.
7. **Demand-controlled ventilation**: Improvement 10-20 kWh/m2/yr. Cost €3,000-6,000.

### The Retrofit-Reality Gap
SEAI grant data shows that actual energy savings from retrofits are typically 50-70% of BER-predicted savings (Rouleau et al 2019). Reasons:
- Prebound effect: the "baseline" consumption was already lower than BER predicted, so the improvement is smaller in absolute terms
- Rebound effect: after retrofit, occupants increase comfort (higher temperatures, more rooms heated)
- Installation quality: thermal bridges, gaps, workmanship issues reduce real performance
- Real U-values differ from designed U-values

## 6. The Radon-BER Tension

The EPA UNVEIL project (2024) documented that energy-efficient retrofits can increase indoor radon concentrations by reducing ventilation rates. This creates a tension:
- Better BER requires better airtightness
- Better airtightness reduces air changes per hour
- Reduced air changes can trap radon from soil gas
- High radon risk areas (granitic bedrock — parts of Wicklow, Galway, Donegal, Castlebar) are most affected
- Mitigation requires mechanical ventilation with heat recovery (MVHR), which adds cost and complexity

## 7. What We CAN and CANNOT Claim

### CAN claim:
- What building characteristics predict the DEAP-calculated BER Energy Value
- Which features the DEAP model is most sensitive to
- How BER ratings vary by geography, building age, and construction type
- Which retrofit combinations produce the largest BER improvements
- Whether assessor effects exist in the data (systematic rater differences)

### CANNOT claim:
- Direct measurement of the performance gap (we don't have matched BER + metered data)
- Causal effects of retrofits on actual energy consumption
- That improving BER rating by N kWh/m2/yr will reduce actual energy bills by N kWh/m2/yr
- Individual-level predictions of household energy consumption

### The honest framing:
This project builds a surrogate model of the DEAP calculation engine and uses it to understand what the BER system measures, what it rewards, and where its predictions are most likely to diverge from reality. We rely on published performance gap studies (especially Coyne & Denny 2021) to interpret our findings in the context of actual energy use.
