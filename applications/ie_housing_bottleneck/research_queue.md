# Research Queue

## Format: ID | Hypothesis | Prior | Mechanism | Design Variable | Metric | Baseline | Status

### Phase 0.5 / Baseline
H001 | Waterfall accounting from 38k permissions produces ~13k completions at 35.1% yield | 0.90 | Direct multiplication | pipeline_yield | completions | 13,338 | DONE-E00
H002 | Non-opt-out yield (51.4%) implies ~19.5k completions from 38k | 0.85 | Exclude opt-out artefact | opt_out_build_rate | completions | 19,532 | DONE-E01

### Phase 1 / Tournament
H003 | Simple waterfall accounting identifies permission volume as binding | 0.80 | If yield < 1, permissions is a flow constraint | permission_volume | marginal_units | N/A | DONE-T01
H004 | Sensitivity ranking puts permission volume first | 0.75 | Largest partial derivative | all_params | rank | N/A | DONE-T02
H005 | TOC identifies construction capacity as the ONE constraint | 0.60 | Only one stage can be binding at a time | capacity | bottleneck_id | N/A | DONE-T03
H006 | SEM path coefficients show permission->completion strongest | 0.65 | Path coefficient magnitude | path_coef | R2 | N/A | DONE-T04
H007 | Monte Carlo propagation shows wide CI on completions | 0.85 | Uncertainty propagation | all_ci | completions_ci | N/A | DONE-T05

### Phase 2 / Experiments
H008 | Opt-out 90% built raises effective yield to ~48% | 0.70 | Opt-out homes ARE built | opt_out_build_rate=0.9 | yield | 35.1% | DONE-E01
H009 | +10k permissions adds ~3,500 completions at current yield | 0.80 | Linear scaling | permission_volume=48k | delta_completions | 0 | DONE-E02a
H010 | +20k permissions adds ~7,000 completions | 0.80 | Linear scaling | permission_volume=58k | delta_completions | 0 | DONE-E02b
H011 | +30k permissions adds ~10,500 completions | 0.75 | Assumes no capacity ceiling | permission_volume=68k | delta_completions | 0 | DONE-E02c
H012 | ABP at 18wk adds ~500 completions/yr vs current | 0.50 | Speed-up reduces delay but not attrition | abp_weeks=18 | delta_completions | 0 | DONE-E03a
H013 | ABP at 30wk saves half the excess delay | 0.60 | Intermediate scenario | abp_weeks=30 | delta_completions | 0 | DONE-E03b
H014 | Removing JR entirely adds ~1,000-2,400 units/yr | 0.55 | Counterfactual from S-2 | jr_removed | delta_completions | 0 | DONE-E04
H015 | Halving lapse adds ~700 completions/yr | 0.85 | Direct from S-1 sensitivity | lapse_rate=0.0475 | delta_completions | 0 | DONE-E05
H016 | Halving construction duration has minimal effect on completions/yr | 0.60 | Duration shifts timing not throughput | comm_to_ccc_factor=0.5 | delta_completions | 0 | DONE-E06
H017 | 35k capacity ceiling binds, 50k does not | 0.70 | Current completions near 35k | capacity_ceiling | completions | N/A | DONE-E07a
H018 | 40k capacity ceiling allows some additional completions | 0.75 | 5k headroom | capacity_ceiling=40k | completions | N/A | DONE-E07b
H019 | 50k capacity ceiling is not currently binding | 0.80 | 15k headroom | capacity_ceiling=50k | completions | N/A | DONE-E07c
H020 | LDA 3x adds only ~1,700 units/yr | 0.85 | 3 x 850 = 2,550 but attribution | lda_scale=3 | completions | N/A | DONE-E08
H021 | Combined permission+capacity+ABP scenario | 0.65 | Interaction effects | combined | delta_completions | 0 | DONE-E09
H022 | Dublin accounts for >40% of the pipeline | 0.70 | Dublin is dominant market | dublin_share | completions | N/A | DONE-E10
H023 | Apartment-only pipeline has higher yield than aggregate | 0.65 | Larger schemes complete at higher rate | apartment_only | yield | 35.1% | DONE-E11
H024 | Labour supply proxy shows constraint | 0.55 | Workforce gap 160k vs 200k needed | labour_gap | capacity | N/A | DONE-E12
H025 | International comparison shows Ireland low on yield | 0.80 | UK 50-70%, NZ 80%, NL 90% | international | yield | 35.1% | DONE-E13
H026 | Permission volume sensitivity is nonlinear above capacity | 0.60 | Capacity ceiling creates kink | volume_vs_capacity | completions | N/A | DONE-E14
H027 | Commencement delay economic cost is ~EUR 2B/yr | 0.50 | 38k x 232 days x holding cost | delay_cost | EUR | N/A | DONE-E15
H028 | CCC non-filing is 90%+ measurement artefact | 0.70 | Opt-out + filing discipline | ccc_decomposition | artefact_share | N/A | DONE-E16
H029 | Construction duration is average by international standards | 0.55 | 498 days = 16.6 months | intl_duration | months | 498d | DONE-E17
H030 | ABP delay affects only ~15% of all permissions | 0.70 | Only ABP cases experience this | abp_share | fraction | N/A | DONE-E18
H031 | Full constraint removal scenario adds 15-20k completions/yr | 0.45 | All bottlenecks relaxed simultaneously | all_relaxed | delta_completions | 0 | DONE-E19
H032 | Permission gap to HFA is 12,500-16,500 units/yr at current yield | 0.85 | 50,500 - 34,177 = 16,323 gap | permission_gap | units | N/A | DONE-E20

### Long-shot hypotheses (prior <= 0.3)
H033 | LDA additionality is non-zero | 0.20 | Forward purchase may pull forward construction timing | lda_additionality | units | 0 | DONE-E08
H034 | JR is the binding constraint | 0.15 | JR operates on ~35 cases vs 38k permissions | jr_binding | rank | N/A | DONE-E04
H035 | Construction duration is the binding constraint | 0.10 | Duration affects timing not throughput | duration_binding | rank | N/A | DONE-E06
H036 | ABP decision time is the binding constraint | 0.25 | ABP handles ~15% of permissions | abp_binding | rank | N/A | DONE-E03
H037 | CCC non-filing represents genuine non-completion | 0.20 | Opt-out homes are built but not filed | ccc_genuine | fraction | N/A | DONE-E16
H038 | Emigration materially constrains construction labour | 0.30 | 65.6k emigrants vs 160k construction workforce | emigration_effect | workers | N/A | DONE-E12
H039 | District Court backlog constrains housing delivery | 0.10 | Courts resolve planning disputes | court_constraint | effect | N/A | DONE-E18

### Additional hypotheses (H040-H100+) covering robustness, subgroup, temporal variations
H040 | Pre-COVID vs post-COVID yield differs | 0.50 | COVID disruption | covid_split | yield_diff | 0 | OPEN
H041 | Grant year trend in lapse rate | 0.45 | Temporal improvement | year_trend | slope | 0 | OPEN
H042 | Large schemes (50+) have different bottleneck ranking | 0.55 | Size-specific pipeline | size_filter | rank | N/A | OPEN
H043 | AHB schemes have higher yield than private | 0.60 | AHB completion incentives | ahb_filter | yield_diff | 0 | OPEN
H044 | One-off houses have fundamentally different pipeline | 0.80 | Self-build opt-out | oneoff_filter | yield | N/A | OPEN
H045 | Permission-volume constraint tightens post-2020 | 0.50 | Flat permissions despite demand | temporal | constraint_rank | N/A | OPEN
H046 | SHD-era permissions had worse yield than non-SHD | 0.55 | SHD JR exposure | shd_filter | yield_diff | 0 | OPEN
H047 | Construction cost is a binding constraint on starts | 0.40 | High costs prevent commencement | cost_proxy | starts_per_permission | N/A | OPEN
H048 | Infrastructure (water/sewage) constrains permissions | 0.50 | Infrastructure deficits in some areas | infra_proxy | constrained_share | N/A | OPEN
H049 | Multiple bottlenecks interact (non-additive) | 0.55 | Compounding effects | interaction | delta_vs_sum | 0 | DONE-Phase2.5
H050 | The "binding constraint" changes over time | 0.60 | Pre-2019 was capacity; post-2019 is permissions | temporal_binding | constraint_id | N/A | OPEN
H051-H100 | [Additional robustness, subgroup, and temporal hypotheses] | 0.30-0.70 | Various | Various | Various | Various | OPEN
