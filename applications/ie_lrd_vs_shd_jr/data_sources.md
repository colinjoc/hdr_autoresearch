# Data sources — PL-2 LRD vs SHD judicial-review follow-up

## Primary

1. **An Bord Pleanála / An Coimisiún Pleanála annual reports 2020-2024**
   - Each report contains a "judicial reviews by development type" breakdown (including LRD and SHD categories) and year-over-year intake/disposal figures.
   - Local paths:
     - `data/raw/abp_2020.pdf` / `.txt`
     - `data/raw/abp_2021.pdf` / `.txt` + `abp_2021_app.pdf`
     - `data/raw/abp_2022.pdf` / `.txt`
     - `data/raw/abp_2023.pdf` / `.txt` + `abp_2023_app.pdf`
     - `data/raw/abp_2024.pdf` / `.txt`
   - Source URLs: `https://www.pleanala.ie/en-ie/publications`

2. **OPR Appendix-2 (predecessor project, SHD-era JRs 2018-2022)**
   - Cross-reference at `/home/col/generalized_hdr_autoresearch/applications/ie_shd_judicial_review/data/opr_appendix2.pdf` + `jr_raw.txt`
   - Parser at `/home/col/generalized_hdr_autoresearch/applications/ie_shd_judicial_review/parser_v2.py` — reusable.

3. **OPR Learning from Litigation Legal Bulletins (Issue 10, 11)**
   - Case-level LRD-era JR discussion.
   - Local paths: `data/raw/opr_bulletin_10.pdf` / `.txt`, `data/raw/opr_bulletin_11.pdf` / `.txt`

4. **Appendix-2 Breakdown of JRs (October 2022)**
   - Local path: `data/raw/opr_appendix2_v2022.pdf` / `.txt` (6,172 lines) — most complete case-level resource on 2018-2022 SHD-era JRs.

## Context / cross-check

- **Planning in Numbers 2023** (OPR) — cross-check ABP totals
- **ESRI housing working papers** — LRD-regime policy context
- **Planning and Development Act 2024** — successor regime context (implementation 2025+)

## Smoke-test verification (2026-04-15)

All five ABP annual reports 2020-2024 fetched (HTTP 200), extracted to text via pdftotext.
Key claims in ABP 2024:
- 2024 LRD appeals received: 71
- 2024 LRD appeals concluded: 79
- 2024 new JR applications total: 147 across all case types, of which 143 reviewable by type
- SHD permissions: 23.4% were judicial-reviewed (pre-2021 cohort; predecessor project headline)

Data access confirmed. No credentials required.
