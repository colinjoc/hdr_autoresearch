# Knowledge Base — Xylella Olive Decline Prediction

## Established Facts

### Biology of Xylella fastidiosa
1. Xylella fastidiosa subsp. pauca (Xfp) is a gram-negative, xylem-limited bacterium that causes Olive Quick Decline Syndrome (OQDS) in European olive groves [1, 2].
2. The bacterium blocks xylem vessels, preventing water transport, causing leaf scorch and progressive canopy desiccation [36, 37].
3. Xfp has a wide host range (595+ plant species) but only causes severe disease in olive (Olea europaea) and a few other hosts in Europe [55].
4. The cultivar Leccino shows partial tolerance; most traditional Puglia cultivars (Cellina di Nardo, Ogliarola salentina) are highly susceptible [3, 58].

### Vector Ecology
5. Philaenus spumarius (meadow spittlebug) is the primary insect vector in Europe [5, 6].
6. Adults acquire the bacterium by feeding on infected xylem sap and transmit it to new hosts [22].
7. Vector activity is temperature-dependent: adults emerge in spring when temperatures exceed ~10 degrees C [23].
8. Vector populations persist on ground cover vegetation and move to olive canopy in summer [6].

### Temperature Thresholds (Competing Hypotheses)
9. **Hypothesis A (vector frost-kill):** P. spumarius eggs and overwintering adults may be killed by sustained temperatures below approximately -6 degrees C [6, 49].
10. **Hypothesis B (bacterial cold-curing):** Xylella fastidiosa cannot survive sustained temperatures below -8 to -12 degrees C in planta; cold winters may "cure" infected trees [10, 11, 12].
11. **In vitro data:** No Xf growth below 12 degrees C; growth rate drops sharply below 17 degrees C; bacterial death at prolonged exposure below -8 degrees C [11].
12. **The Purcell cold-curing concept** (1980): grapevines in cold-winter regions spontaneously clear Pierce's disease infections [10]. This has NOT been confirmed for Xfp in olive.

### Spatial Expansion
13. The Xf epidemic in Puglia was first identified in October 2013 in the municipality of Gallipoli, Lecce province [1].
14. The expansion front has moved northward at approximately 20 km/year since 2013 [16, 53].
15. By 2025, the front has reached the Foggia province (northern Puglia) [EFSA dashboard].
16. The expansion in Spain (Alicante, first detected 2017) appears slower, possibly due to different landscape and host composition [69].
17. **The front shape is not a simple circle**: it follows the Adriatic coast more rapidly than the interior, likely due to olive grove density [53].

### Remote Sensing
18. Sentinel-2 NDVI reliably detects olive grove health decline 1-2 years before visual symptoms become severe [18, 19].
19. Healthy olive groves in Puglia: NDVI 0.35-0.55; severely affected: NDVI 0.15-0.30 [18, 73].
20. EVI (Enhanced Vegetation Index) is less sensitive to atmospheric effects but also less sensitive to early-stage decline [30, 114].
21. NDVI trend (temporal derivative) is the single most informative remote sensing feature for predicting future decline [73, 103].

### Climate Context
22. Southern Puglia (Lecce/Brindisi) has a hot-summer Mediterranean climate with rare frost [85].
23. Northern Puglia (Foggia) has more continental influence with occasional hard frosts [118].
24. The Mediterranean region is warming faster than the global average [86, 87].
25. Warming may expand the climate-suitable zone for Xf northward [13, 14, 110].

### Economics
26. Economic losses estimated at EUR 132 million/year in the Salento region alone [21].
27. Approximately 21 million olive trees affected across Puglia by 2024 [21, 95].
28. Land abandonment is documented in severely affected areas [84].

## What Works in Prediction
29. **Distance to nearest affected area** is the strongest predictor of new decline in spatial models [16, 53, 72].
30. **NDVI trend** (temporal derivative) provides early warning 1-2 years ahead [18, 19, 73].
31. **Winter minimum temperature** features contribute but are weaker predictors than spatial proximity [13, 14].
32. **Spatial cross-validation grouped by province** is essential to avoid leakage from spatial autocorrelation [41].
33. **XGBoost and LightGBM** outperform linear models for this problem by 5-10% AUC [94, 100].

## What Does Not Work
34. **Climate-only models** (no spatial features) fail under spatial CV (AUC < 0.50) because the climate signal is confounded with latitude [mechanism comparison M_A].
35. **EVI does not add value** beyond NDVI for this prediction task [E13 revert].
36. **Province ordinal encoding** leaks spatial information without adding signal [E22 revert].
37. **Individual frost threshold features** (days below -6C, days below -12C) are weaker than the combined frost severity index [E05-E06 revert vs E09 keep].

## Open Questions
38. Is cold-curing operative for Xfp in olive under field conditions? No field validation exists.
39. Will the decline front stall at the Foggia-Molise border due to colder winters?
40. Can the Spanish expansion be predicted from the Italian model, or are the dynamics fundamentally different?
41. How much of the expansion rate is vector-mediated vs. human-mediated (transport of infected plant material)?

## Key Methodological Notes
42. Ground truth is constructed from the EFSA demarcated zone expansion timeline at province/municipality level, NOT from individual tree measurements. This introduces a 1-3 year lag between actual infection and administrative detection.
43. The synthetic data generator is calibrated to published expansion rates, climate statistics, and NDVI ranges. Results should be validated on real Sentinel-2 + E-OBS data when available.
44. Spatial CV with province grouping gives conservative but honest performance estimates. Random CV would inflate AUC by an estimated 10-20%.
