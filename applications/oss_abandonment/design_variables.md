# Design Variables — OSS Abandonment Prediction

88 candidate features grouped by family. Each can be computed from GH Archive events + optional Libraries.io / OSS Insight enrichment.

## Activity-decay (16)

| # | name | formula | inputs |
|---|---|---|---|
| 1 | commits_30d | count PushEvent.distinct_size | PushEvent |
| 2 | commits_90d | count | PushEvent |
| 3 | commits_180d | count | PushEvent |
| 4 | commits_365d | count | PushEvent |
| 5 | commits_decay_30_90 | c30 / c90 | derived |
| 6 | commits_decay_90_365 | c90 / c365 | derived |
| 7 | days_since_last_commit | `T - max(created_at)` | PushEvent |
| 8 | commits_ar1_52w | AR(1) coef on weekly counts | weekly |
| 9 | commits_exp_decay_h90 | Σ c_i × exp(-(T-t_i)/90) | PushEvent |
| 10 | commits_weekday_entropy | entropy of day-of-week distr | PushEvent |
| 11 | commits_hourofday_entropy | entropy | PushEvent |
| 12 | weekend_commit_share | c_weekend / c_total | PushEvent |
| 13 | pelt_changepoints_52w | PELT count on weekly counts | ruptures |
| 14 | weeks_since_last_pelt_cp | derived | ruptures |
| 15 | holt_winters_forecast_90d | HW forecast for next 90d | statsmodels |
| 16 | commits_hbot_ratio | human / (human+bot) | PushEvent+is_bot |

## Releases (4)

| # | name | formula | inputs |
|---|---|---|---|
| 17 | releases_365d | count ReleaseEvent | ReleaseEvent |
| 18 | release_cadence_median_days | median gap | ReleaseEvent |
| 19 | days_since_last_release | T - max | ReleaseEvent |
| 20 | prerelease_share | prereleases/all | ReleaseEvent |

## Contributors & bus-factor (14)

| # | name | formula | inputs |
|---|---|---|---|
| 21 | authors_90d | distinct author count | PushEvent |
| 22 | authors_365d | distinct | PushEvent |
| 23 | author_gini_180d | Gini on author commit counts | derived |
| 24 | author_entropy_180d | Shannon entropy | derived |
| 25 | truck_factor_doa | Avelino DOA | commits + files |
| 26 | elephant_factor | smallest org set for 50% commits | PushEvent.actor + org |
| 27 | top1_author_share | max author share | derived |
| 28 | top5_author_share | sum top-5 share | derived |
| 29 | newcomer_retention_90d | first-time contributors who return within 90d | PushEvent |
| 30 | one_shot_contributor_rate | 1-commit authors / all | PushEvent |
| 31 | tenure_mean_days | mean contributor tenure at T | PushEvent |
| 32 | tenure_median_days | median | PushEvent |
| 33 | corporate_email_share | fraction with corp-domain email | PushEvent |
| 34 | contributor_turnover_12mo | authors active 6mo ago but not now | PushEvent |

## Issues / PRs / response times (14)

| # | name | formula | inputs |
|---|---|---|---|
| 35 | issues_opened_90d | count | IssuesEvent |
| 36 | issues_closed_90d | count | IssuesEvent |
| 37 | issue_backlog | opened - closed all-time | IssuesEvent |
| 38 | issue_backlog_growth_90d | Δ in 90d | IssuesEvent |
| 39 | median_issue_first_response_90d | median first non-author comment time | IssueCommentEvent |
| 40 | p90_issue_first_response_90d | p90 | derived |
| 41 | stale_issue_ratio | issues with no activity 90d / open | IssuesEvent |
| 42 | prs_opened_90d | count | PullRequestEvent |
| 43 | pr_merged_rate_90d | merged/closed | PullRequestEvent |
| 44 | pr_median_close_time_90d | median | PullRequestEvent |
| 45 | pr_backlog | opened - closed | PullRequestEvent |
| 46 | maintainer_response_share | core-team responses / total | IssueCommentEvent |
| 47 | days_since_last_maintainer_comment | derived | IssueCommentEvent |
| 48 | issue_thread_len_mean | avg comments per issue | IssueCommentEvent |

## Popularity & structure (12)

| # | name | formula | inputs |
|---|---|---|---|
| 49 | stars_at_T | cumulative WatchEvent count | WatchEvent |
| 50 | star_velocity_90d | stars/day in last 90d | WatchEvent |
| 51 | forks_at_T | ForkEvent cumulative | ForkEvent |
| 52 | fork_velocity_90d | forks/day | ForkEvent |
| 53 | age_days_at_T | T - repo_created_at | GH API |
| 54 | owner_type | User / Organization | GH API |
| 55 | language_primary | most-used language | GH API |
| 56 | license_class | permissive / copyleft / none | GH API |
| 57 | has_contributing_md | 0/1 | repo files |
| 58 | has_code_of_conduct | 0/1 | repo files |
| 59 | has_readme | 0/1 | repo files |
| 60 | default_branch_main | "main" vs "master" | GH API |

## Size & complexity (6)

| # | name | formula | inputs |
|---|---|---|---|
| 61 | repo_size_kb | size_kb at T | GH API |
| 62 | file_count_approx | via tree API | GH API |
| 63 | loc_estimate | via cloc or stats | GH API |
| 64 | avg_commit_size | mean files_changed per push | PushEvent |
| 65 | commit_msg_len_mean | char avg | PushEvent |
| 66 | commit_msg_has_trailing_signed_off | fraction | PushEvent |

## Dependency network (10)

| # | name | formula | inputs |
|---|---|---|---|
| 67 | libraries_io_in_degree | count depends-on | Libraries.io |
| 68 | libraries_io_out_degree | count deps | Libraries.io |
| 69 | libraries_io_pagerank | PageRank | Libraries.io + networkx |
| 70 | unmaintained_dep_share | deps with Status=Unmaintained | Libraries.io |
| 71 | stale_dep_share | deps with no release 365d | Libraries.io |
| 72 | is_census_iii_critical | 0/1 | Census III table |
| 73 | ecosystem_label | npm/PyPI/Maven/... | Libraries.io |
| 74 | downstream_avg_activity | mean recent activity of dependents | Libraries.io + GH |
| 75 | deepwalk_embedding_32d | 32-dim node embedding | gensim |
| 76 | graphsage_embedding_32d | inductive embedding | PyG |

## Sentiment & community smell (7)

| # | name | formula | inputs |
|---|---|---|---|
| 77 | issue_comment_mean_sentiment_180d | VADER compound | IssueCommentEvent |
| 78 | issue_comment_neg_share_180d | neg / total | IssueCommentEvent |
| 79 | toxic_rate_180d | trained classifier | IssueCommentEvent |
| 80 | maintainer_pushback_rate | Raman 2020 classifier | IssueCommentEvent |
| 81 | first_interaction_sentiment_median | newcomer-first-comment sentiment | derived |
| 82 | lone_wolf_smell | 1 contributor in key files | PushEvent |
| 83 | silo_smell | team-communication gaps | IssueCommentEvent graph |

## Calendar + misc (5)

| # | name | formula | inputs |
|---|---|---|---|
| 84 | prediction_year | int(T.year) | derived |
| 85 | is_weekend_heavy | weekend activity share | PushEvent |
| 86 | activity_during_holidays | holiday-window activity | PushEvent + calendar |
| 87 | bot_activity_90d | bot PushEvent count | PushEvent+is_bot |
| 88 | archived_before_T | 0/1 (exclude if 1) | GH API |

## Feature-selection plan

- Phase 0.5 baseline: use a minimal feature set (A1–A8, B1–B5, C1–C3, E1–E6) — 22 features.
- Phase 2: one feature or one family addition per experiment.
- Phase 2.5: top-10 features by SHAP × pairwise.
