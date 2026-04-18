# Feature Candidates

This project is a simulation/policy-analysis project (Option C), not a predictive ML project. The "features" are the design variables (levers) and derived quantities from the feedback loop model.

## Input Features (Lever Settings)

1. Duration reduction fraction (0-0.50)
2. Modular hard-cost reduction fraction (0-0.30)
3. VAT rate (0-0.135)
4. Part V rate (0-0.20)
5. Development contributions fraction (0-1.0)
6. BCAR compliance fraction (0-1.0)
7. Land cost multiplier (0.1-1.0)
8. Finance rate (0.03-0.07)
9. Developer margin (0.06-0.15)
10. Workforce multiplier (1.0-1.5)

## Derived Features (Computed)

11. Total cost reduction (fraction)
12. Cost saving per unit (EUR)
13. New viability margin (fraction)
14. Viability delta (pp)
15. Application multiplier
16. New application rate (units/yr)
17. New permission rate (units/yr)
18. Gross completions (uncapped)
19. Capacity ceiling (effective)
20. Final completions (capped)
21. Ceiling-binding indicator (boolean)
22. Gap to HFA target (units/yr)
23. Pairwise interaction term for each lever pair (45 pairs)
24. Three-way interaction term for selected lever triples
25. Marginal interaction contribution per lever

## Response Variables

- Primary: Final completions (units/yr)
- Secondary: Net additional completions vs baseline
- Tertiary: Cost-effectiveness (completions per EUR of policy cost)
- Quaternary: Robustness (95% CI width from Monte Carlo)
