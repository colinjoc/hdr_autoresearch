# Feature Candidates — JR Tax on Housing Supply

## Direct Delay Variables
1. **Units per JR case**: stated or imputed from SHD scheme size
2. **Delay months**: lodgement-year to decision-year, plus remittal time for quashed cases
3. **Outcome weight**: 1.0 (quashed/conceded), 0.5 (refused/dismissed), 0.25 (upheld)
4. **Unit-months**: units x delay_months x outcome_weight
5. **Holding cost**: unit-months x EUR/unit/month

## Indirect Delay Variables
6. **ABP mean weeks excess**: observed - 18 (baseline)
7. **JR attribution share**: [0%, 25%, 50%] — channel bounds
8. **Housing case volume**: annual housing-type cases at ABP (~1,120/year)
9. **Indirect unit-months**: excess_weeks x JR_share x housing_cases x 12/52

## Counterfactual Variables
10. **SOP compliance rate**: observed vs counterfactual 18-week
11. **Completions shifted**: annual completions x (excess_weeks/52) x housing_share
12. **Cumulative gap**: running total of shifted completions

## Cost Variables
13. **Land finance cost**: ~EUR 500/unit/month (6% annual on 30% of EUR 350k)
14. **Opportunity cost (rent)**: ~EUR 1,500/unit/month Dublin
15. **Construction inflation**: 7% p.a. compound applied to delay period
16. **Total economic cost**: holding + opportunity + inflation per unit-month

## Queueing Variables
17. **Utilisation rho**: intake / disposed
18. **JR equivalent caseload**: JR cases x multiplier (7x normal case time)
19. **JR contribution to rho**: JR equivalent / total disposed
20. **Backlog-at-start**: on-hand cases at year start (from ABP Table 1)
