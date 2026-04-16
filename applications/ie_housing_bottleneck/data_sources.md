# Data Sources

This is a meta-analysis synthesis project. All data comes from predecessor studies' published results, not from primary data downloads. The "data" is the set of measured parameters from 13 predecessor papers.

| Source | Coverage | Schema | URL | Smoke Test |
|--------|----------|--------|-----|------------|
| PL-0: ie_housing_pipeline/paper.md | Aggregate conversion 2019-2025 | Permissions, completions, 2-yr lag ratio | Local file | PASS |
| PL-1: ie_commencement_notices/paper.md | BCMS cohort 2014-2025 (N=183,633) | Duration medians, CCC rates | Local file | PASS |
| PL-4: ie_lapsed_permissions/paper.md | NPR-BCMS linkage 2014-2019 (N=46,073) | Lapse rate, CI | Local file | PASS |
| PL-3 LDA: ie_lda_delivery/paper.md | LDA 2023 delivery | ca. 850 homes, 3% HFA | Local file | PASS |
| PL-1 SHD: ie_shd_judicial_review/paper.md | SHD JR 2018-2022 (N=22 cases) | State-loss rate, case-level | Local file | PASS |
| PL-2: ie_lrd_vs_shd_jr/paper.md | LRD vs SHD comparison | Honest null, n=2 LRD outcomes | Local file | PASS |
| PL-3 ABP: ie_abp_decision_times/paper.md | ABP 2015-2025 | Mean weeks, SOP, rho | Local file | PASS |
| S-1: ie_housing_pipeline_e2e/paper.md | Pipeline yield 2014-2019 | 35.1% yield, stage rates | Local file | PASS |
| S-2: ie_jr_tax_on_supply/paper.md | JR cost quantification | 105,504 unit-months, counterfactual | Local file | PASS |
| ie_courts_waits/paper.md | Court filing surplus 2017-2024 | Resolution ratios by court | Local file | PASS |
| ie_graduate_emigration/paper.md | Emigration 2020-2025 | Destination mix, net migration | Local file | PASS |
| ie_gender_pay_gap/paper.md | Gender pay gap Ireland | Within-firm narrowing | Local file | PASS |
| uk_gender_pay_gap/paper.md | Gender pay gap UK | 40-55yr parity horizon | Local file | PASS |

**No primary data download required.** All parameters are extracted from predecessor papers' published results tables and embedded as constants in analysis.py. This is a synthesis, not a primary data collection.
