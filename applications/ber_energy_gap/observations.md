# Observations: BER Energy Gap

## Data Observations

1. **Dataset is massive**: 1.37M real BER certificates with 211 columns. After cleaning: 1,330,022 model-ready records.

2. **BER bands explain ~80% of variance**: The letter grade alone is a strong predictor. The remaining ~20% within-band variance is what the model needs to capture.

3. **Within-band correlations are individually weak** (r < 0.07): Because BER bands are narrow (25 kWh/m2/yr wide), individual features have limited room to predict within-band position.

4. **Heat Loss Parameter (HLP) proxy dominates**: 55.4 mean absolute SHAP value, 8.6% built-in importance. Physically correct: HLP is the standard summary metric for building fabric quality.

5. **Heating system efficiency is second most important**: 23.7 mean absolute SHAP. Heat pumps create a discontinuity: efficiency >100% (COP > 1) fundamentally changes the energy profile.

6. **Primary energy factor is third by SHAP**: 14.5 mean absolute SHAP. The fuel-specific conversion from delivered to primary energy is a major determinant.

7. **Linear model captures most variance**: Ridge R2=0.862 means most of the BER relationship is linear. Nonlinear improvement from tree models (R2=0.951) captures interactions and thresholds.

8. **Construction year range includes errors**: Min year 1753, max 2104 in raw data.

9. **Dublin postal districts fragment the county variable**: 22 Dublin postal codes + "Co. Dublin" normalised to "Dublin".

## Model Results

10. **Tournament**: Ridge MAE=32.28, ExtraTrees MAE=20.51, XGBoost MAE=19.26, LightGBM MAE=19.54.

11. **Best single HDR feature**: Space heating fraction (MAE -1.07). All other individual features improved MAE by < 0.03.

12. **Composition**: LightGBM tuned + 4 HDR features = MAE 18.05, R2=0.9508. This is 7.6% better than the LightGBM baseline.

13. **Log target transformation did not help**: MAE increased by 0.13. BER distribution is not sufficiently skewed to benefit.

14. **Interaction features did not help individually**: Wall-era and heating-fabric interactions were reverted. The tree model already captures these nonlinearities.

## Retrofit Analysis Findings

15. **Chimney sealing has highest DEAP impact per euro**: 25.1 kWh/m2/yr saving at ~200 EUR = 8 EUR per kWh/m2/yr saved.

16. **Heat pump installation gives second-highest saving**: 15.5 kWh/m2/yr but at 10,000 EUR = 644 EUR per kWh/m2/yr.

17. **LED lighting is second most cost-effective**: 8.5 kWh/m2/yr at 500 EUR = 59 EUR per kWh/m2/yr.

18. **Wall insulation shows near-zero marginal DEAP effect**: The model predicts only -0.8 kWh/m2/yr change for a wall U-value improvement of 0.3 W/m2K. This is because wall U-value interacts with other features (area, other insulation) and the average dwelling already has reasonable walls.

19. **County variation is large**: Leitrim mean 239, Kildare mean 160. This 50% spread reflects both building stock age and rural vs urban construction quality.

20. **Construction era dominates**: Pre-1930 mean 339, 2021+ mean 40. A factor of 8.5x. But this is DEAP-calculated, not measured — the actual consumption gap is much smaller (~2x per literature).

## Fundamental Limitation

21. **BER = DEAP-calculated, NOT measured**: We cannot answer "why does an A-rated home use almost the same energy as a G-rated one" with this data alone. What we CAN answer: what building characteristics determine the DEAP rating, and which modifications shift it most.

22. **The performance gap exists in the literature** (Moran et al. 2020): A-rated homes use ~1.3x their DEAP value, G-rated homes use ~0.6x. The real gap is ~2:1, not the 8.5:1 that DEAP predicts.
