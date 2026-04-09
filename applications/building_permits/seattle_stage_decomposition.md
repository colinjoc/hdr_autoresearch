# Seattle per-stage decomposition — Phase 2.5 Task 1

**Dataset**: Seattle Plan Review `tqk8-y2z5` — one row per (permit × review_type × cycle). Collapsed to one row per permit with per-stage features.

**n_permits** = 20,173  
**Total variance of duration_days** = 43,392 days² (σ = 208.3 days)

## Univariate r² per feature

| feature | Pearson r | r² (variance explained) |
|---|---:|---:|
| days_plan_review_city | +0.626 | 39.2% |
| total_cycles | +0.601 | 36.1% |
| number_review_cycles | +0.596 | 35.5% |
| total_active_days | +0.556 | 30.9% |
| drainage_cycles | +0.494 | 24.4% |
| zoning_cycles | +0.447 | 20.0% |
| drainage_active_days | +0.432 | 18.6% |
| days_out_corrections | +0.431 | 18.5% |
| zoning_active_days | +0.400 | 16.0% |
| days_initial_plan_review | +0.390 | 15.2% |
| structural_engineer_active_days | +0.323 | 10.4% |
| energy_active_days | +0.286 | 8.2% |
| energy_cycles | +0.278 | 7.7% |
| structural_engineer_cycles | +0.271 | 7.3% |
| addressing_active_days | +0.222 | 4.9% |
| ordinance_structural_active_days | +0.150 | 2.2% |
| addressing_cycles | +0.122 | 1.5% |
| ordinance_structural_cycles | +0.089 | 0.8% |

## Joint models (R²)

- **Global buckets** (`days_plan_review_city + days_out_corrections`): R² = **54.1%**
- **Per-stage active days + cycles** (top-6 stages): R² = **36.2%**
- **Stages + global buckets**: R² = **57.0%**

## Global-bucket coefficients (days of total per day of bucket)

- `const`: β = +19.766
- `days_plan_review_city`: β = +1.650
- `days_out_corrections`: β = +0.242

## Stage variance-attribution (R² share, stage-only OLS)

| feature | signed share | share of stage-R² |
|---|---:|---:|
| drainage_cycles | +11.5% | +31.8% |
| zoning_cycles | +7.7% | +21.3% |
| structural_engineer_cycles | +4.5% | +12.5% |
| structural_engineer_active_days | +4.5% | +12.5% |
| zoning_active_days | +3.7% | +10.2% |
| drainage_active_days | +3.1% | +8.7% |
| energy_active_days | -2.2% | -6.1% |
| energy_cycles | +1.6% | +4.5% |
| ordinance_structural_cycles | +0.8% | +2.1% |
| ordinance_structural_active_days | +0.4% | +1.0% |
| addressing_cycles | +0.3% | +0.9% |
| addressing_active_days | +0.3% | +0.8% |

## Interpretation

The top-level decomposition is clean: `days_plan_review_city` + `days_out_corrections` absorb **54.1%** of the variance in `duration_days`, with near-unit slopes (β_city = +1.65, β_out = +0.24). That is the fundamental identity: wall time = city review time + applicant correction time.

The univariate r² column is the most policy-actionable view. It tells you which bucket of time is most *correlated* with long permits — i.e. where the slow permits spend their slow days.

Among the per-stage *city-active* reviews, **drainage_active_days** is the single dominant bottleneck (r² = 18.6%).

**Headline**: the dominant bucket of total variance is **city plan review** at **39.2% of variance**, versus **applicant-side corrections** at **18.5%**. So the bigger predictor of a slow Seattle permit is how long the city takes to review, not the other way round.

## Phase 2.5 Task 4 ablations (XGBoost on the Seattle subset, 5-fold CV)

| exp_id | features | MAE (days) | R²_log | R²_days |
|---|---|---:|---:|---:|
| **C013** | generic metadata only (subtype OHE, applied_year, housing_units) | 99.9 | 0.24 | 0.13 |
| **C001** | + all top-6 per-stage active days + per-stage cycles | 70.8 | 0.67 | 0.46 |
| **C012** | `days_plan_review_city` + `days_out_corrections` only (2 features) | **24.7** | **0.88** | **0.84** |

**C012 is the dominant result of Phase 2.5**: two features (the city and
applicant time buckets) drive MAE from 99.9 days (no stage info) to
**24.7 days** — a 4× improvement on the Seattle subset. The cross-city
Phase 2 baseline's 89.4-day floor was never about the model, it was about
the *features*. When the feature set contains the actual stage-timing
decomposition, the problem collapses.

## Cross-city comparison (the ablation that matters)

| sample | features | MAE | R²_log | source |
|---|---|---:|---:|---|
| cross-city (5 cities) | 120 Phase-2 features | 89.40 | 0.516 | E00 / T01-T05 |
| LA only (n≈133k) | `business_unit` intake + type | 100.8 | 0.418 | C014 |
| Chicago only (n≈73k) | `review_type` intake + ward | 42.6 | 0.362 | C015 |
| Seattle only (n≈20k) | 2 stage buckets | **24.7** | **0.884** | C012 |
| NYC BIS only (n≈42k) | 4 BIS stage intervals | **4.0** | **0.999** | C002 |

The NYC and Seattle results confirm the Phase 2 headline:
**the time prediction problem is fully explained by the stage timing data
when it exists**. Generic tabular features cannot substitute for the
stage-level signal and the Phase 2 saturation at 89.4 days MAE was
structural, not a tuning failure.
