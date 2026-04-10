# Knowledge Base: Irish BER Energy Gap

## Established Facts

### BER System
1. BER (Building Energy Rating) is Ireland's implementation of the EU Energy Performance of Buildings Directive (EPBD). Mandatory for sale/rental since 2009.
2. BER uses DEAP (Dwelling Energy Assessment Procedure), Ireland's national calculation methodology based on ISO 13790.
3. BER rating = primary energy in kWh/m²/yr. Bands: A1 (≤25) through G (≥450).
4. DEAP assumes standardised occupancy: 2.5 people, 21°C living room, 18°C other rooms, standard hot water demand. Real occupancy varies hugely.
5. DEAP calculates energy based on building fabric + systems, NOT measured consumption.

### The Energy Performance Gap (Literature)
6. The "energy performance gap" in literature refers to the difference between calculated (DEAP) and actual (metered) energy consumption.
7. Sunikka-Blank & Galvin (2012): Prebound effect — occupants of inefficient homes use less energy than calculated (they under-heat). Factor: 0.6-0.8x of calculated.
8. Galvin (2014): Rebound effect — occupants of efficient homes use more energy than calculated (they increase comfort). Factor: 1.2-1.5x of calculated.
9. Combined effect: A-rated homes use ~1.3x calculated, G-rated homes use ~0.6x calculated. The actual energy gap between best and worst is much smaller than the DEAP gap.
10. Moran et al. (2020): In Ireland specifically, the DEAP-to-actual gap is ~30-50% for poorly rated homes and ~10-30% for well-rated homes.

### Irish Housing Stock
11. ~2M dwellings in Ireland. ~1.37M have BER certificates (our dataset).
12. 82% of housing built before 2006 (pre-modern building regulations).
13. Dominant fuel types: Mains gas (34%), oil (33%), electricity (26%).
14. High electricity efficiency (>100%) indicates heat pump — COP 3-4 is common.
15. Pre-1978 buildings typically have uninsulated cavity walls (U-value ~1.5 W/m²K).
16. Post-2012 (nZEB era) buildings typically have U-value ~0.18 W/m²K.

### Key Physical Relationships
17. Heat Loss Parameter (HLP) = total fabric heat loss / floor area. Strongest single predictor of BER rating.
18. Window U-value is disproportionately important because windows have high U-values AND are hard to insulate.
19. Heating system efficiency separates gas/oil (~85%) from heat pumps (~300-400%).
20. Ventilation heat loss is ~30% of total in modern buildings (as fabric improves, ventilation share grows).

## Data Quality Findings
21. Dataset: 1,366,752 records, 211 columns. Real SEAI data, CC BY 4.0.
22. ~27,000 rows (~2%) skipped due to malformed TSV lines.
23. BER rating distribution: roughly normal, peaked around 150-250 kWh/m²/yr.
24. Year range: 1753-2104 (some clearly erroneous years).
25. BER band boundaries explain 79.2% of total BerRating variance (between-band). 20.8% is within-band.
26. Within-band correlations are weak (r < 0.07 for individual features) because bands are narrow (25 kWh/m²/yr wide).

## Model Tournament Results
27. Ridge (linear): MAE=32.28, R²=0.862 — strong linear signal.
28. Random Forest: MAE=20.22, R²=0.937 — significant nonlinear improvement.
29. XGBoost (GPU): MAE=19.26, R²=0.943 — best tree model.
30. HLP proxy is the single most important feature (27-58% importance depending on model).
31. Heat pump status and fuel type are the second most important feature group.
32. Window U-value third most important.

## Observations
33. The research question "why does an A-rated home use almost the same energy as a G-rated one" cannot be answered with BER data alone — BER gives calculated, not measured energy.
34. What we CAN answer: (a) What building characteristics determine the BER rating, (b) Which retrofits shift the calculated rating most, (c) What the within-band variation tells us about building diversity.
35. The more scientifically precise question for this dataset: "What determines a dwelling's DEAP-calculated energy performance, and which building characteristics offer the largest marginal improvement?"
