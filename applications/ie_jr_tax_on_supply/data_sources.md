# Data Sources — JR Tax on Housing Supply

## Primary Sources (from predecessor projects)

| Source | URL | Coverage | Schema | Smoke Test |
|--------|-----|----------|--------|------------|
| OPR Appendix-2 (2022) | ie_shd_judicial_review/data/opr_appendix2.pdf | 144 JR cases 2012-2022 | case_num, date, record_no, citation, name, body, outcome | PASS (PL-1 27-test suite) |
| ABP Annual Reports 2020-2024 | ie_lrd_vs_shd_jr/data/raw/abp_202[0-4].txt | Aggregate intake, disposed, SOP, mean weeks | Narrative + tables | PASS (PL-3 11-test suite) |
| ABP Quarterly Reports 2024-2025 | ie_abp_decision_times/data/raw/q[1-3]_202[4-5].txt | Monthly compliance YTD | Tables | PASS |
| CSO NDQ07 Completions | https://data.cso.ie/table/NDQ07 | Annual housing completions 2015-2024 | year, completions | PASS |

## Derived Data (compiled for this synthesis)

| Artifact | Location | Description |
|----------|----------|-------------|
| SHD_JR_CASES | analysis.py | 22 SHD JR cases with unit counts (8 stated, 14 imputed) |
| ABP_ANNUAL | analysis.py | Mean weeks-to-dispose 2015-2024 from PL-3 |
| CSO_COMPLETIONS | analysis.py | Annual completions from CSO StatBank |
| SHD_DECISIONS | analysis.py | SHD decisions per year from PL-2 R1a + ABP reports |

## No Synthetic Data

All data is from published real sources (OPR, ABP, CSO). Unit count imputation for 14 of 22 JR cases uses the SHD regime minimum (100 units) or typical scheme size; this is documented as a sensitivity parameter, not synthetic data generation.
