# Feature Candidates — IE Housing Pipeline E2E

## Stage 1→2 Features (Permission → Commencement)

1. **NumResidentialUnits** — scheme size; larger schemes take longer to commence but are less likely to lapse
2. **Planning Authority** — LA-level administrative efficiency and demand heterogeneity
3. **Application Type** — PERMISSION vs OUTLINE vs RETENTION; different regulatory pathways
4. **One-Off House flag** — single self-build dwellings have different dynamics
5. **Dublin indicator** — Dublin LAs have distinct market conditions
6. **Grant year** — time trend in lapse rates (2014-2016 vs 2017-2019)
7. **Appeal status** — appealed permissions may have lower commencement rates
8. **Section 42 extension** — extended permissions indicate delayed commencement
9. **Land Use Code** — residential vs mixed-use

## Stage 2→3 Features (Commencement → CCC)

10. **Opt-out flag** — opt-out projects (one-off self-builds) rarely file CCC; regulatory artefact
11. **Scheme size (units)** — monotone relationship: larger = higher CCC rate
12. **Apartment vs dwelling** — apartment blocks have longer construction but higher completion
13. **AHB flag** — Approved Housing Bodies have higher CCC rates (72%)
14. **Multi-phase flag** — phased developments have higher CCC rates (85% vs 27%)
15. **Construction method** — MMC/modular vs traditional masonry
16. **SHD era** — Strategic Housing Development permissions (2017-2021)
17. **COVID timing** — post-March 2020 commencements take ~28d longer to CCC
18. **Local Authority** — large heterogeneity in CCC filing rates (CV=0.48)
19. **Grant-to-expiry duration** — Section 42 extensions indicate extended timeline

## Stage 3→4 Features (CCC → Occupied)

20. **CCC type** — full completion vs partial; partial may indicate ongoing phases
21. **CCC units vs declared units** — ratio indicates partial completion
22. **Tenure type** — social/affordable vs market may have different occupancy lag

## Cross-cutting / Derived Features

23. **Pipeline duration** — total days from grant to CCC; IQR [691, 1710]
24. **Inverse yield** — permissions needed per completion; currently ~2.8
25. **LA-level yield** — composite metric combining lapse and CCC rates
26. **CSO aggregate ratio** — 2-year lagged permissions-to-completions ratio
