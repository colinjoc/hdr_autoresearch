# Feature Candidates

## Pipeline Stage Features (from predecessor data)

1. **Permission volume** (units/yr) — annual permissions granted from BHQ15
2. **Lapse rate** (fraction) — non-commencement rate from PL-4
3. **Commencement rate** (1 - lapse_rate) — fraction proceeding to construction
4. **Permission-to-commencement duration** (days) — from PL-1
5. **Commencement-to-CCC duration** (days) — from PL-1
6. **CCC filing rate** (fraction) — from S-1
7. **Opt-out share** (fraction of commenced) — from S-1
8. **Non-opt-out CCC rate** (fraction) — from S-1
9. **CCC-to-occupied rate** (fraction) — estimated from S-1
10. **ABP decision time** (weeks) — from PL-3
11. **ABP SOP compliance** (fraction) — from PL-3
12. **ABP utilisation ratio** (intake/disposed) — from PL-3
13. **JR direct unit-months** — from S-2
14. **JR indirect unit-months** — from S-2 (bounded)
15. **Construction capacity ceiling** (units/yr) — observed from CSO
16. **LDA delivery** (units/yr) — from PL-3 LDA
17. **Construction workforce** (persons) — from CSO/SOLAS
18. **Construction cost index** — from CSO wholesale prices
19. **Scheme size distribution** — from PL-1
20. **Dublin vs non-Dublin share** — from PL-1
21. **Apartment vs dwelling share** — from PL-1
22. **AHB vs private share** — from PL-1

## Derived Bottleneck Features

23. **Marginal completions per unit relaxation** — partial derivative of completions w.r.t. each parameter
24. **Throughput bottleneck indicator** — TOC identification of tightest stage
25. **Waterfall attrition per stage** (units lost) — from pipeline model
26. **Sensitivity rank** — ordering of bottlenecks by marginal impact
27. **Interaction strength** — pairwise compounding between bottlenecks
