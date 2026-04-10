# Knowledge Base — DART Punctuality Cascade Prediction

## 1. DART Network Topology

### 1.1 Route Structure
DART (Dublin Area Rapid Transit) serves Dublin and surrounding counties on the Irish Rail network. The system operates on three main corridors:
- **Northern line**: Malahide/Howth to Connolly (dual track, 1980s electrification)
- **City centre**: Connolly - Tara Street - Pearse - Grand Canal Dock (the bottleneck section)
- **Southern line**: Pearse to Bray/Greystones (dual track, some single-track sections south of Bray)

### 1.2 Key Stations and Junctions
- **Connolly Station**: Central hub. 1970s-era signalling system with mechanical interlocking. Handles DART, InterCity, and Commuter services. ~6 platform faces for DART. The junction between the Northern Line, the Maynooth Line, and the city centre throughput is the single biggest capacity constraint.
- **Tara Street**: Underground through station, dual track. Ventilation and passenger flow constraints.
- **Pearse Station**: Junction where DART services diverge to Dun Laoghaire line. Limited crossover capacity.
- **Grand Canal Dock**: New station (2001), serves the Docklands area. Limited reversing capacity.
- **Dun Laoghaire**: Formerly a terminus; now through station to Bray/Greystones.
- **Bray**: Dual-track section ends. Signalling transition point.
- **Greystones**: Southern terminus of DART. Turnaround point; limited siding capacity.

### 1.3 The Bray-Greystones Section
- Single-track section along the coast
- Exposed to easterly and south-easterly winds (Irish Sea)
- Speed restrictions imposed at wind speeds >50 km/h
- The cliffs at Bray Head create a microclimate — localised gusts can exceed anemometer readings from Dublin Airport
- Track flooding occurs during heavy rain + high tides
- Historically the most weather-sensitive section of the DART network

### 1.4 Signalling
- **Connolly area**: 1970s relay-based signalling, manual route setting in some areas
- **City centre throughput**: Colour-light signalling with limited headway (~3 min minimum)
- **Northern line**: Modern signalling north of Connolly (post-2000 upgrade)
- **Southern line**: Mix of older and newer signalling
- **No ETCS/ERTMS**: Ireland has not deployed the European Train Control System on DART

## 2. The 2024 Timetable Change

### 2.1 What Changed
In September 2024, Irish Rail introduced a new timetable for DART services. Key changes:
- **Increased service frequency**: Additional services during peak hours
- **Reduced turnaround times**: Buffer at Connolly and Greystones reduced from ~4 minutes to ~2 minutes
- **Tighter running time margins**: Recovery time between stations reduced
- **New stopping patterns**: Some services gained additional stops without increased running time

### 2.2 Consequences
- The reduced buffers meant that any delay at one end of the line propagated through the entire service pattern
- With no recovery margin, a 3-minute delay at Connolly would cause the return working to depart late, creating a knock-on cascade
- The increased service frequency placed higher demand on the already-constrained Connolly signalling
- Punctuality dropped from 92.8% (June 2024) to 64.5% (October 2024) — a 28.3 percentage point collapse

### 2.3 The Buffer Hypothesis
The dominant mechanism for the punctuality collapse is the reduction in timetable buffer times. This is supported by:
1. The temporal correlation (collapse immediately follows the timetable change)
2. The feature importance analysis (post_timetable_change is the #1 predictor)
3. The interaction with weather (post_change_x_wind is #2 — reduced buffers amplify weather sensitivity)
4. Published commentary from Irish Rail drivers and NBRU (National Bus and Rail Union) citing "unworkable timetable"
5. Partial recovery in 2025 after timetable adjustments restored some buffer time

## 3. Punctuality Definitions

### 3.1 Irish Rail Definitions
- **Commuter (DART)**: On-time = arriving within **5 minutes** of scheduled time
- **InterCity**: On-time = arriving within **10 minutes** of scheduled time
- **Monthly punctuality**: Percentage of scheduled services arriving on time, reported to the NTA

### 3.2 Our Definition
- **Bad day**: >15% of DART services delayed >5 minutes (equivalent to daily punctuality < 85%)
- **Cascading delay day**: A bad day where morning disruption propagates to afternoon — identified by morning_afternoon_gap feature

## 4. Weather Effects on DART

### 4.1 Wind
- Speed restrictions at 50+ km/h (yellow warning) on exposed sections
- Cancellations at 80+ km/h (red warning)
- Bray-Greystones most exposed; Howth Junction-Malahide moderately exposed
- Autumn-winter peak (Oct-Feb); prevailing south-westerlies less damaging than easterlies

### 4.2 Rain
- Rail adhesion problems (wheel slip) above ~10mm/day
- Signal failures from water ingress (older relay equipment)
- Track flooding on low-lying sections
- Combined rain + high tide causes sea wall overtopping at Bray Head

### 4.3 Temperature
- Frozen points below 0C (typically Dec-Feb, ~10-15 days per year in Dublin)
- Rail buckling above ~30C (very rare in Dublin; maybe 1-2 days per year)
- Frost reduces platform grip, slowing passenger boarding

## 5. Demand Patterns

### 5.1 Daily
- Morning peak: 07:00-09:30 (heaviest at 08:00-08:30)
- Evening peak: 16:30-19:00 (heaviest at 17:00-17:30)
- Inter-peak: ~30-40% of peak demand
- Weekend: ~30% of weekday demand

### 5.2 Seasonal
- School term (Sep-Jun): Highest demand
- School holidays (Jul-Aug): Lower commuter demand, some tourism demand
- Mid-term breaks: Demand dip
- Christmas/New Year: Very low demand (Dec 22 - Jan 3)

### 5.3 Events
- GAA matches at Croke Park: +10,000 passengers on Drumcondra/Connolly services
- Concerts at Aviva Stadium: +5,000 passengers on Lansdowne Road services
- Rugby internationals: Similar to concerts
- These events stress the already-constrained Connolly junction

## 6. Key Findings from Phase 2 HDR Loop

### 6.1 Feature Importance
1. The timetable change (post_timetable_change) is the dominant predictor (~49% importance)
2. Its interaction with wind speed (post_change_x_wind) is the second-strongest (~25%)
3. Morning punctuality is the strongest operational predictor (~11%)
4. All other features contribute <3% individually

### 6.2 The Cascade Mechanism
The model confirms a morning-to-afternoon cascade mechanism:
- A delay in the 06:00-08:00 window (captured by morning_punct) strongly predicts a bad afternoon
- The gap between morning and afternoon punctuality (morning_afternoon_gap) is itself predictive
- This cascade effect is AMPLIFIED by the reduced buffers post-September 2024

### 6.3 Day-of-Week Effects
- Monday is the worst day (risk 0.560 vs 0.410 Sunday)
- Friday is second-worst (risk 0.534) — possibly due to Friday evening leisure demand
- Weekends are best (Saturday 0.426, Sunday 0.410)
- This matches the school/work pattern exactly

### 6.4 Seasonal Pattern
- October-December highest risk (0.649-0.771)
- June-August lowest risk (0.288-0.314)
- September is the discontinuity point where the timetable change occurred
- January is elevated (0.471) due to winter weather + school return

### 6.5 Competing Explanations
- **(a) Timetable change**: DOMINANT. The strongest predictor by a factor of 2x.
- **(b) Connolly signalling**: Not directly testable from this data, but the timetable change EXPOSES the signalling limitation by demanding higher throughput.
- **(c) Weather sensitivity**: REAL but SECONDARY. Weather causes delays, but only in combination with reduced buffers does it cause cascading collapse.
- **(d) Rolling stock**: Not directly testable; would require fleet availability data.

### 6.6 Buffer Restoration
Counterfactual analysis shows that restoring pre-September 2024 buffer times would substantially reduce predicted bad days. The model estimates that the timetable change accounts for the majority of the June-October 2024 drop.
