# Data sources — PL-3 An Bord Pleanála decision-time trend

## Primary

1. **ABP Annual Report Appendices 2018, 2020-2024**
   - Each contains tables titled "Average Time Taken to Dispose of Cases (Weeks)" and "Summary of Cases Disposed of by Reference to Statutory Objective Period".
   - Statutory Objective Period (SOP): 18 weeks for most appeals/referrals, 16 weeks for certain fast-track cases, different for SID/SHD/LRD.
   - Local paths: `data/raw/ar_2018.txt` (+pdf), `data/raw/appendix_202[0-3].txt/.pdf`, and `data/raw/abp_2024.pdf/.txt` (shared with `/applications/ie_lrd_vs_shd_jr/`).
   - Also `data/raw/appendix_2022.pdf/.txt` (year 2022), `data/raw/abp_2022.txt/.pdf` (year 2022 main report).

2. **ABP Quarterly Planning Casework Statistics, 2024 Q1-Q3 and 2025 Q1-Q3**
   - Per-quarter: monthly SOP compliance by case-type band.
   - Local paths: `data/raw/q[1-3]_2024.pdf/.txt`, `data/raw/q[1-3]_2025.pdf/.txt`
   - Source list: https://www.pleanala.ie/en-ie/statistics/quarterly-statistics

3. **Annual Report 2018** (full) for baseline pre-crisis context
   - Local path: `data/raw/ar_2018.pdf/.txt`

## Cross-validation / context

- **Companion ABP 2020-2024 annual reports** (from PL-2 project): `/home/col/generalized_hdr_autoresearch/applications/ie_lrd_vs_shd_jr/data/raw/abp_202[0-4].{pdf,txt}` — same source, used for JR volumes and case-type splits.
- **Press reporting** on 28% statutory compliance in 2023 (Irish Times Oct 2024), 1,000+ backlog (Irish Examiner 2023).

## Smoke-test verification (2026-04-15)

- All 11 PDFs fetched (HTTP 200), extracted to text via pdftotext.
- Key text strings located in Q1 2025 report: "100% compliance with 16 week SOP", "% Formal Disposals Within SOP 25 30 41", monthly compliance table.
- Appendix 2023 has "Average Time Taken to Dispose of Cases (Weeks)" table in Table 2.
- Statutory Objective Period definition confirmed (18 weeks appeals/referrals; 16 weeks fast-track).

Data access confirmed. No credentials required.
