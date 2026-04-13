# Research Queue — OSS Abandonment Prediction

120 pre-registered hypotheses. Each has a prior probability that the change improves **Score** (primary metric: PR-AUC at 365-day horizon on temporal holdout). Status codes: OPEN, RESOLVED, RETIRED, DEFERRED.

---

## Theme A — Activity-decay features (A1–A15)

- **A1** [OPEN | prior 70%] Replace raw `commits_last_90d` with `log1p(commits_last_90d)`.
- **A2** [OPEN | prior 65%] Add `commits_decay_ratio = commits_30d / commits_365d`.
- **A3** [OPEN | prior 60%] Add weekly commit counts as a 52-dim vector.
- **A4** [OPEN | prior 55%] Add PELT change-point counts on weekly commits.
- **A5** [OPEN | prior 50%] Add time-since-last-commit.
- **A6** [OPEN | prior 55%] Add `commits_ar1` (AR(1) coefficient on weekly counts).
- **A7** [OPEN | prior 50%] Replace count-based features with `tsfresh` automated extraction.
- **A8** [OPEN | prior 45%] Add exponential-decay-weighted commit count (half-life 90d).
- **A9** [OPEN | prior 40%] Add Holt-Winters forecasted commits for next 90d as feature.
- **A10** [OPEN | prior 45%] Add commits-by-weekday distribution entropy.
- **A11** [OPEN | prior 40%] Add `release_cadence_days` (median gap between ReleaseEvents).
- **A12** [OPEN | prior 35%] Add `release_backlog_days_since_last_release`.
- **A13** [OPEN | prior 40%] Bot-filtered commit count supersedes raw commit count.
- **A14** [OPEN | prior 40%] Weekend-commit share (personal projects vs corporate).
- **A15** [OPEN | prior 30%] Commit-message-length mean/std.

## Theme B — Contributor concentration (B1–B15)

- **B1** [OPEN | prior 70%] Add author Gini coefficient over 180d.
- **B2** [OPEN | prior 65%] Add Shannon entropy of author contributions.
- **B3** [OPEN | prior 70%] Add DOA-based truck factor (Avelino 2016).
- **B4** [OPEN | prior 60%] Add CHAOSS Elephant Factor (org-level).
- **B5** [OPEN | prior 55%] Add number of distinct committers in last 90d / 180d / 365d.
- **B6** [OPEN | prior 50%] Add ratio of elite-5 contributors' share.
- **B7** [OPEN | prior 55%] Add newcomer-retention rate (commits by first-time contributors who return within 90d).
- **B8** [OPEN | prior 50%] Add fraction of commits by most recent quarter contributors.
- **B9** [OPEN | prior 45%] Interaction: `truck_factor × org_type`.
- **B10** [OPEN | prior 45%] Add max-streak-length of top contributor's inactive days.
- **B11** [OPEN | prior 35%] Add contributor tenure distribution moments (mean, median, skew).
- **B12** [OPEN | prior 40%] Add contributor-graph clustering coefficient.
- **B13** [OPEN | prior 45%] Add `contributor_turnover_rate_12mo`.
- **B14** [OPEN | prior 40%] Corporate-email-domain share (is project backed by a company?).
- **B15** [OPEN | prior 30%] Gender diversity (Vasilescu 2015 [54]) — probably can't infer reliably.

## Theme C — Response-time & engagement (C1–C12)

- **C1** [OPEN | prior 60%] Add median issue first-response time over 180d.
- **C2** [OPEN | prior 55%] Add p90 issue first-response time (heavy tail).
- **C3** [OPEN | prior 55%] Add PR median close-time.
- **C4** [OPEN | prior 50%] Add PR reject rate (closed-without-merge).
- **C5** [OPEN | prior 50%] Add open-issue backlog size and growth rate.
- **C6** [OPEN | prior 50%] Add open-PR backlog size and growth rate.
- **C7** [OPEN | prior 45%] Stale-issue ratio (no activity in 90d).
- **C8** [OPEN | prior 40%] Avg issue thread length (engagement proxy).
- **C9** [OPEN | prior 40%] Maintainer-first-response-share (is a core maintainer responding?).
- **C10** [OPEN | prior 35%] Time-since-last-maintainer-comment.
- **C11** [OPEN | prior 30%] Ratio of closed-as-not-planned to closed-as-completed.
- **C12** [OPEN | prior 25%] Labels "help wanted"/"good first issue" counts.

## Theme D — Sentiment & community-smell (D1–D10)

- **D1** [OPEN | prior 45%] Mean sentiment of issue comments (VADER).
- **D2** [OPEN | prior 40%] Fraction of toxic comments (trained classifier).
- **D3** [OPEN | prior 40%] Negative-sentiment growth rate.
- **D4** [OPEN | prior 35%] Maintainer pushback rate (Raman 2020 [8]).
- **D5** [OPEN | prior 35%] Community-smell indicators (Tamburri 2019 [67]).
- **D6** [OPEN | prior 30%] Incivility event count in trailing 90d.
- **D7** [OPEN | prior 25%] Profanity count in issue comments (crude proxy).
- **D8** [OPEN | prior 30%] First-interaction-sentiment for newcomers.
- **D9** [OPEN | prior 25%] CoC violation report count.
- **D10** [OPEN | prior 20%] Emoji-reaction distribution over last 30d.

## Theme E — Popularity & structure (E1–E12)

- **E1** [OPEN | prior 45%] Log1p star count at T.
- **E2** [OPEN | prior 40%] Star velocity (stars/day) in last 90d.
- **E3** [OPEN | prior 35%] Fork count log1p + fork velocity.
- **E4** [OPEN | prior 30%] Star/fork ratio.
- **E5** [OPEN | prior 40%] Age in days at T (log).
- **E6** [OPEN | prior 45%] Owner type (User vs Org).
- **E7** [OPEN | prior 35%] Language (top 10 one-hot + other).
- **E8** [OPEN | prior 35%] License class (permissive/copyleft/none/other).
- **E9** [OPEN | prior 35%] Has CONTRIBUTING.md / has CoC.
- **E10** [OPEN | prior 30%] README length, has badges.
- **E11** [OPEN | prior 40%] Repo size bucket (LOC bin).
- **E12** [OPEN | prior 25%] Default branch = `main` vs `master` (modernization proxy).

## Theme F — Dependency network (F1–F10)

- **F1** [OPEN | prior 55%] Libraries.io in-degree (how many packages depend on this).
- **F2** [OPEN | prior 50%] PageRank on Libraries.io graph.
- **F3** [OPEN | prior 45%] Out-degree to Unmaintained deps.
- **F4** [OPEN | prior 40%] Fraction of deps with recent commits.
- **F5** [OPEN | prior 45%] Node2Vec/DeepWalk embedding features (Perozzi 2014 [262]).
- **F6** [OPEN | prior 35%] GraphSAGE inductive embedding (Hamilton 2017 [263]).
- **F7** [OPEN | prior 40%] Is this repo a Census-III critical package?
- **F8** [OPEN | prior 30%] Dependency-graph betweenness.
- **F9** [OPEN | prior 30%] Ecosystem membership (npm/PyPI/Maven/Cargo).
- **F10** [OPEN | prior 25%] Fraction of downstream dependents actively updating.

## Theme G — Target engineering (G1–G8)

- **G1** [OPEN | prior 40%] Horizon H = 180d instead of 365d.
- **G2** [OPEN | prior 35%] Horizon H = 540d.
- **G3** [OPEN | prior 40%] Continuous target (commits in next 365d) + regressor.
- **G4** [OPEN | prior 30%] Survival-analysis formulation (Cox PH TVC, RSF).
- **G5** [OPEN | prior 35%] Competing-risks framing (abandonment vs archived vs forked).
- **G6** [OPEN | prior 25%] Soft labels (fraction of months with a human commit).
- **G7** [OPEN | prior 30%] Include `archived` and Libraries.io `Status` flip as positive supplement.
- **G8** [OPEN | prior 25%] Exclude repos with ≤100 stars (narrow to "serious" projects).

## Theme H — Class imbalance & calibration (H1–H8)

- **H1** [OPEN | prior 55%] Use `scale_pos_weight` in XGBoost.
- **H2** [OPEN | prior 45%] SMOTE oversampling of positives.
- **H3** [OPEN | prior 40%] Focal loss via LightGBM custom objective.
- **H4** [OPEN | prior 60%] Isotonic calibration after GBDT.
- **H5** [OPEN | prior 40%] Platt (sigmoid) calibration — probably worse than isotonic but cheap.
- **H6** [OPEN | prior 35%] Stratified bootstrap CIs on PR-AUC.
- **H7** [OPEN | prior 30%] Rebalance cohort at train-time only, not test-time.
- **H8** [OPEN | prior 25%] Cost-sensitive decision threshold.

## Theme I — Hyperparameter tuning (I1–I10)

- **I1** [OPEN | prior 40%] XGBoost max_depth sweep {4,6,8}.
- **I2** [OPEN | prior 35%] learning_rate {0.03, 0.05, 0.1}.
- **I3** [OPEN | prior 30%] num_boost_round with early stopping.
- **I4** [OPEN | prior 30%] min_child_weight {1,10,50}.
- **I5** [OPEN | prior 30%] subsample {0.5,0.7,0.9,1.0}.
- **I6** [OPEN | prior 30%] colsample_bytree {0.5,0.7,0.9,1.0}.
- **I7** [OPEN | prior 35%] reg_alpha / reg_lambda grid.
- **I8** [OPEN | prior 30%] Optuna TPE w/ Hyperband for 100 trials.
- **I9** [OPEN | prior 25%] LightGBM num_leaves sweep.
- **I10** [OPEN | prior 25%] CatBoost with ordered boosting on-by-default.

## Theme J — Model-family tournament (J1–J10, Phase 1 core)

- **J1** [OPEN | prior — baseline] XGBoost (baseline E00).
- **J2** [OPEN | prior 45%] LightGBM.
- **J3** [OPEN | prior 40%] CatBoost.
- **J4** [OPEN | prior 40%] Random Forest.
- **J5** [OPEN | prior 30%] Logistic regression (linear sanity check).
- **J6** [OPEN | prior 40%] Random Survival Forest (Ishwaran 2008 [250]).
- **J7** [OPEN | prior 35%] Cox PH with time-varying covariates.
- **J8** [OPEN | prior 30%] DeepSurv (Katzman 2018 [251]).
- **J9** [OPEN | prior 25%] Transformer Hawkes (Zuo 2020 [226]) on event streams.
- **J10** [OPEN | prior 35%] Stacking ensemble of J1+J2+J6 with logistic meta.

## Theme K — Concept drift / temporal validation (K1–K8)

- **K1** [OPEN | prior 60%] Rolling-origin 5-fold temporal CV.
- **K2** [OPEN | prior 45%] Train 2019–2021, test 2022–2023.
- **K3** [OPEN | prior 35%] Weight older training samples exponentially down.
- **K4** [OPEN | prior 30%] Include `prediction_year` as feature (absorb drift).
- **K5** [OPEN | prior 25%] Separate models per year window.
- **K6** [OPEN | prior 30%] Retrain monthly with sliding window.
- **K7** [OPEN | prior 25%] Domain-adversarial training.
- **K8** [OPEN | prior 20%] Remove features with highest drift (KS stat).

## Theme L — Interactions & pairwise (L1–L10, Phase 2.5)

- **L1** [OPEN | prior 40%] `truck_factor × star_count`.
- **L2** [OPEN | prior 35%] `commits_decay_ratio × org_type`.
- **L3** [OPEN | prior 35%] `response_time × bot_activity`.
- **L4** [OPEN | prior 30%] `language × age_bucket`.
- **L5** [OPEN | prior 25%] `license × owner_type`.
- **L6** [OPEN | prior 30%] `in_degree × maintainer_burnout_proxy`.
- **L7** [OPEN | prior 30%] `issue_backlog × PR_close_time`.
- **L8** [OPEN | prior 25%] `commits_ar1 × contributor_entropy`.
- **L9** [OPEN | prior 25%] Deep feature interaction (XGB 2nd-order via GBDT depth).
- **L10** [OPEN | prior 25%] Manual top-10-SHAP pairwise sweep.

## Theme M — Negative controls (M1–M5)

- **M1** [OPEN | prior — validation] CHAOSS project repos must score ≤median risk.
- **M2** [OPEN | prior — validation] Repos archived within window must score ≥p75 risk.
- **M3** [OPEN | prior — validation] `random_feature` must have zero SHAP importance.
- **M4** [OPEN | prior — validation] Permutation test: shuffle labels → PR-AUC → 0.5.
- **M5** [OPEN | prior — validation] Train on pre-2020 → test on 2020+ (concept-drift sanity).

---

Total: **120 pre-registered hypotheses**. KEEP threshold: +0.01 PR-AUC on temporal holdout with bootstrap CI not crossing zero, OR a +0.5pp Brier-score improvement on the same split.
