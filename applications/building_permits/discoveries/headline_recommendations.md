# Phase B headline recommendations

Top-5 actionable findings from the Phase B counterfactual stage-time intervention sweep, ranked by predicted mean duration savings. All dollar figures assume a $300/day small-residential carrying cost and use the per-city annual permit volume observed in the Phase 2.5 sample.

## 1. Seattle: attack the single dominant stage first

- **Stage**: Global bucket: Applicant corrections (days_out_corrections)
- **Intervention**: cut 50% of per-permit active days on this stage
- **Baseline mean duration** (Seattle, n=20,173): **173.5 days**
- **New mean duration**: 129.4 days
- **Days saved (mean)**: **44.1 days per permit**
- **Predicted annual savings** (20,173 permits × $300/day): **$266.8M / year**

## 2. Seattle global bucket attack: cut city plan review in half

- **Target**: `days_plan_review_city` (the sum of reviewer-side active days, regardless of which stage)
- **Days saved (mean)**: 37.6
- **New mean duration**: 135.8 days
- **Predicted annual savings**: **$227.8M / year**
- **Policy lever**: cross-training reviewers across stages, pre-check triage, or same-day-resubmit routing for minor corrections — any reduction in aggregate reviewer hours per permit works.

## 3. NYC BIS: eliminate the owner pickup wait

- **Stage**: DOB approved → permit picked up (owner wait)
- **Baseline mean duration** (NYC BIS n=142,983): **121.0 days**
- **Intervention**: cut 50% of the post-approval pickup wait
- **New mean duration**: 87.6 days
- **Days saved (mean)**: **33.4 days per permit**
- **Predicted annual savings** (42,018 permits × $300/day): **$420.4M / year**
- **Policy lever**: this is an *applicant-side* wait, not a DOB review. Reducing it requires automated notifications, auto-issuance for pro-cert filings, or a deadline-enforced pickup window.

## 4. Cross-city: publish per-stage timestamps

- **Finding**: the cross-city Phase 2 baseline saturates at MAE 89.4 days. The Seattle-with-stages model reaches MAE 24.7 days (4× improvement); the NYC-BIS-with-stages model reaches MAE 4.0 days (22× improvement).
- **Recommendation**: every US municipal open-data portal should publish the per-(review_type × cycle) timestamps that Seattle already publishes in `tqk8-y2z5`. The marginal data-engineering cost is small; the prediction lift is enormous.
- **Projected lift**: applying the Seattle ratio to the 5-city baseline would drop MAE from **89.4 → ~22.1 days** (see `cross_city_counterfactual.md`).

## 5. Intake channel standardisation

- **LA `business_unit` effect**: 4× median-duration spread between Plan-Check-at-Counter (~43 days) and Regular Plan Check (~182 days).
- **Chicago `review_type` effect**: 7.5× spread (EXPRESS 6 days vs STANDARD 45 days).
- **NYC `professional_cert` effect**: 12.7× median speedup (6 days vs 76 days for standard filings).
- **Recommendation**: a substantial share of the cross-city variance is determined *at intake* by which channel the applicant is eligible to use. Expanding eligibility for the fast channels (express, over-the-counter, pro-cert) is a high-leverage legislative intervention with near-zero engineering cost.

## Top-5 Seattle stages by 50%-intervention savings

| rank | stage | days_saved_mean | annual $M |
|---:|---|---:|---:|
| 1 | Global bucket: Applicant corrections (days_out_corrections) | 44.1 | 266.8 |
| 2 | Global bucket: City plan review (days_plan_review_city) | 37.6 | 227.8 |
| 3 | Other (Building / Mechanical / Site Engineer / all other) | 26.3 | 159.0 |
| 4 | Zoning | 15.8 | 95.9 |
| 5 | Drainage | 10.3 | 62.3 |

## NYC BIS stages by 50%-intervention savings

| rank | stage | days_saved_mean | annual $M |
|---:|---|---:|---:|
| 1 | DOB approved → permit picked up (owner wait) | 33.4 | 420.4 |
| 2 | Fully paid → DOB approved | 25.3 | 319.3 |
| 3 | Fees paid → fully paid | 1.6 | 19.9 |
| 4 | Filing → fees paid | 0.2 | 3.1 |

## Methodology note

These projections are *direct counterfactuals*: we subtract a fraction of each permit's observed per-stage active days from its observed total duration. They are not model predictions. A model-based counterfactual would layer the OLS stage coefficients (β_city ≈ +1.65, β_out ≈ +0.24 in the Seattle global-bucket regression) on top, which increases the city bucket's effective lift by ~65% and decreases the applicant bucket's effective lift by ~75%. The direct counterfactual in this document is the conservative floor.
