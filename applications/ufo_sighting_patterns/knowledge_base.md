# Knowledge Base: NUFORC UFO Sighting Pattern Analysis

## Established Facts

1. **NUFORC database contains 147,890 structured reports** spanning ~1950s-2024, with 80,332 geocoded in the Kaggle subset (through 2013) [38, 134]
2. **41% of sighting times fall on exact clock hours** — strong digit-preference bias [2]
3. **Reporting is media-sensitive** — sighting counts spike after major UFO news coverage [2, 57]
4. **~88% of investigated UFO cases are identifiable** as conventional objects (Hendry 1979: 22% stars/planets, 21.5% aircraft, 8% advertising planes, etc.) [74]
5. **Venus is historically the #1 misidentification source**, followed by aircraft and satellites [19, 55]
6. **Starlink trains cause misidentification** — documented case with 5 airline pilots reporting simultaneously [14]
7. **NUFORC provides explanations for only ~803 of 147,890 reports** (0.5%), mostly post-2019 [38]
8. **Western US states have higher per-capita sighting rates** even after population normalization, attributed to sky-view potential (dark skies, low cloud cover, open terrain) [1]
9. **Sighting rates correlate with military installation proximity** but causation is ambiguous [1]
10. **Summer seasonality is robust** — July-August peaks consistently observed [76]
11. **Dusk peak at 8-10 PM** is the most consistently replicated temporal finding across decades and countries [76]
12. **Shape taxonomy has shifted over decades**: "disk/saucer" dominated 1950s-1980s; "light", "orb", "triangle" dominate 2000s+ [3, 133]
13. **Reporting lag varies from minutes to decades** — some reports are retrospective [2]
14. **The 2012-2014 peak** in annual report counts coincides with internet saturation and is not necessarily a peak in underlying events

## Known Pitfalls

1. **Population confounding**: Raw sighting counts reflect population distribution, not event distribution
2. **Internet adoption confound**: The growth curve 1995-2014 mirrors internet penetration, not sighting rate
3. **Temporal reporting bias**: Clock-hour rounding, media-driven waves, retrospective reports
4. **Shape category overlap**: "Circle" vs "Sphere" vs "Orb" vs "Light" are poorly distinguished
5. **Selection bias**: NUFORC self-reporters are a non-random subset of sky observers
6. **Explanation field is sparse**: Only 0.5% annotated; cannot treat unannotated as "unexplained"
7. **Geocoding coverage gap**: The 2014-2024 period lacks lat/lon in the structured dataset
8. **Duration parsing challenges**: Free-text durations ("several seconds", "a few minutes") require NLP
9. **Country imbalance**: 82% of geocoded reports are US; cross-country comparison has severe power issues for non-US
10. **July 4th contamination**: Fireworks generate UFO reports; any summer analysis must control for July 4th ± 3 days

## What Works in This Domain

- Per-capita normalization is essential for any spatial comparison
- STL decomposition cleanly separates trend from seasonality in monthly data
- DBSCAN with haversine metric handles geographic clustering well
- Logistic regression provides interpretable baselines for classification
- Text length and detail level correlate with report quality
- Before/after designs (e.g., Starlink launch date) provide cleaner identification than cross-sectional comparisons

## What Doesn't Work

- Raw counts without normalization (population artifacts dominate)
- Treating all NUFORC entries as independent observations (media-driven correlation)
- Fine-grained temporal analysis pre-1990 (sparse data)
- Cross-country comparison with this data (US dominance)
- Treating "no explanation" as "unexplained" (explanation field is sparsely populated)
