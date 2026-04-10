# Knowledge Base: Iberian Blackout Cascade Prediction

## Established Facts

### The Event
- **Date**: 28 April 2025, 12:33 CEST
- **Affected**: 31 GW disconnected (25.2 GW Spain + 5.9 GW Portugal), ~47 million people
- **Duration**: ~10 hours most areas; full restoration 04:00 April 29 (Spain), early April 29 (Portugal)
- **Classification**: ENTSO-E Incident Classification Scale 3 — worst in Continental Europe in 20+ years

### Pre-Blackout Grid State (12:30 CEST)
- Total generation: 32 GW
- Demand: 25 GW
- Solar PV: ~19.5 GW (59% of generation)
- Wind: 3.6 GW (12%)
- Nuclear: 3.3 GW (11%)
- Gas: 1.6 GW (5%)
- Hydro + other renewables: ~4.2 GW (13%)
- Exports: 2.6 GW to Portugal, 0.87 GW to France, 0.78 GW to Morocco
- Hydro-pumping consuming: 3 GW
- Spot price: approximately -1 EUR/MWh (negative!)

### Cascade Sequence (ENTSO-E Final Report, March 2026)
1. **12:03-12:07**: First inter-area oscillation (0.2 Hz between Iberia and rest of Europe), detected and damped
2. **12:16-12:22**: Second inter-area oscillation, detected and damped
3. **12:32:00-12:32:48**: ~500 MW large renewable plants reduced output; fixed power factor operation caused proportional reactive power drop, boosting voltage
4. **12:32:57**: 400/220 kV transformer near Granada tripped on overvoltage, severing 355 MW
5. **12:33:16**: Badajoz region lost 727 MW solar/CSP
6. **Within 2 seconds**: Additional 928 MW disconnected across five provinces
7. **12:33:18-21**: Frequency dropped below 48.0 Hz; automatic load shedding activated
8. **12:33:19**: Spain and Portugal lost synchronism with European grid
9. **12:33:21**: AC lines France-Spain tripped
10. **12:33:24**: Complete grid collapse; HVDC France-Spain disconnected

### Root Cause Analysis (ENTSO-E Final Report)
- **Primary mechanism: OVERVOLTAGE CASCADE** — NOT primarily an inertia problem
- "Even with significantly higher inertia values, the loss of system synchronism would not have been avoided"
- Voltage exceeded 435 kV during cascade (vs recommended 380-420 kV operating range)
- Conventional generators achieved <75% of required reactive power output at critical moments
- Many renewable installations in fixed power factor mode — no dynamic voltage support
- Shunt reactors (reactive power absorbers) were available but not activated during voltage rise
- Manual connection/disconnection of voltage control equipment slowed response
- Some renewable protection settings had overvoltage thresholds below regulatory limits
- Rooftop solar (<1 MW) had incomplete production data — blind spot for TSO

### Key Insight: Novel Failure Mode
- **First-ever overvoltage-driven cascading blackout in Continental Europe synchronous area**
- Previous blackouts (Italy 2003, Turkey 2015) were under-frequency events
- This was an OVER-voltage event — fundamentally different mechanism
- High solar + low demand + high exports = lightly loaded lines = voltage rise
- Fixed power factor renewable generation worsened voltage when output changed

## What Works
- Physics-informed features outperform raw statistics
- Composite risk score (renewable fraction + solar fraction + sync fraction) gives AUC-ROC 0.91
- Voltage stress proxy captures the actual mechanism better than inertia proxy
- Feature interactions (solar × low_sync) are strong predictors

## What Doesn't Work
- Inertia alone is NOT a sufficient predictor (ENTSO-E report explicitly states this)
- Simple renewable penetration fraction misses the voltage mechanism
- Daily granularity loses the sub-second cascade dynamics
- Without reactive power measurements, we rely on proxies

## Open Questions
- Can sub-hourly demand data improve prediction?
- What threshold of solar fraction becomes dangerous?
- Does the combination of negative prices + high solar + low sync define a "danger zone"?
- Can we reconstruct voltage conditions from generation mix alone?
- How does interconnector flow direction affect cascade propagation?
