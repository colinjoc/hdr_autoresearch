# Research Queue

## Hypotheses (100+)

| ID | Hypothesis | Prior | Mechanism | Design Variable | Metric | Baseline | Status |
|----|-----------|-------|-----------|----------------|--------|----------|--------|
| H001 | Duration -50% alone produces >40k gross completions | 0.70 | Finance savings increase viability -> more apps | duration_reduction | gross_completions | 35,000 | OPEN |
| H002 | Modular -30% alone produces >80k gross completions | 0.60 | 15.9% cost reduction -> large viability swing | modular_reduction | gross_completions | 35,000 | OPEN |
| H003 | VAT 0% alone produces >70k gross completions | 0.65 | 11.9% cost reduction | vat_rate | gross_completions | 35,000 | OPEN |
| H004 | Land CPO (agricultural) alone produces >80k gross completions | 0.60 | 16.2% cost reduction, largest single lever | land_cost_multiplier | gross_completions | 35,000 | OPEN |
| H005 | Workforce +50% alone does NOT increase completions | 0.90 | Workforce only lifts ceiling; without cost reduction, no demand increase | workforce_multiplier | completions | 35,000 | OPEN |
| H006 | BCAR abolished alone produces <42k gross completions | 0.80 | Only 1.5% cost reduction, small effect | bcar_fraction | gross_completions | 35,000 | OPEN |
| H007 | Duration + Modular interaction is super-additive | 0.55 | Duration reduces time, modular reduces cost; independent mechanisms | dur+mod | interaction_term | 0 | OPEN |
| H008 | Duration + Finance rate interaction is sub-additive | 0.70 | Both act on finance costs; redundant on same component | dur+fin | interaction_term | 0 | OPEN |
| H009 | VAT + Part V interaction is approximately additive | 0.60 | Both reduce cost on different components | vat+partv | interaction_term | 0 | OPEN |
| H010 | Triple (duration + modular + VAT) has positive 3-way interaction | 0.50 | Three independent cost mechanisms compound | triple | interaction_term | 0 | OPEN |
| H011 | All 10 levers maxed produce >200k gross completions | 0.40 | 70% cost reduction -> massive viability swing | all_levers | gross_completions | 35,000 | OPEN |
| H012 | Capacity ceiling binds for any >15% cost reduction with workforce at +0% | 0.85 | 15% cost reduction -> ~49k gross, ceiling at 35k | ceiling | binding | FALSE | OPEN |
| H013 | 50,500 target requires workforce lever of at least +20% | 0.75 | Ceiling at 35k prevents reaching 50.5k without expansion | target | workforce_needed | N/A | OPEN |
| H014 | Optimal 3-lever combo is modular + land CPO + workforce | 0.45 | Two largest cost levers + ceiling lift | optimal_3 | completions | 35,000 | OPEN |
| H015 | Politically feasible package achieves <45k completions | 0.55 | Moderate levers produce moderate outcomes | feasible | completions | 35,000 | OPEN |
| H016 | Radical package achieves >50k completions | 0.60 | Strong cost levers + some ceiling lift | radical | completions | 35,000 | OPEN |
| H017 | Multiplicative model predicts higher combined effects than additive | 0.65 | Product of (1+effects) > sum of effects | model_comparison | delta_completions | varies | OPEN |
| H018 | Full factorial reveals at least 5 lever combos exceeding 50.5k (with workforce) | 0.70 | Many high-cost-reduction combos exist | factorial | count_above_target | 0 | OPEN |
| H019 | Monte Carlo 95% CI for best package spans >20k units | 0.50 | Parameter uncertainty is large relative to effects | mc_ci | CI_width | N/A | OPEN |
| H020 | Marginal interaction is largest for workforce lever (enables all others) | 0.75 | Workforce lifts ceiling; other levers push against it | marginal | interaction_rank | N/A | OPEN |
| H021 | Duration + Modular + VAT produces interaction > 5,000 units | 0.45 | Three independent mechanisms | triple_interaction | units | 0 | OPEN |
| H022 | Part V abolition alone produces <50k gross completions | 0.80 | Only 3.9% cost reduction | partv_alone | gross_completions | 35,000 | OPEN |
| H023 | Dev contribs zeroed alone produces <45k gross completions | 0.85 | Only 3% cost reduction | devcontribs_alone | gross_completions | 35,000 | OPEN |
| H024 | Finance rate 3% alone produces >50k gross completions | 0.55 | 6.3% cost reduction, moderate | finance_alone | gross_completions | 35,000 | OPEN |
| H025 | Developer margin 6% alone produces >60k gross completions | 0.50 | 9% cost reduction | margin_alone | gross_completions | 35,000 | OPEN |
| H026 | Modular + Workforce synergy is the largest pairwise interaction | 0.55 | Modular reduces cost AND expands effective capacity | mod_work | interaction_rank | N/A | OPEN |
| H027 | Land CPO + Workforce synergy is second-largest pairwise interaction | 0.50 | Largest cost lever meets ceiling lift | land_work | interaction_rank | N/A | OPEN |
| H028 | VAT + Workforce synergy is third-largest pairwise interaction | 0.50 | Large cost lever meets ceiling lift | vat_work | interaction_rank | N/A | OPEN |
| H029 | Duration + Finance is the most sub-additive pair | 0.65 | Both target finance costs | dur_fin | interaction_sign | negative | OPEN |
| H030 | BCAR + Dev contribs is the most redundant pair (smallest combined effect) | 0.60 | Both are small levers | bcar_dev | combined_effect | small | OPEN |
| H031 | Systems-dynamics model with third-order feedback produces >5% more completions | 0.30 | Scale economies are uncertain | sd_model | delta_vs_linear | 0% | OPEN |
| H032 | Time-to-target for best package is <5 years | 0.40 | Pipeline delay means 2-3 years before effects materialize | time | years_to_target | N/A | OPEN |
| H033 | Absorption rate does NOT bind below 55k completions/yr | 0.70 | Latent demand (170k+ waiting lists) absorbs easily | absorption | binding | FALSE | OPEN |
| H034 | GE effects reduce the net completions by <10% for packages under 50k | 0.65 | Price effects modest at moderate volumes | ge | reduction_pct | 0% | OPEN |
| H035 | GE effects reduce net completions by >20% for "everything" package | 0.45 | Large volume increases compress margins significantly | ge_extreme | reduction_pct | 0% | OPEN |
| H036 | Pareto frontier (3-lever combos) has a clear knee point | 0.60 | Diminishing returns after the most cost-effective levers | pareto | knee_exists | N/A | OPEN |
| H037 | Developer margin is the most cost-effective lever (completions per EUR cost to govt) | 0.30 | Margin reduction is cost-free to government | cost_eff | rank | N/A | OPEN |
| H038 | VAT cut is the LEAST cost-effective lever (per EUR of revenue forgone) | 0.40 | VAT cut costs ~€1.4B/yr in revenue | cost_eff_vat | rank | N/A | OPEN |
| H039 | Land CPO + modular + workforce is the Pareto-optimal 3-lever combo | 0.45 | Two largest cost levers + ceiling lift | pareto_3 | frontier | N/A | OPEN |
| H040 | With +50% workforce, there exist 100+ lever combos exceeding HFA target | 0.60 | Many high-cost combos push past 50.5k with raised ceiling | count | combos_above_target | 0 | OPEN |
| H041 | Without workforce lever, ZERO combos reach HFA target | 0.90 | Ceiling at 35k < target of 50.5k | no_work | combos_above_target | 0 | OPEN |
| H042 | Sensitivity to build-yield is larger than sensitivity to approval rate | 0.55 | Build-yield CI is wider (55-64%) | sensitivity | ranking | N/A | OPEN |
| H043 | Cost reduction of 10%+ flips Dublin viability from negative to positive | 0.80 | Baseline is -3.1%, so 3.2pp+ makes it positive | viability | threshold | -3.1% | OPEN |
| H044 | Flipping viability creates a discontinuous jump in applications | 0.45 | The r=0.91 elasticity is linear, not threshold-based in our model | viability_threshold | jump | continuous | OPEN |
| H045 | At least 3 levers individually flip Dublin viability positive | 0.75 | Modular (15.9%), VAT (11.9%), Land (16.2%) all >3.1% | viability_flip | count | 0 | OPEN |
| H046 | Duration -25% + Modular -10% + VAT 9% is sufficient to flip viability | 0.70 | Combined ~16% cost reduction >> 3.1% deficit | combo_viability | margin | <0 | OPEN |
| H047 | The "politically feasible" package increases gross completions by >30% | 0.55 | Moderate cost levers produce moderate viability gains | feasible_pct | gross_delta_pct | 0% | OPEN |
| H048 | The interaction matrix has >20 positive (synergistic) cells | 0.40 | Most interactions should be near-zero or slightly positive | matrix | positive_count | 0 | OPEN |
| H049 | The interaction matrix has <5 strongly negative (redundant) cells | 0.65 | Few lever pairs target the same cost component | matrix | negative_count | 0 | OPEN |
| H050 | Workforce × any cost lever is always positive in the interaction matrix | 0.80 | Workforce enables all cost levers to translate to completions | work_interaction | always_positive | TRUE | OPEN |
| H051 | Duration × Finance is the only strongly sub-additive pair | 0.50 | Only this pair targets the same cost component | sub_additive | count | 1 | OPEN |
| H052 | 95% CI for "everything" package is [45k, 60k] | 0.35 | Wide uncertainty from many uncertain parameters | mc_everything | CI | N/A | OPEN |
| H053 | The optimal 5-lever combo achieves 95% of the 10-lever effect | 0.50 | Diminishing returns from smaller levers | optimal_5 | pct_of_10 | N/A | OPEN |
| H054 | Removing developer margin from optimal package barely changes completions | 0.40 | Margin is medium-sized (9%); other levers compensate | margin_ablation | delta | small | OPEN |
| H055 | Removing workforce from "everything" package drops completions by >30% | 0.70 | Ceiling becomes binding at 35k instead of 52.5k | work_ablation | delta_pct | 0% | OPEN |
| H056 | Materials CAGR of 4% erodes cost-reduction benefits within 4 years | 0.55 | 4% compounding -> 17% over 4 years, comparable to many levers | erosion | years_to_erode | N/A | OPEN |
| H057 | Modular cost reduction persists despite CAGR because it's structural | 0.70 | Modular changes the production function, not just current prices | modular_persist | persists | TRUE | OPEN |
| H058 | VAT cut benefit is immediately eroded if developers raise pre-tax prices | 0.30 | Supply constraint means developers have pricing power | vat_passthrough | pct_eroded | 0% | OPEN |
| H059 | At current viability (-3.1%), even small cost reductions produce large app changes | 0.65 | Starting from deeply negative viability, each pp matters | elasticity_at_baseline | magnitude | large | OPEN |
| H060 | The r=0.91 elasticity overstates the causal effect (correlation != causation) | 0.40 | r=0.91 may include confounders | r_causal | overstated | unknown | OPEN |
| H061 | Build-yield of 59.6% understates capacity because it includes legacy permissions | 0.45 | Old permissions with different viability conditions drag down yield | yield_bias | direction | understated | OPEN |
| H062 | Approval rate of 68% is stable across viability regimes | 0.55 | Planning decisions are not primarily viability-driven | approval_stable | variation | small | OPEN |
| H063 | Lapse rate decreases with improved viability | 0.75 | Better viability -> fewer permissions expire unused | lapse_viability | correlation | negative | OPEN |
| H064 | Capacity ceiling is NOT a hard wall — it's a cost curve (diminishing returns) | 0.50 | In reality, pushing past capacity raises costs, doesn't stop production | ceiling_soft | shape | curve | OPEN |
| H065 | Doubling the number of apprentices takes 4+ years to impact capacity | 0.80 | Apprenticeships take 4 years to complete | apprentice_lag | years | 4+ | OPEN |
| H066 | Immigration of skilled workers can raise ceiling within 1-2 years | 0.60 | Faster than training but depends on availability | immigration | years | 1-2 | OPEN |
| H067 | Modular factories can expand capacity within 2-3 years | 0.55 | Factory construction plus supply chain setup | factory_lag | years | 2-3 | OPEN |
| H068 | The 104,976-combination factorial can be reduced to <1000 effective combos with screening | 0.50 | Many levers have small effects; screening eliminates them | screening | effective_combos | 104,976 | OPEN |
| H069 | Top-10 lever combos by completions all include workforce +50% | 0.80 | Ceiling binding means workforce is necessary | top10_work | all_include | TRUE | OPEN |
| H070 | Top-10 lever combos by completions all include modular -30% | 0.60 | Largest cost lever | top10_mod | all_include | TRUE | OPEN |
| H071 | Top-10 lever combos by completions all include land CPO (agricultural) | 0.55 | Largest cost lever (tied with modular) | top10_land | all_include | TRUE | OPEN |
| H072 | BCAR appears in <50% of top-100 lever combos | 0.65 | Small lever, not discriminating | bcar_top100 | pct | <50% | OPEN |
| H073 | Dev contribs appears in <50% of top-100 lever combos | 0.60 | Small lever | dev_top100 | pct | <50% | OPEN |
| H074 | Multiplicative model produces 5-15% higher predictions than additive for the best combo | 0.55 | Multiplicative compounds individual effects | mult_vs_add | delta_pct | 0% | OPEN |
| H075 | Systems-dynamics model produces similar results to multiplicative | 0.50 | SD captures same compounding via feedback | sd_vs_mult | similarity | N/A | OPEN |
| H076 | Tournament winner is T04 (full factorial) because it captures all interactions exactly | 0.65 | Full enumeration is the ground truth | tournament | winner | N/A | OPEN |
| H077 | The additive model underestimates the best package by >20% | 0.55 | Missing interaction effects are large | additive_error | pct | 0% | OPEN |
| H078 | With workforce +20% (more realistic), HFA target is still achievable with strong cost levers | 0.60 | +20% -> ceiling 42k; need strong cost levers to push demand | work20_target | achievable | unknown | OPEN |
| H079 | Pareto frontier has fewer than 20 non-dominated 3-lever combos | 0.50 | Many combos are dominated | pareto_count | count | N/A | OPEN |
| H080 | Developer margin cut is on the Pareto frontier (zero fiscal cost) | 0.70 | Free for government | margin_pareto | on_frontier | TRUE | OPEN |
| H081 | VAT zeroing is NOT on the Pareto frontier (very high fiscal cost) | 0.55 | €1.4B cost may not justify completions gained | vat_pareto | on_frontier | FALSE | OPEN |
| H082 | Modular + workforce is the cost-efficiency champion 2-lever combo | 0.50 | Moderate fiscal cost, high completions | mod_work_eff | rank | N/A | OPEN |
| H083 | Land CPO is politically infeasible and should be modeled separately | 0.70 | Constitutional property rights issues | cpo_feasibility | feasible | uncertain | OPEN |
| H084 | Without CPO, the best achievable package reaches ~48k completions | 0.45 | Losing 16% cost reduction is significant | no_cpo | completions | N/A | OPEN |
| H085 | The sensitivity of the optimal package to the r=0.91 parameter is >±5k units | 0.55 | The entire demand amplification depends on this correlation | r_sensitivity | delta | ±5k | OPEN |
| H086 | The sensitivity to build-yield is >±3k units for the best package | 0.50 | 55-64% CI -> significant completion variation | yield_sensitivity | delta | ±3k | OPEN |
| H087 | Cost escalation (4%/yr) means static lever effects overstate 5-year outcomes by >15% | 0.50 | Compounding erosion | escalation | overstatement | 0% | OPEN |
| H088 | A "phased" package (implement levers sequentially) reaches target later than "big bang" | 0.75 | Interaction effects mean simultaneous deployment is more effective | phased_vs_bigbang | time_diff | 0 years | OPEN |
| H089 | The feedback loop model is roughly linear in viability improvement | 0.60 | The elasticity formula is explicitly linear | linearity | R_squared | >0.95 | OPEN |
| H090 | Nonlinearity enters only through the capacity ceiling | 0.70 | Ceiling introduces a kink | nonlinearity_source | ceiling | TRUE | OPEN |
| H091 | If viability elasticity is 0.50 instead of 0.91, best-package completions drop >30% | 0.60 | Halving the amplification factor | low_elasticity | delta_pct | 0% | OPEN |
| H092 | Commuter belt viability (-9 to -11%) requires >10% cost reduction just to break even | 0.80 | Much deeper viability deficit | commuter_viability | threshold | 10% | OPEN |
| H093 | Even with all levers, commuter belt viability remains marginal (<5%) | 0.40 | 70% cost reduction should more than cover 11% deficit | commuter_margin | viability | <5% | OPEN |
| H094 | The model predicts correctly that current system produces ~35k completions | 0.95 | Calibration target | calibration | completions | 35,000 | OPEN |
| H095 | Sensitivity analysis shows workforce lever has the highest "option value" | 0.65 | Enables all other levers to translate to completions | option_value | rank | N/A | OPEN |
| H096 | Two levers alone can achieve 50.5k: land CPO + workforce +50% | 0.55 | 16.2% cost reduction + ceiling at 52.5k | two_lever_target | achievable | unknown | OPEN |
| H097 | Three levers alone can achieve 50.5k: modular + VAT + workforce | 0.60 | ~28% cost reduction + ceiling at 52.5k | three_lever_target | achievable | unknown | OPEN |
| H098 | The "everything" package minus the two smallest levers loses <2% of completions | 0.65 | BCAR and dev contribs contribute <3% combined | diminishing_returns | loss_pct | 0% | OPEN |
| H099 | Monte Carlo reveals asymmetric uncertainty: upside > downside | 0.45 | Ceiling truncates upside; downside is unbounded | mc_asymmetry | skewness | 0 | OPEN |
| H100 | The interaction matrix is mostly positive (synergistic) | 0.55 | Most lever pairs are independent -> slightly positive through nonlinearity | matrix_sign | net_positive | TRUE | OPEN |
| H101 | At least one 4-way interaction is detectable (>1000 units) | 0.35 | Higher-order interactions diminish rapidly | four_way | magnitude | <1000 | OPEN |
| H102 | The Sobol first-order indices sum to >0.80 (interactions are <20% of variance) | 0.50 | Main effects dominate in most factorial designs | sobol | sum_first_order | N/A | OPEN |
| H103 | The Sobol total-order index for workforce is >0.30 (largest of all levers) | 0.60 | Workforce interacts with everything | sobol_work | total_order | N/A | OPEN |
| H104 | Removing BCAR from the optimal package changes completions by <500 units | 0.75 | BCAR is the smallest lever | bcar_marginal | delta | <500 | OPEN |
| H105 | The "everything minus CPO" package still exceeds 50.5k with workforce +50% | 0.60 | Remaining levers sum to ~55% cost reduction | no_cpo_target | achievable | unknown | OPEN |
