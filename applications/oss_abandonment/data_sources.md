# Data Sources — OSS Project Abandonment

## 1. GH Archive (primary event stream)

- **URL root**: `https://data.gharchive.org/`
- **File pattern**: `YYYY-MM-DD-H.json.gz` (UNPADDED hour: `-0.json.gz`, `-14.json.gz`)
- **Coverage**: hourly since 2011-02-12; schema v3 since Jan 2015
- **BigQuery mirror**: `githubarchive.day.*` / `githubarchive.month.*` (public, pay-per-query)
- **Size**: busy hour ~150 MB gzip / 1.2 GB decompressed / 600k events; daily 2.5–4 GB gzip; yearly ~1–1.5 TB gzip
- **Event types we care about**: see `knowledge_base.md` §2

## 2. Libraries.io dumps

- **URL**: `https://zenodo.org/records/3626071` (v1.6.0, 2020-01-12)
- **Files**: `projects.csv` (~4.5M), `versions.csv` (~26M), `dependencies.csv` (~114M), `repository.csv` (~3.3M with `Status`: Active/Deprecated/Unmaintained/Removed)
- **Status**: read-only since 2022; supplement with `deps.dev` BigQuery (`bigquery-public-data.deps_dev_v1`) for 2020–2024 data, and https://ecosyste.ms.

## 3. OSS Insight API

- **Base**: `https://api.ossinsight.io/v1/`
- **Rate limits**: 600/hr anon, 3600/hr with API key
- **Useful endpoints**: `/repos/{o}/{r}/issues/creators/`, `/pull-requests/creators/`, `/contributors/activity/`, `/pull-request-response-time/`, `/issue-response-time/`, `/contributors/absence-factor/`, `/contributors/bus-factor/`
- **Role**: enrichment layer for final cohort, not bulk discovery

## 4. GitHub REST/GraphQL API

- **REST**: `https://api.github.com` — 5000/hr auth, 60 unauth, secondary rate limit on 403
- **GraphQL**: 5000 points/hr — nested queries cost 1–50 points
- **Key endpoints**: `/repos/{o}/{r}`, `/stats/contributors` (202 on cache miss; retry), `/stats/commit_activity`, `/stats/participation`, `/contributors`, `/commits`, `/issues`, `/releases`
- **Auth**: `GITHUB_TOKEN` env var; prefer fine-grained PAT with public-repo read scope

## 5. Sampling plan

- **Active-repo filter**: aggregate `PushEvent.repo.id` across 90-day windows; keep repos with ≥10 distinct commits in any window.
- **Sampling window**: 7 evenly spaced days per quarter × 6 calendar years (2019–2024) = 168 days ≈ 500–700 GB gzip.
- **Backfill**: full event history for ~25k cohort via BigQuery SQL (~$5–20/year-slice) OR re-scan hourly files with repo.id filter.
- **Stratification**: language (top 10 + other), repo age at T, star tier, license class.

## 6. Expected dataset scale

- 25,000 repos × 10 prediction times (semi-annual 2019–2023) = **250,000 (repo, T) observations**
- At ~6–10% positive rate: 15,000–25,000 positive labels
- Storage: ~900 GB total (raw sampled + cohort parquet + enrichment cache)

## 7. **Practical scope for this session** (RTX 3060, limited bandwidth)

For Phase 0.5 baseline we will **NOT** pull 25k repos × 6 years. Instead:
- Pull a single 2-week window of GH Archive (336 hourly files, ~45 GB gzip, ~7 hours download at home internet).
- Filter to ~2000–5000 active repos (≥10 commits in that window).
- Use `T = start of window − 180 days` as the prediction cutoff (we need 180 days prior-activity and 365 days forward-activity to label).
- This means we need GH Archive from roughly 2023-04 to 2024-10 to get 1 full year of forward labels for a prediction window in 2023-10.
- Final usable cohort ≈ 1000–3000 repos; 5 prediction times; ~5000 observations with 300–500 positives. Small but enough for a working baseline.

If the user approves a larger budget later, we'll upgrade to the 25k-repo plan.
