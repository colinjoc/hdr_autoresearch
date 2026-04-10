# Knowledge Base: Irish Radon Prediction

## Radon Physics Fundamentals

- **Radon-222 (Rn-222)**: Noble gas, half-life 3.82 days. Product of Ra-226 decay (itself from U-238 chain). Measured in Becquerels per cubic metre (Bq/m3).
- **Transport mechanisms**: Diffusion (concentration gradient, ~10^4 Bq/m3 in soil vs ~10^2 indoor) and advection (pressure-driven, stack effect, wind, mechanical ventilation).
- **Emanation coefficient**: Fraction of Rn atoms escaping mineral grains into pore space. Range: 0.05-0.40, depends on rock type, moisture, grain size.
- **Radon potential (Neznal formula)**: RP = C_soil / (-log10(k)), where C_soil = soil gas Rn concentration (kBq/m3) and k = soil gas permeability (m2). Categories: low (<10), medium (10-35), high (>35).
- **Indoor concentration steady state**: C_indoor = (Entry_rate) / (Ventilation_rate × Volume) + C_materials.
- **Seasonal variation**: Factor 2-5x. Winter peaks due to stack effect + closed windows. Summer lows due to open windows + weaker stack effect.
- **Measurement protocol**: 3-month integrated detectors (CR-39 or electret). Seasonal correction factors applied. Two detectors per home (living room + bedroom).

## Reference Levels Worldwide

| Country/Org | Reference Level (Bq/m3) | Notes |
|---|---|---|
| WHO | 100 | Recommended, "as low as reasonably achievable" |
| EU BSS | 300 | Maximum for member states |
| Ireland | 200 | RPII/EPA, since 1990 |
| UK | 200 | HPA/PHE |
| USA | 148 (4 pCi/L) | EPA action level |
| Canada | 200 | Health Canada |
| Norway | 200 | NRPA |
| Germany | 300 | BfS |
| Sweden | 200 | SSM |

## Irish Radon Statistics

- National geometric mean: ~89 Bq/m3
- National arithmetic mean: ~91 Bq/m3
- Percentage > 200 Bq/m3: ~7%
- Percentage > 100 Bq/m3: ~23%
- Maximum recorded: ~49,000 Bq/m3 (extreme outlier)
- Housing stock: ~2 million dwellings
- Measured homes: ~60,000 (~3% coverage)
- Estimated radon-attributable lung cancer deaths: ~250/year
- EPA grant for remediation: available, typical cost EUR 800-2,500

## High Radon Area (HRA) Designation

- Definition: >10% of homes predicted to exceed 200 Bq/m3
- Grid resolution: 10 km × 10 km
- Coverage: ~28% of Irish land area designated HRA
- Key limitation: too coarse for individual home prediction
- Within a single HRA cell, radon varies by >10x

## Geology-Radon Correlations for Ireland

### High-radon lithologies (ranked):
1. **Leinster Granite**: U = 5-20 ppm. Covers parts of Dublin, Wicklow, Wexford, Carlow, Kilkenny. Single largest radon source.
2. **Namurian/Dinantian black shales**: U = 10-50 ppm. Clare, North Kerry, parts of Limerick.
3. **Carboniferous limestone (karstified)**: U = 1-5 ppm BUT high permeability karst transport. Midlands, west, Burren.
4. **Devonian/Silurian metamorphics**: Moderate U but fractured. Parts of Waterford, Cork.
5. **Galway Granite**: Similar to Leinster but smaller extent.

### Low-radon lithologies:
1. **Quaternary peat (thick)**: Low permeability cap; midlands, west.
2. **Marine alluvium/estuarine**: Generally low U.
3. **Basalt**: Low U (2-3 ppm), low permeability. Northeast only (Antrim).

### Quaternary modifiers:
- Thick glacial till (>5m): Attenuates radon signal by 30-60%
- Thin glacial till (<3m): Minimal attenuation
- Sand and gravel: High permeability, amplifies bedrock signal
- Rock at surface: Maximum radon transport
- Peat (>2m): Acts as barrier (low permeability, high moisture)

## Tellus Airborne Radiometric Data

- **Measurements**: equivalent Uranium (eU in ppm), equivalent Thorium (eTh in ppm), Potassium (K in %)
- **Flight altitude**: 56 m above ground
- **Line spacing**: 200 m
- **Resolution**: ~50-100 m ground footprint
- **Coverage**: Entire Republic of Ireland (completed by ~2023)
- **Key predictor**: eU is the single strongest geological predictor of indoor radon (explains ~30-40% variance in log-radon at 1-km scale)
- **Derived features**: eU/eTh ratio (uranium enrichment), total dose rate (0.0417K + 0.604eU + 0.310eTh), ternary classification

## Building-Radon Relationships

### Floor type effects (from UK/European studies):
- Suspended timber floor: Highest radon (factor 2-3x vs slab)
- Slab-on-ground (concrete): Baseline
- Basement: Variable (can be very high if unventilated, low if sealed)

### Ventilation effects:
- Natural ventilation (windows + trickle vents): 0.4-0.8 ACH. Moderate radon.
- Extract only (kitchen/bathroom fans): 0.3-0.6 ACH. Slightly higher radon due to depressurisation.
- MVHR (balanced): 0.4-0.6 ACH designed. Can be very effective IF properly installed. Many underperform.
- Passive house: <0.6 ACH @ 50 Pa. Requires functioning MVHR for acceptable radon.

### Airtightness effects:
- Pre-1970s homes: Air permeability ~10-20 m3/(h·m2) @ 50 Pa. Natural ventilation. Low radon dilution but also many uncontrolled pathways.
- Modern regulations (2019 Part L): ~5-7 m3/(h·m2) @ 50 Pa. Reduced ventilation.
- NZEB (2021+): ~3 m3/(h·m2) @ 50 Pa. Requires MVHR.
- Passive house: ~0.6 ACH @ 50 Pa. Critical radon concern on high-radon geology.

## The Airtightness-Radon Paradox

1. Energy-efficient homes reduce air infiltration (good for energy, bad for radon dilution).
2. Deep retrofits (e.g., SEAI scheme) typically reduce air permeability by 30-60%.
3. EPA UNVEIL project found: post-retrofit radon increases of 60% (normal geology) to >100% (high-radon geology).
4. Some homes crossed the 200 Bq/m3 threshold BECAUSE of retrofit.
5. The BER rating is effectively an INVERSE ventilation proxy: high BER = low ventilation = higher radon risk (all else equal).
6. The interaction term BER_rating × geology_radon_potential is the headline finding to test.

## Established Results from Prior Work

- Elío et al. (2022): Logistic regression on Tellus eU + geology → AUC ~0.78-0.82 for Irish HRA prediction
- Kropat et al. (2015): Random Forest + geology + building features → AUC ~0.82 for Swiss radon prediction
- Tchorz-Trzeciakiewicz et al. (2021): XGBoost on Polish data → AUC ~0.85
- No published study combines Tellus radiometric + BER building features for Ireland
- No published study models the BER × geology interaction for Irish radon prediction

## What Works

1. eU from airborne radiometric surveys is the single best geological predictor
2. Bedrock geology code provides independent discrimination
3. Quaternary geology modulates bedrock signal
4. Tree-based ensemble methods (XGBoost, RF) outperform logistic regression by 3-7% AUC
5. Spatial CV is essential; standard CV inflates performance by 10-30%
6. Building features add 2-5% AUC beyond geology alone (Swiss and Polish evidence)
7. The interaction between building airtightness and geology is real but not yet modeled predictively

## What Doesn't Work

1. Deep learning: Marginal improvement over tree methods for tabular radon data
2. Distance-to-fault: Irish faults poorly mapped; adds little beyond bedrock geology
3. Soil gas measurements: Too sparse for national-scale prediction in Ireland
4. Standard random CV: Gives inflated and misleading performance for spatial data
5. Point-measurement indoor radon prediction: Too much house-to-house variability; area-level (Small Area/ED) classification is more reliable

## Key Gaps This Project Fills

1. First use of tree-based ML (XGBoost/LightGBM) for Irish radon prediction (vs logistic regression baseline)
2. First combination of Tellus radiometric + BER building features
3. First quantification of the BER × geology interaction at national scale
4. First identification of "hidden danger" zones (high radon geology + high BER + no measurement)
5. Small Area resolution prediction (vs 10-km grid)
