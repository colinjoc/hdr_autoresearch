# Knowledge Base — OSS Project Abandonment

Facts, formulas, and reference material. Bracketed numbers = rows in `papers.csv`.

## 1. Target definition (operational)

- **Abandonment(T, H=365)** = 1 iff in `[T, T+H)`:
  - 0 human-authored commits by any contributor, AND
  - repo was not `archived=true` at T, AND
  - repo had ≥20 human-authored commits in `[T-180d, T)`.
- **Human author** = commit where `author.name.lower()` does not end with `[bot]` and is not in the bot list:
  - `dependabot, renovate, renovate-bot, greenkeeper, pre-commit-ci, github-actions, snyk-bot, allcontributors, pyup-bot, imgbot, whitesource-bolt-for-github, mergify`
- **Positive supplement**: `archived` flag flipped to True or Libraries.io `Status` flipped to {Unmaintained, Deprecated} within the forward window.

Rationale: matches CHAOSS Dormancy and Valiev 2018 [6, 132, 164] at the long-horizon end; excludes noise repos (one-off scripts, toys). Human-commit filter is essential — dependabot-only activity is a strong *positive* signal masquerading as "active" (Dey 2020 [35]).

## 2. GitHub Events API core facts (GH Archive post-2015 v3 schema)

Envelope: `id, type, actor.login, actor.id, repo.name (owner/name), repo.id, created_at, payload, public, org`.

| Event | Signal |
|---|---|
| `PushEvent` | commit frequency, author identity, `distinct_size` = new commits (NOT `size`, which includes force-push dupes) |
| `PullRequestEvent` | PR open/close/merge latency, contributor diversity |
| `PullRequestReviewEvent` / `*CommentEvent` | maintainer review latency |
| `IssuesEvent` / `IssueCommentEvent` | issue open/close, time-to-first-response |
| `WatchEvent` | star (always `action=started`; no unstar event) |
| `ForkEvent` | fork growth |
| `CreateEvent` / `DeleteEvent` | branch/tag lifecycle |
| `ReleaseEvent` | release cadence |
| `MemberEvent` | maintainer-team changes (key abandonment signal) |

Common pitfalls:
- GH Archive filenames use UNPADDED hour integers (`-0.json.gz`, `-14.json.gz`).
- `WatchEvent` means "started watching" = star. No unstar event.
- `/stats/contributors` endpoint returns HTTP 202 on first request (cache warming); retry after ~5s.

## 3. Feature families — formulas

### Activity decay
- `commits_last_N_days(T, N)` — count of human-authored PushEvents in `[T-N, T)`
- `commits_decay_ratio = commits_last_30d / commits_last_365d` — 0 = dead, ≥1 = accelerating
- `commits_ar1 = corr(commits_week_t, commits_week_{t-1})` over trailing 52 weeks

### Contributor concentration (bus-factor family)
- **Gini coefficient** of author commit counts over trailing 180d:
  `G = Σ|x_i − x_j| / (2n Σx_i)` — 0 = even, 1 = single author (Gini 1912 [258])
- **Truck factor (Avelino DOA)** — smallest set of authors whose removal leaves < 50% of files with a primary author (Avelino 2016 [1, 163])
- **CHAOSS Elephant Factor** — smallest set of organizations contributing ≥50% of commits (CHAOSS [147])
- **Contributor Shannon entropy** — `H = -Σ p_i log p_i` where p_i = author's share of commits. Lower = more concentrated.

### Response time
- `median_issue_first_response_time_90d` — median time from `IssuesEvent(opened)` to first non-author `IssueCommentEvent`
- `p90_issue_first_response_time_90d` — same at 90th percentile
- `PR_median_close_time_90d` — median time from `PullRequestEvent(opened)` to closed/merged
- `PR_reject_rate_90d` — fraction of PRs closed without merge

### Change-point
- `commits_pelt_changepoints_52w` — number of PELT-detected change-points in weekly commit counts (Killick 2012 [218], ruptures package [220])
- `pelt_since_last_changepoint` — bars since the most recent change-point

### Dependency centrality
- `pagerank_in_libraries_io` — PageRank on Libraries.io dependency graph (direction: "depends on" → "is depended by")
- `in_degree` — number of packages depending on this repo
- `out_degree_unmaintained` — number of this repo's dependencies flagged Unmaintained/Deprecated

### Sentiment / community smells
- `median_issue_comment_sentiment_180d` — VADER or HuggingFace sentiment averaged over `IssueCommentEvent.payload.comment.body`
- `toxic_comment_rate` — fraction flagged by Perspective API or a trained classifier (Miller 2019 [7])

### Calendar / structure
- `age_days_at_T`
- `language` (top 10 + other)
- `license_class` (permissive / copyleft / none)
- `has_contributing_md`, `has_code_of_conduct_md`
- `owner_type` (User / Org)
- `star_count_at_T`, `star_velocity_90d`
- `fork_count_at_T`
- `release_cadence_days` — median days between ReleaseEvents in trailing 365d

## 4. Base rates (from literature)

- Valiev 2018 [6]: ~9.5% of active PyPI packages become dormant over 12 months.
- Avelino 2019 [2]: ~16% truck-factor-loss per 12 months on 1932 GitHub projects.
- Samoladas 2010 [77]: 50% of SourceForge projects die within year 1.
- Tidelift 2024 [108]: 60% of maintainers have considered quitting.
- Our ≥20/180d gate should make abandonment base rate ~5–10% at 365-day horizon.

## 5. Key modelling lessons

- **Tree ensembles dominate tabular** — Fernández-Delgado 2014 [254]; Grinsztajn 2022 [255]. GBDT is the expected Phase 1 winner.
- **Raw GBDT scores miscalibrated for rare events** — use isotonic regression [234–235] (Platt fails on skewed distributions).
- **PR-AUC, not ROC-AUC, for imbalanced target** — Saito & Rehmsmeier 2015 [238].
- **Concept drift is real** — OSS-community norms change over years (CI adoption, generative-AI bots). Rolling-origin temporal CV required (Gama 2014 [241]).
- **Censoring**: currently-active repos at end of data are right-censored. Use survival framework or explicit last-observed-status feature.

## 6. Known failure modes / confounds

- **Bot activity inflates every activity metric** — Dey 2020 [35]; OSS Insight 2022 [155]. Filter to human-author commits.
- **Forks that drift** — many forks are inactive study-snapshots; exclude `fork=true` repos from training unless deliberately modelling fork-lineage.
- **Popularity bias** — star-count and fork-count are heavy-tailed; log1p transform.
- **Geographic + corporate concentration** — if training on all-of-GitHub, US-commercial repos are over-represented; consider stratified sampling (Octoverse 2019 [118]).
- **Generative-AI commit flood (2023+)** — Copilot-assisted commits look human-authored but represent weaker engagement. Hard to detect; possible Phase 2 experiment.

## 7. Relation to prior HDR projects

This is the first project in this pipeline to:
- Use a rare-event binary prediction target (contrasts with continuous regressors like permit-duration or NO2 concentration).
- Use a large-scale event-stream dataset (>1B events sampled) rather than a curated tabular CSV.
- Test a dependency-graph-centrality feature family against activity-decay features head-to-head.
