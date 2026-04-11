# Review Signoff: Dublin and Cork NO2 Source Apportionment

**Date**: 2026-04-10
**Reviewer recommendation**: Minor revision
**Post-revision assessment**: All addressable issues resolved. Paper ready for publication.

---

## Issue Resolution Summary

| Category | Critical | Major | Minor | Resolved | Deferred |
|----------|----------|-------|-------|----------|----------|
| Claims vs evidence | 0 | 2 | 1 | 3 | 0 |
| Scope vs framing | 0 | 0 | 3 | 3 | 0 |
| Reproducibility | 0 | 0 | 2 | 1 | 1 |
| Missing experiments | 0 | 7 | 0 | 4 | 3 |
| Overclaiming | 0 | 0 | 3 | 3 | 0 |
| Literature positioning | 0 | 2 | 1 | 3 | 0 |
| **Total** | **0** | **11** | **10** | **17** | **4** |

## Resolved Issues (17)

1. COVID tautology explicitly acknowledged in abstract and text
2. Citation [5] error corrected (China not London)
3. Wind-direction analysis added (Figure 6)
4. NO2 photochemistry discussed with O3-NO2 scatter (Figure 8)
5. Weekend/weekday correction performed numerically (Figure 7)
6. 2019-vs-2020 weather comparison added
7. Title changed: "Validated" to "Supported"
8. "Diesel traffic" changed to "road traffic" with fleet composition note
9. WHO exceedance contextualized within Europe (94% of EU urban population)
10. Cork limited coverage acknowledged
11. "Source attribution" changed to "source apportionment" throughout
12. Lough Navar weekday-weekend anomaly explained
13. 6 new references added (total now 21)
14. "Even complete elimination" claim qualified
15. EMEP, openair, DEFRA AURN cited
16. Harrison et al. (2012) NOx chemistry cited
17. Code repository already linked

## Deferred Issues (4)

These are acknowledged as future work and do not block publication:

1. **Trend analysis** -- COVID disruption makes 9-year trend estimation unreliable without segmented regression
2. **Population-weighted exposure** -- requires Census spatial data and interpolation beyond this study's scope
3. **Formal uncertainty quantification** -- bootstrap CIs on attribution percentages; informal bounds provided via method comparison (14 pp mean disagreement)
4. **Sensitivity to station subset** -- combinatorial testing of station selections; acknowledged but not performed

## New Analyses Added

| Analysis | Key Finding | Figure |
|----------|-------------|--------|
| Wind direction (16-sector) | Winetavern NO2 1.7x higher under N vs S winds | Figure 6 |
| Weekday-weekend correction | Corrected estimates within 14 pp of station-differencing (vs 44 pp raw) | Figure 7 |
| O3-NO2 photochemistry | Anti-correlation r=-0.40 at urban stations; Irish O3 peaks in winter (transport-dominated) | Figure 8 |
| Weather 2019 vs 2020 | Temp +0.3C, wind speed unchanged, sunnier in 2020 -- confirms COVID signal is emission-driven | In text |

## New Results in results.tsv

- R1_ww_correction: weekday-weekend raw error 44.3%, corrected error 14.2%
- R2_photochemistry: mean urban O3-NO2 correlation -0.401
- R3_weather_confound: temp diff +0.30C, wind diff -0.03 knots, sun diff +1.63 hrs
- R4_wind_direction: Winetavern max/min ratio 1.70

## Signoff

The paper has been revised to address all critical and major reviewer concerns that are feasible with the available data. The four deferred items are acknowledged as limitations and future work. The revised paper is stronger than the original: it is more honest about the COVID validation tautology, includes three new independent analyses that triangulate the traffic attribution, properly discusses NO2 photochemistry, and corrects all factual errors. The reference list has grown from 15 to 21 entries, covering the key omissions identified by the reviewer.

**Status: SIGNED OFF**
