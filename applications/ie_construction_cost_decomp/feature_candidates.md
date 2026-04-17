# Feature Candidates: Construction Cost Decomposition

## Material-Level Features
1. **Index level** (WPM28C01): Current price index value for each of 40 materials
2. **Month-on-month change** (WPM28C02): Short-term price momentum
3. **Year-on-year change** (WPM28C03): Annual inflation rate per material
4. **CAGR 2015-latest**: Long-run growth rate for each material
5. **Volatility (rolling 12-month std)**: Price stability measure
6. **COVID peak impact**: Maximum deviation during 2020-2021
7. **Ukraine peak impact**: Maximum deviation during 2022-2023
8. **Post-crisis reversion**: Current level relative to peak
9. **PCA loading on PC1**: Sensitivity to common factor
10. **Variance contribution**: Material's share of aggregate index variance

## Trade-Level Features
11. **Trade share of hard cost**: Percentage of construction cost per trade
12. **Weighted inflation contribution**: Share x material CAGR
13. **Labour intensity by trade**: Estimated labour fraction per trade
14. **Material intensity by trade**: Estimated material fraction per trade
15. **NZEB sensitivity**: Degree of regulatory cost impact per trade

## Labour Market Features
16. **Hourly total labour cost** (EHQ03C08): Quarterly construction wage
17. **Average weekly hours** (EHQ03C05): Hours worked proxy
18. **Employment count** (EHQ03C01): Workforce size
19. **Labour CAGR**: Annualised wage growth
20. **Labour-materials gap**: Difference in growth rates

## Macroeconomic Features
21. **Production value index** (BEA04C01): Sector output value
22. **Production volume index** (BEA04C02): Real output
23. **Implied construction price deflator**: Value/volume ratio
24. **Tender price index** (SCSI): Bidding market temperature
25. **CPI general**: Background inflation context

## Regulatory Features
26. **Pre/post NZEB indicator**: Binary for Nov 2019 policy change
27. **Excess inflation post-NZEB**: Material-specific regulatory cost premium
28. **BCAR implementation indicator**: Post-SI 9 2014
29. **Part L compliance level**: Regulatory stringency
30. **BER target rating**: Energy specification tier
