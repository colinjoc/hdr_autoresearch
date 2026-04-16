# Knowledge Base — IE Housing Pipeline E2E

## Established Facts

### Pipeline Structure
1. Irish residential planning permissions lapse after 5 years if not commenced (Planning and Development Act 2000, s.42).
2. Commencement requires filing a Commencement Notice (CN) with the Building Control Management System (BCMS) under BCAR 2014.
3. Completion requires filing a Certificate of Completion and Compliance (CCC) for non-opt-out projects.
4. Opt-out projects (predominantly one-off self-build dwellings) are exempt from CCC filing under S.I. No. 9 of 2014.
5. CSO measures completions via ESB meter connections (NDQ series) and local authority returns (NDA12), not via BCMS CCC filings.

### Quantitative Pipeline Parameters (from predecessor projects)
6. **Lapse rate (PL-4)**: NRU>0 2017-2019 cohort: 9.5% [9.1%, 9.9%]. Broader cohort with fuzzy matching: 27.4%. True rate bounded [9.5%, 27.4%].
7. **CCC filing rate (PL-1)**: All commenced 2014-2019: 40.9% [40.5%, 41.2%]. Non-opt-out only: 59.8%.
8. **Median perm→commencement (PL-1)**: 232-234 days [231, 236].
9. **Median comm→CCC (PL-1)**: 496-498 days [492, 500].
10. **Median perm→CCC (PL-1)**: 962-1,096 days (varies by subcohort definition).
11. **CSO aggregate 2-yr conversion (PL-0)**: 41% (2019) rising to 65% (2022); pre-COVID was 77-86% (2016-2017).
12. **LDA delivery (PL-3)**: ca. 850 homes in 2023, 100% Project Tosaigh acquisition, 3.5% of NDA12 towns.

### Key Confounds and Channel Effects
13. The low overall CCC rate (40.9%) is dominated by opt-out projects (31.6% of cohort) that are not required to file CCCs.
14. PL-4's lapse rate is confounded by the join quality between the planning register and BCMS: fuzzy matching inflates apparent lapse.
15. The dark-permission rate is channel-dependent: 0.67% under "never commenced" definition, up to 39% under "CCC never filed among non-opt-out" (PL-1 finding).
16. CSO completions and BCMS CCC measure different things: ESB connections vs regulatory certification. Modest but real discrepancy.
17. LDA Project Tosaigh homes are already counted in the national completions denominator — they represent attribution, not additionality.

### Structural Findings
18. **Permission volume is the binding constraint**: even at 100% conversion, ~38,000 permissions/yr cannot deliver 50,500 completions/yr (PL-0).
19. **Scheme size is the dominant predictor of CCC filing**: 1-unit = 12.2%, 200+ units = 88.8% (this project, E01).
20. **AHB projects outperform private**: 72.3% vs 40.4% CCC rate (E08).
21. **Multi-phase > single-phase**: 85.4% vs 27.2% CCC rate (E25).
22. **Dublin > non-Dublin**: 47.5% vs 39.5% CCC rate (E06).
23. **COVID added ~28 days to comm→CCC** (E05).
24. **Later grant years have higher CCC rates**: 2014 = 37.1%, 2019 = 44.9% (E13/E28).
25. **LA-level heterogeneity is large**: CV = 0.48 across LAs with n≥50 (E02).

### Pipeline Yield
26. **Best-estimate yield**: 35.1% [27.9%, 35.4%] for 2014-2019 cohort.
27. **Yield decomposition**: (1 - 0.095 lapse) × 0.409 CCC × 0.95 occupied = 35.1%.
28. **Non-opt-out yield** would be: (1 - 0.095) × 0.598 × 0.95 = 51.4%.
29. **Permissions needed for HFA 50,500/yr**: ~144,000 at current yield; ~98,000 at non-opt-out yield.
30. **Gap**: current ~38,000 perms/yr is 26-39% of what's needed.

### What Doesn't Work / Known Pitfalls
31. Row-level linkage between the planning register and BCMS is unreliable: different identifier formats, LA naming inconsistencies, and the planning register's Application Number does not always match BCMS's CN_Planning_Permission_Number.
32. Cox PH models fail to converge on the perm→comm transition in BCMS because the BCMS only contains projects that filed a CN — survival variation is minimal.
33. Aggregate 2-year lag ratios (CSO-style) are not cohort-tracked and conflate permissions from different years.
34. The apartment flag is poorly populated in BCMS for the 2014-2019 period; CN_Sub_Group is more reliable than CN_Dwelling_House_Type.
35. Right-censoring is severe for 2018-2019 grants: many may still file CCCs.

### Limitations
36. Stage 3→4 (CCC→occupied) is not directly measurable; 95% is a proxy.
37. The lapse rate range [9.5%, 27.4%] is wide; the true value depends on unmeasurable join quality.
38. Opt-out CCC non-filing is regulatory, not economic — these homes are built and occupied but never certified.
39. No tenure data: social, affordable, and market are pooled.
40. No cost data: cannot assess whether delivered homes are affordable.
